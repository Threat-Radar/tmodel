"""Opt-in checks of the real PyInstaller executable, including runtime cleanup.

TMODEL_PACKAGED_ENGINE=/absolute/path/to/tmodel-engine pytest tests/test_packaging.py
The normal engine suite skips these until a sidecar has been built.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGED_ENGINE = os.environ.get("TMODEL_PACKAGED_ENGINE")
pytestmark = pytest.mark.skipif(not PACKAGED_ENGINE, reason="build the packaged engine first")
MODEL = Path(__file__).resolve().parents[2] / "spec/vectors/mvp-01-software-doc-service.yaml"


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
                import selectors

                with selectors.DefaultSelector() as selector:
                    selector.register(proc.stdout, selectors.EVENT_READ)
                    assert selector.select(timeout=60), "engine did not start"
                assert b"listening on http://127.0.0.1:" in proc.stdout.readline()
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
