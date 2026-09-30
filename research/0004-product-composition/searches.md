---
schema: "archdoc/v1"
id: RPT-0004-searches
title: "RPT-0004 search log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-30"
record: RPT-0004
---

# RPT-0004: search log

Every query run, so the survey is reproducible. One row per query.

| date | dimension | query | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-09-28 | 1 | CycloneDX Authoritative Guide SBOM HBOM guides cyclonedx.org | web (via Claude Code) | OWASP CycloneDX Authoritative Guide to SBOM; cyclonedx.org/guides |

## Tool runs

| date | command | input | result |
|---|---|---|---|
| 2026-09-28 | `syft alpine:latest -o cyclonedx-json` (Syft 1.52.0) | alpine:latest | CycloneDX 1.7; 16 packages, 78 files, 1 OS; no package hashes, no `compositions`, no `vulnerabilities` |
| 2026-09-28 | `trivy sbom alpine.cdx.json` (Trivy 0.74.0) | Syft SBOM above | 0 CVEs; warns "Third-party SBOM may lead to inaccurate vulnerability detection" |
| 2026-09-28 | `grype alpine.cdx.json` (Grype 0.119.0) | Syft SBOM above | 4 matches = 2 distinct CVEs (busybox CVE counted 3x via origin package); 0 fixed |
| 2026-09-28 | `grype alpine.cdx.json -o json`| Syft SBOM above | all 4 matches are `cpe-match` against `nvd:cpe`; `cwes` present: CWE-787 (zlib), CWE-284 (busybox) | 
| 2026-09-28 | `grype alpine.cdx.json -o cyclonedx-json` | Syft SBOM above | same 4 matches; `cwes` field empty |
| 2026-09-30 | `jq '.definitions.component.required' bom-1.7.schema.json` | CycloneDX 1.7 JSON schema (see sources.md) | `["type","name"]`: the only required component fields (§1.1 Naming) |
| 2026-09-30 | `jq '.definitions.componentIdentityEvidence.properties.field.enum' bom-1.7.schema.json` | same | `group`, `name`, `version`, `purl`, `cpe`, `omniborId`, `swhid`, `swid`, `hash`: the spec's identity fields (§1.1 Naming) |
| 2026-09-30 | `jq '[paths \| map(tostring) \| join(".") \| select(test("cwe";"i"))]' bom-1.7.schema.json` | same | every match is under `definitions.cwe` or `vulnerability.cwes`: no other place for a CWE (§1.1 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.dependency.properties.dependsOn.items, .definitions.vulnerability.properties.affects.items.properties.ref.anyOf' bom-1.7.schema.json` | same | `dependsOn` accepts only `refLinkType` (same file); `affects.ref` also accepts `bomLinkElementType` (BOM-Link) (§1.1 Dependencies, Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.vulnerability.properties.analysis \| {required, allOf, if}' bom-1.7.schema.json` | same | all `null`: no rule requires a `justification` for `not_affected` (§1.1 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.scoreMethod.enum' bom-1.7.schema.json` | same | CVSSv2, CVSSv3, CVSSv31, CVSSv4, OWASP, SSVC, other (§1.2 Vulnerabilities) |
| 2026-09-30 | `jq '[paths(type == "string" and test("EPSS\|Known Exploited\|exploit catalog";"i"))]' bom-1.7.schema.json` | same | `[]`: no EPSS or exploit-catalog field (§1.2 Vulnerabilities) |
| 2026-09-30 | `shasum -a 256` | CISA Framing (3rd ed.) PDF, from the record's Source URL | `3a204b5f...cb3397`, same as the `cisa-framing-software-component-transparency` digest; the §2.2.2.5 "discontinued in 2030" sentence is on p. 14 (§1.1 Naming) |
| 2026-09-30 | `grep -o 'Core/RelationshipType/[A-Za-z]*>' spdx-model.ttl \| sort -u \| wc -l` | SPDX 3.0.1 model file (see sources.md) | 59 relationship types (§1.2 Dependencies) |
| 2026-09-30 | `grep -o 'Core/ProfileIdentifierType/[A-Za-z]*>' spdx-model.ttl \| sort -u` | same | 10 profiles: ai, build, core, dataset, expandedLicensing, extension, lite, security, simpleLicensing, software; none for hardware (§1.2 Hardware) |
| 2026-09-30 | `grep -i -c -E 'serialnumber\|macaddress\|manufacturer' spdx-model.ttl` | same | `0`: no serial number, MAC address or manufacturer term (§1.2 Hardware) |
| 2026-09-30 | `grep -o 'Core/HashAlgorithm/[A-Za-z0-9_]*>' spdx-model.ttl \| sort -u \| wc -l` | same | 22 hash algorithm values (§1.2 Naming) |
| 2026-09-30 | `grep -n -i cwe spdx-model.ttl` | same | 4 lines, all about `ExternalRefType/cwe`: CWEs are supported only as an external-reference type, with no dedicated field (§1.2 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.externalReference.properties.url.anyOf, .definitions.externalReference.properties.type."meta:enum".bom' bom-1.7.schema.json` | CycloneDX 1.7 JSON schema | an external reference's `url` may be an IRI or a BOM-Link, and type `bom` is "Bill of Materials (SBOM, OBOM, HBOM, SaaSBOM, etc)": SBOMs can be linked without a dependency (§1.1 Dependencies) |
| 2026-09-30 | `grep -o 'terms/Extension/[A-Za-z]*' spdx-model.ttl \| sort -u` | SPDX 3.0.1 model file | the Extension profile includes `CdxPropertiesExtension` (name/value pairs "intended to be compatible with" CycloneDX properties, per its spec page) (§1.2 Hardware) |
| 2026-09-30 | `grep -n -i -E 'composition\|aggregate'` on the extracted PDF text | CISA Framing (3rd ed.) PDF | no mapping of completeness to CycloneDX `compositions`/`aggregate`: the completeness tables in §1.1 and §1.2 are our alignment |
| 2026-09-30 | `for w in hardware firmware CPE purl; do grep -c -i "$w" rfc9393.txt; done` | RFC 9393 (rfc-editor.org/rfc/rfc9393.txt) | `0` for each word (§1.3 Naming, Hardware) |
| 2026-09-30 | `grep -c -i -E 'cve\|cwe\|vex\|vulnerab'` on RFC 9393 §2.10 (the full CDDL) | same | `0`: no vulnerability fields in CoSWID's data definition (§1.3 Vulnerabilities) |
| 2026-09-30 | `grep -n -i hardware` on the extracted PDF text | NIST IR 8060 PDF (nvlpubs.nist.gov), sha256 `9aff60d8...a6de8` | 2 lines, both in §5.2.3's definition of executable files (§1.3 Hardware) |
| 2026-09-30 | `curl` of iso.org/standard/65666.html | ISO/IEC 19770-2:2015 page | blocked by a bot check; the standard's current edition status could not be confirmed (§1.3) |
| 2026-09-30 | `grep -c -i` for `exploitable`, `in_triage`, `SPDX` on the extracted text | CISA "Minimum Requirements for VEX" PDF (cisa.gov; direct `curl` got HTTP 403, fetched through Claude Code's web fetch), sha256 `1e73325c...975c8` | `0`, `0`, `0`: CycloneDX appears only as a VEX-capable format; no CycloneDX or SPDX values are mapped. Defines 4 statuses and 5 justifications (§2.7.1) |
| 2026-09-30 | `jq '.definitions.metadata.properties \| keys'` and the same for `license` and `componentEvidence` | CycloneDX 1.7 JSON schema | `authors`, `timestamp`, `lifecycles`, `component`, `supplier`; license `acknowledgement` (declared, concluded) and `licensing`; evidence `licenses`, `copyright`: every CycloneDX 1.6 field in CISA's Table 1 still exists in 1.7 (comparison table) |
| 2026-09-30 | Properties tables of the CreationInfo, Sbom and Package pages | SPDX 3.0.1 spec site | `created`, `createdBy`; `sbomType`; `name`, `packageVersion`, `suppliedBy`, `verifiedUsing`, `copyrightText`, `packageUrl`: every SPDX 3.0 field in CISA's Table 1 still exists in 3.0.1 (comparison table) |
| 2026-09-30 | `sed` of `software-meta-entry` in §2.8, plus `grep -c -i` for `licens`, `copyright`, `timestamp` | RFC 9393 | no license, copyright or creation-time field; `licens` hits are the `licensor` role and license keys, `timestamp` only concerns signatures (comparison table, SWID column) |
| 2026-09-30 | the "corresponds to" / "represents" sentence on each VEX class page | SPDX 3.0.1 spec site | Affected and NotAffected "correspond to", Fixed and UnderInvestigation "represent", the VEX `affected`, `not_affected`, `fixed` and `under_investigation` statuses (comparison table) |
| 2026-09-30 | `curl` of the page, then word counts | cyclonedx.org/capabilities/vex/ (the CycloneDX page CISA cites) | `under_investigation`, `in_triage`, `not_affected`, `fixed`, `CISA`, `justification`: all `0`: no mapping to CISA's statuses |