"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from engine import __version__
from engine.graph import AttackGraph, GraphError
from engine.load.vector import load_vector, load_vector_document
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths

ENGINE_NAME = "tmodel-engine"
APPROVED_VECTOR_DIRECTORY = Path(__file__).resolve().parents[2] / "spec" / "vectors"


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
