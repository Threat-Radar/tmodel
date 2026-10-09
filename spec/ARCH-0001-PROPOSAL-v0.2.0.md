---
schema: "archdoc/v1"
id: ARCH-0001-PROPOSAL
title: "Proposed ARCH-0001 v0.2.0 — core object model & modeling requirements (iteration 6)"
short_title: "Object-model proposal v0.2.0"
description: "Iteration 5 of the DEC-001 object-model synthesis (#15), with the iteration-6 adversarial critic folded in (DL-0007). Folds merged frameworks/products research (#6/#7) and three decision analyses: a partial lift of the DFD-standard caveat, STRIDE as a multi-valued method facet, AND/OR + ordering on attack paths, a substrate-neutral reified-Assertion provenance model, and an ISO 21434-shaped MVP risk metric. The critic pass corrected the risk metric (feasibility ≠ CVSS-base), the SHACL gate (substrate-neutral), R-023 scope, and over-claims. Proposed, not accepted — and not yet ADR-ready (§12)."
type: architecture
category: security
status: proposed
version: "0.2.0-proposed.13"
version_policy: "iterate the -proposed.N suffix; folds into ARCH-0001 §3/§4 (and an ADR accepts DEC-001)"
date: "2026-09-30"
updated: "2026-10-09"
decision_makers:
  - role: sponsor
    id: nymble
