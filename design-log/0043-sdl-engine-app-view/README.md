---
schema: "archdoc/v1"
id: DL-0043
title: "SDL in the engine and the desktop app: GET /sdl and a read-only SDL tab"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0043
defers_to: ARCH-0001
bears_on: [DEC-001b, APP-0001, R-041]
---

# SDL in the engine and the desktop app

## Request

@nymble, 2026-11-07: "just do it all". This is DL-0040 step 4: an engine `GET /sdl` route and a
read-only SDL view in the Mac app.

## Produced

- **`engine/engine/sdl.py`.** The SDL view logic moved out of `docs/publishing/render_sdl.py`:
  `collect()`, the reference checks and the PROC-0002 review rules (`governance()`). The page and
  the app now read the same code. `render_sdl.py` is a thin wrapper that adds the site's relative
  links, and the page output is byte-identical.
  - MAP-0001 columns are now derived from each RequirementSource's library record (MAP-0001
    `frameworks.*.record`). The manifest's `map_columns` is only an override.
- **`GET /sdl`** (server route), `core.sdl()` and **`tmodel sdl [FILE] [--program P]`**. With
  no file it lists the `spec/vectors/sdl-*.yaml` models and their programs. With a file it
  returns the view, which says that every selection is a proposal until the sponsor reviews it.
  - The usual model-path guard applies, and a file that isn't `sdl-*.yaml` is refused (400).
  - A broken review rule is a 400, never a silently "accepted" row.
  - `bin/build-engine` bundles `spec/MAP-0001.yaml`, and its smoke test runs `sdl`.
- **Desktop app.** An **SDL** tab with a model/program selector and these sections: requirement
  sets with their decision, practices by phase with status, owner, evidence links and selection
  state, milestones and gates with their name review, and open gaps.
  - Review state reuses `review-status.ts`, so a proposed row can never show as accepted.
  - Only http(s) links are rendered as links. All text goes in as text.
- **Navigation.** `AppNavigation` now takes a list of views, the same API as #211, so the two
  PRs merge by adding entries to one list.
- **Tests.** `engine/tests/test_sdl.py` (13) covers the list, the view, bad queries, an AI review
  being refused, the route, the CLI, decider roles matching `sdl.yaml`, and the GUI fixture
  matching the engine. The frontend adds `sdl-view.test.ts` and `engine-sdl-provider.test.ts`,
  and `app-navigation.test.ts` is updated for three views.

## Accepted / rejected (by the drafting agent, for the human to check)

- **Rejected: rendering the static HTML page inside the app.** The app would need the site's CSS
  and relative links. Plain data from the engine keeps one source.
- **Rejected: any write path from this tab.** Proposals come through `tmodel propose` (DL-0044),
  and decisions are a person's Review in a PR (PROC-0002).
- **Deferred:** the threat-model table (the Knowledge Graph and #211 report views cover it), the
  MAP-0001 framework columns, and filtering.

## Human review

Pending: @nymble. @kriishnaa-18 owns the app's views, so their review is welcome.

## Validation

Engine: `ruff check`, `ruff format --check`, and `pytest` (252 passed, 5 skipped). Frontend:
`tsc --noEmit`, `vitest run` (184 passed) and `vite build`. `render_sdl.py --check` is fresh,
`test_render_sdl.py` and `check_links` pass. The local .dmg build on the Mac mini is reported in
the PR.
