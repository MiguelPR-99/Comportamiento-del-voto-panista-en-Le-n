# Final frontend QA - Epica 3.3

## Resumen ejecutivo

La pieza editorial interactiva se encuentra en estado aprobable para deploy v1. Se completaron pulido visual desktop, responsive base, accesibilidad basica y flujo de exportacion PNG. El frontend mantiene la direccion editorial (sin dashboard) y no recalcula metricas electorales.

## Checks desktop/tablet/mobile

- Desktop:
  - Layout editorial consistente: titulo/subtitulo, mapa protagonista, leyenda, inset y fuentes.
  - Escala grafica visible en km.
  - Boton `Exportar PNG` visible y operativo.
- Tablet:
  - Stack vertical sin ocultar leyenda ni fuentes.
  - Inset visible y funcional.
- Mobile:
  - Apilado completo de bloques (titulo, subtitulo, mapa, leyenda, inset, fuentes).
  - Sin overflow horizontal por ajustes en grid/tipografia/padding.

## Checks de accesibilidad basica

- Landmarks semanticos presentes (`main`, `header`, `section`, `aside`, `footer`).
- Descripcion textual del mapa (`map-description`) para contexto no visual.
- Foco visible en boton de exportacion y controles de mapa.
- Panel persistente "Seccion activa" para no depender solo del tooltip.
- `aria-label` aplicado en mapa principal, inset y leyenda.

## Checks de exportacion PNG

- Export UI: boton integrado en la pieza (`html-to-image`).
- Export CLI: `npm run export:png` funcional.
- Archivo generado:
  - `exports/leon_pan_bivariate_desktop.png`
- Contenido esperado incluido:
  - titulo
  - mapa principal
  - leyenda
  - inset
  - fuentes/creditos

## Build y lint

- `npm run lint`: OK
- `npm run build`: OK (ejecucion validada fuera del sandbox)
- `npm run export:png`: OK (requiere app corriendo en 127.0.0.1:3000 y browser de Playwright instalado)

## Riesgos restantes

- El encuadre de inset v1 sigue editorial (bbox reducido), aun sin geometria formal.
- El hatch de `no_data` puede afinarse para mayor fidelidad cartografica.
- El flujo CLI depende de Playwright; en entornos limpios puede requerir `npx playwright install chromium`.

## Veredicto

**Aprobado para deploy v1**, con pendientes no bloqueantes para una iteracion posterior (Epica 3.4 o mantenimiento post-v1).
