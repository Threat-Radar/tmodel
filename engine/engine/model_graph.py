"""Storage-neutral projection of a LinkML-shaped model document into graph DTOs.

The current source adapter is the example-vector loader.  The API consumes this
projection rather than YAML details so a future storage façade (#65) can provide
the same nodes and directed relationships without changing the desktop client.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from engine.graph import GraphError

# Collection names come from the sponsor-approved ExampleModel containers.  This
# is an adapter map only; it does not add to or alter the canonical schema.
COLLECTION_DOMAIN_TYPES = {
    "parties": "Party",
    "products": "Product",
    "product_instances": "ProductInstance",
    "components": "Component",
    "weaknesses": "Weakness",
    "vulnerabilities": "Vulnerability",
    "attack_patterns": "AttackPattern",
    "threat_instances": "ThreatInstance",
    "attack_steps": "AttackStep",
    "attack_paths": "AttackPath",
    "damage_scenarios": "DamageScenario",
    "mitigations": "Mitigation",
    "risk_scores": "RiskScore",
    "reviews": "Review",
    "assertions": "Assertion",
    "deployments": "Deployment",
    "environments": "Environment",
    "lifecycle_phases": "LifecyclePhase",
    "redundancy_groups": "RedundancyGroup",
    "views": "View",
    "threat_models": "ThreatModel",
    "security_programs": "SecurityProgram",
    "gates": "Gate",
    "milestones": "Milestone",
    "checkpoints": "Checkpoint",
    "requirements": "Requirement",
    "governed_views": "GovernedView",
}

# Sponsor-approved slots whose ranges are model classes. ``impact`` is omitted:
# it is an inlined value object, not an identity-bearing graph node.
RELATIONSHIP_SLOTS = frozenset(
    {
        "composed_of",
        "depends_on",
        "uses_component",
        "manufactured_by",
        "supplied_by",
        "owned_by",
        "of_product",
        "current_phase",
        "affects",
        "reported_by",
        "assigned_by",
        "realizes_damage",
        "applies_in_phase",
        "precedes",
        "steps",
        "realizes_threat",
        "pivots_to",
        "mitigates",
        "implementation_owner",
        "threat",
        "attack_paths",
        "damage_scenario",
        "for_stakeholder",
        "reviews",
        "reviewer",
        "subject",
        "object",
        "product_instance",
        "environment",
        "replicas",
        "members",
        "owner",
        "approved_by",
        "supersedes",
        "governs",
        "program_nodes",
        "incorporates",
        "at_phase",
        "gated_by",
        "decided_by",
        "depends_on_node",
        "validates_conformance_of",
        "offset_from",
        "renders",
        "maps_to",
        "satisfied_by",
    }
)


@dataclass(frozen=True)
class ModelNode:
    id: str
    domain_type: str
    label: str
    properties: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "domain_type": self.domain_type,
            "label": self.label,
            "properties": dict(self.properties),
        }


@dataclass(frozen=True)
class ModelEdge:
    id: str
    source: str
    target: str
    relationship_type: str
    properties: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "properties": dict(self.properties),
        }


@dataclass(frozen=True)
class ModelGraph:
    nodes: tuple[ModelNode, ...]
    edges: tuple[ModelEdge, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


def project_model_graph(doc: Mapping[str, Any]) -> ModelGraph:
    """Project schema-backed objects and id-reference slots into a graph."""
    records: list[tuple[str, Mapping[str, Any]]] = []
    ids: set[str] = set()
    for collection, domain_type in COLLECTION_DOMAIN_TYPES.items():
        entries = doc.get(collection) or []
        if not isinstance(entries, list):
            raise GraphError(f"{collection}: expected a list")
        for index, raw in enumerate(entries):
            if not isinstance(raw, Mapping) or not isinstance(raw.get("id"), str):
                raise GraphError(
                    f"{collection}[{index}]: expected a mapping with a string id "
                    "(quote numeric ids)"
                )
            object_id = raw["id"]
            if object_id in ids:
                raise GraphError(f"duplicate model object id: {object_id}")
            ids.add(object_id)
            records.append((domain_type, raw))

    nodes = tuple(_node(domain_type, raw) for domain_type, raw in records)
    edges: dict[tuple[str, str, str], ModelEdge] = {}
    for _domain_type, raw in records:
        source = raw["id"]
        for slot in RELATIONSHIP_SLOTS:
            if slot not in raw:
                continue
            for target in _references(source, slot, raw[slot]):
                if target not in ids:
                    raise GraphError(f"{source}: {slot} references unknown object {target}")
                _add_edge(edges, source, target, slot, {})

    reviews = _reviews_by_assertion(doc)
    for assertion in _collection(doc, "assertions"):
        subject = assertion.get("subject")
        predicate = assertion.get("predicate")
        object_id = assertion.get("object")
        if not all(isinstance(value, str) for value in (subject, predicate, object_id)):
            raise GraphError(
                f"{assertion['id']}: assertion subject, predicate, and object must be strings"
            )
        review = reviews.get(assertion["id"])
        properties: dict[str, Any] = {
            "assertion_ids": [assertion["id"]],
            "assertion_status": _json_value(assertion.get("assertion_status")),
            "confidence": _json_value(assertion.get("confidence")),
        }
        if review is not None:
            properties.update(
                {
                    "review_ids": [review["id"]],
                    "review_status": _json_value(review.get("review_status")),
                }
            )
        _add_edge(edges, subject, object_id, predicate, properties)

    return ModelGraph(nodes=nodes, edges=tuple(edges.values()))


def _node(domain_type: str, raw: Mapping[str, Any]) -> ModelNode:
    properties = {
        key: _json_value(value)
        for key, value in raw.items()
        if key not in {"id", "name"} and key not in RELATIONSHIP_SLOTS
    }
    return ModelNode(
        id=raw["id"],
        domain_type=domain_type,
        label=raw.get("name") if isinstance(raw.get("name"), str) else raw["id"],
        properties=properties,
    )


def _references(source: str, slot: str, value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise GraphError(f"{source}: {slot} must be an id or list of ids")


def _add_edge(
    edges: dict[tuple[str, str, str], ModelEdge],
    source: str,
    target: str,
    relationship_type: str,
    properties: Mapping[str, Any],
) -> None:
    key = (source, relationship_type, target)
    previous = edges.get(key)
    merged = dict(previous.properties) if previous else {}
    for name, value in properties.items():
        if name in {"assertion_ids", "review_ids"} and isinstance(value, list):
            merged[name] = list(dict.fromkeys([*(merged.get(name) or []), *value]))
        elif value is not None:
            merged[name] = value
    edges[key] = ModelEdge(
        id=_edge_id(source, relationship_type, target),
        source=source,
        target=target,
        relationship_type=relationship_type,
        properties=merged,
    )


def _edge_id(source: str, relationship_type: str, target: str) -> str:
    return f"relationship:{source}|{relationship_type}|{target}"


def _collection(doc: Mapping[str, Any], name: str) -> list[Mapping[str, Any]]:
    entries = doc.get(name) or []
    if not isinstance(entries, list):
        raise GraphError(f"{name}: expected a list")
    return [entry for entry in entries if isinstance(entry, Mapping)]


def _reviews_by_assertion(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for review in _collection(doc, "reviews"):
        target = review.get("reviews")
        if isinstance(target, str):
            result[target] = review
    return result


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        if all(item is None or isinstance(item, (str, int, float, bool)) for item in value):
            return value
        return json.dumps(value, sort_keys=True, default=str)
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)
