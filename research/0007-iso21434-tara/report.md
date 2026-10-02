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

> **About quotations.** ISO/SAE 21434 is a paid standard, and its copyright page forbids reproducing it or posting it online. This repository is public, so the report describes the standard in our own words and points to clause, table and figure numbers (for example 15.9 or Table G.9). Apart from names (defined terms, impact categories, rating levels and rating factors, clause and table titles, requirement identifiers) and single keywords such as "shall", no wording is taken from it.

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

Clause 15 defines TARA as a set of methods for working out how far a threat scenario can affect road users, carried out from the point of view of the road users affected (15.1). The methods are generic modules: other clauses call them, at any stage of an item's or component's lifecycle, and their work products are recorded inside those clauses' work products (15.1). An organization may use its own scales for impact, attack feasibility and risk, as long as it maps them onto the standard's scales (15.1). Annex H walks through the methods with an example (§4).

### 2.1 The vocabulary

The terms TARA is built from, in our words. Clause 3.1 defines 40 terms in all.

| term | meaning | defined in |
|---|---|---|
| asset | something that has value or contributes to it; it has one or more cybersecurity properties, and compromising them can lead to damage scenarios | 3.1.2 |
| cybersecurity property | an attribute worth protecting, such as confidentiality, integrity or availability | 3.1.20 |
| damage scenario | a harmful consequence that involves a vehicle or a vehicle function and affects a road user | 3.1.22 |
| road user | anyone who uses a road, for example passengers, pedestrians, cyclists, motorists and vehicle owners | 3.1.31 |
| threat scenario | a possible cause of compromise of one or more assets' cybersecurity properties, leading to a damage scenario | 3.1.33 |
| attack path | the set of deliberate actions that realizes a threat scenario | 3.1.4 |
| attacker | whoever carries out an attack path: a person, a group or an organization | 3.1.5 |
| attack feasibility | how easily the actions of an attack path can be carried out successfully; a property of the path | 3.1.3 |
| impact | an estimate of how much damage or physical harm a damage scenario causes | 3.1.24 |
| risk | the effect of uncertainty on a road vehicle's cybersecurity, described by attack feasibility and impact | 3.1.29 |
| cybersecurity goal | a cybersecurity requirement at concept level, tied to one or more threat scenarios | 3.1.16 |
| cybersecurity claim | a statement about a risk, which can justify retaining or sharing it | 3.1.12 |
| cybersecurity control | a measure that modifies risk (adapted from ISO 31000) | 3.1.14 |
| weakness | a flaw or trait that can cause unwanted behaviour, such as a missing requirement, a design flaw or an implementation defect | 3.1.40 |
| vulnerability | a weakness that an attack path can exploit (adapted from ISO/IEC 27000) | 3.1.38 |

Two terms the steps rely on are not defined in 3.1: *impact rating* and *risk value*. Their meaning comes from the provisions in 15.5 and 15.8. The standard never uses the phrase "attack step": an attack path is a set of actions, and the example in 15.6 lists them in order.

### 2.2 The seven steps at a glance

| step | clause | needs (prerequisites) | provisions | produces |
|---|---|---|---|---|
| asset identification | 15.3 | item definition (WP-09-01) | RQ-15-01, RQ-15-02 | damage scenarios (WP-15-01); assets with cybersecurity properties (WP-15-02) |
| threat scenario identification | 15.4 | item definition | RQ-15-03 | threat scenarios (WP-15-03) |
| impact rating | 15.5 | damage scenarios | RQ-15-04 to RQ-15-06, PM-15-07 | impact ratings with their impact categories (WP-15-04) |
| attack path analysis | 15.6 | item definition (for an item) or cybersecurity specifications (for a component); threat scenarios | RQ-15-08, RQ-15-09 | attack paths (WP-15-05) |
| attack feasibility rating | 15.7 | attack paths | RQ-15-10, RC-15-11 to RC-15-14 | attack feasibility ratings (WP-15-06) |
| risk value determination | 15.8 | threat scenarios, impact ratings, attack feasibility ratings | RQ-15-15, RQ-15-16 | risk values (WP-15-07) |
| risk treatment decision | 15.9 | item definition, threat scenarios, risk values | RQ-15-17 | risk treatment decisions (WP-15-08) |

Clause 15 lists the methods in this order, but they are modules that other clauses call when needed (15.1); RQ-09-03, for example, runs six of them together (§2.10). The only fixed order comes from the prerequisites. Impact rating needs damage scenarios, feasibility rating needs attack paths, the risk value needs threat scenarios and both kinds of rating, and the treatment decision needs risk values.

### 2.3 Asset identification (15.3)

- Despite the step's name, its first provision asks for damage scenarios (RQ-15-01). The second asks for the assets, with their cybersecurity properties, whose compromise leads to those damage scenarios (RQ-15-02).
- A damage scenario can describe how the item's function relates to the harm, the harm to the road user, and the assets involved (NOTE 1).
- Assets can be found by analysing the item definition, by doing an impact rating, by working back from threat scenarios, or from predefined catalogues (NOTE 2).
- The two examples: personal data stored in an infotainment system, whose confidentiality is lost when it is disclosed without consent; and the data communication of the braking function, whose loss of integrity causes unintended full braking at high speed and a rear-end collision.

