#!/usr/bin/env python3
"""Render archdoc markdown reports to static, versioned HTML.

Reads docs/publishing/reports.yaml. For each report: parse front matter (the
`version` becomes the page REVISION; `updated` the date), render a Markdown
SUBSET of the body to HTML, wrap in a self-contained styled page. Deterministic,
stdlib only, no network, no remote scripts. Front-matter person fields are never
emitted; check_identities.py is the backstop. The page is static — regenerate
only when the source changes.

    python3 docs/publishing/render_report.py
"""
from __future__ import annotations
import html, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "publishing" / "reports.yaml"


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm, body = {}, m.group(1)
    for line in body.splitlines():
        mm = re.match(r'^([a-z_]+):\s*"?(.*?)"?\s*$', line)
        if mm:
            fm[mm.group(1)] = mm.group(2)
    return fm, m.group(2)


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(md: str) -> str:
    out, i, lines = [], 0, md.splitlines()
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("```"):
            i += 1; buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1; out.append("<pre><code>" + "\n".join(buf) + "</code></pre>"); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if re.match(r"^(---+|\*\*\*+)\s*$", ln):
            out.append("<hr>"); i += 1; continue
        if ln.lstrip().startswith(">"):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(inline(lines[i].lstrip()[1:].strip())); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i+1]):
            def cells(r): return [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln); i += 2; rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i])); i += 1
            t = ["<table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in head] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>"); out.append("".join(t)); continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln)); tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{it}</li>" for it in items) + f"</{tag}>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|>|\s*([-*]|\d+\.)\s|\s*\|)", lines[i]) and not re.match(r"^(---+|\*\*\*+)\s*$", lines[i]):
            buf.append(inline(lines[i])); i += 1
        if buf:
            out.append("<p>" + "<br>".join(buf) + "</p>")
    return "\n".join(out)


CSS = """body{max-width:52rem;margin:2rem auto;padding:0 1rem;font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a}
h1,h2,h3,h4{line-height:1.25} h1{border-bottom:2px solid #eee;padding-bottom:.3rem}
code{background:#f4f4f4;padding:.1em .3em;border-radius:3px;font-size:.9em}
pre{background:#f4f4f4;padding:1rem;overflow:auto;border-radius:6px}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95em} th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}
th{background:#fafafa} blockquote{border-left:4px solid #ddd;margin:1rem 0;padding:.2rem 1rem;color:#555}
.rev{font-size:.85em;color:#666;background:#fafafa;border:1px solid #eee;border-radius:6px;padding:.5rem .8rem;margin:1rem 0}
.rl a{margin-right:1rem} footer{margin-top:3rem;border-top:1px solid #eee;padding-top:1rem;font-size:.85em;color:#777}"""


def render(rep: dict) -> None:
    src = ROOT / rep["src"]
    fm, body = front_matter(src.read_text())
    title = rep.get("title") or fm.get("title") or fm.get("short_title") or src.stem
    rev = fm.get("version", "—"); updated = fm.get("updated", "—")
    links = "".join(f'<a href="{html.escape(l["href"])}">{html.escape(l["text"])}</a>' for l in rep.get("links", []))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<h1>{html.escape(title)}</h1>
<div class="rev"><strong>Revision {html.escape(rev)}</strong> · updated {html.escape(updated)} · static page (regenerated only when the source changes)</div>
{f'<p class="rl">{links}</p>' if links else ''}
{md_to_html(body)}
<footer>Generated from <code>{html.escape(rep['src'])}</code> by <code>render_report.py</code>. No personal identities are published (enforced by <code>check_identities.py</code>).</footer>
</body></html>"""
    out = ROOT / rep["out"]; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page)
    print(f"  {rep['out']}  (revision {rev})")


def main() -> int:
    txt = MANIFEST.read_text()
    reps, cur = [], None
    for line in txt.splitlines():
        m = re.match(r"^\s*-\s+src:\s*(\S+)", line)
        if m:
            cur = {"src": m.group(1), "links": []}; reps.append(cur); continue
        if cur is not None:
            mo = re.match(r'^\s+out:\s*(\S+)', line); mt = re.match(r'^\s+title:\s*"?(.+?)"?\s*$', line)
            ml = re.match(r'^\s+-\s+\{\s*text:\s*"?(.+?)"?,\s*href:\s*"?(.+?)"?\s*\}', line)
            if mo: cur["out"] = mo.group(1)
            elif mt and "title" not in cur: cur["title"] = mt.group(1)
            elif ml: cur["links"].append({"text": ml.group(1), "href": ml.group(2)})
    print(f"render_report: {len(reps)} report page(s)")
    for r in reps:
        render(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
