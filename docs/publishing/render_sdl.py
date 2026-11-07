#!/usr/bin/env python3
"""Render an SDL example model as one static page: "tmodel SDL" (DL-0040).

Reads docs/publishing/sdl.yaml. Each entry names an SDL model in spec/vectors/
(validated by example-container-sdl.linkml.yaml) and the page to write. Two steps,
as render_tara.py does:

    collect(doc, entry) -> dict    the page's sections as plain data; fails on a
                                   dangling id, an unknown MAP-0001 row or status
    render(data) -> str            one self-contained page, no scripts

The page adds no judgement of its own. Status, owners and evidence come from the
model; the framework ids per practice come from spec/MAP-0001.yaml; every
selection (practice, requirement set, milestone name) is read from the Assertion +
Review spine, so it shows "proposed" until a human Review accepts or rejects it.
People render as roles (CLAUDE.md, check_identities.py). Licensed standards: ids
only (#154).

    engine/.venv/bin/python docs/publishing/render_sdl.py           # write
    engine/.venv/bin/python docs/publishing/render_sdl.py --check   # compare only
    engine/.venv/bin/python docs/publishing/render_sdl.py --check --strict
                                   # also fail while a selection awaits review

Review rules (PROC-0002) are checked on every run: a selection is decided only by a
person's Review, never an AI agent's; see governance().

The same collect() output is the shape an engine route (e.g. GET /sdl) would
return to the desktop app; see DL-0040.
"""
from __future__ import annotations

import hashlib
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "publishing" / "sdl.yaml"
MAP_0001 = ROOT / "spec" / "MAP-0001.yaml"
REPO = "https://github.com/Threat-Radar/tmodel/"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_nav  # noqa: E402  (site nav from docs/publishing/site.yaml)
from render_report import CSS as REPORT_CSS  # noqa: E402  (same look as the reports)

try:  # PyYAML, as render_tara.py: the engine's environment (CONTRIBUTING §10) has it
    import yaml
except ModuleNotFoundError as exc:
    raise SystemExit(
        "render_sdl: PyYAML is missing; run it with engine/.venv/bin/python or "
        "spec/schema tooling (CONTRIBUTING §10)"
    ) from exc


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


PHASE_ORDER = ["concept", "design", "implementation", "verification_validation",
               "distribution", "operation", "maintenance", "end_of_support"]
STATUS = {  # MitigationStatus -> label, css class
    "complete": ("Done", "ok"),
    "in_progress": ("In progress", "part"),
    "planned": ("Gap / planned", "gap"),
    "accepted_risk": ("Risk accepted", "part"),
    "not_applicable": ("Not applicable", "na"),
}
GATE_STATUS = {"planned": "Planned", "in_progress": "In progress", "passed": "Passed",
               "failed": "Failed", "waived": "Waived", "blocked": "Blocked"}
SOURCE_PREDICATES = {
    "selects_requirement_source": "select",
    "considers_requirement_source": "candidate",
    "excludes_requirement_source": "not applicable",
}
# Every predicate that records an SDL selection (PROC-0002). Each Assertion with one of
# these is a proposal until a human Review decides it.
SELECTION_PREDICATES = frozenset(SOURCE_PREDICATES) | {"selects_practice", "proposes_milestone_name"}
VERDICTS = {"accepted", "rejected", "changes_requested"}
REF_KEYS = {
    "composed_of", "manufactured_by", "supplied_by", "owned_by", "of_product", "current_phase",
    "applies_in_phase", "targets_element", "mitigates", "implementation_owner", "members",
    "owner", "governs", "program_nodes", "incorporates", "at_phase", "gated_by", "decided_by",
    "depends_on_node", "validates_conformance_of", "offset_from", "satisfied_by", "applies_to",
    "maps_to", "refines", "derived_from", "addresses", "subject", "object", "reviews",
    "reviewer", "asserted_by", "implements", "produces", "in_program_node", "source_members",
}


