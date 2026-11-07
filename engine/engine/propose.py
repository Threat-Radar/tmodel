"""`tmodel propose`: an agent's change to a model becomes a proposal only (DL-0044, DL-0046).

An AI agent (Claude Code, Grok Bot, any script) or a person hands the engine a *patch*.
A patch can add objects, edit or remove existing ones, and make Assertions. It can
target any example model in spec/vectors: a threat or attack-path model (`mvp-*`,
`tv-*`, `pv-*`), an SDL model (`sdl-*`), or the model's saved KG views (the `views`
collection the Graph tab loads).

The engine checks the patch and appends it to a proposals file beside the model. It
never edits the model, never writes a Review and never sets anything to accepted. The
sponsor decides each proposal with `tmodel accept` (engine/engine/accept.py) in a
branch, and the decision merges as a pull request (PROC-0002).

Patch format (YAML or JSON). `tmodel.patch/v0` (DL-0044) has only `add` and
`assertions`. `tmodel.patch/v1` adds `edit` and `remove`:

    schema: tmodel.patch/v1
    target: mvp-01-software-doc-service.yaml
    proposed_by: party:drafting-agent         # a Party in the model or in `add.parties`
    generated_by: "claude-code 2.x, run 1234" # tool and run, as on an Assertion
    rationale: Why this change.
    add:                                      # new objects, by collection
      mitigations: [...]
      views: [{id: view:x, name: ..., projection: graph, focus_query: "a -> b"}]
    edit:                                     # field changes to existing objects
      - {collection: components, id: component:x, set: {name: ...}, unset: [description]}
    remove:                                   # objects to take out
      - {collection: mitigations, id: mitigation:y}
    assertions:                               # claims and selections; always `proposed`
      - {id: assertion:x, predicate: mitigates, subject: ..., object: ...}

The proposals file is spec/vectors/proposals/<model stem>.proposals.yaml. GET /proposals
and GET /sdl list its entries, so the app shows them with the review-status UI.
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
from engine.graph import AttackGraph, GraphError
from engine.model_graph import COLLECTION_DOMAIN_TYPES, RELATIONSHIP_SLOTS, project_model_graph

PATCH_SCHEMA = "tmodel.patch/v1"
PATCH_SCHEMAS = ("tmodel.patch/v0", PATCH_SCHEMA)
PROPOSALS_SCHEMA = "tmodel.proposals/v0"
MODEL_PREFIXES = ("mvp-", "tv-", "pv-", "sdl-")
SDL_PREFIX = "sdl-"
# Collections a patch may add to, edit or remove from. Reviews are never among them:
# only the sponsor writes a Review (`tmodel accept`). Assertions are made with
# `assertions`, and may be edited or removed as a proposal.
ADDABLE_SDL = (
    "sdl_practices",
    "evidence_items",
    "requirement_sources",
    "requirements",
    "milestones",
    "gates",
    "parties",
    "views",
)
ADDABLE_THREAT = (
    *(c for c in COLLECTION_DOMAIN_TYPES if c not in ("reviews", "assertions")),
    # Accepted via ADR-0011 (DL-0024); not yet in the graph adapter's map.
    "assets",
    "trust_boundaries",
    "data_flows",
)
# The older name, kept for callers of the v0 hook.
ADDABLE = ADDABLE_SDL
# Keys that record a decision; a proposal may not carry or set them.
DECISION_KEYS = frozenset(
    {"review_status", "reviews", "reviewer", "approved_by", "decided_by", "approval_status"}
)
PATCH_KEYS = frozenset(
    {
        "schema",
        "target",
        "proposed_by",
        "generated_by",
        "rationale",
        "add",
        "edit",
        "remove",
        "assertions",
    }
)


NOT_CHANGEABLE = "is not a collection a proposal may change"


class ProposalError(ValueError):
    """The patch is not a valid proposal; nothing was written."""


def model_kind(model: Path | str) -> str:
    """`sdl` for an SDL model, `threat` for a threat or attack-path model."""
    return "sdl" if Path(model).name.startswith(SDL_PREFIX) else "threat"


def addable(kind: str) -> tuple[str, ...]:
    return ADDABLE_SDL if kind == "sdl" else ADDABLE_THREAT


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


def write_proposals(model: Path, proposals: list[Mapping[str, Any]]) -> None:
    path = proposals_path(model)
    if not proposals:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "schema": PROPOSALS_SCHEMA,
        "target": model.name,
        "note": "Pending proposals (DL-0044, DL-0046). Nothing here is accepted; "
        "the sponsor decides each one with `tmodel accept` in a PR (PROC-0002).",
        "proposals": list(proposals),
    }
    path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _find(doc: Mapping[str, Any], collection: str, object_id: str) -> int | None:
    for i, o in enumerate(doc.get(collection) or []):
        if isinstance(o, dict) and o.get("id") == object_id:
            return i
    return None


def apply_record(
    out: dict[str, Any], record: Mapping[str, Any], *, assertion_status: str | None = None
) -> dict[str, Any]:
    """Fold one proposal into `out` (in place): adds, then edits, removals, assertions."""
    for coll, items in (record.get("objects") or {}).items():
        out[coll] = list(out.get(coll) or []) + copy.deepcopy(list(items))
    for e in record.get("edits") or []:
        i = _find(out, e["collection"], e["id"])
        if i is None:
            raise ProposalError(f"edit {e['id']}: not in {e['collection']}")
        obj = dict(out[e["collection"]][i])
        obj.update(copy.deepcopy(e.get("set") or {}))
        for key in e.get("unset") or []:
            obj.pop(key, None)
        out[e["collection"]] = list(out[e["collection"]])
        out[e["collection"]][i] = obj
    for r in record.get("removals") or []:
        i = _find(out, r["collection"], r["id"])
        if i is None:
            raise ProposalError(f"remove {r['id']}: not in {r['collection']}")
        out[r["collection"]] = [o for j, o in enumerate(out[r["collection"]]) if j != i]
    added = copy.deepcopy(list(record.get("assertions") or []))
    if assertion_status:
        for a in added:
            a["assertion_status"] = assertion_status
    if added:
        out["assertions"] = list(out.get("assertions") or []) + added
    return out


def merged(doc: Mapping[str, Any], proposals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """The model with every pending proposal folded in (still all `proposed`)."""
    out = copy.deepcopy(dict(doc))
    for p in proposals:
        apply_record(out, p)
    return out


def _fail(problems: list[str]) -> None:
    if problems:
        raise ProposalError("proposal refused:\n  " + "\n  ".join(problems))


def _check_ref(item: Any, what: str, problems: list[str]) -> bool:
    if not isinstance(item, dict) or not all(
        isinstance(item.get(k), str) and item[k] for k in ("collection", "id")
    ):
        problems.append(f"each {what} needs a collection and an id")
        return False
    if item["collection"] == "reviews":
        problems.append(f"{what} {item['id']}: reviews are written only by the sponsor")
        return False
    return True


def check_patch(patch: Any, kind: str = "sdl") -> None:
    """Shape and decision rules that need no model."""
    if not isinstance(patch, dict):
        raise ProposalError("a patch is a mapping")
    problems = []
    if patch.get("schema") not in PATCH_SCHEMAS:
        problems.append(f"schema must be one of {', '.join(map(repr, PATCH_SCHEMAS))}")
    for key in sorted(set(patch) - PATCH_KEYS):
        problems.append(f"unknown key {key!r} (reviews and decisions cannot be proposed)")
    if patch.get("schema") == "tmodel.patch/v0":
        for key in ("edit", "remove"):
            if key in patch:
                problems.append(f"{key} needs schema {PATCH_SCHEMA!r}")
    for key in ("target", "proposed_by", "generated_by", "rationale"):
        if not isinstance(patch.get(key), str) or not patch[key].strip():
            problems.append(f"{key} is required")
    allowed = addable(kind)
    add = patch.get("add") or {}
    if not isinstance(add, dict):
        problems.append("add must map collection names to lists")
        add = {}
    for coll, items in add.items():
        if coll not in allowed:
            problems.append(
                f"add.{coll}: not a collection a proposal may add to ({', '.join(allowed)})"
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
    for view in add.get("views") or []:
        _check_view(view, problems)
    edits = patch.get("edit") or []
    removes = patch.get("remove") or []
    if not isinstance(edits, list) or not isinstance(removes, list):
        problems.append("edit and remove must be lists")
        edits, removes = [], []
    changeable = (*allowed, "assertions")
    for e in edits:
        if not _check_ref(e, "edit", problems):
            continue
        if e["collection"] not in changeable:
            problems.append(f"edit {e['id']}: {e['collection']} {NOT_CHANGEABLE}")
        sets, unset = e.get("set") or {}, e.get("unset") or []
        if not isinstance(sets, dict) or not isinstance(unset, list) or not (sets or unset):
            problems.append(f"edit {e['id']}: give `set` (a mapping) and/or `unset` (a list)")
            continue
        if "id" in sets or "id" in unset:
            problems.append(f"edit {e['id']}: an id cannot change; remove and add instead")
        for key in sorted((DECISION_KEYS | {"assertion_status"}) & (set(sets) | set(unset))):
            problems.append(f"edit {e['id']}: {key!r} records a decision; only a human sets it")
    for r in removes:
        if _check_ref(r, "remove", problems) and r["collection"] not in changeable:
            problems.append(f"remove {r['id']}: {r['collection']} {NOT_CHANGEABLE}")
    assertions = patch.get("assertions") or []
    if not isinstance(assertions, list):
        problems.append("assertions must be a list")
        assertions = []
    if not add and not assertions and not edits and not removes:
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


def _check_view(view: Mapping[str, Any], problems: list[str]) -> None:
    if view.get("projection", "graph") != "graph":
        problems.append(f"{view.get('id')}: a saved KG view uses projection 'graph'")
    if not isinstance(view.get("focus_query"), str) or not view["focus_query"].strip():
        problems.append(f"{view.get('id')}: a saved KG view needs a focus_query")


def view_members(doc: Mapping[str, Any], focus_query: str) -> list[str]:
    """The object ids a saved View's `focus_query` selects (DL-0046).

    The query is `START_ID -> step -> step ...`, as in the example models. A step is:

    - a collection (`threat_instances`): the objects of that collection nearest (fewest
      links, either direction) to what the view has selected so far;
    - a relationship (`composed_of`, or an Assertion predicate such as `propagates_to`):
      follow it outward from the previous step; `composed_of*` follows it repeatedly.

    Text after `;` is a note for people and is ignored. Raises GraphError.
    """
    query = focus_query.split(";", 1)[0]
    tokens = [t.strip() for t in query.split("->")]
    if not tokens or not tokens[0]:
        raise GraphError("focus_query: expected `START_ID -> step ...`")
    types, links, outward = _link_index(doc)
    if tokens[0] not in types:
        raise GraphError(f"focus_query: {tokens[0]} is not an object in the model")
    relationships = {rel for (_source, rel) in outward}
    members, frontier = [tokens[0]], [tokens[0]]
    for token in tokens[1:]:
        name, repeat = token.rstrip("*"), token.endswith("*")
        if name in types.values() or name in (*ADDABLE_THREAT, *ADDABLE_SDL):
            step = _nearest(members, links, types, name)
        elif name in relationships or name in RELATIONSHIP_SLOTS:
            step, todo = [], list(frontier)
            while todo:
                found = sorted({t for f in todo for t in outward.get((f, name), ())} - set(step))
                step += found
                todo = found if repeat else []
        else:
            raise GraphError(f"focus_query: {token!r} is not a collection or relationship")
        members += [i for i in step if i not in members]
        frontier = step
    return members


def _link_index(
    doc: Mapping[str, Any],
) -> tuple[dict[str, str], dict[str, set[str]], dict[tuple[str, str], set[str]]]:
    """Every object's collection, its links (either direction) and its outward links
    by slot or Assertion predicate. Any field whose values are ids of objects in the
    model is a link, so the same query works on threat and SDL models."""
    types: dict[str, str] = {}
    for coll, items in doc.items():
        if isinstance(items, list) and coll != "views":
            for o in items:
                if isinstance(o, dict) and isinstance(o.get("id"), str):
                    types[o["id"]] = coll
    links: dict[str, set[str]] = {}
    outward: dict[tuple[str, str], set[str]] = {}

    def link(source: str, rel: str, target: str) -> None:
        links.setdefault(source, set()).add(target)
        links.setdefault(target, set()).add(source)
        outward.setdefault((source, rel), set()).add(target)

    for coll, items in doc.items():
        if not isinstance(items, list) or coll in ("views", "assertions"):
            continue
        for o in items:
            if not isinstance(o, dict) or not isinstance(o.get("id"), str):
                continue
            for slot, value in o.items():
                values = value if isinstance(value, list) else [value]
                for v in values:
                    if slot != "id" and isinstance(v, str) and v in types:
                        link(o["id"], slot, v)
    for a in doc.get("assertions") or []:
        if isinstance(a, dict) and a.get("subject") in types and a.get("object") in types:
            link(a["subject"], str(a.get("predicate")), a["object"])
    return types, links, outward


def _nearest(
    start: list[str], links: Mapping[str, set[str]], types: Mapping[str, str], collection: str
) -> list[str]:
    seen, layer = set(start), list(start)
    while layer:
        found = sorted(i for i in layer if types.get(i) == collection and i not in start)
        if found:
            return found
        nxt = sorted({t for f in layer for t in links.get(f, ()) if t not in seen})
        seen.update(nxt)
        layer = nxt
    return []


def validate(doc: Mapping[str, Any], kind: str, xwalk: Mapping[str, Any]) -> None:
    """The model checks a folded-in proposal must pass. Raises ProposalError."""
    try:
        if kind == "sdl":
            sdl.collect(dict(doc), dict(xwalk))
        else:
            AttackGraph.from_dict(doc)
            project_model_graph(doc)
        for view in doc.get("views") or []:
            view_members(doc, view.get("focus_query") or "")
    except (sdl.SdlError, GraphError, KeyError, TypeError) as exc:
        raise ProposalError(f"proposal refused: the model would not hold together: {exc}") from exc


def _ids(doc: Mapping[str, Any]) -> set[str]:
    return {
        o["id"]
        for items in doc.values()
        if isinstance(items, list)
        for o in items
        if isinstance(o, dict) and "id" in o
    }


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
    id, changes something that is not there or already has a pending change, or
    would leave the model with a dangling reference or a broken review rule.
    Returns the proposal record as written.
    """
    kind = model_kind(model)
    check_patch(patch, kind)
    doc = yaml.safe_load(model.read_text(encoding="utf-8")) or {}
    pending = load_proposals(model)
    current = merged(doc, pending)
    known = _ids(current)
    add = {k: list(v) for k, v in (patch.get("add") or {}).items()}
    new_ids = [o["id"] for items in add.values() for o in items]
    new_ids += [a["id"] for a in patch.get("assertions") or []]
    problems = [f"{i}: id already exists" for i in new_ids if i in known]
    problems += [
        f"{i}: id given twice" for i in sorted({i for i in new_ids if new_ids.count(i) > 1})
    ]
    busy = {c["id"] for p in pending for c in [*(p.get("edits") or []), *(p.get("removals") or [])]}
    changes = [*(patch.get("edit") or []), *(patch.get("remove") or [])]
    touched = [c["id"] for c in changes]
    for c in changes:
        if _find(doc, c["collection"], c["id"]) is None:
            problems.append(f"{c['id']}: not in the model's {c['collection']}")
        elif c["id"] in busy:
            problems.append(f"{c['id']}: already has a pending change; decide that one first")
    problems += [
        f"{i}: changed twice in one patch"
        for i in sorted({i for i in touched if touched.count(i) > 1})
    ]
    proposer = patch["proposed_by"]
    if proposer not in known and proposer not in {p["id"] for p in add.get("parties", [])}:
        problems.append(f"proposed_by {proposer}: not a Party in the model or the patch")
    _fail(problems)

    stamp = (now or datetime.now(UTC)).replace(microsecond=0)
    at = stamp.isoformat().replace("+00:00", "Z")
    assertions = [
        dict(
            a,
            assertion_status="proposed",
            asserted_by=proposer,
            asserted_at=at,
            generated_by=patch["generated_by"],
        )
        for a in patch.get("assertions") or []
    ]
    body: dict[str, Any] = {"objects": add}
    if patch.get("edit"):
        body["edits"] = copy.deepcopy(list(patch["edit"]))
    if patch.get("remove"):
        body["removals"] = [{"collection": r["collection"], "id": r["id"]} for r in patch["remove"]]
    body["assertions"] = assertions
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
    # The model with this proposal folded in must still pass the model's checks.
    validate(merged(doc, [*pending, record]), kind, xwalk)
    if write:
        write_proposals(model, [*pending, record])
    return record


