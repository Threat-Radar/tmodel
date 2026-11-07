"""`tmodel accept`: the sponsor decides one pending proposal (DL-0046).

This is the only code that changes a model on a proposal's behalf, and a human runs
it. It is a CLI command, never an API route: the desktop app and the local API stay
read-only. It refuses to run on `main`, so the decision lands as a pull request.

- `--verdict accepted` applies the proposal to the model file: its additions, edits
  and removals, and its Assertions with `assertion_status: accepted`, each with a
  Review by the deciding sponsor. The rest of the file, comments included, is kept:
  only the touched blocks are rewritten.
- `--verdict rejected` or `changes_requested` leaves the model alone.

Either way the proposal leaves the proposals file and goes to the model's decision
log, spec/vectors/proposals/<model stem>.decided.yaml, with who decided, when and why.
"""

from __future__ import annotations

import copy
import re
import subprocess
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from engine import propose as P

VERDICTS = ("accepted", "rejected", "changes_requested")
SPONSOR_ROLE = "role:sponsor"
DECIDED_SCHEMA = "tmodel.decisions/v0"
PROTECTED_BRANCHES = ("main", "master")


class AcceptError(ValueError):
    """The decision was refused; nothing was written."""


def decided_path(model: Path) -> Path:
    return model.parent / "proposals" / f"{model.stem}.decided.yaml"


