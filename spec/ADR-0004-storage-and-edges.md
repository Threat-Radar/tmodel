---
schema: "archdoc/v1"
id: ADR-0004
title: "Storage & edges — file canonical SoT, edge-rich logical model, local working store"
short_title: "Storage & edges"
description: "Accepts DEC-011 (the sponsor storage/edges pin): the canonical source of truth is files in git (YAML/JSON / LinkML objects + explicit link records); the logical invariant is typed edges with properties (substrate-neutral, stable object IDs); the working store is a local embedded, rebuildable graph (no remote servers); export formats are derived, never canonical. Narrows — does not close — DEC-004 (RDF vs LPG) to the working-store implementation."
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
canonical_path: spec/ADR-0004-storage-and-edges.md
accepts: DEC-011
defers_to: ARCH-0001
---

# ADR-0004 — Storage & edges

**Status: accepted (2026-10-01). Accepts DEC-011.** The sponsor pinned how tmodel stores its
knowledge graph. This **narrows — does not close — DEC-004** (RDF vs LPG), which remains open as
the *implementation of the local working store only*. Tracking issue: **Edge Rich KG (#50)**.

## Context

- **ADR-0003 (Path A, in review #48)** set the application: a local-only, macOS-first Tauri/TS +
  Python app, with the KG substrate (DEC-004) deliberately behind an adapter.
- The #15 object-model work established a reified-`Assertion` provenance model and typed relations
  (requirements↔products, vuln propagation, VEX overrides). The sponsor's pin fixes *where the
  truth lives* and *what shape edges have*, independent of which graph engine runs locally.

## Decision (DEC-011)

| # | Decision |
|---|---|
| 1 | **Canonical source of truth = files in git** — YAML/JSON / LinkML-shaped objects **+ explicit link records**. The graph is authored and version-controlled as files, reviewed like any other change. |
| 2 | **Logical invariant = typed edges with properties** (requirements↔products, etc.). **Substrate-neutral:** representable as LPG edges-with-properties locally **or** as RDF-star / a reified `Assertion` — **without changing object IDs**. The #15 reification work (R-027b / R-025) is an **input** here, not a ratified claim. |
| 3 | **Working store = local embedded only** — a rebuildable graph (Oxigraph / SQLite / etc.). **No remote servers**, no "bind for LAN clients". (Path A, ADR-0003.) |
| 4 | **Export / transmit ≠ canonical** — generate Turtle / JSON-LD / GraphML / CSV on demand; the team is **not** required to hand-edit Turtle unless it opts in. |
| 5 | **GUI slice order unchanged** — tables → KG → threat chains → WebGL (ADR-0003). |
| 6 | **DEC-004 remains open** — it is now scoped to *which RDF-or-LPG engine implements the working store*; the logical model stays edge-rich either way. |

## Architecture

```
Canonical (git)                 Working store (local embedded)        Clients — Path A
  YAML / JSON / LinkML   --load/rebuild-->  Oxigraph / SQLite / …  --query-->  GUI (tables→KG→chains→WebGL)
  + explicit link records                   rebuildable · no remote           CLI (same Python engine)
                                                   |
                                                   `--generate (not SoT)--> Turtle · JSON-LD · GraphML · CSV
```

Primary path: **Canonical → Working store → GUI/CLI.** Export is a **side path** — derived, never
the source of truth.

## Object-ID stability (the load-bearing constraint)

The same object and the same edge keep **one stable ID** across every encoding:

- In **LPG**, an edge is a relationship with properties; a *reviewed* edge is promoted to a reified
  node (the #15 `Assertion`) so provenance/review can point at it.
- In **RDF**, the same edge is an RDF-star quoted triple / named graph / reified `Assertion`.
- The canonical file ID is authoritative; adapters MUST map to it **without churning IDs**. An
  export or a substrate swap never renames an object or an edge.

This is what lets DEC-004 stay open: switching the working-store engine is a re-load, not a
re-identification.

## Consequences

- **Accepts DEC-011**; **narrows DEC-004** to the working-store engine pick (still open).
- **Input to DEC-002** (encoding/interchange): the export formats here are the derived side, not the
  canonical serialization; the DEC-002 round-trip test (CF-008, #9) still governs interchange.
- The Python engine (ADR-0003) gains a **loader** (git SoT → working store) and an **edge façade**
  (typed edges + adapters); **Slice 2** notes become "logical edges pinned; DEC-004 = substrate
  only". Sub-tasks: loader (#51), edge façade (#52), export generators (#53), docs sync (#54).
- **Guards:** no remote graph servers, no Turtle-as-canonical authoring, no RDF-only/LPG-only
  assumptions baked into the TS GUI without an adapter, no reordering of the GUI slices.

## Scope guard

Implemented only in **Threat-Radar/tmodel** — not `m-of-n/library` or `tradar`. This ADR does
**not** accept or close DEC-004, and does **not** ratify the #15 R-027b/R-025 claim IDs (input only).
