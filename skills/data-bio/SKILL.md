# Complete Data Bio Tab

Use this skill when the user wants to fill the "DataBio" sheet of `DataProfile.xlsx`.

The DataBio sheet contains 22 narrative questions across six sections (A–F) adapted from the We All Count Data Biography framework. It captures dataset purpose, provenance, collection methods, coverage, consent, and quality — with a focus on equity, ethics, and responsible data use.

This tab is the most human-judgment-intensive of the catalog files. This skill extracts as much as possible from available documentation, but it will not guess on equity, consent, or representativeness questions — those require the data owner or steward.

`DataProfile.xlsx` has two sheets: "DataBio" (this skill) and "Metadata" (the `metadata` skill). Both skills write into the *same* output file, each owning its own sheet — see "Output format" below for how that's handled. `DataDict.xlsx` is a separate file, out of scope for this skill.

Note: "Data Biography" is this sheet specifically — the 22 narrative questions, a framework term from We All Count. That said, the phrase has historically also been used at this org for the whole data profile (both tabs), from before that terminology was cleaned up — so when a user asks to fill out "a data biography"/"a data bio" without clarifying they mean only the narrative questions, **default to assuming they mean the whole data profile** and use `catalog-dataset` instead. Only use this skill directly when the user explicitly clarifies they want just the narrative tab, not metadata (e.g., "just the data bio questions" or "skip metadata, just the bio"). See "When to use this skill" below.

The DataBio sheet has five columns: `Section | Question | Answer | Confidence (AI-Assisted only) | Source (AI-Assisted only)`. There is no dropdown/validation mechanism on the Answer column — treat "Controlled vocabulary by question" below purely as a style guide for consistency across datasets, not as something enforced by the file. Q1, Q13, Q15, and Q22 have no natural controlled vocabulary and are always open narrative text.

An earlier version of the template also had a "Clarification/example" column between Question and Answer, giving per-question guidance on what to consider. That column has been intentionally removed from the template — its content now lives in this skill's Section A–F derivation notes below instead, so nothing was lost, it just doesn't clutter the deliverable.

Confidence and Source replace what used to be a single "Notes/Comments" column. Both are headed "(AI-Assisted only)" — real header text, not a comment — precisely so a researcher filling the sheet out by hand knows at a glance those two columns aren't for them; they only get populated on rows this skill drafted or touched. This data (not cell color, not Excel comments) is how review status is captured now, since the file gets synced into Databricks and formatting doesn't survive that sync. Every question is drafted by AI and then reviewed and approved by the researcher (section by section, see "Workflow" below) before the file is ever generated, so Confidence normally shows the AI's real drafted confidence (High/Medium/Low) rather than a separate review-status flag. The one exception: a question with a genuinely blank Answer (nothing AI or the researcher could determine) shows Confidence as **"Needs human input"** instead — blank Answer is the only thing that triggers that, not a hidden flag.

This skill follows a three-step interactive process — draft everything, review and approve it section by section, then generate the file — see "Workflow" below. Don't jump straight from drafting to generating the Excel file.

## When to use this skill

**Disambiguation first:** if the user asks to fill out "a data biography" or "a data bio" without explicitly clarifying they want only the narrative questions (not metadata), do not use this skill — use `catalog-dataset` instead, since that phrase has historically meant the whole data profile here. Only use this skill when the request is unambiguous.

Use this skill when the user asks to:

* Fill or complete the DataBio tab/sheet in DataProfile.xlsx, specifically (not metadata)
* Draft narrative responses to data biography questions, having already clarified metadata is out of scope this time
* Document dataset purpose, provenance, consent, and quality for a data catalog — again, only once it's clear metadata isn't wanted alongside it
* Generate an equity- and ethics-aware dataset description

## Inputs

The user may provide one or more of the following:

* A study protocol or research proposal
* A questionnaire or survey instrument
* Published papers using or describing the dataset
* Existing README or project documentation
* A dataset usability assessment from the `assess-dataset` skill
* A filled METADATA tab
* A URL — either a direct link to a downloadable data file, or a link to a page describing the dataset (see Step 1 for how this is resolved)
* User-provided context about purpose, methods, population, or access

**Mode A** (full data available): use documentation as the primary source; the dataset file may support Section F questions on data quality.
**Mode B** (documentation only): documentation is the only source. This tab is often well-served in Mode B because most questions are about how data was collected — answerable from protocol and papers.

