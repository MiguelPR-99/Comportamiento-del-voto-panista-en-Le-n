from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = ROOT / "data" / "interim"
REPORT_DIR = ROOT / "reports" / "data_qa"

IN_INE_GEOJSON = INTERIM_DIR / "ine_secciones_leon.geojson"
IN_EDMSLM = INTERIM_DIR / "edmslm_leon.csv"
IN_2018 = INTERIM_DIR / "ieeg_2018_diputaciones_seccion.csv"
IN_2021 = INTERIM_DIR / "ieeg_2021_diputaciones_seccion.csv"

OUT_METRICS_CSV = INTERIM_DIR / "leon_electoral_metrics.csv"
OUT_METRICS_GEOJSON = INTERIM_DIR / "leon_electoral_metrics.geojson"
OUT_REPORT_MD = REPORT_DIR / "electoral_metrics_report.md"
OUT_REPORT_JSON = REPORT_DIR / "electoral_metrics_report.json"

ALLOWED_BIVARIATE_CLASSES = {
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
}


def normalize_digits(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    text = text.replace(",", "")
    if re.fullmatch(r"[-+]?\d+(\.0+)?", text):
        return str(int(float(text)))
    match = re.search(r"\d+", text)
    if not match:
        return None
    return str(int(match.group(0)))


def normalize_entidad(value: Any) -> str | None:
    code = normalize_digits(value)
    if not code:
        return None
    return code.zfill(2)


def normalize_municipio(value: Any) -> str | None:
    code = normalize_digits(value)
    if not code:
        return None
    return code.zfill(3)


def normalize_seccion(value: Any) -> str | None:
    code = normalize_digits(value)
    if not code:
        return None
    return code.lstrip("0") or "0"


def normalize_section_id(value: Any) -> str | None:
    code = normalize_digits(value)
    if not code:
        return None
    return code


def load_geo_base(path: Path) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    gdf = gpd.read_file(path)
    required = ["entidad", "municipio", "seccion", "section_id"]
    for col in required:
        if col not in gdf.columns:
            raise RuntimeError(f"Base geometry missing required column: {col}")
    gdf["entidad"] = gdf["entidad"].map(normalize_entidad)
    gdf["municipio"] = gdf["municipio"].map(normalize_municipio)
    gdf["seccion"] = gdf["seccion"].map(normalize_seccion)
    gdf["section_id"] = gdf["section_id"].map(normalize_section_id)
    if gdf["section_id"].isna().any():
        raise RuntimeError("Base geometry has null section_id values.")
    return gdf


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    df = pd.read_csv(path, dtype="string")
    if "section_id" not in df.columns:
        raise RuntimeError(f"{path.name} missing required section_id column.")
    if "entidad" in df.columns:
        df["entidad"] = df["entidad"].map(normalize_entidad)
    if "municipio" in df.columns:
        df["municipio"] = df["municipio"].map(normalize_municipio)
    if "seccion" in df.columns:
        df["seccion"] = df["seccion"].map(normalize_seccion)
    df["section_id"] = df["section_id"].map(normalize_section_id)
    return df


def as_numeric(df: pd.DataFrame, columns: list[str]) -> None:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def vote_share_bin(value: float | None) -> str | None:
    if value is None or pd.isna(value):
        return None
    if value < 40:
        return "low"
    if value < 60:
        return "mid"
    return "high"


def delta_bin(value: float | None) -> str | None:
    if value is None or pd.isna(value):
        return None
    if value < -10:
        return "decline"
    if value <= 10:
        return "stable"
    return "growth"


def classify_issue_type(row: pd.Series) -> str:
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


def build_report_json(gdf: gpd.GeoDataFrame, geometry_preserved: bool) -> dict[str, Any]:
    class_counts = {
        str(key): int(value)
        for key, value in Counter(gdf["bivariate_class"].fillna("null")).items()
    }
    issue_counts = {
        str(key): int(value)
        for key, value in Counter(gdf["issue_type"].fillna("null")).items()
    }

    duplicate_section_ids = int(gdf["section_id"].duplicated().sum())
    pct_2018_out = int(gdf.loc[gdf["pct_pan_2018"].notna() & ~gdf["pct_pan_2018"].between(0, 100)].shape[0])
    pct_2021_out = int(gdf.loc[gdf["pct_pan_2021"].notna() & ~gdf["pct_pan_2021"].between(0, 100)].shape[0])
    delta_out = int(gdf.loc[gdf["delta_pan_pp"].notna() & ~gdf["delta_pan_pp"].between(-100, 100)].shape[0])
    invalid_class = int((~gdf["bivariate_class"].isin(ALLOWED_BIVARIATE_CLASSES)).sum())

    inconsistent = int(
        (
            ((~gdf["has_data"]) & ((gdf["vote_share_bin"] != "no_data") | (gdf["delta_bin"] != "no_data") | (gdf["bivariate_class"] != "no_data")))
            | ((gdf["has_data"]) & ((gdf["vote_share_bin"] == "no_data") | (gdf["delta_bin"] == "no_data") | (gdf["bivariate_class"] == "no_data")))
        ).sum()
    )

    warnings: list[str] = []
    if issue_counts.get("missing_2018", 0) > 0:
        warnings.append(f"{issue_counts['missing_2018']} section_id with missing 2018 metrics.")
    if issue_counts.get("missing_2021", 0) > 0:
        warnings.append(f"{issue_counts['missing_2021']} section_id with missing 2021 metrics.")
    if issue_counts.get("missing_both", 0) > 0:
        warnings.append(f"{issue_counts['missing_both']} section_id with missing 2018 and 2021 metrics.")
    if issue_counts.get("other_missing", 0) > 0:
        warnings.append(f"{issue_counts['other_missing']} section_id with other missing required values.")
    if duplicate_section_ids > 0:
        warnings.append("Duplicate section_id detected in final output.")
    if invalid_class > 0:
        warnings.append("Found bivariate_class values outside allowed domain.")

    validations = {
        "duplicate_section_ids": duplicate_section_ids,
        "pct_pan_2018_out_of_range": pct_2018_out,
        "pct_pan_2021_out_of_range": pct_2021_out,
        "delta_pan_pp_out_of_range": delta_out,
        "invalid_bivariate_class": invalid_class,
        "has_data_no_data_inconsistency": inconsistent,
        "geometry_preserved": geometry_preserved,
    }

    approved = (
        validations["duplicate_section_ids"] == 0
        and validations["pct_pan_2018_out_of_range"] == 0
        and validations["pct_pan_2021_out_of_range"] == 0
        and validations["delta_pan_pp_out_of_range"] == 0
        and validations["invalid_bivariate_class"] == 0
        and validations["has_data_no_data_inconsistency"] == 0
        and geometry_preserved
    )
    decision = "aprobado para Epica 2.4" if approved else "no aprobado para Epica 2.4"

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "inputs": [
            str(IN_INE_GEOJSON.relative_to(ROOT)),
            str(IN_EDMSLM.relative_to(ROOT)),
            str(IN_2018.relative_to(ROOT)),
            str(IN_2021.relative_to(ROOT)),
        ],
        "outputs": [
            str(OUT_METRICS_CSV.relative_to(ROOT)),
            str(OUT_METRICS_GEOJSON.relative_to(ROOT)),
            str(OUT_REPORT_MD.relative_to(ROOT)),
            str(OUT_REPORT_JSON.relative_to(ROOT)),
        ],
        "section_id_formula": "section_id = entidad(2) + municipio(3) + seccion(normalizada sin decimales)",
        "counts": {
            "sections_total": int(len(gdf)),
            "has_data_true": int((gdf["has_data"] == True).sum()),  # noqa: E712
            "has_data_false": int((gdf["has_data"] == False).sum()),  # noqa: E712
            "no_data_count": int((gdf["bivariate_class"] == "no_data").sum()),
        },
        "bivariate_class_counts": dict(sorted(class_counts.items())),
        "issue_type_counts": dict(sorted(issue_counts.items())),
        "secciones_sin_match": {
            "total_with_issues": int((gdf["issue_type"] != "none").sum()),
            "sample_section_ids": [str(x) for x in gdf.loc[gdf["issue_type"] != "none", "section_id"].head(30).tolist()],
        },
        "totals": {
            "pan_2018_total": float(gdf["pan_2018_votos"].sum(skipna=True)),
            "total_2018_total": float(gdf["total_2018"].sum(skipna=True)),
            "pan_2021_total": float(gdf["pan_2021_votos"].sum(skipna=True)),
            "total_2021_total": float(gdf["total_2021"].sum(skipna=True)),
        },
        "validations": validations,
        "warnings": warnings,
        "decision": decision,
    }
    return report


