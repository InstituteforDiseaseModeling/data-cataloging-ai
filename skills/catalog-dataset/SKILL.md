# Catalog a Dataset

Use this skill when the user wants to generate a full dataset catalog — filling all three files: `Metadata.xlsx` (18 fields), `DataBio.xlsx` (22 data biography questions), and `DataDict.xlsx` (one row per variable).

**A note on terminology:** "Data Biography" refers specifically to the 22 narrative questions in `DataBio.xlsx` (see the `data-bio` skill) — a framework term from We All Count for the equity/provenance-focused contextual questions, not a name for the whole three-file bundle. This skill produces a **dataset catalog** (metadata + data biography + data dictionary together), not "a DataBio." Keep this distinction in your own language when talking to the user, too.

This skill is the primary entry point for data cataloging. It drafts all three files from available sources, collects missing information from the user in a single structured Q&A, incorporates the answers, and automatically generates three formatted Excel files — no separate spreadsheet step required.

## When to use this skill

Use this skill when the user asks to:

* Fully catalog a dataset — metadata, data biography, and data dictionary together
* Generate Metadata.xlsx, DataBio.xlsx, and DataDict.xlsx in one pass
* Run all three tabs (metadata, data bio, variables) at once

## Inputs

The user may provide one or more of the following:

* A dataset file (CSV, Excel, Parquet, Stata .dta, JSON, etc.)
* A folder of datasets
* Supporting documentation (protocol, questionnaire, published papers, README, codebook, existing data dictionary)
* URLs to published papers or documentation
* Previously generated outputs from the `metadata`, `data-bio`, or `data-dictionary` skills
* User-provided context about the dataset

**Mode A** (full data): dataset file available for direct inspection.
**Mode B** (documentation only): only supporting docs available — e.g., due to a DUA. Note this explicitly.

---

## Workflow — three phases, in order

Do not skip or reorder phases.

---

### Phase 1: Draft all three tabs

Read all provided sources. Apply the logic of the `metadata`, `data-bio`, and `data-dictionary` skills to produce complete drafts for all three tabs simultaneously.

For each field or question, determine:

* `value` — the draft answer, or `"Requires human input"` if it cannot be determined from available sources
* `source` — which document, file, or observation the value came from
* `confidence` — High / Medium / Low
* `needs_review` — true if the field needs human confirmation or input; false if it is well-supported
* `review_notes` — a brief specific question to ask the human, only if needs_review is true

**Write all three drafts to `catalog_draft.json`** in the current working directory using the schema below. Do this before presenting anything to the user.

After writing the file, present a summary table like this:

```
Mode: [A / B]
Sources used: [list]

                    METADATA   DATA BIO   VARIABLES   TOTAL
High confidence       X / 18     X / 22    X / N
Medium confidence     X / 18     X / 22    X / N
Low confidence        X / 18     X / 22    X / N       → needs review
```

High confidence = auto-filled, well-supported, no review needed.
Medium confidence = auto-filled with a best guess that needs human confirmation.
Low confidence = could not determine from sources; open question for human.

