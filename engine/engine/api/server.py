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
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

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

ROUTES: dict[str, Callable[[], dict[str, Any]]] = {
    "/health": core.health,
    "/version": core.version,
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
        body = json.dumps(payload).encode("utf-8")
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
        route = ROUTES.get(self.path.split("?", 1)[0])
        if route is None:
            self._send_json(404, {"error": "not found", "path": self.path})
            return
        self._send_json(200, route())

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # quiet by default; the GUI polls /health


def make_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """Create (but do not start) the server. Raises ValueError for non-loopback hosts."""
    if not is_loopback(host):
        raise ValueError(
            f"refusing to bind non-loopback host {host!r}: the engine API is local-only"
        )
    return ThreadingHTTPServer((host, port), EngineHandler)


def serve(host: str = DEFAULT_HOST, port: int | None = None) -> None:
    if port is None:
        port = int(os.environ.get("TMODEL_ENGINE_PORT", DEFAULT_PORT))
    httpd = make_server(host, port)
    bound_host, bound_port = httpd.server_address[:2]
    print(
        f"tmodel-engine {core.version()['version']} listening on http://{bound_host}:{bound_port}",
        flush=True,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
