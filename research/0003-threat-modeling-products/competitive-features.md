---
schema: "archdoc/v1"
id: RPT-0003-competitive-features
title: "RPT-0003 competitive feature list"
type: research
status: draft
version: "0.2.2"
date: "2026-09-26"
updated: "2026-10-12"
record: RPT-0003
---

# RPT-0003 — competitive feature list

This is the reusable feature list extracted from RPT-0003. Issue #37 asks for it as an
artifact for #15 and #18; earlier drafts routed it to #D1 and #D4, and those routings
are kept. It records evidence-backed observations from the reviewed sample of eleven
required products, plus the coverage-check products where noted. It is **not** an
accepted architecture or requirements specification. Each item must pass design and
human review before becoming a tmodel requirement. Evidence was last checked on
2026-10-12.

| id | candidate capability | evidence in reviewed sample | design relevance | routing |
|---|---|---|---|---|
| `CF-001` | Multiple starting points | blank canvas (TMT, Threat Dragon), questionnaire (IriusRisk, SD Elements), template, existing diagram (Tutamantic, Devici), IaC (ThreatModeler, ThreatTree), code (Devici Code Genius, Threat Composer CLI), AI draft | reduce blank-page cost without privileging one input source | #15, #18, #D1, #D4 |
| `CF-002` | Dual authoring | canvas/forms plus text, API or MCP over the same model (Devici, Threat Composer); text-first with generated visuals (pytm, Threagile) | test whether R-014/R-015 and developer automation can operate on one model | #15, #18, #D1, #D4 |
| `CF-003` | Explicit review state | status vocabularies: Threagile (`unchecked` … `false-positive`), Threat Dragon (Open, Mitigated, Accepted, Transferred, Avoided, Eliminated), Devici (accept, mitigate, accepted-risk), TMT (status, priority, justification); ThreatTree owner and treatment; Threagile `checked_by` | evaluate the minimum review record for R-018 while keeping proposal and verdict distinct | #15, #18, R-018 |
| `CF-004` | Deterministic rules beside AI | rules engine (IriusRisk), Codex (Devici), templates (TMT), custom YAML rules (Threagile) alongside AI drafting | require reproducible grounds and provenance for machine proposals | #15, R-018 |
| `CF-005` | Model diff and lifecycle | version-controlled model files (Threat Dragon, pytm, Threagile, Threat Composer), continuous re-assessment (ThreatModeler), PR-triggered refresh and version history (Devici); ThreatAtlas version/risk history in the coverage check | test temporal state rather than overwriting prior review | #15, R-021, DEC-009 |
| `CF-006` | Work-item closure | ticket close → risk Mitigated (ThreatTree); status sync from Jira/Azure DevOps (Devici); 8 trackers plus verification-tool results (SD Elements) | evaluate ownership, implementation links and verification evidence for mitigations | #15, #18, R-021 |
| `CF-007` | Portfolio and focused views | dashboards and registers (SD Elements, ThreatTree, Threat Composer insights) beside per-element findings | support executive, security-reviewer and developer tasks without duplicating domain facts | #18, ADR-0003 / APP-0001 |
| `CF-008` | Open interchange | OTM (IriusRisk, Devici, SD Elements, Threat Dragon), STIX 2.1 export (ThreatTree), TM-BOM (Threat Dragon), `.tc.json`, tool JSON/YAML | acceptance-test what each ADR-0007 import loses, including review, provenance, paths and layout | #15, ADR-0007, R-005 |
| `CF-009` | Reusable knowledge | templates, Codex, threat/control packs, custom rules | separate reusable patterns from product-instance facts and preserve attribution | #15, R-030 |
| `CF-010` | Evidence-bearing reports | PDF/DOCX/HTML/Markdown reports with rationale and status | treat export as a review artifact, not as the canonical graph | #18 |
| `CF-011` | Attack trees linked to architecture | AND/OR attack trees linked to a DFD (ThreatTree); generated attack trees (STRIDE GPT, coverage check) | closest precedent for AttackPath; tmodel needs ordered steps as well as AND/OR structure | #15, #18, DEC-001, R-014/R-015 |
| `CF-012` | AI agent surface with attributable actions | hosted MCP with human-initiated actions and per-call audit log (Devici); MCP server and CLI drafting starter models (Threat Composer); explicit AI proposals and approval documented by ThreatAtlas in the coverage check | an agent may propose; every change must stay attributable and reviewable | #15, R-018, APP-0001 A-045 |
| `CF-013` | SBOM/scanner verification integration | OWASP Dependency-Track and other verification tools are supported by SD Elements; the reviewed documentation does not establish the exact CVE-to-mitigation mapping | test how scanner/SBOM findings can supply verification evidence without assuming an undocumented mapping | #15, R-010, R-021, DEC-008 |

## Evidence and acceptance notes

- Supporting sources and exact reviewed OSS revisions are in [`sources.md`](sources.md).
- No product was acceptance-tested. “Documented” means first-party material
  states the capability; it does not establish completeness or fitness for tmodel.
  OSS entries were read from source at pinned commits.
- `CF-005` and the tmodel implications in `CF-003`, `CF-004`, `CF-006` and `CF-012`
  are researcher inferences to validate during design review.
- Library ingestion of the frontier sources remains outstanding before these are
  complete project references.
