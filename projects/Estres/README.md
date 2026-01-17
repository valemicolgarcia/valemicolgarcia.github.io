---
title: Stress Detection NLP
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# Detector de Estrés con NLP

Aplicación de Machine Learning que utiliza procesamiento de lenguaje natural (NLP) y regresión logística para detectar si un texto indica estrés o no.

## Características

- ✅ Clasificación binaria (Estrés / No Estrés)
- ✅ Probabilidades de predicción
- ✅ Interfaz intuitiva con Gradio
- ✅ Procesamiento de texto en inglés

## Modelo

El modelo utiliza:
- **Algoritmo**: Regresión Logística
- **Vectorización**: Bag of Words (BoW) con bigramas
- **Preprocesamiento**: Tokenización, eliminación de stopwords, lematización

## Uso

1. Ingresa un texto en inglés en el cuadro de texto
2. Haz clic en "Analizar"
3. Obtén la predicción y las probabilidades

## Ejemplos

**Texto con estrés:**
- "I am really stressed and anxious about my exams"

**Texto sin estrés:**
- "I had a great day today"
