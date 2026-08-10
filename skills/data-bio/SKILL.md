# Complete Data Bio Tab

Use this skill when the user wants to fill the "Data Bio" sheet of `DataBio.xlsx`.

The Data Bio sheet contains 22 narrative questions across six sections (A–F) adapted from the We All Count Data Biography framework. It captures dataset purpose, provenance, collection methods, coverage, consent, and quality — with a focus on equity, ethics, and responsible data use.

This tab is the most human-judgment-intensive of the three catalog files. This skill extracts as much as possible from available documentation, but it will not guess on equity, consent, or representativeness questions — those require the data owner or steward.

Note: "Data Biography" is this file specifically — the 22 narrative questions, a framework term from We All Count. It is not a name for the whole catalog (Metadata + DataBio + DataDict); see the `catalog-dataset` skill if the user wants all three filled together.

`DataBio.xlsx` has five columns: `Section | Question | Clarification/example | Select from common dropdown options or write in: | Notes/Comments`. Most questions (Q2–Q12, Q14, Q16–Q21) are backed by a controlled vocabulary on the workbook's "Lists" sheet, exposed as an Excel dropdown on the answer column — but the dropdown prompt itself says "Choose from the list, or type your own answer if none fit," so it's a suggestion, not an enforced constraint. Q1, Q13, Q15, and Q22 have no list and are always open narrative text. See "Controlled vocabulary by question" below for the exact allowed values.

This skill follows a four-step interactive process — draft, ask what needs human input, review section by section, then generate the file — see "Workflow" below. Don't jump straight from drafting to generating the Excel file.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete the Data Bio tab in DataBio.xlsx
* Draft narrative responses to data biography questions
* Document dataset purpose, provenance, consent, and quality for a data catalog
* Generate an equity- and ethics-aware dataset description

## Inputs

The user may provide one or more of the following:

* A study protocol or research proposal
* A questionnaire or survey instrument
* Published papers using or describing the dataset
* Existing README or project documentation
* A dataset profile from the `profile-dataset` skill
* A filled METADATA tab
* A URL — either a direct link to a downloadable data file, or a link to a page describing the dataset (see Step 1 for how this is resolved)
* User-provided context about purpose, methods, population, or access

**Mode A** (full data available): use documentation as the primary source; the dataset file may support Section F questions on data quality.
**Mode B** (documentation only): documentation is the only source. This tab is often well-served in Mode B because most questions are about how data was collected — answerable from protocol and papers.

## Outputs

Draft responses to all 22 questions, organized by section A–F. Each question includes:

* Draft response (or "Requires human input")
* Source (what document or input the response was derived from)
* Confidence (High / Medium / Low)
* Needs review flag

Followed by a consolidated "Questions for human review" list.

## Workflow

This is the entry point when the user mentions filling out a data bio/biography specifically (not the full catalog — see "Relationship to other skills"). Follow these steps in order. Do not generate the Excel file before every section has been explicitly approved.

### Step 1: Resolve sources and draft

If the user provides a URL instead of, or in addition to, an uploaded file:

1. Fetch the URL to see what it actually is: a direct downloadable data file (CSV, Excel, JSON, Parquet, a zipped data bundle, a documented API/export endpoint), or a landing/documentation page that describes a dataset and links out to one or more resources.
2. If the page exposes more than one candidate file, version, or resource — per-year extracts, per-region files, multiple formats of the same data, etc. — **do not guess which one the user means**. Stop and list the options, and ask the user to confirm which file(s) to use before downloading or drafting anything.
3. If there is a single, unambiguous downloadable file, download it. Before drafting anything, tell the user exactly what was pulled: file name, source URL, format, and size (plus row/column count if quick to check). This is a transparency checkpoint, not a blocking question — state it plainly as the lead line of your first response so the user has an obvious chance to say "that's not the one" before you go further, then continue into drafting in the same turn.
4. If the page only exposes documentation with no downloadable data, proceed in Mode B and say so explicitly.
5. Record the exact source (URL, and the fetched file name if applicable) in `sources_used`.

Then draft a response to all 22 questions using the derivation logic in "Section A–F" below, following "Controlled vocabulary by question" where applicable. For each question, determine `response`, `source`, `confidence`, `needs_review`, and `review_notes`.

