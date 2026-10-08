---
schema: "archdoc/v1"
id: DL-0015
title: "RPT-0004 second pass: AI-assisted scoping, survey, extraction and mapping"
type: process
status: draft
version: "0.1.0"
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

- Pending: the student's agreement to start with part A, the student's review of `dimensions.md`, and @nymble's answers to its open questions.

### What was rejected, and why

Nothing yet.
