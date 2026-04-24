# Comportamiento del voto panista en Leon

Pieza editorial interactiva que replica el mapa "Comportamiento del voto panista en Leon", con coropleta bivariante 3x3, mapa principal, inset urbano, leyenda editorial, escala grafica y exportacion PNG.

## Stack

- Next.js + React + TypeScript
- MapLibre GL JS
- CSS editorial custom
- Bundle de datos estatico en `public/data` y `public/config`

## Instalacion

```bash
npm install
```

## Desarrollo local

```bash
npm run dev
```

Abre `http://127.0.0.1:3000`.

## Build de produccion

```bash
npm run lint
npm run build
```

## Exportacion PNG

En UI:
- Boton `Exportar PNG` dentro de la pieza.

Por CLI:

```bash
npm run export:png
```

Requisitos:
- La app debe estar corriendo en `http://127.0.0.1:3000`.
- Si no esta instalado Chromium de Playwright, ejecutar:

```bash
npx playwright install chromium
```

Archivo de salida:
- `exports/leon_pan_bivariate_desktop.png`

## Estructura principal

- `app/`: rutas y layout Next.js
- `components/`: mapa principal, inset, leyenda, tooltip, shell editorial
- `lib/`: carga de spec/datos y utilidades de features
- `styles/`: estilo editorial global
- `public/data/secciones.geojson`: geojson final para frontend
- `public/config/editorial-map-spec.json`: especificacion editorial y leyenda
- `docs/`: especificacion y cierre de epicas
- `reports/frontend_qa/`: reportes de QA frontend

## Datos usados

- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`

El frontend no recalcula metricas electorales ni bins; solo representa artefactos ya procesados.

## Fuentes

- INE: cartografia seccional
- IEEG: resultados de diputaciones locales 2018 y 2021
- INEGI: referencia territorial contextual

## Limitaciones conocidas

- El inset urbano v1 usa encuadre editorial derivado de bbox y es revisable.
- `is_in_inset` se mantiene en `false` en esta version.
- La escala grafica es una aproximacion visual por zoom/latitud.
- El script CLI de PNG depende de Playwright y de tener servidor local activo.
