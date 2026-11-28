"""Threat model projects (#288): save a model version by version, and reopen any version.

This follows the team's design for saving and reopening threat models (DL-0075,
engine/MODEL_WORKSPACE.md). A project is a local folder the user picks, named after
the model, holding:

    original.yaml        the model the project started from, byte for byte, never changed
    project.json         the project: id, name, created time, source, current version, versions
    versions/v001.yaml   every saved version, never rewritten once written: v001 is a
    versions/v002.yaml   copy of original.yaml, and each save adds the next

`ProjectWorkspace` is the `ReviewWorkspace` (engine/review_workspace.py) the #289
review service saves through. The host passes folder and file paths in; the engine
answers with opaque ids (`project:` or `file:` and 32 hex digits) and version labels
(`v001`, `v002`, ...), so no physical path reaches the frontend or an error message.
A YAML file opened on its own is read-only, with the one revision `sha256:<digest>`,
and a project can be started from it.

Saving writes the next version under a temporary name, flushes it to disk and puts it
in place with a hard link, which never replaces a file, then replaces project.json with
a rename. Replacing project.json is the commit point. It happens under the project's
lock, after checking that the expected version is still the current one, so a failure
before it leaves the folder as it was. A link inside a project folder is never followed:
project.json and versions/ must be the folder's own file and folder.
"""

from __future__ import annotations

import errno
import hashlib
import importlib.util
import json
import math
import os
import re
import secrets
import shutil
import stat
import threading
import time
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from engine import core
from engine.graph import GraphError
from engine.load.vector import MODEL_SUFFIXES
from engine.model_graph import project_model_graph
from engine.review_workspace import ModelRevision, ReviewError
from engine.risk import MATRIX_ID, assess_document
from engine.schema_check import Container, SchemaError, load_container
from engine.schema_check import check as schema_problems

try:
    import fcntl
except ImportError:  # Windows: saves are then serialized within one engine process only
    fcntl = None

FORMAT = "tmodel-project"
FORMAT_VERSION = 1
PROJECT_FILE = "project.json"
ORIGINAL = "original.yaml"
VERSIONS = "versions"
MAX_ID_LENGTH = 256  # the ReviewWorkspace contract: ids and revisions of at most 256 characters
MAX_PATH_LENGTH = 4096
MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 500
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024  # a model, as YAML, and so each version file
# project.json, as written and as read: a save that would make it larger is refused, so
# every project the engine accepts can be opened again.
MAX_PROJECT_BYTES = 16 * 1024 * 1024
MAX_SUMMARY_BYTES = 16 * 1024  # a version's summary, as written: indented, as in project.json
MAX_SUMMARY_DEPTH = 8
MAX_DEPTH = 64
LOCK_TIMEOUT_S = 10.0
MESSAGE_LIMIT = 300

_PROJECT_ID = re.compile(r"project:[0-9a-f]{32}")
# The temporary files _put leaves in a project folder if the engine stops mid-write.
_OWN_TEMPORARY = re.compile(r"\.(?:original\.yaml|project\.json)\.[0-9a-f]{16}\.tmp")
_DIGEST = re.compile(r"[0-9a-f]{64}")

# The schema containers. Every one gives a collection it shares with another the same
# definition, so any container that holds a document's collections checks it alike
# (tests/test_model_workspace.py checks this).
CONTAINER_FILES = {
    "ExampleModelCore": "example-container-core.linkml.yaml",
    "ExampleModelProposed": "example-container-proposed.linkml.yaml",
    "ExampleModel": "example-container.linkml.yaml",
    "ExampleModelSdl": "example-container-sdl.linkml.yaml",
}
# A project from an example keeps the container CI validates that example against
# (.github/workflows/schema.yml).
FAMILY_CONTAINERS = (
    ("mvp-", "ExampleModelCore"),
    ("tv-", "ExampleModel"),
    ("pv-", "ExampleModelProposed"),
    ("sdl-", "ExampleModelSdl"),
)
# Any other file gets the first of these that holds its collections. ExampleModelProposed
# is ExampleModelCore plus the classes ADR-0011 accepted, and the container the SBOM
# importer names for its output (DL-0068); ExampleModelSdl is ExampleModel plus the SDL
# classes. No container holds all the others' collections.
FITTING_CONTAINERS = ("ExampleModelProposed", "ExampleModel", "ExampleModelSdl")
# The container files sit beside the examples and are bundled with them, and so is the
# object model they import, ../schema/tmodel-object-model.linkml.yaml (bin/build-engine).
SCHEMA_DIRECTORY = core.APPROVED_VECTOR_DIRECTORY

