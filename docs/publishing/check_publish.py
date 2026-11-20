#!/usr/bin/env python3
"""Block publishing a governed TARA version that is not properly approved (#183, DL-0059).

The publish gate of DL-0027 (rules 1 to 4, decision 1), for each version a record
publishes: one the record marks `governance_status: approved`, or one that has pages
under `docs/models/<item>/tara/v<N>/`. It fails when, for such a version:

- **a required review is missing**: a role in `required_review_roles` has no
  person's review of the version, or that role's latest review is not `approved`;
- **only an AI review approves**: an AI agent approves and no person does
  (DL-0027 rule 1);
- **a comment is open**, on the version or on a review of it (rule 3);
- **the record and the PR disagree**: the version has pages but the record does not
  approve it, or the record approves it and no code owner of the record approves the
  PR at its head, or one requests changes (decision 1);
- **its inputs changed since approval**: `approval_digest` is not the digest
  `input_digest.py` computes (rule 4).

The last two apply to what the PR publishes: a version it newly approves (compared
with `--base`) or whose pages it changes. A version approved earlier whose digest no
longer matches is reported as stale, for the page's stale banner, and does not fail.
Drafts with no pages are not published, so nothing is gated for them; their record is
still checked by check_governance.py.

    python docs/publishing/check_publish.py [RECORD ...] [--base REF]
        [--pr-reviews FILE --head SHA [--author LOGIN]] [--changed FILE]

`--pr-reviews` is the PR's reviews from the GitHub API, as a JSON array or one JSON
object per line; CI passes them (.github/workflows/tara.yml). Without it the PR side
is not checked, and the report says so.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from input_digest import ROOT, digest, versions

PERSON, AGENT = "person", "software_agent"
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# --- the PR side ---------------------------------------------------------------------------------


def read_reviews(path: Path) -> list[Mapping[str, Any]]:
    """GitHub review objects from a JSON array, or from one JSON object per line."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return list(json.loads(text))
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def pr_verdicts(
    reviews: Iterable[Mapping[str, Any]], head: str | None, author: str | None = None
) -> dict[str, str]:
    """Each human reviewer's standing verdict on the PR, as GitHub counts it.

    A comment does not replace an earlier approval or request for changes; a dismissal
    does. An approval counts only on the head commit, so one given before a later push
    is not an approval of what is published. Bots and the PR's author are left out.
    """
    standing: dict[str, str] = {}
    for r in sorted(reviews, key=lambda r: r.get("submitted_at") or ""):
        user = r.get("user") or {}
        login, state = user.get("login"), r.get("state")
        if not login or user.get("type") == "Bot" or login == author:
            continue
        if state == "APPROVED" and head and r.get("commit_id") != head:
            state = "STALE"
        if state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED", "STALE"):
            standing[login] = state
    return standing


def code_owners(path: str, codeowners: Path = CODEOWNERS) -> list[str]:
    """The owners of `path` in a CODEOWNERS file: the last matching line wins."""
    owners: list[str] = []
    if not codeowners.is_file():
        return owners
    for line in codeowners.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        pattern, *names = line.split()
        if _owns(pattern, path):
            owners = [n.lstrip("@") for n in names]
    return owners


def _owns(pattern: str, path: str) -> bool:
    """Whether a CODEOWNERS pattern covers `path`, as gitignore patterns do.

    A pattern with a slash before its end is anchored at the root; one without matches
    at any depth. `*` and `?` stay within one path segment, `**` crosses them, and a
    pattern that names a directory covers everything under it.
    """
    anchored = "/" in pattern.rstrip("/")
    body, i = "", 0
    p = pattern.strip("/")
    while i < len(p):
        if p.startswith("**", i):
            body, i = body + ".*", i + 2
        else:
            body, i = body + {"*": "[^/]*", "?": "[^/]"}.get(p[i], re.escape(p[i])), i + 1
    return re.fullmatch(("" if anchored else "(?:.*/)?") + body + "(?:/.*)?", path) is not None


# --- the record side -----------------------------------------------------------------------------


def _base_doc(record: Path, base: str | None) -> Mapping[str, Any] | None:
    """The record as it is on `base`, or None when it is new there (or no base is given)."""
    if not base:
        return None
    rel = record.resolve().relative_to(ROOT).as_posix()
    shown = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{base}:{rel}"], capture_output=True, text=True
    )
    if shown.returncode != 0:
        return {}
    doc = yaml.safe_load(shown.stdout)
    return doc if isinstance(doc, Mapping) else {}


def pages_dir(record: Path, revision: str) -> str:
    """Where version `revision` of the record's item is published (DL-0027)."""
    return f"docs/models/{record.resolve().parent.name}/tara/v{revision}/"


