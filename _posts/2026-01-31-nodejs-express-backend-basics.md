---
layout: post
title: Node.js backend with Express — the basics
date: 2026-01-31
excerpt: "What you need to know to build a backend in Node.js with Express: server, routes, middleware, request/response, and how it compares to other backends. I learned this in the Backend Programming courses on my career timeline."
categories:
  - "Software & Backend Engineering"
tags:
  - Node.js
  - Express
  - Backend
  - JavaScript
  - REST API
---

This post covers the basics of building a **backend in Node.js with Express**: what it is, how to run a server, define routes, use middleware, and handle request/response. I learned these concepts in the **Backend Programming I and II** courses (Coderhouse) that appear on my [career timeline](/index.html#career).

---

## 1. What is a Node.js backend?

A **backend** is the server-side part of an application: it receives HTTP requests, runs logic (e.g. database queries, business rules), and returns responses (JSON, HTML, etc.). A **Node.js backend** runs on the **Node.js** runtime: JavaScript (or TypeScript) on the server, using the event loop and non-blocking I/O.

Unlike Python (where you often use a separate ASGI server like uvicorn with FastAPI), in Node the **HTTP server** is built into the runtime: the `http` module (or `node:http`) creates the server. Frameworks like **Express** sit on top: they give you routes, middleware, and a simple API to handle requests.

---

## 2. What is Express?

**Express** is a **minimal, flexible framework** for Node.js to build web apps and APIs. It does not impose much structure; you define routes and middleware yourself. It is one of the most used frameworks for Node backends.

- **Routes:** Map HTTP method + path to a handler function (e.g. `GET /users` → function).
- **Middleware:** Functions that run in order; they can read/modify the request and response, or call the next middleware.
- **Request / Response:** Express wraps Node’s `req` and `res` with helpers (e.g. `res.json()`, `req.params`, `req.query`).

---

## 3. Basic setup

### 3.1 Install and run

```bash
mkdir my-api && cd my-api
npm init -y
npm install express
```

Create `index.js` (or `app.js`):

```javascript
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.send('Hello from Express');
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

Run: `node index.js`. The server listens on port 3000; `GET /` returns the string.

- **`express()`** — creates the app.
- **`app.get(path, handler)`** — registers a route for GET requests.
- **`app.listen(port, callback)`** — starts the Node HTTP server and binds the Express app to it.

---

## 4. Routes

Routes are defined by **method** and **path**. The handler receives `(req, res)` (and optionally `next`).

| Method | Example | Use |
|--------|---------|-----|
| **GET** | `app.get('/users', ...)` | Read data. |
| **POST** | `app.post('/users', ...)` | Create data (body in `req.body`). |
| **PUT** / **PATCH** | `app.put('/users/:id', ...)` | Update data. |
| **DELETE** | `app.delete('/users/:id', ...)` | Delete data. |

Example with params and query:

```javascript
app.get('/users/:id', (req, res) => {
  const { id } = req.params;           // URL param, e.g. /users/42 → id = "42"
  const { sort } = req.query;          // Query string, e.g. ?sort=name
  res.json({ userId: id, sort });
});
```

- **`req.params`** — URL parameters (e.g. `:id` in the path).
- **`req.query`** — query string (e.g. `?key=value`).
- **`res.json(obj)`** — sends a JSON response and sets `Content-Type: application/json`.

---

## 5. Middleware

**Middleware** is a function with signature `(req, res, next)`. It runs in the order you register it. It can:

- Read or modify `req` and `res`.
- End the response (e.g. `res.send()`, `res.json()`) — then no later handler runs.
- Call **`next()`** to pass control to the next middleware or route.

Common uses: body parsing, logging, CORS, authentication.

### 5.1 Body parsing

To read JSON in the request body (e.g. for POST), use the built-in middleware:

```javascript
app.use(express.json());   // parses Content-Type: application/json
app.use(express.urlencoded({ extended: true }));  // for form data
```

After that, `req.body` is available in route handlers.

### 5.2 Global vs route-level middleware

- **`app.use(middleware)`** — runs for every request (global).
- **`app.use('/api', middleware)`** — runs only for paths starting with `/api`.
- **`app.get('/path', middleware, handler)`** — runs only for that route.

Example: simple logger

```javascript
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});
```

---

## 6. Request and response (basics)

- **Request:** `req.method`, `req.url`, `req.path`, `req.params`, `req.query`, `req.body`, `req.headers`.
- **Response:** `res.send()`, `res.json()`, `res.status(code)`, `res.sendFile()`, `res.redirect()`.

Example: POST with validation and status code

```javascript
app.post('/items', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: 'name is required' });
  }
  res.status(201).json({ id: 1, name });
});
```

---

## 7. Summary table

| Concept | In Express |
|---------|------------|
| **Runtime** | Node.js (built-in HTTP server) |
| **Framework** | Express |
| **Server** | `app.listen(port)` — Node’s `http` under the hood |
| **Routes** | `app.get()`, `app.post()`, etc. with path + handler |
| **Params** | `req.params` (URL), `req.query` (query string) |
| **Body** | `req.body` after `express.json()` (or urlencoded) |
| **Middleware** | `app.use(fn)` or per-route; `next()` to continue |
| **Response** | `res.send()`, `res.json()`, `res.status()` |
| **Comparison** | No separate “ASGI server” like Python; Express + Node = server + app |

---

This post summarises the basics of a Node.js backend with Express (server, routes, middleware, req/res). I learned this in the **Backend Programming I: Advanced Backend Development** and **Backend Programming II: Backend Design & Architecture** courses (Coderhouse), which you can see on my [career timeline](/index.html#career).
