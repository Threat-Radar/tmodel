---
schema: "archdoc/v1"
id: RPT-0004
title: "Product composition: SBOM and HBOM formats, tools, and the bridge to the threat model"
short_title: "Product composition"
description: "Survey of software and hardware bills of materials: formats, standards, tools, and how composition data becomes threat-model input. No design decisions are made, it only contains the evidence."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-09-28"
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
canonical_path: research/0004-product-composition/report.md
library_commit: "see library/ submodule pointer at time of merge"
informs: [DEC-001, DEC-002, DEC-007, DEC-008]
open_decisions: [DEC-001, DEC-002, DEC-008]
---

# Product composition

> **This report does not select a design.** It is evidence for the open decisions listed above. DEC-007, which it also informs, has since been accepted in ADR-0001 (radar / tmodel split).

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md). 
Axes: [`dimensions.md`](dimensions.md).

## Comparison table

**Baseline attributes.** Rows are CISA's twelve baseline attributes. The CycloneDX and SPDX columns start from CISA's own Table 1 (`cisa-framing-software-component-transparency`, §2.5), which maps CycloneDX 1.6 and SPDX 3.0; every field name was re-checked against CycloneDX 1.7 and SPDX 3.0.1 (see Tool runs in `searches.md`). Two things are ours: SPDX's `packageUrl` property (CISA's table lists purl only as an `externalIdentifier` type), and the SWID column, based on NIST IR 8060 and RFC 9393 (see 1.3). Cells marked "our reading" are closest matches, not official mappings.

| CISA attribute | CycloneDX 1.7 | SPDX 3.0.1 | SWID |
|---|---|---|---|
| SBOM Author Name | `metadata.authors` | `CreationInfo.createdBy` | the tag-creator `Entity` (required) |
| SBOM Timestamp | `metadata.timestamp` | `CreationInfo.created` | no creation time; only an optional `date` on `Evidence`, when a discovery tool collected it |
| SBOM Type | `metadata.lifecycles` | `Sbom.sbomType` | tag type: corpus before installation, primary once installed (our reading) |
| SBOM Primary Component | `metadata.component` | `Sbom.rootElement` | the tag itself (one tag, one piece of software) |
| Component Name | `components[].name` | `name` | `name` |
| Component Version String | `components[].version` | `packageVersion` | `version` (optional, default "0.0") |
| Component Supplier Name | `metadata.supplier`, `components[].supplier` | `suppliedBy` | an `Entity` with role `softwareCreator` or `distributor`; there is no supplier role (our reading) |
| Component Cryptographic Hash | `components[].hashes[]` | `verifiedUsing` | per-file hashes in `Payload` or `Evidence` |
| Component Unique Identifier | `serialNumber` + `version`, `components[].cpe`, `purl`, `swid`, `omniborId`, `swhid`, `evidence.identity` | `spdxId`, `packageUrl`, `contentIdentifier`, `externalIdentifier` | `tagId` |
| Component Relationships | `dependencies[]`, `components[].components` | `Relationship` (`dependsOn`, `contains`, `hasStaticLink`, `hasDynamicLink`, `hasProvidedDependency`, `hasOptionalDependency`) | `Link` (`requires`, `component`, `parent` and others) |
| Component License | `components[].licenses[]`, with `acknowledgement` declared or concluded | `hasDeclaredLicense` and `hasConcludedLicense` relationships | no license field; a `Link` with `rel="license"` can point to a license document, and there is a `licensor` role |
| Component Copyright Holder | `components[].copyright` | `copyrightText` | no field |

**The five questions at a glance.** A summary of sections 1.1 to 1.3:

| | CycloneDX 1.7 | SPDX 3.0.1 | SWID |
|---|---|---|---|
| Required to name a component | `type`, `name` | `spdxId`, `name`, `creationInfo` | `name`, `tagId`, tag creator |
| Every component has a global ID | no (global IDs are optional; `bom-ref` is local) | yes (`spdxId`) | yes (`tagId`) |
| Hardware | `device` type, plus a separate list of property names | only as a purpose label (`device`) | none |
| Kinds of relationship | 3 for dependency and containment, plus `pedigree` links (ancestors, descendants, variants) | 59 types across all profiles | 11 registered link types (3 about installation), plus any IANA link relation |
| Completeness | `compositions`, 10 values | `completeness` on each relationship, 3 values | none |
| "None" versus "unknown" | empty entry versus missing entry | `NoneElement` versus `NoAssertionElement` | not expressible |
| CWE | `cwes` (integers) | external reference of type `cwe` | none |
| VEX | `analysis` inside each vulnerability | relationship classes | none |

**VEX statuses.** CISA's four VEX statuses are the reference (CISA, Minimum Requirements for VEX, §2.7.1; see `sources.md`). Each SPDX class states which VEX status it represents, and SPDX's five justifications are CISA's five. CycloneDX publishes no normative mapping to these statuses (neither CISA's document nor CycloneDX's VEX page gives one), but CycloneDX's own examples for CISA's VEX use cases, which CISA's document links to, use `exploitable` for affected, `resolved` for fixed, `not_affected` for not affected and `in_triage` for under investigation (CycloneDX bom-examples, `VEX/CISA-Use-Cases/Case-1`). The CycloneDX column follows those examples; the Match column is our rating of how closely the written definitions agree. CycloneDX's nine justifications are cut differently and are not mapped.

| CISA status | SPDX 3.0.1 | CycloneDX 1.7 (per its CISA examples) | Match |
|---|---|---|---|
| `not_affected` | `VexNotAffectedVulnAssessmentRelationship` | `not_affected` | same meaning |
| `under_investigation` | `VexUnderInvestigationVulnAssessmentRelationship` | `in_triage` | same meaning |
| `fixed` | `VexFixedVulnAssessmentRelationship` | `resolved` (`resolved_with_pedigree` adds proof; our addition) | close: "has been remediated" is broader than "contain fixes" |
| `affected` | `VexAffectedVulnAssessmentRelationship` | `exploitable` | partial: "may be directly or indirectly exploitable" is not the same claim as "affects" |
| (none) | (none) | `false_positive` | no clean match; the nearest is `not_affected` |

## 1. SBOM formats (CycloneDX, SPDX, SWID)

Input to DEC-002.

**Where each format stands as a standard.** CycloneDX 1.7 is Ecma standard ECMA-424, 2nd edition (`cyclonedx-1-7`), and CycloneDX is also moving through ISO as ISO/IEC CD 27055, "CycloneDX Bill of Materials (BOM) specification", a committee draft at stage 30.99, the decision to register it for the next phase. SPDX's current ISO standard, ISO/IEC 5962:2021, covers SPDX 2.2.1 and is under revision (stage 90.92); ISO lists its replacement as ISO/IEC DIS 5962, "SPDX® Specification V3.0", a draft international standard at stage 40.60. SWID is ISO/IEC 19770-2:2015 (1.3). Two identifiers used below are standards too: SWHID is ISO/IEC 18670:2025 ("SWHID Specification V1.2"), and purl, already ECMA-427, is ISO/IEC CD 27056, also at stage 30.99 (ISO Open Data, `iso_deliverables_metadata`, checked 2026-09-30; stage codes per ISO Guide 69).

