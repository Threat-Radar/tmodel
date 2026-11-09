---
schema: "archdoc/v1"
id: DL-0024
title: "Schema proposal: composition slots (RPT-0004 Table 6) and Asset, TrustBoundary, DataFlow (RPT-0005 G13)"
type: process
status: draft
version: "0.3.1"
date: "2026-10-18"
updated: "2026-10-29"
record: DL-0024
bears_on: [R-002, R-010, R-018, R-022, DEC-001, DEC-002, DEC-008, DEC-009]
defers_to: ARCH-0001
---

# DL-0024: schema proposal, composition slots and the G13 classes

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, working with Claude Code, taking this piece of #64 off @Maimcghee's plate (announced on #64). **It proposed; ADR-0011 accepted it** on 2026-10-22 (see "Decisions (2026-10-22)" below). Every new element's description now starts "Accepted via ADR-0011 (DL-0024)".

## Question asked

Two findings route to the schema lane (#64):

- **RPT-0004 Table 6** (#127, `research/0004-product-composition/mapping.md` §3) found composition facts the accepted core cannot hold: per-build composition, a version, a component kind, the CVE-to-CWE edge, and who made an Assertion and when.
- **RPT-0005 G13** (#126): the committed OTM import (ADR-0007) needs Asset, TrustBoundary and DataFlow, which the accepted core lacks. The sponsor's direction, 2026-10-14 (DL-0013): add them, shaped by iterative example models of published automotive attacks (stealing a car; stealing owners' private data).

The student asked for a tested proposal the lane owner and the sponsor only need to review and decide.

## What is proposed

All changes are additive and optional. No slot is renamed, removed or narrowed, and the six existing vectors validate unchanged.

**Part A, composition (RPT-0004 Table 6)**

| # | Change | Evidence |
|---|---|---|
| A1 | `Vulnerability.instance_of` (range Weakness): the CVE-to-CWE edge | mapping.md findings 4 and 7; ARCH-0001 §3 and PLAN-0002 §5 name the edge `instance_of` |
| A2 | `version` on ProductInstance and Component | Table 6b; until now only the purl inside `identifiers` held it |
| A3 | `Component.component_kind` and enum `ComponentKind` (CycloneDX 1.7's 13 types, plus `service` and `interconnect`) | Table 6b and 6e; R-022 |
| A4 | `ProductInstance.build_composed_of` (range Component): the per-build list an SBOM gives | pilot finding 1; rule R-MERGE-1 |
| A5 | Assertion provenance: `asserted_by` (Party), `asserted_at`, `generated_by`, `evidence`; PartyKind `software_agent` | mapping.md finding 5; DL-0021 findings 4 and 5; RPT-0015 §4 |
| A6 | `Vulnerability.alias_ids` (GHSA, OSV, distribution ids) | Table 6d; `catalog_ref` is single-valued |
| A7 | `supplied_by` and `manufactured_by` on Component | Table 6c and 6e; DL-0021 finding 3 |

**Part B, the G13 classes (sponsor direction)**

| # | Change | Shaped by |
|---|---|---|
| B1 | class `Asset` (`security_properties`, `stored_in`, `processed_by`, `owned_by`) and enum `SecurityProperty` | ISO/SAE 21434 asset and cybersecurity property, as RPT-0007 paraphrases them; OTM `assets`; both example models |
| B2 | class `TrustBoundary` as a zone (`within_boundary`, `trust_level`), with `Component.in_trust_zone` | the proposal's §1 ("a **zone**: `in_trust_zone`"); OTM `trustZones`; both example models |
| B3 | class `DataFlow` (`flow_from`, `flow_to`, `carries`, `protocol`, `bidirectional`, `crosses_boundary`) | OTM `dataflows`; both example models |
| B4 | `DamageScenario.damages_asset`, `compromised_property` (DamageScenario had no slots) | ISO/SAE 21434 damage scenario; RPT-0015 §4 |
| B5 | `ThreatInstance.targets_element` (a Component, DataFlow, Asset or TrustBoundary) | OTM attaches threats to components and flows; RPT-0015 §4 |

Also produced: `spec/vectors/example-container-proposed.linkml.yaml` (the core container plus the three new collections); the example models `spec/vectors/pv-01-can-injection-theft.yaml` and `pv-02-dealer-portal-owner-data.yaml`; `check-refs.py` in this folder; `spec/vectors/README.md` (a proposal-vectors section); and `spec/schema/OBJECT-MODEL.md`, re-rendered (33 classes, 16 enums).

## Decisions for the sponsor

1. **Accept any of A1 to A7 and B1 to B5?** That takes an ADR amending ADR-0010.
2. **Where DataFlow lives.** The proposal's §1 puts DataFlow in a behavioral DFD layer, between Process, DataStore and ExternalEntity elements `realized_by` Components. This draft joins Components directly, which is OTM's shape and needs no DFD classes yet. If the DFD layer is wanted, `flow_from`/`flow_to` change range and the three DFD classes are added; the vectors show what each flow connects.
3. **Names:** `instance_of`, `build_composed_of` (beside the design-level `composed_of`), `targets_element`, and the two enums.
4. **The example models:** whether a human reviews them, so that they can become reviewed vectors.

## Not proposed, and why

- **`affects` stays Product-only.** Per-package matches go in Assertions (mapping.md rule R-MATCH-1), which work now; widening an accepted range is a larger change.
- **Version ranges, completeness, match method detail, file and content identity, build records, edge qualifiers.** These need more design (mapping.md §10); build records are post-MVP (proposal §7).
- **An identifier prefix list** (mapping.md finding 9) is a convention, not a slot; a candidate list is below for #17.
- **An Interconnect class** (proposal §1): `component_kind: interconnect` covers buses for now.

## How the example models shaped the classes

The loop DL-0013 planned: pick documented attacks, write each as a model, validate, adjust the classes, repeat. Two attacks, each from its primary write-up (digests in each file's header):

- **pv-01, keyless car theft by CAN injection** (Toyota RAV4; Canis Automotive Labs, 2023-04-03; CVE-2023-29389). It needed: assets that are messages (the "key validated" signal) as well as the vehicle itself; nested zones (control and powertrain domains within the vehicle); flows on two CAN buses, one crossing the gateway; and a CVE whose CWE came from CISA-ADP while the CNA gave none. A bare `instance_of` slot cannot say who assigned it, but an Assertion with `asserted_by` can (A1 with A5).
- **pv-02, theft of owners' personal data through a dealer portal** (Kia; Curry et al., 2024). It needed: personal data as an asset with confidentiality; a dealer-only zone nested in the manufacturer's cloud, which is the boundary the flaw broke; flows that carry personal data and account roles; and a weakness with no CVE, which enters through an `exploits` Assertion by a `software_agent` Party (A5).

Changes made while iterating:

- The vehicle-perimeter zone first listed members of its own, which contradicted the nesting; membership now comes from `in_trust_zone` alone.
- Zone membership first ran from the zone to its members (`encloses`). It was renamed and turned around to the proposal's own `in_trust_zone`, from a Component to its zone.
- A threat with two outcomes (pv-02) needed two ThreatInstances. `realizes_damage` stays single-valued, because ISO/SAE 21434's threat scenario leads to a damage scenario (RPT-0007 §1, 3.1.33).

**Findings for the next iteration (not proposed yet):**

- **P1. No way to say a Component is reachable from outside its zone.** CAN injection depends on the control bus reaching the edge of the car at the headlight. Candidate: the proposal's AttackSurface (§1), or a zone-level `exposes`.
- **P2. No external entities.** The thief's device and the attacker's browser cannot be a DataFlow's end, and pv-02 models the third-party plate lookup as a Component outside the product. Candidate: the proposal's ExternalEntity (§1), which ties into decision 2.
- **P3. An Asset that is the product itself** (pv-01's vehicle) has no link to its ProductInstance. Candidate: an Asset-to-ProductInstance edge.
- **P4. No AttackStep-to-Weakness slot.** pv-02 uses an `exploits` Assertion (ARCH-0001 §3 lists `exploits`). Candidate: `AttackStep.exploits`.
- **P5. Crossing between sibling zones** cannot be derived from membership alone, so pv-01 states it with `crosses_boundary`.

## Candidate identifier prefixes (mapping.md finding 9, for #17)

| Prefix in the vectors | Scheme | Kind |
|---|---|---|
| `pkg:` | purl (ECMA-427) | standard; its own syntax |
| `cpe:2.3:` | CPE 2.3 | standard; its own syntax |
| `swid:` | SWID or CoSWID tag id | standard id, project prefix |
| `sha256:` | a content digest | standard digest, but it does not say what was hashed. Candidate: name the level, such as `oci-manifest:sha256:<hex>` or `firmware-image:sha256:<hex>` |
| `build:`, `manifest:`, `oem-part:`, `hw-serial:`, `hw-core:`, `subsystem:` | project-defined | local. Candidate: list them in one place with their meaning, or mark them as local (for example `x-oem-part:`) |

Standard schemes the vectors do not use yet but RPT-0004 Table 3 covers: SWHID (`swh:1:`) and OmniBOR (`gitoid:`).

## Gate

```
gen-json-schema, gen-shacl, gen-pydantic (LinkML 1.12.1) on the patched schema   -> exit 0
linkml-validate, the six existing vectors (core and full containers)              -> No issues found
linkml-validate, pv-01 and pv-02 (example-container-proposed)                     -> No issues found
check-refs.py, 8 vectors                                                          -> 352 objects, 581 references, all resolve
check-refs.py on a copy of pv-01 with one dangling reference                      -> exit 1, names it
check-edges.py (DL-0021) on the four mvp-* vectors                                -> all resolve
render_object_model.py                                                            -> 33 classes, 16 enums
bin/validate-archdoc                                                              -> 0 errors
```

`check-refs.py` reads the reference slots from the schema: a slot whose range, or any of its `any_of` ranges, is a class and is not inlined. DL-0021's `check-edges.py` lists them by hand, so it would not check any new slot. On the four `mvp-*` files the two give the same 268 references.

This branch is based on `main`, which does not have #129's generated files yet. If #129 merges first, run `bin/gen-schema` here and commit the result.

## After review (2026-10-22)

**Question asked.** Two pull requests merged after this one opened (#129 and #132), and the lane owner reviewed it: what has to change? The student chose the changes below.

**What changed.**

- `main` was merged in, bringing the generated schema files and the `schema` CI job (#129) and the attack-path tests (#132).
- `bin/gen-schema` regenerated `spec/schema/generated/` from this proposal's schema, and `render_object_model.py` regenerated `OBJECT-MODEL.md`. Before that, `bin/gen-schema --check` reported all three generated files out of date, which is what the `schema` job would have failed on.
- Review note 1 (@Maimcghee): `within_boundary` now accepts a Component as well as a TrustBoundary (`any_of`, the pattern `targets_element` already uses), because an OTM trust zone's `parent` may point at a component. Before, such a zone had no target, and an OTM round trip lost it.
- Review note 2: a `zone_type` string slot on TrustBoundary, beside `trust_level`, for OTM's `trustZones[].type` and threagile's typed boundaries.
- `engine/tests/test_paths_vectors.py` (from #132) requires an `EXPECTED` entry for every example model in `spec/vectors/`. It now skips `pv-*` files, because their attack paths are AI-proposed and unreviewed, and listing them as expected results would present them as checked (CLAUDE.md). They join the test once the proposal is accepted and a human has checked their paths. The engine tests do not run on a pull request that changes only `spec/`, so without this change the failure would have shown up on the next pull request that touches `engine/`.

**Checks run** locally, with the pinned tools from `spec/schema/requirements.txt`: `bin/gen-schema --check` passes; the `schema` job's three vector steps pass (4 MVP core vectors, 2 governance vectors, all references resolve); both `pv-*` vectors validate against `example-container-proposed.linkml.yaml`, and `check-refs.py` resolves all 147 references; in `engine/` (Python 3.12), `ruff check`, `ruff format --check`, `pytest` (102 passed) and the CLI smoke test pass.

**A side effect.** `render_object_model.py` reads only a slot's `range`, so `OBJECT-MODEL.md` now shows `within_boundary` as `string`, and its diagram loses the `TrustBoundary` to `TrustBoundary` edge, as already happens for `targets_element`. The generated JSON Schema and Python types still treat the slot as a reference by id. Teaching the renderer about `any_of` is left to whoever owns it.

## Decisions (2026-10-22)

**Question asked.** The sponsor (@nymble) delegated the four decisions above to the student (@Clovier) on 2026-10-22. The student asked for them to be made as recommended, without further sponsor approval and without pull-request comments, and will give the sponsor a summary.

**What was decided** (ADR-0011):

1. A1 to A7 and B1 to B5 are accepted, in one ADR that amends ADR-0010.
2. DataFlow joins Components directly; the DFD layer is not adopted now. Component's "not an OTM diagram node" is amended in the same change (review note 3).
3. All five names stay.
4. pv-01 and pv-02 stay unreviewed: @Maimcghee has checked their sources, and @paria03 reviews their attack paths, including pv-02's CWE-862.

**What changed.**

- `spec/ADR-0011-object-model-core-amendment-1.md`, new.
- ARCH-0001 0.1.9 (banner, §3, §8) and its changelog; 0.1.10 since `main` was merged on 2026-10-29 (next section).
- The schema: its 34 "PROPOSED" prefixes now say "Accepted via ADR-0011 (DL-0024)"; its header and top description name ADR-0011; the Component and DataFlow descriptions record decision 2.
- `spec/schema/generated/` and `OBJECT-MODEL.md`, regenerated.
- For decision 4: the proposal vectors' README section, the proposal container's comment and the attack-path test's comment.

## Merging `main` after ADR-0012 (2026-10-29)

Once ADR-0012 (Requirement in the core, pull request #167) reached `main`, this pull request conflicted with it in six files, because both amend DEC-001a in the same places. `main` was merged into the branch and the conflicts resolved as follows:

- **The schema** (`tmodel-object-model.linkml.yaml`): the header names both amendments. ADR-0012's two enums (`RequirementKind`, `RequirementTextOrigin`) and this proposal's two (`ComponentKind`, `SecurityProperty`) are all kept, ADR-0012's first so that the ADR-0011 block stays together. Compared with both parents, the result has every class, slot and enum either side added (33 classes, 129 slots, 18 enums), no duplicate keys, and no class lost a slot.
- **ARCH-0001**: both branches had bumped it from 0.1.8 to 0.1.9. `main`'s 0.1.9 (ADR-0012) stays, and ADR-0011's entry becomes 0.1.10 (2026-10-29). The banner, §3 and §8 name both amendments; the DEC-001b row and the "Still open" line keep `main`'s wording, since Requirement left DEC-001b.
- **The generated files and `OBJECT-MODEL.md`**: regenerated with the pinned tools, not merged by hand.
- **The proposal container**: it is the core container plus three collections, and ADR-0012 added `requirements` to the core container, so the proposal container gets the same line.

Checks after the merge: `bin/gen-schema --check` passes; the four `mvp-*`, two `tv-*` and two `pv-*` vectors validate against their containers; `check-edges.py` (mvp vectors) and `check-refs.py` (65 reference slots, 611 references in all vectors, including mvp-02's new Requirements) resolve every reference; in `engine/`, `ruff check`, `ruff format --check` and pytest pass (138 passed; the 3 packaged-engine tests skip without a built engine).

## What was rejected, and why

- **The DFD layer for DataFlow** (decision 2, 2026-10-22): not adopted now. OTM's shape needs no DFD classes, and adding them later only widens `flow_from` and `flow_to`.
- **Listing members on the zone** (`encloses`): it contradicted nesting in pv-01, and the proposal already names the edge from the other side (`in_trust_zone`).
- **Aliases through `identifiers`:** that slot's description limits it to structural nodes, so Vulnerability gets `alias_ids`.
- **A multivalued `realizes_damage`:** see above.
- **Rating feasibility and impact in the example models:** both are human inputs (CLAUDE.md; ADR-0006), so they are left unset.
- **Reviews in the example models:** none is recorded, so nothing AI-drafted appears as reviewed. Every Assertion is `proposed`.
- **`EXPECTED` entries for `pv-01` and `pv-02`** (2026-10-22): they would freeze AI-proposed attack paths as expected results before a human checks them, so the test skips the files instead.
- **Review notes 3 and 4** (2026-10-22: the Component description's "not an OTM diagram node", which Decision 2 runs into, and a mapping for Threat Dragon's drawn boundaries): not applied in this change; the student chose notes 1 and 2.

## What a human accepted

- The student chose to take this piece of #64 and asked for it to be done as a pull request.
- 2026-10-22: @Maimcghee reviewed it as the lane owner (four notes, none blocking). The student chose to merge `main`, regenerate, apply notes 1 and 2, and skip `pv-*` in the attack-path test.
- 2026-10-22: the sponsor (@nymble) delegated the four decisions to the student. The student (@Clovier) made them as recommended (ADR-0011): A1 to A7 and B1 to B5 accepted; DataFlow joins Components directly; the names kept; pv-01 and pv-02 left for @paria03 to review.
- 2026-10-29: the student asked for this pull request's conflicts with `main` to be fixed ("Merging `main` after ADR-0012" above).
