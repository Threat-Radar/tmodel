"""Deterministic JSON rendering and safety checks for public Pages data."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

FORBIDDEN_CREDENTIAL_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:sk|rk)-(?:live|proj)-[A-Za-z0-9_-]{16,}\b"),
)
WINDOWS_USER_PATH = re.compile(r"\b[A-Za-z]:\\\\Users\\\\", re.IGNORECASE)
LOCAL_PATH_MARKERS = ("/Users/", "/home/", "/private/var/", "/var/folders/")


def render_public_json(payload: Any, *, root: Path, context: str) -> str:
    """Serialize *payload* deterministically and reject non-public content."""
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    validate_public_text(text, root=root, context=context)
    return text


def validate_public_text(text: str, *, root: Path, context: str) -> None:
    """Reject credentials and machine-local paths from serialized public data."""
    markers = (str(root), *LOCAL_PATH_MARKERS)
    leaked = next((marker for marker in markers if marker in text), None)
    if leaked:
        raise RuntimeError(
            f"{context}: generated public data contains local path marker {leaked!r}"
        )
    if WINDOWS_USER_PATH.search(text):
        raise RuntimeError(
            f"{context}: generated public data contains local path marker "
            f"{WINDOWS_USER_PATH.pattern!r}"
        )
    secret = next(
        (
            pattern.pattern
            for pattern in FORBIDDEN_CREDENTIAL_PATTERNS
            if pattern.search(text)
        ),
        None,
    )
    if secret:
        raise RuntimeError(
            f"{context}: generated public data contains credential marker {secret!r}"
        )
