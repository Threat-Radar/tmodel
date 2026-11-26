"""Explicit asset targets for attack-path queries (#63, ADR-0011).

Use authored relationships or Assertions with justified human acceptance. Mere
co-location in a component does not establish that an attack reaches an asset.
"""

from collections.abc import Mapping
from typing import Any

from engine.model_graph import project_model_graph
from engine.review import relationship_review_states


def asset_threats(doc: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    graph = project_model_graph(doc)
    types = {node.id: node.domain_type for node in graph.nodes}
    targets: dict[str, set[str]] = {
        node.id: set() for node in graph.nodes if node.domain_type == "Asset"
    }
    states = relationship_review_states(doc)
    edges = [
        edge
        for edge in graph.edges
        if edge.authored
        or states.get((edge.source, edge.relationship_type, edge.target), {}).get("reviewed", False)
    ]
    damaged: dict[str, set[str]] = {}
    for edge in edges:
        if (
            edge.relationship_type == "damages_asset"
            and types[edge.source] == "DamageScenario"
            and edge.target in targets
        ):
            damaged.setdefault(edge.source, set()).add(edge.target)
    for edge in edges:
        if types[edge.source] != "ThreatInstance":
            continue
        if edge.relationship_type == "targets_element" and edge.target in targets:
            targets[edge.target].add(edge.source)
        elif edge.relationship_type == "realizes_damage":
            for asset in damaged.get(edge.target, ()):
                targets[asset].add(edge.source)
    return {asset: tuple(sorted(threats)) for asset, threats in targets.items()}
