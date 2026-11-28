"""Threat model projects (#288): the team's design for saving and reopening models, the
ReviewWorkspace contract (#289), checks before any write, atomic saves, and errors
that name no path. Every project folder here is below pytest's temporary folder."""

import errno
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from unittest.mock import ANY
from uuid import uuid4

import pytest
import yaml
from workspace_support import (
    EXAMPLE,
    EXAMPLES,
    VECTORS,
    Clock,
    Tokens,
    fail_at,
    projects,
    rating_change,
    review_change,
    sha256,
    snapshot,
    use_examples,
)

from engine import core, model_workspace
from engine.model_workspace import CONTAINER_FILES, ProjectWorkspace, linkml_available
from engine.review_workspace import ModelRevision, ProjectReviewWorkspace, ReviewError

needs_linkml = pytest.mark.skipif(
    not linkml_available(), reason="LinkML is not installed (the engine CI job has none)"
)
FAMILY = {"mvp-": "ExampleModelCore", "tv-": "ExampleModel", "pv-": "ExampleModelProposed"}


@pytest.fixture
def ws():
    return ProjectWorkspace(schema_check=False, clock=Clock(), token=Tokens())


@pytest.fixture
def project(ws, monkeypatch, tmp_path):
    """A project started from the synthetic example: (workspace, model id, folder)."""
    use_examples(monkeypatch, tmp_path)
    folder = projects(tmp_path) / "Example Threat Model"
    return ws, ws.create_project(folder, source_file=EXAMPLE)["model_id"], folder


def raises(code, call, *args, **kwargs):
    with pytest.raises(ReviewError) as err:
        call(*args, **kwargs)
    assert err.value.code == code, err.value.to_dict()
    return err.value


# The team's design: the layout, original.yaml, versions and their metadata


def test_a_new_project_has_the_team_layout(project):
    ws, model_id, folder = project
    source = (EXAMPLES / EXAMPLE).read_bytes()
    digest = sha256(EXAMPLES / EXAMPLE)
    assert sorted(snapshot(folder)) == [
        "original.yaml",
        "project.json",
        "versions",
        "versions/v001.yaml",
    ]
    assert (folder / "original.yaml").read_bytes() == source
    assert (folder / "versions" / "v001.yaml").read_bytes() == source
    assert json.loads((folder / "project.json").read_text(encoding="utf-8")) == {
        "format": "tmodel-project",
        "format_version": 1,
        "id": model_id,
        "name": "Example Threat Model",
        "created_at": "2026-11-27T12:00:00Z",
        "source": {"file": EXAMPLE, "sha256": digest, "origin": "example"},
        "container": "ExampleModelProposed",  # not an mvp- example: the first that fits
        "current_version": "v001",
        "versions": [
            {
                "version": "v001",
                "file": "versions/v001.yaml",
                "description": f"Initial model, copied from {EXAMPLE}",
                "created_at": "2026-11-27T12:00:00Z",
                "parent_version": None,
                "sha256": digest,
                "summary": None,
            }
        ],
    }
    assert re.fullmatch(r"project:[0-9a-f]{32}", model_id)
    assert not [p.name for p in folder.parent.iterdir() if p.name != folder.name]


def test_each_save_adds_the_next_version_with_its_metadata(project):
    ws, model_id, folder = project
    document = ws.read(model_id, "v001").document
    current, saved = "v001", []
    for number in range(2, 12):  # through v011: sequential and zero-padded
        current = ws.save_version(
            model_id,
            current,
            rating_change(document, ("high", "low")[number % 2]),
            description=f"Save {number}",
            summary={"highest_risk": number},
        )
        saved.append(current)
    assert saved == [f"v{number:03d}" for number in range(2, 12)]
    assert sorted(p.name for p in (folder / "versions").iterdir()) == [
        f"v{number:03d}.yaml" for number in range(1, 12)
    ]
    versions = ws.list_versions(model_id)["versions"]
    assert [v["number"] for v in versions] == list(range(1, 12))
    assert versions[1] == {
        "number": 2,
        "version": "v002",
        "description": "Save 2",
        "created_at": "2026-11-27T12:01:00Z",
        "parent_version": "v001",
        "sha256": sha256(folder / "versions" / "v002.yaml"),
        "summary": {"highest_risk": 2},
    }
    assert all(v["parent_version"] == f"v{n - 1:03d}" for n, v in enumerate(versions[1:], 2))
    # commit() is save_version with no description or summary (#289 may pass them later)
    assert ws.commit(model_id, "v011", document) == "v012"
    last = ws.list_versions(model_id)["versions"][-1]
    assert (last["version"], last["description"], last["summary"]) == ("v012", None, None)
    stored = json.loads((folder / "project.json").read_text(encoding="utf-8"))
    assert stored["current_version"] == "v012"
    assert stored["versions"][-1]["file"] == "versions/v012.yaml"


def test_original_yaml_never_changes_and_older_versions_reopen(project):
    ws, model_id, folder = project
    original = (folder / "original.yaml").read_bytes()
    first = ws.read(model_id, "v001").document
    second = review_change(first, "high")
    third = review_change(second, "medium", "rejected")
    ws.save_version(model_id, "v001", second, description="Reviewed")
    ws.save_version(model_id, "v002", third, description="Corrected the rating")
    assert (folder / "original.yaml").read_bytes() == original
    for revision, document in (("v001", first), ("v002", second), ("v003", third)):
        opened = ws.open_model(model_id, revision)
        assert (opened["revision"], opened["current_revision"]) == (revision, "v003")
        assert opened["document"] == document
        assert ws.read(model_id, revision).document == document
    assert ws.open_model(model_id)["revision"] == "v003"


