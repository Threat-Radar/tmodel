"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine import __version__
from engine.graph import AttackGraph, GraphError
from engine.load.library import (
    Library,
    LibraryError,
    LibraryRecord,
    cached_library,
    configured_root,
)
from engine.load.vector import load_vector, load_vector_document
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths

ENGINE_NAME = "tmodel-engine"
APPROVED_VECTOR_DIRECTORY = Path(__file__).resolve().parents[2] / "spec" / "vectors"
LIBRARY_FILTERS = ("id", "type", "topic", "status")
# The library table view (#141, #58): what it can sort by, and what it counts for filter menus.
TABLE_OPTIONS = ("search", "sort", "order", "limit", "offset")
TABLE_SORTS = ("id", "title", "type", "shelf", "status", "maturity", "date", "publisher", "topic")
TABLE_FACETS = ("type", "status", "topic")


class Unavailable(RuntimeError):
    """Something the engine needs is missing, such as the library (the API answers 503)."""


def version() -> dict[str, Any]:
    """Engine and runtime version."""
    return {
        "engine": ENGINE_NAME,
        "version": __version__,
        "python": platform.python_version(),
    }


def health() -> dict[str, Any]:
    """Liveness check. Grows real checks (store reachable, library loaded) later."""
    return {"status": "ok", **version()}


def _values(query: Mapping[str, str], allowed: tuple[str, ...], noun: str) -> dict[str, str]:
    """The query's values, each checked to be one of `allowed` and to be non-empty."""
    values: dict[str, str] = {}
    for name, value in query.items():
        if name not in allowed:
            known = ", ".join(allowed[:-1]) + " or " + allowed[-1]
            raise ValueError(f"unknown {noun} {name!r}: use {known}")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{noun} {name!r} needs a value")
        values[name] = value.strip()
    return values


def _served_library() -> Library:
    root = configured_root()
    try:
        return cached_library(root)
    except LibraryError as exc:
        raise Unavailable(
            f"no library at {root}: check out the submodule "
            "(git submodule update --init library) or set TMODEL_LIBRARY to a library checkout"
        ) from exc


def _matching(library: Library, filters: Mapping[str, str]) -> list[LibraryRecord]:
    return [r for r in library if all(getattr(r, k) == v for k, v in filters.items())]


