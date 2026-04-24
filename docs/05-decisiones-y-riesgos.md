# Decisiones y Riesgos

## Decisiones cerradas

- Producto: pieza editorial interactiva, no dashboard.
- Estrategia visual: replica fiel del original con microinteracciones.
- Prioridad de experiencia: `desktop-first`.
- Referencia visual aprobada: `Imagen_referencia.png`.
- Stack preliminar: `Python + GeoPandas + Next.js + MapLibre`.
- Separacion de responsabilidades: pipeline clasifica, frontend representa.
- Sin descarga de datos ni implementacion de pipeline en Fase 0.

## Decisiones abiertas

- Confirmar significado y fuente de la capa lineal roja/coral observada.
- Definir metodo final de cortes para la matriz bivariante `3x3`.
- Confirmar nivel de simplificacion geometrica para inset versus mapa principal.
- Cerrar tipografia final segun licencia y similitud editorial.
- Definir comportamiento exacto de inset en mobile (activo vs secundario).

## Riesgos principales

- Inconsistencia de claves entre resultados 2018 y 2021 por seccion.
- Diferencias entre geometria oficial y geometria usada en la referencia editorial.
- Poca legibilidad de `Sin Datos` en escalas pequenas.
- Deriva de producto hacia interfaz tipo dashboard.
- Peso excesivo de artefactos geograficos para navegacion fluida.

## Mitigaciones propuestas

- Contrato de datos temprano y versionado.
- Validaciones de calidad geometrica e integridad de joins en Epica 1.
- Pruebas de contraste y textura para `Sin Datos` desde prototipos.
- Guardrails de UX: limitar controles y preservar jerarquia editorial.
- Evaluacion temprana de optimizacion (simplificacion/tiling si hace falta).

