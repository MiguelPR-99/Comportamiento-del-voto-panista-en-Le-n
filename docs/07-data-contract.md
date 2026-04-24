# Data Contract Operativo v1

## Alcance

Este documento define el contrato de datos obligatorio para iniciar Epica 1 sin ambiguedad de implementacion.

## Convenciones globales

| Campo | Valor |
|---|---|
| `contract_version` | `1.0.0` |
| `delivery_crs` | `EPSG:4326` |
| `analysis_crs_allowed` | `EPSG:32614` (u otro CRS metrico documentado) |
| `encoding` | `UTF-8` |
| `decimal_precision_recommended` | 6 decimales para coordenadas WGS84 |
| `null_policy` | Para `has_data=false`, bins y clase usan convencion `no_data` |

Regla global de coherencia:

- `color_hex` en `secciones.geojson` debe provenir del mapping definido en `editorial-map-spec.json`, nunca de logica hardcodeada en frontend.

## A) `editorial-map-spec.json`

### Metadata del artefacto

| Atributo | Definicion |
|---|---|
| Nombre de archivo | `editorial-map-spec.json` |
| Proposito | Configuracion editorial y cartografica de la pieza (layout, leyenda, paleta, politica de interaccion) |
| Formato | JSON |
| CRS esperado | N/A (sin geometria directa) |
| Geometria esperada | N/A |
| Version de esquema | `1.0.0` |

### Campos obligatorios

| Campo | Tipo | Req | Valores permitidos | Ejemplo | Regla semantica | Regla de validacion |
|---|---|---|---|---|---|---|
| `schema_version` | string | Si | `1.0.0` | `"1.0.0"` | Version del esquema del artefacto | Debe coincidir con version soportada por frontend |
| `project_id` | string | Si | slug kebab-case | `"leon-pan-vote-2018-2021"` | Identificador unico del proyecto | Regex `^[a-z0-9-]+$` |
| `title` | string | Si | texto no vacio | `"Comportamiento del voto panista en Leon"` | Titulo editorial | Largo minimo 10 caracteres |
| `subtitle` | string | Si | texto no vacio | `"Variaciones en el voto..."` | Subtitulo metodologico | Largo minimo 20 caracteres |
| `source_lines` | array string | Si | 1..10 lineas | `["Fuentes: IEEG, INE, INEGI"]` | Creditos de fuente | No permite array vacio |
| `author_note` | string | Si | texto | `"Elaboro ..."` | Nota de elaboracion | No nulo |
| `palette` | object | Si | llaves hex + tokens | ver ejemplo abajo | Paleta editorial y bivariante | Todos los colores en formato `#RRGGBB` |
| `legend` | object | Si | estructura v1 | ver ejemplo abajo | Define matriz 3x3, labels y clase-color | Debe contener 9 clases + `no_data` |
| `main_view` | object | Si | centro + zoom + bounds opcional | `{"center":[-101.67,21.12],"zoom":9.7}` | Camara inicial mapa principal | `center` longitud 2, zoom numerico |
| `inset_view` | object | Si | centro + zoom + bbox | `{"center":[-101.67,21.12],"zoom":12.4}` | Camara inicial inset | Misma regla que `main_view` |
| `scale_bar_km` | number | Si | >0 | `3` | Longitud de escala grafica | Valor positivo |
| `no_data_style` | object | Si | hatch + color + stroke | `{"fill":"#C5C4C2","hatch":"diagonal"}` | Estilo para `no_data` | `hatch` debe ser `diagonal` en v1 |
| `interaction_policy` | object | Si | flags booleanas | `{"allow_hover":true,"allow_scroll_zoom":false}` | Limites de interaccion editorial | Debe bloquear patrones tipo dashboard en v1 |

### Estructura minima sugerida (ejemplo)

