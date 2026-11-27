"""C7 behavior, independent of #288's physical storage choice."""

from copy import deepcopy

import pytest
from review_support import PRINCIPAL, MemoryWorkspace, review_model

from engine.graph import AttackGraph
from engine.review_service import ReviewService
from engine.review_workspace import ProjectReviewWorkspace, ReviewError, ReviewPrincipal
from engine.risk import MATRIX_ID
from engine.risk_routes import rated_routes


def request(ws, saving=False, revision=None):
    revision = revision or ws.current
    doc = ws.versions[revision]
    route = rated_routes(
        AttackGraph.from_dict(doc),
        "threat:t",
        {p["id"]: p.get("attack_feasibility") for p in doc["attack_paths"]},
    )[0]
    return {
        "model_id": "local:one",
        "expected_revision" if saving else "revision": revision,
        "matrix": MATRIX_ID,
        "threat_id": "threat:t",
        "route_id": route["id"],
    }


def review(verdict="accepted", **kwargs):
    return {
        "assertion_id": "assertion:path",
        "verdict": verdict,
        "rationale": "Test-only human input supplied by the test client.",
        **kwargs,
    }


def test_combined_save_keeps_provenance_and_refreshes_one_revision():
    ws = MemoryWorkspace()
    original = deepcopy(ws.versions["r1"])
    out = ReviewService(ws).save_model_changes(
        {
            **request(ws, True),
            "reviews": [review(annotation="Fixture note")],
            "feasibility": [{"attack_path_id": "path:a", "rating": "high"}],
            "impacts": [
                {
                    "risk_score_id": "risk:r",
                    "damage_scenario_id": "damage:d",
                    "stakeholder_id": "party:reviewer",
                    "values": {"privacy": "major"},
                }
            ],
        },
        PRINCIPAL,
    )
    assert out["revision"] == "r2"
    assert ws.versions["r1"] == original
    saved = ws.versions["r2"]
    assert saved["assertions"] == original["assertions"]
    assert saved["reviews"][0]["reviewer"] == PRINCIPAL.party_id
    assert saved["reviews"][0]["description"] == "Fixture note"
    for view in ("graph", "attack_paths", "risk", "report_data"):
        assert out[view]["revision"] == "r2"
        assert out[view]["model_id"] == "local:one"
    score = out["risk"]["assessments"][0]
    assert score["derived_risk"] == {"safety": 5, "financial": 4, "operational": 3, "privacy": 4}
    assert not score["path_reviewed"]
    assert not out["attack_paths"]["responses"][0]["paths"][0]["review"]["reviewed"]
    assert out["report_data"]["graph"] == out["graph"]


def test_context_exposes_exact_target_provenance_and_permissions():
    ws = MemoryWorkspace()
    out = ReviewService(ws).get_review_context(request(ws), PRINCIPAL)
    assert [a["id"] for a in out["assertions"]] == ["assertion:path"]
    assert out["assertions"][0]["asserted_by"] == "party:agent"
    assert out["permitted_actions"]["submit_review"]
    assert not out["permitted_actions"]["accept_proposal"]
    assert ws.current == "r1"


def test_correction_preserves_previous_revision_and_review_history():
    ws = MemoryWorkspace()
    service = ReviewService(ws)
    service.submit_review({**request(ws, True), "reviews": [review("rejected")]}, PRINCIPAL)
    first = deepcopy(ws.versions["r2"]["reviews"][0])
    service.submit_review(
        {**request(ws, True), "reviews": [review(review_id=first["id"])]}, PRINCIPAL
    )
    assert ws.versions["r2"]["reviews"][0] == first
    context = service.get_review_context(request(ws), PRINCIPAL)
    assert [h["review"]["review_status"] for h in context["history"]] == ["rejected", "accepted"]
    assert context["review_states"][0]["status"] == "proposed"
    assert len(ws.versions["r3"]["reviews"]) == 1


@pytest.mark.parametrize(
    "update",
    [
        {"reviewer_id": "party:other"},
        {"assertion_status": "accepted"},
        {"corrections": {"assertions": []}},
        {"file": "/tmp/unapproved.yaml"},
    ],
)
def test_arbitrary_edits_and_claimed_identity_are_rejected(update):
    ws = MemoryWorkspace()
    with pytest.raises(ReviewError, match="documented fields"):
        ReviewService(ws).save_model_changes(
            {**request(ws, True), "reviews": [review()], **update}, PRINCIPAL
        )
    assert ws.current == "r1"