class SdlError(Exception):
    pass


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


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
                if isinstance(ref, str) and ":" in ref and not ref.startswith(("http", "library:")) \
                        and ref not in ids:
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
        return {"state": "proposed", "label": "Proposed, awaiting human review",
                "by": role(ids, a.get("asserted_by")), "css": "prop"}
    r = revs[-1]
    st = str(r.get("review_status", "")).lower()
    css = {"accepted": "ok", "rejected": "gap"}.get(st, "part")
    return {"state": st, "label": f"{st.replace('_', ' ').capitalize()} by {role(ids, r.get('reviewer'))}",
            "by": role(ids, r.get("reviewer")), "css": css, "why": r.get("justification", "")}


def link_for(loc: str, depth: int) -> str:
    """URL for a work-product locator or a library ref, relative where the site has it."""
    if loc.startswith("http"):
        return loc
    if loc.startswith("library:"):
        rec = loc[len("library:"):].split("#", 1)[0]
        hits = list((ROOT / "docs" / "library" / "records").glob(f"*/{rec}/summary.html"))
        if hits:
            return "../" * depth + str(hits[0].relative_to(ROOT / "docs"))
        return REPO.replace("/tmodel/", "/library/") + f"tree/main/records"
    kind = "tree" if loc.endswith("/") else "blob"
    return f"{REPO}{kind}/main/{loc}"


def _roles(party: dict) -> set:
    return {str(c)[5:] for c in as_list(party.get("classifications")) if str(c).startswith("role:")}


def governance(doc: dict, ids: dict, entry: dict) -> list[dict]:
    """Check the PROC-0002 review rules; return the selections still awaiting a human.

    Fails (SdlError) when a selection is decided without a human Review, when an AI
    agent's Review tries to decide one, when a verdict is not one of VERDICTS, when a
    rejection or change request has no justification, when the Assertion's status and
    its latest Review disagree, or when the reviewer lacks a role the manifest's
    `required_reviewer_roles` names.
    """
    allowed = set(as_list(entry.get("required_reviewer_roles")))
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
                bad.append(f"{r['id']}: reviewer {r.get('reviewer')} is not a person; "
                           "an AI agent may propose but never decide (CLAUDE.md, PROC-0002)")
            if verdict not in VERDICTS:
                bad.append(f"{r['id']}: review_status {verdict!r} is not one of {sorted(VERDICTS)}")
            if verdict in ("rejected", "changes_requested") and not r.get("justification"):
                bad.append(f"{r['id']}: a {verdict} verdict needs a justification")
            if allowed and who and not (_roles(who) & allowed):
                bad.append(f"{r['id']}: reviewer {r.get('reviewer')} has none of the roles "
                           f"{sorted(allowed)} that may decide SDL selections")
        if not revs:
            if status != "proposed":
                bad.append(f"{a['id']}: assertion_status {status!r} with no Review; "
                           "a selection is decided only by a human Review (PROC-0002)")
            waiting.append({"id": a["id"], "predicate": a["predicate"], "name": a.get("name", "")})
            continue
        last = str(revs[-1].get("review_status", "")).lower()
        if last in ("accepted", "rejected") and status != last:
            bad.append(f"{a['id']}: latest Review says {last} but assertion_status is {status!r}; "
                       "set both (PROC-0002 step 3)")
        if last == "changes_requested":
            waiting.append({"id": a["id"], "predicate": a["predicate"], "name": a.get("name", "")})
    if bad:
        raise SdlError("review rules (PROC-0002):\n  " + "\n  ".join(bad))
    return waiting


