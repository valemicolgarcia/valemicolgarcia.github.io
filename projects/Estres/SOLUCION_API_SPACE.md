# 🚀 Solución: Crear API en Hugging Face Space

El error "Failed to fetch" ocurre porque la Inference API de Hugging Face **no funciona directamente con modelos scikit-learn pickle**. 

**Solución**: Crear un **Hugging Face Space** con una API Flask personalizada.

---

## 📋 Pasos Rápidos

### 1. Crear un nuevo Space en Hugging Face

1. Ve a: **https://huggingface.co/spaces**
2. Haz clic en **"Create new Space"**
3. Completa:
   - **Space name**: `stress-detection-api` (o el nombre que prefieras)
   - **SDK**: Selecciona **"Docker"** ⚠️ IMPORTANTE: No Gradio, sino Docker
   - **Visibility**: Public
4. Haz clic en **"Create Space"**

### 2. Subir los archivos

En tu Space, sube estos archivos (en este orden):

1. **`Dockerfile`** (el que acabo de crear)
2. **`requirements_api.txt`** (subirlo con este nombre, sin renombrar)
3. **`app_api.py`** (subirlo con este nombre, sin renombrar)
4. **`stress_model.pkl`**
5. **`stress_vectorizer.pkl`**

### 3. Obtener la URL de tu Space

Una vez que el Space esté desplegado, la URL será:
```
https://TU_USUARIO-TU_SPACE.hf.space
```

Ejemplo: `https://valemicolgarcia-stress-detection-api.hf.space`

### 4. Actualizar el HTML

1. Abre `test-stress.html`
2. Busca la línea con `HF_SPACE_API_URL`
3. Reemplaza con la URL de tu Space:
   ```javascript
   const HF_SPACE_API_URL = 'https://TU_USUARIO-TU_SPACE.hf.space/predict';
   ```

### 5. Subir cambios a GitHub

```bash
git add projects/Estres/test-stress.html
git commit -m "Update to use Hugging Face Space API"
git push
```

---

## ⚡ Alternativa Rápida: Usar Gradio con API

Si prefieres algo más simple, puedes usar el Space con Gradio y exponer una API:

1. Crea un Space con **SDK: Gradio**
2. Sube `app.py` (el que ya tienes con Gradio)
3. Sube `requirements_hf_spaces.txt` (como `requirements.txt`)
4. Sube los archivos `.pkl`
5. Una vez desplegado, Gradio expone automáticamente una API en:
   ```
   https://TU_USUARIO-TU_SPACE.hf.space/api/predict
   ```

Pero necesitarías adaptar el HTML para el formato de Gradio API.

---

## ✅ Checklist

- [ ] Space creado en Hugging Face (SDK: Docker)
- [ ] `Dockerfile` subido
- [ ] `requirements_api.txt` subido (con este nombre)
- [ ] `app_api.py` subido (con este nombre)
- [ ] `stress_model.pkl` subido
- [ ] `stress_vectorizer.pkl` subido
- [ ] Space desplegado y funcionando
- [ ] URL del Space obtenida
- [ ] `HF_SPACE_API_URL` actualizado en `test-stress.html`
- [ ] Cambios subidos a GitHub

---

## 🐛 Si el Space no funciona

1. Revisa los **Logs** en tu Space
2. Verifica que todos los archivos estén subidos
3. Asegúrate de que el Dockerfile esté correcto
4. Verifica que el puerto sea 7860 (puerto por defecto de HF Spaces)

---

## 📝 Nota sobre el Token

Ya **NO necesitas el token** de Hugging Face porque el Space es público y accesible directamente. El HTML actualizado ya no lo requiere.

¡Listo! Una vez que tengas el Space funcionando, actualiza la URL en el HTML y debería funcionar. 🚀
