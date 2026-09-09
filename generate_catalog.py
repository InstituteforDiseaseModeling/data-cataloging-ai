"""
generate_catalog.py

Reads catalog_draft.json from the current working directory and fills the
catalog template files -- DataProfile.xlsx (sheets: "Metadata" and "DataBio")
and DataDict.xlsx -- producing dataset-specific outputs:

    <Dataset>_DataProfile.xlsx
    <Dataset>_DataDict.xlsx

Templates and outputs both live in a SharePoint "Data Profiles" library,
synced locally via OneDrive so this script can read/write them like any
other local files -- no upload/download step, no API credentials. The two
paths involved (the synced _Templates_ folder and the synced Data Profiles
root) are resolved from a small local config file rather than hardcoded,
since every researcher's OneDrive sync path is different:

    {CLAUDE_PLUGIN_DATA}/cataloging_config.json   (when running as an
                                                    installed plugin)
    {this script's folder}/cataloging_config.json (local-dev fallback,
                                                    when CLAUDE_PLUGIN_DATA
                                                    isn't set)

That file is never checked into git -- it's written once per machine by
--set-data-profiles-root and persists across plugin updates (CLAUDE_PLUGIN_DATA
survives updates; CLAUDE_PLUGIN_ROOT, where this script itself lives, does not).

The Metadata and DataBio skills are separate, but they write into the two
sheets of the *same* DataProfile.xlsx output file. If that output file
already exists (e.g. one skill already ran), it's loaded and updated in
place rather than overwritten from the blank template, so filling one sheet
never clobbers the other. DataDict.xlsx gets the same treatment so that
appending more variables later doesn't erase what's already there.

Usage:
    # One-time, per machine: point the script at the researcher's
    # OneDrive-synced "Data Profiles" folder (must contain a _Templates_
    # subfolder with DataProfile.xlsx / DataDict.xlsx).
    python generate_catalog.py --set-data-profiles-root "C:/Users/me/OneDrive - Org/Data Profiles"

    # Normal runs, once configured:
    python generate_catalog.py
    python generate_catalog.py --input path/to/catalog_draft.json
    python generate_catalog.py --only databio            # just the DataBio sheet
    python generate_catalog.py --only metadata,datadict   # any subset
    python generate_catalog.py --output-dir out/          # override the
                                                            # resolved per-dataset
                                                            # folder (mainly for
                                                            # local testing)
"""

import json
import os
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILENAME = "cataloging_config.json"

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

# Metadata sheet: fields end at row 19 ("Related dataset location(s)"); row 20
# is the "To Be Completed by Modeling Technology Team" banner, and rows 21-23
# (Storage/repository location, Data steward, Data Catalog location) are that
# team's responsibility, not this skill's -- never write to those rows.
METADATA_FIRST_ROW = 3
METADATA_LAST_ROW = 19


# ── Config: where the SharePoint-synced templates and dataset folders live ──
def default_config_path():
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    base = Path(plugin_data) if plugin_data else SCRIPT_DIR
    return base / CONFIG_FILENAME


def load_config(config_path):
    if not config_path.exists():
        sys.exit(
            f"ERROR: no config found at {config_path}.\n"
            "Run: python generate_catalog.py --set-data-profiles-root \"<local path to "
            "your OneDrive-synced Data Profiles folder>\" first (one-time, per machine)."
        )
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)
    missing = [k for k in ("templates_dir", "data_profiles_root") if k not in cfg]
    if missing:
        sys.exit(f"ERROR: config at {config_path} is missing key(s): {missing}")
    return cfg


def set_data_profiles_root(config_path, data_profiles_root, templates_dir=None):
    data_profiles_root = Path(data_profiles_root)
    if not data_profiles_root.exists():
        sys.exit(f"ERROR: path does not exist: {data_profiles_root}")
    templates_dir = Path(templates_dir) if templates_dir else data_profiles_root / "_Templates_"
    if not templates_dir.exists():
        sys.exit(
            f"ERROR: templates folder not found: {templates_dir}\n"
            "Pass --templates-dir explicitly if it's not named _Templates_."
        )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            {"data_profiles_root": str(data_profiles_root), "templates_dir": str(templates_dir)},
            f, indent=2,
        )
    print(f"Config saved: {config_path.resolve()}")
    print(f"  data_profiles_root: {data_profiles_root}")
    print(f"  templates_dir:      {templates_dir}")


def _review_comment(entry, fallback="Needs human review before finalizing."):
    text = entry.get("review_notes") or fallback
    return Comment(text, "Catalog generator")


def _load_or_copy(template_path, output_path):
    if not template_path.exists():
        sys.exit(f"ERROR: template not found: {template_path}")
    if output_path.exists():
        return load_workbook(output_path)
    return load_workbook(template_path)


