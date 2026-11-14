#!/usr/bin/env python3
"""Fail if a governed record (models/<item>/governance.yaml) is malformed (#180, DL-0054).

Two passes:

1. **Schema.** The record must validate against ExampleModelGovernance in
   spec/vectors/example-container-governance.linkml.yaml, which catches a missing
   required field or a value outside an enum. Needs LinkML (spec/schema/requirements.txt).
2. **Rules the schema cannot state** (DL-0027, DL-0054):
   - ids are unique, and every reference resolves, to an object of the right kind,
     in the record or in the model file it `governs`;
   - a review of a governed version (ThreatModel, GovernedView) has an outcome;
   - a reviewer is a person or a software agent. An agent's review names its model
     and run and fills no role (DL-0027 rule 1); a person's review of a version
     fills a role and names no model;
   - a resolved comment names the commit or PR that resolved it, and only then;
   - each version has a whole-number revision and required roles, supersedes an
     earlier revision, and, once approved, has an approval digest and is approved
     only by people's `approved` reviews of that version.

The publish gate (a required role unfilled, an open comment, YAML and PR approvals
disagreeing) and the input digest are #183, not this check.

    python docs/publishing/check_governance.py                     # every models/*/governance.yaml
    python docs/publishing/check_governance.py models/tcu/governance.yaml
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "spec" / "vectors" / "example-container-governance.linkml.yaml"
TARGET = "ExampleModelGovernance"
VERSION_KINDS = ("threat_models", "governed_views")
PERSON, AGENT = "person", "software_agent"


def check_schema(doc: Mapping[str, Any], schema: Path = SCHEMA) -> list[str]:
    """LinkML errors for the record, as `path: message` strings."""
    try:
        from linkml.validator import validate
    except ImportError as exc:
        raise SystemExit(
            "check_governance: LinkML is not installed; pip install -r spec/schema/requirements.txt"
        ) from exc
    report = validate(dict(doc), str(schema), TARGET)
    return [r.message for r in report.results if r.severity.name == "ERROR"]


def _ids(doc: Mapping[str, Any]) -> dict[str, str]:
    """Every object id in a container document, mapped to its collection name."""
    found: dict[str, str] = {}
    for collection, items in doc.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                    found.setdefault(item["id"], collection)
    return found


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


def _items(doc: Mapping[str, Any], collection: str) -> Iterable[Mapping[str, Any]]:
    return (i for i in doc.get(collection) or [] if isinstance(i, Mapping))


def check_rules(doc: Mapping[str, Any], model: Mapping[str, Any] | None = None) -> list[str]:
    """Rule errors for a record; `model` is the parsed file the record `governs`."""
    errors: list[str] = []
    local = _ids(doc)
    external = _ids(model or {})

    seen: set[str] = set()
    for items in doc.values():
        for item in items if isinstance(items, list) else []:
            oid = item.get("id") if isinstance(item, Mapping) else None
            if not isinstance(oid, str):
                continue
            if oid in seen:
                errors.append(f"{oid}: id used twice")
            seen.add(oid)

    def ref(
        owner: str, slot: str, value: Any, kinds: tuple[str, ...], *, model_too: bool = False
    ) -> None:
        for target in _list(value):
            kind = local.get(target) or (external.get(target) if model_too else None)
            if kind is None:
                where = "the record or the model it governs" if model_too else "the record"
                errors.append(f"{owner}: {slot} {target!r} is not in {where}")
            elif kinds and kind not in kinds:
                errors.append(
                    f"{owner}: {slot} {target!r} is a {kind} item, not one of {', '.join(kinds)}"
                )

    parties = {p["id"]: p for p in _items(doc, "parties") if "id" in p}
    reviews = {r["id"]: r for r in _items(doc, "reviews") if "id" in r}

    for collection in VERSION_KINDS:
        for v in _items(doc, collection):
            vid = v.get("id", "?")
            ref(vid, "owner", v.get("owner"), ("parties",))
            ref(vid, "supersedes", v.get("supersedes"), (collection,))
            ref(vid, "approved_by", v.get("approved_by"), ("reviews",))
            ref(
                vid,
                "members" if collection == "threat_models" else "renders",
                v.get("members", v.get("renders")),
                (),
                model_too=True,
            )
            revision = str(v.get("revision", ""))
            if not revision.isdigit():
                errors.append(f"{vid}: revision {revision!r} is not a whole number")
            if collection == "threat_models" and not v.get("required_review_roles"):
                errors.append(f"{vid}: names no required_review_roles")
            prior = next(
                (p for p in _items(doc, collection) if p.get("id") == v.get("supersedes")), None
            )
            if prior and revision.isdigit() and str(prior.get("revision", "")).isdigit():
                if int(prior["revision"]) >= int(revision):
                    errors.append(
                        f"{vid}: supersedes revision {prior['revision']}, which is not earlier"
                    )
            if v.get("governance_status") == "approved" and not v.get("approval_digest"):
                errors.append(f"{vid}: approved but has no approval_digest")
            for rid in _list(v.get("approved_by")):
                r = reviews.get(rid)
                if r is None:
                    continue
                if r.get("reviews") != vid or r.get("review_outcome") != "approved":
                    errors.append(
                        f"{vid}: approved_by {rid} is not an `approved` review of this version"
                    )
                if parties.get(r.get("reviewer"), {}).get("party_kind") != PERSON:
                    errors.append(
                        f"{vid}: approved_by {rid} is not a person's review (DL-0027 rule 1)"
                    )

    versions = {v["id"] for c in VERSION_KINDS for v in _items(doc, c) if "id" in v}
    for rid, r in reviews.items():
        target = r.get("reviews")
        ref(rid, "reviews", target, VERSION_KINDS + ("assertions",), model_too=True)
        ref(rid, "reviewer", r.get("reviewer"), ("parties",))
        kind = parties.get(r.get("reviewer"), {}).get("party_kind")
        of_version = target in versions
        if of_version and not r.get("review_outcome"):
            errors.append(f"{rid}: a review of a governed version needs review_outcome")
        if kind == AGENT:
            for slot in ("agent_model", "agent_run_id"):
                if not r.get(slot):
                    errors.append(f"{rid}: an AI agent's review needs {slot}")
            if r.get("reviewer_role"):
                errors.append(f"{rid}: an AI agent's review fills no role (DL-0027 rule 1)")
        elif kind == PERSON:
            if r.get("agent_model") or r.get("agent_run_id"):
                errors.append(f"{rid}: a person's review names no agent model or run")
            if of_version and not r.get("reviewer_role"):
                errors.append(f"{rid}: a person's review of a governed version needs reviewer_role")
        elif kind is not None:
            errors.append(
                f"{rid}: reviewer's party_kind is {kind}; "
                "a review is by a person or a software agent"
            )

    for c in _items(doc, "review_comments"):
        cid = c.get("id", "?")
        ref(cid, "comment_on", c.get("comment_on"), ("reviews",) + VERSION_KINDS)
        resolved = c.get("comment_status") == "resolved"
        if resolved and not c.get("resolved_by"):
            errors.append(f"{cid}: resolved, but names no resolved_by")
        if c.get("resolved_by") and not resolved:
            errors.append(f"{cid}: has resolved_by but is {c.get('comment_status')}")

    for r in _items(doc, "requirements"):
        rid = r.get("id", "?")
        for slot in ("applies_to", "refines", "derived_from", "addresses", "satisfied_by"):
            ref(rid, slot, r.get(slot), (), model_too=True)
    for p in _items(doc, "sdl_practices"):
        pid = p.get("id", "?")
        ref(pid, "owner", p.get("owner"), ("parties",))
        ref(pid, "implements", p.get("implements"), ("requirements",), model_too=True)
        ref(pid, "produces", p.get("produces"), ("evidence_items",))
    for e in _items(doc, "evidence_items"):
        ref(e.get("id", "?"), "evidence_of", e.get("evidence_of"), VERSION_KINDS)
    return errors


def check_file(path: Path, root: Path = ROOT, schema: Path = SCHEMA) -> list[str]:
    """Every error in one governed record, schema first, then rules."""
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"cannot read: {exc}"]
    if not isinstance(doc, Mapping):
        return ["not a mapping at the top level"]
    errors = check_schema(doc, schema)
    model: Mapping[str, Any] | None = None
    governs = doc.get("governs")
    if isinstance(governs, str):
        model_path = (root / governs).resolve()
        if not model_path.is_relative_to(root.resolve()) or not model_path.is_file():
            errors.append(f"governs {governs!r}: no such file in the repo")
        else:
            model = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    return errors + check_rules(doc, model)


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or sorted((ROOT / "models").glob("*/governance.yaml"))
    if not files:
        print("check_governance: no governed records found under models/")
        return 0
    failed = 0
    for path in files:
        errors = check_file(path.resolve())
        name = path.resolve().relative_to(ROOT) if path.resolve().is_relative_to(ROOT) else path
        if errors:
            failed += 1
            print(f"{name}: {len(errors)} error(s)", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
        else:
            print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
