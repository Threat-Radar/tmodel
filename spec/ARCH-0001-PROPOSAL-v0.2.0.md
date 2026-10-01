---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 5)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 5 of the DEC-001 object-model synthesis (#15). Folds the merged frameworks/products research (#6/#7) and three decision analyses: a partial lift of the DFD-standard caveat (method alignment verified, schema alignment still #9), STRIDE generalised to a multi-valued method facet, AND/OR + ordering on attack paths, a substrate-neutral reified-Assertion provenance model (DEC-002/004 logical half), and an ISO 21434-shaped MVP risk metric (DEC-003). Marks ◐→✅* where a direction is now proposed. Proposed, not accepted."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.6"
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
  - role: sponsor-review
    id: paul-lambert
    round: display-redundancy
  - role: research-analysis
    id: agent-iteration-5-frameworks
  - role: research-analysis
    id: agent-iteration-5-reification
  - role: research-analysis
    id: agent-iteration-5-risk
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iteration 5 (DL-0006)
  folds the merged #6/#7 research and three parallel decision analyses (frameworks/DFD,
  reification, risk). It lifts §9 to a partial (method alignment verified; schema alignment
  still owned by #9), generalises STRIDE to a method facet, adds attack-path AND/OR +
  ordering, fixes the provenance model as a substrate-neutral reified Assertion (the logical
  half of DEC-002/DEC-004 — storage stays open behind the Path A/ADR-0003 adapters), and
  specifies an ISO 21434-shaped MVP risk metric (DEC-003). ✅* = proposed direction, accepted
  only when the gating DEC's ADR lands; ◐ = still genuinely open. Unverified library items
  (ISO 21434 Annexes F/G/H, first-cvss, RDF-star) are flagged, not pretended.
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 5)

