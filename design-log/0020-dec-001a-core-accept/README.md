---
schema: "archdoc/v1"
id: DL-0020
title: "proposed.14 adversarial critique → split DEC-001, accept the core (DEC-001a)"
type: decision
status: accepted
version: "0.1.0"
date: "2026-10-12"
updated: "2026-10-12"
record: DL-0020
---

# DL-0020 — DEC-001 split & core acceptance

## Question asked

Sponsor: after the proposed.14 object-model fold (ThreatModel/SDL/Requirement/GovernedView +
example vectors, #116), run a **fresh adversarial-critic pass**, then decide. Sponsor chose
**accept the core now** (vs fix-governed-first / just-record).

## What the critic found (verified: it ran linkml-validate + gen-json-schema + 3 mutation tests)

- The schema is **structurally valid LinkML**; both example vectors validate.
- The **core attack-path type system is sound and ADR-ready.**
- The **governed/program layer is NOT ready** — its three reasons to exist are *named but not
  mechanized*, and the "2 vectors, 0 failures" evidence is shallower than it looks:
  - **C1** — automatable conformance ("approved + evidenced mitigation") is **unrepresentable**:
    `Review.reviews` ranges only on `Assertion`, never `Mitigation`; one vector hand-set a requirement
    `conformant` whose mitigation had no review/evidence.
  - **C2** — `approval_digest` is an opaque placeholder with **no defined binding/canonicalization**;
    "reproducible approval" is undefined.
  - **M1** — governed/program edges are `range: Node` + reference-only, so `linkml-validate` **never
    checks them** (the critic mutated an edge to a nonexistent id and to a wrong type — both passed).
    Needs a hand-written referential + reviewed-Assertion integrity gate (§13).
  - **M2** — the 9 governance slots are hand-copied across three classes because
    `render_object_model.py` can't expand `is_a`/mixins (also a pre-existing bug: it doesn't render
    inherited `id`/`name`/`description`). Needs a `GovernedArtifact` mixin + a renderer fix.
  - **M4** — `GovernedView` and `Checkpoint` are never instantiated; exercise or drop.
  - **M5** — governed artifacts have an approver (`owner`) but **no author/origin** → an AI-authored
    threat model/requirement isn't readable as such (DEC-002 provenance territory).
- Hygiene clean (no DEC pre-emption; DEC-001 was untouched); the DL-0010 guardrails and ADR-0004
  substrate-neutrality are correctly honored.

## Decision (accepted)

**Split DEC-001.** Accept **DEC-001a** (the core attack-path type system) via **ADR-0010**; hold
**DEC-001b** (the governed/program layer: ThreatModel, SecurityProgram/Gate/Milestone/Checkpoint,
Requirement, GovernedView, RedundancyGroup) **open** until C1/C2/M1/M2/M4/M5 are fixed and a
follow-up ADR accepts it. Matches the Nov-5 MVP (ADR-0002: a reviewed attack-path graph, no governance).

## Rejected / not now

- *Fix-governed-layer-first* and *just-record* (the other two sponsor options).
- Accepting all 30 classes at once — the critic's C3: that would silently swallow an unfinished
  governance subsystem into DEC-001.

## Next

- Fix the DEC-001b blockers (C1 conformance edge, C2 digest binding, M1 integrity gate, M2 mixin +
  renderer, M4, M5 — M5 ties to DEC-002 provenance / the #19 audit model), then a DEC-001b ADR.
- Build/complete the §8 MVP core interop vectors (companion to this acceptance).
- The renderer `is_a`/mixin expansion bug (M2) is worth fixing regardless (it under-renders OBJECT-MODEL.md).
