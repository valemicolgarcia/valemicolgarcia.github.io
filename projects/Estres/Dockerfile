FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

# Copiar archivos de la aplicación
COPY app_api.py .
COPY stress_model.pkl .
COPY stress_vectorizer.pkl .

# Exponer puerto
EXPOSE 7860

# Comando para ejecutar la aplicación
CMD ["python", "app_api.py"]
