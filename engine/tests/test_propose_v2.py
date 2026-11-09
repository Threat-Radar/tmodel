"""Hook v2 (DL-0046): proposals for threat models, SDL models and saved KG views,
the read-only GET /proposals route, and `tmodel accept`, the sponsor's decision."""

import copy
import json
import shutil
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

import pytest
import yaml

from engine import accept as A
from engine import cli, core
from engine import propose as P
from engine.api import server

ROOT = Path(__file__).resolve().parents[2]
VECTORS = ROOT / "spec" / "vectors"
THREAT = "mvp-01-software-doc-service.yaml"
SDL = "sdl-01-tmodel-desktop.yaml"
FIXTURES = Path(__file__).parent / "fixtures"
PATCH = yaml.safe_load((FIXTURES / "threat-patch-example.yaml").read_text())
SDL_PATCH = yaml.safe_load((FIXTURES / "sdl-patch-example.yaml").read_text())
XWALK = yaml.safe_load((ROOT / "spec" / "MAP-0001.yaml").read_text())
TODAY = date(2026, 11, 7)


@pytest.fixture
def vectors(tmp_path, monkeypatch):
    """A copy of the approved model directory, so nothing in the repo is written."""
    d = tmp_path / "spec" / "vectors"
    shutil.copytree(VECTORS, d, ignore=shutil.ignore_patterns("proposals"))
    shutil.copy(ROOT / "spec" / "MAP-0001.yaml", tmp_path / "spec" / "MAP-0001.yaml")
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", d)
    monkeypatch.setattr(core, "CROSSWALK_FILE", tmp_path / "spec" / "MAP-0001.yaml")
    return d


def patch(**changes):
    p = copy.deepcopy(PATCH)
    p.update(changes)
    return p


def decide(vectors, name, pid, **kw):
    args = dict(
        verdict="accepted",
        reviewer="party:nymble",
        justification="Checked against the model.",
        xwalk=XWALK,
        today=TODAY,
        check_branch=False,
    )
    args.update(kw)
    return A.decide(vectors / name, pid, **args)


def test_every_threat_model_collection_can_be_proposed():
    """Drift guard: a new collection in an example model needs a decision here."""
    for path in VECTORS.glob("*-*.yaml"):
        if not path.name.startswith(P.MODEL_PREFIXES):
            continue
        doc = yaml.safe_load(path.read_text())
        allowed = set(P.addable(P.model_kind(path))) | {"reviews", "assertions"}
        if P.model_kind(path) == "sdl":
            continue  # SDL models also hold program context a patch does not touch
        lists = {k for k, v in doc.items() if isinstance(v, list)}
        assert lists <= allowed, (path.name, lists - allowed)


def test_threat_patch_is_proposed_only(vectors):
    before = (vectors / THREAT).read_bytes()
    out = core.propose(PATCH)
    assert (vectors / THREAT).read_bytes() == before
    rec = out["proposal"]
    assert rec["status"] == "proposed" and rec["edits"][0]["id"] == "component:render-worker"
    assert all(a["assertion_status"] == "proposed" for a in rec["assertions"])
    assert out["file"] == "spec/vectors/proposals/mvp-01-software-doc-service.proposals.yaml"


