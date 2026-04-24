from __future__ import annotations

import csv
import io
import json
import re
import struct
import subprocess
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
REPORT_DIR = ROOT / "reports" / "data_qa"
TMP_DIR = REPORT_DIR / "tmp_ine_extract"

RAW_INE_ZIP = RAW_DIR / "ine" / "bgd_11_Shapefile.zip"
RAW_EDMSLM = RAW_DIR / "ine" / "edmslm_ine_corte_ene_2026.txt"
RAW_2018_XLSX = RAW_DIR / "ieeg" / "2018" / "Computo x casillas Diputaciones.xlsx"
RAW_2021_ZIP = RAW_DIR / "ieeg" / "2021" / "computos_ieeg_2021_diputaciones_base_datos.zip"

OUT_INE_INDEX = INTERIM_DIR / "ine_secciones_raw_index.csv"
OUT_INE_LEON = INTERIM_DIR / "ine_secciones_leon.geojson"
OUT_EDMSLM_LEON = INTERIM_DIR / "edmslm_leon.csv"
OUT_2018 = INTERIM_DIR / "ieeg_2018_diputaciones_seccion.csv"
OUT_2021 = INTERIM_DIR / "ieeg_2021_diputaciones_seccion.csv"
OUT_JOIN = INTERIM_DIR / "join_key_diagnostics.csv"

