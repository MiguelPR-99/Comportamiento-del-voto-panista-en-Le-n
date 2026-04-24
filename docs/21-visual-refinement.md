# Épica 3.1 - Refinamiento visual editorial

## Decisiones visuales aplicadas

- Se reforzó el layout desktop-first para priorizar el mapa como bloque protagonista.
- Se consolidó jerarquía editorial:
- título grande serif en columna izquierda
- subtítulo serif arriba a la derecha
- leyenda abajo a la izquierda
- inset provisional abajo a la derecha
- fuentes y nota discretas en la parte inferior
- Se ajustó estética de papel cálido con textura sutil por gradientes.
- Se mantuvo el mapa sin basemap genérico visible.
- Se refinó la leyenda para evitar apariencia dashboard y mantener lectura cartográfica.

## Microinteracciones implementadas

- Hover y click sobre sección con cursor contextual.
- Tooltip estable con métricas básicas y estado `has_data`.
- Mensaje `Sin datos suficientes` cuando `has_data=false`.
- Resaltado visual de sección activa con contorno dedicado.
- Resaltado de celda correspondiente en leyenda según `bivariate_class`.
- Transiciones suaves mínimas en tooltip y celdas activas.

## Diferencias conocidas contra el mapa original

- El inset sigue como placeholder visual; no hay geometría operacional de inset.
- La fidelidad tipográfica y de espaciados aún no es pixel-perfect.
- El hatch de `no_data` está representado en leyenda; su tratamiento cartográfico fino en mapa queda para siguiente iteración visual.

## Checklist manual de revisión en navegador

- Carga inicial sin error visible.
- Se muestran título y subtítulo editoriales en posiciones esperadas.
- El mapa se centra en León y mantiene scroll zoom desactivado por defecto.
- El hover/click muestra tooltip con `section_id`, sección, `% PAN 2018`, `% PAN 2021`, `delta_pan_pp`, clase y `has_data`.
- En secciones `has_data=false` aparece `Sin datos suficientes`.
- La leyenda 3x3 muestra conteos por clase y bloque separado de `Sin datos`.
- La celda de leyenda se resalta al activar una sección del mapa.
- No existen filtros persistentes, tabs analíticos ni sidebar de métricas.
- El inset se muestra explícitamente como pendiente/provisional.

## Pendientes para Épica 3.2

- Definir y cablear geometría formal de inset con regla `is_in_inset`.
- Afinar borde municipal de forma más explícita respecto a bordes internos.
- Mejorar accesibilidad por teclado para foco de entidades y lectura de tooltip.
- Ajustar detalles tipográficos y proporciones para acercamiento final a referencia editorial.

Documento revisado y normalizado a UTF-8.
