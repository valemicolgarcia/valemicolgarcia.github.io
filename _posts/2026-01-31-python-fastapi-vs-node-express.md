---
layout: post
title: Python (FastAPI) vs Node.js (Express) — backend comparison
date: 2026-01-31
excerpt: "Key differences between building a backend in Python with FastAPI and in Node.js with Express: runtime, server model, validation, documentation, and when to choose each."
categories:
  - "Software & Backend Engineering"
tags:
  - Python
  - FastAPI
  - Node.js
  - Express
  - Backend
  - REST API
---

This post summarises the main differences between a **Python backend with FastAPI** and a **Node.js backend with Express**: runtime, how the server works, validation, documentation, and typical use cases. For more detail on each stack, see [FastAPI — Python backends and the Nutri-AI API]({% post_url 2026-01-31-fastapi-python-backend-nutri-ai %}) and [Node.js backend with Express — the basics]({% post_url 2026-01-31-nodejs-express-backend-basics %}).

---

## 1. Runtime and language

| | Python + FastAPI | Node.js + Express |
|---|------------------|-------------------|
| **Language** | Python | JavaScript (or TypeScript) |
| **Runtime** | CPython (or PyPy, etc.) | Node.js (V8) |
| **Execution** | Often async via ASGI; sync code can block a worker. | Event loop; I/O is non-blocking by default. |

Both can handle many concurrent connections; FastAPI does it with async/await and an ASGI server; Node does it with the event loop and callbacks/promises.

---

## 2. Server and framework

| | Python + FastAPI | Node.js + Express |
|---|------------------|-------------------|
| **Who serves HTTP?** | A **separate server** (e.g. **uvicorn**). FastAPI is an ASGI app; it does not open a port by itself. | The **runtime**: Node’s `http` module (or the framework on top of it). `app.listen(port)` starts the server. |
| **Interface** | **ASGI** (between uvicorn and FastAPI). The server “translates” HTTP ↔ ASGI. | No ASGI/WSGI; the framework wraps Node’s `req`/`res` and passes them to your handlers. |
| **Run command** | `uvicorn main:app --host 0.0.0.0 --port 7860` | `node index.js` (Express app calls `app.listen(port)`). |

So: in Python you have **server (uvicorn) + app (FastAPI)**; in Node, **Express is the app** and it uses Node’s built-in HTTP server.

---

## 3. Validation and typing

| | Python + FastAPI | Node.js + Express |
|---|------------------|-------------------|
| **Request validation** | **Built-in** via **Pydantic**: you define models and use them as `response_model`, body, or query params. Invalid data → 422 with details. | **Manual** (or with libraries like Joi, Zod, express-validator). No built-in schema validation in Express. |
| **Typing** | **Type hints** are first-class: FastAPI uses them for validation and OpenAPI docs. | JavaScript is dynamically typed; **TypeScript** adds types, but Express does not use them for runtime validation or auto-docs. |

FastAPI gives you automatic validation and schema from types; with Express you typically validate and document by hand (or with extra packages).

---

## 4. Documentation

| | Python + FastAPI | Node.js + Express |
|---|------------------|-------------------|
| **OpenAPI / Swagger** | **Automatic**: `/docs` (Swagger UI) and `/redoc` (ReDoc) from your routes and Pydantic models. | **Manual**: you can use swagger-jsdoc, swagger-ui-express, etc., but you write or generate the spec yourself. |

FastAPI generates the API spec from your code; with Express you usually add and maintain it separately.

---

## 5. Routes and handlers

| | Python + FastAPI | Node.js + Express |
|---|------------------|-------------------|
| **Style** | Decorators: `@app.get("/")`, `@app.post("/detect")`. Handlers are often `async def`. | Methods on the app: `app.get("/", handler)`, `app.post("/detect", handler)`. Callbacks receive `(req, res)`. |
| **Params / body** | Declared with **Query()**, **File()**, Pydantic models; FastAPI injects and validates them. | Read from `req.params`, `req.query`, `req.body` (after body-parser middleware); you validate yourself. |

Both support the same HTTP methods and path params; the main difference is how you declare and validate inputs.

---

## 6. Middleware

Both have a **middleware** concept: functions that run before/after your route logic.

- **FastAPI:** You add middleware (e.g. CORS) with `app.add_middleware(...)`; order matters.
- **Express:** You use `app.use(middleware)`; order matters; `next()` passes to the next middleware or route.

Express middleware is very explicit and widely used (logging, auth, body parsing); FastAPI has fewer built-in middlewares but you can add ASGI middleware.

---

## 7. When to use which?

| Prefer **Python + FastAPI** when… | Prefer **Node.js + Express** when… |
|-----------------------------------|------------------------------------|
| You already use Python (ML, data, scripts). | The team or ecosystem is JavaScript/TypeScript. |
| You want **automatic validation and API docs** with little setup. | You want a **minimal, flexible** setup and are fine adding validation/docs yourself. |
| You integrate with **Python libraries** (e.g. ML models, scientific stack). | You want **one language** for frontend and backend (JS/TS everywhere). |
| You like **type hints** driving both validation and documentation. | You need a **lightweight** server and a huge npm ecosystem. |

Both can build REST APIs, microservices, and backends for SPAs; the choice often comes down to language, ecosystem, and how much you want “batteries included” (FastAPI) vs “minimal and pluggable” (Express).

---

## 8. Summary table

| Aspect | Python + FastAPI | Node.js + Express |
|--------|------------------|-------------------|
| **Runtime** | Python + ASGI server (uvicorn) | Node.js (built-in HTTP) |
| **Framework** | FastAPI (ASGI app) | Express (wraps Node’s server) |
| **Validation** | Pydantic, automatic from types | Manual or via libraries |
| **API docs** | Automatic `/docs`, `/redoc` | Manual (e.g. Swagger) |
| **Typing** | Type hints → validation + docs | Optional (TypeScript); no built-in runtime validation |
| **Async** | `async def` + uvicorn | Event loop, callbacks/promises/async-await |
| **Run** | `uvicorn main:app --port 7860` | `app.listen(7860)` in your script |

---

This post outlined the main differences between a Python backend with FastAPI and a Node.js backend with Express. For more on each stack, see [FastAPI — Python backends and the Nutri-AI API]({% post_url 2026-01-31-fastapi-python-backend-nutri-ai %}) and [Node.js backend with Express — the basics]({% post_url 2026-01-31-nodejs-express-backend-basics %}).
