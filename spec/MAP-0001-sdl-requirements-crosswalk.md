---
schema: "archdoc/v1"
id: MAP-0001
title: "SDL requirements crosswalk — how the secure-development frameworks overlap"
short_title: "SDL requirements crosswalk"
description: "Consolidated crosswalk of 34 atomic secure-development requirements across 16 frameworks (NIST SSDF 1.1, Microsoft SDL + SDL 5.2, OWASP SAMM 2.2, BSIMM16, ISO/SAE 21434, IEC 62443-4-1, SAFECode FPSSD3, EU CRA, ETSI TS 104 219, BSI TR-03185, UK Software Security CoP, OpenSSF OSPS Baseline, SLSA 1.2, OWASP ASVS 5, FDA 2026, ENISA SbD playbook). Every cell is built from verified library records, with the publisher of each mapping or an explicit ours-judgement. Shows the overlaps, the divergences, the contradictions between published mappings, and the canonical phase line. Evidence for RPT-0013 and the iteration-8 SDL model."
type: mapping
category: process
status: draft
version: "0.2.0"
date: "2026-10-01"
updated: "2026-10-03"
version_policy: "semver; 0.x while draft; the companion MAP-0001.yaml carries the same version"
reviewers:
  - role: adversarial-critic
    id: agent-map-0001-review-2026-10-03
    round: crosswalk-v0.2.0 (findings folded in before filing; see the last section)
needs_review: true
reviewed: false
canonical_path: spec/MAP-0001-sdl-requirements-crosswalk.md
defers_to: ARCH-0001
agent_notes: >
  v0.2.0 rebuilt from the verified library records of topic sdl (library-sdl worktree). Hub = SSDF 1.1 tasks;
  cells carry the target record's own ids, each with provenance (anchor / direct / chained / bridge / ours) and
  edition. The full 34 x 16 matrix with per-id provenance, not-adopted published ids, old-edition ids and the
  contradiction list is in the companion MAP-0001.yaml. ISO/SAE 21434, FDA and most SDL 5.2 cells are judgement-only
  (no publisher maps them). An adversarial review (2026-10-03) re-verified every source-claimed id against the publishers' raw
  records, enforced the one-hop chaining rule and removed or re-rowed indefensible judgement cells (last section).
  Human review (pass 4) outstanding. Feeds the Requirement object + conformance (R-042/R-044).
---

# MAP-0001 — SDL requirements crosswalk (v0.2.0)

Maps **34 atomic secure-development requirements** across **16 frameworks**. It answers the sponsor's question "show how the specs share or overlap common requirements", now with evidence. Each cell holds the framework's **own ids** from a verified library record, and each id states **who published the mapping**: the SSDF 1.1 References column, ETSI TS 104 219 Annexes A/B, the OWASP SAMM mappings, BSIMM16 Tables 3–4, OSPS Baseline mappings, BSI TR-03185/TR-03183-1, ENISA Annex C, or **ours** (our judgement from reading both records, with a one-line rationale in the YAML).

**Caveat.** A cell still means different things per column: a hard requirement (ISO 21434, IEC 62443-4-1, CRA, TR-03185, OSPS, SLSA), a maturity activity (SAMM, BSIMM), a named practice (MS SDL, SAFECode), a verification item (ASVS) or a regulator's recommendation (FDA, ENISA, UK CoP). The full matrix is in **`MAP-0001.yaml`** (same directory as this file when filed): every row × every framework, per-id provenance, editions, the published ids we did not adopt, old-edition ids, and the contradiction list.

## Changelog vs v0.1.0

- **Evidence.** v0.1.0 cells were cited to framework structures; 42 of its 133 cells were marked *approx* and 7 *none dedicated*, *thin* or *blank* (one cell both). v0.2.0 rebuilds every cell from library records (all ids validated against the target `requirements.yaml`) and replaces *approx* with a publisher (`src`) or an explicit `ours` rationale. Of the 1,030 ids placed, 90 are row anchors, 391 are directly source-mapped to the anchor, 87 come through one published hop, 4 through a non-column publisher ("bridge"), and 458 are ours.
- **Columns 7 → 16.** Added EU CRA, ETSI TS 104 219, BSI TR-03185, UK CoP, OSPS Baseline, SLSA 1.2, OWASP ASVS 5, FDA 2026, ENISA playbook; SDL 5.2 sits in the MS SDL column. Editions are now explicit: SAMM 2.2 (not "v2"), BSIMM16 (not unnumbered), SAFECode FPSSD 3rd ed. (2018).
- **Rows 19 → 34, numbering kept.** Rows 1–19 keep their numbers. Narrowed: row 7 no longer carries SBOM or provenance; row 13 is release integrity only (signing/hashes/archiving), with compiler/build hardening (PW.6) moved to row 8; row 18 is post-release vulnerability monitoring/investigation, with disclosure policy split out. New: 20 SBOM, 21 build provenance & attestation, 22 advisories & VEX, 23 coordinated vulnerability disclosure, 24 secure update delivery, 25 support period & end-of-support, 26 root-cause feedback, 27 exceptions & risk acceptance, 28 roles & management commitment, 29 security information for users, 30 notification of exploited vulnerabilities/incidents, 31 AI/ML components, 32 AI-generated code & AI tools, 33 secrets management, 34 SDL metrics & improvement.
- **v0.1.0 items resolved.** IEC 62443-4-1 ids (SR-2, SVV-4, SG-3, DM-5 …) verified against the record (text via ISASecure SDLA-312). ISO/SAE 21434 cells now use the record's RQ/RC ids (work products are attached in the record). BSIMM activity ids are BSIMM16 labels via Table 3/Table 9 lineage. MS SDL uses the current 10-practice web set; the 2021 12-practice numbers cited by SSDF/ETSI are kept only as old-edition evidence.
- **v0.1.0 claims corrected.** "Only SSDF PO.4 names the release gate" is wrong: SDL 5.2 (FSR + RTM sign-off), BSIMM SM2.6, IEC SM-11/SM-12, ISO 21434 RQ-06-34, TR-03185 PROD.PM.A.14 and ENISA RM-7 all do. "Crypto is first-class only in MS SDL + SAFECode": ASVS V11, FDA App. 1.C and ENISA 4.17 also make it first-class; SSDF, ISO 21434 and IEC still do not, and SAMM only through Secret Management (I-SD-B). "Threat modeling in all 7": confirmed, and now 11 of 16 with published evidence (15 non-empty).
- **New sections:** contradictions between published mappings; per-row coverage counts; record-phase cross-check of the phase line.

## How to read the tables

