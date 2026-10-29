"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine import __version__
from engine.graph import GraphError
from engine.load.library import LibraryError, cached_library, configured_root
from engine.load.vector import load_vector
from engine.paths import enumerate_paths

ENGINE_NAME = "tmodel-engine"
LIBRARY_FILTERS = ("type", "topic", "status")


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


def library_records(filters: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The library's records, optionally filtered by type, topic and status (#140).

    A filter keeps the records whose field equals its value; several filters must
    all match. The library is the one `configured_root()` names. Records that fail
    to load are left out and listed under `library.problems`, so a screen can still
    open. Raises ValueError for an unknown or empty filter, and Unavailable when
    there is no library to read.
    """
    wanted: dict[str, str] = {}
    for name, value in (filters or {}).items():
        if name not in LIBRARY_FILTERS:
            raise ValueError(f"unknown filter {name!r}: use type, topic or status")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"filter {name!r} needs a value")
        wanted[name] = value.strip()
    root = configured_root()
    try:
        library = cached_library(root)
    except LibraryError as exc:
        raise Unavailable(
            f"no library at {root}: check out the submodule "
            "(git submodule update --init library) or set TMODEL_LIBRARY to a library checkout"
        ) from exc
    records = [r for r in library if all(getattr(r, k) == v for k, v in wanted.items())]
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
