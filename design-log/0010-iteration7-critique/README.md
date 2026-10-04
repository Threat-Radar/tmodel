---
schema: "archdoc/v1"
id: DL-0010
title: "Adversarial critique of proposed.8 → proposed.9 (iteration-7 pass)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0010
---

# DL-0010 — Adversarial critique of iteration 6 (proposed.8)

AI-assisted design record for #15 (per `CLAUDE.md`). An independent adversarial-critic agent
(fresh context, high-effort model) attacked `ARCH-0001-PROPOSAL` proposed.8, focused on the
iteration-6 additions (§2b parties, §3b lifecycle, §3 TARA R-039, §13 LinkML, §7 MVP). **14
findings (5 high, 7 med, 2 low).** Folded into proposed.9.

## Two false positives (stale-checkout artifact — not acted on)

The critic cross-referenced an **un-updated `main` working tree** and so reported:
- **H1** "ADR-0004 / DEC-011 do not exist / are fabricated." **They exist** — merged via #56
  (ADR-0004, DEC-011 in DECISIONS-0001 + ARCH §8, CHANGELOG 0.1.6). The stale checkout predated #56.
- **L2(a)** "no `design-log/0008` entry." **It exists** on the proposed.8 branch (#66). The critic
  checked the stale `main`, not the branch.

Lesson recorded: keep the `main` working tree synced; a reviewer reading stale `main` mis-fires.
(Verified on `origin/main` before dismissing.)

## Accepted → folded into proposed.9

High:
- **H2 — `RiskScore` undefined across multi-owner paths; "no aggregation" contradicts RQ-15-16.**
  Defined multiplicity: one value 1–5 per (threat-scenario[, impact-category][, stakeholder]);
  feasibility aggregated over the attack-path set (worst path); "no aggregation" clarified to mean
  *no cross-category collapse*, not "no value"; cross-owner paths report a score **per affected
  owner** (no fictional single path-owner).
- **H3 — "owner determines impact" overloads ISO S/F/O/P.** Kept S/F/O/P fixed to the end-beneficiary
  (comparability); added a **separate `business_impact` axis** for owner/operator/manufacturer views,
  assessed *in addition to* S/F/O/P, not a relabelling.
- **H4 / L1 — LinkML overstated.** No first-class LPG generator (pinned record `summarized`, lists
  JSON-Schema/SHACL/OWL/RDF only); `gen-shacl` is structural, the §4 conditional gate needs
  hand-written SHACL; the "schema change fails CI" loop is a lane-#64 **future** deliverable
  (`spec/schema`/`spec/vectors` are stubs). Flagged the record as summarized-only.
- **H5 — MVP overloaded.** Pushed **Party, lifecycle, and stakeholder-impact entirely to post-MVP**
  (model-only, like DFD/networks/Environment); MVP risk stays single end-user + simple.

Med:
- **M1** unified `Party`/`ThreatActor`/PROV-`Agent` as facets of one identified entity + dedup rule.
- **M2** relational roles (supplier/operator/owner/…) moved to **edges**; only intrinsic
  classifications (standards-body, cna) on the node.
- **M3** lifecycle "state machine" softened to a **phase enum tag**; the state machine is future work.
- **M4** named **`ProductInstance`** as the state-bearing entity; flagged the missing **temporal axis**
  (`valid_from`/`valid_to`) to add with it; reconciled identity-by-hash vs lifecycle state.
- **M5** custody/returns provenance = supply-chain class §4 defers → **post-MVP / radar contract**,
  not the in-model epistemic Assertion spine.
- **M6** bounded `applies_in_phase` (coarse lifecycle stage) vs `Environment` (runtime exposure) —
  one axis per threat, no double-model.
- **M7** fixed leftover "ADR-0003 in review / gated on #48" text in §7/§10 → **accepted (ADR-0003)**.

Low:
- **L2(b)** publishers reference the **library record's** publisher, not a parallel Party registry.

## Rejected / adapted

- Nothing rejected on merit; H1 and L2(a) dismissed as stale-checkout false positives (verified).
- Adapted scope: the whole iteration-6 feature set is now **post-MVP** (H5) — the right call given
  ADR-0002's "achievable beats ambitious."

## Next

SDL round (DL-0009) folds in iteration 8 after RPT-0013 lands. Add the temporal axis (M4), author
the LinkML schema (lane #64), build the §8 MVP vectors, then the ADRs (§12), DEC-001 last.
