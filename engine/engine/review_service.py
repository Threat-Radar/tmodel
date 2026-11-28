"""Revision-scoped review, annotation and rating logic for editable copies (#289).

No canonical proposal acceptance, filesystem access or alternate risk formula.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from datetime import date, datetime
from typing import Any
from uuid import uuid4

from engine.core import model_summary
from engine.graph import AttackGraph, GraphError
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths
from engine.review import assertion_review_state
from engine.review_workspace import ModelRevision, ReviewError, ReviewPrincipal, ReviewWorkspace
from engine.risk import CATEGORIES, FEASIBILITIES, assess_document
from engine.risk_routes import rated_routes

BASE_FIELDS = {"model_id", "revision", "matrix", "threat_id", "route_id"}
SAVE_FIELDS = BASE_FIELDS - {"revision"} | {
    "expected_revision",
    "reviews",
    "feasibility",
    "impacts",
    "description",
}
SEVERITIES = {"negligible", "moderate", "major", "severe"}


def _invalid(field: str, message: str) -> None:
    raise ReviewError("validation_error", message, field=field)


def _object(value: Any, allowed: set[str], field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) - allowed:
        _invalid(field, "Expected an object containing only the documented fields.")
    return value


def _text(value: Any, field: str, limit: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        _invalid(field, f"Expected nonblank text of at most {limit} characters.")
    return value


def _records(doc: Mapping[str, Any], collection: str) -> dict[str, Any]:
    return {record["id"]: record for record in doc.get(collection) or []}


def _json_safe(value: Any) -> Any:
    """Preserve record structure while encoding YAML timestamps for transport."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _version_summary(risk: Mapping[str, Any]) -> dict[str, Any]:
    """Describe calculated results for version history, retaining unknown inputs."""
    assessments = risk["assessments"]
    return {
        "matrix": risk["matrix"],
        "assessments": len(assessments),
        "incomplete": sum(not item["complete"] for item in assessments),
        "derived_risk": {
            category: max(
                (
                    item["derived_risk"][category]
                    for item in assessments
                    if item["derived_risk"][category] is not None
                ),
                default=None,
            )
            for category in CATEGORIES
        },
    }


