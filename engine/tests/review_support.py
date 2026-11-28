"""Test-only workspace; deliberately not a production #288 storage adapter."""

from copy import deepcopy
from threading import Lock

from engine.model_graph import project_model_graph
from engine.review_workspace import ModelRevision, ReviewError, ReviewPrincipal


def review_model():
    return {
        "parties": [
            {"id": "party:reviewer", "party_kind": "person"},
            {"id": "party:other", "party_kind": "person"},
            {"id": "party:agent", "party_kind": "software_agent"},
        ],
        "threat_instances": [{"id": "threat:t", "realizes_damage": "damage:d"}],
        "damage_scenarios": [{"id": "damage:d"}],
        "attack_steps": [{"id": "step:a"}],
        "attack_paths": [
            {
                "id": "path:a",
                "steps": ["step:a"],
                "realizes_threat": "threat:t",
                "attack_feasibility": "low",
            }
        ],
        "assertions": [
            {
                "id": "assertion:path",
                "subject": "path:a",
                "predicate": "realizes_threat",
                "object": "threat:t",
                "assertion_status": "proposed",
                "asserted_by": "party:agent",
                "generated_by": "test fixture",
                "confidence": "medium",
            }
        ],
        "risk_scores": [
            {
                "id": "risk:r",
                "threat": "threat:t",
                "damage_scenario": "damage:d",
                "for_stakeholder": "party:reviewer",
                "attack_paths": ["path:a"],
                "mitigation_status": "planned",
                "impact": {
                    "safety": "severe",
                    "financial": "major",
                    "operational": "moderate",
                    "privacy": "negligible",
                },
            }
        ],
    }


PRINCIPAL = ReviewPrincipal(
    "party:reviewer", frozenset({"local:one"}), frozenset({"read", "review", "rate"})
)


class MemoryWorkspace:
    def __init__(self, document=None, editable=True):
        self.versions = {"r1": deepcopy(document if document is not None else review_model())}
        self.current = "r1"
        self.editable = editable
        self.fail_save = False
        self.fail_validation = False
        self.lock = Lock()

    def read(self, model_id, revision):
        if model_id != "local:one" or revision not in self.versions:
            raise ReviewError("not_found", "Model revision not found.")
        return ModelRevision(model_id, revision, deepcopy(self.versions[revision]), self.editable)

    def history(self, model_id, revision):
        return [
            self.read(model_id, key) for key in self.versions if int(key[1:]) <= int(revision[1:])
        ]

    def validate(self, document):
        if self.fail_validation:
            raise ReviewError(
                "validation_error", "Fixture validation rejected changes.", field="reviews"
            )
        project_model_graph(document)

    def commit(self, model_id, expected_revision, document):
        with self.lock:
            if expected_revision != self.current:
                raise ReviewError(
                    "revision_conflict", "Reload before retrying.", current_revision=self.current
                )
            if not self.editable:
                raise ReviewError("permission_denied", "Read-only model.")
            self.validate(document)
            if self.fail_save:
                raise OSError("private/path/must/not/escape")
            revision = f"r{len(self.versions) + 1}"
            self.versions[revision] = deepcopy(document)
            self.current = revision
            return revision
