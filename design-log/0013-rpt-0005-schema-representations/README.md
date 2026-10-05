---
schema: "archdoc/v1"
id: DL-0013
title: "RPT-0005 schema representations: AI-assisted scoping, survey and crosswalk"
type: process
status: draft
version: "0.1.0"
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
