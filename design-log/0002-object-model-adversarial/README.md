---
schema: "archdoc/v1"
id: DL-0002
title: "Adversarial review of the object model (iteration 1 → 2)"
type: process
status: draft
version: "0.1.0"
date: "2026-09-30"
updated: "2026-09-30"
record: DL-0002
---

# DL-0002 — Adversarial review of the object model

AI-assisted design record for #15, per `CLAUDE.md` ("the design log is not optional").

## Question asked

Break ARCH-0001-PROPOSAL-v0.2.0 iteration 1: find unmodelable scenarios, missing
nodes/edges, false "greens" in the coverage matrix, standards mis-alignment, and
over-engineering — before research (#6/#7/#9) lands.

## What was produced

An independent adversarial-critic agent (fresh context; verified claims against the
library records for ISO 21434, STIX 2.1, BRON, D3FEND, PROV-O) returned **16 ranked
findings (H1–H16)** with concrete fixes and a toughened test suite.

## Accepted (folded into iteration 2)

All 16, in substance:
- **H1/H7** shared, **CPE/purl-anchored** `Component` + `uses_component` (unlocks the
  multi-product supply-chain query — the MVP's core value). Adopt the full BRON
  backbone (+CPE).
- **H2** cross-product `AttackPath` (`pivots_to`), anchored to assets not one product.
- **H3** `precondition`/`postcondition` on `AttackStep`; AND/OR gates defined over them
  (resolves the open AND/OR case).
- **H4** time/version axis (`valid_from/to`, versioned `ProductInstance`) — R-021 was a
  false green; now genuinely covered.
- **H5/H12** edge **reification** (`Assertion`) so review/confidence/provenance attach to
  AI-proposed *edges*; provenance downgraded to ◐ (gates DEC-002/DEC-004).
- **H6** restore `ProductFamily` + `member_of`.
- **H8** restore `DamageScenario` (S/F/O/P, many-to-many with threats) + `attack_feasibility`.
- **H9** mitigation `effectiveness`/residual + `reduces` to a specific step/path.
- **H10** restore `TrustBoundary`.
- **H11** `ThreatActor` (capability) + D3FEND `defends_against`.
- **H13** drop the redundant generic `Threat` (STIX has none) → AttackPattern + ThreatInstance + ThreatActor.
- **H14** add `Finding` (concrete weakness, no CVE required) — home for radar findings / 0-days.
- **H15** hierarchical `rolls_up_to` with worst-case-per-category aggregation + PROV `wasDerivedFrom` + human override (resolves the open roll-up case).
- **H16** defer `Requirement`/`WorkProduct`/audit **out of the MVP core** (#19); trim `CybersecurityProperty` to an attribute and collapse the mitigation enum for MVP.

## Rejected / adapted (and why)

- Nothing rejected outright — the critique was sound.
- **Adapted:** `CybersecurityProperty` kept as an **attribute** for the MVP (a node
  later) and the mitigation status collapsed for MVP, per H16's own trim guidance —
  i.e. accepted the *direction* but scoped the representation to the MVP.
- **Audit objects deferred, not deleted** — they stay in the model's roadmap for #19,
  just outside the MVP core.

## Next

Iteration 3: fold in research #6/#7/#9; **decide the reification mechanism (H5) →
DEC-002/DEC-004**; build `spec/vectors/` cases 7–13; then fold into ARCH-0001 §3/§4
and accept DEC-001 via an ADR.
