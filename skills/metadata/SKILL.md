# Complete Metadata Tab

Use this skill when the user wants to fill the "Metadata" sheet of `DataProfile.xlsx`.

The Metadata sheet captures 17 administrative and technical fields that identify a dataset, describe its scope, and record stewardship information. This skill drafts as many fields as possible from available sources and flags what requires human input.

`DataProfile.xlsx` has two sheets: "Metadata" (this skill) and "DataBio" (the `data-bio` skill, 22 narrative questions). Both skills write into the *same* output file, each owning its own sheet — see "Output format" below for how that's handled. `DataDict.xlsx` is a separate file, out of scope for this skill.

The Metadata sheet only has two content columns — `Field` and `Response` — in rows 3–19 (row 2 is the header). Below that is a banner row, **"To Be Completed by Modeling Technology Team,"** followed by three fields — Storage/repository location (Databricks URL), Data steward, Data Catalog location (Dataverse URL) — that belong to a different team's downstream process. **Never fill or prompt about those three fields; leave them blank.**

There is no room in the template for source, confidence, or review-flag columns, so this skill tracks that richer context in chat and in `catalog_draft.json`, and the generator surfaces unresolved items as a highlighted cell with a comment rather than an extra column.

Note: this is one of two files in a dataset catalog (alongside `DataDict.xlsx`; the DataBio sheet lives in this same file). "Data Biography" refers specifically to the DataBio sheet's 22 narrative questions, not to metadata or to the catalog as a whole — see the `catalog-dataset` skill if the user wants everything filled together.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete the Metadata tab/sheet in DataProfile.xlsx
* Generate administrative metadata for a dataset
* Draft dataset-level identification, coverage, and stewardship fields
* Prepare a dataset for entry into a data catalog

## Inputs

The user may provide one or more of the following:

* A dataset file (CSV, Excel, Parquet, JSON, GeoJSON, etc.)
* A dataset profile from the `profile-dataset` skill
* Existing documentation (README, protocol, published papers, study report)
* A URL — either a direct link to a downloadable data file, or a link to a page describing the dataset
* User-provided context about ownership, access, storage, or citation

If given a URL, resolve it before drafting anything — see `data-bio`'s Step 1 for the full procedure: fetch it, don't guess which file is meant if a page links to several, and if you download a single unambiguous file, state plainly what was pulled before continuing.

**Mode A** (full data available): use the dataset file and documentation together.
**Mode B** (documentation only): use available documentation only. Do not invent dataset structure or characteristics.

## Outputs

A filled draft of all 17 Metadata fields, each with:

* Draft value (or "Requires human input")
* Source (what the value was derived from)
* Confidence (High / Medium / Low)
* Needs review flag

Followed by a consolidated "Fields for human review" list.

## The 17 metadata fields

### 1. Dataset title / name

Derive from: filename, documentation title, paper title, user context.

A good title includes the main topic, geography if known, and time period if known. Mark as needing review if only inferred from filename.

### 2. Dataset short description

Derive from: abstract, README, protocol summary, user context.

Write 1–2 sentences covering what the dataset contains, its scope, unit of observation if inferable, and primary domain. Do not invent purpose.

### 3. Subject(s)

Derive from: title, abstract, documentation, general domain framing.

A short list of broad topic/domain keywords describing the dataset — e.g., "Population, Demographics," "Health, Nutrition," "Agriculture, Food Security," "Poverty, Economics," "Education." Use broad domain terms, not narrow indicator names. Flag for review if the domain is ambiguous.

### 4. Dataset version

Derive from: filename versioning, documentation, file metadata, user context.

If not provided, leave blank and flag for review.

### 5. Data provider / source organization

Derive from: paper authorship, protocol header, study acknowledgments, user context.

If multiple organizations are involved, list them. If unclear, flag for review.

### 6. Production Date

Derive from: file metadata, documentation, publication or release date, user context.

The date this dataset (or this specific version of it) was produced or released — not the date of underlying data collection, which belongs in the DataBio sheet's Q13. If not provided, flag for review.

### 7. Update frequency / rounds / waves

Derive from: protocol (e.g., "annual survey," "three rounds," "baseline + endline"), documentation.

Use the documentation's own language. If not mentioned, flag for review.

### 8. Data owner / Point of contact

**Always requires human input.** The person, team, or institution with the most knowledge of the dataset and decision-making authority over its access and use. Do not infer from paper authorship alone.

Set to "Requires human input."

### 9. File inventory

Derive from: directory listing (Mode A), documentation listing files (Mode B).

List known files. Flag for review if the inventory may be incomplete.

### 10. Citation / attribution

Derive from: published paper DOI or citation, dataset documentation, user context.

Draft a placeholder if the full citation is not available. Flag if incomplete.

### 11. Sensitive data classification

Derive from: `profile-dataset` output (if available), documentation, column names, user context.

Consider: person-level data, health data, exact coordinates, small-area geography, government data, partner-restricted data.

Common values: Public, Internal, Restricted, Sensitive, Highly Sensitive.

Use cautious language if uncertain. Always flag for human confirmation.

### 12. Data Sharing Agreement (URL, where applicable)

Derive from: DUA mentioned in documentation, user context.

If a specific Data Sharing/Use Agreement document or URL is known, provide it. If no DSA applies (e.g., fully public data with no agreement), state "Not applicable." Always flag for human confirmation regardless of what's drafted — do not assume no DSA exists just because none was mentioned in the documentation reviewed.

