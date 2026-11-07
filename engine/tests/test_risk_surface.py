"""Risk façade/API/CLI parity, incomplete-data behavior and file confinement."""

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
from engine.graph import GraphError
from engine.risk import MATRIX_ID

MODEL = "mvp-02-automotive-ecu.yaml"
GOAL = "threat-instance:remote-diag-injection"


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


def api(base, **params):
    url = f"{base}/risk?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)


def test_real_example_retains_inputs_and_computes_table_values():
    out = core.risk_assessments(MODEL, MATRIX_ID, GOAL)
    assert out["count"] == 1
    row = out["assessments"][0]
    assert row["complete"]
    assert row["feasibility"] == "high"
    assert row["impact"]["safety"] == "severe"
    assert row["derived_risk"] == {"safety": 5, "financial": 4, "operational": 5, "privacy": 1}
    assert row["mitigation_status"] == "in_progress"
    # Preserve the authored prose separately from the numeric calculation.
    assert "safety 5" in row["recorded"]["risk"]


def test_api_cli_and_in_process_are_identical(engine_url, capsys):
    expected = core.risk_assessments(MODEL, MATRIX_ID, GOAL)
    assert api(engine_url, file=MODEL, matrix=MATRIX_ID, goal=GOAL) == expected
    args = ["risk", MODEL, "--matrix", MATRIX_ID, "--goal", GOAL, "--json"]
    assert main([*args, "--in-process"]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    assert main([*args, "--url", engine_url]) == 0
    assert json.loads(capsys.readouterr().out) == expected


def test_incomplete_or_path_emits_json_and_nonzero_exit(capsys):
    assert main(["risk", MODEL, "--matrix", MATRIX_ID, "--json", "--in-process"]) == 1
    out = json.loads(capsys.readouterr().out)
    pivot = next(row for row in out["assessments"] if row["threat"].endswith("infotainment-pivot"))
    assert not pivot["complete"]
    assert len(pivot["paths"][0]["alternatives"]) == 2
    assert pivot["derived_risk"]["safety"] is None


def test_text_shows_the_vector_and_peer_status(capsys):
    assert main(["risk", MODEL, "--matrix", MATRIX_ID, "--goal", GOAL, "--in-process"]) == 0
    out = capsys.readouterr().out
    assert "safety: impact severe; risk 5" in out
    assert "feasibility: high" in out
    assert "mitigation status: in_progress" in out


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"file": MODEL},
        {"file": MODEL, "matrix": "cvss"},
        {"file": MODEL, "matrix": MATRIX_ID, "goal": "threat:absent"},
        {"file": "../outside.yaml", "matrix": MATRIX_ID},
    ],
)
def test_invalid_api_requests_are_400(engine_url, params):
    with pytest.raises(urllib.error.HTTPError) as error:
        api(engine_url, **params)
    assert error.value.code == 400
    assert "error" in json.load(error.value)


def test_file_confinement_including_symlinks(tmp_path, monkeypatch):
    root = tmp_path / "vectors"
    root.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text("threat_instances: []\n")
    (root / "link.yaml").symlink_to(outside)
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", root)
    for name in (str(outside), "../outside.yaml", "link.yaml"):
        with pytest.raises(GraphError, match="outside approved"):
            core.risk_assessments(name, MATRIX_ID)


def test_cli_relative_path_resolves_from_callers_directory(capsys):
    file = Path(__file__).resolve().parents[2] / "spec" / "vectors" / MODEL
    assert (
        main(["risk", str(file), "--matrix", MATRIX_ID, "--goal", GOAL, "--json", "--in-process"])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["file"] == MODEL


def test_cli_requires_explicit_matrix():
    with pytest.raises(SystemExit) as error:
        main(["risk", MODEL])
    assert error.value.code == 2