- Ids are the framework's own. Library citations take the form `library:<record>#<id>`: `sp-800-218`, `microsoft-sdl` / `microsoft-sdl-5-2`, `owasp-samm-2`, `bsimm-16`, `iso-sae-21434-2021`, `iec-62443-4-1-2018`, `eu-cra-2024-2847`, `fda-premarket-cybersecurity-guidance`. In the core table CRA ids are shortened (`I.II(1)` = Annex I Part II(1); `II(7)` = Annex II(7); `Art 13(8)` = Art 13(8), first sentence or more), ISO 21434 drops the `RQ-` prefix (`rc` = recommendation), and SDL 5.2 entries are prefixed `5.2:`.
- **†** = placed by our judgement (`ours`); no publisher maps it to the row. Unmarked ids are anchors or source-mapped (publisher in the YAML `per_id`). `+n` = further ids in the YAML. `—` = nothing in the record.
- **Provenance rules.** *anchor*: the row's defining requirement (normally an SSDF task). *direct*: a publisher maps the id to an anchor. *chained*: a publisher maps it to another id of the same row that is itself anchor/direct, exactly one hop (or it is a record-hierarchy child of one; a parent that only contains a mapped child is *ours*). ETSI `SSDIF-X` takes the class of SSDF `X` in the same row. *bridge*: a publisher maps it to a non-column requirement stating the row (BSI TR-03183-1 RH controls, CISA attestation form). *ours*: our judgement, rationale recorded.
- **Editions.** SSDF 1.1 cites BSIMM12, SAMM 1.5, the 2021 MS SDL page and ASVS 4.0.3; SAMM maps to BSIMM14. BSIMM ids are translated only through BSIMM16's own Table 3/Table 9 lineage, ASVS ids only through ASVS 5's published v4.0.3 mapping; SAMM 1.5 and MSSDL-2021 ids stay verbatim with an edition tag (YAML `also`).
- **Core columns.** The eight columns below were chosen for weight in the tmodel context: the hub (SSDF), the origin practice set (MS SDL), the two maturity models (SAMM, BSIMM), the two certifiable process standards (ISO/SAE 21434, IEC 62443-4-1) and the two regulators with binding force (EU CRA, FDA). ETSI TS 104 219 is omitted here because its ids mirror SSDF one-to-one (SSDIF X = SSDF X).

## Core crosswalk (row = requirement; 8 of 16 frameworks)

