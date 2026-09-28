---
schema: "archdoc/v1"
id: RPT-0003-competitive-features
title: "RPT-0003 competitive feature list"
type: research
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
record: RPT-0003
---

# RPT-0003 — competitive feature list

This is the authoritative reusable feature extraction from RPT-0003 for #D1 and
#D4. It records evidence-backed observations from the reviewed product sample;
it is **not** an accepted architecture or requirements specification. Each item
must pass design and human review before becoming a tmodel requirement.

| id | candidate capability | evidence in reviewed sample | design relevance | routing |
|---|---|---|---|---|
| `CF-001` | Multiple starting points | blank canvas, questionnaire, template, existing diagram, IaC, code, and AI draft are documented across the sample | reduce blank-page cost without privileging one input source | #D1, #D4, DEC-005 |
| `CF-002` | Dual authoring | diagram/form authoring and text/API automation appear as complementary approaches | test whether R-014/R-015 and developer automation can operate on one model | #D1, #D4, DEC-006 |
| `CF-003` | Explicit review state | products document combinations of priority, status, justification, decision, assignee, and linked work-item history | evaluate the minimum review UI for R-018 while keeping proposal and verdict distinct | #D1, #D4, R-018 |
| `CF-004` | Deterministic rules beside AI | STRIDE, knowledge-base, and custom-rule analysis remain inspectable alongside AI-assisted drafting | require reproducible grounds and provenance for machine proposals | #D1, DEC-004 |
| `CF-005` | Model diff and lifecycle | version-controlled model files, continuous assessment, and incremental project workflows are documented in parts of the sample | test temporal state rather than overwriting prior review | #D1, R-021, DEC-009 |
| `CF-006` | Work-item closure | Jira, GitHub, Azure DevOps, and ServiceNow delivery/status workflows are documented by commercial products | evaluate ownership, implementation links, and verification evidence for mitigations | #D1, #D4, R-021 |
| `CF-007` | Portfolio and focused views | dashboard/report and per-element finding views serve different roles | support executive, security-reviewer, and developer tasks without duplicating domain facts | #D4, DEC-006 |
| `CF-008` | Open interchange | OTM, emerging TM-BOM, tool JSON/YAML, and APIs provide different levels of portability | acceptance-test semantic round trips, including review, provenance, paths, and layout | #D1, DEC-002 |
| `CF-009` | Reusable knowledge | templates, threat/control packs, and custom rules recur across products | separate reusable patterns from product-instance facts and preserve attribution | #D1, R-030 |
| `CF-010` | Evidence-bearing reports | diagrams, rationales, unresolved findings, and control status appear in documented exports | treat export as a review artifact, not automatically as the canonical graph | #D4, DEC-006 |

## Evidence and acceptance notes

- Supporting sources and exact reviewed OSS revisions are in [`sources.md`](sources.md).
- No product was acceptance-tested. “Documented” means first-party material
  states the capability; it does not establish completeness or fitness for tmodel.
- `CF-005` and the tmodel implications in `CF-003`, `CF-004`, and `CF-006` are
  researcher inferences to validate during design review.
- #P1 library ingestion remains required before these sources are complete
  project references.
