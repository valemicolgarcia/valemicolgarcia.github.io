---
layout: post
title: "LangChain: theory and implementation in a nutritional label analyzer"
excerpt: "What LangChain is (models, messages, tools), how it relates to LangGraph, and how it is used inside the nodes of a nutritional label analyzer microservice (Gemini, Tavily)."
categories:
  - "Deep Learning & AI"
order: 8
tags:
  - LangChain
  - LangGraph
  - LLM
  - Gemini
  - Tavily
  - Nutritional Labels
  - Agents
---

This post describes **what LangChain is** (theory) and **how it is used** in the microservice that analyzes **nutritional labels**.

---

## Part 1: What is LangChain?

**LangChain** is an open-source framework for building applications that use **language models (LLMs)** and **external tools**. It does not replace the model or the APIs; it provides an **abstraction layer** to connect them with your business logic and to handle prompts, messages, and tools in a uniform way.

### Main goals

- **Unify interfaces:** different providers (OpenAI, Google Gemini, Anthropic, etc.) are used with the same API: create the model, invoke it with messages, read the response.
- **Compose flows:** chain model calls with tools (search, databases, code) and with your own code.
- **Handle messages:** represent conversations (human, assistant, system) and multimodal content (text + images) in a standard format.

### Main concepts

#### 1. Models (LLMs / Chat Models)

- They are the **AI engines** you talk to (e.g. GPT-4, Gemini, Claude).
- In LangChain they are created as configurable objects (API key, model, temperature, etc.).
- You **invoke** them with a list of messages and they return a response (object with `.content`, etc.).
- Each provider has its own package: `langchain_google_genai`, `langchain_openai`, etc.

#### 2. Messages

- They represent each “turn” in a conversation: **HumanMessage** (user), **AIMessage** (assistant), **SystemMessage** (system instructions).
- They can be **multimodal:** text + image (e.g. content with `type: "text"` and `type: "image_url"`).
- Models receive a list of messages and return a response message.

#### 3. Tools

- Functions or external services that the model or your code can use: web search, APIs, databases, etc.
- In LangChain they usually have a standard interface: they are **invoked** with a dictionary of arguments (e.g. `{"query": "..."}`) and return a result.
- They let the application combine **LLM reasoning** with **real-time data** (e.g. internet search).
- **Important:** the **model** (e.g. Gemini) is not a tool. The model is the LLM that “thinks” and generates text (or chooses to call a tool). **Tools** are actions that someone (your code or the agent) invokes: search, calculator, API, etc.

### Models and tools available in LangChain

