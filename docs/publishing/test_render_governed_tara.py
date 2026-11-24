"""Governed TARA render and publication tests for #182."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from check_links import check_links
from engine.risk import MATRIX_ID
from render_governed_tara import (
    DIGEST_TEMPLATE_FILES,
    EXAMPLE_NOTICE,
    Freshness,
    GateContext,
    GateDecision,
    Records,
    RenderError,
    _relationship_rows,
    current_digest,
    current_gate,
    load_yaml,
    publish,
    render_history,
    render_version,
    site_header,
    site_nav,
)

from engine import core

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "docs" / "publishing" / "test_fixtures" / "tara-governance.yaml"
V1 = "threat-model:tcu-tara-v1"
DIGEST = "git-tree:" + "1" * 40


@pytest.fixture(scope="module")
def intermediate():
    """The real #181 contract, collected from the authoritative example vector."""
    return core.collect_tara("mvp-02-automotive-ecu.yaml", MATRIX_ID)


@pytest.fixture
def governance():
    return copy.deepcopy(load_yaml(FIXTURE))


def current(_record, _governance, version_id):
    return DIGEST if version_id == V1 else None


def allow_gate(_record, _governance, _output_root, _context):
    """Stand in only for #183's outcome; it deliberately contains no gate logic."""
    return GateDecision()


def deny_gate(message):
    def gate(_record, _governance, _output_root, _context):
        return GateDecision(errors=(message,))

    return gate


def page(intermediate, governance, freshness=None):
    freshness = freshness or Freshness(DIGEST, DIGEST)
    return render_version(
        intermediate, governance, governance["threat_models"][0], freshness
    )


def test_actual_intermediate_renders_in_required_section_order(
    intermediate, governance
):
    html = page(intermediate, governance)
    positions = [
        html.index(f'id="{section}"')
        for section in (
            "item",
            "assets",
            "threats",
            "impact",
            "paths",
            "feasibility",
            "risk",
            "treatment",
            "requirements",
            "governance",
        )
    ]
    assert positions == sorted(positions)
    assert "product:telematics-control-unit" in html
    assert "risk-score:remote-diag-injection" in html
    assert "annex-h-table-h8" in html


def test_missing_proposed_rejected_reviewed_and_incomplete_information_is_explicit(
    intermediate, governance
):
    html = page(intermediate, governance)
    assert "Proposed assertion — rejected" in html
    assert "Proposed assertion — not accepted" in html
    assert "Accepted assertion — human reviewed" in html
    assert "Related assertion accepted; record not approved" in html
    assert "Incomplete" in html
    assert "reduce (RQ-15-17)" in html
    assert "Authored narrative; no structured schema field." in html
    assert html.count("No authored treatment decision recorded") == 1
    assert "assertion:ai-req-addresses-pivot" in html


def test_governance_keeps_human_and_ai_reviews_distinct(intermediate, governance):
    html = page(intermediate, governance)
    assert "Human review record." in html
    assert "AI agent" in html
    assert "Does not count as human approval." in html
    assert "An accepted review of one Assertion does not approve" in html
    assert "Resolved fixture review comment" in html
    assert "threat-model:tcu-tara-v2" in html
    assert "supersedes" in html.lower()


def test_html_is_escaped_and_unapproved_identity_is_withheld(intermediate, governance):
    altered = copy.deepcopy(intermediate)
    altered["records"]["products"][0]["data"]["name"] = '<script>alert("x")</script>'
    governance["review_comments"][0]["description"] = "<b>not markup</b>"
    html = page(altered, governance)
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html
    assert "<b>not markup</b>" not in html
    assert "&lt;b&gt;not markup&lt;/b&gt;" in html
    assert "@private-reviewer" not in html
    assert "approver role" in html


def test_render_is_deterministic(intermediate, governance):
    assert page(intermediate, governance) == page(intermediate, governance)
    assert EXAMPLE_NOTICE in page(intermediate, governance)
    assert str(ROOT) not in page(intermediate, governance)


