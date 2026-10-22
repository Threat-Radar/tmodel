"""Small client for the engine's local API (used by the CLI; the GUI does the same in TS)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from engine.api.server import DEFAULT_HOST, DEFAULT_PORT


class EngineUnreachable(Exception):
    """The local engine is not running or did not answer."""


class EngineTimeout(EngineUnreachable):
    """The engine accepted the request but did not answer in time (busy, not gone)."""


class EngineError(Exception):
    """The engine answered with an error (bad file, unknown goal, ...)."""


# Loopback only: never route the engine's traffic (model paths, goals) via a proxy.
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def default_url() -> str:
    port = os.environ.get("TMODEL_ENGINE_PORT", DEFAULT_PORT)
    return f"http://{DEFAULT_HOST}:{port}"


def get(
    path: str,
    base_url: str | None = None,
    timeout: float = 3.0,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = (base_url or default_url()).rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with _OPENER.open(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:  # before URLError: it is a subclass
        try:
            body = json.loads(exc.read())
        except ValueError:
            body = None
        message = body.get("error") if isinstance(body, dict) else None
        raise EngineError(message or f"HTTP {exc.code} {exc.reason}") from exc
    except TimeoutError as exc:
        raise EngineTimeout(f"the engine at {url} did not answer within {timeout:g} s") from exc
    except (urllib.error.URLError, ConnectionError) as exc:
        if isinstance(exc.args[0] if exc.args else None, TimeoutError):
            raise EngineTimeout(f"the engine at {url} did not answer within {timeout:g} s") from exc
        raise EngineUnreachable(f"no tmodel engine at {url} ({exc})") from exc
