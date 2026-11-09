---
schema: "archdoc/v1"
id: DL-0044
title: "AI proposal hook: `tmodel propose` writes agent patches as proposals only"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0044
defers_to: ARCH-0001
bears_on: [DEC-001b, APP-0001, R-018]
---

# AI proposal hook: `tmodel propose`

## Request

@nymble asked for this on 2026-11-07. The question was "Perhaps AI hook in the application to
build and edit knowledge graphs?", and the instruction was "just do it all". This is DL-0040 step
4, second half: an AI hook that can only write proposals, which are then decided through the
existing review UI.

## Design

**No model in the app.** Neither the app nor the engine calls a model, and neither holds an API
key. The "AI" is any **external agent**: Claude Code, Grok Bot or a script. It already runs in the
repository and talks to the engine through the CLI. So the hook is a CLI command, not a chat panel:

```sh
tmodel propose patch.yaml            # check, then append to spec/vectors/proposals/<model>.proposals.yaml
tmodel propose patch.yaml --dry-run  # check only
cat patch.json | tmodel propose -    # from stdin
```

Patch format: `engine/engine/propose.py` (docstring); example:
`engine/tests/fixtures/sdl-patch-example.yaml`. A patch names a `target` SDL model, the proposing
Party (`proposed_by`), `generated_by` (the tool and run), a `rationale`, new objects (`add`, by
collection) and Assertions.

**What the engine enforces (nothing is written on any failure):**

- The target is an `sdl-*.yaml` model inside the approved model directory.
- Allowed collections: practices, work products, requirement sets, requirements, milestones,
  gates and proposing parties. **Never `reviews`.**
- No object or Assertion may carry a decision key (`review_status`, `reviewer`, `approved_by`,
  `decided_by` and similar). Every Assertion is stamped `proposed`, with `asserted_by`,
  `asserted_at` and `generated_by`.
- New ids must be new. The proposer must be a Party.
- The model, with every pending proposal folded in, must still pass the SDL checks: references,
  MAP-0001 rows, statuses and the PROC-0002 review rules.
- The model file itself is **never** edited.

**Shown in the app.** `GET /sdl` returns `proposals`: who proposed (AI agent or person), when, the
tool, the rationale, what it adds and what it asks. The SDL tab lists them under **Pending
proposals**, using the same review chip as everything else, so every one shows as Proposed.

**Decided by a human.** In a pull request, a person moves a proposal's objects and Assertions into
the model and removes it from the proposals file. Then they add a Review per PROC-0002, or reject
it by deleting it with a justification in the PR. The proposals file is reviewed like any other
file.

## How an external agent uses it

1. Read `.claude/skills/sdl/SKILL.md` and `project/PROC-0002-sdl-review-and-selection.md`.
2. Write a patch and run `tmodel propose patch.yaml --dry-run` until it passes, then run it
   without `--dry-run`.
3. Commit `spec/vectors/proposals/*.proposals.yaml` on a branch and open a PR that asks the
   decider (today `@nymble`) to accept or reject each proposal.

## Accepted / rejected (by the drafting agent, for the human to check)

- **Rejected: a model API key or chat panel in the app.** It would put credentials in a public,
  student-built app, and it duplicates the agents we already use.
- **Rejected for now: a POST endpoint on the local API.** The API is GET-only and loopback-only.
  A write route would need CSRF and origin hardening that the CLI does not need. It can be added
  later and would call the same `core.propose()`.
- **Rejected: writing proposals straight into the model as `proposed` Assertions.** That mixes
  agent output with the curated model, and it makes a rejection mean editing the model.
- **Deferred:** an "accept" helper that moves a proposal into the model. Doing that by hand in a
  PR keeps a human in the loop. Proposals for attack-path models (`mvp-*`) are deferred too.
- **Limit:** in the packaged app, the bundled examples are read-only. `tmodel propose` is for a
  source checkout.

## Human review

Pending: @nymble. @paria03 owns attack-path review and is a natural reviewer for the review
semantics.

## Validation

Engine: ruff and pytest (268 passed, 5 skipped). `test_propose.py` (16) covers the refused
patches, writing nothing on failure, the model never changing, the view listing proposals and the
CLI dry run. Frontend: tsc and vitest (185 passed).
