# Fase 0 - Especificacion Editorial Interactiva

Este directorio contiene la documentacion de la Fase 0 para la pieza editorial interactiva:
`Comportamiento del voto panista en Leon`.

La Fase 0 cierra definiciones de producto, direccion visual, arquitectura preliminar y criterios de aceptacion antes de programar frontend o pipeline geografico.

## Orden recomendado de lectura

1. `01-product-brief.md`
2. `02-reverse-engineering-visual.md`
3. `03-arquitectura-preliminar.md`
4. `04-criterios-de-aceptacion.md`
5. `05-decisiones-y-riesgos.md`
6. `06-epic-0-closure.md`

## Estado de la fase

- Se conserva enfoque editorial interactivo, `desktop-first`.
- Se mantiene objetivo de replica fiel del mapa original con microinteracciones.
- No se desarrolla codigo de frontend en esta fase.
- No se crea pipeline geografico en esta fase.
- No se descargan datos en esta fase.

## Fuente de referencia visual

- Imagen base: `C:\\Users\\migue\\Desktop\\Salem\\Imagen_referencia.png`

## Entorno Python Recomendado

1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`

Notas:
- El pipeline geoespacial de este repositorio depende de `pandas/geopandas`.
- Instala dependencias dentro de `.venv` (no global).
- Si PowerShell bloquea `activate`, usa `cmd /c ".venv\\Scripts\\activate.bat"` para activar el entorno.
