"""In-memory attack graph: AttackSteps, their AND/OR gates and `precedes` order.

Substrate-neutral on purpose (ADR-0004, ADR-0008): built from plain dicts shaped
like the object model (ADR-0010 core: AttackStep `gate`/`precedes`/`kill_chain_phase`,
AttackPath `steps`/`realizes_threat`), so a vector file today and the store façade
later can both feed it. Path enumeration (#63) runs over this, not over a store.

Every malformed input becomes a GraphError (a ValueError), so callers can report
it instead of crashing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

GATES = ("and_gate", "or_gate")  # AttackGate enum in the core schema


class GraphError(ValueError):
    """The input does not form a valid attack graph (unknown id, bad gate, ...)."""


@dataclass(frozen=True)
class ReviewState:
    """What the model records about an authored path's review (R-018).

    The values are the file's own `assertion_status` and `review_status` (both
    open strings in the schema). `reviewed` is true only for an accepted
    Assertion: the schema says an Assertion "must not be `accepted` until
    provenance and a review are present". Anything else, including no record at
    all, is not presented as reviewed (CLAUDE.md; APP-0001 A-007, A-045).
    """

    assertion_status: str | None = None
    review_status: str | None = None

    @property
    def reviewed(self) -> bool:
        return self.assertion_status == "accepted"

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviewed": self.reviewed,
            "assertion_status": self.assertion_status,
            "review_status": self.review_status,
        }


@dataclass(frozen=True)
class AttackStep:
    id: str
    name: str = ""
    gate: str | None = None  # how this step combines its predecessors
    precedes: tuple[str, ...] = ()
    kill_chain_phase: str | None = None  # coarse order tag, not the ATT&CK technique


@dataclass(frozen=True)
class AttackPath:
    """An AttackPath as authored (e.g. in a vector), not one the engine computed."""

    id: str
    steps: tuple[str, ...] = ()
    realizes_threat: str | None = None
    name: str = ""
    review: ReviewState = ReviewState()


def _entries(doc: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    """The `key` list of a model document; each entry a mapping with a string id."""
    entries = doc.get(key) or []
    if not isinstance(entries, list):
        raise GraphError(f"{key}: expected a list")
    for i, raw in enumerate(entries):
        if not isinstance(raw, Mapping) or not isinstance(raw.get("id"), str):
            raise GraphError(f"{key}[{i}]: expected a mapping with a string id (quote numeric ids)")
    return entries


def _ids(raw: Mapping[str, Any], field_name: str) -> tuple[str, ...]:
    value = raw.get(field_name) or []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise GraphError(f"{raw['id']}: {field_name} must be a list of ids")
    return tuple(value)


def _text(raw: Mapping[str, Any], field_name: str) -> str | None:
    """An optional string field; anything else is rejected before it is formatted."""
    value = raw.get(field_name)
    if value is not None and not isinstance(value, str):
        raise GraphError(f"{raw['id']}: {field_name} must be a string")
    return value


def _reviews(doc: Mapping[str, Any]) -> dict[str, ReviewState]:
    """Review state per authored path, from its `realizes_threat` Assertion and that
    Assertion's latest Review."""
    verdict: dict[str, str | None] = {}
    for review in _entries(doc, "reviews"):
        target = review.get("reviews")
        if isinstance(target, str):
            verdict[target] = _text(review, "review_status")
    states: dict[str, ReviewState] = {}
    for assertion in _entries(doc, "assertions"):
        subject = assertion.get("subject")
        if assertion.get("predicate") == "realizes_threat" and isinstance(subject, str):
            states[subject] = ReviewState(
                assertion_status=_text(assertion, "assertion_status"),
                review_status=verdict.get(assertion["id"]),
            )
    return states


@dataclass
class AttackGraph:
    steps: dict[str, AttackStep] = field(default_factory=dict)
    paths: dict[str, AttackPath] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, doc: Mapping[str, Any]) -> AttackGraph:
        """Build from a model document with `attack_steps` and `attack_paths` lists
        (and, optionally, the `assertions` and `reviews` that record path reviews)."""
        if not isinstance(doc, Mapping):
            raise GraphError("expected a mapping at the top level")
        graph = cls()
        for raw in _entries(doc, "attack_steps"):
            step = AttackStep(
                id=raw["id"],
                name=_text(raw, "name") or "",
                gate=_text(raw, "gate"),
                precedes=_ids(raw, "precedes"),
                kill_chain_phase=_text(raw, "kill_chain_phase"),
            )
            if step.id in graph.steps:
                raise GraphError(f"duplicate attack step id: {step.id}")
            graph.steps[step.id] = step
        reviews = _reviews(doc)
        for raw in _entries(doc, "attack_paths"):
            path = AttackPath(
                id=raw["id"],
                steps=_ids(raw, "steps"),
                realizes_threat=_text(raw, "realizes_threat"),
                name=_text(raw, "name") or "",
                review=reviews.get(raw["id"], ReviewState()),
            )
            if path.id in graph.paths:
                raise GraphError(f"duplicate attack path id: {path.id}")
            graph.paths[path.id] = path
        graph.validate()
        return graph

    def validate(self) -> None:
        """Every gate is a known AttackGate and every reference resolves."""
        for step in self.steps.values():
            if step.gate is not None and step.gate not in GATES:
                raise GraphError(f"{step.id}: unknown gate {step.gate[:40]!r} (expected {GATES})")
            for nxt in step.precedes:
                if nxt not in self.steps:
                    raise GraphError(f"{step.id}: precedes unknown step {nxt}")
        for path in self.paths.values():
            if not path.steps:
                raise GraphError(f"{path.id}: lists no steps")
            for sid in path.steps:
                if sid not in self.steps:
                    raise GraphError(f"{path.id}: lists unknown step {sid}")

    def predecessors(self, step_id: str) -> list[str]:
        """Steps that `precede` the given step, in declaration order."""
        return [s.id for s in self.steps.values() if step_id in s.precedes]

    def paths_for_threat(self, threat_id: str) -> list[AttackPath]:
        return [p for p in self.paths.values() if p.realizes_threat == threat_id]

    def threats(self) -> list[str]:
        return sorted({p.realizes_threat for p in self.paths.values() if p.realizes_threat})

    def threat_reviewed(self, threat_id: str) -> bool:
        """A threat counts as reviewed only if every authored path for it is."""
        paths = self.paths_for_threat(threat_id)
        return bool(paths) and all(p.review.reviewed for p in paths)

    def summary(self) -> dict[str, Any]:
        return {
            "steps": len(self.steps),
            "paths": len(self.paths),
            "threats": self.threats(),
        }
