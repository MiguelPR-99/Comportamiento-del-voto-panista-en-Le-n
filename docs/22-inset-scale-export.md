# Epica 3.2 - Inset real, escala y export PNG

## Alcance implementado

Esta fase agrega tres capacidades al frontend editorial sin cambiar datos ni metodologia:

- Inset urbano real con MapLibre sincronizado con la seccion activa del mapa principal.
- Escala grafica visible en kilometros sobre el mapa principal.
- Exportacion PNG de la pieza completa (layout + mapas + leyenda + fuentes).

## Definicion del inset v1

Como no existe geometria formal de inset en datos (`is_in_inset=false` en todas las secciones), el inset se definio con criterio editorial v1:

- Fuente: mismo `/data/secciones.geojson` del mapa principal.
- Coloreado: misma propiedad `color_hex`.
- Encuadre: bbox municipal de secciones, reducido al 42% alrededor del centro para enfocar la zona urbana central aproximada.
- Interaccion: scroll zoom desactivado, sin controles de navegacion, sin rotacion.
- Sincronizacion: la seccion activa se comparte entre mapa principal, inset y leyenda.

Nota:
- Esta definicion es revisable en Epica 3.3 cuando exista delimitacion formal del inset.
- No se modifican datos ni contrato para crear `is_in_inset` en esta fase.

## Escala grafica

La escala se implementa como overlay editorial (no como control BI), ubicada en el cuadrante superior derecho del mapa principal.

Regla de calculo:
- Se estima `meters_per_pixel` segun latitud central y zoom actual del mapa.
- Se selecciona un valor "amigable" de kilometros (`0.2, 0.5, 1, 2, 3, 5, 10, 15, 20, 30, 50`).
- Se ajusta el ancho de barra segun ese valor para mantener lectura estable.

## Exportacion PNG

### Opcion en UI

- Boton discreto: `Exportar PNG`.
- Captura la pieza visible completa (`data-export-root`) usando `html-to-image`.
- Nombre de descarga: `leon_pan_bivariate_desktop.png`.

### Opcion por comando

Se agrego script CLI con Playwright:

- Archivo: `scripts/export-png.mjs`
- Comando: `npm run export:png`
- Requiere la app corriendo en `http://127.0.0.1:3000`
- Puedes levantarla con `npm run dev` o `npm run start` (despues de `npm run build`).
- Salida por defecto: `exports/leon_pan_bivariate_desktop.png`
- Requisito adicional: instalar navegador de Playwright con `npx playwright install chromium`.
- El script usa `PLAYWRIGHT_BROWSERS_PATH` si existe y, en su ausencia, intenta usar `.tmp/pw-browsers` cuando esta carpeta existe.

Opcionales:
- `EXPORT_URL` para cambiar URL.
- `EXPORT_OUT` para cambiar ruta/nombre de salida.

## Limitaciones conocidas

- El inset v1 usa criterio editorial de bbox reducido y no poligono formal de zona urbana.
- La exportacion por comando depende de que la app este levantada localmente.
- Si no esta instalado el navegador de Playwright, `npm run export:png` falla con error reproducible de `browserType.launch`.
- La escala es aproximada al zoom/latitud de vista y no reemplaza un control geodesico especializado.

## Checklist visual/manual

- La app renderiza mapa principal e inset con las mismas secciones y colores.
- Hover/click mantiene tooltip y resaltado de seccion activa.
- La celda correspondiente de la leyenda se resalta con la misma clase activa.
- La escala en km se ve sobria y legible sobre el mapa principal.
- No aparecen filtros persistentes, tabs analiticos ni sidebar dashboard.
- `Exportar PNG` descarga una imagen con titulo, mapa, leyenda, inset y fuentes.

## Pendientes para Epica 3.3

- Definir geometria formal del inset y activar `is_in_inset` basado en regla cartografica.
- Mejorar tratamiento visual del hatch `no_data` directamente en el mapa (no solo en leyenda).
- Evaluar exportacion a mayor resolucion o variantes de formato para publicacion editorial.
