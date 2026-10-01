---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 5, critic-folded)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 5 of the DEC-001 object-model synthesis (#15), with the iteration-6 adversarial critic folded in (DL-0007). Folds merged frameworks/products research (#6/#7) and three decision analyses: a partial lift of the DFD-standard caveat, STRIDE as a multi-valued method facet, AND/OR + ordering on attack paths, a substrate-neutral reified-Assertion provenance model, and an ISO 21434-shaped MVP risk metric. The critic pass corrected the risk metric (feasibility ≠ CVSS-base), the SHACL gate (substrate-neutral), R-023 scope, and over-claims. Proposed, not accepted — and not yet ADR-ready (§12)."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.7"
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
  - role: adversarial-critic
    id: agent-iteration-6
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-PROPOSAL-v0.2.0.md
proposes: DEC-001
defers_to: ARCH-0001
agent_notes: >
  Proposes against ARCH-0001 §3/§4 — not a parallel model (§9.4). Iteration 5 (DL-0006) folded
  #6/#7 + three decision analyses; proposed.7 folds the iteration-6 adversarial critic (DL-0007,
  14 findings). Corrections: the MVP risk metric is path-level 4-point feasibility × per-category
  S/F/O/P (NO CVSS at MVP; CVSS as a post-MVP refinement uses exploitability metrics only, per
  ISO 21434 RC-15-13); the acceptance gate is stated substrate-neutrally (SHACL on RDF OR
  equivalent LPG checks) and the node-reification commitment is admitted to narrow — not leave
  fully open — DEC-004; R-023 is post-MVP; "method alignment verified" softened (draft RPT-0002,
  records not yet pinned). ADR-0003 (Path A, DEC-006/010) is IN REVIEW (#48), not accepted — the
  substrate-neutrality argument no longer leans on it. ✅ covered · ✅* proposed, ADR-gated · ◐ open.
  Not yet ADR-ready (§12): pin method records, get a reviewed ISO 21434 extraction, gather an
  RDF-star record first.
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 5, critic-folded)

