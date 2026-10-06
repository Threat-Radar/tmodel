---
schema: "archdoc/v1"
id: RPT-0005-pilot
title: "RPT-0005 Phase 1 pilot: CWE, CVE, NVD and OTM"
type: research
status: draft
version: "0.1.1"
date: "2026-10-05"
updated: "2026-10-06"
record: RPT-0005
---

# RPT-0005: Phase 1 pilot

The pilot planned in [dimensions.md](dimensions.md): one catalog (CWE), one record format with its enrichment service (CVE and NVD), and one threat-model format (OTM), filled into the per-format record and the tables before the three-agent fan-out. It has two jobs: produce the first rows of the report, and test whether the columns and marks work. What it changed in `dimensions.md` is in the last section.

Every fact below was checked against the schema file or live data on 2026-10-05, not taken from a summary. Schema files were downloaded and their SHA-256 recorded so the reading can be repeated. Sources are in [sources.md](sources.md); queries in [searches.md](searches.md). These rows feed the report; they are not yet the report.

## Per-format records

### CWE 4.20 (schema 7.3)

| field | value |
|---|---|
| Version pinned | CWE List 4.20, catalog dated 2026-04-30; XML schema `cwe_schema_v7.3.xsd` (namespace `http://cwe.mitre.org/cwe-7`), SHA-256 `690dedee…e45f98` |
| Steward | MITRE, sponsored by CISA. Content changes come through a web submission form, reviewed by the CWE team; accepted work is tracked in the public CWE Content Development Repository on GitHub. A CWE Board sets program goals. |
| Core entities | `Weakness` (969 in 4.20), `Category` (422), `View` (59), `External_Reference`. A Weakness has an `Abstraction` (Pillar, Class, Base, Variant, Compound) and a `Structure` (Simple, Chain, Composite). |
| Identifier scheme | Integer `ID`, written `CWE-79`, shared across weaknesses, categories and views. The schema says it "is considered static for the lifetime of the entry. If this entry becomes deprecated, the identifier will not be reused." |
| Encoding | XML with XSD; CSV extracts per view; HTML. |
| Extension mechanism | None. The XSD is closed: its only `xs:any` slots admit XHTML inside structured text. Enumerations, including the list of external taxonomies a weakness may map to (`TaxonomyNameEnumeration`), are fixed by MITRE. The only route to a new weakness is a submission to MITRE. |
| Licence | MITRE's CWE terms of use: free for research, development and commercial use if MITRE's copyright designation and the licence are reproduced. |
| Library record | `cwe`, `summarized`; must become FX-1 or `stub` (Phase 2). |

Findings that bear on tmodel:

- **Mapping rules are in the data.** Every entry has `Mapping_Notes/Usage`: Allowed (749 weaknesses), Allowed-with-Review (93), Discouraged (44) or Prohibited (83). MITRE's root-cause mapping guidance (v1.1, 2024-03-22) says Base and Variant "should be used whenever possible" and Class only when no Base or Variant fits. A tmodel Weakness node that cites a CWE can be validated against this: a Prohibited or Discouraged id is a finding, not a mapping.
- **Relations are view-scoped.** A `Related_Weakness` carries `Nature`, `CWE_ID` and a required `View_ID`; `ChildOf` in the Research view (CWE-1000) can differ from `ChildOf` in the Software Development view (CWE-699). Optional `Chain_ID` and `Ordinal` (Primary) qualify it further. An edge needs properties, not only a type.
- **`ChildOf` is specialization, not composition.** It means "is a kind of", so it is not ARCH-0001's `part_of`. Category and view membership (`Has_Member`/`Member_Of`) is closer to `part_of`.
- **Deprecation has no machine-readable successor.** A deprecated entry keeps its id with `Status="Deprecated"` and `Usage` Prohibited, and names its successor only in prose. Example: CWE-1187, "This entry has been deprecated because it was a duplicate of CWE-908." An importer must parse text to recover a `supersedes` edge.
- **Provenance is per entry, not per statement.** `Content_History` records the submitter, each modification and each contribution, with name, organization, date, release version and an importance flag (Critical marks a change of meaning). It does not say who asserted any single relation or mitigation.
- **Chains are ordered weakness sequences.** `Structure="Chain"` with `StartsWith` and `CanPrecede`/`CanFollow` is the nearest CWE thing to an AttackPath, but its steps are weaknesses, not attacker actions.
- **Extending CWE locally** (dimensions.md, dimension 1, question 5): the format gives no help, and the pilot found no documented convention. In practice a local weakness has to live in a separate namespace with its own ids, linked to the nearest CWE entry by a fit-graded mapping. CWE's own `Taxonomy_Mapping/Mapping_Fit` (Exact, CWE More Abstract, CWE More Specific, Imprecise, Perspective) is a ready model for the link. What tools do in practice is left to the fan-out (agent 1).

