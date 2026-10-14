---
schema: "archdoc/v1"
id: DL-0017
title: "Publishing & extraction program — plan, adversarial review, sponsor rulings"
type: process
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: DL-0017
---

# DL-0017 — PLAN-0003 planning round

## Question asked

Sponsor: split publishing so bibliographic products live in the library and tmodel output in tmodel;
a clickable GitHub→Pages URL to a tmodel top → bibliography top (alphabetic + by-category, with
**expandable** rows showing applicability/tags/summary/#requirements/extraction-status); deeply
improve extraction (type-aware, repeatable, requirements re-extracted for correctness; procedures,
agents, code, protocol specs, state machines, formal proofs, human-review logs, threats/vulns; mapped
to products/companies/projects/procedures). "The library drives the design." Produce a multi-agent
plan, adversarially review it, then a PR. Are there gaps? Do we need to update/document schemas?

## What was produced

- **3 parallel recon agents** (library publishing · tmodel publishing · extraction/schema), read-only.
  Key correction: **PR #113 + library #14 are merged** — Pages is live, landing/A–Z/by-category/reports
  and all record pages already exist (import model). So the real gaps are narrower.
- **PLAN-0003** — the program plan (two tracks + schema spine + meta-process).
- **1 adversarial critic agent** attacked the plan; findings folded (below).

## Accepted (folded) from the critic

- **C1** — my §8 order built the expando rows before their data; reordered to **A0 → B0 → B1 → A1/A2**.
- **M2** — the `Requirement` type must be an ARCH-0001 **PROPOSAL diff**, never a commit to the
  canonical LinkML (DEC-001 open); the requirement↔product edges are already **ADR-0004 link records**.
- **M3** — made D1 goal-critical, not an equal-cost toss-up.
- **M4** — carved the research track (R-B2…R-B5) out of the Dec-MVP program.
- **M5** — rewrote A0 as a region-replace (`<!-- site-nav -->…<!-- /site-nav -->`) that preserves the
  library's standalone banner, removes double chrome, with a "no re-pin before the fix" gate.
- **m1/m2/m3** — A0 reworded latent (not live); "# requirements" must be defined; `short_title` as the
  interim summary fallback.

## Rejected / overruled

- **M1 (critic: keep the requirements schema library-local, not LinkML).** **Overruled by sponsor:**
  "LinkML for requirements … schema is a primary delivery." Reconciled: the requirements LinkML schema
  **lives in the library** (library owns its products — D1) as an **open IDL** shared across forks;
  tmodel aligns to it, so the dependency still points **tmodel→library** (the critic's real concern —
  library→tmodel/ADR-0007 coupling — is avoided by location + direction, not by refusing LinkML).

## Sponsor rulings (2026-10-08)

D1 → **library** owns the basic biblio generators (fork; shared basic skills; other forks may add
types). D3 → **LinkML for requirements**, expedited, iterated to perfection. A1 → **stub** for now.
A2 → topics must include **threat-modeling, AI-threats, and other major groupings**. **B0 → its own
PR, ASAP, multi-agent create → iterate — the highest priority** (it improves all later extraction).

## Next

A0 fix (library region + tmodel copy step + re-pin). **B0** launched as a multi-agent schema-creation
effort (requirements LinkML keystone + the other artifact schemas), to land as its own library PR.
