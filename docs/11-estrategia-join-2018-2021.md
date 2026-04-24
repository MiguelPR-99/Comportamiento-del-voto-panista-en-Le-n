# Estrategia de Join 2018-2021 (Diputacion Local)

## Objetivo

Definir una union reproducible entre cartografia seccional y resultados 2018/2021 para Leon, con reglas canonicas cerradas para llaves y tratamiento de faltantes.

## Llave canonica de join

Llave compuesta primaria:

- `entidad`
- `municipio`
- `seccion`

Formato canonico obligatorio:

- `entidad`: string de 2 digitos. Guanajuato = `"11"`.
- `municipio`: string de 3 digitos con left padding (`cve_mun` oficial).
- `seccion`: string sin espacios, sin decimales, sin separadores.
- `section_id`: concatenacion canonica `entidad + municipio + seccion_normalizada`.

Regla de padding para `seccion`:

- Si existe campo oficial `cve_secc` en la fuente, usarlo como verdad (incluyendo su padding oficial).
- Si `seccion` se deriva desde casilla y no existe `cve_secc`, mantener string numerico limpio sin padding adicional.
- Si despues se confirma una longitud oficial fija distinta, se actualiza esta regla por decision documentada.

## Campos minimos requeridos

### Cartografia (INE)

- `entidad`
- `municipio`
- `seccion`
- `geometry`

### Resultados 2018 (IEEG)

- `entidad` (o derivable de ambito oficial)
- `municipio`
- `seccion` o `casilla` derivable a seccion
- `votos_pan_2018`
- `votos_totales_2018`

### Resultados 2021 (IEEG)

- `entidad` (o derivable de ambito oficial)
- `municipio`
- `seccion` o `casilla` derivable a seccion
- `votos_pan_2021`
- `votos_totales_2021`

## Normalizacion obligatoria antes del join

1. Limpiar espacios al inicio y final (`trim`) en `entidad`, `municipio`, `seccion` y `casilla`.
2. Convertir `entidad` y `municipio` a string y aplicar padding canonico (2 y 3 digitos).
3. Eliminar decimales espurios y caracteres no numericos en `seccion`.
4. Si la fuente viene por casilla:
- eliminar sufijos de tipo de casilla del identificador.
- derivar `seccion` desde el componente seccional del mismo campo.
- agregar casillas por seccion antes del join.
5. Validar unicidad de (`entidad`,`municipio`,`seccion`) por dataset ya normalizado.
6. Construir `section_id` canonico con la concatenacion definida.

## Regla base de join

1. Normalizar llaves de 2018 y 2021 con reglas canonicas.
2. Agregar a nivel seccion cuando la fuente venga por casilla.
3. Ejecutar `full outer join` entre 2018 y 2021 por llave compuesta.
4. Unir el consolidado al marco geografico INE por la misma llave.
5. Marcar no-match para tratamiento `no_data`.

## Reglas para no match y duplicados

No-match cartografia vs resultados:

- Si la seccion existe en cartografia pero falta en 2018 o 2021:
- mantener geometria;
- `has_data=false`;
- bins y clase en `no_data`;
- registrar conteo en reporte QA.

- Si la seccion existe en resultados pero no en cartografia:
- no forzar geometria;
- registrar incidencia para revision de fuente/equivalencias.

Duplicados:

- Duplicado exacto de (`entidad`,`municipio`,`seccion`) tras normalizacion bloquea avance.
- Duplicado por nivel casilla se resuelve con agregacion previa por seccion.

## Reglas para `no_data`

- No asignar cero cuando falte 2018 o 2021.
- Si falta dato clasificatorio, usar `no_data` segun contrato:
- `has_data=false`
- `vote_share_bin=no_data`
- `delta_bin=no_data`
- `bivariate_class=no_data`

## Tabla de equivalencias seccionales (uso condicional)

- Si existe tabla oficial INE/IEEG de equivalencias, usarla como insumo de conciliacion.
- Si no existe, no inventar equivalencias manuales para v1.
- La ausencia de tabla no bloquea el join inicial si se etiquetan no-match y `no_data`.

## Entregables de join (fase de datos)

- Tabla de cobertura: match completo, no match 2018, no match 2021, no match cartografia.
- Listado de `section_id` en `no_data` con causa.
- Reporte de duplicados y resolucion aplicada.
