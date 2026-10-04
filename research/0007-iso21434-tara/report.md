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
updated: "2026-10-03"
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

> **About quotations.** ISO/SAE 21434 is a paid standard, and its copyright page forbids reproducing it or posting it online without written permission, except where otherwise specified or required to implement it. This repository is public, so the report describes the standard in our own words and points to clause, table and figure numbers (for example 15.9 or Table G.9). Apart from names (defined terms, impact categories, rating levels and rating factors, clause and table titles, requirement identifiers) and single keywords such as "shall", no wording is taken from it.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md).
Axes: [`dimensions.md`](dimensions.md).

## TARA at a glance

The seven Clause 15 methods, what each one produces or rates, and on which scale. Details are in §2 (steps) and §3 (scales).

| step | clause | produces or rates | scale | guidance | provisions | work product |
|---|---|---|---|---|---|---|
| asset identification | 15.3 | damage scenarios; assets with cybersecurity properties | none | | RQ-15-01, RQ-15-02 | WP-15-01, WP-15-02 |
| threat scenario identification | 15.4 | threat scenarios, each naming an asset, a property and a cause | none | EVITA, TVRA, PASTA and STRIDE as examples | RQ-15-03 | WP-15-03 |
| impact rating | 15.5 | each damage scenario, in each category S, F, O, P | severe, major, moderate, negligible | Annex F (examples); safety ratings must come from ISO 26262-3 (RQ-15-06) | RQ-15-04 to RQ-15-06, PM-15-07 | WP-15-04 |
| attack path analysis | 15.6 | attack paths, each linked to the threat scenarios it realizes | none | top-down (attack trees, attack graphs) or bottom-up (from vulnerabilities) | RQ-15-08, RQ-15-09 | WP-15-05 |
| attack feasibility rating | 15.7 | each attack path | High, Medium, Low, Very low | Annex G: attack potential, CVSS v3.1 or attack vector | RQ-15-10, RC-15-11 to RC-15-14 | WP-15-06 |
| risk value determination | 15.8 | each threat scenario, optionally per damage scenario and category | 1 to 5 | Annex H: a risk matrix or a risk formula | RQ-15-15, RQ-15-16 | WP-15-07 |
| risk treatment decision | 15.9 | each threat scenario | avoid, reduce, share, retain | | RQ-15-17 | WP-15-08 |

