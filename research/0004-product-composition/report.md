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
| `cpe` | a product in the NVD's naming scheme | assigned name |
| `swid` | an ISO/IEC 19770-2 tag written by the software's maker | assigned name |
| `hashes` | the exact bytes | computed from bytes |
| `omniborId` | the exact bytes (an OmniBOR artifact ID) | computed from bytes |
| `swhid` | source code, via a Software Heritage ID | computed from bytes |
| `bom-ref` | nothing outside this file; it links parts of one SBOM | local |

Two things stand out. First, the spec words five of the six global identifiers as claims: `purl`, `cpe`, `swid`, `omniborId` and `swhid` each "asserts the identity of the component", and an optional `evidence.identity` field can back the claim up (`cyclonedx-1-7`). Second, only three identifiers are computed from the bytes (`hashes`, `omniborId`, `swhid`; see `cisa-framing-software-component-transparency`, §2.2.2.4); the rest are assigned names, which can be wrong or guessed.

Even `hashes` has limits: the spec does not say which bytes are hashed, so two SBOMs of the same artifact can carry different hashes, and the allowed algorithms still include MD5 and SHA-1, which CISA notes "will be formally discontinued in 2030" (`cisa-framing-software-component-transparency`, §2.2.2.5). All of this matches the names-versus-bytes gap the library's SBOM topic describes (library topic `sbom`), and it matters for DEC-002 (which formats tmodel imports).

**Hardware and firmware.** CycloneDX can describe hardware, but little of it is built into the spec. `device` is the only component type described as hardware ("a hardware device such as a processor or chip-set"); `firmware` and `device-driver` are each "a special type of software", and `platform` is a runtime environment (`cyclonedx-1-7`). The `device` description adds one rule: a device containing firmware "SHOULD include a component for the physical hardware itself and another component of type 'firmware' or 'operating-system'", and nested `components` can show an assembly, "similar to system → subsystem → parts assembly in physical supply chains". There are no hardware-only fields: details such as a serial number, MAC address or location on the board go in the generic `properties` field, which the spec describes as a place for "data not officially supported in the standard", under names from CycloneDX's separate property taxonomy, such as `cdx:device:serialNumber` (see `sources.md`). Because those names live outside the schema, a schema check cannot catch a missing or misspelled one, which matters for DEC-001 (tmodel's core object model) if hardware becomes part of it.

**Dependencies.** CycloneDX separates three kinds of relationship between components (`cyclonedx-1-7`):

| Relationship | Field | Meaning |
|---|---|---|
| depends on | `dependencies[].dependsOn` | the component's direct dependencies; indirect ones come from following the chain |
| provides | `dependencies[].provides` | the component implements a standard or algorithm, which "does not imply that the implementation is in use" |
| contains | nested `components` | an assembly, "similar to system → subsystem → parts assembly"; "This is not a dependency tree" |

Three details matter for anyone reading the graph. First, a missing entry means "unknown", not "none": components with no dependencies "must be declared as empty elements", while components left out of the graph "may have unknown dependencies", to be treated as "opaque and not an indicator of an object being dependency-free". Second, `dependsOn` and `provides` point by `bom-ref` "in the same BOM document"; unlike a vulnerability's `affects`, they cannot use a BOM-Link into another SBOM, so combining several SBOMs means matching components by their global IDs. Third, `scope` says whether a component is reachable at runtime (`required`, `optional` or `excluded`); when it is missing, consumers "SHOULD" assume `required`, and a component that is installed but blocked from being called still counts as `required`. These typed relations bear on DEC-001 (tmodel's core object model and its typed relations), and the same-file limit bears on DEC-002 (which formats tmodel imports).

**Completeness.** A separate top-level `compositions` list says how complete the relationships are (`cyclonedx-1-7`). Each entry names what it covers by `bom-ref` (nested parts in `assemblies`, dependency links in `dependencies`, or the list of `vulnerabilities`) and gives one required `aggregate` value. The ten values line up with CISA's four completeness levels (`cisa-framing-software-component-transparency`, §2.2.2.6.4):

| CISA | CycloneDX `aggregate` |
|---|---|
| Known | `complete` |
| Partial | `incomplete`, or one of six narrower variants such as `incomplete_third_party_only` |
| Unknown (the CISA default) | `unknown` ("a 'best-effort'... but the completeness is inconclusive") or `not_specified` (the CycloneDX default) |
| None | no value of its own; an empty `dependsOn` entry, as described under Dependencies |

Two things stand out. First, CycloneDX splits CISA's Unknown in two: `unknown` means someone tried and could not tell, while `not_specified` means no one said anything, and leaving `compositions` out entirely makes no completeness claim at all. Second, both standards limit the claim to direct relationships: CycloneDX references "do not cascade to transitive dependencies", matching CISA's rule that a "Known" component can have upstream components that are only "Partial" or "Unknown". So an SBOM can be complete at the top and still have gaps further down, and it can never prove that a component is absent (library topic `sbom`). This matters for DEC-001: a model that reads an SBOM as a full list will draw wrong conclusions whenever completeness is unknown or unstated.

**Vulnerabilities and weaknesses.** A top-level `vulnerabilities` list records "vulnerabilities identified in components or services" (`cyclonedx-1-7`). Each entry points at what it hits through `affects`, lists the weakness types behind it in `cwes`, and can carry an `analysis`: the author's answer to "does this actually affect us?", known as VEX (VEX itself is in scope for #9). The analysis has a `state` (for example `exploitable`, `not_affected` or `false_positive`), a `justification` (for example `code_not_reachable` or `protected_by_mitigating_control`), a `response` (for example `update` or `will_not_fix`), a free-text `detail`, and timestamps for when it was first issued and last updated.

Three things stand out. First, `cwes` is the only place a CWE can appear, so a component links to a weakness only through a vulnerability entry, and each CWE is a bare integer ("For example 399") rather than a string like "CWE-399". Second, unlike `dependsOn`, `affects` accepts a BOM-Link, so a vulnerability report can live in a separate file and still point into a product's SBOM. Third, the analysis is again a claim: `not_affected` "should" come with a justification, but the schema does not require one. Several justifications (`code_not_reachable`, `requires_configuration`, `protected_at_perimeter`, `protected_by_mitigating_control`) are threat-model conclusions in their own right, which makes this the most direct link between an SBOM and tmodel's model (DEC-001) and its CWE/NVD integration (DEC-008).

**Takeaway:** CycloneDX 1.7 can express identity, hardware, three kinds of relationship, completeness and vulnerability status, but almost all of it is optional, and most of it is a claim by whoever wrote the SBOM: identifiers are asserted, a missing dependency entry means "unknown", completeness can simply be left unstated, hardware details live outside the schema, and exploitability is the author's assessment. What a real SBOM actually contains depends on the tool that wrote it (section 3).

### 1.2 SPDX 3.0.1

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