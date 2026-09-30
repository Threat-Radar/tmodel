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