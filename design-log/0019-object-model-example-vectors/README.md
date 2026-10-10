---
schema: "archdoc/v1"
id: DL-0019
title: "Dogfood the §13 LinkML draft with worked example threat models (test vectors)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-09"
updated: "2026-10-09"
record: DL-0019
bears_on: [R-020, R-041, R-042, R-043, R-044, DEC-001, DEC-009]
defers_to: ARCH-0001
---

# DL-0019 — example threat models as test vectors; what they revealed

AI-assisted design record for #15 (per `CLAUDE.md`). Builds worked **example threat models** under
`spec/vectors/` and proves they validate against the DRAFT object model
(`spec/schema/tmodel-object-model.linkml.yaml`) with `linkml-validate`. **Proposal only: DEC-001
stays OPEN; nothing accepted; ARCH-0001 §8 untouched.**

## Question asked

Create a few honest example threat models as instance data conforming to the proposed object model,
one per domain (ADR-0002: software build/SBOM *and* hardware/firmware), exercising the real graph —
components, weakness/vuln propagation, AttackPaths with AND/OR gates, Mitigations with status, a
composite-vector RiskScore (ADR-0006), Party roles, the human-reviewed vs AI-proposed distinction,
a governed `ThreatModel` snapshot, and an SDL `SecurityProgram` with a conformance-validating Gate.
Prove each validates (`linkml-validate`, 0 failures). Where the schema can't express something an
honest example needs, treat it as a finding and fix the draft (DEC-001 open) or record it.

## What was produced

- `spec/vectors/example-container.linkml.yaml` — a test-harness container (`ExampleModel`,
  `tree_root`) that `imports` the object model and adds one flat per-type collection class, so a whole
  worked example validates in a single `linkml-validate` run. Deliberately **not** added to the domain
  schema, so no test-only class leaks into the model or `OBJECT-MODEL.md`.
- `spec/vectors/tv-software-auth-service.yaml` — software domain (the ADR-0002 *deep* product): an OSS
  auth microservice. Components with purl/CPE `identifiers`; a CVE→CWE→CAPEC chain with propagation
  modeled as a reviewed `Assertion`; two `AttackPath`s of ordered `AttackStep`s with an **AND** gate
  (deser trigger) and an **OR** gate (publish-malicious-release); `Mitigation`s with `mitigation_status`
  `complete`/`in_progress`; a composite-vector `RiskScore` (S/F/O/P + feasibility + mitigation-status +
  derived risk); Party roles (manufacturer/supplier/owner/cna/reporter); a governed `ThreatModel` rev 3
  that `supersedes` rev 2; and an SDL `SecurityProgram` with a `Gate`/`Milestone`/`Gate`, a
  `Requirement` with opaque `source_ref: library:nist-sp-800-218#PO.1.1`, `satisfied_by` a Mitigation,
  and a release Gate that `validates_conformance_of` the ThreatModel.
- `spec/vectors/tv-hardware-brake-ecu.yaml` — hardware/firmware domain (the ADR-0002 *breadth*
  product): a brake ECU. Firmware-image `sha256` + hardware serial as `ProductInstance` identity; dual
  compute cores as structural `Component`s under a SoC; a distinct physical/glitch `AttackPath` with an
  AND gate; `LifecyclePhase` + `Environment`/`Deployment`; Mitigations with status; a safety-dominated
  composite `RiskScore`; a governed `ThreatModel` rev 1.
- `spec/vectors/README.md` rewritten from the "empty until I2" stub to describe the vectors, the
  examples-not-truth framing, and the validation commands.
- Regenerated `spec/schema/OBJECT-MODEL.md`; bumped `ARCH-0001-PROPOSAL` **proposed.13 → proposed.14**
  (`updated` coupled; §11 note).

### Human-reviewed vs AI-proposed (CLAUDE.md)

AI-proposed content is never presented as reviewed. In both vectors an AI hypothesis is a reified
`Assertion` with `assertion_status: proposed`, a low `confidence`, and a paired `Review` with
`review_status: changes_requested` (software: the upstream supply-chain path; hardware: the
voltage-glitch step). Human-reviewed edges are `assertion_status: accepted` with a `Review` whose
`review_status: accepted` and a `reviewer` Party. `ThreatInstance.source_method` records the proposing
method (e.g. `ai:maestro-agent (hypothesis, unreviewed)` vs `stride-dfd (human-elicited, reviewed)`).

