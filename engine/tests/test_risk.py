"""Table lookup, worst-path reduction, and honest handling of missing inputs (#63)."""

from copy import deepcopy
from itertools import product

import pytest

from engine.graph import GraphError
from engine.risk import CATEGORIES, FEASIBILITIES, MATRIX_ID, assess_document, risk_value


def model(ratings=("low", "high")):
    return {
        "parties": [{"id": "party:user"}],
        "threat_instances": [{"id": "threat:t", "realizes_damage": "damage:d"}],
        "damage_scenarios": [{"id": "damage:d"}],
        "attack_steps": [{"id": f"step:{i}"} for i in range(len(ratings))],
        "attack_paths": [
            {
                "id": f"path:{i}",
                "steps": [f"step:{i}"],
                "realizes_threat": "threat:t",
                "attack_feasibility": rating,
            }
            for i, rating in enumerate(ratings)
        ],
        "risk_scores": [
            {
                "id": "risk:r",
                "threat": "threat:t",
                "damage_scenario": "damage:d",
                "for_stakeholder": "party:user",
                "attack_paths": [f"path:{i}" for i in range(len(ratings))],
                "impact": dict(
                    zip(CATEGORIES, ("severe", "major", "moderate", "negligible"), strict=True)
                ),
                "mitigation_status": "planned",
                "feasibility": "low",  # stale aggregate; the path ratings drive computation
                "risk": "historical authored text, not a computed result",
            }
        ],
    }


def assessment(doc):
    return assess_document(doc, matrix=MATRIX_ID)["assessments"][0]


@pytest.mark.parametrize(
    ("severity", "expected"),
    [
        ("negligible", [1, 1, 1, 1]),
        ("moderate", [1, 2, 2, 3]),
        ("major", [1, 2, 3, 4]),
        ("severe", [2, 3, 4, 5]),
    ],
)
def test_every_annex_h_table_cell(severity, expected):
    # RPT-0007 §4.2, Table H.8. These include pairs where H.10's formula differs.
    assert [risk_value(severity, f, matrix=MATRIX_ID) for f in FEASIBILITIES] == expected


def test_vector_keeps_inputs_and_categories_and_does_not_trust_authored_risk():
    out = assessment(model())
    assert out["complete"]
    assert out["derived_risk"] == dict(zip(CATEGORIES, (5, 4, 3, 1), strict=True))
    assert out["feasibility"] == "high"
    assert out["recorded"]["feasibility"] == "low"
    assert out["recorded"]["risk"] == "historical authored text, not a computed result"
    assert out["for_stakeholder"] == "party:user"


@pytest.mark.parametrize("ratings", list(product(FEASIBILITIES, repeat=2)))
def test_worst_path_is_at_least_each_route_for_every_category(ratings):
    out = assessment(model(ratings))
    for category in CATEGORIES:
        individual = [p["derived_risk"][category] for p in out["paths"]]
        assert out["derived_risk"][category] == max(individual)
        assert 1 <= out["derived_risk"][category] <= 5


@pytest.mark.parametrize(
    "status", [None, "planned", "in_progress", "complete", "accepted_risk", "not_applicable"]
)
def test_mitigation_status_never_changes_derived_risk(status):
    doc = model()
    doc["risk_scores"][0]["mitigation_status"] = status
    out = assessment(doc)
    assert out["mitigation_status"] == status
    assert out["derived_risk"] == assessment(model())["derived_risk"]


def test_unrated_path_prevents_a_false_best_known_aggregate():
    doc = model(("high", None))
    out = assessment(doc)
    assert not out["complete"]
    assert out["feasibility"] is None
    assert all(value is None for value in out["derived_risk"].values())
    assert out["paths"][0]["derived_risk"]["safety"] == 5
    assert "path:1:feasibility_missing" in out["problems"]


def test_missing_impact_category_is_unknown_not_negligible():
    doc = model()
    del doc["risk_scores"][0]["impact"]["safety"]
    out = assessment(doc)
    assert not out["complete"]
    assert out["impact"]["safety"] is None
    assert out["derived_risk"]["safety"] is None
    assert out["derived_risk"]["financial"] == 4


def branching_model(gate):
    doc = model(("medium",))
    doc["attack_steps"] = [
        {"id": "step:a", "precedes": ["step:join"]},
        {"id": "step:b", "precedes": ["step:join"]},
        {"id": "step:join", "gate": gate},
    ]
    # Shared prerequisites need not be repeated in the authored path's steps.
    doc["attack_paths"][0]["steps"] = ["step:join"]
    return doc


def test_and_prerequisites_keep_a_single_path_level_rating():
    out = assessment(branching_model("and_gate"))
    assert out["complete"]
    assert out["paths"][0]["alternatives"] == [["step:a", "step:b", "step:join"]]
    assert out["derived_risk"]["safety"] == 4


def test_or_alternatives_do_not_silently_inherit_one_rating():
    out = assessment(branching_model("or_gate"))
    assert not out["complete"]
    assert out["paths"][0]["alternatives"] == [
        ["step:a", "step:join"],
        ["step:b", "step:join"],
    ]
    assert "path:0:alternative_route_ratings_required" in out["problems"]
    assert all(value is None for value in out["derived_risk"].values())


