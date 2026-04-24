# Criterios de Aceptacion Verificables

## Convenciones de QA

- Referencia visual fuente de verdad: `C:\\Users\\migue\\Desktop\\Salem\\Imagen_referencia.png`.
- Resolucion de control desktop para validacion principal: `1440x900`.
- Umbral de payload geografico v1: `<= 8 MB` sumando `secciones.geojson` + `contexto.geojson` comprimidos en distribucion.
- Si el payload supera umbral, debe documentarse decision de simplificacion o escalamiento a `PMTiles` antes de cerrar Epica 1.

## Checks visuales

- [V-01] En captura desktop `1440x900`, el titulo ocupa la columna izquierda y el subtitulo aparece en el cuadrante superior derecho.
- [V-02] En captura desktop `1440x900`, la leyenda (incluyendo bloque `Sin Datos`) se ubica abajo a la izquierda y el inset abajo a la derecha.
- [V-03] En v1 no existen filtros persistentes, tabs analiticos, sidebar de metricas, selector multi-variable ni paneles tipo BI.
- [V-04] La paleta visible en mapa y leyenda usa solo clases definidas en `legend.class_color_map` y `no_data_style`.

## Checks cartograficos

- [C-01] La clasificacion produce exactamente `9` clases bivariantes + `no_data`.
- [C-02] Toda feature con `has_data=true` tiene `vote_share_bin` en `{low,mid,high}` y `delta_bin` en `{decline,stable,growth}`.
- [C-03] Toda feature con `has_data=false` tiene `vote_share_bin=delta_bin=bivariate_class=no_data`.
- [C-04] En vista inicial desktop, al menos una geometria `no_data` muestra hatch diagonal distinguible del gris de contexto y del fondo.
- [C-05] `secciones.geojson` contiene solo geometrias `Polygon` o `MultiPolygon` y se entrega en `EPSG:4326`.

## Checks funcionales

- [F-01] Hover o focus en una seccion activa tooltip con `section_id`, `pct_pan_2018`, `pct_pan_2021`, `delta_pan_pp` y `bivariate_class`.
- [F-02] Al activar una seccion, la celda correspondiente de la leyenda `3x3` queda resaltada.
- [F-03] Si la seccion pertenece a la ventana del inset, el resaltado se refleja tambien en inset.
- [F-04] `interaction_policy` en v1 mantiene `allow_filters=false`, `allow_tabs=false`, `allow_sidebar_metrics=false`.

## Checks responsive

- [R-01] Desktop (`>=1280px`) conserva disposicion editorial de referencia.
- [R-02] Tablet (`768px-1279px`) reordena bloques sin ocultar leyenda, escala ni creditos.
- [R-03] Mobile (`<=767px`) mantiene lectura secuencial: titulo/subtitulo, mapa, leyenda, inset, fuentes.

## Checks tecnicos

- [T-01] Frontend consume artefactos estaticos y no recalcula bins ni clases bivariantes.
- [T-02] Los tres artefactos (`editorial-map-spec.json`, `secciones.geojson`, `contexto.geojson`) incluyen `schema_version`.
- [T-03] `color_hex` de cada seccion coincide con `legend.class_color_map` del archivo de especificacion.
- [T-04] Sin dependencia obligatoria de basemap externo para la narrativa principal.

## Checks de accesibilidad basica

- [A-01] Elementos interactivos son navegables por teclado.
- [A-02] Existe estado visible de focus en secciones y elementos de leyenda.
- [A-03] Tooltip mantiene contraste legible sobre fondo del mapa.

## Checks de regresion visual

- [G-01] Se guardan capturas de referencia para desktop, tablet y mobile por cada release de Epica 1.
- [G-02] Cualquier cambio en layout editorial, paleta o leyenda exige comparacion contra la referencia y nota de decision.
- [G-03] Si cambia metodologia bivariante, debe existir decision documentada previa; no se permite cambio silencioso.
