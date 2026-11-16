---
schema: "archdoc/v1"
id: DL-0052
title: "CWE weaknesses table and full-entry inspector"
type: process
status: draft
version: "0.1.0"
date: "2026-11-15"
updated: "2026-11-15"
record: DL-0052
bears_on: [APP-0001, DL-0050, DL-0051]
defers_to: ARCH-0001
---

# CWE weaknesses table and full-entry inspector

## Request

Issue #234 asks for a GUI over the CWE 4.20 feed delivered by #144 and PR #233:
a searchable, sortable, filterable and paged table; a details inspector that
preserves the catalog's richer fields; explicit presentation of imported
relationships as proposals; the nine-record development fixture; and a useful
GitHub Pages preview. The work must preserve the existing Model Report, Attack
Paths, Explore Graph, Library and SDL views.

This log records the implementation proposed on the branch
`issue-234-cwe-weaknesses-table`. It is an AI-assisted draft. No design choice
below is accepted until a human reviews and merges it.

## Design

**A dedicated provider contract.** `WeaknessDataProvider` mirrors the engine's
`GET /weaknesses/table` and `GET /weaknesses?id=…` responses rather than
translating them into library documents. The engine provider sends every table
query explicitly and validates successful JSON before the view consumes it.
HTTP failures, malformed JSON and malformed response shapes become visible
errors with retry controls.

**Server-owned table semantics.** Desktop search, filtering, semantic sorting
and pagination are sent to the engine. The client renders the returned order and
contextual facets. Search is debounced by 250 ms; filters, sort direction and
page-size changes reset to the first page. The available page sizes are 25, 50
and 100, with 25 as the default. This keeps the complete 969-row catalog out of
the DOM while preserving the engine's CWE enumeration order.

**Complete live inspector.** Selecting a row first shows its bounded summary,
then independently requests the full entry. Structured CWE fields are rendered
as text under independent native `details` disclosures, with fields not already
surfaced retained under “Additional Catalog Fields”. The overview keeps the id,
classification, status, likelihood, description, row counts and official link
visible. Explanatory sections open by default; the long mitigation, example,
proposal, additional-field and history sections start collapsed, and selecting
another weakness restores those deliberate defaults. Section headings carry
source-derived item counts where the response has a meaningful item boundary.
Alternate terms use the preserved nested field so both each term and its
description remain visible. Example-code line breaks are retained in inert
`pre`/`code` text. Observed CVEs, CAPEC mappings and imported tmodel Assertions
are displayed. Assertions whose status is `proposed` are labelled “Proposed —
not human-reviewed”, followed by their stable id, `asserted_by` party and
`generated_by` provenance; the UI does not infer acceptance from MITRE's source
provenance.

**Text-only catalog rendering.** CWE's `#xhtml` representation is parsed only to
extract text and is assigned through `textContent`; no catalog value reaches
`innerHTML`. Links are emitted only when their parsed protocol is HTTP or HTTPS,
and external links use `noopener noreferrer`. The engine remains responsible
for its pinned digest and bounded XML/ZIP import described by DL-0050.

**Truthful fixture and Pages behavior.** `?weaknessSource=fixture` selects the
nine table rows generated from the sample catalog. Pages selects that same
provider automatically. Search, facets, sorting and pagination run locally over
those nine rows, but selection stops at the row summary and explains that full
fields require a live engine. The fixture does not invent a detail response.
The source notice says it is a nine-record sample rather than the complete
catalog.

**Attribution travels with the data.** Both providers render `catalog.notice`,
the complete `catalog.license` and the HTTPS `catalog.terms_url` returned with
the response. The fixture therefore presents the same MITRE designation and
licence as live catalog rows.

**Failure isolation.** Table and detail requests have separate latest-request
guards and retry buttons. A failed detail request leaves the usable table and
row summary in place. When desktop initially requests before the local engine
is healthy, the table performs the same one-time recovery on the first observed
healthy transition as the Library view.

## Files and boundaries

- `weakness-types.ts` defines the API and provider boundary.
- `engine-weakness-provider.ts` owns HTTP construction and response validation.
- `weakness-fixture.ts` implements the bounded nine-row preview semantics.
- `weakness-fields.ts` converts preserved CWE field values into safe text.
- `weakness-view.ts` owns table interaction, pagination and the inspector.
- `index.html`, `styles.css`, `main.ts` and `app-navigation.ts` connect the new
  view without changing the existing providers or view implementations.