### 1.1 CycloneDX 1.7 (`cyclonedx-1-7`)

**Naming a component.** A component needs only a `type` and a `name`; every identifier is optional. The table lists the fields the spec itself treats as identity fields (the allowed values of `evidence.identity.field`), plus the local `bom-ref`.

| Field | What it identifies | Kind |
|---|---|---|
| `name`, `version` | the component's name and version | assigned name |
| `group` | the maker or namespace, e.g. `org.apache` | assigned name |
| `purl` | a package in a package ecosystem, e.g. `pkg:apk/alpine/zlib@1.3.2-r0` | assigned name |
| `cpe` | a product, in the CPE naming scheme the NVD uses | assigned name |
| `swid` | an ISO/IEC 19770-2 software identification (SWID) tag | assigned name |
| `hashes` | the exact bytes | computed from bytes |
| `omniborId` | the exact bytes (an OmniBOR artifact ID) | computed from bytes |
| `swhid` | files, directories or commits, via a Software Heritage ID | computed from bytes |
| `bom-ref` | a component within this one SBOM; another file can reach it only through a BOM-Link | local |

Two things stand out. First, the spec words five of the six global identifiers as claims: `purl`, `cpe`, `swid`, `omniborId` and `swhid` each "asserts the identity of the component", and an optional `evidence.identity` field can back the claim up (`cyclonedx-1-7`). Second, only three identifiers are computed from the bytes (`hashes`, `omniborId`, `swhid`; see `cisa-framing-software-component-transparency`, §2.2.2.4); the rest are assigned names, which can be wrong or guessed.

Even `hashes` has limits: the spec does not say which bytes are hashed, so two SBOMs of the same artifact can carry different hashes, and the allowed algorithms still include MD5 and SHA-1, which CISA notes "will be formally discontinued in 2030" (`cisa-framing-software-component-transparency`, §2.2.2.5). All of this matches the names-versus-bytes gap the library's SBOM topic describes (library topic `sbom`), and it matters for DEC-002 (which formats tmodel imports).

**Hardware and firmware.** CycloneDX can describe hardware, but little of it is built into the spec. `device` is the only component type described as hardware ("a hardware device such as a processor or chip-set"); `firmware` and `device-driver` are each "a special type of software", and `platform` is a runtime environment (`cyclonedx-1-7`). The `device` description adds one rule: a device containing firmware "SHOULD include a component for the physical hardware itself and another component of type 'firmware' or 'operating-system'", and nested `components` can show an assembly, "similar to system → subsystem → parts assembly in physical supply chains". There are no hardware-only fields: details such as a serial number, MAC address or location on the board go in the generic `properties` field, which the spec describes as a place for "data not officially supported in the standard", under names from CycloneDX's separate property taxonomy, such as `cdx:device:serialNumber` (see `sources.md`). Because those names live outside the schema, a schema check cannot catch a missing or misspelled one, which matters for DEC-001 (tmodel's core object model) if hardware becomes part of it.

**Dependencies.** CycloneDX separates three kinds of structural relationship between components (`cyclonedx-1-7`), shown below; a component's history, such as what it was forked or derived from, is recorded separately in `pedigree`.

| Relationship | Field | Meaning |
|---|---|---|
| depends on | `dependencies[].dependsOn` | the component's direct dependencies; indirect ones come from following the chain |
| provides | `dependencies[].provides` | the component implements a standard or algorithm, which "does not imply that the implementation is in use" |
| contains | nested `components` | an assembly, "similar to system → subsystem → parts assembly"; "This is not a dependency tree" |

Three details matter for anyone reading the graph. First, a missing entry should be read as "unknown", not "none": components with no dependencies "must be declared as empty elements", while components left out of the graph "may have unknown dependencies", to be treated as "opaque and not an indicator of an object being dependency-free". Second, `dependsOn` and `provides` point by `bom-ref` "in the same BOM document"; unlike a vulnerability's `affects`, they cannot use a BOM-Link into another SBOM, so a dependency cannot cross files; separate SBOMs can only be connected in other ways, such as an external reference of type `bom` or matching components by their global IDs. Third, `scope` says whether a component is reachable at runtime (`required`, `optional` or `excluded`); when it is missing, consumers "SHOULD" assume `required`, and a component that is installed but blocked from being called still counts as `required`. These typed relations bear on DEC-001 (tmodel's core object model and its typed relations), and the same-file limit bears on DEC-002 (which formats tmodel imports).

**Completeness.** A separate top-level `compositions` list says how complete the relationships are (`cyclonedx-1-7`). Each entry names what it covers by reference (nested parts in `assemblies`, dependency links in `dependencies`, or the list of `vulnerabilities`) and gives one required `aggregate` value. The table aligns the ten values with CISA's four completeness levels (`cisa-framing-software-component-transparency`, §2.2.2.6.4); the alignment is ours, based on the definitions, not an official crosswalk:

| CISA | CycloneDX `aggregate` |
|---|---|
| Known | `complete` |
| Partial | `incomplete`, or one of six narrower variants such as `incomplete_third_party_only` |
| Unknown (the CISA default) | `unknown` ("a 'best-effort'... but the completeness is inconclusive") or `not_specified` (the CycloneDX default) |
| None | no value of its own; an empty `dependsOn` entry, as described under Dependencies |

Two things stand out. First, CycloneDX splits CISA's Unknown in two: `unknown` usually signals a best-effort attempt that was inconclusive, while `not_specified` means no one said anything, and leaving `compositions` out entirely makes no completeness claim at all. Second, both standards limit the claim to direct relationships: CycloneDX references "do not cascade to transitive dependencies", matching CISA's rule that a "Known" component can have upstream components that are only "Partial" or "Unknown". So an SBOM can be complete at the top and still have gaps further down, and while it can state that a list is complete, it cannot prove that a component is absent (library topic `sbom`). This matters for DEC-001: a model that reads an SBOM as a full list will draw wrong conclusions whenever completeness is unknown or unstated.

**Vulnerabilities and weaknesses.** A top-level `vulnerabilities` list records "vulnerabilities identified in components or services" (`cyclonedx-1-7`). Each entry points at what it hits through `affects`, lists the weakness types behind it in `cwes`, and can carry an `analysis`: the author's answer to "does this actually affect us?", known as VEX (VEX itself is in scope for #9). The analysis has a `state` (for example `exploitable`, `not_affected` or `false_positive`), a `justification` (for example `code_not_reachable` or `protected_by_mitigating_control`), a `response` (for example `update` or `will_not_fix`), a free-text `detail`, and timestamps for when it was first issued and last updated.

Three things stand out. First, `cwes` is the only CWE field, so a component links to a weakness only through a vulnerability entry, and each CWE is a bare integer ("For example 399") rather than a string like "CWE-399". Second, unlike `dependsOn`, `affects` accepts a BOM-Link, so a vulnerability report can live in a separate file and still point into a product's SBOM. Third, the analysis is again a claim: `not_affected` "should" come with a justification, but the schema does not require one. Several justifications (`code_not_reachable`, `requires_configuration`, `protected_at_perimeter`, `protected_by_mitigating_control`) are threat-model conclusions in their own right, which makes this a direct link between an SBOM and tmodel's model (DEC-001) and its CWE/NVD integration (DEC-008).

