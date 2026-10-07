---
schema: "archdoc/v1"
id: DL-0014
title: "Object-model draft view — mermaid graph + per-object schema tables"
type: process
status: draft
version: "0.1.0"
date: "2026-10-07"
updated: "2026-10-07"
record: DL-0014
---

# DL-0014 — incrementable object-model draft view

## Question asked

"Create a draft that we can increment of all current object types, waiting for the full
search is too slow … would like a mermaid graph of objects with relations and schema
definitions." A browsable snapshot of the object model *now*, that regrows as the schema
is filled out — not a wait on the 3-stage #104 schema work.

## What was produced

- **`spec/schema/render_object_model.py`** — a deterministic, stdlib+PyYAML renderer (no
  network, no Node). It reads `spec/schema/tmodel-object-model.linkml.yaml` and emits the
  draft. "Incrementable" = regenerate after any schema edit; the LinkML stays the single
  source of truth, this is a derived view.
- **`spec/schema/OBJECT-MODEL.md`** — generated. A mermaid `classDiagram` of all 22 object
  types (class→class slots as labelled relation edges, multivalued marked `*`, non-`Node`
  inheritance drawn), then per-object schema tables (slot · type · required · multivalued ·
  note), then the 9 enums with their permissible values.

## Decisions / rejections

- **Generated, not hand-authored.** Carries the `<!-- GENERATED … -->` header; `bin/validate-archdoc`
  already skips that marker, so the view needs no archdoc front matter and can't drift from
  the schema. Editing the `.md` by hand is wrong — edit the LinkML and rerun.
- **Omit `Node` inheritance edges from the graph.** 20 of 22 classes `is_a Node`; drawing all
  20 `Node <|-- X` edges drowns the relation graph. `Node`'s role is stated in prose and its
  slots still appear in its own table. Only *relation* edges and non-`Node` inheritance are drawn.
- **classDiagram, not flowchart.** Inheritance (`<|--`) and labelled associations (`--> : slot`)
  render natively on GitHub, which is where this is read.
- **Not normative.** Header flags DEC-001 (object model) and DEC-002 (encoding) still open;
  this reflects the current `proposed.11` LinkML draft (22 classes / 62 slots / 9 enums),
  gaps and all (e.g. `DamageScenario` has no own slots — RPT-0015 §4). It is a mirror of the
  draft schema, not a competing object model (CLAUDE.md "no parallel architecture document").

## Next

Regenerate whenever the LinkML changes. As Stage 2 of #104 fills the gap list (RPT-0015 §4),
this view updates for free — a cheap review surface for schema completeness.
