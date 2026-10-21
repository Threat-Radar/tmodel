---
schema: "archdoc/v1"
id: DL-0013
title: "RPT-0005 schema representations: AI-assisted scoping, survey and crosswalk"
type: process
status: draft
version: "0.10.0"
date: "2026-10-05"
updated: "2026-10-21"
record: DL-0013
---

# DL-0013: RPT-0005, schema representations

AI-assisted research record for #39 part A (which replaces #9), per `CLAUDE.md`. Student: @Maimcghee, working with Claude Code. This entry is extended at each phase of the #39 playbook.

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
- **Press reports that NVD "will drop the 'Deferred' status"** are not used as fact: the live API still returned `Deferred` on 2026-10-05, NVD's own status table lists the web status "Not Scheduled" as API status `Deferred`, and `pilot.md` records what was observed.

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

## Crosswalk assembly, dimension 8 (2026-10-08)

### Question asked

Assemble Tables 2, 3 and 6 from the four Phase 1 files into one crosswalk, apply the sponsor's scope answers, and answer dimension 8's four questions.

### What was produced

`research/0005-schema-representations/crosswalk.md`: mark-only matrices for Table 2 (parts 1 and 2) and Table 3 across 24 formats, with a per-format loss profile and per-concept totals; an identity sub-row for Product and Component (CPE, purl, SWID and others, per the sponsor); grouped lists of edges ARCH-0001 lacks and of recurring edge qualifiers; answers to dimension 8's questions; a consolidated Table 6; and six inputs to the gap analysis.

### Method

The marks were extracted by a script from the cells of `pilot.md` and the three `fanout-*.md` files, without re-judging any cell. The script and its template stayed in the session scratch folder, because they hard-code local paths. The agent wrote the prose, then checked each count and example in it against the source cells.

### Choices the agent made, open to review

- **CPE, purl and KEV columns dropped** from the matrices per the sponsor; the VEX-only columns of CycloneDX and SPDX 3 were folded into those formats' rows; SSVC kept as a row marked "scope open".
- **Cells not assessed are shown as `∅`**, not filled in: the pilot did not assess Advisory/Remediation or DamageScenario, and only agent 3 assessed its two new candidates.
- **Headline claims are counts**, such as "no exact Review in 24 formats". They depend on each source cell's mark, which Phase 4 spot-checks.

### What a human accepted

- The student chose to build the crosswalk before starting Phase 2 (2026-10-08). Review of the result is pending.

### What was rejected, and why

Three statements in the agent's first draft of the prose, each caught by checking the source cells before writing the file:
- "Prose-only successors in CWE, CAPEC and one VEX encoding": the third is pytm's `DEPRECATED` marker, not a VEX encoding.
- "Threat Dragon draws a boundary as a line": its boundaries are a drawn curve or box with geometric membership.
- "Every vulnerability-data and composition format can name the vulnerable thing": too vague to check, so removed.

## Phase 2 test run: CWE extracted to FX-1 (2026-10-08 to 2026-10-13)

### Question asked

Size Phase 2 by extracting one record, `cwe`, to FX-1 in the library repository, in a separate Claude Code session opened there (the `extract` skill loads only from the library root).

### What was produced

Threat-Radar/library#21 (draft): `records/other/cwe/` pinned to CWE List 4.20 and schema 7.3, with the full `distilled/` set (198 requirements, 60 structures, 20 fixtures, design notes mapped to tmodel decisions, and a verification record). The extraction found 16 places where the schema's documentation contradicts its structure. Before upload, the main session added the missing `Signed-off-by` and rebased the branch onto library `main` (22 commits behind). The library's checks passed: `bin/validate`, `bin/check-pr-extraction`, and CI (`validate`, `dco`).

### Cost

The two extraction agents took 32 and 47 minutes, one using about 388k tokens, before an independent checker ran. One record costs over an hour and several hundred thousand tokens, so about twenty would exceed what one student account can carry.

### What a human accepted

- The student reviewed the record's `summary.md`, `design-notes.md` and `verification.md` for clarity (2026-10-13). Technical review is pending; the proposed reviewer is @Clovier, whose #61 imports CWE.
- The student decided not to ask the sponsor to reduce Phase 2 scope. Instead, the plan is to share overlapping records: CycloneDX and SPDX with RPT-0004 (@Clovier), and pytm and Threat Dragon with RPT-0003 (@kriishnaa-18). The messages are drafted but not yet sent.

### What was rejected, and why

