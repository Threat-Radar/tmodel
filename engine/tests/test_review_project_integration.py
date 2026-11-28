"""C7 against the production workspace, HTTP configuration and real YAML files."""

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from urllib.parse import urlencode

import pytest
import yaml
from test_workspace_api import call
from workspace_support import EXAMPLE, EXAMPLES, TOKEN, fail_at, snapshot

from engine.api.server import make_desktop_server
from engine.cli import main
from engine.risk import MATRIX_ID

IDENTITY = f"party:local:{'2' * 32}:{os.getuid()}"


@contextmanager
def running(**options):
    httpd = make_desktop_server(port=0, host_token=TOKEN, reviewer_identity=IDENTITY, **options)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def project(url, folder, source):
    status, _, opened = call(url, "/workspace/host/open-file", "POST", {"path": str(source)})
    assert status == 200, opened
    # A loose model can be shown before it contains this host's reviewer Party.
    loose = {"model_id": opened["model_id"], "revision": opened["revision"], "matrix": MATRIX_ID}
    status, _, view = call(url, "/reviews/refresh", "POST", loose)
    assert status == 200, view
    assert view["report_data"]["model"]["kind_label"] == "Read-only local model"
    status, _, created = call(
        url,
        "/workspace/host/create-project",
        "POST",
        {"path": str(folder), "model_id": opened["model_id"]},
    )
    assert status == 201, created
    return created["model_id"]


def selection(url, model_id, revision="v001"):
    base = {"model_id": model_id, "revision": revision, "matrix": MATRIX_ID}
    status, _, views = call(url, "/reviews/refresh", "POST", base)
    assert status == 200, views
    assessment = views["risk"]["assessments"][0]
    return {
        **base,
        "threat_id": assessment["threat"],
        "route_id": assessment["routes"][0]["id"],
    }


def changes(context, verdict="accepted"):
    context = {**context, "expected_revision": context["revision"]}
    del context["revision"]
    return {
        **context,
        "description": "Synthetic review and rating test",
        "reviews": [
            {
                "assertion_id": "assertion:example-path",
                "verdict": verdict,
                "rationale": "Synthetic test input, not project human acceptance.",
                "annotation": "Test annotation",
            }
        ],
        "feasibility": [{"attack_path_id": "attack-path:example", "rating": "high"}],
        "impacts": [
            {
                "risk_score_id": "risk-score:example",
                "damage_scenario_id": "damage-scenario:example",
                "stakeholder_id": "party:example-reviewer",
                "values": {"safety": "severe"},
            }
        ],
    }


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "source.yaml"
    path.write_bytes((EXAMPLES / EXAMPLE).read_bytes())
    return path


def test_review_rating_save_history_and_reopen_use_real_versions(tmp_path, source):
    folder = tmp_path / "Review project"
    original = source.read_bytes()
    with running() as url:
        model_id = project(url, folder, source)
        selected = selection(url, model_id)
        status, _, context = call(url, "/reviews/context", "POST", selected)
        assert status == 200 and context["reviewer_id"] == IDENTITY
        assert context["permitted_actions"]["submit_review"]
        assert not context["permitted_actions"]["accept_proposal"]
        payload = changes(selected)
        status, _, saved = call(
            url, "/reviews/changes", "POST", payload, headers={"Origin": "tauri://localhost"}
        )
        assert status == 200, saved
        assert saved["revision"] == "v002"
        for name in ("report_data", "graph", "attack_paths", "risk"):
            assert saved[name]["revision"] == "v002"
            assert saved[name]["model_id"] == model_id
        assert saved["risk"]["assessments"][0]["derived_risk"] == {
            "safety": 5,
            "financial": 4,
            "operational": 3,
            "privacy": 1,
        }
        version2 = (folder / "versions/v002.yaml").read_bytes()
        document = yaml.safe_load(version2)
        assert document["reviews"][0]["reviewer"] == IDENTITY
        assert document["assertions"] == yaml.safe_load(original)["assertions"]
        metadata = json.loads((folder / "project.json").read_text())["versions"][-1]
        assert metadata["description"] == payload["description"]
        assert metadata["summary"]["incomplete"] == 0
        assert (
            metadata["summary"]["derived_risk"] == saved["risk"]["assessments"][0]["derived_risk"]
        )

        corrected = changes(selection(url, model_id, "v002"), "rejected")
        corrected["reviews"][0]["review_id"] = document["reviews"][0]["id"]
        assert call(url, "/reviews/changes", "POST", corrected)[0] == 200
        assert (folder / "versions/v002.yaml").read_bytes() == version2
        assert (folder / "versions/v001.yaml").read_bytes() == original
        assert (folder / "original.yaml").read_bytes() == source.read_bytes() == original
        before = snapshot(folder)
        status, _, conflict = call(url, "/reviews/changes", "POST", payload)
        assert status == 409 and conflict["error"]["current_revision"] == "v003"
        assert snapshot(folder) == before

    with running() as restarted:
        assert call(restarted, "/reviews/refresh", "POST", selected)[0] == 403
        status, _, opened = call(
            restarted, "/workspace/host/open-project", "POST", {"path": str(folder)}
        )
        assert status == 200 and opened["model_id"] == model_id
        status, _, views = call(
            restarted, "/reviews/refresh", "POST", {**selected, "revision": "v002"}
        )
        assert status == 200 and views == saved
        status, _, context = call(
            restarted, "/reviews/context", "POST", {**selected, "revision": "v003"}
        )
        assert status == 200
        assert [
            (item["revision"], item["review"]["review_status"]) for item in context["history"]
        ] == [
            ("v002", "accepted"),
            ("v003", "rejected"),
        ]
        assert context["assertions"][0]["assertion_status"] == "proposed"


