---
schema: "archdoc/v1"
id: RPT-0005-dimensions
title: "RPT-0005 dimensions: the search axes"
type: research
status: draft
version: "0.2.0"
date: "2026-10-05"
updated: "2026-10-05"
record: RPT-0005
---

# RPT-0005: search dimensions

The search axes for issue #39 (part A), which replaces #9. Each dimension is one section of `report.md`. This file is Phase 0 of the #39 playbook: it fixes the questions each section must answer and the exact columns of every table, so "complete" means the same thing to the author, the reviewer agent and the human reviewers.

The report feeds #16 (YAML knowledge objects) and #17 (final schema). It is evidence for DEC-001 (object model), DEC-002 (encoding and which formats we import), DEC-008 (CWE/NVD integration) and DEC-009 (generic-to-product mapping). It accepts nothing.

## What complete means: the tables

Every table below must be filled for every in-scope format before the report leaves draft. An empty cell is written as `—` (the format has no such thing) or `?` (not yet found); `?` blocks done.

### Table 1. Comparison table (report §1, one row per format)

| column | what goes in it |
|---|---|
| Format | name and the version pinned for this report |
| Family | weakness/vuln, score, applicability, threat/attack, threat model, requirement/control, composition |
| Steward | who maintains it, and how changes are governed |
| Core entities | the top-level object types, by the format's own names |
| Identifier scheme | how an entity is named (`CWE-79`, `CVE-2024-…`, STIX `type--UUID`, purl, …) and whether ids are stable |
| Encoding | serializations and the schema language (JSON Schema, XSD, OWL/RDF, YAML, Python classes, …) |
| Extension mechanism | how a user adds fields, types or local entries, or `—` if none |
| Licence | licence of the specification and of the data |
| Library record | record id and status (`stub` or `FX-1`) |

### Table 2. Concept crosswalk (report §8, the key artifact)

Rows are concepts. Columns are formats. A cell holds the format's element (path or class name) and a fidelity mark:

| mark | meaning |
|---|---|
| `=` | same concept, no loss on import |
| `≈` | close; import loses something (say what in a note) |
| `⊂` / `⊃` | the format's element is narrower / broader than ours |
| `ext` | absent, but the format's extension mechanism could carry it |
| `txt` | present only as prose, not machine-readable (for example a deprecated CWE entry naming its successor in its description) |
| `—` | absent and not extensible |

**Rows, part 1: ARCH-0001 §3 types.** Asset, Component, TrustBoundary, Weakness, Vulnerability, Threat, AttackStep, AttackPath/ThreatChain, Mitigation, RiskScore, Review, Product/ProductFamily.

**Rows, part 2: concepts the formats carry that ARCH-0001 §3 does not.** Candidates to confirm or drop during the survey: DataFlow, Requirement/Control, Applicability statement (VEX status and justification), Advisory/Remediation, Exploitation evidence (EPSS probability, known-exploited flag), Party (CNA, vendor, threat actor), DamageScenario and Assertion (both in the unaccepted LinkML draft), Software identifier (CPE, purl, SWID), Detection/Indicator. A row kept here is a gap-analysis input, not a proposal to add the type.

**Rows, part 3: cross-cutting fields.** Identifier, version/revision, status and deprecation, provenance (who asserted it, when), references, human review or approval state, edge qualifiers (properties a relation carries, such as CWE's `View_ID` or NVD's AND/OR and `negate`).

**Columns.** One per format. CVE and NVD are separate columns: they differ in steward, provenance model and applicability logic (pilot).

### Table 3. Relation crosswalk (report §8)

Same marks as Table 2. Rows are the typed edges of ARCH-0001 §3 (`exploits`, `mitigated_by`, `part_of`, `step_of`, `instance_of`, `reviewed_by`, `applies_to_product`, `supersedes`) plus edges the formats have that we lack (for example CWE `ChildOf`/`CanPrecede`, STIX `uses`/`mitigates`/`detects`, VEX `not_affected` with justification). ADR-0004 made the logical model edge-rich, so this table matters as much as Table 2. A cell also names the qualifiers the edge carries (scope, order, fit grade), because the pilot found that relations in CWE and NVD are not meaningful without them.

### Table 4. Adoption (report §9)

| column | what goes in it |
|---|---|
| Format | as in Table 1 |
| Produced by | products, services or databases that emit it |
| Consumed by | products that import it |
| Kind | open source / commercial / government |
| Evidence | a verified source for each claim (documentation, schema, release notes); vendor marketing alone is not evidence |
| As of | date checked |

