# Complete Data Bio Tab

Use this skill when the user wants to fill the DATA BIO sheet of `databio_v1.xlsx`.

The DATA BIO sheet contains 22 narrative questions across six sections (A–F) adapted from the We All Count Data Biography framework. It captures dataset purpose, provenance, collection methods, coverage, consent, and quality — with a focus on equity, ethics, and responsible data use.

This tab is the most human-judgment-intensive of the three databio tabs. This skill extracts as much as possible from available documentation, but it will not guess on equity, consent, or representativeness questions — those require the data owner or steward.

## When to use this skill

Use this skill when the user asks to:

* Fill or complete the DATA BIO tab in databio_v1.xlsx
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

Organized by section (A–F). For each question:

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

End with a section called `Questions for human review`. Include only questions with needs_review: true, structured as:

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

## Do not do the following

Do not:

* Generate plausible-sounding consent or ethics statements without documentation.
* Infer that consent was obtained because the dataset exists.
* Assume government involvement is absent without confirmation.
* Make equity or representativeness judgments without human input.
* Treat Q4 (inappropriate uses) or Q22 (equity caveats) as technically answerable from data alone.
* Frame limitations as minor when they may be significant for equity or interpretation.
* Invent purpose, methodology, or access conditions.
