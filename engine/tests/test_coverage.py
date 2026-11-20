"""Coverage changes only with recorded scope, status and human-reviewed links."""

import copy
import json
import threading
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

from engine import cli, core
from engine.api.server import make_server
from engine.coverage import collect
from engine.graph import GraphError
from engine.load.vector import load_vector_document

FILE = "mvp-02-automotive-ecu.yaml"
PRODUCT = "product:telematics-control-unit"


@pytest.fixture
def doc():
    return copy.deepcopy(load_vector_document(core.APPROVED_VECTOR_DIRECTORY / FILE))


def test_mvp02(doc):
    before = copy.deepcopy(doc)
    result = collect(doc, PRODUCT)
    assert doc == before
    assert result["count"] == 5
    assert result["counts"] == {"satisfied": 2, "in_progress": 0, "unsatisfied": 3}
    assert result["unaddressed_threats"] == ["threat-instance:infotainment-pivot"]
    (proposal,) = result["proposed_assertions"]
    assert proposal["id"] == "assertion:ai-req-addresses-pivot"
    assert proposal["if_accepted"]["unaddressed_threats"] == []
    assert "requirement:gateway-filter-safety-can" not in {r["id"] for r in result["requirements"]}


def test_scope_instance_nested_used_and_cycle(doc):
    instance = doc["product_instances"][0]
    doc["components"].append({"id": "component:instance-only", "name": "Instance-only"})
    instance["build_composed_of"] = ["component:instance-only"]
    doc["components"][-1]["composed_of"] = ["component:instance-only"]
    targets = [instance["id"], "component:instance-only", "component:diag-service-lib"]
    for i, target in enumerate(targets):
        doc["requirements"].append({"id": f"requirement:scope-{i}", "applies_to": [target]})
    assert collect(doc, PRODUCT)["count"] == 8
    doc["products"].append({"id": "product:other", "name": "Other"})
    assert collect(doc, "product:other")["count"] == 0


def test_status_rules_and_no_inheritance(doc):
    req = doc["requirements"][0]
    req["satisfied_by"] = ["mitigation:domain-gateway-firewall"]
    result = collect(doc, PRODUCT)
    assert (
        next(r for r in result["requirements"] if r["id"] == req["id"])["status"] == "in_progress"
    )
    req["satisfied_by"].append("mitigation:authenticate-diag-service")
    assert collect(doc, PRODUCT)["counts"]["satisfied"] == 3
    req["satisfied_by"] = ["mitigation:family-authenticated-diagnostics"]
    assert collect(doc, PRODUCT)["counts"]["unsatisfied"] == 3


def accept(doc, assertion):
    assertion["assertion_status"] = "accepted"
    doc["reviews"].append(
        {
            "id": "review:coverage-test",
            "reviews": assertion["id"],
            "reviewer": "party:av-reviewer",
            "review_status": "accepted",
            "justification": "Test fixture only",
        }
    )


def test_acceptance_needs_human_and_no_contrary_review(doc):
    a = doc["assertions"][-1]
    a["assertion_status"] = "accepted"
    assert collect(doc, PRODUCT)["unaddressed_threats"]
    accept(doc, a)
    assert collect(doc, PRODUCT)["unaddressed_threats"] == []
    doc["reviews"].append(
        {
            "id": "review:contrary",
            "reviews": a["id"],
            "reviewer": "party:av-reviewer",
            "review_status": "rejected",
        }
    )
    assert collect(doc, PRODUCT)["unaddressed_threats"]
    doc["reviews"].reverse()
    assert collect(doc, PRODUCT)["unaddressed_threats"]
    doc["reviews"] = [r for r in doc["reviews"] if r["id"] != "review:contrary"]
    doc["parties"].append({"id": "party:software", "party_kind": "software_agent"})
    next(r for r in doc["reviews"] if r["id"] == "review:coverage-test")["reviewer"] = (
        "party:software"
    )
    assert collect(doc, PRODUCT)["unaddressed_threats"]


def test_accepted_scope_and_satisfaction_assertions(doc):
    a = {
        "id": "assertion:scope",
        "subject": "requirement:gateway-filter-safety-can",
        "predicate": "applies_to",
        "object": PRODUCT,
    }
    doc["assertions"].append(a)
    accept(doc, a)
    assert collect(doc, PRODUCT)["count"] == 6
    assert collect(doc, PRODUCT)["counts"]["in_progress"] == 1
    a = {
        "id": "assertion:satisfy",
        "subject": "requirement:iso21434-rq-08-07",
        "predicate": "satisfied_by",
        "object": "mitigation:authenticate-diag-service",
    }
    doc["assertions"].append(a)
    accept(doc, a)
    doc["reviews"][-1]["id"] = "review:satisfy"
    # Earlier accept helper gives a repeated review id; keep every model identity unique.
    assert collect(doc, PRODUCT)["counts"]["satisfied"] == 3


