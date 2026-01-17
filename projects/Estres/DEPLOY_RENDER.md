# 🚀 Deploy de la API en Render (Para GitHub Pages)

Para que tu modelo funcione en `valemicolgarcia.github.io`, necesitas desplegar la API Flask en Render (gratis).

## 📋 Paso a Paso

### Paso 1: Crear cuenta en Render

1. Ve a [https://render.com](https://render.com)
2. Haz clic en **"Get Started for Free"**
3. Crea una cuenta (puedes usar GitHub para registrarte más rápido)
4. Verifica tu email si es necesario

### Paso 2: Conectar tu repositorio de GitHub

1. En Render, ve a **"Dashboard"**
2. Haz clic en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub:
   - Si es la primera vez, autoriza Render a acceder a tus repositorios
   - Selecciona el repositorio: `valemicolgarcia/valemicolgarcia.github.io`
   - Selecciona la rama: `main` o `master`

### Paso 3: Configurar el servicio

Completa el formulario:

- **Name**: `stress-detection-api` (o el nombre que prefieras)
- **Region**: Elige la más cercana a ti (ej: `Oregon (US West)`)
- **Branch**: `main` o `master`
- **Root Directory**: `projects/Estres` ⚠️ **IMPORTANTE**
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install --upgrade pip setuptools wheel cython numpy && pip install -r requirements_render.txt
  ```
- **Start Command**: 
  ```
  python app_render.py
  ```

### Paso 4: Configurar variables de entorno (opcional)

No necesitas variables de entorno para este proyecto, pero puedes agregar:
- `PYTHON_VERSION`: `3.11.0` (opcional)

### Paso 5: Desplegar

1. Haz clic en **"Create Web Service"**
2. Render comenzará a construir tu API
3. Verás el progreso en los logs
4. Puede tardar **5-10 minutos** la primera vez

### Paso 6: Obtener la URL

1. Una vez que el build termine, verás **"Live"** en verde
2. Tu API estará disponible en: `https://stress-detection-api.onrender.com` (o el nombre que elegiste)
3. **Copia esta URL**, la necesitarás para actualizar el HTML

### Paso 7: Actualizar el HTML

1. Abre `test-stress.html`
2. Busca la línea que dice:
   ```javascript
   : 'https://stress-detection-api.onrender.com/predict';
   ```
3. Reemplaza `stress-detection-api.onrender.com` con la URL que te dio Render
4. Debería quedar algo como:
   ```javascript
   : 'https://TU_NOMBRE.onrender.com/predict';
   ```

### Paso 8: Subir cambios a GitHub

1. Haz commit de los cambios en `test-stress.html`
2. Haz push a GitHub
3. GitHub Pages reconstruirá tu sitio automáticamente
4. Espera 1-5 minutos
5. Visita: `https://valemicolgarcia.github.io/projects/Estres/test-stress.html`
6. ¡Debería funcionar! 🎉

## ⚠️ Notas Importantes

### Archivos necesarios en GitHub

Asegúrate de que estos archivos estén en tu repositorio en la carpeta `projects/Estres/`:
- ✅ `app_render.py` - API Flask para Render
- ✅ `requirements_render.txt` - Dependencias para Render
- ✅ `stress_model.pkl` - Modelo entrenado
- ✅ `stress_vectorizer.pkl` - Vectorizador
- ✅ `render.yaml` - Configuración de Render (opcional pero recomendado)

### Tamaño de archivos

- Los archivos `.pkl` pueden ser grandes (50-200MB)
- Render permite hasta **100MB** por archivo en el plan gratuito
- Si tus archivos son muy grandes, considera usar Git LFS o comprimirlos

### Plan gratuito de Render

- ✅ **Gratis** para siempre
- ⚠️ El servicio se "duerme" después de 15 minutos de inactividad
- ⚠️ La primera petición después de dormir puede tardar 30-60 segundos (wake-up time)
- ✅ Después de despertar, funciona normalmente

### Si el servicio se duerme

Si tu API tarda mucho en responder la primera vez:
- Es normal, Render está "despertando" el servicio
- Las siguientes peticiones serán rápidas
- Si quieres evitar esto, puedes usar el plan de pago ($7/mes)

## 🆘 Solución de Problemas

**Error: "Modelo no disponible"**
- Verifica que los archivos `.pkl` estén en el repositorio
- Revisa los logs de Render para ver si hay errores al cargar el modelo

**Error: "Module not found"**
- Verifica que `requirements_render.txt` tenga todas las dependencias
- Revisa los logs de build en Render

**Error de CORS en el navegador**
- Verifica que `flask-cors` esté en `requirements_render.txt`
- Asegúrate de que `CORS(app)` esté en `app_render.py`

**El build falla**
- Revisa los logs en Render
- Verifica que el "Root Directory" esté configurado como `projects/Estres`
- Asegúrate de que todos los archivos necesarios estén en GitHub

## 📝 Checklist Final

Antes de hacer deploy, verifica:

- [ ] Tienes cuenta en Render
- [ ] Los archivos `.pkl` están en GitHub (en `projects/Estres/`)
- [ ] `app_render.py` está en GitHub
- [ ] `requirements_render.txt` está en GitHub
- [ ] `render.yaml` está configurado correctamente (opcional)
- [ ] El "Root Directory" en Render está configurado como `projects/Estres`
- [ ] Actualizaste la URL en `test-stress.html` con la URL de Render

## 🎯 Resumen Rápido

1. **Crear cuenta** en Render
2. **Conectar repositorio** de GitHub
3. **Configurar servicio** (Root Directory: `projects/Estres`)
4. **Desplegar** y esperar build
5. **Copiar URL** de Render
6. **Actualizar** `test-stress.html` con la URL
7. **Hacer commit y push** a GitHub
8. **Probar** en `valemicolgarcia.github.io`

¡Buena suerte! 🚀