@pytest.mark.parametrize(
    "change, message",
    [
        (
            {"edit": [{"collection": "reviews", "id": "review:vuln-prop", "set": {"x": 1}}]},
            "reviews are written only by the sponsor",
        ),
        (
            {"remove": [{"collection": "reviews", "id": "review:vuln-prop"}]},
            "reviews are written only by the sponsor",
        ),
        (
            {
                "edit": [
                    {
                        "collection": "assertions",
                        "id": "assertion:vuln-propagation",
                        "set": {"assertion_status": "accepted"},
                    }
                ]
            },
            "records a decision",
        ),
        (
            {
                "edit": [
                    {
                        "collection": "components",
                        "id": "component:render-worker",
                        "set": {"id": "component:y"},
                    }
                ]
            },
            "an id cannot change",
        ),
        (
            {"edit": [{"collection": "components", "id": "component:nope", "set": {"name": "y"}}]},
            "not in the model's components",
        ),
        (
            {"remove": [{"collection": "components", "id": "component:libxml-parse"}]},
            "would not hold together",
        ),
        (
            {
                "add": {
                    "parties": PATCH["add"]["parties"],
                    "views": [
                        {
                            "id": "view:bad",
                            "name": "x",
                            "projection": "graph",
                            "focus_query": "product:nope -> attack_steps",
                        }
                    ],
                }
            },
            "would not hold together",
        ),
        (
            {
                "add": {
                    "views": [
                        {"id": "view:bad", "name": "x", "projection": "table", "focus_query": "x"}
                    ]
                }
            },
            "projection 'graph'",
        ),
        ({"add": {"sdl_practices": [{"id": "sdl-practice:x"}]}}, "not a collection"),
    ],
)
def test_refused_threat_patches_write_nothing(vectors, change, message):
    with pytest.raises(ValueError, match=message):
        core.propose(patch(**change))
    assert not (vectors / "proposals").exists()


def test_a_second_change_to_the_same_object_waits(vectors):
    core.propose(PATCH)
    again = patch(
        add={},
        assertions=[],
        proposed_by="party:example-agent",
        edit=[{"collection": "components", "id": "component:render-worker", "set": {"name": "x"}}],
    )
    with pytest.raises(ValueError, match="already has a pending change"):
        core.propose(again)


def test_sdl_edit_and_view_proposals(vectors):
    p = copy.deepcopy(SDL_PATCH)
    p["schema"] = P.PATCH_SCHEMA
    p["edit"] = [
        {
            "collection": "gates",
            "id": _first(vectors / SDL, "gates"),
            "set": {"description": "Proposed wording."},
        }
    ]
    p["add"]["views"] = [
        {
            "id": "view:sdl-practices",
            "name": "Practices",
            "projection": "graph",
            "focus_query": "security-program:tmodel-sdl -> sdl_practices",
        }
    ]
    rec = core.propose(p)["proposal"]
    assert rec["edits"][0]["collection"] == "gates"


def _first(path, coll):
    return yaml.safe_load(path.read_text())[coll][0]["id"]


def test_get_proposals_lists_pending_and_views(vectors):
    core.propose(PATCH)
    listing = core.pending_proposals()
    counts = {m["file"]: m["pending"] for m in listing["models"]}
    assert counts[THREAT] == 1 and counts[SDL] == 0
    out = core.pending_proposals({"file": THREAT})
    assert out["kind"] == "threat"
    (shown,) = out["proposals"]
    assert shown["state"] == "proposed" and shown["by"] == "AI agent"
    assert {
        "action": "edit",
        "collection": "components",
        "id": "component:render-worker",
        "fields": ["description"],
    } in shown["changes"]
    states = {v["id"]: v for v in out["views"]}
    assert states["view:papermill-attack-graph"]["state"] == "accepted"
    proposed = states["view:xxe-focus"]
    assert proposed["state"] == "proposed" and proposed["proposal"] == shown["id"]
    assert proposed["node_ids"][0] == "threat-instance:xxe-file-read"
    assert "attack-step:upload-crafted-doc" in proposed["node_ids"]


def test_proposals_route_is_get_only_and_names_no_path(vectors):
    core.propose(PATCH)
    httpd = server.make_server(port=0)
    import threading

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        port = httpd.server_address[1]
        body = urllib.request.urlopen(
            f"http://127.0.0.1:{port}/proposals?file={THREAT}", timeout=5
        ).read()
        assert str(vectors) not in body.decode()
        assert json.loads(body)["views"]
        req = urllib.request.Request(f"http://127.0.0.1:{port}/proposals", data=b"{}")
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(req, timeout=5)
        assert err.value.code in (404, 405, 501)
    finally:
        httpd.shutdown()
    assert not any("accept" in route for route in server.ROUTES)


