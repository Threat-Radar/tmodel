---
schema: "archdoc/v1"
id: RPT-0013-dimensions
title: "RPT-0013 dimensions — Secure Development Lifecycle & conformance (search axes)"
type: research
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: RPT-0013
---

# RPT-0013 — search dimensions (the research plan)

**Goal.** Deep external research on **Secure (Software) Development Lifecycles** and
**conformance validation**, to drive two model additions: (1) an **SDL object** with ordered,
named, dated **gates / checkpoints / milestones** and full program management, and (2)
**conformance validation** — a threat-model instance that can be *automatically* checked for
"are the threats mitigated, with approved evidence?". Plus the cross-cutting insight that a
**threat model and an SDL are both iterating, approvable *views* over the KG-as-SoT**, with
owner / change-tracking / approval / version.

**Method.** Five lanes, multi-agent (verified sources only, per PROC). Every guideline →
a `library/` record (specs get FX-1, T-029). The headline deliverable is a **requirements
crosswalk** (`MAP-0001`) showing *how the specs share / overlap common requirements*, and a
first-draft **RPT-0013** report + gap analysis. Feeds the object model (iteration 7) and the
deferred audit/compliance work (#19).

## Lane 1 — SDL / SSDL guideline landscape (collect → ingest)

Collect and ingest the major guidelines; for each capture scope, phase/gate structure,
required activities, work products, and conformance/assessment model:
- **NIST SSDF** — SP 800-218 (+ **800-218A** for generative-AI), the practice groups (PO/PS/PW/RV).
- **Microsoft SDL** — the classic phase/practice model.
- **OWASP SAMM** and **BSIMM** — maturity models (domains/practices/levels).
- **SAFECode** fundamental practices.
- **ISO/IEC 27034** (application security), **ISO/IEC 27036** (supplier), **ISO/IEC 15408/18045** (CC).
- **ISO/SAE 21434** process requirements + work products (already partly in-library) and **ISO 26262** safety lifecycle.
- **IEC 62443-4-1** (secure product development for OT/ICS).
- **CISA Secure by Design**; **SLSA** + **NIST SP 800-161** (supply chain); **PCI SSLC** where relevant.

## Lane 2 — Phases, gates, checkpoints, milestones (program management)

How each framework **names and orders** its stages, and the governance points between them:
- Extract each framework's phase/gate vocabulary (concept/plan, requirements, design, impl,
  verification, release, response) and its **gates/checkpoints/milestones**.
- Note that **corporate groups name these differently** — produce a **gate crosswalk** mapping
  each framework's gates onto a canonical, **ordered** phase line (reuse the iteration-6
  `LifecyclePhase` axis). Capture what makes a gate: entry/exit criteria, owner, approval,
  planned vs actual **dates**, dependencies — i.e. the **program-management** attributes.

## Lane 3 — Requirements mapping & overlap (the headline deliverable → MAP-0001)

The "show how specs share/overlap common requirements" ask:
- Extract **atomic requirements** from each guideline (e.g. "perform threat modeling",
  "track third-party components", "security code review before release").
- Build a **crosswalk** (`MAP-0001`): one row per common requirement, columns per spec, cells =
  the spec's clause/ID — so overlaps and gaps are visible (e.g. "threat modeling" ↔ SSDF PW.1 ↔
  MS SDL ↔ SAMM Design ↔ 21434 ↔ 62443-4-1). Enrich with where each maps onto our object model.
- Output feeds the `Requirement` object + conformance (Lane 4) and the SDL gates' exit criteria.

## Lane 4 — Conformance validation & automation

How conformance is assessed, and what we can automate:
- How each framework evidences conformance (work products, assessments, attestations, maturity
  scores) and who signs off.
- The automatable core for us: a `Requirement` is satisfied by `Mitigation`/`WorkProduct`/
  `Evidence` + an approving `Review`; a **threat-model instance** is conformant when every
  (in-scope) `ThreatInstance` has an **approved** `MitigationInstance`. Define the check(s) a
  gate's exit criterion can run (e.g. "no un-mitigated High threats", "all PW.1 evidence present").
- Relate to ISO 21434 work-products and the deferred audit model (#19).

## Lane 5 — Document governance as views over the KG

The "both are iterating views, not the SoT" insight:
- Survey how SDL/threat-model artifacts are governed in practice: **owner, change tracking,
  approval, version**. Confirm the pattern that a threat-model report and an SDL plan are
  **materialized, approvable views** whose content derives from the KG (the SoT, ADR-0004) but
  whose approval/version lifecycle is itself tracked.
- Output: the attributes a **governed document-view** needs, to fold into the §10 presentation
  layer (views) + the provenance/review spine (§4).

## Deliverables & scoring

`MAP-0001` (requirements crosswalk), library records for each guideline (FX-1 for specs), a
first-draft **RPT-0013** with gap analysis, and a concrete inputs list for the **iteration-7**
model additions (SDL/Gate/Milestone objects, Mitigation `kind`, conformance validation,
governed document-views). Flag every unverified source; a reference that informs no decision is
one we did not need.
