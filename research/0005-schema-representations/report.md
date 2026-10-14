---
schema: "archdoc/v1"
id: RPT-0005
title: "Schema representations of cybersecurity information"
short_title: "Schema representations"
description: "How the field encodes weaknesses, vulnerabilities, scores, applicability, attacks, threat models, requirements and composition; a cross-format crosswalk onto ARCH-0001's types and where local extension is needed. Evidence, not decisions."
type: research
category: security
status: draft
version: "0.2.0"
date: "2026-10-05"
updated: "2026-10-13"
authors:
  - role: student
    id: mai-li-mcghee
  - role: research
    id: ai-assisted
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0005-schema-representations/report.md
library_commit: "pending Phase 2 (record cwe extracted on Threat-Radar/library#21, unmerged)"
informs: [DEC-001, DEC-002, DEC-008, DEC-009]
open_decisions: [DEC-001, DEC-002, DEC-008, DEC-009]
issue: 39
---

# RPT-0005: Schema representations of cybersecurity information

**Status: draft 0.2.0.** Survey, crosswalk and gap analysis are written. Not yet done: library extraction (Phase 2, one record of about twenty), the adversarial review (Phase 4) and the clarity pass (Phase 6). Nothing here is accepted; every recommendation routes to an open `DEC-*` or issue.

## Overview

tmodel will import security data from formats it does not control, and may export to them (ARCH-0001 §5). This report surveys 24 of those formats in seven families, from weakness catalogs to software bills of materials, and asks of each: what it represents, how it names and versions things, how it can be extended, who uses it, and what is lost when it is mapped onto ARCH-0001's object model.

Three findings matter most for the object model:

1. **No surveyed format encodes ARCH-0001's Review exactly**, and none encodes an ordered attack path. These are the elements that most distinguish tmodel; they must be modelled natively and carried into other formats by extension.
2. **Attributed, multi-source statements are established practice.** CVE records, NVD, STIX, SPDX 3 and CycloneDX all keep several parties' claims side by side with who made them and when. This is evidence for the Assertion pattern in the unaccepted LinkML draft.
3. **Edges need properties.** Relations in every family carry a scope, order, fit grade, logic or justification that a bare typed edge loses (ADR-0004).

One external change bears directly on DEC-008: since April 2026, NIST's National Vulnerability Database enriches only a minority of CVEs, so CWE and product applicability must come mainly from the CVE record itself.

The method is in §12. The questions and table columns were fixed in [dimensions.md](dimensions.md) before the search; the evidence behind every cell is in [pilot.md](pilot.md) and the three `fanout-*.md` files; the crosswalk is assembled in [crosswalk.md](crosswalk.md).

## 1. Comparison and applicability

### Table 1. The formats compared

One row per format, pinned to the version surveyed. Per the sponsor's scope answer (#39, 2026-10-08), CPE and purl are treated as identifier schemes (§9) and CISA KEV as an annotation on a CVE (§3), not as formats; MITRE ATLAS gets one row and is covered by RPT-0014. The "Library record" column gives the record id and its status; Phase 2 moves each to FX-1 or an honest stub.

| Format | Family | Steward | Core entities | Identifier scheme | Encoding | Extension mechanism | Licence | Library record |
|---|---|---|---|---|---|---|---|---|
| CWE 4.20 / schema 7.3 | weakness | MITRE (CISA-sponsored); submissions to the CWE team | Weakness, Category, View | `CWE-<int>`, never reused | XML + XSD; CSV | — (closed XSD) | MITRE CWE terms, attribution | `cwe`, summarized |
| CVE Record Format 5.2.0 | vulnerability | CVE Program (Board; MITRE secretariat; CISA sponsor) | Record → CNA container + ADP containers | `CVE-YYYY-N{4,19}`; org UUIDs | JSON + JSON Schema draft-07 | `x_` properties and tags; `metrics.other`; `taxonomyMappings` | schema CC0-1.0; records ? | `cve-json-5`, summarized |
| NVD CVE API 2.0 | vulnerability (enrichment) | NIST | cve with weaknesses, metrics, configurations, KEV fields | CVE id; CPE 2.3; match UUIDs | JSON REST | — | ? | none |
| OSV schema 1.9.1 | vulnerability (open-source packages) | OpenSSF `ossf/osv-schema` (authors at Google); PR process | record; `affected[]` (package, ranges, versions); references; credits | `<DB>-<ID>` from a closed prefix list or `x_`; `ecosystem` enum (52) + name; optional purl | JSON + JSON Schema 2020-12 | `database_specific`, `ecosystem_specific`; `x_` ids | Apache-2.0 (schema); per-DB data (CC-BY 4.0, CC0, ...) | `osv-schema`, summarized |
| CVSS v3.1 / v4.0 | score | FIRST (CVSS-SIG) | score object (Base, Temporal/Threat, Environmental, Supplemental) | vector string `CVSS:3.1/...`, `CVSS:4.0/...`; no id | JSON Schema, XML Schema, vector text | — (closed; v4 `unevaluatedProperties: false`) | free use, attribution, publish score and vector | `first-cvss`, queued |
| EPSS | score (exploitation probability) | FIRST EPSS SIG; infrastructure by Empirical Security | (CVE, date) record: `epss`, `percentile` | CVE id; (id, date, model version) | CSV (gz), JSON API | — | free, attribution requested | none; new, Phase 2 |
| SSVC (SelectionList 2.0.0) | decision/score (method) | CERT/CC at CMU SEI; CISA tree | SelectionList; decision point selections | (namespace, key, version) per decision point | JSON Schema 2020-12 | namespaces for local decision points (schema `namespace` field) | mixed: CC BY-NC 4.0 text; MIT-style software; schema file ? | none; new, Phase 2 |
| OpenVEX 0.2.0 | applicability (VEX) | OpenVEX project (GitHub); no standards body | document; statement; product; subcomponent | document IRI `@id`; purl/CPE/hash for products; CVE-style `name` | JSON + JSON Schema 2020-12 | — (closed document; roadmap items for 1.0) | CC0-1.0 | none; new, Phase 2 |
| CSAF 2.0 (errata 01) / 2.1 (CSD03) | advisory + applicability (VEX profile) | OASIS CSAF TC | document; product_tree; vulnerabilities | `tracking.id` + publisher namespace; document-local `product_id`; CVE; `ids[]` | JSON + JSON Schema 2020-12 | 2.0 none; 2.1 `x_extensions` + metaschema | OASIS IPR (non-assertion); per-document `license_expression` (2.1) | none; new, Phase 2 |
| MITRE ATT&CK Enterprise 19.2 (ATT&CK spec 3.3.0) | threat/attack | MITRE; twice-yearly major releases plus minors; contribution process ? | tactic, technique/sub-technique, mitigation, group, software, campaign, detection strategy, analytic, data component (ICS: asset) | STIX `type--UUID` + ATT&CK id (`T1059.001`, `TA0005`, `M1031`, …); never reused; revoked/deprecated kept | STIX 2.1 JSON bundles; ADM Zod/TypeScript schema; TAXII 2.1 | STIX custom `x_mitre_*` properties and `x-mitre-*` objects (deprecated §11 route); Workbench org namespace for local ids | MITRE ATT&CK licence (royalty-free, attribution) | `mitre-attack`, summarized |
| CAPEC 3.9 / schema 3.5 | threat/attack | MITRE with the CAPEC community; last release 2023-01-24 | Attack_Pattern (Meta/Standard/Detailed), Category, View | `CAPEC-<int>`, never reused | XML + XSD; STIX 2.1 copy in `mitre/cti` | — (closed XSD) | CAPEC terms (royalty-free, attribution) | `capec`, summarized |
| D3FEND 1.6.0 | threat/attack (countermeasures) | MITRE NSEC, NSA-funded; GitHub issues/PRs | DefensiveTechnique, DefensiveTactic, DigitalArtifact, DigitalEvent, Agent; imported ATT&CK/ATLAS/SPARTA/CWE; NISTControl | class IRI + `d3fend-id` (`D3-TB`); `D3A-` ids not unique | OWL (RDF/XML, TTL, JSON-LD); inferred mappings as SPARQL CSV/JSON | open-world OWL import in own namespace | MIT (repo) + D3FEND terms (royalty-free, attribution) | `d3fend`, summarized |
| STIX 2.1 (OS 2021-06-10; Errata 01 at CSD01) | threat/attack (CTI exchange) | OASIS CTI TC | 19 SDOs, 2 SROs, 18 SCOs, extension-definition | `type--UUID`; version = id + `modified` | JSON; JSON Schema 2020-12 (non-normative repo) | `extension-definition` (new-sdo/sco/sro, property, toplevel-property); §11 custom properties deprecated | OASIS IPR Non-Assertion; schemas BSD-3-Clause | `stix-2-1`, summarized |
| TAXII 2.1 (OS 2021-06-10) | threat/attack (transport) | OASIS CTI TC | discovery, api-root, collection, manifest, envelope, versions, status | collection id/alias; STIX ids | HTTPS + JSON (`application/taxii+json;version=2.1`) | custom properties on resources (§7.1) | OASIS IPR Non-Assertion | none (new, Phase 2) |
| MITRE ATLAS (one row, per the sponsor) | threat/attack (AI systems) | MITRE | ATT&CK-shaped tactics and techniques for AI systems | see RPT-0014 | see RPT-0014 | see RPT-0014 | see RPT-0014 | not surveyed here |
| OTM 0.2.0 | threat model | IriusRisk | project, asset, trustZone, component, dataflow, threat, mitigation, representation | free strings, file-local | JSON/YAML + JSON Schema | `attributes` map; open objects | spec CC BY-SA 4.0; schema file Apache-2.0 | none |
| threagile (master `74e323ed`; tag v0.9.1) | threat model | Threagile GitHub org; PRs | data_assets, technical_assets (+ communication_links), trust_boundaries, shared_runtimes, risk categories, risks, risk_tracking | file-local keys; deterministic `category@element…` risk ids with wildcards in tracking | YAML + JSON Schema draft-07; JSON/PDF/XLSX out | `tags`; custom risk categories; risk scripts (under development) | MIT | none (new, Phase 2) |
| pytm 1.4.0 | threat model | OWASP; CODEOWNERS maintainers | Element subclasses, Boundary, Dataflow, Data, Controls, Threat, Finding, Assumption, TM | element `name`; seeded `uuid`; threat SID (`INP01`); per-run finding counter | Python (Pydantic v2) + JSON in/out; no schema file | `extra="allow"` attributes; custom `threatsFile` | MIT (+ CAPEC terms) | none (new, Phase 2) |
| OWASP Threat Dragon 2.6.2 (schema v2) | threat model | OWASP | summary, detail, diagrams, cells (Actor, Process, Store, Flow, Boundary, BoundaryBox, Text), per-cell threats | UUIDs per cell and threat; file-local | JSON + JSON Schema (open; warn-only) | — (open schema; `compatibility` block on `main`) | Apache-2.0 | none (new, Phase 2) |
| OSCAL 1.2.3 | requirement/control | NIST; GitHub | catalog, profile, component-definition, SSP, assessment-plan, assessment-results, POA&M, mapping-collection | UUIDs everywhere; control token ids within a catalog (`ac-2.10`) | XML/JSON/YAML from Metaschema; XSD + JSON Schema | namespaced `props`, `links`, `parts` (`ns`) | US public domain + CC0 1.0 | none (new, Phase 2) |
| ReqIF 1.2 | requirement/control | OMG (from HIS / ProSTEP iViP RIF) | SpecObject, SpecRelation, Specification/SpecHierarchy, RelationGroup, SpecTypes, Datatypes | `IDENTIFIER` xsd:ID, globally unique, lifetime immutable | XML + XSD (+ CMOF) | user-defined types; `REQ-IF-TOOL-EXTENSION` (`xsd:any ##other`) | OMG spec, IPR RF-Limited | none (new, Phase 2) |
| SysML v2.0 (requirements) | requirement/control (systems model) | OMG; SST pilot on GitHub | RequirementDefinition/Usage, Concern, SatisfyRequirementUsage, VerificationCase, Derivation, Dependency, Allocation, MetadataUsage | `elementId` (global, immutable) + `reqId` short name | textual `.sysml`, JSON (2020-12), XMI, `.kpar`, REST API | `metadata def`, user libraries | OMG spec, IPR Non-Assert; pilot EPL-2.0 | none (new, Phase 2) |
| OMG SACM 2.3 | assurance | OMG; RTF (MITRE, Cambridge, York) | ArgumentPackage, Claim, ArgumentReasoning, AssertedRelationship family, ArtifactReference, Artifact, Activity, Participant, Event, Term | `gid` unique within a model instance; citations across packages | XMI (MOF/UML) + UML profile | TaggedValue, ImplementationConstraint, Term.externalReference | OMG spec, IPR Non-Assert | none (new, Phase 2) |
| SPDX 3.0.1 (Security, AI, Dataset profiles) | composition | Linux Foundation SPDX project; ISO/IEC DIS 5962 | Vulnerability, VulnAssessmentRelationship (VEX ×4, CVSS ×3, EPSS, ExploitCatalog, SSVC), AIPackage, DatasetPackage, Annotation | `spdxId` IRI; typed `externalIdentifier` | OWL + SHACL; JSON-LD + JSON Schema | Extension profile (`Extension` subclasses, `CdxPropertiesExtension`) | CC-BY-3.0 + Community Specification License 1.0 | `spdx-3-0-1`, queued |
| CycloneDX 1.7 (schema 1.7.2) | composition | OWASP + Ecma TC54 (ECMA-424 2nd ed.) | vulnerabilities (analysis, affects), services (trustZone, data flows), annotations, declarations, definitions, citations | `serialNumber`/`version` + local `bom-ref`; BOM-Link | JSON (draft-07), XML, Protobuf | `properties` name-value + Property Taxonomy | Apache-2.0 | `cyclonedx-1-7`, queued |

