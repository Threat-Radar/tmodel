---
schema: "library-summary/v1"
id: greshake-2023-indirect-prompt-injection
record: greshake-2023-indirect-prompt-injection
type: summary
updated: "2026-10-29"
---

# Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

|  |  |
|---|---|
| **Type** | paper |
| **Maturity** | _unset_ (peer-reviewed workshop paper; no maturity level applies) |
| **Authors** | Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, Mario Fritz (Saarland University, CISPA Helmholtz Center for Information Security, sequire technology) |
| **Published** | arXiv v1 2023-02-23, titled "More than you've asked for: A Comprehensive Analysis of Novel Prompt Injection Threats to Application-Integrated Large Language Models"; v2 2023-05-05 under the current title (summarized here); ACM AISec '23, pp. 79-90 (Crossref date 2023-11-26) |
| **Identifier** | arXiv:2302.12173; DOI 10.1145/3605764.3623985 (ACM version of record, not read) |
| **Source** | https://arxiv.org/pdf/2302.12173v2 |
| **Digest** | `sha256:428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81` (arXiv v2, 33 pages) |

## Overview

An application that puts retrieved web pages, emails, documents or code into an LLM's
context lets whoever wrote that content instruct the model, because the model receives
data and instructions in one channel. The paper names this **indirect prompt injection**:
the attacker never talks to the model, but plants instructions where the application will
retrieve them, and the authors compare processing such content to executing attacker code
(abstract, §1, §3). They organise the threat in computer-security terms: four ways to
deliver an injection (passive retrieval, active delivery such as email, user-driven,
hidden), six threat classes (information gathering, fraud, intrusion, malware, manipulated
content, availability) and the parties affected (§3, Figure 2). Each class is demonstrated
on Bing Chat, GitHub Copilot or synthetic GPT-4 and text-davinci-003 applications with
tools, including a self-spreading email worm, re-infection from long-term memory,
remote control from an attacker's server, and hidden, multi-stage and Base64-encoded
payloads (§4). The authors conclude that no effective mitigation existed in 2023: patching
individual jailbreaks does not close the class, and each defense they consider has an open
weakness (§5.6).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | Introduces and demonstrates an attack class that is now standard for LLM applications |
| Cryptography | `none` | Base64 appears only as obfuscation of a payload (§4.3.2) |
| This project | `adjacent` | The object model has to express a threat that enters through a data source and acts through the model's tools; tmodel's own AI features read third-party text too |

`bears_on: DEC-001a` (the core type system, accepted in ADR-0010). Figure 3 traces one
attack path across three of RPT-0014's trust boundaries: external content into the
context (TB2), the model's tool calls (TB7) and egress back to the attacker (TB9).

## Implementations

Searched on 2026-10-29.

| Name | Kind | License | URL |
|---|---|---|---|
| greshake/llm-security | the paper's demonstration code and prompts | MIT | https://github.com/greshake/llm-security |

The paper gives this repository in footnote 1 and a second address,
github.com/greshake/lm-safety, in footnote 11. On 2026-10-29 the second redirected to the
first. Defenses are not this paper's subject; `spotlighting-indirect-prompt-injection` is
one.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this document |

## Limits

- **Preprint, not the version of record.** The digest is arXiv v2 (33 pages, with all
  prompts and screenshots in the appendix). The 12-page ACM version was not read, and the
  differences were not checked.
- **Qualitative only.** No success rates. The authors say measuring them in interactive
  sessions is hard and leave it to future work, while noting that their prompts often
  worked on the first attempt (§5.2).
- **Tested away from production.** To avoid planting real injections, Bing Chat was
  attacked through local HTML files opened in the Edge sidebar, and the agent attacks ran
  on synthetic apps whose tools return prepared content (§4.1, §5.2). Microsoft 365
  Copilot and ChatGPT plugins were not tested (§5.2).
- **The supply-chain vector was fragile.** The Copilot attack plants the injection in a
  comment of a popular package's documentation, which enters the completion context when a
  developer opens it (Figure 9). It worked, but was very sensitive to context and weaker
  inside larger applications (§4.2.4).
- **Threats, not techniques.** The taxonomy is threat-based on purpose, so that it
  outlives particular techniques (§3.2). It does not enumerate techniques; RPT-0014's AIT
  entries supply that level.
- **2023 systems.** Bing Chat on GPT-4, Copilot on Codex, text-davinci-003 and GPT-4 as of
  early 2023. The results do not show how current systems behave.
- **Mitigations are discussed, not evaluated** (§5.6).

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-064, AIT-108, AIT-102, AIT-091, AIT-067, AIT-066, AIT-111 | AIT-064 lists this paper first among its sources (incident INC-025). The demonstrations also instantiate a self-spreading email worm (AIT-108, §4.2.3), re-infection from long-term memory (AIT-102, §4.2.4), an assistant that reads the address book and sends mail as the user (AIT-091, §4.2.3), instructions hidden in HTML and Markdown comments (AIT-067, §4.1.2, §4.3.1), a persuaded user opening a link that carries their name (AIT-066, §4.2.1; a click, not image rendering) and looping background tasks that make Bing Chat time out (AIT-111, §4.2.6) |
| Existing AI threat models | adjacent | none | Figure 2 is a threat model for one attack class (delivery method, threat, affected party). threat-models.md does not list it |
| Weakness enumerations | adjacent | CWE-1427, NISTAML.015, NISTAML.016, NISTAML.017, NISTAML.027, NISTAML.036, NISTAML.039, AML.T0051.001, LLM01:2025 | Not an enumeration, but entries cite it: CWE-1427 as REF-1452 (CWE 5.0, checked 2026-10-29) and NIST AI 100-2e2025 as reference [146] for the six NISTAML ids listed (§3.4). AML.T0051.001 and LLM01:2025 are RPT-0014's mapping; their references were not checked |
| Attack → asset mapping | core | C01, C06, C07, C08, C09, C10, C12, C14 | Figure 3 maps one path: content in an external source (C01) is retrieved (C06) into the application (C07) or agent (C08), which calls tools (C09) to exfiltrate or act, or writes the payload to memory (C10). Users are the target of fraud and persuasion (C12), and Copilot is reached through a package a developer opens (C14). The component mapping is ours |
