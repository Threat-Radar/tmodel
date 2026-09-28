---
schema: "archdoc/v1"
id: RPT-0004-searches
title: "RPT-0004 search log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
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