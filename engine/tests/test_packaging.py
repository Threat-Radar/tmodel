"""Opt-in checks of the real PyInstaller executable, including runtime cleanup.

TMODEL_PACKAGED_ENGINE=/absolute/path/to/tmodel-engine pytest tests/test_packaging.py
The normal engine suite skips these until a sidecar has been built.
"""

import json
import os
import selectors
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

PACKAGED_ENGINE = os.environ.get("TMODEL_PACKAGED_ENGINE")
pytestmark = pytest.mark.skipif(not PACKAGED_ENGINE, reason="build the packaged engine first")
MODEL = Path(__file__).resolve().parents[2] / "spec/vectors/mvp-01-software-doc-service.yaml"


def engine_url(proc):
    with selectors.DefaultSelector() as selector:
        selector.register(proc.stdout, selectors.EVENT_READ)
        assert selector.select(timeout=60), "engine did not start"
    line = proc.stdout.readline().decode().strip()
    assert "listening on http://127.0.0.1:" in line, line
    return line.rsplit(" ", 1)[1]


def get_json(base, endpoint, **query):
    url = f"{base}/{endpoint}?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.load(response)


@pytest.mark.parametrize(
    ("filename", "goal", "review_status"),
    [
        ("mvp-01-software-doc-service.yaml", "threat-instance:imds-pivot", "changes_requested"),
        ("mvp-02-automotive-ecu.yaml", "threat-instance:infotainment-pivot", "rejected"),
    ],
)
def test_relocated_engine_serves_bundled_graph_without_checkout(
    tmp_path, filename, goal, review_status
):
    # Only the executable is copied. No source models, Python, PATH or source
    # checkout is supplied to the process, matching a downloaded installation.
    executable = tmp_path / "tmodel-engine"
    shutil.copy2(PACKAGED_ENGINE, executable)
    proc = subprocess.Popen(
        [str(executable), "serve", "--port", "0", "--exit-with-parent"],
        cwd=tmp_path,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"HOME": str(tmp_path), "TMPDIR": str(tmp_path)},
    )
    try:
        base = engine_url(proc)
        assert get_json(base, "health")["status"] == "ok"
        graph = get_json(base, "graph", file=filename)
        model = Path(graph["file"])
        assert model.name == filename
        assert model.is_relative_to(tmp_path.resolve())
        assert "_MEI" in str(model)
        assert graph["nodes"] and graph["edges"]
        if filename == MODEL.name:
            assert (len(graph["nodes"]), len(graph["edges"])) == (42, 69)
        # The GUI passes /graph's resolved filename back to /attack-paths.
        paths = get_json(base, "attack-paths", file=str(model), goal=goal)["paths"]
        assert len(paths) == 2
        assert all(p["review"]["review_status"] == review_status for p in paths)
        assert all(not p["review"]["reviewed"] for p in paths)
        if filename == "mvp-02-automotive-ecu.yaml":
            risk = get_json(
                base,
                "risk",
                file=str(model),
                goal="threat-instance:remote-diag-injection",
                matrix="annex-h-table-h8",
            )["assessments"][0]
            assert risk["complete"]
            assert risk["derived_risk"] == {
                "safety": 5,
                "financial": 4,
                "operational": 5,
                "privacy": 1,
            }
            assert risk["mitigation_status"] == "in_progress"
            tara = get_json(base, "tara", file=str(model), matrix="annex-h-table-h8")
            assert tara["source"] == {"file": filename, "example_data": True}
            assert len(tara["records"]["assets"]) == 2
            rejected = next(
                p
                for p in tara["records"]["attack_paths"]
                if p["id"] == "attack-path:infotainment-pivot"
            )
            assert rejected["review_state"]["status"] == "rejected"
            assert not rejected["review_state"]["reviewed"]
        for outside in (str(MODEL), "../outside.yaml"):
            with pytest.raises(urllib.error.HTTPError) as error:
                get_json(base, "graph", file=outside)
            assert error.value.code == 400
            assert json.load(error.value)["error"] == "file: outside approved model directory"
    finally:
        proc.stdin.close()
        try:
            assert proc.wait(timeout=60) == 0, proc.stderr.read().decode()
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()
    assert not list(tmp_path.glob("_MEI*"))


def test_bundled_engine_reads_model_without_system_python(tmp_path):
    result = subprocess.run(
        [
            PACKAGED_ENGINE,
            "paths",
            str(MODEL),
            "--goal",
            "threat-instance:imds-pivot",
            "--in-process",
            "--json",
        ],
        env={"HOME": str(tmp_path), "TMPDIR": str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    paths = json.loads(result.stdout)["paths"]
    assert len(paths) == 2
    assert all(p["goal_step"] == "attack-step:fetch-instance-credentials" for p in paths)
    assert not list(tmp_path.glob("_MEI*"))


@pytest.mark.parametrize("close_before_ready", [False, True])
def test_bundled_engine_cleans_runtime_on_stdin_close(tmp_path, close_before_ready):
    # Three restarts catch a launcher that exits but leaks one runtime each time.
    for _ in range(3):
        proc = subprocess.Popen(
            [PACKAGED_ENGINE, "serve", "--port", "0", "--exit-with-parent"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"HOME": str(tmp_path), "TMPDIR": str(tmp_path)},
        )
        try:
            if not close_before_ready:
                # A bounded request also prevents hanging the test if startup fails.
                engine_url(proc)
                assert list(tmp_path.glob("_MEI*")), "one-file runtime was not exercised"
            proc.stdin.close()
            assert proc.wait(timeout=60) == 0, proc.stderr.read().decode()
            assert not list(tmp_path.glob("_MEI*"))
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()
