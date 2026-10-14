---
schema: "library-summary/v1"
id: nist-ai-100-2-e2025
record: nist-ai-100-2-e2025
type: summary
updated: "2026-10-11"
---

# Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations

|  |  |
|---|---|
| **Type** | spec (NIST Trustworthy and Responsible AI report, 127 pp.) |
| **Maturity** | _unset — do not guess_ |
| **Authors** | A. Vassilev, A. Oprea, A. Fordyce, H. Anderson, X. Davies, M. Hamin |
| **Published** | March 2025 (approved 2025-03-20), NIST |
| **Identifier** | NIST AI 100-2e2025; DOI 10.6028/NIST.AI.100-2e2025 |
| **Source** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf |
| **Digest** | `4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646` (matches `pdf-manifest.tsv`) |

## Overview

NIST's taxonomy and glossary for adversarial machine learning (AML), meant as a
common language for other standards and practice guides. It splits the field into
**predictive AI** (§2) and **generative AI** (§3). Attacks are classified along the
attacker's **objective** — availability breakdown, integrity violation, privacy
compromise, and (for GenAI) **misuse enablement** — and along the attacker's
**capabilities**, **knowledge** and the **life-cycle stage** attacked (training vs
deployment). Predictive-AI attack classes are evasion, poisoning and privacy;
GenAI adds supply-chain attacks, direct prompting (jailbreaks, prompt extraction),
**indirect prompt injection**, and a short section on the **security of agents**,
noting that tool use turns prompt injection into code execution and data
exfiltration. Each class is paired with mitigations and their limits, and every
class carries a stable **`NISTAML.*` identifier** (29 distinct ids in this edition,
e.g. NISTAML.01 availability, NISTAML.02 integrity, NISTAML.03 privacy, NISTAML.04
misuse). It closes on open challenges: trade-offs between trustworthiness
attributes, theoretical limits on robustness, and evaluation.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | The reference taxonomy for attacks on ML and GenAI systems. |
| Cryptography | none | Not about cryptography. |
| This project | core | Gives tmodel a normalizing vocabulary and id space (`NISTAML.*`) for AI attack and weakness records (RPT-0014, #74). |

Bears on **DEC-001** (object model — how AI attacks and weaknesses are typed) and
**R-010** (mapping weaknesses to external catalogs).

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | core | AIT-001–AIT-010 (evasion), AIT-011+ (poisoning), AIT-046–AIT-053 (privacy, extraction), AIT-063, AIT-064 (prompt injection), AIT-073, AIT-074 (jailbreaks) | Catalogs the attack classes, with the literature behind each |
| Existing AI threat models | core | TM-004 | Its objective × capability × knowledge axes are an attacker model |
| Weakness enumerations | core | NISTAML.01–NISTAML.051 (29 ids); ATLAS cited as a knowledge base | Is itself an enumeration; no CWE mapping in this edition |
| Attack → asset mapping | adjacent | C01, C02, C03, C04, C05, C06, C08 | Attacks are tied to life-cycle stages and model/data assets, not to a component architecture |

## Implementations

Not software. Its ids are used by catalogs that cross-map to it (e.g. RPT-0014's
`attack-catalog.yaml` and `sources.md` columns). Searched 2026-10-11.

| Name | Kind | License | URL |
|---|---|---|---|

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this summary |

## Limits

- **A taxonomy, not a threat-modeling method.** It does not say how to analyse a
  given system or rate risk in an environment.
- **Agents get one paragraph** (§3.5); agentic and MCP-specific attacks are mostly
  out of scope for this edition.
- **No CWE linkage**, so it does not by itself give weakness ids for tmodel's
  Weakness nodes.
- **Edition-bound.** Ids and classes may change in later editions; records should
  cite `E2025` explicitly.
