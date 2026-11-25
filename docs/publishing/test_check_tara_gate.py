"""Real digest/validator/history adapter; all passing approvals are synthetic."""

import builtins
import copy
import json
import shutil

import check_tara_gate as checker
import pytest
import yaml
from input_digest import ROOT, TEMPLATE, digest

RECORD = ROOT / "models/tcu/governance.yaml"
GATE = ROOT / "prototype/185-tara-gate/gate.yaml"
VERSION = "threat-model:tcu-tara-v1"


@pytest.fixture
def site(tmp_path):
    doc = yaml.safe_load(RECORD.read_text())
    for rel in (
        "models/tcu/governance.yaml",
        "prototype/185-tara-gate/gate.yaml",
        doc["governs"],
        *TEMPLATE,
    ):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    return tmp_path


def inputs(site):
    return site / "models/tcu/governance.yaml", site / "prototype/185-tara-gate/gate.yaml"


def approve_copy(site):
    """Only a scratch copy: never approve or resolve the checked-in example."""
    record, _ = inputs(site)
    doc = yaml.safe_load(record.read_text())
    agents = {p["id"] for p in doc["parties"] if p["party_kind"] == "software_agent"}
    doc["reviews"] = [r for r in doc["reviews"] if r["reviewer"] in agents]
    for role in ("owner", "assessor", "approver"):
        doc["reviews"].append(
            {
                "id": f"review:test-{role}",
                "reviews": VERSION,
                "reviewer": f"party:tara-{role}",
                "reviewer_role": role,
                "reviewed_at": "2026-11-20T00:00:00Z",
                "review_outcome": "approved",
                "justification": "Synthetic approval for the test only.",
            }
        )
    for comment in doc["review_comments"]:
        comment["comment_status"] = "rejected"
        comment.pop("resolved_by", None)
    doc["threat_models"][0].update(
        governance_status="approved",
        approval_status="approved",
        approved_by=["review:test-approver"],
    )
    doc["threat_models"][0]["approval_digest"] = digest(record, doc, VERSION, site)
    record.write_text(yaml.safe_dump(doc, sort_keys=False))
    return doc


def assess(site):
    record, gate = inputs(site)
    return checker.assess(record, gate, evidence_link="evidence-chain", root=site)


def test_human_approved_current_scratch_version_passes(site):
    approve_copy(site)
    before = [path.read_bytes() for path in inputs(site)]
    result = assess(site)
    assert result["status"] == "passed" and result["stale"] is False
    assert [path.read_bytes() for path in inputs(site)] == before


@pytest.mark.parametrize("rel", ["spec/vectors/mvp-02-automotive-ecu.yaml", *TEMPLATE])
def test_actual_input_change_fails_even_though_approval_record_is_unchanged(site, rel):
    approve_copy(site)
    path = site / rel
    path.write_bytes(path.read_bytes() + b"\n# changed after approval\n")
    result = assess(site)
    assert result["status"] == "failed" and result["stale"] is True
    assert "inputs changed after approval" in result["reasons"]


def test_draft_is_unmet_even_though_publish_gate_allows_an_unpublished_draft(site):
    result = assess(site)
    assert result["status"] == "failed"
    assert "version is not recorded as approved in both status fields" in result["reasons"]


def test_reading_outside_repository_or_through_external_symlink_is_refused(site, tmp_path):
    record, gate = inputs(site)
    outside = tmp_path.parent / (tmp_path.name + "-outside.yaml")
    outside.write_text(RECORD.read_text())
    alias = site / "external.yaml"
    alias.symlink_to(outside)
    for candidate in (outside, alias):
        with pytest.raises(ValueError, match="outside the repository"):
            checker.assess(candidate, gate, evidence_link="evidence-chain", root=site)


def test_invalid_record_and_unavailable_input_cannot_pass(site):
    record, _ = inputs(site)
    doc = yaml.safe_load(record.read_text())
    doc["threat_models"][0]["governance_status"] = "not-a-status"
    record.write_text(yaml.safe_dump(doc))
    with pytest.raises(ValueError, match="invalid governance record"):
        assess(site)


def test_template_symlink_cannot_read_outside_the_repository(site):
    outside = site.parent / (site.name + "-template.txt")
    outside.write_text("outside input")
    template = site / TEMPLATE[0]
    template.unlink()
    template.symlink_to(outside)
    with pytest.raises(ValueError, match="outside the repository"):
        assess(site)


def test_history_fragment_escapes_values_and_does_not_claim_gate_approval(site):
    result = assess(site)
    result["reasons"] = ['<script>alert("x")</script>']
    page = checker.render_history_status(result)
    assert "Not met" in page and "Example data" in page and "Pilot proposal" in page
    assert "<script>" not in page and "&lt;script&gt;" in page
    assert "Does not approve a Gate" in page
    assert "party:" not in page


def args(site):
    record, gate = inputs(site)
    return [str(record), "--gate", str(gate), "--evidence-link", "evidence-chain", "--json"]


def test_cli_pass_fail_and_local_history_preview(site, monkeypatch, capsys):
    monkeypatch.setattr(checker, "ROOT", site)
    output = site / "history-preview.html"
    assert checker.main(args(site) + ["--preview", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "failed"
    assert "Not met" in output.read_text()
    approve_copy(site)
    assert checker.main(args(site)) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "passed"


def test_preview_never_overwrites_existing_file_or_writes_under_published_docs(site, monkeypatch):
    monkeypatch.setattr(checker, "ROOT", site)
    output = site / "existing.html"
    output.write_text("keep")
    assert checker.main(args(site) + ["--preview", str(output)]) == 2
    assert output.read_text() == "keep"
    public = site / "docs/history.html"
    assert checker.main(args(site) + ["--preview", str(public)]) == 2
    assert not public.exists()


def test_cli_requires_an_explicit_evidence_route(site):
    record, gate = inputs(site)
    with pytest.raises(SystemExit) as error:
        checker.main([str(record), "--gate", str(gate)])
    assert error.value.code == 2


def test_missing_schema_tools_is_an_input_error_not_a_criterion_verdict(site, monkeypatch, capsys):
    original = builtins.__import__

    def without_validator(name, *positional, **keywords):
        if name == "linkml.validator":
            raise ImportError("missing validation tools")
        return original(name, *positional, **keywords)

    monkeypatch.setattr(checker, "ROOT", site)
    monkeypatch.setattr(builtins, "__import__", without_validator)
    assert checker.main(args(site)) == 2
    captured = capsys.readouterr()
    assert not captured.out and "spec/schema/requirements.txt" in captured.err


def test_result_does_not_depend_on_run_or_machine_paths(site):
    approve_copy(site)
    result = assess(site)
    assert assess(site) == copy.deepcopy(result)
    assert str(site) not in json.dumps(result)
