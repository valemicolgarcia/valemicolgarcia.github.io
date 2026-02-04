---
layout: post
title: Deploying a model on Hugging Face Spaces
excerpt: "How to deploy an ML app (e.g. FastAPI + Grounding DINO) on Hugging Face Spaces: what Spaces is, SDK options, concrete steps, and how Nutri-AI meets the requirements."
categories:
  - "Software & Backend Engineering"
order: 5
tags:
  - Hugging Face
  - Spaces
  - Docker
  - Deploy
  - Nutri-AI
  - FastAPI
---

This post summarises how to deploy an application that uses an ML model (such as Grounding DINO in **Nutri-AI**) on **Hugging Face Spaces**: what Spaces is, what options exist, concrete steps, and requirements that the Nutri-AI project fulfils. For how Nutri-AI is packaged with Docker (Dockerfile, build, run), see [Docker — Overview, basic implementation, and use in Nutri-AI]({% post_url 2026-01-31-docker-resumen-implementacion-nutri-ai %}).

---

## 1. What is Hugging Face Spaces?

**Hugging Face Spaces** is a Hugging Face service for hosting and running applications (demos, APIs, UIs) that often use ML models. Each Space is a repository with code and configuration; Hugging Face builds and runs the app on its infrastructure and gives you a public URL.

- **Free** (with usage and resource limits).
- **Integrated** with the Hub: you can use models and datasets from the Hub in the same ecosystem.
- **Several SDKs:** Gradio, Streamlit, or **Docker** (your own container). For a FastAPI API plus a heavy model (PyTorch, etc.), the usual choice is **Docker**.

---

## 2. Deploy options on Spaces

| SDK | Typical use |
|-----|-------------|
| **Gradio** | Interfaces with `gr.Interface` or blocks; Hugging Face builds an environment with Gradio installed. |
| **Streamlit** | Interactive apps with `st.*`; HF installs Streamlit and runs your script. |
| **Docker** | Container defined by your **Dockerfile**. You control system, dependencies, and startup command. Ideal for APIs (FastAPI, Flask) or models that need system libraries (OpenCV, PIL, CUDA, etc.). |

For a **REST API with FastAPI** and a **model loaded in memory** (like Grounding DINO in Nutri-AI), **Docker** is the right option: same environment as local, same port and environment variables.

---

## 3. How to deploy with Docker (summary)

### 3.1 Create the Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces).
2. **Create new Space**.
3. Choose:
   - **Name** of the Space (e.g. `your-username/food-ingredients-detection`).
   - **SDK:** **Docker**.
   - Visibility (public/private).
4. Create. An empty repo is created (or with a default README).

### 3.2 Configure the Space for Docker

Hugging Face expects:

- A **Dockerfile** at the root of the Space repo.
- A **README.md** with **YAML frontmatter** at the top that specifies `sdk: docker` and the app port.

Example start of `README.md`:

```yaml
---
title: Food Ingredients Detection API
emoji: 🍽️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
```

- **sdk: docker** — tells HF to build and run with Docker.
- **app_port: 7860** — port your app listens on inside the container; HF routes public traffic to that port.

The rest of the README is the documentation users will see (endpoints, usage, etc.).

### 3.3 Files the Space repo should have

At the root (or the structure your Dockerfile expects):

