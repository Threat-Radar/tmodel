"""Loopback-only HTTP server exposing the engine to the desktop app.

ADR-0003: local-only API, no remote servers. The server refuses to bind any
address other than a loopback one.

Run:  python -m engine.api.server            (default 127.0.0.1:47811)
      TMODEL_ENGINE_PORT=0 python -m engine.api.server   (any free port)
"""

from __future__ import annotations

import ipaddress
import json
import os
import sys
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

from engine import core
from engine.api import import_route

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 47811

# Origins the Tauri webview (production and `tauri dev`) may call from.
ALLOWED_ORIGINS = frozenset(
    {
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "http://localhost:1420",
        "http://127.0.0.1:1420",
    }
)


def _attack_paths(query: dict[str, str]) -> dict[str, Any]:
    if "file" not in query:
        raise ValueError("missing query parameter: file")
    return core.attack_paths(query["file"], query.get("goal"))


def _risk(query: dict[str, str]) -> dict[str, Any]:
    for parameter in ("file", "matrix"):
        if parameter not in query:
            raise ValueError(f"missing query parameter: {parameter}")
    return core.risk_assessments(query["file"], query["matrix"], query.get("goal"))


def _tara(query: dict[str, str]) -> dict[str, Any]:
    if set(query) - {"file", "matrix"}:
        raise ValueError("tara: only file and matrix query parameters are supported")
    for parameter in ("file", "matrix"):
        if parameter not in query:
            raise ValueError(f"missing query parameter: {parameter}")
    return core.collect_tara(query["file"], query["matrix"])


def _graph(query: dict[str, str]) -> dict[str, Any]:
    if "file" not in query:
        raise ValueError("missing query parameter: file")
    return core.model_graph(query["file"])


# Each route takes the query parameters; a ValueError becomes a 400 with its message,
# and core.Unavailable a 503 with its message.
ROUTES: dict[str, Callable[[dict[str, str]], dict[str, Any]]] = {
    "/health": lambda _q: core.health(),
    "/version": lambda _q: core.version(),
    "/models": lambda _q: core.list_models(),  # the example models a reader can open (#208)
    "/graph": _graph,
    "/coverage": core.requirement_coverage,
    "/attack-paths": _attack_paths,
    "/risk": _risk,  # explicit matrix profile, with unresolved/missing ratings visible (#63)
    "/tara": _tara,  # read-only collection; file writes happen only in the CLI (#181)
    "/library": core.library_records,  # filters: id, type, topic, status (#140)
    "/library/table": core.library_table,  # rows for the table views (#141, #58)
    "/weaknesses": core.weaknesses,  # the pinned CWE release: import report, or one entry (#144)
    "/weaknesses/table": core.weakness_table,  # rows for the weakness table view (#144, #234)
    "/weaknesses/relationships": core.weakness_relationships,  # by view, with inverses (#145)
    "/attack-patterns": core.attack_patterns,  # the pinned CAPEC release, or one entry (#244)
    "/attack-patterns/table": core.attack_pattern_table,  # rows for the CAPEC table view (#236)
    "/sdl": core.sdl,  # SDL program view; no file = list SDL models (DL-0043)
    "/proposals": core.pending_proposals,  # pending proposals + saved KG views (DL-0046)
}


def is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


# The request headers each POST route accepts, for its CORS preflight (#287).
PREFLIGHT_HEADERS = {import_route.PATH: "Content-Type"}


class _ClientGone(Exception):
    """The client closed the connection part way through its request body: there is
    nobody to answer, so the request ends without a reply."""


