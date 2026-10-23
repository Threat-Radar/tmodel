---
schema: "archdoc/v1"
id: RPT-0006
title: "Knowledge Graph Visualization & Review Console"
short_title: "Knowledge graph visualization"
description: "Research report comparing interactive knowledge-graph visualization and editing approaches, and framing candidate development paths for a human-reviewed, AI-assisted tmodel console. Evidence only; no design decision is made here."
type: research
category: knowledge-graph
status: draft
version: "0.2.0"
date: "2026-10-02"
updated: "2026-10-13"
authors:
  - role: student
    id: kriishnaa-18
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0006-knowledge-graph-visualization/report.md
library_commit: "pending; see library/ submodule pointer at time of merge"
informs: [DEC-006, R-014, R-018]
issue: 10
---

# Knowledge Graph Visualization & Review Console

> **Research report — evidence, not a decision.** This report does not select a
> visualization library, application architecture, graph substrate, or interaction
> model, and it does not accept or reopen any `DEC-*`. Findings are bounded by the
> documented sources, prototype scan, and outstanding evidence gaps below.

Research plan: [`dimensions.md`](dimensions.md). Search log:
[`searches.md`](searches.md). Source log: [`sources.md`](sources.md).

## 1. Why this report / scope

This report evaluates knowledge-graph visualization and review approaches for Issue #10. The goal is to identify capabilities and tradeoffs that could support a tmodel review console where a human can explore threat-model relationships, inspect provenance and evidence, follow attack paths, distinguish proposed from accepted state, and review AI-assisted changes. The report compares visualization libraries, graph-analysis applications, and database-oriented graph tools using the same research dimensions and a limited prototype scan. It provides evidence for later design work but does not select a visualization library, application architecture, graph database, or accepted requirement. Related knowledge-graph, application-stack, schema, and implementation issues are outside this report except where existing repository work directly clarifies Issue #10.

The accepted architecture already constrains this comparison. `ADR-0003` accepts
`DEC-006` and prefers open WebGL candidates—Sigma.js, AntV G6, and Cytoscape.js—while
leaving the concrete visualization-library choice open under `APP-0001` A-044.
`APP-0001` also supplies the licensing, scale, layout, and review-state constraints,
including A-044's exclusion of blocking copyleft or per-seat lock-in. Gephi therefore
remains a reference precedent rather than an unrestricted implementation candidate.

The central questions are whether one canonical graph can support task-specific views,
whether the graphical layer needs a presentation model distinct from domain objects, and
how “gravity” or importance can affect layout and attention without silently changing
facts. Here, artificial intelligence (AI), software development kit (SDK), graphics
processing unit (GPU), Web Graphics Library (WebGL), Graph Data Science (GDS), Graph
Style Script (GSS), Structured Threat Information Expression (STIX), and cyber-threat
intelligence (CTI) are defined on first use for the dense comparisons below.

## 2. Comparison table

First-pass comparison from official documentation, repositories, release pages, and
license pages. “Custom” means the capability could be built around the library; it does
not mean tmodel has implemented or validated it. Scale statements are documented claims,
not results of a tmodel prototype. The main table retains the original eight candidates;
Section 2.1 additionally includes the OASIS STIX Visualizer as security-graph prior art.

| Approach | Type / delivery | Interaction & editing | Layout / focus | Threat-path visualization | Performance / scale | Multiple views / presentation model | Human-review support | License | tmodel fit |
|---|---|---|---|---|---|---|---|---|---|
| Cytoscape.js 3.34.0 | Browser graph library | Rich events/model; editing UI is custom | Built-ins + extensions; positions/view state available | Custom styling and traversal can implement it | Canvas; docs warn cost rises with edges, compounds, and rich styles | Library inside a custom multi-view app | Not native; implement in app state | MIT | Broad documented coverage; bounded prototype completed; review UI custom |
| D3 7.9.0 | Modular browser visualization toolkit | Zoom/drag/select primitives; graph editing is custom | Force and hierarchy modules; extensive control, high custom effort | Entirely custom | SVG/Canvas choice is application code; no graph-scale guarantee | Can build any coordinated view; none supplied as a graph app | Not native; entirely application-owned | ISC | Flexible with substantial custom implementation burden |
| Sigma.js 3.0.3 | WebGL browser graph renderer over Graphology | Camera/events; data mutation via Graphology; editor UI custom | Layouts come from Graphology/external code | Reducers can highlight paths without changing graph data | Official scope is thousands of nodes/edges; no tmodel benchmark | Library inside a custom multi-view app | Not native; implement around graph/view state | MIT | Focused renderer; editing, layouts, and review need assembly |
| yFiles for HTML 3.1 | Commercial browser diagramming SDK | Full interactive creation/editing, inspection, undo/redo | Extensive automatic/incremental layouts and graph analysis | Styling, path algorithms, grouping, filtering; threat semantics custom | Performance-oriented SVG/WebGL styles; no verified tmodel limit | SDK supports custom views and persistence; app supplies domain views | Not native; strong primitives for implementing it | Commercial; development and deployment licenses | Very broad documented SDK capability; cost/procurement and hands-on validation still open |
| Neo4j Bloom 2.37 | Neo4j graph-exploration application | Search, inspect, expand, create/connect/update | GPU physics; Perspectives and rule-based emphasis | Can query/style paths; threat-specific workflow not native | GPU-powered claim; 10M-element Perspective scan warning, not display limit | Graph Scene, Card list, Perspectives; Neo4j-bound presentation state | No proposal accept/reject workflow found; edits can hit database | Neo4j terms; Enterprise/plugin key for collaboration features | Useful product precedent; not documented as an embeddable review-console SDK |
| Gephi 0.11.3 | Open-source desktop analysis application | Explore, select, drag, filter, transform; general analyst editing | ForceAtlas2 and other layouts; weights, metrics, filters | Can filter/style paths manually; no threat-path workflow found | Official claim: 100k nodes/1M edges; not tested here | Overview, Data Laboratory, Preview, filters/timeline; workspace state | No AI proposal/review workflow found | CDDL 1.0 or GPLv3 | Useful analysis/prototype reference; desktop application rather than web SDK |
| Kùzu Explorer (archived) | Browser UI for Kùzu, Vue/G6, Docker | Query and visualize; read-write queries can mutate DB | G6-based; detailed layout/focus evidence still incomplete | Query results may show paths; dedicated support unknown | No primary scale evidence found | Query editor + graph results; coordinated review views unknown | No native proposal/review evidence | MIT | Useful local precedent, but both Explorer and Kùzu are archived |
| Memgraph Lab 3.x | Browser graph database workbench | Query, inspect, expand/collapse; direct edits via Cypher | Orb visualization; GSS maps properties to visual weight/style | Query + GSS can emphasize paths; dedicated workflow not found | Render limits configurable; no primary practical size benchmark found | Split-screen graph/query/GraphChat views | GraphChat has feedback, but graph-change acceptance workflow not documented | Separate Lab user license; DB/OEM/Enterprise terms vary | Relevant product/AI precedent; database and license coupling need review |