OUT_REPORT_MD = REPORT_DIR / "interim_staging_report.md"
OUT_REPORT_JSON = REPORT_DIR / "interim_staging_report.json"


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def detect_encoding(sample: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            sample.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"


def detect_delimiter(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()][:30]
    if not lines:
        return ","
    joined = "\n".join(lines)
    try:
        dialect = csv.Sniffer().sniff(joined, delimiters=",;|\t")
        return dialect.delimiter
    except csv.Error:
        counts = {d: joined.count(d) for d in [",", ";", "|", "\t"]}
        return max(counts, key=counts.get)


def normalize_digits(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    if re.fullmatch(r"[-+]?\d+(\.0+)?", text):
        return str(int(float(text)))
    m = re.search(r"\d+", text)
    if m:
        return str(int(m.group(0)))
    return None


def normalize_entidad(value: Any) -> str | None:
    code = normalize_digits(value)
    if code is None:
        return None
    return code.zfill(2)


def normalize_municipio(value: Any) -> str | None:
    code = normalize_digits(value)
    if code is None:
        return None
    return code.zfill(3)


def normalize_seccion(value: Any) -> str | None:
    code = normalize_digits(value)
    if code is None:
        return None
    return code.lstrip("0") or "0"


def make_section_id(entidad: str | None, municipio: str | None, seccion: str | None) -> str | None:
    if not entidad or not municipio or not seccion:
        return None
    return f"{entidad}{municipio}{seccion}"


def to_int(value: Any) -> int:
    if value is None:
        return 0
    text = str(value).strip()
    if not text:
        return 0
    text = text.replace(",", "")
    text = text.replace(" ", "")
    try:
        return int(float(text))
    except ValueError:
        return 0


def to_pct(part: int, total: int) -> float | None:
    if total <= 0:
        return None
    return (part / total) * 100.0


def canonical_field_map(fields: list[str]) -> dict[str, str | None]:
    mapping: dict[str, str | None] = {
        "entidad": None,
        "municipio": None,
        "municipio_nombre": None,
        "seccion": None,
        "distrito_local": None,
        "distrito_federal": None,
        "casilla": None,
        "pan": None,
        "total": None,
    }
    normalized = {normalize_text(col): col for col in fields}
    for norm, original in normalized.items():
        if mapping["entidad"] is None and ("entidad" in norm or "id_estado" in norm or norm == "estado"):
            mapping["entidad"] = original
        if mapping["municipio"] is None and ("municipio" in norm and "nombre" not in norm):
            mapping["municipio"] = original
        if mapping["municipio_nombre"] is None and ("nombre_municipio" in norm or ("municipio" in norm and "nombre" in norm)):
            mapping["municipio_nombre"] = original
        if mapping["seccion"] is None and "seccion" in norm:
            mapping["seccion"] = original
        if mapping["distrito_federal"] is None and ("distrito_federal" in norm or norm.endswith("distrito_f")):
            mapping["distrito_federal"] = original
        if mapping["distrito_local"] is None and ("distrito_local" in norm or norm.endswith("distrito_l") or norm == "distrito"):
            mapping["distrito_local"] = original
        if mapping["casilla"] is None and ("casilla" in norm or "clave_casilla" in norm or "id_casilla" in norm):
            mapping["casilla"] = original
        if mapping["pan"] is None and (norm == "pan" or norm.endswith("_pan")):
            mapping["pan"] = original
        if mapping["total"] is None and ("total_votos_calculado" in norm or norm == "total" or "total_votos" in norm):
            mapping["total"] = original
    return mapping


def extract_nested_7z(outer_zip: Path, temp_dir: Path) -> list[Path]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    sevenz_files: list[Path] = []
    with zipfile.ZipFile(outer_zip) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".7z"):
                out = temp_dir / Path(name).name
                out.write_bytes(zf.read(name))
                sevenz_files.append(out)
    if not sevenz_files:
        raise RuntimeError("No nested .7z file found in INE ZIP.")
    return sevenz_files


def extract_7z_archive(archive: Path, target: Path) -> str:
    try:
        import py7zr  # type: ignore

        with py7zr.SevenZipFile(archive, mode="r") as zf:
            zf.extractall(path=target)
        return "py7zr"
    except Exception:
        pass

    cmd = ["tar", "-xf", str(archive), "-C", str(target)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0:
        return "tar"
    raise RuntimeError("Unable to extract nested .7z (install py7zr: pip install py7zr).")


def parse_dbf(dbf_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    data = dbf_path.read_bytes()
    if len(data) < 32:
        raise RuntimeError("DBF header is too short.")
    row_count = int.from_bytes(data[4:8], "little")
    header_len = int.from_bytes(data[8:10], "little")
    record_len = int.from_bytes(data[10:12], "little")

    fields: list[tuple[str, str, int, int]] = []
    offset = 32
    while offset + 32 <= header_len:
        chunk = data[offset : offset + 32]
        if chunk[0] == 0x0D:
            break
        name = chunk[:11].split(b"\x00", 1)[0].decode("ascii", errors="ignore").strip()
        ftype = chr(chunk[11])
        flen = int(chunk[16])
        dec = int(chunk[17])
        fields.append((name, ftype, flen, dec))
        offset += 32

    records: list[dict[str, Any]] = []
    pos = header_len
    for _ in range(row_count):
        rec = data[pos : pos + record_len]
        pos += record_len
        if not rec:
            continue
        if rec[0] == 0x2A:
            continue
        rec_data: dict[str, Any] = {}
        ptr = 1
        for name, ftype, flen, dec in fields:
            raw = rec[ptr : ptr + flen]
            ptr += flen
            text = raw.decode("latin1", errors="ignore").strip()
            if text == "":
                value: Any = None
            elif ftype in ("N", "F"):
                if dec == 0:
                    try:
                        value = int(float(text))
                    except ValueError:
                        value = text
                else:
                    try:
                        value = float(text)
                    except ValueError:
                        value = text
            else:
                value = text
            rec_data[name] = value
        records.append(rec_data)
    return records, [f[0] for f in fields]


def parse_shp_polygons(shp_path: Path) -> tuple[list[dict[str, Any] | None], str, int, int]:
    data = shp_path.read_bytes()
    if len(data) < 100:
        raise RuntimeError("SHP file is too short.")

    global_shape_type = struct.unpack("<i", data[32:36])[0]
    global_shape_name = {5: "Polygon", 15: "PolygonZ", 25: "PolygonM"}.get(global_shape_type, str(global_shape_type))

    geometries: list[dict[str, Any] | None] = []
    null_geometries = 0
    invalid_geometries = 0
    pos = 100
    while pos + 8 <= len(data):
        rec_len_words = struct.unpack(">i", data[pos + 4 : pos + 8])[0]
        rec_len = rec_len_words * 2
        rec = data[pos + 8 : pos + 8 + rec_len]
        pos += 8 + rec_len
        if len(rec) < 4:
            geometries.append(None)
            invalid_geometries += 1
            continue
        shape_type = struct.unpack("<i", rec[:4])[0]
        if shape_type == 0:
            geometries.append(None)
            null_geometries += 1
            continue
        if shape_type not in (5, 15, 25):
            geometries.append(None)
            invalid_geometries += 1
            continue
        if len(rec) < 44:
            geometries.append(None)
            invalid_geometries += 1
            continue

        num_parts, num_points = struct.unpack("<2i", rec[36:44])
        base = 44
        expected = base + num_parts * 4 + num_points * 16
        if num_parts < 1 or num_points < 4 or len(rec) < expected:
            geometries.append(None)
            invalid_geometries += 1
            continue

        parts = [struct.unpack("<i", rec[base + i * 4 : base + (i + 1) * 4])[0] for i in range(num_parts)]
        points_offset = base + num_parts * 4
        points = [
            struct.unpack("<2d", rec[points_offset + i * 16 : points_offset + (i + 1) * 16])
            for i in range(num_points)
        ]
        idxs = parts + [num_points]
        rings: list[list[list[float]]] = []
        valid = True
        for a, b in zip(idxs, idxs[1:]):
            if not (0 <= a < b <= num_points):
                valid = False
                break
            ring = [[float(x), float(y)] for x, y in points[a:b]]
            if len(ring) < 4:
                valid = False
                break
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            rings.append(ring)
        if not valid or not rings:
            geometries.append(None)
            invalid_geometries += 1
            continue
        geometries.append({"type": "Polygon", "coordinates": rings})
    return geometries, global_shape_name, null_geometries, invalid_geometries


def detect_leon_from_edmslm() -> tuple[list[dict[str, Any]], set[str], str]:
    if not RAW_EDMSLM.exists():
        raise FileNotFoundError(f"Missing EDMSLM file: {RAW_EDMSLM}")

    sample = RAW_EDMSLM.read_bytes()[:200_000]
    encoding = detect_encoding(sample)
    delimiter = detect_delimiter(sample.decode(encoding, errors="replace"))

    rows_out: list[dict[str, Any]] = []
    leon_codes_counter: Counter[str] = Counter()
    warnings: list[str] = []

    with RAW_EDMSLM.open("r", encoding=encoding, errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        if reader.fieldnames is None:
            raise RuntimeError("EDMSLM has no header row.")
        fields = [f.strip() for f in reader.fieldnames]
        cmap = canonical_field_map(fields)
        if not cmap["entidad"] or not cmap["municipio"] or not cmap["seccion"]:
            raise RuntimeError("EDMSLM missing key fields for entidad/municipio/seccion.")

        mun_name_col = cmap["municipio_nombre"]
        for rec in reader:
            ent = normalize_entidad(rec.get(cmap["entidad"], ""))
            if ent != "11":
                continue
            mun_name = str(rec.get(mun_name_col, "")).strip() if mun_name_col else ""
            mun_name_norm = normalize_text(mun_name)
            is_leon = mun_name_norm == "leon" or mun_name_norm.startswith("leon_")
            if not is_leon:
                continue
            mun = normalize_municipio(rec.get(cmap["municipio"], ""))
            sec = normalize_seccion(rec.get(cmap["seccion"], ""))
            if not mun or not sec:
                continue
            leon_codes_counter[mun] += 1
            distrito_local = rec.get(cmap["distrito_local"], "") if cmap["distrito_local"] else ""
            distrito_federal = rec.get(cmap["distrito_federal"], "") if cmap["distrito_federal"] else ""
            rows_out.append(
                {
                    "entidad": ent,
                    "municipio": mun,
                    "municipio_nombre": mun_name or "LEON",
                    "seccion": sec,
                    "section_id": make_section_id(ent, mun, sec),
                    "distrito_local": str(distrito_local).strip() or None,
                    "distrito_federal": str(distrito_federal).strip() or None,
                }
            )

    if not rows_out:
        raise RuntimeError("Could not detect Leon rows in EDMSLM for entidad 11.")

    leon_codes = set(leon_codes_counter.keys())
    if len(leon_codes) > 1:
        warnings.append(f"Multiple municipio codes detected for Leon in EDMSLM: {sorted(leon_codes)}")

    dedup: dict[str, dict[str, Any]] = {}
    for row in rows_out:
        sid = row["section_id"]
        if sid not in dedup:
            dedup[sid] = row
    final_rows = list(dedup.values())
    final_rows.sort(key=lambda r: int(r["seccion"]))

    with OUT_EDMSLM_LEON.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "entidad",
                "municipio",
                "municipio_nombre",
                "seccion",
                "section_id",
                "distrito_local",
                "distrito_federal",
            ],
        )
        writer.writeheader()
        writer.writerows(final_rows)

    warning_text = "; ".join(warnings) if warnings else ""
    return final_rows, leon_codes, warning_text


def build_ine_interim(leon_codes: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not RAW_INE_ZIP.exists():
        raise FileNotFoundError(f"Missing INE ZIP file: {RAW_INE_ZIP}")
    if not leon_codes:
        raise RuntimeError("No Leon municipio code detected from EDMSLM.")

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    sevenz = extract_nested_7z(RAW_INE_ZIP, TMP_DIR)
    extractor_used = extract_7z_archive(sevenz[0], TMP_DIR)

    shp_candidates = [p for p in TMP_DIR.rglob("*.shp") if normalize_text(p.stem) == "seccion"]
    if not shp_candidates:
        raise RuntimeError("SECCION.shp layer not found after extraction.")
    shp_path = sorted(shp_candidates)[0]
    dbf_path = shp_path.with_suffix(".dbf")
    prj_path = shp_path.with_suffix(".prj")
    if not dbf_path.exists():
        raise RuntimeError("SECCION.dbf not found.")

    records, columns = parse_dbf(dbf_path)
    geometries, geometry_type, null_geometries, invalid_geometries = parse_shp_polygons(shp_path)
    crs_text = prj_path.read_text(encoding="utf-8", errors="replace").strip() if prj_path.exists() else ""
    crs_hint = "EPSG:32614 (heuristic)" if "UTM_Zone_14N" in crs_text or "WGS_1984_UTM_Zone_14N" in crs_text else ""
    cmap = canonical_field_map(columns)
    if not cmap["entidad"] or not cmap["municipio"] or not cmap["seccion"]:
        raise RuntimeError("SECCION layer missing key fields for entidad/municipio/seccion.")

    features: list[dict[str, Any]] = []
    output_rows: list[dict[str, Any]] = []
    max_rows = min(len(records), len(geometries))
    for idx in range(max_rows):
        rec = records[idx]
        geom = geometries[idx]
        ent = normalize_entidad(rec.get(cmap["entidad"])) if cmap["entidad"] else None
        mun = normalize_municipio(rec.get(cmap["municipio"])) if cmap["municipio"] else None
        sec = normalize_seccion(rec.get(cmap["seccion"])) if cmap["seccion"] else None
        if ent != "11" or not mun or mun not in leon_codes or not sec:
            continue
        sid = make_section_id(ent, mun, sec)
        output_rows.append({"entidad": ent, "municipio": mun, "seccion": sec, "section_id": sid, "geometry": geom})
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "entidad": ent,
                    "municipio": mun,
                    "seccion": sec,
                    "section_id": sid,
                },
                "geometry": geom,
            }
        )

    feature_collection = {"type": "FeatureCollection", "name": "ine_secciones_leon", "features": features}
    OUT_INE_LEON.write_text(json.dumps(feature_collection, ensure_ascii=False), encoding="utf-8")

    with OUT_INE_INDEX.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "layer_name",
                "original_columns",
                "crs_detected",
                "row_count",
                "null_geometries",
                "invalid_geometries",
                "candidate_entidad",
                "candidate_municipio",
                "candidate_seccion",
                "extractor_used",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "layer_name": str(shp_path.relative_to(ROOT)),
                "original_columns": "|".join(columns),
                "crs_detected": crs_hint or crs_text,
                "row_count": len(records),
                "null_geometries": null_geometries,
                "invalid_geometries": invalid_geometries,
                "candidate_entidad": cmap["entidad"],
                "candidate_municipio": cmap["municipio"],
                "candidate_seccion": cmap["seccion"],
                "extractor_used": extractor_used,
            }
        )

    summary = {
        "layer_path": str(shp_path.relative_to(ROOT)),
        "crs_detected": crs_hint or crs_text,
        "row_count": len(records),
        "geometry_type": geometry_type,
        "null_geometries": null_geometries,
        "invalid_geometries": invalid_geometries,
        "candidate_keys": {
            "entidad": cmap["entidad"],
            "municipio": cmap["municipio"],
            "seccion": cmap["seccion"],
        },
        "features_leon": len(features),
    }
    return output_rows, summary


