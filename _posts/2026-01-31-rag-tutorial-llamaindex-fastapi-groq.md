---
layout: post
title: "How to add a RAG to your project — step-by-step with LlamaIndex, FastAPI, and Groq"
date: 2026-01-31
excerpt: "Simplified tutorial to add a RAG (Retrieval-Augmented Generation) to a project: folder structure, dependencies, env vars, LlamaIndex engine, FastAPI endpoint, and how it was done in Nutri-AI."
categories:
  - "Deep Learning & AI"
tags:
  - RAG
  - LlamaIndex
  - FastAPI
  - Groq
  - Nutri-AI
  - Hugging Face
  - LLM
---

This post is a **simplified step-by-step** to add a **RAG** (Retrieval-Augmented Generation) to a project using **LlamaIndex**, **FastAPI**, **Groq**, and **Hugging Face embeddings**. It follows the approach used in **Nutri-AI** (where a RAG was added for chat over documents). You can adapt these steps to your own project even if you are new to RAG.

---

## 1. Folder structure

Create (or use) these folders at the **root** of your project:

```
your-project/
├── data_source/     # Put your PDFs (or documents) to index here
├── storage/         # Created automatically; vector index is persisted here
├── ai_engine.py     # RAG engine (index, embeddings, LLM, chat)
├── main.py          # FastAPI server exposing POST /chat
├── requirements.txt
├── .env.example
└── .env             # Do not commit to Git; copy from .env.example with your keys
```

- **data_source:** You (or the user) put PDFs here. The service indexes them automatically.
- **storage:** LlamaIndex uses it to store the index; if you delete it, the index is rebuilt on the next run.

---

## 2. Dependencies (`requirements.txt`)

Include at least:

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
pydantic>=2.0.0

llama-index
llama-index-core
llama-index-llms-groq
llama-index-embeddings-huggingface
llama-index-readers-file

pypdf>=4.0.0
```

- **FastAPI + Uvicorn:** HTTP API.
- **LlamaIndex:** index, embeddings, LLM, chat engine.
- **llama-index-llms-groq:** Groq LLM (e.g. Llama 3.1).
- **llama-index-embeddings-huggingface:** local embeddings (e.g. BAAI/bge-small-en-v1.5).
- **pypdf:** so SimpleDirectoryReader can read PDFs.

Install:

```bash
pip install -r requirements.txt
```

---

## 3. Environment variables

Create `.env.example` with what the user must configure:

```
GROQ_API_KEY=your-groq-api-key
# RAG_DATA_SOURCE=data_source
# RAG_STORAGE=storage
```

Copy to `.env` and set **GROQ_API_KEY** (free key at https://console.groq.com/keys).

In your code, load `.env` at the start of the RAG engine (e.g. in `ai_engine.py`):

```python
from dotenv import load_dotenv
load_dotenv()
```

Use env vars for optional paths:

```python
import os
from pathlib import Path

DATA_SOURCE_DIR = Path(os.getenv("RAG_DATA_SOURCE", "data_source"))
STORAGE_DIR = Path(os.getenv("RAG_STORAGE", "storage"))
DATA_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
```

---

## 4. RAG engine (`ai_engine.py`)

Implement these pieces in order.

### 4.1 LLM (model that generates answers)

Function that returns the configured LLM (here Groq with Llama 3.1):

```python
def _get_llm():
    from llama_index.llms.groq import Groq  # or from llama_index_llms_groq import Groq
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.2)
```

### 4.2 Embedding model (vectorise text)

Function that returns the embedding model (Hugging Face, local):

```python
def _get_embed_model():
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    return HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        trust_remote_code=True,
    )
```

### 4.3 Load documents

Function that reads all PDFs from `data_source/`:

```python
def _load_documents():
    from llama_index.core import SimpleDirectoryReader
    if not DATA_SOURCE_DIR.exists():
        return []
    pdf_files = list(DATA_SOURCE_DIR.glob("**/*.pdf"))
    if not pdf_files:
        return []
    reader = SimpleDirectoryReader(
        input_dir=str(DATA_SOURCE_DIR),
        required_exts=[".pdf"],
        recursive=True,
    )
    return reader.load_data()
