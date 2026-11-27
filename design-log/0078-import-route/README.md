---
schema: "archdoc/v1"
id: DL-0078
title: "Import New Product: the engine route that runs tmodel import-sbom for the app (#287)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
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
  report as text, the counts, every warning, the settled platform, the product (the image's
  repository) and a suggested name. Nothing is written to disk. The app then starts a project
  from the model through the host (#288: the host saves the text, opens it with openFile and
  creates the project from it), and the model becomes the project's `original.yaml`, so the
  model's header names that file.
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
- `engine/tests/test_import_route.py`: 43 tests on a real local server, and 7 in
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
  lists cannot make it take many times its size. The count covers file names too, so a file
  name with more than about 55 brackets and commas in all is refused.
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

## How it was checked

- `engine/tests/test_import_route.py` (43 tests):
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
