---
schema: "archdoc/v1"
id: RPT-0012-dimensions
title: "RPT-0012 dimensions — GUI, platform & implementation-stack search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: RPT-0012
---

# RPT-0012 — search dimensions (the research plan)

**Goal.** Choose the implementation stack for a **best-in-class, commercial-grade**
tmodel application: macOS first, an interactive graph display whose *quality of display,
graphics and interaction is the point*, large interconnected graphs with progressive
loading, an optional CLI, and a licence that permits a commercial product. The sponsor's
rule: **"language choice to be driven by GUI and platform research"** — so this report
produces the *evidence and a recommendation*, and `DEC-006` (UI) + `DEC-010` (stack) are
taken from it. Requirements input is `APP-0001` (A-020…A-046).

**Method.** Five lanes, one multi-agent pass each (verified URLs only, per PROC). Every
tool/library/standard → a `library/` record (a spec gets FX-1, T-029; a product/library
gets a tool/reference record). The report scores each candidate stack against the
`APP-0001` requirements and returns **one recommended stack (or two finalists) with
evidence**, not a vibe.

## Lane 1 — Graph visualization libraries & rendering engines

The core capability. For each candidate: max nodes/edges at interactive FPS, rendering
tech (SVG / Canvas / **WebGL/GPU**), built-in **physics/layout**, **progressive load /
level-of-detail / clustering**, expand-on-click + inspector support, theming/colour
control, export, **licence & cost**, maintenance health.

Candidates to cover (not a shortlist — the lane must confirm/deny each):
- **Open web/JS:** Cytoscape.js, Sigma.js (WebGL), G6 / AntV, D3-force, vis-network.
- **Commercial web/JS:** ReGraph & KeyLines (Cambridge Intelligence), Ogma (Linkurious),
  yFiles (yWorks) — these are the usual "best-in-class, large-graph, licensed" answers;
  capture pricing model and licence terms (A-044).
- **GPU / very large:** Graphistry, Cosmograph / cosmos (GPU force).
- **Native:** a Swift/Metal custom canvas (build layout ourselves), Qt graph widgets.

Scoring target: **A-041 (~10k nodes/~50k edges interactive)**, A-020 (physics), A-023
(progressive), A-042 (quality), A-044 (licence).

## Lane 2 — Desktop app shell & packaging (macOS first)

How the viz + backend ship as a real macOS app (A-046). For each: Mac-native feel,
rendering performance, binary size, code-signing/notarisation, access to the Lane-1 lib,
and cross-platform optionality (not required, but cheap-if-free is a plus).
- **Tauri** (Rust shell + system webview) — small, native, hosts any web viz lib.
- **Electron** (Chromium) — heaviest, maximal web compatibility.
- **Native SwiftUI / AppKit** — best Mac feel; thin graph-viz ecosystem (pairs with a
  custom Metal canvas, Lane 1).
- **Qt (PySide6 / C++)**, **Flutter desktop** (Skia/Impeller custom canvas),
  **Compose Multiplatform**, **egui/wgpu** (Rust immediate-mode GPU).

## Lane 3 — Language / stack: GUI vs backend, and the boundary

The decision is really *two* languages joined by an API (`APP-0001` A-030).
- **Frontend language is driven by Lane 1 + Lane 2** (TypeScript/web if a web viz lib wins;
  Swift if native; Dart/Rust for Flutter/egui). Do **not** pick it before Lanes 1–2.
- **Backend / KG engine language** — score against `DEC-004` (RDF vs LPG, `T-044`):
  **Python** (rdflib, oxrdflib, networkx, pySHACL, LinkML, RDFLib-SHACL) is strong for the
  KG + ingest and matches the `library/` tooling; **Rust** (oxigraph, petgraph) for a fast
  embeddable store; **JVM** (Jena, Neo4j) if LPG/Neo4j wins.
- **The API boundary** (A-030): embedded (same process) vs local service (HTTP/IPC); what
  keeps the CLI (A-060) free and lets GUI language ≠ backend language.
- **Note — not a constraint on the product:** the `~/cb` harness pins `node` v8 (2018); the
  **tmodel product repo has its own toolchain** and may use current Node/Bun. Record this so
  nobody mis-applies the harness rule to the app.

## Lane 4 — Interaction & UX patterns for large graphs

What "best-in-class" actually looks like, from the tools that do it well. Survey
**Linkurious, Neo4j Bloom, Graphistry, Gephi, Cytoscape (desktop), Maltego, GraphXR** for:
progressive expansion, level-of-detail & clustering, **focus+context ("gravity"/fisheye,
A-026)**, filtering as **composable layers (A-025)**, inspectors, and **comparison/diff
views (A-010/R-035)**. Output: concrete interaction patterns the tmodel console should copy
or beat, mapped to `APP-0001` §3 and ARCH-0001 §10.

## Lane 5 — Commercial-grade: licensing, cost, longevity, skills

The hard filters that kill otherwise-great options.
- **Licence compatibility** with a commercial product (A-044) — per Lane-1/2 dependency;
  flag copyleft, per-seat, or source-available-non-commercial terms.
- **Cost** of the commercial viz libs (ReGraph/KeyLines/Ogma/yFiles) — model and ballpark.
- **Longevity & health** — release cadence, maintainer, community size, security posture.
- **Team fit** — can four CS seniors be productive in it this semester (hiring/skill proxy).

## Deliverable & scoring

A comparison matrix of **candidate stacks** (a Lane-1 viz × Lane-2 shell × Lane-3 backend
triple) scored against `APP-0001` A-020…A-046, plus a **recommendation (one stack, or two
finalists to spike in `prototype/`)** with evidence. The report **informs DEC-006 and
DEC-010**; it does not accept them (an ADR does). Gap analysis notes anything the MVP
(ADR-0002) does not need yet.
