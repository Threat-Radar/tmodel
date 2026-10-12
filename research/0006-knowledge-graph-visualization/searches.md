---
schema: "archdoc/v1"
id: RPT-0006-searches
title: "RPT-0006 search log"
type: research
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-05"
record: RPT-0006
---

# RPT-0006 — search log

Record searches and repository inspections that contribute to the report. Preserve the
query or command, name the relevant dimension from `dimensions.md`, and link useful leads
through `sources.md`. Searches are not evidence by themselves.

| date | purpose / dimension | search or query | result / useful leads | rejected leads and reason |
|---|---|---|---|---|
| 2026-10-04 | Cytoscape.js; dimensions 1–8 | Official docs and repository: graph model, events, styles, layouts, performance, license, releases | Cytoscape.js docs; GitHub repository/releases; v3.34.0 release record; MIT license | Cytoscape desktop results rejected as a different product |
| 2026-10-04 | D3; dimensions 1–8 | Official D3 modules and repository: force, hierarchy, drag, zoom, rendering, license, releases | D3 force/drag/zoom/hierarchy docs; v7.9.0 release; ISC license | General gallery examples rejected as insufficient evidence of reusable graph-editor capability |
| 2026-10-04 | Sigma.js; dimensions 1–8 | Official docs and repository: Graphology model, events, reducers, layers, WebGL, layouts, releases, license | Sigma v3 docs; repository; v3.0.3 stable release; v4 alpha docs flagged separately | v4 alpha features not treated as stable-v3 capability |
| 2026-10-04 | yFiles; dimensions 1–8 | Official developer guide: model, editing, interaction, layouts, styling, filtering, analysis, persistence, licensing, releases | yFiles for HTML 3.1 docs and licensing pages | Vendor case studies rejected as unnecessary for capability claims; no independent benchmark located |
| 2026-10-04 | Neo4j Bloom; dimensions 1–8 | Official Bloom guide: features, Scenes, Perspectives, styling, editing, GDS, installation and license tiers | Bloom 2.37 guide; 2.37.1 deployment listing; Desktop/license documentation | Documentation's Creative Commons notice rejected as the product software license |
| 2026-10-04 | Gephi; dimensions 1–8 | Official product, quickstart, layout docs, repository and releases | Gephi 0.11.3; layouts, filters, metrics, OpenGL claims; CDDL/GPL licensing | Project scale claim retained as a claim, not treated as a benchmark |
| 2026-10-04 | Kùzu tooling; dimensions 1–8 | Official Kùzu and Explorer repositories: delivery, stack, modes, version, license, lifecycle | Explorer MIT repository; Kùzu 0.11.3 repository; both archive notices | G6's full feature set rejected as evidence for Explorer unless Explorer docs/code expose it |
| 2026-10-04 | Memgraph tooling; dimensions 1–8 | Official Lab docs, product page, release notes, legal page and repositories | Lab 3.x features, GSS, expand/collapse, split views, GraphChat; separate license families | Community bug report on a memory failure rejected as general scale evidence |

## Follow-up query groups

- Primary evidence still missing for Kùzu Explorer interaction/layout behavior and for
  Memgraph Lab's practical graph-size limits.
- Exact commercial/OEM terms and pricing implications for yFiles, Bloom, and Memgraph Lab.
- Hands-on evidence beyond the bounded Cytoscape.js and Sigma.js scan, especially for
  accessibility, layout stability, live/progressive loading, coordinated views, and
  representative scale.

## Prototype and hands-on checks

Record reproducible checks separately from searches. Do not promote an observation into a
general finding without recording its candidate version and test context.

| date | candidate / version | purpose / dimension | fixture and check | result / observation | source or artifact |
|---|---|---|---|---|---|
| 2026-10-05 | Cytoscape.js 3.34.0 | dimensions 1–8 | Common 11-node/11-edge fixture in headless Chrome: pointer selection/drag, wheel navigation, inspection, mutations, CoSE/breadth-first, style/path/filter, domain snapshot, 300/600 sanity graph | All listed checks completed. Evidence metadata was inspectable; two proposed nodes hid without fixture mutation; one non-blocking HTTP 404 was logged. No editor/review workflow, accessibility, persistence, or benchmark was tested. | Findings retained in `report.md` Section 9; temporary harness and generated artifacts removed after capture |
| 2026-10-05 | Sigma.js 3.0.3 + Graphology 0.26.0 | diagnostic; dimensions 1, 6, 8 | First common-fixture page load | Failed: `Sigma: could not find a suitable program for node type "asset"!`. Fixture semantic `type` collided with Sigma's render-program attribute. Classified as Sigma/Graphology integration adapter issue, not a WebGL or candidate suitability result. | Exact error and diagnostic conclusion retained in `report.md` and this row; temporary harness removed after capture |
| 2026-10-05 | Sigma.js 3.0.3 + Graphology 0.26.0 | dimensions 1–8 | Minimal adapter (`type` → `domainType`, visual `type: "circle"`), then the same checks and fixture as Cytoscape | Final run completed with no browser console/page errors. Selection/inspection, drag, camera, mutation, ForceAtlas2/layered layout, reducer styling/path/filter and 300/600 sanity graph completed; fixture unchanged. No complete editor/review workflow or benchmark tested. | Findings retained in `report.md` Section 9; temporary harness and generated artifacts removed after capture |
| 2026-10-05 | yFiles for HTML 3.1 | access check; dimension 8 | Official public demos and evaluation download path | Public demos were accessible, but the local evaluation package/license requires customer-center signup/download. No common-fixture run; assessment remains documentation-only. | yFiles Graph Editor demo; evaluation signup and setup docs |

The prototype directory was removed on 2026-10-05 after confirming that its JSON added
only harness-level measurements (such as pixel distances, event counts, and elapsed script
timings), not a material finding absent from this log and `report.md` Section 9.
