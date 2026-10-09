#!/usr/bin/env python3
"""Render the WAVE 1 bibliography subset to static HTML.

Reads docs/publishing/bibliography.yaml and library records. Does not write
back into the library. Stdlib only. Re-running with the same inputs is
deterministic: no timestamps, no network.

See docs/publishing/bibliography-review.md for the categorization rules this
script enforces.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "publishing" / "bibliography.yaml"
OUT_DIR = ROOT / "docs" / "bibliography"
RECORDS_ROOT = ROOT / "library" / "records"
TAGS_PATH = ROOT / "library" / "schema" / "tags.yaml"

SCHEMA_BODIES = {
    "ietf", "nist", "w3c", "iso", "oasis", "c2pa", "openssf", "google",
    "academic", "vendor", "community", "regulator", "other",
}
STANDING = {
    "standard", "best-practice", "informational", "experimental", "historic",
    "draft", "recommendation", "white-paper", "implementation", "unofficial",
}
AXES = ("security", "cryptography", "this_project")
AXIS_LABEL = {
    "security": "Security",
    "cryptography": "Cryptography",
    "this_project": "This project",
}
TYPE_HEADING = {
    "rfc": "RFC",
    "draft": "Internet-Draft",
    "spec": "Specification",
    "paper": "Paper",
    "book": "Book",
    "article": "Article",
    "dataset": "Dataset",
    "repo": "Repository",
    "web": "Web page",
    "consortium": "Consortium",
    "note": "Note",
    "hierarchy": "Hierarchy",
    "spreadsheet": "Spreadsheet",
}
BOILERPLATE_MARK = "_Two to five sentences"


# --- YAML subset -----------------------------------------------------------

def _strip_comment(s: str) -> str:
    out = []
    q = None
    i = 0
    while i < len(s):
        c = s[i]
        if q:
            out.append(c)
            if c == "\\" and q == '"':
                if i + 1 < len(s):
                    i += 1
                    out.append(s[i])
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
            out.append(c)
        elif c == "#":
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _unquote(s: str):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        body = s[1:-1]
        if s[0] == "'":
            return body.replace("''", "'")
        return (
            body.replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )
    return s


def _split_flow(inner: str) -> list[str]:
    items = []
    buf: list[str] = []
    depth = 0
    q = None
    i = 0
    while i < len(inner):
        c = inner[i]
        if q:
            buf.append(c)
            if c == "\\" and q == '"':
                if i + 1 < len(inner):
                    i += 1
                    buf.append(inner[i])
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
            buf.append(c)
        elif c in "[{":
            depth += 1
            buf.append(c)
        elif c in "]}":
            depth -= 1
            buf.append(c)
        elif c == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        else:
            buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        items.append(tail)
    return [x for x in items if x != ""]


def _parse_flow_map(s: str) -> dict:
    inner = s.strip()[1:-1]
    out = {}
    for piece in _split_flow(inner):
        key, sep, val = piece.partition(":")
        if not sep:
            raise ValueError(f"bad flow map entry: {piece}")
        out[key.strip()] = _scalar(val.strip())
    return out


def _scalar(s: str):
    s = s.strip()
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if s == "[]":
        return []
    if s == "{}":
        return {}
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return _unquote(s)
    if s.startswith("[") and s.endswith("]"):
        return [_scalar(x) for x in _split_flow(s[1:-1])]
    if s.startswith("{") and s.endswith("}"):
        return _parse_flow_map(s)
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


_MAP_ITEM = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")


def _is_map_item(rest: str) -> bool:
    if not rest or rest[0] in "\"'[{":
        return False
    if re.match(r"^[a-z][a-z0-9+.-]*://", rest):
        return False
    return bool(_MAP_ITEM.match(rest))


class YamlParser:
    def __init__(self, text: str, name: str = ""):
        self.lines = text.splitlines()
        self.n = len(self.lines)
        self.i = 0
        self.name = name

    def parse(self):
        self._skip()
        if self.i < self.n and self.lines[self.i].strip() == "---":
            self.i += 1
        if self.peek() is None:
            return {}
        return self.parse_map(0)

    def _skip(self):
        while self.i < self.n:
            line = self.lines[self.i]
            if not line.strip() or line.lstrip().startswith("#"):
                self.i += 1
                continue
            return

    def peek(self):
        self._skip()
        if self.i >= self.n:
            return None
        return self.lines[self.i]

    def _indent(self, line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def _err(self, msg: str):
        raise ValueError(f"{self.name}:{self.i + 1}: {msg}")

    def parse_map(self, indent: int) -> dict:
        out: dict = {}
        while True:
            line = self.peek()
            if line is None:
                break
            if line.strip() == "---":
                break
            ind = self._indent(line)
            if ind < indent:
                break
            if ind > indent:
                self._err(f"unexpected indent {ind}, wanted {indent}")
            content = _strip_comment(line).strip()
            if content.startswith("- "):
                break
            if ":" not in content:
                self._err(f"expected key: {content}")
            key, _, rest = content.partition(":")
            key = key.strip()
            rest = rest.strip()
            self.i += 1
            if rest in ("|", ">", "|-", ">-", "|+", ">+"):
                out[key] = self._block_scalar(ind, rest)
            elif rest == "":
                out[key] = self._nested(ind)
            else:
                out[key] = _scalar(rest)
        return out

    def _nested(self, key_indent: int):
        nxt = self.peek()
        if nxt is None:
            return None
        if nxt.strip() == "---":
            return None
        ind = self._indent(nxt)
        if ind <= key_indent:
            return None
        content = _strip_comment(nxt).strip()
        if content.startswith("- "):
            return self.parse_list(ind)
        if content[:1] in "[{":
            # flow collection on its own line under the key (`bears_on:\n  []`)
            self.i += 1
            return _scalar(content)
        return self.parse_map(ind)

    def parse_list(self, indent: int) -> list:
        items = []
        while True:
            line = self.peek()
            if line is None:
                break
            if line.strip() == "---":
                break
            ind = self._indent(line)
            if ind < indent:
                break
            content = _strip_comment(line).strip()
            if ind != indent or not content.startswith("- "):
                break
            rest = content[2:].strip()
            self.i += 1
            if rest == "":
                items.append(self._nested(ind))
            elif _is_map_item(rest):
                key, _, val = rest.partition(":")
                item = {key.strip(): _scalar(val.strip()) if val.strip() else self._nested(ind)}
                self._map_into(item, ind + 1)
                items.append(item)
            else:
                items.append(_scalar(rest))
        return items

    def _map_into(self, item: dict, min_indent: int):
        while True:
            line = self.peek()
            if line is None:
                break
            if line.strip() == "---":
                break
            ind = self._indent(line)
            if ind < min_indent:
                break
            content = _strip_comment(line).strip()
            if content.startswith("- ") or ":" not in content:
                break
            key, _, rest = content.partition(":")
            key = key.strip()
            rest = rest.strip()
            self.i += 1
            if rest in ("|", ">", "|-", ">-", "|+", ">+"):
                item[key] = self._block_scalar(ind, rest)
            elif rest == "":
                item[key] = self._nested(ind)
            else:
                item[key] = _scalar(rest)

    def _block_scalar(self, key_indent: int, style: str) -> str:
        raw_lines = []
        while self.i < self.n:
            line = self.lines[self.i]
            if line.strip() and (len(line) - len(line.lstrip(" "))) <= key_indent:
                break
            raw_lines.append(line)
            self.i += 1
        kept = []
        for line in raw_lines:
            if line.strip() == "":
                kept.append("")
            else:
                kept.append(line)
        if not any(x.strip() for x in kept):
            return ""
        mind = min(len(x) - len(x.lstrip(" ")) for x in kept if x.strip())
        body = [("" if not x.strip() else x[mind:]) for x in kept]
        while body and body[-1] == "":
            body.pop()
        if style.startswith(">"):
            paras = []
            cur: list[str] = []
            for line in body:
                if line == "":
                    if cur:
                        paras.append(" ".join(cur))
                        cur = []
                else:
                    cur.append(line)
            if cur:
                paras.append(" ".join(cur))
            return "\n".join(paras)
        return "\n".join(body)


def load_yaml(path: Path):
    return YamlParser(path.read_text(encoding="utf-8"), str(path)).parse()


def load_front_matter(text: str, name: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError(f"{name}: unclosed front matter")
    fm = YamlParser(text[: end + 4], name).parse()
    body = text[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    return fm, body


# --- records ---------------------------------------------------------------

def find_record(record_id: str) -> Path:
    matches = [p for p in RECORDS_ROOT.glob(f"*/{record_id}/record.yaml")]
    if len(matches) != 1:
        raise SystemExit(f"{record_id}: expected one record.yaml, found {len(matches)}")
    return matches[0]


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def tag_groups(tags: list[str], role: set[str], body: set[str]) -> dict[str, list[str]]:
    groups = {"topic": [], "body": [], "role": [], "standing": []}
    for tag in tags:
        if tag in role:
            groups["role"].append(tag)
        elif tag in body or tag in SCHEMA_BODIES:
            groups["body"].append(tag)
        elif tag in STANDING:
            groups["standing"].append(tag)
        else:
            groups["topic"].append(tag)
    return groups


def load_controlled_tags() -> tuple[set[str], set[str]]:
    data = load_yaml(TAGS_PATH)
    role = set(as_list(data.get("role")))
    body = set(as_list(data.get("body"))) | SCHEMA_BODIES
    return role, body


def str_id(value) -> str:
    if isinstance(value, dict):
        return ""
    return str(value).strip()


# --- markdown --------------------------------------------------------------

def _inline(s: str) -> str:
    s = html.escape(s, quote=True)
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", s)

    def link(m):
        text, url = m.group(1), html.unescape(m.group(2).strip())
        if url.startswith(("http://", "https://")):
            return f'<a href="{html.escape(url, quote=True)}">{text}</a>'
        return text

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    # Drop a single leading H1; the page title already says it.
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        i += 1
    lines = lines[i:]
    html_parts: list[str] = []
    para: list[str] = []
    lst: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            html_parts.append("<p>" + _inline(" ".join(para)) + "</p>")
            para = []

    def flush_list():
        nonlocal lst
        if lst:
            html_parts.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in lst) + "</ul>")
            lst = []

    j = 0
    while j < len(lines):
        line = lines[j]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_para()
            flush_list()
            j += 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(html.escape(lines[j]))
                j += 1
            if j < len(lines):
                j += 1
            html_parts.append("<pre>" + "\n".join(buf) + "</pre>")
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_para()
            flush_list()
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append(cells)
                j += 1
            data = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c or "") for c in r)]
            if data:
                head, *rest = data
                thead = "".join(f"<th>{_inline(c)}</th>" for c in head)
                body = ""
                for r in rest:
                    body += "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
                html_parts.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>")
            continue
        if stripped.startswith("##"):
            flush_para()
            flush_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(max(level, 2), 4)
            text = stripped[level:].strip()
            html_parts.append(f"<h{level}>{_inline(text)}</h{level}>")
            j += 1
            continue
        if lst and (line.startswith(" ") or line.startswith("\t")) and stripped and not re.match(r"^[-*] ", stripped) and not stripped.startswith("|") and not stripped.startswith("#"):
            lst[-1] = lst[-1] + " " + stripped
            j += 1
            continue
        if re.match(r"^[-*] ", stripped):
            flush_para()
            lst.append(stripped[2:].strip())
            j += 1
            continue
        if stripped == "":
            flush_para()
            flush_list()
            j += 1
            continue
        flush_list()
        para.append(stripped)
        j += 1
    flush_para()
    flush_list()
    return "\n".join(html_parts)


# --- html chrome -----------------------------------------------------------

CSS = """
:root {
  --ink: #1a1916;
  --muted: #5c574e;
  --line: #e2dcd0;
  --paper: #f6f3ec;
  --card: #fffcf7;
  --accent: #1e4d3a;
  --warn: #6b4e16;
  --warn-bg: #f3ead3;
  --bad-bg: #f6e4dc;
  --ok-bg: #e5efe8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 17px;
  line-height: 1.55;
}
a { color: var(--accent); }
a:hover { text-decoration: none; }
.wrap { max-width: 920px; margin: 0 auto; padding: 0 24px 64px; }
header { border-bottom: 1px solid var(--line); background: var(--card); }
.bar {
  max-width: 920px; margin: 0 auto; padding: 16px 24px;
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 12px 18px;
}
.mark { font-weight: 650; letter-spacing: -0.03em; color: var(--ink); text-decoration: none; }
nav { display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.92rem; }
nav a { color: var(--muted); text-decoration: none; }
nav a[aria-current="page"] { color: var(--ink); font-weight: 650; }
h1 { font-size: clamp(1.8rem, 3vw, 2.4rem); line-height: 1.15; letter-spacing: -0.03em; margin: 28px 0 8px; }
h2 { font-size: 1.25rem; margin: 1.6em 0 0.4em; }
h3 { font-size: 1.05rem; margin: 1.2em 0 0.3em; }
.kicker { margin: 22px 0 0; font-size: 0.78rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); font-weight: 650; }
.lede { color: var(--muted); margin-top: 0; }
.banner, .callout {
  background: var(--warn-bg); color: var(--warn); border-radius: 8px; padding: 12px 14px; margin: 16px 0;
}
.callout.quiet { background: var(--card); color: var(--ink); border: 1px solid var(--line); }
.callout strong { color: var(--ink); }
ul.clean { padding-left: 1.2rem; }
table { width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; background: var(--card); }
th, td { text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); padding: 8px 10px; font-size: 0.95rem; }
th { font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); }
code { font-size: 0.9em; }
.badge {
  display: inline-block; padding: 1px 8px; border-radius: 999px; background: var(--card);
  border: 1px solid var(--line); font-size: 0.82rem; margin: 0 4px 4px 0;
}
.badge.core { background: var(--ok-bg); }
.badge.none, .badge.not-assessed { background: var(--bad-bg); }
.badge.broad { background: var(--warn-bg); }
.meta { color: var(--muted); font-size: 0.92rem; }
footer { margin-top: 48px; color: var(--muted); font-size: 0.85rem; border-top: 1px solid var(--line); padding-top: 16px; }
.cardlink { display: block; padding: 12px 0; border-bottom: 1px solid var(--line); text-decoration: none; color: inherit; }
.cardlink:hover { background: transparent; }
.cardlink strong { color: var(--accent); }
ol.refs { list-style: none; padding: 0; margin: 0; }
ol.refs li { padding: 8px 0 8px 1.6em; text-indent: -1.6em; border-bottom: 1px solid var(--line); overflow-wrap: anywhere; }
ol.refs cite { font-style: italic; }
nav.jump { display: flex; flex-wrap: wrap; gap: 4px 10px; margin: 18px 0 0; font-weight: 600; }
"""


def esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def page(title: str, body: str, current: str, depth: int) -> str:
    # depth 0: docs/bibliography/*.html
    # depth 1: docs/bibliography/records/*.html
    # Landing page is docs/index.html, one level above the bibliography.
    home = "../" * (depth + 1) + "index.html"

    def href(name: str) -> str:
        if depth == 0:
            return name
        return f"../{name}"

    items = [
        ("index.html", "Index"),
        ("by-topic.html", "Topic"),
        ("by-type.html", "Type"),
        ("by-body.html", "Issuing body"),
        ("crosswalk.html", "Crosswalk"),
    ]
    nav = [f'<a class="mark" href="{esc(href("index.html"))}">Bibliography</a><nav>']
    nav.append(f'<a href="{esc(home)}">tmodel</a>')
    for name, label in items:
        cur = ' aria-current="page"' if name == current else ""
        nav.append(f'<a href="{esc(href(name))}"{cur}>{label}</a>')
    nav.append("</nav>")
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="referrer" content="no-referrer">\n'
        f"<title>{esc(title)}</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        f"<header><div class=\"bar\">{''.join(nav)}</div></header>\n"
        f"<main class=\"wrap\">\n{body}\n"
        "<footer><p>Generated from <code>docs/publishing/bibliography.yaml</code> "
        "by <code>docs/publishing/render_bibliography.py</code>. Do not hand-edit. "
        "Static HTML, no scripts, no trackers. See "
        f"<a href=\"{esc(href('../publishing/bibliography-review.md') if depth else '../publishing/bibliography-review.md')}\">bibliography-review.md</a>."
        "</p></footer>\n</main>\n</body>\n</html>\n"
    )


def link_record(record_id: str, published: dict[str, dict]) -> str:
    rec = published.get(record_id)
    label = esc(rec["short"] if rec else record_id)
    ident = esc(record_id)
    if rec:
        return f'<a href="records/{ident}.html">{label}</a> <span class="meta">({ident})</span>'
    return f"{label} <span class=\"meta\">({ident}, not in this subset)</span>"


def link_record_rel(record_id: str, published: dict[str, dict], here: str) -> str:
    """Link used on a record page (one directory down)."""
    rec = published.get(record_id)
    label = esc(rec["short"] if rec else record_id)
    ident = esc(record_id)
    if record_id == here:
        return f"{label} <span class=\"meta\">(this page)</span>"
    if rec:
        return f'<a href="{ident}.html">{label}</a>'
    return f"<code>{ident}</code> <span class=\"meta\">not in this subset</span>"


# --- record pages ----------------------------------------------------------

def applicability_table(app: dict | None) -> str:
    app = app or {}
    rows = []
    keys = list(AXES) + sorted(k for k in app.keys() if k not in AXES)
    for key in keys:
        if key in app and app[key] not in (None, ""):
            rating = str(app[key])
            shown = rating
        else:
            rating = "not-assessed"
            shown = "not assessed"
        label = AXIS_LABEL.get(key, key)
        rows.append(
            f"<tr><td>{esc(label)}</td><td><span class=\"badge {esc(rating)}\">{esc(shown)}</span></td></tr>"
        )
    note = (
        "<p class=\"meta\">Ratings are the <code>applicability</code> map on "
        "<code>record.yaml</code>. A missing axis is not assessed — it is not "
        "<code>none</code>. The summary's Why column is not scraped; two summary "
        "dialects exist, and a blank template cell is not a judgement.</p>"
    )
    return (
        "<table><thead><tr><th>Axis</th><th>Rating</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
        + note
    )


def tag_html(groups: dict[str, list[str]]) -> str:
    labels = [
        ("topic", "Topic tags", "Subject vocabulary and free tags. These are what the topic view and the tag crosswalk use."),
        ("body", "Body tags", "Issuing-body names. Shown here, excluded from the topic view so it is not a second copy of the body index."),
        ("role", "Role tags", "Why the record was kept (normative, prior-art, evidence, …). Not a subject."),
        ("standing", "Standing tags", "Maturity words such as standard or draft. Not a shared subject."),
    ]
    parts = []
    any_tags = False
    for key, title, why in labels:
        tags = groups[key]
        if not tags:
            continue
        any_tags = True
        badges = " ".join(f'<span class="badge">{esc(t)}</span>' for t in tags)
        parts.append(f"<h3>{title}</h3><p>{badges}</p><p class=\"meta\">{why}</p>")
    if not any_tags:
        return "<p class=\"meta\">No tags recorded.</p>"
    return "".join(parts)


def type_section(rec: dict, published: dict[str, dict]) -> str:
    typ = rec["type"]
    heading = TYPE_HEADING.get(typ, typ)
    bits = [f"<h2>{esc(heading)}</h2>"]
    ident = rec["identifiers"]
    if typ == "draft":
        bits.append(
            "<div class=\"callout\"><strong>Not a standard.</strong> "
            "An Internet-Draft is not an RFC. Maturity below is the record's "
            "own field, not a ratification this page inferred.</div>"
        )
    elif typ == "dataset":
        bits.append(
            "<div class=\"callout\"><strong>Catalog, not one row.</strong> "
            "This record is the enumeration itself. Retrieved is when the library "
            "looked, not an edition date. Empty authors are omitted, not missing paper metadata.</div>"
        )
    elif typ == "web":
        bits.append(
            "<div class=\"callout\"><strong>Not an edition.</strong> "
            "A web page can change under the same URL. Retrieved is the look-up date.</div>"
        )
    elif typ == "repo":
        bits.append(
            "<div class=\"callout\"><strong>Implementation, not a ratified text.</strong> "
            "The primary link is the repository URL.</div>"
        )
    elif typ == "paper":
        bits.append(
            "<p class=\"meta\">Authors and date are whatever the record states. "
            "This page does not add a venue.</p>"
        )
    elif typ == "rfc":
        bits.append("<p class=\"meta\">RFC number and DOI are identifiers on the record. Maturity is the record's field.</p>")

    rows = []
    if typ in ("rfc", "paper", "spec", "book", "article", "draft") and rec["authors"]:
        rows.append(("Authors", ", ".join(rec["authors"])))
    if rec["date"] and typ in ("rfc", "paper", "spec", "book", "article", "draft"):
        rows.append(("Date", rec["date"]))
    if typ == "dataset" or typ == "web":
        if rec["retrieved"]:
            rows.append(("Retrieved", rec["retrieved"]))
    if typ == "repo" and rec["retrieved"]:
        rows.append(("Retrieved", rec["retrieved"]))
    if rec["publisher"] and typ in ("rfc", "spec", "paper", "book", "draft"):
        rows.append(("Publisher", rec["publisher"]))
    if rec["version"]:
        rows.append(("Version", rec["version"]))
    if rec["maturity"]:
        rows.append(("Maturity", rec["maturity"]))
    if isinstance(ident, dict):
        for key in sorted(ident):
            if key == "url":
                continue
            val = ident[key]
            if val in (None, ""):
                continue
            shown = str(val)
            if key == "doi":
                shown = f'<a href="https://doi.org/{esc(val)}">{esc(val)}</a>'
                rows.append((key, shown, True))
                continue
            rows.append((key, shown))
    if rec["pages"]:
        rows.append(("Pages", rec["pages"]))
    if rec["media_type"]:
        rows.append(("Media type", rec["media_type"]))
    if rows:
        body = ""
        for row in rows:
            if len(row) == 3:
                body += f"<tr><td>{esc(row[0])}</td><td>{row[1]}</td></tr>"
            else:
                body += f"<tr><td>{esc(row[0])}</td><td>{esc(row[1])}</td></tr>"
        bits.append(f"<table><tbody>{body}</tbody></table>")

    impl = rec["implementations"] or {}
    oss = as_list(impl.get("open_source"))
    if typ == "repo":
        n = len([x for x in oss if isinstance(x, dict)])
        searched = impl.get("searched") or "not recorded"
        bits.append(
            f"<p>Open-source implementations recorded: {n}. "
            f"Search date: {esc(searched)}. Names stay in <code>record.yaml</code> "
            "and, when the summary was written, in the summary prose.</p>"
        )
    elif oss and typ == "rfc":
        bits.append(
            f"<p class=\"meta\">{len(oss)} open-source implementations are on the record. "
            "The summary prose below is the reviewed short list; this page does not "
            "re-typeset every note.</p>"
        )
    return "\n".join(bits)


def relations_section(rec: dict, published: dict[str, dict]) -> str:
    rel = rec["relations"] or {}
    if not isinstance(rel, dict):
        return ""
    blocks = []
    for key in (
        "supersedes", "superseded_by", "updates", "updated_by", "see_also",
        "implements_concept", "contradicts", "part_of", "cited_by",
    ):
        ids = [str_id(x) for x in as_list(rel.get(key)) if str_id(x)]
        if not ids:
            continue
        # supersedes already shown in the type section for some types; still list here once
        items = "".join(f"<li>{link_record_rel(x, published, rec['id'])}</li>" for x in ids)
        blocks.append(f"<h3><code>{esc(key)}</code></h3><ul>{items}</ul>")
    if not blocks:
        return ""
    return (
        "<h2>Recorded relations</h2>"
        "<p class=\"meta\">Curatorial <code>relations</code> on this record only. "
        "Empty lists are omitted. These are not crosswalk edges and not a knowledge graph.</p>"
        + "".join(blocks)
    )


def cites_section(rec: dict, published: dict[str, dict]) -> str:
    cites = as_list(rec["cites"])
    if not cites:
        return ""
    items = []
    for entry in cites:
        if isinstance(entry, dict):
            title = entry.get("title") or entry.get("ref") or "untitled gap"
            loc = entry.get("locator") or ""
            ref = entry.get("ref")
            label = esc(title)
            if isinstance(loc, str) and loc.startswith(("http://", "https://")):
                label = f'<a href="{esc(loc)}">{esc(title)}</a>'
            prefix = f"{esc(ref)} " if ref else ""
            items.append(f"<li>{prefix}{label} <span class=\"meta\">cited, no library record</span></li>")
        else:
            ident = str_id(entry)
            if not ident:
                continue
            items.append(f"<li>{link_record_rel(ident, published, rec['id'])}</li>")
    if not items:
        return ""
    return (
        "<h2>Document cites</h2>"
        "<p class=\"meta\">From <code>cites</code>: what the document references. "
        "Fact about the source, not our crosswalk. Gaps stay gaps.</p><ul>"
        + "".join(items) + "</ul>"
    )


def bib_links(rec: dict) -> str:
    rows = []
    if rec["url"]:
        rows.append(f'<li>Source: <a href="{esc(rec["url"])}">{esc(rec["url"])}</a></li>')
    ident = rec["identifiers"] if isinstance(rec["identifiers"], dict) else {}
    extra = ident.get("url")
    if isinstance(extra, str) and extra.startswith(("http://", "https://")) and extra != rec["url"]:
        rows.append(f'<li>Identifier URL: <a href="{esc(extra)}">{esc(extra)}</a></li>')
    if rec["sha256"]:
        rows.append(f"<li>SHA-256: <code>{esc(rec['sha256'])}</code></li>")
    else:
        rows.append("<li>SHA-256: <span class=\"meta\">not recorded</span></li>")
    if rec["local"] is True:
        rows.append(
            "<li><strong>Local flag is true.</strong> No filesystem path is shown. "
            "The schema requires <code>local: false</code>.</li>"
        )
    if not rows:
        return "<p class=\"meta\">No bibliographic links recorded.</p>"
    return "<ul>" + "".join(rows) + "</ul>"


def record_page(rec: dict, published: dict[str, dict]) -> str:
    bears = [str_id(x) for x in rec["bears_on"] if str_id(x)]
    if bears:
        bear_html = "<ul>" + "".join(f"<li><code>{esc(b)}</code></li>" for b in bears) + "</ul>"
    else:
        bear_html = "<p class=\"meta\">No <code>bears_on</code> ids recorded. None were invented.</p>"
    if rec["summary_written"]:
        summary = (
            "<h2>Summary</h2>"
            "<p class=\"meta\">Prose from <code>summary.md</code>, unedited. "
            "The strip above is <code>record.yaml</code>. If they disagree, "
            "the record wins for type, tags, applicability ratings, and bears_on.</p>"
            + rec["summary_html"]
        )
    else:
        summary = (
            "<h2>Summary</h2>"
            "<div class=\"callout\"><strong>Summary not written.</strong> "
            "<code>summary.md</code> is still the library template "
            "(it still contains the “two to five sentences” instruction). "
            "That text is not rendered. This page is record metadata only.</div>"
        )
    usefulness = ""
    if rec["usefulness"]:
        verdict = rec["usefulness"].get("verdict") or "unassessed"
        reason = rec["usefulness"].get("reason") or ""
        assessed = rec["usefulness"].get("assessed") or ""
        usefulness = (
            f"<h2>Usefulness</h2><p><span class=\"badge\">{esc(verdict)}</span> "
            f"{esc(reason)}</p>"
        )
        if assessed:
            usefulness += f"<p class=\"meta\">Assessed {esc(assessed)}.</p>"
    topic_line = esc(topic_label(rec))
    if rec["record_topic"]:
        topic_src = "record.yaml topic"
    elif not rec["publish_topic"]:
        topic_src = "the record has no topic field and no subject tag; tag it in the library"
    else:
        topic_src = "a tag already on the record; there is no topic field"
    body = f"""
