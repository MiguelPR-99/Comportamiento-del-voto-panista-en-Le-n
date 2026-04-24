# Epica 3.3 - Deploy readiness

## Estado general

La pieza editorial esta lista para pre-publicacion web:
- mapa principal funcional
- inset urbano funcional
- leyenda y tooltip funcionales
- escala grafica visible
- exportacion PNG por UI y CLI
- sin filtros ni componentes tipo dashboard

## Checklist pre-deploy

- `npm install` ejecutado
- `npm run lint` en verde
- `npm run build` en verde
- `npm run export:png` verificado
- `public/data/secciones.geojson` presente
- `public/config/editorial-map-spec.json` presente
- sin cambios en `data/raw` y `data/interim`
- verificacion responsive desktop/tablet/mobile
- verificacion basica de accesibilidad

## Dependencias y entorno

- Node.js 18+
- npm 9+
- Dependencias frontend en `package.json`
- Para export CLI: Playwright Chromium

Instalacion de browser para export CLI (si falta):

```bash
npx playwright install chromium
```

## Comandos operativos

```bash
npm install
npm run lint
npm run build
npm run dev
npm run export:png
```

Alternativa:

```bash
make export-png
```

## Recomendacion de deploy

- Opcion preferida: Vercel (flujo nativo para Next.js).
- Opcion valida: Cloudflare Pages (si se mantiene salida compatible con runtime elegido).

## Pendientes post-v1

- Formalizar geometria de inset y activar regla operativa de `is_in_inset`.
- Afinar tratamiento cartografico de `no_data` en mapa (hatch mas editorial).
- Agregar pruebas visuales automatizadas para regresion responsive.
- Evaluar export de mayor resolucion para presentacion impresa.