reviewers:
  - role: sponsor-review
    id: nymble
  - role: adversarial-critic
    id: agent-iteration-2
  - role: adversarial-critic
    id: agent-iteration-3
  - role: sponsor-review
    id: nymble
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
    id: nymble
    round: lifecycle-parties-tara-schema
  - role: adversarial-critic
    id: agent-iteration-7
  - role: sponsor-review
    id: nymble
    round: composite-risk-vector
  - role: sponsor-review
    id: nymble
    round: sdl-conformance
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
critic; proposed.8 folded a sponsor round (DL-0008): parties/organizations, a lifecycle axis with
returns, stakeholder-relative TARA impact, and the schema-definition approach. **proposed.9 folds
the iteration-7 adversarial critic (DL-0010):** defined `RiskScore` multiplicity, stopped
overloading ISO S/F/O/P by stakeholder, downgraded the LinkML claims, unified actor identity,
softened the lifecycle "state machine", and **pushed Party/lifecycle/stakeholder-impact to
post-MVP**. **proposed.10 folds a sponsor round (DL-0011):** risk is a **composite vector**
(feasibility + impact + **mitigation status** + derived Risk), feasibility method stays ISO 21434
Table-1 with **CC-style display only** (the composite-vector idea — **now accepted via ADR-0006**).
**proposed.11 (iteration 8; DL-0012) folds the SDL round (DL-0009):** `Mitigation.kind` (R-040,
MVP-adjacent), the **SDL/SecurityProgram** object with ordered/dated gates (R-041), **conformance
validation** (R-042), **governed document-views** (R-043), and a **Requirement** object + the
MAP-0001 crosswalk (R-044) — §3c, **all post-MVP except `Mitigation.kind`**. The SDL guideline
library records are being ingested in parallel (RPT-0013/#67).
**proposed.12** was a non-substantive identity scrub (github ids only); **proposed.13 (this; DL-0018)
promotes R-041…R-044 from §3c prose to named first-class objects in the §13 LinkML draft** —
`ThreatModel`, `SecurityProgram` + `Gate`/`Milestone`/`Checkpoint`, `Requirement`, and a governed
`GovernedView` — as **versioned, human-reviewed, program-managed views over the KG-SoT**; still
post-MVP, **DEC-001 still open**.
**Legend:** ✅
covered · ✅\* proposed direction (accepted only via the gating DEC's ADR) · ◐ still open. **These
are *proposed* requirements — several (R-023…R-039) are not yet in ARCH-0001 §4** (L13).

> **Dependency note (updated 2026-10-08).** The stack and data decisions this proposal leaned on are
> now accepted: DEC-006/DEC-010 → **ADR-0003 (Path A)** with the engine split in **ADR-0009** (Python
> brain + Rust store); DEC-011 → **ADR-0004**; and in the 2026-10-08 sweep **DEC-002 → ADR-0007**
> (LinkML IDL + interchange), **DEC-003 → ADR-0006** (the composite risk vector in §3), **DEC-004 →
> ADR-0008** (Oxigraph/RDF working store). This proposal's own subject — **DEC-001, the object model —
> remains *proposed*** (gated on #104 Stage 2/3); §4 substrate-neutrality stands regardless. Where §3
> states the risk metric, it is now ratified by ADR-0006.

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

Companies and standards groups **are** referenced across the model, so they are first-class — a
reusable **`Party`** node (an organization or a person), shared like `Component`.

- **One identity, many facets (critic M1).** `Party`, the `ThreatActor` of §1.3, and the PROV-O
  `Agent` of §4 are **facets of one identified entity**, not three separate nodes: a vendor who is
  also an insider adversary and the agent behind an AI-proposed assertion is **one** `Party` with a
  `ThreatActor` facet and a PROV `Agent` role. Identity is a single `party_id` (with a dedup rule on
  canonical org identifiers); the facets are attached, not cloned. (ExternalEntity stays a DFD role
  that *resolves to* a Party, per the §0 one-artifact rule.)
- **Intrinsic classification vs relational role (critic M2).** Only **intrinsic** classifications
  live on the node (`standards-body`, `cna`). **Relational** roles — `supplier`, `integrator`,
  `operator`, `consumer`, `owner`, `vendor-of` — are **edge types**, because the same Party is a
  supplier *to A* and a consumer *to B*: `Product` `manufactured_by`/`supplied_by` a Party;
  `Asset` `owned_by` a Party (drives the §3 owner-selection); `Vulnerability`/`Finding`
  `reported_by`/`assigned_by` a CNA and `affects` a vendor's `Product`.
- **Publishers reference the library record's publisher (critic L2b).** Standards (ISO 21434, FIPS,
  CWE/CAPEC) are `published_by` the `Party` that the `library/` record already names — **one org
  registry**, not a parallel one; the domain `Party` *is* that canonical identity, referenced by the
  library record, not re-minted.
- Typed edges per ADR-0004 (stable IDs), so "all CVEs from vendor X" or "everything governed by
  ISO" are one-hop queries.

## 3. Structure, networks, deployment, and the risk metric

Recursive `composed_of`; Interconnect→Network/NetworkLink; DNS/services as Components +
`depends_on`. **Environment is a first-class, reusable node** (F9): `ProductInstance` 1→N
`Deployment`, each →1 `Environment` (physical_security/connectivity/operational_context).

### Risk metric — a *composite risk vector* (proposes DEC-003; sponsor round folds the ADR-0005 idea)

**Risk is a *vector*, not a lone scalar (sponsor, 2026-10-02).** The row/record for a threat
carries, as peer fields: **feasibility**, **impact** (per-category), **mitigation status**, and a
**derived `Risk`** — the derived field is shown *alongside* its inputs, never instead of them, and a
single CVSS-like number is **not** the accepted scheme. (This folds the bot-authored ADR-0005
composite-vector idea; DEC-003 itself is **not** accepted here — it accepts later via one clean ADR.)

**MVP metric (simple, per ADR-0002 "a simple risk score reflecting the review"):** the derived
`Risk = M(Impact, Feasibility)`, an ISO 21434-*shaped* impact×feasibility matrix
(`iso-sae-21434-2021#RQ-15-15/16`, Annex H), where:

- **Feasibility `F` is rated at the *attack-path level*** on 21434's 4-point scale (High/Medium/
  Low/Very-low), per **Table 1 / `#RQ-15-10`** (which rates the *path*, not the step) — **human-
  rated for the MVP**, optionally informed by the attack-potential core factors (`#RC-15-12`).
  **No CVSS and no per-step aggregation at MVP** (M7, H5).
- **Impact `I` is per-category S/F/O/P** (severe/major/moderate/negligible; `#RQ-15-04/05`;
  safety ← ISO 26262 `#RQ-15-06`), **human-supplied**. 21434 determines a risk value *per
  category* (Annex H.9), so **keep the category vector**; any single-number collapse (e.g. `max`)
  is an explicit **display** simplification, not the method (M12).
- **Asset ownership & a *separate* stakeholder-impact axis (R-039 — critic-corrected, H3).** An
  `Asset` has an `owned_by` Party (§2b). **The ISO S/F/O/P categories above stay fixed to the
  end-beneficiary** (road user / data subject / end-user) so severities remain comparable — we do
  **not** re-index S/F/O/P by owner (that would change what "privacy" or "financial" *means* and
  break the ISO alignment). Instead, the owner's view is a **distinct `business_impact` axis**
  (e.g. recall cost / liability / reputation for a manufacturer; service-outage for an operator),
  assessed *in addition to* S/F/O/P, not as a relabelling of it. `Asset.owned_by` selects *whose*
  `business_impact` applies.
- **`RiskScore` multiplicity & reduction (H2).** ISO 21434 `#RQ-15-15/16` require a **single value
  1–5 per (threat-scenario)** derived from its damage-scenario impact and the feasibility of its
  attack path(s) — so a reduction *is* required (the earlier "no aggregation" meant **no collapse
  across impact categories**, not "no value"). Definition: feasibility is aggregated **over the set
  of attack paths** realising the scenario (worst path), then `M(I, F)` yields one score **per
  (threat-scenario, impact-category)** and, where owners differ, **per stakeholder**. When an
  `AttackPath` crosses assets with **different owners**, the scenario's score is reported **for each
  affected owner** (no fictional single "owner of the path"). (MVP: one stakeholder, S/F/O/P only,
  no `business_impact` axis — all of R-039 beyond `owned_by` is post-MVP, H5.)
- **Mitigation status is a first-class vector component (R-045, sponsor round).** The risk row/record
  surfaces the threat/path's mitigation lifecycle state (planned / in-progress / complete /
  accepted-risk / n-a — refined by DEC-009) as a **peer field** of feasibility and impact, filterable
  on its own — **not** buried inside the derived `Risk`. (It reads `MitigationInstance.status`, §5; MVP.)
