"""Opt-in HTTP routes for AI-proposed attack paths (#302, DL-0082).

`serve()` installs them on every server it starts. Drafting works only when the engine
starts with `tmodel serve --enable-ai`; otherwise `POST /ai/attack-paths` answers 503
not_enabled, and `GET /ai/status` says so. Like the other routes, they answer only a
loopback Host and the app's origins (or no Origin, for a local process).

    GET  /ai/status          is the local LLM ready? If not, why, and the setup steps
    POST /ai/attack-paths    {"model_text", "max_paths"?}: the model with the AI's attack
                             paths added, each a proposal (engine/ai_paths.py)

The routes write nothing: the app saves the answer's `model_text` as the project's next
version and reviews it there. One draft runs at a time. Errors use the envelope of the
other app routes, `{"error": {"code", "message", ...}}`.
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from http.server import ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from engine.ai_paths import DEFAULT_PATHS, MAX_MODEL_BYTES, AiError, Catalogs, draft
from engine.api.server import ALLOWED_ORIGINS, is_loopback
from engine.llm import Ollama

PREFIX = "/ai"
STATUS = "/ai/status"
ATTACK_PATHS = "/ai/attack-paths"
MAX_BODY = MAX_MODEL_BYTES + 65536  # the model's text, JSON-escaped, and a few fields
BODY_SECONDS = 30.0  # how long a whole request body may take to arrive
ERROR_STATUS = {
    "validation_error": 422,
    "nothing_to_draft": 422,
    "generation_failed": 422,
    "permission_denied": 403,
    "not_found": 404,
    "not_enabled": 503,
    "ai_unavailable": 503,
    "busy": 503,
    "generation_timeout": 504,
}
INTERNAL_ERROR = {"error": {"code": "internal_error", "message": "The draft failed."}}


@dataclass
class AiService:
    """What the routes draft with, and the lock that keeps it to one draft at a time."""

    llm: Ollama = field(default_factory=Ollama)
    catalogs: Catalogs = field(default_factory=Catalogs)
    lock: threading.Lock = field(default_factory=threading.Lock)
    clock: Callable[[], datetime] | None = None  # the Assertions' time; tests fix it

    def status(self) -> dict[str, Any]:
        out = {"enabled": True, **self.llm.status()}
        out["setup"] = None if out["ready"] else self.llm.setup_steps()
        return out

    def attack_paths(self, request: Mapping[str, Any]) -> dict[str, Any]:
        unknown = sorted(set(request) - {"model_text", "max_paths"})
        if unknown:
            raise AiError("validation_error", f"Unknown field {unknown[0]!r}.")
        text = request.get("model_text")
        if not isinstance(text, str) or not text.strip():
            raise AiError("validation_error", "model_text: give the model as YAML text.")
        paths = request.get("max_paths", DEFAULT_PATHS)
        if isinstance(paths, bool) or not isinstance(paths, int):
            raise AiError("validation_error", "max_paths: give a whole number.")
        if not self.lock.acquire(blocking=False):
            raise AiError("busy", "A draft is already running; try again when it finishes.")
        try:
            now = self.clock() if self.clock else None
            result = draft(text, llm=self.llm, catalogs=self.catalogs, max_paths=paths, now=now)
        finally:
            self.lock.release()
        added = result.record["objects"]
        return {
            "model_text": result.model_text,
            "summary": {
                key: len(added.get(key) or [])
                for key in ("threat_instances", "attack_steps", "attack_paths")
            },
            "paths": result.paths,
            "warnings": result.warnings,
            "generated_by": result.generated_by,
        }


def _not_enabled_status() -> dict[str, Any]:
    llm = Ollama()
    return {
        "enabled": False,
        "ready": False,
        "reason": "not_enabled",
        "ollama": {"url": llm.url, "running": None, "version": None},
        "model": {"name": llm.model, "installed": None},
        "setup": ["Start the engine with: tmodel serve --enable-ai", *llm.setup_steps()],
    }


class AiRoutes:
    """Mixed in ahead of the engine's handler: answers /ai/*, passes the rest on. Its
    helpers all start with `_ai_`, so none can replace a helper of the handlers behind
    it (#297's `_read_body` clash)."""

    ai: AiService | None = None

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        if self._ai_path():
            self._ai_reply(*self._ai_answer("GET"))
        else:
            super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self._ai_path():
            self._ai_reply(*self._ai_answer("POST"))
        else:
            self._ai_pass_on("do_POST")

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self._ai_path():
            self._ai_preflight()
        else:
            self._ai_pass_on("do_OPTIONS")

    def _ai_pass_on(self, method: str) -> None:
        handler = getattr(super(), method, None)
        if handler is None:  # what http.server answers for a method it has no handler for
            self.send_error(501, f"Unsupported method ({self.command!r})")
        else:
            handler()

    def _ai_path(self) -> bool:
        path = urlsplit(self.path).path
        return path == PREFIX or path.startswith(PREFIX + "/")

    def _ai_trusted(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        origin = self.headers.get("Origin")
        return is_loopback(host) and (origin is None or origin in ALLOWED_ORIGINS)

    def _ai_answer(self, method: str) -> tuple[int, dict[str, Any]]:
        try:
            if not self._ai_trusted():  # DNS rebinding, or another site's page
                raise AiError("permission_denied", "Forbidden host or origin.")
            path = urlsplit(self.path).path
            if (method, path) == ("GET", STATUS):
                return 200, (self.ai.status() if self.ai else _not_enabled_status())
            if (method, path) != ("POST", ATTACK_PATHS):
                raise AiError("not_found", "Unknown operation.")
            if self.ai is None:
                self._ai_drain()
                raise AiError("not_enabled", "AI proposals are not enabled in this engine.")
            return 200, self.ai.attack_paths(self._ai_body())
        except AiError as exc:
            body: dict[str, Any] = {"code": exc.code, "message": exc.message}
            if exc.problems:
                body["problems"] = exc.problems[:20]
            if exc.code == "ai_unavailable" and self.ai is not None:
                body["setup"] = self.ai.llm.setup_steps()
            return ERROR_STATUS.get(exc.code, 503), {"error": body}
        except Exception:  # never a traceback or a path in the answer
            return 500, INTERNAL_ERROR

    def _ai_length(self) -> int | None:
        lengths = self.headers.get_all("Content-Length", [])
        if (
            self.headers.get("Transfer-Encoding") is not None
            or len(lengths) != 1
            or len(lengths[0]) > 9
            or not lengths[0].isascii()
            or not lengths[0].isdigit()
        ):
            return None
        return int(lengths[0])

    def _ai_drain(self) -> None:
        """Read and drop a body the route refuses, so the client can read the refusal."""
        length = self._ai_length()
        if length is None or length > MAX_BODY:
            return
        try:
            self._ai_read(length)
        except AiError:
            pass

    def _ai_body(self) -> dict[str, Any]:
        length = self._ai_length()
        if length is None or not 0 < length <= MAX_BODY:
            raise AiError("validation_error", f"Send one JSON body of at most {MAX_BODY} bytes.")
        if self.headers.get_content_type() != "application/json":
            self._ai_drain()
            raise AiError("validation_error", "Content-Type must be application/json.")
        try:
            request = json.loads(self._ai_read(length))
        except (ValueError, RecursionError) as exc:  # UnicodeDecodeError is a ValueError
            raise AiError("validation_error", "Expected a JSON object.") from exc
        if not isinstance(request, dict):
            raise AiError("validation_error", "Expected a JSON object.")
        return request

    def _ai_read(self, length: int) -> bytes:
        """The whole body within BODY_SECONDS: one deadline for all of it."""
        deadline = time.monotonic() + BODY_SECONDS
        chunks: list[bytes] = []
        remaining = length
        try:
            while remaining:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise TimeoutError
                self.connection.settimeout(left)
                chunk = self.rfile.read1(min(remaining, 1024 * 1024))
                if not chunk:
                    raise AiError("validation_error", "Incomplete request body.")
                chunks.append(chunk)
                remaining -= len(chunk)
        except OSError as exc:  # the deadline, or the client went away
            raise AiError("validation_error", "Incomplete request body.") from exc
        finally:
            self.connection.settimeout(
                BODY_SECONDS
            )  # for sending the answer; the draft itself uses no socket
        return b"".join(chunks)

    def _ai_preflight(self) -> None:
        path = urlsplit(self.path).path
        methods = {STATUS: "GET", ATTACK_PATHS: "POST"}.get(path)
        origin = self.headers.get("Origin")
        if methods is None or origin not in ALLOWED_ORIGINS or not self._ai_trusted():
            self._ai_reply(403, {"error": {"code": "permission_denied", "message": "Forbidden."}})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", methods)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _ai_reply(self, status: int, payload: Mapping[str, Any]) -> None:
        try:
            body = json.dumps(payload, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError):
            status, body = 500, json.dumps(INTERNAL_ERROR).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):  # the app went away mid-draft
            self.close_connection = True


def install_ai_routes(httpd: ThreadingHTTPServer, ai: AiService | None = None) -> None:
    """Answer /ai/* on this server: drafting with `ai`, or, with none, as not enabled.
    The server gets its own handler class, so enabling one server never enables another."""
    base = httpd.RequestHandlerClass
    httpd.RequestHandlerClass = type("AiEngineHandler", (AiRoutes, base), {"ai": ai})