_THREAD_LOCKS: dict[tuple[int, int], threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()
_LINKML_LOCK = threading.Lock()
_VALIDATORS: dict[str, Any] = {}


def linkml_available() -> bool:
    """Whether LinkML itself can check the schema: LinkML is installed, and the object
    model the containers import is present (a source checkout; the packaged engine has
    no LinkML, and checks with engine/schema_check.py instead)."""
    return (
        importlib.util.find_spec("linkml") is not None
        and (SCHEMA_DIRECTORY.parent / "schema" / "tmodel-object-model.linkml.yaml").is_file()
        and all((SCHEMA_DIRECTORY / name).is_file() for name in CONTAINER_FILES.values())
    )


def version_label(number: int) -> str:
    """The label of the `number`-th version: v001, v002, ... (v1000 after v999)."""
    return f"v{number:03d}"


@dataclass(frozen=True)
class _Project:
    folder: Path
    identity: tuple[int, int]  # the folder's device and inode when it was opened


@dataclass(frozen=True)
class _File:
    name: str  # the file's own name, for display; never its folder
    data: bytes  # its bytes when opened: the read-only snapshot every read parses
    revision: str
    container: str
    opened_at: str


class ProjectWorkspace:
    """The ReviewWorkspace over project folders the host opens, plus read-only files.

    It remembers, for this engine process, which id belongs to which folder or file.
    After a restart the host opens the folder again and gets the same id, because the
    id is stored in project.json. Every save is checked against its schema container.
    `schema_check` None has LinkML do it when `linkml_available()`, True requires
    LinkML, and False uses engine/schema_check.py, as the packaged app does. `clock`
    and `token` exist for repeatable tests.
    """

    def __init__(
        self,
        *,
        schema_check: bool | None = None,
        clock: Callable[[], datetime] | None = None,
        token: Callable[[int], str] | None = None,
    ) -> None:
        available = linkml_available()
        if schema_check and not available:
            raise ValueError("the LinkML schema check needs linkml and spec/schema/")
        self.schema_check = available if schema_check is None else schema_check
        self._containers = {name: _container_collections(name) for name in CONTAINER_FILES}
        self._schemas = _bundled_schemas()  # at start, so a missing object model fails fast
        self._clock = clock or (lambda: datetime.now(UTC))
        self._token = token or secrets.token_hex
        self._models: dict[str, _Project | _File] = {}
        self._registry = threading.Lock()

    # The ReviewWorkspace protocol (engine/review_workspace.py)

    def read(self, model_id: str, revision: str) -> ModelRevision:
        """Exactly `revision`, as a fresh document: never the current one instead."""
        model = self._model(model_id)
        _require_id(revision, "revision")
        if isinstance(model, _File):
            if revision != model.revision:
                raise _not_found()
            return ModelRevision(model_id, revision, _snapshot(model), False)
        project = self._project(model_id, model)
        record = _version(project, revision)
        return ModelRevision(model_id, revision, self._document(model, record), True)

    def history(self, model_id: str, revision: str) -> list[ModelRevision]:
        """Every version from v001 through `revision`, oldest first, none after it."""
        model = self._model(model_id)
        _require_id(revision, "revision")
        if isinstance(model, _File):
            return [self.read(model_id, revision)]
        project = self._project(model_id, model)
        through = project["versions"].index(_version(project, revision)) + 1
        return [
            ModelRevision(model_id, record["version"], self._document(model, record), True)
            for record in project["versions"][:through]
        ]

    def validate(self, document: Mapping[str, Any]) -> None:
        """Every check a save makes, against the first fitting container (FITTING_CONTAINERS).

        A save then checks against its project's own container. Raises validation_error.
        """
        plain = _plain_document(document)
        self._checked(plain, self._fitting_container(plain))

    def commit(self, model_id: str, expected_revision: str, document: Mapping[str, Any]) -> str:
        """`save_version` with no description or summary; #289 may pass them later."""
        return self.save_version(model_id, expected_revision, document)

    # The project operations #288 owns

    def save_version(
        self,
        model_id: str,
        expected_revision: str,
        document: Mapping[str, Any],
        description: str | None = None,
        summary: Mapping[str, Any] | None = None,
    ) -> str:
        """Save `document` as the next version if `expected_revision` is still current.

        Checks the document, then compares and saves under the project's lock, and
        returns the new version's label. A stale revision, an invalid document, an
        invalid description or summary, or a failed write raises ReviewError and leaves
        the folder as it was. The document is stored as given and never changed.
        `summary` is any small JSON object the caller supplies, such as a risk summary.
        """
        model = self._model(model_id)
        _require_id(expected_revision, "expected_revision")
        description = _description(description)
        summary = _summary(summary)
        if isinstance(model, _File):
            _require_current(model.revision, expected_revision)
            raise ReviewError(
                "permission_denied", "This model is read-only. Start a project from it to save."
            )
        project = self._project(model_id, model)
        _require_current(project["current_version"], expected_revision)  # before any work
        data = self._checked(_plain_document(document), project["container"])
        with self._lock(model):
            project = self._project(model_id, model)
            _require_current(project["current_version"], expected_revision)
            return self._append(model, project, data, description, summary)

    def create_project(
        self,
        folder: str | os.PathLike[str],
        *,
        source_file: str | None = None,
        model_id: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Start a project in `folder`, a new or empty folder the host passes.

        The source is a model `GET /models` lists (`source_file`: the bundled examples,
        or spec/vectors in a source checkout), or a file opened with `open_file`
        (`model_id`), such as the SBOM importer's output. It is copied, never changed:
        original.yaml and versions/v001.yaml are its bytes. A link to a folder makes the
        project in the folder it names. `name` defaults to the name of the folder the
        host passed. Returns the project as `open_model` does.
        """
        target = _project_folder(folder)
        chosen_name = Path(os.fspath(folder)).name
        if (source_file is None) == (model_id is None):
            raise _invalid("source_file", "Give either source_file or model_id.")
        if source_file is not None:
            source_name, data = _example(source_file)
            origin = "example"
        else:
            snapshot = self._model(model_id)
            if not isinstance(snapshot, _File):
                raise _invalid("model_id", "Expected a model opened read-only with open_file.")
            source_name, data, origin = snapshot.name, snapshot.data, "file"
        plain = _plain_document(_parsed(data, "source_file" if source_file else "model_id"))
        family = _family_container(source_file) if source_file is not None else None
        container = family or self._fitting_container(plain)
        self._checked(plain, container)
        title = _name(chosen_name if name is None else name)
        digest = hashlib.sha256(data).hexdigest()
        now = self._now()
        project_id = "project:" + self._new_token(16)
        first = version_label(1)
        project = {
            "format": FORMAT,
            "format_version": FORMAT_VERSION,
            "id": project_id,
            "name": title,
            "created_at": now,
            "source": {"file": source_name, "sha256": digest, "origin": origin},
            "container": container,
            "current_version": first,
            "versions": [
                {
                    "version": first,
                    "file": f"{VERSIONS}/{first}.yaml",
                    "description": _clip(f"Initial model, copied from {source_name}"),
                    "created_at": now,
                    "parent_version": None,
                    "sha256": digest,
                    "summary": None,
                }
            ],
        }
        _build_project(target, data, project)
        self._register(project_id, target)
        return self.open_model(project_id)

    def open_project(self, folder: str | os.PathLike[str]) -> dict[str, Any]:
        """Open the project in `folder` at its current version; the same id as before."""
        path = _project_folder(folder)  # a save writes here, so never among the examples
        project = _read_project(path)
        self._register(project["id"], path)
        return self.open_model(project["id"])

    def open_file(self, path: str | os.PathLike[str]) -> dict[str, Any]:
        """Open a YAML model file read-only, as it is now: later reads see these bytes."""
        file = _host_path(path)
        if file.suffix not in MODEL_SUFFIXES:
            raise _invalid("path", "Expected a .yaml or .yml model file.")
        data = _read_file(file)
        plain = _plain_document(_parsed(data, "path"))
        container = self._fitting_container(plain)
        self._checked(plain, container)
        model_id = "file:" + self._new_token(16)
        revision = "sha256:" + hashlib.sha256(data).hexdigest()
        with self._registry:
            self._models[model_id] = _File(file.name, data, revision, container, self._now())
        return self.open_model(model_id)

    def list_models(self) -> dict[str, Any]:
        """The projects and read-only files open in this engine, in the order opened."""
        with self._registry:
            opened = list(self._models.items())
        models, problems = [], []
        for model_id, model in opened:
            try:
                models.append(self._describe(model_id, model)[0])
            except ReviewError as exc:
                problems.append({"model_id": model_id, "error": exc.to_dict()["error"]})
        return {
            "count": len(models),
            "models": models,
            "problems": problems,
            "schema_validation": True,  # by LinkML or by engine/schema_check.py
        }

    def open_model(self, model_id: str, revision: str | None = None) -> dict[str, Any]:
        """A model at its current version, or at exactly `revision`, with its metadata."""
        model = self._model(model_id)
        if revision is not None:
            _require_id(revision, "revision")
        summary, records = self._describe(model_id, model)
        record = records[-1] if revision is None else _find(records, revision)
        if isinstance(model, _File):
            document = _snapshot(model)
        else:
            document = self._document(model, record)
        return {
            **summary,
            "revision": record["version"],
            "version": _public(record, records, summary["kind"]),
            "document": _json_safe(document),
        }

    def list_versions(self, model_id: str, revision: str | None = None) -> dict[str, Any]:
        """Each version's metadata through `revision` (default: the current one), oldest first."""
        model = self._model(model_id)
        if revision is not None:
            _require_id(revision, "revision")
        summary, records = self._describe(model_id, model)
        record = records[-1] if revision is None else _find(records, revision)
        through = records.index(record) + 1
        return {
            "model_id": model_id,
            "revision": record["version"],
            "current_revision": summary["current_revision"],
            "versions": [_public(item, records, summary["kind"]) for item in records[:through]],
        }

    # Registry and storage

    def _model(self, model_id: Any) -> _Project | _File:
        _require_id(model_id, "model_id")
        with self._registry:
            model = self._models.get(model_id)
        if model is None:
            raise _not_found()
        return model

    def _register(self, project_id: str, folder: Path) -> None:
        """Remember which folder holds the project. The same path with a new device or
        inode number (a folder put back from a backup, a drive mounted again) is the same
        place, so it takes the new identity. A copy elsewhere is refused while the folder
        already registered still holds the project."""
        identity = _identity(folder)
        with self._registry:
            known = self._models.get(project_id)
            if (
                isinstance(known, _Project)
                and known.identity != identity
                and not _same_place(known.folder, folder)
                and _holds(known.folder, project_id)
            ):
                raise _invalid(
                    "path",
                    "A project with this id is already open from another folder: a copied "
                    "project folder keeps its id. Start a new project from one of its versions.",
                )
            self._models[project_id] = _Project(folder, identity)

    def _project(self, model_id: str, model: _Project) -> dict[str, Any]:
        project = _read_project(model.folder)
        if project["id"] != model_id:
            raise ReviewError("workspace_failure", "The project folder now holds another project.")
        return project

    def _describe(
        self, model_id: str, model: _Project | _File
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """The summary every answer starts with, and the version records, oldest first."""
        if isinstance(model, _File):
            digest = model.revision.removeprefix("sha256:")
            record = {
                "version": model.revision,
                "description": _clip(f"Opened read-only from {model.name}"),
                "created_at": model.opened_at,
                "parent_version": None,
                "sha256": digest,
                "summary": None,
            }
            summary = {
                "model_id": model_id,
                "kind": "file",
                "name": model.name,
                "editable": False,
                "container": model.container,
                "created_at": model.opened_at,
                "current_revision": model.revision,
                "version_count": 1,
                "source": {"file": model.name, "sha256": digest, "origin": "file"},
            }
            return summary, [record]
        project = self._project(model_id, model)
        summary = {
            "model_id": model_id,
            "kind": "project",
            "name": project["name"],
            "editable": True,
            "container": project["container"],
            "created_at": project["created_at"],
            "current_revision": project["current_version"],
            "version_count": len(project["versions"]),
            "source": dict(project["source"]),
        }
        return summary, project["versions"]

    def _document(self, model: _Project, record: Mapping[str, Any]) -> dict[str, Any]:
        """A version's document. A file that is gone, or whose bytes no longer match
        project.json, makes that revision unavailable: not_found, as the interface asks."""
        # The name comes from the checked label, never from the file field as written.
        path = model.folder / VERSIONS / f"{record['version']}.yaml"
        try:
            data = _read_no_link(path, MAX_DOCUMENT_BYTES)
        except (FileNotFoundError, NotADirectoryError) as exc:
            raise _version_gone() from exc
        except OSError as exc:
            if exc.errno in (errno.ELOOP, errno.EFBIG):  # a link there, or changed outside
                raise _version_gone() from exc
            raise _unreadable() from exc
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise _version_gone()
        try:
            return _load(data)
        except ValueError as exc:  # unreachable unless SHA-256 collides
            raise _version_gone() from exc

    def _append(
        self,
        model: _Project,
        project: dict[str, Any],
        data: bytes,
        description: str | None,
        summary: dict[str, Any] | None,
    ) -> str:
        label = version_label(len(project["versions"]) + 1)
        target = model.folder / VERSIONS / f"{label}.yaml"
        if os.path.lexists(target):
            raise ReviewError(
                "workspace_failure",
                f"The versions folder already has a {label}.yaml that project.json does not "
                "list, left by an interrupted save or put there by hand. Move it out, then save.",
            )
        record = {
            "version": label,
            "file": f"{VERSIONS}/{label}.yaml",
            "description": description,
            "created_at": self._now(),
            "parent_version": project["current_version"],
            "sha256": hashlib.sha256(data).hexdigest(),
            "summary": summary,
        }
        updated = {**project, "current_version": label, "versions": [*project["versions"], record]}
        payload = _json_bytes(updated)
        if len(payload) > MAX_PROJECT_BYTES:  # before anything is written
            raise _invalid(
                "project",
                f"Another version would make project.json larger than {_mib(MAX_PROJECT_BYTES)}, "
                "the most the engine reads. Start a new project from the current version to "
                "save more.",
            )
        try:
            _put(target, data, replace=False)
        except OSError as exc:
            raise _save_failure() from exc
        try:
            _put(model.folder / PROJECT_FILE, payload, replace=True)  # commit point
        except OSError as exc:
            with suppress(OSError):
                os.unlink(target)
            raise _save_failure() from exc
        return label

    @contextmanager
    def _lock(self, model: _Project) -> Iterator[None]:
        """One save per project at a time: a lock this process's threads share, then an
        flock on the project's versions folder, which every process saving to it takes."""
        with _THREAD_LOCKS_GUARD:
            lock = _THREAD_LOCKS.setdefault(model.identity, threading.Lock())
        if not lock.acquire(timeout=LOCK_TIMEOUT_S):
            raise _busy()
        try:
            with _folder_lock(model.folder / VERSIONS):
                yield
        finally:
            lock.release()

    # Checks

    def _fitting_container(self, plain: Mapping[str, Any]) -> str:
        names = set(plain)
        for container in FITTING_CONTAINERS:
            if names <= self._containers[container]:
                return container
        unknown = sorted(names - frozenset().union(*self._containers.values()))
        if unknown:
            raise _invalid(_clip(unknown[0]), "No model container has a collection with this name.")
        raise _invalid("model", "No model container holds all of these collections together.")

    def _checked(self, plain: dict[str, Any], container: str) -> bytes:
        """Every check the engine can make; returns the YAML to store."""
        for name, records in plain.items():
            if name not in self._containers[container]:
                raise _invalid(_clip(name), f"{container} has no collection with this name.")
            if records is not None and type(records) is not list:
                raise _invalid(name, "Expected a list of records.")
        if self.schema_check:
            _schema_check(plain, container)
        else:
            _bundled_schema_check(plain, self._schemas[container])
        try:
            # The engine's own checks, as GET /graph and GET /risk apply them: unique ids,
            # resolving references, the attack graph, and the rating and impact values.
            if not project_model_graph(plain).nodes:
                raise GraphError("expected at least one model object")
            assess_document(plain, matrix=MATRIX_ID)
        except ValueError as exc:  # GraphError is a ValueError
            raise _invalid("model", _clip(f"Model check: {exc}")) from exc
        data = _dump(plain)
        if len(data) > MAX_DOCUMENT_BYTES:
            raise _invalid("model", "The model is larger than 16 MiB.")
        try:
            same = _load(data) == plain
        except ValueError:
            same = False
        if not same:
            raise _invalid("model", "The model would not read back unchanged from YAML.")
        return data

    # Ids and times

    def _now(self) -> str:
        return self._clock().astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    def _new_token(self, size: int) -> str:
        token = self._token(size)
        if not re.fullmatch(f"[0-9a-f]{{{2 * size}}}", token):
            raise RuntimeError("the token factory must return lower-case hex")
        return token


# Errors: transport-safe, never a path (engine/review_workspace.py)


def _invalid(field: str, message: str) -> ReviewError:
    return ReviewError("validation_error", message, field=field)


def _not_found() -> ReviewError:
    return ReviewError("not_found", "This model is not open in the engine, or has no such version.")


def _unreadable() -> ReviewError:
    return ReviewError("workspace_failure", "The project folder could not be read.")


def _linked_versions() -> ReviewError:
    return ReviewError(
        "workspace_failure",
        "The project's versions folder is missing, or is a link or not a folder.",
    )


def _version_gone() -> ReviewError:
    return ReviewError(
        "not_found", "This version's file is missing, or was changed outside the app."
    )


def _save_failure() -> ReviewError:
    return ReviewError("save_failure", "The model could not be saved. Retry your changes.")


def _busy() -> ReviewError:
    return ReviewError("save_failure", "Another save of this project is in progress. Retry.")


def _mib(size: int) -> str:
    return f"{size / (1024 * 1024):g} MiB"


def _clip(text: str, limit: int = MESSAGE_LIMIT) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _require_id(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > MAX_ID_LENGTH:
        raise _invalid(field, f"Expected an id of 1 to {MAX_ID_LENGTH} characters.")


def _require_current(current: str, expected: str) -> None:
    if expected != current:
        raise ReviewError(
            "revision_conflict",
            "A newer version was saved. Reload before retrying.",
            current_revision=current,
        )


def _name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _invalid("name", "Expected a project name.")
    return value.strip()[:MAX_NAME_LENGTH]


def _description(value: Any) -> str | None:
    if value is not None and (not isinstance(value, str) or len(value) > MAX_DESCRIPTION_LENGTH):
        raise _invalid(
            "description", f"Expected text of at most {MAX_DESCRIPTION_LENGTH} characters."
        )
    return value


def _summary(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise _invalid("summary", "Expected a JSON object.")
    plain = _json_value(value, "summary", 0, MAX_SUMMARY_DEPTH)
    # Measured as project.json holds it, indented, so a deep or long summary cannot grow
    # there past what was checked.
    if len(json.dumps(plain, indent=2, ensure_ascii=False)) > MAX_SUMMARY_BYTES:
        raise _invalid(
            "summary", f"The summary is larger than {MAX_SUMMARY_BYTES // 1024} KiB as written."
        )
    return plain


def _json_value(value: Any, where: str, depth: int, limit: int = MAX_DEPTH) -> Any:
    """A copy of a JSON value: text, finite numbers, true/false, null, lists, objects."""
    if depth > limit:
        raise _invalid(where, f"Nested deeper than {limit} levels.")
    kind = type(value)
    if value is None or kind in (str, bool, int):
        return value
    if kind is float:
        if not math.isfinite(value):
            raise _invalid(where, "Numbers must be finite.")
        return value
    if isinstance(value, Mapping):
        if not all(type(key) is str for key in value):
            raise _invalid(where, "Every key must be text.")
        return {key: _json_value(item, where, depth + 1, limit) for key, item in value.items()}
    if kind is list:
        return [_json_value(item, where, depth + 1, limit) for item in value]
    raise _invalid(where, f"A {kind.__name__} value is not JSON.")


# Project files


def _version(project: Mapping[str, Any], revision: str) -> dict[str, Any]:
    return _find(project["versions"], revision)


def _find(records: list[dict[str, Any]], revision: str) -> dict[str, Any]:
    for record in records:
        if record["version"] == revision:
            return record
    raise _not_found()


def _public(record: Mapping[str, Any], records: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    """A version's metadata for the app: its number for display ("Version 4"), no file name.

    A read-only file has one revision and no version number.
    """
    number = records.index(record) + 1 if kind == "project" else None
    return {"number": number, **{key: value for key, value in record.items() if key != "file"}}


def _valid_project(project: Any) -> bool:
    """project.json as this module writes it; anything else is damaged, never guessed at."""
    if not isinstance(project, dict) or project.get("format") != FORMAT:
        return False
    if project.get("format_version") != FORMAT_VERSION:
        return False
    if not isinstance(project.get("id"), str) or not _PROJECT_ID.fullmatch(project["id"]):
        return False
    if not all(isinstance(project.get(key), str) for key in ("name", "created_at")):
        return False
    source = project.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("file"), str):
        return False
    if not isinstance(source.get("sha256"), str) or not _DIGEST.fullmatch(source["sha256"]):
        return False
    if project.get("container") not in CONTAINER_FILES:
        return False
    versions = project.get("versions")
    if not isinstance(versions, list) or not versions:
        return False
    parent = None
    for number, record in enumerate(versions, 1):
        label = version_label(number)
        if not isinstance(record, dict) or record.get("version") != label:
            return False
        if (
            record.get("file") != f"{VERSIONS}/{label}.yaml"
            or record.get("parent_version") != parent
        ):
            return False
        if not isinstance(record.get("created_at"), str):
            return False
        if not isinstance(record.get("sha256"), str) or not _DIGEST.fullmatch(record["sha256"]):
            return False
        if not isinstance(record.get("description"), str | None):
            return False
        if not isinstance(record.get("summary"), dict | None):
            return False
        parent = label
    # v001 is the original's bytes, so it has the source's digest.
    return project.get("current_version") == parent and versions[0]["sha256"] == source["sha256"]


def _read_project(folder: Path) -> dict[str, Any]:
    """project.json, after checking that it and versions/ are the folder's own file and
    folder: a link there would make reads, writes and the lock reach somewhere else."""
    try:
        raw = _read_no_link(folder / PROJECT_FILE, MAX_PROJECT_BYTES)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise ReviewError("not_found", "No tmodel project was found in this folder.") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ReviewError(
                "workspace_failure",
                "project.json must be a regular file in the project folder, not a link or "
                "anything else.",
            ) from exc
        raise _unreadable() from exc
    try:
        versions = os.lstat(folder / VERSIONS).st_mode
    except OSError:
        versions = None
    if versions is None or not stat.S_ISDIR(versions):
        raise _linked_versions()
    try:
        project = json.loads(raw)
    except ValueError as exc:
        raise _unreadable() from exc
    if not _valid_project(project):
        raise ReviewError(
            "workspace_failure",
            "project.json is damaged, or was written by a newer version of tmodel.",
        )
    return project


def _holds(folder: Path, project_id: str) -> bool:
    """Whether `folder` still holds this project (a moved or deleted one does not)."""
    try:
        return _read_project(folder)["id"] == project_id
    except ReviewError:
        return False


def _same_place(one: Path, other: Path) -> bool:
    return os.path.realpath(one) == os.path.realpath(other)


def _read_no_link(path: Path, limit: int) -> bytes:
    """A regular file's bytes, at most `limit`, the most the engine writes there.

    A link there is refused (ELOOP), never followed; so is anything but a regular file.
    """
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags | getattr(os, "O_NONBLOCK", 0))
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(errno.ELOOP, "not a regular file")
        chunks, size = [], 0
        while chunk := os.read(descriptor, 1 << 20):
            size += len(chunk)
            if size > limit:
                raise OSError(errno.EFBIG, "larger than the engine ever writes")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _identity(folder: Path) -> tuple[int, int]:
    try:
        info = os.stat(folder)
    except OSError as exc:
        raise ReviewError("not_found", "The project folder was not found.") from exc
    return info.st_dev, info.st_ino


def _snapshot(model: _File) -> dict[str, Any]:
    try:
        return _load(model.data)
    except ValueError as exc:  # it was read and checked when opened
        raise _unreadable() from exc


# Sources, paths and containers


def _host_path(value: Any, field: str = "path") -> Path:
    """An absolute path from the host; a relative one would depend on the engine's folder."""
    text = os.fspath(value) if isinstance(value, str | os.PathLike) else None
    if (
        not isinstance(text, str)
        or not text
        or len(text) > MAX_PATH_LENGTH
        or "\x00" in text
        or not os.path.isabs(text)
    ):
        raise _invalid(field, "Expected an absolute path.")
    return Path(text)


def _project_folder(value: Any) -> Path:
    """The folder the host passed, with links resolved, so the project is made and kept
    in the folder a link names; never inside the example models folder or holding it."""
    path = _host_path(value)
    examples = core.APPROVED_VECTOR_DIRECTORY.resolve()
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as exc:  # a symlink loop
        raise _invalid("path", "The folder's path could not be resolved.") from exc
    if resolved.is_relative_to(examples) or examples.is_relative_to(resolved):
        raise _invalid("path", "A project folder must be outside the example models folder.")
    return resolved


def _example(source_file: Any) -> tuple[str, bytes]:
    """A model GET /models lists: its file name and its exact bytes, read once."""
    if not isinstance(source_file, str) or not source_file or len(source_file) > MAX_ID_LENGTH:
        raise _invalid("source_file", "Expected the file of a model that GET /models lists.")
    try:
        listed = core.list_models()["models"]
    except OSError as exc:
        raise ReviewError("workspace_failure", "The example models could not be listed.") from exc
    if not any(model["file"] == source_file for model in listed):
        raise ReviewError("not_found", "Choose a model from the list of example models.")
    try:
        # The same containment check GET /graph applies to an example file.
        path = core._approved_vector_path(source_file)
    except ValueError as exc:  # GraphError is a ValueError
        raise ReviewError("workspace_failure", "The example model could not be read.") from exc
    return path.name, _read_file(path, "source_file")


def _read_file(path: Path, field: str = "path") -> bytes:
    """A regular file's bytes (never a pipe or a device), at most 16 MiB."""
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise ReviewError("not_found", "The file was not found.") from exc
    except OSError as exc:
        raise ReviewError("workspace_failure", "The file could not be read.") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise _invalid(field, "Expected a model file.")
        chunks, size = [], 0
        while chunk := os.read(descriptor, 1 << 20):
            size += len(chunk)
            if size > MAX_DOCUMENT_BYTES:
                raise _invalid(field, "The file is larger than 16 MiB.")
            chunks.append(chunk)
    except OSError as exc:
        raise ReviewError("workspace_failure", "The file could not be read.") from exc
    finally:
        os.close(descriptor)
    return b"".join(chunks)


def _parsed(data: bytes, field: str) -> dict[str, Any]:
    try:
        return _load(data)
    except ValueError as exc:
        raise _invalid(field, "Expected a YAML model: a mapping of collections.") from exc


def _family_container(source_file: str) -> str | None:
    return next(
        (name for prefix, name in FAMILY_CONTAINERS if source_file.startswith(prefix)), None
    )


def _container_collections(container: str) -> frozenset[str]:
    """The collections a container exposes, read from its file (no LinkML needed)."""
    try:
        text = (SCHEMA_DIRECTORY / CONTAINER_FILES[container]).read_text(encoding="utf-8")
        return frozenset(yaml.safe_load(text)["classes"][container]["attributes"])
    except (OSError, ValueError, yaml.YAMLError, KeyError, TypeError) as exc:
        raise ValueError(f"cannot read the {container} schema container") from exc


def _schema_check(plain: dict[str, Any], container: str) -> None:
    """LinkML's check of the container class, as `linkml-validate` runs it in CI."""
    with _LINKML_LOCK:
        try:
            validator = _VALIDATORS.get(container)
            if validator is None:
                from linkml.validator import Validator
                from linkml.validator.plugins import JsonschemaValidationPlugin

                validator = Validator(
                    str(SCHEMA_DIRECTORY / CONTAINER_FILES[container]),
                    validation_plugins=[JsonschemaValidationPlugin(closed=True)],
                )
                _VALIDATORS[container] = validator
            results = list(validator.validate(plain, container).results)
        except Exception as exc:  # an unusable validator must not let a save through
            raise ReviewError("workspace_failure", "The schema check could not run.") from exc
    errors = [r for r in results if getattr(r.severity, "value", r.severity) in ("ERROR", "FATAL")]
    if errors:
        source = getattr(errors[0], "source", None)
        detail = getattr(source, "message", None) or errors[0].message
        more = f" ({len(errors) - 1} more)" if len(errors) > 1 else ""
        raise _invalid(
            _pointer(list(getattr(source, "absolute_path", None) or [])),
            _clip(f"Schema check ({container}): {detail}") + more,
        )


def _bundled_schemas() -> dict[str, Container]:
    try:
        return {name: load_container(SCHEMA_DIRECTORY, name) for name in CONTAINER_FILES}
    except (SchemaError, yaml.YAMLError) as exc:
        raise ValueError(
            "cannot read the schema containers and the object model they import"
        ) from exc


def _bundled_schema_check(plain: dict[str, Any], schema: Container) -> None:
    """The same container check without LinkML (engine/schema_check.py, DL-0081)."""
    problems = schema_problems(plain, schema)
    if problems:
        more = f" ({len(problems) - 1} more)" if len(problems) > 1 else ""
        raise _invalid(
            _clip(problems[0].field),
            _clip(f"Schema check ({schema.root}): {problems[0].message}") + more,
        )


def _pointer(path: list[Any]) -> str:
    field = ""
    for part in path:
        field += f"[{part}]" if isinstance(part, int) else (f".{part}" if field else str(part))
    return _clip(field) if field else "model"


# Documents


def _plain_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, Mapping):
        raise _invalid("model", "Expected the model as a mapping of collections.")
    return _plain(document, "model", 0)


def _plain(value: Any, where: str, depth: int) -> Any:
    """A YAML-ready copy: text, finite numbers, true/false, null, dates, lists, mappings."""
    if depth > MAX_DEPTH:
        raise _invalid(where, f"Nested deeper than {MAX_DEPTH} levels.")
    kind = type(value)
    if value is None or kind in (str, bool, int, date, datetime):
        return value
    if kind is float:
        if not math.isfinite(value):
            raise _invalid(where, "Numbers must be finite.")
        return value
    if isinstance(value, Mapping):
        plain = {}
        for key, item in value.items():
            if type(key) is not str:
                raise _invalid(where, "Every key must be text.")
            plain[key] = _plain(
                item, _clip(key if where == "model" else f"{where}.{key}"), depth + 1
            )
        return plain
    if kind is list:
        return [_plain(item, f"{where}[{i}]", depth + 1) for i, item in enumerate(value)]
    raise _invalid(where, f"A {kind.__name__} value cannot be saved in the YAML model.")


class _Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True  # write shared values out in full: no anchors in a saved model


def _dump(plain: dict[str, Any]) -> bytes:
    try:
        text = yaml.dump(
            plain,
            Dumper=_Dumper,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=2**31 - 1,  # no folded lines: each value reads back as written
        )
        return text.encode("utf-8")
    except (yaml.YAMLError, UnicodeError) as exc:
        raise _invalid("model", "The model cannot be written as YAML.") from exc


def _load(data: bytes) -> dict[str, Any]:
    """Parse a model the way the engine reads one (yaml.safe_load). Raises ValueError."""
    try:
        document = yaml.safe_load(data.decode("utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ValueError("not readable YAML") from exc
    if not isinstance(document, dict):
        raise ValueError("not a mapping")
    return document


def _json_safe(value: Any) -> Any:
    if isinstance(value, date | datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# Files. Each step is its own function, so the tests can make any one of them fail.


def _build_project(target: Path, data: bytes, project: dict[str, Any]) -> None:
    """Make the project in `target`, a new folder or an empty one.

    A new folder is assembled beside it and renamed into place in one step. An existing
    empty folder is filled in place, so it keeps its permissions, its extended attributes
    (Finder tags among them) and any `.DS_Store`; project.json goes in last, and a failure
    before it is in place removes what was written.
    """
    parent = target.parent
    if not parent.is_dir():
        raise _invalid("path", "The folder that should hold the project does not exist.")
    if not os.path.lexists(target):
        _assemble_beside(target, data, project)
        return
    if not target.is_dir():
        raise _invalid("path", "Expected a folder.")
    try:
        names = os.listdir(target)
    except OSError as exc:
        raise _invalid("path", "The folder could not be read.") from exc
    if PROJECT_FILE in names:
        raise _invalid("path", "This folder already holds a project. Open it instead.")
    if any(name != ".DS_Store" and not _OWN_TEMPORARY.fullmatch(name) for name in names):
        raise _invalid("path", "Choose an empty folder for a new project.")
    _fill_in_place(target, data, project)


def _project_files(folder: Path, data: bytes, project: dict[str, Any]) -> list[tuple[Path, bytes]]:
    """The files of a new project, in the order they are written: project.json last."""
    first = folder / VERSIONS / f"{project['current_version']}.yaml"
    return [(folder / ORIGINAL, data), (first, data), (folder / PROJECT_FILE, _json_bytes(project))]


def _assemble_beside(target: Path, data: bytes, project: dict[str, Any]) -> None:
    parent = target.parent
    staging = parent / f".tmodel-new-project-{secrets.token_hex(6)}"
    try:
        _make_directory(staging)
        _make_directory(staging / VERSIONS)
        for path, content in _project_files(staging, data, project):
            _put(path, content, replace=False)
        if os.path.lexists(target):
            raise FileExistsError("the chosen folder appeared meanwhile")
        _rename_directory(staging, target)  # the commit point: the project appears whole
    except OSError as exc:
        shutil.rmtree(staging, ignore_errors=True)
        raise _save_failure() from exc
    with suppress(OSError):
        _fsync_directory(parent)


def _fill_in_place(target: Path, data: bytes, project: dict[str, Any]) -> None:
    made: list[Path] = []
    try:
        _make_directory(target / VERSIONS)
        made.append(target / VERSIONS)
        for path, content in _project_files(target, data, project):
            _put(path, content, replace=False)  # project.json, last, is the commit point
            made.append(path)
    except OSError as exc:
        for path in reversed(made):  # only what this call wrote: anything else stays
            with suppress(OSError):
                if path.name == VERSIONS:
                    os.rmdir(path)  # it stays if something else is in it by now
                else:
                    os.unlink(path)
        raise _save_failure() from exc


def _put(path: Path, data: bytes, *, replace: bool) -> None:
    """Write `data` at `path`: a temporary file, flushed, then put in place.

    With replace=False the path is new and stays new. The file goes in with a hard link,
    which fails if anything is there, even a file another program wrote a moment before;
    on a volume without hard links (FAT, exFAT) a check and then a rename put it in, with
    a moment between the two. On any failure nothing is left at the path. With
    replace=True a rename puts it in, the commit point, so the folder flush after it is
    best effort: once renamed, the new content is in place.
    """
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        descriptor = _create(temporary)
        try:
            _write_all(descriptor, data)
            _fsync(descriptor)
        finally:
            os.close(descriptor)
        if replace:
            _replace(temporary, path)
        else:
            _place(temporary, path)
    except BaseException:
        with suppress(OSError):
            os.unlink(temporary)
        raise
    if replace:
        with suppress(OSError):
            _fsync_directory(path.parent)
        return
    try:
        _fsync_directory(path.parent)
    except BaseException:
        with suppress(OSError):
            os.unlink(path)
        raise


# What link() can answer on a volume without hard links, such as FAT or exFAT: EPERM
# (Linux's link(2) names it), ENOTSUP, EOPNOTSUPP or ENOSYS.
_NO_HARD_LINKS = frozenset({errno.EPERM, errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS})


def _place(temporary: Path, path: Path) -> None:
    """Put a new file at `path` without ever replacing what is there."""
    try:
        _link(temporary, path)
    except OSError as exc:
        if exc.errno not in _NO_HARD_LINKS:
            raise  # FileExistsError among them: something is already there
        if os.path.lexists(path):
            raise FileExistsError("refusing to replace a saved file") from exc
        _replace(temporary, path)
        return
    with suppress(OSError):
        os.unlink(temporary)


def _create(path: Path) -> int:
    return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        view = view[os.write(descriptor, view) :]


def _flush(descriptor: int) -> None:
    """Flush to the disk itself. On macOS fsync stops at the drive's cache, so ask for
    F_FULLFSYNC there, and fall back to fsync on a volume that does not support it."""
    if fcntl is not None and hasattr(fcntl, "F_FULLFSYNC"):
        try:
            fcntl.fcntl(descriptor, fcntl.F_FULLFSYNC)
            return
        except OSError:
            pass
    os.fsync(descriptor)


def _fsync(descriptor: int) -> None:
    _flush(descriptor)


def _replace(source: Path, target: Path) -> None:
    os.replace(source, target)


def _link(source: Path, target: Path) -> None:
    os.link(source, target)


def _rename_directory(source: Path, target: Path) -> None:
    os.rename(source, target)


def _fsync_directory(path: Path) -> None:
    """Make a rename in `path` durable. Python cannot open a folder on Windows, so this
    step is skipped there."""
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        _flush(descriptor)
    finally:
        os.close(descriptor)


def _make_directory(path: Path) -> None:
    os.mkdir(path, 0o700)


@contextmanager
def _folder_lock(folder: Path) -> Iterator[None]:
    """An exclusive flock on a folder, never through a link; released when its
    descriptor closes."""
    if fcntl is None:
        yield
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(folder, flags)
    except OSError as exc:
        if exc.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
            raise _linked_versions() from exc
        raise _save_failure() from exc
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise _busy() from None
                time.sleep(0.01)
            except OSError as exc:
                raise _save_failure() from exc
        yield
    finally:
        os.close(descriptor)
