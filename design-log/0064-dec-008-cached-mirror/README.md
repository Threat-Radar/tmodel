---
schema: "archdoc/v1"
id: DL-0064
title: "ADR-0014: external catalogs as a cached pinned mirror (DEC-008)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-22"
updated: "2026-11-22"
record: DL-0064
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0064: ADR-0014, external catalogs as a cached pinned mirror (DEC-008)

AI-assisted design record (per `CLAUDE.md`), drafted by Claude Code for @Clovier. @Clovier accepted ADR-0014 the
same day, without waiting for the sponsor, and will tell them.

## Question asked

#259 found that the downloaded app cannot show the Weaknesses tab, because how the app gets MITRE's catalogs is
DEC-008, still open. @Clovier asked for a proposal that takes the team's lean, a cached mirror.

## What was produced

| File | What it is |
|---|---|
| `spec/ADR-0014-cached-pinned-catalogs.md` | The decision record, status `accepted` |
| `spec/ARCH-0001-threat-model-architecture.md` | 0.1.12: DEC-008 moves to the accepted list, and its row points to ADR-0014 |
| `project/DECISIONS-0001.md` | 0.1.10: DEC-008's row points to ADR-0014, with a dated note |

## Sources read

- ARCH-0001 (DEC-008's wording and R-010), DECISIONS-0001 ("leaning cached mirror per A-043"), APP-0001 A-043,
  PLAN-0002 (no cloud services) and PLAN-0004 Q-07 ("Cached pinned mirror").
- RPT-0001's CWE/NVD section, which was never written ("Pending (T-026)"), so no research report covers this question.
- The code and data: `engine/engine/load/cwe.py`, and the library's `cwe` and `capec` records with their pins.
- MITRE's CWE and CAPEC terms of use (copies are allowed with the copyright designation and the license), and RPT-0004
  `pilot.md` §3 (4 matches, then 30, for the same image).

## Choices the agent made, open to review

- **Shipping the copy inside the app**, rather than fetching it at install: the files are small, and the first launch
  stays offline.
- **NVD under the same rule** (pinned copies fetched by a tool, BACKLOG T-083), because DEC-008 names NVD and R-010
  asks for automated lookup.
- **Weakness ids left out,** although PLAN-0004 Q-07 pairs them with this decision: they are a schema question, not an
  integration one.

## What a human accepted

- @Clovier, 2026-11-22: propose the cached mirror ("do the leaning cached mirror").
- @Clovier, 2026-11-22: accept it now, without the sponsor's sign-off: "there is no need sponsor approval, we can go
  ahead and execute the plan right away. I will update the sponsor when i see them".

## What was rejected, and why

- Live lookups, fetching at install, and user-supplied files only: see ADR-0014's alternatives.

## Next steps

- @Clovier tells the sponsor. If they disagree, a later ADR supersedes this one.
- #259's catalog half: the build fetches, checks and bundles the pinned CWE file, with MITRE's notices.
