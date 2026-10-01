---
schema: "archdoc/v1"
id: APP-0001
title: "Application requirements — the tmodel product (GUI, platform, performance, CLI)"
short_title: "Application requirements"
description: "The product requirements for the tmodel application, distinct from the object-model requirements in ARCH-0001 §4. Covers what the software does, the platform and performance targets, the interactive display, and the radar/tmodel boundary. Feeds DEC-006 (UI) and DEC-010 (stack/language, via RPT-0012). Draft, not ratified."
type: application
category: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
needs_review: true
reviewed: false
canonical_path: spec/APP-0001-application-requirements.md
defers_to: ARCH-0001
agent_notes: >
  APP-0001 is the home for product/application requirements — the sponsor asked
  "where are we capturing the application requirements?" ARCH-0001 §4 holds what the
  *model* must represent (R-0NN); this holds what the *software* must do and the
  platform/quality bars (A-0NN). Nothing here selects a UI stack or language — DEC-006
  and DEC-010 do that, after RPT-0012. Scope is the tmodel tool only; the radar/tmodel
  split is ADR-0001 and is restated in §7.
---

# APP-0001 — Application requirements (the tmodel product)

**What this is.** The requirements for the *software we build* — the tmodel application.
`ARCH-0001` §4 says what the **model** must represent (R-0NN); this says what the
**application** must do and how well (A-0NN). It is the home the sponsor asked for when
they asked "where are we capturing the application requirements?".

**Status: draft.** The MVP functional set is bounded by `ADR-0002`; the platform and
quality targets below are proposed and harden once `RPT-0012` (GUI / platform / stack)
lands and `DEC-006`/`DEC-010` are taken. Nothing here selects a language or UI stack.

## 1. Product shape

The tmodel product is, for the MVP, a **single-user desktop application on macOS** that
loads a threat-model knowledge graph, displays it interactively, and lets a human review
and annotate what the model (and radar, and AI) propose. Its parts:

- **Backend / graph engine** — ingest, the knowledge-graph store and queries, risk
  computation, provenance and review state. (Substrate is `DEC-004`; RDF-vs-LPG is `T-044`.)
- **Interactive GUI (console)** — the graphical threat model and review surface (`DEC-006`;
  ARCH-0001 §10 presentation layer; viz research `#10`).
- **CLI (optional)** — a thin client over the same backend/API for scriptable actions
  (ingest, export, batch queries, CI checks). Nice to have, not the MVP spine.

A clean **backend ↔ frontend boundary (an API)** is a requirement in itself (A-030): it is
what lets the GUI, the CLI, and later a radar hand-off share one engine, and it keeps the
stack/language choice for the GUI (DEC-010) from dictating the backend.

## 2. Functional requirements

MVP-gated per `ADR-0002`; the MVP column mirrors ARCH-0001 §7.

| id | the application shall… | MVP | feeds |
|---|---|---|---|
| **A-001** | ingest a product/instance + components (CPE/purl) and build the KG | ✅ | ARCH §7 |
| **A-002** | import findings/vulnerabilities and propagate them along composition | ✅ | R-027a |
| **A-003** | render the model as an **interactive graph** (one projection) | ✅ | §3, R-033 |
| **A-004** | let a human **review/annotate** proposed nodes/edges (accept/reject + rationale, impact) | ✅ | R-018–R-021 |
| **A-005** | show an **attack path / threat chain** and its feasibility | ✅ | ARCH §7 |
| **A-006** | compute and show a **risk score** per instance (simple, MVP) | ✅ | DEC-003 |
| **A-007** | distinguish **AI-proposed vs human-reviewed** everywhere it shows a node/edge | ✅ | §4 provenance |
| **A-008** | **export** the model (chosen interchange) and import one external format | ◐ | DEC-002 |
| **A-009** | offer **multiple projections** (matrix, timeline, provenance, DFD) | post-MVP | §10 |
| **A-010** | **compare / diff** two subgraphs (e.g. two deployments) side by side | post-MVP | R-035 |
| **A-011** | **saved views / perspectives** a user can name and reopen | post-MVP | R-033 |
| **A-012** | link out to external systems (Jira) from findings/mitigations | post-MVP | R-028 |

