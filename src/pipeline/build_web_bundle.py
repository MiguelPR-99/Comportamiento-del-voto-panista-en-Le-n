from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
PUBLIC_DIR = ROOT / "public"
PUBLIC_DATA_DIR = PUBLIC_DIR / "data"
PUBLIC_CONFIG_DIR = PUBLIC_DIR / "config"
REPORT_DIR = ROOT / "reports" / "data_qa"
DOCS_DIR = ROOT / "docs"

IN_METRICS_GEOJSON = INTERIM_DIR / "leon_electoral_metrics.geojson"
IN_METRICS_CSV = INTERIM_DIR / "leon_electoral_metrics.csv"
IN_CONTRACT_DOC = DOCS_DIR / "07-data-contract.md"
IN_BIVARIATE_DOC = DOCS_DIR / "08-bivariate-classification.md"
IN_EPIC_23_REPORT = REPORT_DIR / "electoral_metrics_report.json"

OUT_PROCESSED_SECCIONES = PROCESSED_DIR / "secciones_leon_bivariate.geojson"
OUT_PROCESSED_SPEC = PROCESSED_DIR / "editorial-map-spec.json"
OUT_PUBLIC_SECCIONES = PUBLIC_DATA_DIR / "secciones.geojson"
OUT_PUBLIC_SPEC = PUBLIC_CONFIG_DIR / "editorial-map-spec.json"
OUT_BUNDLE_REPORT_MD = REPORT_DIR / "web_bundle_report.md"
OUT_BUNDLE_REPORT_JSON = REPORT_DIR / "web_bundle_report.json"

SCHEMA_VERSION = "1.0.0"
PROJECT_ID = "leon_pan_bivariate"

ALLOWED_BIVARIATE_CLASSES = [
    "decline_low",
    "decline_mid",
    "decline_high",
    "stable_low",
    "stable_mid",
    "stable_high",
    "growth_low",
    "growth_mid",
    "growth_high",
    "no_data",
]

CLASS_COLOR_MAP = {
    "decline_low": "#F4C3DA",
    "decline_mid": "#D98DBF",
    "decline_high": "#B95C9E",
    "stable_low": "#C8C5EA",
    "stable_mid": "#9C90D4",
    "stable_high": "#6F67C3",
    "growth_low": "#9EC8EA",
    "growth_mid": "#669DD8",
    "growth_high": "#2F62B8",
    "no_data": "#CFCFCF",
}

REQUIRED_PROPERTIES = [
    "schema_version",
    "section_id",
    "entidad",
    "municipio",
    "municipio_nombre",
    "distrito_local",
    "seccion",
    "pan_2018_votos",
    "pan_2021_votos",
    "total_2018",
    "total_2021",
    "pct_pan_2018",
    "pct_pan_2021",
    "delta_pan_pp",
    "vote_share_bin",
    "delta_bin",
    "bivariate_class",
    "color_hex",
    "has_data",
    "is_in_inset",
    "issue_type",
]

EXPECTED_FEATURES = 846
EXPECTED_NO_DATA = 149


def normalize_section_id(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().replace(",", "")
    if text == "":
        return None
    if text.endswith(".0"):
        text = text[:-2]
    return text


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "si"}