@pytest.mark.parametrize(
    "principal",
    [
        ReviewPrincipal("party:reviewer", frozenset(), frozenset({"read", "review"})),
        ReviewPrincipal("party:agent", PRINCIPAL.model_ids, PRINCIPAL.actions),
        ReviewPrincipal("party:reviewer", PRINCIPAL.model_ids, frozenset({"read"})),
    ],
)
def test_permissions_are_verified_by_backend(principal):
    ws = MemoryWorkspace()
    with pytest.raises(ReviewError) as err:
        ReviewService(ws).submit_review({**request(ws, True), "reviews": [review()]}, principal)
    assert err.value.code == "permission_denied"
    assert ws.current == "r1"


def test_bundled_model_is_readable_but_cannot_be_edited():
    ws = MemoryWorkspace(editable=False)
    service = ReviewService(ws)
    assert not service.get_review_context(request(ws), PRINCIPAL)["permitted_actions"][
        "submit_review"
    ]
    with pytest.raises(ReviewError, match="editable copy"):
        service.submit_review({**request(ws, True), "reviews": [review()]}, PRINCIPAL)


@pytest.mark.parametrize(
    "change",
    [
        {"reviews": [review(assertion_id="assertion:unrelated")]},
        {"reviews": [review(rationale="  ")]},
        {"reviews": [review(verdict="sponsor_approved")]},
        {"reviews": [review(), review()]},
        {"feasibility": [{"attack_path_id": "path:foreign", "rating": "high"}]},
        {"feasibility": [{"attack_path_id": "path:a", "rating": "easy"}]},
        {
            "impacts": [
                {
                    "risk_score_id": "risk:r",
                    "damage_scenario_id": "damage:d",
                    "stakeholder_id": "party:other",
                    "values": {"safety": "severe"},
                }
            ]
        },
        {
            "impacts": [
                {
                    "risk_score_id": "risk:r",
                    "damage_scenario_id": "damage:d",
                    "stakeholder_id": "party:reviewer",
                    "values": {"safety": 5},
                }
            ]
        },
    ],
)
def test_bad_or_foreign_scope_edits_fail_atomically(change):
    ws = MemoryWorkspace()
    before = deepcopy(ws.versions)
    with pytest.raises(ReviewError) as err:
        ReviewService(ws).save_model_changes({**request(ws, True), **change}, PRINCIPAL)
    assert err.value.code == "validation_error"
    assert ws.versions == before


def test_cannot_overwrite_another_persons_review():
    doc = review_model()
    doc["reviews"] = [
        {
            "id": "review:other",
            "reviews": "assertion:path",
            "reviewer": "party:other",
            "review_status": "rejected",
            "justification": "Fixture",
        }
    ]
    ws = MemoryWorkspace(doc)
    with pytest.raises(ReviewError) as err:
        ReviewService(ws).submit_review(
            {**request(ws, True), "reviews": [review(review_id="review:other")]}, PRINCIPAL
        )
    assert err.value.code == "permission_denied"
    ReviewService(ws).submit_review({**request(ws, True), "reviews": [review()]}, PRINCIPAL)
    assert ws.versions["r2"]["reviews"][0] == doc["reviews"][0]


def test_stale_save_does_not_lose_successful_changes():
    ws = MemoryWorkspace()
    service = ReviewService(ws)
    stale = {**request(ws, True), "reviews": [review()]}
    service.save_ratings(
        {**request(ws, True), "feasibility": [{"attack_path_id": "path:a", "rating": "high"}]},
        PRINCIPAL,
    )
    with pytest.raises(ReviewError) as err:
        service.submit_review(stale, PRINCIPAL)
    assert err.value.code == "revision_conflict"
    assert err.value.to_dict()["error"]["current_revision"] == "r2"
    assert "reviews" not in ws.versions["r2"]


@pytest.mark.parametrize("failure", ["fail_validation", "fail_save"])
def test_validation_and_io_failure_preserve_original(failure):
    ws = MemoryWorkspace()
    setattr(ws, failure, True)
    before = deepcopy(ws.versions)
    with pytest.raises(ReviewError) as err:
        ReviewService(ws).submit_review({**request(ws, True), "reviews": [review()]}, PRINCIPAL)
    assert err.value.code == (
        "validation_error" if failure == "fail_validation" else "save_failure"
    )
    assert "private/path" not in str(err.value)
    assert ws.versions == before


def test_refresh_reads_exact_old_revision_after_another_save():
    ws = MemoryWorkspace()
    service = ReviewService(ws)
    old = request(ws)
    service.save_ratings(
        {**request(ws, True), "feasibility": [{"attack_path_id": "path:a", "rating": "high"}]},
        PRINCIPAL,
    )
    out = service.refresh_model(old, PRINCIPAL)
    assert out["revision"] == "r1"
    assert out["risk"]["assessments"][0]["feasibility"] == "low"


