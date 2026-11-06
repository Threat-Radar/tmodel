import json
from pathlib import Path

import pytest

from engine.graph import AttackGraph, GraphError, ReviewState
from engine.load.vector import load_vector

VECTORS = Path(__file__).resolve().parents[2] / "spec" / "vectors"
EXAMPLE_MODELS = sorted(p for p in VECTORS.glob("*.yaml") if ".linkml." not in p.name)


def doc(steps, paths=()):
    return {"attack_steps": list(steps), "attack_paths": list(paths)}


def test_example_models_are_found():
    names = {p.name for p in EXAMPLE_MODELS}
    assert "mvp-01-software-doc-service.yaml" in names
    assert len(EXAMPLE_MODELS) >= 6


@pytest.mark.parametrize("path", EXAMPLE_MODELS, ids=lambda p: p.stem)
def test_every_example_model_loads(path):
    graph = load_vector(path)
    assert graph.steps
    assert graph.paths


def test_mvp01_structure():
    graph = load_vector(VECTORS / "mvp-01-software-doc-service.yaml")
    assert graph.summary() == {
        "steps": 7,
        "paths": 2,
        "threats": ["threat-instance:imds-pivot", "threat-instance:xxe-file-read"],
    }
    read = graph.steps["attack-step:read-internal-file"]
    assert read.gate == "and_gate"
    assert read.kill_chain_phase == "exploitation"
    assert graph.predecessors(read.id) == [
        "attack-step:parser-resolves-entity",
        "attack-step:coerce-file-uri",
    ]
    assert [p.id for p in graph.paths_for_threat("threat-instance:xxe-file-read")] == [
        "attack-path:xxe-file-read"
    ]


def test_unknown_gate_is_rejected():
    with pytest.raises(GraphError, match="unknown gate"):
        AttackGraph.from_dict(doc([{"id": "s1", "gate": "xor_gate"}]))


def test_precedes_must_resolve():
    with pytest.raises(GraphError, match="precedes unknown step s2"):
        AttackGraph.from_dict(doc([{"id": "s1", "precedes": ["s2"]}]))


def test_path_steps_must_resolve():
    with pytest.raises(GraphError, match="lists unknown step s9"):
        AttackGraph.from_dict(doc([{"id": "s1"}], [{"id": "p1", "steps": ["s1", "s9"]}]))


def test_duplicate_step_id_is_rejected():
    with pytest.raises(GraphError, match="duplicate attack step id"):
        AttackGraph.from_dict(doc([{"id": "s1"}, {"id": "s1"}]))


def test_non_mapping_file_is_rejected(tmp_path):
    bad = tmp_path / "list.yaml"
    bad.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(GraphError, match="expected a mapping"):
        load_vector(bad)


REVIEW_CASES = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / "apps"
        / "desktop"
        / "src"
        / "fixtures"
        / "review-state-cases.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize(
    "case",
    REVIEW_CASES,
    ids=[f"{c['assertion_status']}/{c['review_status']}" for c in REVIEW_CASES],
)
def test_review_state_counts_as_reviewed_exactly_when_the_app_shows_accepted(case):
    """The engine's `reviewed` (picker counts, `tmodel paths`) and the app's review
    state (report, path view) follow one rule: a negative Review wins, and only an
    accepted Assertion with no contrary Review is reviewed (#208)."""
    state = ReviewState(case["assertion_status"], case["review_status"])
    assert state.reviewed is (case["kind"] == "accepted"), case["why"]


def test_a_rejecting_review_keeps_an_accepted_assertions_threat_unreviewed():
    doc = {
        "attack_steps": [{"id": "attack-step:a"}],
        "attack_paths": [
            {"id": "attack-path:p", "steps": ["attack-step:a"], "realizes_threat": "threat:t"}
        ],
        "assertions": [
            {
                "id": "assertion:p",
                "subject": "attack-path:p",
                "predicate": "realizes_threat",
                "object": "threat:t",
                "assertion_status": "accepted",
            }
        ],
        "reviews": [{"id": "review:p", "reviews": "assertion:p", "review_status": "rejected"}],
    }
    graph = AttackGraph.from_dict(doc)
    assert graph.paths["attack-path:p"].review.to_dict() == {
        "reviewed": False,
        "assertion_status": "accepted",
        "review_status": "rejected",
    }
    assert graph.threat_reviewed("threat:t") is False
    doc["reviews"][0]["review_status"] = "accepted"
    assert AttackGraph.from_dict(doc).threat_reviewed("threat:t") is True
