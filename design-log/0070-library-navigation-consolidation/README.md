---
schema: "archdoc/v1"
id: DL-0070
title: "Consolidate Library navigation and preserve the SDL layout"
type: process
status: draft
version: "0.1.0"
date: "2026-11-25"
updated: "2026-11-25"
record: DL-0070
defers_to: ARCH-0001
bears_on: [APP-0001, DL-0043, DL-0051, DL-0060, DL-0067]
---

# Consolidate Library navigation and preserve the SDL layout

## Request

Use a single Library tab in the desktop application and browser preview.
Improve the space and clarity of the record tables while preserving their data,
routing, and review statuses. Keep the original SDL layout and interactions,
with fonts, controls, spacing, and colors that match the application.

## Produced

- A compact application header and four top-level tabs. The right-aligned
  Library selector opens All Library Records, CWE Weaknesses, Security
  Requirements, and SDL. The existing hashes and browser history stay in sync.
- Three independently scrollable record tables with bottom-aligned 50-record
  pagination, Clear filters, source disclosures, and flattened Details
  inspectors. Source and model popovers close when focus moves to another
  control. Escape closes the current popover and returns focus to its summary.
  The complete CWE attribution is available in a compact disclosure below pagination.
- Model requirements and recorded coverage follow the global model. Coverage
  loads automatically for a model with one product and stays expanded by
  default. The requirements workspace scrolls when necessary to keep at least
  180 pixels available for the table. The reference catalog remains independent.
- SDL uses the original program summary, requirement sets, phase tables,
  milestones and gates, proposals, and open gaps. It keeps the model selector
  and original interactions. Updated visual styles support both themes. The
  desktop uses the local engine and the preview uses the published examples.

## Human review and superseded SDL design

An earlier iteration combined SDL records into a sortable, paginated table
with search, type and phase filters, and a side inspector. The user rejected
that design because it changed how SDL information was organized and displayed.
The original renderer and interactions were restored. The iteration history
below records the work and validation at each stage. Review of the correction
is pending.

## Initial consolidation validation

- Chrome exercised all four Library views with published fixtures and with the
  local engine. Checks included table-specific filters and inspectors, legacy
  URLs, browser history, keyboard interaction, and SDL in light and dark themes.
- The macOS Tauri bundle connected to the local engine and displayed the Library
  selector and each workspace. The signed bundle passed its packaging checks.
- Frontend type checks and 491 tests passed. The engine passed 784 tests with
  10 skips. Rust formatting, Clippy, and four Rust tests passed. The generated
  Pages assets matched a fresh build and 38 publishing tests passed.
- The architecture and pinned library validations reported zero errors. The
  published relative links and identity checks passed.

## Follow-up layout refinements

The Library selector now sits at the right end of the application navigation
row. It has an accessible name and appears only when Library is active. The
header keeps the brand, model picker and summary, and engine status in a
shorter layout after removal of the description.

The CWE table puts attribution in a keyboard-operable disclosure below
pagination. Its collapsed summary shows the copyright holder and Terms of Use.
The expanded section uses the original catalog notice, license, and Terms of
Use link. The table fills the space freed by the collapsed footer.

At a 1280 × 800 browser viewport, the CWE table grew from 158 to 332 CSS
pixels and from three to eight fully visible rows. Chrome verified the
disclosure and exact legal text, all four Library views, and the light, dark,
and narrow layouts. The rebuilt macOS app showed the compact header, navigation
selector, and collapsed footer against the local catalog. Type checking, 500
frontend tests, 38 publishing tests, preview freshness, documentation
validation, and macOS bundle signature verification passed.

## Compact navigation, source information, and details

The four Library headings now carry source disclosures that work with a
keyboard. The model header uses a compact review indicator and exposes the
original model family, provenance, and review and path counts in a disclosure.
The indicator reports accepted threat reviews. It identifies explicitly
unreviewed proposal examples using the model family supplied by the engine.
The SDL source disclosure also holds the program overview and open gaps.

