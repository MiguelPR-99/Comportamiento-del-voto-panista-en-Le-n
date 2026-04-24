# Release v1 checklist

## Meta

- Proyecto: `Comportamiento del voto panista en Leon`
- Estado: listo para release v1
- URL de produccion: `PENDIENTE`

## Commit/tag sugerido

- Commit base de release: `PENDIENTE_SHA`
- Tag sugerido: `v1.0.0`

## Pruebas minimas en produccion

- [ ] Home carga sin error.
- [ ] `public/data/secciones.geojson` responde correctamente.
- [ ] `public/config/editorial-map-spec.json` responde correctamente.
- [ ] Mapa principal renderiza con color por `color_hex`.
- [ ] Inset urbano renderiza y comparte seccion activa.
- [ ] Leyenda 3x3 visible con conteos por clase.
- [ ] Tooltip visible en hover/click.
- [ ] Escala grafica visible.
- [ ] Fuentes y creditos visibles.
- [ ] Sin apariencia dashboard (sin filtros/sidebar/tabs BI).

## Revision por dispositivo

- [ ] Desktop (>=1280px): composicion editorial correcta.
- [ ] Tablet (~768px): bloques visibles y sin truncado.
- [ ] Mobile (<=560px): sin overflow horizontal y con bloques apilados.

## Revision de exportacion PNG

- [ ] Boton UI `Exportar PNG` funcional.
- [ ] CLI `npm run export:png` funcional en entorno con Playwright.
- [ ] Archivo generado: `exports/leon_pan_bivariate_desktop.png`.
- [ ] Si falla CLI por dependencia: ejecutar `npx playwright install chromium`.

## Pendientes post-v1

- Formalizar geometria de inset (hoy v1 editorial por bbox).
- Mejorar hatch cartografico para `no_data`.
- Agregar regresion visual automatizada para responsive.
- Documentar runbook completo para Cloudflare Pages (si se elige ese destino).
