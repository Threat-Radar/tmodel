from pathlib import Path

import pytest

from engine.graph import AttackGraph, GraphError
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
