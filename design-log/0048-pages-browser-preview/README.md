---
schema: "archdoc/v1"
id: DL-0048
title: "GitHub Pages browser preview from deterministic static app data"
type: process
status: draft
version: "0.1.0"
date: "2026-11-11"
updated: "2026-11-11"
record: DL-0048
defers_to: ARCH-0001
bears_on: [APP-0001, ADR-0003, DL-0038]
---

# GitHub Pages browser preview from deterministic static app data

## Request

Issue #204 asks for the interactive application on GitHub Pages under
`/tmodel/app/`: every supported example model, direct links and model switching,
Model Report, Attack Paths, Explore Graph and a useful Library view, without an
installation or a running Python engine. The page must be visibly example data
and read-only. Desktop behavior must stay engine-backed.

Implementation was authorized after a read-only audit of main including the
merged #211 model and view work. Final human review remains pending.

## Design

**One frontend, two data transports.** Vite's `pages` mode builds the existing
desktop frontend with base `/tmodel/app/`. The report, path, Cytoscape graph,
library, model-session and model-picker implementations are shared. Pages mode
adapts their existing GET requests to same-origin JSON; desktop mode retains the
loopback engine, health polling and Tauri sidecar inspection.

**Generated public data.** `docs/publishing/render_app.py` calls the engine
in-process and fails if any model reported by `/models` cannot load. It writes,
for every listed model, the `/graph` response, the attack-path index and each
goal response. It also writes the complete `/library/table` response. JSON keys,
goal file names and file traversal order are deterministic. Absolute engine
model paths become approved bare model file names, and generation refuses local
path and common credential markers.

**Bounded library inspector.** Search, sorting, type/status/topic filters and
contextual facets run over the complete published table. Selecting a document
shows only fields already present in that table plus artifact counts. Full
library records are not published solely to reproduce the engine inspector;
therefore local record paths, reviewer metadata and extraction contents are not
part of the browser artifact.

**Read-only surface.** Pages mode displays “Example data, read-only preview”. It
hides SDL, pending proposals, saved-view proposal controls and engine status.
There is no mutation route or loopback fallback. Unknown model ids fall back to
a supported example with an explicit notice; a successful selection replaces
the URL's `model` parameter so it remains shareable.

**Publishing and freshness.** `bin/publish-site` owns generation of `docs/app/`
alongside the other published views. `render_app.py --check` performs a clean
temporary build and byte-compares every output, and app CI runs that freshness
check plus targeted generator and link tests. The hand-authored landing page
links directly to the mvp-02 preview.

## Accepted and rejected alternatives

- **Accepted: static responses behind the existing providers.** This keeps #211
  as the presentation source and avoids a second report or graph implementation.
- **Accepted: one complete library table and client-side queries.** The bounded
  artifact is useful without exposing the richer record filesystem surface.
- **Accepted: hide unavailable governed workflows.** A static public preview
  cannot truthfully offer SDL decisions, reviews, proposals or persistence.
- **Rejected: run or proxy the Python engine for Pages.** Static hosting has no
  Python runtime, and a hosted mutable service would be a different security and
  operations design.
- **Rejected: one hand-maintained fixture per view or selected model.** It could
  drift from engine shapes and silently omit new examples.
- **Rejected: publish full library records to make the inspector identical.**
  The table fields meet the preview need with a smaller public-data boundary.

## Limits

The preview is a committed snapshot, not a live workspace. It has no editing,
review, annotation, SDL, proposal, saved-view proposal or persistence feature.
Library document details are deliberately less extensive than an engine-backed
desktop inspector. Regeneration requires the pinned library submodule, the
engine environment and Node dependencies; the runtime requires none of them.
