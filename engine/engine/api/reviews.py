"""Opt-in authenticated transport for the local review service.

The desktop host must supply a #288 workspace and verified session bindings.
There is deliberately no public login/role assignment or file-path endpoint.
"""

import json
from collections.abc import Mapping
from secrets import compare_digest
from typing import Any

from engine.review_service import ReviewService
from engine.review_workspace import ReviewError, ReviewPrincipal

MAX_BODY = 262144
OPERATIONS = {
    "/reviews/context": "get_review_context",
    "/reviews/submit": "submit_review",
    "/reviews/ratings": "save_ratings",
    "/reviews/changes": "save_model_changes",
    "/reviews/refresh": "refresh_model",
}
ERROR_STATUS = {
    "validation_error": 422,
    "permission_denied": 403,
    "not_found": 404,
    "revision_conflict": 409,
    "save_failure": 503,
    "workspace_failure": 503,
}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("nonfinite value")


class ReviewAPI:
    def __init__(self, service: ReviewService, sessions: Mapping[str, ReviewPrincipal]) -> None:
        if not sessions or any(
            not isinstance(token, str) or not token.isascii() or len(token) < 32
            for token in sessions
        ):
            raise ValueError(
                "review sessions require host-generated credentials of at least 32 characters"
            )
        self.service = service
        self.sessions = dict(sessions)

    def authenticate(self, authorization: str) -> ReviewPrincipal:
        if authorization.startswith("Bearer ") and authorization.isascii():
            candidate = authorization[7:]
            for token, principal in self.sessions.items():
                if compare_digest(candidate, token):
                    return principal
        raise ReviewError("permission_denied", "A verified desktop review session is required.")

    def dispatch(self, path: str, principal: ReviewPrincipal, body: bytes) -> dict[str, Any]:
        try:
            request = json.loads(
                body,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
            if not isinstance(request, dict):
                raise ValueError("not an object")
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise ReviewError(
                "validation_error", "Expected a JSON object with unique fields."
            ) from exc
        return getattr(self.service, OPERATIONS[path])(request, principal)
