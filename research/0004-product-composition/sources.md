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
| CycloneDX 1.7 (ECMA-424, 2nd ed.) | spec | 1, 2, 5 | `cyclonedx-1-7` (in fork via Threat-Radar/library#5; `queued`, summary has header metadata only) | DEC-002 |
| CycloneDX 1.7 JSON reference (cyclonedx.org/docs/1.7/json/) | spec (web view) | 1, 2, 5 | same spec as `cyclonedx-1-7`; source of the quoted field descriptions | DEC-002 |
| CycloneDX 1.7 JSON schema file (CycloneDX/specification, tag `1.7`, `schema/bom-1.7.schema.json`) | spec (machine-readable) | 1 | same spec as `cyclonedx-1-7`; used for the checks in Tool runs | DEC-002 |
| CycloneDX property taxonomy, `cdx:device` namespace (github.com/CycloneDX/cyclonedx-property-taxonomy) | spec (side list) | 1, 2 | not yet a record | DEC-001, DEC-002 |
| SPDX 3.0.1 | spec | 1 | `spdx-3-0-1` (in fork via Threat-Radar/library#5; `queued`, summary has header metadata only) | DEC-002 |
| SPDX 3.0.1 model file (spdx.org/rdf/3.0.1/spdx-model.ttl) | spec (machine-readable) | 1 | same spec as `spdx-3-0-1`; used for the checks in Tool runs | DEC-002 |
| ISO/IEC 19770-2:2015, Software identification tag (SWID) | spec | 1 | not yet a record; paywalled, not read; listed in `ntia-sbom-minimum-elements`'s references | DEC-002 |
| ISO/IEC 19770-6:2024, Hardware identification tag | spec | 2 | not yet a record; paywalled, not read; described from ISO Open Data metadata | DEC-001 |
| ISO Open Data, `iso_deliverables_metadata` dataset (downloaded 2026-09-30). "This work is based on the iso_deliverables_metadata dataset from ISO Open Data, licensed under ODC Attribution License (ODC-By) v1.0" | dataset | 1, 2 | not yet a record | DEC-002 |
| ISO Guide 69:1999, Harmonized Stage Code system (preview copy at cdn.standards.iteh.ai) | guide | 1 | not yet a record; used only to read stage code 90.60 | none |
| NIST IR 8060, Guidelines for the Creation of Interoperable Software Identification (SWID) Tags (2016) | guide | 1 | not yet a record; listed in `ntia-sbom-minimum-elements`'s references | DEC-002 |
| RFC 9393, Concise Software Identification Tags (CoSWID) | spec | 1 | not yet a record | DEC-002 |
| NTIA, Minimum Elements for an SBOM (2021) | spec | 1 | `ntia-sbom-minimum-elements` (in fork via Threat-Radar/library#5; `summarized`) | DEC-002 |
| CISA, Framing Software Component Transparency (3rd ed., 2024) | spec | 1, 6 | `cisa-framing-software-component-transparency` (in fork via Threat-Radar/library#5; `summarized`) | DEC-002 |
| gitoid URI scheme (IANA provisional registration), used by OmniBOR | spec | 1 | not yet a record | DEC-002 |
| SWHID specification (Software Heritage), published as ISO/IEC 18670:2025, "SWHID Specification V1.2" | spec | 1 | not yet a record | DEC-002 |
| ISO/IEC 5962:2021 (SPDX 2.2.1), ISO/IEC DIS 5962 (SPDX 3.0), ISO/IEC CD 27055 (CycloneDX), ISO/IEC CD 27056 (purl) | spec | 1 | not yet records; status only, from ISO Open Data; not read | DEC-002 |
| RFC 6149 and RFC 6150 (IETF, "MD2 to Historic Status", "MD4 to Historic Status") | spec | 1 | not yet a record | DEC-002 |
| NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) | spec | 1 | not yet a record | DEC-002 |
| CISA, Minimum Requirements for Vulnerability Exploitability eXchange (VEX) (April 2023) | spec | 5 | not yet a record | DEC-008 |
| CISA, A Hardware Bill of Materials (HBOM) Framework for Supply Chain Risk Management (September 2023) | guide | 2 | not yet a record | DEC-001, DEC-002 |
| CycloneDX HBOM capability page (cyclonedx.org/capabilities/hbom/) | web page | 2 | not yet a record | DEC-001 |
| CISA, Types of Software Bill of Material (SBOM) Documents (April 2023) | guide | 6 | not yet a record | DEC-001 |
| OCI Distribution Specification v1.1.1 (github.com/opencontainers/distribution-spec, tag `v1.1.1`) | spec | 6 | not yet a record | DEC-001 |
| SLSA v1.2 Build Provenance (slsa.dev/spec/v1.2/build-provenance) | spec | 6 | not yet a record | DEC-001 |
| in-toto Attestation Statement v1 (github.com/in-toto/attestation, tag `v1.2.0`, `spec/v1/statement.md`) | spec | 6 | `in-toto-attestation-v1` (`queued`, summary not yet written) | DEC-001 |
| Reproducible Builds, definition (reproducible-builds.org/docs/definition/) | guide | 6 | not yet a record | DEC-001 |
| tradar repository (Threat-Radar/tradar, commit `26d9c76`, 2026-09-10) | code | 3, 4 | not yet a record | DEC-007 |
| NVD API records for CVE-2022-37434, CVE-2025-60876, CVE-2026-85091 (services.nvd.nist.gov/rest/json/cves/2.0, pulled 2026-09-30) | data | 5 | not yet a record | DEC-008 |
| NVD weakness list (nvd.nist.gov/public/service/rest/json/nvd/vulns/weakness) | data | 5 | not yet a record | DEC-008 |
| NVD Vulnerability API documentation (nvd.nist.gov/developers/vulnerabilities) | guide | 5 | not yet a record; the page renders with JavaScript, so the quoted text was checked in NVD's live page bundle (nvd.nist.gov/main-QN4PLKKZ.js) | DEC-008 |
| OSV schema (ossf.github.io/osv-schema) | spec | 5 | not yet a record | DEC-008 |
| Package URL (purl) specification, ECMA-427 (github.com/package-url/purl-spec) | spec | 1, 5 | not yet a record | DEC-002 |
| Alpine secdb, release 3.24, main (secdb.alpinelinux.org/v3.24/main.json, checked 2026-09-30) | data | 5 | not yet a record | DEC-008 |
| Grype documentation (oss.anchore.com: ecosystems guide, interpreting results, configuration reference), source `grype/matcher/apk/matcher.go`, and pull request #1412 | tool docs | 3, 5 | not yet a record | DEC-007, DEC-008 |
| Syft CPE generation README (github.com/anchore/syft, `syft/pkg/cataloger/internal/cpegenerate/README.md`) | tool docs | 3, 5 | not yet a record | DEC-002 |
| Trivy documentation (trivy.dev: scanner/vulnerability, target/sbom) | tool docs | 3, 5 | not yet a record | DEC-008 |
| Dependency-Track documentation (docs.dependencytrack.org for v4; dependencytrack.github.io/docs/next for v5), README 5.1.1, changelog, issue #1746 | tool docs | 3 | not yet a record | DEC-002 |
| GUAC README v1.1.0, docs.guac.sh (GraphQL, OSV certifier, components), `pkg/ingestor/parser/spdx/parse_spdx.go`, issue #1850 | tool docs | 3 | `guac` (in fork) | DEC-002 |
| CycloneDX bom-examples, `VEX/CISA-Use-Cases/Case-1` (github.com/CycloneDX/bom-examples; linked from CISA's VEX document) | examples | 5 | not yet a record | DEC-008 |
| OWASP CycloneDX Authoritative Guide to SBOM | guide | 1 | not yet a record | DEC-002 |
| Syft (anchore/syft, Apache-2.0) | tool | 3, 4 | not yet a record | DEC-007 |
| Grype (anchore/grype, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-007, DEC-008 |
| Trivy (aquasecurity/trivy, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-008 |