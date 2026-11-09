---
schema: "archdoc/v1"
id: DL-0041
title: "SDL classes for DEC-001b: drafted, then accepted with RPT-0013-OM names (ADR-0013)"
type: decision
status: accepted
version: "1.0.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0041
defers_to: ARCH-0001
bears_on: [DEC-001b, ADR-0010, ADR-0012, ADR-0013, R-040, R-041, R-042]
---

# SDL classes for DEC-001b

**Numbering.** DL-0041 was free: 0035, 0036, 0038 and 0045 belonged to open PRs (#207, #211,
#218), and 0040 to #217.

## Request

@nymble, 2026-11-07: "just do it all". This was step 1 of DL-0040: fold the SDL classes into the
DEC-001b proposal.

## Produced (draft, PR #219 first version)

- ADR-0013 as **Proposed**, with the DL-0040 names (`SdlPractice`, `WorkProduct`,
  `RequirementSet`), in a proposal module `spec/schema/proposals/sdl-dec-001b.linkml.yaml`.
- Optional slots aligned with RPT-0013-OM: `evidence_nature`, `digest`, `about_version`,
  `fresh_until`, and `version` as the edition.
- Questions for review: keep the DL-0040 names or use the research names? Is `RequirementProfile`
  needed for the MVP?

## Human decision (2026-11-07)

@nymble, paraphrased: decisions rest with the sponsor; accept the ADR with the research report's
names.

- **Accepted** ADR-0013, using the **RPT-0013-OM names**: `WorkProduct` becomes **`Evidence`** and
  `RequirementSet` becomes **`RequirementSource`**. RPT-0013-OM has no practice type, so
  `SdlPractice` keeps its name. Collections, ids, slots and predicates follow: `evidence_items`,
  `evidence:`, `evidence_kind`, `requirement_sources`, `requirement-source:`, `source_members`
  and `*_requirement_source`.
- **Rejected:** the DL-0040 names.
- **Deferred:** `RequirementProfile` (not answered, so not added).
- The classes moved into `tmodel-object-model.linkml.yaml`, and the proposal module was deleted.
  ARCH-0001 records the change (v0.1.11).

## Validation

linkml-validate 1.12.1 on sdl-01, mvp-\*, tv-\* and pv-\*: no issues. `bin/gen-schema --check`,
`render_sdl.py --check` and `bin/validate-archdoc` pass.