Products already surveyed in RPT-0003 (#7) are reused, not re-researched.

### Table 5. Applicability rubric (report §1 and per-format sections)

Each format is rated on the five axes #39 sets, 0 to 3:

| axis | 3 means |
|---|---|
| Object model | its entities map onto ARCH-0001 §3 types with `=` or `≈` and little loss |
| Provenance/attribution | every statement carries who made it and when, natively |
| Human review/audit | it can record a human accept/reject decision and rationale |
| Federation | ids are globally unique and stable, records can be exchanged and merged across organizations |
| AI-grounding | an agent can cite an entry by a stable id and retrieve its normative text |

0 = absent, 1 = mentioned or weak, 2 = partial (needs extension), 3 = strong. Every rating cites the field or section that justifies it.

Ratings are within the format's own scope: a catalog such as CWE is not marked down on Object model for lacking Asset, and for a catalog the Provenance and Human review axes rate the editorial history of its entries (pilot).

### Table 6. Local extension needs (report §8)

| column | what goes in it |
|---|---|
| Need | the concept or field tmodel needs that the format lacks |
| Format | which format |
| Mechanism | the format's own extension point, if any |
| Local extension proposed | the minimum we would add (evidence only) |
| Routes to | the `DEC-*` or issue that decides it (#16, #17, DEC-001, DEC-002, …) |

## Dimensions

### 1. Weakness and vulnerability records
CWE, CVE (CVE JSON 5 record), NVD (API 2.0 and its CPE applicability data), OSV.
1. What are the entities, identifiers and required fields?
2. How does a record say which product and version is affected (CPE match configurations, purl ranges, `affected[]` with ranges)?
3. How does a CVE point to its CWE, and who made that assignment (CNA, ADP, NVD primary or secondary)?
4. How are updates, rejections and withdrawals represented?
5. **Extending CWE:** how can an organization add a weakness CWE does not have (custom id ranges, views, categories, a separate namespace), and what do existing tools do in practice?
6. How is the data distributed (bulk files, API, rate limits), relevant to DEC-008?

### 2. Scores and exploitation signals
CVSS (v3.1 and v4.0), EPSS.
1. How is a score structured (vector string, metric groups, versions), and where does it live (inside the CVE record, in NVD, separately)?
2. Who assigns it, and can there be several for one vulnerability?
3. What does each field mean for RiskScore inputs? Field mapping only; the risk scheme is DEC-003's question and out of scope.

### 3. Applicability and advisories
VEX as one concept with four encodings (OpenVEX, CSAF VEX profile, CycloneDX VEX, SPDX 3 Security profile), and CSAF as an advisory format.
1. What status values and justification codes does each encoding define, and do they agree?
2. How does each name the product and version a statement applies to?
3. How is a statement attributed, signed and superseded?
4. How does a VEX statement map onto tmodel's per-instance applicability (the `Assertion` plus `Review` pattern in the LinkML draft)? This is #17's "is CVE X applicable to product version Y" capability.

### 4. Threat and attack knowledge
MITRE ATT&CK, CAPEC, D3FEND (OWL), STIX 2.1 and TAXII 2.1.
1. What object and relationship types exist (STIX SDOs and SROs; ATT&CK tactics, techniques, sub-techniques; CAPEC patterns; D3FEND techniques and digital artifacts)?
2. How do they cross-reference each other (CAPEC to CWE, CAPEC to ATT&CK, D3FEND to ATT&CK through digital artifacts)? Who maintains each mapping, and how current is it?
3. How are deprecation and revocation represented?
4. How does STIX allow extension (extension definitions, custom properties), and how does ATT&CK use it?
5. Which of these are the catalogs behind ARCH-0001's Weakness, AttackPattern and Mitigation, and with what fidelity?

### 5. Threat-model object models
OTM (Open Threat Model), threagile YAML, pytm, OWASP Threat Dragon JSON.
1. How does each represent assets, components, data flows, trust boundaries, threats, mitigations and risk?
2. Does it reference CWE, CAPEC or ATT&CK ids, and how?
3. Can it carry review or approval state, owners, and status per threat?
4. Can one be converted into another, and what is lost? (OTM is used as an interchange format by some products.)
5. What is the schema's maturity (versioning, test fixtures, a published schema file)?

RPT-0001 and RPT-0003 already describe these as products. This section adds the schema-level detail they leave out.

### 6. Requirements, controls and assurance
OSCAL (catalog, profile, component definition, system security plan, assessment models), ReqIF 1.2, SysML v2 requirements, OMG SACM 2.x (assurance cases).
1. How is a requirement or control identified, parameterized and versioned?
2. How is it linked to the thing that implements it and to the evidence that it holds?
3. What trace links exist (satisfies, verifies, refines, derives)?
4. How do these map onto Mitigation, Review and a possible Requirement/Control concept?

RPT-0013 (SDL conformance) and MAP-0001 already use some of these; this section cites them and covers what they do not.

### 7. Composition: the security-relevant part
SPDX 3.0.1 and CycloneDX 1.7. RPT-0004 already covers naming, dependencies, completeness, hardware and build identity; that is not repeated.
1. How do vulnerabilities and VEX statements attach to components in each?
2. How do component identifiers (purl, CPE, SWID, hashes) map onto Product and Component?
3. Which other profiles or object types bear on threat modeling (for example the SPDX 3 Security, AI and Dataset profiles)?

### 8. Crosswalk and local extension (synthesis)
Assemble Tables 2, 3 and 6 from sections 1 to 7.
1. Which identifiers can serve as stable keys across formats (CVE id, CWE id, purl, CPE, ATT&CK id, STIX id)?
2. Where is the same concept named differently, and where does the same name mean different things?
3. What would be lost when importing each format into ARCH-0001's types? (Direct input to #16's round-trip test.)
4. Where must tmodel extend a format locally, and through which mechanism?

### 9. Adoption
Table 4. For each format, which products and services produce and consume it, with evidence.

### 10. Adversarial coverage review (Phase 4)
A fresh agent that did not write the draft checks:
1. **Coverage.** Against an independent list of formats, did we miss one that matters? Candidates to test against: CISA KEV, CPE, purl, SWID, OpenC2 (in #9, not in #39), MITRE ATLAS (covered by RPT-0014), CACAO, OCSF, MAEC, SARIF, OVAL/SCAP, VERIS, SSVC (already inside CVE ADP containers and the NVD API, found in the pilot), TM-BOM (emerging threat-model interchange, named in RPT-0003).
2. **Citations.** Is every claim traceable to a verified source?
3. **Extraction.** For each specification: count the normative statements first, then check that the library record extracted the same number.
4. **Crosswalk accuracy.** Spot-check a sample of cells against the specification text.

Findings are fed back through dimensions 1 to 9. Rejected findings and the reasons go in the design log.

## Per-format record

Each Phase 1 search returns, for every format: citation and verified URL, version, steward, entities, identifier scheme, encoding and schema file location, extension mechanism, licence, producers and consumers with evidence, the fields that map to each Table 2 row, the five-axis ratings with justification, and its library record id and status.

## Phase 1 plan

Agent count is capped at three per round to keep cost down (the #39 playbook suggests three to five).

1. **Pilot first, in the main session:** CWE, CVE/NVD and OTM, as #9's self-improving loop suggests. This tests Tables 2 and 5 on one catalog, one record format and one threat-model format before scaling. If the columns or marks do not work, this file is revised before the fan-out. **Done 2026-10-05:** results in [pilot.md](pilot.md); this file's version 0.2.0 carries its changes (the `txt` mark, edge qualifiers, separate CVE and NVD columns, the rubric scope note and two coverage candidates).
2. **Fan-out, three agents in parallel:**
   - agent 1: dimensions 1 to 3 (vulnerability data: CWE, CVE, NVD, OSV, CVSS, EPSS, VEX, CSAF)
   - agent 2: dimensions 4 and 7 (attack knowledge and composition: ATT&CK, CAPEC, D3FEND, STIX/TAXII, SPDX, CycloneDX)
   - agent 3: dimensions 5 and 6 (threat-model formats and requirements: OTM, threagile, pytm, Threat Dragon, OSCAL, ReqIF, SysML v2, SACM)
3. Dimensions 8 and 9 are assembled in the main session from the agents' results.

Every query goes in `searches.md` and every source in `sources.md`. URLs are verified by fetching them; nothing is cited from memory.

## Related reports (cite, do not redo)

| report | overlaps on |
|---|---|
| RPT-0001 landscape | first pass over schemas and object models (OTM, STIX, CWE, CAPEC) |
| RPT-0003 products | threat-modeling products and the formats they use (OTM, pytm, Threat Dragon) |
| RPT-0004 composition | CycloneDX, SPDX, OSV, CVE-to-component matching |
| RPT-0011 knowledge graphs | STIX, D3FEND and OSV as knowledge-graph sources |
| RPT-0013 SDL conformance | OSCAL, SysML v2, OMG SACM |
| RPT-0014 AI threat model | CWE AI entries, CAPEC, ATLAS and their crosswalks |

## Open scope questions (for @nymble)

1. OpenC2 was in #9 but is not in #39. Treat it as a coverage check only?
2. Should CPE, purl and CISA KEV be formats in their own right? They appear inside NVD, OSV and EPSS-adjacent data either way.
3. MITRE ATLAS: a column in the crosswalk, or cite RPT-0014 only?
4. Phase 2 needs the library's FX-1 tooling (`docs/extraction.md`, the `extract` skill, `bin/extract-scaffold`). It is on library branch `feat/sdl-references`, not on `main`. When will it merge, or should records be extracted against that branch?
