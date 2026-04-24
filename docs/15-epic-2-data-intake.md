# Epica 2 - Data Intake (Manual)

## Objetivo

Preparar el ingreso de archivos crudos oficiales antes de construir el pipeline geografico.

## Flujo de adquisicion manual

1. Identificar el insumo en fuentes oficiales curadas (`docs/10` y `docs/12`).
2. Descargar archivo por ruta directa o navegacion manual documentada.
3. Guardar en la carpeta destino bajo `data/raw/`.
4. Registrar el ingreso en `data/raw/data_inventory.csv`.
5. Registrar trazabilidad en `data/raw/manual/fuentes-manifest.csv`.
6. Ejecutar inspeccion inicial con `make inspect-raw`.
7. Revisar `reports/data_qa/raw_file_inventory.md`.

## Registro de archivos descargados

Al registrar un archivo en `data/raw/data_inventory.csv`:

- Completar `actual_filename` con el nombre real descargado.
- Actualizar `acquisition_status` a `downloaded`, `validated` o `rejected`.
- Mantener `acceptance_criteria` y agregar detalle en `notes` si aplica.

## Si el nombre real difiere del esperado

- No renombrar el crudo para "forzarlo" al nombre sugerido.
- Registrar el nombre real en `actual_filename`.
- Documentar en `notes` la equivalencia con `expected_filename`.
- Si hay ambiguedad de version, conservar el sufijo original y agregar fecha en `notes`.

## Archivos obligatorios para Epica 2.1

- Marco seccional INE para Guanajuato (carpeta `data/raw/ine/`).
- Catalogo geoelectoral INE util para llaves.
- Resultados IEEG 2018 de diputacion local (datos + metadata).
- Resultados IEEG 2021 de diputacion local (datos + metadata).
- `data/raw/manual/fuentes-manifest.csv` actualizado.

## Archivos opcionales

- INEGI red vial/contexto territorial (`data/raw/inegi/`).
- Equivalencias seccionales 2018-2021 (solo si existe fuente oficial).

## Checklist para pasar a Epica 2.1

- [ ] Carpetas `data/raw` completas y accesibles.
- [ ] Todos los archivos obligatorios descargados y registrados.
- [ ] `data/raw/data_inventory.csv` actualizado con `actual_filename`.
- [ ] `data/raw/manual/fuentes-manifest.csv` actualizado con URL y fecha.
- [ ] `make inspect-raw` ejecutado sin errores.
- [ ] `reports/data_qa/raw_file_inventory.md` generado y revisado.
- [ ] Cualquier faltante documentado como bloqueo real antes de transformar datos.

