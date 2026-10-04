---
schema: "archdoc/v1"
id: DL-0009
title: "Sponsor round — SDL object, conformance validation, mitigation kinds, documents-as-governed-views"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0009
---

# DL-0009 — SDL / conformance design round (captured for iteration 7)

AI-assisted design record for #15 (per `CLAUDE.md`). A sponsor design round introducing the
**Secure (Software) Development Lifecycle** as a first-class, conformance-validatable concern.
Captured here now; the **research is the gate** (RPT-0013 + MAP-0001), and the model changes
**fold into iteration 7** once RPT-0013 lands and iteration 6 (#66) merges. Nothing accepted
(ADR-only). SDL is **post-MVP** (ADR-0002 scope guard, reinforced by the iteration-6 critic's
MVP-overload finding).

## Questions asked (sponsor)

1. Mitigations may be **technical features, documentation, or process** — model that.
2. Define an **SDL object** that supports **conformance validation**; a threat-model instance on
   a product could **automate validation of how threats are mitigated**.
3. SDL needs **deep external research** — many guidelines; **collect, ingest, enrich**, with
   **requirements mappings** showing how specs share/overlap common requirements.
4. A threat model and an SDL are **both iterating views of status and approvals**, both with
   **document owner, change tracking, approval, versions** — and both should be **views, not the
   SoT; the KG is the SoT**.
5. SDLs have **phases / checkpoints / gates / milestones** — named differently by corporate
   groups — so gates should be **ordered, named, dated**, with **full program management** as
   steps packaged into the SDL KG.

## Design captured (→ iteration 7, post-MVP unless noted)

- **Mitigation kind (R-040).** `MitigationInstance.kind ∈ {technical, documentation, process}` —
  a mitigation can be a feature, a document, or a process step; each still carries
  effectiveness / evidence / owner / status. *This small addition is the one MVP-adjacent part
  (ADR-0002's demo already shows mitigation state).*
- **SDL / SecurityProgram object (R-041, post-MVP).** A program attached to a Product/
  ProductFamily, composed of **ordered, named, dated `Gate`/`Checkpoint`/`Milestone`** nodes with
  entry/exit criteria, owner, approval, planned vs actual dates, and dependencies — i.e. **full
  program management**. Gates map onto the iteration-6 **`LifecyclePhase` axis** (gates are the
  governance points between phases); **corporate naming varies**, so each gate has a canonical
  phase mapping + a local name (MAP via RPT-0013 Lane 2).
- **Conformance validation (R-042).** A `Requirement` (from a spec, via the MAP-0001 crosswalk) is
  satisfied by `Mitigation`/`WorkProduct`/`Evidence` + an approving `Review`. A **threat-model
  instance is conformant** when every in-scope `ThreatInstance` has an **approved**
  `MitigationInstance` — an **automatable** "threats-mitigated" check that a gate's exit criterion
  can run. Connects threat model ↔ SDL gates ↔ the deferred audit model (#19).
- **Documents are governed views; the KG is the SoT (R-043).** A threat-model report and an SDL
  plan are **materialized, approvable projections** over the KG (extends §10 presentation layer),
  but with **governance metadata**: owner, change tracking (via §4 provenance), approval (a
  `Review`), and **version**. Reconcile with §10 "views are transient": a *governed document-view*
  is a **named, versioned, signed-off snapshot** whose view-spec + approval live in the KG while
  its rendered content derives from KG state at a point in time. Both the TM and the SDL *iterate*
  — living views with version history over the one SoT.
- **Requirements crosswalk (R-044) → `MAP-0001`.** A `Requirement` object with **cross-spec
  mappings** (how SSDF ↔ MS SDL ↔ SAMM ↔ 21434 ↔ 62443-4-1 overlap). Output of RPT-0013 Lane 3;
  feeds conformance (R-042) and gate exit-criteria.

## Guardrails from the iteration-6 critic (applied up front)

- **SDL is post-MVP** — the critic flagged the MVP is already overloaded; only `Mitigation.kind`
  (R-040) is MVP-adjacent. The SDL program, gates, conformance automation, and governed views are
  **modeled, not built** for Nov 5.
- **Actor identity must unify** (critic M1): `Party` (owner/vendor/standards-body), `ThreatActor`,
  and PROV-O `Agent` are **roles/facets of one identified entity**, not four node types — the SDL's
  document-owner/approver is a `Party` role. Resolve in iteration 7.
- **Custody vs epistemic provenance** (critic M5): SDL/returns custody provenance is the
  supply-chain class §4 defers to the radar contract — keep it post-MVP, not in the epistemic
  Assertion spine.
- **Don't overload ISO S/F/O/P by stakeholder** (critic H3): keep safety/impact end-user-faithful;
  SDL/business conformance impact is a **separate** axis, not a re-indexing of S/F/O/P.

## Next

Run RPT-0013 (multi-agent: collect → ingest → MAP-0001 overlap → conformance/document-governance).
Then fold R-040…R-044 into **iteration 7** (after #66 merges), with a fresh adversarial-critic pass.
