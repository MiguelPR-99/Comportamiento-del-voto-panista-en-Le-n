# Raw Schema Audit

## Resumen Ejecutivo

- Fecha: `2026-04-24T02:05:21`
- Decision: `aprobado para Epica 2.2`
- Hallazgos clave:
- EDMSLM mantiene campos utiles para entidad/municipio/seccion.
- IEEG 2018 confirma votos PAN y TOTAL en granularidad por casilla.
- IEEG 2021 confirma votos PAN y TOTAL_VOTOS_CALCULADO en granularidad por casilla.
- Paquete INE se resolvio mediante extraccion del .7z anidado y validacion de capa SECCION.

## Archivos Inspeccionados

- `data\raw\ine\bgd_11_Shapefile.zip` -> status: `inspected`, format: `zip -> 7z -> shapefile`
- `data\raw\ine\edmslm_ine_corte_ene_2026.txt` -> status: `ok`, format: `txt`
- `data\raw\ieeg\2018\Computo x casillas Diputaciones.xlsx` -> status: `ok`, format: `xlsx`
- `data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip` -> status: `ok`, format: `zip`
- `data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip::20210610_1200_DIP_LOC_GTO.zip` -> status: `ok`, format: `nested zip`
- `data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip::20210610_1200_DIP_LOC_GTO.zip::GTO_DIP_LOC_CANDIDATURAS_2021.csv` -> status: `ok`, format: `csv (cp1252, ',')`, role: `auxiliary_metadata`
- `data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip::20210610_1200_DIP_LOC_GTO.zip::GTO_DIP_LOC_2021.csv` -> status: `ok`, format: `csv (utf-8-sig, ',')`, role: `primary_votes`
- `data\raw\manual\fuentes-manifest.csv` -> status: `ok`, format: `csv`
- `data\raw\data_inventory.csv` -> status: `ok`, format: `csv`

## Resolucion paquete INE / shapefile seccional

- ZIP analizado: `data\raw\ine\bgd_11_Shapefile.zip`
- .7z anidados detectados: `["11 GUANAJUATO.7z"]`
- Extractor usado: `tar`
- Nota extractor: `py7zr not available (install: pip install py7zr) | tar extraction succeeded`
- Capa seccional detectada: `reports\data_qa\tmp_ine_extract\11 GUANAJUATO\SECCION.shp`
- CRS detectado: `EPSG:32614 (heuristic)`
- Filas: `3357`
- Tipo de geometria: `["Polygon"]`
- Columnas: `id, entidad, distrito_f, distrito_l, municipio, seccion, tipo, control`
- Campos candidatos entidad: `["entidad"]`
- Campos candidatos municipio: `["municipio"]`
- Campos candidatos seccion: `["seccion"]`
- Geometrias nulas: `0`
- Geometrias invalidas (chequeo estructural): `0`
- Usable para join territorial: `True`

## Esquemas detectados para joins y votos

- EDMSLM key candidates: `{"entidad": ["ENTIDAD"], "municipio": ["MUNICIPIO", "NOMBRE_MUNICIPIO"], "seccion": ["SECCION", "TIPO_SECCION"], "distrito_local": ["DISTRITO"], "municipio_nombre": ["NOMBRE_MUNICIPIO"], "casilla": []}`
- IEEG 2018 key candidates: `{"entidad": [], "municipio": [], "seccion": ["SECCI\u00d3N"], "distrito_local": [], "municipio_nombre": [], "casilla": ["CASILLA"]}`
- IEEG 2018 vote candidates: `{"pan": ["PAN"], "total_votos": ["TOTAL"]}`
- IEEG 2021 principal (data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip::20210610_1200_DIP_LOC_GTO.zip::GTO_DIP_LOC_2021.csv):
- key candidates: `{"entidad": ["ID_ESTADO"], "municipio": [], "seccion": ["SECCION"], "distrito_local": ["ID_DISTRITO_LOCAL", "DISTRITO_LOCAL"], "municipio_nombre": [], "casilla": ["CLAVE_CASILLA", "ID_CASILLA", "TIPO_CASILLA"]}`
- vote candidates: `{"pan": ["PAN"], "total_votos": ["TOTAL_VOTOS_CALCULADO"]}`
- IEEG 2021 auxiliar (data\raw\ieeg\2021\computos_ieeg_2021_diputaciones_base_datos.zip::20210610_1200_DIP_LOC_GTO.zip::GTO_DIP_LOC_CANDIDATURAS_2021.csv): metadatos de candidaturas, no fuente principal de votos.

## Riesgos

- IEEG 2018 no trae municipio explicito; se requiere derivacion territorial por seccion.
- IEEG 2021 no trae municipio explicito; se requiere derivacion territorial por seccion.

## Bloqueadores

- None

## Decision

- `aprobado para Epica 2.2`
