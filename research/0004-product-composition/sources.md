---
schema: "archdoc/v1"
id: RPT-0004-sources
title: "RPT-0004 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
record: RPT-0004
---

# RPT-0004: source log

Every source found, and the `library/` record it became.

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| CycloneDX 1.7 (ECMA-424, 2nd ed.) | spec | 1, 2, 5 | `cyclonedx-1-7` (m-of-n/library#25, not yet in fork) | DEC-002 |
| SPDX 3.0.1 | spec | 1 | `spdx-3-0-1` (m-of-n/library#25, not yet in fork) | DEC-002 |
| NTIA, Minimum Elements for an SBOM (2021) | spec | 1 | `ntia-sbom-minimum-elements` (m-of-n/library#25) | DEC-002 |
| CISA, Framing Software Component Transparency (3rd ed., 2024) | spec | 1, 6 | `cisa-framing-software-component-transparency` (m-of-n/library#25, not yet in fork) | DEC-002 |
| OWASP CycloneDX Authoritative Guide to SBOM | guide | 1 | not yet a record | DEC-002 |
| Syft (anchore/syft, Apache-2.0) | tool | 3, 4 | not yet a record | DEC-007 |
| Grype (anchore/grype, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-007, DEC-008 |
| Trivy (aquasecurity/trivy, Apache-2.0) | tool | 3, 5 | not yet a record | DEC-008 |