---
schema: "archdoc/v1"
id: RPT-0009-dimensions
title: "RPT-0009 dimensions: the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
record: RPT-0009
---

# RPT-0009: search dimensions

Each dimension is one section of `report.md`.

## 1. Target and family map
What are the SAGAI editions (2024, 2025, 2026), and what did each produce
(papers, talks, a joint document)? Which related specification families belong
in scope (ETSI SAI, CISA and partner-agency guidance), and which documents are
members of a group (`part_of`) rather than standalone?

## 2. SAGAI papers and outputs
For each paper or output:
1. Which threat does it address (prompt injection, tool misuse, data leakage, ...)?
2. Which defense does it propose, and is it in-model or system-level?
3. Does it state anything requirement-like that a system should do?

## 3. Requirements: ETSI EN 304 223
Every provision, with its principle, the stakeholder responsible (Developer,
System Operator, Data Custodian, End-user), and its verb (shall or should).
What do the related ETSI documents add (TS 104 223, TR 104 128, TS 104 216)?

## 4. Recommendations: CISA AI in OT
The four principles and their subsections. Which recommendations apply beyond
operational technology to any AI system?

## 5. Related guidance
Which documents do the seeds cite (NCSC/CISA guidelines, UK AI Code of Practice,
NIST AI RMF and AI 100-2, MITRE ATLAS, OWASP)? Which carry requirements worth
distilling, and which are stubs? Where do they overlap with #8, #9 and #12?

## 6. Applicability to tmodel
Which AI threats must the object model be able to express? Which requirements
apply to tmodel's own AI features (human oversight, audit trail of prompts and
models)? Which could be checked automatically (#19)?