def test_missing_ratings_stay_unresolved_and_rejected_route_stays_visible():
    ws = MemoryWorkspace()
    out = ReviewService(ws).save_model_changes(
        {
            **request(ws, True),
            "reviews": [review("rejected")],
            "feasibility": [{"attack_path_id": "path:a", "rating": None}],
            "impacts": [
                {
                    "risk_score_id": "risk:r",
                    "damage_scenario_id": "damage:d",
                    "stakeholder_id": "party:reviewer",
                    "values": {"privacy": None},
                }
            ],
        },
        PRINCIPAL,
    )
    score = out["risk"]["assessments"][0]
    assert not score["complete"]
    assert score["derived_risk"]["privacy"] is None
    assert len(score["routes"]) == 1
    assert not score["path_reviewed"]


def test_broad_or_path_cannot_donate_rating_or_review_to_one_alternative():
    doc = review_model()
    doc["attack_steps"] = [
        {"id": "step:a", "precedes": ["step:join"]},
        {"id": "step:b", "precedes": ["step:join"]},
        {"id": "step:join", "gate": "or_gate"},
    ]
    doc["attack_paths"][0]["steps"] = ["step:join"]
    ws = MemoryWorkspace(doc)
    service = ReviewService(ws)
    context = service.get_review_context(request(ws), PRINCIPAL)
    assert context["problems"] == ["route_specific_path_required"]
    assert not context["attack_paths"]
    assert not context["permitted_actions"]["submit_review"]
    with pytest.raises(ReviewError):
        service.save_ratings(
            {**request(ws, True), "feasibility": [{"attack_path_id": "path:a", "rating": "high"}]},
            PRINCIPAL,
        )
    assert ws.current == "r1"


def test_shared_path_assertion_for_another_threat_is_not_a_review_target():
    doc = review_model()
    doc["threat_instances"].append({"id": "threat:other"})
    doc["assertions"].append(
        {
            "id": "assertion:other",
            "subject": "path:a",
            "predicate": "realizes_threat",
            "object": "threat:other",
            "assertion_status": "proposed",
        }
    )
    ws = MemoryWorkspace(doc)
    service = ReviewService(ws)
    assert [a["id"] for a in service.get_review_context(request(ws), PRINCIPAL)["assertions"]] == [
        "assertion:path"
    ]
    with pytest.raises(ReviewError):
        service.submit_review(
            {**request(ws, True), "reviews": [review(assertion_id="assertion:other")]}, PRINCIPAL
        )
    assert ws.current == "r1"


def test_one_route_rating_cannot_resolve_another_owners_conflicting_rating():
    doc = review_model()
    doc["attack_paths"].append({**doc["attack_paths"][0], "id": "path:alias"})
    doc["risk_scores"][0]["attack_paths"].append("path:alias")
    ws = MemoryWorkspace(doc)
    out = ReviewService(ws).save_ratings(
        {**request(ws, True), "feasibility": [{"attack_path_id": "path:a", "rating": "high"}]},
        PRINCIPAL,
    )
    score = out["risk"]["assessments"][0]
    assert not score["complete"]
    assert score["derived_risk"]["safety"] is None
    assert "conflicting_route_ratings" in score["routes"][0]["problems"]
    assert ws.versions["r2"]["attack_paths"][1]["attack_feasibility"] == "low"


def test_risk_failure_happens_before_commit(monkeypatch):
    from engine.graph import GraphError

    ws = MemoryWorkspace()
    service = ReviewService(ws)

    def fail_analysis(*args):
        raise GraphError("Fixture cannot be analyzed.")

    monkeypatch.setattr(service, "_views", fail_analysis)
    with pytest.raises(ReviewError) as err:
        service.submit_review({**request(ws, True), "reviews": [review()]}, PRINCIPAL)
    assert err.value.code == "validation_error"
    assert ws.current == "r1"
    assert "reviews" not in ws.versions["r1"]


def test_two_concurrent_saves_have_exactly_one_winner():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    ws = MemoryWorkspace()
    service = ReviewService(ws)
    barrier = Barrier(2)
    commit = ws.commit

    def synchronized_commit(*args):
        barrier.wait(timeout=5)
        return commit(*args)

    ws.commit = synchronized_commit
    payload = {**request(ws, True), "reviews": [review()]}

    def save():
        try:
            return service.submit_review(payload, PRINCIPAL)["revision"]
        except ReviewError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: save(), range(2))) == ["r2", "revision_conflict"]
    assert len(ws.versions) == 2
    assert len(ws.versions["r2"]["reviews"]) == 1


def test_shared_frontend_contract_examples_are_executable(monkeypatch):
    import json
    from pathlib import Path

    import yaml

    from engine import review_service

    examples = Path(__file__).parents[1] / "examples" / "human-review"
    contract = json.loads((examples / "contract.json").read_text())
    ws = MemoryWorkspace(yaml.safe_load((examples / "model.yaml").read_text()))
    service = ReviewService(ws)
    monkeypatch.setattr(review_service, "uuid4", lambda: "fixture-review")
    assert (
        service.get_review_context(contract["context"]["request"], PRINCIPAL)
        == contract["context"]["response"]
    )
    out = service.save_model_changes(contract["save"]["request"], PRINCIPAL)
    assert out == contract["save"]["response"]


