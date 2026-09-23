---
schema: "archdoc/v1"
id: RPT-0001-dimensions
title: "RPT-0001 dimensions — the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
record: RPT-0001
---

# RPT-0001 — search dimensions

The axes of the threat-modeling landscape survey. Each is one section of
`report.md`, one lane (PROC-0001), and one GitHub issue (the *research-dimension*
template). Each question's answer is a **summary + comparison in the report**;
each source becomes a **`library/` record**; technical specs are **distilled**
toward schema/code.

## 1. Methodologies
STRIDE, PASTA, attack trees, LINDDUN, OCTAVE, Trike, VAST, kill-chain / MITRE
ATT&CK-based. For each: what it models, its notation, where it fits, its limits.
*How does each represent an attack path, and how manual is it?*

## 2. Commercial products
IriusRisk, Microsoft Threat Modeling Tool, ThreatModeler, SD Elements, Tutamantic,
Devici, etc. Features, pricing model, integrations (CI, issue trackers), and
whether the model is exportable/open.

## 3. Open-source projects
OWASP Threat Dragon, pytm, threagile, Microsoft TMT templates, threat-composer,
etc. **Record repo URL, license, and activity.** What is reusable? What is their
object model?

## 4. Academic papers
Recent work on automated / AI-assisted threat modeling, attack-path generation,
risk quantification, and human-in-the-loop review. What is state of the art, and
what is unsolved (traceability, impact judgement)?

## 5. Schema definitions & object models
The **most important dimension for our design.** OTM (Open Threat Model),
threagile's YAML model, pytm's Python model, OWASP Threat Dragon's JSON, OSCAL,
STIX/TAXII (for the threat-intel adjacency), CycloneDX/SPDX (composition input),
MITRE CWE/CAPEC/ATT&CK data models. *What do they model, how do they encode it,
and what would we import (and possibly export)?* Feeds DEC-001/DEC-002.

## 6. UI requirements & competitive UI comparison
How do the products above present the model — diagram-first, form-first, graph,
matrix? What interactions do reviewers actually need (annotate, accept/reject,
re-score, diff over time)? A side-by-side comparison. Feeds DEC-006.

## 7. Risk metrics
CVSS (base/temporal/environmental), EPSS, ISO/SAE 21434 (impact × attack
feasibility), Common Criteria attack-feasibility, DREAD (and why it's deprecated).
*How is "how bad" computed, and how is environment/impact factored in?* Feeds DEC-003.

## 8. CWE / NVD integration
MITRE CWE structure, CAPEC, and NVD/CVE APIs (rate limits, data model, mirroring).
*Live lookup vs cached mirror; how automation runs.* Feeds DEC-008.

---

**Distillation rule.** A technical specification found here does not just get
summarized — it gets **distilled** into the record's `distilled/`: field tables,
schemas, and (where useful) generated code, so the object model is built on real
formats, not paraphrase. A summary must link to implementations, repos, and specs.
