from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path


REQUIRED_RAW_DIRS = [
    Path("data/raw/ine"),
    Path("data/raw/ieeg/2018"),
    Path("data/raw/ieeg/2021"),
    Path("data/raw/inegi"),
    Path("data/raw/manual"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ext_of(path: Path) -> str:
    return path.suffix.lower() if path.suffix else "[no_extension]"


def is_effectively_empty(directory: Path) -> bool:
    # Considera vacio cuando no contiene archivos en ningun nivel.
    return not any(p.is_file() for p in directory.rglob("*"))


def build_report(root: Path) -> str:
    raw_root = root / "data" / "raw"
    report_lines: list[str] = []
    report_lines.append("# Raw File Inventory")
    report_lines.append("")
    report_lines.append(f"- Generated at: `{datetime.now().isoformat(timespec='seconds')}`")
    report_lines.append(f"- Raw root: `{raw_root}`")
    report_lines.append("")

    missing_required = [str(p) for p in REQUIRED_RAW_DIRS if not (root / p).exists()]
    if missing_required:
        report_lines.append("## Missing Required Folders")
        report_lines.append("")
        for folder in missing_required:
            report_lines.append(f"- `{folder}`")
        report_lines.append("")
    else:
        report_lines.append("## Missing Required Folders")
        report_lines.append("")
        report_lines.append("- None")
        report_lines.append("")

    if not raw_root.exists():
        report_lines.append("## Files")
        report_lines.append("")
        report_lines.append("- Raw root does not exist.")
        report_lines.append("")
        return "\n".join(report_lines)

    files = sorted([p for p in raw_root.rglob("*") if p.is_file()])
    report_lines.append("## Files")
    report_lines.append("")
    if files:
        for f in files:
            rel = f.relative_to(root)
            size = f.stat().st_size
            report_lines.append(f"- `{rel}` ({size} bytes)")
    else:
        report_lines.append("- No files found under `data/raw`.")
    report_lines.append("")

    ext_counter = Counter(ext_of(f) for f in files)
    report_lines.append("## Extensions Found")
    report_lines.append("")
    if ext_counter:
        for ext, count in sorted(ext_counter.items()):
            report_lines.append(f"- `{ext}`: {count}")
    else:
        report_lines.append("- None")
    report_lines.append("")

    all_dirs = sorted([d for d in raw_root.rglob("*") if d.is_dir()])
    empty_dirs = [d for d in all_dirs if is_effectively_empty(d)]
    report_lines.append("## Empty Folders")
    report_lines.append("")
    if empty_dirs:
        for d in empty_dirs:
            report_lines.append(f"- `{d.relative_to(root)}`")
    else:
        report_lines.append("- None")
    report_lines.append("")

    report_lines.append("## Warnings")
    report_lines.append("")
    warnings: list[str] = []
    if missing_required:
        warnings.append("Missing one or more required raw folders.")
    if not files:
        warnings.append("No raw files found; data intake not started.")
    if warnings:
        for warning in warnings:
            report_lines.append(f"- {warning}")
    else:
        report_lines.append("- None")
    report_lines.append("")

    return "\n".join(report_lines)


def main() -> None:
    root = project_root()
    report_dir = root / "reports" / "data_qa"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "raw_file_inventory.md"

    report_content = build_report(root)
    report_path.write_text(report_content, encoding="utf-8")

    print(f"[inspect-raw] Report written: {report_path}")


if __name__ == "__main__":
    main()
