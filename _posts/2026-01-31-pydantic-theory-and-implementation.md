---
layout: post
title: "Pydantic: theory and implementation"
excerpt: "What Pydantic is (BaseModel, Field, validation, serialization), why it is used in APIs, and how it is used in the nutritional label analyzer, the RAG service, and the Nutri-AI ingredient-detection backend."
categories:
  - "Software & Backend Engineering"
order: 6
tags:
  - Pydantic
  - FastAPI
  - Validation
  - Python
  - Nutritional Labels
  - Nutri-AI
  - RAG
---

This post explains **what Pydantic is** and **how it is used** in the microservice that analyzes **nutritional labels**, as well as in the **RAG service** (chat over documents) and the **Nutri-AI ingredient-detection backend**. Pydantic is used in all three backends to define data models and validate API inputs and outputs; the frontend (TypeScript/React) uses TypeScript types and interfaces, not Pydantic.

---

## Part 1: What is Pydantic?

**Pydantic** is a Python library for **validating data and defining schemas** using type annotations. It lets you describe the shape your data must have (request, response, environment variables, etc.) and automatically validates that values satisfy those rules.

### Main goals

- **Validation:** check that incoming data (dict, JSON, etc.) has the correct types and meets constraints (ranges, lengths, formats).
- **Clear schemas:** a single class definition acts as both documentation and data contract.
- **Serialization:** convert models to dictionaries or JSON and back, consistently.
- **Integration:** FastAPI uses Pydantic for request/response bodies and OpenAPI documentation.

### Main concepts

#### 1. BaseModel: the base of your schemas

**BaseModel** is a **Pydantic class** you inherit from to define a “data type with a fixed shape”. It is not an object you create by hand; it is the **template** that says: “any data that uses this class must have these fields and these types”.

**In practice:**

1. You create a class that inherits from `BaseModel`.
2. Inside you add **typed attributes** (e.g. `name: str`, `age: int`). Those attributes are the **fields** of the schema.
3. When you want to validate data (e.g. a dict from JSON or the API), you **create an instance** by passing that dict: `MyClass(**dict)`.
4. Pydantic **at instantiation time** checks that each key exists (if required), that the type is correct (str, int, etc.), and that constraints (ge, le, etc.) are met. If something fails, it raises an error; if all is well, you get an object with validated attributes.

**Minimal example:**

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str
    age: int = Field(..., ge=0, le=120)

# Data you receive (e.g. from JSON or the LLM)
data = {"name": "Ana", "age": 30}

# Create instance = validate
p = Person(**data)   # OK: name is str, age is between 0 and 120

print(p.name)        # "Ana"
print(p.age)         # 30

# If data is invalid, Pydantic raises when instantiating:
Person(**{"name": "Ana", "age": 150})   # Error: 150 > 120
Person(**{"name": "Ana"})                # Error: missing "age"
Person(**{"name": 123, "age": 30})       # Error: "name" must be str
```

**Summary:** BaseModel is the parent class that makes your class “understand” dictionaries and validate them on instantiation. You define the shape (attributes + types + Field); Pydantic checks that the data matches that shape when you do `MyModel(**dict)`.

#### 2. Field

- `Field(...)` means the field is **required** (`...` = required).
- `Field(default_value)` sets a default (e.g. `None`, `[]`).
- Numeric constraints: `ge=1, le=4` (greater-or-equal, less-or-equal), `min_length`, `max_length`, etc.
- `description` is used for documentation (e.g. in Swagger).

#### 3. Types and Optional

- Standard types: `str`, `int`, `bool`, `list[str]`, `dict`, etc.
- `Optional[str]` = the field can be `str` or `None`; often used with `Field(None)` for optional fields.

#### 4. Serialization

- **model_dump():** converts the model to a Python dictionary (useful to pass data to other modules or to JSON).
- **model_dump_json():** converts to a JSON string.
- FastAPI uses Pydantic models as `response_model` to serialize the response and validate its shape.

### Why use it here

- The agent’s response (`final_report`) must have a fixed shape for the client; Pydantic ensures it always matches the contract.
- The JSON returned by Gemini can be malformed or have wrong types; validating with a model right after the analyzer avoids errors later in the flow.

---

## Part 2: Implementation in the backends

Pydantic is used in **three backends**:

1. **Nutrition label analyzer** (agent that analyzes label images with Gemini and optionally searches for healthier alternatives): models in `models.py`, used in `main.py` and `nodes.py`.
2. **RAG service** (chat over documents with LlamaIndex + Groq): request/response models for `POST /chat`.
3. **Nutri-AI ingredient-detection backend** (FastAPI + Grounding DINO): models for detection response (e.g. `DetectedIngredient`, `DetectionResponse`).

The **frontend** (TypeScript/React) does not use Pydantic; it uses TypeScript types and interfaces to type the same API contracts.

Below we focus on the **nutritional label analyzer**; the same ideas (BaseModel, Field, validation, response_model) apply to the RAG and Nutri-AI backends.

### 2.1 Models in the label analyzer (`models.py`)

Both classes inherit from **BaseModel**. When in code you do `NutritionalResponse(**final_report)` or `AnalysisResult(**analysis_data)`, Pydantic validates the dictionary against that schema; if something fails (wrong type, missing field, number out of range), it raises. If all is well, you get an object with validated attributes (and you can use `.model_dump()` to get back a dict if needed).

#### NutritionalResponse

This is the **contract for the response** returned by `POST /analyze-label`.

```python
class NutritionalResponse(BaseModel):
    producto: str = Field(..., description="Name of the product identified")
    categoria_nova: int = Field(..., ge=1, le=4, description="NOVA category (1-4)")
    es_ultraprocesado: bool = Field(..., description="Whether the product is ultra-processed (NOVA 3-4)")
    analisis_critico: str = Field(..., description="Critical analysis of the product")
    alternativa_saludable: Optional[str] = Field(None, description="Healthier alternative found")
    link_alternativa: Optional[str] = Field(None, description="Link to the healthier alternative")
    score_salud: int = Field(..., ge=1, le=10, description="Health score of the product (1-10)")
    ingredientes_principales: Optional[list[str]] = Field(None, description="Main ingredients identified")
    advertencias: Optional[list[str]] = Field(None, description="Nutritional warnings")
