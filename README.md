# data-cataloging-ai

This project is part of an effort to capture information about datasets that IDM uses repeatedly to enable better discoverability and usability of data. It's intended for cataloging datasets that will be (or are already) stored in IDM's workspace within Databricks.

This repository contains skills for auto-generating dataset documentation for a data catalog: administrative metadata, a data biography (purpose, provenance, consent, quality), and a variable-level data dictionary.

**This repository is in active development.** Templates, terminology, and workflows here are still being refined and may change without notice.

## Terminology

These three concepts are related but distinct, and the naming is intentionally kept separate to avoid confusion:

* **Metadata** — the administrative/catalog-record fields (title, owner, storage, access, coverage). Lives on `DataProfile.xlsx`'s "Metadata" sheet.
* **Data Biography** — a specific framework from We All Count: narrative, equity-focused questions about a dataset's origin, purpose, and social context (who made it, why, who's excluded, consent). This term refers *only* to `DataProfile.xlsx`'s "DataBio" sheet (22 questions).
* **Data Dictionary / Codebook** — the variable-level schema (one row per column/field in the dataset). Lives in `DataDict.xlsx`.

A filled-out **data profile** is one Excel file (the Metadata and Data Biography sheets), `DataProfile.xlsx`; `DataDict.xlsx` is a separate, optional deliverable (see `data-dictionary` above) — a dataset can end up with zero, one, or several of them.

```
DataProfile.xlsx              <- "the data profile"
├── Metadata sheet            (18 fields   — filled by the `metadata` skill)
└── DataBio sheet             (22 questions — filled by the `data-bio` skill)

DataDict.xlsx                 <- separate, optional (the `data-dictionary` skill)
```

The Data Dictionary is kept separate for practical reasons, not because it's conceptually unrelated: a dataset is sometimes a bundle of several distinct files with different fields, so one dictionary doesn't always map cleanly to one profile — and sometimes the underlying data isn't even accessible to build a dictionary from (Restricted/Sensitive, or under a DUA) while the rest of the profile still can be completed. This is a current design choice, not a permanent one — if those constraints stop being the common case, folding the dictionary back into the data profile as a third sheet may make more sense.

## Where everything lives (SharePoint)

