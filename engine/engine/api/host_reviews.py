"""Bind project reviews to the desktop host's verified local OS identity (#289)."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Any

from engine.api.reviews import ReviewAPI
from engine.review_service import ReviewService
from engine.review_workspace import ProjectReviewWorkspace, ReviewError, ReviewPrincipal

PROOF_DOMAIN = b"tmodel-host-session-v1:"
MODEL_ID = re.compile(r"(?:project|file):[0-9a-f]{32}\Z")
IDENTITY = re.compile(r"party:local:([0-9a-f]{32}):([0-9]+)\Z")
CHALLENGE = re.compile(r"[0-9a-f]{64}\Z")


def local_reviewer(identity: str) -> ReviewPrincipal:
    """Identity comes from the native host's private per-installation record.

    Bind it to this process's real OS user, not a reviewer id sent by a webview.
    The random installation component prevents equal UIDs on two Macs aliasing.
    """
    match = IDENTITY.fullmatch(identity) if isinstance(identity, str) else None
    uid = getattr(os, "getuid", lambda: None)()
    if match is None or uid is None or match[2] != str(uid):
        raise ReviewError(
            "permission_denied", "The desktop reviewer identity is not valid for this OS user."
        )
    return ReviewPrincipal(
        identity,
        frozenset(),
        frozenset({"read", "review", "rate"}),
        allow_party_creation=True,
    )


class HostReviewAPI(ReviewAPI):
    """One desktop host session; only its registered project/file ids get access.

    The #288 host-only pickers register models. A client-provided id never grants
    filesystem access, a reviewer identity, or sponsor permissions.
    """

    def __init__(
        self,
        projects: Any,
        token: str,
        identity: str,
        *,
        list_models: Callable[[], Mapping[str, Any]],
    ) -> None:
        principal = local_reviewer(identity)
        super().__init__(ReviewService(ProjectReviewWorkspace(projects)), {token: principal})
        self._host_key = token.encode("ascii")
        self._list_models = list_models

    def authenticate(self, authorization: str) -> ReviewPrincipal:
        principal = super().authenticate(authorization)
        # Registry contents originate only from the host's approved picker steps.
        models = self._list_models().get("models", [])
        ids = frozenset(
            item["model_id"]
            for item in models
            if isinstance(item, Mapping)
            and isinstance(item.get("model_id"), str)
            and MODEL_ID.fullmatch(item["model_id"])
        )
        return replace(principal, model_ids=ids)

    def host_proof(self, challenge: str) -> dict[str, str]:
        """Prove possession before Rust sends a bearer secret to the fixed port.

        A health string is insufficient: an unrelated local server must not gain
        the host token. Fresh challenges prevent replay of an earlier response.
        """
        if not isinstance(challenge, str) or CHALLENGE.fullmatch(challenge) is None:
            raise ReviewError(
                "validation_error", "Expected a 64-character hexadecimal host challenge."
            )
        proof = hmac.new(self._host_key, PROOF_DOMAIN + challenge.encode("ascii"), hashlib.sha256)
        return {"challenge": challenge, "proof": proof.hexdigest()}
