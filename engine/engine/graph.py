"""In-memory attack graph: AttackSteps, their AND/OR gates and `precedes` order.

Substrate-neutral on purpose (ADR-0004, ADR-0008): built from plain dicts shaped
like the object model (ADR-0010 core: AttackStep `gate`/`precedes`/`kill_chain_phase`,
AttackPath `steps`/`realizes_threat`), so a vector file today and the store façade
later can both feed it. Path enumeration (#63) runs over this, not over a store.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

GATES = ("and_gate", "or_gate")  # AttackGate enum in the core schema


class GraphError(ValueError):
    """The input does not form a valid attack graph (unknown id, bad gate, ...)."""


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


@dataclass
class AttackGraph:
    steps: dict[str, AttackStep] = field(default_factory=dict)
    paths: dict[str, AttackPath] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, doc: Mapping[str, Any]) -> AttackGraph:
        """Build from a model document with `attack_steps` and `attack_paths` lists."""
        graph = cls()
        for raw in doc.get("attack_steps") or []:
            step = AttackStep(
                id=raw["id"],
                name=raw.get("name", ""),
                gate=raw.get("gate"),
                precedes=tuple(raw.get("precedes") or ()),
                kill_chain_phase=raw.get("kill_chain_phase"),
            )
            if step.id in graph.steps:
                raise GraphError(f"duplicate attack step id: {step.id}")
            graph.steps[step.id] = step
        for raw in doc.get("attack_paths") or []:
            path = AttackPath(
                id=raw["id"],
                steps=tuple(raw.get("steps") or ()),
                realizes_threat=raw.get("realizes_threat"),
                name=raw.get("name", ""),
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
                raise GraphError(f"{step.id}: unknown gate {step.gate!r} (expected {GATES})")
            for nxt in step.precedes:
                if nxt not in self.steps:
                    raise GraphError(f"{step.id}: precedes unknown step {nxt}")
        for path in self.paths.values():
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

    def summary(self) -> dict[str, Any]:
        return {
            "steps": len(self.steps),
            "paths": len(self.paths),
            "threats": self.threats(),
        }
