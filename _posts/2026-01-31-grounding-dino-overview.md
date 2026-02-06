---
layout: post
title: Grounding DINO — Model Overview and Concepts
excerpt: "How Grounding DINO is used in the Zero-Shot Object Detection Service: where it comes from, how it is invoked in the code, and how it was put into practice (API, deployment)."
categories:
  - "Deep Learning & AI"
order: 3
tags:
  - Object Detection
  - Transformers
  - Vision-Language
  - Hugging Face
---

This document describes how **Grounding DINO** is used in the [**Zero-Shot Object Detection Service**](/projects/zero-shot-detection.html): what it is, where it comes from, how it is invoked in the code, and how it was put into practice (API, deployment). For an explanation of what a Transformer is and the main transformer architectures (including **vision-language**, which Grounding DINO uses), see [Transformers: what they are and main architectures]({% post_url 2026-01-31-transformers-architectures %}).

---

## 1. What is Grounding DINO and where does it come from?

### What is it?

**Grounding DINO** is a **text-guided object detection** model. That is:

- **Input:** an image plus a list of texts (e.g. "rice", "tomato", "chicken").
- **Output:** bounding boxes in the image that mark where each thing is, with a label (which text matches) and a confidence **score** (0–1).

Unlike a classical detector (which can only detect the classes it was trained on), Grounding DINO can search for **any concept that is passed to it in text**. For this reason it is called **open-set** or **zero-shot**: it was not trained on "rice" or "tomato" specifically, but it understands language and the image well enough to localise those concepts.

### Where it comes from

- **Paper:** *"Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection"* (Liu et al., 2023).  
  Link: [arXiv:2303.05499](https://arxiv.org/abs/2303.05499).
- **Core ideas:** **DINO** (a transformer-based detector, in the spirit of DETR) is combined with **grounded pre-training**: training on data that links image regions to phrases or words.
- **Code and models:** The authors released code and checkpoints; in the Zero-Shot Object Detection Service the version integrated in **Hugging Face** (`transformers`) is used, with the model **IDEA-Research/grounding-dino-tiny** (small variant).

In short: the model comes from the 2023 paper and is used here via the Hugging Face library and its Hub.

---

## 2. How it is named and used in the Zero-Shot Object Detection Service

### Where it is in the code

- **Class that encapsulates the model:** `GroundingDinoDetector` in `detection/grounding_dino.py`.
- **Configuration:** `detection/config.py` (model ID, list of ingredients, thresholds).
- **Point of use:** `main.py` uses `get_detector()` to obtain a single instance (singleton) and then calls `detector.detect(...)` in the endpoints `/detect` and `/detect/image`.

### How it is invoked

1. **Load (once):** `get_detector()` creates `GroundingDinoDetector()`, and the first time `detect()` is called, `load_model()` is executed: the processor and model are downloaded from Hugging Face and moved to GPU or CPU.
2. **Each request:** `detector.detect(image, text_prompts=list_of_ingredients, box_threshold=..., text_threshold=...)` is called. The model returns a list of dictionaries with `label`, `box` (coordinates), and `score`.
3. **Post-processing in `main.py`:** Boxes that are too large are filtered out, labels are normalised to the list of ingredients, and optionally filtering by food category (breakfast, lunch, snack, dinner) is applied.

The "name" of the model in the API and in the documentation is "Grounding DINO (vision-language, zero-shot)"; in code it is the class `GroundingDinoDetector` and the Hugging Face model `IDEA-Research/grounding-dino-tiny`.

---

## 3. How it was put into practice (implementation)

### Stack used

- **Language:** Python.
- **API:** FastAPI (`main.py`).
- **ML:** PyTorch + Hugging Face `transformers` (`AutoModelForZeroShotObjectDetection`, `AutoProcessor`).
- **Images:** PIL/Pillow (open, convert to RGB, draw boxes in `/detect/image`).
- **Config:** Environment variables for model and thresholds; list of ingredients and food categories in `config.py`.

### Flow of a request

1. The user uploads an image to `POST /detect` (or `/detect/image`).
2. The file type is validated (JPEG, PNG, WebP, BMP) and opened with PIL in RGB.
3. The list of texts is built: `ingredients_prompt` (query param) or `INGREDIENTS_LIST` by default; if a string is provided, `ingredients_from_string()` converts it to a list.
4. `get_detector()` returns the single instance of `GroundingDinoDetector`; if the model was not loaded, `load_model()` is called (download from Hugging Face and move to GPU/CPU).
5. `detector.detect(image, text_prompts=..., box_threshold=..., text_threshold=...)` is called:
   - The processor tokenises image and text and produces the tensors.
   - The forward pass is run with `torch.no_grad()`.
   - `post_process_grounded_object_detection()` returns boxes, scores, and labels in image coordinates.
6. In `main.py`: boxes that are too large are filtered (`_is_box_too_large`), the label is normalised with `_normalize_label`, and if requested, filtering by food category is applied.
7. JSON is returned with `ingredients` (list of `DetectedIngredient`) or, in `/detect/image`, the image with the boxes drawn in JPEG.

### Concrete model

- **ID:** `IDEA-Research/grounding-dino-tiny` (configurable via `GROUNDING_DINO_MODEL_ID`).
- **Variant:** "Tiny" (smaller backbone) to balance speed and quality; larger variants exist in the paper's ecosystem (e.g. Swin-L).

### Deployment

- **Local:** `uvicorn main:app --reload --port 8000` (or as configured).
- **Docker:** The Dockerfile builds an image with Python, dependencies, `main.py`, and `detection/`; the default port is 7860 (e.g. for Hugging Face Spaces).
- **Hugging Face Spaces:** It can be deployed as a Space with the Docker SDK using that Dockerfile; the first request downloads the model from the Hub.

---

## 4. Summary table

| Topic | What it is / where it comes from | How it is used in the Zero-Shot Object Detection Service |
|-------|----------------------------------|----------------------------------------------------------|
| **Grounding DINO** | Vision-language, zero-shot model for open-set detection (2023 paper, Hugging Face). | `GroundingDinoDetector` in `detection/grounding_dino.py`; model `grounding-dino-tiny`. |
| **Implementation** | FastAPI + PyTorch + Hugging Face + PIL; detector singleton; Docker/Spaces. | `get_detector()` + `detector.detect()` in `/detect` and `/detect/image`; post-processing and filters in `main.py`. |

---

This document summarises how Grounding DINO is used in the Zero-Shot Object Detection Service backend. For the underlying architecture (Transformers, vision-language), see [Transformers: what they are and main architectures]({% post_url 2026-01-31-transformers-architectures %}).
