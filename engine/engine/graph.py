"""In-memory attack graph: AttackSteps, their AND/OR gates and `precedes` order.

Substrate-neutral on purpose (ADR-0004, ADR-0008): built from plain dicts shaped
like the object model (ADR-0010 core: AttackStep `gate`/`precedes`/`kill_chain_phase`,
AttackPath `steps`/`realizes_threat`), so a vector file today and the store façade
later can both feed it. Path enumeration (#63) runs over this, not over a store.

Every malformed input becomes a GraphError (a ValueError), so callers can report
it instead of crashing.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any

GATES = ("and_gate", "or_gate")  # AttackGate enum in the core schema


class GraphError(ValueError):
    """The input does not form a valid attack graph (unknown id, bad gate, ...)."""


@dataclass(frozen=True)
class ReviewState:
    """What the model records about an authored path's review (R-018).

    Real model inputs resolve justified person reviews for the exact
    path/realizes_threat/threat statement, considering every human verdict.
    Negative or unknown verdicts cannot establish acceptance. The two status
    strings summarize those records; `human_reviewed` carries the evidence
    result. Status-only construction remains a legacy presentation helper for
    shared transport fixtures, not a way to accept model relationships.
    """

    assertion_status: str | None = None
    review_status: str | None = None
    # Real model inputs resolve human evidence; None retains the status-only
    # presentation helper used by legacy transport fixtures.
    human_reviewed: bool | None = None

    @property
    def reviewed(self) -> bool:
        if self.human_reviewed is not None:
            return self.human_reviewed
        assertion = _status(self.assertion_status)
        review = _status(self.review_status)
        return assertion == "accepted" and review in (None, "accepted")

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


def _status(value: str | None) -> str | None:
    """A status as the app compares it: trimmed, lower case, spaces and hyphens as `_`."""
    if value is None:
        return None
    normalized = re.sub(r"[\s-]+", "_", value.strip().lower())
    return normalized or None


def _text(raw: Mapping[str, Any], field_name: str) -> str | None:
    """An optional string field; anything else is rejected before it is formatted."""
    value = raw.get(field_name)
    if value is not None and not isinstance(value, str):
        raise GraphError(f"{raw['id']}: {field_name} must be a string")
    return value


def _reviews(doc: Mapping[str, Any]) -> dict[tuple[str, str], ReviewState]:
    """Human evidence scoped to the exact path/threat statement, independent of order."""
    from engine.review import relationship_review_states

    for review in _entries(doc, "reviews"):
        _text(review, "review_status")
    for assertion in _entries(doc, "assertions"):
        _text(assertion, "assertion_status")
    _entries(doc, "parties")
    return {
        (subject, target): ReviewState(
            state["assertion_status"], state["review_status"], state["reviewed"]
        )
        for (subject, predicate, target), state in relationship_review_states(doc).items()
        if predicate == "realizes_threat"
    }


@dataclass
class AttackGraph:
    steps: dict[str, AttackStep] = field(default_factory=dict)
    paths: dict[str, AttackPath] = field(default_factory=dict)
    asset_threats: dict[str, tuple[str, ...]] = field(default_factory=dict)
    path_reviews: dict[tuple[str, str], ReviewState] = field(default_factory=dict)
    accepted_path_links: frozenset[tuple[str, str]] = frozenset()

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
        graph.path_reviews = reviews
        for raw in _entries(doc, "attack_paths"):
            path = AttackPath(
                id=raw["id"],
                steps=_ids(raw, "steps"),
                realizes_threat=_text(raw, "realizes_threat"),
                name=_text(raw, "name") or "",
                review=reviews.get((raw["id"], raw.get("realizes_threat")), ReviewState()),
            )
            if path.id in graph.paths:
                raise GraphError(f"duplicate attack path id: {path.id}")
            graph.paths[path.id] = path
        threats = {threat["id"] for threat in _entries(doc, "threat_instances")}
        graph.accepted_path_links = frozenset(
            key
            for key, state in reviews.items()
            if state.reviewed and key[0] in graph.paths and key[1] in threats
        )
        graph.validate()
        if doc.get("assets"):
            from engine.asset_goals import asset_threats

            graph.asset_threats = asset_threats(doc)
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
        return [
            replace(
                path,
                realizes_threat=threat_id,
                review=self.path_reviews.get(
                    (path.id, threat_id),
                    path.review if path.realizes_threat == threat_id else ReviewState(),
                ),
            )
            for path in self.paths.values()
            if path.realizes_threat == threat_id or (path.id, threat_id) in self.accepted_path_links
        ]

    def threats(self) -> list[str]:
        return sorted(
            {p.realizes_threat for p in self.paths.values() if p.realizes_threat}
            | {threat for _, threat in self.accepted_path_links}
        )

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