**Takeaway:** CycloneDX 1.7 can express identity, hardware, three kinds of relationship, completeness and vulnerability status, but almost all of it is optional, and most of it is a claim by whoever wrote the SBOM: identifiers are asserted, a missing dependency entry means "unknown", completeness can simply be left unstated, hardware details live outside the schema, and exploitability is the author's assessment. What a real SBOM actually contains depends on the tool that wrote it (section 3).

### 1.2 SPDX 3.0.1 (`spdx-3-0-1`)

**Naming a component.** In SPDX a software package is a `Package` element, and it needs only three things: an `spdxId`, a `name` and a `creationInfo`; even `packageVersion` is optional (`spdx-3-0-1`). The `spdxId` is the big difference from CycloneDX: it is a URI that "uniquely identifies an Element", and references to it "may be internal or external": an `spdxId` is global in itself, while a CycloneDX `bom-ref` is unique only within its file and needs a BOM-Link to be reached from another. The other identifiers live in four places:

| Where | What goes there | Kind |
|---|---|---|
| `packageUrl` | the package's purl | assigned name |
| `externalIdentifier` | an ID typed from a fixed list: `cpe22`, `cpe23`, `packageUrl`, `swid`, `gitoid`, `swhid`, plus types for other kinds of element such as `cve` and `email` | mostly assigned names |
| `contentIdentifier` | "a canonical, unique, immutable identifier of the content": a `gitoid` or `swhid` | computed from bytes |
| `verifiedUsing` | a `Hash` (an `algorithm` plus a `hashValue`) or another integrity method | computed from bytes |

Three things stand out. First, SPDX treats content-based IDs as a way to verify, not just to name: `ContentIdentifier` and `Hash` are both kinds of `IntegrityMethod`, "an independently reproducible mechanism that permits verification", while CycloneDX words `omniborId` and `swhid` as identity claims. Second, one ID can go in two places: a purl fits both `packageUrl` and an `externalIdentifier` of type `packageUrl`, and neither entry says which to use, whereas gitoid gets an explicit rule (a gitoid of the artifact goes in `contentIdentifier`, one of its input manifest in `externalIdentifier`). Third, the same name points to different standards: SPDX's `swid` is a CoSWID tag (RFC 9393), the CBOR-based concise form of SWID, while CycloneDX's `swid` holds the fields of an XML ISO/IEC 19770-2 SWID tag; the two are closely aligned but encoded differently (see 1.3). For DEC-002, a tool importing both formats has to read purls from two SPDX places and reconcile SPDX's global `spdxId` with CycloneDX's file-local `bom-ref`.

The hash lists differ too. SPDX defines a hash algorithm as "a one-way function", yet its list includes the Adler-32 "checksum", MD2 and MD4 (both moved to Historic status by the IETF in RFC 6149 and RFC 6150), and Kyber and Dilithium, which NIST standardizes as a key-encapsulation mechanism and a digital signature scheme rather than as hashes (FIPS 203, FIPS 204). Ten SPDX values have no match in CycloneDX's list (`adler32`, `md2`, `md4`, `md6`, `sha224`, `sha3_224`, the three post-quantum values and `other`), and CycloneDX's Streebog can only become SPDX's generic `other`, so converting between the formats can lose a hash or its algorithm name.

**Hardware and firmware.** SPDX 3.0.1 has no hardware profile or hardware element: none of its ten profiles covers hardware, so a chip can only be described as a software artifact, such as a `Package`, whose `primaryPurpose` is `device` ("The Element refers to a chipset, processor, or electronic board") (`spdx-3-0-1`). `firmware` and `deviceDriver` are purposes too, and the spec calls a purpose "a reasonable estimate of the most likely usage of the Element", "intrinsic to how the Element is being used rather than the content of the Element", so `device` is a usage label, not a hardware type. There are no hardware fields either: the model has nothing for a serial number, MAC address or manufacturer, and defines no hardware property names of its own, so such details would have to go in an `extension`, for example a `CdxPropertiesExtension`, which the spec says is intended to be compatible with CycloneDX properties and so could carry CycloneDX's `cdx:device` names. Assemblies can be written with the generic `contains` relationship ("The `from` Element contains each `to` Element"), but unlike CycloneDX's `device`, SPDX's `device` and `firmware` entries give no rule for separating a device from its firmware. For hardware, SPDX 3.0.1 offers even less than CycloneDX (DEC-001).

**Dependencies.** In SPDX a relationship is an element of its own (`Relationship` is a subclass of `Element`, so it has its own `spdxId`), with one `from`, one or more `to`, and a required `relationshipType` chosen from 59 values (`spdx-3-0-1`). The dependency-related types are finer-grained than CycloneDX's single `dependsOn`:

| SPDX type | Meaning |
|---|---|
| `dependsOn` | "depends on each `to` Element" |
| `hasStaticLink`, `hasDynamicLink` | links the `to` element in statically or dynamically |
| `hasOptionalDependency` | "optionally depends on" |
| `hasProvidedDependency` | the dependency "is not in the distributed artifact, but assumed to be provided" |
| `hasPrerequisite` | "has a prerequisite on" |
| `contains`, `hasOptionalComponent` | containment, like CycloneDX's nested `components` |

Three things stand out. First, "none" and "no claim" are explicit: to assert that no such relationships exist, `to` holds the special `NoneElement`, and to make no assertion it holds `NoAssertionElement`, where CycloneDX relies on an empty `dependsOn` versus a missing entry. Second, because every element has a global `spdxId`, a relationship's `from` and `to` can name elements in other documents, which CycloneDX's `dependsOn` cannot. Third, `LifecycleScopedRelationship` adds a `scope` of `design`, `development`, `build`, `test`, `runtime` or `other`, which says when a relationship applies; CycloneDX's `scope` (`required`, `optional`, `excluded`) says instead whether a component is reachable at runtime, so the two "scopes" do not map one to one. The richer relationship vocabulary bears on DEC-001, and the cross-document links on DEC-002.

**Completeness.** SPDX states completeness on each relationship rather than in a separate list: `completeness` is an optional property of `Relationship` with three values, `complete` ("known to be exhaustive"), `incomplete` ("known not to be exhaustive") and `noAssertion` (`spdx-3-0-1`). Because it sits on the relationship itself, it can be stated for any of the 59 relationship types, not only dependencies. Compared with CISA's four levels (`cisa-framing-software-component-transparency`, §2.2.2.6.4; as in 1.1, the alignment is ours, based on the definitions):

| CISA | SPDX 3.0.1 | CycloneDX 1.7 (see 1.1) |
|---|---|---|
| Known | `complete` | `complete` |
| Partial | `incomplete` | `incomplete` and six narrower variants |
| Unknown | `noAssertion`, or `NoAssertionElement` in `to` | `unknown` or `not_specified` |
| None | `NoneElement` in `to` | an empty `dependsOn` entry |

