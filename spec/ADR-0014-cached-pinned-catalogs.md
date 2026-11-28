---
schema: "archdoc/v1"
id: ADR-0014
title: "External catalogs as a cached pinned mirror (DEC-008)"
short_title: "Cached pinned catalogs (DEC-008)"
description: "Proposed (2026-11-22): tmodel reads MITRE's CWE and CAPEC, and NIST's NVD records, from pinned copies checked by SHA-256 and shipped with the app, never through live lookups; a new release arrives only by a reviewed pull request, and earlier releases stay. The sponsor decides DEC-008. Until then the team works this way, as an interim rule the sponsor has not agreed to yet."
type: decision
category: security
status: proposed
version: "0.3.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-11-22"
updated: "2026-11-25"
authors:
  - role: student
    id: Clovier
decision_makers:
  - role: sponsor
    id: nymble
reviewers:
  - role: drafting-agent
    id: claude-code
    kind: ai_agent
needs_review: true
reviewed: false
canonical_path: spec/ADR-0014-cached-pinned-catalogs.md
bears_on: [DEC-008]
---

# ADR-0014: External catalogs as a cached pinned mirror (DEC-008)

## Status

**Proposed.** The sponsor (@nymble) decides DEC-008, as PROC-0001 §5 says for every `DEC-*`. @Clovier drafted this
on 2026-11-22 and first marked it accepted, then returned it to proposed on 2026-11-23 after review (#261).

**The interim rule.** Until the sponsor decides, the team works this way: the app ships the pinned copies, and a newer
catalog release reaches the app only through a new pull request that moves its pin. @Clovier set this rule on
2026-11-23: "our team decides to use the fixed/cached copy that ships inside it for now, if newer catalogues release,
another pr will have to be opened to update the catalogue". DL-0063 (#260's design log), DL-0064 and DECISIONS-0001
record it.

- **What ships now, and why.** #259 made the catalog part of its fix wait on DEC-008. #260 did not wait: under this
  rule it ships the CWE 4.20 release the library pins, checked against its SHA-256 and with MITRE's notice, so that
  the downloaded app's Weaknesses tab works. #260 merged on 2026-11-25, while this ADR was still in review. CAPEC is
  not bundled yet.
- **The sponsor has not agreed to it yet.** The rule is the team's, not a decision on DEC-008. It holds only until the
  sponsor decides DEC-008.
- **What the sponsor's decision changes.** If the sponsor accepts, this ADR becomes 1.0.0 and accepts DEC-008, the
  interim rule becomes the decision, and the app stays as it is. If the sponsor decides differently, a later ADR
  records that answer, and a later pull request changes how the app gets the releases (DL-0063): the download and
  bundling step in `bin/build-engine`, and where a packaged engine looks for the file (`engine/engine/load/cwe.py`).

The sources and the choices behind this ADR are in DL-0064.

## Context

- **The decision.** DEC-008 asks how tmodel integrates CWE and NVD: "live lookup vs cached mirror; how automation
  runs" (ARCH-0001). R-010 asks to "Map Weakness→CWE and Vulnerability→CVE, with automated NVD lookup (DEC-008)."
- **Offline is a requirement.** A-043 (APP-0001): the app "works without network for the core loop (ingest → graph →
  review); external lookups (NVD/CWE) may be cached (DEC-008)". PLAN-0002 adds that no cloud services are required.
- **The team's lean.** DECISIONS-0001 records "leaning cached mirror per A-043", and PLAN-0004 Q-07 proposes a
  "Cached pinned mirror".
