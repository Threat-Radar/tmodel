---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-11-01"
---

# An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning (BIML-78)

|  |  |
|---|---|
| **Type** | paper (a self-published institute report) |
| **Maturity** | _unset_. Neither the document nor the publisher's page states a standing |
| **Authors** | Gary McGraw, Harold Figueroa, Victor Shepardson, Richie Bonett |
| **Published** | Berryville Institute of Machine Learning (BIML). The cover reads "Version 1.0 (1.13.20)", i.e. 2020-01-13. The BIML results page dates publication to 20 January 2020, and the PDF metadata has CreationDate and ModDate of 2020-01-20. We record 2020-01-20 as the release date and 1.13.20 as the version date. Licensed CC BY-SA 3.0 (p. 2) |
| **Identifier** | none (no DOI or report number); the publisher page is https://berryvilleiml.com/results/ |
| **Source** | https://berryvilleiml.com/results/ara.pdf, which on 2026-11-01 redirected to https://berryvilleiml.com/docs/ara.pdf (server Last-Modified 2025-10-25; the bytes are unchanged) |
| **Digest** | `sha256:247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312` (848,055 bytes, 42 pages, retrieved 2026-11-01; matches `pdf-manifest.tsv`) |

Locators are printed page numbers. Pages 6, 27, 28, 37, 38 and 42 are decorative; they were checked visually.

## Overview

**Method.** The report performs a design-level architectural risk analysis (ARA) of a *generic* ML system, intended as a baseline that engineers map onto their own system (pp. 3, 7–8). Its worked example is Google's neural machine translation system (GNMT).

**The generic system.** Nine components joined by information flows (Fig. 1, p. 7):
- the "things": raw data in the world, datasets, inputs, model, outputs;
- the processes: dataset assembly, learning algorithm, evaluation, inference algorithm.

**Part One: risks.**
- Risks are listed per component, each with an identifier of the form `[component:number:descriptor]`, followed by 10 system-wide risks (pp. 10–26).
- A top-ten list is drawn from them (pp. 8–10).
- A six-way attack taxonomy crosses manipulation and extraction with data, input and model (Fig. 2, pp. 22–24).
- Three attack surfaces: deployment, engineering and data sources (p. 24).

**Part Two: principles.** Saltzer and Schroeder's design principles, as adapted in *Building Secure Software*, applied to ML (pp. 29–36).

**Central claims.**
- Data matter more to ML security than algorithms (pp. 10, 15, 30).
- Many risks are intrinsic design flaws rather than attacks (p. 8).
- Security comes from engineering and design, not from patching the attack of the day (pp. 4–5).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | A security risk analysis of ML systems with controls and design principles |
| Cryptography | `adjacent` | Only incidental: cryptographic versus Monte Carlo randomness (`[assembly:8:random]`, `[alg:4:randomness]`), an optional cryptographic integrity transform for data (p. 12), and differential privacy (pp. 16, 20, 34). No cryptographic mechanism is specified |
| This project | `core` | A component-based, design-level threat model meant to be specialised to concrete systems, which is tmodel's own pattern |

`bears_on: R-020, DEC-009`. This covers only part of DEC-009.