def test_proposals_with_joint_scope_effect_and_irrelevant_links(doc):
    req = {"id": "requirement:proposed-scope"}
    doc["requirements"].append(req)
    for aid, pred, target in [
        ("scope", "applies_to", PRODUCT),
        ("address", "addresses", "threat-instance:infotainment-pivot"),
    ]:
        doc["assertions"].append(
            {
                "id": f"assertion:{aid}",
                "subject": req["id"],
                "predicate": pred,
                "object": target,
                "assertion_status": "proposed",
            }
        )
    result = collect(doc, PRODUCT)
    assert result["count"] == 5
    proposal = next(p for p in result["proposed_assertions"] if p["id"] == "assertion:address")
    assert proposal["effect"] == "with_other_proposals"
    assert result["if_all_proposed_accepted"]["count"] == 6
    assert result["if_all_proposed_accepted"]["unaddressed_threats"] == []
    assert proposal["if_accepted"]["unaddressed_threats"]  # individually unchanged


@pytest.mark.parametrize(
    "slot,target",
    [
        ("applies_to", "component:missing"),
        ("satisfied_by", PRODUCT),
        ("addresses", "mitigation:authenticate-diag-service"),
    ],
)
def test_invalid_references_fail(doc, slot, target):
    doc["requirements"][0][slot] = [target]
    with pytest.raises(GraphError):
        collect(doc, PRODUCT)


def test_bad_product_and_families(doc):
    with pytest.raises(GraphError, match="unknown product"):
        collect(doc, "component:diag-service-lib")
    doc["products"][0]["classifications"] = [7]
    with pytest.raises(GraphError):
        collect(doc, PRODUCT)


def test_api_cli_parity_and_validation(capsys, tmp_path, monkeypatch):
    params = {"file": FILE, "product": PRODUCT}
    expected = core.requirement_coverage(params)
    assert cli.main(["coverage", FILE, "--product", PRODUCT, "--json", "--in-process"]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        with urlopen(f"{url}/coverage?{urlencode(params)}") as response:
            assert json.load(response) == expected
        assert cli.main(["coverage", FILE, "--product", PRODUCT, "--url", url, "--json"]) == 0
        assert json.loads(capsys.readouterr().out) == expected
        for query in [
            {},
            {"file": FILE},
            {**params, "product": " "},
            {**params, "extra": "x"},
            {**params, "file": str(tmp_path / "secret.yaml")},
        ]:
            with pytest.raises(HTTPError) as exc:
                urlopen(f"{url}/coverage?{urlencode(query)}")
            assert exc.value.code == 400
    finally:
        httpd.shutdown()
        httpd.server_close()
    (tmp_path / "secret.yaml").write_text("products: []")
    approved = tmp_path / "approved"
    approved.mkdir()
    (approved / "escape.yaml").symlink_to(tmp_path / "secret.yaml")
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", approved)
    with pytest.raises(GraphError, match="outside approved"):
        core.requirement_coverage({**params, "file": "escape.yaml"})


def test_minimal_model_without_attack_structure_and_empty_collections():
    doc = {"products": [{"id": "product:minimal"}], "requirements": [], "assertions": None}
    assert collect(doc, "product:minimal")["count"] == 0


def test_invalid_mitigation_status_and_redundant_proposals(doc):
    doc["mitigations"][0]["mitigation_status"] = {"invalid": "complete"}
    with pytest.raises(GraphError, match="mitigation_status"):
        collect(doc, PRODUCT)
    doc["mitigations"][0]["mitigation_status"] = "complete"
    # A proposed copy of an already authored edge cannot change the answer.
    doc["assertions"].append(
        {
            "id": "assertion:already-authored",
            "subject": "requirement:tcu-diag-authentication",
            "predicate": "satisfied_by",
            "object": "mitigation:authenticate-diag-service",
            "assertion_status": "proposed",
        }
    )
    assert "assertion:already-authored" not in {
        a["id"] for a in collect(doc, PRODUCT)["proposed_assertions"]
    }


def test_empty_cli_coverage_is_usage_error_and_bad_product_is_error(capsys):
    with pytest.raises(SystemExit) as error:
        cli.main(["coverage", FILE])
    assert error.value.code == 2
    assert cli.main(["coverage", FILE, "--product", "product:missing", "--in-process"]) == 1
    assert "unknown product" in capsys.readouterr().err


@pytest.mark.parametrize("justification", [None, "", "  ", 7, False, {}])
def test_malformed_justification_cannot_accept_an_assertion(doc, justification):
    a = doc["assertions"][-1]
    accept(doc, a)
    doc["reviews"][-1]["justification"] = justification
    assert collect(doc, PRODUCT)["unaddressed_threats"]


def test_only_a_party_can_be_a_human_reviewer(doc):
    a = doc["assertions"][-1]
    accept(doc, a)
    component = doc["components"][0]
    component["party_kind"] = "person"
    doc["reviews"][-1]["reviewer"] = component["id"]
    assert collect(doc, PRODUCT)["unaddressed_threats"]
