---
schema: "archdoc/v1"
id: DL-0075
title: "Threat model projects: saving a model version by version and reopening any version (#288)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0075
human_owner: Clovier
bears_on: [DEC-001a, ADR-0004, R-018]
defers_to: ARCH-0001
---

# DL-0075: threat model projects (#288)

`main` ends at DL-0073, and open pull requests use DL-0068 (#268), DL-0070 (#273), DL-0071
(#277) and DL-0074 (#291), so this entry is DL-0075.

## Question asked

Issue #288, "Backend: Editable Model Workspace and Persistence": create an editable copy of
a product model or reopen one, with a stable model id and revision; keep the originals and
the bundled examples unchanged; save with the existing YAML schema, keeping every earlier
revision and its provenance; refuse stale and invalid saves without changing the saved
model, in one atomic save that can hold review decisions, annotations and rating changes
together; answer every failure with a consistent error; and give #289 and #290 shared
interfaces and mock responses. Review logic, identity and permissions are out of scope.

#289's draft pull request #291 (commit 125a95d) already proposes the storage interface,
`engine/engine/review_workspace.py`: `ReviewError`, `ModelRevision`, the `ReviewWorkspace`
protocol (`read`, `history`, `validate`, `commit`) and `ReviewPrincipal`. #288 had to
implement it so that #291 plugs in without rework. During the build the team's design for
saving and reopening threat models arrived, and replaced the agent's first layout (below).

## What was produced

- `engine/engine/review_workspace.py`: #291's file byte for byte, as of its commit 1a01456
  (git blob `0efa9eb0`), so the two pull requests add the same file and do not conflict.
  Nothing in it was changed here. Since 125a95d it also holds #291's
  `ProjectReviewWorkspace`, which saves through `ProjectWorkspace.save_version`, and
  `ReviewPrincipal.allow_party_creation` and `display_name`.
- `engine/engine/model_workspace.py`: `ProjectWorkspace`, the `ReviewWorkspace` over project
  folders, with `create_project`, `open_project`, `open_file`, `list_models`, `open_model`,
  `list_versions` and `save_version`.
- `engine/engine/api/workspace.py`: the opt-in HTTP routes, installed by `serve()`.
- `engine/engine/api/server.py`: `serve(host_token=...)` installs the routes, on only with a
  token. `make_server` and the request handler are unchanged.
- `engine/engine/cli.py`: `tmodel serve --projects`, which reads the token from
  `TMODEL_HOST_TOKEN`.
- `engine/MODEL_WORKSPACE.md`: the interface for #289, #290 and the desktop host.
- `engine/examples/model-workspace/`: `workspace-example.yaml`, a synthetic one-threat model,
  and `contract.json`, a request and an answer for every operation and error code.
- `engine/tests/test_model_workspace.py`, `test_workspace_api.py` and `workspace_support.py`.
- This entry.

## The team's design

The app offers three ways in: "Import New Product" (an SBOM and a Grype scan of it, through
`tmodel import-sbom`), "Open Existing Threat Model" (a saved YAML file of any version) and
"Open Existing Project" (continue a project and its version history). A project is a local
folder the user picks, named after the model, holding `original.yaml` (the model the project
started from, byte for byte, never changed), `project.json` (its metadata: name, current
version and the versions) and `versions/v001.yaml`, `v002.yaml` and so on, each never
rewritten once written. `v001` is a copy of the original, described as the initial model and
its source, and each save adds the next. The flow is the model YAML, then the engine (report,
knowledge graph, attack paths, risk), then review and edit, then "Save New Version", which
goes through the engine again; a save never overwrites an older version. The app is to show
a version selector ("Version 4 (Current)") and a table with each version's version, short
description, risk summary and date, and to reopen older versions.

For the engine, the team's design asks for exactly that layout; a host that passes the folder's
path and gets back an opaque id; `project.json` with a stable random id, the name, the created
time, the source (the original file's name and SHA-256) and the current version; each version
entry with its version, file, description, created time, parent version, SHA-256 and an
optional summary the caller supplies; versions `v001`, `v002` and so on as the revisions; a
`save_version` that takes a description and a summary, with `commit()` calling it with
neither; a compare-and-save of the current version under a lock; and the operations below.

## Choices the agent made, open to review

- **The interface is unchanged.** `save_version(model_id, expected_revision, document,
  description=None, summary=None)` is the one addition #288's own API needs, and `commit()`
  calls it with neither, so #291's service works as written. Checked on a merged tree (under
  How it was checked).
- **Ids.** A project's id is `project:` and 32 random hex digits, stored in `project.json`, so
  it stays the same after a restart or a move. A file opened read-only gets `file:` and 32
  random hex digits each time, and its one revision is `sha256:` and the digest of its bytes,
  which the engine keeps from the moment it was opened. Neither id is made from a path.
- **The engine remembers open ids until it stops.** After a restart the host opens the folder
  again and gets the same id; opening it at the same path finds it even when its device or
  inode number changed (Review changes, item 1). Nothing is written outside the project
  folders except the hidden folder a project in a new folder is assembled in, beside it,
  which becomes the project folder when renamed; a link inside a project folder is never
  followed (item 3). There is no list of recent projects, which stays the host's to keep.
- **A copied project folder keeps its id**, so the engine refuses to open the copy while the
  original is open and still holds the project. Starting a project from one of the copy's
  versions gives it a new id.
- **The host passes paths over its own routes.** The engine API listens on loopback, which
  every local account on the computer can reach. Without a secret, any of them could use
  routes that take a path, or return a model, to read the user's YAML files or write into
  their folders (web pages are already refused by the Host and Origin checks). So every
  `/workspace/*` operation needs the host's secret (`Authorization: Bearer`), and the three
  that take a path also refuse any request with an Origin header, which a browser or webview
  adds to every POST. The app reads with ids only, so no path reaches it. This is a
  transport check, like #291's session tokens; it is not reviewer identity or permission,
  which stay out of scope.
- **The secret comes from `TMODEL_HOST_TOKEN`, not the command line,** which other local
  accounts can see. It must be 32 to 512 printable ASCII characters with no spaces.
- **Off by default.** Without `--projects`, the routes answer 503 `workspace_failure` and touch
  no file, so the desktop launch, which passes no such flag, is unchanged.
- **Merging with #291.** In `server.py` only `serve()` changes, and it imports the new
  modules inside the function. The routes come from a handler subclass that `serve()`
  installs on the server it made, the way #291 gives each server its own handler class, and
  it passes any other request to the engine's handler, so #291's `do_POST`, `do_OPTIONS` and
  `/host/health` still answer theirs. In `cli.py` only `_serve` and the `serve` parser change.
  With #291's head e30dc7f the two merged without conflict. Its commit 1a01456 also adds
  `review_api` to `serve()`, which gives two small conflict hunks there, the parameter list
  and the `make_server` call; keeping both (`host_token`, then keyword-only `review_api`)
  and passing `review_api` to `make_server` resolves them. `cli.py` merges cleanly.
- **No save route.** "Save New Version" is #289's `saveModelChanges`, with its sessions and
  permissions; a route here that saved a whole document would be the arbitrary write #291
  refuses.
- **What a save checks, before any write.** Plain data (text, finite numbers, true/false,
  null, dates, lists and mappings with text keys, 64 levels, 16 MiB); only the collections
  the project's schema container exposes; the LinkML check of that container when LinkML and
  `spec/schema/` are present, as `linkml-validate` runs in CI; the engine's own checks as
  `GET /graph` and `GET /risk` apply them (at least one object, unique ids, every reference
  slot resolving, the attack graph, and the rating, impact and mitigation values); and a YAML
  round trip. Without LinkML (the engine's CI job and the packaged app), unknown fields in a
  record, and slots the engine does not read, are not checked; a test shows one case each way,
  and `GET /workspace/models` reports `schema_validation`.
- **The container.** A project from an example keeps the one CI validates that example
  against: `mvp-*` ExampleModelCore, `tv-*` ExampleModel, `pv-*` ExampleModelProposed. Any
  other file gets the first of ExampleModelProposed, ExampleModel and ExampleModelSdl that
  holds its collections. ExampleModelProposed is ExampleModelCore plus the classes ADR-0011
  accepted, and the container the SBOM importer names for its output (DL-0068), so a project
  started from an import can later hold trust boundaries and data flows. No container holds
  all the others (ExampleModel has no `assets`, which mvp-02 uses), so a single one would
  refuse some examples. A test checks that every container defines a shared collection
  alike, so any container that holds a document's collections checks it alike.
  `validate(document)` has no project, so it uses the container a file would get, and the
  save then uses the project's. (The first build used the narrowest container that fits,
  which gave the importer's output ExampleModelCore.)
- **Atomic writes.** Each file is written under a temporary name, flushed (`F_FULLFSYNC` on
  macOS, whose `fsync` stops at the drive's cache) and put in place, and its folder is
  flushed. A save puts the next version in with a hard link, then replaces `project.json`
  with a rename, the commit point. A failed folder flush after that still answers success,
  because the version is in place. A project in a new folder is assembled in a hidden folder
  beside it and renamed into place. An existing empty folder is filled in place, so it keeps
  its inode, permissions, extended attributes (Finder tags) and any `.DS_Store`;
  `project.json` goes in last, and a failure before it is in place removes only what was
  written, leaving `versions/` if something else was put in it meanwhile (item 2; second
  round, N2).
- **The lock** is a lock shared by the engine's threads and an `flock` on `versions/`, which
  every engine process takes; a lock file would add a file to the team's layout.
- **A version file is never replaced.** A new one goes in with a hard link, which fails if
  anything is at its name, even a file another program wrote a moment before (item 5). On a
  volume without hard links (FAT, exFAT) a check and then a rename put it in, with a moment
  between the two in which such a file could still be replaced. If the next one exists but
  `project.json` does not list it (an interrupted save, or a file put there by hand), the
  save stops with `workspace_failure` and writes nothing. Reusing the name could destroy a
  real version, for example after `project.json` was restored from a backup.
- **Metadata.** v001's description is "Initial model, copied from" and the source file's
  name. A later version's description and summary are what the caller passes, or null; the
  summary is a JSON object of at most 16 KiB as written (indented, as `project.json` holds
  it) and 8 levels deep, which the engine stores and does not compute (second round, N1).
  The name defaults to the name of the folder the host passed. `project.json` also records its format, the
  schema container and whether the source was an example or an opened file. In answers, a
  version carries `number` for display and no file name.
- **Files on disk** are created for the user only (folders 0700, files 0600, which the
  umask can only narrow), as a threat model may hold review notes.
- **ADR-0004.** Each version is a YAML file in the existing example-model format, and the
  working store (ADR-0008, #65) can be rebuilt from such files. No DEC is decided here: the
  format is the draft object model the examples already use.

## How it was checked

- `tests/test_model_workspace.py` (111 tests) and `tests/test_workspace_api.py` (35 tests):
  the layout; `original.yaml` byte for byte and unchanged after saves; v001 to v012 numbered
  and zero-padded, each with its metadata; reopening every older version, and the project
  after a restart, after a move, put back from a backup, and on a drive mounted again; an
  existing empty folder filled in place, and a link to one; a read-only file and a project
  started from it; refused folders and sources; every example copied and saved with
  `spec/vectors/` unchanged (a SHA-256 of every file), and a read-only examples folder; stale
  saves and twelve kinds of invalid document refused with the folder unchanged; a failure at
  each of the 9 write steps of a save, the 18 of a project in a new folder and the 16 of one
  in an existing empty folder holding a `.DS_Store`, each leaving no change (that folder with
  its inode, permissions and `.DS_Store`), and the folder flush after the commit point of a
  save and of a new folder; two racing saves on one folder through two workspaces, as two
  windows would make them, exactly one winning; a save while another process holds the
  folder's `flock`; a file another program writes at a new version's name meanwhile, with and
  without hard links; links inside a project folder; an unlisted version file; damaged and
  oversized files; a save refused before `project.json` would pass 16 MiB, and summaries at
  and past their limits; a failed fill keeping what the user put in meanwhile; the engine's
  own leftover temporary files in a folder chosen for a project; #291's
  `ProjectReviewWorkspace` saving through a project, with its description and summary; no path in any error; the LinkML check on and off; the containers; and the
  call sequence of #291's `ReviewService` (read, detach, change, validate, commit, history, a
  stale commit). Over HTTP: off by default, the token on every route, host routes refused to
  browsers, foreign Host and Origin, every bad request, a request body that stops arriving
  and one that trickles in, failures with no path, `tmodel serve` with and without
  `--projects`, and the contract.
- The review's findings, six in the first round and three in the second, each reproduced
  before it was fixed or recorded: see Review changes, and Review changes, second round.
- The whole engine suite: 960 passed, 14 skipped (the LinkML tests skip without LinkML, as
  in CI); with LinkML 1.12.1 on the path, 962 passed, 12 skipped.
- A merged tree: #291's commit 1a01456 with these files added, `cli.py` merged cleanly by
  `git merge-file` and `server.py`'s two hunks resolved as above. Its whole engine suite
  passes (1061 passed, 14 skipped), #291's own review tests among them (59 passed). With
  #291's `HostReviewAPI` and these routes on one server, as its integration notes describe,
  the host proof, opening a file, starting a project from it, a review saved through
  `/reviews/changes` (v002, with #291's description and risk summary in `project.json` and
  the host's reviewer Party added) and a stale save refused all work, with LinkML and
  without. (With its earlier head e30dc7f: 1041 passed, 14 skipped.)
- The SBOM importer's output: #268's importer (head 4be86c1) run on its own fixture gives a
  model that opens read-only and starts a project, with LinkML and without.
- `ruff check` (only the five UP038 lines already in `model_graph.py` and `tara.py`),
  `ruff format --check`, `tmodel health --in-process`, `bin/validate-archdoc` and
  `git diff --check`.

## Review changes (2026-11-27)

An independent review of this draft, before any pull request, found one P2 and five P3
issues. Each was reproduced on this branch first, with scratch scripts, then fixed or
recorded. Where the review used a FAT disk image, the device number's change was simulated
instead, because creating a disk image is refused where these checks ran.

1. **P2: the same folder at the same path was refused as its own copy** once its device or
   inode number changed: a folder put back from a backup (reproduced by copying it, deleting
   it and renaming the copy back), or a FAT drive attached again (reproduced by giving
   `_identity` another device number). The copy check compared those numbers only. Now a
   project already open from the same path, both with links resolved, takes the new numbers;
   a copy at another path is still refused while the folder first opened holds the project.
   Tests: `test_a_folder_put_back_at_the_same_path_opens_again`,
   `test_a_drive_mounted_again_opens_again`; the copy test still passes.
2. **P3-1: an existing empty folder was replaced, not filled, and could lose its
   `.DS_Store`.** Reproduced: a 0755 folder with a Finder tag came back 0700 with no extended
   attributes and a new inode; a failed final rename left it without its `.DS_Store`; and a
   path that is a link to an empty folder failed on every try (a folder cannot be renamed
   onto a link) after deleting the real folder's `.DS_Store`. Decided: fill an existing empty
   folder in place, which keeps the user's folder as it is (above, Atomic writes), and resolve
   the chosen path first, so a link to a folder makes the project in the folder it names.
   Tests: `test_an_empty_folder_the_user_made_is_filled_in_place`,
   `test_a_link_to_an_empty_folder_makes_the_project_in_that_folder`, and the step-failure
   test for both kinds of folder.
3. **P3-2: a link inside a project folder was followed.** Reproduced: `versions/` replaced by
   a link made the next save write `v002.yaml` where the link pointed, the example models
   folder included, and a linked `project.json` was read. Now, whenever a project is read,
   which includes under the lock just before a save writes, `project.json` must be a regular
   file and `versions/` a folder, both checked without following a link; the lock opens
   `versions/` with `O_NOFOLLOW`; a version file that is a link reads as `not_found`; and
   `original.yaml` is never read or written once the project is made. Tests:
   `test_a_linked_versions_folder_is_never_followed`,
   `test_a_linked_project_json_is_never_followed`,
   `test_links_to_a_version_or_the_original_are_never_followed`.
4. **P3-3: the 5 second body timeout applied to each read, not to the whole body.**
   Reproduced: with a 1 second budget, a body sent a byte at a time held the engine's thread
   for 5.4 seconds. Fixed rather than recorded: one deadline covers the whole body (`read1`
   in a loop against `time.monotonic()`, as #287's import route does), the answer is 422
   "Incomplete request body.", and the socket has a 5 second timeout again for sending it.
   Test: `test_a_body_that_trickles_in_gets_one_deadline_for_all_of_it`.
5. **P3-4: a new version file was checked for, then renamed into place,** so a file another
   program wrote in between was replaced. Reproduced by writing that file at that moment. Now
   it goes in with a hard link (above, A version file is never replaced). Tests:
   `test_a_file_another_program_writes_meanwhile_is_never_replaced`,
   `test_without_hard_links_a_new_file_is_checked_then_renamed` (link answering EPERM, ENOTSUP
   or EOPNOTSUPP, simulated here). The reviewer's spot-check then tried real FAT and exFAT
   disk images: `link()` answers ENOTSUP there, the fallback runs, and the 19-step failure
   injection of an in-place fill leaves the folder exactly as it was.
6. **P3-5: `open_file` has no close.** Reproduced: five opens of one file gave five open
   models, each holding the file's bytes. Recorded, not changed: a close would add a route to
   the contract, and the engine cannot yet tell whether a review session still uses a model.
   `engine/MODEL_WORKSPACE.md` states the growth, and Follow-ups lists the close.

The same kinds of defect were then looked for across the module. One more was found:
`project.json` and version files were read whole, whatever their size. They are now read only
up to 16 MiB, the most the engine writes (for `project.json`, since the second round, N1); a
larger version file reads as `not_found` and a larger `project.json` as `workspace_failure`
(`test_files_larger_than_the_engine_writes_are_not_read`). `contract.json` did not change:
the contract test passes without rewriting it, and it is byte for byte the file reviewed.

## Review changes, second round (2026-11-27)

The reviewer's spot-check confirmed the six fixes above, on real FAT and exFAT images as
well, and found that they added one P2 and two P3 issues. Each was reproduced on this branch
first, with the reviewer's probes run against it, then fixed.

1. **N1 (P2): saves could make `project.json` larger than the 16 MiB the engine reads,** and
   the project then could not be opened, read or saved. Reproduced: summaries just under the
   64 KiB limit, as compact JSON, but nested 60 levels deep took 2.72 MiB each in the indented
   `project.json`; after 7 accepted saves it was 16.32 MiB, and opening, reading v001 and the
   next save all answered `workspace_failure`. Now a save whose new `project.json` would pass
   16 MiB (`MAX_PROJECT_BYTES`, also the read limit) is refused with `validation_error`, field
   `project`, before anything is written, so every project the engine accepts can be opened
   again; a new project started from the current version takes further versions. A summary
   is now at most 16 KiB measured as written, indented, and 8 levels deep, so indentation
   cannot multiply it. With the largest flat summary, a probe with the cap set to 2 MiB was
   refused after 125 saves, with `project.json` under the cap and the project still opening.
   Tests: `test_a_save_that_would_make_project_json_too_large_is_refused` (the refused save
   leaves the project openable, in the same engine and a new one),
   `test_a_summary_at_the_limits_is_accepted`, and three new bad-summary cases.
2. **N2 (P3): a failed in-place fill deleted anything put into `versions/` meanwhile,** as
   the rollback removed the folder whole. Reproduced with a file dropped into `versions/`
   just before a write failed. Now the rollback removes only the files it wrote and then
   removes `versions/` only if it is empty. Test:
   `test_a_failed_fill_keeps_what_the_user_put_in_meanwhile`.
3. **N3 (P3): after a crash, the engine's own hidden temporary file kept a folder from
   counting as empty.** Reproduced by stopping the engine while `original.yaml`'s
   temporary file was written: once the user removed the `versions/` left behind,
   `.original.yaml.<hex>.tmp` remained, and the next create answered "Choose an empty
   folder" with nothing visible in it. Now the emptiness check ignores exactly the names the
   engine writes there (`.original.yaml.<16 hex>.tmp`, `.project.json.<16 hex>.tmp`); any
   other file, hidden or not, still counts. Test:
   `test_the_engines_own_leftover_temporary_files_do_not_make_a_folder_busy`.

Two messages were also made true: a `project.json` that is a pipe, not a link, now gets
"must be a regular file in the project folder, not a link or anything else", and a missing
`versions` folder gets "missing, or is a link or not a folder", which
`engine/MODEL_WORKSPACE.md` now lists (test:
`test_a_missing_versions_folder_or_a_project_json_that_is_no_file_is_reported`).
`contract.json` did not change in this round either.

## What a human accepted

- @Clovier, 2026-11-27: took over #288 and asked for it to be built ("start on 288, 290, and
  236"); the wording and code are Claude Code's draft until the pull request review accepts
  them.
- @Clovier, 2026-11-27: during the build, shared the team's design for saving and reopening
  threat models and chose to align this change with it ("Yes, align now"), which replaced the
  agent's first layout (below).

## What was rejected, and why

- **The agent's first layout:** one workspace folder chosen by the host (by default the
  per-user application data folder), holding every editable copy under `models/<id>/` with an
  `index.json`, `local:` ids and `r<n>-<hex>` revisions. The team's design replaced it before
  anything was committed: each project is a folder the user picks, with the layout above. The
  per-user default folder went with it, since the user picks every project folder.
- **Unauthenticated read routes,** in the first build: on loopback they would have shown any
  local account the user's models.
- **Overwriting an unlisted version file:** it may be a real version that `project.json` no
  longer lists.

## Follow-ups

- **The desktop host:** #291 carries it since its commit 1a01456 (`project_host.rs`): the
  token, the native pickers and calls to this change's three host routes. It leaves out
  `--projects` until this change lands. Still to do once both are merged: pass `--projects`
  only when the host has credentials (this command exits on an empty token); wire #291's
  `HostReviewAPI` over this `ProjectWorkspace` into `serve()`, which neither change does yet,
  so until then the host's `/host/health` proof fails; and open the last project again at
  launch (the host clears its list at startup).
- **#289:** #291's `ProjectReviewWorkspace` (since 1a01456) passes a description and the risk
  summary to `save_version`. A description over 500 characters is refused here, while #291
  accepts up to 4096; one of the two should change (500 is the team's "short description").
  `HUMAN_REVIEW.md`'s integration status still needs updating. Its test double's ids
  (`local:one`, `r1`) differ from these, which is fine for a double.
- **Shared HTTP helpers:** the strict JSON parsing and the error status table now exist in
  both `api/reviews.py` (#291) and `api/workspace.py`; one copy can go once both are merged.
- **Import New Product:** the import route (DL-0078, #287) returns the model's text; the host
  saves it, opens it with openFile and starts a project from it. A project from #268's
  importer output was checked (above).
- **The packaged app has no LinkML** and no `spec/schema/`, so it runs the engine checks only.
- **Crash leftovers** (hidden temporary files, a hidden new-project folder, an unlisted version
  file) are never read, and are not cleaned up. A crash while an existing empty folder is
  being filled leaves `original.yaml` and `versions/` without `project.json`; the folder is
  then not empty, and making a project there needs them removed first. The engine's own
  temporary files left there do not count against an empty folder (second round, N3).
- **Closing a read-only file** (Review changes, item 6): each openFile keeps the file's bytes,
  up to 16 MiB, until the engine stops. A close is for when the routes can tell whether a
  review session still uses the model.
- **Links put in during a save:** the checks run just before a save writes, so a link put into
  a project folder in the moment between the check and the write could still be followed.
- **Request headers:** the engine's server has no deadline for reading a request's headers,
  on every route, as before this change; one for the whole request is for the server.
- **A folder put back from a backup** while the app has it open can reuse a version label, and
  a save based on the first one is not detected as stale.
- **Windows:** no `flock`, so saves are serialized within one engine process only.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