def fill_metadata_sheet(wb, data):
    # Field | Response only -- no color/comment review-flagging here. An
    # unresolved field is simply left blank; everything else about its
    # review status lives in chat and catalog_draft.json, not in the file.
    ws = wb["Metadata"]
    entries = data.get("metadata", [])
    max_entries = METADATA_LAST_ROW - METADATA_FIRST_ROW + 1
    for i, entry in enumerate(entries[:max_entries]):
        row = METADATA_FIRST_ROW + i
        ws.cell(row=row, column=2, value=entry.get("value", ""))
    return wb


# DataBio sheet columns: Section | Question | Answer | Confidence (AI-assisted
# only) | Source (AI-assisted only). There used to be a "Clarification/example"
# column between Question and Answer (removed -- see Section A-F derivation
# notes in the skill instead) and a single "Notes/Comments" column after
# Answer (split into Confidence + Source so review status is plain cell data
# instead of color/comments, which don't survive the Databricks sync).
DATABIO_ANSWER_COL = 3
DATABIO_CONFIDENCE_COL = 4
DATABIO_SOURCE_COL = 5


def fill_databio_sheet(wb, data):
    # Every question is drafted by AI and then approved (with edits folded
    # in) during section-by-section review before generation ever runs, so a
    # populated response is trustworthy on its own -- Confidence/Source are
    # keyed purely off whether response is blank, not a separate needs_review
    # flag (that field still exists in the JSON schema for catalog-dataset's
    # own tiered Q&A, it's just not consulted here).
    ws = wb["DataBio"]
    for i, entry in enumerate(data.get("data_bio", [])):
        row = 3 + i
        response = entry.get("response", "")

        ws.cell(row=row, column=DATABIO_ANSWER_COL, value=response)
        if response:
            confidence = entry.get("confidence", "")
            source = entry.get("source", "")
        else:
            confidence = "Needs human input"
            source = entry.get("review_notes") or "Needs input from data owner/steward."
        ws.cell(row=row, column=DATABIO_CONFIDENCE_COL, value=confidence)
        ws.cell(row=row, column=DATABIO_SOURCE_COL, value=source)
    return wb


def fill_dataprofile(data, templates_dir, output_dir, base_name, sheets):
    """sheets is a subset of {"metadata", "databio"} -- which sheet(s) to
    (re)fill in this run. The other sheet, if already present in an existing
    output file, is left untouched."""
    template_path = Path(templates_dir) / "DataProfile.xlsx"
    output_path = output_dir / f"{base_name}_DataProfile.xlsx"
    wb = _load_or_copy(template_path, output_path)

    if "metadata" in sheets:
        fill_metadata_sheet(wb, data)
    if "databio" in sheets:
        fill_databio_sheet(wb, data)

    wb.save(output_path)
    return output_path


# ── DataDict.xlsx ────────────────────────────────────────────────────────────
def fill_datadict(data, templates_dir, output_dir, base_name):
    template_path = Path(templates_dir) / "DataDict.xlsx"
    output_path = output_dir / f"{base_name}_DataDict.xlsx"
    wb = _load_or_copy(template_path, output_path)
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

    wb.save(output_path)
    return output_path


ALL_TARGETS = ("metadata", "databio", "datadict")


def main():
    args = sys.argv[1:]
    input_path = "catalog_draft.json"
    output_dir_override = None
    config_path = default_config_path()
    targets = list(ALL_TARGETS)
    set_root = None
    set_templates_dir = None

    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir_override = Path(args[i + 1])
            i += 2
        elif args[i] == "--config" and i + 1 < len(args):
            config_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--set-data-profiles-root" and i + 1 < len(args):
            set_root = args[i + 1]
            i += 2
        elif args[i] == "--templates-dir" and i + 1 < len(args):
            set_templates_dir = args[i + 1]
            i += 2
        elif args[i] == "--only" and i + 1 < len(args):
            targets = [t.strip().lower() for t in args[i + 1].split(",")]
            unknown = [t for t in targets if t not in ALL_TARGETS]
            if unknown:
                sys.exit(f"ERROR: unknown --only target(s) {unknown}; choose from {ALL_TARGETS}")
            i += 2
        else:
            i += 1

    if set_root is not None:
        set_data_profiles_root(config_path, set_root, set_templates_dir)
        return

    if not Path(input_path).exists():
        sys.exit(f"ERROR: {input_path} not found. Run the catalog-dataset skill first to generate it.")

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    config = load_config(config_path)
    base_name = data.get("dataset_name", "Dataset").replace(" ", "_")

    if output_dir_override is not None:
        output_dir = output_dir_override
    else:
        output_dir = Path(config["data_profiles_root"]) / base_name
    output_dir.mkdir(parents=True, exist_ok=True)

    dataprofile_sheets = {t for t in targets if t in ("metadata", "databio")}
    if dataprofile_sheets:
        path = fill_dataprofile(data, config["templates_dir"], output_dir, base_name, dataprofile_sheets)
        print(f"DataProfile saved ({', '.join(sorted(dataprofile_sheets))}): {path.resolve()}")

    if "datadict" in targets:
        path = fill_datadict(data, config["templates_dir"], output_dir, base_name)
        print(f"DataDict saved: {path.resolve()}")


if __name__ == "__main__":
    main()
