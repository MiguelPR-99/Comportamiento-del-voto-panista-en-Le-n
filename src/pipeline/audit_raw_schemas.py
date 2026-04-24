from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence
from xml.etree import ElementTree as ET
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports" / "data_qa"
REPORT_MD = REPORT_DIR / "raw_schema_audit.md"
REPORT_JSON = REPORT_DIR / "raw_schema_audit.json"
INVENTORY_CSV = RAW_DIR / "data_inventory.csv"


@dataclass
class AuditItem:
    file: str
    status: str
    detected_format: str
    row_count_sampled: int | None
    columns: list[str] = field(default_factory=list)
    key_candidates: dict[str, list[str]] = field(default_factory=dict)
    vote_candidates: dict[str, list[str]] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    details: dict[str, object] = field(default_factory=dict)


def normalize(text: str) -> str:
    txt = unicodedata.normalize("NFKD", text)
    txt = txt.encode("ascii", "ignore").decode("ascii")
    txt = txt.lower().strip()
    txt = re.sub(r"[^a-z0-9]+", "_", txt)
    return txt.strip("_")


def detect_encoding_from_bytes(sample: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            sample.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"


def detect_delimiter_from_text(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()][:20]
    if not lines:
        return ","
    joined = "\n".join(lines)
    try:
        dialect = csv.Sniffer().sniff(joined, delimiters=",;|\t")
        return dialect.delimiter
    except csv.Error:
        counts = {d: joined.count(d) for d in [",", ";", "|", "\t"]}
        return max(counts, key=counts.get)


def norm_path(path: str) -> str:
    return path.replace("\\", "/").lower()


def key_candidates(columns: Sequence[str]) -> dict[str, list[str]]:
    mapped = {"entidad": [], "municipio": [], "seccion": [], "distrito_local": [], "municipio_nombre": [], "casilla": []}
    for col in columns:
        n = normalize(col)
        if any(tok in n for tok in ("entidad", "cve_ent", "id_estado", "estado_id")):
            mapped["entidad"].append(col)
        if any(tok in n for tok in ("municipio", "cve_mun", "id_municipio")):
            mapped["municipio"].append(col)
        if any(tok in n for tok in ("seccion", "cve_secc", "sec_elec")):
            mapped["seccion"].append(col)
        if any(tok in n for tok in ("distrito_local", "distrito", "id_distrito_local")):
            mapped["distrito_local"].append(col)
        if any(tok in n for tok in ("nombre_municipio", "nom_mun", "municipio_nombre")):
            mapped["municipio_nombre"].append(col)
        if "casilla" in n or "id_casilla" in n or "clave_casilla" in n:
            mapped["casilla"].append(col)
    return mapped


def vote_candidates(columns: Sequence[str]) -> dict[str, list[str]]:
    mapped = {"pan": [], "total_votos": []}
    for col in columns:
        n = normalize(col)
        if n == "pan" or n.endswith("_pan") or "_pan_" in n:
            mapped["pan"].append(col)
        if any(tok in n for tok in ("total_votos", "votacion_total", "total_votacion", "total")):
            mapped["total_votos"].append(col)
    return mapped


def parse_dbf_header(dbf_bytes: bytes) -> tuple[int | None, list[str]]:
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


def inspect_ine_zip(path: Path) -> AuditItem:
    item = AuditItem(file=str(path.relative_to(ROOT)), status="ok", detected_format="zip", row_count_sampled=None)
    if not path.exists():
        item.status = "error"
        item.issues.append("File not found")
        return item

    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        item.details["internal_files"] = names
        shp_files = [n for n in names if n.lower().endswith(".shp")]
        item.details["shp_layers"] = shp_files
        has_7z = any(n.lower().endswith(".7z") for n in names)
        if has_7z:
            item.issues.append("ZIP contains nested .7z; shapefile schema cannot be read without extraction support.")
        if not shp_files:
            item.issues.append("No .shp layer found directly inside ZIP.")

        gpd = None
        try:
            import geopandas as _gpd  # type: ignore

            gpd = _gpd
        except Exception:
            gpd = None

        if shp_files and gpd is not None:
            layer = shp_files[0]
            try:
                uri = f"zip://{path.as_posix()}!{layer}"
                gdf = gpd.read_file(uri)
                item.row_count_sampled = int(len(gdf))
                item.columns = [str(c) for c in gdf.columns]
                item.key_candidates = key_candidates(item.columns)
                item.vote_candidates = vote_candidates(item.columns)
                item.details["crs"] = str(gdf.crs) if gdf.crs is not None else None
            except Exception as exc:
                item.issues.append(f"Could not read shp with geopandas: {exc}")
        elif shp_files:
            dbf_by_base = {}
            prj_by_base = {}
            for n in names:
                low = n.lower()
                base = re.sub(r"\.[^.]+$", "", low)
                if low.endswith(".dbf"):
                    dbf_by_base[base] = n
                if low.endswith(".prj"):
                    prj_by_base[base] = n
            layer = shp_files[0]
            base = re.sub(r"\.[^.]+$", "", layer.lower())
            dbf_name = dbf_by_base.get(base)
            if dbf_name:
                dbf_bytes = zf.read(dbf_name)
                row_count, fields = parse_dbf_header(dbf_bytes)
                item.row_count_sampled = row_count
                item.columns = fields
                item.key_candidates = key_candidates(fields)
                item.vote_candidates = vote_candidates(fields)
            else:
                item.issues.append("No .dbf file found for detected .shp layer.")
            prj_name = prj_by_base.get(base)
            if prj_name:
                enc = detect_encoding_from_bytes(zf.read(prj_name)[:4000])
                prj_text = zf.read(prj_name).decode(enc, errors="replace")
                item.details["crs"] = prj_text[:400].strip()
            else:
                item.details["crs"] = None

    if not item.columns:
        item.status = "needs_review"
    item.details["section_layer_detected"] = bool(item.key_candidates.get("seccion"))
    return item


def inspect_text_file(path: Path, max_sample_rows: int = 30, max_scan_rows: int = 2_000_000) -> AuditItem:
    item = AuditItem(file=str(path.relative_to(ROOT)), status="ok", detected_format="txt", row_count_sampled=0)
    if not path.exists():
        item.status = "error"
        item.issues.append("File not found")
        return item

    with path.open("rb") as fh:
        sample = fh.read(200_000)
    enc = detect_encoding_from_bytes(sample)
    txt = sample.decode(enc, errors="replace")
    delim = detect_delimiter_from_text(txt)
    item.details["encoding"] = enc
    item.details["delimiter"] = delim

    found_gto = False
    header: list[str] | None = None
    sampled_rows = 0
    scanned_rows = 0
    sample_preview: list[list[str]] = []

    with path.open("r", encoding=enc, errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter=delim)
        for row in reader:
            if not row:
                continue
            scanned_rows += 1
            if header is None:
                header = [c.strip() for c in row]
                item.columns = header
                item.key_candidates = key_candidates(item.columns)
                item.vote_candidates = vote_candidates(item.columns)
                continue
            if sampled_rows < max_sample_rows:
                sampled_rows += 1
                if len(sample_preview) < 5:
                    sample_preview.append(row[:20])
            if header:
                idx_ent = next((i for i, c in enumerate(header) if normalize(c) in ("entidad", "id_estado", "cve_ent")), None)
                idx_nom = next((i for i, c in enumerate(header) if "municipio" in normalize(c) and "nombre" in normalize(c)), None)
                if idx_ent is not None and idx_ent < len(row):
                    if row[idx_ent].strip() in ("11", "011"):
                        found_gto = True
                        break
                if idx_nom is not None and idx_nom < len(row):
                    if "guanajuato" in normalize(row[idx_nom]):
                        found_gto = True
                        break
            if scanned_rows >= max_scan_rows:
                item.issues.append("Max scan rows reached before confirming Guanajuato.")
                break

    item.row_count_sampled = sampled_rows
    item.details["contains_entity_11_or_guanajuato"] = found_gto
    item.details["rows_scanned"] = scanned_rows
    item.details["sample_rows_preview"] = sample_preview
    if not found_gto:
        item.issues.append("Could not confirm presence of entity 11/Guanajuato within scanned rows.")
    if not item.columns:
        item.status = "needs_review"
        item.issues.append("Header not detected.")
    return item


def xlsx_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    data = zf.read(name)
    root = ET.fromstring(data)
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    out = []
    for si in root.findall(".//x:si", ns):
        texts = [t.text or "" for t in si.findall(".//x:t", ns)]
        out.append("".join(texts))
    return out


def xlsx_sheet_map(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    ns_w = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ns_r = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    rel_map = {}
    for rel in rels.findall(".//r:Relationship", ns_r):
        rel_map[rel.attrib.get("Id", "")] = rel.attrib.get("Target", "")
    result = []
    for sheet in wb.findall(".//x:sheets/x:sheet", ns_w):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
        target = rel_map.get(rid, "")
        if target and not target.startswith("xl/"):
            target = f"xl/{target}"
        result.append((name, target))
    return result


def col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return max(idx - 1, 0)


def read_xlsx_rows(zf: zipfile.ZipFile, sheet_path: str, shared: Sequence[str], max_rows: int = 80) -> list[list[str]]:
    if sheet_path not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(sheet_path))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        cells: dict[int, str] = {}
        for c in row.findall("x:c", ns):
            ref = c.attrib.get("r", "")
            i = col_index(ref) if ref else len(cells)
            t = c.attrib.get("t", "")
            v = c.find("x:v", ns)
            value = ""
            if t == "s" and v is not None and v.text and v.text.isdigit():
                idx = int(v.text)
                if 0 <= idx < len(shared):
                    value = shared[idx]
            elif t == "inlineStr":
                tnode = c.find("x:is/x:t", ns)
                value = tnode.text if tnode is not None and tnode.text else ""
            elif v is not None and v.text is not None:
                value = v.text
            cells[i] = value.strip()
        if cells:
            max_idx = max(cells)
            row_vals = [cells.get(i, "") for i in range(max_idx + 1)]
            rows.append(row_vals)
        if len(rows) >= max_rows:
            break
    return rows


def pick_header(rows: Sequence[Sequence[str]]) -> tuple[int | None, list[str]]:
    best_idx = None
    best_score = -1
    best_cols: list[str] = []
    tokens = ("seccion", "casilla", "distrito", "municipio", "pan", "total", "votos")
    for i, row in enumerate(rows):
        cols = [str(c).strip() for c in row if str(c).strip()]
        if not cols:
            continue
        score = len(cols)
        for c in cols:
            n = normalize(c)
            if any(tok in n for tok in tokens):
                score += 2
        if score > best_score:
            best_score = score
            best_idx = i
            best_cols = [str(c).strip() for c in row]
    if best_idx is None:
        return None, []
    while best_cols and not best_cols[-1]:
        best_cols.pop()
    return best_idx, best_cols


def inspect_xlsx(path: Path, label: str | None = None) -> AuditItem:
    rel_path = label if label else str(path.relative_to(ROOT))
    item = AuditItem(file=rel_path, status="ok", detected_format="xlsx", row_count_sampled=0)
    if not path.exists():
        item.status = "error"
        item.issues.append("File not found")
        return item
    try:
        with zipfile.ZipFile(path) as zf:
            sheets = xlsx_sheet_map(zf)
            item.details["sheets"] = [s[0] for s in sheets]
            shared = xlsx_shared_strings(zf)
            relevant: list[dict[str, object]] = []
            sampled_total = 0
            for sheet_name, sheet_path in sheets:
                rows = read_xlsx_rows(zf, sheet_path, shared)
                if not rows:
                    continue
                hidx, cols = pick_header(rows)
                if hidx is None or not cols:
                    continue
                data_rows = [r for r in rows[hidx + 1 :] if any(str(c).strip() for c in r)]
                sampled_total += len(data_rows)
                k = key_candidates(cols)
                v = vote_candidates(cols)
                sheet_info = {
                    "sheet": sheet_name,
                    "columns": cols,
                    "key_candidates": k,
                    "vote_candidates": v,
                    "row_count_sampled": len(data_rows),
                    "granularity": "casilla" if k.get("casilla") else ("seccion" if k.get("seccion") else "unknown"),
                    "is_diputaciones_candidate": "dip" in normalize(sheet_name)
                    or any("dip" in normalize(c) for c in cols),
                }
                relevant.append(sheet_info)
            item.details["sheet_summaries"] = relevant
            item.row_count_sampled = sampled_total
            if relevant:
                chosen = [s for s in relevant if s["is_diputaciones_candidate"]]
                source = chosen if chosen else relevant
                item.details["contains_diputaciones_data"] = bool(chosen)
                all_cols = []
                for s in source:
                    all_cols.extend(s["columns"])
                uniq_cols = list(dict.fromkeys([c for c in all_cols if c]))
                item.columns = uniq_cols
                item.key_candidates = key_candidates(item.columns)
                item.vote_candidates = vote_candidates(item.columns)
                item.details["data_granularity_detected"] = (
                    "casilla"
                    if any(s["granularity"] == "casilla" for s in source)
                    else ("seccion" if any(s["granularity"] == "seccion" for s in source) else "unknown")
                )
            else:
                item.status = "needs_review"
                item.issues.append("No readable sheets with detectable headers.")
    except Exception as exc:
        item.status = "needs_review"
        item.issues.append(f"Could not inspect XLSX: {exc}")
    return item


def detect_header_from_lines(lines: Sequence[str], delimiter: str) -> tuple[int | None, list[str]]:
    tokens = ("seccion", "casilla", "distrito", "municipio", "pan", "total", "votos", "id_")
    fallback_idx = None
    fallback_cols: list[str] = []
    for i, line in enumerate(lines):
        row = next(csv.reader([line], delimiter=delimiter))
        cols = [c.strip() for c in row]
        non_empty = [c for c in cols if c]
        if len(non_empty) < 3:
            continue
        if fallback_idx is None:
            fallback_idx, fallback_cols = i, cols
        normalized = [normalize(c) for c in non_empty]
        token_hits = sum(1 for n in normalized if any(tok in n for tok in tokens))
        alpha_like = sum(1 for c in non_empty if any(ch.isalpha() for ch in c))
        mostly_numeric = sum(1 for c in non_empty if re.fullmatch(r"[\d\.'\-]+", c or "") is not None)
        # Header heuristic: enough semantic tokens, mostly textual, not mostly numeric.
        if token_hits >= 2 and alpha_like >= max(2, len(non_empty) // 2) and mostly_numeric < len(non_empty) // 2:
            while cols and not cols[-1]:
                cols.pop()
            return i, cols
    if fallback_idx is not None:
        while fallback_cols and not fallback_cols[-1]:
            fallback_cols.pop()
        return fallback_idx, fallback_cols
    return None, []


def inspect_csv_bytes(data: bytes, label: str) -> AuditItem:
    enc = detect_encoding_from_bytes(data[:120_000])
    text = data.decode(enc, errors="replace")
    lines = text.splitlines()
    sample_lines = lines[:120]
    delim = detect_delimiter_from_text("\n".join(sample_lines))

    item = AuditItem(file=label, status="ok", detected_format=f"csv ({enc}, '{delim}')", row_count_sampled=0)
    hidx, cols = detect_header_from_lines(sample_lines, delim)
    if hidx is None:
        item.status = "needs_review"
        item.issues.append("Could not detect header row in CSV sample.")
        return item
    item.columns = cols
    item.key_candidates = key_candidates(cols)
    item.vote_candidates = vote_candidates(cols)

    data_rows = 0
    for line in lines[hidx + 1 :]:
        row = next(csv.reader([line], delimiter=delim))
        if any(c.strip() for c in row):
            data_rows += 1
        if data_rows >= 2000:
            break
    item.row_count_sampled = data_rows
    item.details["header_row_index"] = hidx + 1
    item.details["data_granularity_detected"] = (
        "casilla"
        if item.key_candidates.get("casilla")
        else ("seccion" if item.key_candidates.get("seccion") else "unknown")
    )
    return item


def inspect_xlsx_from_bytes(data: bytes, label: str) -> AuditItem:
    item = AuditItem(file=label, status="ok", detected_format="xlsx", row_count_sampled=0)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            sheets = xlsx_sheet_map(zf)
            item.details["sheets"] = [s[0] for s in sheets]
            shared = xlsx_shared_strings(zf)
            summaries = []
            sampled = 0
            for sheet_name, sheet_path in sheets:
                rows = read_xlsx_rows(zf, sheet_path, shared)
                if not rows:
                    continue
                hidx, cols = pick_header(rows)
                if hidx is None:
                    continue
                data_rows = [r for r in rows[hidx + 1 :] if any(str(c).strip() for c in r)]
                sampled += len(data_rows)
                summaries.append(
                    {
                        "sheet": sheet_name,
                        "columns": cols,
                        "granularity": "casilla" if key_candidates(cols).get("casilla") else "seccion",
                        "is_diputaciones_candidate": "dip" in normalize(sheet_name)
                        or any("dip" in normalize(c) for c in cols),
                    }
                )
            item.details["sheet_summaries"] = summaries
            item.row_count_sampled = sampled
            if summaries:
                src = [s for s in summaries if s["is_diputaciones_candidate"]] or summaries
                item.details["contains_diputaciones_data"] = any(s["is_diputaciones_candidate"] for s in summaries)
                cols = list(dict.fromkeys([c for s in src for c in s["columns"] if c]))
                item.columns = cols
                item.key_candidates = key_candidates(cols)
                item.vote_candidates = vote_candidates(cols)
                item.details["data_granularity_detected"] = (
                    "casilla" if any(s["granularity"] == "casilla" for s in src) else "seccion"
                )
            else:
                item.status = "needs_review"
                item.issues.append("No readable worksheets found.")
    except Exception as exc:
        item.status = "needs_review"
        item.issues.append(f"Could not inspect XLSX bytes: {exc}")
    return item


def inspect_ieeg_2021_zip(path: Path) -> list[AuditItem]:
    results: list[AuditItem] = []
    top = AuditItem(file=str(path.relative_to(ROOT)), status="ok", detected_format="zip", row_count_sampled=None)
    if not path.exists():
        top.status = "error"
        top.issues.append("File not found")
        return [top]
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        top.details["internal_files"] = names
        results.append(top)
        relevant_outer = [n for n in names if "dip" in normalize(n) and "ayun" not in normalize(n)]
        if not relevant_outer:
            top.status = "needs_review"
            top.issues.append("No diputaciones-locales file found in outer ZIP.")
            return results
        for outer_name in relevant_outer:
            if outer_name.lower().endswith(".zip"):
                nested_bytes = zf.read(outer_name)
                with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nz:
                    nested_names = nz.namelist()
                    results.append(
                        AuditItem(
                            file=f"{path.relative_to(ROOT)}::{outer_name}",
                            status="ok",
                            detected_format="nested zip",
                            row_count_sampled=None,
                            details={"internal_files": nested_names},
                        )
                    )
                    for nn in nested_names:
                        nlow = normalize(nn)
                        if "ayun" in nlow:
                            continue
                        if nn.lower().endswith(".csv"):
                            results.append(inspect_csv_bytes(nz.read(nn), f"{path.relative_to(ROOT)}::{outer_name}::{nn}"))
                        elif nn.lower().endswith(".xlsx"):
                            results.append(
                                inspect_xlsx_from_bytes(nz.read(nn), f"{path.relative_to(ROOT)}::{outer_name}::{nn}")
                            )
            elif outer_name.lower().endswith(".csv"):
                results.append(inspect_csv_bytes(zf.read(outer_name), f"{path.relative_to(ROOT)}::{outer_name}"))
            elif outer_name.lower().endswith(".xlsx"):
                results.append(inspect_xlsx_from_bytes(zf.read(outer_name), f"{path.relative_to(ROOT)}::{outer_name}"))
    return results


def inspect_csv_file(path: Path) -> AuditItem:
    item = AuditItem(file=str(path.relative_to(ROOT)), status="ok", detected_format="csv", row_count_sampled=0)
    if not path.exists():
        item.status = "error"
        item.issues.append("File not found")
        return item
    sample = path.read_bytes()[:150_000]
    enc = detect_encoding_from_bytes(sample)
    text = sample.decode(enc, errors="replace")
    delim = detect_delimiter_from_text(text)
    with path.open("r", encoding=enc, errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter=delim)
        first_row = next(reader, None)
        if first_row is None:
            item.status = "needs_review"
            item.issues.append("CSV is empty.")
            return item
        item.columns = [c.strip() for c in first_row]
        sampled = 0
        for row in reader:
            if any(str(c).strip() for c in row):
                sampled += 1
            if sampled >= 200:
                break
    item.key_candidates = key_candidates(item.columns)
    item.vote_candidates = vote_candidates(item.columns)
    item.row_count_sampled = sampled
    item.details["encoding"] = enc
    item.details["delimiter"] = delim
    return item


def summarize_for_markdown(items: Sequence[AuditItem]) -> tuple[list[str], list[str], list[str], str]:
    blockers: list[str] = []
    risks: list[str] = []
    findings: list[str] = []

    ine_item = next((i for i in items if norm_path(i.file).endswith("data/raw/ine/bgd_11_shapefile.zip")), None)
    if ine_item:
        if not ine_item.details.get("section_layer_detected"):
            blockers.append("No se pudo confirmar capa de secciones en el ZIP INE (contiene .7z interno sin extraccion).")
        if ine_item.issues:
            risks.extend([f"INE ZIP: {m}" for m in ine_item.issues])

    txt_item = next((i for i in items if norm_path(i.file).endswith("data/raw/ine/edmslm_ine_corte_ene_2026.txt")), None)
    if txt_item:
        if not txt_item.details.get("contains_entity_11_or_guanajuato"):
            blockers.append("No se confirmo presencia de entidad 11/Guanajuato en EDMSLM escaneado.")
        findings.append(
            f"EDMSLM detectado con delimiter `{txt_item.details.get('delimiter')}` y encoding `{txt_item.details.get('encoding')}`."
        )

    x2018 = [i for i in items if "computo x casillas diputaciones.xlsx" in norm_path(i.file)]
    if x2018:
        i = x2018[0]
        gran = i.details.get("data_granularity_detected", "unknown")
        findings.append(f"IEEG 2018 detectado con granularidad `{gran}`.")
        if gran == "unknown":
            blockers.append("No se pudo determinar granularidad de IEEG 2018 (casilla/seccion).")
        if not i.key_candidates.get("municipio"):
            risks.append("IEEG 2018 no muestra campo municipio explicito en esquema detectado.")

    x2021 = [i for i in items if "gto_dip_loc_2021.csv" in norm_path(i.file)]
    if x2021:
        i = x2021[0]
        gran = i.details.get("data_granularity_detected", "unknown")
        findings.append(f"IEEG 2021 diputaciones detectado con granularidad `{gran}`.")
        if gran == "unknown":
            blockers.append("No se pudo determinar granularidad de IEEG 2021.")
        if not i.key_candidates.get("municipio"):
            risks.append("IEEG 2021 no muestra campo municipio explicito; se requerira derivacion via seccion/cartografia.")
    else:
        blockers.append("No se encontro archivo interno de resultados de diputaciones 2021 en el ZIP.")

    decision = "no aprobado para Epica 2.2" if blockers else "aprobado para Epica 2.2"
    return findings, risks, blockers, decision


def write_markdown(items: Sequence[AuditItem]) -> None:
    findings, risks, blockers, decision = summarize_for_markdown(items)
    lines: list[str] = []
    lines.append("# Raw Schema Audit")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append("")
    lines.append(f"- Fecha: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Decision: `{decision}`")
    lines.append("")
    if findings:
        lines.append("- Hallazgos clave:")
        for f in findings:
            lines.append(f"- {f}")
        lines.append("")

    lines.append("## Archivos Inspeccionados")
    lines.append("")
    for it in items:
        lines.append(f"- `{it.file}` -> status: `{it.status}`, format: `{it.detected_format}`")
    lines.append("")

    lines.append("## Esquemas Detectados")
    lines.append("")
    for it in items:
        if not it.columns:
            if it.details.get("internal_files"):
                lines.append(f"### `{it.file}`")
                lines.append("")
                lines.append(f"- Internal files: `{json.dumps(it.details.get('internal_files'), ensure_ascii=True)}`")
                if it.details.get("shp_layers") is not None:
                    lines.append(f"- Shp layers detected: `{json.dumps(it.details.get('shp_layers'), ensure_ascii=True)}`")
                if it.issues:
                    lines.append(f"- Issues: `{json.dumps(it.issues, ensure_ascii=True)}`")
                lines.append("")
            continue
        lines.append(f"### `{it.file}`")
        lines.append("")
        lines.append(f"- Columnas ({len(it.columns)}): {', '.join(it.columns)}")
        if it.details.get("sheets"):
            lines.append(f"- Hojas detectadas: `{json.dumps(it.details.get('sheets'), ensure_ascii=True)}`")
        if it.details.get("contains_diputaciones_data") is not None:
            lines.append(f"- Contiene datos de diputaciones: `{it.details.get('contains_diputaciones_data')}`")
        if it.details.get("internal_files"):
            lines.append(f"- Internal files: `{json.dumps(it.details.get('internal_files'), ensure_ascii=True)}`")
        if it.details.get("contains_entity_11_or_guanajuato") is not None:
            lines.append(f"- Contiene entidad 11/Guanajuato: `{it.details.get('contains_entity_11_or_guanajuato')}`")
        if it.details.get("sample_rows_preview"):
            lines.append(f"- Primeras filas (preview): `{json.dumps(it.details.get('sample_rows_preview'), ensure_ascii=True)}`")
        if it.details.get("crs") is not None:
            lines.append(f"- CRS reportado: `{it.details.get('crs')}`")
        if it.key_candidates:
            lines.append(f"- Key candidates: `{json.dumps(it.key_candidates, ensure_ascii=True)}`")
        if it.vote_candidates:
            lines.append(f"- Vote candidates: `{json.dumps(it.vote_candidates, ensure_ascii=True)}`")
        if it.details.get("data_granularity_detected"):
            lines.append(f"- Granularidad detectada: `{it.details['data_granularity_detected']}`")
        lines.append("")

    lines.append("## Riesgos")
    lines.append("")
    if risks:
        for r in risks:
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

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_json(items: Sequence[AuditItem]) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "results": [
            {
                "file": i.file,
                "status": i.status,
                "detected_format": i.detected_format,
                "row_count_sampled": i.row_count_sampled,
                "columns": i.columns,
                "key_candidates": i.key_candidates,
                "vote_candidates": i.vote_candidates,
                "issues": i.issues,
            }
            for i in items
        ],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def update_inventory(items: Sequence[AuditItem]) -> None:
    if not INVENTORY_CSV.exists():
        return
    rows = list(csv.DictReader(INVENTORY_CSV.read_text(encoding="utf-8").splitlines()))
    if not rows:
        return

    status_by_filename: dict[str, tuple[str, str]] = {}
    for it in items:
        filename = Path(it.file.split("::")[-1]).name
        if filename:
            if it.status == "ok":
                new_status = "inspected"
            elif it.status == "needs_review":
                new_status = "needs_review"
            else:
                new_status = "rejected"
            note = "Schema audit completed." if it.status == "ok" else "; ".join(it.issues[:2])
            status_by_filename[filename] = (new_status, note)

    fieldnames = rows[0].keys()
    for row in rows:
        actual = (row.get("actual_filename") or "").strip()
        if not actual:
            continue
        if actual in status_by_filename:
            new_status, note = status_by_filename[actual]
            current = (row.get("acquisition_status") or "").strip().lower()
            if current in ("downloaded", "inspected", "needs_review", "rejected"):
                row["acquisition_status"] = new_status
                old_notes = row.get("notes", "").strip()
                if note and note not in old_notes:
                    row["notes"] = (old_notes + " | " + note).strip(" |")

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    INVENTORY_CSV.write_text(out.getvalue(), encoding="utf-8", newline="")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    items: list[AuditItem] = []
    ine_zip = RAW_DIR / "ine" / "bgd_11_Shapefile.zip"
    edmslm_txt = RAW_DIR / "ine" / "edmslm_ine_corte_ene_2026.txt"
    ieeg_2018_xlsx = RAW_DIR / "ieeg" / "2018" / "Computo x casillas Diputaciones.xlsx"
    ieeg_2021_zip = RAW_DIR / "ieeg" / "2021" / "computos_ieeg_2021_diputaciones_base_datos.zip"
    manifest_csv = RAW_DIR / "manual" / "fuentes-manifest.csv"

    items.append(inspect_ine_zip(ine_zip))
    items.append(inspect_text_file(edmslm_txt))
    items.append(inspect_xlsx(ieeg_2018_xlsx))
    items.extend(inspect_ieeg_2021_zip(ieeg_2021_zip))
    items.append(inspect_csv_file(manifest_csv))
    items.append(inspect_csv_file(INVENTORY_CSV))

    write_markdown(items)
    write_json(items)
    update_inventory(items)

    print(f"[audit-raw-schemas] Markdown report: {REPORT_MD}")
    print(f"[audit-raw-schemas] JSON report: {REPORT_JSON}")
    print(f"[audit-raw-schemas] Inventory updated: {INVENTORY_CSV}")


if __name__ == "__main__":
    main()
