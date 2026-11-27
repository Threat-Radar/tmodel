---
schema: "archdoc/v1"
id: DL-0063
title: "The packaged app ships the reference library and the pinned CWE release (#259)"
type: process
status: draft
version: "0.1.2"
date: "2026-11-22"
updated: "2026-11-23"
record: DL-0063
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0063: The packaged app ships the reference library and the pinned CWE release (#259)

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
| `bin/build-engine` | Copies the files the loader reads (its `RECORD_GLOB` and `NOTED_GLOBS`) from `library/` into the sidecar, stops if the submodule is missing, and checks that the built executable lists the library; downloads the CWE release the library pins, refuses it unless its SHA-256 matches, bundles it under `catalogs/`, and checks that the built executable reads it |
| `engine/engine/load/cwe.py`, `engine/engine/core.py` | A packaged engine reads the bundled CWE release; `$TMODEL_CWE_CATALOG` still wins |
| `apps/desktop/THIRD_PARTY_NOTICES.md` | MITRE's copyright designation and license for the bundled CWE release |
| `engine/engine/load/library.py` | A packaged (frozen) engine serves the bundled copy below `_MEIPASS`; `$TMODEL_LIBRARY` still wins |
| `.github/workflows/app.yml`, `release.yml` | The desktop and release builds check out the library submodule |
| `engine/tests/test_library_surface.py`, `engine/tests/test_load_cwe.py`, `engine/tests/test_packaging.py` | Where the engine finds the library and the CWE release, and the relocated executable listing the library and reading the release with no checkout |
| `CONTRIBUTING.md` | The sidecar bundles the library's records |

## Choices

- **Bundled like the example models.** The records are PyInstaller data below `_MEIPASS`, as `spec/vectors` already
  is, so the CLI and the server find them the same way and no Rust change is needed.
- **Only what the loader reads.** That is about 2.7 MB of `record.yaml` and `summary.md` files out of a 29 MB
  `records/` folder. Distilled files, such as a licensed standard's `requirements.yaml`, stay out, so no licensed
  wording ships in the app.
- **Fail the build, not the app.** `bin/build-engine` stops without the submodule, and its smoke test fails on an
  empty library or on a record that does not load.

## The CWE release (ADR-0014)

- The first commit left the catalogs alone, because how the app gets them is DEC-008. ADR-0014 (#261) proposes a
  cached pinned mirror, shipped with the app; the sponsor decides DEC-008, and until then the app ships the pinned
  copies. The second commit does that for CWE: the build downloads the release the library pins, refuses it unless
  its SHA-256 matches, and bundles it; a packaged engine reads it when `$TMODEL_CWE_CATALOG` is not set; and the
  app's third-party notices carry MITRE's copyright designation and license, as MITRE's terms require.
- CAPEC follows the same way once #245 merges.

## What a human accepted

- @Clovier, 2026-11-22: file #259, put it in Sprint 6 and start on it.
- @Clovier, 2026-11-22: decide DEC-008 in ADR-0014 (#261) and "execute the plan right away".
- @Clovier, 2026-11-23, after #261's review: ADR-0014 goes back to proposed, for the sponsor to decide; meanwhile
  "our team decides to use the fixed/cached copy that ships inside it for now, if newer catalogues release, another
  pr will have to be opened to update the catalogue".

## Options not taken, and why

- **Bundling the CWE release in the first commit:** it would have settled DEC-008 in code, before any ADR; the second
  commit follows ADR-0014 (#261) and the team's working rule instead.
- **The whole `records/` folder:** 29 MB, and it includes distilled source text.
- **Setting `TMODEL_LIBRARY` from the Tauri app:** a Rust change and a resource path for the same result.

## Review changes (2026-11-22)

@kriishnaa-18 reviewed the pull request and asked for one blocking change and suggested one more. Both are done:

1. **A library change now rebuilds the release.** `release.yml` builds `latest-main` on a push to `main` that touches the paths it lists, and `library` was not one of them, so a pull request that only moved the library pin would have left the downloadable app on the old library and CWE release. It now lists `library`, as `app.yml` does.
2. **The CWE download is streamed with a limit.** `bin/build-engine` read the whole response before checking anything. It now reads in 1 MiB pieces and stops once the file passes the engine's own limit for a catalog file (`MAX_FILE_BYTES` in `engine/engine/load/cwe.py`, 256 MiB). A copy that `TMODEL_CWE_CATALOG` names gets its size checked before it is read. Tested by downloading the pinned release, by using a local copy, and, with the limit set to 1,000 bytes, by both stopping with a message and writing nothing.

## Review changes (2026-11-23)

After @paria03's review of #261, ADR-0014 went back to proposed (DL-0064). This record now says that ADR-0014
proposes the cached pinned mirror and the sponsor decides DEC-008, and it records the team's working rule meanwhile.

## Next steps

- Merge #261 (ADR-0014) before this PR.
- If the sponsor decides DEC-008 another way, a later pull request changes how the app gets the release.
- CAPEC, once #245 merges.
- The desktop CI job runs the packaging tests against the built app.
