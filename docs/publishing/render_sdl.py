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



sys.path.insert(0, str(ROOT / "engine"))
from engine.sdl import (  # noqa: E402,F401  (one SDL view for the page and the app, DL-0043)
    DECIDER_ROLES,
    SELECTION_PREDICATES,
    STATUS,
    SdlError,
)
from engine import sdl as _sdl  # noqa: E402


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def link_for(loc: str, depth: int) -> str:
    """URL for a work-product locator or a library ref, relative where the site has it."""
    if loc.startswith("library:"):
        rec = loc[len("library:"):].split("#", 1)[0]
        hits = list((ROOT / "docs" / "library" / "records").glob(f"*/{rec}/summary.html"))
        if hits:
            return "../" * depth + str(hits[0].relative_to(ROOT / "docs"))
    return _sdl.default_link(loc)


def collect(doc: dict, entry: dict, xwalk: dict) -> dict:
    """engine.sdl.collect() for one manifest entry, with the page's relative links."""
    depth = entry["out"].count("/") - 1
    data = _sdl.collect(
        doc, xwalk, program=entry["program"], columns=entry.get("map_columns"),
        decider_roles=entry.get("required_reviewer_roles", DECIDER_ROLES),
        link=lambda loc: link_for(loc, depth),
    )
    return dict(data, title=entry["title"], src=entry["src"], depth=depth)


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