### 2.1 Issue #37 design-question comparison

The table below separates capabilities that are easy to conflate. “Multiple views” asks
whether views can coordinate over stable objects, not merely whether several panels exist.
“Graphical object model” asks how presentation objects and reserved fields relate to the
domain graph. “Weight / gravity” distinguishes stored meaning from layout mechanics,
visual emphasis, and ranking or filtering.

| Approach | Multiple views over shared data | Graphical object model | Weight / “gravity” mechanisms |
|---|---|---|---|
| Cytoscape.js | One graph instance can be filtered or restyled and coordinated with application-owned tables/details; saved views and cross-view synchronization are custom | Native nodes, edges, compounds, classes, scratch/view state and data-driven style; application must keep canonical semantics separate | Domain scores can map to style; layouts expose algorithm-specific weights/forces; algorithms and selectors can rank/filter; no single gravity concept |
| D3 | Shared application state can drive graph, table, matrix or timeline presentations; D3 supplies primitives, not saved views | DOM/Canvas marks and bound data are fully application-defined; groups, badges, overlays and semantics are custom | Force link strength/distance and many-body forces affect layout; scales affect prominence; ranking/filtering is application code |
| Sigma.js + Graphology | Graphology can be shared with Sigma and other application views; subgraphs/filters and persistence require surrounding code | Graphology stores arbitrary attributes; Sigma reducers and render programs supply visual state. Sigma’s reserved visual `type` collided with the fixture’s semantic `type`, requiring `domainType` plus visual `type` | Graphology metrics include weighted degree and centralities; ForceAtlas2 supplies layout forces; reducers map scores to size/color or hide elements |
| yFiles for HTML | SDK primitives support filtering, alternate components and persistence, but tmodel would define coordinated task views and ownership | Rich graph, group, port, label, style, tag and overlay concepts; domain-to-presentation mapping remains application design | Layouts and graph algorithms accept tool-specific weights/constraints; styles can expose importance; filtering/folding controls focus |
| Neo4j Bloom | Scenes, Card list and Perspectives are saved Neo4j-bound views; GDS results can remain Scene-local or be written to database properties | Categories, rules, icons and Scene state form a presentation layer over Neo4j nodes/relationships | GDS scores can drive rule-based node size/edge thickness; search, filters and Perspectives rank or restrict attention; physics settings are product-managed |
| Gephi | Overview, Data Laboratory, Preview, filters and timeline share a workspace; this is analyst state rather than a tmodel view contract | Graph attributes, appearance mappings, filters and workspace/layout state are distinct but stored in Gephi’s project model | Edge weights and centrality metrics can drive layouts, ranking and size/color; ForceAtlas2 gravity is a layout parameter, not semantic importance |
| Kùzu Explorer | Query editor and graph results share database results; saved/coordinated review views were not established | G6-backed rendering is documented at stack level, but Explorer’s exposed style/group/view model is insufficiently documented | Cypher can calculate/filter scores; primary evidence did not establish user-facing layout weights or gravity controls |
| Memgraph Lab | Query, graph and GraphChat can share a split workspace; durable saved-view semantics remain product-specific | GSS maps database properties to labels, sizes, widths, colors and images; graph facts remain in Memgraph unless Cypher mutates them | Stored scores can map to GSS prominence; Cypher ranks/filters; Orb layout mechanics are not documented as a semantic weighting model |
| OASIS STIX Visualizer | Graph, legend, selected/linked-object details and optional timeline operate over one loaded STIX bundle | STIX Domain Objects become nodes and STIX Relationship Objects become edges; the viewer adds layout, selection, legend and timeline state | Type toggles and the timeline filter attention; no semantic importance or review weighting model is documented |

**Multiple views.** The same canonical tmodel graph can feasibly support graph, table,
matrix, timeline, detail and diff views if each view uses stable domain identifiers and
view actions are classified as presentation-only or domain-changing. Libraries enable
this architecture but do not supply it; Bloom, Gephi, Memgraph Lab and the STIX viewer
are useful product precedents whose saved state is coupled to their own data/workspace
models. Filtering a view, deriving a subgraph and saving a view must remain distinct.