def check_record(
    record: Path,
    doc: Mapping[str, Any],
    *,
    base_doc: Mapping[str, Any] | None = None,
    verdicts: Mapping[str, str] | None = None,
    changed: Iterable[str] = (),
    codeowners: Path = CODEOWNERS,
    root: Path = ROOT,
) -> Result:
    """Gate every version `doc` publishes. `base_doc` None means every one is new here."""
    out = Result()
    rel = record.resolve().relative_to(root.resolve()).as_posix()
    parties = {p.get("id"): p for p in doc.get("parties") or [] if isinstance(p, Mapping)}
    reviews = [r for r in doc.get("reviews") or [] if isinstance(r, Mapping)]
    comments = [c for c in doc.get("review_comments") or [] if isinstance(c, Mapping)]
    changed = list(changed)
    before = (
        None
        if base_doc is None
        else {v["id"]: v.get("governance_status") for v in versions(base_doc)}
    )

    for v in versions(doc):
        vid, revision = v["id"], str(v.get("revision", ""))
        pages = pages_dir(record, revision)
        has_pages = (root / pages).is_dir()
        approved = v.get("governance_status") == "approved"
        if not (approved or has_pages):
            out.notes.append(f"{vid}: {v.get('governance_status', 'no status')}, not published")
            continue
        newly = before is None or before.get(vid) != "approved"
        publishing = newly or any(p.startswith(pages) for p in changed)

        if has_pages and not approved:
            out.errors.append(
                f"{vid}: has pages under {pages}, but the record does not approve it "
                f"(governance_status: {v.get('governance_status')})"
            )

        mine = [r for r in reviews if r.get("reviews") == vid]
        people = [r for r in mine if parties.get(r.get("reviewer"), {}).get("party_kind") == PERSON]
        agents = [r for r in mine if parties.get(r.get("reviewer"), {}).get("party_kind") == AGENT]
        for role in v.get("required_review_roles") or []:
            filled = sorted(
                (r for r in people if r.get("reviewer_role") == role),
                key=lambda r: str(r.get("reviewed_at", "")),
            )
            if not filled:
                out.errors.append(f"{vid}: required review missing: no {role} review by a person")
            elif filled[-1].get("review_outcome") != "approved":
                out.errors.append(
                    f"{vid}: the {role} review ({filled[-1].get('id')}) is "
                    f"{filled[-1].get('review_outcome')}, not approved"
                )
        if any(r.get("review_outcome") == "approved" for r in agents) and not any(
            r.get("review_outcome") == "approved" for r in people
        ):
            out.errors.append(f"{vid}: only an AI review approves it (DL-0027 rule 1)")

        on_version = {vid} | {r.get("id") for r in mine}
        for c in comments:
            if c.get("comment_on") in on_version and c.get("comment_status") == "open":
                out.errors.append(f"{vid}: comment {c.get('id')} is open")

        if approved:
            pinned, current = v.get("approval_digest"), digest(record, doc, vid, root)
            if not pinned:
                out.errors.append(f"{vid}: approved but has no approval_digest")
            elif pinned != current:
                if publishing:
                    out.errors.append(
                        f"{vid}: approval_digest {pinned} is not its inputs' digest {current}: "
                        "the inputs changed after approval (input_digest.py --list shows them)"
                    )
                else:
                    out.notes.append(
                        f"{vid}: STALE, its inputs changed after approval "
                        f"({pinned} approved, {current} now); the page shows the stale banner"
                    )

        if publishing and approved:
            if verdicts is None:
                out.notes.append(f"{vid}: PR approvals not checked (no --pr-reviews)")
                continue
            owners = code_owners(rel, codeowners)
            blocking = sorted(u for u, s in verdicts.items() if s == "CHANGES_REQUESTED")
            if blocking:
                out.errors.append(
                    f"{vid}: the record approves it, but "
                    + ", ".join(f"@{u}" for u in blocking)
                    + " requests changes on the PR"
                )
            if not any(verdicts.get(o) == "APPROVED" for o in owners):
                named = ", ".join(f"@{o}" for o in owners) or "none listed"
                out.errors.append(
                    f"{vid}: the record approves it, but no code owner of {rel} "
                    f"({named}) approves the PR at its head commit"
                )
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("records", nargs="*", type=Path, help="default: models/*/governance.yaml")
    parser.add_argument("--base", help="git ref the PR merges into, e.g. origin/main")
    parser.add_argument("--pr-reviews", type=Path, help="the PR's reviews (GitHub API JSON)")
    parser.add_argument("--head", help="the PR's head commit; approvals of others do not count")
    parser.add_argument("--author", help="the PR's author, whose review does not count")
    parser.add_argument("--changed", type=Path, help="file listing the PR's changed paths")
    args = parser.parse_args(argv)
    if args.pr_reviews and not args.head:
        parser.error("--pr-reviews needs --head")

    records = args.records or sorted((ROOT / "models").glob("*/governance.yaml"))
    verdicts = (
        pr_verdicts(read_reviews(args.pr_reviews), args.head, args.author)
        if args.pr_reviews
        else None
    )
    changed = args.changed.read_text(encoding="utf-8").split() if args.changed else []
    failed = 0
    for record in records:
        record = record.resolve()
        doc = yaml.safe_load(record.read_text(encoding="utf-8"))
        result = check_record(
            record, doc, base_doc=_base_doc(record, args.base), verdicts=verdicts, changed=changed
        )
        name = record.relative_to(ROOT).as_posix()
        print(f"{name}: {'BLOCKED' if result.errors else 'ok'}")
        for line in result.errors:
            print(f"  error: {line}")
        for line in result.notes:
            print(f"  note: {line}")
        failed += bool(result.errors)
    if not records:
        print("check_publish: no governed records under models/")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
