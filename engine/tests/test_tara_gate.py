"""Synthetic approvals exercise the pilot; the repository's draft stays unchanged."""

import copy
from pathlib import Path

import pytest
import yaml

from engine import core
from engine.graph import GraphError

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "models/tcu/governance.yaml"
GATE = ROOT / "prototype/185-tara-gate/gate.yaml"
CURRENT = "git-tree:" + "a" * 40


@pytest.fixture
def gate():
    return yaml.safe_load(GATE.read_text())


@pytest.fixture
def approved():
    doc = yaml.safe_load(RECORD.read_text())
    version = doc["threat_models"][0]
    agents = {p["id"] for p in doc["parties"] if p["party_kind"] == "software_agent"}
    doc["reviews"] = [r for r in doc["reviews"] if r["reviewer"] in agents]
    for role in ("owner", "assessor", "approver"):
        doc["reviews"].append(
            {
                "id": f"review:test-{role}",
                "reviews": version["id"],
                "reviewer": f"party:tara-{role}",
                "reviewer_role": role,
                "reviewed_at": "2026-11-20T00:00:00Z",
                "review_outcome": "approved",
                "justification": "Synthetic test approval; not a real review.",
            }
        )
    for comment in doc["review_comments"]:
        comment["comment_status"] = "rejected"
        comment.pop("resolved_by", None)
    version.update(
        governance_status="approved",
        approval_status="approved",
        approved_by=["review:test-approver"],
        approval_digest=CURRENT,
    )
    return doc


def check(gate, doc, *, mode="evidence-chain", current=CURRENT):
    return core.evaluate_tara_gate(gate, doc, current_digest=current, evidence_link=mode)


def test_approved_current_linked_tara_passes_without_deciding_gate(gate, approved):
    before = copy.deepcopy((gate, approved))
    result = check(gate, approved)
    assert result["status"] == "passed" and result["reasons"] == []
    assert result["stale"] is False
    assert result["evidence_paths"] == [
        [
            "requirement:tcu-approved-tara",
            "sdl-practice:tcu-threat-modeling",
            "evidence:tcu-tara-v1",
            "threat-model:tcu-tara-v1",
        ]
    ]
    assert result["scope"] == "pilot-recorded-tara-exit-criterion"
    assert (gate, approved) == before and gate["gate_status"] == "planned"


def test_real_draft_fails_and_is_not_approved_by_running_check(gate):
    before = RECORD.read_bytes()
    result = check(gate, yaml.safe_load(before))
    assert result["status"] == "failed"
    assert "version is not recorded as approved in both status fields" in result["reasons"]
    assert RECORD.read_bytes() == before


@pytest.mark.parametrize("slot", ["governance_status", "approval_status"])
def test_both_status_fields_must_agree(gate, approved, slot):
    approved["threat_models"][0][slot] = "pending" if slot == "approval_status" else "draft"
    assert check(gate, approved)["status"] == "failed"


def test_missing_required_human_review_fails(gate, approved):
    approved["reviews"] = [r for r in approved["reviews"] if r.get("reviewer_role") != "assessor"]
    assert "no assessor approval by a person" in check(gate, approved)["reasons"]


def test_agent_approval_cannot_fill_a_human_role(gate, approved):
    agent = next(p["id"] for p in approved["parties"] if p["party_kind"] == "software_agent")
    for review in approved["reviews"]:
        review["reviewer"] = agent
    result = check(gate, approved)
    assert result["status"] == "failed" and result["latest_person_reviews"] == {}


def test_flags_alone_and_owner_approval_do_not_replace_final_approver(gate, approved):
    approved["threat_models"][0]["approved_by"] = ["review:test-owner"]
    assert (
        "approved_by must include the current human approver's review"
        in check(gate, approved)["reasons"]
    )


def test_review_of_another_version_cannot_approve_this_one(gate, approved):
    for review in approved["reviews"]:
        review["reviews"] = "threat-model:other-version"
    assert check(gate, approved)["status"] == "failed"


def test_later_changes_request_overrides_older_approval(gate, approved):
    later = copy.deepcopy(approved["reviews"][-1])
    later.update(
        id="review:test-later",
        reviewed_at="2026-11-21T00:00:00Z",
        review_outcome="changes_requested",
    )
    approved["reviews"].append(later)
    assert check(gate, approved)["status"] == "failed"


def test_equal_time_contrary_reviews_fail_independently_of_file_order(gate, approved):
    contrary = copy.deepcopy(approved["reviews"][-1])
    contrary.update(id="review:test-contrary", review_outcome="changes_requested")
    approved["reviews"].append(contrary)
    first = check(gate, approved)
    approved["reviews"].reverse()
    assert check(gate, approved) == first
    assert first["status"] == "failed"


def test_review_times_compare_as_instants_not_lexicographic_strings(gate, approved):
    later = copy.deepcopy(approved["reviews"][-1])
    later.update(
        id="review:test-later",
        reviewed_at="2026-11-19T23:30:00-01:00",
        review_outcome="changes_requested",
    )
    approved["reviews"].append(later)
    assert check(gate, approved)["status"] == "failed"


@pytest.mark.parametrize("pinned", [None, "placeholder", "git-tree:" + "b" * 40])
def test_missing_invalid_or_stale_digest_never_passes(gate, approved, pinned):
    approved["threat_models"][0]["approval_digest"] = pinned
    result = check(gate, approved)
    assert result["status"] == "failed"
    assert result["stale"] == (pinned == "git-tree:" + "b" * 40)


def test_open_comment_blocks_even_with_approvals_and_matching_digest(gate, approved):
    approved["review_comments"][0]["comment_status"] = "open"
    assert check(gate, approved)["status"] == "failed"


def test_unlinked_requirement_does_not_gain_coverage_from_approval(gate, approved):
    approved["sdl_practices"][0]["produces"] = []
    assert check(gate, approved)["status"] == "failed"


def test_evidence_for_another_revision_does_not_count(gate, approved):
    approved["evidence_items"][0]["about_version"] = "2"
    assert check(gate, approved)["status"] == "failed"


def test_direct_route_is_explicit_and_does_not_fall_back_to_evidence_chain(gate, approved):
    assert check(gate, approved, mode="direct")["status"] == "failed"
    approved["requirements"][0]["evidenced_by"] = [gate["validates_conformance_of"]]
    result = check(gate, approved, mode="direct")
    assert result["status"] == "passed"
    assert result["evidence_paths"] == [[gate["gated_by"][0], gate["validates_conformance_of"]]]


@pytest.mark.parametrize(
    "slot,value",
    [("validates_conformance_of", "unknown"), ("gated_by", []), ("gated_by", ["unknown"])],
)
def test_invalid_gate_binding_is_an_input_error(gate, approved, slot, value):
    gate[slot] = value
    with pytest.raises(GraphError):
        check(gate, approved)


def test_mode_and_current_digest_cannot_be_guessed(gate, approved):
    with pytest.raises(GraphError):
        check(gate, approved, mode="auto")
    with pytest.raises(GraphError):
        check(gate, approved, current="placeholder")


def test_approver_cannot_be_removed_from_the_required_roles(gate, approved):
    approved["threat_models"][0]["required_review_roles"] = ["owner"]
    assert check(gate, approved)["status"] == "failed"