**Graphical object model.** The evidence strongly supports separating presentation state
from canonical domain data. Presentation state may contain positions, viewport, visual
node/edge type, groups, labels, badges, overlays, selection, filters and review emphasis
while referencing canonical objects by stable ID.
The Sigma prototype is the clearest failure case: passing semantic `type: "asset"`
directly into the renderer selected a nonexistent render program. An adapter preserving
`domainType: "asset"` while assigning visual `type: "circle"` fixed the integration
without changing domain facts. Other tools use different reserved fields and abstractions,
so the boundary must be explicit rather than inferred from a library schema.

**Weighting / gravity.** “Gravity” is not one portable feature. Tmodel can store a named,
evidenced semantic score; derive centrality or risk rankings; map either to visual size,
width, opacity, labels or filtering; and pass a deliberately chosen derivative into a
layout algorithm. Node mass, repulsion, edge strength, desired length and central gravity
are algorithm-specific presentation inputs and must not be written back as semantic
importance. The feasible cross-tool contract is therefore named domain measures plus
separate view/layout mappings, not a universal `gravity` property.

## 3. Per-approach / tool sections

The eight original candidates below are the set named or implied by Issue #10. Version
0.2.0 additionally adds the OASIS STIX Visualizer as relevant security-graph prior art,
not as a general implementation candidate. Fit statements synthesize documented
capability and, for Cytoscape.js and Sigma.js, the bounded hands-on scan. They are
assessments for later review, not recommendations.

### Cytoscape.js

**What it is**

Cytoscape.js 3.34.0 is an MIT-licensed JavaScript library with its own graph model,
Canvas renderer, styling system, graph algorithms, layouts, viewport, and event APIs.

**Relevant capabilities**

Official docs cover directed and undirected graphs, loops, multigraphs, compound nodes,
element add/remove/data operations, selection, pan/zoom/drag events, traversal, rich
data-driven node/edge styling, and built-in layouts. Extensions add hierarchical and
compound-aware layouts. Path algorithms and selector-based styling provide primitives for
threat-path emphasis. View positions and temporary visual state can be kept separate from
domain attributes by application code.

**Limitations / gaps**

It is a library, not a review application: forms, tables, timelines, proposal diffs,
accept/reject state, provenance panels, accessibility review, and persistence must be
built around it. The performance guide explicitly says rich styles, compounds, edges,
pixel ratio, and large canvases add cost. The prototype scan below is only a modest
sanity check, not a tmodel benchmark.

**Issue #10 fit**

Documented graph interaction and styling cover much of dimensions 1–5. The prototype
observed core interaction, styling, path emphasis, filtering, and separation of presentation
state from the domain fixture at modest scale. Multiple coordinated views and AI/human
review remain application-level work. Accessibility, production-scale performance, stable
incremental layout, and a complete review workflow remain unverified.

**Hands-on qualification (2026-10-05)**

The common fixture rendered in headless Chrome. Automated pointer/wheel checks exercised
selection and evidence inspection, node dragging, zoom and pan. Programmatic add/remove,
CoSE and breadth-first layouts, type/review styling, primary-path highlighting with the
alternate branch retained, and hiding two proposed nodes all completed. Positions,
viewport, selection, highlights and filters stayed outside the immutable fixture. A
single 300-node/600-edge synthetic run rendered and remained script-responsive; this is
not benchmark evidence. No complete editing or accept/reject UI was tested.

### D3.js

**What it is**

D3 7.9.0 is an ISC-licensed collection of JavaScript modules for binding data to the DOM
and building custom visualizations. It is not a graph application or graph-specific SDK.

**Relevant capabilities**

Official modules provide selections, transitions, drag and zoom behaviors, force
simulation, and hierarchy layouts. A developer can render through SVG or Canvas and can
coordinate graph, table, matrix, timeline, and detail views over shared application state.
Its low-level model gives application code control over visual encodings, focus behavior, and
threat-path presentation.

**Limitations / gaps**

D3 does not supply a graph data model, graph editor, compound-node semantics, inspector,
undo/redo, review workflow, or ready-made large-graph strategy. Those are application
work. The force module describes simulation mechanics but does not establish a practical
scale target for tmodel.

**Issue #10 fit**

D3 is an option when bespoke coordinated views are the priority and the team accepts a
substantial implementation burden. AI proposals and human review would be entirely tmodel
application behavior. A prototype would need to test whether that control justifies the
amount of custom graph interaction and performance engineering.

### Sigma.js

**What it is**

Sigma.js 3.0.3 is an MIT-licensed WebGL graph renderer for the browser, built on the
Graphology data model. Sigma v4 exists only as an alpha and is not assessed as stable here.

**Relevant capabilities**

Official docs describe camera interaction, mouse/touch events, node dragging, node/edge
rendering, custom render programs and layers, and automatic updates from Graphology
events. Node and edge reducers can highlight focus or path context without changing the
underlying graph. The project describes its target as graphs with thousands of nodes and
edges; Graphology supplies algorithms and ForceAtlas2 rather than Sigma itself.

**Limitations / gaps**

Editing controls, group/compound presentation, layouts, filtering UI, inspectors,
coordinated views, persistence, and review state require surrounding code or packages.
Edge interaction may carry extra GPU cost and is disabled by default in the v4 alpha.
No tmodel benchmark or stable-v4 migration assessment has been performed. Sigma also
reserves the node attribute `type` for render-program selection, so a domain model using
`type` needs an explicit adapter or non-conflicting presentation attribute.

**Issue #10 fit**

Sigma is a focused rendering candidate where WebGL scale and a clean domain/view split are
valuable. Threat-path styling is implementable with reducers. AI/human review and multiple
views are outside the renderer and would belong to tmodel.

