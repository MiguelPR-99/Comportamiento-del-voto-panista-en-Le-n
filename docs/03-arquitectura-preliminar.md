# Arquitectura Preliminar

## Objetivo tecnico de Epica 0.6

Dejar la arquitectura lista para iniciar Epica 1 sin retrabajo, cerrando:

- contrato de datos operativo;
- metodologia bivariante v1 documentada;
- criterios de validacion de salida.

## Principios no negociables

- Separacion estricta entre preparacion geografica y presentacion editorial.
- El frontend no recalcula clasificaciones electorales.
- La pieza mantiene direccion editorial interactiva, `desktop-first`, replica fiel + microinteracciones.
- v1 no se convierte en dashboard.

## Stack objetivo

- Analisis y preparacion: `Python + GeoPandas`
- Aplicacion web: `Next.js`
- Render cartografico: `MapLibre`

## Capas y responsabilidades

## 1) Capa geografica (Epica 1)

- Cargar y depurar geometria de secciones electorales.
- Integrar resultados 2018 y 2021 con estrategia de join documentada.
- Calcular metricas base (`pct_pan_2018`, `pct_pan_2021`, `delta_pan_pp`).
- Aplicar clasificacion bivariante v1 y reglas `no_data`.
- Exportar artefactos web validados contra contrato de datos.

## 2) Capa de especificacion editorial

- Mantener reglas visuales, layout, leyenda, escala, fuentes y nota editorial.
- Definir politica de interaccion para evitar deriva a UI de dashboard.
- Versionar paleta y mapping clase-color en artefacto de configuracion.

## 3) Capa frontend editorial

- Componer layout final (titulo, subtitulo, mapa principal, leyenda, inset, escala, creditos).
- Ejecutar microinteracciones: hover/focus, tooltip, resaltado en leyenda, sincronizacion mapa-inset.
- Consumir artefactos estaticos sin logica analitica embebida.

## Contrato de datos y metodo bivariante

- Contrato operativo completo: [07-data-contract.md](C:\Users\migue\Desktop\Salem\docs\07-data-contract.md)
- Clasificacion bivariante v1: [08-bivariate-classification.md](C:\Users\migue\Desktop\Salem\docs\08-bivariate-classification.md)

Artefactos obligatorios:

- `editorial-map-spec.json`
- `secciones.geojson`
- `contexto.geojson`

## Estrategia de formatos y CRS

- Canonico interno de analisis: `GeoParquet`.
- Entrega web v1: `GeoJSON` optimizado.
- Escalamiento opcional: `PMTiles` si se supera umbral de payload documentado en criterios tecnicos.
- Calculo analitico permitido en CRS metrico local (default: `EPSG:32614`).
- Entrega web obligatoria en `EPSG:4326` (`WGS84`).

## Regla de desacople

- Cambios de datos no deben exigir cambios en layout editorial.
- Cambios de estilo no deben exigir recalculo de clases bivariantes.
- Cada build debe publicar version de esquema y metadatos de fuente para trazabilidad.
