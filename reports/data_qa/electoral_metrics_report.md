# Electoral Metrics Report

## Resumen Ejecutivo

- Fecha: `2026-04-24T08:00:15`
- Veredicto: `aprobado para Epica 2.4`
- Secciones analizadas: `846`

## Conteos

- has_data=true: `697`
- has_data=false: `149`
- bivariate_class=no_data: `149`

## Conteo por bivariate_class

- decline_low: `3`
- decline_mid: `1`
- growth_high: `106`
- growth_mid: `30`
- no_data: `149`
- stable_high: `122`
- stable_low: `7`
- stable_mid: `428`

## Secciones sin Match

- total_with_issues: `149`
- sample_section_ids: `110201536, 110201538, 110203155, 110203156, 110203157, 110203158, 110203159, 110203160, 110203161, 110203162, 110203163, 110203164, 110203165, 110203166, 110203167, 110203168, 110203182, 110203183, 110203184, 110203185, 110203186, 110203187, 110203188, 110203189, 110203190, 110203191, 110203192, 110203193, 110203194, 110203195`

## Totales Electorales

- PAN 2018 total: `265152`
- Total votos 2018: `507529`
- PAN 2021 total: `264046`
- Total votos 2021: `456168`

## Validaciones

- duplicate_section_ids: `0`
- pct_pan_2018_out_of_range: `0`
- pct_pan_2021_out_of_range: `0`
- delta_pan_pp_out_of_range: `0`
- invalid_bivariate_class: `0`
- has_data_no_data_inconsistency: `0`
- geometry_preserved: `True`

## Advertencias

- 16 section_id with missing 2018 metrics.
- 133 section_id with missing 2018 and 2021 metrics.

## Nota Sobre Ceros Heredados

- Existen 2 secciones con `pan_2018_votos=0` y `total_2018=0` heredadas del staging 2018.
- Estos valores no fueron inyectados artificialmente durante Epica 2.3.
- Los casos quedan trazables dentro de `missing_2018` y pasan a `no_data` cuando `pct_pan_2018` es `null`.
- No se debe imputar cero para resolver faltantes.

## Archivos Generados

- `data\interim\leon_electoral_metrics.csv`
- `data\interim\leon_electoral_metrics.geojson`
- `reports\data_qa\electoral_metrics_report.md`
- `reports\data_qa\electoral_metrics_report.json`