**Hands-on qualification (2026-10-05)**

The first Sigma page load failed with `Sigma: could not find a suitable program for node
type "asset"!` because the fixture's semantic `type` was passed directly to Sigma's visual
program selector. A minimal adapter copied it to `domainType` and assigned visual type
`circle`; fixture semantics and pinned versions were unchanged. The final run then rendered
the common fixture with no console or page errors. Selection/evidence inspection, dragging,
camera navigation, Graphology add/remove, ForceAtlas2 and a simple layered layout, reducers
for review/path/filter state, and the 300-node/600-edge sanity check completed. The domain
fixture remained unchanged. Editing UI and accept/reject workflow remained application code.

### yFiles for HTML

**What it is**

yFiles for HTML 3.1 is a commercial JavaScript/TypeScript SDK for building browser-based
graph and diagram applications.

**Relevant capabilities**

The official guide covers directed/undirected edges, loops, parallel edges, ports, labels,
groups, create/connect/delete/edit interactions, selection, focus, tooltips, keyboard and
touch input, clipboard, undo/redo, persistence, and SVG/WebGL styles. Its layout set
includes hierarchical, organic/force-directed, orthogonal, tree, circular, radial,
series-parallel, grouped and incremental arrangements. Graph analysis, filtering, path
algorithms, rule-based styling, and custom application views provide strong primitives for
threat-path and focus/context work.

**Limitations / gaps**

It remains an SDK: tmodel must define domain/presentation state, coordinated non-graph
views, and the AI proposal/review protocol. Production requires commercial development
and distribution licensing; pricing and redistribution terms need procurement review.
No tmodel prototype or independent scale measurement has been run.

**Issue #10 fit**

The documented SDK provides a very broad editing/layout foundation in this pass. Human
review is implementable rather than a named product feature. Commercial constraints and
whether its breadth reduces enough custom work must be validated.

### Neo4j Bloom

**What it is**

Neo4j Bloom 2.37 is a Neo4j-backed graph exploration application with a GPU-powered Scene,
search, Perspectives, inspection, and direct data editing.

**Relevant capabilities**

Official docs show search, expand/explore, node and relationship inspection, creation,
connection and property updates, saved Scenes, category/relationship filtering, icons,
rule-based color/size/thickness, a Card list, and reusable Perspectives. Scene actions can
run Cypher against selected elements. GDS results may remain temporary in a Scene or be
written to database properties, an explicit example of view-only versus domain state.

**Limitations / gaps**

Bloom is coupled to Neo4j and is an application rather than an embeddable visualization
SDK. Basic versus Enterprise access differs for remote databases, persistent/shared
Perspectives and Scenes, authorization, and collaboration. No native AI-proposed graph
diff with accept/reject/edit workflow was found. Its documented 10-million-element note
concerns Perspective scanning, not interactive display capacity.

**Issue #10 fit**

Bloom is a useful precedent for inspection, expansion, styling, saved views, and direct
editing. It is less obviously a component for tmodel's console, and its direct-edit model
does not by itself satisfy proposal/accepted-state separation.

### Gephi

**What it is**

Gephi 0.11.3 is a free desktop application for interactive network exploration, analysis,
layout, filtering, transformation, and publication. Its main source is dual-licensed under
CDDL 1.0 and GPLv3.

**Relevant capabilities**

Official material documents node dragging, neighbor highlighting, filters over attributes
and topology, Data Laboratory tables, Preview, timeline/dynamic graph support, metrics,
weighted styling, and layouts including ForceAtlas2, Fruchterman-Reingold, OpenOrd and
Yifan Hu. The current product page claims up to 100,000 nodes and 1,000,000 edges; that is
recorded as a project claim, not a verified tmodel result.

**Limitations / gaps**

Gephi is an analyst desktop environment, not a web-console library. Threat paths can be
queried, filtered, selected, and styled, but no dedicated threat-chain interaction was
found. No AI proposal acceptance workflow is documented. Embedding or reusing its Java/
OpenGL platform would introduce a different integration model from a browser library.

**Issue #10 fit**

Gephi is useful as a reference and prototype environment for layout, filtering, weights,
large-network exploration, and graph/table/timeline separation. As a desktop application,
it would require a different integration approach from a browser-based tmodel console.

### Kùzu Explorer

**What it is**

Kùzu Explorer is an MIT-licensed, Docker-delivered browser UI for the Kùzu property graph
database, built with Vue, Monaco, and G6. The Explorer repository was archived on
2025-10-10; the Kùzu database repository is also archived, with final release 0.11.3.

**Relevant capabilities**

The official repository documents local read-write and read-only database modes, Cypher
querying, graph-result visualization, bundled datasets, Docker deployment, and an in-
browser WebAssembly mode. Its use of a query editor plus graph visualization is relevant
to the console pattern, and G6 implies a capable visualization layer, but G6 features are
not automatically evidence of what Explorer exposes.

**Limitations / gaps**

Primary documentation found in this pass does not establish Explorer's editing gestures,
layouts, focus/weight controls, threat-path workflow, large-graph limits, coordinated
views, or human review model. Archive status is a material maintenance risk. Write queries
mutate database state rather than providing a documented proposal/acceptance layer.

**Issue #10 fit**

Explorer remains useful as a local graph-query UI precedent, but the evidence is too thin
for a strong capability rating and the archived lifecycle weakens direct adoption. Keep it
in the requested comparison; a hands-on archival build check would decide how much more
research is worthwhile.

### Memgraph Lab

**What it is**