def test_omitted_annotation_does_not_clear_existing_note_on_correction():
    ws = MemoryWorkspace()
    service = ReviewService(ws)
    service.submit_review(
        {**request(ws, True), "reviews": [review("rejected", annotation="Keep this note.")]},
        PRINCIPAL,
    )
    review_id = ws.versions["r2"]["reviews"][0]["id"]
    service.submit_review(
        {**request(ws, True), "reviews": [review(review_id=review_id)]}, PRINCIPAL
    )
    assert ws.versions["r3"]["reviews"][0]["description"] == "Keep this note."


def test_imported_model_views_do_not_require_a_reviewer_party():
    ws = MemoryWorkspace(
        {"components": [{"id": "component:imported", "name": "Imported part"}]}, editable=False
    )
    principal = ReviewPrincipal("party:host-user", PRINCIPAL.model_ids, frozenset({"read"}))
    out = ReviewService(ws).refresh_model(
        {
            "model_id": "local:one",
            "revision": "r1",
            "matrix": MATRIX_ID,
        },
        principal,
    )
    assert out["graph"]["nodes"][0]["id"] == "component:imported"
    assert out["risk"]["count"] == 0
    assert out["report_data"]["model"]["kind_label"] == "Read-only local model"
    assert "parties" not in ws.versions["r1"]


def test_verified_host_identity_is_added_atomically_without_impersonating_model_authors():
    ws = MemoryWorkspace()
    principal = ReviewPrincipal(
        "party:host-user", PRINCIPAL.model_ids, PRINCIPAL.actions, allow_party_creation=True
    )
    service = ReviewService(ws)
    context = service.get_review_context(request(ws), principal)
    assert context["reviewer_id"] == "party:host-user"
    assert context["permitted_actions"]["submit_review"]
    assert "party:host-user" not in {p["id"] for p in ws.versions["r1"]["parties"]}
    service.submit_review({**request(ws, True), "reviews": [review()]}, principal)
    saved = ws.versions["r2"]
    assert saved["reviews"][0]["reviewer"] == "party:host-user"
    assert saved["parties"][-1] == {
        "id": "party:host-user",
        "name": "Local reviewer",
        "party_kind": "person",
    }
    assert saved["assertions"] == ws.versions["r1"]["assertions"]


def test_party_provisioning_never_reclassifies_an_agent_or_bypasses_permissions():
    ws = MemoryWorkspace()
    agent = ReviewPrincipal(
        "party:agent", PRINCIPAL.model_ids, PRINCIPAL.actions, allow_party_creation=True
    )
    with pytest.raises(ReviewError) as err:
        ReviewService(ws).submit_review({**request(ws, True), "reviews": [review()]}, agent)
    assert err.value.code == "permission_denied"
    reader = ReviewPrincipal(
        "party:host-user", PRINCIPAL.model_ids, frozenset({"read"}), allow_party_creation=True
    )
    with pytest.raises(ReviewError):
        ReviewService(ws).submit_review({**request(ws, True), "reviews": [review()]}, reader)
    assert "party:host-user" not in {p["id"] for p in ws.versions["r1"]["parties"]}


def test_version_metadata_is_saved_in_the_same_commit_as_review_changes():
    class VersionedWorkspace(MemoryWorkspace):
        def save_version(self, model_id, expected_revision, document, *, description, summary):
            revision = self.commit(model_id, expected_revision, document)
            self.metadata = {"revision": revision, "description": description, "summary": summary}
            return revision

    ws = VersionedWorkspace()
    service = ReviewService(ProjectReviewWorkspace(ws))
    out = service.save_model_changes(
        {
            **request(ws, True),
            "reviews": [review()],
            "description": "Reviewed this route",
            "feasibility": [{"attack_path_id": "path:a", "rating": "high"}],
        },
        PRINCIPAL,
    )
    assert ws.metadata["revision"] == out["revision"] == "r2"
    assert ws.metadata["description"] == "Reviewed this route"
    assert ws.metadata["summary"]["derived_risk"] == out["risk"]["assessments"][0]["derived_risk"]
    assert ws.metadata["summary"]["incomplete"] == 0
    ws.fail_save = True
    with pytest.raises(ReviewError):
        service.save_ratings(
            {
                **request(ws, True),
                "description": "Not saved",
                "feasibility": [{"attack_path_id": "path:a", "rating": None}],
            },
            PRINCIPAL,
        )
    assert ws.metadata["description"] == "Reviewed this route"
    assert ws.current == "r2"
