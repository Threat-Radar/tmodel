#!/usr/bin/env python3
"""Render example models as TARA-shaped pages, in ISO/SAE 21434 clause 15 order.

Reads docs/publishing/tara.yaml. Each entry names a model in spec/vectors/ and the
page to write. The model is read through the engine (engine/engine/load/vector.py
and graph.py): the same YAML checks as the app's /graph, and the same review rule
as attack-path enumeration, under which a threat counts as reviewed only when every
attack path for it has an accepted Assertion. Two steps, kept apart as DL-0027
plans them (#181 collect, #182 render):

    collect(doc, entry) -> dict    the TARA, section by section, as plain data
    render(tara) -> str            one self-contained static page

This is the MVP stop-gap (#202 item 3, DL-0037), not the governed TARA of
DL-0027: nothing on the page is approved, and every page says it is a draft built
from example data. It adds no judgement of its own. Every rating, risk value and
decision is read from the model, and the build fails where a written reason and
its rating disagree. ISO/SAE 21434 is licensed, so the page paraphrases it and
cites clause, provision and table ids only (#154). Needs the engine's PyYAML
(CONTRIBUTING §10):

    engine/.venv/bin/python docs/publishing/render_tara.py           # write
    engine/.venv/bin/python docs/publishing/render_tara.py --check   # compare only
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "publishing" / "tara.yaml"
REPORTS = ROOT / "docs" / "publishing" / "reports.yaml"  # its `listed:` puts each page on the index
REPO = "https://github.com/Threat-Radar/tmodel/blob/main/"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "engine"))
try:
    import yaml
    from engine.graph import AttackGraph, GraphError
    from engine.load.vector import load_vector_document
except ModuleNotFoundError as exc:  # PyYAML missing: not the engine's environment
    raise SystemExit(
        f"render_tara: {exc.name} is missing; run it with engine/.venv/bin/python "
        "(CONTRIBUTING §10)"
    ) from exc
import site_nav  # noqa: E402  (site nav from docs/publishing/site.yaml)
from render_report import CSS as REPORT_CSS  # noqa: E402  (same look as the reports)

CATEGORIES = ("safety", "financial", "operational", "privacy")
FEASIBILITY = {"high": "High", "medium": "Medium", "low": "Low", "very_low": "Very low"}
GATES = {"and_gate": "AND", "or_gate": "OR"}
PREDICATES = {
    "instance_of": "is an instance of",
    "exploited_by": "is exploited by",
    "propagates_to": "reaches",
    "realizes_threat": "realizes",
    "addresses": "addresses",
}
SECTIONS = (
    ("item", "Item and scope", "9.3"),
    ("assets", "Assets and damage scenarios", "15.3"),
    ("threats", "Threat scenarios", "15.4"),
    ("impact", "Impact rating", "15.5"),
    ("paths", "Attack paths", "15.6"),
    ("feasibility", "Attack feasibility", "15.7"),
    ("risk", "Risk values", "15.8"),
    ("treatment", "Risk treatment decisions", "15.9"),
    ("requirements", "Requirements the TARA produced", "9.5"),
    ("left-out", "Left out: not reviewed or rejected", ""),
    ("reviews", "Review record", ""),
    ("gaps", "What this draft does not have yet", ""),
)
# A RiskScore description carries one paragraph per clause until the schema has
# fields for them (#184 F1, F3, F5): "Impact (15.5), ...", "Treatment decision
# (15.9): reduce ...". Unlabelled paragraphs are the score's general description.
LABEL = re.compile(r"^(?P<label>[A-Z][a-z]+(?: [a-z]+)?) \((?P<clause>15\.[3-9])\)[,:]?\s*(?P<body>.+)$", re.S)
REASON = re.compile(r"\b(Safety|Financial|Operational|Privacy) (severe|major|moderate|negligible): ")
DECISION = re.compile(r"^(?P<d>(?:avoid|reduce|share|retain)(?:(?:, | and )(?:avoid|reduce|share|retain))*)\b")
RISK = re.compile(r"^(?P<vals>[a-z]+ [1-5](?: / [a-z]+ [1-5])*)\s*(?:\((?P<how>.+)\))?\s*$", re.S)

CSS = REPORT_CSS + """
.banner{background:#fff4d6;border:2px solid #c99700;border-radius:6px;padding:.7rem 1rem;margin:1rem 0}
.cl{font-size:.65em;font-weight:600;color:#444;background:#eef0f3;border-radius:4px;padding:.1em .45em;vertical-align:middle;margin-left:.3rem}
.tag{display:inline-block;font-size:.82em;line-height:1.4;border:1px solid;border-radius:4px;padding:0 .4em;white-space:nowrap}
.ok{color:#14532d;background:#ecfdf3;border-color:#9fd3b2}.no{color:#7f1d1d;background:#fef2f2;border-color:#efb1b1}
.open{color:#6b4e00;background:#fefbe8;border-color:#e3cf7d}.gate{color:#333;background:#f1f1f1;border-color:#c8c8c8}
.aside{border:1px dashed #b9b9b9;border-radius:6px;padding:.1rem 1rem .4rem;margin:1rem 0;background:#fafafa}
.lead{color:#444} .muted{color:#666;font-size:.92em} td.n{text-align:center;font-weight:650;white-space:nowrap}
.toc{columns:2 16rem;padding-left:1.2rem} .toc li{margin:.1rem 0}
ul.parts{margin:.2rem 0 .2rem 1.1rem;padding:0} ol.steps{padding-left:1.4rem} ol.steps li{margin:.25rem 0}
@media print{.site-nav{display:none}}"""


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def git_blob(data: bytes) -> str:
    """The id git gives these bytes as a blob, so a reader can match the page to a commit."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class Model:
    """Id lookup over a model document."""

    def __init__(self, doc: dict) -> None:
        self.doc = doc
        self.by_id: dict[str, dict] = {}
        for items in doc.values():
            for obj in items if isinstance(items, list) else []:
                if isinstance(obj, dict) and isinstance(obj.get("id"), str):
                    self.by_id[obj["id"]] = obj

    def all(self, collection: str) -> list[dict]:
        return [o for o in self.doc.get(collection) or [] if isinstance(o, dict)]

    def get(self, oid: object) -> dict:
        return self.by_id.get(oid, {}) if isinstance(oid, str) else {}

    def name(self, oid: object) -> str:
        return self.get(oid).get("name") or str(oid)

    def label(self, oid: object) -> str:
        """A catalog entry by its id (CVE-2026-41200; CWE-306 with its name), anything else by name."""
        ref = self.get(oid).get("catalog_ref")
        if not ref:
            return self.name(oid)
        return ref if oid in {v["id"] for v in self.all("vulnerabilities")} else f"{ref} ({self.name(oid)})"

    def party(self, oid: object) -> str:
        """Organizations by name; a person only as a role (DL-0027, check_identities.py)."""
        if not oid:
            return ""
        return "a human reviewer (example role)" if self.get(oid).get("party_kind") == "person" else self.name(oid)

    @staticmethod
    def refs(obj: dict, slot: str) -> list[str]:
        value = obj.get(slot)
        return [v for v in (value if isinstance(value, list) else [value]) if isinstance(v, str)]


def paragraphs(text: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    general = []
    for para in (text or "").split("\n"):
        para = para.strip()
        m = LABEL.match(para)
        if m:
            out[m["clause"]] = m["body"].strip()
        elif para:
            general.append(para)
    out[""] = " ".join(general)
    return out


def sentence(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def collect(doc: dict, entry: dict) -> dict:
    m = Model(doc)
    try:
        graph = AttackGraph.from_dict(doc)
    except GraphError as exc:
        raise SystemExit(f"{entry['src']}: {exc}") from exc
    item = m.get(entry["item"])
    if not item:
        raise SystemExit(f"{entry['src']}: the item {entry['item']} is not in the model")
    review_of = {r.get("reviews"): r for r in m.all("reviews")}
    threats = m.all("threat_instances")
    tids = [t["id"] for t in threats if graph.threat_reviewed(t["id"])]
    scores = [r for r in m.all("risk_scores") if r.get("threat") in tids]
    mits = [x for x in m.all("mitigations") if set(m.refs(x, "mitigates")) & set(tids)]
    mit_ids = {x["id"] for x in mits}

    def claim(a: dict) -> dict:
        r = review_of.get(a["id"], {})
        return {
            "text": f"{m.label(a.get('subject'))} {PREDICATES.get(a.get('predicate'), a.get('predicate'))} {m.label(a.get('object'))}",
            "name": a.get("name") or a["id"],
            "status": a.get("assertion_status") or "no status",
            "review": r.get("review_status") or "",
            "by": m.party(r.get("reviewer")),
            "why": r.get("justification") or "",
        }

    def path_view(pid: str) -> dict:
        raw, p = m.get(pid), graph.paths[pid]
        order = {sid: n for n, sid in enumerate(p.steps, 1)}
        steps = []
        for sid in p.steps:
            s = graph.steps[sid]
            needs = [order[x] for x in graph.predecessors(sid) if x in order]
            steps.append({"name": s.name or sid, "gate": GATES.get(s.gate or "", ""), "needs": needs,
                          "phase": (s.kill_chain_phase or "").replace("_", " ")})
        realizing = next((a for a in m.all("assertions") if a.get("subject") == pid
                          and a.get("predicate") == "realizes_threat"), None)
        return {
            "name": raw.get("name") or pid, "threat": m.name(p.realizes_threat),
            "steps": steps, "feasibility": FEASIBILITY.get(raw.get("attack_feasibility"), "not rated"),
            "description": raw.get("description", ""), "review": p.review,
            "claim": claim(realizing) if realizing else None,
        }

    def part(oid: str, seen: frozenset) -> dict:
        c = m.get(oid)
        return {"name": m.name(oid), "description": c.get("description", ""),
                "uses": [m.name(u) for u in m.refs(c, "uses_component")],
                "parts": [part(k, seen | {oid}) for k in m.refs(c, "composed_of") if k not in seen]}

    damage_ids = list(dict.fromkeys(
        [d for t in threats if t["id"] in tids for d in m.refs(t, "realizes_damage")]
        + [d for r in scores for d in m.refs(r, "damage_scenario")]))
    reqs = [r for r in m.all("requirements")
            if set(m.refs(r, "addresses")) & set(tids) or set(m.refs(r, "satisfied_by")) & mit_ids
            or r["id"] in {s for x in mits for s in m.refs(x, "stated_as")}]
    req_ids = {r["id"] for r in reqs}
    sources = list(dict.fromkeys(s for r in reqs for slot in ("derived_from", "refines")
                                 for s in m.refs(r, slot) if s not in req_ids))

    impact, risk, treatment = [], [], []
    for r in scores:
        paras = paragraphs(r.get("description"))
        levels = r.get("impact") or {}
        parts = REASON.split(paras.get("15.5", ""))
        why = {}
        for i in range(1, len(parts), 3):
            cat, level = parts[i].lower(), parts[i + 1]
            if levels.get(cat) != level:
                raise SystemExit(f"{r['id']}: its reason rates {cat} {level}, but impact.{cat} is {levels.get(cat)}")
            why[cat] = sentence(parts[i + 2].strip())
        impact.append({"damage": m.name(r.get("damage_scenario")), "for": m.party(r.get("for_stakeholder")),
                       "intro": sentence(parts[0].strip()),
                       "rows": [(c, levels.get(c, "not rated"), why.get(c, "")) for c in CATEGORIES]})
        rm = RISK.match(r.get("risk") or "")
        values = dict(pair.split(" ") for pair in rm["vals"].split(" / ")) if rm else {}
        risk.append({"threat": m.name(r.get("threat")), "feasibility": FEASIBILITY.get(r.get("feasibility"), "not rated"),
                     "values": [(c, levels.get(c, "not rated"), values.get(c, "")) for c in CATEGORIES],
                     "how": (rm["how"] or "") if rm else "", "raw": "" if rm else r.get("risk", ""),
                     "note": paras.get("15.8", "")})
        body = paras.get("15.9", "")
        dm = DECISION.match(body)
        treatment.append({
            "threat": m.name(r.get("threat")), "decision": dm["d"] if dm else "",
            "text": body[dm.end():] if dm else body,
            "status": (r.get("mitigation_status") or "").replace("_", " "),
            "mitigations": [{
                "name": x.get("name") or x["id"], "status": (x.get("mitigation_status") or "no status").replace("_", " "),
                "owner": m.party(x.get("implementation_owner")), "ref": x.get("catalog_ref", ""),
                "phases": [m.name(p) for p in m.refs(x, "applies_in_phase")],
                "requirements": [q.get("name") or q["id"] for q in reqs if x["id"] in m.refs(q, "satisfied_by")
                                 or q["id"] in m.refs(x, "stated_as")],
            } for x in mits if r.get("threat") in m.refs(x, "mitigates")]})

    vulns = [v for v in m.all("vulnerabilities") if entry["item"] in m.refs(v, "affects")]
    chain_ids = {v["id"] for v in vulns}
    chain_ids |= {a.get("object") for a in m.all("assertions")
                  if a.get("subject") in chain_ids and a.get("predicate") == "instance_of"}
    left_paths = [p["id"] for p in m.all("attack_paths") if p.get("realizes_threat") not in tids]
    left_threats = [t for t in threats if t["id"] not in tids]
    left_ids = {t["id"] for t in left_threats} | set(left_paths)

    records = []
    for rid in entry.get("record_ids") or []:
        page = ROOT / "docs" / "library" / "records" / rid / "summary.html"
        if not page.is_file():
            raise SystemExit(f"{MANIFEST.name}: no published record page for {rid} ({page.relative_to(ROOT)})")
        records.append((rid.split("/")[-1], f"library/records/{rid}/summary.html"))

    src_bytes = (ROOT / entry["src"]).read_bytes()
    return {
        "title": entry["title"], "src": entry["src"], "out": entry["out"], "blob": git_blob(src_bytes),
        "item": {
            "name": item.get("name") or entry["item"], "description": item.get("description", ""),
            "made_by": m.party(item.get("manufactured_by")), "owned_by": m.party(item.get("owned_by")),
            "parts": [part(k, frozenset({entry["item"]})) for k in m.refs(item, "composed_of")],
            "units": [(u.get("name") or u["id"], m.name(u.get("current_phase"))) for u in m.all("product_instances")
                      if u.get("of_product") == entry["item"]],
        },
        "assets": [{
            "name": a.get("name") or a["id"], "description": a.get("description", ""),
            "properties": m.refs(a, "security_properties"),
            "where": [m.name(c) for slot in ("processed_by", "stored_in") for c in m.refs(a, slot)],
            "damaged_in": [m.name(d) for d in damage_ids if a["id"] in m.refs(m.get(d), "damages_asset")],
            "targeted_by": [m.name(t) for t in tids if a["id"] in m.refs(m.get(t), "targets_element")],
        } for a in m.all("assets")],
        "damage": [{"name": m.name(d), "description": m.get(d).get("description", ""),
                    "assets": [m.name(a) for a in m.refs(m.get(d), "damages_asset")],
                    "properties": m.refs(m.get(d), "compromised_property")} for d in damage_ids],
        "threats": [{
            "name": m.name(t), "description": m.get(t).get("description", ""),
            "targets": [m.name(x) for x in m.refs(m.get(t), "targets_element")],
            "property": m.get(t).get("violates_property", ""), "method": m.get(t).get("source_method", ""),
            "facets": [str(f).upper() for f in m.refs(m.get(t), "method_facet")
                       if str(f).lower() not in str(m.get(t).get("source_method", "")).lower()],
            "leads_to": [m.name(d) for d in m.refs(m.get(t), "realizes_damage")],
        } for t in tids],
        "impact": impact,
        "paths": [path_view(p["id"]) for p in m.all("attack_paths") if p.get("realizes_threat") in tids],
        "vulns": [{"name": v.get("name") or v["id"], "ref": v.get("catalog_ref", ""),
                   "claims": [claim(a) for a in m.all("assertions") if a.get("subject") in chain_ids]}
                  for v in vulns],
        "risk": risk,
        "treatment": treatment,
        "requirements": [{
            "name": q.get("name") or q["id"], "text": q.get("text", ""), "origin": q.get("text_origin", ""),
            "kind": q.get("requirement_kind", ""), "normativity": q.get("normativity", ""),
            "description": q.get("description", ""),
            "traces": [(label, [m.name(x) for x in m.refs(q, slot)]) for slot, label in (
                ("addresses", "addresses"), ("satisfied_by", "met by"), ("refines", "refines"),
                ("derived_from", "derived from")) if m.refs(q, slot)],
        } for q in reqs],
        "sources": [{"name": m.name(s), "text": m.get(s).get("text", ""), "origin": m.get(s).get("text_origin", ""),
                     "locator": m.get(s).get("source_locator", "")} for s in sources],
        "left_threats": [{"name": m.name(t["id"]), "method": t.get("source_method", ""),
                          "description": t.get("description", "")} for t in left_threats],
        "left_paths": [path_view(p) for p in left_paths],
        "left_claims": [claim(a) for a in m.all("assertions")
                        if a.get("object") in left_ids and a.get("subject") not in left_ids],
        "claims": [claim(a) for a in m.all("assertions")],
        "gaps": entry.get("gaps") or [],
        "records": records,
    }


def tag(text: str, kind: str) -> str:
    return f'<span class="tag {kind}">{esc(text)}</span>'


def review_tag(state) -> str:
    if state.reviewed:
        return tag("accepted by human review", "ok")
    if state.review_status == "rejected":
        return tag("rejected by human review", "no")
    if state.assertion_status == "proposed":
        return tag("proposed, not reviewed", "open")
    return tag("no review recorded", "open")


def claim_tag(c: dict) -> str:
    if c["review"] == "rejected":
        return tag("rejected", "no")
    if c["status"] == "accepted":
        return tag("accepted", "ok")
    return tag(f"{c['status']}, not reviewed" if not c["review"] else c["review"], "open")


def table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f'<th scope="col">{esc(h)}</th>' for h in head)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


def names(items: list[str]) -> str:
    return esc(", ".join(items)) if items else '<span class="muted">none recorded</span>'


def parts_html(parts: list[dict]) -> str:
    if not parts:
        return ""
    lis = "".join(
        f"<li><strong>{esc(p['name'])}</strong>{': ' + esc(p['description']) if p['description'] else ''}"
        f"{' Uses ' + esc(', '.join(p['uses'])) + '.' if p['uses'] else ''}{parts_html(p['parts'])}</li>"
        for p in parts)
    return f'<ul class="parts">{lis}</ul>'


def steps_html(steps: list[dict]) -> str:
    lis = []
    for s in steps:
        need, nums = "", [str(n) for n in s["needs"]]
        plural = "s" if len(nums) > 1 else ""
        if nums and s["gate"] == "AND":
            need = f" {tag('AND', 'gate')} needs step{plural} {esc(' and '.join(nums))}"
        elif nums and s["gate"] == "OR":
            need = f" {tag('OR', 'gate')} needs step{plural} {esc(' or '.join(nums))}"
        elif nums:
            need = f' <span class="muted">after step{plural} {esc(", ".join(nums))}</span>'
        phase = f' <span class="muted">({esc(s["phase"])})</span>' if s["phase"] else ""
        lis.append(f"<li>{esc(s['name'])}{phase}{need}</li>")
    return f'<ol class="steps">{"".join(lis)}</ol>'


def path_html(p: dict) -> str:
    why = ""
    if p["claim"] and p["claim"]["why"]:
        why = f'<p class="muted">Review by {esc(p["claim"]["by"])}: {esc(p["claim"]["why"])}</p>'
    return (f"<h3>{esc(p['name'])}</h3><p>Realizes: <strong>{esc(p['threat'])}</strong>. "
            f"{review_tag(p['review'])}</p>{steps_html(p['steps'])}{why}")


def section(n: int, sid: str, title: str, clause: str, lead: str, inner: str) -> str:
    cl = f' <span class="cl" title="ISO/SAE 21434 clause">{esc(clause)}</span>' if clause else ""
    return f'<section id="{sid}"><h2>{n}. {esc(title)}{cl}</h2><p class="lead">{lead}</p>{inner}</section>'


def render(t: dict) -> str:
    depth = t["out"].count("/") - 1
    up = "../" * depth
    it = t["item"]
    units = "".join(f"<li>{esc(n)}: lifecycle phase <em>{esc(ph)}</em></li>" for n, ph in it["units"])
    s = {}
    s["item"] = (
        f"<p><strong>{esc(it['name'])}</strong>: {esc(it['description'])}</p>"
        f"<p>Made by {esc(it['made_by'] or 'not recorded')}; owned by {esc(it['owned_by'] or 'not recorded')}.</p>"
        f"<p>Its parts:</p>{parts_html(it['parts'])}"
        + (f"<p>Fielded units:</p><ul>{units}</ul>" if units else ""))
    s["assets"] = table(
        ["Asset", "Properties to protect", "Where it lives", "Damage if lost"],
        [[f"<strong>{esc(a['name'])}</strong><br><span class=\"muted\">{esc(a['description'])}</span>",
          names(a["properties"]), names(a["where"]), names(a["damaged_in"])] for a in t["assets"]]
    ) + table(
        ["Damage scenario", "What happens", "Asset damaged", "Property lost"],
        [[f"<strong>{esc(d['name'])}</strong>", esc(d["description"]), names(d["assets"]), names(d["properties"])]
         for d in t["damage"]])
    s["threats"] = table(
        ["Threat scenario", "Targets", "Property broken", "How it was found", "Leads to"],
        [[f"<strong>{esc(x['name'])}</strong><br><span class=\"muted\">{esc(x['description'])}</span>",
          names(x["targets"]), esc(x["property"]) or names([]),
          esc(x["method"]) + (f" ({esc(', '.join(x['facets']))})" if x["facets"] else ""), names(x["leads_to"])]
         for x in t["threats"]]) + "<p>Each threat here is reviewed: every attack path for it has an accepted review.</p>"
    s["impact"] = "".join(
        f"<h3>{esc(i['damage'])}</h3><p>{esc(i['intro'])} Reported for: {esc(i['for'])}.</p>"
        + table(["Category", "Rating", "Reason"],
                [[esc(c.capitalize()), f"<strong>{esc(lv)}</strong>",
                  esc(why) if why else tag("no reason recorded", "open")] for c, lv, why in i["rows"]])
        for i in t["impact"])
    vulns = "".join(
        f"<p>Known vulnerability on this item: <strong>{esc(v['ref'])}</strong>, {esc(v['name'])}.</p><ul>"
        + "".join(f"<li>{esc(c['text'])} {claim_tag(c)}</li>" for c in v["claims"]) + "</ul>" for v in t["vulns"])
    s["paths"] = "".join(path_html(p) for p in t["paths"]) + vulns
    s["feasibility"] = table(
        ["Attack path", "Rating", "Method and reason"],
        [[f"<strong>{esc(p['name'])}</strong>", f"<strong>{esc(p['feasibility'])}</strong>", esc(p["description"])]
         for p in t["paths"]])
    s["risk"] = "".join(
        f"<h3>{esc(r['threat'])}</h3>"
        + table(["Category", "Impact", "Feasibility", "Risk value (1 to 5)"],
                [[esc(c.capitalize()), esc(lv), esc(r["feasibility"]),
                  f'<span class="n">{esc(v)}</span>' if v else tag("not recorded", "open")]
                 for c, lv, v in r["values"]])
        + (f"<p>Risk values: {esc(r['note'])}</p>" if r["note"]
           else f"<p class=\"muted\">As recorded: {esc(r['how'])}.</p>" if r["how"] else "")
        + (f"<p class=\"muted\">Recorded as text: {esc(r['raw'])}</p>" if r["raw"] else "")
        for r in t["risk"])
    s["treatment"] = "".join(
        f"<h3>{esc(x['threat'])}</h3><p>Decision: "
        + (f"<strong>{esc(x['decision'])}</strong>{esc(x['text'])}" if x["decision"]
           else tag("no decision recorded", "open") + (f" {esc(x['text'])}" if x["text"] else ""))
        + f"</p><p>Mitigation status: {esc(x['status'] or 'not recorded')}.</p>"
        + table(["Mitigation", "Status", "Owner", "Lifecycle phases", "Stated as requirement"],
                [[f"<strong>{esc(mi['name'])}</strong>" + (f"<br><span class=\"muted\">{esc(mi['ref'])}</span>" if mi["ref"] else ""),
                  tag(mi["status"], "ok" if mi["status"] == "complete" else "open"), esc(mi["owner"]),
                  names(mi["phases"]), names(mi["requirements"])] for mi in x["mitigations"]])
        for x in t["treatment"])
    s["requirements"] = table(
        ["Requirement", "Text", "Traces"],
        [[f"<strong>{esc(q['name'])}</strong><br><span class=\"muted\">{esc(q['kind'])}, {esc(q['normativity'])}, "
          f"{esc(q['origin'])} text</span>", esc(q["text"]),
          "<br>".join(f"{esc(label)}: {esc(', '.join(v))}" for label, v in q["traces"])] for q in t["requirements"]]
    ) + ("<p>Where they come from:</p><ul>" + "".join(
        f"<li><strong>{esc(src['name'])}</strong>. {esc(src['text'])} <span class=\"muted\">Source: "
        f"{esc(src['locator'])}, {esc(src['origin'])}.</span></li>"
        for src in t["sources"]) + "</ul>" if t["sources"] else "")
    s["left-out"] = "<p>None: every threat in the model is reviewed.</p>" if not (
        t["left_threats"] or t["left_paths"]) else '<div class="aside">' + "".join(
        f"<h3>{esc(x['name'])}</h3><p>{tag('not reviewed', 'open')} Proposed by <code>{esc(x['method'])}</code>. "
        f"{esc(x['description'])}</p>" for x in t["left_threats"]) + "".join(
        path_html(p) + f"<p class=\"muted\">Feasibility as proposed: {esc(p['feasibility'])}.</p>"
        for p in t["left_paths"]) + ("<p>Other links to it:</p><ul>" + "".join(
            f"<li>{esc(c['name'])} {claim_tag(c)}</li>" for c in t["left_claims"]) + "</ul>"
                                     if t["left_claims"] else "") + "</div>"
    s["reviews"] = table(
        ["Claim", "Status", "Reason"],
        [[esc(c["name"]), claim_tag(c), esc(c["why"]) or '<span class="muted">no review recorded</span>']
         for c in t["claims"]])
    s["gaps"] = "<ul>" + "".join(
        f'<li><span class="cl">{esc(g.get("clause", ""))}</span> {esc(g.get("text", ""))}</li>' for g in t["gaps"]) + "</ul>"
    leads = {
        "item": "What the analysis covers. The standard starts a TARA from the item definition: the item's "
                "functions, its boundary and its operational environment.",
        "assets": "What is worth protecting, and the harm that follows if it is not. Each asset lists the "
                  "cybersecurity properties to protect; a damage scenario is what happens when one is lost.",
        "threats": "How the damage could come about. Each threat scenario names the asset it targets, the "
                   "property it breaks and what causes it (RQ-15-03).",
        "impact": "How bad the damage would be for the road users harmed, in four categories, each rated "
                  "severe, major, moderate or negligible (RQ-15-04, RQ-15-05). Safety ratings follow the "
                  "ISO 26262-3 severity classes (RQ-15-06).",
        "paths": "The steps an attacker would take (RQ-15-08). An AND step needs all the steps it lists; an "
                 "OR step needs any one of them.",
        "feasibility": "How easy each attack path is: High, Medium, Low or Very low (RQ-15-10). The model "
                       "says which of the standard's rating approaches it used.",
        "risk": "A risk value from 1 (minimal) to 5, from the impact and the feasibility (RQ-15-15, "
                "RQ-15-16). The values are as the model records them; this page computes nothing.",
        "treatment": "What to do about each risk: avoid, reduce, share or retain it (RQ-15-17), and the "
                     "mitigations that carry the decision out.",
        "requirements": "The requirements the analysis led to: those that address a threat above, and those "
                        "its mitigations meet. Paraphrase text restates the standard in our own words.",
        "left-out": "Threats and attack paths that no human has accepted, such as AI-proposed hypotheses and "
                    "paths a reviewer rejected, are not part of the TARA. They stay in the model, labelled, as "
                    "a record of what was proposed and why it was turned down.",
        "reviews": "Every claim in the model that needs a human decision, with its status. AI output stays a "
                   "hypothesis until a human accepts it. These reviews are example data too.",
        "gaps": "What a complete TARA has that this draft does not have yet.",
    }
    body = "".join(section(n, sid, title, cl, esc(leads[sid]), s[sid])
                   for n, (sid, title, cl) in enumerate(SECTIONS, 1))
    toc = "".join(f'<li><a href="#{sid}">{esc(title)}</a></li>' for sid, title, _ in SECTIONS)
    records = ", ".join(f'<a href="{esc(up + href)}">{esc(rid)}</a>' for rid, href in t["records"]) or "none"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(t['title'])}</title><style>{CSS}</style></head><body>
{site_nav.header(depth, "reports/index.html")}
<div class="banner" role="note"><strong>Example data, not an assessment of a real product.</strong> This is draft v0
of a TARA built from an example model. Nothing on it has been approved as a TARA, and the reviews it shows are
example data too.</div>
<h1>{esc(t['title'])}</h1>
<div class="rev"><strong>Draft v0</strong> · model <code>{esc(t['src'])}</code>, git blob <code>{esc(t['blob'][:12])}</code>
· static page (regenerated when the model changes)</div>
<p class="rl"><a href="{esc(REPO + t['src'])}">The model (YAML)</a><a href="{esc(REPO)}research/0007-iso21434-tara/report.md">How the
standard's TARA works (RPT-0007)</a></p>
<p>A TARA (threat analysis and risk assessment) is how ISO/SAE 21434 has a vehicle maker work out what could go
wrong with a part of a vehicle, how harmful and how likely that is, and what to do about it (clause 15). This page
lays one example model out in the order of clause 15's work products. The standard is licensed, so the page
describes it in our own words and cites clause, provision and table numbers only. Library records cited: {records}.</p>
<ol class="toc">{toc}</ol>
{body}
<footer>Generated from <code>{esc(t['src'])}</code> by <code>render_tara.py</code> (listed in
<code>docs/publishing/tara.yaml</code>). Do not hand-edit. People in the model appear as roles; no personal
identities are published (enforced by <code>check_identities.py</code>).</footer>
</body></html>
"""


def main(argv: list[str]) -> int:
    check = "--check" in argv
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("taras") or []
    reports = yaml.safe_load(REPORTS.read_text(encoding="utf-8"))
    listed = {e.get("page"): e.get("title") for e in reports.get("listed") or [] if isinstance(e, dict)}
    print(f"render_tara: {len(entries)} TARA page(s){' (check only)' if check else ''}")
    stale = []
    for entry in entries:
        if listed.get(entry["out"]) != entry["title"]:
            raise SystemExit(f"render_tara: list {entry['out']} under `listed:` in {REPORTS.relative_to(ROOT)} "
                             f"with the title {entry['title']!r}, so the reports index links to it")
        try:
            doc = dict(load_vector_document(ROOT / entry["src"]))
        except GraphError as exc:
            raise SystemExit(f"render_tara: {exc}") from exc
        page = render(collect(doc, entry))
        out = ROOT / entry["out"]
        if check:
            if not out.is_file() or out.read_text(encoding="utf-8") != page:
                stale.append(entry["out"])
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"  {entry['out']}  (from {entry['src']})")
    for path in stale:
        print(f"  out of date: {path} (run docs/publishing/render_tara.py and commit the result)")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
