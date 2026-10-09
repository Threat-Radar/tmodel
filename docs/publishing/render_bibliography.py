#!/usr/bin/env python3
"""Publish the bibliography: manifest in, static HTML out.

Two outputs, two owners:

- docs/library/records/<body>/<id>/summary.html -- the per-record pages.
  The library builds them beside their source (library bin/_record_html.py,
  untracked records/<body>/<id>/summary.html). This script renders them in
  the pinned submodule, then copies the ones the manifest lists. It changes
  only the site-nav slot, and it turns links to unpublished records into
  plain text.
- docs/bibliography/*.html -- the A-Z index plus the topic, type, body, and
  crosswalk views. These belong to tmodel and come from the manifest
  (docs/publishing/bibliography.yaml), with nav from docs/publishing/site.yaml.

    python3 docs/publishing/render_bibliography.py          # render
    python3 docs/publishing/render_bibliography.py --sync   # add new library records to the manifest

Deterministic, stdlib only, no network. Rules: bibliography-review.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "library" / "bin"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _record_html as rh  # noqa: E402  (pinned library submodule)
from _record_yaml import load_yaml  # noqa: E402
import site_nav as site_chrome  # noqa: E402  (docs/publishing/site_nav.py)

MANIFEST_PATH = ROOT / "docs" / "publishing" / "bibliography.yaml"
OUT_DIR = ROOT / "docs" / "bibliography"
REC_OUT = ROOT / "docs" / "library" / "records"
RECORDS_ROOT = rh.RECORDS_ROOT
TAGS_PATH = rh.TAGS_PATH
TYPE_HEADING = rh.TYPE_HEADING
CSS = rh.CSS
esc = rh.esc
as_list = rh.as_list
tag_groups = rh.tag_groups
load_controlled_tags = rh.load_controlled_tags
str_id = rh.str_id


# --- chrome and links --------------------------------------------------------

def record_href(rec: dict) -> str:
    """From docs/bibliography/ to the copied library page."""
    return f"../library/records/{rec['body']}/{rec['id']}/{rh.PAGE_NAME}"


def page(title: str, body: str, current: str) -> str:
    items = [
        ("index.html", "A-Z"),
        ("by-topic.html", "Topic"),
        ("by-type.html", "Type"),
        ("by-body.html", "Issuing body"),
        ("crosswalk.html", "Crosswalk"),
    ]
    sub = ['<nav class="sub" aria-label="Bibliography views">']
    for name, label in items:
        cur = ' aria-current="page"' if name == current else ""
        sub.append(f'<a href="{name}"{cur}>{label}</a>')
    sub.append("</nav>")
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="referrer" content="no-referrer">\n'
        f"<title>{esc(title)}</title>\n"
        f"<style>{CSS}{SUB_CSS}</style>\n</head>\n<body>\n"
        f"{site_chrome.header(1, 'bibliography/index.html')}\n"
        f"<main class=\"wrap\">\n{''.join(sub)}\n{body}\n"
        "<footer><p>Generated from <code>docs/publishing/bibliography.yaml</code> "
        "by <code>docs/publishing/render_bibliography.py</code>. Record pages are built in the "
        "library beside their source. Do not hand-edit. Static HTML, no scripts, no trackers. See "
        "<a href=\"../publishing/bibliography-review.md\">bibliography-review.md</a>."
        "</p></footer>\n</main>\n</body>\n</html>\n"
    )


SUB_CSS = """
nav.sub { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 18px 0 0; font-size: 0.92rem; }
nav.sub a { color: var(--muted); text-decoration: none; }
nav.sub a[aria-current="page"] { color: var(--ink); font-weight: 650; }
ol.refs { list-style: none; padding: 0; margin: 0; }
ol.refs li { padding: 8px 0 8px 1.6em; text-indent: -1.6em; border-bottom: 1px solid var(--line); overflow-wrap: anywhere; }
ol.refs cite { font-style: italic; }
nav.jump { display: flex; flex-wrap: wrap; gap: 4px 10px; margin: 18px 0 0; font-weight: 600; }
"""


def link_record(record_id: str, published: dict[str, dict]) -> str:
    rec = published.get(record_id)
    label = esc(rec["short"] if rec else record_id)
    ident = esc(record_id)
    if rec:
        return f'<a href="{esc(record_href(rec))}">{label}</a> <span class="meta">({ident})</span>'
    return f"{label} <span class=\"meta\">({ident}, not published)</span>"


# --- views -----------------------------------------------------------------

def record_line(rec: dict, depth: int) -> str:
    href = esc(record_href(rec))
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
    parts.append(f'<a href="{esc(record_href(rec))}"><cite>{esc(rec["title"])}</cite></a>.')
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
    return page("Bibliography — tmodel", body, "index.html")


def grouped_page(title: str, intro: str, groups: list[tuple[str, str, list[dict]]], current: str) -> str:
    parts = [f"<p class=\"kicker\">WAVE 1</p><h1>{esc(title)}</h1>", f"<p class=\"lede\">{intro}</p>"]
    for key, note, recs in groups:
        if not recs:
            continue
        parts.append(f"<h2 id=\"{esc(key)}\">{esc(key)}</h2>")
        if note:
            parts.append(f"<p class=\"meta\">{note}</p>")
        parts.append("\n".join(record_line(r, 0) for r in recs))
    return page(title, "\n".join(parts), current)


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
    return page("Crosswalk", "\n".join(parts), "crosswalk.html"), tag_map, bear_map


# --- main ------------------------------------------------------------------

def build_record(entry: dict, library: dict[str, dict]) -> dict:
    """The library's record plus this site's publish topic, checked."""
    record_id = entry["id"]
    if record_id not in library:
        raise SystemExit(f"{record_id}: in the manifest but not in library/records")
    rec = dict(library[record_id])
    if rec["type"] != entry.get("type"):
        raise SystemExit(
            f"{record_id}: manifest type {entry.get('type')!r} != record.yaml type {rec['type']!r}. "
            "Refusing to relabel."
        )
    record_topic = rec["record_topic"]
    manifest_topic = str(entry.get("topic") or "").strip()
    if record_topic:
        if manifest_topic != record_topic:
            raise SystemExit(
                f"{record_id}: record.topic is {record_topic!r}; manifest has {manifest_topic!r}."
            )
    elif not manifest_topic:
        if rec["groups"]["topic"]:
            raise SystemExit(
                f"{record_id}: manifest topic is empty but the record has topic tags {rec['groups']['topic']}; pick one."
            )
    elif manifest_topic not in rec["tags"]:
        raise SystemExit(
            f"{record_id}: manifest topic {manifest_topic!r} is not record.topic and not one of the record's tags {rec['tags']}."
        )
    rec["publish_topic"] = manifest_topic
    return rec


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


_REC_LINK = re.compile(r'<a class="rec" data-id="([^"]+)" href="[^"]*">(.*?)</a>')


def publish_record_pages(records: list[dict], library: dict[str, dict], published: dict[str, dict]):
    """Render pages beside their source in the library, then copy the listed ones."""
    rh.render(library, [r["id"] for r in records])
    nav = site_chrome.header(4, "bibliography/index.html")
    wanted = set()
    for rec in records:
        text = rec["page_path"].read_text(encoding="utf-8")
        if rh.SITE_NAV_SLOT not in text:
            raise SystemExit(f"{rec['id']}: library page has no site-nav slot")
        text = text.replace(rh.SITE_NAV_SLOT, nav, 1)
        text = _REC_LINK.sub(
            lambda m: m.group(0) if m.group(1) in published
            else f'{m.group(2)} <span class="meta">(not published)</span>',
            text,
        )
        _refuse_active(text, rec["id"])
        out = REC_OUT / rec["body"] / rec["id"] / rh.PAGE_NAME
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        wanted.add(out)
    for stale in REC_OUT.glob(f"*/*/{rh.PAGE_NAME}"):
        if stale not in wanted:
            stale.unlink()
            try:
                stale.parent.rmdir()
            except OSError:
                pass


def write_outputs(records: list[dict], library: dict[str, dict], published: dict[str, dict], library_count: int):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
    publish_record_pages(records, library, published)
    return tag_map, bear_map


def _refuse_active(text: str, name: str):
    rh.refuse_active(text, name)
    if "{{" in text or "{%" in text:
        raise SystemExit(f"{name}: template delimiter refused")
    lower = text.lower()
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
    library = rh.load_all()
    records = [build_record(e, library) for e in entries]
    published = {r["id"]: r for r in records}
    library_count = len(library)
    tag_map, bear_map = write_outputs(records, library, published, library_count)
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