Memgraph Lab 3.x is a browser workbench for querying, visualizing, styling, and inspecting
Memgraph property graphs. It uses the Orb visualization library and Memgraph's Graph Style
Script (GSS).

**Relevant capabilities**

Official docs and release notes describe Cypher query results, node expansion/collapse,
custom node/relationship colors, sizes, widths, labels, images and map tiles, saved style
history, configurable automatic-render limits, split-screen layouts, query collections,
and GraphChat. GraphChat translates natural language to Cypher, exposes generated-query
steps/schema references, and lets a user give feedback on responses. GSS can visually
weight properties without establishing tmodel domain semantics.

**Limitations / gaps**

No documented graph-change proposal layer with accept/reject/edit/defer and rollback was
found; GraphChat feedback is not the same workflow. Dedicated threat-path interaction and
practical display limits remain unknown. Lab, DB Community/Enterprise, remote storage,
and OEM embedding have separate terms, so the exact distribution scenario needs license
review. Lab source is not presented as a general embeddable SDK.

**Issue #10 fit**

Lab is a relevant product precedent for graph/query multi-view work and the only candidate
in this pass with documented LLM-assisted querying and feedback. That does not establish
AI-proposed graph editing. Database coupling, licensing, and review-state integration need
further evidence or a hands-on check.

### OASIS STIX Visualizer — security-graph prior art

The OASIS Open CTI project’s browser visualizer loads STIX 2.x JSON from pasted content
or a URL, maps STIX Domain Objects to nodes and STIX Relationship Objects to edges, and
coordinates the graph with a type legend, selected/linked-object details and optional
timeline filtering. It is relevant prior art because it keeps canonical security-object
semantics in the input while adding selection, layout, visibility and time-window state
for inspection.

The visualizer is not evidence for general-purpose editing, saved collaborative views,
semantic importance, proposal verdicts or audit workflow. Its useful lesson for tmodel is
narrower: a security graph can expose type filters, temporal focus and object details over
the same loaded bundle without making those presentation controls domain facts.

## 4. Console requirements

The following are provisional, evidence-backed needs for an Issue #10 review console.
They are candidate requirements for later review, not accepted architecture or product
requirements.

1. **Explore a graph without losing orientation.** A reviewer should be able to zoom,
   pan, select, drag, search, expand/collapse where data can be loaded incrementally, and
   return to a stable context. These operations are common across the documented library
   and product candidates; the prototype exercised the core pointer interactions only.
2. **Inspect an object in context.** Selection should expose the object's type, properties,
   relationships, review state, and stable domain identifier while retaining its graph
   neighborhood. The Cytoscape.js and Sigma.js fixture checks exercised selection and an
   evidence detail panel, but not a production inspector.
3. **Make provenance visible.** Claims and proposed changes should link to evidence,
   source/revision, rationale, confidence where present, and their review history. A graph
   glyph alone is insufficient for this information.
4. **Trace threats and mitigations.** Reviewers should be able to emphasize a directed
   attack path, its alternate branches and mitigations while retaining enough surrounding
   context to detect omissions or misleading isolation.
5. **Filter and focus without silently changing facts.** Type, layer, review-state, path,
   and neighborhood filters should affect presentation state unless the user explicitly
   performs a domain edit. The prototype verified this separation for two libraries.
6. **Keep proposed and accepted state unmistakably distinct.** Proposed, accepted,
   rejected, deferred, and unresolved items should use labels or other redundant cues in
   addition to color. A verdict must be an explicit application action, not a side effect
   of selecting, hiding, or laying out an element.
7. **Remain responsive at an agreed review scale.** Interaction, inspection, filtering,
   and review actions need measurable responsiveness targets, plus progressive loading or
   aggregation when a full graph exceeds them. The 300-node/600-edge runs establish only
   basic feasibility in one environment; they do not set a target or benchmark.
8. **Support accessible review.** Keyboard navigation, visible focus, non-color review
   cues, readable labels/details, and screen-reader alternatives are candidate needs. The
   evidence is incomplete: yFiles documents keyboard support, but this scan did not test
   accessibility across candidates.

## 5. Views and presentation model

No single view covers all Issue #10 review tasks. The evidence supports evaluating a
coordinated set rather than treating the graph as the entire console:

- **Graph view:** best suited to neighborhood exploration, topology, attack paths,
  branches, mitigations, and focus+context. It becomes less effective for dense property
  comparison or long provenance records.
- **Table view:** useful for sortable properties, missing-data checks, review queues, and
  careful comparison or batch selection. Gephi's Data Laboratory and Bloom's Card list
  are product precedents; a tmodel editing model remains unspecified.
- **Matrix view:** potentially useful for dense many-to-many relationships and coverage
  comparisons, but this pass found little candidate-specific evidence. Its necessity and
  synchronization behavior remain open.
- **Timeline, detail, and diff views:** a detail view is needed to show provenance and
  evidence without overloading graph labels. A diff is a logical requirement of reviewing
  proposals against accepted state. Gephi supplies a timeline precedent, but the role of
  time in Issue #10 and the exact diff/timeline interactions were not prototyped.

If multiple views are used, selection, focus, review state, and explicit edits should be
coordinated through stable domain identifiers. A change in one view must distinguish a
domain edit from a presentation-only action in another. The prototype showed that node
positions, camera, selection, path emphasis, and filters can remain separate from an
immutable domain fixture in both Cytoscape.js and Sigma.js; it did not test round trips
among graph, table, matrix, timeline, detail, or diff views.