| Requirement | NIST SSDF 1.1 | MS SDL (+5.2) | SAMM 2.2 | BSIMM16 | ISO/SAE 21434 | IEC 62443-4-1 | EU CRA | FDA 2026 |
|---|---|---|---|---|---|---|---|---|
| **1. Security training & competence** | PO.2.2 | 10†; 5.2: R001†, R002† +2 | G-EG-A, G-EG-1-A, G-EG-2-A | T1.1, T1.7, T2.9 +1 | 05-07† | SM-4 | — | — |
| **2. Define & track security requirements** | PO.1.1, PO.1.2, PW.1.2 | 1.1†, 1.2; 5.2: R005†, R016† +2 | D-SR-A, D-SR-1-A, D-SR-2-A | SR1.1, SR1.3, CP1.1 | 09-05†, 09-09†, 09-10† +3 | SR-3, SR-4, SR-5 | Art 13(3)†, I.I(2)(d), I.I(2)(e) +3 | V.B.1-01†, V.B.1-02†, V.B.1-13† |
| **3. Threat modeling / risk assessment (TARA)** | PW.1.1 | 3†, 3.1, 3.3 +1; 5.2: R030†, R431† +3 | D-TA-B, D-TA-1-B, D-TA-2-B +2 | AM1.3, AM2.1, AA2.1 +1 | 15-01†, 15-02†, 15-03† +4 | SR-2, SR-2.review, SR-2.periodic +1 | Art 13(2)†, Art 13(3)†, I.I(1) | V.A.1-02†, V.A.1-03†, V.A.1-07† +1 |
| **4. Secure design principles & standard security features** | PW.1.3 | 2†, 2.1; 5.2: R026†, R027† +1 | D-SA-A, D-SA-1-A, D-SA-2-A | SFD1.1, SFD2.1, SFD3.2 | rc10-06† | SD-2, SD-4, SD-4.2 | I.I(2)(d), I.I(2)(e), I.I(2)(f) +2 | V.B-09†, V.B.1-03†, App1.B-05† |
| **5. Security design / architecture review** | PW.2.1 | 3†, 3.2; 5.2: R023†, R192† +1 | V-AA-A, V-AA-2-A, V-AA-B | AA1.1, AA1.2, AA2.1 +1 | 10-07† | SD-3 | — | — |
| **6. Cryptographic standards & key management** | — | 4, 4.1, 4.2 +2; 5.2: R099†, R491† +2 | I-SD-B | SFD1.1†, SR3.3† | — | — | I.I(2)(e)† | App1.C-01†, App1.C-02†, App1.C-03† +2 |
| **7. Third-party component risk management** | PO.1.3, PW.4.1, PW.4.4 | 5†, 5.1, 5.2; 5.2: R145†, R146† +1 | I-SB-B, I-SB-2-B, I-SB-3-B +3 | SR1.5, SR2.7, SM3.5† +2 | 06-21†, 06-22†, 07-01† +1 | SM-9, SM-10 | Art 13(5)†, Art 13(6)†, I.II(1) | V.A.4-01†, V.A.4-03†, V.A.4.b-08† +1 |
| **8. Approved, securely configured toolchain** | PO.3.1, PO.3.2, PW.6.1 +1 | 2.5; 5.2: R048†, R050† +2 | D-SA-B, D-SA-2-B, I-SB-A +2 | SE3.9, SR3.4, SE2.4 | 05-14† | SI-2, SM-7 | — | — |
| **9. Secure coding standards** | PW.5.1 | STAGE-code†; 5.2: R051†, R059† +3 | D-SA-1-A | SR3.3, CR3.5 | 10-04†, 10-05† | SI-2 | — | App1.D-14† |
| **10. Code review & static analysis** | PW.7.1, PW.7.2 | 7.1; 5.2: R050†, R056† +3 | V-ST-A, V-ST-1-A, V-ST-3-A | CR1.4, CR1.5, CR2.6 | 10-09†, 10-10† | SI-1, SI-1.sca-tool, SI-1.sca-changes | I.II(3)† | V.C-23†, App1.D-17† |
| **11. Security testing of executable code (dynamic, functional, fuzz)** | PW.8.1, PW.8.2 | 7†, 7.2, 7.5 +1; 5.2: R100†, R119† +2 | V-RT-A, V-RT-B, V-RT-2-A +2 | ST1.1, ST1.3, ST1.4 +2 | rc10-12†, 10-11†, 11-02† | SVV-1, SVV-2, SVV-3 +1 | I.II(3) | V.C-05†, V.C-07†, V.C-12† +4 |
| **12. Penetration testing** | PW.8.2 | 7.3, 7.4, 8.7; 5.2: R225† | V-ST-B, V-ST-2-B | PT1.1, PT1.3, PT2.3 +1 | 11-01† | SVV-4 | — | V.C-24†, V.C-25†, V.C-26† +1 |
| **13. Release integrity: signing, integrity data & archiving** | PS.2.1, PS.3.1 | 5.4; 5.2: R168† | I-SD-A, I-SD-3-A, I-SB-1-A | SE2.4 | 05-12†, rc05-15† | SM-6, SM-8, SUM-4 | — | App1.D-02†, App1.D-03†, VI.A-17† |
| **14. Secure-by-default configuration & hardening guidance** | PW.9.1, PW.9.2 | 8.3, 8.6; 5.2: R413†, R432† +1 | O-EM-A, O-EM-2-A | SE1.4 | — | SG-3, SG-1, SD-4.e | I.I(2)(b), I.I(2)(j) | VI.A-23†, App1.B-06†, App1.F-09† |
| **15. Release security gate / sign-off** | PO.4.1, PO.4.2 | 1.3; 5.2: R106†, R154† +5 | G-SM-2-B, G-PC-1-A, I-SD-2-A† | SM1.4, SM1.7, SM2.6 +1 | 06-31†, 06-33†, 06-34† | SM-11†, SM-12, SVV-3 | I.I(2)(a), Art 13(12)† | V.C-34† |
| **16. Protect development environments & source code** | PO.5.1, PO.5.2, PS.1.1 | 6†, 6.1†, 6.2 +1 | I-SB-A, I-SD-B | SE3.10, SE2.4 | rc05-16† | SM-7, SM-8 | — | V.A.4-06† |
| **17. Vulnerability / defect management (triage & remediation)** | RV.2.1, RV.2.2 | 5.2: R036†, R106† +2 | I-DM-A, I-DM-1-A, I-DM-2-A | CMVM1.3, PT1.2, CR2.8 | 08-05†, 08-07† | DM-2, DM-3, DM-4 | I.II(2) | V.A.2-05†, V.A.4.b-11†, V.C-35† +1 |
| **18. Vulnerability monitoring & investigation (released software)** | RV.1.1, RV.1.2 | 9†; 5.2: R171†, R443† | V-ST-B, O-EM-3-B, V-ST-2-A | CMVM1.2, CMVM1.4, AM1.5 +1 | 08-01†, 08-02†, 08-03† +1 | DM-1, DM-2 | Art 13(8)†, I.II(6) | VI.B-03†, VI.B-06†, VI.B-07† |
| **19. Security monitoring & incident response (operations)** | — | 9†, 9.1†, 9.2; 5.2: R142†, R443† +1 | O-IM-A†, O-IM-B, O-IM-1-B +1 | CMVM1.1, CMVM3.3, SE3.3† | 13-01†, 13-02†, 08-08† | — | I.I(2)(l)† | App1.F-04†, App1.F-06†, VI.A-24† |
| **20. SBOM / component inventory** | PS.3.2 | 5.3 | I-SB-B, I-SB-1-B, I-SB-2-B | SE3.6, SR1.5 | — | SM-9 | I.II(1), II(9)†, VII(8)† | V.A.4.a-01†, V.A.4.a-03†, V.A.4.b-01† +5 |
| **21. Build provenance & attestation** | PS.3.2† | 5.4† | — | — | — | — | — | — |
| **22. Security advisories & VEX (vulnerability-status communication)** | RV.2.2 | — | — | — | — | DM-5†, SUM-2†, SUM-3† | I.II(4), I.II(4)-delay† | VI.B-13†, VII.C.1-06† |
| **23. Coordinated vulnerability disclosure (policy & reporting channel)** | RV.1.3 | — | O-IM-B, O-IM-3-B | CMVM2.4, CMVM3.4† | — | DM-1 | I.II(5), I.II(6), Art 13(8)† +2 | VI.B-12†, VII.C.1-04†, VII.C.1-05† |
| **24. Secure update delivery** | RV.2.2 | 8.9†; 5.2: R147†, R418† | O-EM-B† | — | 13-03† | SUM-1†, SUM-4†, SUM-5† | I.I(2)(c), I.II(7), I.II(8) +1 | App1.H-01†, App1.H-03†, App1.H-06† +2 |
| **25. Defined support period & end-of-support notice** | — | — | O-OM-B, O-OM-1-B, O-OM-2-B | — | 14-01† | — | Art 13(8), Art 13(19), II(7) | VI.A-26†, VI.A-27† |
| **26. Root-cause analysis fed back into the SDL** | RV.3.1, RV.3.2, RV.3.3 +1 | 5.2: R011†, R013† | I-DM-B, I-DM-3-B, I-DM-2-A +1 | CMVM3.2, CMVM3.1, CR3.3 +1 | — | DM-3, DM-4, DM-6 +3 | — | App1.F-16†, VII.C.1-13† |
| **27. Security exceptions & risk acceptance** | PO.4.1, RV.2.2† | 1.4, 1-X1†, 1-X2† +1; 5.2: R160†, R177† +3 | G-SM-A, G-SM-1-A | SM1.7, CP2.2 | 09-06†, 15-17†, 06-14† | DM-4.residual† | I.I(1) | V.A-09†, V.A.2-01†, V.A.2-03† +1 |
| **28. Security roles, responsibilities & management commitment** | PO.2.1, PO.2.3 | 1†; 5.2: R127†, R144† | G-EG-B, G-EG-2-B, G-SM-2-A | SM1.1, SM2.3, SM1.3 +1 | 05-01†, 05-03†, 05-04† +1 | SM-2 | — | V.A.6-01†, VI.B-05† |
| **29. Security information & instructions for users** | PW.9.1, PW.9.2 | 5.2: R039†, R041† +1 | O-EM-A, O-OM-B† | — | 14-02† | SG-1, SG-2, SG-4† +3 | Art 13(18), II(4)†, II(5)† +2 | VI.A-04†, VI.A-07†, VI.A-09† +2 |
| **30. Notification of exploited vulnerabilities & severe incidents** | — | — | — | — | — | — | Art 14(1), Art 14(2)(a)†, Art 14(2)(b)† +3 | — |
| **31. AI/ML components: inventory, provenance & AI-specific threats** | — | 2.2, 3.1† | — | AM3.4† | — | — | — | — |
| **32. AI-generated code & AI dev tools** | — | — | — | SR3.5† | — | — | — | — |
| **33. Secrets & credential management (no hard-coded secrets)** | PW.5.1, PO.5.2 | 4.4; 5.2: R219†, R488† | I-SD-B, I-SD-1-B, I-SD-3-B | SE3.9† | — | SM-8† | — | App1.A-13†, App2.B-24† |
| **34. SDL programme metrics & continuous improvement** | — | 1.3; 5.2: R422† | G-SM-B, G-SM-1-B, G-SM-2-B +2 | SM2.1, SM3.3, SM1.1† | 05-08†, 05-17† | SM-13, DM-6 | — | V.A.6-05†, V.A.6-06† |

## Coverage per requirement (all 16 frameworks)

"Sourced" = the framework's cell holds at least one anchor/direct/chained/bridge id. "Judgement only" = the cell is filled but only by `ours`. "Absent" = nothing found in the record.