**Status: proposed (iteration 5).** Iteration 4 reconciled the layers and bounded the MVP;
proposed.5 added the presentation layer + redundancy. Iteration 5 (DL-0006) folds the now-
merged frameworks/products research (#6 RPT-0002, #7 RPT-0003) and three parallel decision
analyses, and **proposes directions** for reification (DEC-002/004) and the risk metric
(DEC-003). **Legend:** ✅ covered · ✅\* proposed direction (accepted only via the gating
DEC's ADR) · ◐ still open.

## 0. One-artifact rule (F1) — how the layers relate

- **`Component` is the authoritative layer** — the deployed artifact that *exists*
  (service, container, dependency, chip, core).
- **DFD elements are behavioral *roles* projected onto Components**, not new things:
  a `Process`/`DataStore` MUST resolve to ≥1 Component via **`realized_by`/`runs_on`/
  `stored_in`**. A `DataFlow` resolves to a `connected_via` path between those
  Components' hosts. When the two disagree, the Component layer wins and the DFD is
  invalid until it resolves. This removes the Component-vs-Process and
  reachability double-modeling.
- **Naming caveat (iter 5, RPT-0003).** OTM and most DFD tools call a *diagram node* a
  "component"; our `Component` is the deployed artifact. The `realized_by` projection has
  **no precedent** in the surveyed tools (they model DFD elements directly, with no
  authoritative artifact layer). The projection stays **our design, provisional** — the OTM
  field-level crosswalk that would confirm or rename it is owned by #9.

## 1. Layers (reconciled)

1. **Structural (authoritative)** — Product/ProductInstance(versioned), Component
   (CPE/purl, shared), `composed_of`, Interconnect/Network/NetworkLink, TrustBoundary
   (a **zone**: elements declare `in_trust_zone`, F12), AttackSurface, Deployment→Environment,
   **RedundancyGroup** (`replica_of`/`redundant_with`, §10).
2. **Behavioral (DFD) — projected onto (1)** — ExternalEntity, Process, DataStore,
   DataFlow, Workflow, each `realized_by` Component(s), with **security properties**
   (authenticated? encrypted? privilege) and **data `classification`** that drive STRIDE.
   The verified element set (entity / process / data store / data flow / trust boundary)
   matches Microsoft TMT and OTM (RPT-0002 §2; RPT-0003) — no rename forced.
3. **Threat & catalog (one vocabulary, F2)** — generic Weakness(CWE)/AttackPattern
   (CAPEC/ATT&CK)/Mitigation(D3FEND)/ThreatActor; instance ThreatInstance (carries a
   **method facet** — §2 — `realizes` DamageScenario), AttackStep(pre/postconditions, AND/OR
   gates, ordering — §2a)/AttackPath (`attack_feasibility`), Finding/Vulnerability,
   MitigationInstance, RiskScore.
4. **Cross-cutting** — **one provenance spine** (F6): PROV-O Entity/Activity/Agent
   nodes + a reified **`Assertion`** node (the substrate-neutral invariant — §4); Review;
   ProductFamily; external refs.
5. **Presentation (derived, transient)** — `View`/`Perspective` specs + rendered
   view-state (geometry, colour, weight, expand state), computed from (1)–(4) and
   **never written back**. A separate visual object model that binds to the domain by
   reference. See §10. This is the UI/console concern (DEC-006 → ADR-0003 Path A), not
   domain truth.

**Reachability is one concept at three levels, not three models:** `connected_via`
(physical/network reachability) → an `AttackStep.precondition` may require it → an
`AttackPath` `pivots_to` across it. DataFlow is the *intended* traffic; AttackStep is
the *adversary* use of the same substrate.

## 2. Threat vocabulary — STRIDE is a *method facet*, not an AttackPattern property (F2 + iter 5)

**Iteration-5 correction (RPT-0002 §2, `sei-threat-modeling-methods-2018`).** STRIDE is a
per-element / per-interaction classification generated by rule over DFD element types — it
is **not** a property of an `AttackPattern`, and the merged research gives **no**
STRIDE↔CWE/CAPEC mapping. So:

- The STRIDE classification is a **facet recorded on the DFD target** (Process, DataStore,
  DataFlow, ExternalEntity). A per-element-type applicability rule *generates candidate*
  `ThreatInstance`s (S→spoofing on entities/processes, T→tampering on flows/stores, … ).
- Each STRIDE category is the **violation of one security property**; add a
  `violates_property` attribute aligned to the DFD element's security properties
  (S↔authentication, T↔integrity, R↔non-repudiation, I↔confidentiality, D↔availability,
  E↔authorization — RPT-0002 §2).
- **Generalise the single `stride` facet to a multi-valued `method_facet`** on
  `ThreatInstance` (values: `stride`, `linddun`, `maestro`, …) plus a `source_method`
  attribute (which method proposed this threat — commercial tools emit all three; RPT-0003
  Devici). LINDDUN is privacy (7 categories over DFD elements; note "non-repudiation" is a
  *threat* in LINDDUN but a *property* in STRIDE — RPT-0002 §5); MAESTRO is the agentic-AI
  layer model (feeds #12).
- The **CWE/CAPEC link is a separate, human-reviewed mapping**, not a property of the facet.
  The STRIDE↔CWE/CAPEC table is **unsupported by the merged research** and **deferred to #9**
  (pytm's catalogue reuses CAPEC — RPT-0002 §2 — a candidate practical source, not a mapping).

One threat list, classifiable by STRIDE/LINDDUN/MAESTRO *and* traceable to BRON where a
human maps it.

## 2a. Attack structure — AND/OR + ordering (iter 5, RPT-0002 §4/§11.2)

An attack is a *set of leaves with structure*, not always a root-to-leaf path (attack
trees/graphs; `schneier-attack-trees-1999`, `mulval`). Add:

- **`AttackStep` combinators** — AND/OR gates between steps (AND = all required; OR =
  alternatives), over the existing pre/postconditions.
- **Ordering** — an explicit `precedes` edge (or order attribute); basic AND is unordered,
  sequence needs it (SAND / Attack Flow).
- **Shared steps** — a step may belong to several `AttackPath`s (the point of an attack
  *graph*).
- **Coarse phase tag** — an optional Kill-Chain phase on `AttackStep`, kept **distinct** from
  the ATT&CK technique: technique = *what* (a tag), kill-chain phase = *coarse order*
  (RPT-0002 §11.2). *Attack Flow's own schema is unverified (not a library record) — flagged.*

This supersedes the iteration-3 "ordered set of steps" with explicit structure and defines
**R-031** (workflow/attack ordering).

## 3. Structure, networks, deployment, and the risk metric

Recursive `composed_of`; Interconnect→Network/NetworkLink (bus→Ethernet→WAN); DNS/
services as Components + `depends_on`. **Environment is a first-class, reusable node**
(F9): `ProductInstance` 1→N `Deployment`, each →1 `Environment`
(physical_security/connectivity/operational_context, enum-typed).

**Risk metric (iter 5 — proposes DEC-003 direction).** Adopt an **ISO/SAE 21434-shaped
skeleton `Risk = M(Impact, Feasibility)`** with the **Feasibility term instantiated by CVSS
(base + environmental)** for the MVP and the **Impact term supplied by the human S/F/O/P
judgement** — *not* a composite running two schemes in parallel (that is the F5 double-count
ban). This is the §7 MVP line "CVSS-env + human impact", specified:

- **Per-step feasibility `f_i`** on 21434's 4-point scale (Table 1, `iso-sae-21434-2021#RQ-15-10`):
  from the exploited `Vulnerability`'s CVSS exploitability/base where a CVE exists, else a
  human enum. CVSS-as-feasibility is a 21434-**sanctioned** method (`#RC-15-11`(b)).
- **Path feasibility** `F = min f_i` along an AND-chain (hardest step is the bottleneck),
  `max` over OR-alternatives (uses §2a).
- **Impact `I`** from the terminal `DamageScenario`: human rates **S/F/O/P** severe/major/
  moderate/negligible (`#RQ-15-04/05`; safety ← ISO 26262 `#RQ-15-06`); keep the category
  vector, scalar `I = max`.
- **`RiskScore = M(I, F)`** via a small 21434-style ordinal matrix (`#RQ-15-15/16`).

**Environment + AttackSurface.exposure parameterise the *feasibility term only*** (F5 — no
post-hoc adjustment on `R`): exposure → CVSS Attack-Vector of the entry step; connectivity →
gates reachability-dependent steps; physical_security → window-of-opportunity gate;
operational_context → CVSS environmental CIA modifiers. Attacker position relative to a
Network is an `AttackStep` precondition type (F10). *Human impact is the human's input; the
machine proposes the path + feasibility (CLAUDE.md: no AI path is reviewed until a human
owns it).* **Caveat:** ISO 21434 Annexes F (impact criteria) and G/H (feasibility methods)
are **not distilled** in the library, and `first-cvss` is a **stub** — both backlogged
(T-029 family) before implementation; the full-TARA extension is post-MVP (§11).

**Redundancy is a relationship, not just two deployments** (R-034). A `RedundancyGroup`
(`replica_of`/`redundant_with`) marks `Deployment`s or whole build/review systems as replicas
of one function → redundancy-as-availability-mitigation, **common-mode risk** (a shared
`Component`/CWE compromises *all* replicas at once), and per-replica mitigation divergence
(R-020). Full treatment + the two-location compare scenario are in §10.

## 4. Provenance — one spine, a substrate-neutral reified Assertion (iter 5 — proposes DEC-002/004 logical half)

PROV-O is the node model (Entity/Activity/Agent + used/wasGeneratedBy/wasDerivedFrom/
wasAssociatedWith; `prov-o`, RPT-0011 §2). **The logical reification invariant is a reified
`Assertion` node** — because the "AI proposes → a human accepts, recorded" rule makes edge
metadata *n-ary and point-at-able* (an Activity generates it; ≥0 `Review` nodes point back at
it; confidence attaches; successive verdicts accumulate). Only a **node** can be the target of
further statements. The four candidate mechanisms (RDF-star, named graphs, reified node, LPG
edge-properties) are therefore **physical lowerings the storage adapter chooses, not the
model**:

- **RDF adapter** → classic `rdf:Statement` reification, *or* RDF-star + annotation, *or* a
  per-assertion named graph — same logical fields.
- **LPG adapter** → an edge-with-properties for the trivial case, **promoted to a reified
  intermediate node the moment the assertion must be pointed at** (always, under the review
  rule).

This **survives DEC-004 staying open** (Path A/ADR-0003 keeps the substrate behind a façade):
the façade exposes one `Assertion { reified (s,p,o); provenance → Activity + Agent;
confidence; review_state; → ≥0 Review }` contract regardless of store. **SHACL is the
acceptance gate** (`shacl`, RPT-0011 §5/§6): a shape "every `Assertion` MUST carry provenance
+ a review status before `status=accepted`". The human verdict is a `Review` node (STIX
**Opinion/Note** maps directly, `stix-2-1`), kept **separate from the proposal** (proposal and
verdict coexist).

**AI-generation provenance** (prompt→output) stays in-model. **Compile/SLSA build provenance
moves to the radar→tmodel contract** (ADR-0001) — out of the MVP core (F7); SLSA/in-toto
equivalence vs `in-toto-attestation-v1`/`guac` remains ◐. *Unverified: RDF-star / SPARQL-star
/ SHACL-over-RDF-star have **no library record** (grep-confirmed) — gather one before the
DEC-002 serialization sub-decision; `prov-o`/`shacl`/`stix-2-1`/`rdf-1-1-concepts` are
`summarized` only.*

## 5. Propagation, VEX, mitigation & review (F8 + iter 5)

Vulnerability/Finding propagation along `uses_component`/`composed_of` is sound (✅). The
per-instance **VEX override** is an `Assertion` whose subject is the propagated (vuln,
component-instance) edge, carrying the VEX status/justification, pointing at its generating
Activity + a `Review` — concrete and substrate-neutral per §4, so **R-027b → ✅\***.

**Enrich `MitigationInstance` and `Review`** (RPT-0003 SD Elements / TMT): a mitigation needs
an **implementation owner, a linked work item (`external_refs`/Jira), verification evidence,
and status**; a Review carries status/priority/justification and keeps **proposal and verdict
separate**. The OTM semantic round-trip test (must carry review + provenance + ordered paths)
is the **CF-008 acceptance test for DEC-002** (owned by #9). External refs (Jira) unchanged.

## 6. Requirements-coverage matrix — honest (iter 5)

R-001…R-022 as before, with these corrections and additions
(✅\* = proposed, accepted via the gating DEC's ADR):

| req | covered by | status |
|---|---|---|
| R-023 (deployment-relative risk) | ISO 21434-shaped metric; Environment/exposure parameterise feasibility (§3) | ✅\* at MVP (proposes DEC-003); multi-deployment post-MVP |
| R-024 (data-flow / DFD) | Process/DataFlow/… projected via realized_by + security properties + classification | ◐ (schema crosswalk #9) |
| R-025 (process provenance) | PROV-O + substrate-neutral Assertion; SHACL gate (§4) | ✅\* mechanism (proposes DEC-002/004); provenance **view** #10 post-MVP |
| R-026 (network topology) | Network/NetworkLink + service depends_on | ✅ |
| R-027a (vuln propagation) | traversal of uses_component/composed_of | ✅ |
| R-027b (VEX override) | Assertion+Review on propagated edge (§4/§5) | ✅\* (proposes DEC-002/004) |
| R-028 (external refs / Jira) | external_refs on Finding/MitigationInstance/Review | ✅ |
| R-029 (data classification) | `classification` on DataStore/DataFlow/Asset | ✅ |
| R-031 (attack/workflow ordering) | AND/OR gates + `precedes` on AttackStep (§2a) | ✅\* (new mechanism; vectors pending) |
| R-032 (entity/agent trust) | trust level on ExternalEntity + PROV Agent | ◐ |
| R-033 (presentation/view layer) | View/Perspective + transient view-state (§10) | ◐ (MVP = one graph projection) |
| R-034 (redundancy / common-mode) | RedundancyGroup/replica_of (§3/§10) | ◐ (post-MVP) |
| R-035 (compare / diff) | compare projection over two subgraphs (§10) | ◐ (post-MVP) |

Iter-5 deltas: R-023/R-025/R-027b/R-031 → ✅\* (directions proposed for DEC-002/003/004);
R-024 stays ◐ on #9. The STRIDE↔CWE/CAPEC mapping remains **unasserted** (§2).

## 7. MVP / post-MVP split (F3) — *the scope gate*

ADR-0002 accepted an **attack-path knowledge graph** (Option A), not a DFD/STRIDE tool.
The model expresses more than the MVP builds; this table is binding for Nov 5.

| object / capability | MVP (Nov 5) | post-MVP |
|---|---|---|
| Product/ProductInstance, Component(CPE/purl)+composition | ✅ build | |
| BRON backbone: Weakness/AttackPattern/Vulnerability/Finding | ✅ build | |
| ThreatInstance / AttackStep / AttackPath (+feasibility, AND/OR, ordering) | ✅ build | |
| Review + substrate-neutral Assertion provenance of AI-proposed nodes/edges | ✅ build (minimal) | |
| **RiskScore** = ISO 21434 `M(Impact, Feasibility)`; CVSS feasibility + human S/F/O/P | ✅ build | full-TARA (Annex F/G/H) |
| generic↔instance mapping, ≥2 domains/instance types | ✅ build | |
| full **DFD layer** (Process/DataFlow/DataStore/ExternalEntity/Workflow) | *one illustrative flow only* | ✅ post-MVP |
| **method facets** beyond STRIDE (LINDDUN/MAESTRO) | — | ✅ post-MVP |
| **Network/NetworkLink/DNS** topology | — | ✅ post-MVP |
| **Deployment/Environment/exposure** (multi-deployment risk) | *single deployment assumed* | ✅ post-MVP |
| **compile/SLSA build provenance** | — (radar contract) | ✅ post-MVP |
| **VEX** override | — | ✅ post-MVP |
| **Jira external_refs**, audit (Requirement/WorkProduct) | — | ✅ post-MVP (#19) |
| **interactive graph view** (force layout, type colours, click-expand/inspect, progressive load) | ✅ build (one projection) | matrix/timeline/compare, saved views, layer/tag compositing |
| **redundancy / common-mode / compare** (RedundancyGroup, diff projection) | — | ✅ post-MVP |

**The MVP is the attack-path KG.** Students build the top block; DFD/networks/
provenance are modeled but **not built** for Nov 5 (at most one illustrative flow +
one AI-gen provenance chain, if time).

## 8. Vectors (must become `spec/vectors/`)

MVP vectors 1–6 + 18 (vuln-carry) first, now including: an **AND/OR attack path with
ordering** (§2a), a **RiskScore computation** exercising CVSS-feasibility × S/F/O/P impact
with an Environment parameter (§3), and an **Assertion+Review** round-trip (§4). Post-MVP
vectors 7–17 (DFD, networks, provenance view, env-relative risk, compare) follow.

## 9. DFD-standard alignment — *partial lift* (iter 5, RPT-0002/RPT-0003)

**Method-level alignment is verified** (RPT-0002): STRIDE, attack trees, PASTA, Trike,
LINDDUN, ATT&CK, Kill Chain are backed by library records (`sei-threat-modeling-methods-2018`,
`schneier-attack-trees-1999`, `trike-v1-2005`, `deng-linddun-2011`, `mitre-attack`,
`lockheed-kill-chain-2011` — *subject to a submodule-pin re-check; several ids were not in
the pinned checkout*). This supports §2 (facets), §2a (structure), §3 (feasibility).

**Schema-level alignment is NOT verified and stays owned by #9.** RPT-0003 describes OTM /
threagile / pytm / Threat Dragon from vendor & repo docs only — "**none of the products were
acceptance-tested**", the sources are not yet library records (#P1), and there is **no neutral
round-trip**. Threat Dragon itself declares incompatibility with pytm/threagile/OTM (TM-BOM is
its successor direction). So the field-level crosswalk, the `Component`↔OTM-"component" rename
check, round-trip loss tests, TM-BOM, and whether OTM can carry `RedundancyGroup`/`Assertion`/
ordered paths/layout **remain #9 + DEC-002**. *(Also unresolved there: pytm licence — RPT-0002
says MIT, RPT-0003 says GPL-3.0.)* OTM carries **layout**; our §10 "view-state never written
back" is stricter than any tool — the interchange must carry or drop layout (DEC-002).

## 10. Presentation / view layer & redundancy (sponsor display round)

The display is a **derived lens, not domain truth.** It is a fifth, UI-facing concern
(§1.5) computed from the four domain layers and never stored back onto them. This is the
substance of DEC-006 (→ ADR-0003, Path A); the *product* requirements (platform, performance,
licensing, CLI) live in **APP-0001**.

- **`View` / `Perspective` (spec; persisted or transient).** A named lens = *a query/
  filter over the KG + a projection type + layer/tag composition + layout + styling*.
  Saved views are reviewable artifacts with provenance; ad-hoc exploration is transient.
- **Rendered view-state (transient).** Node geometry, colour, size, focus "gravity"/
  weight, expand/collapse, cluster membership — computed per session, optionally cached or
  exported to a viz engine, **never written to domain nodes**. The **visual object model is
  separate** from the domain and binds to it by reference.
- **Projections over one graph**: node-link **graph**, **threat × mitigation matrix**,
  **attack-path / tree**, **DFD**, **timeline**, **provenance**, and **compare / diff**.
- **Scale — progressive loading (R-033).** The View is a *bounded query*, so the UI never
  loads the whole KG: open from a focus node/filter, expand lazily on demand (expand-on-click,
  paged neighbourhoods, LOD collapse of `composed_of` subtrees); clustering + roll-up keep
  large graphs legible.
- **Layers / tags as composable overlays (R-033).** Any tag/type/trust-zone/domain/MVP marker
  is a toggle-able overlay a View composites — named, independently toggled filter sets over
  the one graph, not separate graphs.
- **Dynamic behaviour (R-033).** Force-directed physics; per-type/-facet **unique colours**;
  **click to open containment** (`composed_of`) or **inspect** (detail + provenance + review).

**Redundancy & the two-location compare (R-034/R-035).** Two locations = two `Deployment`s of
one `ProductInstance`/`Workflow`, each → its `Environment` (§3). *An AI code-review on a secure
server in two distinct locations, then compare* is representable once (a) `RedundancyGroup`
marks them replicas (common-mode + divergence) and (b) a **compare/diff projection** shows
same-vs-different threats/mitigations (and, via §4 provenance, which model/version produced
each). **Scope:** one interactive graph projection is MVP; matrix/compare/saved-views/layers
and redundancy are post-MVP (§7).

## 11. Iteration log & next

- **Iter 1–3:** split, adversarial fixes, three layers.
- **Iter 4:** reconcile layers (one-artifact rule), unify threat vocabulary + provenance,
  honest matrix, MVP/post-MVP table, compile/SLSA → radar (F1–F13; DL-0004).
- **proposed.5:** sponsor display/redundancy round (DL-0005): presentation layer + redundancy
  (§10, R-033/034/035); app requirements → APP-0001; stack → DEC-010/ADR-0003.
- **Iter 5 (this, DL-0006):** fold #6/#7; **partial lift of §9** (method verified, schema #9);
  STRIDE → multi-valued **method facet** (§2); attack-path **AND/OR + ordering** (§2a);
  **substrate-neutral reified Assertion** provenance (§4, proposes DEC-002/004 logical half);
  **ISO 21434-shaped MVP risk metric** (§3, proposes DEC-003); enriched mitigation/review (§5).
  ◐→✅\* on R-023/025/027b/031. Backlog: distill ISO 21434 Annexes F/G/H + a real `first-cvss`;
  gather an RDF-star record (DEC-002).
- **Iter 6 (next):** run the **adversarial-critic** pass on this; fold #9 (schema crosswalk)
  when it lands to close R-024 and lift §9 fully; **build the §8 MVP vectors**; then the
  sponsor accepts via ADRs — **DEC-003** (risk) and the **DEC-002/004 reification logical
  model** are ADR-ready now; **DEC-001** (whole object model) accepts last, folding this into
  ARCH-0001 §3/§4.

## 12. Ready for ADR acceptance (sponsor calls)

Proposed directions that are ADR-ready this iteration (each accepted **only** by an ADR +
changelog + ARCH-0001 status update, per CLAUDE.md):

- **DEC-003 (risk metric)** — the ISO 21434-shaped `M(Impact, Feasibility)` with CVSS
  feasibility (§3). Caveat: full-TARA annexes undistilled (post-MVP).
- **DEC-002/DEC-004 (logical reification)** — the substrate-neutral `Assertion`/`Review`/
  PROV-O model with the SHACL gate (§4). Note: this is the **logical** half; the RDF-vs-LPG
  *storage* pick (DEC-004) and the *serialization* pick (DEC-002) stay open behind the Path A
  adapters until an RDF-star record is gathered and #9 lands.
- **DEC-001 (object model)** — accept last, after the iteration-6 critic + MVP vectors.
