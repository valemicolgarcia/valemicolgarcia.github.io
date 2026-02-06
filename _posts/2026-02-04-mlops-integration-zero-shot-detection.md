---
layout: post
title: "MLOps Integration in the Zero-Shot Object Detection Service"
excerpt: "How a human-in-the-loop (HITL) flow was added to collect user corrections on ingredient detection (Grounding DINO), and which MLOps concepts are applied — data storage, annotation format, governance, and future evaluation/training pipelines."
categories:
  - "Deep Learning & AI"
order: 2
tags:
  - MLOps
  - Human-in-the-Loop
  - Grounding DINO
  - Zero-Shot Detection
  - Supabase
  - FastAPI
---

This post describes how a **human-in-the-loop (HITL)** flow was integrated into the [**Zero-Shot Object Detection Service**](/projects/zero-shot-detection.html) to collect user corrections on ingredient detection (Grounding DINO), and which MLOps concepts are applied.

---

## 1. Goal of the integration

- **Collect corrections** when the user uploads a photo: the model detects ingredients and the user can confirm, edit, or add ingredients (and optionally draw or correct bounding boxes on the image).
- Build **two types of dataset** from the same flow:
  - **Classification:** image + list of ingredients (text). Suitable for fine-tuning a model that predicts “which ingredients are present” without positions.
  - **Detection:** image + list of ingredients + **bounding boxes** per ingredient. Suitable for fine-tuning Grounding DINO (or another detector).
- **Rule:** if the user only edits the list → store image + text (classification). If they also draw or edit boxes → store image + text + boxes (detection and classification).

---

## 2. MLOps concepts used

### 2.1 Human-in-the-loop (HITL)

The implemented flow follows the classic HITL pattern:

1. **Prediction:** the model (Grounding DINO) returns ingredients and, optionally, boxes.
2. **Review:** the user removes false positives, adds missing ingredients, and can draw or correct boxes.
3. **Persistence:** only if the user gives **explicit consent** is the correction sent to the backend and stored (Supabase or local).

This produces a human-labeled dataset from real app usage.

### 2.2 Data storage and versioning

- **Production:** Supabase Storage (bucket `mlops-corrections`) + Postgres table `ingredient_corrections`. Images and annotations live in the cloud for future evaluation or training pipelines.
- **Development / fallback:** local folder `nutri-ai-backend/data/corrections/` (images + `annotations.jsonl`). If Supabase env vars are not set, the backend writes there.
- **Versioning:** the format of each record is stable (see below); in the future **DVC** or similar could be used to version the dataset (v1, v2) and reproduce which data was used in each experiment.

### 2.3 Annotation format

Each correction is stored with a clear schema:

- **Detected by the model:** list of `{ "label": "..." }` (no boxes in the “detected” payload; boxes go in “corrected” when the user confirms or draws them).
- **Corrected by the user:** list of `{ "label": "...", "box": [x0, y0, x1, y1] | null }`. If the user did not draw a box for that item, `box` is `null`.
- **Interpretation:** an ingredient in “detected” but not in “corrected” is **rejected** (false positive). One in “corrected” but not in “detected” is **added** (the model missed it).

This format is compatible with export to **COCO** or tools like **Label Studio** for review or training.

### 2.4 Data governance

- **Explicit consent:** no correction is stored unless the user checks the box “Allow using this correction to improve the model (MLOps)”.
- The backend validates `consent === 'true'`; otherwise it returns 400.
- In Supabase (or local JSON) only records with `consent: true` are persisted. Any later pipeline (evaluation, training) must use only consented records.

### 2.5 Evaluation pipeline (future)

The corrections dataset serves as a **real test set**:

- Script that loads corrections (from Supabase or local JSONL).
- Runs the current model on those images (or uses stored “detected” predictions).
- Compares with “corrected” and computes metrics (precision, recall, F1 per ingredient or per image).
- Typical tools: **Python** (pandas, sklearn or custom metrics), **MLflow** to log each evaluation run (parameters + metrics) and compare model versions.