def write_markdown_report(report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Electoral Metrics Report")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append("")
    lines.append(f"- Fecha: `{report['generated_at']}`")
    lines.append(f"- Veredicto: `{report['decision']}`")
    lines.append(f"- Secciones analizadas: `{report['counts']['sections_total']}`")
    lines.append("")
    lines.append("## Conteos")
    lines.append("")
    lines.append(f"- has_data=true: `{report['counts']['has_data_true']}`")
    lines.append(f"- has_data=false: `{report['counts']['has_data_false']}`")
    lines.append(f"- bivariate_class=no_data: `{report['counts']['no_data_count']}`")
    lines.append("")
    lines.append("## Conteo por bivariate_class")
    lines.append("")
    for key, value in report["bivariate_class_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Secciones sin Match")
    lines.append("")
    lines.append(f"- total_with_issues: `{report['secciones_sin_match']['total_with_issues']}`")
    lines.append(f"- sample_section_ids: `{', '.join(report['secciones_sin_match']['sample_section_ids'])}`")
    lines.append("")
    lines.append("## Totales Electorales")
    lines.append("")
    lines.append(f"- PAN 2018 total: `{int(report['totals']['pan_2018_total'])}`")
    lines.append(f"- Total votos 2018: `{int(report['totals']['total_2018_total'])}`")
    lines.append(f"- PAN 2021 total: `{int(report['totals']['pan_2021_total'])}`")
    lines.append(f"- Total votos 2021: `{int(report['totals']['total_2021_total'])}`")
    lines.append("")
    lines.append("## Validaciones")
    lines.append("")
    for key, value in report["validations"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Advertencias")
    lines.append("")
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Archivos Generados")
    lines.append("")
    for path in report["outputs"]:
        lines.append(f"- `{path}`")
    lines.append("")

    OUT_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def build_metrics() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    base_gdf = load_geo_base(IN_INE_GEOJSON)
    input_feature_count = len(base_gdf)

    edmslm_df = load_csv(IN_EDMSLM)
    y2018_df = load_csv(IN_2018)
    y2021_df = load_csv(IN_2021)

    as_numeric(y2018_df, ["pan_2018_votos", "total_2018", "pct_pan_2018", "source_rows_2018"])
    as_numeric(y2021_df, ["pan_2021_votos", "total_2021", "pct_pan_2021", "source_rows_2021"])

    edmslm_cols = [c for c in ["section_id", "municipio_nombre", "distrito_local", "distrito_federal"] if c in edmslm_df.columns]
    y2018_cols = [c for c in ["section_id", "pan_2018_votos", "total_2018", "pct_pan_2018", "source_rows_2018"] if c in y2018_df.columns]
    y2021_cols = [c for c in ["section_id", "pan_2021_votos", "total_2021", "pct_pan_2021", "source_rows_2021"] if c in y2021_df.columns]

    merged = base_gdf.merge(edmslm_df[edmslm_cols], on="section_id", how="left")
    merged = merged.merge(y2018_df[y2018_cols], on="section_id", how="left")
    merged = merged.merge(y2021_df[y2021_cols], on="section_id", how="left")
    merged = gpd.GeoDataFrame(merged, geometry="geometry", crs=base_gdf.crs)

    for col in ["pan_2018_votos", "total_2018", "pct_pan_2018", "pan_2021_votos", "total_2021", "pct_pan_2021"]:
        if col not in merged.columns:
            merged[col] = pd.NA
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged["delta_pan_pp"] = merged["pct_pan_2021"] - merged["pct_pan_2018"]

    required = [
        "pan_2018_votos",
        "pan_2021_votos",
        "total_2018",
        "total_2021",
        "pct_pan_2018",
        "pct_pan_2021",
        "delta_pan_pp",
    ]
    merged["has_data"] = merged[required].notna().all(axis=1)
    merged["issue_type"] = merged.apply(classify_issue_type, axis=1)

    merged["vote_share_bin"] = merged["pct_pan_2021"].apply(vote_share_bin)
    merged["delta_bin"] = merged["delta_pan_pp"].apply(delta_bin)
    merged["bivariate_class"] = merged.apply(
        lambda row: f"{row['delta_bin']}_{row['vote_share_bin']}"
        if pd.notna(row["delta_bin"]) and pd.notna(row["vote_share_bin"])
        else None,
        axis=1,
    )

    no_data_mask = ~merged["has_data"]
    merged.loc[no_data_mask, "vote_share_bin"] = "no_data"
    merged.loc[no_data_mask, "delta_bin"] = "no_data"
    merged.loc[no_data_mask, "bivariate_class"] = "no_data"

    merged["_sid_sort"] = pd.to_numeric(merged["section_id"], errors="coerce")
    merged = merged.sort_values("_sid_sort").drop(columns=["_sid_sort"]).reset_index(drop=True)

    output_columns = [
        "entidad",
        "municipio",
        "seccion",
        "section_id",
        "municipio_nombre",
        "distrito_local",
        "distrito_federal",
        "pan_2018_votos",
        "pan_2021_votos",
        "total_2018",
        "total_2021",
        "pct_pan_2018",
        "pct_pan_2021",
        "delta_pan_pp",
        "has_data",
        "issue_type",
        "vote_share_bin",
        "delta_bin",
        "bivariate_class",
        "source_rows_2018",
        "source_rows_2021",
    ]
    for col in output_columns:
        if col not in merged.columns:
            merged[col] = pd.NA

    merged[output_columns].to_csv(OUT_METRICS_CSV, index=False, encoding="utf-8")

    out_gdf = merged.copy()
    for col in output_columns:
        out_gdf[col] = out_gdf[col].where(pd.notna(out_gdf[col]), None)
    out_gdf.to_file(OUT_METRICS_GEOJSON, driver="GeoJSON")

    geometry_preserved = len(out_gdf) == input_feature_count and out_gdf.geometry.notna().all()

    report = build_report_json(out_gdf, geometry_preserved=bool(geometry_preserved))
    OUT_REPORT_JSON.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    write_markdown_report(report)
    return report


def main() -> None:
    report = build_metrics()
    print(f"[build-metrics] Generated: {OUT_METRICS_CSV}")
    print(f"[build-metrics] Generated: {OUT_METRICS_GEOJSON}")
    print(f"[build-metrics] Report: {OUT_REPORT_MD}")
    print(f"[build-metrics] Report: {OUT_REPORT_JSON}")
    print(f"[build-metrics] Decision: {report['decision']}")


if __name__ == "__main__":
    main()
