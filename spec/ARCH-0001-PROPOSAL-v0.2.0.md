---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 6)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 5 of the DEC-001 object-model synthesis (#15), with the iteration-6 adversarial critic folded in (DL-0007). Folds merged frameworks/products research (#6/#7) and three decision analyses: a partial lift of the DFD-standard caveat, STRIDE as a multi-valued method facet, AND/OR + ordering on attack paths, a substrate-neutral reified-Assertion provenance model, and an ISO 21434-shaped MVP risk metric. The critic pass corrected the risk metric (feasibility ≠ CVSS-base), the SHACL gate (substrate-neutral), R-023 scope, and over-claims. Proposed, not accepted — and not yet ADR-ready (§12)."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.8"
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
  - role: sponsor-review
    id: paul-lambert
    round: lifecycle-parties-tara-schema
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
  RDF-star record first. proposed.8 (iteration 6, DL-0008) folds a sponsor round: a first-class
  Party/Organization entity (R-036, §2b), a lifecycle-phase axis with reverse logistics/returns
  (R-037/R-038, §3b), stakeholder-relative impact driven by asset ownership (R-039, §3 TARA), and
  the schema-definition approach — LinkML in spec/schema, iterable (§13; proposes DEC-002's IDL).
---

# Proposed ARCH-0001 v0.2.0 — core object model (iteration 6)

**Status: proposed (iteration 6, proposed.8).** proposed.5 added the presentation layer +
redundancy; proposed.6 folded #6/#7 + three decision analyses; proposed.7 folded the adversarial
critic; **proposed.8 folds a sponsor round (DL-0008): parties/organizations, a lifecycle axis with
returns, stakeholder-relative TARA impact, and the schema-definition approach.** **Legend:** ✅
covered · ✅\* proposed direction (accepted only via the gating DEC's ADR) · ◐ still open. **These
are *proposed* requirements — several (R-023…R-039) are not yet in ARCH-0001 §4** (L13).

> **Dependency note.** DEC-006/DEC-010 (the stack) are now **accepted — ADR-0003 (Path A)** — and
> DEC-011 storage/edges is **accepted — ADR-0004**; DEC-004 (RDF vs LPG) is narrowed to the
> working-store engine and still open. This proposal's §4 substrate-neutrality stands on the logical
> model regardless of the DEC-004 pick.

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
   (`replica_of`/`redundant_with`, §10), and **Party/Organization** (vendor, manufacturer,
   standards body, CNA, operator, owner — §2b).
2. **Behavioral (DFD) — projected onto (1)** — ExternalEntity, Process, DataStore, DataFlow,
   Workflow, each `realized_by` Component(s), with **security properties** (authenticated?
   encrypted? privilege) and **data `classification`**. Verified element set matches Microsoft
   TMT and OTM (RPT-0002 §2; RPT-0003).
3. **Threat & catalog (one vocabulary, F2)** — generic Weakness(CWE)/AttackPattern(CAPEC/
   ATT&CK)/Mitigation(D3FEND)/ThreatActor; instance ThreatInstance (carries a **method facet**,
   §2, `realizes` DamageScenario), AttackStep (pre/postconditions, AND/OR gates, ordering — §2a)/
   AttackPath (`attack_feasibility`), Finding/Vulnerability, MitigationInstance, RiskScore.
4. **Cross-cutting** — **one provenance spine** (F6): PROV-O Entity/Activity/Agent + a reified
   **`Assertion`** node (the substrate-neutral invariant — §4); Review; ProductFamily; external refs;
   the **LifecyclePhase axis** (§3b) that scopes threats/mitigations; **Party** roles & ownership (§2b).
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

## 2b. Parties & organizations (sponsor round — R-036)

Companies and standards groups **are** referenced across the model, so they are first-class.
A single **`Party`** node (an organization or a person) carries one or more **roles** rather than
a subclass per role (one company is often both a manufacturer and an operator):

- **Roles:** `vendor`, `manufacturer` (incl. *product manufacturer* vs *chip/component manufacturer*),
  `supplier`, `integrator`, `operator`/`service-provider`, `consumer`/`end-user`, `owner`,
  `standards-body`, `cna`/`advisory-source`, `regulator`.
- **Where they attach:** `Vulnerability`/`Finding` → `reported_by`/`assigned_by` a CNA and
  `affects` a vendor's `Product`; `Product`/`ProductFamily` → `manufactured_by`/`supplied_by` a
  Party; library standard records (ISO 21434, FIPS, CWE/CAPEC/ATT&CK) → `published_by` a
  standards body (ISO, NIST, MITRE); `Asset` → `owned_by` a Party (drives TARA impact, §3).
- Modeled as typed edges per ADR-0004 (stable IDs). Parties are reusable nodes (shared like
  `Component`), so "all CVEs from vendor X" or "everything governed by ISO" are one-hop queries.

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
- **Impact is stakeholder-relative — the asset *owner* determines it (sponsor round, R-039).**
  An `Asset` has an `owned_by` Party (§2b); the **same** damage scenario weighs differently for a
  **consumer** vs a **service operator** vs a **product manufacturer** vs a **chip manufacturer**
  (e.g. a recall is severe-financial for the product maker, operational for the operator, privacy
  for the consumer). So `DamageScenario` impact is a **(category, stakeholder-role, severity)**
  tuple — the per-category vector from above, indexed by stakeholder. The `RiskScore` is computed
  **for the relevant owner/stakeholder**; whose impact "counts" is driven by `Asset.owned_by`.
  ISO 21434 fixes the stakeholder to the road user; our multi-domain model generalises to the
  owner. (MVP: one stakeholder per asset — the owner; multi-stakeholder impact is post-MVP.)

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

## 3b. Lifecycle & reverse logistics (sponsor round — R-037/R-038)

**Every step in a product's life is a different place with different threats, and this must be
captured.** A `Product`/`ProductInstance`/`Component` moves through a **`LifecyclePhase`**, and
threats, weaknesses, attack surfaces and mitigations are **scoped to the phase(s) they apply in**
(`applies_in_phase`). The forward phases (aligned to ISO/SAE 21434's lifecycle and ISO 26262):

`concept → architecture → design → implementation → verification/validation → production/
manufacturing → distribution → deployment/commissioning → operation/use → maintenance/update →
end-of-support → decommission/disposal`.

- **Phase-scoped threats (R-037).** The same component faces *different* threats per phase: a
  supply-chain tamper in **production**, a design flaw in **design**, a runtime exploit in
  **operation**, data remanence in **decommission**. A `ThreatInstance`/`Mitigation`/`AttackSurface`
  carries the phase(s) it applies in; a query can ask "threats in the manufacturing phase".
- **Lifecycle is a state machine, not a line — reverse logistics / returns (R-038).** A unit can
  **return** (RMA) → **inspect** → **refurbish** → **resell/redeploy**, or → **recycle/dispose**.
  Returns carry their own threats: **data remanence** on returned devices, **counterfeit or
  tampered re-insertion** into the refurbished supply chain, warranty fraud, and a **changed
  provenance/trust** when a unit re-enters `operation` under a new owner. Model as lifecycle states
  + transitions (including the return/refurbish loop); a refurbished `ProductInstance` gets a new
  `Deployment` and an updated provenance (§4) recording who refurbished it.
- This is an **axis**, not a new layer: it cross-cuts structure, threats, risk, and provenance.
  (MVP: the phase enum + `applies_in_phase` on threats for one worked example; the full state
  machine and returns branch are post-MVP.)

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
| **R-036 (parties/organizations)** | `Party` node + roles; reported_by/manufactured_by/published_by/owned_by (§2b) | ✅\* (new) |
| **R-037 (lifecycle-phase axis)** | `LifecyclePhase` + `applies_in_phase` on threats/mitigations (§3b) | ✅\* (new; MVP = enum + one example) |
| **R-038 (reverse logistics / returns)** | lifecycle state machine incl. return/refurbish/resale/dispose (§3b) | ◐ (new; post-MVP) |
| **R-039 (stakeholder-relative impact)** | `Asset.owned_by` Party → per-stakeholder DamageScenario impact (§3 TARA) | ✅\* (new; MVP = one stakeholder/asset) |

Iter-5+critic deltas: R-025/R-027b/R-031 → ✅\*; **R-023 moved to post-MVP** (was ✅\*, H3);
STRIDE↔CWE/CAPEC remains unasserted (§2). Iter-6 adds R-036…R-039 (§2b/§3/§3b) and §13 schema.

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
| **Party/Organization** (vendor/manufacturer/CNA/standards-body/owner) | ✅ build (minimal — CVE vendors/CNAs, mfr, owner) | full role set, supplier graph |
| **lifecycle phase** (`applies_in_phase` on threats) | *enum + one worked example* | full state machine + **returns/reverse logistics** |
| **stakeholder-relative impact** (`Asset.owned_by` → impact) | ✅ build (one stakeholder/asset) | multi-stakeholder impact |

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
- **proposed.8 (iteration 6; DL-0008):** sponsor round — **Party/Organization** (R-036, §2b),
  **lifecycle-phase axis + reverse logistics/returns** (R-037/R-038, §3b), **stakeholder-relative
  impact** via asset ownership (R-039, §3), and the **schema-definition approach (LinkML, §13)**.
  Dependency note updated: ADR-0003 + ADR-0004 now accepted.
- **Next:** pin the 5 absent method records + get a human-reviewed ISO 21434 extraction + gather an
  RDF-star record; **author the LinkML schema in `spec/schema`** (§13; lane #64); fold #9 (schema
  crosswalk) to close R-024/lift §9 fully; **build the §8 MVP vectors**; then the ADRs (§12);
  **DEC-001** accepts last, folding this into ARCH-0001 §3/§4. A fresh adversarial-critic pass runs
  on this iteration before any ADR.

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
- **DEC-002 (schema IDL)** — §13 proposes **LinkML** as the schema definition language (the IDL),
  distinct from the *serialization/interchange* sub-question (export side, ADR-0004) which still
  needs the OTM round-trip (#9). Ready to pilot (lane #64) before an ADR formalises it.
- **DEC-001 (object model)** — accept last, after the MVP vectors prove the model runs. The iter-6
  additions (Party/lifecycle/stakeholder impact) are **proposed**, pending the next critic pass.

Each `DEC-*` is accepted **only** by an `ADR-NNNN` + changelog + ARCH-0001 status update (CLAUDE.md).

## 13. Schema definition & iteration — LinkML (proposes DEC-002's IDL)

**Question: what syntax defines our schemas, and how do we iterate on them?** Proposal: author the
object model as **[LinkML](https://linkml.io)** — YAML schema files in **`spec/schema/`** — as the
single machine-readable encoding of ARCH-0001 §3. Why LinkML:

- **One source, many targets.** A LinkML schema generates **JSON Schema**, **SHACL** (the §4
  acceptance gate), **Python** types (pydantic/dataclasses for the engine), ER diagrams, and docs —
  so it fits ADR-0004's "YAML/JSON / LinkML-shaped objects" canonical SoT and the Path A Python
  engine, and is **substrate-neutral** (works for files + both RDF and LPG, so it survives DEC-004).
- **Objects = classes, typed edges = slots.** Proposed classes mirror §3 (Product, ProductInstance,
  Component, Party, Weakness, Vulnerability, AttackPattern, ThreatInstance, AttackStep, AttackPath,
  DamageScenario, Mitigation, RiskScore, Review, Assertion, Deployment, Environment, LifecyclePhase,
  RedundancyGroup, View); relations are slots with ranges + an edge reification (`Assertion`) for the
  reviewed ones (§4). Local/non-MITRE extensions (e.g. `tr-weak-*`) are just added classes/instances.
- **How we iterate (the ask).** Schemas are versioned like any archdoc (version/updated); a change is
  a `spec/schema` PR; CI regenerates JSON Schema + SHACL and runs the **§8 vectors** against them, so
  a schema change that breaks a vector fails CI. The *logical* model (this proposal → ARCH-0001 §3)
  and the *machine* schema (LinkML) iterate together; the schema never diverges silently.
- **Scope/relationship:** LinkML is the **IDL** (DEC-002's schema-language half). The *interchange/
  export* formats (Turtle/JSON-LD/GraphML/CSV) are derived per ADR-0004, and the OTM semantic
  round-trip remains the DEC-002 interchange test (#9). First cut is lane **#64** (Mai Li).
