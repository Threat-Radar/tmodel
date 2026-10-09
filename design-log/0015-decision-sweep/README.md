---
schema: "archdoc/v1"
id: DL-0015
title: "Decision sweep — accept DEC-002/003/004, refine DEC-010 (engine split)"
type: decision
status: accepted
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: DL-0015
---

# DL-0015 — decision sweep (2026-10-08)

## Question asked

Sponsor: *"step through a review of each open decision/design, then update architecture, plan,
design doc, app plan with correct details."* Triggered by *"KG engine — could it be Rust? Is
Python more mature?"* We reviewed all six open DEC-* plus the two open design points (A-044 viz,
engine language) and the sponsor ruled on four via AskUserQuestion.

## What was produced

Four ADRs (the only place a DEC flips) + synced docs, one PR.

| ADR | Decision | Accepts |
|---|---|---|
| **ADR-0006** | Risk = composite vector (feasibility [ISO 21434 Table-1] + impact [S/F/O/P] + mitigation-status + derived risk; CC display-only) | DEC-003 |
| **ADR-0007** | LinkML canonical IDL; generated JSON-Schema/SHACL; import OTM + STIX 2.1; export JSON-LD/Turtle/GraphML/CSV | DEC-002 |
| **ADR-0008** | Oxigraph (embedded RDF, SPARQL, RDF-star) as the working store, behind the ADR-0004 façade | DEC-004 |
| **ADR-0009** | Engine language split: Python brain (LinkML/extraction/CLI) + Rust store/hot-paths | refines DEC-010 / amends ADR-0003 |

Docs synced: ARCH-0001 (§5/§6/§8 + status banner, v0.1.7) + changelog; DECISIONS-0001 (v0.1.7);
PLAN-0001 (I2–I4 + decisions-status, v0.1.3); PLAN-0002 (engine/store/interchange, v0.1.1);
ARCH-0001-PROPOSAL (dependency note + §3 risk ratified, proposed.12); APP-0001 (§6 + A-044
direction, v0.2.2).

## Decisions / rejections

- **Engine: Python brain + Rust store** (not all-Rust). Rejected all-Rust: it would reimplement or
  forgo the LinkML + extraction ecosystem (both Python-only), for a one-semester team, to buy
  single-binary packaging. The A-030 API boundary keeps the choice reversible, so the cost of
  staying Python-for-the-brain is low. Rust owns the store (Oxigraph) and, later, PyO3 hot paths.
- **DEC-002: committed interchange now** (the sponsor chose this over "defer to the crosswalk").
  Pinned OTM + STIX 2.1 import / JSON-LD+Turtle+GraphML+CSV export; the #39 crosswalk may *extend*
  import coverage but cannot change the canonical IDL.
- **DEC-004: Oxigraph/RDF over LPG.** RDF-star matches the reified-Assertion provenance directly;
  SPARQL/SHACL align with the standards track; Oxigraph is Rust, unifying with the shell. The LPG
  edge view stays available through the façade's edge adapter for the viz layer.
- **Numbering:** started at ADR-0006. **0005 is left a deliberate tombstone** (withdrawn
  composite-risk-vector draft, closed #70) so existing "ADR-0005 was dropped" references stay true;
  ADR-0006 records that it supersedes that draft.

## Kept open (with gates)

- **DEC-001** object model — gated on #104 Stage 2 (schemas filled) + Stage 3 (extraction vectors).
- **DEC-008** CWE/NVD — leaning cached local mirror (A-043 offline + A-044 licensing); not yet an ADR.
- **DEC-009** threat→product / mitigation-lifecycle — depends on DEC-001.
- **A-044** viz library — direction set (open WebGL first); concrete pick deferred behind the adapter.

## Next

Sponsor merges the PR (tmodel `main` is protected). DEC-008 is a quick follow-up ADR if the sponsor
wants the cached-mirror leaning ratified. The ADR-0008 store pick feeds the #50/#51/#52 façade/loader
tasks (now targeting Oxigraph).