def test_view_members_follow_the_example_queries():
    doc = yaml.safe_load((VECTORS / "mvp-03-hierarchical-system.yaml").read_text())
    members = P.view_members(doc, doc["views"][0]["focus_query"])
    assert "component:brake-ecu" in members and any(m.startswith("attack-path:") for m in members)
    doc18 = yaml.safe_load((VECTORS / "mvp-18-shared-vuln-vex-override.yaml").read_text())
    assert len(P.view_members(doc18, doc18["views"][0]["focus_query"])) > 1
    with pytest.raises(ValueError, match="not a collection or relationship"):
        P.view_members(doc, "product:connected-vehicle-system -> nonsense")


# ---- tmodel accept: the sponsor's decision ----


def test_accept_applies_keeps_comments_and_writes_reviews(vectors):
    pid = core.propose(PATCH)["proposal"]["id"]
    text = (vectors / THREAT).read_text()
    comments = [line for line in text.splitlines() if line.lstrip().startswith("#")]
    out = decide(vectors, THREAT, pid, declare_sponsor="nymble")
    assert out["model_changed"] and out["verdict"] == "accepted"
    new = (vectors / THREAT).read_text()
    assert [line for line in new.splitlines() if line.lstrip().startswith("#")] == comments
    doc = yaml.safe_load(new)
    ids = {o["id"] for c in doc.values() if isinstance(c, list) for o in c}
    assert {"mitigation:reject-doctype-uploads", "view:xxe-focus", "party:nymble"} <= ids
    (a,) = [x for x in doc["assertions"] if x["id"] == "assertion:doctype-reject-mitigates-xxe"]
    assert a["assertion_status"] == "accepted"
    (r,) = [x for x in doc["reviews"] if x["reviews"] == a["id"]]
    assert r["reviewer"] == "party:nymble" and r["review_status"] == "accepted"
    worker = next(c for c in doc["components"] if c["id"] == "component:render-worker")
    assert "agent clarification" in worker["description"]
    assert not P.proposals_path(vectors / THREAT).exists()
    log = yaml.safe_load(A.decided_path(vectors / THREAT).read_text())
    assert log["decisions"][0]["decided_by"] == "party:nymble"
    # The accepted model still loads as the app loads it.
    assert core.model_graph(THREAT)["nodes"]


def test_accept_removal(vectors):
    p = patch(
        add={"parties": PATCH["add"]["parties"]},
        edit=[],
        assertions=[],
        remove=[{"collection": "views", "id": "view:papermill-attack-graph"}],
    )
    pid = core.propose(p)["proposal"]["id"]
    assert core.pending_proposals({"file": THREAT})["views"][0]["state"] == "proposed_removal"
    decide(vectors, THREAT, pid, declare_sponsor="nymble")
    assert "views" not in yaml.safe_load((vectors / THREAT).read_text()) or not yaml.safe_load(
        (vectors / THREAT).read_text()
    ).get("views")


def test_reject_leaves_the_model_alone(vectors):
    pid = core.propose(PATCH)["proposal"]["id"]
    before = (vectors / THREAT).read_bytes()
    out = decide(
        vectors,
        THREAT,
        pid,
        verdict="rejected",
        justification="Not this release.",
        declare_sponsor="nymble",
    )
    assert not out["model_changed"] or b"party:nymble" in (vectors / THREAT).read_bytes()
    doc = yaml.safe_load((vectors / THREAT).read_text())
    assert "mitigation:reject-doctype-uploads" not in {m["id"] for m in doc["mitigations"]}
    assert before.count(b"\n") <= (vectors / THREAT).read_bytes().count(b"\n")
    assert (
        yaml.safe_load(A.decided_path(vectors / THREAT).read_text())["decisions"][0][
            "proposal_record"
        ]["id"]
        == pid
    )


