---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 1)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 1 of the DEC-001 object-model synthesis (#15). Proposes an expanded ARCH-0001 §3/§4: a generic/instance object model spanning diverse domains and instance types, with a requirements-coverage matrix and adversarial test cases. Proposed, not accepted."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.1"
version_policy: "iterate the -proposed.N suffix; folds into ARCH-0001 §3/§4 (and an ADR accepts DEC-001)"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iterative: the
  requirements-coverage matrix (§4) and the adversarial test cases (§5) are the
  gate; an item is not "modeled" until a test case exercises it. Nothing accepts
  DEC-001 here — an ADR does, once the matrix is green and research (#6/#7/#9) lands.
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 1)

**Status: proposed (iteration 1).** Synthesizes the object model for DEC-001 from
what is in hand (ARCH-0001 §3/§4, ADR-0001 split, ADR-0002 MVP scope, RPT-0011 gap
analysis, the ISO 21434 object model, STIX 2.1 / BRON / D3FEND). **It is iterated:
each pass must keep the §4 coverage matrix green and resolve §5 adversarial cases.**

## 1. Shape: a generic catalog + a per-instance overlay

The model has **two layers**, which is what makes it generalize across domains and
instance types (ADR-0002 R-020/R-022):

- **Generic layer** — the reusable catalog, modeled once: `Weakness` (CWE),
  `AttackPattern` (CAPEC / ATT&CK technique), generic `Threat`, generic
  `Mitigation` (D3FEND), `CybersecurityProperty`.
- **Instance layer** — a specific product and its graph: `Product` → `ProductInstance`,
  `Component`, `Asset`, `Vulnerability` (CVE), `ThreatInstance`, `AttackStep`,
  `AttackPath`, `MitigationInstance` (with status), `RiskScore`.
- **Cross-cutting** — `Review` (human verdict), `Provenance` (PROV-O), and
  `Requirement`/`WorkProduct` (compliance, from ISO 21434).

A generic item **applies to** an instance via the overlay (`applies_to_product` +
`Review` + `MitigationInstance`) — so the same CWE/attack pattern is authored once
and specialized per product without duplication.

## 2. Domains and instance types (ADR-0002)

- **ProductType** ∈ {software, hardware, system}; **Domain** is a label
  (e.g. software-OSS, automotive-embedded) that binds a domain vocabulary onto the
  shared backbone.
- **Instance identity differs by type:** software = build / commit / hash / SBOM;
  hardware = firmware + buses + compute cores (HBOM); system = hierarchical
  `composed_of` of the above.
- **Domain vocabularies map in, not fork:** e.g. ISO 21434 `asset / damage scenario
  / threat scenario` map onto `Asset / (RiskScore impact) / ThreatInstance`; software
  `component / dependency` map onto `Component`. The backbone (CWE/CVE/CAPEC/ATT&CK)
  stays shared.

## 3. Nodes & typed edges (proposed §3 replacement)

| node | layer | notes / external anchor |
|---|---|---|
| Weakness | generic | CWE |
| AttackPattern | generic | CAPEC / ATT&CK technique |
| Threat (generic) | generic | STIX Attack-Pattern-ish |
| Mitigation (generic) | generic | D3FEND countermeasure |
| CybersecurityProperty | generic | C/I/A… |
| Product / ProductInstance | instance | typed (sw/hw/system); identity per §2 |
| Component | instance | SBOM / HBOM element |
| Asset | instance | the thing damage happens to |
| Vulnerability | instance | CVE/NVD/OSV |
| ThreatInstance | instance | a generic Threat applied to this product |
| AttackStep / AttackPath | instance | step_of; AND/OR composition |
| MitigationInstance | instance | status: planned/deferred/complete/accepted-risk/na |
| RiskScore | instance | per environment (DEC-003) |
| Review | cross | verdict + impact + rationale + reviewer |
| Provenance (Entity/Activity/Agent) | cross | PROV-O |
| Requirement / WorkProduct | cross | ISO 21434 / compliance |

**Typed edges:** `instance_of` · `has_weakness` · `exploits` · `affects` ·
`composed_of` / `part_of` · `allocated_to` · `realizes` · `compromises` ·
`step_of` (+ `and`/`or` grouping) · `mitigated_by` · `applies_to_product` ·
`reviewed_by` · `wasGeneratedBy` / `wasAttributedTo` / `wasDerivedFrom` (PROV) ·
`satisfies` / `derives_from` (requirements). Edges are typed (not tags) — queryable.

## 4. Requirements-coverage matrix — *the gate*

Every modeling requirement must be satisfied by a node/edge above. Green = covered.

| req | what it needs | covered by | status |
|---|---|---|---|
| R-001 | queryable typed graph | all nodes + typed edges | ✅ |
| R-002 | ingest radar composition | Component/Vulnerability + `affects` (ADR-0001) | ✅ |
| R-005/006 | import/export existing formats | STIX/BRON alignment; MAP-* | ◐ (needs #9 crosswalk) |
| R-010 | CWE/CVE mapping + NVD | Weakness/Vulnerability + `has_weakness`/`exploits` | ✅ |
| R-011/012/013 | risk "how bad" (CVSS/21434/CC) | RiskScore + Review impact | ◐ (DEC-003) |
| R-014/015 | interactive graph + authoring | AttackStep/AttackPath graph (DEC-006, #10) | ◐ |
| R-018…R-021 | human review, impact, product + lifecycle | Review + MitigationInstance + `applies_to_product` | ✅ (lifecycle automation = I4) |
| R-020 | generic→product/family mapping | generic layer + overlay | ✅ (family divergence = I4) |
| R-022 | diverse domains + instance types | ProductType + per-type identity (§2) | ✅ |
| (audit) | requirement→work-product→evidence | Requirement/WorkProduct + `satisfies` | ◐ (#19) |
| (provenance) | attribution/audit of every assertion | Provenance (PROV-O) | ✅ |

◐ = structurally covered, pending a decision or research input (named). **No red** —
every requirement has a home in the model.

## 5. Adversarial test cases — *must pass*

The model is only "right" if these resolve. (iteration 1 result)

1. **Container image (software, deep):** radar → Components + CVEs → CWE → CAPEC → ATT&CK path; review; risk. → **pass** (backbone + overlay).
2. **Automotive ECU (embedded):** ISO 21434 asset/damage/threat-scenario map onto Asset/ThreatInstance/RiskScore; same CWE/CVE backbone. → **pass** (domain vocab binds in).
3. **Hierarchical system:** `composed_of` subsystems; threats roll up. → **pass** (composition edge); *open:* roll-up/aggregation semantics (iteration 2).
4. **Product family, divergent mitigations:** same generic weakness, different `MitigationInstance` per instance. → **pass** structurally; family-level automation deferred (I4).
5. **Multi-step attack path, AND/OR:** `step_of` + and/or grouping. → **pass** (needs vector in `spec/vectors/`).
6. **AI-proposed threat, human-rejected, with provenance:** ThreatInstance + Review(verdict=reject) + Provenance(Activity=AI, Agent=reviewer). → **pass** (this is the core thesis).

## 6. Iteration log & next

- **Iteration 1 (this doc):** generic/instance split, domain + instance-type model,
  typed edges, coverage matrix green, 6 adversarial cases (4 pass, 2 pass-with-open).
- **Iteration 2 (next):** fold in the frameworks feature list (#6), the products
  feature matrix (#7), and the schema crosswalk (#9); run a fresh **adversarial-critic
  pass**; resolve the open items (system roll-up; AND/OR vector; export, R-006);
  pick the STIX-vs-native encoding (DEC-002) and graph substrate (DEC-004).
- **Then:** fold the matured model into ARCH-0001 §3/§4 and accept DEC-001 via an ADR.
- **Build `spec/vectors/`** for cases 1, 5, 6 as the executable contract.
