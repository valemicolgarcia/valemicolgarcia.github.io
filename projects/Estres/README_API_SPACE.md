---
title: Stress Detection API
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: 4.0.0
app_file: Dockerfile
pinned: false
license: mit
---

# API de Detección de Estrés

API Flask para el modelo de detección de estrés usando NLP y regresión logística.

## Archivos necesarios

- `Dockerfile` - Configuración Docker
- `app_api.py` - API Flask
- `requirements_api.txt` - Dependencias
- `stress_model.pkl` - Modelo entrenado
- `stress_vectorizer.pkl` - Vectorizador

## Endpoints

- `GET /` - Información de la API
- `POST /predict` - Predecir estrés en un texto
- `GET /health` - Estado de la API

## Uso

```bash
POST /predict
Content-Type: application/json

{
  "text": "I am really stressed and anxious"
}
```

Respuesta:
```json
{
  "text": "I am really stressed and anxious",
  "prediction": 1,
  "label": "Estrés",
  "probability": {
    "no_stress": 0.2,
    "stress": 0.8
  }
}
```
