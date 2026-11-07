"""SDL program view of an SDL model: the data behind "tmodel SDL" (DL-0040, DL-0043).

One function, `collect()`, turns an SDL model (spec/vectors/sdl-*.yaml; the ADR-0013
classes SdlPractice, Evidence and RequirementSource) and the MAP-0001 crosswalk into
plain data: requirement sources with their decision, practices by phase with status,
evidence and selection state,
milestones, the product's threat model and the gaps. The engine's `GET /sdl` route
serves it to the desktop app, and docs/publishing/render_sdl.py renders the same data
as the static page, so the app and the page cannot disagree.

It also applies the PROC-0002 review rules (`governance()`): a selection is decided
only by a person's Review, never an AI agent's. Nothing here accepts anything; it reads
the Assertion + Review spine: every selection is a proposal until the sponsor's Review
decides it, and the payload says so.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

REPO = "https://github.com/Threat-Radar/tmodel/"
LIBRARY_REPO = "https://github.com/Threat-Radar/library/"
# Who may decide an SDL selection (PROC-0002). Keep in step with
# `required_reviewer_roles` in docs/publishing/sdl.yaml (a test checks).
DECIDER_ROLES = ("sponsor",)

PHASE_ORDER = [
    "concept",
    "design",
    "implementation",
    "verification_validation",
    "distribution",
    "operation",
    "maintenance",
    "end_of_support",
]
STATUS = {  # MitigationStatus -> label, css class
    "complete": ("Done", "ok"),
    "in_progress": ("In progress", "part"),
    "planned": ("Gap / planned", "gap"),
    "accepted_risk": ("Risk accepted", "part"),
    "not_applicable": ("Not applicable", "na"),
}
GATE_STATUS = {
    "planned": "Planned",
    "in_progress": "In progress",
    "passed": "Passed",
    "failed": "Failed",
    "waived": "Waived",
    "blocked": "Blocked",
}
SOURCE_PREDICATES = {
    "selects_requirement_source": "select",
    "considers_requirement_source": "candidate",
    "excludes_requirement_source": "not applicable",
}
# Every predicate that records an SDL selection (PROC-0002). Each Assertion with one of
# these is a proposal until a human Review decides it.
SELECTION_PREDICATES = frozenset(SOURCE_PREDICATES) | {
    "selects_practice",
    "proposes_milestone_name",
}
VERDICTS = {"accepted", "rejected", "changes_requested"}
REF_KEYS = {
    "composed_of",
    "manufactured_by",
    "supplied_by",
    "owned_by",
    "of_product",
    "current_phase",
    "applies_in_phase",
    "targets_element",
    "mitigates",
    "implementation_owner",
    "members",
    "owner",
    "governs",
    "program_nodes",
    "incorporates",
    "at_phase",
    "gated_by",
    "decided_by",
    "depends_on_node",
    "validates_conformance_of",
    "offset_from",
    "satisfied_by",
    "applies_to",
    "maps_to",
    "refines",
    "derived_from",
    "addresses",
    "subject",
    "object",
    "reviews",
    "reviewer",
    "asserted_by",
    "implements",
    "produces",
    "in_program_node",
    "source_members",
}


class SdlError(ValueError):
    """An SDL model breaks a rule: a dangling id, an unknown row or status, a review rule."""


def as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def index(doc: dict) -> dict:
    ids: dict = {}
    for coll, items in doc.items():
        if not isinstance(items, list):
            continue
        for it in items:
            if isinstance(it, dict) and "id" in it:
                if it["id"] in ids:
                    raise SdlError(f"duplicate id {it['id']}")
                ids[it["id"]] = dict(it, _coll=coll)
    return ids


def check_refs(ids: dict) -> None:
    bad = []
    for oid, obj in ids.items():
        for k in REF_KEYS & obj.keys():
            for ref in as_list(obj[k]):
                if (
                    isinstance(ref, str)
                    and ":" in ref
                    and not ref.startswith(("http", "library:"))
                    and ref not in ids
                ):
                    bad.append(f"{oid}.{k} -> {ref}")
    if bad:
        raise SdlError("dangling references:\n  " + "\n  ".join(bad))


def role(ids: dict, pid: str | None) -> str:
    """A party as a role, never a handle (published pages carry no identities)."""
    if not pid:
        return "unassigned"
    p = ids[pid]
    if p.get("party_kind") == "person":
        for c in as_list(p.get("classifications")):
            if str(c).startswith("role:"):
                return str(c)[5:].replace("-", " ")
        return "person"
    if p.get("party_kind") == "software_agent":
        return "AI agent"
    for c in as_list(p.get("classifications")):
        if str(c).startswith("role:"):
            return str(c)[5:].replace("-", " ")
    return str(p.get("name", pid))


def decision(doc: dict, ids: dict, assertion_id: str) -> dict:
    """The human verdict on a proposal: the latest Review that points at it."""
    revs = [r for r in as_list(doc.get("reviews")) if r.get("reviews") == assertion_id]
    a = ids[assertion_id]
    if not revs:
        return {
            "state": "proposed",
            "label": "Proposed, awaiting human review",
            "by": role(ids, a.get("asserted_by")),
            "css": "prop",
        }
    r = revs[-1]
    st = str(r.get("review_status", "")).lower()
    css = {"accepted": "ok", "rejected": "gap"}.get(st, "part")
    return {
        "state": st,
        "label": f"{st.replace('_', ' ').capitalize()} by {role(ids, r.get('reviewer'))}",
        "by": role(ids, r.get("reviewer")),
        "css": css,
        "why": r.get("justification", ""),
    }


def default_link(loc: str) -> str:
    """An absolute URL for a work-product locator or a library ref (the app has no site)."""
    if loc.startswith("http"):
        return loc
    if loc.startswith("library:"):
        return LIBRARY_REPO + "tree/main/records"
    kind = "tree" if loc.endswith("/") else "blob"
    return f"{REPO}{kind}/main/{loc}"


def map_columns(doc: dict, xwalk: dict, overrides: dict | None = None) -> dict:
    """RequirementSource id -> MAP-0001 column, matched on the set's library record."""
    by_record = {f.get("record"): key for key, f in (xwalk.get("frameworks") or {}).items()}
    cols = {}
    for rs in as_list(doc.get("requirement_sources")):
        rec = str(rs.get("source_ref", "")).removeprefix("library:").split("#", 1)[0]
        if rec in by_record:
            cols[rs["id"]] = by_record[rec]
    cols.update(overrides or {})
    return cols


