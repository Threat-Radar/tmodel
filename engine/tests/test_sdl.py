"""GET /sdl and `tmodel sdl`: the SDL program view (DL-0043; PROC-0002 rules)."""

import copy
import json
import os
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

from engine import cli, core, sdl
from engine.api.server import make_server

ROOT = Path(__file__).resolve().parents[2]
SDL_FILE = "sdl-01-tmodel-desktop.yaml"
DOC = yaml.safe_load((ROOT / "spec" / "vectors" / SDL_FILE).read_text(encoding="utf-8"))
XWALK = yaml.safe_load((ROOT / "spec" / "MAP-0001.yaml").read_text(encoding="utf-8"))


@pytest.fixture
def server():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.status, json.loads(resp.read())


def test_lists_sdl_models_only():
    models = core.sdl()["models"]
    assert [m["file"] for m in models] == [SDL_FILE]
    assert models[0]["programs"][0]["id"] == "security-program:tmodel-sdl"


def test_view_has_the_page_sections():
    view = core.sdl({"file": SDL_FILE})
    assert view["file"] == SDL_FILE
    assert view["program"]["name"]
    assert sum(len(p["items"]) for p in view["phases"]) == len(DOC["sdl_practices"])
    assert {s["id"] for s in view["sets"]} == {rs["id"] for rs in DOC["requirement_sources"]}
    assert view["nodes"] and view["threats"] and view["gaps"]
    assert "proposal until the sponsor reviews it" in view["proposal"]
    # Nothing in the example is reviewed, so every selection is waiting (PROC-0002).
    assert view["awaiting_review"]
    assert all(it["decision"]["state"] == "proposed" for p in view["phases"] for it in p["items"])


def test_view_names_no_local_path():
    assert str(ROOT) not in json.dumps(core.sdl({"file": SDL_FILE}))


def test_columns_come_from_the_crosswalk_records():
    cols = sdl.map_columns(DOC, XWALK)
    assert cols["requirement-source:ssdf-1-1"] == "ssdf"
    assert cols["requirement-source:slsa-1-2-build-l2"] == "slsa"


def test_decider_roles_match_the_page_manifest():
    manifest = yaml.safe_load((ROOT / "docs" / "publishing" / "sdl.yaml").read_text())
    for page in manifest["pages"]:
        assert tuple(page["required_reviewer_roles"]) == sdl.DECIDER_ROLES


@pytest.mark.parametrize(
    "query, message",
    [
        ({"file": "mvp-01-software-doc-service.yaml"}, "not an SDL model"),
        ({"file": "../../README.md"}, "outside approved model directory"),
        ({"file": SDL_FILE, "program": "security-program:nope"}, "not found"),
        ({"file": SDL_FILE, "bogus": "x"}, "unknown parameter"),
    ],
)
def test_bad_queries(query, message):
    with pytest.raises(ValueError, match=message):
        core.sdl(query)


def test_ai_review_is_refused():
    doc = copy.deepcopy(DOC)
    target = doc["assertions"][0]["id"]
    doc["reviews"] = [
        {
            "id": "review:x",
            "reviews": target,
            "reviewer": "party:drafting-agent",
            "review_status": "accepted",
        }
    ]
    with pytest.raises(sdl.SdlError, match="not a person"):
        sdl.collect(doc, XWALK)


def test_route(server):
    status, body = fetch(f"{server}/sdl")
    assert status == 200 and body["models"][0]["file"] == SDL_FILE
    status, body = fetch(f"{server}/sdl?file={SDL_FILE}")
    assert status == 200 and body["phases"]
    with pytest.raises(urllib.error.HTTPError) as err:
        fetch(f"{server}/sdl?file=mvp-01-software-doc-service.yaml")
    assert err.value.code == 400


def test_cli_in_process(capsys):
    assert cli.main(["sdl", SDL_FILE, "--in-process"]) == 0
    assert "awaiting human review" in capsys.readouterr().out
    assert cli.main(["sdl", "--in-process", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["models"]


GUI_FIXTURE = ROOT / "apps" / "desktop" / "src" / "fixtures" / "sdl-01-view.json"


def test_gui_fixture_matches_the_engine():
    """apps/desktop/src/fixtures/sdl-01-view.json is the engine's answer (DL-0043)."""
    view = core.sdl({"file": SDL_FILE})
    text = json.dumps(view, indent=1, sort_keys=True) + "\n"
    if os.environ.get("TMODEL_UPDATE_FIXTURES"):
        GUI_FIXTURE.write_text(text, encoding="utf-8")
    assert GUI_FIXTURE.read_text(encoding="utf-8") == text
