---
schema: "archdoc/v1"
id: RPT-0012
title: "GUI, platform & implementation stack"
short_title: "GUI / platform / stack"
description: "Evidence toward the implementation stack for a commercial-grade, macOS-first tmodel application with a best-in-class interactive graph display. Scores candidate stacks against APP-0001; informs DEC-006 (UI) and DEC-010 (stack/language). Evidence, not decisions."
type: research
category: application
status: draft
version: "0.2.0"
date: "2026-10-01"
updated: "2026-10-01"
authors:
  - role: sponsor
    id: nymble
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0012-gui-platform-stack/report.md
defers_to: ARCH-0001
agent_notes: >
  Skeleton. The plan is in dimensions.md (five lanes). Sections below are `pending`
  until the multi-agent passes run. Requirements input is APP-0001; outputs inform
  DEC-006 and DEC-010. Every tool cited gets a library/ record.
---

# RPT-0012 — GUI, platform & implementation stack

**Evidence, not a decision.** This report chooses nothing; it scores candidate stacks
against `APP-0001` so the sponsor can take `DEC-006` (UI) and `DEC-010` (stack/language).
The search plan is `dimensions.md`. Requirements: `APP-0001` A-020…A-046.

## 0. Summary & recommendation

**Direction decided by the sponsor (2026-10-01): Path A** — a local-only, macOS-first
desktop app, **Tauri (Rust) shell + TypeScript/WebGL frontend over a Python KG engine**,
with a shared CLI and local IPC. Accepted in **`ADR-0003`** (DEC-006 + DEC-010). The
decision was taken from the landscape below without running every lane to exhaustion.

**Residual research (still live against the fixed shell/engine):**
- **Lane 1 / A-044** — the WebGL **viz-library** comparison (open: Sigma.js / G6 /
  Cytoscape.js; commercial only if open fails the quality/scale bar): the one sub-choice
  Path A deliberately left open.
- **Lane 3 / DEC-004** — the KG substrate (RDF vs LPG) behind the Python façade; informed
  by the iteration-5 reification analysis (#15).
- Lanes 4–5 (interaction patterns, licensing/longevity) inform the slice work (I-App) but
  no longer gate the stack direction.

## 1. Graph visualization libraries & rendering (Lane 1)

_pending — Cytoscape.js, Sigma.js, G6, D3; ReGraph/KeyLines, Ogma, yFiles; Graphistry;
native Metal / Qt. Scale, physics, progressive/LOD, licence._

## 2. Desktop shell & packaging, macOS-first (Lane 2)

_pending — Tauri, Electron, SwiftUI/AppKit, Qt, Flutter, Compose, egui/wgpu._

## 3. Language / stack & the API boundary (Lane 3)

_pending — GUI language follows §1–§2; backend (Python / Rust / JVM) follows DEC-004;
the A-030 boundary; the "harness node-v8 is not a product constraint" note._

## 4. Interaction patterns for large graphs (Lane 4)

_pending — Linkurious, Neo4j Bloom, Graphistry, Gephi, Cytoscape, Maltego, GraphXR →
progressive load, LOD/clustering, focus+context, layers, compare._

## 5. Commercial-grade: licensing, cost, longevity, skills (Lane 5)

_pending — licence compatibility (A-044), cost of commercial libs, health, team fit._

## 6. Comparison matrix & gap analysis

_pending — candidate stacks × APP-0001 requirements; what the MVP does not need yet._
