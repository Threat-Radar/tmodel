---
schema: "library-summary/v1"
id: nist-ai-100-2-e2025
record: nist-ai-100-2-e2025
type: summary
updated: "2026-11-01"
---

# Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (NIST AI 100-2e2025)

|  |  |
|---|---|
| **Type** | spec (a NIST Trustworthy and Responsible AI report; filed with the library's other NIST technical-series records) |
| **Maturity** | _unset_. Neither the PDF nor the CSRC publication page assigns a standing on the RFC 2026 scale. The report describes itself as voluntary guidance that is not a regulation (p. viii) |
| **Authors** | Apostol Vassilev (NIST), Alina Oprea (Northeastern University), Alie Fordyce and Hyrum Anderson (Cisco), Xander Davies (U.K. AI Security Institute), Maia Hamin (U.S. AI Safety Institute) |
| **Published** | March 2025. Final released 2025-03-24 (CSRC document history); approved by the NIST Editorial Review Board 2025-03-20 (unnumbered PDF p. 3); corrected PDF uploaded 2025-04-01 (CSRC) |
| **Identifier** | NIST AI 100-2e2025; doi:10.6028/NIST.AI.100-2e2025 |
| **Source** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf (via the DOI); details at https://csrc.nist.gov/pubs/ai/100/2/e2025/final |
| **Digest** | `sha256:4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646` (1,964,469 bytes, 127 pages, retrieved 2026-11-01; matches `pdf-manifest.tsv`; PDF ModDate 2025-04-01, so this is the corrected upload) |
| **Errata** | "Potential updates" PDF, last updated 2025-06-03 (CSRC). It corrects the GenAI availability entries of the index on p. x. NIST states these are not official changes |

Page numbers below are the printed page labels. For body pages, the PDF page is the label plus 13.

## Overview

The report sets out a common vocabulary for attacks on machine learning (pp. xii, 2). It splits systems into predictive AI (§2) and generative AI (§3).

**How attacks are classified** (§2.1, §3.1):
- by learning stage and by attacker knowledge;
- by attacker objective: availability, integrity, privacy, plus misuse enablement for GenAI;
- by attacker capability: control of training data, the model, testing data, labels, source code, query access and, for GenAI, external resources.

**Capabilities decide applicability.** Each attack class is tied to the capabilities it needs (Figs. 1–2). The report says that how a model is released and the application it is built into determine which capabilities an attacker has, and therefore which attacks are possible (p. 37).

**Mitigations are weak.** Mitigations are paired with each class. Most are empirical, carry no information-theoretic guarantee, and are repeatedly broken by adaptive attacks (p. 2, §2.2.5, §4.1.2, §4.2.5).

**Design advice for GenAI.** GenAI applications are vulnerable because data and instructions share one channel, which the report compares to SQL injection (p. 38). It recommends designing systems on the assumption that the model can be made to misbehave (pp. 43, 49–50, 53–54).

**Ids.** It assigns 30 `NISTAML` ids to attack classes (pp. x–xi).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | The whole document is a taxonomy of attacks on ML systems and their mitigations |
| Cryptography | `adjacent` | Incidental only: hash-verified dataset downloads (§3.2.3, p. 43), cryptographic origin and integrity attestation (§4.2.1, p. 58), secure computation for training confidentiality (§2.1.2, p. 7). It defines no cryptographic mechanism |
| This project | `core` | RPT-0014's attack vocabulary. Its capability axes are the preconditions that decide whether a generic attack class applies to a given AI system |

`bears_on: R-020, DEC-009`. This is our interpretation and covers only part of DEC-009.

- **What supports it.** The report states that release choices (open weights versus a hosted API) decide whether an attacker has model control. It states that an application's integration context adds attack vectors (p. 37). It also states that query access varies with what the API exposes (p. 41).
- **Why R-020.** Read together with the capability-to-attack links in Figs. 1–2, these give conditions for mapping a generic attack class onto a specific product (R-020). The report does not perform such a mapping itself.
- **What it does not cover.** It does not inform mitigation-lifecycle tracking (R-021, the other half of DEC-009). Its mitigation stages (Fig. 7) are the model's development and deployment life cycle, not a product's design life cycle.
- **Why not DEC-008 or R-010.** It says nothing about CWE, CVE or NVD integration.

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-001, AIT-002, AIT-003, AIT-004, AIT-006, AIT-007, AIT-008, AIT-010, AIT-011, AIT-012, AIT-013, AIT-015, AIT-016, AIT-017, AIT-018, AIT-019, AIT-020, AIT-022, AIT-024, AIT-027, AIT-032, AIT-034, AIT-046, AIT-047, AIT-048, AIT-051, AIT-052, AIT-053, AIT-057, AIT-063, AIT-064, AIT-066, AIT-067, AIT-070, AIT-072, AIT-073, AIT-074, AIT-075, AIT-081, AIT-083, AIT-084, AIT-086, AIT-091, AIT-108, AIT-111, AIT-112, AIT-137 | A secondary source: it surveys published attacks (449 references) rather than presenting new ones. Each linked AIT is a technique the text describes (§2.2–§2.4, §3.2–§3.5, §4.2). Real-world evidence is limited to §2.2.4 and §2.3.5. §2.2.4 covers ID.me face verification and a commercial phishing detector; it says the malware-detector cases were researcher demonstrations, not attacks in the wild. §2.3.5 covers Tay, the Gmail spam filter and VirusTotal |
| Existing AI threat models | adjacent | TM-004 | It provides attacker-model axes (objective × capability × knowledge × stage) and reference figures for LLM adoption, RAG and the model life cycle (Figs. 4–7). It has no system decomposition, assets, trust boundaries or risk method, and it leaves risk tolerance and risk decisions aside (p. xii, §4.2.5). It is vocabulary for a threat model, not a threat model of a system |
| Weakness enumerations | adjacent | NISTAML.01–.05; .011–.018, .021–.027, .031–.039, .051 | An attack taxonomy, not a weakness enumeration. Its 30 ids name attacker objectives and attack classes, not product flaws. The one root cause it names, the shared data and instruction channel (p. 38), gets no id. The report never mentions CWE, CAPEC or OWASP (0 occurrences) and cites ATLAS only for case studies (pp. 16, 27). The ids are useful as one more column in a crosswalk, but they are defined only in the PDF index (pp. x–xi; .016 and .017 appear only at p. 51) and have no machine-readable release |
| Attack → asset mapping | adjacent | A01, A02, A03, A04, A05, A07, A11, A12, A15, A16; C01, C02, C03, C04, C05, C06, C07, C08, C09, C13, C16, C17 | The report maps attacks to objectives and capabilities, not to assets. The asset and component ids are **our mapping** (see the note below) |

**Our mapping of capabilities to components:**
- training-data control → C01–C03 / A01;
- model control → C03, C04, C13 / A02, A03;
- query access → C05, C07, C13;
- resource control → C01, C06, C09, and agents C08;
- testing-data control → C05, C16;
- output handling → C17 (p. 39).

**Where each asset appears in the report:**
- training data and model confidentiality (A01, A02): §2.1.2;
- system prompts (A04): p. 38;
- RAG knowledge base (A05): p. 40;
- user data (A07): §3.4.3;
- availability (A11);
- downstream and physical decisions (A12): p. 1;
- identity verification (A15): §2.2.4;
- security classifiers (A16): §2.1.5, §2.2.4.

**AIT entries not linked.** `attack-catalog.yaml` assigns the AIT entries below NISTAML ids at class level, and its header calls those ids candidate edges, not asserted mappings. This record does not say those class-level mappings are wrong. It records only that the report does not *describe* the technique, checked by reading the full text and searching the body:

- **Not described.** None of these techniques appears in the body or glossary:
  - AIT-005: LiDAR appears only as an image modality, p. 9.
  - AIT-009: reinforcement learning and graph networks appear only as learning paradigms or as targets of property inference, pp. 5, 31.
  - AIT-025: energy-latency attacks appear only via query access, not via training, p. 6.
  - AIT-031, AIT-033, AIT-049, AIT-050: no mention at all.
  - AIT-035: "Editing" appears only as a stage label in Fig. 7, p. 47.
  - AIT-061: Rowhammer appears only as a means of model extraction, p. 31.
  - AIT-119: watermarking is discussed only for generated content, not for model IP, p. 50.
- **Mentioned but not described (borderline).** Left unlinked; a reviewer may disagree:
  - AIT-014: the report says pretraining poisoning may need only a small fraction of the dataset [46], which is not the near-constant poison count the AIT describes, p. 42.
  - AIT-021: only a news reference to artists' poisoning tools, p. 57.
  - AIT-026: one mention of insider threat, p. 58.
  - AIT-065: the parts of the chain (email-borne injection, forwarding, URL exfiltration) are described separately, pp. 52–53, and are linked through AIT-064, AIT-066 and AIT-084, but the zero-click copilot chain itself is not.
  - AIT-079: one sentence saying the attacks also apply to multimodal and text-to-image models, p. 38.
  - AIT-088: generic availability attacks through indirect prompt injection, p. 51, with nothing specific to RAG.

## Implementations

The report is a taxonomy, so there is nothing to implement directly. On 2026-11-01 one web search for tooling that implements or exports the NISTAML ids found none. That was a single search, not a survey. The report names these open-source evaluation tools (§2.4.2, §3.6); we have not verified them or checked their licences:

| Name | Kind | License | URL |
|---|---|---|---|
| Garak [106] | LLM vulnerability scanner | not checked | https://github.com/leondz/garak |
| PyRIT [364] | GenAI red-teaming toolkit | not checked | https://github.com/Azure/PyRIT |
| TensorFlow Privacy [350] | membership-inference testing | not checked | https://blog.tensorflow.org/2020/06/introducing-new-privacy-testing-library.html |
| ML Privacy Meter [259] | privacy-risk measurement | not checked | https://arxiv.org/abs/2007.09339 |

The report also names benchmarks: JailbreakBench, AdvBench, HarmBench, StrongREJECT, AgentHarm, Do-Not-Answer, TrustLLM and AgentDojo (§3.6).

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | Metadata. `cites` is a **calibration subset** of 25 of the 449 references, chosen for RPT-0014; it is not the full list. Complete reference expansion and stub creation are reserved for subset-1 (LANES.md, Step 2, item 5). No stub records were created |
| `summary.md` | This document |

## Limits

- **Scope excludes most of the platform.** Attacks on the platforms that host models are left to traditional cybersecurity taxonomies (p. 2), and non-adversarial flaws are excluded (p. xiii). Unsafe model loading, MLOps infrastructure, credentials and plugin code therefore get no NISTAML id. §3.2 covers supply-chain risk only where it exploits ML's statistical nature. Agents (§3.5) get one page and no id.
- **No risk or asset model.** By design (p. xii, §4.2.5). Impact and prioritisation remain ours.
- **Mitigations are largely empirical.** The report itself cites impossibility results for detection, watermarking and alignment (§4.1.2, §3.3.3, §4.2.5).
- **Coverage ends around late 2024.** The arXiv count is dated July 2024 (p. 3). 14 of the roughly 20 dated access stamps are August 2024, ATLAS was retrieved December 2024, and the only 2025 item is a January 2025 NIST blog post [353]. Later agentic and MCP attacks are absent.
- **Edition lineage is not stated in the source.** The text never mentions the 2023 edition (S-0841), so no `supersedes` edge is asserted here.
- **Confirmed errors.** Each is verified against the document, NIST's errata, or the arXiv record the identifier resolves to:
  - *Index, GenAI availability entries* (p. x): wrong. NIST's errata of 2025-06-03 replaces them with .016 and .017.
  - *Wrong identifiers*, each resolving to a different paper (checked against the arXiv API on 2026-11-01):
    - [34] MixMatch (p. 63) carries the DOI of [33], Societal Adaptation.
    - [170] Sleeper Agents (p. 78) carries a DOI for arXiv 2201.07207, Language Models as Zero-Shot Planners.
    - [237] HarmBench (p. 85) carries a DOI for arXiv 2402.15911, PRP.
    - [267] NSCAI final report (p. 88) carries the Sponge Examples DOI, arXiv 2006.03463.
    - [410] SecGPT (p. 102) carries the DOI of [408], arXiv 2402.18649.
    - [449] PoisonedRAG (p. 106) gives URL and DOI for arXiv 2005.11401, the original RAG paper; its own arXiv id, 2402.07867, is correct.
  - *Duplicated entries*: six pairs cite the same work twice with the same title and authors, at pp. 62, 72, 92, 94, 95 and 100: [22]/[23], [121]/[122], [309]/[310], [337]/[338], [342]/[343], [395]/[396].
  - *Misspelling*: "Szedegy" appears five times (pp. 11–12); the reference list spells it Szegedy.
- **Possible discrepancies, not confirmed as errors:**
  - Index label .027 "Misaligned Outputs" (p. xi) heads a body section titled "Integrity Attacks" (§3.4.2, p. 51).
  - Model extraction on GenAI (§3.3.2, Fig. 2) has no GenAI index entry.
  - p. 34 sends misuse enablement to §2.1.2, which does not discuss misuse; §3.1.2 defines it.
- **Design choices that limit the ids:**
  - Jailbreak and fine-tuning circumvention have no id of their own.
  - One leaf id spans several objectives, for example .018 under integrity, privacy and misuse, so a leaf does not identify the objective.
