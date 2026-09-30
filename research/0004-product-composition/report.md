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
updated: "2026-09-30"
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
open_decisions: [DEC-001, DEC-002, DEC-007, DEC-008]
---

# Product composition

> **This report does not select a design.** It is evidence for the open decisions listed above.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md). 
Axes: [`dimensions.md`](dimensions.md).

## Comparison table

_In progress. Starting point: CISA Framing (3rd ed.) Table 1, updated to CycloneDX 1.7, plus SWID._

## 1. SBOM formats (CycloneDX, SPDX, SWID)

Input to DEC-002.

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

**Dependencies.** CycloneDX separates three kinds of relationship between components (`cyclonedx-1-7`):

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

Three things stand out. First, SPDX treats content-based IDs as a way to verify, not just to name: `ContentIdentifier` and `Hash` are both kinds of `IntegrityMethod`, "an independently reproducible mechanism that permits verification", while CycloneDX words `omniborId` and `swhid` as identity claims. Second, one ID can go in two places: a purl fits both `packageUrl` and an `externalIdentifier` of type `packageUrl`, and neither entry says which to use, whereas gitoid gets an explicit rule (a gitoid of the artifact goes in `contentIdentifier`, one of its input manifest in `externalIdentifier`). Third, the same name means different things across formats: SPDX's `swid` is a CoSWID tag (RFC 9393), while CycloneDX's `swid` is an ISO/IEC 19770-2 SWID tag (see 1.3). For DEC-002, a tool importing both formats has to read purls from two SPDX places and reconcile SPDX's global `spdxId` with CycloneDX's file-local `bom-ref`.

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

Three things stand out. First, SPDX supports CWEs but has no dedicated CWE field: a weakness is attached as an external reference (`externalRef`) of type `cwe` ("a reference to a source of software flaw defined within the official CWE List"), whose value goes in a free-text `locator`, where CycloneDX has a dedicated `cwes` list of integers. Second, the VEX vocabularies differ: SPDX has four statuses and five justifications (`componentNotPresent`, `vulnerableCodeNotPresent`, `vulnerableCodeNotInExecutePath`, `vulnerableCodeCannotBeControlledByAdversary`, `inlineMitigationsAlreadyExist`), CycloneDX six states and nine justifications, and neither specification maps its values onto the other's. Third, SPDX is stricter in one place and not in another: an "affected" statement must carry an `actionStatement` (CycloneDX's `response` is only "strongly encouraged", and only when a vulnerability is exploitable), but for "not affected" the spec says one of `impactStatement` or `justificationType` "MUST be defined" while giving both a cardinality of 0..1, "making them optional". SPDX also covers EPSS and exploit catalogs such as KEV, which CycloneDX 1.7 has no field for. This bears on DEC-008 (CWE/NVD integration) and, since VEX statuses become typed links between vulnerabilities and products, on DEC-001.

**Takeaway:** SPDX 3.0.1 is built as a graph: every package, vulnerability and relationship is an element with a global `spdxId`, so it can link across documents, and it offers far more relationship types (59) and more kinds of vulnerability assessment (adding EPSS and exploit catalogs) than CycloneDX. It is weaker where CycloneDX is strong: hardware is only a purpose label, a CWE has no dedicated field (only an external-reference type), and completeness has three values with no stated default. As with CycloneDX, almost everything beyond an ID, a name and creation information is optional and asserted by the author, and some rules the text states (a "MUST" that a not-affected statement give a justification or an impact statement) are not enforced by the model.

### 1.3 SWID

## 2. HBOM (hardware and firmware)

Input to DEC-001.

## 3. Tools (Syft, Grype, Trivy, Dependency-Track)

Input to DEC-002 and DEC-007.

## 4. How tradar uses these today

Input to DEC-007.

## 5. The bridge: components to CVEs and CWEs

Input to DEC-001 and DEC-008.

## 6. Build identity: how composition pins a product version

Input to DEC-001.

## 7. Synthesis: implications for tmodel