### Table 5. Applicability to tmodel

Each format is rated 0 (absent) to 3 (strong) on the five axes #39 sets, within the format's own scope (dimensions.md). Each rating cites the field that justifies it.

| Format | Object model | Provenance | Human review | Federation | AI-grounding |
|---|---|---|---|---|---|
| CWE | 3: Weakness `=`; Mitigation, Chain `≈` | 2: per-entry `Content_History`, not per relation | 1: `Status` and `Mapping_Notes` rationale, no decision record | 2: stable global ids, but one authority mints them | 3: stable id, versioned normative text, bulk XML |
| CVE 5.2.0 | 2: Vulnerability, Product `=`; mitigations and exploits in prose | 3: every container attributed and dated | 1: `disputed`, REJECTED only | 3: global ids, multi-org containers by design | 3: stable ids, bulk repo and API |
| NVD API 2.0 | 2: adds configurations and KEV fields | 2: `source` and `type` per weakness and score, no date | 1: `vulnStatus` is NVD's workflow, no rationale | 2: keyed on CVE id, single authority, read-only | 2: stable ids, but enrichment now sparse (2026-04) |
| OSV 1.9.1 | 2: `affected[].package` + `ranges` ≈ Product applicability; no not-affected, no weakness field | 2: `severity[].source`, per-record `modified` and DB prefix; no per-field author | 1: no review field; only `database_specific.github_reviewed` | 3: DB-prefixed ids, `aliases`, `upstream`, `related`, `x_` local DBs, `modified` latest-wins merge rule | 3: stable ids, API without rate limit, versioned bucket, normative `IsVulnerable` text |
| CVSS | 2: RiskScore inputs `=` (Base/Threat/Environmental); `scope` ⊂ TrustBoundary | 0: no author or date in `cvss-v3.1.json` / `cvss-v4.0.json` | 0: none | 2: vector string is globally meaningful but not an id; no registry of scores | 3: spec text and formulas public, schema versioned, vector parsable |
| EPSS | 1: one RiskScore input (probability), CVE-keyed only | 1: single source (FIRST); only CSV header `score_date`, `model_version` | 0: none | 2: CVE-keyed, daily, free; one producer | 2: stable CVE key and API with date; no per-score id, model changes daily |
| SSVC | 1: a decision outcome; decision points are not ARCH-0001 types | 2: `timestamp`, `role` when embedded (CISA Coordinator) | 1: a decision method, not a review record | 2: namespaced decision points, `target_ids` | 2: schema versioned; the decision-point catalogue was not read (?) |
| OpenVEX 0.2.0 | 3: Applicability `=`, Component `≈`; no version range | 2: `author`, `role`, `timestamp`, `tooling` per document/statement; strings only | 1: `status_notes`, `impact_statement`; no reviewer | 2: IRIs for docs, purl/CPE for products; statements can be re-used; no federation rules until 1.0 | 2: `@id` optional on statements; spec is short and normative (MUST/SHOULD) |
| CSAF 2.0 / 2.1 | 3: Product (`product_tree`) `=`, Applicability `=`, Mitigation `≈`, per-product scores | 3: `publisher`, `tracking.revision_history`, signature files; 2.1 `involvement`; statements dated per array | 2: `tracking.status` draft/interim/final and revision summaries; no accept/reject decision | 3: publisher namespaces, provider-metadata, ROLIE, aggregators (BSI lists 14 providers) | 3: stable `tracking.id`, signed documents, normative spec with 2.0 errata |
| ATT&CK 19.2 | 2: `attack-pattern` ≈ Threat/AttackStep, `course-of-action` ≈ Mitigation, detection =; no Weakness link, no path | 3: every relationship is an SRO with `created`, `modified`, `created_by_ref` and citations in `external_references` (18,960 of 21,262) | 1: only `revoked`/`x_mitre_deprecated`; no status or review | 2: global STIX UUIDs and TAXII distribution, but one minting authority and ids that change meaning (`TA0005`) | 3: stable T-ids and STIX ids, per-release bundles and per-release TAXII roots, normative `description` text |
| CAPEC 3.9 | 2: `Attack_Pattern` ≈ Threat, `Attack_Step` ≈, `Related_Weakness` ⊂, mitigations txt | 2: per-entry `Content_History` (submission, modifications, importance), not per relation | 1: `Status` is editorial maturity (402 of 615 Draft); no decision record | 2: stable integer ids, one authority; STIX copy adds UUIDs | 2: stable ids and bulk XML, but frozen since 2023-01-24 with ATT&CK mappings from ATT&CK 12.0 |
| D3FEND 1.6.0 | 2: `DefensiveTechnique` = Mitigation; `DigitalArtifact` ≈ Asset/Component (types); offence links only inferred | 1: `kb-reference` (author, organization) per technique; no per-assertion creator or date; release CHANGELOG | 0: no status, review or editorial history per class; only `owl:deprecated` | 2: resolvable IRIs, OWL import by design; but IRIs renamed without tombstones and 27 `D3A-` ids collide | 2: IRI, `d3fend-id`, `d3f:definition`, `kb-article`, `versionIRI`; one `D3-` id change in 247 between 1.2.0 and 1.6.0 |
| STIX 2.1 | 2: attack-pattern, course-of-action (stub), vulnerability, infrastructure, indicator ≈; no Weakness, path, risk, product applicability | 3: `created_by_ref`, `created`, `modified`, `confidence` on every SDO and SRO; object-creator rules §3.5 | 2: `opinion` (5-point enum, `explanation`, `authors`, `object_refs`), `note`; no accept/reject or impact | 3: `type--UUID`, versioning and revocation rules, re-publisher must mint new id, `duplicate-of`, TAXII exchange | 2: stable ids and normative spec; grounding depends on the content carried |
| TAXII 2.1 | 0: transport; carries STIX | 1: manifest `date_added`, `version` only | 0: none | 3: discovery, API roots, collections, `match[id]`/`match[version]`, cross-org use (CISA AIS) | 2: retrieval by id and version; retention undefined (§1.6.11) |
| OTM 0.2.0 | 2: system-side types `=`; no attack side | 1: `project.owner` only | 1: free-string `state` | 1: file-local ids; exchange yes, merge no | 1: no catalog; CWE ids as strings |
| threagile | 2: Asset, Component, TrustBoundary, DataFlow `=`; Threat `≈` (category + `Risk`); no attack side, mitigations prose | 1: model `author`/`contributors`; `checked_by` + `date` only on `risk_tracking` entries; generated risks unattributed | 3: `risk_tracking` records status (incl. accepted, false-positive), `justification`, `checked_by`, `date`, `ticket` (risks only) | 1: file-local ids; deterministic `synthetic_id` helps diffing but has no namespace | 2: stable built-in category ids with prose and one `cwe` each, but 15 of 42 CWE links are Prohibited ids |
| pytm 1.4.0 | 2: `Element` subclasses, `Boundary`, `Dataflow` `=`; `Threat`/`Finding` split `=`; mitigation only as `Controls` flags | 0: no author, owner or date anywhere in `TM`, `Element` or `Finding` | 2: `overrides[].response` and `Assumption.exclude` + `description` record decisions with rationale, no who or when | 1: names as ids; per-run `Finding.id` counter; seeded `uuid` depends on creation order | 2: stable threat SIDs with normative text in `threats.json`; CWE/CAPEC only inside a `references` string |
| Threat Dragon 2.6.2 | 2: Actor/Process/Store/Flow/Boundary `=`/`≈`; threats instance-only, no asset object | 1: model `owner`, `reviewer`, `contributors` only | 1: per-threat `status` (3 values), no rationale field; one `reviewer` per model | 1: UUIDs, but file-local semantics and geometric containment | 1: `type` names a STRIDE/LINDDUN category, no catalog ids |
| OSCAL 1.2.3 | 3: `control`, `implemented-requirement`/`by-component`, `component`, `risk`, `finding` cover Requirement/Control, Mitigation, Review | 3: `origins[].actors` (tool, assessment-platform, party) on findings, observations, risks; `risk-log.logged-by`; `metadata.actions` | 3: `finding.target.status` (satisfied/not-satisfied + reason), `attestations`, `actions` (approval), risk `deviation-approved` | 3: UUIDs "consistently used … across revisions"; profiles and leveraged authorizations designed for cross-organization exchange; mapping model | 3: SP 800-53 controls citable by id (`ac-2`) with versioned normative `parts`; withdrawals machine-linked |
| ReqIF 1.2 | 2: generic `SPEC-OBJECT`/`SPEC-RELATION` carry requirements, but every type and link meaning is user-defined | 1: `LAST-CHANGE` per element, exporting tool ids; no author | 1: only a user-defined status enumeration; `IS-EDITABLE` access control | 3: `IDENTIFIER` "must be globally unique", "lifetime immutable"; built for cross-company exchange | 1: no shared catalog; content is whatever the partner exported |
| SysML v2.0 | 2: Requirement, satisfy, verify, derive, refine `=`; Component, DataFlow `=`; no security types | 1: `StatusInfo.originator`/`owner`; API commits have `created` but no author | 2: `VerdictKind`, `StatusInfo.status`, `Rationale`, no reviewer or decision record | 2: global immutable `elementId`; projects, branches, commits in a standard API; cross-model merge not examined | 1: stable library names, but no security catalog to cite |
| OMG SACM 2.3 | 1: argument and evidence only; maps to Review/assurance, not to system or threat types | 2: `Participant`, `Activity`, `Event`, `Artifact.version`/`date`, linked by relationships, not on assertions | 2: `AssertionDeclaration` (needsSupport, assumed, defeated, …) and `isCounter`; no reviewer or date on a claim | 2: `gid` unique only within a model; package interfaces and citations for modular exchange | 1: `Term.externalReference` only |
| SPDX 3.0.1 (security) | 2: Vulnerability =, Package = Component, VEX = applicability, scores ≈; no Threat, AttackStep, Mitigation | 3: `creationInfo` (createdBy, created) required on every element, `suppliedBy` and times on each assessment; document-inheritance rule for VEX | 2: `Annotation` with `annotationType: review`; no verdict or impact field | 3: `spdxId` IRIs, cross-document references, `externalIdentifier.issuingAuthority` | 2: global element ids and CVE/CWE/purl ids; no catalog text of its own |
| CycloneDX 1.7 (security) | 2: Component/Service =, Vulnerability =, applicability =, DataFlow =, TrustBoundary ≈; no Threat or AttackStep | 2: `citations[]` can attribute any field (pointer, `attributedTo`, `timestamp`) but is optional; `analysis` has no author | 2: `annotations[]`, `declarations.affirmation`, `attestations` with rationale, `evidence.reviewer`; no verdict enum | 2: `bom-ref` is document-local; BOM-Link and `serialNumber` UUID for cross-BOM references | 1: no catalog; ids local to a BOM; references CVE/CWE ids |

