---
layout: post
title: "What is RAG and how it is implemented in Nutri-AI"
date: 2026-01-31
excerpt: "What an LLM is, what RAG (Retrieval-Augmented Generation) is, why embeddings are used, and how RAG is implemented in the Nutri-AI project: indexing, chat flow, and models used."
categories:
  - "Deep Learning & AI"
tags:
  - RAG
  - LLM
  - Embeddings
  - Nutri-AI
  - Groq
  - Hugging Face
  - LlamaIndex
---

This post explains **what RAG is** and **how it is implemented** in **Nutri-AI**: what an LLM is, why retrieval-augmented generation is used, the role of embeddings, the models chosen, and the indexing and chat flow. For a step-by-step tutorial on adding a RAG to your own project (folder structure, code, FastAPI), see [How to add a RAG to your project]({% post_url 2026-01-31-rag-tutorial-llamaindex-fastapi-groq %}).

---

## 1. What is a language model (LLM)?

A **language model** (Large Language Model, **LLM**) is an AI model trained on huge amounts of text to predict the next word or token. It can generate coherent text, answer questions, and follow instructions, but **it only “knows” what it saw during training**. It has no access to your PDFs, databases, or private documents unless you put them in the prompt.

Examples: GPT-4, Claude, Llama, Gemini. In **Nutri-AI** we use **Llama 3.1** via **Groq** as the LLM to generate answers.

---

## 2. What is RAG?

**RAG = Retrieval-Augmented Generation.**

- **Problem:** The LLM does not “know” your documents (e.g. nutrition and training PDFs).
- **Idea:** Instead of training the model on your data or sending everything in the prompt, for each question:
  1. **Retrieve** the most relevant chunks from your documents.
  2. **Augment** the LLM’s prompt with that context (plain text).
  3. **Generate** the answer with the LLM using that context.

So the LLM answers **using your data** without that data being part of its training.

---

## 3. Why embeddings are used in RAG

You have many PDFs with a lot of text. You cannot send all of it to the LLM on every question (context limit, cost, speed). You need to **choose** only the relevant chunks.

- **Embeddings** are numerical vectors that represent the “meaning” of text. Similar texts have similar vectors.
- Document chunks are **vectorised** when indexing, and the user’s **question** is vectorised when searching.
- With **semantic search** (e.g. similarity between vectors), the most relevant chunks for the question are found.
- Those chunks are retrieved as **plain text** and passed to the LLM as context. The LLM **does not read vectors**; it only reads the retrieved text.

Summary: embeddings are used to **find** which text is relevant; the LLM receives only that filtered text.

---

## 4. Models used in Nutri-AI

| Role | Model / service | Use |
|------|------------------|-----|
| **Embeddings** | Hugging Face **BAAI/bge-small-en-v1.5** | Vectorise PDF chunks when indexing and the question when searching. |
| **LLM** | **Groq** with **Llama 3.1 8B Instant** | Receives question + context (plain text) and generates the answer. |

- **Embeddings:** Local, free, no Hugging Face API key needed for inference.
- **LLM:** Groq API (free with limits), requires **GROQ_API_KEY**.

---

## 5. How RAG is implemented in Nutri-AI

### 5.1 Indexing (on startup or when no index exists)

- **Documents:** PDFs in `data_source/` (or a dummy document if there are no PDFs).
- **Loading:** **SimpleDirectoryReader** (LlamaIndex) reads the PDFs.
- **Embeddings:** Each chunk is vectorised with **HuggingFaceEmbedding** (`BAAI/bge-small-en-v1.5`).
- **Index:** A **VectorStoreIndex** is built and persisted in `storage/` so it is not re-built on every restart.

### 5.2 When the user sends a message (POST /chat)

- **Input:** `message` (current question) and `chat_history` (history sent by the frontend).
- **Memory:** `_build_memory_from_history(chat_history)` builds a LlamaIndex **ChatMemoryBuffer** with the history (only for this request).
- **Retrieval:** The question is vectorised with the same embedding model; the index is queried and the most relevant chunks are returned as **plain text**.
- **Augmentation:** That text is used as context in the chat engine prompt (`condense_plus_context`).
- **Generation:** The **chat engine** calls the LLM (Groq / Llama 3.1) with context + history + question; the LLM returns the answer as text.
- **Output:** The answer is returned to the client (e.g. in JSON from `main.py`).

### 5.3 Where the code lives

- **`ai_engine.py`:** All RAG logic (index, embeddings, LLM, document loading, memory buffer, chat engine).
- **`main.py`:** FastAPI server that receives `POST /chat`, validates the body, and calls `ai_engine.chat(message, chat_history)`.

History is not stored on the backend; the frontend keeps it and sends it with each request.

---

This post summarised what an LLM is, what RAG is, why embeddings are used, and how RAG is implemented in **Nutri-AI**. For a step-by-step guide to add a RAG to your own project (folders, dependencies, `ai_engine.py`, `main.py`), see [How to add a RAG to your project — step-by-step with LlamaIndex, FastAPI, and Groq]({% post_url 2026-01-31-rag-tutorial-llamaindex-fastapi-groq %}).
