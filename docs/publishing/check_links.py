#!/usr/bin/env python3
"""Fail if a published page under docs/ links to a local path that does not exist.

Checks ``href`` and ``src``. GitHub Pages project-root links beginning
``/tmodel/`` resolve below docs/. External links and in-page anchors are ignored.
Stdlib only.

    python3 docs/publishing/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

DOCS = Path(__file__).resolve().parents[2] / "docs"
LOCAL_ATTRIBUTE = re.compile(r'(?:href|src)="([^"]+)"')
PAGES_ROOT = "/tmodel/"


def check_links(docs: Path = DOCS) -> list[tuple[Path, str]]:
    broken = []
    pages = sorted(docs.rglob("*.html"))
    for page in pages:
        for target in LOCAL_ATTRIBUTE.findall(page.read_text(errors="replace")):
            parsed = urlsplit(target)
            if not parsed.path or parsed.scheme or parsed.netloc:
                continue
            if parsed.path.startswith(PAGES_ROOT):
                path = docs / unquote(parsed.path.removeprefix(PAGES_ROOT))
            elif parsed.path.startswith("/"):
                broken.append((page.relative_to(docs), target))
                continue
            else:
                path = page.parent / unquote(parsed.path)
            path = path.resolve()
            try:
                path.relative_to(docs.resolve())
            except ValueError:
                broken.append((page.relative_to(docs), target))
                continue
            if path.is_dir():
                path = path / "index.html"
            if not path.exists():
                broken.append((page.relative_to(docs), target))
    return broken


def main() -> int:
    pages = sorted(DOCS.rglob("*.html"))
    broken = check_links()
    for page, target in broken:
        print(f"  {page}: {target}", file=sys.stderr)
    if broken:
        print(f"check_links: {len(broken)} broken relative links", file=sys.stderr)
        return 1
    print(f"check_links: {len(pages)} pages, every relative link resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
