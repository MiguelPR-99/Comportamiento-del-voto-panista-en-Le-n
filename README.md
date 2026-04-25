# Comportamiento del voto panista en Leon

Pieza editorial interactiva que replica el mapa "Comportamiento del voto panista en Leon" con enfoque narrativo (no dashboard): coropleta bivariante 3x3, mapa principal, inset urbano, leyenda con conteos reales, escala grafica y exportacion PNG.

Version actual: `v1.1.0`

Deploy publico: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)

## Vista v1

Export oficial validado:

![Export v1](exports/leon_pan_bivariate_desktop.png)

## Stack

- Next.js + React + TypeScript
- MapLibre GL JS
- html-to-image (UI export)
- Playwright (CLI export robusto)
- CSS editorial custom

## Fuentes de datos

- INE: cartografia seccional (geometria electoral)
- IEEG: resultados de diputaciones locales 2018 y 2021
- INEGI: referencia territorial contextual

Artefactos consumidos por frontend:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`

## Metodologia resumida

- Universo espacial final: `846` secciones de Leon.
- Clasificacion bivariante v1 cerrada (3x3 + `no_data`).
- Eje horizontal (% PAN 2021): `low <40`, `mid 40-<60`, `high >=60`.
- Eje vertical (delta vs 2018): `decline <-10`, `stable -10 a 10`, `growth >10`.
- Regla de faltantes: sin imputar ceros; cuando faltan datos clasificatorios se asigna `has_data=false` y `bivariate_class=no_data`.

## Correr localmente

```bash
npm install
npm run dev
```

App local:
- `http://127.0.0.1:3000`

Validacion de calidad:

```bash
npm run lint
npm run build
```

## Exportar PNG

Via UI:
- Boton `Exportar PNG` en la pieza.

Via CLI (recomendada para portafolio):

```bash
npm run export:png
```

Notas:
- URL default de export CLI: `http://127.0.0.1:4173`.
- Si no hay servidor en esa URL, el script inicia uno temporal.
- Para otra URL, usar `EXPORT_URL`.
- Si falta navegador de Playwright, ejecutar:

```bash
npx playwright install chromium
```

Salida:
- `exports/leon_pan_bivariate_desktop.png`

## Estructura del repo

- `app/`: rutas y layout Next.js
- `components/`: mapa principal, inset, leyenda, tooltip, shell editorial
- `lib/`: carga de spec/datos y utilidades
- `styles/`: estilo editorial
- `public/data/`: bundle geo para web
- `public/config/`: spec editorial consumido en frontend
- `data/processed/`: artefactos finales de pipeline
- `docs/`: especificaciones, cierres y caso de estudio
- `reports/`: QA de datos y frontend

## Limitaciones conocidas

- `is_in_inset` se mantiene en `false` en v1 (inset definido editorialmente).
- Escala grafica aproximada por zoom/latitud.
- Export UI puede variar segun navegador/GPU; CLI con Playwright es la via mas estable.
- No hay suite automatizada completa de regresion visual cross-browser.

## Backlog v1.2

- Formalizar geometria del inset.
- Mejorar accesibilidad avanzada.
- Agregar pruebas visuales automatizadas.
- Documentar receta de deploy en Cloudflare Pages.
- Integrar overlay contextual rojo/coral si se confirma fuente oficial.
