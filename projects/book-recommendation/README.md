# Book Recommendation System

Sistema de recomendación de libros implementado utilizando el algoritmo K-Nearest Neighbors (KNN) y técnicas de filtrado colaborativo. El sistema analiza las calificaciones de usuarios y encuentra libros similares basándose en las preferencias de usuarios con gustos similares.

## Problema a Resolver

El objetivo de este proyecto es desarrollar un sistema de recomendación que, dado un libro específico, pueda sugerir 5 libros similares basándose en los patrones de calificación de los usuarios. El sistema utiliza el dataset Book-Crossings que contiene más de 1.1 millones de calificaciones (escala 1-10) de 270,000 libros por 90,000 usuarios.

## Solución Implementada

Se implementó un sistema de recomendación utilizando el algoritmo **NearestNeighbors** de scikit-learn, que mide la distancia para determinar la "cercanía" entre instancias. El sistema funciona mediante filtrado colaborativo, analizando cómo los usuarios han calificado diferentes libros para encontrar patrones de similitud.

## Proceso de Implementación

### 1. Importación y Unión de Datasets

Se importaron dos datasets CSV:
- **BX-Books.csv**: Contiene información sobre libros (ISBN, título, autor)
- **BX-Book-Ratings.csv**: Contiene las calificaciones de usuarios (usuario, ISBN, calificación)

Ambos datasets se unieron para tener una visión completa de los libros y sus calificaciones.

### 2. Tratamiento de Valores Nulos

Se identificaron y eliminaron valores nulos en el dataset de libros para asegurar la calidad de los datos.

### 3. Filtrado de Datos

Para mejorar la calidad de las recomendaciones y reducir el ruido en los datos, se aplicaron dos filtros:

- **Filtro de usuarios**: Se mantuvieron solo los usuarios que tienen 200 o más calificaciones. Esto asegura que las recomendaciones se basen en usuarios con suficiente historial de calificaciones.
- **Filtro de libros**: Se mantuvieron solo los libros que tienen 100 o más calificaciones. Esto garantiza que los libros recomendados tengan suficiente información para calcular similitudes confiables.

### 4. Preparación de Variables

Se creó una matriz de pivot donde:
- Las **filas** representan los libros (indexados por ISBN)
- Las **columnas** representan los usuarios
- Los **valores** son las calificaciones (0 si el usuario no calificó el libro)

Esta matriz permite calcular similitudes entre libros basándose en cómo los usuarios los han calificado.

Posteriormente, se reemplazaron los índices ISBN por los títulos de los libros para facilitar la interpretación de los resultados.

### 5. Entrenamiento del Modelo NearestNeighbors

Se entrenó un modelo **NearestNeighbors** utilizando la métrica de distancia **coseno**, que es ideal para datos de alta dimensionalidad y datos dispersos como las matrices de calificaciones.

**¿Cómo funciona NearestNeighbors?**

El algoritmo NearestNeighbors encuentra los K libros más cercanos a un libro dado basándose en la similitud de sus vectores de calificaciones. La distancia coseno mide el ángulo entre dos vectores, siendo más útil que la distancia euclidiana para datos de calificaciones porque:
- No depende de la magnitud absoluta de las calificaciones
- Se enfoca en los patrones de calificación (qué usuarios calificaron qué libros)
- Es más robusta ante diferencias en escalas de calificación entre usuarios

### 6. Función de Recomendación

Se implementó la función `get_recommends` que:

1. **Recibe** el título de un libro como argumento
2. **Obtiene** el vector de calificaciones del libro desde la matriz
3. **Busca** los 6 libros más cercanos (incluyendo el libro mismo)
4. **Ordena** los resultados por distancia (de mayor a menor)
5. **Selecciona** los 5 libros más similares (excluyendo el libro original)
6. **Retorna** una lista con el título del libro consultado y un array con los 5 libros recomendados junto con sus distancias

```python
def get_recommends(book_title = ""):
    book = df.loc[book_title]
    distances, indices = model.kneighbors([book.values], n_neighbors=6)
    
    recommended_books = pd.DataFrame({
      'title'   : df.iloc[indices[0]].index.values,
      'distance': distances[0]
    }) \
    .sort_values(by='distance', ascending=False) \
    .head(5).values
    
    lista = [book_title, recommended_books]
    return lista
```

## Resultados

El sistema fue probado exitosamente con diferentes libros. Por ejemplo, para el libro **"Where the Heart Is (Oprah's Book Club (Paperback))"**, el sistema recomendó:

1. "I'll Be Seeing You" (distancia: 0.80)
2. "The Weight of Water" (distancia: 0.77)
3. "The Surgeon" (distancia: 0.77)
4. "I Know This Much Is True" (distancia: 0.77)
5. "The Lovely Bones: A Novel" (distancia: 0.72)

Las distancias más altas indican mayor similitud (la distancia coseno se interpreta como similitud cuando es cercana a 1).

## Tecnologías Utilizadas

- **Python**
- **Pandas**: Para manipulación de datos
- **NumPy**: Para operaciones numéricas
- **scikit-learn**: Para el algoritmo NearestNeighbors
- **Jupyter Notebook**: Para el desarrollo y análisis

## Archivos del Proyecto

- `KNNNUEVOOOO.ipynb`: Notebook principal con toda la implementación del sistema de recomendación

## Cómo Probar el Proyecto Localmente

### Requisitos Previos

- Python 3.7 o superior
- Jupyter Notebook o JupyterLab instalado
- Conexión a internet (para descargar los datasets)

### Paso 1: Instalar las Dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install numpy pandas scikit-learn scipy matplotlib jupyter
```

O si prefieres usar un archivo `requirements.txt`, crea uno con este contenido:

```
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
scipy>=1.7.0
matplotlib>=3.4.0
jupyter>=1.0.0
```

Luego instala con:

```bash
pip install -r requirements.txt
```

### Paso 2: Iniciar Jupyter Notebook

En la terminal, navega a la carpeta del proyecto:

```bash
cd projects/book-recommendation
```

Inicia Jupyter Notebook:

```bash
jupyter notebook
```

Esto abrirá tu navegador con la interfaz de Jupyter. Si no se abre automáticamente, copia la URL que aparece en la terminal (generalmente `http://localhost:8888`).

### Paso 3: Abrir y Ejecutar el Notebook

1. En la interfaz de Jupyter, haz clic en `KNNNUEVOOOO.ipynb` para abrirlo
2. Ejecuta todas las celdas en orden:
   - Puedes ejecutar celda por celda con `Shift + Enter`
   - O ejecutar todas las celdas desde el menú: `Cell > Run All`

**Nota importante:** El proceso completo puede tardar varios minutos porque:
- Descarga los datasets desde GitHub (más de 1 millón de registros)
- Procesa y filtra los datos
- Construye la matriz de calificaciones
- Entrena el modelo NearestNeighbors

### Paso 4: Probar la Función de Recomendación

Una vez que todas las celdas se hayan ejecutado correctamente, puedes probar la función `get_recommends` con diferentes libros:

```python
# Ejemplo 1
books = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
print(books)

# Ejemplo 2
books = get_recommends("The Queen of the Damned (Vampire Chronicles (Paperback))")
print(books)

# Ejemplo 3 - Prueba con tu propio libro
# Primero verifica que el libro esté en el dataset:
if "Tu Título de Libro" in df.index:
    books = get_recommends("Tu Título de Libro")
    print(books)
else:
    print("El libro no está en el dataset")
```

### Paso 5: Ver Libros Disponibles

Para ver qué libros están disponibles en el dataset después del filtrado, puedes ejecutar:

```python
# Ver algunos títulos disponibles
print(f"Total de libros disponibles: {len(df)}")
print("\nAlgunos ejemplos de libros:")
print(df.index[:20].tolist())
```

### Solución de Problemas

**Error: "Book title not found"**
- Asegúrate de que el título del libro coincida exactamente con el que está en el dataset
- Los títulos son sensibles a mayúsculas y minúsculas
- Usa `df.index` para ver los títulos disponibles

**Error de memoria**
- El dataset es grande. Si tienes problemas de memoria, considera usar una máquina con más RAM o reducir los filtros (menos de 200 calificaciones por usuario, menos de 100 por libro)

**El notebook tarda mucho en ejecutarse**
- Esto es normal. El procesamiento de más de 1 millón de registros puede tardar varios minutos
- La construcción de la matriz pivot es la operación más costosa

**Error al descargar los datasets**
- Verifica tu conexión a internet
- Los archivos se descargan desde GitHub, asegúrate de que la URL sea accesible

### Ejecutar desde la Terminal (Alternativa)

Si prefieres ejecutar el notebook desde la terminal sin abrir el navegador:

```bash
jupyter nbconvert --to notebook --execute KNNNUEVOOOO.ipynb --inplace
```

O convertir el notebook a un script Python y ejecutarlo:

```bash
jupyter nbconvert --to python KNNNUEVOOOO.ipynb
python KNNNUEVOOOO.py
```