| File / folder | Use |
|---------------|-----|
| **Dockerfile** | Instructions to build the image (base, dependencies, code, CMD). |
| **README.md** | Space description + frontmatter (`sdk: docker`, `app_port`). |
| **requirements.txt** | Python dependencies (if the Dockerfile runs `pip install -r requirements.txt`). |
| **main.py** (or your app name) | API entry point. |
| **detection/** (or your code) | Modules, models, etc. |

Only what the Dockerfile needs is uploaded; `.dockerignore` avoids uploading cache, `.venv`, etc.

### 3.4 Dockerfile requirements for Spaces

Hugging Face runs the container with constraints; it is best to comply with:

| Requirement | Reason |
|-------------|--------|
| **Port** | The app must listen on the port set in `app_port` (e.g. 7860). Use `ENV PORT=7860` and in CMD something like `uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}`. |
| **Host 0.0.0.0** | The server must listen on all interfaces (`0.0.0.0`), not only `127.0.0.1`, so HF can send traffic to the container. |
| **Non-root user** | Some environments (e.g. Spaces) require not running as root. Create a user (e.g. UID 1000) and use `USER user`. |
| **No daemons** | A single process that keeps the container alive (e.g. uvicorn). Do not use background services that HF does not manage. |

If your Dockerfile already meets these (like Nutri-AI’s), you do not need to change it.

### 3.5 Upload the code

- **Option A:** Clone the Space repo, copy your project (Dockerfile, README.md, main.py, detection/, requirements.txt, etc.), commit and push.
- **Option B:** Upload files from the Hugging Face web UI (upload in the Space repo).

After push (or upload), Hugging Face detects changes, **rebuilds the image** with your Dockerfile and **restarts the container**. The first build can take several minutes (pip install torch, transformers, etc.).

### 3.6 Environment variables and secrets

To avoid hardcoding model ID or thresholds:

1. On the Space page → **Settings** → **Variables and secrets**.
2. Add variables (e.g. `GROUNDING_DINO_MODEL_ID`, `GROUNDING_DINO_BOX_THRESHOLD`, `GROUNDING_DINO_TEXT_THRESHOLD`).
3. In the container they are available as `os.environ.get("NAME")`; your code can use them (as in Nutri-AI’s `detection/config.py`).

**Secrets** are variables HF does not show in the UI; useful for API keys (Nutri-AI does not use them).

### 3.7 URL and usage

- The Space URL is: `https://huggingface.co/spaces/<org-or-user>/<space-name>`.
- Hugging Face often provides a **direct link** to the app (e.g. to test the API). It is usually shown on the Space tab.
- For an API: `GET /docs` for Swagger, `POST /detect` to send the image (same as local, with the host replaced by the Space URL).

---

## 4. How this applies to Nutri-AI

### 4.1 What was deployed

- **API:** FastAPI (`main.py`) with endpoints `/`, `/health`, `/docs`, `/detect`, `/detect/image`.
- **Model:** Grounding DINO (zero-shot) loaded in memory on the first request to `/detect`; it is downloaded from the Hub the first time the container runs.

### 4.2 Files in the Nutri-AI Space

- **Dockerfile** — Python 3.10-slim image, libgl1/libglib2.0-0, user `user` (UID 1000), pip install from requirements.txt, copy of main.py and detection/, CMD with uvicorn on port 7860.
- **README.md** — frontmatter with `sdk: docker`, `app_port: 7860`, title and emoji; rest is API documentation.
- **requirements.txt** — FastAPI, uvicorn, transformers, torch, torchvision, Pillow, python-multipart.
- **main.py** — FastAPI application.
- **detection/** — detection module (config, grounding_dino).

### 4.3 Nutri-AI README frontmatter

```yaml
---
title: Food Ingredients Detection API
emoji: 🍽️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
```

### 4.4 Optional variables in Settings

- `GROUNDING_DINO_MODEL_ID` — model on the Hub (default: `IDEA-Research/grounding-dino-tiny`).
- `GROUNDING_DINO_BOX_THRESHOLD` — box threshold (default 0.30).
- `GROUNDING_DINO_TEXT_THRESHOLD` — text–image threshold (default 0.25).

### 4.5 Deploy flow for Nutri-AI

1. Create a Space with SDK Docker.
2. Upload Dockerfile, README.md (with frontmatter), requirements.txt, main.py, detection/.
3. HF builds the image and starts the container; the app listens on port 7860.
4. First request to `/detect`: the code downloads the model from the Hub (if not cached) and responds; later requests use the already-loaded model.

---

## 5. Summary steps

| Step | Action |
|------|--------|
| 1 | Create a Space on Hugging Face with SDK **Docker**. |
| 2 | Add **frontmatter** to the README with `sdk: docker` and `app_port: 7860` (or the port you use). |
| 3 | Upload **Dockerfile**, **requirements.txt**, **main.py**, **detection/** (and whatever your Dockerfile needs). |
| 4 | Ensure the **Dockerfile** listens on **0.0.0.0** and on the port set in `app_port`, and does not run as root (user UID 1000). |
| 5 | Optional: set **Variables and secrets** in Settings (model_id, thresholds, etc.). |
| 6 | Wait for the **build**; use the Space URL to test `/docs` and `/detect`. |

---

This post describes how to deploy an ML-backed app like Nutri-AI (FastAPI API + model from the Hugging Face Hub) on Hugging Face Spaces using Docker. For packaging Nutri-AI with Docker locally, see [Docker — Overview, basic implementation, and use in Nutri-AI]({% post_url 2026-01-31-docker-resumen-implementacion-nutri-ai %}).