def test_version_members_bound_primary_content(intermediate, governance):
    html = page(intermediate, governance)
    requirements = html[
        html.index("<caption>Security requirements</caption>") : html.index(
            "</table>", html.index("<caption>Security requirements</caption>")
        )
    ]
    mitigations = html[
        html.index("<caption>Mitigations</caption>") : html.index(
            "</table>", html.index("<caption>Mitigations</caption>")
        )
    ]
    assert "requirement:tcu-diag-authentication" in requirements
    assert "requirement:gateway-filter-safety-can" in requirements
    assert "requirement:family-authenticated-diagnostics" not in requirements
    assert "requirement:iso21434-rq-05-17" not in requirements
    assert "requirement:iso21434-rq-08-07" not in requirements
    assert "requirement:iso21434-rq-09-09" not in requirements
    assert "mitigation:family-authenticated-diagnostics" not in mitigations
    assert "Item components and referenced context" in html
    assert "Referenced context; not a governed member" in html
    assert "Referenced context; not a governed member." in html


def test_missing_version_member_is_rejected(intermediate, governance):
    governance["threat_models"][0]["members"].append("requirement:not-collected")
    with pytest.raises(RenderError, match="members missing from the TARA intermediate"):
        page(intermediate, governance)


def test_navigation_and_digest_dependencies_are_canonical(intermediate, governance):
    assert site_header(4) == site_nav.header(4, "")
    assert site_header(4) in page(intermediate, governance)
    assert DIGEST_TEMPLATE_FILES == {
        "docs/publishing/render_governed_tara.py",
        "docs/publishing/render_tara.py",
        "docs/publishing/site.yaml",
        "docs/publishing/site_nav.py",
        "publishing/identities.yaml",
    }


def test_digest_interface_treats_incomplete_or_invalid_results_as_unknown(
    governance, monkeypatch
):
    incomplete = SimpleNamespace(
        TEMPLATE=("docs/publishing/render_governed_tara.py",),
        digest=lambda *_: DIGEST,
    )
    monkeypatch.setitem(sys.modules, "input_digest", incomplete)
    assert current_digest(FIXTURE, governance, V1) is None

    invalid = SimpleNamespace(
        TEMPLATE=tuple(DIGEST_TEMPLATE_FILES),
        digest=lambda *_: "not-a-#183-digest",
    )
    monkeypatch.setitem(sys.modules, "input_digest", invalid)
    assert current_digest(FIXTURE, governance, V1) is None


def test_requirement_relationships_preserve_collector_provenance(
    intermediate, governance
):
    altered = copy.deepcopy(intermediate)
    base = {
        "subject": "requirement:tcu-diag-authentication",
        "predicate": "satisfied_by",
        "object": "mitigation:authenticate-diag-service",
        "origin": "assertion",
    }
    for suffix, status, reviewed in (
        ("proposed", "proposed", False),
        ("rejected", "rejected", True),
        ("accepted", "accepted", True),
    ):
        altered["requirement_links"].append(
            {
                **base,
                "assertion_id": f"assertion:fixture-{suffix}",
                "review_state": {
                    "scope": "assertion",
                    "status": status,
                    "reviewed": reviewed,
                },
            }
        )
    records = Records(altered)
    members = frozenset(governance["threat_models"][0]["members"])
    rows = _relationship_rows(records, altered, members)
    rendered = "\n".join(" ".join(row) for row in rows)
    assert "assertion:fixture-proposed" in rendered
    assert "Proposed assertion — not accepted" in rendered
    assert "assertion:fixture-rejected" in rendered
    assert "Rejected assertion" in rendered
    assert "assertion:fixture-accepted" in rendered
    assert "Accepted assertion — human reviewed" in rendered
    slot_rows = [
        row
        for row in rows
        if "requirement:tcu-diag-authentication" in row[0]
        and row[1] == "satisfied by"
        and "mitigation:authenticate-diag-service" in row[2]
        and row[3] == "source slot"
    ]
    assert len(slot_rows) == 1


@pytest.mark.parametrize(
    "gate_error",
    (
        "required review missing: no assessor review by a person",
        "only an AI review approves it",
        "comment comment:open is open",
        "@reviewer requests changes on the PR",
        "#180 governance validation: invalid record",
    ),
)
def test_authoritative_gate_failures_never_write_pages(
    tmp_path, intermediate, governance, gate_error
):
    out = tmp_path / "docs/models/tcu/tara"
    with pytest.raises(RenderError, match="governed TARA publication blocked") as error:
        publish(
            intermediate,
            governance,
            record=FIXTURE,
            output_root=out,
            digest_resolver=current,
            gate_resolver=deny_gate(gate_error),
        )
    assert gate_error in str(error.value)
    assert not out.exists()


