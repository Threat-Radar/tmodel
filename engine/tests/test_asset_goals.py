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
