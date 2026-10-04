---
schema: "archdoc/v1"
id: MAP-0001
title: "SDL requirements crosswalk — how the secure-development frameworks overlap"
short_title: "SDL requirements crosswalk"
description: "First-draft crosswalk of 19 atomic secure-development requirements across 7 frameworks (NIST SSDF, Microsoft SDL, OWASP SAMM, BSIMM, ISO/SAE 21434, IEC 62443-4-1, SAFECode), with a canonical phase line. Shows the big overlaps and the real divergences. Evidence for RPT-0013 and the iteration-8 SDL model; cells flagged 'approx' need verification, and the guidelines still need library records (T-029)."
type: mapping
category: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
needs_review: true
reviewed: false
canonical_path: spec/MAP-0001-sdl-requirements-crosswalk.md
defers_to: ARCH-0001
agent_notes: >
  First draft from RPT-0013 Lane 3 (multi-agent). Framework STRUCTURES verified against primary
  sources; atomic cell mappings cited to those structures. A "cell" means different things per
  column (hard requirement vs maturity activity vs named practice) — see the note. Cells marked
  'approx' and the IEC/ISO work-product IDs need verification before this is accepted; the
  guidelines are not yet library records (T-029). Feeds the Requirement object + conformance (R-042/R-044).
---

# MAP-0001 — SDL requirements crosswalk (first draft)

Maps **19 atomic secure-development requirements** across **7 frameworks**. It answers the
sponsor's "show how the specs share/overlap common requirements". **Caveat:** a cell means
different things per column — a **hard requirement** (ISO 21434, IEC 62443-4-1), a **maturity
activity** (SAMM, BSIMM), or a **named practice** (current Microsoft SDL has no IDs). Cells marked
*approx* lack a dedicated clause; IEC/ISO requirement/work-product IDs need verification against the
purchased standards. Guidelines are **not yet library records** — ingestion is T-029/T-033.

## Crosswalk (row = requirement; blank = absent / not a dedicated clause)

| # | Requirement | NIST SSDF | MS SDL (current 10) | OWASP SAMM v2 | BSIMM | ISO/SAE 21434 | IEC 62443-4-1 | SAFECode 2018 |
|---|---|---|---|---|---|---|---|---|
| 1 | Security training / competence | PO.2.2 | #10 Training | Governance › EG | T | Cl.5.4.3 *approx* | SM-4 *approx* | Expertise & Skill *approx* |
| 2 | Define security requirements | PO.1.1 | #1 standards/governance | Design › SR | SR | Cl.9.4/9.5, 10.4.1 | SR-3, SR-4 | ASC Definition |
| 3 | **Threat modeling / TARA** | PW.1.1 | #3 design review & TM | Design › TA | AA+AM *approx* | **Cl.15 TARA** + 9.4; 8.5 | **SR-2** | Design › Threat Modeling |
| 4 | Secure design principles / defense-in-depth | PW.1 | #2 proven features *approx* | Design › SA | SFD | Cl.10.4.1 *approx* | **SD-1, SD-2** | Secure Design Principles |
| 5 | Secure design / architecture review | PW.2 | #3 | Verification › AA | AA | Cl.10.4.1/.2 *approx* | **SD-3** | *approx* |
| 6 | Cryptographic standards | PW.5/PW.9 *approx* | #4 crypto standards | *none dedicated* | SFD/SR *approx* | *none dedicated* | SD-4, SM-8 *approx* | Encryption Strategy |
| 7 | Third-party components / SBOM / supply chain | PW.4 (+PO.1.3, PS.3.2) | #5 supply chain | Impl › SB; SR | SR/SE *approx* | Cl.7 + 15.x | **SM-9, SM-10** | Third-Party Components |
| 8 | Approved tools / secure toolchain | PO.3.2 | #6 eng environment | *within SB* | SE *approx* | Cl.6 *approx* | SM-7 *approx* | Code Analysis Tools *approx* |
| 9 | Secure coding standards | PW.5 | #2 *approx* | EG/SB *approx* | CR/SR *approx* | Cl.10.4.1 *approx* | **SI-2** | Coding Standards |
| 10 | Static analysis / code review (SAST) | PW.7.2 | #7 security testing | Verification › ST | CR | Cl.10.4.2 *approx* | **SI-1** + SVV | Code Analysis Tools |
| 11 | **Security testing before release** | PW.8 | #7 | Verification › ST+RT | ST | Cl.11 + 10.4.2 | **SVV-1, SVV-2, SVV-3** | Testing & Validation |
| 12 | Penetration testing | PW.8 *approx* | #7 | Verification › ST | PT | Cl.11 *approx* | **SVV-4** | Manual Testing |
| 13 | Secure build & release integrity / provenance | PW.6 + PS.1/.2/.3 | #5 *approx* | Impl › SB+SD | SE *approx* | Cl.12 *approx* | SM-6 *approx* | *thin/blank* |
| 14 | Secure default config / hardening guidance | PW.9 | #8 platform security *approx* | Operations › EM *approx* | SE | *none dedicated* | **SG-1, SG-3** | *thin/blank* |
| 15 | Release gate / security sign-off | PO.4.1/.4.2 | #1 *approx* | Governance › PC *approx* | CP/SM *approx* | Cl.6 release-for-post-dev *approx* | SM-12 *approx* | Risk Acceptance *approx* |
| 16 | Protect dev environment & source integrity | PO.5 + PS.1 | #6 | Operations › EM *approx* | SE | Cl.5/6 *approx* | **SM-7**, SM-6, SM-8 | *approx/blank* |
| 17 | Vulnerability / defect management | RV.1+RV.2(+RV.3) | #9 monitoring & response *approx* | Impl › DM | CMVM | **8.5, 8.6** | **DM-1..DM-4** | Manage Security Findings |
| 18 | Vulnerability disclosure & response | RV.1 | #9 | Operations › IM *approx* | CMVM | 8.3, 8.4 | **DM-5** + SUM-1..5 | Vuln Response & Disclosure |
| 19 | Security monitoring & incident response (ops) | RV.1 *approx* | #9 | Operations › IM | CMVM/SE | **13.3** + 8.3 | *→ 62443-2-1/3-3* | *approx* |