### CVE Record Format 5.2.0

| field | value |
|---|---|
| Version pinned | CVE Record Format 5.2.0 (released 2025-10-29), `CVE_Record_Format.json` (JSON Schema draft-07), SHA-256 `33f75174…3ddfde67`. Records in the wild carry `dataVersion` 5.0, 5.1 or 5.2. |
| Steward | The CVE Program: the CVE Board, with MITRE as secretariat and CISA as sponsor. The program's single federal sponsor drew concern in April 2025, when a CVE Foundation was announced as a possible alternative home. Program news (Board minutes, new members, new CNAs) continued through 2026; the latest item checked is dated 2026-09-24. |
| Core entities | One record per CVE id, with `cveMetadata` (state PUBLISHED or REJECTED, assigner, dates) and `containers`: exactly one `cna` container from the assigning CNA, and any number of `adp` containers from Authorized Data Publishers. Each container holds `affected[]` (products and versions), `problemTypes` (CWE), `metrics` (CVSS v2.0 to v4.0, or `other`), `references`, `solutions`, `workarounds`, `exploits`, `timeline`, `credits`, `taxonomyMappings`, `tags`. |
| Identifier scheme | `CVE-YYYY-NNNN…` (4 to 19 digits), unique and never reassigned; organizations by UUID (`orgId`). |
| Encoding | JSON; JSON Schema draft-07 with CVSS schemas imported. |
| Extension mechanism | Properties matching `^x_` on CNA and ADP containers (`x_generator` is common in real records), `x_` tags, and `metrics[].other` with a `format` name. 5.2.0 closed the product object (`additionalProperties: false`). `taxonomyMappings` is an open relation list to any named taxonomy (ATT&CK, D3FEND, CWE, …). |
| Licence | Schema: CC0-1.0. Record content: CVE terms of use (not checked in the pilot). |
| Distribution | `CVEProject/cvelistV5` on GitHub (bulk, updated continuously) and the CVE Services API. |
| Library record | `cve-json-5`, `summarized`. |

Findings that bear on tmodel:

- **Several parties assert facts about one vulnerability, side by side.** The CNA container and each ADP container carry `providerMetadata` (`orgId`, `shortName`, `dateUpdated`). In CVE-2021-44228, the Apache CNA asserts CWE-502, CWE-400 and CWE-20 and gives severity only as `other` ("critical"); the CISA-ADP container (`orgId 134c704f-…`) adds a CVSS 3.1 vector (base score 10.0) and an SSVC decision (`Exploitation: active`) carried in `metrics[].other`. This is the multi-source `Assertion` pattern that the unaccepted LinkML draft gestures at, already in production use.
- **Product applicability is version-range logic with status.** `affected[].versions[]` gives `version`, `lessThan`/`lessThanOrEqual`, `versionType`, `status` (affected, unaffected, unknown) and `changes[]`, with a normative algorithm in the schema text for deciding a version's status. `defaultStatus` covers versions not listed. 5.2.0 added `packageURL` (purl, without a version) beside `cpes`.
- **Weakness links are references only.** `problemTypes[].descriptions[].cweId` matches `^CWE-[1-9][0-9]*$`; there is no field for confidence, or for which mapping rule was applied.
- **Rejection has a machine-readable successor.** A rejected record has state REJECTED, `rejectedReasons` text and an optional `replacedBy` list of the CVE ids it "was rejected in favor of". Unlike CWE, a `supersedes` edge can be imported without parsing prose.
- **Disputes are tags.** `cnaTags` and `adpTags` take `disputed`; CNAs also have `unsupported-when-assigned` and `exclusively-hosted-service`.

