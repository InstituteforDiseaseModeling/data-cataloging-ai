"""
generate_catalog.py

Reads catalog_draft.json from the current working directory and fills the
three catalog template files (Metadata.xlsx, DataBio.xlsx, DataDict.xlsx)
found alongside this script, producing three dataset-specific outputs:

    <Dataset>_Metadata.xlsx
    <Dataset>_DataBio.xlsx
    <Dataset>_DataDict.xlsx

Usage:
    python generate_catalog.py
    python generate_catalog.py --input path/to/catalog_draft.json
    python generate_catalog.py --input draft.json --output-dir out/
    python generate_catalog.py --only databio            # just DataBio.xlsx
    python generate_catalog.py --only metadata,datadict   # any subset
"""

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_METADATA = SCRIPT_DIR / "Metadata.xlsx"
TEMPLATE_DATABIO = SCRIPT_DIR / "DataBio.xlsx"
TEMPLATE_DATADICT = SCRIPT_DIR / "DataDict.xlsx"

REVIEW_FILL = PatternFill("solid", fgColor="FFE699")
SENSITIVE_FILL = PatternFill("solid", fgColor="FFB3B3")
ALT_FILL = PatternFill("solid", fgColor="F2F7FC")
THIN = Side(style="thin", color="BFBFBF")
THIN_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(wrap_text=True, vertical="top")

DATADICT_KEYS = [
    "file_name", "variable_name", "variable_label", "definition", "data_type",
    "unit", "allowed_values_codes", "missing_unknown_codes", "source_derivation",
    "numerator", "denominator", "sensitive", "data_quality_notes",
]


def _review_comment(entry, fallback="Needs human review before finalizing."):
    text = entry.get("review_notes") or fallback
    return Comment(text, "Catalog generator")


# ── Metadata.xlsx ───────────────────────────────────────────────────────────
def fill_metadata(data, output_dir, base_name):
    if not TEMPLATE_METADATA.exists():
        sys.exit(f"ERROR: template not found: {TEMPLATE_METADATA}")

    wb = load_workbook(TEMPLATE_METADATA)
    ws = wb["Metadata"]

    for i, entry in enumerate(data.get("metadata", [])):
        row = 4 + i
        cell = ws.cell(row=row, column=3, value=entry.get("value", ""))
        if entry.get("needs_review"):
            cell.fill = REVIEW_FILL
            cell.comment = _review_comment(entry)

    output_path = output_dir / f"{base_name}_Metadata.xlsx"
    wb.save(output_path)
    return output_path


# ── DataBio.xlsx (must preserve the Lists-sheet dropdown validation) ───────
def _sheet_xml_target(xlsx_path, sheet_title):
    with zipfile.ZipFile(xlsx_path) as z:
        wb_xml = z.read("xl/workbook.xml").decode("utf-8")
        rels_xml = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")

    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    wb_root = ET.fromstring(wb_xml)
    rid = None
    for sheet in wb_root.find("m:sheets", ns):
        if sheet.get("name") == sheet_title:
            rid = sheet.get(f"{{{ns['r']}}}id")
            break
    if rid is None:
        raise ValueError(f"Sheet {sheet_title!r} not found in {xlsx_path}")

    rels_root = ET.fromstring(rels_xml)
    for rel in rels_root:
        if rel.get("Id") == rid:
            target = rel.get("Target")
            # Target is normally relative to xl/ (e.g. "worksheets/sheet1.xml"),
            # but some writers emit a package-absolute path ("/xl/worksheets/sheet1.xml").
            return target[1:] if target.startswith("/") else f"xl/{target}"

    raise ValueError(f"Relationship {rid!r} not found in {xlsx_path}")


def _restore_data_validation(template_path, output_path, sheet_title="Data Bio"):
    """openpyxl drops the extLst (x14:dataValidation dropdowns) on save.
    Splice the original template's extLst and worksheet namespaces back into
    the saved output so the dropdowns survive."""
    template_sheet = _sheet_xml_target(template_path, sheet_title)
    with zipfile.ZipFile(template_path) as tz:
        template_xml = tz.read(template_sheet).decode("utf-8")

    ext_match = re.search(r"<extLst>.*</extLst>", template_xml, re.DOTALL)
    if not ext_match:
        return  # template has no data validation to preserve

    root_match = re.search(r"<worksheet[^>]*>", template_xml)
    template_root_elem = root_match.group(0)
    ext_block = ext_match.group(0)

    output_sheet = _sheet_xml_target(output_path, sheet_title)
    with zipfile.ZipFile(output_path) as oz:
        entries = {name: oz.read(name) for name in oz.namelist()}

    output_xml = entries[output_sheet].decode("utf-8")
    output_xml = re.sub(r"<worksheet[^>]*>", template_root_elem, output_xml, count=1)
    output_xml = output_xml.replace("</worksheet>", f"{ext_block}</worksheet>")
    entries[output_sheet] = output_xml.encode("utf-8")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as oz:
        for name, content in entries.items():
            oz.writestr(name, content)


