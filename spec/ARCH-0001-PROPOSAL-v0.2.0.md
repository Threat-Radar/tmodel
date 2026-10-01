---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 2)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 2 of the DEC-001 object-model synthesis (#15), incorporating the adversarial-critic findings. Generic catalog + per-instance overlay spanning domains and instance types, shared components, cross-product attack paths with pre/postconditions, a time axis, and edge-level review/provenance. Proposed, not accepted."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.2"
version_policy: "iterate the -proposed.N suffix; folds into ARCH-0001 §3/§4 (and an ADR accepts DEC-001)"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers:
  - role: adversarial-critic
    id: agent-iteration-2
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iteration 2 folds
  in the adversarial-critic findings H1–H16 (see design-log/0002). The §4 matrix and
  §5 test suite are the gate; a case is not "modeled" until a vector exercises it.
  Nothing accepts DEC-001 here — an ADR does, after iteration 3 (research #6/#7/#9 +
  DEC-002/DEC-004).
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 2)

**Status: proposed (iteration 2).** Iteration 1 passed its own matrix by lowering
the bar (single-product cases, structural "greens"). This iteration folds in the
adversarial critique (design-log/0002, findings H1–H16) and **toughens the test
suite** with cases that failed iteration 1.

## 1. Shape: a generic catalog + a per-instance overlay + cross-cutting

- **Generic catalog** (authored once, reused): `Weakness` (CWE), `AttackPattern`
  (CAPEC / ATT&CK technique), `Mitigation` (D3FEND, `defends_against` a technique),
  `ThreatActor` (capability/resources), **`Component` (CPE / purl identity)**,
  `CybersecurityProperty` (C/I/A — an attribute enum for MVP, a node later).
- **Instance overlay** (one specific, versioned product): `Product` →
  `ProductInstance` (**versioned**), `uses_component` → the catalog `Component`,
  `Asset`, `Vulnerability` (CVE), **`Finding`** (a concrete weakness occurrence,
  no CVE required), `ThreatInstance`, **`DamageScenario`** (S/F/O/P), `AttackStep`
  (pre/postconditions), `AttackPath` (cross-product; `attack_feasibility`),
  `MitigationInstance` (effectiveness + status over time), `RiskScore`.
