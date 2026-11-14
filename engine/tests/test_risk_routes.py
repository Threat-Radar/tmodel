"""Separate ratings for OR routes without changing global path enumeration."""

from copy import deepcopy
from itertools import product

import pytest
from test_risk import assessment, branching_model, model

from engine.risk import CATEGORIES, FEASIBILITIES, MATRIX_ID, assess_document


def separately_rated(a="low", b="high"):
    doc = branching_model("or_gate")
    doc["attack_paths"] = [
        {
            "id": "path:physical",
            "steps": ["step:a", "step:join"],
            "realizes_threat": "threat:t",
            "attack_feasibility": a,
        },
        {
            "id": "path:remote",
            "steps": ["step:b", "step:join"],
            "realizes_threat": "threat:t",
            "attack_feasibility": b,
        },
    ]
    doc["risk_scores"][0]["attack_paths"] = ["path:physical", "path:remote"]
    return doc


def test_separate_ratings_follow_the_right_or_route():
    out = assessment(separately_rated())
    assert out["complete"]
    assert out["feasibility"] == "high"
    assert len(out["routes"]) == 2
    routes = {tuple(route["steps"]): route for route in out["routes"]}
    a = routes[("step:a", "step:join")]
    b = routes[("step:b", "step:join")]
    assert a["feasibility"] == "low"
    assert a["rating_paths"] == ["path:physical"]
    assert a["derived_risk"]["safety"] == 3
    assert b["feasibility"] == "high"
    assert b["rating_paths"] == ["path:remote"]
    assert b["derived_risk"]["safety"] == 5
    assert out["derived_risk"]["safety"] == 5
    assert out["paths"][0]["alternatives"] == [["step:a", "step:join"]]
    assert out["paths"][1]["alternatives"] == [["step:b", "step:join"]]


@pytest.mark.parametrize("ratings", list(product(FEASIBILITIES, repeat=2)))
def test_or_route_worst_risk_equals_max_in_each_category(ratings):
    out = assessment(separately_rated(*ratings))
    assert out["complete"]
    for category in CATEGORIES:
        assert out["derived_risk"][category] == max(
            route["derived_risk"][category] for route in out["routes"]
        )


def test_missing_specific_rating_is_not_filled_by_other_route():
    out = assessment(separately_rated("low", None))
    assert not out["complete"]
    assert out["feasibility"] is None
    assert all(value is None for value in out["derived_risk"].values())
    assert out["routes"][0]["derived_risk"]["safety"] == 3
    assert out["routes"][1]["derived_risk"]["safety"] is None


def test_unrated_alternative_is_not_dropped_when_only_one_route_has_a_record():
    doc = separately_rated()
    doc["attack_paths"] = doc["attack_paths"][:1]
    doc["risk_scores"][0]["attack_paths"] = ["path:physical"]
    out = assessment(doc)
    assert len(out["routes"]) == 2  # the global OR graph still has two possibilities
    assert not out["complete"]
    assert out["routes"][0]["feasibility"] == "low"
    assert out["routes"][1]["feasibility"] is None
    assert out["routes"][1]["problems"] == ["route_rating_required"]


def test_legacy_or_rating_does_not_override_specific_routes():
    doc = separately_rated("very_low", "low")
    doc["attack_paths"].insert(
        0,
        {
            "id": "path:broad",
            "steps": ["step:a", "step:b", "step:join"],
            "realizes_threat": "threat:t",
            "attack_feasibility": "high",
        },
    )
    doc["risk_scores"][0]["attack_paths"].append("path:broad")
    out = assessment(doc)
    assert out["complete"]
    assert out["feasibility"] == "low"
    assert all("path:broad" not in route["rating_paths"] for route in out["routes"])
    assert not out["paths"][0]["used_for_ratings"]
    assert out["paths"][0]["derived_risk"]["safety"] is None


def test_conflicting_duplicate_ratings_stay_unresolved():
    doc = separately_rated()
    duplicate = deepcopy(doc["attack_paths"][0])
    duplicate.update(id="path:conflict", attack_feasibility="high")
    doc["attack_paths"].append(duplicate)
    doc["risk_scores"][0]["attack_paths"].append("path:conflict")
    out = assessment(doc)
    assert not out["complete"]
    assert out["routes"][0]["problems"] == ["conflicting_route_ratings"]
    assert out["derived_risk"]["safety"] is None


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("full_rating", ["low", None, "high"])
def test_full_and_single_route_legacy_records_both_own_their_rating(full_rating, reverse):
    # The old partial record and the full record describe the same route.
    # A full record must not silently hide a higher rating or borrow a missing one.
    doc = model(("high",))
    doc["attack_steps"].insert(0, {"id": "step:pre", "precedes": ["step:0"]})
    full = deepcopy(doc["attack_paths"][0])
    full.update(id="path:full", steps=["step:pre", "step:0"], attack_feasibility=full_rating)
    doc["attack_paths"].append(full)
    doc["risk_scores"][0]["attack_paths"].append("path:full")
    if reverse:
        doc["attack_paths"].reverse()
    out = assessment(doc)
    route = out["routes"][0]
    assert set(route["rating_paths"]) == {"path:0", "path:full"}
    assert all(path["used_for_ratings"] for path in out["paths"])
    if full_rating == "high":
        assert out["complete"]
        assert route["feasibility"] == "high"
        assert out["derived_risk"]["safety"] == 5
    else:
        assert not out["complete"]
        assert route["feasibility"] is None
        assert route["problems"] == ["conflicting_route_ratings"]
        assert out["feasibility"] is None
        assert all(value is None for value in out["derived_risk"].values())