class ReviewService:
    def __init__(self, workspace: ReviewWorkspace) -> None:
        self.workspace = workspace

    def _open(
        self,
        request: Mapping[str, Any],
        principal: ReviewPrincipal,
        *,
        saving: bool = False,
        require_reviewer: bool = True,
    ) -> ModelRevision:
        _object(request, SAVE_FIELDS if saving else BASE_FIELDS, "request")
        model_id = _text(request.get("model_id"), "model_id", 256)
        revision = _text(
            request.get("expected_revision" if saving else "revision"), "revision", 256
        )
        if model_id not in principal.model_ids or "read" not in principal.actions:
            raise ReviewError("permission_denied", "This session cannot access this model.")
        snapshot = self.workspace.read(model_id, revision)
        if snapshot.model_id != model_id or snapshot.revision != revision:
            raise ReviewError("workspace_failure", "Workspace returned a different revision.")
        # Detach even if an adapter accidentally returns a shared Python mapping.
        snapshot = ModelRevision(model_id, revision, deepcopy(snapshot.document), snapshot.editable)
        person = _records(snapshot.document, "parties").get(principal.party_id)
        if require_reviewer and not (
            (person is not None and person.get("party_kind") == "person")
            or (person is None and principal.allow_party_creation)
        ):
            raise ReviewError("permission_denied", "The verified reviewer must be a human Party.")
        if saving and not snapshot.editable:
            raise ReviewError("permission_denied", "Create an editable copy before saving.")
        return snapshot

    def _selection(self, doc: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
        threat = _text(request.get("threat_id"), "threat_id", 256)
        route_id = _text(request.get("route_id"), "route_id", 256)
        graph = AttackGraph.from_dict(doc)
        if threat not in graph.threats():
            _invalid("threat_id", "Expected a threat with an authored attack path.")
        paths = _records(doc, "attack_paths")
        routes = rated_routes(
            graph, threat, {key: path.get("attack_feasibility") for key, path in paths.items()}
        )
        route = next((route for route in routes if route["id"] == route_id), None)
        if route is None:
            _invalid("route_id", "This route does not belong to the selected threat and revision.")
        owners = set(route["rating_paths"])
        assertions = [
            assertion
            for assertion in doc.get("assertions") or []
            if assertion.get("subject") == threat
            or (
                assertion.get("subject") in owners
                and assertion.get("predicate") == "realizes_threat"
                and assertion.get("object") == threat
            )
        ]
        return {"threat": threat, "route": route, "owners": owners, "assertions": assertions}

    def _views(
        self, doc: Mapping[str, Any], matrix: Any, model_id: str, *, editable: bool = True
    ) -> dict[str, Any]:
        # All outputs derive from one document. No approved-vector loader or reread.
        risk = assess_document(doc, matrix=matrix)
        graph = AttackGraph.from_dict(doc)
        paths = [
            {"goal": threat, "paths": [path.to_dict() for path in enumerate_paths(graph, threat)]}
            for threat in graph.threats()
        ]
        return {
            "graph": project_model_graph(doc).to_dict(),
            "attack_paths": paths,
            "risk": risk,
            "model": model_summary(
                doc,
                model_id=model_id,
                file=model_id,
                kind="local",
                kind_label="Editable local model" if editable else "Read-only local model",
            ),
        }

    @staticmethod
    def _tag(views: dict[str, Any], model_id: str, revision: str) -> dict[str, Any]:
        tagged = {
            name: {"model_id": model_id, "revision": revision, **value}
            for name, value in views.items()
            if name in {"graph", "risk"}
        }
        tagged["graph"]["file"] = model_id
        paths = [{"file": model_id, **response} for response in views["attack_paths"]]
        tagged["attack_paths"] = {
            "model_id": model_id,
            "revision": revision,
            "responses": paths,
        }
        # Existing frontend report derives from graph + per-threat paths, not a
        # second backend report implementation. Recompute its header too.
        tagged["report_data"] = {
            "model_id": model_id,
            "revision": revision,
            "graph": tagged["graph"],
            "model": views["model"],
            "attackPaths": paths,
        }
        return tagged

    def refresh_model(
        self, request: Mapping[str, Any], principal: ReviewPrincipal
    ) -> dict[str, Any]:
        snapshot = self._open(request, principal, require_reviewer=False)
        try:
            views = self._views(
                snapshot.document,
                request.get("matrix"),
                snapshot.model_id,
                editable=snapshot.editable,
            )
        except (GraphError, ValueError) as exc:
            raise ReviewError("validation_error", str(exc), field="model") from exc
        return {
            "model_id": snapshot.model_id,
            "revision": snapshot.revision,
            **self._tag(views, snapshot.model_id, snapshot.revision),
        }

    def get_review_context(
        self,
        request: Mapping[str, Any],
        principal: ReviewPrincipal,
    ) -> dict[str, Any]:
        snapshot = self._open(request, principal)
        doc = snapshot.document
        try:
            risk = assess_document(doc, matrix=request.get("matrix"))
            selected = self._selection(doc, request)
        except (GraphError, ValueError) as exc:
            raise ReviewError("validation_error", str(exc), field="model") from exc
        assertions = selected["assertions"]
        ids = {assertion["id"] for assertion in assertions}
        reviews = [r for r in doc.get("reviews") or [] if r.get("reviews") in ids]
        parties = _records(doc, "parties")
        history, seen = [], set()
        for prior in self.workspace.history(snapshot.model_id, snapshot.revision):
            if prior.model_id != snapshot.model_id:
                raise ReviewError(
                    "workspace_failure", "Workspace returned another model's history."
                )
            for review in prior.document.get("reviews") or []:
                key = json.dumps(review, sort_keys=True, default=str)
                if review.get("reviews") in ids and key not in seen:
                    history.append({"revision": prior.revision, "review": deepcopy(review)})
                    seen.add(key)
        owners = selected["owners"]
        actions = principal.actions if snapshot.editable else frozenset({"read"})
        return _json_safe(
            {
                "model_id": snapshot.model_id,
                "revision": snapshot.revision,
                "reviewer_id": principal.party_id,
                "route": selected["route"],
                "threat": deepcopy(_records(doc, "threat_instances")[selected["threat"]]),
                "attack_paths": [
                    deepcopy(_records(doc, "attack_paths")[key]) for key in sorted(owners)
                ],
                "assertions": deepcopy(assertions),
                "reviews": deepcopy(reviews),
                "history": history,
                "review_states": [assertion_review_state(a, reviews, parties) for a in assertions],
                "risk_scores": [
                    deepcopy(score)
                    for score in doc.get("risk_scores") or []
                    if score.get("threat") == selected["threat"]
                ],
                "calculated_risk": risk,
                "permitted_actions": {
                    "submit_review": "review" in actions and bool(assertions),
                    "save_feasibility": "rate" in actions and bool(owners),
                    "save_impacts": "rate" in actions
                    and any(
                        score.get("threat") == selected["threat"]
                        for score in doc.get("risk_scores") or []
                    ),
                    "correct_own_review": "review" in actions
                    and any(review.get("reviewer") == principal.party_id for review in reviews),
                    "accept_proposal": False,
                },
                "problems": [] if owners else ["route_specific_path_required"],
            }
        )

    def save_model_changes(
        self,
        request: Mapping[str, Any],
        principal: ReviewPrincipal,
    ) -> dict[str, Any]:
        snapshot = self._open(request, principal, saving=True)
        doc = deepcopy(snapshot.document)
        try:
            assess_document(doc, matrix=request.get("matrix"))
            selected = self._selection(doc, request)
            updates = {}
            for name in ("reviews", "feasibility", "impacts"):
                value = request.get(name, [])
                if not isinstance(value, list) or len(value) > 100:
                    _invalid(name, "Expected a list of at most 100 updates.")
                updates[name] = value
            if not any(updates.values()):
                _invalid("request", "Provide at least one review or rating update.")
            description = request.get("description")
            if description is not None:
                _text(description, "description", 500)
            commit_version = getattr(self.workspace, "commit_version", None)
            if description is not None and commit_version is None:
                raise ReviewError(
                    "workspace_failure", "This workspace cannot save version descriptions."
                )
            if principal.party_id not in _records(doc, "parties"):
                parties = doc.setdefault("parties", [])
                if parties is None:
                    parties = doc["parties"] = []
                parties.append(
                    {
                        "id": principal.party_id,
                        "name": principal.display_name,
                        "party_kind": "person",
                    }
                )
            if updates["reviews"]:
                self._review_updates(doc, selected, updates["reviews"], principal)
            if updates["feasibility"] or updates["impacts"]:
                self._rating_updates(doc, selected, updates, principal)
            self.workspace.validate(doc)
            # Analysis failure must happen before any write. commit is a CAS,
            # so a concurrent writer cannot make this response describe their model.
            views = self._views(doc, request.get("matrix"), snapshot.model_id)
            json.dumps(views, allow_nan=False)  # validate transport before committing
        except (GraphError, ValueError) as exc:
            raise ReviewError("validation_error", str(exc), field="model") from exc
        try:
            if commit_version is not None:
                revision = commit_version(
                    snapshot.model_id,
                    snapshot.revision,
                    doc,
                    description=description or "Human review and rating updates",
                    summary=_version_summary(views["risk"]),
                )
            else:
                revision = self.workspace.commit(snapshot.model_id, snapshot.revision, doc)
        except ReviewError:
            raise
        except Exception as exc:
            raise ReviewError(
                "save_failure", "The model could not be saved. Retry your changes."
            ) from exc
        return {
            "model_id": snapshot.model_id,
            "revision": revision,
            **self._tag(views, snapshot.model_id, revision),
        }

    def submit_review(
        self, request: Mapping[str, Any], principal: ReviewPrincipal
    ) -> dict[str, Any]:
        if set(request) & {"feasibility", "impacts"}:
            _invalid("request", "Use saveModelChanges for a combined save.")
        return self.save_model_changes(request, principal)

    def save_ratings(
        self, request: Mapping[str, Any], principal: ReviewPrincipal
    ) -> dict[str, Any]:
        if "reviews" in request:
            _invalid("request", "Use saveModelChanges for a combined save.")
        return self.save_model_changes(request, principal)

    @staticmethod
    def _review_updates(doc, selected, updates, principal):
        if "review" not in principal.actions:
            raise ReviewError("permission_denied", "This session cannot submit reviews.")
        assertions = {a["id"] for a in selected["assertions"]}
        reviews = doc.setdefault("reviews", [])
        if reviews is None:
            reviews = doc["reviews"] = []
        seen = set()
        for update in updates:
            _object(
                update,
                {"assertion_id", "verdict", "rationale", "annotation", "review_id"},
                "reviews",
            )
            assertion = _text(update.get("assertion_id"), "assertion_id", 256)
            if assertion not in assertions or assertion in seen:
                _invalid("assertion_id", "Select one exact Assertion in this review context once.")
            seen.add(assertion)
            verdict = update.get("verdict")
            if verdict not in ("accepted", "rejected"):
                _invalid("verdict", "Expected accepted or rejected.")
            rationale = _text(update.get("rationale"), "rationale")
            annotation = update.get("annotation")
            if "annotation" in update and (
                not isinstance(annotation, str) or len(annotation) > 4096
            ):
                _invalid("annotation", "Expected text of at most 4096 characters.")
            owned = [
                r
                for r in reviews
                if r.get("reviews") == assertion and r.get("reviewer") == principal.party_id
            ]
            review_id = update.get("review_id")
            if review_id is not None:
                record = next((r for r in owned if r["id"] == review_id), None)
                if record is None:
                    raise ReviewError(
                        "permission_denied", "Only your own matching review can be corrected."
                    )
            elif owned:
                _invalid("review_id", "Select your existing review explicitly to correct it.")
            else:
                record = {
                    "id": f"review:{uuid4()}",
                    "reviews": assertion,
                    "reviewer": principal.party_id,
                }
                reviews.append(record)
            record.update(review_status=verdict, justification=rationale)
            if "annotation" in update:
                record["description"] = annotation

    @staticmethod
    def _rating_updates(doc, selected, updates, principal):
        if "rate" not in principal.actions:
            raise ReviewError("permission_denied", "This session cannot change ratings.")
        paths, scores = _records(doc, "attack_paths"), _records(doc, "risk_scores")
        seen = set()
        for update in updates["feasibility"]:
            _object(update, {"attack_path_id", "rating"}, "feasibility")
            path_id = _text(update.get("attack_path_id"), "attack_path_id", 256)
            if path_id not in selected["owners"] or path_id in seen:
                _invalid(
                    "attack_path_id", "Select one unambiguous authored path for this route once."
                )
            seen.add(path_id)
            if "rating" not in update or (
                update["rating"] is not None and update["rating"] not in FEASIBILITIES
            ):
                _invalid("rating", "Expected high, medium, low, very_low or null.")
            paths[path_id]["attack_feasibility"] = update["rating"]
        seen = set()
        for update in updates["impacts"]:
            _object(
                update,
                {"risk_score_id", "damage_scenario_id", "stakeholder_id", "values"},
                "impacts",
            )
            score_id = _text(update.get("risk_score_id"), "risk_score_id", 256)
            score = scores.get(score_id)
            if (
                score is None
                or score_id in seen
                or score.get("threat") != selected["threat"]
                or "damage_scenario_id" not in update
                or "stakeholder_id" not in update
                or score.get("damage_scenario") != update["damage_scenario_id"]
                or score.get("for_stakeholder") != update["stakeholder_id"]
            ):
                _invalid(
                    "risk_score_id", "RiskScore, threat, damage and stakeholder must match exactly."
                )
            seen.add(score_id)
            values = _object(update.get("values"), set(CATEGORIES), "values")
            if not values:
                _invalid("values", "Provide at least one impact category.")
            for category, value in values.items():
                if value is not None and (not isinstance(value, str) or value not in SEVERITIES):
                    _invalid(
                        f"values.{category}",
                        "Expected negligible, moderate, major, severe or null.",
                    )
            score["impact"] = {**(score.get("impact") or {}), **values}
