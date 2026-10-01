---
schema: "archdoc/v1"
id: RPT-0007
title: "ISO/SAE 21434 and TARA: requirements, method, and object model"
short_title: "ISO/SAE 21434 and TARA"
description: "Extraction of ISO/SAE 21434:2021 and its threat analysis and risk assessment (TARA) method: how the standard is organized, the TARA steps and rating scales, a worked example, how TARA objects map onto the proposed object model, and a check of the library's requirement catalog. No design decisions are made; it only contains the evidence."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
authors:
    - role: student
      id: ty-van-heerden
decision_makers:
    - role: sponsor
      id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0007-iso21434-tara/report.md
library_commit: "see library/ submodule pointer at time of merge"
informs: [DEC-001, DEC-003, DEC-009]
open_decisions: [DEC-001, DEC-003, DEC-009]
---

# ISO/SAE 21434 and TARA

> **This report does not select a design.** It is evidence for the open decisions listed above. It also serves ADR-0002 (which accepted DEC-005), because ADR-0002 names the ISO 21434 object model as the automotive vocabulary that maps onto the shared graph.

> **About quotations.** ISO/SAE 21434 is a paid standard, and its copyright page forbids reproducing it or posting it online. This repository is public, so the report describes the standard in our own words and points to clause, table and figure numbers (for example 15.9 or Table G.9). Apart from names (defined terms, rating levels, clause and table titles, requirement identifiers) and single keywords such as "shall", no wording is taken from it.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md).
Axes: [`dimensions.md`](dimensions.md).

## TARA at a glance

_Pending: filled in after sections 2 and 3._

## 1. The standard and how we use it

### 1.1 What it is

ISO/SAE 21434:2021, *Road vehicles: Cybersecurity engineering*, is a joint standard of ISO and SAE International. ISO's road-vehicle subcommittee for electrical and electronic components and general system aspects (ISO/TC 22/SC 32) prepared it together with SAE's Vehicle Cybersecurity Systems Engineering Committee (TEVEES18A). It is the first edition, and it replaces SAE J3061:2016, with content and structure completely reworked (Foreword; library record `sae-j3061`).

**What it covers:**
- Requirements for managing cybersecurity risk in a road vehicle's electrical and electronic (E/E) systems, their components and their interfaces, over the whole lifecycle, from concept and product development through production, operation and maintenance to decommissioning (Clause 1).
- Process requirements, plus a common vocabulary so that the organizations in a supply chain can communicate and manage cybersecurity risk the same way (Clause 1; Introduction).
- Only the E/E systems of series-production vehicles whose development or modification started after the standard was published (on 2021-08-31, per ISO Open Data) (Clause 1).

**Its unit of analysis is the item.** An item is all the electronics and software in a vehicle that together realize one vehicle-level function, such as braking. The standard describes the engineering of one item at a time and does not say how to divide a vehicle's functions into items. For the vehicle as a whole, it points to the vehicle's E/E architecture, or to the combined cybersecurity cases of every cybersecurity-relevant item and component (Clause 4).

**What it leaves out:**
- The choice of cybersecurity technology and solutions, which is left to the user (Clause 1).
- Prototypes. Aftermarket and service parts are included, but systems outside the vehicle, such as back-end servers, are out of scope, although an analysis may take them into account (Clause 4).
- Data formats. The text never mentions XML, JSON, a schema or an exchange format (searches.md, Tool runs), so encoding TARA results is left to tools, and to us.
- Regulation. It never mentions UN Regulation No. 155 or vehicle type approval (searches.md, Tool runs). Any link between them needs a different source.

**Why tmodel needs it.** ARCH-0001 lists R-012: support ISO/SAE 21434 risk analysis as an option (DEC-003). ADR-0002 names the ISO 21434 object model (asset, damage scenario, threat scenario) as the automotive vocabulary that should map onto the shared CWE/CVE/ATT&CK graph. Issue #11 asks for the standard's requirements and a candidate object model, and the EPIC (#20) feeds its results into #14 (metrics), #17 (schema) and #19 (compliance validation).

### 1.2 Where it stands

Status from ISO's own catalogue data (ISO Open Data, downloaded 2026-09-30). Of these documents, only ISO/SAE 21434 itself was read.