def fill_databio(data, output_dir, base_name):
    import shutil

    if not TEMPLATE_DATABIO.exists():
        sys.exit(f"ERROR: template not found: {TEMPLATE_DATABIO}")

    output_path = output_dir / f"{base_name}_DataBio.xlsx"
    shutil.copy(TEMPLATE_DATABIO, output_path)

    wb = load_workbook(output_path)
    ws = wb["Data Bio"]

    for i, entry in enumerate(data.get("data_bio", [])):
        row = 3 + i
        answer_cell = ws.cell(row=row, column=4, value=entry.get("response", ""))

        notes = f"Source: {entry.get('source', '')}" if entry.get("source") else ""
        if entry.get("needs_review"):
            flag = entry.get("review_notes") or "Needs human review."
            notes = f"⚠ Needs review — {flag}\n{notes}".strip()
            answer_cell.fill = REVIEW_FILL
            answer_cell.comment = _review_comment(entry)
        ws.cell(row=row, column=5, value=notes)

    wb.save(output_path)
    _restore_data_validation(TEMPLATE_DATABIO, output_path)
    return output_path


# ── DataDict.xlsx ────────────────────────────────────────────────────────────
def fill_datadict(data, output_dir, base_name):
    if not TEMPLATE_DATADICT.exists():
        sys.exit(f"ERROR: template not found: {TEMPLATE_DATADICT}")

    wb = load_workbook(TEMPLATE_DATADICT)
    ws = wb["Sheet1"]

    variables = data.get("variables", [])
    for i, entry in enumerate(variables):
        row = 2 + i
        alt = (i % 2 == 1)
        for col, key in enumerate(DATADICT_KEYS, 1):
            cell = ws.cell(row=row, column=col, value=entry.get(key, ""))
            cell.border = THIN_BORDER
            cell.alignment = WRAP_TOP
            if alt:
                cell.fill = ALT_FILL

        if entry.get("sensitive"):
            sensitive_cell = ws.cell(row=row, column=12)
            sensitive_cell.fill = SENSITIVE_FILL
            sensitive_cell.font = Font(bold=True)

        if entry.get("needs_review"):
            name_cell = ws.cell(row=row, column=2)
            name_cell.fill = REVIEW_FILL
            name_cell.comment = _review_comment(entry)

    ws.freeze_panes = "A2"
    if variables:
        ws.auto_filter.ref = f"A1:M{len(variables) + 1}"

    output_path = output_dir / f"{base_name}_DataDict.xlsx"
    wb.save(output_path)
    return output_path


ALL_TARGETS = ("metadata", "databio", "datadict")


def main():
    args = sys.argv[1:]
    input_path = "catalog_draft.json"
    output_dir = Path.cwd()
    targets = list(ALL_TARGETS)

    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = Path(args[i + 1])
            i += 2
        elif args[i] == "--only" and i + 1 < len(args):
            targets = [t.strip().lower() for t in args[i + 1].split(",")]
            unknown = [t for t in targets if t not in ALL_TARGETS]
            if unknown:
                sys.exit(f"ERROR: unknown --only target(s) {unknown}; choose from {ALL_TARGETS}")
            i += 2
        else:
            i += 1

    if not Path(input_path).exists():
        sys.exit(f"ERROR: {input_path} not found. Run the catalog-dataset skill first to generate it.")

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = data.get("dataset_name", "Dataset").replace(" ", "_")

    fillers = {
        "metadata": ("Metadata", fill_metadata),
        "databio": ("DataBio", fill_databio),
        "datadict": ("DataDict", fill_datadict),
    }
    for target in targets:
        label, fill_fn = fillers[target]
        path = fill_fn(data, output_dir, base_name)
        print(f"{label} saved: {path.resolve()}")


if __name__ == "__main__":
    main()
