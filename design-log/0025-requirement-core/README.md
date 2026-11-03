---
schema: "archdoc/v1"
id: DL-0025
title: "Requirement in the core object model (ADR-0012)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-26"
updated: "2026-10-26"
record: DL-0025
bears_on: [DEC-001, DEC-009, R-042, R-044]
defers_to: ARCH-0001
---

# DL-0025 — Requirement in the core object model

This is an AI-assisted design record (per `CLAUDE.md`), drafted by Grok Bot for the sponsor (@nymble). It produced ADR-0012 and the schema, vector and checker changes listed below. Issue: #166.

## Question asked

The sponsor decided on 2026-10-26 (paraphrased): move Requirement into the core model. Requirements also relate to mitigations. A mitigation can be generic for a product type or family, and it then becomes a requirement, which may be technical, process, audit or another kind. Update the decisions and schemas in one complete change so requirements are part of the graph.

The brief asked for:
- a kind enum;
- a source link to the library record and its clause;
- requirement-to-requirement edges;
- edges to ThreatInstance, Weakness and AttackPattern;
- `satisfied_by` a Mitigation;
- product, component and family scope;
- a Mitigation→Requirement relation;
- AI-proposed links kept as `proposed` Assertions.

## What was produced

- `spec/ADR-0012-requirement-in-core.md`. It amends ADR-0010 (DEC-001a) and narrows DEC-001b.
- `spec/schema/tmodel-object-model.linkml.yaml`:
  - Requirement is rewritten as a core class.
  - New slots: `text_origin`, `requirement_kind`, `source_locator`, `refines`, `derived_from`, `conflicts_with`, `addresses` (any_of), `applies_to` (any_of), `applies_to_family`, and `Mitigation.stated_as`.
  - `Product` now takes `classifications`.
  - New enums: `RequirementKind` and `RequirementTextOrigin`.
  - `conformance_status` is re-labelled as proposed (DEC-001b).
- `spec/schema/generated/*`, regenerated with `bin/gen-schema`.
- `spec/schema/OBJECT-MODEL.md`, re-rendered. The renderer (`render_object_model.py`) now draws `any_of` ranges as one edge per allowed class.
- `spec/vectors/example-container-core.linkml.yaml` gains a `requirements` collection.
- `spec/vectors/mvp-02-automotive-ecu.yaml` gains five requirements, one generic family mitigation and one AI-proposed requirement Assertion.
- `design-log/0021-…/check-edges.py` now checks the eight requirement edges. It also fails a core vector that sets `conformance_status`.
- Status text updated to match: ARCH-0001 (0.1.9) and its changelog, DECISIONS-0001, SOW-0001, BACKLOG-0001 (T-224), APP-0001 §7, `spec/schema/README.md`, and `spec/vectors/README.md`.

## Options considered (and what was rejected)

1. **Family scope.**
   - Rejected: a new `ProductFamily` class. It would decide DEC-009 by accident.
   - Rejected: reusing `SecurityProgram.governs`. That slot belongs to DEC-001b.
   - **Chosen:** `applies_to_family`, an opaque string matched against `Product.classifications`. It reuses an existing slot and adds no class.
2. **Mitigation → Requirement.**
   - Rejected: Assertion-only reification. It is heavy for routine authored links and makes every coverage query go through Assertions.
   - Rejected: a `Requirement.derived_from_mitigation` edge. It points the wrong way for the authoring flow (you write the generic mitigation, then state it as a requirement), and it would overload `derived_from`.
   - **Chosen:** a direct `Mitigation.stated_as` edge for human-authored or reviewed links. AI-proposed links are `proposed` Assertions with predicate `stated_as`.
3. **Edges to several target types.**
   - Rejected: three typed slots each (`addresses_threat`, `addresses_weakness`, …).
   - **Chosen:** one `any_of` slot each. All three generators accept it with LinkML 1.12.1; SHACL gets `sh:or` over classes.
4. **Overlap edge.**
   - Rejected: a new `overlaps_with` slot. It would duplicate `maps_to` and break `tv-software-auth-service.yaml`.
   - **Chosen:** keep `maps_to`, re-described as the overlap/crosswalk edge.
5. **`conformance_status`.**
   - Rejected: dropping it. The governed `tv-*` vectors use it.
   - Rejected: accepting it. Blocker C1 is still open.
   - **Chosen:** keep the slot on Requirement, re-labelled as proposed (DEC-001b), and enforce "not in core vectors" in the reference checker.
6. **ETSI EN 304 223 in a vector.** Deferred. mvp-02 has no AI component, and the `etsi-en-304-223` library record is in an open student PR (library#32). The extraction issues route it to the AI-threat lane instead.

## How it was checked

- `bin/gen-schema --check`: up to date.
- `linkml-validate`: all four `mvp-*` vectors pass against `ExampleModelCore` and both `tv-*` vectors pass against `ExampleModel`. A bad `requirement_kind` value is rejected.
- `check-edges.py`: 4 vectors, 196 objects and 298 references, all resolve. Mutation tests catch a dangling `satisfied_by` and a `conformance_status` in a core vector.
- Engine: `pytest` 100 passed. The engine loader ignores collections it does not read, so no engine change was needed.
- `bin/validate-archdoc`: 0 errors.

## What a human accepted or rejected

The sponsor made the decision. The two design choices above (family scope by classification, and `stated_as` as a direct edge) are **flagged for sponsor review on the PR**. Change them before merge if they are not wanted. The mvp-02 requirements paraphrase ISO/SAE 21434; their clause ids come from the library's `iso-sae-21434-2021` extraction, and no reviewer has yet checked them against the standard.
