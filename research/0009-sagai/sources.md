---
schema: "archdoc/v1"
id: RPT-0009-sources
title: "RPT-0009 source log"
type: research
status: draft
version: "0.5.0"
date: "2026-09-28"
updated: "2026-11-02"
record: RPT-0009
---

# RPT-0009: source log

Every source found, and the `library/` record it became. `—` in bears_on means
not yet assessed. Since 0.4.0 (#189) every row has a record or a written reason
it has none; "stub" means pinned by digest with a written summary, not extracted.
0.5.0 adds the sources the adversarial review found (DL-0006).

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| SAGAI workshop series, IEEE S&P workshops (2024, 2025, 2026) | hierarchy | 1 | `sagai-workshop` (summarized) | — |
| Hines et al., *Defending Against Indirect Prompt Injection Attacks With Spotlighting* (SAGAI'24); [arXiv 2403.14720](https://arxiv.org/abs/2403.14720) | paper | 2 | `spotlighting-indirect-prompt-injection` (summarized) | — |
| Sharma, Gupta, Grossman, *Defending Language Models Against Image-Based Prompt Attacks via User-Provided Specifications* (SAGAI'24); [author PDF](https://homes.cs.washington.edu/~reshabh/SAGAI.pdf), [IEEE Xplore 10579532](https://ieeexplore.ieee.org/abstract/document/10579532) | paper | 2 | `spml-image-prompt-injection` (summarized) | — |
| Kang et al., *Exploiting Programmatic Behavior of LLMs: Dual-Use Through Standard Security Attacks* (SAGAI'24); [arXiv 2302.05733](https://arxiv.org/abs/2302.05733) | paper | 2 | `llm-programmatic-dual-use` (summarized) | — |
| Liu et al., *Pre-trained Encoders in Self-Supervised Learning Improve Secure and Privacy-preserving Supervised Learning* (SAGAI'24); [arXiv 2212.03334](https://arxiv.org/abs/2212.03334) | paper | 2 | `pretrained-encoders-secure-learning` (summarized) | — |
| Christodorescu et al., *Systems Security Foundations for Agentic Computing* (arXiv 2512.01295); the SAGAI'25 report: v1's Introduction says so, and v2 drops the sentence | paper | 2 | `systems-security-agentic-computing` (summarized; `part_of: sagai-workshop` since library#40) | — |
| Christodorescu et al., *Agent Security is a Systems Problem* (arXiv 2605.18991) | paper | 2 | `agent-security-systems-problem` (stub, library#40) | — |
| Christodorescu et al., *Securing the Future of GenAI: Policy and Technology* (arXiv 2407.12999); related Oct 2023 workshop | paper | 2 | `securing-future-genai-policy-technology` (stub, library#40) | — |
| *Lessons from Penetration Tests on Large-Scale Agent Systems*, [arXiv 2605.27042](https://arxiv.org/abs/2605.27042) ("Accepted at SAGAI 2026") | paper | 2 | `pentest-lessons-agent-systems` (stub, library#40) | — |
| *CacheProbe: Auditing Prompt Cache Isolation in Gateway APIs*, [arXiv 2605.30613](https://arxiv.org/abs/2605.30613) ("Accepted at SAGAI '26") | paper | 2 | `cacheprobe-prompt-cache-isolation` (stub, library#40) | — |
| *Challenges and Future Directions in Agentic Reverse Engineering Systems*, [arXiv 2604.14317](https://arxiv.org/abs/2604.14317) ("accepted at SAGAI 2026") | paper | 2 | `agentic-reverse-engineering-challenges` (stub, library#40) | — |
| Fraunhofer IESE "SAGAI" (*Software Architecture and Generative AI*); name clash, out of scope | web | 1 | `fraunhofer-iese-sagai` (not-useful, library#40) | — |
| ETSI EN 304 223 V2.1.1 (2025-12), *SAI; Baseline Cyber Security Requirements for AI Models and Systems* | spec | 3, 7 | `etsi-en-304-223` (FX-1, library#32) | DEC-001b, R-018 |
| ETSI TS 104 223 V1.1.1 (2025-04); superseded by EN 304 223 | spec | 3 | `etsi-ts-104-223` (stub, library#40; `superseded_by: etsi-en-304-223`) | — |
| ETSI TR 104 128, *SAI; Guide to Cyber Security for AI Models and Systems* | spec | 3 | `etsi-tr-104-128` (stub, library#40; clause 6 read for report §3) | — |
| ETSI TS 104 050 V1.1.1 (2025-03), *SAI; AI Threat Ontology and definitions*; updates and extends GR SAI 001 | spec | 3, 8 | `etsi-ts-104-050` (stub, library#40) | — |
| ETSI TR 104 222 V1.2.1, *SAI; Mitigation Strategy Report* | spec | 3 | no record: found by the adversarial review and not yet read; no claim in the report rests on it beyond its existence (§6) | — |
| ETSI TS 104 216, *SAI; Conformance assessment for AI (EN 304 223)* | spec | 3 | no record: unpublished (work item DTS/SAI-00025; no deliverable at etsi.org/deliver on 2026-11-02) | — |
| ETSI Technical Committee Securing Artificial Intelligence (TC SAI) | consortium | 3 | no record: a committee, not a document; it is the named author of each ETSI record | — |
| CISA et al., *Principles for the Secure Integration of Artificial Intelligence in Operational Technology* (Dec 2025) | spec | 4, 7 | `cisa-ai-in-ot-principles` (FX-1, library#32) | DEC-001b, R-018 |
| ETSI TR 104 048, *SAI; Data Supply Chain Security* (cited by CISA §3.4) | spec | 3 | `etsi-tr-104-048` (stub, library#40) | — |
| Barrett et al., *Identifying and Mitigating the Security Risks of Generative AI* (July 2023 workshop; cited by arXiv 2407.12999) | paper | 2 | no record: a lead from §2.7 only; no claim in the report rests on it | — |
| NCSC-UK and CISA, *Guidelines for Secure AI System Development* | spec | 5 | `ncsc-secure-ai-guidelines-2023` (stub, library#40) | — |
| UK Government, *Code of Practice for the Cyber Security of AI* and its Implementation Guide | spec | 5 | `uk-ai-cyber-security-code-2025` (stub, library#40); the Implementation Guide is not pinned | — |
| NIST AI 100-1, *AI Risk Management Framework* | spec | 5 | no record: no claim in the report rests on it (risk management, not attacks); EN 304 223 cites it as [i.8] | — |
| NIST AI 100-2 E2025 (March 2025), *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*, <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf> (`4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646`); the attack classes and `NISTAML.*` ids of Table 2 | spec | 5, 7 | `nist-ai-100-2-e2025` (stub, library#40; G12) | DEC-008 |
| MITRE ATLAS 2026.09 (format 6.0.0), <https://raw.githubusercontent.com/mitre-atlas/atlas-data/v2026.09/dist/v6/ATLAS-2026.09.yaml> (`935efa93e28294432d3e2f537eb94991ef8d1f8c58341cd360ea3321ddb66688`); technique ids, and case study AML.CS0059 (EchoLeak). Shared with RPT-0014. ATLAS 2026.10 (2026-10-28) is not pinned; what it changes is in report §6 | dataset | 5, 7, 8 | `mitre-atlas` (stub, library#40; G12; shared with RPT-0014, #71) | DEC-008 |
| OWASP AI Exchange; OWASP Top 10 for LLM Applications | web | 5 | no record: cited only as the EchoLeak case study's own mapping (its Table 2 maps the output steps to LLM02, Insecure Output Handling; §5, G11), quoted from that paper; OWASP's LLM catalog ids are RPT-0014's (#71) | — |
| NSA et al., *Deploying AI Systems Securely*; *AI Data Security* | spec | 5 | no record: no claim in the report rests on them | — |
| CISA 2025 SBOM Minimum Elements; G7 *SBOM for AI* (belongs to #8; stub only) | spec | 5 | no record here: #8's. The library holds the final `cisa-2026-sbom-minimum` (not the 2025 draft) and `g7-sbom-for-ai-2026` | — |
| Reddy and Gujral (The George Washington University), *EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System*, [arXiv 2509.10540v1](https://arxiv.org/abs/2509.10540) (2025-09-06; AAAI Fall Symposium Series 2025; abstract page `34574691…20b51`, HTML `c972c562…3cce5`); a secondary case study built from public material | paper | 8 | `echoleak-zero-click-prompt-injection` (stub, library#40; pins the v1 PDF) | DEC-001b |
| Aim Labs (Aim Security), the EchoLeak disclosure, <https://www.aim.security/lp/aim-labs-echoleak-m365>; the finders' own account, cited by the CVE record | web | 8 | `aim-labs-echoleak-disclosure` (stub, library#40; not pinned: the page returned HTTP 403 to `bin/ingest --fetch`, so it has no digest and no claim rests on its content) | DEC-001b |
| CVE-2025-32711, <https://cveawg.mitre.org/api/cve/CVE-2025-32711> (`614e8f67…bdd9b`, fetched 2026-10-21) | dataset | 8 | `cve-json-5` is the format; no record per CVE | DEC-008 |
| CWE 4.20 entries CWE-74 and CWE-1427, <https://cwe.mitre.org/data/definitions/74.html>, <https://cwe.mitre.org/data/definitions/1427.html> (fetched 2026-10-21); CWE 5.0 is now current (checked 2026-11-02), and the pins stay at 4.20 | dataset | 8 | `cwe` (FX-1, library#21) | DEC-008 |

Full digests for the rows above are in the header of [example-models/em-01-echoleak-m365-copilot.yaml](example-models/em-01-echoleak-m365-copilot.yaml).

## Open questions

- ~~Is arXiv 2512.01295 the SAGAI'25 research-challenges document?~~ Yes (2026-11-02): its v1 Introduction calls it the report of "the IEEE Secure Generative AI Agents 2025 workshop (SAGAI …)".
- ~~SAGAI'26 program: find its papers or talks another way.~~ Three accepted papers found through an arXiv search of author comments (2026-11-02); the program page still returns 404.
- SAGAI'24 papers are in the IEEE SPW 2024 proceedings; free copies are linked above. Find the IEEE Xplore entry for the three arXiv papers.
