# data-cataloging-ai

Skills for auto-generating dataset documentation for a data catalog: administrative metadata, a data biography (purpose, provenance, consent, quality), and a variable-level data dictionary.

## Terminology

These three concepts are related but distinct, and the naming is intentionally kept separate to avoid confusion:

* **Metadata** — the administrative/catalog-record fields (title, owner, storage, access, coverage). Lives in `Metadata.xlsx`.
* **Data Biography** — a specific framework from We All Count: narrative, equity-focused questions about a dataset's origin, purpose, and social context (who made it, why, who's excluded, consent). This term refers *only* to `DataBio.xlsx`'s 22 questions — not to metadata, not to the data dictionary, and not to the three files as a whole.
* **Data Dictionary / Codebook** — the variable-level schema (one row per column/field in the dataset). Lives in `DataDict.xlsx`. A much older and more generic data-documentation concept, unrelated to Data Biography.

The three files together make up a dataset's **catalog**.

## The three deliverables

A fully cataloged dataset produces three separate Excel files, each with a blank template checked into the repo root:

| Template | What it captures |
| --- | --- |
| `Metadata.xlsx` | 18 administrative/technical fields — title, version, owner, steward, storage location, access level, citation, geographic/temporal coverage, etc. Two columns: `Field` / `Response`. |
| `DataBio.xlsx` | 22 narrative questions across six sections (A–F), adapted from the We All Count Data Biography framework — purpose, provenance, collection methods, coverage, consent, and quality. Most questions have a suggested controlled vocabulary (the "Lists" sheet, exposed as an Excel dropdown that also accepts free text). |
| `DataDict.xlsx` | One row per variable, 13 columns — file name, variable name/label, definition, data type, unit, allowed values, missing codes, source/derivation, numerator/denominator, sensitivity, and quality notes. |

**Never edit these three files directly as templates.** Skills draft content into `catalog_draft.json`, and `generate_catalog.py` fills copies of the templates to produce dataset-specific outputs: `<Dataset>_Metadata.xlsx`, `<Dataset>_DataBio.xlsx`, `<Dataset>_DataDict.xlsx`.

## Skills

Each skill lives in `skills/<name>/SKILL.md`. Invoke by name (e.g. `/catalog-dataset`) or by asking for what it does — see each skill's "When to use this skill" section.

### `catalog-dataset` — primary entry point

Fills all three deliverables in one pass. Use this unless you only need a single file.

1. **Draft** — reads all available sources (dataset file(s), protocol, questionnaire, papers, README, existing docs) and drafts every field/question/variable, writing everything to `catalog_draft.json` with a confidence level (High/Medium/Low) and a `needs_review` flag per item.
2. **Q&A** — presents unresolved items back to you in three tiers, one at a time: Critical (data owner, steward, access/DUA terms, consent questions) → Important (version, citation, methodology detail) → Optional (update frequency, enumerator training, etc). Answer by number or type `skip`.
3. **Generate** — runs `python generate_catalog.py`, which fills the three templates and reports the output paths.

### `metadata`

Fills just `Metadata.xlsx`'s 18 fields. Useful when the data biography or data dictionary aren't needed yet, or to redo the metadata file in isolation.

### `data-bio`

Fills just `DataBio.xlsx`'s 22 questions — the actual "data biography." This is the most human-judgment-intensive file — consent, equity, and "inappropriate uses" questions are always flagged for human input.

### `data-dictionary`

Fills just `DataDict.xlsx`, one row per variable. Works either from an actual dataset file (inspecting real values) or from documentation alone (codebook, questionnaire) when only docs are available or data is sensitive.

### `profile-dataset`

Not part of the catalog output — a standalone data-quality/analytical-fitness assessment (completeness, consistency, uniqueness, validity, temporal/spatial coverage, linkability) with a scored usability rating. Useful before cataloging, or as a supporting input the other skills can cite (e.g. for Metadata's "sensitive data classification" or DataBio's Section F quality questions).

## Modes

Every drafting skill operates in one of two modes, and reports which one it used:

* **Mode A — full data available**: the dataset file itself can be inspected (actual values, ranges, missingness), with documentation as a supplementary source.
* **Mode B — documentation only**: no dataset file (e.g. access is under a Data Use Agreement). Drafts come only from protocol, questionnaire, papers, or other documentation. Never invents what the underlying data looks like.

## Review flags in the generated files

Flags surface directly on the cell instead of as extra columns:

* **Needs review** (any file): the cell is filled yellow and carries an Excel comment with the specific question to resolve.
* **Sensitive variable** (`DataDict.xlsx` only): the `Sensitive?` cell is filled red.

Resolve these before treating a catalog as final — check every yellow cell's comment, especially in `DataBio.xlsx`'s Section E (consent/privacy/access), which is always flagged for human input regardless of documentation.

## Running the generator manually

```
python generate_catalog.py                                   # reads ./catalog_draft.json
python generate_catalog.py --input path/to/draft.json
python generate_catalog.py --input draft.json --output-dir out/
```

Requires `openpyxl` (`pip install openpyxl`). Templates are resolved relative to the script's own location, so it works from any working directory as long as `catalog_draft.json` (or `--input`) is reachable.

## Repo layout

```
Metadata.xlsx / DataBio.xlsx / DataDict.xlsx   Blank templates — do not overwrite with real data
generate_catalog.py                            Fills the templates from catalog_draft.json
catalog_draft.json                             Working draft for the dataset currently being cataloged
skills/
  catalog-dataset/   metadata/   data-bio/   data-dictionary/   profile-dataset/
```
