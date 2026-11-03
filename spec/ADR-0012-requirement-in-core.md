---
schema: "archdoc/v1"
id: ADR-0012
title: "Object model — move Requirement into the core (amends ADR-0010 / DEC-001a; narrows DEC-001b)"
short_title: "Requirement in the core (DEC-001a amendment)"
description: "Sponsor decision (2026-10-26): Requirement becomes a core class of the attack-path knowledge graph. It gains a kind (technical / process / audit / documentation / organizational / other), a text origin (paraphrase / verbatim / authored), a source clause locator, requirement-to-requirement edges (refines, derived_from, conflicts_with, maps_to = overlap), edges to what it addresses (ThreatInstance / Weakness / AttackPattern), satisfied_by Mitigation, and scope (applies_to Product / ProductInstance / Component, or applies_to_family matched against Product.classifications). A generic Mitigation for a product family is stated_as a Requirement. Requirement.conformance_status and the rest of the governed/program layer stay DEC-001b."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-26"
updated: "2026-10-26"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0012-requirement-in-core.md
accepts: DEC-001a
amends: ADR-0010
defers_to: ARCH-0001
---

# ADR-0012 — Requirement in the core object model

**Status: accepted on merge.** Issue: #166. Under the repo convention, a decision takes effect only once its ADR is on `main` (CLAUDE.md, CONTRIBUTING §5). This ADR amends **ADR-0010 / DEC-001a** by adding `Requirement` to the accepted core. It narrows **DEC-001b**, which keeps the rest of the governed/program layer open. Design record: `design-log/0025-requirement-core/`.

## Context

- ADR-0010 accepted the core attack-path type system and held `Requirement` in the governed/program layer (DEC-001b). There it was a normative `text`, a `normativity`, an opaque `source_ref`, `maps_to`, `satisfied_by` and the R-042 `conformance_status`.
- The MVP core vectors validate against `ExampleModelCore`, which had no `requirements` collection. So a core model could not say which obligation a mitigation discharges, or which standard a threat model answers to.
- **Sponsor decision (2026-10-26, @nymble), paraphrased:** move Requirement into the core model. Requirements are also related to mitigations. A mitigation can be generic for a product type or family, and that mitigation then becomes a requirement, which may be technical, process, audit or another kind. Update the decisions and schemas in one complete change so requirements are part of the graph.
- The library already extracts standards provisions as structured records. For example, `iso-sae-21434-2021` `distilled/requirements.yaml` gives each provision an id such as `iso-sae-21434-2021#RQ-09-09`. Several ISO/IEC/SAE sources are licensed, so tmodel may carry only a paraphrase plus a clause id.

## Decision

`Requirement` is a **core** class (`is_a: Node`, stable `id` per ADR-0004). It has these slots:

