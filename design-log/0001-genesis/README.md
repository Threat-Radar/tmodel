---
schema: "archdoc/v1"
id: DL-0001
title: "Genesis — bootstrapping the repo, plan, and ARCH-0001 skeleton"
type: process
status: draft
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
record: DL-0001
---

# DL-0001 — Genesis

The AI-assisted bootstrap of `tmodel`, recorded per `CLAUDE.md` ("the design log
is not optional").

## Question asked

Stand up a long-lived senior-project repo — structure + one-semester plan to an
early-December MVP — from the sponsor's kickoff brief, modeled on the sibling
`m-of-n` project's conventions.

## What was produced

- Repo harness: README, CLAUDE, CONTRIBUTING, `.github/` (CODEOWNERS, PR + issue
  templates, CI), `bin/` (`new-doc`, `validate-archdoc`, `wt`), all ported from
  `m-of-n/mofn` and adapted.
- `spec/ARCH-0001` — a **skeleton** object model, draft requirements (R-*), and
  nine open decisions (DEC-001…DEC-009), plus its changelog.
- `project/` — PLAN-0001 (increments I0–I5 to the demo), BACKLOG-0001, PROC-0001
  (team lanes), DECISIONS-0001, GLOSSARY-0001.
- `research/0001-threat-modeling-landscape/` — a versioned report **scaffold**
  (dimensions, empty search/source logs, pending sections).

## What a human accepted

- The four sponsor decisions carried in from the kickoff: fork `m-of-n/library`
  into Threat-Radar; one repo now (schema in `spec/`, not a second repo); local
  container `tmodel2026/`; roster from the latest email note.

## What was deferred / rejected — and why

- **No design chosen.** Every `DEC-*` is open on purpose: writing a schema,
  picking a UI stack, or selecting a risk metric now would decide by accident,
  before RPT-0001 exists. ARCH-0001 is deliberately a skeleton.
- **No `LICENSE` file yet.** The public-license choice is an `agent_ask_first`
  item; CONTRIBUTING §9 states the intended dual license (Apache-2.0 code /
  CC-BY-4.0 docs) pending sponsor confirmation.
- **Library submodule not wired in this commit.** The `Threat-Radar/library`
  fork does not exist yet; wiring it before it exists produces a broken submodule.
  The exact `git submodule add` command is in CONTRIBUTING §8, run at I0 T-002.
- **No publishing site.** mkdocs/build-site from mofn was not ported; parked as
  T-006 until the docs earn a site.
- **Roster not written.** Student names come from the sponsor's email note
  (Gmail), pulled and confirmed before any vault person file is created.

## Next steps

Create the GitHub repos, fork the library, add the roster as admins, wire the
submodule, push, and open the bootstrap PR (BACKLOG I0). Then I1 research begins.