def current_branch(where: Path) -> str | None:
    """The git branch checked out at `where`, or None outside a git work tree."""
    try:
        out = subprocess.run(
            ["git", "-C", str(where), "symbolic-ref", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def _is_sponsor(party: Mapping[str, Any]) -> bool:
    return party.get("party_kind") == "person" and SPONSOR_ROLE in (
        party.get("classifications") or []
    )


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---- Text edits that keep the rest of the YAML file as it is ----

_TOP = re.compile(r"^[^\s#-]")


def _dump_item(item: Mapping[str, Any]) -> list[str]:
    text = yaml.safe_dump([dict(item)], sort_keys=False, allow_unicode=True, width=88)
    return ["  " + line if line else line for line in text.splitlines()]


def _block(lines: list[str], key: str) -> tuple[int, int] | None:
    """(header line, end) of a top-level `key:` block; end is exclusive.

    A comment at column 0 belongs to the block when the block goes on after it.
    """
    for i, line in enumerate(lines):
        if not re.match(rf"^{re.escape(key)}:(\s|$)", line):
            continue
        end = i + 1
        while end < len(lines):
            current = lines[end]
            if current.strip() and not current.startswith("#") and _TOP.match(current):
                break
            if current.startswith("#") or not current.strip():
                ahead = end
                while ahead < len(lines) and (
                    not lines[ahead].strip() or lines[ahead].startswith("#")
                ):
                    ahead += 1
                if ahead == len(lines) or _TOP.match(lines[ahead]):
                    break
                end = ahead
                continue
            end += 1
        return i, end
    return None


def _item(lines: list[str], key: str, object_id: str) -> tuple[int, int]:
    found = _block(lines, key)
    if found is None:
        raise AcceptError(f"{key}: not in the model file")
    head, end = found
    pattern = re.compile(rf"^  - id:\s*['\"]?{re.escape(object_id)}['\"]?\s*(#.*)?$")
    for i in range(head + 1, end):
        if pattern.match(lines[i]):
            j = i + 1
            while j < end and not lines[j].startswith("  - "):
                j += 1
            while j > i + 1 and (not lines[j - 1].strip() or re.match(r"^\s{0,2}#", lines[j - 1])):
                j -= 1
            return i, j
    raise AcceptError(f"{object_id}: cannot find its `  - id:` line under {key}")


def _append(lines: list[str], key: str, items: list[Mapping[str, Any]]) -> list[str]:
    body = [line for item in items for line in _dump_item(item)]
    found = _block(lines, key)
    if found is None:
        while lines and not lines[-1].strip():
            lines = lines[:-1]
        return [*lines, "", f"{key}:", *body]
    head, end = found
    if re.match(rf"^{re.escape(key)}:\s*\[\]\s*$", lines[head]):
        lines = [*lines[:head], f"{key}:", *lines[head + 1 :]]
    return [*lines[:end], *body, *lines[end:]]


def _bare(doc: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if v not in (None, [])}


def apply_text(text: str, record: Mapping[str, Any], extra: Mapping[str, list]) -> str:
    """The model text with `record` applied (accepted) and `extra` objects appended."""
    lines = text.splitlines()
    doc = yaml.safe_load(text) or {}
    for e in record.get("edits") or []:
        i = P._find(doc, e["collection"], e["id"])
        if i is None:
            raise AcceptError(f"edit {e['id']}: no longer in {e['collection']}")
        obj = dict(doc[e["collection"]][i])
        obj.update(copy.deepcopy(e.get("set") or {}))
        for key in e.get("unset") or []:
            obj.pop(key, None)
        a, b = _item(lines, e["collection"], e["id"])
        lines = [*lines[:a], *_dump_item(obj), *lines[b:]]
    for r in record.get("removals") or []:
        a, b = _item(lines, r["collection"], r["id"])
        lines = [*lines[:a], *lines[b:]]
        head, end = _block(lines, r["collection"]) or (0, 0)
        if not any(line.startswith("  - ") for line in lines[head + 1 : end]):
            lines = [*lines[:head], *lines[end:]]  # the last one: drop the empty key
    additions: dict[str, list] = {}
    for coll, items in (record.get("objects") or {}).items():
        additions.setdefault(coll, []).extend(items)
    for coll, items in extra.items():
        additions.setdefault(coll, []).extend(items)
    for coll, items in additions.items():
        if items:
            lines = _append(lines, coll, items)
    return "\n".join(lines) + "\n"


def decide(
    model: Path,
    proposal_id: str,
    *,
    verdict: str,
    reviewer: str,
    justification: str,
    xwalk: Mapping[str, Any],
    today: date | None = None,
    declare_sponsor: str | None = None,
    check_branch: bool = True,
) -> dict[str, Any]:
    """Record the sponsor's decision on one pending proposal. Raises AcceptError."""
    if verdict not in VERDICTS:
        raise AcceptError(f"verdict must be one of {', '.join(VERDICTS)}")
    if not justification.strip():
        raise AcceptError("a decision needs a justification")
    if check_branch:
        branch = current_branch(model.parent)
        if branch in PROTECTED_BRANCHES:
            raise AcceptError(
                f"on branch {branch}: decide in a branch and open a pull request (PROC-0002)"
            )
    text = model.read_text(encoding="utf-8")
    doc = yaml.safe_load(text) or {}
    pending = P.load_proposals(model)
    record = next((p for p in pending if p.get("id") == proposal_id), None)
    if record is None:
        raise AcceptError(f"{proposal_id}: not a pending proposal for {model.name}")

    parties = {p["id"]: p for p in doc.get("parties") or [] if isinstance(p, dict)}
    new_parties = []
    if reviewer not in parties and declare_sponsor:
        if not re.fullmatch(r"[A-Za-z0-9-]+", declare_sponsor):
            raise AcceptError("--declare-sponsor takes a GitHub handle")
        new_parties.append(
            {
                "id": reviewer,
                "name": f"@{declare_sponsor}",
                "description": "Project sponsor, added when deciding a proposal (DL-0046).",
                "party_kind": "person",
                "classifications": [SPONSOR_ROLE],
            }
        )
        parties[reviewer] = new_parties[0]
    who = parties.get(reviewer)
    if who is None:
        raise AcceptError(
            f"{reviewer}: not a Party in {model.name}; add the sponsor with --declare-sponsor"
        )
    if not _is_sponsor(who):
        raise AcceptError(
            f"{reviewer}: only the sponsor decides (a person Party with {SPONSOR_ROLE})"
        )

    on = (today or date.today()).isoformat()
    extra: dict[str, list] = {"parties": new_parties} if new_parties else {}
    reviews = []
    if verdict == "accepted":
        assertions = []
        for a in record.get("assertions") or []:
            assertions.append(dict(a, assertion_status="accepted"))
            reviews.append(
                {
                    "id": f"review:{_slug(a['id'].split(':', 1)[-1])}-{on}",
                    "name": f"Review: {a.get('name') or a['id']}",
                    "reviews": a["id"],
                    "reviewer": reviewer,
                    "review_status": "accepted",
                    "justification": justification,
                }
            )
        accepted = dict(record, assertions=[])
        extra = {**extra}
        if assertions:
            extra["assertions"] = assertions
        if reviews:
            extra["reviews"] = reviews
        new_text = apply_text(text, accepted, extra)
        expected = P.apply_record(copy.deepcopy(dict(doc)), accepted)
        for coll, items in extra.items():
            expected[coll] = list(expected.get(coll) or []) + copy.deepcopy(items)
        if _bare(yaml.safe_load(new_text)) != _bare(expected):
            raise AcceptError("could not apply the proposal to the file text; apply it by hand")
        P.validate(expected, P.model_kind(model), xwalk)
    else:
        new_text = apply_text(text, {}, extra) if extra else text

    log_path = decided_path(model)
    log = (
        yaml.safe_load(log_path.read_text(encoding="utf-8"))
        if log_path.is_file()
        else {"schema": DECIDED_SCHEMA, "target": model.name, "decisions": []}
    )
    entry = {
        "proposal": proposal_id,
        "verdict": verdict,
        "decided_by": reviewer,
        "decided_on": on,
        "justification": justification,
        "proposed_by": record.get("proposed_by"),
        "generated_by": record.get("generated_by"),
        "rationale": record.get("rationale"),
        "reviews": [r["id"] for r in reviews],
    }
    if verdict != "accepted":
        entry["proposal_record"] = record
    log["decisions"] = [*(log.get("decisions") or []), entry]

    if new_text != text:
        model.write_text(new_text, encoding="utf-8")
    P.write_proposals(model, [p for p in pending if p.get("id") != proposal_id])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(yaml.safe_dump(log, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"model_changed": new_text != text, **entry}