- **Display is CC-flavoured; the *method* stays ISO 21434 Table-1 (sponsor round).** Table/row views
  MUST show **concise metric numbers + a human-readable feasibility label + a colour indicator**, not
  an opaque float. This is **presentation only** — the feasibility *computation* remains the ISO 21434
  path-level 4-point rating above; **Common Criteria / ISO 18045 is not the MVP method** (the
  iteration-5 research down-selected it; `iso-iec-18045` is a library stub).

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
captured.** Threats, weaknesses, attack surfaces and mitigations are **scoped to the phase(s) they
apply in** (`applies_in_phase`) along a **`LifecyclePhase`** enum (aligned to ISO/SAE 21434 + ISO 26262):

`concept → architecture → design → implementation → verification/validation → production/
manufacturing → distribution → deployment/commissioning → operation/use → maintenance/update →
end-of-support → decommission/disposal`.

- **The state-bearing entity is the `ProductInstance` (critic M4).** A *lifecycle state* is a
  time-stamped attribute of a `ProductInstance` (not of the generic `Product` or a `Component`),
  and it needs the **time/version axis** the model already owes (`valid_from`/`valid_to` — flagged
  as still-missing: add it with this). A refurbished unit has the *same* firmware hash — i.e. the
  same identity-by-hash `ProductInstance` — but a **new lifecycle state + new `Deployment` + new
  owner**, so state is carried by a (ProductInstance, time) pair, not by the hash alone.
