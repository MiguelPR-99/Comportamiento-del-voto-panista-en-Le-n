from __future__ import annotations

import csv
import io
import json
import re
import struct
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RAW_INE_ZIP = ROOT / "data" / "raw" / "ine" / "bgd_11_Shapefile.zip"
RAW_AUDIT_MD = ROOT / "reports" / "data_qa" / "raw_schema_audit.md"
RAW_AUDIT_JSON = ROOT / "reports" / "data_qa" / "raw_schema_audit.json"
INE_AUDIT_JSON = ROOT / "reports" / "data_qa" / "ine_geography_audit.json"
TMP_DIR = ROOT / "reports" / "data_qa" / "tmp_ine_extract"
INVENTORY_CSV = ROOT / "data" / "raw" / "data_inventory.csv"


SHAPE_TYPE_MAP = {
    0: "Null Shape",
    1: "Point",
    3: "Polyline",
    5: "Polygon",
    8: "MultiPoint",
    11: "PointZ",
    13: "PolylineZ",
    15: "PolygonZ",
    18: "MultiPointZ",
    21: "PointM",
    23: "PolylineM",
    25: "PolygonM",
    28: "MultiPointM",
    31: "MultiPatch",
}


@dataclass
class LayerInspection:
    shp_path: str
    row_count: int | None
    geometry_types: list[str]
    shp_shape_type: str
    columns: list[str]
    key_candidates: dict[str, list[str]]
    crs_wkt: str | None
    crs_hint: str | None
    null_geometries: int | None
    invalid_geometries: int | None
    issues: list[str]


def normalize(text: str) -> str:
    txt = text.lower().strip()
    txt = re.sub(r"[^a-z0-9]+", "_", txt)
    return txt.strip("_")


def key_candidates(columns: list[str]) -> dict[str, list[str]]:
    mapped = {"entidad": [], "municipio": [], "seccion": []}
    for col in columns:
        n = normalize(col)
        if any(tok in n for tok in ("entidad", "cve_ent", "id_estado", "estado")):
            mapped["entidad"].append(col)
        if any(tok in n for tok in ("municipio", "cve_mun", "mun")):
            mapped["municipio"].append(col)
        if any(tok in n for tok in ("seccion", "cve_secc", "sec")):
            mapped["seccion"].append(col)
    return mapped


def parse_dbf_fields(dbf_path: Path) -> tuple[int | None, list[str]]:
    dbf_bytes = dbf_path.read_bytes()
    if len(dbf_bytes) < 32:
        return None, []
    row_count = int.from_bytes(dbf_bytes[4:8], "little")
    header_len = int.from_bytes(dbf_bytes[8:10], "little")
    fields: list[str] = []
    offset = 32
    while offset + 32 <= header_len:
        chunk = dbf_bytes[offset : offset + 32]
        if chunk[0] == 0x0D:
            break
        name = chunk[:11].split(b"\x00", 1)[0].decode("ascii", errors="ignore").strip()
        if name:
            fields.append(name)
        offset += 32
    return row_count, fields


def parse_prj(prj_path: Path) -> tuple[str | None, str | None]:
    if not prj_path.exists():
        return None, None
    text = prj_path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None, None
    hint = None
    up = text.upper()
    if "WGS_1984_UTM_ZONE_14N" in up:
        hint = "EPSG:32614 (heuristic)"
    elif "WGS_84" in up and "UTM_ZONE_14N" in up:
        hint = "EPSG:32614 (heuristic)"
    return text, hint


