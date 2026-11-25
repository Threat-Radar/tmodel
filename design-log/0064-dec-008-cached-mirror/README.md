---
schema: "archdoc/v1"
id: DL-0064
title: "ADR-0014: external catalogs as a cached pinned mirror (DEC-008)"
type: process
status: draft
version: "0.1.3"
date: "2026-11-22"
updated: "2026-11-25"
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
| `spec/ADR-0014-cached-pinned-catalogs.md` | 0.3.0: the decision record, status `proposed`, with the sponsor as decision maker and the team's interim rule until the sponsor decides |
| `project/DECISIONS-0001.md` | 0.1.10: DEC-008's row is `proposed` → ADR-0014, with a dated note on how the team works meanwhile |

ARCH-0001 is unchanged: a proposed ADR does not move DEC-008 to the accepted list.

## Sources read

- ARCH-0001 (DEC-008's wording and R-010), DECISIONS-0001 ("leaning cached mirror per A-043"), APP-0001 A-043,
  PLAN-0002 (no cloud services) and PLAN-0004 Q-07 ("Cached pinned mirror").
- RPT-0001's CWE/NVD section, which was never written ("Pending (T-026)"), so no research report covers this question.
- The code and data: `engine/engine/load/cwe.py`, and the library's `cwe` and `capec` records with their pins.
- MITRE's CWE and CAPEC terms of use (copies are allowed with the copyright designation and the license), and RPT-0004
  `pilot.md` §3 (4 matches, then 30, for the same image).
- For the 2026-11-25 round: #259, and #260 with DL-0063 (what the packaged app ships, and the working rule in
  DL-0063's words); #262 with DL-0065 and Threat-Radar/library#52 (`cwe-4-21` supersedes `cwe`, which keeps its pin);
  the library's `CLAUDE.md` (a new version is a new record); BACKLOG-0001 T-083 (one line, "NVD lookup automation
  (DEC-008)", todo); and, on main, `bin/build-engine` and `engine/engine/load/capec.py` (CAPEC is not bundled yet).

## Choices the agent made, open to review

- **Shipping the copy inside the app**, rather than fetching it at install: the files are small, and the first launch
  stays offline.
- **NVD under the same rule** (pinned copies fetched by a tool, BACKLOG T-083), because DEC-008 names NVD and R-010
  asks for automated lookup.
- **Weakness ids left out,** although PLAN-0004 Q-07 pairs them with this decision: they are a schema question, not an
  integration one.
- **The interim rule written as the team's** (2026-11-25): ADR-0014 cannot say whether the sponsor agrees, because no
  sponsor answer is recorded. It states the rule, says the sponsor has not agreed to it yet, and says what a different
  decision would change.
- **Earlier releases kept, in the decision itself:** a newer release is a new library record, as #262 does, not an
  edit to the old one.
- **NVD snapshots kept, at the level of the decision only:** pinned by digest and never overwritten. Where and how
  they are stored is left to T-083, which has nothing beyond its backlog line yet.
- **Implementation status as its own dated section,** so that Context still says what was built when the ADR was
  drafted.

## What a human accepted

- @Clovier, 2026-11-22: propose the cached mirror ("do the leaning cached mirror").
- @Clovier, 2026-11-22: accept it now, without the sponsor's sign-off: "there is no need sponsor approval, we can go
  ahead and execute the plan right away. I will update the sponsor when i see them".
- @Clovier, 2026-11-23, after @paria03's review: "mark ADR-0014 as proposed, our team decides to use the fixed/cached
  copy that ships inside it for now, if newer catalogues release, another pr will have to be opened to update the
  catalogue".
- @Clovier, 2026-11-25: asked for the changes that answer @kriishnaa-18's review ("aand also fix 261"). The wording of
  this round's changes is Claude Code's; the pull request review is where it is accepted or rejected.

## What was rejected, and why

- Live lookups, fetching at install, and user-supplied files only: see ADR-0014's alternatives.

## Review changes

- 2026-11-23, @paria03's review: PROC-0001 §5 makes the sponsor the decision-maker on every DEC, and ARCH-0001's
  0.1.12 had no changelog entry (§9.5). ADR-0014 went back to `proposed`, with the sponsor as decision maker and no
  `accepts:`. DECISIONS-0001 marks DEC-008 `proposed`, and ARCH-0001 with its changelog is back to main's version,
  so it needs no changelog entry.
- 2026-11-25, @kriishnaa-18's review at `333949c`: @paria03's two findings were addressed, and four points remained.
  ADR-0014 0.3.0 answers each:
  1. **The interim shipping rule.** #259 made catalog packaging wait on DEC-008, but #260 merged on 2026-11-25 with
     the pinned CWE release, before this pull request (DL-0063 had planned the other order). The review asked whether
     the sponsor agrees, and asked @nymble for input. Only the sponsor can answer, and no answer is recorded, so
     ADR-0014's Status now states the rule plainly: what ships and why, where the rule is recorded, that the sponsor
     has not agreed to it yet and it holds only until the sponsor decides, and what a different decision would change.
  2. **Earlier releases stay.** Decision 3: a newer release is a new library record that supersedes the earlier one,
     which keeps its URL and SHA-256, as #262 does (`cwe-4-21` supersedes `cwe`).
  3. **NVD snapshots.** Decision 4: each CVE copy is pinned by its digest and kept, not overwritten. A later fetch is a
     new copy, so a model can be reproduced offline. T-083 settles where and how the copies are stored.
  4. **Implementation status.** A new dated section: #245 and #260 merged, #262 open, T-083 todo. Context, the
     alternatives, Consequences and Validation now say the same.

## Next steps

- The sponsor (@nymble) decides DEC-008, and with it whether the interim rule stands. If accepted, ADR-0014 becomes
  1.0.0 with `accepts: DEC-008`, and ARCH-0001's banner and DEC row change, with a changelog line. If not, a later ADR
  records the other answer, and a later pull request changes how the app gets the releases.
- Meanwhile, the team's working rule holds: the pinned copy ships with the app, and a newer release means a new pull
  request. #259's catalog half (#260) merged under it, and the CWE 4.21 pin (#262, open) follows it.
- Still to do: bundling CAPEC's file the same way (DL-0063), and the NVD tool (T-083).
