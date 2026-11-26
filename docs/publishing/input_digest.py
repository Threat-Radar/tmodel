#!/usr/bin/env python3
"""The input digest of a governed TARA version (#183; DL-0027 decision 4, DL-0059).

The digest is the git tree hash of what a version is built from, so an approval is
pinned to those inputs and a change to any of them shows (DL-0027 rule 4):

- **the vector** the record `governs`, its bytes as committed;
- **the version itself**: its entry in the record, without the fields that change
  when it is approved (`APPROVAL_FIELDS`), as canonical JSON. The rest of the record
  (reviews, the comment log, other versions, the evidence chain) is about approving
  the version, not what it shows, so it is left out: adding a review, or a version 2,
  does not change version 1's digest;
- **the template**: the files that turn the inputs into the page (`TEMPLATE`).

The tree is built the way git builds one, so `git write-tree` over the same files
gives the same id. It is written `git-tree:<sha1>` in `approval_digest`.

    python docs/publishing/input_digest.py                       # every version of every record
    python docs/publishing/input_digest.py models/tcu/governance.yaml [--version ID] [--list]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "git-tree:"
VERSION_KINDS = ("threat_models", "governed_views")

# The TARA page's template today: the renderer and the page text it reads (DL-0037).
# The vN/ template (#182) replaces these when it lands.
TEMPLATE = ("docs/publishing/render_tara.py", "docs/publishing/tara.yaml")

# Fields of a version that record its approval, not its content (DL-0027 "minus its
# review block"). Leaving them out is what lets the digest be written into the same
# entry it is computed from.
APPROVAL_FIELDS = frozenset(
    {"approved_by", "approval_status", "approval_digest", "governance_status", "updated"}
)


def blob_id(data: bytes) -> str:
    """The git object id of a file with these bytes (`git hash-object`)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def tree_id(files: Mapping[str, bytes]) -> str:
    """The git object id of a tree holding `files`, keyed by slash-separated path."""
    tree: dict[str, Any] = {}
    for path, data in files.items():
        parts = path.split("/")
        if any(p in ("", ".", "..") for p in parts):
            raise ValueError(f"not a plain relative path: {path!r}")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise ValueError(f"{path!r}: a file is also a directory")
        if parts[-1] in node:
            raise ValueError(f"{path!r} given twice, or is also a directory")
        node[parts[-1]] = data
    return _tree(tree)


def _tree(node: Mapping[str, Any]) -> str:
    entries = []
    for name, value in node.items():
        if isinstance(value, dict):
            entries.append(
                (name + "/", b"40000 " + name.encode() + b"\0" + bytes.fromhex(_tree(value)))
            )
        else:
            entries.append(
                (name, b"100644 " + name.encode() + b"\0" + bytes.fromhex(blob_id(value)))
            )
    body = b"".join(entry for _, entry in sorted(entries, key=lambda e: e[0].encode()))
    return hashlib.sha1(b"tree %d\0" % len(body) + body).hexdigest()


def versions(doc: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Every governed version in a record, ThreatModels first."""
    return [
        v
        for kind in VERSION_KINDS
        for v in doc.get(kind) or []
        if isinstance(v, Mapping) and isinstance(v.get("id"), str)
    ]


def canonical(value: Any) -> bytes:
    """JSON with sorted keys and no spacing: the same bytes for the same data."""
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return (text + "\n").encode("utf-8")


def inputs(
    record: Path, doc: Mapping[str, Any], version_id: str, root: Path = ROOT
) -> dict[str, bytes]:
    """The files the digest of `version_id` covers, keyed by their path in the tree."""
    version = next((v for v in versions(doc) if v["id"] == version_id), None)
    if version is None:
        raise KeyError(f"{version_id}: not a version in {record.name}")
    governs = doc.get("governs")
    if not isinstance(governs, str):
        raise ValueError(f"{record.name}: names no `governs` model")
    files = {governs: (root / governs).read_bytes()}
    content = {k: v for k, v in version.items() if k not in APPROVAL_FIELDS}
    rel = record.resolve().relative_to(root.resolve()).with_suffix("")
    files[f"{rel.as_posix()}/{version_id.replace(':', '-')}.json"] = canonical(
        {"governs": governs, "version": content}
    )
    for path in TEMPLATE:
        files[path] = (root / path).read_bytes()
    return files


def digest(record: Path, doc: Mapping[str, Any], version_id: str, root: Path = ROOT) -> str:
    """`git-tree:<sha1>` of the inputs of `version_id`."""
    return PREFIX + tree_id(inputs(record, doc, version_id, root))


def load(record: Path) -> Mapping[str, Any]:
    doc = yaml.safe_load(record.read_text(encoding="utf-8"))
    if not isinstance(doc, Mapping):
        raise ValueError(f"{record}: not a mapping at the top level")
    return doc


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("records", nargs="*", type=Path, help="default: models/*/governance.yaml")
    parser.add_argument("--version", help="one version id (default: every version)")
    parser.add_argument("--list", action="store_true", help="also list each input and its blob id")
    args = parser.parse_args(argv)
    records = args.records or sorted((ROOT / "models").glob("*/governance.yaml"))
    for record in records:
        doc = load(record)
        for v in versions(doc):
            if args.version and v["id"] != args.version:
                continue
            files = inputs(record, doc, v["id"])
            print(f"{v['id']}  {PREFIX}{tree_id(files)}")
            if args.list:
                for path in sorted(files):
                    print(f"    {blob_id(files[path])}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
