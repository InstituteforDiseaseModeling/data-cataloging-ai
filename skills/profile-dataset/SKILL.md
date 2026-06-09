# Assess Dataset Usability

Use this skill when the user wants to evaluate whether a dataset is ready to use for analysis — covering data quality and analytical fitness.

This skill produces a scored usability assessment that identifies blockers, gaps, and specific recommendations for improvement. It can also serve as input to downstream metadata generation skills.

## When to use this skill

Use this skill when the user asks to:

* Assess whether a dataset is usable or analysis-ready
* Identify data quality issues before analysis
* Evaluate dataset fitness for a specific purpose
* Check completeness, consistency, or structural suitability
* Get a usability score or readiness rating for a dataset
* Understand what would need to be fixed before the dataset can be used

## Inputs

The user may provide one or more of the following:

* A dataset file, such as CSV, TSV, Excel, Parquet, JSON, GeoJSON, or similar
* A folder containing datasets
* Existing documentation, such as a README, codebook, protocol, or schema
* Optional context about the intended analysis, use case, or audience

If a specific analysis purpose or question is provided, use it to focus the fitness assessment.

## Outputs

Produce a structured usability assessment with the following sections:

1. Dataset snapshot
2. Data quality assessment (scored)
3. Analytical fitness assessment (scored)
4. Overall usability rating
5. Top issues and recommended actions
6. Questions for human review

## Scoring guide

Use the following three-point scale consistently across all scored dimensions:

* **High**: No significant issues. The dataset meets expectations for this dimension with at most minor, easily corrected problems.
* **Medium**: Noticeable issues that may affect analysis quality or require remediation before use. Usable with caution.
* **Low**: Serious issues that are likely to block or significantly compromise analysis. Remediation is required.

Always include the evidence or observation that justifies the score.

## Dataset snapshot

Before scoring, provide a brief orientation:

* File name and format
* Number of rows and columns
* Inferred unit of observation (what each row represents)
* Date range or temporal coverage, if present
* Geographic scope, if present
* Any read or parsing issues

This section is factual. Do not score it.

## Data quality assessment

Assess and score each of the following dimensions.

### Completeness

Score based on the extent and pattern of missing values.

Check for:

* Percent missing per column
* Columns with more than 20% missing
* Columns that are entirely or nearly empty
* Whether missingness appears systematic or random
* Suspicious placeholder values that mask missingness, such as 999, -99, Unknown, N/A, or blank strings

Score guidance:

* High: No columns with substantial missingness; no suspicious placeholders.
* Medium: Some columns missing, but core variables are mostly complete; or missingness is explainable.
* Low: Key columns are heavily missing or placeholder values are widespread.

### Consistency

Score based on whether values are internally coherent.

Check for:

* Mixed data types within a column
* Inconsistent categorical values, such as "male", "Male", and "M" for the same category
* Mixed date formats within a date column
* Outliers or values outside expected ranges in numeric columns
* Columns where values contradict each other, such as end date before start date
* Invalid dates, such as February 30

Score guidance:

* High: Values are consistent and well-formed throughout.
* Medium: Some inconsistencies present but confined to a few columns or rows; likely correctable.
* Low: Widespread inconsistencies or type mixing that would require significant cleaning.

### Uniqueness

Score based on duplication and identifier integrity.

Check for:

* Fully duplicate rows
* Near-duplicate rows
* Columns that appear to be identifiers but contain repeated values
* Expected unique identifiers that are not actually unique

Score guidance:

* High: No unexpected duplicates; identifiers behave as expected.
* Medium: Some duplicates present; may be intentional or limited in scope.
* Low: Widespread duplication or identifier integrity is broken.

### Validity

Score based on whether values fall within expected or meaningful ranges.

Check for:

* Numeric values outside plausible domain ranges
* Date values in the far future or far past relative to the apparent dataset context
* Categorical values not from an expected set, if a set can be inferred
* Free text fields with unusual or potentially erroneous content

Score guidance:

* High: Values appear valid and plausible throughout.
* Medium: Some suspicious values present but confined; may require spot-checking.
* Low: Validity problems are pervasive or affect core variables.

## Analytical fitness assessment

Assess and score each of the following dimensions.

### Unit of observation clarity

Score based on whether the structure of the dataset is clear enough for analysis.

Check for:

* Whether it is clear what each row represents
* Whether a primary key or unique row identifier exists
* Whether the dataset is in a tidy or analysis-ready structure
* Whether wide-format or nested structures would require reshaping before use
* Whether column names are interpretable without documentation

Score guidance:

* High: Unit of observation is unambiguous; structure is analysis-ready.
* Medium: Unit is inferable but not explicit; or minor reshaping may be needed.
* Low: Unit of observation is unclear or the structure requires significant transformation.

### Variable coverage

Score based on whether the dataset contains the variables needed for meaningful analysis.

This dimension depends on context. If the user has provided an analysis purpose, score against that purpose. Otherwise, score based on whether the dataset appears internally complete for its apparent subject.

Check for:

* Presence of key outcome, exposure, or grouping variables, if inferable
* Whether important dimensions such as time, geography, or population are represented
* Whether supporting variables such as denominators, weights, or stratifiers are present
* Columns that are present but uninformative or empty

