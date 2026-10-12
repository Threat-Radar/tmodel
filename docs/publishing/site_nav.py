"""Shared site chrome for every generated page under docs/.

Reads docs/publishing/site.yaml. `header(depth, current)` returns the top
navigation for a page `depth` directories below docs/. It carries its own
<style> so it renders the same on a bibliography view, a report, or a
library record page copied in from the submodule. Stdlib only.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE_PATH = ROOT / "docs" / "publishing" / "site.yaml"
sys.path.insert(0, str(ROOT / "library" / "bin"))
from _record_yaml import load_yaml  # noqa: E402  (pinned library submodule)

STYLE = (
    "<style>"
    ".site-nav{border-bottom:1px solid #e2dcd0;background:#fffcf7;"
    "font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
    ".site-nav .bar{max-width:920px;margin:0 auto;padding:14px 24px;display:flex;flex-wrap:wrap;"
    "align-items:baseline;justify-content:space-between;gap:10px 18px}"
    ".site-nav .mark{font-weight:650;letter-spacing:-0.03em;color:#1a1916;text-decoration:none}"
    ".site-nav nav{display:flex;flex-wrap:wrap;gap:14px;font-size:.92rem}"
    ".site-nav nav a{color:#5c574e;text-decoration:none}"
    ".site-nav nav a[aria-current=page]{color:#1a1916;font-weight:650}"
    "</style>"
)


def nav_items() -> list[dict]:
    items = load_yaml(SITE_PATH).get("nav") or []
    if not items:
        raise SystemExit(f"{SITE_PATH}: nav is empty")
    return items


def header(depth: int, current: str = "") -> str:
    """Site nav for a page `depth` levels below docs/. `current` is a nav href."""
    up = "../" * depth
    links = []
    for item in nav_items():
        href = str(item["href"])
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{html.escape(up + href)}"{cur}>{html.escape(str(item["label"]))}</a>')
    title = html.escape(str(load_yaml(SITE_PATH).get("title") or "tmodel"))
    return (
        f'{STYLE}<header class="site-nav"><div class="bar">'
        f'<a class="mark" href="{html.escape(up)}index.html">{title}</a>'
        f'<nav aria-label="Site">{"".join(links)}</nav></div></header>'
    )
