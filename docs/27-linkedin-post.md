# Post LinkedIn - Comportamiento del voto panista en Leon

## Version corta (ES)

Publique una pieza editorial interactiva sobre la variacion del voto PAN en Leon (2018 vs 2021) por seccion electoral.

El proyecto replica una cartografia editorial estatica y la convierte en experiencia web con:
- coropleta bivariante 3x3
- mapa principal + inset urbano
- tooltip, leyenda con conteos reales y exportacion PNG

Deploy: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)

Fue un ejercicio completo de arquitectura de datos, pipeline geoelectoral y frontend cartografico con Next.js + MapLibre.

## Version tecnica (ES)

Cierre v1 de "Comportamiento del voto panista en Leon":

- Pipeline geoelectoral con normalizacion de llaves territoriales y join por `section_id`.
- Metodologia bivariante cerrada (3x3 + `no_data`) para mantener comparabilidad editorial.
- Bundle web final validado por contrato:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`
- Frontend en Next.js + MapLibre, sin recalculo de metricas en cliente.
- Export PNG estabilizado para mapas WebGL (UI + CLI con Playwright).

Metricas finales:
- 846 secciones
- 149 `no_data`
- payload web ~2.6 MB

Deploy: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)

## Optional English version

I just shipped v1 of an editorial interactive map: "PAN voting behavior in Leon" (2018 vs 2021), at electoral section level.

Highlights:
- 3x3 bivariate choropleth
- main map + urban inset
- real class counts in legend
- robust PNG export for WebGL maps

Built with a full geo-data workflow (official sources, section-level joins, QA gates) and a Next.js + MapLibre frontend.

Live demo: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)

## CTA sugerido

Si te interesa cartografia editorial, data storytelling o geovisualizacion electoral, te invito a explorar el proyecto y compartir feedback.