- **What supports it.** The source states that its risks were built for a generic system so that they apply to any specific one. It shows a worked mapping of the nine components onto GNMT and says that, given such a mapping, a risk analysis per component is straightforward (pp. 7–8). That is a method for R-020: mapping generic threats onto a specific product.
- **What it does not cover.** Product families and mitigation-lifecycle tracking (R-021, the other half of DEC-009).
- **Considered and rejected:** DEC-001a, already accepted, and R-005, since the source has no import format.

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | AIT-001, AIT-003, AIT-004, AIT-006, AIT-007, AIT-011, AIT-015, AIT-026, AIT-027, AIT-046, AIT-047, AIT-052 | The source maps known attack classes it cites onto its model (pp. 23–24); it demonstrates nothing itself. Real-world mentions are only Tay (p. 25) and a rumoured Google Translate feedback loop (pp. 11–12). Evidence for each AIT is listed below the table |
| Existing AI threat models | core | TM-014 | A full design-level ARA of a generic ML system: decomposition (Fig. 1), risks per component, system-wide risks, attack taxonomy, attack surfaces (Fig. 2), controls and design principles. The PDF never uses the term threat model; BIML's results page describes an ARA as something sometimes called a threat model |
| Weakness enumerations | adjacent | BIML-78 identifiers, for example `[raw:1:data confidentiality]` | 78 identifiers mixing attacks, intrinsic design flaws and engineering hygiene such as reproducibility and overfitting (p. 8). It is closer to a weakness list than an attack taxonomy, but it has no mapping to CWE or other catalogs, no versioned machine-readable release, and identifier defects (see Limits) |
| Attack → asset mapping | core (to components; no business assets) | C01, C02, C03, C04, C05, C17; TB1, TB3, TB11; A01, A02, A03, A11, A12, A13, A16, A18 — **assigned by us, not by the authors** | LANES.md defines this topic's linked ids as asset or component ids from `report.md` §1, and §1 defines components and trust boundaries; the A-ids are defined later, in §4. Under that definition a systematic attack-to-component mapping meets the topic, and this source provides one: each of its 78 identifiers is keyed to one of nine components or to the system as a whole, and Fig. 2 places all six attack classes on components and attack surfaces. What it lacks is a business-asset vocabulary and an attack-to-asset mapping; the word "asset" never appears. Its components are generic ML-pipeline parts, so only six §1 components are reachable. The C-, TB- and A-ids are our assignment onto RPT-0014's preliminary vocabularies; see the lists below |

**Evidence for each linked AIT.** These are the attacks the source names or cites; none are demonstrated by the authors:
- AIT-001: adversarial examples [14].
- AIT-003: transfer of attacks from a public base model, `[data:2:transfer]` and [28].
- AIT-004: physical stop sign [21].
- AIT-006: audio [23].
- AIT-007: spam evasion [22].
- AIT-011: data poisoning, `[data:1:poisoning]`.
- AIT-015: model manipulation or backdooring [24], and `[model:2:Trojan]`.
- AIT-026: the malicious insider, `[system:8:insider]`, and hyperparameter tampering, `[alg:10]`.
- AIT-027: online manipulation, `[alg:1]`, `[data:7]`, `[inference:1]`, and Tay.
- AIT-046: membership and property inference [7] [26].
- AIT-047: model inversion and input extraction [27] [33].
- AIT-052: model extraction [29].

**Not linked (borderline):**
- AIT-005: sensor blinding is a one-line example (p. 12).
- AIT-012: an attacker boosting the error rate in one sub-category, `[assembly:7]`, is not described as a targeted or clean-label attack.
- AIT-013: poisoning of public data is discussed conceptually (pp. 10, 30), but no web-scale mechanism is given.

**What the source itself identifies** (checked against the rendered Figs. 1 and 2 and the text):
- *Components and flows (Fig. 1):*
  - raw data → dataset assembly → datasets;
  - training and validation sets → learning algorithm; test set → evaluation; evaluation → learning algorithm;
  - learning algorithm → model; model → evaluation and → inference algorithm;
  - raw data → inputs → inference algorithm → outputs → back to raw data.
- *Attacks placed on Fig. 2:*
  - in red, manipulation: (1) at datasets, (2) at inputs, (3) at the model;
  - in blue, extraction flows: (4) from the training data through the learning algorithm into the model, (5) from inputs to outputs, (6) from the model to outputs.
- *Attack surfaces (Fig. 2):* three gray plates.
  - Engineering covers components 2–5.
  - Deployment covers components 6–9.
  - Data sources is the halo around component 1.
- *Trust boundaries:* none are drawn. The text says components are natural trust boundaries (p. 32), pipeline boundaries make poor ones (p. 33), and common ML containers have no internal trust boundaries (pp. 33–34).

**Our assignment onto RPT-0014's preliminary ids.** None of these ids appears in the source; this is our interpretation.
- *Components:*
  - raw data → C01;
  - dataset assembly and datasets → C02;
  - learning algorithm and evaluation → C03;
  - a reused or transferred model → C04 (`[model:1]`, `[model:2]`, `[alg:11]`);
  - inputs, deployed model and inference algorithm → C05;
  - outputs → C17.
- *Trust boundaries:*
  - TB1: the data-sources plate against the engineering plate;
  - TB3: public models and parameters entering the system (`[data:2]`, `[model:2]`, `[alg:11]`, Principle 10);
  - TB11: `[raw:12:sensor]`.