Before opening the dataset file for Section F, check for signals that it may be classified Restricted, Sensitive, or Highly Sensitive (a known classification, a DUA, a confidentiality notice, or the researcher's own description). If present, do not open it — answer Section F from documentation only (Mode B) and tell the researcher why, per `assess-dataset`'s "Sensitive data classification gate" (the researcher can explicitly authorize inspection anyway).

## Outputs

Draft responses to all 22 questions, organized by section A–F. Each question includes:

* Draft response, or blank if nothing can be confirmed yet
* Source (what document or input the response was derived from)
* Confidence (High / Medium / Low, or "Needs human input" if the response is blank)

## Workflow

This is the entry point once it's clear the user wants only the narrative tab, not metadata too — see the disambiguation note in "When to use this skill" and "Relationship to other skills" below. Follow these steps in order. Do not generate the Excel file before every section has been explicitly approved.

### Step 0: Locate the SharePoint templates and dataset folder

`DataProfile.xlsx` lives in a SharePoint "Data Profiles" library, synced locally via OneDrive rather than bundled with this skill — see `catalog-dataset`'s "Step 0" for the full procedure: check `${CLAUDE_PLUGIN_DATA}/cataloging_config.json`; if missing, ask the researcher once for their OneDrive-synced "Data Profiles" folder path and save it via `python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --set-data-profiles-root "<path>"`. This is a one-time-per-machine step, shared across all these skills — don't ask again if it's already configured.

### Step 1: Resolve sources and draft

If the user provides a URL instead of, or in addition to, an uploaded file:

1. Fetch the URL to see what it actually is: a direct downloadable data file (CSV, Excel, JSON, Parquet, a zipped data bundle, a documented API/export endpoint), or a landing/documentation page that describes a dataset and links out to one or more resources.
2. If the page exposes more than one candidate file, version, or resource — per-year extracts, per-region files, multiple formats of the same data, etc. — **do not guess which one the user means**. Stop and list the options, and ask the user to confirm which file(s) to use before downloading or drafting anything.
3. Before downloading, check the landing page/documentation for signals that the data is classified Restricted, Sensitive, or Highly Sensitive (a DUA, a confidentiality notice, access-request language). If present, don't download it — treat this as Mode B and say so explicitly, per `assess-dataset`'s "Sensitive data classification gate" (the researcher can explicitly authorize downloading anyway). Otherwise, if there is a single, unambiguous downloadable file, download it. Before drafting anything, tell the user exactly what was pulled: file name, source URL, format, and size (plus row/column count if quick to check). This is a transparency checkpoint, not a blocking question — state it plainly as the lead line of your first response so the user has an obvious chance to say "that's not the one" before you go further, then continue into drafting in the same turn.
4. If the page only exposes documentation with no downloadable data, proceed in Mode B and say so explicitly.
5. Record the exact source (URL, and the fetched file name if applicable) in `sources_used`.

Then draft a response to all 22 questions using the derivation logic in "Section A–F" below, following "Controlled vocabulary by question" where applicable. Attempt a real answer for every question, including the sensitive ones (Q4, Q15, Q16–19, Q22) — leave `response` blank only when truly nothing can be determined from available sources, not by policy. For each question, determine `response`, `source`, and `confidence`.

Write the draft to the `data_bio` array of `catalog_draft.json` in the current working directory (create the file with a `dataset_name` and empty `metadata`/`variables` arrays if it doesn't exist yet — see the schema in the `catalog-dataset` skill). Do this before presenting anything to the user.

### Step 2: Section-by-section review and approval

Present the questions one section at a time, in order (A → B → C → D → E → F). This is the *only* human-approval step — every question gets a look here, not just ones that seem uncertain, since a confidently auto-filled answer may still need the user's editorial correction, and this is also the point where the researcher's own current context (e.g. Q3's current use, Q4's sense of what's inappropriate) gets folded in. For each section:

1. Show the section's questions, each with its `response`, `confidence`, and `source` — not response alone. Seeing confidence and source together is what lets the researcher judge whether to trust a drafted answer or correct it. A question with a blank `response` shows that plainly, with confidence noted as "Needs human input."
2. Ask the user to approve as-is or request changes.
3. If they request changes, apply them to `response`, set `source` to `"Human input."`, update `catalog_draft.json`, and show the revised section again.
4. If approved as-is and `response` was AI-drafted, set `source` to `"Generated by AI, reviewed and approved by {reviewer}."` (appending `" Source: {URL}"` if a specific document was consulted) — see "Output format" below for the full composition rule. Default `{reviewer}` to the current user's identity from session context rather than asking.
5. Repeat until the user approves that section, then move to the next.

Do not move to the next section until the current one is explicitly approved, and do not present more than one section at a time.

### Step 3: Generate the Excel file

Once all six sections are approved, run:

```
python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --only databio
```

This fills the DataBio sheet from `catalog_draft.json` and writes `<Dataset>_DataProfile.xlsx` directly into the OneDrive-synced SharePoint folder resolved in Step 0 (no export step — saving there is what puts it in SharePoint). If that file already exists (e.g. because the `metadata` skill already ran for this dataset), the DataBio sheet is updated in place without disturbing the Metadata sheet. Tell the user the full path to the file so they can retrieve it, and that it's already synced.

## Section A: Dataset Purpose and Intended Use

The per-question notes below (what to consider, what to look for) used to live in a "Clarification/example" column on the DataBio sheet. That column has been intentionally removed from the template — this guidance now lives here instead, informing what you derive and how thoroughly you check, not how much you write. The "Response length and style" concision rules still apply to the actual `response` text regardless of how much derivation guidance follows.

### Q1: What does this dataset measure?

Derive from: protocol, paper abstract, data documentation, user context.

Describe the main topic, outcome, indicator, population, or phenomenon represented — briefly. Auto-fill potential: **High**.

### Q2: Why was the data originally collected?

Derive from: protocol objectives, paper rationale, grant or project description.

Include both the primary purpose and any known secondary purpose (e.g., a dataset collected for program monitoring that also supports research). Distinguish original collection purpose from current use (addressed in Q3). Auto-fill potential: **High**.

### Q3: What is the data being used for now?

Derive from: user context, current project documentation, protocol/paper framing of ongoing use.

If the current use differs from the original purpose (Q2), note that distinction. Draft a response from whatever documentation is available; this is exactly the kind of question where the researcher's own current context (surfaced during section review) often supersedes what an older protocol or paper says.

Auto-fill potential: **Medium** — depends on user-provided context.

### Q4: What uses of this data would be inappropriate, unsupported, or potentially harmful?

Derive from: protocol restrictions, data use agreement terms, ethical review documentation, and reasoned judgment about the population/context.

Draft a plausible list: uses that could misrepresent populations, exceed the data's validity, or create risk — including uses outside the consent scope, applications to populations not represented in the sample, publication of disaggregated results that could enable identification or cause harm, and uses not aligned with the original data use agreement. Always attempt a draft here rather than leaving it blank by default — the researcher reviews and corrects it during section review, same as any other question.

Auto-fill potential: **Low** — a reasoned judgment call, not something directly stated in documentation.

## Section B: Data Provenance

### Q5: Who collected the data?

Derive from: protocol, paper authorship, study acknowledgments.

Include whichever of these apply: the organization, research team, government agency, implementing partner, platform, system, or model that created the data. For modeled/administrative datasets, "who collected" may really mean "what system or model produced this." Auto-fill potential: **High**.

### Q6: Who provided the data?

Derive from: protocol, paper methods, study description.

Describe the respondents, patients, households, facilities, program or administrative staff, or other data providers. Auto-fill potential: **High**.

### Q7: Was the data collected by, for, or in partnership with a government entity?

Derive from: protocol, paper acknowledgments, user context.

Note any government involvement in collection, funding, or oversight, and — if evident — why it matters: implications for access, trust, privacy, surveillance risk, eligibility, or interpretation. Flag for human confirmation even if documentation suggests an answer.

Auto-fill potential: **Medium**.

### Q8: Has the data changed hands, been combined, or passed through multiple systems?

Derive from: protocol, data processing notes, user context.

Describe any owner handoffs, extracts, merges, or linkages before the dataset reached its current form — data linkage, transfer, combination with other sources, or system migration. Flag for human confirmation if the full data chain is unclear.

Auto-fill potential: **Medium**.

## Section C: Data Collection Methods

### Q9: How was the data collected?

Derive from: protocol methods section, paper methods section.

Examples: household survey, interview, administrative record, surveillance system, facility assessment, remote sensing, laboratory, modeling. Auto-fill potential: **High**.

### Q10: What tools, instruments, systems, software, or technologies were used?

Derive from: protocol, paper methods, questionnaire metadata.

Examples: questionnaire (paper or electronic), model pipelines, APIs, ODK, DHIS2, REDCap, GPS devices, analysis software. Auto-fill potential: **High**.

### Q11: If people were asked questions, how were those questions administered?

Derive from: questionnaire, protocol enumerator guidance.

Cover: interviewer-administered vs. self-administered, direct vs. proxy responses, enumerator training, languages used, translations, respondent burden, approximate interview length.

Auto-fill potential: **Medium** — requires questionnaire or detailed protocol.

### Q12: Were incentives, repeated follow-ups, eligibility rules, or skip patterns used?

Derive from: protocol, questionnaire skip logic, study design section.

Describe any: participant incentives, follow-up attempts, eligibility criteria, questionnaire skip patterns or routing — and, where evident, how these may have affected participation, response rates, who was included, or what was recorded.

Auto-fill potential: **Medium** — requires questionnaire or detailed protocol.

## Section D: Coverage, Scope, and Representativeness

### Q13: What are the geographic, temporal, demographic, and sample-size boundaries?

Derive from: protocol, paper methods, `assess-dataset` output, filled Metadata sheet.

Cover: location; time period; collection dates *or* reference period (these can differ — a survey fielded in one month may ask about the prior 12 months); demographic/eligible-population scope; and number of records/respondents (planned and achieved). Auto-fill potential: **High**.

### Q14: How were respondents, records, facilities, geographies, or observations selected?

Derive from: protocol sampling section, paper methods.

Describe whichever apply: probability vs. purposive sampling, sampling frame, clustering, stratification, selection criteria, recruitment process — or, for administrative/surveillance data, the reporting requirement that determines what gets included (e.g., "all confirmed cases reported to system X," not a sample at all). Auto-fill potential: **High**.

### Q15: Who or what is included, excluded, underrepresented, or overrepresented?

**Requires human review for the equity-focused portion.**

Draft structural exclusions from the protocol (e.g., eligibility criteria) into `response` — groups intentionally excluded, accidentally excluded, missing, undercounted, or overrepresented. If no structural exclusions can be drafted at all, leave `response` blank.

Do not make equity judgments without human input: the structural portion goes through the same drafted-and-reviewed process as any other question, but when presenting this one during section review, call out explicitly that the equity/representativeness assessment for specific marginalized groups (rural, mobile, low-connectivity, low-literacy, conflict-affected, disabled, minoritized, undocumented, or otherwise marginalized populations not captured by the sampling frame) needs the researcher's own input — don't let a confidently-drafted structural answer imply that judgment has already been made.

Auto-fill potential: **Medium (structural exclusions)** / **Low (equity judgment)**.

## Section E: Consent, Privacy, and Access

All four questions in this section always attempt a draft from available documentation (protocol consent language, IRB/ethics approval, consent forms) rather than being left blank by default. These are consequential enough that they deserve extra scrutiny during section review — don't let a well-worded draft read as more certain than the underlying documentation actually is — but they're approved the same way as every other question, no separate confirmation gate.

### Q16: Was the data collected with informed consent?

Derive from: protocol consent section, IRB/ethics committee approval language, consent forms if available.

Draft what's evident: whether consent was individual, institutional, or community-level; whether it covered secondary uses of the data; and any applicable IRB or ethics committee approvals and their scope. Leave `response` blank only if nothing at all is documented.

### Q17: Is this data collected in connection with an incentive or eligibility for a benefit?

Derive from: protocol, description of program benefits/eligibility tied to participation.

Draft what's evident: whether participation was tied to receiving services, benefits, or payments. Leave `response` blank only if nothing at all is documented.

### Q18: Is this data collected by the government?

Derive from: protocol, funding/oversight documentation (may overlap with Q7).

Draft what's evident: whether collection involved government authority, and any known data-sharing obligations. Leave `response` blank only if nothing at all is documented.

### Q19: Is this data collected with a blinding process?

Derive from: protocol methodology section.

Draft what's evident, including stating plainly if no blinding is mentioned at all. Leave `response` blank only if nothing at all can be said.

## Section F: Data Readiness, Quality, and Interpretation

### Q20: Are key variable definitions, indicator definitions, units, codes, and classifications documented?

Derive from: the completed DataDict.xlsx, existing data dictionary or codebook, documentation links.

Check for and list what's findable: data dictionaries, codebooks, questionnaires, indicator definitions, standard code references (ICD-10, ISO 3166), admin boundary versions, facility identifiers, demographic fields, or disaggregation variables. Note gaps where documentation is absent. Auto-fill potential: **High**.

### Q21: Has the data been cleaned, transformed, aggregated, linked, anonymized, modeled, or otherwise processed?

Derive from: protocol data management section, paper methods, processing documentation, user context.

Describe what was done, who did it, whether code is available, and whether raw or earlier versions are available. If processing documentation is unavailable, flag for review. Auto-fill potential: **Medium**.

### Q22: What limitations, equity concerns, or interpretation caveats should users consider?

**Always requires human review for the equity-focused portion.**

Draft technical limitations from `assess-dataset` output and documentation into `response` — consider missingness, completeness, denominator quality, reporting bias, comparability across sites/time/waves, and other known quirks. If no technical limitations can be drafted at all, leave `response` blank.

When presenting this one during section review, call out explicitly that equity concerns, deficit-framing risks, and guidance on who should be involved in interpretation require the researcher's or a domain expert's own input and shouldn't be treated as covered just because the technical limitations are well drafted.

Auto-fill potential: **Medium (technical limitations)** / **Low (equity and interpretation judgment)**.

## Controlled vocabulary by question

These are suggested values for consistency across datasets, not an enforced Excel dropdown (see the note in the intro — this template has no data-validation mechanism). When drafting a response for one of these questions, prefer one of the listed values if it fits; otherwise write free text. Do not force a poor-fitting category — a clear free-text answer beats a mismatched list value.

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
* Attempt a real draft for every question, including the sensitive ones (Q3, Q4, Q15, Q16–19, Q22) — leave `response` blank only when truly nothing can be determined, not by policy.
* For Q15 and Q22: draft the structural/technical portion into `response`, then call out the equity-judgment portion for human input specifically when presenting that question during section review (see their sections).
* Use the language of the question when drafting responses.
* Distinguish documented facts from inferences.
* Do not make final governance, ethics, or access decisions.
* Keep every `response` concise — see "Response length and style" below.

## Response length and style

Responses have been running too long. Default to **1–2 sentences (roughly 15–40 words)** per question. Longer is only justified for questions that inherently enumerate several distinct facts (Q13's geographic/temporal/demographic/sample-size boundaries, Q22's limitations list) — even there, use short semicolon-separated phrases, not a full sentence of justification per point.

* State the fact. Don't also explain why you believe it, hedge it twice, or restate the question back.
* Don't put citations or source attribution inline in the response text (e.g., "(Bandiera et al. 2017)") — that belongs in `source`/the Notes column, not duplicated in the answer itself.
* Don't repeat boilerplate phrases like "not documented in the materials reviewed" as a full clause on every under-documented question — say it once, tersely, or fold the gap directly into `review_notes` instead of narrating it in `response`.
* One clear declarative sentence beats a compound sentence with three subordinate clauses.
* Cut a drafted response by at least a third before finalizing it if it's doing any of the above.

## Confidence scoring

* High: directly stated in documentation.
* Medium: inferable from documentation with reasonable confidence.
* Low: absent from documentation, or requires domain or ethical judgment.

## Output format

In chat, organize by section (A–F). For each question, the `response`/`source`/`confidence` shape below feeds `catalog_draft.json`, which `catalog-dataset` also uses when running this same drafting logic as part of a full data profile. It maps onto the final `DataProfile.xlsx` file as follows:

* `response` → the DataBio sheet's Answer column. Populated whenever a draft (or human answer) exists — left blank only when genuinely nothing can be said, never filled with placeholder text like "Requires human input."
* `confidence` → the Confidence (AI-Assisted only) column, *unless* `response` is blank, in which case the generator writes the literal value **"Needs human input"** instead. This is the only thing that triggers it — a populated Answer always shows a real confidence level, never a review-status flag.
* `source` → the Source (AI-Assisted only) column, *unless* `response` is blank, in which case the generator writes `review_notes` instead (falling back to a generic note if `review_notes` is empty). Set `review_notes` to a short note on what's needed and from whom whenever you leave a `response` blank — it's the only place that context surfaces in the deliverable.

The `source` field is a plain-language attribution, not just a citation, since a reader opening the file cold has no visibility into the drafting/review conversation, and it evolves as a question moves through the Workflow:

* While still just a draft (before Step 2's section review reaches it): a plain citation, `"Source: {URL or document name}"`, or nothing yet if it's a reasoned judgment call with nothing citable.
* Once approved as-is (or lightly copyedited) during Step 2: `"Generated by AI, reviewed and approved by {reviewer}."` — append `" Source: {URL}"` if a specific document was also consulted, even if the exact wording isn't drawn verbatim from it.
* Once the researcher supplies or substantively rewrites the answer during Step 2 (not just wording tweaks — actual new content only they would know): `"Human input."`

Default `{reviewer}` to the current user's identity from session context (e.g. email, git config) rather than asking, unless it's ambiguous or the user says otherwise. Every question passes through Step 2's section-by-section review before generation ever runs, so by the time the file is generated, every populated `response` should carry one of the two approved forms above — the plain "Source: {doc}" form is a transient drafting-time state, not something that should still be sitting there at Step 3 (Generate).

For each question, give each field its own line with blank lines between them and bold labels — dense single-line listings are hard to scan when reviewing 3-4 questions per section:

```
**Q[N]: [Question text]**

**Response:** [text, or blank if nothing can be confirmed yet]

**Confidence:** [High / Medium / Low, or "Needs human input" if blank]

**Source:** [document or input used]

**Note:** [optional — a short follow-up question or caveat, only when one is relevant]
```

Leave a blank line between one question's block and the next one, too. This formatting applies whenever responses are shown in chat — both the initial draft summary and Step 2's section-by-section review.

Also provide a YAML block. `needs_review` is optional here — this skill's own workflow doesn't act on it (see "Output format" above, which keys off blank `response` instead), and `catalog-dataset`'s Phase 2 doesn't filter by it either (it reviews every question regardless). It's kept as a simple record of what a researcher explicitly skipped versus resolved:

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

## Question importance reference

Not tied to any specific step in this skill's own workflow (which reviews every question section by section regardless of priority) — just a rough guide to which questions matter most, useful when deciding what deserves extra scrutiny or explaining to the researcher why something needs a closer look:

* Critical: Q4 (inappropriate uses), Q15 (equity/exclusion), Q16–Q19 (all consent/access questions)
* Important: Q3 (current use), Q7–Q8 (provenance chain), Q22 (limitations and equity caveats)
* Optional: Q11–Q12 (administration details) if questionnaire was not provided

## Relationship to other skills

Use this skill only once the user has made clear they want just the narrative tab, not metadata too. A bare "fill out a data biography"/"data bio" request, with no such clarification, should go to `catalog-dataset` instead — it runs the same drafting logic for both sheets together, reviewing Metadata as a whole and DataBio section by section, and generates `DataProfile.xlsx` in one pass. `DataDict.xlsx` is a separate, optional deliverable — `catalog-dataset` will offer it when the actual data can be read, or invoke `data-dictionary` directly any time.

## Do not do the following

Do not:

* Generate plausible-sounding consent or ethics statements without documentation.
* Infer that consent was obtained because the dataset exists.
* Assume government involvement is absent without confirmation.
* Make equity or representativeness judgments without human input.
* Treat Q4 (inappropriate uses) or Q22 (equity caveats) as technically answerable from data alone — always call out the equity/judgment portion for the researcher's own input during section review.
* Leave Q4 or Q16–Q19 blank by default — draft a candidate response for all of them like any other question; only leave them blank if truly nothing can be said.
* Frame limitations as minor when they may be significant for equity or interpretation.
* Invent purpose, methodology, or access conditions.
* Skip Step 2 (section-by-section review) — do not go straight from drafting to generating the Excel file.
* Present more than one section at a time in Step 2, or move on before the current section is explicitly approved.
* Show a question's response without its confidence and source during Step 2 — the researcher needs all three to decide whether to approve or correct it.
* Guess which file a landing page refers to when it links to multiple candidates — ask first.
* Open a dataset file for Section F once a Restricted/Sensitive/Highly Sensitive signal is present, without the researcher's explicit authorization — see the Sensitive data classification gate in Inputs.
* Draft from a downloaded file without first telling the user exactly what was pulled and from where.
