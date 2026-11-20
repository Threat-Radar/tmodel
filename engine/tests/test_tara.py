"""TARA collection keeps model identity, provenance and incomplete assessments."""

from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
from test_risk import model

from engine import core
from engine.graph import GraphError
from engine.load.vector import load_vector_document
from engine.model_graph import COLLECTION_DOMAIN_TYPES
from engine.risk import MATRIX_ID
from engine.tara import collect_document, serialize

MODEL = "mvp-02-automotive-ecu.yaml"
ROOT = Path(__file__).resolve().parents[2]


def minimal():
    doc = model(("high",))
    doc["products"] = [{"id": "product:p", "name": "Test product"}]
    doc["parties"][0]["party_kind"] = "person"
    doc["assertions"] = [
        {
            "id": "assertion:path",
            "subject": "path:0",
            "predicate": "realizes_threat",
            "object": "threat:t",
            "assertion_status": "accepted",
        }
    ]
    doc["reviews"] = [
        {
            "id": "review:accept",
            "reviews": "assertion:path",
            "reviewer": "party:user",
            "review_status": "accepted",
            "justification": "Recorded human assessment.",
        }
    ]
    return doc


def item(out, collection, oid):
    return next(r for r in out["records"][collection] if r["id"] == oid)


def test_mvp02_contains_all_source_records_with_ids_and_review_states():
    doc = load_vector_document(ROOT / "spec/vectors" / MODEL)
    before = deepcopy(doc)
    out = core.collect_tara(MODEL, MATRIX_ID)
    assert out["source"] == {"file": MODEL, "example_data": True}
    assert out["scope"] == {
        "kind": "whole_model",
        "product_ids": ["product:telematics-control-unit"],
    }
    for name in COLLECTION_DOMAIN_TYPES:
        rows = out["records"][name]
        assert {r["id"] for r in rows} == {r["id"] for r in doc.get(name) or []}
        for row in rows:
            assert row["data"]["id"] == row["id"]
            assert "reviewed" in row["review_state"]
    assert len(out["records"]["assets"]) == 2
    assert len(out["records"]["threat_instances"]) == 2
    assert doc == before
    assert "not an approved TARA" in out["notice"]


def test_rejected_ai_path_and_proposed_requirement_claim_are_not_hidden_or_accepted():
    out = core.collect_tara(MODEL, MATRIX_ID)
    path = item(out, "attack_paths", "attack-path:infotainment-pivot")
    assert path["review_state"]["status"] == "rejected"
    assert not path["review_state"]["reviewed"]
    assertion = item(out, "assertions", "assertion:ai-pivot-realizes")
    assert assertion["data"]["assertion_status"] == "proposed"
    assert assertion["review_state"]["review_ids"] == ["review:ai-pivot-reject"]
    proposed = item(out, "assertions", "assertion:ai-req-addresses-pivot")
    assert proposed["review_state"]["status"] == "proposed"
    assert not proposed["review_state"]["reviewed"]
    req = item(out, "requirements", "requirement:family-authenticated-diagnostics")
    assert "threat-instance:infotainment-pivot" not in req["data"].get("addresses", [])


def test_computed_risk_keeps_rated_and_incomplete_hypotheses_separate_from_authored_data():
    out = core.collect_tara(MODEL, MATRIX_ID)
    risks = {r["threat"]: r for r in out["calculated_risk"]["assessments"]}
    diag = risks["threat-instance:remote-diag-injection"]
    assert diag["derived_risk"] == {"safety": 5, "financial": 4, "operational": 5, "privacy": 1}
    assert diag["mitigation_status"] == "in_progress"
    assert diag["source_id"] == "risk-score:remote-diag-injection"
    assert not diag["review_state"]["reviewed"]
    pivot = risks["threat-instance:infotainment-pivot"]
    assert not pivot["complete"]
    assert len(pivot["routes"]) == 2
    assert pivot["derived_risk"]["safety"] is None
    assert pivot["source_id"] == "threat-instance:infotainment-pivot"
    assert not pivot["review_state"]["reviewed"]
    raw = item(out, "risk_scores", "risk-score:remote-diag-injection")
    assert isinstance(raw["data"]["impact"], dict)
    assert isinstance(raw["data"]["risk"], str)
    assert not raw["review_state"]["reviewed"]  # no direct approval is invented


@pytest.mark.parametrize("reverse", [False, True])
def test_all_contrary_reviews_survive_and_file_order_cannot_erase_rejection(reverse):
    doc = minimal()
    rejected = {**doc["reviews"][0], "id": "review:reject", "review_status": "rejected"}
    doc["reviews"].append(rejected)
    if reverse:
        doc["reviews"].reverse()
    out = collect_document(doc, matrix=MATRIX_ID)
    state = item(out, "attack_paths", "path:0")["review_state"]
    assert state["status"] == "rejected"
    assert not state["reviewed"]
    assert state["review_ids"] == ["review:accept", "review:reject"]
    assert len(out["records"]["reviews"]) == 2


