"""Library records through core, the local API and the CLI (#140: parity, errors, filters).

Most tests point the engine at the fixture library (`fixtures/library/`, 12 real
records) through TMODEL_LIBRARY. The last one reads the pinned submodule and skips
when it is not checked out, as in CI.
"""

import json
import shutil
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from engine import core
from engine.api.server import make_server
from engine.cli import main
from engine.load import library as library_module

TESTS = Path(__file__).resolve().parent
FIXTURES = TESTS / "fixtures" / "library"
PINNED = TESTS.parents[1] / "library"

# filters -> the record ids the fixture library should answer, checked by hand
EXPECTED = [
    ({}, None),  # None: all 12
    ({"type": "rfc"}, ["rfc-8152", "rfc-8785", "rfc-9393"]),
    (
        {"status": "stub"},
        ["benedetti-2024-sbom-python", "ecma-424", "rfc-9393", "sbomproof-2025"],
    ),
    (
        {"topic": "product-composition"},
        ["benedetti-2024-sbom-python", "rfc-9393", "sbomproof-2025"],
    ),
    ({"type": "paper", "status": "stub"}, ["benedetti-2024-sbom-python", "sbomproof-2025"]),
    ({"topic": "supply-chain-attestation", "status": "summarized"}, ["eo-14306"]),
    ({"type": "book"}, []),
]


@pytest.fixture(autouse=True)
def fixture_library(monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(FIXTURES))


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def api(base, query=""):
    with urllib.request.urlopen(f"{base}/library?{query}", timeout=30) as resp:
        return resp.status, json.loads(resp.read())


def api_error(base, query):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(base, query)
    return err.value.code, json.loads(err.value.read())


def ids(payload):
    return [r["id"] for r in payload["records"]]


def cli_json(capsys, *args):
    code = main(["library", *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def flags(filters):
    return [part for name, value in filters.items() for part in (f"--{name}", value)]


# --- the engine operation (core) ---------------------------------------------


@pytest.mark.parametrize("filters, expected", EXPECTED)
def test_core_filters(filters, expected):
    out = core.library_records(filters)
    assert out["filters"] == filters
    assert out["library"]["count"] == 12
    assert out["library"]["problems"] == []
    assert ids(out) == (expected if expected is not None else sorted(ids(out)))
    assert out["count"] == len(out["records"]) == (12 if expected is None else len(expected))


def test_core_records_are_the_loaders_records():
    out = core.library_records({"type": "rfc"})
    rfc = out["records"][1]
    assert rfc["id"] == "rfc-8785"
    assert rfc["identifiers"]["rfc"] == "8785"
    assert rfc["profile"] == "full"
    assert out["library"]["root"] == str(FIXTURES.resolve())


@pytest.mark.parametrize(
    "filters, message",
    [
        ({"kind": "rfc"}, "unknown filter 'kind': use type, topic or status"),
        ({"type": ""}, "filter 'type' needs a value"),
        ({"status": "   "}, "filter 'status' needs a value"),
    ],
)
def test_core_rejects_bad_filters(filters, message):
    with pytest.raises(ValueError, match=message):
        core.library_records(filters)


def test_core_strips_filter_values():
    assert ids(core.library_records({"type": " rfc "})) == ["rfc-8152", "rfc-8785", "rfc-9393"]


def test_core_without_a_library_is_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path))
    with pytest.raises(core.Unavailable, match="no library at .*TMODEL_LIBRARY"):
        core.library_records()


# --- local API -----------------------------------------------------------------


@pytest.mark.parametrize("filters, expected", EXPECTED)
def test_api_matches_core(engine_url, filters, expected):
    status, body = api(engine_url, urllib.parse.urlencode(filters))
    assert status == 200
    assert body == core.library_records(filters)


@pytest.mark.parametrize(
    "query, message",
    [
        ("kind=rfc", "unknown filter 'kind'"),
        ("type=", "filter 'type' needs a value"),
        ("type=rfc&color=red", "unknown filter 'color'"),
    ],
)
def test_api_bad_input_is_400_with_a_message(engine_url, query, message):
    code, body = api_error(engine_url, query)
    assert code == 400
    assert message in body["error"]


