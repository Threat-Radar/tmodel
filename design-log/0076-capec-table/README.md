---
schema: "archdoc/v1"
id: DL-0076
title: "CAPEC attack patterns table and details inspector (#236)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0076
bears_on: [APP-0001, DL-0056, DL-0060, DL-0070]
defers_to: ARCH-0001
---

# DL-0076: the CAPEC attack patterns table

AI-assisted design record (per `CLAUDE.md`), written with Claude Code. DL-0074 is on the branch
for #289 and DL-0075 is reserved for #288, so this entry is DL-0076.

## Question asked

Issue #236: add an accessible Attack Patterns (CAPEC) table to the desktop app on the engine's
API. It must search, sort, filter and page; show the ID, name, description, abstraction and
status the API gives; inspect one attack pattern in full; show the source attribution CAPEC's
terms require; have accessible loading, empty, error and retry states; and work on fixture and
live data without changing what the app already does. #236 was blocked on data until the CAPEC
import (#244, DL-0056) added `GET /attack-patterns/table`, `GET /attack-patterns?id=` and a
table fixture. The browser preview on GitHub Pages must work too.

## What was produced

| File | Change |
|---|---|
| `apps/desktop/src/attack-pattern-types.ts` | new: the two answers' types, the sorts, filters and CAPEC's own order for its enumerations, and the provider interface |
| `apps/desktop/src/engine-attack-pattern-provider.ts` | new: the engine client, which sends every query parameter and checks each answer's shape before the view reads it |
| `apps/desktop/src/attack-pattern-fixture.ts` | new: the fixture provider, with the engine's query rules over the 13 sample rows |
| `apps/desktop/src/attack-pattern-provider.ts` | new: picks the engine or the fixture |
| `apps/desktop/src/attack-pattern-view.ts` | new: the table, its controls and states, and the inspector |
| `apps/desktop/src/catalog-entry-render.ts` | new: the inspector's field rendering, moved out of `weakness-view.ts` so both inspectors share it |
| `apps/desktop/src/fixtures/attack-pattern-details.json` | new: the engine's details answer for each of the 13 sample rows |
| `apps/desktop/src/weakness-view.ts`, `weakness-fields.ts` | the CWE inspector uses the shared renderer; the field helpers accept a CAPEC entry |
| `apps/desktop/index.html`; `apps/desktop/src/styles.css`, `main.ts`, `app-navigation.ts`, `library-presentation.ts` | the view's markup, styles and wiring, its `#attack-patterns` route, and an optional page size for the shared pager |
| `apps/desktop/src/*.test.ts` | five new test files; the shell, navigation, welcome, layout and style tests extended to the fifth Library view; and the CWE view's test for its proposal label (choice 7) |
| `apps/desktop/src/fixtures/README.md`, `apps/desktop/THIRD_PARTY_NOTICES.md` | the details fixture, and CAPEC among the third-party data the app carries |
| `engine/tests/test_attack_pattern_table.py` | one test that keeps the details fixture equal to the engine's answers |
| `docs/app/` | the browser preview, rebuilt by `docs/publishing/render_app.py` |

No engine code changed.

### What the view does

- **Where it is.** A fifth Library view, "CAPEC Attack Patterns", after "CWE Weaknesses" in the
  Library selector (DL-0070), at `#attack-patterns`. The link opens the view directly and keeps
  its place in history.
- **The table.** One row per attack pattern: ID, name, abstraction, status, likelihood of attack
  and typical severity, each a sortable column, then counts of related CWE weaknesses, ATT&CK
  techniques, attack steps and mitigations. Each cell is one field of the engine's row, or the
  length of one of its lists. Four filters (abstraction, status, likelihood, severity) list their values
  with the counts the engine gives under the other filters and the search. Search waits 250 ms
  after typing, or runs at once on Enter. Pages hold 50 rows. A filter, sort or search goes back to
  the first page, and a page past the end shows the last one.
- **Order.** The engine sorts; an enumeration sorts in CAPEC's own order (Meta, Standard,
  Detailed; Stable to Deprecated; High to Unknown; Very High to Very Low), rows without the value
  last in both directions, and equal values in ID order. The filter menus list values in the same
  order.
- **The inspector.** Selecting a row shows its name, ID, status, description and an overview at
  once (abstraction, likelihood, severity, the six counts, the tmodel object ID and the entry's
  page on capec.mitre.org), then asks for the full entry. Its sections follow CAPEC's schema:
  extended description, alternate terms, related attack patterns, execution flow, prerequisites,
  skills and resources required, indicators, consequences, mitigations, example instances,
  related CWE weaknesses, ATT&CK techniques, taxonomy mappings, references, notes, the proposed
  relationships the import makes, any field this reader does not know, and the content history.
  Each is a native disclosure, with an item count where CAPEC's field has items; only the
  extended description starts open.
- **Safety.** Catalog text reaches the page only as text, and a link only when its URL is HTTP or
  HTTPS, opening in a new window without an opener. The shared renderer is the CWE inspector's,
  unchanged in these rules (DL-0060).