Related: a cybersecurity goal can carry a CAL (CAL1 to CAL4 in Annex E's example, where it is set from impact and attack vector; §3.3).

## 1. The standard and how we use it

### 1.1 What it is

ISO/SAE 21434:2021, *Road vehicles: Cybersecurity engineering*, is a joint standard of ISO and SAE International. ISO's road-vehicle subcommittee for electrical and electronic components and general system aspects (ISO/TC 22/SC 32) prepared it together with SAE's Vehicle Cybersecurity Systems Engineering Committee (TEVEES18A). It is the first edition, and it replaces SAE J3061:2016, with content and structure completely reworked (Foreword; library record `sae-j3061`).

**What it covers:**
- Requirements for managing cybersecurity risk in a road vehicle's electrical and electronic (E/E) systems, their components and their interfaces, over the whole lifecycle, from concept and product development through production, operation and maintenance to decommissioning (Clause 1).
- Process requirements, plus a common vocabulary so that the organizations in a supply chain can communicate and manage cybersecurity risk the same way (Clause 1; Introduction).
- Only series-production E/E systems (with their components and interfaces) that were developed or modified after the standard was published (on 2021-08-31, per ISO Open Data) (Clause 1).

**Its unit of analysis is the item, or a component.** An item is all the electronics and software in a vehicle that together realize a specific vehicle-level functionality, such as braking; Figure 3 shows an item implementing one or more functions. The standard describes the engineering of one item at a time and does not say how to divide a vehicle's functions into items. For the vehicle as a whole, it points to the vehicle's E/E architecture, or to the combined cybersecurity cases of every cybersecurity-relevant item and component (Clause 4). The TARA methods apply to an item or a component (15.1), and components can also be developed out of context, without a known item (6.4.5).

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
| ISO 26262-3:2018 | Functional safety, Part 3: Concept phase | 90.92, to be revised | the only normative reference of ISO/SAE 21434 (Clause 2); a 3rd edition, titled Part 3: Product development at the item level, is in development as a draft International Standard (ISO/DIS 26262-3, stage 40.00); since Clause 2 cites the 2018 edition by date, that edition is the one that applies |
| ISO/SAE PAS 8475 | Cybersecurity assurance levels (CAL) and targeted attack feasibility (TAF) | 60.00, under publication | bears on assurance levels (Annex E) and attack feasibility (§3) |
| ISO/SAE TR 8477 | Cybersecurity verification and validation | 60.00, under publication | |
| ISO/PAS 5112:2022 | Guidelines for auditing cybersecurity engineering | 90.92, to be revised | a 2nd edition is in development as a draft Technical Specification (ISO/DTS 5112, stage 50.20); bears on audit automation (#19) |
| ISO 24089:2023 | Software update engineering | 60.60, published | amended by ISO 24089:2023/Amd 1:2024 |

The stage names come from ISO's harmonized stage codes. ISO's website refused automated access (HTTP 403), so the names are still pending a manual check on iso.org (searches.md).

### 1.3 How it is organized

- **Clauses 1 to 3:** scope, the one normative reference (ISO 26262-3:2018), and the vocabulary (terms in 3.1, abbreviations in 3.2).
- **Clause 4, general considerations:** context only. The Introduction calls it informational, and it has no provisions. It explains items, risk management across the supply chain and the lifecycle, and defence in depth.
- **Clauses 5 to 8** cover activities that span the lifecycle: organizational cybersecurity management (5), project-dependent management (6), activities split between customer and supplier (7), and continual activities such as monitoring and vulnerability management (8).
- **Clauses 9 to 14** follow the lifecycle's phases: concept (9), product development (10), validation (11), production (12), operations and maintenance (13), and end of cybersecurity support and decommissioning (14).
- **Clause 15, the TARA methods:** building blocks that the activities in other clauses call when they need a risk assessment (Introduction; Clause 4). Most of the objects in §5 come from here.
- **Annexes A to H,** all informative (guidance, not requirements): a summary of activities and work products (A), cybersecurity culture (B), an interface agreement template (C), cybersecurity relevance (D), cybersecurity assurance levels (E), impact rating (F), attack feasibility rating (G), and a worked TARA example for a headlamp system (H).

**Provisions and work products.** Clauses 5 to 15 each give objectives, provisions and work products (Introduction). A provision is a requirement, a recommendation or a permission; every requirement in the standard uses "shall", every recommendation "should" and every permission "may" (searches.md, Tool runs). Work products are what the activities produce, and each one says what it results from: 32 name the provisions behind them (one also names a subclause), and 10 name subclauses only. Inputs are listed as prerequisites (mandatory work products from an earlier phase) or further supporting information (optional) (Introduction).

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

The counts match the library catalog (`iso-sae-21434-2021`, `distilled/requirements.yaml`), but 16 of its 118 provision texts are wrong or incomplete, and many of its work-product links are missing (§7).

**Why the identifiers matter for tmodel.** They give every obligation a stable key that does not depend on wording, and they link work products to the provisions or subclauses behind them. The library catalog already uses them as keys (for example `iso-sae-21434-2021#RQ-15-17`), and its distilled notes propose this requirement-to-work-product structure as the template for automating audits (`iso-sae-21434-2021`, `distilled/normative.md` §4). Automated compliance validation is issue #19.

### 1.4 Our copy and how we cite it

- **The copy.** We worked from the sponsor's purchased copy, the SAE-issued PDF of ISO/SAE 21434:2021 (87 PDF pages: the 81 numbered pages ISO counts, plus a cover, front matter and a back page; SHA-256 `73f990078d3a5b47dec91dd0d2b4e6c24cecd9e4160ae5b143c3b3fa80b7cdf4`, the digest in the library record and in #11). It stays on our machines and is never committed. Its text was extracted with `pdftotext` only to search and check it, and the extract also stays outside the repository (searches.md).
- **Citations.** Clause and subclause numbers (15.9), provision and work-product identifiers (RQ-15-17, WP-15-08), and table, figure and annex numbers (Table G.9, Figure 3). Unlike page numbers, these do not depend on the copy's layout.
- **Library links.** An identifier resolves in the library catalog as `iso-sae-21434-2021#RQ-15-17`. For the entries listed in §7, read the standard instead until the catalog is fixed.

**Takeaway:** ISO/SAE 21434 is a process standard for one item, or component, at a time. It says which activities must happen and which work products must exist, and it leaves the choice of technology, specific tools and data formats to the user, though it requires tools that can affect cybersecurity to be managed (RQ-05-14). Its RQ, RC, PM and WP identifiers give tmodel ready-made keys for requirements and evidence. The 2021 first edition is the current one: ISO lists it as under systematic review with no replacement project yet, while the companion PAS 8475 on assurance levels and targeted attack feasibility is under publication.

## 2. TARA step by step

Clause 15 defines TARA as a set of methods, together with their work products, for working out how far a threat scenario can affect road users, carried out from the point of view of the road users affected (15.1). The methods are generic modules: other clauses call them, at any stage of an item's or component's lifecycle, and their work products are recorded inside those clauses' work products (15.1). An organization can use its own scales for impact, attack feasibility and risk, mapped onto the standard's scales (15.1). Annex H walks through the methods with an example (§4).

### 2.1 The vocabulary

The terms TARA is built from, in our words. Clause 3.1 defines 40 terms in all.

| term | meaning | defined in |
|---|---|---|
| asset | something that has value or contributes to it; it has one or more cybersecurity properties, and compromising them can lead to damage scenarios | 3.1.2 |
| cybersecurity property | an attribute that can be worth protecting, such as confidentiality, integrity or availability | 3.1.20 |
| damage scenario | a harmful consequence that involves a vehicle or a vehicle function and affects a road user | 3.1.22 |
| road user | anyone who uses a road, for example passengers, pedestrians, cyclists, motorists and vehicle owners | 3.1.31 |
| threat scenario | a possible cause of compromise of one or more assets' cybersecurity properties, leading to a damage scenario | 3.1.33 |
| attack path | the set of deliberate actions that realizes a threat scenario; "attack" is an accepted synonym | 3.1.4 |
| attacker | whoever carries out an attack path: a person, a group or an organization | 3.1.5 |
| attack feasibility | how easily the actions of an attack path can be carried out successfully; a property of the path | 3.1.3 |
| impact | an estimate of how much damage or physical harm a damage scenario causes | 3.1.24 |
| risk | the effect of uncertainty on a road vehicle's cybersecurity, described by attack feasibility and impact | 3.1.29 |
| cybersecurity goal | a cybersecurity requirement at concept level, tied to one or more threat scenarios | 3.1.16 |
| cybersecurity claim | a statement about a risk, which can justify retaining or sharing it | 3.1.12 |
| cybersecurity control | a measure that modifies risk (adapted from ISO 31000) | 3.1.14 |
| weakness | a flaw or trait that can cause unwanted behaviour, such as a missing requirement, a design flaw or an implementation defect | 3.1.40 |
| vulnerability | a weakness that an attack path can exploit (adapted from ISO/IEC 27000) | 3.1.38 |

Several terms the steps rely on are not defined in 3.1, among them *impact rating*, *impact category*, *attack feasibility rating*, *risk value* and *risk treatment*. Their meaning comes from the provisions in 15.5, 15.7, 15.8 and 15.9. The standard never uses the phrase "attack step": an attack path is a set of actions, and the example in 15.6 lists them in order. Informative Annex G does speak of the distinct steps of an attack (G.2.2).

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

Clause 15 lists the methods in this order, but they are modules that other clauses call when needed (15.1); RQ-09-03, for example, runs six of them together (§2.10). The only fixed order comes from the prerequisites. Impact rating needs damage scenarios, attack path analysis needs threat scenarios, feasibility rating needs attack paths, the risk value needs threat scenarios and both kinds of rating, and the treatment decision needs risk values.

### 2.3 Asset identification (15.3)

- Despite the step's name, its first provision asks for damage scenarios (RQ-15-01). The second asks for the assets, with their cybersecurity properties, whose compromise leads to those damage scenarios (RQ-15-02).
- A damage scenario can describe how the item's function relates to the harm, the harm to the road user, and the assets involved (NOTE 1).
- Assets can be found by analysing the item definition, by doing an impact rating, by working back from threat scenarios, or from predefined catalogues (NOTE 2).
- The two examples: personal data stored in an infotainment system, whose loss of confidentiality leads to the damage scenario of its disclosure without the customer's consent; and the data communication of the braking function, whose loss of integrity causes unintended full braking at high speed and a rear-end collision.

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
  - **attack vector:** based on the predominant attack vector of the path, in the CVSS sense (RC-15-14). It can suit early phases, such as the concept phase, when specific attack paths cannot be identified yet (NOTE 6). Guidance: G.4.
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

Found by searching Clauses 4 to 14 for references to 15.3 to 15.9, to "Clause 15", to the Clause 15 work products, and to "TARA" (searches.md, Tool runs).

| where | how it uses TARA | provisions |
|---|---|---|
| 9.4, cybersecurity goals (concept phase) | Runs steps 15.3 to 15.8 on the item (RQ-09-03), then 15.9 for every threat scenario (RQ-09-04); together these form the TARA work product (WP-09-02). Missing item information can be assumed (NOTE 1). Reducing a risk requires one or more cybersecurity goals (RQ-09-05), and a CAL can be set for a goal (NOTE 4, Annex E). Sharing a risk, or retaining it because of assumptions made in the analysis, requires cybersecurity claims (RQ-09-06). Avoiding a risk by removing its source can change the item (NOTE 2). A verification checks the analysis, the decisions, the goals and the claims (RQ-09-07). | RQ-09-03 to RQ-09-07; WP-09-02 to WP-09-05 |
| 9.5, cybersecurity concept | Can use the TARA as supporting input (9.5.1.2). | |
| 6.4, project management | The cybersecurity plan must specify the activities required by Clauses 9, 10, 11 and 15 (RQ-06-06), and can be updated from TARA results (RQ-06-07, NOTE 4). Threat scenarios with risk value 1 (from 15.8) need not conform to 9.5 or to Clauses 10 and 11 (PM-06-08); if they still have cybersecurity consequences, their risks are treated, possibly with less rigour (NOTE 5). A reuse analysis must identify affected or missing work products, and its example of one is a TARA covering assets, threat scenarios or risk values that are new or have changed (RQ-06-16, EXAMPLE 4). The decision whether to do a cybersecurity assessment can rest on TARA results (RQ-06-24, NOTE 1). | RQ-06-06, RQ-06-07, PM-06-08, RQ-06-16, RQ-06-24 |
| 5.4, organizational management | The organization's rules and processes include the TARA methods (RQ-05-02, NOTE 4). | RQ-05-02 |
| 7.4, distributed activities | What customer and supplier share can include how changes are communicated, including a possible rerun of the TARA (RQ-07-04, NOTE 1). | RQ-07-04 |
| 8.3 and 8.4, monitoring and event evaluation | Threat scenarios and cybersecurity claims can inform monitoring (8.3.1.2), and threat scenarios can be updated after an event is evaluated (RQ-08-04, NOTE 3). | RQ-08-04 |
| 8.5, vulnerability analysis | Attack paths can be an input (8.5.1.2). Whether a weakness is a vulnerability can be decided with attack path analysis (15.6) and feasibility rating (15.7) (RQ-08-05, NOTE 1). The examples show a weakness not being treated as a vulnerability because no attack path exists, or because its feasibility is very low (EXAMPLES 1 and 2), and every weakness not treated as a vulnerability needs a rationale (RQ-08-06). | RQ-08-05, RQ-08-06 |
| 8.6, vulnerability management | For each vulnerability, either its risks are assessed and treated through 15.9 until no unreasonable risk remains, or it is removed by an available remediation without a TARA (RQ-08-07). If a treatment decision needs incident response, 13.3 applies (RQ-08-08), and incident response can also run without a TARA (NOTE 3). | RQ-08-07, RQ-08-08 |
| 11.4, validation | Validation at the vehicle level must confirm, among other things, that the cybersecurity goals are adequate for the threat scenarios and their risk (RQ-11-01, item a). Risks found during validation that no goal addresses can be taken back to 9.4 (NOTE 1). | RQ-11-01 |

Clauses 10 to 14 never cite Clause 15, its subclauses or its work products by number. Besides RQ-11-01, Clauses 10 and 11 build on concept-phase outputs that rest on the TARA: the cybersecurity concept (WP-09-06) in both, and the cybersecurity goals and claims (WP-09-03, WP-09-04) in Clause 11. Clauses 12 to 14 cite no concept-phase work product. Clause 13 is reached from Clause 8 instead: RQ-08-08 sends treatment decisions that need incident response to 13.3 (searches.md, Tool runs).

**Takeaway:** TARA produces a chain of linked objects: assets with cybersecurity properties, damage scenarios rated per impact category, threat scenarios that name an asset, a property and a cause, attack paths rated for feasibility, risk values from 1 to 5, and treatment decisions that lead to cybersecurity goals, cybersecurity claims or a change to the item. Each rating attaches to a specific object: impact to a damage scenario in each category, feasibility to an attack path, and risk to a threat scenario, optionally split by damage scenario and category. The standard fixes the scales but not the formula that combines them, and it rates each attack path as a whole: no provision rates or combines the individual actions inside a path. Section 5 maps these objects onto the proposed object model, and section 6 compares the risk rules with the metric in ARCH-0001-PROPOSAL.

## 3. Rating scales and methods (Annexes E, F and G)

All three annexes are informative, and their tables are examples. For impact and attack feasibility, an organization can apply its own scales, mapped onto the standard's (15.1); Annex E's CAL scheme is likewise only an example. Annex G calls its point values a proposal "based on" ISO/IEC 18045 (G.2.2.6), and Annex E says its Tables E.2 to E.4 are there so that industry can gain experience with CALs (E.3.1). The numbers below are those example values, not requirements. They were checked against the PDF, including page images for Tables E.1, G.6 and G.7, whose layout does not survive text extraction (searches.md, Tool runs).

### 3.1 Impact criteria (Annex F)

Annex F gives one example table per impact category (Tables F.1 to F.4). In our words:

| level | safety (Table F.1) | financial (Table F.2) | operational (Table F.3) | privacy (Table F.4) |
|---|---|---|---|---|
| severe | ISO 26262 class S3: fatal or life-threatening injuries, survival uncertain | harm the road user might not recover from | a core vehicle function is lost or impaired | significant or irreversible harm; highly sensitive information that is easy to link to the person |
| major | S2: severe and life-threatening injuries, survival probable | serious harm the road user can recover from | an important vehicle function is lost or impaired | serious harm; highly sensitive but hard to link, or sensitive and easy to link |
| moderate | S1: light and moderate injuries | inconvenient harm, recoverable with limited resources | a vehicle function is partly degraded | inconvenient consequences; sensitive but hard to link, or non-sensitive and easy to link |
| negligible | S0: no injuries | no or negligible effect, or irrelevant to the road user | no impairment, or none the user would notice | no or negligible effect; not sensitive and hard to link |

- **Safety** reuses ISO 26262-3:2018's severity classes, and that standard's controllability and exposure can also be considered if a rationale is given (F.2).
- **Operational** examples are a vehicle that does not work or whose core functions behave unexpectedly, for example by entering limp-home mode (severe), significant annoyance of the driver (major), and lower user satisfaction (moderate). Operational damage may or may not also have safety consequences (F.4).
- **Privacy** levels pair a consequence for the road user, from significant or irreversible down to none, with a grid of two questions: how sensitive the information is (highly sensitive, sensitive, not sensitive), and how easily it links to the person it is about, the "PII principal" of ISO/IEC 29100 (F.5).
- **Scale of damage** is left out. The examples do not cover one damage scenario hurting many road users at once, but an organization can add that to its own criteria (F.1, citing EVITA).

### 3.2 Attack feasibility: the three methods (Annex G)

Annex G gives guidance for each of the three approaches in RC-15-11. For any of them, whether an attack can scale, meaning it extends easily to many instances and targets, may also count in the rating (G.1).

**Attack potential (G.2).** Attack potential, a concept from ISO/IEC 18045, measures the effort an attack takes in terms of the attacker's expertise and resources (G.2.1). The five factors, their levels, and the example points of Table G.6:

| factor | what it measures | levels and points (Table G.6) |
|---|---|---|
| elapsed time | time to find the vulnerability and to develop and apply an exploit, judged by what experts know at the time of rating (G.2.2.1) | ≤1 day 0, ≤1 week 1, ≤1 month 4, ≤6 months 17, >6 months 19 |
| specialist expertise | the attacker's skill and experience; "multiple experts" means distinct steps of the attack need experts in different fields (G.2.2.2) | layman 0, proficient 3, expert 6, multiple experts 8 |
| knowledge of the item or component | the information the attacker has about the item or component, graded by how closely it is held (G.2.2.3) | public 0, restricted 3, confidential 7, strictly confidential 11 |
| window of opportunity | the access the attack needs: logical or physical, limited or unlimited in time (G.2.2.4) | unlimited 0, easy 1, moderate 4, difficult/none 10 |
| equipment | the tools needed; "multiple bespoke" means distinct steps need different bespoke equipment (G.2.2.5) | standard 0, specialized 4, bespoke 7, multiple bespoke 9 |

The points of all five factors are added (G.2.2.6, following ISO/IEC 18045), and Table G.7 maps the total to a rating: **0 to 13 is High** (the table lists two bands, 0 to 9 and 10 to 13, both High), 14 to 19 Medium, 20 to 24 Low, and 25 or more Very low. More points mean more effort, so a higher total means a lower feasibility. By our arithmetic, totals run from 0 to 57.

**CVSS (G.3).** Only the four exploitability metrics of the CVSS base group are used: attack vector, attack complexity, privileges required and user interaction. The other CVSS metrics, such as impact, are covered by other parts of the standard, for example damage scenarios and impact rating (G.3).
- The exploitability value is E = 8.22 × AV × AC × PR × UI, the product of the four metric weights times 8.22, which gives values from 0.12 to 3.89 (G.3). This is the exploitability equation of CVSS v3.1 (FIRST's v3.1 specification, 7.1), the version the standard cites (Bibliography [24]). FIRST's v3.1 metric weights reproduce the 0.12 to 3.89 range (searches.md, Tool runs).
- Table G.8 cuts that range into four equal steps: 2.96 to 3.89 High, 2.00 to 2.95 Medium, 1.06 to 1.99 Low, 0.12 to 1.05 Very low.
- A NOTE says that using only the exploitability metrics does not strictly follow CVSS's own rules, and lets the standard's impact rating (Annex F) stand in for the missing impact part (G.3).
- An organization can supplement the metric descriptions with its own examples, keeping the metric values unchanged. The metrics can rate conceptual weaknesses, flaws and gaps, not only vulnerabilities (G.3).
- **CVSS v4.0 does not fit this method directly** (our finding, from FIRST's specifications). Version 4.0 has five exploitability metrics, adding attack requirements (AT); it scores through MacroVector lookup tables with interpolation; and its specification defines no exploitability equation or subscore. A v4.0 vector therefore cannot be put through E and Table G.8 as they stand (searches.md, Tool runs).

**Attack vector (G.4).** The more remote an attacker can be, logically and physically, the higher the feasibility, on the assumption that more people can attack over the internet than with physical access (G.4). Table G.9:

| attack vector | rating | meaning, with the standard's example |
|---|---|---|
| network | High | reachable through the network stack without limits, e.g. an ECU on the internet through a cellular connection |
| adjacent | Medium | through the network stack, but only over a physically or logically limited connection, e.g. Bluetooth or a VPN |
| local | Low | not through the network stack; the attacker needs direct access to the item, e.g. a USB storage device or a memory card |
| physical | Very low | the attacker needs physical access |

The four values are the CVSS attack vector values, given automotive examples. RC-15-14 asks for the path's predominant attack vector, and NOTE 6 says this approach can be suitable in early phases, such as the concept phase, when specific attack paths cannot be identified yet (§2.7).

**Side by side:**

| approach | input per attack path | output before mapping | when the standard suggests it |
|---|---|---|---|
| attack potential (G.2) | five factor levels | points, 0 to 57 | no phase given |
| CVSS (G.3) | four CVSS v3.1 exploitability metrics | E, 0.12 to 3.89 | no phase given |
| attack vector (G.4) | one attack vector | none: maps straight to a rating | early phases, such as the concept (RC-15-14, NOTE 6) |

### 3.3 Cybersecurity assurance levels (Annex E)

- **What a CAL is.** A level of rigour for assurance activities, giving confidence that the protection of an item's or component's assets is adequately developed. It gives organizations a common language for assurance requirements and sets no technical requirements for controls (E.1).
- **Who sets it.** The organization developing the item, or, for an out-of-context component, the component's developer, by assumption (E.1).
- **Where it lives.** A CAL can be an attribute of a cybersecurity goal, inherited by the cybersecurity requirements refined from the goal (E.1; E.3.2). An item can have one CAL for all its goals or one per goal, and goals that are combined take the highest of their CALs (E.2). A component that receives requirements with different CALs takes the highest; one shown to be isolated from the other components can have its CAL lowered or dropped, with a rationale (E.3.2).
- **Why it is not a risk value.** A CAL relates to risk only indirectly. The risk value changes as the specification, design, implementation and operational environment change, while a CAL is meant to stay fixed. So a CAL can be chosen early, in the concept phase, from parameters expected to stay stable until the end of cybersecurity support, before controls are considered (E.2). Figure E.1 shows this: the risk value falls when a control is shown to work, rises when a vulnerability is found in the field, and falls again when it is fixed, while the CAL set at the start does not move.
- **Example determination (Table E.1),** using two inputs from the threat scenarios concerned: their highest impact rating and their attack vector. A table note calls attack vector a static feasibility parameter.

| impact | physical | local | adjacent | network |
|---|---|---|---|---|
| severe | CAL2 | CAL3 | CAL4 | CAL4 |
| major | CAL1 | CAL2 | CAL3 | CAL4 |
| moderate | CAL1 | CAL1 | CAL2 | CAL3 |
| negligible | none: a dash, pointing to PM-06-08 | none | none | none |

- **What it scales.** The methods used for development and verification, the methods for finding weaknesses and analysing vulnerabilities, and the approach to cybersecurity assessment (E.3.1). The examples suggest a level of independence per activity, from a different person (I1) to a person independent of the originating department in management, resources and release authority (I3) (Table E.3), and which testing parameters apply to functional testing, vulnerability scanning, fuzz testing and penetration testing (Table E.4).
- ISO/SAE PAS 8475, on CALs and targeted attack feasibility (TAF), is under publication (§1.2). We have not read it.

**Takeaway:** Every scale in the annexes is an example. The raw values (attack potential points, a CVSS v3.1 exploitability value, an attack vector) only mean something with the method that produced them; the final four-level rating has one definition whatever the method (Table 1), so the method behind each rating is worth recording. The CVSS route is tied to v3.1 and does not take CVSS v4.0 vectors as they are. Privacy levels combine the consequence for the road user with two properties of the data, its sensitivity and its linkability. A CAL behaves differently from risk: it can be set early and is meant to stay fixed; it can be attached to cybersecurity goals; requirements inherit their goal's CAL, while components and combined goals take the highest CAL they receive. Section 5 looks at what these facts mean for the object model.

## 4. Worked example: the Annex H headlamp system

Annex H illustrates the TARA methods on a headlamp system. It is for illustration only, covers just the concept phase (item definition and TARA), and is simplified (H.1). It says the methods can run in any order and gives two sample orders; the example itself goes from assets to impact rating, threat scenarios, attack paths, feasibility, risk value and treatment (H.1). Figure H.1 shows the concept-phase wiring from §2.10: RQ-09-03 calls 15.3 to 15.8, RQ-09-04 calls 15.9, and RQ-09-05 specifies cybersecurity goals when a decision includes reducing the risk. Every page of Annex H with a figure or table (PDF pages 77 to 83) was checked as a page image (searches.md, Tool runs).

### 4.1 The item

- **Function.** The system switches the headlamps on and off when the driver uses the switch. In high-beam mode it dips to low beam automatically when it detects an oncoming vehicle, and returns to high beam once that vehicle is no longer detected (H.2.1). The headlamp function does not depend on the navigation or gateway ECUs (H.2.1, NOTE).
- **Inside the item boundary** (Figure H.2): a headlamp switch, a body control ECU, a camera ECU, a power switch actuator and the lamps. Two signals matter: the lamp request (low, high or off) from the body control ECU to the power switch actuator, and the oncoming car information (yes or no) from the camera ECU.
- **Outside the boundary, in the operational environment** (Figure H.2, Table H.1): a gateway ECU connected to the item and to a navigation ECU. Other ECUs connect to the gateway but are drawn outside the operational environment. The navigation ECU has Bluetooth and cellular interfaces; the gateway has an OBD-II connector. Two assumptions are recorded: the navigation ECU's firewall blocks invalid data from its external interfaces, and the gateway has strong controls, including a firewall, developed to CAL4 (Table H.1).

### 4.2 The chain, step by step

| step | what the example produces | source |
|---|---|---|
| assets | Three assets: the lamp request communication (integrity, availability), the oncoming car information communication (integrity, availability), and the body control ECU's firmware (confidentiality, integrity; its damage scenario is left out). Four damage scenarios are written out, for example a front collision with a tree when the headlamps switch off while driving at night at medium speed. | Table H.2 |
| impact rating | Three damage scenarios rated, each in one category: the collision S, severe (S3); a vehicle that cannot be driven at night since the headlamps seem disabled while parked O, major; automatic high beam stuck on low beam O, moderate. | Table H.3 |
| threat scenarios | Two for the collision: spoofing the lamp request signal, and tampering with the signal the body control ECU sends, either of which can switch the headlamps off. One for the automatic high beam that stays on low beam, written as RQ-15-03's three elements: asset oncoming car information, property availability, cause denial of service. | Table H.4 |
| attack paths | Spoofing has three 4-step paths into the navigation ECU (through its cellular or its Bluetooth interface) or into the OBD connector (local access), then through the gateway to the power switch actuator. Denial of service has a 4-step path through cellular and a 5-step path through a Bluetooth OBD dongle and the driver's compromised smartphone, both ending in flooding the bus. Tampering gets no paths. Paths that require getting physically inside the item, for example to the body control ECU's microcontroller, are excluded by assumption (H.2.5). | Table H.5, Figure H.3 |
| attack feasibility | Spoofing paths, by attack vector (G.4): cellular High, Bluetooth Medium, OBD Low. This approach suits the concept phase, when not all vulnerability information can be known (NOTE 1). Denial-of-service paths, by attack potential (G.2): 1 + 8 + 7 + 0 + 4 = 20 points and 1 + 8 + 7 + 4 + 4 = 24 points, both Low. The second path's window of opportunity is 4 (moderate) because it needs physical access (NOTE 2). | Tables H.6, H.7 |
| risk value | The two threat scenarios that have attack paths get a feasibility aggregated over their paths (spoofing High, denial of service Low), combined with their impact through the example risk matrix below: spoofing gets "S: 5", denial of service "O: 2". The example formula R = 1 + I × F, with I and F set to 0, 1, 1.5 or 2 for the four impact and feasibility levels, gives the same two values. | Tables H.8 to H.10 |
| treatment | Both threat scenarios: reduce the risk. The example ends here; it shows no cybersecurity goals or claims. | Table H.11 |

The example risk matrix (Table H.8):

| impact | very low | low | medium | high |
|---|---|---|---|---|
| severe | 2 | 3 | 4 | 5 |
| major | 1 | 2 | 3 | 4 |
| moderate | 1 | 2 | 2 | 3 |
| negligible | 1 | 1 | 1 | 1 |

### 4.3 What the example shows that the clauses do not

1. **Two feasibility methods in one analysis.** One threat scenario's paths are rated by attack vector and the other's by attack potential (Tables H.6, H.7), and both end up in the same risk table (Table H.9). Annex H presents attack potential as an alternative (H.2.6); the standard does not say whether mixing methods is acceptable, and RC-15-11 recommends basing the method on one approach.
2. **Aggregation by the highest rating.** The spoofing threat scenario takes High from its High, Medium and Low paths (Tables H.6 and H.9), the example given in RQ-15-15, NOTE 2.
3. **Risk values labelled by category.** Each value carries its impact category ("S: 5", "O: 2"; Table H.9), in line with RQ-15-15, NOTE 1. Each threat scenario here has only one rated category, so the example never shows a threat scenario with several risk values.
4. **The matrix and the formula do not agree everywhere.** The standard only says they give the same values for the two threat scenarios shown. Over all 16 combinations, by our arithmetic, they agree on 12 and differ on 4: severe with very low feasibility (formula 1, matrix 2), major with low (2.5 and 2), major with medium (3.25 and 3), and moderate with medium (2.5 and 2). Three of the four formula results are not whole numbers, and the standard gives no rounding rule. RQ-15-16 asks for a value from 1 to 5 without saying it must be a whole number.
5. **The tables are not fully consistent.** Table H.6 has the spoofing paths switch the lamp request "ON" and gives the OBD path three steps. Table H.5 says "OFF" for all three paths, as does Figure H.3 for the cellular one, which matches the threat scenario, and gives the OBD path four steps. The spoofing threat scenario is worded the same in Tables H.4 and H.5, but Tables H.9 and H.11 shorten it and drop the clause about the headlamp switching off, and Figure H.3 has a third variant.
6. **Assumptions shape the analysis.** Paths that require getting physically inside the item are excluded according to an assumption (H.2.5), though Table H.1 does not list that assumption. Annex H never says how the firewall and CAL4 assumptions of Table H.1 affect any path or rating.
7. **The example is partial.** The damage scenario of a vehicle that cannot be driven at night is rated but gets no threat scenario; the one about dazzled oncoming drivers gets neither a rating nor a threat scenario; the firmware asset's damage scenario is left out; and the tampering threat scenario gets no attack paths, rating, risk value or treatment.

### 4.4 As a candidate test case for #17

Counted from the tables and figures: one item with five kinds of components inside the boundary, two named ECUs and three external interfaces outside it, 3 assets, 4 written-out damage scenarios, 3 impact ratings, 3 threat scenarios, 5 attack paths with 21 steps between them as listed in Table H.5 (20 with Table H.6's version of the OBD path), 5 feasibility ratings (3 by attack vector, 2 by attack potential), 2 risk values and 2 treatment decisions. The expected results a test could check are the two aggregated ratings (High, Low), the two risk values (5 and 2, by matrix and by formula) and the two decisions (reduce, reduce). Under the library's full-extraction standard (FX-1), every example in a spec record that a pull request touches becomes a fixture file with expected results, unless it is marked not applicable with a reason. For this licensed standard, a fixture would have to be written in our own words. Turning this one into a fixture would first need the inconsistencies in item 5 resolved, and links between rows by identifier, since the wording drifts between tables. ADR-0004 already requires one stable ID for every object and edge.

Our suggestion for the Table H.5 and H.6 conflict in item 5, if the sponsor makes this a fixture: take Table H.5 as the reference (lamp request OFF, a four-step OBD path), since it fits the threat scenario, in which the headlamp turns off, and so does Figure H.3, which draws only the cellular path; record Table H.6's version as a known discrepancy. The choice changes none of the expected results. Each spoofing path is rated by its predominant attack vector (RC-15-14), and in both tables the OBD path starts at the OBD connector, which Table H.5 marks as local access (Table G.9), so the ratings stay High, Medium and Low, and the aggregate, the risk value and the decision stay High, 5 and reduce. Only the lamp state and the step count (21 or 20) differ.

**Takeaway:** The example walks the whole chain on a small system and confirms the shapes from §2: ratings on paths, aggregation per threat scenario, and a risk value labelled by impact category. It also shows what the clauses leave open. The example rates its two threat scenarios with different methods and combines them in one table, although the standard does not say whether that is acceptable. The example risk formula and risk matrix are not interchangeable in general. And the standard does not say whether a risk value must be a whole number, while the example formula gives fractions for 3 of the 16 combinations. Its small inconsistencies are a reason to link the objects by identifier, not by text.

## 5. TARA objects mapped onto the proposed object model

This section lines up the objects ISO/SAE 21434 uses with the types in ARCH-0001 §3 (v0.1.6, the current working labels) and in ARCH-0001-PROPOSAL v0.2.0 (`0.2.0-proposed.10`, the DEC-001 synthesis for #15). It is evidence for #15 and #17, not a model of its own: where the standard and the models differ, it says so and leaves the choice to DEC-001. ADR-0002 expects this mapping, with the ISO 21434 object model binding onto the shared graph.

The mapping was first made against `proposed.7` and, as the sponsor asked on PR #69, remapped after #66 and #77 merged. `proposed.8` to `proposed.10` add parties with asset owners, a lifecycle-phase axis, a separate business-impact axis, a rule for how many risk values a threat gets, risk as a vector with a mitigation status and display rules, and a list of schema classes (proposal §2b, §3, §3b, §13; DL-0008, DL-0010, DL-0011). The remap changed no object's fit; the table and §5.3 say what changed within the rows, and §6.2 checks the new risk rules.

### 5.1 The standard's own object model

Figure 3 relates ten things through thirteen labelled edges. Each row reads an arrow from its tail to its head, with the label as drawn. The figure was checked on a zoomed page image, because the direction of three arrows matters (searches.md, Tool runs).

| from | edge | to |
|---|---|---|
| item | implements | function(s) |
| item | consists of | component |
| item | contains | asset |
| cybersecurity property | attribute of | asset |
| cybersecurity goal | protects | asset |
| cybersecurity goal | associated with | item |
| cybersecurity goal | associated with | threat scenario |
| cybersecurity goal | realized by | cybersecurity requirement |
| cybersecurity requirement | allocated to | item |
| cybersecurity requirement | allocated to | component |
| threat scenario | compromises | cybersecurity property |
| threat scenario | realizes | damage scenario |
| damage scenario | affects | road user |

The definition of item agrees with the first row: one or more components that together provide a vehicle-level function (3.1.25). The library's distilled notes state three of these edges with a different meaning (one reversed, two starting from the wrong node) and write two more the other way round with the same meaning (§7).

Clause 15, Clause 9 and the annexes add relations the figure does not draw:

| relation | source |
|---|---|
| a threat scenario names its targeted asset, the compromised property and the cause | RQ-15-03 |
| damage scenarios and threat scenarios are many-to-many | 15.4, NOTE 3 |
| a damage scenario gets one impact rating for each category assessed (S, F, O, P) | RQ-15-04, RQ-15-05, PM-15-07 |
| an attack path is linked to every threat scenario it can realize | RQ-15-09 |
| each attack path gets one feasibility rating; the method should follow one of three approaches | RQ-15-10; RC-15-11 |
| a threat scenario gets one or more risk values, each from 1 to 5 | RQ-15-15, NOTE 1; RQ-15-16 |
| a threat scenario gets one or more treatment options: avoid, reduce, share, retain | RQ-15-17 |
| reducing a risk leads to cybersecurity goals; sharing it, or retaining it because of assumptions, leads to cybersecurity claims | RQ-09-05, RQ-09-06 |
| a goal can carry a CAL, which its requirements inherit; a component takes the highest CAL it receives | E.1, E.2, E.3.2 |
| an item has an operational environment, whose description can include assumptions | RQ-09-02, NOTE 8 |
| an attacker carries out an attack path | 3.1.5 |
| a weakness counts as a vulnerability only if an attack path can exploit it | 3.1.38; RQ-08-05, EXAMPLE 1 |
| each work product results from one or more provisions | §1.3 |

### 5.2 The mapping

**Fit:** *same* means the same meaning; *close* means the same idea with something missing; *partial* means the meanings only overlap; *none* means there is no type; *extension* means the model has something 21434 does not.

| ISO/SAE 21434 | ARCH-0001 §3 (v0.1.6) | ARCH-0001-PROPOSAL (proposed.10) | fit | what differs |
|---|---|---|---|---|
| component | Component | Component, with `composed_of` | same | |
| asset | Asset | Asset, named but not defined: `classification` (R-029, §6) and an owner, `owned_by` a Party (§2b, §3), modeled but not built for the MVP (§7); not in §13's list of schema classes | close | 21434 gives each asset its cybersecurity properties (3.1.2); neither model records them, and neither has the item-contains-asset edge. 21434 has no asset owner |
| cybersecurity property | none | `violates_property`, the security property each STRIDE category violates (§2) | partial | this records the property a threat violates, which matches the `compromises` edge, but not the properties an asset has. Its values come from STRIDE and add authentication, non-repudiation and authorization; 21434's examples are confidentiality, integrity and availability, as an open list (3.1.20) |
| damage scenario | none | DamageScenario, the target of `realizes` (§1) and one of §13's schema classes | close | no attributes yet; in 21434 it also affects a road user and carries the impact ratings (RQ-15-05) |
| road user | none | none as a type; §3 keeps S, F, O and P fixed to the "end-beneficiary" (road user, data subject or end-user) | none | the party a damage scenario harms (3.1.22): a person who uses a road, for example a passenger, a cyclist or the vehicle owner (3.1.31). TARA takes the viewpoint of affected road users (15.1) |
| impact rating, per category | part of Review: impact is a human judgement (§3) | per-category S, F, O, P impact, supplied by a human, as a field of the threat's risk record (§3, composite risk vector); post-MVP, a separate `business_impact` axis for the asset's owner (§3, R-039) | partial | 21434 attaches the rating to the damage scenario, per category (RQ-15-05). The proposal shows it on the threat's record and derives the risk from the threat's damage-scenario impact (proposal §3), but gives no rule for several damage scenarios of one threat scenario rated in the same category (15.4, NOTE 3); RQ-15-15, NOTE 1 would allow one value per rating instead. By our reading, the business-impact axis has no counterpart in 21434 for owners who are not road users (§6.2) |
| threat scenario | Threat, an adverse action against an asset | ThreatInstance, with `realizes` DamageScenario and a method facet (§1, §2) | close | 21434 also requires the targeted asset and the cause (RQ-15-03). ARCH-0001's Threat names an asset; the proposal generates threats from DFD elements, which resolve to components, and states no asset link, although its per-owner rule presumes that attack paths cross assets (proposal §3). Neither model has a separate cause field, though the threat itself, and in the proposal its STRIDE category, carries part of it |
| attack path | AttackPath / ThreatChain | AttackPath, made of AttackSteps | close | 21434 links each path to every threat scenario it can realize (RQ-15-09), and one path can realize several. The proposal's risk rule aggregates feasibility over "the set of attack paths realising the scenario" (proposal §3), which presumes that link, but neither model names an edge for it |
| (attack step) | AttackStep | AttackStep, with AND/OR gates and `precedes` ordering (§2a) | extension | 21434 defines no step object and rates only whole paths; it shows attack trees and graphs as analysis aids (15.6, NOTE 1; Figure H.3) and lists a path's actions in order (Table H.5) |
| attack feasibility rating | none | `attack_feasibility` on AttackPath, 4-point, human-rated at MVP, under the risk vector's display rules: a feasibility label, a colour and "concise metric numbers" (§3) | close | no field records the rating method or its inputs (factor levels, CVSS v3.1 metrics, attack vector); `source_method` records which threat method proposed a threat, not which rating method rated a path |
| attacker | none | ThreatActor, a generic catalog type (§1), and a facet of a Party, a person or an organization (§2b; modeled, not built for the MVP, §7) | partial | 21434's attacker is whoever carries out a path, a person, a group or an organization (3.1.5); neither model links an attacker to the paths it carries out |
| risk value | RiskScore | the derived `Risk = M(I, F)` (RiskScore): one per threat scenario and impact category, and post-MVP per affected owner, shown next to its inputs (§3) | same | the range 1 to 5 is fixed (RQ-15-16); whole numbers are not (§4.3). Values per owner have no counterpart in 21434 |
| risk treatment decision | none | MitigationInstance, which by our reading corresponds to reducing (§5, §7), and its status, a field of the risk record: planned, in-progress, complete, accepted-risk or n-a (§3) | partial | by our reading, `accepted-risk` is retaining. Avoiding and sharing have no home, and neither does the cybersecurity claim that records why a risk is retained or shared (RQ-15-17, NOTE); each option leads somewhere else (§2.9, §2.10) |
| cybersecurity control | Mitigation | Mitigation (D3FEND) and MitigationInstance | same | a measure that modifies risk (3.1.14) |
| cybersecurity goal | none | none | none | central to 9.4: created by reduce decisions, protects assets, can carry a CAL |
| cybersecurity claim | none | none | none | a statement about a risk (3.1.12). Not the proposal's `Assertion`, which records where a proposed node or edge came from (proposal §4) |
| cybersecurity requirement | none | none: the proposal's Requirement (post-MVP, #19; §7) is a different thing | none | in 21434 it realizes a goal and is allocated to an item or component (Figure 3); the proposal's Requirement belongs to the audit model, so the name clashes rather than matches |
| CAL | none | none | none | an attribute of a goal, inherited by requirements and components (Annex E) |
| weakness | Weakness (CWE) | Weakness (CWE) | partial | 21434's examples of weaknesses include a missing requirement and a flawed operational procedure (3.1.40), which may have no CWE entry |
| vulnerability | Vulnerability (CVE, NVD) | Finding / Vulnerability | partial | in 21434 a weakness becomes a vulnerability when an attack path can exploit it (3.1.38), whether or not a CVE exists |
| item | Product, the closest type | Product / ProductInstance, with `composed_of` | partial | an item implements one or more vehicle-level functions (3.1.25; Figure 3) and has a boundary (RQ-09-01); neither model has a unit scoped by function |
| function | none | Process / Workflow, DFD roles (§1) | partial | a 21434 function is the item's intended behaviour at vehicle level (RQ-09-01, NOTE 2); a DFD process is a behavioral role that components realize |
| operational environment | none | Environment, one per Deployment, post-MVP (§3, §7) | partial | 21434 describes it per item, with assumptions (RQ-09-02; Table H.1); neither model has a type for assumptions. 21434's operational use can include production and service and repair (3.1.26, Note 1), which the proposal, by our reading, files under lifecycle phases rather than Environment (proposal §3b) |
| provision and work product | none | Requirement / WorkProduct, post-MVP (#19; §7) | close | the RQ, RC, PM and WP identifiers can serve as keys (§1.3) |

Section numbers in the third column refer to ARCH-0001-PROPOSAL.

### 5.3 Gaps, both ways

**What 21434 needs that neither model has yet:**
1. Cybersecurity goals and claims, and the links from treatment decisions to them (RQ-09-05, RQ-09-06).
2. Avoiding and sharing as treatment options (RQ-15-17). Retaining now has a counterpart, by our reading, in the `accepted-risk` mitigation status, but not the cybersecurity claim that records its rationale (RQ-15-17, NOTE).
3. CALs on goals, and their inheritance by requirements and components (Annex E).
4. The cybersecurity properties of an asset, and the item-contains-asset edge (Figure 3).
5. A separate field for the threat scenario's cause, and, in the proposal, its link to the targeted asset (RQ-15-03), which the per-owner rule already presumes (proposal §3).
6. Road users as a type, and the impact rating on the damage scenario, where 21434 puts it (RQ-15-04, RQ-15-05); the proposal puts impact on the threat's risk record, with no rule yet for several damage scenarios of one threat scenario rated in the same category (15.4, NOTE 3).
7. The method and inputs behind each feasibility rating (RC-15-11 to RC-15-14; §3).
8. The item as a unit scoped by its functions, and its operational environment with assumptions (RQ-09-01, RQ-09-02).
9. An edge from each attack path to the threat scenarios it realizes (RQ-15-09), which the proposal's risk rule already presumes (proposal §3).

**What the proposal has beyond 21434:**
- Attack steps, AND/OR gates, ordering and shared steps stored as model data (proposal §2a). 21434 shows attack trees and graphs as analysis aids (15.6, NOTE 1; Figure H.3) but defines no step object and rates only whole paths, so step-level data would still have to yield one rating per path. The proposal already treats per-step aggregation as a post-MVP deviation from 21434 (proposal §3).
- Method facets. 21434 itself names STRIDE, with EVITA, TVRA and PASTA, as a way to identify threat scenarios (15.4, NOTE 2). The facet mechanism, LINDDUN and MAESTRO, provenance (`Assertion`, Review), VEX, the DFD layer, networks, redundancy and the view layer are outside its scope and do not conflict with it.
- Product families and the generic-to-instance mapping. 21434 works one item, or component, at a time.
- Parties and owners (modeled, not built for the MVP; proposal §2b, §3, §7). An Asset `owned_by` a Party selects whose `business_impact` applies, an axis assessed in addition to S, F, O and P, and risk is reported for each affected owner. 21434 names no asset owner; the owners it mentions are vehicle owners: one of its examples of a road user (3.1.31) and, in Annex G's examples, a possible attacker (Tables G.2, G.4). Its TARA takes the viewpoint of affected road users (15.1), and RQ-15-04, NOTE 2 allows additional impact categories in that assessment. Keeping S, F, O and P on the end-beneficiary, which includes the road user, as the proposal does since `proposed.9`, avoids a conflict (§6.2).
- A lifecycle-phase axis (R-037; proposal §3b). Its enum has a counterpart for each stage that 21434's Clauses 9 to 14 cover (concept, product development, validation, production, operations and maintenance, end of cybersecurity support and decommissioning, though the act of decommissioning is outside 21434's scope, 14.1), so the alignment the proposal claims holds at that level, by our reading. The enum also splits development into finer steps and adds distribution and deployment or commissioning, which have no phase of their own in 21434 (its production covers assembly up to the vehicle, 12.1); R-038 also calls returns, refurbishment and resale phases, though the enum as listed omits them. 21434 does not tag a threat scenario with a phase, since the TARA methods are modules that any phase can call (15.1), though goals may be set for any phase of the item's lifecycle (RQ-09-05, NOTE 5).
- Display rules for the risk vector: concise numbers, a feasibility label and a colour (proposal §3). 21434 sets no display rules.

**Names to watch:**
- A 21434 "claim" is not the proposal's `Assertion`.
- "Requirement" has three senses: an engineering cybersecurity requirement (Figure 3), a provision of the standard tagged RQ, and, by our reading, the proposal's audit-model Requirement (#19), which is the second sense.
- The "security properties" on the proposal's DFD elements (authenticated, encrypted, privilege; proposal §1) describe controls; 21434's cybersecurity properties are attributes that can be worth protecting (3.1.20).
- The ARCH-0001 "Threat" corresponds to a 21434 "threat scenario".
- "Owner": the proposal's asset owner is a Party whose business impact is kept apart from S, F, O and P; the owners 21434 mentions are vehicle owners, who count as road users (3.1.31) and appear as possible attackers in Annex G's examples (Tables G.2, G.4).
- "Table 1" is 21434's four-level feasibility scale (RQ-15-10), not a rating method; the methods are the three approaches of RC-15-11. The proposal calls it a method (proposal §3, §12; see §6.2).

### 5.4 Cardinalities the standard states

Rows that rest only on a NOTE or on informative Annex E are marked as such.

| relation | how many | source |
|---|---|---|
| damage scenario to threat scenario | many-to-many (a NOTE) | 15.4, NOTE 3 |
| attack path to threat scenario | many-to-many: a path is linked to every threat scenario it can realize, and a threat scenario can have several paths | RQ-15-09; RQ-15-15, NOTE 2 |
| threat scenario to asset | one or more | 3.1.33; RQ-15-03 |
| damage scenario to impact rating | one per category assessed: up to four (S, F, O, P), more if the organization adds categories, fewer when PM-15-07 applies | RQ-15-04, RQ-15-05, PM-15-07 |
| attack path to feasibility rating | one | RQ-15-10 |
| threat scenario to risk value | one or more; one per impact rating is allowed (a NOTE) | RQ-15-15, NOTE 1 |
| threat scenario to treatment option | one to four | RQ-15-17 |
| reduce decision to cybersecurity goal | one or more | RQ-09-05 |
| share or assumption-based retain decision to cybersecurity claim | one or more | RQ-09-06 |
| cybersecurity goal to CAL | at most one; combined goals take the highest (informative Annex E) | E.2 |
| component to CAL | can take the highest of the CALs it receives, or less if it is shown to be isolated (informative Annex E) | E.3.2 |

**Takeaway:** Of the 23 objects in the mapping table, not counting the attack step, 9 have the same or a close type in the proposal (`proposed.10`), 9 overlap only partly, and 5 have no type at all: road user, cybersecurity goal, cybersecurity claim, CAL and the engineering cybersecurity requirement. The remap from `proposed.7` moved none of these. The core of TARA is at least named in the proposal: component, asset, damage scenario, threat scenario (as ThreatInstance), attack path with its feasibility, risk value and cybersecurity control. Asset and damage scenario are named there but not yet defined (Asset is a defined type in ARCH-0001 v0.1.6), and neither model has an edge from an attack path to the threat scenarios it realizes, although the proposal's risk rule now presumes one. The concept-phase objects that turn a risk decision into engineering work have no home: cybersecurity goals, claims, requirements and CALs, and the treatment options of avoiding and sharing; retaining now matches, by our reading, the `accepted-risk` mitigation status. The smaller gaps are the properties on assets, a field for the threat scenario's cause, road users, the impact rating on the damage scenario, the method behind each rating, and the item with its operational assumptions. In the other direction, storing attack steps with AND/OR gates goes beyond 21434, which works as long as one rating per path can still be recorded, as 21434 requires. So do the newer asset owners and business-impact axis, which the proposal keeps apart from S, F, O and P, and its per-owner risk values, for which it does not say which impact they use; by our reading, its lifecycle enum has a counterpart for every stage of 21434's lifecycle.

## 6. How ISO/SAE 21434 risk relates to the risk-metric work

DEC-003, the risk-metric scheme, is open. ARCH-0001 §6 says the scheme must at least accommodate CVSS, an impact set by a human for each environment (R-019), and, as options, ISO/SAE 21434 (R-012) and a Common Criteria feasibility score (R-013). ARCH-0001-PROPOSAL (`proposed.10`) proposes a composite risk vector for the MVP: path-level feasibility, per-category impact, a mitigation status and a risk value derived from an ISO 21434-shaped matrix, shown side by side (its §3, "Risk metric"). Before DEC-003 can go to an ADR, it lists three blockers: "a human-reviewed ISO 21434 extraction", a documented aggregation function for the derived risk, and a distilled `first-cvss` if the post-MVP CVSS option is wanted (its §12). A separate ADR-0005 that marked DEC-003 accepted was closed without merging, and DEC-003 stays open (#70; DL-0011). Issue #14 owns the metrics research. This section compares what the standard says with that proposal; it does not choose a metric.

### 6.1 What 21434 fixes and what it leaves open

| question | fixed by the standard | left open | source |
|---|---|---|---|
| what impact is rated on | each damage scenario, for its adverse consequences to road users, in each category assessed (S, F, O, P) | extra categories; skipping a category when PM-15-07 applies; any weighting between categories | RQ-15-04, RQ-15-05; 15.5 NOTE 1 and NOTE 2; PM-15-07 |
| impact levels | severe, major, moderate, negligible; safety ratings from ISO 26262-3 | the criteria for financial, operational and privacy levels (Annex F is an example) | RQ-15-05, RQ-15-06; Annex F |
| what feasibility is rated on | each attack path, as a whole | any rating of the actions inside a path | RQ-15-10; 3.1.3 |
| feasibility levels | High, Medium, Low, Very low | the method (three recommended approaches) and its scale (Annex G is an example) | RQ-15-10; RC-15-11 to RC-15-14; Annex G |
| several paths for one threat scenario | the risk value draws on the feasibility of all associated attack paths | whether and how to aggregate them (the highest rating is the example) | RQ-15-15 and NOTE 2 |
| risk value | a value for each threat scenario, from 1 to 5, where 1 is minimal | the combining function (a matrix or a formula, as examples); whether to keep one value per impact rating; whether values are whole numbers | RQ-15-15 and NOTE 1; RQ-15-16 and its EXAMPLE; Annex H |
| scales | the standard's own levels | organization-specific scales that map onto them | 15.1 |
| treatment | one or more of avoid, reduce, share and retain, for each threat scenario | which option | RQ-15-17 |
| process effect of risk | threat scenarios with risk value 1 need not conform to 9.5 or to Clauses 10 and 11 | | PM-06-08 |
| assurance level | nothing: CALs are optional | the scheme. Informative Annex E says a CAL is related to risk only indirectly and cannot be read directly off a risk value | 9.4, NOTE 4; E.2 |

### 6.2 The proposal's risk metric, checked against the standard

The proposal's statements below come from its §3 ("Risk metric") and §12. Items 1 to 11 were first checked at `proposed.7` and still hold at `proposed.10`, with the wording updated where it changed; items 12 to 16 check what `proposed.8` to `proposed.10` added.

| # | the proposal says | the standard | verdict |
|---|---|---|---|
| 1 | the derived Risk = M(Impact, Feasibility), an "ISO 21434-shaped" impact by feasibility matrix, citing RQ-15-15/16 and Annex H | RQ-15-15 and RQ-15-16 require a value from 1 to 5 derived from impact and feasibility; Table H.8 is one example matrix | consistent. The matrix still has to be chosen: Annex H's own formula and matrix disagree on 4 of the 16 pairs (§4.3) |
| 2 | feasibility is rated per attack path on Table 1's four-point scale (RQ-15-10), not per step | RQ-15-10; 3.1.3 | consistent |
| 3 | feasibility is rated by a human at the MVP, optionally informed by the attack potential factors (RC-15-12) | only a Table 1 rating is required (RQ-15-10); basing the method on one of the three approaches is a recommendation (RC-15-11) | consistent with the requirement; it follows the recommendation only if the rater uses one of the approaches |
| 4 | no CVSS and no per-step aggregation at the MVP | CVSS is one of three recommended approaches (RC-15-11, RC-15-13); the standard has no per-step rating | consistent |
| 5 | impact is rated per category (S, F, O, P) on four levels by a human, with safety from ISO 26262 (RQ-15-04 to RQ-15-06) | the same provisions; ARCH-0001's R-019 also has a human set the impact | consistent |
| 6 | "21434 determines a risk value per category (Annex H.9)", so the category vector is kept and any single number is only a display simplification | RQ-15-15 requires a risk value for each threat scenario; NOTE 1 allows one for each impact rating; Table H.9 labels its values by category, but each threat scenario there has only one rated category | overstated. Per-category values are allowed, not required, and a single value per threat scenario also conforms. Keeping the vector fits NOTE 1 and the plural "risk values" of RQ-15-17. `proposed.10` keeps this sentence two bullets above its multiplicity rule (item 14), which says 21434 requires one value per threat scenario; the two disagree |
| 7 | environment and exposure feed only the exploitability side of feasibility (attack vector, reachability, window of opportunity), never confidentiality, integrity or availability (impact) | the standard rates impact on road users (S, F, O, P) apart from feasibility on paths; confidentiality, integrity and availability are cybersecurity properties of assets (3.1.2, Note 1; 3.1.20), not impact categories. The driving situation can be part of the damage scenario (for example night driving at medium speed, Table H.2), and for safety, ISO 26262-3's controllability and exposure may be considered with a rationale (F.2) | consistent in keeping the two apart, but stricter than the standard, where the situation can shape impact through the damage scenario. The "exposure" of F.2 is ISO 26262-3's parameter, not network exposure (we did not read ISO 26262-3). ARCH-0001's R-019, a human-set impact per environment, also sits uneasily with this rule; the proposal does not mention R-019 |
| 8 | a later CVSS option would use only the exploitability metrics AV, AC, PR and UI (RC-15-13), never CVSS base or environmental impact | RC-15-13; G.3 replaces CVSS impact with the standard's own impact rating | consistent, but Annex G's CVSS guidance is tied to CVSS v3.1: v4.0 adds attack requirements (AT) and has no exploitability equation, so a v4.0 vector does not fit G.3 and Table G.8 as they stand (§3.2) |
| 9 | per-step feasibility with AND/OR aggregation (minimum on an AND chain, maximum over OR) is attack-tree cost propagation, a deliberate deviation from 21434's path-level rating | the standard rates whole paths (RQ-15-10); its example for several paths is the highest rating (RQ-15-15, NOTE 2); Annex G lets distinct steps raise some factors (G.2.2) but never rates steps | consistent. Taking the maximum over alternative paths matches the standard's example; the minimum over an AND chain has no counterpart in it |
| 10 | caveat: the Clause 15 material and Annex H are "extracted but `not-reviewed`", with "OCR spillover in `#RQ-09-03`" | the catalog was made with `pdftotext` and a script, not OCR (`generated_from` in its record.yaml and requirements.yaml), and RQ-09-03's entry holds Annex H text that the extractor picked up in place of the provision; 15 other entries are also wrong or cut short (§7). The library's notes say the annexes were not distilled (`normative.md`, coverage line), so Annex H was not extracted | partly wrong: the problem is not OCR, Annex H was not extracted, and the defect is wider (§7) |
| 11 | DEC-003 blocker: "a human-reviewed ISO 21434 extraction (annexes `not-reviewed`)" | sections 2 to 4 of this report cover Clause 15 and Annexes E to H, and §7 checks the catalog against the standard | this report covers that ground; whether it clears the blocker is the sponsor's call, after human review. The sponsor's note on PR #69 (2026-10-02) says this extraction is evidence and does not accept the risk-metric decision, and holds the merge for a human DEC-003 sign-off. By our reading, the second blocker, the aggregation function, is where the risk-value row of §6.1 needs answers |
| 12 | risk is a vector, not a lone scalar: a threat's record carries feasibility, per-category impact, mitigation status and a derived risk as peer fields, the derived value shown next to its inputs; a single CVSS-like number is not the scheme (R-045) | RQ-15-15 and RQ-15-16 require a risk value for each threat scenario; RQ-15-17 then has each threat scenario's treatment decided in the light of its risk values; the standard sets no display rules | consistent. Showing the inputs next to the value conflicts with nothing in the standard, and keeping the status out of the formula fits RQ-15-15, whose only inputs are impact and feasibility; a control shown to work still lowers the risk value over time (E.2, Figure E.1; §3.3) |
| 13 | mitigation status is a peer field: planned, in-progress, complete, accepted-risk or n-a, read from `MitigationInstance.status` and refined by DEC-009 | each threat scenario gets one or more of four treatment options: avoid, reduce, share, retain (RQ-15-17); the rationale for retaining or sharing is recorded as a cybersecurity claim and covered by monitoring and vulnerability management (RQ-15-17, NOTE); sharing, and retaining because of assumptions, need claims (RQ-09-06) | no conflict, but the status records the treatment decision only in part. By our reading, planned, in-progress and complete track a reduction, and `accepted-risk` is retaining; avoiding and sharing have no value, and the proposal has no cybersecurity claim to record why a risk is retained (§5.3) |
| 14 | `RiskScore` multiplicity: RQ-15-15/16 require a single value from 1 to 5 per threat scenario, so a reduction is needed; feasibility is aggregated over the attack paths that realize the scenario (worst path), then M(I, F) gives one score per threat scenario and impact category, and, post-MVP, per affected owner | RQ-15-15 requires a risk value for each threat scenario, from the impact of its damage scenarios and the feasibility of its attack paths; NOTE 1 allows a separate value for each impact rating, that is, for each damage scenario and category; NOTE 2 gives the highest path rating as an example of aggregation; RQ-15-16 fixes the range | consistent. The worst path is NOTE 2's example. One score per threat scenario and category relies on NOTE 1, which the proposal does not cite, and still needs a rule when several damage scenarios of one threat scenario are rated in the same category; by our reading, that rule is part of the aggregation function the proposal's §12 lists as a blocker. Scores per owner have no counterpart in the standard, and the proposal does not say which impact they use, since S, F, O and P are not re-indexed by owner (item 15) |
| 15 | S, F, O and P stay fixed to the "end-beneficiary" (road user, data subject or end-user); the asset owner's view is a separate `business_impact` axis, assessed in addition to them and chosen by `Asset.owned_by` (post-MVP; R-039) | damage scenarios are rated for their adverse consequences to road users (RQ-15-04), and TARA takes the viewpoint of affected road users (15.1); additional impact categories can be considered (RQ-15-04, NOTE 2); a road user is any person using a road, the vehicle owner included (3.1.31) | consistent in keeping S, F, O and P on the road user. "Data subject" is not a 21434 term, and "end-user" appears only once, in an incident-response note (RQ-13-01, NOTE 5); 21434 rates impact on road users, and its privacy example speaks of the PII principal (F.5). The business-impact axis has no counterpart: NOTE 2 allows more categories, but in an assessment of consequences to road users, so the loss of an owner who is not a road user, such as a manufacturer or an operator, lies outside 21434's ratings (our reading); a vehicle owner's loss is already a road-user impact (3.1.31; F.3). Keeping it as a separate axis, as the proposal does, avoids a conflict |
| 16 | the feasibility method stays ISO 21434 Table 1, path-level and four-point; Common Criteria and ISO/IEC 18045 are not the MVP method; views show concise numbers, a feasibility label and a colour (Common Criteria-style display only) | Table 1 is the four-level scale, each level described by the effort an attack path takes (RQ-15-10); the method should follow one of three approaches (RC-15-11); RC-15-12, NOTE 2 names ISO/IEC 18045 as a source of its core attack potential factors, and Annex G's points and bands are based on it (G.2.1, G.2.2.6) | consistent. Table 1 is the scale the rating must use, not a method; item 3 covers the method. The factors that may inform the MVP rating (item 3) have ISO/IEC 18045 as a source, so 18045 stays in the background even though it is not the MVP method. Display is outside the standard's scope |

### 6.3 The other DEC-003 options

- **CVSS.** CVSS enters 21434 only on the feasibility side: through its four exploitability metrics (G.3), or through its attack vector alone (RC-15-14, G.4). Its impact metrics are replaced by the standard's own impact rating, and Annex G's CVSS guidance follows CVSS v3.1 (G.3; §3.2). A full CVSS score, which includes impact, is therefore not part of a 21434 risk value, while ARCH-0001 §6 also asks the scheme to accommodate CVSS's base, temporal and environmental metrics.
- **Common Criteria attack feasibility (R-013).** The standard's attack potential approach is based on ISO/IEC 18045 (G.2.1, G.2.2.6, Table G.7), the same source issue #14 names, together with ISO/IEC 15408 and AVA_VAN, for the Common Criteria metric. The two options share a method family, so #14's planned feasibility calculator bears on both. We did not read ISO/IEC 18045 and do not claim its factor values or bands equal Annex G's. From `proposed.10`, Common Criteria enters the proposal only as a display style, and ISO/IEC 18045 is not the MVP method (item 16).
- **Human-set impact per environment (R-019).** This fits the standard, whose damage scenarios can describe the situation they happen in (Table H.2).
- **CAL.** A CAL can be set in the concept phase and is meant to stay fixed; it cannot be read directly off a risk value (E.2), and it can be attached to a cybersecurity goal as one of the goal's attributes (E.1; §3.3, §5.2).

**Takeaway:** On the points that matter for the MVP, the proposal's metric, now a composite risk vector, is consistent with the standard. The checks found one overstatement (item 6: per-category risk values are allowed, not required; `proposed.10` keeps it, although its multiplicity rule in item 14 disagrees), one rule stricter than the standard (item 7) and a partly wrong caveat (item 10). Of the parts added since `proposed.7`, by our reading, the mitigation status covers reducing and retaining, but not avoiding or sharing (item 13); one risk value per threat scenario and impact category rests on NOTE 1 of RQ-15-15 and still needs a rule for several damage scenarios rated in one category, which, by our reading, belongs to the aggregation function the proposal itself lists as a blocker (item 14); the business-impact axis and per-owner values go beyond the standard's road-user viewpoint (item 15); and "Table 1" is a scale, not a method (item 16). Three facts bear on the choices still open in DEC-003: the risk value's range is fixed but its function and number type are not, and Annex H's own matrix and formula disagree on 4 of 16 pairs; Annex G's CVSS guidance is tied to v3.1; and the attack potential approach shares its source with the Common Criteria option (R-013), which links #11 to #14.

## 7. Check of the library's requirement catalog

The library holds the sponsor's catalog of the standard's provisions and work products (`iso-sae-21434-2021`, `distilled/requirements.yaml`) and a short distillation (`distilled/normative.md`). We checked them at library `5b82f83`, the commit tmodel pins, which holds the same 21434 record as library `main` (`25a4cf8`). The catalog is the closest thing to the referenceable requirements file that #11 asks for, although #11 asked for requirements in our own words and the catalog is verbatim; the proposal cites its entries (§6.2). The checks follow the second, adversarial pass of the library's full-extraction standard (FX-1): counts, word-for-word text, dropped or spliced statements, locators, and the links between provisions and work products (searches.md, Tool runs). An independent subagent then recomputed every number in this section and corrected one classification (RQ-07-04). This report changed nothing in the library. Our library pull request, Threat-Radar/library#9 (open), proposes the fixes in §7.2 for the missing provision links, the subclause links (in a new `from_subclauses` field), the locators, the titles, the Figure 3 edges and the inaccurate note; it leaves the 16 texts as they are, pending the exceptions and the rewrite that §7.3 describes.

### 7.1 What matches

- **Counts.** 101 requirements, 13 recommendations, 4 permissions and 42 work products, as in the standard (§1.3), with every identifier present.
- **Labels.** Every entry's normativity and verb match its tag: RQ with "shall", RC with "should", PM with "may".
- **Text.** 102 of the 118 provision texts equal the standard's after normalizing whitespace, dashes, quotes and list labels. Two of them keep small extraction artifacts: a stray space at a line break in RQ-07-01, and Table 1 flattened into RQ-15-10.
- **Locators.** 113 of the 118 provision locators point to the subclause that holds the provision.
- **Work-product links.** Of the 32 work products that the standard ties to named provisions, 16 list exactly those provisions, and every link recorded on the provision side also appears in the standard.

### 7.2 What does not match

| problem | entries (PDF page of our copy) | detail |
|---|---|---|
| annex text instead of the provision | RQ-07-04 (26), RQ-09-03 (33), RQ-09-04 (33), RQ-10-08 (39), RQ-11-01 (41) | the extractor took a later mention of the identifier in an annex and copied what followed it: Annex C's interface agreement template for RQ-07-04, and Annex E, F or H text for the others. RQ-09-04's entry runs on into the bibliography (6,698 characters). RQ-09-03 and RQ-09-04 are the provisions that run the TARA in the concept phase (§2.10) |
| list cut short where a NOTE or EXAMPLE interrupts it | RQ-05-11 (15), RQ-06-02 (19), RQ-06-15 (20), RQ-06-16 (21), RQ-06-30 (23), RQ-09-01 (32), RQ-10-01 (37), RQ-10-04 (38), RQ-12-02 (42), RQ-13-01 (44), RQ-15-17 (54) | 11 entries lose the list items after the interruption; RQ-15-17 keeps only the first of the four treatment options (§2.9) |
| clause-level provision locator | RQ-07-04, RQ-09-03, RQ-09-04, RQ-10-08, RQ-11-01 | the same five entries as the first row; they point to a clause instead of the subclause that holds them (7.4.3, 9.4.2, 9.4.2, 10.4.1, 11.4) |
| work product with no links | WP-05-02, WP-08-02, WP-08-03, WP-09-03, WP-09-04, WP-09-05, WP-09-07, WP-10-02 to WP-10-07, WP-14-01, WP-15-02 | 15 work products have an empty list although the standard names the provisions they result from |
| incomplete link | WP-15-04, impact ratings | lists RQ-15-04 only; the standard gives the range RQ-15-04 to RQ-15-06 |
| links missing in total | 22 of the 48 provision-to-work-product links the standard names | from the two rows above; each is missing on both sides, from the work product's list and from the provision's `expects_deliverables` |
| work-product locator | 14 of the 15 work products with no links | they point somewhere other than the subclause that defines the work product, for example WP-08-02 to 8.3 instead of 8.3.3, and WP-05-02 to 5.4.2 instead of 5.5 |
| subclause links not recorded | WP-05-01, WP-05-03 to WP-05-05, WP-06-01 to WP-06-04, WP-07-01, WP-09-01 | the standard ties these 10 work products to subclauses (for example 5.4.1 to 5.4.3) rather than to provisions; the catalog leaves them empty |
| work-product titles from Annex A | WP-09-07, WP-10-03, WP-10-07 | the catalog uses the wording of the Annex A summary table, which differs from the clause (WP-10-03 loses "if applicable"); for WP-09-07 and WP-10-07, neighbouring table text is attached as well |
| Figure 3 edges in `normative.md` | five of thirteen edges | three differ in meaning: the notes have function implements item, function contains asset, and goal allocated to item or component, where the figure has item implements function(s), item contains asset, and cybersecurity requirement allocated to item (the notes' requirement-to-component edge is correct). Two more are written the other way round with the same meaning (item associated with goal; asset has attribute property) (§5.1) |
| inaccurate note in `summary.md` | its Limits section | describes the texts as prefixes of at most 320 characters; 14 are longer |

### 7.3 Why it matters

- **The proposal's risk anchors are mostly sound.** The entries it cites for the risk metric (RQ-15-04 to RQ-15-06, RQ-15-10, RC-15-12, RC-15-13, RQ-15-15, RQ-15-16; §6.2) have the right text and locators, but RQ-15-05 and RQ-15-06 lack their link to WP-15-04. The defects next to them are the treatment step (RQ-15-17), the concept-phase TARA (RQ-09-03, RQ-09-04) and the impact-rating work product (WP-15-04).
- **The defects are spread across the catalog.** The 16 text defects fall in 9 of the 11 clauses that have provisions, Clause 6 having the most (4); Clause 15 has one in 17.
- **Audit automation needs the links.** The library's notes propose the provision-to-work-product structure as the seed for automated audits (`normative.md` §4, which cites tmodel #15; automated compliance validation is #19). With 22 of the 48 named links missing, a coverage query over the catalog would report gaps that are not in the standard.
- **The sponsor's note names a text posture.** The library's draft policy requires requirement text to be verbatim, warning that a paraphrase can quietly weaken a MUST (in ISO terms, a shall) into a SHOULD (its `docs/requirements.md`), while the standard's copyright page forbids posting its text online without written permission, which can be requested from ISO or SAE International, except where otherwise specified or required to implement the standard (see "About quotations" at the top). The sponsor's note on PR #69 (2026-10-02) lists the posture for #11 as its first merge hold: the library keeps paraphrase plus locators and digests, not verbatim ISO text. If the catalog follows it, all 118 provision texts, about 32,700 characters, give way to our own wording, not only the 16 wrong ones; correcting the 16 in place would still leave about 22,600 characters of verbatim text, because the five annex-text entries alone hold about 13,200, including the whole bibliography. Two rules would then need an exception for licensed text: the draft policy's verbatim `text`, and FX-1, whose normative and requirements artifacts must be verbatim and cannot be marked not applicable (§7.4). Our suggestion: keeping each entry's identifier, tag, verb and locator beside our wording would guard against the drift the policy warns about, and the catalog already has `normativity` and `verb` fields (§7.1).

### 7.4 Against the full-extraction standard (FX-1)

FX-1 lives in the upstream m-of-n/library and is not yet in the Threat-Radar fork. It applies to a spec record once a pull request touches it; records older than FX-1 (normative from 2026-09-28), like this one (ingested on 2026-09-25), are left as they are until then. A pull request that fixes the catalog would therefore have to meet FX-1's definition of done: the full artifact set, or a written reason for each missing artifact, reconciled keyword counts, and passes 1 to 3 recorded.

| FX-1 artifact | this record |
|---|---|
| summary and labels | present, except `topic`, which is empty; one inaccurate note (§7.2) |
| normative statements, verbatim, with locators | `normative.md` is an overview, not every statement. FX-1 allows no exception for this artifact, so under the posture in §7.3 a paid standard cannot meet it as written |
| requirements | present; 16 texts, 5 provision locators, 14 work-product locators, 16 work-product link lists and 3 titles need fixing (§7.2; library PR #9 covers all but the texts), and FX-1's fields `testable` and `kind` and its keyword-count header are missing. FX-1 also wants this text verbatim, with no exception allowed |
| schema, messages, protocol, state machine | the standard defines no data format (§1.1), which is the kind of reason FX-1 asks for when these are marked not applicable |
| examples and test vectors | Annex H could become a fixture once its inconsistencies are resolved (§4.4) |
| design notes | none yet; §5 and §6 of this report hold the material |

No passes are recorded on the record. Counting the sponsor's extraction as the first, this section is the mechanical part of the second; the cross-check and the human review (`reviewed_by` is empty on every artifact) remain.

**Takeaway:** The catalog's counts and labels are right and most of its texts match the standard, but 16 provision texts, 16 work-product link lists, 19 locators, 3 titles and 3 Figure 3 edges do not, and the defects are spread across the catalog. The ones that matter most here are the concept-phase TARA provisions (RQ-09-03, RQ-09-04), the treatment step (RQ-15-17), and the provision-to-work-product links that audit automation would build on. Library PR #9 proposes the metadata fixes. The texts are the larger job: under the posture in the sponsor's note, every provision text would become our own wording, which would need an exception in the draft policy and in FX-1, and someone to own the rewrite (§8, question 3).

## 8. Synthesis

This section gathers the evidence above by decision. It does not select a design.

**DEC-001 (object model).**
- Of the 23 objects mapped, 9 have the same or a close type in the proposal (`proposed.10`), 9 overlap only partly, and 5 have no type at all (§5.2); the remap from `proposed.7` changed no fit. The core of TARA is at least named there: component, asset, damage scenario, threat scenario (as ThreatInstance), attack path with its feasibility, risk value and cybersecurity control. Asset and damage scenario are named but not yet defined in the proposal, Asset is missing from its list of schema classes, and neither ARCH-0001 nor the proposal has an edge from an attack path to the threat scenarios it realizes, although the proposal's risk rule presumes one (§5.2, §5.3).
- The concept-phase objects that turn risk decisions into engineering work are missing: cybersecurity goals, claims, engineering cybersecurity requirements and CALs, and the treatment options of avoiding and sharing (retaining matches the `accepted-risk` status, by our reading). Smaller gaps are the properties on assets and the item-contains-asset edge; a field for the threat scenario's cause and, in the proposal, its link to the targeted asset; road users as a type, and the impact rating on the damage scenario rather than on the threat's risk record; the method behind each feasibility rating; and the item with its operational assumptions (§5.3).
- By our reading, the parts added in `proposed.8` to `proposed.10` sit beside 21434 rather than against it: asset owners and a business-impact axis go beyond its road-user viewpoint and are kept apart from S, F, O and P; per-owner risk values go beyond it too, and the proposal does not say which impact they use; and the lifecycle enum has a counterpart for each stage 21434 covers (§5.3, §6.2).
- The standard states cardinalities a schema has to allow: damage scenarios and threat scenarios are many-to-many, so are attack paths and threat scenarios, each path gets one feasibility rating, and a threat scenario can carry several risk values (§5.4).
- Figure 3 covers ten objects and thirteen edges but no attack paths, ratings, risk values, treatment decisions, claims or CALs, which come from Clauses 9 and 15 and the annexes (§5.1). The library's notes state three of its edges with a different meaning (§7.2).
- Annex H's wording drifts between tables (§4.3), which is a reason to link objects by identifier (§4.4); ADR-0004 already requires stable IDs.

**DEC-003 (risk metric).**
- The standard fixes the reference levels (four impact levels, four feasibility levels, risk values from 1 to 5), onto which an organization's own scales can be mapped (15.1). It leaves open the combining function, the aggregation across paths, the rating method and whether risk values are whole numbers (§6.1).
- The proposal's MVP metric, a composite risk vector since `proposed.10`, is consistent with the standard on the points that matter for the MVP. The checks found one overstatement (per-category risk values are allowed, not required), one rule stricter than the standard (environment never shaping impact, which also sits uneasily with R-019), and a partly wrong caveat about the catalog (§6.2).
- Of the newer rules, by our reading, the mitigation status covers reducing and retaining, but not avoiding or sharing; one risk value per threat scenario and impact category rests on NOTE 1 of RQ-15-15 and needs a rule for several damage scenarios rated in one category; the business-impact axis lies outside the standard's ratings for owners who are not road users; and "Table 1" is a scale, not a method (§6.2, items 13 to 16).
- Three facts bear on the open choices: Annex G's CVSS guidance follows CVSS v3.1, which a CVSS v4.0 vector does not fit as it stands (§3.2); the attack potential approach shares its source, ISO/IEC 18045, with the Common Criteria option R-013 (§6.3); and Annex H's own risk matrix and risk formula disagree on 4 of 16 pairs (§4.3). A CAL cannot be read directly off a risk value (§3.3, §6.3).
- Sections 2 to 4 and 7 cover the ground of the proposal's first blocker, a human-reviewed extraction; whether they clear it, after human review, is the sponsor's call, and the sponsor has said this extraction is evidence that does not accept DEC-003 (§6.2). By our reading, documenting the aggregation function, the proposal's second blocker, would settle what §6.1 leaves open for the risk value: the combining function, a rule for several damage scenarios rated in one category, and whether values are whole numbers; across paths, the proposal already takes the worst path (proposal §3).

**DEC-009 (generic-threat to product mapping; mitigation lifecycle).**
- The standard ties the mitigation lifecycle to TARA. Treatment decisions lead to goals, claims or a changed item (§2.9, §2.10); claims are covered by monitoring and vulnerability management (15.9, NOTE); evaluated events can update threat scenarios (RQ-08-04, NOTE 3); a vulnerability's risks go back through the treatment decision unless a remediation removes it (RQ-08-07); and a reuse analysis can identify a TARA as an affected or missing work product, for assets, threat scenarios or risk values that are new or have changed (RQ-06-16, EXAMPLE 4). These continual activities run in every lifecycle phase, and vulnerability management runs until the end of cybersecurity support (8.1).
- The metric has a process effect: threat scenarios with risk value 1 need not conform to 9.5 or to Clauses 10 and 11 (PM-06-08).
- The standard works one item, or component, at a time and says nothing about product families (§1.1, §5.3).
- The proposal's mitigation status (planned, in-progress, complete, accepted-risk, n-a), which DEC-009 is to refine, has no value for avoiding or sharing a risk and no link to the cybersecurity claim that records why a risk is retained or shared (§6.2, item 13).

**ADR-0002 (accepted).** It names the ISO 21434 object model as the automotive vocabulary that binds to the shared graph. Section 5 now maps it type by type, with the gaps listed.

**Tool support.** Not surveyed. RPT-0003 covers IriusRisk, one of the candidate tools the library record lists, as a general threat-modeling tool, but it never mentions ISO/SAE 21434, TARA or automotive use. The library record lists its candidates without a survey (`iso-sae-21434-2021`, summary.md, Implementations).

**Limits.**
- One standard, read in full: the 2021 first edition. The other ISO documents this report names (ISO 26262-3, ISO/IEC 15408, ISO/IEC 18045, ISO/IEC 27000, ISO/IEC 29100, ISO 31000, ISO/SAE PAS 8475, ISO/SAE TR 8477, ISO/PAS 5112, ISO 24089) were not read, nor were EVITA, TVRA and PASTA. The report gives only what ISO/SAE 21434 or our own issues say about them, plus the ISO status of those in §1.2, where the stage names still need a manual check on iso.org.
- The report paraphrases the standard and cites clause numbers, so a reader needs the standard to check it. It reproduces the example values of Tables E.1, G.6 to G.9, H.8 and H.10, and results from Tables H.7 and H.9.
- The fit labels in §5.2 and the verdicts in §6.2 are our reading. They follow ARCH-0001-PROPOSAL `proposed.10`; a later iteration needs another remap.
- The catalog check in §7 is the mechanical part of an adversarial pass; FX-1's cross-check and a human review and sign-off remain (§7.4).
- Annex H illustrates only the concept phase, with one small example (§4).
- Every section was fact-checked by an independent subagent against the sources, and each finding was re-checked before it was fixed (searches.md, Tool runs); a human review is still needed.

**Open questions for the sponsor, and what the note on PR #69 says.** The sponsor's note on PR #69 (2026-10-02) holds the merge on five points: the copyright posture, a human DEC-003 sign-off, who owns the catalog fixes, Annex H, and a remap once #66 lands. It adds that the open questions in the PR body stand.
1. May the public library keep the standard's verbatim text, or should it hold locators, digests and our own wording, as #11 asked (§7.3)? *The note:* paraphrase plus locators and digests, not verbatim ISO text. *Still open:* the exceptions this needs in the library's draft policy and in FX-1, and who rewrites the catalog's 118 texts (question 3).
2. Once reviewed and signed off, do sections 2 to 4 and 7 meet the DEC-003 blocker of a human-reviewed extraction, or must the catalog be fixed first (§6.2, §7)? *The note:* this extraction is evidence and does not accept the risk-metric decision; the merge waits for a human DEC-003 sign-off. *Still open:* whether these sections, once signed off, meet the blocker; whether the catalog must be fixed first; and the order of the two steps, since the merge waits for the DEC-003 sign-off while the DEC-003 ADR waits for a reviewed extraction (proposal §12).
3. Who fixes the catalog in a library pull request, and should Annex H become a fixture? FX-1 would govern that pull request once it reaches the fork, or if the pull request goes upstream (§4.4, §7.4). *Still open.* Our library PR #9 already proposes the metadata fixes. If Annex H becomes a fixture, we suggest following Table H.5, which Figure H.3 matches; that changes none of the expected results (§4.4).
4. Remap §5 and §6 once #66 lands (titled `proposed.8`; it merged at `proposed.9`). *Done:* #66 and then #77 merged after the note, and §5 and §6 now follow `proposed.10` (§5, §6.2).
