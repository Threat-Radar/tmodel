---
schema: "archdoc/v1"
id: DL-0020
title: "§8 MVP CORE attack-path vectors — acceptance evidence for DEC-001a (core object model)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-12"
updated: "2026-10-12"
record: DL-0020
bears_on: [R-001, R-002, R-014, R-018, R-020, R-022, DEC-001, DEC-005]
defers_to: ARCH-0001
---

# DL-0020 — §8 MVP CORE attack-path vectors (DEC-001a evidence)

AI-assisted design record (per `CLAUDE.md`). Builds the `ARCH-0001-PROPOSAL` §8
**MVP interop vector set — "vectors 1–6 + 18"** — as worked example threat models
under `spec/vectors/`, using the **CORE** object model only (no governance layer,
no Environment), and proves each validates with `linkml-validate` (0 failures).
These are the acceptance evidence for **DEC-001a** (the core object model).
**Proposal only: DEC-001 stays OPEN; nothing accepted; `ARCH-0001` §8 untouched.**

## Question asked

The existing `tv-*` vectors (DL-0019) are governance-heavy: they exercise the
DEC-001b governed layer (ThreatModel / SecurityProgram / Gate / Requirement /
GovernedView). The §8 MVP set the critic actually cited — **vectors 1–6 + 18** — is
the *core* attack-path knowledge graph: **no governance, no Environment** (§8: "no
Environment parameter — post-MVP, H3"). Build that core set as honest worked models
spanning ≥2 domains with one deep (ADR-0002), and prove they validate against the
CORE classes alone, so the core model can stand as DEC-001a evidence independent of
the held governed layer.

### What "vectors 1–6 + 18" are (provenance)

The numbered enumeration is historical — it lived in earlier revisions of the
proposal's adversarial-test-case section (commits `928a852` for 1–6, `8fc6a46` for
7–13, `9c6cecf` for 14–18) and the current §8 keeps only the prose reference "MVP
vectors 1–6 + 18 first". The cited MVP cases:

1. container-image software model (deep) — Components + CVEs → CWE → CAPEC path, review, risk;
2. automotive ECU (embedded) — ISO 21434 asset/damage/threat-scenario onto the same backbone;
3. hierarchical system — `composed_of` subsystems; threats roll up;
4. product family, divergent mitigations — same weakness, different per-instance disposition;
5. multi-step attack path, AND/OR;
6. AI-proposed threat, human-rejected, with provenance;
18. a vuln carries through core → chip → server but is VEX `not_affected` in product X.

## What was produced

- `spec/vectors/example-container-core.linkml.yaml` — a **CORE-only** test-harness
  container (`ExampleModelCore`, `tree_root`) that `imports` the same object model
  but whose bundle exposes collections for the **DEC-001a core classes only**: no
  ThreatModel/SecurityProgram/Gate/Milestone/Checkpoint/Requirement/GovernedView,
  and no Environment/Deployment. A core vector that referenced a governed or
  Environment class would have nowhere to put it, so "no governance, no Environment"
  is enforced **structurally**, not by convention. The full `example-container`
  stays for the `tv-*` governance vectors.
- `spec/vectors/mvp-01-software-doc-service.yaml` — **§8 vector 1**, software (the
  ADR-0002 *deep* product): OSS document service in an OCI container; Components with
  purl/CPE `identifiers`; a CVE→CWE→CAPEC chain with propagation as a reviewed
  `Assertion`; two ordered `AttackPath`s with an **AND** gate (XXE disclosure) and an
  **OR** gate (metadata-pivot fetch); a composite-vector `RiskScore`; a core graph
  `View`; human-reviewed vs AI-proposed.
