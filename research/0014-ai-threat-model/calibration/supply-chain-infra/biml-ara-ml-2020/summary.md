---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-10-29"
---

# An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning

|  |  |
|---|---|
| **Type** | paper (technical report) |
| **Maturity** | _unset_ (self-published by BIML as version 1.0; no review venue named) |
| **Authors** | Gary McGraw, Harold Figueroa, Victor Shepardson, Richie Bonett (Berryville Institute of Machine Learning) |
| **Published** | Version 1.0, dated 1.13.20 on the cover (2020-01-13); BIML's results page lists it under 20 January 2020 |
| **Identifier** | none; BIML calls it BIML-78 |
| **Source** | https://berryvilleiml.com/results/ara.pdf |
| **Digest** | `sha256:247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312` (42 pages) |
| **License** | Creative Commons Attribution-Share Alike 3.0 (p. 2) |

## Overview

BIML argues that ML security needs design-level architectural risk analysis instead of
another round of penetrate-and-patch against the attack of the day, and that data are
the most important part of an ML system to secure (pp. 4, 10). It models a generic ML
system as nine components, four processes (dataset assembly, learning algorithm,
evaluation, inference algorithm) and five collections (raw data in the world, datasets,
inputs, model, outputs), and lists labelled risks for each, such as
`[raw:1:data confidentiality]`, plus ten system-wide risks and a numbered top ten led by
adversarial examples, data poisoning and online system manipulation (pp. 7-26). A
taxonomy sorts known attacks by how they compromise a system (manipulation or extraction)
and where (data, input or model), giving six categories across three attack surfaces:
deployment, engineering and data sources (Figure 2, pp. 22-24). Part Two adapts ten
security principles, from Saltzer and Schroeder by way of Viega and McGraw's *Building
Secure Software*, to ML engineering (pp. 29-36).

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | `core` | A published threat model of ML systems: components, risks, attack categories and design principles |
| Cryptography | `none` | Mentions integrity protection and cryptographic randomness in passing (pp. 12, 14, 16); no mechanism |
| This project | `adjacent` | Prior art for component-based threat modeling of AI: risks attach to components, which is how RPT-0014's catalog attaches techniques to C01-C21 |

`bears_on: DEC-001a` (the core type system, accepted in ADR-0010). Its structure, risks
attached to components and attacks attached to a site, is evidence for how Component and
Threat relate in that type system, and its labels are a candidate set of external ids.

## Implementations

Searched on 2026-10-29.

| Name | Kind | License | URL |
|---|---|---|---|
| BIML Interactive Machine Learning Risk Framework | free web page: click a component to see its risks, with the same labels | not stated | https://berryvilleiml.com/results/interactive/ |

No machine-readable risk list (CSV, JSON or spreadsheet) was found. BIML's results page
offers the PDF and the interactive page. Its 2024 analysis of large language models
(BIML-LLM24, RPT-0014 source S-0739, TM-024) is a separate document that applies the
method to LLMs.

Because the text is CC BY-SA 3.0, a catalog that adapts BIML's risk descriptions must
credit BIML and share the adaptation under the same license.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this document |

## Limits

- **Before LLMs.** Written in January 2020: no prompt injection, retrieval or agents. The
  2024 LLM analysis (S-0739) covers those.
- **Nothing demonstrated.** It names attacks and cites the literature, but runs none.
- **Labels are not unique keys.** The document counts 78 risks (pp. 5, 36), and the
  per-component numbers do add up to 78, but two inference risks share the number 3
  (hyperparameters and confidence scores, p. 20), so 79 risks are described. Four
  cross-references use the wrong number: `[data:4:disimilarity]` (p. 15),
  `[data:6:online]` (p. 18), `[eval:4:catastrophic forgetting]` (p. 19) and
  `[inference:3:hosting]` (p. 21). A parser keyed on component and number would merge or
  misfile them; component plus descriptor resolves all five cases.
- **Thin controls.** Many risks have no control, and the controls given are mostly general
  advice (for example p. 12).
- **Infrastructure left out.** It sets aside attacks on ML infrastructure (p. 23), treats
  hosting in two sentences (`[inference:4:hosting]`, p. 20), and raises external tools such as
  TensorFlow, Kubeflow and pip only as a question of trust (Principle 9, p. 35). For the
  supply chain it covers transferred and Trojaned models, not model files, registries or
  MLOps platforms.
- **One version.** Version 1.0 has not been revised; the results page listed no newer
  version on 2026-10-29.

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | AIT-001, AIT-003, AIT-004, AIT-006, AIT-007, AIT-011, AIT-012, AIT-015, AIT-026, AIT-027, AIT-037, AIT-044, AIT-046, AIT-047, AIT-052 | Names attacks and cites the papers behind them, but demonstrates none, and no AIT entry cites S-0728. The mapping is ours: input manipulation and its stop-sign, spam and audio examples (AIT-001, AIT-004, AIT-007, AIT-006, p. 23); data manipulation (AIT-011, AIT-012, p. 23) and online system manipulation (AIT-027, p. 9); transfer attacks from a public base model and Trojaned models (AIT-003, AIT-015, pp. 14, 20); extraction (AIT-046, AIT-047, AIT-052, pp. 23-24); insiders (AIT-026, p. 26); attacker-controlled randomness (AIT-044, pp. 14, 16); compromised external code and tools (AIT-037, pp. 30, 35) |
| Existing AI threat models | core | TM-014, TM-024 | It is TM-014 (BIML-78). TM-024 is BIML's 2024 LLM analysis, built with the same method |
| Weakness enumerations | adjacent | CWE-1039, AML.T0043, AML.T0015, AML.T0020, AML.T0018, AML.T0024, AML.T0010, ML01:2023, ML02:2023, ML03:2023, ML04:2023, ML05:2023, ML07:2023, ML09:2023, ML10:2023 | Its labelled risks are an informal enumeration with no external ids. The ids listed are concept matches (ours). Four OWASP Machine Learning Security Top 10 (2023 draft) entries carry BIML's names: Input Manipulation (ML01), Data Poisoning (ML02), Transfer Learning (ML07) and Output Integrity (ML09). It compares its taxonomy with NIST's 2019 draft, NISTIR 8269 (p. 24, reference 31), which NIST obsoleted in 2023 for the AI 100-2 series |
| Attack → asset mapping | core | C01, C02, C03, C04, C05, C15, C17 | Risks attach to components, apart from ten system-wide risks, and attacks to a site (Figure 2). Our mapping of the nine components: raw data (C01); dataset assembly and datasets (C02); learning algorithm and evaluation (C03); a reused or transferred model (C04); inputs, model and inference algorithm in deployment (C05); outputs (C17). Hosting and external tools such as Kubeflow touch C15 |
