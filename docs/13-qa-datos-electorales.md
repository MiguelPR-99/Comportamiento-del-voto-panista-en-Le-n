# QA de Datos Electorales (Previo a Pipeline)

## Objetivo

Definir checks minimos de calidad para aceptar insumos de Epica 1 antes de clasificacion bivariante y render editorial.

## Matriz de checks

| ID | Check | Regla verificable | Severidad | Accion si falla |
|---|---|---|---|---|
| `QA-01` | Unicidad de clave seccional | No debe haber duplicados en (`entidad`,`municipio`,`seccion`) por dataset consolidado | Critica | Bloquear avance y resolver normalizacion/duplicados |
| `QA-02` | Geometrias validas | Todas las features de secciones deben tener geometria valida y tipo `Polygon`/`MultiPolygon` | Critica | Corregir/cambiar fuente antes de continuar |
| `QA-03` | CRS esperado | Artefactos web geograficos deben salir en `EPSG:4326`; si se calcula en CRS metrico, reproyeccion documentada | Critica | Reproyectar y revalidar |
| `QA-04` | Filas sin match 2018/2021 | Toda fila sin correspondencia debe quedar etiquetada y contabilizada en reporte de cobertura | Alta | Registrar incidencia y aplicar regla `no_data` |
| `QA-05` | Duplicados de resultados | Si hay multiples filas por seccion tras agregacion a seccion, se considera error de integracion | Critica | Revisar agregacion casilla->seccion y limpiar |
| `QA-06` | Totales electorales consistentes | `votos_pan <= votos_totales` y `votos_totales > 0` donde aplique | Alta | Corregir origen o excluir fila con justificacion |
| `QA-07` | Porcentajes en rango | `pct_pan_2018` y `pct_pan_2021` en [0,100] o `no_data` | Critica | Recalcular o marcar `no_data` |
| `QA-08` | Delta razonable | `delta_pan_pp = pct_pan_2021 - pct_pan_2018` con tolerancia +-0.01 y rango [-100,100] | Alta | Recalcular delta y auditar formula |
| `QA-09` | Bins validos | `vote_share_bin` en `{low,mid,high,no_data}` y `delta_bin` en `{decline,stable,growth,no_data}` | Critica | Reclasificar usando metodologia v1 |
| `QA-10` | Clase bivariante valida | `bivariate_class` solo en dominio cerrado (`9` clases + `no_data`) | Critica | Bloquear build y corregir mapping |
| `QA-11` | Coherencia `no_data` | Si `has_data=false` entonces bins y clase deben ser `no_data`; nunca cero forzado | Critica | Ajustar reglas de imputacion |
| `QA-12` | Color-clase consistente | `color_hex` debe coincidir con `legend.class_color_map` de `editorial-map-spec.json` | Alta | Regenerar color por mapping oficial |

## Cobertura minima esperada de QA

- `100%` de filas pasan checks criticos (`QA-01`, `QA-02`, `QA-03`, `QA-05`, `QA-07`, `QA-09`, `QA-10`, `QA-11`).
- Checks altos pueden tener incidencias solo si quedan documentadas y tratadas en output final (`no_data` o exclusion justificada).

## Evidencias requeridas por corrida de QA

- Reporte de unicidad de llave.
- Resumen de validez geometrica.
- Reporte de CRS de entrada/salida.
- Tabla de no match 2018/2021.
- Conteo final por `bivariate_class`.
- Conteo final de `has_data=false` y justificacion.