def read_xlsx_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(name))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    out: list[str] = []
    for si in root.findall(".//x:si", ns):
        texts = [t.text or "" for t in si.findall(".//x:t", ns)]
        out.append("".join(texts))
    return out


def read_xlsx_sheet_map(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    ns_w = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ns_r = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    rel_map = {rel.attrib.get("Id", ""): rel.attrib.get("Target", "") for rel in rels.findall(".//r:Relationship", ns_r)}
    out: list[tuple[str, str]] = []
    for sheet in wb.findall(".//x:sheets/x:sheet", ns_w):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
        target = rel_map.get(rid, "")
        if target and not target.startswith("xl/"):
            target = f"xl/{target}"
        out.append((name, target))
    return out


def col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return max(idx - 1, 0)


def read_sheet_rows(zf: zipfile.ZipFile, sheet_path: str, shared: list[str]) -> list[list[str]]:
    if sheet_path not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(sheet_path))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        cells: dict[int, str] = {}
        for c in row.findall("x:c", ns):
            ref = c.attrib.get("r", "")
            idx = col_index(ref) if ref else len(cells)
            t = c.attrib.get("t", "")
            value = ""
            if t == "s":
                v = c.find("x:v", ns)
                if v is not None and v.text and v.text.isdigit():
                    sidx = int(v.text)
                    if 0 <= sidx < len(shared):
                        value = shared[sidx]
            elif t == "inlineStr":
                tn = c.find("x:is/x:t", ns)
                value = tn.text if tn is not None and tn.text else ""
            else:
                v = c.find("x:v", ns)
                value = v.text if v is not None and v.text else ""
            cells[idx] = value.strip()
        if cells:
            max_idx = max(cells.keys())
            rows.append([cells.get(i, "") for i in range(max_idx + 1)])
    return rows


