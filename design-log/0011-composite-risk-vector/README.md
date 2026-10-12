---
schema: "archdoc/v1"
id: DL-0011
title: "Sponsor round — composite risk vector; disposition of the bot-authored ADR-0005"
type: process
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-02"
record: DL-0011
---

# DL-0011 — Composite risk vector (and dropping ADR-0005)

AI-assisted design record for #15 (per `CLAUDE.md`). A **grok bot** authored
`spec/ADR-0005-composite-risk-vector.md` on branch `doc/adr-0005-composite-risk-vector` (PR #70),
self-marked `status: accepted` / `decision_makers: nymble` / "Accept DEC-003". The sponsor
reviewed it and made two calls; this records them and the fold into proposed.10.

## What the bot's ADR-0005 proposed

Risk as a **composite vector** — attack feasibility (Common Criteria-style) + impact (S/F/O/P) +
mitigation status + a derived Risk + an extension point — "tightening" ARCH-0001-PROPOSAL proposed.7.

## Assessment (surfaced to the sponsor)

- **Governance: did not meet the bar.** It edited `DECISIONS-0001` only — **no ARCH-0001 §8 update,
  no CHANGELOG, no sponsor sign-off in fact** (a bot asserting acceptance is not acceptance). Per the
  one hard rule, that is not a valid DEC acceptance.
- **Substance: mostly compatible + one good idea.** "Vector, not a lone scalar" matches proposed.9
  ("keep the per-category vector; collapse is display-only"); **mitigation status as a first-class
  field** is a genuine improvement (matches critic M9 + PLAN-0002 Slice 1). It is **not** the
  parallel-schemes composite the iteration-5 analysis rejected as double-counting.
- **One real divergence: Common Criteria feasibility.** The iteration-5 risk research **down-selected
  CC / ISO 18045** for the MVP (heaviest method; `iso-iec-18045` is a library stub) in favour of
  **ISO 21434 Table-1 path-level feasibility** (proposed.9). It was also written against proposed.7,
  behind the critic-corrected proposed.9.

## Sponsor decisions (2026-10-02)

1. **Fold the idea into proposed.9; drop the standalone ADR.** → Folded into proposed.10 (below);
   **ADR-0005 branch/PR #70 dropped** (branch deleted; commit `51dc17b…` recoverable; #70 commented).
2. **MVP feasibility = ISO 21434 Table-1 (method); CC-style display.** → feasibility *computation*
   stays the ISO 21434 path-level 4-point rating; **CC is presentation only** (numbers + label +
   colour); CC/18045 is not the MVP method.

## Folded into proposed.10

- **§3:** risk reframed as a **composite risk vector** — {feasibility, per-category impact,
  **mitigation status** (R-045, peer field reading `MitigationInstance.status`), derived
  `Risk=M(I,F)`}; the derived field is shown alongside its inputs, never instead; a lone CVSS-like
  score is not the scheme. **Display is CC-flavoured; the method stays ISO 21434 Table-1.**
- **§6 matrix:** R-045 (composite risk vector) → ✅\* (MVP; proposes DEC-003).
- **§7 MVP:** the RiskScore row is now the composite vector (incl. mitigation-status column — MVP).
- **§12:** DEC-003 strengthened but **still open**; accepts later via **one clean ADR** with full
  governance (not the bot's ADR-0005).

## Rejected / adapted

- **Rejected** the bot's self-acceptance and CC-as-method; **dropped** ADR-0005.
- **Adapted:** kept the vector shape + mitigation-status (good), bound feasibility to ISO 21434
  Table-1 (research), made CC display-only.
- **Governance note for future bot output:** an ADR that self-marks `accepted` without a PR, ARCH §8
  status update, and CHANGELOG line is **not** an accepted decision — treat as a proposal and verify
  the sponsor actually decided.

## Next

The derived-`Risk` aggregation function + the human-reviewed ISO 21434 extraction gate the clean
DEC-003 ADR. A fresh adversarial-critic pass runs before that ADR.