def test_missing_authoritative_gate_fails_closed(
    tmp_path, intermediate, governance, monkeypatch
):
    monkeypatch.setitem(sys.modules, "check_governance", None)
    monkeypatch.setitem(sys.modules, "check_publish", None)
    out = tmp_path / "docs/models/tcu/tara"
    with pytest.raises(RenderError, match="#180/#183 governance gate unavailable"):
        publish(
            intermediate,
            governance,
            record=FIXTURE,
            output_root=out,
            digest_resolver=current,
        )
    assert not out.exists()


def test_authoritative_gate_adapter_uses_180_and_183_interfaces(
    tmp_path, governance, monkeypatch
):
    calls = {}
    reviews_path = tmp_path / "reviews.json"
    reviews_path.write_text("[]", encoding="utf-8")

    def check_file(record):
        calls["validated"] = record
        return []

    def check_record(record, doc, **kwargs):
        calls["record"] = record
        calls["doc"] = doc
        calls["gate"] = kwargs
        return SimpleNamespace(errors=[], notes=[])

    monkeypatch.setitem(
        sys.modules, "check_governance", SimpleNamespace(check_file=check_file)
    )
    monkeypatch.setitem(
        sys.modules,
        "check_publish",
        SimpleNamespace(
            read_reviews=lambda path: [{"path": str(path)}],
            pr_verdicts=lambda reviews, head, author: {
                "codeowner": f"APPROVED:{reviews[0]['path']}:{head}:{author}"
            },
            pages_dir=lambda _record, number: f"docs/models/tcu/tara/v{number}/",
            _base_doc=lambda _record, base: {"base": base},
            check_record=check_record,
        ),
    )
    out = tmp_path / "docs/models/tcu/tara"
    decision = current_gate(
        FIXTURE,
        governance,
        out,
        GateContext(
            pr_reviews=reviews_path,
            head="head-sha",
            author="author",
            base="origin/main",
            changed=("models/tcu/governance.yaml",),
        ),
    )
    assert decision == GateDecision()
    assert calls["validated"] == FIXTURE
    assert calls["record"] == FIXTURE
    assert calls["doc"] == governance
    assert calls["gate"]["base_doc"] == {"base": "origin/main"}
    assert calls["gate"]["verdicts"]["codeowner"].endswith(":head-sha:author")
    assert calls["gate"]["changed"] == [
        "models/tcu/governance.yaml",
        "docs/models/tcu/tara/v1/index.html",
    ]


def test_first_publish_writes_only_approved_v1_latest_and_history(
    tmp_path, intermediate, governance
):
    out = tmp_path / "docs" / "models" / "tcu" / "tara"
    result = publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    assert [path.relative_to(out).as_posix() for path in result.created] == [
        "v1/index.html"
    ]
    assert (out / "latest/index.html").is_file()
    assert (out / "history.html").is_file()
    assert not (out / "v2").exists()
    latest = (out / "latest/index.html").read_text()
    history = (out / "history.html").read_text()
    assert "TCU TARA, fixture version 1" in latest
    assert "v2 (not published)" in history
    assert "comment:tcu-v2-open" in history
    assert 'href="v1/"' in history
    assert EXAMPLE_NOTICE in latest and EXAMPLE_NOTICE in history


def test_repeated_publish_never_overwrites_v1_and_refreshes_stale_views(
    tmp_path, intermediate, governance
):
    out = tmp_path / "docs/models/tcu/tara"
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    historical = out / "v1/index.html"
    before = historical.read_bytes()
    historical_text = before.decode()
    assert "matched at publication" in historical_text
    assert "freshness: <strong>current</strong>" not in historical_text
    changed_intermediate = copy.deepcopy(intermediate)
    changed_intermediate["records"]["products"][0]["data"]["name"] = (
        "Changed draft item"
    )

    def changed(_record, _governance, _version_id):
        return "git-tree:" + "2" * 40

    result = publish(
        changed_intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=changed,
        gate_resolver=allow_gate,
    )
    assert historical.read_bytes() == before
    assert historical in result.preserved
    latest = (out / "latest/index.html").read_text()
    assert "STALE TARA" in latest
    assert "freshness: <strong>stale</strong>" in latest
    assert "freshness: <strong>current</strong>" not in latest
    assert "Input digest matches the approved version" not in latest
    assert "Changed draft item" not in latest
    assert "STALE TARA" in (out / "history.html").read_text()


