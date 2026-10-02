---
schema: "archdoc/v1"
id: ADR-0003
title: "Path A — local desktop app: Tauri/TypeScript + Python KG engine"
short_title: "Path A — local app stack"
description: "Accepts DEC-006 (UI stack / interaction path) and DEC-010 (language & packaging): a local-only, macOS-first desktop application — a Tauri (Rust) shell hosting a TypeScript/WebGL frontend over a Python knowledge-graph engine, with a CLI on the same engine. Direction decided; viz-library (A-044) and KG substrate (DEC-004) remain open behind adapters."
type: decision
category: application
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-01"
updated: "2026-10-01"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0003-path-a-local-app.md
accepts:
  - DEC-006
  - DEC-010
defers_to: ARCH-0001
---

# ADR-0003 — Path A: local Tauri/TS + Python KG app

**Status: accepted (2026-10-01). Accepts DEC-006 and DEC-010.** The sponsor chose
**Path A** from the RPT-0012 landscape. This settles the *direction* of the application
stack and packaging; it does **not** pick the viz library (gated on A-044) or the KG
substrate (DEC-004) — both stay behind adapters.

## Context

- `APP-0001` set the application requirements: macOS-first, best-in-class interactive
  graph display, large graphs with progressive load, **commercial-grade licensing**, a
  clean backend↔frontend boundary (A-030), and an optional CLI.
- `RPT-0012` framed the candidate stacks and criteria. Rather than run all five research
  lanes to exhaustion, the sponsor made the direction call now; the residual research
  (viz-library comparison under A-044) continues against the fixed shell/engine choice.
- The project is a 4-student semester with a Nov 5 demo floor (ADR-0002); the stack must
  let the team iterate a GUI fast, starting simple.

## Decision

A **local-only, macOS-first desktop application** with these layers:

| Layer | Choice |
|---|---|
| App shell | **Tauri** (Rust thin shell; Mac-first packaging, small binary, system WebView) |
| Frontend / viz | **TypeScript** + a WebGL graph stack (specific library deferred under **A-044**) |
| KG engine | **Python** process / package (models, filters, path/chain queries, store adapters) |
| Integration | **Local-only API** — loopback HTTP/WebSocket and/or native IPC (Tauri commands / stdio / UDS). **No remote servers.** |
| Agentic surface | **CLI** wrapping the *same* Python engine the GUI uses |

This is the realization of `APP-0001` §1 (product shape) and makes A-040 (platform) and
A-046 (packaging) concrete. It accepts **DEC-006** (UI stack / interaction path = local
Tauri desktop, progressive tables→graph) and **DEC-010** (language & packaging = Tauri +
TS frontend / Python engine / local IPC / shared CLI).

## Still open — do not pre-empt

- **DEC-004** — RDF vs LPG (or hybrid) for the Python KG layer. Every slice that touches
  storage/query keeps adapters behind a stable façade until DEC-004 lands. (Iteration-5
  reification analysis, #15, recommends the *logical* model that survives either.) **Narrowed by
  ADR-0004 (DEC-011):** the canonical SoT is git files and the logical model is edge-rich either
  way; DEC-004 is now just the working-store engine pick. See Edge Rich KG (#50).
- **A-044** — commercial viz licence filter (ReGraph / KeyLines / Ogma / yFiles). Prefer
  open WebGL first (Sigma.js / G6 / Cytoscape.js); pick the concrete library later, with a
  licence note, per A-044.

## Boundaries (binding)

| Boundary | Rule |
|---|---|
| GUI ↔ engine | Only through the documented **local API / IPC**. No KG business logic in the WebView beyond presentation. |
| CLI ↔ engine | Same Python package/process API as the GUI. The CLI is **not** a second implementation. |
| Network | **No cloud backend**, no deployed remote service, no "bind for LAN clients" as the product model. Loopback/IPC only, documented as local-only. |
| Viz | Open WebGL first; commercial options only after an **A-044** note. |
| Data model | Storage/query adapters behind a façade until **DEC-004**. |
| Toolchain | The `~/cb` harness pins `node` v8 — that is **harness-only**. The app repo uses **current Node** / modern frontend tooling. Do not pin product Node to v8. |

## Architecture

```
Local machine (macOS-first, offline-capable)
  Tauri shell (Rust)
    └─ TypeScript frontend (WebView):  tables → KG browse → threat chains → WebGL
         │  local API / IPC (loopback HTTP·WS / UDS / Tauri commands) — local-only
         ▼
    Python KG engine  (models · filters · path/chain queries · store adapters)
         ▲                                   │
    CLI (same engine) ─────────────────────┘ │
                                             ▼
                              Local graph / file store (DEC-004 gated)
```

## Execution — progressive vertical slices

Driven by application use cases; each slice ships end-to-end (a user, or an agent via the
CLI, can exercise it). **Progressive UI: tables → KG browse → threat chains → WebGL.** The
per-slice cadence is **design → documents → code → build → test → validate → GUI
integrate → review → plan next**. The slice backlog is in `BACKLOG-0001` (increment I-App)
and the tracking epic is the GitHub "Path A" issue:

- **Slice 0 — Scaffolding:** runnable Tauri+TS shell, Python package, local API `health`,
  CLI stub, CI build/test (no cloud).
- **Slice 1 — Tabular filter UI:** first useful GUI — tables of filter info (sample → live).
- **Slice 2 — KG browse/query** *(gated by DEC-004)*: browse/query through the façade.
- **Slice 3 — Threat chains/paths:** compute + display chains (tabular + linked views).
- **Slice 4 — WebGL graph viz:** interactive graph; library picked under A-044.
- **Slice 5 — Polish, packaging, agent CLI recipes:** Mac packaging, loopback hardening.

## Consequences

- Flips **DEC-006** and **DEC-010** to accepted; `APP-0001` A-040/A-046 are now concrete,
  and APP-0001 becomes the living requirements for the slices.
- Keeps **DEC-004** and **A-044** genuinely open by mandating adapter/façade boundaries —
  the GUI and schemas must not bake in RDF-only or LPG-only assumptions.
- Opens a new backlog increment (**I-App**, Slices 0–5) alongside the research/model track.
  The Nov 5 MVP (ADR-0002) is demonstrated *through* this app: Slices 0–3 are the spine;
  Slice 4 (graph viz) is the ADR-0002 "interactive attack-path graph".
- RPT-0012 is no longer "undecided" for stack direction; its remaining work is the A-044
  viz-library comparison.

## Scope guard

Not this repo elsewhere: Path A is implemented **only in `Threat-Radar/tmodel`**, never in
`m-of-n/library` or `tradar`. No cloud servers, hosted APIs, or online-auth for core
features. No commercial viz before an A-044 note. No skipping design/docs to "just code"
WebGL before tables work.