**Status: proposed (iteration 5, proposed.7).** Iteration 4 reconciled the layers; proposed.5
added the presentation layer + redundancy; proposed.6 folded #6/#7 + three decision analyses;
**proposed.7 folds the iteration-6 adversarial critic (DL-0007)**, which corrected the risk
metric, the provenance gate, and several over-claims. **Legend:** ✅ covered · ✅\* proposed
direction (accepted only via the gating DEC's ADR) · ◐ still open. **These are *proposed*
requirements — several (R-023…R-032) are not yet in ARCH-0001 §4** (L13).

> **Dependency note (H1).** DEC-006/DEC-010 (the stack) are proposed in **ADR-0003 — Path A,
> currently in review (PR #48), *not yet accepted***. This proposal references Path A only as a
> pending direction; no argument here *depends* on it (the §4 substrate-neutrality stands on the
> logical model alone). If #48 is revised or rejected, only the "realised by Path A" asides change.

## 0. One-artifact rule (F1) — how the layers relate

- **`Component` is the authoritative layer** — the deployed artifact that *exists*
  (service, container, dependency, chip, core).
- **DFD elements are behavioral *roles* projected onto Components**: a `Process`/`DataStore`
  MUST resolve to ≥1 Component via **`realized_by`/`runs_on`/`stored_in`**; a `DataFlow`
  resolves to a `connected_via` path. When the two disagree the Component layer wins. Removes
  the Component-vs-Process and reachability double-modeling.
- **Naming caveat (RPT-0003).** OTM and most DFD tools call a *diagram node* a "component";
  our `Component` is the deployed artifact. The `realized_by` projection has **no precedent** in
  the surveyed tools (they model DFD elements directly) — it stays **our design, provisional**;
  the OTM field-level crosswalk that confirms or renames it is owned by #9.

## 1. Layers (reconciled)

1. **Structural (authoritative)** — Product/ProductInstance(versioned), Component (CPE/purl,
   shared), `composed_of`, Interconnect/Network/NetworkLink, TrustBoundary (a **zone**:
   `in_trust_zone`, F12), AttackSurface, Deployment→Environment, **RedundancyGroup**
   (`replica_of`/`redundant_with`, §10).
2. **Behavioral (DFD) — projected onto (1)** — ExternalEntity, Process, DataStore, DataFlow,
   Workflow, each `realized_by` Component(s), with **security properties** (authenticated?
   encrypted? privilege) and **data `classification`**. Verified element set matches Microsoft
   TMT and OTM (RPT-0002 §2; RPT-0003).
3. **Threat & catalog (one vocabulary, F2)** — generic Weakness(CWE)/AttackPattern(CAPEC/
   ATT&CK)/Mitigation(D3FEND)/ThreatActor; instance ThreatInstance (carries a **method facet**,
   §2, `realizes` DamageScenario), AttackStep (pre/postconditions, AND/OR gates, ordering — §2a)/
   AttackPath (`attack_feasibility`), Finding/Vulnerability, MitigationInstance, RiskScore.
4. **Cross-cutting** — **one provenance spine** (F6): PROV-O Entity/Activity/Agent + a reified
   **`Assertion`** node (the substrate-neutral invariant — §4); Review; ProductFamily; external refs.
5. **Presentation (derived, transient)** — `View`/`Perspective` specs + rendered view-state,
   computed from (1)–(4) and **never written back**; a separate visual object model binding to the
   domain by reference (§10). The UI/console concern (DEC-006; proposed in ADR-0003, #48), not
   domain truth.

**Reachability is one concept at three levels:** `connected_via` → an `AttackStep.precondition`
may require it → an `AttackPath` `pivots_to` across it. DataFlow is the *intended* traffic;
AttackStep is the *adversary* use of the same substrate.

## 2. Threat vocabulary — STRIDE is a *method facet*, not an AttackPattern property

**(RPT-0002 §2, `sei-threat-modeling-methods-2018`.)** STRIDE is a per-element classification
generated by rule over DFD element types — **not** a property of an `AttackPattern`, and the
merged research gives **no** STRIDE↔CWE/CAPEC mapping. So:

- The STRIDE classification is a **facet recorded on the DFD target** (Process/DataStore/
  DataFlow/ExternalEntity); a per-element-type rule *generates candidate* `ThreatInstance`s.
- Each category is the **violation of one security property** → a `violates_property` attribute
  (S↔authentication, T↔integrity, R↔non-repudiation, I↔confidentiality, D↔availability,
  E↔authorization — RPT-0002 §2, checks out).
- **Generalise `stride` to a multi-valued `method_facet`** (stride/linddun/maestro) + a
  `source_method` attribute (which method proposed it). LINDDUN = privacy (note non-repudiation
  is a *threat* in LINDDUN but a *property* in STRIDE — RPT-0002 §5); MAESTRO = agentic-AI (#12).
  *The LINDDUN/MAESTRO library records are **not yet pinned** (L15); facets beyond STRIDE are
  post-MVP (§7).*
- The **CWE/CAPEC link is a separate, human-reviewed mapping**, not a facet property. The
  STRIDE↔CWE/CAPEC table is **unasserted** (no source) and **deferred to #9** (pytm's catalogue
  reuses CAPEC — a candidate practical source, not a mapping).

## 2a. Attack structure — AND/OR + ordering (RPT-0002 §4/§11.2)

An attack is a *set of leaves with structure* (attack trees/graphs; `schneier-attack-trees-1999`,
`mulval` — present at the pin). Add: **`AttackStep` AND/OR gates**; explicit **`precedes`**
ordering; **shared steps** across paths (the point of an attack *graph*); and an optional
**Kill-Chain phase** tag kept **distinct** from the ATT&CK technique (technique = *what*, phase =
*coarse order*). Defines **R-031**. *The kill-chain record (`lockheed-kill-chain-2011`) and an
Attack Flow record are **not yet pinned** — ingest before relying on the phase tag (L14).*

## 3. Structure, networks, deployment, and the risk metric

Recursive `composed_of`; Interconnect→Network/NetworkLink; DNS/services as Components +
`depends_on`. **Environment is a first-class, reusable node** (F9): `ProductInstance` 1→N
`Deployment`, each →1 `Environment` (physical_security/connectivity/operational_context).

### Risk metric (proposes DEC-003 — corrected by the critic pass)

**MVP metric (simple, per ADR-0002 "a simple risk score reflecting the review"):**
`RiskScore = M(Impact, Feasibility)`, an ISO 21434-*shaped* impact×feasibility matrix
(`iso-sae-21434-2021#RQ-15-15/16`, Annex H), where:

- **Feasibility `F` is rated at the *attack-path level*** on 21434's 4-point scale (High/Medium/
  Low/Very-low), per **Table 1 / `#RQ-15-10`** (which rates the *path*, not the step) — **human-
  rated for the MVP**, optionally informed by the attack-potential core factors (`#RC-15-12`).
  **No CVSS and no per-step aggregation at MVP** (M7, H5).
- **Impact `I` is per-category S/F/O/P** (severe/major/moderate/negligible; `#RQ-15-04/05`;
  safety ← ISO 26262 `#RQ-15-06`), **human-supplied**. 21434 determines a risk value *per
  category* (Annex H.9), so **keep the category vector**; any single-number collapse (e.g. `max`)
  is an explicit **display** simplification, not the method (M12).

**Environment/exposure parameterise *feasibility only*, and only its exploitability side** (F5
double-count ban, tightened by H2): exposure/connectivity/physical_security feed **attack vector,
reachability, and window-of-opportunity** — **never confidentiality/integrity/availability
(impact)**. **Deployment-relativity (R-023) is post-MVP** (single deployment assumed at MVP —
§7); the MVP metric runs without an Environment node (H3).

**Post-MVP refinements (attributed honestly):**
- A **CVSS-driven feasibility** option — when used, from the **CVSS exploitability metrics only
  (AV/AC/PR/UI)** per **`#RC-15-13`**, *never* CVSS base or environmental CIA (those carry impact
  → the double-count H2). Gated on distilling `first-cvss` (a stub).
- **Per-step feasibility with AND/OR aggregation** (`F=min` on an AND-chain, `max` over OR) is
  **attack-tree cost-propagation** (`schneier-attack-trees-1999`, `mulval`), a deliberate
  deviation from 21434's path-level rating — not Table 1 (H5).
- **Multi-deployment, Environment-relative risk** (completes R-023) → enables the two-location
  compare (R-035).

**Caveat (M10, corrected):** the ISO 21434 TARA clause-15 material + Annex H are **extracted but
`not-reviewed`** (`distilled/requirements.yaml` `audit_status: not-reviewed`, with OCR spillover
in `#RQ-09-03`) — a human pass is required before an ADR cites specific anchors. `first-cvss` and
`iso-iec-18045` are stubs.

### Redundancy (R-034)
A `RedundancyGroup` (`replica_of`/`redundant_with`) marks `Deployment`s or whole build/review
systems as replicas → redundancy-as-availability-mitigation, **common-mode risk** (a shared
`Component`/CWE compromises *all* replicas), and per-replica mitigation divergence (R-020). Full
treatment + the two-location compare are in §10.

## 4. Provenance — one spine, a substrate-neutral reified Assertion (proposes DEC-002/004 logical half)

PROV-O is the node model (`prov-o`, RPT-0011 §2). **The logical reification invariant is a reified
`Assertion` node** — the "AI proposes → a human accepts, recorded" rule makes edge metadata
*n-ary and point-at-able* (an Activity generates it; ≥0 `Review` nodes point at it; confidence
attaches; verdicts accumulate), and only a **node** can be the target of further statements.

**Substrate-neutrality — and its honest limit (H4).** An `Assertion` is "a node + edges," which
*every* substrate represents (RDF triples, an LPG reification node, a relational row), so the
model does **not** pick RDF vs LPG. **But committing to node-reification whenever an assertion
must be pointed at (i.e. for every reviewed assertion) *narrows* DEC-004: it forecloses a
pure edge-property-only representation.** That is a logical commitment, stated plainly — not a
claim that DEC-004 stays *fully* open. The four mechanisms (RDF-star, named graphs, reified node,
LPG edge-properties) are the **storage lowerings** of this one logical node:
- **RDF adapter** → `rdf:Statement` reification, RDF-star + annotation, or a per-assertion named graph.
- **LPG adapter** → an edge-with-properties for the trivial un-pointed-at case, **promoted to a
  reified node** the moment it is reviewed.

**Acceptance gate — stated substrate-neutrally (H4):** *a validation step enforces "every
`Assertion` carries provenance + a review status before `status=accepted`"* — realised as **SHACL
on RDF, or equivalent constraint checks on LPG** (openCypher/GQL constraints). SHACL is the RDF
*realisation*, not the gate itself. The human verdict is a `Review` node (STIX **Opinion/Note**,
`stix-2-1`), kept **separate from the proposal**.

**AI-generation provenance** (prompt→output) stays in-model. **Compile/SLSA build provenance** →
radar→tmodel contract (ADR-0001), out of MVP (F7); SLSA/in-toto equivalence vs
`in-toto-attestation-v1`/`guac` remains ◐. *Unverified: RDF-star / SPARQL-star / SHACL-star have
**no library record** (grep-confirmed); `prov-o`/`shacl`/`stix-2-1`/`rdf-1-1-concepts` are
`summarized` only — so the logical model is proposed, **not yet ADR-ready** (§12).*

## 5. Propagation, VEX, mitigation & review (F8 + iter 5)

Vuln/Finding propagation along `uses_component`/`composed_of` is sound (✅). The per-instance
**VEX override** is an `Assertion` on the propagated (vuln, component-instance) edge + a `Review`
— concrete and substrate-neutral per §4, so **R-027b → ✅\***.

**Enrich `MitigationInstance` and `Review`** (RPT-0003 SD Elements / TMT): a mitigation needs an
**implementation owner, a linked work item (`external_refs`/Jira), verification evidence, and
status**; a Review carries status/priority/justification and keeps **proposal and verdict
separate**. The OTM semantic round-trip (must carry review + provenance + ordered paths) is the
**CF-008 acceptance test for DEC-002** (owned by #9).

## 6. Proposed requirements-coverage matrix (several not yet in ARCH-0001 §4 — L13)

R-001…R-022 as ratified; the rows below are **proposed** (R-023–R-032 appear only here; R-033–035
flagged in the CHANGELOG as proposed). ✅\* = proposed direction, ADR-gated.

| req | covered by | status |
|---|---|---|
| R-023 (deployment-relative risk) | Environment/exposure parameterise feasibility (§3) | ◐ **post-MVP** (single deployment at MVP) |
| R-024 (data-flow / DFD) | Process/DataFlow/… projected via realized_by + classification | ◐ (schema crosswalk #9) |
| R-025 (process provenance) | PROV-O + substrate-neutral Assertion; validation gate (§4) | ✅\* mechanism (firm minimal MVP); provenance **view** #10 post-MVP |
| R-026 (network topology) | Network/NetworkLink + service depends_on | ✅ |
| R-027a (vuln propagation) | traversal of uses_component/composed_of | ✅ |
| R-027b (VEX override) | Assertion+Review on propagated edge (§4/§5) | ✅\* |
| R-028 (external refs / Jira) | external_refs on Finding/MitigationInstance/Review | ✅ |
| R-029 (data classification) | `classification` on DataStore/DataFlow/Asset | ✅ |
| R-031 (attack/workflow ordering) | AND/OR gates + `precedes` on AttackStep (§2a) | ✅\* (soundest; records to pin) |
| R-032 (entity/agent trust) | trust level on ExternalEntity + PROV Agent | ◐ |
| R-033 (presentation/view layer) | View/Perspective + transient view-state (§10) | ◐ (MVP = one graph projection) |
| R-034 (redundancy / common-mode) | RedundancyGroup/replica_of (§3/§10) | ◐ (post-MVP) |
| R-035 (compare / diff) | compare projection over two subgraphs (§10) | ◐ (post-MVP) |

Iter-5+critic deltas: R-025/R-027b/R-031 → ✅\*; **R-023 moved to post-MVP** (was ✅\*, H3);
STRIDE↔CWE/CAPEC remains unasserted (§2).

## 7. MVP / post-MVP split (F3) — *the scope gate*

ADR-0002 accepted an **attack-path knowledge graph** (Option A). Binding for Nov 5:

| object / capability | MVP (Nov 5) | post-MVP |
|---|---|---|
| Product/ProductInstance, Component(CPE/purl)+composition | ✅ build | |
| BRON backbone: Weakness/AttackPattern/Vulnerability/Finding | ✅ build | |
| ThreatInstance / AttackStep / AttackPath (+feasibility, AND/OR, ordering) | ✅ build | |
| Review + substrate-neutral Assertion provenance of AI-proposed nodes/edges | ✅ build (minimal, **firm** — not "if time") | provenance **view** |
| **RiskScore** = `M(per-category S/F/O/P, path-level 4-point feasibility)`, **human-rated, no CVSS** | ✅ build | CVSS-feasibility; per-step aggregation; full-TARA annexes |
| **MitigationInstance + mitigation-state visible** (ADR-0002 demo) | ✅ build (minimal) | owner/work-item/verification enrichment |
| generic↔instance mapping, ≥2 domains/instance types | ✅ build | |
| full **DFD layer** (Process/DataFlow/DataStore/ExternalEntity/Workflow) | *one illustrative flow only* | ✅ post-MVP |
| **method facets** beyond STRIDE (LINDDUN/MAESTRO) | — | ✅ post-MVP |
| **Network/NetworkLink/DNS** topology | — | ✅ post-MVP |
| **Deployment/Environment/exposure** (→ R-023 relativity) | — (*single deployment assumed*) | ✅ post-MVP |
| **compile/SLSA build provenance** | — (radar contract) | ✅ post-MVP |
| **VEX** override | — | ✅ post-MVP |
| **Jira external_refs**, audit (Requirement/WorkProduct) | — | ✅ post-MVP (#19) |
| **interactive graph view** — *one working projection* (force layout, type colours, click-expand/inspect, progressive load) — **gated on the stack ADR (DEC-006/010, #48) landing first** | ✅ build (working, not yet "best-in-class" A-042) | best-in-class bar; matrix/timeline/compare; saved views; layer/tag compositing |
| **redundancy / common-mode / compare** (RedundancyGroup, diff projection) | — | ✅ post-MVP |

**The MVP is the attack-path KG.** DFD/networks/Environment are modeled but **not built** for
Nov 5 (at most one illustrative flow). The interactive view is a **working single projection**
contingent on the stack decision (#48) merging first (M8); the "best-in-class" bar (APP-0001
A-042) is post-MVP.

## 8. Vectors (must become `spec/vectors/`)

MVP vectors 1–6 + 18 first, now including: an **AND/OR attack path with ordering** (§2a); a
**RiskScore computation** = path-level 4-point feasibility × per-category S/F/O/P, **no Environment
parameter** (that's post-MVP, H3); and an **Assertion+Review** round-trip (§4). Post-MVP vectors:
Environment-relative risk, CVSS feasibility, DFD/networks, provenance view, compare.

## 9. DFD-standard alignment — *partial lift* (RPT-0002/RPT-0003)

**Method-level alignment is asserted by the draft RPT-0002 (`reviewed: false`), not yet by pinned
records (M6).** Of the cited records (`sei-threat-modeling-methods-2018`, `schneier-attack-trees-
1999`, `trike-v1-2005`, `deng-linddun-2011`, `mitre-attack`, `lockheed-kill-chain-2011`) **only
`mitre-attack` is present at the pin; the other five are absent** — ingest/pin them before any ADR
relies on this. The alignment supports §2 (facets), §2a (structure), §3 (feasibility) *as a draft
direction*.

**Schema-level alignment is NOT verified and stays owned by #9.** RPT-0003 describes OTM /
threagile / pytm / Threat Dragon from vendor & repo docs only — "**none acceptance-tested**",
sources not yet library records (#P1), no neutral round-trip; Threat Dragon declares
incompatibility with the others (TM-BOM is its successor). The field crosswalk, the `Component`↔
OTM-"component" rename check, round-trip loss tests, TM-BOM, layout interchange (OTM carries
layout; our §10 "never written back" is stricter), and the pytm licence conflict (MIT vs GPL-3.0)
**remain #9 + DEC-002**.

## 10. Presentation / view layer & redundancy (sponsor display round)

The display is a **derived lens, not domain truth** — a fifth, UI-facing concern (§1.5) computed
from the four domain layers and never stored back. DEC-006 (proposed in ADR-0003, #48); product
requirements live in **APP-0001**.

- **`View`/`Perspective` (spec; persisted or transient)** = query/filter + projection + layer/tag
  composition + layout + styling. Saved views are reviewable artifacts; ad-hoc is transient.
- **Rendered view-state (transient)** — geometry/colour/weight/expand/cluster, per session,
  optionally cached/exported, **never written to domain nodes**; the **visual object model is
  separate**, binding by reference.
- **Projections over one graph**: node-link **graph**, **threat×mitigation matrix**, **attack-
  path/tree**, **DFD**, **timeline**, **provenance**, **compare/diff**.
- **Scale — progressive loading (R-033):** the View is a *bounded query*; open from a focus/filter,
  expand lazily (expand-on-click, paged neighbourhoods, LOD collapse of `composed_of`); cluster +
  roll-up for legibility.
- **Layers/tags as composable overlays (R-033):** any tag/type/zone/domain marker is a toggle-able
  overlay a View composites — named filter sets over the one graph, not separate graphs.
- **Dynamic behaviour (R-033):** force physics; per-type/-facet **unique colours**; **click to open
  containment** (`composed_of`) or **inspect** (detail + provenance + review).

**Redundancy & the two-location compare (R-034/R-035).** Two locations = two `Deployment`s of one
`ProductInstance`/`Workflow`. *An AI code-review on a secure server in two locations, then compare*
is representable once (a) `RedundancyGroup` marks them replicas (common-mode + divergence) and (b)
a **compare/diff projection** shows same-vs-different threats/mitigations (and, via §4 provenance,
which model/version produced each). **Scope:** one graph projection is MVP; matrix/compare/saved-
views/layers and redundancy are post-MVP (§7).

## 11. Iteration log & next

- **Iter 1–3:** split, adversarial fixes, three layers.
- **Iter 4:** reconcile layers, unify vocabulary + provenance, honest matrix, MVP table (DL-0004).
- **proposed.5:** sponsor display/redundancy round (DL-0005); app requirements → APP-0001.
- **proposed.6 (DL-0006):** fold #6/#7 + reification + risk; §9 partial lift; STRIDE method facet;
  AND/OR + ordering; reified Assertion; ISO 21434-shaped metric.
- **proposed.7 (this; DL-0007):** fold the **iteration-6 adversarial critic** (14 findings). Fixed
  the feasibility term (no CVSS base/environmental; exploitability only, RC-15-13), made the MVP
  metric path-level + per-category + human-rated (no CVSS, no per-step min/max at MVP), stated the
  acceptance gate substrate-neutrally and admitted node-reification narrows DEC-004, moved **R-023
  post-MVP**, added MVP MitigationInstance, de-leaned from ADR-0003, softened "verified"→"draft,
  records unpinned".
- **Next:** pin the 5 absent method records + get a human-reviewed ISO 21434 extraction + gather an
  RDF-star record; fold #9 (schema crosswalk) to close R-024/lift §9 fully; **build the §8 MVP
  vectors**; then the ADRs (§12); **DEC-001** accepts last, folding this into ARCH-0001 §3/§4.

## 12. ADR-readiness — *not yet* (critic-corrected)

proposed.6 claimed DEC-003 and the DEC-002/004 logical model were "ADR-ready now." The critic pass
shows they are **strengthened but not yet ADR-ready**; the gates are:

- **DEC-003 (risk metric)** — direction sound *after* this pass (path-level feasibility ×
  per-category S/F/O/P). **Blockers:** a human-reviewed ISO 21434 extraction (annexes are
  `not-reviewed`); `first-cvss` distilled *if* the CVSS option is wanted.
- **DEC-002/DEC-004 (logical reification)** — substrate-neutral `Assertion`/`Review`/PROV-O with a
  substrate-neutral validation gate. **Blockers:** an RDF-star library record; `prov-o`/`shacl`/
  `stix-2-1` are only `summarized`; and the sponsor must accept that node-reification **narrows**
  DEC-004 (no pure edge-property option for reviewed assertions). The RDF-vs-LPG *storage* pick and
  the DEC-002 *serialization* pick stay open.
- **DEC-001 (object model)** — accept last, after the MVP vectors prove the model runs.

Each `DEC-*` is accepted **only** by an `ADR-NNNN` + changelog + ARCH-0001 status update (CLAUDE.md).
