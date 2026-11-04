---
schema: "archdoc/v1"
id: DL-0011-lane-ml-risk-assets
title: "RPT-0014 Wave 1 calibration, lane ml-risk-assets (#81): S-0855, S-0166, S-0728"
type: process
status: draft
version: "0.1.0"
date: "2026-11-01"
updated: "2026-11-01"
record: RPT-0014
issue: 81
defers_to: ARCH-0001
---

# Lane ml-risk-assets: Wave 1 calibration (#81)

AI-assisted design record (per `CLAUDE.md`). Lane owner: @kriishnaa-18, working with Claude Code. Every rating below is the agent's proposal, reviewed and approved source by source by the lane owner. It is a hypothesis for the #84 gate, not a reviewed library record.

## Question asked

Wave 1 Step 1 (LANES.md): independently produce `record.yaml` and `summary.md` for the three shared calibration sources. Each needs all six summary sections and the four-topic RPT-0014 applicability table, and must not look at any other lane's work. This was a fresh run: nothing from earlier attempts was reused.

## What was produced

| Source | Record | Library type / shelf | Files |
|---|---|---|---|
| S-0855 NIST AI 100-2e2025 | `nist-ai-100-2-e2025` | spec / nist | `research/0014-ai-threat-model/calibration/ml-risk-assets/nist-ai-100-2-e2025/{record.yaml,summary.md}` |
| S-0166 Greshake et al. 2023 | `greshake-2023-indirect-prompt-injection` | paper / academic | `.../greshake-2023-indirect-prompt-injection/{record.yaml,summary.md}` |
| S-0728 BIML ARA 2020 | `biml-ara-ml-2020` | paper / other | `.../biml-ara-ml-2020/{record.yaml,summary.md}` |

No library PR, stub records, `rpt0014-extract` run, Wave 2 extraction or knowledge-graph objects were made.

## Setup and independence

### Workspaces

- **tmodel worktree:** `tmodel-wt/issue-81-ml-risk-assets-wave1` on a new branch `issue-81-ml-risk-assets-wave1`, created from `origin/main` 8722e4b. It was created with `--no-checkout`, so no other lane's file ever reached disk.
- **Sparse checkout:** a non-cone explicit allowlist.
  - In `research/0014-ai-threat-model/`, only the 11 shared files plus `calibration/ml-risk-assets/`.
  - In `design-log/0011-ai-threat-model-research/`, only this file.
  - Verified by counts only, never by listing names: 0 files from other calibration directories and 0 other files from this design-log directory were checked out.
  - The main checkout (`issue-58-library-tables`) and the library submodule pin were not touched, and the submodule was not initialised in the worktree.
- **Library scratch clone:** a fresh clone of `Threat-Radar/library` `main` (3eacfd0), with push disabled.
  - It was used for `bin/ingest`, `bin/validate`, `bin/export`, `bin/reindex` and `bin/render-html`, and is never committed.
  - The session was moved to it after the S-0855 setup, so the library skills loaded natively. For S-0855's first pass, the `ingest-reference` and `summarize` SKILL.md files were followed as text. The `summarize` skill was then loaded through the Skill tool and applied to all later passes.

### What was not accessed

- The shared `calibration/` directory beyond its own lane path, including `COMPARISON.md`. Its existence was confirmed with one `git ls-tree` entry; the sparse check counted 6 tracked files in it, never by name.
- Any other lane's design-log, PR, description, comment, review or branch, and PR #192.
- An existing library worktree (`library-wt/rpt0014-ml-risk-assets-wave1`) and a remote branch (`origin/rpt0014-ml-risk-assets`). Both appeared in `git worktree list` and `git branch -a` output; neither was opened.
- A memory file from an earlier session about this lane. It was not read.
- Three existing library records (on library `main`) that contain an "RPT-0014 applicability" section. They appeared by filename in one `grep -l`; they were not opened.

### What was read

- **tmodel:**
  - `CLAUDE.md`, `LANES.md`, `wave1-assignments.csv`, ARCH-0001;
  - `design-log/README.md`, and `DL-0026` for the front-matter format;
  - from RPT-0014, used only to map ids and to check preliminary claims, treated as hypotheses: the rows and sections of `sources.md` for the three sources, `pdf-manifest.tsv` rows, `report.md` §1 and §4 vocabularies, `attack-catalog.yaml`, `threat-models.md` (TM-004, TM-014), `enumerations.md`, and `incidents.md` (INC-025).
