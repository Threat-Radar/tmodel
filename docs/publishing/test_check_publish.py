import copy
import json
import shutil

import pytest
import yaml
from check_publish import ROOT, _owns, check_record, code_owners, main, pr_verdicts, read_reviews
from input_digest import TEMPLATE, digest

RECORD = ROOT / "models" / "tcu" / "governance.yaml"
V1 = "threat-model:tcu-tara-v1"
HEAD = "a" * 40
OWNERS = "*  @student-a @student-b\n/spec/  @sponsor\n"


@pytest.fixture
def site(tmp_path):
    """A scratch root with the TARA's inputs and a CODEOWNERS file."""
    record = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    for rel in (record["governs"], *TEMPLATE):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, tmp_path / rel)
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "CODEOWNERS").write_text(OWNERS, encoding="utf-8")
    (tmp_path / "models" / "tcu").mkdir(parents=True)
    return tmp_path


def approved(site):
    """Version 1 as a person in each role would approve it, its comment resolved."""
    doc = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    doc["reviews"] = [r for r in doc["reviews"] if r["id"] == "review:tcu-tara-v1-claude-code"]
    for role in ("owner", "assessor", "approver"):
        doc["reviews"].append(
            {
                "id": f"review:tcu-tara-v1-{role}",
                "reviews": V1,
                "reviewer": f"party:tara-{role}",
                "reviewer_role": role,
                "reviewed_at": "2026-11-20T00:00:00Z",
                "review_outcome": "approved",
                "justification": "test",
            }
        )
    comment = next(c for c in doc["review_comments"] if c["id"] == "comment:tcu-tara-v1-dec-003")
    comment.update(comment_status="resolved", resolved_by="https://example.invalid/pr/1")
    v1 = doc["threat_models"][0]
    v1.update(
        governance_status="approved",
        approval_status="approved",
        approved_by=["review:tcu-tara-v1-approver"],
    )
    v1["approval_digest"] = digest(site / "models/tcu/governance.yaml", doc, V1, site)
    return doc


def gate(site, doc, *, base=None, verdicts=None, changed=()):
    path = site / "models" / "tcu" / "governance.yaml"
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return check_record(
        path,
        doc,
        base_doc=base,
        verdicts={"student-a": "APPROVED"} if verdicts is None else verdicts,
        changed=changed,
        codeowners=site / ".github" / "CODEOWNERS",
        root=site,
    )


def review(doc, role):
    return next(r for r in doc["reviews"] if r.get("reviewer_role") == role)


# --- the passing case ---------------------------------------------------------------------------


def test_a_properly_approved_version_passes(site):
    result = gate(site, approved(site))
    assert result.errors == []


def test_todays_draft_is_not_published_so_nothing_is_gated(site):
    doc = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    result = gate(site, doc, verdicts={})
    assert result.errors == [] and result.notes == [f"{V1}: draft, not published"]


# --- 1. a required review is missing -------------------------------------------------------------


def test_a_missing_role_blocks(site):
    doc = approved(site)
    doc["reviews"].remove(review(doc, "assessor"))
    assert gate(site, doc).errors == [
        f"{V1}: required review missing: no assessor review by a person"
    ]


def test_a_role_whose_latest_review_is_not_an_approval_blocks(site):
    doc = approved(site)
    later = copy.deepcopy(review(doc, "owner")) | {
        "id": "review:tcu-tara-v1-owner-2",
        "reviewed_at": "2026-11-21T00:00:00Z",
        "review_outcome": "changes_requested",
    }
    doc["reviews"].append(later)
    assert gate(site, doc).errors == [
        f"{V1}: the owner review (review:tcu-tara-v1-owner-2) is changes_requested, not approved"
    ]


# --- 2. only an AI review approves ---------------------------------------------------------------


def test_an_ai_approval_alone_blocks(site):
    doc = approved(site)
    doc["reviews"] = [r for r in doc["reviews"] if r["reviewer"] == "party:claude-code"]
    doc["reviews"][0]["review_outcome"] = "approved"
    errors = gate(site, doc).errors
    assert f"{V1}: only an AI review approves it (DL-0027 rule 1)" in errors
    assert f"{V1}: required review missing: no approver review by a person" in errors


def test_an_ai_review_cannot_fill_a_role(site):
    doc = approved(site)
    doc["reviews"].remove(review(doc, "approver"))
    doc["reviews"][0] |= {"reviewer_role": "approver", "review_outcome": "approved"}
    assert gate(site, doc).errors == [
        f"{V1}: required review missing: no approver review by a person"
    ]


# --- 3. a comment is open ------------------------------------------------------------------------


@pytest.mark.parametrize("on", [V1, "review:tcu-tara-v1-claude-code"])
def test_an_open_comment_on_the_version_or_its_review_blocks(site, on):
    doc = approved(site)
    doc["review_comments"].append(
        {"id": "comment:new", "comment_on": on, "comment_status": "open", "name": "x"}
    )
    assert gate(site, doc).errors == [f"{V1}: comment comment:new is open"]


def test_a_rejected_comment_does_not_block(site):
    doc = approved(site)
    doc["review_comments"].append(
        {"id": "comment:new", "comment_on": V1, "comment_status": "rejected", "name": "x"}
    )
    assert gate(site, doc).errors == []


# --- 4. the record and the PR disagree -----------------------------------------------------------