- **Phase-scoped threats (R-037), bounded against Environment (critic M6).** `applies_in_phase` =
  the **coarse lifecycle stage** a threat belongs to (design flaw in *design*, supply-chain tamper
  in *production*, data remanence in *decommission*). This is **distinct from** the §3 `Environment`
  (the *concrete operational exposure* of a running deployment): "runtime exploit" is scoped by
  Environment, *not* by `applies_in_phase=operation` — the phase answers *when in the lifecycle*,
  the Environment answers *where/how exposed at runtime*. One threat picks the axis that fits; it
  does not get both (the F1/F5 no-double-model rule).
- **Reverse logistics / returns (R-038) — a phase set now, a state machine later (critic M3).**
  What is modeled today is the **phase enum tag** (returns/refurbish/resale/dispose as phases);
  the **transitions, guards and current-state history** (the actual state machine) are **future
  work**, not yet modeled. Returns carry their own threats (data remanence, counterfeit/tampered
  re-insertion, warranty fraud). **Custody provenance** — "who refurbished it", the changed
  trust on re-entry — is **supply-chain provenance**, the class §4 defers to the radar→tmodel
  contract (ADR-0001); it is **post-MVP**, not part of the in-model epistemic Assertion spine.
- This is an **axis**, not a new layer. (MVP: the phase enum + `applies_in_phase` on threats for
  one worked example; the state machine, the returns branch, and custody provenance are post-MVP.)

## 3c. SDL, conformance & governed document-views (sponsor round — R-040…R-044; DL-0009)