The checker's residual issues are listed in `verification.md`. One of them, that the CVE `replacedBy` claim could not be checked, is answered by this log's pilot entry, which verified `replacedBy` against the CVE 5.2.0 schema.

## Report draft 0.2.0 (2026-10-13)

### Question asked

Write `report.md` from the Phase 1 material and the crosswalk, ahead of Phase 2 and Phase 4, so that the adversarial review has a draft to attack and the sponsor sees results early. The playbook places synthesis after review; this draft is reviewed in Phase 4 and revised.

### What was produced

`report.md` 0.2.0: overview; Table 1 (24 formats plus one ATLAS row) and Table 5 (ratings), merged by script from the four source files with the sponsor's scope applied; a section per family with each format's findings, paraphrased from the sources' "Findings that bear on tmodel"; the crosswalk's main matrix; Table 4 (38 adoption rows); a synthesis and a gap analysis of twelve findings, each routed to a `DEC-*` or issue; and method, scope and limits.

### Choices the agent made, open to review

- **Tables are merged, not rewritten.** Rows are copied verbatim from the source files. The CycloneDX and SPDX VEX rows from agent 1 are folded into agent 2's rows, and CPE, purl and KEV are left out per the sponsor.
- **The format sections paraphrase the sources' findings** and add no new claims, except where the pilot or the main session verified a fact (for example the NVD sample).
- **Gap analysis rows are evidence, routed, not proposals.** No `DEC-*` is accepted.

### What a human accepted

- The student chose to draft the report while teammates are asked about sharing Phase 2 (2026-10-13). Review is pending.

### What was rejected, and why

Four statements in the agent's template, each caught by checking against the sources before generating the file:
- "In CVE-2021-44228 the CNA and CISA give different CWE and severity data": CISA's container adds a CVSS score and SSVC, not a CWE; the differing CWE comes from NVD.
- "OSCAL is the strongest format on four of the five axes": it is rated 3 on all five.
- "15 of 42 threagile risk categories link to CWE ids CWE says not to use": the source says 15 of the 42 CWE links are to Prohibited ids.
- "3 rejected claims in the pilot": this log records 4.

## Report 0.3.0: update for decisions accepted on 2026-10-08 and 2026-10-12 (2026-10-13)

### Question asked

Bring the report up to date with tmodel PR #111, which accepted DEC-002 (ADR-0007), DEC-003 (ADR-0006) and DEC-004 (ADR-0008) on 2026-10-08, and PR #119, which accepted DEC-001a (ADR-0010) on 2026-10-12, after the survey was scoped. ADR-0007 commits tmodel to importing OTM and STIX 2.1 and names this crosswalk as the work that "refines and may extend import coverage".

### What was produced

- The branch was merged with `main` (58 commits; no conflicts). The merge carried the sponsor's repo-wide removal of personal names; the report's author id was changed to the GitHub id to match.
- `report.md` 0.3.0: a table of the accepted decisions and what each means for the report; a mapping of the crosswalk's rows onto ADR-0010's classes, read from `spec/schema/tmodel-object-model.linkml.yaml` on `main`; the gap analysis re-routed to accepted ADRs or still-open decisions; and two new findings, G13 and G14.
- `crosswalk.md` 0.1.1: a pointer to that mapping.

### Choices the agent made, open to review

