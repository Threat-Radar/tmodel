---
schema: "archdoc/v1"
id: ADR-0008
title: "KG working-store substrate — Oxigraph (embedded RDF), behind the ADR-0004 façade"
short_title: "Working store — Oxigraph/RDF"
description: "Accepts DEC-004 (the question ADR-0004 narrowed to the working-store engine): the local embedded working store is Oxigraph (Rust, embedded RDF with SPARQL and RDF-star). RDF-star carries the reified Assertion; SPARQL runs path/chain queries. The store stays a rebuildable cache (git files remain the SoT, ADR-0004) and lives behind the engine store façade, so the choice is reversible by re-load."
type: decision
category: application
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-08"
updated: "2026-10-08"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0008-working-store-oxigraph.md
accepts: DEC-004
defers_to: ARCH-0001
---

# ADR-0008 — Working store: Oxigraph (RDF)

**Status: accepted (2026-10-08). Accepts DEC-004.** ADR-0004 narrowed DEC-004 to "which RDF-or-LPG
engine implements the local working store." The sponsor picked **RDF via Oxigraph** as the
prototyping default, kept behind the ADR-0004 façade so a later swap is a re-load, not a re-identify.

## Context

- `ADR-0004` fixed the canonical SoT as files in git, the logical invariant as typed edges with
  properties, and the working store as a local embedded, rebuildable graph — leaving the engine open.
- `ADR-0003` makes the app local-only/macOS-first with a Rust (Tauri) shell; `ADR-0009` keeps the
  engine brain in Python with Rust for the store/hot paths. A Rust, embeddable RDF store fits both.
- The #15 object model is a **reified `Assertion`** with provenance/review — a shape RDF-star
  expresses directly.

## Decision (DEC-004)

| # | Decision |
|---|---|
| 1 | **Working store = Oxigraph** — embedded RDF (Rust), **SPARQL** query, **RDF-star** for the reified `Assertion` (provenance/review point at the quoted triple). |
| 2 | **Still a rebuildable cache.** Git files stay the canonical SoT (ADR-0004); the store is loaded/rebuilt from them and is never hand-edited as truth. |
| 3 | **Behind the store façade** (`engine/store/`). The Python engine and the GUI talk to the façade, not to Oxigraph directly; no RDF-only assumption leaks into the TS frontend. |
| 4 | **Path/chain queries** (AttackPath, propagation along `uses_component`/`composed_of`) run as SPARQL inside the façade; results cross the A-030 API as plain objects. |

**Why RDF/Oxigraph over an LPG engine:** RDF-star matches the reified-Assertion provenance model
directly; SPARQL + SHACL (generated per ADR-0007) align with the standards track (RDF 1.2, SHACL 1.2);
Oxigraph is Rust and embeddable, unifying with the Tauri shell and ADR-0009's Rust store. The LPG
edge-properties view remains available through the façade's edge adapter (ADR-0004) for the viz layer.

## Consequences

- Flips **DEC-004** to accepted; ADR-0004's "DEC-004 remains open" line is now resolved to Oxigraph.
- **PLAN-0002** Track B / Slice 2 "LPG or RDF behind the façade" becomes "RDF/Oxigraph behind the
  façade"; the façade and loader (#51/#52) are unchanged — they now target Oxigraph.
- Pairs with **ADR-0007**: Turtle/JSON-LD export is a direct Oxigraph dump; GraphML/CSV are projected
  through the edge adapter for the viz.
- Reversibility preserved: object/edge IDs are canonical in git (ADR-0004), so switching engines is a
  re-load. This ADR does not pin a SPARQL dialect beyond what Oxigraph supports.

## Scope guard

Implemented only in **Threat-Radar/tmodel**. **Embedded only — no remote/LAN graph server** (ADR-0003/0004).
Oxigraph is not the source of truth; no Turtle-as-canonical authoring; no RDF-only assumptions baked
into the GUI without going through the façade.
