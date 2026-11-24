"""Prove the CWE import lost nothing (#146; PLAN-0002 §5's acceptance test).

The catalog file is read twice: once through the importer (`cwe.load_catalog`), and
once more with ElementTree alone, with none of the importer's code. The two readings
are compared:

- **entries**: every Weakness, Category and View in the file is imported once, with
  its own kind and id, and every External_Reference id as many times as the file
  defines it. PLAN-0002 §5 named "the
  union of entries across the views". The import reads the whole catalog (#61,
  question 1), so the report also counts the entries that no view's relationships
  reach, which a view-by-view import would drop;
- **relationships**: the (entry, nature, target, view) tuples the file writes, as a
  Related_Weakness or a Has_Member or Member_Of, equal the ones the import keeps
  (#145), each as many times as the file writes it, all together and view by view;
- **fields**: for each entry and each of its fields, what the file holds equals what
  was kept: an attribute's value exactly, and for any other field its elements, the
  names and values of the attributes inside it, and its words, in order. A field the
  reader does not know is kept, not lost, and is flagged;
- **links**: every CAPEC link and observed example in the file is read.

`lossless` is true only when all of these agree. Run as a module, it prints the report
and exits 1 on any loss; CI runs it on MITRE's release (`.github/workflows/cwe.yml`).

    python -m engine.load.cwe_reconcile FILE [--sha256 S] [--json] [--write R | --check R]

`--write` saves the Markdown report to R, and `--check` fails when R differs from it,
so the committed report stays the one the real import gives.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter
from collections.abc import Iterable, Mapping
from itertools import zip_longest
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from engine.load import cwe

NS = f"{{{cwe.CWE_NS}}}"
XML_NS = "{http://www.w3.org/XML/1998/namespace}"
XSI_NS = "{http://www.w3.org/2001/XMLSchema-instance}"
KINDS = {"Weaknesses": "Weakness", "Categories": "Category", "Views": "View"}
RELATIONSHIP_FIELDS = {
    "Weakness": "Related_Weaknesses",
    "Category": "Relationships",
    "View": "Members",
}
MEMBERSHIP = {"Has_Member": "HasMember", "Member_Of": "MemberOf"}
# The views PLAN-0002 §5 named, which the report shows first.
NAMED_VIEWS = (1000, 699, 1194)


def reconcile(path: str | Path, sha256: str | None = None) -> dict[str, Any]:
    """The reconciliation report for the catalog at `path`. CweError when it cannot be read.

    With `sha256`, the file must have exactly that digest, as `cwe.load_catalog` asks.
    """
    path = Path(path)
    catalog = cwe.load_catalog(path, sha256)
    data = cwe._read(path)  # the importer's bounded read: a regular file, size-limited
    if hashlib.sha256(data).hexdigest() != catalog.sha256:
        raise cwe.CweError(f"{path.name}: the file changed while it was being read")
    source = _source(_root(path.name, data))
    return _report(catalog, source)


# --- the file, read with ElementTree alone ----------------------------------------------------


def _root(name: str, data: bytes) -> ElementTree.Element:
    xml = data
    if data[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            (member,) = [i for i in archive.infolist() if not i.is_dir()]
            with archive.open(member) as handle:
                xml = handle.read(cwe.MAX_XML_BYTES + 1)
    if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:  # the importer refused these too
        raise cwe.CweError(f"{name}: has a DOCTYPE or ENTITY declaration")
    return ElementTree.fromstring(xml)


def _source(root: ElementTree.Element) -> dict[str, Any]:
    """What the file holds: entries, references, relationships, fields and links."""
    entries: dict[str, tuple[str, str | None, str | None]] = {}  # id -> (kind, Status, Type)
    elements: dict[str, ElementTree.Element] = {}  # id -> the entry or reference element
    references: list[str] = []
    relationships: list[tuple[str, str, str, int]] = []
    capec = examples = 0
    for container in root:
        name = container.tag.removeprefix(NS)
        if name == "External_References":
            for reference in container:
                references.append(reference.get("Reference_ID", ""))
                elements[reference.get("Reference_ID", "")] = reference
            continue
        kind = KINDS.get(name)
        for entry in container if kind is not None else ():
            entry_id = f"CWE-{int(entry.get('ID', '-1'))}"
            entries[entry_id] = (kind, entry.get("Status"), entry.get("Type"))
            elements[entry_id] = entry
            for holder in entry.findall(NS + RELATIONSHIP_FIELDS[kind]):
                for child in holder:
                    tag = child.tag.removeprefix(NS)
                    nature = (
                        child.get("Nature") if tag == "Related_Weakness" else MEMBERSHIP.get(tag)
                    )
                    if nature is None:
                        continue  # not a relationship: the field tallies still count it
                    relationships.append(
                        (
                            entry_id,
                            nature,
                            f"CWE-{int(child.get('CWE_ID', '-1'))}",
                            int(child.get("View_ID", "-1")),
                        )
                    )
            capec += len(entry.findall(f"{NS}Related_Attack_Patterns/{NS}Related_Attack_Pattern"))
            examples += len(entry.findall(f"{NS}Observed_Examples/{NS}Observed_Example"))
    return {
        "entries": entries,
        "elements": elements,
        "references": references,
        "relationships": relationships,
        "capec": capec,
        "examples": examples,
    }


# --- the comparison ------------------------------------------------------------------------


def _report(catalog: cwe.CweCatalog, source: Mapping[str, Any]) -> dict[str, Any]:
    imported = {e.id: e for e in (*catalog.weaknesses, *catalog.categories, *catalog.views)}
    kept_references = [r.get("@Reference_ID", "") for r in catalog.references]
    entries = _entries(source["entries"], imported, source["references"], kept_references)
    relationships = _relationships(source["relationships"], catalog.stated_relationships)
    kept_fields = {
        **{e.id: e.fields for e in imported.values()},
        **{r.get("@Reference_ID", ""): r for r in catalog.references},
    }
    fields = _fields(source["elements"], kept_fields, source["entries"])
    reached = {s for s, *_ in source["relationships"]} | {
        t for _, _, t, _ in source["relationships"]
    }
    views = {
        "entries_reached": len(reached & set(source["entries"])),
        "entries_without_view": [
            {"id": i, "kind": kind, "status": status, "view_type": view_type}
            for i, (kind, status, view_type) in sorted(
                source["entries"].items(), key=lambda e: _order(e[0])
            )
            if i not in reached
        ],
    }
    links = {
        "attack_pattern_links": {
            "in_file": source["capec"],
            "imported": catalog.links()["attack_pattern_links"],
        },
        "observed_examples": {
            "in_file": source["examples"],
            "imported": sum(len(w.observed_examples) for w in catalog.weaknesses),
        },
    }
    # Equal totals are not enough on their own: one relationship can lose a copy while
    # another gains one, and two entries can trade kinds (#249 review). So each tuple and
    # each reference id must be kept as many times as the file gives it, and each entry
    # with its own kind.
    lossless = (
        not any(entries[k]["missing"] or entries[k]["extra"] for k in ("entries", "references"))
        and entries["entries"]["by_kind_in_file"] == entries["entries"]["by_kind_imported"]
        and not entries["entries"]["kind_changed"]
        and entries["references"]["in_file"] == entries["references"]["imported"]
        and not entries["references"]["repeated_differently"]
        and not relationships["missing"]
        and not relationships["extra"]
        and relationships["in_file"] == relationships["imported"]
        and not relationships["repeated_differently"]
        and not fields["not_kept"]
        and all(link["in_file"] == link["imported"] for link in links.values())
    )
    return {
        "catalog": {
            "name": catalog.name,
            "version": catalog.version,
            "date": catalog.date,
            "schema": catalog.schema,
            "file": catalog.file,
            "sha256": catalog.sha256,
        },
        "lossless": lossless,
        **entries,
        "views": views,
        "relationships": relationships,
        "fields": fields,
        "links": links,
    }


def _entries(
    in_file: Mapping[str, tuple[str, str | None, str | None]],
    imported: Mapping[str, cwe.CweEntry],
    references: list[str],
    kept_references: list[str],
) -> dict[str, Any]:
    file_ids, kept_ids = Counter(references), Counter(kept_references)
    return {
        "entries": {
            "by_kind_in_file": dict(Counter(kind for kind, *_ in in_file.values())),
            "by_kind_imported": dict(Counter(e.kind for e in imported.values())),
            "missing": sorted(set(in_file) - set(imported), key=_order),
            "extra": sorted(set(imported) - set(in_file), key=_order),
            "kind_changed": sorted(
                (i for i in set(in_file) & set(imported) if in_file[i][0] != imported[i].kind),
                key=_order,
            ),
        },
        "references": {
            "in_file": len(references),
            "imported": len(kept_references),
            "missing": sorted(set(references) - set(kept_references)),
            "extra": sorted(set(kept_references) - set(references)),
            # an id the file defines more or fewer times than the import keeps it
            "repeated_differently": sorted(
                i for i in set(file_ids) & set(kept_ids) if file_ids[i] != kept_ids[i]
            ),
        },
    }


def _relationships(
    in_file: list[tuple[str, str, str, int]], imported: Iterable[cwe.Relationship]
) -> dict[str, Any]:
    kept = [(r.source, r.nature, r.target, r.view) for r in imported]
    file_count, kept_count = Counter(in_file), Counter(kept)
    file_natures = Counter(nature for _, nature, _, _ in in_file)
    kept_natures = Counter(nature for _, nature, _, _ in kept)
    views = sorted({v for *_, v in in_file} | {v for *_, v in kept}, key=_view_order)
    return {
        "in_file": len(in_file),
        "imported": len(kept),
        "distinct_in_file": len(file_count),
        "distinct_imported": len(kept_count),
        "missing": [_tuple(t) for t in sorted(set(file_count) - set(kept_count))],
        "extra": [_tuple(t) for t in sorted(set(kept_count) - set(file_count))],
        "repeated_differently": [
            {**_tuple(t), "in_file": file_count[t], "imported": kept_count[t]}
            for t in sorted(set(file_count) & set(kept_count))
            if file_count[t] != kept_count[t]
        ],
        "by_nature": {
            nature: {"in_file": file_natures[nature], "imported": kept_natures[nature]}
            for nature in _in_nature_order(file_natures | kept_natures)
        },
        "by_view": {
            f"CWE-{view}": {
                "in_file": sum(1 for *_, v in in_file if v == view),
                "imported": sum(1 for *_, v in kept if v == view),
            }
            for view in views
        },
    }


def _fields(
    elements: Mapping[str, ElementTree.Element],
    kept: Mapping[str, Mapping[str, Any]],
    entries: Mapping[str, tuple[str, str | None, str | None]],
) -> dict[str, Any]:
    """Field by field, for every entry and reference: what the file holds against what was kept."""
    not_kept: list[dict[str, Any]] = []
    carried: Counter[tuple[str, str]] = Counter()
    kept_carried: Counter[tuple[str, str]] = Counter()
    for item_id, element in elements.items():
        kind = entries[item_id][0] if item_id in entries else "External_Reference"
        fields = kept.get(item_id)
        if fields is None:
            continue  # the entry itself is missing, which the entries section says
        in_file = _file_fields(element)
        held = _kept_fields(fields)
        carried.update((kind, name) for name in in_file)
        kept_carried.update((kind, name) for name in held)
        for name in sorted(set(in_file) | set(held)):
            if name.startswith("@"):
                if in_file.get(name) != held.get(name):
                    not_kept.append(
                        {
                            "entry": item_id,
                            "field": name,
                            "in_file": in_file.get(name),
                            "kept": held.get(name),
                        }
                    )
                continue
            file_side = _joined_signatures(_xml_signature(e) for e in in_file.get(name, []))
            kept_side = _joined_signatures(_kept_signature(v, name) for v in held.get(name, []))
            counts = (len(in_file.get(name, [])), len(held.get(name, [])))
            differs = [
                what
                for what, a, b in (
                    ("values", counts[0], counts[1]),
                    ("elements", file_side[0], kept_side[0]),
                    ("names", file_side[3], kept_side[3]),
                    ("attributes", file_side[1], kept_side[1]),
                    ("words", file_side[2], kept_side[2]),
                )
                if a != b
            ]
            if differs:
                loss = {
                    "entry": item_id,
                    "field": name,
                    "differs": differs,
                    "in_file": {"values": counts[0], "tally": _tally(file_side)},
                    "kept": {"values": counts[1], "tally": _tally(kept_side)},
                }
                if "names" in differs:
                    loss["first_name_difference"] = _first_difference(file_side[3], kept_side[3])
                not_kept.append(loss)
    known = {(kind, name) for kind, names in cwe.ENTRY_FIELDS.items() for name in names}
    rows = [
        {
            "kind": kind,
            "field": name,
            "in_file": carried[(kind, name)],
            "imported": kept_carried[(kind, name)],
            "maps_to": cwe.MAPPED.get((kind, name)),
            "known": (kind, name) in known,
        }
        for kind, name in [
            *((k, n) for k, names in cwe.ENTRY_FIELDS.items() for n in names),
            *sorted(set(carried) - known),
        ]
    ]
    return {
        "checked": len(elements),
        "rows": rows,
        "unknown": [r for r in rows if not r["known"] and r["in_file"]],
        "not_kept": not_kept,
    }


# --- tallies: elements, attributes and words, from each side ------------------------------------


def _file_fields(element: ElementTree.Element) -> dict[str, Any]:
    """An entry's fields in the file: each attribute's value, and each child's elements."""
    fields: dict[str, Any] = {f"@{_attribute(k)}": v for k, v in element.attrib.items()}
    for child in element:
        fields.setdefault(child.tag.rpartition("}")[2], []).append(child)
    return fields


