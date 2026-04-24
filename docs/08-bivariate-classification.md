# Bivariate Classification v1

## Decision metodologica cerrada para v1

La clasificacion bivariante v1 se define por cortes editoriales manuales alineados con la leyenda original.

- No se usan cuantiles en v1.
- Objetivo: preservar comparabilidad visual y narrativa con la referencia original.
- Solo puede cambiarse mediante decision documentada si en Epica 1 aparece evidencia metodologica original distinta.

## Variables de entrada

- `vote_share_bin` se calcula desde `pct_pan_2021`.
- `delta_bin` se calcula desde `delta_pan_pp` (`pct_pan_2021 - pct_pan_2018`).

## Cortes obligatorios v1

### `vote_share_bin` (sobre `pct_pan_2021`)

- `low` si `pct_pan_2021 < 40`
- `mid` si `40 <= pct_pan_2021 < 60`
- `high` si `pct_pan_2021 >= 60`

### `delta_bin` (sobre `delta_pan_pp`)

- `decline` si `delta_pan_pp < -10`
- `stable` si `-10 <= delta_pan_pp <= 10`
- `growth` si `delta_pan_pp > 10`

## Regla de `Sin Datos`

- Si falta cualquiera de `pct_pan_2018`, `pct_pan_2021` o `delta_pan_pp`:
- `has_data=false`
- `vote_share_bin="no_data"`
- `delta_bin="no_data"`
- `bivariate_class="no_data"`

Convencion v1:

- Se usa token de texto `no_data` (no `null`) para bins y clase final.

## Dominio cerrado de `bivariate_class`

- `decline_low`
- `decline_mid`
- `decline_high`
- `stable_low`
- `stable_mid`
- `stable_high`
- `growth_low`
- `growth_mid`
- `growth_high`
- `no_data`

Regla:

- Ningun otro valor es valido en v1.

## Mapping clase-leyenda 3x3

Filas de la leyenda (vertical):

- superior: `growth`
- media: `stable`
- inferior: `decline`

Columnas de la leyenda (horizontal):

- izquierda: `low`
- centro: `mid`
- derecha: `high`

Tabla de cruce:

| `delta_bin` \ `vote_share_bin` | `low` | `mid` | `high` |
|---|---|---|---|
| `growth` | `growth_low` | `growth_mid` | `growth_high` |
| `stable` | `stable_low` | `stable_mid` | `stable_high` |
| `decline` | `decline_low` | `decline_mid` | `decline_high` |

## Conexion con paleta

- Cada valor de `bivariate_class` se mapea a un color definido en `editorial-map-spec.json -> legend.class_color_map`.
- `secciones.geojson.color_hex` debe salir de ese mapping, no de decisiones ad hoc en implementacion.
- `no_data` usa color base + hatch definido en `no_data_style`.

## Pruebas minimas de consistencia metodologica

- El cruce de bins produce exactamente 9 clases tematicas posibles + `no_data`.
- No existen clases fuera del dominio cerrado.
- Todas las features con `has_data=true` tienen bins y clase distintos de `no_data`.
- Todas las features con `has_data=false` cumplen convencion `no_data`.
