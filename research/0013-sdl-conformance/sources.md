---
schema: "archdoc/v1"
id: RPT-0013-sources
title: "RPT-0013 source log"
type: research
status: draft
version: "0.3.0"
date: "2026-10-01"
updated: "2026-10-03"
record: RPT-0013
---

# RPT-0013 — source log

**Ingested (2026-10-03).** Every SDL source is now a record in `library/`, topic `sdl`
(Threat-Radar/library, branch `feat/sdl-references`). "FX-1 full" = normative text, every
requirement, design notes and an object-model pass, then an independent adversarial verify and a
cross-check pass (`distilled/verification.md` in each record). "summarized" = paywalled or
licence-walled (free official material only) or secondary. Human review (pass 4) is outstanding for
all of them. Sources are hashed and cached locally; no third-party bytes are committed.

| source | version | extraction | library record |
|---|---|---|---|
| BSI TR-03183-1 | 1.0.0 | FX-1 full | `bsi-tr-03183-1` |
| BSI TR-03185 | 1.1.1 | FX-1 full | `bsi-tr-03185` |
| BSIMM16 | 16 | FX-1 full | `bsimm-16` |
| CIS/SAFECode Secure by Design v1.1 | 1.1 | stub | `cis-safecode-sbd-assessment-1-1` |
| CISA Secure by Design (2023) | 2023-10-25 revision (first published Apr | FX-1 full | `cisa-secure-by-design-2023` |
| CISA Secure by Design Pledge | May 2024 | FX-1 full | `cisa-secure-by-design-pledge-2024` |
| CISA Secure Software Development Attestation Form | 1.0 | FX-1 full | `cisa-ssdf-attestation-form-2024` |
| CISA/FBI Secure by Demand Guide | As of August 2024 | FX-1 full | `cisa-secure-by-demand-guide-2024` |
| CNCF SSCBP v2 | v2 | summarized | `cncf-supply-chain-best-practices-v2` |
| Cyber Resilience Act (CRA) | OJ L 2024/2847 (20.11.2024) as corrected | FX-1 full | `eu-cra-2024-2847` |
| ENISA SbD&D Playbook v1.0 | 1.0 | FX-1 full | `enisa-sbd-playbook-2026` |
| EO 14028 | as issued 2021-05-12 (in force 2026-10-0 | FX-1 full | `eo-14028` |
| EO 14144 | as issued 2025-01-16; amended by EO 1430 | summarized | `eo-14144` |
| EO 14306 | as issued 2025-06-06 | summarized | `eo-14306` |
| ESF Securing the Software Supply Chain — Developers | August 2022 (Part 1 of 3) | FX-1 full | `esf-sscs-developers-2022` |
| ETSI TS 104 219 (SSDIF) | V1.1.1 | FX-1 full | `etsi-ts-104-219` |
| FDA premarket cybersecurity guidance | 2026-02-03 final (Level 2 revision; supe | FX-1 full | `fda-premarket-cybersecurity-guidance` |
| IEC 62443-4-1 | Edition 1.0 (2018) | summarized | `iec-62443-4-1-2018` |
| IEC 81001-5-1 | Edition 1.0 (2021-12), corrected version | summarized | `iec-81001-5-1-2021` |
| ISO/IEC 27034-1 | 2011 (ed. 1) + Cor 1:2014 | summarized | `iso-iec-27034-1` |
| ISO/IEC 29147 | 2018 (Edition 2) | summarized | `iso-iec-29147-2018` |
| ISO/IEC 30111 | 2019 (Edition 2) | summarized | `iso-iec-30111-2019` |
| ISO/SAE 21434 | 2021 | distilled | `iso-sae-21434-2021` |
| Microsoft SDL (10 practices) | web practice set (10 practices, 48 sub-p | FX-1 full | `microsoft-sdl` |
| Microsoft SDL 5.2 | 5.2 | FX-1 full | `microsoft-sdl-5-2` |
| NIST SP 800-204D | Final (February 2024) | FX-1 full | `sp-800-204d` |
| OMB M-22-18 | M-22-18 | FX-1 full | `omb-m-22-18` |
| OMB M-23-16 | M-23-16 | FX-1 full | `omb-m-23-16` |
| OMB M-26-05 | M-26-05 | FX-1 full | `omb-m-26-05` |
| OpenSSF Concise Guide (developing) | living; main@99c65a8522 (2026-09-19) | summarized | `openssf-concise-guide-secure-software` |
| OpenSSF Scorecard checks | v5.5.0 | summarized | `openssf-scorecard-checks` |
| OSPS Baseline | v2026.08.28 | FX-1 full | `openssf-osps-baseline` |
| OWASP ASVS 5.0.0 | 5.0.0 | FX-1 full | `owasp-asvs-5` |
| OWASP DSOMM | 5.1.0 | summarized | `owasp-dsomm` |
| OWASP SAMM 2.2 | 2.2.0 | FX-1 full | `owasp-samm-2` |
| PCI Secure SLC v2.0 | 2.0 | summarized | `pci-secure-slc-2` |
| SAFECode FPSSD 3rd ed. | 3rd edition | FX-1 full | `safecode-fpssd-3` |
| Secure by Demand — OT priority considerations | 2025-01-13 | summarized | `cisa-secure-by-demand-ot-2025` |
| Simplified SDL (2010) | updated November 4, 2010 | FX-1 full | `microsoft-sdl-simplified-2010` |
| SLSA 1.2 | 1.2 | FX-1 full | `slsa-1-2` |
| SP 800-218A (SSDF Community Profile for AI Model Development) | July 2024 (final) | FX-1 full | `sp-800-218a` |
| SP 800-53r5 | Rev. 5 (upd1, 2020-12-10) + Release 5.2. | summarized | `sp-800-53r5` |
| SSDF 1.1 | 1.1 | FX-1 full | `sp-800-218` |
| SSDF 1.2 (SP 800-218r1 ipd) | 1.2 ipd | FX-1 full | `sp-800-218r1` |
| UK Software Security Code of Practice | May 2025 (Code); Implementation Guidance | FX-1 full | `uk-software-security-code-of-practice` |

**Still pending (not SDL specifications; lanes 4–5 context):** NIST OSCAL, OMG SACM v2.1, SysML v2
View/Viewpoint, GSA OSCAL→Word, Kyverno. Already held elsewhere in the library: `iso-26262-3-2018`,
`sp-800-161r1` (stub), `in-toto-attestation-v1`, `sigstore-2022`.

**Candidates found but not ingested** (discovery search 2026-10-02): FprEN 40000-1-2 / prEN 40000-1-3
(CRA harmonised standards, in approval), PCI Secure Software Standard v2.0, ISO/IEC 27002:2022 §8.25–8.31,
DO-326B/ED-202B (aviation), ECSS-E-ST-80C (space), IEC 63452 / CLC/TS 50701 (rail), ANSI/AAMI SW96,
ISO/IEC 15408-3:2026 (ALC), ASD ISM software-development guidelines, NIST SP 1800-44 (draft),
CISA 2026 SBOM minimum elements (held as `cisa-2026-sbom-minimum`).