| slot | range | note |
|---|---|---|
| `text` | string | The statement. For a licensed standard it is **always a paraphrase**. |
| `text_origin` | `RequirementTextOrigin` {paraphrase, verbatim, authored} | Makes the licensing rule checkable. `verbatim` only where the source's licence allows. |
| `requirement_kind` | `RequirementKind` {technical, process, audit, documentation, organizational, other} | A mitigation that becomes a requirement can be any of these kinds. |
| `normativity` | `Normativity` (unchanged) | mandatory / recommended / optional / informative / conditional. |
| `source_ref` | uriorcurie, opaque | The library record (and provision), scheme-prefixed like `catalog_ref`, e.g. `library:iso-sae-21434-2021#RQ-09-09`. Reference only; no library schema is imported. |
| `source_locator` | string | The clause, section or table locator a reader uses to find the authoritative wording, e.g. `RQ-09-09 (§9.5.2)`. |
| `refines` | → Requirement * | Same intent, made more specific (narrower scope or more detail). |
| `derived_from` | → Requirement * | Derived from the target. The intent may differ (e.g. a family requirement derived from a standard's provision). |
| `conflicts_with` | → Requirement * | Both cannot be met as written; a human must resolve it. |
| `maps_to` | → Requirement * | **Overlap**, the MAP-0001 crosswalk (kept under its existing name). |
| `addresses` | → ThreatInstance \| Weakness \| AttackPattern * | What the requirement counters (`any_of`). |
| `satisfied_by` | → Mitigation * | The mitigation(s) that discharge it, normally product-specific. |
| `applies_to` | → Product \| ProductInstance \| Component * | Concrete scope (`any_of`). |
| `applies_to_family` | string * | Product type or family scope, matched against `Product.classifications`. |

The decision adds or changes three things outside the Requirement class:

- **`Mitigation.stated_as`** (→ Requirement \*) is a new edge.
- **`Product.classifications`** is the existing Party slot, now also allowed on Product. It holds the product types or families a product belongs to.
- Two enums are new: **`RequirementKind`** and **`RequirementTextOrigin`**.

**Not accepted here:** `Requirement.conformance_status` (the R-042 automated verdict). It stays a DEC-001b, proposal-level slot because it depends on blocker C1, the Mitigation→Review evidence edge. Core vectors must not set it, and the core reference checker (DL-0021 `check-edges.py`) fails a core vector that does. `SecurityProgram.incorporates` and `ProgramNode.gated_by` still point at Requirement from the governed side, so nothing there changes.

**Review rule (unchanged core rule, restated for requirements).** A requirement link that an AI proposes, whether `addresses`, `stated_as`, `maps_to`, `satisfied_by` or another, is a `proposed` **Assertion** (subject, predicate, object) with no Review. It is **not** a slot value until a human Review accepts it. Ingesting a standard's provisions is not reviewing them.

## Design choices

### 1. Product type/family scope: a classification, not a ProductFamily class

**Chosen:** `Requirement.applies_to_family` is an opaque scheme-prefixed string (e.g. `family:connected-ecu`). It matches the same value in `Product.classifications`. A family-scoped requirement applies to every Product carrying that classification.

**Why this is the least invasive option:**
- DEC-009 (generic threat → product / product family) is still open, and ARCH-0001 §3 lists "Product / ProductFamily" only as a working label. Adding a `ProductFamily` class would decide DEC-009's shape by accident.
- The classification reuses a slot that already exists on `Party` and follows the same opaque, scheme-prefixed pattern as `identifiers`, `catalog_ref` and `external_refs` (ADR-0004 substrate neutrality).
- No new class is added, and no existing slot is renamed or narrowed.

**Trade-offs:**
- (a) Family membership is a string match. It is not an edge, so the graph cannot hang properties (owner, version) on a family.
- (b) Typos are not caught by `linkml-validate`. A later lint or a `ProductFamily` class (DEC-009) can replace it.
- (c) `SecurityProgram.governs` (DEC-001b) still uses `range: Node` for families, so the two layers name families differently until DEC-009 is decided.

### 2. Mitigation → Requirement: a direct edge, with Assertion reification for proposed links

**Chosen:** a direct core edge, **`Mitigation.stated_as` → Requirement**. A generic family mitigation is restated as a Requirement that carries the family scope (`applies_to_family`) and a `requirement_kind`. Product-specific mitigations then discharge that Requirement through `Requirement.satisfied_by`. So the chain reads: generic Mitigation —stated_as→ Requirement —satisfied_by→ product Mitigation.

**Trade-offs:**
- **A direct edge (chosen)** is cheap to query: "which family requirements does product X not yet satisfy" is one hop each way. It validates with `linkml-validate` and the reference checker, and it matches how other authored core edges work (`mitigates`, `realizes_threat`).
- **Assertion-only reification (rejected as the only form)** would give every link provenance and a Review. But it would turn a routine authoring link into a three-node pattern and make every coverage query go through Assertions.
- **The rule we keep:** a human-authored or reviewed link is a slot value. An AI-proposed or still-disputed link is a `proposed` Assertion with predicate `stated_as`, until a Review accepts it and the value is written. This is the same split the core already uses for `realizes_threat` and CWE↔CAPEC.

### 3. `addresses` and `applies_to` use `any_of`

There is one slot each, with an `any_of` class range. This avoids three near-duplicate slots. The generated JSON Schema, SHACL (`sh:or` over classes) and pydantic types all accept it with the pinned LinkML 1.12.1 tools. The `OBJECT-MODEL.md` renderer now draws one edge per allowed class.

### 4. Licensed text

The schema cannot detect copied text, so the rule is carried in three places:
- `text_origin` names where the text came from;
- `source_locator` points to the authoritative clause;
- the slot description says that licensed ISO/IEC/SAE text is paraphrased.

The worked vector uses paraphrase plus clause id for ISO/SAE 21434.

## Evidence

- `spec/vectors/mvp-02-automotive-ecu.yaml` (core, `ExampleModelCore`) now carries five Requirements:
  - three ISO/SAE 21434 provisions, paraphrased with clause ids: RQ-09-09 (process), RQ-08-07 (process) and RQ-05-17 (audit);
  - a family requirement for `family:connected-ecu`, which the generic mitigation is `stated_as`, `derived_from` RQ-09-09, and which `addresses` CWE-306 and CAPEC-115;
  - a TCU requirement that `refines` the family requirement and `addresses` the threat.

  Both product-level requirements are `satisfied_by` the TCU's own mitigation. One AI-proposed `addresses` link stays a `proposed` Assertion with no Review.
- Checks run:
  - `linkml-validate` on all `mvp-*` (core) and `tv-*` (full) vectors;
  - `bin/gen-schema --check`;
  - `check-edges.py`, which now covers the requirement edges and rejects `conformance_status` in a core vector; both mutation-tested;
  - engine tests (100 passed).

## Consequences

- **DEC-001a** is amended by this ADR. `ARCH-0001` §3/§8, `DECISIONS-0001` and the schema header point here.
- **DEC-001b** is narrowed. It still holds ThreatModel, SecurityProgram/Gate/Milestone/Checkpoint, GovernedView, RedundancyGroup and `Requirement.conformance_status`, with blockers C1, C2, M1, M2, M4 and M5 unchanged.
- **DEC-009** stays open. It now has a core Requirement and a family-scope hook to build on, and it may later replace `applies_to_family` with a ProductFamily class.
- `ExampleModelCore` gains a `requirements` collection.
- The library standards records need a requirement-extraction pass to feed this class. That pass is tracked as student-lane issues: ingesting is not reviewing, and links stay `proposed`.
- **Coordination:** open PR #130 (a separate DEC-001a amendment, numbered ADR-0011 on its branch) also edits the schema, the generated files, `OBJECT-MODEL.md` and ARCH-0001. The two changes are additive and touch different classes. Whichever merges second regenerates (`bin/gen-schema`, `render_object_model.py`) and resolves the ARCH-0001 status lines.

## Scope guard

This applies only to **Threat-Radar/tmodel** and accepts the logical type only. It does not accept:
- the conformance check (R-042),
- any governed artifact,
- an import mapping from the library's requirement format (DEC-002 / #9),
- a ProductFamily class.
