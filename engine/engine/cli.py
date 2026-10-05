"""`tmodel` command line — the agentic surface over the same engine the GUI uses.

  tmodel serve                 start the local engine (loopback only)
  tmodel health [--json]       ask the running engine whether it is healthy
  tmodel version [--json]      ask the running engine for its version

By default `health` and `version` go through the local API, exactly like the
desktop app (APP-0001 A-030, A-060). `--in-process` calls the engine code
directly instead, for scripts that do not want a server.

Exit codes: 0 ok · 1 engine unreachable or unhealthy · 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from typing import Any

from engine import core
from engine.api import server
from engine.client import EngineUnreachable, get

LOCAL: dict[str, Callable[[], dict[str, Any]]] = {"health": core.health, "version": core.version}


def _print(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload))
        return
    if "status" in payload:
        print(f"{payload['status']} · {payload['engine']} v{payload['version']}")
    else:
        print(f"{payload['engine']} v{payload['version']} (python {payload['python']})")


def _query(args: argparse.Namespace) -> int:
    try:
        payload = LOCAL[args.command]() if args.in_process else get(f"/{args.command}", args.url)
    except EngineUnreachable as exc:
        print(f"error: {exc}\nstart it with: tmodel serve", file=sys.stderr)
        return 1
    _print(payload, args.json)
    return 0 if payload.get("status", "ok") == "ok" else 1


def _serve(args: argparse.Namespace) -> int:
    try:
        server.serve(port=args.port)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tmodel", description="tmodel engine command line")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="start the local engine (127.0.0.1 only)")
    serve.add_argument("--port", type=int, default=None, help="port (default 47811; 0 = any)")
    serve.set_defaults(func=_serve)

    for name, text in (("health", "engine health"), ("version", "engine version")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--json", action="store_true", help="print JSON")
        cmd.add_argument("--url", default=None, help="engine URL (default http://127.0.0.1:47811)")
        cmd.add_argument(
            "--in-process", action="store_true", help="call the engine directly, no server"
        )
        cmd.set_defaults(func=_query)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
