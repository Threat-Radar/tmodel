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
updated: "2026-10-02"
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

Annex G gives guidance for each of the three approaches in RC-15-11. For any of them, whether an attack can scale, meaning it extends easily to many instances and targets, can be included in the rating (G.1).

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
- **Who sets it.** The organization developing the item, or, for a component developed out of context, the component's developer by assumption (E.1).
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
| impact rating | Three damage scenarios rated, each in one category: the collision S, severe (S3); a vehicle that cannot be driven at night because the headlamps seem disabled while parked O, major; automatic high beam stuck on low beam O, moderate. | Table H.3 |
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

**Takeaway:** The example walks the whole chain on a small system and confirms the shapes from §2: ratings on paths, aggregation per threat scenario, and a risk value labelled by impact category. It also shows what the clauses leave open. The example rates its two threat scenarios with different methods and combines them in one table, although the standard does not say whether that is acceptable. The example risk formula and risk matrix are not interchangeable in general. And the standard does not say whether a risk value must be a whole number, while the example formula gives fractions for 3 of the 16 combinations. Its small inconsistencies are a reason to link the objects by identifier, not by text.

## 5. TARA objects mapped onto the proposed object model

This section lines up the objects ISO/SAE 21434 uses with the types in ARCH-0001 §3 (v0.1.6, the current working labels) and in ARCH-0001-PROPOSAL v0.2.0 (`0.2.0-proposed.7`, the DEC-001 synthesis for #15). It is evidence for #15 and #17, not a model of its own: where the standard and the models differ, it says so and leaves the choice to DEC-001. ADR-0002 expects this mapping, with the ISO 21434 object model binding onto the shared graph.

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

| ISO/SAE 21434 | ARCH-0001 §3 (v0.1.6) | ARCH-0001-PROPOSAL (proposed.7) | fit | what differs |
|---|---|---|---|---|
| component | Component | Component, with `composed_of` | same | |
| asset | Asset | Asset, named only in the R-029 row, with `classification` (§6) | close | 21434 gives each asset its cybersecurity properties (3.1.2); neither model records them, and neither has the item-contains-asset edge |
| cybersecurity property | none | `violates_property`, the security property each STRIDE category violates (§2) | partial | this records the property a threat violates, which matches the `compromises` edge, but not the properties an asset has. Its values come from STRIDE and add authentication, non-repudiation and authorization; 21434's examples are confidentiality, integrity and availability, as an open list (3.1.20) |
| damage scenario | none | DamageScenario, the target of `realizes` (§1) | close | named only as the target of `realizes`; in 21434 it also affects a road user and carries the impact ratings |
| road user | none | none | none | the party a damage scenario harms (3.1.22) |
| impact rating, per category | part of Review: impact is a human judgement (§3) | the impact input of RiskScore: per category S, F, O, P, supplied by a human (§3, risk metric) | partial | 21434 attaches the rating to the damage scenario, per category (RQ-15-05); the proposal keeps the category vector but does not say which object carries it |
| threat scenario | Threat, an adverse action against an asset | ThreatInstance, with `realizes` DamageScenario and a method facet (§1, §2) | close | 21434 also requires the targeted asset and the cause (RQ-15-03). ARCH-0001's Threat names an asset; the proposal generates threats from DFD elements, which resolve to components, and states no asset link. Neither model has a separate cause field, though the threat itself, and in the proposal its STRIDE category, carries part of it |
| attack path | AttackPath / ThreatChain | AttackPath, made of AttackSteps | close | neither model links a path to the threat scenarios it realizes, which 21434 requires (RQ-15-09); one path can realize several threat scenarios |
| (attack step) | AttackStep | AttackStep, with AND/OR gates and `precedes` ordering (§2a) | extension | 21434 defines no step object and rates only whole paths; it shows attack trees and graphs as analysis aids (15.6, NOTE 1; Figure H.3) and lists a path's actions in order (Table H.5) |
| attack feasibility rating | none | `attack_feasibility` on AttackPath, 4-point, human-rated at MVP (§3) | close | no field records the rating method or its inputs (factor levels, CVSS v3.1 metrics, attack vector); `source_method` records which threat method proposed a threat, not which rating method rated a path |
| attacker | none | ThreatActor, a generic catalog type (§1) | partial | 21434's attacker is whoever carries out a path (3.1.5) |
| risk value | RiskScore | RiskScore = M(Impact, Feasibility), keeping the category vector (§3) | same | the range 1 to 5 is fixed (RQ-15-16); whole numbers are not (§4.3) |
| risk treatment decision | none | MitigationInstance, which by our reading corresponds to reducing (§5, §7) | partial | avoiding, sharing and retaining have no home; each leads somewhere else (§2.9, §2.10) |
| cybersecurity control | Mitigation | Mitigation (D3FEND) and MitigationInstance | same | a measure that modifies risk (3.1.14) |
| cybersecurity goal | none | none | none | central to 9.4: created by reduce decisions, protects assets, can carry a CAL |
| cybersecurity claim | none | none | none | a statement about a risk (3.1.12). Not the proposal's `Assertion`, which records where a proposed node or edge came from (§4) |
| cybersecurity requirement | none | none: the proposal's Requirement (post-MVP, #19; §7) is a different thing | none | in 21434 it realizes a goal and is allocated to an item or component (Figure 3); the proposal's Requirement belongs to the audit model, so the name clashes rather than matches |
| CAL | none | none | none | an attribute of a goal, inherited by requirements and components (Annex E) |
| weakness | Weakness (CWE) | Weakness (CWE) | partial | 21434's examples of weaknesses include a missing requirement and a flawed operational procedure (3.1.40), which may have no CWE entry |
| vulnerability | Vulnerability (CVE, NVD) | Finding / Vulnerability | partial | in 21434 a weakness becomes a vulnerability when an attack path can exploit it (3.1.38), whether or not a CVE exists |
| item | Product, the closest type | Product / ProductInstance, with `composed_of` | partial | an item implements one or more vehicle-level functions (3.1.25; Figure 3) and has a boundary (RQ-09-01); neither model has a unit scoped by function |
| function | none | Process / Workflow, DFD roles (§1) | partial | a 21434 function is the item's intended behaviour at vehicle level (RQ-09-01, NOTE 2); a DFD process is a behavioral role that components realize |
| operational environment | none | Environment, one per Deployment, post-MVP (§3, §7) | partial | 21434 describes it per item, with assumptions (RQ-09-02; Table H.1); neither model has a type for assumptions |
| provision and work product | none | Requirement / WorkProduct, post-MVP (#19; §7) | close | the RQ, RC, PM and WP identifiers can serve as keys (§1.3) |

Section numbers in the third column refer to ARCH-0001-PROPOSAL.

### 5.3 Gaps, both ways

**What 21434 needs that neither model has yet:**
1. Cybersecurity goals and claims, and the links from treatment decisions to them (RQ-09-05, RQ-09-06).
2. The treatment options other than reducing: avoiding, sharing and retaining (RQ-15-17).
3. CALs on goals, and their inheritance by requirements and components (Annex E).
4. The cybersecurity properties of an asset, and the item-contains-asset edge (Figure 3).
5. A separate field for the threat scenario's cause, and, in the proposal, its link to the targeted asset (RQ-15-03).
6. Road users, and an owner for the per-category impact rating (RQ-15-04, RQ-15-05).
7. The method and inputs behind each feasibility rating (RC-15-11 to RC-15-14; §3).
8. The item as a unit scoped by its functions, and its operational environment with assumptions (RQ-09-01, RQ-09-02).
9. A link from each attack path to the threat scenarios it realizes (RQ-15-09).

**What the proposal has beyond 21434:**
- Attack steps, AND/OR gates, ordering and shared steps stored as model data (proposal §2a). 21434 shows attack trees and graphs as analysis aids (15.6, NOTE 1; Figure H.3) but defines no step object and rates only whole paths, so step-level data would still have to yield one rating per path. The proposal already treats per-step aggregation as a post-MVP deviation from 21434 (proposal §3).
- Method facets. 21434 itself names STRIDE, with EVITA, TVRA and PASTA, as a way to identify threat scenarios (15.4, NOTE 2). The facet mechanism, LINDDUN and MAESTRO, provenance (`Assertion`, Review), VEX, the DFD layer, networks, redundancy and the view layer are outside its scope and do not conflict with it.
- Product families and the generic-to-instance mapping. 21434 works one item, or component, at a time.

**Names to watch:**
- A 21434 "claim" is not the proposal's `Assertion`.
- "Requirement" has three senses: an engineering cybersecurity requirement (Figure 3), a provision of the standard tagged RQ, and, by our reading, the proposal's audit-model Requirement (#19), which is the second sense.
- The "security properties" on the proposal's DFD elements (authenticated, encrypted, privilege; proposal §1) describe controls; 21434's cybersecurity properties are attributes that can be worth protecting (3.1.20).
- The ARCH-0001 "Threat" corresponds to a 21434 "threat scenario".

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

**Takeaway:** Of the 23 objects in the mapping table, not counting the attack step, 9 have the same or a close type in the proposal, 9 overlap only partly, and 5 have no type at all: road user, cybersecurity goal, cybersecurity claim, CAL and the engineering cybersecurity requirement. The core of TARA is at least named in the proposal: component, asset, damage scenario, threat scenario (as ThreatInstance), attack path with its feasibility, risk value and cybersecurity control. Asset and damage scenario are named there but not yet defined (Asset is a defined type in ARCH-0001 v0.1.6), and neither model links an attack path to the threat scenarios it realizes. The concept-phase objects that turn a risk decision into engineering work have no home: cybersecurity goals, claims, requirements and CALs, and the treatment options other than reducing. The smaller gaps are the properties on assets, a field for the threat scenario's cause, road users, the method behind each rating, and the item with its operational assumptions. In the other direction, storing attack steps with AND/OR gates goes beyond 21434, which works as long as one rating per path can still be recorded, as 21434 requires.

## 6. How ISO/SAE 21434 risk relates to the risk-metric work

DEC-003, the risk-metric scheme, is open. ARCH-0001 §6 says the scheme must at least accommodate CVSS, an impact set by a human for each environment (R-019), and, as options, ISO/SAE 21434 (R-012) and a Common Criteria feasibility score (R-013). ARCH-0001-PROPOSAL (`proposed.7`) proposes an ISO 21434-shaped metric for the MVP (its §3, "Risk metric") and lists "a human-reviewed ISO 21434 extraction" among the blockers before DEC-003 can go to an ADR (its §12). Issue #14 owns the metrics research. This section compares what the standard says with that proposal; it does not choose a metric.

### 6.1 What 21434 fixes and what it leaves open

| question | fixed by the standard | left open | source |
|---|---|---|---|
| what impact is rated on | each damage scenario, in each category assessed (S, F, O, P) | extra categories; skipping a category when PM-15-07 applies; any weighting between categories | RQ-15-04, RQ-15-05; 15.5 NOTE 1 and NOTE 2; PM-15-07 |
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

The proposal's statements below come from its §3 ("Risk metric") and §12, at `proposed.7`.

| # | the proposal says | the standard | verdict |
|---|---|---|---|
| 1 | RiskScore = M(Impact, Feasibility), an "ISO 21434-shaped" impact by feasibility matrix, citing RQ-15-15/16 and Annex H | RQ-15-15 and RQ-15-16 require a value from 1 to 5 derived from impact and feasibility; Table H.8 is one example matrix | consistent. The matrix still has to be chosen: Annex H's own formula and matrix disagree on 4 of the 16 pairs (§4.3) |
| 2 | feasibility is rated per attack path on Table 1's four-point scale (RQ-15-10), not per step | RQ-15-10; 3.1.3 | consistent |
| 3 | feasibility is rated by a human at the MVP, optionally informed by the attack potential factors (RC-15-12) | only a Table 1 rating is required (RQ-15-10); basing the method on one of the three approaches is a recommendation (RC-15-11) | consistent with the requirement; it follows the recommendation only if the rater uses one of the approaches |
| 4 | no CVSS and no per-step aggregation at the MVP | CVSS is one of three recommended approaches (RC-15-11, RC-15-13); the standard has no per-step rating | consistent |
| 5 | impact is rated per category (S, F, O, P) on four levels by a human, with safety from ISO 26262 (RQ-15-04 to RQ-15-06) | the same provisions; ARCH-0001's R-019 also has a human set the impact | consistent |
| 6 | "21434 determines a risk value per category (Annex H.9)", so the category vector is kept and any single number is only a display simplification | RQ-15-15 requires a risk value for each threat scenario; NOTE 1 allows one for each impact rating; Table H.9 labels its values by category, but each threat scenario there has only one rated category | overstated. Per-category values are allowed, not required, and a single value per threat scenario also conforms. Keeping the vector fits NOTE 1 and the plural "risk values" of RQ-15-17 |
| 7 | environment and exposure feed only the exploitability side of feasibility (attack vector, reachability, window of opportunity), never confidentiality, integrity or availability (impact) | the standard rates impact on road users (S, F, O, P) apart from feasibility on paths; confidentiality, integrity and availability are cybersecurity properties of assets (3.1.2, Note 1; 3.1.20), not impact categories. The driving situation can be part of the damage scenario (for example night driving at medium speed, Table H.2), and for safety, ISO 26262-3's controllability and exposure may be considered with a rationale (F.2) | consistent in keeping the two apart, but stricter than the standard, where the situation can shape impact through the damage scenario. The "exposure" of F.2 is ISO 26262-3's parameter, not network exposure (we did not read ISO 26262-3). ARCH-0001's R-019, a human-set impact per environment, also sits uneasily with this rule; the proposal does not mention R-019 |
| 8 | a later CVSS option would use only the exploitability metrics AV, AC, PR and UI (RC-15-13), never CVSS base or environmental impact | RC-15-13; G.3 replaces CVSS impact with the standard's own impact rating | consistent, but Annex G's CVSS guidance is tied to CVSS v3.1: v4.0 adds attack requirements (AT) and has no exploitability equation, so a v4.0 vector does not fit G.3 and Table G.8 as they stand (§3.2) |
| 9 | per-step feasibility with AND/OR aggregation (minimum on an AND chain, maximum over OR) is attack-tree cost propagation, a deliberate deviation from 21434's path-level rating | the standard rates whole paths (RQ-15-10); its example for several paths is the highest rating (RQ-15-15, NOTE 2); Annex G lets distinct steps raise some factors (G.2.2) but never rates steps | consistent. Taking the maximum over alternative paths matches the standard's example; the minimum over an AND chain has no counterpart in it |
| 10 | caveat: the Clause 15 material and Annex H are "extracted but `not-reviewed`", with "OCR spillover in `#RQ-09-03`" | the catalog was made with `pdftotext` and a script, not OCR (`generated_from` in its record.yaml and requirements.yaml), and RQ-09-03's entry holds Annex H text that the extractor picked up in place of the provision; 15 other entries are also wrong or cut short (§7). The library's notes say the annexes were not distilled (`normative.md`, coverage line), so Annex H was not extracted | partly wrong: the problem is not OCR, Annex H was not extracted, and the defect is wider (§7) |
| 11 | DEC-003 blocker: "a human-reviewed ISO 21434 extraction (annexes are `not-reviewed`)" | sections 2 to 4 of this report cover Clause 15 and Annexes E to H, and §7 checks the catalog against the standard | this report covers that ground; whether it clears the blocker is the sponsor's call, after human review |

### 6.3 The other DEC-003 options

- **CVSS.** CVSS enters 21434 only on the feasibility side: through its four exploitability metrics (G.3), or through its attack vector alone (RC-15-14, G.4). Its impact metrics are replaced by the standard's own impact rating, and Annex G's CVSS guidance follows CVSS v3.1 (G.3; §3.2). A full CVSS score, which includes impact, is therefore not part of a 21434 risk value, while ARCH-0001 §6 also asks the scheme to accommodate CVSS's base, temporal and environmental metrics.
- **Common Criteria attack feasibility (R-013).** The standard's attack potential approach is based on ISO/IEC 18045 (G.2.1, G.2.2.6, Table G.7), the same source issue #14 names, together with ISO/IEC 15408 and AVA_VAN, for the Common Criteria metric. The two options share a method family, so #14's planned feasibility calculator bears on both. We did not read ISO/IEC 18045 and do not claim its factor values or bands equal Annex G's.
- **Human-set impact per environment (R-019).** This fits the standard, whose damage scenarios can describe the situation they happen in (Table H.2).
- **CAL.** A CAL can be set in the concept phase and is meant to stay fixed; it cannot be read directly off a risk value (E.2), and it can be attached to a cybersecurity goal as one of the goal's attributes (E.1; §3.3, §5.2).

**Takeaway:** On the points that matter for the MVP, the proposal's metric is consistent with the standard. The checks found one overstatement (item 6: per-category risk values are allowed, not required), one rule stricter than the standard (item 7) and an imprecise caveat (item 10). Three facts bear on the choices still open in DEC-003: the risk value's range is fixed but its function and number type are not, and Annex H's own matrix and formula disagree on 4 of 16 pairs; Annex G's CVSS guidance is tied to v3.1; and the attack potential approach shares its source with the Common Criteria option (R-013), which links #11 to #14.

## 7. Check of the library's requirement catalog

_Pending. Results so far are logged in `searches.md` (Tool runs): 16 of the 118 catalog entries do not match the standard, and three Figure 3 edges in `distilled/normative.md` point differently from the figure (§5.1)._

## 8. Synthesis

_Pending._