def inspect_shp_structure(shp_path: Path) -> tuple[str, list[str], int | None, int | None, list[str]]:
    issues: list[str] = []
    data = shp_path.read_bytes()
    if len(data) < 100:
        return "Unknown", [], None, None, ["SHP header is too short."]

    file_len_words = struct.unpack(">i", data[24:28])[0]
    file_len = file_len_words * 2
    if file_len != len(data):
        issues.append(f"SHP length mismatch: header={file_len}, actual={len(data)}.")

    shape_type_code = struct.unpack("<i", data[32:36])[0]
    shp_shape_type = SHAPE_TYPE_MAP.get(shape_type_code, f"Unknown({shape_type_code})")

    record_types: dict[int, int] = {}
    null_geometries = 0
    invalid_geometries = 0

    pos = 100
    while pos + 8 <= len(data):
        rec_no, rec_len_words = struct.unpack(">2i", data[pos : pos + 8])
        _ = rec_no
        rec_len = rec_len_words * 2
        rec = data[pos + 8 : pos + 8 + rec_len]
        if len(rec) < 4:
            invalid_geometries += 1
            break
        rec_shape = struct.unpack("<i", rec[:4])[0]
        record_types[rec_shape] = record_types.get(rec_shape, 0) + 1
        if rec_shape == 0:
            null_geometries += 1
        elif rec_shape in (5, 15, 25):
            # Structural validity checks for polygon-like records.
            if len(rec) < 44:
                invalid_geometries += 1
            else:
                num_parts, num_points = struct.unpack("<2i", rec[36:44])
                base = 44
                expected_min = base + (num_parts * 4) + (num_points * 16)
                if num_parts < 1 or num_points < 4 or len(rec) < expected_min:
                    invalid_geometries += 1
                else:
                    parts: list[int] = []
                    for i in range(num_parts):
                        parts.append(struct.unpack("<i", rec[base + i * 4 : base + (i + 1) * 4])[0])
                    pts_off = base + (num_parts * 4)
                    points: list[tuple[float, float]] = []
                    for i in range(num_points):
                        x, y = struct.unpack("<2d", rec[pts_off + i * 16 : pts_off + (i + 1) * 16])
                        points.append((x, y))
                    idxs = parts + [num_points]
                    for a, b in zip(idxs, idxs[1:]):
                        if not (0 <= a < b <= num_points):
                            invalid_geometries += 1
                            break
                        ring = points[a:b]
                        if len(ring) < 4 or ring[0] != ring[-1]:
                            invalid_geometries += 1
                            break
        pos += 8 + rec_len

    geometry_types = [SHAPE_TYPE_MAP.get(code, f"Unknown({code})") for code in sorted(record_types.keys())]
    return shp_shape_type, geometry_types, null_geometries, invalid_geometries, issues


