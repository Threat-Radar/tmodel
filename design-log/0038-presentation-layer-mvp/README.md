---
schema: "archdoc/v1"
id: DL-0038
title: "Presentation layer MVP: model picker, model report, focused attack-path view, static model pages"
type: process
status: draft
version: "0.4.0"
date: "2026-11-04"
updated: "2026-11-05"
record: DL-0038
defers_to: ARCH-0001
---

# Presentation layer MVP: model picker, model report, focused attack-path view, static model pages

**Status: implemented on a branch for review. Nothing here is accepted.** No
`DEC-*` is decided here. The UI stack stays as ADR-0003 has it (Tauri +
TypeScript). This entry follows the proposed direction of DL-0036 (#207), which
is itself unaccepted; the choices below that DL-0036 left open are listed under
"Open for the sponsor". Version 0.2.0 records a review round (below) and the
fixes made after it; 0.3.0 records the connector routing and the path view's
interaction (below); 0.4.0 records a second review round (below).

## Request

Issue #208 (GUI lane, @kriishnaa-18): replace the raw Knowledge Graph as the only
way to read a model with readable model views, per the acceptance criteria in
#208 and DL-0036: a model picker, a TARA-ordered model report as the default
view, a focused attack-path view, review state on every threat and path, and
one renderer for the app and static Pages HTML (#204, #202 item 1). The agent
was asked to keep the existing graph, library and loading behaviour, to invent
no data, and to commit nothing.

## What was produced

| Piece | Where | What it does |
|---|---|---|
| `/models` route and `tmodel models` | `engine/engine/core.py` (`list_models`), `api/server.py`, `cli.py` | Lists the example models in the approved model directory (bundled examples in the packaged app). Title and description come from the model's products (one "Name: description" line per product when there are several, as in mvp-18); harness files (`*.linkml.yaml`) are skipped; a file that fails to load is listed under `problems`. No local path in the payload. |
| ADR-0011 classes in `/graph` | `engine/engine/model_graph.py` | `assets`, `trust_boundaries` and `data_flows` (accepted by ADR-0011) are projected as nodes, so the report can show assets (pv-01, pv-02, and mvp-02 once #209 lands). Their own slots stay node properties; no relationship slot was added. |
| Report builder | `apps/desktop/src/model-report.ts` | Pure function from the engine's `/graph` and `/attack-paths` answers to a `ModelReport`: assets, components, damage scenarios, threats, attack paths (ordered steps with AND/OR and the engine's computed alternatives), mitigations, risk, requirements. |
| Renderer | `apps/desktop/src/report-render.ts`, `path-diagram.ts`, `safe-html.ts`, `report.css` | One renderer for both outputs. `path-diagram.ts` lays out each path and routes its connectors; Cytoscape (app) and SVG (report, Pages) draw the same routes. Every model value is escaped; no script, handler or external reference. Ids, CURIEs, CPE/purl strings, schema field names and raw status values appear only behind a "Details" toggle. `defaultViewLeaks` finds any that show with the toggles closed. |
| App views | `index.html`, `main.ts`, `model-session.ts`, `model-catalog.ts`, `report-view.ts`, `path-view.ts`, `app-navigation.ts` | Model picker (engine list, remembers the last model, `?model=`/`?file=` stay as developer switches). Tabs: Model report (default), Attack paths (Cytoscape, the shared layout, fitted to the canvas), Explore graph (the existing Knowledge Graph; see below), Library (unchanged). `model-session.ts` opens a model: only the latest choice is shown. |
| Explore graph | `graph-view.ts`, `engine-graph-provider.ts` | Opens on the model's threats and their one-hop neighbours (paths, damage, risk, mitigations, requirements); every other node is reached with Expand neighborhood, or all at once with "Show whole model". Bookkeeping records are hidden unless the reader ticks the toggle. |
| Static pages | `docs/publishing/render_models.py`, `apps/desktop/scripts/render-model-pages.mjs`, `src/model-pages.ts`, `docs/models/` | The engine collects every model in-process; Node (22.6 or newer) runs the app's renderer to write one self-contained page per model plus an index. The writer refuses to write any page whose default view shows an id or schema name. Wired into `bin/publish-site`; `--check` fails when pages are stale. Linked from the landing page. |
| Review rule | `engine/engine/graph.py` (`ReviewState.reviewed`), `apps/desktop/src/review-status.ts`, `apps/desktop/src/fixtures/review-state-cases.json` | One rule for "reviewed" in the engine (picker counts, `tmodel paths`) and the app (report, path view), tested on one shared table of status combinations. |
| Tests | `engine/tests/test_models_surface.py`, `test_graph.py`; `apps/desktop/src/*.test.ts` | Engine: model list, problems, ordering, product descriptions, CLI parity, ADR-0011 projection, the review rule, and the shape of the saved GUI fixtures. Frontend: report, renderer, diagram, path view, catalog, pages, provider, model session, report view, and the Explore graph's model switching. The report tests run on saved engine answers for mvp-01 and mvp-02 (`src/fixtures/report-input-*.json`); the default view of all eight models is checked on the published pages. |

## How review state is shown

Only recorded Assertions and Reviews set a status (CLAUDE.md: AI output is a
hypothesis until a human accepts it). A threat's status comes from the
`realizes_threat` Assertion of the paths that realise it and that Assertion's
Review, using the same rule as `review-status.ts` and the engine's
`ReviewState`: a Review that rejects or asks for changes wins over the
Assertion's own status, and only an accepted Assertion with no contrary Review
counts as accepted (or "reviewed" in the picker's count). The two are tested on
one table of cases, including contradictory ones (an accepted Assertion with a
rejecting Review) and transitional ones (an accepted Assertion whose Review is
still open). A threat whose own `source_method` says "reviewed" but has no
recorded review shows **Not reviewed** (mvp-03, mvp-18 and the tv models have
such threats). Labels: Accepted, Rejected, Changes requested, AI-proposed / not
reviewed, Not reviewed; the reviewer's handle comes from the Review's `reviewer`
Party. In mvp-02 the infotainment pivot shows **Rejected** by `@av-reviewer`
with the reviewer's reason, in the threat table, the path card, the path
diagram and the app's path view. A second threat linked to a path only through
an Assertion is listed with its own status ("Also linked to …"), never merged
into the path's own.

## Choices the agent made, and alternatives it rejected

- **Report shape in the frontend, over `/graph`, not a new engine report
  route.** An engine route returning TARA-ordered JSON is the #181 collect step,
  assigned to @paria03 and not yet specified; writing it here would duplicate
  that work. The builder only arranges what `/graph` already returns, and its
  output type mirrors #181's list (assets, damage, threats, paths, risk,
  treatments, requirements, each with its id and review state), so #181's output
  can replace the builder's input later. Step order and AND/OR alternatives are
  the engine's (`/attack-paths`); the builder only assigns columns for drawing.
- **One renderer by running the TypeScript renderer in Node for Pages.**
  Rejected: a Python HTML renderer beside the app (two code paths that can
  disagree, which #208 rules out); Cytoscape on Pages (the publishing rules
  allow no `<script>`). The path diagram is one layout drawn twice: Cytoscape in
  the app, inline SVG in the report and on Pages.
- **Descriptions are shown as a subset of the model's own sentences.** The
  vectors' descriptions mix reader text with modelling notes ("(§3 structural
  node)", "(ADR-0002)", backticked slot names, ids). The report shows the
  leading sentences up to the first one holding such a note, drops
  parenthetical spec references, and keeps the full text under Details. This
  applies to every description shown by default, including the model's own
  product description in the report header and on the Pages index, and to a
  reviewer's reason. Rewording was rejected: it would put words in the model
  that it does not contain.
- **An object with no name is shown as "Unnamed <type>"**, never by its id
  (the engine labels an unnamed object with its id).
- **Missing data is rendered as missing.** "No assets are recorded", "Not
  rated", "Not assessed: the model records no risk score for this threat"
  (mvp-02's rejected pivot). Nothing is filled in (DL-0036 open question 4).
  When the engine cannot compute some attack paths, the report still opens,
  says "Incomplete" at the top, names the threats affected and marks each
  affected path; only a failure to read the model graph stops the report.
- **The example-data banner depends on the kind of model and on its recorded
  reviews.** For the mvp- and tv- models: an illustrative model written to
  exercise the object model, not a security assessment of a real product. For
  the pv- models, which spec/vectors/README.md describes as published
  automotive attacks modeled from their primary write-ups, AI-drafted and
  unreviewed: drafted by AI from the published write-up of a real automotive
  attack, not a verified security assessment of the product it names. "No
  human review is recorded" is said only when the model records none.
- **The Explore graph opens on the threats.** The original start view (the
  first Component's neighbourhood: 4 nodes for mvp-02, a parts list) is the
  problem #208 describes; the first version of this branch opened on the
  whole model instead, which left nothing to expand. It now opens on every
  threat and its neighbours (9 nodes for mvp-02, 3 of them expandable), keeps
  Expand neighborhood, and offers "Show whole model" for a developer who wants
  everything at once.
- **Connectors are routed once, in the shared layout.** The first version
  let Cytoscape draw each connector as a straight line between box centres
  (diagonals entering a box anywhere, one of them through step 2 of mvp-01's
  XXE path) while the SVG drew S-curves, so the app and the report did not
  match. Now `path-diagram.ts` routes every connector as a right-angled line:
  out of a box's right side and into the next box's left side (mitigations and
  targeted elements from below and above), turning just before the box it
  enters so lines into one AND/OR gate join on one vertical line, and around
  the main band if a straight run would cross a box. A connector shared by
  several lines (into a gate, from several final steps into the threat, from
  the threat to several damages, mitigations, targets) carries its word once,
  on a straight stretch, never on a box. A step with no predecessor is drawn in
  the column just before its first successor, which removes the long lines;
  step numbers, order and gates are unchanged. Cytoscape draws these routes
  exactly (`round-segments` from the layout's own points; labels as fixed
  boxes at the layout's label positions) and the SVG draws the same points with
  the same rounded corners. Tests check, for every mvp-01 and mvp-02 path and
  for synthetic paths with long joins and shared lines, that no line is
  diagonal, crosses a box, or has a label over a box or another label; all 15
  paths of the eight models (and #209's mvp-02) were checked the same way.
  Rejected: Cytoscape's automatic `taxi` routing (its turns are not where the
  SVG's are, so the two drawings would differ again) and drawing the app's path
  view as SVG instead of Cytoscape (the issue brief asks for Cytoscape).
- **The attack-path view is a fixed drawing.** Boxes cannot be dragged: their
  places carry the order, and the routed lines depend on them. The reader can
  pan (drag the background) and zoom (scroll), and "Fit to view" restores the
  fitted drawing. The Explore graph stays the place to rearrange and expand a
  graph. Scrolling over the drawing zooms it rather than scrolling the page,
  as in the Explore graph.
- **The packaged window opens at 1280×800** (was 900×640), the size #208's
  path-view criterion names.

## Review round (2026-11-05)

An independent review of the first version returned NEEDS FIXES. Each finding
and what was done:

| Finding | Resolution |
|---|---|
| Switching models while the Explore graph was loading let the old model's late attack paths replace the new model's "Highlight attack path" list (reproduced in the browser). The bookkeeping toggle had the same race. | Fixed. A disposed view checks after every wait, aborts its graph load, ignores late answers and failures, and empties the shared controls and their handlers when disposed. Tests reproduce the race (they fail without the fix) and cover a dispose between graph batches and a late failure; the browser reproduction now keeps the new model's list. |
| mvp-03's report header showed "ADR-0002 … `composed_of` … (§3)". | Fixed: the header and the Pages index use the same reader-text rule as every other description; parenthetical spec references such as "(ADR-0002)" are dropped too. The default view of all eight models is now tested on the published pages, and the page writer refuses a page with a leak. |
| The banner told pv-01 and pv-02 readers "not an assessment of a real product" under the titles "Toyota RAV4 (2021)" and "Kia vehicle with remote services". | Fixed: the banner depends on the model's kind (see above). Whether to publish those two pages is left to the sponsor (below). |
| In the Explore graph every node said "No additional neighbors": the whole model was loaded at once, so neighbourhood expansion could not be reached. | Fixed: threat-centred start view, Expand neighborhood works again, "Show whole model" on request. Tested on mvp-02's real graph. |
| The fixture test failed whenever anyone edited mvp-01 or mvp-02, so #209 would have failed CI. | Changed: the fixtures are a saved snapshot; the engine test now checks that they have the shape the engine returns (keys at every level the GUI reads), not the same values. #209's mvp-02 passes it. Stale published pages are a separate question (below). |
| One failed `/attack-paths` request made the whole report fail. | Fixed: attack paths are fetched per threat; failures are reported, the rest is shown. |
| The picker's "Could not load …" note vanished when a model opened; the docs said Node 22 where 22.6 is needed; `report-view.ts` and `main.ts` had no tests; two path ids that slug alike could repeat an HTML id; a path linked to two threats showed only one. | Fixed: the note stays (with the reason); Node 22.6 is documented and checked; `report-view.test.ts` and `model-session.test.ts` (main.ts's model switching, moved into `model-session.ts` so it can be tested) were added; anchors, arrow markers and page names are made unique; other linked threats are listed with their status. |
| `site.yaml` and `SKILL.md` conflicted with #209; `bin/publish-site` chose the engine's Python differently. | My entries moved to lines #209 does not touch; `bin/publish-site` uses #209's convention. A simulated three-way merge with #209's head (`cfe96cb`) has no conflicts. |

## Second review round (2026-11-05)

A second independent review of the whole branch returned NEEDS FIXES. Each
finding and what was done:

| Finding | Resolution |
|---|---|
| (High) Section 4 had path cards and diagrams but no attack-path table, so the report did not have the six tables #208 asks for. | Fixed: section 4 opens with a table (path, threat, steps in order, feasibility, review status with the reviewer); each path's name links to its card, and the cards and diagrams stay. Tests check that all six tables exist in order, for the fixtures and on all eight published pages. |
| (Medium) A multi-product model's title named every product but its scope used only the first product's description (mvp-18: the Edge Sensor was missing). | Fixed in `list_models`: one "Name: description" line per product that records a description, in model order; nothing is added for a product with none. The app and the Pages index read each product's line on its own (`readableDescription`), so a modelling note in one product cannot hide another; the header shows one line per product. |
| (Medium) The engine counted a path as reviewed whenever its Assertion was `accepted`, ignoring a Review that rejected it or asked for changes; the app showed such a path as rejected. The picker's "N with an accepted review" and the report could disagree. | Fixed: `ReviewState.reviewed` now follows the app's rule (a negative Review wins; an accepted Assertion counts only with no Review or an accepting one; values compared trimmed, lower case). No path in the eight models or in #209's mvp-02 changes value. One shared table of 18 cases drives both test suites; the published index and every page are checked to give the same accepted count. |
| (Accessibility) Steps in the app's path view could be highlighted only with a mouse. | Fixed: each step's name is a native button there (Tab, Enter and Space), with `aria-pressed` for the step shown in the drawing; it looks as before. The static report and Pages keep plain text, as nothing on them reacts. Checked with real Enter and Space presses in the browser. |
| CI does not check that `docs/models/` is up to date. | Proposed, not made (workflow files need the GUI lane owner's approval): see open question 9. |

## Acceptance criteria (#208), as implemented here

| Criterion | State |
|---|---|
| Pick mvp-01, mvp-02 and at least one more model without URL parameters, in the packaged app | Verified in the browser build against `tmodel serve` (8 models). Packaged: see "Packaged app" below. |
| Title, example-data banner and threat counts by review status before any graph | Verified (report is the default tab). |
| Tables for assets/components, damage, threats, paths, mitigations, risk, in order; no CURIE/CPE/purl/schema name by default | Verified for all eight models: all six tables, in order, and no technical identifier by default, on the published pages (tested) and in the app (checked in the browser). |
| Review status and reviewer handle on each threat and path | Verified. |
| mvp-02 infotainment pivot marked rejected in the table and the path view | Verified. |
| Path view: ordered steps with AND/OR, threat, damage, mitigations; fits 1280×800; every node labelled | Verified in the browser at 1280×800 (screenshots below). Affected components are shown only where the model links them (`targets_element`); mvp-01/02 link none to a threat today (#209 adds them for mvp-02). |
| No Assertion/Review/Party/LifecyclePhase/View nodes in the default views | Verified: the report and path view draw none; the Explore graph hides them unless asked. |
| Same renderer writes a static page per model, linked from the landing page, passing `check_links.py` and `check_identities.py` | Verified: `docs/models/` (8 models + index); both checks pass. Not in the shared site nav (adding it re-renders every bibliography page). |
| Before-and-after screenshots for mvp-01 and mvp-02 | Below; to be attached to the PR when one is opened. |

### Packaged app

Built locally on 2026-11-05 (Apple Silicon, no downloads) the way CI builds
it: the engine sidecar with PyInstaller 6.22.3 (the pinned version, already
installed in a local `bin/build-engine` environment) from this branch's
engine, then `CI=true npx tauri build --debug --bundles app` with Cargo
offline. Ad-hoc signed, review only.

- Verified: the bundle passes CI's checks (`codesign --verify`, the
  third-party notices file, `engine/tests/test_packaging.py` against the
  bundled engine: 5 passed). The app launches, starts its bundled engine on
  port 47811, and that engine's `/models` lists all eight models from the
  bundled `spec/vectors/`. The app's own frontend, served by Vite in a browser
  and pointed at that packaged engine, picks models, opens their reports and
  draws their attack paths (mvp-02 rejected pivot, pv-01, mvp-03).
- Not verified: choosing a model inside the packaged window itself. Driving or
  capturing that native window needs macOS Screen Recording or Accessibility
  permission, which was not granted. A reader can check it by opening the
  built `tmodel.app` and using the picker.
- The debug build was rebuilt after the connector routing (0.3.0) and checked
  the same way. It predates the 0.4.0 fixes; rebuild it to see them.

## Screenshots (1280×800, headless Chrome, engine from source)

| File | Shows |
|---|---|
| [`mvp01-before.png`](mvp01-before.png) | `main` at `b6d95ec`: the Knowledge Graph opens on mvp-01's neighbourhood |
| [`mvp02-before.png`](mvp02-before.png) | `main` at `b6d95ec`, `?file=mvp-02-automotive-ecu.yaml`: a 4-node parts list |
| [`mvp01-after-report.png`](mvp01-after-report.png) | mvp-01 Model report: title, banner, 1 accepted / 1 changes requested |
| [`mvp01-after-path-changes-requested.png`](mvp01-after-path-changes-requested.png) | mvp-01 IMDS pivot path: OR gate, changes requested by `@sec-reviewer` |
| [`mvp02-after-report.png`](mvp02-after-report.png) | mvp-02 Model report: 1 accepted / 1 rejected, reviewed by `@av-reviewer` |
| [`mvp02-after-report-threats.png`](mvp02-after-report-threats.png) | mvp-02 threat table: the AI pivot marked Rejected AI hypothesis |
| [`mvp02-after-path-rejected.png`](mvp02-after-path-rejected.png) | mvp-02 pivot path view, fitted: routed lines joining at the OR gate, rejected threat, damage, mitigation, Fit to view |
| [`mvp02-after-explore.png`](mvp02-after-explore.png) | mvp-02 Explore graph: opens on the two threats and their neighbours, Show whole model offered |
| [`pages-mvp02-after.png`](pages-mvp02-after.png) | `docs/models/mvp-02-automotive-ecu.html`, the static page |

## Open for the sponsor (not decided here)

1. Report first when a model opens (implemented, as DL-0036 proposed) or graph first?
2. Keep the whole-model Explore graph in the MVP (kept, behind its own tab,
   opening on the threats, with bookkeeping hidden) or hide it until I4?
3. Report shape: frontend over `/graph` (implemented) or an engine route fed by
   #181? Switching later replaces the builder's input, not the renderer.
4. mvp-02 data gaps (#184, PR #209): rendered as "not recorded"/"not assessed"
   here. #209's Assets, `damages_asset` and `targets_element` were checked
   against this renderer and appear without code changes; when #209 merges,
   `docs/models/` must be rebuilt (`bin/publish-site`).
5. `/attack-paths` still wants an absolute path. The app passes the path `/graph`
   returns, so the picker works without unifying the two routes.
6. Edge words are a fixed vocabulary in the renderer ("then", "realizes",
   "leads to", "mitigates", "targets"), not text in the vectors.
7. **Publishing pv-01 and pv-02 on Pages.** Their pages name real products
   ("Toyota RAV4 (2021)", "Kia vehicle with remote services") and hold AI-drafted,
   unreviewed threat models of published attacks. The banner now says so; whether
   they belong on the public site at all is the sponsor's call.
8. **Two renderers for mvp-02 once #209 merges.** #209 adds `render_tara.py`, a
   Python renderer that writes `docs/reports/tara-mvp-02.html` (a clause-15 TARA
   draft) with its own collect step and review rule. This branch writes
   `docs/models/mvp-02-automotive-ecu.html` with the app's renderer. Both are
   correct today but can drift. Merging them (one collect step, #181; one
   renderer, #182) is for the sponsor, @Clovier and @paria03 to decide, not this
   branch.
9. **Detecting stale model pages in CI** needs a workflow change, which this
   branch does not make. The smallest reliable one is a job in `ci.yml` (which
   runs on every pull request): check out with `submodules: true` (the public
   `library` repo; `site_nav.py` reads `site.yaml` with its YAML reader), set
   up Python and Node 22, `pip install -e engine` (PyYAML), then run
   `python docs/publishing/render_models.py --check`. It needs no npm install:
   the renderer imports only its own TypeScript files. It would fail any pull
   request that changes a model, the engine's answer or the renderer without
   rebuilding the pages (`bin/publish-site`), which is the point, and which
   also means the second of #208 and #209 to merge must rebuild them. Until
   then `bin/publish-site` rebuilds the pages, and the frontend tests check the
   committed pages' default view, tables and review counts.

## Human review

Pending. The GUI lane owner (@kriishnaa-18) reviews the branch before anything
is committed; sponsor (@nymble) review of the open questions above is still to
come. Nothing in this entry was accepted or rejected by a human yet.