def test_the_record_approves_but_no_code_owner_approves_the_pr(site):
    errors = gate(site, approved(site), verdicts={"sponsor": "APPROVED"}).errors
    assert errors == [
        f"{V1}: the record approves it, but no code owner of models/tcu/governance.yaml "
        "(@student-a, @student-b) approves the PR at its head commit"
    ]


def test_the_record_approves_but_a_reviewer_requests_changes(site):
    verdicts = {"student-a": "APPROVED", "student-b": "CHANGES_REQUESTED"}
    assert gate(site, approved(site), verdicts=verdicts).errors == [
        f"{V1}: the record approves it, but @student-b requests changes on the PR"
    ]


def test_pages_for_a_version_the_record_does_not_approve_block(site):
    doc = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    (site / "docs/models/tcu/tara/v1").mkdir(parents=True)
    errors = gate(site, doc).errors
    assert errors[0] == (
        f"{V1}: has pages under docs/models/tcu/tara/v1/, but the record does not approve it "
        "(governance_status: draft)"
    )


def test_an_approval_given_before_the_last_push_does_not_count():
    reviews = [
        {
            "user": {"login": "student-a"},
            "state": "APPROVED",
            "commit_id": "b" * 40,
            "submitted_at": "2026-11-20T00:00:00Z",
        },
    ]
    assert pr_verdicts(reviews, HEAD) == {"student-a": "STALE"}


def test_pr_verdicts_follow_githubs_rules():
    reviews = [
        {"user": {"login": "a"}, "state": "APPROVED", "commit_id": HEAD, "submitted_at": "1"},
        {"user": {"login": "a"}, "state": "COMMENTED", "commit_id": HEAD, "submitted_at": "2"},
        {"user": {"login": "b"}, "state": "APPROVED", "commit_id": HEAD, "submitted_at": "1"},
        {"user": {"login": "b"}, "state": "DISMISSED", "commit_id": HEAD, "submitted_at": "2"},
        {"user": {"login": "bot", "type": "Bot"}, "state": "APPROVED", "commit_id": HEAD},
        {"user": {"login": "author"}, "state": "APPROVED", "commit_id": HEAD},
    ]
    assert pr_verdicts(reviews, HEAD, "author") == {"a": "APPROVED", "b": "DISMISSED"}


# --- 5. the inputs changed after approval --------------------------------------------------------


def test_an_input_changed_after_approval_blocks_the_version_being_published(site):
    doc = approved(site)
    with (site / doc["governs"]).open("ab") as f:
        f.write(b"\n# edited after approval\n")
    [error] = gate(site, doc).errors
    assert error.startswith(f"{V1}: approval_digest git-tree:") and "inputs changed" in error


def test_a_version_approved_earlier_is_only_reported_stale(site):
    doc = approved(site)
    with (site / doc["governs"]).open("ab") as f:
        f.write(b"\n# edited after approval\n")
    result = gate(site, doc, base=copy.deepcopy(doc), verdicts={})
    assert result.errors == []
    assert any(n.startswith(f"{V1}: STALE") for n in result.notes)


def test_a_version_approved_earlier_is_gated_again_when_its_pages_change(site):
    doc = approved(site)
    (site / "docs/models/tcu/tara/v1").mkdir(parents=True)
    result = gate(
        site,
        doc,
        base=copy.deepcopy(doc),
        verdicts={},
        changed=["docs/models/tcu/tara/v1/index.html"],
    )
    assert any("no code owner" in e for e in result.errors)


def test_an_approved_version_needs_a_digest(site):
    doc = approved(site)
    del doc["threat_models"][0]["approval_digest"]
    assert gate(site, doc).errors == [f"{V1}: approved but has no approval_digest"]


# --- CODEOWNERS and the command ------------------------------------------------------------------


@pytest.mark.parametrize(
    "pattern, path, owns",
    [
        ("*", "models/tcu/governance.yaml", True),
        ("/spec/", "spec/vectors/x.yaml", True),
        ("/spec/", "docs/spec/x.yaml", False),
        ("docs/models/", "docs/models/tcu/tara/v1/index.html", True),
        ("*.yaml", "models/tcu/governance.yaml", True),
        ("models/*.yaml", "models/tcu/governance.yaml", False),
        ("models/**/governance.yaml", "models/tcu/governance.yaml", True),
    ],
)
def test_codeowners_patterns_match_as_github_reads_them(pattern, path, owns):
    assert _owns(pattern, path) is owns


def test_the_last_matching_codeowners_line_wins(tmp_path):
    owners = tmp_path / "CODEOWNERS"
    owners.write_text("*  @a @b\n/models/  @c  # the sponsor\n", encoding="utf-8")
    assert code_owners("models/tcu/governance.yaml", owners) == ["c"]
    assert code_owners("docs/x.md", owners) == ["a", "b"]


def test_reviews_are_read_as_an_array_or_as_lines(tmp_path):
    one = {"user": {"login": "a"}, "state": "APPROVED"}
    (tmp_path / "array.json").write_text(json.dumps([one, one]), encoding="utf-8")
    (tmp_path / "lines.json").write_text(json.dumps(one) + "\n" + json.dumps(one), encoding="utf-8")
    assert (
        read_reviews(tmp_path / "array.json") == read_reviews(tmp_path / "lines.json") == [one, one]
    )


def test_the_command_passes_on_the_repo_today(tmp_path, capsys):
    reviews = tmp_path / "reviews.json"
    reviews.write_text("[]", encoding="utf-8")
    assert main(["--pr-reviews", str(reviews), "--head", HEAD]) == 0
    assert "models/tcu/governance.yaml: ok" in capsys.readouterr().out
