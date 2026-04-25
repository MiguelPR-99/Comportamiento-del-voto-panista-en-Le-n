# Release v1.1.0 - Comportamiento del voto panista en Leon

## Metadata de release

- Version: `v1.1.0`
- Fecha de release: `2026-04-25`
- Estado: `lista para publicar`
- URL publica: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)
- PNG oficial: `exports/leon_pan_bivariate_desktop.png`

## Cambios incluidos en v1.1.0

- Leyenda con etiquetas legibles en espanol natural (sin cambiar clases internas).
- Inset sin copy tecnico visible.
- Mejor encuadre visual del mapa principal (menos aire).
- Pulido de copy visible en frontend.
- Limpieza ligera de presentacion en frontend (`labels` y formateadores extraidos a helper).

## Que no cambio

- No se modifico `data/raw`.
- No se modifico `data/interim`.
- No se modifico `public/data/secciones.geojson`.
- No se cambiaron metricas, bins, clasificacion ni metodologia.
- No se agregaron features nuevas.

## QA ejecutado

- `npm run lint`: OK
- `npm run build`: OK fuera del sandbox (en sandbox puede aparecer `spawn EPERM`)
- `npm run export:png`: OK
- Revision visual: mapa principal, inset, leyenda y export PNG activos.

## Limitaciones restantes

- `is_in_inset` sigue en `false` (geometria formal pendiente).
- La escala grafica es aproximada por zoom/latitud.
- Export UI puede variar segun navegador/GPU; CLI con Playwright sigue siendo la via mas estable.
- Aun no hay suite completa de regresion visual automatizada.

## Veredicto final

`v1.1.0 aprobada para release publico`.
