# Release v1.0.0 - Comportamiento del voto panista en Leon

## Metadata del release

- Version: `v1.0.0`
- Fecha de release: `2026-04-25`
- Estado: `lista para publicacion`
- URL publica: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)
- Artefacto PNG oficial: `exports/leon_pan_bivariate_desktop.png`

## Que incluye v1.0.0

- Pieza editorial interactiva (desktop-first), sin patron dashboard.
- Mapa principal de secciones con coropleta bivariante 3x3.
- Inset urbano funcional sincronizado con seccion activa.
- Tooltip, leyenda con conteos reales y escala grafica.
- Exportacion PNG por UI y por CLI (`npm run export:png`).
- Bundle web final validado:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`
- Documentacion de cierre, deploy y portafolio en `docs/` y `reports/`.

## Que queda fuera de v1.0.0

- Geometria formal de inset (`is_in_inset` sigue en `false`).
- Hardening avanzado de accesibilidad (auditoria AA completa).
- Suite automatizada completa de regresion visual cross-browser.
- Overlay contextual rojo/coral sin confirmacion de fuente oficial.

## Checklist final de publicacion

- [x] Deploy publico funcional.
- [x] URL publica verificada.
- [x] Export PNG oficial validado.
- [x] README publico actualizado con stack, fuentes, metodologia y comandos.
- [x] Cierre formal v1 documentado.
- [x] Caso de estudio de portafolio documentado.
- [x] Post base para LinkedIn documentado.
- [x] Backlog v1.1 separado de alcance v1.0.0.
- [x] Sin cambios en datos crudos/intermedios ni metodologia.

## Backlog v1.1 (no bloqueante)

- Mejorar labels de leyenda a espanol natural.
- Refinar encuadre del mapa principal.
- Quitar texto tecnico del inset.
- Formalizar geometria del inset.
- Mejorar accesibilidad avanzada.
- Agregar pruebas visuales automatizadas.
- Documentar receta de deploy en Cloudflare Pages.
- Integrar overlay contextual rojo/coral si se confirma fuente oficial.

## Veredicto final

`v1.0.0 aprobada para release publico`.
