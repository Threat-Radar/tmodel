"""`tmodel` command line — the agentic surface over the same engine the GUI uses.

  tmodel serve                 start the local engine (loopback only)
  tmodel health [--json]       ask the running engine whether it is healthy
  tmodel version [--json]      ask the running engine for its version
  tmodel paths FILE [--goal G] [--json]
                               attack paths to a step or threat in a model file;
                               without --goal, list the file's threats

By default these go through the local API, exactly like the desktop app
(APP-0001 A-030, A-060). `--in-process` calls the engine code directly
instead, for scripts that do not want a server.

Exit codes: 0 ok · 1 engine unreachable, unhealthy or an engine error · 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from engine import core
from engine.api import server
from engine.client import EngineError, EngineUnreachable, get
from engine.graph import GraphError

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


def _short(step_id: str) -> str:
    return step_id.split(":", 1)[-1]


def _print_paths(payload: dict[str, Any]) -> None:
    if "goal" not in payload:
        print(f"{payload['file']}: {payload['steps']} steps; threats:")
        for threat in payload["threats"]:
            print(f"  {threat}")
        return
    paths = payload["paths"]
    print(f"{payload['goal']}: {len(paths)} path{'s' if len(paths) != 1 else ''}")
    for i, path in enumerate(paths, 1):
        print(f"  {i}. " + " -> ".join(_short(s) for s in path["steps"]))


def _paths(args: argparse.Namespace) -> int:
    file = str(Path(args.file).resolve())  # the server may run from another directory
    try:
        if args.in_process:
            payload = core.attack_paths(file, args.goal)
        else:
            params = {"file": file, **({"goal": args.goal} if args.goal else {})}
            payload = get("/attack-paths", args.url, params=params)
    except EngineUnreachable as exc:
        print(f"error: {exc}\nstart it with: tmodel serve", file=sys.stderr)
        return 1
    except (EngineError, GraphError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_paths(payload)
    return 0


def _add_transport(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument("--json", action="store_true", help="print JSON")
    cmd.add_argument("--url", default=None, help="engine URL (default http://127.0.0.1:47811)")
    cmd.add_argument(
        "--in-process", action="store_true", help="call the engine directly, no server"
    )


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
        _add_transport(cmd)
        cmd.set_defaults(func=_query)

    paths = sub.add_parser("paths", help="attack paths in a model file (#63)")
    paths.add_argument(
        "file", help="model file, e.g. spec/vectors/mvp-01-software-doc-service.yaml"
    )
    paths.add_argument("--goal", default=None, help="step or threat id; omit to list threats")
    _add_transport(paths)
    paths.set_defaults(func=_paths)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
