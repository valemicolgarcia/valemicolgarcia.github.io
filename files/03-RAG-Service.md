# RAG Service

**Habits** · Subproject: *LlamaIndex, Groq, Llama 3.1, Hugging Face Embeddings, FastAPI*

---

## What is it for?

It provides a **question-answering assistant** inside the **Habits** app that answers about **nutrition and training** using **your own documents** (e.g. PDFs): guides, articles, recipes, etc.

The user types questions in natural language (e.g. "How much protein do I need per day?", "How can I improve recovery?") and gets answers **based on the content of those PDFs**, not only the model's built-in knowledge. The service also keeps **conversation history** so you can ask follow-up questions in the same session.

---

## How does it work?

1. On the **dashboard** of Habits there is a chat bar: "Ask about nutrition and training". The user types a message and sends it.
2. The frontend calls the **RAG Service** microservice with `POST /chat`, sending the message and `chat_history` (previous messages in the conversation).
3. The backend uses **LlamaIndex** to:
   - **Index:** PDFs in the `data_source` folder are read with `SimpleDirectoryReader` (and **pypdf**); they are split into chunks and **embeddings** are generated with a **Hugging Face** model (e.g. BGE) that runs locally, without an API key. The index is persisted in `storage` so it doesn't need to be reindexed on each restart.
   - **Retrieval:** For each question, the most relevant chunks from the index are retrieved (embedding similarity).
   - **Generation:** The retrieved context plus chat history are sent to the **LLM** (Groq with **Llama 3.1**); the model generates the answer using that context (RAG = Retrieval-Augmented Generation).
4. The response is returned to the frontend in JSON (`response`); the frontend updates the history and shows the assistant's message. So answers are grounded in the documents you upload, not only the model's base knowledge.

---

## Implementation

- **API:** **FastAPI** with endpoint `POST /chat`: body with `message` and optionally `chat_history` (list of `role` + `content`). Request/response models are validated with **Pydantic** (`ChatRequest`, `ChatResponse`, `ChatMessage`). **Uvicorn** as ASGI server; **python-dotenv** for environment variables.
- **RAG with LlamaIndex:** **LlamaIndex** is used (and packages like `llama-index-core`, `llama-index-readers-file`) to: read PDFs, build the vector index, and expose a **chat engine** with memory. The **retriever** returns the most relevant chunks; the **chat engine** combines context + history and calls the LLM.
- **LLM:** **Groq** with **Llama 3.1** model (package `llama-index-llms-groq`): fast answers and no OpenAI/Anthropic cost for the end user.
- **Embeddings:** **Hugging Face** model (e.g. `BAAI/bge-small-en-v1.5`) via `llama-index-embeddings-huggingface`, run locally on the RAG server; no external embedding API is used.
- **PDFs:** Read with **pypdf** and LlamaIndex's reader; the `data_source` and `storage` paths are configurable via environment.
- **Deployment:** Standalone Python microservice (Docker); requires `GROQ_API_KEY`. The frontend uses `VITE_RAG_API_URL` to connect to this service.

In summary: **LlamaIndex** orchestrates the RAG (index, retrieval, chat engine), **Groq** and **Llama 3.1** generate answers, **Hugging Face Embeddings** build the index locally, and **FastAPI** + **Pydantic** expose the API for **Habits**.
