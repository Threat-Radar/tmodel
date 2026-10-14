---
schema: "archdoc/v1"
id: DL-0018
title: "Fold §3c SDL/governance objects into the §13 LinkML draft as named first-class types"
type: process
status: draft
version: "0.1.0"
date: "2026-10-09"
updated: "2026-10-09"
record: DL-0018
bears_on: [R-041, R-042, R-043, R-044, DEC-001, DEC-002]
defers_to: ARCH-0001
---

# DL-0018 — governed, versioned, human-reviewed, program-managed objects

AI-assisted design record for #15 (per `CLAUDE.md`). Extends the DRAFT object model
(`spec/schema/tmodel-object-model.linkml.yaml`, the DEC-001 proposal vehicle) with the §3c
SDL/governance objects, promoting R-041…R-044 from post-MVP *prose* to *named first-class types*.
**Proposal only: DEC-001 stays OPEN; nothing accepted; ARCH-0001 §8 untouched.**

## Question asked

Model, as first-class LinkML objects, the **versioned, human-reviewed, program-managed** nature of a
threat model and an SDL — grounded in ARCH-0001 §3c ("a threat model and an SDL are both iterating,
approvable views over the KG-as-SoT", R-040…R-044), DL-0009, DL-0012, and RPT-0013-OM. Invent nothing
structural the proposal/research does not already call for.

## What was produced

Extended the existing draft (did **not** fork a parallel schema):

- **8 classes** — `ThreatModel`, `SecurityProgram`, abstract `ProgramNode` → `Gate` / `Milestone` /
  `Checkpoint`, `Requirement`, `GovernedView` (`is_a` the §10 `View`).
- **~34 slots** — the shared governed-view facet (`owner`, `revision`, `approved_by`,
  `approval_digest`, `approval_status`, `governance_status`, `supersedes`, `created`, `updated`);
  ThreatModel scope (`scope_query`, `members`); program fields (`governs`, `program_nodes`,
  `incorporates`, `order`, `planned_date`, `actual_date`, `gate_status`, `at_phase`, `gated_by`,
  `decided_by`, `depends_on_node`, `validates_conformance_of`, `offset_from`); Requirement
  (`text`, `normativity`, `source_ref`, `maps_to`, `satisfied_by`, `conformance_status`); `renders`.
- **5 enums** — `GateStatus`, `ThreatModelStatus`, `ApprovalStatus`, `RequirementConformanceStatus`,
  `Normativity`.
- Promoted §3c (R-041…R-044) to name the classes; bumped `ARCH-0001-PROPOSAL` **proposed.12 →
  proposed.13** with `updated` (CI couples them); regenerated `spec/schema/OBJECT-MODEL.md`.

### How the semantics are modeled

- **Versioned.** Every governed artifact carries `revision` and `supersedes` (self-type via
  `slot_usage`), so revisions chain across review cycles; `created`/`updated` track change.
- **Human-reviewed / approved.** Approval runs through the existing **`Review` + `Assertion`
  spine** (§4) via `approved_by` → `Review`; no parallel provenance mechanism. `approval_digest`
  pins the sign-off to a commit/content digest so it is **reproducible** against KG state at a point
  in time (§3c prior art: SysML v2 View/Viewpoint, OMG SACM, OSCAL).
- **Program-managed.** `SecurityProgram` holds ordered `program_nodes`; each `Gate`/`Milestone`/
  `Checkpoint` carries `order`, planned vs actual dates, `gate_status`, `owner`, `at_phase`
  (mapped onto the §3b LifecyclePhase axis), `gated_by` Requirements and `decided_by` Reviews.
- **Conformance.** `Gate.validates_conformance_of` → `ThreatModel`; `Requirement.satisfied_by`
  Mitigation(s) + `conformance_status`. The check proves **linkage + approval, NOT adequacy**.
- **Governed vs transient view.** `GovernedView is_a View`: the existing `View` stays the transient
  lens; `GovernedView` is the tracked, owned, approved snapshot. `ThreatModel`/`SecurityProgram`
  carry the same governance facet, so they are governed views too.

## Accepted (and why)

- **Reuse the Party/Review/Assertion/LifecyclePhase/View spine.** `owner` is a **`Party` role**
  (§2b), not a new actor type; approval is a `Review`; gates map onto `LifecyclePhase`; `GovernedView`
  subtypes `View`. Honors the iteration-7 critic (DL-0010) guardrails.
- **Opaque `source_ref` (uriorcurie) to the library requirement record.** tmodel → library by
  reference ONLY; the LinkML does **not** `import` the library schema (Threat-Radar/library PR #16),
  honoring ADR-0004 substrate-neutrality and the no-dependency constraint.
- **Abstract `ProgramNode`** parent for the three program nodes — mirrors how `Node` factors shared
  identity; the three share `order`/dates/status/owner/phase/gating. Grounded in RPT-0013-OM
  (Gate/Milestone/Checkpoint, order, planned/actual dates).
- **Single `revision` slot** serves ThreatModel's `revision` and GovernedView's "version" (one
  concept, one slot) rather than minting two names for the same thing — the more conservative choice.
- **`approval_status` vs `governance_status`** kept distinct: the review-cycle verdict vs the
  snapshot's lifecycle (DL-0009 Q4: "iterating views of *status and approvals*").

## Rejected / deferred (and why)

- **The other ~40 RPT-0013-OM objects** — `Evidence`, `ConformanceAssessment`/`ConformanceResult`,
  `Attestation`, `SBOM`, `RequirementSource`, `CrosswalkMapping`, `AssuranceLevel`/`MaturityLevel`,
  `Exception`, `VulnerabilityHandlingPolicy`, `SecurityRiskAssessment`, `ActionPlan`,
  `SourceRepository`, etc. **Not added**: out of this cut's scope (the five object families the fold
  names). Evidence is referenced only in prose via `Mitigation.external_refs` + the approving
  `Review`; a dedicated `Evidence`/`WorkProduct` class remains the #19 audit model's call.
- **A LinkML `mixin`** for the shared governance facet — rejected: `render_object_model.py` does not
  expand mixins (or `is_a`-inherited slots), so a mixin would hide the governance slots from the
  rendered per-class tables. Instead the slots are listed on each governed class (house style — cf.
  `owned_by`, `applies_in_phase` reused across classes), so they render and draw correctly.
- **Tightening the existing `Review.review_status`** to an enum — left as the deliberately-open
  string it already is; `ApprovalStatus` lives on the governed artifact as a denormalized read.
- **Any DEC acceptance or ARCH-0001 §8 edit** — out of scope by instruction and `CLAUDE.md`.

## Gate

`bin/validate-archdoc` clean; `python3 spec/schema/render_object_model.py` runs (30 classes, 14
enums); the LinkML parses under `yaml.safe_load`. DEC-001 remains OPEN.

## Next

A fresh adversarial-critic pass on proposed.13 before any ADR; the SDL guideline library records
finish FX-1 verify (RPT-0013/#67); DEC-001 accepts last, folding this into ARCH-0001 §3/§4.
