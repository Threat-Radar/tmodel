---
schema: "archdoc/v1"
id: RPT-0005-searches
title: "RPT-0005 search log"
type: research
status: draft
version: "0.2.0"
date: "2026-10-05"
updated: "2026-10-05"
record: RPT-0005
---

# RPT-0005: search log

Every query run, so the survey is reproducible. One row per query.

| date | dimension | query | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-10-05 | all (Phase 0) | which existing reports, specs and library records already cover each in-scope format | repository search of `tmodel` (`research/`, `spec/`, `project/`) and `library` (`records/`), via Claude Code | overlaps listed in dimensions.md "Related reports"; existing records listed in sources.md |
| 2026-10-05 | 1 (pilot: CWE) | direct fetch: cwe.mitre.org downloads, terms of use, schema docs; `cwe_schema_latest.xsd` and `cwec_latest.xml.zip` downloaded and parsed | web fetch + curl | CWE 4.20 / schema 7.3; summarizer's release date (2024-11-19) contradicted by the XML header (2026-04-30) and rejected |
| 2026-10-05 | 1 (pilot: CWE) | CWE custom weakness local extension organization-specific CWE identifiers tool vendor | web search | nothing usable; no documented local-extension convention found (left open for the fan-out) |
| 2026-10-05 | 1 (pilot: CWE) | CWE root cause mapping guidance Usage Prohibited Discouraged Allowed-with-Review CVE CNA | web search | CWE root-cause mapping guidance v1.1 |
| 2026-10-05 | 1 (pilot: CWE) | CWE content submission process board governance new entry request | web search | CWE submission guidelines; CWE Content Development Repository |
| 2026-10-05 | 1 (pilot: CVE) | GitHub API: `CVEProject/cve-schema` contents, releases, licence; schema v5.2.0 and `tags/*.json` downloaded and parsed | gh + curl | CVE Record Format 5.2.0 |
| 2026-10-05 | 1 (pilot: CVE) | CVE program governance 2026 CVE Foundation MITRE CISA contract; CVE program MITRE contract March 2026 renewal CVE Foundation transition | web search | press coverage of the 2025 contract extension only; status checked instead in `CVEProject/cve-website` `news.json` |
| 2026-10-05 | 1 (pilot: CVE) | CVE-2021-44228 record from `CVEProject/cvelistV5` | curl | CNA and CISA-ADP containers compared |
| 2026-10-05 | 1 (pilot: NVD) | NVD API docs page (did not render); live NVD CVE API 2.0 for CVE-2021-44228 and for all CVEs published 2026-09-20 | web fetch + curl | response structure; enrichment sample (96 of 102 Deferred) |
| 2026-10-05 | 1 (pilot: NVD) | NVD backlog 2026 deferred status enrichment CPE NIST; nvd.nist.gov news April 2026 NVD prioritization enrichment "Not Scheduled" | web search | NIST news release of 2026-04-15 (primary), fetched and quoted |
| 2026-10-05 | 5 (pilot: OTM) | GitHub API: `iriusrisk/OpenThreatModel` metadata, releases, commits; `otm_schema.json`, `EXAMPLE.json`, `README.md` downloaded and parsed; `iriusrisk/startleft` metadata | gh + curl | OTM 0.2.0; StartLeft |
