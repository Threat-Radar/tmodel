---
schema: "archdoc/v1"
id: DL-0024
title: "Publish the reviewed SDL report; refresh RPT-0013; publish the SDL object model (#67)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-22"
updated: "2026-10-22"
record: DL-0024
bears_on: [DEC-001]
defers_to: ARCH-0001
---

# DL-0024: publish the reviewed SDL report and refresh RPT-0013

AI-assisted design record (per `CLAUDE.md`). Sponsor: @nymble, working with Claude Code.

## Question asked

The sponsor asked whether `docs/reports/sdl.html` was correct and current. It was not. It rendered
`research/0013-sdl-conformance/report.md` v0.3.0, whose body was still the 2026-10-01 first draft
with a short update note on top. That body stated claims the SDL ingestion and crosswalk had since
disproved: "no guideline is a library record yet", "only SSDF PO.4 names" a release gate, "SSDF 1.2
… final status unconfirmed", and a 19 × 7 MAP-0001. The reviewed public report ("Secure Development
Lifecycle", written 2026-10-02/03 and adversarially reviewed) existed only outside the repo, so the
publishing pipeline had never seen it. The sponsor approved three changes.

## What was produced

1. `research/0013-sdl-conformance/sdl-report.md` (RPT-0013-PUB v1.0.0): the reviewed public report,
   exported unchanged except for removing the byline and replacing the interactive diagram with a
   static SVG (`docs/reports/img/sdl-object-model.svg`, light theme, no scripts).
   `reports.yaml` now publishes it as `docs/reports/sdl.html`.
2. `research/0013-sdl-conformance/report.md` v0.4.0: the first-draft body is replaced by the
   verified findings and pointers to the evidence (library topic `sdl`, MAP-0001 v0.2.0,
   RPT-0013-OM, the public report). It is no longer published; it is the internal research record.
3. `research/0013-sdl-conformance/sdl-object-model.md` v0.2.1, published as
   `docs/reports/sdl-object-model.html`. The only content change: the link to the companion YAML
   now points at GitHub, because the YAML is not published.
4. `docs/publishing/render_report.py`: local images (`![alt](path)`, path relative to the source,
   rewritten relative to the page; remote images dropped), and paragraph soft line breaks rendered
   as spaces so emphasis can span lines (two bold phrases in the object model were broken).

## Method and checks

- `check_identities.py`: 423 pages clean. `check_links.py`: every relative link resolves.
  `bin/validate-archdoc`: 0 errors. The rendered pages were scanned for leftover Markdown
  (`**`, `](`, list markers): none outside code blocks.
- The SVG reproduces the reviewed diagram's ten objects and ten edges exactly (same coordinates).

## Choices made, open to review

- **The public report keeps its 2026-10-03 facts.** It is versioned 1.0.0 as reviewed then; it was
  not re-researched. Events after 2026-10-03 (iteration 8, ADR-0010 holding DEC-001b open) are
  reflected in `report.md`, not in the public report.
- **`report.md` is no longer published.** The public report replaces it on the site; the research
  record stays in the repo.
- **The object model's Mermaid diagram renders as a code block** on the page (the site loads no
  scripts). A static SVG of the full 46-type diagram is a possible follow-up.

## Rejected

- Hand-editing `docs/reports/sdl.html`: `docs/` is generated; the fix had to be in the source.