def ensure_directories() -> None:
    for directory in [PROCESSED_DIR, PUBLIC_DIR, PUBLIC_DATA_DIR, PUBLIC_CONFIG_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def read_required_docs() -> list[str]:
    warnings: list[str] = []
    contract_text = IN_CONTRACT_DOC.read_text(encoding="utf-8")
    bivariate_text = IN_BIVARIATE_DOC.read_text(encoding="utf-8")

    if "EPSG:4326" not in contract_text:
        warnings.append("No se detecto token EPSG:4326 en docs/07-data-contract.md.")
    if "decline_low" not in bivariate_text or "growth_high" not in bivariate_text:
        warnings.append("No se detecto dominio bivariante completo en docs/08-bivariate-classification.md.")
    return warnings


def compute_bins_and_class(row: pd.Series) -> tuple[str, str, str]:
    has_data = bool(row["has_data"])
    if not has_data:
        return "no_data", "no_data", "no_data"

    pct = row["pct_pan_2021"]
    delta = row["delta_pan_pp"]
    if pd.isna(pct) or pd.isna(delta):
        return "no_data", "no_data", "no_data"

    if pct < 40:
        vote_share_bin = "low"
    elif pct < 60:
        vote_share_bin = "mid"
    else:
        vote_share_bin = "high"

    if delta < -10:
        delta_bin = "decline"
    elif delta <= 10:
        delta_bin = "stable"
    else:
        delta_bin = "growth"

    return vote_share_bin, delta_bin, f"{delta_bin}_{vote_share_bin}"


def build_issue_type(row: pd.Series) -> str:
    if bool(row["has_data"]):
        return "none"

    missing_2018 = any(pd.isna(row[col]) for col in ["pan_2018_votos", "total_2018", "pct_pan_2018"])
    missing_2021 = any(pd.isna(row[col]) for col in ["pan_2021_votos", "total_2021", "pct_pan_2021"])
    if missing_2018 and missing_2021:
        return "missing_both"
    if missing_2018:
        return "missing_2018"
    if missing_2021:
        return "missing_2021"
    return "other_missing"


def validate_contract_properties(gdf: gpd.GeoDataFrame) -> dict[str, Any]:
    props = [c for c in gdf.columns if c != "geometry"]
    required_set = set(REQUIRED_PROPERTIES)
    props_set = set(props)
    return {
        "required_fields_present": required_set.issubset(props_set),
        "unexpected_fields_present": sorted(props_set - required_set),
        "missing_fields": sorted(required_set - props_set),
        "ordered_fields_match": props == REQUIRED_PROPERTIES,
    }


def looks_like_wgs84_bounds(bounds: tuple[float, float, float, float]) -> bool:
    minx, miny, maxx, maxy = bounds
    return minx >= -180 and maxx <= 180 and miny >= -90 and maxy <= 90


def load_and_build_web_layer() -> tuple[gpd.GeoDataFrame, dict[str, Any], list[str]]:
    warnings: list[str] = []
    gdf = gpd.read_file(IN_METRICS_GEOJSON)
    df = pd.read_csv(IN_METRICS_CSV)

    for frame in [gdf, df]:
        if "section_id" not in frame.columns:
            raise RuntimeError("section_id es obligatorio en entradas de Epica 2.3.")
        frame["section_id"] = frame["section_id"].map(normalize_section_id)

    for col in ["entidad", "municipio", "seccion"]:
        if col in gdf.columns:
            gdf[f"{col}_base"] = gdf[col]

    merged = gdf[["section_id", "entidad_base", "municipio_base", "seccion_base", "geometry"]].merge(
        df, on="section_id", how="left", validate="one_to_one"
    )

    merged["entidad"] = merged["entidad"].combine_first(merged["entidad_base"])
    merged["municipio"] = merged["municipio"].combine_first(merged["municipio_base"])
    merged["seccion"] = merged["seccion"].combine_first(merged["seccion_base"])
    merged = merged.drop(columns=["entidad_base", "municipio_base", "seccion_base"])

    for col in ["pan_2018_votos", "pan_2021_votos", "total_2018", "total_2021", "pct_pan_2018", "pct_pan_2021", "delta_pan_pp"]:
        if col not in merged.columns:
            merged[col] = pd.NA
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    required_has_data = [
        "pan_2018_votos",
        "pan_2021_votos",
        "total_2018",
        "total_2021",
        "pct_pan_2018",
        "pct_pan_2021",
        "delta_pan_pp",
    ]
    merged["has_data"] = merged[required_has_data].notna().all(axis=1)
    merged["issue_type"] = merged.apply(build_issue_type, axis=1)

    bins = merged.apply(compute_bins_and_class, axis=1, result_type="expand")
    merged["vote_share_bin"] = bins[0]
    merged["delta_bin"] = bins[1]
    merged["bivariate_class"] = bins[2]

    merged["color_hex"] = merged["bivariate_class"].map(CLASS_COLOR_MAP)
    merged["schema_version"] = SCHEMA_VERSION
    merged["is_in_inset"] = False
    warnings.append("is_in_inset se asigno en false por defecto; no existe geometria formal de inset en esta fase.")

    if "municipio_nombre" not in merged.columns:
        merged["municipio_nombre"] = "LEON"

    if "distrito_local" not in merged.columns:
        merged["distrito_local"] = pd.NA

    for col in REQUIRED_PROPERTIES:
        if col not in merged.columns:
            merged[col] = pd.NA

    for col in REQUIRED_PROPERTIES:
        if col not in {"has_data", "is_in_inset"}:
            merged[col] = merged[col].replace("", pd.NA)

    out_gdf = gpd.GeoDataFrame(merged[REQUIRED_PROPERTIES + ["geometry"]], geometry="geometry", crs=gdf.crs)

    source_crs = out_gdf.crs
    bounds = tuple(float(x) for x in out_gdf.total_bounds)
    if out_gdf.crs is None:
        if looks_like_wgs84_bounds(bounds):
            out_gdf = out_gdf.set_crs(epsg=4326, allow_override=True)
            warnings.append("CRS sin metadata: se asumio EPSG:4326 por rango de coordenadas.")
        else:
            try:
                out_gdf = out_gdf.set_crs(epsg=32614, allow_override=True).to_crs(epsg=4326)
                warnings.append("CRS sin metadata: se asumio EPSG:32614 por rango de coordenadas y se reproyecto a EPSG:4326.")
            except Exception:
                warnings.append("No fue posible confirmar/reproyectar CRS a EPSG:4326; se conserva geometria original.")
    else:
        epsg = out_gdf.crs.to_epsg()
        if epsg == 4326 and not looks_like_wgs84_bounds(bounds):
            try:
                out_gdf = out_gdf.set_crs(epsg=32614, allow_override=True).to_crs(epsg=4326)
                warnings.append("CRS indicaba EPSG:4326 pero coordenadas no estaban en rango geodesico; se corrigio asumiendo EPSG:32614.")
            except Exception:
                warnings.append("CRS de entrada inconsistente y no fue posible corregir a EPSG:4326.")
        elif epsg != 4326:
            try:
                out_gdf = out_gdf.to_crs(epsg=4326)
                warnings.append(f"Geometria reproyectada a EPSG:4326 desde CRS fuente {source_crs}.")
            except Exception:
                warnings.append("Fallo la reproyeccion a EPSG:4326; se conserva CRS original.")

    out_gdf = out_gdf.sort_values(
        by="section_id",
        key=lambda s: pd.to_numeric(s, errors="coerce"),
    ).reset_index(drop=True)

    class_counts = {cls: int((out_gdf["bivariate_class"] == cls).sum()) for cls in ALLOWED_BIVARIATE_CLASSES}
    return out_gdf, class_counts, warnings


def build_editorial_spec(gdf: gpd.GeoDataFrame, class_counts: dict[str, int], warnings: list[str], qa_summary: dict[str, Any]) -> dict[str, Any]:
    minx, miny, maxx, maxy = gdf.total_bounds
    center = [round((minx + maxx) / 2, 6), round((miny + maxy) / 2, 6)]
    spec = {
        "schema_version": SCHEMA_VERSION,
        "project_id": PROJECT_ID,
        "title": "Comportamiento del voto panista en Leon",
        "subtitle": "Variacion del voto PAN entre 2018 y 2021 por seccion electoral",
        "source_lines": [
            "Fuentes: INE (cartografia seccional), IEEG (resultados de diputaciones 2018 y 2021), INEGI (referencia territorial)."
        ],
        "author_note": "Elaboracion editorial para pieza interactiva. No se imputan ceros para resolver faltantes electorales.",
        "palette": {
            "family": "violeta_azul_rosa",
            "class_color_map": CLASS_COLOR_MAP,
            "neutral_no_data": CLASS_COLOR_MAP["no_data"],
        },
        "class_color_map": CLASS_COLOR_MAP,
        "legend": {
            "type": "bivariate_3x3",
            "x_axis_label": "Porcentaje de voto PAN 2021",
            "y_axis_label": "Variacion respecto a 2018 (pp)",
            "bins": {
                "vote_share_bin": {"low": "<40", "mid": "40-<60", "high": ">=60"},
                "delta_bin": {"decline": "<-10", "stable": "-10 a 10", "growth": ">10"},
            },
            "matrix": {
                "rows": ["growth", "stable", "decline"],
                "cols": ["low", "mid", "high"],
                "class_grid": [
                    ["growth_low", "growth_mid", "growth_high"],
                    ["stable_low", "stable_mid", "stable_high"],
                    ["decline_low", "decline_mid", "decline_high"],
                ],
            },
            "class_counts": class_counts,
            "include_no_data": True,
        },
        "main_view": {
            "layout": "desktop-first",
            "center": center,
            "zoom": 10.1,
            "bounds": [round(minx, 6), round(miny, 6), round(maxx, 6), round(maxy, 6)],
        },
        "inset_view": {
            "layout": "desktop-first",
            "center": center,
            "zoom": 11.7,
            "enabled": False,
            "notes": "Inset formal pendiente de definicion geometrica.",
        },
        "scale_bar_km": 3,
        "no_data_style": {
            "fill": CLASS_COLOR_MAP["no_data"],
            "hatch": "diagonal",
            "stroke": "#8F8F8F",
        },
        "interaction_policy": {
            "layout": "desktop-first",
            "mode": "replica fiel + microinteracciones",
            "allow_hover": True,
            "allow_click": True,
            "allow_scroll_zoom": False,
            "allow_filters": False,
            "allow_tabs": False,
            "allow_sidebar_metrics": False,
        },
        "data_files": {"secciones": "/data/secciones.geojson"},
        "qa_summary": qa_summary,
        "warnings": warnings,
    }
    return spec


def build_report(
    gdf: gpd.GeoDataFrame,
    class_counts: dict[str, int],
    contract_validation: dict[str, Any],
    warnings: list[str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    duplicate_section_ids = int(gdf["section_id"].duplicated().sum())
    allowed_set = set(ALLOWED_BIVARIATE_CLASSES)
    invalid_classes = int((~gdf["bivariate_class"].isin(allowed_set)).sum())
    has_data_false = int((gdf["has_data"] == False).sum())  # noqa: E712
    no_data_count = int((gdf["bivariate_class"] == "no_data").sum())
    inconsistent_no_data = int(
        (
            ((gdf["has_data"] == False) & (gdf["bivariate_class"] != "no_data"))  # noqa: E712
            | ((gdf["has_data"] == True) & (gdf["bivariate_class"] == "no_data"))  # noqa: E712
        ).sum()
    )
    missing_color = int(gdf["color_hex"].isna().sum())
    color_outside_map = int((~gdf["color_hex"].isin(set(CLASS_COLOR_MAP.values()))).sum())

    payload_bytes = OUT_PUBLIC_SECCIONES.stat().st_size + OUT_PUBLIC_SPEC.stat().st_size
    payload_mb = round(payload_bytes / (1024 * 1024), 3)

    epic23_counts_match = None
    epic23_no_data_match = None
    epic23_has_data_false_match = None
    if IN_EPIC_23_REPORT.exists():
        epic23 = json.loads(IN_EPIC_23_REPORT.read_text(encoding="utf-8"))
        epic23_counts = {k: int(v) for k, v in epic23.get("bivariate_class_counts", {}).items()}
        epic23_counts_match = all(int(class_counts.get(k, 0)) == int(v) for k, v in epic23_counts.items())
        epic23_no_data_match = no_data_count == int(epic23.get("counts", {}).get("no_data_count", -1))
        epic23_has_data_false_match = has_data_false == int(epic23.get("counts", {}).get("has_data_false", -1))

    frontend_files = []
    for ext in ["*.html", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css"]:
        frontend_files.extend(str(p.relative_to(ROOT)) for p in PUBLIC_DIR.rglob(ext))
    frontend_files = sorted(set(frontend_files))

    validations = {
        "public_data_exists": OUT_PUBLIC_SECCIONES.exists(),
        "public_config_exists": OUT_PUBLIC_SPEC.exists(),
        "feature_count": int(len(gdf)),
        "feature_count_expected_846": int(len(gdf)) == EXPECTED_FEATURES,
        "duplicate_section_ids": duplicate_section_ids,
        "all_classes_in_domain": invalid_classes == 0,
        "class_counts_match_epic_2_3": epic23_counts_match,
        "no_data_count": no_data_count,
        "no_data_expected_149": no_data_count == EXPECTED_NO_DATA,
        "has_data_false_count": has_data_false,
        "has_data_false_expected_149": has_data_false == EXPECTED_NO_DATA,
        "has_data_no_data_inconsistency": inconsistent_no_data,
        "all_colors_present": missing_color == 0,
        "all_colors_in_class_map": color_outside_map == 0,
        "contract_required_fields": bool(contract_validation["required_fields_present"]),
        "contract_no_missing_fields": len(contract_validation["missing_fields"]) == 0,
        "contract_no_unexpected_fields": len(contract_validation["unexpected_fields_present"]) == 0,
        "frontend_files_in_public": frontend_files,
    }

    if epic23_no_data_match is not None:
        validations["no_data_matches_epic_2_3_report"] = epic23_no_data_match
    if epic23_has_data_false_match is not None:
        validations["has_data_false_matches_epic_2_3_report"] = epic23_has_data_false_match

    if frontend_files:
        warnings.append("Se detectaron posibles artefactos de frontend en public/; revisar en Epica 3.")

    pending_frontend = [
        "Definir geometria y posicion final de inset urbano (is_in_inset).",
        "Implementar render MapLibre y microinteracciones editoriales.",
        "Aplicar jerarquia tipografica final y composicion visual de la leyenda 3x3.",
    ]

    approved = (
        validations["public_data_exists"]
        and validations["public_config_exists"]
        and validations["feature_count_expected_846"]
        and validations["duplicate_section_ids"] == 0
        and validations["all_classes_in_domain"]
        and validations["no_data_expected_149"]
        and validations["has_data_false_expected_149"]
        and validations["has_data_no_data_inconsistency"] == 0
        and validations["all_colors_present"]
        and validations["all_colors_in_class_map"]
        and validations["contract_required_fields"]
        and validations["contract_no_missing_fields"]
        and validations["contract_no_unexpected_fields"]
    )
    decision = "aprobado para Epica 3" if approved else "no aprobado para Epica 3"

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "outputs": [
            str(OUT_PROCESSED_SECCIONES.relative_to(ROOT)),
            str(OUT_PROCESSED_SPEC.relative_to(ROOT)),
            str(OUT_PUBLIC_SECCIONES.relative_to(ROOT)),
            str(OUT_PUBLIC_SPEC.relative_to(ROOT)),
            str(OUT_BUNDLE_REPORT_MD.relative_to(ROOT)),
            str(OUT_BUNDLE_REPORT_JSON.relative_to(ROOT)),
        ],
        "counts": {
            "features": int(len(gdf)),
            "class_counts": class_counts,
            "no_data_count": no_data_count,
            "has_data_false_count": has_data_false,
        },
        "payload": {
            "bytes": payload_bytes,
            "mb": payload_mb,
            "public_data_geojson_bytes": OUT_PUBLIC_SECCIONES.stat().st_size,
            "public_spec_json_bytes": OUT_PUBLIC_SPEC.stat().st_size,
        },
        "contract_validation": contract_validation,
        "qa_validations": validations,
        "warnings": warnings,
        "pending_frontend": pending_frontend,
        "spec_summary": {
            "project_id": spec["project_id"],
            "title": spec["title"],
            "subtitle": spec["subtitle"],
            "interaction_policy": spec["interaction_policy"]["mode"],
            "data_files": spec["data_files"],
        },
        "decision": decision,
    }
    return report


def write_markdown_report(report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Web Bundle Report")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append("")
    lines.append(f"- Fecha: `{report['generated_at']}`")
    lines.append(f"- Veredicto: `{report['decision']}`")
    lines.append("")
    lines.append("## Archivos Generados")
    lines.append("")
    for path in report["outputs"]:
        lines.append(f"- `{path}`")
    lines.append("")
    lines.append("## Conteos Finales")
    lines.append("")
    lines.append(f"- features: `{report['counts']['features']}`")
    lines.append(f"- no_data_count: `{report['counts']['no_data_count']}`")
    lines.append(f"- has_data_false_count: `{report['counts']['has_data_false_count']}`")
    lines.append("")
    lines.append("## Conteo Por Clase Bivariante")
    lines.append("")
    for key, value in report["counts"]["class_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Payload")
    lines.append("")
    lines.append(f"- total_mb: `{report['payload']['mb']}`")
    lines.append(f"- public/data/secciones.geojson bytes: `{report['payload']['public_data_geojson_bytes']}`")
    lines.append(f"- public/config/editorial-map-spec.json bytes: `{report['payload']['public_spec_json_bytes']}`")
    lines.append("")
    lines.append("## Validacion De Contrato")
    lines.append("")
    lines.append(f"- required_fields_present: `{report['contract_validation']['required_fields_present']}`")
    lines.append(f"- missing_fields: `{report['contract_validation']['missing_fields']}`")
    lines.append(f"- unexpected_fields_present: `{report['contract_validation']['unexpected_fields_present']}`")
    lines.append("")
    lines.append("## QA")
    lines.append("")
    for key, value in report["qa_validations"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Pendientes Para Frontend")
    lines.append("")
    for item in report["pending_frontend"]:
        lines.append(f"- {item}")
    lines.append("")

    OUT_BUNDLE_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_directories()
    warnings = read_required_docs()

    gdf, class_counts, build_warnings = load_and_build_web_layer()
    warnings.extend(build_warnings)

    # Guardado de capa procesada y copia directa a public.
    gdf.to_file(OUT_PROCESSED_SECCIONES, driver="GeoJSON")
    shutil.copy2(OUT_PROCESSED_SECCIONES, OUT_PUBLIC_SECCIONES)

    contract_validation = validate_contract_properties(gdf)
    qa_summary = {
        "feature_count": int(len(gdf)),
        "class_counts": class_counts,
        "contract_validation": contract_validation,
        "warnings_count": len(warnings),
    }
    spec = build_editorial_spec(gdf, class_counts, warnings, qa_summary)
    OUT_PROCESSED_SPEC.write_text(json.dumps(spec, ensure_ascii=True, indent=2), encoding="utf-8")
    shutil.copy2(OUT_PROCESSED_SPEC, OUT_PUBLIC_SPEC)

    report = build_report(gdf, class_counts, contract_validation, warnings, spec)
    OUT_BUNDLE_REPORT_JSON.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    write_markdown_report(report)

    print(f"[build-web-bundle] Generated: {OUT_PROCESSED_SECCIONES}")
    print(f"[build-web-bundle] Generated: {OUT_PROCESSED_SPEC}")
    print(f"[build-web-bundle] Generated: {OUT_PUBLIC_SECCIONES}")
    print(f"[build-web-bundle] Generated: {OUT_PUBLIC_SPEC}")
    print(f"[build-web-bundle] Report: {OUT_BUNDLE_REPORT_MD}")
    print(f"[build-web-bundle] Report: {OUT_BUNDLE_REPORT_JSON}")
    print(f"[build-web-bundle] Decision: {report['decision']}")


if __name__ == "__main__":
    main()
