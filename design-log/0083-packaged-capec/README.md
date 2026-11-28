---
schema: "archdoc/v1"
id: DL-0083
title: "Packaged app: bundle the pinned CAPEC release as the CWE one is (ADR-0014's interim rule)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-28"
updated: "2026-11-28"
record: DL-0083
human_owner: Clovier
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0083: the packaged app bundles the pinned CAPEC release

DL-0082 is #303's, so this entry is DL-0083.

## Question asked

The packaged app ships the library and the pinned CWE release (#260, DL-0063), but not the
pinned CAPEC release: the engine reads CAPEC only from the file `$TMODEL_CAPEC_CATALOG`
names. So in a downloaded app the Attack Patterns tab (#236, #294) has no catalog, and the
AI proposals (#302, #303) answer `ai_unavailable`, since they draw on CAPEC's names and
descriptions. kriishnaa-18's review of #294 left the packaging "to be addressed separately
before the final release". Clovier took it on for the demo.

## What was produced

- `bin/build-engine`: a CAPEC block after the CWE one, doing what it does for the
  library's `capec` record: the file `$TMODEL_CAPEC_CATALOG` names if set, else a download
  from the record's URL (three tries, streamed, refused past the engine's own size limit),
  refused unless its SHA-256 matches the pin, then bundled as `catalogs/capec_v3.9.xml`. A
  new smoke step, before the CWE one, runs `attack-patterns --limit 1` in the built engine
  with no environment.
- `engine/engine/load/capec.py`: `configured_catalog(url)` finds a packaged engine's copy
  below `_MEIPASS/catalogs/`, named by the URL's last segment, exactly as `cwe.py` does;
  the variable still wins, and a source checkout never looks for a bundled copy.
- `engine/engine/core.py`: the CAPEC lookup passes the pinned URL.
- Tests: four in `tests/test_load_capec.py` (the bundled copy is found, a missing one is
  none, a source checkout never looks, the variable wins), each failing on main's code,
  and `test_relocated_engine_reads_bundled_capec_release_without_checkout` in
  `tests/test_packaging.py`, which runs against a built engine, as in the desktop CI job.

## The rule this follows

DEC-008 (how tmodel integrates external catalogs) is open, and the sponsor decides it.
ADR-0014 (proposed, #261) records the team's interim rule until then: MITRE's CWE and
CAPEC are read from pinned copies checked by SHA-256 and shipped with the app, never
through live lookups. #260 bundled CWE under that rule; this bundles CAPEC under the same
rule and decides nothing about DEC-008. If the sponsor decides otherwise, both go
together. ADR-0014's line "CAPEC is not bundled yet" changes once this merges.

## How it was checked

- The build script's CAPEC block, run on its own (no PyInstaller) with the variable
  naming the pinned file: it bundled `capec_v3.9.xml` (3,849,998 bytes) with its pinned
  digest, and refused a copy that does not match the pin, naming both digests and bundling
  nothing. `bash -n bin/build-engine` passes.
- Merges, checked with `git merge-tree` against today's main: this merges cleanly with
  #262 (the CWE 4.21 pin), #291 and #301, each of which changes `bin/build-engine`, and
  after #301 merged. #262 conflicts with #291 and #301 by itself, in neighbouring lines of
  the smoke steps; that is theirs to settle.
- `tests/test_load_capec.py`, `tests/test_attack_pattern_table.py` and
  `tests/test_packaging.py`: 100 passed, 9 skipped (the packaging tests wait for a built
  engine). The four new loader tests fail on main.
- `tmodel attack-patterns --limit 1 --in-process --json` reports `total` 615 for CAPEC 3.9,
  the key the new smoke step reads.
- Not run here: `bin/build-engine` itself, which builds a virtual environment and
  downloads its packages. The desktop CI job runs it and then `tests/test_packaging.py`.

## What a human accepted

- Clovier, 2026-11-28: took on the packaged app's two blockers for the demo ("ill do it,
  lets get started"), this one and the launcher's switches. The code and the wording are
  Claude Code's draft until the pull request review accepts them.

## What was rejected, and why

- **Fetching CAPEC at first launch:** a live lookup, which ADR-0014's interim rule rules
  out, and a first launch that fails offline.
- **One loop for both releases in the build script.** It was the first draft: it kept the
  two releases' checks the same, but it rewrote the CWE block that #262 changes, so it
  conflicted with #262, #291 and #301. The CAPEC block repeats the CWE one instead, and the
  smoke step sits before the CWE one, away from where #291 and #301 add theirs.

## Follow-ups

- ADR-0014 (#261): update "CAPEC is not bundled yet".
- The launcher's switches (`--enable-import`, `--projects`, `--enable-ai`): a separate
  change, after #291, #297 and #303 merge.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass
on the files this change touches.
