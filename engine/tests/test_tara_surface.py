"""Repeatable export bytes, transport parity, and a read-only local API."""

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
from engine.cli import main
from engine.graph import GraphError
from engine.risk import MATRIX_ID
from engine.tara import serialize

MODEL = "mvp-02-automotive-ecu.yaml"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def engine_url():
    httpd = make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


def api(base, **params):
    url = f"{base}/tara?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)


def test_api_and_both_cli_transports_emit_the_same_collection(engine_url, capsys, tmp_path):
    expected = core.collect_tara(MODEL, MATRIX_ID)
    assert api(engine_url, file=MODEL, matrix=MATRIX_ID) == expected
    for transport in (["--in-process"], ["--url", engine_url]):
        args = ["tara", MODEL, "--matrix", MATRIX_ID, "--json", *transport]
        assert main(args) == 0  # a draft with incomplete risk is a valid collection
        assert capsys.readouterr().out == serialize(expected)
        path = tmp_path / "tara.json"
        assert main([*args, "--output", str(path)]) == 0
        assert path.read_text() == serialize(expected)
        assert not capsys.readouterr().out


def test_two_processes_with_different_hash_seeds_write_identical_files(tmp_path):
    outputs = []
    for seed in ["1", "91"]:
        path = tmp_path / f"tara-{seed}.json"
        env = {**os.environ, "PYTHONPATH": str(ROOT / "engine"), "PYTHONHASHSEED": seed}
        subprocess.run(
            [
                sys.executable,
                "-m",
                "engine",
                "tara",
                MODEL,
                "--matrix",
                MATRIX_ID,
                "--in-process",
                "--output",
                str(path),
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        outputs.append(path.read_bytes())
    assert outputs[0] == outputs[1]
    assert str(ROOT).encode() not in outputs[0]
    assert json.loads(outputs[0])["source"]["file"] == MODEL


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"file": MODEL},
        {"file": MODEL, "matrix": "cvss"},
        {"file": "../outside.yaml", "matrix": MATRIX_ID},
        {"file": MODEL, "matrix": MATRIX_ID, "output": "/tmp/must-not-write.json"},
    ],
)
def test_bad_api_queries_are_400_and_cannot_request_a_file_write(engine_url, params):
    with pytest.raises(urllib.error.HTTPError) as error:
        api(engine_url, **params)
    assert error.value.code == 400


def test_core_confinement_including_symlinks(tmp_path, monkeypatch):
    root = tmp_path / "vectors"
    root.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text("products: []\n")
    (root / "link.yaml").symlink_to(outside)
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", root)
    for name in (str(outside), "../outside.yaml", "link.yaml"):
        with pytest.raises(GraphError, match="outside approved"):
            core.collect_tara(name, MATRIX_ID)


def test_invalid_input_leaves_previous_export_untouched(tmp_path, capsys):
    path = tmp_path / "tara.json"
    path.write_text("previous export\n")
    assert (
        main(
            [
                "tara",
                MODEL,
                "--matrix",
                "bad-profile",
                "--in-process",
                "--output",
                str(path),
            ]
        )
        == 1
    )
    assert path.read_text() == "previous export\n"
    assert "error:" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == [path]


def test_output_errors_are_reported_and_input_cannot_be_overwritten(tmp_path, capsys):
    model = ROOT / "spec" / "vectors" / MODEL
    before = model.read_bytes()
    assert (
        main(
            [
                "tara",
                str(model),
                "--matrix",
                MATRIX_ID,
                "--in-process",
                "--output",
                str(model),
            ]
        )
        == 1
    )
    assert model.read_bytes() == before
    output = tmp_path / "missing-directory" / "tara.json"
    assert (
        main(
            [
                "tara",
                MODEL,
                "--matrix",
                MATRIX_ID,
                "--in-process",
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert not output.exists()
    assert "error:" in capsys.readouterr().err


def test_matrix_selection_is_required():
    with pytest.raises(SystemExit) as error:
        main(["tara", MODEL])
    assert error.value.code == 2
