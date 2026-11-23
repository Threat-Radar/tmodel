---
schema: "archdoc/v1"
id: DL-0063
title: "The packaged app ships the reference library (#259)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-22"
updated: "2026-11-22"
record: DL-0063
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0063: The packaged app ships the reference library (#259)

AI-assisted design record (per `CLAUDE.md`), drafted by Claude Code for @Clovier.

## Question asked

In #258's PR test build, the Library and Weaknesses tabs failed with "no library at …/library". #259 asks for both
tabs to work in the .dmg and in PR test builds, with no environment variables set.

## What was found

- `configured_root()` in `engine/engine/load/library.py` served `$TMODEL_LIBRARY` or the repo's `library/` submodule.
  A packaged engine has neither, and the docstring left "how the app provides a library" to #124.
- `bin/build-engine` bundled only `spec/vectors` and `MAP-0001.yaml`, and neither the desktop job in `app.yml` nor
  `release.yml` checked out the library submodule (only the browser-preview job did).
- The Weaknesses tab needs the library (for the pinned CWE digest) and the CWE release file, which the engine reads
  from `$TMODEL_CWE_CATALOG`. That function's docstring says whether the catalog is "bundled, cached or fetched at
  install is DEC-008, still open".

## What was produced

| File | Change |
|---|---|
| `bin/build-engine` | Copies the files the loader reads (its `RECORD_GLOB` and `NOTED_GLOBS`) from `library/` into the sidecar, stops if the submodule is missing, and checks that the built executable lists the library |
| `engine/engine/load/library.py` | A packaged (frozen) engine serves the bundled copy below `_MEIPASS`; `$TMODEL_LIBRARY` still wins |
| `.github/workflows/app.yml`, `release.yml` | The desktop and release builds check out the library submodule |
| `engine/tests/test_library_surface.py`, `engine/tests/test_packaging.py` | The three library-root cases, and the relocated executable listing the pinned library with no checkout |
| `CONTRIBUTING.md` | The sidecar bundles the library's records |

## Choices

- **Bundled like the example models.** The records are PyInstaller data below `_MEIPASS`, as `spec/vectors` already
  is, so the CLI and the server find them the same way and no Rust change is needed.
- **Only what the loader reads.** That is about 2.7 MB of `record.yaml` and `summary.md` files out of a 29 MB
  `records/` folder. Distilled files, such as a licensed standard's `requirements.yaml`, stay out, so no licensed
  wording ships in the app.
- **Fail the build, not the app.** `bin/build-engine` stops without the submodule, and its smoke test fails on an
  empty library or on a record that does not load.

## What stays open

- **The CWE and CAPEC catalogs (DEC-008).** Bundling, caching or fetching the pinned releases would decide DEC-008,
  which is open (DECISIONS-0001 notes a lean toward a cached mirror; PLAN-0004 Q-07 proposes a cached pinned mirror).
  Until it is decided, the packaged app's Weaknesses tab reads the catalog from `$TMODEL_CWE_CATALOG` as before and
  says so when it is unset.

## What a human accepted

- @Clovier, 2026-11-22: file #259, put it in Sprint 6 and start on it.

## Options not taken, and why

- **Bundling the CWE release now:** it would decide DEC-008 in code, which `CLAUDE.md` rules out until an ADR
  accepts it.
- **The whole `records/` folder:** 29 MB, and it includes distilled source text.
- **Setting `TMODEL_LIBRARY` from the Tauri app:** a Rust change and a resource path for the same result.

## Next steps

- @Clovier decides how #259's catalog part proceeds, given DEC-008.
- The desktop CI job runs the new packaging test against the built app.
