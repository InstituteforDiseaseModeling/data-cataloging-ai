# Complete Variables Tab

Use this skill when the user wants to fill the INDIVIDUAL VARIABLES sheet of `databio_v1.xlsx`.

The INDIVIDUAL VARIABLES sheet is a structured data dictionary with one row per variable and 12 columns. This skill generates a draft row for each variable from the available dataset or documentation.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete the INDIVIDUAL VARIABLES tab in databio_v1.xlsx
* Generate a data dictionary or codebook for a dataset
* Describe dataset columns or variables
* Produce variable-level metadata for a catalog, README, or data biography

## Inputs

The user may provide one or more of the following:

* A dataset file
* An existing data dictionary, codebook, or questionnaire
* A dataset profile from the `profile-dataset` skill
* Existing documentation (README, protocol, schema)
* Domain context from the user

**Mode A** (full data available): derive from the actual dataset. Use documentation as supplementary source.
**Mode B** (documentation only): derive from codebook, questionnaire, or existing variable list. Never invent what the data looks like.

## Outputs

A data dictionary table with one row per variable and 12 columns, matching the INDIVIDUAL VARIABLES tab structure. Includes confidence scores and review flags per variable. Ends with a prioritized "Variables for human review" list.

## The 12 variable columns

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

Default to a markdown table:

| variable_name | variable_label | definition | data_type | unit | allowed_values_codes | missing_unknown_codes | source_derivation | numerator | denominator | sensitive | data_quality_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Also provide a YAML block:

```yaml
variables_tab:
  - variable_name:
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