def test_same_rating_on_both_routes_still_keeps_individual_results():
    out = assessment(separately_rated("medium", "medium"))
    assert out["complete"]
    assert len(out["routes"]) == 2
    assert out["routes"][0]["id"] != out["routes"][1]["id"]


def test_route_ids_and_binding_survive_record_reordering():
    doc = separately_rated()
    before = assessment(doc)
    doc["attack_steps"].reverse()
    doc["attack_paths"].reverse()
    doc["risk_scores"][0]["attack_paths"].reverse()
    after = assessment(doc)
    assert {route["id"]: route for route in before["routes"]} == {
        route["id"]: route for route in after["routes"]
    }


def test_shared_and_prerequisites_cannot_be_omitted_from_a_rating_record():
    doc = separately_rated()
    doc["attack_steps"].extend(
        [
            {"id": "step:pre1", "precedes": ["step:a"]},
            {"id": "step:pre2", "precedes": ["step:a"]},
        ]
    )
    doc["attack_steps"][0]["gate"] = "and_gate"
    doc["attack_paths"][0]["steps"] = ["step:pre1", "step:pre2", "step:a", "step:join"]
    out = assessment(doc)
    a = next(route for route in out["routes"] if "step:a" in route["steps"])
    assert out["complete"]
    assert set(a["steps"]) == {"step:pre1", "step:pre2", "step:a", "step:join"}
    assert a["feasibility"] == "low"

    doc["attack_paths"][0]["steps"] = ["step:a", "step:join"]
    out = assessment(doc)
    assert not out["complete"]  # a partial OR record could rate either global route
    assert (
        next(route for route in out["routes"] if "step:a" in route["steps"])["feasibility"] is None
    )


def test_ambiguous_or_record_never_claims_that_one_rating_covers_every_route():
    out = assessment(branching_model("or_gate"))
    assert not out["complete"]
    assert len(out["routes"]) == 2
    assert all(route["feasibility"] is None for route in out["routes"])


def test_sdl_only_example_has_no_fictional_risk_assessments():
    assert assess_document({"sdl_practices": []}, matrix=MATRIX_ID) == {
        "matrix": MATRIX_ID,
        "count": 0,
        "assessments": [],
    }


def test_accepted_sdl_records_do_not_break_risk_in_a_mixed_model():
    doc = separately_rated()
    doc["sdl_practices"] = [{"id": "practice:review"}]
    doc["evidence_items"] = [{"id": "evidence:test"}]
    doc["requirement_sources"] = [{"id": "source:requirements"}]
    doc["security_programs"] = [{"id": "program:demo"}]
    doc["assertions"] = [
        {
            "id": "assertion:select",
            "subject": "program:demo",
            "predicate": "selects_requirement_source",
            "object": "source:requirements",
            "assertion_status": "proposed",
        },
        {
            "id": "assertion:evidence",
            "subject": "practice:review",
            "predicate": "produces",
            "object": "evidence:test",
            "assertion_status": "proposed",
        },
    ]
    assert assessment(doc)["complete"]


@pytest.mark.parametrize("collection", ["sdl_practices", "evidence_items", "requirement_sources"])
@pytest.mark.parametrize("operation", ["add", "edit", "remove"])
def test_reading_sdl_records_does_not_expand_threat_proposal_permissions(collection, operation):
    from engine.propose import check_patch

    patch = {
        "schema": "tmodel.patch/v1",
        "target": "mvp-01-software-doc-service.yaml",
        "proposed_by": "party:agent",
        "generated_by": "test fixture",
        "rationale": "Permission boundary regression",
    }
    if operation == "add":
        patch[operation] = {collection: [{"id": "example:x"}]}
    else:
        patch[operation] = [{"collection": collection, "id": "example:x", "set": {"name": "x"}}]
    with pytest.raises(ValueError, match="not a collection"):
        check_patch(patch, "threat")
