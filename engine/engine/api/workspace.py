"""Opt-in HTTP routes for threat model projects (#288, DL-0075).

`serve()` installs them on every server it starts. They work only when the host starts
the engine with project folders on (`tmodel serve --projects`, with a secret in
TMODEL_HOST_TOKEN). Otherwise each answers 503 workspace_failure and touches no file,
so the default launch stays read-only.

Every request needs `Authorization: Bearer <the host's secret>`, which the host keeps
in memory and may give to its own webview. The host routes take paths, so they also
refuse a request with an Origin header, which every browser request has: only the
desktop host passes a folder or file path in, and every answer names models by
opaque ids.

    POST /workspace/host/create-project  {"path", "source_file" or "model_id", "name"?}
    POST /workspace/host/open-project    {"path"}
    POST /workspace/host/open-file       {"path"}
    GET  /workspace/models                             the models open in this engine
    GET  /workspace/model?model_id=M[&revision=R]      a model at its current or an exact version
    GET  /workspace/versions?model_id=M[&revision=R]   version metadata, oldest first, through R

"Save New Version" is not a route here: it is the #289 review service calling
ProjectWorkspace.commit, with its own sessions and permissions. Errors are ReviewError
bodies (engine/review_workspace.py).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from http.server import ThreadingHTTPServer
from secrets import compare_digest
from typing import Any
from urllib.parse import parse_qs, urlsplit

from engine.api.server import ALLOWED_ORIGINS, is_loopback
from engine.model_workspace import ProjectWorkspace
from engine.review_workspace import ReviewError

PREFIX = "/workspace"
MAX_BODY = 16384  # a path and a few short fields
MAX_PARAMETERS = 8
BODY_TIMEOUT_S = 5.0  # how long a whole request body may take to arrive
MIN_TOKEN_LENGTH = 32
MAX_TOKEN_LENGTH = 512
# The status for each ReviewError code, as the review routes (#289) answer them.
ERROR_STATUS = {
    "validation_error": 422,
    "permission_denied": 403,
    "not_found": 404,
    "revision_conflict": 409,
    "save_failure": 503,
    "workspace_failure": 503,
}
INTERNAL_ERROR = {"error": {"code": "internal_error", "message": "Workspace operation failed."}}

Reply = tuple[int, dict[str, Any]]


def check_host_token(token: Any) -> str:
    """The host's secret: 32 to 512 printable ASCII characters, no spaces.

    `secrets.token_urlsafe(32)` makes one. Raises ValueError, never echoing the value.
    """
    if (
        not isinstance(token, str)
        or not MIN_TOKEN_LENGTH <= len(token) <= MAX_TOKEN_LENGTH
        or not token.isascii()
        or not token.isprintable()
        or any(character.isspace() for character in token)
    ):
        raise ValueError(
            f"the host token must be {MIN_TOKEN_LENGTH} to {MAX_TOKEN_LENGTH} printable "
            "ASCII characters with no spaces"
        )
    return token


def _invalid(field: str, message: str) -> ReviewError:
    return ReviewError("validation_error", message, field=field[:64])


def _parameters(
    query: Mapping[str, list[str]], allowed: tuple[str, ...] = (), required: tuple[str, ...] = ()
) -> dict[str, str]:
    for name, values in query.items():
        if name not in allowed:
            raise _invalid(name, "Unknown query parameter.")
        if len(values) != 1:
            raise _invalid(name, "Give this query parameter once.")
    for name in required:
        if name not in query:
            raise _invalid(name, "This query parameter is required.")
    return {name: values[0] for name, values in query.items()}


def _fields(body: Mapping[str, Any], allowed: tuple[str, ...], required: tuple[str, ...]) -> None:
    for name in body:
        if name not in allowed:
            raise _invalid(name, "Unknown field.")
    for name in required:
        if name not in body:
            raise _invalid(name, "This field is required.")


def _create_project(workspace: ProjectWorkspace, body: Mapping[str, Any]) -> Reply:
    _fields(body, ("path", "source_file", "model_id", "name"), ("path",))
    project = workspace.create_project(
        body["path"],
        source_file=body.get("source_file"),
        model_id=body.get("model_id"),
        name=body.get("name"),
    )
    return 201, project


def _open_project(workspace: ProjectWorkspace, body: Mapping[str, Any]) -> Reply:
    _fields(body, ("path",), ("path",))
    return 200, workspace.open_project(body["path"])


def _open_file(workspace: ProjectWorkspace, body: Mapping[str, Any]) -> Reply:
    _fields(body, ("path",), ("path",))
    return 200, workspace.open_file(body["path"])


def _list(workspace: ProjectWorkspace, query: Mapping[str, list[str]]) -> Reply:
    _parameters(query)
    return 200, workspace.list_models()


def _model(workspace: ProjectWorkspace, query: Mapping[str, list[str]]) -> Reply:
    values = _parameters(query, ("model_id", "revision"), ("model_id",))
    return 200, workspace.open_model(values["model_id"], values.get("revision"))


def _versions(workspace: ProjectWorkspace, query: Mapping[str, list[str]]) -> Reply:
    values = _parameters(query, ("model_id", "revision"), ("model_id",))
    return 200, workspace.list_versions(values["model_id"], values.get("revision"))


# (method, path) -> (operation, whether only the desktop host may call it)
OPERATIONS: dict[tuple[str, str], tuple[Callable[[ProjectWorkspace, Any], Reply], bool]] = {
    ("POST", "/workspace/host/create-project"): (_create_project, True),
    ("POST", "/workspace/host/open-project"): (_open_project, True),
    ("POST", "/workspace/host/open-file"): (_open_file, True),
    ("GET", "/workspace/models"): (_list, False),
    ("GET", "/workspace/model"): (_model, False),
    ("GET", "/workspace/versions"): (_versions, False),
}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> Any:
    raise ValueError("nonfinite value")


class WorkspaceRoutes:
    """Mixed in ahead of the engine's handler: answers /workspace/*, passes the rest on."""

    workspace: ProjectWorkspace | None = None
    host_token: str | None = None

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        if self._is_workspace_path():
            self._reply(*self._answer("GET"))
        else:
            super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self._is_workspace_path():
            self._reply(*self._answer("POST"))
        else:
            self._pass_on("do_POST")

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self._is_workspace_path():
            self._preflight()
        else:
            self._pass_on("do_OPTIONS")

    def _pass_on(self, method: str) -> None:
        handler = getattr(super(), method, None)
        if handler is None:  # what http.server answers for a method it has no handler for
            self.send_error(501, f"Unsupported method ({self.command!r})")
        else:
            handler()

    def _is_workspace_path(self) -> bool:
        path = urlsplit(self.path).path
        return path == PREFIX or path.startswith(PREFIX + "/")

    def _trusted(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        origin = self.headers.get("Origin")
        return is_loopback(host) and (origin is None or origin in ALLOWED_ORIGINS)

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        if self.host_token is None or not header.startswith("Bearer ") or not header.isascii():
            return False
        return compare_digest(header[len("Bearer ") :], self.host_token)

    def _answer(self, method: str) -> Reply:
        try:
            if not self._trusted():  # DNS rebinding, or another site's page
                raise ReviewError("permission_denied", "Forbidden host or origin.")
            url = urlsplit(self.path)
            route = OPERATIONS.get((method, url.path))
            if route is None:
                return 404, {"error": {"code": "not_found", "message": "Unknown operation."}}
            operation, host_only = route
            if self.workspace is None:
                raise ReviewError(
                    "workspace_failure", "Project folders are not enabled in this engine."
                )
            if not self._authorized():
                raise ReviewError("permission_denied", "The host's session token is required.")
            if host_only and self.headers.get("Origin") is not None:
                raise ReviewError(
                    "permission_denied", "Only the desktop host can pass a folder or file path."
                )
            argument = self._body() if method == "POST" else self._query(url.query)
            return operation(self.workspace, argument)
        except ReviewError as exc:
            return ERROR_STATUS.get(exc.code, 503), exc.to_dict()
        except Exception:  # never a traceback or a path in the answer
            return 500, INTERNAL_ERROR

    @staticmethod
    def _query(query: str) -> dict[str, list[str]]:
        try:
            return parse_qs(query, keep_blank_values=True, max_num_fields=MAX_PARAMETERS)
        except ValueError as exc:
            raise _invalid("request", "Too many query parameters.") from exc

    def _body(self) -> dict[str, Any]:
        if self.headers.get_content_type() != "application/json":
            raise _invalid("request", "Content-Type must be application/json.")
        lengths = self.headers.get_all("Content-Length", [])
        if (
            self.headers.get("Transfer-Encoding") is not None
            or len(lengths) != 1
            or len(lengths[0]) > 6
            or not lengths[0].isascii()
            or not lengths[0].isdigit()
            or not 0 < int(lengths[0]) <= MAX_BODY
        ):
            raise _invalid("request", f"Provide a JSON body of at most {MAX_BODY} bytes.")
        body = self._read_body(int(lengths[0]))
        try:
            request = json.loads(
                body, object_pairs_hook=_unique_object, parse_constant=_reject_constant
            )
        except (ValueError, RecursionError) as exc:  # UnicodeDecodeError is a ValueError
            raise _invalid("request", "Expected a JSON object with unique fields.") from exc
        if not isinstance(request, dict):
            raise _invalid("request", "Expected a JSON object with unique fields.")
        return request

    def _read_body(self, length: int) -> bytes:
        """The whole body within BODY_TIMEOUT_S: one deadline for all of it, so a client
        sending a byte at a time cannot hold the engine's thread."""
        deadline = time.monotonic() + BODY_TIMEOUT_S
        chunks: list[bytes] = []
        remaining = length
        try:
            while remaining:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise TimeoutError
                self.connection.settimeout(left)
                chunk = self.rfile.read1(min(remaining, 65536))
                if not chunk:
                    raise _invalid("request", "Incomplete request body.")
                chunks.append(chunk)
                remaining -= len(chunk)
        except OSError as exc:  # the deadline (TimeoutError), or the client went away
            raise _invalid("request", "Incomplete request body.") from exc
        finally:
            self.connection.settimeout(BODY_TIMEOUT_S)  # a deadline for sending the answer
        return b"".join(chunks)

    def _preflight(self) -> None:
        """Browsers may ask before calling the app routes; never the host routes."""
        path = urlsplit(self.path).path
        methods = sorted(
            method
            for (method, route), (_, host_only) in OPERATIONS.items()
            if route == path and not host_only
        )
        origin = self.headers.get("Origin")
        if not methods or origin not in ALLOWED_ORIGINS or not self._trusted():
            self._reply(403, {"error": {"code": "permission_denied", "message": "Forbidden."}})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", ", ".join(methods))
        self.send_header("Access-Control-Allow-Headers", "Authorization")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _reply(self, status: int, payload: Mapping[str, Any]) -> None:
        try:
            body = json.dumps(payload, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError):
            status, body = 500, json.dumps(INTERNAL_ERROR).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")  # a project's current version changes
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)


def install_workspace_routes(
    httpd: ThreadingHTTPServer,
    workspace: ProjectWorkspace | None = None,
    host_token: str | None = None,
) -> None:
    """Answer /workspace/* on this server: from `workspace`, for callers with
    `host_token`, or, with no workspace, as not enabled.

    The server gets its own handler class, so enabling one server never enables another.
    """
    token = None if workspace is None else check_host_token(host_token)
    base = httpd.RequestHandlerClass
    httpd.RequestHandlerClass = type(
        "WorkspaceEngineHandler",
        (WorkspaceRoutes, base),
        {"workspace": workspace, "host_token": token},
    )
