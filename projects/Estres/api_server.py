"""
API Flask para el modelo de detección de estrés
Servidor para conectar con test-stress.html
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import joblib
import nltk
from nltk import word_tokenize
import os

app = Flask(__name__)
CORS(app)  # Permitir requests desde cualquier origen

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
    # Asegurarse de que estamos en el directorio correcto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    model = joblib.load('stress_model.pkl')
    vectorizer = joblib.load('stress_vectorizer.pkl')
    print("Modelo y vectorizador cargados exitosamente")
except Exception as e:
    print(f"Error cargando modelo: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    model = None
    vectorizer = None

def preprocess_text(text):
    """Preprocesa el texto de la misma manera que en el entrenamiento"""
    text = text.lower()  # Convertir a minúsculas
    text = re.sub('[^A-Za-z0-9 ]+', ' ', text)  # Eliminar caracteres especiales
    return text

@app.route('/')
def home():
    return jsonify({
        "message": "API de Detección de Estrés",
        "endpoint": "/predict",
        "method": "POST",
        "example": {
            "text": "I am really stressed and anxious"
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para predecir estrés en un texto"""
    if model is None or vectorizer is None:
        return jsonify({
            "error": "Modelo no disponible"
        }), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                "error": "El texto no puede estar vacío"
            }), 400
        
        # Preprocesar texto
        preprocessed_text = preprocess_text(text)
        
        # Vectorizar
        text_bow = vectorizer.transform([preprocessed_text])
        
        # Predecir
        prediction = model.predict(text_bow)[0]
        probability = model.predict_proba(text_bow)[0]
        
        result = {
            "text": text,
            "prediction": int(prediction),
            "label": "Estrés" if prediction == 1 else "No Estrés",
            "probability": {
                "no_stress": float(probability[0]),
                "stress": float(probability[1])
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que la API está funcionando"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Servidor Flask iniciado")
    print("API disponible en: http://localhost:5000")
    print("Endpoint de predicción: http://localhost:5000/predict")
    print("="*50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
