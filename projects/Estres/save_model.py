"""
Script para guardar el modelo de regresión logística y el vectorizador
Ejecutar este script después de entrenar el modelo en el notebook
"""

import pandas as pd
import numpy as np
import re
import pickle
import joblib
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import nltk

# Descargar recursos de NLTK si no están disponibles
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Leer el dataset
print("Leyendo dataset...")
df = pd.read_csv('https://raw.githubusercontent.com/valemicolgarcia/Stress-Detection/main/Stress.csv')

# Preprocesamiento: convertir a minúsculas y eliminar caracteres especiales
print("Preprocesando datos...")
df['text_new'] = df['text'].str.lower()
df['text_new'] = df['text_new'].apply(lambda x: re.sub('[^A-Za-z0-9 ]+', ' ', str(x)))

# División en X e Y
X = df['text_new']
Y = df['label']

# Tokenización para análisis de frecuencia
token_lists = [word_tokenize(each) for each in df['text_new']]
tokens = [item for sublist in token_lists for item in sublist]

# Stopwords
print("Procesando stopwords...")
noise_words = []
stopwords_corpus = nltk.corpus.stopwords
eng_stop_words = stopwords_corpus.words('english')
noise_words.extend(eng_stop_words)

# Palabras de alta y baja frecuencia
one_percentile = int(len(set(tokens)) * 0.01)
top_1_percentile = Counter(tokens).most_common(one_percentile)
bottom_1_percentile = Counter(tokens).most_common()[-one_percentile:]

noise_words.extend([word for word, val in top_1_percentile])
noise_words.extend([word for word, val in bottom_1_percentile])

# Tokenizar las noise words
processed_stopwords = [word.lower() for stopword in noise_words for word in word_tokenize(stopword)]

# Crear vectorizador
print("Creando vectorizador...")
bow_counts = CountVectorizer(
    tokenizer=word_tokenize,
    stop_words=processed_stopwords,
    ngram_range=(1, 2)  # bigramas
)

# División en datos de entrenamiento y prueba
print("Dividiendo datos...")
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

# Vectorizar
print("Vectorizando datos...")
X_train_bow = bow_counts.fit_transform(X_train)
X_test_bow = bow_counts.transform(X_test)

# Entrenar modelo
print("Entrenando modelo...")
model = LogisticRegression(C=1, solver="lbfgs", max_iter=50000)
model.fit(X_train_bow, y_train)

# Guardar modelo y vectorizador
print("Guardando modelo y vectorizador...")
joblib.dump(model, 'stress_model.pkl')
joblib.dump(bow_counts, 'stress_vectorizer.pkl')
pickle.dump(processed_stopwords, open('processed_stopwords.pkl', 'wb'))

print("✅ Modelo y vectorizador guardados exitosamente!")
print("Archivos creados:")
print("  - stress_model.pkl")
print("  - stress_vectorizer.pkl")
print("  - processed_stopwords.pkl")
