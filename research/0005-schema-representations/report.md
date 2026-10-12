---
schema: "archdoc/v1"
id: RPT-0005
title: "Schema representations of cybersecurity information"
short_title: "Schema representations"
description: "How the field encodes weaknesses, vulnerabilities, scores, applicability, attacks, threat models, requirements and composition; a cross-format crosswalk onto ARCH-0001's types and where local extension is needed. Evidence, not decisions."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-10-05"
updated: "2026-10-05"
authors:
  - role: student
    id: mai-li-mcghee
  - role: research
    id: ai-assisted
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0005-schema-representations/report.md
library_commit: "records not yet extracted"
informs: [DEC-001, DEC-002, DEC-008, DEC-009]
open_decisions: [DEC-001, DEC-002, DEC-008, DEC-009]
issue: 39
---

# RPT-0005: Schema representations of cybersecurity information

**Status: scaffold.** The plan, the questions each section answers and the columns of every table are in [dimensions.md](dimensions.md). Nothing here is accepted.

## Planned sections

1. Comparison table and applicability ratings (Tables 1 and 5)
2. Weakness and vulnerability records: CWE, CVE, NVD, OSV
3. Scores and exploitation signals: CVSS, EPSS
4. Applicability and advisories: VEX (four encodings), CSAF
5. Threat and attack knowledge: ATT&CK, CAPEC, D3FEND, STIX/TAXII
6. Threat-model object models: OTM, threagile, pytm, Threat Dragon
7. Requirements, controls and assurance: OSCAL, ReqIF, SysML v2, OMG SACM
8. Composition, security-relevant part: SPDX 3, CycloneDX
9. Crosswalk and local extension (Tables 2, 3 and 6)
10. Adoption (Table 4)
11. Synthesis and gap analysis, routed to `DEC-*` and issues
12. Method, coverage review and limits
