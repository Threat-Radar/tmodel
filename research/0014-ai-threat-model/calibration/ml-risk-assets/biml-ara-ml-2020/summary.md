---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-10-30"
---

# An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning

|  |  |
|---|---|
| **Type** | paper (self-published technical report) |
| **Maturity** | white-paper: published by BIML on its own site, with no venue or peer review stated |
| **Authors** | G. McGraw, H. Figueroa, V. Shepardson, R. Bonett (Berryville Institute of Machine Learning) |
| **Published** | 2020-01-20, the date BIML gives on berryvilleiml.com/results/. The cover reads "Version 1.0 (1.13.20)", which is 2020-01-13. |
| **Identifier** | none (no DOI or report number); the URL is the identifier. BIML calls the risk set "BIML-78". |
| **Source** | https://berryvilleiml.com/results/ara.pdf, which redirects to `/docs/ara.pdf` (42 pp.) |
| **Digest** | `247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312` (retrieved 2026-10-30; equals `pdf-manifest.tsv`) |
| **License** | CC BY-SA 3.0 (p. 2) |

## Source check (2026-10-30)

- **Two dates.** The cover dates Version 1.0 "1.13.20". BIML's results page says it was
  published January 20, 2020, and the PDF's internal creation date is also 2020-01-20. This
  record uses the publisher's date. `sources.md` and `threat-models.md` give 2020-01-13.
- **Only one version is published.** The results page links only `ara.pdf`, and no later
  version was found. The 2024 sequel (an ARA of LLMs, RPT-0014 S-0739) is a separate document.
- **The risk count.** The document says it has 78 risks (pp. 5, 36), and BIML's site calls
  them the BIML-78. Counting the labelled entries in Part One gives **79 entries under 78
  labels**: `[inference:3:…]` is used twice, for *hyperparameters* and for *confidence
  scores*. Four cross-references cite the wrong number:
  - `[data:4:disimilarity]` should be `data:3`;
  - `[data:6:online]` should be `data:7`;
  - `[eval:4:catastrophic forgetting]` should be `eval:5`;
  - `[inference:3:hosting]` should be `inference:4`.

  The count was made by script from the PDF text and checked by reading every section.

## Overview

The report applies software-security **architectural risk analysis** to machine learning. It
is a design-level look for systemic risks, offered as an alternative to chasing individual
published attacks (pp. 4–5).

It models a **generic ML system as nine components** (Fig. 1):

1. raw data in the world
2. dataset assembly
3. datasets
4. learning algorithm
5. evaluation
6. inputs
7. model
8. inference algorithm
9. outputs

Components 2, 4, 5 and 8 are processes. Components 1, 3, 6, 7 and 9 are things or collections
of things.

For each component it lists labelled risks of the form `[component:n:descriptor]`, with
associated controls, and then adds ten system-wide risks. It also gives:

- a top-ten list;
- a six-category attack taxonomy, built from *how* the system is compromised (manipulation
  or extraction) and *where* (data, input or model);
- three attack surfaces: data sources, engineering and deployment (Fig. 2);
- Part Two: Saltzer and Schroeder's security principles adapted to ML.

Its central claims are three:

- **Data matter more than the algorithm** for ML security (pp. 10, 15).
- **Many risks are intrinsic design flaws** made by well-meaning engineers, not only attacks
  (p. 8).
- **Mapping a specific system onto the nine components** makes the risk analysis
  straightforward. It shows this with Google's neural machine translation system (GNMT,
  pp. 7–8).

### The risk vocabulary (from the source)

| Component | Label prefix | Entries |
|---|---|---|
| 1 Raw data in the world | `raw` | 13 |
| 2 Dataset assembly | `assembly` | 8 |
| 3 Datasets | `data` | 7 |
| 4 Learning algorithm | `alg` | 11 |
| 5 Evaluation | `eval` | 7 |
| 6 Inputs | `input` | 5 |
| 7 Model | `model` | 5 |
| 8 Inference algorithm | `inference` | 6 (two share the number 3) |
| 9 Outputs | `output` | 7 |
| System-wide | `system` | 10 |
| **Total** | | **79 entries, 78 labels** |

**Top ten (pp. 8–10):**

1. adversarial examples
2. data poisoning
3. online system manipulation
4. transfer learning attack
5. data confidentiality
6. data trustworthiness
7. reproducibility
8. overfitting
9. encoding integrity
10. output integrity

**Attack taxonomy (pp. 23–24):**

- manipulation: (1) data manipulation, (2) input manipulation, (3) model manipulation;
- extraction: (4) data extraction, (5) input extraction, (6) model extraction.

**System-wide risks (pp. 25–26):** black-box discrimination, overconfidence, loss of
confidence, public perception, error propagation, cry wolf, data integrity, insider, API
encoding, and denial of service.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | A security-engineering risk analysis of ML systems, with controls. |
| Cryptography | adjacent | Concrete but brief. It warns against non-cryptographic randomness for dataset partitions and weight initialization (`[assembly:8:random]`, `[alg:4:randomness]`), suggests cryptographic protection of data integrity (`[raw:generic]`), and presents differential privacy (Principle 7). It specifies no scheme. |
| This project | core | **RPT-0014's preliminary artifacts** (AI-generated, a hypothesis) list it as TM-014 in `threat-models.md`, cite it in `report.md` §5, and name `TM-014-biml-78` as a WAVE 2 extraction unit for this lane. |

Bears on **R-020** (map a generic threat onto a product) and on **DEC-009** (generic-threat →
product mapping, open). Its method *is* a generic-to-specific mapping: decompose the specific
system into the nine generic components, then carry across each component's risks. Linking
it to the tmodel decisions is this pass's reading; the report does not reference tmodel.

## RPT-0014 applicability

