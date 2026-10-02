---
schema: "archdoc/v1"
id: RPT-0007-sources
title: "RPT-0007 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-02"
record: RPT-0007
---

# RPT-0007: source log

Every source found, and the `library/` record it became.

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| ISO/SAE 21434:2021, Road vehicles: Cybersecurity engineering (1st edition; the sponsor's purchased SAE copy, 87 pages, SHA-256 `73f990078d3a5b47dec91dd0d2b4e6c24cecd9e4160ae5b143c3b3fa80b7cdf4`; held locally, never committed) | spec | 1 to 7 | `iso-sae-21434-2021` (`distilled`; catalog not yet reviewed, see §7) | DEC-001, DEC-003, DEC-009 |
| Library catalog for ISO/SAE 21434 (`records/iso/iso-sae-21434-2021/distilled/requirements.yaml` and `normative.md`, library `5b82f83`) | catalog | 1, 7 | `iso-sae-21434-2021` | DEC-001, DEC-003 |
| SAE J3061:2016 (replaced by ISO/SAE 21434) | guide | 1 | `sae-j3061` | none |
| ISO 26262-3:2018, Road vehicles: Functional safety, Part 3: Concept phase (the only normative reference of ISO/SAE 21434) | spec | 1, 3 | `iso-26262-3-2018`; not read; status only, from ISO Open Data | DEC-003 |
| ISO/SAE PAS 8475 (CAL and TAF), ISO/SAE TR 8477 (verification and validation), ISO/PAS 5112:2022 and ISO/DTS 5112 (auditing), ISO 24089:2023 (software updates) | spec | 1 | not yet records; status only, from ISO Open Data; not read | DEC-003 (PAS 8475) |
| ISO Open Data, `iso_deliverables_metadata` dataset (downloaded 2026-09-30). "This work is based on the iso_deliverables_metadata dataset from ISO Open Data, licensed under ODC Attribution License (ODC-By) v1.0" | dataset | 1 | not yet a record | none |
| Methods and metrics that ISO/SAE 21434 points to, not read for this report: ISO/IEC 18045 (attack potential factors, RC-15-12, G.2), EVITA, TVRA, PASTA and STRIDE (RQ-15-03, NOTE 2; EVITA also in F.1), ISO/IEC 29100 (PII principal, F.5) | spec | 2, 3 | `iso-iec-18045`, `etsi-ts-102-165-1` (TVRA) and `pasta-risk-centric-threat-modeling`, all `queued`; EVITA and ISO/IEC 29100 have no record (EVITA is a gap listed in `iso-sae-21434-2021`); STRIDE is covered by RPT-0002 | DEC-003 |
| FIRST, Common Vulnerability Scoring System v3.1: Specification Document (first.org/cvss/v3.1/specification-document), the CVSS version ISO/SAE 21434 cites ([24]); read 2026-10-01 | spec | 3 | `first-cvss` (`queued`, no version pinned) | DEC-003 |
| FIRST, Common Vulnerability Scoring System v4.0: Specification Document (first.org/cvss/v4.0/specification-document); read 2026-10-01 | spec | 3 | `first-cvss` (`queued`, no version pinned) | DEC-003 |
| ARCH-0001-PROPOSAL v0.2.0 (`0.2.0-proposed.7`, 2026-10-01), the proposed object model (#15) | design proposal (this repo) | 5, 6 | n/a (in `spec/`) | DEC-001, DEC-003 |
| ADR-0002, MVP scope (accepts DEC-005) | decision (this repo) | 1, 5 | n/a (in `spec/`) | DEC-005 (accepted) |
| ARCH-0001 v0.1.6, §3 object model (the current working labels) | architecture (this repo) | 5 | n/a (in `spec/`) | DEC-001 |
| ADR-0004, storage and edges (accepts DEC-011): typed edges with properties, stable IDs | decision (this repo) | 4, 5 | n/a (in `spec/`) | DEC-011 (accepted) |
| Full extraction standard FX-1 (`docs/extraction.md` in the upstream m-of-n/library; not yet in the Threat-Radar fork) | process standard | 7 | n/a | none |
| Library rules for requirement catalogs (`docs/requirements.md` in the Threat-Radar library fork: `text` is verbatim) | process rule | 7 | n/a | none |
