# API de Detección de Estrés

Este proyecto incluye una API Flask para predecir estrés en textos usando un modelo de regresión logística entrenado.

## 📋 Requisitos Previos

1. Python 3.8 o superior
2. Las librerías listadas en `requirements.txt`

## 🚀 Instrucciones de Uso

### 1. Guardar el Modelo

Primero, ejecuta el script para entrenar y guardar el modelo:

```bash
cd projects/Estres
python save_model.py
```

Esto creará los archivos:
- `stress_model.pkl` - Modelo entrenado
- `stress_vectorizer.pkl` - Vectorizador entrenado
- `processed_stopwords.pkl` - Stopwords procesados

### 2. Probar Localmente

Para probar la API localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la API
python app.py
```

La API estará disponible en `http://localhost:5000`

### 3. Desplegar la API

#### Opción A: Render (Recomendado - Gratis)

1. Crea una cuenta en [Render.com](https://render.com)
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
5. Asegúrate de que los archivos `.pkl` estén en el repositorio o súbelos manualmente
6. Render te dará una URL como: `https://tu-api.onrender.com`

#### Opción B: Railway

1. Crea una cuenta en [Railway.app](https://railway.app)
2. Crea un nuevo proyecto desde GitHub
3. Railway detectará automáticamente que es una app Python
4. Asegúrate de tener los archivos `.pkl` en el repositorio
5. Railway te dará una URL automáticamente

#### Opción C: Heroku

1. Crea una cuenta en [Heroku](https://heroku.com)
2. Instala Heroku CLI
3. Crea un `Procfile` con: `web: python app.py`
4. Despliega:
```bash
heroku create tu-api-nombre
git push heroku main
```

### 4. Actualizar la URL en la Página

Una vez desplegada la API, actualiza la URL en `test-stress.html`:

```javascript
const API_URL = 'https://tu-api-url.com/predict';
```

## 📝 Endpoints

### POST `/predict`

Predice si un texto contiene estrés.

**Request:**
```json
{
  "text": "I am really stressed and anxious"
}
```

**Response:**
```json
{
  "text": "I am really stressed and anxious",
  "prediction": 1,
  "label": "Estrés",
  "probability": {
    "no_stress": 0.23,
    "stress": 0.77
  }
}
```

### GET `/health`

Verifica el estado de la API.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vectorizer_loaded": true
}
```

## ⚠️ Notas Importantes

- Los archivos `.pkl` son grandes (~50-100MB). Considera usar Git LFS o subirlos manualmente al servidor
- La API necesita tener acceso a los archivos `.pkl` en el mismo directorio que `app.py`
- Para producción, considera usar un servidor WSGI como Gunicorn:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 app:app
  ```

## 🔒 Seguridad

Para producción, considera:
- Agregar rate limiting
- Validar y sanitizar inputs
- Usar HTTPS
- Agregar autenticación si es necesario
