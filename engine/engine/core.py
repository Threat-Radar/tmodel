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
from engine import propose as proposals
from engine import sdl as sdl_view
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
from engine.risk import assess_document

ENGINE_NAME = "tmodel-engine"
# PyInstaller unpacks the one-file sidecar and its data below _MEIPASS. In a
# source checkout, the examples live at the repository root instead. Neither
# location depends on the app's working directory or a developer's checkout.
APPROVED_VECTOR_DIRECTORY = (
    (Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2])
    / "spec"
    / "vectors"
)
# The MAP-0001 crosswalk the SDL view reads (bundled beside spec/vectors by bin/build-engine).
CROSSWALK_FILE = APPROVED_VECTOR_DIRECTORY.parent / "MAP-0001.yaml"
SDL_PREFIX = "sdl-"  # SDL models are spec/vectors/sdl-*.yaml (DL-0040)
SDL_OPTIONS = ("file", "program")
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


def risk_assessments(file: str, matrix: str, goal: str | None = None) -> dict[str, Any]:
    """Derived risk for approved example-model files; ratings remain authored inputs."""
    path = _approved_vector_path(file)
    try:
        result = assess_document(load_vector_document(path), matrix=matrix, goal=goal)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    return {"file": path.name, **result}


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


def sdl_models() -> dict[str, Any]:
    """The SDL models the app can open (spec/vectors/sdl-*.yaml), with their programs."""
    root = APPROVED_VECTOR_DIRECTORY
    models = []
    for path in sorted(root.glob(f"{SDL_PREFIX}*.yaml")):
        try:
            doc = load_vector_document(path)
        except GraphError as exc:
            models.append({"file": path.name, "error": _sanitized_model_error(path, exc)})
            continue
        models.append({"file": path.name, "programs": sdl_view.programs(dict(doc))})
    return {"models": models}


def sdl(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The SDL program view of one SDL model (DL-0043): what the "tmodel SDL" page shows.

    Without `file`, lists the SDL models (`sdl_models`). `file` is a name in the
    approved model directory and must be an `sdl-*.yaml` model; `program` picks a
    SecurityProgram when the file has more than one. Raises ValueError (400) for a bad
    file, an unknown program, a dangling reference or a broken PROC-0002 review rule.
    The payload is read-only and names no local path.
    """
    values = _values(query or {}, SDL_OPTIONS, "parameter")
    if "file" not in values:
        return sdl_models()
    path = _approved_vector_path(values["file"])
    if not path.name.startswith(SDL_PREFIX):
        raise GraphError(f"{path.name}: not an SDL model (expected {SDL_PREFIX}*.yaml)")
    try:
        doc = dict(load_vector_document(path))
        xwalk = load_vector_document(CROSSWALK_FILE)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    try:
        pending = proposals.load_proposals(path)
        view = sdl_view.collect(doc, dict(xwalk), program=values.get("program"))
        view["proposals"] = proposals.summary(pending, doc)
    except (KeyError, TypeError) as exc:
        raise GraphError(f"{path.name}: malformed SDL model ({type(exc).__name__}: {exc})") from exc
    except sdl_view.SdlError as exc:
        raise GraphError(f"{path.name}: {exc}") from exc
    return {"file": path.name, **view}


def _model_path(file: str) -> Path:
    """An example model in the approved directory: mvp-*, tv-*, pv-* or sdl-*.yaml."""
    path = _approved_vector_path(file)
    if not path.name.startswith(proposals.MODEL_PREFIXES) or path.suffix != ".yaml":
        raise GraphError(
            f"{path.name}: not a model file (expected "
            f"{', '.join(p + '*.yaml' for p in proposals.MODEL_PREFIXES)})"
        )
    return path


def _relative(path: Path) -> str:
    return str(path.relative_to(APPROVED_VECTOR_DIRECTORY.parent.parent))


def propose(patch: Mapping[str, Any], write: bool = True) -> dict[str, Any]:
    """Check an agent's patch and append it to the target's proposals file (DL-0044, DL-0046).

    Never edits the model, writes a Review or accepts anything. Raises ValueError
    (ProposalError) with every problem when the patch is refused; nothing is written.
    """
    target = patch.get("target") if isinstance(patch, Mapping) else None
    if not isinstance(target, str):
        raise proposals.ProposalError("target is required")
    try:
        path = _model_path(target)
    except GraphError as exc:
        raise proposals.ProposalError(str(exc)) from exc
    xwalk = load_vector_document(CROSSWALK_FILE)
    record = proposals.propose(patch, path, xwalk, write=write)
    return {
        "written": write,
        "file": _relative(proposals.proposals_path(path)) if write else None,
        "proposal": record,
    }


def pending_proposals(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """GET /proposals (DL-0046): pending proposals and saved KG views. Read-only.

    Without `file`, lists every example model with its number of pending proposals.
    With `file`, returns that model's pending proposals (as GET /sdl shows them) and
    its saved KG views, the model's own first, then the proposed ones, each with the
    object ids it selects. Nothing here accepts anything; there is no write route.
    """
    values = _values(query or {}, ("file",), "parameter")
    root = APPROVED_VECTOR_DIRECTORY
    if "file" not in values:
        models = []
        for path in sorted(root.glob("*.yaml")):
            if not path.name.startswith(proposals.MODEL_PREFIXES):
                continue
            try:
                count = len(proposals.load_proposals(path))
            except proposals.ProposalError as exc:
                models.append({"file": path.name, "error": str(exc)})
                continue
            models.append({"file": path.name, "kind": proposals.model_kind(path), "pending": count})
        return {"models": models}
    path = _model_path(values["file"])
    try:
        doc = dict(load_vector_document(path))
        pending = proposals.load_proposals(path)
        return {
            "file": path.name,
            "kind": proposals.model_kind(path),
            "proposals": proposals.summary(pending, doc),
            "views": proposals.views(doc, pending),
        }
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    except (KeyError, TypeError) as exc:
        raise GraphError(f"{path.name}: malformed proposals ({type(exc).__name__}: {exc})") from exc