Saved layouts, views, layers, and filters are useful precedents in Bloom Perspectives and
Scenes, Gephi workspaces, yFiles persistence APIs, and Memgraph Lab split views. Whether
tmodel persists them per user, per model, or as shareable review artifacts is unresolved
and should not be encoded into the domain model without a separate decision.

## 6. Layouts / weighting / focus

Force-directed layouts are useful for exploratory clustering and neighborhood discovery,
but movement can disrupt a reviewer's spatial memory. Hierarchical or layered layouts
better expose direction and sequence in an attack path, although cross-links and alternate
branches can become awkward. The prototype exercised one force-oriented and one layered
layout per library and observed immediate position changes; it did not measure layout
quality, stability, or reviewer comprehension.

Pinning, incremental layout, and preservation of manually adjusted positions are therefore
candidate needs, especially after expansion, filtering, or a model update. yFiles documents
incremental layout support; equivalent production behavior was not validated for the other
candidates. A console may offer more than one layout, but this report does not choose an
algorithm or default.

Importance, risk, confidence, review state, and path membership can drive size, color,
opacity, edge width, badges, or labels. Those visual mappings should reference domain
facts without rewriting them. Layout weights, gravity, camera position, semantic-zoom
rules, selection, and temporary emphasis belong to presentation state unless a separately
reviewed domain concept says otherwise. The prototype mapped importance and review state
to visuals without mutating the fixture.

Focus+context should emphasize a node, neighborhood, or path while dimming or simplifying
rather than automatically deleting surrounding context. Semantic zoom may help label and
detail density, but it was not exercised in this scan.

## 7. Threat-path visualization

A threat-path presentation should make direction and step order legible, distinguish the
primary path from alternate branches, show where mitigations interrupt or reduce the path,
and allow each step to be inspected for provenance, evidence, uncertainty, and review
state. Highlighting should retain surrounding nodes and edges in a subdued form so the
reviewer can see omitted branches and avoid mistaking a focused view for the complete
model.

The common fixture provided evidence that both Cytoscape.js styles/selectors and Sigma.js
attributes/reducers can highlight a seven-edge primary path while leaving a two-edge
alternate branch visible. Evidence metadata was inspectable and proposed nodes were
visually distinct. This establishes visualization feasibility only: it did not validate
path computation, bottleneck analysis, multiple-path comparison, progressive expansion,
uncertainty encoding, or mitigation effectiveness semantics.

Computed, manually curated, and AI-proposed paths should be labelled as such. Presentation
should not imply causality, confidence, or acceptance merely because an edge is prominent.
Any synchronized detail or diff view should use stable identifiers for the same path
elements.

## 8. AI proposals + human review

None of the researched candidates provides the whole AI-proposal and human-review workflow
natively. Visualization libraries provide rendering, events, and mutable graph primitives;
products provide forms, queries, or direct database editing. The following provisional
workflow would be application behavior around the visualization layer:

1. Store an AI output as a **proposal** against a known accepted revision. Keep it separate
   from accepted state and attach provenance, evidence, rationale, confidence, model/run
   identity, and any validation results.
2. Let a reviewer **inspect** the affected nodes, edges, path context, evidence, and a
   before/after diff before recording a verdict.
3. Support explicit **accept**, **reject**, **edit**, **defer**, and **comment** actions.
   Editing a proposal should preserve the original suggestion and attribution.
4. Permit **batch review** only where dependencies, conflicts, shared evidence, and partial
   failure are visible; a batch action must not hide individual outcomes.
5. Apply accepted changes through application/domain validation rather than directly from
   a graph gesture. Rejection or hiding should not delete accepted facts.
6. Record an **audit trail** with actor, time, input revision, rationale/comment, and
   before/after state. Undo or rollback should be an explicit, auditable domain operation,
   not merely a renderer-level undo stack.

The prototype confirmed only that proposed and accepted items can be styled, selected,
filtered, and inspected differently. It did not implement verdicts, conflicts, validation,
audit history, undo/rollback, or concurrent review. Bloom and Memgraph demonstrate direct
graph editing and AI-assisted querying respectively, but neither is evidence of this
proposal/acceptance model.

## 9. Prototype / hands-on findings

The bounded scan used a temporary common fixture: 11 nodes (three assets/components, four
threats, two vulnerabilities and two mitigations) and 11 directed edges. It includes a
seven-edge primary attack path, a two-edge alternate branch, evidence metadata, and two
proposed items. It is a research fixture, not a proposed schema. The run used Node
24.19.0 and Headless Chrome 154 at 1280×800 with SwiftShader; candidate and dependency
versions were Cytoscape.js 3.34.0, Sigma.js 3.0.3, and Graphology 0.26.0. The temporary
harness and generated artifacts were removed after the material observations were recorded
in this report and the search log.

| check | Cytoscape.js 3.34.0 | Sigma.js 3.0.3 |
|---|---|---|
| render, zoom/pan, select, drag, inspect | completed; evidence node inspected and drag/viewport events observed | completed after the adapter fix; no final console/page errors |
| mutation | Graph model add/remove completed; no editor UI tested | Graphology add/remove completed; no editor UI tested |
| layouts | CoSE and breadth-first completed and changed positions | ForceAtlas2 and a small fixture-specific layered layout completed and changed positions |
| styling and path | type/importance/review styles; primary highlighted and alternate retained | equivalent styling through attributes and reducers |
| filter/focus | two proposed nodes hidden in view; fixture unchanged | two proposed nodes hidden by reducer; fixture unchanged |
| presentation/domain split | positions, viewport, selection, highlight and filter held outside fixture | same; required mapping semantic `type` to presentation `domainType` |
| modest scale sanity | 300 nodes/600 edges rendered and remained script-responsive | 300 nodes/600 edges rendered and remained script-responsive |
| review feasibility | proposed items were visually distinct and selectable; no native verdict workflow | same; surrounding application code would own verdicts |

