"""Small client for the engine's local API (used by the CLI; the GUI does the same in TS)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from engine.api.server import DEFAULT_HOST, DEFAULT_PORT


class EngineUnreachable(Exception):
    """The local engine is not running or did not answer."""


def default_url() -> str:
    port = os.environ.get("TMODEL_ENGINE_PORT", DEFAULT_PORT)
    return f"http://{DEFAULT_HOST}:{port}"


def get(path: str, base_url: str | None = None, timeout: float = 3.0) -> dict[str, Any]:
    url = (base_url or default_url()).rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise EngineUnreachable(f"no tmodel engine at {url} ({exc})") from exc
