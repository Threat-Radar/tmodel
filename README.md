# tmodel

A knowledge-graph-backed threat-modeling system: an object model for
vulnerabilities, threats, weaknesses, assets, attack paths, attack steps, and
mitigations, tracked as linked, reviewable nodes; a graphical, interactive model
that a human reviews and annotates; risk metrics that say *how bad* a threat is;
and mappings from generic threats to specific products and product families,
tracked over a product's design lifecycle.

USF CS 490 Senior Team Project, Fall 2026. Sponsor: Paul Lambert (Threat-Radar).
Faculty: Prof. Paul Haskell. Four students, one semester, an early-December MVP.

Extends the 2025 *Threat Radar* master's work (container / dependency composition
analysis — [`Threat-Radar/tradar`](https://github.com/Threat-Radar/tradar)) and
reuses the [`library`](https://github.com/Threat-Radar/library) knowledge graph.

> **A threat model proves nothing on its own.** An AI-generated attack path is a
> hypothesis until a human with domain knowledge accepts it. Human review,
> annotation, and impact judgement are first-class here, not an afterthought.
> See [`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md).

## What the model tracks

The graph's first-class nodes — draft, ratified by
[`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md) §3, every `DEC-*`
still open:

| node | what it is | maps to |
|---|---|---|
| **Asset** | what damage happens to | — |
| **Component** | a part of the system (container, dependency, source module) | SBOM / composition |
| **Weakness** | a *class* of flaw | **MITRE CWE** |
| **Vulnerability** | a concrete instance of a weakness | **CVE / NVD** |
| **Threat** | an adverse action against an asset | — |
| **Attack step** | one atomic action an attacker takes | — |
| **Attack path / chain** | an ordered set of attack steps leading to damage | rendered as a graph |
| **Mitigation** | a control that reduces a threat | tracked per product |
| **Risk score** | *how bad*, in a given environment | CVSS / ISO 21434 / Common Criteria (DEC-003) |
| **Review** | a human's verdict + assigned impact on any node | — |
| **Product / family** | what a generic threat is mapped onto | — |

Edges are **typed** (`exploits`, `mitigated_by`, `instance_of`, `step_of`,
`reviewed_by`, `applies_to_product`, …) — that is what makes the graph queryable,
e.g. *"every unmitigated attack path bearing on asset X in product Y."*

### Why track weaknesses and vulnerabilities, not just threats

A threat is a judgement; a weakness (CWE) and a vulnerability (CVE) are catalogued
facts. Keeping them as distinct, linked nodes is what lets tmodel:

- **integrate MITRE CWE and automate NVD/CVE lookups**, instead of hand-listing risks;
- carry a **per-product mitigation status** — the same weakness can be mitigated in
  one product and open in another member of the same family;
- answer the lifecycle question **"is this weakness still mitigated in product X?"**
  as the design evolves, rather than rebuilding the model each release.

This dimension grows the graph fastest, and it carries a design implication: the
schema ([`spec/schema/`](spec/schema/)) and the `library` (which ingests
CWE / CAPEC / NVD as reference data) must treat weaknesses and vulnerabilities as
**durable, versioned, cross-linked** records — not transient scan output. Tracked
in ARCH-0001 as R-010 (CWE/CVE mapping + NVD automation) and R-021 (mitigation
lifecycle), with the open decisions DEC-004 (graph substrate + annotation) and
DEC-008 (CWE/NVD integration).

## Where to start

| document | what it is |
|---|---|
| [`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md) | **Architecture — the source of truth.** Read first. `DEC-*` are open. |
| [`project/PLAN-0001`](project/PLAN-0001-project-plan.md) | Semester execution plan, increments, demo |
| [`project/BACKLOG-0001`](project/BACKLOG-0001.md) | Tasks (`T-NNN`) |
| [`project/DECISIONS-0001`](project/DECISIONS-0001.md) | Open decisions waiting on a human |
| [`project/PROC-0001`](project/PROC-0001-team-coordination.md) | Team lanes, who opens which repo |
| [`research/0001-threat-modeling-landscape`](research/0001-threat-modeling-landscape/report.md) | First research report — the competitive landscape |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branches, worktrees, PRs, review |
| [`CLAUDE.md`](CLAUDE.md) | Constraints for agents and humans |

## Status

**Pre-implementation — bootstrap.** The architecture is a v0.1.0 skeleton with
every `DEC-*` open. Requirements and final goals are finalized in **week 1**
(PLAN-0001 §Week-0 gate). Nothing here is decided because it appears in a draft;
an open decision is settled only by an `ADR`.

## Layout

```
spec/          ARCH, ADR, MAP — the object model and architecture      (archdoc/v1)
spec/schema/   our threat-model schema; imports (and may export) existing formats
spec/vectors/  example threat models — the interop / regression contract
project/       PLAN, BACKLOG, PROC, DECISIONS, GLOSSARY — how we run it (archdoc/v1)
research/      versioned research reports; references land in library/
library/       submodule -> Threat-Radar/library (the knowledge graph)
prototype/     throwaway spikes; never ships
design-log/    AI-assisted design record — what was produced, accepted, rejected
```

## The library is a submodule

`library/` is a fork of [`m-of-n/library`](https://github.com/m-of-n/library) in
the Threat-Radar org, vendored here as a submodule pinned to a commit so a report's
bibliography — and its CWE/CAPEC/NVD reference records — is reproducible as
`library@<commit>`. Expanding it is a named deliverable. **Never work inside
`library/`** from this checkout (detached HEAD); open the `library` repo directly.
See CONTRIBUTING §3.

First-time clone:

```sh
git clone --recurse-submodules https://github.com/Threat-Radar/tmodel
```
