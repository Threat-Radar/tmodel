---
schema: "archdoc/v1"
id: ADR-0005
title: "Composite risk vector — CC feasibility × impact × mitigation × derived risk"
short_title: "Composite risk vector"
description: "Accepts DEC-003: risk is a composite vector, not a single CVSS-like score alone. MVP components are attack feasibility (Common Criteria style), impact (21434-style S/F/O/P or the project's damage model), mitigation status, and a derived/aggregated Risk field, with explicit room for further components later. Updates ARCH-0001-PROPOSAL proposed.7 risk metric and DECISIONS-0001."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-02"
updated: "2026-10-02"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0005-composite-risk-vector.md
accepts: DEC-003
defers_to: ARCH-0001
---

# ADR-0005 — Composite risk vector (DEC-003)

**Status: accepted (2026-10-02). Accepts DEC-003.** The sponsor chose a **composite risk
vector**, not a single CVSS-like score alone. This settles the *shape* of risk for MVP
table/row views and for the schema; it does **not** invent additional vector components
beyond the MVP set below — those require a further Paul decision.

> **House path.** Land this file in-repo as
> `spec/ADR-0005-composite-risk-vector.md` (tmodel ADR layout). If a PR prefers the
> alternate `docs/architecture/` tree, keep the same body and set `canonical_path`
> accordingly; do **not** invent a parallel decision document.

## Context

- `ARCH-0001` §6 / §8 left **DEC-003** open: risk-metric scheme — CVSS / custom /
  ISO 21434 / Common Criteria / composite. Requirements **R-011…R-013** depend on it.
- `ARCH-0001-PROPOSAL` **v0.2.0-proposed.7** already proposed an ISO 21434-*shaped*
  MVP: path-level 4-point feasibility × per-category **S/F/O/P** impact, human-rated,
  **no CVSS at MVP**, with RiskScore = `M(Impact, Feasibility)`. RPT-0007 (#11 / PR #69)
  is research evidence for that framing; it does **not** accept DEC-003 by itself.
- Path A (ADR-0003, epic [#47](https://github.com/Threat-Radar/tmodel/issues/47)) builds
  progressive UI: **tables → KG → threat chains → WebGL**. I-App **Slice 1 (T-201)** is
  the tabular filter UI — the first place a risk column set will show up.

## Decision (DEC-003)

**Risk is a composite vector**, not a single scalar standing alone.

### MVP vector components

| # | Component | Meaning (MVP) | UI / table note |
|---|---|---|---|
| 1 | **Attack feasibility** | Common Criteria–style attack feasibility (align with CC / ISO 18045 attack-potential factors where useful; compatible with 21434 path-level feasibility scales in proposed.7) | Table column: **concise metric numbers + feasibility label + colored indicator** |
| 2 | **Impact** | Damage of the attack — align with **21434-style impact categories** where useful (**S/F/O/P**) or the project's damage model | Keep the category vector; any single-number collapse is a **display** choice, not the method |
| 3 | **Mitigation status** | Where the threat/path sits in the mitigation lifecycle (planned / deferred / complete / accepted-risk / n/a — refine with DEC-009 as it lands) | First-class column / field, not buried only inside a score |
| 4 | **Risk** | **Derived / aggregated** field for the row — computed from the other components (matrix / aggregation rules stay implementable; do not pretend one CVSS base score *is* the model) | Shown alongside the inputs, never instead of them |
| 5 | **Room for more** | Explicit extension point (“perhaps more later”) | **Do not invent new components** without Paul |

### Binding rules

1. **Vector > scalar.** A lone CVSS-like number is **not** the accepted scheme. CVSS (or
   CVSS exploitability-only, per proposed.7 / `#RC-15-13`) may appear later as a
   *refinement or input to feasibility* — not as a replacement for the vector.
2. **Feasibility is CC-flavored in the UI.** Table views MUST surface concise metric
   numbers, a human-readable feasibility label, and a colored indicator — not an opaque
   float alone.
3. **Impact stays multi-category when 21434-shaped.** Prefer S/F/O/P (or the project's
   damage model) over prematurely collapsing to one impact number.
4. **Mitigation is in the vector.** Status is a peer component of feasibility and impact
   for row display and filtering.
5. **Risk is derived.** The Risk column/field is aggregated from the vector; document the
   aggregation when it is implemented (matrix, max-over-categories, etc.). Do not invent
   a proprietary formula in agent sessions without recording it against this ADR.
6. **Extension gate.** Additional components need an explicit sponsor decision — update
   this ADR (or a superseding ADR) and DECISIONS-0001. Agents MUST NOT silently add
   columns to the accepted MVP set.

### Relation to proposed.7

This ADR **accepts the composite direction** and **tightens** proposed.7:

| proposed.7 | This ADR |
|---|---|
| `RiskScore = M(Impact, Feasibility)` | Keep M(·) as the **derived Risk** field; **add Mitigation status** as a peer MVP component |
| Path-level 4-point feasibility; human-rated; no CVSS at MVP | Same; UI emphasizes **CC-style** presentation (numbers + label + color) |
| Per-category S/F/O/P impact | Same (or project's damage model) |
| MitigationInstance visible in MVP demo | Elevated into the **risk vector** for tabular rows |

Update `ARCH-0001-PROPOSAL` / ARCH §6 language to point here when the acceptance PR lands.

## How agents find this decision

Claude / coding agents should treat the following trio as the discovery path (same
governance as other accepted DECs):

1. **Canonical ADR in the repo** — `spec/ADR-0005-composite-risk-vector.md` (this file,
   once merged). Search `DEC-003` or `ADR-0005`.
2. **`project/DECISIONS-0001.md`** — row **DEC-003** status = **`accepted → ADR-0005`**
   (not merely proposed). The register tracks; it does not accept.
3. **Tracking GitHub issue** — the accept / land issue created from
   `ISSUE-DEC-003-accept.md` (link the issue number here after create). Cross-link
   Path A epic [#47](https://github.com/Threat-Radar/tmodel/issues/47) and I-App
   Slice 1 (tabular / feasibility column).

Also: ARCH-0001 §8 DEC-003 row must point at this ADR; `ARCH-0001-CHANGELOG.md` gets a
line; only an `ADR-NNNN` accepts a `DEC-*` (ARCH §9).

## Consequences

- **Schema / KG:** Risk-related fields on AttackPath / ThreatInstance / RiskScore carry
  the vector components (feasibility, impact categories, mitigation status, derived risk).
  Do not collapse the model to one float.
- **Path A / I-App tabular slice (Slice 1, T-201):** include a **feasibility column**
  (numbers + label + color) plus impact / mitigation / derived risk as the table matures.
  Link work under epic [#47](https://github.com/Threat-Radar/tmodel/issues/47).
- **R-011…R-013:** satisfied in direction — composite covering CC-style feasibility and
  21434-shaped impact; CVSS remains optional post-MVP refinement, not MVP SoT.
- **RPT-0007 / PR #69:** remains evidence; human DEC-003 sign-off is this ADR. Remap
  §5/§6 after `proposed.8` (#66) if needed — do not treat the research PR as acceptance.
- **Still open:** exact aggregation function for derived Risk; precise CC factor set vs
  21434 Table-1 label mapping; DEC-009 mitigation lifecycle detail; post-MVP CVSS /
  per-step feasibility aggregation (proposed.7).

## Scope guard

- Implemented / documented only in **Threat-Radar/tmodel** — not `m-of-n/library` or
  `tradar`.
- **Do not invent more vector components** without Paul.
- Does **not** accept DEC-001, DEC-004, or DEC-009.
- Does **not** authorize committing ISO standard verbatim text.