@pytest.mark.parametrize("description", ["x" * 501, " "])
def test_invalid_version_description_writes_nothing(tmp_path, source, description):
    folder = tmp_path / "Description test"
    with running() as url:
        model_id = project(url, folder, source)
        payload = changes(selection(url, model_id))
        payload["description"] = description
        before = snapshot(folder)
        status, _, error = call(url, "/reviews/changes", "POST", payload)
        assert status == 422 and error["error"]["fields"][0]["field"] == "description"
        assert snapshot(folder) == before


def test_production_save_failure_preserves_yaml_and_metadata(tmp_path, source, monkeypatch):
    folder = tmp_path / "Failure test"
    with running() as url:
        model_id = project(url, folder, source)
        payload = changes(selection(url, model_id))
        before = snapshot(folder)
        fail_at(monkeypatch, "_replace", 1, "private-path-and-token")
        status, _, error = call(url, "/reviews/changes", "POST", payload)
        assert status == 503 and error["error"]["code"] == "save_failure"
        assert "private-path-and-token" not in json.dumps(error)
        assert snapshot(folder) == before


def test_two_http_review_saves_have_one_winner(tmp_path, source):
    folder = tmp_path / "Concurrent test"
    with running() as url:
        model_id = project(url, folder, source)
        payload = changes(selection(url, model_id))
        with ThreadPoolExecutor(max_workers=2) as pool:
            answers = list(
                pool.map(lambda _: call(url, "/reviews/changes", "POST", payload), range(2))
            )
        assert sorted(answer[0] for answer in answers) == [200, 409]
        assert len(list((folder / "versions").glob("*.yaml"))) == 2
        assert len(yaml.safe_load((folder / "versions/v002.yaml").read_bytes())["reviews"]) == 1


def test_host_permissions_and_invalid_targets_do_not_write(tmp_path, source):
    folder = tmp_path / "Permission test"
    with running() as url:
        model_id = project(url, folder, source)
        payload = changes(selection(url, model_id))
        before = snapshot(folder)
        for headers, token in (({}, "wrong-token"), ({"Origin": "https://foreign.invalid"}, TOKEN)):
            assert (
                call(url, "/reviews/changes", "POST", payload, token=token, headers=headers)[0]
                == 403
            )
        bad = deepcopy(payload)
        bad["reviews"][0]["assertion_id"] = "assertion:unrelated"
        assert call(url, "/reviews/changes", "POST", bad)[0] == 422
        bad = {**payload, "reviewer_id": "party:example-reviewer"}
        assert call(url, "/reviews/changes", "POST", bad)[0] == 422
        assert snapshot(folder) == before
        status, _, versions = call(url, "/workspace/versions?" + urlencode({"model_id": model_id}))
        assert status == 200 and versions["current_revision"] == "v001"


def test_cli_uses_the_host_identity_only_when_projects_are_enabled(monkeypatch):
    from engine.api import server

    seen = {}
    monkeypatch.setattr(server, "serve", lambda **kwargs: seen.update(kwargs))
    monkeypatch.setenv("TMODEL_HOST_TOKEN", TOKEN)
    monkeypatch.setenv("TMODEL_REVIEWER_ID", IDENTITY)
    assert main(["serve"]) == 0 and seen["reviewer_identity"] is None
    assert main(["serve", "--projects"]) == 0 and seen["reviewer_identity"] == IDENTITY


def test_invalid_host_identity_fails_before_binding():
    with pytest.raises(ValueError, match="OS user"):
        make_desktop_server(port=0, host_token=TOKEN, reviewer_identity="party:claimed-sponsor")
    with pytest.raises(ValueError, match="workspace"):
        make_desktop_server(port=0, reviewer_identity=IDENTITY)
