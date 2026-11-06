"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
import sys
from collections import Counter
from collections.abc import Iterable, Mapping
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
from engine.load.vector import MODEL_SUFFIXES, load_vector, load_vector_document
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths

ENGINE_NAME = "tmodel-engine"
# PyInstaller unpacks the one-file sidecar and its data below _MEIPASS. In a
# source checkout, the examples live at the repository root instead. Neither
# location depends on the app's working directory or a developer's checkout.
APPROVED_VECTOR_DIRECTORY = (
    (Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2])
    / "spec"
    / "vectors"
)
LIBRARY_FILTERS = ("id", "type", "topic", "status")
# The library table view (#141, #58): what it can sort by, and what it counts for filter menus.
TABLE_OPTIONS = ("search", "sort", "order", "limit", "offset")
TABLE_SORTS = ("id", "title", "type", "shelf", "status", "maturity", "date", "publisher", "topic")
TABLE_FACETS = ("type", "status", "topic")
# The example-model families, told apart by file-name prefix (spec/vectors/README.md).
# The order is the order the model list uses.
MODEL_KINDS = (
    ("mvp-", "core", "Core example"),
    ("tv-", "worked", "Worked example with governance"),
    ("pv-", "proposal", "Proposal example (AI-drafted, unreviewed)"),
)
# Schema test harnesses live beside the models but are not models.
HARNESS_SUFFIX = ".linkml.yaml"
# What a model summary counts: summary name -> model collection.
MODEL_COUNTS = (
    ("assets", "assets"),
    ("components", "components"),
    ("damage_scenarios", "damage_scenarios"),
    ("threats", "threat_instances"),
    ("attack_paths", "attack_paths"),
    ("mitigations", "mitigations"),
    ("risk_scores", "risk_scores"),
    ("requirements", "requirements"),
)


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


def _matching(records: Iterable[LibraryRecord], filters: Mapping[str, str]) -> list[LibraryRecord]:
    return [r for r in records if all(getattr(r, k) == v for k, v in filters.items())]


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
    the matches before paging. `facets` contains whole-library counts for type,
    status, and topic. `contextual_facets` applies the current search and the
    other exact filters, excluding each facet's own filter so a user can switch
    its selection. The payload names no local path, so a saved copy is the same
    on every machine.
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
    searched = _searched(library, search)
    matched = _matching(searched, filters)
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
        "contextual_facets": {
            name: _counts(
                _matching(searched, {key: value for key, value in filters.items() if key != name}),
                name,
            )
            for name in TABLE_FACETS
        },
    }


def _counts(records: Iterable[LibraryRecord], field: str) -> dict[str, int]:
    """How many records have each value of `field`, in value order; blanks are not counted."""
    return dict(sorted(Counter(getattr(r, field) for r in records if getattr(r, field)).items()))


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


def _searched(records: Iterable[LibraryRecord], search: str | None) -> list[LibraryRecord]:
    """Records matching the table's text search, or every record when search is absent."""
    if search is None:
        return list(records)
    needle = search.casefold()
    return [record for record in records if needle in _searchable(record)]


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

    Relative paths are resolved below the bundled examples (or ``spec/vectors``
    in a source checkout). Absolute paths must resolve inside that directory.
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


def list_models() -> dict[str, Any]:
    """The example models a reader can open (#208), one summary each.

    Lists the approved model directory: the bundled examples, or ``spec/vectors``
    in a source checkout. Schema test harnesses (``*.linkml.yaml``) are not models
    and are left out. A file that fails to load is listed under ``problems`` so the
    rest can still be opened. Each summary's ``file`` is what ``/graph`` accepts.
    The title and description come from the model itself (its products), else the
    file name; nothing is made up. The payload names no local path.
    """
    root = APPROVED_VECTOR_DIRECTORY.resolve()
    models: list[dict[str, Any]] = []
    problems: list[dict[str, str]] = []
    candidates = sorted(root.iterdir()) if root.is_dir() else []
    for path in candidates:
        if (
            path.suffix not in MODEL_SUFFIXES
            or path.name.endswith(HARNESS_SUFFIX)
            or not path.is_file()
        ):
            continue
        try:
            summary = _model_summary(path)
        except GraphError as exc:
            problems.append({"file": path.name, "error": _sanitized_model_error(path, exc)})
            continue
        if summary is not None:
            models.append(summary)
    rank = {kind: index for index, (_prefix, kind, _label) in enumerate(MODEL_KINDS)}
    models.sort(key=lambda model: (rank.get(model["kind"], len(rank)), model["file"]))
    return {"count": len(models), "models": models, "problems": problems}


def _model_summary(path: Path) -> dict[str, Any] | None:
    """One model's list entry, or None for a file with no model objects."""
    doc = load_vector_document(path)
    attack_graph = AttackGraph.from_dict(doc)  # the same integrity checks as /graph
    if not project_model_graph(doc).nodes:
        return None
    products = [p for p in doc.get("products") or [] if isinstance(p, Mapping)]
    names = [p["name"].strip() for p in products if _has_text(p.get("name"))]
    kind, kind_label = next(
        ((kind, label) for prefix, kind, label in MODEL_KINDS if path.name.startswith(prefix)),
        ("other", "Example model"),
    )
    threats = attack_graph.threats()
    return {
        "id": path.stem,
        "file": path.name,
        "title": " and ".join(names) if names else path.stem,
        "description": _products_description(products),
        "kind": kind,
        "kind_label": kind_label,
        "counts": {
            name: len(entries) if isinstance(entries := doc.get(collection), list) else 0
            for name, collection in MODEL_COUNTS
        },
        "reviewed_threats": sum(1 for t in threats if attack_graph.threat_reviewed(t)),
    }


def _products_description(products: list[Mapping[str, Any]]) -> str | None:
    """The products' own descriptions, in model order, nothing added.

    One product: its description. Several (mvp-18 has two): one line per product
    that has a description, "Name: description", so the scope covers every
    product the title names. Whitespace inside a description is collapsed, so a
    newline only ever separates two products; the app reads each line apart.
    """
    described = [
        (p.get("name"), " ".join(p["description"].split()))
        for p in products
        if _has_text(p.get("description"))
    ]
    if not described:
        return None
    if len(products) == 1:
        return described[0][1]
    return "\n".join(
        f"{name.strip()}: {text}" if _has_text(name) else text for name, text in described
    )


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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
