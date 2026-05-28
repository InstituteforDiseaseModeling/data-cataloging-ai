# Draft Dataset Description

Use this skill when the user wants to generate dataset-level descriptive metadata from a dataset, dataset profile, data dictionary, or supporting documentation.

This skill drafts human-readable dataset metadata such as title, abstract, purpose, coverage, source, methods summary, limitations, and recommended citation fields.

## When to use this skill

Use this skill when the user asks to:

* Draft a dataset description
* Generate dataset-level metadata
* Create a README description
* Summarize what a dataset contains
* Prepare metadata for a data catalog
* Create a title, abstract, or purpose statement for a dataset
* Describe dataset coverage, provenance, or intended use

## Inputs

The user may provide one or more of the following:

* A dataset file
* A dataset profile
* A data dictionary
* Existing README or documentation
* Study protocol or project summary
* Source information
* User-provided context about purpose, methods, geography, population, or access restrictions

## Outputs

Generate a review-ready dataset description with the following sections:

1. Suggested title
2. Short description
3. Detailed description
4. Purpose and intended use
5. Unit of observation
6. Topics and keywords
7. Spatial coverage
8. Temporal coverage
9. Population or scope
10. Source and provenance
11. Methodology or processing summary
12. Key variables
13. Limitations and caveats
14. Sensitivity and access notes
15. Recommended citation fields, if possible
16. Fields needing human review

## Required behavior

When drafting dataset-level metadata:

* Use provided documentation as the highest-priority source.
* Use dataset profile and data dictionary outputs as supporting evidence.
* Clearly distinguish documented facts from inferred metadata.
* Do not invent source, owner, license, collection methodology, or access conditions.
* Mark uncertain fields as needing human review.
* Use concise, professional language suitable for a dataset catalog or README.
* Preserve important domain terminology.
* Avoid overclaiming what the dataset can be used for.
* Include sensitivity or access caveats when potentially relevant.
* Include confidence levels for inferred fields.

## Suggested title

Create a concise, descriptive title.

A good title should usually include:

* Main topic or indicator
* Geography, if known
* Time period, if known
* Dataset type, if useful

Examples:

```text
Health Facility Service Readiness Indicators in Senegal, 2021–2023
```

```text
Simulated Malaria Incidence Outputs by District and Intervention Scenario
```

If geography or time period is inferred rather than documented, indicate that review is needed.

## Short description

Write 1–2 sentences summarizing:

* What the dataset contains
* Geographic or temporal scope, if known
* Unit of observation, if inferable
* Primary use or domain, if supported

Example:

```text
This dataset contains district-level malaria incidence estimates and intervention scenario outputs for multiple simulation runs. The data appear to support comparison of modeled intervention strategies across geographic areas and time periods.
```

## Detailed description

Write 1–3 paragraphs covering:

* Dataset contents
* Major entities represented
* Important variables or measures
* Time and geographic coverage
* Source or generation process, if known
* How the dataset may be used
* Important caveats

Keep the tone factual and cautious.

## Purpose and intended use

Describe the likely or documented purpose.

Use language such as:

* “This dataset is intended to support…”
* “Based on available metadata, this dataset appears to support…”
* “The intended use should be confirmed by the data owner…”

Do not invent a purpose when none is provided.

## Unit of observation

Infer the likely unit represented by each row.

Examples:

* person
* household
* health facility
* administrative area
* country-year
* facility-month
* survey response
* lab sample
* model run
* simulation scenario
* intervention package
* unknown

Explain the evidence, such as identifier columns, date columns, or repeated values.

## Topics and keywords

Suggest keywords based on:

* Dataset title
* Column names
* Observed values
* User-provided context
* Existing documentation

Separate confirmed keywords from suggested keywords.

Example:

```yaml
keywords:
  confirmed:
    - malaria
    - incidence
  suggested_for_review:
    - intervention modeling
    - district-level estimates
```

## Spatial coverage

If geography is present, summarize:

* Countries
* Administrative levels
* Facilities or sites
* Coordinates or geometry
* Geographic granularity

If inferred, include the source columns and confidence.

Example:

```yaml
spatial_coverage:
  value: "Senegal"
  source: "country column"
  confidence: "high"
  needs_review: false
```

## Temporal coverage

If dates or years are present, summarize:

* Start date or year
* End date or year
* Date column used
* Granularity
* Whether the date likely represents collection, reporting, event, or model time

Example:

```yaml
temporal_coverage:
  start: "2020"
  end: "2023"
  source_column: "year"
  granularity: "year"
  confidence: "medium"
  needs_review: true
```

## Source and provenance

Capture source information only when available or inferable with caution.

Possible fields:

* Source organization
* Data owner or steward
* Original data source
* Collection method
* Processing pipeline
* Code repository
* Model or software version
* Extraction or generation date
* Upstream datasets

If source information is missing, say so directly.

## Methodology or processing summary

Summarize known methods, such as:

* Survey
* Routine health information system
* Simulation model
* Statistical model output
* Geospatial processing
* Laboratory sequencing
* Administrative reporting
* Data cleaning or aggregation

Do not invent methodology from column names alone.

Use cautious language when needed:

```text
The dataset appears to contain model output, but the model type, version, and calibration process are not provided.
```

## Limitations and caveats

Identify limitations such as:

* Missing source documentation
* Ambiguous column meanings
* Unclear units
* Missing license
* Unknown data collection method
* Incomplete temporal coverage
* Potential sensitivity
* Inferred rather than documented metadata
* Coded categories without labels
* Possible data quality issues

## Sensitivity and access notes

Include a review-oriented note if the dataset may contain:

* Person-level data
* Household-level data
* Facility-level data
* Exact coordinates
* Small-area geography
* Sensitive health indicators
* Free text
* Partner-restricted data
* Internal-only fields

Do not make final access decisions.

## Recommended citation fields

If possible, draft placeholders for:

* Dataset title
* Creator
* Publisher
* Publication year
* Version
* DOI or persistent identifier
* Access URL
* License

Use placeholders where information is missing.

Example:

```yaml
recommended_citation_fields:
  title: "Draft title pending review"
  creator: "Not provided"
  publisher: "Not provided"
  publication_year: "Not provided"
  version: "Not provided"
  identifier: "Not provided"
  license: "Not provided"
```

## Output format

Default to markdown.

Also include a structured YAML block when useful:

```yaml
dataset_description:
  title:
    value:
    source:
    confidence:
    needs_review:
  short_description:
    value:
    source:
    confidence:
    needs_review:
  detailed_description:
    value:
    source:
    confidence:
    needs_review:
  purpose:
    value:
    source:
    confidence:
    needs_review:
  unit_of_observation:
    value:
    evidence:
    confidence:
    needs_review:
  spatial_coverage:
    value:
    source:
    confidence:
    needs_review:
  temporal_coverage:
    start:
    end:
    source:
    confidence:
    needs_review:
  keywords:
    confirmed:
    suggested_for_review:
  provenance:
    source:
    owner:
    processing_notes:
    confidence:
    needs_review:
  limitations:
    - 
  sensitivity_and_access_notes:
    - 
  recommended_citation_fields:
    title:
    creator:
    publisher:
    publication_year:
    version:
    identifier:
    license:
  fields_needing_human_review:
    - field:
      reason:
```

## Confidence scoring

Use:

* High: directly documented or strongly supported by dataset structure and values.
* Medium: likely based on dataset profile, column names, and observed values.
* Low: speculative or requires project/domain knowledge.

## Human review section

End with a section called `Fields needing human review`.

Include missing or uncertain information such as:

* Dataset owner
* Dataset source
* License
* Access restrictions
* Citation information
* Intended use
* Collection methodology
* Meaning of ambiguous fields
* Sensitivity classification
* Temporal coverage interpretation
* Geographic coverage interpretation

## Do not do the following

Do not:

* Invent a title that overstates the dataset’s scope.
* Invent collection methods, owner, license, or funding source.
* Claim that the dataset is publication-ready unless required metadata is complete.
* Assume inferred metadata is confirmed.
* Ignore privacy or access concerns.
* Use overly promotional language.
* Include raw sensitive values in the description.