def collect(doc: dict, entry: dict, xwalk: dict) -> dict:
    ids = index(doc)
    check_refs(ids)
    waiting = governance(doc, ids, entry)
    depth = entry["out"].count("/") - 1
    prog = ids.get(entry["program"])
    if not prog or prog["_coll"] != "security_programs":
        raise SdlError(f"program {entry['program']} not found")
    product = ids[prog["governs"]]
    rows = {r["key"]: r for r in xwalk["rows"]}
    cols = entry.get("map_columns") or {}

    # Requirement sets and their (proposed or decided) standing
    sets = []
    for a in as_list(doc.get("assertions")):
        if a.get("subject") == prog["id"] and a.get("predicate") in SOURCE_PREDICATES:
            rs = ids[a["object"]]
            sets.append({
                "id": rs["id"], "name": rs.get("name"), "proposal": SOURCE_PREDICATES[a["predicate"]],
                "rationale": a.get("description", ""), "decision": decision(doc, ids, a["id"]),
                "link": link_for(rs["source_ref"], depth) if rs.get("source_ref") else "",
                "members": [ids[m] for m in as_list(rs.get("source_members"))],
                "column": cols.get(rs["id"]),
            })
    shown_cols = [(s["column"], s["name"]) for s in sets
                  if s["column"] and s["proposal"] in ("select", "candidate")]

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
        sel = [a for a in as_list(doc.get("assertions"))
               if a.get("predicate") == "selects_practice" and a.get("object") == p["id"]]
        ph = ids[p["at_phase"]]
        phases.setdefault(ph["code"], {"name": ph.get("name"), "items": []})["items"].append({
            "id": p["id"], "name": p.get("name"), "description": p.get("description", ""),
            "row": row["title"], "row_n": row["n"], "status": st, "owner": role(ids, p.get("owner")),
            "evidence": [{"name": ids[w].get("name"), "href": link_for(ids[w]["locator"], depth),
                          "kind": ids[w].get("evidence_kind")} for w in as_list(p.get("produces"))],
            "requirements": [{"name": ids[r].get("name"), "href": link_for(ids[r]["source_ref"], depth)
                              if ids[r].get("source_ref") else ""} for r in as_list(p.get("implements"))],
            "frameworks": fw, "covered": covered, "total": len(row["cells"]),
            "due": [ids[n].get("name") for n in as_list(p.get("in_program_node"))],
            "decision": decision(doc, ids, sel[-1]["id"]) if sel else
            {"state": "proposed", "label": "Proposed delivery item, awaiting human selection",
             "css": "prop", "by": ""},
        })
    phase_list = [dict(code=c, **phases[c]) for c in PHASE_ORDER if c in phases]

    # Milestones and gates, in program order
    nodes = []
    for nid in as_list(prog.get("program_nodes")):
        n = ids[nid]
        name_a = [a for a in as_list(doc.get("assertions"))
                  if a.get("predicate") == "proposes_milestone_name" and a.get("object") == nid]
        nodes.append({
            "order": n.get("order"), "name": n.get("name"),
            "kind": {"gates": "Gate", "milestones": "Milestone", "checkpoints": "Checkpoint"}[n["_coll"]],
            "planned": n.get("planned_date", ""), "actual": n.get("actual_date", ""),
            "status": GATE_STATUS.get(n.get("gate_status"), n.get("gate_status", "")),
            "owner": role(ids, n.get("owner")), "description": n.get("description", ""),
            "gated_by": [ids[r].get("name") for r in as_list(n.get("gated_by"))],
            "practices": sum(1 for ph in phase_list for it in ph["items"] if n.get("name") in it["due"]),
            "name_decision": decision(doc, ids, name_a[-1]["id"]) if name_a else None,
        })
    nodes.sort(key=lambda x: x["order"] or 0)

    # Threat model of the product
    weak_of = {a["subject"]: ids[a["object"]] for a in as_list(doc.get("assertions"))
               if a.get("predicate") == "exploits_weakness"}
    capec_of = {a["subject"]: ids[a["object"]] for a in as_list(doc.get("assertions"))
                if a.get("predicate") == "exploited_by"}
    threats = []
    for t in as_list(doc.get("threat_instances")):
        w = weak_of.get(t["id"])
        c = capec_of.get(w["id"]) if w else None
        mits = [m for m in as_list(doc.get("mitigations")) if t["id"] in as_list(m.get("mitigates"))]
        threats.append({
            "name": t.get("name"), "description": t.get("description", ""),
            "cwe": w.get("catalog_ref") if w else "", "capec": c.get("catalog_ref") if c else "",
            "mitigations": [{"name": m.get("name"), "status": m.get("mitigation_status")} for m in mits],
        })
    tm = next((ids[x] for x in ids if ids[x]["_coll"] == "threat_models"
               and prog["governs"] in as_list(ids[x].get("members"))), None)

    # Gaps: planned practices, planned mitigations, MAP-0001 rows with no practice
    gaps = [f"{it['name']}: {it['description']}" for ph in phase_list for it in ph["items"]
            if it["status"] == "planned"]
    gaps += [f"{m.get('name')}: {m.get('description', '')}".rstrip(": ")
             for m in as_list(doc.get("mitigations")) if m.get("mitigation_status") == "planned"]
    used = {p.get("practice_key") for p in as_list(doc.get("sdl_practices"))}
    uncovered = [r["title"] for r in xwalk["rows"] if r["key"] not in used]

    return {
        "title": entry["title"], "src": entry["src"], "depth": depth,
        "product": {"name": product.get("name"), "description": product.get("description", "")},
        "program": {"name": prog.get("name"), "revision": prog.get("revision"),
                    "governance": prog.get("governance_status"), "approval": prog.get("approval_status"),
                    "owner": role(ids, prog.get("owner")), "description": prog.get("description", "")},
        "sets": sets, "columns": shown_cols, "phases": phase_list, "nodes": nodes,
        "threats": threats,
        "threat_model": {"name": tm.get("name"), "status": tm.get("governance_status")} if tm else None,
        "gaps": gaps, "uncovered": uncovered, "map_rows": len(xwalk["rows"]),
        "awaiting_review": waiting,
        "counts": {k: sum(1 for ph in phase_list for it in ph["items"] if it["status"] == k) for k in STATUS},
    }