### NVD CVE API 2.0

| field | value |
|---|---|
| Version pinned | NVD CVE API 2.0 (`format: NVD_CVE`, `version: 2.0`), observed live on 2026-10-05. |
| Steward | NIST. |
| Core entities | One `cve` object per CVE id: `vulnStatus`, `descriptions`, `affected` (the CNA's `affected[]`, passed through with its `source`), `metrics` (`cvssMetricV40`, `cvssMetricV31`, `cvssMetricV30`, `cvssMetricV2`, and `ssvcV203` from CISA-ADP), `weaknesses`, `configurations`, `references`, and for KEV entries `cisaExploitAdd`, `cisaActionDue`, `cisaRequiredAction`, `cisaVulnerabilityName`. |
| Identifier scheme | The CVE id; CPE 2.3 names for products; a UUID `matchCriteriaId` per CPE match. |
| Encoding | JSON over a REST API; no schema file was checked in the pilot. |
| Extension mechanism | — (a read-only service). |
| Licence | US government work; terms not checked in the pilot. |
| Library record | none yet. |

Findings that bear on tmodel:

- **Each weakness and score has a source and a role.** Entries in `weaknesses[]` and in each `cvssMetric*` list carry `source` (an email or an orgId) and `type` (Primary or Secondary). For CVE-2021-44228, NVD's own CWE assignment (CWE-917, from `nvd@nist.gov`) differs from the CNA's (CWE-502, CWE-400, CWE-20). A tmodel import keeps both, attributed, and does not choose silently.
- **Applicability is boolean CPE logic.** `configurations[].nodes[]` combine `cpeMatch[]` entries with `operator` (AND/OR) and `negate`; each match has `vulnerable`, `criteria` (a CPE 2.3 string) and `versionStart/End` `Including/Excluding`. `vulnerable: false` marks the platform the vulnerable part must run on (in CVE-2021-44228, Siemens firmware AND its hardware). This is richer than ARCH-0001's single `applies_to_product` edge.
- **KEV status is carried inline.** The `cisaExploitAdd` and related fields give the date a CVE entered CISA's Known Exploited Vulnerabilities catalog, the due date and the required action.
- **NVD enrichment is now the exception (DEC-008).** On 2026-04-15 NIST announced that NVD will enrich only CVEs in CISA KEV, CVEs for software used in the federal government, and critical software under Executive Order 14028; it "will no longer routinely provide a separate severity score" for other CVEs, and backlogged CVEs published before 2026-03-01 move to "Not Scheduled". Live data agrees: of the 102 CVEs published on 2026-09-20, 96 are `Deferred`, 4 `Awaiting Analysis` and 2 `Analyzed`; 2 have NVD `configurations` and none has an NVD-sourced CWE, while all 102 have the CNA's `affected` and `weaknesses`. The API still says `Deferred`, not the announced "Not Scheduled". For tmodel, the CNA's `affected[]` (with purl since 5.2.0) and ADP data are now the main applicability and CWE source; NVD CPE configurations are a bonus for a minority of CVEs.

### OTM (Open Threat Model) 0.2.0

| field | value |
|---|---|
| Version pinned | Schema 0.2.0 (`$id https://iriusrisk.com/schema/otm-0.2.0.schema.json`, JSON Schema draft-07), released 2023-08-30; SHA-256 `81e7f5a5…45eef0c`. Last repository commit 2025-12-11 (example files only). |
| Steward | IriusRisk (vendor), on GitHub `iriusrisk/OpenThreatModel`; no external governance body. |
| Core entities | `project`, `representations` (diagram, code, threat-model views, with positions and sizes), `assets` (with confidentiality, integrity and availability ratings), `trustZones` (with a numeric `trustRating`), `components` (with a required `parent` trust zone or component), `dataflows` (`source`, `destination`, `bidirectional`), `threats` (with `categories`, `cwes`, and `risk` as likelihood and impact), `mitigations` (with `riskReduction`). A component or data flow lists threat *instances*: `{threat, state, mitigations: [{mitigation, state}]}`. |
| Identifier scheme | Free strings, unique within one file (the example uses UUIDs); no namespace. |
| Encoding | JSON or YAML, validated by JSON Schema. |
| Extension mechanism | A free-form `attributes` map on every element, and no `additionalProperties: false` anywhere, so unknown keys also validate. |
| Licence | Split: the repository (specification text) is CC BY-SA 4.0 (licence file added 2024-11-20), but the schema file's `$comment` says it "is published under the terms of the Apache License 2.0". Corrected after the fan-out (agent 3). |
| Producers and consumers | IriusRisk imports and exports it; IriusRisk's StartLeft (Apache-2.0, active 2026) generates OTM from infrastructure-as-code, diagrams and other tools' exports; Devici hands models to SD Elements in OTM (RPT-0003). |
| Library record | none yet. |

Findings that bear on tmodel:

- **Closest to ARCH-0001's system side.** Asset, Component, TrustBoundary (as zones), DataFlow, Threat and Mitigation all exist, with the generic threat separated from its per-component instance, which matches the generic-to-product split in DEC-009.
- **Nothing on the attack side.** No attack step, attack path, vulnerability or product version; `cwes` and `categories` are unvalidated strings, and there is no CAPEC or ATT&CK field.
- **State without review.** Threat and mitigation `state` are required but free strings (the examples use `exposed`, `mitigated`, `implemented`, `required`); there is no reviewer, date or rationale. A tmodel Review cannot round-trip except through `attributes`.
- **Trust boundaries are zones.** OTM models nested zones with a trust rating; a boundary is implied wherever a data flow crosses zones. Importing into an edge-style TrustBoundary is derivable, but the reverse loses boundaries that are not zone edges.
- **0.x after three years.** The README asks for semantic versioning, but the schema has stayed at 0.2.0 since 2023-08. Adoption is real (IriusRisk, StartLeft, Devici to SD Elements), but the format is controlled by one vendor.

## Tables, pilot rows

Marks as in [dimensions.md](dimensions.md), plus `txt` (added after this pilot): present only as prose, not machine-readable.

### Table 1. Comparison (pilot rows)

| Format | Family | Steward | Core entities | Identifier scheme | Encoding | Extension mechanism | Licence | Library record |
|---|---|---|---|---|---|---|---|---|
| CWE 4.20 / schema 7.3 | weakness | MITRE (CISA-sponsored); submissions to the CWE team | Weakness, Category, View | `CWE-<int>`, never reused | XML + XSD; CSV | — (closed XSD) | MITRE CWE terms, attribution | `cwe`, summarized |
| CVE Record Format 5.2.0 | vulnerability | CVE Program (Board; MITRE secretariat; CISA sponsor) | Record → CNA container + ADP containers | `CVE-YYYY-N{4,19}`; org UUIDs | JSON + JSON Schema draft-07 | `x_` properties and tags; `metrics.other`; `taxonomyMappings` | schema CC0-1.0; records ? | `cve-json-5`, summarized |
| NVD CVE API 2.0 | vulnerability (enrichment) | NIST | cve with weaknesses, metrics, configurations, KEV fields | CVE id; CPE 2.3; match UUIDs | JSON REST | — | ? | none |
| OTM 0.2.0 | threat model | IriusRisk | project, asset, trustZone, component, dataflow, threat, mitigation, representation | free strings, file-local | JSON/YAML + JSON Schema | `attributes` map; open objects | spec CC BY-SA 4.0; schema file Apache-2.0 | none |

### Table 2. Concept crosswalk (pilot rows)

Part 1: ARCH-0001 §3 types.

| Concept | CWE 4.20 | CVE 5.2.0 | NVD API 2.0 | OTM 0.2.0 |
|---|---|---|---|---|
| Asset | — | — | — | `assets[]` = |
| Component | — | `affected[].modules`, `programFiles`, `programRoutines` ⊂ | — | `components[]` = |
| TrustBoundary | — | — | — | `trustZones[]` ≈ (zones; boundaries implied) |
| Weakness | `Weakness` = | `problemTypes[].descriptions[].cweId` ⊂ (reference) | `weaknesses[]` ⊂ (reference + source) | `threats[].cwes[]` ⊂ (unvalidated string) |
| Vulnerability | `Observed_Examples` ⊂ (CVE ids as examples) | record = | `cve` = | — |
| Threat | — | — | — | `threats[]` ≈ (generic) + component `threats[]` (instance) |
| AttackStep | — (`Related_Attack_Patterns` points to CAPEC) | `exploits[]` txt | — | — |
| AttackPath / ThreatChain | `Structure="Chain"` + `StartsWith`/`CanPrecede` ≈ (weakness order, not attacker steps) | — | — | — |
| Mitigation | `Potential_Mitigations` ≈ (generic, by phase and strategy) | `solutions[]`, `workarounds[]` txt | `cisaRequiredAction` txt (KEV only) | `mitigations[]` = + instance `state` |
| RiskScore | `Likelihood_Of_Exploit`, `Common_Consequences` ≈ (qualitative) | `metrics[]` ≈ (CVSS 2.0–4.0, `other`, `scenarios`) | `cvssMetric*`, `ssvcV203` ≈ | `threats[].risk`, asset C/I/A ≈ |
| Review | `Status` ⊂ (editorial maturity) | `disputed` tag, REJECTED state ⊂ | `vulnStatus` ⊂ (NVD workflow) | instance `state` ⊂ (free string) |
| Product / ProductFamily | `Applicable_Platforms` ⊃ (technology classes) | `affected[]` = (vendor, product, cpes, packageURL, versions, defaultStatus) | `configurations` = (CPE with AND/OR) | — |

Part 2: candidate concepts.

| Concept | CWE | CVE | NVD | OTM | Verdict from pilot |
|---|---|---|---|---|---|
| DataFlow | — | — | — | `dataflows[]` = | keep |
| Applicability statement | — | `versions[].status` ≈ (no justification) | `cpeMatch.vulnerable` ≈ | — | keep; VEX adds justification (dimension 3) |
| Exploitation evidence | — | `exploits[]` txt; CISA-ADP SSVC `Exploitation` | `cisaExploitAdd` = | — | keep |
| Party | `Content_History` names and orgs ≈ | `orgId`, `assignerShortName`, `credits` = | `source` ≈ | `project.owner` ⊂ | keep |
| Software identifier | — | `cpes`, `packageURL` = | CPE 2.3 `criteria` = | — | keep; CPE and purl decide scope question 2 |
| Assertion (multi-source) | — | CNA + ADP containers = | Primary/Secondary `source` ≈ | — | keep; confirmed in live data |
| Detection | `Detection_Methods` ≈ (technique class) | — | — | — | keep for dimension 4 |
| Requirement/Control | — | — | — | — | test in dimension 6 |

Part 3: cross-cutting fields.

| Field | CWE | CVE | NVD | OTM |
|---|---|---|---|---|
| Identifier | integer, never reused | CVE id; org UUID | CVE id; match UUID | file-local string |
| Version / revision | catalog version; per-entry `Content_History` | `dateUpdated` per record and container | `lastModified` | `otmVersion` (schema only) |
| Status / deprecation | `Status` (Deprecated, Obsolete, …) | state REJECTED + reason + `replacedBy` | `vulnStatus` (Rejected, Deferred, …) | — |
| Provenance | per entry (submitter, modifications) | per container (`providerMetadata`) | per weakness/metric (`source`, `type`) | — |
| References | `References`, `External_References` | `references[]` with tags | `references[]` | — |
| Human review | — | — | — | — |

### Table 3. Relation crosswalk (pilot rows)

| Edge | CWE | CVE | NVD | OTM |
|---|---|---|---|---|
| `exploits` | — | — | — | — |
| `mitigated_by` | `Potential_Mitigations` ≈ (nested, generic) | `solutions` txt | — | instance `mitigations[]` = (with state) |
| `part_of` | `Has_Member`/`Member_Of` ≈ | — | — | `parent` = |
| `step_of` | `Chain_ID` + `StartsWith` ≈ | — | — | — |
| `instance_of` | `Observed_Examples` ≈ (reverse: weakness → CVE) | `problemTypes.cweId` ≈ (CVE → CWE) | `weaknesses[]` ≈ | component `threats[].threat` = |
| `reviewed_by` | — | — | — | — |
| `applies_to_product` | — | `affected[]` = | `configurations` = | — |
| `supersedes` | deprecated entry names successor txt | `replacedBy` = (rejected records only) | — | — |

Edges the formats have and ARCH-0001 lacks: CWE `ChildOf`/`ParentOf` (specialization, scoped by view), `CanPrecede`/`CanFollow` (causal order), `Requires`/`RequiredBy` (composites), `CanAlsoBe`, `PeerOf`; CWE → CAPEC (`Related_Attack_Pattern`); fit-graded mappings to external taxonomies (CWE `Mapping_Fit`, CVE `taxonomyMappings`); NVD platform dependency (`vulnerable: false` under AND); OTM data flow `source`/`destination`.

### Table 5. Applicability ratings (pilot)

0 = absent, 1 = weak, 2 = partial, 3 = strong; rated within the format's own scope (see the rubric note added to dimensions.md).

| Format | Object model | Provenance | Human review | Federation | AI-grounding |
|---|---|---|---|---|---|
| CWE | 3: Weakness `=`; Mitigation, Chain `≈` | 2: per-entry `Content_History`, not per relation | 1: `Status` and `Mapping_Notes` rationale, no decision record | 2: stable global ids, but one authority mints them | 3: stable id, versioned normative text, bulk XML |
| CVE 5.2.0 | 2: Vulnerability, Product `=`; mitigations and exploits in prose | 3: every container attributed and dated | 1: `disputed`, REJECTED only | 3: global ids, multi-org containers by design | 3: stable ids, bulk repo and API |
| NVD API 2.0 | 2: adds configurations and KEV fields | 2: `source` and `type` per weakness and score, no date | 1: `vulnStatus` is NVD's workflow, no rationale | 2: keyed on CVE id, single authority, read-only | 2: stable ids, but enrichment now sparse (2026-04) |
| OTM 0.2.0 | 2: system-side types `=`; no attack side | 1: `project.owner` only | 1: free-string `state` | 1: file-local ids; exchange yes, merge no | 1: no catalog; CWE ids as strings |

## What the pilot changed in dimensions.md

1. **New mark `txt`**: the concept is present only as prose. The existing marks could not tell CWE's prose successor ("duplicate of CWE-908") from a missing field, and the difference matters for an importer.
2. **Edge qualifiers.** CWE relations need `View_ID`, `Chain_ID` and `Ordinal`; NVD matches need AND/OR and `negate`; mappings carry a fit grade. Table 3 gets a "qualifiers" note per cell, and part 3 of Table 2 gets an "edge qualifiers" row.
3. **CVE and NVD are separate columns.** They differ in steward, provenance model and applicability logic, and NVD's coverage changed in 2026.
4. **Rubric note.** Ratings are within a format's own scope: a catalog is not penalized on Object model for lacking Asset. Provenance and Review for a catalog rate its editorial history.
5. **Coverage candidates added for Phase 4:** SSVC (in CVE ADP containers and the NVD API, so imported data already contains it) and TM-BOM (an emerging threat-model interchange named in RPT-0003).
6. **Columns that worked unchanged:** Table 1 and the per-format record. Table 4 (adoption) is left to the fan-out.

## Open after the pilot

- NVD API rate limits, the NVD data licence and the CVE record content licence (marked `?` above).
- How tools extend CWE locally in practice (dimension 1, question 5).
- The CVE Program's sponsorship after the 2025 contract extension: the pilot confirmed only that the program is operating as of 2026-09.
