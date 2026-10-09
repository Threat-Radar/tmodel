#!/usr/bin/env python3
"""Fail if any protected personal identity appears in a published page.

Scans docs/**/*.html against publishing/identities.yaml (kept OUTSIDE docs/ so
the list is never itself published). That tracked file holds GITHUB IDS ONLY —
never real names — because the repo is world-viewable and the list must not leak
identities. Real names, if you want them matched too, go in an untracked local
override, publishing/identities.local.yaml (gitignored), merged here when present.
Public bibliographic authors of cited external standards are fine; this guards the
PROJECT's own people. Stdlib only.

    python3 docs/publishing/check_identities.py
Exit 0 = clean; exit 1 = a protected identity is published without approval.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "publishing" / "identities.yaml"
LOCAL = ROOT / "publishing" / "identities.local.yaml"
DOCS = ROOT / "docs"


def load_list(key: str, text: str) -> list[str]:
    out, grab = [], False
    for line in text.splitlines():
        if re.match(rf"^{key}:\s*\[\s*\]\s*$", line):
            return []
        if re.match(rf"^{key}:\s*$", line):
            grab = True
            continue
        if grab:
            m = re.match(r'^\s+-\s+"?(.+?)"?\s*$', line)
            if m:
                out.append(m.group(1))
            elif line and not line[0].isspace():
                break
    return out


def main() -> int:
    if not CFG.exists():
        print(f"check_identities: missing {CFG}", file=sys.stderr)
        return 2
    text = CFG.read_text()
    protected = load_list("protected", text)
    approved = {a.lower() for a in load_list("approved", text)}
    if LOCAL.exists():   # untracked, gitignored: real names for local checking
        ltext = LOCAL.read_text()
        protected += load_list("protected", ltext)
        approved |= {a.lower() for a in load_list("approved", ltext)}
    terms = [p for p in dict.fromkeys(protected) if p.lower() not in approved]
    pats = [(p, re.compile(re.escape(p), re.I)) for p in terms]
    violations = []
    for html in sorted(DOCS.rglob("*.html")):
        body = html.read_text(errors="replace")
        for name, pat in pats:
            if pat.search(body):
                violations.append((html.relative_to(ROOT), name))
    if violations:
        print("BLOCKED — protected personal identities in published pages "
              "(approve in publishing/identities.yaml with sponsor sign-off, "
              "or remove from the page):", file=sys.stderr)
        for f, n in violations:
            print(f"  {f}: {n!r}", file=sys.stderr)
        return 1
    n = len(list(DOCS.rglob("*.html")))
    print(f"check_identities: {n} published pages clean "
          f"({len(terms)} protected identities enforced).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
