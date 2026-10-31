---
schema: "archdoc/v1"
id: DL-0029
title: "Library loader: read the pinned library's records into typed objects, and serve them (#60, #138, #139, #140, #141)"
type: process
status: draft
version: "0.3.2"
date: "2026-10-29"
updated: "2026-10-30"
record: DL-0029
bears_on: [DEC-004, DEC-011]
defers_to: ARCH-0001
---

# DL-0029: the library loader

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, the Data lane owner, working with Claude Code.

## Question asked

#60 (PLAN-0002 §4 B1, backlog T-207) asks the engine to read the library records, read-only, and expose them as typed objects. Two sub-issues cover the first steps:

- **#138** asks for a design note before any code: which library files are read, which typed objects come out, the read-only and deterministic-rebuild rules, where the code lives, and how records reach the store façade (#65) and the table views (#58).
- **#139** asks to parse every record in the pinned library into typed Python objects. Every record either loads or fails with an error that names its file. The output is the same for the same input, and there are unit tests on real records of several types.

The SOW's November 5th milestone (M3, the demo floor) starts with "library in engine", so this is on the critical path.

## The design (#138)

### What it reads

The loader reads one library checkout. By default that is the `library/` submodule at the commit this repo pins, which is `a28a013` with 550 records today. For each record it reads `records/<shelf>/<id>/record.yaml`, the current version of one document line. That is the same set of files the library's own `bin/validate` checks.

It also notes two things about each record folder without reading their contents: whether `summary.md` exists, and which superseded versions are kept under `versions/`. It never reads `.cache/`, never sees a PDF (the library commits none), and ignores the generated `exports/` and `index/` folders.

### What comes out

`load_library(root)` returns a `Library`: every record as a `LibraryRecord`, sorted by id, plus a digest of what was read.

A `LibraryRecord` carries the fields a table or a graph needs:

| Group | Fields |
|---|---|
| Identity | `id`, `body` (the shelf), `type`, `title`, `short_title`, `status`, `path` |
| Bibliographic | `authors`, `date`, `version`, `publisher`, `maturity`, `identifiers` (doi, rfc, iso, url and so on) |
| The document | `content`: its link, digest, retrieval date, media type and page count |
| Labels | `topic`, `tags`, `bears_on`, `owner`, `confidence`, `applicability`, `usefulness` |
| Links | `relations` (see_also, supersedes, part_of and the other typed relations), `cites`, `duplicate_of` |
| Extraction | `artifacts` (each with whether a person reviewed it), `profile` (`full` means a complete extraction) |
| Folder | `summary` (its path, if present), `versions` (the superseded versions' names) |

Everything else in the file stays in `raw`, a read-only copy of the whole record as written. Nothing is lost, so a later consumer can read a field this version does not type.

These are the engine's read models of library records. They are not classes in the tmodel schema: the schema refers to a library record by id only (the `source_ref` slot), and the loader keeps it that way.

### Rules

- **Read-only.** Files are only opened for reading. A test loads a copy whose files and folders are all read-only and checks that nothing changed.
- **Deterministic.** The same files give the same objects in the same order. Records are sorted by id and every list keeps the order the file gives. `Library.digest` is a SHA-256 over every record file's path and bytes, so the store can tell whether a rebuild is needed (ADR-0004 and ADR-0008: files in git are the truth, and the working store is a rebuildable copy).
- **Values kept as written.** Records are read with PyYAML's `BaseLoader`, which keeps every value as the text in the file. The default loader guesses numbers and dates, and a scan of all 550 records found two arXiv ids and 99 RFC numbers it would turn into numbers. As a number, the arXiv id 2409.06390 would lose its last digit and the version 1.10 would become 1.1. Only `content.local` and `content.pages` are converted, and a bad value in either is an error.
- **Never stricter than the library.** The loader checks what `bin/validate` checks about a record's identity: the required fields are present, the id matches its folder and is kebab-case, and the shelf matches `body`. It adds one rule, that ids are unique across shelves, because the engine looks records up by id and the record schema says ids are globally unique. It does not reject an unknown type, status or relation, so a library update that adds a value does not break the app.
- **Errors name the file.** A broken record raises one `LibraryError` that lists every failing file with its reason, in path order. With `strict=False`, the loader returns the records that did load and lists the failures in `Library.problems`, for a screen that should still open.

### Where it lives

`engine/engine/load/library.py`, next to the example-model loader from #132 (`load/vector.py`), which it does not touch. The tests are in `engine/tests/test_load_library.py`.

### How records reach the store (#65) and the tables (#58)

- **#140** exposes the records through `engine/core.py`, a local API route and a `tmodel library` command, all returning `Library.to_dict()` or a slice of it. The tables get their data only from the engine API, with no business logic in the WebView (APP-0001 A-030).
- **#141** shapes the table feed: one row per record, plus counts by type and status for the filters.
- **#142** hands the `Library` to the store façade. The proposal, open to #65: each record becomes a node keyed `library:<record-id>`, the same form a Requirement's `source_ref` uses. Each relation, and each citation that names a record id, becomes a typed edge. The store keeps the digest so it rebuilds only when the library changed.

### Open questions

These are posted on the issues they belong to.

- **For #65:** should library records be nodes in the working store with the id `library:<record-id>`? Which links become edges: all nine relation kinds plus `cites`, or a subset? Should the store keep `Library.digest` to decide when to rebuild?
- **For #58:** the library holds documents (standards, papers, specs, datasets), not weaknesses or vulnerabilities. Weakness rows come from the CWE import (#61), and attack patterns later. Is a documents table plus a weakness table enough for November 5th? Which columns come first? Should the API page the list, since all 550 records are about 900 KB of JSON? @kriishnaa-18 answered on 2026-10-30; see "What a human accepted" under #141.
- **For the sponsor:** CI checks out this repo without its submodules, so the whole-library test is skipped there. Adding `submodules: true` to the engine job in `.github/workflows/app.yml` would run it on every pull request and catch a library pin bump that the loader cannot read. Separately, the packaged app (#124) needs the library too: should a snapshot be bundled at build time, or should the app be pointed at a library folder?

## What was produced

- `engine/engine/load/library.py`: `load_library`, `Library`, `LibraryRecord`, `LibraryError`, and small value types for content, citations, implementations, artifacts and the usefulness verdict.
- `engine/tests/test_load_library.py`: 30 tests. They cover real records of seven types and four statuses, values kept as written, same input and same output, read-only loading, eleven kinds of broken record (each error names its file), duplicate ids across shelves, and the whole pinned library.
- `engine/tests/fixtures/library/`: byte-for-byte copies of 13 record files from the library at `a28a013`, with a README saying why each is there. CI has no submodule, so these let the record tests run there.
- This entry.

No other engine file changed, so this does not overlap #162, which edits `core.py`, `api/server.py` and `load/vector.py`.

## Method and checks

- All 550 records at the pin load in about 0.6 seconds with no problems. Two loads give equal records, an equal digest and identical JSON.
- The whole engine suite passes: 130 tests, including the 100 that were already there. `ruff check` and `ruff format --check` pass.
- In a copy without the library submodule, as CI runs it, 29 tests pass and the whole-library test skips with a reason that says how to check the submodule out.
- The fixture copies were compared byte for byte with the library and checked for project people's real names. There are none: record owners appear as GitHub ids or the placeholder `S1`.

## Choices made, open to review

- **`BaseLoader` instead of `yaml.safe_load`,** for the reason under "Values kept as written". The cost is that each typed field needs an explicit conversion, and only two need one.
- **Superseded versions are listed, not loaded.** The library schema keeps one record per document line, and `bin/validate` skips `versions/`. Loading them as records would also clash with the parent's id rules.
- **Typed fields plus a read-only `raw` copy,** instead of typing every field. Records also use seven top-level keys that the record schema does not list: `venue`, `license`, `commit`, `media_type`, `pages`, `edition` and `sources_consulted`. Typing every field would make this file a second copy of the library schema to keep in step.
- **`media_type` and `pages` are read only from `content`,** where the record schema puts them. 57 records put `media_type` and 52 put `pages` at the top level instead; those values stay in `raw`. The fix belongs in the library repo, not in a fallback here.
- **Read models in the engine, not a new schema class.** The schema aligns with the library by reference only, and `spec/` is the sponsor's.
- **Fixtures for CI, instead of changing CI in this pull request.** `.github/` belongs to the sponsor under CODEOWNERS; the CI change is proposed above as an open question instead.
- **A strict default.** On `main` the library's own CI keeps records valid, so a failure most likely means a pin bump the loader cannot read, and that should be loud. `strict=False` is there for screens.

## What was rejected, and why

Nothing yet.

## What a human accepted

- @paria03 reviewed pull request #186 on 2026-10-29: the loader is well scoped, and the pinned library loads. One finding to fix before approval: two expected failures escaped the per-record error handling and stopped the whole load. One is a page count written with a non-ASCII digit, since "²" passes `str.isdigit()` but `int()` rejects it. The other is a `versions/` folder the loader cannot read. Both now fail only their own record, with its file named, and regression tests cover each in strict and partial mode. Other exceptions still propagate, as the review asked.
- @nymble merged pull request #186 on 2026-10-29.

## #140: the records through core, the API and the CLI

### Question asked

#140 asks for "the same façade pattern as the engine skeleton and #132: a core function, a local API route and a `tmodel` CLI command over the loaded records". It is done when core, the API and the CLI return the same results (parity tests), bad input gets a 400 with a clear message and never a dropped connection, and records can be filtered by type, topic and status. The student asked to start it on 2026-10-29, while #139 was in review in pull request #186, so this branch starts from #139's.

### What was produced

- `core.library_records(filters)`: the records whose `type`, `topic` and `status` equal the given values, with the library's root, digest, record count and the files that failed to load.
- `GET /library` on the local API, with the filters as query parameters. An unknown or empty filter gets a 400 with a message. No library gets a 503 (`core.Unavailable`) with a message that says how to provide one.
- `tmodel library`, with `--type`, `--topic`, `--status`, `--json`, `--in-process` and `--url`: a table of id, type, status and title, or the API's JSON.
- In `engine/engine/load/library.py`: `configured_root()`, which is `$TMODEL_LIBRARY` or else the pinned submodule, and `cached_library()`.
- `engine/tests/test_library_surface.py`: 44 tests, 5 of them added after review (0.3.2).
- `CONTRIBUTING.md` §10: one paragraph on the library the engine serves.

### Method and checks

- On the pinned library, the API lists 99 RFCs. The first request takes about 0.65 seconds and a repeated one about 0.03 seconds. All 550 records come to about 890 KB of JSON.
- Engine suite: 169 passed, the 130 from #139's branch and 39 new. `ruff check` and `ruff format --check` are clean. Without the submodule, as CI runs, 67 library tests pass and the 2 that need the pinned library skip.
- After @kriishnaa-18's review of #188 (0.3.2): 6 new tests, 5 in `test_library_surface.py` and 1 in `test_load_library.py`. On Python 3.12 all 6 fail on the code before the fix (on 3.13 the symlink loop already gave a 503). With the fix, the engine suite has 234 passed and 3 skipped on Python 3.12 and 3.13, and `ruff` is clean.

### Choices made, open to review

- **One loaded copy, checked on every request.** Each call hashes every record file and checks which summaries and old versions exist, and reloads only if something was added, removed or edited. A pulled or edited library shows up on the next request without restarting the engine. The first version compared sizes and modification times, which an edit can keep (`cp -p` and `rsync -t` do), so @kriishnaa-18's review of #188 found that a same-size edit could go unseen. On the pinned library, hashing moved a repeated request from about 0.023 to 0.029 seconds.
- **Broken records do not stop the screen.** The API answers 200 with the records that loaded and lists the failures under `library.problems`. The CLI prints them and exits 1 with a warning. A missing library is different: a 503, because the caller cannot fix it.
- **503 instead of 400 for a missing library.** The server turns every ValueError into a 400, and `LibraryError` is a ValueError, so core raises `Unavailable` instead, and the server answers 503. A path the system cannot look at counts as missing too: a folder inside one without read permission, a name that is too long, a symlink loop, or `~name` for a user that does not exist. Before 0.3.2 these gave a 500, as @kriishnaa-18's review found.
- **Filters match exactly and take one value each.** The server keeps the last value of a repeated parameter, as it does for `/attack-paths`, so `?type=rfc&type=draft` filters on `draft`. Several values per filter, or matching that ignores case, can come with #141 if the table views need them.
- **Every match comes back whole.** The response carries each record's full `to_dict()`. Shaping rows for the tables, with fewer fields, counts for filter menus or paging, is #141's job, once @kriishnaa-18 answers on #58.
- **Placed apart from #162 and #155.** The core function sits after `health()` and the CLI command after `paths`, away from the lines that #162 and #155 change in the same files. That kept the overlap small but not empty: after #162 merged on 2026-10-30, merging `main` conflicted in the imports and constants at the top of `core.py` and in one comment in `api/server.py`. Both sides were kept, and all six routes are served.
- **The CLI catches ValueError,** which includes `GraphError`, so `--type ""` prints one error line instead of a traceback.

### Open

- How the packaged app finds a library (#124; asked on #60).

### What a human accepted

- The student asked to start #140 (2026-10-29).
- @kriishnaa-18 reviewed #188 at `9c6a0ad`, against `main` with #162 merged: the routes match the contract agreed for #58, all 550 pinned records load, and `/graph` and `/attack-paths` still work. The review approved the pull request and asked for two nonblocking fixes before merging, the cache check and the 500s above; both were made in 0.3.2.
- Pending: approval of the commit with those fixes.

## #141: the data feed for the table views

### Question asked

#141 asks to "agree the JSON shape and the sort and filter parameters that the table views need (#58, PLAN-0002 B2, T-201), and provide a sample fixture the GUI can start from". It is done when the shape is agreed on #58, a sample fixture is committed, and the API supports the agreed parameters. @kriishnaa-18 had not yet answered the questions posted on #58, so this builds a concrete proposal to agree on. The student asked to start it on 2026-10-29.

### What was produced

- `core.library_table(query)` and `GET /library/table`: one row per record, with `type`, `topic`, `status` and `id` filters, `search`, `sort`, `order`, `limit` and `offset`. Each row has id, title, short title, type, shelf, status, maturity, date, publisher, topic, tags, url, artifact counts and the extraction profile. `facets` counts each type, status and topic in the whole library, for filter menus.
- An `id` filter on `/library` (#140), so a details view can fetch one record in full.
- `apps/desktop/src/fixtures/library-table.json`, the engine's answer over the 12 fixture records, with a README.
- `engine/tests/test_library_table.py`: 39 tests, including one that fails when the fixture no longer matches the engine's answer.

### Method and checks

- Each expected order in the tests was checked against the fixture records' fields by hand: blanks sort last in both orders, ties keep id order, titles sort without regard to case.
- On the fixture library, the whole answer is about 8 KB. On the pinned library, the 550 rows come to about 240 KB, against about 890 KB from `/library`, because rows leave out each record's longer fields.
- Engine suite: 208 passed, 39 of them new; `ruff check` and `ruff format --check` are clean.
- After #186 merged, the branch was moved onto `main`, which brings in the loader fix from @paria03's review. There the engine suite has 214 passed and 3 skipped (the packaged-engine tests, which need a built engine), and `ruff` is clean.

### Choices made, open to review

- **A separate route for rows.** `/library` keeps returning whole records (#140), and `/library/table` returns what a table shows. The table can change for the GUI without changing what the CLI and other callers get.
- **The engine sorts, filters, searches and pages.** #58 asks for no business logic in the WebView (APP-0001 A-030), so the table sends parameters and shows the rows it gets back.
- **Facets count the whole library, not the current match.** A filter menu then lists every value with a stable count. Counting within the current match is easy to add if #58 wants it.
- **No local path in the answer.** The table leaves out the library's root folder, so the fixture is the same on every machine and can be compared exactly.
- **No new CLI command.** APP-0001 makes the CLI optional (A-060), and `tmodel library` already lists and filters the records; the table shape is for the GUI.
- **One generated fixture,** checked by a test, instead of hand-written sample data that could drift from the engine.
- **Parameter errors are 400s with a message,** and `limit` and `offset` accept ASCII digits only, the same rule the loader now applies to page counts after @paria03's review of #186.

### Open

- Paging is supported but off by default, since 550 rows are small enough to send at once.
- Tables for one product's threats, attacks and risk will likely need their own engine data contract, as @kriishnaa-18 noted on #58. This feed covers the library's documents.

### What a human accepted

- The student asked to start #141 (2026-10-29).
- @kriishnaa-18 agreed to the shape on #58 on 2026-10-30, for the frontend. The proposed fields cover what the table needs: title, type, status, topic, date and the reviewed-artifact information show first, and the rest go in a details view. All 550 rows can come in one response, with `limit` and `offset` kept for later. Search, sorting, filters and facets are enough, with no multi-select filters for now. The documents table comes first, and a weakness table follows if the CWE import (#61) is ready in time; whether that is enough for November 5th is still to be confirmed with @nymble. This meets #141's first done item.
- The same review of #188 found that `/library/table` behaves as agreed: search, filters, sorting, paging, facets and full-record retrieval.
- Pending: approval of #188 with the review fixes (see #140).

