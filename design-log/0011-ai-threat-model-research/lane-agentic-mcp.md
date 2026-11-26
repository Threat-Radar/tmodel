---
schema: "archdoc/v1"
id: DL-0011-lane-agentic-mcp
title: "RPT-0014 agentic/MCP WAVE 1 bibliography completion (#78)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-25"
updated: "2026-11-25"
record: RPT-0014
issue: 78
defers_to: ARCH-0001
---

# Agentic/MCP lane: WAVE 1 bibliography

Owner: @paria03. This records the bibliography completion pass requested for
[#78](https://github.com/Threat-Radar/tmodel/issues/78). It does not rerun the
independent calibration or claim human review of newly added metadata.

## Prior work and remaining gap

- Calibration: merged [#117](https://github.com/Threat-Radar/tmodel/pull/117),
  with three pairs of calibration `record.yaml` / `summary.md` files.
- Subset-1: merged [library#22](https://github.com/Threat-Radar/library/pull/22),
  with 19 summarized records; S-0848 reused `cisa-ai-in-ot-principles`.
- Existing source review: @kriishnaa-18 checked five records against their sources
  in [this comment](https://github.com/Threat-Radar/library/pull/22#issuecomment-6355715327).
  Those comments remain the evidence of the earlier check; no new signature or
  approval is inferred from them.
- The remaining WAVE 1 checkbox covered controlled tags, applicability and
  reference expansion. PR #22 explicitly left the reference stubs unfinished.

## This pass

Work started from tmodel `18e28cd` and independent library `ba336a9`. The library
submodule and its pin are unchanged. The implementation is in the library branch
`fix/78-agentic-bibliography-closeout`; this note is on
`docs/78-agentic-bibliography-closeout` in tmodel.

1. Reconciled all 20 assigned subset-1 rows in `wave1-assignments.csv` with their
   library records. Checked the six summary sections, the three applicability
   axes and all four RPT-0014 topic rows. Added the missing lane applicability
   table to the reused CISA summary, explicitly as proposed ratings; retained
   that record's full extraction, tags, primary topic and source metadata.
2. Promoted the lane's 14 AI subject terms to the controlled tag list. Removed
   redundant shelf labels from lane-authored tags and added `prior-art` to the
   two OWASP records. Added an owned topic that includes all assigned sources.
3. Read the assigned sources' bibliography or linked security references. Used
   publisher URLs, versioned PDFs, reference numbers and named bibliography
   entries as locators. Compared source identities against all existing library
   records and the 1,181-entry `sources.md` corpus before ingestion.
4. Recorded 147 distinct first-hop cited works in 190 citation edges: 10 held
   records, 58 already in the corpus, and 79 new bibliography stubs. `cites`
   captures source facts; new stubs carry `cited_by` as explicitly required by
   WAVE 1 Step 2.5. The library audit calls out its difference from the library's
   draft reference-semantics policy, so review can confirm that choice.
5. Used `bin/ingest --stub` for each new record. Left every new record at
   `status: stub`, `confidence: low`, with no invented applicability, acceptance
   or `bears_on` claims. @paria03 owns their future reading in #78; any full
   extraction is #73 work after #84. No third-party source document is committed.

The reviewable evidence lives alongside the actual library records:

- `docs/agentic-mcp-wave1.md`: scope, decisions, limitations and ownership;
- `docs/agentic-mcp-wave1/sources.csv`: 20-source assignment and capture audit;
- `docs/agentic-mcp-wave1/references.csv`: 190 citations with source-side locators,
  target identity and disposition.

These paths will be linked to the library PR when publication is authorized.
This tmodel note intentionally does not duplicate the CSVs or bump the library pin.

## Accepted and rejected findings

- **Version drift:** the Khodayari unversioned PDF moved to v2. Fetching v1
  recovers the original recorded SHA-256. Twelve source PDFs, including CISA,
  match their original hashes. Six current HTML pages differ; Lenovo and
  Tracebit required indexed publisher text. Original hashes are preserved,
  rather than silently substituting later pages for prior evidence.
- **Identity changes:** current titles, older citation titles and stable arXiv
  identifiers are distinguished. SecGPT / IsolateGPT and the renamed prompt
  extraction paper do not create duplicate works. The Cursor FAQ does not stand
  in for the two original research publications it cites.
- **Access failures:** four cited targets could not be retrieved. They remain
  explicitly identified, low-confidence stubs without source digests; retrieval
  failure is not presented as a completed reading or a verified paper claim.
- **Source errors:** Jones [5] misidentifies WebArena's arXiv number. Jones [18]
  and Habler [20] provide no verified primary locator for the claimed work.
  Unverifiable claims are documented instead of manufacturing records for them.
- **Scope:** no recursive snowballing, optional news sweep, generic AI/ML methods
  or broad policy bibliography. The library audit gives source-specific
  exclusions and treats catalog sections as parts, not separate publications.
- **Review boundary:** no previous review is repurposed as approval of this pass.
  New metadata, the tag promotion, reference semantics and the added CISA
  applicability rows need review through the normal PR process.

## Validation

Library baseline: 686 records, 381 written, 305 scaffold, 42 fully extracted,
24 topics, 0 errors and 99 warnings. After the bibliography pass: 765 records,
381 written, 384 scaffold, 42 fully extracted, 25 topics, 0 errors and the same
99 warnings. The increase is exactly 79 intentional stubs, not 79 read sources.

Local checks:

- `bin/validate` and `bin/test_yaml.py`;
- `bin/check-requirements` and `bin/check-artifacts` using the pinned validation
  environment;
- `bin/export`, then `bin/reindex`, with one bibliography entry per record and
  no dangling relations;
- `bin/check-pr-extraction ba336a9`, preserving the existing CISA extraction;
- assignment IDs, summary sections, applicability axes, controlled tags,
  reference dispositions, new-stub ownership and citation backlinks reconciled;
- tmodel `python3 bin/validate-archdoc` and `git diff --check` in both repos.

The branch is kept local pending publication authorization. Hosted CI has not
run for these commits; local validation is not reported as hosted CI success.

## Issue status and next stage

Once the bibliography change is reviewed and merged, the remaining **WAVE 1**
checkbox can be checked with links to both PRs. Keep #78 open: the sponsor's
[#84 gate](https://github.com/Threat-Radar/tmodel/issues/84) requires comparable
calibration units before scaling extraction and explicitly keeps the lane issues
open. This pass does not declare that gate passed.

Later WAVE 2 work remains the six extraction units listed on #78, their complete
file sets and reconciled `verify.md` files, the required news sweep, and real
review-partner signatures. Neither the calibration comparison nor another
person's review duty is silently assigned a completion status here.

Publication should use **Part of #78**, not **Closes #78**. No issue checkboxes,
PR comments, source reviews or acceptance decisions were posted by this pass.
