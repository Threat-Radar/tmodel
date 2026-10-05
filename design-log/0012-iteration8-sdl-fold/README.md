---
schema: "archdoc/v1"
id: DL-0012
title: "Iteration 8 — fold the SDL / conformance model into the proposal"
type: process
status: draft
version: "0.1.0"
date: "2026-10-05"
updated: "2026-10-05"
record: DL-0012
---

# DL-0012 — Iteration 8 SDL fold

AI-assisted design record for #15 (per `CLAUDE.md`). Folds the SDL / conformance design
(captured in **DL-0009**, researched in **RPT-0013 + MAP-0001**) into
`ARCH-0001-PROPOSAL` (proposed.10 → proposed.11, new §3c). Nothing accepted (ADR-only). The SDL
guideline **library records are being ingested in parallel** (RPT-0013 / #67).

## What folded (§3c)

- **R-040 `Mitigation.kind` {technical, documentation, process}** — the one MVP-adjacent piece;
  shows as the mitigation-status component of the risk vector (§3).
- **R-041 SDL / SecurityProgram** — ordered, named, dated `Gate`/`Checkpoint`/`Milestone` nodes +
  program management, mapped onto the `LifecyclePhase` axis (§3b); corporate gate-naming via the
  MAP-0001 gate crosswalk. Post-MVP.
- **R-042 conformance validation** — `Requirement`↔`Mitigation`/`Evidence`+`Review`; the automatable
  "every in-scope threat has an approved, evidenced mitigation" gate check (RPT-0013 §4 design:
  schema + policy rules + signed evidence). Proves linkage + approval, **not adequacy** (human
  assessment remains). Post-MVP; connects to #19.
- **R-043 governed document-views** — a threat-model report and an SDL plan are owned / approved /
  versioned **snapshot-views over the KG-SoT** (extends §10 + §4); approval attaches to a
  commit/digest so it is reproducible (SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word as prior art).
  Post-MVP.
- **R-044 `Requirement` object + cross-spec crosswalk** — `maps_to` edges = the MAP-0001 overlap.
  Post-MVP.

## Guardrails carried from the iteration-7 critic (DL-0010)

- **SDL is post-MVP** (MVP-overload finding) — only `Mitigation.kind` is MVP-adjacent.
- The SDL document-owner/approver is a **`Party` role** (one identity, many facets — §2b), not a new
  actor type.
- Custody/returns provenance stays **supply-chain / radar** (§3b/§4), not the epistemic Assertion spine.
- Conformance/business impact is **not** a re-indexing of the ISO S/F/O/P (§3).

## Rejected / adapted

- Nothing rejected; the SDL design was pre-shaped by DL-0009 against the critic's guardrails.
- **Adapted scope:** everything SDL is modelled-not-built for Nov 5.

## Ingestion status (parallel; RPT-0013 / #67)

Batch 1 (public): **NIST SSDF 800-218/218A** (FX-1-grade — real `pdftotext` pass), **OWASP SAMM v2**
and **SLSA v1.0** (summarized — WebFetch summary-grade, full-FX-1 verbatim verify pending, T-029).
Remaining stubbed; **paywalled** (IEC 62443-4-1, ISO/IEC 27034, ISO 26262, BSIMM) flagged for the
iTeh-preview / ask-first path. See the library PR.

## Next

A fresh adversarial-critic pass on proposed.11 before any ADR; finish FX-1 verify on the batch-1
records; ingest the paywalled set via the preview/ask path; then the SDL/DEC-009 and clean DEC-003
ADRs. DEC-001 accepts last.