```json
{
  "schema_version": "1.0.0",
  "project_id": "leon-pan-vote-2018-2021",
  "title": "Comportamiento del voto panista en Leon",
  "subtitle": "Variaciones en el voto...",
  "source_lines": ["Fuentes: IEEG, INE, INEGI"],
  "author_note": "Elaboro ...",
  "palette": {
    "decline_low": "#...",
    "decline_mid": "#...",
    "decline_high": "#...",
    "stable_low": "#...",
    "stable_mid": "#...",
    "stable_high": "#...",
    "growth_low": "#...",
    "growth_mid": "#...",
    "growth_high": "#...",
    "no_data": "#C5C4C2"
  },
  "legend": {
    "x_axis_label": "% de votos totales (2021)",
    "y_axis_label": "Variacion vs 2018 (pp)",
    "classes_order": [
      "growth_low", "growth_mid", "growth_high",
      "stable_low", "stable_mid", "stable_high",
      "decline_low", "decline_mid", "decline_high"
    ],
    "class_color_map": {
      "decline_low": "#...",
      "decline_mid": "#...",
      "decline_high": "#...",
      "stable_low": "#...",
      "stable_mid": "#...",
      "stable_high": "#...",
      "growth_low": "#...",
      "growth_mid": "#...",
      "growth_high": "#...",
      "no_data": "#C5C4C2"
    }
  },
  "main_view": {"center": [-101.67, 21.12], "zoom": 9.7},
  "inset_view": {"center": [-101.67, 21.12], "zoom": 12.4},
  "scale_bar_km": 3,
  "no_data_style": {"fill": "#C5C4C2", "hatch": "diagonal", "stroke": "#8A8A8A"},
  "interaction_policy": {
    "allow_hover": true,
    "allow_focus": true,
    "allow_scroll_zoom": false,
    "allow_filters": false,
    "allow_tabs": false,
    "allow_sidebar_metrics": false
  }
}
```

## B) `secciones.geojson`

### Metadata del artefacto

| Atributo | Definicion |
|---|---|
| Nombre de archivo | `secciones.geojson` |
| Proposito | Capa principal por seccion electoral con metricas y clase bivariante |
| Formato | GeoJSON (`FeatureCollection`) |
| CRS esperado | `EPSG:4326` obligatorio en entrega web |
| Geometria esperada | `Polygon` o `MultiPolygon` |
| Version de esquema | `1.0.0` |

Nota de CRS:

- Analisis puede calcularse previamente en CRS metrico.
- El artefacto de salida web debe estar en `WGS84 / EPSG:4326`.

### Campos obligatorios por feature (`properties`)

| Campo | Tipo | Req | Valores permitidos | Ejemplo | Regla semantica | Regla de validacion |
|---|---|---|---|---|---|---|
| `schema_version` | string | Si | `1.0.0` | `"1.0.0"` | Version del esquema de feature | Debe coincidir con version del artefacto |
| `section_id` | string | Si | id oficial de seccion | `"110200123"` | Identificador unico de seccion | Unico dentro del archivo |
| `municipio` | string | Si | texto | `"Leon"` | Municipio de la seccion | Para v1 debe ser `Leon` |
| `distrito_local` | string | Si | texto/codigo distrito | `"D-06"` | Distrito local de referencia | No vacio |
| `pct_pan_2018` | number/null | Si | 0..100 o null | `48.37` | % PAN en 2018 | Si hay dato, rango 0..100 |
| `pct_pan_2021` | number/null | Si | 0..100 o null | `56.12` | % PAN en 2021 | Si hay dato, rango 0..100 |
| `delta_pan_pp` | number/null | Si | numero real o null | `7.75` | Diferencia en puntos porcentuales 2021-2018 | Si hay dato, debe cumplir `pct_pan_2021 - pct_pan_2018` con tolerancia +-0.01 |
| `vote_share_bin` | string | Si | `low`, `mid`, `high`, `no_data` | `"mid"` | Bin por % PAN 2021 | Si `has_data=false`, debe ser `no_data` |
| `delta_bin` | string | Si | `decline`, `stable`, `growth`, `no_data` | `"stable"` | Bin por variacion vs 2018 | Si `has_data=false`, debe ser `no_data` |
| `bivariate_class` | string | Si | `decline_low`, `decline_mid`, `decline_high`, `stable_low`, `stable_mid`, `stable_high`, `growth_low`, `growth_mid`, `growth_high`, `no_data` | `"stable_mid"` | Clase final de leyenda 3x3 | Si `has_data=false`, debe ser `no_data` |
| `color_hex` | string | Si | `#RRGGBB` | `"#615CFF"` | Color final aplicado en mapa | Debe existir en `legend.class_color_map` |
| `has_data` | boolean | Si | `true`, `false` | `true` | Disponibilidad de datos para clasificar | Debe ser `false` si falta cualquiera de los campos necesarios |
| `is_in_inset` | boolean | Si | `true`, `false` | `false` | Marca para inclusion visual en inset | No nulo |

