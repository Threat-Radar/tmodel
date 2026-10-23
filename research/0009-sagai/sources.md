---
schema: "archdoc/v1"
id: RPT-0009-sources
title: "RPT-0009 source log"
type: research
status: draft
version: "0.3.0"
date: "2026-09-28"
updated: "2026-10-22"
record: RPT-0009
---

# RPT-0009: source log

Every source found, and the `library/` record it became. `—` in bears_on means
not yet assessed.

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| SAGAI workshop series, IEEE S&P workshops (2024, 2025, 2026) | hierarchy | 1 | `sagai-workshop` (summarized) | — |
| Hines et al., *Defending Against Indirect Prompt Injection Attacks With Spotlighting* (SAGAI'24); [arXiv 2403.14720](https://arxiv.org/abs/2403.14720) | paper | 2 | `spotlighting-indirect-prompt-injection` (summarized) | — |
| Sharma, Gupta, Grossman, *Defending Language Models Against Image-Based Prompt Attacks via User-Provided Specifications* (SAGAI'24); [author PDF](https://homes.cs.washington.edu/~reshabh/SAGAI.pdf), [IEEE Xplore 10579532](https://ieeexplore.ieee.org/abstract/document/10579532) | paper | 2 | `spml-image-prompt-injection` (summarized) | — |
| Kang et al., *Exploiting Programmatic Behavior of LLMs: Dual-Use Through Standard Security Attacks* (SAGAI'24); [arXiv 2302.05733](https://arxiv.org/abs/2302.05733) | paper | 2 | `llm-programmatic-dual-use` (summarized) | — |
| Liu et al., *Pre-trained Encoders in Self-Supervised Learning Improve Secure and Privacy-preserving Supervised Learning* (SAGAI'24); [arXiv 2212.03334](https://arxiv.org/abs/2212.03334) | paper | 2 | `pretrained-encoders-secure-learning` (summarized) | — |
| Christodorescu et al., *Systems Security Foundations for Agentic Computing* (arXiv 2512.01295); probably the SAGAI'25 output, unconfirmed | paper | 2 | `systems-security-agentic-computing` (summarized) | — |
| Christodorescu et al., *Agent Security is a Systems Problem* (arXiv 2605.18991) | paper | 2 | not yet a record | — |
| Christodorescu et al., *Securing the Future of GenAI: Policy and Technology* (arXiv 2407.12999); related Oct 2023 workshop | paper | 2 | not yet a record | — |
| Fraunhofer IESE "SAGAI" (*Software Architecture and Generative AI*); name clash, out of scope | web | 1 | not yet a record (record as not-useful) | — |
| ETSI EN 304 223 V2.1.1 (2025-12), *SAI; Baseline Cyber Security Requirements for AI Models and Systems* | spec | 3, 7 | `etsi-en-304-223` (FX-1, library#32) | DEC-001b, R-018 |
| ETSI TS 104 223 V1.1.1 (2025-04); superseded by EN 304 223 | spec | 3 | not yet a record | — |
| ETSI TR 104 128, *SAI; Guide to Cyber Security for AI Models and Systems* | spec | 3 | not yet a record | — |
| ETSI TS 104 216, *SAI; Conformance assessment for AI (EN 304 223)* | spec | 3 | not yet a record | — |
| ETSI Technical Committee Securing Artificial Intelligence (TC SAI) | consortium | 3 | not yet a record | — |
| CISA et al., *Principles for the Secure Integration of Artificial Intelligence in Operational Technology* (Dec 2025) | spec | 4, 7 | `cisa-ai-in-ot-principles` (FX-1, library#32) | DEC-001b, R-018 |
| ETSI TR 104 048, *SAI; Data Supply Chain Security* (cited by CISA §3.4) | spec | 3 | not yet a record | — |
| Barrett et al., *Identifying and Mitigating the Security Risks of Generative AI* (July 2023 workshop; cited by arXiv 2407.12999) | paper | 2 | not yet a record | — |
| NCSC-UK and CISA, *Guidelines for Secure AI System Development* | spec | 5 | not yet a record | — |
| UK Government, *Code of Practice for the Cyber Security of AI* and its Implementation Guide | spec | 5 | not yet a record | — |
| NIST AI 100-1, *AI Risk Management Framework* | spec | 5 | not yet a record | — |
| NIST AI 100-2 E2025 (March 2025), *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*, <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf> (`4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646`); the attack classes and `NISTAML.*` ids of Table 2 | spec | 5, 7 | not yet a record (G12) | DEC-008 |
| MITRE ATLAS 2026.09 (format 6.0.0), <https://raw.githubusercontent.com/mitre-atlas/atlas-data/v2026.09/dist/v6/ATLAS-2026.09.yaml> (`935efa93e28294432d3e2f537eb94991ef8d1f8c58341cd360ea3321ddb66688`); technique ids, and case study AML.CS0059 (EchoLeak). Shared with RPT-0014 | dataset | 5, 7, 8 | not yet a record (G12) | DEC-008 |
| OWASP AI Exchange; OWASP Top 10 for LLM Applications | web | 5 | not yet a record | — |
| NSA et al., *Deploying AI Systems Securely*; *AI Data Security* | spec | 5 | not yet a record | — |
| CISA 2025 SBOM Minimum Elements; G7 *SBOM for AI* (belongs to #8; stub only) | spec | 5 | not yet a record | — |
| Reddy and Gujral, *EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System*, [arXiv 2509.10540v1](https://arxiv.org/abs/2509.10540) (2025-09-06; abstract page `34574691…20b51`, HTML `c972c562…3cce5`) | paper | 8 | not yet a record | DEC-001b |
| CVE-2025-32711, <https://cveawg.mitre.org/api/cve/CVE-2025-32711> (`614e8f67…bdd9b`, fetched 2026-10-21) | dataset | 8 | `cve-json-5` is the format; no record per CVE | DEC-008 |
| CWE 4.20 entries CWE-74 and CWE-1427, <https://cwe.mitre.org/data/definitions/74.html>, <https://cwe.mitre.org/data/definitions/1427.html> (fetched 2026-10-21) | dataset | 8 | `cwe` (FX-1, library#21) | DEC-008 |

Full digests for the rows above are in the header of [example-models/em-01-echoleak-m365-copilot.yaml](example-models/em-01-echoleak-m365-copilot.yaml).

## Open questions

- Is arXiv 2512.01295 the SAGAI'25 research-challenges document? Ask @nymble.
- SAGAI'26 program: the site's program page returns 404; find its papers or talks another way.
- SAGAI'24 papers are in the IEEE SPW 2024 proceedings; free copies are linked above. Find the IEEE Xplore entry for the three arXiv papers.
