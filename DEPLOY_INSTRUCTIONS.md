# Instrucciones para Deploy a GitHub Pages

## Pasos para hacer el deploy de tu sitio web

### 1. Verificar que el repositorio esté configurado correctamente

Asegúrate de que tu repositorio se llame exactamente: `valemicolgarcia.github.io`

### 2. Configurar GitHub Pages

1. Ve a tu repositorio en GitHub: `https://github.com/valemicolgarcia/valemicolgarcia.github.io`
2. Haz clic en **Settings** (Configuración)
3. En el menú lateral izquierdo, busca **Pages**
4. En **Source**, selecciona la rama `main` o `master` (la que estés usando)
5. En **Folder**, selecciona `/ (root)` o `/docs` si prefieres usar la carpeta docs
6. Haz clic en **Save**

### 3. Configurar Jekyll (si GitHub Pages no lo detecta automáticamente)

GitHub Pages debería detectar automáticamente que es un sitio Jekyll, pero si no:

1. Crea un archivo `.nojekyll` en la raíz SOLO si NO quieres usar Jekyll
2. Si quieres usar Jekyll (recomendado), NO crees el archivo `.nojekyll`

### 4. Esperar el build

- GitHub Pages tarda entre 1-10 minutos en construir y publicar tu sitio
- Puedes ver el progreso en la pestaña **Actions** de tu repositorio

### 5. Verificar que funciona

Una vez que el build esté completo, visita:
- `https://valemicolgarcia.github.io`

### 6. Configuración adicional (opcional)

Si quieres usar un dominio personalizado:

1. Agrega tu dominio en el archivo `CNAME` (ya está creado pero vacío)
2. En GitHub Settings > Pages, agrega tu dominio personalizado
3. Configura los registros DNS según las instrucciones de GitHub

## Archivos importantes para el deploy

- ✅ `_config.yml` - Configuración de Jekyll (ya configurado con URL correcta)
- ✅ `CNAME` - Para dominio personalizado (opcional)
- ✅ `Gemfile` - Dependencias de Jekyll
- ✅ Todos los archivos HTML, CSS, imágenes, etc.

## Notas importantes

1. **No commits el folder `_site`** - Este se genera automáticamente
2. **Asegúrate de que todos los archivos estén en la rama correcta** (main o master)
3. **Los cambios pueden tardar unos minutos en aparecer** después del push

## Solución de problemas

Si el sitio no aparece después de 10 minutos:

1. Verifica que el repositorio se llame exactamente `valemicolgarcia.github.io`
2. Revisa la pestaña **Actions** para ver si hay errores en el build
3. Verifica que `_config.yml` tenga la URL correcta
4. Asegúrate de que todos los archivos necesarios estén commiteados

## Comandos útiles (opcional, para desarrollo local)

Si quieres probar el sitio localmente antes de hacer push:

```bash
bundle install
bundle exec jekyll serve
```

Luego visita `http://localhost:4000` en tu navegador.