The [Data Profiles library](https://bmgf.sharepoint.com/:f:/r/sites/IDMOD/Shared%20Documents/IDM%20Software/Data%20Management%20Strategy/Data%20Profiles?d=wec03896e3ffb400f86111a2f0e8c9bf2&csf=1&web=1&e=0IeHLQ) is IDM's SharePoint directory for storing dataset catalog records. It holds the master templates (`_Templates_` folder), plus one folder per dataset that's been cataloged so far, each containing that dataset's finished `DataProfile.xlsx` and (if generated) `DataDict.xlsx`. Anyone at IDM can browse it to see what's already been documented about a dataset — what it contains, who owns it, its access restrictions — without needing access to the underlying data itself, which matters most for datasets that are Restricted/Sensitive or governed by a DUA.

There's no API integration here — it's plain file access. Once you've synced the library via OneDrive (see Setup above), it's just a folder on your disk; editing a file in it *is* editing the SharePoint copy, and OneDrive pushes the change back automatically (usually within about a minute).

The skills need to know the local path to that synced folder. The first time any of them runs on a given machine, it checks for a small config file and, if missing, asks you for the path once:
```
python "$CLAUDE_PLUGIN_ROOT/generate_catalog.py" --set-data-profiles-root "<path to your synced Data Profiles folder>"
```
This is saved to `${CLAUDE_PLUGIN_DATA}/cataloging_config.json` — tied to the installed plugin, not to any project folder, so it survives plugin updates and you're never asked again on that machine. It expects a `_Templates_` subfolder inside the path you give it (containing `DataProfile.xlsx`/`DataDict.xlsx`); pass `--templates-dir` explicitly if yours is named differently.

## Setup

Two one-time steps, no git or code required:

1. **Sync the Data Profiles folder to your computer.** Open the [Data Profiles SharePoint library](https://bmgf.sharepoint.com/:f:/r/sites/IDMOD/Shared%20Documents/IDM%20Software/Data%20Management%20Strategy/Data%20Profiles?d=wec03896e3ffb400f86111a2f0e8c9bf2&csf=1&web=1&e=0IeHLQ) and click **"Add shortcut to OneDrive"** (toolbar, or right-click the folder), then confirm **"My files"** when prompted for the destination. It'll then appear under "OneDrive - Gates Foundation" in File Explorer within a minute or two — copy its path; you'll need it below.
2. **Install the skills in Claude Code.** How you do this depends on how you access Claude Code:

   **Claude Desktop app:** Go to **Settings → Plugins**, click **Add**, then **Add marketplace**, and enter:
   ```
   InstituteforDiseaseModeling/data-cataloging-ai
   ```
   Once the marketplace is added, click the **+** next to it to install the `data-cataloging-ai` plugin. If there is an option to enable auto-update for the plugin on the settings screen, do so, so that future updates reach you automatically.

   **Claude Code CLI (terminal):**
   ```
   /plugin marketplace add InstituteforDiseaseModeling/data-cataloging-ai
   /plugin install data-cataloging-ai@data-cataloging-ai
   ```
   Then run `/plugin` → **Marketplaces** tab → enable **auto-update** for this marketplace, so future updates reach you automatically.

   Note: `/plugin` is a CLI-only command — if you're in the Desktop app and see "`/plugin` isn't available in this environment," use the Settings → Plugins path above instead.

## Modes

Every drafting skill operates in one of two modes, and reports which one it used:

* **Mode A — full data available**: the dataset file itself can be inspected (actual values, ranges, missingness), with documentation as a supplementary source. Datasets are expected to be deposited directly in the same SharePoint dataset folder as their profile; check there first.
* **Mode B — documentation only**: no dataset file (e.g. access is under a Data Use Agreement). Drafts come only from protocol, questionnaire, papers, or other documentation. Never invents what the underlying data looks like.

**Sensitive data classification gate**: before opening any dataset file, every skill checks for signals that it's classified Restricted, Sensitive, or Highly Sensitive (a known classification, a DUA, a confidentiality notice, or your own description). If present, the skill won't open the file at all — it drops to Mode B and tells you why, drafting from documentation only. You can explicitly authorize inspection anyway if you confirm you're allowed to share it.

## How to catalog a dataset

Invoke the skill with a forward slash followed by its name, then your request — for example:

> `/catalog-dataset` I need to fill out a data profile for the XYZ dataset. It's a CSV file at [path or link], and I have a study protocol I can share too.

Plain natural language (no `/`) can also trigger the skill if it matches closely enough, but the slash form is the reliable way to invoke it directly.

The first time you do this on a machine, Claude will ask for the folder path from Setup and remember it after that — see "Where everything lives" below. From there:

1. **First pass** — Claude drafts the whole thing itself from whatever you shared (the dataset file, protocol, papers, etc.), filling in as much as it can on its own.
2. **Section-by-section review** — it walks through the draft with you one section at a time, showing what it filled in and why, and revises based on your feedback until you approve that section before moving to the next.
3. **Generate** — once every section is signed off, it generates the Excel file(s) directly in your synced folder — no export step.

Once it's done, here's how to tell what's finished versus what still needs your attention before treating the file as final:

* **DataBio sheet**: an unresolved question is a blank Answer cell, with Confidence reading "Needs human input" and Source explaining what's needed. Everything else gets a real Confidence (High/Medium/Low) and a Source attribution (a citation, "Generated by AI, reviewed and approved by {reviewer}," or "Human input.").
* **Metadata sheet**: an unresolved field is simply a blank Response cell — this sheet has no Confidence/Source columns; that context lives only in chat and `catalog_draft.json` while drafting.
* **DataDict.xlsx**: Any variable that needs review will have a yellow cell with an Excel comment, and any sensitive variable will have a red cell.

Resolve these before treating a catalog as final — scan the DataBio sheet for "Needs human input" and the Metadata sheet for blank Response cells.

## Skills

Each skill lives in `skills/<name>/SKILL.md`. You may invoke by name (e.g. `/catalog-dataset`) or by asking for what it does — see each skill's "When to use this skill" section.

### `catalog-dataset` — primary entry point

Fills the whole data profile (Metadata + DataBio) in one pass: drafts everything, reviews the Metadata table with you as a whole, then walks through DataBio section by section, then generates the Excel file directly into SharePoint. **Use this by default.**

### `metadata` / `data-bio`

Fill one sheet at a time instead of the whole profile — `metadata` for the 18 admin fields, `data-bio` for the 22 narrative questions. Reach for these only when you specifically want just one sheet.

### `data-dictionary`

Fills `DataDict.xlsx` — always separate and optional, never bundled in automatically. Works from the actual data file or from documentation alone; if the dataset is several distinct files, it'll ask whether you want one combined dictionary or one per file.

### `assess-dataset`

A standalone data-quality/usability check (completeness, consistency, validity, etc.) — not part of the catalog output, but useful before or alongside cataloging.

## Repo layout

```
.claude-plugin/       plugin.json + marketplace.json -- makes this repo installable via /plugin
generate_catalog.py   Fills the SharePoint-hosted templates from catalog_draft.json
catalog_draft.json    Working draft for the dataset currently being cataloged
skills/
  catalog-dataset/   metadata/   data-bio/   data-dictionary/   assess-dataset/
```

`DataProfile.xlsx` and `DataDict.xlsx` are **not** in this repo — the masters live in the SharePoint `_Templates_` folder with the `Data Profiles` directory, which is the single source of truth for template content.
