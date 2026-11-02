---
schema: "library-summary/v1"
id: nist-ai-100-2-e2025
record: nist-ai-100-2-e2025
type: summary
updated: "2026-10-30"
---

# NIST AI 100-2e2025: Adversarial Machine Learning — A Taxonomy and Terminology of Attacks and Mitigations

|  |  |
|---|---|
| **Type** | spec (NIST Trustworthy and Responsible AI report) |
| **Maturity** | informational: p. viii says it is voluntary guidance and sets no standard or legal requirement |
| **Authors** | A. Vassilev (NIST), A. Oprea (Northeastern University), A. Fordyce and H. Anderson (Cisco), X. Davies (U.K. AI Security Institute), M. Hamin (U.S. AI Safety Institute) |
| **Published** | March 2025 (approved by the NIST Editorial Review Board 2025-03-20) |
| **Identifier** | NIST AI 100-2e2025 · doi:10.6028/NIST.AI.100-2e2025 |
| **Source** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf (127 pp., reached through the DOI) |
| **Digest** | `4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646` (retrieved 2026-10-30; equals `pdf-manifest.tsv`) |

## Source check (2026-10-30)

- https://csrc.nist.gov/pubs/ai/100/2/e2025/final lists E2025 (March 2025) as final. NIST
  uploaded a corrected PDF on 2025-04-01, with updated affiliations and figure alt text. The
  digest above is of the PDF served today.
- **Known error in the id index.** NIST's errata note (planning note of 2025-06-03,
  `nist.ai.100-2e2025_potential_updates.pdf`) says the page-x index is wrong. Under GenAI
  Availability Violations (NISTAML.01) it lists .013, .015 and .018, but the correct entries
  are NISTAML.016 (Manipulate Resources) and NISTAML.017 (Time-Consuming Tasks). The body
  text (§3.4.1) already uses .016 and .017. Take the ids from the body, not from the index.
- The prior edition, E2023 (RPT-0014 S-0841), has no library record.

## Overview

The report sets out a common vocabulary for **adversarial machine learning**: attacks that
exploit the statistical, data-based nature of ML. It treats attacks on platforms and
infrastructure as traditional cybersecurity and leaves them out of scope (§1).

It classifies attacks along the same axes for predictive AI (§2) and generative AI (§3):

- the attacker's objective: availability, integrity, privacy, and for GenAI also misuse
  enablement;
- the capability the attacker controls. PredAI has six: training data, model, testing data,
  label limit, source code and query access. GenAI uses training data, query access, model
  control, and adds *resource control*, which is what indirect prompt injection needs;
- the attacker's knowledge: white-, gray- or black-box;
- the learning stage: training time or deployment time.

Each attack class has a stable id. There are 30 in all, five objective classes and 25 leaves,
NISTAML.01 to .05 and NISTAML.011 to .051. For each class the report also gives mitigations
and, importantly, their known limits.

Its central argument is in §1 and §4.1.2. No widely used ML algorithm has an
information-theoretic security proof, and impossibility results are appearing. Mitigations
are therefore empirical and may fall to new attacks, so pre-deployment testing has to be
combined with system design that treats the model as an untrusted component (§3.3.3, §4.2.5).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | A government taxonomy of attacks on ML and GenAI systems, with a mitigation discussion and its limits for every attack class. |
| Cryptography | adjacent | Names cryptographic measures only as mitigations: secure computation to keep training data confidential (§2.1.2), publisher hashes checked on web-scale data downloads (§3.2.3), and origin and integrity attestation of data (§4.2.1). It specifies none of them. |
| This project | core | RPT-0014's preliminary research already depends on it. It is TM-004 in `threat-models.md`, and RPT-0014's `attack-catalog.yaml` pins its NISTAML ids as one of five catalogs; that catalog maps 98 of its 146 AITs to a NISTAML id. Those mappings are RPT-0014's (AI-generated, review status `hypothesis`), not NIST's. |

Bears on **R-020** (map a generic threat onto a product). NISTAML classes are generic AI
attack classes, and the capability axis states what an attacker must control for the class
to apply to a given product. Also bears on **DEC-009** (generic-threat → product mapping and
mitigation lifecycle, open), because each class comes with mitigations and the conditions
under which they fail. It does not bear on R-010 or DEC-008: the report uses no CWE ids, and
`enumerations.md` §3.1 records that there is no official mapping from NISTAML ids to CWE,
ATLAS or OWASP.

## RPT-0014 applicability

