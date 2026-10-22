---
schema: "archdoc/v1"
id: DL-0015
title: "RPT-0004 second pass: AI-assisted scoping, survey, extraction and mapping"
type: process
status: draft
version: "0.10.0"
date: "2026-10-08"
updated: "2026-10-22"
record: DL-0015
---

# DL-0015: RPT-0004 second pass, product composition

AI-assisted research record for #38 part A (Product Composition, the second pass on RPT-0004), per `CLAUDE.md`. Student: @Clovier, working with Claude Code. This entry is extended at each phase of the #38 playbook.

## Phase 0: scope (2026-10-08)

### Question asked

The student asked the agent to start work on #38. #38 has two parts: A, deepen RPT-0004 to completeness with full extraction (FX-1) of its library records; and B, finish the ISO/SAE 21434 library record to FX-1. The agent started with part A, because part B waits on the sponsor's first hold on PR #69 (the copyright posture): FX-1 requires the normative text verbatim, and the sponsor asked for paraphrase plus locators instead.

### What was produced

- `research/0004-product-composition/dimensions.md` 0.2.0: nine tables with fixed columns (formats at a glance, minimum-element crosswalk, identifier schemes, hardware and firmware coverage, tools, the composition → model-input mapping, applicability ratings, gap analysis, library records); twelve dimensions, five of them new (identifier schemes, minimum elements and policy baselines, other bill types, the mapping, method and review); a per-source record shape; the Phase 1 plan (a pilot, then five agents); phases 2 to 6; the definition of done; the overlaps with seven other reports; and four open questions for @nymble.

### Choices the agent made, open to review

- **Sections 1 to 6 keep their numbers**, because RPT-0005 cites them. New sections come after them, so the order is not the most natural one for a first-time reader; the clarity pass (Phase 6) can add a short reading guide.
- **Table 6's rows include the draft model**, not only ARCH-0001 §3. RPT-0005 took its crosswalk rows from §3 alone. This report's mapping is for #15 and #17, which iterate the proposal and the LinkML draft, so their types (ProductInstance, Party, Assertion) are rows here, marked as draft.
- **The rubric and the fidelity marks are RPT-0005's**, so ratings and cells can be compared across the two reports. The one change is that the "absent" mark is written `none` instead of a dash, to follow the student's writing-style rule.
- **Three dimensions go beyond #38's list:** identifier schemes (the mapping's identity rules depend on them), minimum elements and policy baselines (Table 2's rows come from them, and CISA's 2026 version may change those rows), and other bill types (a coverage reviewer would ask about CBOMs and AI-BOMs).
- **Left out on purpose:** VEX encodings and the security parts of SPDX and CycloneDX (RPT-0005 owns them), and AI-BOM security (RPT-0014 owns AI threats). Repeating them would create two versions of the same facts.
- **A pilot comes before the fan-out**, on the mapping table, because the table is new and I2 (October 9 to 22) needs a mapping soon.
- **Five agents, not three.** RPT-0005 capped its fan-out at three to control cost; `dimensions.md` says how to merge to three.

### What a human accepted

- On 2026-10-08 the student accepted starting with part A and the Phase 0 scope as written, asked the agent to create the branch (`topic/rpt-0004-deep-research`), commit, push and open draft PR #110, and to start Phase 1 with five agents.
- Pending: @nymble's answers to the open questions in `dimensions.md`.

### What was rejected, and why

Nothing yet.

## Phase 1 pilot: one real composition through Table 6 (2026-10-08)

### Question asked

Run the pilot planned in `dimensions.md`: push one real composition (`alpine:latest`, scanned with Syft 1.52.0 and Grype 0.119.0) through Table 6, the composition → model-input mapping, and fill Table 3's rows for purl and CPE, to test the columns before the fan-out results are used.

### What was produced

- `research/0004-product-composition/pilot.md`: the run and its digests, what the SBOM and the scan hold, Table 6 filled for this composition (25 rows), six findings for #15 and #17, and Table 3's purl and CPE rows.
- `dimensions.md` 0.3.0: Table 6's fidelity mark moved into each source cell and the radar column split in two; Table 6's gap rows extended; questions 5.2 (the database snapshot) and 6.1 (the three image digests) sharpened.

### Method

Facts come from the tool outputs (parsed with python3), the CycloneDX 1.7.2 JSON Schema, the SPDX 3.0.1 model file and JSON-LD context, the OCI index served by Docker Hub's registry, and the LinkML draft. Each claim in `pilot.md` was re-checked by a second script before the file was kept.

### Choices the agent made, open to review

- **The pilot ran alongside the fan-out, not before it.** `dimensions.md` 0.2.0 said "pilot first". The agent launched the five agents first because Table 6 is assembled in the main session and no agent fills it; only Table 3's purl and CPE rows overlap with agent 2, and the pilot left Table 3's columns unchanged.
- **Gap rows are kept in Table 6** (identifiers, version, kind, upstream package, provenance, and others), marked "target: none", rather than dropped, because each one is a finding for #15 and #17.
- **No match is called false.** The pilot says every CPE here is a guess (all 81 are `syft-generated`); it does not say that any of the 29 CPE matches is wrong, which would need a check against each advisory.

### What a human accepted

- Pending: the student's review of `pilot.md` and `dimensions.md` 0.3.0.

### What was rejected, and why

- **"Grype's CycloneDX output uses a `vers` range in every entry"**, in the agent's first draft of `pilot.md`. Rejected on re-checking the file: only 1 of the 30 entries has a range; the other 29 list only the affected version.

## Phase 1 fan-out: five research agents (2026-10-08)

### Question asked

The student asked for Phase 1 with five agents. Each agent got one to three dimensions of `dimensions.md` 0.2.0, its rules (verified sources only, primary artifacts parsed rather than described, quotes with locators, no third-party files in the repository) and the per-source record shape, and wrote its notes to one file.

### What was produced

- Five notes files, about 95,000 words in all: `fanout-formats-baselines.md` (agent 1: dimensions 1, 8, 9), `fanout-identity.md` (agent 2: 6, 7), `fanout-bridge.md` (agent 3: 5), `fanout-hardware.md` (agent 4: 2) and `fanout-tools.md` (agent 5: 3, 4).
- `searches.md` 0.2.0: 147 queries and 63 tool runs added, with the agent's number on each row.
- `sources.md` 0.2.0: 175 source rows added, with the agent's number. Sources found by more than one agent are not merged yet; Phase 2 merges them into one library record each.

### What happened during the run

