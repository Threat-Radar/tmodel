---
schema: "library-summary/v1"
id: biml-ara-ml-2020
record: biml-ara-ml-2020
type: summary
updated: "2026-10-11"
---

# An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning

|  |  |
|---|---|
| **Type** | paper (institute report, 42 pp.) |
| **Maturity** | _unset — do not guess_ |
| **Authors** | G. McGraw, H. Figueroa, V. Shepardson, R. Bonett |
| **Published** | Version 1.0, 2020-01-13, Berryville Institute of Machine Learning (BIML); CC BY-SA 3.0 |
| **Identifier** | https://berryvilleiml.com/results/ara.pdf |
| **Source** | same |
| **Digest** | `247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312` (matches `pdf-manifest.tsv`) |

## Overview

An **architectural risk analysis** (ARA) of a *generic* machine-learning system,
written from a "building security in" software-security perspective: secure ML
proactively at design time instead of "penetrate and patch". It decomposes a
generic ML system into **nine components** — raw data in the world, dataset
assembly, datasets, learning algorithm, evaluation, inputs, model, inference
algorithm, outputs — illustrated on Google's neural machine translation system,
and works through each component to name **78 risks** (the document's count),
each with a stable `component:n:name` identifier (e.g. `[data:1:poisoning]`),
followed by **system-wide risks** that arise between components. It ranks a **top
ten**: adversarial examples, data poisoning, online system manipulation, transfer
learning attacks, data confidentiality, data trustworthiness, reproducibility,
overfitting, encoding integrity and output integrity. Part Two adapts Saltzer and
Schroeder's **security principles** to ML.

## Applicability

| Axis | Rating | Why |
|---|---|---|
| Security | core | A published threat model / risk analysis of ML systems. |
| Cryptography | none | Not about cryptography. |
| This project | core | A component decomposition with named risks — the shape tmodel needs to attach AI threats to system components (ARCH-0001 Component, Threat). |

Bears on **DEC-001** (object model — component-based risk attachment).

## RPT-0014 applicability

| Topic of interest | Rating | Linked ids | Why |
|---|---|---|---|
| Published attacks | adjacent | AIT-001, AIT-011, AIT-027 | Names attack classes (adversarial examples, poisoning, online manipulation) but reports no new attacks |
| Existing AI threat models | core | TM-014 | Is the threat model (BIML-78) |
| Weakness enumerations | adjacent | BIML `component:n:name` ids | Its own risk ids; no CWE, ATLAS or OWASP mapping (predates them for AI) |
| Attack → asset mapping | core | C01, C02, C03, C05 | Every risk is tied to one of nine data/training/inference components |

## Implementations

Not software. The risk list is reused by BIML's later LLM analysis (BIML-81,
S-0739). Searched 2026-10-11.

| Name | Kind | License | URL |
|---|---|---|---|

## Artifacts in this record

| File | What it is |
|---|---|
| `record.yaml` | metadata |
| `summary.md` | this summary |

## Limits

- **Pre-LLM (2020).** No prompt injection, agents, tools or RAG; components are
  classic train/infer ML. BIML-81 (2024) covers LLMs.
- **Qualitative.** Risks are named and discussed, not rated or prioritized beyond
  the top-ten list.
- **Count not reconciled here.** The text says 78 risks; this WAVE 1 pass did not
  enumerate the identifiers one by one (that is WAVE 2 extraction).
- **Generic system only.** Applying it needs a system-specific ARA, as the authors say.
