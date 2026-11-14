"""The example-model list behind the app's model picker (#208), and the
ADR-0011 classes in the graph projection that the model report reads."""

import json
import os
import threading
import urllib.request

import pytest

from engine import core
from engine.api.server import make_server
from engine.cli import main

VECTORS = core.APPROVED_VECTOR_DIRECTORY


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get_models(base, headers=None):
    request = urllib.request.Request(f"{base}/models", headers=headers or {})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, dict(response.headers), json.loads(response.read())


def test_lists_every_example_model_and_no_schema_harness():
    payload = core.list_models()
    files = [model["file"] for model in payload["models"]]
    assert payload["count"] == len(files)
    assert payload["problems"] == []
    # The issue asks for mvp-01, mvp-02 and at least one more example.
    assert {"mvp-01-software-doc-service.yaml", "mvp-02-automotive-ecu.yaml"} <= set(files)
    assert len(files) >= 3
    assert not any(name.endswith(".linkml.yaml") for name in files)
    on_disk = {
        p.name
        for p in VECTORS.iterdir()
        if p.suffix in (".yaml", ".yml")
        and not p.name.endswith(".linkml.yaml")
        and not p.name.startswith("sdl-")
    }
    assert set(files) == on_disk
    assert not any(name.startswith("sdl-") for name in files)


def test_core_examples_come_first_and_the_order_is_stable():
    first = core.list_models()
    assert first == core.list_models()
    kinds = [model["kind"] for model in first["models"]]
    assert kinds == sorted(kinds, key=["core", "worked", "proposal", "other"].index)
    core_files = [m["file"] for m in first["models"] if m["kind"] == "core"]
    assert core_files == sorted(core_files)


def test_titles_and_descriptions_come_from_the_model_itself():
    models = {model["id"]: model for model in core.list_models()["models"]}
    tcu = models["mvp-02-automotive-ecu"]
    assert tcu["file"] == "mvp-02-automotive-ecu.yaml"
    assert tcu["title"] == "Telematics Control Unit (TCU)"
    assert tcu["description"].startswith("Cellular-connected telematics ECU")
    assert tcu["kind_label"] == "Core example"
    assert tcu["counts"]["threats"] == 2
    assert tcu["counts"]["attack_paths"] == 2
    assert tcu["reviewed_threats"] == 1  # the remote path; the AI pivot was rejected
    assert models["pv-01-can-injection-theft"]["kind"] == "proposal"
    assert models["pv-01-can-injection-theft"]["reviewed_threats"] == 0


def test_every_listed_file_opens_through_the_graph_route():
    for model in core.list_models()["models"]:
        assert core.model_graph(model["file"])["nodes"]


def test_payload_names_no_local_path():
    text = json.dumps(core.list_models())
    assert str(VECTORS.resolve()) not in text
    assert str(VECTORS.resolve().parent) not in text


def test_a_broken_model_is_reported_and_the_rest_still_listed(tmp_path, monkeypatch):
    (tmp_path / "good.yaml").write_text(
        "products:\n  - id: product:a\n    name: Widget\n", encoding="utf-8"
    )
    (tmp_path / "bad.yaml").write_text("components: not-a-list\n", encoding="utf-8")
    (tmp_path / "empty.yaml").write_text("{}\n", encoding="utf-8")  # no model objects
    (tmp_path / "harness.linkml.yaml").write_text("id: harness\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a model\n", encoding="utf-8")
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", tmp_path)

    payload = core.list_models()
    assert [m["file"] for m in payload["models"]] == ["good.yaml"]
    assert payload["models"][0]["title"] == "Widget"
    assert payload["models"][0]["kind"] == "other"
    assert payload["problems"] == [
        {"file": "bad.yaml", "error": "bad.yaml: components: expected a list"}
    ]
    assert str(tmp_path) not in json.dumps(payload)


def test_a_model_without_products_is_titled_by_its_file(tmp_path, monkeypatch):
    (tmp_path / "bare.yaml").write_text(
        "components:\n  - id: component:a\n    name: A part\n", encoding="utf-8"
    )
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", tmp_path)
    [model] = core.list_models()["models"]
    assert model["title"] == "bare"
    assert model["description"] is None


