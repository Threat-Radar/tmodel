---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 3)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 3 of the DEC-001 object-model synthesis (#15). Three layers — structure (composition, networks, deployment/environment), behavior (data-flow/DFD, workflows), and provenance (PROV-O over nodes, edges, and processes) — plus the generic/instance threat catalog. Proposed, not accepted."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.3"
version_policy: "iterate the -proposed.N suffix; folds into ARCH-0001 §3/§4 (and an ADR accepts DEC-001)"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers:
  - role: sponsor-review
    id: paul-lambert
  - role: adversarial-critic
    id: agent-iteration-2
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iteration 3 folds
  in two rounds of sponsor review (design-log/0003): physical/environment, codebase
  findings + Jira, vulnerability propagation + VEX, hardware composition depth + buses;
  and networks/topology, data-flow (DFD), process provenance (compile / AI-generation).
  The §7 matrix and §8 vectors are the gate. DEC-001 is accepted by an ADR after
  iteration (research #6/#7/#9 + the reification decision DEC-002/DEC-004).
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 3)

**Status: proposed (iteration 3).** The model is now **three layers plus a threat
catalog and cross-cutting provenance** — enough to express the sponsor's review
cases (physical exposure, networks/DNS, AI workflows across phone↔server, build and
AI-generation provenance), while the MVP (ADR-0002) still exercises only a slice (§9).

## 1. Layers

1. **Structural** — *what a thing is made of and where it runs*: Product,
   ProductInstance, Component, composition, Interconnect/Network, TrustBoundary,
   AttackSurface, Deployment→Environment.
2. **Behavioral (data-flow / DFD)** — *what it does*: ExternalEntity, Process,
   DataStore, DataFlow, Workflow — laid over the structure, crossing trust boundaries.
3. **Threat & catalog** — generic catalog (Weakness, AttackPattern, Mitigation,
   ThreatActor) + instance threats (ThreatInstance, DamageScenario, AttackStep,
   AttackPath, Finding, Vulnerability, MitigationInstance, RiskScore).
4. **Cross-cutting** — Provenance (PROV-O over nodes, **edges via Assertion**, and
   **Processes**), Review, ProductFamily, external refs.

Threats/attack-paths attach to elements of **either** layer 1 or 2 (STRIDE-per-element
on the DFD; attack steps traverse structure and networks). Everything is
**deployment/environment-relative** (feasibility & risk, §2).

## 2. Structural layer

- **Composition is recursive:** `composed_of` is a graph — server ⊃ board ⊃ chip ⊃
  core works at any depth, software and hardware alike.
- **Interconnect ≠ containment.** `Interconnect` generalizes to **`Network`**
  (short-range `Bus` — CAN/PCIe/I²C — through LAN **Ethernet** to **WAN/Internet**),
  joined by **`NetworkLink`** (server↔server, with distance / latency / exposure).
  Components connect via `connected_via`; a bus/network is also an `AttackSurface`/
  `TrustBoundary` that `AttackStep`s `pivot_to` across (reaches multiple ECUs/servers).
- **Network services are Components:** `DNS`, gateway, load-balancer, CA. A flow or
  link that relies on one gets `depends_on` → DNS-spoofing / resolver-outage are
  modelable threats on that dependency.
- **Deployment & Environment (per instance, not per build).** `ProductInstance`
  (versioned) → `Deployment` → `Environment`:
  `physical_security` (secure-facility / controlled / unattended-public),
  `connectivity` (air-gapped / LAN / internet-facing), `operational_context`. One
  build → many deployments → **different risk**.
- **AttackSurface / Interface** with `exposure` (internal / external / remote) — the
  "inside vs outside the car" / "locked rack vs phone in pocket" distinction. Referenced
  by `AttackStep.precondition` and by `attack_feasibility`.

**Feasibility & risk are computed relative to the Deployment's Environment and the
exposure of the surfaces an AttackPath uses** (ISO 21434 window-of-opportunity /
CC attack-potential). The same build is high-risk on a phone, low-risk in a locked rack.

## 3. Behavioral layer — data flow / DFD

A classic threat-modeling DFD, over the structural substrate (aligns us with
STRIDE / Threat Dragon / pytm / threagile / OTM — #6/#7/#9):

- **`Process`** — a unit of processing (also a PROV `Activity`, §5).
- **`DataFlow`** — data moving between processes/stores/entities **over** an
  Interconnect/Network, crossing `TrustBoundary`s (where most threats live).
- **`DataStore`** (data at rest) · **`ExternalEntity`** (user / outside system).
- **`Workflow`** — a DAG of Processes + DataFlows.

**Worked case — AI in phone vs AI in secure server, communicating:**
`ExternalEntity(user)` → `Process(phone-side AI)` [Deployment: handheld, exposure
external] → `DataFlow(prompt)` over a `NetworkLink` crossing the phone↔datacenter
`TrustBoundary` → `Process(server inference)` [Deployment: secure-facility] →
`DataFlow(response)`. Two Deployments of (maybe) one model, a channel between, each
element carrying its own threats/exposure.

## 4. Threat & catalog layer (from iteration 2)

Generic catalog authored once (`Weakness` CWE · `AttackPattern` CAPEC/ATT&CK ·
`Mitigation` D3FEND `defends_against` · `ThreatActor` capability · shared `Component`
CPE/purl). Instance overlay per product: `ThreatInstance` `realizes` `DamageScenario`
(S/F/O/P, many-to-many) · `AttackStep` (pre/postconditions) → `AttackPath`
(`attack_feasibility`, cross-product `pivots_to`) · `Finding` (concrete weakness, no
CVE needed) / `Vulnerability` (CVE) · `MitigationInstance` (effectiveness, validity
time) `reduces` a step/path · `RiskScore`. (Unchanged from iter 2 except the
attachment points now include DFD elements.)

## 5. Provenance (PROV-O over nodes, edges, and processes)

- **Edges:** AI-proposed relationships are reified as `Assertion`s carrying
  `confidence` + `Review` verdict + provenance (gates DEC-002/DEC-004 — §10).
- **Processes = PROV Activities.** Processing transforms inputs→outputs:
  - **Compile:** `Process(compile)` `used` source, `wasGeneratedBy`→binary,
    `wasAssociatedWith` toolchain `Agent` — this **is SLSA / in-toto build provenance**
    (GUAC already a library record; reuse, don't reinvent).
  - **AI generation:** `Process(generate)` `used` {prompt, model, context},
    `wasGeneratedBy`→output, `wasAssociatedWith` the model/agent.
- **Provenance of a flow** = the PROV subgraph over the Workflow: the transitive
  `wasDerivedFrom` chain from an output back to its sources (toolchain / prompt /
  model / upstream data). **Shown** as a provenance view in the review console (#10) —
  the same KG, filtered to Activity/Entity/Agent + derivation edges. Doubles as the
  "AI proposes → human reviews" audit trail and the supply-chain trust layer (SLSA).

## 6. Propagation & VEX

- A `Vulnerability`/`Finding` `affects` a shared `Component`; applicability
  **propagates** along `uses_component` and recursively up `composed_of` (a vuln in a
  core carries to chip → board → server → product) — a derived `applies_to` via graph
  traversal, not hand-duplication. Answers *"which products use this vulnerable
  component?"* in one query.
- **VEX stops over-reporting:** a per-instance `vex_status` (`not_affected` / `affected`
  / `fixed` + justification) overrides the propagated applicability — modeled as an
  `Assertion` + `Review` on the propagated edge (OpenVEX/CSAF).
- **External tracking:** `Finding` / `MitigationInstance` / `Review` carry
  `external_refs` (`{system: jira, id, url, status}`) — a codebase issue across three
  products, tracked in Jira, is one query (Finding → shared Component → products +
  external_ref).

## 7. Requirements-coverage matrix (gate)

Existing R-001…R-022 as iteration 2 (R-021 ✅ via time axis; provenance/edge-review ◐
pending reification). New, from the two review rounds:

| req | needs | covered by | status |
|---|---|---|---|
| R-023 | feasibility/risk **relative to deployment environment** (physical security, connectivity, exposure) | Deployment→Environment + AttackSurface.exposure → attack_feasibility/RiskScore | ✅ |
| R-024 | **data-flow modeling** (DFD: processes, flows, stores, external entities, workflows) over structure, crossing boundaries | Process/DataFlow/DataStore/ExternalEntity/Workflow | ✅ |
| R-025 | **process provenance** (compile, AI-generation) captured and shown | Process=PROV Activity + used/wasGeneratedBy/wasAssociatedWith; SLSA/in-toto; provenance view | ◐ (gated on DEC-002/004 reification) |
| R-026 | **network topology** incl. long-distance + service dependencies (DNS) | Network/NetworkLink + service Components + depends_on | ✅ |
| R-027 | **vulnerability/finding propagation** + VEX override | affects + uses_component/composed_of traversal + vex_status Assertion | ✅ |
| R-028 | **external tracker refs** (Jira) on findings/mitigations/reviews | external_refs attribute | ✅ |

## 8. Test suite / vectors (must become `spec/vectors/`)

Iteration-2 cases 1–13, plus:
14. **AI phone↔secure-server flow** — DFD across two Deployments + a NetworkLink crossing a TrustBoundary; threats on the prompt/response flows. → §3.
15. **Server-to-server over a WAN with a DNS dependency** — NetworkLink (long-distance) + `depends_on` DNS service; DNS-spoofing threat on the link. → §2.
16. **Compile / AI-generation provenance** — a built artifact's `wasDerivedFrom` chain back to source+toolchain (SLSA) and a generated output back to prompt+model. → §5.
17. **Deployment-relative risk** — same build, two Deployments (locked rack vs phone), different `attack_feasibility`/risk. → §2.
18. **Vuln carries through core→chip→server but VEX `not_affected` in product X** — propagation + override. → §6.

## 9. MVP scope (ADR-0002) vs. full model

The full model above is the DEC-001 target; the **MVP demonstrates a slice**: the
deep product exercises structure + a small DFD + the attack-path graph + review +
risk; the second-domain product proves generalization. **Networks/DNS, multi-step
AI workflows, and full process provenance are representable now but need only a
minimal demonstration in the MVP** (one flow, one provenance chain) — the rest is
post-demo depth. Audit objects (Requirement/WorkProduct) remain deferred (#19).

## 10. Iteration log & next

- **Iter 1–2:** generic/instance split; adversarial fixes (shared CPE component,
  cross-product paths, step pre/postconditions, time axis, edge reification,
  restored boundary/family/damage/actor/finding).
- **Iter 3 (this):** +structural depth (recursive composition, Interconnect→Network,
  DNS services, Deployment/Environment/exposure); +behavioral DFD layer
  (Process/DataFlow/DataStore/ExternalEntity/Workflow); +process provenance
  (compile/AI-gen = SLSA/in-toto + prompt); +VEX propagation; +external refs
  (Jira). New R-023…R-028; vectors 14–18. (design-log/0003)
- **Iter 4 (next):** fold frameworks (#6) / products (#7) / schema-crosswalk (#9);
  **decide the reification mechanism → DEC-002/DEC-004**; build vectors; then fold the
  matured model into ARCH-0001 §3/§4 and **accept DEC-001 via an ADR**.
