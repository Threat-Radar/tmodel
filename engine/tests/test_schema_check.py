"""engine.schema_check: the LinkML container check the workspace runs on every save (#288).

DL-0081 records the cross-check against linkml-validate itself: the same verdict on 51
mutated copies of pv-01, mvp-02 and tv-software-auth-service.
"""

import copy
import datetime as dt

import pytest
import yaml

from engine import core
from engine import schema_check as sc
from engine.load.vector import load_vector_document

VECTORS = core.APPROVED_VECTOR_DIRECTORY
CONTAINERS = {"mvp-": "ExampleModelCore", "pv-": "ExampleModelProposed", "tv-": "ExampleModel"}
CONTAINERS["sdl-"] = "ExampleModelSdl"


def container(root):
    return sc.load_container(VECTORS, root)


def models():
    for path in sorted(VECTORS.glob("*.yaml")):
        if not path.name.endswith(".linkml.yaml"):
            yield path


@pytest.mark.parametrize("path", list(models()), ids=lambda p: p.name)
def test_every_example_fits_its_container(path):
    root = next(r for prefix, r in CONTAINERS.items() if path.name.startswith(prefix))
    assert sc.check(load_vector_document(path), container(root)) == []


@pytest.fixture
def pv01():
    return copy.deepcopy(load_vector_document(VECTORS / "pv-01-can-injection-theft.yaml"))


def problems(doc, root="ExampleModelProposed"):
    return sc.check(doc, container(root))


def test_unknown_collection(pv01):
    pv01["widgets"] = []
    assert problems(pv01)[0].field == "widgets"


def test_unknown_field_on_an_object(pv01):
    pv01["attack_paths"][0]["colour"] = "red"
    found = problems(pv01)
    assert found[0].field == "attack_paths[0].colour"
    assert "no field 'colour'" in found[0].message


def test_enum_value(pv01):
    pv01["attack_paths"][0]["attack_feasibility"] = "extreme"
    found = problems(pv01)
    assert found[0].field == "attack_paths[0].attack_feasibility"
    assert "FeasibilityLevel" in found[0].message


def test_missing_id_is_required(pv01):
    del pv01["attack_paths"][0]["id"]
    assert problems(pv01)[0].message.endswith("requires id")


def test_null_is_absent_for_optional_fields_but_not_required_ones(pv01):
    pv01["attack_paths"][0]["name"] = None
    assert problems(pv01) == []
    pv01["attack_paths"][0]["id"] = None
    assert problems(pv01)[0].field == "attack_paths[0].id"


def test_list_and_scalar_shapes(pv01):
    path = pv01["attack_paths"][0]
    path["steps"] = path["steps"][0]
    path["name"] = ["a", "b"]
    fields = {p.field: p.message for p in problems(pv01)}
    assert fields["attack_paths[0].steps"] == "expected a list"
    assert fields["attack_paths[0].name"] == "expected text"


def test_references_are_ids_not_objects(pv01):
    pv01["attack_paths"][0]["realizes_threat"] = {"id": "threat-instance:x"}
    assert "expected the id of a ThreatInstance" in problems(pv01)[0].message


def test_inlined_impact_vector_is_checked():
    doc = copy.deepcopy(load_vector_document(VECTORS / "mvp-02-automotive-ecu.yaml"))
    doc["risk_scores"][0]["impact"]["safety"] = "catastrophic"
    found = problems(doc, "ExampleModelCore")
    assert found[0].field == "risk_scores[0].impact.safety"


def test_any_of_reference_accepts_any_listed_class():
    slot = sc.Slot("targets", ("Component", "Asset"), False, False, False)
    out = []
    sc._check_value(7, slot, "Mitigation", "x", container("ExampleModelProposed"), out, 20)
    assert out[0].message == "expected the id of a Component or Asset"


def test_dates_and_datetimes():
    doc = copy.deepcopy(load_vector_document(VECTORS / "tv-software-auth-service.yaml"))
    doc["gates"][0]["planned_date"] = dt.date(2026, 10, 20)  # an unquoted YAML date
    assert problems(doc, "ExampleModel") == []
    doc["gates"][0]["planned_date"] = "20 October"
    doc["threat_models"][0]["created"] = "yesterday"
    fields = sorted(p.field for p in problems(doc, "ExampleModel"))
    assert fields == ["gates[0].planned_date", "threat_models[0].created"]


def test_core_container_refuses_proposed_collections(pv01):
    assert any(p.field == "data_flows" for p in problems(pv01, "ExampleModelCore"))


def test_problem_count_is_capped(pv01):
    for party in pv01["parties"]:
        party["colour"] = "red"
    assert len(sc.check(pv01, container("ExampleModelProposed"), limit=3)) == 3


def test_unsupported_linkml_feature_fails_loudly(tmp_path):
    (tmp_path / "schema").mkdir()
    vectors = tmp_path / "vectors"
    vectors.mkdir()
    (tmp_path / "schema" / "tmodel-object-model.linkml.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "x",
                "name": "x",
                "classes": {"Thing": {"slots": ["id"]}},
                "slots": {"id": {"identifier": True, "pattern": "^x"}},
            }
        )
    )
    (vectors / sc.CONTAINER_FILES["ExampleModelCore"]).write_text(
        yaml.safe_dump(
            {
                "id": "c",
                "name": "c",
                "imports": ["linkml:types", "../schema/tmodel-object-model.linkml"],
                "classes": {
                    "ExampleModelCore": {
                        "tree_root": True,
                        "attributes": {"things": {"range": "Thing", "multivalued": True}},
                    }
                },
            }
        )
    )
    with pytest.raises(sc.SchemaError, match="pattern"):
        sc.load_container(vectors, "ExampleModelCore")