```

If you want, when there are no PDFs you can create a dummy document with generic text so the index exists and the LLM can still answer with general knowledge.

### 4.4 Create or load the index

- If `storage/docstore.json` exists, load the index from `storage/`.
- Otherwise, load documents, build a **VectorStoreIndex** with the embedding model, persist to `storage/`, and return the index.

Set **Settings.llm** and **Settings.embed_model** with `_get_llm()` and `_get_embed_model()` before creating or loading the index.

```python
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings, Document

def get_or_create_index():
    Settings.llm = _get_llm()
    Settings.embed_model = _get_embed_model()
    if (STORAGE_DIR / "docstore.json").exists():
        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(STORAGE_DIR))
            return load_index_from_storage(storage_context)
        except Exception:
            pass
    documents = _load_documents()
    if not documents:
        documents = [Document(text="Dummy text or general instructions...")]
    index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
    index.storage_context.persist(persist_dir=str(STORAGE_DIR))
    return index
```

### 4.5 Conversation memory (chat history)

Function that turns a list of messages `[{"role": "user"|"assistant", "content": "..."}]` into a LlamaIndex **ChatMemoryBuffer**:

```python
def _build_memory_from_history(chat_history: list[dict[str, str]]):
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core.llms import ChatMessage, MessageRole
    memory = ChatMemoryBuffer.from_defaults()
    for msg in (chat_history or []):
        role_str = (msg.get("role") or "user").lower()
        content = msg.get("content") or ""
        if not content:
            continue
        role = MessageRole.USER if role_str == "user" else MessageRole.ASSISTANT
        memory.put(ChatMessage(role=role, content=content))
    return memory
```

The frontend keeps the history and sends it with each request; the backend does not persist sessions.

### 4.6 Chat function (main RAG entry point)

Function that takes the current message and history, and returns the reply as text:

```python
def chat(message: str, chat_history: list[dict[str, str]] | None = None) -> str:
    index = get_or_create_index()
    memory = _build_memory_from_history(chat_history or [])
    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=memory,
        verbose=False,
    )
    response = chat_engine.chat(message)
    return str(response)
```

**condense_plus_context** turns history + question into a standalone query, retrieves context from the index, and generates the answer with the LLM.

---

## 5. FastAPI API (`main.py`)

### 5.1 App and CORS

Create the app and configure CORS for your frontend (localhost, production, etc.):

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 Pydantic models

Define the POST body and response:

```python
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: list[ChatMessage] | None = []

class ChatResponse(BaseModel):
    response: str
```

### 5.3 POST /chat endpoint

Accepts `message` and `chat_history`, validates, calls the RAG engine, and returns the reply:

```python
from ai_engine import chat as rag_chat

@app.post("/chat", response_model=ChatResponse)
def post_chat(body: ChatRequest):
    if not (body.message or "").strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    history = [{"role": m.role, "content": m.content} for m in (body.chat_history or [])]
    try:
        response_text = rag_chat(message=body.message.strip(), chat_history=history)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(response=response_text)
```

Optional: `GET /` and `GET /health` to check that the service is up.

---

## 6. Run the service

1. Put at least one PDF in `data_source/` (or rely on a dummy document if you added that).
2. Have `.env` with **GROQ_API_KEY**.
3. Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

4. Test from the frontend or with curl:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How much protein do I need?", "chat_history": []}'
```

---

## 7. Flow summary

1. **Indexing (once):** PDFs in `data_source/` → SimpleDirectoryReader → chunks → embeddings (Hugging Face) → VectorStoreIndex → persist in `storage/`.
2. **Each question:** Frontend sends `message` + `chat_history` → backend builds memory with `_build_memory_from_history` → chat engine (condense_plus_context) retrieves context from the index → LLM (Groq) generates the answer → backend returns `{ "response": "..." }`.
3. The frontend stores the history; the backend only uses it for that request.

---

This tutorial follows the same scheme used in **Nutri-AI**, where a RAG was added for chat over documents: LlamaIndex, Groq, Hugging Face embeddings, persisted index, and chat with history via FastAPI. With these steps you can add a RAG to your own project from scratch.