### 2.4 Threat scenario identification (15.4)

- Every threat scenario has to name three things: the asset targeted, which of its cybersecurity properties is compromised, and what causes the compromise (RQ-15-03).
- It can also carry, or link to, more: the damage scenarios, the attackers with their methods and tools, the attack surfaces, and technical dependencies between assets (NOTE 1).
- Threat scenarios can come from group discussion or from systematic methods, for example misuse and abuse cases, or frameworks such as EVITA, TVRA, PASTA and STRIDE (NOTE 2).
- Damage scenarios and threat scenarios are many-to-many: one damage scenario can have several threat scenarios, and one threat scenario can lead to several damage scenarios (NOTE 3).
- The example: spoofed CAN messages sent to the braking ECU, which compromise the integrity of the braking function.

### 2.5 Impact rating (15.5)

- Each damage scenario is assessed for harm to road users in four impact categories: safety, financial, operational and privacy, written S, F, O and P (RQ-15-04).
- In each category the rating is one of four levels: severe, major, moderate or negligible (RQ-15-05). Annex F has example criteria for each category (§3).
- Safety ratings must come from ISO 26262-3:2018, subclause 6.4.3 (RQ-15-06), and an existing functional safety evaluation can be reused (NOTE 6).
- The standard gives no weighting between the categories (NOTE 1). An organization can add categories (NOTE 2) and can share its reasons for them along the supply chain (NOTE 3).
- A category can be skipped when it can be argued that all its impacts are less critical than a rating already found (PM-15-07). In the example, once the safety impact is rated severe, the financial impact is not analysed further.

### 2.6 Attack path analysis (15.6)

- Threat scenarios are analysed to find attack paths (RQ-15-08), and each attack path is linked to every threat scenario it can realize (RQ-15-09).
- The analysis can work top-down, from a threat scenario to the ways it could be realized (attack trees, attack graphs), or bottom-up, building paths from vulnerabilities already identified (NOTE 1). A partial path that cannot realize any threat scenario can be dropped (NOTE 2).
- Early in development, paths are often incomplete or imprecise, and they are refined as more is known, for example after a vulnerability analysis (NOTE 3).
- The analysis runs on an item, using its item definition, or on a component, using its cybersecurity specifications (15.6.1.1). Weaknesses found in cybersecurity events or during development, the architectural design, earlier attack paths and vulnerability analyses can all be used (15.6.1.2).
- The example is a three-step path: an attacker compromises the telematics ECU through its cellular interface, uses it to compromise the gateway ECU over CAN, and the gateway then forwards malicious braking requests.

### 2.7 Attack feasibility rating (15.7)

- Every attack path gets one of four ratings from Table 1: High, Medium, Low or Very low, meaning the path takes low, medium, high or very high effort (RQ-15-10). The rating belongs to the path, as the definition of attack feasibility also says (3.1.3).
- The rating method should follow one of three approaches (RC-15-11), and the choice can depend on the lifecycle phase and the information available (NOTE 1):
  - **attack potential:** based on five core factors, namely elapsed time, specialist expertise, knowledge of the item or component, window of opportunity, and equipment (RC-15-12). ISO/IEC 18045 is the source the standard gives for these factors (NOTE 2). Guidance: G.2.
  - **CVSS:** using the four exploitability metrics from the CVSS base group, namely attack vector, attack complexity, privileges required and user interaction (RC-15-13). Guidance: G.3.
  - **attack vector:** based on the predominant attack vector of the path, in the CVSS sense (RC-15-14). It suits early phases, such as the concept phase, when specific attack paths cannot be identified yet (NOTE 6). Guidance: G.4.
- All three approaches are recommendations (RC), not requirements. The requirement is only that each path ends up with a Table 1 rating.

### 2.8 Risk value determination (15.8)

- For each threat scenario, a risk value is determined from two inputs: the impact of the damage scenarios it leads to, and the feasibility of its attack paths (RQ-15-15). It is a number from 1 to 5, where 1 is minimal risk (RQ-15-16). Risk matrices and risk formulas are the example methods; Annex H shows both (§4).
- **Several risk values per threat scenario are allowed.** When a threat scenario leads to more than one damage scenario, or one damage scenario is rated in several categories, each of those impact ratings can get its own risk value (NOTE 1). Clause 15.9 then speaks of a threat scenario's risk values, in the plural (RQ-15-17).
- **Several attack paths can be combined.** When a threat scenario has more than one attack path, their feasibility ratings can be aggregated, for example by giving the threat scenario the highest of them (NOTE 2). Clause 15 says nothing about combining the actions within one path; the path is rated as a whole (RQ-15-10). Annex G's attack potential guidance also rates the whole path, but lets distinct steps raise some factors, for example when different steps need experts in different fields (G.2.2; §3).
- The standard fixes the scales at both ends (four impact levels, four feasibility levels, risk from 1 to 5) but not the function that combines them, and it allows organization-specific scales that map onto its own (15.1).

