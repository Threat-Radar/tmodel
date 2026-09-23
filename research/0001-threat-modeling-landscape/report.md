---
schema: "archdoc/v1"
id: RPT-0001
title: "The threat-modeling landscape — methodologies, products, schemas, UI, and risk metrics"
short_title: "Threat-modeling landscape"
description: "Deep survey of the competitive and standards environment for threat modeling. Evidence for DEC-001, DEC-002, DEC-003, DEC-005, DEC-006, DEC-008. It does not select a design."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
authors:
  - role: team
    id: cs490-fall-2026
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0001-threat-modeling-landscape/report.md
library_commit: "see library/ submodule pointer at time of merge"
informs: [DEC-001, DEC-002, DEC-003, DEC-005, DEC-006, DEC-008]
open_decisions: [DEC-001, DEC-002, DEC-003, DEC-005, DEC-006, DEC-008]
---

# The threat-modeling landscape

> **This report does not select a design.** Every `DEC-*` it informs is open, and
> `CLAUDE.md` forbids documents that assume a selection. It is **evidence**: what
> exists, how the field models threats, where the tools differ, and what humans
> actually need from a reviewer's UI.

**Iterated in place.** This file is versioned; do not spawn a `-v2`. Bump
`version` + `updated` together as sections fill (§9.5). References live in
`library/`; this report summarizes and compares and links to implementations.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md).
Axes: [`dimensions.md`](dimensions.md).

## 1. Methodologies

_Pending (T-020)._ STRIDE, PASTA, attack trees, LINDDUN, OCTAVE, Trike, VAST,
ATT&CK-based. How each represents an attack path; how manual each is.

## 2. Commercial products

_Pending (T-021)._ IriusRisk, MS TMT, ThreatModeler, SD Elements, … — features,
integrations, model portability.

## 3. Open-source projects

_Pending (T-022)._ Threat Dragon, pytm, threagile, threat-composer, … — repo,
license, activity, object model, reusability.

## 4. Academic papers

_Pending (T-023)._ Automated / AI-assisted threat modeling; attack-path
generation; human-in-the-loop review; risk quantification.

## 5. Schema definitions & object models

_Pending (T-024)._ OTM, threagile YAML, pytm, Threat Dragon JSON, OSCAL,
STIX/TAXII, CycloneDX/SPDX, CWE/CAPEC/ATT&CK data models. **What we would import
(and possibly export).** Primary input to DEC-001/DEC-002.

## 6. UI requirements & competitive UI comparison

_Pending (T-021 / T-060)._ Diagram-first vs form-first vs graph vs matrix; the
interactions reviewers need (annotate, accept/reject, re-score, diff over time).
Input to DEC-006.

## 7. Risk metrics

_Pending (T-025)._ CVSS, EPSS, ISO/SAE 21434, Common Criteria feasibility, DREAD.
How "how bad" is computed and how environment/impact enters. Input to DEC-003.

## 8. CWE / NVD integration

_Pending (T-026)._ CWE/CAPEC structure; NVD/CVE APIs, rate limits, mirroring.
Input to DEC-008.

## 9. Synthesis — implications for tmodel

_Pending._ What the landscape implies for the object model, the MVP scope
(DEC-005), and the risk scheme (DEC-003). **No decision is taken here** — the
synthesis frames the options for the ADRs.