@pytest.mark.parametrize("party_kind", ["software_agent", "organization", None])
def test_only_recorded_person_reviews_can_supply_human_acceptance(party_kind):
    doc = minimal()
    doc["parties"][0]["party_kind"] = party_kind
    state = item(collect_document(doc, matrix=MATRIX_ID), "assertions", "assertion:path")[
        "review_state"
    ]
    assert not state["reviewed"]
    assert state["status"] == "unreviewed"
    assert state["assertions"][0]["human_review_ids"] == []
    assert state["review_ids"] == ["review:accept"]


def test_accepted_assertion_without_review_is_not_presented_as_human_reviewed():
    doc = minimal()
    doc["reviews"] = []
    out = collect_document(doc, matrix=MATRIX_ID)
    state = item(out, "assertions", "assertion:path")["review_state"]
    assert not state["reviewed"]
    assert state["assertions"][0]["assertion_status"] == "accepted"


def test_proposed_assertion_is_not_promoted_by_an_accepted_review():
    doc = minimal()
    doc["assertions"][0]["assertion_status"] = "proposed"
    state = item(collect_document(doc, matrix=MATRIX_ID), "assertions", "assertion:path")[
        "review_state"
    ]
    assert state["status"] == "proposed"
    assert not state["reviewed"]


def test_non_string_status_on_a_non_path_assertion_is_a_useful_input_error():
    doc = minimal()
    doc["assertions"].append(
        {
            "id": "assertion:bad-status",
            "subject": "product:p",
            "predicate": "related_to",
            "object": "threat:t",
            "assertion_status": date(2026, 11, 14),
        }
    )
    with pytest.raises(GraphError, match="assertion_status must be a string"):
        collect_document(doc, matrix=MATRIX_ID)


def test_recorded_person_acceptance_is_visible_but_does_not_approve_endpoint_objects():
    out = collect_document(minimal(), matrix=MATRIX_ID)
    state = item(out, "attack_paths", "path:0")["review_state"]
    assert state["reviewed"]
    assert state["scope"] == "related_assertions"
    assert state["assertion_ids"] == ["assertion:path"]
    assert not item(out, "products", "product:p")["review_state"]["reviewed"]


def test_requirement_links_distinguish_slots_from_proposed_assertions():
    doc = minimal()
    doc["requirements"] = [
        {"id": "requirement:family", "satisfied_by": ["mitigation:specific"]},
        {"id": "requirement:proposed"},
    ]
    doc["mitigations"] = [
        {"id": "mitigation:generic", "stated_as": ["requirement:family"]},
        {"id": "mitigation:specific"},
    ]
    doc["assertions"].append(
        {
            "id": "assertion:stated-as",
            "subject": "mitigation:generic",
            "predicate": "stated_as",
            "object": "requirement:proposed",
            "assertion_status": "proposed",
        }
    )
    out = collect_document(doc, matrix=MATRIX_ID)
    links = out["requirement_links"]
    assert len(links) == 3
    link = next(link for link in links if link["origin"] == "assertion")
    assert link["object"] == "requirement:proposed"
    assert link["review_state"]["status"] == "proposed"
    assert not link["review_state"]["reviewed"]
    generic = item(out, "mitigations", "mitigation:generic")
    assert generic["data"]["stated_as"] == ["requirement:family"]
    assert {link["predicate"] for link in links} == {"stated_as", "satisfied_by"}


def test_dangling_stated_as_cannot_become_a_silent_missing_requirement():
    doc = minimal()
    doc["mitigations"] = [{"id": "mitigation:m", "stated_as": ["requirement:missing"]}]
    with pytest.raises(GraphError, match="stated_as"):
        collect_document(doc, matrix=MATRIX_ID)


def test_dates_and_unicode_are_portable_and_source_is_unchanged():
    doc = minimal()
    doc["products"][0].update(name="Télématique", valid_from=date(2026, 11, 14))
    before = deepcopy(doc)
    out = collect_document(doc, matrix=MATRIX_ID)
    assert item(out, "products", "product:p")["data"]["valid_from"] == "2026-11-14"
    assert "Télématique" in serialize(out)
    assert doc == before


def test_missing_or_malformed_input_is_refused():
    with pytest.raises(GraphError, match="Product"):
        collect_document({}, matrix=MATRIX_ID)
    doc = minimal()
    doc["products"][0]["bad_number"] = float("nan")
    with pytest.raises(GraphError, match="JSON-compatible"):
        collect_document(doc, matrix=MATRIX_ID)