- **G13:** the committed OTM import has no target class for OTM's `assets`, `trustZones` and `dataflows`. The accepted schema has no Asset, TrustBoundary or DataFlow class, and notes "Asset is not a §13 class". This is reported as a risk to ADR-0007's round-trip vector, not as a proposal to add classes.
- **G14:** the committed STIX import yields attack patterns, mitigations, parties and provenance, but no weakness, path, risk or applicability (from the fan-out's STIX findings).
- **Threat → `ThreatInstance`**, with the generic level as `AttackPattern`, based on the two classes' descriptions in the schema.
- **The crosswalk is not re-keyed** to ADR-0010's names. The mapping table is the bridge; re-keying is left to the clarity pass.

### What a human accepted

- The student asked for the update to be done in parallel with the OTM FX-1 run (2026-10-13). Review is pending.

### What was rejected, and why

- **An early reading that the sponsor's name-removal sweep (PR #112) had covered the report.** Checking showed the author id still used a personal name, so it was changed. The same personal id remains in another report on `main` (to be fixed separately).

## Sponsor direction on G13 (2026-10-14)

### Question asked

The student asked @nymble, by text message, whether to add the classes that G13 finds missing (Asset, TrustBoundary, DataFlow), given that ADR-0007 commits tmodel to importing OTM.

### The answer, as the student relayed it

> "Do add … suggest iterative example building … have it make models … based on literature or such in a relatively narrow set of attacks … perhaps automotive … cyber attacks … ability to steal car … user private info etc"

As read: add the three classes, and shape them by building small example threat models iteratively, from published automotive attacks (stealing a car; stealing owners' private data), rather than designing the classes in the abstract.

### What this does and does not do

- It is sponsor direction to start the work, not acceptance. ADR-0010 accepted the core type system without these classes, so adding them needs an ADR that amends it (`CLAUDE.md`: only an ADR accepts a decision).
- The work belongs to the schema lane (#64, owned by the student). The existing automotive examples (`spec/vectors/mvp-02-automotive-ecu.yaml`, `tv-hardware-brake-ecu.yaml`) and RPT-0007 (ISO/SAE 21434) are the starting points.
- Planned loop: choose two or three well-documented attacks from verified sources; write each as an example model; validate it against the schema; add or adjust the classes; repeat.

### What a human accepted

- The sponsor's direction above. The student considers this reading confirmed (2026-10-14).

### What was rejected, and why

Nothing yet.

## CWE FX-1 run: final numbers and a correction (2026-10-16)

The library session's final report on the CWE run, read on 2026-10-16:

- **Cost:** about 1 h 40 min of active time and about 1.65M tokens, possibly up to about 2M (setup and notes ~180k; extraction agents 388k and 507k; checker 577k, interrupted by the usage limit and resumed). One full extraction of a format this size uses most of a session's limit.
- **Scope rule:** the library's CI enforces FX-1 only on `rfc`, `draft`, `spec` and `ietf` records; a `dataset` record such as `cwe` may stay a stub or summary. The session suggested full extraction only for the formats tmodel imports. Since ADR-0007, those are OTM and STIX 2.1, possibly with CVE for R-010; the others would be honest stubs.
- **Third-party files:** the record commits MITRE's XSD verbatim and 13 catalog entries (about 167 KB). FX-1 requires the source schema verbatim, MITRE's licence allows copies that keep its header (kept), and `CLAUDE.md`'s ban covers PDFs, spreadsheets, ebooks and vendor reports. Flagged for the sponsor's review on library#21.

### What was rejected, and why

- **The pilot's "a deprecated CWE entry names its successor only in prose".** The FX-1 extraction found that 2 of the 25 deprecated weaknesses in 4.20 carry a machine-readable suggestion (`Mapping_Notes/Suggestions`). `report.md` 0.3.2 now says "usually". `pilot.md` is left as the record of what the pilot found.
- **Corrections passed on by RPT-0004 (DL-0015, "Corrections for other documents"):** NVD's web status "Not Scheduled" is the API status "Deferred"; `dataVersion` 5.0 occurs only on rejected CVE records; CycloneDX 1.7.2 is a GitHub release (2026-09-17), so the rejection in `fanout-vuln-data.md` no longer holds; `fanout-attack-composition.md` §1.6 shortens the `spdx-model.ttl` SHA-256 as `…a5c404c593`, where its §10 (and the file) ends `…d5f404c593`.

## Technical review by @Clovier, applied (2026-10-21)

### Question asked

@Clovier reviewed tmodel#126 on 2026-10-19, as comments only: 47 one-click suggestions, 4 comments, and 15 fixes for files outside the diff. On 2026-10-21 the student asked for the fixes to be applied.

### What was produced

- **All 47 suggestions, applied as written**, in `report.md`, `crosswalk.md`, `dimensions.md` and this log.
- **Two crosswalk marks**, from the comments:
  - CVE 5.2.0 Exploitation evidence goes from `txt` to `≈`, for CISA-ADP's `ssvc` and `kev` entries. Its source cell in `pilot.md` was corrected, so the script reproduces the mark.
  - SPDX 3.0.1 Req./control goes from `⊂` to `—`, because `hasRequirement` is a lifecycle-scoped dependency. This one was changed by hand, as `crosswalk.md` now says.
  - Neither change alters a "formats with `=`" total or any count in the text.
- **Fixes outside the diff:**
  - `pilot.md`: (a), (b), (c) and the CVE cell, with a corrections note at the top.
  - `sources.md` lines 172 and 173: the CycloneDX schema rows at tags 1.7.2 and 1.7.
  - Line 79 of this log.
  - `dimensions.md`: section numbers (§8 → §9, §9 → §10).
  - The report's Table 1, whose library-record column now gives each record's status (library#20, #21, #25, #26, #28), and the record notes on the per-format paragraphs.

### Checks before applying

- **Against `main`:**
  - ADR-0006, ADR-0007 and ADR-0008 say "accepted (2026-10-08)", and ADR-0010 says "accepted (2026-10-12)". PR #111 merged at 2026-10-09 UTC, which the old date followed; #119 merged on 2026-10-12.
  - The schema's "Asset is not a §13 class" and "not an OTM diagram node" sentences, ADR-0007's "STIX post-MVP ok", ADR-0010's C1, and RPT-0003's pytm licence correction to MIT.
- **Against this report's own files:** `fanout-attack-composition.md` documents only the ATT&CK → CAPEC removal (§1.1, mitre/cti #221), not a CWE one. The full SPDX digests end `…d5f404c593` and `…649234b1`.
- **Against the source:** NIST's notice of 2026-04-15 (fetched 2026-10-21) says CVEs outside its criteria are "lowest priority" and "will not be immediately enriched", and that users can request enrichment.
- **Taken on @Clovier's evidence, not re-run:**
  - the cvelistV5 counts of 2026-10-18: 14,058 records at `dataVersion` 5.0, `replacedBy` on 239 of 18,506 rejected records, and `ssvc` on 204,455 and `kev` on 1,747 of 390,784 published records;
  - CycloneDX 1.7.2's release, CVE 5.2.0's `cpeApplicability`, OSV's `Red Hat` CPE suffix and NVD's pass-through since 2026-06-17.
- `bin/validate-archdoc`: 0 errors.

### Choices the agent made, open to review

- **The fan-out notes stay as the agents wrote them.** Their header says later corrections go to this log, so @Clovier's fixes to `fanout-vuln-data.md` (lines 166, 200, 569, 570, 629, 661) and `fanout-attack-composition.md` (lines 136, 158, 230) are recorded here instead:
  - CycloneDX 1.7.2 is a GitHub release (2026-09-17), so the "1.7.2" rejection in `fanout-vuln-data.md` no longer holds.
  - Its JSON Schema equals the one at tag 1.7.1 and on `master`. It differs from the tag 1.7 file in six description or `$comment` strings, one of which adds "Consumers SHOULD consider ratings in prioritization decisions". So the "earlier download" is the schema at tag 1.7, and "the JSON changes are editorial" undersells one change.
  - Line 136 of `fanout-attack-composition.md` shortens both SPDX digests wrongly.
  - `assessedElement`'s class is Software `SoftwareArtifact`, not Core.
  - SPDX `hasRequirement` is not a requirement (the mark above).
- **`pilot.md` is corrected in place**, as 0.1.1 was, with each change listed at its top. Its CWE "only in prose" sentence stays as the pilot found it (entry of 2026-10-16) and is noted there.
- **The optional fix (c) was taken.**

### What a human accepted

- The student asked for @Clovier's fixes to be applied. The student did not judge them technically: the technical review is @Clovier's, and the sponsor's sign-off is pending.

### What was rejected, and why

- **The decision dates in 0.3.0 to 0.3.2** (2026-10-09 for all four). They followed PR #111's merge time, but the ADRs date DEC-002, DEC-003 and DEC-004 to 2026-10-08, and DEC-001a came separately (2026-10-12, PR #119).
- **Line 254 of this log named the sponsor**, against `CLAUDE.md`. It now gives the role.
- **"ATT&CK → CAPEC and CWE (dropped in ATT&CK 13)."** ATT&CK never carried CWE links; only the CAPEC links were dropped.
- **"NVD enriches only KEV, federal and critical-software CVEs."** NIST says it prioritizes them; the others are not immediately enriched, and users can request enrichment.
- **"ADR-0010 models both natively"** (Review, AttackPath). The accepted `Review` has no date or impact slot and reviews only an `Assertion`.
- **NVD among the five exact Assertion formats.** NVD is `≈`; STIX is the fifth.
- **The two crosswalk marks** above.
- None of @Clovier's suggestions was declined.

### Not fixable in this PR

- Six earlier commits on this branch carry a personal name and a university email in their author and `Signed-off-by:` lines, and commit fedc13d's message repeats the old dates. A squash merge with a clean message and a GitHub-id sign-off fixes both on `main`. That is the sponsor's call at merge.