- **Attribution.** Below the pager, as for CWE (DL-0070): a collapsed disclosure whose summary
  gives MITRE's copyright years as the answer's `catalog.notice` writes them, holding the notice,
  the licence and a link to the CAPEC Terms of Use. It shows with every answer the engine or the
  fixture gives, and hides after a failure.
- **States.** Loading sets `aria-busy` and a polite status. An empty answer says whether nothing
  matches or the release has no attack patterns. A failure gives the engine's message and a Retry
  button; a failed details request keeps the table and the row's overview and has its own retry.
  A table request that failed while the engine was not yet known to be up is made again once its
  health check answers, as the CWE view does. A newer request always wins over an older one.

## Choices the agent made, open to review

1. **A Library view, not a new top-level tab.** The issue says "tab"; since DL-0070 every record
   table, CWE's included, is a view in the Library tab.
2. **Fixture or engine, as for CWE.** The preview always uses the fixture, and the desktop app does
   with `?attackPatternSource=fixture`; otherwise it asks the local engine. There is no third,
   published source: publishing all 615 attack patterns of the release is a decision of its own,
   as it was for CWE (DL-0060, choice 3).
3. **A details fixture of the engine's own answers.** `attack-pattern-details.json` holds
   `GET /attack-patterns?id=` for all 13 sample rows, and an engine test fails when it drifts, as
   the table fixture's does. So the preview and fixture mode show the full inspector. This departs
   from the CWE fixture, which stops at the row (DL-0060, choice 4) for fear of drift; the engine
   test answers that fear.
4. **The details load on demand.** The 13 answers are a separate 124 kB chunk (27 kB compressed),
   loaded on the first selected row or search, so the app's main bundle grows only by the table
   rows and the view (42 kB).
5. **The fixture follows the engine's query rules.** Its search reads alternate terms from the
   details, so it looks in the same fields as the engine's, and its filters, order, paging and
   facet counts are the engine's. The fixture tests run the engine's own test cases and expect
   the engine's answers.
6. **One renderer for both inspectors.** The field rendering moved from `weakness-view.ts` to
   `catalog-entry-render.ts`, for the reason DL-0056 shared the CWE reader with the CAPEC one:
   two copies of the same rules would drift. Each inspector keeps its own class names, through a
   prefix, so the CWE inspector's page structure and styles stay as they were.
7. **One proposal label.** The shared renderer labels a proposed relationship "Proposed, not
   human-reviewed". In the Weaknesses tab only the punctuation changes: the dash between the two
   parts becomes a comma.
8. **Description in the inspector, not a column,** as in the CWE table. The table keeps six
   sortable columns and four counts; the counts of related attack patterns and examples are in
   the inspector.
9. **"Not stated" for a value CAPEC does not give,** in muted text, where the other tables show a
   dash. A screen reader reads it as words.
10. **Execution flow as steps.** Each attack step shows "Step N · Phase", what the adversary does,
    and its techniques as a list. Any other field a step has is still shown.
11. **Links go to MITRE's pages.** CWE, ATT&CK and CAPEC IDs in the inspector link to
    cwe.mitre.org, attack.mitre.org and capec.mitre.org, as the CWE inspector's CAPEC links do.
    Related attack patterns are shown as CAPEC writes them, so anything an item holds besides its
    nature and target is shown too.
12. **References are resolved.** Each citation shows its title (linked to its URL), section,
    authors, edition, publication, publisher, date and URL date. A date reads as
    `2004-02` from CAPEC's year and `--02` month. A citation the release does not define says so.
13. **The engine's release in the source notice.** After the first answer, the notice names the
    release, its date and how many attack patterns it holds.
14. **Focus is never dropped.** Beyond the CWE view's behaviour: when a keyboard user's Retry,
    page button or detail retry is hidden or disabled, or a failure or an empty answer hides the
    table they were in, focus moves to the next sensible control (Search, the other page button,
    Retry, or the inspector). The selected row's ID button carries `aria-current`, count cells
    are read as "1 mitigation" or "3 mitigations", and the search and filters form a named group.
15. **A narrower table minimum.** 960 px instead of the CWE table's 1090 px, so all ten columns
    show at 1440 px; at the app's default 1280 px window the table scrolls sideways, less than the
    CWE table does.

## How it was checked

- **Frontend:** `npm run typecheck`, `npm test` (49 files, 756 tests) and `npm run build` pass,
  apart from the flaky layout check under Follow-ups, which fails in some runs on `main` too.
  The new tests cover the engine client against the engine's real table and details answers
  (`engine-attack-pattern-provider.test.ts`), the fixture against the engine's own query cases
  (`attack-pattern-fixture.test.ts`), the provider choice, the shared renderer, and the view:
  rendering, search, filters, sorting, paging and its edges, selection, every state, stale
  answers, engine recovery and focus (`attack-pattern-view.test.ts`).