Mitigations are not only technical; an **SDL** is a first-class, conformance-validatable object;
and a threat model and an SDL are both **iterating, approvable views over the KG-as-SoT**. The
research is **RPT-0013 + MAP-0001** (on main); the guideline **library records are being ingested**
now (T-033/T-029). **All of this is post-MVP except `Mitigation.kind`** (ADR-0002 scope guard +
the iteration-7 critic's MVP-overload finding).

**Promoted to named first-class objects in the §13 LinkML draft (proposed.13).** R-041…R-044 are no
longer prose only: the draft object model (`spec/schema/tmodel-object-model.linkml.yaml`) now names
**`ThreatModel`**, **`SecurityProgram`** with **`Gate`/`Milestone`/`Checkpoint`** program nodes,
**`Requirement`**, and a governed, versioned **`GovernedView`** (complementing the transient `View`
of §10) — each modeled as a **versioned, human-reviewed, program-managed view over the KG-SoT**:
an `owner` (a `Party` role, §2b), a `revision`, approval through the existing `Review`/`Assertion`
spine (§4) pinned to a reproducible `approval_digest`, a `governance_status`
(draft/in-review/approved/superseded), and a `supersedes` link across review cycles. This remains a
**proposal** — it is the DEC-001 proposal vehicle; **DEC-001 stays open and nothing here is accepted**
(see §8/§12). The render is `spec/schema/OBJECT-MODEL.md`; the design-log entry is DL-0018.

- **Mitigation kind (R-040) — MVP-adjacent.** `MitigationInstance.kind ∈ {technical, documentation,
  process}` — a mitigation may be a feature, a document, or a process step; each still carries
  effectiveness / evidence / owner / status (§5) and shows as the mitigation-status component of the
  risk vector (§3).
- **SDL / SecurityProgram object (R-041) — post-MVP.** A program attached to a Product/ProductFamily,
  composed of **ordered, named, dated `Gate`/`Checkpoint`/`Milestone`** nodes with entry/exit criteria,
  owner, approval, planned vs actual dates, and dependencies — **full program management as graph
  nodes**. Gates map onto the **`LifecyclePhase` axis** (§3b); **corporate gate-naming varies**, so a
  gate has a canonical phase mapping + a local name (the MAP-0001 gate crosswalk). **§13 draft:**
  `SecurityProgram` (`governs` a Product/ProductInstance/ProductFamily, `program_nodes`,
  `incorporates` Requirements) with the abstract `ProgramNode` realized by `Gate`/`Milestone`/
  `Checkpoint` (`order`, `planned_date`/`actual_date`, `gate_status`, `owner`, `at_phase`,
  `gated_by`, `decided_by`, `depends_on_node`) — itself a governed/versioned view.
- **Conformance validation (R-042) — post-MVP (minimal via the risk vector at MVP).** A `Requirement`
  (from a spec, via MAP-0001) is satisfied by `Mitigation`/`WorkProduct`/`Evidence` + an approving
  `Review`. A **threat-model instance is conformant** when every in-scope `ThreatInstance` has an
  **approved, evidenced** `MitigationInstance` — an **automatable** check a `Gate`'s exit criterion
  runs (RPT-0013 §4 design: schema + policy rules + signed evidence). **It proves linkage + approval,
  not adequacy** — the human cybersecurity-assessment role remains (CLAUDE.md). Connects to the
  deferred audit model (#19). **§13 draft:** `Requirement.satisfied_by` Mitigation(s) +
  `Requirement.conformance_status` (`RequirementConformanceStatus`); a `Gate.validates_conformance_of`
  edge points the exit-criterion check at a `ThreatModel`.
- **Governed document-views (R-043) — post-MVP.** A threat-model report and an SDL plan are
  **materialized, approvable projections** over the KG (extends §10), with governance metadata —
  **owner, change tracking (§4 provenance), approval (`Review`), version**. Reconciling §10's "views
  are transient": a *governed document-view* is a **named, versioned, signed-off snapshot** whose
  view-spec + approval live in the KG and whose content derives from KG state at a point in time
  (approval attaches to a commit/digest so it is reproducible — SysML v2 View/Viewpoint, OMG SACM,
  OSCAL→Word as prior art). Both the TM and the SDL *iterate* — living views over the one SoT.
  **§13 draft:** `GovernedView` (`is_a` the §10 `View`) adds `revision`, `owner`, `approved_by`
  (Review), `approval_digest`, `governance_status`, `supersedes`, `renders`; `ThreatModel` and
  `SecurityProgram` carry the same governance facet, so a threat-model report and an SDL plan are
  owned/approved/versioned snapshots, not transient lenses.
- **Requirement object + cross-spec crosswalk (R-044) — post-MVP.** A `Requirement` with `maps_to`
  edges across specs (the MAP-0001 overlap); `Gate` exit criteria and conformance (R-042) reference it.
  **§13 draft:** `Requirement` carries `text`, `normativity` (`Normativity`), `maps_to` other
  Requirements, and a `source_ref` that is an **opaque `uriorcurie`** into the Threat-Radar/library
  requirement record — tmodel→library by reference only; **no import of or dependency on the library
  schema.**

**Guardrails (from the iteration-7 critic).** The SDL document-owner/approver is a **`Party` role**
(§2b — one identity, many facets), not a new actor type. Custody provenance stays supply-chain /
radar (§3b/§4). Business/conformance impact is **not** a re-indexing of the ISO S/F/O/P (§3).

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
| **R-036 (parties/organizations)** | one `Party` identity (ThreatActor/PROV-Agent facets); relational roles on edges; publisher via library (§2b) | ◐ (new; post-MVP — H5) |
| **R-037 (lifecycle-phase axis)** | `LifecyclePhase` enum + `applies_in_phase`, bounded vs Environment (§3b) | ◐ (new; enum modeled, scoping post-MVP) |
| **R-038 (reverse logistics / returns)** | phase set now; state machine + custody provenance later (§3b) | ◐ (new; post-MVP) |
| **R-039 (asset owner + stakeholder/business impact)** | `Asset.owned_by`; separate `business_impact` axis (S/F/O/P stays end-user); RiskScore reduction per RQ-15-16 (§3) | ◐ (new; post-MVP — MVP risk is single end-user) |
| **R-045 (composite risk vector)** | risk = {feasibility, impact, **mitigation status**, derived Risk}; CC-style display, ISO 21434 Table-1 method (§3) | ✅\* (new; MVP — proposes DEC-003) |
| **R-040 (mitigation kind)** | `MitigationInstance.kind ∈ {technical, documentation, process}` (§3c/§5) | ✅\* (new; MVP-adjacent) |
| **R-041 (SDL / SecurityProgram)** | ordered/named/dated Gates/Checkpoints/Milestones + program mgmt, mapped to LifecyclePhase (§3c); **§13: `SecurityProgram`, `ProgramNode`→`Gate`/`Milestone`/`Checkpoint`** | ◐ (new; post-MVP) |
| **R-042 (conformance validation)** | Requirement↔Mitigation/Evidence+Review; automatable "threats-mitigated" gate check (§3c; RPT-0013 §4); **§13: `Requirement.conformance_status`, `Gate.validates_conformance_of`** | ◐ (new; post-MVP) |
| **R-043 (governed document-views)** | TM & SDL as owned/approved/versioned snapshot-views over KG-SoT (§3c; extends §10/§4); **§13: `GovernedView`, `ThreatModel`, `SecurityProgram` governance facet** | ◐ (new; post-MVP) |
| **R-044 (Requirement + spec crosswalk)** | `Requirement` + `maps_to` edges (MAP-0001) (§3c); **§13: `Requirement` with opaque `source_ref` to library** | ◐ (new; post-MVP) |

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
| **Composite risk vector** = {feasibility (ISO 21434 Table-1, CC-style display), per-category S/F/O/P impact, **mitigation status**, derived `Risk=M(I,F)`} — human-rated, no CVSS | ✅ build | CVSS-feasibility; per-step aggregation; full-TARA annexes; `business_impact` axis |
| **MitigationInstance + mitigation-state visible** (ADR-0002 demo) | ✅ build (minimal) | owner/work-item/verification enrichment |
| generic↔instance mapping, ≥2 domains/instance types | ✅ build | |
| full **DFD layer** (Process/DataFlow/DataStore/ExternalEntity/Workflow) | *one illustrative flow only* | ✅ post-MVP |
| **method facets** beyond STRIDE (LINDDUN/MAESTRO) | — | ✅ post-MVP |
| **Network/NetworkLink/DNS** topology | — | ✅ post-MVP |
| **Deployment/Environment/exposure** (→ R-023 relativity) | — (*single deployment assumed*) | ✅ post-MVP |
| **compile/SLSA build provenance** | — (radar contract) | ✅ post-MVP |
| **VEX** override | — | ✅ post-MVP |
| **Jira external_refs**, audit (Requirement/WorkProduct) | — | ✅ post-MVP (#19) |
| **interactive graph view** — *one working projection* (force layout, type colours, click-expand/inspect, progressive load); stack is decided (ADR-0003, Path A) | ✅ build (working, not yet "best-in-class" A-042) | best-in-class bar; matrix/timeline/compare; saved views; layer/tag compositing |
| **redundancy / common-mode / compare** (RedundancyGroup, diff projection) | — | ✅ post-MVP |
| **Party/Organization** (vendor/manufacturer/CNA/owner) | — (modeled; only CVE vendor/CNA labels, free from NVD) | full role/edge set, supplier graph |
| **lifecycle phase** (`applies_in_phase`) | — (modeled; phase enum only) | phase-scoped threats, state machine, **returns/reverse logistics** |
| **stakeholder impact** (`Asset.owned_by` + `business_impact`) | — (MVP risk is single end-user, S/F/O/P only) | owner-selection + business-impact axis |
| **`Mitigation.kind`** {technical, documentation, process} | ✅ build (attribute) | — |
| **SDL/SecurityProgram, gates, conformance validation, governed document-views, Requirement crosswalk** | — (modeled §3c) | ✅ post-MVP (SDL program, automatable conformance, #19 audit) |

**The MVP is the attack-path KG.** DFD/networks/Environment are modeled but **not built** for
Nov 5 (at most one illustrative flow). The interactive view is a **working single projection** on
the decided stack (ADR-0003, Path A); the "best-in-class" bar (APP-0001 A-042) is post-MVP. The
iter-6 additions (Party, lifecycle, stakeholder impact) are **modeled, not built** for Nov 5 (H5).

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
from the four domain layers and never stored back. DEC-006 (**accepted — ADR-0003, Path A**);
product requirements live in **APP-0001**.

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
- **proposed.9 (iteration 7 critic; DL-0010):** folded the adversarial critic on proposed.8 —
  defined `RiskScore` multiplicity/reduction (RQ-15-16) and **stopped overloading ISO S/F/O/P by
  stakeholder** (added a separate `business_impact` axis); **downgraded LinkML** (no LPG generator,
  gate needs hand-written SHACL, CI loop is lane-#64 future); **unified Party/ThreatActor/Agent
  identity** + relational-roles-on-edges + publisher-via-library; **softened the lifecycle "state
  machine" to a phase enum** + named `ProductInstance` as state-bearer + flagged the temporal axis +
  bounded phase vs Environment + custody provenance → post-MVP; **pushed Party/lifecycle/stakeholder
  impact to post-MVP** (MVP overload). (SDL round, DL-0009, folds in iteration 8.)
- **proposed.10 (sponsor round; DL-0011):** risk is a **composite risk vector** (feasibility +
  impact + **mitigation status** + derived Risk) — folded the bot-authored **ADR-0005** idea
  (R-045); **feasibility method stays ISO 21434 Table-1, CC is display-only**; **ADR-0005 dropped**
  (bot self-marked accepted, no governance) and **DEC-003 stays open** (accepts via a clean ADR later).
- **proposed.11 (iteration 8; DL-0012):** folded the SDL round (DL-0009) — §3c adds `Mitigation.kind`
  (R-040), SDL/SecurityProgram + gates (R-041), conformance validation (R-042), governed
  document-views (R-043), Requirement + MAP-0001 crosswalk (R-044); **all post-MVP except
  `Mitigation.kind`**. In parallel, the SDL guideline **library records are being ingested** (RPT-0013/
  #67): NIST SSDF (FX-1-grade), OWASP SAMM + SLSA (summarized, FX-1 verify pending), rest stubbed;
  paywalled (IEC 62443-4-1, ISO 27034/26262, BSIMM) flagged for the preview/ask path.
- **proposed.12:** non-substantive — the repo-wide identity scrub (project people by github id only).
- **proposed.13 (this; DL-0018):** fold the §3c SDL/governance objects into the **§13 LinkML draft** as
  named first-class types, grounded in RPT-0013-OM: **`ThreatModel`** (governed scope snapshot),
  **`SecurityProgram`** with abstract **`ProgramNode`** → **`Gate`/`Milestone`/`Checkpoint`**,
  **`Requirement`** (opaque `source_ref` to a library record; `maps_to`; `satisfied_by`;
  `conformance_status`), and **`GovernedView`** (`is_a` §10 `View`). The shared governed-view facet
  (owner = `Party` role, `revision`, `approved_by` via the §4 `Review`/`Assertion` spine, reproducible
  `approval_digest`, `governance_status`, `supersedes`, `created`/`updated`) makes the TM and the SDL
  **versioned, human-reviewed, program-managed** views over the KG-SoT. Added enums `GateStatus`,
  `ThreatModelStatus`, `ApprovalStatus`, `RequirementConformanceStatus`, `Normativity`. Honors the
  iteration-7 guardrails (owner is a Party role; approval uses the existing Review spine; conformance
  proves linkage + approval, not adequacy). **Still post-MVP; DEC-001 stays open — this is the DEC-001
  proposal vehicle, nothing accepted.**
- **Next:** pin the 5 absent method records + get a human-reviewed ISO 21434 extraction + gather an
  RDF-star record; **author the LinkML schema in `spec/schema`** (§13; lane #64); fold #9 (schema
  crosswalk) to close R-024/lift §9 fully; **build the §8 MVP vectors**; then the ADRs (§12);
  **DEC-001** accepts last, folding this into ARCH-0001 §3/§4. A fresh adversarial-critic pass runs
  on this iteration before any ADR.

## 12. ADR-readiness — *not yet* (critic-corrected)

proposed.6 claimed DEC-003 and the DEC-002/004 logical model were "ADR-ready now." The critic pass
shows they are **strengthened but not yet ADR-ready**; the gates are:

- **DEC-003 (risk metric)** — direction now a **composite risk vector** (feasibility + impact +
  mitigation status + derived Risk; ISO 21434 Table-1 feasibility method, CC-style display), folding
  the ADR-0005 idea per the sponsor. **Accepts via one clean ADR** (full governance: ARCH §8 +
  CHANGELOG) once settled — **not** the bot's self-marked ADR-0005, which was dropped. **Blockers:**
  a human-reviewed ISO 21434 extraction (annexes `not-reviewed`); the derived-`Risk` aggregation
  function documented; `first-cvss` distilled *if* the post-MVP CVSS option is wanted.
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

- **One source, several targets.** A LinkML schema generates **JSON Schema**, **SHACL**, **OWL/RDF**,
  **Python** types (pydantic/dataclasses), ER diagrams and docs — fitting ADR-0004's "YAML/JSON /
  LinkML-shaped objects" canonical SoT and the Path A Python engine. **Honest limits (critic H4,
  L1):** LinkML has **no first-class LPG/Cypher generator** (the pinned `community/linkml` record,
  `status: summarized`, lists JSON-Schema/SHACL/OWL/RDF only) — the **LPG lowering needs a custom
  adapter** (the §4 edge-reification); and `gen-shacl` emits **structural** shapes (cardinality/
  range/pattern), so the §4 **conditional acceptance gate** ("provenance + review before
  `status=accepted`") needs **hand-written SHACL/constraints**, not generation. So LinkML covers
  files + RDF/SHACL/JSON/Python; it does **not** by itself make the model substrate-neutral.
- **Objects = classes, typed edges = slots.** Proposed classes mirror §3 (Product, ProductInstance,
  Component, Party, Weakness, Vulnerability, AttackPattern, ThreatInstance, AttackStep, AttackPath,
  DamageScenario, Mitigation, RiskScore, Review, Assertion, Deployment, Environment, LifecyclePhase,
  RedundancyGroup, View, and — iteration 8 — `SDL`/SecurityProgram, Gate/Checkpoint/Milestone,
  Requirement, WorkProduct/Evidence, GovernedView); relations are slots with ranges + an edge
  reification (`Assertion`) for the reviewed ones (§4). Local/non-MITRE extensions (e.g. `tr-weak-*`)
  are just added classes/instances.
- **How we iterate (the ask) — *target* workflow, not yet built (H4).** Schemas versioned like any
  archdoc; a change is a `spec/schema` PR; CI regenerates JSON Schema + SHACL and runs the §8 vectors,
  so a schema change that breaks a vector fails CI. **Today `spec/schema/` and `spec/vectors/` are
  README stubs** — this loop is the deliverable of **lane #64**, stated as a goal, not a current
  property. The *logical* model and the *machine* schema are meant to iterate together.
- **Scope/relationship:** LinkML is the **IDL** (DEC-002's schema-language half). The *interchange/
  export* formats (Turtle/JSON-LD/GraphML/CSV) are derived per ADR-0004, and the OTM semantic
  round-trip remains the DEC-002 interchange test (#9). First cut is lane **#64** (@Maimcghee).
