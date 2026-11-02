---
schema: "archdoc/v1"
id: DL-0011-lane-ml-risk-assets
title: "RPT-0014 lane ml-risk-assets: WAVE 1 calibration"
type: process
status: draft
version: "0.1.0"
date: "2026-10-30"
updated: "2026-10-30"
record: DL-0011
---

# Lane ml-risk-assets: WAVE 1 calibration (#81)

AI-assisted research record for #81 (lane ml-risk-assets, WAVE 1, under #86), as required by
`CLAUDE.md`. It covers **calibration only**, LANES.md Step 1: the three shared sources, done
independently. Subset-1 (library PR) and WAVE 2 extraction (gated by #84) are not part of it.

## Question asked

Prepare this lane's own version of the three calibration records, without looking at other
lanes' versions, following the WAVE 1 instructions in `research/0014-ai-threat-model/LANES.md`:

- S-0855, NIST AI 100-2e2025;
- S-0166, Greshake et al., indirect prompt injection;
- S-0728, BIML's architectural risk analysis of ML systems.

Each record is a library-format `record.yaml` plus a `summary.md` that has the six
`summarize` sections and the RPT-0014 applicability table.

## What was run

- **Tool.** One interactive Claude Code session (desktop app, model `claude-opus-5-5`),
  driven by @kriishnaa-18 with a human review checkpoint after each source.
- **Not run.** No `rpt0014-extract` or `rpt0014-sweep` workflow, no subagents, and no
  `bin/fetch-pdfs`.
- **Effort.** Not confirmed. The session's exact reasoning-effort setting was not visible to
  the agent and was not recorded. No per-step override was requested.
- **Tokens.** Usage was not metered per source.
- **Where the work ran.** The session ran from the parent workspace, not from the `library`
  repo, so the library skills did not load automatically. Their instructions
  (`library/CLAUDE.md`, `ingest-reference`, `summarize`, `distill`) and `LANES.md` were read
  directly and followed by hand.
- **Isolation.**
  - The work was done in worktree `tmodel-wt/rpt0014-ml-risk-assets`, branched from `main`
    at `a013f87`.
  - Scaffolds were made with `bin/ingest` in a scratch copy of `library` at `3eacfd0`. The
    library worktree was not modified.
  - Library `bin/validate` ran on that scratch copy with the three records added.
- **Sources.**
  - Each primary PDF was fetched individually, one at a time, into a scratch directory outside
    every repo, and each sha256 matches `pdf-manifest.tsv`. There were three additional
    retrievals:
    - the Greshake PDF was fetched a second time, from its versioned arXiv v2 URL, to confirm
      the same digest;
    - NIST's errata notice (`nist.ai.100-2e2025_potential_updates.pdf`) was downloaded;
    - one request for ACM's PDF of the Greshake paper returned HTTP 403, so no ACM file was
      obtained.
  - Metadata was checked against publisher pages, Crossref, Crossmark and the arXiv API.
    ACM's article page was read in a browser because ACM blocks scripted retrieval.
  - BIML's risk labels were counted by script, and the count was checked by reading every
    section.

## Results

| Record | Type / maturity | Library applicability (sec / crypto / project) | RPT-0014 ratings (attacks / threat models / enumerations / attack→asset) |
|---|---|---|---|
| `nist-ai-100-2-e2025` | spec / informational | core / adjacent / core | adjacent / core / adjacent / adjacent |
| `greshake-2023-indirect-prompt-injection` | paper / unset | core / none / core | core / adjacent / adjacent / core |
| `biml-ara-ml-2020` | paper / white-paper | core / adjacent / core | adjacent / core / adjacent / core |

Every linked id in the summaries is labelled by where it comes from:

- **Source:** stated in the document.
- **RPT-0014:** already in the preliminary, AI-generated artifacts.
- **This pass:** this lane's reading.

All 73 distinct AIT-, TM-, INC-, A-, C-, R- and DEC- ids cited exist in the RPT-0014
artifacts or ARCH-0001.

## Accepted, corrected and rejected

**Corrections made at human review** (@kriishnaa-18). Each was accepted before the next source
was started.

- *NIST*:
  - `publisher` was simplified to NIST, with the co-author affiliations moved to the
    authorship line.
  - A scaffold comment claiming that every new spec version needs a separate record was
    removed, because it conflicts with the schema's one-record-per-line `versions` note. The
    library's own instructions disagree on this point (see Tooling gaps). This record follows
    the schema and does not resolve the policy.
  - The AIT counts and the A-/C- placements are now labelled as RPT-0014's or this pass's,
    not NIST's.
- *Greshake*:
  - `date` is now the ACM version of record (2023-11-26), not arXiv v1.
  - An undeclared `venue` field was removed and its content moved to the summary.
  - Verified locators were added for four references.
  - ACM's Corrected VoR (2024-01-10) is now noted as not compared.

**Rejected or withdrawn by this pass.**

- Two candidate reference matches were false positives and were dropped: Greshake [9] →
  S-0741, a different paper on ChatGPT plugins; and BIML [7] → S-0154, a later membership
  inference paper.
- For Greshake's remote-control and fraud demonstrations, AIT-124 (AI services as C2) and
  AIT-126 (AI-automated phishing) were considered and rejected. Both describe an attacker
  using AI, not a compromised integrated LLM.
- For NIST, R-010 and DEC-008 were rejected as `bears_on`, because the source uses no CWE ids.
- No `maturity` was set for the Greshake paper: no level applies, and the rule is not to guess.
- Statements not supported by the source were removed before review:
  - that the systems Greshake tested have since been retired (from background knowledge);
  - which BIML components sit on which attack surface (drawn only in Fig. 2, not stated in
    the text);
  - several short verbatim phrases, now paraphrased, because quotes belong in `quotes.md`.
- Reference expansion (stubs) was deliberately not done. It starts with subset-1, as
  LANES.md Step 2 says.

## Source limitations found

- **NIST.** NIST's errata (2025-06-03) says the page-x id index is wrong under GenAI
  availability: the correct ids are NISTAML.016 and .017, which the body already uses. There
  is no machine-readable release of the ids, and agents (§3.5) have no id.
- **Greshake.**
  - The record was built from arXiv v2. The ACM version of record and the Corrected VoR were
    not read (ACM returns 403 to scripts).
  - The evidence is qualitative only, with no success rates.
  - The paper gives two repository URLs, which resolve to the same repository.
- **BIML.**
  - It has 79 risk entries under 78 labels: `inference:3` is used twice.
  - Four cross-references cite the wrong number.
  - The cover date (2020-01-13) differs from the publisher's date (2020-01-20).
  - It predates GenAI.
  - The Tay example cites an unrelated reference ([32]).

## Independence

The contents of other lanes' calibration files were not opened. Two kinds of information about
the other lanes were seen during planning, before this lane's calibration began.

**PR descriptions.** The descriptions and file lists of two calibration PRs were read while
their status was being checked:

- **tmodel#117** (@paria03, agentic-mcp). It states no ratings. It notes two things: the
  Greshake arXiv v2 PDF names no venue, and BIML's own count of 78 risks was recorded without
  being reconciled id by id.
- **tmodel#187** (@Clovier, supply-chain-infra). It states headline ratings for all three
  sources, and these findings:
  - the Greshake venue, confirmed through Crossref;
  - BIML's labels as unsafe keys (79 entries under 78 numbers, four wrong cross-references);
  - NIST's errata for the id index, plus two NIST references whose DOIs resolve to other
    papers;
  - CWE 5.0 having been published.

**File names only.** Listings showed the paths of the six calibration files under
`calibration/agentic-mcp/` on `main`, and the paths in #117's and #187's file lists. No file
contents were read.

How that was handled:

- None of #187's ratings was used. This lane's ratings were set from the sources.
- The overlapping findings were re-derived independently: the Greshake venue from Crossref,
  BIML's label defects by script from the PDF, and the NIST id-index errata from NIST's own
  errata notice.
- Two of #187's points were not checked and are not used here: the NIST DOI mismatches, and
  CWE 5.0, which does not bear on these three sources.
- The overlap is disclosed here so that `calibration/COMPARISON.md` can weigh it.

## Notes for the integration lane (not edits)

`sources.md`, `threat-models.md`, `report.md` and `attack-catalog.yaml` were not edited.

- **S-0855 (NIST)**
  - `sources.md` types it `standard`, but the document says it is voluntary guidance and not
    a standard.
  - TM-004 says "25+ leaf ids"; there are exactly 25.
- **S-0166 (Greshake)**
  - The venue is marked "from memory"; it is confirmed as AISec '23,
    doi:10.1145/3605764.3623985.
  - The `sources.md` row writes `ASI01` without the year suffix.
  - AIT-064's components omit C10, C14 and C20, which the paper's demonstrations reach.
  - There is no AIT for code-completion context injection.
  - It is not in `threat-models.md`.
- **S-0728 (BIML)**
  - The date should be 2020-01-20, not 2020-01-13.
  - "78 risks" is in fact 79 entries under 78 labels.
  - The `report.md` §5 BIML row credits the 2020 document with a vendor-boundary concept it
    does not contain (it is presumably from S-0739).
  - TM-014's comparison row marks its threat ids as stable.

## Tooling gaps noticed (library; for a library issue, not fixed here)

- `bin/adapters/paper.yaml` emits `venue: ""`, and also top-level `media_type` and `pages`.
  None of these is declared in `schema/record.schema.yaml`.
- `bin/validate` does not reject undeclared fields, so they pass silently.
- The versioning instructions conflict:
  - `library/CLAUDE.md` (line 20) and the `spec` adapter template (`bin/adapters/spec.yaml`,
    line 1) say a new version of a spec is a new record linked by `supersedes`.
  - `schema/record.schema.yaml` (`storage.versions`, line 37) says one record per document
    line, tracking the current version, with superseded versions kept under
    `versions/<version>/`. A separate record is made only for a document that obsoletes
    another.

  Neither file was changed; the policy is the library's to settle.

## Validation

- **Library `bin/validate`.** Run on a scratch copy of library `3eacfd0` with the three
  records added. Result: 0 errors and no new warnings against the baseline (604 records, 99
  pre-existing warnings). `bin/export`, `bin/reindex` and `bin/render-html` also succeed for
  all three.
- **tmodel.** `bin/validate-archdoc` reports 0 errors and `check_identities.py` is clean.
- **No document bytes are committed.**