def library_records(filters: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The library's records, optionally filtered by id, type, topic and status (#140).

    A filter keeps the records whose field equals its value; several filters must
    all match, so `id` alone returns one record. The library is the one
    `configured_root()` names. Records that fail to load are left out and listed
    under `library.problems`, so a screen can still open. Raises ValueError for an
    unknown or empty filter, and Unavailable when there is no library to read.
    """
    wanted = _values(filters or {}, LIBRARY_FILTERS, "filter")
    library = _served_library()
    records = _matching(library, wanted)
    return {
        "library": {
            "root": library.root,
            "digest": library.digest,
            "count": len(library),
            "problems": list(library.problems),
        },
        "filters": wanted,
        "count": len(records),
        "records": [r.to_dict() for r in records],
    }


def library_table(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Rows for the library table views (#141, #58): filtered, searched, sorted, paged.

    Parameters, all optional: the `library_records` filters; `search`, a text that
    must appear (ignoring case) in a record's id, title, short title, publisher,
    topic or tags; `sort`, one of TABLE_SORTS (default `id`); `order`, `asc` or
    `desc`; and `limit` and `offset` for paging. Records without a value for the
    sort field come last in both orders, and ties keep id order. `total` counts
    the matches before paging. `facets` counts each type, status and topic in the
    whole library, for filter menus. The payload names no local path, so a saved
    copy is the same on every machine.
    """
    values = _values(query or {}, LIBRARY_FILTERS + TABLE_OPTIONS, "parameter")
    sort = values.get("sort", "id")
    if sort not in TABLE_SORTS:
        raise ValueError(f"cannot sort by {sort!r}: use one of {', '.join(TABLE_SORTS)}")
    order = values.get("order", "asc")
    if order not in ("asc", "desc"):
        raise ValueError(f"order must be asc or desc, not {order!r}")
    limit = _whole_number(values, "limit", minimum=1)
    offset = _whole_number(values, "offset", minimum=0) or 0
    search = values.get("search")

    library = _served_library()
    filters = {k: v for k, v in values.items() if k in LIBRARY_FILTERS}
    matched = _matching(library, filters)
    if search is not None:
        needle = search.casefold()
        matched = [r for r in matched if needle in _searchable(r)]
    matched = _sorted(matched, sort, descending=order == "desc")
    page = matched[offset : offset + limit if limit is not None else None]
    return {
        "library": {
            "digest": library.digest,
            "count": len(library),
            "problems": list(library.problems),
        },
        "query": {
            "filters": filters,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
        "total": len(matched),
        "count": len(page),
        "rows": [_row(r) for r in page],
        "facets": {name: _counts(library, name) for name in TABLE_FACETS},
    }


def _counts(library: Library, field: str) -> dict[str, int]:
    """How many records have each value of `field`, in value order; blanks are not counted."""
    return dict(sorted(Counter(getattr(r, field) for r in library if getattr(r, field)).items()))


def _whole_number(values: Mapping[str, str], name: str, minimum: int) -> int | None:
    if name not in values:
        return None
    text = values[name]
    if not (text.isascii() and text.isdigit()) or int(text) < minimum:
        raise ValueError(f"{name} must be a whole number of at least {minimum}, not {text!r}")
    return int(text)


def _searchable(r: LibraryRecord) -> str:
    fields = [r.id, r.title, r.short_title, r.publisher, r.topic, *r.tags]
    return " ".join(f for f in fields if f).casefold()


def _sort_value(r: LibraryRecord, field: str) -> str | None:
    value = r.body if field == "shelf" else getattr(r, field)
    return value.casefold() if value else None


def _sorted(records: list[LibraryRecord], field: str, descending: bool) -> list[LibraryRecord]:
    by_id = sorted(records, key=lambda r: r.id)
    present = [r for r in by_id if _sort_value(r, field) is not None]
    missing = [r for r in by_id if _sort_value(r, field) is None]
    present.sort(key=lambda r: _sort_value(r, field), reverse=descending)  # stable: ties by id
    return present + missing


def _row(r: LibraryRecord) -> dict[str, Any]:
    """One table row: what a list of documents shows, plus the key to fetch the rest."""
    return {
        "id": r.id,
        "title": r.title,
        "short_title": r.short_title,
        "type": r.type,
        "shelf": r.body,
        "status": r.status,
        "maturity": r.maturity,
        "date": r.date,
        "publisher": r.publisher,
        "topic": r.topic,
        "tags": list(r.tags),
        "url": r.content.url,
        "artifacts": len(r.artifacts),
        "reviewed_artifacts": sum(1 for a in r.artifacts if a.reviewed),
        "profile": r.profile,
    }


def attack_paths(file: str, goal: str | None = None) -> dict[str, Any]:
    """Attack paths to `goal` (a step or threat id) in a model file (#63).

    Without a goal, lists the file's threats, each with whether it is reviewed,
    so a caller can pick one. Raises GraphError (a ValueError) for a bad file or
    goal. `file` must be absolute: the API serves callers in any directory.
    """
    path = Path(file)
    if not path.is_absolute():
        raise GraphError(f"{file}: give an absolute path")
    graph = load_vector(path)
    if goal is None:
        return {
            "file": str(path),
            "threats": graph.threats(),
            "reviewed_threats": [t for t in graph.threats() if graph.threat_reviewed(t)],
            "steps": len(graph.steps),
        }
    return {
        "file": str(path),
        "goal": goal,
        "paths": [p.to_dict() for p in enumerate_paths(graph, goal)],
    }


def model_graph(file: str) -> dict[str, Any]:
    """Return a read-only graph projection of an approved example model.

    Relative paths are resolved below ``spec/vectors``. Absolute paths are
    accepted only when their resolved target is in that same directory.
    """
    path = _approved_vector_path(file)
    try:
        doc = load_vector_document(path)
        # Retain the graph integrity checks already used by PR #132.
        AttackGraph.from_dict(doc)
        graph = project_model_graph(doc)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    if not graph.nodes:
        raise GraphError(f"{path.name}: expected at least one model object")
    return {"file": str(path), **graph.to_dict()}


def _approved_vector_path(file: str) -> Path:
    if not file or not file.strip():
        raise GraphError("file: expected a model filename")
    root = APPROVED_VECTOR_DIRECTORY.resolve()
    supplied = Path(file)
    candidate = supplied if supplied.is_absolute() else root / supplied
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise GraphError("file: outside approved model directory")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise GraphError(f"{supplied.name or 'file'}: cannot read") from exc
    if not resolved.is_relative_to(root):
        raise GraphError("file: outside approved model directory")
    if not resolved.is_file():
        raise GraphError(f"{resolved.name}: expected a model file")
    return resolved


def _sanitized_model_error(path: Path, error: GraphError) -> str:
    """Keep model errors useful without returning the engine's local filesystem path."""
    message = str(error).replace(str(path), path.name)
    return message if message.startswith(f"{path.name}:") else f"{path.name}: {message}"