- **Cross-cutting:** `Assertion` (reified edge — see §6/H5), `Review` (human
  verdict/impact/rationale), `Provenance` (PROV-O Entity/Activity/Agent),
  `TrustBoundary`, `ProductFamily`. **Deferred (post-MVP, #19):** `Requirement` /
  `WorkProduct` / `Evidence` (compliance/audit — ADR-0002 puts audit out of MVP).

The generic↔instance join is **shared, CPE/purl-anchored components**: one catalog
`Component` node, many `uses_component` usages → *"which products use this vulnerable
component?"* is one query (H1/H7).

## 2. Domains, instance types, versioning (ADR-0002 R-022)

`ProductType` ∈ {software, hardware, system}; `Domain` binds a vocabulary onto the
shared backbone. **Instance identity by type:** software = build/commit/hash/SBOM;
hardware = firmware + buses + compute cores (HBOM); system = hierarchical
`composed_of`. `ProductInstance` is **versioned** (identity includes the version),
so review/mitigation/risk are answerable "as of version N" (H4). ISO 21434
(`asset / damage scenario / threat scenario`) and software (`component / dependency`)
map onto the shared nodes; the backbone (CWE/CVE/CAPEC/ATT&CK/**CPE**) stays shared.

## 3. Nodes & typed edges (proposed §3 replacement)

**Generic:** Weakness · AttackPattern · Mitigation · ThreatActor · Component(CPE/purl) · CybersecurityProperty(attr).
**Instance:** Product · ProductInstance(versioned) · Asset · Vulnerability(CVE) · Finding · ThreatInstance · DamageScenario(S/F/O/P) · AttackStep(pre/post) · AttackPath(feasibility) · MitigationInstance(effectiveness, valid_from/to) · RiskScore.
**Cross-cutting:** Assertion(reified edge) · Review · Provenance(PROV-O) · TrustBoundary · ProductFamily.
**Deferred:** Requirement · WorkProduct · Evidence.

**Typed edges:** `instance_of` · `uses_component` · `has_weakness`/`Finding instance_of Weakness` · `exploits` · `affects` (Vulnerability→Component) · `composed_of`/`part_of` · `member_of` (ProductInstance→ProductFamily) · `crosses`/`within` (TrustBoundary) · `allocated_to` · `realizes` (ThreatInstance→DamageScenario, **many-to-many**) · `compromises` (→CybersecurityProperty) · `step_of` + `and`/`or` gate nodes over step **pre/postconditions** · `pivots_to`/`traverses` (AttackStep across ProductInstances) · `reduces` (Mitigation→AttackStep/Path, with effectiveness) · `defends_against` (Mitigation→AttackPattern, D3FEND) · `rolls_up_to` (risk aggregation) · `reviewed_by` · PROV `wasGeneratedBy`/`wasAttributedTo`/`wasDerivedFrom`. Edges are typed and, where AI-proposed, **reified as `Assertion`** so they carry confidence + review + provenance (§6/H5).

## 4. Requirements-coverage matrix — *the gate (honest)*

| req | needs | covered by | status |
|---|---|---|---|
| R-001 | queryable typed graph | all nodes + typed edges | ✅ |
| R-002 | ingest radar composition | ProductInstance `uses_component` Component; Vulnerability `affects` | ✅ |
| R-005/006 | import/export formats | STIX/BRON alignment; MAP-* | ◐ (#9 crosswalk; export = iter 3) |
| R-010 | CWE/CVE mapping + NVD | Weakness/Vulnerability/Finding + CPE join | ✅ |
| R-011/012/013 | risk + attack feasibility | RiskScore + `attack_feasibility` + Review impact + ThreatActor | ◐ (DEC-003) |
| R-014/015 | interactive graph + authoring | AttackStep/Path DAG (DEC-006, #10) | ◐ |
| R-018/019 | human review + impact, on nodes **and edges** | Review + `Assertion` reification | ◐ (needs DEC-002/004 reification) |
| R-020 | generic→product **and family** | generic catalog + overlay + `ProductFamily`/`member_of` | ✅ (divergence automation = I4) |
| R-021 | mitigation across lifecycle | MitigationInstance `valid_from/to` + versioned ProductInstance | ✅ |
| R-022 | diverse domains + instance types | ProductType + per-type identity + versioning | ✅ |
| provenance | attribution of every assertion | PROV-O + `Assertion` reification | ◐ (gated on DEC-002/004) |
| ~~audit~~ | requirement→WP→evidence | deferred (Requirement/WorkProduct/Evidence) | **deferred — post-MVP (#19)** |

Honest change from iteration 1: provenance and edge-level review are **◐ not ✅**
(they gate the reification decision, H5/H12); the audit row is **deferred out of the
MVP** (H16); R-021 is now genuinely ✅ via the time axis (was a false green, H4).

## 5. Adversarial test cases — toughened (must pass as `spec/vectors/`)

Iteration-1 cases 1–6 plus the critic's must-fail cases:
7. **Shared vulnerable component across two products** — one catalog `Component`, `uses_component` from both; `Vulnerability affects` it → both products returned. → resolved by H1/H7.
8. **Cross-product pivot** — AttackPath whose steps `pivots_to` a second ProductInstance. → H2.
9. **Attack step gated on prior privilege** — step B `precondition` = postcondition of step A; AND/OR gate. → H3 (resolves open case b).
10. **"Mitigation status as of version N"** — MitigationInstance `valid_from/to` queried at a version. → H4.
11. **Reviewer rejects an AI-proposed `exploits` edge** — `Assertion`(edge) + Review(reject) + Provenance(AI activity). → H5.
12. **Partial mitigation** — `reduces` likelihood-not-impact on a specific AttackStep, residual risk recomputed. → H9.
13. **Hierarchical roll-up** — `rolls_up_to` with worst-case-per-S/F/O/P aggregation, `wasDerivedFrom` inputs, human override. → H15 (resolves open case a).

A case is "modeled" only when it exists as a vector in `spec/vectors/`.

## 6. Edge-level review & provenance (H5 — architectural, gates DEC-002/004)

The thesis is *AI proposes, humans review* — and what AI proposes is mostly
**relationships** (this CWE applies here; this `exploits`; this step follows that).
Edges must therefore carry **confidence**, a **review verdict**, and **per-assertion
provenance**. In RDF this needs reification — **named graphs, RDF-star, or an explicit
`Statement`/`Assertion` node**. This is a prerequisite for DEC-002 (encoding) and
DEC-004 (substrate), not cosmetic. Iteration 3 must pick the mechanism.

## 7. Iteration log & next

- **Iter 1:** generic/instance split, domains, typed edges, matrix green-by-lowered-bar.
- **Iter 2 (this):** folded H1–H16 — shared CPE/purl components, cross-product paths,
  step pre/postconditions + AND/OR, time axis, edge reification, restored
  TrustBoundary/ProductFamily/DamageScenario(+feasibility)/ThreatActor/Finding,
  dropped redundant generic `Threat`, roll-up semantics, deferred audit; honest matrix.
- **Iter 3 (next):** fold frameworks (#6) / products (#7) / schema-crosswalk (#9);
  **decide the reification mechanism (H5) → DEC-002/DEC-004**; build vectors 7–13;
  then fold the matured model into ARCH-0001 §3/§4 and **accept DEC-001 via an ADR**.