### 13. Geographic coverage

Derive from: `profile-dataset` output (if available), documentation, column names, observed values.

Describe countries, regions, administrative levels, or sites. Include the source of the inference and confidence level.

### 14. Unit of observation / granularity

Derive from: `profile-dataset` output (if available), documentation, dataset structure.

Examples: person, household, health facility, district, country-year, survey cluster, model run.

Explain the evidence and flag if ambiguous.

### 15. Temporal Coverage (Start)

Derive from: `profile-dataset` output (if available), documentation, date columns in dataset, paper methods sections.

The earliest date or year the dataset covers. Note whether this represents the collection period, reference period, or model time.

### 16. Temporal Coverage (End)

Derive from: same sources as Start.

The latest date or year the dataset covers, or "Present" / "Ongoing" if data collection is still active.

### 17. Related dataset location(s)

Derive from: documentation references to upstream, downstream, or companion datasets.

If not documented, set to "Requires human input."

## Fields out of scope for this skill

Never fill in, draft, or ask the user about these — they sit below the "To Be Completed by Modeling Technology Team" banner in the template and are a different team's responsibility:

* Storage/repository location (Databricks URL)
* Data steward
* Data Catalog location (Dataverse URL)

## Required behavior

* In Mode A: inspect the actual dataset. Use documentation as secondary source.
* In Mode B: use documentation only. Do not invent dataset characteristics.
* Distinguish documented facts from inferences. Use language like "appears to" or "likely" for inferences.
* Never invent data owner/point of contact, DSA terms, or citation.
* Never write to or prompt about the three fields under the "Modeling Technology Team" banner.
* Mark fields with low confidence as needing review.
* Do not expose sensitive row-level data.

## Confidence scoring

* High: directly documented or unambiguously observable.
* Medium: likely based on documentation patterns or file inspection.
* Low: speculative, inferred from indirect evidence, or absent from available sources.

## Output format

In chat, return a markdown table:

| Field | Draft value | Source | Confidence | Needs review |
| ----- | ----------- | ------ | ---------- | ------------ |

This `value/source/confidence/needs_review` shape also feeds `catalog_draft.json` for the tiered Q&A in `catalog-dataset`. It does **not** map one-to-one onto the final `DataProfile.xlsx` file: the Metadata sheet only has `Field` and `Response` columns. When the file is generated, each field's `value` goes into Response (rows 3–19) as plain text; fields still flagged `needs_review` get a yellow-filled Response cell with an Excel comment carrying the review question (source/confidence are not visible columns in the deliverable — keep them in chat and the JSON draft).

Because the Metadata and DataBio sheets live in one workbook but are filled by two separate skills, the generator (`python generate_catalog.py --only metadata`) loads the existing `<Dataset>_DataProfile.xlsx` output if one is already there (e.g. because `data-bio` already ran) and updates just the Metadata sheet in place, rather than overwriting the whole file from the blank template.

Also return a YAML block:

```yaml
metadata_tab:
  dataset_title:
    value:
    source:
    confidence:
    needs_review:
  short_description:
    value:
    source:
    confidence:
    needs_review:
  subjects:
    value:
    source:
    confidence:
    needs_review:
  dataset_version:
    value:
    source:
    confidence:
    needs_review:
  data_provider_source_org:
    value:
    source:
    confidence:
    needs_review:
  production_date:
    value:
    source:
    confidence:
    needs_review:
  update_frequency_rounds_waves:
    value:
    source:
    confidence:
    needs_review:
  data_owner_point_of_contact:
    value:
    source:
    confidence:
    needs_review:
  file_inventory:
    value:
    source:
    confidence:
    needs_review:
  citation_attribution:
    value:
    source:
    confidence:
    needs_review:
  sensitive_data_classification:
    value:
    source:
    confidence:
    needs_review:
  data_sharing_agreement_url:
    value:
    source:
    confidence:
    needs_review:
  geographic_coverage:
    value:
    source:
    confidence:
    needs_review:
  unit_of_observation:
    value:
    source:
    confidence:
    needs_review:
  temporal_coverage_start:
    value:
    source:
    confidence:
    needs_review:
  temporal_coverage_end:
    value:
    source:
    confidence:
    needs_review:
  related_dataset_locations:
    value:
    source:
    confidence:
    needs_review:
```

## Fields for human review

End with a section called `Fields for human review`. List only fields with needs_review: true, structured as:

```
Priority: Critical / Important / Optional
Field: [field name]
Why: [brief reason it needs review]
What to provide: [what the human should supply]
```

Priority guidance:

* Critical: data owner/point of contact, Data Sharing Agreement URL, sensitive data classification
* Important: version, citation/attribution, geographic coverage, temporal coverage (start/end), unit of observation
* Optional: subject(s), update frequency, related dataset locations

## Do not do the following

Do not:

* Invent a data owner/point of contact, DSA terms, or citation.
* Infer that no Data Sharing Agreement applies just because none was mentioned in documentation.
* Set sensitive data classification to "Public" without clear evidence.
* Claim the metadata is complete when review items remain.
* Fill in or ask about Storage/repository location, Data steward, or Data Catalog location — those are out of scope for this skill.
* Use overly promotional or overclaiming language.