def detect_header_row(rows: list[list[str]]) -> tuple[int, list[str]]:
    best_idx = -1
    best_score = -1
    best_cols: list[str] = []
    tokens = ("seccion", "casilla", "pan", "total")
    for idx, row in enumerate(rows[:120]):
        cols = [c.strip() for c in row]
        non_empty = [c for c in cols if c]
        if len(non_empty) < 4:
            continue
        score = len(non_empty)
        norms = [normalize_text(c) for c in non_empty]
        token_hits = sum(1 for n in norms if any(tok in n for tok in tokens))
        score += token_hits * 3
        if score > best_score:
            best_score = score
            best_idx = idx
            best_cols = cols
    if best_idx < 0:
        raise RuntimeError("Unable to detect XLSX header row.")
    while best_cols and best_cols[-1] == "":
        best_cols.pop()
    return best_idx, best_cols


def detect_csv_header(lines: list[str], delimiter: str) -> tuple[int, list[str]]:
    best_idx = -1
    best_score = -1
    best_cols: list[str] = []
    tokens = ("seccion", "casilla", "pan", "total")
    for idx, line in enumerate(lines[:80]):
        row = next(csv.reader([line], delimiter=delimiter))
        cols = [c.strip() for c in row]
        non_empty = [c for c in cols if c]
        if len(non_empty) < 4:
            continue
        norms = [normalize_text(c) for c in non_empty]
        score = len(non_empty) + sum(3 for n in norms if any(tok in n for tok in tokens))
        if score > best_score:
            best_score = score
            best_idx = idx
            best_cols = cols
    if best_idx < 0:
        raise RuntimeError("Unable to detect CSV header row.")
    while best_cols and best_cols[-1] == "":
        best_cols.pop()
    return best_idx, best_cols


