# Export QA - Epica 4.1

## Causa probable del bug

La exportacion UI usaba captura de DOM con `html-to-image` mientras MapLibre renderiza capas en canvas WebGL. Sin `preserveDrawingBuffer`, el buffer del canvas puede no estar disponible al momento de la captura, resultando en mapas vacios (contenedores sin poligonos).

## Solucion aplicada

- Se activo `preserveDrawingBuffer: true` en:
  - mapa principal (`components/EditorialMap.tsx`)
  - inset (`components/InsetMap.tsx`)
- Se agrego estado de readiness de mapas:
  - `mainMapReady`
  - `insetMapReady`
- El boton de exportacion UI queda deshabilitado hasta que ambos mapas reportan estado listo.
- Antes de exportar UI se espera:
  - presencia de 2 canvas MapLibre visibles
  - frame extra de render + delay corto
- Se fortalecio export CLI (`scripts/export-png.mjs`) para esperar:
  - `domcontentloaded`
  - presencia de leyenda
  - presencia de 2 canvas MapLibre
  - estado de boton `Exportar PNG` (mapa principal + inset listos)
  - delay corto adicional
  - y para iniciar servidor local temporal automaticamente (URL default `http://127.0.0.1:4173`) si no hay uno activo.

## Estado de preserveDrawingBuffer

- Mapa principal: activo.
- Inset: activo.

## Estado export UI

- Implementacion corregida.
- Debe incluir mapa principal e inset cuando el navegador permite captura de WebGL con buffer preservado.
- Si falla, se muestra error con recomendacion de usar export CLI.

## Estado export CLI

- Funcional y considerado via confiable para salida final reproducible.
- Salida esperada:
  - `exports/leon_pan_bivariate_desktop.png`
- Validado en corrida real de QA con `npm run export:png`.

## Evidencia de inclusion de mapas

- Se verifico que el flujo CLI espera 2 canvas de MapLibre antes de screenshot.
- El archivo `exports/leon_pan_bivariate_desktop.png` se genera despues de la espera de mapa + leyenda.
- Revision visual del archivo exportado confirma presencia de mapa principal e inset.

## Limitaciones conocidas

- La exportacion UI puede variar segun navegador/GPU/WebGL.
- Para entregable final de portafolio se recomienda CLI con Playwright.

## Veredicto

- Estado: **aprobado para compartir export estatico**.