def test_missing_current_digest_refreshes_latest_to_unknown_without_touching_v1(
    tmp_path, intermediate, governance
):
    out = tmp_path / "docs/models/tcu/tara"
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    historical = out / "v1/index.html"
    before = historical.read_bytes()
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=lambda *_: None,
        gate_resolver=allow_gate,
    )
    assert historical.read_bytes() == before
    latest = (out / "latest/index.html").read_text()
    assert "Freshness not verified" in latest
    assert "freshness: <strong>unknown</strong>" in latest
    assert "freshness: <strong>current</strong>" not in latest


def test_repeated_unchanged_publish_is_a_no_op(tmp_path, intermediate, governance):
    out = tmp_path / "docs/models/tcu/tara"
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    snapshot = {
        path.relative_to(out): path.read_bytes() for path in out.rglob("*.html")
    }
    second = publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    assert second.created == []
    assert second.refreshed == []
    assert second.preserved == [out / "v1/index.html"]
    assert snapshot == {
        path.relative_to(out): path.read_bytes() for path in out.rglob("*.html")
    }


def test_first_publish_refuses_missing_or_stale_digest(
    tmp_path, intermediate, governance
):
    for value in (None, "git-tree:" + "2" * 40):
        with pytest.raises(RenderError, match="refusing first publication"):
            publish(
                intermediate,
                governance,
                record=FIXTURE,
                output_root=tmp_path / str(value),
                digest_resolver=lambda *_args, value=value: value,
                gate_resolver=allow_gate,
            )


def test_newest_approved_version_becomes_latest(tmp_path, intermediate, governance):
    v3 = copy.deepcopy(governance["threat_models"][0])
    v3.update(
        id="threat-model:tcu-tara-v3",
        name="TCU TARA, fixture version 3",
        revision="3",
        supersedes=V1,
        approval_digest="git-tree:" + "3" * 40,
    )
    governance["threat_models"].append(v3)
    out = tmp_path / "docs/models/tcu/tara"

    def digests(_record, _governance, version_id):
        return {V1: DIGEST, v3["id"]: v3["approval_digest"]}.get(version_id)

    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=digests,
        gate_resolver=allow_gate,
    )
    assert (out / "v1/index.html").is_file()
    assert (out / "v3/index.html").is_file()
    assert not (out / "v2").exists()
    assert "fixture version 3" in (out / "latest/index.html").read_text()


def test_all_draft_record_publishes_nothing(tmp_path, intermediate, governance):
    for version in governance["threat_models"]:
        version["governance_status"] = "draft"
    out = tmp_path / "docs/models/tcu/tara"
    result = publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=lambda *_: None,
        gate_resolver=allow_gate,
    )
    assert not out.exists()
    assert result.notes == [
        "no approved governance version; no governed TARA was published"
    ]


def test_unapproved_existing_directory_is_never_linked_or_accepted(
    tmp_path, intermediate, governance
):
    out = tmp_path / "docs/models/tcu/tara"
    draft_page = out / "v2/index.html"
    draft_page.parent.mkdir(parents=True)
    draft_page.write_text("not a publication", encoding="utf-8")
    history = render_history(
        governance,
        out,
        {V1: Freshness(DIGEST, DIGEST)},
        governance["threat_models"][0],
    )
    assert 'href="v2/"' not in history
    assert "v2 (not published)" in history
    with pytest.raises(RenderError, match="unapproved version.*publication path"):
        publish(
            intermediate,
            governance,
            record=FIXTURE,
            output_root=out,
            digest_resolver=current,
            gate_resolver=allow_gate,
        )


def test_generated_links_resolve_and_pages_have_static_structure(
    tmp_path, intermediate, governance
):
    docs = tmp_path / "docs"
    for path in (
        docs / "index.html",
        docs / "bibliography/index.html",
        docs / "reports/index.html",
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<!doctype html><title>fixture</title>", encoding="utf-8")
    out = docs / "models/tcu/tara"
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    assert check_links(docs) == []
    for path in out.rglob("*.html"):
        text = path.read_text()
        assert text.startswith("<!doctype html>")
        assert "<script" not in text


def test_check_mode_reports_refreshable_drift_without_touching_files(
    tmp_path, intermediate, governance
):
    out = tmp_path / "docs/models/tcu/tara"
    publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
    )
    latest = out / "latest/index.html"
    latest.write_text("old\n", encoding="utf-8")
    result = publish(
        intermediate,
        governance,
        record=FIXTURE,
        output_root=out,
        digest_resolver=current,
        gate_resolver=allow_gate,
        check=True,
    )
    assert result.out_of_date == [latest]
    assert latest.read_text() == "old\n"
