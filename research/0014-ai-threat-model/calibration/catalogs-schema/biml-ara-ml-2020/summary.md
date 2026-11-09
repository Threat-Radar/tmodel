---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-11-08"
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
| This project | adjacent | The closest prior art to tmodel's own approach. It maps generic risks onto system components, which is **DEC-009**. Its parseable `component:n:descriptor` ids are another external catalog that a `Weakness` or `AttackPattern` could cite (**DEC-001a**). It covers classic ML only, not LLMs or agents. |

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
| Weakness enumerations | core | `[component:n:descriptor]` ids, for example `[data:1:poisoning]`, `[input:1:adversarial examples]`, `[model:2:Trojan]` | It has its own parseable id scheme with no crosswalk to CWE, ATLAS or NISTAML: it predates ATLAS and AI 100-2. Several entries are design flaws (overfitting, reproducibility), not attacks, which a weakness catalogue can hold but an attack catalogue cannot. |
| Attack → asset mapping | core | C01, C02, C03, C05, C17; A01, A02, A03, A07 | Every risk is attached to a component. Mapped to RPT-0014: raw data → C01; assembly and datasets → C02; learning algorithm and evaluation → C03; inputs, model and inference algorithm → C05; outputs → C17. The confidentiality risks put A01 and A07 at stake, model theft A02, and integrity risks A03. |

## Reference expansion

Checked against `sources.md` on 2026-11-08. These cited, in-scope references are **not** in `sources.md` and are candidate `status: stub` records for the integration lane:

- M. Barreno, B. Nelson, R. Sears, A. D. Joseph, J. D. Tygar, "Can machine learning be secure?", ASIACCS 2006 (ref. 5);
- M. Barreno, B. Nelson, A. D. Joseph, J. D. Tygar, "The Security of Machine Learning", *Machine Learning*, 2010 (ref. 8);
- M. Kloft, P. Laskov, "A poisoning attack against online anomaly detection", NIPS Workshop on Machine Learning in Adversarial Environments for Computer Security, 2007 (ref. 18);
- E. Tabassi et al., "A Taxonomy and Terminology of Adversarial Machine Learning", NISTIR 8269 draft, October 2019, DOI 10.6028/NIST.IR.8269-draft (ref. 31). This is the draft that NIST AI 100-2 later grew from, so a `supersedes` chain may be wanted.

Already present: Papernot et al. SoK (S-0010), Shokri et al. membership inference (S-0027), Tramèr et al. model stealing (S-0013), Fredrikson et al. model inversion (S-0004), Gu et al. BadNets (S-0019), Biggio and Roli (S-0001).

## Limits

- **Classic ML, 2020.** No LLMs, retrieval, tools or agents, so prompt injection and the agentic risks that dominate RPT-0014 are absent. Use S-0739 for those.
- **Generic by design.** The nine-component model is the paper's strength and its limit: the risks must be re-derived for each specific system, and the paper offers no likelihood or severity ranking beyond the top ten's ordering.
- **Not peer reviewed**, and the top ten is the authors' judgement, not derived from data.
- **Its comparison with NIST is with the 2019 draft** (NISTIR 8269), not with AI 100-2. It positions BIML's taxonomy as simpler and practitioner-focused rather than contradicting NIST.
- **Read in part.** This summary rests on the front matter, the motivation, the generic model, the top ten, the format and opening entries of the component risks, the attack taxonomy, the attack surface, the system-wide risks and the close. Not every one of the 78 risk entries was read, so `confidence: medium`.
