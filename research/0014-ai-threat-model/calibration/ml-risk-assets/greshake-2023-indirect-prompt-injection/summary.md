---
schema: "library-summary/v1"
id: greshake-2023-indirect-prompt-injection
record: greshake-2023-indirect-prompt-injection
type: summary
updated: "2026-10-30"
---

# Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

|  |  |
|---|---|
| **Type** | paper (peer-reviewed workshop paper) |
| **Maturity** | _unset: no maturity level applies to a research paper_ |
| **Authors** | K. Greshake (Saarland University; sequire technology GmbH), S. Abdelnabi (CISPA), S. Mishra (Saarland University), C. Endres (sequire technology GmbH), T. Holz (CISPA), M. Fritz (CISPA). Greshake and Abdelnabi contributed equally. |
| **Published** | 2023-11-26 (ACM version of record, online). Venue: AISec '23, Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security, co-located with ACM CCS '23, Copenhagen, pp. 79–90. Corrected VoR 2024-01-10. Preprint arXiv v1 2023-02-23, v2 2023-05-05. |
| **Identifier** | doi:10.1145/3605764.3623985 · arXiv:2302.12173 |
| **Source** | https://arxiv.org/pdf/2302.12173v2 (33 pp.: 13 pp. body, then appendix prompts and screenshots) |
| **Digest** | `428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81` (arXiv v2, retrieved 2026-10-30; equals `pdf-manifest.tsv`) |

## Source check (2026-10-30)

- **Venue.** Verified through Crossref: doi:10.1145/3605764.3623985 has the same six authors
  and title, in the AISec '23 proceedings, pp. 79–90. The arXiv record carries no journal
  reference or DOI, and the v2 PDF does not name a venue.
- **Version read.** arXiv v2, the same bytes as the unversioned arXiv URL in
  `pdf-manifest.tsv`. ACM's PDF returned HTTP 403 to automated retrieval, so the version of
  record was **not** compared with v2.
- **Corrected version of record.** ACM's article page (Editorial Notes, read 2026-10-30)
  reports that, at the authors' request, a Corrected VoR with minor, non-substantive changes
  was published on 2024-01-10. The original VoR is kept under Supplemental Material. Crossref
  and Crossmark list no update for the DOI. Neither the original nor the Corrected VoR was
  compared with arXiv v2.
- **Title change.** v1 (2023-02-23) was titled "More than you've asked for: A Comprehensive
  Analysis of Novel Prompt Injection Threats to Application-Integrated Large Language
  Models". The library record `spotlighting-indirect-prompt-injection` cites this paper
  under that v1 title.
- **Two repository URLs.** The paper names `github.com/greshake/llm-security` (footnote 1)
  and `github.com/greshake/lm-safety` (footnote 11). Both resolve to the same repository.

## Overview

The paper argues that once an LLM is integrated into an application that retrieves content
or calls tools, the line between **data and instructions** disappears. An attacker who never
talks to the model can plant instructions in content the application will later read: web
pages, emails, documents or code. When those instructions are retrieved, they steer the
model much as arbitrary code would (§1, §3).

It names this **indirect prompt injection** and organizes it as a threat taxonomy adapted
from cyber-threat taxonomies (§3, Fig. 2), with three dimensions:

- **Injection methods:** passive (by retrieval), active (for example emails), user-driven,
  and hidden (multi-stage, encoded, multimodal).
- **Threats:** information gathering, fraud, intrusion (remote control, persistence, code
  completion), malware (including self-spreading prompts that act as worms), manipulated content,
  and availability.
- **Affected parties:** end users, developers, automated systems, and the LLM itself.

It then demonstrates instances of each threat qualitatively. Targets are synthetic GPT-4 and
text-davinci-003 applications with mocked tools (search, view page, fetch URL, email,
address book, key-value memory), Bing Chat through the Edge sidebar reading local HTML, and
GitHub Copilot (§4).

Its conclusion is that input filtering on the chat channel does not cover ingested content,
that RLHF-style defenses fix individual jailbreaks one at a time, and that no foolproof mitigation is in sight
(§5.6).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | It is the primary source for an attack class on LLM-integrated applications, with end-to-end demonstrations. |
| Cryptography | none | No cryptographic content. Encrypting a payload is mentioned only as a way to hide injections (§3.1), with no scheme. |
| This project | core | **RPT-0014's preliminary artifacts** (AI-generated, review status `hypothesis`) already rely on it. It is a source of AIT-064, the primary source of INC-025, and the citation for `report.md` Summary finding 1, that the "one genuinely new root cause" is instructions and data on one channel (CWE-1427). |

Bears on **R-020** (map a generic threat onto a product). The paper's preconditions decide
whether IPI applies to a product: attacker-reachable content enters the context window, and
the model can call tools or affect the user. This is this pass's reading; the paper does not
reference tmodel. It informs no open DEC directly.

## RPT-0014 applicability

**How to read the linked ids.** Three kinds of statement are kept apart:

- **Paper:** stated or demonstrated in the source.
- **RPT-0014:** a mapping already present in RPT-0014's preliminary artifacts
  (`sources.md`, `attack-catalog.yaml`, `incidents.md`, `report.md`), which are AI-generated
  hypotheses.