## Accepted (and why) — the one schema fix the examples forced

- **Opaque, multivalued `identifiers` slot on `Product` / `ProductInstance` / `Component`.** ADR-0002
  makes per-type **instance identity** first-class ("software = build/commit/hash/SBOM; hardware =
  firmware + buses + cores (HBOM)"), and both honest examples need to carry a purl/CPE/SBOM ref and a
  firmware-image digest. The draft had **no** home for this: `catalog_ref` exists only on the catalog
  classes (Weakness/Vulnerability/AttackPattern/Mitigation) and names a *generic* catalog entry, not
  the concrete artifact. Faking it in `name`/`description` would defeat the dogfooding. The fix is the
  minimal, house-style one: an **opaque** scheme-prefixed string list (like `catalog_ref` /
  `external_refs`), importing no CPE/SBOM schema (ADR-0004 substrate-neutrality), additive, DEC-001
  still open. Added to the LinkML, re-rendered `OBJECT-MODEL.md`, bumped the proposal.

### Other things accepted

- **A separate importing container schema** rather than an `ExampleModel` class in the domain model —
  keeps the proposed object model pure and its rendered view honest.
- **Every cross-reference resolves** to a real object in the same file, even though `linkml-validate`
  does not enforce referential integrity for `inlined: false` edges — honesty over the minimum.

## Findings — recorded, NOT fixed (gaps the model still can't express)

1. **No provenance/agent edge on `Assertion`.** An Assertion has `subject`/`predicate`/`object`/
   `confidence`/`assertion_status` but **no `asserted_by`** to the Party/agent that made it. The schema
   says PROV Agent is a facet of Party, yet nothing links a statement to its author. AI-vs-human origin
   is today only *inferable* from `assertion_status: proposed` + `confidence` + the presence/verdict of
   a `Review`, plus `ThreatInstance.source_method`. Sufficient for MVP distinguishability; a real
   `asserted_by`/PROV-O edge is DEC-002 territory (out of scope).
2. **`PartyKind` has only `organization` / `person`** — no `software-agent`/`automated` value, so an
   AI author cannot be represented as a first-class Party facet even though the model claims PROV Agent
   is such a facet. Avoided in the vectors by not minting an AI Party.
3. **No origin field on `AttackPath` / `AttackStep` / most domain nodes.** Only `ThreatInstance` has
   `source_method`. An AI-proposed *path* or *step* carries its origin only via a reifying Assertion,
   not on the node itself — workable, but it means "was this node AI-proposed?" is a join, not a read.
4. **`Mitigation` has no evidence/work-product link beyond opaque `external_refs`.** Conformance
   "evidenced" (R-042) leans on free strings + the approving Review; a first-class `Evidence`/
   `WorkProduct` is the #19 audit model's call (as DL-0018 already noted).
5. **`members` / `supersedes` ranges are `Node` (abstract).** Expressive but unconstrained — a
   ThreatModel could list any node as a member; a per-type constraint is left to a future SHACL/gate
   layer (§13 says the acceptance gate is hand-written, not gen-emitted).

None of 1–5 blocked an honest example, so none were fixed here; they are inputs to the next critic
pass and the eventual DEC-001/DEC-002 ADRs.

## Gate

```
linkml-validate -s spec/vectors/example-container.linkml.yaml -C ExampleModel \
  spec/vectors/tv-software-auth-service.yaml   → No issues found
linkml-validate -s spec/vectors/example-container.linkml.yaml -C ExampleModel \
  spec/vectors/tv-hardware-brake-ecu.yaml       → No issues found
python3 spec/schema/render_object_model.py      → wrote OBJECT-MODEL.md — 30 classes, 14 enums
bin/validate-archdoc                             → clean
```

2 example threat models validated, 0 failures. DEC-001 remains OPEN.

## Next

A fresh adversarial-critic pass on proposed.14; feed findings 1–5 into the DEC-002 provenance/PROV-O
work and the #19 audit model; DEC-001 accepts last, folding the model into ARCH-0001 §3/§4.
