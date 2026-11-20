---
schema: "library-summary/v1"
id: greshake-2023-indirect-prompt-injection
record: greshake-2023-indirect-prompt-injection
type: summary
updated: "2026-11-10"
lane: catalogs-schema
reviewed_by: ""
---

# Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

|  |  |
|---|---|
| **Type** | paper (peer-reviewed workshop paper) |
| **Maturity** | _unset_ |
| **Authors** | Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, Mario Fritz |
| **Published** | AISec '23 (16th ACM Workshop on Artificial Intelligence and Security), 2023-11-26, pp. 79–90. arXiv v1 2023-02-23, v2 2023-05-05 |
| **Identifier** | DOI 10.1145/3605764.3623985; arXiv:2302.12173 |
| **Source** | https://arxiv.org/pdf/2302.12173 (arXiv v2, 33 pages including appendix) |
| **Digest** | `428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81` (arXiv v2 PDF; matches `pdf-manifest.tsv`) |

The venue and DOI were checked against Crossref on 2026-11-08. `sources.md` S-0166 gives the venue only "from memory". The digest is of the arXiv v2 PDF, not the ACM version of record, so the two texts may differ.

## Overview

Once an LLM application retrieves content (web pages, email, documents, code) and can call tools, anyone who can place text where it will be retrieved can steer the model. They need no direct access to it: the paper argues that LLM-integrated applications "blur the line between data and instructions" (Abstract).

The authors name this **indirect prompt injection**. They give a threat taxonomy borrowed from cyber-threat taxonomies rather than a technique list:
- **injection methods:** passive, active, user-driven and hidden;
- **threats:** information gathering, fraud, intrusion, malware, manipulated content and availability;
- **targets:** untargeted or targeted (Fig. 2, §3).

They demonstrated each threat against Bing Chat (GPT-4), against code completion, and against synthetic LangChain or GPT-4 agents with search, email, URL and memory tools (§4). The demonstrations include data exfiltration, a self-spreading email "worm", remote control, and persistence through a memory tool.

Their mitigation discussion is candid that no robust defence existed (§5.6). Filtering, a supervising LLM and RLHF all face a dilemma: a model capable enough to recognise an encoded injection is also capable enough to follow it.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | It defines and first demonstrates a now-central attack class (NISTAML.015, LLM01:2025, AML.T0051.001). |
| Cryptography | none | No cryptographic content. |
| This project | adjacent | Bears on **R-018**, because tmodel's AI-proposal hook (DL-0044, DL-0046) feeds repository and library text to an agent. By this paper's argument, that text can carry instructions, which is why agent output must stay a `proposed` assertion until a human reviews it. Also bears on **DEC-009**: its threats are generic threats to map onto LLM-integrated products. |

## Implementations

Searched 2026-11-08 (GitHub):

| Name | Kind | License | URL |
|---|---|---|---|
| greshake/llm-security | the paper's demonstration code and prompts | MIT | https://github.com/greshake/llm-security |
| garak | LLM scanner whose probes include indirect prompt injection | Apache-2.0 | https://github.com/NVIDIA/garak |

Defences that grew from this line of work are records in their own right, for example `spotlighting-indirect-prompt-injection` (S-0265).

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: identifiers, digest, applicability, tags |
| `summary.md` | this summary, with the RPT-0014 applicability table |

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-064, AIT-108, AIT-102, AIT-111, AIT-068 | Primary evidence. §4.2 demonstrates indirect prompt injection (AIT-064), an email worm (§4.2.3, AIT-108), memory persistence (§4.2.4, AIT-102) and slow or blocked service (§4.2.6). The time-consuming background task in §4.2.6 is a loop of instructions that makes the model time out. NIST names it `NISTAML.017`, citing this paper, and the catalog files `.017` under AIT-111. The search-disruption attacks in §4.2.6 resemble AIT-088 (RAG jamming, `.016`), but that entry is about a poisoned retrieval index, so it is noted here, not linked. The multimodal case (AIT-068) is only a limited LLaVA example (§5.3, Fig. 28). |
| Existing AI threat models | adjacent | — | Fig. 2 is a threat model of LLM-integrated applications (method × threat × target), but it has no system decomposition and no TM id in `threat-models.md`. |
| Weakness enumerations | adjacent | NISTAML.015, NISTAML.016, NISTAML.017, LLM01:2025, AML.T0051.001, CWE-1427 | It predates these ids and is cited by them, through RPT-0014's AIT-064 `catalog_ids` and `sources`. NIST cites it ([146]) as the only source for `.016`, availability attacks through indirect prompt injection, and `.017`, time-consuming background tasks (§3.4.1). It defines no ids of its own. |
| Attack → asset mapping | core | A07, A09, A04, A06, A11, A13; C06, C07, C08, C09, C10, C17 | Each threat names its target. Information gathering takes user data and credentials (A07, A09); intrusion reaches the system prompt, tools and memory (A04, A06; C08–C10); availability hits A11; manipulated content hits A13. Delivery comes through retrieval and the application (C06, C07) to downstream consumers (C17). |

## Reference expansion

Checked against `sources.md` on 2026-11-08: Perez and Ribeiro, "Ignore previous prompt" (S-0149), and Kang et al., programmatic dual-use (S-0173), are already there. No in-scope cited reference was found missing in this pass, but the pass covered only the references the threat taxonomy relies on, not all 82.

## Limits

- **No real-world injections.** To avoid harming users, the authors did not plant prompts in public sources. The attacks ran on synthetic applications and on local HTML pages in Bing Chat's sidebar (§5.2), so in-the-wild success is argued from anecdote, not measured.
- **No success rates.** The paper is qualitative and says quantification is future work (§5.2). Its claim that injections were "rather simple" to write rests on the authors' own experience.
- **2023 systems.** Bing Chat, `text-davinci-003` and early plugins have changed or gone. The threat classes hold up (later incidents in RPT-0014 confirm them), but the specific demonstrations may not reproduce.
- **Mitigations are discussed, not evaluated.** Later defences (spotlighting, CaMeL-style control/data separation, tool restrictions) are not covered.