- *Assets*, read from what each risk endangers:
  - A01: training data confidentiality, `[raw:1]`;
  - A02: model theft, `[model:5:steal the box]`;
  - A03: model behaviour integrity;
  - A11: denial of service, `[system:10]`;
  - A12: error propagation into decisions, `[system:5]`;
  - A13: public perception, `[system:4]`;
  - A16: cry wolf in intrusion detection, `[system:6]`;
  - A18: discrimination against people in the data, `[system:1]`.

## Implementations

Searched 2026-11-01, limited to the publisher.

| Name | Kind | License | URL |
|---|---|---|---|
| BIML Interactive Machine Learning Risk Framework | Web page presenting the same risks; it repeats `inference:3` twice, as the PDF does | not stated; not checked | https://berryvilleiml.com/interactive/ |

The source references no other tooling or machine-readable export. Its sequel, the BIML LLM ARA of 2024-01-24 (S-0739), is listed on the same results page.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | Metadata. `cites` is a **calibration subset** of 21 of the 35 references; it is not the full list. Complete reference expansion and stub creation are reserved for subset-1 (LANES.md, Step 2, item 5). No stub records were created |
| `summary.md` | This document |

## Limits

- **No asset vocabulary and no scoring.**
  - The source keys risks to components, not assets.
  - It says it ranks risks within each component (p. 10) but gives no ranking criteria, likelihood or impact.
  - The top ten is the authors' judgement (p. 8).
- **Generic and from 2020.**
  - There is nothing on LLMs, retrieval, agents or tools; BIML's 2024 LLM ARA (S-0739) covers those.
  - Attacks on ML infrastructure and attacks that circumvent ML-based defences are set aside (p. 23).
  - Its comparison with NIST is against the 2019 draft NIST IR 8269 [31], not the later AI 100-2 editions.
- **Controls are thin and uneven.**
  - There are 26 control statements across eight components: 7 generic and 19 tied to specific risks.
  - The outputs component and the 10 system-wide risks have no associated controls.
- **The "78 risks" count depends on how you count** (pp. 5, 36).
  - There are 79 distinct risks: 69 per component plus 10 system-wide.
  - They carry 78 unique identifiers, because `[inference:3]` is used for both `hyperparameters` and `confidence scores` (p. 20).
- **Confirmed identifier errors** (the cross-reference does not match the definition):
  - p. 15: a control cites `[data:4:disimilarity]`; the risk is `[data:3:disimilarity]`.
  - p. 18: `[eval:1]` cites `[data:6:online]`; the risk is `[data:7:online]`, and data:6 is `supervisor`.
  - p. 19: `[eval:4:catastrophic forgetting]`; the risk is `[eval:5]`, and eval:4 is `science`.
  - p. 21: a control cites `[inference:3:hosting]`; the risk is `[inference:4:hosting]`.
  - Descriptors carry typos (`disimilarity`, `fludity`), so the identifiers cannot be parsed reliably without cleaning.
- **Confirmed reference defects:**
  - [3] prints volume and issue as 9(63); Crossref has 63(9), 1975. The text dates the principles 1972 (pp. 4, 5, 36) against its own 1975 reference.
  - [12] and [19] are the same Alfeld et al. AAAI 2016 paper.
  - [13] is printed as "Securing Engineering for Machine Learning" (p. 40); BIML's own results page lists the article as "Security Engineering for Machine Learning". `cites` keeps the printed title and gives the corrected one in the locator.
  - `[model:2:Trojan]` cites [7], a membership-inference paper that does not concern Trojans.
- **Confirmed figure and text mismatch.** p. 7 says components 1, 3, 6, 7 and 9 are drawn as rectangles; Fig. 1 draws component 1 as a hexagon.
- **Possible discrepancies, not confirmed:**
  - The Tay discussion (p. 25) cites [32], a regression-poisoning paper; whether that paper covers Tay was not checked.
  - The cover version date (2020-01-13) and the release date (2020-01-20) differ. This is probably a version-date convention, but BIML does not say.
- **Preliminary RPT-0014 statements checked against the source.**
  - `sources.md` and `threat-models.md` give the date as 2020-01-13; that is the cover's version date, not the release date.
  - TM-014 lists the assets as the nine components; that is an interpretation, because the source names no assets.
  - TM-014 calls the ids parseable; that holds only after the defects above are fixed.
  - The OWASP ML and ATLAS ids in `sources.md` are not in the source (2020) and were not verified.
