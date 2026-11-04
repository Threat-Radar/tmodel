"""`tmodel` command line — the agentic surface over the same engine the GUI uses.

  tmodel serve                 start the local engine (loopback only)
  tmodel health [--json]       ask the running engine whether it is healthy
  tmodel version [--json]      ask the running engine for its version
  tmodel paths FILE [--goal G] [--json]
                               attack paths to a step or threat in a model file;
                               without --goal, list the file's threats
  tmodel library [--id I] [--type T] [--topic T] [--status S] [--json]
                               the library's records, optionally filtered; the
                               library is $TMODEL_LIBRARY or the pinned submodule

By default these go through the local API, exactly like the desktop app
(APP-0001 A-030, A-060). `--in-process` calls the engine code directly
instead, for scripts that do not want a server.

Exit codes: 0 ok · 1 engine unreachable, unhealthy or an engine error · 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from typing import Any

from engine import core
from engine.api import server
from engine.client import EngineError, EngineTimeout, EngineUnreachable, get

LOCAL: dict[str, Callable[[], dict[str, Any]]] = {"health": core.health, "version": core.version}


def _print(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload))
        return
    if "status" in payload:
        print(f"{payload['status']} · {payload['engine']} v{payload['version']}")
    else:
        print(f"{payload['engine']} v{payload['version']} (python {payload['python']})")


PATHS_TIMEOUT_S = 60.0  # enumeration can take longer than /health


def _call(fetch: Callable[[], dict[str, Any]]) -> dict[str, Any] | None:
    """Run a request; on failure print one error line (no traceback) and return None."""
    try:
        return fetch()
    except EngineTimeout as exc:
        print(f"error: {exc}; it may still be working (try --in-process)", file=sys.stderr)
    except EngineUnreachable as exc:
        print(f"error: {exc}\nstart it with: tmodel serve", file=sys.stderr)
    except (EngineError, ValueError, core.Unavailable) as exc:  # ValueError covers GraphError
        print(f"error: {exc}", file=sys.stderr)
    return None


def _query(args: argparse.Namespace) -> int:
    payload = _call(
        lambda: LOCAL[args.command]() if args.in_process else get(f"/{args.command}", args.url)
    )
    if payload is None:
        return 1
    _print(payload, args.json)
    return 0 if payload.get("status", "ok") == "ok" else 1


def _short(step_id: str) -> str:
    return step_id.split(":", 1)[-1]


def _review_note(review: dict[str, Any]) -> str:
    """Empty for a reviewed path; otherwise says why it is not (R-018)."""
    if review.get("reviewed"):
        return ""
    recorded = review.get("review_status") or review.get("assertion_status")
    return f"  [not reviewed: {recorded}]" if recorded else "  [not reviewed]"


def _print_paths(payload: dict[str, Any]) -> None:
    if "goal" not in payload:
        reviewed = set(payload.get("reviewed_threats", []))
        print(f"{payload['file']}: {payload['steps']} steps; threats:")
        for threat in payload["threats"]:
            print(f"  {threat}" + ("" if threat in reviewed else "  [not reviewed]"))
        return
    paths = payload["paths"]
    print(f"{payload['goal']}: {len(paths)} path{'s' if len(paths) != 1 else ''}")
    for i, path in enumerate(paths, 1):
        steps = " -> ".join(_short(s) for s in path["steps"])
        print(f"  {i}. {steps}{_review_note(path.get('review', {}))}")


def _paths(args: argparse.Namespace) -> int:
    # absolute, without following symlinks: the server may run from another directory
    file = os.path.abspath(args.file)
    params = {"file": file, **({"goal": args.goal} if args.goal is not None else {})}
    payload = _call(
        lambda: (
            core.attack_paths(file, args.goal)
            if args.in_process
            else get("/attack-paths", args.url, timeout=PATHS_TIMEOUT_S, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_paths(payload)
    return 0


LIBRARY_TIMEOUT_S = 60.0  # the engine's first request loads every record


def _print_library(payload: dict[str, Any]) -> None:
    records, library = payload["records"], payload["library"]
    print(f"{payload['count']} of {library['count']} records in {library['root']}")
    columns = ("id", "type", "status")
    width = {c: max((len(r[c]) for r in records), default=0) for c in columns}
    for r in records:
        cells = "  ".join(f"{r[c]:<{width[c]}}" for c in columns)
        print(f"  {cells}  {r['title']}")


def _library(args: argparse.Namespace) -> int:
    filters = {name: getattr(args, name) for name in core.LIBRARY_FILTERS}
    filters = {name: value for name, value in filters.items() if value is not None}
    payload = _call(
        lambda: (
            core.library_records(filters)
            if args.in_process
            else get("/library", args.url, timeout=LIBRARY_TIMEOUT_S, params=filters)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_library(payload)
    problems = payload["library"]["problems"]
    if problems:  # the records that loaded are printed; say what is missing
        noun = "record" if len(problems) == 1 else "records"
        print(
            f"warning: {len(problems)} library {noun} failed to load; --json lists them",
            file=sys.stderr,
        )
        return 1
    return 0


def _add_transport(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument("--json", action="store_true", help="print JSON")
    cmd.add_argument("--url", default=None, help="engine URL (default http://127.0.0.1:47811)")
    cmd.add_argument(
        "--in-process", action="store_true", help="call the engine directly, no server"
    )


def _serve(args: argparse.Namespace) -> int:
    try:
        server.serve(port=args.port, exit_with_parent=args.exit_with_parent)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tmodel", description="tmodel engine command line")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="start the local engine (127.0.0.1 only)")
    serve.add_argument("--port", type=int, default=None, help="port (default 47811; 0 = any)")
    serve.add_argument(
        "--exit-with-parent",
        action="store_true",
        help="stop when stdin closes (the desktop app starts the engine this way)",
    )
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

    library = sub.add_parser("library", help="the library's records (#140)")
    for name in core.LIBRARY_FILTERS:
        library.add_argument(f"--{name}", default=None, help=f"only records with this {name}")
    _add_transport(library)
    library.set_defaults(func=_library)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