Read across the columns:

- **Human review is the weakest axis.** Only OSCAL and threagile score 3. OSCAL records findings, attestations and approval actions; threagile records a per-risk status with justification, reviewer and date. Neither carries the human-assigned impact that ARCH-0001 §7 requires, which is why both are `≈`, not `=`, for Review in the crosswalk.
- **The threat-model formats score lowest on provenance, federation and AI-grounding.** OTM, threagile, pytm and Threat Dragon use file-local ids and record little about who asserted what. They were built for one team's model, not for exchange.
- **The standards-body formats score highest.** OSCAL scores 3 on every axis; CSAF, STIX and SPDX 3 follow. All three are maintained by a standards body or government with a published schema and stable global identifiers.

## 2. Weakness and vulnerability records

**CWE 4.20** (MITRE; record `cwe`, FX-1 on library#21). A catalog of 969 weakness types in a closed XML schema.
- Every entry says whether it may be used to map a real vulnerability (`Mapping_Notes/Usage`: Allowed, Allowed-with-Review, Discouraged, Prohibited), so a tmodel import can check its own mappings.
- Relations are scoped to a view: `ChildOf` in one view can differ from `ChildOf` in another, and `ChildOf` means "is a kind of", not "is part of".
- A deprecated entry names its successor only in prose, and provenance is recorded per entry, not per relation.
- There is no extension point, so a local weakness needs its own namespace, linked to CWE by a fit-graded mapping.
- The FX-1 extraction found 16 places where the schema's documentation contradicts its own structure.

**CVE Record Format 5.2.0** (CVE Program; record `cve-json-5`). One record per vulnerability, with one container from the assigning CNA and any number from Authorized Data Publishers.
- Several organizations assert facts about one vulnerability side by side, each container attributed and dated. In CVE-2021-44228 the CNA gives CWE ids and a text severity, CISA's container adds a CVSS score and an SSVC decision, and NVD separately assigns a different CWE.
- Product applicability is version-range logic with a status per range, and since 5.2.0 a purl.
- A rejected record names its replacement in `replacedBy`; disputes are tags.

**NVD CVE API 2.0** (NIST; no record yet). Enrichment of CVE records.
- Each CWE and score carries its source and a Primary or Secondary role.
- Applicability is boolean CPE logic (AND, OR, negate), richer than a single `applies_to_product` edge.
- CISA KEV membership is carried inline.
- **Enrichment is now the exception:** NIST announced on 2026-04-15 that it enriches only KEV, federal and critical-software CVEs. Of 102 CVEs published on 2026-09-20, 2 had NVD product configurations and none had an NVD-assigned CWE. NVD also uses two placeholder weaknesses, `NVD-CWE-noinfo` and `NVD-CWE-Other`, on up to one CVE in six.

**OSV 1.9.1** (OpenSSF; record `osv-schema`). The open-source vulnerability format.
- Applicability is a typed version timeline per package, not a status per product.
- Several databases describe the same vulnerability and are linked through `aliases`.
- There is no weakness field, and withdrawal has no successor.
- purl names the package, not the instance.

## 3. Scores and exploitation signals

**CVSS 3.1 and 4.0** (FIRST; records `first-cvss`, `first-cvss-v3-1`, `first-cvss-v4-0`).
- A score is a vector string in metric groups, and several scores per vulnerability are normal.
- The score carries no author; attribution comes from where it is stored.
- v3.1's `scope` and v4.0's subsequent-system impacts record that an impact crosses a security authority. This is a property of the vulnerability, not a trust boundary in the model.

**EPSS** (FIRST; no record yet).
- A probability of exploitation in the next 30 days, which is not a severity.
- Scores are published daily, so every score has a date; the percentile is a rank, not a second probability.

**SSVC** (CISA; scope open). A decision model. Its `Exploitation` value already appears inside CVE records from CISA's ADP container and in the NVD API.

**CISA KEV** (annotation, per the sponsor). A curated list of CVEs known to be exploited. NVD carries its fields inline, and SPDX 3 has an exploit-catalog relationship for it. In tmodel it belongs as an attributed assertion on a Vulnerability.

## 4. Applicability and advisories (VEX and CSAF)

VEX is one concept, "is this product affected by this vulnerability, and why", in four encodings. §8 of [fanout-vuln-data.md](fanout-vuln-data.md) compares them side by side.

- **Status and justification agree in three encodings.** OpenVEX, CSAF and SPDX 3 use the same five justification codes. CycloneDX uses nine different ones, so mapping it is lossy.
- **No encoding has a review field** for a human's accept or reject of a statement.
- **Product naming differs.** OpenVEX has no version ranges; CSAF has the richest product identification; SPDX 3 makes product versus subcomponent explicit.
- **Supersession is weak.** OpenVEX supersedes by time, CSAF by document revision and CycloneDX by BOM version. OpenVEX and CycloneDX statements may have no id at all.

**CSAF 2.0 / 2.1** (OASIS; no record yet). A full advisory format in which VEX is one profile. The lifecycle is per document, not per statement. CSAF 2.1 is a Committee Specification Draft (2026-09-11), not yet an OASIS Standard.

## 5. Threat and attack knowledge

**MITRE ATT&CK 19.2** (record `mitre-attack`).
- Relations are first-class objects with their own citations, and revocation names its successor (`revoked-by`).
- **ATT&CK no longer links to CAPEC:** no active technique has carried a CAPEC reference since v13.
- An id can change meaning without being revoked (`TA0005`), so every mapping must pin the ATT&CK version.
- Detection is now its own layer. There are no paths and no ordering of techniques.

**CAPEC 3.9** (record `capec`).
- Frozen since 2023-01-24, with its ATT&CK mappings pinned to ATT&CK 12.0.
- The CAPEC-to-CWE link is the one maintained on both sides.
- Its execution flow (`Attack_Step`) is the nearest thing to an AttackStep in any released format.
- Deprecation names its successor only in prose, as in CWE.

**D3FEND 1.6.0** (record `d3fend`).
- Defence-to-offence links are not stated in the ontology. They are inferred through shared digital artifacts and published separately.
- Its coverage of ATT&CK 19.2 is partial.
- Digital artifacts are the closest catalog to Asset and Component types.
- Neither key is fully stable: IRIs are renamed between releases, and 27 `D3A-` ids collide.

**STIX 2.1 and TAXII 2.1** (OASIS; records `stix-2-1`, none for TAXII).
- STIX carries provenance and versioning in every object, and its `opinion` object is a native carrier for agreement, though not for tmodel's verdict.
- STIX has no weakness, attack path, risk or product applicability.
- ATT&CK still uses STIX's deprecated custom-property route rather than extension definitions.
- TAXII is a transport, not a model, and leaves retention undefined.

**MITRE ATLAS** reuses ATT&CK's structure for AI systems. Its coverage is RPT-0014's.

## 6. Threat-model object models

**OTM 0.2.0** (IriusRisk; record `open-threat-model`). The closest format to ARCH-0001's system side: assets, components, trust zones, data flows, and threats separated from their per-component instances.
- Nothing on the attack side, and state without review.
- Trust boundaries are zones.
- A vendor-controlled 0.x schema since 2023, though it is used across vendors (IriusRisk, StartLeft, Devici to SD Elements).

**threagile** (latest tag v0.9.1; record `threagile`).
- The only threat-model format with a real review record (`risk_tracking`: status, justification, reviewer, date).
- Generic risks are instantiated by rule.
- 15 of the 42 CWE links in its built-in risk categories point to ids CWE marks Prohibited for mapping.
- Its published schema and its code disagree.

**pytm 1.4.0** (OWASP; no record yet). Threats are rules and mitigations are flags, so an unset control and a false one look the same. References are plain strings. Its licence is MIT (RPT-0003 gives GPL-3.0; to be corrected there).

**OWASP Threat Dragon 2.6.2** (no record yet). The published schema does not validate threats. Review is model-level only, threat type is a category rather than a threat, and containment in a boundary is geometric. The converters in its source tree do not work at 2.6.2.

**What converting between them loses** is in §8 of [fanout-models-requirements.md](fanout-models-requirements.md). In short, every conversion drops review state, and all four lack the attack side.

## 7. Requirements, controls and assurance

**OSCAL 1.2.3** (NIST; no record yet). The only format rated 3 on all five axes.
- Withdrawal names its successor, parameters are structured, and implementation and evidence are separate, linked objects.
- Risks are first-class and carry threat ids, and provenance is native.
- Cross-framework mapping is now standard.
- It has no system model (no trust boundary or data flow), so it complements a threat model rather than replacing one.

**ReqIF 1.2** (OMG; no record yet). Strong identity (globally unique, lifetime-immutable ids) and change tracking. Every type and link meaning is user-defined, so trace semantics need a published profile.

**SysML v2.0** (OMG; no record yet). All four trace links (satisfy, verify, derive, refine) are typed, and satisfaction is a logical claim that can be negated. Status and rationale are library metadata. It has no security vocabulary; product-line variants are part of the language.

**OMG SACM 2.3** (no record yet). Assurance cases.
- Claim states (`needsSupport`, `assumed`, `defeated`, …) are a review vocabulary, and counter-evidence is native.
- Who and when are recorded on artifacts, not on claims.
- The specification and its normative XMI disagree on one class name.

## 8. Composition: the security-relevant part

RPT-0004 covers naming, dependencies and build identity; this section covers only vulnerabilities, VEX and review.

**SPDX 3.0.1** (record `spdx-3-0-1`, queued).
- A VEX statement or score is a relationship element with its own creator and time.
- Human review has a slot (`Annotation` of type review), but no verdict.
- Threat models are only referenced.
- The AI and Dataset profiles add asset properties.
- Producers exist; consumers were not found.

**CycloneDX 1.7** (record `cyclonedx-1-7`, queued).
- Models the system side of a threat model: services, trust zones and data flows.
- Per-field provenance (`citations`) arrived in 1.7.
- Review, claims and attestations exist, but without a verdict.
- Threat models are carried by reference; tool support for its VEX is real.
- CycloneDX 2.0 adds threat-model modules (TM-BOM: threats, attack trees, ordered attack paths, requirements, controls). These are merged into the development branch but unreleased: the 2.0 milestone passed its 2026-08-31 date with 90 of 176 issues open.

## 9. Crosswalk and local extension

The full crosswalk, with its method, is [crosswalk.md](crosswalk.md). Its main matrix, ARCH-0001's types against all 24 formats (`=` same, `≈` close, `⊂`/`⊃` narrower/broader, `txt` prose only, `ext` extensible, `—` absent):

| Format | Asset | Comp. | Trust bnd. | Weak. | Vuln. | Threat | Att. step | Att. path | Mitig. | Risk | Review | Product | `=` | `≈⊂⊃` | `txt` | `ext` | `—` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Weakness and vulnerability** | | | | | | | | | | | | | | | | | |
| CWE 4.20 | — | — | — | = | ⊂ | — | — | ≈ | ≈ | ≈ | ⊂ | ⊃ | 1 | 6 | 0 | 0 | 5 |
| CVE 5.2.0 | — | ⊂ | — | ⊂ | = | — | txt | — | txt | ≈ | ⊂ | = | 2 | 4 | 2 | 0 | 4 |
| NVD API 2.0 | — | — | — | ⊂ | = | — | — | — | txt | ≈ | ⊂ | = | 2 | 3 | 1 | 0 | 6 |
| OSV 1.9.1 | — | ≈ | — | — | = | — | txt | — | ≈ | ≈ | ext | ≈ | 1 | 4 | 1 | 1 | 5 |
| **Scores and signals** | | | | | | | | | | | | | | | | | |
| CVSS 3.1 / 4.0 | ⊂ | — | ⊂ | — | — | — | ⊂ | — | ⊂ | = | — | — | 1 | 4 | 0 | 0 | 7 |
| EPSS | — | — | — | — | ⊂ | — | — | — | — | ≈ | — | — | 0 | 2 | 0 | 0 | 10 |
| SSVC (scope open) | ? | — | — | — | ⊂ | — | — | — | ? | ≈ | — | — | 0 | 2 | 0 | 0 | 8 |
| **Applicability and advisories** | | | | | | | | | | | | | | | | | |
| OpenVEX 0.2.0 | — | ≈ | — | — | ⊂ | — | — | — | ≈ | — | — | ≈ | 0 | 4 | 0 | 0 | 8 |
| CSAF 2.0 / 2.1 | — | ≈ | — | ⊂ | = | txt | — | — | ≈ | ≈ | ⊂ | = | 2 | 5 | 1 | 0 | 4 |
| **Threat and attack knowledge** | | | | | | | | | | | | | | | | | |
| ATT&CK 19.2 | — | ⊃ | — | — | txt | ≈ | ≈ | — | ≈ | — | — | ⊃ | 0 | 5 | 1 | 0 | 6 |
| CAPEC 3.9 | — | — | — | ⊂ | txt | ≈ | ≈ | ≈ | txt | ≈ | ⊂ | — | 0 | 6 | 2 | 0 | 4 |
| D3FEND 1.6.0 | ≈ | ≈ | — | = | — | ≈ | ≈ | — | = | — | — | — | 2 | 4 | 0 | 0 | 6 |
| STIX 2.1 | ≈ | ≈ | ext | ext | ≈ | ≈ | ≈ | ext | ≈ | ext | ≈ | ⊂ | 0 | 8 | 0 | 4 | 0 |
| TAXII 2.1 | — | — | — | — | — | — | — | — | — | — | — | — | 0 | 0 | 0 | 0 | 12 |
| **Threat-model formats** | | | | | | | | | | | | | | | | | |
| OTM 0.2.0 | = | = | ≈ | ⊂ | — | ≈ | — | — | = | ≈ | ⊂ | — | 3 | 5 | 0 | 0 | 4 |
| threagile (master) | = | = | = | ⊂ | — | ≈ | txt | — | txt | ≈ | ≈ | — | 3 | 4 | 2 | 0 | 3 |
| pytm 1.4.0 | ≈ | = | ≈ | txt | txt | = | — | — | ≈ | ≈ | ⊂ | — | 2 | 5 | 2 | 0 | 3 |
| Threat Dragon 2.6.2 | ⊂ | = | ≈ | — | — | ⊂ | — | — | txt | ≈ | ⊂ | — | 1 | 5 | 1 | 0 | 5 |
| **Requirements and assurance** | | | | | | | | | | | | | | | | | |
| OSCAL 1.2.3 | ≈ | = | txt | ext | ≈ | ⊂ | — | — | = | ≈ | ≈ | ≈ | 2 | 6 | 1 | 1 | 2 |
| ReqIF 1.2 | ext | ext | ext | ext | ext | ext | ext | ext | ext | ext | ext | — | 0 | 0 | 0 | 11 | 1 |
| SysML v2.0 | ext | = | ext | ext | ext | ext | ext | ext | ≈ | ⊃ | ≈ | ≈ | 1 | 4 | 0 | 7 | 0 |
| OMG SACM 2.3 | — | — | — | — | — | — | — | — | — | — | ≈ | — | 0 | 1 | 0 | 0 | 11 |
| **Composition (security part)** | | | | | | | | | | | | | | | | | |
| SPDX 3.0.1 | ≈ | = | ext | ⊂ | = | ⊃ | — | — | txt | ≈ | ≈ | = | 3 | 5 | 1 | 1 | 2 |
| CycloneDX 1.7 | ≈ | = | ≈ | ⊂ | = | ⊃ | txt | — | txt | ≈ | ≈ | = | 3 | 6 | 2 | 0 | 1 |
| **formats with `=`** | **2** | **8** | **1** | **2** | **6** | **1** | **0** | **0** | **3** | **1** | **0** | **5** | | | | | |

What the matrix shows:

- **Review has no exact match in any of the 24 formats.** Eight carry something narrower (`⊂`), usually an editorial or workflow status: CWE and CAPEC `Status`, NVD `vulnStatus`, OTM `state`. Seven carry something close (`≈`), such as STIX `opinion`, threagile `risk_tracking` and OSCAL findings. ARCH-0001 §7's Review (reviewer, date, verdict, assigned impact and rationale on any element) has no ready-made encoding to import or export.
- **The attack side is the thinnest.** AttackStep has no exact match. AttackPath has none either: 19 formats lack it, and the two `≈` are ordered weakness or pattern sequences in CWE and CAPEC, not attacker steps. CycloneDX 2.0's threat module (TM-BOM) has an ordered `attackPath` but is unreleased (fanout-models-requirements.md §9).
- **The system side is well covered.** Component has 8 exact matches and Product 5. Vulnerability has 6 exact matches.
- **TrustBoundary and Threat each have one exact match** (threagile and pytm). Elsewhere a boundary is a zone (OTM, pytm), a drawn shape whose membership is geometric (Threat Dragon) or a property of a service (CycloneDX). A threat is either a generic library entry or a per-element instance; few formats keep both.
- **Weakness has two exact matches** (CWE, and D3FEND's imported CWE classes); eight formats reference a CWE id (`⊂`).

## Table 2, part 2: concepts ARCH-0001 §3 does not have

Candidates for the gap analysis, not proposals to add types. Assumption and Verification/Evidence were proposed by the requirements survey and assessed only there.

| Format | Data flow | Req./control | Applic. | Advisory | Exploit. ev. | Party | Damage sc. | Assertion | Detection | Assumption | Verif./evid. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Weakness and vulnerability** | | | | | | | | | | | |
| CWE 4.20 | — | — | — | ∅ | — | ≈ | ∅ | — | ≈ | ∅ | ∅ |
| CVE 5.2.0 | — | — | ≈ | ∅ | txt | = | ∅ | = | — | ∅ | ∅ |
| NVD API 2.0 | — | — | ≈ | ∅ | = | ≈ | ∅ | ≈ | — | ∅ | ∅ |
| OSV 1.9.1 | — | — | ≈ | ≈ | — | ≈ | — | ≈ | txt | ∅ | ∅ |
| **Scores and signals** | | | | | | | | | | | |
| CVSS 3.1 / 4.0 | — | ⊂ | — | — | ≈ | — | ⊂ | — | — | ∅ | ∅ |
| EPSS | — | — | — | — | = | — | — | ≈ | — | ∅ | ∅ |
| SSVC (scope open) | — | — | — | — | ≈ | ⊂ | ⊂ | ≈ | — | ∅ | ∅ |
| **Applicability and advisories** | | | | | | | | | | | |
| OpenVEX 0.2.0 | — | — | = | txt | — | ⊂ | txt | = | — | ∅ | ∅ |
| CSAF 2.0 / 2.1 | — | — | = | = | txt | = | txt | ⊃ | — | ∅ | ∅ |
| **Threat and attack knowledge** | | | | | | | | | | | |
| ATT&CK 19.2 | — | — | — | — | ≈ | = | ⊂ | ≈ | = | ∅ | ∅ |
| CAPEC 3.9 | — | — | txt | — | txt | ≈ | ≈ | — | txt | ∅ | ∅ |
| D3FEND 1.6.0 | ≈ | ≈ | — | — | — | ⊂ | — | ≈ | ≈ | ∅ | ∅ |
| STIX 2.1 | ⊂ | — | ext | ⊃ | ≈ | = | — | = | = | ∅ | ∅ |
| TAXII 2.1 | — | — | — | — | — | — | — | ⊂ | — | ∅ | ∅ |
| **Threat-model formats** | | | | | | | | | | | |
| OTM 0.2.0 | = | — | — | ∅ | — | ⊂ | ∅ | — | — | ∅ | ∅ |
| threagile (master) | = | txt | ≈ | — | — | ≈ | txt | — | txt | txt | ∅ |
| pytm 1.4.0 | = | ⊂ | ≈ | — | — | — | txt | — | — | = | ∅ |
| Threat Dragon 2.6.2 | = | — | ≈ | — | — | ≈ | — | — | — | — | ∅ |
| **Requirements and assurance** | | | | | | | | | | | |
| OSCAL 1.2.3 | txt | = | ≈ | = | — | = | — | ≈ | — | — | = |
| ReqIF 1.2 | ext | ≈ | — | — | — | ⊂ | — | — | — | — | — |
| SysML v2.0 | = | = | — | — | — | ≈ | — | — | — | ≈ | = |
| OMG SACM 2.3 | — | ⊃ | ≈ | — | — | ≈ | — | ≈ | — | ≈ | = |
| **Composition (security part)** | | | | | | | | | | | |
| SPDX 3.0.1 | — | ⊂ | = | ⊂ | = | = | ⊂ | = | — | ∅ | ∅ |
| CycloneDX 1.7 | = | = | = | ≈ | txt | ≈ | ⊂ | = | — | ∅ | ∅ |
| **formats with `=`** | **6** | **3** | **4** | **2** | **3** | **6** | **0** | **5** | **2** | **1** | **3** |

- **Assertion is common.** Five formats carry multi-source, attributed statements exactly (CVE's CNA and ADP containers, OpenVEX statements, STIX objects with `created_by_ref`, SPDX 3 assessment relationships, CycloneDX citations), and eight more come close. This is evidence for the Assertion-plus-Review pattern in the unaccepted LinkML draft.
- **Data flow and Requirement/Control are well represented** where they belong: data flow in all four threat-model formats, SysML v2 and CycloneDX; requirement or control in OSCAL, SysML v2 and CycloneDX.
- **Applicability with a reason** is exact in the VEX-carrying formats (OpenVEX, CSAF, SPDX 3, CycloneDX); their justification codes do not fully agree (CycloneDX has 9, the others 5).
- **DamageScenario has no exact match**; this matters for ISO/SAE 21434 (RPT-0007).

### Identity sub-row: how formats name a Product or Component

Per the sponsor's answer, identifier schemes are a property of Product and Component, not a format column.

| Format | Identifier schemes it uses for the affected or described thing |
|---|---|
| CVE 5.2.0 | CPE (`cpes`); purl (`packageURL`, which must not include a version) |
| NVD API 2.0 | CPE 2.3 (`criteria`), with version-range bounds |
| OSV 1.9.1 | purl (`package.purl`); ecosystem + package name |
| OpenVEX 0.2.0 | purl, CPE 2.2 and 2.3 (`identifiers`); `hashes` |
| CSAF 2.0 / 2.1 | `product_identification_helper`: CPE, purl(s), hashes, SBOM URLs, serial, model and SKU numbers, generic URIs |
| STIX 2.1 | `software` object: CPE, SWID (no purl) |
| SPDX 3.0.1 | `packageUrl`; `externalIdentifier` of type cpe22, cpe23, swid, packageUrl, gitoid or swhid; `verifiedUsing` hashes |
| CycloneDX 1.7 | `purl`, `cpe`, `swid`, `omniborId`, `swhid`, `hashes` |
| D3FEND 1.6.0 | `PackageURL` only as an artifact class |
| OSCAL 1.2.3 | component `props` (no dedicated field) |
| threagile, pytm | technology classes or OS strings, not product identifiers |
| all others | none |

purl and CPE are the only schemes shared across vulnerability data, VEX and composition formats. CVE stores purl without a version; the version lives in the version ranges. A tmodel import that keeps both CPE and purl when present, and versions the purl only for an instance, loses nothing (fanout-vuln-data.md, Table 6).

## Table 3: ARCH-0001's typed edges

| Format | exploits | mitigated_by | part_of | step_of | instance_of | reviewed_by | applies_to_product | supersedes |
|---|---|---|---|---|---|---|---|---|
| **Weakness and vulnerability** | | | | | | | | |
| CWE 4.20 | — | ≈ | ≈ | ≈ | ≈ | — | — | txt |
| CVE 5.2.0 | — | txt | — | — | ≈ | — | = | = |
| NVD API 2.0 | — | — | — | — | ≈ | — | = | — |
| OSV 1.9.1 | — | ≈ | — | — | ext | — | = | ≈ |
| **Scores and signals** | | | | | | | | |
| CVSS 3.1 / 4.0 | — | — | — | — | — | — | — | — |
| EPSS | — | — | — | — | — | — | — | — |
| SSVC (scope open) | — | — | — | — | — | — | — | — |
| **Applicability and advisories** | | | | | | | | |
| OpenVEX 0.2.0 | — | txt | = | — | — | — | = | ≈ |
| CSAF 2.0 / 2.1 | — | ≈ | = | — | ≈ | — | = | ≈ |
| **Threat and attack knowledge** | | | | | | | | |
| ATT&CK 19.2 | — | ≈ | — | — | = | — | ⊃ | = |
| CAPEC 3.9 | ≈ | txt | ≈ | = | txt | — | — | txt |
| D3FEND 1.6.0 | — | ≈ | = | — | — | — | — | ≈ |
| STIX 2.1 | ⊂ | = | ≈ | — | ≈ | ≈ | ≈ | ⊂ |
| TAXII 2.1 | — | — | — | — | — | — | — | — |
| **Threat-model formats** | | | | | | | | |
| OTM 0.2.0 | — | = | = | — | = | — | — | — |
| threagile (master) | ≈ | txt | ≈ | — | = | ≈ | — | — |
| pytm 1.4.0 | txt | ≈ | = | — | = | ⊂ | — | txt |
| Threat Dragon 2.6.2 | — | txt | — | — | — | ⊃ | — | — |
| **Requirements and assurance** | | | | | | | | |
| OSCAL 1.2.3 | ≈ | = | ≈ | — | = | ≈ | ≈ | = |
| ReqIF 1.2 | ext | ext | ≈ | — | ⊃ | ext | — | — |
| SysML v2.0 | ext | ≈ | = | ext | = | ≈ | ≈ | — |
| OMG SACM 2.3 | — | ≈ | ≈ | — | ≈ | — | ≈ | — |
| **Composition (security part)** | | | | | | | | |
| SPDX 3.0.1 | — | ⊂ | = | — | — | ≈ | = | ≈ |
| CycloneDX 1.7 | — | ⊂ | = | — | ⊂ | ≈ | = | ≈ |
| **formats with `=`** | **0** | **3** | **8** | **1** | **6** | **0** | **7** | **3** |

- **`reviewed_by` and `exploits` have no exact match** anywhere, mirroring the Review and attack-side gaps above.
- **`step_of` has one** (CAPEC's execution-flow steps); 21 formats lack it.
- **`applies_to_product` is the best-covered edge** (7 exact), always with qualifiers ARCH-0001's single edge cannot hold: version ranges, AND/OR platform logic (NVD), status and justification (VEX).
- **`supersedes` is exact in three formats** (CVE `replacedBy`, ATT&CK `revoked-by`, OSCAL withdrawn-control links) and prose-only in three (CWE, CAPEC and pytm's `DEPRECATED` marker), where an importer must parse text.

### Edges the formats have and ARCH-0001 lacks

Grouped from the four sources. Each group is a gap-analysis input.

| Group | Examples (format: element) | Nearest ARCH-0001 edge |
|---|---|---|
| Specialization ("is a kind of") | CWE and CAPEC `ChildOf`; ATT&CK `subtechnique-of` | none; not `part_of` |
| Order and causality | CWE and CAPEC `CanPrecede`/`CanFollow`; CWE chains | `step_of` only partly |
| Adversary and target | ATT&CK and STIX `uses`, `attributed-to`, `targets` | none (`targets` is implicit in Threat) |
| Detection and sightings | ATT&CK `detects`; STIX `indicates`, `based-on`, `sighting` | none |
| Same thing across sources | OSV `aliases`, `upstream`, `related`; VEX and CSAF aliases; STIX `duplicate-of`, `derived-from` | none |
| Applicability with status and reason | VEX `not_affected` + justification in four encodings; SPDX `affects`, `doesNotAffect`, `fixedIn` | `applies_to_product`, without status |
| Attribution | VEX `author`/`publisher`/`suppliedBy`; OSV `severity[].source`; SPDX `foundBy`, `reportedBy`; CycloneDX `citations.attributedTo` | none |
| Graded mapping between catalogs | CWE and CAPEC `Taxonomy_Mapping` with fit; D3FEND graded control links; OSCAL `mapping-collection`; CVE `taxonomyMappings` | none |
| Requirement trace | `satisfies`, `verifies`, `derives`, `refines`, `requires` (OSCAL, ReqIF, SysML v2, SACM); SACM counter-evidence and defeat | none |
| Scoping out | threagile `out_of_scope`, pytm `Assumption.exclude`, Threat Dragon `outOfScope` (each with a reason); OSCAL `not-applicable` | none |
| Decision tracking | threagile `risk_tracking`; pytm overrides; OSCAL `risk-log` | `reviewed_by`, partly |
| Data flow | OTM, threagile, pytm, Threat Dragon, CycloneDX `source`/`destination`; SysML v2 flow connections | none |
| Defence-to-artifact | D3FEND `analyzes`, `hardens`, … (its defence-offence pairs are derived from these) | `mitigated_by`, derived |
| AI supply chain | SPDX 3 `trainedOn`, `testedOn` | none |

**Edge qualifiers recur in every family:** scope (CWE `View_ID`), order (chain ordinal, step position), fit grade (CWE `Mapping_Fit`, D3FEND graded links), boolean logic (NVD `operator`, `negate`), status and justification (VEX), catalog version pins (ATT&CK collection version), negation (SysML v2 `isNegated`) and counter-evidence (SACM `isCounter`). An edge type alone loses all of these.

## Dimension 8, question by question

### 1. Which identifiers can serve as stable keys across formats?

| Key | Stability, from the sources | Use as a cross-format key |
|---|---|---|
| CVE id | unique, never reassigned; a rejected id names its replacement in `replacedBy` | yes |
| CWE id, CAPEC id | integers never reused; deprecated entries kept, successor named only in prose | yes, with successor parsing |
| ATT&CK id (`T1059.001`, `TA0005`, `M1031`) | never reused, but revoked objects point on with `revoked-by` and at least one id has changed meaning (`TA0005`) | yes, if every use pins the ATT&CK collection version |
| STIX id (`type--UUID`) | globally unique; a version is the id plus `modified` | yes within STIX exchange |
| D3FEND IRI and `d3fend-id` | IRIs renamed between releases without tombstones; 27 `D3A-` ids collide | key by IRI plus version; `d3fend-id` as an alias only |
| OSV id | database-prefixed (`GHSA-`, `PYSEC-`, …) with `aliases` to CVE | yes, through `aliases` |
| purl, CPE | product and package identity, shared across vulnerability, VEX and composition formats | yes, for Product and Component |
| OSCAL UUIDs and control ids (`ac-2`) | UUIDs kept across revisions; control ids stable within a catalog version | yes, for controls |
| SPDX `spdxId`, CycloneDX `serialNumber` + BOM-Link | IRIs and UUIDs; CycloneDX `bom-ref` is document-local | across documents only through these |
| threat-model ids (OTM, threagile, pytm, Threat Dragon) | file-local strings or UUIDs, no namespace | no |

The catalogs' ids and purl/CPE can join formats; threat-model and SBOM-internal ids cannot. Every catalog key needs its catalog version beside it.

### 2. Where is the same concept named differently, and where does one name mean different things?

- **One concept, many shapes: Mitigation.** CWE `Potential_Mitigations` is generic advice; ATT&CK `course-of-action` (M-ids) and D3FEND `DefensiveTechnique` are catalog entries; OTM `mitigations[]` and OSCAL implemented requirements carry per-instance state; pytm expresses mitigation only as control flags read by threat conditions. Only OTM and OSCAL record whether a mitigation is in place for one element.
- **One concept, two levels: Threat.** OTM separates a library `threat` from its per-component instance; pytm separates `Threat` (rule) from `Finding` (instance); threagile separates risk category from risk. tmodel's generic-to-product mapping (DEC-009) needs both levels, and formats that keep only one lose the other on import.
- **One concept, four shapes: TrustBoundary.** A zone (OTM with a trust rating, pytm with nesting), an explicit typed boundary with listed members (threagile), a drawn curve or box whose membership is geometric (Threat Dragon), or a `trustZone` property of a service (CycloneDX). CVSS `scope: CHANGED` looks like a boundary crossing but is a property of a vulnerability (fanout-vuln-data.md, Table 6).
- **One word, different meanings: "status".** In CWE and CAPEC it is editorial maturity (Draft, Stable); in VEX it is applicability (`not_affected`, …); in OTM it is the state of a threat instance (`exposed`, `mitigated`); in NVD it is NIST's workflow (`Analyzed`, `Deferred`); in OSCAL findings it is satisfied or not. An importer that maps every `status` field to one tmodel field would mix all five.

### 3. What is lost when importing each format into ARCH-0001's types?

The loss profile columns of Table 2 part 1 give the count per format. Across all formats, three losses recur:

1. **Review state is lost or flattened** in every format, because none carries ARCH-0001's Review exactly.
2. **Edge qualifiers are lost** whenever an edge with scope, order, fit, logic or justification is imported as a bare typed edge.
3. **Successor links become prose** for CWE, CAPEC and pytm, so `supersedes` must be parsed from text and flagged as such.

Per-format losses are listed in each source file's "Findings that bear on tmodel". These counts are the input to #16's round-trip test.

### 4. Where must tmodel extend a format locally, and through which mechanism?

Table 6, consolidated from the four sources. Each row is evidence for the decision it routes to, not a proposal.

| Need | Formats affected | Mechanism the sources found | Routes to |
|---|---|---|---|
| Review on any element (verdict, impact, rationale, reviewer, date) | OTM, threagile, pytm, Threat Dragon, STIX, SPDX 3, CycloneDX, SACM, VEX statements | OTM `attributes`; STIX `opinion` extension; SPDX `Annotation` + extension; CycloneDX properties; SACM `Activity` + `Participant`; for threagile, keep Review outside the YAML, keyed by `synthetic_id` | ARCH-0001 §7, R-018, #16, #17 |
| Ordered attack steps and paths | ATT&CK, STIX, OTM and the other threat-model formats | none fits; keep tmodel-native, export to CycloneDX 2.0 when it is released | DEC-001, #17 |
| Fit-graded, version-pinned mappings between catalogs | CAPEC → ATT&CK (pinned to ATT&CK 12.0); ATT&CK → CAPEC and CWE (dropped in ATT&CK 13); D3FEND inferred pairs; CWE references in threat-model formats | a mapping edge carrying fit grade (CWE `Mapping_Fit` as model), both catalog versions, and provenance "derived" where inferred | #16, #17, DEC-001, DEC-008, DEC-009 |
| Local entries a closed catalog lacks | CWE (closed XSD), ATT&CK, CAPEC | a separate local namespace linked to the nearest catalog entry by a fit-graded edge; SARIF custom taxonomies and ATT&CK Workbench namespaces are the nearest practice found | DEC-001, DEC-002, DEC-008 |
| Machine-readable supersession | CWE, CAPEC (prose), OpenVEX (time order), CSAF 2.0 (revisions) | a `supersedes` edge filled at import, flagged when text-derived | ARCH-0001 §3, #16 |
| Statement identity and provenance | OpenVEX (`@id` optional), CycloneDX VEX (no statement id or author) | mint statement ids; require a citation (`attributedTo`, `timestamp`); one Assertion kind (source, signal, value, date) for exploitation evidence such as EPSS, KEV and SSVC | #16, DEC-001 |
| Applicability with a justification, per instance | OSV (no not-affected), CVE `affected[]`, VEX justification codes (9 in CycloneDX vs 5 elsewhere) | a VEX-style status + justification beside each range; a many-to-one justification map with a lossy flag | #17, DEC-002, DEC-009 |
| Trust boundary and system model | CycloneDX (boundary on a service, not a flow), OSCAL (no boundary or data flow) | keep tmodel-native; derive from differing `trustZone` at a flow's ends; link by component UUID | DEC-001 |
| Security vocabulary in general-purpose models | ReqIF, SysML v2, OSCAL | a published tmodel ReqIF profile; a small SysML v2 library (Threat, Mitigation, Review); a tmodel namespace for OSCAL `props` | DEC-002, MAP-0001 |
| Valid CWE references | threagile (15 of 42 category links use Prohibited CWE ids), pytm | validate against CWE `Usage`; keep the original beside a corrected, fit-graded mapping | DEC-008, #17 |

## Inputs to the gap analysis (Phase 5)

Evidence only; each item routes to an open decision.

1. **Review is tmodel's most distinctive element.** No surveyed format encodes it exactly, so every import and export loses it unless carried by extension (ARCH-0001 §7, R-018, #17).
2. **Attack paths are tmodel-native for now.** No released format has an ordered attacker path; CycloneDX 2.0 is the only candidate and is unreleased (DEC-001, DEC-002).
3. **The Assertion pattern is established practice.** Five formats carry attributed multi-source statements exactly (DEC-001, #16).
4. **ARCH-0001 has no specialization edge.** CWE, CAPEC and ATT&CK all use one, and mapping it to `part_of` would be wrong (DEC-001).
5. **Edges need qualifiers.** Every family uses at least one (ADR-0004's edge façade, #16).
6. **Candidate concepts confirmed by the survey:** Requirement/Control, DataFlow, Applicability statement, Exploitation evidence, Party, Assertion; and proposed by it: Assumption, Verification/Evidence (DEC-001, #17).

## Limits

- Marks are extracted by script from the source files and were not re-judged here. The Phase 4 adversarial review spot-checks a sample of cells against the specifications (dimension 10, question 4).
- `∅` cells were not assessed: the pilot did not assess Advisory/Remediation or DamageScenario, and only the requirements survey assessed Assumption and Verification/Evidence.
- Table 4 (adoption) and Table 5 (ratings) stay in the source files until the report is synthesized.

**Identity.** CPE and purl are the only identifier schemes shared across vulnerability data, VEX and composition formats. Keeping both when present, and versioning the purl only for an instance, loses nothing (crosswalk.md, identity sub-row).

**Stable keys.** CVE, CWE and CAPEC ids, ATT&CK ids pinned to a collection version, OSV ids through `aliases`, purl, CPE and OSCAL UUIDs can join formats. Threat-model and SBOM-internal ids cannot.

**Local extension** is needed in ten places, consolidated in crosswalk.md (dimension 8, question 4). The recurring ones are: Review on any element; ordered attack paths; fit-graded, version-pinned mappings between catalogs; a local namespace for entries a closed catalog lacks; and machine-readable supersession.

## 10. Adoption

Who produces and consumes each format, with evidence. Vendor marketing alone was not accepted as evidence.

| Format | Produced by | Consumed by | Kind | Evidence | As of |
|---|---|---|---|---|---|
| CWE 4.20 | MITRE (catalog; CISA-sponsored). CNAs and ADPs write CWE ids into CVE records; NVD assigns its own; GitHub Advisory DB writes `cwe_ids`; CSAF publishers (Red Hat: `cwe` CWE-20) | CVE record format (`problemTypes.cweId`), NVD `weaknesses`, CISA KEV `cwes[]` (1,559 of 1,734 entries have one), CSAF `cwe`/`cwes`, CycloneDX `cwes`, CodeQL query tags, SARIF taxonomies | open (MITRE, free with attribution) / government-sponsored | KEV feed and schema; CVE schema 5.2.0; CSAF 2.0 and 2.1 schemas; CycloneDX 1.7.2 schema; CodeQL style guide https://github.com/github/codeql/blob/main/docs/query-metadata-style-guide.md; GHSA OSV record (`database_specific.cwe_ids`); CWE FAQ https://cwe.mitre.org/about/faq.html | 2026-10-06 |
| CVE Record Format 5.2.0 / CVE List | 555 CNA entries in the CVE website's `CNAsList.json` (dev branch); CISA-ADP and CVE-ADP containers; `cvelistV5` repo updated hourly (release `cve_2026-10-06_1900Z`) | NVD (every CVE), CISA KEV (keyed on CVE id), OSV (`aliases`, `CVE-` prefix), GitHub advisories, EPSS (CVE-keyed), CSAF (`cve`), Dependency-Track NVD data source, Grype NVD provider | open; government-sponsored | https://github.com/CVEProject/cve-website/blob/dev/src/assets/data/CNAsList.json (555 entries); https://github.com/CVEProject/cvelistV5; Dependency-Track tree `vuln-data-source/nvd`, Grype tree `grype/db/internal/provider/unmarshal/nvd` (links below) | 2026-10-06 |
| NVD CVE API 2.0 (schema 2.2.4) | NIST NVD. Live: 401,518 CVEs; 1,851,652 CPE names (API `totalResults`). Enrichment is now selective (pilot) | Dependency-Track (`vuln-data-source/nvd`), Grype (`unmarshal/nvd`), GitHub advisories (`database_specific.nvd_published_at`), OSV (`severity[].source: NVD`) | government (public domain) | https://github.com/DependencyTrack/dependency-track/tree/main/vuln-data-source ; https://github.com/anchore/grype/tree/main/grype/db/internal/provider/unmarshal ; NVD terms and rate limits in section 1.0 | 2026-10-06 |
| OSV schema 1.9.1 | OSV.dev aggregator (`google/osv.dev`) and the databases on its data page (GitHub Advisory DB, PyPA, Go, RustSec, Drupal, GSD, OSS-Fuzz, Rocky, AlmaLinux, Haskell, R Consortium, malicious-packages, Ubuntu, others) | osv.dev API and bucket; Third-party tools named on the OSV site: Cortex XSOAR, dep-scan, Dependency-Track, GUAC, OSS Review Toolkit, pip-audit, Renovate, Trivy; Bomber (default provider); VulnerableCode (importers `osv.py`, `github_osv.py`) | open source (Apache-2.0 schema; data licences vary) | https://raw.githubusercontent.com/google/osv.dev/master/docs/data.md ; https://raw.githubusercontent.com/google/osv.dev/master/docs/third-party.md (maintainers note the tools are "community built ... not supported or endorsed"); https://raw.githubusercontent.com/devops-kung-fu/bomber/main/README.md ; https://github.com/DependencyTrack/dependency-track/tree/main/vuln-data-source (has `osv`) | 2026-10-06 |
| CVSS v3.1 / v4.0 | CNAs and ADPs (CVE `metrics`), NVD (`cvssMetricV31`, `cvssMetricV40`), vendors in CSAF (`scores`/`metrics`), GitHub (`severity[]` vectors in OSV) | CVE, NVD, CSAF 2.0/2.1, CycloneDX `ratings`, SPDX 3.0.1 Cvss relationships, OSV `severity`, EPSS (uses CVSS metrics as features), Grype | open (FIRST, free with attribution) | CVE record CVE-2021-44228 (CISA-ADP container); Red Hat and Siemens CSAF files; schemas of all five formats; EPSS "How EPSS works" | 2026-10-06 |
| EPSS | FIRST EPSS SIG, data by Empirical Security; daily file 2026-10-05 (382,795 CVEs) | Self-reported list at https://www.first.org/epss/who_is_using (vendors: AWS Inspector, Snyk, Tenable, Qualys, Microsoft Defender, Cisco, GitHub Dependabot and Advisory Database, Dependency-Track, VulnerableCode, Bomber, ...). Verified in source: Grype (`grype/db/processors/epss_processor.go`; README "Threat & risk prioritization with EPSS, KEV"), Dependency-Track (`apiserver/.../epss/Epss.java`), VulnerableCode (`importers/epss.py`). Formats: CSAF 2.1 `metrics.epss`; SPDX 3.0.1 `EpssVulnAssessmentRelationship` | open data (free, attribution requested) | https://www.first.org/epss/who_is_using (self-reported, vendor-supplied links: not counted as evidence on its own) ; https://github.com/anchore/grype/tree/main/grype/db/processors ; https://github.com/DependencyTrack/dependency-track/tree/main/apiserver/src/main/java/org/dependencytrack/epss ; https://github.com/aboutcode-org/vulnerablecode/blob/main/vulnerabilities/importers/epss.py | 2026-10-06 |
| SSVC | CISA-ADP (Vulnrichment) writes SSVC decisions into CVE records; CISA | NVD `ssvcV203`; CSAF 2.1 `ssvc_v2`; CycloneDX `ratings.method: SSVC`; SPDX `SsvcVulnAssessmentRelationship`; BOD 26-04 Appendix A | open (CERT/CC); government use | CVE-2021-44228 record; BOD 26-04 https://www.cisa.gov/news-events/directives/bod-26-04-prioritizing-security-updates-based-risk ; https://github.com/cisagov/vulnrichment (CC0-1.0, active 2026-10-06) | 2026-10-06 |
| OpenVEX 0.2.0 | Trivy (its own repo VEX, `aquasecurity/trivy:613fd5…`, 21 statements, author "Aqua Security", tooling `magefiles/vex.go`); Deckhouse (`vex-virtualization-virt-handler-runc-cve-2026-41579`); Checkmarx KICS (`trivy.vex`, author "Fernando Nogueira", one not_affected statement with `vulnerable_code_not_in_execute_path`); the go-vex library (header "Copyright 2023 The OpenVEX Authors") | Trivy (`pkg/vex/openvex.go`; docs "Trivy supports ... CycloneDX, OpenVEX, CSAF"), Grype (README "OpenVEX support for filtering and augmenting scan results"; db processors `openvex`, `annotated_openvex`) | open source | https://github.com/aquasecurity/trivy/tree/main/pkg/vex ; https://raw.githubusercontent.com/anchore/grype/main/README.md ; real documents: https://raw.githubusercontent.com/aquasecurity/trivy/main/.vex/trivy.openvex.json ; https://raw.githubusercontent.com/deckhouse/virtualization/main/images/virt-handler/known_vulnerabilities.vex ; https://raw.githubusercontent.com/Checkmarx/kics/master/trivy.vex | 2026-10-06 |
| CSAF 2.0 (errata 01) | Red Hat Product Security (VEX per CVE), Siemens ProductCERT (advisories, signed `.asc`). BSI's aggregator lists 14 providers and 1 publisher: KUNBUS, IDS Innomic, Open-Xchange, Stackable, **CISA**, Schneider Electric CPCERT, BSI, Huawei PSIRT, Red Hat, Intevation, Nozomi Networks, SICK, ABB, Siemens (+ Hitachi Energy as publisher) | Trivy (`pkg/vex/csaf.go`: uses `known_not_affected` and `fixed` matched on purl), Grype (db processor `csaf_vex_processor.go`) | open standard; mixed vendors | https://wid.cert-bund.de/.well-known/csaf-aggregator/aggregator.json (14 + 1; `last_updated` 2026-10-06T19:00:27Z); https://security.access.redhat.com/data/csaf/v2/vex/2021/cve-2021-44228.json ; https://cert-portal.siemens.com/productcert/csaf/ssa-661247.json ; https://github.com/aquasecurity/trivy/tree/main/pkg/vex. The aggregator lists only the providers registered with that one lister, so the figure is a lower bound for the ecosystem | 2026-10-06 |
| CSAF 2.1 (CSD03) | none found in production: it is a draft (public review closed 2026-09-29) | none found | open standard (draft) | CSAF 2.1 CSD03 and its public-review metadata | 2026-10-06 |
| CAPEC | MITRE: XML; STIX 2.1 copy in `mitre/cti` | CWE (mirrors all 1,212 CAPEC–CWE pairs); OpenCTI `mitre` connector (`MITRE_CAPEC_FILE_URL` → `stix-capec.json`); OWASP pytm threat library (98 of 114 threats cite `capec.mitre.org` in `references`) | open source / government-funded | <https://capec.mitre.org/data/xml/capec_latest.xml>; <https://github.com/mitre/cti/tree/master/capec/2.1>; <https://github.com/OWASP/pytm/blob/master/pytm/threatlib/threats.json>; OpenCTI as above | 2026-10-05 |
| D3FEND | MITRE NSEC (ontology, inferred-mapping CSV, D3FEND CAD tool) | MISP galaxy `mitre-d3fend.json` (generated by `tools/gen_mitre_d3fend.py`); D3FEND CAD threat-modeling method (MITRE) | open source / government-funded | <https://d3fend.mitre.org/resources/ontology/>; <https://github.com/MISP/misp-galaxy/blob/main/galaxies/mitre-d3fend.json>; <https://d3fend.mitre.org/blog/threat-modeling-with-d3fend-ontology-and-cad/> | 2026-10-05 |
| ATT&CK (STIX 2.1) | MITRE: `attack-stix-data` bundles; ATT&CK TAXII 2.1 server (45 API roots, one per release) | OpenCTI `mitre` connector (downloads `enterprise-attack.json`); ATT&CK Navigator; D3FEND (imports ATT&CK v19.0); Sigma rules (tag namespace `attack.t1234`); CAPEC (maps to ATT&CK 12.0) | open source / government-funded (FFRDC) | <https://github.com/mitre-attack/attack-stix-data/releases/tag/v19.2>; <https://attack-taxii.mitre.org/taxii2/>; <https://github.com/OpenCTI-Platform/connectors/blob/master/external-import/mitre/src/models/configs/mitre_configs.py>; <https://github.com/mitre-attack/attack-navigator> (README references `enterprise-attack.json`); <https://github.com/d3fend/d3fend-ontology/blob/1.6.0/CHANGELOG.md>; <https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-rules-specification.md> | 2026-10-05 |
| STIX 2.1 | MITRE (ATT&CK, CAPEC bundles); MISP via `misp-stix` (MISP ↔ STIX 1.x/2.0/2.1, release 2026.9.8); OpenCTI (exports STIX2 bundles) | OpenCTI (knowledge schema "based on the STIX2 standards"); MISP; Microsoft Sentinel (imports via TAXII); CISA AIS participants | open source, commercial, government | <https://github.com/MISP/misp-stix>; <https://github.com/OpenCTI-Platform/opencti>; <https://learn.microsoft.com/en-us/azure/sentinel/connect-threat-intelligence-taxii> (ms.date 2026-07-01); <https://www.cisa.gov/topics/cyber-threats-and-advisories/information-sharing/automated-indicator-sharing-ais> | 2026-10-05 |
| TAXII 2.1 | Servers: MITRE ATT&CK TAXII; ATT&CK Workbench TAXII server; CISA AIS ("bidirectional AIS TAXII connection"); OASIS `medallion` reference server (last push 2024-04-15) | Clients: Microsoft Sentinel "Threat Intelligence – TAXII" (import from TAXII 2.0/2.1, export to 2.1); `taxii2-client` (ATT&CK USAGE.md); AIS participants ("use an open source TAXII 2.1 client") | open source, commercial, government | <https://attack-taxii.mitre.org/taxii2/>; <https://github.com/mitre-attack/attack-workbench-taxii-server>; CISA AIS and Microsoft Learn as above; <https://github.com/oasis-open/cti-taxii-server> | 2026-10-05 |
| OTM 0.2.0 | IriusRisk | IriusRisk | commercial | RPT-0003 (`iriusrisk-otm`, `iriusrisk-cli`); `iriusrisk/iriusrisk-cli` README @`a7d5aafc`: "Import/Export Threat Models: Use OTM (Open Threat Model) format …" | 2026-10-05 |
| OTM 0.2.0 | StartLeft (from CloudFormation, Terraform, Terraform plan, Visio, draw.io, Microsoft TMT, Abacus: `slp_*` processors) | — | open source (Apache-2.0, vendor) | `iriusrisk/startleft` @`e1bd3364`, repo contents; release 1.38.0 (2025-11-13) | 2026-10-05 |
| OTM 0.2.0 | threatcl (`threatcl export -format=otm`, emits `otmVersion: "0.2.0"`) | — | open source (MIT) | `threatcl/threatcl` README @`03b7f5e2`, lines 261–265 | 2026-10-05 |
| OTM 0.2.0 | Devici | SD Elements | commercial | RPT-0003 (`devici-sdelements`); not re-researched | 2026-10-04 (RPT-0003) |
| OTM 0.2.0 | tmac (export) | tmac (import) | open source (Apache-2.0), personal project created 2026-09-06 | `sheltowt/threat_model` @`a92a35f9`, `packages/importers/src/export-otm.ts`, `otm.ts` | 2026-10-05 |
| OTM 0.2.0 | — | OWASP Threat Dragon `main` only (import; unreleased); v2.6.2 refuses OTM | open source | `td.vue/src/views/ImportModel.vue` at v2.6.2 (`otmUnsupported`) and at `main` (`importOtm`) | 2026-10-05 |
| threagile YAML | Threagile | Threagile; tmac (import, incl. `risk_tracking`) | open source | Threagile repo @`74e323ed`; tmac `threagile.ts` | 2026-10-05 |
| pytm JSON | pytm (`--json`) | pytm (`pytm.json.load`); tmac (import) | open source | pytm v1.4.0 `pytm/json.py`, `tm.py`; tmac `pytm.ts` | 2026-10-05 |
| Threat Dragon v2 JSON | OWASP Threat Dragon | Threat Dragon; tmac (import) | open source | TD v2.6.2 source; tmac `threat-dragon.ts` | 2026-10-05 |
| OSCAL | NIST (SP 800-53 Rev 5.2.0 catalog and baselines in OSCAL) | — | government | `usnistgov/oscal-content` @`78650f02`, `nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json` | 2026-10-05 |
| OSCAL | compliance-trestle | compliance-trestle | open source (Apache-2.0; `oscal-compass` org) | `oscal-compass/compliance-trestle` README @`ecccc7cc`: "leverages NIST's OSCAL as a standard data format for interchange" | 2026-10-05 |
| OSCAL | — | GSA oscal-ssp-to-word (SSP → Word) | government, open source; last push 2021-10-19 | `GSA/oscal-ssp-to-word` repo metadata; RPT-0013 lane 5 | 2026-10-05 |
| ReqIF 1.2 | StrictDoc | StrictDoc | open source | `strictdoc-project/strictdoc` @`abf7be7d`: `strictdoc/backend/reqif/p01_sdoc/sdoc_to_reqif_converter.py`, `reqif_to_sdoc_converter.py` | 2026-10-05 |
| ReqIF 1.2 | Eclipse RMF | Eclipse RMF | open source; repo last pushed 2023-05-17 | `eclipse-rmf/org.eclipse.rmf` repo metadata (activity status ?) | 2026-10-05 |
| Commercial ReqIF, SysML v2 and SACM tools | ? | ? | commercial | not verified (open item) | — |
| SysML v2 | SysML v2 Pilot Implementation | Pilot Implementation; SysML v2 API Services | open source (EPL-2.0), OMG submission team | `Systems-Modeling/SysML-v2-Pilot-Implementation` (pushed 2026-10-03), `SysML-v2-API-Services` (pushed 2026-05-14) | 2026-10-05 |
| SysML v2 | Eclipse SysON (editors) | Eclipse SysON | open source (EPL-2.0) | `eclipse-syson/syson` README @`b380dada`: edits SysML v2 models; textual exchange "will support" (future) | 2026-10-05 |
| OMG SACM 2.3 | SACM EMF implementation and UML profile (RTF) | same | open source research; last push 2023-05-19 | `SystemsAssuranceGroup/SACM` README @`eb936422` | 2026-10-05 |
| OMG SACM | `wrwei/SACM` (EMF implementation) | same | open source (Apache-2.0), research; last push 2024-12-05 | repo metadata | 2026-10-05 |
| SPDX 3.0.1 Security VEX | OpenEmbedded-Core (`sbom30.py`, `spdx30_tasks.py`; `SPDX_INCLUDE_VEX` none/current/all; justification validated against the SPDX enum) | none found (no scanner source tree checked reads SPDX 3 VEX) | open source | https://github.com/openembedded/openembedded-core/blob/master/meta/lib/oe/spdx30_tasks.py (hash in section 10) | 2026-10-06 |
| SPDX 3.0.1 Security profile | OpenEmbedded-Core / Yocto (`meta/lib/oe/sbom30.py`: VexFixed, VexAffected, VexNotAffected relationships); `spdx/tools-python` 0.8.5 (writes SPDX 3, does not read it); `Spdx-Java-Library` 2.0.5 (SPDX 3 model) | none found: Trivy VEX input is CycloneDX, OpenVEX, CSAF; Dependency-Track and GUAC cannot read SPDX 3 (RPT-0004) | open source | <https://github.com/openembedded/openembedded-core/blob/master/meta/lib/oe/sbom30.py>; <https://github.com/spdx/tools-python>; <https://github.com/spdx/Spdx-Java-Library>; Trivy doc below | 2026-10-05 |
| CycloneDX VEX (1.7 `vulnerabilities`) | Dependency-Track exports a project's VEX in CycloneDX (`VexResource`, `/cyclonedx/project/{uuid}`, `Variant.VEX`); CycloneDX example repository (CISA use cases, 8 of 9 "Supported") | Trivy (`pkg/vex/cyclonedx.go`, via SBOM or file), Dependency-Track | open source | https://raw.githubusercontent.com/DependencyTrack/dependency-track/main/apiserver/src/main/java/org/dependencytrack/resources/v1/VexResource.java ; https://github.com/CycloneDX/bom-examples/tree/master/VEX/CISA-Use-Cases ; https://github.com/aquasecurity/trivy/tree/main/pkg/vex | 2026-10-06 |
| CycloneDX 1.7 vulnerabilities/VEX/services | Trivy (`--format cyclonedx`), Syft/Grype (RPT-0004 tool runs); cdxgen (services with `x-trust-boundary`); Dependency-Track (exports CycloneDX VEX) | Trivy (local CycloneDX VEX files, BOM-Link to SBOM); Dependency-Track (VEX upload `PUT`/`POST /v1/vex`) | open source | <https://github.com/aquasecurity/trivy/blob/main/docs/guide/supply-chain/vex/file.md>; <https://github.com/DependencyTrack/dependency-track/blob/master/apiserver/src/main/java/org/dependencytrack/resources/v1/VexResource.java>; <https://github.com/cdxgen/cdxgen/blob/master/lib/inventory/analyzer.js>; RPT-0004 §3 | 2026-10-05 |

## 11. Synthesis and gap analysis

The field is mature where tmodel needs to read: vulnerability records, scores, applicability statements and component identity are standardized, versioned and widely produced. It is immature where tmodel needs to write: no released format records a human's reviewed verdict on a threat, or an ordered attack path. tmodel's distinctive elements are therefore its own to model. Interchange is a matter of carrying them through other formats' extension points without loss.

What the field has or lacks, against tmodel, with the decision each finding is evidence for:

| # | Finding | Evidence | Routes to |
|---|---|---|---|
| G1 | No format encodes Review (verdict, assigned impact, rationale, reviewer, date) exactly. OSCAL and threagile come closest, and neither has assigned impact. | Table 5; crosswalk Review column (0 of 24 `=`) | ARCH-0001 §7, R-018, #17 |
| G2 | No released format has an ordered attack path. CAPEC's execution flow is the nearest; CycloneDX 2.0 TM-BOM is a draft candidate. | crosswalk AttackStep and AttackPath (0 of 24 `=`); §8 | DEC-001, DEC-002, #17 |
| G3 | Attributed, multi-source assertions are common practice (5 exact, 8 close). | crosswalk part 2; §2, §4, §8 | DEC-001, #16 (Assertion) |
| G4 | ARCH-0001 has no specialization edge, but CWE, CAPEC and ATT&CK all use one. Mapping it to `part_of` would be wrong. | crosswalk, edges ARCH-0001 lacks | DEC-001 |
| G5 | Edges carry qualifiers in every family: scope, order, fit, logic, justification, version pin. | crosswalk, edge qualifiers | ADR-0004 edge façade (#52, #65), #16 |
| G6 | Applicability with a reason, per product version, is standardized as VEX, but the four encodings' justification codes differ (9 versus 5). | §4 | #17 ("is CVE X applicable to product Y"), DEC-009 |
| G7 | NVD no longer enriches most CVEs; CNA and ADP data in the CVE record is the main source of CWE and applicability. | §2 | DEC-008 |
| G8 | Catalog references need a validity gate (CWE `Usage`) and a version pin (ATT&CK ids change meaning; CAPEC is frozen at ATT&CK 12.0). | §2, §5; threagile's 15 of 42 | DEC-008, #16 |
| G9 | Closed catalogs (CWE, CAPEC) cannot be extended in place; local entries need a separate namespace with a fit-graded link. | §2; crosswalk Table 6 | DEC-001, DEC-002, DEC-008 |
| G10 | Requirement/Control and Verification evidence are first-class in OSCAL and SysML v2 but absent from ARCH-0001 §3. | §7; crosswalk part 2 | DEC-001, #19 |
| G11 | CPE and purl are the shared identity for Product and Component. | §9 | DEC-002, DEC-009 |
| G12 | OTM is the only threat-model interchange used across vendors, but it is a vendor-controlled 0.x schema without review or attack data; TM-BOM may supersede it. | §6, §8 | DEC-002 (R-005 import target) |

## 12. Method, coverage and limits

**Method.** The #39 playbook, phases 0 to 1, with a cost cap of three parallel agents. Phase 0 fixed the questions and table columns ([dimensions.md](dimensions.md)). A pilot on CWE, CVE, NVD and OTM in the main session tested the tables and changed five things in them ([pilot.md](pilot.md)). Three research agents then covered the other formats. Facts were taken from the artifacts (schema files, real example documents, live APIs), each with its SHA-256, not from summaries. The main session re-derived ten of the agents' facts from the artifacts, and all matched. The crosswalk marks were assembled by script without re-judgment. Every query is in [searches.md](searches.md) and every source in [sources.md](sources.md). The design log, DL-0013, records each phase and what was rejected: 4 claims in the pilot, 36 in the fan-out and 3 in the crosswalk draft.

**Scope decisions.** OpenC2 is out of scope (a command language, not threat knowledge). CPE, purl and KEV are not formats. ATLAS is covered by RPT-0014. All three were decided by the sponsor. Still open: whether CycloneDX 2.0 TM-BOM gets full coverage as a pinned draft, and whether SSVC is a format.

**Not yet done.**
- **Phase 2:** library records. `cwe` is extracted (library#21); the others are summaries or queued and must reach FX-1 or an honest stub. Splitting records that overlap with RPT-0004 (CycloneDX, SPDX) and RPT-0003 (pytm, Threat Dragon) is being agreed.
- **Phase 4:** the adversarial review. It will test coverage against CACAO, OCSF, MAEC, SARIF, OVAL/SCAP, VERIS and SWID; spot-check crosswalk cells against the specifications; and count normative statements against the extractions.
- **Phase 6:** the clarity pass.

**Limits.** Ratings and marks are AI-produced and only spot-checked by a human. The student's review so far is for clarity, not technical correctness (DL-0013). Adoption evidence is a sample, dated per row.

**References** live in the library: the record ids above, and every source with its URL and digest in [sources.md](sources.md). The library commit is pinned when Phase 2 merges.
