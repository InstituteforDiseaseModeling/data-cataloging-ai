# Catalog a Dataset

Use this skill when the user wants to fill out a dataset's **data profile** — `DataProfile.xlsx`'s "Metadata" sheet (18 fields) and "DataBio" sheet (22 data biography questions), drafted and reviewed together in one workflow.

`DataDict.xlsx` (the data dictionary, one row per variable) is a **separate, optional deliverable**, not an automatic part of this skill's output. A dataset can have more than one data dictionary — e.g., a bundle of several distinct files may warrant a dictionary per file rather than one combined file — so it's never assumed. See "Offering the data dictionary" below for when and how to bring it up.

**A note on terminology:** "Data Biography" refers specifically to the 22 narrative questions on `DataProfile.xlsx`'s DataBio sheet (see the `data-bio` skill) — a framework term from We All Count for the equity/provenance-focused contextual questions, not a name for the whole profile. Keep this distinction in your own language when talking to the user. That said, don't let this precision affect *routing*: the phrase has historically been used here for the whole profile too, so an ambiguous request to fill out "a data biography" still defaults to this skill (see "When to use this skill") even though you'll describe things precisely once you're working.

This skill is the primary entry point for filling out a data profile. It drafts everything from available sources, collects missing information from the user in a single structured Q&A, incorporates the answers, and automatically generates a formatted Excel file — no separate spreadsheet step required.

## When to use this skill

Use this skill when the user asks to:

* Fill out a data profile — metadata and data biography together
* Generate DataProfile.xlsx
* Run both tabs (metadata, data bio) at once
* Fill out "a data biography" or "a data bio" **without clarifying they mean only the narrative questions** — that phrase has historically also been used at this org for the whole data profile, so default here rather than routing to `data-bio` alone. Only use `data-bio` by itself if the user explicitly says they don't want metadata included this time.

## Inputs

The user may provide one or more of the following:

* A dataset file (CSV, Excel, Parquet, Stata .dta, JSON, etc.)
* A folder of datasets
* Supporting documentation (protocol, questionnaire, published papers, README, codebook, existing data dictionary)
* A URL — either a direct link to a downloadable data file, or a link to a page describing the dataset
* Previously generated outputs from the `metadata`, `data-bio`, or `data-dictionary` skills
* User-provided context about the dataset

**Mode A** (full data): dataset file available for direct inspection.
**Mode B** (documentation only): only supporting docs available — e.g., due to a DUA. Note this explicitly.

Before using Mode A, check for signals that the dataset may be classified Restricted, Sensitive, or Highly Sensitive (a known classification, a DUA, a confidentiality notice, or the researcher's own description). If present, do not open the dataset file at all — run Mode B and tell the researcher why. See `assess-dataset`'s "Sensitive data classification gate" for exactly when a researcher's authorization is (and isn't) enough to proceed — a DUA/DSA signal specifically requires reading the agreement's actual terms, not just the researcher's say-so — and for the minimize-what-you-inspect rule once authorized.

## Offering the data dictionary

Once Mode A is confirmed (the dataset file can actually be read — not blocked by the sensitivity gate above), ask the researcher whether they'd also like a data dictionary generated, as a separate file. For example:

> "Since I can read the actual data, would you also like me to fill out a data dictionary (`DataDict.xlsx`) for it? That's a separate file from the data profile — if this is a bundle of several distinct files, I can generate a dictionary per file instead of one combined one, whichever makes more sense here."

* If they decline or the dataset is Mode B (no readable file), proceed with just the data profile (Phase 1 below drafts only Metadata + DataBio).
* If they accept and there's a single coherent dataset file, apply `data-dictionary`'s logic as an additional pass and generate `DataDict.xlsx` alongside the profile (see Phase 3).
* If they accept and the dataset is a bundle of multiple distinct files, ask whether they want one combined dictionary (using the `file_name` column to distinguish rows, which `data-dictionary` already supports) or a separate `DataDict.xlsx` per file. For separate files, draft and generate each independently with its own distinguishing `dataset_name` (e.g. `<Dataset>_<ComponentName>`) so the output filenames don't collide — see Phase 3 for the exact generation command.

Don't default to including the data dictionary just because Mode A applies — always ask first.

---

## Step 0: Locate the SharePoint templates and this dataset's folder

`DataProfile.xlsx` (and `DataDict.xlsx`, if offered and accepted) are not bundled with this skill — the master copies live in a SharePoint "Data Profiles" library, and this step resolves where that library is synced locally on this machine. Do this before Phase 1.