<p class="kicker">WAVE 1 draft · {esc(rec['id'])}</p>
<h1>{esc(rec['title'])}</h1>
<p class="lede">{esc(rec.get('short_title') or '')}</p>
<p>
  <span class="badge">{esc(rec['type'])}</span>
  <span class="badge">{esc(rec['body'])}</span>
  <span class="badge">{esc(rec['status'])}</span>
  <span class="badge">{esc(rec['confidence'] or 'confidence unset')}</span>
</p>
<p class="meta">Publish topic: <strong>{topic_line}</strong> ({topic_src}). Status <code>{esc(rec['status'])}</code> is how far review got, not a quality score.</p>
<h2>Bibliographic links</h2>
{bib_links(rec)}
{type_section(rec, published)}
<h2>Applicability</h2>
{applicability_table(rec['applicability'])}
<h2>Tags</h2>
{tag_html(rec['groups'])}
<h2>Bears on</h2>
{bear_html}
{usefulness}
{relations_section(rec, published)}
{cites_section(rec, published)}
{summary}
"""
    return page(rec["title"], body, "", 1)


# --- views -----------------------------------------------------------------

def record_line(rec: dict, depth: int) -> str:
    href = f"records/{esc(rec['id'])}.html" if depth == 0 else f"{esc(rec['id'])}.html"
    reason = ""
    if rec["usefulness"] and rec["usefulness"].get("reason"):
        reason = f"<br><span class=\"meta\">{esc(rec['usefulness']['reason'])}</span>"
    written = "summary written" if rec["summary_written"] else "summary not written"
    return (
        f'<a class="cardlink" href="{href}"><strong>{esc(rec["title"])}</strong>'
        f"<br><span class=\"meta\">{esc(rec['type'])} · {esc(rec['body'])} · "
        f"topic {esc(topic_label(rec))} · {esc(rec['status'])} · {written}</span>"
        f"{reason}</a>"
    )


UNTAGGED = "no topic tag yet"


def topic_label(rec: dict) -> str:
    return rec["publish_topic"] or UNTAGGED


def _sort_key(rec: dict) -> str:
    title = re.sub(r"^[\W_]+", "", str(rec["title"])).lower()
    title = re.sub(r"^(?:the|a|an) ", "", title)
    return f"{title}\x00{rec['id']}"


def citation(rec: dict) -> str:
    """One reference-list entry. Only fields the record has; nothing guessed."""
    authors = rec["authors"]
    if len(authors) > 3:
        lead = f"{authors[0]} et al."
    elif authors:
        lead = ", ".join(authors)
    else:
        # Not `body`: that is the storage folder, and it is not an author.
        lead = rec["publisher"]
    parts = []
    if lead:
        parts.append(esc(lead.rstrip(".")) + ".")
    parts.append(f'<a href="records/{esc(rec["id"])}.html"><cite>{esc(rec["title"])}</cite></a>.')
    detail = [TYPE_HEADING.get(rec["type"], rec["type"])]
    if rec["version"]:
        detail.append(f"version {rec['version']}")
    ident = rec["identifiers"]
    for key, label in (("rfc", "RFC"), ("doi", "doi:"), ("arxiv", "arXiv:")):
        val = ident.get(key)
        if val and not isinstance(val, (dict, list)):
            sep = " " if label == "RFC" else ""
            detail.append(f"{label}{sep}{val}")
    if rec["date"]:
        detail.append(rec["date"])
    elif rec["retrieved"]:
        detail.append(f"retrieved {rec['retrieved']}")
    parts.append(esc(", ".join(detail)) + ".")
    if rec["url"]:
        parts.append(f'<a class="meta" href="{esc(rec["url"])}" rel="noreferrer">source</a>')
    if not rec["summary_written"]:
        parts.append('<span class="badge not-assessed">summary not written</span>')
    return f'<li id="{esc(rec["id"])}">' + " ".join(parts) + "</li>"


def index_page(records: list[dict], library_count: int) -> str:
    ordered = sorted(records, key=_sort_key)
    by_letter: dict[str, list[dict]] = {}
    for rec in ordered:
        first = _sort_key(rec)[:1].upper()
        by_letter.setdefault(first if first.isalpha() else "#", []).append(rec)
    letters = sorted(by_letter, key=lambda c: (c == "#", c))
    jump = " ".join(f'<a href="#letter-{esc(c)}">{esc(c)}</a>' for c in letters)
    sections = []
    for c in letters:
        items = "\n".join(citation(r) for r in by_letter[c])
        sections.append(f'<h2 id="letter-{esc(c)}">{esc(c)}</h2>\n<ol class="refs">\n{items}\n</ol>')
    written = sum(1 for r in records if r["summary_written"])
    untagged = sum(1 for r in records if not r["publish_topic"])
    types: dict[str, int] = {}
    for rec in records:
        types[rec["type"]] = types.get(rec["type"], 0) + 1
    type_bits = ", ".join(f"{n} {esc(t)}" for t, n in sorted(types.items(), key=lambda kv: (-kv[1], kv[0])))
    coverage = (
        "every library record" if len(records) == library_count
        else f"{len(records)} of {library_count} library records"
    )
    body = f"""
