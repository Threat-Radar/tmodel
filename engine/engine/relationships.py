"""Authored or human-accepted relationships shared by model queries."""

from collections.abc import Mapping
from typing import Any

from engine.model_graph import ModelEdge, ModelGraph
from engine.review import relationship_review_states


def effective_edges(doc: Mapping[str, Any], graph: ModelGraph) -> tuple[ModelEdge, ...]:
    """Keep authored links and exact Assertion links with justified human acceptance."""
    states = relationship_review_states(doc)
    return tuple(
        edge
        for edge in graph.edges
        if edge.authored
        or states.get((edge.source, edge.relationship_type, edge.target), {}).get("reviewed", False)
    )
