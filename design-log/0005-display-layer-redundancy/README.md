---
schema: "archdoc/v1"
id: DL-0005
title: "Sponsor review (display layer + redundancy) → folded into iteration 4"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0005
---

# DL-0005 — Sponsor review: display layer + redundancy

AI-assisted design record for #15 (per `CLAUDE.md`). A sponsor review round on
`ARCH-0001-PROPOSAL-v0.2.0` (iteration 4, merged in #45). Folded in place into the
same proposal (`proposed.4` → `proposed.5`, §10), not a new iteration — the sponsor
asked to "fold into #45".

## Questions asked

1. **Display of information & associations.** How do we support graphical display and
   the associations between objects? Is there a **display layer or set of (perhaps
   transient) objects** that drive an interactive display?
2. **At scale.** With a large number of interconnected objects: can we **progressively
   load**? Can we treat **objects or tags as layers** for incorporation? Can we support
   **dynamic display behaviour** — physics, unique colours, click-to-open containment or
   object info?
3. **Robustness — redundant systems.** Is the model robust enough to model **redundant
   build systems**? Concretely: show the threats + mitigations of an **AI code-review
   running on a secure server in two distinct locations**, then **compare** results.
4. **Where do application requirements live?** (→ spun out, see Accepted.)

## What was produced

Design comments, then folded into the proposal §10 and the §6 matrix:

- A **presentation/view layer** as a fifth, derived, UI-facing concern (§1.5, §10):
  `View`/`Perspective` specs (persisted or transient) + **transient rendered view-state**
  that is computed from the domain and never written back; a **separate visual object
  model** bound to the domain by reference. This answers "is there a display layer / set
  of transient objects" — yes, and it is derived, not domain truth.
- **Multiple projections over one graph** (graph, matrix, attack-path, DFD, timeline,
  provenance, compare) — the View picks one.
- **Progressive loading** (the View is a bounded query; expand-on-click, paged
  neighbourhoods, LOD collapse of `composed_of`), **layers/tags as composable overlays**,
  and **dynamic behaviour** (force physics, per-type/-facet colours, click-to-expand
  containment, click-to-inspect). Captured as **R-033**.
- **Redundancy as a relationship:** `RedundancyGroup`/`replica_of` (§3), enabling
  redundancy-as-mitigation, **common-mode risk** (shared `Component`/CWE defeats the
  redundancy), and per-replica divergence. Captured as **R-034**.
- **Compare/diff projection** over two subgraphs + provenance compare, which makes the
  two-location AI-code-review-compare scenario representable. Captured as **R-035**.

## Accepted → folded into iteration 4 (proposed.5)

- Presentation/view layer and R-033/034/035 added (§10); matrix (§6) and MVP table (§7)
  updated. **MVP = one interactive graph projection** (force layout, type colours,
  click-expand/inspect, progressive load); matrix/compare/saved-views/layers and
  redundancy are **post-MVP**.
- **Application (product) requirements spun out to `APP-0001`** — the object-model
  proposal is not the home for platform/GUI/performance/CLI/licensing requirements.
- **Stack/language made an explicit open decision, `DEC-010`**, to be settled by research
  **RPT-0012** (GUI, platform & implementation stack) — per the sponsor's "language
  choice to be driven by GUI and platform research".

## Rejected / adapted

- Nothing rejected. **Adapted the scope:** the display layer is powerful, but only a
  single interactive graph projection is in the MVP; everything else (compare, matrix,
  redundancy) is modelled but post-MVP, consistent with the F3 scope gate.
- Did **not** pick a language or UI stack here (that would pre-empt DEC-006/DEC-010); the
  code-options landscape is framed as research dimensions in RPT-0012, not a decision.

## Next

Iteration 5 (unchanged): fold research #6/#7/#9, decide reification (DEC-002/004) and the
risk metric (DEC-003), build MVP vectors, then accept DEC-001 via an ADR. In parallel,
RPT-0012 informs DEC-006/DEC-010 and APP-0001 hardens from `draft` once the research lands.
