# 🚀 Instrucciones para Desplegar en Hugging Face Spaces

## Paso 1: Preparar los archivos

He creado los siguientes archivos para ti:
- ✅ `app.py` - Aplicación Gradio (versión para HF Spaces)
- ✅ `requirements_hf.txt` - Dependencias optimizadas
- ✅ `README_HF.md` - Documentación del Space

**IMPORTANTE**: Necesitas tener estos archivos en tu proyecto:
- `stress_model.pkl` - Tu modelo entrenado
- `stress_vectorizer.pkl` - Tu vectorizador
- `app.py` - La aplicación Gradio
- `requirements.txt` - Las dependencias (usa `requirements_hf.txt`)

## Paso 2: Crear cuenta en Hugging Face

1. Ve a [https://huggingface.co/](https://huggingface.co/)
2. Crea una cuenta gratuita (si no tienes una)
3. Verifica tu email

## Paso 3: Crear un nuevo Space

1. Ve a [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Haz clic en **"Create new Space"** o **"New Space"**
3. Completa el formulario:
   - **Space name**: `stress-detection-nlp` (o el nombre que prefieras)
   - **SDK**: Selecciona **"Gradio"**
   - **Visibility**: Elige **"Public"** (gratis) o **"Private"** (si tienes plan)
   - Haz clic en **"Create Space"**

## Paso 4: Subir los archivos

Tienes **2 opciones**:

### Opción A: Usando la interfaz web de Hugging Face (Más fácil)

1. En tu Space recién creado, verás una interfaz de archivos
2. Haz clic en **"Add file"** → **"Upload file"**
3. Sube estos archivos **en este orden**:
   - `app.py` (el archivo Gradio que creé)
   - `requirements.txt` (copia el contenido de `requirements_hf.txt`)
   - `README.md` (copia el contenido de `README_HF.md`)
   - `stress_model.pkl`
   - `stress_vectorizer.pkl`

### Opción B: Usando Git (Recomendado para actualizaciones)

1. En tu Space, verás instrucciones de Git
2. Abre tu terminal en la carpeta del proyecto:
   ```bash
   cd projects/Estres
   ```

3. Inicializa Git (si no está inicializado):
   ```bash
   git init
   ```

4. Agrega el remote de Hugging Face (copia el comando que te da HF):
   ```bash
   git remote add origin https://huggingface.co/spaces/TU_USUARIO/TU_SPACE_NAME
   ```

5. Copia los archivos necesarios a una carpeta temporal o renombra:
   ```bash
   # En Windows PowerShell:
   Copy-Item app_gradio.py app.py
   Copy-Item requirements_hf.txt requirements.txt
   Copy-Item README_HF.md README.md
   ```

6. Agrega y haz commit:
   ```bash
   git add app.py requirements.txt README.md stress_model.pkl stress_vectorizer.pkl
   git commit -m "Initial commit: Stress detection NLP model"
   git push origin main
   ```

## Paso 5: Esperar el build

1. Hugging Face comenzará a construir tu Space automáticamente
2. Verás el progreso en la pestaña **"Logs"**
3. El proceso puede tardar 2-5 minutos
4. Cuando termine, verás **"Running"** en verde

## Paso 6: Probar tu aplicación

1. Una vez que el build termine, tu aplicación estará disponible en:
   `https://huggingface.co/spaces/TU_USUARIO/TU_SPACE_NAME`
2. Prueba con algunos ejemplos de texto
3. ¡Listo! Tu modelo está desplegado y funcionando 🎉

## ⚠️ Notas Importantes

### Tamaño de archivos
- Los archivos `.pkl` pueden ser grandes
- Hugging Face Spaces gratuito permite hasta **50GB** de espacio
- Si tus archivos son muy grandes (>1GB), considera comprimirlos o usar un modelo más pequeño

### Si hay errores en el build

1. Revisa los **Logs** en tu Space
2. Errores comunes:
   - **Falta un archivo**: Asegúrate de subir todos los `.pkl`
   - **Error de dependencias**: Verifica `requirements.txt`
   - **Error de NLTK**: El código descarga automáticamente los recursos necesarios

### Actualizar el modelo

Si quieres actualizar tu modelo:
1. Entrena y guarda nuevos archivos `.pkl`
2. Sube los nuevos archivos a tu Space (reemplazando los antiguos)
3. El Space se reconstruirá automáticamente

## 📝 Checklist Final

Antes de desplegar, verifica:
- [ ] Tienes cuenta en Hugging Face
- [ ] Tienes los archivos: `app.py`, `requirements.txt`, `README.md`
- [ ] Tienes los modelos: `stress_model.pkl`, `stress_vectorizer.pkl`
- [ ] Los archivos `.pkl` están en la misma carpeta que `app.py`
- [ ] Probaste el código localmente (opcional pero recomendado)

## 🆘 Solución de Problemas

**Error: "Modelo no disponible"**
- Verifica que los archivos `.pkl` estén en el repositorio
- Revisa que los nombres de archivo coincidan exactamente

**Error: "Module not found"**
- Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los logs para ver qué módulo falta

**El build tarda mucho**
- Es normal, especialmente la primera vez
- Puede tardar hasta 10 minutos si hay muchas dependencias

¡Buena suerte con tu despliegue! 🚀
