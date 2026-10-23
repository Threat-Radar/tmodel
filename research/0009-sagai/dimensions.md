---
schema: "archdoc/v1"
id: RPT-0009-dimensions
title: "RPT-0009 dimensions: the search axes"
type: research
status: draft
version: "0.2.0"
date: "2026-09-28"
updated: "2026-10-22"
record: RPT-0009
---

# RPT-0009: search dimensions

Each dimension is one section of `report.md`. Dimensions 7 and 8 were added on 2026-10-22, after the sponsor's direction to frame part B around AI threats (DL-0006).

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

## 7. Threat mapping (report Table 2)
For every entry of ETSI EN 304 223 and CISA AI-in-OT: which attack does it defend
against, as a NIST AI 100-2 E2025 class and, where one fits, a MITRE ATLAS
technique id? Is the mapping stated by the document or inferred by us? Which
classes does no entry reach?

## 8. Worked example (report §5)
Take one documented attack, model it against the schema, and place each of its
steps against the nearest provisions. Where do the requirements stop, and what
does the schema lack to model the attack?
