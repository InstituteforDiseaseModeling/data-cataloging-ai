# Complete Metadata Tab

Use this skill when the user wants to fill the METADATA sheet of `databio_v1.xlsx`.

The METADATA sheet captures 18 administrative and technical fields that identify a dataset, describe its scope, and record stewardship information. This skill drafts as many fields as possible from available sources and flags what requires human input.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete the METADATA tab in databio_v1.xlsx
* Generate administrative metadata for a dataset
* Draft dataset-level identification, coverage, and stewardship fields
* Prepare a dataset for entry into a data catalog

## Inputs

The user may provide one or more of the following:

* A dataset file (CSV, Excel, Parquet, JSON, GeoJSON, etc.)
* A dataset profile from the `profile-dataset` skill
* Existing documentation (README, protocol, published papers, study report)
* User-provided context about ownership, access, storage, or citation

**Mode A** (full data available): use the dataset file and documentation together.
**Mode B** (documentation only): use available documentation only. Do not invent dataset structure or characteristics.

## Outputs

A filled draft of all 18 METADATA fields, each with:

* Draft value (or "Requires human input")
* Source (what the value was derived from)
* Confidence (High / Medium / Low)
* Needs review flag

Followed by a consolidated "Fields for human review" list.

## The 18 metadata fields

### 1. Dataset title / name

Derive from: filename, documentation title, paper title, user context.

A good title includes the main topic, geography if known, and time period if known. Mark as needing review if only inferred from filename.

### 2. Dataset short description

Derive from: abstract, README, protocol summary, user context.

Write 1–2 sentences covering what the dataset contains, its scope, unit of observation if inferable, and primary domain. Do not invent purpose.

### 3. Dataset version

Derive from: filename versioning, documentation, file metadata, user context.

If not provided, leave blank and flag for review.

### 4. Date biography last updated

Set to today's date automatically.

### 5. Data provider / source organization

Derive from: paper authorship, protocol header, study acknowledgments, user context.

If multiple organizations are involved, list them. If unclear, flag for review.

### 6. Extract / release date

Derive from: file metadata, documentation, user context. If not provided, flag for review.

### 7. Update frequency / rounds / waves

Derive from: protocol (e.g., "annual survey," "three rounds," "baseline + endline"), documentation.

Use the documentation's own language. If not mentioned, flag for review.

### 8. Data owner

**Always requires human input.** The data owner is the person or institution with decision-making authority over the dataset. Do not infer from paper authorship alone.

Set to "Requires human input."

### 9. Data steward / primary contact

**Always requires human input.** The data steward handles day-to-day management and user requests.

Set to "Requires human input."

### 10. File inventory

Derive from: directory listing (Mode A), documentation listing files (Mode B).

List known files. Flag for review if the inventory may be incomplete.

### 11. Storage / repository location

**Requires human input.** The physical or logical storage path, data platform, or repository URL.

Set to "Requires human input."

### 12. Access level / restrictions

Derive from: DUA status mentioned in documentation, data use terms, user context.

Common values: Public, Internal, Restricted, Confidential, Under DUA.

If access terms are mentioned in documentation, extract and paraphrase them. Always flag for human confirmation.

### 13. Citation / attribution

Derive from: published paper DOI or citation, dataset documentation, user context.

Draft a placeholder if the full citation is not available. Flag if incomplete.

### 14. Sensitive data classification

Derive from: `profile-dataset` output (if available), documentation, column names, user context.

Consider: person-level data, health data, exact coordinates, small-area geography, government data, partner-restricted data.

Common values: Public, Internal, Restricted, Sensitive, Highly Sensitive.

Use cautious language if uncertain. Always flag for human confirmation.

### 15. Geographic coverage

Derive from: `profile-dataset` output (if available), documentation, column names, observed values.

Describe countries, regions, administrative levels, or sites. Include the source of the inference and confidence level.

### 16. Temporal coverage / reference period

Derive from: `profile-dataset` output (if available), documentation, date columns in dataset, paper methods sections.

Describe start/end date or year and granularity. Note whether this represents the collection period, reference period, or model time.

### 17. Unit of observation / granularity

Derive from: `profile-dataset` output (if available), documentation, dataset structure.

Examples: person, household, health facility, district, country-year, survey cluster, model run.

Explain the evidence and flag if ambiguous.

### 18. Related dataset location(s)

Derive from: documentation references to upstream, downstream, or companion datasets.

If not documented, set to "Requires human input."

## Required behavior

* In Mode A: inspect the actual dataset. Use documentation as secondary source.
* In Mode B: use documentation only. Do not invent dataset characteristics.
* Distinguish documented facts from inferences. Use language like "appears to" or "likely" for inferences.
* Never invent data owner, steward, access terms, storage location, or citation.
* Mark fields with low confidence as needing review.
* Do not expose sensitive row-level data.

## Confidence scoring

* High: directly documented or unambiguously observable.
* Medium: likely based on documentation patterns or file inspection.
* Low: speculative, inferred from indirect evidence, or absent from available sources.

## Output format

Return a markdown table:

| Field | Draft value | Source | Confidence | Needs review |
| ----- | ----------- | ------ | ---------- | ------------ |

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
  dataset_version:
    value:
    source:
    confidence:
    needs_review:
  date_bio_last_updated:
    value:
    source:
    confidence:
    needs_review:
  data_provider_source_org:
    value:
    source:
    confidence:
    needs_review:
  extract_release_date:
    value:
    source:
    confidence:
    needs_review:
  update_frequency_rounds_waves:
    value:
    source:
    confidence:
    needs_review:
  data_owner:
    value:
    source:
    confidence:
    needs_review:
  data_steward_primary_contact:
    value:
    source:
    confidence:
    needs_review:
  file_inventory:
    value:
    source:
    confidence:
    needs_review:
  storage_repository_location:
    value:
    source:
    confidence:
    needs_review:
  access_level_restrictions:
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
  geographic_coverage:
    value:
    source:
    confidence:
    needs_review:
  temporal_coverage:
    value:
    source:
    confidence:
    needs_review:
  unit_of_observation:
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

* Critical: data owner, data steward, access level/restrictions, storage location, sensitive data classification
* Important: version, citation/attribution, geographic coverage, temporal coverage, unit of observation
* Optional: update frequency, related dataset locations

## Do not do the following

Do not:

* Invent data owner, data steward, or storage location.
* Infer access restrictions without evidence in documentation.
* Set sensitive data classification to "Public" without clear evidence.
* Claim the metadata is complete when review items remain.
* Use overly promotional or overclaiming language.