- **What was built when this was drafted** (2026-11-22). The library pins one release of each MITRE catalog by URL and
  SHA-256: CWE 4.20 (`cwec_v4.20.xml.zip`, `3976f599…`) and CAPEC 3.9 (`capec_v3.9.xml`, `70279a2d…`). The engine reads
  the CWE file that `$TMODEL_CWE_CATALOG` names and refuses any file whose digest differs from the pin (#233); the
  CAPEC import in #245 works the same way with `$TMODEL_CAPEC_CATALOG`. Whether that copy is "bundled, cached or
  fetched at install is DEC-008, still open", said `engine/engine/load/cwe.py`, so the downloaded app's Weaknesses tab
  could not work (#259). What has merged since is under Implementation status.
- **Live data moves.** RPT-0004's pilot scanned the same image twice and got 4 matches on 2026-09-28 and 30 on
  2026-10-08 (`research/0004-product-composition/pilot.md` §3).

## Decision

1. **A cached pinned mirror, never live.** tmodel reads each external catalog from a local copy of one release,
   pinned by URL and SHA-256 in that catalog's library record. Neither the app nor the engine calls MITRE or NVD at
   run time.
2. **Shipped with the app.** The release and PR builds download each pinned file, refuse it unless its SHA-256
   matches the pin, and bundle it with the engine. The engine then finds it without the environment variables, which
   still override it for development. The app carries MITRE's copyright designation and license for each catalog it
   ships, as the CWE and CAPEC terms of use require.
3. **New releases by reviewed pull request.** A catalog changes only when someone updates its pin in the library (URL
   and SHA-256), reviews the import report, and the change merges. Nothing updates itself. Tools may automate the
   steps (download, digest, report) and open that pull request. **Earlier releases stay:** the newer release gets a
   new library record that supersedes the one before it, as the library's `CLAUDE.md` says ("a new version of a spec
   is a new record linked by `supersedes`"), and the earlier record keeps its URL and SHA-256. #262 does this for
   CWE 4.21: the library's record `cwe-4-21` (library#52) supersedes `cwe`, which stays the 4.20 record with its pin.
4. **NVD the same way.** CVE records are pinned copies too: a tool fetches the records a model needs, by CVE id, and
   stores each with its digest for review. That is how R-010's automated NVD lookup runs, without live calls from the
   app. **Snapshots are kept, not overwritten.** A later fetch of the same CVE may differ, since live data moves
   (Context), so it becomes a new pinned copy, added by a reviewed pull request, and the earlier copy and its digest
   stay. A model can then be reproduced offline from the copies it was built on. The tool is BACKLOG T-083 (still
   todo), and where and how it stores the copies is for T-083 to settle. Until it exists, models cite CVE records by
   link, as `pv-03` does for CVE-2015-9235.

## Alternatives considered

- **Live lookups from the app** (NVD's API, MITRE's sites): always current, but it breaks A-043's offline loop, the
  same model can give different results from one day to the next, and it depends on outside services being reachable.
- **A cached copy fetched at install or on first use:** a smaller download, but it needs the network once and adds a
  way for the first launch to fail. The pinned files are small: 1.9 MB for CWE 4.20 (zipped) and 3.7 MB for CAPEC 3.9.
- **User-supplied files only** (the environment variables alone, as before #260): nothing to bundle, but the
  Weaknesses tab does not work for anyone who downloads the app.

## Consequences

- #259's catalog half went ahead under the interim rule above (#260): the build fetches, checks and bundles the
  pinned CWE file, with MITRE's notice. CAPEC's file follows the same way (DL-0063).
- DECISIONS-0001 marks DEC-008 `proposed` and points here. ARCH-0001's status banner and DEC table change only when
  the sponsor accepts. #260 changed the docstring in `engine/engine/load/cwe.py` to point here; the one in
  `engine/engine/load/capec.py` still says DEC-008 is open.
- Updating a catalog becomes a routine pull request: add the new release's library record, rebuild, review. The
  earlier release's record stays.
- Not decided here: weakness ids and catalog keys (the other half of PLAN-0004 Q-07), and which CWE views are
  imported (#61).

## Implementation status (2026-11-25)

- **CAPEC import, #245** (merged 2026-11-23): the engine reads CAPEC 3.9 from the file `$TMODEL_CAPEC_CATALOG` names
  and refuses one whose SHA-256 differs from the pin. The build does not bundle CAPEC yet, so a packaged engine has no
  CAPEC copy unless that variable names one.
- **CWE in the packaged app, #260** (merged 2026-11-25, closes #259), under the interim rule: the release and PR builds
  download the CWE 4.20 file the library pins, stop unless its SHA-256 matches, and bundle it. A packaged engine reads
  it when `$TMODEL_CWE_CATALOG` is not set, and the app's third-party notices carry MITRE's copyright designation and
  license.
- **CWE 4.21, #262** (open): moves the library pin to the commit that adds the record `cwe-4-21` (library#52), which
  supersedes `cwe`; `cwe` stays the 4.20 record with its URL and SHA-256 (Decision 3).
- **NVD, BACKLOG T-083** (todo): no tool yet, so models cite CVE records by link (Decision 4).

## Validation

A packaged build shows the pinned CWE release in the Weaknesses tab with no environment variables set, and the build
fails if a bundled file's SHA-256 differs from its pin. For CWE, #260 meets both: its second PR test build listed all
969 weaknesses of the pinned CWE 4.20 release with MITRE's notice, the build's smoke test reads the bundled release
under `env -i` (no `$TMODEL_CWE_CATALOG`), and `bin/build-engine` stops when the file's SHA-256 differs from the pin.
CAPEC gets the same check once the build bundles it.
