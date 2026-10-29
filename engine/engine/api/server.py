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
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

from engine import core

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


# Each route takes the query parameters; a ValueError becomes a 400 with its message.
ROUTES: dict[str, Callable[[dict[str, str]], dict[str, Any]]] = {
    "/health": lambda _q: core.health(),
    "/version": lambda _q: core.version(),
    "/attack-paths": _attack_paths,
}


def is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class EngineHandler(BaseHTTPRequestHandler):
    server_version = "tmodel-engine"

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
        except Exception as exc:  # never drop the connection: the CLI would say "not running"
            status, payload = 500, {"error": f"internal error: {type(exc).__name__}"}
        self._send_json(status, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # quiet by default; the GUI polls /health


def make_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """Create (but do not start) the server. Raises ValueError for non-loopback hosts."""
    if not is_loopback(host):
        raise ValueError(
            f"refusing to bind non-loopback host {host!r}: the engine API is local-only"
        )
    return ThreadingHTTPServer((host, port), EngineHandler)


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
    host: str = DEFAULT_HOST, port: int | None = None, exit_with_parent: bool = False
) -> None:
    if port is None:
        port = int(os.environ.get("TMODEL_ENGINE_PORT", DEFAULT_PORT))
    httpd = make_server(host, port)
    bound_host, bound_port = httpd.server_address[:2]
    print(
        f"tmodel-engine {core.version()['version']} listening on http://{bound_host}:{bound_port}",
        flush=True,
    )
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