- All five agents stopped at the student's account usage limit (HTTP 429, "session limit") within a few minutes of each other. Four had written complete notes. Agent 2 had written sections 1 to 8 but not section 9 (rejected claims) or section 10 (open items), and its working context could not be resumed in the next session.
- At the student's request, a second agent finished agent 2's notes. It re-checked 95 of agent 2's claims against primary sources (75 held, 3 rejected as stated, 17 qualified) and wrote section 9, section 10 (open items, the other agents' notes to agent 2, notes for later phases) and a table of its own searches. It did not change sections 1 to 8: the main session confirmed the same word count (21,959) and the same last row.
- The session's scratch folder (the agents' downloads and the pilot's outputs) is no longer available to the main session. Nothing in the repository depends on it: the notes identify every file by URL and SHA-256.

### Edits the main session made to the agents' notes

- Redacted the names and email addresses of two Alpine package maintainers, quoted from SBOM output, in `fanout-formats-baselines.md` and `fanout-tools.md`, as the pilot does. The organizational security mailboxes that appear in CVE data (CNA and PSIRT addresses) were kept.
- Appended two "Not written" sections to `fanout-identity.md`; the second agent replaced them.
- Nothing else. Corrections are recorded below, not made in the notes, following RPT-0005's practice (DL-0013).

### Main-session spot checks

Seven claims that bear most on the report were checked again against their primary sources:

| claim | from | check | result |
|---|---|---|---|
| Syft writes SPDX 3.0.1 | agent 5 | ran `syft dir:. -o spdx-json@3.0` with Syft 1.52.0; read the v1.46.0 release notes ("SPDX 3 Support", 2026-06-26) | confirmed: `specVersion` 3.0.1 |
| Latest releases: Syft 1.54.1, Grype 0.120.1, Trivy 0.75.0, Dependency-Track 5.2.0, GUAC 1.1.0 | agents 3, 5 | GitHub releases API | confirmed, with the agents' dates |
| CycloneDX 2.0-dev has threat, risk, weakness, requirement, control, blueprint and physical modules; milestone 2.0 open, due 2026-08-31 | agents 1, 4 | GitHub contents and milestones API, branch `2.0-dev` | confirmed |
| SPDX 3.1-rc1 (pre-release, 2026-01-24) adds Hardware, SupplyChain, Service, Operations and FunctionalSafety | agents 1, 4 | GitHub release and `model/` folder at tag `3.1-rc1` | confirmed |
| CISA's 2026 Minimum Elements is final: version 2.1, published 2026-07-29, "updates and replaces" NTIA 2021 | agent 1 | downloaded the IC3 copy; SHA-256, `pdfinfo` and text | confirmed (SHA-256 `1faeda1e…3873`, 23 pages) |
| NVD removed its XML CPE dictionary (2025-08-20), enriches only prioritized CVEs, and passes through CNA "affected" data, whose `packageURL` "MUST NOT include a version" | agent 2 | nvd.nist.gov/general/news and `cve_affected_1.0.json` | confirmed (all three quotes and the field) |
| The pilot's unnamed CWE source `134c704f-…` is CISA-ADP | agent 3 | CVE-2025-60876 from the cveawg.mitre.org API | confirmed; `pilot.md` updated |
| Syft's CycloneDX root `version` depends on how the image is named | re-check of agent 2's notes | Syft 1.52.0 on `alpine:latest`, `alpine:3.24.2` and `alpine@sha256:294b683c…` | confirmed: the platform manifest digest, `3.24.2`, the index digest; `pilot.md` qualified |

### What was rejected, and why

