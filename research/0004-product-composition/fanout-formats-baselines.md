---
schema: "archdoc/v1"
id: RPT-0004-fanout-formats-baselines
title: "RPT-0004 Phase 1 fan-out: formats, minimum elements and other bill types"
type: research
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: RPT-0004
---

> Phase 1 fan-out notes, kept as the research agent wrote them; corrections found later are recorded in the design log (DL-0015). Downloaded files were not committed (third-party material); each is identified by URL and SHA-256 so it can be fetched again.

# RPT-0004 fan-out, agent 1: dimensions 1, 8 and 9

Scope: dimension 1 (SBOM formats: CycloneDX 1.7, SPDX 3.0.1, SWID with CoSWID), dimension 8 (minimum elements and policy baselines) and dimension 9 (other bill types, composition side only), plus Tables 1 and 2. Everything below was checked on 2026-10-08. Files were downloaded with `curl` or `gh api` into the session scratchpad (`scratchpad/fanout/agent1/`) and parsed with `jq` 1.8.1 and Python 3.13.9. RDF and validation tests ran in a scratch virtual environment with rdflib 7.6.0, pySHACL 0.40.1, python-jsonschema 4.26.0, PyLD 3.3.0, spdx3-validate 0.0.7 and xmlschema 4.3.2; XML Schema checks also ran with `xmllint` (libxml2 2.13.9). WebSearch worked for this agent (9 queries, section 7). Where a page blocked `curl` (cisa.gov, iso.org), the fallback is named in the record. "Our reading" marks an interpretation; everything else is quoted or measured.

Abbreviations used throughout: SBOM (software bill of materials), BOM (bill of materials), RDF (Resource Description Framework), OWL (Web Ontology Language), SHACL (Shapes Constraint Language), JSON-LD (JSON for Linked Data), XSD (XML Schema Definition), CDDL (Concise Data Definition Language), CBOR (Concise Binary Object Representation), BCP 14 (the IETF rule that uppercase MUST, SHOULD and so on are normative), purl (package URL), CPE (Common Platform Enumeration), VEX (Vulnerability Exploitability eXchange), TLP (Traffic Light Protocol).

**The most important findings, in short.**

