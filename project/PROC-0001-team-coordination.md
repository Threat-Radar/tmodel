---
schema: "archdoc/v1"
id: PROC-0001
title: "Team coordination — lanes, skills, and who opens which repo"
short_title: "Team coordination"
description: "How four students plus a sponsor split work across tmodel and its library submodule without colliding, and which project root to open for which task."
type: process
category: process
status: draft
version: "0.1.0"
version_policy: "semver; MINOR = additive process rules"
date: "2026-09-23"
updated: "2026-09-23"
needs_review: true
reviewed: false
canonical_path: project/PROC-0001-team-coordination.md
defers_to: ARCH-0001
---

# PROC-0001 — Team coordination

**Status: draft. Open for review.**

Four people, two repositories, several lanes at once. This says how the lanes
stay out of each other's way, and — the part that is easy to get wrong — **which
project root to open.**

## 1. Skill partition: open the repo you are working in

**Claude Code loads skills from the project root only. Never transitively
through a submodule, and never from a parent directory.**

A session rooted at `~/cb` (the umbrella workspace) loads `~/cb`'s skills and
**none** of tmodel's. Work done that way runs without the project's judgement and
nothing warns you.

| Working on | Open as project | Skills |
|---|---|---|
| architecture, plan, spec, backlog, research | **`tmodel/`** | `research`, `propose-arch` (I0: T-005) |
| library records, ingestion, summaries | **`library/`** | `ingest-reference`, `summarize`, `distill` |
| both at once, or neither | `~/cb` | the workspace skills only — **not these** |

Skills are partitioned by **what they act on**, never duplicated — duplicates
drift, and a drifted skill is worse than a missing one.

**Never work inside `library/` from the `tmodel` checkout.** It is a submodule on
a **detached HEAD**; commits there belong to no branch and are trivially lost.
Open the `library` repo directly.

## 2. Lanes

A **lane** is one person or agent, one topic, one branch, one worktree, in one
repository.

- One topic per branch; branch names carry the topic/doc id (CONTRIBUTING §2).
- Use a worktree per lane (`bin/wt new <branch>`) so edits never collide.
- Research lanes are sized by dimension (one section of RPT-0001 each), so two
  students do not touch the same file.

## 3. Serialization points

Some work cannot run in parallel:

- **ARCH-0001.** One architecture change at a time (ARCH-0001 §9.4). Two parallel
  model branches produce divergent designs. Serialize.
- **The submodule pin.** Only one PR at a time should bump `library/`'s commit;
  otherwise the pin conflicts. Coordinate at the weekly Zoom.

## 4. The weekly rhythm

- **Draft PR on day one** of each increment — the progress signal.
- **Weekly 30-min Zoom** — decisions, unblocking, increment demo; notes committed
  the same day.
- **Issues before code** — every task is an issue (`T-NNN`) before it is a diff.
- **Chat/SMS is escalation only, never content.** A decision made in chat that is
  not written into an issue, a doc, or an ADR did not happen.

## 5. Faculty and sponsor

- **Sponsor** (Paul Lambert) owns `spec/**` review via `CODEOWNERS` and is the
  decision-maker on `DEC-*` (accepted only by an ADR).
- **Faculty** (Prof. Haskell) advises and grades; keep the public repo legible
  for that.
