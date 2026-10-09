---
schema: "archdoc/v1"
id: ADR-0007
title: "Schema IDL & interchange — LinkML canonical, generated JSON-Schema/SHACL, committed import/export formats"
short_title: "Schema IDL & interchange"
description: "Accepts DEC-002: LinkML is the canonical schema IDL for the tmodel object model; JSON-Schema and SHACL are generated from it, never hand-authored. Canonical instance data is LinkML-shaped YAML/JSON + link records in git (ADR-0004). Committed interchange: import OTM and STIX 2.1, export JSON-LD / Turtle / GraphML / CSV, each proven by a spec/vectors round-trip. The #39 crosswalk refines and may extend import coverage."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-08"
updated: "2026-10-08"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0007-schema-idl-and-interchange.md
accepts: DEC-002
defers_to: ARCH-0001
---

# ADR-0007 — Schema IDL & interchange

**Status: accepted (2026-10-08). Accepts DEC-002.** The sponsor pinned the schema definition
language **and** committed the interchange formats now (rather than deferring the import/export
side to the crosswalk). RPT-0015 (#104 Stage 1) established LinkML as the IDL; this ADR ratifies
it and names the formats.

## Context

- `ARCH-0001` §5 kept DEC-002 open: the encoding/IDL *and* which existing formats we import/export.
- The object model is already authored in **LinkML** (`spec/schema/tmodel-object-model.linkml.yaml`),
  and ADR-0004 fixed canonical instance data as files in git with derived exports. RPT-0015 §3
  recommended LinkML as substrate-neutral with generated JSON-Schema/SHACL + a Python integrity checker.

## Decision (DEC-002)

**Schema IDL.**

| # | Decision |
|---|---|
| 1 | **LinkML is the canonical schema IDL.** The object model is defined once, in LinkML. |
| 2 | **JSON-Schema and SHACL are generated** from the LinkML (`gen-json-schema`, `gen-shacl`), **never hand-authored**. Integrity/gate rules LinkML can't express are a substrate-neutral **Python checker** (RPT-0015 §4), not hand-edited SHACL. |
| 3 | **Canonical instance data = LinkML-shaped YAML/JSON + explicit link records in git** (ADR-0004). |

**Interchange (committed baseline).**

| direction | formats |
|---|---|
| **Import** | **OTM** (Open Threat Model — first-class threat-model object model, satisfies R-005) and **STIX 2.1** bundles (threat intel). Each gets a `MAP-NNNN` crosswalk + a `spec/vectors/` round-trip. |
| **Export** | **JSON-LD**, **Turtle** (RDF-star, aligns with ADR-0008), **GraphML**, **CSV** — all **derived, never canonical** (ADR-0004). |

The **#39 schema-representations crosswalk** validates these mappings and may **extend** import
coverage (pytm, threagile, Threat Dragon) via further `MAP-NNNN` docs; it does not change the
canonical IDL or the export set.

## Consequences

- Flips **DEC-002** to accepted; `ARCH-0001` §5 and R-005/R-006 point here. `APP-0001` A-008
  (import one external format / export) resolves to: import OTM at MVP (STIX post-MVP ok), export
  the four derived forms.
- The DEC-002 round-trip contract (CF-008, #9) governs every import/export vector.
- Pairs with **ADR-0008**: Turtle/JSON-LD export is the RDF side of the Oxigraph working store;
  GraphML/CSV serve the graph viz and tabular tooling.
- The LinkML→LPG and LinkML→RDF-star lowerings (two native-generator gaps noted in RPT-0015)
  remain engineering tasks, tracked under the schema work, not blockers to this decision.

## Scope guard

Implemented only in **Threat-Radar/tmodel**. No hand-authored JSON-Schema/SHACL (generate it); no
Turtle-as-canonical authoring; import/export are derived sides, not the source of truth; interchange
additions arrive as MAP-NNNN + a vector, never as silent schema drift.