def programs(doc: dict) -> list[dict]:
    return [
        {"id": p["id"], "name": p.get("name", p["id"])}
        for p in as_list(doc.get("security_programs"))
    ]


def _roles(party: dict) -> set:
    return {str(c)[5:] for c in as_list(party.get("classifications")) if str(c).startswith("role:")}


def governance(doc: dict, ids: dict, decider_roles: Iterable[str] = DECIDER_ROLES) -> list[dict]:
    """Check the PROC-0002 review rules; return the selections still awaiting a human.

    Fails (SdlError) when a selection is decided without a human Review, when an AI
    agent's Review tries to decide one, when a verdict is not one of VERDICTS, when a
    rejection or change request has no justification, when the Assertion's status and
    its latest Review disagree, or when the reviewer lacks one of `decider_roles`.
    """
    allowed = set(decider_roles)
    by_target: dict = {}
    for r in as_list(doc.get("reviews")):
        by_target.setdefault(r.get("reviews"), []).append(r)
    bad, waiting = [], []
    for a in as_list(doc.get("assertions")):
        if a.get("predicate") not in SELECTION_PREDICATES:
            continue
        status = str(a.get("assertion_status", "proposed")).lower()
        revs = by_target.get(a["id"], [])
        for r in revs:
            who = ids.get(r.get("reviewer"), {})
            verdict = str(r.get("review_status", "")).lower()
            if who.get("party_kind") != "person":
                bad.append(
                    f"{r['id']}: reviewer {r.get('reviewer')} is not a person; "
                    "an AI agent may propose but never decide (CLAUDE.md, PROC-0002)"
                )
            if verdict not in VERDICTS:
                bad.append(f"{r['id']}: review_status {verdict!r} is not one of {sorted(VERDICTS)}")
            if verdict in ("rejected", "changes_requested") and not r.get("justification"):
                bad.append(f"{r['id']}: a {verdict} verdict needs a justification")
            if allowed and who and not (_roles(who) & allowed):
                bad.append(
                    f"{r['id']}: reviewer {r.get('reviewer')} has none of the roles "
                    f"{sorted(allowed)} that may decide SDL selections"
                )
        if not revs:
            if status != "proposed":
                bad.append(
                    f"{a['id']}: assertion_status {status!r} with no Review; "
                    "a selection is decided only by a human Review (PROC-0002)"
                )
            waiting.append({"id": a["id"], "predicate": a["predicate"], "name": a.get("name", "")})
            continue
        last = str(revs[-1].get("review_status", "")).lower()
        if last in ("accepted", "rejected") and status != last:
            bad.append(
                f"{a['id']}: latest Review says {last} but assertion_status is {status!r}; "
                "set both (PROC-0002 step 3)"
            )
        if last == "changes_requested":
            waiting.append({"id": a["id"], "predicate": a["predicate"], "name": a.get("name", "")})
    if bad:
        raise SdlError("review rules (PROC-0002):\n  " + "\n  ".join(bad))
    return waiting


