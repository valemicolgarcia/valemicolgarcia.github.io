# 🔧 Configuración de Hugging Face Inference API

Este documento explica cómo configurar el modelo para usar la Hugging Face Inference API desde tu portfolio web.

## 📋 Requisitos Previos

1. **Cuenta en Hugging Face**: Si no tienes una, créala en [https://huggingface.co/](https://huggingface.co/)
2. **Modelo subido a Hugging Face**: Tu modelo debe estar disponible en Hugging Face Model Hub
3. **Token de acceso**: Necesitas un token de acceso para usar la Inference API

## 🔑 Paso 1: Obtener tu Token de Hugging Face

1. Ve a [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Haz clic en **"New token"**
3. Dale un nombre (ej: "portfolio-stress-detection")
4. Selecciona el tipo: **"Read"** (suficiente para Inference API)
5. Haz clic en **"Generate token"**
6. **Copia el token inmediatamente** (no podrás verlo de nuevo)

## 📦 Paso 2: Subir tu Modelo a Hugging Face (si no lo has hecho)

Si tu modelo ya está en Hugging Face, salta este paso.

### Opción A: Usando la interfaz web

1. Ve a [https://huggingface.co/new](https://huggingface.co/new)
2. Selecciona **"Model"**
3. Completa:
   - **Model name**: `stress-detection` (o el nombre que prefieras)
   - **Visibility**: Public o Private
4. Haz clic en **"Create model"**
5. En la página del modelo, haz clic en **"Add file"** → **"Upload file"**
6. Sube tus archivos:
   - `stress_model.pkl`
   - `stress_vectorizer.pkl`
   - Cualquier otro archivo necesario

### Opción B: Usando Git

```bash
cd projects/Estres
git init
git lfs install
git add stress_model.pkl stress_vectorizer.pkl
git commit -m "Add model files"
git remote add origin https://huggingface.co/TU_USUARIO/TU_MODELO
git push -u origin main
```

## ⚙️ Paso 3: Configurar el HTML

1. Abre `test-stress.html`
2. Busca las constantes al principio del script:
   ```javascript
   const HF_TOKEN = 'TU_HF_TOKEN_AQUI';
   const MODEL_ID = 'TU_USUARIO/TU_MODELO';
   ```
3. Reemplaza `TU_HF_TOKEN_AQUI` con tu token de Hugging Face
4. Reemplaza `TU_USUARIO/TU_MODELO` con el ID de tu modelo (ej: `valemicolgarcia/stress-detection`)

**Ejemplo:**
```javascript
const HF_TOKEN = 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
const MODEL_ID = 'valemicolgarcia/stress-detection';
```

## 🔒 Seguridad: Token en Frontend

⚠️ **IMPORTANTE**: El token estará visible en el código fuente del HTML. Esto es aceptable para tokens de tipo "Read" en modelos públicos, pero considera:

- ✅ **Seguro para**: Modelos públicos con tokens de solo lectura
- ⚠️ **No recomendado para**: Modelos privados o tokens con permisos de escritura
- 💡 **Alternativa**: Si necesitas más seguridad, considera crear un endpoint intermedio en tu servidor

## 🧪 Paso 4: Probar

### Modo Local (con Flask)

1. Asegúrate de tener `api_server.py` funcionando:
   ```bash
   cd projects/Estres
   python api_server.py
   ```
2. Abre `test-stress.html` en tu navegador (debe estar en `localhost`)
3. El sistema detectará automáticamente que estás en localhost y usará la API Flask local

### Modo Producción (con Hugging Face)

1. Sube los cambios a GitHub
2. Espera a que GitHub Pages actualice (1-5 minutos)
3. Visita: `https://valemicolgarcia.github.io/projects/Estres/test-stress.html`
4. El sistema detectará que no estás en localhost y usará la API de Hugging Face

## 🐛 Solución de Problemas

### Error: "Por favor configura HF_TOKEN y MODEL_ID"
- **Solución**: Asegúrate de haber reemplazado los placeholders en `test-stress.html`

### Error: "El modelo está cargando"
- **Causa**: El modelo en Hugging Face está en modo "sleep" (plan gratuito)
- **Solución**: Espera 10-30 segundos y vuelve a intentar. La primera petición puede tardar.

### Error: "401 Unauthorized"
- **Causa**: Token inválido o expirado
- **Solución**: Verifica que el token sea correcto y tenga permisos de lectura

### Error: "404 Not Found"
- **Causa**: El MODEL_ID no existe o es incorrecto
- **Solución**: Verifica que el modelo exista en Hugging Face y que el ID sea correcto

### El modelo no funciona localmente
- **Solución**: Asegúrate de que `api_server.py` esté corriendo en `http://localhost:5000`

## 📝 Formato de Respuesta Esperado

La API de Hugging Face debe devolver un formato compatible. El código maneja estos formatos:

1. **Array de objetos** (más común):
   ```json
   [
     {"label": "LABEL_0", "score": 0.3},
     {"label": "LABEL_1", "score": 0.7}
   ]
   ```

2. **Objeto único**:
   ```json
   {"label": "LABEL_1", "score": 0.7}
   ```

El código detecta automáticamente las etiquetas que contengan "stress", "estrés", "1", o "positive" para clasificarlas como "Estrés".

## ✅ Checklist Final

- [ ] Token de Hugging Face obtenido
- [ ] Modelo subido a Hugging Face (si aplica)
- [ ] `HF_TOKEN` configurado en `test-stress.html`
- [ ] `MODEL_ID` configurado en `test-stress.html`
- [ ] Probado localmente con Flask
- [ ] Probado en producción con Hugging Face API
- [ ] Archivos subidos a GitHub

¡Listo! Tu modelo debería funcionar tanto localmente como desde tu portfolio web. 🚀