class EngineHandler(BaseHTTPRequestHandler):
    server_version = "tmodel-engine"
    # The Import New Product route (#287) runs only when the host enables it.
    import_enabled: bool = False

    def handle(self) -> None:
        """Serve the connection. A client that goes away part way (a reset or a broken
        pipe) ends it quietly, on every route, the workspace routes' too, instead of
        printing a traceback for a reply nobody can read."""
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def _local_host(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        return is_loopback(host)

    def do_OPTIONS(self) -> None:  # noqa: N802 (http.server naming)
        """The webview's CORS preflight, which a JSON POST needs. It is answered for the
        app's origins whether or not the route is enabled, so that the app reads the
        POST's `not_enabled` rather than a failed request."""
        headers = PREFLIGHT_HEADERS.get(self.path)
        if (
            headers is None
            or self.headers.get("Origin") not in ALLOWED_ORIGINS
            or not self._local_host()
        ):
            self._send_json(
                403, {"error": {"code": "permission_denied", "message": "Forbidden preflight."}}
            )
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", headers)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 (http.server naming)
        try:
            if not self._local_host() or self.headers.get("Origin") not in (None, *ALLOWED_ORIGINS):
                raise import_route.ImportRouteError(
                    403, "permission_denied", "Forbidden host or origin."
                )
            if self.path != import_route.PATH:
                raise import_route.ImportRouteError(404, "not_found", "Unknown operation.")
            self._send_json(200, self._post_import())
        except _ClientGone:
            self.close_connection = True
        except import_route.ImportRouteError as exc:
            self._send_json(exc.status, exc.to_dict())
        except Exception:  # never drop the connection, and never send a path or a traceback
            self._send_json(
                500, {"error": {"code": "internal_error", "message": "The import failed."}}
            )

    def _post_import(self) -> dict[str, Any]:
        lengths = self.headers.get_all("Content-Length", [])
        if (
            self.headers.get("Transfer-Encoding") is not None
            or len(lengths) != 1
            or not lengths[0].isascii()
            or not lengths[0].isdigit()
            or len(lengths[0]) > 12
            or int(lengths[0]) == 0
        ):
            raise import_route.invalid("Send one JSON body with its Content-Length.")
        length = int(lengths[0])
        if length > import_route.MAX_BODY_BYTES:  # refused unread: the app checks sizes first
            raise import_route.invalid(
                f"The request is too large: each file may be at most {import_route.MAX_MIB} MiB."
            )
        # A client sends the whole body before it reads the answer, so every later refusal
        # reads and discards the body first; otherwise the client sees a closed connection.
        refusal = None
        if not self.import_enabled:
            refusal = import_route.ImportRouteError(
                503, "not_enabled", "Importing is not enabled in this engine."
            )
        elif self.headers.get_content_type() != "application/json":
            refusal = import_route.invalid("Content-Type must be application/json.")
        elif not import_route.acquire_slot():
            refusal = import_route.busy()
        if refusal is not None:
            self._drain(length, import_route.READ_SECONDS)
            raise refusal
        try:
            body = self._read_body(length, import_route.READ_SECONDS)
            return import_route.run_import(body)
        finally:
            import_route.release_slot()

    def _drain(self, length: int, seconds: float) -> None:
        """Read and discard a body the engine refuses, so that the client can read the
        refusal. Best effort, within `seconds`; nothing is kept."""
        deadline = time.monotonic() + seconds
        remaining = length
        try:
            while remaining:
                left = deadline - time.monotonic()
                if left <= 0:
                    return
                self.connection.settimeout(left)
                chunk = self.rfile.read1(min(remaining, 1024 * 1024))
                if not chunk:
                    return
                remaining -= len(chunk)
        except OSError:  # the deadline, or the client went away
            return
        finally:
            self.connection.settimeout(seconds)  # for sending the answer

    def _read_body(self, length: int, seconds: float) -> bytes:
        """The request body, all of which must arrive within `seconds`: one deadline for
        the whole body, so a client sending a byte at a time cannot hold the thread."""
        deadline = time.monotonic() + seconds
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
                    raise import_route.invalid("Incomplete request body.")
                chunks.append(chunk)
                remaining -= len(chunk)
        except TimeoutError:
            raise import_route.ImportRouteError(
                408, "request_timeout", f"The request did not arrive within {seconds} seconds."
            ) from None
        except OSError:  # the client reset the connection, or went away
            raise _ClientGone from None
        finally:
            self.connection.settimeout(seconds)  # for sending the answer
        return b"".join(chunks)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        try:
            body = json.dumps(payload).encode("utf-8")
        except (TypeError, ValueError):
            status, body = 500, b'{"error": "internal error: response not serialisable"}'
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if not is_loopback(host):  # DNS rebinding: a foreign Host is not this app
            self._send_json(403, {"error": "forbidden host"})
            return
        try:
            url = urlsplit(self.path)
            route = ROUTES.get(url.path)
            if route is None:
                self._send_json(404, {"error": "not found", "path": self.path})
                return
            query = {k: v[-1] for k, v in parse_qs(url.query, keep_blank_values=True).items()}
            status, payload = 200, route(query)
        except ValueError as exc:
            status, payload = 400, {"error": str(exc)}
        except core.Unavailable as exc:
            status, payload = 503, {"error": str(exc)}
        except Exception as exc:  # never drop the connection: the CLI would say "not running"
            status, payload = 500, {"error": f"internal error: {type(exc).__name__}"}
        self._send_json(status, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # quiet by default; the GUI polls /health


def make_server(
    host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, import_enabled: bool = False
) -> ThreadingHTTPServer:
    """Create (but do not start) the server. Raises ValueError for non-loopback hosts.
    `import_enabled` turns on the Import New Product route (#287)."""
    if not is_loopback(host):
        raise ValueError(
            f"refusing to bind non-loopback host {host!r}: the engine API is local-only"
        )
    # Per-server handler class: enabling the route on one server must not enable another.
    handler = type("ConfiguredEngineHandler", (EngineHandler,), {"import_enabled": import_enabled})
    return ThreadingHTTPServer((host, port), handler)


def _shutdown_when_stdin_closes(httpd: ThreadingHTTPServer) -> None:
    """Stop the server once stdin reaches end-of-file.

    The desktop app holds the write end of the engine's stdin, so the pipe
    closes whenever the app exits, even if it crashes or is killed (#124).
    """

    def watch() -> None:
        try:
            while sys.stdin.buffer.read(4096):
                pass
        except (OSError, ValueError):
            pass
        httpd.shutdown()

    threading.Thread(target=watch, name="stdin-watch", daemon=True).start()


def serve(
    host: str = DEFAULT_HOST,
    port: int | None = None,
    exit_with_parent: bool = False,
    *,
    import_enabled: bool = False,
    host_token: str | None = None,
) -> None:
    """Serve until stopped. With `import_enabled`, the app's Import New Product route
    answers (#287). With `host_token`, the host's secret, the host can open and create
    threat model project folders (#288); without it the /workspace/* routes answer "not
    enabled" and write nothing. The workspace routes wrap the import route's handler and
    pass every other path on to it, so the two work together."""
    from engine.api.workspace import check_host_token, install_workspace_routes
    from engine.model_workspace import ProjectWorkspace

    if port is None:
        port = int(os.environ.get("TMODEL_ENGINE_PORT", DEFAULT_PORT))
    projects = None
    if host_token is not None:
        check_host_token(host_token)  # before binding, so a bad secret fails fast
        projects = ProjectWorkspace()
    httpd = make_server(host, port, import_enabled=import_enabled)
    install_workspace_routes(httpd, projects, host_token)
    bound_host, bound_port = httpd.server_address[:2]
    print(
        f"tmodel-engine {core.version()['version']} listening on http://{bound_host}:{bound_port}",
        flush=True,
    )
    if projects is not None:
        print("project folders: on, for callers with the host token (#288)", flush=True)
    if exit_with_parent:
        _shutdown_when_stdin_closes(httpd)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