Score guidance:

* High: Variables needed for the apparent purpose are present and populated.
* Medium: Some important variables appear to be missing or are present but poorly populated.
* Low: Core variables needed for analysis are absent or unusable.

### Temporal coverage

Score based on whether time coverage is adequate and clearly represented.

Check for:

* Presence of a date or time variable
* Earliest and latest observed date
* Whether the time range appears complete or has gaps
* Whether the granularity, such as year, month, or day, is sufficient
* Whether the meaning of the date column is clear

If no temporal dimension is present and one is expected for the use case, score Low. If time is not relevant, note that and skip scoring.

Score guidance:

* High: Date coverage is complete, clearly labeled, and at the right granularity.
* Medium: Some date coverage present but gaps, ambiguity, or granularity issues exist.
* Low: Date coverage is missing, severely incomplete, or the date meaning is unclear.

### Spatial coverage

Score based on whether geographic coverage is adequate and clearly represented.

Check for:

* Presence of geographic identifiers, such as country codes, admin names, coordinates
* Whether coverage appears complete for the expected scope
* Whether spatial identifiers are consistent and interpretable
* Whether geographic granularity is sufficient for the intended use

If no spatial dimension is present and one is expected for the use case, score Low. If geography is not relevant, note that and skip scoring.

Score guidance:

* High: Geography is present, consistent, and at the right level of granularity.
* Medium: Some geographic information present but coverage gaps or ambiguity exist.
* Low: Geographic information is missing, inconsistent, or at the wrong level.

### Linkability

Score based on whether the dataset can be joined to other datasets if needed.

Check for:

* Presence of standard identifiers such as ISO country codes, facility codes, or survey IDs
* Whether identifier columns are clearly labeled
* Whether values are in formats compatible with common reference datasets
* Whether join keys are unique and consistently formatted

If the dataset is intended to be standalone and no linkage is needed, note that and skip scoring.

Score guidance:

* High: Standard identifiers are present, consistent, and suitable for joining.
* Medium: Some identifiers present but non-standard, inconsistently formatted, or partially populated.
* Low: No identifiers suitable for linkage, or they are too inconsistent to use.

## Overall usability rating

After scoring all dimensions, provide a single overall usability rating using the same High / Medium / Low scale.

Base the overall rating on:

* The lowest-scoring dimension that is critical for the stated or apparent use case
* The number and severity of Medium and Low scores
* Whether any single issue would block analysis outright

Format:

```
Overall usability: [High / Medium / Low]

Summary: [2–3 sentences describing the main strengths and the most significant barriers to use.]
```

## Top issues and recommended actions

List the three to five most important issues, ordered by impact on usability.

For each issue:

* Name the dimension and specific finding
* Describe the likely impact on analysis
* Suggest a concrete remediation step

Format:

```
1. [Issue]: [What was observed]
   Impact: [How this affects use]
   Recommendation: [Specific action]
```

If the dataset scores High overall, briefly confirm what makes it ready and note any minor items to watch.

## Required behavior

When assessing the dataset:

* Inspect the actual dataset whenever a file is available. Do not rely only on column names.
* Distinguish observed facts from inferences. Use language like "appears to" or "likely" for inferences.
* Do not modify or clean the dataset.
* Do not expose sensitive row-level data. Use aggregate summaries.
* Use representative examples, not raw data dumps.
* Flag columns that may contain personal, sensitive, or identifiable information.
* Be honest about uncertainty. Use confidence qualifiers and the review section.

## Output format

Return the assessment in clear markdown with section headers.

Also include a machine-readable YAML summary:

```yaml
usability_assessment:
  file_name:
  row_count:
  column_count:
  unit_of_observation:
    value:
    confidence:
  date_assessed:
  data_quality:
    completeness:
      score:
      finding:
    consistency:
      score:
      finding:
    uniqueness:
      score:
      finding:
    validity:
      score:
      finding:
  analytical_fitness:
    unit_of_observation_clarity:
      score:
      finding:
    variable_coverage:
      score:
      finding:
    temporal_coverage:
      score:
      finding:
      start:
      end:
    spatial_coverage:
      score:
      finding:
    linkability:
      score:
      finding:
  overall_usability:
    score:
    summary:
  top_issues:
    - dimension:
      finding:
      impact:
      recommendation:
```

## Questions for human review

End with a short section called `Questions for human review`.

Focus questions on what would change the assessment if answered:

* What is the intended analysis or use case?
* Are specific missing values meaningful, such as coded as missing vs. truly absent?
* Are any apparent duplicates expected, such as repeated measures or panel data?
* What is the expected temporal or geographic scope?
* Are any columns intentionally excluded from this file?
* Are there known quality issues the data owner can explain?

## Do not do the following

Do not:

* Invent dataset purpose, source, owner, or methodology.
* Treat inferred meaning as confirmed fact.
* Print large amounts of raw data.
* Change, clean, or overwrite the dataset.
* Assign a High overall rating when critical dimensions score Low.
* Produce a final usability judgment without flagging what could not be verified.