def build_ieeg_2018(leon_sections: set[str], leon_municipio: str, source_formula: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not RAW_2018_XLSX.exists():
        raise FileNotFoundError(f"Missing IEEG 2018 XLSX: {RAW_2018_XLSX}")
    with zipfile.ZipFile(RAW_2018_XLSX) as zf:
        shared = read_xlsx_shared_strings(zf)
        sheets = read_xlsx_sheet_map(zf)
        candidate = next((s for s in sheets if "dip" in normalize_text(s[0])), sheets[0] if sheets else None)
        if candidate is None:
            raise RuntimeError("No sheet found in IEEG 2018 XLSX.")
        sheet_name, sheet_path = candidate
        rows = read_sheet_rows(zf, sheet_path, shared)
    if not rows:
        raise RuntimeError("IEEG 2018 sheet has no rows.")
    header_idx, header = detect_header_row(rows)
    cmap = canonical_field_map(header)
    if not cmap["seccion"] or not cmap["pan"] or not cmap["total"]:
        raise RuntimeError("IEEG 2018 missing seccion/PAN/TOTAL columns.")
    col_idx = {name: i for i, name in enumerate(header)}
    sec_i = col_idx[cmap["seccion"]]
    pan_i = col_idx[cmap["pan"]]
    total_i = col_idx[cmap["total"]]

    agg: dict[str, dict[str, Any]] = defaultdict(lambda: {"pan": 0, "total": 0, "rows": 0})
    for row in rows[header_idx + 1 :]:
        sec = normalize_seccion(row[sec_i] if sec_i < len(row) else "")
        if not sec or sec not in leon_sections:
            continue
        pan = to_int(row[pan_i] if pan_i < len(row) else 0)
        total = to_int(row[total_i] if total_i < len(row) else 0)
        agg[sec]["pan"] += pan
        agg[sec]["total"] += total
        agg[sec]["rows"] += 1

    out_rows: list[dict[str, Any]] = []
    for sec in sorted(agg.keys(), key=lambda x: int(x)):
        pan = int(agg[sec]["pan"])
        total = int(agg[sec]["total"])
        out_rows.append(
            {
                "entidad": "11",
                "municipio": leon_municipio or None,
                "seccion": sec,
                "section_id": make_section_id("11", leon_municipio, sec),
                "pan_2018_votos": pan,
                "total_2018": total,
                "pct_pan_2018": to_pct(pan, total),
                "source_rows_2018": int(agg[sec]["rows"]),
            }
        )

    with OUT_2018.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "entidad",
                "municipio",
                "seccion",
                "section_id",
                "pan_2018_votos",
                "total_2018",
                "pct_pan_2018",
                "source_rows_2018",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "source_sheet": sheet_name,
        "rows_output": len(out_rows),
        "pan_total": sum(r["pan_2018_votos"] for r in out_rows),
        "votes_total": sum(r["total_2018"] for r in out_rows),
        "section_id_formula": source_formula,
    }
    return out_rows, summary