| # | Requirement (definition in YAML) | Phase | Sourced (of 16) | Judgement only | Absent |
|---|---|---|---|---|---|
| 1 | Security training & competence | spanning | **8** | MS SDL, 21434 | CRA, OSPS, SLSA, ASVS, FDA, ENISA |
| 2 | Define & track security requirements | requirements | **9** | 21434, SAFECode, ASVS, FDA, ENISA | OSPS, SLSA |
| 3 | Threat modeling / risk assessment (TARA) | design | **11** | 21434, ASVS, FDA, ENISA | SLSA |
| 4 | Secure design principles & standard security features | design | **11** | 21434, ASVS, FDA | OSPS, SLSA |
| 5 | Security design / architecture review | design | **8** | 21434, SAFECode, ENISA | CRA, UK CoP, OSPS, SLSA, FDA |
| 6 | Cryptographic standards & key management | design | **2** | BSIMM, SAFECode, CRA, ASVS, FDA, ENISA | SSDF, 21434, 62443-4-1, ETSI, TR-03185, UK CoP, OSPS, SLSA |
| 7 | Third-party component risk management | implementation | **13** | 21434, FDA | SLSA |
| 8 | Approved, securely configured toolchain | implementation | **10** | 21434, SLSA | CRA, ASVS, FDA, ENISA |
| 9 | Secure coding standards | implementation | **9** | MS SDL, 21434, FDA, ENISA | CRA, OSPS, SLSA |
| 10 | Code review & static analysis | implementation | **9** | 21434, CRA, SLSA, FDA, ENISA | UK CoP, ASVS |
| 11 | Security testing of executable code (dynamic, functional, fuzz) | verification | **12** | 21434, ASVS, FDA | SLSA |
| 12 | Penetration testing | verification | **8** | 21434, ASVS, FDA | CRA, UK CoP, OSPS, SLSA, ENISA |
| 13 | Release integrity: signing, integrity data & archiving | release | **9** | 21434, FDA, ENISA | SAFECode, CRA, SLSA, ASVS |
| 14 | Secure-by-default configuration & hardening guidance | release | **11** | ASVS, FDA | 21434, OSPS, SLSA |
| 15 | Release security gate / sign-off | release | **8** | 21434, TR-03185, FDA, ENISA | SAFECode, UK CoP, SLSA, ASVS |
| 16 | Protect development environments & source code | implementation | **9** | 21434, SLSA, FDA, ENISA | SAFECode, CRA, ASVS |
| 17 | Vulnerability / defect management (triage & remediation) | response | **11** | MS SDL, 21434, FDA | SLSA, ASVS |
| 18 | Vulnerability monitoring & investigation (released software) | response | **11** | MS SDL, 21434, FDA | SLSA, ASVS |
| 19 | Security monitoring & incident response (operations) | response | **3** | 21434, CRA, UK CoP, ASVS, FDA, ENISA | SSDF, 62443-4-1, SAFECode, ETSI, TR-03185, OSPS, SLSA |
| 20 | SBOM / component inventory | release | **10** | ASVS, FDA, ENISA | 21434, SAFECode, SLSA |
| 21 | Build provenance & attestation | release | **3** | SSDF, MS SDL, ETSI, ENISA | SAMM, BSIMM, 21434, 62443-4-1, SAFECode, CRA, UK CoP, ASVS, FDA |
| 22 | Security advisories & VEX (vulnerability-status communication) | response | **7** | 62443-4-1, SAFECode, FDA | MS SDL, SAMM, BSIMM, 21434, SLSA, ASVS |
| 23 | Coordinated vulnerability disclosure (policy & reporting channel) | response | **10** | FDA, ENISA | MS SDL, 21434, SLSA, ASVS |
| 24 | Secure update delivery | response | **6** | MS SDL, SAMM, 21434, 62443-4-1, TR-03185, FDA | BSIMM, SAFECode, SLSA, ASVS |
| 25 | Defined support period & end-of-support notice | release | **5** | 21434, FDA, ENISA | SSDF, MS SDL, BSIMM, 62443-4-1, SAFECode, ETSI, SLSA, ASVS |
| 26 | Root-cause analysis fed back into the SDL | response | **7** | MS SDL, FDA, ENISA | 21434, CRA, UK CoP, OSPS, SLSA, ASVS |
| 27 | Security exceptions & risk acceptance | spanning | **7** | 21434, 62443-4-1, TR-03185, FDA, ENISA | UK CoP, OSPS, SLSA, ASVS |
| 28 | Security roles, responsibilities & management commitment | spanning | **6** | MS SDL, 21434, SAFECode, UK CoP, OSPS, FDA | CRA, SLSA, ASVS, ENISA |
| 29 | Security information & instructions for users | release | **7** | MS SDL, 21434, OSPS, FDA, ENISA | BSIMM, SAFECode, SLSA, ASVS |
| 30 | Notification of exploited vulnerabilities & severe incidents | response | **1** | TR-03185, UK CoP | SSDF, MS SDL, SAMM, BSIMM, 21434, 62443-4-1, SAFECode, ETSI, OSPS, SLSA, ASVS, FDA, ENISA |
| 31 | AI/ML components: inventory, provenance & AI-specific threats | design | **2** | BSIMM, ETSI | SSDF, SAMM, 21434, 62443-4-1, SAFECode, CRA, TR-03185, UK CoP, OSPS, SLSA, ASVS, FDA |
| 32 | AI-generated code & AI dev tools | implementation | **1** | BSIMM, TR-03185 | SSDF, MS SDL, SAMM, 21434, 62443-4-1, SAFECode, CRA, ETSI, UK CoP, OSPS, SLSA, ASVS, FDA |
| 33 | Secrets & credential management (no hard-coded secrets) | implementation | **7** | BSIMM, 62443-4-1, SAFECode, TR-03185, SLSA, FDA, ENISA | 21434, CRA |
| 34 | SDL programme metrics & continuous improvement | spanning | **5** | 21434, SAFECode, FDA | SSDF, CRA, ETSI, UK CoP, OSPS, SLSA, ASVS, ENISA |

## Biggest overlaps

Ranked by the number of frameworks with a source-backed cell (non-empty cells including judgement in brackets).

1. **Third-party component risk management (row 7)** — 13 sourced (15 non-empty). Absent in: SLSA.
2. **Security testing of executable code (dynamic, functional, fuzz) (row 11)** — 12 sourced (15 non-empty). Absent in: SLSA.
3. **Threat modeling / risk assessment (TARA) (row 3)** — 11 sourced (15 non-empty). Absent in: SLSA.
4. **Secure design principles & standard security features (row 4)** — 11 sourced (14 non-empty). Absent in: OSPS, SLSA.
5. **Vulnerability / defect management (triage & remediation) (row 17)** — 11 sourced (14 non-empty). Absent in: SLSA, ASVS.
6. **Vulnerability monitoring & investigation (released software) (row 18)** — 11 sourced (14 non-empty). Absent in: SLSA, ASVS.
7. **Secure-by-default configuration & hardening guidance (row 14)** — 11 sourced (13 non-empty). Absent in: 21434, OSPS, SLSA.
8. **SBOM / component inventory (row 20)** — 10 sourced (13 non-empty). Absent in: 21434, SAFECode, SLSA.
9. **Approved, securely configured toolchain (row 8)** — 10 sourced (12 non-empty). Absent in: CRA, ASVS, FDA, ENISA.
10. **Coordinated vulnerability disclosure (policy & reporting channel) (row 23)** — 10 sourced (12 non-empty). Absent in: MS SDL, 21434, SLSA, ASVS.