Fields at Medium and Low confidence are presented to the user in Phase 2.
```

---

### Phase 2: Human Q&A — three sequential rounds

This phase collects missing information in three separate rounds, one tier at a time. Present each round, wait for the user's response, then move to the next. Do not combine tiers into a single message.

**Tier definitions**

* **Critical** — required for the catalog to be usable or compliant: data owner, data steward/contact, storage location, access level/DUA terms, consent details (Q16–Q19), inappropriate uses (Q4)
* **Important** — needed for catalog users to understand and use the dataset: version, citation/DOI, current use (Q3), data chain (Q8), methodology details, equity caveats (Q22)
* **Optional** — enhances the record but not blocking: update frequency, related datasets, enumerator training, blinding details, variable coding edge cases

**Question format by confidence level**

How to phrase each question depends on the confidence of the auto-filled draft:

* **Medium confidence** (a best guess exists): Show the inferred value and ask the user to confirm or correct it. Example:
  > `[METADATA: Geographic coverage]` I inferred: *"Bangladesh; 13 poorest districts concentrated in the northern monga region."* Does this look right? If not, please correct it.

* **Low confidence** (no reasonable guess): Ask an open-ended question with no suggested answer. Example:
  > `[METADATA: Data owner]` Who is the institution or person with final decision-making authority over this dataset's access and use?

**Round 1: Critical questions**

Present only Critical fields needing review. Number them starting from 1. End with:

> "Answer by number. Write 'skip' to leave a Critical field blank (it will be yellow-flagged in the output). When you're ready, I'll move on to Important questions."

Wait for the user's response before presenting Round 2.

**Round 2: Important questions**

After incorporating Round 1 answers, present Important fields. Number them starting from 1. End with:

> "Answer by number. Write 'skip' for anything you don't know. When you're ready, I'll finish with Optional questions."

Wait for the user's response before presenting Round 3.

**Round 3: Optional questions**

After incorporating Round 2 answers, present Optional fields. Number them starting from 1. End with:

> "Answer by number, or write 'skip all' to skip these entirely. I'll generate the Excel files after this."

Wait for the user's response, then proceed to Phase 3.

**Incorporating answers after each round**

After each round's response, update `catalog_draft.json` before presenting the next round:
* For answered questions: set `value` to the human's answer, `source` to `"Human input"`, `needs_review` to `false`, clear `review_notes`
* For skipped or unanswered fields: keep `needs_review: true`, keep existing `value`

If the user says "skip all" or "unknown for all" for any round, note it, keep all fields in that tier flagged, and move on.

---

### Phase 3: Generate Excel

After `catalog_draft.json` is updated, run:

```
python generate_catalog.py
```

The script reads `catalog_draft.json` from the current working directory and fills the three template files (`Metadata.xlsx`, `DataBio.xlsx`, `DataDict.xlsx`) from the project root, writing three dataset-specific outputs named from `dataset_name`:

* `<Dataset>_Metadata.xlsx`
* `<Dataset>_DataBio.xlsx`
* `<Dataset>_DataDict.xlsx`

Fields and questions still flagged `needs_review` after the Q&A rounds appear with a yellow-filled cell and an Excel comment carrying the review question, rather than a separate column — none of the three templates have source/confidence/needs_review columns.

If `generate_catalog.py` is not found in the working directory, alert the user and provide its expected path: the project root of the data-cataloging-ai repository.

Tell the user the full paths to all three generated Excel files.

---

## catalog_draft.json schema

Write this file at the start of Phase 1 and update it at the end of Phase 2.

```json
{
  "dataset_name": "short descriptive name used to derive all three output filenames",
  "generated_date": "YYYY-MM-DD",
  "mode": "A or B",
  "sources_used": ["list of source documents and files consulted"],
  "metadata": [
    {
      "field": "Dataset title / name",
      "value": "",
      "source": "",
      "confidence": "High",
      "needs_review": false,
      "review_notes": ""
    }
  ],
  "data_bio": [
    {
      "section": "A: Purpose & Intended Use",
      "question_num": "Q1",
      "question": "What does this dataset measure?",
      "response": "",
      "source": "",
      "confidence": "High",
      "needs_review": false,
      "review_notes": ""
    }
  ],
  "variables": [
    {
      "file_name": "",
      "variable_name": "",
      "variable_label": "",
      "definition": "",
      "data_type": "",
      "unit": "",
      "allowed_values_codes": "",
      "missing_unknown_codes": "",
      "source_derivation": "",
      "numerator": "",
      "denominator": "",
      "sensitive": false,
      "data_quality_notes": "",
      "confidence": "High",
      "needs_review": false,
      "review_notes": ""
    }
  ]
}
```

The metadata array must contain exactly these 18 fields in order:
1. Dataset title / name
2. Dataset short description
3. Dataset version
4. Date catalog last updated
5. Data provider / source organization
6. Extract / release date
7. Update frequency / rounds / waves
8. Data owner
9. Data steward / primary contact
10. File inventory
11. Storage / repository location
12. Access level / restrictions
13. Citation / attribution
14. Sensitive data classification
15. Geographic coverage
16. Temporal coverage / reference period
17. Unit of observation / granularity
18. Related dataset location(s)

The data_bio array must contain exactly 22 entries covering Q1–Q22 across sections A–F.

The variables array contains one entry per variable. Include all variables findable from the data or documentation. Flag ambiguous or sensitive variables with needs_review: true.

---

## Required behavior

* Always write `catalog_draft.json` before the Q&A — auto-filled content is never lost regardless of conversation length.
* Always present Phase 1 summary with the High / Medium / Low confidence breakdown per tab before asking any questions.
* Present tiers one at a time in order: Critical → Important → Optional. Never combine tiers in one message.
* Show the inferred draft value for Medium confidence questions. Ask open-ended for Low confidence questions.
* Always set "Date catalog last updated" (the Metadata field) to today's date automatically.
* Update `catalog_draft.json` after each round before presenting the next round.
* If the user skips Critical questions, generate the Excel files anyway — but yellow-flag all unanswered Critical fields in the output.
* Always end this skill by running `python generate_catalog.py` and confirming the output file paths.

## Relationship to other skills

The `metadata`, `data-bio`, and `data-dictionary` skills can be run individually when the user only needs one file. Use `catalog-dataset` when the user wants all three (the full catalog) in a single workflow with automatic Excel output.

## Do not do the following

Do not:
* Mix tiers — present Critical, Important, and Optional as separate rounds, one at a time.
* Show a guessed value for Low confidence fields — ask open-ended instead.
* Skip showing the inferred value for Medium confidence fields — always show it and ask for confirmation.
* Generate the Excel before all three rounds are complete (or the user has explicitly skipped a round).
* Invent data owner, steward, consent details, storage location, or access conditions.
* Skip writing `catalog_draft.json` before the Q&A.
* End the skill without running `python generate_catalog.py`.
* Refer the user back to a previous step to create the spreadsheet — generate it automatically.
* Call the whole three-file output "a DataBio" — that name belongs to `DataBio.xlsx` specifically.