def build_ieeg_2021(leon_sections: set[str], leon_municipio: str, source_formula: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not RAW_2021_ZIP.exists():
        raise FileNotFoundError(f"Missing IEEG 2021 ZIP: {RAW_2021_ZIP}")

    with zipfile.ZipFile(RAW_2021_ZIP) as oz:
        nested_dip = next((n for n in oz.namelist() if "dip_loc" in normalize_text(n) and n.lower().endswith(".zip")), None)
        if nested_dip is None:
            raise RuntimeError("IEEG 2021 DIP_LOC nested ZIP not found.")
        dip_bytes = oz.read(nested_dip)

    with zipfile.ZipFile(io.BytesIO(dip_bytes)) as dz:
        names = dz.namelist()
        votes_file = next((n for n in names if n.lower().endswith(".csv") and "candidaturas" not in normalize_text(n) and "_2021" in normalize_text(n)), None)
        aux_file = next((n for n in names if "candidaturas" in normalize_text(n) and n.lower().endswith(".csv")), None)
        if votes_file is None:
            raise RuntimeError("IEEG 2021 primary votes CSV not found.")
        csv_bytes = dz.read(votes_file)

    enc = detect_encoding(csv_bytes[:120_000])
    text = csv_bytes.decode(enc, errors="replace")
    delim = detect_delimiter(text[:10000])
    lines = text.splitlines()
    header_idx, fields = detect_csv_header(lines, delim)
    cmap = canonical_field_map(fields)
    if not cmap["seccion"] or not cmap["pan"] or not cmap["total"]:
        raise RuntimeError("IEEG 2021 votes CSV missing seccion/PAN/total columns.")

    col_idx = {name: i for i, name in enumerate(fields)}
    sec_i = col_idx[cmap["seccion"]]
    pan_i = col_idx[cmap["pan"]]
    total_i = col_idx[cmap["total"]]

    agg: dict[str, dict[str, Any]] = defaultdict(lambda: {"pan": 0, "total": 0, "rows": 0})
    for line in lines[header_idx + 1 :]:
        row = next(csv.reader([line], delimiter=delim))
        if not any(cell.strip() for cell in row):
            continue
        sec = normalize_seccion(row[sec_i] if sec_i < len(row) else "")
        if not sec or sec not in leon_sections:
            continue
        pan = to_int(row[pan_i] if pan_i < len(row) else 0)
        total = to_int(row[total_i] if total_i < len(row) else 0)
        agg[sec]["pan"] += pan
        agg[sec]["total"] += total
        agg[sec]["rows"] += 1

    out_rows: list[dict[str, Any]] = []
    for sec in sorted(agg.keys(), key=lambda x: int(x)):
        pan = int(agg[sec]["pan"])
        total = int(agg[sec]["total"])
        out_rows.append(
            {
                "entidad": "11",
                "municipio": leon_municipio or None,
                "seccion": sec,
                "section_id": make_section_id("11", leon_municipio, sec),
                "pan_2021_votos": pan,
                "total_2021": total,
                "pct_pan_2021": to_pct(pan, total),
                "source_rows_2021": int(agg[sec]["rows"]),
            }
        )

    with OUT_2021.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "entidad",
                "municipio",
                "seccion",
                "section_id",
                "pan_2021_votos",
                "total_2021",
                "pct_pan_2021",
                "source_rows_2021",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "source_nested_zip": nested_dip,
        "source_votes_file": votes_file,
        "source_aux_file": aux_file,
        "rows_output": len(out_rows),
        "pan_total": sum(r["pan_2021_votos"] for r in out_rows),
        "votes_total": sum(r["total_2021"] for r in out_rows),
        "section_id_formula": source_formula,
    }
    return out_rows, summary


def load_geojson_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    rows: list[dict[str, Any]] = []
    for feat in features:
        props = feat.get("properties", {})
        rows.append(
            {
                "entidad": props.get("entidad"),
                "municipio": props.get("municipio"),
                "seccion": props.get("seccion"),
                "section_id": props.get("section_id"),
            }
        )
    return rows


def build_join_diagnostics(
    ine_rows: list[dict[str, Any]],
    edmslm_rows: list[dict[str, Any]],
    y2018_rows: list[dict[str, Any]],
    y2021_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ine_ids = {r["section_id"] for r in ine_rows if r.get("section_id")}
    ed_ids = {r["section_id"] for r in edmslm_rows if r.get("section_id")}
    y18_ids = {r["section_id"] for r in y2018_rows if r.get("section_id")}
    y21_ids = {r["section_id"] for r in y2021_rows if r.get("section_id")}
    all_ids = sorted(ine_ids | ed_ids | y18_ids | y21_ids, key=lambda x: int(x))

    out: list[dict[str, Any]] = []
    for sid in all_ids:
        in_ine = sid in ine_ids
        in_ed = sid in ed_ids
        in_2018 = sid in y18_ids
        in_2021 = sid in y21_ids

        if in_ine and in_ed and in_2018 and in_2021:
            status = "complete"
        elif in_ine and in_ed and (in_2018 or in_2021):
            status = "partial_electoral"
        elif in_ine and in_ed and not in_2018 and not in_2021:
            status = "no_electoral"
        elif (in_2018 or in_2021) and not in_ine and not in_ed:
            status = "electoral_without_reference"
        elif in_ine and not in_ed:
            status = "missing_edmslm"
        elif in_ed and not in_ine:
            status = "missing_ine_geometry"
        else:
            status = "mixed"

        issues: list[str] = []
        if not in_ine:
            issues.append("missing_ine_geometry")
        if not in_ed:
            issues.append("missing_edmslm")
        if not in_2018:
            issues.append("missing_2018")
        if not in_2021:
            issues.append("missing_2021")
        issue_type = ";".join(issues) if issues else "none"

        out.append(
            {
                "section_id": sid,
                "in_ine_geometry": in_ine,
                "in_edmslm": in_ed,
                "in_2018": in_2018,
                "in_2021": in_2021,
                "join_status": status,
                "issue_type": issue_type,
            }
        )

    with OUT_JOIN.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "section_id",
                "in_ine_geometry",
                "in_edmslm",
                "in_2018",
                "in_2021",
                "join_status",
                "issue_type",
            ],
        )
        writer.writeheader()
        writer.writerows(out)

    return out


