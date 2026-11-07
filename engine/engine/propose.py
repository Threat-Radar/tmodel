"""`tmodel propose`: write an agent's change to an SDL model as proposals only (DL-0044).

An AI agent (Claude Code, Grok Bot, any script) or a person hands the engine a *patch*:
new objects for an SDL model and Assertions about them. The engine checks the patch
and appends it to a proposals file beside the model. It never edits the model, never
writes a Review and never sets anything to accepted. A human decides each proposal
by moving it into the model in a pull request and adding a Review (PROC-0002).

Patch format (YAML or JSON):

    schema: tmodel.patch/v0
    target: sdl-01-tmodel-desktop.yaml        # an sdl-*.yaml model
    proposed_by: party:drafting-agent         # a Party in the model or in `add.parties`
    generated_by: "claude-code 2.x, run 1234" # tool and run, as on an Assertion
    rationale: Why this change.
    add:                                      # new objects, by collection
      sdl_practices: [...]
      evidence_items: [...]
    assertions:                               # claims and selections; always `proposed`
      - {id: assertion:x, predicate: selects_practice, subject: ..., object: ...}

The proposals file is spec/vectors/proposals/<model stem>.proposals.yaml. GET /sdl lists
its entries as pending proposals, so the app shows them with the review-status UI.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from engine import sdl

PATCH_SCHEMA = "tmodel.patch/v0"
PROPOSALS_SCHEMA = "tmodel.proposals/v0"
# Collections a patch may add to. Reviews are never among them.
ADDABLE = (
    "sdl_practices",
    "evidence_items",
    "requirement_sources",
    "requirements",
    "milestones",
    "gates",
    "parties",
)
# Keys that record a decision; a proposal may not carry them.
DECISION_KEYS = frozenset(
    {"review_status", "reviews", "reviewer", "approved_by", "decided_by", "approval_status"}
)
PATCH_KEYS = frozenset(
    {"schema", "target", "proposed_by", "generated_by", "rationale", "add", "assertions"}
)


class ProposalError(ValueError):
    """The patch is not a valid proposal; nothing was written."""


def proposals_path(model: Path) -> Path:
    return model.parent / "proposals" / f"{model.stem}.proposals.yaml"


def load_proposals(model: Path) -> list[dict[str, Any]]:
    path = proposals_path(model)
    if not path.is_file():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if doc.get("schema") != PROPOSALS_SCHEMA or not isinstance(doc.get("proposals"), list):
        raise ProposalError(f"{path.name}: not a {PROPOSALS_SCHEMA} file")
    return doc["proposals"]


def merged(doc: Mapping[str, Any], proposals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """The model with every pending proposal folded in (still all `proposed`)."""
    out = copy.deepcopy(dict(doc))
    for p in proposals:
        for coll, items in (p.get("objects") or {}).items():
            out.setdefault(coll, [])
            out[coll] = list(out[coll] or []) + copy.deepcopy(list(items))
        out["assertions"] = list(out.get("assertions") or []) + copy.deepcopy(
            list(p.get("assertions") or [])
        )
    return out


def _fail(problems: list[str]) -> None:
    if problems:
        raise ProposalError("proposal refused:\n  " + "\n  ".join(problems))


def check_patch(patch: Any) -> None:
    """Shape and decision rules that need no model."""
    if not isinstance(patch, dict):
        raise ProposalError("a patch is a mapping")
    problems = []
    if patch.get("schema") != PATCH_SCHEMA:
        problems.append(f"schema must be {PATCH_SCHEMA!r}")
    for key in sorted(set(patch) - PATCH_KEYS):
        problems.append(f"unknown key {key!r} (reviews and decisions cannot be proposed)")
    for key in ("target", "proposed_by", "generated_by", "rationale"):
        if not isinstance(patch.get(key), str) or not patch[key].strip():
            problems.append(f"{key} is required")
    add = patch.get("add") or {}
    if not isinstance(add, dict):
        problems.append("add must map collection names to lists")
        add = {}
    for coll, items in add.items():
        if coll not in ADDABLE:
            problems.append(
                f"add.{coll}: not a collection a proposal may add to ({', '.join(ADDABLE)})"
            )
            continue
        if not isinstance(items, list) or not all(isinstance(i, dict) and "id" in i for i in items):
            problems.append(f"add.{coll}: a list of objects, each with an id")
            continue
        for item in items:
            for key in sorted(DECISION_KEYS & item.keys()):
                problems.append(f"{item['id']}: {key!r} records a decision; only a human sets it")
    for party in add.get("parties") or []:
        if party.get("party_kind") not in ("software_agent", "person"):
            problems.append(f"{party.get('id')}: a proposing party is a software_agent or person")
    assertions = patch.get("assertions") or []
    if not isinstance(assertions, list):
        problems.append("assertions must be a list")
        assertions = []
    if not add and not assertions:
        problems.append("the patch proposes nothing")
    for a in assertions:
        if not isinstance(a, dict) or not all(
            a.get(k) for k in ("id", "predicate", "subject", "object")
        ):
            problems.append("each assertion needs id, predicate, subject and object")
            continue
        status = a.get("assertion_status", "proposed")
        if status != "proposed":
            problems.append(
                f"{a['id']}: assertion_status {status!r}; a proposal is always 'proposed'"
            )
        for key in sorted(DECISION_KEYS & a.keys()):
            problems.append(f"{a['id']}: {key!r} records a decision; only a human sets it")
    _fail(problems)


def propose(
    patch: Mapping[str, Any],
    model: Path,
    xwalk: Mapping[str, Any],
    *,
    now: datetime | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Check `patch` against `model` and append it to the model's proposals file.

    Raises ProposalError (nothing written) when the patch breaks a rule, reuses an
    id, or would leave the model with a dangling reference or a broken review rule.
    Returns the proposal record as written.
    """
    check_patch(patch)
    doc = yaml.safe_load(model.read_text(encoding="utf-8")) or {}
    pending = load_proposals(model)
    current = merged(doc, pending)
    known = {
        o["id"]
        for items in current.values()
        if isinstance(items, list)
        for o in items
        if isinstance(o, dict) and "id" in o
    }
    add = {k: list(v) for k, v in (patch.get("add") or {}).items()}
    new_ids = [o["id"] for items in add.values() for o in items]
    new_ids += [a["id"] for a in patch.get("assertions") or []]
    problems = [f"{i}: id already exists" for i in new_ids if i in known]
    problems += [
        f"{i}: id given twice" for i in sorted({i for i in new_ids if new_ids.count(i) > 1})
    ]
    proposer = patch["proposed_by"]
    if proposer not in known and proposer not in {p["id"] for p in add.get("parties", [])}:
        problems.append(f"proposed_by {proposer}: not a Party in the model or the patch")
    _fail(problems)

    stamp = (now or datetime.now(UTC)).replace(microsecond=0)
    at = stamp.isoformat().replace("+00:00", "Z")
    assertions = []
    for a in patch.get("assertions") or []:
        assertions.append(
            dict(
                a,
                assertion_status="proposed",
                asserted_by=proposer,
                asserted_at=at,
                generated_by=patch["generated_by"],
            )
        )
    body = {"objects": add, "assertions": assertions}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:10]
    record = {
        "id": f"proposal:{stamp.strftime('%Y%m%dT%H%M%SZ')}-{digest}",
        "status": "proposed",
        "proposed_by": proposer,
        "proposed_at": at,
        "generated_by": patch["generated_by"],
        "rationale": patch["rationale"],
        **body,
    }
    # The model with this proposal folded in must still pass the SDL checks.
    try:
        sdl.collect(merged(doc, [*pending, record]), dict(xwalk))
    except (sdl.SdlError, KeyError, TypeError) as exc:
        raise ProposalError(f"proposal refused: the model would not hold together: {exc}") from exc
    if write:
        path = proposals_path(model)
        path.parent.mkdir(parents=True, exist_ok=True)
        out = {
            "schema": PROPOSALS_SCHEMA,
            "target": model.name,
            "note": "Pending proposals (DL-0044). Nothing here is accepted; "
            "a human decides each one in a PR (PROC-0002).",
            "proposals": [*pending, record],
        }
        path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return record


def summary(proposals: list[Mapping[str, Any]], doc: Mapping[str, Any]) -> list[dict[str, Any]]:
    """What GET /sdl shows of the pending proposals: who, when, what, and its state."""
    parties = {p["id"]: p for p in doc.get("parties") or []}
    out = []
    for p in proposals:
        by = parties.get(p.get("proposed_by"), {})
        for extra in (p.get("objects") or {}).get("parties", []):
            if extra.get("id") == p.get("proposed_by"):
                by = extra
        out.append(
            {
                "id": p.get("id"),
                "state": "proposed",
                "by": "AI agent" if by.get("party_kind") == "software_agent" else "person",
                "at": p.get("proposed_at"),
                "generated_by": p.get("generated_by"),
                "rationale": p.get("rationale"),
                "objects": [
                    {"collection": c, "id": o.get("id"), "name": o.get("name", "")}
                    for c, items in (p.get("objects") or {}).items()
                    for o in items
                ],
                "assertions": [
                    {
                        "id": a.get("id"),
                        "predicate": a.get("predicate"),
                        "object": a.get("object"),
                        "name": a.get("name", ""),
                    }
                    for a in p.get("assertions") or []
                ],
            }
        )
    return out
