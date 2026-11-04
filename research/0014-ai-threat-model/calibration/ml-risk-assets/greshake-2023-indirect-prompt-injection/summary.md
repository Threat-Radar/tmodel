---
schema: "library-summary/v1"
id: greshake-2023-indirect-prompt-injection
record: greshake-2023-indirect-prompt-injection
type: summary
updated: "2026-11-01"
---

# Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

|  |  |
|---|---|
| **Type** | paper |
| **Maturity** | _unset_. Peer-reviewed workshop paper; the RFC 2026 scale does not apply and no standing is asserted |
| **Authors** | Kai Greshake (Saarland University; sequire technology), Sahar Abdelnabi (CISPA), Shailesh Mishra (Saarland University), Christoph Endres (sequire technology), Thorsten Holz (CISPA), Mario Fritz (CISPA) |
| **Published** | AISec '23, the 16th ACM Workshop on Artificial Intelligence and Security, co-located with CCS '23 in Copenhagen: pp. 79–90, ACM, online 2023-11-26 (Crossref). Preprint arXiv v1 2023-02-23, v2 2023-05-05 (arXiv) |
| **Identifier** | doi:10.1145/3605764.3623985; arXiv:2302.12173 |
| **Source** | https://arxiv.org/pdf/2302.12173v2 (the text read; the ACM PDF returned HTTP 403 on 2026-11-01) |
| **Digest** | `sha256:428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81` (7,306,999 bytes, 33 pages, arXiv v2, retrieved 2026-11-01). It matches `pdf-manifest.tsv`, whose unversioned URL currently serves the same v2 bytes |

Locators are the paper's printed page numbers: body pp. 1–13, appendix of prompts and screenshots pp. 14–33.

## Overview

**The argument.** Once an LLM application retrieves outside content, data and instructions are no longer separate. Anyone who can place text where the application will read it can steer the model without ever talking to it, so processing retrieved text is comparable to running arbitrary code with the application's capabilities (pp. 1–3).

**Taxonomy.** The paper adapts a cyber threat taxonomy [45] to this setting (Fig. 2, §3).
- *Injection methods:* passive (web pages, SEO, code repositories, retrieved files), active (emails), user-driven (copy and paste), and hidden (multi-stage, encoded, in images).
- *Threats:* information gathering, fraud, intrusion, malware (including self-spreading prompts), manipulated content, and availability.
- *Affected parties:* end users, developers, automated systems, and the model itself.

**Demonstrations.** Each threat is demonstrated qualitatively (§4) on:
- synthetic GPT-4 and text-davinci-003 applications with mock tools;
- Bing Chat, with injections served as local HTML read by the Edge sidebar;
- GitHub Copilot.

**Defences.** The paper argues that input/output filtering and RLHF do not address injected data. It discusses candidate defences but evaluates none (§5.6).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | Introduces and demonstrates a primary attack class against LLM applications and agents |
| Cryptography | `none` | "Encrypted" or encoded payloads (pp. 4, 12) mean obfuscation such as Base64; no cryptography is involved |
| This project | `core` | Indirect prompt injection is a central RPT-0014 attack class. Our interpretation: tmodel's own AI-assisted research pipeline reads third-party documents, so the same threat applies to it |

`bears_on: R-020, DEC-009`. This is our interpretation and covers only part of DEC-009.

**What supports it.**
- §3.1 ties each injection method to an application feature: search retrieval, a browser sidebar that reads the page, code-completion context, retrieval plugins, and email processing.
- §4.1.1 and Fig. 3 show that the tools an application holds decide what a compromised model can do: search, fetch URL, read and send email, address book, memory.
- So mapping this generic threat onto a specific product (R-020) depends on that product's retrieval channels and tools. The paper does not perform such a mapping.

**What it does not cover.** Mitigation-lifecycle tracking (R-021, the other half of DEC-009).