def test_omitting_a_route_from_the_authored_score_does_not_lower_risk():
    doc = model()
    doc["risk_scores"][0]["attack_paths"] = ["path:0"]
    out = assessment(doc)
    assert not out["complete"]
    assert "attack_path_scope_mismatch" in out["problems"]
    assert len(out["paths"]) == 2
    assert out["derived_risk"]["safety"] is None


def test_missing_assessment_stays_in_output_without_invented_ratings():
    doc = model()
    doc["risk_scores"] = []
    out = assessment(doc)
    assert out["id"] is None
    assert not out["complete"]
    assert all(value is None for value in out["derived_risk"].values())


def test_reviews_are_preserved_and_not_accepted_by_calculation():
    doc = model()
    doc["assertions"] = [
        {
            "id": "assertion:a",
            "subject": "path:0",
            "predicate": "realizes_threat",
            "object": "threat:t",
            "assertion_status": "proposed",
        }
    ]
    doc["reviews"] = [
        {"id": "review:a", "reviews": "assertion:a", "review_status": "rejected"},
        {"id": "review:b", "reviews": "assertion:a", "review_status": "changes_requested"},
    ]
    before = deepcopy(doc)
    out = assessment(doc)
    assert doc == before
    assert out["paths"][0]["review_records"]["assertions"][0]["assertion_status"] == "proposed"
    assert len(out["paths"][0]["review_records"]["reviews"]) == 2
    # Proposals are reported with evidence, never silently removed from the worst-path fold.
    assert len(out["paths"]) == 2


@pytest.mark.parametrize(
    "field,value", [("impact", 4), ("mitigation_status", "safe"), ("feasibility", "easy")]
)
def test_bad_ratings_are_validation_errors(field, value):
    doc = model()
    doc["risk_scores"][0][field] = value
    with pytest.raises(GraphError):
        assessment(doc)


def test_matrix_is_an_explicit_profile_not_a_guessed_formula():
    with pytest.raises(GraphError, match="matrix"):
        risk_value("severe", "high", matrix="cvss")
    with pytest.raises(GraphError, match="impact"):
        risk_value("critical", "high", matrix=MATRIX_ID)
    with pytest.raises(GraphError, match="feasibility"):
        risk_value("severe", 4, matrix=MATRIX_ID)


def test_unknown_goal_is_rejected():
    with pytest.raises(GraphError, match="unknown goal"):
        assess_document(model(), matrix=MATRIX_ID, goal="threat:absent")


def test_foreign_damage_cannot_supply_a_threats_impact():
    doc = model()
    doc["damage_scenarios"].append({"id": "damage:other"})
    doc["risk_scores"][0]["damage_scenario"] = "damage:other"
    out = assessment(doc)
    assert "damage_scenario_scope_mismatch" in out["problems"]
    assert all(value is None for value in out["derived_risk"].values())


def test_assessments_remain_separate_without_a_stakeholder_collapse():
    doc = model()
    doc["parties"].append({"id": "party:other"})
    other = deepcopy(doc["risk_scores"][0])
    other.update(id="risk:other", for_stakeholder="party:other")
    other["impact"]["financial"] = "negligible"
    doc["risk_scores"].append(other)
    out = assess_document(doc, matrix=MATRIX_ID)["assessments"]
    assert len(out) == 2
    assert out[0]["for_stakeholder"] == "party:user"
    assert out[0]["derived_risk"]["financial"] == 4
    assert out[1]["for_stakeholder"] == "party:other"
    assert out[1]["derived_risk"]["financial"] == 1


def test_all_current_vectors_can_be_reported_and_serialized():
    import json
    from pathlib import Path

    from engine.load.vector import load_vector_document

    vectors = Path(__file__).resolve().parents[2] / "spec" / "vectors"
    for path in vectors.glob("*.yaml"):
        if ".linkml." in path.name:
            continue
        out = assess_document(load_vector_document(path), matrix=MATRIX_ID)
        assert out["assessments"], path.name
        json.dumps(out)


def test_headlamp_rating_projection_matches_rpt0007():
    # RPT-0007 §4.2: spoofing has high/medium/low paths, safety severe -> 5.
    # DoS has two low paths, operational moderate -> 2. Other impact categories
    # were not supplied in that example, so do not fill them with negligible.
    spoofing = model(("high", "medium", "low"))
    spoofing["risk_scores"][0]["impact"] = {"safety": "severe"}
    dos = model(("low", "low"))
    dos["risk_scores"][0]["impact"] = {"operational": "moderate"}
    assert assessment(spoofing)["feasibility"] == "high"
    assert assessment(spoofing)["derived_risk"]["safety"] == 5
    assert assessment(dos)["feasibility"] == "low"
    assert assessment(dos)["derived_risk"]["operational"] == 2
    assert assessment(dos)["derived_risk"]["privacy"] is None