## Biggest overlaps (nearly everyone mandates)

1. **Threat modeling / risk assessment (row 3)** — all 7 (only the vocabulary differs; automotive = TARA). The single most universal requirement — and the anchor for tmodel.
2. **Security requirements (row 2)** — all 7.
3. **Security testing before release (row 11)** — all 7 (IEC most granular, SVV-1..4).
4. **Vulnerability management + disclosure (rows 17–18)** — all 7 (RV / DM / CMVM / Cl.8 near-identical).
5. **Third-party / supply-chain (row 7)** — all 7, fastest-growing (SBOM now explicit in SSDF PW.4, MS #5).
6. **Secure design & architecture review (rows 4–5)**; **secure coding (rows 9–10)** — all 7.

## Notable divergences

- **Crypto standards (row 6):** first-class only in MS SDL (#4) and SAFECode; others fold it into generic secure-design/coding.
- **Secure build / provenance (row 13):** strong in SSDF (PS.1/.2) + MS; weak/implicit elsewhere.
- **Hardening / secure defaults (row 14):** IEC 62443-4-1 (SG) by far the most prescriptive; most others thin.
- **Operational IR (row 19):** IEC 4-1 stops at development (ops IR → 62443-2-1/3-3); ISO 21434 (13.3) and MS (#9) own it.
- **Release gate / sign-off (row 15):** everyone implies a gate; only SSDF (PO.4) names it as a discrete auditable practice — a maturity differentiator (and the hook for our SDL `Gate` exit-criteria).

## Canonical phase line (gate/checkpoint crosswalk)

`concept → requirements → design → implementation → verification → release → response`

| Canonical phase | SSDF | MS SDL | SAMM | BSIMM | ISO 21434 | IEC 62443-4-1 | SAFECode |
|---|---|---|---|---|---|---|---|
| Concept | PO.1 | (in Req) | Design › TA | Intelligence | **Cl.9** (+TARA Cl.15) | SR-1 | ASC Definition |
| Requirements | PO.1, PW.1.1 | Requirements | Design (TA, SR) | Intelligence | 9.4/9.5, 10.4.1 | SR | ASC Definition |
| Design | PW.1, PW.2 | Design | Design (SA)+Verif(AA) | Intel(SFD)+Touchpoints(AA) | 10.4.1 | SD | Design |
| Implementation | PW.5/.6/.7 | Implementation | Impl (SB, SD, DM) | Touchpoints (CR) | 10.4.1 | SI | Secure Coding |
| Verification | PW.7/.8, PO.4 | Verification | Verification (AA,RT,ST) | Touchpoints(ST)+Deploy(PT) | **Cl.11** + 10.4.2 | SVV | Testing & Validation |
| Release | PS.1/.2/.3, PO.4 gate | Release | Impl › Secure Deployment | Deployment (SE) | Cl.6 release, Cl.12 | SM-6, SG | Manage Findings |
| Response / Operations | **RV.1/.2/.3** | Response (#9) | Operations (IM,EM,OM) | Deployment › CMVM | **Cl.13** + Cl.8 | DM, SUM (dev-side) | Vuln Response |
| *Spanning* | PO.2/.3/.5 | #1,#6,#10 | Governance | Governance | Cl.5–7, Cl.8 | SM, SG | Planning |

**Note:** SSDF and BSIMM are deliberately org/domain-structured, not phase-ordered; their cells are best-fit (approx).

## Verify before acceptance (flagged by the research)

1. IEC 62443-4-1 exact requirement titles/IDs (SR-2, SVV-4, SG-3, DM-5) — source PDF was 403.
2. ISO/SAE 21434 work-product IDs (WP-xx-yy) — clause numbers cited; WP codes need the purchased standard.
3. BSIMM activity-number cells (edition-dependent) — practice codes used are stable.
4. The *approx* cells (crypto, hardening, build/provenance, gates).
5. MS SDL: track the current 10-practice list (used here) vs the legacy 12-practice list.

## Use in the model (iteration 8)

Each row becomes a `Requirement` with cross-spec `maps_to` edges (R-044); a `Gate`'s exit criteria
reference the requirements due by that phase; conformance (R-042) checks a product's threat model +
mitigations against the applicable rows. Guidelines must be ingested as library records first (T-033/T-029).
