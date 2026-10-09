---
schema: "archdoc/v1"
id: ADR-0009
title: "Engine language split — Python brain + Rust store/hot-paths, behind the A-030 façade"
short_title: "Engine language split"
description: "Amends ADR-0003 (DEC-010): the KG engine is not a single-language process. Python owns the modeling (LinkML), schema-guided extraction, orchestration, and the CLI; Rust owns the embedded store (Oxigraph, ADR-0008) and, later, perf-critical graph cores via PyO3. The A-030 API boundary keeps the GUI independent of the engine's internal languages, so this is reversible. ADR-0003's stack direction is otherwise unchanged."
type: decision
category: application
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-10-08"
updated: "2026-10-08"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0009-engine-language-split.md
amends: ADR-0003
refines: DEC-010
defers_to: ARCH-0001
---

# ADR-0009 — Engine language split

**Status: accepted (2026-10-08). Amends ADR-0003 (refines DEC-010).** ADR-0003 wrote the KG engine
as a "Python process." The sponsor refined that: the engine is **Python for the brain, Rust for the
store and hot paths**. This changes one row of ADR-0003's stack table; the rest of Path A stands.

## Context

- ADR-0003 chose Path A (local Tauri/TS + Python KG engine + shared CLI) and deliberately put the
  store behind a façade (DEC-004). ADR-0008 then picked **Oxigraph (Rust)** for that store.
- The sponsor asked whether the engine could be Rust and whether Python is more mature. The honest
  answer splits by layer: the **modeling + extraction** layer is Python-mature (LinkML, SPIRES/OntoGPT,
  the whole LLM/NLP ecosystem) and has no Rust equivalent; the **store + raw graph traversal** layer is
  Rust's strength (Oxigraph, PyO3). A full-Rust engine would buy single-binary packaging at the cost of
  the LinkML/extraction ecosystem — not worth it for a one-semester, AI-assisted project.

## Decision (refines DEC-010 / amends ADR-0003)

| Concern | Language | Rationale |
|---|---|---|
| Object modeling, schema (LinkML, ADR-0007), validation | **Python** | LinkML is Python-native; JSON-Schema/SHACL generators are Python. No Rust LinkML. |
| Schema-guided **extraction** (SPIRES/OntoGPT, grounding) | **Python** | The engine's hardest part; the entire ecosystem is Python. |
| Orchestration, loaders, local API, **CLI** | **Python** | One engine package; the CLI is the same engine (ADR-0003). |
| Embedded **store** (Oxigraph) + SPARQL | **Rust** | ADR-0008. Used from Python via its bindings. |
| Perf-critical **graph cores** (path/chain at scale), later | **Rust via PyO3/maturin** | Pushed down only when a measured need appears; not premature. |

**Reversibility.** The **A-030 API boundary** means the Tauri/TS GUI talks to a local API, never to
Python or Rust directly. The engine's internal language mix can change without touching the frontend.

**Packaging note (accepted cost).** Bundling a Python runtime inside a Tauri/macOS app (A-046) is more
work than a single Rust binary. ADR-0003's packaging slice (Slice 5) owns this; it is an accepted cost
of keeping the Python modeling/extraction ecosystem, not a reason to go all-Rust.

## Consequences

- Updates the ADR-0003 stack table "KG engine" row to **Python brain + Rust store/hot-paths**;
  DEC-010 stays accepted (this refines, does not reopen it).
- **PLAN-0002**: `engine/` stays a Python package (`pyproject.toml`); `engine/store/` wraps Oxigraph
  (Rust) via bindings; a future `engine/_native/` (PyO3) is where hot paths go. Phase-0 packaging must
  prove the Python-in-Tauri bundle, not just a Rust binary.
- No new DEC; the register keeps DEC-010 accepted with ADR-0003 **+ this amendment**.

## Scope guard

Implemented only in **Threat-Radar/tmodel**. The CLI stays the same engine (no second implementation);
no engine business logic in the WebView; Rust hot paths only behind the façade and only on a measured
need. The `~/cb` harness Node v8 pin is harness-only (ADR-0003) and unrelated.