### 2.9 Risk treatment decision (15.9)

- For each threat scenario, taking its risk values into account, one or more of four options must be chosen: avoiding, reducing, sharing or retaining the risk (RQ-15-17). Avoiding can mean removing the risk sources, or deciding not to start or not to continue the activity that causes the risk (EXAMPLE 1). Sharing can mean contracts or insurance (EXAMPLE 2).
- The reasons for retaining or sharing a risk are recorded as cybersecurity claims, which are then covered by cybersecurity monitoring and vulnerability management in Clause 8 (NOTE).
- The library catalog's entry for RQ-15-17 stops after the first option (§7).

### 2.10 Where the rest of the standard uses TARA

Found by searching Clauses 4 to 14 for references to 15.3 to 15.9, to the Clause 15 work products, and to "TARA" (searches.md, Tool runs).

| where | how it uses TARA | provisions |
|---|---|---|
| 9.4, cybersecurity goals (concept phase) | Runs steps 15.3 to 15.8 on the item (RQ-09-03), then 15.9 for every threat scenario (RQ-09-04); together these form the TARA work product (WP-09-02). Missing item information can be assumed (NOTE 1). Reducing a risk requires one or more cybersecurity goals (RQ-09-05), and a CAL can be set for a goal (NOTE 4, Annex E). Sharing a risk, or retaining it because of assumptions made in the analysis, requires cybersecurity claims (RQ-09-06). Avoiding a risk by removing its source can change the item (NOTE 2). A verification checks the analysis, the decisions, the goals and the claims (RQ-09-07). | RQ-09-03 to RQ-09-07; WP-09-02 to WP-09-05 |
| 9.5, cybersecurity concept | Can use the TARA as supporting input (9.5.1.2). | |
| 6.4, project management | Threat scenarios with risk value 1 (from 15.8) need not conform to 9.5 or to Clauses 10 and 11 (PM-06-08); their risks are still treated, possibly with less rigour (NOTE 5). The cybersecurity plan can be updated from TARA results (RQ-06-07, NOTE 4). A reuse analysis can lead to a new TARA for changed assets, threat scenarios or risk values (RQ-06-16, EXAMPLE 4). The decision whether to do a cybersecurity assessment can rest on TARA results (RQ-06-24, NOTE 1). | PM-06-08, RQ-06-07, RQ-06-16, RQ-06-24 |
| 5.4, organizational management | The organization's rules and processes include the TARA methods (RQ-05-02, NOTE 4). | RQ-05-02 |
| 7.4, distributed activities | What customer and supplier share can include how changes are communicated, including a possible rerun of the TARA (RQ-07-04, NOTE 1). | RQ-07-04 |
| 8.3 and 8.4, monitoring and event evaluation | Threat scenarios and cybersecurity claims can inform monitoring (8.3.1.2), and threat scenarios can be updated after an event is evaluated (RQ-08-04, NOTE 3). | RQ-08-04 |
| 8.5, vulnerability analysis | Whether a weakness is a vulnerability can be decided with attack path analysis (15.6) and feasibility rating (15.7) (RQ-08-05, NOTE 1). With no attack path, or a very low feasibility, the weakness does not count as a vulnerability (EXAMPLES 1 and 2), and every weakness not treated as a vulnerability needs a rationale (RQ-08-06). | RQ-08-05, RQ-08-06 |
| 8.6, vulnerability management | Each vulnerability is either assessed and treated through 15.9 until no unreasonable risk remains, or removed by an available remediation without a TARA (RQ-08-07). If a treatment decision needs incident response, 13.3 applies (RQ-08-08). | RQ-08-07, RQ-08-08 |
| 11.4, validation | Validation at the vehicle level must confirm, among other things, that the cybersecurity goals are adequate for the threat scenarios and their risk (RQ-11-01, item a). | RQ-11-01 |

Clauses 10 to 14 never cite Clause 15, its subclauses or its work products by number. Besides RQ-11-01, Clauses 10 and 11 build on concept-phase outputs that rest on the TARA: the cybersecurity concept (WP-09-06) in both, and the cybersecurity goals and claims (WP-09-03, WP-09-04) in Clause 11. Clauses 12 to 14 cite no concept-phase work product. Clause 13 is reached from Clause 8 instead: RQ-08-08 sends treatment decisions that need incident response to 13.3 (searches.md, Tool runs).

**Takeaway:** TARA produces a chain of linked objects: assets with cybersecurity properties, damage scenarios rated per impact category, threat scenarios that name an asset, a property and a cause, attack paths rated for feasibility, risk values from 1 to 5, and treatment decisions that lead to cybersecurity goals, cybersecurity claims or a change to the item. Each rating attaches to a specific object: impact to a damage scenario in each category, feasibility to an attack path, and risk to a threat scenario, optionally split by damage scenario and category. The standard fixes the scales but not the formula that combines them, and it rates each attack path as a whole: no provision rates or combines the individual actions inside a path. Section 5 maps these objects onto the proposed object model, and section 6 compares the risk rules with the metric in ARCH-0001-PROPOSAL.

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
