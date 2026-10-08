---
schema: "archdoc/v1"
id: DL-0013
title: "RPT-0005 schema representations: AI-assisted scoping, survey and crosswalk"
type: process
status: draft
version: "0.4.0"
date: "2026-10-05"
updated: "2026-10-08"
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

## Phase 1 fan-out: three research agents (2026-10-05 to 2026-10-06)

### Question asked

Run the rest of Phase 1 as planned in `dimensions.md`: three research agents in parallel, each filling the per-format record and Tables 1 to 6 for its dimensions, to the pilot's standard (artifacts over summaries, SHA-256 per file, every rejected claim recorded).

### What was produced

- `fanout-vuln-data.md` (dimensions 1 to 3): OSV, CVSS 3.1 and 4.0, EPSS, VEX in four encodings, CSAF 2.0 and 2.1; light records for CPE, purl, CISA KEV and SSVC; adoption rows for CWE, CVE and NVD; the pilot's open items closed.
- `fanout-attack-composition.md` (dimensions 4 and 7): ATT&CK 19.2, CAPEC 3.9, D3FEND 1.6.0, STIX 2.1, TAXII 2.1, and the security-relevant parts of SPDX 3.0.1 and CycloneDX 1.7.
- `fanout-models-requirements.md` (dimensions 5 and 6): threagile, pytm, OWASP Threat Dragon, OSCAL 1.2.3, ReqIF 1.2, SysML v2.0, OMG SACM 2.3, and a TM-BOM coverage check; `fanout-models-requirements-sha256.txt` lists its 138 downloaded files.
- `searches.md` and `sources.md` 0.3.0: the agents' query and source rows appended.

The three files are kept as the agents wrote them. Downloaded third-party files stayed in the session scratch folder and are not committed.

### Method and what went wrong

- Three agents, not five, to control cost (the student's cap). All three hit the account's usage limit on 2026-10-05. Agents 2 and 3 had already written their complete files; agent 1 had downloaded its sources (171 files) but written nothing.
- Agent 1 was re-run on 2026-10-06 on a cheaper model (Sonnet), told to reuse the downloaded files and re-verify each one's source URL and hash. It rejected nine of the previous run's files as unusable (empty, error pages, JavaScript stubs, an unrecoverable source).

### How the main session checked the agents

Ten facts were re-derived from the downloaded artifacts or live data, and all matched: CAPEC 3.9 has 615 attack patterns, 402 Draft; ATT&CK 19.2 has 697 `detects`, 157 `revoked-by` and 26 `attributed-to` relationships, and no active technique carries a CAPEC reference; the OTM schema file states Apache License 2.0; pytm's licence file is MIT; CycloneDX issue #462 (TM-BOM) closed 2026-08-20; the NVD placeholder weaknesses `NVD-CWE-noinfo` and `NVD-CWE-Other` count 36,262 and 30,013 (36,258 and 30,007 a day earlier, in the agent's file); CycloneDX defines 9 VEX justification codes and OpenVEX 5. This is a sample, not a full check; Phase 4's adversarial review is the full one.

### Corrections the fan-out forced on earlier work

- **`pilot.md` (0.1.1):** OTM's licence is split, CC BY-SA 4.0 for the specification text and Apache-2.0 for the schema file (agent 3). Corrected.
- **RPT-0003:** it gives pytm's licence as GPL-3.0; the licence file is MIT (agent 3, confirmed). Not changed here, because RPT-0003 is outside this PR; to be raised separately.
- **Library summaries** (`stix-2-1`, `capec`, `d3fend`, `mitre-attack`) and RPT-0011 contain claims the agents found wrong or out of date: STIX 2.1 has 19 SDOs, not 17; CAPEC's ATT&CK links are pinned to ATT&CK 12.0, and ATT&CK dropped its CAPEC links in v13; D3FEND has no direct defence-to-offence edges, because those pairs are inferred and published separately. These feed Phase 2, when the records are extracted to FX-1.
- **The pilot's "NVD CVE API 2.0" label:** the response says `version: "2.0"`, but the schema document is titled version 2.2.4. Both are kept.

### Choices the agents made, open to review

- **TM-BOM as a full format** (agent 3): CycloneDX 2.0's threat-model modules were merged into the `2.0-dev` branch on 2026-08-20 but are unreleased. The 2.0 milestone's due date (2026-08-31) has passed with 90 of 176 issues open, and the TM-BOM schema review (#731) is still open. Recommended: cover it as a draft pinned to a commit, subject to @nymble's agreement.
- **CSAF 2.1 is rated as a draft:** it is a Committee Specification Draft (2026-09-11), not an OASIS Standard.

### What a human accepted

- The student approved the fan-out after the pilot (2026-10-05), and on 2026-10-06 approved re-running agent 1 on a cheaper model, reusing its downloads, to save cost.
- Technical review of the three files is pending, through Phase 4 and @nymble.

### What was rejected, and why

The agents' own rejected claims are listed in section 11 or 12 of each `fanout-*.md` file: 13 in agent 1's, 10 in agent 2's and 13 in agent 3's. Most of them corrected summaries, file names and version labels against the artifact.


## Sponsor answers to the scope questions (2026-10-08)

### Question asked

The student posted the four open scope questions from `dimensions.md` on #39 (2026-10-06). @nymble answered on 2026-10-08 (<https://github.com/Threat-Radar/tmodel/issues/39#issuecomment-6049323428>). The reply is signed "Claude (for @nymble)": written by an AI on the sponsor's behalf, with the scope calls (questions 2 and 3) stated as the sponsor's.

### What was produced

`dimensions.md` 0.3.0: the open-questions section is replaced by the answers; CPE, purl and SWID move to an identity sub-row under Product/Component; KEV becomes an attribute on the Vulnerability and Exploitation-evidence rows; OpenC2 and ATLAS are recorded as coverage-only and one row respectively.

### What a human accepted

- The sponsor confirmed two of the agent's proposed defaults: OpenC2 as coverage-only, and ATLAS cited through RPT-0014 (at most one row).
- The sponsor confirmed that the FX-1 tooling is on library `main`; the agent checked that the six files are there (2026-10-08).

### What was rejected, and why

- **The agent's proposed default "CPE and purl as formats in their own right"** (suggested to the student on 2026-10-05). Rejected by the sponsor: they are identifier schemes, so they belong in an identity sub-row, not in object-model columns.
- **The agent's proposed default "KEV handled alongside EPSS"** was refined rather than rejected: KEV is a curated annotation on a CVE, so it is modelled as an attribute or assertion on the vulnerability row, not as a scoring scheme.