Two things stand out. First, SPDX has a named value for "none" (`NoneElement`) that works for any relationship type, but it merges what CycloneDX splits: `NoAssertionElement` covers a creator who "attempted to but cannot reach a reasonable objective determination", one who "made no attempt", and one who "intentionally provided no information", so a reader cannot tell a failed search from no search. Second, `completeness` is optional, neither its property page nor its value list states a default, and unlike CycloneDX, SPDX's `dependsOn` does not say whether it lists only direct dependencies, so "complete" does not say how deep the list goes. As in CycloneDX, "none" and "complete" are the author's assertions, not proof (DEC-001).

**Vulnerabilities and weaknesses.** In SPDX a vulnerability is an element of its own (`Vulnerability`, a kind of `Artifact`), named like anything else through `externalIdentifier`, for example of type `cve` (`spdx-3-0-1`). Everything else is a relationship: `hasAssociatedVulnerability` links "a `from` Artifact with each `to` Vulnerability"; other types record who found, reported, published or republished it ("i.e. NVD"); and each assessment is a relationship class of its own, running from the vulnerability to the products it concerns:

| Assessment | SPDX 3.0.1 relationship class |
|---|---|
| VEX affected | `VexAffectedVulnAssessmentRelationship` (requires an `actionStatement`) |
| VEX not affected | `VexNotAffectedVulnAssessmentRelationship` (optional `justificationType`, one of five) |
| VEX fixed | `VexFixedVulnAssessmentRelationship` |
| VEX under investigation | `VexUnderInvestigationVulnAssessmentRelationship` |
| Severity and priority | CVSS v2, v3 and v4, EPSS, exploit catalog (`kev` or `other`), SSVC |

