import copy
from pathlib import Path

import pytest
import yaml
from check_governance import ROOT, check_file, check_rules, check_schema

RECORD = ROOT / "models" / "tcu" / "governance.yaml"
MODEL = ROOT / "spec" / "vectors" / "mvp-02-automotive-ecu.yaml"


@pytest.fixture
def record():
    return yaml.safe_load(RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def model():
    return yaml.safe_load(MODEL.read_text(encoding="utf-8"))


def by_id(doc, collection, oid):
    return next(i for i in doc[collection] if i["id"] == oid)


# --- the schema pass (#180: a missing field and a bad enum value fail) ------------------------


def test_the_tcu_record_passes_both_passes():
    pytest.importorskip("linkml")
    assert check_file(RECORD) == []


def test_a_missing_required_field_fails(record):
    pytest.importorskip("linkml")
    del record["review_comments"][0]["comment_status"]
    assert any("'comment_status' is a required property" in e for e in check_schema(record))


def test_a_bad_enum_value_fails(record):
    pytest.importorskip("linkml")
    record["reviews"][0]["review_outcome"] = "lgtm"
    assert any("'lgtm' is not one of" in e for e in check_schema(record))


def test_a_review_of_a_version_needs_its_target(record):
    pytest.importorskip("linkml")
    del record["reviews"][1]["reviews"]
    assert any("'reviews' is a required property" in e for e in check_schema(record))


def test_a_missing_governs_file_fails(record, tmp_path: Path):
    pytest.importorskip("linkml")
    record["governs"] = "spec/vectors/no-such-model.yaml"
    path = tmp_path / "governance.yaml"
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    assert "governs 'spec/vectors/no-such-model.yaml': no such file in the repo" in check_file(path)


# --- the rules ----------------------------------------------------------------------------------


def test_the_tcu_record_passes_the_rules(record, model):
    assert check_rules(record, model) == []


def test_an_ai_review_fills_no_role_and_names_its_run(record, model):
    ai = by_id(record, "reviews", "review:tcu-tara-v1-claude-code")
    ai["reviewer_role"] = "approver"
    del ai["agent_run_id"]
    errors = check_rules(record, model)
    assert (
        "review:tcu-tara-v1-claude-code: an AI agent's review fills no role (DL-0027 rule 1)"
        in errors
    )
    assert "review:tcu-tara-v1-claude-code: an AI agent's review needs agent_run_id" in errors


def test_a_persons_review_of_a_version_fills_a_role_and_names_no_model(record, model):
    person = by_id(record, "reviews", "review:tcu-tara-v1-owner-example")
    del person["reviewer_role"]
    person["agent_model"] = "claude-opus-5-5"
    errors = check_rules(record, model)
    assert (
        "review:tcu-tara-v1-owner-example: "
        "a person's review of a governed version needs reviewer_role" in errors
    )
    assert (
        "review:tcu-tara-v1-owner-example: a person's review names no agent model or run" in errors
    )


def test_an_organization_cannot_review(record, model):
    record["parties"].append({"id": "party:oem", "party_kind": "organization"})
    by_id(record, "reviews", "review:tcu-tara-v1-owner-example")["reviewer"] = "party:oem"
    assert (
        "review:tcu-tara-v1-owner-example: reviewer's party_kind is organization; "
        "a review is by a person or a software agent" in check_rules(record, model)
    )


def test_a_review_of_a_version_needs_an_outcome(record, model):
    del by_id(record, "reviews", "review:tcu-tara-v1-claude-code")["review_outcome"]
    assert (
        "review:tcu-tara-v1-claude-code: a review of a governed version needs review_outcome"
        in check_rules(record, model)
    )


def test_a_resolved_comment_names_its_fix_and_only_then(record, model):
    by_id(record, "review_comments", "comment:tcu-tara-v1-assets").pop("resolved_by")
    by_id(record, "review_comments", "comment:tcu-tara-v1-dec-003")["resolved_by"] = (
        "https://example.invalid/pr/1"
    )
    errors = check_rules(record, model)
    assert "comment:tcu-tara-v1-assets: resolved, but names no resolved_by" in errors
    assert "comment:tcu-tara-v1-dec-003: has resolved_by but is open" in errors


def test_references_resolve_to_the_right_kind(record, model):
    by_id(record, "reviews", "review:tcu-tara-v1-owner-example")["reviewer"] = "party:nobody"
    by_id(record, "review_comments", "comment:tcu-tara-v1-assets")["comment_on"] = (
        "party:tara-owner"
    )
    by_id(record, "evidence_items", "evidence:tcu-tara-v1")["evidence_of"] = (
        "requirement:tcu-approved-tara"
    )
    errors = check_rules(record, model)
    assert (
        "review:tcu-tara-v1-owner-example: reviewer 'party:nobody' is not in the record" in errors
    )
    assert (
        "comment:tcu-tara-v1-assets: comment_on 'party:tara-owner' is a parties item, "
        "not one of reviews, threat_models, governed_views" in errors
    )
    assert (
        "evidence:tcu-tara-v1: evidence_of 'requirement:tcu-approved-tara' is a requirements item, "
        "not one of threat_models, governed_views" in errors
    )


def test_members_resolve_in_the_governed_model(record, model):
    by_id(record, "threat_models", "threat-model:tcu-tara-v1")["members"].append(
        "threat-instance:not-in-mvp-02"
    )
    assert (
        "threat-model:tcu-tara-v1: members 'threat-instance:not-in-mvp-02' is not in the record "
        "or the model it governs" in check_rules(record, model)
    )
    assert any("is not in the record or the model" in e for e in check_rules(record, None))


def test_an_approved_version_has_a_digest_and_only_peoples_approvals(record, model):
    v1 = by_id(record, "threat_models", "threat-model:tcu-tara-v1")
    v1["governance_status"] = "approved"
    v1["approved_by"] = ["review:tcu-tara-v1-claude-code"]
    errors = check_rules(record, model)
    assert "threat-model:tcu-tara-v1: approved but has no approval_digest" in errors
    approved_by = "threat-model:tcu-tara-v1: approved_by review:tcu-tara-v1-claude-code"
    assert f"{approved_by} is not an `approved` review of this version" in errors
    assert f"{approved_by} is not a person's review (DL-0027 rule 1)" in errors


def test_a_version_supersedes_an_earlier_revision(record, model):
    v1 = by_id(record, "threat_models", "threat-model:tcu-tara-v1")
    v0 = copy.deepcopy(v1) | {"id": "threat-model:tcu-tara-v0", "revision": "2"}
    record["threat_models"].append(v0)
    v1["supersedes"] = "threat-model:tcu-tara-v0"
    v1["revision"] = "one"
    errors = check_rules(record, model)
    assert "threat-model:tcu-tara-v1: revision 'one' is not a whole number" in errors
    v1["revision"] = "1"
    assert "threat-model:tcu-tara-v1: supersedes revision 2, which is not earlier" in check_rules(
        record, model
    )


def test_ids_are_unique(record, model):
    record["reviews"].append(copy.deepcopy(record["reviews"][0]))
    assert "review:tcu-tara-v1-claude-code: id used twice" in check_rules(record, model)
