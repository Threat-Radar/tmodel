---
schema: "archdoc/v1"
id: RPT-0005-sources
title: "RPT-0005 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-10-05"
updated: "2026-10-05"
record: RPT-0005
---

# RPT-0005: source log

Every source found, and the `library/` record it became. #39 accepts a record only as `stub` (kept for later, honestly marked) or FX-1 (fully extracted); `summarized` and `queued` records must be moved to one or the other.

## Records that already exist (library `main` at `e36b37c`, 2026-10-05)

| source | type | dimension | library record id | status | bears_on |
|---|---|---|---|---|---|
| MITRE CWE | catalog | 1 | `cwe` | summarized | DEC-001, DEC-008 |
| CVE record format (CVE JSON 5) | spec | 1 | `cve-json-5` | summarized | DEC-001, DEC-002, DEC-008 |
| OSV schema | spec | 1, 7 | `osv-schema` | summarized | DEC-002 |
| FIRST CVSS | spec | 2 | `first-cvss` | queued | DEC-002 |
| MITRE ATT&CK | catalog | 4 | `mitre-attack` | summarized | DEC-001 |
| MITRE CAPEC | catalog | 4 | `capec` | summarized | DEC-001 |
| MITRE D3FEND | ontology | 4 | `d3fend` | summarized | DEC-001 |
| OASIS STIX 2.1 | spec | 4 | `stix-2-1` | summarized | DEC-002, DEC-004 |
| SPDX 3.0.1 | spec | 7 | `spdx-3-0-1` | queued | DEC-002 |
| CycloneDX 1.7 | spec | 7 | `cyclonedx-1-7` | queued | DEC-002 |

## Formats with no record yet

NVD (API 2.0 and CPE data), EPSS, OpenVEX, CSAF 2.x (and its VEX profile), TAXII 2.1, OTM, threagile, pytm, OWASP Threat Dragon, OSCAL, ReqIF, SysML v2, OMG SACM (listed as pending in RPT-0013's sources).

## Sources found in Phase 1

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
