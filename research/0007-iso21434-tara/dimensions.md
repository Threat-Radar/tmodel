---
schema: "archdoc/v1"
id: RPT-0007-dimensions
title: "RPT-0007 dimensions: the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: RPT-0007
---

# RPT-0007: search dimensions

Each dimension is one section of `report.md`. They come from issue #11 (scope and questions, definition of done) and from the sponsor's next steps in its comments: review the library's requirement catalog line by line, and distill the annexes on impact and attack feasibility.

## 1. The standard
What does ISO/SAE 21434:2021 cover and leave out, where does it stand in ISO's process, how is it organized, and how are its requirements and work products identified?

## 2. TARA step by step
For each step of Clause 15 (asset identification, threat scenarios, impact rating, attack paths, attack feasibility, risk value, risk treatment):
1. What goes in, and what comes out?
2. Which provisions and work products apply?
3. Which other clauses call it (concept, product development, vulnerability analysis, and so on)?

## 3. Rating scales and methods
Annexes E, F and G:
1. How is impact rated, per category and level, and where do safety ratings come from (ISO 26262-3)?
2. What are the three ways to rate attack feasibility (attack potential, CVSS, attack vector), and how do their inputs and outputs differ?
3. How do cybersecurity assurance levels (CAL) depend on TARA results?

## 4. Worked example
How does the Annex H headlamp example move through every step, and which objects and values does it produce? (A candidate test fixture for #17.)

## 5. Objects and relations
1. Which objects and relations does TARA need (Figure 3 plus Clause 15)?
2. How do they map onto the types in ARCH-0001-PROPOSAL v0.2.0 (`DamageScenario`, `ThreatInstance`, `AttackPath`, `RiskScore`, and so on)?
3. What is missing on either side? This is evidence for #15 and #17, not a rival model.

## 6. Risk
How does ISO/SAE 21434 turn impact and feasibility into a risk value, and how does that relate to CVSS and the other options in DEC-003 (#14)?

## 7. Library catalog check
Does the library's requirement catalog (`iso-sae-21434-2021`, `distilled/requirements.yaml`) match the standard? This is the verify pass of the library's full-extraction standard (FX-1): counts, word-for-word text, dropped or spliced statements, locators.

## 8. Synthesis
Evidence by decision (DEC-001, DEC-003, DEC-009), tool support (a pointer to RPT-0003, #7), and limits.
