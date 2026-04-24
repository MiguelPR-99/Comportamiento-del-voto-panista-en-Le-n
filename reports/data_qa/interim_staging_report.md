# Interim Staging Report

## Resumen

- Fecha: `2026-04-24T07:45:41`
- Decision: `aprobado para Epica 2.3`

## Archivos Generados

- `data\interim\ine_secciones_raw_index.csv`
- `data\interim\ine_secciones_leon.geojson`
- `data\interim\edmslm_leon.csv`
- `data\interim\ieeg_2018_diputaciones_seccion.csv`
- `data\interim\ieeg_2021_diputaciones_seccion.csv`
- `data\interim\join_key_diagnostics.csv`

## Conteos por Fuente

- ine_leon_sections: `846`
- edmslm_leon_sections: `846`
- ieeg_2018_sections: `699`
- ieeg_2021_sections: `713`

## Normalizacion

- Formula section_id: `section_id = entidad(2) + municipio(3) + seccion(normalizada sin decimales)`
- CRS INE detectado: `EPSG:32614 (heuristic)`
- Capa INE: `reports\data_qa\tmp_ine_extract\11 GUANAJUATO\SECCION.shp`
- Municipio normalizado en staging electoral: `020` corresponde a Leon para compatibilidad territorial entre fuentes.
- Nota CRS: `EPSG:32614` sigue pendiente de confirmacion programatica completa con stack geoespacial, pero no bloquea calculo de metricas electorales.

## Join Diagnostics

- complete: `699`
- partial_electoral: `14`
- no_electoral: `133`
- missing_2018: `147`
- missing_2021: `133`

## Duplicados y Nulos

- Duplicados: `{"ine": 0, "edmslm": 0, "ieeg_2018": 0, "ieeg_2021": 0}`
- Nulos: `{"edmslm": {"entidad": 0, "municipio": 0, "seccion": 0, "section_id": 0}, "ieeg_2018": {"entidad": 0, "municipio": 0, "seccion": 0, "section_id": 0, "pct_pan_2018": 2}, "ieeg_2021": {"entidad": 0, "municipio": 0, "seccion": 0, "section_id": 0, "pct_pan_2021": 0}}`

## Totales Electorales

- PAN 2018 total: `265152`
- Total votos 2018: `507529`
- PAN 2021 total: `264046`
- Total votos 2021: `456168`

## Advertencias

- 147 section_id without 2018 electoral data.
- 133 section_id without 2021 electoral data.
- Regla Epica 2.3: `missing_2018` y `missing_2021` se trasladan a `has_data=false` y clasificacion `no_data`.
