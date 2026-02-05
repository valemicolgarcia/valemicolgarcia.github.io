# Nutrition Label Agent

**Habits** · Subproject: *LangChain, LangGraph, Gemini Vision, Tavily, FastAPI, Pydantic*

---

## What is it for?

It lets **Habits** app users upload a **photo of a nutrition label** (packaging, nutrition facts panel) and get in seconds:

- **Product name** and **main ingredients**
- **NOVA classification** (1–4) and whether it is **ultra-processed**
- **Health score** (1–10) and a **brief analysis**
- If ultra-processed: a suggested **healthier alternative** (web search)

This helps users decide what to eat with better information and replace ultra-processed products with better options.

---

## How does it work?

1. The user uploads an image from the **Nutrition** section of Habits (button "Upload nutrition label photo").
2. The frontend sends the image to the **Nutrition Label Agent** microservice via `POST /analyze-label`.
3. The agent runs a **graph** (LangGraph) with three logical steps:
   - **Analyzer:** The image is sent to **Gemini (vision)** with a prompt that requests a JSON: product, NOVA category, whether it's ultra-processed, main ingredients, and brief reasoning. The response is validated with **Pydantic** (`AnalysisResult`).
   - **Decision:** If the analysis says "ultra-processed", the flow goes to the **Searcher**; otherwise it goes straight to the **Finalizer**.
   - **Searcher (only when applicable):** **Tavily** is used to search for healthier alternatives on the web; results are filtered and **Gemini** extracts a single suggested food name.
   - **Finalizer:** The final report is built (product, NOVA, score, analysis, alternative if a search was done, warnings) and validated with **Pydantic** (`NutritionalResponse`).
4. The API returns that JSON to the frontend, which displays the result (NOVA, score, ingredients, warnings, and healthier alternative).

The whole flow is orchestrated by **LangGraph** (nodes and conditional edges); **LangChain** is used to connect to Gemini and Tavily.

---

## Implementation

- **API:** **FastAPI** with a single analysis endpoint (`POST /analyze-label`) and health check. The image is sent as `multipart/form-data`, converted to base64, and injected into the graph's initial state.
- **Graph:** Defined in `graph.py` with **LangGraph** (`StateGraph`): nodes `analyzer`, `searcher`, `finalizer`; entry at `analyzer`; conditional edge based on `is_ultra_processed`; state is passed from node to node (image, analysis, search results, final report).
- **Nodes:** In `nodes.py`: `analyzer_node` calls **Gemini** (multimodal message: prompt + base64 image), parses JSON and validates with **Pydantic**; `searcher_node` uses **Tavily** (LangChain) and optionally Gemini to extract the alternative's name; `finalizer_node` builds the report and validates it with **Pydantic**.
- **Models:** In `models.py`, **Pydantic** defines `AnalysisResult` (analyzer output) and `NutritionalResponse` (API response).
- **Deployment:** Standalone Python service (Docker), configured with `GOOGLE_API_KEY` and `TAVILY_API_KEY`; the frontend uses `VITE_LABEL_ANALYZER_API_URL` to point to the microservice.

In summary: **LangChain** for Gemini and Tavily, **LangGraph** for the agent flow, **Gemini Vision** to analyze the label, **Tavily** to search for alternatives, **FastAPI** to expose the API, and **Pydantic** to validate inputs and outputs.