def _kept_fields(fields: Mapping[str, Any]) -> dict[str, Any]:
    """The same fields as the import kept them, whichever form (`#items` or lists) holds them."""
    found: dict[str, Any] = {}
    for key, value in fields.items():
        if key.startswith("@"):
            found[key] = value
        elif key == "#items":
            for item in value:
                for name, one in item.items():
                    found.setdefault(name, []).append(one)
        elif not key.startswith("#"):
            found.setdefault(key, []).extend(value)
    return found


# (elements, attribute names and values, words, element paths), each in document order.
Signature = tuple[int, list[tuple[str, str]], list[str], list[str]]


def _xml_signature(element: ElementTree.Element, parent: str = "") -> Signature:
    """(elements, attributes, words, element paths) under an element, in document order.

    Structured text (XHTML, or text between CWE elements) gives its words, as the
    importer's `#xhtml` does; any other element gives its own attributes, then its
    children's, and its text if it holds no element. Each element also gives its path
    from the field down (`Modes_Of_Introduction/Introduction/Phase`), so an element
    kept under another name, or moved to another parent, does not pass as kept.
    """
    path = element.tag.rpartition("}")[2]
    path = f"{parent}/{path}" if parent else path
    children = list(element)
    mixed = any(not c.tag.startswith(NS) for c in children) or bool(
        children and ((element.text or "").strip() or any((c.tail or "").strip() for c in children))
    )
    attributes = sorted((_attribute(k), v) for k, v in element.attrib.items())
    if mixed or not children:
        return 1, attributes, " ".join(element.itertext()).split(), [path]
    elements, words, paths = 1, [], [path]
    for child in children:
        e, a, w, p = _xml_signature(child, path)
        elements, attributes, words, paths = elements + e, attributes + a, words + w, paths + p
    return elements, attributes, words, paths


