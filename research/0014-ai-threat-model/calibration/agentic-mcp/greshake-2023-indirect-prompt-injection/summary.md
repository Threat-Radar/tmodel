---
schema: "library-summary/v1"
id: greshake-2023-indirect-prompt-injection
record: greshake-2023-indirect-prompt-injection
type: summary
updated: "2026-10-11"
---

# Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

|  |  |
|---|---|
| **Type** | paper (33 pp., incl. appendix of attack prompts) |
| **Maturity** | _unset — do not guess_ |
| **Authors** | K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, M. Fritz |
| **Published** | arXiv:2302.12173, v2 of 2023-05-05 (the copy read). The PDF states no venue; `sources.md` gives ACM AISec 2023 "from memory" — not verified here |
| **Identifier** | arXiv:2302.12173 |
| **Source** | https://arxiv.org/pdf/2302.12173 |
| **Digest** | `428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81` (matches `pdf-manifest.tsv`) |

## Overview

Introduces **indirect prompt injection**: once an LLM application retrieves
external content (web pages, emails, documents, code), anyone who can place text
in that content can steer the model **without direct access to it**, because the
model does not separate data from instructions — retrieved prompts act like
"arbitrary code". The paper builds a **threat taxonomy** borrowed from computer
security: *injection methods* (passive retrieval, active delivery such as email,
user-driven copy-paste, hidden multi-stage and encoded payloads) and *threats*
(information gathering, fraud, intrusion, malware, manipulated content,
availability), including self-spreading "prompts as worms", persistence through
an agent's memory, and remote control. It **demonstrates** these against Bing
Chat (GPT-4) via the Edge sidebar, against GitHub Copilot code completion, and
against synthetic GPT-4/LangChain agents with search, URL fetch, email, address
book and memory tools. It argues current mitigations (RLHF, input/output filters)
are "whack-a-mole" and that no robust defense yet exists.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | Defines a now-dominant attack class on LLM applications and agents. |
| Cryptography | none | Not about cryptography. |
| This project | core | The root cause behind most agentic/MCP attack classes in RPT-0014; tmodel needs it as an attack with explicit preconditions (untrusted content reaches an LLM that holds tools or data). |

Bears on **DEC-001** (object model — attack preconditions and components) and
**R-010** (maps to CWE-1427, which postdates the paper).

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-064, AIT-067, AIT-068, AIT-091, AIT-102, AIT-108 | Indirect injection; hidden (HTML-comment, invisible-text) and multimodal payloads; tool hijacking; memory persistence; spreading prompts ("prompts as worms") |
| Existing AI threat models | adjacent | — | Gives a threat taxonomy for LLM-integrated apps, not a full threat-modeling method |
| Weakness enumerations | adjacent | CWE-1427, AML.T0051.001, LLM01:2025 | The paper names no catalog ids; these are the later catalog entries for its attack |
| Attack → asset mapping | core | C01, C06, C07, C08, C09, C10, C12, C14, C20 | Maps injection channels and impacts onto web/email sources, retrieval, the app layer, agent tools and memory, users, the IDE and the browser sidebar |

## Implementations

Attack prompts are in the paper's appendix and the authors' GitHub repository
(cited in the paper). No tool to build on; searched 2026-10-11.

| Name | Kind | License | URL |
|---|---|---|---|

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this summary |

## Limits

- **2023 systems.** Bing Chat, Copilot and the models tested have changed; the
  demonstrations show feasibility, not current success rates.
- **Mostly qualitative.** Synthetic apps run at temperature 0 with prepared
  content; no systematic measurement across many injections (the authors say so).
- **No defense evaluated.** Mitigations are discussed, not tested.
- **Venue unverified.** Cite the arXiv version unless the published version is checked.