### 2.6 Training data pipeline

- **Classification:** from the same storage, export only image + list of labels (ignoring `box`).
- **Detection:** export only “corrected” items with non-null `box`; format compatible with detector training (e.g. COCO).
- Later tools: **Hugging Face Datasets**, **DVC**, export scripts depending on the trainer.

---

## 3. Integration architecture

```
[User] → uploads photo → [Frontend]
                              ↓
                       POST /detect (nutri-ai-backend)
                              ↓
                       [Grounding DINO] → ingredients + boxes
                              ↓
[User] → edits list, optionally draws/edits boxes, checks consent → Save meal
                              ↓
                       Frontend calls POST /corrections (only if consent = true)
                              ↓
                       [nutri-ai-backend]
                              ↓
               SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY?
                       /                           \
                      yes                           no
                      ↓                             ↓
               [Supabase]                    [Local disk]
               - Storage: image              - data/corrections/images/
               - Table: row with            - data/corrections/annotations.jsonl
                 detected_ingredients,
                 corrected_ingredients
```

- **Frontend:** React (NutritionPage). Shows the image, boxes (IngredientBoxEditor), ingredient list, consent checkbox; on save, calls `sendCorrection()` if consent was given.
- **Backend:** FastAPI. Endpoint `POST /corrections` receives image (file), `detected_ingredients` (JSON), `corrected_ingredients` (JSON), `consent`. If Supabase is configured, it uploads the image to the bucket and inserts a row in `ingredient_corrections`; otherwise it writes to local disk.

---

## 4. Key files

| Component | File | Role |
|-----------|------|------|
| Backend: endpoint and logic | `nutri-ai-backend/main.py` | `POST /corrections`, .env loading, Supabase client, save to Storage + table or to local. |
| Backend: dependencies | `nutri-ai-backend/requirements.txt` | `supabase`, `python-dotenv`. |
| Supabase migration | `supabase/supabase-migration-mlops-corrections.sql` | Creates table `ingredient_corrections` (image_id, image_path, detected_ingredients, corrected_ingredients, consent, created_at). |
| Frontend: API | `src/lib/nutriApi.ts` | `sendCorrection()`, types `CorrectedIngredientItem`. |
| Frontend: box editor | `src/components/IngredientBoxEditor.tsx` | Draw and edit bounding boxes on the image (Pointer Events, desktop and mobile). |
| Frontend: nutrition flow | `src/components/NutritionPage.tsx` | State for boxes, consent, BoxEditor integration, call to `sendCorrection` on save. |

---

## 5. Configuration

- **Local (Supabase):** in the project root `.env` (or `nutri-ai-backend/.env`): `VITE_SUPABASE_URL` (or `SUPABASE_URL`) and `SUPABASE_SERVICE_ROLE_KEY`. The backend loads this .env; if both are set, it saves to Supabase.
- **Production (e.g. Hugging Face Space):** in the Space, Settings → Variables and secrets: `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. In Supabase: create bucket `mlops-corrections` and run the migration `supabase-migration-mlops-corrections.sql`.

If the URL or key is missing (or client creation fails), the backend writes to `data/corrections/` and logs `[MLOps] Saving correction locally`.

---

## 6. Summary of MLOps concepts applied

| Concept | How it is applied in this project |
|---------|-----------------------------------|
| **Human-in-the-loop** | User corrects model predictions; data is persisted only with consent. |
| **Data storage** | Supabase (Storage + Postgres) in production; local disk as fallback. |
| **Annotation format** | Per-correction record: image_id, detected, corrected (label + optional box), consent. |
| **Data governance** | Explicit consent; backend validation; only consented records in the dataset. |
| **Evaluation (future)** | Corrections dataset as test set; metrics script; optional MLflow. |
| **Training data pipeline** | Same storage supports export for classification (labels only) or detection (labels + boxes). |

The integration does not include (but is compatible with) **MLflow** for experiments, **DVC** for dataset versioning, or **Label Studio** as a review UI; these can be added later on top of this base.