**Where the linked ids come from.** The NISTAML ids, section numbers and figures are taken
from the NIST publication. The AIT-, TM-, A- and C- ids, the AIT counts, and every pairing of
a NISTAML id with an AIT are taken from RPT-0014's existing preliminary research artifacts:
`attack-catalog.yaml` (its `nist_ai_100_2` and `nist_scope` fields), `threat-models.md`, and
`report.md` §1 and §4. NIST did not establish them. The catalog marks every entry
`review_status: hypothesis`. Placing NIST's targets and figures onto RPT-0014's asset (A-) and
component (C-) vocabularies is this calibration pass's reading, and is a hypothesis as well.

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | AIT-001 (.022), AIT-002 (.025), AIT-013 (.013), AIT-014 (.023), AIT-032–AIT-035 (.051), AIT-052 (.031), AIT-047 (.032, .034), AIT-046 (.033), AIT-063 (.018), AIT-064 (.015), AIT-088 (.016), AIT-111 (.017), AIT-083 (.035), AIT-084 (.036, .038), AIT-091 (.039); no id (gap): AIT-099, AIT-100, AIT-101, AIT-109, AIT-138, AIT-139, AIT-140 | It reports no attack of its own. It classifies the published literature (449 references) and cites the canonical attack papers. RPT-0014's catalog maps 98 of its AITs to its ids; the pairings shown are the catalog's. The catalog marks seven agent AITs as `gap`, which is consistent with §3.5 (Security of Agents) having no NISTAML id. |
| Existing AI threat models | core | TM-004 | It is TM-004. It decomposes threats by objective × capability × knowledge × stage, which is the lifecycle × capability style of `threat-models.md` (style a). |
| Weakness enumerations | adjacent | NISTAML.01–.05, NISTAML.011–.051 (25 leaves); cites ATLAS mitigations AML.M0000, AML.M0001, AML.M0002, AML.M0004 ([249]–[252]) | It is an id scheme for **attack classes**, not weaknesses: it names no root-cause flaw and no CWE. `report.md` §6 and `enumerations.md` already classify it as a taxonomy, not a weakness enumeration. |
| Attack → asset mapping | adjacent | assets A01, A02, A03, A04, A05, A07, A11; components C01, C02, C03, C04, C05, C06, C07, C08, C09, C13, C16 | NIST names targets only in passing and has no asset vocabulary. The A- and C- ids are RPT-0014's (`report.md` §4 and §1), and placing NIST's text onto them is this pass's reading: training data (A01); weights and architecture (A02); model behaviour (A03); system prompt (A04); the RAG knowledge base (A05); user and in-context data (A07); availability and compute (A11, from energy-latency and time-consuming-task attacks). Components come from Fig. 4 to Fig. 6 and §3.1: web-scale data and ingested resources (C01, C02); training, fine-tuning and RLHF (C03); third-party models and plugins (C04, C09); query access and serving (C05); RAG (C06); system prompt and output handling (C07); agents (C08); hosted and fine-tuning APIs (C13); and quantized edge models and physical evasion (C16). It has no asset × attack matrix. |

## Implementations

| Name | Kind | License | URL |
|---|---|---|---|
| garak | LLM vulnerability scanner (cited [106]) | Apache-2.0 | https://github.com/NVIDIA/garak |
| PyRIT | GenAI risk identification and red-teaming framework (cited [364]) | MIT | https://github.com/microsoft/PyRIT |

Searched 2026-10-30. The report's own URLs have moved: `leondz/garak` redirects to
`NVIDIA/garak`, and `Azure/PyRIT` is archived, with development continuing at
`microsoft/PyRIT`. NIST publishes the taxonomy only as a PDF. No machine-readable release of
the NISTAML ids was found on the publication page.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: bibliographic fields, digest, partial `cites`, relations, `bears_on`, applicability, tags |
| `summary.md` | this summary, with the RPT-0014 applicability table |

The PDF is not committed. It is fetched by its digest through `pdf-manifest.tsv`.

## Limits

- **Platform and system attacks are out of scope by design** (§1). Infrastructure, MLOps,
  credential and tool-authorization attacks, which a company threat model needs, have no
  NISTAML id. RPT-0014's preliminary catalog records 41 of its AITs as out of scope, and the
  agent attacks above as gaps.
- **Agents are discussed but not classified.** §3.5 is one page and has no id.
- **No asset vocabulary.** It names what is attacked only in passing, so it cannot drive the
  attack → asset matrix in `report.md` §4.
- **No risk tolerance.** It explicitly makes no risk-tolerance recommendation (Executive
  Summary) and leaves risk-management decisions aside (§4.2.5).
- **The ids are not machine-readable** and have no official crosswalk to CWE, ATLAS or OWASP.
  The page-x index has a known error (see the source check above).
- **Notes for the integration lane, not edits.**
  - `sources.md` types S-0855 as `standard`. The document disclaims being one; this record
    uses `spec` with maturity `informational`.
  - `threat-models.md` TM-004 says "25+ leaf ids". The count is exactly 25.
  - The report cites Greshake et al. [146] as an arXiv preprint and gives no venue. It does
    not cite BIML's ARA (S-0728).
- **What this pass read and did not read.** It read the front matter, the index,
  §1, §2.1, §2.2.5, §2.4.5, §3.1–§3.6, §4 and the reference list. The attack bodies of
  §2.2–§2.4 and the mitigation detail in §2.3 and §3.4.4 were skimmed, not read line by line.