**Considered and not included: R-018** (human review of machine-proposed elements). The paper shows search-chat answers that look grounded in citations but are wrong (§4.2.5, Fig. 18), and says users cannot be expected to watch every sub-operation (§5.5). Linking that to tmodel's review requirement would be our inference about a different kind of system, so it is left for a reviewer to decide.

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-064, AIT-067, AIT-068, AIT-071, AIT-073, AIT-091, AIT-102, AIT-108, AIT-112 | The primary demonstration of indirect prompt injection, done as research rather than observed in the wild (§5.1–5.2: no public injections). Evidence for each AIT is listed below the table |
| Existing AI threat models | adjacent | — (no TM entry in `threat-models.md`) | The authors call Fig. 2 an overview of their threat model (p. 3), but it is a taxonomy: injection methods × threats × affected parties, deliberately threat-based rather than technique-based (p. 4). Fig. 3 illustrates the attack flow. It has no asset inventory, risk method or mitigation mapping, and covers one attack vector. Whether it merits a TM entry is an integration question; this record only notes the absence |
| Weakness enumerations | adjacent | NISTAML.015, .016, .017, .027, .036, .039 | No enumeration or ids of its own. It names the root cause, a shared channel for data and instructions (pp. 1, 3, 6), which later catalogs encode. The NISTAML ids are verified: NIST AI 100-2e2025 cites this paper as [146] in exactly those sections (S-0855 §3.4, pp. 50–53). The preliminary RPT-0014 ids (AML.T0051.001, LLM01:2025, ASI01 and CWE-1427 in `sources.md`; AML.CS0020 in `incidents.md`) are **not verified** here, and the paper neither uses nor cites them |
| Attack → asset mapping | core | A03, A06, A07, A08, A09, A11; C01, C06, C07, C08, C09, C10, C12, C14, C20; TB2, TB7, TB9, TB13 — **assigned by us, not by the authors** | The paper maps each threat to what it compromises and who is affected (Fig. 2), and draws the attack flow (Fig. 3). Every A-, C- and TB-id is our assignment onto RPT-0014's preliminary vocabularies (`report.md` §1, §4), which are themselves AI-generated hypotheses. See the two lists below the table. The rating is core for indirect prompt injection only |

**Evidence for each linked AIT:**
- AIT-064: the core contribution (§3, §4).
- AIT-067: invisible page text (p. 4), HTML comments (p. 6), a Markdown comment inside a Wikipedia page (p. 11), Base64 encoding (p. 11).
- AIT-068: a visual injection on LLaVA, with limited success (§5.3, Fig. 28).
- AIT-071 and AIT-102: an injection stored in memory re-infects the model when a later session reads that memory (p. 8, Fig. 8, Output 3).
- AIT-073: jailbreak prompts delivered indirectly evade Bing Chat's filter (p. 6 fn. 5; Prompt 9 adapts the AIM jailbreak).
- AIT-091: the synthetic assistant sends email to every contact, and fetches commands from an attacker server, using the user's tools (pp. 7–8).
- AIT-108: an email worm (p. 7, Prompt 7, Output 1).
- AIT-112: injected time-consuming background tasks make Bing Chat time out (p. 10, Prompt 14).

**What the paper itself identifies** (checked against the rendered figures on p. 3 and the text):
- *Fig. 2, threats and what they hit:*
  - information gathering: personal data, credentials, chat leakage;
  - fraud: phishing, scams, masquerading;
  - intrusion: persistence, remote control, API calls;
  - malware: spreading injections (prompts as worms), spreading malware;
  - manipulated content: wrong summary, disinformation, propaganda or bias, data hiding, ads or promotion;
  - availability: DoS, increased computation.
- *Fig. 2, affected parties:* end users, developers, automated systems, and the LLM itself (availability).
- *Fig. 3, actors and flows:*
  - Parties: an attacker; external sources (drawn as web, document, email and file icons); the LLM-integrated application; a user; APIs and tools.
  - Flows: ① plant prompts in the sources; ② the user prompts the app; ③ the app retrieves; ④ the app calls APIs; ⑤ the APIs communicate back to the attacker; ⑥ the app influences the user.
  - A dashed outline encloses the user, the application and the APIs. The figure does not label it. The text says only that attackers can cross security boundaries, without naming them (p. 3).
- *Other figures:* memory as the persistence channel (Fig. 8, p. 8); a public code repository and the developer's code-completion context (Fig. 9, p. 8); the Edge sidebar reading the open page (§4.1.2, p. 6).

**Our assignment onto RPT-0014's preliminary ids.** None of these ids appears in the paper; this is our interpretation.
- *Assets:*
  - A07: personal data and chat leakage (Fig. 2), plus the emails and contacts read in the worm demonstration;
  - A09: credentials (Fig. 2);
  - A03: manipulated content (Fig. 2);
  - A11: availability (Fig. 2);
  - A06: memory (Fig. 8);
  - A08: code suggestions (Fig. 9).
- *Components:*
  - C01: external sources (Fig. 3);
  - C06: search retrieval;
  - C07: the LLM-integrated application, Bing Chat;
  - C08: the synthetic tool-using assistant;
  - C09: APIs and tools (Fig. 3);
  - C10: memory;
  - C12: the user (Fig. 3);
  - C14: the developer's IDE context;
  - C20: the Edge sidebar.