def test_models_route_matches_core_and_is_cors_accessible_to_tauri(engine_url):
    status, headers, body = get_models(engine_url, {"Origin": "tauri://localhost"})
    assert status == 200
    assert headers.get("Access-Control-Allow-Origin") == "tauri://localhost"
    assert body == core.list_models()


def test_a_single_product_models_scope_is_its_own_description():
    mvp02 = next(
        m for m in core.list_models()["models"] if m["file"] == "mvp-02-automotive-ecu.yaml"
    )
    assert mvp02["title"] == "Telematics Control Unit (TCU)"
    assert mvp02["description"] == (
        "Cellular-connected telematics ECU bridging the mobile network and the in-vehicle CAN."
    )
    assert "\n" not in mvp02["description"]


def test_a_multi_product_models_scope_covers_every_product_in_model_order():
    mvp18 = next(
        m
        for m in core.list_models()["models"]
        if m["file"] == "mvp-18-shared-vuln-vex-override.yaml"
    )
    assert mvp18["title"] == "Crypto Server Appliance and Edge Sensor"
    lines = mvp18["description"].split("\n")
    assert [line.split(": ", 1)[0] for line in lines] == ["Crypto Server Appliance", "Edge Sensor"]
    assert lines[0].endswith("a TLS-terminating server appliance that embeds the SoC. AFFECTED.")
    assert "an edge sensor that embeds the SAME SoC/IP core" in lines[1]


def test_scope_uses_only_recorded_descriptions(tmp_path):
    """Nothing is made up: a product without a description adds no line, none gives None."""
    model = tmp_path / "multi.yaml"
    model.write_text(
        "products:\n"
        "  - id: product:a\n"
        "    name: Alpha\n"
        "    description: >-\n"
        "      First   product,\n"
        "      folded.\n"
        "  - id: product:b\n"
        "    name: Beta\n"
        "  - id: product:c\n"
        "    name: Gamma\n"
        "    description: Third product.\n",
        encoding="utf-8",
    )
    summary = core._model_summary(model)
    assert summary["title"] == "Alpha and Beta and Gamma"
    assert summary["description"] == "Alpha: First product, folded.\nGamma: Third product."
    model.write_text("products:\n  - id: product:a\n    name: Alpha\n", encoding="utf-8")
    assert core._model_summary(model)["description"] is None


def test_cli_lists_models_through_the_api_and_in_process(engine_url, capsys):
    assert main(["models", "--json", "--url", engine_url]) == 0
    via_api = json.loads(capsys.readouterr().out)
    assert main(["models", "--json", "--in-process"]) == 0
    assert json.loads(capsys.readouterr().out) == via_api
    assert main(["models", "--in-process"]) == 0
    text = capsys.readouterr().out
    assert "mvp-02-automotive-ecu.yaml" in text
    assert "Telematics Control Unit (TCU)" in text


def test_adr_0011_classes_are_projected_as_nodes():
    graph = core.model_graph("pv-01-can-injection-theft.yaml")
    by_id = {node["id"]: node for node in graph["nodes"]}
    assert by_id["asset:vehicle"]["domain_type"] == "Asset"
    assert by_id["asset:vehicle"]["label"] == "The vehicle"
    assert by_id["asset:vehicle"]["properties"]["security_properties"] == ["availability"]
    flow = by_id["data-flow:key-validated-to-gateway"]
    assert flow["domain_type"] == "DataFlow"
    assert "carries" not in flow["properties"]
    assert by_id["trust-boundary:control-domain"]["domain_type"] == "TrustBoundary"
    projected = {
        (edge["source"], edge["relationship_type"], edge["target"]) for edge in graph["edges"]
    }
    assert ("asset:vehicle", "owned_by", "party:vehicle-owner") in projected
    assert (
        "data-flow:key-validated-to-gateway",
        "carries",
        "asset:key-validated-message",
    ) in projected
    assert (
        "data-flow:key-validated-to-engine",
        "crosses_boundary",
        "trust-boundary:control-domain",
    ) in projected


GUI_FIXTURES = VECTORS.parents[1] / "apps" / "desktop" / "src" / "fixtures"


def report_input(file):
    """What the app's model report reads for one model: list entry, /graph, /attack-paths."""
    summary = next(m for m in core.list_models()["models"] if m["file"] == file)
    graph = core.model_graph(file)
    local = graph["file"]  # an absolute path; /attack-paths needs it, the fixture must not hold it
    paths = [core.attack_paths(local, goal) for goal in core.attack_paths(local)["threats"]]
    return {
        "model": summary,
        "graph": {**graph, "file": file},
        "attackPaths": [{**p, "file": file} for p in paths],
    }