Write the draft to the `data_bio` array of `catalog_draft.json` in the current working directory (create the file with a `dataset_name` and empty `metadata`/`variables` arrays if it doesn't exist yet — see the schema in the `catalog-dataset` skill). Do this before presenting anything to the user.

### Step 2: Ask the questions that need human input

Present only the questions still flagged `needs_review: true` after drafting — this always includes Q4, Q16–Q19, and the equity-judgment portions of Q15 and Q22 (see their sections below), plus anything else that couldn't be determined from available sources. Number them, show what (if anything) was inferred, and ask the user to answer or confirm. One round — do not split this into tiers.

Wait for the user's response before continuing. Update `catalog_draft.json`: for answered questions, set `response` to the human's answer, `source` to `"Human input"`, `needs_review` to `false`. For anything the user explicitly skips, leave `needs_review: true` and move on rather than blocking.

### Step 3: Section-by-section review

Present the questions one section at a time, in order (A → B → C → D → E → F), showing every question's current response — not just the ones that were flagged, since a confidently auto-filled answer may still need the user's editorial correction. For each section:

1. Show the section's questions and current responses.
2. Ask the user to approve as-is or request changes.
3. If they request changes, apply them, update `catalog_draft.json`, and show the revised section again.
4. Repeat until the user approves that section, then move to the next.

Do not move to the next section until the current one is explicitly approved, and do not present more than one section at a time.

### Step 4: Generate the Excel file

Once all six sections are approved, run:

```
python generate_catalog.py --only databio
```

This fills `DataBio.xlsx` from `catalog_draft.json` and writes `<Dataset>_DataBio.xlsx`. Tell the user the full path to the file so they can retrieve it.

## Section A: Dataset Purpose and Intended Use

### Q1: What does this dataset measure?

Derive from: protocol, paper abstract, data documentation, user context.

Describe the primary subject, indicator, or phenomenon captured. Auto-fill potential: **High**.

### Q2: Why was the data originally collected?

Derive from: protocol objectives, paper rationale, grant or project description.

Distinguish original collection purpose from current use (addressed in Q3). Auto-fill potential: **High**.

### Q3: What is the data being used for now?

Derive from: user context, current project documentation.

If the current use differs from the original purpose (Q2), note that distinction. If not provided, flag for review.

Auto-fill potential: **Medium** — depends on user-provided context.

### Q4: What uses of this data would be inappropriate, unsupported, or potentially harmful?

**Always requires human review.** Do not generate a list of inappropriate uses without explicit guidance from the data owner.

Draft: "Requires input from data owner or steward. Consider: uses outside the consent scope, applications to populations not represented in the sample, publication of disaggregated results that could enable identification or cause harm, and uses not aligned with the original data use agreement."

## Section B: Data Provenance

### Q5: Who collected the data?

Derive from: protocol, paper authorship, study acknowledgments.

Include: organization, research team, field data collection partner. Auto-fill potential: **High**.

### Q6: Who provided the data?

Derive from: protocol, paper methods, study description.

Describe the respondents, patients, facilities, administrative sources, or other data providers. Auto-fill potential: **High**.

### Q7: Was the data collected by, for, or in partnership with a government entity?

Derive from: protocol, paper acknowledgments, user context.

Note any government involvement in collection, funding, or oversight. Flag for human confirmation even if documentation suggests an answer.

Auto-fill potential: **Medium**.

### Q8: Has the data changed hands, been combined, or passed through multiple systems?

Derive from: protocol, data processing notes, user context.

Describe any data linkage, transfer, combination with other sources, or system migration. Flag for human confirmation if the full data chain is unclear.

Auto-fill potential: **Medium**.

## Section C: Data Collection Methods

### Q9: How was the data collected?

Derive from: protocol methods section, paper methods section.

Examples: household survey, facility assessment, administrative records, disease surveillance, remote sensing, laboratory, modeling. Auto-fill potential: **High**.

### Q10: What tools, instruments, systems, software, or technologies were used?

Derive from: protocol, paper methods, questionnaire metadata.

Examples: ODK, DHIS2, REDCap, specific survey instruments, GPS devices, analysis software. Auto-fill potential: **High**.

### Q11: If people were asked questions, how were those questions administered?

Derive from: questionnaire, protocol enumerator guidance.

Cover: interviewer-administered vs. self-administered, languages used, enumerator training, respondent burden, approximate interview length.

Auto-fill potential: **Medium** — requires questionnaire or detailed protocol.

### Q12: Were incentives, repeated follow-ups, eligibility rules, or skip patterns used?

Derive from: protocol, questionnaire skip logic, study design section.

Describe any: participant incentives, follow-up attempts, eligibility criteria, questionnaire skip patterns or routing.

Auto-fill potential: **Medium** — requires questionnaire or detailed protocol.

## Section D: Coverage, Scope, and Representativeness

### Q13: What are the geographic, temporal, demographic, and sample-size boundaries?

Derive from: protocol, paper methods, `profile-dataset` output, filled METADATA tab.

Cover: countries/regions, time period, eligible populations, planned and achieved sample size. Auto-fill potential: **High**.

### Q14: How were respondents, records, facilities, geographies, or observations selected?

Derive from: protocol sampling section, paper methods.

Describe: probability vs. purposive sampling, sampling frame, clustering, stratification, selection criteria. Auto-fill potential: **High**.

### Q15: Who or what is included, excluded, underrepresented, or overrepresented?

**Requires human review for the equity-focused portion.**

Draft structural exclusions from the protocol (e.g., eligibility criteria). Then state explicitly: "The following groups may be structurally underrepresented and require human assessment: mobile populations, undocumented residents, individuals without access to [collection modality], and others not captured by the sampling frame. Equity and representativeness assessment for specific marginalized groups requires input from the data owner or domain expert."

Do not make equity judgments without human input.

Auto-fill potential: **Medium (structural exclusions)** / **Low (equity judgment)**.

## Section E: Consent, Privacy, and Access

All four questions in this section require human review. The skill will draft placeholder text and flag all four. Do not generate plausible-sounding answers for consent or ethics questions.

### Q16: Was the data collected with informed consent?

**Requires human input.** Consent details may appear in a protocol, but confirmation must come from the data owner.

Draft: "Requires confirmation from data owner. Specify: whether consent was individual, institutional, or community-level; whether consent covered secondary uses of the data; and any applicable IRB or ethics committee approvals and their scope."

### Q17: Is this data collected in connection with an incentive or eligibility for a benefit?

**Requires human input.** This question addresses power dynamics in data collection.

Draft: "Requires confirmation from data owner. Consider whether participation was tied to receiving services, benefits, or payments, and whether this may have influenced response patterns or created coercive conditions."

### Q18: Is this data collected by the government?

**Requires human input or confirmation.** May be partially addressed by Q7, but the framing here — focused on government authority and its implications for respondent privacy and data use — requires human judgment.

Draft: "Requires confirmation from data owner. Clarify: whether collection involved government authority, whether data are subject to government data-sharing obligations, and any implications for respondent privacy."

### Q19: Is this data collected with a blinding process?

**Requires human input.** Describe any masking of data collector identity or respondent information during collection or analysis.

Draft: "Requires confirmation from data owner. Describe any blinding applied to enumerators, respondents, analysts, or data processors, and why."

## Section F: Data Readiness, Quality, and Interpretation

### Q20: Are key variable definitions, indicator definitions, units, codes, and classifications documented?

Derive from: the completed INDIVIDUAL VARIABLES tab, existing data dictionary or codebook, documentation links.

List available documentation artifacts (data dictionaries, codebooks, standard code references such as ICD-10, ISO 3166). Note gaps where documentation is absent. Auto-fill potential: **High**.

### Q21: Has the data been cleaned, transformed, aggregated, linked, anonymized, modeled, or otherwise processed?

Derive from: protocol data management section, paper methods, processing documentation, user context.

Describe all known post-collection transformations. If processing documentation is unavailable, flag for review. Auto-fill potential: **Medium**.

### Q22: What limitations, equity concerns, or interpretation caveats should users consider?

**Always requires human review for the equity-focused portion.**

Draft technical limitations from `profile-dataset` output (missingness, coverage gaps, quality flags) and documentation. Then state explicitly: "Equity concerns, deficit framing risks, comparability caveats across sites or time periods, and guidance on appropriate interpretation require input from the data owner or domain expert and should not be generated without their review."

Auto-fill potential: **Medium (technical limitations)** / **Low (equity and interpretation judgment)**.

## Controlled vocabulary by question

When drafting a response for one of these questions, prefer one of its listed values if it fits; otherwise write free text (the template explicitly allows writing in an answer that isn't on the list). Do not force a poor-fitting category — a clear free-text answer beats a mismatched list value.

* **Q2** (why originally collected): Surveillance, Program monitoring, Research, Service delivery, Modeling, Reporting, Evaluation, Multiple purposes, Other
* **Q3** (current use): Same as original purpose, Surveillance, Program monitoring, Research, Service delivery, Modeling, Reporting, Evaluation, Policy-making, Other
* **Q4** (inappropriate uses): Re-identifying individuals, Population profiling or targeting, Policy decisions beyond the data's scope/validity, Commercial resale or monetization, Law enforcement or immigration enforcement, Denying services or benefits, Comparisons across incompatible groups/periods, Other
* **Q5** (who collected): Government agency, Research institution/university, NGO/implementing partner, Private company/platform, Multilateral organization, Community-based organization, AI/model system, Other
* **Q6** (who provided): Individuals/respondents, Households, Patients/clients, Facilities/institutions, Program or administrative staff, Sensors/devices/systems, Other
* **Q7** (government partnership): Yes, fully government-led; Yes, in partnership with government; No government involvement; Unclear/Unknown
* **Q8** (data chain): Yes, combined/merged; Yes, passed through multiple systems; No; Unknown
* **Q9** (how collected): Survey, Interview, Administrative record, Surveillance system, Sensor/device data, Web or app data, Model-derived/synthetic data, Other
* **Q10** (tools/technologies): Paper questionnaire, Electronic/mobile data collection, Administrative/IT system, API, Model pipeline, Sensor/IoT device, Other
* **Q11** (question administration mode): In-person, Phone/telephone, Self-administered (online/paper), Proxy respondent, Not applicable, Other
* **Q12** (incentives/eligibility/follow-ups): Yes, incentives used; Yes, eligibility rules/skip patterns used; Yes, repeated follow-ups used; No; Unknown
* **Q14** (selection method): Census/full enumeration, Probability/random sampling, Convenience sampling, Purposive sampling, Administrative/reporting requirement (not sampled), Other
* **Q16** (informed consent): Yes, No, Unknown
* **Q17** (incentive or benefit eligibility): Yes, No, Partial (e.g., some respondents/some data elements), Not applicable, Unknown
* **Q18** (collected by government): Yes, No, Public-private partnership, Unknown
* **Q19** (blinding process): Yes, No, Unknown
* **Q20** (documentation status): Yes, fully documented; Partially documented; No; Unknown
* **Q21** (processing applied): Cleaned, Transformed, Aggregated, Linked/merged, Anonymized/de-identified, Modeled/derived, Multiple of the above, No processing applied, Unknown

Q1, Q13, Q15, and Q22 have no controlled vocabulary — always draft open narrative text for these.

## Required behavior

* Use documentation as the primary source for all responses.
* Do not invent consent details, government involvement, or access conditions.
* For all Section E questions (Q16–Q19): always flag for human input. Do not generate plausible-sounding answers.
* For Q4, Q15, and Q22: draft what can be derived structurally, then explicitly request human review for the equity and ethics components.
* Use the language of the question when drafting responses.
* Distinguish documented facts from inferences.
* Do not make final governance, ethics, or access decisions.

## Confidence scoring

* High: directly stated in documentation.
* Medium: inferable from documentation with reasonable confidence.
* Low: absent from documentation, or requires domain or ethical judgment.

## Output format

In chat, organize by section (A–F). For each question, the `response`/`source`/`confidence`/`needs_review` shape below feeds `catalog_draft.json` for the tiered Q&A in `catalog-dataset`. It does not map one-to-one onto the final `DataBio.xlsx` file: `response` goes into the "Select from common dropdown options or write in:" column, and `source` is written directly into the Notes/Comments column (prefixed with the review question when `needs_review` is true). There is no separate confidence column in the deliverable — questions still flagged `needs_review` get a yellow-filled answer cell with an Excel comment instead.

The `source` field is a plain-language attribution, not just a citation, since a reader opening the file cold has no visibility into the drafting/review conversation. Compose it as:

* A response drawn from a specific document or page: `"Source: {URL or document name}"`.
* An AI-drafted response (inference, judgment call, or "not applicable" conclusion with nothing directly citable) that a human then reviewed and accepted: `"Generated by AI, reviewed and approved by {reviewer}."` — append `" Source: {URL}"` if a specific page was also consulted, even if the exact wording isn't drawn verbatim from it.
* A response the user wrote or dictated directly: `"Human input."`

Default `{reviewer}` to the current user's identity from session context (e.g. email, git config) rather than asking, unless it's ambiguous or the user says otherwise. Every question that reaches Step 3 of the Workflow ends up reviewed and approved at the section level, so this attribution applies across the board, not just to individually-flagged questions — the exception is a question left as an explicit unanswered placeholder (e.g. "Need researcher to complete"), which has no attribution to make.

For each question:

```
**Q[N]: [Question text]**

Draft response: [text or "Requires human input"]
Source: [document or input used]
Confidence: [High / Medium / Low]
Needs review: [true / false]
```

Also provide a YAML block:

```yaml
data_bio_tab:
  section_a:
    q1_what_does_dataset_measure:
      response:
      source:
      confidence:
      needs_review:
    q2_why_originally_collected:
      response:
      source:
      confidence:
      needs_review:
    q3_current_use:
      response:
      source:
      confidence:
      needs_review:
    q4_inappropriate_uses:
      response:
      source:
      confidence:
      needs_review:
  section_b:
    q5_who_collected:
      response:
      source:
      confidence:
      needs_review:
    q6_who_provided:
      response:
      source:
      confidence:
      needs_review:
    q7_government_involvement:
      response:
      source:
      confidence:
      needs_review:
    q8_data_chain:
      response:
      source:
      confidence:
      needs_review:
  section_c:
    q9_collection_method:
      response:
      source:
      confidence:
      needs_review:
    q10_tools_and_technologies:
      response:
      source:
      confidence:
      needs_review:
    q11_question_administration:
      response:
      source:
      confidence:
      needs_review:
    q12_incentives_and_patterns:
      response:
      source:
      confidence:
      needs_review:
  section_d:
    q13_scope_and_boundaries:
      response:
      source:
      confidence:
      needs_review:
    q14_selection_method:
      response:
      source:
      confidence:
      needs_review:
    q15_inclusion_exclusion:
      response:
      source:
      confidence:
      needs_review:
  section_e:
    q16_informed_consent:
      response:
      source:
      confidence:
      needs_review:
    q17_incentive_or_benefit:
      response:
      source:
      confidence:
      needs_review:
    q18_government_collection:
      response:
      source:
      confidence:
      needs_review:
    q19_blinding:
      response:
      source:
      confidence:
      needs_review:
  section_f:
    q20_documentation_status:
      response:
      source:
      confidence:
      needs_review:
    q21_processing_and_transformation:
      response:
      source:
      confidence:
      needs_review:
    q22_limitations_and_caveats:
      response:
      source:
      confidence:
      needs_review:
```

## Questions for human review

These are the questions Step 2 of the Workflow asks the user interactively, in a single round ordered Critical first, then Important, then Optional — not split into separate tiered rounds (that tiering is specific to the `catalog-dataset` skill, which handles all three files at once). Include only questions with needs_review: true, structured as:

```
Priority: Critical / Important / Optional
Question: Q[N] — [question text]
Why: [reason it needs human input]
What to provide: [what the human should supply]
```

Priority guidance:

* Critical: Q4 (inappropriate uses), Q15 (equity/exclusion), Q16–Q19 (all consent/access questions)
* Important: Q3 (current use), Q7–Q8 (provenance chain), Q22 (limitations and equity caveats)
* Optional: Q11–Q12 (administration details) if questionnaire was not provided

## Relationship to other skills

Use this skill when the user asks specifically about a data bio/biography. If the user wants metadata and/or a data dictionary filled too, use `catalog-dataset` instead — it runs the same drafting logic for all three files together with its own tiered Q&A, and generates all three Excel files at once.

## Do not do the following

Do not:

* Generate plausible-sounding consent or ethics statements without documentation.
* Infer that consent was obtained because the dataset exists.
* Assume government involvement is absent without confirmation.
* Make equity or representativeness judgments without human input.
* Treat Q4 (inappropriate uses) or Q22 (equity caveats) as technically answerable from data alone.
* Frame limitations as minor when they may be significant for equity or interpretation.
* Invent purpose, methodology, or access conditions.
* Skip Step 2 (asking needs-review questions) or Step 3 (section-by-section review) — do not go straight from drafting to generating the Excel file.
* Present more than one section at a time in Step 3, or move on before the current section is explicitly approved.
* Mix Step 2's questions into tiers — ask them in a single round.
* Guess which file a landing page refers to when it links to multiple candidates — ask first.
* Draft from a downloaded file without first telling the user exactly what was pulled and from where.
