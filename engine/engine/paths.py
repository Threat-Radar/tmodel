"""Attack-path enumeration over an AttackGraph (#63 Part 1; ARCH-0001-PROPOSAL §2a, R-031).

A step's `gate` says how it combines the steps that `precede` it:

- no predecessors: a starting step; reaching it takes only itself;
- one predecessor and no gate: a sequence;
- `or_gate`: any one predecessor suffices, so each alternative is its own path;
- `and_gate`: every predecessor is needed, so their paths are combined.

A path is the set of steps that together reach the goal, listed in `precedes`
order (ties in declaration order). Supersets of another path are dropped, so a
step shared by two branches is not counted twice. Several predecessors without a
gate is ambiguous and rejected, as is a cycle.

A goal is a step id or a threat id. For a threat, the goal steps are the final
steps (no successor inside the path) of each authored AttackPath that realizes
it; enumeration then runs over the whole graph, so shared steps count.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import prod
from typing import Any

from engine.graph import AttackGraph, GraphError

DEFAULT_LIMIT = 1000  # guard against combinatorial blow-up on large AND/OR graphs


@dataclass(frozen=True)
class ComputedPath:
    steps: tuple[str, ...]  # in `precedes` order
    goal_step: str
    authored_path: str | None = None  # the vector's AttackPath it came from, if any

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"steps": list(self.steps), "goal_step": self.goal_step}
        if self.authored_path:
            out["authored_path"] = self.authored_path
        return out


def enumerate_paths(
    graph: AttackGraph, goal: str, limit: int = DEFAULT_LIMIT
) -> list[ComputedPath]:
    """All minimal attack paths reaching `goal` (a step id or a threat id)."""
    if goal in graph.steps:
        targets = [(goal, None)]
    else:
        authored = graph.paths_for_threat(goal)
        if not authored:
            raise GraphError(f"unknown goal: {goal} (not a step, and no path realizes it)")
        targets = [(sink, p.id) for p in authored for sink in _final_steps(graph, p.steps)]

    order = {sid: i for i, sid in enumerate(graph.steps)}
    memo: dict[str, list[frozenset[str]]] = {}
    result: list[ComputedPath] = []
    seen: set[frozenset[str]] = set()
    for sink, authored_id in targets:
        for step_set in _reach(graph, sink, memo, (), limit):
            if step_set in seen:
                continue
            seen.add(step_set)
            result.append(ComputedPath(_ordered(graph, step_set, order), sink, authored_id))
    return result


def _reach(
    graph: AttackGraph,
    step_id: str,
    memo: dict[str, list[frozenset[str]]],
    stack: tuple[str, ...],
    limit: int,
) -> list[frozenset[str]]:
    """Minimal step sets that reach `step_id`."""
    if step_id in stack:
        cycle = " -> ".join((*stack[stack.index(step_id) :], step_id))
        raise GraphError(f"cycle in precedes: {cycle}")
    if step_id in memo:
        return memo[step_id]

    stack = (*stack, step_id)
    preds = graph.predecessors(step_id)
    gate = graph.steps[step_id].gate
    if not preds:
        options = [frozenset()]
    elif len(preds) == 1:
        options = _reach(graph, preds[0], memo, stack, limit)
    elif gate == "or_gate":
        options = [s for p in preds for s in _reach(graph, p, memo, stack, limit)]
    elif gate == "and_gate":
        branches = [_reach(graph, p, memo, stack, limit) for p in preds]
        if prod(len(b) for b in branches) > limit:
            raise GraphError(f"{step_id}: more than {limit} attack paths; narrow the goal")
        options = [frozenset().union(*combo) for combo in product(*branches)]
    else:
        raise GraphError(
            f"{step_id}: {len(preds)} predecessors but no gate; set and_gate or or_gate"
        )

    sets = _minimal([s | {step_id} for s in options])
    if len(sets) > limit:
        raise GraphError(f"{step_id}: more than {limit} attack paths; narrow the goal")
    memo[step_id] = sets
    return sets


def _minimal(sets: list[frozenset[str]]) -> list[frozenset[str]]:
    """Drop duplicates and any set that contains another one; keep first-seen order."""
    unique = list(dict.fromkeys(sets))
    return [s for s in unique if not any(o < s for o in unique)]


def _final_steps(graph: AttackGraph, steps: tuple[str, ...]) -> list[str]:
    inside = set(steps)
    return [s for s in steps if not inside & set(graph.steps[s].precedes)]


def _ordered(
    graph: AttackGraph, step_set: frozenset[str], order: dict[str, int]
) -> tuple[str, ...]:
    """Topological order under `precedes` within the set; ties by declaration order."""
    indegree = {s: 0 for s in step_set}
    for s in step_set:
        for nxt in graph.steps[s].precedes:
            if nxt in indegree:
                indegree[nxt] += 1
    ready = sorted((s for s, d in indegree.items() if d == 0), key=order.__getitem__)
    out: list[str] = []
    while ready:
        s = ready.pop(0)
        out.append(s)
        for nxt in graph.steps[s].precedes:
            if nxt in indegree:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    ready.append(nxt)
                    ready.sort(key=order.__getitem__)
    return tuple(out)