1. Check whether a config file exists at `${CLAUDE_PLUGIN_DATA}/cataloging_config.json` (e.g. via `cat "$CLAUDE_PLUGIN_DATA/cataloging_config.json"`).
   * **Exists**: read `data_profiles_root` and `templates_dir` from it and continue.
   * **Missing (first time on this machine)**: ask the researcher for the local path to their OneDrive-synced "Data Profiles" folder — the one containing a `_Templates_` subfolder with `DataProfile.xlsx`/`DataDict.xlsx`. Explain plainly that this requires having synced that SharePoint library via OneDrive first (in the browser: "Add shortcut to OneDrive" on the library, a one-time action) if they haven't done so. Once given, run:
     ```
     python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --set-data-profiles-root "<path they gave>"
     ```
     This saves the config to `${CLAUDE_PLUGIN_DATA}/cataloging_config.json`, which persists across plugin updates — never ask again on this machine.
2. Determine the dataset's folder name from `dataset_name` (spaces → underscores, matching how output filenames are already derived). This resolves to `<data_profiles_root>/<DatasetFolder>/` — the destination for `<Dataset>_DataProfile.xlsx` and, if applicable, one or more `..._DataDict.xlsx` files. It doesn't need to exist yet; `generate_catalog.py` creates it automatically at generation time.
3. Check that same folder for the raw dataset file itself before looking elsewhere for Mode A/B resolution — datasets are expected to be deposited directly alongside their profile, in that folder. If it's not there, fall back to a link in documentation/user-provided context (e.g. to a OneDrive location) or ask the researcher directly, same as usual.

---

## Workflow — three phases, in order

Do not skip or reorder phases.

---

### Phase 1: Draft the data profile (plus variables, if offered and accepted)

If the user provides a URL instead of, or in addition to, an uploaded file, resolve it first — see `data-bio`'s Step 1 for the full procedure: fetch it, determine whether it's a direct data file or a documentation/landing page, **stop and ask if the page links to multiple candidate files** rather than guessing, and if there is a single unambiguous file, download it and state plainly what was pulled (file name, source URL, format, size) before drafting anything.

Read all provided sources. Apply the logic of the `metadata` and `data-bio` skills to produce complete drafts for both tabs simultaneously. If the data dictionary was offered (see "Offering the data dictionary" above) and accepted, also apply `data-dictionary`'s logic to draft the `variables` array in the same pass — otherwise omit `variables` entirely.

For each field or question, determine:

* `value` — the draft answer, or leave blank if it cannot be determined from available sources
* `source` — which document, file, or observation the value came from
* `confidence` — High / Medium / Low
* `needs_review` — true if the field needs human confirmation or input; false if it is well-supported
* `review_notes` — a brief specific question to ask the human, only if needs_review is true

**Write the draft(s) to `catalog_draft.json`** in the current working directory using the schema below. Do this before presenting anything to the user.

