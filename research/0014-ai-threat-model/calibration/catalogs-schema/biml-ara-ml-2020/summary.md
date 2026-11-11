---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-11-10"
lane: catalogs-schema
reviewed_by: ""
---

# An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning

|  |  |
|---|---|
| **Type** | article (institute white paper; not peer reviewed) |
| **Maturity** | _unset_ |
| **Authors** | Gary McGraw, Harold Figueroa, Victor Shepardson, Richie Bonett |
| **Published** | Version 1.0, dated 1.13.20 (2020-01-13), Berryville Institute of Machine Learning. CC BY-SA 3.0 |
| **Identifier** | none (no DOI) |
| **Source** | https://berryvilleiml.com/results/ara.pdf (42 pages) |
| **Digest** | `247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312` (matches `pdf-manifest.tsv`) |

## Overview

The paper argues that ML security in 2020 was repeating software security's "penetrate and patch" years. It calls for an architectural risk analysis (ARA) instead: a design-level view that brings out systemic risks before a system is built.

**The generic system.** The authors break a generic ML system into nine components with information flows between them (Fig. 1): raw data in the world, dataset assembly, datasets, learning algorithm, evaluation, inputs, model, inference algorithm and outputs. Their premise is that a risk which applies to this generic system almost certainly applies to any specific one.

**The 78 risks.** Each risk is listed under its component with an id of the form `[component:n:descriptor]`, for example `[raw:1:data confidentiality]` or `[model:2:Trojan]`, followed by controls. On top of that come system-wide risks (`[system:n:…]`, for example overconfidence and black-box discrimination) and a top ten. The top ten mixes attacks (adversarial examples, data poisoning, online system manipulation, transfer-learning attack) with intrinsic design flaws (reproducibility, overfitting, encoding and output integrity).

**Attacks and principles.** Attacks are classified separately, by how (manipulation or extraction) and where (data, input or model), giving six categories. Part Two adapts the ten security principles of *Building Secure Software* to ML.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | A published threat model and risk catalogue for ML systems, organised the way an architect would use it. |
| Cryptography | none | No cryptographic content. |
| This project | adjacent | The closest prior art to tmodel's own approach. It maps generic risks onto system components, which is **DEC-009**. Its `component:n:descriptor` ids are another external catalog that a `Weakness` or `AttackPattern` could cite (**DEC-001a**), keyed on the full id because the number alone is not unique (see Limits). It covers classic ML only, not LLMs or agents. |

## Implementations

Searched 2026-11-08: none found. The paper is an analysis with no tooling. BIML's later *Architectural Risk Analysis of Large Language Models* (S-0739, TM-024) applies the same method to LLMs.

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata: identifiers, digest, applicability, tags |
| `summary.md` | this summary, with the RPT-0014 applicability table |

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | — | The six attack categories (data manipulation, input manipulation, model manipulation, data extraction, input extraction, model extraction) survey known research attacks with citations. The paper reports no attacks of its own, so it is not evidence of any AIT entry. |
| Existing AI threat models | core | TM-014 | It *is* TM-014: a component-based threat model with a top ten and 78 component risks plus system-wide risks. |
| Weakness enumerations | core | `[component:n:descriptor]` ids, for example `[data:1:poisoning]`, `[input:1:adversarial examples]`, `[model:2:Trojan]` | It has its own id scheme with no crosswalk to CWE, ATLAS or NISTAML: it predates ATLAS and AI 100-2. Component and number do not identify a risk on their own, because two numbers are each given to two risks, so a parser has to key on the full id. Several entries are design flaws (overfitting, reproducibility), not attacks, which a weakness catalogue can hold but an attack catalogue cannot. |
| Attack → asset mapping | core | C01, C02, C03, C05, C17; A01, A02, A03, A07 | Every risk is attached to a component. Mapped to RPT-0014: raw data → C01; assembly and datasets → C02; learning algorithm and evaluation → C03; inputs, model and inference algorithm → C05; outputs → C17. The confidentiality risks put A01 and A07 at stake, model theft A02, and integrity risks A03. |

## Reference expansion

All 35 references were checked against `sources.md` on 2026-11-10, by title and then by author.

**Already present (12):**

| Ref. | Paper | `sources.md` |
|---|---|---|
| 7 | Shokri et al., membership inference | S-0027 |
| 14 | Goodfellow et al., adversarial examples | S-0006 |
| 21 | Eykholt et al., physical-world attacks | S-0038 |
| 22 | Biggio et al. 2013, evasion at test time | S-0002 |
| 23 | Carlini and Wagner, audio adversarial examples | S-0035 |
| 24 | Gu et al., BadNets | S-0019 |
| 25 | Kumar et al., failure modes in ML systems | S-0872 |
| 27 | Fredrikson et al. 2014, pharmacogenetics | S-0004 |
| 29 | Papernot et al., practical black-box attacks | S-0026 |
| 32 | Jagielski et al., poisoning regression learning | S-0042 |
| 33 | Fredrikson et al. 2015, model inversion | S-0005 |
| 34 | Abadi et al., deep learning with differential privacy | S-0007 |