- **"Syft cannot write SPDX 3"**, in the 0.1.0 report (§3 and §7, merged on `main`), the pilot, `dimensions.md` 0.3.0 (question 3.4), and agent 1's note to agent 5. Rejected: Syft has written SPDX 3.0.1 with `-o spdx-json@3.0` since version 1.46.0, and Syft 1.52.0, the version 0.1.0 used, does so (spot checks above). Its help text lists only SPDX 2 examples, which is the likely source of the error. The pilot and `dimensions.md` were corrected; the report's §3 and §7 will be corrected when the report is rewritten in Phase 5.
- **The pilot's "Syft puts the platform manifest digest in `metadata.component.version`"** as a general rule. Qualified: it holds only when the image is named `latest` (re-check of agent 2's notes, confirmed above). `pilot.md` now says so, and `dimensions.md` question 6.1 asks whether the anchor depends on how the image was named.
- The agents' own rejections are in section 9 of each notes file: 49 from agents 1, 3, 4 and 5 (14, 12, 11 and 12), and 20 from the re-check of agent 2's notes (3 rejected as stated, 17 qualified; agent 2's own rejections were lost).

### Suggestions from the re-check, accepted by the student

On 2026-10-08 the student asked for both of the re-check's suggestions, and `dimensions.md` 0.4.0 carries them:

- **A "Named by policy" column in Table 3.** Its example was checked against CISA 2026's own text: the Component Identifiers element "should use common software identifiers, such as" CPE and purl, and "may also include" UUIDs, organization-specific identifiers, commit hashes, OmniBOR and SWHID (IC3 copy, SHA-256 `1faeda1e…3873`). The column records how strongly each rule names a scheme, not only whether it does.
- **Five more failure modes that Table 3 must cover:** unregistered purl types, purl-shaped strings that are not purls, copies of one record that disagree, placeholder hashes, and inconsistent vendor names in NVD. Each has evidence in `fanout-identity.md` §9 and §10 (the type registry and ECMA-427, Syft's source code, Canonical's and OSV.dev's copies of one record, and Anwar et al.).

### Corrections for other documents (to pass on; not made here)

- **RPT-0004 0.1.0** (for Phase 5): the Syft error above; ISO stages out of date in §1 (DIS 27055 and DIS 27056 are at 40.00, DIS 5962 at 40.99; agents 1, 2); Dependency-Track's current release in §3 (5.2.0, 2026-10-08; agent 5); §5's statement that Alpine's feed lists neither CVE no longer holds for CVE-2026-85091 (agents 3, 5, and the pilot); §1.2's "needs only three things" needs a qualifier, because `name` is required by the model text but by neither the SHACL shapes nor the JSON Schema (agent 1).
- **RPT-0005** (for the student to pass to its author, for DL-0013): NVD's web status "Not Scheduled" is the API status "Deferred" by NVD's own table; `dataVersion` 5.0 occurs only on rejected CVE records; the pilot's "unknown UUID" is CISA-ADP; CycloneDX 1.7.2 is a GitHub release (2026-09-17) (agents 1, 3); and `fanout-attack-composition.md` §1.6 shortens the SHA-256 of `spdx-model.ttl` as `…a5c404c593`, where the full value in its own §10 ends `…d5f404c593` (main session).
- **RPT-0014** (source S-0840 summary): the AI profile property is `builtTime`, not "buildTime", and the model text requires it only for DatasetPackage (agent 1).
- **Library** (Phase 2): `cisa-2026-sbom-minimum` has empty metadata; `ecma-424`, `ntia-2021-sbom-minimum` and `iso-iec-5962` duplicate other records (agent 1).

### What a human accepted

- Pending: the student's review of the five notes files, the merged logs, and the corrections above.
- On 2026-10-12 the sponsor merged PR #110 (Phases 0 and 1) without review comments.

## Phase 2: library records, a first FX-1 test run (2026-10-15)

### Question asked

The student asked the agent to continue #38. Because PR #110 had merged, the agent asked first and the student chose: create new branches (PROC-0001 §2.1: never push to a merged pull request); extract one record first as a test run, with purl (ECMA-427) chosen over CoSWID (RFC 9393), the CISA 2026 Minimum Elements, or all of Phase 1's roughly 20 FX-1 candidates; and show the sponsor note before posting it.

### What changed since Phase 1

- The library fork was synced with upstream on 2026-10-09 (Threat-Radar/library#18), so it now follows the upstream FX-1 trigger: only the intent to extract a record triggers FX-1, and a summary-only pull request is allowed. This answers half of sponsor question 1 in `dimensions.md`; whether #38's stricter rule ("a spec record left at `summarized` is rejected") still holds was asked on #38.
- RPT-0005's author ran the same kind of one-record test run (CWE, Threat-Radar/library#21), so this pass follows that precedent.
- Upstream m-of-n/library adopted on 2026-10-13 a rule this fork has not synced yet: every file in `distilled/schema/` that the library wrote carries `.derived.` in its name. The extraction follows it.

### What was produced

Threat-Radar/library#24 (draft; branch `topic/rpt-0004-records`; CI green):

- A new topic, `product-composition` (owner: the student), for RPT-0004.
- A new record, `ecma-427` (ECMA-427 Package-URL specification, 1st edition, December 2025), FX-1 complete: 291 normative statements; 168 requirements; the Annex A JSON Schema verbatim plus a derived ABNF grammar for the purl string; 13 message structures with 65 fields; 54 example fixtures with expected and actual results; design notes mapped to tmodel decisions; and a verification log. Protocol and state machine are declared not applicable, with reasons.

### Method

- The PDF was fetched with `bin/ingest --fetch`; its SHA-256 (`037180df…3825`) matches the digest Phase 1 recorded on 2026-10-08. Text came from `pdftotext -layout`, and rendered page images were used wherever the text layer was ambiguous (tables, hyphenated line breaks, quote marks).
- Pass 1: five agents in parallel (normative text, requirements, schema and messages, examples, design notes), each reading the source and never a summary or another agent's output. Pass 2: an independent agent that did not extract. Pass 3: a cross-check agent. All at maximum effort, as `docs/extraction.md` and #38 require.
- ECMA-427 writes its provisions in lowercase ("shall", "should", "may"), so `bin/bcp14-count` finds only 2 keywords, both in licence text. The requirements file reconciles against the document's own baseline instead: all 108 lowercase occurrences are accounted for by line, as the library's ISO records already do.
- Local runs of every CI step: `bin/validate`, `bin/check-requirements`, `bin/check-artifacts`, `bin/export` and `bin/reindex`, the bibliography count, `bin/check-pr-extraction` and the sign-off check.

### Choices the agent made, open to review

- The record is the 1st edition, the adopted standard. The 2nd edition text (purl-spec v1.1.0, approved by TC54 on 2026-10-07 for the December 2026 General Assembly) will need its own record that supersedes this one.
- The schema file is taken from purl-spec tag v1.0.0, because the link Annex A prints for the electronic copy returns 404; the file was shown equal to the printed annex token for token.
- `bears_on` is DEC-001, DEC-002 and DEC-009, since the design notes route most adapt items to DEC-009 (generic to product mapping).
- The derived grammar makes five readings the text does not settle (R1 to R5 in `distilled/schema/README.md`), for example that a percent-encoded letter or colon is invalid rather than merely non-canonical.

### What was rejected, and why

The verify pass found 7 material defects in pass 1's output, all fixed: two "may look like a host" sentences filed as permissions, though they state a possibility; a claim that §5.6.6 (an empty qualifier value counts as absent) conflicts with Clause 2's rejection rule, withdrawn because the sentence itself says the pair is treated as absent; two entries that called inputs unspecified when a "shall" rule rejects them; a false claim that a type containing a period can never have a valid `$id`; a false claim that the text is silent on raw spaces (§5.4 requires `%20`); a 2nd-edition schema claim that holds for the repository file but not for the 2nd edition's own Annex A; and a design-notes sentence that called parsing fully defined. Pass 3 found no wrong requirement labels and fixed one contradiction between files. Details are in `distilled/verification.md` in the record.

### Findings for the report (Phase 5) and for tmodel

- The 1st edition requires one canonical form for equivalent purls (Clause 2) but never fixes the order of qualifiers and never states the "equivalence rules" it names.
- packageurl-python 0.17.6, the package-url project's own Python library, accepts and rewrites several inputs the standard says to reject.
- Between purl-spec tags v1.0.0 and v1.1.0, the npm and golang type definitions changed `case_sensitive` from false to true, so the same two strings stopped naming one package.
- In tmodel's own vectors, four `oci` purls use a namespace that the `oci` type definition prohibits (for #15 and #17; not changed here).

### Sponsor questions posted

On 2026-10-15, at the student's request, the agent posted four questions on #38: the FX-1 bar for RPT-0004's other specs; who extracts CycloneDX 1.7 and SPDX 3.0.1 (both owned by the upstream `sbom` lane); access to ISO/IEC 19770-2 and 19770-6; and Part B's licensed-text choice (hold 1 from #69). It also asked whether part A continues through I2, since the open SOW (#125) ends report work on October 13.

### What a human accepted

- The student chose purl as the first record, approved committing and pushing the extraction to the draft pull request, and approved posting the sponsor questions.
- Pending: human review of the extracted artifacts (`reviewed_by` is empty on every one).

## Table 6: composition to model-input mapping (2026-10-18)

### Question asked

The student asked what #38 contributes to the app build. The agent answered that Table 6 is the input contract for bringing radar output (an SBOM and a vulnerability scan) into the engine, and the student asked it to "complete table 6".

### What was produced

- `research/0004-product-composition/mapping.md` 0.1.0: Table 6 in six parts (6a product, instance and SBOM; 6b components; 6c structure and parties; 6d vulnerabilities and weaknesses; 6e hardware and firmware; 6f the core classes composition does not feed), 11 findings, a summary for an importer of radar output, and 20 candidate rules with ids.
- `dimensions.md` 0.6.0: a status line under Table 6 pointing to mapping.md.
- `searches.md` 0.3.0: the runs behind mapping.md.
- `report.md` 0.1.1: the corrections this log listed in Phase 1 for Phase 5 ("Corrections for other documents"), applied now instead, because RPT-0005 cites §3 and §5 and Table 6 is going to reviewers: Syft writes SPDX 3; the ISO stages; Dependency-Track 5.2.0 and its Snyk analyzer; §1.2's qualifier; and database dates on the §3 and §5 scan results. A note at the top lists them. The input-contract notes now defer to mapping.md.
- In the same change, real names were replaced by GitHub ids: `dimensions.md` (Phase 6 row), this file's header, and the `authors` id in RPT-0004 and RPT-0007 (both now 0.1.1), as `CLAUDE.md` requires.

### Method

- Targets re-pointed from the pilot's draft schema to the core type system ADR-0010 accepted (DEC-001a), at `main` 9f56628. Slot lists, vector edges and identifier prefixes were read from the files, not from summaries.
- Syft 1.52.0 and Grype 0.119.0 (the pilot's versions) re-run on the pilot's image, named by its platform manifest digest, in four SBOM formats including SPDX 3.0.1; Grype with the 2026-10-17 database. Every count in the tables was computed with `python3` from these outputs.
- The CycloneDX 1.7.2 schema and the three SPDX 3.0.1 files re-fetched; all four digests equal those already recorded. Every format field, enum value and class named in the tables was looked up in them.
- Three fact-check agents in parallel, each told to report only: format cells, tool and tradar cells, and claims about tmodel's own documents. The main session re-verified each material finding against the source before fixing it.

### Choices the agent made, open to review

- Table 6 lives in its own file until Phase 5, so `report.md` 0.1.0 stays as merged.
- The image was named by digest, so the input bytes equal the pilot's. The cost: the index digest appears in no output (finding recorded in Table 6a and R-ID-1).
- "Routes to" names deciders only; requirements appear as "bound by".
- Rules keep agent 2's ids (R-ID-1 to R-ID-5, R-MERGE-1 and 2, R-BUILD-1) and add new ones in the same style.
- Table 6e (hardware) is not backed by a tool run, because no surveyed tool produces a hardware bill.

### What was rejected, and why

The checkers reported 46 findings, 45 of them distinct. All were accepted; none was rejected. The material ones, which were the agent's own errors:

- **Model and decisions (20).**
  - R-MATCH-1 said the vectors derive Product-level `affects` by propagation; they set `affects` by hand.
  - The importer summary called per-build composition and component suppliers lost, though the tables carry both as Assertions, and it left out seven lost items.
  - The Scores row had no "Lost" entry, though Vulnerability has no slot for a score.
  - The introduction called the table the specification for "the scanner half of the library loader (#60)". #60 loads library records; the table now points at an importer under `engine/load/`, which no issue owns.
  - `instance_of` was attributed to ARCH-0001 §3, which lists the edge without its ends; PLAN-0002 §5 is the document that names it as the CVE-to-CWE link.
  - The proposal's §8 was misquoted.
  - "A change to a core class is a change to ADR-0010" was wrong: an accepted ADR changes only to record that it is superseded.
  - Four readings were stated as facts (finding 8, R-EDGE-3, R-ID-4's post-MVP scoping, the capture-stage row).
  - Routes listed requirements as deciders, sent two rows to DEC-008 outside its question, left out DEC-009's mitigation-lifecycle half, and left ADR-0001 off the platform-changes row.
  - Six smaller precision fixes.
- **Tools and tradar (11).**
  - "Syft JSON labels all three digests" held for the pilot's scan by tag, not for this scan by digest.
  - tradar does add `CONTAINS` edges through `env build-graph --merge-scan`.
  - Its saved scan files drop data source and namespace. Its raw-JSON path reads `fix.versions[0]`, which fails on an empty list. This became mapping.md finding 11.
  - Eight smaller precision fixes.
- **Formats (15, one shared with the tools checker).**
  - `metadata.manufacturer` is the organization that created the BOM, not the product's maker.
  - R-COMP-1 claimed CycloneDX's schema is silent on a missing `dependencies` entry. The `dependency` definition answers it ("may have unknown dependencies"). The agent's own check had read the wrong description.
  - `usesTool` is not limited to build and test time.
  - The OS survives in SPDX as a purl qualifier.
  - CycloneDX file components are not linked to their packages.
  - Two hardware marks were too strong.
  - Several SPDX names lacked their JSON-LD prefixes.
  - Five rows lacked marks.
  - Four smaller precision fixes.

### Findings for #15, #17 and the importer

mapping.md §3 lists them. The ones a reviewer should see first:
- the CVE-to-CWE link is missing from every MVP vector, though their README says it is there (finding 7);
- SBOM and scan formats are not on ADR-0007's import list (finding 8);
- the vectors use ten unregistered identifier prefixes (finding 9);
- the pilot's findings 1, 2, 4 and 5 still stand against the accepted core.

### What a human accepted

- The student asked for Table 6.
- Pending: the student's review of mapping.md and the commit.
- A teammate (@paria03) reviewed #127 on 2026-10-18 and found three problems, all fixed in mapping.md 0.1.1:
  - Finding 11 said 29 of the 30 matches "have one", meaning an empty `fix.versions`; it now says so. Table 6d's "3 empty" meant an empty `state`, not empty versions, so the two read as a contradiction. The cell now gives each state and says `versions` is empty on all 29.
  - §8 cited Syft 1.54.1's 71 catalogers, a Phase 1 figure, though these runs used Syft 1.52.0. Syft 1.52.0 was listed too (69 catalogers, none for hardware or firmware; `searches.md` 0.3.1), and §8 now cites both.
  - The pull request's description still named DL-0015 0.6.0; it now gives the current versions.

## Phase 2: honest stubs for the remaining sources (2026-10-18)

### Question asked

The student asked whether #38 was finished. The agent answered that Phase 2 was furthest behind: of the roughly 110 records RPT-0004 needs, about 92 did not exist. Asked how long Phase 2 would take with five subagents, the agent estimated 2 to 3 hours for honest stubs and days for full extractions. The student chose the stub route at maximum effort, which #38's definition of done allows ("FX-1 complete or an honest stub").

Earlier the same day, at RPT-0005's request (#39), the student took over `cyclonedx-1-7` and `spdx-3-0-1` from the upstream `sbom` lane and made both honest stubs (Threat-Radar/library#26).

### What was produced

- Threat-Radar/library#27: 86 stub records. By type: 38 spec, 13 dataset, 13 paper, 8 repo, 5 rfc, 4 web, 2 article, 1 book, 1 draft and 1 note. Each has `status: stub`, `owner: Clovier`, `topic: product-composition`, the pinned version, a SHA-256 where one can be taken, and a summary whose Limits section says what was checked.
- Implementations entries instead of records, under the library's rule (docs/scope.md §3):
  - cosign and actions/attest under `sigstore-bundle-v0-3`;
  - python-uswid and coreboot under `rfc-9393`;
  - PACCOR and HIRS under `tcg-platform-certificate-profile-2-1`;
  - spdx3-validate, spdx/tools-golang and the OpenEmbedded-Core SPDX 3.0 classes under `spdx-3-0-1` (Threat-Radar/library#26).
- `dimensions.md` 0.7.0: a status line under Table 9 and on sponsor question 2.

### Method

- **Merging.** The agent merged the 219 source rows of `sources.md` into 160 sources, matching them by URL and record id. It set aside the 17 that already have a record and the sources that need none, and split the remaining 86 into five batches: formats and policy; identity and build; vulnerability data and version ordering; hardware and firmware; tools and papers.
- **Research.** Five research agents, at maximum effort, took one batch each. They gathered metadata only and edited no repository. Each returned JSON for its sources:
  - title, version, publisher and date;
  - maturity, only where the source states its standing;
  - identifiers and licence;
  - the SHA-256 of the bytes it fetched;
  - a one- or two-sentence overview.
- **Independent check.** The main session re-fetched every source with its own script and recomputed each digest. TCG and CISA block scripted downloads, so those digests were confirmed against Internet Archive copies.
- **Building.** It created each record with `bin/ingest --stub`, filled it from the checked data, and ran every library CI step locally.

### Choices the agent made, open to review

- **Tools.** Tools that implement a spec the library holds became implementations entries, not records (scope §3). Syft, Grype, Trivy, Dependency-Track, OSV-Scanner and tradar got records anyway, because RPT-0004 studies their own behaviour, which no specification defines.
- **No new record** for:
  - sources already held: FIPS 203 and 204, SLSA 1.2, the OSV schema and in-toto;
  - sources in open pull requests: `ecma-427` and `nvd-cve-api-2-0`;
  - the CycloneDX HBOM capability page, a secondary summary (scope §2);
  - unreleased drafts: CycloneDX 2.0-dev and SPDX 3.1-RC1;
  - the team's own scan outputs and test inputs.
- **Folded into another record:**
  - the CISA HBOM fact sheet and the UEFI 2024 Plugfest deck, mentioned in their records' Limits;
  - the IANA gitoid registration, an identifier on `omnibor-spec`;
  - ISO/IEC 18670:2025, an identifier on `swhid-spec-1-2`.
- **Shared ids.** Three ids are RPT-0014's canonical ids (`cert-in-2025-aibom-guidelines`, `lf-2024-spdx3-aibom` and `nocera-2025-aibom-mlr`), so the two reports share one record each.
- **Zephyr.** Its `west spdx` is recorded nowhere: v4.4.2 writes only SPDX 2.2 and 2.3, and the library has no SPDX 2.3 record.

### What was rejected, and why

- **Agent output the main session changed:**
  - The PCIe registry id became `tcg-pcie-component-class-registry-1-0-r18`, matching its sibling `tcg-component-class-registry-1-0-r14` and the cover's "Version 1.0".
  - The two IANA registries moved to the `iso` shelf, where the library's other IANA records sit.
  - Maturity `best-practice` on the five NIST IRs was dropped, matching `nistir-8547` and `nistir-8610`.
  - Identifier keys that are not identifiers were removed: archive copies, TLP markings, extra page URLs and the draft name on RFC records. Archive copies moved to the Limits text.
  - Licences that GitHub reports as NOASSERTION were replaced by what the projects' own licence files say.
  - The HIRS entry was reworded. HIRS v3.2.0 implements Platform Certificate profile 1.1 r15, with 2.0 in development; it does not claim 2.1.
  - The Debian tracker's date was cleared, because a live feed has no publication date.
- **The agent's own errors:**
  - The keyword patterns that attached `sources.md` rows to records also matched numbers inside SHA-256 values ("7698", "9124"). One agent caught it and left those rows' decision ids out. An audit with digests stripped found no other case.
  - Rebuilding the record folders inside the file-synced Desktop folder left 17 duplicate files (`record 2.yaml`, `summary 2.md`) in the first commit. A second commit removes them.

### Findings for the report (Phase 5) and for tmodel

- **report.md:**
  - ISO now lists SPDX 3.0 as ISO/IEC PRF 5962 at stage 50.00; §1 and §7 still say DIS at 40.99.
  - ISO Guide 69:1999 was withdrawn in 2014. §1.3 can cite ISO's stage-codes page instead; the meaning of 90.60 has not changed.
  - ISO/IEC 19770-2:2015 was confirmed in 2021, and a second review closed on 2026-06-05 with its outcome pending.
  - The CycloneDX bom-examples VEX cases behind the comparison table are CycloneDX 1.4 files, not 1.7.
  - The Commission's CRA guidance, C(2026) 5252, is formally still a draft.
- **sources.md and the Phase 1 notes:**
  - Shortened digests with wrong endings: L106 to L108 (NIST IR 7695, 7696 and 7697), L110 (RFC 9393), and two in `fanout-bridge.md` §1.11.
  - The BSI URL at L92 returns HTML unless `?__blob=publicationFile` is added.
  - Row L164 (trivy-db) belongs with Trivy, not the GitHub Advisory Database.
  - The Red Hat VEX counts in `fanout-bridge.md` §1.9 are stale: the file was regenerated on 2026-10-15 with different content.
- **Facts for Phase 5:**
  - CISA Vulnrichment stopped adding CPE strings on 2024-12-10.
  - The osv.dev FAQ itself says it computes purls on import; Phase 1 had marked this as our reading.
  - The SUIT manifest draft is waiting on five unpublished SUIT drafts it cites.
  - uSWID is a header defined by python-uswid and required by OSFW §4.6, not a standard.
  - Yocto 5.1 emits SPDX 3.0.0, and 5.2 onward 3.0.1. tools-golang's SPDX 3.0.1 support is not yet in a release.
  - The semver.org page differs from the 2013 v2.0.0 tag on build metadata: it says MUST be ignored where the tag said SHOULD.

### What a human accepted

- The student chose the stub route, five subagents and maximum effort.
- Pending: review of the 86 records in Threat-Radar/library#27, and the sponsor's answers to sponsor questions 1 and 2 on #38.
- Later the same day the student merged Threat-Radar/library#26 and #27.

## Library pin, Table 9 and report 0.1.2 (2026-10-18)

### Question asked

With Threat-Radar/library#26 and #27 merged, the student asked for one tmodel change that points tmodel at the merged records, updates the record ids in `sources.md`, and fixes the three report errors the Phase 2 agents found.

### What was produced

- **The library pin** moves from `b3786cd` to `a28a013`, which adds 25 library commits, including library#26 and #27. `bin/validate` passes at `a28a013`: 550 records, 0 errors.
- **`sources.md` 0.3.0** adds Table 9: each cited source with the record it became and that record's status before and after Phase 2, or why it has none. It also updates the two rows that still said `queued`.
- **`report.md` 0.1.2** applies the three corrections, with a note at the top.
- **`dimensions.md` 0.7.1** points the Table 9 status line at `sources.md`.

### Method

Each correction was re-checked against its primary source on 2026-10-18:
- **The SPDX 3.0 stage:** ISO Open Data's deliverables file of 2026-10-14 lists ISO/IEC PRF 5962 at stage 50.00. Stage names come from ISO's stage-codes page.
- **ISO Guide 69:1999:** its ISO catalog page shows stage 95.99, withdrawn on 2014-06-18.
- **The CycloneDX VEX examples:** all four `Case-1` files in CycloneDX bom-examples declare `specVersion` 1.4 and were last changed on 2022-03-23. All four states they use are in the CycloneDX 1.7 schema's `impactAnalysisState` list.

Table 9's statuses were read from the library at `a28a013`.

### Choices the agent made, open to review

- **Layout.** The earlier rows of `sources.md` stay as the log of what each pass found. Table 9 is added at the end rather than rewriting about 220 rows, and the top of the file points to it.
- **Records that don't meet #38's rule.** Mapping every source showed that eight cited records owned by others sit at a status #38 rejects for specs (`summarized` or `queued`): `cisa-framing-software-component-transparency`, `ntia-sbom-minimum-elements`, `iso-iec-5962-2021`, `osv-schema`, `cve-json-5`, `in-toto-attestation-v1`, `fips-203` and `fips-204`. Table 9 lists them as they are. The sponsor's answer to RPT-0005's question on #39 (do spec summaries need to become stubs?) settles them.

### What a human accepted

- The student asked for this change.
- Pending: review.

## Table 7 ratings (2026-10-19)

### Question asked

After Threat-Radar/library#28 and #29 were submitted for review, the student asked to start the Table 7 ratings: the five-axis applicability rating that `dimensions.md` requires for every kept source (step 3 of the #38 playbook, "Distill and rate").

### What was produced

- **`sources.md` 0.4.0** adds Table 7 just before Table 9. It has 121 rows, one per Table 9 row, each rated 0 to 3 on Object model, Provenance/attribution, Human review/audit, Federation and AI-grounding. Every cell gives the field or section behind its rating and a locator, and a `basis` column says where the rating comes from. The section also has the conventions used, a summary by axis, every disagreement settled, and the calls a human reviewer should check.
- **`dimensions.md` 0.7.2** adds a status line under Table 7.

### Method

- **Inventory.** A script listed Table 9's 121 rows and the 92 rating rows in the five fan-outs' section 4 tables, and matched them by name. The match was crude (it placed 70 of the 92), so it was only a starting list for the agents.
- **Five rating agents** (Claude Code), one per batch: identity and naming (25 rows), formats and baselines (27), hardware and firmware (27), the bridge to vulnerability data (24), and tools and studies (18). A shared brief gave them the rubric; where every earlier rating is (the five fan-outs, the pilot, and RPT-0005's Table 5 ratings); how to carry over, reconcile or newly rate a source; and the hard rules: cite a field or section for every rating and never invent one, mark what cannot be read with `?`, send no personal data, and write nothing in tmodel or the library.
- **Result.** 56 rows carry one earlier rating, checked against the fan-out's evidence (a few values changed, each with its reason). In 21 rows earlier ratings disagreed and one value was chosen on each axis. 40 sources were rated for the first time from their own text, and 4 rows are `n/a`.
- **Sources read again.** The agents fetched about 130 public files: arXiv papers, RFCs, NIST, IANA and ISO pages, UN documents, GitHub files at pinned commits, and Internet Archive copies of cisa.gov files that refuse scripted downloads. Each download was compared with the library record's digest where one exists. All matched except two dynamic web pages, a Red Hat blog post and the UEFI blog post, whose HTML has changed; the Red Hat post's text still holds the passages Phase 1 quoted. No request carried an email address or other personal data.
- **Merge.** The coordinating session merged the five tables in Table 9's order. It applied one convention to rows that cover more than one document (the higher value on each axis, which changed row 107's Federation from 2 to 3), and removed notes that referred to the agents' own working files.

### Choices the agent made, open to review

- **The conventions** stated above Table 7 in `sources.md`: how papers, regulations, guides, combined rows, signatures and paywalled texts are rated.
- **The calls listed under "For a human reviewer"** in `sources.md`, among them that row 1's AI-grounding leans on the open FX-1 extraction in Threat-Radar/library#24. Rows 8 and 68 also cite the open extractions in #28 and #29, but their values do not depend on them.
- **Placement.** Table 7 sits just before Table 9 in `sources.md`, where `dimensions.md` puts it ("Table 7 in sources.md"), and follows Table 9's row order, so each rating traces to its record.

### What a human accepted

- The student asked for this work.
- Pending: review.
- A teammate (@Maimcghee) reviewed #133 on 2026-10-19. She checked the row numbering against Table 9, the counts by axis, the RPT-0005 ratings that Table 7 cites, and the front matter, but not the ratings against their sources. Her three notes, none blocking, are fixed in `sources.md` 0.4.1 and `dimensions.md` 0.7.3, and no rating changed:
  - `sources.md` and `dimensions.md` said the report's §11 "summarizes" the ratings in 0.2.0, but `report.md` is still 0.1.2 and ends at §7. Both now say it will.
  - Row 68 was described two ways. The conventions said its values do not depend on the open extraction in Threat-Radar/library#29, while "For a human reviewer" and this entry said row 68 leans on it, and its AI-grounding cell gave the FX-1 requirement ids as the reason. The conventions were right: row 68's AI-grounding 3 is fanout-identity's rating, made before the extraction existed, and its Object model 2 is RPT-0005's. Row 68's cells, "For a human reviewer" and this entry now say so.
  - Row 3 said RPT-0005 rated the SPDX Security profile 1 on Human review. RPT-0005's `report.md` Table 5 gives 2, the value Table 7 chose; the 1 is in its fan-out notes (`fanout-vuln-data.md` §6). Row 3's `basis` cell and its entry under "Disagreements settled" now name that file.

## Report 0.2.0: Tables 1 and 2, §1.4 to §1.6 (#147, 2026-10-22)

### Question asked

With #131 and #133 merged, the student asked to continue #38 with `report.md` 0.2.0, starting with sub-issue #147: Table 1 (formats at a glance) and Table 2 (minimum-element crosswalk) at the front of the report, and §1's new questions 6 to 8. The student chose one branch and one draft pull request for all of 0.2.0 (`topic/rpt-0004-report-0.2.0`), a stop for review after each sub-issue, and one fact-check agent per sub-issue.

### What was produced

- **`report.md` 0.2.0, in progress:** a status note at the top; "Comparison tables" with Table 1 and Table 2, which replace 0.1.2's table of CISA's 2024 attributes and its "five questions" table; the VEX status table, unchanged because RPT-0005 cites it; and three new sections: §1.4 (the SPDX 3 RDF model), §1.5 (validation in every format) and §1.6 (what changed, and what comes next).
- **`dimensions.md` 0.7.4:** a Validation row in Table 1's plan, and a status line under Table 2.
- **`searches.md` 0.3.2:** the release, milestone and record checks of 2026-10-22.

### Method

- The text is condensed from Phase 1's notes (`fanout-formats-baselines.md`, sections 2 and 3), with every correction this log has recorded since then applied: Syft writes SPDX 3.0.1 (`-o spdx-json@3.0`); the ISO stages from the file of 2026-10-14; and the record statuses at `a28a013`, where both format records are now stubs.
- Release and milestone status was re-checked on GitHub on 2026-10-22, and every cited record id was looked up in the library at `a28a013` (`searches.md`).
- One fact-check agent (Claude Code) checked every new claim against its primary source; see "Fact-check" below.

### Choices the agent made, open to review

- **Table 1 adds a Validation row** beyond the plan's list, as Phase 1 suggested; it points at §1.5.
- **No extra columns in Table 1.** SPDX 2.3, CycloneDX 2.0 and SPDX 3.1 are discussed under the table and in §1.6 instead.
- **Table 2 replaces 0.1.2's CISA 2024 table.** Its "Required by" column keeps the CISA 2024 levels, and its notes keep CISA 2024's official mappings.
- **§1.5 shows all 31 sampled rules** (X7 and X8 share a row), so the argument is in the report and not only in the notes.
- **Version 0.2.0 is set at the first sub-issue,** with a note at the top saying what is done so far; the pull request stays a draft until #151.

### Fact-check

- **The agent.** One fact-check agent (Claude Code; about 476,000 tokens, 189 tool calls, 33 minutes) checked the new text against primary sources it fetched itself: the CycloneDX schemas at 1.6.2 and 1.7.2, ECMA-424, the SPDX 3.0.1 model, context, JSON Schema and examples, the SPDX annex, RFC 9393, NIST IR 8060, the SWID XSD, the CISA 2026, NTIA 2021 and CISA 2024 documents, BSI TR-03183-2, CERT-In 2.0, the FDA guidance, the CRA (from the EU Publications Office, because EUR-Lex refused scripts), OMB M-26-05, the IANA registry and ISO Open Data. It re-ran Syft 1.52.0 on the pilot's image and plain pySHACL and spdx3-validate on the examples. Every source digest matched the notes except the IANA CSV, which has a new hash and the same nine rows. It sent no email or other personal data, and it did not use Crossref.
- **What it confirmed.** 30 of Table 1's 39 cells exactly; all 23 of Table 2's CISA 2026 change labels and every other baseline level except those below; all of Syft's counts but one (below); and the §1.4 to §1.6 claims except those below, including every quoted rule in §1.5.
- **Its 21 findings, all applied.**
  - **Errors:**
    - FDA was missing from six Table 2 rows its baseline covers.
    - CISA 2024, CERT-In and BSI entries were missing from three practice rows.
    - CERT-In does recommend signing (§5.4).
    - The counts were off: 9 BOM-Link places, not 10; 13 objects with a signature, not 16; 11 CDDL group sockets plus 5 enumeration sockets, not 7.
    - Syft leaves out 83 dependency entries, not 5.
    - SPDX 3.0's ISO stage moved to 50.20 on 2026-10-21.
    - "Versions must be SemVer" was too broad.
    - #1158's summary fitted AI packages only.
    - The milestone counts mix issues and pull requests.
    - SPDX's hardware purposes include `deviceDriver`.
    - "What Table 2 shows" listed only three of Syft's six misses.
  - **Precision and citations:** a paraphrase shown as a quote (CycloneDX's licence choice); a top-level `@vocab`, not none; spdx3-validate is used by the SPDX specification repository but is not SPDX's own; test ids; and eleven smaller wordings.
- **Applied differently.**
  - The keyword counts in §1.5 now say "more than 700" and "more than 50", because the exact numbers depend on whether "shall not" and "must not" are counted.
  - The forward reference to §8 now says it is to be written for #150.
  - The extraction question now points at sponsor questions 1 and 2, since both bear on it.
- **Main-session spot checks** of four findings against the agent's downloads (13 signature objects, 47 unique-item arrays, 9 BOM-Link places, PRF 5962 at 50.20) agreed; see `searches.md`.
- **Not checked:**
  - PyLD (T4), the SWID `xmllint` tests (T13), and the single mutations other than M9 and M11 were not re-run.
  - The cryptographic-asset fields added in 1.7 were not itemized.
  - The RFC 3339 and RFC 9557 reading stays "our reading".

### What a human accepted

- The student asked for this work and made the three choices above.
- Pending: review.

## Report 0.2.0: §2 to §4, Tables 4 and 5 (#148, 2026-10-22)

### Question asked

After #147, the student said to continue #38; the next sub-issue is #148: §2 with Table 4 (hardware and firmware coverage) from `fanout-hardware.md`, §3 with Table 5 (tools) from `fanout-tools.md`, and §4 re-checked against tradar's `main`. The student's earlier choices hold: one branch and one draft pull request, a stop for review after each sub-issue, and one fact-check agent per sub-issue. #147 was committed at the student's word ("commit #147") before this work began.

### What was produced

- **`report.md`, §2:** the 0.1.2 text kept where it still holds, with CISA's 2023 mapping counts set beside our reading of the current schemas; Table 4 in two parts (4a bills and guidance, 4b identity and attestation standards); and new paragraphs for questions 3 to 9: how firmware is tied to a device, buses and cores, firmware bills in practice, attestation as a measured bill, ISO/IEC 19770-6 (from public metadata and its preview only), hierarchical systems and vehicles, and guidance beyond CISA.
- **`report.md`, §3:** the second round of tool runs (2026-10-08: four inputs, Syft 1.54.1, Grype 0.120.1, Trivy 0.75.0) beside the first; Table 5; the SPDX 3 support table; and new or rewritten paragraphs on Dependency-Track 5, GUAC's graph model and deps.dev.
- **`report.md`, §4:** re-checked against tradar's `main` (still `26d9c76`), with Phase 1's three nuances and its new facts on what reaches the graph.
- **`dimensions.md` 0.7.5** and **`searches.md` 0.3.3:** status lines and the checks of 2026-10-22.

### Method

- The text is condensed from Phase 1's notes, with this log's later corrections applied: uSWID is a header defined by python-uswid and required by the firmware SBOM specification, not a standard; Yocto 5.1 writes SPDX 3.0.0 and 5.2 onward 3.0.1; the SUIT manifest waits on five unpublished drafts; spdx/tools-golang still has no final release with SPDX 3.0.1; and the qualified tradar claims (`manifestDigest`, the GHSA ids named `cve:`).
- On 2026-10-22: the latest tool releases and their notes, the two SPDX 3 issues, tradar's `main`, and every cited record id at `a28a013` (`searches.md`). The tools were not run again: the newer releases change no format support.
- One fact-check agent (Claude Code) checked the new text against primary sources; see "Fact-check" below.

### Choices the agent made, open to review

- **Table 4 keeps the plan's rows** and does not split the last row ("measured identity") into device evidence and supplier references, which Phase 1 suggested; the intro and the cells say which each is.
- **Table 4 has no ISO/IEC 19770-6 column,** as the plan allows when no copy can be read.
- **Two draft columns** (the CycloneDX 2.0 and SPDX 3.1 development branches) are in Table 4a, marked unreleased, because they are where hardware support is moving.
- **The 47-field crosswalk** stays in `fanout-hardware.md` §3.3; the report gives its counts.
- **Table 5 pins the versions run on 2026-10-08,** and the text names the newer releases instead of re-running them.

### Fact-check

- **The agent.** One fact-check agent (Claude Code; about 606,000 tokens, 318 tool calls, 57 minutes) checked the #148 part of the version note, §2 with Tables 4a and 4b, §3 with Table 5 and its three smaller tables, and §4. It used primary sources it fetched itself:
  - the CISA HBOM framework (from the Wayback Machine, because cisa.gov refuses scripts; the digest matched), NTIA, CERT-In 2.0, Auto-ISAC, UN R155 and R156, ITU-T C548, ISO Open Data and the BSI preview of ISO/IEC 19770-6;
  - the CycloneDX 1.7.2 schema and property taxonomy, the CycloneDX 2.0 and SPDX 3.1 development branches, and SPDX 3.0.1;
  - the TCG, DMTF and IETF documents of Table 4b;
  - the firmware SBOM specification 0.10, python-uswid, coreboot, the UEFI material, Yocto and Zephyr;
  - the source of Syft, Grype, Trivy, GUAC and Dependency-Track at the pinned tags, with their documentation;
  - deps.dev, where it repeated 3 of the 15 live calls.

  It re-ran Syft 1.54.1 on the pinned image digests after checking the release checksum. It also re-ran Grype 0.120.1 and Trivy 0.75.0 with the exact databases of 2026-10-08, which can still be downloaded and whose digests matched the notes. It read tradar at `26d9c76` without running it. It sent no email or other personal data, and it did not use Crossref.
- **What it confirmed.**
  - Every count in the composition and matching tables, including Trivy's 0.1.0 tradar figures, re-run with the database of 2026-09-30.
  - Table 5's Syft cells; all four SPDX 3 files are valid against the 3.0.1 JSON Schema.
  - The release dates, and that the newer releases change no formats.
  - CISA's 47 fields, its 37 and 36 unmapped fields, our 24 = 9 + 15, 19 = 7 + 12, 40 and 38, and all 13 CISA quotes.
  - Table 4b's standards and versions.
  - Every code locator in §4 at `26d9c76`.
  - All 33 cited record ids at `a28a013`.
- **Its 17 findings, all applied.**
  - **Errors:**
    - GUAC's deps.dev certifier adds dependencies, source links and Scorecard results, not vulnerabilities (Table 5 and §3).
    - Three Dependency-Track quotes came from its version 4 documentation, not version 5's.
    - GUAC v1.1.0 pins tools-golang v0.5.5; only its `main` pins v0.5.7.
    - The log4j SBOM has no dependency links.
    - Trivy reads the Python and Java packages in Syft's SPDX 2.3 files (tradar 15, log4j 7); only the two images give nothing.
    - SPDX 3.1's `Hardware` requires `partNumber` and `productAgent`; `category` is optional.
    - On Alpine, Grype adds 14 CVEs that Trivy lacks, not 13; the 14th is busybox's CVE-2025-60876.
  - **Overstatements and citations:**
    - "No digest" in the CISA framework is our reading, because its hash fields are described as identifiers.
    - Not every source names firmware.
    - LVFS's export is now cited to the firmware SBOM specification §7.6, and CBFS to coreboot's documentation.
    - "HIRS at version 1.1 r15" had no source for "r15".
    - Two interpretations now say "our reading".
    - 4 of GUAC's 86 edges have no reverse.
    - tradar's converter is also called from tests.
    - tradar can also ask Syft for Syft JSON, table or text.
    - Syft's suppliers come from package metadata, not only maintainer fields.
  - **Minor:**
    - Grype also reads a CPE file, and Syft also writes SPDX 2.1 tag-value.
    - CISA §1.3 is now quoted in full.
    - R156's register is kept per RXSWIN.
    - Table 4's marks are adapted from RPT-0005, which marks absence with a dash.
    - "Hardware support beyond a purpose label".
    - GUAC's documentation lives in a separate repository.
    - tradar's helpers also read Syft's own properties.
- **Applied differently.**
  - Dependency-Track's hardware advice is kept, labelled as version 4's, beside version 5's statement that NVD is "the broadest source for non-package software (operating systems, firmware, network equipment)". The agent suggested dropping it or labelling it.
  - The PACCOR and HIRS sentence is rewritten from their READMEs and HIRS's documentation: PACCOR supports 2.1 but writes 1.1 by default, and HIRS validates 1.1, with 2.0 in development.
  - "It cannot read SPDX 3 at all" is said of the format, not of each file. Trivy's format detection (`pkg/sbom/sbom.go:105-117`) does not recognize SPDX 3, and only Alpine's SPDX 3 file was run.
- **Corrected in our own log.** `searches.md` said §2 to §4 cite 28 records. They cite 33: 31 stubs, plus `guac` and `ntia-sbom-minimum-elements`, which are summarized.
- **For the library repository.** The `tcg-platform-certificate-profile-2-1` stub carries the same unsupported "1.1 r15" for HIRS, in `record.yaml` and `summary.md`. It needs fixing there, not from this checkout.
- **Main-session spot checks** agreed with the agent; see `searches.md`. They covered 12 findings (F1 to F3, F5, F6, F8, F10, F11 and F13 to F16) and four minor fixes, against the agent's downloads and runs and three read-only GitHub API calls (the HIRS README and v3.2.0 notes, and the PACCOR README).
- **Not checked:**
  - The 0.1.0 Grype figures and the 0.1.0 Trivy Alpine "0". The Grype databases of 2026-09-28 and 09-30 were never recorded, and the Trivy database of 09-28 was not fetched.
  - "CISA has not updated the framework since" rests on the Wayback copy.
  - The remaining 12 of the 15 deps.dev calls.
  - "Syft's documentation lists no dictionary lookups for Alpine" was checked in Syft's source only.
  - Some details were checked at term level only: CoRIM's triple semantics, EAT's measurement contents, Redfish's cable and `Port` details, and Yocto and Zephyr naming hardware only as a build input.
  - PACCOR has since released v2.0r17 (2026-10-13). The report keeps v2.0r16, the release Phase 1 recorded.

### What a human accepted

- The student asked for this work.
- Pending: review.
