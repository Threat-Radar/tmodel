---
schema: "archdoc/v1"
id: PROC-0002
title: "SDL review and selection — how a human accepts or rejects requirement sets, delivery items and milestone names"
short_title: "SDL review and selection"
description: "One-page procedure. Agents and people propose SDL selections as Assertions; only a human Review, by a person in an allowed role, decides them. Reuses the #180 governance-overlay fields on the existing Assertion + Review spine. render_sdl.py enforces the rules."
type: process
category: process
status: draft
version: "0.1.0"
version_policy: "semver; MINOR = additive rules, MAJOR = a rule removed or reversed"
date: "2026-11-07"
updated: "2026-11-07"
owner:
  role: sponsor
  id: nymble
decision_makers:
  - role: sponsor
    id: nymble
reviewers:
  - role: sponsor
    id: nymble
    kind: human
  - role: faculty
    id: phaskell
    kind: human
  - role: drafting-agent
    id: grok-bot
    kind: ai_agent
needs_review: true
reviewed: false
canonical_path: project/PROC-0002-sdl-review-and-selection.md
defers_to: ARCH-0001
---

# PROC-0002 — SDL review and selection

**Status: draft.** Applies to SDL models (`spec/vectors/sdl-*.yaml`, DL-0040). Design record:
DL-0042.

## What gets decided

| Decision | Assertion predicate (subject: the SecurityProgram) | Object |
|---|---|---|
| A requirement set governs the product | `selects_requirement_source` | RequirementSource |
| A set is a candidate / is ruled out | `considers_requirement_source` / `excludes_requirement_source` | RequirementSource |
| A practice is a delivery item | `selects_practice` | SdlPractice |
| A milestone or gate is called this | `proposes_milestone_name` | Milestone / Gate |

## Rules

1. **Anyone proposes; only a person decides.** An agent or a person adds the Assertion with
   `assertion_status: proposed`, `asserted_by` and the reasoning in `description`. An AI agent
   never writes a Review of a selection and never sets an Assertion to accepted or rejected
   (CLAUDE.md).
2. **Who may decide: the sponsor (@nymble) only.** The decider is a Party with
   `party_kind: person` and the role `sponsor`, which is `required_reviewer_roles` for the page in
   `docs/publishing/sdl.yaml`. **Faculty (@phaskell) and students are not deciders.** They may
   propose and comment, and their Reviews are refused. The sponsor decided this on 2026-11-07.
3. **How to decide.** Add one `Review` per Assertion and set the Assertion to match:

   | verdict | `review_status` | `assertion_status` | `justification` |
   |---|---|---|---|
   | accept | `accepted` | `accepted` | optional |
   | reject | `rejected` | `rejected` | required |
   | send back | `changes_requested` | stays `proposed` | required |

   A changed proposal is a new Assertion. The old one stays, rejected, as the record.
4. **Where.** Only in a pull request that changes the SDL YAML. The reviewer approves the PR on
   GitHub, and the YAML Review is the record that the page and app show. The PR approval alone
   is not the record (DL-0027).
5. **Until decided**, the page and the app show the selection as *Proposed*, and it counts as
   "awaiting human review".

## Mapping to the #180 governance overlay

| #180 field | Here |
|---|---|
| required reviewers by role | `required_reviewer_roles` in `sdl.yaml` |
| review: reviewer id, actor kind | `Review.reviewer` → Party (`party_kind` person / software_agent) |
| outcome (approved / changes requested / comment) | `review_status` accepted / changes_requested / rejected |
| reason, comment log | `justification`; PR conversation for discussion |
| date, resolving commit | the merge commit of the PR (Review has no date slot: a DEC-001b gap) |

## Enforcement

`docs/publishing/render_sdl.py` checks rules 1 to 3 on every run and in CI (`schema.yml`). It
fails on a non-person reviewer, an unknown verdict, a missing justification, a status that
disagrees with its latest Review, or a reviewer without an allowed role. It prints how many
selections are awaiting review. `--strict` also fails while any selection is awaiting review,
for use at a release Gate.

## Change log

| version | date | change |
|---|---|---|
| 0.1.0 | 2026-11-07 | First draft (DL-0042). Decider: the sponsor only; faculty is not a decider (@nymble, 2026-11-07). |
