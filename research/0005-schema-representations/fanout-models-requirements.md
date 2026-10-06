---
schema: "archdoc/v1"
id: RPT-0005-fanout-models-requirements
title: "RPT-0005 Phase 1 fan-out: threat-model formats, requirements and assurance"
type: research
status: draft
version: "0.1.0"
date: "2026-10-05"
updated: "2026-10-06"
record: RPT-0005
---

> Phase 1 fan-out notes, kept as the research agent wrote them; corrections found later are recorded in the design log (DL-0013). Downloaded files named under `scratchpad/` were not committed (third-party material); each is identified by URL and SHA-256 so it can be fetched again.

# RPT-0005 fan-out, agent 3: dimensions 5 and 6

Threat-model object models (threagile, pytm, OWASP Threat Dragon; OTM as baseline from [pilot.md](pilot.md)) and requirements, controls and assurance (OSCAL, ReqIF 1.2, SysML v2 requirements, OMG SACM 2.x), plus a TM-BOM coverage check. Evidence only; nothing here decides anything.

Method. Every fact below was checked on 2026-10-05 against a downloaded artifact (schema, source file, specification PDF or live repository metadata), not taken from a summary. Files are in `scratchpad/fanout/agent3-files/` with SHA-256 listed in `scratchpad/fanout/agent3-sha256.txt` (138 files) and in section 11. OMG PDFs were kept in the scratch folder only. WebFetch was not used; three WebSearch summaries were used only to find candidates, and every claim taken from them was re-checked against the repository or rejected (section 12). Marks as in [dimensions.md](dimensions.md): `=`, `≈`, `⊂`/`⊃`, `ext`, `txt`, `—`, `?`.

---

## 1. Per-format records

### threagile (master `74e323ed`, schema `support/schema.json`)

| field | value |
|---|---|
| Version pinned | `Threagile/threagile` master at `74e323ed635f` (2026-04-08), the head on 2026-10-05 and the revision RPT-0003 reviewed. Latest tag `v0.9.1` (2024-07-30) plus a moving `stable` tag (2024-11-20). Models and README say `threagile_version: 1.0.0`, but `docs/releases.md` says "1.0.0 Not released yet". Schema `support/schema.json` (JSON Schema draft-07, no version of its own), SHA-256 `2f44c0b6…e715c0`. |
| Steward | The `Threagile` GitHub organization; changes by pull request. No foundation or external governance found. |
| Core entities | `data_assets` (map; `usage`, `quantity`, `confidentiality`, `integrity`, `availability`, `owner`, `origin`, `justification_cia_rating`), `technical_assets` (map; `type` ∈ external-entity, process, datastore; `size`, `machine`, `encryption`, `internet`, `out_of_scope` + `justification_out_of_scope`, `technologies`, C/I/A, `data_assets_processed`/`_stored`, nested `communication_links`), `trust_boundaries` (`type` ∈ network-on-prem, network-dedicated-hoster, network-virtual-lan, network-cloud-provider, network-cloud-security-group, network-policy-namespace-isolation, execution-environment; `technical_assets_inside`, `trust_boundaries_nested`), `shared_runtimes`, `individual_risk_categories` (schema) / `custom_risk_categories` (code) with `risks_identified`, `risk_tracking`, plus prose maps `abuse_cases`, `security_requirements`, `questions`. Output: generated `Risk` objects (`category`, `risk_status`, `severity`, `exploitation_likelihood`, `exploitation_impact`, `synthetic_id`, `most_relevant_*`, `data_breach_probability`, `risk_explanation`, `rating_explanation`) in `risks.json`. |
| Identifier scheme | Map keys and `id` strings, unique within one model. Generated risks get a deterministic `synthetic_id` of the form `category@element@…` (example: `untrusted-deserialization@erp-system`); `risk_tracking` keys may use `*` wildcards between `@` (`ldap-injection@*@ldap-auth-server@*`). No namespace. |
| Encoding | YAML in (with `includes` to split files); JSON Schema draft-07 for editor validation; JSON (`risks.json`, `technical-assets.json`, `stats.json`), PDF, XLSX and diagrams out; REST server mode. |
| Extension mechanism | `tags` (declared in required `tags_available`) on assets, links, boundaries, runtimes; custom risk categories; custom risk rule scripts (`docs/custom-risk-rules.md`: "Highly likely this feature is under development"). The schema has no `additionalProperties: false`, but the Go loader (`pkg/input/model.go`) unmarshals into fixed structs, so unknown keys validate and are then ignored. |
| Licence | MIT (GitHub licence API and README). |
| Producers and consumers | Threagile itself; `tmac` imports it (section 8). |
| Library record | none (new, Phase 2). |

Findings that bear on tmodel:

- **The only one of the three with a real review record.** `risk_tracking.<synthetic risk id>` requires `status` ∈ unchecked, in-discussion, accepted, in-progress, mitigated, false-positive, plus `justification`, `ticket`, `date`, `checked_by`. That is ARCH-0001's Review minus `impact`, attached to a generated risk instance. Wildcard keys let one decision cover many instances without listing them, so an importer must expand the wildcard against the current risk set and record that it did.
- **Generic-to-instance split, done by rule.** 42 built-in rules (`pkg/risks/builtin/*_rule.go`) each define a `RiskCategory` (`id`, `title`, `impact`, `asvs`, `cheat_sheet`, `action`, `mitigation`, `check`, `function`, `stride`, `detection_logic`, `false_positives`, `cwe`) and emit `Risk` instances bound to elements. Category = generic threat, risk = instance: the same split as DEC-009 and OTM.
- **CWE links are often to ids CWE says not to map to.** Every built-in category has exactly one `cwe` integer (25 distinct). Checked against CWE 4.20 `Mapping_Notes/Usage`: 16 are Allowed, 4 Allowed-with-Review, 7 Discouraged and **15 Prohibited**. 14 rules point at CWE-1008, which is a View ("Architectural Concepts"), and `missing-hardening` points at CWE-16, an obsolete Category. The pilot's proposed validation (a Prohibited id is a finding, not a mapping) would flag over a third of threagile's links.
- **Mitigations are prose.** `mitigation`, `action` and `check` are strings on the category; there is no mitigation object, owner or per-instance state other than `risk_tracking.status: mitigated`.
- **Schema and code disagree.** `support/schema.json` and the shipped demo model use `individual_risk_categories` (a map); the loader struct reads `custom_risk_categories` (a list), and `test/all.yaml` uses that key. Both files validate against the schema (0 errors each, checked with `jsonschema`), because the schema is open. The old key survives only in the risk-script parser (`pkg/risks/script/script.go`) and the server's stub template. Whether a model using the schema's key still loads its manual risks in CLI mode was not tested (Go not run; open item).
- **No attack side.** `abuse_cases` is a map of title to prose; there is no attack step, path, CAPEC or ATT&CK field.

### pytm 1.4.0

| field | value |
|---|---|
| Version pinned | `OWASP/pytm` tag `v1.4.0` (GitHub release published 2026-07-06; `CHANGELOG.md` dates 1.4.0 as 2026-05-21). Master is active: on 2026-10-05 alone it gained five commits, including "Remove SetofProcesses element (#364)" (`858ad799`). Source files read at the tag: `pytm/element.py` (`bc435e81…aef131`), `base.py`, `finding.py` (`cbf830c3…921f19`), `threat.py`, `tm.py`, `json.py`, `threatlib/threats.json` (`0ba13d12…24e075`). |
| Steward | OWASP project; `.github/CODEOWNERS` "defaults a maintainer set on all paths" (CHANGELOG). Semantic versioning "in spirit" (CHANGELOG), with a declared breaking change shipped in 1.4.0 (`tm.sqlDump()` removed). |
| Core entities | Pydantic v2 models since 1.4.0. `Element` (`name`, `description`, `inBoundary`, `inScope`, `maxClassification`, `minTLSVersion`, `findings`, `overrides`, `assumptions`, `levels`, `sourceFiles`, `controls`, `severity`, `uuid`); subclasses `Actor`, `Asset` → `Server`, `Datastore`, `Process` (→ `SetOfProcesses`, removed on master), `Lambda`, `ExternalEntity`, `Agent`, `LLM` (new in 1.4.0); `Boundary`; `Dataflow` (`source`, `sink`, `protocol`, `srcPort`, `dstPort`, `tlsVersion`, `data`, `order`, `isResponse`, `responseTo`, `note`); `Data` (`classification`, `isPII`, `isCredentials`, `credentialsLife`, `isStored`, …); `Controls` (43 flags: 41 booleans such as `sanitizesInput`, `usesMFA`, `isHardened`, plus `authenticationScheme` and `usesEncryptionAlgorithm`); `Assumption` (`name`, `exclude` set of threat SIDs, `description`); `Threat` (`id`, `description`, `condition`, `details`, `likelihood`, `severity`, `mitigations`, `prerequisites`, `example`, `references`, `target`); `Finding` (`element`, `target`, `id`, `threat_id`, `severity`, `mitigations`, `references`, `response`, `cvss`, `likelihood`, `assumption`, …); `TM` (`name`, `description`, `threatsFile`, `isOrdered`, `mergeResponses`, `findings`, `excluded_findings`, `assumptions`). |
| Identifier scheme | Elements are keyed by `name` (a write-once field); `uuid` comes from `random.getrandbits(128)` after `random.seed(0)` in `TM.__init__`, so it is reproducible only while element creation order is unchanged. Threats have library SIDs (`INP01` … `LLM09`, 114 entries). Findings get `id=str(finding_count)`, a per-run counter. |
| Encoding | Python source (`tm.py` model scripts); JSON input via `pytm.json.load` (keys `boundaries`, `data`, `elements` with `__class__`, `flows`); `--json` output (serialized `TM`); generated DFD (Graphviz), sequence diagrams, Markdown reports. No published schema file; `tests/input.json` and `tests/output.json` are the de facto fixtures. |
| Extension mechanism | `model_config = ConfigDict(extra="allow")` on `Element`, `Controls`, `Data`, `Finding`, `Assumption`, so arbitrary attributes are kept; a custom threat library through `TM.threatsFile`. |
| Licence | MIT (`LICENSE`, unchanged in substance since 2018-06-27), with MITRE's CAPEC licence reproduced for the CAPEC-derived threat catalog. Not GPL-3.0 (section 12). |
| Producers and consumers | pytm itself; `tmac` imports pytm JSON (section 8). |
| Library record | none (new, Phase 2). |

Findings that bear on tmodel:

- **Threats are rules, mitigations are flags.** A `Threat.condition` is a Python expression over element attributes and `controls` (for example `target.usesEnvironmentVariables is True and target.controls.sanitizesInput is False …`). A mitigation is therefore implicit: setting a control flag makes the condition false and the finding disappears. There is no explicit `mitigated_by` edge to import; it has to be derived by reading the condition.
- **Unset and false look the same.** All 41 boolean controls default to `False`. An importer cannot tell "not implemented" from "nobody said" (also noted by the `tmac` README, section 8).
- **References are strings.** `references` is one free-text string per threat. Of 114 entries, 98 contain CAPEC URLs, 75 contain CWE URLs and none contain ATT&CK. The 90 distinct CWE ids cited are, by CWE 4.20 usage: 56 Allowed, 14 Allowed-with-Review, 15 Discouraged, 5 Prohibited (CWE-133, -227, -713, -714, -719, all Categories). Import is `txt`: URLs must be parsed out.
- **Review is two weak mechanisms.** `Element.overrides` holds `Finding`s that set `response` (documented as "Can be one of: mitigated, transferred, avoided, accepted", but a free string; the README example is Markdown prose), `cvss` and `severity`. `Assumption.exclude` drops threats by SID with a `description`, which is a rejection with rationale. Neither records who or when.
- **Deprecation is a field.** One library entry carries `DEPRECATED`: "AC22 was replaced by AC23 and AC24 …", and `tm.py` skips entries that have it. A `supersedes` edge exists only as text.
- **Ordered flows are not attack paths.** `Dataflow.order` with `TM.isOrdered` orders data flows for sequence diagrams; it is not an attacker's step order.

### OWASP Threat Dragon 2.6.2 (model schema v2)