Three things stand out. First, SPDX supports CWEs but has no dedicated CWE field: a weakness is attached as an external reference (`externalRef`) of type `cwe` ("a reference to a source of software flaw defined within the official CWE List"), whose value goes in a free-text `locator`, where CycloneDX has a dedicated `cwes` list of integers. Second, the VEX vocabularies differ: SPDX has four statuses and five justifications (`componentNotPresent`, `vulnerableCodeNotPresent`, `vulnerableCodeNotInExecutePath`, `vulnerableCodeCannotBeControlledByAdversary`, `inlineMitigationsAlreadyExist`), CycloneDX six states and nine justifications, and neither specification maps its values onto the other's. SPDX's four statuses and five justifications match those in CISA's Minimum Requirements for VEX (§2.7.1); the comparison table shows how CycloneDX's own examples line its states up with them. Third, SPDX is stricter in one place and not in another: an "affected" statement must carry an `actionStatement` (CycloneDX's `response` is only "strongly encouraged", and only when a vulnerability is exploitable), but for "not affected" the spec says one of `impactStatement` or `justificationType` "MUST be defined" while giving both a cardinality of 0..1, "making them optional". SPDX also covers EPSS and exploit catalogs such as KEV, which CycloneDX 1.7 has no field for. This bears on DEC-008 (CWE/NVD integration) and, since VEX statuses become typed links between vulnerabilities and products, on DEC-001.

**Takeaway:** SPDX 3.0.1 is built as a graph: every package, vulnerability and relationship is an element with a global `spdxId`, so it can link across documents, and it offers far more relationship types (59) and more kinds of vulnerability assessment (adding EPSS and exploit catalogs) than CycloneDX. It is weaker where CycloneDX is strong: hardware is only a purpose label, a CWE has no dedicated field (only an external-reference type), and completeness has three values with no stated default. As with CycloneDX, almost everything beyond an ID, a name and creation information is optional and asserted by the author, and some rules the text states (a "MUST" that a not-affected statement give a justification or an impact statement) are not enforced by the model.

### 1.3 SWID (ISO/IEC 19770-2)

The SWID standard itself, ISO/IEC 19770-2:2015, is paywalled and was not read for this report. ISO's own metadata lists this second edition, published 2015-09-30, as current: nothing replaces it, and its stage code 90.60 marks the close of a review whose outcome the metadata does not show (ISO Open Data, `iso_deliverables_metadata`, checked 2026-09-30; stage codes per ISO Guide 69). This section relies on two public sources: NIST IR 8060, NIST's guidelines for creating interoperable SWID tags, which reports the standard's requirements for each tag element, and RFC 9393, which defines Concise SWID (CoSWID) tags as a CBOR-based "more concise representation of SWID information" whose data definition "is aligned with" the standard's XML schema. Where only CoSWID is described, the text says so.

SWID also has a different shape from the other two formats. A tag describes one piece of software, and a primary tag "is intended to be installed on an endpoint along with the corresponding software component" (RFC 9393 §1.1), so an inventory is a collection of tags rather than one document. There are four tag types: primary, patch, corpus (software before installation) and supplemental (extra information about another tag).

**Naming a component.** The standard requires a `name` and a `tagId`, and "every tag contains an <Entity> element identifying the tag creator"; `version` is optional and "defaults to "0.0"", although NIST's guidelines require it in primary and corpus tags (NIST IR 8060 §3.1.1, §3.1.2). The `tagId` is a built-in global identifier: RFC 9393 says it "MUST be globally unique" and "serves as the global key for matching and lookups", written for example as a UUID or as a DNS domain name followed by "/" and a string (§2.3). There is no purl or CPE field (neither word appears in RFC 9393); NIST IR 8060 instead describes generating a CPE name from a tag's metadata (§5.2.4). Content enters through file lists: in an authoritative tag, "Every <File> element within a <Payload> element MUST include a hash value" (GEN-16, §4.6.1), where an authoritative tag creator is the software's creator or a party that aggregates, distributes or licenses it on the creator's behalf (§4.2). CoSWID accepts only hash algorithms from IANA's "Named Information Hash Algorithm Registry": "other hash algorithms MUST NOT be used" (RFC 9393 §2.9.1).

**Hardware and firmware.** SWID covers software only: neither "hardware" nor "firmware" appears in RFC 9393, the four tag types all describe software, and NIST IR 8060 mentions hardware only when defining which files count as executable (§5.2.3). A device cannot be described.

**Dependencies.** Relationships are `link` entries with an `href` and a `rel`, and RFC 9393 says its rel values "match the link rel values defined in the ISO/IEC 19770-2:2015 specification" (§2.7, §4.4). The dependency-like links are about installation rather than running: `requires` "references a prerequisite for installing this software", and a link's optional `use` (`optional`, `required` or `recommended`, each quoted "From [SWID]") says whether the linked software "has to be installed before installing" this one (§2.7, §4.5). The other values cover bundles (`component`, `parent`), history (`ancestor`, `patches`, `supersedes`), installers (`installationmedia`, `packageinstaller`), `feature`, `see-also` and `supplemental`, and `rel` may also be any name from IANA's "Link Relation Types" registry (§2.7); none of the registered values describes using another component at runtime. Because an `href` can name another tag as `swid:` plus its tag ID, links cross tags by design.

**Completeness.** Neither source describes a completeness field. RFC 9393 warns that "any collection of CoSWID tags cannot automatically be assumed to represent either a complete or fully accurate representation of the software inventory of the endpoint", partly because "not all software products automatically install CoSWID tags" (§9). Within a tag, NIST's guidance is that `<Payload>` and `<Evidence>` "SHOULD list every file comprising the product described by the tag", with executable files as the minimum (NIST IR 8060 §5.2.3, PRI-8).

**Vulnerabilities and weaknesses.** SWID carries no vulnerability data: CoSWID's data definition has no field for CVEs, CWEs or VEX. Tags are meant to be matched against vulnerability information instead. RFC 9393 lists "Vulnerability Assessment, which requires a semantic link between standardized vulnerability descriptions and software components" among the uses of SWID tags (§1), a `link` can point to a "vulnerability database association" (§2.3), and NIST IR 8060 describes forming CPE names from tags so that bulletins naming products by CPE can be matched to endpoints (§6.1.3).

**Takeaway:** SWID is an identification and inventory format rather than a composition graph: each tag names one piece of software with a globally unique `tagId` and lists its files with hashes, its dependency-like links are about installation, and it has nothing for hardware, completeness or vulnerabilities. Its most useful idea here is the explicit difference between authoritative tags, made by the software's creator or its distributors, and non-authoritative tags, typically made by discovery tools (NIST IR 8060 §4.2), which bears on how much an imported identity can be trusted (DEC-002). The standard itself was not read (paywalled).

## 2. HBOM (hardware and firmware)

Input to DEC-001.

**The reference.** The main public guidance is CISA's *A Hardware Bill of Materials (HBOM) Framework for Supply Chain Risk Management* (September 2023), written by the HBOM working group of the ICT Supply Chain Risk Management Task Force "to create a consistent, repeatable way for vendors to communicate with purchasers of hardware components" (§1). NTIA's SBOM minimum elements leave hardware out of scope (`ntia-sbom-minimum-elements`, §III). The framework sorts HBOM use cases into three categories (Appendix A, Table 1): Compliance, for example laws that may prohibit certain components; Security, meaning "exposure to known vulnerabilities and/or high susceptibility to untrusted entities/geolocations"; and Availability, the effect of world events and of too little supplier diversity.

**What an HBOM records that an SBOM does not.** The framework's taxonomy has 47 fields in seven categories: header information, finished-good product details, entity names, entity locations, component part information, component part details and production details (Appendix C.1 to C.7). Most describe the physical supply chain rather than code: the contract manufacturer and the assembly-and-test supplier; the locations of the product's supplier, its manufacturers, the component manufacturer and the assembly-and-test site, with coordinates and location codes; the manufacturer's part number; the semiconductor technology node; the share of a part sourced from a supplier; lead times, quantities and date codes. For semiconductors it asks for the supplier and the fab or foundry "as separate data points" (Appendix B.1.3). Parts are typed only loosely: `COMP_TYPE` is "hardware", "software" or "service", and `COMP_PART_TYPE` is a free-text "Component category (e.g., semiconductor, antenna, etc.)", so the parts issue #8 names, such as buses and compute cores, have no field of their own. Firmware is covered thinly: the framework records "the provider of the firmware" but "stops short of proposing a framework for examining the provenance and other attributes of that firmware" (§1.3).

**How it fits the SBOM formats.** The framework defines fields and a nesting layout rather than a file format, and its layout example "is suggested for spreadsheet HBOMs": each assembly gets its own HBOM, joined to its parent through part-level information (Appendix B.1.1). It maps its fields to CycloneDX and SPDX "where possible", but of the 47 fields, 37 list no CycloneDX equivalent and 36 no SPDX equivalent (the SPDX mappings use older SPDX 2.x field numbers). Fields such as country of origin cannot be mapped one to one, and where no field exists "the developer should create a user-defined field" (Appendix B.2). The framework calls this area immature, since "further work will be required to achieve the necessary maturity for true interoperability" (§1.2), and it leaves SBOM information out of scope while recommending future work so it "can merge with emerging SBOM frameworks" (§1.3).

**What the formats offer today.** Of the three formats in section 1, only CycloneDX has hardware support: a `device` type, a rule for separating a device from its firmware, nesting for assemblies, and hardware details as `cdx:device` properties outside the schema (1.1). CycloneDX presents HBOM as covering "processors, embedded systems, IoT devices, and industrial control systems" (CycloneDX HBOM capability page). Its property list covers a few of the framework's fields, such as quantities (`cdx:device:quantity`) and lot or date codes (`cdx:device:lotNumber`, `cdx:device:prodTimestamp`), and adds details the framework does not ask for, such as serial numbers, board locations and GS1 product codes. CISA's mapping lists no CycloneDX field for locations, but in CycloneDX 1.7 an organization, such as a component's `manufacturer` or `supplier`, can carry a postal `address` with a `country`, which covers part of the location fields; coordinates, location codes, technology node, sourcing share and lead times still have no field. SPDX 3.0.1 has only a `device` purpose label and no address field, and SWID has nothing for hardware (1.2, 1.3).

**An ISO hardware tag.** ISO also publishes a hardware counterpart to SWID: ISO/IEC 19770-6:2024, *Hardware identification tag*, published 2024-01-26. According to ISO's own metadata, it "provides specifications for a transport format" for "hardware identification (HWID) data", which it calls "a HWID tag, just as ISO/IEC 19770-2 refers to software identification (SWID) tags", and it "deals only with hardware device or component identification" (ISO Open Data, `iso_deliverables_metadata`). The standard is paywalled and was not read, so this report cannot say which fields it defines or whether any tool produces it.

**Takeaway:** An HBOM is mostly supply-chain data (who made a part, where, and how concentrated its sources are) rather than vulnerability data, and the main public framework for it is a field taxonomy built around spreadsheets whose fields mostly have no home in CycloneDX or SPDX; ISO's hardware identification tag (ISO/IEC 19770-6:2024) exists but was not read. For tmodel, hardware would need object types or attributes of its own (DEC-001), and importing HBOM data today would mean CycloneDX `device` components plus user-defined properties, the route the framework itself points to (DEC-002). Firmware is where hardware links back to software and its vulnerabilities.

## 3. Tools (Syft, Grype, Trivy, Dependency-Track)

Input to DEC-002, and to the radar-to-tmodel data contract set by ADR-0001 (DEC-007).

We ran the three command-line tools on two inputs: the `alpine:latest` container image (2026-09-28) and the tradar source repository (2026-09-30), with Syft 1.52.0, Grype 0.119.0 and Trivy 0.74.0 (Tool runs in `searches.md`). Two inputs are a small sample, so the counts below describe these runs, not the tools in general.

**Syft produces the SBOM.** It writes CycloneDX (JSON or XML), SPDX 2.3 or 2.2, and its own JSON format, but not SPDX 3 (`syft scan --help`), so the SPDX 3.0.1 model in 1.2 cannot come from Syft today. In the CycloneDX output of both runs every package got a purl and a CPE, and no package got a hash or a supplier (Syft's SPDX output of tradar does name a supplier for its 9 GitHub Actions); the Alpine packages got licenses and tradar's did not. File components got hashes (SHA-1 and SHA-256 for all 78 Alpine files). Both SBOMs have dependency links (24 edges for Alpine, 104 for tradar) but no `compositions`, `lifecycles`, `formulation`, `scope` or `evidence`. The CPEs are mostly guesses. Syft produced 81 candidate CPEs for the 16 Alpine packages and 996 for tradar's 76; of tradar's, 10 came from NVD's CPE dictionary and 986 were generated (Syft JSON output), and Syft's documentation lists no dictionary lookups for Alpine packages, only heuristic generation. In 15 of the 16 Alpine CPEs in the standard `cpe` field, the vendor and product are the same name. The CycloneDX output puts one CPE per package in that field and the rest (65 for Alpine, 920 for tradar) in Syft's own `syft:cpe23` properties, while the SPDX output of tradar lists all 996 as `cpe23Type` references, so the same scan carries different identity data depending on the output format. From requirements files, Syft listed only exact pins (`PyGithub==2.1.1`, `python-dotenv==1.0.0`) and skipped ranges such as `typer>=0.9.0`; most of tradar's packages (65 of 76) came from `uv.lock`.

**Grype matches packages to vulnerabilities.** How it matched depended on the package type. The four Alpine matches came from Grype's `apk-matcher` but were CPE matches against NVD data (namespace `nvd:cpe`), with version ranges from Grype's NVD data (one of which NVD's own record does not contain; section 5) and no fix state; the busybox CVE was counted three times, once for each binary package built from busybox (`busybox`, `busybox-binsh`, `ssl_client`). The tradar matches were exact package matches against GitHub advisories: 13 from the `python-matcher`, and 2 from the `stock-matcher` for one GitHub Action used in two workflow files. Grype's JSON output carries CWEs (both Alpine CVEs and all 15 tradar matches), but its CycloneDX output of the Alpine run left `cwes` empty.

**Trivy.** On Syft's Alpine SBOM, Trivy reported no vulnerabilities and warned "Third-party SBOM may lead to inaccurate vulnerability detection". On tradar, `trivy fs` reported 12 CVEs, all in `uv.lock`, and `trivy sbom` on Syft's SBOM reported 13; the extra one is `python-dotenv@1.0.0` from `docker/requirements-docker.txt`, which Trivy's own scan did not report. All of Trivy's findings carry CWE IDs and come from GitHub advisory data (`ghsa`).

**The tools disagree on the same input.** For tradar's Python packages the scanners agree on the same SBOM: every CVE `trivy sbom` reported is among Grype's (by CVE alias), and Grype adds only the GitHub Action advisory. For Alpine they do not: Grype reported two CVEs from NVD CPE matching and Trivy none. Section 5 looks at why the matching method, more than the SBOM, decides the result.

**Dependency-Track (not run; from its documentation).** Dependency-Track is a server that tracks SBOMs across many projects; its current release is 5.1.1 (2026-09-20), and version 4 "will reach end-of-life in December 2026" (Dependency-Track README, 5.1.1). It accepts only one SBOM format, "CycloneDX is the only format supported for uploading SBOMs to Dependency-Track", including CycloneDX 1.7; it removed its old SPDX support in 4.3.0, and SPDX 3 is an open issue marked "on hold" (#1746). Its internal analyzer "is applicable to all components with valid CPEs or PURLs", but "Matching against data from the NVD requires components to have a valid CPE", and its OSS Index, Snyk and Trivy analyzers use purl matching only. It keeps each vulnerability's CWEs, exports findings as CycloneDX VEX or VDR and "imports CycloneDX VEX documents", and lists hardware and firmware among its component types, noting that such "Non-application dependencies such as operating systems, hardware, firmware, etc, should have valid CPEs" to be analyzed.

**GUAC (not run; from its documentation).** GUAC (OpenSSF, v1.1.0, 2026-03-13) is not a scanner but a graph built from many documents: its README lists CycloneDX, SPDX, SLSA, in-toto, DSSE, OpenVEX, CSAF, OSV, deps.dev and OpenSSF Scorecard as inputs. "We represent a package by a pURL", and for artifacts "we separate the algorithm used for the checksum from the digest value" (GUAC GraphQL docs); vulnerabilities come from an OSV certifier that works by "Package identification through PURL". Its SPDX parser reads SPDX 2.x (it imports `spdx/v2` from spdx/tools-golang), SPDX 3.0 is an open long-term issue (#1850), and its default storage is "a non-persistent in-memory backend". It describes itself as "under active development" and an OpenSSF incubating project (README).

**Takeaway:** No single tool covers the whole chain. Syft writes the SBOM, with mostly guessed CPEs and without SPDX 3; Grype and Trivy match it against different data and can disagree on the same input; Dependency-Track reads only CycloneDX; and GUAC reads SPDX only in version 2. So an SPDX 3.0.1 import path (DEC-002) has no support in Syft, Dependency-Track or GUAC today, and radar (tradar), which ADR-0001 makes tmodel's source of composition data, inherits the choices its Syft and Grype defaults make.

## 4. How tradar uses these today

Input to the radar-to-tmodel data contract. ADR-0001 accepted DEC-007 on 2026-09-30: tradar becomes "radar", the composition and finding tool whose output tmodel consumes, and "the interface is the composition→model-input mapping surveyed in RPT-0004 (#8)".

This section describes `tradar` at commit `26d9c76` (2026-09-10). Paths are relative to its `threat_radar/` package.

**Tools and formats.** tradar runs Syft and Grype as command-line programs: `syft scan <target> -o <format> --scope <scope>` (`core/syft_integration.py:109-123`), with CycloneDX JSON as the default format (`cli/sbom.py:95`), and `grype <target> -o json` (`core/grype_integration.py:172`). It reads SBOMs back only as JSON (`utils/sbom_utils.py`, `load_sbom`), and it never matches components to vulnerabilities itself: `cve scan-sbom` hands the SBOM file to Grype as `sbom:<file>` (`core/grype_integration.py:282`).

**What it keeps.** From SBOM components, tradar's helpers read name, version and type; purl and licenses are used only for display (`sbom components --details`), a CSV export and license statistics (`utils/sbom_utils.py`); an SBOM converter that also parses the purl (`core/sbom_package_converter.py`) is only called from `analyze_container_with_sbom`, which nothing calls. Its code never reads an SBOM's `dependencies`, `compositions`, `serialNumber`, `hashes` or `supplier` (none of these keys appears outside its environment-config code). From Grype's JSON it keeps the vulnerability ID, severity, first fix version, description, URLs, data source, namespace, one CVSS base score (the highest in the first related record that has scores), the package's name, version, type and location, and Grype's `source` and `descriptor` blocks (`core/grype_integration.py:335-430`). It does not read how Grype made each match (`matchDetails`), related CVE IDs, the fix state, the package's purl or CPEs, or any CWE.

**What reaches the graph.** The graph is a NetworkX directed graph saved as GraphML (`graph/graph_client.py:107, 329`). `graph build` creates it from Grype results, not from an SBOM: for each vulnerability it adds a vulnerability node and, if missing, a package node with only `name`, `version` and `ecosystem` (`graph/builders.py:166-186`). Only vulnerable packages, plus one node for each fix version (marked `is_fix`, `graph/builders.py:211-237`), therefore become package nodes, and purl, CPE, licenses, hashes, supplier and the SBOM's dependency links never reach the graph. `graph build` accepts raw Grype JSON or tradar's own scan files that carry a `target` key (`cli/graph.py:65-68`); the file saved by `cve scan-sbom` carries `sbom_file` instead (`cli/cve.py:321`) and is rejected as an "Unsupported scan result format" (`cli/graph.py:125`). The project's own documentation also lists graph edges, such as `RUNS_ON` and `SCANNED_BY`, that `graph build` does not create (`CLAUDE.md:2542-2543`).

**CWE, NVD and the rest.** The current code has no CWE handling and calls no vulnerability API; a case-insensitive search for "cwe" across its code, tests and docs finds nothing. The git history shows an NVD client that extracted CWE IDs, added on 2025-10-05 (`629d92a`) and removed on 2025-10-09 (`3e26837`, "Remove manual SBOM package converter and replace with Grype integration"). Nothing in the code handles hardware, VEX or completeness. The nearest thing to build identity is a local Docker image ID, which could label a container node (`graph/builders.py:100`), but both CLI paths that build graphs call `build_from_scan` without a container (`cli/graph.py:152`, `cli/env.py:247`). tradar's saved scan files also keep Grype's `source` block, which for an image includes its `manifestDigest` (`cli/cve.py:151, 337, 480`), but no code reads that digest.

**Takeaway:** tradar is a thin wrapper around Syft and Grype whose graph keeps only the name, version and ecosystem of vulnerable packages. Under ADR-0001, tmodel consumes radar's output instead of re-implementing scanning, so what radar's pipeline now drops, such as purl and CPE, dependency links and CWEs, is what the composition-to-model-input contract would have to add if tmodel needs it; Syft's and Grype's JSON outputs already contain all of it (see section 3).

## 5. The bridge: components to CVEs and CWEs

Input to DEC-001 and DEC-008.

**Two ways to name affected software.** Vulnerability data names affected software in one of two ways. NVD writes "configurations" of CPE match criteria for each CVE it has analyzed: for CVE-2022-37434 in zlib, one criterion is `cpe:2.3:a:zlib:zlib:*:*:*:*:*:*:*:*` with `versionEndIncluding` 1.2.12 (NVD API). Ecosystem advisories name a package instead: in the OSV format, "The object itself has two required fields, `ecosystem` and `name`, and an optional `purl` field" (OSV schema). A purl is "a standardized URL-based syntax that uniquely identifies software packages" and is an Ecma standard, ECMA-427 (purl specification). A CPE match therefore depends on a correct vendor and product, which for Syft means a dictionary lookup where one exists and a heuristic guess otherwise (Syft's `cpegenerate` documentation describes this "two-tier approach"), while an ecosystem match depends on the package manager's own name.

**Which route the scanners take.** Grype 0.119.0 turns CPE matching off by default for the language ecosystems covered by GitHub advisories (Python, JavaScript, Java, Go, Ruby, Rust, .NET, Hex) and for Debian and RPM packages, and keeps it on for its catch-all `stock` matcher (`grype config`); for the GitHub-advisory ecosystems the change dates from 2023 (Grype pull request #1412, "disable CPE-based matching for GHSA ecosystems by default"). For Alpine packages, its apk matcher combines Alpine's security feed with NVD's CPE data, and in its own source code "NVD counts only where the feed is silent" (`grype/matcher/apk/matcher.go`). Anchore's guidance is that "exact-direct-match and exact-indirect-match are high confidence, cpe-match requires verification". Trivy takes the other route for operating-system packages: it "uses the advisory database from the appropriate OS vendor", because "OS vendors usually backport upstream fixes" (Trivy documentation); we found no Trivy documentation describing NVD CPE matching.

**What that meant in our runs.** This explains the disagreement in section 3. Alpine's feed for release 3.24 has entries for busybox and zlib but lists neither CVE-2025-60876 nor CVE-2026-85091 (Alpine secdb, checked 2026-09-30), so Grype's four Alpine matches came from NVD CPE data, while Trivy, which reads the Alpine feed, reported nothing. The CPE route also depends on NVD's analysis: NVD's record for the zlib match, CVE-2026-85091, is still "Awaiting Analysis" and has no configurations at all (NVD API, 2026-09-30), so the version range Grype matched on did not come from an NVD configuration in the current record. For tradar's Python packages, both scanners used GitHub advisories, and on the same SBOM they reported the same 13 CVEs.

**Weaknesses (CWEs).** In CycloneDX, and in all the scanner data we saw, a CWE reaches a component only through a vulnerability (SPDX could attach a `cwe` external reference to a package directly), and each CWE assignment has a source. NVD labels each source "Primary" or "Secondary", and its API documentation says "Primary sources include the NVD and CNA who have reached the provider level in CVMAP". Sources can disagree: for CVE-2022-37434, NVD gives CWE-787 and a second source gives CWE-120. For the two Alpine CVEs in our runs NVD had assigned no CWE of its own; CWE-284 and CWE-787 came only from Secondary sources, and Grype passed them through with their source and type (NVD API; Tool runs). When NVD cannot classify a weakness, it uses placeholders instead of CWE numbers: `NVD-CWE-noinfo`, "There is insufficient information about the issue to classify it", and `NVD-CWE-Other`, "NVD is only using a subset of CWE for mapping instead of the entire CWE, and the weakness type is not covered by that subset" (NVD weakness list). Those placeholders do not fit CycloneDX's integer `cwes` field (1.1); SPDX records a CWE only as an external reference (1.2); OSV has no CWE field and leaves `database_specific` "entirely defined by the database" (OSV schema); and SWID has nothing (1.3).

**Takeaway:** The bridge from components to CVEs runs through one of two naming systems, CPE for NVD and package names for ecosystem and distribution advisories, and the choice decides the result: CPE matches need verification, by the scanner vendor's own guidance, while distribution feeds reflect backported fixes but cover only their own packages. CWEs arrive second-hand, attached to vulnerabilities, from sources that can disagree, and with placeholders that not every format can store. For DEC-008, NVD is one source among several: its CPE configurations can be missing for CVEs awaiting analysis, its own CWE is not always present, and in our runs most reported matches came from GitHub advisory data, while all four Alpine matches came from NVD CPE data because the Alpine feed listed neither CVE.

## 6. Build identity: how composition pins a product version

Input to DEC-001.

**The document versus the product.** An SBOM identifies two different things, and the formats keep them apart. The first is the SBOM document itself: CycloneDX says "Every BOM generated SHOULD have a unique serial number, even if the contents of the BOM have not changed over time", and its `version` "SHOULD be incremented by 1" whenever an existing BOM is modified (`cyclonedx-1-7`); an SPDX document has an `spdxId` like any other element. The second is the product the SBOM describes, CISA's "Primary Component": CycloneDX's `metadata.component` or SPDX's `Sbom.rootElement`, each with its own name, version and identifiers (comparison table). A serial number therefore identifies an SBOM, not a build: two independently generated SBOMs of the same build should carry different serial numbers.

**What pins the product.** A version string names a release; a content digest pins exact bytes. CISA's framing asks, at its Recommended Practice level, for "at least one hash of the Primary Component" (`cisa-framing-software-component-transparency`, §2.2.2.5). For container images the natural pin is the image digest: in the OCI specifications a digest is "a unique identifier created from a cryptographic hash of a Blob's content", a tag is "a custom, human-readable pointer to a manifest", and "A manifest digest may have zero, one, or many tags referencing it"; only when a manifest is requested by digest do the rules say "clients SHOULD verify the returned manifest matches this digest" (OCI Distribution Spec v1.1.1). For source code the pin is a commit, which SLSA's model records as a build dependency: "a build that takes a git repository URI as a parameter might record the specific git commit that the URI resolved to as a dependency" (SLSA v1.2 Build Provenance).

**What our tool runs recorded.** Syft's SBOM of `alpine:latest` set the primary component's version to the image digest (`sha256:260479a1...`), which pins it to exact bytes. Syft's SBOM of the tradar source directory has a primary component of type `file`, named after the local path, with no version at all (Tool runs in `searches.md`). Neither SBOM states its SBOM type (`metadata.lifecycles` is absent) or how the product was built (`formulation` is absent), although CycloneDX 1.7 has both fields. In our reading, the first fits CISA's "Analyzed" type, "generated through analysis of artifacts ... after its build", and the second its "Source" type, "created directly from the development environment, source files, and included dependencies" (CISA, Types of SBOM Documents; SPDX's `sbomType` values reuse these definitions).

**Records of the build itself.** Some formats describe the build, not just its output. SPDX 3.0.1's Build profile has a `Build` element that "describes a build instance of software/artifacts": beyond the `spdxId` and `creationInfo` every element needs, only `buildType` is required, and it can record a `buildId`, the digest of the build configuration (`configSourceDigest`), parameters, environment and start and end times, and link to inputs and outputs through `hasInput` and `hasOutput` relationships (`spdx-3-0-1`). CycloneDX's `formulation` can describe how "any referencable object within the BOM" was "created, assembled, deployed, tested" (`cyclonedx-1-7`). SLSA provenance is "an attestation that a particular build platform produced a set of software artifacts through execution of the buildDefinition" (SLSA v1.2 Build Provenance), and in the in-toto format it uses, each subject "MUST have `digest` set" and subjects "are matched purely by digest" (in-toto Attestation Statement v1; library record `in-toto-attestation-v1`, not yet summarized). Reproducible builds close the loop: a build is reproducible if "any party can recreate bit-by-bit identical copies of all specified artifacts" (reproducible-builds.org). A SWID tag, by contrast, has no build record; its `tagVersion` only lets a newer tag replace an older one "without suggesting any change to the underlying software product" (NIST IR 8060 §3.1.1).

**Takeaway:** Build identity involves three separate things that the formats keep apart: an ID for the SBOM document (serial number), an identity for the product (name and version, pinned by a content digest when one is recorded), and optionally a record of the build that produced it (SPDX `Build`, CycloneDX `formulation`, SLSA provenance). In our runs, Syft recorded a digest for a container image, nothing that pins a source directory, and no build record. For DEC-001, this is the evidence on what can anchor a "product version": a content digest pins bytes, a version string only names a release, and an SBOM serial number identifies the document, not the build.

## 7. Synthesis: implications for tmodel

This section gathers the evidence above by decision: the three that are still open, and DEC-007, which ADR-0001 has since accepted. It does not select a design.

**DEC-001 (core object model).**
- *Identity.* A component can carry several identifiers at once, and only some can be checked against its bytes (`hashes`, OmniBOR, SWHID; 1.1, 1.2, comparison table). Names such as CPEs can be guesses (section 3).
- *Relationships.* CycloneDX separates depends-on, contains and provides, with a component's history in `pedigree`; SPDX has 59 relationship types across all its profiles; the two formats' "scope" qualifiers mean different things (1.1, 1.2).
- *Completeness.* "None" and "unknown" are different claims, and an SBOM can assert completeness but cannot prove that a component is absent (1.1, 1.2).
- *Hardware.* An HBOM is mostly supply-chain data, and most of CISA's HBOM fields have no home in the SBOM formats; firmware is where hardware meets software (section 2).
- *Build identity.* A content digest pins bytes, a version string names a release, and an SBOM serial number identifies the document, not the build (section 6).
- *VEX.* Exploitability statements link a vulnerability to a product; SPDX's statuses follow CISA's, while CycloneDX's line up only partly (comparison table).

**DEC-002 (formats to import and export).**
- CycloneDX 1.7 is what our tools wrote and what Dependency-Track reads. SPDX 3.0.1 is the more graph-like model, but Syft cannot write it and Dependency-Track and GUAC cannot read it yet. SWID is an identification tag, not a composition format (1.2, 1.3, section 3). Both main formats are on their way to ISO: SPDX 3.0 as ISO/IEC DIS 5962 and CycloneDX as ISO/IEC CD 27055 (section 1).
- The same scan carries different data depending on the output format (Syft's CPEs, section 3), and converting between formats can lose a hash's algorithm name and VEX distinctions (1.2, comparison table).

**DEC-007 (accepted in ADR-0001, radar / tmodel split).** Under ADR-0001, tmodel consumes radar's (tradar's) output, and "the interface is the composition→model-input mapping surveyed in RPT-0004 (#8)". Today radar's graph keeps only the name, version and ecosystem of vulnerable packages; purl, CPE, dependency links and CWEs are dropped on the way, although the Syft and Grype outputs it already uses contain them (section 4).

**DEC-008 (CWE/NVD integration).** NVD is one source among several: its CPE configurations can be missing for CVEs awaiting analysis, CWEs come from Primary and Secondary sources that can differ, and NVD uses placeholder values that some formats cannot store. In our runs most reported matches came from GitHub advisory data, and all Alpine matches came from NVD CPE data, since the Alpine feed listed neither CVE (section 5).

**Limits of this report.**
- Paywalled standards not read: ISO/IEC 19770-2:2015 (SWID) and ISO/IEC 19770-6:2024 (hardware identification tags). Related supply-chain standards in ISO's catalog, such as ISO/IEC 27036-3:2023 (guidelines for hardware, software, and services supply chain security) and ISO/IEC 18974:2023 (OpenChain security assurance), were not reviewed.
- Dependency-Track and GUAC are described from their documentation, not run.
- The tool runs cover two inputs; other ecosystems (for example a Debian-based image or a Java project) would exercise other matchers.
- The `cyclonedx-1-7` and `spdx-3-0-1` library summaries have header metadata only; their Overview and Applicability sections are still unfilled. Most sources in `sources.md` are not yet library records.
- Overlap: VEX and CSAF in depth belong to #9.