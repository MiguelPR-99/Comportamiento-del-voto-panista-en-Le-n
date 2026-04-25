# Public Repo Cleanup - v1.1.0

## Objetivo

Limpiar la estructura publica del repositorio para presentacion de portafolio sin cambiar funcionalidad, metodologia, clasificacion ni datos finales de producto.

## Que se limpio

- Se creo `public/images/` para alojar screenshots versionados.
- Se copio el PNG oficial desde `exports/leon_pan_bivariate_desktop.png` hacia:
- `public/images/leon_pan_bivariate_v1.1.0.png`
- Se actualizo `README.md` para usar la ruta publica versionada del screenshot.
- Se actualizo `.gitignore` con exclusiones explicitas de activos internos/no-publicos:
- `data/interim/`
- `Planning/`
- `Cartografía oficial de secciones electorales.docx`
- `Imagen_referencia.png`

## Que se mantuvo

- Frontend y comportamiento funcional de la app.
- Bundle web final en:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`
- Pipeline y scripts en `src/pipeline/`.
- Artefactos finales en `data/processed/`.
- Documentacion tecnica y de release en `docs/` y `reports/`.

## Que salio del tracking (sin borrar local)

- `data/interim/`
- `Planning/`
- `Cartografía oficial de secciones electorales.docx`
- `Imagen_referencia.png`

Accion aplicada:
- `git rm --cached` (y `git rm -r --cached` en carpetas), preservando archivos en disco local.

## Por que `data/interim` y `Planning` no van en repo publico

- `data/interim/` contiene staging temporal de proceso; no es necesario para el consumo de la app publica ni para la lectura de portafolio.
- `Planning/` contiene notas internas y borradores de trabajo que agregan ruido para reclutadores/revisores.
- Mantener estos insumos fuera del tracking publico mejora claridad, enfoque y curacion del proyecto sin perder operatividad.

## Evidencia de validacion

- Verificacion de tracking:
- `git ls-files` ya no lista `data/interim/`, `Planning/`, `.docx` ni `Imagen_referencia.png`.
- `git ls-files` mantiene artefactos clave (`public/data`, `public/config`, `data/processed`, `src/pipeline`, `app`, `components`, `lib`, `styles`, `docs`, `reports`, `README.md`).
- QA:
- `npm run lint`: OK
- `npm run build`: falla en sandbox por `spawn EPERM` (entorno), OK fuera del sandbox.
- `npm run export:png`: OK fuera del sandbox (`exports/leon_pan_bivariate_desktop.png` regenerado).

## Veredicto final

Repositorio publico `v1.1.0` mas limpio y profesional para portafolio, sin cambios funcionales ni de metodologia.
