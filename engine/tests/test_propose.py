"""`tmodel propose`: an agent's SDL patch becomes proposals only (DL-0044)."""

import copy
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from engine import cli, core
from engine import propose as P

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "spec" / "vectors" / "sdl-01-tmodel-desktop.yaml"
PATCH = yaml.safe_load((Path(__file__).parent / "fixtures" / "sdl-patch-example.yaml").read_text())
XWALK = yaml.safe_load((ROOT / "spec" / "MAP-0001.yaml").read_text())
NOW = datetime(2026, 11, 7, 12, 0, tzinfo=UTC)


@pytest.fixture
def vectors(tmp_path, monkeypatch):
    """A copy of the approved model directory, so nothing in the repo is written."""
    d = tmp_path / "spec" / "vectors"
    d.mkdir(parents=True)
    shutil.copy(MODEL, d / MODEL.name)
    shutil.copy(MODEL.parent / "mvp-01-software-doc-service.yaml", d)
    shutil.copy(MODEL.parent / "example-container.linkml.yaml", d)
    shutil.copy(ROOT / "spec" / "MAP-0001.yaml", tmp_path / "spec" / "MAP-0001.yaml")
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", d)
    monkeypatch.setattr(core, "CROSSWALK_FILE", tmp_path / "spec" / "MAP-0001.yaml")
    return d


def patch(**changes):
    p = copy.deepcopy(PATCH)
    p.update(changes)
    return p


def test_writes_only_proposals_and_leaves_the_model_alone(vectors):
    before = (vectors / MODEL.name).read_bytes()
    out = core.propose(PATCH)
    assert (vectors / MODEL.name).read_bytes() == before
    assert out["file"] == "spec/vectors/proposals/sdl-01-tmodel-desktop.proposals.yaml"
    written = yaml.safe_load(
        (vectors / "proposals" / "sdl-01-tmodel-desktop.proposals.yaml").read_text()
    )
    rec = written["proposals"][0]
    assert rec["status"] == "proposed"
    assert all(a["assertion_status"] == "proposed" for a in rec["assertions"])
    assert rec["assertions"][0]["asserted_by"] == "party:example-agent"
    assert "reviews" not in rec["objects"]


def test_the_sdl_view_lists_pending_proposals(vectors):
    core.propose(PATCH)
    view = core.sdl({"file": MODEL.name})
    assert len(view["proposals"]) == 1
    shown = view["proposals"][0]
    assert shown["state"] == "proposed" and shown["by"] == "AI agent"
    assert {
        "collection": "sdl_practices",
        "id": "sdl-practice:secrets-management",
        "name": "Keep secrets out of the repository",
    } in shown["objects"]
    # The model itself is unchanged: the practice is not in the phases.
    ids = {it["id"] for ph in view["phases"] for it in ph["items"]}
    assert "sdl-practice:secrets-management" not in ids


def test_same_ids_twice_are_refused(vectors):
    core.propose(PATCH)
    with pytest.raises(ValueError, match="id already exists"):
        core.propose(PATCH)


@pytest.mark.parametrize(
    "change, message",
    [
        ({"add": {"reviews": [{"id": "review:x"}]}}, "not a collection a proposal may add to"),
        ({"reviews": []}, "unknown key 'reviews'"),
        ({"schema": "nope"}, "schema must be"),
        ({"edit": [{"collection": "gates", "id": "gate:x", "set": {"name": "y"}}]}, "needs schema"),
        ({"generated_by": ""}, "generated_by is required"),
        ({"target": "example-container.linkml.yaml"}, "not a model file"),
        ({"target": "../../etc/passwd.yaml"}, "outside approved model directory"),
        ({"proposed_by": "party:nobody"}, "not a Party"),
    ],
)
def test_refused_patches_write_nothing(vectors, change, message):
    with pytest.raises(ValueError, match=message):
        core.propose(patch(**change))
    assert not (vectors / "proposals").exists()


def test_cannot_propose_an_accepted_assertion(vectors):
    p = patch()
    p["assertions"][0]["assertion_status"] = "accepted"
    with pytest.raises(ValueError, match="always 'proposed'"):
        core.propose(p)


def test_cannot_smuggle_a_decision_onto_an_object(vectors):
    p = patch()
    p["add"]["sdl_practices"][0]["review_status"] = "accepted"
    with pytest.raises(ValueError, match="records a decision"):
        core.propose(p)


def test_a_dangling_reference_is_refused(vectors):
    p = patch()
    p["add"]["sdl_practices"][0]["produces"] = ["evidence:missing"]
    with pytest.raises(ValueError, match="would not hold together"):
        core.propose(p)


def test_an_unknown_practice_row_is_refused(vectors):
    p = patch()
    p["add"]["sdl_practices"][0]["practice_key"] = "not-a-row"
    with pytest.raises(ValueError, match="not a MAP-0001 row"):
        core.propose(p)


def test_record_is_stamped_and_ided():
    rec = P.propose(PATCH, MODEL, XWALK, now=NOW, write=False)
    assert rec["id"].startswith("proposal:20261107T120000Z-")
    assert rec["proposed_at"] == "2026-11-07T12:00:00Z"


def test_cli_dry_run(vectors, tmp_path, capsys):
    f = tmp_path / "patch.json"
    f.write_text(json.dumps(PATCH))
    assert cli.main(["propose", str(f), "--dry-run"]) == 0
    assert "dry run" in capsys.readouterr().out
    assert not (vectors / "proposals").exists()
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(patch(schema="x")))
    assert cli.main(["propose", str(bad)]) == 1
    assert "schema must be" in capsys.readouterr().err
