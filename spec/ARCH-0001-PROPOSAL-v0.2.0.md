---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 4)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 4 of the DEC-001 object-model synthesis (#15). Reconciles the three layers after the iteration-3 adversarial pass: one authoritative artifact layer with DFD roles projected onto it, STRIDE as a facet of the single threat vocabulary, one provenance spine, honest matrix, and an explicit MVP/post-MVP split. Proposed, not accepted."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.4"
version_policy: "iterate the -proposed.N suffix; folds into ARCH-0001 §3/§4 (and an ADR accepts DEC-001)"
date: "2026-09-30"
updated: "2026-10-01"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers:
  - role: sponsor-review
    id: paul-lambert
  - role: adversarial-critic
    id: agent-iteration-2
  - role: adversarial-critic
    id: agent-iteration-3
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iteration 4 folds the
  iteration-3 adversarial findings F1–F13 (design-log/0004): reconcile the layers,
  unify the threat vocabulary and the provenance spine, add the missing requirements,
  make the matrix honest, and bound the MVP (§9). Open items (reification DEC-002/004,
  risk metric DEC-003, DFD-standard alignment pending #9) are marked ◐, not pretended.
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 4)

**Status: proposed (iteration 4).** Iteration 3 added three layers but, per the
adversarial pass (DL-0004), **double-modeled reality on three axes**, ran two threat
taxonomies and two provenance mechanisms without crosswalks, and claimed DFD-standard
alignment ahead of the research (#9). Iteration 4 **reconciles** them and **bounds the
MVP**.

## 0. One-artifact rule (F1) — how the layers relate

- **`Component` is the authoritative layer** — the deployed artifact that *exists*
  (service, container, dependency, chip, core).
- **DFD elements are behavioral *roles* projected onto Components**, not new things:
  a `Process`/`DataStore` MUST resolve to ≥1 Component via **`realized_by`/`runs_on`/
  `stored_in`**. A `DataFlow` resolves to a `connected_via` path between those
  Components' hosts. When the two disagree, the Component layer wins and the DFD is
  invalid until it resolves. This removes the Component-vs-Process and
  reachability double-modeling.

## 1. Layers (reconciled)

1. **Structural (authoritative)** — Product/ProductInstance(versioned), Component
   (CPE/purl, shared), `composed_of`, Interconnect/Network/NetworkLink, TrustBoundary
   (a **zone**: elements declare `in_trust_zone`, F12), AttackSurface, Deployment→Environment.
2. **Behavioral (DFD) — projected onto (1)** — ExternalEntity, Process, DataStore,
   DataFlow, Workflow, each `realized_by` Component(s), with **security properties**
   (authenticated? encrypted? privilege) and **data `classification`** that drive STRIDE.
3. **Threat & catalog (one vocabulary, F2)** — generic Weakness(CWE)/AttackPattern
   (CAPEC/ATT&CK)/Mitigation(D3FEND)/ThreatActor; instance ThreatInstance (carries a
   **STRIDE facet**, `realizes` DamageScenario), AttackStep(pre/postconditions)/AttackPath
   (`attack_feasibility`), Finding/Vulnerability, MitigationInstance, RiskScore.
4. **Cross-cutting** — **one provenance spine** (F6): PROV-O Entity/Activity/Agent
   nodes + a reified **`Assertion`** for AI-proposed edges that *points at* its
   generating Activity; Review; ProductFamily; external refs.

**Reachability is one concept at three levels, not three models:** `connected_via`
(physical/network reachability) → an `AttackStep.precondition` may require it → an
`AttackPath` `pivots_to` across it. DataFlow is the *intended* traffic; AttackStep is
the *adversary* use of the same substrate.

## 2. Threat vocabulary — STRIDE is a facet, not a parallel list (F2)

A STRIDE "Tampering-on-this-DataFlow" **is a `ThreatInstance`** whose `AttackPattern`
carries a `stride` facet and anchors to CWE/CAPEC; an `AttackStep` `exploits` the flow.
One threat list, classifiable by STRIDE *and* traceable to BRON. (The STRIDE↔CWE/CAPEC
mapping table is deferred to #9; the integration rule is fixed here.)

## 3. Structure, networks, deployment (as iteration 3, with fixes)

Recursive `composed_of`; Interconnect→Network/NetworkLink (bus→Ethernet→WAN); DNS/
services as Components + `depends_on`. **Environment is a first-class, reusable node**
(F9): `ProductInstance` 1→N `Deployment`, each →1 `Environment`
(physical_security/connectivity/operational_context, enum-typed). **Environment +
AttackSurface.exposure are risk *inputs that parameterize the chosen metric*** (F5) —
they feed ISO 21434 window-of-opportunity / CVSS Attack-Vector+environmental, **never a
parallel adjustment**. Attacker position relative to a Network is an `AttackStep`
precondition type (F10).

## 4. Provenance — one spine (F6/F7)

PROV-O is the node model (Entity/Activity/Agent + used/wasGeneratedBy/wasDerivedFrom/
wasAssociatedWith). An AI-proposed edge is a reified **`Assertion`** whose provenance
**points at the AI-generation `Activity`** — *one* event, not two mechanisms.
**AI-generation provenance** (prompt→output) stays in-model (the "AI proposes → human
reviews" audit). **Compile / SLSA build provenance moves to the radar→tmodel contract
as imported attestations** (supply-chain integrity = radar's territory, ADR-0001) —
out of the MVP core (F7). The provenance **view (#10) does not exist yet**; SLSA/in-toto
equivalence is unverified against `in-toto-attestation-v1`/`guac` — both marked ◐.

## 5. Propagation & VEX (F8)

Vulnerability/Finding propagation along `uses_component`/`composed_of` is sound (✅).
The per-instance **VEX override** is an `Assertion`+`Review` on the propagated edge —
same open reification as §4 — so it is **◐**, not ✅. External refs (Jira) unchanged.

## 6. Requirements-coverage matrix — honest (F4/F8/F11)

R-001…R-022 as before, with these corrections and additions:

| req | covered by | status |
|---|---|---|
| R-023 (deployment-relative risk) | Environment/exposure as metric inputs | ◐ (gated on DEC-003) |
| R-024 (data-flow / DFD) | Process/DataFlow/… projected via realized_by | ◐ (needs data classification, below) |
| R-025 (process provenance) | PROV-O + Assertion spine; AI-gen in-model | ◐ (gated on reification; view #10 TBD) |
| R-026 (network topology) | Network/NetworkLink + service depends_on | ✅ |
| R-027a (vuln propagation) | traversal of uses_component/composed_of | ✅ |
| R-027b (VEX override) | Assertion+Review on propagated edge | ◐ (gated on reification) |
| R-028 (external refs / Jira) | external_refs attribute | ✅ |
| **R-029 (data classification)** | `classification` on DataStore/DataFlow/Asset | ✅ (new) |
| **R-031 (workflow ordering)** | ordering/sequence on Workflow | ◐ (new; define in iter 5) |
| **R-032 (entity/agent trust)** | trust level on ExternalEntity + PROV Agent | ◐ (new) |

Honest deltas from iteration 3: R-023/R-024/R-025 and R-027b downgraded to ◐; R-029/R-031/R-032 added.

## 7. MVP / post-MVP split (F3) — *the scope gate*

ADR-0002 accepted an **attack-path knowledge graph** (Option A), not a DFD/STRIDE tool.
The model expresses more than the MVP builds; this table is binding for Nov 5.

| object / capability | MVP (Nov 5) | post-MVP |
|---|---|---|
| Product/ProductInstance, Component(CPE/purl)+composition | ✅ build | |
| BRON backbone: Weakness/AttackPattern/Vulnerability/Finding | ✅ build | |
| ThreatInstance / AttackStep / AttackPath (+feasibility) | ✅ build | |
| Review + provenance of AI-proposed nodes/edges | ✅ build (minimal) | |
| RiskScore (simple: CVSS-env + human impact) | ✅ build | |
| generic↔instance mapping, ≥2 domains/instance types | ✅ build | |
| full **DFD layer** (Process/DataFlow/DataStore/ExternalEntity/Workflow) | *one illustrative flow only* | ✅ post-MVP |
| **Network/NetworkLink/DNS** topology | — | ✅ post-MVP |
| **Deployment/Environment/exposure** | *single deployment assumed* | ✅ post-MVP |
| **compile/SLSA build provenance** | — (radar contract) | ✅ post-MVP |
| **VEX** override | — | ✅ post-MVP |
| **Jira external_refs**, audit (Requirement/WorkProduct) | — | ✅ post-MVP (#19) |

**The MVP is the attack-path KG.** Students build the top block; DFD/networks/
provenance are modeled but **not built** for Nov 5 (at most one illustrative flow +
one AI-gen provenance chain, if time).

## 8. Vectors (must become `spec/vectors/`)

MVP vectors 1–6 + 18 (vuln-carry) first. Post-MVP vectors 7–17 (DFD, networks,
provenance, env-relative risk) follow, and need the element security properties +
attacker-position preconditions added in §1/§3 (F10).

## 9. Caveat — DFD-standard alignment is provisional

iteration 3 claimed alignment with OTM/threagile/pytm/Threat Dragon; **those records
don't exist yet and RPT-0001 §3/§5 is pending.** Only RPT-0003 (products) is verified.
The DFD design here is **provisional pending #9**; interchange/layout (OTM) and the fact
that these tools are mutually incompatible are flagged for DEC-002 (F13).

## 10. Iteration log & next

- **Iter 1–3:** split, adversarial fixes, three layers.
- **Iter 4 (this):** reconcile layers (one-artifact rule), unify threat vocabulary
  (STRIDE facet) and provenance (one spine), add R-029/031/032 + data classification,
  honest matrix, **MVP/post-MVP table**, move compile/SLSA to radar contract (F1–F13; DL-0004).
- **Iter 5 (next):** fold frameworks (#6)/products (#7)/schema-crosswalk (#9);
  **decide reification (DEC-002/DEC-004)** and the **risk metric (DEC-003)** — these flip
  the ◐s; build the MVP vectors; then fold into ARCH-0001 §3/§4 and **accept DEC-001 via an ADR**.
