import json
from pathlib import Path

import pytest
import render_app
import yaml


def test_static_data_covers_every_model_and_the_complete_library(
    tmp_path: Path,
) -> None:
    model_count, record_count = render_app.write_data(tmp_path)
    catalog = json.loads((tmp_path / "data/models.json").read_text())

    assert model_count == catalog["count"] == len(catalog["models"])
    assert catalog["problems"] == []
    assert model_count > 0
    for model in catalog["models"]:
        model_dir = tmp_path / "data/models" / model["id"]
        graph = json.loads((model_dir / "graph.json").read_text())
        paths = json.loads((model_dir / "attack-paths/index.json").read_text())
        goals = json.loads((model_dir / "attack-paths/goals.json").read_text())["goals"]
        assert graph["file"] == model["file"]
        assert paths["file"] == model["file"]
        risk = json.loads((model_dir / "risk.json").read_text())
        assert risk["file"] == model["file"]
        assert risk["matrix"] == "annex-h-table-h8"
        assert risk["count"] == len(risk["assessments"])
        assert all("recorded" in item for item in risk["assessments"])
        for item in risk["assessments"]:
            if item["damage_scenario"] is None or any(
                problem.endswith("scope_mismatch") for problem in item["problems"]
            ):
                assert all(
                    value is None
                    for result in [item, *item["routes"]]
                    for value in result["derived_risk"].values()
                )
        assert all(
            "review_records" not in path
            for item in risk["assessments"]
            for path in item["paths"]
        )
        assert len(goals) == len(paths["threats"])
        assert all(
            (model_dir / "attack-paths" / goal["file"]).is_file() for goal in goals
        )

    library = json.loads((tmp_path / "data/library/table.json").read_text())
    assert (
        record_count
        == library["count"]
        == library["total"]
        == library["library"]["count"]
    )
    assert library["library"]["problems"] == []
    assert record_count > 0


def test_sdl_data_contains_each_public_program_without_local_proposals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_if_read(*_args):
        pytest.fail("preview generation read local proposals")

    monkeypatch.setattr(render_app.core.proposals, "load_proposals", fail_if_read)
    render_app._write_sdl_data(tmp_path)
    listing = json.loads((tmp_path / "models.json").read_text())
    assert listing == render_app.core.sdl_models()
    assert listing["models"]
    for model in listing["models"]:
        views = json.loads((tmp_path / f"{Path(model['file']).stem}.json").read_text())[
            "views"
        ]
        assert set(views) == {program["id"] for program in model["programs"]}
        for program in model["programs"]:
            view = views[program["id"]]
            assert view["file"] == model["file"]
            assert view["program"]["name"] == program["name"]
            assert isinstance(view["phases"], list) and isinstance(
                view["awaiting_review"], list
            )
            assert "proposals" not in view


def test_static_data_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    render_app.write_data(first)
    render_app.write_data(second)
    assert render_app._files(first) == render_app._files(second)


@pytest.mark.parametrize("reviewer_kinds, reviewed", [(('software_agent',), False), (('person', 'person'), True)])
def test_risk_snapshot_keeps_effective_review_without_private_review_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reviewer_kinds, reviewed,
) -> None:
    source = render_app.core.APPROVED_VECTOR_DIRECTORY / "mvp-02-automotive-ecu.yaml"
    doc = yaml.safe_load(source.read_text())
    path = doc["attack_paths"][0]
    threat = path["realizes_threat"]
    doc["assertions"], doc["reviews"] = [], []
    for index, kind in enumerate(reviewer_kinds):
        reviewer = f"party:test-reviewer-{index}"
        assertion = f"assertion:test-path-{index}"
        doc["parties"].append({"id": reviewer, "party_kind": kind})
        doc["assertions"].append({
            "id": assertion, "subject": path["id"], "predicate": "realizes_threat",
            "object": threat, "assertion_status": "accepted",
        })
        doc["reviews"].append({
            "id": f"review:test-{index}", "reviews": assertion, "reviewer": reviewer,
            "review_status": "accepted", "justification": "Private test review rationale",
        })
    models = tmp_path / "models"
    models.mkdir()
    file = models / source.name
    file.write_text(yaml.safe_dump(doc))
    monkeypatch.setattr(render_app.core, "APPROVED_VECTOR_DIRECTORY", models)
    render_app.write_data(tmp_path / "published")
    snapshot = tmp_path / "published/data/models" / file.stem / "risk.json"
    rows = json.loads(snapshot.read_text())["assessments"]
    assert next(row for row in rows if row["threat"] == threat)["path_reviewed"] is reviewed
    assert "Private test review rationale" not in snapshot.read_text()
    assert all("review_records" not in path for row in rows for path in row["paths"])


