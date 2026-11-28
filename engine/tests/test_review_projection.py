"""One engine-authored review contract shared by report, graph, paths and risk."""

import json
import os
from copy import deepcopy
from pathlib import Path

import pytest

from engine.graph import AttackGraph
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths
from engine.risk import MATRIX_ID, assess_document

CASES = {
    "agent_only": ([("agent", "accepted", "Automated opinion")], False),
    "unjustified_human": ([("human", "accepted", " ")], False),
    "multiple_human_assertions": (
        [("human", "accepted", "Checked"), ("human2", "accepted", "Checked independently")],
        True,
    ),
    "human_accepts_agent_rejects": (
        [("human", "accepted", "Checked"), ("agent", "rejected", "Automated concern")],
        True,
    ),
    "human_rejects_agent_accepts": (
        [("human", "rejected", "Invalid path"), ("agent", "accepted", "Automated opinion")],
        False,
    ),
    "no_review": ([], False),
}
FIXTURE = Path(__file__).parents[2] / "apps/desktop/src/fixtures/review-evidence.json"


def document(name):
    reviews, _ = CASES[name]
    doc = {
        "parties": [
            {
                "id": f"party:{party}",
                "name": party,
                "party_kind": "software_agent" if party == "agent" else "person",
            }
            for party in ("human", "human2", "agent")
        ],
        "threat_instances": [
            {
                "id": "threat:t",
                "name": "Fixture threat",
                "source_method": "ai:fixture",
                "realizes_damage": "damage:d",
            }
        ],
        "damage_scenarios": [{"id": "damage:d", "name": "Fixture damage"}],
        "attack_steps": [{"id": "step:a", "name": "Fixture step"}],
        "attack_paths": [
            {
                "id": "path:a",
                "name": "Fixture route",
                "steps": ["step:a"],
                "realizes_threat": "threat:t",
                "attack_feasibility": "high",
            }
        ],
        "risk_scores": [
            {
                "id": "risk:r",
                "threat": "threat:t",
                "damage_scenario": "damage:d",
                "for_stakeholder": "party:human",
                "attack_paths": ["path:a"],
                "impact": {
                    key: "moderate" for key in ("safety", "financial", "operational", "privacy")
                },
                "mitigation_status": "planned",
            }
        ],
        "assertions": [
            {
                "id": "assertion:a",
                "subject": "path:a",
                "predicate": "realizes_threat",
                "object": "threat:t",
                "assertion_status": "accepted",
            }
        ],
        "reviews": [],
    }
    for index, (party, verdict, rationale) in enumerate(reviews):
        assertion = "assertion:a"
        if name == "multiple_human_assertions" and index:
            assertion = f"assertion:{index}"
            doc["assertions"].append({**doc["assertions"][0], "id": assertion})
        doc["reviews"].append(
            {
                "id": f"review:{index}",
                "reviews": assertion,
                "reviewer": f"party:{party}",
                "review_status": verdict,
                "justification": rationale,
            }
        )
    return doc


def example(name):
    doc = document(name)
    before = deepcopy(doc)
    graph = AttackGraph.from_dict(doc)
    projection = project_model_graph(doc).to_dict()
    paths = [p.to_dict() for p in enumerate_paths(graph, "threat:t")]
    risk = assess_document(doc, matrix=MATRIX_ID)
    assert doc == before
    return {
        "name": name,
        "human_reviewed": CASES[name][1],
        "input": {
            "model": {
                "id": "review-evidence",
                "file": "review-evidence.yaml",
                "title": "Synthetic review evidence",
                "description": "Test judgments only.",
                "kind": "core",
                "kind_label": "Synthetic fixture",
                "counts": {},
                "reviewed_threats": int(graph.threat_reviewed("threat:t")),
            },
            "graph": {"file": "review-evidence.yaml", **projection},
            "attackPaths": [{"file": "review-evidence.yaml", "goal": "threat:t", "paths": paths}],
        },
        "risk": {"file": "review-evidence.yaml", **risk},
    }


@pytest.mark.parametrize("name", CASES)
def test_human_acceptance_matches_across_engine_outputs(name):
    out = example(name)
    expected = out["human_reviewed"]
    edge = next(
        e
        for e in out["input"]["graph"]["edges"]
        if e["source"] == "path:a" and e["relationship_type"] == "realizes_threat"
    )
    assert edge["properties"]["human_reviewed"] is expected
    assert out["risk"]["assessments"][0]["path_reviewed"] is expected
    assert out["input"]["attackPaths"][0]["paths"][0]["review"]["reviewed"] is expected
    assert edge["assertions"][0]["assertion_status"] == "accepted"
    if name == "agent_only":
        assert edge["properties"]["review_status"] == "accepted"
    elif name == "human_accepts_agent_rejects":
        assert edge["properties"]["review_status"] == "rejected"


def test_frontend_review_evidence_fixture_matches_the_engine():
    current = {
        "note": "Synthetic review judgments, not human project sign-offs.",
        "cases": [example(name) for name in CASES],
    }
    if os.environ.get("TMODEL_UPDATE_FIXTURES") == "1":
        FIXTURE.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n")
    assert json.loads(FIXTURE.read_text()) == current
