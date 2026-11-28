# Threat model projects (#288)

The engine can save a threat model version by version and reopen any version. This
follows the team's design for saving and reopening threat models, below. The #289
review service saves through it, and the #290 app is to show it. The choices made in
building it, and how it was checked, are in
[DL-0075](../design-log/0075-model-workspace/README.md). It is off unless the host
turns it on, so the normal desktop launch is unchanged and read-only.

## The team's design

The app offers three ways in:

- **Import New Product:** an SBOM and a Grype scan of it, through `tmodel import-sbom`
  (#257, open in #268).
- **Open Existing Threat Model:** a saved YAML file, of any version, opened read-only.
  A project can be started from it.
- **Open Existing Project:** continue a project and its version history.

A project is a local folder the user picks, named after the model, such as
`JuiceShop Threat Model/`:

```text
JuiceShop Threat Model/
  original.yaml      the model the project started from, byte for byte; never changed
  project.json       id, name, created time, source, current version, and every version
  versions/
    v001.yaml        the starting model: a copy of original.yaml
    v002.yaml        each save adds the next version; none is ever rewritten
```

The flow is: the model YAML goes through the engine (report, knowledge graph, attack
paths, risk), the user reviews and edits, and "Save New Version" goes through the
engine again. A save never overwrites an older version. The app is to show a version
selector ("Version 4 (Current)") and a table of versions with each one's version, short
description, risk summary and date, and to reopen any older version.

## Turning it on

```sh
export TMODEL_HOST_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
tmodel serve --projects
```

In Python the host calls `engine.api.server.serve(host_token=...)`. The token is the
host's secret: 32 to 512 printable ASCII characters with no spaces. It is read from the
environment, never from the command line, because other local accounts can see a
process's command line. Every `/workspace/*` operation needs
`Authorization: Bearer <token>`; a browser's CORS preflight is answered without it. The
host keeps the token in memory and may give it to its own webview; it never goes in a
URL, a YAML file or a log.

Without `--projects`, every `/workspace/*` operation answers 503 `workspace_failure`
(403 for a foreign Host or Origin) and no file is written. Every other route behaves as
before.

## Operations

| Shared name | HTTP | Python (`ProjectWorkspace`) | Caller |
| --- | --- | --- | --- |
| createProject | `POST /workspace/host/create-project` `{"path", "source_file" or "model_id", "name"?}` (201) | `create_project(folder, source_file=, model_id=, name=)` | host |
| openProject | `POST /workspace/host/open-project` `{"path"}` | `open_project(folder)` | host |
| openFile | `POST /workspace/host/open-file` `{"path"}` | `open_file(path)` | host |
| listOpenModels | `GET /workspace/models` | `list_models()` | app or host |
| openModel | `GET /workspace/model?model_id=M` | `open_model(model_id)` | app or host |
| readVersion | `GET /workspace/model?model_id=M&revision=R` | `open_model(model_id, revision)` | app or host |
| listVersions | `GET /workspace/versions?model_id=M[&revision=R]` | `list_versions(model_id, revision)` | app or host |
| saveVersion | none | `save_version(model_id, expected_revision, document, description=None, summary=None)` | #289 |

- **Only the host passes paths.** The `/workspace/host/*` routes take a folder or file
  path, so they refuse any request with an Origin header, which a browser or webview
  adds to every POST it sends. No answer contains a path: the app works with ids only.
- **Sources.** `source_file` is a `file` that `GET /models` lists: the bundled examples
  in the app, or `spec/vectors/` in a source checkout. `model_id` is a file opened with
  openFile, such as the SBOM importer's output. The source is only read.
- **The folder.** createProject needs a new folder whose parent exists, or an empty
  one. An existing folder counts as empty when it holds nothing but a `.DS_Store`
  (Finder's view settings) and the engine's own leftover temporary files
  (`.original.yaml.<16 hex>.tmp`, `.project.json.<16 hex>.tmp`); any other file, hidden
  or not, counts. An existing empty folder is filled in place, so it keeps its permissions, extended attributes such as Finder tags,
  and `.DS_Store`. A link to a folder makes the project in the folder it names. `name`
  defaults to the name of the folder the host passed. A project folder can never be
  inside the example models folder or hold it, and a link inside a project folder is
  never followed (What a save guarantees).
- **Saving** has no route: #289's `saveModelChanges` saves through
  `ProjectReviewWorkspace` (in `engine/review_workspace.py`, shared with #291), whose
  `commit_version` calls `save_version` with a description and a summary such as the
  engine's risk summary, and whose `commit` calls it with neither. `summary` is any JSON object of at most
  16 KiB as written (indented, as `project.json` holds it) and at most 8 levels deep;
  the engine stores it and does not compute it. A description is at most 500
  characters.
- A version in an answer has `number` (1 for v001, null for a read-only file) for
  display, and no file name.
- `GET /workspace/models` also says that every save is checked against the schema
  (`schema_validation`, always true: by LinkML, or without it by `engine/schema_check.py`).
- A request body must arrive whole within 5 seconds, or the answer is 422.
- Answers carry `Cache-Control: no-store`. The Tauri origins get CORS headers on the app
  routes, whose preflight allows the `Authorization` header.

[`examples/model-workspace/contract.json`](examples/model-workspace/contract.json) has a
request and an answer for every operation and every error code, made from
[`workspace-example.yaml`](examples/model-workspace/workspace-example.yaml), a synthetic
model. `tests/test_workspace_api.py` checks that the engine still answers exactly that.

## Ids and versions

- A project's id is `project:` and 32 random hex digits, stored in `project.json`, so it
  stays the same when the engine restarts or the folder moves.
- A file opened read-only gets `file:` and 32 random hex digits each time it is opened.
  Its one revision is `sha256:` and the digest of its bytes as opened; later changes to
  the file are not seen.
- Versions are `v001`, `v002` and so on (`v1000` follows `v999`). To the
  `ReviewWorkspace` interface they are opaque strings.
- The engine remembers which folder or file each id belongs to until it stops. After a
  restart, the host opens the project folder again and gets the same id. Opening it at
  the same path finds it even when its device or inode number changed, as when the folder
  is put back from a backup or its drive is mounted again. An id the engine has not
  opened is `not_found`.
- A copied project folder keeps its id, so the engine refuses to open the copy, at
  another path, while the original is open and still holds the project. Starting a new
  project from one of the copy's versions gives it a new id.

## What a save guarantees

- `original.yaml` is the source's bytes and is never read or written again; `v001.yaml`
  is the same bytes. The examples and the bundled models are only read.
- A link inside a project folder is never followed. `project.json` must be a regular file
  and `versions/` a folder, both checked without following a link each time the project
  is read, including just before a save writes; otherwise the answer is
  `workspace_failure`. A version file that is a link answers `not_found`.
- Every check below runs before anything is written. Then, under the project's lock (a
  lock the engine's threads share, and an `flock` on `versions/` that every engine
  process saving to the folder takes), the engine checks that the expected version is
  still current, writes the next `vNNN.yaml` under a temporary name, flushes it to disk
  and puts it in place with a hard link, then replaces `project.json` with a rename.
- Replacing `project.json` is the commit point. A write that fails before it leaves the
  folder as it was and answers `save_failure`. A failed flush of the folder after it
  still answers success, because the new version is already in place.
- A save never replaces a version file. The hard link fails if anything is at the
  version's name, even a file another program wrote a moment before; the save then
  answers `save_failure`. On a volume without hard links, such as FAT or exFAT, a check
  and then a rename put the file in, and a file written in the moment between the two
  would be replaced. If the file a save would write exists but `project.json` does not
  list it (an interrupted save, or a file put there by hand), the save answers
  `workspace_failure` and writes nothing; moving the file out lets saving continue.
- A project in a new folder is assembled in a hidden folder next to it and renamed into
  place in one step. In an existing empty folder, `versions/`, `original.yaml` and
  `v001.yaml` go in first and `project.json` last. Either way a failed write leaves no
  project and no half-made folder: an existing folder is as it was, except that anything
  someone else put in it meanwhile stays, and `versions/` with it if that is where.
- A save that would make `project.json` larger than 16 MiB is refused with
  `validation_error` (field `project`) before anything is written, so every project the
  engine accepts can be opened again; a new project started from the current version
  takes further versions.
- Files are read only up to 16 MiB, the most the engine writes: a larger version file
  answers `not_found`, a larger `project.json` `workspace_failure`.
- Every read checks the version file's SHA-256 against `project.json`. A version file
  that is missing, or was changed outside the app, answers `not_found`: that revision is
  unavailable, as the `ReviewWorkspace` interface defines it.

## What a save checks

1. **Plain data:** text, finite numbers, true/false, null, dates, lists, and mappings
   with text keys; at most 64 levels deep and 16 MiB as YAML.
2. **Collections:** only those the project's schema container exposes. A project from
   an example keeps the container CI validates that example against
   (`.github/workflows/schema.yml`): `mvp-*` ExampleModelCore, `tv-*` ExampleModel,
   `pv-*` ExampleModelProposed. Any other file, such as the SBOM importer's output, gets
   the first of ExampleModelProposed (the core plus the classes ADR-0011 accepted),
   ExampleModel and ExampleModelSdl that holds its collections.
3. **The schema check:** the container class, closed to unknown fields, as
   `linkml-validate` runs in CI. LinkML does it when it is installed and `spec/schema/`
   is present (a source checkout). Without LinkML, as in the engine's CI job and the
   packaged app, `engine/schema_check.py` does it. That module reads the same container
   files and the object model they import, which `bin/build-engine` bundles. It applies
   the part of LinkML those files use, and refuses to load a schema that uses any other
   part, so a schema change cannot quietly weaken it. The engine does not start with
   project folders on if the schema cannot be loaded.
4. **The engine's own checks**, as `GET /graph` and `GET /risk` apply them: at least one
   model object, unique ids, every reference slot resolving, the attack graph (gates and
   steps), and the references and the feasibility, impact and mitigation values the risk
   calculation reads.
5. **A YAML round trip:** the YAML to be stored must read back equal to the document.

The two schema checks give the same verdict on 51 broken copies of `pv-01`, `mvp-02`
and `tv-software-auth-service` (DL-0081). Their `fields[0].field` can differ: LinkML
names the record (`attack_paths[0]`), and `engine/schema_check.py` the field in it
(`attack_paths[0].colour`). Neither checks that a reference resolves; check 4 does.
`validate(document)`, which has no project to go by, uses the container a file would
get; a save then uses its project's own container.

## Errors

Error bodies are the `ReviewError` shape from `engine/review_workspace.py`, the same as
#289's. Messages never contain a path; the tests check this.

| Code | HTTP | When |
| --- | --- | --- |
| validation_error | 422 | A bad request or field (`fields[].field`); an invalid document, description or summary; a save that would make `project.json` larger than 16 MiB (field `project`); a folder that cannot hold a new project |
| permission_denied | 403 | No or a wrong token; a foreign Host or Origin; a browser calling a host route; saving a read-only file |
| not_found | 404 | An id that is not open, or no such version; a version file that is missing, a link, or changed outside the app; no project in the folder; a missing file; a source `GET /models` does not list; an unknown operation |
| revision_conflict | 409, through #289 | The expected version is not the current one; `current_revision` names it, and nothing is written |
| save_failure | 503 | A write failed, or another save of the project held the lock for 10 seconds; nothing changed |
| workspace_failure | 503 | Project folders are off; a damaged `project.json`, or a project folder that cannot be read; a `project.json` that is a link or not a regular file; a `versions` folder that is missing, a link or not a folder; an unlisted version file in the way; the schema check could not run |
| internal_error | 500 | Anything unexpected |

## Limits

- Without `fcntl` (Windows), saves are serialized within one engine process only.
- A crash can leave a hidden temporary file (`.name.<hex>.tmp`), a hidden
  `.tmodel-new-project-<hex>` folder next to a project being made, or an unlisted
  version file, which stops the next save until it is moved. None is ever read. A crash
  while an existing empty folder is filled leaves `original.yaml` and `versions/`
  without `project.json`; the folder must then be emptied before a project is made in it,
  though the engine's own temporary files left there do not count against it.
- There is no close: each openFile adds an open model that keeps the file's bytes, up to
  16 MiB, until the engine stops, and opening the same file again adds another. An open
  project keeps only its folder's path.
- The link checks run just before a save writes, so a link put into a project folder in
  the moment between the check and the write could still be followed.
- If an older copy of a project folder is put back while the app has it open, a version
  label can be used twice, and a save based on the first one is not detected as stale.
- A project in an iCloud-synced folder can get "name 2" copies of its files. The
  engine reads only the exact names, and reports a version file that sync removed as
  `not_found`; a removed `project.json` makes the whole project `not_found`, and a
  removed `versions` folder answers `workspace_failure`.