def collect(
    doc: dict,
    xwalk: dict,
    *,
    program: str | None = None,
    columns: dict | None = None,
    decider_roles: Iterable[str] = DECIDER_ROLES,
    link: Callable[[str], str] = default_link,
) -> dict[str, Any]:
    """The SDL view of one program in `doc` (the only one when `program` is None)."""
    ids = index(doc)
    check_refs(ids)
    waiting = governance(doc, ids, decider_roles)
    if program is None:
        found = programs(doc)
        if len(found) != 1:
            raise SdlError(f"name a program: the model has {len(found)}")
        program = found[0]["id"]
    prog = ids.get(program)
    if not prog or prog["_coll"] != "security_programs":
        raise SdlError(f"program {program} not found")
    product = ids[prog["governs"]]
    rows = {r["key"]: r for r in xwalk["rows"]}
    cols = map_columns(doc, xwalk, columns)

    # Requirement sets and their (proposed or decided) standing
    sets = []
    for a in as_list(doc.get("assertions")):
        if a.get("subject") == prog["id"] and a.get("predicate") in SOURCE_PREDICATES:
            rs = ids[a["object"]]
            sets.append(
                {
                    "id": rs["id"],
                    "name": rs.get("name"),
                    "proposal": SOURCE_PREDICATES[a["predicate"]],
                    "rationale": a.get("description", ""),
                    "decision": decision(doc, ids, a["id"]),
                    "link": link(rs["source_ref"]) if rs.get("source_ref") else "",
                    "members": [ids[m] for m in as_list(rs.get("source_members"))],
                    "column": cols.get(rs["id"]),
                }
            )
    shown_cols = [
        (s["column"], s["name"])
        for s in sets
        if s["column"] and s["proposal"] in ("select", "candidate")
    ]

    # Practices grouped by phase
    phases: dict = {}
    for p in as_list(doc.get("sdl_practices")):
        key = p.get("practice_key")
        if key not in rows:
            raise SdlError(f"{p['id']}: practice_key {key!r} is not a MAP-0001 row")
        st = p.get("mitigation_status")
        if st not in STATUS:
            raise SdlError(f"{p['id']}: unknown status {st!r}")
        row = rows[key]
        fw = {}
        for col, _name in shown_cols:
            cell = row["cells"].get(col) or {}
            fw[col] = list(cell.get("ids") or [])
        covered = sum(1 for c in row["cells"].values() if (c or {}).get("ids"))
        sel = [
            a
            for a in as_list(doc.get("assertions"))
            if a.get("predicate") == "selects_practice" and a.get("object") == p["id"]
        ]
        ph = ids[p["at_phase"]]
        phases.setdefault(ph["code"], {"name": ph.get("name"), "items": []})["items"].append(
            {
                "id": p["id"],
                "name": p.get("name"),
                "description": p.get("description", ""),
                "row": row["title"],
                "row_n": row["n"],
                "status": st,
                "owner": role(ids, p.get("owner")),
                "evidence": [
                    {
                        "name": ids[w].get("name"),
                        "href": link(ids[w]["locator"]),
                        "kind": ids[w].get("evidence_kind"),
                    }
                    for w in as_list(p.get("produces"))
                ],
                "requirements": [
                    {
                        "name": ids[r].get("name"),
                        "href": link(ids[r]["source_ref"]) if ids[r].get("source_ref") else "",
                    }
                    for r in as_list(p.get("implements"))
                ],
                "frameworks": fw,
                "covered": covered,
                "total": len(row["cells"]),
                "due": [ids[n].get("name") for n in as_list(p.get("in_program_node"))],
                "decision": decision(doc, ids, sel[-1]["id"])
                if sel
                else {
                    "state": "proposed",
                    "label": "Proposed delivery item, awaiting human selection",
                    "css": "prop",
                    "by": "",
                },
            }
        )
    phase_list = [dict(code=c, **phases[c]) for c in PHASE_ORDER if c in phases]

    # Milestones and gates, in program order
    nodes = []
    for nid in as_list(prog.get("program_nodes")):
        n = ids[nid]
        name_a = [
            a
            for a in as_list(doc.get("assertions"))
            if a.get("predicate") == "proposes_milestone_name" and a.get("object") == nid
        ]
        nodes.append(
            {
                "order": n.get("order"),
                "name": n.get("name"),
                "kind": {"gates": "Gate", "milestones": "Milestone", "checkpoints": "Checkpoint"}[
                    n["_coll"]
                ],
                "planned": n.get("planned_date", ""),
                "actual": n.get("actual_date", ""),
                "status": GATE_STATUS.get(n.get("gate_status"), n.get("gate_status", "")),
                "owner": role(ids, n.get("owner")),
                "description": n.get("description", ""),
                "gated_by": [ids[r].get("name") for r in as_list(n.get("gated_by"))],
                "practices": sum(
                    1 for ph in phase_list for it in ph["items"] if n.get("name") in it["due"]
                ),
                "name_decision": decision(doc, ids, name_a[-1]["id"]) if name_a else None,
            }
        )
    nodes.sort(key=lambda x: x["order"] or 0)

    # Threat model of the product
    weak_of = {
        a["subject"]: ids[a["object"]]
        for a in as_list(doc.get("assertions"))
        if a.get("predicate") == "exploits_weakness"
    }
    capec_of = {
        a["subject"]: ids[a["object"]]
        for a in as_list(doc.get("assertions"))
        if a.get("predicate") == "exploited_by"
    }
    threats = []
    for t in as_list(doc.get("threat_instances")):
        w = weak_of.get(t["id"])
        c = capec_of.get(w["id"]) if w else None
        mits = [
            m for m in as_list(doc.get("mitigations")) if t["id"] in as_list(m.get("mitigates"))
        ]
        threats.append(
            {
                "name": t.get("name"),
                "description": t.get("description", ""),
                "cwe": w.get("catalog_ref") if w else "",
                "capec": c.get("catalog_ref") if c else "",
                "mitigations": [
                    {"name": m.get("name"), "status": m.get("mitigation_status")} for m in mits
                ],
            }
        )
    tm = next(
        (
            ids[x]
            for x in ids
            if ids[x]["_coll"] == "threat_models"
            and prog["governs"] in as_list(ids[x].get("members"))
        ),
        None,
    )

    # Gaps: planned practices, planned mitigations, MAP-0001 rows with no practice
    gaps = [
        f"{it['name']}: {it['description']}"
        for ph in phase_list
        for it in ph["items"]
        if it["status"] == "planned"
    ]
    gaps += [
        f"{m.get('name')}: {m.get('description', '')}".rstrip(": ")
        for m in as_list(doc.get("mitigations"))
        if m.get("mitigation_status") == "planned"
    ]
    used = {p.get("practice_key") for p in as_list(doc.get("sdl_practices"))}
    uncovered = [r["title"] for r in xwalk["rows"] if r["key"] not in used]

    return {
        "proposal": "Example data: each selection is a proposal until the sponsor reviews it",
        "product": {"name": product.get("name"), "description": product.get("description", "")},
        "program": {
            "name": prog.get("name"),
            "revision": prog.get("revision"),
            "governance": prog.get("governance_status"),
            "approval": prog.get("approval_status"),
            "owner": role(ids, prog.get("owner")),
            "description": prog.get("description", ""),
        },
        "sets": sets,
        "columns": shown_cols,
        "phases": phase_list,
        "nodes": nodes,
        "threats": threats,
        "threat_model": {"name": tm.get("name"), "status": tm.get("governance_status")}
        if tm
        else None,
        "gaps": gaps,
        "uncovered": uncovered,
        "map_rows": len(xwalk["rows"]),
        "awaiting_review": waiting,
        "counts": {
            k: sum(1 for ph in phase_list for it in ph["items"] if it["status"] == k)
            for k in STATUS
        },
    }
