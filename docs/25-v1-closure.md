# Cierre v1 - Comportamiento del voto panista en Leon

## Estado final v1

- Estado: `cerrada y publicada`
- URL publica: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)
- Export oficial: `exports/leon_pan_bivariate_desktop.png`
- Veredicto operativo: `v1 lista para portafolio y difusion`

## Que incluye v1

- Pieza editorial interactiva desktop-first (no dashboard).
- Mapa principal + inset urbano con seleccion activa compartida.
- Coropleta bivariante 3x3 + categoria `no_data`.
- Tooltip por seccion con metricas electorales.
- Leyenda bivariante con conteos reales por clase.
- Escala grafica y creditos editoriales visibles.
- Exportacion PNG por UI y via CLI con Playwright.
- Bundle web final validado:
- `public/data/secciones.geojson` (846 features)
- `public/config/editorial-map-spec.json`

## Que no incluye v1

- Geometria formal de inset (`is_in_inset` sigue en `false`).
- Suite de pruebas visuales automatizadas cross-browser.
- Hardening de accesibilidad AA completo.
- Overlay contextual rojo/coral como capa confirmada oficial.

## Decisiones cerradas

- Direccion de producto: pieza editorial interactiva de replica fiel.
- Metodologia bivariante v1 congelada:
- `% PAN 2021`: `low <40`, `mid 40-<60`, `high >=60`
- `delta pp`: `decline <-10`, `stable -10 a 10`, `growth >10`
- Regla de faltantes: sin imputacion en cero, `has_data=false` + `bivariate_class=no_data`.
- Frontend no recalcula metricas ni bins.
- Deploy recomendado: Vercel con defaults de Next.js.
- Export CLI con Playwright como ruta reproducible para entregables estaticos.

## Limitaciones aceptadas

- Inset v1 definido editorialmente, no por recorte formal cartografico.
- Escala grafica aproximada segun zoom/latitud.
- Export UI depende del entorno WebGL del navegador.

## Backlog v1.1 (no bloqueante)

- Mejorar labels de leyenda a espanol natural.
- Refinar encuadre del mapa principal.
- Quitar texto tecnico del inset.
- Formalizar geometria del inset.
- Mejorar accesibilidad avanzada.
- Pruebas visuales automatizadas.
- Receta de deploy en Cloudflare Pages.
- Overlay contextual rojo/coral si se confirma fuente oficial.

## Veredicto final

`v1 aprobada y cerrada formalmente`. No se requieren mas epicas tecnicas para publicar la version actual. Los ajustes restantes pasan a backlog `v1.1`.