- **This pass:** this calibration's own reading, also a hypothesis.

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | **RPT-0014:** AIT-064, INC-025 (ATLAS case study AML.CS0020). **This pass:** AIT-066, AIT-067, AIT-068, AIT-102, AIT-108, AIT-111 | **Paper:** it introduces and demonstrates the class (§4.2–§4.3). **RPT-0014:** S-0166 is in the `sources` of AIT-064 only, and is the primary source of INC-025. **This pass:** the paper also demonstrates instances of six more catalog techniques that do not cite it: markdown-link exfiltration (§4.2.1 → AIT-066), injections hidden in HTML or Markdown comments and Base64 (§4.1.2, §4.3 → AIT-067), image injection on LLaVA (§5.3, Fig. 28 → AIT-068), memory persistence (§4.2.4 → AIT-102), an email worm (§4.2.3 → AIT-108), and time-consuming background tasks (§4.2.6 → AIT-111). |
| Existing AI threat models | adjacent | none in `threat-models.md` | **Paper:** Fig. 2 is a threat taxonomy, with injection method × threat × affected party, for one attack class. **This pass:** it is not a system threat model and has no TM- id. It could be a candidate for `threat-models.md`, but that is the integration lane's call. |
| Weakness enumerations | adjacent | **RPT-0014:** CWE-1427, AML.T0051.001, LLM01:2025, ASI01, NISTAML.015 (the `sources.md` row for S-0166) | **Paper:** it names no CWE or catalog id, since it predates most of them. It states the root cause: data and instructions are not separated (§4.2). **RPT-0014:** maps it to the ids listed. **This pass:** NIST AI 100-2e2025 cites it [146] throughout §3.4, the indirect prompt injection section that defines NISTAML.015, .016 and .017. |
| Attack → asset mapping | core | **RPT-0014 (AIT-064):** A07, A08, A09, A12, A14; C06, C07, C08, C09. **This pass:** A03, A06, A07, A08, A09, A11, A13; C01, C06, C07, C08, C09, C10, C12, C14, C20 | **Paper:** it shows *paths* across components, not just a target. Fig. 3 shows the injection planted, retrieved, then acting through APIs back to the attacker or to the user. It names what is reached: personal data and chat (§4.2.1), credentials (§4.2.2), persistent memory (§4.2.4), code suggestions (§4.2.4), search results and summaries (§4.2.5), and availability (§4.2.6). **This pass:** places those on A- and C- ids. The demonstrations reach C10 (memory), C14 (Copilot in the developer environment), C20 (the Edge sidebar) and C12 (persuaded users), but AIT-064's components stop at C06–C09. |

## Implementations

| Name | Kind | License | URL |
|---|---|---|---|
| greshake/llm-security | the paper's demonstration code and prompts | MIT | https://github.com/greshake/llm-security |

Searched 2026-10-30. The paper proposes no defense to build on. It names candidate defenses
in §5.6: filtering retrieved inputs, an LLM supervisor, and interpretability-based outlier
detection. Defenses that came later belong in their own records, for example the library's
`spotlighting-indirect-prompt-injection`.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: bibliographic fields, version, digest, partial `cites`, `cited_by`, `bears_on`, applicability, tags |
| `summary.md` | this summary, with the RPT-0014 applicability table |

The PDF is not committed. It is fetched by its digest through `pdf-manifest.tsv`.

## Limits

- **Qualitative only.** The paper reports no success rates. The authors say quantifying
  success in interactive sessions is left for future work (§5.2). Its evidence is
  demonstrations at temperature 0 on synthetic applications, plus black-box sessions on Bing
  Chat that cannot be exactly reproduced (§5.4).
- **No public injection.** On ethical grounds, nothing was planted in retrievable public
  sources. Bing Chat was tested through local HTML in the Edge sidebar, and the multi-stage
  attack only on the synthetic app (§4.3.1, §5.1). In-the-wild feasibility is argued from
  anecdote, not shown.
- **Code completion is weak evidence.** The authors say the Copilot injection was very
  sensitive to context and was much less effective in larger projects. They call for more
  research on real-world feasibility (§4.2.4).
- **2023 systems.** The tested systems are 2023 versions of Bing Chat, GitHub Copilot,
  text-davinci-003 and GPT-4. Whether the results hold for today's versions was not checked
  in this pass. The paper could not test Microsoft 365 Copilot or plugins (§5.2). Multimodal
  results come from smaller open models, not GPT-4 (§5.3).
- **Mitigations are named, not evaluated** (§5.6).
- **Notes for the integration lane, not edits.**
  - `sources.md` marks the venue "from memory". Crossref confirms AISec '23 with
    doi:10.1145/3605764.3623985.
  - The `sources.md` row writes `ASI01` with no year suffix, while `attack-catalog.yaml`
    uses `ASI01:2026`.
  - AIT-064's components omit C10, C14 and C20, which the paper's demonstrations reach.
  - There is no catalog technique specific to code-completion context injection.
- **What this pass read and did not read.** It read the whole body, pp. 1–13, including
  the references. The appendix (Prompts 1–20, Outputs 1–4, Figures 13–28) was read in part:
  Prompts 1–3, and the prompts quoted in the body. Neither ACM version of record (2023-11-26,
  or the Corrected VoR of 2024-01-10) was read.
