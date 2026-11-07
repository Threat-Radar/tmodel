---
schema: "archdoc/v1"
id: DL-0042
title: "SDL review and selection procedure (PROC-0002) and its check"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0042
defers_to: ARCH-0001
bears_on: [DEC-001b, R-041, R-042]
---

# SDL review and selection procedure

## Request

@nymble, 2026-11-07: "just do it all", on DL-0040 step 2. That step was a one-page procedure in
which a human Review accepts or rejects each SDL selection, using the #180 overlay shape, plus a
check.

## Produced

- `project/PROC-0002-sdl-review-and-selection.md`: the procedure. It lists the decisions, gives
  five rules, maps the #180 overlay fields onto Assertion + Review, and says how the rules are
  enforced.
- `render_sdl.governance()`: the rules as a check, with `required_reviewer_roles` in `sdl.yaml`
  and a `--strict` gate mode. The page shows how many selections are awaiting review.
- `docs/publishing/test_render_sdl.py`: nine cases (AI reviewer, decided without a review,
  missing justification, status mismatch, unknown verdict, wrong role, changes requested).
- `schema.yml` now runs `render_sdl.py --check` and the tests. DL-0040 described the check, but
  CI did not run it.

## Accepted / rejected (by the drafting agent, for the human to check)

- **Rejected: a separate overlay file per SDL model** (#180 puts the TCU TARA record in
  `models/tcu/governance.yaml`). The SDL model already holds Reviews, so a second file would
  duplicate them. Only the required roles live outside the model, in the page manifest.
- **Rejected: treating a GitHub approval as the decision.** Same reason as DL-0027.
- **Gap found:** `Review` has no date slot. The merge commit stands in for now. This is recorded
  for DEC-001b.

## Human review

Pending: @nymble (owner). @phaskell is listed as a reviewer.

## Validation

`render_sdl.py --check` is fresh and reports 10 selections awaiting review. `test_render_sdl.py`:
9 passed. `bin/validate-archdoc`, `check_links` and `check_identities` are clean.
