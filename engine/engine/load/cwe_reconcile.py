"""Prove the CWE import lost nothing (#146; PLAN-0002 §5's acceptance test).

The catalog file is read twice: once through the importer (`cwe.load_catalog`), and
once more with ElementTree alone, with none of the importer's code. The two readings
are compared:

- **entries**: every Weakness, Category and View in the file is imported as many times
  as the file gives it, with its own kind and id, and every External_Reference id as
  many times as the file defines it. PLAN-0002 §5 named "the union of entries across the
  three views", which the report gives on its own. The import reads the whole catalog
  (#61, question 1), so the report also counts the entries that no view's relationships
  reach, which a view-by-view import would drop;
- **relationships**: the (entry, nature, target, view, ordinal, chain) tuples the file
  writes, as a Related_Weakness or a Has_Member or Member_Of, equal the ones the import
  keeps (#145), each as many times as the file writes it, all together and view by view;
- **fields**: for each copy of each entry and reference, and each of its fields, what the
  file holds equals what was kept: an attribute's value exactly, and any other field
  element by element, in order, structured text (XHTML) included: each element's name
  and path, the names and values of its attributes, and its own text. A field the reader
  does not know is kept, not lost, and is flagged;
- **links**: every CAPEC link and observed example in the file is read, and the ones the
  import serves (`attack_patterns`, `observed_examples`) hold the file's values.

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
import re
import sys
import zipfile
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
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
WHOLE_NUMBER = re.compile(r"[0-9]+")  # ASCII digits only
# A relationship as the file writes it: (entry, nature, target, view, Ordinal, Chain_ID).
Relation = tuple[str, str, str, int, str | None, str | None]
# One element of a field: (path from the field down, attributes by name, its own text).
Item = tuple[str, tuple[tuple[str, str], ...], tuple[str, ...]]


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
    """What the file holds, copy by copy in file order: entries, references, relationships,
    fields and links. Nothing is keyed by id, so an id given twice keeps both copies."""
    entries: list[tuple[str, str, str | None, str | None]] = []  # (id, kind, Status, Type)
    elements: list[tuple[str, str, ElementTree.Element]] = []  # (id, kind, the element)
    references: list[str] = []
    relationships: list[Relation] = []
    capec: list[tuple[str, list[str]]] = []  # (entry, its CAPEC_IDs as written)
    examples: list[tuple[str, list[dict[str, str | None]]]] = []  # (entry, its examples)
    for container in root:
        name = container.tag.removeprefix(NS)
        if name == "External_References":
            for reference in container:
                reference_id = reference.get("Reference_ID", "")
                references.append(reference_id)
                elements.append((reference_id, "External_Reference", reference))
            continue
        kind = KINDS.get(name)
        for entry in container if kind is not None else ():
            entry_id = f"CWE-{int(entry.get('ID', '-1'))}"
            entries.append((entry_id, kind, entry.get("Status"), entry.get("Type")))
            elements.append((entry_id, kind, entry))
            for holder in entry.findall(NS + RELATIONSHIP_FIELDS[kind]):
                for child in holder:
                    tag = child.tag.removeprefix(NS)
                    nature = (
                        child.get("Nature") if tag == "Related_Weakness" else MEMBERSHIP.get(tag)
                    )
                    if nature is None:
                        continue  # not a relationship: the field tallies still count it
                    chain = child.get("Chain_ID") or None  # a named chain: 692 is CWE-692
                    relationships.append(
                        (
                            entry_id,
                            nature,
                            f"CWE-{int(child.get('CWE_ID', '-1'))}",
                            int(child.get("View_ID", "-1")),
                            child.get("Ordinal") or None,
                            f"CWE-{int(chain)}"
                            if chain and WHOLE_NUMBER.fullmatch(chain)
                            else chain,
                        )
                    )
            patterns = entry.findall(f"{NS}Related_Attack_Patterns/{NS}Related_Attack_Pattern")
            capec.append((entry_id, [p.get("CAPEC_ID", "") for p in patterns]))
            observed = entry.findall(f"{NS}Observed_Examples/{NS}Observed_Example")
            examples.append((entry_id, [_example(e) for e in observed]))
    return {
        "entries": entries,
        "elements": elements,
        "references": references,
        "relationships": relationships,
        "capec": capec,
        "examples": examples,
    }


def _example(example: ElementTree.Element) -> dict[str, str | None]:
    """An Observed_Example as the app reads it: the text of its first Reference,
    Description and Link, each run of whitespace one space, and no Link as None."""

    def text(name: str) -> str:
        found = example.find(NS + name)
        return _words(" ".join(found.itertext())) if found is not None else ""

    return {
        "reference": text("Reference"),
        "description": text("Description"),
        "link": text("Link") or None,
    }


# --- the comparison ------------------------------------------------------------------------


def _report(catalog: cwe.CweCatalog, source: Mapping[str, Any]) -> dict[str, Any]:
    imported = [*catalog.weaknesses, *catalog.categories, *catalog.views]  # every copy
    kept_references = [r.get("@Reference_ID", "") for r in catalog.references]
    entries = _entries(source["entries"], imported, source["references"], kept_references)
    relationships = _relationships(source["relationships"], catalog.stated_relationships)
    kept_fields = [(e.id, e.fields) for e in imported] + [
        (r.get("@Reference_ID", ""), r) for r in catalog.references
    ]
    fields = _fields(source["elements"], kept_fields)
    views = _views(source["entries"], source["relationships"], imported)
    links = _links(source, imported, catalog.links()["attack_pattern_links"])
    # Equal totals are not enough on their own: one relationship can lose a copy while
    # another gains one, and two entries can trade kinds (#249 review). Nor are equal
    # tallies: text can move to the next element, an attribute inside XHTML can go, a
    # typed link can change and a second copy can hide behind an id (#249, second
    # review). So each tuple, entry and reference id must be kept as many times as the
    # file gives it, each entry with its own kind, each element of each copy as the file
    # holds it, and each link the import serves with the file's values.
    lossless = (
        not any(entries[k]["missing"] or entries[k]["extra"] for k in ("entries", "references"))
        and entries["entries"]["by_kind_in_file"] == entries["entries"]["by_kind_imported"]
        and not entries["entries"]["kind_changed"]
        and not entries["entries"]["repeated_differently"]
        and entries["references"]["in_file"] == entries["references"]["imported"]
        and not entries["references"]["repeated_differently"]
        and not views["named"]["missing"]
        and not relationships["missing"]
        and not relationships["extra"]
        and relationships["in_file"] == relationships["imported"]
        and not relationships["repeated_differently"]
        and not fields["not_kept"]
        and all(
            link["in_file"] == link["imported"] and not link["values_differ"]
            for link in links.values()
        )
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
    in_file: Sequence[tuple[str, str, str | None, str | None]],
    imported: Sequence[cwe.CweEntry],
    references: list[str],
    kept_references: list[str],
) -> dict[str, Any]:
    file_ids, kept_ids = Counter(i for i, *_ in in_file), Counter(e.id for e in imported)
    file_kinds: dict[str, Counter[str]] = {}
    kept_kinds: dict[str, Counter[str]] = {}
    for entry_id, kind, *_ in in_file:
        file_kinds.setdefault(entry_id, Counter())[kind] += 1
    for entry in imported:
        kept_kinds.setdefault(entry.id, Counter())[entry.kind] += 1
    both = set(file_ids) & set(kept_ids)
    file_references, kept_reference_ids = Counter(references), Counter(kept_references)
    return {
        "entries": {
            "by_kind_in_file": dict(Counter(kind for _, kind, *_ in in_file)),
            "by_kind_imported": dict(Counter(e.kind for e in imported)),
            "missing": sorted(set(file_ids) - set(kept_ids), key=_order),
            "extra": sorted(set(kept_ids) - set(file_ids), key=_order),
            "kind_changed": sorted(
                (i for i in both if file_ids[i] == kept_ids[i] and file_kinds[i] != kept_kinds[i]),
                key=_order,
            ),
            # an entry the file gives more or fewer times than the import keeps it
            "repeated_differently": sorted(
                (i for i in both if file_ids[i] != kept_ids[i]), key=_order
            ),
        },
        "references": {
            "in_file": len(references),
            "imported": len(kept_references),
            "missing": sorted(set(references) - set(kept_references)),
            "extra": sorted(set(kept_references) - set(references)),
            # an id the file defines more or fewer times than the import keeps it
            "repeated_differently": sorted(
                i
                for i in set(file_references) & set(kept_reference_ids)
                if file_references[i] != kept_reference_ids[i]
            ),
        },
    }


def _views(
    in_file: Sequence[tuple[str, str, str | None, str | None]],
    relationships: Sequence[Relation],
    imported: Sequence[cwe.CweEntry],
) -> dict[str, Any]:
    """The entries the views' relationships reach: across every view, and across the three
    PLAN-0002 §5 named, whose union is its acceptance test (#146)."""
    first: dict[str, tuple[str, str | None, str | None]] = {}  # each entry's first copy
    for entry_id, *rest in in_file:
        first.setdefault(entry_id, (rest[0], rest[1], rest[2]))
    reached = {t[0] for t in relationships} | {t[2] for t in relationships}
    named = {x for t in relationships if t[3] in NAMED_VIEWS for x in (t[0], t[2])} & set(first)
    kept = {e.id for e in imported}
    return {
        "entries_reached": len(reached & set(first)),
        "entries_without_view": [
            {"id": i, "kind": kind, "status": status, "view_type": view_type}
            for i, (kind, status, view_type) in sorted(first.items(), key=lambda e: _order(e[0]))
            if i not in reached
        ],
        "named": {
            "views": [f"CWE-{view}" for view in NAMED_VIEWS],
            "entries_reached": len(named),
            "imported": len(named & kept),
            "missing": sorted(named - kept, key=_order),
        },
    }


def _relationships(in_file: list[Relation], imported: Iterable[cwe.Relationship]) -> dict[str, Any]:
    kept = [(r.source, r.nature, r.target, r.view, r.ordinal, r.chain) for r in imported]
    file_count, kept_count = Counter(in_file), Counter(kept)
    file_natures = Counter(t[1] for t in in_file)
    kept_natures = Counter(t[1] for t in kept)
    views = sorted({t[3] for t in in_file} | {t[3] for t in kept}, key=_view_order)
    return {
        "in_file": len(in_file),
        "imported": len(kept),
        "distinct_in_file": len(file_count),
        "distinct_imported": len(kept_count),
        "missing": [_tuple(t) for t in sorted(set(file_count) - set(kept_count), key=_by_tuple)],
        "extra": [_tuple(t) for t in sorted(set(kept_count) - set(file_count), key=_by_tuple)],
        "repeated_differently": [
            {**_tuple(t), "in_file": file_count[t], "imported": kept_count[t]}
            for t in sorted(set(file_count) & set(kept_count), key=_by_tuple)
            if file_count[t] != kept_count[t]
        ],
        "by_nature": {
            nature: {"in_file": file_natures[nature], "imported": kept_natures[nature]}
            for nature in _in_nature_order(file_natures | kept_natures)
        },
        "by_view": {
            f"CWE-{view}": {
                "in_file": sum(1 for t in in_file if t[3] == view),
                "imported": sum(1 for t in kept if t[3] == view),
            }
            for view in views
        },
    }


def _links(
    source: Mapping[str, Any], imported: Sequence[cwe.CweEntry], capec_imported: int
) -> dict[str, Any]:
    """Each CAPEC link and observed example: counted, and, copy by copy, compared with the
    values the import serves (`attack_patterns`, `observed_examples`)."""
    served = [(e.id, e) for e in imported]
    capec_differ = []
    for entry_id, copy, ids, entry in _paired(source["capec"], served):
        # what the importer serves: CAPEC-<n>, in file order, a link given twice once
        wanted = list(
            dict.fromkeys(f"CAPEC-{int(i)}" if WHOLE_NUMBER.fullmatch(i) else i for i in ids)
        )
        if wanted != list(entry.attack_patterns):
            capec_differ.append(
                {
                    "entry": entry_id,
                    **copy,
                    "in_file": wanted,
                    "imported": list(entry.attack_patterns),
                }
            )
    examples_differ = []
    for entry_id, copy, wanted, entry in _paired(source["examples"], served):
        kept = [
            {"reference": x.reference, "description": x.description, "link": x.link}
            for x in entry.observed_examples
        ]
        for number, (a, b) in enumerate(zip_longest(wanted, kept), start=1):
            if a != b:
                examples_differ.append(
                    {"entry": entry_id, **copy, "number": number, "in_file": a, "imported": b}
                )
    return {
        "attack_pattern_links": {
            "in_file": sum(len(ids) for _, ids in source["capec"]),
            "imported": capec_imported,
            "values_differ": capec_differ,
        },
        "observed_examples": {
            "in_file": sum(len(found) for _, found in source["examples"]),
            "imported": sum(len(e.observed_examples) for e in imported),
            "values_differ": examples_differ,
        },
    }


def _paired(
    in_file: Iterable[tuple[str, Any]], kept: Iterable[tuple[str, Any]]
) -> Iterator[tuple[str, dict[str, int], Any, Any]]:
    """Each copy the file gives with the same copy the import keeps: first with first.

    A copy only one side has is left out, since the entries and references sections name
    it. `copy` (from 1) is given only for an id the file gives more than once.
    """
    in_file = list(in_file)
    copies: dict[str, list[Any]] = {}
    for item_id, value in kept:
        copies.setdefault(item_id, []).append(value)
    total = Counter(item_id for item_id, _ in in_file)
    seen: Counter[str] = Counter()
    for item_id, value in in_file:
        number = seen[item_id]
        seen[item_id] += 1
        held = copies.get(item_id, [])
        if number < len(held):
            copy = {"copy": number + 1} if total[item_id] > 1 else {}
            yield item_id, copy, value, held[number]


def _fields(
    elements: Sequence[tuple[str, str, ElementTree.Element]],
    kept: Sequence[tuple[str, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Field by field, for every copy of every entry and reference: what the file holds
    against what was kept, element by element."""
    not_kept: list[dict[str, Any]] = []
    carried: Counter[tuple[str, str]] = Counter()
    kept_carried: Counter[tuple[str, str]] = Counter()
    pairs = _paired(((i, (kind, element)) for i, kind, element in elements), kept)
    for item_id, copy, (kind, element), fields in pairs:
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
                            **copy,
                            "field": name,
                            "in_file": in_file.get(name),
                            "kept": held.get(name),
                        }
                    )
                continue
            file_items = [i for e in in_file.get(name, []) for i in _xml_items(e)]
            kept_items = [i for v in held.get(name, []) for i in _kept_items(v, name)]
            file_side, kept_side = _tallies(file_items), _tallies(kept_items)
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
            if not differs and file_items != kept_items:
                # every tally agrees, but an element holds another element's text or
                # attributes: Phase's text in the Note beside it (#249, second review)
                differs = ["placement"]
            if differs:
                loss = {
                    "entry": item_id,
                    **copy,
                    "field": name,
                    "differs": differs,
                    "in_file": {"values": counts[0], "tally": _tally(file_side)},
                    "kept": {"values": counts[1], "tally": _tally(kept_side)},
                    "first_difference": _first_item_difference(file_items, kept_items),
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


def _xml_items(element: ElementTree.Element, parent: str = "") -> list[Item]:
    """Every element of a field, the field's own element first, in document order.

    Each gives its path from the field down (`Modes_Of_Introduction/Introduction/Phase`),
    its attributes by name and value, and the text it holds itself, each run of
    whitespace one space: a leaf its text, and an element holding only elements none.
    Structured text (XHTML, or text between CWE elements), which the importer keeps as
    `#xhtml`, gives the text before its first child and after each child, and each
    element inside it gives its own in the same way. So text moved to another element,
    or an attribute dropped inside XHTML, does not pass as kept (#249, second review).
    """
    path = _path(parent, element.tag)
    children = list(element)
    mixed = any(not c.tag.startswith(NS) for c in children) or bool(
        children and ((element.text or "").strip() or any((c.tail or "").strip() for c in children))
    )
    if mixed:
        return _markup_items(element, path)
    if not children:
        return [(path, _attributes(element), (_words(element.text),))]
    items: list[Item] = [(path, _attributes(element), ())]
    for child in children:
        items += _xml_items(child, path)
    return items


def _markup_items(element: ElementTree.Element, path: str) -> list[Item]:
    """Structured text's elements, in document order, each with its own pieces of text."""
    texts = (_words(element.text), *(_words(child.tail) for child in element))
    items: list[Item] = [(path, _attributes(element), texts)]
    for child in element:
        items += _markup_items(child, _path(path, child.tag))
    return items


def _kept_items(value: Any, path: str) -> list[Item]:
    """The same items, over a value the import kept for the element at `path` (DL-0050).

    An `#xhtml` value is markup the importer wrote; it is read back as elements, so
    each element inside it is compared, attributes and all.
    """
    if isinstance(value, str):
        return [(path, (), (_words(value),))]
    attributes = tuple(sorted((k[1:], v) for k, v in value.items() if k.startswith("@")))
    if "#xhtml" in value:
        root = _markup(value["#xhtml"])
        if root is None:  # not markup that reads back: as one text, it cannot pass as kept
            return [(path, attributes, (_words(value["#xhtml"]),))]
        texts = (_words(root.text), *(_words(child.tail) for child in root))
        items: list[Item] = [(path, attributes, texts)]
        for child in root:
            items += _markup_items(child, _path(path, child.tag))
        return items
    children: list[tuple[str, Any]] = []
    for key, item in value.items():
        if key == "#items":  # mixed children in order, one {name: value} each
            children += [next(iter(one.items())) for one in item]
        elif not key.startswith(("@", "#")):
            children += [(key, one) for one in item]
    if not children:
        return [(path, attributes, (_words(value.get("#text", "")),))]
    items = [(path, attributes, ())]
    for name, part in children:
        items += _kept_items(part, f"{path}/{name}")
    return items


def _markup(markup: str) -> ElementTree.Element | None:
    """The importer's `#xhtml` read back as elements under one root, or None if it does not
    parse. Its names are local, and `xml:` and `xsi:` attributes keep their prefix."""
    try:
        return ElementTree.fromstring(f'<r xmlns:xsi="{XSI_NS[1:-1]}">{markup}</r>')
    except ElementTree.ParseError:
        return None


# (elements, attribute names and values, words, element paths), from the items in order.
Signature = tuple[int, list[tuple[str, str]], list[str], list[str]]


def _tallies(items: Sequence[Item]) -> Signature:
    """What a reader counts: the elements, their attributes, their words and their paths."""
    return (
        len(items),
        [attribute for _, attributes, _ in items for attribute in attributes],
        [word for _, _, texts in items for text in texts for word in text.split()],
        [path for path, _, _ in items],
    )


def _first_item_difference(in_file: Sequence[Item], kept: Sequence[Item]) -> dict[str, Any]:
    """The first element the two sides give differently, for a reader of the report."""
    for a, b in zip_longest(in_file, kept):
        if a != b:
            return {"in_file": _item(a), "kept": _item(b)}
    return {"in_file": None, "kept": None}


def _item(item: Item | None) -> dict[str, Any] | None:
    if item is None:
        return None
    path, attributes, texts = item
    return {"path": path, "attributes": dict(attributes), "text": list(texts)}


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


def _attributes(element: ElementTree.Element) -> tuple[tuple[str, str], ...]:
    """An element's attributes by name and value; their order is not kept (DL-0058 choice 2)."""
    return tuple(sorted((_attribute(k), v) for k, v in element.attrib.items()))


def _path(parent: str, tag: str) -> str:
    name = tag.rpartition("}")[2]
    return f"{parent}/{name}" if parent else name


def _words(text: str | None) -> str:
    """Text with each run of whitespace one space, as both readings keep it."""
    return " ".join((text or "").split())


def _order(entry_id: str) -> tuple[int, str]:
    number = entry_id.removeprefix("CWE-")
    return (int(number), entry_id) if number.isdigit() else (sys.maxsize, entry_id)


def _view_order(view: int) -> tuple[int, int]:
    return (NAMED_VIEWS.index(view), view) if view in NAMED_VIEWS else (len(NAMED_VIEWS), view)


def _tuple(t: Relation) -> dict[str, Any]:
    return {
        "source": t[0],
        "nature": t[1],
        "target": t[2],
        "view": f"CWE-{t[3]}",
        "ordinal": t[4],
        "chain": t[5],
    }


def _by_tuple(t: Relation) -> tuple[str, str, str, int, str, str]:
    """Relationships in tuple order, with no Ordinal or Chain_ID before any."""
    return (t[0], t[1], t[2], t[3], t[4] or "", t[5] or "")


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
    if e["repeated_differently"] or r["repeated_differently"]:
        recounted_ids = _listed(e["repeated_differently"] + r["repeated_differently"])
        retyped += f" Given a different number of times: {recounted_ids}."
    lost = _listed([_relation(t) for t in rel["missing"]])
    added = _listed([_relation(t) for t in rel["extra"]])
    recounted = _listed([_relation(t) for t in rel["repeated_differently"]])
    recount = (
        f" Given a different number of times: {recounted}." if rel["repeated_differently"] else ""
    )
    not_kept = _listed([f"{_copy(x)} {x['field']}" for x in f["not_kept"]])
    capec_differ = _listed([_copy(x) for x in links["attack_pattern_links"]["values_differ"]])
    examples_differ = _listed(
        [f"{_copy(x)} example {x['number']}" for x in links["observed_examples"]["values_differ"]]
    )
    named = v["named"]
    named_views = _joined(named["views"])
    named_kept = (
        "the import has all of them"
        if not named["missing"]
        else f"the import is missing {_listed(named['missing'])}"
    )
    without = v["entries_without_view"]
    deprecated = sum(1 for x in without if x["status"] == "Deprecated")
    deprecated_views = sum(
        1 for x in without if x["status"] == "Deprecated" and x["view_type"] == "Implicit"
    )
    implicit = sum(
        1 for x in without if x["status"] != "Deprecated" and x["view_type"] == "Implicit"
    )
    others = len(without) - deprecated - implicit
    # the implicit views that are deprecated are counted with the deprecated entries, so
    # the rest are the "other" implicit views (#249, second review)
    other = "other " if deprecated_views else ""
    among = _count(deprecated_views, "of them an implicit view", "of them implicit views")
    unreached = _joined(
        [
            *(
                [
                    f"the {_count(deprecated, 'deprecated entry', 'deprecated entries')}"
                    + (f" ({among})" if deprecated_views else "")
                ]
                if deprecated
                else []
            ),
            *(
                [
                    f"the {_count(implicit, f'{other}implicit view', f'{other}implicit views')}, "
                    + ("which picks its" if implicit == 1 else "which pick their")
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
        "PLAN-0002 §5's test counts the entries as the union of the entries across the three "
        f"views it names, {named_views}: their relationships reach "
        f"{_count(named['entries_reached'], 'entry', 'entries')}, and {named_kept}. "
        "Across all the views, "
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
        "| Distinct (entry, nature, target, view, ordinal, chain) | "
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
        f"Every field of the {f['checked']:,} entries and references was compared, copy by "
        "copy: an attribute by its value, and any other field element by element, in order, "
        "its structured text (XHTML) included: each element's name and path, the names and "
        "values of its attributes, and its own text. "
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
        "Each link is also compared with the one the import serves, entry by entry: the CAPEC "
        "ids, and each observed example's reference, description and link. "
        f"CAPEC links kept with other values: {capec_differ}. "
        f"Observed examples kept with other values: {examples_differ}.",
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
    """A relationship in a sentence: CWE-79 ChildOf CWE-74 in CWE-1000 (ordinal Primary)."""
    held = [f"{key} {t[key]}" for key in ("ordinal", "chain") if t.get(key)]
    detail = f" ({', '.join(held)})" if held else ""
    return f"{t['source']} {t['nature']} {t['target']} in {t['view']}{detail}"


def _copy(x: Mapping[str, Any]) -> str:
    """An entry or reference id, with its copy when the file gives the id more than once."""
    return f"{x['entry']} (copy {x['copy']})" if "copy" in x else x["entry"]


def _kind_label(entry: Mapping[str, Any]) -> str:
    """An entry's kind, with a view's type: View (Implicit)."""
    return f"{entry['kind']} ({entry['view_type']})" if entry["view_type"] else entry["kind"]


def _destination(row: Mapping[str, Any]) -> str:
    if row["maps_to"]:
        return row["maps_to"]
    return "kept on the entry" if row["known"] else "kept; not known to the reader"


if __name__ == "__main__":
    sys.exit(main())
