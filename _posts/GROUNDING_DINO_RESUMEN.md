# Grounding DINO: resumen del modelo y conceptos

Este documento explica de forma clara qué es Grounding DINO, de dónde viene, los conceptos que usa (transformers, visión por computadora, texto-imagen) y cómo se puso en marcha en este proyecto.

---

## 1. ¿Qué es Grounding DINO y de dónde sale?

### ¿Qué es?

**Grounding DINO** es un modelo de **detección de objetos guiada por texto**. Es decir:

- **Entrada:** una imagen + una lista de textos (por ejemplo: "rice", "tomato", "chicken").
- **Salida:** cajas (bounding boxes) en la imagen que marcan dónde está cada cosa, con una etiqueta (cuál texto coincide) y un **score** de confianza (0–1).

A diferencia de un detector clásico (que solo sabe detectar las clases con las que fue entrenado), Grounding DINO puede buscar **cualquier concepto que le pases en texto**. Por eso se llama **open-set** o **zero-shot**: no fue entrenado en “arroz” o “tomate” específicamente, pero entiende el lenguaje y la imagen lo bastante bien como para localizar esos conceptos.

### De dónde sale

- **Paper:** *"Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection"* (Liu et al., 2023).  
  Enlace: [arXiv:2303.05499](https://arxiv.org/abs/2303.05499).
- **Ideas base:** Combina **DINO** (un detector basado en transformers, tipo DETR) con **grounded pre-training**: entrenamiento con datos que relacionan regiones de imagen con frases o palabras.
- **Código y modelos:** Los autores publicaron código y checkpoints; en este proyecto se usa la versión integrada en **Hugging Face** (`transformers`), con el modelo **IDEA-Research/grounding-dino-tiny** (variante pequeña).

En resumen: el modelo “sale” del paper de 2023 y lo usamos a través de la librería Hugging Face y su Hub.

---

## 2. Cómo se llama y se usa en este proyecto

### Dónde está en el código

- **Clase que encapsula el modelo:** `GroundingDinoDetector` en `detection/grounding_dino.py`.
- **Configuración:** `detection/config.py` (ID del modelo, lista de ingredientes, umbrales).
- **Punto de uso:** `main.py` usa `get_detector()` para obtener una única instancia (singleton) y luego llama a `detector.detect(...)` en los endpoints `/detect` y `/detect/image`.

### Cómo se invoca

1. **Carga (una sola vez):** `get_detector()` crea `GroundingDinoDetector()`, y la primera vez que se llama a `detect()` se ejecuta `load_model()`: se descargan el processor y el modelo desde Hugging Face y se llevan a GPU o CPU.
2. **Cada petición:** Se llama `detector.detect(image, text_prompts=lista_de_ingredientes, box_threshold=..., text_threshold=...)`. El modelo devuelve una lista de diccionarios con `label`, `box` (coordenadas) y `score`.
3. **Post-procesado en `main.py`:** Se filtran cajas demasiado grandes, se normalizan las etiquetas a la lista de ingredientes y, opcionalmente, se filtra por categoría de comida (breakfast, lunch, snack, dinner).

El “nombre” del modelo en la API y en la documentación es “Grounding DINO (vision-language, zero-shot)”; en código es la clase `GroundingDinoDetector` y el modelo de Hugging Face `IDEA-Research/grounding-dino-tiny`.

---

## 3. ¿Qué es un Transformer?

### Idea sencilla

Un **Transformer** es una arquitectura de red neuronal basada en **atención** (attention): en lugar de procesar la secuencia o la imagen de golpe, cada “posición” (token o región) puede **atender** a otras posiciones y combinar su información. Así se capturan relaciones de largo alcance (por ejemplo, un objeto a la izquierda y otro a la derecha).

### En Grounding DINO

- **Imagen:** Se divide en regiones o parches; cada uno se convierte en un “token” (vector). Esos tokens pasan por capas de **self-attention** (se miran entre sí) y **cross-attention** (la imagen “mira” al texto y el texto “mira” a la imagen).
- **Texto:** Las palabras o frases (por ejemplo, “rice”, “tomato”) se tokenizan y se convierten en vectores; también participan en atención con los tokens de imagen.
- **Decoder:** Un conjunto de “queries” (consultas) va refinando dónde están los objetos y qué texto les corresponde, usando atención sobre características de imagen y de texto.

Todo esto es **transformers**: bloques de atención + redes feed-forward, sin convoluciones clásicas en el núcleo del detector (aunque el backbone de imagen puede usar algo tipo Swin Transformer, que tiene ventanas locales). En nuestro caso, Hugging Face encapsula esa arquitectura en `AutoModelForZeroShotObjectDetection`.

---

## 4. Visión por computadora en este contexto

### Qué hace la visión aquí

- **Entrada:** Una imagen (en nuestro caso, foto de un plato de comida).
- **Objetivo:** Encontrar **objetos** (ingredientes) y sus **posiciones** (cajas rectangulares).
- **Tarea:** Detección de objetos (object detection): para cada objeto, devolver (caja, etiqueta, confianza).

### Por qué “visión + lenguaje”

En detección clásica las clases son fijas (ej. 80 clases de COCO). En **open-set**, las “clases” son los textos que tú das. Por eso el modelo debe entender **a la vez**:

- **Visión:** qué hay en cada región de la imagen (forma, color, contexto).
- **Lenguaje:** qué significa cada palabra o frase que pasas.

Grounding DINO hace **visión por computadora** en el sentido de que analiza píxeles y devuelve cajas y etiquetas; pero esa visión está **guiada por texto**, por eso se llama “vision-language” o “grounded”.

---

## 5. Cómo se relaciona el texto con la imagen

### En alto nivel

1. **Imagen → características:** Un backbone (ej. Swin Transformer) convierte la imagen en un conjunto de vectores (uno por región o escala). Cada vector resume el contenido visual de esa zona.
2. **Texto → características:** Un encoder de texto (ej. BERT) convierte las palabras (p. ej. “rice”, “tomato”) en vectores en el **mismo espacio** (misma dimensión) que los de imagen, o en un espacio alineado.
3. **Fusión:** Varios módulos hacen que imagen y texto “se hablen”:
   - **Feature enhancer:** atención imagen↔texto (image-to-text y text-to-image) para alinear regiones con palabras.
   - **Language-guided query selection:** se eligen las regiones de imagen más “parecidas” al texto (p. ej. por similitud coseno o producto escalar) para inicializar las queries del decoder.
   - **Cross-modality decoder:** cada query atiende tanto a características de imagen como de texto y va refinando la caja y la etiqueta.

Así, “relacionar texto con imagen” significa: **representar ambos en espacios compatibles y usar atención y similitud para asociar regiones de la imagen con palabras**.

### En la API

- Tú pasas **text_prompts** = lista de ingredientes en inglés (por defecto la de `config.INGREDIENTS_LIST`, o un string separado por comas vía `ingredients_prompt`).
- El modelo busca en la imagen **esas** cosas; la salida son cajas cuya etiqueta es uno de esos textos y un score de cuánto coincide esa región con esa palabra.

---

## 6. La matemática detrás (simplificada)

No hace falta implementar nada de esto; el modelo ya lo trae. Sirve para tener una idea de “qué está pasando”.

### Atención (attention)

- Se tienen vectores **Q** (query), **K** (key), **V** (value).
- Para cada query se calcula afinidad con todas las keys: por ejemplo **scores = Q K^T / √d** (producto escalar escalado).
- Se aplica softmax a los scores → pesos que suman 1.
- La salida es una **combinación ponderada de V** con esos pesos. Así cada posición “ve” al resto y mezcla su información.

En Grounding DINO hay atención entre tokens de imagen, entre tokens de texto, y **cross-attention** entre imagen y texto (Q de un lado, K y V del otro).

### Language-guided query selection (paper)

- **X_I:** características de imagen (N_I vectores de dimensión d).
- **X_T:** características de texto (N_T vectores de dimensión d).
- Se calcula **similitud** entre cada región de imagen y cada token de texto, por ejemplo el producto escalar: **X_I X_T^T** (matriz N_I × N_T).
- Para cada región de imagen se toma el **máximo** sobre los textos (la palabra que más “pega” con esa región).
- De esas puntuaciones se eligen las **top-K** regiones (p. ej. 900) como “queries” iniciales del decoder.

En fórmula del paper: los índices de las top-Nq queries son  
**I_{Nq} = TopNq( Max_{−1}( X_I X_T^T ) )**.  
Es decir: “qué regiones de la imagen se parecen más a alguno de los textos”.

### Umbrales (box_threshold y text_threshold)

- **box_threshold:** Después del decoder, cada predicción tiene un score de “confianza de caja”. Se descartan las cajas con score &lt; box_threshold.
- **text_threshold:** Mide la alineación región–texto. Se descartan predicciones cuya alineación con el texto sea &lt; text_threshold.

En el código esto se aplica en `post_process_grounded_object_detection()` del processor de Hugging Face; nosotros solo pasamos los umbrales (por defecto 0.30 y 0.25 en `config.py`).

### Entrenamiento (solo contexto; nosotros no entrenamos)

El modelo fue entrenado con:

- **Pérdida de caja:** L1 + GIoU entre cajas predichas y cajas reales.
- **Pérdida de clasificación:** tipo contrastiva (similar a GLIP): que la región predicha sea más parecida al texto correcto que a otros textos.

Nosotros solo hacemos **inferencia**: no hay pérdida ni gradientes; solo forward y post-procesado.

---

## 7. Cómo se puso en marcha (implementación)

### Stack usado

- **Lenguaje:** Python.
- **API:** FastAPI (`main.py`).
- **ML:** PyTorch + Hugging Face `transformers` (`AutoModelForZeroShotObjectDetection`, `AutoProcessor`).
- **Imágenes:** PIL/Pillow (abrir, convertir a RGB, dibujar cajas en `/detect/image`).
- **Config:** Variables de entorno para modelo y umbrales; lista de ingredientes y categorías de comida en `config.py`.

### Flujo de una petición

1. El usuario sube una imagen a `POST /detect` (o `/detect/image`).
2. Se valida el tipo de archivo (JPEG, PNG, WebP, BMP) y se abre con PIL en RGB.
3. Se arma la lista de textos: `ingredients_prompt` (query param) o `INGREDIENTS_LIST` por defecto; si viene string, `ingredients_from_string()` lo convierte en lista.
4. `get_detector()` devuelve la instancia única de `GroundingDinoDetector`; si el modelo no estaba cargado, se llama `load_model()` (descarga desde Hugging Face y lo pone en GPU/CPU).
5. Se llama `detector.detect(image, text_prompts=..., box_threshold=..., text_threshold=...)`:
   - El processor tokeniza imagen y texto y genera los tensores.
   - Se hace el forward con `torch.no_grad()`.
   - `post_process_grounded_object_detection()` devuelve cajas, scores y etiquetas en coordenadas de la imagen.
6. En `main.py`: se filtran cajas demasiado grandes (`_is_box_too_large`), se normaliza la etiqueta con `_normalize_label` y, si se pidió, se filtra por categoría de comida.
7. Se devuelve JSON con `ingredients` (lista de `DetectedIngredient`) o, en `/detect/image`, la imagen con las cajas dibujadas en JPEG.

### Modelo concreto

- **ID:** `IDEA-Research/grounding-dino-tiny` (configurable por `GROUNDING_DINO_MODEL_ID`).
- **Variante:** “Tiny” (backbone más pequeño) para equilibrar velocidad y calidad; hay otras variantes más grandes en el ecosistema del paper (p. ej. Swin-L).

### Despliegue

- **Local:** `uvicorn main:app --reload --port 8000` (o el que se configure).
- **Docker:** El Dockerfile construye una imagen con Python, dependencias, `main.py` y `detection/`; el puerto por defecto es 7860 (p. ej. para Hugging Face Spaces).
- **Hugging Face Spaces:** Se puede desplegar como Space con SDK Docker usando ese Dockerfile; la primera petición descarga el modelo desde el Hub.

---

## 8. Resumen en una tabla

| Tema | Qué es / de dónde sale | Cómo se usa en este proyecto |
|------|------------------------|------------------------------|
| **Grounding DINO** | Modelo vision-language, zero-shot, para detección open-set (paper 2023, Hugging Face). | `GroundingDinoDetector` en `detection/grounding_dino.py`; modelo `grounding-dino-tiny`. |
| **Transformer** | Arquitectura basada en atención (self y cross) para imagen y texto. | El modelo interno es tipo DETR/DINO + fusión con texto; se usa vía `transformers`. |
| **Visión por computadora** | Analizar imagen y devolver objetos con cajas y etiquetas. | Entrada: foto de plato; salida: ingredientes con caja y score. |
| **Texto ↔ imagen** | Misma dimensión / espacio alineado + atención y similitud (ej. X_I X_T^T, query selection). | Lista de ingredientes en inglés como `text_prompts`; el modelo asocia regiones a esas palabras. |
| **Matemática** | Atención (Q,K,V), query selection (top-K por similitud), umbrales en post-proceso. | `box_threshold` y `text_threshold` en config y en API; el resto dentro del modelo y del processor. |
| **Puesta en marcha** | FastAPI + PyTorch + Hugging Face + PIL; singleton del detector; Docker/Spaces. | `get_detector()` + `detector.detect()` en `/detect` y `/detect/image`; post-procesado y filtros en `main.py`. |

---

Este documento resume el modelo Grounding DINO y todos los conceptos asociados que se usan para tenerlo en funcionamiento en este backend, de forma clara y sin entrar en detalles de implementación interna del código de Hugging Face.
