---
schema: "archdoc/v1"
id: PROC-0001
title: "Team coordination — lanes, skills, and who opens which repo"
short_title: "Team coordination"
description: "How four students plus a sponsor split work across tmodel and its library submodule without colliding, and which project root to open for which task."
type: process
category: process
status: draft
version: "0.2.0"
version_policy: "semver; MINOR = additive process rules"
date: "2026-09-23"
updated: "2026-10-12"
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

### 2.1 Claim before you start; re-check before you push

Agents run several sessions at once, often in the same lane. On 2026-10-09 a
follow-up commit was pushed to tmodel #113 after it had merged, so it landed on
a dead branch. By then another session had already shipped the same fix
(library #15, tmodel #115). DL-0016 has the details.

- **Claim the lane.** Before any code, assign yourself to the issue or comment
  on it ("taking this: <branch>"). Do not start on an issue someone else has
  already claimed.
- **Look in both repos.** Check `gh pr list` and the last day's merges in
  `tmodel` *and* `library` for the same lane. If the fix is already on `main`,
  verify `main`. Do not cherry-pick a duplicate.
- **Re-check state before every follow-up push.** Run
  `gh pr view <n> --json state,headRefOid`. If the PR has merged, open a new
  branch from `main`.

## 3. Serialization points

Some work cannot run in parallel:

- **ARCH-0001.** One architecture change at a time (ARCH-0001 §9.4). Two parallel
  model branches produce divergent designs. Serialize.
- **The submodule pin.** Only one PR at a time should bump `library/`'s commit;
  otherwise the pin conflicts. Coordinate at the weekly Zoom. A pin bump runs
  `bin/publish-site`, and the PR must pass `check_links.py` (§6).

## 4. The weekly rhythm

- **Draft PR on day one** of each increment — the progress signal.
- **Weekly 30-min Zoom** — decisions, unblocking, increment demo; notes committed
  the same day.
- **Issues before code** — every task is an issue (`T-NNN`) before it is a diff.
- **Chat/SMS is escalation only, never content.** A decision made in chat that is
  not written into an issue, a doc, or an ADR did not happen.

## 5. Faculty and sponsor

- **Sponsor** (@nymble) owns `spec/**` review via `CODEOWNERS` and is the
  decision-maker on `DEC-*` (accepted only by an ADR).
- **Faculty** (@phaskell) advises and grades; keep the public repo legible
  for that.

## 6. Cross-repo gates

The library is consumed: tmodel copies its record pages and reads its records.
A gate that runs only in the repo that changed cannot see what the change
breaks downstream. In DL-0016, a library chrome change put 828 dead links into
tmodel's pages. A gate that grepped generated markdown also kept library
`main` red for four days without anyone noticing. Rules:

1. **Rebuild in CI, then diff.** tmodel CI checks out submodules, runs
   `bin/publish-site`, and fails on `git diff --exit-code docs/`. That catches
   stale pages and contract breaks on the PR that causes them, not at the next
   manual re-pin. *(Not yet wired.)*
2. **Publisher contract test in the library.** Library CI asserts that every
   `summary.html` has the `<!-- site-nav -->` … `<!-- /site-nav -->` region
   and that no repo-relative link sits outside it. Those two hooks are the
   whole contract with publishers (library `docs/generated-views.md`).
   *(Not yet wired.)*
3. **Gate on data, not on a rendering.** `bin/reindex` writes the record count
   and the bibliography count as data, and CI compares those values. CI does
   not grep `index/bibliography.md`, whose layout changes whenever someone
   adds a view. *(Not yet wired.)*
4. **One YAML reader.** The library keeps a single reader. `test_yaml.py`
   includes a PyYAML comparison across every record whenever PyYAML is
   installed. That comparison is how DL-0016 found a parser that silently
   rejected half the library.
5. **Red `main` is an incident.** Whoever sees `main` failing in either repo
   files an issue that day. A PR that fails only because it inherited a red
   `main` is not ready, and is not blamed.

## 7. The library fork

`Threat-Radar/library` is a GitHub fork of `m-of-n/library`. The two are kept
in step **both ways, by PR, with merge commits** (not squash), so they share
one history. The first fold-back was Threat-Radar #18 and m-of-n #62.

- **Sync small and often.** Open a sync PR in each direction whenever either
  `main` moves materially, at least once per increment. In DL-0016, both sides
  had fixed the same two bugs independently.
- **Same CI on both sides.** Run the same gates in both repos, and change them
  in both repos in the same week. The fork's looser gates let in 19 records
  that m-of-n's FX-1 gate rejects.
- **Sign-off.** Use `git commit -s` in either repo. The DCO check does not
  apply to merge commits that GitHub creates.
- **Agents pass `--repo`.** In a fork checkout, a bare `gh pr view N` resolves
  to the parent repo. Always name `--repo Threat-Radar/library` or
  `--repo m-of-n/library`.
