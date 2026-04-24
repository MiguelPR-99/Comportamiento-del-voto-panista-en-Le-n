# Cierre v1 - pieza editorial publica

## Que incluye v1

- Pieza editorial interactiva desktop-first con:
  - mapa principal de secciones
  - leyenda bivariante 3x3
  - inset urbano funcional
  - tooltip y seleccion activa
  - escala grafica en kilometros
  - fuentes y creditos editoriales
- Exportacion PNG:
  - boton UI
  - comando CLI (`npm run export:png`)
- Documentacion de QA y deploy:
  - `README.md`
  - `docs/23-deploy-readiness.md`
  - `docs/24-deploy-v1.md`
  - `reports/frontend_qa/final_frontend_qa.md`
  - `reports/frontend_qa/release_v1_checklist.md`

## Que no incluye v1

- Geometria formal de inset por regla cartografica (`is_in_inset` sigue en `false`).
- Hardening avanzado de accesibilidad (auditoria AA completa).
- Suite automatizada de regresion visual cross-device.
- Pipeline adicional o recalculo de datos en frontend.

## Decisiones cerradas

- Publicacion como pieza editorial (no dashboard).
- Datos estaticos servidos desde `public/data` y `public/config`.
- Metodo bivariante y cortes metodologicos congelados en v1.
- Ruta recomendada de deploy: GitHub + Vercel.
- `vercel.json` no requerido para v1 (defaults de Next.js suficientes).

## Limitaciones conocidas

- Inset v1 basado en bbox editorial, revisable.
- Escala grafica aproximada por zoom/latitud.
- Export CLI depende de Playwright Chromium en entorno local.

## Backlog sugerido para v1.1 / Epica 3.4 opcional

- Definir inset formal y activar `is_in_inset` real.
- Pulir tratamiento visual de `no_data` en mapa.
- Automatizar pruebas visuales y de accesibilidad.
- Cerrar guia operativa para deploy en Cloudflare Pages.

## Veredicto de cierre

v1 queda lista para publicacion publica en Vercel, con pendientes no bloqueantes para una iteracion de hardening posterior.
