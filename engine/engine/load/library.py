"""Load the library's records into typed objects (#60, #139; PLAN-0002 §4 B1).

Input is a checkout of the Threat-Radar/library repo, normally the `library/`
submodule pinned by this repo. One record is `records/<body>/<id>/record.yaml`,
the current version of one document line (library record schema, `storage`).
Superseded versions under a record's `versions/` folder are listed by name and
not loaded, matching the library's own `bin/validate`.

Read-only: files are only ever opened for reading, and nothing is written in the
library or anywhere else. Files in git are the source of truth; anything built
from these objects is a rebuildable copy (ADR-0004, ADR-0008).

Deterministic: the same files give the same objects in the same order. Records
are sorted by id, every list keeps the order the file gives, and
`Library.digest` fingerprints the exact bytes that were read.

Every value is read as the text the record wrote (PyYAML's BaseLoader), never
guessed into a number or a date: as a float, the arXiv id 2409.06390 would lose
its last digit and the version 1.10 would become 1.1. The few typed fields
(`content.local`, `content.pages`) are converted explicitly.

These are the engine's read models of library records, not classes of the tmodel
schema: tmodel refers to library records by id only (schema slot `source_ref`).

For serving (#140), `configured_root()` names the library the engine reads, and
`cached_library()` keeps one loaded copy, reloading only when a file it reads
has changed.
"""

from __future__ import annotations

import hashlib
import os
import re
import threading
from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass, field
from functools import cached_property
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

# Mirrors the library's bin/validate: the keys every record must have.
REQUIRED = ("schema", "id", "body", "type", "title", "content", "tags", "status")
RECORD_ID = re.compile(r"[a-z0-9][a-z0-9-]*")
WHOLE_NUMBER = re.compile(r"[0-9]+")  # ASCII digits only, so int() always accepts it
RECORD_GLOB = "records/*/*/record.yaml"
# What a record's folder adds to its record.yaml: whether a summary exists, and old versions.
NOTED_GLOBS = ("records/*/*/summary.md", "records/*/*/versions/*/record.yaml")
# Points the engine at a library checkout other than this repo's pinned submodule.
LIBRARY_ENV = "TMODEL_LIBRARY"