The scale runs were single local executions with different rendering pipelines and are
not comparable benchmarks; their elapsed script timings must not be used to rank the
candidates. Accessibility, keyboard review, incremental/live loading,
compound/group behavior, persistence, coordinated non-graph views, undo/redo, and a real
accept/reject/edit/defer workflow remain unverified.

The Cytoscape final run logged one HTTP 404 for an unspecified page resource (consistent
with the harness having no favicon); it did not prevent any check. Sigma's earlier exact
runtime error was resolved by the minimal adapter and did not recur. This was an
integration finding, not evidence that Sigma itself is unsuitable.

**yFiles boundary.** Public official demos are accessible, but the local evaluation
package and license require customer-center signup/download. It was not exercised with
the common fixture and remains documentation-only.

## 10. Candidate development paths

These paths are options for later evaluation, not a ranking or architecture decision.

| candidate path | likely strengths | tradeoffs and implementation burden | licensing implications | remaining validation |
|---|---|---|---|---|
| Graph-focused open-source library (Cytoscape.js or Sigma.js/Graphology family) | Purpose-built graph interaction and styling; both supported the common fixture and presentation/domain separation | tmodel must build inspectors, editing semantics, coordinated views, accessibility, persistence, and the complete review workflow; Sigma needs explicit domain-to-renderer adapters and external layout pieces | MIT for the assessed versions; dependencies and redistribution still need routine review | Accessible keyboard workflow, production editing, layout stability, live/progressive loading, multi-view synchronization, and representative-scale testing |
| Low-level custom visualization (D3) | Fine-grained control over graph, table, matrix, timeline, diff, bespoke encodings, and shared state | Substantial interaction, graph-model, editing, performance, and maintenance burden; few complete graph-console behaviors arrive ready-made | ISC for D3; application and auxiliary dependency terms remain tmodel's responsibility | A smallest-fair prototype should test whether custom coordinated views justify the added engineering and accessibility burden |
| Commercial SDK (yFiles for HTML) | Very broad documented editing, layout, analysis, styling, accessibility-related, and persistence primitives may reduce custom graph work | Still requires tmodel domain/presentation boundaries and review workflow; procurement, package access, deployment, and vendor dependency add constraints | Commercial development and deployment terms require scenario-specific legal/procurement review | Common-fixture hands-on evaluation, price/distribution fit, accessible review behavior, and comparison of implementation effort |
| Product/reference-only (Bloom, Gephi, Kùzu Explorer, Memgraph Lab) | Concrete precedents for exploration, graph/table or query split views, saved perspectives, filtering, styling, and analyst workflows | These are not interchangeable embedded SDKs: Bloom/Memgraph are database-coupled, Gephi is desktop-oriented, and Kùzu tooling is archived | Product, database, OEM, desktop, and open-source terms differ; reuse cannot be inferred from UI precedent | Validate which interaction patterns users value; clarify licenses only if embedding/integration is proposed; do not treat product features as library APIs |

## 11. Adversarial completeness review

The completeness pass compared the fixed set with independent current tool families and
challenged claims that could be mistaken for verified behavior. The OASIS STIX Visualizer
was identified as useful security-graph prior art and was added to the comparison. The
pass did not find evidence that another candidate would overturn the development paths
above.

| Considered approach | Why it matters | Disposition |
|---|---|---|
| React Flow | Strong node-editor interaction, subflows, save/restore examples and documented keyboard/screen-reader support | Record as a serious follow-up for an editing-first React console. Not added to the fixed comparison because its value is UI/editor composition, not graph analytics or an existing review workflow. |
| vis-network | Mature browser network renderer with clustering, node mass/value scaling and explicit physics “gravity” controls | Coverage evidence for why gravity must be decomposed. Not added because it does not materially change the library-versus-application conclusion. |
| Graphology ecosystem | Supplies Sigma’s graph model, subgraph operators, weighted metrics, centralities, layouts and paths | Incorporated into the Sigma assessment rather than treated as a separate renderer candidate. |
| AntV G6 | Broad graph SDK with combos, states, layouts and configurable force parameters | One of ADR-0003's preferred open WebGL candidates alongside Sigma.js and Cytoscape.js. Retained for the open A-044 library choice rather than added to this fixed comparison; its evidence does not change the current architectural findings. |
| Ogma / Linkurious | Commercial WebGL SDK and investigation product with rich styling, layouts and an accessibility example | Commercial comparator worth procurement-led follow-up. Not added because no common-fixture or licensing comparison was performed and the current report already has commercial SDK and product precedents. |
| OASIS STIX Visualizer | Direct security-object graph, legend, details and timeline over STIX 2.x | Added as relevant security-graph prior art; not presented as a general editor or review-console SDK. |

The pass found no basis for upgrading vendor scale claims into benchmarks. Gephi’s
100,000-node/1,000,000-edge statement remains a project claim; Bloom’s 10-million-element
note remains a Perspective scan warning, not display capacity; Sigma’s “thousands” remains
project scope. The 300-node/600-edge checks remain single-run responsiveness observations.

Review and accessibility claims are also deliberately narrow. Direct database editing,
GraphChat feedback, renderer selection events and undo stacks do not constitute a human
proposal-verdict workflow. React Flow documents keyboard and screen-reader primitives;
yFiles documents keyboard input; Ogma publishes an accessibility example. None of that
establishes an accessible tmodel console without end-to-end testing. Commercial SDKs and
database products are compared as capability precedents, not scored as if they had the
same delivery model as open-source rendering libraries.

