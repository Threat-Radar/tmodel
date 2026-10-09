---
schema: "archdoc/v1"
id: ADR-0006
title: "Risk metric — composite vector (feasibility + impact + mitigation-status + derived risk)"
short_title: "Risk composite vector"
description: "Accepts DEC-003: the tmodel risk metric is a composite vector shown alongside its inputs, never collapsed to one number. Feasibility uses the ISO/SAE 21434 Table-1 method (human-rated at MVP); impact is the ISO 21434 S/F/O/P vector; mitigation-status is a peer; derived Risk = M(Impact, Feasibility) per 21434. Common Criteria is display-only (numbers + label + indicator). Supersedes the withdrawn ADR-0005 draft."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-08"
updated: "2026-10-08"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0006-risk-composite-vector.md
accepts: DEC-003
defers_to: ARCH-0001
---

# ADR-0006 — Risk metric: composite vector

**Status: accepted (2026-10-08). Accepts DEC-003.** The sponsor chose the composite-vector
risk metric that iteration 5–7 developed and `ARCH-0001-PROPOSAL` §3 carries (proposed.10/.11,
DL-0011). This **supersedes the withdrawn ADR-0005 draft** (composite-risk-vector, closed #70) —
a bot authored that draft and self-marked DEC-003 accepted, which was rejected; the *idea* was
affirmed and folded into the proposal, and this ADR accepts it through the proper gate.

## Context

- `ARCH-0001` §6 kept DEC-003 open across CVSS, custom, ISO/SAE 21434, Common Criteria, or a
  composite. RPT-0001 (risk metrics) and RPT-0007 (ISO 21434 TARA) surveyed the field.
- The sponsor's standing guidance (AskUserQuestion, iteration 7): **ISO 21434 Table-1 as the
  feasibility *method*; Common Criteria as *display only*.** The risk is shown with its inputs,
  not instead of them.

## Decision (DEC-003)

The risk metric is a **composite vector**, not a single score. Its components are **peers**,
each shown alongside the derived risk, never replaced by it:

| Component | Definition |
|---|---|
| **Feasibility** | Path-level attack feasibility on the **ISO/SAE 21434 Table-1 4-point scale** (high / medium / low / very-low), **human-rated at MVP**. The *method* is 21434 Table-1 — **not** CVSS exploitability. |
| **Impact** | The **ISO 21434 S/F/O/P vector** (safety / financial / operational / privacy), each `severe \| major \| moderate \| negligible`, human-supplied. Kept as four categories; collapsing to one number is **display only**. |
| **Mitigation-status** | A peer component (planned / in-progress / complete / accepted-risk / n-a), **not an input** that silently lowers the derived risk. |
| **Derived Risk** | `M(Impact, Feasibility)` per ISO 21434 — one value 1–5 per (threat-scenario, impact-category), per stakeholder where owners differ. The fold across attack paths is **worst-path**. |

- **Common Criteria** attack-feasibility (R-013) is **display-only**: its numbers, label, and a
  coloured indicator may appear in table views, but CC does not drive the derived risk.
- **MVP:** one stakeholder; feasibility is human-rated; `business_impact` is a distinct post-MVP
  axis and intentionally has **no** slot. More vector components require a further sponsor decision.

This is the `RiskScore` / `ImpactVector` shape already in `spec/schema/tmodel-object-model.linkml.yaml`
and documented in `spec/schema/OBJECT-MODEL.md`.

## Consequences

- Flips **DEC-003** to accepted; `ARCH-0001` §6 and R-011…R-013 now point here, and the §3 risk
  text in the proposal is ratified for the metric (DEC-001 object model remains open).
- `APP-0001` A-006 ("compute and show a risk score, simple at MVP") resolves to: show the vector,
  human-rate feasibility, derive Risk by the 21434 table.
- Does **not** reopen the ADR-0005 number; 0005 stays a tombstone so prior "ADR-0005 was dropped"
  references remain true.
- Feeds **I4 Risk & mitigation** (PLAN-0001): the metric is pinned, so I4 implements rather than surveys.

## Scope guard

Implemented only in **Threat-Radar/tmodel**. No single-number CVSS substituted for the vector; no
automatic risk reduction from mitigation-status; Common Criteria stays display-only; no second
stakeholder axis or `business_impact` at MVP without a further decision.