1. **CISA's 2026 Minimum Elements are final.** Version 2.1, published 2026-07-29, co-authored by CISA, NSA, FBI and 15 partner agencies (including Germany's BSI and India's CERT-In). It "updates and replaces" NTIA 2021, has 17 data fields and 6 practices, and removes SWID tags from the list of SBOM formats. Table 2 uses its elements as rows (section 3).
2. **CycloneDX 1.7.1 and 1.7.2 are real releases** (2026-06-02 and 2026-09-17). The JSON Schema changed only in 1.7.1 (typo fixes plus one new SHOULD sentence); 1.7.2 changed only the XML schema. CycloneDX 2.0 is in development (draft pull request #652), drops the XML and Protocol Buffers schemas, and its milestone (due 2026-08-31) is still open. There is no 1.8 milestone.
3. **SPDX 3.1 is not final.** Only 3.1-RC1 (2026-01-24) exists; the 3.1-rc2 milestone (due 2026-09-27) is still open. SPDX term IRIs are version-specific (3.0, 3.0.1 and 3.1 each have their own namespace), and the SPDX project has decided that the 3.0 maintenance branch goes back to `/3.0/` IRIs.
4. **ISO status moved since v0.1.0.** ISO Open Data (file dated 2026-10-07) shows ISO/IEC DIS 5962 (SPDX 3.0) at stage 40.99 "DIS approved for registration as FDIS", and CycloneDX and purl as ISO/IEC DIS 27055 and DIS 27056 at stage 40.00 "DIS registered".
5. **An SPDX 3.0.1 JSON-LD document loads into RDF as it is**, with caveats: the context must be fetched over the network, keys the context does not define are dropped silently, relative `spdxId` values become location-dependent IRIs, and the published SHACL shapes reject every reference to an element defined in another document. Plain pySHACL fails 2 of 9 official examples for that reason; SPDX's own validator works around it.
6. **Many rules exist only as text.** SPDX 3.0.1: the 14 cardinality restrictions written under "External properties restrictions" (for example "Package requires a name") are in neither the SHACL shapes nor the JSON Schema, and no profile-conformance rule is machine-checked; an official SPDX example that declares the AI profile breaks the AI profile's MUST. CycloneDX 1.7: duplicate `bom-ref` values, dangling `dependsOn` targets, invalid purls and misplaced `data` or `modelCard` objects all validate; `format: date-time` is only checked if the validator is configured to assert formats. SWID: a tag with no `Entity` at all validates against ISO's own XSD, although the XSD comment says one is required.
7. **The three main texts do not use BCP 14 the same way.** ECMA-424 (CycloneDX) uses ISO-style lowercase "shall" (717 times) and has only 2 uppercase keywords, both in licence boilerplate; SPDX 3.0.1 mixes cases; RFC 9393 (CoSWID) and BSI TR-03183-2 declare BCP 14. FX-1 keyword counting (which counts uppercase only) needs a different rule for ECMA-424.
8. **Baselines conflict on vulnerability data.** BSI TR-03183-2 says "An SBOM MUST NOT contain vulnerability information"; CERT-In's guidelines list "Vulnerabilities" as a required SBOM field.

---

## 1. Per-source records

### 1.1 CycloneDX 1.7 (ECMA-424 2nd edition), JSON Schema at tag 1.7.2

| field | value |
|---|---|
| Citation and verified URL | OWASP CycloneDX and Ecma TC54, "CycloneDX Bill of materials specification", ECMA-424 2nd edition, December 2025 (= CycloneDX 1.7). PDF: <https://ecma-international.org/wp-content/uploads/ECMA-424_2nd_edition_december_2025.pdf>. Schema: <https://raw.githubusercontent.com/CycloneDX/specification/1.7.2/schema/bom-1.7.schema.json>. Releases: <https://github.com/CycloneDX/specification/releases>. |
| Version pinned and date | 1.7, GitHub release 2025-10-21; ECMA-424 2nd edition "adopted by the General Assembly of December 2025" (PDF, Introduction). Patch releases 1.7.1 (2026-06-02) and 1.7.2 (2026-09-17), both GitHub releases with tags (`gh api repos/CycloneDX/specification/releases`, 2026-10-08). Latest on 2026-10-08: 1.7.2. The Ecma page lists only the 2nd edition (December 2025) and, in its archive, the 1st edition (June 2024): the patch releases are not separate Ecma editions. |
| Steward | OWASP CycloneDX project, standardised by Ecma TC54 ("TC54 aims to standardize core data formats, APIs and algorithms around software transparency information", Ecma TC54 page). In ISO as ISO/IEC DIS 27055 (section 1.9; the Ecma ECMA-424 page also says "ISO/IEC number DIS 27055"). |
| What it is | A general-purpose BOM format: components (13 types), services, dependencies, compositions (completeness), vulnerabilities, formulation, declarations, citations. JSON Schema draft-07, XML Schema and Protocol Buffers. |
| Licence | Schema `$comment`: "CycloneDX JSON schema is published under the terms of the Apache License 2.0." Repository: Apache-2.0 (GitHub licence API at tag 1.7.2). ECMA-424 PDF: Ecma copyright notice (copy and distribute with the notice; limited derivative works), and "All Software contained in this document ('Software') is protected by copyright and is being made available under the 'BSD License'" (PDF, "Software License"). |
| Library record | `cyclonedx-1-7`, `queued` (owner Ndewedo-Newbury). A second record, `ecma-424` (in `other/`), is a `stub` for the same text. |
| How checked | PDF sha256 `e8c55a3a968f3ef534fbcdd891c361714d3dc303b3747464f1d554f65b04c8e1` (same as the library record); `pdftotext` of 566 pages. JSON Schema at tags 1.7 (`df472ef4aaf593904c479293723a1a5c191d6672715c93b3c0b5c318f3914221`), 1.7.1 and 1.7.2 and `master` (all three `73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce`); 1.6 schema at tags 1.6 (`3e92dddb…afb93`), 1.6.1 (`efc54d74…ea541`), 1.6.2 (`18f57f74…5b37d`); XSD 1.7.2 (`c1da1a8d…25cdda`); proto 1.7.2 (`c662ecc6…1af6`). Diffs with `jq -S` and a Python walker; 20 validation tests with python-jsonschema (section 7, tool runs T10 to T12). |

Findings:

- **What the patch releases changed.** Between tags 1.7 and 1.7.1 the JSON Schema changed only in description strings: five typo fixes and one new sentence on `ratings`: "Consumers SHOULD consider ratings in prioritization decisions; source ratings may differ and aid prioritization." (`#/definitions/vulnerability/properties/ratings/description`, from pull request #722). No property, type, enum or `required` list changed (`diff` of `jq -S` output). The 1.7.1 release notes list XML and Protocol Buffers alignment for `modelCard` (`ModelCard.property`, repeated `considerations` lists). The 1.7.2 release notes list one XML change ("added the optional, repeated node `//bom/components/component/cryptoProperties/protocolProperties/relatedCryptographicAssets/relatedCryptographicAsset`"), and the JSON Schema file at 1.7.2 is byte-identical to 1.7.1.
- **ECMA-424 does not use BCP 14.** Its conformance clause uses ISO-style verbal forms: "It shall interpret and process the contents of CycloneDX BOMs in a manner conforming to this Standard" and "It should instantiate a warning or error condition when a CycloneDX BOM is not conforming to this Standard" (ECMA-424 §2). Its normative references do not include RFC 2119 or RFC 8174 (search of the PDF text for "2119", "8174", "BCP 14", "key words": 0 hits). In the PDF text, lowercase "shall" occurs 717 times, "shall not" 9, "should" 132, "should not" 301 (292 of them the repeated sentence "Value should not start with the BOM-Link intro 'urn:cdx:'"); the only 2 uppercase keywords are in licence boilerplate ("IN NO EVENT SHALL", "REQUIRED TO IMPLEMENT").
- **The schema's keyword casing changed over time.** Uppercase BCP 14 keywords in description and `meta:enum` strings: 81 in the 1.6 release (MUST 35, SHOULD 27, OPTIONAL 10, RECOMMENDED 6, MUST NOT 2, MAY 1), 27 in 1.6.1 (all SHOULD), 28 in 1.6.2 and 1.7, 29 in 1.7.1 and 1.7.2 (all SHOULD). The MUSTs became lowercase "must" (52 lowercase "must" in 1.7.2). Our reading: the change came with the ECMA-424 1st edition work (milestone "1.6-ECMA": "Minor documentation changes which do not affect the meaning of the specification"; pull request #501 "[DOCS] 1.6 ecma takeover descriptions").
- **What the text says the schema does not enforce** (scope and examples in section 2, Q7): ECMA-424 itself notes "This Standard does not define enforcement mechanisms for verifying the accuracy or completeness of a BOM, nor does it prescribe a specific transport mechanism for exchanging BOMs" (ECMA-424 §1, NOTE 2).
- **Cross-BOM references.** A BOM-Link (`urn:cdx:<serialNumber>/<version>#<bom-ref>`) is accepted in 10 places: `externalReferences[].url`, service data-flow `source` and `destination`, `compositions[].assemblies`, `vulnerabilities[].affects[].ref`, `annotations[].subjects`, `modelCard.modelParameters.datasets[].ref`, `resourceReferenceChoice.ref` (formulation) and `componentIdentityEvidence.tools` (walk of all `$ref` targets in the 1.7.2 schema). `dependencies[].dependsOn` and `.provides` accept only same-BOM references (`refLinkType`), as v0.1.0 found.
- **The schema leans on `format`.** It uses `format` 57 times (`date-time` 32, `iri-reference` 19, `date` 4, `idn-email` 2). JSON Schema draft-07 treats `format` as an annotation unless a validator is told to assert it; in our tests a timestamp of `"yesterday"` passed until both a format checker and the optional `rfc3339-validator` package were used (test C12). The SPDX 3.0.1 JSON Schema uses no `format` keyword at all (it uses patterns).
- **`specVersion` is not pinned.** It is a free string with only an example (`"1.7"`), so a document saying `"specVersion": "9.9"` validates against the 1.7 schema (test C13).
- **Open in XML, closed in JSON.** 132 JSON objects set `"additionalProperties": false` (unknown keys are rejected: test C18), so JSON extensions go through `properties[]`. The 1.7.2 XSD has 61 `xs:any namespace="##other"` and 48 `xs:anyAttribute` extension points ("Allows any undeclared elements as long as the elements are placed in a different namespace"). An XML BOM can therefore carry namespaced extensions that have no JSON equivalent.

### 1.2 CycloneDX 2.0 (in development, not released)

| field | value |
|---|---|
| Citation and verified URL | Draft pull request "[WIP] CycloneDX v2.0 Specification", <https://github.com/CycloneDX/specification/pull/652> (base `master`, head `2.0-dev`, opened 2025-06-15, last updated 2026-10-07); milestone <https://github.com/CycloneDX/specification/milestone/2>; schema at `2.0-dev` commit `f6dcf4d33fecff511c21c4616a5a66d2b8134687` (2026-10-07). |
| Version pinned and date | Unreleased. Milestone "2.0": due 2026-08-31, open, 90 open and 86 closed issues (updated 2026-10-05). Milestone "2.1": due 2027-04-16, open. No "1.8" milestone exists (`gh api .../milestones?state=all`, 2026-10-08). |
| Steward | OWASP CycloneDX, Ecma TC54. |
| What it is | A modular rewrite: one top-level schema referencing 35 module schemas (for example `cyclonedx-component-2.0`, `-party-2.0`, `-physical-2.0`, `-threat-2.0`, `-risk-2.0`, `-weakness-2.0`, `-blueprint-2.0`). |
| Licence | not checked for 2.0 (repository Apache-2.0). |
| Library record | none (a new record when 2.0 is released). |
| How checked | `gh pr view 652`, `gh api` of milestones and branches; downloaded `schema/2.0/README.md` (`266a72f3…7f6d`), `cyclonedx-2.0.schema.json` (`c7dbb1c9…f122`), `cyclonedx-2.0-bundled.schema.json` (`72ffe3c4…3280`), `modules/cyclonedx-component-2.0.schema.json` (`6d893030…0975`), parsed with `jq` and Python. |

Findings (all subject to change before release):

- **Breaking changes announced:** "Drop schema for XML." and "Drop schema for Protocol Buffers" with the reason "Downstream spec users may build ontop of JSON schema" (PR #652 body).
- **Top level:** JSON Schema 2020-12; `specFormat` (enum `"CycloneDX"`) and `specVersion` are required, replacing 1.x `bomFormat`; new top-level `threats`, `risks`, `controls`, `blueprints`, `perspectives`, `profiles`, `signatures`; there is no top-level `services` (component `type` now includes `service` and `material`).
- **Identity becomes attributed.** A component's `identifiers[]` are "Identifiers asserted by one or more parties to identify this component. Each entry groups one or more identity claims by the party asserting them"; each entry requires a `party` and `identities`, with 25 predefined schemes (`purl`, `cpe`, `swid`, `swhid`, `omniborid`, GS1 schemes, `mpn`, `part-number`, `serial-number`, `mac-address`, `imei`, `udi-di` and others). The 1.x component fields `purl`, `cpe`, `swid`, `omniborId`, `swhid`, `supplier`, `manufacturer`, `authors` and `publisher` are not in the 2.0-dev component properties. Our reading: an importer written for 1.x will not read 2.0 unchanged.
- **Hardware fields appear on components:** `boardLocation`, `deviceType`, `quantity`, `leadTime`, `materialForm`, `origins`, `certifications` (component module, 2.0-dev).

### 1.3 SPDX 3.0.1: model (OWL and SHACL), JSON-LD context, JSON Schema, specification text

| field | value |
|---|---|
| Citation and verified URL | The Linux Foundation and its Contributors, "System Package Data Exchange (SPDX) Specification Version 3.0.1". Model: <https://spdx.org/rdf/3.0.1/spdx-model.ttl> (HTTP 301 to `spdx.github.io/spdx-spec/v3.0.1/rdf/spdx-model.ttl`). Context: <https://spdx.org/rdf/3.0.1/spdx-context.jsonld>. JSON Schema: <https://spdx.org/schema/3.0.1/spdx-json-schema.json>. Specification source: `spdx/spdx-spec` tag `3.0.1` (tag object `f1b4f90c`); model source: `spdx/spdx-3-model` tag `3.0.1` (tag object `5878caae`). |
| Version pinned and date | 3.0.1: specification release 2024-12-17, model release 2024-12-12, model CHANGELOG "3.0.1 (2024-12-10)". No later final release on 2026-10-08 (section 1.4). |
| Steward | SPDX project of the Linux Foundation; ISO track as ISO/IEC DIS 5962 (section 1.9). |
| What it is | An RDF data model defined in OWL, with SHACL shapes in the same Turtle file, serialised as JSON-LD with a fixed context and constrained by a JSON Schema generated from the shapes (`"$comment": "This file was automatically generated by shacl2code"`). Ten profiles (Core, Software, Security, Licensing in two parts, Dataset, AI, Build, Lite, Extension). |
| Licence | Specification: "The SPDX Specification is provided under the Community Specification License 1.0 (Community-Spec-1.0)"; "Pre-existing portions ... are provided under Creative Commons Attribution 3.0 Unported (CC-BY-3.0)" (spec `LICENSE` at tag 3.0.1). Model files carry `SPDX-License-Identifier: Community-Spec-1.0`. |
| Library record | `spdx-3-0-1`, `queued` (owner Ndewedo-Newbury); related `iso-iec-5962-2021` (`queued`) and `iso-iec-5962` (`stub`, duplicate). |
| How checked | Served model sha256 `30ebb4af2d70a9809044ef46f44cc3dc5125226d70f818a50ed2e1d5f404c593` (same as RPT-0005's 2026-10-05 download; `Last-Modified` changes with each site rebuild); model at tag 3.0.1 `77b058eb…a5cf8`; context `c72b0928f094c83e5c127784edb1ebca2af74a104fcacc007c332b23cbc788bd` (same at tag and served); JSON Schema `582c64e809d5b3ef9bd0c4de13a32391b47b0284a3e8d199569fb96f649234b1`; source tarballs (spdx-3-model `b3285f33…d78`, spdx-spec `eaaed0b3…3623`). Loaded 9 official example documents with rdflib and PyLD, validated with pySHACL, python-jsonschema and spdx3-validate, ran 22 mutation tests and 3 extra tests (section 7, tool runs T1 to T9). |

Findings:

- **The model served at the 3.0.1 URL is not the tagged 3.0.1 model.** Parsed with rdflib, the served file has 3,735 triples and the file at tag `3.0.1` 3,569; the graphs are not isomorphic. The differences: the ontology label gains trademark signs, and the shape for `Core/Element` property `extension` changed. At the tag it requires `sh:class` `Extension/Extension`; served, it has a `sh:not` over a list of 54 known non-extension classes with the message "Class is known to not derive from Extension and cannot be used" (shape-by-shape comparison: 52 node shapes in both, only this one differs). Our reading: tools that fetch the model from the canonical URL validate extensions more leniently than the tagged artifact; a record should pin both hashes.
- **The specification defines two validation layers.** "An SPDX serialization in JSON-LD format is considered conformant to the SPDX specification if it adheres to the following two validation criteria: Structural validation: The JSON-LD document must structurally validate against the SPDX JSON Schema ... Semantic validation: The JSON-LD document must successfully validate against the SPDX OWL ontology ... The SPDX OWL ontology also incorporates SHACL shape restrictions" (`docs/serializations.md`, "JSON-LD validation", tag 3.0.1).
- **The JSON Schema is stricter than the text on the context.** The text says "All SPDX documents in JSON-LD format must include a reference to the SPDX global context file at the top level" and also "Additional namespace mappings may be defined within a separate object within the context" (`serializations.md`, "JSON-LD context file"). The schema requires `"@context": {"const": "https://spdx.org/rdf/3.0.1/spdx-context.jsonld"}`, so a context array with an extra mapping object fails structural validation (test M10).
- **SPDX now calls its JSON a subset of JSON-LD.** In the 3.1-RC1 text: "The SPDX 3 JSON format is a strict subset of JSON-LD." and it "may be parsed", "not serialized", "using standard JSON-LD libraries" (`docs/serializations.md` at tag `v3.1-RC1`, "A strict subset of JSON-LD"; the source sets "not serialized" off with dashes). The 3.0.1 text does not contain this sentence; it came from pull request #1197 (merged 2025-04-16).
- **The shapes and the schema miss rules the model text states.** 14 cardinality constraints written under "External properties restrictions" in five class pages are in neither the SHACL shapes nor the JSON Schema: `Software/Package` and `Software/File` name minCount 1; `AI/AIPackage` releaseTime, suppliedBy, downloadLocation, packageVersion, primaryPurpose minCount 1; `Dataset/DatasetPackage` builtTime, originatedBy (minCount 1, maxCount 1), releaseTime, downloadLocation, primaryPurpose minCount 1; `Security/EpssVulnAssessmentRelationship` publishedTime minCount 1 (search of all 271 model `.md` files for that heading; each restriction looked up in the class's SHACL property shapes; the model has no `sh:targetClass` and no `sh:sparql`). Behaviour confirms it: a Package without a name passes both layers (test M4), and so do an AIPackage and a DatasetPackage carrying only `spdxId`, `name` and `creationInfo` (test T8).
- **Profile conformance is not machine-checked.** Example: "for every `/AI/AIPackage` there MUST exist exactly one `/Core/Relationship` of type `hasConcludedLicense` having that element as its `from` property and a `/SimpleLicensing/AnyLicenseInfo` as its `to` property" (`model/AI/AI.md`, "Profile conformance"). The official example `ai/example01` in `spdx/spdx-examples` declares `profileConformance` `ai` but neither of its two AIPackages has a `hasConcludedLicense` relationship, and it passes the JSON Schema, pySHACL and spdx3-validate (test T7). Its DatasetPackage also lacks `releaseTime`, which `DatasetPackage.md` requires. The SPDX project tracks the gap: issue #522 "Expressing conformance constraints" (open since 2023-10-21, milestone 3.1).
- **The VEX "not affected" MUST is still text only.** "Both impactStatement and justificationType properties have a cardinality of 0..1 making them optional. Nevertheless, to produce a valid VEX not_affected statement, one of them MUST be defined." (`VexNotAffectedVulnAssessmentRelationship.md`, as v0.1.0 found). Issue #923 (open, milestone 3.1) proposes an `sh:or` shape for it. Test M6 confirms neither layer checks it. The same page says the class "is restricted to the doesNotAffect relationship type" and that "The from: end of the relationship must be a /Security/Vulnerability classed element"; a statement with `relationshipType` `contains` and a Package as `from` passes both layers (test T9).
- **The project fixes text and model mismatches when it finds them.** 3.0.1 "Corrected `actionStatement` cardinality from `0..1` to `1..1` to match its textual description" (model CHANGELOG, 3.0.1, pull request #908).
- **3.0.0 and 3.0.1 are not IRI-compatible.** 3.0.1 renamed `imports` to `import`, `parameters` to `parameter`, `hasInputs` and `hasOutputs` to `hasInput` and `hasOutput`, fixed `hasPrerequsite` to `hasPrerequisite`, removed `Software/contentType` (model CHANGELOG, "Changes since 3.0"), and changed the namespace to `https://spdx.org/rdf/3.0.1/terms/` (pull request #800).
- **A small text error.** The `SupportType` entries say "There is a validUntilDate that can provide additional information about the duration of support", but the property is named `validUntilTime` (`model/Core/Vocabularies/SupportType.md`, `model/Core/Properties/validUntilTime.md`).

### 1.4 SPDX after 3.0.1: 3.1-RC1 and the 3.0 maintenance branch

| field | value |
|---|---|
| Citation and verified URL | <https://github.com/spdx/spdx-spec/releases/tag/v3.1-RC1>; <https://github.com/spdx/spdx-3-model/releases/tag/3.1-rc1>; milestones of both repositories; issues spdx-3-model #1046, #1051, #1158. |
| Version pinned and date | v3.1-RC1, pre-release, 2026-01-24 (both repositories). On 2026-10-08: milestone "3.1-rc2" due 2026-09-27 still open (24 open issues in spdx-3-model, 13 in spdx-spec); "3.1-rc3" open; "3.1" open (110 open, 131 closed in spdx-3-model); "3.0.2" due 2026-04-30 still open. Commits were still landing on `develop` on 2026-10-06 (for example "Rename artifactSize to byteSize", "Add rdfiri ExternalIdentifierType"). **No final 3.1.** |
| Steward | SPDX project. |
| What it is | The next minor version; adds Hardware, Service, SupplyChain, Operations and FunctionalSafety namespaces (RC1 model). |
| Licence | as 3.0.1 (not re-checked for RC1). |
| Library record | none; a new record when 3.1 is final. |
| How checked | `gh api` of releases, milestones, commits, issues; downloaded the RC1 model (`711b44ef…0949`), the RC1 context (`e57db84c…f178`) and `serializations.md` at `v3.1-RC1` (`c63e297b…93eb`). |

Findings:

- **Namespaces change per version.** The RC1 model uses `https://spdx.org/rdf/3.1/terms/` (881 occurrences) and contains no `3.0.1` string, so it declares no mapping to 3.0.1 terms. The canonical 3.1 context URL, `https://spdx.org/rdf/3.1/spdx-context.jsonld`, already serves the RC1 context (byte-identical to the `v3.1-RC1` copy). Our reading: a JSON-LD document that points at the 3.1 URL today is parsed with a pre-release vocabulary.
- **The 3.0 maintenance branch goes back to `/3.0/` IRIs.** Issue #1046 (closed 2025-10-10): "For publishing the specification, RDF should remain constant ... instead of `https://spdx.org/rdf/3.0.1/terms/Core/Element` they should simply be `https://spdx.org/rdf/3.0/terms/Core/Element`"; pull request #1051 ("[3.0] RDF URL '3.0.1' -> '3.0'", merged 2025-07-25, milestone 3.0.2) applies it to `support/3.0`. Our reading: if 3.0.2 is released, its documents will not share term IRIs with 3.0.1 documents.
- **3.1 relaxes the AI and Dataset rules.** Pull request #1158 (merged 2026-01-07, milestone 3.1) drops releaseTime, suppliedBy, downloadLocation and packageVersion from the AIPackage and DatasetPackage restrictions and drops the licence-relationship conformance rules, keeping primaryPurpose mandatory.
- **3.1 moves to ISO verbal forms.** RC1 text: "Key names shall be wrapped in double quotes" (3.0.1: "Key names MUST be wrapped in double quotes").

### 1.5 SPDX "Differences from previous editions" annex

| field | value |
|---|---|
| Citation and verified URL | SPDX, "Differences from previous editions", <https://github.com/spdx/using/blob/main/docs/diffs-from-previous-editions.md>. The 3.0.1 specification site page `annexes/diffs-from-previous-editions/` redirects there. |
| Version pinned and date | `spdx/using` at commit `10e4b14c9cc5642aa4b4ce629e2b0560b771cf34`; the file's last commits are dated 2024-10-01 to 2024-11-13. |
| Steward | SPDX project (informative, not part of the normative 3.0.1 text). |
| What it is | Section A.1 lists structural differences, removed properties, renamed properties, a 45-row relationship-type mapping and serialisation changes from 2.3 to 3.0. |
| Licence | `SPDX-License-Identifier: Community-Spec-1.0` (file header). |
| Library record | none; cite under `spdx-3-0-1`. |
| How checked | Downloaded raw file (`78c7819a…e163`); parsed the mapping table with Python (45 rows, 34 marked "Swap to and from? Y"); compared two rows with the 2.3 relationship chapter (`spdx-spec` tag `v2.3`, `chapters/relationships-between-SPDX-elements.md`, `e2a91703…6f98`) and the 3.0.1 RelationshipType page. |

Findings:

- **Breaking changes for a 2.3 importer** (A.1 "Structural Differences"): `ExternalDocumentRef` becomes `NamespaceMap` plus `ExternalMap` (`import`); creator strings become `Agent` and `Tool` elements (`createdBy`, `createdUsing`); supplier and originator become `suppliedBy` and `originatedBy`; `fileContributor` becomes `originatedBy`; `FileType` splits into `contentType` and `SoftwarePurpose`; `packageFileName` and `packageChecksum` become a File with a `hasDistributionArtifact` relationship; external references split into `externalIdentifier` (cpe22Type, cpe23Type, swid, purl), `contentIdentifier` (gitoid, swh) and `externalRef`; purl gets its own `packageUrl` property; Annotation and Relationship become Elements; `FilesAnalyzed` and `LicenseInfoInFile` are removed; versions must be SemVer. "The Tag/Value, YAML, RDF/XML and Spreadsheet formats are not supported." (A.1, "Serialization Formats").
- **34 of 45 relationship types reverse direction** in the mapping (for example `DEPENDENCY_OF` becomes `dependsOn` with "from" and "to" swapped).
- **One row looks wrong (our reading).** The table marks `DYNAMIC_LINK` to `hasDynamicLink` as "Swap ... Y" but `STATIC_LINK` to `hasStaticLink` without a swap. Both 2.3 definitions run the same way ("Is to be used when SPDXRef-A dynamically links to SPDXRef-B", and "statically links to"), and so do both 3.0.1 definitions ("The `from` Element dynamically links in each `to` Element"). An importer following the table literally would reverse dynamic-link edges.
- **Two statements conflict with the normative text (our reading).** The annex says, for completeness, "'to' value is an SPDX element: No value for the completeness - uses the default", but the 3.0.1 model states no default for `completeness` (v0.1.0 §1.2). And it lists RDF/XML as not supported, while `serializations.md` lists RDF/XML among the RDF serialisations SPDX data "can be serialized in".

### 1.6 spdx3-validate 0.0.7 and the official examples

| field | value |
|---|---|
| Citation and verified URL | spdx3-validate, <https://pypi.org/project/spdx3-validate/> (repository <https://github.com/JPEWdev/spdx3-validate>); examples <https://github.com/spdx/spdx-examples>; specification example `examples/jsonld/package_sbom.json` at `spdx-spec` tag `3.0.1`. |
| Version pinned and date | spdx3-validate 0.0.7, uploaded 2026-08-10 (PyPI JSON API); `spdx-examples` at commit `08a3552c7a5348f79ae996196a5c4f99e068607e`. |
| Steward | Maintained outside the SPDX GitHub organisation; used by the SPDX specification's example workflow (spdx-spec pull request #1134, "Add spdx3-validate to examples validation workflow"). |
| What it is | A validator that runs the JSON Schema and pySHACL, then filters SHACL class errors for elements declared in an `ExternalMap`. |
| Licence | MIT (source file headers `SPDX-License-Identifier: MIT`). |
| Library record | none (tool; agent 5's scope if it is kept). |
| How checked | Installed in the scratch venv and read `core.py` and `spdx_versions.py`; ran it on 3 examples. Example files hashed (section 8). |

Findings:

- **SHACL alone rejects cross-document references.** Every `to` and `from` must have `sh:class` `Core/Element` with `sh:nodeKind sh:IRI`, so an IRI that is only referenced, not typed, in the document fails, even when the document lists it in an `ExternalMap`: plain pySHACL fails `software/example7` (5 violations) and `software/example14` (1), all on `import`ed IRIs (test T2). The SPDX spec repository removed pySHACL from its example checks for this reason: "PyShacl doesn't support external elements which will soon be added in one of the examples. It looks like spdx3-validate should be sufficient." (spdx-spec pull request #1300, merged 2025-11-03), and "pyshacl failed. It can't handle external IDs." (issue comment 3471615629, 2025-10-31).
- **How spdx3-validate copes.** It calls `pyshacl.validate(graph, shacl_graph=shacl_graph, ont_graph=shacl_graph)`, collects `externalSpdxId` values from `Core/import`, and skips `ClassConstraintComponent` violations whose value is one of them (`core.py`, `check_graph`). It also validates a merged graph of several documents when asked. Both failing examples pass with it (test T3).
- **It fetches the model from the canonical URL** (`https://spdx.org/rdf/3.0.1/spdx-model.ttl`), so it uses the served model, not the tagged one (section 1.3).

### 1.7 ISO/IEC 19770-2:2015 (SWID tags), through ISO's free XML Schema, and NIST IR 8060

| field | value |
|---|---|
| Citation and verified URL | ISO/IEC 19770-2:2015, "IT asset management, Part 2: Software identification tag" (paywalled, not read, as instructed). Its XML Schema is free from the ISO Standards Maintenance Portal: <https://standards.iso.org/iso/19770/-2/2015-current/schema.xsd> (and `.../2015/schema.xsd`). NIST IR 8060, "Guidelines for the Creation of Interoperable Software Identification (SWID) Tags", <https://nvlpubs.nist.gov/nistpubs/ir/2016/NIST.IR.8060.pdf>, CSRC page <https://csrc.nist.gov/pubs/ir/8060/final>. |
| Version pinned and date | Standard: 2nd edition, published 2015-09-30, stage 90.60 (section 1.9). XSD `<version>2.0</version>`. NIST IR 8060: "Date Published: April 2016" (CSRC), no withdrawal or supersession shown. |
| Steward | ISO/IEC JTC 1/SC 7; NIST (guidelines). |
| What it is | An XML tag that identifies one piece of software (name, version, tag creator, links, files), installed with the software. |
| Licence | XSD: "ISO and IEC grant the users of this Standard the right to use this XSD file free of charge for the purpose of implementing the present Standard." Portal: "You are permitted to use the electronic insert(s) available on this site, in their original format without any modifications for the purposes specified in their respective ISO standard(s)." NIST IR 8060: "This publication is available free of charge". |
| Library record | none (proposed stubs `iso-iec-19770-2-2015` and `nistir-8060`, section 6). |
| How checked | XSD files `2015-current` (`6af9d055…e5d4`) and `2015` (`fd214d62…695d`) parsed with Python `ElementTree`; 3 test tags validated with `xmllint` and `xmlschema` (test T13); NIST IR 8060 PDF `9aff60d8…a6de8` (same as v0.1.0) read with `pdftotext`. |

Findings:

- **What the XSD requires.** `SoftwareIdentity` requires `name` and `tagId` (both `xs:string`); `version` is optional with default "0.0", `versionScheme` defaults to "multipartnumeric", `tagVersion` defaults to 0. `Entity` requires `name` and `role` (`xs:NMTOKENS`); `regid` defaults to "http://invalid.unavailable". `Link` requires `href` and `rel` (`xs:NMTOKEN`, no list of values).
- **The XSD does not enforce the tag-creator rule it describes.** The `Entity` declaration says: "This has a minOccurs of 1 because the spec declares that you must have at least a Entity with role='tagCreator'". But the element sits inside `<xs:choice maxOccurs="unbounded">` next to optional particles, so the choice can be satisfied without it: a `SoftwareIdentity` with no `Entity` at all validates with both `xmllint` and `xmlschema`, and so does one whose only entity has role `softwareCreator` (test T13).
- **Hashes and signatures are extensions.** File hashes are namespaced attributes (NIST IR 8060 examples use `SHA256:hash` with namespace `http://www.w3.org/2001/04/xmlenc#sha256`); NIST requires them in authoritative tags: "GEN-16. [Auth] Every <File> element within a <Payload> element MUST include a hash value." Signatures: "Signatures are not a mandatory part of the software identification tag standard ... If signatures are included in the software identification tag, they shall follow the W3C recommendation defining the XML signature syntax" (XSD, `xs:any` documentation).
- **Extension points.** `xs:any namespace="##other"` in `SoftwareIdentity` and `xs:anyAttribute` on base elements; NIST IR 8060 defines its own extension namespace `http://csrc.nist.gov/ns/swid/2015-extensions/1.0`.
- **A labelling oddity.** The file at `.../2015/schema.xsd` declares the target namespace `http://standards.iso.org/iso/19770/-2/2014-DIS/schema.xsd`; the `2015-current` file declares the 2015 namespace.

### 1.8 RFC 9393, Concise Software Identification Tags (CoSWID)

| field | value |
|---|---|
| Citation and verified URL | H. Birkholz, J. Fitzgerald-McKay, C. Schmidt, D. Waltermire, "Concise Software Identification Tags", RFC 9393, <https://www.rfc-editor.org/rfc/rfc9393.txt>. |
| Version pinned and date | June 2023, Proposed Standard; `updates`, `updated_by` and `obsoleted_by` empty (RFC Editor JSON); errata page: "No matching errata found" (2026-10-08). |
| Steward | IETF. |
| What it is | A CBOR encoding of SWID information defined in CDDL, "aligned with the information able to be expressed with the XML Schema definition of ISO-19770-2:2015" (§1.2). |
| Licence | IETF Trust; "Code Components extracted from this document must include Revised BSD License text" (boilerplate), which covers the CDDL. |
| Library record | none (proposed `rfc-9393`). |
| How checked | Text `6708be37…4ebc`; RFC Editor JSON; BCP 14 count with the library's `_bcp14` module: 99 (MUST 71, MUST NOT 7, SHOULD 14, SHOULD NOT 2, MAY 5). |

Findings:

- **Declares BCP 14** (§1.3, the standard boilerplate).
- **Required members:** `tag-id`, `tag-version`, `software-name`, and one or more `entity` entries (`concise-swid-tag` CDDL, §2.3). Unlike the XSD, `tag-version` is required.
- **Identity:** "The tag identifier MUST be globally unique. Failure to ensure global uniqueness can create ambiguity in tag use, since the tag-id serves as the global key for matching and lookups." and "A textual tag-id value MUST NOT contain a sequence of two underscores" (§2.3). Links can name another tag as `swid:` plus its tag-id (§2.7).
- **Text rules CDDL cannot carry (our reading):** "An entity item MUST be provided with the role of 'tag-creator' for every CoSWID tag." (§2.6) cannot be expressed by `role => one-or-more<$role>`; global uniqueness and the double-underscore rule are not in the CDDL type `text / bstr .size 16`; the hash rule "whose value MUST refer to an ID in the IANA 'Named Information Hash Algorithm Registry' with a Status of 'current' ... other hash algorithms MUST NOT be used" (§2.9.1) is typed only as `int`. Not tested with a CDDL tool.
- **Extension:** seven CDDL sockets (`$$coswid-extension`, `$$entity-extension`, `$$link-extension`, `$$software-meta-extension`, `$$resource-collection-extension`, `$$file-extension`, `$$directory-extension`, §2.2) and IANA registries (§6).
- **Encoding facts:** media type `application/swid+cbor` (CoAP content-format 258) and CBOR tag 1398229316 (§6.4, §6.5); signed tags use COSE_Sign1 (§7).
- **Registered values:** 11 link `rel` values (§4.4) and 6 entity roles: tagCreator, softwareCreator, aggregator, distributor, licensor, maintainer (§4.2).

### 1.9 ISO Open Data (deliverables metadata) and ISO stage codes

| field | value |
|---|---|
| Citation and verified URL | ISO Open Data, `iso_deliverables_metadata`: <https://isopublicstorageprod.blob.core.windows.net/opendata/_latest/iso_deliverables_metadata/csv/iso_deliverables_metadata.csv> (and `.jsonl`). Stage codes: <https://committee.iso.org/stage-codes.html>. |
| Version pinned and date | CSV `Last-Modified: Wed, 07 Oct 2026 00:41:52 GMT`; downloaded 2026-10-08; 81,585 rows. |
| Steward | ISO. |
| What it is | ISO's catalogue metadata (reference, title, edition, stage, replaces, replacedBy). |
| Licence | ODC Attribution License (ODC-By) v1.0, as recorded in v0.1.0 `sources.md` (the iso.org page was not re-fetched: it is behind a bot check). |
| Library record | none (proposed dataset record, section 6). |
| How checked | CSV `cf68a7ee…bb91`, JSONL `3d0bc2fa…ba3e`; filtered with Python `csv` for 5962, 27055, 27056, 18670, 19770, 27036-3, 18974 and title words (bill of materials, SBOM, SPDX, CycloneDX, PURL, SWHID). Stage-code page `52f0888f…f506` (iso.org itself returned HTTP 403). |

Findings:

| reference | title (ISO) | stage | meaning (ISO stage codes page) |
|---|---|---|---|
| ISO/IEC 5962:2021 | SPDX® Specification V2.2.1 | 90.92 | "International Standard to be revised"; `replacedBy` 93810 |
| ISO/IEC DIS 5962 (id 93810, edition 2, 212 pages) | SPDX® Specification V3.0 | 40.99 | "Full report circulated: DIS approved for registration as FDIS" |
| ISO/IEC DIS 27055 (id 95169) | CycloneDX Bill of Materials (BOM) specification | 40.00 | "DIS registered" |
| ISO/IEC DIS 27056 (id 95170) | Package-URL (PURL) specification | 40.00 | "DIS registered" |
| ISO/IEC 19770-2:2015 | Part 2: Software identification tag | 90.60 | review closed (v0.1.0) |
| ISO/IEC 19770-6:2024 | Part 6: Hardware identification tag | 60.60 | "International Standard published" |
| ISO/IEC 18670:2025 | SoftWare Hash IDentifier (SWHID) Specification V1.2 | 60.60 | published |

These update v0.1.0 §1, which (checked 2026-09-30) had DIS 5962 at 40.60 and CycloneDX and purl as committee drafts at 30.99 ("CD approved for registration as DIS"). The dataset gives no date for a stage change.

### 1.10 NTIA, The Minimum Elements for a Software Bill of Materials (2021)

| field | value |
|---|---|
| Citation and verified URL | US Department of Commerce (NTIA), "The Minimum Elements For a Software Bill of Materials (SBOM)", <https://www.ntia.gov/sites/default/files/publications/sbom_minimum_elements_report_0.pdf>. |
| Version pinned and date | 2021-07-12 (library record). |
| Steward | NTIA. |
| What it is | The original US baseline: 7 data fields, automation support (SPDX, CycloneDX, SWID tags) and 6 practices. |
| Licence | not checked (US government report). |
| Library record | `ntia-sbom-minimum-elements`, `summarized`; duplicate stub `ntia-2021-sbom-minimum`. |
| How checked | PDF sha256 `b0fbbe5e3c5773977df1f402eceb845c4d5715a02cde4d967e54aef51856b716` (same as the record); `pdftotext`. |

Findings:

- Data fields (§IV, table): "Supplier Name", "Component Name", "Version of the Component", "Other Unique Identifiers", "Dependency Relationship", "Author of SBOM Data", "Timestamp". Practices: "Frequency, Depth, Known Unknowns, Distribution and Delivery, Access Control, and Accommodation of Mistakes" (§I).
- §V "Recommended Data Fields": "Hash of the Component", "Lifecycle Phase", "Other Component Relationships", "License Information".
- Depth: "At a minimum, all top-level dependencies must be listed with enough detail to seek out the transitive dependencies recursively." Known Unknowns: "the default interpretation of the data should be that the data is incomplete" (§IV).
- Superseded in practice: CISA 2026 "updates and replaces" it (section 1.12).

### 1.11 CISA, Framing Software Component Transparency, third edition (2024)

| field | value |
|---|---|
| Citation and verified URL | CISA SBOM Tooling and Implementation Working Group, "Framing Software Component Transparency: Establishing a Common Software Bill of Materials (SBOM)", third edition. Record URL: <https://www.cisa.gov/sites/default/files/2024-10/SBOM%20Framing%20Software%20Component%20Transparency%202024.pdf> (HTTP 403 to `curl` on 2026-10-08); bytes fetched from the Internet Archive copy <https://web.archive.org/web/20251228151823id_/https://www.cisa.gov/sites/default/files/2024-10/SBOM%20Framing%20Software%20Component%20Transparency%202024.pdf>. |
| Version pinned and date | Third edition, dated 2024-09-03 (library record). |
| Steward | CISA working group. |
| What it is | 12 baseline attributes graded at three maturity levels, plus relationship completeness and a mapping to SPDX 3.0 and CycloneDX 1.6. |
| Licence | not checked. |
| Library record | `cisa-framing-software-component-transparency`, `summarized`. |
| How checked | Archive copy sha256 `3a204b5f6f988b5f32e635132feabc885789efc436d0756294d388f148cb3397`, identical to the library record's hash, so these are the same bytes; `pdftotext`; `grep` for maturity statements. |

Findings:

- Maturity levels: "Minimum Expected", "Recommended Practice", "Aspirational Goal" (§2.2). "If there are no maturity levels for the Attribute, the instructions presented are the minimum expected."
- Levels used in Table 2: Author Name (Min; Rec adds "identify tool(s) and version(s)"), Timestamp (Min), Type ("This Attribute is optional and considered an aspirational goal", §2.2.1.3), Primary Component, Component Name, Version, Supplier Name (Min), Unique Identifier (Min "at least one unique identifier should be declared"; Rec "list as many globally unique identifiers as available"), Cryptographic Hash (Min when available, with algorithm and object; Rec hash of the Primary Component and SHA-2), Relationship (Min "Relationships and relationship completeness declared for the Primary Component and direct Dependencies"), License and Copyright Notice (Min for the Primary Component; Asp for all).
- Completeness default: "Unknown. This is the default ... This default value implies the open-world ontological assumption." (§2.2.2.6.4).
- No practice elements: a search of the text for "accommodat", "mistake", "frequency", "distribution and delivery" and "access control" found nothing.

### 1.12 CISA and partners, 2026 Minimum Elements for a Software Bill of Materials

| field | value |
|---|---|
| Citation and verified URL | CISA, NSA, FBI and partners, "2026 Minimum Elements for a Software Bill of Materials (SBOM)". Landing page <https://www.cisa.gov/resources-tools/resources/2026-minimum-elements-software-bill-materials-sbom> (HTTP 403 to `curl`; read through the WebFetch tool, which gave the PDF link <https://www.cisa.gov/sites/default/files/2026-07/2026_cisa_sbom_minimum_elements_508c.pdf>, also 403). The bytes used here are the copy hosted by the FBI's IC3 site: <https://www.ic3.gov/CSA/2026/260729.pdf>. |
| Version pinned and date | "Publication: July 29, 2026" (cover); version history: "1.0 July 12, 2021 Initial version"; "2.0 August 22, 2025 Published draft document"; "2.1 July 29, 2026 ... updated document based on comments received in response to a request for comment on a draft" (p. 2). **Final.** |
| Steward | CISA, with NSA, FBI, ASD's ACSC, Cyber Centre, NÚKIB, ANSSI, BSI, CERT-In, ACN, METI, NCO, NIS/NCSC, KISA, NCSC-NL, NCSC-NZ, NASK, NBU (p. 2 header and p. 4 list); DG CONNECT "contributed to the drafting" without binding the Commission (p. 17, footnote 27). |
| What it is | The updated US and partner baseline: 17 data fields (8 SBOM metadata, 9 component... see below), 6 practices and processes, with definitions in Appendix A and a change log in Appendix B. 23 pages, TLP:CLEAR. |
| Licence | "TLP:CLEAR information may be distributed without restriction" (cover); copyright not otherwise stated. |
| Library record | `cisa-2026-sbom-minimum`, `stub` with empty title metadata, date, version and digest. |
| How checked | IC3 PDF sha256 `1faeda1ee6c4420a84991edf3c1d526bd3789716c41214a1139822c8ec3c3873`; `pdfinfo`: Title "2026 Minimum Elements for a Software Bill of Materials (SBOM)", Author "CISA", 23 pages, created 2026-07-28. Not byte-compared with the cisa.gov file (blocked). |

Findings:

- **Status:** "updates and replaces the Minimum Elements for a Software Bill of Materials published by the National Telecommunications and Information Administration (NTIA)" (p. 4); "The minimum elements do not create new requirements; they refine how organizations should generate and request SBOMs." (p. 7).
- **Data fields (Appendix A, Table 1):** SBOM metadata: SBOM Author, SBOM Author Signature, SBOM Data Format Name, SBOM Data Format Version, SBOM Generation Context, SBOM Timestamp, SBOM Tool Name, SBOM Tool Version, SBOM Version (9). Component data: Component Dependency Relationship, Component Hash Algorithm, Component Hash Value, Component Identifiers, Component License, Component Name, Component Producer, Component Version (8). Total 17. No field is graded: the document has no maturity levels; all are "the baseline an SBOM should meet" (p. 6).
- **Practices and processes:** Accommodation of Updates to SBOM Data, Coverage, Distribution and Delivery, Explicitly Identifying Unknown Information, Frequency, Machine-Processable Data (pp. 13 to 14). Access Control was removed and merged into Distribution and Delivery (p. 6).
- **Hash:** "The output generated from applying a cryptographic hash algorithm to an executable component artifact." and "The SBOM author should identify the algorithm using Internet Assigned Numbers Authority (IANA) Hash Function Textual Names." (pp. 11 to 12). The IANA registry has 9 names (md2, md5, sha-1, sha-224, sha-256, sha-384, sha-512, shake128, shake256; CSV fetched 2026-10-08); none of the three formats uses those strings (CycloneDX `SHA-256`, SPDX `sha256`, CoSWID integer ids), and SHA-3 and BLAKE have no IANA textual name (our reading).
- **Producer replaces supplier:** "The Component Producer element replaces the Supplier Name element from the 2021 SBOM Minimum Elements. Supplier Name has proven ambiguous in practice, particularly around distributors of software." and "Only one organization should be identified as the component producer for a given component." (pp. 10 to 11).
- **Coverage:** "An SBOM should include information for all components that make up the target software, including transitive dependencies. There is no minimum depth." and "the recipient of an SBOM should be able to conclude that a newly reported vulnerability does not affect them if the SBOM does not list the component associated with the vulnerability" (p. 13). Our reading: this is a closed-world expectation, the opposite of the 2024 framing's open-world default, and it is a practice, not a data field.
- **Unknown versus withheld:** "the SBOM author should explicitly state whether the information is unknown to the SBOM author or whether the SBOM author is withholding the information from the SBOM" (pp. 13 to 14).
- **Formats:** "Remove Software Identification (SWID) Tags from list of data formats." because "SWID tags are not a widely used SBOM data format for which multiple tools exist." (Appendix B, Automation Support); SPDX and CycloneDX are "the two data formats currently widely used" (p. 14); "organizations should avoid accepting SBOMs for new software generated in deprecated versions of any format" (p. 14).
- **Other details:** Timestamp "should adhere to RFC 9557" (p. 9); Component Name: "Data formats implementing the Component Name element should allow for multiple entries to capture alternate names." (p. 12); AI: "this document does not introduce additional elements for SBOMs for AI systems" (p. 15), pointing to a separate G7 guidance (section 1.20).

### 1.13 BSI TR-03183-2, Software Bill of Materials, version 2.1.0

| field | value |
|---|---|
| Citation and verified URL | Federal Office for Information Security (BSI), "Technical Guideline BSI TR-03183: Cyber Resilience Requirements for Manufacturers and Products, Part 2: Software Bill of Materials (SBOM)", version 2.1.0, <https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TR03183/BSI-TR-03183-2_v2_1_0.pdf?__blob=publicationFile>; landing page <https://bsi.bund.de/dok/TR-03183-en>. |
| Version pinned and date | 2.1.0, "2025-08-20" (Document History, Table 1); file `Last-Modified` 2026-07-31. The English and German landing pages (2026-10-08) both say version 2.1.0 is current. |
| Steward | BSI. |
| What it is | Formal and technical SBOM requirements in support of the EU Cyber Resilience Act; "not binding or mandatory. It cannot be used as presumption of conformity" (landing page). |
| Licence | "© Federal Office for Information Security 2023 - 2025"; reuse terms not checked. |
| Library record | none for Part 2 (Part 1 is `bsi-tr-03183-1`, `distilled`). Proposed `bsi-tr-03183-2`. |
| How checked | v2.1.0 PDF sha256 `dda0ccd9b6148571d1d12241a1618b30027f22bc15e24248fdd21a011e62845c` (37 pages); v2.0.0 `20db4a9e…ac226`; the file named `..._v2_2_0.pdf` `62818650…93cc`; landing pages read as text with every download link mapped to its label. |

Findings:

- **Uses BCP 14:** "The key words ... are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals" (§2).
- **Formats:** "A newly generated or updated SBOM MUST be in JSON- or XML-format and a valid SBOM according to one of the following specifications in one of the specified versions: CycloneDX, version 1.6 or higher; System Package Data Exchange (SPDX), version 3.0.1 or higher" and "Only officially released versions of these specifications MUST be used." (§4). Our reading: an SPDX 2.3 SBOM (what Syft writes) does not satisfy v2.1.0.
- **No vulnerabilities in an SBOM:** "An SBOM MUST NOT contain vulnerability information, because SBOM data is static with respect to software that is not changing." (§3.1).
- **Required fields** (§5.2.1, §5.2.2): for the SBOM, Creator of the SBOM (email or URL) and Timestamp; for each component, Component creator, Component name, Component version, Filename of the component, Dependencies on other components (with "the completeness of this enumeration MUST be clearly indicated"), Distribution licences, Hash value of the deployable component ("as SHA-512"), Executable property, Archive property, Structured property. **Additional** fields (MUST if they exist, §5.2.3 to §5.2.4): SBOM-URI, Source code URI, URI of the deployable form, Other unique identifiers (for example CPE or purl), Original licences. **Optional** (MAY, §5.2.5): Effective licence, Hash value of the source code, URL of the security.txt.
- **Depth:** "recursive dependency resolution MUST be performed at least for each component included in the scope of delivery on each path downward ... at least up to and including the first component that is outside the scope of delivery" (§5.1).
- **The mapping appendix is explanatory and contains invalid snippets (our reading, checked).** §8 says "While the sections 3 to 5 set normative requirements ... this section is intended to provide helpful information". Its §8.2 tables use names that are not valid SPDX 3.0.1 JSON: `externalIdentifers` (misspelt), `simpleLicensing_LicenseExpression` and `licenseExpression` (the context terms are `simplelicensing_LicenseExpression` and `simplelicensing_licenseExpression`), `binaryArtifact` as a File property (in 3.0.1 it is only an `ExternalRefType` value), `externalRefType` `SourceArtifact` (the value is `sourceArtifact`), `externalIdentifierType` `packageURL` (the value is `packageUrl`), and an instance of `software_SoftwareArtifact`, which is abstract (rejected by both validation layers: test M17). For CycloneDX it writes `"manufacturer": [{...}]`, but `manufacturer` is a single object in 1.6 and 1.7. All names checked against the 3.0.1 context and model and the 1.6.2 schema.
- **A mislabelled download (checked):** the landing-page link labelled "Version 1.1 (outdated)" points to `BSI-TR-03183-2_v2_2_0.pdf`, whose content is version 1.1 (history ends at "1.1 2023-11-28"; "CycloneDX, version 1.4 or higher"). There is no version 2.2.0.
- **BSI registers its own CycloneDX property namespace** for fields the formats lack (`bsi:component:filename`, `bsi:component:executable` and others; taxonomy at <https://github.com/BSI-Bund/tr-03183-cyclonedx-property-taxonomy>, not fetched).

### 1.14 EU Cyber Resilience Act (Regulation (EU) 2024/2847), Commission guidance and standardisation

| field | value |
|---|---|
| Citation and verified URL | Regulation (EU) 2024/2847 (Cyber Resilience Act, CRA), EUR-Lex HTML <https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202402847>. Commission guidance C(2026) 5252 (2026-07-27): <https://ec.europa.eu/newsroom/dae/redirection/document/131456> (annex) and `131455` (communication). Standardisation page <https://digital-strategy.ec.europa.eu/en/policies/cra-standardisation>. DIN draft page for prEN 40000-1-3 <https://www.din.de/en/getting-involved/standards-committees/nia/drafts/wdc-beuth:din21:404676965>. |
| Version pinned and date | OJ L of 2024-11-20, "Done at Strasbourg, 23 October 2024"; applies "from 11 December 2027. However, Article 14 shall apply from 11 September 2026 and Chapter IV (Articles 35 to 51) shall apply from 11 June 2026." (Art 71(2)). English corrigenda do not touch the SBOM text (library record `eu-cra-2024-2847`). |
| Steward | European Parliament and Council; European Commission (implementing acts, guidance). |
| What it is | EU market-access law for products with digital elements; the SBOM is part of the vulnerability-handling requirements. |
| Licence | EU legal act; reuse terms not checked. |
| Library record | `eu-cra-2024-2847`, `distilled` (its notes already record "No SBOM implementing act found as of 2026-10-02"). |
| How checked | EUR-Lex HTML sha256 `8afe9d07…7167` (hashes differ between requests; the library record's capture is `628cb514…5589`), text extracted with Python; guidance annex PDF `fe209c25…f8234` (84 pages, searched with `grep -i 'bill of materials\|SBOM'`: 0 hits); standardisation page `b1aeb7c6…b1a9`; DIN page `f81197e0…3cad`. |

Findings:

- **Definition:** "'software bill of materials' means a formal record containing details and supply chain relationships of components included in the software elements of a product with digital elements" (Art 3(39)).
- **The obligation:** manufacturers shall "identify and document vulnerabilities and components contained in products with digital elements, including by drawing up a software bill of materials in a commonly used and machine-readable format covering at the very least the top-level dependencies of the products" (Annex I, Part II, point (1)).
- **Format and elements are left to an implementing act:** "The Commission may, by means of implementing acts taking into account European or international standards and best practices, specify the format and elements of the software bill of materials referred to in Part II, point (1), of Annex I." (Art 13(24)). No such act was found: the library record's SPARQL check (2026-10-02), the Commission's CRA pages, and two web searches (2026-10-08) show none.
- **Who sees it:** technical documentation includes "the software bill of materials" (Annex VII, point 2(b)) and "where applicable, the software bill of materials, further to a reasoned request from a market surveillance authority" (Annex VII, point 8); user information only "If the manufacturer decides to make available the software bill of materials to the user" (Annex II, point 9); "Manufacturers should not be obliged to make the SBOM public." (recital 77); market surveillance authorities may request SBOMs for a Union-wide dependency assessment (Art 13(25)).
- **Guidance:** the Commission's 84-page guidance annex C(2026) 5252 (2026-07-27) does not mention the SBOM (0 hits).
- **Standards:** standardisation request M/606 (C(2025)618) asks for "a set of 41 standards in support of the CRA", including horizontal standards "on vulnerability handling" (Commission standardisation page, last update 31 July 2026). The vulnerability-handling draft is prEN 40000-1-3:2025, "Cybersecurity requirements for products with digital elements - Part 1-3: Vulnerability Handling", from CEN/CLC/JTC 13/WG 9, published by DIN as a draft with "Edition 2026-09" (DIN page). Its text is paywalled and was not read, so whether it specifies SBOM fields is unknown here.

### 1.15 FDA, Cybersecurity in Medical Devices (premarket guidance)

| field | value |
|---|---|
| Citation and verified URL | US Food and Drug Administration, "Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions", Guidance for Industry and FDA Staff, <https://www.fda.gov/media/119933/download>. |
| Version pinned and date | "Document issued on February 3, 2026." "This document supersedes ... issued June 27, 2025." (cover). Guidance history: Level 2 revisions "to align with the amendments to 21 CFR 820 (the Quality Management System Regulation (QMSR))". |
| Steward | FDA (CDRH, CBER). |
| What it is | Premarket expectations for device cybersecurity, including SBOMs. Every page is headed "Contains Nonbinding Recommendations". |
| Licence | not checked (US government). |
| Library record | `fda-premarket-cybersecurity-guidance`, `distilled` (same digest). |
| How checked | PDF sha256 `d046fa836048933e1a8795bcf2f8224bcfa08789c2f3ef6f46ae53c2eb096c54` (same as the library record), 64 pages; `grep -c -i 'cyclonedx\|spdx\|swid'`: 0. |

Findings:

- **Baseline:** "manufacturers should provide machine-readable SBOMs consistent with the minimum elements (also referred to as “baseline attributes”) identified in the October 2021 National Telecommunications and Information Administration (NTIA) Multistakeholder Process on Software Component Transparency document “Framing Software Component Transparency: Establishing a Common Software Bill of Materials (SBOM).”" (§V.A.4.b). Our reading: it points to the NTIA framing (second edition, 2021), not to the 2021 Minimum Elements report, CISA's 2024 framing or CISA 2026.
- **Two extra elements per component:** "The software level of support provided through monitoring and maintenance from the software component manufacturer (e.g., the software is actively maintained, no longer maintained, abandoned)" and "The software component’s end-of-support date." (§V.A.4.b).
- **Legal basis for cyber devices:** "For cyber devices, an SBOM is required (see section 524B(b)(3) of the FD&C Act ...)" (§V.A.4). The guidance names no format: "Industry-accepted formats of SBOMs are encouraged."; for labelling, "The SBOM should be in a machine-readable format." (§VI).
- **Vulnerabilities go beside the SBOM:** "manufacturers should also identify all known vulnerabilities associated with the device and the software components, including those identified in CISA’s Known Exploited Vulnerabilities Catalog" (§V.A.4.b).

### 1.16 OMB M-26-05

| field | value |
|---|---|
| Citation and verified URL | Office of Management and Budget, "M-26-05: Adopting a Risk-based Approach to Software and Hardware Security", <https://www.whitehouse.gov/wp-content/uploads/2026/01/M-26-05-Adopting-a-Risk-based-Approach-to-Software-and-Hardware-Security.pdf>. |
| Version pinned and date | 2026-01-23 (library record). |
| Steward | OMB. |
| What it is | Two-page memo rescinding M-22-18 and M-23-16; SBOMs become an optional contract term. |
| Licence | not checked (US government). |
| Library record | `omb-m-26-05`, `distilled` (9 statements). |
| How checked | PDF sha256 `54d5132e19ab394b20fad0fbec57a945320a7cda1918f499fb594ad9af2167ab` (same as the record); `pdftotext`; read the record's `normative.md`. |

Findings:

- "Agencies may also choose to adopt contractual terms that require a software producer to provide a current software bill of materials (SBOM) upon request." Footnote 1: "For a cloud platform, agencies adopting such a contractual term should specify that the producer must provide an SBOM of the runtime production environment upon request." (p. 1).
- It lists as references "Cybersecurity and Infrastructure Security Agency (CISA), 2025 Minimum Elements for a Software Bill of Materials (SBOM) (published in draft form on Aug. 22, 2025)" and the CISA HBOM framework (pp. 1 to 2). The draft it cites has since been finalised as CISA 2026 (section 1.12). The memo sets no SBOM elements of its own.

### 1.17 CERT-In, Technical Guidelines on SBOM, QBOM and CBOM, AIBOM and HBOM, version 2.0 (RPT-0014 S-0847)

| field | value |
|---|---|
| Citation and verified URL | Indian Computer Emergency Response Team (CERT-In), Ministry of Electronics and Information Technology, "Technical Guidelines on SBOM, QBOM & CBOM, AIBOM, HBOM", version 2.0, <https://www.cert-in.org.in/PDF/TechnicalGuidelines-on-SBOM,QBOM&CBOM,AIBOM_and_HBOM_ver2.0.pdf>. |
| Version pinned and date | "Version 2.0 Dated 09.07.2025" (page footers), i.e. 2025-07-09. |
| Steward | CERT-In (Government of India). |
| What it is | Guidelines for public-sector and essential-services software procurement, with minimum elements for SBOM (Table 5), QBOM and CBOM (Tables 8, 9), AIBOM (Table 10) and HBOM (Table 11). 66 pages. |
| Licence | not checked. |
| Library record | none (RPT-0014 canonical id `cert-in-2025-aibom-guidelines`, "not yet a record"). |
| How checked | PDF sha256 `28aa48f329114d665f8e4f8c4d2f33baf4981e29168a318e6e719c11a5ff5151`, identical to RPT-0014's recorded hash; `pdftotext`. |

Findings:

- **SBOM data fields (§4.2):** Component Name, Component Version, Component Description, Component Supplier, Component License, Component Origin, Component Dependencies, Vulnerabilities, Patch Status, Release Date, End-of-Life (EOL) Date, Criticality, Usage Restrictions, Checksums or Hashes, Comments or Notes, Author of SBOM Data, Timestamp, Executable Property, Archive Property, Structured Property, Unique Identifier (21).
- **Status of the list:** "The SBOM of the software supplied to the government and public sector organizations/departments must include the data fields mentioned in Chapter 4, section 4.2 of this document." (§7.1.4); format "should be Software Package Data eXchange (SPDX) or CycloneDX" (§7.1.5).
- **Unique identifier syntax:** "structured as 'pkg:supplier/OrganizationName/ComponentName@Version?qualifiers&subpath'" (§4.2, item 21). Our reading: this is purl-shaped but uses a `supplier` type; agent 2 should check it against the purl type registry.
- **AIBOM (Table 10)** adds model name, version, type, developer, licensing, software dependencies, ML models and algorithms, performance metrics, data source, data sets, hardware, security requirements, input, output, intended usage, out-of-scope usage, environmental impact, vulnerabilities and attestations. AIBOM definition: "a comprehensive list of components used in building, training, and deploying AI models. It typically includes hardware (such as servers, sensors, and GPUs), software (AI models, frameworks, and development tools), data sources, and any other essential elements" (§9.1).
- **QBOM and CBOM (Tables 8, 9):** QBOM for "quantum algorithms, security frameworks, and related technologies"; CBOM "an inventory of cryptographic assets, including algorithms, keys, protocols, certificates, and dependencies" (§8.1, punctuation simplified); Table 9 elements per asset type: algorithms, keys, protocols, certificates.

### 1.18 CycloneDX's other bill types (capability pages and schema structures)

| field | value |
|---|---|
| Citation and verified URL | CycloneDX capability pages: <https://cyclonedx.org/capabilities/saasbom/>, `/cbom/`, `/mlbom/` (RPT-0014 S-0827), `/obom/`, `/mbom/` (also `/sbom/`, `/hbom/` for comparison). Structures: CycloneDX 1.7.2 JSON Schema (section 1.1). |
| Version pinned and date | Pages fetched 2026-10-08; they carry no version or date. |
| Steward | OWASP CycloneDX. |
| What it is | Short descriptions of each "bill" use; all of them are the same CycloneDX schema used for different content. |
| Licence | not checked. |
| Library record | none (cite under `cyclonedx-1-7`). |
| How checked | Pages hashed (section 8) and reduced to text; schema structures read with `jq`. |

Findings (page quote, then the schema structure that carries it):

- **SaaSBOM:** "Inventory services, endpoints, and data flows and classifications that power cloud-native applications." Schema: top-level `services[]` (`provider`, `group`, `name` (required), `version`, `endpoints`, `authenticated`, `x-trust-boundary`, `trustZone`, `data[]` flows, `licenses`, nested `services`, `releaseNotes`, `properties`, `tags`, `signature`, `patentAssertions`).
- **CBOM:** "Discover, manage, and report on cryptographic assets in preparation for a quantum-safe future." Schema: component `type` `cryptographic-asset` ("A cryptographic asset including algorithms, protocols, certificates, keys, tokens, and secrets") with `cryptoProperties.assetType` in `algorithm`, `certificate`, `protocol`, `related-crypto-material`; `dependencies[].provides` for "implements" links. 1.7 restructured CBOM fields (18 crypto-related definitions or properties added or deprecated, section 2, Q8).
- **ML-BOM:** "Model and dataset transparency for security, privacy, safety and ethical considerations." Schema: component `type` `machine-learning-model` with `modelCard` (`modelParameters` with `approach`, `task`, `architectureFamily`, `modelArchitecture`, `datasets` (inline or by reference, BOM-Link allowed), `inputs`, `outputs`; `quantitativeAnalysis`; `considerations`); component `type` `data` with `data[]` of `type` `source-code`, `configuration`, `dataset`, `definition` or `other`.
- **OBOM:** "Full-stack inventory of runtime environments, configurations, and additional dependencies." No dedicated structure; it uses component types such as `operating-system`, `platform`, `container`, `device`, `data` (`configuration`), and `metadata.lifecycles` phase `operations` ("BOM produced that represents inventory that is running and operational").
- **MBOM:** "Declared and observed formulation for reproducibility throughout the product lifecycle." Schema: `formulation[]` (formula with `components`, `services`, `workflows`), which in 1.7 may describe "any referencable object within the BOM, including components, services, metadata, declarations, or the BOM itself" (`#/properties/formulation/description`).

### 1.19 SPDX 3.0.1 AI, Dataset, Build and Lite profiles

| field | value |
|---|---|
| Citation and verified URL | SPDX 3.0.1 model (section 1.3), profile pages `model/AI/AI.md`, `model/Dataset/Dataset.md`, `model/Build/Build.md`, `model/Lite/Lite.md` at tag 3.0.1, and annex `docs/annexes/spdx-lite.md` (spec tag 3.0.1). |
| Version pinned and date | 3.0.1. |
| Steward | SPDX project (AI and Dataset profiles by its AI team). |
| What it is | Profiles that add classes and properties for AI models, datasets and builds, plus a licensing-focused subset (Lite). |
| Licence | Community-Spec-1.0. |
| Library record | `spdx-3-0-1`. |
| How checked | Classes, superclasses and properties per namespace listed with rdflib from the served model; required properties from SHACL `minCount`. |

Findings:

- **AI:** class `AI/AIPackage`, a subclass of `Software/Package`, with 20 AI properties (for example `typeOfModel`, `informationAboutTraining`, `hyperparameter`, `metric`, `limitation`, `safetyRiskAssessment`, `autonomyType`, energy consumption); SHACL requires none of them; the model text requires five inherited properties (section 1.3). Model lineage uses relationship types `trainedOn` and `testedOn` ("The `from` Element has been trained on the `to` Element(s).").
- **Dataset:** class `Dataset/DatasetPackage`, a subclass of `Software/Package`, with 13 properties; SHACL requires `datasetType`.
- **Build:** class `Build/Build`, a subclass of `Core/Element` (not of Artifact), with 9 properties; SHACL requires `buildType`; it links to inputs and outputs with `hasInput`, `hasOutput`, `hasHost`, `invokedBy`.
- **Lite:** no classes or properties of its own (0 terms in the `Lite/` namespace); it is a conformance profile: "The Lite profile specifies that some properties MUST be present and some others SHOULD be present, as much as possible." (`spdx-lite.md`), for example "there MUST be at least a “downloadLocation” or “packageUrl” property". None of this is in the shapes.

### 1.20 AI-BOM sources reused from RPT-0014, and the G7 AI SBOM guidance

| field | value |
|---|---|
| Citation and verified URL | S-0705: Nocera et al., "What We Know about AIBOMs" (ACM TOSEM 2025, DOI 10.1145/3786773), reused as listed (RPT-0014 notes its abstract was not fetched; not read here either). S-0827: the CycloneDX ML-BOM page (section 1.18). S-0840: Bennet et al., "Implementing AI Bill of Materials (AI BOM) with SPDX 3.0", Linux Foundation, <https://www.linuxfoundation.org/hubfs/LF%20Research/lfr_spdx_aibom_102524a.pdf>. S-0847: CERT-In (section 1.17). New: CISA and G7 partners, "Software Bill of Materials for AI, Minimum Elements" (the title separates the two parts with a dash), announced in CISA bulletin <https://content.govdelivery.com/accounts/USDHSCISA/bulletins/416bd74>. |
| Version pinned and date | S-0840: October 2024 (file name `102524a`). G7 guidance: bulletin "sent this bulletin at 05/12/2026 09:29 AM EDT". |
| Steward | LF Research; CISA and G7 Cybersecurity Working Group. |
| What it is | S-0840: a guide to the SPDX 3.0 AI and Dataset profiles. G7: AI-specific SBOM elements "in addition to the general minimum elements". |
| Licence | not checked. |
| Library record | none (RPT-0014 canonical ids `lf-2024-spdx3-aibom`, `cyclonedx-mlbom`, `nocera-2025-aibom-mlr`); G7: none. |
| How checked | S-0840 PDF sha256 `d4d60f903d32eca183ca16a92b661dc00c017096535e61854c7b168ae54994c6`, identical to RPT-0014's hash; read Table 8. G7: the bulletin only (`d4e0bcf3…ecc4`); the guidance page on cisa.gov returned HTTP 403, and the Internet Archive copy was also a 403 page. |

Findings:

- **S-0840's mandatory-field table disagrees with the 3.0.1 model.** Its Table 8 ("Mandatory fields for AIPackage from AI Profile") lists "buildTime Required(1..1)", "downloadLocation Required(1..*)" and "suppliedBy Required(1..*)". The model has `builtTime` (not `buildTime`), does not require it for AIPackage (only DatasetPackage), and gives `downloadLocation` and `suppliedBy` a maximum of 1 (section 1.3; SHACL `maxCount 1`). RPT-0014's summary of S-0840 repeats "buildTime" as mandatory.
- **G7 guidance exists but was not read:** "Because AI systems are software systems, these recommendations should be considered in addition to the general minimum elements for an SBOM. While not exhaustive or mandatory, the supplemental minimal elements outlined in this guidance reflect the consensus of G7 experts" (CISA bulletin, 2026-05-12). Flagged for RPT-0014 and the main session (section 10).

### 1.21 Pilot output: Syft 1.52.0 CycloneDX SBOM of alpine:latest (tool observation)

| field | value |
|---|---|
| Citation | `scratchpad/pilot/alpine.cdx.json`, produced in the main session on 2026-10-08 by Syft 1.52.0 (`metadata.tools`). |
| Version pinned and date | `specVersion` 1.7, `serialNumber` `urn:uuid:dd9def15-aedf-4e87-9d42-335572c393cc`, `version` 1, `metadata.timestamp` 2026-10-08T10:31:04-07:00. |
| How checked | sha256 `057c616b81fe01be2f658eb9493c056616933b6dff9d9d98c772c9011b8fe289`; `jq` counts; validated against the 1.7.2 schema (test C0: valid). Not modified. |

Findings (used for Table 2, "Filled in practice"):

- `metadata` holds only `component`, `timestamp` and `tools`: no `authors`, `manufacturer`, `supplier`, `lifecycles`, `distributionConstraints`; no `signature`; no `compositions`.
- Components: 16 `library`, 78 `file`, 1 `operating-system`. All 16 libraries have `name`, `version`, `purl`, `cpe` (plus 65 more CPE candidates in `syft:cpe23` properties, v0.1.0), `licenses` (14 license ids, 2 expressions, none with `acknowledgement`) and `publisher` (the Alpine package maintainers, each written as a person's name and email address: one maintainer on 13 packages, another on 3; not reproduced here); none has `hashes`, `supplier`, `manufacturer` or `authors`. All 78 files have SHA-1 and SHA-256 hashes. The OS component carries `"swid": {"tagId": "alpine", ...}`.
- Dependencies: 12 entries with 24 edges; the primary component (`metadata.component`, type `container`, version `sha256:260479a1…3e2d`) has no entry, and four libraries plus the OS have no entry, so by CycloneDX's own text their dependencies are "unknown".

---

## 2. Dimension questions answered

### Dimension 1. SBOM formats

1. **How is a component named?** Settled in v0.1.0 §1.1 to §1.3; re-checked the fields used here (sections 1.1, 1.3, 1.7, 1.8 and Table 1). New: CycloneDX 2.0-dev moves every identifier into `identifiers[]` entries that name the asserting party (section 1.2); the SWID XSD types `tagId` as a plain string, and Syft wrote the non-unique tag id "alpine" (section 1.21).
2. **Hardware or firmware?** Settled in v0.1.0; agent 4 owns Table 4. New pointers: CycloneDX 2.0-dev adds hardware fields and identifier schemes (section 1.2); SPDX 3.1-RC1 adds a `Hardware` namespace (section 1.4).
3. **"A depends on B"?** Settled (v0.1.0). New: SPDX's 2.3 to 3.0 mapping reverses 34 of 45 relationship types, and its `DYNAMIC_LINK` row looks wrong (section 1.5). CycloneDX `dependsOn` still accepts only same-BOM references (section 1.1).
4. **"This list is complete"?** Settled (v0.1.0). New: the SPDX annex speaks of a completeness default that the model does not define (section 1.5); CISA 2026 now expects SBOMs to support "does not affect us" conclusions (section 1.12).
5. **Vulnerabilities (CVE, CWE)?** Settled in v0.1.0 and RPT-0005 dimension 7. New for baselines: BSI forbids vulnerability data in an SBOM; CERT-In requires a Vulnerabilities field; FDA asks for known vulnerabilities beside the SBOM (sections 1.13, 1.15, 1.17).
6. **The SPDX 3 RDF model.** *Can a document be loaded into an RDF store as it is?* Yes, with four caveats. (a) The context is remote: `https://spdx.org/rdf/3.0.1/spdx-context.jsonld` answers HTTP 301 to `spdx.github.io` with `content-type: application/ld+json` and `access-control-allow-origin: *`; rdflib 7.6.0 followed it and loaded all 9 official examples (47 to 983 triples, about 0.3 s each, test T1); PyLD 3.3.0 needed an explicit `requests` document loader, then produced the same 47 triples for the specification example, differing from rdflib only in typing plain strings as `xsd:string` (test T4). (b) The context has no `@vocab`, so a key it does not define is dropped without warning (test M9). (c) A relative `spdxId` becomes an IRI relative to the file's location (`Package1` became `file:///tmp/Package1`, test M11), and a misspelt `type` becomes a relative class IRI (`file:///tmp/software_Packge`, test M20). (d) Term IRIs are version-specific (3.0.1, 3.1, and `/3.0/` planned for 3.0.2), so a store holding several versions holds several vocabularies (section 1.4). *What does the JSON Schema check?* Structure: the exact `@context` string, the `type` of every object, known keys only (`unevaluatedProperties: false`), required properties, enumerations, and patterns for IRIs (`^(?!_:).+:.+`), timestamps and versions; it uses no `format` keyword. It cannot check that a reference points to an element of the right class. *What do the SHACL shapes check?* Class membership of referenced nodes (`sh:class`), node kind (Elements must be IRIs: test M14), cardinality (`relationshipType` 1..1, test M1; `creationInfo` 1..1, test M2), vocabularies (`sh:in`, test M3), datatypes and patterns (timestamps must be `YYYY-MM-DDThh:mm:ssZ`, test M8), and abstract classes (test M17). They cannot see keys that JSON-LD dropped, and they reject references to elements defined in other documents (test M15, M16; 2 of 9 examples). *Which rules does neither check?* The 14 "External properties restrictions", all profile-conformance rules (AI, Dataset, Licensing, Lite), the VEX not-affected "one of them MUST", the VEX relationship-type and `from`-class restrictions, "MUST NOT contain more than one SpdxDocument", and value-level rules such as a valid purl or a hash of the right length (tests M4 to M6, M12, M13, T7 to T9). For DEC-004 and ADR-0004's RDF adapter, our reading: an RDF import needs the JSON Schema step before JSON-LD expansion (to catch dropped keys and relative IRIs), a cached copy of the context and model pinned by hash, and SPDX-style handling of `ExternalMap` references.
7. **Validation in every format.** *Counts* (Python, the library's `_bcp14` regex, uppercase only): CycloneDX 1.7.2 JSON Schema: 29 keywords, all SHOULD, in 28 of 1,118 description and `meta:enum` strings (21 of them the repeated `bom-ref` sentence; 9 distinct sentences); 52 lowercase "must" in the same strings. ECMA-424 PDF: 2 (licence boilerplate) against 717 lowercase "shall" (section 1.1). SPDX 3.0.1: 0 in the 513 `rdfs:comment` literals of the model file (which hold only summaries); 15 in the 271 model Markdown files at tag 3.0.1 (MUST 11, MUST NOT 1, SHOULD 2, MAY 1; 8 in Description sections, 7 in profile-conformance sections); 23 more in the specification prose (serialisations 2, Lite annex 16, licence-expression annex 5), not counting 4 in embedded licence texts. RFC 9393: 99. *Classified samples* (test ids in section 7):

   | # | Rule as written | Where | Enforced? | Evidence |
   |---|---|---|---|---|
   | S1 | "the relationship MUST include one actionStatement" | SPDX `actionStatement.md` | yes, both layers | SHACL minCount 1, JSON Schema `required`; M7 fails both (fixed in 3.0.1, CHANGELOG #908) |
   | S2 | "one of them MUST be defined" (impactStatement or justificationType) | SPDX `VexNotAffectedVulnAssessmentRelationship.md`, `justificationType.md` | no | M6 passes both; issue #923 open |
   | S3 | "Any instance of serialization of SPDX data MUST NOT contain more than one SpdxDocument element definition." | SPDX `SpdxDocument.md` | no | M5 passes both |
   | S4 | AIPackage: "there MUST exist exactly one `/Core/Relationship` of type `hasConcludedLicense`" | SPDX `AI.md` (conformance) | no | T7: official `ai/example01` breaks it and passes; issue #522 |
   | S5 | Dataset and Licensing conformance MUSTs; Lite "minCount for `copyrightText` is 1" and others | SPDX `Dataset.md`, `Licensing.md`, `Lite.md` | no | no shapes for them (Lite namespace has 0 terms); T8 |
   | S6 | Licensing: if concluded differs from declared, "a written explanation SHOULD be provided" | SPDX `Licensing.md` | no (not machine-checkable) | no property links the two |
   | S7 | Package and File "name" minCount 1 (External properties restrictions) | SPDX `Package.md`, `File.md` | no | M4 passes both |
   | S8 | VexNotAffected "is restricted to the doesNotAffect relationship type"; "from ... must be a /Security/Vulnerability" | SPDX VexNotAffected page | no | T9 passes both |
   | S9 | "must include a reference to the SPDX global context file at the top level" | SPDX `serializations.md` | yes, by JSON Schema, more strictly than the text | `@context` `const`; M10 rejects the "additional namespace mappings" the text allows |
   | S10 | "Key names MUST be wrapped in double quotes" | SPDX `serializations.md` | yes, by any JSON parser | JSON syntax |
   | S11 | "there MUST be at least a “downloadLocation” or “packageUrl” property" | SPDX `spdx-lite.md` | no | no Lite shapes |
   | S12 | `relationshipType` 1..1, `creationInfo` 1..1, timestamp pattern | SPDX model cardinality | yes | M1, M2, M8 |
   | X1 | "Every BOM generated SHOULD have a unique serial number" | CycloneDX `serialNumber` | format only | pattern rejects `12345` (C3b); absence passes (C3) |
   | X2 | "the version of the BOM SHOULD be incremented by 1" | CycloneDX `version` | no (needs two documents) | `minimum: 1` only |
   | X3 | "the system SHOULD use the most recent version of the BOM" | CycloneDX `version` | no (consumer behaviour) | none possible |
   | X4 | "Value SHOULD not start with the BOM-Link intro 'urn:cdx:'" (21 places) | CycloneDX `refType` and every `bom-ref` | no | C2 passes; schema `$comment`: "TODO (breaking change): add a format constraint that prevents the value from starting with 'urn:cdx:'" |
   | X5 | device "SHOULD include a component for the physical hardware itself and another component of type 'firmware'" | CycloneDX `type` `meta:enum` | no | no conditional rule |
   | X6 | "If scope is not specified, 'required' scope SHOULD be assumed by the consumer" | CycloneDX `scope` | no (annotation) | `"default": "required"` does not affect validation |
   | X7 | `data` "SHOULD be specified for any component of type `data` and must not be specified for other component types" | CycloneDX `component.data` | no | C8 passes |
   | X8 | the same for `modelCard` and `machine-learning-model` | CycloneDX `modelCard` | no | C9 passes |
   | X9 | "Consumers SHOULD consider ratings in prioritization decisions" | CycloneDX `ratings` (new in 1.7.1) | no (consumer behaviour) | none possible |
   | X10 | "Every bom-ref must be unique within the BOM" | CycloneDX `bom-ref` | no | C1 passes |
   | X11 | "Must be used exclusively, either 'version' or 'versionRange', but not both." | CycloneDX `version`, `versionRange` | yes | `allOf` `not required [version, versionRange]`; C5 fails |
   | X12 | versionRange "May only be used if `.isExternal` is set to `true`" | CycloneDX `versionRange` | yes | `if`/`then`; C6 fails |
   | X13 | "For `$.metadata.component`, it must be set to `false`" | CycloneDX `isExternal` | no | C7 passes |
   | X14 | "The purl, if specified, must be valid and conform to the specification" | CycloneDX `purl` | no | plain string; C11 passes |
   | X15 | components without dependencies "must be declared as empty elements within the graph" | CycloneDX `dependency` | no (cannot be expressed per entry) | C19 passes; Syft's own output omits five such entries |
   | X16 | `dependsOn` names bom-refs "in the same BOM document" (v0.1.0) | CycloneDX `dependsOn` | no referential check | C4 passes |
   | X17 | timestamps `format: date-time` | CycloneDX `metadata.timestamp` and 31 others | only if the validator asserts `format` | C12 passes by default, fails with format checking and `rfc3339-validator` |
   | W1 | "you must have at least a Entity with role='tagCreator'" | SWID XSD comment | no | T13: tags with no Entity, or no tagCreator, validate |
   | W2 | "An entity item MUST be provided with the role of 'tag-creator'"; tag-id "MUST be globally unique" | RFC 9393 §2.6, §2.3 | no (our reading of the CDDL) | not expressible in the CDDL as written |

   *Pattern (our reading):* in all three formats the machine layer checks shape, types and vocabularies; rules that involve two objects (uniqueness, references, "one of", "exactly one per package", "not with that type"), the whole document, or the meaning of a value live only in text. SPDX is the only format with a second, graph-level layer (SHACL), and even it holds none of the profile rules.
8. **What changed, and what comes next.**
   - *CycloneDX 1.6 to 1.7 (schema diff 1.6.2 to 1.7.2):* 17 definitions added (citations, licensing, the patent family, TLP classification, related cryptographic assets, IKEv2 transform types), none removed; new fields `citations` (top level), `metadata.distributionConstraints` (TLP), `component.isExternal`, `component.versionRange`, `component.patentAssertions`, `service.patentAssertions`, `externalReferences[].properties`, `definitions.patents`, and many CBOM fields; enum additions (`hash-alg` Streebog-256 and Streebog-512; external reference types `citation`, `patent`, `patent-assertion`, `patent-family`; six protocol types; primitive `key-wrap`); no change to any `required` list; JSON Schema `deprecated` added to already-deprecated items (`component.modified`, the legacy `tools` arrays, `definitions.tool`) and to replaced CBOM fields; `formulation` widened to any referencable object. Two changes need importer code (our reading): (1) `licenseChoice` changed from "a list of licenses, or exactly one expression" (`oneOf` of two array shapes in 1.6.2) to an array whose items may each be a license or an expression with `expressionDetails` (1.7.2), so mixed and multiple expressions are now valid; (2) a component may carry `versionRange` (a `vers` string) instead of `version` when `isExternal` is true.
   - *1.7.1 and 1.7.2:* section 1.1; for a JSON importer, nothing structural.
   - *Next CycloneDX:* 2.0 (section 1.2): milestone due 2026-08-31, still open on 2026-10-08; JSON only; renamed and moved fields. Ecma: no third edition announced (Ecma ECMA-424 page; Ecma-TC54/ECMA-424 repository, last commit "Second-edition styles", 2026-08-31). ISO: DIS 27055 at 40.00.
   - *SPDX 2.3 to 3.0:* section 1.5 (identity model, agents, external references, relationships as elements with direction swaps, removed formats).
   - *SPDX 3.0 to 3.0.1:* renamed terms and a new namespace (section 1.3).
   - *SPDX 3.1:* only RC1; RC2 overdue; namespace `3.1`; Hardware, Service, SupplyChain, Operations, FunctionalSafety; relaxed AI and Dataset rules (section 1.4).
   - *ISO:* DIS 5962 (SPDX 3.0) approved for registration as FDIS (40.99); DIS 27055 (CycloneDX) and DIS 27056 (purl) registered (40.00) (section 1.9).

### Dimension 8. Minimum elements and policy baselines

1. **What does each require, and at which level?** NTIA 2021: 7 minimum fields, 3 formats, 6 practices; hash, lifecycle phase, other relationships and license "recommended" (section 1.10). CISA 2024 framing: 12 attributes at Minimum Expected, Recommended Practice or Aspirational Goal (section 1.11). CISA 2026: 17 fields and 6 practices, ungraded baseline, "do not create new requirements" (section 1.12). BSI TR-03183-2 2.1.0: required, additional (if it exists) and optional fields under BCP 14, two formats at minimum versions, and no vulnerability data (section 1.13). CRA: an SBOM in "a commonly used and machine-readable format covering at the very least the top-level dependencies", elements left to an implementing act that has not been adopted (section 1.14). FDA 2026: NTIA framing baseline plus support level and end-of-support date, nonbinding guidance on a statutory duty for cyber devices (section 1.15). OMB M-26-05: an optional contract term; no elements (section 1.16). CERT-In 2.0: 21 fields that "must" accompany software supplied to government, SPDX or CycloneDX (section 1.17). Table 2 puts them side by side.
2. **What changed from NTIA 2021 to CISA 2026?** From Appendix B: 10 new elements (SBOM Author Signature, SBOM Data Format Name, SBOM Data Format Version, SBOM Generation Context, SBOM Tool Name, SBOM Tool Version, SBOM Version, Component Hash Value, Component Hash Algorithm, Component License); Supplier Name became Component Producer; Other Unique Identifiers became Component Identifiers ("at least one", "include all"); Depth became Coverage ("no minimum depth", transitive included); Known Unknowns became Explicitly Identifying Unknown Information (unknown versus withheld); Accommodation of Mistakes became Accommodation of Updates; Automation Support became Machine-Processable Data and dropped SWID; Access Control was folded into Distribution and Delivery; Timestamp points to RFC 9557. Our reading: the biggest model-relevant shifts are the hash moving into the baseline (as the 2024 framing already did), the producer replacing the supplier, and the move from an open-world default to an expectation of full coverage.
3. **Does each format carry each element?** Table 2. In short: CycloneDX 1.7 has a field for 16 of the 17 data fields (no field-level way to say "withheld"); SPDX 3.0.1 has no field for SBOM Author Signature, SBOM Tool Version or SBOM Version; SWID/CoSWID lacks Generation Context, Tool Name and Tool Version, Component License and Producer except as an entity role, and was dropped as a format by CISA 2026.
4. **Which baselines require a hash, a supplier, a dependency depth or a completeness statement, and do our tools meet them?**

   | | Hash | Supplier or producer | Depth | Completeness statement |
   |---|---|---|---|---|
   | NTIA 2021 | recommended only | Supplier Name (min) | top-level, transitive recommended | Known Unknowns (min practice) |
   | CISA 2024 | Min when available; Rec primary component, SHA-2 | Supplier Name (Min) | direct (Min), more levels (Rec) | Min for primary and direct dependencies (supplemental attribute) |
   | CISA 2026 | yes (value and algorithm) | Component Producer | all, "no minimum depth" | Explicitly Identifying Unknown Information (practice) |
   | BSI TR-03183-2 2.1.0 | yes, SHA-512 of the deployable component | Component creator (email or URL) | through the scope of delivery plus one level | "MUST be clearly indicated" |
   | CRA | not specified | not specified | "at the very least the top-level dependencies" | not specified |
   | FDA 2026 | via NTIA framing (not a minimum there) | via NTIA framing | not specified | not specified |
   | CERT-In 2.0 | "Checksums or Hashes" | Component Supplier | Depth practice | Known Unknowns practice |

   *Our tools (Syft 1.52.0 CycloneDX of alpine:latest):* no package hash (files only); no supplier, manufacturer or author (only `publisher`); dependency edges among packages but none from the primary component; no `compositions`. So it does not meet the hash, producer or completeness elements of CISA 2026, BSI or CERT-In; it meets name, version, identifiers, license (CISA 2026), timestamp, tool and format elements (Table 2). It would fail BSI on hash (SHA-512 required), creator, filename and the three file properties.

### Dimension 9. Other bill types (composition side only)

1. **Which kinds of component does each add?**

   | Bill type | Adds | Carried by |
   |---|---|---|
   | CycloneDX SaaSBOM | services and their endpoints, data flows, trust zones | top-level `services[]` (in 2.0-dev: component `type` `service`) |
   | CycloneDX CBOM | cryptographic assets: algorithms, certificates, protocols, related material (keys, tokens) | component `type` `cryptographic-asset`, `cryptoProperties`, `provides` |
   | CycloneDX ML-BOM | machine-learning models and data (datasets, configuration, source code, definitions) | component `type` `machine-learning-model` (`modelCard`) and `data` (`data[]`) |
   | CycloneDX OBOM | running environments and configurations | existing types plus lifecycle phase `operations` |
   | CycloneDX MBOM | how things were made (workflows, tasks) | `formulation[]` (not components) |
   | SPDX AI profile | AI models | `AIPackage` (a Package) with `trainedOn`, `testedOn` |
   | SPDX Dataset profile | datasets | `DatasetPackage` (a Package) |
   | SPDX Build profile | builds (an activity, not a component) | `Build` (an Element) with `hasInput`, `hasOutput`, `hasHost`, `invokedBy` |
   | SPDX Lite profile | nothing new: a licensing-focused subset of Package fields | conformance rules only |
   | CERT-In QBOM, CBOM, AIBOM | quantum devices, cryptographic assets, AI models, datasets, compute hardware | element tables, no format |
2. **Does tmodel's Component cover them?** ARCH-0001 §3 defines Component as "A part of the system (service, container, dependency, source module)"; the proposal §0 calls it "the deployed artifact that *exists* (service, container, dependency, chip, core)". Our reading: *Services* fit Component by name (=), but their endpoints, trust zones and data flows map to the proposal's DataFlow and TrustBoundary layers, which are post-MVP. *Models* (weights files) fit Component (≈); training lineage (`trainedOn`, `modelCard.datasets`) needs an edge the draft does not have. *Datasets* are not deployed artifacts in many cases; they fit ARCH-0001's Asset ("Something worth protecting") or a DFD DataStore role better than Component, so DEC-001 has to choose. *Cryptographic assets* split: a certificate or key is closer to Asset; an algorithm or protocol is a capability a component "provides" (CycloneDX's own `provides` edge) rather than a part; Component does not cover them well. *Builds and formulation* are activities (PROV-O Activity in proposal §4), not components; the proposal puts build provenance after the MVP (§7). *OBOM* content maps to the proposal's Deployment and Environment nodes. RPT-0014 owns AI threats; RPT-0005 owns the security fields of these profiles.

---

## 3. Table cells

### Table 1. Formats at a glance

| row | CycloneDX 1.7 | SPDX 3.0.1 | SWID (ISO/IEC 19770-2:2015) with CoSWID (RFC 9393) |
|---|---|---|---|
| Version pinned | 1.7 (2025-10-21; ECMA-424 2nd ed., December 2025); patches 1.7.1 (2026-06-02) and 1.7.2 (2026-09-17), JSON Schema sha256 `73308ede…76ce`; newer: 2.0 in development (draft PR #652, milestone overdue), no 1.8 | 3.0.1 (spec 2024-12-17); served model `30ebb4af…c593` differs from the tagged model `77b058eb…a5cf8`; newer: 3.1-RC1 (2026-01-24, pre-release), 3.0.2 milestone open | SWID 2nd ed., 2015-09-30 (XSD "2015-current", version 2.0); CoSWID RFC 9393, June 2023, no errata; NIST IR 8060, April 2016 |
| Steward and standard status | OWASP CycloneDX with Ecma TC54; Ecma standard ECMA-424 2nd ed.; ISO/IEC DIS 27055 at 40.00 "DIS registered" | SPDX project, Linux Foundation; ISO/IEC 5962:2021 (SPDX 2.2.1) at 90.92 "to be revised"; ISO/IEC DIS 5962 (SPDX V3.0) at 40.99 "DIS approved for registration as FDIS" | ISO/IEC JTC 1/SC 7, International Standard, stage 90.60; CoSWID: IETF Proposed Standard |
| Encodings | JSON (JSON Schema draft-07), XML (XSD), Protocol Buffers; ECMA-424 scope names JSON | RDF model in OWL with SHACL (one Turtle file); JSON-LD with a fixed context and a JSON Schema (draft 2020-12) generated from the shapes; other RDF syntaxes allowed by the text | XML (XSD); CoSWID: CBOR defined in CDDL, `application/swid+cbor`, CBOR tag 1398229316, COSE signing |
| Element identity | `bom-ref`, unique only within one BOM (not checked by the schema); the BOM by `serialNumber` (UUID URN) + `version`; BOM-Link `urn:cdx:<serial>/<version>#<bom-ref>` accepted in 10 places, not in `dependsOn` | `spdxId`, a required IRI, global; Elements must be IRIs (SHACL `sh:nodeKind sh:IRI`); IRI pattern in the JSON Schema | `tagId`, required; "MUST be globally unique" (RFC 9393) but only `xs:string` in the XSD; entity `regid` defaults to "http://invalid.unavailable" |
| Component identifiers | `purl`, `cpe`, `swid` (object: `tagId`, `name` required), `omniborId[]`, `swhid[]`, `hashes[]` (14 algorithms); backing evidence in `evidence.identity` | `packageUrl`; `externalIdentifier[]` (`cpe22`, `cpe23`, `packageUrl`, `swid`, `gitoid`, `swhid`, and others); `contentIdentifier[]` (`gitoid`, `swhid`); `verifiedUsing` Hash (22 algorithms) | `tagId`; no purl or CPE field (NIST IR 8060 derives CPE from tag data); file hashes as namespaced XML attributes; CoSWID `hash-entry` with IANA hash ids |
| Required to name a component | `type`, `name` | `spdxId`, `creationInfo` in the machine layers; `name` too in the model text for Package and File, not enforced (test M4) | XSD: `name`, `tagId`; text also requires a tagCreator entity (not enforced, test T13); CoSWID: `tag-id`, `tag-version`, `software-name`, `entity` |
| Hardware and firmware | types `device`, `firmware`, `device-driver`, `platform`; details only as `properties` (v0.1.0 §1.1; Table 4) | purposes `device`, `firmware` only (v0.1.0 §1.2); a `Hardware` namespace appears in 3.1-RC1 | none (software only); hardware tags are ISO/IEC 19770-6:2024 (agent 4) |
| Relationships | `dependsOn`, `provides`, nested `components`, `pedigree`; same-BOM only for dependencies; other BOMs via external reference type `bom` | 59 relationship types as Elements, with lifecycle scope; `from` and `to` may name elements in other documents (`ExternalMap`) | 11 registered link `rel` values (3 about installation) plus IANA link relations; `href` may be `swid:<tag-id>`, so links cross tags |
| Completeness | `compositions[].aggregate` (10 values); empty dependency entry = none, missing entry = unknown | `completeness` on each relationship (3 values, optional, no default); `NoneElement` vs `NoAssertionElement` | none (RFC 9393 §9: a collection of tags cannot be assumed complete) |
| Vulnerability link | `vulnerabilities[].affects[].ref` (BOM-Link allowed), `cwes` integers (RPT-0005 dimension 7) | `Vulnerability` element, VEX and score relationship classes, CWE as `externalRef` type `cwe` (RPT-0005) | none in the data model (v0.1.0 §1.3) |
| Build record | `formulation[]` (any referencable object since 1.7); `metadata.lifecycles` | `Build` element (Build profile; `buildType` required) with `hasInput`, `hasOutput` | none (`tagVersion` replaces tags, not builds) |
| Extension mechanism | JSON: `properties[]` name-value pairs (132 objects are closed); XML: 61 `xs:any` and 48 `xs:anyAttribute` | Extension profile (`extension` property, `CdxPropertiesExtension`); unknown JSON keys rejected by the schema and dropped by JSON-LD | XML `xs:any ##other`, `xs:anyAttribute` (NIST IR 8060 namespace); CoSWID: 7 CDDL sockets and IANA registries |
| Licence | Schema and repository Apache-2.0; ECMA-424 text under Ecma's copyright licence, embedded software under BSD | Community Specification License 1.0; older portions CC-BY-3.0 | Standard paywalled; XSD free "for the purpose of implementing the present Standard"; RFC 9393: IETF Trust, Revised BSD for code |
| Library record | `cyclonedx-1-7` (`queued`); duplicate `ecma-424` (`stub`) | `spdx-3-0-1` (`queued`) | none (proposed `iso-iec-19770-2-2015` stub, `rfc-9393`, `nistir-8060`) |

**Candidate formats a reviewer would expect** (flagged; cells not researched are `?`):

| row | SPDX 2.3 | CycloneDX 2.0 (unreleased) | SPDX 3.1 (RC1) |
|---|---|---|---|
| Why expected | Syft writes it (pilot `alpine.spdx23.json`); ISO/IEC 5962:2021 is SPDX 2.2.1 | the next CycloneDX; drops XML and Protobuf; identity by asserting party | the next SPDX; Hardware and Service profiles |
| Version pinned | v2.3, release 2022-11-03; JSON Schema `spdx-schema.json` at tag `v2.3` (sha256 `239208b7…b89b`) | `2.0-dev` commit `f6dcf4d3` (2026-10-07) | `v3.1-RC1` (2026-01-24) |
| Encodings | JSON (draft-07), YAML, Tag/Value, RDF/XML, spreadsheet (per the 3.0 annex, which drops these) | JSON Schema 2020-12 only | as 3.0.1 |
| Required to name a component | package: `SPDXID`, `downloadLocation`, `name` (schema `required`) | `type`, `name` | ? |
| Relationships | 45 types (schema enum) | ? | ? |
| Recommendation | add as a column only if radar keeps emitting SPDX 2.3; BSI 2.1.0 no longer accepts it | track; do not pin until released | track; do not pin until final |

### Table 2. Minimum-element crosswalk

Rows are the CISA 2026 Minimum Elements (final). Codes in "Required by": **N21** NTIA 2021 (min = minimum element; rec = §V recommended); **C24** CISA framing 2024 (Min, Rec, Asp = Minimum Expected, Recommended Practice, Aspirational Goal); **C26** CISA 2026 (all elements are the ungraded baseline; "new", "major", "minor" are its own change labels); **BSI** TR-03183-2 2.1.0 (Req = required MUST, Add = MUST if it exists, Opt = MAY); **CERT** CERT-In 2.0 §4.2 field list; **FDA** 2026 guidance (via the NTIA framing baseline, plus its two extra elements); **CRA** Annex I Part II(1) (only "SBOM", "machine-readable", "top-level dependencies"). "Filled in practice" is the Syft 1.52.0 CycloneDX output of alpine:latest (section 1.21). Field paths are our closest matches unless a note cites an official mapping (CISA 2024 Table 1 or BSI §8.2).

| Element | Required by | CycloneDX 1.7 | SPDX 3.0.1 | SWID / CoSWID | Filled in practice | Notes |
|---|---|---|---|---|---|---|
| SBOM Author | N21 Author of SBOM Data (min); C24 Author Name (Min); C26 major; BSI Creator of the SBOM (Req, email or URL); CERT yes; FDA via framing | `metadata.authors[]` (persons) or `metadata.manufacturer` (organization) | `CreationInfo.createdBy` (Agent) | Entity role `tagCreator` / `tag-creator` | no (`tools[].author` "anchore" is the tool's author) | CISA 2024 maps to `metadata.authors`; BSI maps to `metadata.manufacturer` (written as an array; the schema has one object). C26: the entity "operating the tool" |
| SBOM Author Signature | N21 rec (§V signing); C24 supplemental (§2.4); C26 new; BSI none (§8.1.15 "should"); CERT none for SBOM | `signature` (JSF, enveloped; 16 objects can carry one) | none (no "signature" term in the model; sign outside the document, our reading) | XML `ds:Signature` (optional); CoSWID COSE_Sign1 (§7) | no | |
| SBOM Data Format Name | N21 automation (SPDX, CycloneDX, SWID); C26 new; BSI §4 (formats, not a field); CERT §7.1.5 | `bomFormat` (required, `"CycloneDX"`) | the `@context` value (schema `const`) (our reading) | XML namespace; CoSWID media type or CBOR tag (our reading) | yes (`CycloneDX`) | CISA 2026 drops SWID as a format |
| SBOM Data Format Version | C26 new; BSI minimum versions (CycloneDX ≥1.6, SPDX ≥3.0.1) | `specVersion` (required; no enum, test C13) | `CreationInfo.specVersion` (required, SemVer pattern) | XSD namespace year and version 2.0 (our reading); CoSWID none | yes (`1.7`) | C26: avoid deprecated format versions |
| SBOM Generation Context | N21 rec (Lifecycle Phase); C24 Type (Asp); C26 new; BSI §8.4 classification (informative); CERT §3.2 (informative) | `metadata.lifecycles[].phase` (7 values) | `Sbom.sbomType` (6 values) | tag type: corpus, primary, patch, supplemental (our reading, v0.1.0) | no | phases do not map one to one (for example CycloneDX `pre-build` vs SPDX `source`) |
| SBOM Timestamp | N21 min; C24 Min (ISO 8601); C26 minor (RFC 9557); BSI Req (UTC recommended); CERT yes | `metadata.timestamp` (`format: date-time`, asserted only on request) | `CreationInfo.created` (required, `...Z` pattern, no fractions) | none for creation (Evidence `date` only) | yes (`2026-10-08T10:31:04-07:00`) | SPDX rejects offsets and fractions (test M8); our reading: an RFC 3339 value is valid RFC 9557 |
| SBOM Tool Name | C24 Rec (under Author Name); C26 new | `metadata.tools.components[].name` | `CreationInfo.createdUsing` → Tool `name` | none (our reading) | yes (`syft`) | legacy `tools` array deprecated |
| SBOM Tool Version | C24 Rec; C26 new | `metadata.tools.components[].version` | none (Tool has no own properties; our reading: name or an `externalIdentifier`) | none | yes (`1.52.0`) | |
| SBOM Version | C26 new (may use SemVer; or an identifier per RFC 9562); BSI §3.1 (new SBOM version rules), SBOM-URI (Add) | `version` (integer ≥1) with `serialNumber` | none as a field (a new document gets a new `spdxId`; `amendedBy` can chain versions, our reading) | `tagVersion` (XSD default 0); CoSWID `tag-version` (required) | yes (`version` 1, `serialNumber` set) | N21 and C24 have no SBOM version |
| Component Producer | N21 Supplier Name (min); C24 Supplier Name (Min); C26 major (replaces supplier; one organization); BSI Component creator (Req); CERT Component Supplier, Component Origin; FDA via framing | `components[].manufacturer` or `.authors` (our reading; `.supplier` "may also be a distributor or repackager") | `Artifact.originatedBy` (BSI's mapping); `suppliedBy` is CISA 2024's mapping for Supplier | Entity role `softwareCreator` (CoSWID: SHOULD) | no (0 of 16; all 16 have `publisher` = Alpine maintainer) | our reading: `publisher` is not the producer |
| Component Dependency Relationship | N21 min; C24 Relationship (Min: primary and direct, with completeness); C26 minor; BSI Req (with completeness); CERT yes; CRA top-level dependencies | `dependencies[].dependsOn`; nested `components` for containment | `Relationship` `dependsOn`, `contains` and the link types | link `rel` `requires` (installation), `component`, `parent` | partly (12 entries, 24 edges; primary component and 5 others without entries) | BSI counts containment as dependency |
| Component Hash Value | N21 rec; C24 Min when available; C26 new ("executable component artifact"); BSI Req (deployable component, SHA-512); CERT yes | `components[].hashes[].content` (hex of 32, 40, 64, 96 or 128 digits, not tied to the algorithm: test C14) | `verifiedUsing` Hash `hashValue` (any string: test M13) | XML namespaced `hash` attribute on `File`; CoSWID `hash-value` bytes | no for packages; yes for 78 files (SHA-1, SHA-256) | primary component digest appears only as its `version` string |
| Component Hash Algorithm | C24 Min (with the object hashed); C26 new (IANA Hash Function Textual Names); BSI fixed SHA-512 | `hashes[].alg` (14 values, e.g. `SHA-256`) | Hash `algorithm` (22 values, e.g. `sha256`) | attribute namespace (e.g. `xmlenc#sha256`); CoSWID `hash-alg-id` (IANA Named Information ids) | files only | no format uses the IANA textual names (`sha-256`) verbatim |
| Component Identifiers | N21 Other Unique Identifiers (min); C24 Min (one), Rec (all); C26 major ("include all"); BSI Add (CPE, purl); CERT Unique Identifier | `purl`, `cpe`, `swid`, `omniborId[]`, `swhid[]` | `packageUrl`, `externalIdentifier[]`, `contentIdentifier[]` | `tagId` | yes (16/16 purl and CPE; OS `swid.tagId` "alpine") | CycloneDX 2.0-dev moves these into `identifiers[]` with an asserting party |
| Component License | N21 rec; C24 License (Min: primary; Asp: all); C26 new; BSI Distribution licences (Req), Original (Add), Effective (Opt); CERT yes | `components[].licenses[]` (id, name or expression; `acknowledgement` declared or concluded) | `hasDeclaredLicense`, `hasConcludedLicense` relationships | none (licensor role; link to a license document, our reading) | yes (16/16: 14 ids, 2 expressions; no acknowledgement) | BSI's three licence categories map onto declared/concluded only partly (BSI §8.1.13) |
| Component Name | N21 min; C24 Min; C26 minor (multiple entries); BSI Req; CERT yes | `name` (one string; `group` separate) | `name` (maxCount 1) | `name` (required) | yes (16/16) | none of the three has a multi-valued name (CycloneDX `aliases` exist only on release notes and workspaces) |
| Component Version | N21 min; C24 Min; C26 major ("unknown" if absent); BSI Req (SemVer or CalVer SHOULD; else file date); CERT yes | `version`, or `versionRange` for external components | `packageVersion` (0..1) | `version` (default "0.0"), `versionScheme`; CoSWID `software-version` | yes (16/16) | |
| *Practice:* Coverage | N21 Depth (min); C24 depth levels; C26 major (all, transitive, "no minimum depth"); BSI §5.1; CRA top-level at least; CERT Depth | `compositions[].aggregate` per assembly or dependency set | `completeness` per relationship | none | partly (packages listed; no completeness claim) | C26 expects closed-world reading; formats default to open-world |
| *Practice:* Explicitly Identifying Unknown Information | N21 Known Unknowns (min); C24 §2.3 Undeclared SBOM Data; C26 major (unknown vs withheld); BSI completeness MUST; CERT Known Unknowns | `aggregate` `unknown` / `not_specified`; empty vs missing dependency entries; no "withheld" value (our reading, `aggregateType` enum checked) | `noAssertion`, `NoAssertionElement`, `NoAssertionLicense`; one value for unknown and withheld | none | no | no format separates "unknown" from "withheld" per field |
| *Practice:* Accommodation of Updates to SBOM Data | N21 Accommodation of Mistakes (min); C24 none found; C26 major | same `serialNumber`, higher `version` | new document, `amendedBy` (our reading) | `tagVersion` | not applicable (one document) | |
| *Practice:* Distribution and Delivery | N21 min (with Access Control); C24 none found; C26 minor; CRA Annex II(9), Art 13(25); FDA labelling; OMB on request | `metadata.distributionConstraints.tlp` (new in 1.7); external reference type `bom` | none for TLP (0 hits in the model) | tags installed with the software (RFC 9393 §1.1) | no | |
| *Practice:* Frequency | N21 min; C24 none found; C26 minor; BSI §3.1 (one SBOM per software version, MUST) | process; `serialNumber`/`version` | process | process | not applicable | |
| *Practice:* Machine-Processable Data | N21 Automation Support (min); C24 machine-readable; C26 major; BSI §4; CRA; FDA; CERT §7.1.5 | JSON, XML, Protobuf | JSON-LD (+ RDF) | XML; CBOR | yes (CycloneDX 1.7 JSON, valid against the 1.7.2 schema) | BSI accepts SPDX only from 3.0.1, which Syft does not write |

---

## 4. Table 7 ratings

0 = absent, 1 = mentioned or weak, 2 = partial (needs extension), 3 = strong; within each source's own scope. For policy baselines, the axes rate what the baseline asks SBOM data to carry (Object model: does it name model concepts; Provenance: does it require author and time; Human review: does it require a recorded human decision; Federation: does it require global identifiers and exchange formats), and AI-grounding rates the document itself as a citable source.

| Source | Object model | Provenance | Human review | Federation | AI-grounding |
|---|---|---|---|---|---|
| CycloneDX 1.7 (composition scope) | 3: components (13 types), services, `dependencies`, nested `components`, `supplier`/`manufacturer` map to Component, `depends_on`, `composed_of`, Party edges with `=` or `≈` (Table 1) | 2: BOM-level `metadata.authors`/`manufacturer`/`timestamp`/`tools`; `citations[]` (1.7) can attribute any field with a required `timestamp`, but is optional | 2: `annotations[]` and `declarations`; no verdict field (RPT-0005) | 2: `serialNumber` UUID per BOM, but `bom-ref` is local and `dependsOn` cannot cross BOMs | 2: numbered clauses with a "Location" path per field in ECMA-424 and a versioned schema, but the schema text ("must") and the Ecma text ("shall") differ, and patch releases are not Ecma editions |
| CycloneDX 2.0-dev (unreleased) | 2: adds threat, risk, control and blueprint modules (RPT-0005) and services as components | 3: identity claims carry an asserting `party` (`identifiers[]`) | 2: not checked beyond RPT-0005 | 2: unchanged BOM identity in what was read | 1: unreleased, changing daily |
| SPDX 3.0.1 (composition scope) | 3: Package/File/Snippet `=` Component; `contains`, `dependsOn` `=` edges; `suppliedBy`/`originatedBy` `≈` Party edges; Relationship as an Element `≈` Assertion | 3: `creationInfo` (`createdBy`, `created`) required on every element, relationships included | 2: `Annotation` with `annotationType` `review` (RPT-0005) | 3: `spdxId` IRIs, cross-document `ExternalMap`; minus: version-specific namespaces | 2: stable term IRIs and per-class pages, but the served model differs from the tagged one and many rules are text only |
| SPDX 3.1-RC1 | 2: adds Hardware, Service, SupplyChain, Operations profiles (not examined in depth) | 3: as 3.0.1 | 2: as 3.0.1 | 2: new namespace, no mapping to 3.0.1 | 1: pre-release |
| SPDX diffs annex (spdx/using) | 2: maps 2.3 structures to 3.0 | 0 | 0 | 1: explains `ExternalMap` | 2: stable headings, informative, one wrong row |
| spdx3-validate 0.0.7 (tool) | 0: no model of its own | 0 | 0 | 2: validates `ExternalMap` references and merged documents | 1: errors cite SHACL shapes |
| ISO/IEC 19770-2:2015 via XSD, with NIST IR 8060 | 1: one tag per software `≈` Component; links are about installation | 2: tagCreator entity, `regid`, Evidence `date`, optional signatures | 0 | 2: `tagId` meant to be global, not enforced | 1: standard paywalled; XSD and NIST guide public |
| RFC 9393 CoSWID | 1: as SWID | 2: entity roles, signed tags | 0 | 2: global `tag-id` by rule; IANA registries | 3: public RFC, BCP 14, numbered sections, CDDL |
| ISO Open Data and stage codes | 0 | 0 | 0 | 2: ISO deliverable ids | 2: stable ids and stage codes; licence ODC-By |
| NTIA 2021 | 1: names supplier, component, version, dependency | 2: Author of SBOM Data, Timestamp | 0 | 1: other identifiers optional; three formats | 1: named elements without ids; replaced by CISA 2026 |
| CISA framing 2024 | 2: primary component, relationship kinds (included-in, heritage), completeness | 2: author, timestamp, tools (Rec) | 1: "no assertion" and redaction, no decision record | 2: unique identifiers, format mapping (Table 1) | 2: numbered sections and maturity levels |
| CISA 2026 | 2: target component, components, producer, dependency relationship | 2: author, author signature, tool name and version, timestamp, SBOM version (document level) | 1: unknown vs withheld; no decision record | 2: identifiers "include all"; 18 co-authoring agencies | 2: named elements with definitions (Appendix A), version history; no element ids |
| BSI TR-03183-2 2.1.0 | 2: logical, external, identified and referenced components; dependency includes containment | 2: creator and timestamp, component creator | 0 | 2: identifiers when they exist, referenced BOMs, two formats | 3: BCP 14, numbered sections, field tables (mapping appendix informative and partly invalid) |
| EU CRA | 1: product with digital elements, component, SBOM definition | 1: none for SBOM content | 0 | 1: "commonly used and machine-readable" | 3: stable article and annex locators, CELEX id; record `distilled` |
| Commission CRA guidance C(2026) 5252 | 0 for SBOM (0 hits) | 0 | 0 | 0 | 2: numbered paragraphs (not used here) |
| FDA 2026 guidance | 1: SBOM per device; support level and end of support per component | 1 | 1: risk assessment per known vulnerability, outside the SBOM | 1: "machine-readable", "industry-accepted formats" | 2: section numbers; nonbinding; record `distilled` |
| OMB M-26-05 | 0: inventory and SBOM on request only | 0 | 0 | 1: points to the CISA draft | 2: memo id; record `distilled` with statement ids |
| CERT-In 2.0 | 2: 21 SBOM fields plus QBOM/CBOM, AIBOM, HBOM tables | 2: Author of SBOM Data, Timestamp; attestations for QBOM and AIBOM | 1: criticality, patch status; VEX statuses | 1: purl-like but non-standard identifier syntax | 2: numbered sections and tables, dated version |
| CycloneDX capability pages | 1: name the kinds of content | 0 | 0 | 1 | 1: unversioned web pages |
| LF AI-BOM with SPDX 3.0 (S-0840) | 2: AI and Dataset profile fields explained | 1 | 0 | 2: inherits `spdxId` | 1: its mandatory-field table contradicts the model |
| G7 SBOM for AI (not read) | ? | ? | ? | ? | ? |
| Pilot Syft output (tool observation) | 2: components, dependencies, primary component | 1: timestamp and tool only | 0 | 2: purl and CPE on every package | 1: one run |

The G7 row stays `?` until the document is read (section 10).

---

## 5. Applicability to the tmodel model (candidate Table 6 rows)

Draft targets: ARCH-0001 §3 (source of truth), proposal `0.2.0-proposed.11`, LinkML draft 0.1.0. "radar today" uses the pilot Syft output (section 1.21) and v0.1.0 §4 for what tradar keeps. Every rule is a candidate, not a decision.

| Model input | CycloneDX 1.7 | SPDX 3.0.1 | radar today | Fidelity | Rule (candidate) | Lost | Routes to |
|---|---|---|---|---|---|---|---|
| Product (ARCH §3; LinkML `Product`) | `metadata.component` | `Sbom.rootElement` (and `SpdxDocument.rootElement`) | Syft: `container` "alpine", version = image digest; tradar drops it | `≈` | one Product per (producer, name); the version moves to ProductInstance | formats merge product and instance in one object | DEC-001, #15 |
| ProductInstance (proposal §1, §3b; LinkML) | `metadata.component.version`, `.hashes` | root Package `packageVersion`, `verifiedUsing` | digest only as a version string | `≈` | key by content digest when present, else by (name, version); a new `serialNumber` is a new document, not a new instance | generation context (`lifecycles`, `sbomType`) has no slot | DEC-001; agent 2 (dimension 6) |
| Component (LinkML `Component`) | `components[]` (13 types), `services[]` | Package, File, Snippet, AIPackage, DatasetPackage | 16 libraries, 78 files, 1 OS; tradar keeps only vulnerable packages | `=` for software parts; `≈` for services, models, data, crypto assets (section 2, dimension 9) | key by purl when present, plus hashes when present; keep the whole identifier set | LinkML `Component` has no slot for identifiers, type, version, hashes or licences | DEC-001, #17 |
| `composed_of` | nested `components` | `contains`, `hasOptionalComponent` | not used by Syft | `≈` | parent to child; never infer from `dependsOn` ("This is not a dependency tree", v0.1.0) | optional vs required containment | DEC-001 |
| `depends_on` | `dependencies[].dependsOn` | `dependsOn`, `hasStaticLink`, `hasDynamicLink`, `hasOptionalDependency`, `hasProvidedDependency`, `hasPrerequisite` | 24 edges among packages; none from the primary component | `≈` (SPDX finer) | from the dependent to the dependency; keep the subtype and the lifecycle scope as edge qualifiers; when importing SPDX 2.3, check direction per type (section 1.5) | CycloneDX `scope` and SPDX lifecycle scope do not map | DEC-001 |
| `uses_component` | none dedicated | `usesTool` (build or test time) | none | `none` / `≈` | do not derive until the draft defines how "uses" differs from "depends on" | | DEC-001 |
| Party + `supplied_by` (LinkML on Product only) | `component.supplier` | `Artifact.suppliedBy` | none (only `publisher`) | `≈` | one Party per canonical organisation; supplier may be a distributor | supplier vs producer ambiguity (CISA 2026) | DEC-001, R-036 |
| Party + `manufactured_by` | `component.manufacturer`, `authors` | `Artifact.originatedBy` | none | `≈` | map CISA 2026 Component Producer here; one producer per component | LinkML has `manufactured_by` only on Product, not Component | DEC-001, R-036 |
| Vulnerability + `affects` | `vulnerabilities[].affects` | VEX relationship classes | Grype JSON; tradar keeps name, version, ecosystem | cite RPT-0005 | note that BSI forbids vulnerability data in an SBOM, so vulnerabilities may arrive in a separate document | | DEC-008 |
| Assertion (LinkML) | `citations[]` (field-level, 1.7), `evidence.identity` (confidence) | every Relationship is an Element with `creationInfo` | none | `≈` | each imported fact becomes an Assertion attributed to the SBOM author and tool (document level) unless field-level provenance exists | CycloneDX facts without `citations` have only document-level provenance | DEC-001, DEC-004 |
| Review (LinkML) | `annotations[]` | `Annotation` (`review`) | none | cite RPT-0005 | | | DEC-001 |
| *Gap:* SBOM document metadata (author, signature, format name and version, tool name and version, SBOM version, serial, timestamp) | `metadata`, `bomFormat`, `specVersion`, `serialNumber`, `version`, `signature` | `CreationInfo`, `SpdxDocument` | timestamp, tool, format, serial | `none` in the draft | model the SBOM as a PROV Entity produced by an Activity of an Agent (proposal §4), our reading | 9 of 17 CISA 2026 data fields are document-level | DEC-001, DEC-002 |
| *Gap:* completeness claims | `compositions` | `completeness`, `NoneElement`, `NoAssertionElement` | none | `none` | store the claim with its scope; default to "unknown" | "none" vs "unknown" vs "withheld" | DEC-001 |
| *Gap:* identifier set | `purl`, `cpe`, `swid`, `omniborId`, `swhid`, `hashes` | `packageUrl`, `externalIdentifier`, `contentIdentifier`, `verifiedUsing` | purl and CPE (+65 CPE candidates) | `none` | keep all, each with its scheme and who asserted it (as CycloneDX 2.0-dev does) | | DEC-001, #17; agent 2 |
| *Gap:* licences | `licenses[]` | licence relationships | 16/16 | `none` | | BSI's three licence categories | DEC-001 |
| *Gap:* support level and end of support (FDA) | none in 1.7 (Ecma TC54 also publishes ECMA-428, Common Lifecycle Enumeration, not read) | `supportLevel`, `validUntilTime` | none | `none` | could feed the proposal's LifecyclePhase `end-of-support` (our reading) | | DEC-001, R-037 |
| *Gap:* build record | `formulation[]` | `Build` | none | `none` | post-MVP (proposal §7) | | DEC-001; agent 2 |
| *Gap:* other bill types | services (`trustZone`, `x-trust-boundary`, data flows); models; data; crypto assets | AIPackage, DatasetPackage | none | `≈` or `none` | services to Component plus DataFlow and TrustBoundary (post-MVP); datasets and keys may be Assets | crypto algorithms and protocols have no type | DEC-001; RPT-0014 |
| *Gap:* distribution constraints | `metadata.distributionConstraints.tlp` | none | none | `none` | | | DEC-002 |

---

## 6. Library records (Table 9 rows)

FX-1 rules: `library/docs/extraction.md` (fork). Open questions 1 to 3 in `dimensions.md` (FX-1 trigger, upstream owner, duplicates) apply to several rows.

| Source | Record id | Type | Status before → after | FX-1 artifacts | Notes |
|---|---|---|---|---|---|
| CycloneDX 1.7 / ECMA-424 2nd ed. | `cyclonedx-1-7` | spec | `queued` → FX-1 | all applicable (schema verbatim: JSON, XSD, proto); keyword reconciliation must count ISO verbal forms ("shall" 717 in the PDF), since uppercase BCP 14 gives 2 | owner Ndewedo-Newbury (open question 2); 566 pages; record should note 1.7.1 and 1.7.2 |
| ECMA-424 (duplicate) | `ecma-424` | spec | `stub` → retire into `cyclonedx-1-7` | not applicable (duplicate) | `cyclonedx-1-7` says the two are "the SAME TEXT under two publishers" (open question 3) |
| SPDX 3.0.1 | `spdx-3-0-1` | spec | `queued` → FX-1 | all applicable; schema: TTL and JSON Schema verbatim; pin both the served and the tagged model hashes; examples from `spdx-spec` and `spdx-examples` | owner Ndewedo-Newbury; mixed-case keywords (15 uppercase in the model) |
| SPDX diffs annex | none | guide | cite under `spdx-3-0-1` | not applicable | informative; one wrong row |
| SPDX 3.1 | none yet | spec | new record when final | | RC1 only |
| ISO/IEC 5962:2021 | `iso-iec-5962-2021` | spec | `queued` → stub | not applicable: paywalled | status only; duplicate `iso-iec-5962` (`stub`) to retire |
| ISO/IEC 19770-2:2015 (SWID) | proposed `iso-iec-19770-2-2015` | spec | none → stub | not applicable: paywalled (XSD free) | cited for status and the free XSD |
| RFC 9393 (CoSWID) | proposed `rfc-9393` | rfc | none → FX-1 | all applicable (CDDL verbatim; 99 BCP 14 keywords) | listed in `dimensions.md` as an FX-1 candidate |
| NIST IR 8060 | proposed `nistir-8060` | guide | none → summary | not applicable (guide) | GEN-16 and PRI-8 used |
| ISO Open Data deliverables | proposed `iso-open-data-deliverables` | dataset | none → summary | not applicable | ODC-By; date the snapshot |
| NTIA 2021 Minimum Elements | `ntia-sbom-minimum-elements` | spec | `summarized` → FX-1 (28 pages) or stub, per open question 1 | requirements and normative only (no schema) | replaced by CISA 2026; duplicate `ntia-2021-sbom-minimum` (`stub`) to retire |
| CISA framing 2024 | `cisa-framing-software-component-transparency` | spec | `summarized` → FX-1 | requirements (attribute × maturity level), normative, examples | its summary already marks it as the likeliest FX-1 candidate |
| CISA 2026 Minimum Elements | `cisa-2026-sbom-minimum` | spec | `stub` (empty metadata) → FX-1 | requirements (17 fields, 6 practices), normative; schema not applicable (no format) | fill title, date 2026-07-29, version 2.1, publisher and the IC3 copy's digest; note cisa.gov copy not byte-checked |
| BSI TR-03183-2 2.1.0 | proposed `bsi-tr-03183-2` | spec | none → FX-1 | requirements (BCP 14), normative, design notes; mapping tables as informative examples, flagged | Part 1 is `bsi-tr-03183-1` (`distilled`) |
| EU CRA | `eu-cra-2024-2847` | spec | `distilled` → no change | present | already records "no SBOM implementing act" |
| Commission CRA guidance C(2026) 5252 | proposed (the CRA record names it a candidate) | guide | none → stub | not applicable | no SBOM content |
| FDA premarket guidance | `fda-premarket-cybersecurity-guidance` | spec | `distilled` → no change | present | same digest as fetched |
| OMB M-26-05 | `omb-m-26-05` | spec | `distilled` → no change | present | cites the 2025 draft now finalised |
| CERT-In TG 2.0 | proposed `cert-in-bom-guidelines-2-0` (RPT-0014 id `cert-in-2025-aibom-guidelines`) | spec | none → summary or FX-1 (66 pages), per Phase 2 | if FX-1: requirements, normative | one record for RPT-0004 and RPT-0014 |
| LF AI-BOM with SPDX 3.0 (S-0840) | proposed `lf-2024-spdx3-aibom` (RPT-0014 id) | guide | none → summary | not applicable | note the table that contradicts the model |
| G7 SBOM for AI (2026-05-12) | proposed `g7-sbom-for-ai-2026` | spec | none → stub | not applicable until read | not read (403) |
| CycloneDX 2.0 | none yet | spec | new record when released | | |
| spdx3-validate | proposed `spdx3-validate` | tool | none → summary (agent 5) | not applicable | |

---

## 7. searches.md rows

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-08 | 1, 8, 9 | which RPT-0004 v0.1.0, RPT-0005, RPT-0014 sections, ARCH-0001 §3, proposal, LinkML draft and library records cover formats and baselines | local repository read | v0.1.0 §1; RPT-0005 `fanout-attack-composition.md` §1.6, §1.7 and `fanout-vuln-data.md` rejected-claims row on "1.7.2"; RPT-0014 S-0705, S-0827, S-0840, S-0847; records `cyclonedx-1-7`, `spdx-3-0-1`, `cisa-2026-sbom-minimum`, `eu-cra-2024-2847`, `fda-premarket-cybersecurity-guidance`, `omb-m-26-05` |
| 2026-10-08 | 1 | `gh api repos/CycloneDX/specification/{releases,tags,milestones,branches}`; release notes 1.7, 1.7.1, 1.7.2; PR #652, #680; milestone 10 | gh | 1.7.1 2026-06-02, 1.7.2 2026-09-17; 2.0 milestone overdue; no 1.8; "1.6-ECMA" milestone |
| 2026-10-08 | 1 | CycloneDX schemas at tags 1.6, 1.6.1, 1.6.2, 1.7, 1.7.1, 1.7.2, master; XSD, proto, spdx, jsf, cryptography-defs at 1.7.2; 2.0-dev schema files | curl + jq + python3 | diffs (section 2, Q8); keyword counts |
| 2026-10-08 | 1 | ECMA-424 2nd edition PDF; Ecma ECMA-424 and TC54 pages; tc54.org; `Ecma-TC54/ECMA-424` repository | curl + gh | conformance clause; "ISO/IEC number DIS 27055"; no third edition |
| 2026-10-08 | 1 | `gh api repos/spdx/spdx-spec` and `spdx/spdx-3-model` releases, tags, milestones, branches, commits; issues #522, #923, #1046, #1051, #1134, #1158; PRs #1197, #1300; issue comment 3471615629 | gh | 3.1-RC1 only; milestones overdue; pyshacl removed from example checks |
| 2026-10-08 | 1 | `spdx.org/rdf/3.0.1/` model, context; `spdx.org/schema/3.0.1/` schema; files at tag 3.0.1; tarballs of both repositories at 3.0.1 | curl | served model differs from tagged model |
| 2026-10-08 | 1 | `spdx/spdx-examples` tree; 8 SPDX 3 examples at commit `08a3552c` | gh + curl | 9 test documents with the spec example |
| 2026-10-08 | 1 | SPDX diffs annex (site redirect to `spdx/using`); 2.3 relationships chapter at `v2.3`; 2.3 JSON schema | curl + gh | 2.3 to 3.0 changes; `DYNAMIC_LINK` row |
| 2026-10-08 | 1 | SPDX 3.1-RC1 `serializations.md`, model, context; `spdx.org/rdf/3.1/spdx-context.jsonld` | curl | "strict subset of JSON-LD"; 3.1 namespace |
| 2026-10-08 | 1 | PyPI JSON for `spdx3-validate` | curl | 0.0.7 (2026-08-10) |
| 2026-10-08 | 1 | ISO Open Data CSV and JSONL (blob storage URL); `iso.org/stage-codes.html` (403); `committee.iso.org/stage-codes.html` | curl + python3 | DIS 5962 at 40.99; DIS 27055 and 27056 at 40.00 |
| 2026-10-08 | 1 | ISO Guide 69 harmonized stage codes "40.99" "40.00" DIS registered pdf | WebSearch | iso.org Guide 69 pages (blocked); used `committee.iso.org/stage-codes.html` instead |
| 2026-10-08 | 1 | cdn.standards.iteh.ai ISO Guide 69 1999 harmonized stage code sample pdf | WebSearch | no preview link found |
| 2026-10-08 | 1 | `standards.iso.org/iso/19770/-2/` portal, `2015/schema.xsd`, `2015-current/schema.xsd` | curl | free SWID XSD |
| 2026-10-08 | 1 | RFC 9393 text, JSON metadata, errata page; NIST IR 8060 PDF and CSRC page | curl | no errata; IR 8060 April 2016 |
| 2026-10-08 | 8 | CISA "2026 Minimum Elements for a Software Bill of Materials" | WebSearch | news items, IC3 PDF link |
| 2026-10-08 | 8 | CISA 2026 landing page (curl 403; WebFetch summary) and PDF link (403); IC3 copy | curl + WebFetch | publication date confirmed in the PDF |
| 2026-10-08 | 8 | CISA framing 2024 PDF (403); Internet Archive copy; NTIA 2021 PDF | curl | same hashes as the library records |
| 2026-10-08 | 8 | BSI TR-03183-2 Software Bill of Materials version 2.1 2.2 2026 pdf | WebSearch | BSI download, mirrors |
| 2026-10-08 | 8 | BSI TR-03183 English and German landing pages; PDFs v2.0.0, v2.1.0 and the file named v2_2_0 | curl + python3 | 2.1.0 current; mislabelled 1.1 file |
| 2026-10-08 | 8 | EUR-Lex CRA HTML (`OJ:L_202402847`) | curl + python3 | SBOM passages |
| 2026-10-08 | 8 | Cyber Resilience Act implementing act Article 13(24) software bill of materials format elements Commission 2026 | WebSearch | no implementing act; a snippet misattributing the SBOM duty to Article 16 (rejected) |
| 2026-10-08 | 8 | CRA standardisation request M/606 vulnerability handling prEN 40000-1-3 SBOM CEN CENELEC JTC 13 | WebSearch | DIN draft page, ibf article |
| 2026-10-08 | 8 | "have your say" Cyber Resilience Act implementing regulation "software bill of materials" format draft | WebSearch | nothing relevant |
| 2026-10-08 | 8 | Commission CRA pages (policy, standardisation, implementation (404)), guidance announcement and C(2026) 5252 PDFs; DIN prEN 40000-1-3 page; STAN4CR pages | curl + python3 | guidance has no SBOM text; prEN 40000-1-3 draft 2026-09 |
| 2026-10-08 | 8 | FDA "Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions" 2026 guidance SBOM | WebSearch | 2026-02-03 final; blog claims (partly rejected) |
| 2026-10-08 | 8 | FDA guidance PDF (`/media/119933/download`); OMB M-26-05 PDF; CERT-In v2.0 PDF; IANA hash function text names CSV | curl | hashes match library and RPT-0014 |
| 2026-10-08 | 8, 9 | G7 "Software Bill of Materials for AI" "Minimum Elements" CISA May 2026 | WebSearch | CISA bulletin, law-firm summaries |
| 2026-10-08 | 8, 9 | CISA bulletin 416bd74; cisa.gov G7 page via the Internet Archive (403) | curl | G7 guidance exists, not read |
| 2026-10-08 | 9 | CycloneDX capability pages (sbom, saasbom, cbom, hbom, mlbom, obom, mbom) | curl | page texts |
| 2026-10-08 | 9 | Linux Foundation AI-BOM landing page and PDF (S-0840) | curl + pdftotext | Table 8 vs model |

**Tool runs** (scratch venv; files in `scratchpad/fanout/agent1/`):

| id | date | command | input | result |
|---|---|---|---|---|
| T1 | 2026-10-08 | `rdflib.Graph().parse(f, format="json-ld")` | 9 SPDX 3 examples (spec 3.0.1 + 8 from `spdx-examples`) | all loaded (47 to 983 triples); no undefined keys |
| T2 | 2026-10-08 | `pyshacl.validate(g, shacl_graph=model, ont_graph=model)` with the served and the tagged model | same 9 | 7 conform; `software/example7` (5) and `example14` (1) fail `sh:class` on `import`ed IRIs; same result with both models |
| T3 | 2026-10-08 | `spdx3-validate -q --json <file>` | spec example, example7, example14, ai/example01 | all exit 0 |
| T4 | 2026-10-08 | PyLD `to_rdf` with `requests_document_loader` vs rdflib | spec example | 47 triples each; differ only in `xsd:string` typing; default PyLD loader failed ("Could not expand input") |
| T5 | 2026-10-08 | python-jsonschema (`validator_for(schema)`, with and without `FORMAT_CHECKER`) | 9 examples | 0 errors each |
| T6 | 2026-10-08 | 22 mutations M0 to M22 of the spec example through JSON Schema, JSON-LD, pySHACL and spdx3-validate's SHACL step (`scripts/spdx_mutations.py`) | spec example | M1, M2, M3, M7, M8, M8b, M14, M17, M19 fail both layers; M9, M10, M11, M20 fail only the JSON Schema; M15, M16, M22 fail only SHACL (M16 passes spdx3-validate); M4, M5, M6, M12, M13, M18, M21 pass both |
| T7 | 2026-10-08 | Python check of AI and Dataset conformance rules | 9 examples | `ai/example01` declares `ai`; both AIPackages lack `hasConcludedLicense`; its DatasetPackage lacks `releaseTime` |
| T8 | 2026-10-08 | AIPackage and DatasetPackage with only `spdxId`, `name`, `creationInfo` (+ `datasetType`) | spec example + 2 elements | JSON Schema 0 errors; SHACL conforms |
| T9 | 2026-10-08 | VexNotAffected with `relationshipType` `contains` and a Package as `from` | spec example + 1 element | JSON Schema 0 errors; SHACL conforms |
| T10 | 2026-10-08 | `Draft7Validator` with a `referencing` registry (spdx, jsf, cryptography-defs) | `alpine.cdx.json` (pilot) | valid (C0) |
| T11 | 2026-10-08 | 20 mutations C0 to C19 (`scripts/cdx_mutations.py`) | `alpine.cdx.json` | C3b, C5, C6, C15, C17, C18 fail; all others pass |
| T12 | 2026-10-08 | C12 again after `pip install rfc3339-validator` | same | `"yesterday"` now fails with format checking on |
| T13 | 2026-10-08 | `xmllint --noout --schema` and `xmlschema.validate` | 3 SWID tags: no tagCreator; no Entity; tagId "alpine" | all three valid with both validators |
| T14 | 2026-10-08 | `_bcp14` keyword counts (library `bin/_bcp14.py`, imported read-only) | CycloneDX schemas 1.6 to 1.7.2; ECMA-424 text; SPDX TTL comments, model Markdown, spec prose; RFC 9393 | section 2, Q7 |
| T15 | 2026-10-08 | rdflib `to_isomorphic` and shape-by-shape comparison | served vs tagged SPDX 3.0.1 model | not isomorphic; one shape differs (section 1.3) |
| T16 | 2026-10-08 | `jq` counts | `alpine.cdx.json` | section 1.21 |

---

## 8. sources.md rows

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| ECMA-424 2nd edition (CycloneDX 1.7), <https://ecma-international.org/wp-content/uploads/ECMA-424_2nd_edition_december_2025.pdf> (`e8c55a3a968f3ef534fbcdd891c361714d3dc303b3747464f1d554f65b04c8e1`) | spec | 1, 8, 9 | `cyclonedx-1-7` (existing) | DEC-001, DEC-002 |
| CycloneDX JSON Schema 1.7.2 (= 1.7.1, master), <https://raw.githubusercontent.com/CycloneDX/specification/1.7.2/schema/bom-1.7.schema.json> (`73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce`); at 1.7 (`df472ef4aaf593904c479293723a1a5c191d6672715c93b3c0b5c318f3914221`); 1.6 at tags 1.6 (`3e92dddbc30cf7f6a02b80f0942b1a4cfd4fb1c26f1dfc4310afa9d613cafb93`), 1.6.1 (`efc54d749e32a6e16abd19394b80b4c67d846e12c782e04505130375f94ea541`), 1.6.2 (`18f57f7482593bad9f21b4feed09084640cbeff419d62ad5090c5ceccca5b37d`) | spec (schema) | 1 | `cyclonedx-1-7` | DEC-002 |
| CycloneDX XSD 1.7.2 (`c1da1a8d42c4022c5a6decd6ba9541081fdbaa2a0715f8fbb4b825411b25cdda`), proto 1.7.2 (`c662ecc64c025732eda2df18716e3aaa09002435ecb8cfd2311cffaec8041af6`), `spdx.schema.json` (`4b345e23…b359`), `jsf-0.82.schema.json` (`8bae002c…0aae`), `cryptography-defs.schema.json` (`027b059a…5b44`) at 1.7.2 | spec (schema) | 1 | `cyclonedx-1-7` | DEC-002 |
| CycloneDX releases and milestones, <https://github.com/CycloneDX/specification/releases>, <https://github.com/CycloneDX/specification/milestones> | release notes | 1 | `cyclonedx-1-7` | DEC-002 |
| CycloneDX 2.0 draft PR #652 and `2.0-dev` schemas at `f6dcf4d33fecff511c21c4616a5a66d2b8134687`: README (`266a72f3…7f6d`), `cyclonedx-2.0.schema.json` (`c7dbb1c9…f122`), bundled (`72ffe3c4…3280`), component module (`6d893030…0975`) | spec (draft) | 1 | none (future record) | DEC-001, DEC-002 |
| Ecma ECMA-424 page (`4a058544…9f11`), Ecma TC54 page (`845a065d…e295`), tc54.org (`72037bd8…18e81`) | web page | 1 | `cyclonedx-1-7` | DEC-002 |
| SPDX 3.0.1 model (served), <https://spdx.org/rdf/3.0.1/spdx-model.ttl> (`30ebb4af2d70a9809044ef46f44cc3dc5125226d70f818a50ed2e1d5f404c593`); at tag 3.0.1 `rdf/spdx-model.ttl` (`77b058ebbea268db1ad191f54da908945d4c279110a5e28b20eae4ac201a5cf8`) | spec (model) | 1, 9 | `spdx-3-0-1` (existing) | DEC-001, DEC-002, DEC-004 |
| SPDX 3.0.1 context, <https://spdx.org/rdf/3.0.1/spdx-context.jsonld> (`c72b0928f094c83e5c127784edb1ebca2af74a104fcacc007c332b23cbc788bd`), and JSON Schema, <https://spdx.org/schema/3.0.1/spdx-json-schema.json> (`582c64e809d5b3ef9bd0c4de13a32391b47b0284a3e8d199569fb96f649234b1`) | spec (schema) | 1 | `spdx-3-0-1` | DEC-002, DEC-004 |
| SPDX spec and model source at tag 3.0.1: `spdx-spec-3.0.1.tar.gz` (`eaaed0b35382e7012834fdfa5e8218d652a3842b50c3e2236fbcf934ff133623`), `spdx-3-model-3.0.1.tar.gz` (`b3285f33a55a204ffea084abc6412fce969b971347c30390a80f0379eff9fd78`) | spec (source) | 1, 9 | `spdx-3-0-1` | DEC-002 |
| SPDX releases, milestones and issues (#522, #923, #1046, #1051, #1158; spdx-spec PRs #1197, #1300), <https://github.com/spdx/spdx-spec/releases>, <https://github.com/spdx/spdx-3-model/milestones> | release notes, issues | 1 | `spdx-3-0-1`; 3.1 future record | DEC-002, DEC-004 |
| SPDX 3.1-RC1: model (`711b44efb7bcefc05ec752cd096b8fbd3d2d487e5143aaed12025615ee840949`), context (`e57db84c9418d9ff88ff0d1901a893a4377653ea69155ad94ce6e41441f3f178`, same bytes at `spdx.org/rdf/3.1/`), `serializations.md` (`c63e297b69826614a063c7f99549bf20bbfbed0c5a3ea2c3b7044105898593eb`) | spec (pre-release) | 1 | none | DEC-002, DEC-004 |
| SPDX diffs annex, <https://github.com/spdx/using/blob/10e4b14c9cc5642aa4b4ce629e2b0560b771cf34/docs/diffs-from-previous-editions.md> (`78c7819abb63f16bb88d29ffcebfb45fe06af091ef7dce84af03e8fe42e9f163`); SPDX 2.3 relationships chapter (`e2a917031ac013422d4c2a350343682f64e917602537641b84791eb639b76f98`); SPDX 2.3 JSON Schema (`239208b7ac287b3cf5d9a9af23f9d69863971102a5e1587a27a398b43490b89b`) | guide; spec | 1 | `spdx-3-0-1` | DEC-002 |
| SPDX examples: spec `examples/jsonld/package_sbom.json` at 3.0.1 (`97f4455b30e1e69918b8ef0a696b40c6826e5c5381ab2ae871ca7424c1933b33`); `spdx-examples` at `08a3552c`: ai/example01 (`2b3765b5…f232b`), ai/example02 (`8d6075a8…88b4`), dataset/example01 (`88f6224c…dd0d`), software/example1 (`566e49a5…0fd13`), example11 (`81996577…c497b`), example13 (`968511c6…3319f`), example14 enriched (`6023d2ed…30b3`), example7-bin (`6697a208…f469`) | examples | 1 | `spdx-3-0-1` | DEC-004 |
| spdx3-validate 0.0.7, <https://pypi.org/project/spdx3-validate/0.0.7/> | tool | 1 | proposed `spdx3-validate` (agent 5) | DEC-004 |
| ISO/IEC 19770-2:2015 XSD, <https://standards.iso.org/iso/19770/-2/2015-current/schema.xsd> (`6af9d0554932102ace5c696f723c1dc4a4b1a9846908cddec67ccc0518c0e5d4`) and `.../2015/schema.xsd` (`fd214d620ef9b92696cbe3b2bf23e9aac759855b381b9066609ab9387880695d`) | spec (schema) | 1 | proposed `iso-iec-19770-2-2015` (stub) | DEC-002 |
| NIST IR 8060, <https://nvlpubs.nist.gov/nistpubs/ir/2016/NIST.IR.8060.pdf> (`9aff60d8aecab8cc6143476867a1ea8a1faf45bbed89d73492c7f77c238a6de8`) | guide | 1 | proposed `nistir-8060` | DEC-002 |
| RFC 9393, <https://www.rfc-editor.org/rfc/rfc9393.txt> (`6708be37258615edb39de76e32b11439967885d6792f4e2f0ee02de1a0864ebc`) | rfc | 1 | proposed `rfc-9393` | DEC-002 |
| ISO Open Data `iso_deliverables_metadata` CSV (`cf68a7ee4eaedc8a2a35a137a22b2f19360b8cd228935f7774e6003df8bb0b91`, file of 2026-10-07) and JSONL (`3d0bc2fa20af65f6f95a98641869304b104d182b7415287d16d8db5172ceba3e`); ISO stage codes, <https://committee.iso.org/stage-codes.html> (`52f0888f31e2786c8bf4a39f396bcda1fb600d712e072454bc4aa6e1c972f506`) | dataset | 1 | proposed `iso-open-data-deliverables` | DEC-002 |
| NTIA 2021 Minimum Elements, <https://www.ntia.gov/sites/default/files/publications/sbom_minimum_elements_report_0.pdf> (`b0fbbe5e3c5773977df1f402eceb845c4d5715a02cde4d967e54aef51856b716`) | spec | 8 | `ntia-sbom-minimum-elements` (existing) | DEC-002 |
| CISA framing 2024 (third edition), Internet Archive copy of the record URL (`3a204b5f6f988b5f32e635132feabc885789efc436d0756294d388f148cb3397`) | spec | 8 | `cisa-framing-software-component-transparency` (existing) | DEC-001, DEC-002 |
| CISA 2026 Minimum Elements v2.1, <https://www.ic3.gov/CSA/2026/260729.pdf> (`1faeda1ee6c4420a84991edf3c1d526bd3789716c41214a1139822c8ec3c3873`); landing page <https://www.cisa.gov/resources-tools/resources/2026-minimum-elements-software-bill-materials-sbom> (WebFetch only) | spec | 8 | `cisa-2026-sbom-minimum` (existing stub) | DEC-001, DEC-002 |
| IANA Hash Function Textual Names, <https://www.iana.org/assignments/hash-function-text-names/hash-function-text-names-1.csv> (`f80a6ba1caa7959b73a72bc57fce3e7d98bf4a7e64e2062b08a1f7e9f7ca5a5d`) | registry | 8 | none | DEC-002 |
| BSI TR-03183-2 v2.1.0, <https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TR03183/BSI-TR-03183-2_v2_1_0.pdf> (`dda0ccd9b6148571d1d12241a1618b30027f22bc15e24248fdd21a011e62845c`); v2.0.0 (`20db4a9e5bfe1d5168e212bd9f3c427a014b3732a061216992e30ceb365ac226`); file named v2_2_0 = v1.1 (`62818650412344c17bfbac5e1866d86416ccef61988c8c906ae7c535432f93cc`); landing pages EN (`a66fff3e…c0e5`) and DE (`8f689d9f…b7c1`) | spec | 8 | proposed `bsi-tr-03183-2` | DEC-001, DEC-002 |
| EU CRA, EUR-Lex HTML <https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202402847> (`8afe9d07ff910a1bfcf21c93abfb580cc99249e5475418d68d45fbded7483167`, varies per request) | spec (law) | 8 | `eu-cra-2024-2847` (existing) | DEC-002 |
| Commission CRA guidance C(2026) 5252: communication (`d218cd8d6663469bfc20088b05940e7bb4263353af394f2ed43898e85951f2d5`), annex (`fe209c250e3d1f7599e42826d91963666951332927edcf511a2e79fe8d2f8234`); CRA standardisation page (`b1aeb7c6db9d75683da2ce8a449b5b465d269642af9f09ee1f777359eab8b1a9`); DIN prEN 40000-1-3 page (`f81197e0f6ce1e5d47d9a817519e937cb796dff3139586811b33480c49885cad`) | guide; status pages | 8 | proposed stub (guidance); none | DEC-002 |
| FDA premarket cybersecurity guidance, <https://www.fda.gov/media/119933/download> (`d046fa836048933e1a8795bcf2f8224bcfa08789c2f3ef6f46ae53c2eb096c54`) | spec (guidance) | 8 | `fda-premarket-cybersecurity-guidance` (existing) | DEC-001, DEC-002 |
| OMB M-26-05 (`54d5132e19ab394b20fad0fbec57a945320a7cda1918f499fb594ad9af2167ab`) | spec (policy) | 8 | `omb-m-26-05` (existing) | DEC-002 |
| CERT-In Technical Guidelines v2.0 (`28aa48f329114d665f8e4f8c4d2f33baf4981e29168a318e6e719c11a5ff5151`), RPT-0014 S-0847 | spec (guideline) | 8, 9 | proposed `cert-in-bom-guidelines-2-0` | DEC-001, DEC-002 |
| CycloneDX capability pages: saasbom (`204edd8e…b5c`), cbom (`1f6deeaf…b6c`), mlbom (`b47aa891…06b`, RPT-0014 S-0827), obom (`c4f3a7f0…be`), mbom (`43e7d637…d8a`), sbom (`4d34acfb…11b`), hbom (`bca41ee8…680`) | web page | 9 | `cyclonedx-1-7` | DEC-001 |
| LF "Implementing AI BOM with SPDX 3.0", RPT-0014 S-0840 (`d4d60f903d32eca183ca16a92b661dc00c017096535e61854c7b168ae54994c6`) | guide | 9 | proposed `lf-2024-spdx3-aibom` | DEC-001 |
| CISA bulletin on the G7 SBOM for AI guidance, <https://content.govdelivery.com/accounts/USDHSCISA/bulletins/416bd74> (`d4e0bcf32484e2b485c365d390d768cfcdc2a82bffa3e29d6305a0a08ffcecc4`) | announcement | 9 | proposed `g7-sbom-for-ai-2026` (stub) | DEC-001 |
| RPT-0014 S-0705 (Nocera et al., TOSEM 2025), reused as listed, not read | survey | 9 | none | none |
| Pilot `alpine.cdx.json` (Syft 1.52.0, 2026-10-08) (`057c616b81fe01be2f658eb9493c056616933b6dff9d9d98c772c9011b8fe289`) | tool output | 8 | none | DEC-002 |

---

## 9. Rejected claims

| what | where it came from | why rejected |
|---|---|---|
| "No separate 1.7.2 release was verified, so the record is '1.7 (master file)'." | RPT-0005 `fanout-vuln-data.md`, rejected-claims table | GitHub lists releases and tags 1.7.1 (2026-06-02) and 1.7.2 (2026-09-17). The confusion is understandable: the JSON Schema at 1.7.2 is byte-identical to 1.7.1 and to `master`, so the file is all three. |
| "the JSON changes are editorial" (1.7.1 and 1.7.2) | RPT-0005 `fanout-attack-composition.md` §1.7 | Refined, not wrong: no structural change, but 1.7.1 added a new uppercase SHOULD sentence to `ratings`, and 1.7.2 made no JSON change at all. |
| "ISO/IEC CD 27055 ... a committee draft at stage 30.99" and "ISO/IEC DIS 5962 ... stage 40.60" | v0.1.0 §1 (checked 2026-09-30) | Out of date: the 2026-10-07 ISO Open Data file shows DIS 27055 at 40.00, DIS 27056 at 40.00 and DIS 5962 at 40.99. |
| A Package "needs only three things: an `spdxId`, a `name` and a `creationInfo`" | v0.1.0 §1.2 | Needs a qualifier: `name` is required by the model text (`Package.md`) but not by the SHACL shapes or the JSON Schema (test M4). |
| "Article 16 of the CRA establishes the SBOM as a mandatory regulatory requirement" | web-search result summary (CRA implementing-act query) | Article 16 is "Establishment of a single reporting platform" (EUR-Lex text). The SBOM duty is Annex I Part II(1), applied through Article 13. |
| "The 2026 final guidance sets binding expectations for SBOM, VEX, threat modeling..." and the SBOM "format being machine-readable (CycloneDX or SPDX)" | web-search result summary (FDA query) | Every page of the guidance says "Contains Nonbinding Recommendations"; the guidance names no format (0 hits for CycloneDX, SPDX or SWID). The SBOM duty for cyber devices is statutory (FD&C Act 524B(b)(3)). |
| "presented as final guidance" (CISA 2026) | WebFetch summary of the cisa.gov page | Not relied on as such: the final status was confirmed from the PDF's own version history ("2.1 July 29, 2026"). |
| "buildTime Required(1..1)", "downloadLocation Required(1..*)", "suppliedBy Required(1..*)" for AIPackage | LF AI-BOM guide (S-0840), Table 8; repeated in RPT-0014's S-0840 summary | The SPDX 3.0.1 property is `builtTime`, required by the model text only for DatasetPackage; `downloadLocation` and `suppliedBy` have a maximum of 1 (model and SHACL). |
| BSI TR-03183-2 §8.2 mapping snippets as usable SPDX 3.0.1 or CycloneDX JSON | BSI TR-03183-2 2.1.0 | Several names are not valid (section 1.13) and the appendix is explanatory by its own statement. |
| A BSI TR-03183-2 version 2.2.0 | BSI landing page file name `BSI-TR-03183-2_v2_2_0.pdf` | The file contains version 1.1 (2023-11-28) and is labelled "Version 1.1 (outdated)"; both landing pages say 2.1.0 is current. |
| `DYNAMIC_LINK` to `hasDynamicLink` needs "from" and "to" swapped | SPDX diffs annex (spdx/using) | Both the 2.3 and 3.0.1 definitions run from the linking element to the linked one, as `STATIC_LINK` does (our reading; section 1.5). |
| The file at `https://spdx.org/rdf/3.0.1/spdx-model.ttl` is the tagged 3.0.1 artifact | implied by the specification's link | The served graph differs from the tag's (section 1.3). Both are kept, with hashes. |
| The SWID XSD enforces at least one `Entity` (with role tagCreator) | the XSD's own comment | Two validators accept a tag with no `Entity` (test T13). |
| "Formal registration is optional" read as a normative OPTIONAL | CycloneDX descriptions | Not a claim we rely on; noted because 1.6's uppercase "OPTIONAL" was lowercased in 1.6.1, so keyword counts differ by version. |

---

## 10. Open items, and notes for other agents

**Open items.**

1. The G7 "Software Bill of Materials for AI" minimum elements (2026-05-12) were not read (cisa.gov and the Internet Archive copy returned HTTP 403). Its Table 7 row is `?`. Fetch it through a browser or another mirror; it bears on dimension 9 and on RPT-0014.
2. The CISA 2026 PDF was taken from the FBI's IC3 site; the cisa.gov file was not byte-compared (blocked).
3. prEN 40000-1-3 (CRA vulnerability handling) is paywalled; whether it defines SBOM fields is unknown.
4. CDDL validation of the CoSWID rules (W2) was by reading, not with a CDDL tool.
5. The licences of the policy documents (CISA, NTIA, BSI, CERT-In, FDA, OMB) were not checked; none is needed for Table 1.
6. CycloneDX 2.0-dev and SPDX 3.1-RC1 were read only for importer-relevant changes; both are moving targets.
7. ECMA-428 (Common Lifecycle Enumeration, listed on tc54.org) may answer FDA's end-of-support element; not read.

**Suggestions for `dimensions.md`.**

- Table 2: CISA 2026 is final, so its 17 data fields and 6 practices are the rows (done here). Add BSI TR-03183-2 2.1.0 and CERT-In 2.0 to "Required by" as dimension 8's "other baselines", and FDA through the NTIA framing.
- Table 1: add a "Validation layers" row (what the machine layer checks and what stays text), since Q7 found it differs sharply between the formats; and decide on the candidate columns (SPDX 2.3 because Syft emits it; CycloneDX 2.0 and SPDX 3.1 when released).
- Phase 4, item 3 ("count the source's normative keywords first"): for ECMA-424 the count must use ISO verbal forms (shall, should, may, can), because the uppercase BCP 14 count is 2 and both are boilerplate. The same will apply to SPDX 3.1, which moved to "shall".
- Table 6 starting rows: the LinkML `Component` has no identifier, version, hash or licence slot, and `manufactured_by` and `supplied_by` sit only on Product; these are the first gaps any import hits.

**Notes for other agents.**

- *Agent 2 (identifiers, build identity):* Syft writes `"swid": {"tagId": "alpine"}` for the OS component, which cannot meet RFC 9393's "MUST be globally unique". CERT-In's identifier syntax "pkg:supplier/OrganizationName/ComponentName@Version?qualifiers&subpath" uses a `supplier` purl type. CycloneDX 2.0-dev replaces `purl`, `cpe` and the rest with `identifiers[]` naming the asserting party, with 25 schemes. CISA 2026 asks for all identifiers and for hashes named by IANA textual names, which none of the formats uses. ISO/IEC DIS 27056 (purl) is at 40.00.
- *Agent 3 (bridge):* BSI TR-03183-2: "An SBOM MUST NOT contain vulnerability information"; CERT-In requires a "Vulnerabilities" field; FDA asks for known vulnerabilities, including KEV, beside the SBOM. CycloneDX 2.0-dev has a `weakness` module and an `2.0-dev-epss` branch.
- *Agent 4 (hardware and firmware):* CycloneDX 2.0-dev adds component fields `boardLocation`, `deviceType`, `quantity`, `leadTime`, `materialForm`, `origins`, `certifications`, a `physical` module and hardware identifier schemes (GTIN, MPN, serial number, MAC address, IMEI, UDI). SPDX 3.1-RC1 has a `Hardware` namespace (class `Hardware/Hardware`, `VirtualHardwareModelType`). `spdx-examples` has a `hardware/` folder. CERT-In 2.0 has an HBOM table (Table 11). BSI TR-03183-H is about conformity "Module H", not hardware. ISO/IEC 19770-6:2024 is at 60.60.
- *Agent 5 (tools and radar):* spdx3-validate 0.0.7 is what the SPDX spec repository uses; plain pySHACL rejects cross-document references. python-jsonschema does not assert `format` by default and needs `rfc3339-validator` for `date-time`. The Syft 1.52.0 CycloneDX output validates against the 1.7.2 schema but leaves 5 non-file components and the primary component without dependency entries. BSI 2.1.0 accepts SPDX only from 3.0.1, which Syft does not write.
- *Main session and RPT-0014:* the G7 AI SBOM guidance (open item 1); SPDX pull request #1158 drops most AI and Dataset requirements in 3.1, so RPT-0014's AI-BOM field lists will age; RPT-0014's S-0840 summary repeats the "buildTime" error.
- *Library (Phase 2):* `cisa-2026-sbom-minimum` needs its metadata filled; `ecma-424`, `ntia-2021-sbom-minimum` and `iso-iec-5962` duplicate other records.
