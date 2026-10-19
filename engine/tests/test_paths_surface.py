"""Attack paths through the local API and the CLI (#63: façade, API, CLI parity)."""

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from engine import core
from engine.api.server import make_server
from engine.cli import main

MVP01 = str(
    Path(__file__).resolve().parents[2] / "spec" / "vectors" / "mvp-01-software-doc-service.yaml"
)
IMDS = "threat-instance:imds-pivot"


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def api(base, **params):
    url = f"{base}/attack-paths?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, json.loads(resp.read())


def api_error(base, **params):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(base, **params)
    return err.value.code, json.loads(err.value.read())


# --- the engine operation (core) ---------------------------------------------


def test_core_lists_threats_without_goal():
    out = core.attack_paths(MVP01)
    assert out["threats"] == [IMDS, "threat-instance:xxe-file-read"]
    assert out["steps"] == 7


def test_core_paths_for_goal():
    out = core.attack_paths(MVP01, IMDS)
    assert out["goal"] == IMDS
    assert [p["steps"] for p in out["paths"]] == [
        ["attack-step:point-entity-at-metadata", "attack-step:fetch-instance-credentials"],
        ["attack-step:dns-rebind-to-metadata", "attack-step:fetch-instance-credentials"],
    ]


# --- local API ---------------------------------------------------------------


def test_api_paths_for_goal(engine_url):
    status, body = api(engine_url, file=MVP01, goal=IMDS)
    assert status == 200
    assert body == core.attack_paths(MVP01, IMDS)


def test_api_lists_threats_without_goal(engine_url):
    status, body = api(engine_url, file=MVP01)
    assert status == 200
    assert IMDS in body["threats"]


def test_api_missing_file_param_is_400(engine_url):
    code, body = api_error(engine_url, goal=IMDS)
    assert code == 400
    assert "missing query parameter: file" in body["error"]


def test_api_unknown_goal_is_400(engine_url):
    code, body = api_error(engine_url, file=MVP01, goal="threat-instance:nope")
    assert code == 400
    assert "unknown goal" in body["error"]


def test_api_rejects_non_yaml_file(engine_url):
    code, body = api_error(engine_url, file="/etc/hosts")
    assert code == 400
    assert ".yaml or .yml" in body["error"]


def test_api_missing_file_is_400(engine_url, tmp_path):
    code, body = api_error(engine_url, file=str(tmp_path / "absent.yaml"))
    assert code == 400
    assert "cannot read" in body["error"]


def test_api_cors_on_paths_for_tauri_origin(engine_url):
    url = f"{engine_url}/attack-paths?" + urllib.parse.urlencode({"file": MVP01})
    req = urllib.request.Request(url, headers={"Origin": "tauri://localhost"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.headers.get("Access-Control-Allow-Origin") == "tauri://localhost"


# --- CLI ---------------------------------------------------------------------


def test_cli_paths_human_output(engine_url, capsys):
    assert main(["paths", MVP01, "--goal", IMDS, "--url", engine_url]) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"{IMDS}: 2 paths",
        "  1. point-entity-at-metadata -> fetch-instance-credentials",
        "  2. dns-rebind-to-metadata -> fetch-instance-credentials",
    ]


def test_cli_lists_threats(engine_url, capsys):
    assert main(["paths", MVP01, "--url", engine_url]) == 0
    out = capsys.readouterr().out
    assert "7 steps; threats:" in out
    assert f"  {IMDS}" in out


@pytest.mark.parametrize("goal", [None, IMDS, "threat-instance:xxe-file-read"])
def test_cli_api_and_in_process_give_same_answer(engine_url, capsys, goal):
    extra = ["--goal", goal] if goal else []
    assert main(["paths", MVP01, *extra, "--json", "--url", engine_url]) == 0
    via_api = json.loads(capsys.readouterr().out)
    assert main(["paths", MVP01, *extra, "--json", "--in-process"]) == 0
    assert json.loads(capsys.readouterr().out) == via_api


def test_cli_relative_file_is_resolved(engine_url, capsys, monkeypatch):
    monkeypatch.chdir(Path(MVP01).parent)
    assert main(["paths", Path(MVP01).name, "--json", "--url", engine_url]) == 0
    assert json.loads(capsys.readouterr().out)["file"] == MVP01


@pytest.mark.parametrize("transport", [["--in-process"], None])
def test_cli_unknown_goal_exits_1_with_message(engine_url, capsys, transport):
    transport = transport or ["--url", engine_url]
    assert main(["paths", MVP01, "--goal", "nope", *transport]) == 1
    assert "unknown goal: nope" in capsys.readouterr().err


def test_cli_paths_unreachable_engine_exits_1(capsys):
    assert main(["paths", MVP01, "--url", "http://127.0.0.1:9"]) == 1
    assert "no tmodel engine" in capsys.readouterr().err
