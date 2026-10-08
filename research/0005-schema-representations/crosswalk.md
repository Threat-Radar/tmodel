---
schema: "archdoc/v1"
id: RPT-0005-crosswalk
title: "RPT-0005 crosswalk: 24 formats onto ARCH-0001's types and edges"
type: research
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: RPT-0005
---

# RPT-0005: crosswalk and local extension (dimension 8)

This file assembles Tables 2, 3 and 6 of [dimensions.md](dimensions.md) from the four Phase 1 files: [pilot.md](pilot.md), [fanout-vuln-data.md](fanout-vuln-data.md), [fanout-attack-composition.md](fanout-attack-composition.md) and [fanout-models-requirements.md](fanout-models-requirements.md). It answers the four questions of dimension 8. It is evidence for DEC-001, DEC-002, DEC-008 and DEC-009 and for #16 and #17; it accepts nothing.

**How it was built.** Each matrix cell is the fidelity mark taken by script from the matching cell of the source file. The source cell names the format's own element (field path or class) and its qualifiers; look there before relying on a mark. No mark was changed by hand. A cell shows `∅` where the source did not assess that concept, and `?` where the source could not verify it.

**Scope.** The sponsor's answers on #39 (2026-10-08) apply. CPE, purl and SWID are identifier schemes, not columns; they appear in the identity sub-row below. CISA KEV is an annotation on a CVE and appears under exploitation evidence. MITRE ATLAS gets no column: it reuses ATT&CK's structure, and RPT-0014 covers it. OpenC2 is out of scope. SSVC stays as a row until its scope is settled. The VEX profiles of CycloneDX and SPDX 3 are folded into those formats' rows; the side-by-side VEX comparison is §8 of fanout-vuln-data.md.

**Marks.** `=` same concept, no loss on import. `≈` close, with some loss. `⊂` / `⊃` the format's element is narrower / broader than ours. `txt` present only as prose. `ext` absent, but the format's extension mechanism could carry it. `—` absent and not extensible. Counts are a loss profile, not a quality score: a catalog is expected to have many `—` outside its scope (dimensions.md rubric note).

## Table 2, part 1: ARCH-0001 §3 types

The five right-hand columns count the marks in each row, as a loss profile for import.

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
