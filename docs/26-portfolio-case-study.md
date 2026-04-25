# Caso de estudio - Comportamiento del voto panista en Leon

## Problema

El insumo original era un mapa estatico editorial sobre variacion del voto PAN en Leon. El reto consistia en convertirlo en una pieza web interactiva fiel a la composicion original, sin degradarlo a dashboard ni romper la lectura narrativa.

## Objetivo

Construir una experiencia cartografica interactiva, desktop-first, con alto estandar visual, basada en una coropleta bivariante 3x3 y soporte de exportacion para presentacion en portafolio.

## Datos usados

- INE: cartografia seccional (geometria de secciones).
- IEEG: resultados de diputaciones locales 2018 y 2021.
- INEGI: referencia territorial contextual.
- Artefactos finales consumidos por frontend:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`

## Metodologia

- Join por `section_id` normalizado.
- Calculo de metricas por seccion:
- `% PAN 2018`
- `% PAN 2021`
- `delta_pan_pp`
- Clasificacion bivariante v1 cerrada:
- Horizontal: `% PAN 2021` (`low`, `mid`, `high`)
- Vertical: `delta_pan_pp` (`decline`, `stable`, `growth`)
- Categoria adicional: `no_data`.
- Politica de faltantes: no imputar ceros.

## Proceso tecnico

1. Fase documental de producto/cartografia: contrato de datos, metodologia y criterios verificables.
2. Curaduria de fuentes oficiales y estrategia de join 2018-2021.
3. QA de crudos y staging intermedio.
4. Join electoral + metricas finales + validaciones.
5. Bundle web final para frontend (`secciones.geojson` + `editorial-map-spec.json`).
6. Frontend Next.js + MapLibre con layout editorial, leyenda, tooltip, inset y escala.
7. Exportacion PNG estabilizada (UI + CLI Playwright).

## Decisiones UX/UI

- Mantener estructura editorial: titulo, subtitulo, mapa protagonista, leyenda, inset, fuentes.
- Evitar patron dashboard: sin filtros persistentes, sin sidebar BI, sin tabs analiticos.
- Resaltar coherencia entre mapa, leyenda e inset con seccion activa compartida.
- Preservar paleta violeta/azul/rosa y lectura bivariante del original.

## Resultado final

- Deploy publico: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)
- Export oficial validado: `exports/leon_pan_bivariate_desktop.png`
- Universo final: `846` secciones.
- `no_data`: `149`.
- Payload web aproximado: `2.603 MB`.

## Aprendizajes

- La fidelidad editorial requiere cerrar metodologia y contrato de datos antes del frontend.
- La calidad de llaves territoriales (join) define la confiabilidad de toda la narrativa visual.
- La exportacion de mapas WebGL requiere estrategia especifica (readiness + Playwright robusto).

## Posibles mejoras (v1.1)

- Formalizar geometria del inset y limpiar texto tecnico residual.
- Mejorar etiquetas de leyenda en espanol natural.
- Subir nivel de accesibilidad y pruebas visuales automatizadas.
- Evaluar overlay rojo/coral solo con fuente oficial confirmada.
