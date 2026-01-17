# 🚀 Guía Completa: Deploy en Hugging Face Spaces

## ✅ Archivos Listos

Ya tienes todos los archivos necesarios preparados:
- ✅ `app.py` - Aplicación Gradio lista
- ✅ `requirements_hf_spaces.txt` - Dependencias para HF Spaces
- ✅ `README.md` - Documentación con frontmatter de HF
- ✅ `stress_model.pkl` - Modelo entrenado
- ✅ `stress_vectorizer.pkl` - Vectorizador

## 📋 Paso a Paso

### Paso 1: Crear cuenta en Hugging Face

1. Ve a [https://huggingface.co/](https://huggingface.co/)
2. Haz clic en **"Sign Up"** o **"Sign In"** si ya tienes cuenta
3. Crea tu cuenta (es gratis)
4. Verifica tu email si es necesario

### Paso 2: Crear un nuevo Space

1. Ve a [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Haz clic en el botón **"Create new Space"** (arriba a la derecha)
3. Completa el formulario:
   - **Space name**: `stress-detection-nlp` (o el nombre que prefieras, sin espacios)
   - **SDK**: Selecciona **"Gradio"** del dropdown
   - **Hardware**: Deja **"CPU basic"** (gratis)
   - **Visibility**: Selecciona **"Public"** (gratis) o **"Private"** si tienes plan
4. Haz clic en **"Create Space"**

### Paso 3: Subir los archivos

Tienes **2 opciones**:

#### Opción A: Interfaz Web (Más Fácil) ⭐ RECOMENDADO

1. En tu Space recién creado, verás una interfaz de archivos
2. Haz clic en **"Add file"** → **"Upload file"**
3. Sube estos archivos **en este orden**:

   **a) Archivos de código:**
   - `app.py` (el archivo principal con Gradio)
   - `requirements.txt` (usa el contenido de `requirements_hf_spaces.txt`)
   - `README.md` (ya tiene el frontmatter correcto)

   **b) Archivos del modelo:**
   - `stress_model.pkl`
   - `stress_vectorizer.pkl`

4. Para cada archivo:
   - Haz clic en "Add file" → "Upload file"
   - Selecciona el archivo
   - Haz clic en "Commit changes to main"

**⚠️ IMPORTANTE**: 
- Para `requirements.txt`, copia el contenido de `requirements_hf_spaces.txt` (no subas Flask)
- Los archivos `.pkl` pueden ser grandes, ten paciencia al subirlos

#### Opción B: Usando Git (Para actualizaciones futuras)

1. En tu Space, verás instrucciones de Git en la parte inferior
2. Abre PowerShell en la carpeta del proyecto:
   ```powershell
   cd c:\Users\VICTUS\Documents\valemicolgarcia_io\valemicolgarcia.github.io\projects\Estres
   ```

3. Copia el contenido de `requirements_hf_spaces.txt` a `requirements.txt`:
   ```powershell
   Copy-Item requirements_hf_spaces.txt requirements.txt -Force
   ```

4. Inicializa Git (si no está inicializado):
   ```powershell
   git init
   ```

5. Agrega el remote de Hugging Face (copia el comando que te da HF, será algo como):
   ```powershell
   git remote add origin https://huggingface.co/spaces/TU_USUARIO/stress-detection-nlp
   ```

6. Agrega los archivos necesarios:
   ```powershell
   git add app.py requirements.txt README.md stress_model.pkl stress_vectorizer.pkl
   git commit -m "Initial commit: Stress detection NLP model"
   git push origin main
   ```

### Paso 4: Esperar el Build

1. Hugging Face comenzará a construir tu Space automáticamente
2. Verás el progreso en la pestaña **"Logs"** (arriba)
3. El proceso puede tardar **2-10 minutos** dependiendo del tamaño de los archivos
4. Verás mensajes como:
   - "Building..."
   - "Installing dependencies..."
   - "Running..."
5. Cuando termine, verás **"Running"** en verde

### Paso 5: Probar tu aplicación

1. Una vez que el build termine, tu aplicación estará disponible en:
   `https://huggingface.co/spaces/TU_USUARIO/TU_SPACE_NAME`
2. Prueba con algunos ejemplos:
   - "I am really stressed and anxious"
   - "I had a great day today"
3. ¡Listo! Tu modelo está desplegado y funcionando 🎉

## 📝 Checklist Antes de Subir

Antes de hacer el deploy, verifica:

- [ ] Tienes cuenta en Hugging Face
- [ ] Tienes el archivo `app.py` (versión Gradio, sin parámetros de launch local)
- [ ] Tienes `requirements.txt` con solo las dependencias de Gradio (sin Flask)
- [ ] Tienes `README.md` con el frontmatter de HF Spaces
- [ ] Tienes `stress_model.pkl` y `stress_vectorizer.pkl`
- [ ] Los archivos `.pkl` están en la misma carpeta que `app.py`

## ⚠️ Notas Importantes

### Tamaño de archivos
- Los archivos `.pkl` pueden ser grandes (50-200MB)
- Hugging Face Spaces gratuito permite hasta **50GB** de espacio
- Si tus archivos son muy grandes (>1GB), considera comprimirlos

### Si hay errores en el build

1. Revisa la pestaña **"Logs"** en tu Space
2. Errores comunes:
   - **"Modelo no disponible"**: Verifica que los archivos `.pkl` estén subidos
   - **"Module not found"**: Verifica que `requirements.txt` tenga todas las dependencias
   - **Error de NLTK**: El código descarga automáticamente los recursos necesarios

### Actualizar el modelo

Si quieres actualizar tu modelo en el futuro:
1. Entrena y guarda nuevos archivos `.pkl`
2. Sube los nuevos archivos a tu Space (reemplazando los antiguos)
3. El Space se reconstruirá automáticamente

## 🆘 Solución de Problemas

**Error: "Modelo no disponible"**
- Verifica que los archivos `.pkl` estén en el repositorio
- Revisa que los nombres de archivo coincidan exactamente: `stress_model.pkl` y `stress_vectorizer.pkl`

**Error: "Module not found"**
- Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los logs para ver qué módulo falta

**El build tarda mucho**
- Es normal, especialmente la primera vez
- Puede tardar hasta 10-15 minutos si hay muchas dependencias o archivos grandes

**Error de CORS o conexión**
- No deberías tener este problema en HF Spaces, ya que todo corre en el mismo servidor

## 🎯 Resumen Rápido

1. **Crear Space** en Hugging Face
2. **Subir archivos**: `app.py`, `requirements.txt`, `README.md`, `stress_model.pkl`, `stress_vectorizer.pkl`
3. **Esperar build** (2-10 minutos)
4. **Probar** tu aplicación
5. **¡Listo!** 🚀

¡Buena suerte con tu despliegue!
