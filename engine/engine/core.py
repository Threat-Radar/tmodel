"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from engine import __version__
from engine.load.vector import load_vector
from engine.paths import enumerate_paths

ENGINE_NAME = "tmodel-engine"


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

    Without a goal, lists the file's threats so a caller can pick one. Raises
    GraphError (a ValueError) for a bad file or goal.
    """
    path = Path(file)
    graph = load_vector(path)
    if goal is None:
        return {"file": str(path), "threats": graph.threats(), "steps": len(graph.steps)}
    return {
        "file": str(path),
        "goal": goal,
        "paths": [p.to_dict() for p in enumerate_paths(graph, goal)],
    }
