"""Bind computed routes to separately rated AttackPath records (#63).

The step graph stays global: narrowing enumeration to an authored path would
lose shared prerequisites. Instead, match a rating to the complete computed
step set. A legacy record with partial steps can supply a rating only when it
enumerates exactly one route. Broad OR records never donate their rating to
an arbitrary alternative.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from engine.graph import AttackGraph, AttackPath
from engine.paths import ComputedPath, enumerate_paths


def rated_routes(
    graph: AttackGraph, threat: str, ratings: Mapping[str, str | None]
) -> list[dict[str, Any]]:
    """One result per actual route, with explicit rating sources or missing data."""
    paths = graph.paths_for_threat(threat)
    alternatives = {
        path.id: enumerate_paths(AttackGraph(steps=graph.steps, paths={path.id: path}), threat)
        for path in paths
    }
    results = []
    for route in enumerate_paths(graph, threat):
        steps = frozenset(route.steps)
        # Keep every unambiguous owner, including partial legacy records.
        # Exact records must neither hide a conflicting legacy rating nor
        # borrow one when their own rating is missing. Broad OR records still
        # cannot donate a rating to an arbitrary alternative.
        owners = [
            path
            for path in paths
            if frozenset(path.steps) == steps
            or (
                len(alternatives[path.id]) == 1
                and frozenset(alternatives[path.id][0].steps) == steps
            )
        ]
        feasibility, problems = _rating(owners, ratings)
        results.append(
            {
                "id": _route_id(graph, threat, route),
                "steps": list(route.steps),
                "goal_step": route.goal_step,
                "authored_path": route.authored_path,
                "rating_paths": [path.id for path in owners],
                "feasibility": feasibility,
                "problems": problems,
            }
        )
    return results


def _rating(
    owners: list[AttackPath], ratings: Mapping[str, str | None]
) -> tuple[str | None, list[str]]:
    if not owners:
        return None, ["route_rating_required"]
    values = {ratings[path.id] for path in owners}
    if len(values) > 1:
        return None, ["conflicting_route_ratings"]
    value = next(iter(values))
    return (value, []) if value is not None else (None, ["feasibility_missing"])


def _route_id(graph: AttackGraph, threat: str, route: ComputedPath) -> str:
    """Content identity for output, independent of list order and authored aliases.

    Ratings still live on authored AttackPath records. The digest identifies
    the route shown in API/CLI output; it is not a human approval or a new KG node.
    """
    steps = set(route.steps)
    structure = {
        "threat": threat,
        "goal_step": route.goal_step,
        "steps": [
            [
                sid,
                graph.steps[sid].gate,
                sorted(nxt for nxt in graph.steps[sid].precedes if nxt in steps),
            ]
            for sid in sorted(steps)
        ],
    }
    canonical = json.dumps(structure, sort_keys=True, separators=(",", ":"))
    return "route:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
