---
schema: "archdoc/v1"
id: DL-0004
title: "Adversarial critique of iteration 3 → iteration 4"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0004
---

# DL-0004 — Adversarial critique of iteration 3

AI-assisted design record for #15 (per CLAUDE.md). An independent adversarial-critic
agent attacked iteration 3 (three layers). 13 findings (4 high, 5 med, 4 low).

## Verdict
Additions individually plausible, but the model **double-modeled reality on three axes**
(Component vs Process/DataStore; network reachability vs adversary reachability;
Assertion-reification vs PROV-O-Processes), ran **two threat taxonomies** (STRIDE vs
BRON) and **two provenance mechanisms** without crosswalks, and **claimed DFD-standard
alignment ahead of the #9 research** that would prove it.

## Accepted → folded into iteration 4
- **F1** one-artifact rule: `Component` authoritative; DFD elements projected via `realized_by`/`runs_on`/`stored_in`.
- **F2** STRIDE is a **facet** of the single `ThreatInstance`/CWE/CAPEC vocabulary, not a parallel list; reachability unified (connected_via → precondition → pivots_to).
- **F3** explicit **MVP/post-MVP table** (§7); the MVP is the **attack-path KG**, not a DFD tool; DFD/networks/Deployment/provenance modeled but not built for Nov 5.
- **F4/F11** added **data classification** (R-029) + workflow ordering (R-031) + entity/agent trust (R-032) + element security properties; R-024 → ◐.
- **F5/F9** Environment is a first-class reusable **node** and a **risk *input* that parameterizes** the metric (no double-count); R-023 → ◐ (gated DEC-003).
- **F6** one **provenance spine**: PROV-O nodes + reified `Assertion` pointing at the generating Activity.
- **F7** **compile/SLSA build provenance → radar→tmodel imported attestations** (out of MVP); only AI-generation provenance stays in-model.
- **F8** matrix fixed: split R-027 (propagation ✅ / VEX ◐); R-025 ◐.
- **F10** attacker-position-on-network as a precondition type; element properties drive STRIDE.
- **F12** TrustBoundary as a **zone** (`in_trust_zone`), boundary-crossing derived.
- **F13** interchange/layout + tool-incompatibility flagged for #9/DEC-002.

## Adapted / noted
- Kept the DFD/networks/provenance **in the model** (the sponsor requested them) but
  marked **post-MVP** per F3 — reconciles "represent it" with "don't build it for Nov 5."
- DFD-standard alignment marked **provisional** (RPT-0001 §3/§5 pending; only RPT-0003 verified).
- Nothing rejected outright.

## Next (iteration 5)
Fold research #6/#7/#9; **decide reification (DEC-002/004) and the risk metric (DEC-003)**
— these flip the ◐s; build the MVP vectors; then fold into ARCH-0001 §3/§4 and accept
DEC-001 via an ADR.
