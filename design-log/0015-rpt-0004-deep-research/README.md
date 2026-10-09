---
schema: "archdoc/v1"
id: DL-0015
title: "RPT-0004 second pass: AI-assisted scoping, survey, extraction and mapping"
type: process
status: draft
version: "0.3.0"
date: "2026-10-08"
updated: "2026-10-08"
record: DL-0015
---

# DL-0015: RPT-0004 second pass, product composition

AI-assisted research record for #38 part A (Product Composition, the second pass on RPT-0004), per `CLAUDE.md`. Student: Tyler Van Heerden, working with Claude Code. This entry is extended at each phase of the #38 playbook.

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

### Suggestions from the re-check, not applied (open to review)

- A "Named by policy" column for Table 3 (CISA 2026 names CPE and purl). This changes the Phase 0 scope, so it is left for the student to decide.
- More failure modes for Table 3: unregistered purl types (CERT-In's `pkg:supplier/...`), purl-shaped ids that are not purls (`pkg:<GUID>`), copies of one record that disagree (Ubuntu purls with versions in Canonical's files, without them on OSV.dev), all-zero SHA-1 placeholders, and inconsistent vendor names in NVD. These are cell content for Phase 5.

### Corrections for other documents (to pass on; not made here)

- **RPT-0004 0.1.0** (for Phase 5): the Syft error above; ISO stages out of date in §1 (DIS 27055 and DIS 27056 are at 40.00, DIS 5962 at 40.99; agents 1, 2); Dependency-Track's current release in §3 (5.2.0, 2026-10-08; agent 5); §5's statement that Alpine's feed lists neither CVE no longer holds for CVE-2026-85091 (agents 3, 5, and the pilot); §1.2's "needs only three things" needs a qualifier, because `name` is required by the model text but by neither the SHACL shapes nor the JSON Schema (agent 1).
- **RPT-0005** (for the student to pass to its author, for DL-0013): NVD's web status "Not Scheduled" is the API status "Deferred" by NVD's own table; `dataVersion` 5.0 occurs only on rejected CVE records; the pilot's "unknown UUID" is CISA-ADP; CycloneDX 1.7.2 is a GitHub release (2026-09-17) (agents 1, 3); and `fanout-attack-composition.md` §1.6 shortens the SHA-256 of `spdx-model.ttl` as `…a5c404c593`, where the full value in its own §10 ends `…d5f404c593` (main session).
- **RPT-0014** (source S-0840 summary): the AI profile property is `builtTime`, not "buildTime", and the model text requires it only for DatasetPackage (agent 1).
- **Library** (Phase 2): `cisa-2026-sbom-minimum` has empty metadata; `ecma-424`, `ntia-2021-sbom-minimum` and `iso-iec-5962` duplicate other records (agent 1).

### What a human accepted

- Pending: the student's review of the five notes files, the merged logs, and the corrections above.
