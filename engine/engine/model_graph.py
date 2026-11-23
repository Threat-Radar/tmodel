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
    # ADR-0013: mixed SDL/threat models may reference these from Assertions.
    "sdl_practices": "SdlPractice",
    "evidence_items": "Evidence",
    "requirement_sources": "RequirementSource",
    # ADR-0011 (accepted 2026-10-22) added these classes to the core; the proposal
    # container lists them.
    "assets": "Asset",
    "trust_boundaries": "TrustBoundary",
    "data_flows": "DataFlow",
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
        "build_composed_of",
        "instance_of",
        "asserted_by",
        "stored_in",
        "processed_by",
        "in_trust_zone",
        "within_boundary",
        "flow_from",
        "flow_to",
        "carries",
        "crosses_boundary",
        "damages_asset",
        "targets_element",
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
        "addresses",
        "stated_as",
        "satisfied_by",
        "refines",
        "derived_from",
        "conflicts_with",
        "applies_to",
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
    authored: bool
    assertions: tuple[Mapping[str, Any], ...]
    properties: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "authored": self.authored,
            "assertions": [dict(assertion) for assertion in self.assertions],
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
        # A frozenset iterates in hash order, which changes per process; sort it
        # so the `/graph` edge order is the same on every engine start.
        for slot in sorted(RELATIONSHIP_SLOTS):
            if slot not in raw:
                continue
            for target in _references(source, slot, raw[slot]):
                if target not in ids:
                    raise GraphError(f"{source}: {slot} references unknown object {target}")
                _add_edge(edges, source, target, slot, authored=True)

    reviews = _reviews_by_assertion(doc)
    for assertion in _collection(doc, "assertions"):
        subject = assertion.get("subject")
        predicate = assertion.get("predicate")
        object_id = assertion.get("object")
        if not all(isinstance(value, str) for value in (subject, predicate, object_id)):
            raise GraphError(
                f"{assertion['id']}: assertion subject, predicate, and object must be strings"
            )
        assertion_reviews = reviews.get(assertion["id"], [])
        assertion_provenance: dict[str, Any] = {
            "id": assertion["id"],
            "assertion_status": _json_value(assertion.get("assertion_status")),
            "confidence": _json_value(assertion.get("confidence")),
            "description": None,
            "evidence": [],
            "reviews": [],
        }
        description = assertion.get("description")
        if isinstance(description, str) and description.strip():
            assertion_provenance["description"] = description
        evidence = assertion.get("evidence")
        if isinstance(evidence, list) and all(isinstance(item, str) for item in evidence):
            assertion_provenance["evidence"] = evidence
        if assertion_reviews:
            assertion_provenance["reviews"] = [
                {
                    "id": review["id"],
                    "review_status": _json_value(review.get("review_status")),
                    "reviewer": _json_value(review.get("reviewer")),
                    "justification": _json_value(review.get("justification")),
                }
                for review in assertion_reviews
            ]
        _add_edge(edges, subject, object_id, predicate, assertion=assertion_provenance)

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
    *,
    authored: bool = False,
    assertion: Mapping[str, Any] | None = None,
) -> None:
    key = (source, relationship_type, target)
    previous = edges.get(key)
    assertions = list(previous.assertions if previous else ())
    if assertion is not None:
        assertions.append(assertion)
    edges[key] = ModelEdge(
        id=_edge_id(source, relationship_type, target),
        source=source,
        target=target,
        relationship_type=relationship_type,
        authored=authored or bool(previous and previous.authored),
        assertions=tuple(assertions),
        properties=_assertion_summary(assertions),
    )


def _assertion_summary(assertions: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Backward-compatible display properties; full provenance stays per Assertion."""
    if not assertions:
        return {}
    properties: dict[str, Any] = {"assertion_ids": [item["id"] for item in assertions]}
    reviews = [review for item in assertions for review in item.get("reviews", [])]
    if len(assertions) > 1:
        properties["assertion_statuses"] = [
            item.get("assertion_status") or "not_recorded" for item in assertions
        ]
        properties["assertion_confidences"] = [
            item.get("confidence") or "not_recorded" for item in assertions
        ]
        if reviews:
            properties["review_ids"] = [review["id"] for review in reviews]
            properties["review_statuses"] = [
                review.get("review_status") or "not_recorded" for review in reviews
            ]
        return properties

    assertion = assertions[0]
    for name in ("assertion_status", "confidence"):
        if assertion.get(name) is not None:
            properties[name] = assertion[name]
    if assertion.get("description"):
        properties["assertion_descriptions"] = [assertion["description"]]
    if assertion.get("evidence"):
        properties["assertion_evidence"] = assertion["evidence"]
    if reviews:
        statuses = [
            review.get("review_status")
            for review in reviews
            if isinstance(review.get("review_status"), str)
        ]
        justifications = [
            review["justification"]
            for review in reviews
            if isinstance(review.get("justification"), str) and review["justification"].strip()
        ]
        properties.update(
            {
                "review_ids": [review["id"] for review in reviews],
                "review_status": _combined_review_status(statuses),
                "review_statuses": statuses,
                "review_justifications": justifications,
            }
        )
    return properties


def _edge_id(source: str, relationship_type: str, target: str) -> str:
    return f"relationship:{source}|{relationship_type}|{target}"


def _collection(doc: Mapping[str, Any], name: str) -> list[Mapping[str, Any]]:
    entries = doc.get(name) or []
    if not isinstance(entries, list):
        raise GraphError(f"{name}: expected a list")
    return [entry for entry in entries if isinstance(entry, Mapping)]


def _reviews_by_assertion(doc: Mapping[str, Any]) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for review in _collection(doc, "reviews"):
        target = review.get("reviews")
        if isinstance(target, str):
            result.setdefault(target, []).append(review)
    return result


def _combined_review_status(statuses: list[Any]) -> str | None:
    """Conservative display status when several Reviews target one Assertion."""
    normalized = [status.strip().lower().replace("-", "_") for status in statuses]
    if "rejected" in normalized:
        return "rejected"
    if "changes_requested" in normalized:
        return "changes_requested"
    if normalized and all(status == "accepted" for status in normalized):
        return "accepted"
    return normalized[0] if len(set(normalized)) == 1 else "mixed"


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