def _kept_signature(value: Any, path: str) -> Signature:
    """The same signature, over a value the import kept for the element at `path`."""
    if isinstance(value, str):
        return 1, [], cwe.plain_text(value).split(), [path]
    attributes = sorted((k[1:], v) for k, v in value.items() if k.startswith("@"))
    elements, words, paths = 1, [], [path]
    for key, item in value.items():
        if key in ("#text", "#xhtml"):
            words += cwe.plain_text({key: item}).split()
        elif not key.startswith("@"):
            # `#items` keeps mixed children in order, one {name: value} each.
            parts = (
                (next(iter(one.items())) for one in item)
                if key == "#items"
                else ((key, one) for one in item)
            )
            for name, part in parts:
                e, a, w, p = _kept_signature(part, f"{path}/{name}")
                elements, attributes = elements + e, attributes + a
                words, paths = words + w, paths + p
    return elements, attributes, words, paths


def _joined_signatures(signatures: Iterable[Signature]) -> Signature:
    elements, attributes, words, paths = 0, [], [], []
    for e, a, w, p in signatures:
        elements, attributes, words, paths = elements + e, attributes + a, words + w, paths + p
    return elements, attributes, words, paths


def _first_difference(in_file: list[str], kept: list[str]) -> dict[str, str | None]:
    """The first element path the two sides give differently, for a reader of the report."""
    for a, b in zip_longest(in_file, kept):
        if a != b:
            return {"in_file": a, "kept": b}
    return {"in_file": None, "kept": None}