| document | subject | ISO stage | notes |
|---|---|---|---|
| ISO/SAE 21434:2021 | this standard | 90.20, under systematic review | 1st edition, published 2021-08-31, 81 pages; no replacement project listed |
| ISO 26262-3:2018 | Functional safety, Part 3: Concept phase | 90.92, to be revised | the only normative reference of ISO/SAE 21434 (Clause 2); a 3rd edition is in development as a draft International Standard (ISO/DIS 26262-3, stage 40.00) |
| ISO/SAE PAS 8475 | Cybersecurity assurance levels (CAL) and targeted attack feasibility (TAF) | 60.00, under publication | bears on assurance levels (Annex E) and attack feasibility (§3) |
| ISO/SAE TR 8477 | Cybersecurity verification and validation | 60.00, under publication | |
| ISO/PAS 5112:2022 | Guidelines for auditing cybersecurity engineering | 90.92, to be revised | a 2nd edition is in development as a draft Technical Specification (ISO/DTS 5112, stage 50.20); bears on audit automation (#19) |
| ISO 24089:2023 | Software update engineering | 60.60, published | amended by ISO 24089:2023/Amd 1:2024 |

The stage names come from ISO's harmonized stage codes. ISO's website refused automated access (HTTP 403), so the names are still pending a manual check on iso.org (searches.md).

### 1.3 How it is organized

- **Clauses 1 to 3:** scope, the one normative reference (ISO 26262-3:2018), and the vocabulary (terms in 3.1, abbreviations in 3.2).
- **Clause 4, general considerations:** context only. The Introduction calls it informational, and it has no provisions. It explains items, risk management across the supply chain and the lifecycle, and defence in depth.
- **Clauses 5 to 14** follow the lifecycle: organizational cybersecurity management (5), project-dependent management (6), activities split between customer and supplier (7), continual activities such as monitoring and vulnerability management (8), concept (9), product development (10), validation (11), production (12), operations and maintenance (13), and end of cybersecurity support and decommissioning (14).
- **Clause 15, the TARA methods:** building blocks that the activities in other clauses call when they need a risk assessment (Introduction; Clause 4). Most of the objects in §5 come from here.
- **Annexes A to H,** all informative (guidance, not requirements): a summary of activities and work products (A), cybersecurity culture (B), an interface agreement template (C), cybersecurity relevance (D), cybersecurity assurance levels (E), impact rating (F), attack feasibility rating (G), and a worked TARA example for a headlamp system (H).

**Provisions and work products.** Clauses 5 to 15 each give objectives, provisions and work products (Introduction). A provision is a requirement, a recommendation or a permission; every requirement in the standard uses "shall", every recommendation "should" and every permission "may" (searches.md, Tool runs). Work products are what the activities produce, and each one names the provisions it results from. Inputs are listed as prerequisites (mandatory work products from an earlier phase) or further supporting information (optional) (Introduction).

**Identifiers.** Each provision and work product carries a tag: RQ (requirement), RC (recommendation), PM (permission) or WP (work product), then the clause number, then a sequence number (Introduction). Provisions share one sequence per clause, whatever their kind: in Clause 15, PM-15-07 sits between RQ-15-06 and RQ-15-08, and RC-15-11 to RC-15-14 sit between RQ-15-10 and RQ-15-15. Work products have their own sequence.

Counted in our copy (searches.md, Tool runs):

| clause | title | provisions | work products |
|---|---|---|---|
| 5 | Organizational cybersecurity management | 17 | 5 |
| 6 | Project dependent cybersecurity management | 34 | 4 |
| 7 | Distributed cybersecurity activities | 8 | 1 |
| 8 | Continual cybersecurity activities | 8 | 6 |
| 9 | Concept | 11 | 7 |
| 10 | Product development | 13 | 7 |
| 11 | Cybersecurity validation | 2 | 1 |
| 12 | Production | 3 | 1 |
| 13 | Operations and maintenance | 3 | 1 |
| 14 | End of cybersecurity support and decommissioning | 2 | 1 |
| 15 | Threat analysis and risk assessment methods | 17 | 8 |
| **all** | | **118** (101 RQ, 13 RC, 4 PM) | **42** |

The counts match the library catalog (`iso-sae-21434-2021`, `distilled/requirements.yaml`), but 16 of its 118 entries carry wrong or incomplete text (§7).

**Why the identifiers matter for tmodel.** They give every obligation a stable key that does not depend on wording, and they link each work product to the provisions behind it. The library catalog already uses them as keys (for example `iso-sae-21434-2021#RQ-15-17`), and its distilled notes propose this requirement-to-work-product structure as the template for automating audits (`iso-sae-21434-2021`, `distilled/normative.md` §4). Automated compliance validation is issue #19.

### 1.4 Our copy and how we cite it

- **The copy.** We worked from the sponsor's purchased copy, the SAE-issued PDF of ISO/SAE 21434:2021 (87 pages; SHA-256 `73f990078d3a5b47dec91dd0d2b4e6c24cecd9e4160ae5b143c3b3fa80b7cdf4`, the digest in the library record and in #11). It stays on our machines and is never committed. Its text was extracted with `pdftotext` only to search and check it, and the extract also stays outside the repository (searches.md).
- **Citations.** Clause and subclause numbers (15.9), provision and work-product identifiers (RQ-15-17, WP-15-08), and table, figure and annex numbers (Table G.9, Figure 3). Unlike page numbers, these do not depend on the copy's layout.
- **Library links.** An identifier resolves in the library catalog as `iso-sae-21434-2021#RQ-15-17`. For the 16 entries listed in §7, read the standard instead until the catalog is fixed.

**Takeaway:** ISO/SAE 21434 is a process standard for one vehicle item at a time. It says which activities must happen and which work products must exist, and it leaves technology, tools and data formats to the user. Its RQ, RC, PM and WP identifiers give tmodel ready-made keys for requirements and evidence. The 2021 first edition is the current one: ISO lists it as under systematic review with no replacement project yet, while the companion PAS 8475 on assurance levels and targeted attack feasibility is under publication.

## 2. TARA step by step

_Pending._

## 3. Rating scales and methods (Annexes E, F and G)

_Pending._

## 4. Worked example: the Annex H headlamp system

_Pending._

## 5. TARA objects mapped onto the proposed object model

_Pending._

## 6. How ISO/SAE 21434 risk relates to the risk-metric work

_Pending._

## 7. Check of the library's requirement catalog

_Pending. Results so far are logged in `searches.md` (Tool runs): 16 of the 118 catalog entries do not match the standard._

## 8. Synthesis

_Pending._
