---
schema: "archdoc/v1"
id: DL-0008
title: "Iteration 6 — parties/orgs, lifecycle + returns, stakeholder-relative TARA, schema (LinkML)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0008
---

# DL-0008 — Iteration 6 sponsor round

AI-assisted design record for #15 (per `CLAUDE.md`). A sponsor design round on
`ARCH-0001-PROPOSAL` (proposed.7 → proposed.8). Four substantive additions, folded by hand.
Nothing here accepts a `DEC-*` (ADR-only). A fresh adversarial-critic pass runs next.

## Questions asked (sponsor)

1. **Do we need to model companies / standards groups / other such entities?** They are
   referenced by CVEs and by products / product families.
2. **Lifecycle — think deep.** Concept, architecture, design, implementation, … — *every step
   in a product's life is a place with different threats; this must be captured.* And **product
   returns**?
3. **TARA — asset ownership drives impact.** Assets should have an **owner**, which determines
   the impact (consumer vs service operator vs product manufacturer vs chip manufacturer).
4. **Schemas — what syntax, which objects, in a way we can iterate on schemas?**

## What was produced → folded into proposed.8

- **§2b `Party`/Organization (R-036).** One `Party` node with **roles** (vendor, product vs chip
  **manufacturer**, supplier, operator, consumer, **owner**, **standards-body**, **CNA**,
  regulator) rather than a class per role. Attaches to: CVE/Finding (`reported_by` CNA, `affects`
  vendor), Product/Family (`manufactured_by`/`supplied_by`), library standards (`published_by`
  ISO/NIST/MITRE), Asset (`owned_by` → TARA). Reusable/shared node; typed edges per ADR-0004.
- **§3b lifecycle axis (R-037) + reverse logistics (R-038).** A `LifecyclePhase` (concept →
  architecture → design → implementation → V&V → production → distribution → deployment →
  operation → maintenance → end-of-support → decommission), with threats/mitigations/attack
  surfaces **scoped by `applies_in_phase`** — "every step is a different place with different
  threats." It is a **state machine, not a line**: **returns/RMA → refurbish → resell/redeploy →
  recycle/dispose**, carrying their own threats (data remanence, counterfeit re-insertion, changed
  provenance when a unit re-enters operation under a new owner). An **axis**, cross-cutting
  structure/threat/risk/provenance — not a new layer.
- **§3 stakeholder-relative impact (R-039).** `Asset.owned_by` a Party; a `DamageScenario`'s impact
  becomes a **(category, stakeholder-role, severity)** tuple — the same damage weighs differently
  for consumer vs operator vs product-mfr vs chip-mfr; the owner determines whose impact the
  `RiskScore` uses. Generalises ISO 21434's fixed road-user stakeholder to the multi-domain owner.
- **§13 schema definition — LinkML (proposes DEC-002's IDL).** Author the model as **LinkML** YAML
  in `spec/schema/`; generate JSON Schema + SHACL (the §4 gate) + Python types; objects = classes,
  typed edges = slots (reviewed edges reified as `Assertion`). **Iteration:** schema is versioned,
  changed by PR, CI regenerates validators and runs the §8 vectors against them (a schema change
  that breaks a vector fails CI). Substrate-neutral (survives DEC-004); local/non-MITRE extensions
  are just added classes/instances.

## Scope held (MVP)

Party (minimal: CVE vendors/CNAs, manufacturer, owner), lifecycle phase (**enum +
`applies_in_phase` on one worked example**), and stakeholder impact (**one stakeholder per asset**)
are MVP. The full role set, the lifecycle **state machine + returns branch**, and multi-stakeholder
impact are **post-MVP**.

## Rejected / deferred

- Did **not** accept any DEC (ADR-only). Did **not** make lifecycle a new layer (it's an axis).
- Did **not** model role subclasses (one `Party`, many roles) — avoids a combinatorial type tree.
- LinkML is proposed as the **IDL**; the *interchange/export* formats stay ADR-0004 + the OTM
  round-trip (#9) — not conflated.

## Next

Fresh adversarial-critic pass on proposed.8 → fold. Pilot the LinkML schema (lane #64). Then the
ADRs (§12), DEC-001 last.
