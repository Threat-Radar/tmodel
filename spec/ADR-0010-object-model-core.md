---
schema: "archdoc/v1"
id: ADR-0010
title: "Object model — accept the CORE attack-path type system (DEC-001a); hold the governed/program layer (DEC-001b)"
short_title: "Object model core (DEC-001a)"
description: "Splits DEC-001 and accepts DEC-001a: the core attack-path knowledge-graph type system (Node, Product/ProductInstance/Component, Party, Weakness/Vulnerability/AttackPattern, ThreatInstance/AttackStep/AttackPath, DamageScenario, Mitigation, RiskScore/ImpactVector, Review/Assertion, Deployment/Environment/LifecyclePhase, View, the identifiers slot, and the core enums). The governed/program layer (ThreatModel, SecurityProgram/Gate/Milestone/Checkpoint, Requirement, GovernedView, RedundancyGroup) is held OPEN as DEC-001b pending the proposed.14 critique fixes. Encoding (DEC-002), substrate (DEC-004) already accepted; this accepts the logical type system only."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-12"
updated: "2026-10-12"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0010-object-model-core.md
accepts: DEC-001a
defers_to: ARCH-0001
---

# ADR-0010 — Object model: accept the core (DEC-001a)

**Status: accepted (2026-10-12). Splits DEC-001; accepts DEC-001a; holds DEC-001b.** The object
model has been developed as a proposal through `ARCH-0001-PROPOSAL` (iterations 1–8, proposed.14)
and dogfooded by worked example threat models. A fresh adversarial critic (DL-0020) found the
**core attack-path type system sound and ADR-ready**, but the **governed/program layer not yet
mechanized**. The sponsor's call: accept the core now, hold the governed layer.

## Context

- `ARCH-0001` §8 kept **DEC-001** (the core object model) open; §3 says "names are working labels;
  DEC-001 ratifies the model." The LinkML draft (`spec/schema/tmodel-object-model.linkml.yaml`,
  `proposes: DEC-001`) carries 30 classes.
- The Nov-5 MVP (ADR-0002) is a **reviewed attack-path graph over multiple products in ≥2 domains** —
  the *core* type system, no governance.
- The proposed.14 adversarial critique (DL-0020) verified the schema is valid LinkML (ran
  `linkml-validate` + `gen-json-schema` + mutation tests) and recommended **ACCEPT-CORE-NOW**: the
  core is close to ready; the governed layer's three reasons to exist (reproducible approval,
  automatable conformance, human sign-off) are *named but not mechanized*.

## Decision (DEC-001a)

**Accept the CORE attack-path type system** as the logical object model — the first-class types and
typed relations the MVP builds on. Accepted classes:

`Node` (abstract id), `Product`, `ProductInstance`, `Component`, `Party`, `Weakness`,
`Vulnerability`, `AttackPattern`, `ThreatInstance`, `AttackStep`, `AttackPath`, `DamageScenario`,
`Mitigation`, `RiskScore`, `ImpactVector`, `Review`, `Assertion`, `Deployment`, `Environment`,
`LifecyclePhase`, `View` — plus the opaque multivalued `identifiers` slot (purl/CPE/SBOM/firmware
digest; ADR-0002 per-type instance identity) and the core enums (`PartyKind`, `MethodFacet`,
`AttackGate`, `FeasibilityLevel`, `ImpactSeverity`, `MitigationStatus`, `LifecyclePhaseCode`,
`ViewProjection`).

This is the type system only. It defers to the already-accepted encoding/substrate decisions:
**ADR-0007** (LinkML canonical IDL), **ADR-0004** (file SoT, stable ids, typed edges), **ADR-0006**
(composite `RiskScore`). AND/OR attack structure, vuln propagation along composition, the reified
`Assertion` provenance spine, and the human-reviewed-vs-AI-proposed distinction (`Review`/`Assertion`,
never present AI output as reviewed) are all part of the accepted core.

**Evidence:** the worked example threat models `spec/vectors/tv-software-auth-service.yaml` and
`tv-hardware-brake-ecu.yaml` validate against the schema; the **§8 MVP core interop vectors**
(`spec/vectors/mvp-*`) are the companion acceptance set.

## Held OPEN as DEC-001b (the governed / program layer)

**Not accepted.** `ThreatModel`, `SecurityProgram`, `ProgramNode`, `Gate`, `Milestone`,
`Checkpoint`, `Requirement`, `GovernedView`, and `RedundancyGroup` (post-MVP) remain **proposal-level**
until the DL-0020 blockers are resolved and a follow-up ADR accepts them:

- **C1** — automatable conformance needs a `Mitigation`→`Review` (approved+evidenced) edge; today
  `Review.reviews` only ranges on `Assertion`, so the verdict is hand-set (and one vector set it wrong).
- **C2** — `approval_digest` has no defined binding/canonicalization; "reproducible approval" is undefined.
- **M1** — governed/program edges are `range: Node` + reference-only, unchecked by `linkml-validate`
  (mutation-proven); needs a hand-written referential + reviewed-Assertion integrity gate (§13).
- **M2** — the governance facet is hand-copied across three classes because the renderer can't expand
  `is_a`/mixins; needs a `GovernedArtifact` mixin + a renderer fix.
- **M4** — `GovernedView` and `Checkpoint` are never instantiated; exercise or drop.
- **M5** — governed artifacts have an approver (`owner`) but no author/origin; AI-authored artifacts
  aren't readable as such (DEC-002 provenance territory).

## Consequences

- Flips **DEC-001a** to accepted; `ARCH-0001` §3/§8 point here for the core. DEC-001b, DEC-008,
  DEC-009 remain open.
- `APP-0001` A-001…A-007 (ingest, propagate, graph, review, chains, risk, provenance) now build on an
  accepted type system; I2/I3 implement against it.
- The LinkML file stays one file; its header marks the core as accepted (DEC-001a) and the
  governed classes as still proposing DEC-001b. Working-label names in `ARCH-0001` §3 are superseded
  by the accepted class names for the core.
- Does **not** accept encoding beyond ADR-0007, nor the governed layer; no SHACL/gate code is accepted
  here (the §13 integrity checker is still to be built).

## Scope guard

Implemented only in **Threat-Radar/tmodel**. This accepts the logical type system, not a UI, not the
governed/program subsystem, not DEC-002 interchange beyond ADR-0007. No DEC-001b class may be treated
as accepted until its follow-up ADR. The `~/cb` harness is unaffected.