## 12. Gap analysis and routing

These gaps are evidence inputs for existing requirements and implementation issues.
`DEC-006` remains accepted through `ADR-0003`; routing a finding does not reopen it or
create an architecture requirement.

| Finding / gap | Evidence | Implication for tmodel | Routed constraint / requirement / issue |
|---|---|---|---|
| Multiple views need a shared identity and state contract | Libraries permit coordinated application views; Bloom Scenes/Perspectives, Gephi workspaces, Memgraph split views and the STIX viewer are product-specific precedents | Define how graph, table, matrix, timeline, detail and diff views share selection and edits while keeping per-user/session state separate | APP-0001 A-009–A-011, A-025; R-014; Issue #59 (T-202–T-204) |
| Presentation objects must not overwrite domain semantics | Cytoscape/Sigma prototype kept positions and filters outside the fixture; Sigma semantic `type` collided with visual `type` | Define an adapter/presentation model for visual type, position, viewport, grouping, labels, overlays, badges and saved-view metadata keyed by stable domain IDs | ADR-0003 visualization-adapter boundary; APP-0001 A-025; R-014; Issue #59 (T-204) |
| “Gravity” has four distinct meanings | D3/ForceAtlas-style forces, Graphology metrics, Gephi weights, Bloom GDS styling and GSS mappings affect different layers | Name semantic measures explicitly and keep layout force, visual prominence and ranking/filtering as derived mappings | APP-0001 A-020, A-024, A-026; R-014; Issue #59 (T-204) |
| No candidate supplies AI proposal review end to end | Libraries expose events/mutation; Bloom edits DB state; GraphChat feedback is not graph-change acceptance | Specify proposed-versus-accepted state, diff, verdicts, evidence, validation, audit and rollback outside the renderer | APP-0001 A-007, A-045; R-018; Issue #59 (T-202–T-204) |
| Accessibility evidence is incomplete | Only partial official primitives/examples were found; no candidate passed an end-to-end tmodel accessibility test | Require keyboard, focus, non-color state, screen-reader alternative and reduced-motion validation in any prototype | Issue #59 (T-204 validation) |
| Performance evidence does not establish a target | Vendor/project claims are not comparable; local 300/600 runs are not benchmarks | Establish representative graph shapes and measurable interaction, layout and loading budgets before selection | APP-0001 A-023, A-027, A-041; Issue #59 (T-204) |
| Commercial and product precedents have integration boundaries | yFiles/Ogma require commercial review; Bloom/Memgraph are database-coupled; Gephi is desktop; Kùzu is archived | Evaluate delivery, procurement, embedding and maintenance separately from feature breadth | ADR-0003; APP-0001 A-044; Issue #59 (T-204) |
| Matrix, timeline and diff behavior remain weakly tested | STIX and Gephi provide timeline precedents; no common fixture exercised coordinated non-graph views | Prototype only if these views are required by concrete review tasks; do not infer synchronization from panel availability | APP-0001 A-009, A-010, A-025; R-014; Issue #59 (T-202–T-204) |
| Library provenance is incomplete | Source records are prepared in library PR #23 but are not yet on library `main` | Merge library PR #23 before citing a durable `library@<commit>` | Issue #37 library/FX-1 workflow; library PR #23 |

## 13. Outstanding evidence gaps

- Accessibility has not been tested end to end.
- Coordinated graph, table, matrix, timeline, detail, and diff views have not been prototyped together.
- The 300-node/600-edge runs are sanity checks, not performance benchmarks.
- D3, Neo4j Bloom, Gephi, Kùzu Explorer, and Memgraph Lab were not run against the
  common fixture; yFiles remains documentation-only because a local evaluation package
  was not used.
- The RPT-0006 research prototype did not validate live updates, incremental loading,
  compound/group behavior, collaboration, undo/redo, or concurrent review; this is a
  research-evidence boundary, not a claim about later implementation work.
- Kùzu Explorer interaction evidence and Memgraph Lab practical graph-size evidence remain limited.
- Commercial licensing and deployment terms require scenario-specific review if those candidates advance.
- Standalone library ingestion remains separate from this report and awaits library PR #23.

## 14. Conclusion

The evidence supports a console built around one canonical graph with several coordinated
task views, but it does not select a toolkit or storage architecture. Graph libraries such
as Cytoscape.js and Sigma/Graphology provide strong rendering and analysis primitives;
D3 offers maximum presentation freedom at higher implementation cost; yFiles offers broad
commercial SDK capability; and Bloom, Gephi, Kùzu Explorer, Memgraph Lab and the OASIS
STIX Visualizer are useful workflow precedents rather than interchangeable components.

Three conclusions answer Issue #37 directly. First, multiple graph, table, matrix,
timeline, detail and diff views are feasible when they share stable domain identifiers
and explicitly separate view actions from domain edits. Second, the graphical layer needs
its own presentation model; the Sigma `type` collision demonstrates the cost of passing
domain fields directly into a renderer. Third, “gravity” must be decomposed into semantic
importance, layout force, visual prominence, and ranking/filtering. Tmodel can support all
four through named measures and derived mappings, but no candidate provides a portable,
semantically safe gravity feature.

The decisive remaining work is not another broad tool survey. It is validation against
representative review tasks: coordinated views, accessible proposal diffs and verdicts,
stable layout under change, and measurable performance at an agreed graph size. Those
questions are routed to the applicable `APP-0001` requirements, R-014/R-018, and Issue
#59 (T-202–T-204). `DEC-006` remains accepted through `ADR-0003`; this report neither
reopens it nor makes a new architecture decision.
