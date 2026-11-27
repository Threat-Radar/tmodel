---
schema: "archdoc/v1"
id: DL-0080
title: "Import New Product: the app's screen for an SBOM and its scan (#287, #290)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0080
human_owner: Clovier
bears_on: [DL-0068, DL-0077, DL-0078]
defers_to: ARCH-0001
---

# DL-0080: the Import New Product screen

## Question asked

The team's design for saving and reopening threat models gives the home page three entry
points (DL-0077). The first, Import New Product, makes a threat model from a container image's
SBOM and, if the user has one, a vulnerability scan of it. The engine's side is
`POST /import/sbom` (DL-0078, #287), which runs `tmodel import-sbom` on the bytes it is sent and
answers with the model and its report. What should the app's screen do?

## What was produced

All of it is in `apps/desktop/src/`, on top of #290's screens (DL-0077):

- `import-client.ts`: the route's client. It reads each chosen file's bytes, sends them in
  base64 with the file's name and the optional platform, and reads the answer or the error
  envelope, which is #291's.
- `import-screen.ts` and `import-screen.css`: the screen, opened from the home page's Import New
  Product option: an SBOM (required), a scan (optional), a platform (optional) and Import; then
  the result (product, platform, counts and every warning) and "Start a project" through the
  host's step (DL-0077).
- `import-mock.ts`: a stand-in for the route, for the tests and for a Vite development server
  opened with `?projectSource=mock`. Production builds leave it out.
- `fixtures/sbom-import-responses.json`: answers in the route's shape (a success, a success with
  a platform warning, and a refusal), made from the importer's own output for its alpine test
  files, and described in the fixtures README.
- `main.ts`: one import, and the lines in the desktop block that create the screen and hand it
  to the home page.
- `import-client.test.ts` (13 tests) and `import-screen.test.ts` (15 tests).
- This entry.

## Choices open to review

- **Bytes, not text.** The screen reads each file with `arrayBuffer()` and sends it in base64,
  encoded in chunks, never through `text()`. The engine therefore sees the file's exact bytes,
  records the file's own digest, and refuses what the command line refuses.
- **Checked before reading.** Each file is checked against the importer's 64 MiB limit before
  it is read. The engine refuses a larger request before reading it, which a browser may report
  only as a failed request, so the screen says so first.
- **One import at a time.** Import is disabled while one runs, Back cancels it and ignores its
  late answer, and an empty platform is sent as null.
- **A refusal keeps the input.** The chosen files stay. The importer's message and every note
  are shown as the importer words them, and a platform the importer's text suggests is offered
  for the platform field. A `validation_error` marks the field it names, `not_enabled` keeps the
  screen disabled and says importing is not available, and `busy` and `request_timeout` allow a
  retry.
- **No Authorization header.** The route's contract names none: it answers only the app's
  origins and local processes, and writes nothing.
- **A project from the result** goes through the host's step with the model's text and the name
  the user gives (DL-0077's `create-project` from `{model_text, name}`).

## What is still pending

- **The engine route** is in the import-route pull request (DL-0078), stacked on #268's
  importer. Until both merge, the engine has no `POST /import/sbom`, and the screen shows that
  the import failed.
- **The host's step** that saves the model's text and starts a project from it (DL-0077).
- **Imported projects cannot be shown yet:** #289's refreshModel needs the reviewer's Party in
  the model, and an imported model has none (DL-0077).

## How it was checked

- `import-client.test.ts` and `import-screen.test.ts` (28 tests): the request holds only the
  three fields, with each file's exact bytes in base64, including a file larger than one chunk;
  the importer's real answers and refusals are read and shown exactly, with their notes and the
  platform they suggest; an unreachable engine and an unreadable answer are reported; the
  screen replaces the home screen and returns focus to it; every field is labelled; a file's name
  and size show, never a path, and a file over the limit is refused before it is read; an SBOM
  and a well-formed platform are needed before anything is sent; one import runs at a time, with
  progress; a validation error marks its field; `not_enabled` keeps the screen disabled; a
  project is created from the model's text under the name the user gives, or the screen says why
  it cannot be; Back cancels a running import and never shows its late answer.
- With #290 below it: the frontend type check, tests and build, and `render_app.py --check` (the
  preview is unchanged).
- A headless Chrome tour of a Vite development server with the mock: the screen's result with
  its platform warning, then a project created from it. The refusal is covered by the unit tests.

## What a human accepted

- @Clovier, 2026-11-27: asked for the import screen to be started ("can you also get started on
  the import screen right now"), as part of the team's design; the wording and code are Claude
  Code's draft until the pull request review accepts them.