After writing the file, present a summary table like this (drop the VARIABLES column entirely if the data dictionary wasn't offered/accepted):

```
Mode: [A / B]
Sources used: [list]

                    METADATA   DATA BIO   [VARIABLES]   TOTAL
High confidence       X / 18     X / 22     [X / N]
Medium confidence     X / 18     X / 22     [X / N]
Low confidence        X / 18     X / 22     [X / N]       → needs review
```

High confidence = auto-filled, well-supported, no review needed.
Medium confidence = auto-filled with a best guess that needs human confirmation.
Low confidence = could not determine from sources; open question for human.

Every field and question gets reviewed in Phase 2, regardless of confidence — Confidence just tells the researcher where to look most closely.
```

---

### Phase 2: Review — Metadata as a whole, then DataBio section by section

No tiers, no rounds split by priority. Two passes, in order:

**Pass 1 — Metadata, all at once**

Present all 18 fields together as one table (mirroring `metadata`'s own Output format: `Field | Draft value | Source | Confidence | Needs review`) — every field, not just the ones flagged `needs_review`. Ask the researcher to approve as-is or correct any field(s). Apply corrections, show the corrected table again if anything changed, and don't move to Pass 2 until they approve.

Never ask about Storage/repository location, Data steward, or Data Catalog location — those three fields are out of scope for this skill (see `metadata`'s "Fields out of scope for this skill"); leave them blank in every case.

**Pass 2 — DataBio, section by section**

Present sections A through F one at a time, exactly as `data-bio`'s own "Section-by-section review and approval" step: for each section, show every question's `response`, `confidence`, and `source` — not just flagged ones — ask the researcher to approve as-is or request changes, and repeat until they approve that section before moving to the next. Do not present more than one section at a time.

**If the data dictionary was offered and accepted**, add a third pass for `variables` — one table of all drafted rows (mirroring `data-dictionary`'s own Output format), approve as-is or correct, in one pass.

**Phrasing draft values during either pass**

* A Medium-confidence draft: show the inferred value and ask the researcher to confirm or correct it. Example:
  > `[METADATA: Geographic coverage]` I inferred: *"Bangladesh; 13 poorest districts concentrated in the northern monga region."* Does this look right? If not, please correct it.
* A Low-confidence or blank item: ask an open-ended question with no suggested answer. Example:
  > `[METADATA: IDM Data owner]` Who is the IDM person or team with final decision-making authority over this dataset's access and use?

**Incorporating answers**

Update `catalog_draft.json` as corrections come in, before showing the next table/section:
* For anything the researcher corrects: set `value`/`response` to their answer, `source` to `"Human input."`, `needs_review` to `false`, clear `review_notes`.
* For anything approved as-is that was AI-drafted: compose `source` per `data-bio`'s Output format convention ("Generated by AI, reviewed and approved by {reviewer}." + `" Source: {doc}"` if applicable) — this is what actually shows in the DataBio sheet's Source column; for Metadata it's harmless bookkeeping only, since that sheet has no Source column.
* For anything the researcher explicitly skips: leave `needs_review: true`, keep the existing `value`/`response` (blank or drafted) as-is, and move on rather than blocking.

---

### Phase 3: Generate Excel

After `catalog_draft.json` is updated, run:

```
python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --only metadata,databio
```

Using `$CLAUDE_PLUGIN_ROOT` (not a bare relative path) is required — this script ships inside the plugin, and the researcher's working directory has nothing to do with where it's installed. The script reads `catalog_draft.json` from the current working directory, resolves both the template source and the output destination from the config saved in Step 0, and writes `<Dataset>_DataProfile.xlsx` (Metadata + DataBio, filled together in one pass) directly into `<data_profiles_root>/<DatasetFolder>/` — the OneDrive-synced SharePoint folder, not a local scratch location.

**If the data dictionary was offered and accepted**, generate it too, right after the profile:

* **Single combined dictionary** (one dataset file, or a bundle documented in one dictionary via the `file_name` column): run
  ```
  python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --only datadict
  ```
  against the same `catalog_draft.json` — produces `<Dataset>_DataDict.xlsx` in the same folder.
* **Separate dictionary per file** in a multi-file bundle: for each component, write its own small JSON (same `variables` schema, its own distinguishing `dataset_name`, e.g. `<Dataset>_<ComponentName>`) and run
  ```
  python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --input catalog_draft_<component>.json --output-dir "<data_profiles_root>/<DatasetFolder>" --only datadict
  ```
  once per component, so each lands in the same dataset folder as `<Dataset>_<ComponentName>_DataDict.xlsx` without overwriting the others.

Because that folder is synced, saving there is the entire "delivery" step — OneDrive pushes it to SharePoint automatically, typically within about a minute. There is no export/upload step to perform or mention.

Neither sheet uses a yellow-filled cell or Excel comment for unresolved items — this data gets synced into Databricks, and formatting doesn't survive that sync. The two sheets handle it differently, and in both cases what actually drives the display is whether the field/question ended up genuinely **blank**, not the `needs_review` flag itself:

* Metadata sheet (`Field`/`Response` only): an unresolved field is just a blank Response cell.
* DataBio sheet (adds `Confidence (AI-Assisted only)` and `Source (AI-Assisted only)`): a blank Answer shows Confidence as "Needs human input" and Source carrying the `review_notes` explanation of what's needed. A question that was drafted with real content but left unanswered after Phase 2 (`needs_review: true`, `value`/`response` non-blank per "Incorporating answers" above) instead shows its original drafted confidence — the Excel file doesn't currently distinguish "drafted and skipped" from "drafted and confirmed" the way it distinguishes blank from populated. Point this out to the researcher in the summary if anything important was skipped this way, since it won't be visually obvious in the spreadsheet.

If Step 0 wasn't completed (no config, or `$CLAUDE_PLUGIN_ROOT`/`$CLAUDE_PLUGIN_DATA` unset because this isn't running as an installed plugin), the script's own error message explains what's missing — surface that message to the researcher rather than guessing at a fix.

Tell the user the full path(s) to every generated Excel file (the profile, plus any data dictionary/dictionaries), and that they're already synced to SharePoint.

---

## catalog_draft.json schema

Write this file at the start of Phase 1 and update it at the end of Phase 2.

```json
{
  "dataset_name": "short descriptive name used to derive output filenames",
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

`variables` is **only present at all if the data dictionary was offered and accepted** (see "Offering the data dictionary" above) — omit the key entirely otherwise, don't write an empty array. If separate per-file dictionaries were chosen for a multi-file bundle, each component gets its own small JSON with just `dataset_name` and `variables` (no `metadata`/`data_bio` needed in those files).

The metadata array must contain exactly these 18 fields in order (see the `metadata` skill for full derivation guidance on each):
1. Dataset title / name
2. Dataset short description
3. Subject(s)
4. Dataset version
5. Data provider / source organization
6. Data Provider Point of Contact
7. Production Date
8. Update frequency / rounds / waves
9. IDM Data owner
10. Data Location(s)
11. Citation / attribution
12. Sensitive data classification
13. Data Sharing Agreement (URL, where applicable)
14. Geographic coverage
15. Unit of observation / granularity
16. Temporal Coverage (Start)
17. Temporal Coverage (End)
18. Related dataset location(s)

Do not include Storage/repository location, Data steward, or Data Catalog location in this array — those three fields are out of scope (a different team fills them in later) and must be left blank in the output.

The data_bio array must contain exactly 22 entries covering Q1–Q22 across sections A–F.

If present, the variables array contains one entry per variable. Include all variables findable from the data or documentation. Flag ambiguous or sensitive variables with needs_review: true.

---

## Required behavior

* Always write `catalog_draft.json` before the Q&A — auto-filled content is never lost regardless of conversation length.
* Always present Phase 1 summary with the High / Medium / Low confidence breakdown per tab before asking any questions.
* Present Metadata as one full table (Pass 1), then DataBio one section at a time (Pass 2) — never combine Pass 1 and a DataBio section, or two DataBio sections, into a single message.
* Show the inferred draft value for Medium confidence questions. Ask open-ended for Low-confidence or blank items.
* Update `catalog_draft.json` after each pass/section before presenting the next.
* If the user skips something, generate the Excel file(s) anyway. Never fill an unresolved field/question with placeholder text — an item with no draft at all stays blank (plus "Needs human input" Confidence on the DataBio sheet); one that had a real draft but was skipped keeps that draft as-is (see the caveat in "Phase 3: Generate Excel" about this not being visually flagged).
* Once Mode A is confirmed, always ask about the data dictionary before drafting — never assume the answer either way.
* Always end this skill by running `generate_catalog.py` for the profile (and, if accepted, the data dictionary/dictionaries) and confirming every output file path.
* Complete Step 0 before Phase 1 — do not assume the templates or dataset folder location.

## Relationship to other skills

The `metadata` and `data-bio` skills can be run individually when the user only needs one sheet — they write into the same `<Dataset>_DataProfile.xlsx` output without clobbering each other's sheet (see `generate_catalog.py`'s load-if-exists behavior). `data-dictionary` is fully independent — run it standalone any time, or accept this skill's offer to run it as part of the same session. Use `catalog-dataset` when the user wants the full data profile (metadata + data biography) in a single workflow with automatic Excel output.

## Do not do the following

Do not:
* Combine Pass 1 (Metadata) and any DataBio section into one message, or combine two DataBio sections together.
* Show a guessed value for Low confidence fields — ask open-ended instead.
* Skip showing the inferred value for Medium confidence fields — always show it and ask for confirmation.
* Generate the Excel before Metadata is approved and every DataBio section is approved (or the user has explicitly skipped something).
* Invent an IDM Data owner, Data Provider Point of Contact, consent details, or Data Sharing Agreement terms.
* Ask about or fill Storage/repository location, Data steward, or Data Catalog location — out of scope, a different team's job.
* Skip writing `catalog_draft.json` before the Q&A.
* End the skill without running `python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py"`.
* Invoke `generate_catalog.py` with a bare relative path — always use `$CLAUDE_PLUGIN_ROOT`.
* Refer the user back to a previous step to create the spreadsheet — generate it automatically.
* Call the output "a DataBio" — that name belongs to the DataBio sheet specifically, not the whole catalog.
* Guess which file a landing page refers to when it links to multiple candidates — ask first.
* Draft from a downloaded file without first telling the user exactly what was pulled and from where.
* Open a dataset file once a Restricted/Sensitive/Highly Sensitive signal is present, without the researcher's explicit authorization — see the Sensitive data classification gate in Inputs.
* Rely on a researcher's authorization alone when the signal is a DUA/DSA — its actual terms must be read first; they can prohibit AI/automated processing outright.
* Inspect the whole file once authorized, when the draft only needs a subset of columns/rows.
* Automatically draft or generate a data dictionary without asking first, even when Mode A applies.
* Force a multi-file bundle into one combined data dictionary without asking whether separate per-file dictionaries would serve better.
