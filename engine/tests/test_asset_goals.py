"""Asset queries follow explicit, grounded relationships, preserving attack logic."""

from copy import deepcopy

import pytest

from engine.graph import AttackGraph, GraphError
from engine.paths import enumerate_paths


def model():
    return {
        "assets": [{"id": "asset:target"}, {"id": "asset:unlinked"}],
        "damage_scenarios": [{"id": "damage:one", "damages_asset": ["asset:target"]}],
        "threat_instances": [
            {"id": "threat:direct", "targets_element": ["asset:target"]},
            {"id": "threat:damage", "realizes_damage": "damage:one"},
        ],
        "attack_steps": [
            {"id": "step:left", "precedes": ["step:goal"], "kill_chain_phase": "entry"},
            {"id": "step:right", "precedes": ["step:goal"]},
            {"id": "step:goal", "gate": "or_gate", "kill_chain_phase": "execution"},
        ],
        "attack_paths": [
            {"id": "path:direct", "steps": ["step:goal"], "realizes_threat": "threat:direct"},
            {"id": "path:damage", "steps": ["step:goal"], "realizes_threat": "threat:damage"},
        ],
    }


def test_direct_and_damage_routes_keep_threat_identity_and_phases():
    graph = AttackGraph.from_dict(model())
    paths = enumerate_paths(graph, "asset:target")
    assert [path.threat for path in paths] == ["threat:damage"] * 2 + ["threat:direct"] * 2
    assert [path.steps for path in paths[:2]] == [
        ("step:left", "step:goal"),
        ("step:right", "step:goal"),
    ]
    assert paths[0].to_dict()["step_phases"] == {"step:left": "entry", "step:goal": "execution"}
    assert paths[0].authored_path == "path:damage"
    assert not any(path.review.reviewed for path in paths)
    assert enumerate_paths(graph, "asset:unlinked") == []
    with pytest.raises(GraphError, match="unknown goal"):
        enumerate_paths(graph, "asset:unknown")


def test_asset_query_keeps_and_logic_and_enforces_total_limit():
    doc = model()
    doc["attack_steps"][-1]["gate"] = "and_gate"
    graph = AttackGraph.from_dict(doc)
    assert all(
        path.steps == ("step:left", "step:right", "step:goal")
        for path in enumerate_paths(graph, "asset:target")
    )
    with pytest.raises(GraphError, match="more than 1 attack paths"):
        enumerate_paths(graph, "asset:target", limit=1)


@pytest.mark.parametrize(
    "status,verdict,person,reason,expected",
    [
        ("proposed", "accepted", True, "Checked", False),
        ("accepted", "accepted", False, "Checked", False),
        ("accepted", "accepted", True, "", False),
        ("accepted", "rejected", True, "Checked", False),
        ("accepted", "accepted", True, "Checked", True),
    ],
)
def test_asset_assertions_need_justified_human_acceptance(
    status, verdict, person, reason, expected
):
    doc = model()
    doc["threat_instances"] = [{"id": "threat:direct"}, {"id": "threat:damage"}]
    doc["parties"] = [{"id": "party:r", "party_kind": "person" if person else "software_agent"}]
    doc["assertions"] = [
        {
            "id": "assertion:target",
            "subject": "threat:direct",
            "predicate": "targets_element",
            "object": "asset:target",
            "assertion_status": status,
        }
    ]
    doc["reviews"] = [
        {
            "id": "review:target",
            "reviews": "assertion:target",
            "reviewer": "party:r",
            "review_status": verdict,
            "justification": reason,
        }
    ]
    before = deepcopy(doc)
    paths = enumerate_paths(AttackGraph.from_dict(doc), "asset:target")
    assert bool(paths) is expected
    assert doc == before


def test_unlinked_threat_or_component_location_does_not_establish_asset_damage():
    doc = model()
    doc["components"] = [{"id": "component:host"}]
    doc["assets"][0]["stored_in"] = ["component:host"]
    doc["threat_instances"] = [
        {"id": "threat:direct", "targets_element": ["component:host"]},
        {"id": "threat:damage"},
    ]
    assert enumerate_paths(AttackGraph.from_dict(doc), "asset:target") == []


def reviewed_link(doc, target="threat:damage", status="accepted"):
    doc["parties"] = [{"id": "party:person", "party_kind": "person"}]
    doc["assertions"] = [
        {
            "id": "assertion:path",
            "subject": "path:direct",
            "predicate": "realizes_threat",
            "object": target,
            "assertion_status": status,
        }
    ]
    doc["reviews"] = [
        {
            "id": "review:accept",
            "reviews": "assertion:path",
            "reviewer": "party:person",
            "review_status": "accepted",
            "justification": "Checked this exact relationship.",
        }
    ]


def test_shared_path_cannot_borrow_another_threats_review():
    doc = model()
    reviewed_link(doc)
    for assertions in (doc["assertions"], list(reversed(doc["assertions"]))):
        doc["assertions"] = assertions
        routes = enumerate_paths(AttackGraph.from_dict(doc), "asset:target")
        direct = [route for route in routes if route.threat == "threat:direct"]
        secondary = [route for route in routes if route.threat == "threat:damage"]
        assert direct and not any(route.review.reviewed for route in direct)
        assert secondary and all(route.review.reviewed for route in secondary)


@pytest.mark.parametrize(
    "status,verdict,expected",
    [
        ("accepted", "accepted", True),
        ("proposed", "accepted", False),
        ("accepted", "rejected", False),
        ("accepted", "changes_requested", False),
    ],
)
def test_assertion_only_path_links_require_human_acceptance(status, verdict, expected):
    doc = model()
    doc["attack_paths"] = [doc["attack_paths"][0]]
    doc["attack_paths"][0].pop("realizes_threat")
    reviewed_link(doc, "threat:direct", status)
    doc["reviews"][0]["review_status"] = verdict
    graph = AttackGraph.from_dict(doc)
    routes = enumerate_paths(graph, "asset:target")
    assert bool(routes) is expected
    if expected:
        assert graph.threats() == ["threat:direct"]
        assert all(route.threat == "threat:direct" and route.review.reviewed for route in routes)


@pytest.mark.parametrize("same_assertion", [True, False])
def test_all_matching_human_verdicts_count_independently_of_record_order(same_assertion):
    doc = model()
    reviewed_link(doc, "threat:direct")
    if not same_assertion:
        other = {**doc["assertions"][0], "id": "assertion:other"}
        doc["assertions"].append(other)
    doc["reviews"].append(
        {
            "id": "review:reject",
            "reviews": "assertion:path" if same_assertion else "assertion:other",
            "reviewer": "party:person",
            "review_status": "rejected",
            "justification": "Contrary evidence.",
        }
    )
    for _ in range(2):
        routes = enumerate_paths(AttackGraph.from_dict(doc), "threat:direct")
        assert all(
            not route.review.reviewed and route.review.review_status == "rejected"
            for route in routes
        )
        doc["reviews"].reverse()
        doc["assertions"].reverse()


@pytest.mark.parametrize("person,reason", [(False, "Checked"), (True, "")])
def test_path_acceptance_requires_a_person_and_rationale(person, reason):
    doc = model()
    reviewed_link(doc, "threat:direct")
    doc["parties"][0]["party_kind"] = "person" if person else "software_agent"
    doc["reviews"][0]["justification"] = reason
    assert not any(
        route.review.reviewed
        for route in enumerate_paths(AttackGraph.from_dict(doc), "threat:direct")
    )
