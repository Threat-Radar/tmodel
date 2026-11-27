---
schema: "archdoc/v1"
id: DL-0077
title: "Review screens: projects, versions, review and rating of attack paths (#290)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0077
defers_to: ARCH-0001
bears_on: [R-011, R-018, R-019, DEC-003, DEC-006, DL-0068, DL-0073, DL-0074]
---

# DL-0077: the review screens

DL-0074 is #291's (#289), DL-0075 is #288's and DL-0076 is #236's, so this entry is DL-0077.

## Question asked

Issue #290: the frontend for human review and annotation of attack paths. Open an editable
model, select an attack path, review, annotate, accept or reject it as the backend permits,
update the permitted impact and feasibility ratings, save everything through one atomic
operation without losing input on any failure, and show every view refreshed from the saved
version with its recalculated risk. It is built on #291 (the #289 review backend), which is
built on #269 (#63's calculated risk), and follows #288's project workspace.

During the build the team's design for saving and reopening threat models was supplied, and
this entry follows it:

- **Home page:** under the welcome text, three large options with a line of explanation each:
  Import New Product (a threat model from an SBOM and a vulnerability scan), Open Existing
  Threat Model (a previously saved YAML file) and Open Existing Project (a project and its
  version history), built into #278's welcome screen.
- **A project is a local folder the user picks:** `original.yaml` (never changed),
  `project.json` and `versions/v001.yaml`, `v002.yaml`, and so on. The engine (#288) manages it
  and the app sees only ids.
- **The project view:** a header with the project's name and a version selector ("Version 4
  (Current)"); a side navigation of Model Report, Attack Paths, Graph, Risk Score and Review &
  Edit; and a Version History table of Version, Description, Risk summary and Date, where any
  older version can be viewed, read-only.
- **The flow:** Review & Edit, then "Save New Version", then everything reruns through the
  engine. A save never overwrites a version; a save from an out-of-date version is refused as a
  revision conflict.

The design's Import New Product entry point is its own screen, in its own files, in a pull
request stacked on this one (DL-0080). Until that lands, the home page shows the option as
coming soon.

## What was produced

All of it is frontend code in `apps/desktop/src/`, plus one engine test that generates a
fixture.

**Projects, versions and review (#290):**

- `review-contract.ts`: #289's request and response shapes, and parsers that refuse an answer
  naming another model, revision, threat or route, or whose four views disagree about their
  revision. `review-client.ts`: getReviewContext, saveModelChanges and refreshModel, each a JSON
  POST with the host's bearer session. submitReview and saveRatings are not used: HUMAN_REVIEW.md
  says one Save uses saveModelChanges.
- `project-workspace.ts`: #288's three webview routes (`GET /workspace/models`,
  `GET /workspace/versions`) and the provider that joins them to the host's step.
  `project-host.ts`: the host step, behind one function, `hostProjectStep`, and the session probe.
- `project-controller.ts`: opens a project or a read-only file, loads a version with
  refreshModel and shows it in every view through `ModelSession`, and replaces every view from
  a save's answer. `revision-api.ts`: one version's views behind the engine's GET routes, in
  memory, so the existing report, Explore graph, risk panel and coverage providers read them
  without any project id reaching the approved-vector routes.
- `project-view.ts`: the project header, version selector, Version History table, side
  navigation and Risk Score page. `review-workbench.ts`, `review-render.ts` and
  `review-drafts.ts`: Review & Edit. `home-entry.ts`: the home page options.
- `desktop-projects.ts`: the wiring, two small subclasses (the attack-path view reports its
  path; the report says what a project version is) and the backend choice. `project-mock.ts`: a
  stand-in for the host, #288 and #289 built from the shared examples, for tests and for a Vite
  development server opened with `?projectSource=mock`. `project-screens.css`: the styles.
- `main.ts`: the wiring, every line of it on the desktop side of the existing browser-preview
  guard.
- Fixtures: `human-review-revisions.json` (the review service's refresh at r1 and context at r2,
  from `engine/tests/test_review_frontend_fixture.py`, which fails when they drift) and
  `model-workspace-contract.json` (a copy of #288's examples), both described in the fixtures
  README.

### How the acceptance criteria are met

- **Open, select, review, annotate, accept or reject, as permitted.** Open Existing Project and
  Open Existing Threat Model, and "Start a project" from an example or a read-only file, go
  through the host's step; the project's current version opens in every view. Review & Edit
  follows the attack-path view's path, lists the engine's computed routes for it (route ids from
  #63's answer, never built from labels), reads the route's context and shows each Assertion
  (subject, predicate, object, proposer, status), its reviews with rationale and annotation, and
  its history by version. Accept or reject with a rationale and an optional annotation;
  correcting one's own review sends its `review_id`. Each control appears only when
  `permitted_actions` allows it, only on a project's current version, and never on an older
  version or a read-only file.
- **Ratings in one atomic save.** Route feasibility (per authored path that owns exactly the
  route) and scenario impact (per risk assessment, safety, financial, operational and privacy)
  are separate sections that say which one applies to the route only and which to every route
  of the threat. Missing ratings, conflicting route ratings and routes without a route-specific
  path are flagged in words. "Save New Version" sends the route's reviews, feasibility and
  impact changes as one saveModelChanges request against the version the context was read from.
- **Failures keep the input.** A draft is cleared only after the engine confirms the save.
  Validation errors are listed (and checked before sending); a revision conflict saves nothing,
  overwrites nothing and offers "Load Version N", which keeps the draft and marks it as made on
  the older version; permission and workspace failures stop saving until the review reloads; a
  save failure, an unreachable engine or an unreadable answer keep the draft and allow a retry.
- **Every view from the saved version.** A save's answer (graph, attack paths, risk and report
  data, all checked to carry its revision) replaces the report, attack paths, Explore graph,
  requirements, Risk Score and the review context together, and the panel states the route's
  recalculated risk beside its previous values.
- **Tests.** 70 new frontend tests: contract tests against #289's and #288's examples, the
  client, drafts, the in-memory views, the workspace provider, the project view, the home page
  and the wiring, and 21 for the review flow end to end.

### Choices open to review

- **Review & Edit is the attack-path view with the review form open.** The issue puts the
  controls in the existing attack-path view and the team's design gives Review & Edit its own
  place in the side navigation; Attack Paths and Review & Edit therefore show the same path, and
  only Review & Edit shows the form, in the view's side column. Below 1500 pixels the form sits
  under the drawing, which is shorter in review mode, and the form takes focus scrolling no
  further than it needs, so the drawing stays in view above it (checked at 1440 by 900 pixels).
- **The Version History table is a disclosure under the project header,** so it is one click
  away from every page.
- **A version's risk summary** is, per impact category, the highest value the engine derived
  across the version's assessments, with the engine's own category names and the number of
  assessments, or the summary a version recorded when it groups derived risk by category.
  Neither invents a category. Today #289's save records no summary, so the table shows one for
  versions this session read or saved, and "Not recorded" for the rest.
- **One draft per route,** because #289's save request names one threat and route. Drafts on
  other routes are kept and counted, live in memory only, and survive a version change or closing
  the project; the page asks before it unloads with any unsaved, where the webview shows that
  prompt. Discarding asks for a second press.
- **Save New Version uses `aria-disabled`,** so it keeps focus and explains itself when pressed
  with nothing to save. While a save runs the form, the version selector and Close are disabled
  and a double press sends one request.
- **The browser preview is unchanged.** Every desktop module is reached only through the
  existing `preview` guard, and the styles are added at run time (`?inline`), so the Pages bundle
  is byte for byte the committed one (`render_app.py --check`). The development mock and its
  notices are also left out of production builds.
- **The report header of a project version** says "Threat model · Project version" and that a
  review saved in a project is not the sponsor's acceptance of a proposal; the shared renderer
  calls every model example data, which stays true for the bundled models and the preview.
- **Read-only files** show as "Opened file", with "Start a project from this file".
- **"Get started" stays** beside the three new options, so the example models and the Library
  remain one click from the home page.

## The host step and what is still pending

- **#288's contract** is the one in the #288 worktree on 2026-11-27, not yet committed
  (`engine/MODEL_WORKSPACE.md`, `engine/examples/model-workspace/contract.json`, copied here as a
  fixture). Once #288 merges, the tests should read #288's file and the copy should go.
- **The desktop host's part is in #291 since its commit 1a01456**
  (`apps/desktop/src-tauri/src/project_host.rs`): `project_host_session` and
  `project_host_step`, with the native pickers, the two commands this change calls. Until a
  build includes it, projects stay unavailable and the home page says so; the normal launch is
  as read-only as before. An end-to-end rehearsal with the real engine and the packaged app is
  still to come. What this entry asked the host for:
  1. At launch, a token of at least 32 random characters, passed to the engine as
     `TMODEL_HOST_TOKEN` in its environment (never its arguments), with
     `serve --projects --enable-import`, and a review session for that token bound to the
     verified reviewer's Party (HUMAN_REVIEW.md, integration step 2).
  2. A Tauri command `project_host_session` returning the token to the app's own window, or
     null when projects are off.
  3. A Tauri command `project_host_step` taking `{ step }`, where `step` is `{kind:
     "open-project"}`, `{kind: "open-file"}` or `{kind: "create-project", from}` with `from` one
     of `{source_file}`, `{model_id}` or `{model_text, name}`. It shows a native folder or file
     picker (the dialog plugin and its capability), calls the matching
     `POST /workspace/host/*` route from Rust with the token and no Origin header, and returns
     the answer's `model_id`, or null when the user cancels. For `model_text` it writes the text
     to a file the user agrees to, opens it with open-file, and creates the project from that
     file's model id.
  4. Both commands registered in `invoke_handler`, and the token kept out of every log.
- **A gap between #288 and #289:** refreshModel is the only route that returns a workspace
  model's views, and #289 requires the session's Party to be a human Party in the model. A
  project from an imported SBOM has no such Party, so it cannot be shown until the engine offers
  views without that check or the project gains the reviewer's Party. The app reports the
  engine's refusal. Since 1a01456, #291 lets the native host add its verified reviewer as a
  Party on the first save (`allow_party_creation`); whether an imported project can be shown
  before that first save is still to be checked end to end.

## How it was checked

- `npm run typecheck`, `npm test` (771 tests, of which 769 pass: #269's dark-mode contrast test
  fails as it does on e30dc7f, because headless Chrome follows this Mac's dark appearance, and
  so does the popover-focus case below; CI passes both) and
  `npm run build`. The real-browser layout test's popover-focus case is
  timing-dependent on this machine: it failed in 4 of 5 runs on e30dc7f and in 2 of 5 with these
  changes, which do not touch the page and stylesheets it loads.
- `render_app.py --check` (the preview is up to date: 10 models, 685 library records), the five
  publishing test files (40 passed), `check_links.py`, `check_identities.py`,
  `bin/validate-archdoc` and `git diff --check`. The library submodule is not checked out in
  this worktree, so the preview and publishing checks ran on a copy of the worktree with the
  pinned library commit (`e406827`) exported into it; on e30dc7f the same two checks fail in the
  worktree itself for that reason alone.
- For the new engine test: the engine suite (901 passed, 10 skipped; 900 and 10 on e30dc7f),
  `ruff format --check`, the in-process health check, and `ruff check`, whose only findings are
  the six UP038 ones in `model_graph.py`, `review_service.py` and `tara.py` that the local ruff
  0.12 also reports on e30dc7f. Under heavy load one run failed #291's
  `test_invalid_framing_or_large_body_is_rejected` with a reset connection; that file passed
  three times alone, and the next full run passed.
- After #291 moved to 1a01456, whose review service now reports each assertion's effective
  status (`human_reviewed`, `effective_status` and the like), this branch merged it,
  `human-review-revisions.json` was regenerated with `TMODEL_UPDATE_FIXTURES=1`, and the 70
  review and project tests pass with it; the whole app suite passes but for the dark-mode
  contrast test.
- A headless Chrome tour of a Vite development server with the mock: the home page, opening a
  project and a read-only file, Review & Edit, a save and its refreshed views, the version table,
  Risk Score, the Graph, an older version, a validation error, dark mode and a 700 pixel window.
  The keyboard reaches every option and field in order, Space chooses a verdict, and typing
  keeps focus while the unsaved count updates. A second tour at 1440 by 900 pixels confirmed the
  drawing stays in view when Review & Edit opens, as at 1680.

## What a human accepted

- @Clovier, 2026-11-27: took over #290 and asked for it to be built ("start on 288, 290, and
  236"; "can we start the review screens as well?"); the wording and code are Claude Code's
  draft until the pull request review accepts them.

The team's design was supplied during the build as the agreed design; the screens built from it
are the agent's draft until the pull request review accepts them.

## What was rejected, and why

No human has rejected anything in this entry yet. The agent set these approaches aside:

- **Regenerating the browser preview.** It would add a new bundle to `docs/app/` that every
  other preview-changing pull request would conflict with, and the preview has no projects.
- **Review & Edit as a page without the attack-path drawing.** The issue asks for the controls
  in the existing attack-path view.
- **A description field for a new version.** #289's save request accepts none, and an unknown
  field fails validation.
- **Reading a version's views from `GET /workspace/model`.** It returns the YAML document, not
  the engine's views; refreshModel returns all four from one revision.
- **Retrying a conflicting save on the newer version automatically.** That would apply changes
  made against an older version on top of a newer one the reviewer has not seen.

## Follow-ups

- An end-to-end rehearsal of #291's host part with these screens, the real engine and the
  packaged app.
- Engine views for workspace models without the reviewer-Party check, or the importer adding
  the reviewer's Party, so imported projects can be shown.
- #289's save could record a version description and the engine's risk summary in #288's
  `save_version`, which already accepts both.
- Requirements coverage for a project version uses the frontend fallback, whose notice still
  calls the model an example.

## Gate

`bin/validate-archdoc` clean. Frontend type check, tests (but the pre-existing dark-mode
contrast test) and build pass; the preview is unchanged.
