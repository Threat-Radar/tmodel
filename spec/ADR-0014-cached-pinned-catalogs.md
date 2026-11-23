---
schema: "archdoc/v1"
id: ADR-0014
title: "External catalogs as a cached pinned mirror (accepts DEC-008)"
short_title: "Cached pinned catalogs (DEC-008)"
description: "Decision (2026-11-22): tmodel reads MITRE's CWE and CAPEC, and NIST's NVD records, from pinned copies checked by SHA-256 and shipped with the app, never through live lookups; a new release arrives only by a reviewed pull request."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-11-22"
updated: "2026-11-22"
decision_makers:
  - role: student
    id: Clovier
reviewers:
  - role: drafting-agent
    id: claude-code
    kind: ai_agent
needs_review: false
reviewed: false
canonical_path: spec/ADR-0014-cached-pinned-catalogs.md
accepts: DEC-008
---

# ADR-0014: External catalogs as a cached pinned mirror (accepts DEC-008)

## Status

**Accepted** on 2026-11-22 by @Clovier, who proposed and decided it the same day and will tell the sponsor (@nymble).
It accepts DEC-008 (ARCH-0001, DECISIONS-0001). The sources and the choices behind it are in DL-0064.

## Context

- **The decision.** DEC-008 asks how tmodel integrates CWE and NVD: "live lookup vs cached mirror; how automation
  runs" (ARCH-0001). R-010 asks to "Map Weakness→CWE and Vulnerability→CVE, with automated NVD lookup (DEC-008)."
- **Offline is a requirement.** A-043 (APP-0001): the app "works without network for the core loop (ingest → graph →
  review); external lookups (NVD/CWE) may be cached (DEC-008)". PLAN-0002 adds that no cloud services are required.
- **The team's lean.** DECISIONS-0001 records "leaning cached mirror per A-043", and PLAN-0004 Q-07 proposes a
  "Cached pinned mirror".
- **What is built.** The library pins one release of each MITRE catalog by URL and SHA-256: CWE 4.20
  (`cwec_v4.20.xml.zip`, `3976f599…`) and CAPEC 3.9 (`capec_v3.9.xml`, `70279a2d…`). The engine reads the CWE file that
  `$TMODEL_CWE_CATALOG` names and refuses any file whose digest differs from the pin (#233); the CAPEC import in #245
  works the same way with `$TMODEL_CAPEC_CATALOG`. Whether that copy is "bundled, cached or fetched at install is
  DEC-008, still open" (`engine/engine/load/cwe.py`), so the downloaded app's Weaknesses tab cannot work yet (#259).
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
   steps (download, digest, report) and open that pull request.
4. **NVD the same way.** CVE records are pinned copies too: a tool fetches the records a model needs, by CVE id, and
   stores each with its digest for review. That is how R-010's automated NVD lookup runs, without live calls from the
   app. The tool is BACKLOG T-083; until it exists, models cite CVE records by link, as `pv-03` does for
   CVE-2015-9235.

## Alternatives considered

- **Live lookups from the app** (NVD's API, MITRE's sites): always current, but it breaks A-043's offline loop, the
  same model can give different results from one day to the next, and it depends on outside services being reachable.
- **A cached copy fetched at install or on first use:** a smaller download, but it needs the network once and adds a
  way for the first launch to fail. The pinned files are small: 1.9 MB for CWE 4.20 (zipped) and 3.7 MB for CAPEC 3.9.
- **User-supplied files only** (today's environment variables): no change to the build, but the Weaknesses tab stays
  broken for anyone who downloads the app.

## Consequences

- #259's catalog half proceeds: the build fetches, checks and bundles the pinned CWE file, and CAPEC's once #245
  merges, with MITRE's notices.
- ARCH-0001's status banner and DEC table and DECISIONS-0001's row point here; the docstring in
  `engine/engine/load/cwe.py` changes with #259's catalog half.
- Updating a catalog becomes a routine pull request: change the library pin, rebuild, review.
- Not decided here: weakness ids and catalog keys (the other half of PLAN-0004 Q-07), and which CWE views are
  imported (#61).

## Validation

Once #259's catalog half lands, a packaged build shows the pinned CWE release in the Weaknesses tab with no environment variables
set, and the build fails if a bundled file's SHA-256 differs from its pin.
