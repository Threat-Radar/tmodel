---
schema: "archdoc/v1"
id: DL-0007
title: "Adversarial critique of proposed.6 → proposed.7 (iteration-6 pass)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0007
---

# DL-0007 — Adversarial critique of iteration 5 (proposed.6)

AI-assisted design record for #15 (per `CLAUDE.md`). An independent adversarial-critic agent
(fresh context, high-effort model) attacked `ARCH-0001-PROPOSAL` proposed.6, cross-checking every
load-bearing claim against ARCH-0001, the ADRs, DECISIONS-0001, APP-0001, RPT-0002/0003/0011, and
the **pinned** `library/records/`. **14 findings (5 high, 7 med, 3 low).** All folded into
proposed.7.

## Verdict
The iteration-5 additions were individually plausible but the proposal **over-claimed**: it
leaned on a not-yet-accepted decision (ADR-0003), chose a risk feasibility term that re-imported
impact, mis-attributed attack-tree math to ISO 21434, made its acceptance gate silently
RDF-only, and marked things "verified"/"ADR-ready" that the pinned evidence did not support.

## High — folded
- **H1 ADR-0003 is not accepted** (it is in review, PR #48; absent from `main`). Removed every
  "accepted Path A" lean; the §4 substrate-neutrality now stands on the logical model alone; added
  a dependency note.
- **H2 CVSS-as-feasibility re-imports impact** (violates `iso-sae-21434#RC-15-13` and the §3 F5
  double-count ban: CVSS *base* blends impact, environmental CIA scales impact). Fixed: MVP uses
  **no CVSS**; the post-MVP CVSS option uses **exploitability metrics AV/AC/PR/UI only**; Environment
  feeds exploitability/window-of-opportunity, **never CIA**.
- **H3 R-023 ✅\*-at-MVP contradicts §7** (Environment is post-MVP; single deployment assumed) **and
  §8** (an MVP vector used an Environment parameter). Moved **R-023 to post-MVP**; removed the
  Environment parameter from MVP vectors.
- **H4 the SHACL gate makes §4 RDF-only**, and "always reify to a node" quietly pre-decides part of
  DEC-004. Fixed: gate stated substrate-neutrally (SHACL on RDF *or* equivalent LPG checks); admitted
  node-reification **narrows** DEC-004 (no pure edge-property option for reviewed assertions).
- **H5 per-step min/max feasibility mis-attributed to 21434 Table 1** (Table 1/`RQ-15-10` rates the
  *path*; attack-potential `RC-15-12` *compounds* factors). Fixed: MVP rates feasibility at the
  **path level**; per-step AND/OR min/max is re-attributed to **attack-tree semantics** as a
  deliberate post-MVP deviation.

## Med — folded
- **M6** "method alignment verified" → "asserted by **draft** RPT-0002 (`reviewed:false`); **5 of 6**
  cited records absent from the pin — ingest before any ADR" (§9).
- **M7** MVP risk over-specified vs ADR-0002 "simple" and rests on the `first-cvss` stub → MVP
  collapsed to path-level 4-point × S/F/O/P, human-rated, no CVSS.
- **M8** interactive graph view is MVP while DEC-006/010 are open → marked **gated on the stack ADR
  (#48) landing first**; MVP bar dropped to "a working single projection" (best-in-class = post-MVP).
- **M9** ADR-0002's demo requires visible mitigation state, missing from §7 MVP → added a minimal
  **MitigationInstance + mitigation-state** MVP row.
- **M10** the "annexes not distilled" caveat mis-stated the gap (the material *is* extracted) → the
  real issue is `audit_status: not-reviewed` + OCR spillover; caveat corrected.
- **M11** R-025 ✅\* leaned on a provenance step §7 marked "if time" → minimal Assertion+Review
  provenance committed as **firm MVP**; "if time" removed.
- **M12** "scalar I = max" ≠ 21434 (per-category risk) → keep the **per-category S/F/O/P vector**;
  any collapse is an explicit display simplification.

## Low — folded
- **L13** the matrix read as scoring vs a ratified baseline → relabelled "proposed requirements
  (several not yet in ARCH-0001 §4)".
- **L14** R-031 (AND/OR + ordering) is the soundest ✅\* (credit) — but the kill-chain and Attack
  Flow records are unpinned; noted.
- **L15** LINDDUN/MAESTRO records absent at the pin → marked "not yet pinned"; the §2 STRIDE↔property
  mapping and LINDDUN nuance *do* check out against RPT-0002.

## Rejected / adapted
- Nothing rejected outright — the critique was sound and sharpened the honesty of §3/§4/§9/§12.
- **Adapted:** proposed.6 said DEC-003 and the reification model were "ADR-ready now"; §12 now says
  **not yet** and lists the blockers (pin records, reviewed ISO extraction, RDF-star record,
  sponsor acceptance that node-reification narrows DEC-004).

## Next
Pin the 5 absent method records + a reviewed ISO 21434 extraction + an RDF-star record; fold #9;
build the §8 MVP vectors; then the ADRs (§12), DEC-001 last.