| field | value |
|---|---|
| Version pinned | `OWASP/threat-dragon` release `v2.6.2` (2026-05-10). Schema `td.vue/src/assets/schema/threat-dragon-v2.schema.json` (`$id` points at `main`; no `$schema` keyword), SHA-256 `9567284b…50489d`. Source tarball SHA-256 `c2c391c1…332583`. `main` (`1753ad0f`, 2026-09-30) is 591 commits ahead and changes the schema and the OTM converter (noted where relevant; unreleased). |
| Steward | OWASP project (Production, per RPT-0003); Apache-2.0. |
| Core entities | `summary` (`title`, `owner`, `description`, `id`), `detail` (`contributors[]`, `diagrams[]`, `reviewer` (required string), `diagramTop`, `threatTop`). A diagram has `diagramType` (STRIDE, LINDDUN, CIA, CIADIE, PLOT4ai, Generic), `version` and AntV X6 `cells[]`. Cell `data.type`: `tm.Actor`, `tm.Process`, `tm.Store`, `tm.Flow`, `tm.Boundary` (curve), `tm.BoundaryBox`, `tm.Text`; properties such as `isEncrypted`, `isPublicNetwork`, `protocol`, `isBidirectional`, `providesAuthentication`, `storesCredentials`, `privilegeLevel`, `outOfScope` + `reasonOutOfScope`, `hasOpenThreats`. Threats live in `cells[].data.threats[]`: `id` (UUID v4), `title`, `type`, `modelType`, `status`, `severity`, `score`, `description`, `mitigation`, `number`, `new`. |
| Identifier scheme | UUIDs for cells and threats (examples: `a25bbb4e-093f-…`, threat `7df716cd-…`); per-model counter `threatTop`. No namespace. |
| Encoding | JSON; JSON Schema for v1, v2, templates, plus bundled copies of the OTM 0.2.0 schema (byte-identical to the pilot's, `81e7f5a5…45eef0c`) and the OWASP Threat Model Library (TM-BOM) schema. |
| Extension mechanism | None declared. The schema is open (no `additionalProperties: false`) and the app only warns on validation failure (`docs/development/schema.md`: "it will not stop the threat model from loading"). On `main`, a `compatibility` block keeps fields from imported OTM and TM-BOM files. |
| Licence | Apache-2.0. |
| Producers and consumers | Threat Dragon; `tmac` imports v2 (section 8). |
| Library record | none (new, Phase 2). |

Findings that bear on tmodel:

- **The published schema does not validate threats.** The schema declares threats at `cells[].threats[]` with `threatId`; the app writes them to `cells[].data.threats[]` with `id`. Corrupting every threat in the v2 demo model (status set to an integer, title removed) leaves the error count unchanged at 11. The 11 errors, and 9 in the Threat Model Cookbook model `generic-cms.json`, are all `attrs.body.strokeDasharray: null`: the project's own demo models fail its own schema.
- **Status vocabulary is small and growing.** v2.6.2's editor offers `NotApplicable`, `Open`, `Mitigated` and severities `TBD`, `Low`, `Medium`, `High`, `Critical`; `score` is a free string. The `main` schema description extends status to "NA, Open, Mitigated, Accepted, Transferred, Avoided or Eliminated", which is closer to risk-treatment terms (unreleased).
- **Review is model-level only.** `detail.reviewer` is one required string for the whole model; per threat there is a status but no reviewer, date or rationale field.
- **Threat type is a category, not a threat.** `type` holds a STRIDE, LINDDUN, CIA-DIE or PLOT4ai category label and `modelType` the method; there is no generic threat catalog, no CWE, CAPEC or ATT&CK field anywhere in the v2 schema.
- **Containment is geometric.** No cell has a parent field; membership in a boundary is implied by drawing position. An importer must compute it.
- **Converters exist in the tree but do not work at v2.6.2.** See section 8: OTM import is refused with "not yet supported", the TD→OTM exporter is dead code that emits schema-invalid OTM, and TM-BOM import works by flattening CWE and CAPEC ids into description text.

### OSCAL 1.2.3

| field | value |
|---|---|
| Version pinned | OSCAL `v1.2.3` (GitHub release 2026-08-07). `oscal_complete_schema.json` (JSON Schema draft-07, `$id …/1.2.3/oscal-complete-schema.json`), SHA-256 `38432410…87a206`; `oscal_mapping_schema.json` `ed28b68c…f8817e`; constraints from `oscal_catalog_metaschema_RESOLVED.xml` and `src/metaschema/oscal_mapping-common_metaschema.xml`. Example data: NIST SP 800-53 Rev 5.2.0 catalog from `usnistgov/oscal-content` at `78650f02` (`oscal-version` 1.2.2, last-modified 2026-05-11), SHA-256 `01f37cf9…9bc062`. |
| Steward | NIST (`usnistgov/OSCAL`); development on GitHub. Releases 1.2.0 (2025-12-12), 1.2.1, 1.2.2 and 1.2.3 within ten months. |
| Core entities | Models: `catalog` (`groups`, `controls` with nested enhancement `controls`, `params`, `parts`, `props`, `links`), `profile` (`imports` with `include-all`/`exclude-controls`, `merge`, `modify` with `set-parameters` and `alters`), `component-definition` (`defined-components` with `control-implementations[].implemented-requirements`), `system-security-plan` (`system-characteristics` incl. `information-types` with C/I/A impact, `authorization-boundary`, `network-architecture`, `data-flow`; `system-implementation.components`; `control-implementation.implemented-requirements[].by-components`), `assessment-plan`, `assessment-results` (`result` with `observations`, `risks`, `findings`, `attestations`, `assessment-log`, `reviewed-controls`), `plan-of-action-and-milestones` (`poam-item`), and since 1.2.0 a `mapping-collection` model. |
| Identifier scheme | Every document and most objects carry a `uuid`; the schema says a UUID "should be consistently used for a given location across revisions of the document". Controls have a token `id` unique within their catalog (`ac-2`, enhancement `ac-2.10`), parameters `ac-02_odp.01`, statement parts `ac-2_smt.k`; implementations point at controls by `control-id`, resolved through the imported profile or catalog. |
| Encoding | XML (XSD), JSON (JSON Schema), YAML; all generated from NIST Metaschema definitions, with XSL converters between XML and JSON shipped in each release. |
| Extension mechanism | `props` (name/value with an optional `ns` namespace URI and `class`), `links`, and `parts` with `ns`. Objects are closed (`additionalProperties: false` throughout), and many allowed-value lists are `allow-other="yes"` in the metaschema, so local vocabularies go in a namespace rather than new fields. |
| Licence | Public domain in the US and CC0 1.0 worldwide (`LICENSE.md`, SHA-256 `63407ac4…3244b1`). |
| Library record | none (pending in RPT-0013; new, Phase 2). |

Findings that bear on tmodel:

- **Withdrawal has a machine-readable successor.** In SP 800-53 Rev 5.2.0, 182 of 1,196 controls and enhancements carry `props: status=withdrawn`; their `links` use `rel` `incorporated-into` (166) or `moved-to` (34). Example: `ac-2.10` → `#ac-2_smt.k` (`incorporated-into`). Allowed `rel` values for control links are `reference`, `related`, `required`, `incorporated-into`, `moved-to`; status values include withdrawn, reserved, deprecated, conditional, superseded, modified, experimental. This is the `supersedes` edge CWE lacks (pilot).
- **Parameters are structured.** A `param` has `id`, `label`, `usage`, `guidelines`, `constraints`, `depends-on`, and either `values` or `select` (`how-many` one or one-or-more, `choice[]`). Profiles set them (`modify.set-parameters`), SSPs and component definitions set them per implementation.
- **Implementation and evidence are separate, linked objects.** A control is implemented by `implemented-requirements[].by-components[]` (`component-uuid`, `implementation-status.state` ∈ implemented, partial, planned, alternative, not-applicable); evidence is an assessment `observation` (`methods` EXAMINE, INTERVIEW, TEST, UNKNOWN; `relevant-evidence[].href`; `collected`; `expires`); the verdict is a `finding.target.status.state` ∈ satisfied, not-satisfied with `reason` pass, fail, other, pointing at a `statement-id` or `objective-id`. This is the evidence chain RPT-0013 §4 sketches for the "threats-mitigated" check.
- **Risks are first-class and carry threat ids.** `risk` has `status` ∈ open, investigating, remediating, deviation-requested, deviation-approved, closed; `threat-ids[]` (`system` URI, open list); `characterizations[].facets[]` whose `system` values include `http://cve.mitre.org` and CVSS v2.0, v3.0, v3.1 and v4.0; `mitigating-factors[]` pointing at an implementation (`implementation-uuid`); `remediations[]` with `lifecycle` recommendation, planned, completed; and a `risk-log` of entries with `logged-by` and `status-change`. It is the closest standard object to ARCH-0001's Threat + RiskScore + Mitigation + lifecycle (R-021) in this survey.
- **Provenance is native.** Findings, observations, risks and responses carry `origins[].actors[]` with `type` ∈ tool, assessment-platform, party and an `actor-uuid`; `metadata` has `parties`, `responsible-parties`, `revisions`, and `actions` ("An action applied by a role within a given party to the content", with `type` such as approval, `date`, `responsible-parties`). Machine-proposed versus human-asserted can be told apart by `origin-actor.type`.
- **Cross-framework mapping is now standard.** The 1.2.0 mapping model's `map` requires `relationship` ∈ equivalent-to, equal-to, subset-of, superset-of, intersects-with, no-relationship, and carries `matching-rationale` (syntactic, semantic, functional), `confidence-score`, `coverage` and `qualifiers`; the collection's `provenance.method` is human, automation or hybrid. This is a ready encoding for MAP-0001's `maps_to` edges, with fit grades.
- **No system model.** Boundaries and data flows in an SSP are `description` + `diagrams` (prose and images); there is no threat, attack step or data-flow object.

### ReqIF 1.2

| field | value |
|---|---|
| Version pinned | OMG Requirements Interchange Format 1.2, formal/16-07-01 (July 2016); XSD `http://www.omg.org/spec/ReqIF/20110401/reqif.xsd` (SHA-256 `9243f345…ba94c0`), `driver.xsd` (`4995bc97…44effd`), CMOF `ReqIF/20101201/reqif.cmof` (not downloaded). PDF SHA-256 `c9d4fc54…299a2f` (98 pages, 48 "Constraints" sections). |
| Steward | OMG. Originated as RIF from the HIS automotive group and then ProSTEP iViP (spec §"Preface"). No change since 2016. |
| Core entities | `REQ-IF` with `REQ-IF-HEADER` (`CREATION-TIME`, `REPOSITORY-ID`, `REQ-IF-TOOL-ID`, `SOURCE-TOOL-ID`, `REQ-IF-VERSION`, `TITLE`, `COMMENT`) and `REQ-IF-CONTENT`: `DATATYPES` (Boolean, Date, Enumeration, Integer, Real, String, XHTML), `SPEC-TYPES` (`SPEC-OBJECT-TYPE`, `SPEC-RELATION-TYPE`, `SPECIFICATION-TYPE`, `RELATION-GROUP-TYPE`), `SPEC-OBJECTS`, `SPEC-RELATIONS` (`SOURCE`, `TARGET`, `TYPE`), `SPECIFICATIONS` (trees of `SPEC-HIERARCHY` pointing at objects), `RELATION-GROUPS`; 38 complex types in the XSD. |
| Identifier scheme | `IDENTIFIER` (`xsd:ID`) on every Identifiable; spec: "The value of Identifiable::identifier must be globally unique" and Identifiable "provides globally unique and lifetime immutable identity". Optional `ALTERNATIVE-ID` for tools that cannot keep it. |
| Encoding | XML + XSD; one exchange document per transfer. |
| Extension mechanism | Everything domain-specific is user-defined: object, relation and specification types with typed attribute definitions. `REQ-IF-TOOL-EXTENSION` holds `xsd:any namespace="##other" processContents="lax"`. |
| Licence | OMG specification; IPR mode "RF-Limited" (OMG page). |
| Library record | none (new, Phase 2). |

Findings that bear on tmodel:

- **No trace vocabulary.** ReqIF fixes the mechanism (a `SPEC-RELATION` from one `SPEC-OBJECT` to another, typed by a user `SPEC-RELATION-TYPE` with its own attributes) but not the meaning. "satisfies", "verifies", "derives" or "mitigates" exist only as relation-type names a partner agrees on. The spec lists relations' purposes as "to establish traceability" and "to connect non-functional to functional requirements".
- **Change tracking without authorship.** Every element has required `LAST-CHANGE` (dateTime) but no author; the header names the exporting tool. Status is the spec's own example of a user-defined enumeration attribute ("accepted," "rejected," etc.), not a built-in.
- **Access control is in the format.** `IS-EDITABLE` on hierarchies and attribute definitions lets an exporter mark content read-only for the partner; that is review-adjacent (who may change what), not a review record.
- **Identity is the strong point.** Globally unique, lifetime-immutable ids designed for cross-company round trips make ReqIF a candidate carrier for exchanging tmodel Requirements and Mitigations with requirements tools, if a SpecObjectType/SpecRelationType profile is agreed.

### SysML v2.0 requirements (with KerML 1.0 and Systems Modeling API 1.0)

| field | value |
|---|---|
| Version pinned | SysML 2.0, Part 1 Language, formal/2026-03-02 (PDF cover dated March 2026; the OMG page says "Publication Date: September 2025"), PDF SHA-256 `46e6c047…84a83a`. KerML 1.0 formal/2026-03-01 (`3bcc96f9…373697`). Systems Modeling API and Services 1.0 formal/26-03-04. Machine-readable files dated 20250201: `SysML.json` (JSON Schema 2020-12, `bb0d8af1…d546c5`), API `Schema.json` (`cd1d7435…589274`), `Systems-Library.kpar` (`df7d8b2c…793a1f`), `Requirement-Derivation-Domain-Library.kpar` (`a136e72a…aee6e5`), `Metadata-Domain-Library.kpar` (`5c51cd3b…458b9b`). |
| Steward | OMG (Systems Modeling); pilot implementation and API reference implementation by the SysML v2 Submission Team on GitHub (`Systems-Modeling/*`, EPL-2.0). |
| Core entities | `RequirementDefinition`/`RequirementUsage` (`reqId`, `text`, `subjectParameter`, `actorParameter`, `stakeholderParameter`, `assumedConstraint`, `requiredConstraint`, `framedConcern`), `ConcernUsage`, `SatisfyRequirementUsage` (`satisfiedRequirement`, `satisfyingFeature`, `isNegated`), `VerificationCaseUsage` (`objectiveRequirement`, `verifiedRequirement`) with `RequirementVerificationMembership`, `Dependency` (`client`, `supplier`), `AllocationUsage`, `MetadataUsage`; library `Requirements::RequirementCheck` (with `FunctionalRequirementCheck`, `InterfaceRequirementCheck`, `PerformanceRequirementCheck`, `PhysicalRequirementCheck`, `DesignConstraintCheck`), `VerificationCases::VerdictKind` (pass, fail, inconclusive, error), `VerificationMethodKind` (inspect, analyze, demo, test), `DerivationConnections::Derivation`, `ModelingMetadata::StatusInfo`/`Rationale`/`Issue`/`Refinement`, `RiskMetadata::Risk`. Plus the whole systems model (parts, ports, interfaces, flows, actions, states). |
| Identifier scheme | KerML `elementId`: "The globally unique identifier for this Element. This is intended to be set by tooling, and it must not change during the lifetime of the Element" (JSON `@id`, UUID). `reqId` "redefines declaredShortName", the modeler's id, written `requirement <'1'> name`. Versions are API `Commit`s on `Branch`es of a `Project` (`previousCommit`, `created`). |
| Encoding | Textual notation (`.sysml`), JSON (SysML.json), XMI; `.kpar` model-interchange archives; REST/HTTP API (OpenAPI). |
| Extension mechanism | User-defined `metadata def` and library packages; semantic metadata can introduce keywords (`#derive`, `#refinement`). |
| Licence | OMG specification; IPR mode "Non-Assert" (OMG pages). Pilot implementation EPL-2.0. |
| Library record | none (pending in RPT-0013; new, Phase 2). |

Findings that bear on tmodel:

- **All four trace links are typed.** satisfy: `satisfy vehicleMaximumMass by vehicle1;` (a `SatisfyRequirementUsage`, negatable with `not satisfy`); verify: `objective { verify vehicleMassRequirement; }` inside a verification case, whose result is a `VerdictKind`; derive: `#derivation connection { end #original ::> …; end #derive ::> …; }` from the Requirement Derivation domain library, with the asserted constraint that satisfying the original implies satisfying each derived requirement; refine: `metadata def <refinement> Refinement` on a `Dependency`. Allocation is `allocate x to y`.
- **Satisfaction is a logical claim, not just a link.** A requirement is a constraint (`assumptions` imply `constraints`), and satisfy asserts it holds for a subject. That is stronger than tmodel's `mitigated_by`; a Mitigation modeled as satisfying a security requirement would carry evaluable semantics.
- **Status and rationale are library metadata.** `StatusInfo` has `originator`, `owner`, `status` ∈ open, tbd, tbr, tbc, done, closed, and `risk`; `Rationale` has `text` and `explanation`. There is no reviewer, review date or accept/reject verdict, and the API `Commit` has no author field.
- **No security vocabulary.** Nothing in the standard libraries names a threat, attack, weakness or control. `RiskMetadata::Risk` is project risk (`technicalRisk`, `scheduleRisk`, `costRisk` as probability/impact levels 0–1). Security content would be a user library.
- **Product lines are in the language.** `variation`/`variant` definitions and usages (spec annex A.12 "Variability") are a native candidate for ProductFamily (not examined further).

### OMG SACM 2.3

| field | value |
|---|---|
| Version pinned | Structured Assurance Case Metamodel 2.3, formal/23-05-08 (October 2023); normative `SACM/20220301/SACM.xml` (ptc/22-03-13, UML XMI), SHA-256 `4bc12020…fbeb1e`; PDF `8004a2ee…de3012` (95 pages). OMG also lists 2.4 Beta 1 (publication date September 2026; `SACM/20260504/SACM2.4_Metamodel.xml`), not read. |
| Steward | OMG; revision task force members listed in `SystemsAssuranceGroup/SACM` README: MITRE, University of Cambridge, University of York. Not IETF SACM. |
| Core entities | 54 classes in the XMI. Base: `SACMElement` (`gid`, `isCitation`, `isAbstract`, `citedElement`, `abstractForm`), `ModelElement` (name, description, `ImplementationConstraint`, `Note`, `TaggedValue`). Argumentation: `ArgumentPackage` (+ `Interface`, `Binding`), `ArgumentGroup`, `Claim`, `ArgumentReasoning`, `ArtifactReference`, `Assertion` (`assertionDeclaration`, `metaClaim`), `AssertedRelationship` (`isCounter`, `reasoning`, `source`, `target`) with `AssertedInference`, `AssertedEvidence`, `AssertedContext`, `AssertedArtifactSupport`, `AssertedArtifactContext`. Artifact: `Artifact` (`version`, `date`), `Activity` (`startTime`, `endTime`), `Event`, `Participant`, `Resource` (`location`), `Technique`, `Property`, and the artifact-to-artifact relationship. Terminology: `Term` (`externalReference`, `origin`), `Category`, `Expression`. Enumeration `AssertionDeclaration`: asserted, needsSupport, assumed, axiomatic, defeated, asCited. |
| Identifier scheme | `gid`: "a unique identifier that is unique within the scope of the model instance" (not global). Cross-package references by citation (`isCitation`, `citedElement`) through package interfaces. |
| Encoding | XMI (MOF/UML metamodel) and a UML profile; no JSON or XSD binding. |
| Extension mechanism | `TaggedValue` (key/value), `ImplementationConstraint`, `Note` on any `ModelElement`; `Term.externalReference` to outside vocabularies; abstract elements as patterns (`isAbstract`, `abstractForm`). |
| Licence | OMG specification; IPR mode "Non-Assert". |
| Library record | none (pending in RPT-0013; new, Phase 2). |

Findings that bear on tmodel:

- **Claim states are a review vocabulary.** `AssertionDeclaration` distinguishes asserted, needsSupport ("further argumentation has yet to be provided"), assumed, axiomatic, defeated ("defeated by counter-evidence and/or argumentation") and asCited. Mapped onto tmodel, a machine-proposed "threat T is mitigated in product P" is needsSupport until a human attaches evidence; a rejected one is defeated.
- **Counter-evidence is native.** Any `AssertedRelationship` can have `isCounter = true`, so evidence against a mitigation claim is recorded, not deleted. None of the threat-model formats has this.
- **Who and when live in the artifact model, not on the claim.** `Participant`, `Activity` (start, end), `Event` and `Technique` can be linked to `Artifact`s, but an `Assertion` has no author or date of its own.
- **Spec and XMI disagree on one class name.** PDF §12.14 defines `ArtifactAssetRelationship`; the normative XMI names it `ArtifactAssertedRelationship`. An importer keyed on the XMI and a reader of the PDF will not match.
- **Modular, but only locally identified.** Package interfaces and bindings let organizations publish part of an argument and cite elements across packages; `gid` is unique only within a model, so federation depends on package-level citation, not global ids.

### Answers to the dimension questions

**Dimension 5 (threat-model object models), with OTM from the pilot.**

1. *Assets, components, flows, boundaries, threats, mitigations, risk.* OTM: `assets`, `components`, `dataflows`, `trustZones`, generic `threats` + per-component instances, `mitigations` with `riskReduction`, `risk` likelihood/impact. threagile: `data_assets`, `technical_assets`, `communication_links` (nested under the source asset, with protocol, authentication, authorization, VPN, IP filtering, read-only and the data assets sent and received), `trust_boundaries` (typed, nested, list members), `shared_runtimes`; threats are rule-generated `Risk`s under `RiskCategory`s; mitigations are prose on the category; risk is severity, exploitation likelihood and impact, and data-breach probability. pytm: `Data`, `Element` subclasses, `Dataflow`, `Boundary`; threats are library `Threat`s with executable `condition`, instances are `Finding`s; mitigations are `Controls` flags plus prose; risk is `severity`, likelihood and a `cvss` string. Threat Dragon: no asset object (only flags such as `storesCredentials`); `tm.Actor`/`tm.Process`/`tm.Store` cells; `tm.Flow` cells; `tm.Boundary`/`tm.BoundaryBox` drawings; threats only as per-cell instances with prose `mitigation`; risk is `severity` and a free `score`.
2. *CWE, CAPEC, ATT&CK ids.* OTM: `threats[].cwes[]` unvalidated strings. threagile: one `cwe` integer per risk category (15 of 42 built-ins point at Prohibited ids) plus an `asvs` chapter string and a cheat-sheet URL; no CAPEC or ATT&CK. pytm: CAPEC and CWE URLs and CVE ids inside the free-text `references` string; no ATT&CK. Threat Dragon: none (TM-BOM import turns `capec_id`/`cwe_id` into description text). None references ATT&CK.
3. *Review, approval, owners, per-threat status.* OTM: free-string `state` per instance; `project.owner`. threagile: `risk_tracking` with status enum, justification, ticket, date, `checked_by` (the strongest); `author`, `contributors`; asset `owner`. pytm: `overrides` (response, cvss, severity) and `Assumption.exclude` with description; no owner or reviewer. Threat Dragon: per-threat `status` (3 values at 2.6.2, 7 on `main`), model-level `owner`, `reviewer`, `contributors`.
4. *Conversion and loss.* Section 8.
5. *Schema maturity.* OTM: published JSON Schema at 0.2.0 since 2023-08, example files, vendor-controlled. threagile: published draft-07 schema, unversioned and out of step with the loader (`individual_risk_categories` versus `custom_risk_categories`); test YAML fixtures; last tag 2024, 1.0.0 unreleased. pytm: no schema file; Pydantic models since 1.4.0 could generate one but none is published; JSON fixtures in `tests/`; semantic versioning with a declared exception. Threat Dragon: published v1 and v2 schemas, validation only warns, the threat payload is outside the schema, and shipped demo models fail it; frequent releases (2.6.0 to 2.6.2 in six weeks).

**Dimension 6 (requirements, controls, assurance).**

1. *Identification, parameterization, versioning.* OSCAL: control token `id` within a catalog plus document and object UUIDs; `params` with values or selections, set by profiles and implementations; catalog `metadata.version`/`revisions`, control `status` props and `moved-to`/`incorporated-into` links. ReqIF: globally unique, immutable `IDENTIFIER` and `LAST-CHANGE`; no parameters; no version beyond the timestamp. SysML v2: `elementId` (global, immutable) and `reqId` (modeler's short name); parameterization through requirement attributes and redefinition (`:>> speedLimit = 100[km/h]` in a satisfy); versions are API commits. SACM: `gid` within the model; `Artifact.version` and `date`; no parameters.
2. *Link to implementation and to evidence.* OSCAL: `by-components[].component-uuid` with `implementation-status`; evidence via `observations` (`relevant-evidence[].href`, `methods`, `collected`, `expires`) and `findings` (`target.status`, `related-observations`). ReqIF: only through user-typed `SPEC-RELATION`s. SysML v2: `satisfy R by X` (implementation) and verification cases with `verify` and a `VerdictKind` result (evidence). SACM: `AssertedEvidence` from an `ArtifactReference` (cited `Artifact` with version, date, `Resource.location`) to a `Claim`.
3. *Trace links.* satisfies: SysML `SatisfyRequirementUsage` (=); OSCAL `by-component` (implements) and finding status `satisfied` (≈); OSCAL `by-component.satisfied` means a leveraging system satisfying a provider's responsibility (⊂); ReqIF user-typed; SACM `AssertedInference`/`AssertedEvidence` (≈). verifies: SysML `RequirementVerificationMembership` (=); OSCAL `finding` → `objective-id` with observations (=); SACM `AssertedEvidence` (≈). refines: SysML `#refinement` (=); OSCAL profile `alters` and control enhancements (≈). derives: SysML `Derivation` (=); OSCAL profile import/modify and mapping `subset-of` (≈). Cross-framework `maps_to`: OSCAL mapping model (=, with relationship, rationale and confidence).
4. *Mapping onto Mitigation, Review and a Requirement/Control concept.* A Requirement/Control row is justified: OSCAL `control`, SysML `RequirementUsage`, ReqIF `SPEC-OBJECT` (typed), and CycloneDX 2.0-dev `requirement`/`control` (section 9) all carry it, and MAP-0001 already models 19 of them. tmodel's Mitigation corresponds to an *implementation* of a control (OSCAL `implemented-requirement`/`by-component` with state; SysML satisfy; OSCAL risk `mitigating-factors`), not to the control itself, so the formats suggest Mitigation `implements` Control, not Mitigation = Control. tmodel's Review maps to OSCAL `finding` + `attestation` + `metadata.actions` (verdict, assessor, approval), SysML `VerdictKind` + `StatusInfo` + `Rationale`, and SACM `AssertionDeclaration` + `isCounter`; none of them has ARCH-0001's "impact the human assigned".

---

## 2. Table 1 rows

| Format | Family | Steward | Core entities | Identifier scheme | Encoding | Extension mechanism | Licence | Library record |
|---|---|---|---|---|---|---|---|---|
| threagile (master `74e323ed`; tag v0.9.1) | threat model | Threagile GitHub org; PRs | data_assets, technical_assets (+ communication_links), trust_boundaries, shared_runtimes, risk categories, risks, risk_tracking | file-local keys; deterministic `category@element…` risk ids with wildcards in tracking | YAML + JSON Schema draft-07; JSON/PDF/XLSX out | `tags`; custom risk categories; risk scripts (under development) | MIT | none (new, Phase 2) |
| pytm 1.4.0 | threat model | OWASP; CODEOWNERS maintainers | Element subclasses, Boundary, Dataflow, Data, Controls, Threat, Finding, Assumption, TM | element `name`; seeded `uuid`; threat SID (`INP01`); per-run finding counter | Python (Pydantic v2) + JSON in/out; no schema file | `extra="allow"` attributes; custom `threatsFile` | MIT (+ CAPEC terms) | none (new, Phase 2) |
| OWASP Threat Dragon 2.6.2 (schema v2) | threat model | OWASP | summary, detail, diagrams, cells (Actor, Process, Store, Flow, Boundary, BoundaryBox, Text), per-cell threats | UUIDs per cell and threat; file-local | JSON + JSON Schema (open; warn-only) | — (open schema; `compatibility` block on `main`) | Apache-2.0 | none (new, Phase 2) |
| OSCAL 1.2.3 | requirement/control | NIST; GitHub | catalog, profile, component-definition, SSP, assessment-plan, assessment-results, POA&M, mapping-collection | UUIDs everywhere; control token ids within a catalog (`ac-2.10`) | XML/JSON/YAML from Metaschema; XSD + JSON Schema | namespaced `props`, `links`, `parts` (`ns`) | US public domain + CC0 1.0 | none (new, Phase 2) |
| ReqIF 1.2 | requirement/control | OMG (from HIS / ProSTEP iViP RIF) | SpecObject, SpecRelation, Specification/SpecHierarchy, RelationGroup, SpecTypes, Datatypes | `IDENTIFIER` xsd:ID, globally unique, lifetime immutable | XML + XSD (+ CMOF) | user-defined types; `REQ-IF-TOOL-EXTENSION` (`xsd:any ##other`) | OMG spec, IPR RF-Limited | none (new, Phase 2) |
| SysML v2.0 (requirements) | requirement/control (systems model) | OMG; SST pilot on GitHub | RequirementDefinition/Usage, Concern, SatisfyRequirementUsage, VerificationCase, Derivation, Dependency, Allocation, MetadataUsage | `elementId` (global, immutable) + `reqId` short name | textual `.sysml`, JSON (2020-12), XMI, `.kpar`, REST API | `metadata def`, user libraries | OMG spec, IPR Non-Assert; pilot EPL-2.0 | none (new, Phase 2) |
| OMG SACM 2.3 | assurance | OMG; RTF (MITRE, Cambridge, York) | ArgumentPackage, Claim, ArgumentReasoning, AssertedRelationship family, ArtifactReference, Artifact, Activity, Participant, Event, Term | `gid` unique within a model instance; citations across packages | XMI (MOF/UML) + UML profile | TaggedValue, ImplementationConstraint, Term.externalReference | OMG spec, IPR Non-Assert | none (new, Phase 2) |

---

## 3. Table 2 cells

Split in two for width: 2a for the threat-model formats (OTM is in pilot.md), 2b for requirement and assurance formats. Rows are the full lists from dimensions.md.

### Table 2a. Threat-model formats

Part 1: ARCH-0001 §3 types.

| Concept | threagile | pytm 1.4.0 | Threat Dragon 2.6.2 |
|---|---|---|---|
| Asset | `data_assets` = (C/I/A, quantity, owner, origin, rating justification) | `Data` ≈ (classification, isPII, isCredentials); note pytm's `Asset` class is a system node, not an ARCH Asset | ⊂ (booleans on cells: `storesCredentials`, `storesInventory`, `handlesCardPayment`) |
| Component | `technical_assets` = (type, technologies, size, machine, C/I/A) | `Element` subclasses = (Server, Process, Datastore, Lambda, ExternalEntity, Agent, LLM, Actor) | `tm.Process`, `tm.Store`, `tm.Actor` cells = |
| TrustBoundary | `trust_boundaries` = (typed, nested, explicit members) | `Boundary` + `inBoundary` ≈ (zones; nesting) | `tm.Boundary` curve, `tm.BoundaryBox` ≈ (drawn; membership geometric) |
| Weakness | category `cwe` ⊂ (one integer; 15/42 Prohibited) | `references` txt (CWE URLs) | — |
| Vulnerability | — | `references` txt (CVE ids) | — |
| Threat | risk category ≈ (generic) + generated `Risk` (instance, `synthetic_id`) | `Threat` = (generic, SID, condition) + `Finding` (instance) | `data.threats[]` ⊂ (instance only; `type` is a category) |
| AttackStep | `abuse_cases` txt | — | — |
| AttackPath / ThreatChain | — | — (`Dataflow.order` orders flows, not attacks) | — |
| Mitigation | category `mitigation`, `action`, `check` txt; `security_requirements` txt | `Controls` flags ≈ (link to threat only through `condition`); `mitigations` txt | `mitigation` txt |
| RiskScore | `severity`, `exploitation_likelihood`, `exploitation_impact`, `data_breach_probability` ≈ (enums + explanations) | `severity`, `Likelihood Of Attack`, Finding `cvss`, `likelihood` ≈ | `severity` (TBD…Critical), `score` (free string) ≈ |
| Review | `risk_tracking` ≈ (status, justification, ticket, date, checked_by; no impact) | `overrides[].response`, `Assumption` ⊂ (no who/when) | threat `status` ⊂; model `reviewer` ⊂ |
| Product / ProductFamily | — (one system per model) | — | — |

Part 2: candidate concepts.

| Concept | threagile | pytm | Threat Dragon |
|---|---|---|---|
| DataFlow | `communication_links` = (protocol, authn, authz, vpn, ip_filtered, readonly, data sent/received) | `Dataflow` = (protocol, ports, TLS, data, order, response pairing) | `tm.Flow` = (protocol, isEncrypted, isPublicNetwork, isBidirectional) |
| Requirement/Control | `security_requirements` txt (map name → prose) | `Controls` ⊂ (fixed flag set) | — |
| Applicability statement | `out_of_scope` + `justification_out_of_scope` ≈; tracking `false-positive` ≈ | `Assumption.exclude` + description ≈ | `outOfScope` + `reasonOutOfScope`; status `NotApplicable` ≈ |
| Advisory/Remediation | — | — | — |
| Exploitation evidence | — | — | — |
| Party | `author`, `contributors`, asset `owner`, `checked_by` ≈ | — | `owner`, `reviewer`, `contributors` ≈ (model level) |
| DamageScenario | category `impact` txt | threat `details`/`example` txt | — |
| Assertion (multi-source) | — | — | — |
| Software identifier | `technologies` ⊃ (technology classes, not products) | `OS`, `codeType` txt | — |
| Detection/Indicator | category `detection_logic` txt (how the rule detects, not attack detection) | — | — |
| Assumption (new candidate) | `questions` txt | `Assumption` = | — |

Part 3: cross-cutting fields.

| Field | threagile | pytm | Threat Dragon |
|---|---|---|---|
| Identifier | file-local keys; deterministic risk `synthetic_id` | `name`; seeded `uuid`; threat SID; per-run finding counter | UUIDs (cells, threats) |
| Version / revision | `threagile_version` (tool), `date` | — (TM has none) | `version` (tool), diagram `version` |
| Status / deprecation | — (no element status) | threat `DEPRECATED` txt | — |
| Provenance | `author`, `contributors`; `checked_by` + `date` per tracking entry | — | model `owner`, `reviewer`, `contributors` |
| References | `asvs`, `cheat_sheet` URL per category | `references` string per threat | — |
| Human review | `risk_tracking` (status enum + justification + who + when) | `overrides`, `assumptions` | `status` per threat; `reviewer` per model |
| Edge qualifiers | communication-link properties (protocol, authn, authz, vpn, ip_filtered, readonly, usage, data sent/received); tracking wildcards | flow `protocol`, ports, `tlsVersion`, `data`, `order`, `isResponse`/`responseTo` | flow `protocol`, `isEncrypted`, `isPublicNetwork`, `isBidirectional` |

### Table 2b. Requirement, control and assurance formats

Part 1: ARCH-0001 §3 types.

| Concept | OSCAL 1.2.3 | ReqIF 1.2 | SysML v2.0 | SACM 2.3 |
|---|---|---|---|---|
| Asset | SSP `information-types` ≈ (C/I/A impact) | ext | ext (part/item usage) | — |
| Component | SSP `system-implementation.components`; `defined-components` = (type software, hardware, service, …) | ext | `PartUsage` = | — |
| TrustBoundary | `authorization-boundary` txt (description + diagrams) | ext | ext (interfaces/ports) | — |
| Weakness | ext (`props` with `ns`) | ext | ext | — |
| Vulnerability | risk facet `system: http://cve.mitre.org` ≈; observation `types: discovery` ≈ | ext | ext | — |
| Threat | risk `threat-ids` ⊂ (external id + system URI) | ext | ext (`ConcernUsage` could carry it) | — |
| AttackStep | — | ext | ext (`ActionUsage`) | — |
| AttackPath / ThreatChain | — | ext | ext (action succession) | — |
| Mitigation | `implemented-requirement`/`by-component` = (implementation-status); risk `mitigating-factors` = | ext | satisfying feature of `satisfy` ≈ | — (a Claim about it ≈) |
| RiskScore | risk `characterizations.facets` ≈ (CVSS 2.0–4.0, FedRAMP systems) | ext | `RiskMetadata::Risk` ⊃ (project risk) | — |
| Review | `finding.target.status`, `attestations`, `metadata.actions` ≈ (no impact field) | ext (user enum attribute) | `StatusInfo` + `Rationale` + `VerdictKind` ≈ | `AssertionDeclaration` + `isCounter` ≈ |
| Product / ProductFamily | SSP `system-characteristics` ≈; component-definition (vendor product) ≈; `inventory-items` ≈ | — | `variation`/`variant` ≈ (not examined) | — |

Part 2: candidate concepts.

| Concept | OSCAL | ReqIF | SysML v2 | SACM |
|---|---|---|---|---|
| DataFlow | SSP `data-flow` txt (description + diagrams) | ext | `FlowUsage` = | — |
| Requirement/Control | `control` = (params, parts, enhancements) | `SPEC-OBJECT` ≈ (typed by user) | `RequirementUsage` = | `Claim` ⊃ |
| Applicability statement | `implementation-status: not-applicable` ≈; profile include/exclude ≈ | — | — | `AssertedContext` ≈ |
| Advisory/Remediation | risk `remediations` (lifecycle recommendation/planned/completed) =; POA&M items = | — | — | — |
| Exploitation evidence | — | — | — | — |
| Party | `parties`, `responsible-parties`, origin actors = | header tool ids ⊂ | `StatusInfo.originator`/`owner` ≈ | `Participant` ≈ |
| DamageScenario | — | — | — | — |
| Assertion (multi-source) | `origins` per finding/observation/risk ≈ | — | — | `Assertion` ≈ |
| Software identifier | component `props` ⊂ | — | — | — |
| Detection/Indicator | — | — | — | — |
| Verification/Evidence (new candidate) | `observation` (methods, relevant-evidence, collected, expires) = | — | `VerificationCaseUsage` + `VerdictKind` = | `AssertedEvidence` + `Artifact` = |
| Assumption (new candidate) | — | — | requirement `assumedConstraint` ≈ | declaration `assumed` ≈ |

Part 3: cross-cutting fields.

| Field | OSCAL | ReqIF | SysML v2 | SACM |
|---|---|---|---|---|
| Identifier | UUIDs; control token ids within a catalog | global immutable `IDENTIFIER` | global immutable `elementId`; `reqId` | `gid` within a model |
| Version / revision | `metadata.version`, `revisions`, `last-modified`, `oscal-version` | `LAST-CHANGE` per element | API commits/branches/tags | `Artifact.version`, `date` |
| Status / deprecation | control `status` prop (withdrawn …) + `moved-to`/`incorporated-into`; mapping `status` incl. deprecated, superseded | — (user enum) | `StatusInfo.status` (open … closed) | `AssertionDeclaration` |
| Provenance | `origins` (tool, assessment-platform, party); `risk-log.logged-by`; `actions` | header tool ids; no author | `originator`; commits without author | `Participant`/`Activity`/`Event` linked to artifacts |
| References | `links` (`rel`), `back-matter` resources | — | — | `Term.externalReference`, `Resource.location` |
| Human review | finding status + reason; attestations; actions (approval) | — | `VerdictKind`; `StatusInfo`; `Rationale` | `AssertionDeclaration`; `isCounter` |
| Edge qualifiers | link `rel`; mapping `relationship`, `matching-rationale`, `confidence-score`, `coverage`, `qualifiers`; by-component `implementation-status` | user attributes on `SPEC-RELATION-TYPE` | satisfy `isNegated`; verification `VerdictKind`, `VerificationMethodKind`; derivation original/derived ends | `isCounter`; `reasoning` (ArgumentReasoning) |

---

## 4. Table 3 cells

Same marks; qualifiers in parentheses.

### Table 3a. ARCH-0001 edges

| Edge | threagile | pytm | Threat Dragon | OSCAL | ReqIF | SysML v2 | SACM |
|---|---|---|---|---|---|---|---|
| `exploits` | category `cwe` ≈ (one per category; no fit grade) | `references` txt | — | risk `threat-ids` ≈ (`system` URI); CVE facet ≈ | ext | ext | — |
| `mitigated_by` | category `mitigation` txt; tracking `mitigated` ≈ (state, not link) | implicit via `condition` over `controls` ≈; `mitigations` txt | `mitigation` txt + `status: Mitigated` | risk `mitigating-factors[].implementation-uuid` = ; `by-component` (implementation-status) | ext | `satisfy` ≈ (`isNegated`) | `AssertedEvidence` ≈ (`isCounter`) |
| `part_of` | boundary `technical_assets_inside`, `trust_boundaries_nested`, runtime `technical_assets_running` ≈ (containment, not composition) | `inBoundary` = | — (no parent; geometric) | nested `controls` (enhancements), `parts` ≈ | `SPEC-HIERARCHY` ≈ (document tree) | part ownership = | packages, `ArgumentGroup` ≈ |
| `step_of` | — | — (`order` is flow order) | — | — | — | ext (succession) | — |
| `instance_of` | `Risk.category` = (`synthetic_id`) | `Finding.threat_id` = | — (`type` is a category ⊃) | `implemented-requirement.control-id` = (resolved via profile/catalog) | `TYPE` → SpecObjectType ⊃ | feature typing = | `abstractForm` ≈ (pattern) |
| `reviewed_by` | `risk_tracking` key ≈ (wildcards; who, when, ticket) | `overrides` ⊂ | model `reviewer` ⊃ | finding `origins`, `attestations.responsible-parties`, `actions.responsible-parties` ≈ | ext | `StatusInfo` metadata ≈ | — (declaration has no reviewer) |
| `applies_to_product` | — | — | — | SSP `import-profile` + `by-component.component-uuid` ≈; component-definition ≈ | — | allocation ≈ | `AssertedContext` ≈ |
| `supersedes` | — | `DEPRECATED` txt | — | link `rel: moved-to`, `incorporated-into` = (with `status: withdrawn`) | — | — (commit lineage only) | — |

### Table 3b. Edges the formats have and ARCH-0001 lacks

| Edge | threagile | pytm | Threat Dragon | OSCAL | ReqIF | SysML v2 | SACM |
|---|---|---|---|---|---|---|---|
| data flow (source → target) | `communication_links.target` = (protocol, authn, authz, vpn, ip_filtered, readonly, usage, data) | `Dataflow` `source`/`sink` = (protocol, ports, TLS, data, order) | flow `source.cell`/`target.cell` = (protocol, encryption, public, bidirectional) | `data-flow` txt | — | flow connection = | — |
| satisfies | — | — | — | `by-component` ≈; finding status `satisfied` ≈; `by-component.satisfied` ⊂ (leveraged responsibility) | user relation type ext | `SatisfyRequirementUsage` = (`isNegated`) | `AssertedInference` ≈ |
| verifies | category `check` txt | — | — | `finding` → `objective-id`/`statement-id` = (state, reason, `related-observations`, methods) | ext | `RequirementVerificationMembership` = (VerdictKind, VerificationMethodKind) | `AssertedEvidence` = (`isCounter`) |
| derives | — | — | — | profile import/modify ≈; mapping `subset-of` ≈ | ext | `Derivation` connection = (one original, ≥1 derived) | `AssertedInference` ≈ |
| refines | — | — | — | profile `alters`; enhancements ≈ | `SPEC-HIERARCHY` ≈ | `#refinement` dependency = | — |
| maps_to (cross-framework) | `asvs`, `cheat_sheet` txt | `references` txt | — | `mapping-collection` `map` = (relationship, matching-rationale, confidence-score, coverage, provenance method) | — | — | `Term.externalReference` ≈ |
| requires / related | — | — | — | control link `rel: required`, `related` =; param `depends-on` = | ext | `Dependency` ≈ | — |
| excludes (not applicable, with reason) | `out_of_scope` + justification ≈; tracking `false-positive` ≈ | `Assumption.exclude` = (description) | `outOfScope` + `reasonOutOfScope` ≈ | `implementation-status: not-applicable` ≈ | — | — | — |
| counter-evidence / defeat | — | — | — | finding `not-satisfied` ≈ | — | `not satisfy` ≈ | `isCounter`, `defeated` = |
| inherits / leverages | `shared_runtimes` ≈ (co-location) | — | — | `by-component.inherited`/`export`, `leveraged-authorizations` = | — | — | package binding ≈ |
| tracks (decision → instance) | `risk_tracking` → risk `synthetic_id` = (wildcards) | override → threat SID ≈ | — | `risk-log` entries (`status-change`, `related-responses`) = | — | — | — |

---

## 5. Table 4 rows (adoption)

Products already in RPT-0003 are cited, not re-researched. A converter that only imports into its own model is listed as a consumer.

| Format | Produced by | Consumed by | Kind | Evidence | As of |
|---|---|---|---|---|---|
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
| SysML v2 | SysML v2 Pilot Implementation | Pilot Implementation; SysML v2 API Services | open source (EPL-2.0), OMG submission team | `Systems-Modeling/SysML-v2-Pilot-Implementation` (pushed 2026-10-03), `SysML-v2-API-Services` (pushed 2026-05-14) | 2026-10-05 |
| SysML v2 | Eclipse SysON (editors) | Eclipse SysON | open source (EPL-2.0) | `eclipse-syson/syson` README @`b380dada`: edits SysML v2 models; textual exchange "will support" (future) | 2026-10-05 |
| OMG SACM 2.3 | SACM EMF implementation and UML profile (RTF) | same | open source research; last push 2023-05-19 | `SystemsAssuranceGroup/SACM` README @`eb936422` | 2026-10-05 |
| OMG SACM | `wrwei/SACM` (EMF implementation) | same | open source (Apache-2.0), research; last push 2024-12-05 | repo metadata | 2026-10-05 |
| Commercial ReqIF, SysML v2 and SACM tools | ? | ? | commercial | not verified (open item) | — |

---

## 6. Table 5 ratings

Within each format's own scope (rubric note in dimensions.md).

| Format | Object model | Provenance | Human review | Federation | AI-grounding |
|---|---|---|---|---|---|
| threagile | 2: Asset, Component, TrustBoundary, DataFlow `=`; Threat `≈` (category + `Risk`); no attack side, mitigations prose | 1: model `author`/`contributors`; `checked_by` + `date` only on `risk_tracking` entries; generated risks unattributed | 3: `risk_tracking` records status (incl. accepted, false-positive), `justification`, `checked_by`, `date`, `ticket` (risks only) | 1: file-local ids; deterministic `synthetic_id` helps diffing but has no namespace | 2: stable built-in category ids with prose and one `cwe` each, but 15 of 42 CWE links are Prohibited ids |
| pytm 1.4.0 | 2: `Element` subclasses, `Boundary`, `Dataflow` `=`; `Threat`/`Finding` split `=`; mitigation only as `Controls` flags | 0: no author, owner or date anywhere in `TM`, `Element` or `Finding` | 2: `overrides[].response` and `Assumption.exclude` + `description` record decisions with rationale, no who or when | 1: names as ids; per-run `Finding.id` counter; seeded `uuid` depends on creation order | 2: stable threat SIDs with normative text in `threats.json`; CWE/CAPEC only inside a `references` string |
| Threat Dragon 2.6.2 | 2: Actor/Process/Store/Flow/Boundary `=`/`≈`; threats instance-only, no asset object | 1: model `owner`, `reviewer`, `contributors` only | 1: per-threat `status` (3 values), no rationale field; one `reviewer` per model | 1: UUIDs, but file-local semantics and geometric containment | 1: `type` names a STRIDE/LINDDUN category, no catalog ids |
| OSCAL 1.2.3 | 3: `control`, `implemented-requirement`/`by-component`, `component`, `risk`, `finding` cover Requirement/Control, Mitigation, Review | 3: `origins[].actors` (tool, assessment-platform, party) on findings, observations, risks; `risk-log.logged-by`; `metadata.actions` | 3: `finding.target.status` (satisfied/not-satisfied + reason), `attestations`, `actions` (approval), risk `deviation-approved` | 3: UUIDs "consistently used … across revisions"; profiles and leveraged authorizations designed for cross-organization exchange; mapping model | 3: SP 800-53 controls citable by id (`ac-2`) with versioned normative `parts`; withdrawals machine-linked |
| ReqIF 1.2 | 2: generic `SPEC-OBJECT`/`SPEC-RELATION` carry requirements, but every type and link meaning is user-defined | 1: `LAST-CHANGE` per element, exporting tool ids; no author | 1: only a user-defined status enumeration; `IS-EDITABLE` access control | 3: `IDENTIFIER` "must be globally unique", "lifetime immutable"; built for cross-company exchange | 1: no shared catalog; content is whatever the partner exported |
| SysML v2.0 | 2: Requirement, satisfy, verify, derive, refine `=`; Component, DataFlow `=`; no security types | 1: `StatusInfo.originator`/`owner`; API commits have `created` but no author | 2: `VerdictKind`, `StatusInfo.status`, `Rationale`, no reviewer or decision record | 2: global immutable `elementId`; projects, branches, commits in a standard API; cross-model merge not examined | 1: stable library names, but no security catalog to cite |
| OMG SACM 2.3 | 1: argument and evidence only; maps to Review/assurance, not to system or threat types | 2: `Participant`, `Activity`, `Event`, `Artifact.version`/`date`, linked by relationships, not on assertions | 2: `AssertionDeclaration` (needsSupport, assumed, defeated, …) and `isCounter`; no reviewer or date on a claim | 2: `gid` unique only within a model; package interfaces and citations for modular exchange | 1: `Term.externalReference` only |

---

## 7. Table 6 rows (local extension needs)

| Need | Format | Mechanism | Local extension proposed | Routes to |
|---|---|---|---|---|
| Review on any element (reviewer, date, verdict, impact, rationale) | OTM | `attributes` map | namespaced `attributes` keys (for example `tmodel.review.*`) on threat instances and components | DEC-002, #16 |
| Attack steps and paths | OTM | `attributes`; open objects | none fits; keep AttackStep/AttackPath tmodel-native and export only as attributes or to CycloneDX 2.0 (section 9) | DEC-001, DEC-002 |
| CAPEC / ATT&CK references | OTM, threagile, Threat Dragon | OTM `attributes`; threagile `tags`; TD none (open schema) | a references list with taxonomy, id and fit grade (CWE `Mapping_Fit` model, pilot) | #17, DEC-008 |
| Review fields beyond `risk_tracking` (impact; review of non-risk elements) | threagile | `tags` only; loader drops unknown keys | keep tmodel Review outside the YAML, keyed by `synthetic_id`; expand wildcards at import | DEC-001, R-018 |
| Valid CWE mapping on risk categories | threagile, pytm | none (fixed integer / string) | validate against CWE `Usage`; store a corrected mapping with fit grade beside the original | DEC-008, #17 |
| Provenance and reviewer on findings | pytm | `extra="allow"` on `Finding`, `Element` | `reviewer`, `reviewed_at`, `source` attributes on override `Finding`s | DEC-002, R-018 |
| Explicit mitigation link | pytm | none (implicit in `condition`) | derive `mitigated_by` from the control flags each condition reads; store derived edges with provenance "derived" | DEC-001 |
| Per-threat reviewer, date, rationale | Threat Dragon | none declared; schema open | extra keys on `data.threats[]` (survive load because the schema does not validate threats); confirm the app preserves them on save (?) | DEC-002, R-018 |
| Threat, attack and weakness objects | OSCAL | `props` with `ns`; risk `threat-ids` (`system` open); `parts` with `ns` | tmodel namespace for props; ATT&CK/CAPEC URIs as `threat-ids` systems; CWE as a characterization facet system | DEC-002, MAP-0001 |
| System model (boundary, data flow) | OSCAL | none (prose + diagrams) | keep tmodel-native; link by component UUID | DEC-001 |
| Typed trace semantics | ReqIF | user `SPEC-RELATION-TYPE`, `SPEC-OBJECT-TYPE` | a published tmodel ReqIF profile: object types Requirement, Mitigation, Threat; relation types satisfies, verifies, derives, mitigates | DEC-002, #16 |
| Security vocabulary | SysML v2 | `metadata def`, user library package | a small library (Threat, Mitigation, Review metadata with reviewer and date) | DEC-002 |
| Reviewer and date on a claim | SACM | `TaggedValue`; `Participant`/`Activity` artifacts | represent a tmodel Review as an `Activity` with a `Participant`, linked to the evidence artifact; claim state from `AssertionDeclaration` | DEC-001, R-018 |
| Link from a claim to a tmodel element | SACM | `Term.externalReference`, `ArtifactReference` | cite the tmodel record id as the referenced artifact's `Resource.location` | #17 |

---

## 8. Threat-model conversion matrix

### 8.1 Existing converters (verified by reading code; none was executed)

| Converter | Direction | State on 2026-10-05 | Evidence |
|---|---|---|---|
| Threat Dragon v2.6.2 OTM import | OTM → TD | refused: `console.error('Convert OTM to internal TD format not yet supported')` and toast `otmUnsupported`; `toTD.js` converts only `project` and `representations` (component, flow, zone and threat code commented out) | `ImportModel.vue`, `main.desktop.js`, `migration/otm/toTD.js` (`9affc8ae…9289c9`) |
| Threat Dragon v2.6.2 `fromTD.js` | TD → OTM | dead code: nothing imports `openThreatModel.js` (grep of the v2.6.2 source tree). A line-by-line Python port run on the v2 demo model gives OTM that fails the OTM 0.2.0 schema with 71 errors (no `parent`, threat instances without `threat`/`state`, `attributes` as arrays, integer `project.id`) | `fromTD.js` (`26c717c1…51d4f8`); port `tests/td_fromTD_port.py` (`882330c7…470af4`) |
| Threat Dragon `main` (unreleased) OTM import | OTM → TD | implemented June 2026 ("import Open Threat Model diagrams, threats to follow", 2026-06-21; dataflow fix 2026-06-24); `fromTD.js` removed, so no TD → OTM | `main@1753ad0f`: `migration/otm/otm.js` (`7998228e…6272a4`), `cells/threats.js` (`ecef12d1…b45b38`) |
| Threat Dragon v2.6.2 TM-BOM | TM-BOM (OWASP Threat Model Library schema) → TD | import works; export function `exportAsTmbom` exists but has no caller | `migration/tmBom/tmBom.js` (`35d1796e…0f646f2cd60c9a325278f8ee1261e5389b11e1cef63f82bd03d6c308`[sic, see sources]) |
| tmac (`sheltowt/threat_model`) | TD v2, pytm JSON, threagile YAML, OTM → tmac; tmac → OTM, CycloneDX TM-BOM | 20 commits, created 2026-09-06, 1 star. By code reading, its OTM export writes threat instances as `{ threat: id }` without the required `state`, and fixes `risk` at `{likelihood: 50, impact: 50}` | `packages/importers/src/*.ts` @`a92a35f9` |
| StartLeft | CFT, Terraform, tfplan, Visio, draw.io, MTMT, Abacus → OTM | no threagile, pytm or Threat Dragon processor | repo contents @`e1bd3364` |
| threatcl | HCL → OTM | not one of the four formats | README @`03b7f5e2` |

No converter was found between threagile and pytm, threagile and Threat Dragon, or pytm and Threat Dragon, other than tmac's one-way imports into its own model (GitHub repository searches for seven name pairs returned nothing; section 10).

### 8.2 What is lost each way (schema comparison; row = source, column = target)

| from \ to | OTM 0.2.0 | threagile | pytm | Threat Dragon v2 |
|---|---|---|---|---|
| **OTM** | — | No converter. OTM threats must become custom risk categories with `risks_identified`; mitigation objects and `riskReduction` collapse to category prose; instance `state` (free string) cannot map to the `risk_tracking` enum without a table; layout (`representations`) lost; zone `trustRating` lost and threagile's required boundary `type` and asset fields (`usage`, `size`, `machine`, `encryption`, `internet`, C/I/A enums …) must be invented. | No converter. Each OTM threat needs a custom `threatsFile` entry (OTM has no `condition`) and an `overrides` Finding per instance; mitigations become text; layout, `riskReduction`, asset C/I/A numbers lost. | v2.6.2: refused. `main`: threats imported with `status` forced to `Open` ("no reasonable way of calculating this from OTMs freeform strings"), `score` = likelihood × impact / 1000 mapped to severity bands, mitigations flattened to text ("Mitigation applied: … with risk reduction N %"), new UUIDs replace OTM threat ids, `cwes` not carried; OTM-only fields kept in `compatibility`. |
| **threagile** | tmac only. Generated risks have no OTM slot except as threats; `risk_tracking` (justification, ticket, date, `checked_by`) survives only as `attributes`; shared runtimes, abuse cases, security requirements, questions, link security properties (authn, authz, vpn, ip_filtered) go to attributes (tmac parks shared runtimes and data assets under project attributes per its README); boundary `type` enum lost. | — | No converter. `risk_tracking` has no pytm field; C/I/A enums collapse to one `Classification` scale; threagile rules and pytm threats have unrelated ids; link authn/authz enums only partly map to `Controls` booleans. | No converter. Data assets and risk tracking have no TD field; risk categories become per-cell threats with prose; nesting must be redrawn as geometry. |
| **pytm** | tmac only. `condition` (executable rule) and `Assumption` exclusions have no OTM field; `Controls` booleans go to attributes, and unset is indistinguishable from false; `Dataflow.order`/`isResponse` lost; CAPEC/CWE must be parsed out of `references` into `cwes`. | No converter. Findings become custom risks; `overrides.response` text cannot become a `risk_tracking` status without interpretation; no reviewer/date to carry. | — | No converter. Conditions, controls and data objects lost; findings become per-cell threats with prose mitigation; flow order lost. |
| **Threat Dragon** | v2.6.2 dead code (invalid output; only the first diagram; `tm.BoundaryBox` and text dropped; actor threats dropped by a bug: it tests `cell.threats` not `cell.data.threats`). tmac imports TD then exports OTM. Model `reviewer`, `contributors` and threat `status`/`severity` have no OTM field except `attributes`; geometric boundary membership must be computed. | No converter. TD has no data assets or C/I/A; threagile's required asset fields must be invented; TD threats become custom risks; `status` maps partly to `risk_tracking` (no date, no reviewer). | No converter. TD threats have no `condition`; they become overrides on a custom threat file; STRIDE/LINDDUN `type` has no pytm field. | — |

Via TM-BOM (OWASP Threat Model Library schema): Threat Dragon v2.6.2 imports it, and in doing so turns `attack_mechanisms[].capec_id` and `weaknesses[].cwe_id` into description text (`txt`), forces `status: Open`, `severity: TBD`, then sets `Mitigated` only if a linked control's status is in its "mitigated" list. Threat Dragon's bundled copy of the TM-BOM schema is not the tagged v1.0.2 file: it drops `trust_zone` from three `required` lists (24-line diff).

Losses common to every path: review history (who decided what, when, why) except threagile's `risk_tracking`; generic-versus-instance identity (only OTM, threagile and pytm have both, each with different ids); CWE/CAPEC references (strings or prose in all four); attack steps and paths (none of the four has them).

---

## 9. TM-BOM coverage paragraph

"TM-BOM" names two related things. (a) **CycloneDX TM-BOM**, threat-modeling capabilities for CycloneDX: issue CycloneDX/specification#462 "Add threat model capabilities to CycloneDX / TM-BOM" carries the labels "RFC vote accepted", "tc54 accepted" and milestone "2.0", and was closed as completed on 2026-08-20 when PR #678 "[2.0] Threatmodeling and Blueprints" was merged into the `2.0-dev` branch. That branch (`7a3ab082`, 2026-10-05) has modules `cyclonedx-threat-2.0` (threat, threatScenario, attackPattern, technique, attackTree with AND/OR nodes, `attackPath` with ordered `steps` whose `attackPathStep` has `source`, `destination`, `boundaryCrossed`, `exploits`, `mitigations`, killChainPhase, abuseCase, indicators), `risk`, `requirement` (status draft, proposed, approved, implemented, verified, deferred, rejected, replaced, obsolete), `control` (`implementedBy`, `satisfies`, `appliesTo`, `effectiveness`, `owner`) and `blueprint` (zone, boundary, flow, dataStore, actor, assumption). It is unreleased: the CycloneDX 1.7.2 release (2026-09-17) has no `threat-model` component type, and issue #731 ("Risk, threat and Model Schemas Review for TM-BOM") is still open. Steward: OWASP CycloneDX, standardized through Ecma TC54. (b) **OWASP Threat Model Library schema** (`OWASP/www-project-threat-model-library`, MIT, tags v1.0.0 to v1.0.2, latest 2025-10-20; `project.owasp.yaml` `level: 2`), an interim JSON format whose README says the CycloneDX TM-BOM "official release is pending! Once TM-BOM is released, there will be another version released of the Threat Model Library Schema"; it has `cwe-ref`, `capec-ref`, threats with personas, controls with status (assumed, active, suggested, under_review, approved, scheduled, retired, wont_do), risks, `reviewed_at`, and an `extensions` slot, and Threat Dragon imports it. **Recommendation (evidence only):** CycloneDX 2.0 TM-BOM should be a full format in the report, pinned to the `2.0-dev` commit until a release, because it is the only threat-model interchange under a standards body and the only candidate in this survey that carries AttackStep/AttackPath, Requirement and Control together; coordinate with agent 2 (CycloneDX 1.7). The OWASP Threat Model Library schema is a coverage row only.

---

## 10. searches.md rows

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-05 | 5 | GitHub API: `Threagile/threagile` metadata, releases, tags, commits, tree at `74e323ed`; `support/schema.json`, demo and test YAML, `pkg/input/*.go`, `pkg/types/risk*.go`, `pkg/model/read.go`, `docs/*.md`, all 42 `pkg/risks/builtin/*_rule.go` downloaded and parsed | gh + curl | schema/loader drift (`individual_risk_categories` vs `custom_risk_categories`); 42 rule CWE ids |
| 2026-10-05 | 5 | GitHub code search `individual_risk_categories` and `KnownFields` in `Threagile/threagile`; `pkg/server/model.go`, `pkg/risks/script/script.go` downloaded | gh search code | old key only in script parser and server stub |
| 2026-10-05 | 5 | GitHub API: `OWASP/pytm` metadata, releases, commits, tree at `v1.4.0`; element, base, finding, threat, tm, json sources, `threatlib/threats.json`, tests, LICENSE, CHANGELOG, pyproject; LICENSE commit history; LICENSE at master and at `78895796` | gh + curl | pytm MIT since 2018 (contradicts RPT-0003 GPL-3.0); 114 threats |
| 2026-10-05 | 5 | GitHub API: `OWASP/threat-dragon` metadata, releases, tree at `v2.6.2`; schemas, migration code, demo models, `ThreatEditDialog.vue`, views; v2.6.2 source tarball (grep for callers); compare `v2.6.2...main`; `main` OTM migration files | gh + curl | OTM import refused at 2.6.2; fromTD dead code; main imports OTM |
| 2026-10-05 | 5 | GitHub code search `openThreatModel`, `tmBom` in `OWASP/threat-dragon`; commits touching `migration/otm/toTD.js` | gh search code, gh api | OTM import commits of 2026-06-21 and 06-24 |
| 2026-10-05 | 5 | Python port of TD `fromTD.js` run on `v2-threat-model.json`, validated with `jsonschema` against OTM 0.2.0; TD and threagile examples validated against their own schemas | local python3 | 71 OTM errors; TD demo models fail own schema (11, 9) |
| 2026-10-05 | 5 | CWE 4.20 `cwec_latest.xml.zip` re-downloaded; threagile and pytm CWE ids checked against `Mapping_Notes/Usage` | curl + python3 | threagile 15/42 Prohibited; pytm 5/90 Prohibited |
| 2026-10-05 | 5 | threagile to Open Threat Model OTM converter | web search | `sheltowt/threat_model` (tmac); ThreatCode issue #9 (open, not a converter) |
| 2026-10-05 | 5 | pytm export Open Threat Model OTM JSON converter github | web search | `threatcl/go-otm`; pytm; IriusRisk parser blog (not used) |
| 2026-10-05 | 5 | `gh search repos`: "threagile otm", "pytm otm", "otm threagile", "threagile2otm", "pytm2otm", "pytm threat dragon", "threagile threat dragon" | GitHub repository search | no hits |
| 2026-10-05 | 5, 9 | GitHub API: `sheltowt/threat_model` tree, README, importer and exporter sources; `iriusrisk/startleft` metadata, releases, contents, README; `threatcl/threatcl`, `threatcl/go-otm`, `ajokunu/ThreatCode`, `iriusrisk/iriusrisk-cli` metadata and READMEs; `iriusrisk/OpenThreatModel` licence | gh + curl | tmac converters; threatcl OTM export; OTM schema `$comment` Apache-2.0 |
| 2026-10-05 | 5 (TM-BOM) | GitHub API: `OWASP/www-project-threat-model-library` metadata, tags, releases, commits, README, index, schema at v1.0.2; `CycloneDX/specification` releases, `bom-1.7.schema.json`, `gh search issues "TM-BOM"`, issues #462 and #731 with comments and timeline, PR #678 and files, `2.0-dev` module schemas | gh + curl | TM-BOM accepted for CycloneDX 2.0, merged to `2.0-dev` 2026-08-20; unreleased |
| 2026-10-05 | 6 | GitHub API: `usnistgov/OSCAL` releases; v1.2.3 `oscal_complete_schema.json`, `oscal_mapping_schema.json`, catalog/mapping/SSP `*_metaschema_RESOLVED.xml`, `src/metaschema/oscal_mapping-common_metaschema.xml`, `LICENSE.md`; `usnistgov/oscal-content` SP 800-53 Rev 5 catalog | gh + curl | OSCAL 1.2.3; link rels and status values; mapping relationships; 182 withdrawn controls |
| 2026-10-05 | 6 | OMG ReqIF 1.2 page; `reqif.xsd`, `driver.xsd`, PDF | curl | formal/16-07-01; identifier semantics |
| 2026-10-05 | 6 | OMG SysML 2.0, KerML 1.0, Systems Modeling API 1.0 pages; `SysML.json`, API `Schema.json`, `OpenAPI.json`, three `.kpar` libraries; Language and KerML PDFs | curl + pypdf | satisfy/verify/derive/refine definitions; `elementId` semantics |
| 2026-10-05 | 6 | OMG SACM index and 2.3 pages; `SACM/20220301/SACM.xml`; 2.3 PDF | curl + pypdf | 2.3 formal, 2.4 beta 1; AssertionDeclaration; class-name mismatch |
| 2026-10-05 | 6 | OMG SACM 2.x tool support assurance case editor Eclipse OpenCert ACME SACM export | web search | `SystemsAssuranceGroup/SACM`, `nasa/CertWare`, `LuisFelipeAN/sacm-mbac-updatesite`; tool descriptions in the summary not verified |
| 2026-10-05 | 6 | `gh search repos`: "SACM assurance case", "structured assurance case metamodel" | GitHub repository search | `kit-sdq/SACM-Metamodel`, `wrwei/SACM` |
| 2026-10-05 | 9 (adoption) | GitHub API: `oscal-compass/compliance-trestle`, `GSA/oscal-ssp-to-word`, `GSA/fedramp-automation` (404), `FedRAMP/fedramp-automation` (404), `strictdoc-project/strictdoc` (tree grep `reqif`), `eclipse-rmf/org.eclipse.rmf`, `Systems-Modeling/SysML-v2-Pilot-Implementation`, `Systems-Modeling/SysML-v2-API-Services`, `eclipse-syson/syson`, `SystemsAssuranceGroup/SACM`, `nasa/CertWare`, `wrwei/SACM`, `LuisFelipeAN/sacm-mbac-updatesite` | gh | adoption rows in Table 4; FedRAMP OSCAL repository not found |

---

## 11. sources.md rows

| source (title, URL, SHA-256 if downloaded) | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| Threagile, <https://github.com/Threagile/threagile> @`74e323ed635f026ca85bd61b5082f0da053ba1b2`; `support/schema.json` (`2f44c0b6396dee00552c2a2614bd1ae64c3e7582a1df730ec8b798107ae715c0`); `demo/example/threagile.yaml` (`0935fc68f12fe64d7efd5608d1804c6b0506922d89a07da055005efbf37f8e9d`); `pkg/input/model.go` (`ecb5601dd15fea1d7bf40c6f1a84c62b1409d12aabf13f7a7cb52622031eb597`); 42 built-in rule files (concatenated `7c99d46883f32981003a5ebc94c18eb9587f983e8f86ecfe093e08a0b52e06e1`) | spec + tool | 5 | new, Phase 2 | DEC-001, DEC-002 |
| OWASP pytm 1.4.0, <https://github.com/OWASP/pytm/tree/v1.4.0>; `pytm/element.py` (`bc435e81459f251c55765505a81170f9205f3e62c317fe959b47e36e75aef131`), `pytm/finding.py` (`cbf830c3c5975f7145950483333ac21e1b962ff7ba02bdf1e643ee4001921f19`), `pytm/base.py` (`e4bfef56c91052d9f90930e61ec1ee4e507f97a85f3a92991c8a6642dae2921a`), `pytm/threat.py` (`8160640c1e653751eb5d04ee4e1e510ae0d02473a28afcca7325e725c337006c`), `pytm/tm.py` (`1f2b811e34590bb5d512321645dfe3b971490d3123cd4b08cd97d702a0ee2c92`), `pytm/json.py` (`7765a2e0b9c90c940d2661c1b06d45f49846df3d6f2c97907bbf68be196206d9`), `pytm/threatlib/threats.json` (`0ba13d12cf8d67c2e18488f441e47368229c3875e519848f3e26e8a6b824e075`), `LICENSE` (`8dfce4fa0ccb25f5c67b3be6f463bce9bfac7c65e875c667caa5cdccc67194d8`), `tests/input.json` (`99e6c32db28f53f0c576c1586fdf8c08d8d6c2a6011ed1f038c3bbf2e4a5fd22`) | spec + tool | 5 | new, Phase 2 | DEC-001, DEC-002 |
| OWASP Threat Dragon v2.6.2, <https://github.com/OWASP/threat-dragon/tree/v2.6.2>; source tarball (`c2c391c144234c68a8af1cf6f11aee26511fbede8559eaeda55cdcbc94332583`); `threat-dragon-v2.schema.json` (`9567284b86199dbc33276deb68e2ff92a4c23c8de2c50af4f7927719c950489d`); `ThreatDragonModels/v2-threat-model.json` (`d7a9f35dad1653b940fde6bfbf18b59d8826b76026191722c160ec36736f0a41`); `td.vue/src/service/demo/generic-cms.json` (`3b3e1b00602e6f2cd60c9a325278f8ee1261e5389b11e1cef63f82bd03d6c308`); `ThreatEditDialog.vue` (`c3070c6e41acb32035678b868e40258d38357fc23deb2c34ed314541a290c5d4`) | spec + tool | 5 | new, Phase 2 | DEC-002, DEC-006 |
| Threat Dragon OTM and TM-BOM converters: v2.6.2 `migration/otm/fromTD.js` (`26c717c16265482088bbf0bb00d2ab5a2223b729fb4a6f8ef359dbf86151d4f8`), `toTD.js` (`9affc8aed625d232b0d283afd8170db17882801f24a6ba764c65bfa0963289c9`), `migration/tmBom/tmBom.js` (`35d1796e70ce55e77bc4539e394e9678159546407117dba5aee76d0646f3cf17`); `main@1753ad0fae42d65c56e754fa8faf8fb57179f9f5` `migration/otm/otm.js` (`7998228e0fa9875c6afe444a9126c9d6f4565e8ff5dab896dd54895f4c6272a4`), `cells/threats.js` (`ecef12d12f4d88f09b71ea7fec3dfe3db4667774cae8cfe91894948bcfb45b38`), `main` v2 schema (`d918054a571b0925e1f0f41a0a1e0746a487afbfe923df64412ed088c2eb05b2`) | tool | 5 | new, Phase 2 | DEC-002 |
| OTM 0.2.0 schema as bundled in Threat Dragon (`81e7f5a52a0a7d66b44cc4e0c15f21b5d60e1ca945c810e39622a730545eef0c`, identical to the pilot's); `$comment` states Apache-2.0; repo licence CC-BY-SA-4.0, <https://github.com/iriusrisk/OpenThreatModel> | spec | 5 | new, Phase 2 | DEC-002 |
| Python port of TD `fromTD.js` used for the OTM validation test (`882330c70af5dc42060297c0e520bfd225c900074190b14910d5b20659470af4`, scratch only) | test | 5 | none (method) | DEC-002 |
| tmac, <https://github.com/sheltowt/threat_model> @`a92a35f95b0ca51f6d6fc032c7910739e63bd16c`; README (`34af3e1b7fbedb2f40fa1dce716412eb9165a860452494bf0650bf789273d08b`); `export-otm.ts` (`bf5cfabbe8b70fa4c73e416895fa4345889379f2487be0213a1dbf09da6c4d0a`), `threagile.ts` (`9a6b6fa556612f49081ef29625198052df041c954ff582f88251b7421c9858c4`), `pytm.ts` (`f1fecedb81d376bed8630922f0d5fdd4f763a3d6f27b8809d8e89c63c4f4b88f`), `threat-dragon.ts` (`dcfe1131085afe042f8e945c9fde1e61a8bc6ff0c389d3ae1dd4c1e1e7977f1c`), `otm.ts` (`5a9141142472ec8bad04033abedd0c41ce6afcc678d355388dc1475fa36ff445`) | tool | 5 | none (context; too new for a record) | DEC-002 |
| StartLeft, <https://github.com/iriusrisk/startleft> @`e1bd3364322f95fd57e9f602cec78dfa67f2d770`, README (`58aed0da32f6516fe2713c71afdeacf6aa4c9e88d293dd387270ed274ca66bfe`) | tool | 5, 9 | new, Phase 2 (already listed by pilot) | DEC-002 |
| threatcl, <https://github.com/threatcl/threatcl> @`03b7f5e2b726d10a4718299ce987174ec155a6c6`, README (`3f4d47e30d524088c1f680e9a4dff5805aa0efd761f748b4740ad20dc92ef33d`); go-otm, <https://github.com/threatcl/go-otm> (metadata only) | tool | 5, 9 | new, Phase 2 | DEC-002 |
| IriusRisk CLI, <https://github.com/iriusrisk/iriusrisk-cli> @`a7d5aafcbb887bb180dbd5f3ee89c315218e3232`, README (`5133fb050f66b5f8942c4cd47520ad07a68702d62b1fa14eacb812afdd8f91e5`) | tool | 9 | `iriusrisk-cli` (RPT-0003 frontier) | DEC-002 |
| CWE List 4.20, <https://cwe.mitre.org/data/xml/cwec_latest.xml.zip> (`3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`, same as pilot) | dataset | 5 | `cwe` (existing) | DEC-008 |
| OWASP Threat Model Library schema v1.0.2, <https://github.com/OWASP/www-project-threat-model-library/blob/v1.0.2/threat-model.schema.json> (`428772fecfed799921e90bb7e7acf7ce7bb8e379128e43c4e7f4346a528539be`); README (`1e05fc7f33c9c967bcc85d9a18307dfda4e91801567881ba6eb2b382140f4ad1`); TD-bundled copy (`bed64d9f19495788e933fd4b0f0ed1a67142250bdb9361383b287086682b0289`) | spec | 5 | `tm-bom` (RPT-0003 frontier) | DEC-002 |
| CycloneDX TM-BOM: issue #462 <https://github.com/CycloneDX/specification/issues/462>, issue #731, PR #678 <https://github.com/CycloneDX/specification/pull/678>; `2.0-dev@7a3ab082d8e608cb31c89ba492bb8f188e63e45f` modules threat (`f33a9a819231f6c1a9c7e4b1cc8bef6f2e5f440d6834de7eb4e7b580358f2534`), requirement (`ad4d656d4437d485461958766f544e3c49c4300f4b5614302cda03bb0a5b9fb5`), control (`1cc47a2e2f0696c768382b2382ce888db22706ec4ab488b1bae04ea488cea238`), risk (`8404ed8a37a7854cf821dfde4c80404d7881be45e2e2c77bb2c72a148fb34cc3`), blueprint (`260ddf5c5ceb0aad05cf764200063fc649458d1b0c22eb55601876d0f961419c`); released `bom-1.7.schema.json` (`73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce`) | spec (draft) | 5 (TM-BOM), 7 | new, Phase 2 (coordinate with `cyclonedx-1-7`) | DEC-001, DEC-002 |
| OSCAL 1.2.3, <https://github.com/usnistgov/OSCAL/releases/tag/v1.2.3>; `oscal_complete_schema.json` (`384324105c7a817af0f65b120a963146caa0e0d55d969cf0daf60e063b87a206`), `oscal_mapping_schema.json` (`ed28b68c8e56cc7d39f0c6076a5d7da3e8100fbe25abf5bb731120bd34f8817e`), `oscal_catalog_metaschema_RESOLVED.xml` (`775f8326e3dac336be17c4f7eefa89661053230fb1e8538364186c927ee062b1`), `oscal_mapping-common_metaschema.xml` (`ca0c7ac96fc4f5606df8e96de3cff402952de7102d60735acd7502d26224606e`), `LICENSE.md` (`63407ac41abc46911bc9759fc0c19fd0ba7f66c59bb6746e51d85e2f2f3244b1`) | spec | 6 | new, Phase 2 (pending in RPT-0013) | DEC-001, DEC-002, MAP-0001 |
| NIST SP 800-53 Rev 5.2.0 in OSCAL, <https://github.com/usnistgov/oscal-content> @`78650f02ad9321bb7b817846f8fbd4f2bcd620de`, `nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json` (`01f37cf90ea99d92242c936cbfbdebcc338eef1f71454e2acac36cc56e9bc062`) | dataset | 6, 9 | new, Phase 2 | MAP-0001 |
| compliance-trestle, <https://github.com/oscal-compass/compliance-trestle> @`ecccc7ccabb5c8bdde40d7183da7fdf6d3f2fdfe`, README (`b8b2581089593d8b713fe61034735b2449ed57ca7a862e397151e8714aa5eaa0`) | tool | 6, 9 | new, Phase 2 | DEC-002 |
| GSA oscal-ssp-to-word, <https://github.com/GSA/oscal-ssp-to-word> (metadata only) | tool | 6, 9 | pending in RPT-0013 | — |
| OMG ReqIF 1.2 (formal/16-07-01), <https://www.omg.org/spec/ReqIF/1.2/About-ReqIF>; PDF <https://www.omg.org/spec/ReqIF/1.2/PDF> (`c9d4fc54a13c5bd931c1a8eb039c77494d441e98a2be889ff3e9e96c3d299a2f`, scratch only); `reqif.xsd` <https://www.omg.org/spec/ReqIF/20110401/reqif.xsd> (`9243f345540f25db3b53403da9ad9cd4744277ef01492ac3589937f533ba94c0`); `driver.xsd` (`4995bc97cf0a9b8462ca295006dd54d9a85fb820cf9fd6e134a51743fc44effd`) | spec | 6 | new, Phase 2 | DEC-002 |
| StrictDoc, <https://github.com/strictdoc-project/strictdoc> @`abf7be7daa2a25721a56980b5be15845336ea0b8` (ReqIF converters; README `9d59ba31656426e33d5bca28bcc6f2359159cc0a30e9dd1ada5e3a2ac7084de1`) | tool | 6, 9 | new, Phase 2 | DEC-002 |
| Eclipse RMF, <https://github.com/eclipse-rmf/org.eclipse.rmf> (metadata only) | tool | 6, 9 | none (context) | — |
| OMG SysML 2.0 Part 1 (formal/2026-03-02), <https://www.omg.org/spec/SysML/2.0/About-SysML>; Language PDF <https://www.omg.org/spec/SysML/2.0/Language/PDF> (`46e6c0476a6f1f34f367d57e039d56659bff75e41d2e4b3d37ca4cadea84a83a`, scratch only); `SysML.json` <https://www.omg.org/spec/SysML/20250201/SysML.json> (`bb0d8af159cf2cbe4a0df4ed6b903505a57e33d047068e5a50a7008a18d546c5`); `Systems-Library.kpar` (`df7d8b2c6e08232ca7ce123a63148949c383fcbeaeba8d89c27ceece43793a1f`); `Requirement-Derivation-Domain-Library.kpar` (`a136e72ac6afbd96ede220cfec77fd54c75242d577d3f5ab9e5278b25baee6e5`); `Metadata-Domain-Library.kpar` (`5c51cd3b21b60c89742dbba0f59f25bdbc34224d05e32975d77bb93092458b9b`) | spec | 6 | new, Phase 2 (pending in RPT-0013) | DEC-002 |
| OMG KerML 1.0 (formal/2026-03-01), <https://www.omg.org/spec/KerML/1.0/About-KerML>; PDF (`3bcc96f989bfa9d05cd28e026df3351b795fe8d494187b87bff3db7d96373697`, scratch only) | spec | 6 | new, Phase 2 | DEC-002 |
| OMG Systems Modeling API and Services 1.0 (formal/26-03-04), <https://www.omg.org/spec/SystemsModelingAPI/1.0/About-SystemsModelingAPI>; `Schema.json` (`cd1d74359d275fdb5c9182a390daffbff51c9c8c30f2a8955b2d9e4eb7589274`); `OpenAPI.json` (`17e7e8586df6c51ada09d802f48bec6dd68d141454fae05d3f45e9b9879e01ab`) | spec | 6 | new, Phase 2 | DEC-002, DEC-004 |
| SysML v2 Pilot Implementation <https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation>, API Services <https://github.com/Systems-Modeling/SysML-v2-API-Services>, Eclipse SysON <https://github.com/eclipse-syson/syson> @`b380dada415ce05155150f23cb3b74ae21cc45e4` (README `4409715b1bec5cb460241e692d95c8ec1d22f519ff61be1e7e66dbcef5532d98`) | tool | 6, 9 | none (context) | — |
| OMG SACM 2.3 (formal/23-05-08), <https://www.omg.org/spec/SACM/2.3/About-SACM>; PDF <https://www.omg.org/spec/SACM/2.3/PDF> (`8004a2ee2e3469552ae199deea22e44ec86a1d4769948bdce4782c7220de3012`, scratch only); `SACM.xml` <https://www.omg.org/spec/SACM/20220301/SACM.xml> (`4bc12020fe38018fe24d39e56ec04f2fc9190fe7cf1161d85452fda5f3fbeb1e`); 2.4 Beta 1 listing <https://www.omg.org/spec/SACM/> | spec | 6 | new, Phase 2 (pending in RPT-0013 as 2.1) | DEC-001 |
| SACM EMF implementation, <https://github.com/SystemsAssuranceGroup/SACM> @`eb9364229286168642a4ae71e53914a16efbd0f6`; `wrwei/SACM`; `nasa/CertWare` (metadata only) | tool | 6, 9 | none (context) | — |

---

## 12. Rejected claims

| what | where it came from | why rejected or corrected |
|---|---|---|
| pytm is licensed GPL-3.0 | RPT-0003 comparison table and `sources.md` row `pytm` | `LICENSE` is MIT (commit `8d73bae6` "Create LICENSE … Moved to MIT", 2018-06-27), with the CAPEC licence appended in 2020; MIT at v1.4.0, at master, and at RPT-0003's own reviewed revision `78895796`. `pyproject.toml` says MIT. |
| OTM licence is CC BY-SA 4.0 (only) | pilot.md, OTM record and Table 1 | Incomplete. The repository licence is CC-BY-SA-4.0, but `otm_schema.json`'s `$comment` says "published under the terms of the Apache License 2.0" (RPT-0003 already noted the split). Table 1 should say "spec CC BY-SA 4.0; schema file Apache-2.0". |
| threagile 1.0.0 is the current version | example model and README (`threagile_version: 1.0.0`, "Version: 1.0.0") | `docs/releases.md`: "1.0.0 Not released yet"; the latest tag is v0.9.1 (2024-07-30). Pinned to the master commit instead. |
| threagile models "comply to" `support/schema.json` | `docs/model.md` line 3 | The loader reads `custom_risk_categories`, the schema defines `individual_risk_categories`; the schema is open, so it does not check which key is used. |
| Threat Dragon v2 threats are at `cells[].threats[]` with `threatId` | `threat-dragon-v2.schema.json` | The app writes `cells[].data.threats[]` with `id` (UUID); the schema location is unused, so threats are not validated. |
| pytm 1.4.0 release date 2026-05-21 | `CHANGELOG.md` | GitHub release published 2026-07-06. Both are recorded; neither is chosen. |
| SysML 2.0 publication date September 2025 | OMG specification page | The Language PDF cover says "OMG Document Number: formal/2026-03-02, Date: March 2026". Both recorded. |
| SACM class `ArtifactAssetRelationship` | SACM 2.3 PDF §12.14 | The normative XMI (`SACM.xml`, ptc/22-03-13) names it `ArtifactAssertedRelationship`. Inconsistency recorded, not resolved. |
| SACM pinned at 2.1 | RPT-0013 `sources.md` | Superseded: 2.2 (June 2021), 2.3 (October 2023), 2.4 Beta 1 listed (September 2026). |
| "SACM ACEditor supports SACM 2.2"; OpenCert "editor for argumentation is the main basis for Assurance Case Management"; ACME "supports GSN for the argumentation part" | WebSearch summary, query on SACM tool support | Not verified against the tools (only repository existence was checked; `LuisFelipeAN/sacm-mbac-updatesite` has no description). Not used. |
| "go-otm was primarily constructed to allow hcltm to export OTM" | WebSearch summary | Not checked in go-otm; OTM export was verified in the threatcl README instead. |
| "Through OTM, a round trip keeps its meaning … a test asserting … the same findings after a round trip" | tmac README | Author's claim, not tested here; by code reading its OTM export omits the required `state` on threat instances, so its output would not validate against OTM 0.2.0. |
| Threat Dragon "v2.6.0 released in 2026" as current | RPT-0003 | Not wrong at the time; v2.6.1 (2026-05-05) and v2.6.2 (2026-05-10) have followed. |

---

## 13. Open items

1. threagile: does a model using the schema's `individual_risk_categories` key still load its manual risks in CLI mode at `74e323ed`? Needs a Go run.
2. Threat Dragon: does the app preserve unknown keys on `data.threats[]` when it saves (Table 6 row)? Needs a UI or unit-test run.
3. Threat Dragon: when will the `main` OTM importer ship, and will TD→OTM export return? `?`
4. tmac: do its converters work and does its OTM export validate? Code read only; tests not run. Its maturity (one month old, one star) makes it weak adoption evidence.
5. TM-BOM example files `tmbom-pytm-example.cdx.json` and `tmbom-otm-example.cdx.json` in Threat Dragon: produced by a tool or by hand? `?` (issue #462 comments call them "proof of concepts").
6. CycloneDX 2.0 release date `?`; whether the `2.0-dev` threat module will change before release (issue #731 open).
7. OWASP Threat Model Library `level: 2` in `project.owasp.yaml`: which OWASP maturity level that denotes `?`.
8. OSCAL adoption by FedRAMP: both `GSA/fedramp-automation` and `FedRAMP/fedramp-automation` returned 404; the current location of FedRAMP's OSCAL baselines `?`.
9. Commercial adoption of ReqIF, SysML v2 and SACM (DOORS, Polarion, Jama, Cameo, Astah, etc.): not verified `?`.
10. Eclipse RMF activity status (last push 2023-05-17) `?`.
11. SysML v2 `variation`/`variant` as a ProductFamily mechanism: noted, not examined.
12. SACM 2.4 Beta 1 changes versus 2.3: not read.
13. Normative-statement counts for Phase 4 extraction: ReqIF has 48 "Constraints" sections (heading count, not a statement count); not counted for OSCAL, SysML v2 or SACM.
14. Library records: none of the seven formats has one; all are "new, Phase 2". RPT-0003's frontier ids (`threat-dragon`, `pytm`, `threagile`, `tm-bom`, `iriusrisk-otm`) may be reused by the main session.

Remaining `?` cells in the tables: 3 (Table 4: commercial ReqIF/SysML v2/SACM tools ×2 cells, Eclipse RMF status) plus 1 in Table 6 (TD unknown-key preservation).