**How to read the linked ids.** Three kinds of statement are kept apart:

- **Source:** stated in the BIML document.
- **RPT-0014:** a mapping already present in RPT-0014's preliminary artifacts, which are
  AI-generated hypotheses.
- **This pass:** this calibration's own reading, also a hypothesis.

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | **RPT-0014:** no AIT lists S-0728 in its `sources`. **This pass:** data manipulation → AIT-011, AIT-012, AIT-013; input manipulation → AIT-001, AIT-002, AIT-004; model manipulation → AIT-015, AIT-034; data extraction → AIT-046, AIT-047; input extraction → AIT-047; model extraction → AIT-052; top-ten online manipulation → AIT-027; top-ten transfer attack → AIT-003 | **Source:** it reports no new attack. It sorts known attacks into six categories with citations to the original papers (pp. 23–24), and explicitly sets aside attacks on ML infrastructure. **This pass:** the AIT pairings are mine. |
| Existing AI threat models | core | **RPT-0014:** TM-014 | **Source:** it is an architectural risk analysis (a threat model) of a generic ML system. **RPT-0014:** `threat-models.md` files it as TM-014 under decomposition style (b), component or layer. |
| Weakness enumerations | adjacent | **RPT-0014:** AML.T0020, AML.T0043, AML.T0015, AML.T0024, ML01, ML10 (the `sources.md` row for S-0728) | **Source:** its labelled risks mix attacks with intrinsic design flaws (p. 8). That makes it more weakness-like than an attack taxonomy, but it uses no CWE ids. **This pass:** the labels are not stable keys: one number is used twice and four cross-references are wrong (see the source check). They would need a reconciled id table before any catalog could link to them. |
| Attack → asset mapping | core | **RPT-0014 (TM-014):** "the nine components" as assets. **This pass:** components 1 → C01; 2 and 3 → C02; 4 and 5 → C03; 6 → C05, and C16 for sensors; 7 → C04 and C05; 8 → C05; 9 → C17. Assets A01, A02, A03, A07, A11, A12, A13, A16 | **Source:** it is the only one of the three calibration sources whose primary axis is *the components of the system*. Every risk is attached to a component, processes are separated from collections, and three attack surfaces group them. The text places the inference software and model in deployment, the build process in engineering, and raw data in data sources. The exact plate boundaries are drawn only in Fig. 2. Its data-as-money exercise (Principle 1) asks where valuable data enter, are stored and leave. **This pass:** the C- and A- placements are mine. The system-wide risks are what carry it to business assets: error propagation into decisions (A12), cry wolf in security monitoring (A16), and public perception (A13). |

### What it offers company-level AI threat modeling (this pass)

These are interpretations, not claims of the source.

- **A reusable template.** Mapping the system onto the nine components, then walking each
  component's risk list, is a procedure a company threat model can apply per ML subsystem.
  The GNMT walk-through is a worked example.
- **Processes versus collections** lines up with data-flow-diagram processes and data stores.
  That makes the components easy to place on a company's architecture.
- **The three attack surfaces** are a coarse ownership and lifecycle axis. Data sources are
  often outside the company, engineering is internal, and deployment is exposed.
- **What it lacks for company use:**
  - No GenAI, RAG, tools or agents, so components C06–C11 have no counterpart. The 2024 LLM
    sequel, S-0739, is where that continues.
  - No business-asset vocabulary.
  - No attacker capability model.
  - No severity or likelihood, beyond the ordering of the top ten.

## Implementations

| Name | Kind | License | URL |
|---|---|---|---|

Searched GitHub on 2026-10-30 for "BIML architectural risk analysis", "berryvilleiml" and
"BIML-78": no implementation or machine-readable release found. The risks exist only as
labelled prose in the PDF.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: bibliographic fields, version, digest, partial `cites`, `bears_on`, applicability, tags |
| `summary.md` | this summary, with the risk-vocabulary tables and the RPT-0014 applicability table |

The PDF is not committed. It is fetched by its digest through `pdf-manifest.tsv`.

## Limits

- **It predates GenAI (2020).** It treats a generic, mostly predictive, ML pipeline.
  Prompt-driven, retrieval and agent systems are absent. Generative models are mentioned only
  in passing (`[eval:1]`, `[inference:3]`).
- **Not peer reviewed.** It is an expert analysis by one institute. The risks are argued
  from experience and literature, not measured.
- **No prioritization method.** The top ten is the authors' judgement. Component risks are
  described as ranked (p. 10), but no criteria are given.
- **Infrastructure is set aside.** Attacks on ML infrastructure, and attacks that circumvent
  ML-based defences, are excluded (p. 23). Conventional security is mentioned but not
  analysed (`[inference:4:hosting]`).
- **Labels are not stable keys.** See the source check: 79 entries under 78 labels, and
  four wrong cross-references.
- **Citation defects (this pass).** The Tay example under `[system:4:public perception]`
  cites [32], Jagielski et al. on poisoning regression learning, which does not concern Tay.
  The Saltzer and Schroeder principles are dated 1972 in the text but cited as a 1975
  publication [3].
- **Notes for the integration lane, not edits.**
  - `sources.md` and `threat-models.md` date S-0728 to 2020-01-13; BIML gives 2020-01-20.
  - TM-014 says "78 risks"; the document has 79 entries under 78 labels.
  - `report.md` §5 credits the BIML ARA row (S-0728 with S-0739) with a vendor-boundary
    concept. That concept does not appear in this 2020 document, which never mentions
    vendors, so it presumably comes from S-0739.
  - TM-014's comparison row marks its threat ids as stable; see the label defects above.
- **What this pass read.** All 42 pages, including Part Two and the 35 references. Pages 6
  and 27–28 carry only the running header.
