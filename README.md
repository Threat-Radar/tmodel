# tmodel

**Best-in-class threat modeling.** A knowledge-graph-backed threat-modeling
system: an object model for threats, attack paths and mitigations; a graphical,
interactive model that a human reviews and annotates; risk metrics that say *how
bad* a threat is; and mappings from generic threats to specific products and
product families, tracked over a product's design lifecycle.

USF CS 490 Senior Team Project, Fall 2026. Sponsor: Paul Lambert (Threat-Radar).
Faculty: Prof. Paul Haskell. Four students, one semester, an early-December MVP.

Extends the 2025 *Threat Radar* master's work (container / dependency composition
analysis, [`Threat-Radar/tradar`](https://github.com/Threat-Radar/tradar)) and
reuses the [`library`](https://github.com/Threat-Radar/library) knowledge graph.

> **A threat model proves nothing on its own.** An AI-generated attack path is a
> hypothesis until a human with domain knowledge accepts it. Human review,
> annotation, and impact judgement are first-class in this system, not an
> afterthought. See [`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md).

## Where to start

| | |
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
(see PLAN-0001 §Week-0 gate). Nothing here is decided because it appears in a
draft; an open decision is settled only by an `ADR`.

## Layout

```
spec/               ARCH, ADR, MAP — the object model and architecture   (archdoc/v1)
spec/schema/        our threat-model schema; imports (and may export) existing formats
spec/vectors/       example threat models — the interop / regression contract
project/            PLAN, BACKLOG, PROC, DECISIONS, GLOSSARY — how we run it (archdoc/v1)
research/           versioned research reports; references land in library/
library/            submodule -> Threat-Radar/library (the knowledge graph)
prototype/          throwaway spikes; never ships
design-log/         AI-assisted design record — what was produced, accepted, and rejected
```

## The library is a submodule

`library/` is a fork of [`m-of-n/library`](https://github.com/m-of-n/library)
in the Threat-Radar org, vendored here as a submodule pinned to a commit so a
report's bibliography is reproducible as `library@<commit>`. Expanding it is a
named deliverable. **Never work inside `library/`** from this checkout (detached
HEAD) — open the `library` repo directly. See CONTRIBUTING §3.

First-time clone:

```sh
git clone --recurse-submodules https://github.com/Threat-Radar/tmodel
```
