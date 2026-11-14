#!/usr/bin/env python3
"""Build docs/models/: one static report page per example model, and an index (#208).

The engine collects each model (the same `/models`, `/graph` and `/attack-paths`
code the app calls), and the app's own report renderer writes the HTML
(apps/desktop/src/report-render.ts, run by Node), so a page and the app's Model
report view cannot disagree. Pages are self-contained: CSS inline, no script, no
remote asset, relative links (docs/publishing/SKILL.md).

The engine needs PyYAML, so run this with the engine's Python, and Node 22.6 or
newer must be on PATH (it runs the TypeScript renderer with
--experimental-strip-types, which Node added in 22.6.0):

    engine/.venv/bin/python docs/publishing/render_models.py           # write docs/models/
    engine/.venv/bin/python docs/publishing/render_models.py --check   # fail if out of date

The site nav comes from site.yaml through site_nav.py, which reads it with the
pinned library submodule's YAML reader.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "models"
WRITER = ROOT / "apps" / "desktop" / "scripts" / "render-model-pages.mjs"
SOURCE_BASE_URL = "https://github.com/Threat-Radar/tmodel/blob/main/spec/vectors"
MIN_NODE = (22, 6)
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from engine import core  # noqa: E402
except ImportError as exc:  # PyYAML missing: not the engine's Python
    raise SystemExit(
        f"render_models: cannot import the engine ({exc}); run with engine/.venv/bin/python"
    ) from exc
from site_nav import header  # noqa: E402  (needs the library submodule)


def collect() -> dict:
    """Every example model as the app sees it, with no local path in the result."""
    listing = core.list_models()
    models = []
    for summary in listing["models"]:
        graph = core.model_graph(summary["file"])
        local = graph["file"]  # absolute on this machine; /attack-paths needs it
        goals = core.attack_paths(local)["threats"]
        paths = [core.attack_paths(local, goal) for goal in goals]
        models.append(
            {
                "summary": summary,
                "graph": {**graph, "file": summary["file"]},
                "attack_paths": [{**p, "file": summary["file"]} for p in paths],
            }
        )
    return {
        "nav_html": header(1, ""),
        "source_base_url": SOURCE_BASE_URL,
        "models": models,
        "problems": listing["problems"],
    }


def node_executable() -> str:
    """Node, if it is new enough to run the renderer's TypeScript directly."""
    wanted = ".".join(map(str, MIN_NODE))
    node = shutil.which("node")
    if node is None:
        raise SystemExit(f"render_models: Node {wanted} or newer is needed to run the app's renderer")
    version = subprocess.run(
        [node, "--version"], capture_output=True, text=True, check=True
    ).stdout.strip()
    try:
        found = tuple(int(part) for part in version.lstrip("v").split(".")[:2])
    except ValueError:
        found = (0, 0)
    if found < MIN_NODE:
        raise SystemExit(
            f"render_models: Node {version} is too old; {wanted} or newer runs the renderer"
            " (--experimental-strip-types)"
        )
    return node


def write(out: Path) -> None:
    node = node_executable()
    with tempfile.TemporaryDirectory() as tmp:
        bundle = Path(tmp) / "models.json"
        bundle.write_text(json.dumps(collect(), sort_keys=True), encoding="utf-8")
        subprocess.run(
            [node, "--experimental-strip-types", "--no-warnings", str(WRITER), str(bundle), str(out)],
            check=True,
            cwd=ROOT,
        )


def check() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "models"
        write(fresh)
        if not OUT.is_dir():
            print("render_models: docs/models/ is missing; run without --check", file=sys.stderr)
            return 1
        names = {p.name for p in fresh.glob("*.html")} | {p.name for p in OUT.glob("*.html")}
        stale = sorted(
            n
            for n in names
            if not (fresh / n).exists()
            or not (OUT / n).exists()
            or not filecmp.cmp(fresh / n, OUT / n, shallow=False)
        )
    if stale:
        print(f"render_models: out of date: {', '.join(stale)}", file=sys.stderr)
        return 1
    print(f"render_models: docs/models/ is up to date ({len(names)} pages)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if docs/models/ is out of date")
    args = parser.parse_args()
    if args.check:
        return check()
    write(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
