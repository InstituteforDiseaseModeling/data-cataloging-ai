# Complete Data Dictionary

Use this skill when the user wants to fill `DataDict.xlsx`.

`DataDict.xlsx` is a structured data dictionary with one row per variable and 13 columns. This skill generates a draft row for each variable from the available dataset or documentation.

Note: this is one of three files in a dataset catalog (alongside `Metadata.xlsx` and `DataBio.xlsx`). It is a data dictionary/codebook, not a "data biography" — that term is reserved for `DataBio.xlsx`'s 22 narrative questions. See the `catalog-dataset` skill if the user wants all three filled together.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete DataDict.xlsx
* Generate a data dictionary or codebook for a dataset
* Describe dataset columns or variables
* Produce variable-level metadata for a catalog or README

## Inputs

The user may provide one or more of the following:

* A dataset file
* An existing data dictionary, codebook, or questionnaire
* A dataset profile from the `profile-dataset` skill
* Existing documentation (README, protocol, schema)
* A URL — either a direct link to a downloadable data file, or a link to a page describing the dataset
* Domain context from the user

If given a URL, resolve it before drafting anything — see `data-bio`'s Step 1 for the full procedure: fetch it, don't guess which file is meant if a page links to several, and if you download a single unambiguous file, state plainly what was pulled before continuing.

**Mode A** (full data available): derive from the actual dataset. Use documentation as supplementary source.
**Mode B** (documentation only): derive from codebook, questionnaire, or existing variable list. Never invent what the data looks like.

## Outputs

A data dictionary table with one row per variable and 13 columns, matching the DataDict.xlsx structure. Includes confidence scores and review flags per variable. Ends with a prioritized "Variables for human review" list.

## The 13 variable columns

### file_name

The name of the file this variable belongs to (e.g., the dataset filename, or a table/sheet name if the dataset bundle has multiple files).

Derive from: the dataset filename (Mode A), or the file name as stated in documentation (Mode B — e.g., a data layout doc that lists file names).

If the dataset is a bundle of multiple files, repeat this column per variable so each row is traceable to its source file. Flag for review if the source file is ambiguous.

### variable_name

The original column name exactly as it appears in the dataset. Never rename.

### variable_label

A human-readable label. Expand abbreviations where clearly supportable. Replace underscores or camelCase with readable words.

Examples:

* `admin1_name` → Administrative level 1 name
* `facility_id` → Facility identifier
* `cp_rate` → flag as needing review if the abbreviation is unclear

If the label requires domain knowledge to get right, flag for review.

### definition

A plain-language explanation of what the variable represents, in one sentence when possible.

Answer: What does this variable measure? How should the value be interpreted? Are there known restrictions or dependencies?

Use cautious language for inferred definitions: "Likely represents…" or "Appears to indicate…"

### data_type

Infer from observed values (Mode A) or documentation (Mode B).

Standard types: string, integer, float, boolean, date, datetime, categorical, geometry, json, array, unknown.

Do not infer type from the first few rows only if more data is available.

### unit

The unit of measurement, if applicable.

Examples: kg, USD, percentage, per 1,000 population, years, days, degrees Celsius.

Leave blank if not applicable (e.g., categorical or identifier fields). Flag for review if the unit is unclear for a numeric variable.

### allowed_values_codes

For categorical variables: list observed or documented categories. If the list is long, summarize.
For numeric variables: state observed or documented min/max and whether values are continuous or discrete.
For date variables: state observed range and format.
For coded variables: reference the codebook or coding scheme.

Do not list every raw value for high-cardinality or sensitive columns.

### missing_unknown_codes

Document how missing, unknown, or not-applicable values are represented.

Examples: blank, NA, N/A, null, Unknown, Other, 999, -99.

Note whether missingness appears meaningful or structural.

### source_derivation

Describe where the variable comes from.

Examples: original (collected directly), calculated (derived from other variables), modeled, administrative, linked from external source, aggregated, cleaned/recoded.

If derivation details are in documentation, summarize them. If unknown, flag for review.

### numerator

For calculated rates or indicators: describe what the numerator counts or measures.

Leave blank if not applicable. Flag for review if the variable appears to be a rate or indicator but the numerator is not documented.

### denominator

For calculated rates or indicators: describe the denominator (population, total, expected cases, etc.).

Leave blank if not applicable. Flag for review if the variable appears to be a rate or indicator but the denominator is not documented.

### sensitive

Boolean: true or false.

Mark true if the variable may contain:

* Names, contact information, or person identifiers
* Household or facility identifiers
* Exact GPS coordinates
* Sensitive health indicators (e.g., HIV status, mental health, reproductive health)
* Demographic characteristics that could enable re-identification
* Small-area geography
* Partner-restricted or internal-only information
* Free text that may contain sensitive content

When uncertain, default to true and note the reason. Do not make final governance decisions.

### data_quality_notes

Document known issues, interpretation caveats, or quality flags.

Examples: high missingness rate, suspicious placeholder values, inconsistent formatting, comparability caveats across time or geography, coding inconsistencies.

If no issues are identified, leave blank.

## Required behavior

* Preserve original variable names exactly.
* In Mode A: inspect actual data values, not just column names.
* In Mode B: derive from documentation. Do not invent types, ranges, or values.
* Clearly distinguish documented facts from inferred descriptions.
* Flag variables with ambiguous meaning, sensitivity concerns, or missing documentation.
* Use plain language accessible to a dataset user without domain expertise.
* Do not expose sensitive row-level data. Use representative examples and aggregate summaries.
* Mark uncertainty explicitly using confidence levels.

## Confidence scoring

* High: directly documented or strongly supported by column name and observed values.
* Medium: likely interpretation based on naming patterns, values, or documentation.
* Low: ambiguous, abbreviation unclear, or insufficient evidence.

## Output format

In chat, default to a markdown table:

| file_name | variable_name | variable_label | definition | data_type | unit | allowed_values_codes | missing_unknown_codes | source_derivation | numerator | denominator | sensitive | data_quality_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

This table (plus `confidence`/`needs_review` from the YAML below) feeds `catalog_draft.json` for the tiered Q&A in `catalog-dataset`. The final `DataDict.xlsx` file has these same 13 content columns but no confidence or needs_review columns: variables still flagged `needs_review` get a yellow-filled Variable Name cell with an Excel comment carrying the issue, and `sensitive: true` variables get a red-filled Sensitive? cell.

Also provide a YAML block:

```yaml
variables_tab:
  - file_name:
    variable_name:
    variable_label:
    definition:
    data_type:
    unit:
    allowed_values_codes:
    missing_unknown_codes:
    source_derivation:
    numerator:
    denominator:
    sensitive:
    data_quality_notes:
    confidence:
    needs_review:
```

## Variables for human review

End with a section called `Variables for human review`. List variables with needs_review: true, prioritized:

1. Sensitive variables (potential privacy or governance impact)
2. Ambiguous-meaning variables (low confidence definitions)
3. Missing documentation (unit unclear, codes not labeled, derivation unknown)

For each:

```
Variable: [name]
Issue: [what is unclear or concerning]
What to provide: [what the human should confirm or supply]
```

## Do not do the following

Do not:

* Rename variables.
* Remove variables from the table.
* Invent units, coding schemes, or derivation logic.
* Treat inferred descriptions as confirmed facts.
* Include long lists of raw values for high-cardinality or sensitive columns.
* Ignore existing documentation when it conflicts with inference.
* Mark sensitive as false without clear evidence that the variable is non-sensitive.
