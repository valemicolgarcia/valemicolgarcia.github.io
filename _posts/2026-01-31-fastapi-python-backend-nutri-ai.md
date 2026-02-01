---
layout: post
title: FastAPI — Python backends and the Nutri-AI ingredient-detection API
date: 2026-01-31
excerpt: "What FastAPI is, what a Python backend is, and how FastAPI was used in the Nutri-AI food-detection API: app setup, CORS, Pydantic, routes, and documentation."
categories:
  - "Software & Backend Engineering"
tags:
  - FastAPI
  - Python
  - Backend
  - Pydantic
  - Nutri-AI
  - REST API
---

This post explains what FastAPI is, what a Python backend is, and how FastAPI was used in the **Nutri-AI** ingredient-detection project (food-detection API).

---

## 1. What is FastAPI?

**FastAPI** is a **Python framework** for building **web APIs** (REST, for example). It is used to expose HTTP endpoints (GET, POST, etc.) that your application or a frontend can call.

### Main features

- **Asynchronous:** Supports `async def` in route handlers; useful when there is I/O (file reads, model calls, network) without blocking the server.
- **Automatic validation:** Integrates **Pydantic**: request parameters and body are validated by type; if something does not match, FastAPI returns a 422 error with details.
- **Automatic documentation:** Generates **OpenAPI** (Swagger) and a UI at `/docs` (Swagger UI) and `/redoc` (ReDoc) without extra code.
- **Performance:** Based on **ASGI** (uvicorn, etc.); typically faster than synchronous frameworks for many concurrent requests.
- **Typing:** Designed to use Python **type hints**; validation and documentation are derived from the types.

### What it is used for

To build **backends**: services that receive HTTP requests, run logic (e.g. load a model, process an image) and return responses (JSON, image, etc.). A frontend (React, Vue, etc.) or another app consumes that API.

---

## 2. What is a Python backend?

The **backend** is the part of the system that runs on the server: it receives requests, applies business logic, accesses data or models, and responds. It does not render screens for the user; it exposes an **API** that other programs consume.

### Backend in Python

- **Language:** Python.
- **Role:** Server that exposes endpoints (URLs + HTTP method). Example: `POST /detect` receives an image and returns JSON with ingredients.
- **Framework:** FastAPI, Flask, Django REST, etc. In Nutri-AI we use **FastAPI**.
- **ASGI server:** FastAPI does not serve HTTP on its own; it is run with a **server** such as **uvicorn**. Example: `uvicorn main:app --host 0.0.0.0 --port 7860`.

### Frontend vs backend

- **Frontend:** What the user sees (pages, forms, photo upload). Usually a SPA (React, Vite, etc.) that calls the backend over HTTP.
- **Backend:** The API (FastAPI here): receives the image, calls the model (Grounding DINO), returns ingredients. The frontend consumes that API.

In Nutri-AI the backend is the API only (FastAPI + detection); the frontend lives in another repo (e.g. Vite/React) and connects to this API (CORS is configured for localhost and Vercel).

---

## 3. How FastAPI was used in Nutri-AI

### 3.1 App creation

In `main.py` the FastAPI app is instantiated with title, description and version:

```python
app = FastAPI(
    title="Food Ingredients Detection API",
    description=(
        "Detection of visible ingredients in dish photos with Grounding DINO. "
        "Accepts an image and returns a list of detected ingredients with score. "
        "The user can manually correct the results afterwards."
    ),
    version="2.0.0",
)
```

This feeds the documentation at `/docs` and `/redoc`.

### 3.2 CORS

So that a frontend on another origin (e.g. `http://localhost:5173` or `https://your-app.vercel.app`) can call the API, **CORS** is added:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^https://[\w-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- **allow_origins:** Allowed origins (local development).
- **allow_origin_regex:** Any subdomain of `*.vercel.app`.
- **allow_credentials, methods, headers:** Allows cookies and all methods/headers needed by the frontend.

### 3.3 Pydantic models (request/response)

Pydantic models are used to **type and validate** the response (and document the schema):

```python
class DetectedIngredient(BaseModel):
    """A detected ingredient with its confidence score."""
    label: str
    score: float
    box: list[float] | None = None  # [x0, y0, x1, y1] for manual correction in the UI


class DetectionResponse(BaseModel):
    """List of detected ingredients (visible only, no recipes)."""
    ingredients: list[DetectedIngredient]
```

