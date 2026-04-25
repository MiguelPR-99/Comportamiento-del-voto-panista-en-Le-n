# Epica 4 - Deploy v1 publico

## Opcion recomendada

Ruta recomendada: GitHub + Vercel (integracion nativa con Next.js).

## Prerequisitos

- Repositorio en GitHub con rama principal actualizada.
- Node.js 18+ y npm 9+ en entorno local.
- Build local validado antes de desplegar.
- Artefactos estaticos presentes:
  - `public/data/secciones.geojson`
  - `public/config/editorial-map-spec.json`

## Validacion local previa

Ejecutar en este orden:

```bash
npm install
npm run lint
npm run build
```

Notas:
- En entornos restringidos puede aparecer `spawn EPERM`; validar build en entorno sin esa restriccion.
- Para export PNG por CLI (opcional en pre-release):

```bash
npx playwright install chromium
npm run export:png
```

Comportamiento del script CLI:
- URL por defecto: `http://127.0.0.1:4173`.
- Si no hay servidor activo en esa URL, inicia uno temporal automaticamente para exportar.
- Tambien se puede exportar desde otra URL configurando `EXPORT_URL`.

Recomendacion:
- Para entregables estaticos de portafolio, usar `npm run export:png` como via principal.
- La exportacion UI puede depender del comportamiento del navegador al capturar canvas WebGL.

## Deploy con GitHub + Vercel (recomendado)

1. Subir cambios a GitHub (`main` o rama de release).
2. Entrar a [vercel.com](https://vercel.com/) y crear proyecto nuevo.
3. Seleccionar repositorio `leon-pan-editorial-map`.
4. Framework detectado: Next.js (dejar default).
5. Build command: `npm run build` (default).
6. Output: default de Next.js (sin override).
7. Ejecutar deploy.
8. Validar URL de produccion y registrar en checklist de release.

## Deploy con Vercel CLI (alternativa)

```bash
npm i -g vercel
vercel --prod
```

Usar esta ruta cuando se necesite publicar rapido sin pasar por UI de Vercel.

## Nota sobre datos estaticos

- La app consume datos desde `public/`.
- No requiere backend para servir `secciones.geojson` y `editorial-map-spec.json`.
- No modificar `data/raw` ni `data/interim` durante deploy.

## Checklist post-deploy

- Carga inicial sin error en la URL publica.
- Mapa principal visible con secciones coloreadas.
- Inset visible y sincronizado con seccion activa.
- Leyenda con conteos reales visible.
- Tooltip y seleccion activa funcionando.
- Escala grafica visible.
- Fuentes y creditos visibles.
- Responsive validado en desktop/tablet/mobile.
- Export PNG en UI funcional.
- Export PNG CLI validado como respaldo reproducible.

## Sobre vercel.json

Para esta v1 no hace falta `vercel.json`: Next.js funciona correctamente con configuracion por defecto de Vercel.