CSS = REPORT_CSS + """
body{max-width:72rem}
.banner{background:#fff4d6;border:1px solid #e8c766;border-radius:6px;padding:.6rem .9rem;margin:1rem 0;font-size:.95em}
.pill{display:inline-block;border-radius:999px;padding:.05rem .55rem;font-size:.82em;white-space:nowrap;border:1px solid}
.ok{background:#e7f6ea;border-color:#9fd3aa;color:#1d5b2a}.part{background:#fff6e0;border-color:#e8c766;color:#6b4e00}
.gap{background:#fde8e8;border-color:#eba3a3;color:#7d1f1f}.na{background:#f1f1f1;border-color:#ccc;color:#555}
.prop{background:#eef2fb;border-color:#a9b8e0;color:#273e7a}
.small{font-size:.85em;color:#555} td ul{margin:0;padding-left:1.1rem} .fw code{font-size:.8em}
.kpis{display:flex;flex-wrap:wrap;gap:.6rem;margin:.6rem 0}.kpis span{border:1px solid #ddd;border-radius:6px;padding:.3rem .7rem}
h2{margin-top:2rem}"""


def pill(text: str, css: str) -> str:
    return f'<span class="pill {css}">{esc(text)}</span>'


def render(d: dict) -> str:
    out = []
    w = out.append
    w(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(d['title'])}</title><style>{CSS}</style></head><body>
{site_nav.header(d['depth'], '')}
<h1>{esc(d['title'])}: {esc(d['product']['name'])}</h1>
<div class="banner"><strong>Example data, draft.</strong> Built from an example SDL model, not from
approved project records. Every selection on this page is a proposal until a human review accepts it;
status was drafted by an AI agent from repository evidence and has not been reviewed. Not a
conformance claim. Licensed standards appear as ids only.</div>
<p>{esc(d['product']['description'])}</p>
<p class="small">Program: <strong>{esc(d['program']['name'])}</strong> · revision {esc(d['program']['revision'])}
· {esc(d['program']['governance'])} · approval {esc(d['program']['approval'])} · owner: {esc(d['program']['owner'])}</p>
<div class="kpis">""")
    for k, (label, css) in STATUS.items():
        if d["counts"].get(k):
            w(f"<span>{pill(label, css)} {d['counts'][k]}</span>")
    w(f"<span>{len(d['gaps'])} open gaps</span>"
      f"<span>{pill(str(len(d['awaiting_review'])) + ' selections awaiting human review', 'prop')}</span></div>")

    w("<h2>Governing requirement sets</h2><table><tr><th>Set</th><th>Proposal</th><th>Why</th><th>Decision</th></tr>")
    for s in d["sets"]:
        css = {"select": "ok", "candidate": "part", "not applicable": "na"}[s["proposal"]]
        name = f'<a href="{esc(s["link"])}">{esc(s["name"])}</a>' if s["link"] else esc(s["name"])
        mem = ", ".join(esc(m.get("name")) for m in s["members"])
        w(f"<tr><td>{name}{f'<div class=small>used here: {mem}</div>' if mem else ''}</td>"
          f"<td>{pill(s['proposal'], css)}</td><td>{esc(s['rationale'])}</td>"
          f"<td>{pill(s['decision']['label'], s['decision']['css'])}</td></tr>")
    w("</table>")

    w("<h2>Practices by phase</h2><p class='small'>Each practice is a row of the MAP-0001 crosswalk; "
      "the framework columns show that row's ids for the selected and candidate sets, and how many of the "
      f"crosswalk's frameworks cover it.</p>")
    cols = d["columns"]
    for ph in d["phases"]:
        w(f"<h3>{esc(ph['name'])}</h3><table><tr><th>Practice</th><th>Status</th><th>Owner</th>"
          f"<th>Evidence</th><th>Frameworks</th><th>Selection</th></tr>")
        for it in ph["items"]:
            label, css = STATUS[it["status"]]
            ev = "".join(f'<li><a href="{esc(e["href"])}">{esc(e["name"])}</a></li>' for e in it["evidence"])
            rq = "".join(f'<li><a href="{esc(r["href"])}">{esc(r["name"])}</a></li>' if r["href"]
                         else f"<li>{esc(r['name'])}</li>" for r in it["requirements"])
            fw = "".join(
                f"<div><span class=small>{esc(col)}:</span> "
                f"<code>{esc(', '.join(it['frameworks'].get(col) or []) or '—')}</code></div>"
                for col, _n in cols)
            due = f"<div class=small>due: {esc(', '.join(it['due']))}</div>" if it["due"] else ""
            w(f"<tr><td><strong>{esc(it['name'])}</strong><div class=small>MAP-0001 row {esc(it['row_n'])}: "
              f"{esc(it['row'])}</div><div class=small>{esc(it['description'])}</div>{due}</td>"
              f"<td>{pill(label, css)}</td><td>{esc(it['owner'])}</td>"
              f"<td><ul>{ev}</ul>{f'<div class=small>implements:</div><ul>{rq}</ul>' if rq else ''}</td>"
              f"<td class=fw>{fw}<div class=small>{it['covered']} of {it['total']} frameworks</div></td>"
              f"<td>{pill(it['decision']['label'], it['decision']['css'])}</td></tr>")
        w("</table>")

    w("<h2>Milestones and gates</h2><table><tr><th>#</th><th>Name</th><th>Kind</th><th>Planned</th>"
      "<th>Status</th><th>Owner</th><th>Practices due</th><th>Name</th></tr>")
    for n in d["nodes"]:
        nd = n["name_decision"]
        gb = f"<div class=small>gated by: {esc(', '.join(n['gated_by']))}</div>" if n["gated_by"] else ""
        w(f"<tr><td>{esc(n['order'])}</td><td><strong>{esc(n['name'])}</strong>"
          f"<div class=small>{esc(n['description'])}</div>{gb}</td><td>{esc(n['kind'])}</td>"
          f"<td>{esc(n['planned'])}{' / ' + esc(n['actual']) if n['actual'] else ''}</td>"
          f"<td>{esc(n['status'])}</td><td>{esc(n['owner'])}</td><td>{n['practices']}</td>"
          f"<td>{pill(nd['label'], nd['css']) if nd else ''}</td></tr>")
    w("</table>")

    if d["threats"]:
        tmn = d["threat_model"]
        w(f"<h2>Threat model of the product</h2><p class=small>{esc(tmn['name']) if tmn else ''}"
          f"{' · ' + esc(tmn['status']) if tmn else ''} · weakness and attack-pattern links are proposed, "
          "not reviewed.</p><table><tr><th>Threat</th><th>CWE</th><th>CAPEC</th><th>Mitigations</th></tr>")
        for t in d["threats"]:
            mi = "".join(f"<li>{esc(m['name'])} {pill(STATUS[m['status']][0], STATUS[m['status']][1])}</li>"
                         for m in t["mitigations"])
            w(f"<tr><td><strong>{esc(t['name'])}</strong><div class=small>{esc(t['description'])}</div></td>"
              f"<td>{esc(t['cwe'])}</td><td>{esc(t['capec'])}</td><td><ul>{mi}</ul></td></tr>")
        w("</table>")

    w("<h2>Open gaps</h2><ul>" + "".join(f"<li>{esc(g)}</li>" for g in d["gaps"]) + "</ul>")
    if d["uncovered"]:
        w(f"<p class=small>MAP-0001 practices with no entry in this program yet "
          f"({len(d['uncovered'])} of {d['map_rows']}): {esc('; '.join(d['uncovered']))}.</p>")
    w(f"""<footer>Generated from <code>{esc(d['src'])}</code> (sha256 {esc(d['digest'][:12])}) and
