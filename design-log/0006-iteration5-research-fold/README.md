---
schema: "archdoc/v1"
id: DL-0006
title: "Iteration 5 — fold merged research + three decision analyses (frameworks, reification, risk)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0006
---

# DL-0006 — Iteration 5 synthesis

AI-assisted design record for #15 (per `CLAUDE.md`). Three parallel, independent analysis
agents (two on a high-effort model) attacked three questions against the merged research and
the library; their outputs were folded by hand into `ARCH-0001-PROPOSAL-v0.2.0` (proposed.5 →
proposed.6). Nothing here accepts a `DEC-*` — acceptances are ADR-only. The adversarial-critic
pass on proposed.6 is the next step (iteration 6).

## Questions (one agent each)

1. **Frameworks / DFD fold.** Now that #6 (RPT-0002) and #7 (RPT-0003) are merged, what does
   the object model need, and can the §9 "DFD-standard alignment is provisional" caveat lift?
2. **Reification (DEC-002/004).** The logical edge-reification mechanism that survives the
   Path A decision to keep RDF-vs-LPG open behind adapters.
3. **Risk metric (DEC-003).** The MVP risk scheme, Environment/exposure as inputs, no
   double-count, extensible to ISO 21434.

## What was produced → folded into proposed.6

- **§9 → partial lift.** Method-level alignment (STRIDE, attack trees, PASTA, Trike, LINDDUN,
  ATT&CK, Kill Chain) is verified from library records; **schema-level** alignment (OTM,
  threagile, pytm, Threat Dragon) is **not** — RPT-0003 is vendor-doc only, "none
  acceptance-tested", no round-trip, sources not yet records (#P1). Stale text fixed (#6/#7 are
  merged; RPT-0001 §3/§5 still stubs). Schema crosswalk + round-trip + TM-BOM stay **#9/DEC-002**.
- **§2 STRIDE.** Corrected: STRIDE is a **per-element method facet** (on the DFD target), not an
  `AttackPattern` property; generalised to a multi-valued **`method_facet`** (stride/linddun/
  maestro) + `source_method` + `violates_property`. The STRIDE↔CWE/CAPEC table is left
  **unasserted** (no source) and deferred to #9.
- **§2a attack structure.** Added AND/OR gates + `precedes` ordering + shared steps + an
  optional Kill-Chain phase tag (distinct from ATT&CK technique). Defines **R-031**.
- **§4 provenance.** Fixed the **reified `Assertion` node** as the substrate-neutral *logical
  invariant*; RDF-star / named graphs / LPG edge-properties are **adapter lowerings** (survives
  DEC-004 staying open under Path A/ADR-0003). SHACL acceptance gate; Review = STIX Opinion/Note,
  proposal kept separate from verdict. Flips **R-025 mechanism** and **R-027b** to ✅\*.
- **§3 risk.** ISO 21434-shaped `Risk = M(Impact, Feasibility)`; CVSS feasibility (a 21434-
  sanctioned method) + human S/F/O/P impact; Environment/exposure parameterise the *feasibility
  term only* (no double-count). Flips **R-023** to ✅\* at MVP. Specifies the §7 RiskScore line.
- **§5 mitigation/review enrichment** (owner, work item, verification, status; proposal vs
  verdict); the OTM semantic round-trip = the CF-008 test for DEC-002.

**Legend introduced:** ✅\* = proposed direction, accepted only when the gating DEC's ADR lands.

## Rejected / deferred (and why)

- **Did NOT accept DEC-002/003/004.** These need the sponsor's ADR (CLAUDE.md). Path A
  (ADR-0003) explicitly keeps DEC-004 (RDF vs LPG) open — so only the *logical* reification
  model is proposed, not a storage pick.
- **Did NOT assert a STRIDE↔CWE/CAPEC mapping** — the merged research does not support one.
- **Did NOT lift §9 fully** — schema alignment is unverified; forcing it would repeat the
  iteration-3 error.
- **Trike Actor/Action/Rule** and **Attack Flow schema** noted as optional/unverified, not
  adopted wholesale.

## Verification flags carried into the proposal

- Several RPT-0002 library ids were absent from the pinned submodule checkout → **re-check the
  pin** before citing.
- **ISO 21434 Annexes F/G/H** (impact + attack-potential/feasibility) are **not distilled**;
  **`first-cvss`** and **`iso-iec-18045`** are **stubs**; **RDF-star/SHACL-star** have **no
  library record**. Backlog: distill the ISO annexes + fetch `first-cvss` (gates post-MVP
  full-TARA); gather an RDF-star record (gates the DEC-002 serialization sub-decision).
- pytm licence conflict (MIT vs GPL-3.0) to resolve in #9.

## Next

Iteration 6: adversarial-critic pass on proposed.6 → fold findings; fold #9 when it lands
(closes R-024, lifts §9 fully); build the §8 MVP vectors. Then ADRs accept **DEC-003** and the
**DEC-002/004 logical reification model** (ready now), and **DEC-001** last.
