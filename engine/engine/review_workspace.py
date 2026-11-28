"""Local review storage contract and adapter for #288's version writer (#289)."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class ReviewError(Exception):
    """Transport-safe failure. Adapters must not include paths or credentials."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        field: str | None = None,
        current_revision: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field
        self.current_revision = current_revision

    def to_dict(self) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.field:
            error["fields"] = [{"field": self.field, "message": self.message}]
        if self.current_revision is not None:
            error["current_revision"] = self.current_revision
        return {"error": error}


@dataclass(frozen=True)
class ModelRevision:
    model_id: str
    revision: str
    document: Mapping[str, Any]
    editable: bool


class ReviewWorkspace(Protocol):
    """Proposed #288 adapter: all documents are isolated snapshots.

    read() returns the requested immutable revision, never silently the latest.
    history() returns snapshots through that revision, oldest first.
    validate() performs full ExampleModel schema validation, raising ReviewError.
    commit() validates and atomically compares the *current* revision, writes the
    candidate, retains previous revisions and returns the new opaque revision.
    A stale revision raises revision_conflict, including current_revision.
    Any failure leaves stored content and the current revision unchanged.
    commit() must independently enforce editable-copy status and validation.
    """

    def read(self, model_id: str, revision: str) -> ModelRevision: ...

    def history(self, model_id: str, revision: str) -> Sequence[ModelRevision]: ...

    def validate(self, document: Mapping[str, Any]) -> None: ...

    def commit(self, model_id: str, expected_revision: str, document: Mapping[str, Any]) -> str: ...


class ProjectReviewWorkspace:
    """Use #288's version writer; physical storage remains owned by #288."""

    def __init__(self, projects: Any) -> None:
        self.projects = projects

    def read(self, model_id: str, revision: str) -> ModelRevision:
        return self.projects.read(model_id, revision)

    def history(self, model_id: str, revision: str) -> Sequence[ModelRevision]:
        return self.projects.history(model_id, revision)

    def validate(self, document: Mapping[str, Any]) -> None:
        self.projects.validate(document)

    def commit(self, model_id: str, expected_revision: str, document: Mapping[str, Any]) -> str:
        return self.commit_version(
            model_id, expected_revision, document, description=None, summary=None
        )

    def commit_version(
        self,
        model_id: str,
        expected_revision: str,
        document: Mapping[str, Any],
        *,
        description: str | None,
        summary: Mapping[str, Any] | None,
    ) -> str:
        return self.projects.save_version(
            model_id,
            expected_revision,
            document,
            description=description,
            summary=summary,
        )


@dataclass(frozen=True)
class ReviewPrincipal:
    """Verified by the host, never constructed from an HTTP request body.

    The host binds its authenticated session to a human Party, model access and
    explicit actions. Only the native host may provision its verified local user
    on first save. Model roles (including sponsor) grant nothing.
    """

    party_id: str
    model_ids: frozenset[str]
    actions: frozenset[str] = frozenset({"read"})
    # Host-only capability: provision this verified person's identity atomically
    # with their first change to an editable copy. Never reclassify an old Party.
    allow_party_creation: bool = False
    display_name: str = "Local reviewer"