NODE_KEYS = {"id", "domain_type", "label", "properties"}
EDGE_KEYS = {"id", "source", "target", "relationship_type", "properties"}


def _key_sets(items):
    return {frozenset(item) for item in items}


def _union_keys(items):
    return set().union(*(set(item) for item in items)) if items else set()


def assert_same_shape(saved, current, file):
    """Same keys at every level the GUI reads; values are free to differ."""
    hint = (
        f"the engine's response shape changed for {file}: update the GUI types "
        "(apps/desktop/src/model-types.ts, graph-types.ts), then refresh the fixture with "
        "TMODEL_UPDATE_FIXTURES=1 pytest tests/test_models_surface.py"
    )
    assert set(saved) == set(current) == {"model", "graph", "attackPaths"}, hint
    assert set(saved["model"]) == set(current["model"]), hint
    assert set(saved["model"]["counts"]) == set(current["model"]["counts"]), hint
    assert set(saved["graph"]) == set(current["graph"]), hint
    assert _key_sets(saved["graph"]["nodes"]) == {frozenset(NODE_KEYS)}, hint
    assert _key_sets(current["graph"]["nodes"]) == {frozenset(NODE_KEYS)}, hint
    assert _key_sets(saved["graph"]["edges"]) == {frozenset(EDGE_KEYS)}, hint
    assert _key_sets(current["graph"]["edges"]) == {frozenset(EDGE_KEYS)}, hint
    assert _key_sets(saved["attackPaths"]) == _key_sets(current["attackPaths"]), hint
    saved_paths = [p for answer in saved["attackPaths"] for p in answer["paths"]]
    current_paths = [p for answer in current["attackPaths"] for p in answer["paths"]]
    assert _union_keys(saved_paths) == _union_keys(current_paths), hint
    assert _union_keys([p["review"] for p in saved_paths]) == _union_keys(
        [p["review"] for p in current_paths]
    ), hint


@pytest.mark.parametrize(
    ("file", "fixture"),
    [
        ("mvp-01-software-doc-service.yaml", "report-input-mvp-01.json"),
        ("mvp-02-automotive-ecu.yaml", "report-input-mvp-02.json"),
        ("mvp-03-hierarchical-system.yaml", "report-input-mvp-03.json"),
    ],
)
def test_gui_report_fixtures_have_the_engines_response_shape(file, fixture):
    """The GUI's report tests run on a saved engine answer (apps/desktop/src/fixtures).

    This checks that the saved answer still has the shape the engine returns now,
    so a change to the engine's responses cannot slip past the GUI tests. It does
    not compare values: editing mvp-01 or mvp-02 does not oblige anyone to refresh
    the GUI's test data. TMODEL_UPDATE_FIXTURES=1 refreshes it on purpose.
    """
    current = report_input(file)
    path = GUI_FIXTURES / fixture
    if os.environ.get("TMODEL_UPDATE_FIXTURES") == "1":
        path.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    saved = json.loads(text)
    assert_same_shape(saved, current, file)
    assert saved["model"]["file"] == saved["graph"]["file"] == file
    assert "/Users/" not in text  # the fixture never holds a local path


def test_gui_fixture_check_allows_edited_model_values_and_catches_renamed_keys():
    current = report_input("mvp-02-automotive-ecu.yaml")
    # A teammate's edit to the model's content passes.
    edited = json.loads(json.dumps(current))
    edited["graph"]["nodes"][0]["label"] = "Renamed by a teammate"
    edited["graph"]["nodes"] = edited["graph"]["nodes"][1:]
    edited["model"]["counts"]["threats"] += 1
    assert_same_shape(edited, current, "mvp-02-automotive-ecu.yaml")
    # A renamed engine field does not.
    renamed = json.loads(json.dumps(current))
    renamed["graph"]["nodes"][0]["type"] = renamed["graph"]["nodes"][0].pop("domain_type")
    with pytest.raises(AssertionError, match="response shape changed"):
        assert_same_shape(renamed, current, "mvp-02-automotive-ecu.yaml")
