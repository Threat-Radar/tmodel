---
schema: "archdoc/v1"
id: RPT-0006-sources
title: "RPT-0006 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-05"
record: RPT-0006
---

# RPT-0006 — source log

Record every source used or considered. References live in `library/`, not inline in the
report. Use the exact canonical URL, pin a version or revision where relevant, identify
the evidence type, and name the claim or dimension supported. Keep notes brief; use the
library record for bibliographic detail.

| source name | exact URL | source type | version / revision | date accessed | evidence type | claim / dimension supported | notes |
|---|---|---|---|---|---|---|---|
| Cytoscape.js documentation | https://js.cytoscape.org/ | official documentation | current docs; assessed with v3.34.0 | 2026-10-04 | official documentation | Cytoscape graph model, mutation API, events, styling, layouts, algorithms, and performance guidance; dimensions 1–8 | Primary capability source |
| Cytoscape.js repository | https://github.com/cytoscape/cytoscape.js | official repository | v3.34.0 / repository state read 2026-10-04 | 2026-10-04 | source/license inspection | Project maturity, tests/benchmarks present, MIT license, release identity; dimension 8 | No local clone or benchmark performed |
| Cytoscape.js v3.34.0 release record | https://zenodo.org/records/20511608 | official archived release record | v3.34.0, 2026-06-02 | 2026-10-04 | official release metadata | Version pin | Links to the tagged GitHub source |
| D3 force documentation | https://d3js.org/d3-force | official documentation | D3 7.9.0 | 2026-10-04 | official documentation | Force simulation and renderer-independent output; dimensions 3 and 5 | No scale guarantee stated |
| D3 drag documentation | https://d3js.org/d3-drag | official documentation | D3 7.9.0 | 2026-10-04 | official documentation | Drag behavior and composition with zoom; dimension 2 | — |
| D3 zoom documentation | https://d3js.org/d3-zoom | official documentation | D3 7.9.0 | 2026-10-04 | official documentation | Pan/zoom behavior; dimension 2 | — |
| D3 hierarchy documentation | https://d3js.org/d3-hierarchy | official documentation | D3 7.9.0 | 2026-10-04 | official documentation | Hierarchical layout primitives; dimension 3 | — |
| D3 repository releases | https://github.com/d3/d3/releases | official repository / releases | v7.9.0 | 2026-10-04 | source/release inspection | Current stable version and maturity; dimension 8 | — |
| D3 license | https://github.com/d3/d3/blob/main/LICENSE | official repository license | main read 2026-10-04 | 2026-10-04 | source/license inspection | ISC license; dimension 8 | — |
| Sigma.js documentation | https://www.sigmajs.org/docs/ | official documentation | v3 docs; v4 identified as alpha | 2026-10-04 | official documentation | WebGL renderer, Graphology dependency, intended scale; dimensions 1–8 | Stable assessment uses v3 |
| Sigma graph-data documentation | https://www.sigmajs.org/docs/advanced/data/ | official documentation | v3 | 2026-10-04 | official documentation | Reducers can change visual attributes without graph mutation; dimensions 3, 4, and 6 | Key presentation/domain separation evidence |
| Sigma layers and renderer documentation | https://www.sigmajs.org/docs/advanced/layers/ | official documentation | v3 | 2026-10-04 | official documentation | WebGL/Canvas layers and custom layers; dimensions 4–6 | — |
| Sigma.js repository and releases | https://github.com/jacomyal/sigma.js | official repository | stable v3.0.3; v4.0.0-alpha.5 visible | 2026-10-04 | source/license inspection | MIT license, maturity, release state; dimension 8 | v4 alpha not treated as stable capability |
| yFiles for HTML developer guide | https://docs.yworks.com/yfiles-html/dguide/ | official documentation | 3.1 | 2026-10-04 | official documentation | Graph model, interaction/editing, styles, I/O, layouts, analysis; dimensions 1–8 | Primary capability source |
| yFiles automatic layouts | https://docs.yworks.com/yfiles-html/dguide/automatic-layouts-main-chapter/index.html | official documentation | 3.1 | 2026-10-04 | official documentation | Layout families and customization; dimensions 3–5 | — |
| yFiles licensing guide | https://docs.yworks.com/yfiles-html/dguide/deployment/licensing.html | official licensing documentation | 3.x | 2026-10-04 | official license documentation | Development versus deployment licenses; dimension 8 | Pricing and final redistribution terms remain open |
| yFiles 3.1 release announcement | https://www.yworks.com/news | official release page | 3.1, 2026-05-13 | 2026-10-04 | official release metadata | Current version and new layout/visualization features; dimensions 3, 4, and 8 | — |
| Neo4j Bloom user guide | https://neo4j.com/docs/bloom-user-guide/current/ | official product documentation | 2.37 | 2026-10-04 | official documentation | Bloom application purpose and version; dimensions 1–8 | Documentation license is not the product license |
| About Neo4j Bloom | https://neo4j.com/docs/bloom-user-guide/current/about-bloom/ | official product documentation | 2.37 | 2026-10-04 | official documentation | Search, exploration, inspection, editing, GPU rendering, feature tiers; dimensions 1, 2, 5–8 | — |
| Bloom Perspectives | https://neo4j.com/docs/bloom-user-guide/current/bloom-perspectives/perspective-creation/ | official product documentation | 2.37 | 2026-10-04 | official documentation | Saved business views, filters, styling, Scene actions, scan warning; dimensions 3–6 | 10M note is scan behavior, not display capacity |
| Bloom GDS integration | https://neo4j.com/docs/bloom-user-guide/current/bloom-tutorial/gds-integration/ | official product documentation | 2.37 | 2026-10-04 | official documentation | Temporary Scene scores versus properties written to DB; dimensions 3 and 6 | — |
| Bloom installation and activation | https://neo4j.com/docs/bloom-user-guide/current/bloom-installation/installation-activation/ | official licensing/deployment documentation | Bloom 2.37 / current Neo4j 5 and CalVer guidance | 2026-10-04 | official license documentation | Enterprise plugin key and collaboration/remote deployment boundary; dimension 8 | Exact commercial terms need follow-up |
| Gephi Desktop product page | https://gephi.org/desktop/ | official product page | 0.11.3 | 2026-10-04 | official documentation/vendor claim | Interaction, layouts, filters, metrics, OpenGL and scale claim; dimensions 1–8 | 100k nodes/1M edges remains unverified claim |
| Gephi quickstart | https://gephi.org/quickstart/ | official documentation | current | 2026-10-04 | official documentation | Layout, attribute/topology filtering, appearance; dimensions 2–6 | — |
| Gephi repository | https://github.com/gephi/gephi | official repository | v0.11.3 | 2026-10-04 | source/license inspection | Java/OpenGL architecture, extension APIs, CDDL 1.0/GPLv3; dimension 8 | — |
| Gephi releases | https://github.com/gephi/gephi/releases | official repository / releases | v0.11.3 | 2026-10-04 | official release metadata | Version, active maintenance, weight/layout/edit changes; dimensions 1, 3, 4, and 8 | — |
| Kùzu Explorer repository | https://github.com/kuzudb/explorer | official repository | archived 2025-10-10; master read 2026-10-04 | 2026-10-04 | source/license inspection | Browser UI, Vue/Monaco/G6 stack, Docker/Wasm and read modes, MIT license, archive status; dimensions 1, 6, and 8 | Capability documentation is incomplete |
| Kùzu repository | https://github.com/kuzudb/kuzu | official repository | final v0.11.3; archived | 2026-10-04 | source/license inspection | Database lifecycle and MIT license; dimension 8 | Archive status materially affects fit |
| Memgraph Lab product page | https://memgraph.com/lab | official product page | Lab 3.x | 2026-10-04 | official documentation/vendor claim | Graph/query split views, Orb, styling, GraphChat, query collections; dimensions 1, 2, 4, 6–8 | Marketing claims corroborated where possible by docs/releases |
| Memgraph Graph Style Script | https://memgraph.com/docs/memgraph-lab/features/graph-style-script | official documentation | current Lab docs | 2026-10-04 | official documentation | Data-driven node/edge labels, sizes, widths, colors and performance caveat; dimensions 3–5 | — |
| Memgraph release notes | https://memgraph.com/docs/release-notes | official release notes | Lab 3.x; v3.0.0 details reviewed | 2026-10-04 | official release metadata | Expand/collapse, render limits, history, split GraphChat views, feedback; dimensions 2, 5–7 | — |
| Memgraph legal policies | https://memgraph.com/legal | official licensing page | current 2026-10-04 | 2026-10-04 | official license documentation | Separate Lab, Community, Enterprise, OEM and Cloud terms; dimension 8 | Exact Lab/OEM terms need scenario-specific review |
| Memgraph repository | https://github.com/memgraph/memgraph | official repository | repository state read 2026-10-04 | 2026-10-04 | source/repository inspection | Lab positioned as UI to explore/manipulate DB; maturity/ecosystem; dimension 8 | Lab source itself is not established as an embeddable SDK |
| yFiles Graph Editor demo | https://www.yfiles.com/demos/view/grapheditor/index.html | official interactive demo | 3.1-era public demo | 2026-10-05 | official documentation / limited access check | Confirms a public editing demo exists; dimensions 1, 2, and 8 | Not exercised with the common fixture |
| yFiles evaluation signup | https://my.yworks.com/signup?product=YFILES_HTML_EVAL | official evaluation portal | accessed 2026-10-05 | 2026-10-05 | official access/licensing evidence | Local evaluation requires customer-center signup and licensed package download; dimension 8 | No account was created |
| yFiles evaluation setup | https://docs.yworks.com/yfiles-html/dguide/getting_started-ide/ | official documentation | 3.1 | 2026-10-05 | official documentation | Evaluation package contains local tgz and license file; dimension 8 | Explains why no equivalent local common-fixture run was made |
| RPT-0006 common-fixture prototype scan | n/a — observations retained in `report.md` Section 9 and `searches.md` | temporary repository research activity | run 2026-10-05; Cytoscape.js 3.34.0, Sigma.js 3.0.3, Graphology 0.26.0 | 2026-10-05 | reproducible hands-on observation | Cytoscape.js and Sigma.js checks across dimensions 1–8 | Not benchmark evidence; temporary harness, JSON, and generated artifacts removed after material observations were captured |
