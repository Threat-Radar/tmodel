---
schema: "library-summary/v1"
id: nist-ai-100-2-e2025
record: nist-ai-100-2-e2025
type: summary
updated: "2026-11-10"
lane: catalogs-schema
reviewed_by: ""
---

# Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (NIST AI 100-2 E2025)

|  |  |
|---|---|
| **Type** | spec (NIST Trustworthy and Responsible AI report) |
| **Maturity** | _unset: a NIST AI report, not a standard; standing not checked further_ |
| **Authors** | Apostol Vassilev, Alina Oprea, Alie Fordyce, Hyrum Anderson, Xander Davies, Maia Hamin |
| **Published** | March 2025 |
| **Identifier** | DOI 10.6028/NIST.AI.100-2e2025 |
| **Source** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf (127 pages) |
| **Digest** | `4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646` (matches `pdf-manifest.tsv`) |

## Overview

The report sets out a shared vocabulary and a taxonomy for adversarial machine learning (AML), meaning attacks that exploit the statistical, data-driven nature of ML rather than the platform it runs on. Traditional cyber attacks on that platform are explicitly left to existing cybersecurity taxonomies (§1). It splits AI into predictive (PredAI, §2) and generative (GenAI, §3) systems. It classifies each attack by five things: the system type, the life-cycle stage where it is mounted, the attacker's objective (availability, integrity, privacy, plus misuse for GenAI), the attacker's capabilities, and the attacker's knowledge (Executive Summary).

Each attack class gets a stable id in a two-level scheme.
- **Objectives** are `NISTAML.01` to `.05`.
- **Leaf attacks** under them run from `NISTAML.011` to `.051`, 25 in all. Examples: `.015` indirect prompt injection, `.018` prompt injection, `.031` model extraction, `.039` compromising connected resources.
- **The index is incomplete.** The taxonomy index on pp. x–xi lists 23 leaves. `.016` (availability attacks through indirect prompt injection) and `.017` (time-consuming background tasks) are defined only in §3.4.1 (p. 51).

Each class comes with its mitigations and their limits.

The central claim is sobering: AML defences are mostly empirical, with no information-theoretic guarantees, and published impossibility results bound what alignment and detection can achieve (§1, §4.2.5). So mitigations should be expected to fail against new attacks, and the report deliberately leaves risk tolerance to the reader.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | A government consensus taxonomy of attacks on ML and GenAI systems, with an id for every class. |
| Cryptography | adjacent | Names cryptographic techniques as mitigations three times, without analysing them: secure computation for training-data confidentiality (§2.1.2, p. 7), published hashes so downloaders can verify training data (§3.2.3, p. 43), and cryptographic attestation of origin and integrity (§4.2.1, p. 58). It also uses cryptography as a contrast, for the provable guarantees that AML lacks (§1). |
| This project | adjacent | Bears on **DEC-001a**: its ids are a ready external catalog for `AttackPattern`/`Weakness` mappings, beside CWE and ATLAS. Also bears on **DEC-009**, since its attack classes are the generic threats RPT-0014 maps onto products. It is not a threat-modelling method, and it does not cover tmodel's own platform risks. |

## Implementations

Searched 2026-11-08 and re-checked 2026-11-10 (GitHub, for maintained open-source tools that implement attacks or tests in this taxonomy's classes):

| Name | Kind | License | URL |
|---|---|---|---|
| Adversarial Robustness Toolbox (ART) | PredAI evasion, poisoning, extraction and inference attacks plus defences (library) | MIT | https://github.com/Trusted-AI/adversarial-robustness-toolbox |
| garak | LLM probe and scanner: prompt injection, jailbreak, leakage | Apache-2.0 | https://github.com/NVIDIA/garak |
| PyRIT | GenAI red-teaming toolkit: automated scans and multi-turn attacks | MIT | https://github.com/microsoft/PyRIT |

The report ships no code. §3.6 (p. 54) names two open-source tools, "Garak [106] and PyRIT [364]", beside its benchmarks (JailbreakBench, HarmBench, AgentDojo and others).

The report's [364] points at `Azure/PyRIT`, which is archived with a notice that PyRIT has moved to `microsoft/PyRIT`, an active repository. Microsoft's Counterfit (`Azure/counterfit`) is archived with no successor, so it is not listed.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: identifiers, digest, applicability, tags |
| `summary.md` | this summary, with the RPT-0014 applicability table |

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | 98 of the 146 AIT entries, via `catalog_ids.nist_ai_100_2`: 60 up to AIT-075 and 38 after it (highest AIT-137) | It classifies and cites the published attacks (449 references) but reports none of its own, so it is the index, not the evidence. |
| Existing AI threat models | core | TM-004 | It *is* TM-004: an attacker model on five axes (system type, stage, objective, capability, knowledge). It has no system decomposition of its own beyond the GenAI reference architectures in Figs. 4–6. |
| Weakness enumerations | core | NISTAML.01–.05; NISTAML.011–.018, .021–.027, .031–.039, .051 (25 leaves) | The id scheme RPT-0014 uses on 98 of its 146 attack-catalog entries. The other 48 have an empty list and a scope note: 32 are conventional cyber, platform or misuse attacks, 9 are non-adversarial, insider or provider failures, and 7 are agent attacks (§3.5 has no id). The ids are attack classes, not weaknesses. Some leaves sit under more than one objective (`.012`, `.013`, `.015`, `.018`, `.023`), so an id alone does not tell you which property was violated. `.016` and `.017` (§3.4.1) are missing from the index; the catalog uses them on AIT-088 and AIT-111. |
| Attack → asset mapping | adjacent | A01, A02, A03, A05, A07; C01, C02, C03, C04, C05, C06, C07 | Attacks are mapped to life-cycle stage and to violated property, not to assets. The asset link has to be inferred from the capability: training-data control → A01, query access → A02 and A07, resource control → A05. |

## Reference expansion

Not completed in this calibration pass. The report has 449 references, and a proper diff against `sources.md` needs a scripted title match, not spot checks. Spot checks: Greshake et al. ([146]) is S-0166, and PoisonedRAG ([449]) is S-0493, so both are already in `sources.md`. [146] is also the only source §3.4.1 cites for `.016` and `.017`.

## Limits

- **Taxonomy, not threat model.** It says what attacks exist and what they violate, not which apply to a given system or how likely they are. §4.2.5 says outright that it leaves risk-management decisions aside.
- **Adversarial ML only.** Platform and infrastructure attacks (exposed model stores, compromised MLOps tooling, credential theft from AI gateways) are out of scope by design (§1), yet many RPT-0014 entries are of exactly that kind. An entry with a NISTAML id covers only its ML part.
- **The id hierarchy is not a tree.** The same leaf id appears under several objectives, so tools that treat `NISTAML.0xy` as having a single parent `NISTAML.0x` will mis-file it.
- **Agents get one page** (§3.5): the report calls agent security research "still in its early stages" and folds agent risks into direct and indirect prompt injection. No agent-specific classes (tool misuse, memory poisoning, delegation) get ids.
- **The index is not the id list.** Two leaf ids (`.016`, `.017`) appear only in the body (§3.4.1), so a tool that harvests ids from the index will miss them.
- **Read in part.** This summary rests on these parts of the report:
  - the table of contents, the Executive Summary, §1 and the taxonomy index;
  - §§3.4.1, 3.5, 3.6 and 4.2.5;
  - the passages on cryptographic mitigations (§§2.1.2, 3.2.3, 4.2.1), checked after review.

  It is not a full read of §§2–3, which is why `confidence: medium`. A text search of the whole report for `NISTAML` ids found the two the index lacks.
