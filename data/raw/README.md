# Raw Data Intake Guide (Epica 2.0)

Este directorio almacena insumos crudos oficiales descargados manualmente.

Regla clave:

- Los archivos crudos no deben editarse manualmente.
- Si un archivo requiere limpieza o estandarizacion, se hace en `data/interim/` en fases posteriores.

## Que va en cada carpeta

| Carpeta | Fuente esperada | Archivo esperado | Formato esperado | Criterio minimo de aceptacion |
|---|---|---|---|---|
| `data/raw/ine/` | INE | Marco seccional Guanajuato + catalogo geoelectoral | SHP/GeoPackage/ZIP, CSV/TXT/MDB/ZIP | Incluye llaves equivalentes a `entidad`, `municipio`, `seccion` y geometria valida (para marco seccional) |
| `data/raw/ieeg/2018/` | IEEG | Resultados diputacion local 2018 + metadata | CSV/XLSX/ZIP, PDF/HTML/TXT | Permite reconstruir a nivel seccion (directo o desde casilla) y contiene votos PAN + total votos |
| `data/raw/ieeg/2021/` | IEEG | Resultados diputacion local 2021 + metadata | CSV/XLSX/ZIP, PDF/HTML/TXT | Permite reconstruir a nivel seccion (directo o desde casilla) y contiene votos PAN + total votos |
| `data/raw/inegi/` | INEGI | Red vial/contexto territorial (opcional v1) | SHP/GeoJSON/ZIP | Usable como contexto u overlay opcional; no bloquea generacion de `secciones.geojson` |
| `data/raw/manual/` | Curaduria interna + INE/IEEG | `fuentes-manifest.csv` + equivalencias oficiales (si existen) | CSV, CSV/XLSX/PDF | Manifest completo por archivo descargado; equivalencias solo si son oficiales |

## Inventario obligatorio

- Registrar cada archivo descargado en `data/raw/data_inventory.csv`.
- Mantener actualizado `data/raw/manual/fuentes-manifest.csv` con URL y fecha de consulta.

