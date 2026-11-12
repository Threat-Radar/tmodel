---
schema: "archdoc/v1"
id: DL-0051
title: "GitHub Pages browser preview from deterministic static app data"
type: process
status: draft
version: "0.1.0"
date: "2026-11-11"
updated: "2026-11-11"
record: DL-0051
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

This log describes the implementation proposed in PR #231. It does not record
an accepted architecture decision; human review and merge remain pending.

## Design

**One frontend, two data transports.** Vite's `pages` mode builds the existing
desktop frontend with base `/tmodel/app/`. The report, path, Cytoscape graph,
library, model-session and model-picker implementations are shared. Pages mode
adapts their existing GET requests to same-origin JSON; desktop mode retains the
loopback engine, health polling and Tauri sidecar inspection.

**Generated public data.** `docs/publishing/render_app.py` calls the engine
in-process and fails if any model reported by `/models` cannot load. It writes,
for every listed model, the `/graph` response, the attack-path index and each
goal response. It also writes the complete `/library/table` response from the
repository's pinned library, ignoring `TMODEL_LIBRARY`. JSON keys, goal file
names and file traversal order are deterministic. Absolute engine model paths
become approved bare model file names, and generation refuses local path and
common credential markers.

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
temporary build and byte-compares every output. On applicable PRs and pushes to
`main`, app CI runs that verification plus generator, identity, and link tests
against the committed snapshot. CI does not regenerate files back into the
branch, commit them, or deploy through a separate Pages workflow. The #204 CI
requirement is satisfied by rejecting input changes whose committed
`docs/app/` no longer matches a clean generation.

## Proposed design choices and provenance

The implementation submitted in PR #231 proposes the choices below. No project
record currently shows a human accepting or rejecting these individual design
choices. In the PR review, @Clovier independently rebuilt and exercised the
preview, identified the design-log collision and unpinned library override as
blocking, and described the other five points as non-blocking suggestions. The
review state was “Commented”, with approval deferred until the blocking points
were fixed. That is verification and review feedback, not design acceptance;
all choices remain awaiting maintainer or sponsor approval.

- **Proposed: static responses behind the existing providers.** This keeps #211
  as the presentation source and avoids a second report or graph implementation.
- **Proposed: one complete library table and client-side queries.** The bounded
  artifact is useful without exposing the richer record filesystem surface.
- **Proposed: hide unavailable governed workflows.** A static public preview
  cannot truthfully offer SDL decisions, reviews, proposals or persistence.
- **Proposed not to run or proxy the Python engine for Pages.** Static hosting
  has no Python runtime, and a hosted mutable service would be a different
  security and operations design.
- **Proposed not to maintain one fixture per view or selected model.** Such
  fixtures could drift from engine shapes and silently omit new examples.
- **Proposed not to publish full library records.** The table fields meet the
  preview need with a smaller public-data boundary.

## Limits

The preview is a committed snapshot, not a live workspace. It has no editing,
review, annotation, SDL, proposal, saved-view proposal or persistence feature.
Library document details are deliberately less extensive than an engine-backed
desktop inspector. Regeneration requires the pinned library submodule, the
engine environment and Node dependencies; the runtime requires none of them.