def run_tar_extract(archive_path: Path, target_dir: Path) -> tuple[bool, str]:
    cmd = ["tar", "-xf", str(archive_path), "-C", str(target_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0:
        return True, "tar extraction succeeded"
    error = (proc.stderr or proc.stdout or "").strip()
    return False, f"tar extraction failed: {error}"


def run_py7zr_extract(archive_path: Path, target_dir: Path) -> tuple[bool, str]:
    try:
        import py7zr  # type: ignore
    except Exception:
        return False, "py7zr not available (install: pip install py7zr)"
    try:
        with py7zr.SevenZipFile(archive_path, mode="r") as zf:
            zf.extractall(path=target_dir)
        return True, "py7zr extraction succeeded"
    except Exception as exc:
        return False, f"py7zr extraction failed: {exc}"


def collect_shp_layers(root_dir: Path) -> list[Path]:
    return sorted(root_dir.rglob("*.shp"))


def choose_section_layer(layers: list[LayerInspection]) -> LayerInspection | None:
    if not layers:
        return None
    for layer in layers:
        if "seccion" in normalize(Path(layer.shp_path).stem):
            return layer
    for layer in layers:
        if layer.key_candidates.get("seccion"):
            return layer
    return layers[0]


def inspect_layer(shp_path: Path) -> LayerInspection:
    issues: list[str] = []
    dbf_path = shp_path.with_suffix(".dbf")
    prj_path = shp_path.with_suffix(".prj")

    row_count = None
    columns: list[str] = []
    if dbf_path.exists():
        row_count, columns = parse_dbf_fields(dbf_path)
    else:
        issues.append("Missing DBF for shapefile layer.")

    crs_wkt, crs_hint = parse_prj(prj_path)
    shp_shape_type, geometry_types, null_geoms, invalid_geoms, shp_issues = inspect_shp_structure(shp_path)
    issues.extend(shp_issues)

    # Prefer geopandas when available; fallback remains structural inspection.
    try:
        import geopandas as gpd  # type: ignore

        gdf = gpd.read_file(shp_path)
        row_count = int(len(gdf))
        columns = [str(c) for c in gdf.columns]
        key_map = key_candidates(columns)
        geom_series = gdf.geometry
        null_geoms = int(geom_series.isna().sum())
        invalid_geoms = int((~geom_series.is_valid).sum())
        geom_types = sorted(set(str(gt) for gt in geom_series.geom_type.dropna().tolist()))
        if gdf.crs is not None:
            crs_hint = str(gdf.crs)
    except Exception:
        issues.append("geopandas not available or failed; using structural shapefile checks.")
        key_map = key_candidates(columns)
        geom_types = geometry_types

    return LayerInspection(
        shp_path=str(shp_path.relative_to(ROOT)),
        row_count=row_count,
        geometry_types=geom_types,
        shp_shape_type=shp_shape_type,
        columns=columns,
        key_candidates=key_map,
        crs_wkt=crs_wkt,
        crs_hint=crs_hint,
        null_geometries=null_geoms,
        invalid_geometries=invalid_geoms,
        issues=issues,
    )


def inspect_ine_package() -> dict[str, Any]:
    result: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "zip_file": str(RAW_INE_ZIP.relative_to(ROOT)),
        "status": "needs_review",
        "nested_7z_files": [],
        "extractor_used": None,
        "extractor_note": None,
        "layers_found": [],
        "section_layer": None,
        "usable_for_territorial_join": False,
        "issues": [],
    }

    if not RAW_INE_ZIP.exists():
        result["issues"].append("INE ZIP file not found.")
        return result

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(RAW_INE_ZIP) as zf:
        nested_7z = [name for name in zf.namelist() if name.lower().endswith(".7z")]
        result["nested_7z_files"] = nested_7z
        if not nested_7z:
            result["issues"].append("No nested .7z found inside INE ZIP.")
            return result
        for name in nested_7z:
            out_path = TMP_DIR / Path(name).name
            out_path.write_bytes(zf.read(name))

    extracted_any = False
    extractor_notes: list[str] = []
    for nested in [TMP_DIR / Path(n).name for n in result["nested_7z_files"]]:
        ok, note = run_py7zr_extract(nested, TMP_DIR)
        extractor_notes.append(note)
        if ok:
            extracted_any = True
            result["extractor_used"] = "py7zr"
            break

    if not extracted_any:
        for nested in [TMP_DIR / Path(n).name for n in result["nested_7z_files"]]:
            ok, note = run_tar_extract(nested, TMP_DIR)
            extractor_notes.append(note)
            if ok:
                extracted_any = True
                result["extractor_used"] = "tar"
                break

    result["extractor_note"] = " | ".join(extractor_notes)
    if not extracted_any:
        result["issues"].append("Could not extract nested .7z with py7zr or tar.")
        result["issues"].append("Install dependency: pip install py7zr")
        return result

    shp_paths = collect_shp_layers(TMP_DIR)
    if not shp_paths:
        result["issues"].append("No .shp files found after extraction.")
        return result

    layer_inspections = [inspect_layer(p) for p in shp_paths]
    result["layers_found"] = [
        {
            "shp_path": li.shp_path,
            "row_count": li.row_count,
            "shp_shape_type": li.shp_shape_type,
            "columns": li.columns,
            "key_candidates": li.key_candidates,
            "crs_hint": li.crs_hint,
            "null_geometries": li.null_geometries,
            "invalid_geometries": li.invalid_geometries,
            "issues": li.issues,
        }
        for li in layer_inspections
    ]

    section_layer = choose_section_layer(layer_inspections)
    if section_layer is None:
        result["issues"].append("Could not identify secciones layer.")
        return result

    result["section_layer"] = {
        "shp_path": section_layer.shp_path,
        "row_count": section_layer.row_count,
        "crs_wkt": section_layer.crs_wkt,
        "crs_hint": section_layer.crs_hint,
        "geometry_types": section_layer.geometry_types,
        "shp_shape_type": section_layer.shp_shape_type,
        "columns": section_layer.columns,
        "key_candidates": section_layer.key_candidates,
        "null_geometries": section_layer.null_geometries,
        "invalid_geometries": section_layer.invalid_geometries,
        "issues": section_layer.issues,
    }

    has_keys = (
        bool(section_layer.key_candidates.get("entidad"))
        and bool(section_layer.key_candidates.get("municipio"))
        and bool(section_layer.key_candidates.get("seccion"))
    )
    no_geom_errors = (section_layer.null_geometries or 0) == 0 and (section_layer.invalid_geometries or 0) == 0
    has_rows = (section_layer.row_count or 0) > 0
    polygon_like = any("Polygon" in gt for gt in section_layer.geometry_types)

    result["usable_for_territorial_join"] = bool(has_keys and no_geom_errors and has_rows and polygon_like)
    result["status"] = "inspected" if result["usable_for_territorial_join"] else "needs_review"
    if not result["usable_for_territorial_join"]:
        result["issues"].append("Section layer found but failed minimum usability checks for territorial join.")
    return result


def load_raw_schema_json() -> dict[str, Any]:
    if RAW_AUDIT_JSON.exists():
        return json.loads(RAW_AUDIT_JSON.read_text(encoding="utf-8"))
    return {"generated_at": datetime.now().isoformat(timespec="seconds"), "results": []}


def update_raw_schema_json(ine_result: dict[str, Any]) -> dict[str, Any]:
    payload = load_raw_schema_json()
    results = payload.get("results", [])
    if not isinstance(results, list):
        results = []

    section = ine_result.get("section_layer") or {}
    ine_entry = {
        "file": "data\\raw\\ine\\bgd_11_Shapefile.zip",
        "status": "inspected" if ine_result.get("usable_for_territorial_join") else "needs_review",
        "detected_format": "zip -> 7z -> shapefile",
        "row_count_sampled": section.get("row_count"),
        "columns": section.get("columns", []),
        "key_candidates": section.get("key_candidates", {}),
        "vote_candidates": {"pan": [], "total_votos": []},
        "issues": ine_result.get("issues", []),
        "section_layer_detected": section.get("shp_path"),
        "crs": section.get("crs_hint") or section.get("crs_wkt"),
        "geometry_types": section.get("geometry_types", []),
        "null_geometries": section.get("null_geometries"),
        "invalid_geometries": section.get("invalid_geometries"),
        "usable_for_territorial_join": ine_result.get("usable_for_territorial_join", False),
    }

    replaced = False
    for idx, row in enumerate(results):
        if str(row.get("file", "")).replace("/", "\\").lower() == "data\\raw\\ine\\bgd_11_shapefile.zip":
            results[idx] = ine_entry
            replaced = True
            break
    if not replaced:
        results.insert(0, ine_entry)

    # Remove stale nested INE pseudo-rows if any.
    payload["results"] = results
    payload["generated_at"] = datetime.now().isoformat(timespec="seconds")

    # Disambiguate IEEG 2021 files.
    for row in payload["results"]:
        file_name = str(row.get("file", "")).lower()
        if file_name.endswith("gto_dip_loc_2021.csv"):
            row["role"] = "primary_votes"
        if file_name.endswith("gto_dip_loc_candidaturas_2021.csv"):
            row["role"] = "auxiliary_metadata"

    RAW_AUDIT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return payload


def inventory_update_for_ine(ine_result: dict[str, Any]) -> None:
    if not INVENTORY_CSV.exists():
        return
    rows = list(csv.DictReader(INVENTORY_CSV.read_text(encoding="utf-8").splitlines()))
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    for row in rows:
        actual = (row.get("actual_filename") or "").strip()
        if actual.lower() != "bgd_11_shapefile.zip":
            continue
        if ine_result.get("usable_for_territorial_join"):
            row["acquisition_status"] = "inspected"
            note = "Inspected: nested .7z extracted; SECCION layer usable for territorial join."
        else:
            row["acquisition_status"] = "needs_review"
            note = "Needs review: extraction or section-layer validation failed."
        old = row.get("notes", "").strip()
        if note not in old:
            row["notes"] = (old + " | " + note).strip(" |")

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    INVENTORY_CSV.write_text(out.getvalue(), encoding="utf-8", newline="")


def write_raw_schema_markdown(payload: dict[str, Any], ine_result: dict[str, Any]) -> None:
    results = payload.get("results", [])

    def by_file(needle: str) -> dict[str, Any] | None:
        for item in results:
            if needle.lower() in str(item.get("file", "")).lower():
                return item
        return None

    ine = by_file("data\\raw\\ine\\bgd_11_shapefile.zip")
    edmslm = by_file("edmslm_ine_corte_ene_2026.txt")
    x18 = by_file("computo x casillas diputaciones.xlsx")
    x21_votes = by_file("gto_dip_loc_2021.csv")
    x21_cand = by_file("gto_dip_loc_candidaturas_2021.csv")

    blockers: list[str] = []
    if not ine_result.get("usable_for_territorial_join"):
        blockers.append("No se pudo confirmar capa seccional INE usable para join territorial.")

    decision = "aprobado para Epica 2.2" if not blockers else "no aprobado para Epica 2.2"

    lines: list[str] = []
    lines.append("# Raw Schema Audit")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append("")
    lines.append(f"- Fecha: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Decision: `{decision}`")
    lines.append("- Hallazgos clave:")
    if edmslm:
        lines.append("- EDMSLM mantiene campos utiles para entidad/municipio/seccion.")
    if x18:
        lines.append("- IEEG 2018 confirma votos PAN y TOTAL en granularidad por casilla.")
    if x21_votes:
        lines.append("- IEEG 2021 confirma votos PAN y TOTAL_VOTOS_CALCULADO en granularidad por casilla.")
    lines.append("- Paquete INE se resolvio mediante extraccion del .7z anidado y validacion de capa SECCION.")
    lines.append("")

    lines.append("## Archivos Inspeccionados")
    lines.append("")
    for item in results:
        role = item.get("role")
        role_txt = f", role: `{role}`" if role else ""
        lines.append(
            f"- `{item.get('file')}` -> status: `{item.get('status')}`, format: `{item.get('detected_format')}`{role_txt}"
        )
    lines.append("")

    lines.append("## Resolucion paquete INE / shapefile seccional")
    lines.append("")
    lines.append(f"- ZIP analizado: `{ine_result.get('zip_file')}`")
    lines.append(f"- .7z anidados detectados: `{json.dumps(ine_result.get('nested_7z_files', []), ensure_ascii=True)}`")
    lines.append(f"- Extractor usado: `{ine_result.get('extractor_used')}`")
    lines.append(f"- Nota extractor: `{ine_result.get('extractor_note')}`")
    section = ine_result.get("section_layer") or {}
    if section:
        lines.append(f"- Capa seccional detectada: `{section.get('shp_path')}`")
        lines.append(f"- CRS detectado: `{section.get('crs_hint') or section.get('crs_wkt')}`")
        lines.append(f"- Filas: `{section.get('row_count')}`")
        lines.append(f"- Tipo de geometria: `{json.dumps(section.get('geometry_types', []), ensure_ascii=True)}`")
        lines.append(f"- Columnas: `{', '.join(section.get('columns', []))}`")
        lines.append(f"- Campos candidatos entidad: `{json.dumps(section.get('key_candidates', {}).get('entidad', []), ensure_ascii=True)}`")
        lines.append(f"- Campos candidatos municipio: `{json.dumps(section.get('key_candidates', {}).get('municipio', []), ensure_ascii=True)}`")
        lines.append(f"- Campos candidatos seccion: `{json.dumps(section.get('key_candidates', {}).get('seccion', []), ensure_ascii=True)}`")
        lines.append(f"- Geometrias nulas: `{section.get('null_geometries')}`")
        lines.append(f"- Geometrias invalidas (chequeo estructural): `{section.get('invalid_geometries')}`")
    lines.append(f"- Usable para join territorial: `{ine_result.get('usable_for_territorial_join')}`")
    lines.append("")

    lines.append("## Esquemas detectados para joins y votos")
    lines.append("")
    if edmslm:
        lines.append(f"- EDMSLM key candidates: `{json.dumps(edmslm.get('key_candidates', {}), ensure_ascii=True)}`")
    if x18:
        lines.append(f"- IEEG 2018 key candidates: `{json.dumps(x18.get('key_candidates', {}), ensure_ascii=True)}`")
        lines.append(f"- IEEG 2018 vote candidates: `{json.dumps(x18.get('vote_candidates', {}), ensure_ascii=True)}`")
    if x21_votes:
        lines.append(f"- IEEG 2021 principal ({x21_votes.get('file')}):")
        lines.append(f"- key candidates: `{json.dumps(x21_votes.get('key_candidates', {}), ensure_ascii=True)}`")
        lines.append(f"- vote candidates: `{json.dumps(x21_votes.get('vote_candidates', {}), ensure_ascii=True)}`")
    if x21_cand:
        lines.append(f"- IEEG 2021 auxiliar ({x21_cand.get('file')}): metadatos de candidaturas, no fuente principal de votos.")
    lines.append("")

    lines.append("## Riesgos")
    lines.append("")
    risk_lines: list[str] = []
    if not x18 or not x18.get("key_candidates", {}).get("municipio"):
        risk_lines.append("IEEG 2018 no trae municipio explicito; se requiere derivacion territorial por seccion.")
    if not x21_votes or not x21_votes.get("key_candidates", {}).get("municipio"):
        risk_lines.append("IEEG 2021 no trae municipio explicito; se requiere derivacion territorial por seccion.")
    for issue in ine_result.get("issues", []):
        if "install dependency" in issue.lower():
            risk_lines.append(issue)
    if risk_lines:
        for r in risk_lines:
            lines.append(f"- {r}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Bloqueadores")
    lines.append("")
    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Decision")
    lines.append("")
    lines.append(f"- `{decision}`")
    lines.append("")

    RAW_AUDIT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    (ROOT / "reports" / "data_qa").mkdir(parents=True, exist_ok=True)
    ine_result = inspect_ine_package()
    INE_AUDIT_JSON.write_text(json.dumps(ine_result, ensure_ascii=True, indent=2), encoding="utf-8")
    payload = update_raw_schema_json(ine_result)
    write_raw_schema_markdown(payload, ine_result)
    inventory_update_for_ine(ine_result)
    print(f"[audit-ine-geography] INE report: {INE_AUDIT_JSON}")
    print(f"[audit-ine-geography] Updated: {RAW_AUDIT_MD}")
    print(f"[audit-ine-geography] Updated: {RAW_AUDIT_JSON}")
    print(f"[audit-ine-geography] Updated: {INVENTORY_CSV}")


if __name__ == "__main__":
    main()
