---
schema: "archdoc/v1"
id: DL-0046
title: "AI hook v2: proposals for threat models, SDL and saved KG views; `tmodel accept` for the sponsor"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0046
defers_to: ARCH-0001
bears_on: [DEC-001b, APP-0001, R-018]
---

# AI hook v2: threat models, SDL, saved KG views, and the sponsor's `accept`

## Request

@nymble, 2026-11-07: "AI hook should manage KG view and potentially additions, edits to KG and
threat model and SDL". The follow-up instruction was that everything stays a proposal; the model
is never edited directly, and only a sponsor Review accepts. It also asked for an `accept` helper
that a human runs in a branch or PR, pending proposals and proposed views shown in the app, an
optional read-only `GET /proposals`, and no write endpoints or API keys in the app. This
extends DL-0044 (v0, SDL additions only).

## Design

**Same hook, wider target.** `tmodel propose` accepts `tmodel.patch/v1`. v0 patches still
work. A patch can target any example model in `spec/vectors`, in three families:

- attack-path and threat models: `mvp-*`, `tv-*` and `pv-*`;
- SDL models: `sdl-*`;
- saved KG views: the model's `views` collection (class `View`: `projection: graph` plus a
  `focus_query`).

Besides `add` and `assertions`, a patch can now hold:

- `edit`: `{collection, id, set, unset}`;
- `remove`: `{collection, id}`.

Everything is still written only to `spec/vectors/proposals/<model>.proposals.yaml`. The model
file is not touched.

**What the engine enforces (nothing is written on any failure):**

- The target is a model file (`mvp-`, `tv-`, `pv-` or `sdl-*.yaml`) in the approved
  directory.
- Collections are checked per family:
  - SDL: practices, evidence, requirement sources, requirements, milestones, gates, parties
    and views.
  - Threat models: every collection in the example containers except `reviews` and
    `assertions`. A drift test fails when a model gains a collection the hook doesn't know.
- `reviews` can never be added, edited or removed.
- An edit can't change an `id`, or set or unset a decision key. Decision keys are
  `assertion_status`, `review_status`, `reviewer`, `approved_by`, `decided_by` and
  `approval_status`.
- Every proposed Assertion is stamped `proposed`, with `asserted_by`, `asserted_at` and
  `generated_by`.
- An edit or removal must name an object in the model. An object with a pending change can't get
  a second one until the first is decided, so decisions never conflict.
- The model, with every pending proposal folded in, must still pass that model's checks:
  - threat models: the attack-graph loader and the `/graph` projection (dangling references,
    duplicate ids);
  - SDL models: the SDL checks and the PROC-0002 review rules;
  - both: every saved view's `focus_query` must resolve.

**Saved KG views.** A `focus_query` is written `START_ID -> step -> ...`, the form the example
models already use. A step is one of:

- a collection: the nearest objects of that kind, by fewest links in either direction;
- a relationship: a slot or an Assertion predicate, followed outward. `*` repeats it, as in
  `composed_of*`.

Text after `;` is a note. `engine/engine/propose.py:view_members` resolves a query to object
ids, using any id-valued field as a link, so the same code works for SDL models.

**`GET /proposals` (read-only).**

- Without `file`: every model with its number of pending proposals.
- With `file`:
  - the pending proposals, in the same summary `GET /sdl` uses, plus `changes` for edits and
    removals;
  - the saved views. The model's own come first, as `accepted`, or `proposed_removal` when a
    proposal would remove one. Then come proposed views, as `proposed` with their proposal id.
    Each carries the object ids it selects.
- No local path is returned. There is still no write route, and a test checks that none named
  "accept" exists.

**`tmodel accept`: the sponsor's command.** It is a CLI command only, never an API route.

- It refuses to run on `main` or `master`.
- The reviewer must be a person Party with `role:sponsor`. For an SDL model that is
  `party:nymble`. In threat models that don't list the sponsor yet, `--declare-sponsor nymble`
  adds the Party in the same change.
- A justification is always required.
- `accepted`:
  - applies the additions, edits and removals to the model **text**. Only the touched list
    entries are rewritten and the comments are kept; the result is checked to parse to exactly
    the expected document;
  - marks each Assertion `accepted`, with a `Review` by the sponsor;
  - re-runs the model checks.
- `rejected` and `changes_requested` leave the model alone.
- Either way, the proposal leaves the proposals file and goes to
  `spec/vectors/proposals/<model>.decided.yaml` with who decided, when and why. A rejection also
  keeps the full record. The sponsor then pushes to the PR, and schema CI (`linkml-validate`)
  checks the result.

**App.** The Graph tab gains two things:

- a **Saved view** selector. A proposed view is labelled "Proposed: … (not reviewed)". Picking
  one loads the view's objects and dims everything else; the status line shows the view's
  review state with the shared `review-status.ts` presentation, and "Show all" clears it.
- a **Pending proposals** list, with the same review chip. It shows what each proposal adds,
  edits, removes and asserts.

The SDL tab's pending-proposals table also lists edits and removals. Both come from the
read-only `GET /proposals` and `GET /sdl`. The app has no model, no key and no write path.

## How Claude Code or Grok Bot use it

`.claude/skills/kg-propose/SKILL.md`, which `.claude/skills/sdl/SKILL.md` links:

1. branch;
2. look with `tmodel proposals` and `tmodel paths`;
3. write a v1 patch;
4. `tmodel propose --dry-run`, then `tmodel propose`;
5. commit the proposals file and open a PR asking @nymble to decide.

The agent never runs `tmodel accept`.

## Accepted / rejected (by the drafting agent, for the human to check)

- **Accepted: views as `View` objects in the model**, not a separate views file. The class
  already exists in the accepted core (`projection`, `focus_query`), and mvp-01, mvp-02, mvp-03
  and mvp-18 already carry one. This needs no schema change.
- **Accepted: text-level apply** in `tmodel accept`. Re-dumping the YAML would drop the model
  files' comments, which carry review notes. An edited entry is re-emitted in block style, so
  comments *inside* that one entry are lost.
- **Rejected: a POST `/proposals` or `/accept` route.** This keeps the DL-0044 reasoning: a
  loopback write API would need CSRF and origin hardening, and accepting must stay a human act in
  a PR.
- **Deferred:** proposals against the packaged app's bundled read-only examples, an interactive
  view editor in the Graph tab, and LinkML validation inside the engine (schema CI covers it).

## Human review

Pending: @nymble, the only decider. @paria03 owns attack-path review and is a natural second
reader for the threat-model patch rules.

## Validation

Engine: ruff, plus pytest (`test_propose_v2.py`). It covers:

- the refused patches;
- the drift guard;
- `GET /proposals` and that it is GET-only;
- view queries on mvp-01, mvp-03 and mvp-18;
- `accept` keeping comments, writing Reviews and refusing non-sponsors and `main`;
- reject and removal;
- SDL accept;
- the CLI;
- the GUI fixture matching the engine.

Locally, the accepted mvp-01 and sdl-01 pass `linkml-validate`. Frontend: tsc and vitest
(`graph-saved-views.test.ts`).