```

- **Required fields** (`Field(...)`): producto, categoria_nova, es_ultraprocesado, analisis_critico, score_salud.
- **Optional** (`Field(None)`): alternativa_saludable, link_alternativa, ingredientes_principales, advertencias.
- **Constraints:** categoria_nova between 1 and 4, score_salud between 1 and 10.

#### AnalysisResult

This is the **contract for the JSON** that Gemini must return in the analyzer node.

```python
class AnalysisResult(BaseModel):
    producto: str
    categoria_nova: int = Field(..., ge=1, le=4)
    es_ultraprocesado: bool
    ingredientes_principales: Optional[list[str]] = None
    razonamiento: Optional[str] = None
```

- Required: producto, categoria_nova, es_ultraprocesado.
- Optional: ingredientes_principales, razonamiento.
- categoria_nova validated in range 1–4.

### 2.2 Use in the API (main.py, label analyzer)

- The endpoint declares the response with the model:
  ```python
  @app.post("/analyze-label", response_model=NutritionalResponse)
  async def analyze_label(file: UploadFile = File(...)):
  ```
  So FastAPI serializes the response according to `NutritionalResponse` and documents the schema in `/docs`.

- After running the graph, `final_report` is validated before returning:
  ```python
  response = NutritionalResponse(**final_report)
  return response
  ```
  If `final_report` has a wrong type or is missing a required field, Pydantic raises and FastAPI can return 500 with a clear message; the client never receives invalid JSON.

### 2.3 Use in the graph (nodes.py, label analyzer)

- In the **analyzer**, the text returned by Gemini is parsed to JSON and validated with `AnalysisResult`:
  ```python
  analysis_data = json.loads(response_text)
  analysis_result = AnalysisResult(**analysis_data)
  return { **state, "analysis": analysis_result.model_dump(), }
  ```
  If Gemini returns a number outside 1–4 or a required field is missing, it fails here and does not propagate bad state to the rest of the graph.

- **model_dump()** converts the validated model to a dictionary to store in `state["analysis"]`, which the searcher and finalizer then read.

### 2.4 Use in the RAG and Nutri-AI backends

- **RAG service:** Pydantic models define the body of `POST /chat` (e.g. `ChatRequest` with `message` and `chat_history`) and the response (e.g. `ChatResponse` with `response`). FastAPI validates and documents them.
- **Nutri-AI ingredient-detection backend:** Pydantic models (e.g. `DetectedIngredient`, `DetectionResponse`) define the shape of the detection API response; see [FastAPI — Python backends and the Nutri-AI API]({% post_url 2026-01-31-fastapi-python-backend-nutri-ai %}) for details.

### 2.5 Summary of use (label analyzer)

| Model | Where used | Purpose |
|-------|------------|---------|
| **NutritionalResponse** | `main.py` | Declare and validate the response of `POST /analyze-label`; FastAPI serializes to JSON according to this schema. |
| **AnalysisResult** | `nodes.py` (analyzer) | Validate the JSON returned by Gemini and get a typed dict for `state["analysis"]` via `model_dump()`. |

---

## Conclusion

- **Theory:** Pydantic is used to define schemas with types and constraints, validate data on instantiation, and serialize to dict/JSON.
- **In these projects:** Pydantic is used in all three backends—**nutrition-label-agent**, **rag-service**, and **nutri-ai-backend**—to define data models and validate API inputs and outputs. In the **nutritional label analyzer**, two models in `models.py` are central: **NutritionalResponse** for the API response and **AnalysisResult** for the analyzer output. That ensures the client always receives a known contract and that the graph state is not corrupted by a malformed Gemini response. The **frontend** (TypeScript/React) uses TypeScript types and interfaces for the same contracts; it does not use Pydantic.
