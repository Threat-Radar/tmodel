#!/usr/bin/env python3
"""Build the engine-free browser preview under docs/app/ (Issue #204).

The application bundle is the existing Vite frontend built in ``pages`` mode.
The data files are exact, path-sanitised engine responses for every model that
``GET /models`` lists, plus the complete ``GET /library/table`` response.

    engine/.venv/bin/python docs/publishing/render_app.py
    engine/.venv/bin/python docs/publishing/render_app.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "app"
APP = ROOT / "apps" / "desktop"
sys.path.insert(0, str(ROOT / "engine"))

try:
    from engine import core
except ImportError as exc:
    raise SystemExit(
        f"render_app: cannot import the engine ({exc}); run with engine/.venv/bin/python"
    ) from exc


FORBIDDEN_PUBLIC_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:sk|rk)-(?:live|proj)-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\b[A-Za-z]:\\\\Users\\\\", re.IGNORECASE),
)


def _write_json(path: Path, payload: Any) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    local_markers = (str(ROOT), "/Users/", "/home/", "/private/var/", "/var/folders/")
    leaked = next((marker for marker in local_markers if marker in text), None)
    if leaked:
        raise RuntimeError(
            f"{path.name}: generated public data contains local path marker {leaked!r}"
        )
    secret = next(
        (
            pattern.pattern
            for pattern in FORBIDDEN_PUBLIC_PATTERNS
            if pattern.search(text)
        ),
        None,
    )
    if secret:
        raise RuntimeError(
            f"{path.name}: generated public data contains credential marker {secret!r}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _public_file(payload: dict[str, Any], file: str) -> dict[str, Any]:
    """Replace the engine's approved absolute model path with its public file name."""
    return {**payload, "file": file}


def write_data(out: Path) -> tuple[int, int]:
    listing = core.list_models()
    if listing["problems"]:
        detail = "; ".join(f"{p['file']}: {p['error']}" for p in listing["problems"])
        raise RuntimeError(f"refusing to omit model data: {detail}")
    if not listing["models"] or listing["count"] != len(listing["models"]):
        raise RuntimeError("the engine returned an empty or inconsistent model catalog")

    _write_json(out / "data" / "models.json", listing)
    for summary in listing["models"]:
        model_id = summary["id"]
        file = summary["file"]
        if Path(file).stem != model_id:
            raise RuntimeError(
                f"model id {model_id!r} does not match public file name {file!r}"
            )
        model_dir = out / "data" / "models" / model_id
        graph = core.model_graph(file)
        local_file = graph["file"]
        _write_json(model_dir / "graph.json", _public_file(graph, file))

        index = core.attack_paths(local_file)
        _write_json(
            model_dir / "attack-paths" / "index.json", _public_file(index, file)
        )
        goal_files = []
        for number, goal in enumerate(index["threats"], start=1):
            name = f"goal-{number:03d}.json"
            response = core.attack_paths(local_file, goal)
            _write_json(model_dir / "attack-paths" / name, _public_file(response, file))
            goal_files.append({"goal": goal, "file": name})
        _write_json(model_dir / "attack-paths" / "goals.json", {"goals": goal_files})

    library = core.library_table()
    if library["library"]["problems"]:
        raise RuntimeError(
            "refusing to publish an incomplete library table: "
            + "; ".join(library["library"]["problems"])
        )
    if (
        library["count"] != library["total"]
        or library["total"] != library["library"]["count"]
    ):
        raise RuntimeError(
            "the unfiltered library table did not contain every loaded record"
        )
    _write_json(out / "data" / "library" / "table.json", library)
    return len(listing["models"]), library["count"]


def _build(out: Path) -> tuple[int, int]:
    env = os.environ.copy()
    env["TMODEL_APP_OUT_DIR"] = str(out)
    subprocess.run(["npm", "run", "build:pages"], cwd=APP, env=env, check=True)
    return write_data(out)


def write(out: Path) -> tuple[int, int]:
    """Build completely beside ``out``, then replace only that destination."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not out.is_dir():
        raise RuntimeError(f"{out} exists but is not a directory")
    with tempfile.TemporaryDirectory(prefix=f".{out.name}-", dir=out.parent) as tmp:
        scratch = Path(tmp)
        staged = scratch / "generated"
        result = _build(staged)

        # A failed build never reaches this point. If either rename fails, put
        # the prior valid tree back; TemporaryDirectory then removes only the
        # private staging/backup directory created above.
        previous = scratch / "previous"
        had_previous = out.exists()
        if had_previous:
            out.rename(previous)
        try:
            staged.rename(out)
        except BaseException:
            if had_previous and previous.exists() and not out.exists():
                previous.rename(out)
            raise
        return result


def _files(root: Path) -> dict[Path, bytes]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def check() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "app"
        models, records = _build(fresh)
        expected = _files(fresh)
        current = _files(OUT)
    stale = sorted(
        set(expected) ^ set(current)
        | {
            path
            for path in expected.keys() & current.keys()
            if expected[path] != current[path]
        }
    )
    if stale:
        print("render_app: docs/app/ is out of date:", file=sys.stderr)
        for path in stale:
            print(f"  {path}", file=sys.stderr)
        return 1
    print(
        f"render_app: docs/app/ is up to date ({models} models, {records} library records)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="fail if docs/app/ is out of date"
    )
    args = parser.parse_args()
    if args.check:
        return check()
    models, records = write(OUT)
    print(f"render_app: wrote docs/app/ ({models} models, {records} library records)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f"render_app: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