<code>spec/MAP-0001.yaml</code> by <code>docs/publishing/render_sdl.py</code>; schema proposal in
<code>spec/schema/tmodel-object-model.linkml.yaml</code> (SDL classes: ADR-0013). Do not hand-edit: change the model and
re-run. No personal identities are published (people show as roles; enforced by
<code>check_identities.py</code>).</footer></body></html>
""")
    return "".join(out)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    strict = "--strict" in argv  # also fail while any selection awaits review (a gate)
    manifest = load(MANIFEST)
    xwalk = load(MAP_0001)
    stale = 0
    for entry in manifest.get("pages") or []:
        src = ROOT / entry["src"]
        try:
            data = collect(load(src), entry, xwalk)
        except (SdlError, KeyError) as exc:
            print(f"render_sdl: {entry['src']}: {exc}", file=sys.stderr)
            return 1
        data["digest"] = hashlib.sha256(src.read_bytes()).hexdigest()
        if data["awaiting_review"]:
            print(f"render_sdl: {entry['src']}: {len(data['awaiting_review'])} selections await "
                  "human review (PROC-0002)", file=sys.stderr)
            if strict:
                for a in data["awaiting_review"]:
                    print(f"  {a['id']} ({a['predicate']})", file=sys.stderr)
                stale += 1
        page = render(data)
        out = ROOT / entry["out"]
        if check:
            if not out.exists() or out.read_text(encoding="utf-8") != page:
                print(f"render_sdl: {entry['out']} is stale; run docs/publishing/render_sdl.py", file=sys.stderr)
                stale += 1
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"  {entry['out']}  ({sum(len(p['items']) for p in data['phases'])} practices, "
              f"{len(data['nodes'])} program nodes, {len(data['gaps'])} gaps)")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