def count_duplicates(rows: list[dict[str, Any]], key: str = "section_id") -> int:
    counts = Counter(r.get(key) for r in rows if r.get(key))
    return sum(1 for _, c in counts.items() if c > 1)


def count_nulls(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, int]:
    out = {f: 0 for f in fields}
    for row in rows:
        for f in fields:
            val = row.get(f)
            if val is None or str(val).strip() == "":
                out[f] += 1
    return out


def write_reports(
    ine_summary: dict[str, Any],
    edmslm_rows: list[dict[str, Any]],
    y2018_rows: list[dict[str, Any]],
    y2021_rows: list[dict[str, Any]],
    join_rows: list[dict[str, Any]],
    extra_warnings: list[str],
) -> str:
    generated_files = [
        str(OUT_INE_INDEX.relative_to(ROOT)),
        str(OUT_INE_LEON.relative_to(ROOT)),
        str(OUT_EDMSLM_LEON.relative_to(ROOT)),
        str(OUT_2018.relative_to(ROOT)),
        str(OUT_2021.relative_to(ROOT)),
        str(OUT_JOIN.relative_to(ROOT)),
    ]
    section_formula = "section_id = entidad(2) + municipio(3) + seccion(normalizada sin decimales)"
    status_counts = Counter(r["join_status"] for r in join_rows)

    duplicates = {
        "ine": count_duplicates(load_geojson_rows(OUT_INE_LEON)),
        "edmslm": count_duplicates(edmslm_rows),
        "ieeg_2018": count_duplicates(y2018_rows),
        "ieeg_2021": count_duplicates(y2021_rows),
    }
    nulls = {
        "edmslm": count_nulls(edmslm_rows, ["entidad", "municipio", "seccion", "section_id"]),
        "ieeg_2018": count_nulls(y2018_rows, ["entidad", "municipio", "seccion", "section_id", "pct_pan_2018"]),
        "ieeg_2021": count_nulls(y2021_rows, ["entidad", "municipio", "seccion", "section_id", "pct_pan_2021"]),
    }
    missing_2018 = sum(1 for r in join_rows if not r["in_2018"])
    missing_2021 = sum(1 for r in join_rows if not r["in_2021"])

    warnings = list(extra_warnings)
    if missing_2018 > 0:
        warnings.append(f"{missing_2018} section_id without 2018 electoral data.")
    if missing_2021 > 0:
        warnings.append(f"{missing_2021} section_id without 2021 electoral data.")
    if duplicates["ieeg_2018"] > 0 or duplicates["ieeg_2021"] > 0:
        warnings.append("Detected duplicate section_id in staged electoral outputs.")

    approved = (
        ine_summary.get("features_leon", 0) > 0
        and len(edmslm_rows) > 0
        and len(y2018_rows) > 0
        and len(y2021_rows) > 0
    )
    decision = "aprobado para Epica 2.3" if approved else "no aprobado para Epica 2.3"

    report_json = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_files": generated_files,
        "counts_by_source": {
            "ine_leon_sections": ine_summary.get("features_leon", 0),
            "edmslm_leon_sections": len(edmslm_rows),
            "ieeg_2018_sections": len(y2018_rows),
            "ieeg_2021_sections": len(y2021_rows),
        },
        "columns_normalized": {
            "ine_min": ["entidad", "municipio", "seccion", "section_id", "geometry"],
            "edmslm_min": ["entidad", "municipio", "municipio_nombre", "seccion", "section_id", "distrito_local", "distrito_federal"],
            "ieeg_2018_min": ["entidad", "municipio", "seccion", "section_id", "pan_2018_votos", "total_2018", "pct_pan_2018", "source_rows_2018"],
            "ieeg_2021_min": ["entidad", "municipio", "seccion", "section_id", "pan_2021_votos", "total_2021", "pct_pan_2021", "source_rows_2021"],
        },
        "section_id_formula": section_formula,
        "join_status_counts": dict(status_counts),
        "secciones_sin_match": {
            "missing_2018": missing_2018,
            "missing_2021": missing_2021,
        },
        "duplicates": duplicates,
        "nulls": nulls,
        "totals": {
            "pan_2018_total": sum(int(r["pan_2018_votos"]) for r in y2018_rows),
            "total_2018_total": sum(int(r["total_2018"]) for r in y2018_rows),
            "pan_2021_total": sum(int(r["pan_2021_votos"]) for r in y2021_rows),
            "total_2021_total": sum(int(r["total_2021"]) for r in y2021_rows),
        },
        "warnings": warnings,
        "decision": decision,
    }
    OUT_REPORT_JSON.write_text(json.dumps(report_json, ensure_ascii=True, indent=2), encoding="utf-8")

    md_lines: list[str] = []
    md_lines.append("# Interim Staging Report")
    md_lines.append("")
    md_lines.append("## Resumen")
    md_lines.append("")
    md_lines.append(f"- Fecha: `{report_json['generated_at']}`")
    md_lines.append(f"- Decision: `{decision}`")
    md_lines.append("")
    md_lines.append("## Archivos Generados")
    md_lines.append("")
    for path in generated_files:
        md_lines.append(f"- `{path}`")
    md_lines.append("")
    md_lines.append("## Conteos por Fuente")
    md_lines.append("")
    for key, val in report_json["counts_by_source"].items():
        md_lines.append(f"- {key}: `{val}`")
    md_lines.append("")
    md_lines.append("## Normalizacion")
    md_lines.append("")
    md_lines.append(f"- Formula section_id: `{section_formula}`")
    md_lines.append(f"- CRS INE detectado: `{ine_summary.get('crs_detected', '')}`")
    md_lines.append(f"- Capa INE: `{ine_summary.get('layer_path', '')}`")
    md_lines.append("")
    md_lines.append("## Join Diagnostics")
    md_lines.append("")
    for key, val in dict(status_counts).items():
        md_lines.append(f"- {key}: `{val}`")
    md_lines.append(f"- missing_2018: `{missing_2018}`")
    md_lines.append(f"- missing_2021: `{missing_2021}`")
    md_lines.append("")
    md_lines.append("## Duplicados y Nulos")
    md_lines.append("")
    md_lines.append(f"- Duplicados: `{json.dumps(duplicates, ensure_ascii=True)}`")
    md_lines.append(f"- Nulos: `{json.dumps(nulls, ensure_ascii=True)}`")
    md_lines.append("")
    md_lines.append("## Totales Electorales")
    md_lines.append("")
    md_lines.append(f"- PAN 2018 total: `{report_json['totals']['pan_2018_total']}`")
    md_lines.append(f"- Total votos 2018: `{report_json['totals']['total_2018_total']}`")
    md_lines.append(f"- PAN 2021 total: `{report_json['totals']['pan_2021_total']}`")
    md_lines.append(f"- Total votos 2021: `{report_json['totals']['total_2021_total']}`")
    md_lines.append("")
    md_lines.append("## Advertencias")
    md_lines.append("")
    if warnings:
        for w in warnings:
            md_lines.append(f"- {w}")
    else:
        md_lines.append("- None")
    md_lines.append("")
    OUT_REPORT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    return decision