def _tally(signature: Signature) -> list[int]:
    """[elements, attributes, words], for a reader of the report."""
    return [signature[0], len(signature[1]), len(signature[2])]


# --- small helpers ---------------------------------------------------------------------------


def _attribute(key: str) -> str:
    if key.startswith(XML_NS):
        return f"xml:{key.removeprefix(XML_NS)}"
    if key.startswith(XSI_NS):
        return f"xsi:{key.removeprefix(XSI_NS)}"
    return key.rpartition("}")[2]


def _order(entry_id: str) -> tuple[int, str]:
    number = entry_id.removeprefix("CWE-")
    return (int(number), entry_id) if number.isdigit() else (sys.maxsize, entry_id)


def _view_order(view: int) -> tuple[int, int]:
    return (NAMED_VIEWS.index(view), view) if view in NAMED_VIEWS else (len(NAMED_VIEWS), view)


def _tuple(t: tuple[str, str, str, int]) -> dict[str, Any]:
    return {"source": t[0], "nature": t[1], "target": t[2], "view": f"CWE-{t[3]}"}


def _in_nature_order(natures: Iterable[str]) -> list[str]:
    """Natures in schema order, then membership, then any other by name."""
    rank = {n: i for i, n in enumerate((*cwe.NATURES, *MEMBERSHIP.values()))}
    return sorted(natures, key=lambda n: (rank.get(n, len(rank)), n))


