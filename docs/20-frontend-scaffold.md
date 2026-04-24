# Épica 3.0 - Frontend Scaffold (Next.js + MapLibre)

## Objetivo

Se implementó la primera versión funcional del frontend editorial interactivo para:
`Comportamiento del voto panista en León`.

## Cómo correr la app

1. `npm install`
2. `npm run dev`
3. Abrir `http://localhost:3000`

Scripts disponibles en `package.json`:

- `npm run dev`
- `npm run build`
- `npm run lint`

## Datos que consume

El frontend solo consume artefactos públicos estáticos:

- `/data/secciones.geojson`
- `/config/editorial-map-spec.json`

No consume `data/processed` directamente y no recalcula datos.

## Implementado en Épica 3.0

- Scaffold base Next.js + React + TypeScript.
- Integración de MapLibre GL JS.
- Layout editorial desktop-first:
- título a la izquierda
- subtítulo arriba a la derecha
- mapa principal al centro
- leyenda bivariante abajo a la izquierda
- bloque de fuentes y nota abajo
- placeholder de inset abajo a la derecha
- Tooltip por hover/click de sección con:
- `section_id`
- `seccion`
- `pct_pan_2018`
- `pct_pan_2021`
- `delta_pan_pp`
- `bivariate_class`
- `has_data`
- mensaje `Sin datos suficientes` cuando `has_data=false`
- Leyenda 3x3 construida desde `editorial-map-spec.json` con conteos reales por clase y bloque `no_data`.
- Validaciones de carga y consistencia visual:
- error visible si falla la carga de `secciones.geojson`
- error visible si falla la carga de `editorial-map-spec.json`
- fallback a color neutral si falta `color_hex` + warning en consola
- warning en consola si `bivariate_class` no existe en `class_color_map`

## Limitaciones conocidas

- `is_in_inset` sigue provisional en `false`.
- La fidelidad visual no es final/pixel-perfect.
- El inset urbano aún es placeholder editorial.

## Pendientes para Épica 3.1

- Definir composición final del inset urbano y su comportamiento en responsive.
- Refinar tipografía, espaciado y microinteracciones para mayor fidelidad visual.
- Incorporar ajustes de accesibilidad de navegación por teclado sobre entidades del mapa.
- Agregar pruebas de regresión visual para layout y leyenda.

Documento revisado y normalizado a UTF-8.
