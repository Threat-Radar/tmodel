"""Read-only general graph surface for Issue #59."""

import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from engine import core
from engine.api.server import make_server

MVP01 = (
    Path(__file__).resolve().parents[2] / "spec" / "vectors" / "mvp-01-software-doc-service.yaml"
)


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def api(base, **params):
    url = f"{base}/graph?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.status, json.loads(response.read())


def api_error(base, **params):
    with pytest.raises(urllib.error.HTTPError) as error:
        api(base, **params)
    return error.value.code, json.loads(error.value.read())


def test_graph_response_preserves_stable_ids_types_and_directions():
    result = core.model_graph(MVP01.name)
    nodes = {node["id"]: node for node in result["nodes"]}
    assert nodes["component:papermill-api"] == {
        "id": "component:papermill-api",
        "domain_type": "Component",
        "label": "papermill-api (service container)",
        "properties": {
            "description": (
                "The deployed service artifact (§0 authoritative component, not a DFD node)."
            ),
            "identifiers": ["pkg:oci/papermill/doc-service@sha256:3b9e1d2a"],
        },
    }
    edge = next(
        edge
        for edge in result["edges"]
        if edge["source"] == "component:papermill-api"
        and edge["relationship_type"] == "uses_component"
        and edge["target"] == "component:libxml-parse"
    )
    assert edge["id"] == (
        "relationship:component:papermill-api|uses_component|component:libxml-parse"
    )


def test_reviewed_assertion_is_projected_as_semantic_edge():
    result = core.model_graph(MVP01.name)
    edge = next(edge for edge in result["edges"] if edge["relationship_type"] == "instance_of")
    assert (edge["source"], edge["target"]) == (
        "vulnerability:cve-2026-30111",
        "weakness:cwe-611",
    )
    assert edge["properties"] == {
        "assertion_ids": ["assertion:cve-cwe-instance"],
        "assertion_status": "accepted",
        "confidence": "high",
        "review_ids": ["review:cve-cwe"],
        "review_status": "accepted",
    }


def test_proposed_assertion_keeps_its_review_verdict_on_the_edge():
    result = core.model_graph(MVP01.name)
    edge_id = "relationship:attack-path:imds-pivot|realizes_threat|threat-instance:imds-pivot"
    edge = next(edge for edge in result["edges"] if edge["id"] == edge_id)
    assert edge["properties"] == {
        "assertion_ids": ["assertion:ai-imds-pivot-realizes"],
        "assertion_status": "proposed",
        "confidence": "low",
        "review_ids": ["review:ai-triage"],
        "review_status": "changes_requested",
    }


def test_relationship_slots_are_projected_in_sorted_order():
    graph = core.project_model_graph(
        {
            "components": [
                {"id": "component:a", "uses_component": "component:c", "depends_on": "component:b"},
                {"id": "component:b"},
                {"id": "component:c", "composed_of": ["component:b"], "affects": "component:a"},
            ]
        }
    )
    assert [edge.id for edge in graph.edges] == [
        "relationship:component:a|depends_on|component:b",
        "relationship:component:a|uses_component|component:c",
        "relationship:component:c|affects|component:a",
        "relationship:component:c|composed_of|component:b",
    ]


def test_graph_edge_order_does_not_depend_on_string_hash_seed():
    script = (
        "import json; from engine import core; "
        f"print(json.dumps([edge['id'] for edge in core.model_graph({MVP01.name!r})['edges']]))"
    )
    engine_root = Path(__file__).resolve().parents[1]
    orders = set()
    for seed in ("1", "2", "3"):
        output = subprocess.run(
            [sys.executable, "-c", script],
            cwd=engine_root,
            env={**os.environ, "PYTHONHASHSEED": seed},
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        orders.add(output)
    assert len(orders) == 1


def test_api_accepts_basename_and_approved_absolute_path(engine_url):
    for file in (MVP01.name, str(MVP01)):
        status, body = api(engine_url, file=file)
        assert status == 200
        assert body["file"] == str(MVP01)
        assert body["nodes"] and body["edges"]


def test_api_missing_or_blank_file_is_a_clear_400(engine_url):
    code, body = api_error(engine_url)
    assert code == 400
    assert body["error"] == "missing query parameter: file"
    code, body = api_error(engine_url, file="")
    assert code == 400
    assert "expected a model filename" in body["error"]


@pytest.mark.parametrize("file", ["../schema/tmodel-object-model.linkml.yaml", "/etc/hosts"])
def test_api_rejects_paths_outside_the_approved_directory(engine_url, file):
    code, body = api_error(engine_url, file=file)
    assert code == 400
    assert "outside approved model directory" in body["error"]
    assert str(core.APPROVED_VECTOR_DIRECTORY.resolve()) not in body["error"]


def test_api_rejects_missing_and_non_yaml_files(engine_url):
    code, body = api_error(engine_url, file="absent.yaml")
    assert code == 400
    assert "cannot read" in body["error"]
    code, body = api_error(engine_url, file="README.md")
    assert code == 400
    assert ".yaml or .yml" in body["error"]


def test_api_rejects_a_schema_harness_as_not_a_model(engine_url):
    code, body = api_error(engine_url, file="example-container.linkml.yaml")
    assert code == 400
    assert "expected at least one model object" in body["error"]


def test_symlink_escape_is_rejected(engine_url, tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    approved.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text("attack_steps: []\n", encoding="utf-8")
    (approved / "escape.yaml").symlink_to(outside)
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", approved)

    code, body = api_error(engine_url, file="escape.yaml")
    assert code == 400
    assert "outside approved model directory" in body["error"]


def test_malformed_approved_model_is_a_400(engine_url, tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    approved.mkdir()
    malformed = approved / "bad.yaml"
    malformed.write_text("components: not-a-list\n", encoding="utf-8")
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", approved)

    code, body = api_error(engine_url, file=malformed.name)
    assert code == 400
    assert "components: expected a list" in body["error"]
    assert str(approved.resolve()) not in body["error"]
    assert str(malformed.resolve()) not in body["error"]


def test_graph_endpoint_is_cors_accessible_to_tauri(engine_url):
    url = f"{engine_url}/graph?" + urllib.parse.urlencode({"file": MVP01.name})
    request = urllib.request.Request(url, headers={"Origin": "tauri://localhost"})
    with urllib.request.urlopen(request, timeout=5) as response:
        assert response.headers.get("Access-Control-Allow-Origin") == "tauri://localhost"