LangChain provides **integrations** with many providers. The full list is in the [official documentation](https://python.langchain.com/docs/integrations/). Here is a summary by category.

#### Models (LLMs / Chat Models)

Each lives in a separate package. All expose the same idea: create the model, call `.invoke(messages)`, and read `.content`.

| Provider | Package | Example model / class |
|----------|---------|------------------------|
| Google | `langchain_google_genai` | `ChatGoogleGenerativeAI` (Gemini) |
| OpenAI | `langchain_openai` | `ChatOpenAI` (GPT-4, etc.) |
| Anthropic | `langchain_anthropic` | `ChatAnthropic` (Claude) |
| Cohere | `langchain_cohere` | `ChatCohere` |
| Mistral | `langchain_mistralai` | `ChatMistralAI` |
| Groq | `langchain_groq` | `ChatGroq` |
| Ollama | `langchain_community` | `ChatOllama` (local models) |
| Azure OpenAI | `langchain_openai` | `AzureChatOpenAI` |

There are more (Fireworks, Together, etc.); the pattern is always: integration package + chat model class.

#### Tools

Tools are usually in `langchain_community.tools.*` or in specific packages. Some categories:

| Category | Examples (classes / integrations) |
|----------|-----------------------------------|
| Web search | `TavilySearchResults`, `DuckDuckGoSearchRun`, `GoogleSearchRun`, `SerperAPIWrapper` |
| APIs / HTTP | Generic tools to call APIs; also concrete integrations (Wikipedia, etc.) |
| Code / shell | `PythonREPLTool`, `ShellTool` (with security care) |
| Databases | Tools for SQL, vectors, etc. |
| Custom | You can define your own tools with `@tool` or by implementing the interface |

Each tool is invoked with `.invoke({...})` with the arguments that tool expects (e.g. `{"query": "..."}` for search).

#### What we use in the nutritional label analyzer

In this project (the **nutritional label analyzer**) we only use **one model** and **one tool** from LangChain:

| Type | LangChain integration | Use in the project |
|------|------------------------|---------------------|
| **Model** | `ChatGoogleGenerativeAI` (package `langchain_google_genai`) | Gemini: image analysis of the label (analyzer node) and extraction of the healthier-alternative name (searcher node). |
| **Tool** | `TavilySearchResults` (package `langchain_community`) | Web search for healthier alternatives to the product (searcher node). |

We do not use the LangChain agent (which “binds” the model to a list of tools so it decides when to call them); we define the flow ourselves with **LangGraph**, and in each node we invoke the model or the tool explicitly.

#### 4. Chains and agents (optional)

- **Chains:** fixed sequences of steps (prompt → model → maybe another tool). The order is defined by you in code.
- **Agents:** flows where **the model itself decides** at each step whether to call a tool, which one, and with what arguments. LangChain includes this “classic” agent; in this project we use **LangGraph** for orchestration, not the LangChain agent (see below).

### The built-in LangChain agent (and why we use LangGraph here)

LangChain has the notion of an **agent**: a loop where the **LLM makes all the decisions** about the flow.

**How the LangChain agent works:**

1. You give the model a list of **tools** with name and description. The model “knows” it can use them.
2. You send the user message (e.g. “Analyze this label and search for healthier alternatives”).
3. The model responds with **text** or with a **tool call**: it chooses a tool and arguments (e.g. `tavily_search(query="alternatives to oreo cookies")`).
4. If there was a tool call, LangChain runs that tool and **feeds the result back into the conversation** as a message (“the search result was: …”).
5. The model sees that result and **decides again**: it can answer the user or make another tool call. The loop continues until the model returns a final text response (no tool call).

That pattern is often called **ReAct** (Reasoning + Acting): the model “thinks” and “acts” (uses tools) in cycles. You do not write the flow step by step; the flow is determined by the model on each run.

**Why we do not use that agent in this project:**

- We want a **fixed, predictable flow**: first always analyze the image with Gemini; then, **only if** the analysis says “ultra-processed”, search for alternatives with Tavily; finally, consolidate. That is a **business rule** (clear logic), not something we want the LLM to “invent” on each call.
- With the LangChain agent, the model might decide to search when it should not, not search when it should, or call tools in a different order. Behaviour would be more flexible but less controlled.
- With **LangGraph** we define **nodes** (analyzer, searcher, finalizer) and **conditional edges** in code. The rule “if ultra-processed → search; else → finalize” is written by us, not inferred by the model. The nodes still use **LangChain** (Gemini model and Tavily tool), but **who does what and when** is defined by the graph.

**Summary:** The LangChain agent = “the model decides at each step whether to use a tool and which one”. Our approach with LangGraph = “we define the flow and the conditions; inside each step we use LangChain to call the model and the tools”. That gives us explicit control over order and business logic.

### Relation to LangGraph

- **LangChain** provides the “building blocks”: the model (Gemini), the tool (Tavily), messages (`HumanMessage`).
- **LangGraph** defines the flow: in what order the steps run and how state is passed between nodes.
- In practice: the **nodes** of the graph are functions that, internally, use LangChain to call the model and the tools. The API (FastAPI) does not import LangChain; it only invokes the graph.

---

## Part 2: Implementation in the nutritional label analyzer

LangChain is **only used inside the nodes** of the graph, in the file `nodes.py`. The API (`main.py`) and the graph definition (`graph.py`) do not import LangChain.

### 2.1 Dependencies (requirements.txt)

```
langchain>=0.1.0
langchain-google-genai>=1.0.0
langchain-community>=0.0.20
```

- **langchain:** core and conventions.
- **langchain-google-genai:** integration with Google Gemini (chat model with vision support).
- **langchain-community:** third-party tools, including Tavily search.

LangGraph also uses components from **langchain_core** (e.g. messages), which usually come as a dependency of the packages above.

### 2.2 Model: Gemini (langchain_google_genai)

The model is created in `nodes.py` with `ChatGoogleGenerativeAI`:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.3,
    )