- *Trust boundaries:*
  - TB2: flows ① and ③, external content into the context;
  - TB7: flow ④, model to tools;
  - TB9: flow ⑤, egress to the attacker;
  - TB13: agent to memory (Fig. 8).
  - The paper names none of these boundaries. TB2, TB7 and TB9 are our reading of the arrows that cross Fig. 3's unlabeled dashed outline.

**AIT entries not linked** (techniques the text mentions or resembles but does not demonstrate):
- AIT-063 and AIT-083: direct injection and system-prompt leakage appear only as prior work [67].
- AIT-066: exfiltration through links needs the user to click (pp. 6–7); nothing is fetched automatically on render.
- AIT-069: payloads contain chat-template and end-of-text tokens (pp. 28, 31), but the paper does not show they are parsed as control tokens.
- AIT-086 and AIT-088: answer manipulation and source blocking work by injected instructions, not by poisoning or jamming a corpus (pp. 9–10).
- AIT-087 and AIT-090: SEO and flooding the web are mentioned (pp. 4, 10, 12) but not demonstrated.
- AIT-092 and AIT-095: Copilot context contamination is neither code execution nor rules-file loading (p. 8).
- AIT-104: the Edge sidebar reads the page but takes no actions.
- AIT-111: overlaps AIT-112; no agent loop or billing is shown.
- AIT-126 and AIT-129: fraud and disinformation are delivered *through* a compromised assistant, not generated by an attacker's own AI.

## Implementations

Searched 2026-11-01, limited to the paper's own artifacts. The paper evaluates no defences, so there is nothing defensive to build on.

| Name | Kind | License | URL |
|---|---|---|---|
| greshake/llm-security | The paper's demonstration code: synthetic applications and prompts | MIT (GitHub API, 2026-11-01) | https://github.com/greshake/llm-security |

The paper names the repository as `llm-security` (p. 2) and as `lm-safety` (p. 12). The GitHub API shows both resolve to the same repository (id 603706708), created 2023-02-19 and last pushed 2025-07-17. We have not run it.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | Metadata. `cites` is a **calibration subset** of 17 of the 82 references in arXiv v2; it is not the full list. Complete reference expansion and stub creation are reserved for subset-1 (LANES.md, Step 2, item 5). No stub records were created |
| `summary.md` | This document |

## Limits

- **The version of record was not read.** The ACM AISec '23 PDF was not accessible. Crossref lists 72 deposited references for it against 82 in arXiv v2, so the two texts may differ; this is not verified. arXiv v1 had a different title ("More than you've asked for: A Comprehensive Analysis of Novel Prompt Injection Threats to Application-Integrated Large Language Models"), so citations of arXiv 2302.12173 may use either title.
- **Evidence is qualitative.**
  - No success rates are reported (§5.2), and the screenshots (Figs. 13–28) are single sessions.
  - The authors say prompts often worked on the first attempt, but this is not measured.
  - This record reviewed the figures by their captions and the prompt text; the screenshot images were not examined in detail.
- **Real-world reach is narrower than the title suggests.**
  - Bing Chat was attacked through local HTML in the Edge sidebar; there were no public, search-indexed injections.
  - The worm, remote-control and persistence attacks were shown only on synthetic applications with mock tools at temperature 0.
  - Microsoft 365 Copilot and ChatGPT plugins were not tested (§5.2).
  - The Copilot injection was highly sensitive to context, and its effect was much reduced inside larger applications (p. 8).
- **Multimodal injection is preliminary.** One LLaVA example; GPT-4's vision model was not tested (§5.3).
- **No defence is evaluated** (§5.6). The systems and models tested are from 2023 and may have changed since.
- **Confirmed source defects.**
  - The demonstration repository is named two ways (p. 2 versus p. 12); both resolve, so nothing is broken.
  - The citation "[68, 68]" on p. 1 repeats the same reference.
  - References [1]–[33] print only "[Link]", so a printed copy loses their targets; the URLs exist only as PDF hyperlinks.
- **Preliminary RPT-0014 statements checked against the source.**
  - Confirmed: the AISec 2023 venue, which `sources.md` marked "from memory" (Crossref); the February 2023 date of INC-025 (arXiv v1); the research-demonstration kind (§5.1–5.2).
  - Not checked: the ATLAS, OWASP and CWE ids.
