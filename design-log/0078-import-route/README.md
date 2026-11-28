---
schema: "archdoc/v1"
id: DL-0078
title: "Import New Product: the engine route that runs tmodel import-sbom for the app (#287)"
type: process
status: draft
version: "0.3.0"
date: "2026-11-27"
updated: "2026-11-28"
record: DL-0078
human_owner: Clovier
bears_on: [ADR-0003]
defers_to: ARCH-0001
---

# DL-0078: the import route

## Question asked

The team's design for saving and reopening threat models gives the app three entry points:
Import New Product, Open Existing Threat Model and Open Existing Project. Import New Product
needs the SBOM import (#257, #268, DL-0068), which so far ran only as the command
`tmodel import-sbom`. #287 lists an upload screen in the app as a next step. What should the
engine offer that screen?

## What was produced

- `engine/engine/api/import_route.py`: `POST /import/sbom`. The request carries the bytes of
  the SBOM and, if the user has one, of a Grype scan of the same image, each in base64 with
  its file name, and an optional platform (`OS/ARCH[/VARIANT]`). The engine runs
  `import_sbom.build` on those bytes in memory and answers with the model and the import
  report as text, the counts (every Assertion, and each kind of them), every warning, the
  settled platform, the product (the image's repository) and a suggested name. Nothing is
  written to disk. The app then starts a project from the model through the host (#288: the
  host saves the text, opens it with openFile and creates the project from it), and the model
  becomes the project's `original.yaml`, so the model's header names that file.
- `engine/engine/import_sbom.py`: `Upload`, a file's name and bytes. `build` takes one in place
  of a path, with the same checks, and gives the same model, report and refusals for the same
  name and bytes. `ImportResult` also carries `product` and `platform`.
- `engine/engine/api/server.py`: the route, its CORS preflight for the app's webview, and the
  checks before an import runs: a loopback host, the app's origins (or no origin, for a local
  client), a JSON body, one Content-Length within the limit, the whole body within 30
  seconds, and one import at a time.
- `engine/engine/cli.py`: `tmodel serve --enable-import`. The route is off by default, so the
  normal desktop launch stays read-only; `make_server(import_enabled=True)` is the same switch.
  The importer's `-o` help now suggests an `im-` file name (#281).
- `design-log/0068-sbom-import/README.md`: its line saying the API has no route to the import
  now points here.
- `engine/tests/test_import_route.py`: 68 tests, 54 of them on a real local server, and 7 in
  `engine/tests/test_import_sbom.py` for `Upload`.
- This entry.

## Choices open to review

- **Bytes in, text out.** The app sends each file's exact bytes in base64, not its text, so the
  model records each file's own SHA-256 and the route refuses exactly what the command line
  refuses: a file that is not UTF-8, a key repeated in one object, NaN, nesting too deep, or a
  file over 64 MiB (`MAX_INPUT_BYTES`).
- **In memory.** Nothing touches the disk. There is no temporary folder to clean up if the
  engine stops during an import, and two files whose names differ only in case, which a Mac's
  disk would treat as one file, are both read. A file name is reduced to a plain base name
  (folders dropped; only letters, digits, dots, dashes and underscores kept), and no local path
  crosses the API in either direction.
- **No project is made here.** The route returns the model; making the project, its folder and
  its versions belongs to #288's workspace. So this change does not depend on #288, and the app
  can show the model and its warnings before the user commits to a project.
- **Errors follow the review operations of #289** (the `{"error": {"code", "message"}}` table
  in `engine/HUMAN_REVIEW.md` on #291's branch): a malformed request is `422
  validation_error`, naming the field when there is one; a foreign host or origin is `403
  permission_denied`; another path is `404 not_found`; an unexpected failure is `500
  internal_error`, with no path and no traceback. The route adds four of its own: `422
  import_refused` (the importer's message and its notes), `503 not_enabled`, `503 busy` and
  `408 request_timeout`.
- **A strict envelope.** Only `sbom`, `scan` and `platform`; a file is only its `name` and
  `base64`; a repeated key or NaN is refused. Base64 has no brackets or commas, so a real
  request holds only a few. The body may hold at most 64 of them in all, counted before
  parsing, so parsing makes at most a few dozen values, and a crafted body of nested or long
  lists cannot make it take many times its size. Only those outside strings count (from
  kriishnaa-18's review, below), so a file name or platform may hold any number of them.
- **One import at a time.** An import can hold hundreds of MB. A second waits up to 60 seconds
  for the first, then is answered `busy`. A client that stalls holds the slot until its
  30-second deadline, so a local process could keep the route busy.
- **The preflight answers the app's origins whether or not the route is enabled**, so that the
  app reads `not_enabled` instead of a failed request.
- **A refusal reaches a client that is still sending.** A client sends the whole body before it
  reads the answer, so `not_enabled`, `busy` and a wrong content type are answered only after
  the engine has read and discarded the body; otherwise the client would see the connection
  close instead.
- **Limits that remain.** A request with no usable Content-Length, or over the limit, is
  refused before its body is read, so a client sending it may see the connection close instead
  of the refusal. The app's Import New Product screen is to check each file's size before it
  sends (the contract given to #290's screen says so). The body has one 30-second deadline; the
  headers before it have none, on every route of this server, a gap that predates this change.
  Only the app's origins and local processes can reach the route.
- **The switch.** One flag now. When #288's workspace and #289's review operations land, the
  host may enable all three together, and the route may then take #289's session as the review
  operations do; that is a choice for then.

## With #288's project folders on main (2026-11-27)

#298 (#288) merged first, so this change took main in (`b38074f`). `serve()` and `tmodel serve`
conflicted as text, each adding an option, and both are kept: the workspace routes wrap this
route's handler (`install_workspace_routes`) and pass every other path on to it. A test of the
two together then found what the text merge could not: the workspace routes and this handler
each had a private `_read_body`, with different arguments, and the workspace one, ahead of this
handler in the class, replaced it, so with project folders on every import failed with 500. The
workspace helper is now `_read_workspace_body`. Tests, in `engine/tests/test_import_route.py`:

- `test_the_import_route_answers_beside_the_project_routes`: an import, its preflight and a
  project route on one server. On `b38074f` the import answered 500.
- `test_the_workspace_routes_share_no_helper_with_this_handler`: the two may share only
  `do_GET`, `do_POST` and `do_OPTIONS`, which the workspace routes pass on. It failed on
  `b38074f`.
- `test_the_serve_command_passes_both_switches`: `--enable-import` and `--projects` reach
  `serve()`, which takes both by name only (`test_serve_takes_its_switches_by_name_only`): by
  position, a token meant for `host_token` would have turned importing on instead.

An independent review of `d4fb812` found one more thing, also on main's workspace routes: a
client that reset the connection part way through its body got an answer written into the
closed connection, which raised again and printed a traceback (a 500 from this route, a 400
from the workspace routes). The engine's handler now ends such a connection quietly on every
route (`EngineHandler.handle`), and this route stops reading without answering. Test:
`test_a_client_that_resets_part_way_through_its_body_is_let_go_quietly`, for this route and a
workspace route; both cases failed on `d4fb812`.

## kriishnaa-18's review (2026-11-28)

kriishnaa-18 ran the route with the source engine and the packaged macOS engine, and asked for
one change, with one smaller point. CodeQL flagged a third.

- **The total of Assertions.** `counts` gave `match_assertions` and `cwe_assertions` but not
  their total, so #296's screen, which shows `components`, `vulnerabilities`, `weaknesses` and
  `assertions` first, showed "Not reported". `counts.assertions` is now the total, beside both
  parts. Each match and each CWE link writes one Assertion (`_match_assertions`,
  `_cwe_assertions`), so the sum is every Assertion the model holds, and the import report
  uses the same count. Tests: `test_the_counts_give_every_assertion_and_both_kinds`, 45 with
  the alpine scan and 0 without, each checked against the model's own `assertions` list; the
  importer's exact counts test in `test_import_sbom.py` now includes the total and checks it
  the same way. All three failed before this change.
- **Brackets and commas in names.** A name with 62 commas was refused, because the structure
  count took in strings. Only brackets and commas outside strings count now
  (`import_route.structure`). The count finds the strings with one pattern that never
  backtracks: a string runs to its closing quote, or to the end of the body when it has none,
  where parsing stops too.
  - A simpler pattern, which needs the closing quote, was rejected: it took 4 seconds on a
    40,000-character body of escaped quotes, and its time grows with the square of the length.
  - The pattern's quantifiers are possessive (Python 3.11; the engine needs 3.11 or later).
    Without that, the search keeps a step to go back to for every escape. A second review of
    this change, by another Claude Code agent, found it: 808 MB at its peak for a 9 MB body of
    escaped quotes, and 889 MB for escaped backslashes, about 90 bytes for each byte, so a
    179 MB body would have needed some 16 GB and could freeze the Mac. With possessive
    quantifiers both stay flat, and the counts are the same: the review compared the two
    patterns on 300,000 random texts.
  - A body may hold at most 1,024 quote characters (`MAX_QUOTES`), checked before the strings
    are looked for: a real request has about two dozen, and any its two file names hold. Each
    string found costs a little memory, and a body of bare quotes took 2.3 seconds and 360 MB
    at 36 MB, while the import slot was held.
  - This reads a 179 MB request (two 64 MiB files) in under a second.
  - The body is read as UTF-8 only (RFC 8259 §8.1, and what the app sends), with or without a
    byte order mark, as before. `json` also reads UTF-16 and UTF-32, whose bytes the count
    would not read as parsing does; such a body is now answered "The request body must be
    JSON in UTF-8." So is one with an encoded lone surrogate, which `json` read before and
    which no file name or base64 needs.

  Tests: a name with 62 commas, and one with escaped quotes and brackets, import; five texts
  are counted as parsing reads them; structure after an escaped quote still counts; bodies of
  2 million escaped quotes and of 4 million bare quotes are refused before the strings are
  looked for; the count's memory, traced, stays below the size of 1 MB texts of escaped
  quotes, escaped backslashes and other escapes; UTF-16 and UTF-32 bodies are refused; a byte
  order mark is read past. Each failed before this change, or with the pattern or the quote
  limit put back as they were (the memory tests saw 97 MB), except the escaped-quote
  structure test and the byte order mark, which pass on both and guard against a change.

  The second review also checked, and found right: that the count never sees fewer brackets
  and commas than parsing can reach (the 300,000 texts, against `json`'s own string reader);
  that `counts.assertions` matches the model's `assertions` list in all 437 imports the route
  and importer tests run, and with hand-made scans; the preflight, with the route on and off;
  and that every header built from a request is checked against the list of the app's
  origins.
- **CodeQL's HTTP response splitting alert** on the preflight (`server.py`): it checked one
  read of the `Origin` header and sent a second read. It now reads the header once and sends
  the value it checked, as the workspace routes and the engine's other answers already do.
  Only the app's origins were ever sent back, so no answer changes.

The review's integration requirements are for the integration changes, as it says, and are
listed under Follow-ups.

## How it was checked

- `engine/tests/test_import_route.py` (68 tests; the 17 added for kriishnaa-18's review are
  listed in that section):
  - **Switched off by default:** a POST is answered `503 not_enabled`.
  - **The fixture's answer:** the model and report equal the command line's byte for byte, with
    each file's own digest, and the counts, platform, product and name come back.
  - **The importer's own answers:** a warning (`linux/amd64`) comes back, and so do the
    refusals for a malformed platform and for no platform (null or empty). An SBOM alone
    imports with no vulnerabilities.
  - **Refused requests:**
    - eleven malformed payloads, nine of them naming their field;
    - a body that is not JSON, NaN, and a repeated key;
    - nested brackets and a long flat list, both refused before parsing;
    - a non-JSON content type;
    - a file or a body over the limit, with the same refusal for every file just over it;
    - a foreign host or origin, and an unknown operation.
    A name full of brackets and commas still imports.
  - **Refusals while the client is still sending:** `not_enabled`, `busy` and a wrong content
    type reach a client sending a 2.7 MB body. With the body left unread, the same test fails
    with "Connection reset by peer".
  - **The preflight:** it answers the app's origin with the route on or off, and the app then
    reads `not_enabled`; it refuses other origins and paths.
  - **File names and paths:** names lose their folders, and no path comes back. Two files with
    names that differ only in case, or not at all, are both read.
  - **No disk:** an import succeeds with the importer's file read and every temporary-file call
    made to fail.
  - **Concurrency:** three simultaneous imports return one identical model, and one that cannot
    get the import slot is answered `busy`.
  - **Slow clients:** the body deadline cuts off a body that trickles in, and is measured for
    the whole body rather than for each read; a stalled client is answered `408`.
  - **Failures:** an unexpected failure names no path.
- `engine/tests/test_import_sbom.py`: an `Upload` gives the same `ImportResult` as the files,
  and is refused with the file's own message when it is not UTF-8, not a JSON object, repeats
  a key, holds NaN, nests too deeply or is over the size limit.
- An independent review of this change's first draft, by a second Claude Code agent, found
  nine problems:
  - names differing only in case collided on a Mac's disk;
  - a lone surrogate and deep nesting gave `500`, and a repeated key was accepted;
  - the read timeout applied to each read, not to the whole body;
  - a body over the limit closed the connection unanswered;
  - nothing capped memory or simultaneous imports;
  - a temporary folder was left behind if the engine stopped during an import;
  - error codes differed from #291's for the same cases;
  - the preflight hid `not_enabled`;
  - and some wording.

  Each was reproduced. This version fixes them, or, for the early refusal of an oversized
  request, records the limit above.

  A second pass of the same review found eight of the nine fixed and the ninth recorded, and
  five more problems:
  - refusals were lost for files over about 300 KB;
  - a long flat list slipped past the bracket count;
  - a name with many brackets was refused;
  - a file just over the limit drew two different refusals;
  - and some wording.

  This version fixes them.
- The engine suite, `ruff check`, `ruff format --check`, `bin/validate-archdoc` and
  `git diff --check`.

## What a human accepted

- @Clovier, 2026-11-27: asked for the Import New Product screen to be started ("can you also
  get started on the import screen right now"), as part of the team's design for saving and
  reopening threat models; the wording and code are Claude Code's draft until the pull request
  review accepts them.

## Follow-ups

- The app's Import New Product screen, which calls this route and then #288's project creation.
- One switch for the import route, #288's workspace and #289's review operations, once all three
  have landed.
- A read deadline for request headers, on every route of the server.
- From kriishnaa-18's review, for the integration changes: reconcile `server.py` and `cli.py`
  with #291, keeping the route dispatch, the checks and both switches; the launcher passes
  `--enable-import` with `--projects`; the app checks that the engine on its port is its own
  before sending a file; and the whole native workflow is tested, from importing a product to
  a project, a human review, the risk recalculated and a saved version.
