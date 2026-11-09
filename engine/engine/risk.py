"""Risk calculations over model records, independent of storage and transport (#63).

ADR-0006 keeps human-supplied path feasibility, S/F/O/P impact and mitigation
status visible alongside derived risk. The caller explicitly selects the
illustrative Annex H table profile; no CVSS/CC or mitigation adjustment enters
the calculation. RPT-0007 §4.2 records the values; §4.3 explains why the example
formula is not interchangeable with this table.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any

from engine.graph import AttackGraph, GraphError
from engine.model_graph import project_model_graph
from engine.risk_routes import rated_routes

MATRIX_ID = "annex-h-table-h8"
CATEGORIES = ("safety", "financial", "operational", "privacy")
FEASIBILITIES = ("very_low", "low", "medium", "high")
# Informative example, not a claim that ISO mandates this particular matrix.
_TABLE = {
    "negligible": (1, 1, 1, 1),
    "moderate": (1, 2, 2, 3),
    "major": (1, 2, 3, 4),
    "severe": (2, 3, 4, 5),
}
MITIGATION_STATUSES = ("planned", "in_progress", "complete", "accepted_risk", "not_applicable")


def _matrix(matrix: str) -> None:
    if matrix != MATRIX_ID:
        raise GraphError(f"matrix: select {MATRIX_ID!r} explicitly")


def risk_value(impact: str, feasibility: str, *, matrix: str) -> int:
    """One impact category and one recorded path rating -> one table value."""
    _matrix(matrix)
    if not isinstance(impact, str) or impact not in _TABLE:
        raise GraphError(f"impact: expected one of {tuple(_TABLE)}")
    if not isinstance(feasibility, str) or feasibility not in FEASIBILITIES:
        raise GraphError(f"feasibility: expected one of {FEASIBILITIES}")
    return _TABLE[impact][FEASIBILITIES.index(feasibility)]


def assess_document(
    doc: Mapping[str, Any], *, matrix: str, goal: str | None = None
) -> dict[str, Any]:
    """Compute existing RiskScore assessments; list unrated threats as incomplete.

    Missing inputs stay missing. OR routes use separately authored path ratings
    matched to their complete steps, never a broad path's shared rating.
    Computation neither accepts an assertion nor creates a human review.
    """
    _matrix(matrix)
    project_model_graph(doc)  # duplicate ids and schema-backed references must resolve
    graph = AttackGraph.from_dict(doc)
    threats = _records(doc, "threat_instances")
    damages = _records(doc, "damage_scenarios")
    paths = _records(doc, "attack_paths")
    scores = _records(doc, "risk_scores")
    parties = _records(doc, "parties")
    if goal is not None and goal not in threats:
        raise GraphError("unknown goal: expected a threat-instance id in this model")

    assessments = []
    covered: set[str] = set()
    for score in scores.values():
        threat = score.get("threat")
        if not isinstance(threat, str) or threat not in threats:
            raise GraphError(f"{score['id']}: threat must reference a ThreatInstance")
        if goal is not None and threat != goal:
            continue
        covered.add(threat)
        assessments.append(_assessment(doc, graph, score, threat, damages, paths, parties, matrix))
    for threat in threats:
        if threat not in covered and (goal is None or threat == goal):
            assessments.append(_assessment(doc, graph, {}, threat, damages, paths, parties, matrix))
    return {"matrix": matrix, "count": len(assessments), "assessments": assessments}


def _records(doc: Mapping[str, Any], key: str) -> dict[str, Mapping[str, Any]]:
    # project_model_graph has already validated all these collections and ids.
    return {record["id"]: record for record in doc.get(key) or []}


def _optional_enum(value: Any, choices: Collection[str], field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value not in choices:
        raise GraphError(f"{field}: expected one of {tuple(choices)}")
    return value


def _assessment(
    doc: Mapping[str, Any],
    graph: AttackGraph,
    score: Mapping[str, Any],
    threat: str,
    damages: Mapping[str, Any],
    paths: Mapping[str, Any],
    parties: Mapping[str, Any],
    matrix: str,
) -> dict[str, Any]:
    problems: list[str] = []
    damage = score.get("damage_scenario")
    if damage is None:
        problems.append("damage_scenario_missing")
    elif not isinstance(damage, str) or damage not in damages:
        raise GraphError("damage_scenario: expected a DamageScenario reference")
    linked_damage = _records(doc, "threat_instances")[threat].get("realizes_damage")
    if damage is not None and linked_damage is not None and damage != linked_damage:
        problems.append("damage_scenario_scope_mismatch")
    stakeholder = score.get("for_stakeholder")
    if stakeholder is not None and (not isinstance(stakeholder, str) or stakeholder not in parties):
        raise GraphError("for_stakeholder: expected a Party reference")
    # Do not select an owner or combine stakeholders; preserve the assessment's scope.
    impact = score.get("impact")
    if impact is not None and not isinstance(impact, Mapping):
        raise GraphError("impact: expected a mapping with S/F/O/P ratings")
    if impact is not None and set(impact) - set(CATEGORIES):
        raise GraphError("impact: only safety, financial, operational and privacy are supported")
    impact = {
        category: _optional_enum((impact or {}).get(category), _TABLE, f"impact.{category}")
        for category in CATEGORIES
    }
    for category, rating in impact.items():
        if rating is None:
            problems.append(f"impact_missing:{category}")
    mitigation = _optional_enum(
        score.get("mitigation_status"), MITIGATION_STATUSES, "mitigation_status"
    )
    if mitigation is None:
        problems.append("mitigation_status_missing")
    recorded_feasibility = _optional_enum(score.get("feasibility"), FEASIBILITIES, "feasibility")
    recorded_risk = score.get("risk")
    if recorded_risk is not None and not isinstance(recorded_risk, str):
        raise GraphError("risk: expected authored text, not a computed numeric field")

    selected = graph.paths_for_threat(threat)
    if not selected:
        problems.append("attack_paths_missing")
    # A supplied assessment scope must agree with the threat's paths. Never
    # silently omit a harder/easier route or fold a different threat's path in.
    scope = score.get("attack_paths")
    if scope is not None and (
        not isinstance(scope, list) or not all(isinstance(item, str) for item in scope)
    ):
        raise GraphError("attack_paths: expected a list of AttackPath references")
    expected = {path.id for path in selected}
    if scope is not None and set(scope) != expected:
        problems.append("attack_path_scope_mismatch")

    ratings = {
        path.id: _optional_enum(
            paths[path.id].get("attack_feasibility"), FEASIBILITIES, "attack_feasibility"
        )
        for path in selected
    }
    routes = rated_routes(graph, threat, ratings) if selected else []
    for route in routes:
        route["derived_risk"] = _derived(impact, route["feasibility"], matrix)
        problems.extend(f"{route['id']}:{problem}" for problem in route["problems"])

    path_results = []
    for path in selected:
        owned = [route for route in routes if path.id in route["rating_paths"]]
        unbound = [
            route
            for route in routes
            if not route["rating_paths"] and route["authored_path"] == path.id
        ]
        visible = owned + unbound
        path_problems = sorted(
            {
                "alternative_route_ratings_required"
                if problem == "route_rating_required"
                else problem
                for route in visible
                for problem in route["problems"]
            }
        )
        rated = bool(owned) and all(route["feasibility"] is not None for route in owned)
        rating = (
            max((route["feasibility"] for route in owned), key=FEASIBILITIES.index)
            if rated
            else None
        )
        path_results.append(
            {
                "id": path.id,
                "feasibility": ratings[path.id],
                "rating_source": "AttackPath.attack_feasibility",
                "used_for_ratings": bool(owned),
                "route_ids": [route["id"] for route in visible],
                "alternatives": [route["steps"] for route in visible],
                "derived_risk": _derived(impact, rating, matrix),
                "review_records": _review_records(doc, path.id, threat),
                "problems": path_problems,
            }
        )
        problems.extend(f"{path.id}:{problem}" for problem in path_problems)
    all_routes_rated = bool(routes) and all(route["feasibility"] is not None for route in routes)
    feasibility = (
        max((route["feasibility"] for route in routes), key=FEASIBILITIES.index)
        if all_routes_rated
        else None
    )
    scope_valid = damage is not None and not any("scope_mismatch" in p for p in problems)
    derived = {
        category: risk_value(severity, feasibility, matrix=matrix)
        if severity is not None and feasibility is not None and scope_valid
        else None
        for category, severity in impact.items()
    }
    return {
        "id": score.get("id"),
        "threat": threat,
        "damage_scenario": damage,
        "for_stakeholder": stakeholder,
        "feasibility": feasibility,
        "impact": impact,
        "mitigation_status": mitigation,
        "derived_risk": derived,
        "recorded": {"feasibility": recorded_feasibility, "risk": recorded_risk},
        "paths": path_results,
        "routes": routes,
        "complete": not problems,
        "problems": problems,
    }


def _derived(
    impact: Mapping[str, str | None], rating: str | None, matrix: str
) -> dict[str, int | None]:
    return {
        category: risk_value(severity, rating, matrix=matrix)
        if severity is not None and rating is not None
        else None
        for category, severity in impact.items()
    }


def _review_records(doc: Mapping[str, Any], path_id: str, threat: str) -> dict[str, Any]:
    """Keep every matching review; do not manufacture a verdict from file order."""
    assertions = [
        record
        for record in doc.get("assertions") or []
        if record.get("subject") == path_id
        and record.get("predicate") == "realizes_threat"
        and record.get("object") == threat
    ]
    ids = {record["id"] for record in assertions}
    return {
        "assertions": [_review_fields(record) for record in assertions],
        "reviews": [
            _review_fields(record)
            for record in doc.get("reviews") or []
            if record.get("reviews") in ids
        ],
    }


def _review_fields(record: Mapping[str, Any]) -> dict[str, str | None]:
    # YAML timestamps may be date/datetime objects; keep the API JSON-safe.
    fields = (
        "id",
        "assertion_status",
        "asserted_by",
        "asserted_at",
        "reviews",
        "reviewer",
        "review_status",
        "justification",
    )
    return {
        key: str(record[key]) if record[key] is not None else None
        for key in fields
        if key in record
    }
