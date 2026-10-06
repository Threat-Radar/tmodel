---
schema: "archdoc/v1"
id: DL-0013
title: "RPT-0005 schema representations: AI-assisted scoping, survey and crosswalk"
type: process
status: draft
version: "0.2.0"
date: "2026-10-05"
updated: "2026-10-05"
record: DL-0013
---

# DL-0013: RPT-0005, schema representations

AI-assisted research record for #39 part A (which replaces #9), per `CLAUDE.md`. Student: Mai Li McGhee, working with Claude Code. This entry is extended at each phase of the #39 playbook.

## Phase 0: scope (2026-10-05)

### Question asked

Start #39 part A: write `dimensions.md` with the sub-questions and the exact columns of the comparison table, so that "complete" is fixed before the search starts.

### What was produced

- `research/0005-schema-representations/dimensions.md`: six tables with fixed columns (comparison, concept crosswalk, relation crosswalk, adoption, five-axis applicability rubric, local extension needs), ten dimensions, a per-format record shape, the Phase 1 plan, the overlaps with other reports, and four open scope questions for @nymble.
- Scaffolds for `report.md`, `searches.md` and `sources.md`. `sources.md` lists the ten library records that already exist for in-scope formats and their status (seven `summarized`, three `queued`; none is FX-1).

### Choices the agent made, open to review

- **Crosswalk rows come from ARCH-0001 §3**, the source of truth, not from the unaccepted LinkML draft in `spec/schema/`. Concepts that are only in the draft (DamageScenario, Assertion, Party) are listed as candidates in part 2 of Table 2.
- **A relation crosswalk (Table 3) was added** beside the concept crosswalk, because ADR-0004 made the logical model edge-rich. #9 and #39 ask for a concept crosswalk only.
- **VEX is one concept with four encodings** (OpenVEX, CSAF VEX profile, CycloneDX VEX, SPDX 3 Security profile), not four formats.
- **Composition covers only what RPT-0004 does not**: how vulnerabilities and VEX attach to components, and identifier mapping.
- **"SACM" is OMG SACM** (assurance cases), as in RPT-0013, not IETF SACM (endpoint posture monitoring).
- **A pilot comes before the fan-out**: CWE, CVE/NVD and OTM in the main session, as #9's self-improving loop suggests.

### What a human accepted

- The student chose to start with part A before part B (SAGAI), which waits on @nymble confirming the spec set.
- The student capped parallel research agents at three per round instead of the playbook's three to five, to control cost.
- Pending: the student's and @nymble's review of `dimensions.md`, and answers to its open scope questions.

### What was rejected, and why

Nothing yet.

## Phase 1 pilot: CWE, CVE, NVD and OTM (2026-10-05)

### Question asked

Run the pilot planned in `dimensions.md` in the main session, without sub-agents: fill the per-format record and the tables for CWE, CVE/NVD and OTM, and report whether the columns and marks work before the three-agent fan-out.

### What was produced

- `research/0005-schema-representations/pilot.md`: per-format records for CWE 4.20, CVE Record Format 5.2.0, NVD CVE API 2.0 and OTM 0.2.0; pilot rows of Tables 1, 2, 3 and 5; the changes made to `dimensions.md`; open items.
- `dimensions.md` 0.2.0: the `txt` mark, edge qualifiers, separate CVE and NVD columns, a rubric scope note, and SSVC and TM-BOM as coverage candidates.
- `searches.md` and `sources.md` 0.2.0: ten query rows and twelve sources.

### Method

Facts were taken from the artifacts, not from summaries: the CWE XSD and XML, the CVE JSON Schema and a real CVE record, the live NVD API, and the OTM schema, example and README were downloaded and parsed, and each schema's SHA-256 recorded. Web pages were used for licence, governance and announcements. The NVD API documentation page did not render for the fetch tool, so the live API was used instead.

### Choices the agent made, open to review

- **NVD's 2026 enrichment change is treated as a DEC-008 finding**, backed by NIST's announcement and a one-day sample of live data (102 CVEs), not by press reports alone.
- **Ratings are within each format's scope** (now a rubric note in `dimensions.md`), so a catalog is not marked down for lacking system-side types.
- **CWE `ChildOf` is mapped as specialization, not `part_of`**; ARCH-0001 has no specialization edge, so it is listed as an edge we lack.
- **Local CWE extension:** the pilot found no documented convention and proposes, as evidence only, a separate namespace linked by a fit-graded mapping modelled on CWE's `Mapping_Fit`. Practice in tools is left to the fan-out.

### What a human accepted

- The student reviewed the pilot's five main findings for clarity on 2026-10-05, after a plain-language walk-through, and approved starting the fan-out. This is a clarity review, not a technical one: the student is new to the field. Technical review of the facts and ratings is still pending, through the Phase 4 adversarial review and @nymble.

### What was rejected, and why

- **CWE 4.20 release date "November 19, 2024"**, from the web-fetch summarizer of the CWE downloads page. Rejected: the downloaded catalog's header says `Version="4.20" Date="2026-04-30"`.
- **"The Apache CNA asserts CVSS 3.1 for CVE-2021-44228"**, in the agent's first draft of `pilot.md`. Rejected on checking the record: the CNA container has only `other` ("critical"); the CVSS 3.1 vector and SSVC decision come from the CISA-ADP container.
- **"A rejected CVE names its replacement only in prose"**, in the same draft. Rejected on checking the schema: `cnaRejectedContainer.replacedBy` lists the CVE ids it was rejected in favor of. The `supersedes` cell for CVE was changed from `txt` to `=`.
- **Press reports that NVD "will drop the 'Deferred' status"** are not used as fact: the live API still returned `Deferred` on 2026-10-05, and `pilot.md` records what was observed.