The GUI does not download, cache, replace or repin the catalog. How the desktop
application obtains the pinned bytes remains DEC-008. It does not add mutations,
reviews or acceptance controls; those remain governed workflows outside #234.

## Verification

The change adds focused provider, provider-selection, fixture, field-safety and
view tests. They cover query parameters, malformed responses, engine errors,
semantic order, individual and combined filters, contextual facets, paging,
stale requests, independent retries, the truthful row-only fixture, text-only
XHTML, HTTP(S)-only links, nested alternate-term descriptions, preserved
additional fields, Assertion provenance, full detail rendering and the explicit
proposal label. A stylesheet regression reads the actual CSS and checks the
light and dark pagination, disclosure summaries, disabled-control and
focus-indicator contrast ratios. Inspector tests use realistic nested fields to
check disclosure labels and counts, default state, selection reset, preserved
code line breaks, safe links and the full Assertion provenance. Native
`details`/`summary` supplies standard Enter and Space keyboard interaction and
allows multiple sections to remain open.
The existing navigation test includes the Weaknesses tab in its Arrow, Home and
End keyboard behavior.

On 2026-11-15, after the independent-review fixes, the complete frontend suite
passed with 36 files and 396 tests; `npm run typecheck`, `npm run build` and
`npm run build:pages` passed. The
existing generator rewrote `docs/app/`, then `render_app.py --check` reproduced
it byte for byte (8 models and 550 library records). The 14 publishing guard
tests passed, as did `bin/validate-archdoc` (28 documents), the published
identity and link checks, `git diff --check`, and the pinned submodule check.

The generated Pages build was exercised in a browser at its narrow responsive
layout. Its search, status filter, semantic likelihood sort, row summary,
sample-source warning and complete MITRE attribution were visible and usable;
the Pages provider-selection test establishes that this build cannot construct
the localhost provider. A second browser smoke test ran the frontend against
the loopback engine with the bundled, digest-pinned nine-entry sample. CWE-79's
full field sections loaded through the browser's `DOMParser` path; alternate-term
descriptions and Assertion ids and provenance were present; all 26 generated
Assertions were shown as “Proposed — not human-reviewed”; all 46 rendered detail
links were HTTP(S), with no scripts or inline event handlers in the inspector;
and the browser console had no warnings or errors.

The full 969-weakness MITRE 4.20 file was not present, and neither
`TMODEL_CWE_CATALOG` nor a newer library override was configured. The live test
above is therefore sample-catalog integration evidence, not full-catalog
verification. The full catalog still requires bytes whose digest matches the
library pin.

The disclosure-layout update reran all 36 frontend files: 400 tests passed,
followed by typecheck and the production frontend build. The existing Pages
generator rebuilt `docs/app/` and `render_app.py --check` reproduced 8 models
and 550 library records byte for byte. The generated preview loaded with the
Weaknesses table selected and no regression in its table layout; its row-only
fixture intentionally cannot exercise the live inspector disclosures. The
architecture, generated-link and published-identity checks also passed. The 14
Python publishing guard tests were not rerun for this update because neither
available Python environment has pytest; their prior passing result remains the
evidence recorded above. Native inspection of the updated full-entry disclosure
layout remains the human review step before the branch is submitted.

## Proposed choices open to review

1. A separate Weaknesses top-level tab, labelled “Weaknesses”, with the view
   heading “Weaknesses (CWE)”.
2. A 25-row default and 25/50/100 page-size choices.
3. Pages uses the existing nine-record fixture, not a published copy of all 969
   rows, pending a separate decision to publish a full catalog-derived artifact.
4. Fixture details stop at the row summary rather than maintaining a second,
   easily drifting full-entry fixture.
5. Every preserved field not represented by a named inspector section appears
   in an additional-fields section instead of being silently hidden.
6. Imported Assertions are informational in this view and have no accept/reject
   control.

## Limits and follow-ups

- The static preview cannot show full entry fields or generated Assertion
  objects because those are not in the table fixture.
- Vitest runs in Node and this repository has no browser-DOM test dependency, so
  the browser's native `DOMParser` branch is exercised by the browser smoke test,
  not an automated DOM test. The automated tests still verify text-only output,
  inert script markup and HTTP(S)-only link creation. Adding a browser test runner
  would require a separately reviewed development dependency.
- Catalog acquisition and packaging remain DEC-008.
- CWE categories, views and hierarchy remain #145; reconciliation remains #146.
- Mapping CWE mitigations into the core graph still needs the model decision
  recorded by DL-0050 and #61. The table and inspector display the catalog
  mitigation content without inventing a graph predicate.