### Reglas de negocio obligatorias

1. `has_data=false` cuando falte cualquiera de: `pct_pan_2018`, `pct_pan_2021`, `delta_pan_pp`.
2. Si `has_data=false` entonces:
- `vote_share_bin="no_data"`
- `delta_bin="no_data"`
- `bivariate_class="no_data"`
3. `bivariate_class` debe estar en el conjunto cerrado permitido.
4. `color_hex` debe resolverse por mapping de configuracion (`editorial-map-spec.json`), no por if/else hardcodeado.
5. Geometria debe ser valida y de tipo `Polygon` o `MultiPolygon`.

### Estructura minima sugerida (ejemplo)

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "schema_version": "1.0.0",
        "section_id": "110200123",
        "municipio": "Leon",
        "distrito_local": "D-06",
        "pct_pan_2018": 48.37,
        "pct_pan_2021": 56.12,
        "delta_pan_pp": 7.75,
        "vote_share_bin": "mid",
        "delta_bin": "stable",
        "bivariate_class": "stable_mid",
        "color_hex": "#615CFF",
        "has_data": true,
        "is_in_inset": false
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-101.0, 21.0], [-101.0, 21.1], [-101.1, 21.1], [-101.0, 21.0]]]
      }
    }
  ]
}
```

## C) `contexto.geojson`

### Metadata del artefacto

| Atributo | Definicion |
|---|---|
| Nombre de archivo | `contexto.geojson` |
| Proposito | Capas cartograficas de apoyo visual (region, limites, anclajes de etiqueta) |
| Formato | GeoJSON (`FeatureCollection`) |
| CRS esperado | `EPSG:4326` obligatorio |
| Geometria esperada | Segun `context_type` y `visual_role` |
| Version de esquema | `1.0.0` |

### Campos obligatorios por feature (`properties`)

| Campo | Tipo | Req | Valores permitidos | Ejemplo | Regla semantica | Regla de validacion |
|---|---|---|---|---|---|---|
| `schema_version` | string | Si | `1.0.0` | `"1.0.0"` | Version del esquema de feature | Debe coincidir con artefacto |
| `context_id` | string | Si | id unico | `"ctx_leon_boundary"` | Identificador de feature de contexto | Unico dentro del archivo |
| `context_type` | string | Si | `municipal_area`, `regional_area`, `boundary_line`, `label_anchor` | `"boundary_line"` | Tipo semantico de contexto | Debe corresponder a tipo de geometria |
| `label` | string/null | Si | texto o null | `"Silao"` | Texto de etiqueta si aplica | Si `context_type=label_anchor`, no debe ser null |
| `visual_role` | string | Si | `muted_fill`, `outline`, `label`, `inset_mask`, `reference_line` | `"outline"` | Rol visual editorial | Debe ser uno del conjunto permitido |

### Regla de geometria por `context_type`

| `context_type` | Geometria permitida |
|---|---|
| `municipal_area` | `Polygon` o `MultiPolygon` |
| `regional_area` | `Polygon` o `MultiPolygon` |
| `boundary_line` | `LineString` |
| `label_anchor` | `Point` |

Regla:

- Si el tipo de geometria no coincide con su `context_type`, la feature no pasa validacion.

## Checklist minimo de validacion del contrato

- Todos los artefactos incluyen `schema_version=1.0.0`.
- `secciones.geojson` en `EPSG:4326`, geometria valida `Polygon/MultiPolygon`.
- `has_data` y convencion `no_data` consistentes en todas las features.
- `bivariate_class` solo usa valores permitidos cerrados.
- `color_hex` coincide con `legend.class_color_map`.
- `contexto.geojson` cumple geometria permitida por `context_type`.