All four inspectors use a common Details heading, a single selection prompt,
and compact rows for metadata. Secondary sections use native disclosures and
dividers. Descriptions have the full inspector width, and code examples retain
their dedicated formatting. The tabs use an underline for the active state
and retain the existing keyboard behavior and right-aligned Library selector.

All 502 frontend tests, 38 publishing tests, TypeScript checks, preview
freshness, link and identity checks, and architecture validation passed. Chrome
verified the four Library views with both published data and the local engine,
including source and model disclosures, long details, and narrow widths in both
themes. All four views were also visually inspected in the macOS application
with empty and populated inspectors. The rebuilt bundle passed signature
verification.

## Library pagination, filter reset, and model coverage

All four Library tables scroll independently and use a right-aligned footer
with a 50-record page size. Single-page results keep the range and count.
The CWE attribution disclosure follows the footer. Empty workspaces show
one message that distinguishes missing records from an unsuccessful search.
Clear filters appears beside Search when it has something to reset. It
returns focus to Search and opens the first page while preserving the selected
Library view, global model, requirement browsing mode, and SDL program.

Model requirements follow the global model, including requirements without
recorded product scope. A single product loads coverage automatically.
Multi-product models provide a Product filter and display coverage for the
chosen product. The reference catalog keeps its state when the global model
changes. Superseded model and coverage requests cannot repopulate the view.

Recorded requirement coverage stays open by default and preserves the user's
disclosure state. A scrollable results area keeps the table available while
showing existing counts, evidence, threats, and hypothetical proposal outcomes.
The UI explains the limits of recorded evidence and leaves coverage calculations
in the existing provider.

The 511 frontend tests include real Chrome layout checks at 700, 1000, 1280,
and 1600 pixels for full, short, and empty tables. Chrome also verified both
themes, independent filters, and traversal of all 685 published Library
records. The rebuilt macOS app showed all four tables against the local
engine. In Security Requirements, switching from an empty model to the TCU
refreshed the table and coverage automatically. Type checks, 47 publishing
tests, four Rust tests, preview freshness, link, identity and architecture
checks, and macOS signature verification passed. The engine suite passed
784 tests with 10 skips. The pinned library validator reported zero errors
and 99 existing warnings.

## Restore the original SDL sections

SDL keeps its Library dropdown entry and existing route. The renderer and
data types match `main` at `18e28cd`. The selected model's program summary,
governing requirement sets, phase tables, milestones and gates, pending
proposals, and open gaps appear in their original order. The original model
selector, evidence links, review labels, and loading behavior are restored.

SDL uses the application's type scale, controls, surfaces, borders, link
colors, and light and dark status chips. Narrow screens can scroll individual
tables horizontally while the sections retain their order and full page flow.
The browser preview uses the same renderer with published example data.
The shared table footers, filter resets, and inspectors still apply to the
other three Library views.

TypeScript checks, 512 frontend tests, and 47 publishing tests passed.
Regression tests cover the section order, table columns, pending proposals,
model changes, and the Library route. Chrome verified light, dark, and
390-pixel layouts. The rebuilt macOS app showed the original sections against
the local engine. Preview freshness, published links and identities,
architecture validation, and the macOS bundle signature passed.

## Pre-commit review fixes

The source and model disclosures dismiss on outside focus or click. Escape
returns focus to the disclosure summary when focus was inside, and preserves
focus on an outside control when the disclosure was opened by pointer.

Security Requirements retains a 180-pixel minimum for its table. On short
windows the Requirements content scrolls so the table and pagination remain
reachable with coverage expanded. The browser preview and the desktop runtime
with its local sidecar passed checks at 721 × 468, 800 × 500, and 1280 × 800.
The standard layout keeps pagination at the bottom. The pre-commit cleanup
removed unused count badges, popover detail-row rules, and the unused model
source title. The 515 frontend tests include regression checks for outside
focus, Escape, and short workspaces. The publishing suite, preview freshness,
architecture checks, and the rebuilt macOS bundle verification also passed.