<p class="kicker">WAVE 1 · issue 91</p>
<h1>Bibliography</h1>
<p class="lede">{len(records)} sources the tmodel project cites or keeps for reference, rendered from {coverage}.
Each entry links to a record page with its applicability table, tags, and summary.</p>
<div class="banner"><strong>Draft, not reviewed.</strong>
{written} of {len(records)} records have a written summary; the rest are labeled. {untagged} records have no topic tag yet.
Ratings and topics come from the library records. Nothing here is a ranking or an accepted <code>DEC-*</code>.</div>
<p class="meta">By type: {type_bits}.</p>
<p class="meta">Other views: <a href="by-topic.html">topic</a>, <a href="by-type.html">document type</a>,
<a href="by-body.html">issuing body</a>, <a href="crosswalk.html">crosswalk</a>.</p>
<nav class="jump" aria-label="Jump to letter">{jump}</nav>
{"".join(sections)}
<h2>How this is categorized</h2>
<ul class="clean">
<li>Document type comes from <code>record.yaml</code>, never from summary front matter (<code>type: summary</code> on every summary).</li>
<li>Topic, document type, and issuing body are three views. Body tags, role tags, and words like <code>standard</code> are not topics.</li>
<li>Applicability ratings come from the record map. Missing means not assessed.</li>
<li>A template summary is labeled not written, not shown as prose.</li>
<li>The crosswalk is shared tags and shared <code>bears_on</code> only. No invented relations.</li>
</ul>
"""
    return page("Bibliography — tmodel", body, "index.html", 0)


def grouped_page(title: str, intro: str, groups: list[tuple[str, str, list[dict]]], current: str) -> str:
    parts = [f"<p class=\"kicker\">WAVE 1</p><h1>{esc(title)}</h1>", f"<p class=\"lede\">{intro}</p>"]
    for key, note, recs in groups:
        if not recs:
            continue
        parts.append(f"<h2 id=\"{esc(key)}\">{esc(key)}</h2>")
        if note:
            parts.append(f"<p class=\"meta\">{note}</p>")
        parts.append("\n".join(record_line(r, 0) for r in recs))
    return page(title, "\n".join(parts), current, 0)


def topic_page(records: list[dict]) -> str:
    by: dict[str, list[dict]] = {}
    for rec in records:
        by.setdefault(topic_label(rec), []).append(rec)
    primary = []
    for topic in sorted(by, key=lambda k: (k == UNTAGGED, k)):
        primary.append((topic, "Primary publish topic. One home per record.", by[topic]))
    # secondary tag index
    tag_map: dict[str, list[dict]] = {}
    for rec in records:
        for tag in rec["groups"]["topic"]:
            if tag == rec["publish_topic"]:
                continue
            tag_map.setdefault(tag, []).append(rec)
    secondary_bits = ["<h2>Other topic tags</h2>",
                      "<p class=\"meta\">A record can sit in more than one subject tag. "
                      "Tags equal to the primary topic are not repeated. Body, role, and standing tags are not listed here.</p>"]
    if not tag_map:
        secondary_bits.append("<p class=\"meta\">No extra topic tags in this subset.</p>")
    for tag in sorted(tag_map):
        secondary_bits.append(f"<h3 id=\"tag-{esc(tag)}\">{esc(tag)}</h3>")
        secondary_bits.append("\n".join(record_line(r, 0) for r in tag_map[tag]))
    intro = (
        "Primary topic is <code>record.topic</code> when that field is set, "
        "otherwise one tag the record already carries. The manifest cannot introduce a topic the record does not."
    )
    base = grouped_page("By topic", intro, primary, "by-topic.html")
    # insert secondary before footer by rebuilding simply
    body_inner_end = base.rfind("<footer>")
    return base[:body_inner_end] + "\n".join(secondary_bits) + "\n" + base[body_inner_end:]


def type_page(records: list[dict]) -> str:
    blurbs = {
        "rfc": "Internet Standard or other RFC. Number and maturity come from the record.",
        "draft": "Internet-Draft. Not rendered as an RFC.",
        "spec": "Specification from a body, a regulator, or a consortium. Publisher and version when the record has them.",
        "paper": "Paper. Authors and date only as recorded.",
        "dataset": "Living catalog or enumeration. One record for the dataset, not one row.",
        "repo": "Source repository. Treated as an implementation.",
        "web": "Web page. Retrieval date, not an edition.",
    }
    by: dict[str, list[dict]] = {}
    for rec in records:
        by.setdefault(rec["type"], []).append(rec)
    groups = []
    for typ in sorted(by):
        groups.append((typ, blurbs.get(typ, "Document type from record.yaml."), by[typ]))
    return grouped_page(
        "By document type",
        "Type is record.yaml <code>type</code>. Summary front matter is ignored for this view.",
        groups,
        "by-type.html",
    )


def body_page(records: list[dict]) -> str:
    by: dict[str, list[dict]] = {}
    for rec in records:
        by.setdefault(rec["body"], []).append(rec)
    groups = [(b, "Issuing body. Not a topic.", by[b]) for b in sorted(by)]
    return grouped_page(
        "By issuing body",
        "Separate from topic. The folder under <code>library/records/</code> is this field, and several body names also appear as tags. Those tags do not create topic groups.",
        groups,
        "by-body.html",
    )


def crosswalk_page(records: list[dict], published: dict[str, dict]) -> str:
    tag_map: dict[str, list[dict]] = {}
    bear_map: dict[str, list[dict]] = {}
    for rec in records:
        for tag in rec["groups"]["topic"]:
            tag_map.setdefault(tag, []).append(rec)
        for b in rec["bears_on"]:
            ident = str_id(b)
            if ident:
                bear_map.setdefault(ident, []).append(rec)
    tag_map = {k: v for k, v in tag_map.items() if len(v) >= 2}
    bear_map = {k: v for k, v in bear_map.items() if len(v) >= 2}

    parts = [
        "<p class=\"kicker\">WAVE 1</p>",
        "<h1>Crosswalk</h1>",
        "<div class=\"callout\"><strong>Co-membership only.</strong> "
        "A shared tag is not a citation. A shared <code>bears_on</code> id means both records name it, not that they agree. "
        "<code>relations</code> and <code>cites</code> stay on the record page and are not copied here. "
        "Nothing is linked that the records do not already both carry. "
        "Body tags, role tags, and standing words are excluded.</div>",
        "<h2>Shared bears_on</h2>",
    ]
    if not bear_map:
        parts.append("<p class=\"meta\">No shared bears_on id in this subset.</p>")
    for key in sorted(bear_map):
        recs = bear_map[key]
        parts.append(f"<h3 id=\"bears-{esc(key)}\"><code>{esc(key)}</code></h3>")
        parts.append("<p class=\"meta\">Named on each of these records. Not an edge we added.</p><ul>")
        for rec in recs:
            parts.append(f"<li>{link_record(rec['id'], published)}</li>")
        parts.append("</ul>")
    parts.append("<h2>Shared topic tags</h2>")
    if not tag_map:
        parts.append("<p class=\"meta\">No topic tag is shared by two published records.</p>")
    for tag in sorted(tag_map):
        recs = tag_map[tag]
        topics = {r["publish_topic"] for r in recs}
        broad = len(topics) > 1
        flag = " <span class=\"badge broad\">broad</span>" if broad else ""
        parts.append(f"<h3 id=\"tag-{esc(tag)}\">{esc(tag)}{flag}</h3>")
        if broad:
            parts.append(
                "<p class=\"meta\">Broad: these records do not share one publish-topic "
                f"({esc(', '.join(sorted(topics)))}). Co-membership only — not a reviewed synonym and not a citation.</p>"
            )
        else:
            parts.append("<p class=\"meta\">Same publish-topic. Still co-membership, not a typed relation.</p>")
        parts.append("<ul>")
        for rec in recs:
            parts.append(f"<li>{link_record(rec['id'], published)}</li>")
        parts.append("</ul>")
    return page("Crosswalk", "\n".join(parts), "crosswalk.html", 0), tag_map, bear_map


# --- main ------------------------------------------------------------------

def build_record(entry: dict, role: set[str], body_tags: set[str]) -> dict:
    record_id = entry["id"]
    path = find_record(record_id)
    data = load_yaml(path)
    if data.get("id") != record_id:
        raise SystemExit(f"{path}: id is {data.get('id')!r}, manifest says {record_id}")
    typ = data.get("type")
    if typ != entry.get("type"):
        raise SystemExit(
            f"{record_id}: manifest type {entry.get('type')!r} != record.yaml type {typ!r}. "
            "Refusing to relabel."
        )
    tags = [str(t) for t in as_list(data.get("tags"))]
    groups = tag_groups(tags, role, body_tags)
    record_topic = data.get("topic") or ""
    if isinstance(record_topic, str):
        record_topic = record_topic.strip()
    else:
        record_topic = str(record_topic)
    manifest_topic = str(entry.get("topic") or "").strip()
    if record_topic:
        if manifest_topic != record_topic:
            raise SystemExit(
                f"{record_id}: record.topic is {record_topic!r}; manifest has {manifest_topic!r}."
            )
    elif not manifest_topic:
        if groups["topic"]:
            raise SystemExit(
                f"{record_id}: manifest topic is empty but the record has topic tags {groups['topic']}; pick one."
            )
    elif manifest_topic not in tags:
        raise SystemExit(
            f"{record_id}: manifest topic {manifest_topic!r} is not record.topic and not one of the record's tags {tags}."
        )
    summary_path = path.parent / "summary.md"
    summary_written = False
    summary_html = ""
    front_type = None
    if summary_path.exists():
        fm, md = load_front_matter(summary_path.read_text(encoding="utf-8"), str(summary_path))
        front_type = fm.get("type")
        summary_written = BOILERPLATE_MARK not in md
        if summary_written:
            summary_html = md_to_html(md)
    content = data.get("content") or {}
    if not isinstance(content, dict):
        content = {}
    local = content.get("local")
    url = content.get("url") if isinstance(content.get("url"), str) else ""
    if local is True:
        url = url if isinstance(url, str) and url.startswith(("http://", "https://")) else ""
    authors = []
    for a in as_list(data.get("authors")):
        if isinstance(a, str):
            authors.append(a)
    usefulness = data.get("usefulness") if isinstance(data.get("usefulness"), dict) else {}
    short = data.get("short_title") or data.get("title") or record_id
    return {
        "id": record_id,
        "title": data.get("title") or record_id,
        "short": short,
        "short_title": data.get("short_title") or "",
        "type": typ,
        "body": data.get("body") or "",
        "status": data.get("status") or "",
        "maturity": data.get("maturity") or "",
        "confidence": data.get("confidence") or "",
        "date": str(data.get("date") or ""),
        "publisher": data.get("publisher") or "",
        "version": str(data.get("version") or ""),
        "authors": authors,
        "identifiers": data.get("identifiers") if isinstance(data.get("identifiers"), dict) else {},
        "url": url,
        "sha256": content.get("sha256") or "",
        "retrieved": str(content.get("retrieved") or ""),
        "local": local,
        "pages": content.get("pages") or "",
        "media_type": content.get("media_type") or "",
        "relations": data.get("relations") if isinstance(data.get("relations"), dict) else {},
        "cites": data.get("cites"),
        "bears_on": as_list(data.get("bears_on")),
        "applicability": data.get("applicability") if isinstance(data.get("applicability"), dict) else {},
        "implementations": data.get("implementations") if isinstance(data.get("implementations"), dict) else {},
        "usefulness": usefulness,
        "tags": tags,
        "groups": groups,
        "record_topic": record_topic,
        "publish_topic": manifest_topic,
        "summary_written": summary_written,
        "summary_html": summary_html,
        "summary_front_type": front_type,
        "path": path,
    }


def check_security(manifest: dict):
    sec = manifest.get("security") or {}
    for flag in ("remote_scripts", "trackers", "secrets"):
        if sec.get(flag) not in (False, None):
            raise SystemExit(f"security.{flag} must be false")


def assert_rules(published: dict[str, dict], tag_map: dict, bear_map: dict):
    rfc = published["rfc-8949"]
    if rfc["summary_front_type"] != "summary":
        raise SystemExit("expected the summary-front-matter trap on rfc-8949")
    if rfc["type"] != "rfc":
        raise SystemExit("rfc-8949 type was relabeled")
    if published["draft-ietf-vcon-vcon-core-04"]["type"] != "draft":
        raise SystemExit("draft was filed as something else")
    if published["cyclonedx-1-7"]["summary_written"]:
        raise SystemExit("cyclonedx template was treated as a written summary")
    for banned in ("standard", "ietf", "normative", "prior-art", "nist", "iso", "openssf"):
        if banned in tag_map:
            raise SystemExit(f"crosswalk included non-topic tag {banned}")
    if "graph" not in tag_map:
        raise SystemExit("expected a real shared topic tag 'graph'")
    if "DEC-001" not in bear_map:
        raise SystemExit("expected shared bears_on DEC-001")
    # standing tag exists on records but must not be a crosswalk key
    standing_holders = [
        r["id"] for r in published.values() if "standard" in r["tags"]
    ]
    if len(standing_holders) < 2:
        raise SystemExit(f"fixture weakened: 'standard' tag not on 2+ records ({standing_holders})")


def write_outputs(records: list[dict], published: dict[str, dict], library_count: int):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rec_dir = OUT_DIR / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    wanted = {r["id"] for r in records}
    for stale in rec_dir.glob("*.html"):
        if stale.stem not in wanted:
            stale.unlink()
    files = {
        "index.html": index_page(records, library_count),
        "by-topic.html": topic_page(records),
        "by-type.html": type_page(records),
        "by-body.html": body_page(records),
    }
    cross_html, tag_map, bear_map = crosswalk_page(records, published)
    files["crosswalk.html"] = cross_html
    assert_rules(published, tag_map, bear_map)
    for name, text in files.items():
        _refuse_active(text, name)
        (OUT_DIR / name).write_text(text, encoding="utf-8")
    for rec in records:
        text = record_page(rec, published)
        _refuse_active(text, rec["id"])
        (rec_dir / f"{rec['id']}.html").write_text(text, encoding="utf-8")
    return tag_map, bear_map


def _refuse_active(text: str, name: str):
    lower = text.lower()
    if "<script" in lower or "javascript:" in lower:
        raise SystemExit(f"{name}: script refused")
    if "{{" in text or "{%" in text:
        raise SystemExit(f"{name}: template delimiter refused")
    # A citation may link to a repo named `foo.js`; only a loaded asset is refused.
    if re.search(r"<(?:script|link|img|iframe)\b[^>]*(?:src|href)=[\"']?(?:https?:)?//", text, re.I):
        raise SystemExit(f"{name}: remote asset refused")
    for banned in ("google-analytics", "googletagmanager", "fonts.googleapis", "cdn.jsdelivr"):
        if banned in lower:
            raise SystemExit(f"{name}: tracker or remote font refused")


def default_topic(data: dict, role: set[str], body_tags: set[str], subject: list[str]) -> str:
    """Primary topic for a newly listed record: never a word the record lacks.

    record.topic if set; else the first controlled subject tag the record
    carries; else its first other topic tag; else empty (shown as untagged).
    """
    record_topic = str(data.get("topic") or "").strip()
    if record_topic:
        return record_topic
    topic_tags = tag_groups([str(t) for t in as_list(data.get("tags"))], role, body_tags)["topic"]
    for tag in topic_tags:
        if tag in subject:
            return tag
    return topic_tags[0] if topic_tags else ""


def sync_manifest(role: set[str], body_tags: set[str]) -> int:
    """Append library records missing from the manifest. Existing entries are
    never changed, so a reviewer's topic choice survives every sync."""
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    listed = {e["id"] for e in as_list(load_yaml(MANIFEST_PATH).get("records"))}
    subject = [str(s) for s in as_list(load_yaml(TAGS_PATH).get("subject"))]
    lines = []
    for path in sorted(RECORDS_ROOT.glob("*/*/record.yaml")):
        data = load_yaml(path)
        rid = data.get("id")
        if rid in listed:
            continue
        topic = default_topic(data, role, body_tags, subject)
        lines += [f"  - id: {rid}", f"    type: {data.get('type')}",
                  f"    topic: {topic}" if topic else "    topic: ~  # no topic tag on the record yet"]
    if not lines:
        print("manifest already lists every library record")
        return 0
    marker = "\noutputs:"
    if marker not in text:
        raise SystemExit("manifest: cannot find the outputs: key that follows records:")
    text = text.replace(marker, "\n" + "\n".join(lines) + marker, 1)
    MANIFEST_PATH.write_text(text, encoding="utf-8")
    print(f"appended {len(lines) // 3} records to {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


def main() -> int:
    manifest = load_yaml(MANIFEST_PATH)
    if manifest.get("schema") != "tmodel.publishing/v0":
        raise SystemExit("manifest schema must be tmodel.publishing/v0")
    check_security(manifest)
    role, body_tags = load_controlled_tags()
    if "--sync" in sys.argv[1:]:
        return sync_manifest(role, body_tags)
    entries = manifest.get("records")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("manifest records must be a non-empty list")
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids in manifest")
    records = [build_record(e, role, body_tags) for e in entries]
    published = {r["id"]: r for r in records}
    library_count = len(list(RECORDS_ROOT.glob("*/*/record.yaml")))
    tag_map, bear_map = write_outputs(records, published, library_count)
    print(f"rendered {len(records)} records ({library_count} in library)")
    print("topics:", ", ".join(sorted({r['publish_topic'] for r in records})))
    print("types:", ", ".join(sorted({r['type'] for r in records})))
    print("bodies:", ", ".join(sorted({r['body'] for r in records})))
    print("crosswalk tags:", ", ".join(sorted(tag_map)))
    print("crosswalk bears_on:", ", ".join(sorted(bear_map)))
    unwritten = [r["id"] for r in records if not r["summary_written"]]
    print(f"summary not written: {len(unwritten)}")
    untagged = [r["id"] for r in records if not r["publish_topic"]]
    print(f"{UNTAGGED}: {', '.join(untagged) or '(none)'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
