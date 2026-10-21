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
        "  1. point-entity-at-metadata -> fetch-instance-credentials"
        "  [not reviewed: changes_requested]",
        "  2. dns-rebind-to-metadata -> fetch-instance-credentials"
        "  [not reviewed: changes_requested]",
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


# --- fixes from review on #132 ------------------------------------------------

VECTORS = Path(MVP01).parent


def reviews_of(file, goal):
    return [p["review"] for p in core.attack_paths(str(VECTORS / file), goal)["paths"]]


def test_review_state_is_carried_into_the_output():
    # accepted by a human
    assert reviews_of("mvp-01-software-doc-service.yaml", "threat-instance:xxe-file-read") == [
        {"reviewed": True, "assertion_status": "accepted", "review_status": "accepted"}
    ]
    # an AI hypothesis a human rejected: never shown as reviewed
    rejected = reviews_of("mvp-02-automotive-ecu.yaml", "threat-instance:infotainment-pivot")
    assert rejected and all(
        r == {"reviewed": False, "assertion_status": "proposed", "review_status": "rejected"}
        for r in rejected
    )
    # no review recorded for the path: not reviewed either
    unrecorded = reviews_of(
        "mvp-03-hierarchical-system.yaml", "threat-instance:gateway-default-creds"
    )
    assert unrecorded == [{"reviewed": False, "assertion_status": None, "review_status": None}]


def test_threat_list_marks_unreviewed_threats(capsys):
    out = core.attack_paths(MVP01)
    assert out["reviewed_threats"] == ["threat-instance:xxe-file-read"]
    assert main(["paths", MVP01, "--in-process"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert f"  {IMDS}  [not reviewed]" in lines
    assert "  threat-instance:xxe-file-read" in lines


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("attack_steps: [{name: x}]\n", "expected a mapping with a string id"),
        ("attack_steps: {a: 1}\n", "attack_steps: expected a list"),
        ("attack_steps: [{id: a, precedes: b}]\n", "precedes must be a list of ids"),
        ("attack_steps: [{id: 100}]\n", "quote numeric ids"),
        ("attack_paths: [{id: p, steps: [], realizes_threat: t}]\n", "lists no steps"),
        ("updated: 2026-02-30\n", "not valid YAML"),
    ],
)
def test_malformed_files_are_400s_with_the_file_name(engine_url, tmp_path, text, message):
    bad = tmp_path / "bad.yaml"
    bad.write_text(text, encoding="utf-8")
    code, body = api_error(engine_url, file=str(bad))
    assert code == 400
    assert message in body["error"] and str(bad) in body["error"]


def test_non_utf8_file_is_a_400(engine_url, tmp_path):
    bad = tmp_path / "latin1.yaml"
    bad.write_bytes(b"name: caf\xe9\n")
    code, body = api_error(engine_url, file=str(bad))
    assert (code, "not UTF-8" in body["error"]) == (400, True)


def test_alias_bomb_in_gate_gives_a_short_error(tmp_path):
    lines = ["l0: &l0 [x,x,x,x,x,x,x,x,x,x]"]
    lines += [f"l{i}: &l{i} [" + ",".join([f"*l{i - 1}"] * 10) + "]" for i in range(1, 7)]
    lines += ["attack_steps: [{id: s, gate: *l6}]"]
    bomb = tmp_path / "bomb.yaml"
    bomb.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError) as err:
        core.attack_paths(str(bomb))
    assert len(str(err.value)) < 300


def test_relative_file_is_a_400(engine_url):
    code, body = api_error(engine_url, file="mvp-01-software-doc-service.yaml")
    assert code == 400
    assert "absolute path" in body["error"]


def test_blank_goal_is_an_unknown_goal_both_ways(engine_url, capsys):
    assert main(["paths", MVP01, "--goal", "", "--url", engine_url]) == 1
    assert "unknown goal" in capsys.readouterr().err
    assert main(["paths", MVP01, "--goal", "", "--in-process"]) == 1
    assert "unknown goal" in capsys.readouterr().err


def test_foreign_host_header_is_403(engine_url):
    req = urllib.request.Request(f"{engine_url}/health", headers={"Host": "attacker.example"})
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(req, timeout=5)
    assert err.value.code == 403


def test_internal_error_is_a_json_500_not_a_dropped_connection(engine_url, monkeypatch):
    def boom(_file, _goal=None):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(core, "attack_paths", boom)
    code, body = api_error(engine_url, file=MVP01)
    assert code == 500
    assert body["error"] == "internal error: RuntimeError"


def test_health_on_a_wrong_url_is_one_error_line_not_a_traceback(engine_url, capsys):
    assert main(["health", "--url", f"{engine_url}/api"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: not found") and "Traceback" not in err


def test_slow_engine_is_reported_as_busy_not_missing(capsys, monkeypatch):
    import engine.cli as cli
    from engine.client import EngineTimeout

    def slow(*_a, **_k):
        raise EngineTimeout("the engine at http://x did not answer within 60 s")

    monkeypatch.setattr(cli, "get", slow)
    assert main(["paths", MVP01, "--url", "http://x"]) == 1
    err = capsys.readouterr().err
    assert "did not answer within 60 s" in err and "tmodel serve" not in err