def test_only_the_sponsor_decides(vectors):
    pid = core.propose(PATCH)["proposal"]["id"]
    with pytest.raises(ValueError, match="only the sponsor decides"):
        decide(vectors, THREAT, pid, reviewer="party:sec-reviewer")
    with pytest.raises(ValueError, match="not a Party"):
        decide(vectors, THREAT, pid, reviewer="party:nymble")
    with pytest.raises(ValueError, match="justification"):
        decide(vectors, THREAT, pid, justification=" ", declare_sponsor="nymble")
    with pytest.raises(ValueError, match="not a pending proposal"):
        decide(vectors, THREAT, "proposal:nope", declare_sponsor="nymble")
    assert P.load_proposals(vectors / THREAT)


def test_sdl_accept_uses_the_sponsor_in_the_model(vectors):
    pid = core.propose(SDL_PATCH)["proposal"]["id"]
    with pytest.raises(ValueError, match="only the sponsor decides"):
        decide(vectors, SDL, pid, reviewer="party:phaskell")
    decide(vectors, SDL, pid)
    view = core.sdl({"file": SDL})
    ids = {it["id"] for ph in view["phases"] for it in ph["items"]}
    assert "sdl-practice:secrets-management" in ids
    assert view["proposals"] == []


def test_accept_refuses_main(vectors, tmp_path):
    pid = core.propose(PATCH)["proposal"]["id"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(vectors)], check=True)
    with pytest.raises(ValueError, match="on branch main"):
        decide(vectors, THREAT, pid, check_branch=True, declare_sponsor="nymble")


def test_cli_proposals_and_accept(vectors, tmp_path, capsys):
    f = tmp_path / "patch.yaml"
    f.write_text(yaml.safe_dump(PATCH))
    assert cli.main(["propose", str(f), "--json"]) == 0
    pid = json.loads(capsys.readouterr().out)["proposal"]["id"]
    assert cli.main(["proposals", THREAT, "--in-process"]) == 0
    assert "view view:xxe-focus  [proposed]" in capsys.readouterr().out
    args = [
        "accept",
        pid,
        "--model",
        THREAT,
        "--reviewer",
        "party:nymble",
        "--justification",
        "ok",
        "--declare-sponsor",
        "nymble",
    ]
    rc = cli.main(args)
    out = capsys.readouterr()
    if A.current_branch(vectors) in A.PROTECTED_BRANCHES:
        assert rc == 1 and "on branch" in out.err
    else:
        assert rc == 0 and "accepted by party:nymble" in out.out


GUI_FIXTURE = ROOT / "apps" / "desktop" / "src" / "fixtures" / "proposals-mvp-01.json"


def fixture_payload(vectors):
    """GET /proposals for mvp-01 with the example patch pending, at a fixed time."""
    from datetime import UTC, datetime

    P.propose(PATCH, vectors / THREAT, XWALK, now=datetime(2026, 11, 7, 20, 0, tzinfo=UTC))
    return core.pending_proposals({"file": THREAT})


def test_gui_fixture_matches_the_engine(vectors):
    """apps/desktop/src/fixtures/proposals-mvp-01.json is what the engine serves.
    Regenerate: python -m tests.test_propose_v2 (from engine/)."""
    assert json.loads(GUI_FIXTURE.read_text()) == fixture_payload(vectors)


if __name__ == "__main__":  # regenerate the GUI fixture
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "spec" / "vectors"
        shutil.copytree(VECTORS, d, ignore=shutil.ignore_patterns("proposals"))
        shutil.copy(ROOT / "spec" / "MAP-0001.yaml", Path(tmp) / "spec" / "MAP-0001.yaml")
        core.APPROVED_VECTOR_DIRECTORY = d
        core.CROSSWALK_FILE = Path(tmp) / "spec" / "MAP-0001.yaml"
        GUI_FIXTURE.write_text(json.dumps(fixture_payload(d), indent=2) + "\n")