- **library:**
  - `CLAUDE.md`, the skills, `schema/record.schema.yaml`, `schema/summary.template.md`, `schema/tags.yaml`, `docs/references.md`, and the `bin/` scripts;
  - a few unrelated records, for format only (for example `spotlighting-indirect-prompt-injection`, `sp-800-218a`, `nistir-8060`).

## Method

### Tools and model

- Claude Code desktop app, model Opus 5.5 (`claude-opus-5-5`).
- The reasoning-effort setting was not visible to the agent and is not recorded. Total token consumption is not available. The session context held about 594k tokens when this log was written; that is a snapshot, not a total.

### Sources and verification

- **Download.** Each PDF came from the publisher URL listed in `pdf-manifest.tsv` into `~/tmodel-pdf-cache/ai-threat-model/`, outside the repo.
  - `bin/ingest --fetch` failed on a local Python SSL certificate error, so every digest was computed with `curl` plus `shasum -a 256`.
  - All three matched the manifest (see the table below).
- **Reading.**
  - Text was extracted page by page with macOS PDFKit (`osascript`); nothing was installed.
  - Each body was read in full.
  - Key figures were rendered to PNG and examined visually: Greshake Figs. 2–3, BIML Figs. 1–2, and BIML's decorative pages.
  - Reference lists were parsed and checked mechanically, then key entries were checked by hand.
- **Metadata checks:**
  - S-0855: the NIST CSRC publication page and its errata PDF.
  - S-0166: the arXiv API and abstract pages, which show the version history, and Crossref, which gives the ACM DOI and venue. The ACM PDF returned HTTP 403.
  - S-0728: the BIML results page and the PDF metadata.
- **Identifier and reference checks:**
  - the arXiv API, for identifiers in conflicting NIST references;
  - Crossref, for the Saltzer and Schroeder citation;
  - the GitHub API, for the S-0166 demonstration repository;
  - one web search, for tooling that implements the NISTAML ids.

| Source | sha256 (manifest match) | Bytes, pages | Version and date as recorded |
|---|---|---|---|
| S-0855 | `4811fb6a…7646` ✓ | 1,964,469, 127 | E2025 final, released 2025-03-24; corrected PDF of 2025-04-01 |
| S-0166 | `428e23e8…0e81` ✓ | 7,306,999, 33 | arXiv v2 (2023-05-05) read; ACM AISec '23 version of record dated 2023-11-26, not read |
| S-0728 | `247d7f06…f312` ✓ | 848,055, 42 | v1.0 dated 1.13.20 on the cover; released 2020-01-20 per BIML and the PDF metadata |

## Results (as approved)

| | S-0855 | S-0166 | S-0728 |
|---|---|---|---|
| Security / Cryptography / This project | core / adjacent / core | core / none / core | core / adjacent / core |
| `bears_on` | R-020, DEC-009 (generic-to-product half) | R-020, DEC-009 (generic-to-product half) | R-020, DEC-009 (generic-to-product half) |
| Published attacks | core (47 AIT) | core (9 AIT) | adjacent (12 AIT) |
| Existing AI threat models | adjacent (TM-004) | adjacent (no TM entry) | core (TM-014) |
| Weakness enumerations | adjacent (30 NISTAML ids) | adjacent (6 NISTAML ids, verified via S-0855) | adjacent (its own 78 identifiers) |
| Attack → asset mapping | adjacent | core (for indirect prompt injection) | core (to components; no business assets) |
| Maturity / confidence | unset / high | unset / medium | unset / high |

All A-, C- and TB-ids in the three summaries are the agent's assignment onto RPT-0014's preliminary vocabularies. No source uses them.

## Human review: corrections and rejections

### Setup

- The lane owner required the bibliographically accurate type for NIST, not one chosen to avoid FX-1. The result is `spec`; FX-1 does not fire for a summarized record.
- The lane owner required natively loaded skills, investigation of any digest difference (none occurred), an explicit sparse allowlist that excludes `COMPARISON.md`, and `git status --untracked-files=all` for scope checks.

### S-0855

- **`bears_on`: rejected and replaced.** The agent first proposed DEC-008 and R-010. The source has no CWE, CVE or NVD content, so these were replaced with R-020 and DEC-009 on the strength of p. 37 and p. 41.
- **Weakness enumerations: changed from core to adjacent.** An attack taxonomy is not a weakness enumeration. The `ai-weakness-catalog` tag was removed for the same reason.
- **"The catalog over-links the source": withdrawn.** The agent had said `attack-catalog.yaml` linked 17 AITs that the report does not support. The catalog's NISTAML ids are class-level candidates, so the claim was reworded: 10 techniques are not described in the report and 6 are borderline, each with a page locator.
  - On re-checking, AIT-112 was found to be described and was linked.
