---
layout: post
title: "What is LlamaIndex?"
date: 2026-01-31
excerpt: "LlamaIndex is an open-source framework for building apps that connect your data (documents, PDFs, databases) with LLMs. It orchestrates indexing, semantic search, and context for RAG. How it is used in Nutri-AI."
categories:
  - "Deep Learning & AI"
tags:
  - LlamaIndex
  - RAG
  - LLM
  - Nutri-AI
  - Groq
  - Hugging Face
  - Embeddings
---

**LlamaIndex** is an open-source framework for building applications that connect **your data** (documents, PDFs, databases) with **language models (LLMs)**. It is not a model itself: it is the “orchestration” that lets you index documents, search by meaning, and give context to the LLM so it can answer.

It is mainly used for **RAG (Retrieval-Augmented Generation)**: loading documents, creating vector indexes, retrieving relevant chunks, and passing them to the LLM to generate answers.

---

## 1. What LlamaIndex “includes”: LLM integrations

LlamaIndex **does not include** the models inside the package. It provides a **unified interface** to connect to many external providers via optional packages (`llama-index-llms-*`). Each provider is a separate integration.

Some LLM integrations it supports:

| Provider / type | Typical package | Example models |
|------------------|------------------|----------------|
| **Groq** | `llama-index-llms-groq` | Llama 3.1, Mixtral |
| **OpenAI** | `llama-index-llms-openai` | GPT-4, GPT-3.5 |
| **Anthropic** | `llama-index-llms-anthropic` | Claude |
| **Google** | `llama-index-llms-gemini` | Gemini |
| **Hugging Face** | `llama-index-llms-huggingface` | Local / remote models |
| **Cohere** | `llama-index-llms-cohere` | Command R, etc. |
| **Mistral** | `llama-index-llms-mistralai` | Mistral, Mixtral |
| **Azure OpenAI** | `llama-index-llms-azure-openai` | GPT via Azure |
| **Ollama** | `llama-index-llms-ollama` | Local models |
| **LlamaCPP** | `llama-index-llms-llama-cpp` | Local GGUF models |
| **LiteLLM** | `llama-index-llms-litellm` | Many providers |

And more (Bedrock, Fireworks, etc.). The full list is in the LlamaIndex docs under “LLM integrations”.

---

## 2. Hugging Face embeddings

LlamaIndex lets you use **embedding models** from Hugging Face to turn text into vectors. Those vectors are used to build the index and do semantic search (find chunks relevant to a question).

- Typical package: `llama-index-embeddings-huggingface`
- The model runs **locally** (or on your server), with no Hugging Face API key needed for inference.
- In **Nutri-AI** we use **BAAI/bge-small-en-v1.5** to index PDFs and to vectorise the user’s question when searching.

---

## 3. Memory buffer (chat history)

LlamaIndex includes **ChatMemoryBuffer** and related classes to keep conversation history in memory during a chat session. That allows:

- Follow-up questions (“What if I exercise a lot?”).
- The engine to know what was said before (user and assistant).

In **Nutri-AI** the history is not stored on the backend: the frontend sends `chat_history` with each request. The function `_build_memory_from_history` in `ai_engine.py` turns that list of messages into a LlamaIndex **ChatMemoryBuffer** for that single request. So LlamaIndex gives you the memory buffer via **ChatMemoryBuffer**, **ChatMessage**, and **MessageRole**, and you rebuild the history from what the client sends.

---

## 4. What LlamaIndex is used for in Nutri-AI

All in **`ai_engine.py`**:

| Use in Nutri-AI | LlamaIndex module / class |
|-----------------|---------------------------|
| LLM (generate answers) | `llama_index.llms.groq` → **Groq** (model `llama-3.1-8b-instant`) |
| Embeddings (vectorise text) | `llama_index.embeddings.huggingface` → **HuggingFaceEmbedding** (`BAAI/bge-small-en-v1.5`) |
| Load PDFs | `llama_index.core` → **SimpleDirectoryReader**, **Document** |
| Vector index and persistence | **VectorStoreIndex**, **StorageContext**, **load_index_from_storage**, **Settings** |
| Chat history (memory buffer) | **ChatMemoryBuffer**, **ChatMessage**, **MessageRole** |
| RAG chat engine | **index.as_chat_engine** with `chat_mode="condense_plus_context"` and `memory` |

Dependencies in `requirements.txt`:

- `llama-index`
- `llama-index-core`
- `llama-index-llms-groq`
- `llama-index-embeddings-huggingface`
- `llama-index-readers-file`

`main.py` does not import LlamaIndex; it only calls `ai_engine.chat()`.

---

This post summarised what LlamaIndex is, its LLM and embedding integrations, the memory buffer, and how it is used in **Nutri-AI**. For what RAG is and how it is implemented in Nutri-AI, see [What is RAG and how it is implemented in Nutri-AI]({% post_url 2026-01-31-what-is-rag-nutri-ai %}). For a step-by-step tutorial to add a RAG to your project, see [How to add a RAG to your project]({% post_url 2026-01-31-rag-tutorial-llamaindex-fastapi-groq %}).