# --- the report as Markdown, and the command ---------------------------------------------------


def to_markdown(report: Mapping[str, Any]) -> str:
    """The report as a page a reviewer reads. The same file always gives the same text."""
    c = report["catalog"]
    e, r, v, f = report["entries"], report["references"], report["views"], report["fields"]
    rel, links = report["relationships"], report["links"]
    total = sum(e["by_kind_in_file"].values())
    missing = _listed(e["missing"] + r["missing"])
    extra = _listed(e["extra"] + r["extra"])
    retyped = f" Read as another kind: {_listed(e['kind_changed'])}." if e["kind_changed"] else ""
    if r["repeated_differently"]:
        retyped += f" Given a different number of times: {_listed(r['repeated_differently'])}."
    lost = _listed([_relation(t) for t in rel["missing"]])
    added = _listed([_relation(t) for t in rel["extra"]])
    recounted = _listed([_relation(t) for t in rel["repeated_differently"]])
    recount = (
        f" Given a different number of times: {recounted}." if rel["repeated_differently"] else ""
    )
    not_kept = _listed([f"{x['entry']} {x['field']}" for x in f["not_kept"]])
    without = v["entries_without_view"]
    deprecated = sum(1 for x in without if x["status"] == "Deprecated")
    implicit = sum(
        1 for x in without if x["status"] != "Deprecated" and x["view_type"] == "Implicit"
    )
    others = len(without) - deprecated - implicit
    unreached = _joined(
        [
            *(
                [f"the {_count(deprecated, 'deprecated entry', 'deprecated entries')}"]
                if deprecated
                else []
            ),
            *(
                [
                    f"the {_count(implicit, 'implicit view', 'implicit views')}, which "
                    + ("picks its" if implicit == 1 else "pick their")
                    + " members with a filter instead of listing them"
                ]
                if implicit
                else []
            ),
            *([_count(others, "other", "others")] if others else []),
        ]
    )
    unknown = _listed([f"{x['kind']}/{x['field']}" for x in f["unknown"]])
    if report["lossless"]:
        verdict = (
            "**Lossless: yes.** Every entry, reference, relationship, field and link in the "
            "file is in the import."
        )
    else:
        verdict = "**Lossless: no.** The sections below name what the import lost."
    lines = [
        f"# CWE import reconciliation: {c['name']} {c['version']}",
        "",
        "Generated by `python -m engine.load.cwe_reconcile` (#146, DL-0058) from the catalog "
        f"file with SHA-256 `{c['sha256']}`: {c['name']} {c['version']} of {c['date']}, written "
        f"to CWE XML Schema {c['schema']}. The file is read twice, through the importer and "
        "with ElementTree alone, and the two readings are compared. Its local name is left out, "
        "so the same file gives the same report wherever it is saved.",
        "",
        verdict,
        "",
        "## Entries",
        "",
        "| Kind | In the file | Imported |",
        "|---|---:|---:|",
        *(
            f"| {kind} | {e['by_kind_in_file'].get(kind, 0):,} | "
            f"{e['by_kind_imported'].get(kind, 0):,} |"
            for kind in ("Weakness", "Category", "View")
        ),
        f"| External_Reference | {r['in_file']:,} | {r['imported']:,} |",
        "",
        f"Missing: {missing}. Extra: {extra}.{retyped}",
        "",
        "PLAN-0002 §5 counted the entries as the union of the entries across the views. "
        f"{_count(v['entries_reached'], 'entry is', 'entries are')} reached by some view's "
        f"relationships. {_count(len(without), 'is', 'are')} reached by none: {unreached}. "
        "An import that took its entries "
        "from the views' relationships would drop them. This import reads the whole catalog, "
        f"so it has all {total:,}. They are listed at the end.",
        "",
        "## Relationships",
        "",
        "| | In the file | Imported |",
        "|---|---:|---:|",
        f"| All | {rel['in_file']:,} | {rel['imported']:,} |",
        "| Distinct (entry, nature, target, view) | "
        f"{rel['distinct_in_file']:,} | {rel['distinct_imported']:,} |",
        "",
        f"Missing: {lost}. Extra: {added}.{recount}",
        "",
        "| Nature | In the file | Imported |",
        "|---|---:|---:|",
        *(
            f"| {nature} | {n['in_file']:,} | {n['imported']:,} |"
            for nature, n in rel["by_nature"].items()
        ),
        "",
        "### By view",
        "",
        "The views PLAN-0002 §5 named come first.",
        "",
        "| View | In the file | Imported |",
        "|---|---:|---:|",
        *(
            f"| {view} | {n['in_file']:,} | {n['imported']:,} |"
            for view, n in rel["by_view"].items()
        ),
        "",
        "## Fields",
        "",
        f"Every field of the {f['checked']:,} entries and references was compared: an "
        "attribute by its value, and any other field by its elements, the names and values "
        "of the attributes inside it, and its words, in order. "
        f"Fields not kept: {not_kept}. Fields the reader does not know: {unknown}.",
        "",
        "| Kind | Field | Entries in the file | Imported | Goes to |",
        "|---|---|---:|---:|---|",
        *(
            f"| {row['kind']} | `{row['field']}` | {row['in_file']:,} | {row['imported']:,} | "
            f"{_destination(row)} |"
            for row in f["rows"]
        ),
        "",
        "## Links",
        "",
        "| Link | In the file | Imported |",
        "|---|---:|---:|",
        *(
            f"| {label} | {links[key]['in_file']:,} | {links[key]['imported']:,} |"
            for key, label in (
                ("attack_pattern_links", "CAPEC links (Related_Attack_Pattern)"),
                ("observed_examples", "Observed examples"),
            )
        ),
        "",
        "## Entries no view reaches",
        "",
    ]
    if v["entries_without_view"]:
        lines += [
            "| Entry | Kind | Status |",
            "|---|---|---|",
            *(
                f"| {x['id']} | {_kind_label(x)} | {x['status']} |"
                for x in v["entries_without_view"]
            ),
        ]
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Reconcile a CWE catalog file: 0 when lossless, 1 on a loss or a stale report, 2 otherwise."""
    parser = argparse.ArgumentParser(
        prog="python -m engine.load.cwe_reconcile",
        description="Prove the CWE import lost nothing from a catalog file (#146).",
    )
    parser.add_argument("file", help="MITRE's cwec_vX.Y.xml.zip, or the XML inside it")
    parser.add_argument("--sha256", default=None, help="refuse any other bytes than these")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    saved = parser.add_mutually_exclusive_group()
    saved.add_argument("--write", metavar="REPORT", help="also save the Markdown report here")
    saved.add_argument(
        "--check", metavar="REPORT", help="fail unless REPORT is the Markdown report this gives"
    )
    args = parser.parse_args(argv)
    try:
        report = reconcile(args.file, args.sha256)
    except cwe.CweError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    markdown = to_markdown(report)
    print(json.dumps(report, indent=2) if args.json else markdown.rstrip("\n"))
    status = 0
    if not report["lossless"]:
        print(
            "error: the import lost something from the file; the report names it", file=sys.stderr
        )
        status = 1
    if args.write:
        Path(args.write).write_text(markdown, encoding="utf-8")
    if args.check:
        try:
            committed = Path(args.check).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {args.check} ({exc.strerror or exc})", file=sys.stderr)
            return 2
        if committed != markdown:
            print(
                f"error: {args.check} is not the report this import gives; "
                f"regenerate it with --write {args.check}",
                file=sys.stderr,
            )
            status = 1
    return status


def _listed(items: list[str]) -> str:
    return ", ".join(items) if items else "none"


def _joined(items: list[str]) -> str:
    """Items in a sentence: a; a and b; a, b, and c."""
    if len(items) < 3:
        return " and ".join(items) if items else "none"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _count(n: int, one: str, many: str) -> str:
    """A number and its noun: 1 entry, 2 entries."""
    return f"{n:,} {one if n == 1 else many}"


def _relation(t: Mapping[str, Any]) -> str:
    return f"{t['source']} {t['nature']} {t['target']} in {t['view']}"


def _kind_label(entry: Mapping[str, Any]) -> str:
    """An entry's kind, with a view's type: View (Implicit)."""
    return f"{entry['kind']} ({entry['view_type']})" if entry["view_type"] else entry["kind"]


def _destination(row: Mapping[str, Any]) -> str:
    if row["maps_to"]:
        return row["maps_to"]
    return "kept on the entry" if row["known"] else "kept; not known to the reader"


if __name__ == "__main__":
    sys.exit(main())
