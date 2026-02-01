---
layout: post
title: Docker — Overview, basic implementation, and use in Nutri-AI
date: 2026-01-31
excerpt: "What Docker is, how it is implemented at a basic level (Dockerfile, build, run, .dockerignore), and how it was used in the Nutri-AI food-detection (ingredient-detection) backend."
categories:
  - "Software & Backend Engineering"
tags:
  - Docker
  - Containers
  - FastAPI
  - Nutri-AI
---

This document explains what Docker is, how it is implemented at a basic level, and how it was used in **Nutri-AI**, a food-detection project (ingredient-detection backend).

---

## 1. What is Docker?

**Docker** is a platform for creating, running, and distributing **containers**.

### Container

A **container** is an isolated environment that packages your application together with everything it needs to run: programming language, dependencies, system libraries, and your code. It runs on the host operating system but with its own filesystem and processes.

- **It is not a virtual machine:** it does not include a full OS; it shares the host kernel. It is lighter and starts faster.
- **Reproducible:** if the image is built correctly, the same container behaves the same on your PC or on a server.

### Image

An **image** is the “template” of the container: layers of files (base + system + dependencies + your app). You define the image with a **Dockerfile**; running `docker build` produces the image; running `docker run` creates and starts a container from that image.

### What it is for

- **Same environment everywhere:** avoids “it works on my machine”; development, CI, and production use the same image.
- **Simple deployment:** you upload the image (or the Dockerfile) and the service runs without installing Python, pip, or libraries by hand.
- **Isolation:** the app runs in its own container; it does not pollute the system nor depend on global versions.

---

## 2. Basic Docker implementation

### 2.1 Dockerfile

The **Dockerfile** is a text file with instructions to build the image. Each instruction adds a layer.

| Instruction | Typical use |
|-------------|-------------|
| **FROM** | Base image (e.g. `python:3.10-slim`). Required; usually first. |
| **RUN** | Run a command inside the image (install packages, etc.). |
| **COPY** | Copy files from the host into the container. |
| **WORKDIR** | Working directory inside the container. |
| **ENV** | Set environment variables. |
| **EXPOSE** | Document which port the app uses (does not open the port; that is done with `-p` when running). |
| **CMD** | Default command when the container starts (only one; if there are multiple CMD lines, the last one counts). |

Usual order: base → system dependencies → app dependencies → copy code → variables → startup command.

### 2.2 Basic commands

```bash
# Build the image from the Dockerfile (in the current directory)
docker build -t image-name .

# Run a container from the image
docker run -p host_port:container_port image-name

# Example: expose container port 7860 on host port 7860
docker run -p 7860:7860 image-name
```

- **`-t`** in `build`: gives the image a name (and optionally a tag).
- **`-p`** in `run`: maps host port to container port so the service can be reached from outside.

### 2.3 .dockerignore

A file at the project root that lists files or folders that must **not** be copied into the build context (e.g. with `COPY`). This avoids sending `__pycache__`, `.venv`, `.git`, etc., so the build is faster and cleaner.

---

## 3. How Docker was used in Nutri-AI

### 3.1 Goal

- Package the Nutri-AI FastAPI + Grounding DINO API (food/ingredient detection) so it runs in any environment (local or server).
- Use a non-root user (UID 1000) for safer execution.
- Expose the API on port 7860.

### 3.2 Nutri-AI Dockerfile

The Nutri-AI `Dockerfile` does the following, step by step:

| Step | Instruction | What it does |
|------|-------------|--------------|
| 1 | `FROM python:3.10-slim` | Starts from an official Python 3.10 image (“slim” variant, smaller). |
| 2 | `RUN apt-get update && apt-get install -y ... libgl1 libglib2.0-0` | Installs system libraries needed for PIL/image processing. Cleans apt cache (`rm -rf /var/lib/apt/lists/*`) to reduce size. |
| 3 | `RUN useradd -m -u 1000 user` / `USER user` | Creates a `user` with UID 1000 and switches to that user (do not run the app as root). |
| 4 | `ENV HOME=... PATH=...` / `WORKDIR $HOME/app` | Sets environment variables and working directory `/home/user/app`. |
| 5 | `RUN pip install --no-cache-dir --upgrade pip` | Upgrades pip. |
| 6 | `COPY --chown=user:user requirements.txt .` | Copies `requirements.txt` and sets owner to `user`. |
| 7 | `RUN pip install --no-cache-dir --user -r requirements.txt` | Installs Python dependencies for the user (FastAPI, uvicorn, transformers, torch, Pillow, etc.). |
| 8 | `COPY --chown=user:user main.py .` / `COPY ... detection/ ./detection/` | Copies the API code (`main.py` and the `detection/` package). |
| 9 | `ENV PORT=7860` / `EXPOSE 7860` | Sets the default port and documents it. |
| 10 | `CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]` | When the container starts, runs uvicorn: API on all interfaces (`0.0.0.0`) and on port `PORT` (default 7860). |

- **`--host 0.0.0.0`** is required so the API is reachable from outside the container (not only from localhost).
- **`${PORT:-7860}`** uses the `PORT` environment variable if set; otherwise 7860.

### 3.3 Nutri-AI .dockerignore

In the Nutri-AI repo, among others, the following are excluded:

- `__pycache__`, `*.pyc`
- `.git`, `.gitignore`, `.env`
- `.venv`, `venv`, `*.egg-info`
- `*.md` except `README.md`

So the build context only includes what is needed to build and run the app.

### 3.4 How to build and run (local)

From the Nutri-AI project root (where the `Dockerfile` is):

```bash
docker build -t nutri-ai-backend .
docker run -p 7860:7860 nutri-ai-backend
```

- **Build:** builds the image with the name `nutri-ai-backend`.
- **Run:** creates a container listening on port 7860; the API is at **http://localhost:7860** (docs at http://localhost:7860/docs).

To deploy the same Nutri-AI image on **Hugging Face Spaces** (create Space, frontmatter, variables, etc.), see [Deploying a model on Hugging Face Spaces]({% post_url 2026-01-31-deploy-hugging-face-spaces %}).

---

## 4. Summary table

| Topic | In Nutri-AI |
|-------|-----------------|
| **Base image** | `python:3.10-slim` |
| **System dependencies** | `libgl1`, `libglib2.0-0` (for PIL/images) |
| **User** | `user` (UID 1000), not root |
| **Python dependencies** | `requirements.txt` (FastAPI, uvicorn, transformers, torch, Pillow, etc.) |
| **Code copied** | `main.py`, `detection/` |
| **Port** | 7860 (variable `PORT`) |
| **Startup command** | `uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}` |
| **Deployment** | Local with `docker build` + `docker run`; for deploy on Hugging Face Spaces, see [Deploying on Hugging Face Spaces]({% post_url 2026-01-31-deploy-hugging-face-spaces %}). |

---

This document summarises what Docker is, the basic implementation (Dockerfile, build, run, .dockerignore), and how it was applied in the Nutri-AI project to package the food-detection (ingredient-detection) API. For deploying that API on Hugging Face Spaces, see [Deploying a model on Hugging Face Spaces]({% post_url 2026-01-31-deploy-hugging-face-spaces %}).
