.PHONY: inspect-raw audit-raw-schemas audit-ine-geography build-interim build-metrics build-web-bundle export-png

inspect-raw:
	python src/pipeline/inspect_raw_files.py

audit-raw-schemas:
	python src/pipeline/audit_raw_schemas.py

audit-ine-geography:
	python src/pipeline/audit_ine_geography.py

build-interim:
	python src/pipeline/build_interim_staging.py

build-metrics:
	python src/pipeline/build_electoral_metrics.py

build-web-bundle:
	python src/pipeline/build_web_bundle.py

export-png:
	npm run export:png