```

- **Use:** `get_gemini_model()` is called inside the **analyzer** and **searcher** nodes.
- **Role:** connect to the Google Gemini API using the standard LangChain interface (object with `.invoke(messages)`).

### 2.3 Messages: HumanMessage (langchain_core)

Messages are used to send both text and image (multimodal content) to the model.

In the **analyzer** node a message is built with text + base64 image:

```python
from langchain_core.messages import HumanMessage

message = HumanMessage(
    content=[
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{state['image_data']}",
        },
    ]
)

response = model.invoke([message])
response_text = response.content.strip()
```

- **HumanMessage:** represents the “user” turn (here, our prompt + the label photo).
- **content:** list of blocks; here, a text block (NOVA analysis prompt) and an image block (data URI in base64).
- **model.invoke([message]):** standard LangChain interface to send a list of messages and get the model response.

In the **searcher** node only text is sent (no image):

```python
resp = model.invoke([prompt])  # prompt is a string; LangChain treats it as user message
nombre = (resp.content or "").strip()
```

### 2.4 Tool: Tavily (langchain_community)

Web search is done with the Tavily tool, exposed as a “tool” in LangChain:

```python
from langchain_community.tools.tavily_search import TavilySearchResults

def get_tavily_tool():
    api_key = os.getenv("TAVILY_API_KEY")
    return TavilySearchResults(
        max_results=8,
        tavily_api_key=api_key,
    )
```

In the **searcher** node it is used like this:

```python
tool = get_tavily_tool()
results = tool.invoke({"query": query})
```

- **invoke({"query": ...}):** standard tool interface in LangChain; here the tool calls the Tavily API and returns a list of results (title, URL, content).
- The rest of the node (filter results, prioritise, extract a name with Gemini) is project-specific logic; LangChain only provides the connection to Tavily.

### 2.5 Where LangChain is used (summary)

| LangChain component | File | Use in the project |
|---------------------|------|--------------------|
| **ChatGoogleGenerativeAI** | `nodes.py` | Gemini model: image analysis (analyzer) and alternative name extraction (searcher). |
| **HumanMessage** | `nodes.py` | Multimodal message (text + image) in analyzer; in searcher only text via string. |
| **TavilySearchResults** | `nodes.py` | Web search for healthier alternatives in searcher. |
| **model.invoke(...)** | `nodes.py` | Model call in both nodes that use Gemini. |
| **tool.invoke(...)** | `nodes.py` | Tavily tool call in searcher. |

- **main.py:** does not import LangChain; only prepares state and invokes the graph.
- **graph.py:** does not import LangChain; only defines nodes and edges. The nodes are functions that, when run, use LangChain internally.

### 2.6 Data flow with LangChain

1. **Analyzer:**  
   State with `image_data` (base64) → create `HumanMessage` (prompt + image) → `model.invoke([message])` (Gemini) → parse JSON and update `state["analysis"]`.

2. **Searcher:**  
   State with `analysis["producto"]` → `tool.invoke({"query": ...})` (Tavily) → filter and prioritise in Python → `model.invoke([prompt])` (Gemini) to extract a name → update `state["search_results"]`.

3. **Finalizer:**  
   Does not use LangChain; only reads state and builds `final_report`.

---

## Conclusion

- **Theory:** LangChain is a framework to connect LLMs and tools to your application through standard interfaces (models, messages, tools, and invoke).
- **In this project (the nutritional label analyzer):** LangChain is used only in `nodes.py`: to connect to **Gemini** (vision and text model) and **Tavily** (web search), and to build the **multimodal message** that Gemini receives in the analyzer. The flow and state are orchestrated by **LangGraph**; the API exposes them via **FastAPI**.

For how the flow and state are defined (graph, nodes, conditional edges), see [LangGraph: theory and implementation in a nutritional label analyzer]({% post_url 2026-01-31-langgraph-theory-and-implementation %}).
