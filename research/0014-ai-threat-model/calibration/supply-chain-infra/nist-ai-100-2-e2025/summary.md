---
schema: "library-summary/v1"
id: nist-ai-100-2-e2025
record: nist-ai-100-2-e2025
type: summary
updated: "2026-10-29"
---

# Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations

|  |  |
|---|---|
| **Type** | spec (NIST Trustworthy and Responsible AI report) |
| **Maturity** | _unset_ (a NIST AI series report, not an SP; the report calls its guidance voluntary) |
| **Authors** | Apostol Vassilev (NIST), Alina Oprea (Northeastern University), Alie Fordyce and Hyrum Anderson (Cisco), Xander Davies (U.K. AI Security Institute), Maia Hamin (U.S. AI Safety Institute) |
| **Published** | March 2025. CSRC lists the final as 2025-03-24 and a corrected PDF (author affiliations, figure alt text) as 2025-04-01 |
| **Identifier** | NIST AI 100-2e2025; DOI 10.6028/NIST.AI.100-2e2025 |
| **Source** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf |
| **Digest** | `sha256:4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646` (127 pages; PDF modified 2025-04-01, the date of the corrected upload) |

## Overview

The report sets a common vocabulary for attacks on machine learning, with one taxonomy for
predictive AI (PredAI) and one for generative AI (GenAI) (§2, §3). It places each attack
class by the property the attacker violates (availability, integrity, privacy, and for
GenAI also misuse enablement), the capabilities the attacker needs (six for PredAI, such
as training data, model and query control; four for GenAI, including resource control over
documents and pages the model ingests), the attacker's knowledge (white, gray or black
box) and the learning stage (training or deployment) (§2.1, §3.1). Classes carry stable
identifiers, indexed on pages x-xi: NISTAML.01 to NISTAML.05 for five top-level categories
(the four goals plus supply chain attacks) and 25 leaf ids. The GenAI part covers supply
chain attacks, direct prompting, indirect prompt injection and agents (§3.2 to §3.5).
For each class it lists mitigations and their limits,
and it argues that AML defenses are mostly empirical, without the provable guarantees that
cryptography offers, so they may fail against new attacks (§1, §4.1).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | The reference US government vocabulary for attacks on ML and GenAI |
| Cryptography | `adjacent` | Recommends published cryptographic hashes for web-scale training downloads (§3.2.3) and cryptographic origin and integrity attestation for training data (§4.2.1); specifies neither |
| This project | `adjacent` | Its capability and knowledge axes are part of the evidence for RPT-0014's proposed attacker-precondition fields on AttackStep (report §7) |

`bears_on: DEC-001a` (the core type system, accepted in ADR-0010), through those
AttackStep preconditions. It does not bear on DEC-008: it mentions neither CWE nor CVE.

## Implementations

Searched on 2026-10-29. The taxonomy itself has no machine-readable release: CSRC offers
the PDF and an errata PDF only. §3.6 names test tools for the attack classes:

| Name | Kind | License | URL |
|---|---|---|---|
| garak | LLM vulnerability scanner (cited as github.com/leondz/garak) | Apache-2.0 | https://github.com/NVIDIA/garak |
| PyRIT | risk identification tool for GenAI (the cited github.com/Azure/PyRIT is archived) | MIT | https://github.com/microsoft/PyRIT |
| AgentDojo | prompt injection benchmark for agents | MIT | https://github.com/ethz-spylab/agentdojo |

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this document |

## Limits

- **Attacks on models and data only.** Attacks on the platforms that host AI are left to
  traditional cybersecurity taxonomies (§1), and failures without an adversary are out of
  scope (executive summary). In the supply chain this leaves data and model poisoning:
  NISTAML.05 has one leaf, NISTAML.051 model poisoning (§3.2.2). Executable model files,
  malicious packages, hub typosquatting and MLOps platform exploits get no id, and the
  word "pickle" does not appear. In RPT-0014's attack-catalog.yaml, 12 of the 19
  supply-chain (X03) techniques and 3 of the 4 infrastructure (X07) techniques carry no
  NISTAML id.
- **Agents get two paragraphs and no id** (§3.5).
- **The id index has a known error.** NIST's errata, last updated 2025-06-03, says the
  GenAI availability entries on page x should be NISTAML.016 and .017 instead of .013,
  .015 and .018. NIST calls these corrections proposed, not official. The body text
  (§3.4.1) already uses .016 and .017.
- **An id does not fix the goal, and a name does not fix the id.** Some leaves sit under
  more than one goal (NISTAML.012 under availability and integrity in the PredAI index).
  "Model poisoning" is NISTAML.011, .026 or .051 depending on where it sits.
- **No crosswalk.** It cites MITRE ATLAS as a knowledge base and four ATLAS mitigations
  (AML.M0000, M0001, M0002, M0004), but maps no NISTAML id to ATLAS techniques, CWE or
  OWASP. CWE and OWASP are not mentioned.
- **Two references resolve to the wrong paper.** By DOI, reference [267] (the National
  Security Commission on AI final report) points to "Sponge Examples" (arXiv:2006.03463),
  and [410] (SecGPT, arXiv:2403.04960) points to reference [408]'s paper
  (arXiv:2402.18649). Checked against arXiv on 2026-10-29.
- **No risk guidance.** It leaves risk tolerance and deployment decisions to organizations
  (executive summary, §4.2.5).

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | AIT-013, AIT-016, AIT-017, AIT-018, AIT-019, AIT-020, AIT-021, AIT-032 | A taxonomy over 449 references, not an attack report: no AIT entry cites it as a source, while 98 of the 146 entries in attack-catalog.yaml carry a NISTAML id (RPT-0014's mapping). Linked here are the attacks its supply-chain discussion describes, this lane's focus: domain purchase in web-scale datasets (AIT-013, §3.2.1), instruction-tuning and RLHF poisoning (AIT-017, AIT-018, §3.2.1), poisoned code suggestion (AIT-020, §3.2.1), backdoors that survive safety training (AIT-019, §3.2.2), undetectable backdoors (AIT-016, §4.2.2), artist poisoning tools for image models (AIT-021, §4.2.1) and harmful quantized models (AIT-032, §4.2.4) |
| Existing AI threat models | core | TM-004 | It is TM-004. It contributes attacker axes (goal, capability, knowledge, stage) rather than a system decomposition |
| Weakness enumerations | core | NISTAML.01 to NISTAML.05; leaves NISTAML.011 to .018, .021 to .027, .031 to .039, .051 | One of the enumerations RPT-0014 §6 surveys: 30 stable ids, 5 top-level categories and 25 leaves. It classifies attacks, not weaknesses, and links to no other catalog. The errata and the ids shared across goals (Limits) matter to anyone storing its ids |
| Attack → asset mapping | adjacent | C01, C03, C04, C05, C06, C07, C08, C09, C13 | It classifies by property violated and capability, not by asset. Its GenAI figures name the parts an attack touches: external data sources, the LLM, orchestration and external applications (Figure 5) and the RAG store (Figure 6). Our mapping: scraped training data (C01, C03), third-party models and fine-tuning APIs (C04, C13), query access to the served model (C05), retrieval (C06), system prompt and output handling (C07), agents (C08) and tools (C09) |