def test_static_data_ignores_external_library_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    alternate = tmp_path / "alternate-library"
    alternate.mkdir()
    monkeypatch.setenv("TMODEL_LIBRARY", str(alternate))

    generated = tmp_path / "generated"
    render_app.write_data(generated)

    assert "TMODEL_LIBRARY" not in render_app.os.environ
    assert (generated / "data/library/table.json").read_bytes() == (
        render_app.OUT / "data/library/table.json"
    ).read_bytes()


def test_committed_browser_bundle_is_preview_only() -> None:
    index = (render_app.OUT / "index.html").read_text()
    scripts = "\n".join(
        path.read_text(errors="replace")
        for path in sorted((render_app.OUT / "assets").glob("*.js"))
    )

    assert "Example data, read-only preview" in index
    assert scripts
    for forbidden in ("127.0.0.1", "localhost", "__TAURI__", "@tauri-apps", "invoke("):
        assert forbidden not in scripts


def test_generator_fails_instead_of_omitting_problem_models(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        render_app.core,
        "list_models",
        lambda: {
            "count": 0,
            "models": [],
            "problems": [{"file": "broken.yaml", "error": "invalid model"}],
        },
    )
    with pytest.raises(RuntimeError, match="refusing to omit model data.*broken.yaml"):
        render_app.write_data(tmp_path)


def test_atomic_generation_keeps_previous_preview_after_partial_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "app"
    destination.mkdir()
    (destination / "valid.txt").write_text("previous valid preview\n")

    def fail_after_model_data(staged: Path) -> tuple[int, int]:
        render_app._write_json(
            staged / "data/models/mvp-01-software-doc-service/graph.json",
            {"id": "partially-generated"},
        )
        raise RuntimeError("simulated model generation failure")

    monkeypatch.setattr(render_app, "_build", fail_after_model_data)
    with pytest.raises(RuntimeError, match="simulated model generation failure"):
        render_app.write(destination)

    assert render_app._files(destination) == {
        Path("valid.txt"): b"previous valid preview\n"
    }
    assert sorted(path.name for path in tmp_path.iterdir()) == ["app"]


def test_atomic_generation_replaces_only_the_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "app"
    destination.mkdir()
    (destination / "old.txt").write_text("old\n")
    unrelated = tmp_path / "keep"
    unrelated.mkdir()
    (unrelated / "file.txt").write_text("keep\n")

    def succeed(staged: Path) -> tuple[int, int]:
        (staged / "assets").mkdir(parents=True)
        (staged / "assets/new.txt").write_text("new\n")
        return 8, 550

    monkeypatch.setattr(render_app, "_build", succeed)
    assert render_app.write(destination) == (8, 550)
    assert render_app._files(destination) == {Path("assets/new.txt"): b"new\n"}
    assert (unrelated / "file.txt").read_text() == "keep\n"


@pytest.mark.parametrize(
    "value, marker",
    [
        (str(render_app.ROOT / "spec/vectors/model.yaml"), "local path marker"),
        ("-----BEGIN PRIVATE KEY-----", "credential marker"),
        ("AKIA1234567890ABCDEF", "credential marker"),
    ],
)
def test_public_json_guard_rejects_local_paths_and_credentials(
    tmp_path: Path,
    value: str,
    marker: str,
) -> None:
    with pytest.raises(RuntimeError, match=marker):
        render_app._write_json(tmp_path / "public.json", {"value": value})
