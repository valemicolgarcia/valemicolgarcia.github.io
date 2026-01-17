"""
Aplicación Gradio para detección de estrés
Desplegada en Hugging Face Spaces
"""

import re
import joblib
import nltk
from nltk import word_tokenize
import gradio as gr

# Descargar recursos de NLTK si no están disponibles
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Cargar modelo y vectorizador
print("Cargando modelo y vectorizador...")
try:
    model = joblib.load('stress_model.pkl')
    vectorizer = joblib.load('stress_vectorizer.pkl')
    print("✅ Modelo y vectorizador cargados exitosamente")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    model = None
    vectorizer = None

def preprocess_text(text):
    """Preprocesa el texto de la misma manera que en el entrenamiento"""
    text = text.lower()  # Convertir a minúsculas
    text = re.sub('[^A-Za-z0-9 ]+', ' ', text)  # Eliminar caracteres especiales
    return text

def predict_stress(text):
    """Predice si un texto indica estrés o no"""
    if model is None or vectorizer is None:
        return {
            "error": "Modelo no disponible. Por favor, verifica que los archivos del modelo estén cargados."
        }
    
    if not text or not text.strip():
        return {
            "error": "Por favor, ingresa un texto para analizar."
        }
    
    try:
        # Preprocesar texto
        preprocessed_text = preprocess_text(text)
        
        # Vectorizar
        text_bow = vectorizer.transform([preprocessed_text])
        
        # Predecir
        prediction = model.predict(text_bow)[0]
        probability = model.predict_proba(text_bow)[0]
        
        # Determinar resultado
        label = "Estrés" if prediction == 1 else "No Estrés"
        stress_prob = float(probability[1]) * 100
        no_stress_prob = float(probability[0]) * 100
        
        # Crear resultado formateado
        result = f"""
## Resultado: **{label}**

### Probabilidades:
- **Estrés**: {stress_prob:.2f}%
- **No Estrés**: {no_stress_prob:.2f}%

### Texto analizado:
"{text}"
        """
        
        return result
    
    except Exception as e:
        return f"Error al procesar el texto: {str(e)}"

# Crear interfaz Gradio
title = "🔍 Detector de Estrés con NLP"
description = """
Esta aplicación utiliza un modelo de Machine Learning (Regresión Logística) entrenado con NLP 
para detectar si un texto indica estrés o no.

**Cómo usar:**
1. Escribe o pega un texto en inglés en el cuadro de texto
2. Haz clic en "Analizar"
3. Obtendrás la predicción y las probabilidades

**Ejemplos de texto con estrés:**
- "I am really stressed and anxious about my exams"
- "I feel overwhelmed and can't sleep"

**Ejemplos de texto sin estrés:**
- "I had a great day today"
- "Everything is going well"
"""

examples = [
    ["I am really stressed and anxious about my upcoming exams"],
    ["I feel overwhelmed and can't sleep at night"],
    ["I had a wonderful day today"],
    ["Everything is going well in my life"],
    ["I'm worried about the future and feel constant pressure"]
]

demo = gr.Interface(
    fn=predict_stress,
    inputs=gr.Textbox(
        label="Ingresa el texto a analizar",
        placeholder="Escribe aquí tu texto en inglés...",
        lines=5
    ),
    outputs=gr.Markdown(label="Resultado del análisis"),
    title=title,
    description=description,
    examples=examples,
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
