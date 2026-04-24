# Data Acquisition Plan (Epica 1.2)

## Alcance

Definir una ruta operativa de adquisicion para Epica 2 sin descargar datos en esta fase.

## Regla de aprobacion para Epica 2

- `Endpoint directo no es obligatorio`.
- El insumo pasa si tiene:
- portal oficial confirmado,
- ruta manual usable,
- criterio de aceptacion del archivo descargado.

## Estructura destino

```text
data/raw/
  ine/
  ieeg/2018/
  ieeg/2021/
  inegi/
  manual/
```

## Inventario operativo por archivo

| Carpeta destino | Nombre sugerido | Formato esperado | Columnas minimas esperadas | Fuente | Estado actual | Accion manual pendiente | Criterio de aceptacion del archivo | Obligatorio para Epica 2 |
|---|---|---|---|---|---|---|---|---|
| `data/raw/ine/` | `ine_marco_seccional_gto_YYYYMMDD.*` | SHP/GeoPackage/ZIP oficial | `entidad`, `municipio`, `seccion`, `geometry` | INE | Pendiente | Navegar portal INE oficial y descargar marco seccional de Guanajuato | `Sirve` si incluye Guanajuato, geometria valida y llaves seccionales equivalentes a entidad/municipio/seccion | si |
| `data/raw/ine/` | `ine_catalogo_geoelectoral_gto_YYYYMMDD.*` | CSV/TXT/MDB/ZIP | `cve_ent`, `cve_mun`, `cve_secc` | INE | Pendiente | Ubicar catalogo oficial vigente y descargar version util | `Sirve` si permite validar normalizacion de llaves (`cve_ent`, `cve_mun`, `cve_secc`) | si |
| `data/raw/ieeg/2018/` | `ieeg_dip_local_2018_YYYYMMDD.*` | CSV/XLSX/ZIP oficial | `entidad`, `municipio`, `seccion` o `casilla`, `votos_pan`, `votos_totales` | IEEG | Pendiente | Entrar a computos 2018 y exportar tabla oficial | `Sirve` si se puede reconstruir a nivel seccion y contiene votos PAN + total de votos | si |
| `data/raw/ieeg/2018/` | `ieeg_dip_local_2018_metadata_YYYYMMDD.*` | PDF/HTML/TXT | definicion de variables y fecha de corte | IEEG | Pendiente | Guardar nota metodologica oficial asociada al dataset descargado | `Sirve` si documenta definiciones de campos usados en join y calculos | si |
| `data/raw/ieeg/2021/` | `ieeg_dip_local_2021_YYYYMMDD.*` | CSV/XLSX/ZIP oficial | `entidad`, `municipio`, `seccion` o `casilla`, `votos_pan`, `votos_totales` | IEEG | Pendiente | Entrar a portal 2021 y exportar tabla oficial | `Sirve` si se puede reconstruir a nivel seccion y contiene votos PAN + total de votos | si |
| `data/raw/ieeg/2021/` | `ieeg_dip_local_2021_metadata_YYYYMMDD.*` | PDF/HTML/TXT | definicion de variables y fecha de corte | IEEG | Pendiente | Guardar nota metodologica oficial asociada al dataset descargado | `Sirve` si documenta definiciones de campos usados en join y calculos | si |
| `data/raw/inegi/` | `inegi_rnc_gto_YYYYMMDD.*` | SHP/GeoJSON/ZIP | identificador de tramo, tipo vial, `geometry` | INEGI | Pendiente | Descargar dataset vial oficial si se decide overlay contextual | `Sirve` solo para contexto u overlay opcional; no afecta generacion de `secciones.geojson` | no |
| `data/raw/inegi/` | `inegi_contexto_territorial_gto_YYYYMMDD.*` | SHP/GeoJSON/ZIP | limites/contexto, `geometry` | INEGI | Pendiente | Descargar solo si el contexto editorial lo requiere | `Sirve` para contexto visual, no para calculo tematico electoral | no |
| `data/raw/manual/` | `fuentes-manifest.csv` | CSV | `insumo`, `url`, `fecha_consulta`, `estado_verificacion`, `responsable` | Curaduria interna | No creado | Crear plantilla y completar por cada descarga | `Sirve` si registra trazabilidad completa de cada archivo adquirido | si |
| `data/raw/manual/` | `equivalencias_seccionales_2018_2021.*` | CSV/XLSX/PDF oficial | claves origen-destino y tipo de cambio | INE/IEEG | Pendiente | Buscar documento oficial; si no existe, registrar ausencia confirmada | `Sirve` si es oficial y util para conciliacion; si no existe, dejar evidencia de no disponibilidad | no |

## Reglas operativas

- No se acepta como primaria ninguna fuente no institucional.
- Toda descarga debe registrarse en `data/raw/manual/fuentes-manifest.csv`.
- Todo archivo guardado debe incluir fecha en el nombre sugerido.
- Si un portal solo permite navegacion manual, la ruta y evidencia de pasos deben quedar documentadas.

## Estado de esta fase

- Plan operativo definido.
- Descargas no iniciadas por restriccion de Epica 1.2.