- **Defect claims split.** They are now separated into confirmed errors and possible discrepancies.
  - The "inconsistent arXiv ids" turned out to be wrong DOIs or URLs, confirmed against the arXiv API.
- **Smaller fixes.**
  - Verbatim quotes were removed from `summary.md`, per the `summarize` skill.
  - The note that reference expansion is reserved for subset-1 was added.
  - Maturity was kept unset.

### S-0166

- **`cited_by: nist-ai-100-2-e2025` removed.** `docs/references.md` reserves `cited_by` for our own documents. The citation remains recorded in S-0855's `cites`.
- **`ai-threat-model` tag removed.** The paper gives a threat taxonomy, not a system threat model.
- **Figs. 2–3 checked visually.** The summary now separates what the paper identifies from the A-, C- and TB-ids the agent assigned.
- **Kept:** the ACM date, the arXiv v2 provenance, medium confidence, and leaving out R-018. R-018 was considered and not included because linking it would be the agent's inference.

### S-0728

- **Attack → asset mapping: kept at core after reconsideration.** The lane owner asked whether adjacent fits better.
  - LANES.md defines the linked ids as asset or component ids from `report.md` §1, and §1 defines components. BIML maps every risk to a component, so core was kept.
  - The missing business-asset vocabulary is stated explicitly. The lane owner approved this.
- **`cites` [13]:** now records the printed title and the corrected publication title separately.

## Source defects

**Confirmed:**
- **S-0855:**
  - the index entries for GenAI availability are wrong (NIST's own errata);
  - six wrong identifiers, at [34], [170], [237], [267], [410] and [449];
  - six duplicated reference pairs;
  - "Szedegy" misspelled five times.
- **S-0166:**
  - the demonstration repository is named two ways; both resolve to the same repository;
  - one citation is repeated as "[68, 68]";
  - references [1]–[33] carry only hyperlinks.
- **S-0728:**
  - 79 distinct risks under 78 identifiers, because `[inference:3]` is used twice;
  - four cross-references to the wrong number (pp. 15, 18, 19, 21);
  - reference [3] has volume and issue transposed and conflicts with the text's 1972 date;
  - [12] and [19] are duplicates;
  - [13] is mistitled;
  - `[model:2:Trojan]` cites a membership-inference paper;
  - Fig. 1 draws component 1 in a different shape from the one the text describes.

**Possible, not confirmed:**
- S-0855: the label for NISTAML.027 against its section heading; GenAI model extraction has no index entry; a cross-reference on p. 34.
- S-0728: the citation used for Tay; the gap between the cover date and the release date.

## Limitations and unresolved questions

- **S-0166's version of record was not read.** The ACM PDF returned 403. Crossref lists 72 references for it against 82 in arXiv v2, so the two texts may differ.
- **Not every screenshot was examined.** Greshake's screenshot images (Figs. 13–28) were reviewed through their captions and prompt text only.
- **Preliminary RPT-0014 catalog ids were not verified** where the source does not use them: ATLAS, OWASP and CWE in `sources.md`.
- **Implementation searches were limited.** One web search for NIST, and the publishers' own pages for the other two.
- **`cites` are calibration subsets:** 25 of 449, 17 of 82, and 21 of 35 references. Complete reference expansion and stub creation are left for subset-1.
- **Open questions for the integration lane, not acted on:**
  - whether S-0166 should get a TM entry;
  - whether `cited_by: RPT-0014` belongs on records, which `docs/references.md` lists as an open question.

## Validation

- **Library:** run in the scratch clone with all three records present.
  - `bin/validate`: 0 errors, with no messages for the three records.
  - `bin/export` and `bin/reindex`: succeed. Each record appears in `index/bibliography.md` and under R-020 and DEC-009 in `index/by-decision.md`.
  - `bin/render-html`: builds each page, and the generated `summary.html` stays gitignored.
- **tmodel:** `bin/validate-archdoc` gives 0 errors. It checks `spec/` and `project/` only.
- **Integrity:** each approved calibration was checked byte for byte against its SHA-256 snapshot after every later change. The worktree copies are byte-identical to the validated library copies.
- **Scope:** `git status --short --untracked-files=all` shows only the seven lane files. `git diff --stat origin/main` is empty, and there are no PDFs, HTML or images.

## Remaining Wave 1 work for #81

- The 20 `ml-risk-assets` subset-1 sources: records, summaries, tags, RPT-0014 applicability, and reference expansion with stub records.
- One library PR for subset-1, with a body that says `Part of Threat-Radar/tmodel#81`.
- A review of at least five of the review partner's records against their sources.
