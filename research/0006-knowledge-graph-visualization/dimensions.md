---
schema: "archdoc/v1"
id: RPT-0006-dimensions
title: "RPT-0006 dimensions — the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-05"
record: RPT-0006
---

# RPT-0006 — search dimensions

This is the research rubric for Issue #10. Apply the same questions to each candidate
where they are relevant, distinguish documented capability from hands-on verification,
and log evidence in `sources.md`. These axes organize research; they are not accepted
requirements or architecture decisions.

## 1. Visualization and editing

- Which graph types, node and edge forms, groups, compound nodes, annotations, and graph
  mutations are supported?
- Can users create, edit, delete, reconnect, merge, split, and annotate graph elements?
- Is the approach a rendering library, editing toolkit, complete application, or
  database-specific viewer? Which capabilities require extensions or custom code?

## 2. Interaction and inspection

- How well are zoom, pan, select, multi-select, drag, inspect, expand/collapse,
  neighborhood traversal, search, keyboard use, and context actions supported?
- Can a reviewer reveal provenance and details without losing graph context?
- Where relevant, are accessibility, interaction history, and undo/redo supported?

## 3. Layouts, weighting, and focus

- Which force-directed, hierarchical, constrained, incremental, deterministic, and
  custom layouts are available?
- Can users pin nodes, constrain regions, and keep layouts stable as nodes arrive or the
  view changes?
- Can node and edge weights influence layout, gravity, salience, focus+context, or
  semantic zoom without conflating importance, confidence, risk, and reviewer attention?
- Does changing a visual weight affect domain data, view state, or neither?

## 4. Styling and threat-path visualization

- Can shapes, sizes, colors, icons, labels, badges, lines, arrows, and state be mapped
  from data without conflating presentation with domain facts?
- How are parallel edges, self-loops, direction, uncertainty, provenance, review state,
  and dense labels made legible?
- Can attack paths or threat chains be isolated, highlighted, compared, stepped through,
  and explained while preserving surrounding context?
- Can branches, alternate paths, mitigations, bottlenecks, prerequisites, and unresolved
  evidence be shown without implying unsupported causality or ordering?

## 5. Performance and large graphs

- What practical evidence exists for graph sizes, update rates, time to first useful
  view, memory use, and interaction latency? What was measured versus vendor-claimed?
- Where relevant, how do Canvas, SVG, WebGL/WebGPU, virtualization, level of detail,
  clustering, sampling, server-side queries, and progressive loading affect behavior?
- How responsive are filtering, selection, layout changes, progressive expansion, and
  live updates?

## 6. Views and presentation model

- How do graph, table, matrix, timeline, detail, diff, and summary views support distinct
  review tasks? Do selections and edits stay synchronized across views?
- Which presentation state exists beyond domain nodes and edges: layouts, viewports,
  groups, layers, visual encodings, annotations, selections, and saved views?
- What belongs in durable shared state versus per-user or session state? Can views,
  layouts, filters, and layers be saved and linked to stable domain identifiers?
- Can presentation changes round-trip without polluting or silently rewriting the domain
  model?

## 7. AI proposals and human review

- Can AI-proposed changes remain distinct from accepted state and appear as inspectable
  diffs rather than directly mutating the accepted graph?
- Can a human accept, reject, edit, defer, comment on, or batch-review nodes, edges,
  attributes, paths, and deletions?
- Are evidence, rationale, confidence, validation results, identity, timestamps, audit
  history, undo, and rollback available for proposals and verdicts?

## 8. Fit for tmodel

- Which Issue #10 review tasks does the approach directly support, partially support, or
  not support, and what evidence backs that rating?
- What integration and development complexity follows from its languages, frameworks,
  APIs, data adapters, runtime assumptions, and extension points?
- What licensing or commercial constraints apply, including copyleft, attribution,
  redistribution, seat, deployment, data-volume, evaluation, and procurement terms?
- What do maturity, documentation, release activity, maintainership, ecosystem, and support
  indicate?
- What needs hands-on validation, and what is the smallest fair prototype for threat
  models, attack paths, bibliography/KG material, provenance, and human review?

## Cross-cutting evidence rubric

For every material claim, record the evidence type: official documentation, source or
license inspection, hands-on observation, benchmark, vendor claim, secondary analysis,
or researcher inference. Record versions and dates where relevant, mark unknowns clearly,
and log rejected approaches with reasons.