def summary(proposals: list[Mapping[str, Any]], doc: Mapping[str, Any]) -> list[dict[str, Any]]:
    """What GET /sdl and GET /proposals show of the pending proposals."""
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
                "changes": [
                    {
                        "action": "edit",
                        "collection": e.get("collection"),
                        "id": e.get("id"),
                        "fields": sorted([*(e.get("set") or {}), *(e.get("unset") or [])]),
                    }
                    for e in p.get("edits") or []
                ]
                + [
                    {
                        "action": "remove",
                        "collection": r.get("collection"),
                        "id": r.get("id"),
                        "fields": [],
                    }
                    for r in p.get("removals") or []
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


def views(doc: Mapping[str, Any], proposals: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Saved KG views for the Graph tab: the model's own, then the proposed ones.

    A proposed view (added or edited by a pending proposal) is marked `proposed` with
    its proposal id; a view a proposal would remove is marked `proposed_removal`.
    `node_ids` are the objects the view's focus query selects in the model with that
    proposal folded in, so a proposed view can show proposed objects.
    """
    out = []
    removing: dict[str, str] = {}
    for p in proposals:
        for r in p.get("removals") or []:
            if r.get("collection") == "views":
                removing[r["id"]] = p["id"]
    for v in doc.get("views") or []:
        out.append(
            _view_entry(
                doc,
                v,
                "proposed_removal" if v["id"] in removing else "accepted",
                removing.get(v["id"]),
            )
        )
    for p in proposals:
        folded = apply_record(copy.deepcopy(dict(doc)), p)
        edited = {e["id"] for e in p.get("edits") or [] if e.get("collection") == "views"}
        for v in folded.get("views") or []:
            added = v in (p.get("objects") or {}).get("views", [])
            if added or v["id"] in edited:
                out.append(_view_entry(folded, v, "proposed", p["id"]))
    return out


def _view_entry(
    doc: Mapping[str, Any], v: Mapping[str, Any], state: str, proposal: str | None
) -> dict[str, Any]:
    try:
        members, error = view_members(doc, v.get("focus_query") or ""), None
    except GraphError as exc:
        members, error = [], str(exc)
    entry = {
        "id": v.get("id"),
        "name": v.get("name", v.get("id")),
        "description": v.get("description", ""),
        "focus_query": v.get("focus_query", ""),
        "state": state,
        "proposal": proposal,
        "node_ids": members,
    }
    if error:
        entry["error"] = error
    return entry