class LibraryError(ValueError):
    """The library, or a record in it, cannot be loaded.

    The message names every file that failed; `problems` holds one line per file,
    each starting with the file's path relative to the library root.
    """

    def __init__(self, message: str, problems: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.problems = problems


class _BadRecord(Exception):
    """One record is malformed. Internal: becomes a line in LibraryError.problems."""


@dataclass(frozen=True)
class Content:
    """Where the document lives and what was fetched (the record's `content`)."""

    url: str | None = None
    retrieved: str | None = None  # empty in the file until someone fetches it
    sha256: str | None = None
    local: bool = False  # the library schema says this MUST stay false
    media_type: str | None = None
    pages: int | None = None


@dataclass(frozen=True)
class Citation:
    """One `cites` entry: a reference the document itself makes, not our judgement.

    A bare entry is a library record id (`record`). Otherwise the entry describes
    a target the library may not hold; `ref` is then the document's own label for
    it (a footnote mark or section name), not a record id.
    """

    record: str | None = None
    ref: str | None = None
    title: str | None = None
    url: str | None = None
    locator: str | None = None


@dataclass(frozen=True)
class Implementation:
    """Something that implements the document. A one-line entry is kept whole in `name`."""

    name: str
    commercial: bool = False
    url: str | None = None
    license: str | None = None
    language: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Artifact:
    """One distilled artifact (`distillation.artifacts`), such as extracted requirements."""

    kind: str
    path: str  # relative to the record's folder
    coverage: str = ""
    reviewed_by: str = ""
    generated_from: str | None = None

    @property
    def reviewed(self) -> bool:
        """An empty `reviewed_by` means readable but not checked by a person (library schema)."""
        return bool(self.reviewed_by)


@dataclass(frozen=True)
class Usefulness:
    """The library's verdict on whether the document is worth keeping, with its reason."""

    verdict: str
    reason: str | None = None
    assessed: str | None = None


@dataclass(frozen=True)
class LibraryRecord:
    """One library record, typed. `raw` keeps the whole file, read-only, as written."""

    id: str
    body: str
    type: str
    title: str
    status: str
    path: str  # the record.yaml, relative to the library root
    short_title: str | None = None
    maturity: str | None = None
    date: str | None = None
    version: str | None = None
    publisher: str | None = None
    topic: str | None = None
    owner: str | None = None
    confidence: str | None = None
    duplicate_of: str | None = None
    authors: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    bears_on: tuple[str, ...] = ()
    identifiers: tuple[tuple[str, str], ...] = ()  # (scheme, value), in file order
    content: Content = field(default_factory=Content)
    relations: tuple[tuple[str, tuple[str, ...]], ...] = ()  # (kind, record ids)
    cites: tuple[Citation, ...] = ()
    applicability: tuple[tuple[str, str], ...] = ()  # (axis, rating)
    usefulness: Usefulness | None = None
    implementations: tuple[Implementation, ...] = ()
    artifacts: tuple[Artifact, ...] = ()
    profile: str | None = None  # distillation.profile; "full" means a complete extraction
    summary: str | None = None  # summary.md, relative to the library root
    versions: tuple[str, ...] = ()  # superseded versions kept under versions/
    raw: Mapping[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def identifier(self, scheme: str) -> str | None:
        """The identifier for one scheme (doi, rfc, iso, url, ...), if the record has it."""
        return next((value for key, value in self.identifiers if key == scheme), None)

    def related(self, kind: str) -> tuple[str, ...]:
        """Record ids under one relation (see_also, supersedes, part_of, ...)."""
        return next((ids for key, ids in self.relations if key == kind), ())

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready, in a fixed key order. `raw` is left out."""
        return {
            "id": self.id,
            "body": self.body,
            "type": self.type,
            "title": self.title,
            "short_title": self.short_title,
            "status": self.status,
            "maturity": self.maturity,
            "date": self.date,
            "version": self.version,
            "publisher": self.publisher,
            "topic": self.topic,
            "owner": self.owner,
            "confidence": self.confidence,
            "duplicate_of": self.duplicate_of,
            "authors": list(self.authors),
            "tags": list(self.tags),
            "bears_on": list(self.bears_on),
            "identifiers": dict(self.identifiers),
            "content": asdict(self.content),
            "relations": {kind: list(ids) for kind, ids in self.relations},
            "cites": [asdict(c) for c in self.cites],
            "applicability": dict(self.applicability),
            "usefulness": asdict(self.usefulness) if self.usefulness else None,
            "implementations": [asdict(i) for i in self.implementations],
            "artifacts": [{**asdict(a), "reviewed": a.reviewed} for a in self.artifacts],
            "profile": self.profile,
            "summary": self.summary,
            "versions": list(self.versions),
            "path": self.path,
        }


@dataclass(frozen=True)
class Library:
    """Every record that loaded, sorted by id, plus a fingerprint of what was read."""

    root: str
    records: tuple[LibraryRecord, ...]
    digest: str  # sha256 over each record.yaml's relative path and bytes, in path order
    problems: tuple[str, ...] = ()  # only with strict=False: files that failed to load

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[LibraryRecord]:
        return iter(self.records)

    @cached_property
    def _by_id(self) -> Mapping[str, LibraryRecord]:
        return MappingProxyType({r.id: r for r in self.records})

    def get(self, record_id: str) -> LibraryRecord | None:
        return self._by_id.get(record_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "digest": self.digest,
            "count": len(self.records),
            "records": [r.to_dict() for r in self.records],
            "problems": list(self.problems),
        }


def load_library(root: str | Path, *, strict: bool = True) -> Library:
    """Load every record under `root` (a library checkout).

    With `strict` (the default), any record that fails raises one LibraryError
    that lists every failing file. With `strict=False`, failing records are left
    out and listed in `Library.problems` instead.
    """
    root = _checkout(root)
    files = sorted(root.glob(RECORD_GLOB), key=lambda p: p.relative_to(root).as_posix())
    digest = hashlib.sha256()
    loaded: dict[str, LibraryRecord] = {}
    problems: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            data = path.read_bytes()
        except OSError as exc:
            problems.append(f"{rel}: cannot read ({exc.strerror or exc})")
            continue
        digest.update(rel.encode("utf-8") + b"\0" + data + b"\0")
        try:
            record = _record(root, path, rel, data)
        except _BadRecord as exc:
            problems.append(f"{rel}: {exc}")
            continue
        if record.id in loaded:
            problems.append(f"{rel}: id '{record.id}' is also used by {loaded[record.id].path}")
            continue
        loaded[record.id] = record
    if problems and strict:
        count = f"{len(problems)} record{'s' if len(problems) != 1 else ''}"
        raise LibraryError(
            f"{root}: {count} failed to load:\n  " + "\n  ".join(problems), tuple(problems)
        )
    return Library(
        root=str(root),
        records=tuple(loaded[i] for i in sorted(loaded)),
        digest=digest.hexdigest(),
        problems=tuple(problems),
    )


def _checkout(root: str | Path) -> Path:
    """`root` made absolute, once it is known to hold `records/`; LibraryError if not.

    A path the system cannot look at counts as no library too: a folder inside one
    without read permission, a name that is too long, or a symlink loop.
    """
    try:
        path = Path(root).resolve()
        found = (path / "records").is_dir()
    except OSError as exc:  # is_dir() raises for these instead of returning False
        raise LibraryError(f"{root}: cannot read this folder ({exc.strerror or exc})") from exc
    except RuntimeError as exc:  # resolve() raises this for a symlink loop before Python 3.13
        raise LibraryError(f"{root}: cannot read this folder ({exc})") from exc
    if not found:
        raise LibraryError(
            f"{path}: no records/ folder; is this a library checkout? "
            "(an empty library/ usually means the submodule is not checked out: "
            "git submodule update --init library)"
        )
    return path


def configured_root() -> Path:
    """The library the engine serves: `$TMODEL_LIBRARY` if set, else the pinned submodule.

    The default is the `library/` folder at the root of this repo, which exists in a
    source checkout. A packaged engine has no repo around it, so it needs the
    variable (#124 decides how the app provides a library).
    """
    configured = os.environ.get(LIBRARY_ENV, "").strip()
    if configured:
        # os.path leaves "~name" as written when there is no such user, as the shell
        # does, so it reads as no library; Path.expanduser() would raise instead.
        return Path(os.path.expanduser(configured))
    return Path(__file__).resolve().parents[3] / "library"


_cache_lock = threading.Lock()
_cache: dict[str, tuple[tuple[tuple[str, str], ...], Library]] = {}


def _fingerprint(root: Path) -> tuple[tuple[str, str], ...]:
    """Every record file with the SHA-256 of its bytes, then every file the loader notes.

    Contents, not sizes and modification times, which an edit can keep (`cp -p` and
    `rsync -t` do). Noted files count by path only, since the loader only checks
    that they are there.
    """
    seen = []
    for path in sorted(root.glob(RECORD_GLOB)):
        try:
            data = path.read_bytes()
        except OSError:  # removed since the glob, or unreadable; the next call sees any change
            continue
        seen.append((path.relative_to(root).as_posix(), hashlib.sha256(data).hexdigest()))
    for pattern in NOTED_GLOBS:
        seen += [(p.relative_to(root).as_posix(), "") for p in sorted(root.glob(pattern))]
    return tuple(seen)


def cached_library(root: str | Path | None = None) -> Library:
    """`load_library(root, strict=False)`, kept until a file it reads changes.

    Loading every record takes about half a second, which is too slow to repeat on
    each request. Hashing the record files takes a few hundredths of a second, so
    each call hashes them and reloads only if something was added, removed or
    edited. With no `root`, it reads `configured_root()`. Like `load_library`, it
    raises LibraryError when the folder holds no `records/` or cannot be read.
    """
    root = _checkout(root if root is not None else configured_root())
    with _cache_lock:
        fingerprint = _fingerprint(root)
        cached = _cache.get(str(root))
        if cached is not None and cached[0] == fingerprint:
            return cached[1]
        library = load_library(root, strict=False)
        _cache[str(root)] = (fingerprint, library)
        return library


def _record(root: Path, path: Path, rel: str, data: bytes) -> LibraryRecord:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _BadRecord("not UTF-8 text") from exc
    try:
        doc = yaml.load(text, Loader=yaml.BaseLoader)  # strings only; builds no objects
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark else ""
        reason = " ".join(str(getattr(exc, "problem", None) or exc).split())  # one line
        raise _BadRecord(f"not valid YAML{where} ({reason})") from exc
    if not isinstance(doc, dict):
        raise _BadRecord("expected a mapping at the top level")

    missing = [key for key in REQUIRED if key not in doc]
    if missing:
        fields = "field" if len(missing) == 1 else "fields"
        raise _BadRecord(f"missing required {fields} {', '.join(repr(k) for k in missing)}")
    folder, shelf = path.parent.name, path.parent.parent.name
    record_id, body = _required(doc, "id"), _required(doc, "body")
    if record_id != folder:
        raise _BadRecord(f"id '{record_id}' does not match its folder '{folder}'")
    if not RECORD_ID.fullmatch(record_id):
        raise _BadRecord(f"id '{record_id}' is not kebab-case")
    if body != shelf:
        raise _BadRecord(f"body '{body}' does not match its folder '{shelf}'")

    distillation = _mapping(doc, "distillation")
    return LibraryRecord(
        id=record_id,
        body=body,
        type=_required(doc, "type"),
        title=_required(doc, "title"),
        status=_required(doc, "status"),
        path=rel,
        short_title=_text(doc, "short_title"),
        maturity=_text(doc, "maturity"),
        date=_text(doc, "date"),
        version=_text(doc, "version"),
        publisher=_text(doc, "publisher"),
        topic=_text(doc, "topic"),
        owner=_text(doc, "owner"),
        confidence=_text(doc, "confidence"),
        duplicate_of=_text(doc, "duplicate_of"),
        authors=_texts(doc, "authors"),
        tags=_texts(doc, "tags"),
        bears_on=_texts(doc, "bears_on"),
        identifiers=_pairs(doc, "identifiers"),
        content=_content(doc),
        relations=_relations(doc),
        cites=_cites(doc),
        applicability=_pairs(doc, "applicability"),
        usefulness=_usefulness(doc),
        implementations=_implementations(doc),
        artifacts=_artifacts(distillation),
        profile=_text(distillation, "profile", "distillation.profile"),
        summary=_summary(path.parent, root),
        versions=_versions(path.parent / "versions"),
        raw=_freeze(doc),
    )


# The record's folder is read too. A folder the loader cannot read makes that record
# fail with its file named, like a malformed field, instead of stopping the whole load.


def _summary(folder: Path, root: Path) -> str | None:
    """The record's summary.md, relative to the library root, if there is one."""
    summary = folder / "summary.md"
    try:
        present = summary.is_file()
    except OSError as exc:  # some Python versions raise here instead of returning False
        raise _BadRecord(f"cannot check summary.md ({exc.strerror or exc})") from exc
    return summary.relative_to(root).as_posix() if present else None


def _versions(folder: Path) -> tuple[str, ...]:
    """Names of the superseded versions kept under a record's versions/ folder."""
    try:
        if not folder.is_dir():
            return ()
        return tuple(sorted(v.name for v in folder.iterdir() if (v / "record.yaml").is_file()))
    except OSError as exc:
        raise _BadRecord(f"cannot read versions/ ({exc.strerror or exc})") from exc


# --- field readers: each names the field it rejects -----------------------------


def _shape(value: Any) -> str:
    if isinstance(value, dict):
        return "mapping"
    if isinstance(value, list):
        return "list"
    return "text"


def _text(doc: Mapping[str, Any], key: str, name: str | None = None) -> str | None:
    """Optional text. A blank value counts as absent."""
    value = doc.get(key)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise _BadRecord(f"'{name or key}' should be text, found a {_shape(value)}")
    return value


def _required(doc: Mapping[str, Any], key: str) -> str:
    value = _text(doc, key)
    if value is None:
        raise _BadRecord(f"'{key}' is empty")
    return value


def _list(doc: Mapping[str, Any], key: str, name: str | None = None) -> list[Any]:
    value = doc.get(key)
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise _BadRecord(f"'{name or key}' should be a list, found {_shape(value)}")
    return value


def _mapping(doc: Mapping[str, Any], key: str, name: str | None = None) -> dict[str, Any]:
    value = doc.get(key)
    if value is None or value == "":
        return {}
    if not isinstance(value, dict):
        raise _BadRecord(f"'{name or key}' should be a mapping, found {_shape(value)}")
    return value


def _texts(doc: Mapping[str, Any], key: str, name: str | None = None) -> tuple[str, ...]:
    items = _list(doc, key, name)
    for item in items:
        if not isinstance(item, str):
            raise _BadRecord(f"'{name or key}' should list text, found a {_shape(item)}")
    return tuple(items)


def _pairs(doc: Mapping[str, Any], key: str) -> tuple[tuple[str, str], ...]:
    """A mapping of text to text, such as `identifiers`; blank values are dropped."""
    pairs = []
    for name, value in _mapping(doc, key).items():
        if value == "":
            continue
        if not isinstance(value, str):
            raise _BadRecord(f"'{key}.{name}' should be text, found a {_shape(value)}")
        pairs.append((name, value))
    return tuple(pairs)


def _content(doc: Mapping[str, Any]) -> Content:
    raw = _mapping(doc, "content")
    local = _text(raw, "local", "content.local")
    if local not in (None, "true", "false"):
        raise _BadRecord(f"'content.local' should be true or false, found '{local}'")
    pages = _text(raw, "pages", "content.pages")
    if pages is not None and not WHOLE_NUMBER.fullmatch(pages):  # not isdigit(): "²" passes it
        raise _BadRecord(f"'content.pages' should be a whole number, found '{pages}'")
    return Content(
        url=_text(raw, "url", "content.url"),
        retrieved=_text(raw, "retrieved", "content.retrieved"),
        sha256=_text(raw, "sha256", "content.sha256"),
        local=local == "true",
        media_type=_text(raw, "media_type", "content.media_type"),
        pages=int(pages) if pages is not None else None,
    )


def _relations(doc: Mapping[str, Any]) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Typed links to other records. Empty relation lists are left out."""
    relations = []
    for kind in _mapping(doc, "relations"):
        ids = _texts(doc["relations"], kind, f"relations.{kind}")
        if ids:
            relations.append((kind, ids))
    return tuple(relations)


def _cites(doc: Mapping[str, Any]) -> tuple[Citation, ...]:
    cites = []
    for item in _list(doc, "cites"):
        if isinstance(item, str):
            cites.append(Citation(record=item))
        elif isinstance(item, dict):
            cites.append(
                Citation(
                    ref=_text(item, "ref", "cites.ref"),
                    title=_text(item, "title", "cites.title"),
                    url=_text(item, "url", "cites.url"),
                    locator=_text(item, "locator", "cites.locator"),
                )
            )
        else:
            raise _BadRecord("'cites' entries should be a record id or a mapping")
    return tuple(cites)


def _usefulness(doc: Mapping[str, Any]) -> Usefulness | None:
    raw = _mapping(doc, "usefulness")
    verdict = _text(raw, "verdict", "usefulness.verdict")
    if verdict is None:
        return None
    return Usefulness(
        verdict=verdict,
        reason=_text(raw, "reason", "usefulness.reason"),
        assessed=_text(raw, "assessed", "usefulness.assessed"),
    )


def _implementations(doc: Mapping[str, Any]) -> tuple[Implementation, ...]:
    raw = _mapping(doc, "implementations")
    found = []
    for group, commercial in (("open_source", False), ("commercial", True)):
        for item in _list(raw, group, f"implementations.{group}"):
            if isinstance(item, str):
                found.append(Implementation(name=item, commercial=commercial))
                continue
            name = f"implementations.{group}"
            if not isinstance(item, dict) or _text(item, "name", f"{name}.name") is None:
                raise _BadRecord(f"'{name}' entries should be text or have a name")
            found.append(
                Implementation(
                    name=item["name"],
                    commercial=commercial,
                    url=_text(item, "url", f"{name}.url"),
                    license=_text(item, "license", f"{name}.license"),
                    language=_text(item, "language", f"{name}.language"),
                    note=_text(item, "note", f"{name}.note"),
                )
            )
    return tuple(found)


def _artifacts(distillation: Mapping[str, Any]) -> tuple[Artifact, ...]:
    artifacts = []
    for item in _list(distillation, "artifacts", "distillation.artifacts"):
        name = "distillation.artifacts"
        if not isinstance(item, dict):
            raise _BadRecord(f"'{name}' entries should be mappings")
        kind, path = _text(item, "kind", f"{name}.kind"), _text(item, "path", f"{name}.path")
        if kind is None or path is None:
            raise _BadRecord(f"'{name}' entries need a kind and a path")
        artifacts.append(
            Artifact(
                kind=kind,
                path=path,
                coverage=_text(item, "coverage", f"{name}.coverage") or "",
                reviewed_by=_text(item, "reviewed_by", f"{name}.reviewed_by") or "",
                generated_from=_text(item, "generated_from", f"{name}.generated_from"),
            )
        )
    return tuple(artifacts)


def _freeze(value: Any) -> Any:
    """A read-only copy: mappings become MappingProxyType, lists become tuples."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value
