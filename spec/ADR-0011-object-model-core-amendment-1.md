---
schema: "archdoc/v1"
id: ADR-0011
title: "Object model core, amendment 1: composition slots and the Asset, TrustBoundary and DataFlow classes (refines DEC-001a)"
short_title: "Core amendment 1 (DEC-001a)"
description: "Amends ADR-0010 (DEC-001a). Accepts DL-0024's additions to the core: A1 to A7, the composition slots RPT-0004's Table 6 asked for, and B1 to B5, the Asset, TrustBoundary and DataFlow classes RPT-0005's gap G13 asked for. DataFlow joins Components directly, as OTM does. The proposed names stay. The example models pv-01 and pv-02 stay unreviewed until a human other than their author checks their attack paths."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-22"
updated: "2026-10-22"
decision_makers:
  - role: student
    id: Clovier
    delegated_by: nymble
reviewers: []
needs_review: false
reviewed: false
canonical_path: spec/ADR-0011-object-model-core-amendment-1.md
amends: ADR-0010
refines: DEC-001a
defers_to: ARCH-0001
---

# ADR-0011: Object model core, amendment 1 (DEC-001a)

**Status: accepted (2026-10-22). Amends ADR-0010 (refines DEC-001a).** Decided by @Clovier, to whom the sponsor (@nymble) delegated the four decisions DL-0024 asks for, on 2026-10-22. The proposal behind it (DL-0024, pull request #130) was reviewed by the schema lane owner (@Maimcghee) on 2026-10-22.

## Context

- ADR-0010 accepted the core attack-path type system. Two later findings showed facts the core cannot hold:
  - RPT-0004's Table 6 (`research/0004-product-composition/mapping.md`): per-build composition, a version, a component kind, the CVE-to-CWE edge, who made an Assertion and when, alias ids, and a component's supplier or maker.
  - RPT-0005's gap G13: the OTM import ADR-0007 commits to needs Asset, TrustBoundary and DataFlow. The sponsor's direction of 2026-10-14 (DL-0013) was to add them, shaped by example models of published automotive attacks.
- DL-0024 proposed additive, optional changes for both (A1 to A7, B1 to B5). No slot is renamed, removed or narrowed, and the six existing vectors still validate. Two example models, `spec/vectors/pv-01-can-injection-theft.yaml` and `pv-02-dealer-portal-owner-data.yaml`, shaped the classes.

## Decision

1. **Accept A1 to A7 and B1 to B5** as DL-0024 defines them, into the core:
   - A1: `Vulnerability.instance_of` (range Weakness), the CVE-to-CWE edge.
   - A2: `version` on ProductInstance and Component.
   - A3: `Component.component_kind`, with the enum `ComponentKind` (CycloneDX 1.7's 13 component types, plus `service` and `interconnect`).
   - A4: `ProductInstance.build_composed_of` (range Component), the per-build composition an SBOM gives.
   - A5: Assertion provenance (`asserted_by`, `asserted_at`, `generated_by`, `evidence`), and the PartyKind value `software_agent`.
   - A6: `Vulnerability.alias_ids` (GHSA, OSV and distribution ids).
   - A7: `supplied_by` and `manufactured_by` on Component.
   - B1: the class `Asset` (`security_properties`, `stored_in`, `processed_by`, `owned_by`), with the enum `SecurityProperty`.
   - B2: the class `TrustBoundary` as a zone (`within_boundary`, `trust_level`, `zone_type`), with `Component.in_trust_zone`.
   - B3: the class `DataFlow` (`flow_from`, `flow_to`, `carries`, `protocol`, `bidirectional`, `crosses_boundary`).
   - B4: `DamageScenario.damages_asset` and `compromised_property`.
   - B5: `ThreatInstance.targets_element` (a Component, DataFlow, Asset or TrustBoundary).
2. **DataFlow joins Components directly,** as OTM's `dataflows` do. The behavioral DFD layer in the proposal's §1 (Process, DataStore and ExternalEntity elements `realized_by` Components) is not adopted now; a later ADR that adds it would widen `flow_from` and `flow_to`. Component's description drops "not an OTM diagram node" (§0), because a Component is now the end of a DataFlow and a member of a trust zone, as an OTM component is. This settles review note 3 on #130.
3. **The proposed names stay:** `instance_of`, `build_composed_of` (beside the design-level `composed_of`), `targets_element`, `ComponentKind` and `SecurityProperty`.
4. **The example models stay unreviewed until a human other than their author checks them.** @Maimcghee checked both against their sources in her review of #130. @paria03 reviews their attack paths, including whether CWE-862 is the right weakness for pv-02, which nobody has checked yet. Until then every Assertion in them stays `proposed`, they keep their own container (`spec/vectors/example-container-proposed.linkml.yaml`), and the attack-path test skips them (`engine/tests/test_paths_vectors.py`).

## Consequences

- DEC-001a now includes these elements. ARCH-0001's status banner, §3 and §8 point to this ADR as well as to ADR-0010, and the schema's descriptions say "Accepted via ADR-0011 (DL-0024)" where they said "PROPOSED".
- Not accepted here:
  - what DL-0024 lists under "Not proposed": `affects` stays Product-only; version ranges, completeness, match details, file and content identity, build records and edge qualifiers; an identifier prefix list; an Interconnect class;
  - DL-0024's findings P1 to P5 for a next iteration: reachability from outside a zone, external entities, an Asset-to-ProductInstance edge, `AttackStep.exploits`, and crossing between sibling zones;
  - review note 4 on #130, a mapping for Threat Dragon's drawn boundaries.
- DEC-001b, DEC-008 and DEC-009 stay open.
- The OTM import (ADR-0007) can map OTM `assets`, `trustZones` and `dataflows` onto core classes. Its field-level crosswalk is still to be written (#9), as a `MAP-NNNN` with a vector.
- `OBJECT-MODEL.md` shows `within_boundary` and `targets_element` as strings, because its renderer reads only a slot's `range`; the generated JSON Schema and Python types treat them as references (DL-0024).

## Scope guard

Implemented only in Threat-Radar/tmodel. This accepts logical types and slots, not encoding beyond ADR-0007, not the governed layer (DEC-001b), and not a DFD layer. pv-01 and pv-02 are not reviewed vectors.
