---
schema: "archdoc/v1"
id: DL-0015
title: "RPT-0004 second pass: AI-assisted scoping, survey, extraction and mapping"
type: process
status: draft
version: "0.6.0"
date: "2026-10-08"
updated: "2026-10-18"
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