Read with two caveats. (1) "Sourced" depends on publishers: no publisher maps anything to ISO/SAE 21434, FDA or SDL 5.2, so those columns can only ever add judgement cells. (2) ETSI TS 104 219's cell is the SSDF cell by construction (clause 5.0.1: SSDIF X = SSDF X), so every row with a sourced SSDF task also gets a sourced ETSI cell; subtract one for a count of independent publishers. Counting non-empty cells instead, no row is present in all 16 frameworks; Threat modeling / risk assessment (TARA) (row 3), Third-party component risk management (row 7), Security testing of executable code (dynamic, functional, fuzz) (row 11) in 15.

**Threat modeling (row 3) remains the anchor for tmodel:** 11 frameworks with published evidence, 15 non-empty — only SLSA has no producer threat-modelling duty; 21434, ASVS, FDA, ENISA are judgement-only.

## Real divergences

- **Process standards vs regulators.** The CRA, FDA and UK CoP are strongest where products meet users — vulnerability handling, CVD, updates, support periods, user documentation, incident notification (rows 17–18, 22–25, 29–30). The CRA and FDA are silent on training and toolchains (rows 1, 8) and nearly so on coding standards and code review (rows 9–10), which SSDF, SAMM, BSIMM, IEC and TR-03185 cover densely; the UK CoP touches them only through APC claims 1.1.2, 1.1.3 and 1.4.4.
- **Support period & end-of-support (row 25)** is a regulatory invention: CRA Art 13(8)/(19), UK 4.1/4.2, OSPS DO-04/DO-05, TR-03185 PROD.DECOM.2, ISO 21434 Cl. 14, FDA labeling. SSDF, ETSI, the current MS SDL set, BSIMM, IEC and SAFECode have no support-period concept (OSPS's links to PO.4.2/PS.3.1/RV.1.3 are not adopted); SAMM enters only through O-OM-B decommissioning/legacy management, which OSPS links to its support-statement controls.
- **Notification of exploited vulnerabilities/severe incidents (row 30)** exists with deadlines only in the CRA (Art 14: 24 h / 72 h / 14 days); the UK CoP (3.4, 4.3) and BSI TR-03185 (FIX.A.9) only require informing users or relevant parties, without deadlines or authority reporting; IEC DM-5 is user disclosure (row 22), not notification; no SDL or maturity model covers it.
- **Build provenance (row 21)** is SLSA's home ground, with published links only from OSPS and BSI TR-03185 (BR.01/BR.06 "induced by SLSA 1.1 Build L1"); MS SDL 5.4 and ENISA 4.14 add it by our judgement. SAMM, BSIMM, ISO 21434, IEC, SAFECode, the CRA and FDA require none. SSDF 1.1 has no build-provenance task: PS.3.2 is provenance data of the release's components (the SBOM anchor of row 20), kept in row 21 as judgement only, and ETSI follows SSDF.
- **Cryptography (row 6)** is first-class in MS SDL (4.1–4.4), SAFECode, ASVS V11, FDA App. 1.C and ENISA 4.17, but no publisher maps them to each other or to an SSDF task: the only source-backed cells are MS SDL (the row anchor) and SAMM I-SD-B Secret Management (via the SAMM sheet's link to MS SDL 4.4). SSDF 1.1, ISO 21434, IEC 62443-4-1 (its SM-8 protects code-signing keys only, rows 13/16/33), OSPS and TR-03185 have no cryptography-standard requirement; BSIMM touches it only inside SFD1.1/SR3.3.
- **Operational incident response (row 19)** stays split: MS SDL 9, SAMM O-IM, BSIMM CMVM, ISO 21434 Cl. 13 and UK 4.3 own it; SSDF and IEC 62443-4-1 scope it out (IEC defers to 62443-2-1/3-3).
- **Release gate (row 15)** is now near-universal (8 sourced, 12 non-empty) but realised differently: criteria-based (SSDF PO.4, OSPS QA-03), a named review + sign-off (SDL 5.2 FSR/RTM, BSIMM SM2.6, ISO 21434 RQ-06-34, IEC SM-11/SM-12, ENISA RM-7), or a legal precondition (CRA Annex I Part I(2)(a) "no known exploitable vulnerabilities" + conformity assessment). The tmodel `Gate` exit criteria should model all three.
- **Security exceptions (row 27)** are explicit and time-bound only in MS SDL (1.4, 1-X1..X3), SDL 5.2 (FSR exceptions), SAFECode, BSIMM SM1.7 and ENISA (exception log with owner and expiry); ISO 21434 handles it as risk retention with cybersecurity claims; the CRA leaves no room for accepting non-conformity with Annex I.
- **AI (rows 31–32)** is almost absent: ENISA (AI/ML models in inventory and threat identification; AI-generated code under the same checks), MS SDL 2.2, BSIMM SR3.5/AM3.4, ETSI R-0002 and TR-03185 R-0002. SSDF 1.1 is silent (the SP 800-218A profile covers it but is not a column).
- **SBOM vs third-party management (rows 7 vs 20)** split along publishers (see contradiction C-01).

## Contradictions between published mappings

15 curated findings (full text, evidence ids and resolution in the YAML; 104 automated row-level checks listed there too). The ones that change a cell:

- **C-01 SBOM: where CRA Annex I Part II(1) belongs.** ETSI TS 104 219 Annex A maps CRA Annex I Part II(1) (identify components, draw up an SBOM) only to SSDIF PW.4.1/PW.4.4 (third-party components) and maps no CRA provision to PS.3.2. SSDF 1.1 itself files the NTIA SBOM reference under PS.3.2, OSPS maps its SBOM requirement (OSPS-QA-02.02) to PS.3.2 and to CRA 2.1 (= Part II(1)), and ENISA Annex C maps playbook 4.14 (inventory + SBOM) to Part II(1). The same split recurs for UK APC claim 1.2.1: ETSI B.1 -> PW.4.1, OSPS -> PS.3.2 (via OSPS-QA-02.0x). *Resolution:* SBOM is its own row (20) anchored on PS.3.2; Part II(1) is kept in row 7 (ETSI, direct) and row 20 (OSPS chain) with this note.
- **C-02 OWASP SAMM contradicts itself: stream sheet vs OLIR workbook.** The two SAMM-published SSDF mappings disagree on 15 SSDF tasks. Disjoint on 5: PO.1.1 (stream sheet G-SM-A/B; OLIR G-PC-1-A, G-PC-2-B), PO.2.3 (G-PC-A vs G-SM-2-A), PO.4.2 (G-PC-B vs G-SM-3-B, V-ST-1-A), PW.7.1 and PW.8.1 (G-SM-A vs G-PC-1-A). The architecture-assessment streams are swapped: the stream sheet puts V-AA-A at PW.1.1 and V-AA-B at PW.2.1/PW.9.1, OLIR puts V-AA-1-B at PW.1.1 and V-AA-2-A at PW.2.1, V-AA-1-A at PW.9.1. RV.1.1: V-ST-B vs V-ST-2-A. *Resolution:* Both mappings are carried; per_id names which one sourced each SAMM id. Row 5 keeps V-AA-A (OLIR) and V-AA-B (stream sheet).
- **C-07 ETSI Annex B.2 vs its upstream (SSDF References).** Ten B.2 rows printed as a second "PW.1.1" are SSDF PS.3.2 rows (BSAFSS SM.2, BSIMM SE3.6, CNCF, EO 4e(vi)/(vii)/(ix)/(x), NTIA SBOM "All", SCVS, SAFECode SCSIC/SCTPC, SP 800-53/-161 SA-8, SR-3, SR-4): read literally, SBOM evidence lands on threat modelling. B.2 also omits SSDF's BSIMM references for PO.1.1-PO.1.3 (27 ids) and prints MASVS "1.1" for "1.10". For the column frameworks (IEC, SAMM 1.5, MSSDL, SCFPSSD, ASVS 4.0.3) B.2 otherwise replicates the SSDF References exactly, so it is not independent evidence. *Resolution:* B.2 rows keyed to PS.3.2 (ssdf_1_1_task flag); B.2 not counted as a separate publisher.

Minor/info: C-03 SSDF References vs SAMM map on IEC 62443-4-1 ids (10 ids); C-04 SSDF References (BSIMM12->16) vs SAMM map (BSIMM14->16) on 40 BSIMM activities; C-05 CISA attestation form vs SP 800-218 Appendix A (EO 14028 4e -> SSDF); C-06 SSDF internal: RV.2.2 EO 14028 mapping; C-08 BSI TR-03185 Part 2: code peer review "induced by" design review; C-09 OSPS vs ETSI B.1 on UK APC claims (16 row-disjoint pairs); C-10 OSPS internal: CVD-policy control mapped away from the UK CVD principle; C-11 SSDF References: PW.4.1 -> MSSDL #6 (cryptography); C-12 SAMM mapping cites non-existent target ids; C-13 FDA cites 62443-4-1 without clauses; C-14 OSPS vs ETSI Annex A on CRA placement (21 row-disjoint co-mappings); C-15 CRA product properties treated as design inputs by ETSI only.

## Canonical phase line (re-derived)

`concept → requirements → design → implementation → verification → release → response` (+ *spanning*). Each row was placed by its definition and cross-checked against the `phase` the source records assign to the row's ids (YAML `record_phase_check`).

| Phase | Rows | SSDF | MS SDL | SAMM | BSIMM | ISO 21434 | IEC 62443-4-1 | EU CRA |
|---|---|---|---|---|---|---|---|---|
| Concept | — (folded into Requirements/Design: ISO 21434 Cl. 9 concept, IEC SR-1) | | | | | | | |
| **Requirements** | 2 | PO.1.1, PO.1.2, PW.1.2 | 1.1, 1.2 | D-SR | SR, CP | Cl.9, Cl.10 | SR-3, SR-4, SR-5 | Art 13(3), I.I(2) |
| **Design** | 3, 4, 5, 6, 31 | PW.1.1, PW.1.3, PW.2.1 | 3, 3.1, 3.3, 3.4, 2, 2.1 … | D-TA, D-SA, V-AA, I-SD | AM, AA, SFD, SR | Cl.15, Cl.9, Cl.10 | SR-2, SD-2, SD-4, SD-3 | Art 13(2), Art 13(3), I.I(1), I.I(2) |
| **Implementation** | 7, 8, 9, 10, 16, 32, 33 | PO.1.3, PW.4.1, PW.4.4, PO.3.1, PO.3.2, PW.6.1 … | 5, 5.1, 5.2, 2.5, STAGE-code, 7.1 … | I-SB, D-SR, D-SA, V-ST, I-SD | SR, SM, CP, SE, CR | Cl.6, Cl.7, Cl.5, Cl.10 | SM-9, SM-10, SI-2, SM-7, SI-1, SM-8 | Art 13(5), Art 13(6), I.II(1), I.II(3) |
| **Verification** | 11, 12 | PW.8.1, PW.8.2 | 7, 7.2, 7.5, 7.6, 7.3, 7.4 … | V-RT, V-ST | ST, PT | Cl.10, Cl.11 | SVV-1, SVV-2, SVV-3, SVV-5, SVV-4 | I.II(3) |
| **Release** | 13, 14, 15, 20, 21, 25, 29 | PS.2.1, PS.3.1, PW.9.1, PW.9.2, PO.4.1, PO.4.2 … | 5.4, 8.3, 8.6, 1.3, 5.3 | I-SD, I-SB, O-EM, G-SM, G-PC, O-OM | SE, SM, CP, SR | Cl.5, Cl.6, Cl.14 | SM-6, SM-8, SUM-4, SG-3, SG-1, SD-4 … | I.I(2), Art 13(12), I.II(1), II(9), VII(8), Art 13(8) … |
| **Response** | 17, 18, 19, 22, 23, 24, 26, 30 | RV.2.1, RV.2.2, RV.1.1, RV.1.2, RV.1.3, RV.3.1 … | 9, 9.1, 9.2, 8.9 | I-DM, V-ST, O-EM, O-IM, G-SM | CMVM, PT, CR, AM, SE, CP | Cl.8, Cl.13 | DM-2, DM-3, DM-4, DM-1, DM-5, SUM-2 … | I.II(2), Art 13(8), I.II(6), I.I(2), I.II(4), I.II(4)-delay … |
| **Spanning** | 1, 27, 28, 34 | PO.2.2, PO.4.1, RV.2.2, PO.2.1, PO.2.3 | 10, 1.4, 1-X1, 1-X2, 1-X3, 1 … | G-EG, G-SM, I-DM | T, SM, CP | Cl.5, Cl.9, Cl.15, Cl.6 | SM-4, DM-4, SM-2, SM-13, DM-6 | I.I(1) |

**Record cross-check.** Placements agree with the records' own phase majority except: row 7 placed *implementation*, records lean *supply-chain* (51 vs 0 ids); row 10 placed *implementation*, records lean *verification* (17 vs 16 ids); row 20 placed *release*, records lean *supply-chain* (22 vs 5 ids); row 25 placed *release*, records lean *response* (15 vs 7 ids); row 33 placed *implementation*, records lean *release* (10 vs 7 ids). "supply-chain" is not on the canonical line; component management goes to *implementation*, SBOM and provenance to *release* (produced per release). Support period is placed at *release* because the CRA fixes it at placing on market, although most ids describe its in-life consequences. Code review stays in *implementation* (v0.1.0 placement), the records split almost evenly with *verification*.

**Note:** SSDF, BSIMM, SAMM and SAFECode are not phase-ordered; their placement is via the rows. ISO 21434 Clause 9 (concept) has no separate row: its cells sit in rows 2–3.

## Verify before acceptance

- ISO/SAE 21434: no published mapping to any other framework exists in the library; all 23 non-empty cells are ours. The record has no verification.md, and RQ-09-03, RQ-11-01 (and RQ-07-04, RQ-10-08) carry garbled text from table/annex spill - the ids are used but the record needs repair before acceptance.
- FDA 2026: publishes no crosswalk (only 62443-4-1 and NTIA citations without clauses); all 27 non-empty cells are ours.
- MS SDL: the current web set has no published mapping except via the SAMM sheet; SDL 5.2 publishes none. SSDF/ETSI cite the 2021 12-practice page whose numbers do not resolve against either record.
- SLSA 1.2: only OSPS (SLSA 1.0 names) and BSI TR-03185 Part 2 ("SLSA 1.1 Build L1") point at it; SLSA itself publishes no crosswalk.
- ETSI B.1 cites CRT APC v1.0 claims 5.1.1-5.4.5 (product principle 5) that are not in the uk-software-security-code-of-practice record (it holds APC principles 1-4).
- IEC 62443-4-1 text in the record comes from ISASecure SDLA-312 (public), not the paywalled IEC body; sub-ids (SR-2.review, DM-4.residual, ...) are the record's own splits.
- BSI TR-03185 Pruefspezifikation mapping was written against German Part 1 v1.0; id alignment with EN v1.1.1 rests on unchanged ids (not re-verified cell by cell). OSPS maps to TR-03185-2 v1.1.0 ids, now merged into v1.1.1.
- SAMM 1.5 (cited by SSDF) has no published translation to SAMM 2.2 stream ids; kept verbatim with edition tag.
- ASVS 4.0.3 chapter-level SSDF references (e.g. PW.1.1 -> chapters 2-13) translate into hundreds of ASVS 5 rows; only requirement-level translations were adopted.
- AI rows (31, 32) rest almost entirely on ENISA and MS SDL text; SSDF coverage exists only in the SP 800-218A community profile (not a column).
- Ours-only cells (judgement, not source-backed): 123 of 544 cells; listed in the YAML `unresolved.ours_only_cells`. They need a reviewer who reads both records.
- Human review (pass 4) of every library record used here is outstanding (`reviewed_by` empty).

## Use in the model (iteration 8)

Each row becomes a `Requirement` with cross-spec `maps_to` edges (R-044) that carry the YAML provenance (`src`, `edition`, anchor/direct/chained/bridge/ours) so conformance can weigh published vs judged equivalence. A `Gate`'s exit criteria reference the rows due by its phase (row 15 gives the three gate styles); conformance (R-042) checks a product's threat model and mitigations against the applicable rows, with row 3 as the anchor. The contradiction list shows where a single published crosswalk cannot be trusted alone (SAMM's two sheets, ETSI Annex A vs OSPS on SBOM).

## Adversarial review (2026-10-03)

An independent reviewer, not the builder, checked v0.2.0 on 2026-10-03. Every finding below was fixed in the build inputs (`rows.py` review block, `build.py`, `emit*.py`, `contra_curated.py`), and the three outputs were regenerated. All counts, tables and prose above are post-review. The build is now deterministic: it gives byte-identical output for four `PYTHONHASHSEED` values. **Net effect:** ids 1,062 → 1,030. Provenance went from anchor 86 / direct 398 / chained 115 / bridge 3 / ours 460 to 90 / 391 / 87 / 4 / 458. Ours-only cells went from 128 → 123.

### Method

- **Source claims (check 1).** All 516 source-claimed ids (direct/chained/bridge) were checked, not a sample. They cover every column that has one: ISO/SAE 21434 and FDA have none. A separate parser re-read the publishers' raw records: SSDF `crosswalk.yaml` (with my own BSIMM Table 9 lineage), ETSI `crosswalk.yaml` (Annex A, B.1), the SAMM `pairs` and OLIR sheets, BSIMM16 `maps_to`, OSPS `maps_to`, the BSI TR-03185 Prüfspezifikation and Induced-by data, TR-03183-1 and ENISA Annex C. The parser does not reuse `edges.py`. Results:
  - 447 claims matched automatically.
  - 69 were flagged. 51 of these were correct on a hand check: SAFECode section-title matches, practice-level OSPS/BSI entries such as "PS.1", "PO.4" and "PW.9", OSPS→SAMM 2.0 stream names and SLSA 1.0 names, TR-03185 Induced-by CRA ranges, and SAMM stream-level edges.
  - The other 18 were labelling defects: 7 multi-hop chains, 6 ETSI mirror labels and 5 SAMM anchor activities.
  - Enforcing the one-hop rule then surfaced the rest of P1/P2 below.
  - 24 more claims were spot-checked by hand against the raw entries. All 1,030 ids and all refs resolve in their target `requirements.yaml`.
- **Judgement cells (check 2).** I read all 460 `ours` ids against the row definition, not just a sample of 60. That includes all 59 ISO/SAE 21434 ids, all 93 FDA ids and all 87 SDL 5.2 ids.

### Defects by category

| Category | Defects | What was wrong | Fix |
|---|---|---|---|
| Provenance | 37 ids | **P1 (13 ids): two-hop chains labelled *chained*.** The build ran a second pass that chained through chained ids and through bridge ids, against the stated one-hop rule. Examples: ENISA PB-4.1 (via bridge CRA I(1)), CRA II(3) in row 10, TR-03185 DEV.D.3 / PM.A.14 / DOC.B.5 / DOC.B.6, ENISA PB-4.14 / PB-4.13-CL-01 / PB-4.9-CL-18, UK APC-3.2-01/02 / APC-3.3-02, SAMM O-IM-A. Rows 3, 10, 15 and 20 each lost one sourced framework. **P2 (12 ids):** a parent principle or practice inherited a child's mapping and was labelled *chained*: MS SDL 2/3/5/6/7, UK 1.2/1.3/1.4/2.1/2.2. In row 19 a parent and a sibling of anchor 9.2 were labelled *anchor*. **P3 (3 ids):** every `SSDIF-X` was labelled *direct* whatever the provenance of SSDF X (rows 21, 29, 33). **P4 (2 ids):** row 21's SSDF/ETSI "sourcing" rested on PS.3.2 (see R1); a latent practice-level OSPS "PS.3" edge would have re-chained it. **P5 (7 ids):** activities of an anchor SAMM stream were understated as *chained* or *direct*. | One-hop rule enforced: chains run only from anchor/direct ids and never through bridge ids. A child inherits from its parent, but a parent that only contains a mapped child is *ours* with an automatic rationale. `SSDIF-X` mirrors the class of SSDF X. A practice-level edge cannot single out one task for a chain. SAMM activities of an anchor stream are *anchor*. No claimed edge was missing from the publisher's record. |
| Judgement placements | 39 of 460 ids (34 removed, 5 moved) | Removed as indefensible: SLSA R-0150/R-0151 (passing functional tests) in security testing; IEC DM-5 and DM-4 e) as exploited-vulnerability *notification* (row 30); OSPS BR-03 (TLS on project channels), IEC SM-8 and TR PM.A.13 as *cryptography standards*; SLSA R-0117 (a *perpetual* robot exception) and ASVS F-20 (a report listing exceptions) as time-bound risk acceptance; UK principle 1.4 (secure by design) in threat modelling; ASVS P-38 (anomaly limits); FDA V.B-10 (system context) as design review; IEC SM-1, OSPS GV-01.01 and SDL 5.2 R-0006/R-0007 (privacy advisors) as security roles; SDL 5.2 R-0143 and TR REL.2 / OSPS BR-02.01 (version identifiers) as support period / release integrity. Removed as double placements across overlapping rows: ISO RQ-05-08 (26 and 34), RQ-14-02 and RQ-05-12 (25), FDA V.A.4.b-11 (7 and 17), V.A.4.b-03/04 (20 and 25), V.A.2-03 (15 and 27), MS SDL 9.1 and SDL 5.2 R-0142 (18 and 19), R-0011 (17 and 26). Moved: ISO RQ-09-11 (5 → 2, it verifies requirements), FDA App1.D-17 (9 → 10, code review), SAFECode Define Severity (15 → 17), FDA V.A.2-08 (15 → 27), BSIMM SR3.5 (31 → 32, governs AI adoption). BSIMM CR1.7 (AI mentioned only descriptively) removed. | Applied in the `rows.py` review block. Rationales rewritten. Every removal that empties a cell leaves a note saying why. |
| Row definitions | 4 | **R1:** row 21 (build provenance) was anchored on SSDF PS.3.2. PS.3.2 covers provenance of the *components* of a release, and it is also the anchor of SBOM row 20. Every PS.3.2 mapping was double-counted, and SSDF/ETSI counted as having build provenance. **R2:** rows 11 and 12 share PW.8.2. That is justified by PW.8.2 Example 6 (penetration testing), but it carried the generic CRA II(3) into row 12 as "sourced". **R3:** overlapping pairs (7/17, 15/27, 17/26, 18/19, 20/25, 25/29, 26/34) double-placed judgement ids (listed above). **R4:** BSIMM SR3.5 was filed under AI components rather than AI tool governance. | Row 21 is re-anchored on SLSA R-0010/R-0008; SSDF PS.3.2 and SSDIF-PS.3.2 stay as judgement only, and sourced drops 5 → 3. CRA II(3) is not adopted in row 12 (YAML `also`). Overlaps are de-duplicated. The narrowing of rows 7, 13 and 18 and the PW.6 move to row 8 were checked against the SSDF texts and are justified. |
| Counts & statements | 9 | Hard-coded numbers had gone stale: threat modelling "12 of 16 / 15", release gate "9 / 13", ISO "all 24", FDA "all 28". "Security testing is present in all 16 frameworks" rested on SLSA R-0150/0151. The report said "no SDL/maturity model has a support period" while SAMM O-OM-B is a sourced row-25 cell. The crypto divergence said SAMM has no crypto requirement while listing SAMM I-SD-B as sourced. The row-30 divergence contradicted its own IEC cell. The record cross-check reported a tie (row 14, 12 vs 12) as a "lean". The overlap ranking did not say that ETSI's cell is SSDF's by construction. | All numbers are now computed from the data. The prose is corrected. A tie is no longer reported as a lean. The ETSI caveat is added to "Biggest overlaps". |
| Contradictions | 1 of 15 | All 15 were reopened against both records. C-02's "15 differ / 5 disjoint" was recomputed exactly, and C-05 was re-derived from the form vs Table 2. C-01, C-03, C-04, C-06–C-10 and C-12–C-15 are confirmed as stated. **C-11** called SSDF's PW.4.1 → MSSDL #6 citation a "probable mis-numbering" without evidence: MSSDL-2021 practice 6 asks for vetted crypto libraries, which PW.4.1 covers. | C-11 is downgraded to *info* and its resolution reworded. No cell depended on it. |
| Editions | 0 | No current-edition id is substituted for a changed one. No SAMM or MS SDL cell is sourced from SSDF's SAMM 1.5 or MSSDL-2021 citations. All 40 old-edition `also` entries (SAMM 1.5, MSSDL-2021, ASVS 4.0.3) keep `refs: []` and an edition tag. BSIMM12/14 → 16 translations re-derived from Table 9 agree with every BSIMM edge used. ASVS 4.0.3 → 5 uses only ASVS 5's own mapping. | — |
| Public catalog | 2 | "Key source ids" showed judgement ids even when a published id existed (row 3 CRA showed Art 13(2)† rather than the published I(1)). Rows anchored outside SSDF led with SSDF ids: the secrets row led with PW.5.1, a broad OSPS mapping, rather than its OSPS/SAMM anchors. | Published ids are now listed first, and anchors lead for non-SSDF rows. The catalog regenerates from the YAML, so its counts match. |
| Structure / build | 3 | The front matter lacked `version_policy` and `reviewers`, which the other spec docs carry; adversarial critics are listed as reviewers there. Row-level notes were never written to the YAML. The build was non-deterministic: set iteration order changed provenance labels ("inherited from 5.1" vs "5.2"), the task picked for practice-level OSPS edges (PO.4.1 vs PO.4.2), notes and `record_phase_check` order between runs. | Front matter fields added. Row `note` is emitted. All set iteration is sorted, and the output is verified byte-identical across four hash seeds. |

### Residual (not fixed; for the human reviewer)

- **Judgement-only columns.** ISO/SAE 21434 (23 cells) and FDA (27 cells) are still 100% judgement. I read every id, but no second reviewer has. ISO RQ-11-01 is placed in penetration testing only on garbled Annex E spill text in the record.
- **Weak placements kept, each marked †:**
  - Product logging/forensics features as operational incident response: CRA I(2)(l) and FDA App1.F-04/F-06 (row 19).
  - FDA App1.D-02/03, device-side signature checks (row 13).
  - ISO RQ-10-09/10, generic verification (row 10).
  - ASVS P-18 (row 3), F-03/F-26 (row 11) and 16.1.1 (row 19).
  - BSIMM SFD1.1/SR3.3 (row 6), ETSI R-0002 (row 31) and TR-03185 R-0002 (row 32).
- **Overlaps accepted as faithful to the sources:**
  - RV.2.2 appears in rows 17, 22, 24 and 27, backed by its examples E1/E3/E4.
  - PW.9.1/9.2 appear in rows 14 and 29, because SSDF lists IEC SG-1 under PW.9.1.
  - "No default credentials" sits in both row 14 and row 33. UK APC-1.4-03 is published to both, by ETSI and OSPS respectively (C-09).
  - MS SDL practice 3 is in rows 3 and 5. ENISA 4.14-CL-08/RG-05 is in rows 13 and 21.
- **Non-atomic rows:** 6 (standard + inventory + PQC plan), 14 (defaults + guidance), 16 (environment + source code), 31 (inventory + provenance + threats) and 33 (development secrets + product credentials).
- **Translations that are ours:** "SLSA 1.1 Build L1" → R-0010, which carries TR-03185 BR.01/BR.06. Practice-level publisher entries ("PS.1", "PO.4", "PW.9") are expanded to tasks for *direct* links, labelled `(at …)`. `per_id` strings do not repeat the source edition for OSPS's SAMM 2.0 names and SLSA 1.0 names; it is given only in `publishers`.
- **ETSI is not independent of SSDF.** ETSI stays a counted column even though its cell equals SSDF's by construction. The overlap ranking now carries that caveat.
- **Library records not yet reviewed.** Human pass-4 review of the library records is outstanding. The ISO 21434 record also needs text repair.