def main() -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    formula = "section_id = entidad(2) + municipio(3) + seccion(normalizada sin decimales)"
    extra_warnings: list[str] = []

    edmslm_rows, leon_codes, edmslm_warning = detect_leon_from_edmslm()
    if edmslm_warning:
        extra_warnings.append(edmslm_warning)
    leon_municipio = sorted(leon_codes)[0]

    ine_rows, ine_summary = build_ine_interim(leon_codes)
    leon_sections = {r["seccion"] for r in ine_rows if r.get("seccion")}

    y2018_rows, _ = build_ieeg_2018(leon_sections, leon_municipio, formula)
    y2021_rows, y2021_summary = build_ieeg_2021(leon_sections, leon_municipio, formula)

    if not y2021_summary.get("source_aux_file"):
        extra_warnings.append("IEEG 2021 candidaturas auxiliary file not detected.")

    join_rows = build_join_diagnostics(ine_rows, edmslm_rows, y2018_rows, y2021_rows)
    decision = write_reports(ine_summary, edmslm_rows, y2018_rows, y2021_rows, join_rows, extra_warnings)

    print(f"[build-interim] Generated: {OUT_INE_INDEX}")
    print(f"[build-interim] Generated: {OUT_INE_LEON}")
    print(f"[build-interim] Generated: {OUT_EDMSLM_LEON}")
    print(f"[build-interim] Generated: {OUT_2018}")
    print(f"[build-interim] Generated: {OUT_2021}")
    print(f"[build-interim] Generated: {OUT_JOIN}")
    print(f"[build-interim] Report: {OUT_REPORT_MD}")
    print(f"[build-interim] Report: {OUT_REPORT_JSON}")
    print(f"[build-interim] Decision: {decision}")


if __name__ == "__main__":
    main()
