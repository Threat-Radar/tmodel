#!/usr/bin/env python3
"""Fail if a generated page under docs/ links to a relative path that does not exist.

External links (http:, https:, mailto:) and in-page anchors are not checked.
Stdlib only.

    python3 docs/publishing/check_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / "docs"
HREF = re.compile(r'href="([^"#]*)(?:#[^"]*)?"')


def main() -> int:
    broken = []
    pages = sorted(DOCS.rglob("*.html"))
    for page in pages:
        for target in HREF.findall(page.read_text(errors="replace")):
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target):
                continue
            path = (page.parent / target).resolve()
            if path.is_dir():
                path = path / "index.html"
            if not path.exists():
                broken.append((page.relative_to(DOCS), target))
    for page, target in broken:
        print(f"  {page}: {target}", file=sys.stderr)
    if broken:
        print(f"check_links: {len(broken)} broken relative links", file=sys.stderr)
        return 1
    print(f"check_links: {len(pages)} pages, every relative link resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
