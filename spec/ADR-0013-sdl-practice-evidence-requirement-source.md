---
schema: "archdoc/v1"
id: ADR-0013
title: "Object model — SDL practices, evidence and requirement sources (accepts part of DEC-001b; amends ADR-0010 / ADR-0012)"
short_title: "SDL classes (DEC-001b, part)"
description: "Sponsor decision (2026-11-07): three program-layer classes join the object model for a product's secure development lifecycle, under the RPT-0013-OM names. SdlPractice is one SDL activity keyed to a MAP-0001 row; RPT-0013-OM has no practice type, so it keeps its name. Evidence is a deliverable or evidence item (MVP subset of RPT-0013-OM Evidence). RequirementSource is a governing body of requirements (RPT-0013-OM RequirementSource). Selection of practices, requirement sources and milestone names stays on the Assertion + Review spine, decided by the sponsor (PROC-0002). The rest of DEC-001b stays open."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-11-07"
updated: "2026-11-07"
decision_makers:
  - role: sponsor
    id: nymble
reviewers:
  - role: sponsor
    id: nymble
    kind: human
  - role: schema-review
    id: Maimcghee
    kind: human
  - role: drafting-agent
    id: grok-bot
    kind: ai_agent
needs_review: false
reviewed: true
canonical_path: spec/ADR-0013-sdl-practice-evidence-requirement-source.md
accepts: DEC-001b (part)
amends: [ADR-0010, ADR-0012]
defers_to: ARCH-0001
---

# ADR-0013 — SDL practices, evidence and requirement sources

**Status: accepted (2026-11-07) on merge.** Decided by @nymble. It accepts **part of DEC-001b**:
the three classes below. The rest of DEC-001b stays open, including ThreatModel,
SecurityProgram/Gate/Milestone/Checkpoint, GovernedView and RedundancyGroup, and the DL-0020
blockers C1, C2 and M1 to M5. Design records: DL-0040 (the example) and DL-0041 (this decision).

## Review

| date | who | kind | verdict |
|---|---|---|---|
| 2026-11-07 | drafting agent | ai_agent | drafted as Proposed (DL-0041), with the DL-0040 names |
| 2026-11-07 | @nymble (sponsor) | human | **accepted, with the RPT-0013-OM names**. Paraphrase of the decision: accept the ADR and use the research report's names. |

@Maimcghee was asked for a schema review. The decision did not wait for it, so that review is
welcome after the fact as a follow-up issue.

## Context

- ADR-0010 accepted the core attack-path type system and held the governed/program layer open as
  DEC-001b. ADR-0012 moved `Requirement` into the core.
- The program layer had no class for **what the team does** (a practice), **what that produces**
  (evidence) or **which body of requirements governs the product**. DL-0040 needed all three to
  model the tmodel app's own SDL (`spec/vectors/sdl-01-tmodel-desktop.yaml`).
- RPT-0013-OM (46 canonical SDL object types) has `Evidence` and `RequirementSource`, and no
  canonical Activity or Practice type. MAP-0001 has 34 practice rows across 16 frameworks.

## Decision

Three classes are added to `spec/schema/tmodel-object-model.linkml.yaml`. Each description starts
"Accepted via ADR-0013".

| class (`is_a: Node`) | slots | from |
|---|---|---|
| `SdlPractice` | `practice_key` (a MAP-0001 row), `at_phase` → LifecyclePhase, `owner` → Party, `mitigation_status`, `implements` → Requirement \*, `produces` → Evidence \*, `in_program_node` → ProgramNode \*, `external_refs` | RPT-0013-OM has no practice type, so the DL-0040 name is kept. MAP-0001 is the practice catalogue. |
| `Evidence` | `locator`, `evidence_kind` (EvidenceKind), `evidence_nature` {work_product, by_product}, `digest`, `about_version`, `fresh_until`, `evidence` | MVP subset of RPT-0013-OM `Evidence`. Retention, disclosure tier and `gathered_by` are deferred. |
| `RequirementSource` | `source_ref` (library record), `source_locator`, `version` (edition), `source_members` → Requirement \*, `applies_to_family` | RPT-0013-OM `RequirementSource`. The tailored per-product `RequirementProfile` is deferred. |

**Selection is not a field.** These are Assertions about the `SecurityProgram`. Each is `proposed`
until the sponsor's Review decides it (PROC-0002):

| predicate | object | meaning |
|---|---|---|
| `selects_requirement_source` | RequirementSource | this source governs the product |
| `considers_requirement_source` | RequirementSource | candidate, not yet decided |
| `excludes_requirement_source` | RequirementSource | ruled out; rationale in `description` |
| `selects_practice` | SdlPractice | the practice is a delivery item |
| `proposes_milestone_name` | Milestone / Gate | the node's `name` is the proposed name |

## Amendments

- **ADR-0010.** `SdlPractice`, `Evidence` and `RequirementSource` leave the "held open" set: they
  are accepted program-layer classes. The other DEC-001b classes and blockers are unchanged.
- **ADR-0012.** `Requirement` stays core. `RequirementSource.source_members` and
  `SdlPractice.implements` point into it. No core slot changes.
- The DL-0041 proposal module `spec/schema/proposals/sdl-dec-001b.linkml.yaml` is folded into the
  main file and deleted. `bin/gen-schema` regenerates `generated/`, and `OBJECT-MODEL.md` is
  re-rendered.

## Alternatives considered

1. **Status or `selected` fields.** Rejected: an AI-drafted selection would look decided.
2. **The DL-0040 names (`WorkProduct`, `RequirementSet`).** Rejected by the sponsor in favour of
   the research names.
3. **No practice class (reuse Mitigation or Requirement).** Rejected. A practice is something a
   team does at a phase, with an owner and outputs.

## Consequences

- SDL models validate against `spec/vectors/example-container-sdl.linkml.yaml`, which now imports
  only the object model.
- The engine (`GET /sdl`) and the app read these classes as accepted classes. Every *selection*
  is still a proposal until reviewed.
- `Assertion.evidence` (a slot) and `Evidence` (a class) share a word. They are different things:
  the slot is an opaque reference on an Assertion.

## Validation (2026-11-07)

Pinned `linkml-validate` 1.12.1 reports no issues on sdl-01 (`ExampleModelSdl`), mvp-\*
(`ExampleModelCore`), tv-\* (`ExampleModel`) and pv-\* (`ExampleModelProposed`).
`bin/gen-schema --check` passes after regenerating.
