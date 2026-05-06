# Repository Publication Checklist

## Must keep
- README.md
- package.json / lockfile
- app/
- components/
- lib/
- styles/
- public/data/secciones.geojson
- public/config/editorial-map-spec.json
- public/images/export screenshot
- scripts/export-png.mjs
- docs/portfolio_case_study.md
- reportes finales de QA o cierre
- data/raw/README.md
- data/raw/data_inventory.csv
- data/raw/manual/fuentes-manifest.csv
- .gitignore
- LICENSE (si existe)

## Keep only if useful
- data/processed/
- documentación técnica extensa
- reportes detallados

## Archive or omit from public-facing repo if present
- raw data files pesados
- data/interim
- temporary exports
- local planning files
- prompts internos
- screenshots duplicados
- archivos con rutas locales
- outputs experimentales
- notebooks sucios
- archivos que contradigan la versión final

## Pre-publication checks
- No secrets
- No .env
- No local absolute paths
- README opens with a clear value proposition
- Demo link works
- Main screenshot is visible
- `npm run lint` passes or failure is documented
- `npm run build` passes or failure is documented
