---
schema: "archdoc/v1"
id: RPT-0004-sources
title: "RPT-0004 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-30"
record: RPT-0004
---

# RPT-0004: source log

Every source found, and the `library/` record it became.

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| CycloneDX 1.7 (ECMA-424, 2nd ed.) | spec | 1, 2, 5 | `cyclonedx-1-7` (in fork via Threat-Radar/library#5; `queued`, summary still blank) | DEC-002 |
| CycloneDX 1.7 JSON reference (cyclonedx.org/docs/1.7/json/) | spec (web view) | 1, 2, 5 | same spec as `cyclonedx-1-7`; source of the quoted field descriptions | DEC-002 |
| CycloneDX 1.7 JSON schema file (CycloneDX/specification, tag `1.7`, `schema/bom-1.7.schema.json`) | spec (machine-readable) | 1 | same spec as `cyclonedx-1-7`; used for the checks in Tool runs | DEC-002 |
| CycloneDX property taxonomy, `cdx:device` namespace (github.com/CycloneDX/cyclonedx-property-taxonomy) | spec (side list) | 1, 2 | not yet a record | DEC-001, DEC-002 |
| SPDX 3.0.1 | spec | 1 | `spdx-3-0-1` (in fork via Threat-Radar/library#5; `queued`, summary still blank) | DEC-002 |
| SPDX 3.0.1 model file (spdx.org/rdf/3.0.1/spdx-model.ttl) | spec (machine-readable) | 1 | same spec as `spdx-3-0-1`; used for the checks in Tool runs | DEC-002 |
| ISO/IEC 19770-2:2015, Software identification tag (SWID) | spec | 1 | not yet a record; paywalled, not read; listed in `ntia-sbom-minimum-elements`'s references | DEC-002 |
| NIST IR 8060, Guidelines for the Creation of Interoperable Software Identification (SWID) Tags (2016) | guide | 1 | not yet a record; listed in `ntia-sbom-minimum-elements`'s references | DEC-002 |
| RFC 9393, Concise Software Identification Tags (CoSWID) | spec | 1 | not yet a record | DEC-002 |
| NTIA, Minimum Elements for an SBOM (2021) | spec | 1 | `ntia-sbom-minimum-elements` (in fork via Threat-Radar/library#5; `summarized`) | DEC-002 |
| CISA, Framing Software Component Transparency (3rd ed., 2024) | spec | 1, 6 | `cisa-framing-software-component-transparency` (in fork via Threat-Radar/library#5; `summarized`) | DEC-002 |
| gitoid URI scheme (IANA provisional registration), used by OmniBOR | spec | 1 | not yet a record | DEC-002 |
| SWHID specification (Software Heritage) | spec | 1 | not yet a record | DEC-002 |
| RFC 6149 and RFC 6150 (IETF, "MD2 to Historic Status", "MD4 to Historic Status") | spec | 1 | not yet a record | DEC-002 |
| NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) | spec | 1 | not yet a record | DEC-002 |
| OWASP CycloneDX Authoritative Guide to SBOM | guide | 1 | not yet a record | DEC-002 |
| Syft (anchore/syft, Apache-2.0) | tool | 3, 4 | not yet a record | DEC-007 |
| Grype (anchore/grype, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-007, DEC-008 |
| Trivy (aquasecurity/trivy, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-008 |