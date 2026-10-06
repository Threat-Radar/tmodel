---
schema: "archdoc/v1"
id: RPT-0005-sources
title: "RPT-0005 source log"
type: research
status: draft
version: "0.2.0"
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
| CWE XML schema 7.3, <https://cwe.mitre.org/data/xsd/cwe_schema_v7.3.xsd> (SHA-256 `690dedeed4e12eb8ba7244bbab90176afac549cfd6403de37000de7481e45f98`) and CWE List 4.20, <https://cwe.mitre.org/data/xml/cwec_latest.xml.zip> (SHA-256 `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`) | spec + dataset | 1 | `cwe` (existing) | DEC-001, DEC-008 |
| CWE terms of use, <https://cwe.mitre.org/about/termsofuse.html> | licence | 1 | `cwe` (existing) | DEC-002 |
| CWE root-cause mapping guidance v1.1 (2024-03-22), <https://cwe.mitre.org/documents/cwe_usage/guidance.html> | guidance | 1 | new, Phase 2 | DEC-008 |
| CWE submission guidelines, <https://cwe.mitre.org/community/submissions/guidelines.html>; CWE Content Development Repository, <https://github.com/CWE-CAPEC/CWE-Content-Development-Repository> | process | 1 | `cwe` (existing) | DEC-001 |
| CVE Record Format 5.2.0, <https://github.com/CVEProject/cve-schema/blob/v5.2.0/schema/CVE_Record_Format.json> (SHA-256 `33f7517424facfc712c7b808be1b6503fc74b2e6b85979bbaacb9b623ddfde67`); release notes <https://github.com/CVEProject/cve-schema/releases/tag/v5.2.0> | spec | 1 | `cve-json-5` (existing; update to 5.2.0) | DEC-001, DEC-002, DEC-008 |
| CVE List in CVE JSON 5, <https://github.com/CVEProject/cvelistV5> | dataset | 1 | new, Phase 2 | DEC-008 |
| CISA Vulnrichment (CISA-ADP), <https://github.com/cisagov/vulnrichment> | dataset | 1, 2 | new, Phase 2 | DEC-008 |
| CVE Program news, <https://github.com/CVEProject/cve-website/blob/main/src/assets/data/news.json> | governance | 1 | none (context only) | — |
| NVD CVE API 2.0, <https://services.nvd.nist.gov/rest/json/cves/2.0> (observed 2026-10-05) | service | 1 | new, Phase 2 | DEC-008 |
| NIST, "NIST Updates NVD Operations to Address Record CVE Growth" (2026-04-15), <https://www.nist.gov/news-events/news/2026/04/nist-updates-nvd-operations-address-record-cve-growth> | announcement | 1 | new, Phase 2 | DEC-008 |
| Open Threat Model 0.2.0, <https://github.com/iriusrisk/OpenThreatModel> (schema SHA-256 `81e7f5a52a0a7d66b44cc4e0c15f21b5d60e1ca945c810e39622a730545eef0c`) | spec | 5 | new, Phase 2 | DEC-002 |
| StartLeft, <https://github.com/iriusrisk/startleft> | tool | 5, 9 | new, Phase 2 | DEC-002 |