def test_api_without_a_library_is_503(engine_url, monkeypatch, tmp_path):
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path))
    code, body = api_error(engine_url, "")
    assert code == 503
    assert body["error"].startswith(f"no library at {tmp_path}")
    assert "git submodule update --init library" in body["error"]


def test_api_serves_what_loaded_and_lists_what_did_not(engine_url, monkeypatch, tmp_path):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    broken = tmp_path / "lib" / "records" / "ietf" / "broken" / "record.yaml"
    broken.parent.mkdir()
    broken.write_text("id: broken\n", encoding="utf-8")
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path / "lib"))
    status, body = api(engine_url)
    assert status == 200
    assert body["count"] == body["library"]["count"] == 12
    (problem,) = body["library"]["problems"]
    assert problem.startswith("records/ietf/broken/record.yaml: missing required fields")


def test_api_cors_for_the_desktop_app(engine_url):
    req = urllib.request.Request(f"{engine_url}/library", headers={"Origin": "tauri://localhost"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        assert resp.headers.get("Access-Control-Allow-Origin") == "tauri://localhost"


# --- CLI -----------------------------------------------------------------------


@pytest.mark.parametrize("filters, expected", EXPECTED)
def test_cli_in_process_and_api_match_core(engine_url, capsys, filters, expected):
    code, in_process = cli_json(capsys, *flags(filters), "--in-process")
    assert code == 0
    code, via_api = cli_json(capsys, *flags(filters), "--url", engine_url)
    assert code == 0
    assert in_process == via_api == core.library_records(filters)


def test_cli_human_output(engine_url, capsys):
    assert main(["library", "--type", "rfc", "--url", engine_url]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"3 of 12 records in {FIXTURES.resolve()}"
    assert lines[1].split() == ["rfc-8152", "rfc", "fetched", *lines[1].split()[3:]]
    assert [line.split()[0] for line in lines[1:]] == ["rfc-8152", "rfc-8785", "rfc-9393"]


def test_cli_bad_filter_is_an_error(capsys):
    assert main(["library", "--type", "", "--in-process"]) == 1
    assert capsys.readouterr().err.strip() == "error: filter 'type' needs a value"


def test_cli_without_a_library(engine_url, capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path))
    for transport in (["--in-process"], ["--url", engine_url]):
        assert main(["library", *transport]) == 1
        assert capsys.readouterr().err.startswith(f"error: no library at {tmp_path}")


def test_cli_warns_when_records_failed(capsys, monkeypatch, tmp_path):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    (tmp_path / "lib" / "records" / "ietf" / "rfc-8785" / "record.yaml").write_text(
        "- not a mapping\n", encoding="utf-8"
    )
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path / "lib"))
    assert main(["library", "--in-process"]) == 1
    captured = capsys.readouterr()
    assert captured.out.startswith("11 of 11 records in")
    assert captured.err.strip() == "warning: 1 library record failed to load; --json lists them"


# --- loading once, and again only after a change --------------------------------


def test_the_library_is_loaded_once_until_a_file_changes(monkeypatch, tmp_path):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path / "lib"))
    loads = []
    real = library_module.load_library
    monkeypatch.setattr(
        library_module, "load_library", lambda *a, **k: loads.append(1) or real(*a, **k)
    )
    first = core.library_records()
    assert core.library_records() == first
    assert len(loads) == 1
    record = tmp_path / "lib" / "records" / "other" / "cwe" / "record.yaml"
    record.write_text(record.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    second = core.library_records()
    assert len(loads) == 2
    assert second["library"]["digest"] != first["library"]["digest"]
    shutil.rmtree(tmp_path / "lib" / "records" / "other" / "cwe")
    assert core.library_records()["library"]["count"] == 11
    assert len(loads) == 3


# --- the pinned library, by default -----------------------------------------------


@pytest.mark.skipif(
    not (PINNED / "records").is_dir(),
    reason="library submodule not checked out (git submodule update --init library)",
)
def test_default_library_is_the_pinned_submodule(monkeypatch):
    monkeypatch.delenv("TMODEL_LIBRARY")
    out = core.library_records({"type": "rfc"})
    assert out["library"]["root"] == str(PINNED.resolve())
    assert out["library"]["problems"] == []
    assert out["count"] > 0
    assert {r["type"] for r in out["records"]} == {"rfc"}
