# Web Bundle Report

## Resumen Ejecutivo

- Fecha: `2026-04-24T08:08:50`
- Veredicto: `aprobado para Epica 3`

## Archivos Generados

- `data\processed\secciones_leon_bivariate.geojson`
- `data\processed\editorial-map-spec.json`
- `public\data\secciones.geojson`
- `public\config\editorial-map-spec.json`
- `reports\data_qa\web_bundle_report.md`
- `reports\data_qa\web_bundle_report.json`

## Conteos Finales

- features: `846`
- no_data_count: `149`
- has_data_false_count: `149`

## Conteo Por Clase Bivariante

- decline_low: `3`
- decline_mid: `1`
- decline_high: `0`
- stable_low: `7`
- stable_mid: `428`
- stable_high: `122`
- growth_low: `0`
- growth_mid: `30`
- growth_high: `106`
- no_data: `149`

## Payload

- total_mb: `2.603`
- public/data/secciones.geojson bytes: `2725385`
- public/config/editorial-map-spec.json bytes: `4215`

## Validacion De Contrato

- required_fields_present: `True`
- missing_fields: `[]`
- unexpected_fields_present: `[]`

## QA

- public_data_exists: `True`
- public_config_exists: `True`
- feature_count: `846`
- feature_count_expected_846: `True`
- duplicate_section_ids: `0`
- all_classes_in_domain: `True`
- class_counts_match_epic_2_3: `True`
- no_data_count: `149`
- no_data_expected_149: `True`
- has_data_false_count: `149`
- has_data_false_expected_149: `True`
- has_data_no_data_inconsistency: `0`
- all_colors_present: `True`
- all_colors_in_class_map: `True`
- contract_required_fields: `True`
- contract_no_missing_fields: `True`
- contract_no_unexpected_fields: `True`
- frontend_files_in_public: `[]`
- no_data_matches_epic_2_3_report: `True`
- has_data_false_matches_epic_2_3_report: `True`

## Warnings

- is_in_inset se asigno en false por defecto; no existe geometria formal de inset en esta fase.
- CRS indicaba EPSG:4326 pero coordenadas no estaban en rango geodesico; se corrigio asumiendo EPSG:32614.

## Pendientes Para Frontend

- Definir geometria y posicion final de inset urbano (is_in_inset).
- Implementar render MapLibre y microinteracciones editoriales.
- Aplicar jerarquia tipografica final y composicion visual de la leyenda 3x3.