- `spec/vectors/mvp-02-automotive-ecu.yaml` — **§8 vector 2**, automotive/embedded
  (breadth): a Telematics Control Unit; ISO 21434 TARA (asset/damage/threat-scenario)
  binds onto the same `DamageScenario`/`ThreatInstance`/`RiskScore` core classes and
  the same CWE/CVE/CAPEC backbone; firmware-digest + HBOM instance identity; a
  remote-injection AND path and an AI-proposed pivot OR path that is **human-rejected**
  (vector 6's "human-rejected" verdict).
- `spec/vectors/mvp-03-hierarchical-system.yaml` — **§8 vector 3**, the ADR-0002
  *system* instance type: a Connected-Vehicle System with a 3-level `composed_of`
  tree (system → in-vehicle + cloud subsystems → leaf ECUs/services); two subsystem
  threats **roll up** (reviewed `rolls_up_to` Assertions) to one system-level
  `DamageScenario` and a single **worst-path** system `RiskScore`; a cross-subsystem
  AI-proposed pivot.
- `spec/vectors/mvp-18-shared-vuln-vex-override.yaml` — **§8 vector 18**: one finding
  in a shared crypto IP core propagates **core → chip → server** in product A (two
  reviewed `propagates_to` Assertions along `composed_of`/`uses_component`), while a
  second product embedding the same chip is **VEX `not_affected`** (a reviewed
  `vex_not_affected` Assertion with a justification on the Review). Carries the
  §8 vector-4 flavour (divergent per-product disposition) without a `ProductFamily`.
- `spec/vectors/README.md` — adds the CORE §8 MVP section, the §8-vector→file matrix,
  and the CORE-container validation commands; keeps the `tv-*` section.
- `design-log/0020-.../check-edges.py` — the standalone edge-integrity resolver
  (below), committed so the referential-integrity claim is reproducible.

### Human-reviewed vs AI-proposed (CLAUDE.md)

In every vector an AI hypothesis is a reified `Assertion` with
`assertion_status: proposed`, low `confidence`, and a paired `Review` that is
**not** an acceptance — `changes_requested` in mvp-01/03/18, and an explicit
`rejected` in mvp-02 (vector 6's "human-rejected"). Human-reviewed edges are
`assertion_status: accepted` with an `accepted` Review and a `reviewer` Party.
`ThreatInstance.source_method` records the proposing method (`ai:llm-threat-proposer
(hypothesis, unreviewed)` vs e.g. `stride-dfd (human-elicited, reviewed)`). No AI
content is presented as reviewed. People appear as github ids / roles only.

## Findings — what the CORE model can't express (recorded, NOT fixed)

DEC-001 stays open; these are inputs to the critic pass and the DEC-001 ADR, not
schema changes.

1. **No `ProductFamily` / `MitigationInstance` class (§8 vector 4).** "Same generic
   weakness, divergent mitigation per family member" has no first-class home in the
   core. Its expressible shadow — divergent per-*product* disposition — is shown in
   `mvp-18` (VEX `not_affected` on product X; per-instance `mitigation_status`), but
   true product-family divergence is post-MVP (ADR-0002 defers family automation).
2. **Roll-up / aggregation semantics are not a class (§8 vector 3).** The core
   `RiskScore` stores a *set* of `attack_paths` and the fold is "worst-path"
   (ADR-0006), so a system risk can be rolled up; but per-S/F/O/P cross-subsystem
   aggregation with a human override (the historical vector-13 `rolls_up_to` case) is
   not modeled. `mvp-03` carries roll-up as reviewed `rolls_up_to` Assertions + a
   worst-path system `RiskScore` and flags the gap in-file.
3. **`manufactured_by` / `supplied_by` are Product-only.** A `Component` cannot carry
   a manufacturer role edge (only `owned_by`). In `mvp-18` the chip-vendor→IP-core
   relationship reifies as an `Assertion` (`predicate: manufactured_by`) — which is
   the schema's intended escape hatch (§4), but it means a common supply-chain edge
   is a join, not a slot read.
4. **No provenance/agent edge on `Assertion` (carried from DL-0019 finding 1).** An
   Assertion has no `asserted_by`; AI-vs-human origin is inferable only from
   `assertion_status`/`confidence`/the Review verdict plus `source_method`. Adequate
   for MVP distinguishability; a real PROV-O edge is DEC-002 territory.
5. **`PartyKind` has no software-agent value (DL-0019 finding 2).** An AI author
   cannot be a first-class Party facet; avoided by not minting an AI Party.

None of 1–5 blocked an honest core example.

## Gate

```
# CORE vectors vs the CORE container (no governed / no Environment collections):
linkml-validate -s spec/vectors/example-container-core.linkml.yaml -C ExampleModelCore \
  spec/vectors/mvp-01-software-doc-service.yaml        -> No issues found
  spec/vectors/mvp-02-automotive-ecu.yaml              -> No issues found
  spec/vectors/mvp-03-hierarchical-system.yaml         -> No issues found
  spec/vectors/mvp-18-shared-vuln-vex-override.yaml    -> No issues found

# Edge integrity (linkml-validate does NOT check inlined:false id-ref edges):
python3 design-log/0020-mvp-core-attack-path-vectors/check-edges.py spec/vectors/mvp-*.yaml
  -> 181 objects, 268 id-references, ALL REFERENCES RESOLVE

python3 -c "import yaml; ..."  (parse)                 -> all 5 files OK
bin/validate-archdoc                                   -> 20 documents — 0 errors
```

4 CORE example threat models validated, 0 failures; 268/268 cross-references
resolve. DEC-001 remains OPEN; §8 statuses untouched.

## Next

A fresh adversarial-critic pass on the core set; feed findings 1–5 into the DEC-001
object-model ADR and the DEC-002 provenance work. The governed-layer `tv-*` vectors
remain the DEC-001b evidence on the parallel track.
