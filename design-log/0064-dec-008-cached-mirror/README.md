---
schema: "archdoc/v1"
id: DL-0064
title: "ADR-0014: external catalogs as a cached pinned mirror (DEC-008)"
type: process
status: draft
version: "0.1.2"
date: "2026-11-22"
updated: "2026-11-23"
record: DL-0064
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0064: ADR-0014, external catalogs as a cached pinned mirror (DEC-008)

AI-assisted design record (per `CLAUDE.md`), drafted by Claude Code for @Clovier. @Clovier first marked ADR-0014
accepted the same day; after review it went back to proposed on 2026-11-23, for the sponsor to decide.

## Question asked

#259 found that the downloaded app cannot show the Weaknesses tab, because how the app gets MITRE's catalogs is
DEC-008, still open. @Clovier asked for a proposal that takes the team's lean, a cached mirror.

## What was produced

| File | What it is |
|---|---|
| `spec/ADR-0014-cached-pinned-catalogs.md` | The decision record, status `proposed`, with the sponsor as decision maker |
| `project/DECISIONS-0001.md` | 0.1.10: DEC-008's row is `proposed` → ADR-0014, with a dated note on how the team works meanwhile |

ARCH-0001 is unchanged: a proposed ADR does not move DEC-008 to the accepted list.

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
- @Clovier, 2026-11-23, after @paria03's review: "mark ADR-0014 as proposed, our team decides to use the fixed/cached
  copy that ships inside it for now, if newer catalogues release, another pr will have to be opened to update the
  catalogue".

## What was rejected, and why

- Live lookups, fetching at install, and user-supplied files only: see ADR-0014's alternatives.

## Review changes

- 2026-11-23, @paria03's review: PROC-0001 §5 makes the sponsor the decision-maker on every DEC, and ARCH-0001's
  0.1.12 had no changelog entry (§9.5). ADR-0014 went back to `proposed`, with the sponsor as decision maker and no
  `accepts:`. DECISIONS-0001 marks DEC-008 `proposed`, and ARCH-0001 with its changelog is back to main's version,
  so it needs no changelog entry.

## Next steps

- The sponsor (@nymble) decides DEC-008. If accepted, ADR-0014 becomes 1.0.0 with `accepts: DEC-008`, and ARCH-0001's
  banner and DEC row change, with a changelog line. If not, a later ADR records the other answer.
- Meanwhile, #259's catalog half (#260) and the CWE 4.21 pin (#262) follow the team's working rule: the pinned copy
  ships with the app, and a newer release means a new pull request.