def test_a_project_reopens_after_a_restart_with_the_same_id(project):
    ws, model_id, folder = project
    saved = review_change(ws.read(model_id, "v001").document)
    ws.save_version(model_id, "v001", saved, description="Reviewed")
    restarted = ProjectWorkspace(schema_check=False)  # a new engine: nothing is open yet
    raises("not_found", restarted.read, model_id, "v001")
    opened = restarted.open_project(folder)
    assert (opened["model_id"], opened["revision"], opened["version_count"]) == (
        model_id,
        "v002",
        2,
    )
    assert opened["document"] == saved
    assert restarted.list_models()["models"][0]["model_id"] == model_id
    # The id is in project.json, so a moved folder keeps it too.
    moved = folder.parent / "Moved Threat Model"
    folder.rename(moved)
    raises("not_found", restarted.open_model, model_id)
    assert restarted.open_project(moved)["model_id"] == model_id


def _xattrs(folder):
    if sys.platform != "darwin" or shutil.which("xattr") is None:
        return None
    return subprocess.run(["xattr", str(folder)], capture_output=True, text=True).stdout.split()


def test_an_empty_folder_the_user_made_is_filled_in_place(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    folder = projects(tmp_path) / "Made in Finder"
    folder.mkdir()
    folder.chmod(0o755)
    (folder / ".DS_Store").write_bytes(b"Finder view settings")
    if _xattrs(folder) is not None:  # a Finder tag, on macOS
        tag = ["xattr", "-w", "com.apple.metadata:_kMDItemUserTags", "Blue", str(folder)]
        subprocess.run(tag, check=True)
    before, tags = folder.stat(), _xattrs(folder)
    ws.create_project(folder, source_file=EXAMPLE, name="  Example service review  ")
    assert sorted(snapshot(folder)) == [
        ".DS_Store",
        "original.yaml",
        "project.json",
        "versions",
        "versions/v001.yaml",
    ]
    # The same folder, not a replacement: its inode, its permissions, its tags stay.
    after = folder.stat()
    assert (after.st_ino, stat.S_IMODE(after.st_mode)) == (before.st_ino, 0o755)
    assert _xattrs(folder) == tags
    assert (folder / ".DS_Store").read_bytes() == b"Finder view settings"
    assert ws.list_models()["models"][0]["name"] == "Example service review"


def test_a_link_to_an_empty_folder_makes_the_project_in_that_folder(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    real = projects(tmp_path) / "Real folder"
    real.mkdir()
    (real / ".DS_Store").write_bytes(b"Finder view settings")
    chosen = projects(tmp_path) / "Chosen"
    chosen.symlink_to(real)
    created = ws.create_project(chosen, source_file=EXAMPLE)
    assert created["name"] == "Chosen"  # the name of the folder the host passed
    assert chosen.is_symlink()
    assert sorted(snapshot(real)) == [
        ".DS_Store",
        "original.yaml",
        "project.json",
        "versions",
        "versions/v001.yaml",
    ]
    assert ws.open_project(chosen)["model_id"] == created["model_id"]
    assert ws.open_project(real)["model_id"] == created["model_id"]


def test_projects_from_every_example_leave_the_examples_unchanged(ws, tmp_path):
    before = snapshot(VECTORS)
    for model in core.list_models()["models"]:
        folder = projects(tmp_path) / model["id"]
        created = ws.create_project(folder, source_file=model["file"])
        assert created["container"] == FAMILY[model["file"][: model["file"].index("-") + 1]]
        assert (folder / "original.yaml").read_bytes() == (VECTORS / model["file"]).read_bytes()
        document = ws.read(created["model_id"], "v001").document
        assert ws.save_version(created["model_id"], "v001", rating_change(document)) == "v002"
    assert snapshot(VECTORS) == before


def test_a_read_only_examples_folder_is_enough(ws, monkeypatch, tmp_path):
    examples = use_examples(monkeypatch, tmp_path, EXAMPLE, "pv-01-can-injection-theft.yaml")
    for path in examples.iterdir():
        path.chmod(0o444)
    examples.chmod(0o555)  # as the bundled examples are in the app
    try:
        before = snapshot(examples)
        folder = projects(tmp_path) / "Theft"
        model_id = ws.create_project(folder, source_file="pv-01-can-injection-theft.yaml")[
            "model_id"
        ]
        ws.save_version(model_id, "v001", review_change(ws.read(model_id, "v001").document))
        assert snapshot(examples) == before
    finally:
        examples.chmod(0o755)


# Read-only files and starting a project from one


def test_a_file_opens_read_only_and_can_start_a_project(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    loose = tmp_path / "downloads" / "imported-model.yaml"
    loose.parent.mkdir()
    shutil.copyfile(EXAMPLES / EXAMPLE, loose)
    opened = ws.open_file(loose)
    model_id, revision = opened["model_id"], opened["revision"]
    assert re.fullmatch(r"file:[0-9a-f]{32}", model_id)
    assert revision == opened["current_revision"] == "sha256:" + sha256(loose)
    assert (opened["kind"], opened["editable"], opened["name"]) == ("file", False, loose.name)
    assert opened["version"]["number"] is None
    snapshot_revision = ws.read(model_id, revision)
    assert not snapshot_revision.editable
    assert [r.revision for r in ws.history(model_id, revision)] == [revision]
    loose.write_text("parties: []\n", encoding="utf-8")  # later reads see the file as opened
    assert ws.read(model_id, revision).document == snapshot_revision.document
    raises("permission_denied", ws.commit, model_id, revision, snapshot_revision.document)
    assert raises("revision_conflict", ws.commit, model_id, "v001", {}).current_revision == revision
    folder = projects(tmp_path) / "Imported"
    started = ws.create_project(folder, model_id=model_id, name="Imported product")
    assert (folder / "original.yaml").read_bytes() == (EXAMPLES / EXAMPLE).read_bytes()
    assert started["name"] == "Imported product"
    assert started["source"] == {
        "file": "imported-model.yaml",
        "sha256": sha256(EXAMPLES / EXAMPLE),
        "origin": "file",
    }
    assert [m["kind"] for m in ws.list_models()["models"]] == ["file", "project"]


def test_opening_a_file_refuses_what_is_not_a_model_file(ws, tmp_path):
    (tmp_path / "notes.txt").write_text("parties: []\n", encoding="utf-8")
    (tmp_path / "broken.yaml").write_text("parties: [\n", encoding="utf-8")
    (tmp_path / "list.yaml").write_text("- one\n", encoding="utf-8")
    (tmp_path / "folder.yaml").mkdir()
    raises("not_found", ws.open_file, tmp_path / "missing.yaml")
    for name, field in (
        ("notes.txt", "path"),
        ("broken.yaml", "path"),
        ("list.yaml", "path"),
        ("folder.yaml", "path"),
    ):
        assert raises("validation_error", ws.open_file, tmp_path / name).field == field
    assert raises("validation_error", ws.open_file, "relative/model.yaml").field == "path"
    if hasattr(os, "mkfifo"):
        os.mkfifo(tmp_path / "pipe.yaml")  # must not hang
        assert raises("validation_error", ws.open_file, tmp_path / "pipe.yaml").field == "path"
    assert ws.list_models()["count"] == 0


# Where a project may be made, and from what


def test_create_refuses_unusable_folders_and_sources(project, tmp_path):
    ws, model_id, folder = project
    busy = projects(tmp_path) / "Busy"
    busy.mkdir()
    (busy / "notes.txt").write_text("mine\n", encoding="utf-8")
    cases = [
        ((busy,), {"source_file": EXAMPLE}, "path"),
        ((folder,), {"source_file": EXAMPLE}, "path"),  # already a project
        ((tmp_path / "no" / "parent",), {"source_file": EXAMPLE}, "path"),
        (("relative/folder",), {"source_file": EXAMPLE}, "path"),
        ((tmp_path / "New",), {}, "source_file"),
        ((tmp_path / "New",), {"source_file": EXAMPLE, "model_id": model_id}, "source_file"),
        ((tmp_path / "New",), {"model_id": model_id}, "model_id"),  # a project, not a file
        ((tmp_path / "New",), {"source_file": EXAMPLE, "name": "  "}, "name"),
    ]
    before = snapshot(tmp_path)
    for args, kwargs, field in cases:
        assert raises("validation_error", ws.create_project, *args, **kwargs).field == field
    for source in ("sdl-01-tmodel-desktop.yaml", "../vectors/mvp-01-software-doc-service.yaml"):
        raises("not_found", ws.create_project, tmp_path / "New", source_file=source)
    raises("not_found", ws.create_project, tmp_path / "New", model_id="file:" + "0" * 32)
    assert snapshot(tmp_path) == before
    assert busy.joinpath("notes.txt").read_text(encoding="utf-8") == "mine\n"


def test_a_project_folder_is_never_among_the_examples(ws):
    inside = VECTORS / "a-project"
    for folder in (inside, VECTORS, VECTORS.parent.parent):  # inside, the folder, a parent
        error = raises("validation_error", ws.create_project, folder, source_file=EXAMPLE)
        assert error.field == "path"
        assert raises("validation_error", ws.open_project, folder).field == "path"
    assert not inside.exists()


def test_a_folder_put_back_at_the_same_path_opens_again(project):
    ws, model_id, folder = project
    ws.save_version(model_id, "v001", rating_change(ws.read(model_id, "v001").document))
    backup = folder.parent / "Backup"
    shutil.copytree(folder, backup)
    shutil.rmtree(folder)
    backup.rename(folder)  # a new inode at the same path, as a restore from a backup gives
    opened = ws.open_project(folder)
    assert (opened["model_id"], opened["revision"]) == (model_id, "v002")
    assert ws.save_version(model_id, "v002", ws.read(model_id, "v002").document) == "v003"


def test_a_drive_mounted_again_opens_again(project, monkeypatch):
    ws, model_id, folder = project
    identity = model_workspace._identity

    def another_device(path):  # a FAT drive attached again gets another device number
        device, inode = identity(path)
        return device + 1, inode

    monkeypatch.setattr(model_workspace, "_identity", another_device)
    assert ws.open_project(folder)["model_id"] == model_id
    document = rating_change(ws.read(model_id, "v001").document)
    assert ws.save_version(model_id, "v001", document) == "v002"


def test_a_copied_project_folder_is_refused_while_its_original_is_open(project):
    ws, model_id, folder = project
    copy = folder.parent / "Copy of Example Threat Model"
    shutil.copytree(folder, copy)
    assert raises("validation_error", ws.open_project, copy).field == "path"
    shutil.rmtree(folder)
    assert ws.open_project(copy)["model_id"] == model_id  # the original is gone


def test_a_project_keeps_the_container_ci_checks_its_example_against(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path, "mvp-01-software-doc-service.yaml")
    created = ws.create_project(
        projects(tmp_path) / "Core", source_file="mvp-01-software-doc-service.yaml"
    )
    assert created["container"] == "ExampleModelCore"
    document = ws.read(created["model_id"], "v001").document
    bounded = {**document, "trust_boundaries": []}  # ExampleModelProposed has it; Core does not
    ws.validate(bounded)  # a container holds all of these collections
    error = raises("validation_error", ws.save_version, created["model_id"], "v001", bounded)
    assert error.field == "trust_boundaries"
    # A file that is not an example gets the first container that holds its collections.
    governed = projects(tmp_path) / "governed.yaml"
    governed.write_text(yaml.safe_dump({**document, "threat_models": []}), encoding="utf-8")
    assert ws.open_file(governed)["container"] == "ExampleModel"


def _attributes(container):
    path = VECTORS / CONTAINER_FILES[container]
    return yaml.safe_load(path.read_text(encoding="utf-8"))["classes"][container]["attributes"]


def test_shared_collections_are_defined_alike_in_every_container():
    seen = {}
    for container in CONTAINER_FILES:
        for name, definition in _attributes(container).items():
            assert seen.setdefault(name, definition) == definition, (container, name)
    # Why FITTING_CONTAINERS can skip ExampleModelCore and stop at ExampleModelSdl
    assert set(_attributes("ExampleModelCore")) <= set(_attributes("ExampleModelProposed"))
    assert set(_attributes("ExampleModel")) <= set(_attributes("ExampleModelSdl"))
    assert set(_attributes("ExampleModelProposed")) - set(_attributes("ExampleModelSdl"))


# Checks before any write


def _nested(depth):
    value = "deep"
    for _ in range(depth):
        value = {"level": value}
    return value


INVALID = [
    (lambda d: {**d, "colours": []}, "colours"),
    (lambda d: {**d, "parties": {"id": "party:x"}}, "parties"),
    (lambda d: _set(d, "attack_paths", "steps", ["attack-step:missing"]), "model"),
    (lambda d: _set(d, "attack_steps", "gate", "xor_gate"), "model"),
    (lambda d: _set(d, "attack_paths", "attack_feasibility", "certain"), "model"),
    (lambda d: _set(d, "risk_scores", "weight", float("nan")), "risk_scores[0].weight"),
    (lambda d: _set(d, "attack_paths", "steps", ("attack-step:example",)), "attack_paths[0].steps"),
    (lambda d: _set(d, "parties", 1, "a number as a key"), "parties[0]"),
    (lambda d: _set(d, "products", "notes", _nested(70)), re.compile(r"products\[0\]\.notes\..*")),
    (lambda d: {**d, "parties": d["parties"] + d["parties"][:1]}, "model"),
    (lambda d: {}, "model"),
    (lambda d: ["not", "a", "mapping"], "model"),
]


def _set(document, collection, key, value):
    changed = deepcopy(document)
    changed[collection][0][key] = value
    return changed


@pytest.mark.parametrize(("change", "field"), INVALID)
def test_an_invalid_document_is_refused_and_writes_nothing(project, change, field):
    ws, model_id, folder = project
    candidate = change(ws.read(model_id, "v001").document)
    before = snapshot(folder)
    for error in (
        raises("validation_error", ws.validate, candidate),
        raises("validation_error", ws.save_version, model_id, "v001", candidate),
    ):
        assert (
            field.fullmatch(error.field) if isinstance(field, re.Pattern) else error.field == field
        )
    assert snapshot(folder) == before


def test_a_summary_at_the_limits_is_accepted(project):
    ws, model_id, folder = project
    document = rating_change(ws.read(model_id, "v001").document)
    summary = _nested(8)  # 8 levels deep, small
    assert ws.save_version(model_id, "v001", document, summary=summary) == "v002"
    assert ws.list_versions(model_id)["versions"][-1]["summary"] == summary


@pytest.mark.parametrize(
    ("description", "summary", "field"),
    [
        ("x" * 501, None, "description"),
        (5, None, "description"),
        (None, ["not", "an object"], "summary"),
        (None, {"risk": float("inf")}, "summary"),
        (None, {1: "a number as a key"}, "summary"),
        (None, {"risk": ("a", "tuple")}, "summary"),
        (None, {"big": "x" * 70000}, "summary"),
        (None, {"long": "x" * 17000}, "summary"),  # over 16 KiB
        (None, {"zeros": [0] * 4000}, "summary"),  # 12 KB compact, over 16 KiB indented
        (None, _nested(9), "summary"),  # deeper than 8 levels
    ],
)
def test_a_bad_description_or_summary_is_refused_and_writes_nothing(
    project, description, summary, field
):
    ws, model_id, folder = project
    candidate = rating_change(ws.read(model_id, "v001").document)
    before = snapshot(folder)
    error = raises(
        "validation_error",
        ws.save_version,
        model_id,
        "v001",
        candidate,
        description=description,
        summary=summary,
    )
    assert error.field == field
    assert snapshot(folder) == before


def test_a_stale_save_is_refused_and_writes_nothing(project):
    ws, model_id, folder = project
    document = ws.read(model_id, "v001").document
    ws.save_version(model_id, "v001", rating_change(document))
    before = snapshot(folder)
    for stale, candidate in (
        ("v001", rating_change(document, "low")),
        ("v001", {"not": "a model"}),  # stale first: no check runs, nothing is written
        ("v009", document),
        ("anything", document),
    ):
        error = raises("revision_conflict", ws.save_version, model_id, stale, candidate)
        assert error.to_dict()["error"]["current_revision"] == "v002"
    assert snapshot(folder) == before


def test_reads_are_isolated_and_a_save_keeps_the_candidate_as_given(project):
    ws, model_id, folder = project
    ws.read(model_id, "v001").document["parties"].clear()
    assert ws.read(model_id, "v001").document["parties"]
    candidate = review_change(ws.read(model_id, "v001").document)
    kept = deepcopy(candidate)
    saved = ws.save_version(model_id, "v001", candidate)
    assert candidate == kept
    candidate["parties"].clear()
    assert ws.read(model_id, saved).document == kept


def test_history_is_oldest_first_and_stops_at_the_requested_version(project):
    ws, model_id, folder = project
    documents = [ws.read(model_id, "v001").document]
    for rating in ("high", "medium", "low"):
        documents.append(rating_change(documents[0], rating))
        ws.save_version(model_id, f"v{len(documents) - 1:03d}", documents[-1])
    history = ws.history(model_id, "v003")
    assert [h.revision for h in history] == ["v001", "v002", "v003"]
    assert [h.document for h in history] == documents[:3]
    assert all(h.model_id == model_id and h.editable for h in history)
    assert [v["version"] for v in ws.list_versions(model_id, "v002")["versions"]] == [
        "v001",
        "v002",
    ]
    for unknown in ("v005", "v0001", "v01", "r1", "sha256:00"):
        raises("not_found", ws.history, model_id, unknown)
        raises("not_found", ws.read, model_id, unknown)
    raises("not_found", ws.read, "project:" + "0" * 32, "v001")
    assert raises("validation_error", ws.read, model_id, "v" * 257).field == "revision"
    assert raises("validation_error", ws.read, 7, "v001").field == "model_id"


# Atomic saves


SAVE_STEPS = [
    ("_create", 1),  # the new version's temporary file
    ("_write_all", 1),
    ("_fsync", 1),
    ("_link", 1),  # the new version linked into place: it never replaces a file
    ("_fsync_directory", 1),
    ("_create", 2),  # project.json's temporary file
    ("_write_all", 2),
    ("_fsync", 2),
    ("_replace", 1),  # project.json replaced: the commit point
]


@pytest.mark.parametrize(("step", "call"), SAVE_STEPS)
def test_a_save_failing_at_any_step_before_the_commit_point_changes_nothing(
    project, monkeypatch, tmp_path, step, call
):
    ws, model_id, folder = project
    candidate = review_change(ws.read(model_id, "v001").document)
    before = snapshot(folder)
    record = fail_at(monkeypatch, step, call, tmp_path / "secret folder")
    error = raises("save_failure", ws.save_version, model_id, "v001", candidate)
    assert record["count"] >= call
    assert str(tmp_path) not in json.dumps(error.to_dict())
    assert snapshot(folder) == before
    monkeypatch.setattr(model_workspace, step, record["real"])
    assert ws.save_version(model_id, "v001", candidate) == "v002"  # the folder is not stuck


def test_a_failed_flush_after_the_commit_point_still_saves(project, monkeypatch, tmp_path):
    ws, model_id, folder = project
    candidate = review_change(ws.read(model_id, "v001").document)
    fail_at(monkeypatch, "_fsync_directory", 2, tmp_path)
    assert ws.save_version(model_id, "v001", candidate) == "v002"
    assert ws.open_model(model_id)["revision"] == "v002"
    assert ws.read(model_id, "v002").document == candidate


FILE_STEPS = [
    (step, call)
    for call in (1, 2, 3)  # original.yaml, versions/v001.yaml, project.json
    for step in ("_create", "_write_all", "_fsync", "_link", "_fsync_directory")
]
# A new folder is assembled beside it and renamed into place (the commit point). An
# existing empty folder is filled in place; project.json, linked in last, is the commit.
CREATE_STEPS = [
    *[
        ("new", step, call)
        for step, call in [*[("_make_directory", n) for n in (1, 2)], *FILE_STEPS]
    ],
    ("new", "_rename_directory", 1),
    *[("empty", step, call) for step, call in [("_make_directory", 1), *FILE_STEPS]],
]


@pytest.mark.parametrize(("chosen", "step", "call"), CREATE_STEPS)
def test_a_project_failing_at_any_step_before_the_commit_point_is_not_made(
    ws, monkeypatch, tmp_path, chosen, step, call
):
    examples = use_examples(monkeypatch, tmp_path)
    parent = projects(tmp_path)
    target = parent / "New"
    if chosen == "empty":  # a folder the user made, holding Finder's view settings
        target.mkdir()
        target.chmod(0o755)
        (target / ".DS_Store").write_bytes(b"Finder view settings")
    before, sources = snapshot(parent), snapshot(examples)
    inode = target.stat().st_ino if chosen == "empty" else None
    record = fail_at(monkeypatch, step, call, tmp_path / "secret folder")
    error = raises("save_failure", ws.create_project, target, source_file=EXAMPLE)
    assert record["count"] >= call
    assert str(tmp_path) not in json.dumps(error.to_dict())
    assert snapshot(parent) == before  # no project, nothing half-made, .DS_Store as it was
    if inode is not None:
        assert (target.stat().st_ino, stat.S_IMODE(target.stat().st_mode)) == (inode, 0o755)
    assert snapshot(examples) == sources
    assert ws.list_models()["count"] == 0
    monkeypatch.setattr(model_workspace, step, record["real"])
    assert ws.create_project(target, source_file=EXAMPLE)["revision"] == "v001"


def test_a_failed_fill_keeps_what_the_user_put_in_meanwhile(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    folder = projects(tmp_path) / "Busy meanwhile"
    folder.mkdir()
    (folder / ".DS_Store").write_bytes(b"Finder view settings")
    create, calls = model_workspace._create, {"count": 0}

    def the_user_adds_files_then_a_write_fails(path):
        calls["count"] += 1
        if calls["count"] == 3:  # project.json's temporary file: v001.yaml is in by now
            (folder / "versions" / "my-notes.txt").write_text("the user's notes")
            (folder / "notes.txt").write_text("more of the user's notes")
            raise OSError(errno.EIO, "injected")
        return create(path)

    monkeypatch.setattr(model_workspace, "_create", the_user_adds_files_then_a_write_fails)
    raises("save_failure", ws.create_project, folder, source_file=EXAMPLE)
    # Only what the engine wrote is gone; versions/ stays, as it is not empty.
    assert sorted(snapshot(folder)) == [
        ".DS_Store",
        "notes.txt",
        "versions",
        "versions/my-notes.txt",
    ]


def test_the_engines_own_leftover_temporary_files_do_not_make_a_folder_busy(
    ws, monkeypatch, tmp_path
):
    use_examples(monkeypatch, tmp_path)
    folder = projects(tmp_path) / "After a crash"
    folder.mkdir()
    for name in (".original.yaml.0123456789abcdef.tmp", ".project.json.fedcba9876543210.tmp"):
        (folder / name).write_bytes(b"left by an engine that stopped mid-write")
    assert ws.create_project(folder, source_file=EXAMPLE)["revision"] == "v001"
    # Any other name, hidden or not, still counts.
    for name in (".original.yaml.tmp", ".notes", ".project.json.0123456789ABCDEF.tmp"):
        other = projects(tmp_path) / f"With {name}"
        other.mkdir()
        (other / name).write_bytes(b"the user's")
        assert (
            raises("validation_error", ws.create_project, other, source_file=EXAMPLE).field
            == "path"
        )


def test_a_failed_flush_after_the_project_appears_still_makes_it(ws, monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    fail_at(monkeypatch, "_fsync_directory", 4, tmp_path)
    created = ws.create_project(projects(tmp_path) / "New", source_file=EXAMPLE)
    assert ws.open_model(created["model_id"])["revision"] == "v001"


def test_two_racing_saves_have_exactly_one_winner(project, monkeypatch):
    ws, model_id, folder = project
    barrier = threading.Barrier(2)
    checked = ProjectWorkspace._checked

    def checked_together(self, plain, container):
        data = checked(self, plain, container)
        barrier.wait(timeout=10)  # both saves are past the unlocked version check
        return data

    monkeypatch.setattr(ProjectWorkspace, "_checked", checked_together)
    other_window = ProjectWorkspace(schema_check=False)
    other_window.open_project(folder)
    document = ws.read(model_id, "v001").document

    def save(args):
        workspace, rating = args
        try:
            return workspace.save_version(model_id, "v001", rating_change(document, rating))
        except ReviewError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = sorted(pool.map(save, [(ws, "high"), (other_window, "low")]))
    assert results == ["revision_conflict", "v002"]
    assert sorted(p.name for p in (folder / "versions").iterdir()) == ["v001.yaml", "v002.yaml"]
    assert ws.open_model(model_id)["version_count"] == 2


@pytest.mark.skipif(model_workspace.fcntl is None, reason="no flock on this platform")
def test_a_save_waits_for_the_lock_another_process_holds(project, monkeypatch):
    import fcntl

    ws, model_id, folder = project
    candidate = rating_change(ws.read(model_id, "v001").document)
    monkeypatch.setattr(model_workspace, "LOCK_TIMEOUT_S", 0.2)
    descriptor = os.open(folder / "versions", os.O_RDONLY)
    fcntl.flock(descriptor, fcntl.LOCK_EX)  # what another engine holds while it saves
    try:
        before = snapshot(folder)
        raises("save_failure", ws.save_version, model_id, "v001", candidate)
        assert snapshot(folder) == before
    finally:
        os.close(descriptor)
    assert ws.save_version(model_id, "v001", candidate) == "v002"


def test_a_file_another_program_writes_meanwhile_is_never_replaced(project, monkeypatch):
    ws, model_id, folder = project
    link = model_workspace._link

    def another_writer_first(source, target):
        if target.name == "v002.yaml":
            target.write_bytes(b"another program's v002\n")
        link(source, target)

    monkeypatch.setattr(model_workspace, "_link", another_writer_first)
    document = rating_change(ws.read(model_id, "v001").document)
    raises("save_failure", ws.save_version, model_id, "v001", document)
    assert (folder / "versions" / "v002.yaml").read_bytes() == b"another program's v002\n"
    assert ws.open_model(model_id)["revision"] == "v001"
    assert not [p.name for p in (folder / "versions").iterdir() if p.name.endswith(".tmp")]


@pytest.mark.parametrize("code", [errno.EPERM, errno.ENOTSUP, errno.EOPNOTSUPP])
def test_without_hard_links_a_new_file_is_checked_then_renamed(
    project, monkeypatch, tmp_path, code
):
    ws, model_id, folder = project

    def no_links(source, target):  # as link() answers on FAT or exFAT
        raise OSError(code, "no hard links on this volume")

    monkeypatch.setattr(model_workspace, "_link", no_links)
    document = rating_change(ws.read(model_id, "v001").document)
    assert ws.save_version(model_id, "v001", document) == "v002"
    assert ws.create_project(projects(tmp_path) / "On FAT", source_file=EXAMPLE)["revision"]

    def another_writer_first(source, target):
        target.write_bytes(b"another program's v003\n")
        no_links(source, target)

    monkeypatch.setattr(model_workspace, "_link", another_writer_first)
    raises("save_failure", ws.save_version, model_id, "v002", document)
    assert (folder / "versions" / "v003.yaml").read_bytes() == b"another program's v003\n"


@pytest.mark.parametrize("into", ["another folder", "the examples folder"])
def test_a_linked_versions_folder_is_never_followed(project, tmp_path, into):
    ws, model_id, folder = project
    document = ws.read(model_id, "v001").document
    elsewhere = (
        tmp_path / "elsewhere" if into == "another folder" else core.APPROVED_VECTOR_DIRECTORY
    )
    if into == "another folder":
        shutil.copytree(folder / "versions", elsewhere)
    else:
        shutil.copyfile(folder / "versions" / "v001.yaml", elsewhere / "v001.yaml")
    shutil.rmtree(folder / "versions")
    (folder / "versions").symlink_to(elsewhere)
    before = snapshot(elsewhere)
    for call, args in (
        (ws.read, (model_id, "v001")),
        (ws.save_version, (model_id, "v001", rating_change(document))),
        (ws.open_project, (folder,)),
    ):
        assert "link" in raises("workspace_failure", call, *args).message
    assert snapshot(elsewhere) == before


def test_a_linked_project_json_is_never_followed(project, tmp_path):
    ws, model_id, folder = project
    document = ws.read(model_id, "v001").document
    outside = tmp_path / "outside-project.json"
    outside.write_bytes((folder / "project.json").read_bytes())
    (folder / "project.json").unlink()
    (folder / "project.json").symlink_to(outside)
    before = outside.read_bytes()
    for call, args in (
        (ws.read, (model_id, "v001")),
        (ws.save_version, (model_id, "v001", rating_change(document))),
        (ws.open_project, (folder,)),
    ):
        assert "link" in raises("workspace_failure", call, *args).message
    assert outside.read_bytes() == before
    assert (folder / "project.json").is_symlink()


def test_links_to_a_version_or_the_original_are_never_followed(project, tmp_path):
    ws, model_id, folder = project
    outside = tmp_path / "outside-original.yaml"
    outside.write_bytes((folder / "original.yaml").read_bytes())
    (folder / "original.yaml").unlink()
    (folder / "original.yaml").symlink_to(outside)  # no read or write ever goes to it
    document = rating_change(ws.read(model_id, "v001").document)
    assert ws.save_version(model_id, "v001", document) == "v002"
    assert (folder / "original.yaml").is_symlink()
    assert outside.read_bytes() == (EXAMPLES / EXAMPLE).read_bytes()
    copy = tmp_path / "outside-v002.yaml"
    copy.write_bytes((folder / "versions" / "v002.yaml").read_bytes())  # the same bytes
    (folder / "versions" / "v002.yaml").unlink()
    (folder / "versions" / "v002.yaml").symlink_to(copy)
    raises("not_found", ws.read, model_id, "v002")


def test_files_larger_than_the_engine_writes_are_not_read(project, monkeypatch):
    ws, model_id, folder = project
    project_json = (folder / "project.json").stat().st_size
    assert (folder / "versions" / "v001.yaml").stat().st_size > project_json
    monkeypatch.setattr(model_workspace, "MAX_DOCUMENT_BYTES", project_json)
    raises("not_found", ws.read, model_id, "v001")  # the version: changed outside the app
    monkeypatch.setattr(model_workspace, "MAX_PROJECT_BYTES", project_json - 1)
    raises("workspace_failure", ws.open_project, folder)  # project.json: unreadable


def test_a_save_that_would_make_project_json_too_large_is_refused(project, monkeypatch):
    ws, model_id, folder = project
    document = rating_change(ws.read(model_id, "v001").document)
    limit = (folder / "project.json").stat().st_size + 600  # room for one small version
    monkeypatch.setattr(model_workspace, "MAX_PROJECT_BYTES", limit)
    assert ws.save_version(model_id, "v001", document, summary={"note": "fits"}) == "v002"
    before = snapshot(folder)
    error = raises(
        "validation_error", ws.save_version, model_id, "v002", document, summary={"n": "x" * 500}
    )
    assert error.field == "project"
    assert snapshot(folder) == before  # nothing written, the next version file included
    # The project the engine accepted still opens, in this engine and in a new one.
    assert ProjectWorkspace(schema_check=False).open_project(folder)["revision"] == "v002"
    assert ws.read(model_id, "v001").document
    assert (folder / "project.json").stat().st_size <= limit


def test_a_missing_versions_folder_or_a_project_json_that_is_no_file_is_reported(project):
    ws, model_id, folder = project
    versions = folder / "versions"
    versions.rename(folder.parent / "versions elsewhere")  # as a sync tool might leave it
    assert "missing" in raises("workspace_failure", ws.open_project, folder).message
    (folder.parent / "versions elsewhere").rename(versions)
    if hasattr(os, "mkfifo"):  # a pipe is not a link, and must not hang the engine
        (folder / "project.json").unlink()
        os.mkfifo(folder / "project.json")
        error = raises("workspace_failure", ws.open_project, folder)
        assert "regular file" in error.message and "anything else" in error.message


def test_an_unlisted_version_file_is_never_overwritten(project):
    ws, model_id, folder = project
    (folder / "versions" / "v002.yaml").write_text("left: by an interrupted save\n")
    before = snapshot(folder)
    error = raises(
        "workspace_failure", ws.save_version, model_id, "v001", ws.read(model_id, "v001").document
    )
    assert "v002.yaml" in error.message and str(folder) not in error.message
    assert snapshot(folder) == before


def test_a_damaged_project_is_reported_never_guessed_at(project, tmp_path):
    ws, model_id, folder = project
    ws.save_version(model_id, "v001", rating_change(ws.read(model_id, "v001").document))
    (folder / "versions" / "v002.yaml").write_text("parties: []\n")  # changed outside the app
    assert "outside the app" in raises("not_found", ws.read, model_id, "v002").message
    assert ws.read(model_id, "v001").document  # the other versions still read
    (folder / "versions" / "v001.yaml").unlink()  # as a sync tool might
    raises("not_found", ws.history, model_id, "v002")
    raises("not_found", ws.open_model, model_id, "v001")
    project_json = json.loads((folder / "project.json").read_text(encoding="utf-8"))
    for damage in ("{", json.dumps({**project_json, "format_version": 2})):
        (folder / "project.json").write_text(damage, encoding="utf-8")
        raises("workspace_failure", ws.open_model, model_id)
        assert ws.list_models()["problems"][0]["error"]["code"] == "workspace_failure"
    empty = tmp_path / "empty"
    empty.mkdir()
    raises("not_found", ws.open_project, empty)
    raises("not_found", ws.open_project, tmp_path / "missing")


# Errors and the LinkML check


def test_errors_never_name_a_path(project, monkeypatch, tmp_path):
    ws, model_id, folder = project
    document = ws.read(model_id, "v001").document
    errors = []
    for call in (
        lambda: ws.open_project(tmp_path / "missing"),
        lambda: ws.open_file(tmp_path / "missing.yaml"),
        lambda: ws.create_project(folder, source_file=EXAMPLE),
        lambda: ws.read(model_id, "v404"),
        lambda: ws.save_version(model_id, "v009", document),
        lambda: ws.save_version(model_id, "v001", {**document, "colours": []}),
    ):
        with pytest.raises(ReviewError) as err:
            call()
        errors.append(err.value)
    fail_at(monkeypatch, "_replace", 1, folder)
    with pytest.raises(ReviewError) as err:
        ws.save_version(model_id, "v001", rating_change(document))
    errors.append(err.value)
    text = json.dumps([e.to_dict() for e in errors])
    for local in {str(tmp_path), os.path.realpath(tmp_path), str(Path.home()), str(VECTORS)}:
        assert local not in text
    assert {e.code for e in errors} == {
        "not_found",
        "validation_error",
        "revision_conflict",
        "save_failure",
    }


def test_requiring_linkml_where_it_is_missing_fails_at_start(monkeypatch):
    monkeypatch.setattr(model_workspace, "linkml_available", lambda: False)
    with pytest.raises(ValueError, match="LinkML"):
        ProjectWorkspace(schema_check=True)
    assert ProjectWorkspace().schema_check is False


@needs_linkml
def test_with_linkml_every_example_and_a_review_save_pass_the_schema_check(tmp_path):
    ws = ProjectWorkspace(schema_check=True)
    for model in core.list_models()["models"]:
        created = ws.create_project(projects(tmp_path) / model["id"], source_file=model["file"])
        if model["file"].startswith("pv-01"):
            document = ws.read(created["model_id"], "v001").document
            ws.save_version(created["model_id"], "v001", review_change(document))


@needs_linkml
def test_linkml_catches_what_the_engine_checks_alone_do_not(monkeypatch, tmp_path):
    use_examples(monkeypatch, tmp_path)
    for strict in (True, False):
        ws = ProjectWorkspace(schema_check=strict)
        model_id = ws.create_project(projects(tmp_path) / str(strict), source_file=EXAMPLE)[
            "model_id"
        ]
        candidate = deepcopy(ws.read(model_id, "v001").document)
        candidate["attack_paths"][0]["colour"] = "red"  # not a slot of AttackPath
        if strict:
            error = raises("validation_error", ws.save_version, model_id, "v001", candidate)
            assert error.field == "attack_paths[0]"
            assert "ExampleModelProposed" in error.message
        else:
            assert ws.save_version(model_id, "v001", candidate) == "v002"


# The way #289 uses the interface


def test_the_review_service_call_sequence_works_on_a_project(ws, monkeypatch, tmp_path):
    """What #289's ReviewService does with its workspace (engine/review_service.py at
    125a95d): read an exact revision and check the ids it gets back, change a detached
    copy, validate it, commit it, walk the history, and meet a conflict on a stale save."""
    use_examples(monkeypatch, tmp_path, "pv-01-can-injection-theft.yaml")
    created = ws.create_project(
        projects(tmp_path) / "Theft", source_file="pv-01-can-injection-theft.yaml"
    )
    model_id, revision = created["model_id"], created["revision"]
    snapshot_ = ws.read(model_id, revision)
    assert (snapshot_.model_id, snapshot_.revision, snapshot_.editable) == (
        model_id,
        revision,
        True,
    )
    snapshot_ = ModelRevision(model_id, revision, deepcopy(snapshot_.document), snapshot_.editable)
    document = deepcopy(snapshot_.document)
    person = next(p["id"] for p in document["parties"] if p.get("party_kind") == "person")
    assertion = next(a for a in document["assertions"] if a["predicate"] == "realizes_threat")
    reviews = document.setdefault("reviews", [])
    reviews.append(
        {
            "id": f"review:{uuid4()}",
            "reviews": assertion["id"],
            "reviewer": person,
            "review_status": "accepted",
            "justification": "Test-only input, not a human review.",
        }
    )
    next(p for p in document["attack_paths"] if p["id"] == assertion["subject"])[
        "attack_feasibility"
    ] = "medium"
    ws.validate(document)
    saved = ws.commit(model_id, snapshot_.revision, document)
    assert saved == "v002"
    assert ws.read(model_id, saved).document == document
    history = ws.history(model_id, saved)
    assert [(p.revision, len(p.document.get("reviews") or [])) for p in history] == [
        ("v001", 0),
        ("v002", 1),
    ]
    assert all(prior.model_id == model_id for prior in history)
    error = raises("revision_conflict", ws.commit, model_id, snapshot_.revision, document)
    assert error.to_dict() == {
        "error": {"code": "revision_conflict", "message": ANY, "current_revision": "v002"}
    }
    assert ws.read(model_id, revision).document == snapshot_.document


def test_projects_review_workspace_saves_versions_through_a_project(ws, monkeypatch, tmp_path):
    """#291's ProjectReviewWorkspace (engine/review_workspace.py) over a ProjectWorkspace:
    read, history and validate pass through, commit_version's description and summary
    land in project.json, commit leaves them null, and errors come back unchanged."""
    use_examples(monkeypatch, tmp_path, "pv-01-can-injection-theft.yaml")
    folder = projects(tmp_path) / "Theft"
    model_id = ws.create_project(folder, source_file="pv-01-can-injection-theft.yaml")["model_id"]
    adapter = ProjectReviewWorkspace(ws)
    first = adapter.read(model_id, "v001")
    assert (first.model_id, first.revision, first.editable) == (model_id, "v001", True)
    document = review_change(first.document)
    adapter.validate(document)
    summary = {"matrix": "annex-h-table-h8", "assessments": 1, "incomplete": 1}
    saved = adapter.commit_version(
        model_id, "v001", document, description="Human review and rating updates", summary=summary
    )
    assert saved == "v002"
    versions = json.loads((folder / "project.json").read_text(encoding="utf-8"))["versions"]
    assert (versions[-1]["description"], versions[-1]["summary"]) == (
        "Human review and rating updates",
        summary,
    )
    assert adapter.commit(model_id, "v002", document) == "v003"
    versions = json.loads((folder / "project.json").read_text(encoding="utf-8"))["versions"]
    assert (versions[-1]["description"], versions[-1]["summary"]) == (None, None)
    assert [r.revision for r in adapter.history(model_id, "v003")] == ["v001", "v002", "v003"]
    stale = raises(
        "revision_conflict",
        adapter.commit_version,
        model_id,
        "v001",
        document,
        description=None,
        summary=None,
    )
    assert stale.current_revision == "v003"
    long = "x" * 501  # #289 accepts longer text; a version's description is at most 500
    raises(
        "validation_error",
        adapter.commit_version,
        model_id,
        "v003",
        document,
        description=long,
        summary=None,
    )
    opened = ws.open_file(folder / "versions" / "v001.yaml")
    assert not adapter.read(opened["model_id"], opened["revision"]).editable
    raises("permission_denied", adapter.commit, opened["model_id"], opened["revision"], document)
    assert ws.open_model(model_id)["revision"] == "v003"