## 3. Display & interaction requirements (sponsor round)

These make ARCH-0001 §10 concrete as *product* requirements. The display is a derived
view over the graph (ARCH §1.5) — these are how it must behave.

| id | the display shall… | MVP |
|---|---|---|
| **A-020** | lay out the graph with **force-directed physics**, stable under interaction | ✅ |
| **A-021** | colour nodes/edges **uniquely by type and facet** (STRIDE, severity, trust zone) | ✅ |
| **A-022** | **click a node to expand containment** (`composed_of`) or **inspect** it (detail, provenance, review state) | ✅ |
| **A-023** | **progressively load** — open from a focus/filter and expand lazily; never load the whole KG at once | ✅ |
| **A-024** | collapse/aggregate (**level-of-detail**, roll-up clusters) to keep large graphs legible | ◐ |
| **A-025** | treat **tags/types/zones/domains as toggle-able layers** composited over one graph | post-MVP |
| **A-026** | let a user weight focus (**"gravity"**) to bring an area forward (focus + context) | post-MVP |
| **A-027** | remain responsive at the **target graph scale** (A-041) | ✅ |

## 4. Non-functional requirements

| id | requirement | target (proposed; confirm at DEC-006/DEC-010) |
|---|---|---|
| **A-040** | **Platform** — primary target | macOS first; cross-platform not required for MVP |
| **A-041** | **Scale** — interactive at | ≥ ~10k nodes / ~50k edges with progressive load (confirm vs real models in RPT-0012) |
| **A-042** | **Display quality** — graphics & interaction | "best-in-class": smooth pan/zoom/drag, crisp rendering, no jank at A-041; a named product-quality bar, not a prototype |
| **A-043** | **Offline** | works without network for the core loop (ingest → graph → review); external lookups (NVD/CWE) may be cached (DEC-008) |
| **A-044** | **Licensing** — commercial-grade | the stack and every graph/viz dependency must have a licence compatible with a commercial product; no copyleft or per-seat lock-in that blocks that (a hard filter in RPT-0012) |
| **A-045** | **Provenance integrity** | the UI never presents AI output as reviewed (CLAUDE.md); review state is always visible |
| **A-046** | **Packaging** | installs and runs as a normal macOS app (a single artefact), not a dev-only toolchain |

## 5. CLI (optional)

| id | the CLI may… | MVP |
|---|---|---|
| **A-060** | ingest / export / run batch queries over the same backend API | optional |
| **A-061** | run as a CI check (validate a model, diff two models) | optional |
| **A-062** | share config and the graph engine with the GUI (no second implementation) | optional |

The CLI is **optional** per the sponsor; it is attractive because it falls out almost for
free *if* the backend/API boundary (A-030) is honoured. It must never become a second
engine.

## 6. Open decisions this feeds

- **DEC-006** — UI stack & interaction model. APP-0001 §2–§4 are its requirements input;
  the candidate stacks and the decision criteria are researched in **RPT-0012**.
- **DEC-010** (new) — implementation stack & language. "Language choice to be driven by
  GUI and platform research" (sponsor). See DECISIONS-0001 and **RPT-0012**.
- **DEC-004** — knowledge-graph substrate (RDF vs LPG) and the review model; the backend
  (A-001, A-030) depends on it (`T-044`).
- **DEC-002** — interchange formats, which A-008 depends on.

## 7. Scope — the radar / tmodel boundary (ADR-0001)

tmodel is the **architectural-modelling** product: it builds and displays the threat
model and carries human review. **tradar** does composition/finding discovery and feeds
tmodel as imported attestations (SBOM/SLSA, ADR-0001 §…). This document scopes **only the
tmodel application**; build/compile provenance and supply-chain scanning are radar's and
arrive over the radar→tmodel contract, not re-implemented here. Audit/compliance tooling
(Requirement/WorkProduct) stays deferred to `#19`.

## 8. Not in scope (MVP)

Multi-user/collaboration, server/web deployment, authn/authz, mobile, and automated
compliance reporting are **out of the MVP** — recorded so the stack research (RPT-0012)
does not over-weight them, while A-030's clean boundary keeps them reachable later.