- **Engine:** the details fixture test passes; the full suite (819 passed, 10 skipped), `ruff
  format --check` and `python -m engine health --in-process` pass. `ruff check` reports only the
  five UP038 lines in `model_graph.py` and `tara.py` that `main` already has.
- **Preview and publishing:** `render_app.py` rebuilt `docs/app/`, `render_app.py --check` passes,
  and so do the 38 publishing tests, `check_links.py` and `check_identities.py`.
- **By hand, against a running engine:** `tmodel serve` on a spare port with the CAPEC sample
  (`TMODEL_CAPEC_CATALOG` and the sample's one-record library), and the app in Vite, driven in
  headless Chrome over the DevTools protocol at 1440 px, 700 px, light and dark. Enter on an ID
  button and Space on a section summary worked; all 15 of CAPEC-66's sections loaded; all five
  inspector links were HTTPS with no opener; the severity filter, likelihood sort, an
  alternate-term search ("HTTP Desync") and Clear filters gave the engine's answers; a blocked
  request showed the error, and Enter on Retry loaded the table and left focus on Search. The
  page did not scroll sideways at 700 px, and the console had no errors or warnings. The same
  run on the rebuilt preview, served at `/tmodel/app/`, gave the same answers from the fixture,
  fetched the details chunk once and had no errors.
- **Not checked:** MITRE's full 3.9 file was not at hand, so the 615 attack patterns of the
  release were not run through the view; paging was tested on the 13 sample rows five to a page.
  The macOS app was not built or opened.

## What a human accepted

- @Clovier, 2026-11-27: took over #236 and asked for it to be built ("start on 288, 290, and
  236"); the wording and code are Claude Code's draft until the pull request review accepts them.

## What was rejected, and why

The PR #294 review found that Enter left keyboard focus on the selected row. At a 700 px
window, reaching the inspector then took 52 Tab presses. The review requested direct access
to the inspector and a way back to the selected row.

The agent set these aside during the initial implementation:

- **A fixture that stops at the row, as CWE's does.** The issue asks for a details inspector, and
  the preview could not show one; the engine test keeps the fuller fixture from drifting.
- **The details in the main bundle.** Every desktop user would load 124 kB that only the fixture
  uses.
- **A copy of the CWE inspector's rendering in the CAPEC view.** Two copies of the text-only
  rendering rules would drift.
- **One neutral class prefix for both inspectors.** It would change the CWE inspector's page
  structure and its tests for no visible gain.
- **Each attack step as generic label and value rows,** the first draft: the step's number,
  phase, description and techniques read as separate rows, with all the techniques on one line.
- **The CWE table's 1090 px minimum,** also from the first draft: it hid the last column at
  1440 px.

## Keyboard focus review fix

Enter or Space on a CAPEC row button selects the record and focuses the existing Details
inspector immediately, while the full entry loads. The inspector's accessible name includes
the selected record ID and title. Its first Tab stop is **Back to selected row**, which
returns focus to the selected ID button so Tab can continue through the table. Pointer clicks
still select the record as before. The row, inspector and return button use the design system's
focus outline.

Search, sort, filter and page controls retain focus while they remain available. A refreshed
row is found by its CAPEC ID. If the selected row leaves the current results while focus is
in its inspector, focus returns to the table region or to Search for an empty result. A page
button that becomes disabled transfers focus only if it still held focus when results arrived.

The native Tauri test builds used the pinned 615-record catalog from a local file. In the
700 px dark window, Enter on CAPEC-1 focused Details immediately. Tab and Enter returned
focus to CAPEC-1, and the next Tab reached CAPEC-2. Pagination, alternate-term search,
the Meta filter and descending ID sort all kept focus usable. The 1280 px light window
passed the round trip for CAPEC-66 and showed its related CWE links. The generated preview
passed keyboard and focus-outline checks at both widths. All 762 frontend tests passed on
rerun after the documented model-popover test flaked.

## Follow-ups

- **The packaged app has no CAPEC release.** `bin/build-engine` bundles the CWE release (ADR-0014)
  but not CAPEC's, so the installed app's table shows the engine's message (download
  `capec_v3.9.xml` and set `TMODEL_CAPEC_CATALOG`) until the build bundles it the same way.
- **Links inside the app,** from a CWE ID to its row in the Weaknesses view and from a related
  attack pattern to its row, in place of MITRE's pages.
- **The full release,** once a copy matching the library's pin is at hand: the 615 rows, paging
  past 50 and the slowest entries.
- **One table controller.** The Library, CWE and CAPEC views each keep their own search, filter,
  sort and paging code, as the first two did; one shared controller could serve all three, with
  this view's focus handling.
- **A flaky layout test.** In `canvas-layout.test.ts`, the model popover's focus check fails in
  some runs on a loaded machine, on `main` as on this branch (6 and 7 of 12 interleaved runs).
  It does not involve this view.
- **For the CWE view's owner:** the proposal label in choice 7.

## Gate

`bin/validate-archdoc` clean; `git diff --check` clean. The frontend, engine and publishing
checks above pass.
