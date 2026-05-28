# Profile Dataset

Use this skill when the user wants to inspect, summarize, or understand the structure and quality of a dataset before generating metadata.

This skill creates a dataset profile that can be used as input for downstream metadata generation, including data dictionaries, dataset descriptions, FAIR assessments, and metadata export packages.

## When to use this skill

Use this skill when the user provides or refers to a dataset and asks to:

* Profile the dataset
* Inspect columns, types, or values
* Summarize dataset structure
* Identify missingness, duplicates, or quality issues
* Prepare a dataset for metadata generation
* Generate an initial technical summary of a dataset

## Inputs

The user may provide one or more of the following:

* A dataset file, such as CSV, TSV, Excel, Parquet, JSON, GeoJSON, or similar
* A folder containing datasets
* Existing documentation, such as a README, codebook, protocol, or schema
* Optional context about the dataset’s purpose, source, geography, or domain

## Outputs

Create a structured dataset profile with the following sections:

1. Dataset overview
2. File-level metadata
3. Column-level profile
4. Missingness summary
5. Duplicate and uniqueness summary
6. Value distribution summary
7. Date and time coverage, if applicable
8. Geographic coverage, if applicable
9. Potential identifiers and keys
10. Data quality observations
11. Inferred metadata candidates
12. Questions for human review

## Required behavior

When profiling the dataset:

* Inspect the actual dataset whenever a file is available.
* Do not rely only on column names if values are available.
* Infer data types from both column names and observed values.
* Clearly distinguish observed facts from inferred assumptions.
* Do not modify the original dataset.
* Do not expose sensitive row-level data unnecessarily.
* Use aggregate summaries instead of listing many raw values.
* When showing example values, use a small number of representative examples.
* Flag fields that may contain personal, sensitive, restricted, or identifiable information.
* Mark uncertainty explicitly.

## File-level metadata to capture

For each dataset file, report:

* File name
* File format
* File size, if available
* Number of rows
* Number of columns
* Encoding, if detectable
* Delimiter, if applicable
* Sheet names, if applicable
* CRS or geometry type, if geospatial
* Date profiled
* Any read/parsing issues

## Column-level metadata to capture

For each column, report:

* Column name
* Inferred data type
* Number of non-null values
* Number of missing values
* Percent missing
* Number of unique values
* Example values
* Potential semantic meaning
* Potential role, such as identifier, date, category, measure, geography, or free text
* Data quality notes
* Confidence level: high, medium, or low

## Data quality checks

Check for:

* Fully empty columns
* Duplicate rows
* Potential duplicate identifiers
* Inconsistent data types within a column
* Unexpected missingness
* Suspicious placeholder values, such as 999, -99, Unknown, N/A, or blank strings
* Outliers in numeric columns
* Invalid dates
* Mixed date formats
* Inconsistent categorical values
* Columns with high cardinality
* Columns that may contain personally identifiable information
* Columns that may contain sensitive health, location, demographic, or partner data

## Date and time inference

If date-like columns are present, infer:

* Earliest observed date
* Latest observed date
* Date format
* Granularity, such as year, month, day, week, or timestamp
* Whether the date appears to represent collection date, report date, event date, model run date, or another date type

If the meaning of a date column is unclear, mark it as uncertain.

## Geographic inference

If geography-like columns are present, infer:

* Countries
* Administrative levels
* Facility names
* Coordinates
* Spatial identifiers
* Coordinate reference system, if available
* Geographic granularity

Flag cases where location data may create re-identification or sensitivity risk.

## Identifier inference

Identify columns that may be:

* Primary keys
* Composite keys
* Foreign keys
* Person identifiers
* Household identifiers
* Facility identifiers
* Geographic identifiers
* Survey cluster identifiers
* Model run identifiers

For each possible identifier, explain the evidence.

## Output format

Return the dataset profile in clear markdown.

When useful, include a compact table like this:

| Column | Type | Missing | Unique | Example values | Likely meaning | Notes | Confidence |
| ------ | ---: | ------: | -----: | -------------- | -------------- | ----- | ---------- |

Also include a machine-readable summary when the user may use the output downstream:

```yaml
dataset_profile:
  file_name:
  file_format:
  row_count:
  column_count:
  date_profiled:
  inferred_temporal_coverage:
    start:
    end:
    source_column:
    confidence:
  inferred_geographic_coverage:
    values:
    source_columns:
    confidence:
  possible_identifiers:
    - column:
      reason:
      confidence:
  data_quality_flags:
    - issue:
      severity:
      affected_columns:
  columns:
    - name:
      inferred_type:
      missing_count:
      missing_percent:
      unique_count:
      example_values:
      likely_meaning:
      role:
      notes:
      confidence:
```

## Confidence scoring

Use the following guidance:

* High confidence: directly observed in the dataset or strongly supported by values and names.
* Medium confidence: likely based on column names, patterns, or common conventions.
* Low confidence: speculative or requires domain knowledge.

Always include the confidence level for inferred meanings.

## Human review questions

End with a short section called `Questions for human review`.

Include questions about:

* Dataset purpose
* Source or owner
* License or access restrictions
* Meaning of ambiguous columns
* Whether inferred identifiers are correct
* Whether sensitive fields should be masked, removed, or restricted
* Whether temporal and geographic coverage are correct

## Do not do the following

Do not:

* Invent dataset purpose if it is not present.
* Invent source, owner, license, or collection methodology.
* Assume that a column is safe to publish because it lacks obvious names.
* Print large amounts of raw data.
* Change, clean, or overwrite the dataset unless explicitly asked.
* Produce final publication-ready metadata without noting fields that need human review.