- **DetectedIngredient:** One ingredient with `label`, `score` and optionally `box`.
- **DetectionResponse:** Object with list `ingredients`. Used as `response_model=DetectionResponse` on `/detect` so FastAPI serialises and documents the response.

### 3.4 Routes (endpoints)

| Method | Route | Function | Use |
|--------|-------|----------|-----|
| **GET** | `/` | `root()` | Returns message, model info and links to docs and health. |
| **GET** | `/health` | `health()` | Health check: `{"status": "ok"}`. |
| **POST** | `/detect` | `detect_ingredients()` | Receives image (file) + query params; returns JSON with list of ingredients. |
| **POST** | `/detect/image` | `detect_ingredients_image()` | Receives image + query params; returns the image with boxes and labels drawn (JPEG). |

All routes are defined with **decorators** `@app.get(...)` or `@app.post(...)` on `async def` functions.

### 3.5 Parameters: File and Query

- **File (image):** Received with `UploadFile = File(...)` in the request body (multipart). `content_type` is validated (JPEG, PNG, WebP, BMP only) and the file is read with `await file.read()`.
- **Query params:** Declared with `Query(...)` (optional or with default). Examples: `category`, `ingredients_prompt`, `box_threshold`, `text_threshold`, `include_boxes`. FastAPI validates and documents them in `/docs`.

Example signature for `/detect`:

```python
async def detect_ingredients(
    file: UploadFile = File(...),
    category: str | None = Query(None, description="..."),
    ingredients_prompt: str | None = Query(None, ...),
    box_threshold: float | None = Query(None, ...),
    text_threshold: float | None = Query(None, ...),
    include_boxes: bool = Query(True, ...),
):
```

### 3.6 Validation and HTTP errors

- **Manual validation:** If `category` is not in `MEAL_CATEGORIES`, or `content_type` is not allowed, or the file is empty, or the image cannot be opened, **HTTPException** is raised with `status_code=400` and a clear `detail`.
- **Model errors:** If `detector.detect(...)` fails, **HTTPException** is returned with `status_code=500` and the error message.

Example:

```python
if category is not None and category not in MEAL_CATEGORIES:
    raise HTTPException(
        status_code=400,
        detail=f"Invalid category: {category}. Allowed values: {list(MEAL_CATEGORIES.keys())}",
    )
```

### 3.7 Custom response (image)

In `/detect/image` the response is not JSON but **JPEG**. FastAPI’s **Response** is used:

```python
return Response(content=buf.getvalue(), media_type="image/jpeg")
```

`buf` is a `BytesIO` with the image already drawn (PIL); `response_class=Response` in the decorator allows returning bytes with the given `media_type`.

### 3.8 response_model

On `POST /detect`, **response_model=DetectionResponse** is used. FastAPI serialises the return value (an instance of `DetectionResponse`) to JSON, validates that the response matches the schema, and documents the format in OpenAPI.

---

## 4. Summary table

| Concept | In Nutri-AI |
|---------|-------------|
| **Framework** | FastAPI |
| **App** | `app = FastAPI(title=..., description=..., version=...)` |
| **Middleware** | CORSMiddleware (origins localhost and Vercel) |
| **Models** | Pydantic: `DetectedIngredient`, `DetectionResponse` |
| **Routes** | GET `/`, GET `/health`, POST `/detect`, POST `/detect/image` |
| **Input** | `UploadFile` (image), `Query` (category, thresholds, etc.) |
| **Output** | JSON (DetectionResponse) or JPEG image (Response) |
| **Errors** | HTTPException (400, 500) with message in `detail` |
| **Documentation** | Automatic at `/docs` (Swagger) |
| **Server** | uvicorn (`uvicorn main:app --host 0.0.0.0 --port 7860`) |

---

This post summarises what FastAPI is, what a Python backend is, and how FastAPI was applied in the Nutri-AI project (app, CORS, Pydantic, routes, File/Query, HTTPException, Response and documentation). For packaging and running the Nutri-AI API with Docker, see [Docker — Overview, basic implementation, and use in Nutri-AI]({% post_url 2026-01-31-docker-resumen-implementacion-nutri-ai %}).
