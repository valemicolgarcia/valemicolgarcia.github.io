---
layout: post
title: "LangGraph: theory and implementation in a nutritional label analyzer"
excerpt: "What LangGraph is (state graphs, nodes, edges), how it relates to LangChain, and how it was implemented in a microservice that analyzes nutritional labels with Gemini and Tavily."
categories:
  - "Deep Learning & AI"
order: 7
tags:
  - LangGraph
  - LangChain
  - Agents
  - LLM
  - Gemini
  - Nutritional Labels
  - Tavily
---

This post explains **what LangGraph is** (theory) and **how it was implemented** in a microservice that analyzes **nutritional labels**: image analysis with Gemini, optional search for healthier alternatives with Tavily, and consolidation of the final report.

---

## Part 1: What is LangGraph?

**LangGraph** is a library in the LangChain ecosystem that lets you build **agents and workflows** modelled as **stateful graphs**. Instead of a linear chain of steps, you define **nodes** (functions) and **connections** between them; **state** is passed from node to node and can determine which path to take.

### Main concepts

#### 1. State

- A **shared dictionary** that flows through the whole graph.
- Each node receives the current state, can read it and **return updates** (new keys or values).
- LangGraph **merges** each node’s return value with the previous state (by default, key-wise merge).

In short: state is the “memory” of the flow; all nodes read from and write to it.

#### 2. Nodes

- **Functions** that receive the state and return a dictionary with the **parts of the state they update**.
- Each node does a concrete task: call an LLM, use a tool, compute something, etc.
- Nodes do not know the graph; they only receive state and return updates.

#### 3. Edges (connections)

- **Fixed edge:** always go from node A to node B.
- **Conditional edge:** a function receives the state and decides the **next node** (e.g. "search" or "finalize"). This is how branches and decisions are implemented.

#### 4. Entry and end

- You define an **entry point** (first node).
- The flow ends when it reaches the special **END** node.

### Advantages of LangGraph

- **Flows with conditional logic:** different paths depending on state (e.g. “only if ultra-processed, search for alternatives”).
- **Reusability:** each node is an independent function, easy to test and change.
- **Transparency:** state at each step is inspectable, useful for debugging and future improvements (logs, persistence).
- **Compatible with LangChain:** nodes can use LangChain models, tools, and messages without issue.

### Relation to LangChain

- **LangChain** provides the “building blocks”: models (e.g. Gemini), tools (e.g. Tavily), messages (`HumanMessage`).
- **LangGraph** orchestrates those blocks in a graph: in what order they run and how state is passed between them.
- In practice: LangGraph defines the **flow**; inside each node you use **LangChain** to call APIs and tools.

---

## Part 2: Implementation in the nutritional label analyzer

In this project (the **nutritional label analyzer** microservice), LangGraph is used to orchestrate the label-analysis agent: image analysis with Gemini, optional search for alternatives with Tavily, and consolidation of the final result.

### 2.1 Agent state: `AgentState`

The state is defined in `nodes.py` as a `TypedDict`:

```python
class AgentState(TypedDict):
    image_data: str      # Base64 of the image
    analysis: dict       # Result of initial analysis (Gemini)
    search_results: str  # Healthier alternative found (if applicable)
    final_report: dict   # Final report for the API
```

- **`image_data`:** filled by the API (FastAPI) before invoking the graph.
- **`analysis`:** filled by the **analyzer** node (product, NOVA category, whether ultra-processed, ingredients, reasoning).
- **`search_results`:** filled by the **searcher** node only when alternatives are searched (a food name).
- **`final_report`:** filled by the **finalizer** node with the object that is later returned to the client (and validated with `NutritionalResponse` in `models.py`).

### 2.2 Nodes (in `nodes.py`)

| Node | Function | What it does |
|------|----------|--------------|
| **analyzer** | `analyzer_node` | Receives the image in base64, sends it to Gemini with a prompt that asks for a JSON (product, categoria_nova, es_ultraprocesado, ingredientes_principales, razonamiento). Parses and validates with `AnalysisResult`. Updates `state["analysis"]`. |
| **searcher** | `searcher_node` | Runs only if the analysis says ultra-processed. Uses Tavily to search for healthier alternatives, filters unwanted results, and uses Gemini to extract a single food name. Updates `state["search_results"]`. |
| **finalizer** | `finalizer_node` | Reads `analysis` and `search_results`, builds the critical analysis text, health score (1–10), warnings, and healthier-alternative field. Assembles the final dictionary. Updates `state["final_report"]`. |

The **analyzer** and **searcher** nodes use LangChain (Gemini, Tavily, `HumanMessage`); the **finalizer** only uses the state already computed.

### 2.3 Graph (in `graph.py`)

- A **StateGraph** is created with `AgentState`:
  ```python
  workflow = StateGraph(AgentState)
  ```

- The three nodes are registered:
  ```python
  workflow.add_node("analyzer", analyzer_node)
  workflow.add_node("searcher", searcher_node)
  workflow.add_node("finalizer", finalizer_node)
  ```

- **Entry:** the flow always starts at `analyzer`:
  ```python
  workflow.set_entry_point("analyzer")
  ```

- **Conditional edge after `analyzer`:** the function `should_search(state)` reads `state["analysis"]["es_ultraprocesado"]`:
  - If `True` → next node: **searcher**
  - If `False` → next node: **finalizer** (no search for alternatives)

- **Fixed edges:**
  - `searcher` → **finalizer** (after searching, always consolidate)
  - **finalizer** → **END** (end of graph)

Flow summary:

```
        [ENTRY]
             │
             ▼
        analyzer
             │
     should_search(state)
             │
     ┌───────┴───────┐
     │               │
ultra-processed     no
     │               │
     ▼               │
  searcher           │
     │               │
     └───────┬───────┘
             ▼
        finalizer
             │
             ▼
           [END]
```

### 2.4 Use from the API (`main.py`)

The API does **not** use LangChain directly; it only uses the compiled graph:

1. Receives the image in `POST /analyze-label`.
2. Validates and converts the image to base64.
3. Builds the initial state:
   ```python
   initial_state = {
       "image_data": image_base64,
       "analysis": {},
       "search_results": "",
       "final_report": {},
   }
   ```
4. Gets the graph and runs it:
   ```python
   graph = get_nutrition_agent_graph()
   result = graph.invoke(initial_state)
   ```
5. Takes `result["final_report"]`, validates it with `NutritionalResponse`, and returns it as JSON to the client.

The graph instance is reused (singleton in `get_nutrition_agent_graph()` in `graph.py`).

### 2.5 File summary

| File | Role with respect to LangGraph |
|------|--------------------------------|
| `graph.py` | Defines the `StateGraph`, nodes, conditional and fixed edges, and exposes the compiled graph. |
| `nodes.py` | Defines `AgentState` and implements the three nodes (which use LangChain internally). |
| `models.py` | Defines `AnalysisResult` (analyzer output) and `NutritionalResponse` (equivalent to `final_report`). |
| `main.py` | Prepares the initial state, calls `graph.invoke(initial_state)`, and returns `final_report` as the API response. |

---

## Conclusion

- **Theory:** LangGraph is a framework for building flows with state, nodes, and edges (fixed or conditional), typically using LangChain inside the nodes.
- **In this project (the nutritional label analyzer):** the graph orchestrates image analysis (Gemini), optional search for alternatives (Tavily + Gemini), and consolidation of the result; the API only prepares the state, invokes the graph, and returns the `final_report`.