**Missing and in scope (12).** These are cited, in-scope references not in `sources.md`, and candidate `status: stub` records for the integration lane:

- N. Papernot, "A Marauder's Map of Security and Privacy in Machine Learning", arXiv:1811.01134, 2018 (ref. 4);
- M. Barreno, B. Nelson, R. Sears, A. D. Joseph, J. D. Tygar, "Can machine learning be secure?", ASIACCS 2006 (ref. 5);
- M. Barreno, B. Nelson, A. D. Joseph, J. D. Tygar, "The Security of Machine Learning", *Machine Learning* 81(2), 2010 (ref. 8);
- S. Alfeld, X. Zhu, P. Barford, "Data Poisoning Attacks against Autoregressive Models", AAAI 2016 (refs. 12 and 19, the same paper listed twice);
- G. McGraw, R. Bonett, H. Figueroa, V. Shepardson, "Securing Engineering for Machine Learning", *IEEE Computer* 52(8), 2019 (ref. 13);
- X. Yuan, P. He, Q. Zhu, X. Li, "Adversarial Examples: Attacks and Defenses for Deep Learning", *IEEE TNNLS*, 2019 (ref. 16);
- M. Kloft, P. Laskov, "A poisoning attack against online anomaly detection", NIPS Workshop on Machine Learning in Adversarial Environments for Computer Security, 2007 (ref. 18);
- M. Mozaffari-Kermani et al., "Systematic poisoning attacks on and defenses for machine learning in healthcare", *IEEE JBHI* 19(6), 2014 (ref. 20);
- G. Ateniese et al., "Hacking smart machines with smarter ones", arXiv:1306.4447, 2013 (ref. 26);
- B. Wang, Y. Yao, B. Viswanath, H. Zheng, B. Y. Zhao, "With Great Training Comes Great Vulnerability: Practical Attacks against Transfer Learning", USENIX Security 2018 (ref. 28), the attack behind BIML's top-ten item 4;
- J. Gilmer et al., "Motivating the Rules of the Game for Adversarial Example Research", arXiv:1807.06732, 2018 (ref. 30);
- E. Tabassi et al., "A Taxonomy and Terminology of Adversarial Machine Learning", NISTIR 8269 draft, October 2019, DOI 10.6028/NIST.IR.8269-draft (ref. 31). This is the draft that NIST AI 100-2 later grew from, so a `supersedes` chain may be wanted.

**Out of scope for RPT-0014:**
- software-security books and papers (refs. 1–3);
- machine translation (6), fairness (9), technical debt (10) and explainability (11);
- BLEU (15), a popular book (17) and data-release privacy (35).

**Corrected after review.** The first version of this section, on 2026-11-08, made two errors:
- **It listed four papers as cited that BIML does not cite:**
  - Biggio and Roli (S-0001 is Biggio, Nelson and Laskov 2012, and *Wild Patterns* is S-0672);
  - Papernot et al.'s SoK (S-0673);
  - "The Limitations of Deep Learning in Adversarial Settings" (S-0010);
  - Tramèr et al. (S-0013).
- **It found only four of the twelve missing references.**

## Limits

- **Classic ML, 2020.** No LLMs, retrieval, tools or agents, so prompt injection and the agentic risks that dominate RPT-0014 are absent. Use S-0739 for those.
- **Generic by design.** The nine-component model is the paper's strength and its limit: the risks must be re-derived for each specific system, and the paper offers no likelihood or severity ranking beyond the top ten's ordering.
- **Not peer reviewed**, and the top ten is the authors' judgement, not derived from data.
- **Ids are not unique by component and number.**
  - **Two risks share a number.** `[data:4:storage]` and `[data:4:disimilarity]` are both defined on PDF p. 15, and `[inference:3:hyperparameters]` and `[inference:3:confidence scores]` on p. 20.
  - **Three cross-references use the wrong number:**
    - `[data:6:online]` on p. 18 means `[data:7:online]`;
    - `[eval:4:catastrophic forgetting]` on p. 19 means `eval:5`;
    - `[inference:3:hosting]` on p. 21 means `[inference:4:hosting]`.

  A parser has to key on the full id, descriptor included.
- **Its comparison with NIST is with the 2019 draft** (NISTIR 8269), not with AI 100-2. It positions BIML's taxonomy as simpler and practitioner-focused rather than contradicting NIST.
- **Read in part.** This summary rests on the front matter, the motivation, the generic model, the top ten, the format and opening entries of the component risks, the attack taxonomy, the attack surface, the system-wide risks and the close. Not every one of the 78 risk entries was read, so `confidence: medium`.
