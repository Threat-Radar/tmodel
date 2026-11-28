"""Read MITRE's CAPEC list into typed entries, keeping every field (#244, for #236).

Input is the CAPEC list as MITRE publishes it, `capec_vX.Y.xml`, written to CAPEC XML
Schema 3 (namespace `http://capec.mitre.org/capec-3`; release 3.9 names schema 3.5).
Which release the engine reads is the library's call: its `capec` record pins the
file's SHA-256, and `load_catalog` refuses any other bytes.

It is built the way the CWE reader is (`engine.load.cwe`, DL-0050) and reuses its
bounded read and its element-to-value rules, so the two catalogs come out in one
shape. Every element and attribute of an entry is kept in `CapecEntry.fields`.
`CapecCatalog.report()` says, field by field, where each entry field goes in the
object model and how many entries carry it, and `CapecCatalog.unknown` lists any
entry field this reader does not know, such as one a newer schema adds. Nothing is
dropped silently.

`to_objects()` maps the attack patterns onto the accepted object model (ADR-0010,
ADR-0011): one AttackPattern per CAPEC attack pattern, and a proposed Assertion for
each CWE weakness CAPEC relates it to (DL-0056).

References: an entry cites an External_Reference by its id, and `CapecCatalog.citations`
resolves each citation to the reference's title, authors, publication and URL, for the
details view (#236). A reference defined twice makes the file unreadable, as an entry id
given twice does. A citation of a reference the release does not define (in 3.9,
CAPEC-244 cites REF-97) and a related attack pattern the release does not have are
listed in `CapecCatalog.links()` and kept, not refused.

Read-only and deterministic: the same bytes give the same entries in the same order,
and nothing is written anywhere.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import threading
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import MappingProxyType
from typing import Any
from xml.etree import ElementTree

from engine.load import cwe
from engine.load.cwe import plain_text

CAPEC_NS = "http://capec.mitre.org/capec-3"  # CAPEC XML Schema 3.x
# Names the CAPEC catalog file the engine reads (the library record pins its digest).
CATALOG_ENV = "TMODEL_CAPEC_CATALOG"
# The library record that pins the release: content.url and content.sha256.
LIBRARY_RECORD = "capec"
# The 3.9 XML is 3.8 MB. A file larger than this is refused before any of it is read.
MAX_FILE_BYTES = 64 * 1024 * 1024
TERMS_URL = "https://capec.mitre.org/about/termsofuse.html"
# The licence on that page (last reviewed 2019-04-04), which a copy of CAPEC content reproduces.
LICENSE = (
    "The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license "
    "to use Common Attack Pattern Enumeration and Classification (CAPEC™) for research, "
    "development, and commercial purposes. Any copy you make for such purposes is "
    "authorized provided that you reproduce MITRE’s copyright designation and this license "
    "in any such copy."
)
DEFINITION_URL = "https://capec.mitre.org/data/definitions/{number}.html"

# The containers under Attack_Pattern_Catalog, in schema order, with the entry each holds.
CONTAINERS = (
    ("Attack_Patterns", "Attack_Pattern"),
    ("Categories", "Category"),
    ("Views", "View"),
    ("External_References", "External_Reference"),
)
# Each entry's own fields in CAPEC XML Schema 3.5 (ap_schema_v3.5.xsd), attributes
# first, then child elements in schema order. A field outside these lists is still
# kept, and is reported in CapecCatalog.unknown.
ENTRY_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "Attack_Pattern": (
            "@ID",
            "@Name",
            "@Abstraction",
            "@Status",
            "Description",
            "Extended_Description",
            "Alternate_Terms",
            "Likelihood_Of_Attack",
            "Typical_Severity",
            "Related_Attack_Patterns",
            "Execution_Flow",
            "Prerequisites",
            "Skills_Required",
            "Resources_Required",
            "Indicators",
            "Consequences",
            "Mitigations",
            "Example_Instances",
            "Related_Weaknesses",
            "Taxonomy_Mappings",
            "References",
            "Notes",
            "Content_History",
        ),
        "Category": (
            "@ID",
            "@Name",
            "@Status",
            "Summary",
            "Relationships",
            "Taxonomy_Mappings",
            "References",
            "Notes",
            "Content_History",
        ),
        "View": (
            "@ID",
            "@Name",
            "@Type",
            "@Status",
            "Objective",
            "Audience",
            "Members",
            "Filter",
            "References",
            "Notes",
            "Content_History",
        ),
        "External_Reference": (
            "@Reference_ID",
            "Author",
            "Title",
            "Edition",
            "Publication",
            "Publication_Year",
            "Publication_Month",
            "Publication_Day",
            "Publisher",
            "URL",
            "URL_Date",
        ),
    }
)
# Where an entry field goes in the object model (ADR-0010 core, ADR-0011; DL-0056).
# Every other field stays on the entry only, kept whole in CapecEntry.fields.
MAPPED: Mapping[tuple[str, str], str] = MappingProxyType(
    {
        ("Attack_Pattern", "@ID"): "AttackPattern.id, AttackPattern.catalog_ref",
        ("Attack_Pattern", "@Name"): "AttackPattern.name",
        ("Attack_Pattern", "Description"): "AttackPattern.description",
        ("Attack_Pattern", "Related_Weaknesses"): "Assertion: Weakness exploited_by AttackPattern",
    }
)
# The organization every imported Assertion is attributed to, as the CWE import does.
MITRE_PARTY = "party:mitre-capec"
SCHEMA_FILE = re.compile(r"ap_schema_v([0-9][0-9.]*)\.xsd$")
WHOLE_NUMBER = re.compile(r"[0-9]+")  # ASCII digits only, so int() always accepts it
# An ATT&CK technique as CAPEC's Taxonomy_Mapping writes it, without the leading T.
ATTACK_ENTRY = re.compile(r"[0-9]{4}(\.[0-9]{3})?")
_LABELS = {"Attack_Pattern": "an attack pattern", "Category": "a category", "View": "a view"}


class CapecError(ValueError):
    """The catalog cannot be read: other bytes than the pinned ones, not CAPEC, bad XML."""


@dataclass(frozen=True)
class CapecEntry:
    """One Attack_Pattern, Category or View. `fields` keeps every field of the entry, read-only."""

    kind: str  # Attack_Pattern, Category or View
    number: int
    name: str
    status: str
    # Plain text: an attack pattern's Description, a category's Summary, a view's Objective.
    description: str
    fields: Mapping[str, Any] = field(compare=False, repr=False)
    abstraction: str | None = None  # attack patterns: Meta, Standard or Detailed
    view_type: str | None = None  # views: Implicit, Explicit or Graph
    likelihood: str | None = None  # Likelihood_Of_Attack
    severity: str | None = None  # Typical_Severity
    alternate_terms: tuple[str, ...] = ()
    related_attack_patterns: tuple[tuple[str, str], ...] = ()  # (nature, CAPEC id), file order
    weaknesses: tuple[str, ...] = ()  # CWE ids such as CWE-89, in file order
    attack_techniques: tuple[str, ...] = ()  # ATT&CK ids such as T1574.010, in file order
    steps: int = 0  # Execution_Flow entries (Attack_Step)
    mitigations: int = 0  # Mitigations entries
    examples: int = 0  # Example_Instances entries

    @property
    def id(self) -> str:
        return f"CAPEC-{self.number}"

    @property
    def url(self) -> str:
        return DEFINITION_URL.format(number=self.number)

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready, in a fixed key order, with every field under `fields`."""
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "status": self.status,
            "abstraction": self.abstraction,
            "view_type": self.view_type,
            "likelihood": self.likelihood,
            "severity": self.severity,
            "description": self.description,
            "alternate_terms": list(self.alternate_terms),
            "related_attack_patterns": [
                {"nature": nature, "id": capec} for nature, capec in self.related_attack_patterns
            ],
            "weaknesses": list(self.weaknesses),
            "attack_techniques": list(self.attack_techniques),
            "steps": self.steps,
            "mitigations": self.mitigations,
            "examples": self.examples,
            "url": self.url,
            "fields": cwe._thawed(self.fields),
        }


@dataclass(frozen=True)
class CapecCatalog:
    """One CAPEC release: its entries in file order, and what the reader found in them."""

    name: str
    version: str
    date: str
    schema: str | None  # the schema version its xsi:schemaLocation names, such as 3.5
    file: str  # the file's name only, so an answer names no local path
    sha256: str  # of the file as read
    attack_patterns: tuple[CapecEntry, ...]
    categories: tuple[CapecEntry, ...]
    views: tuple[CapecEntry, ...]
    references: tuple[Mapping[str, Any], ...]  # External_Reference fields, in file order
    field_counts: tuple[tuple[str, str, int], ...]  # (kind, field, entries carrying it)
    unknown: tuple[tuple[str, int], ...] = ()  # ("Kind/Field", entries) the reader does not know

    @cached_property
    def _by_number(self) -> Mapping[int, CapecEntry]:
        entries = (*self.attack_patterns, *self.categories, *self.views)
        return MappingProxyType({e.number: e for e in entries})

    def get(self, capec_id: str | int) -> CapecEntry | None:
        """The entry with this id: `CAPEC-66`, `capec-66`, `66` or 66."""
        number = _number(capec_id)
        return self._by_number.get(number) if number is not None else None

    def report(self) -> list[dict[str, Any]]:
        """One row per entry field: how many entries carry it, and where it goes.

        `maps_to` names the object model slot or Assertion a field becomes, or is None
        for a field kept only on the entry. A field the reader does not know comes
        last, with `known` false.
        """
        counts = {(kind, name): n for kind, name, n in self.field_counts}
        rows = [
            {
                "kind": kind,
                "field": name,
                "entries": counts.get((kind, name), 0),
                "maps_to": MAPPED.get((kind, name)),
                "known": True,
            }
            for kind, names in ENTRY_FIELDS.items()
            for name in names
        ]
        for path, n in self.unknown:
            kind, _, name = path.partition("/")
            rows.append(
                {"kind": kind, "field": name, "entries": n, "maps_to": None, "known": False}
            )
        return rows

    @cached_property
    def _references_by_id(self) -> Mapping[str, Mapping[str, Any]]:
        return MappingProxyType({str(r.get("@Reference_ID", "")): r for r in self.references})

    def citations(self, entry: CapecEntry) -> list[dict[str, Any]]:
        """The references an entry cites, each resolved to what it is (#236's details view).

        One item per Reference in the entry's References, in file order: the reference
        id and the cited section, then the reference's title, authors, edition,
        publication, publisher, publication date (year, month and day as CAPEC writes
        them) and URL with the date it was accessed. Every item has every key. A
        citation of a reference this release does not define has `resolved` false and
        the reference's keys empty.
        """
        return [
            _citation(cited, self._references_by_id.get(_cited_id(cited)))
            for cited in cwe._items(entry.fields, "References", "Reference")
        ]

    def links(self) -> dict[str, Any]:
        """What became of CAPEC's links (DL-0056), naming each one not mapped.

        A Related_Weakness becomes an `exploited_by` Assertion when its CWE_ID is a
        whole number; the others stay on their entry and are listed here. A weakness
        CAPEC gives twice for one attack pattern becomes one Assertion, and is listed
        too. Links between attack patterns and taxonomy mappings stay on their
        entries, and are counted by kind. A link to an attack pattern the release does
        not have, and a citation of a reference it does not define, are listed: they
        are kept on their entry, not refused.
        """
        given = [
            (p.id, str(w.get("@CWE_ID", "")))
            for p in self.attack_patterns
            for w in cwe._items(p.fields, "Related_Weaknesses", "Related_Weakness")
        ]
        mapped = Counter((p, f"CWE-{int(raw)}") for p, raw in given if WHOLE_NUMBER.fullmatch(raw))
        related = [
            (p.id, str(r.get("@Nature", "")), str(r.get("@CAPEC_ID", "")))
            for p in self.attack_patterns
            for r in cwe._items(p.fields, "Related_Attack_Patterns", "Related_Attack_Pattern")
        ]
        cited = [
            (e.id, _cited_id(c), c.get("@Section"))
            for e in (*self.attack_patterns, *self.categories, *self.views)
            for c in cwe._items(e.fields, "References", "Reference")
        ]
        return {
            "weakness_links": len(given),
            "weakness_links_without_cwe_id": [
                {"attack_pattern": p, "cwe_id": raw}
                for p, raw in given
                if not WHOLE_NUMBER.fullmatch(raw)
            ],
            "weakness_links_repeated": [
                {"attack_pattern": p, "weakness": w, "times": n}
                for (p, w), n in mapped.items()
                if n > 1
            ],
            "attack_pattern_links": dict(
                sorted(
                    Counter(
                        nature
                        for p in self.attack_patterns
                        for nature, _ in p.related_attack_patterns
                    ).items()
                )
            ),
            "attack_pattern_links_unresolved": [
                {"attack_pattern": p, "nature": nature, "capec_id": raw}
                for p, nature, raw in related
                if not self._is_attack_pattern(raw)
            ],
            "reference_citations": len(cited),
            "references_unresolved": [
                {"entry": e, "reference": ref, "section": section}
                for e, ref, section in cited
                if ref not in self._references_by_id
            ],
            "taxonomy_mappings": dict(
                sorted(
                    Counter(
                        str(t.get("@Taxonomy_Name", ""))
                        for p in self.attack_patterns
                        for t in cwe._items(p.fields, "Taxonomy_Mappings", "Taxonomy_Mapping")
                    ).items()
                )
            ),
        }

    def _is_attack_pattern(self, capec_id: str) -> bool:
        target = self.get(capec_id)
        return target is not None and target.kind == "Attack_Pattern"

    @cached_property
    def objects(self) -> Mapping[str, tuple[Mapping[str, Any], ...]]:
        """`to_objects()` for every attack pattern, built once."""
        built = to_objects(self)
        return MappingProxyType({name: tuple(items) for name, items in built.items()})


def notice(catalog: CapecCatalog) -> str:
    """MITRE's copyright designation for a release, which every copy of CAPEC content carries.

    The CAPEC Terms of Use (TERMS_URL) let anyone copy CAPEC provided that the copy
    reproduces this designation and LICENSE.
    """
    return (
        f"Copyright © 2007-{catalog.date[:4]}, The MITRE Corporation. CAPEC and the CAPEC "
        "logo are trademarks of The MITRE Corporation."
    )


def capec_number(capec_id: str) -> int:
    """The number in a CAPEC id written `CAPEC-66`, `capec-66` or `66`; ValueError otherwise."""
    number = _number(capec_id)
    if number is None:
        raise ValueError(f"a CAPEC id looks like CAPEC-66, not {capec_id!r}")
    return number


def load_catalog(path: str | Path, sha256: str | None = None) -> CapecCatalog:
    """Read the catalog at `path`, MITRE's CAPEC XML.

    With `sha256`, the file must have exactly that digest, or CapecError says which
    it has instead. Raises CapecError for a file that is not a CAPEC Schema 3
    catalog, and, before reading it, for one that is not a regular file or is larger
    than MAX_FILE_BYTES.
    """
    path = Path(path)
    return _from_bytes(path.name, _read(path), sha256)


def configured_catalog(url: str | None = None) -> Path | None:
    """The CAPEC release to read: `$TMODEL_CAPEC_CATALOG` if set, else a packaged engine's
    copy.

    The engine never fetches a catalog itself. DEC-008 is open; until the sponsor decides
    it, the team's interim rule (ADR-0014, proposed) applies, as it does to CWE:
    `bin/build-engine` downloads the release the library pins at `url`, checks its SHA-256
    and bundles it below `_MEIPASS` as `catalogs/<bundled_name(url)>`, and a packaged
    engine reads that copy. In a source checkout there is none until the variable names a
    file.
    """
    configured = os.environ.get(CATALOG_ENV, "").strip()
    if configured:
        return Path(os.path.expanduser(configured))
    if url and getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / cwe.BUNDLED_CATALOGS / cwe.bundled_name(url)
        return bundled if bundled.is_file() else None
    return None


_cache_lock = threading.Lock()
_cache: dict[str, tuple[str, CapecCatalog]] = {}


def cached_catalog(path: str | Path, sha256: str) -> CapecCatalog:
    """`load_catalog(path, sha256)`, kept until the file's bytes change.

    Each call hashes the file, which takes a few milliseconds for the 3.8 MB release,
    and parses it again only when the bytes changed.
    """
    path = Path(path)
    pinned = sha256.strip().lower()
    data = _read(path)
    digest = hashlib.sha256(data).hexdigest()
    with _cache_lock:
        cached = _cache.get(str(path))
        if cached is not None and cached[0] == digest == pinned:
            return cached[1]
        catalog = _from_bytes(path.name, data, pinned)
        _cache[str(path)] = (digest, catalog)
        return catalog


# --- objects in the tmodel object model -------------------------------------------------


def attack_pattern_id(number: int) -> str:
    """The tmodel object id of CAPEC attack pattern `number`, as the example models write it."""
    return f"attack-pattern:capec-{number}"


def to_objects(
    catalog: CapecCatalog, numbers: Iterable[int] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """The tmodel objects for the catalog's attack patterns (all, or those numbered).

    The collections are those of the example models (`ExampleModelCore`):

    - `attack_patterns`: one AttackPattern per CAPEC attack pattern, with `id`
      attack-pattern:capec-N, `name`, `description` (its Description) and
      `catalog_ref` CAPEC-N. The CWE import makes the same ids with only
      `catalog_ref`; these give them names;
    - `weaknesses`: one Weakness per CWE id those attack patterns relate to, with only
      `catalog_ref`, as the CWE import's ids (weakness:cwe-N), which carry the rest;
    - `assertions`: Weakness `exploited_by` AttackPattern for each Related_Weakness,
      the predicate the CWE import and mvp-02 use. All are `proposed` and attributed
      to MITRE's CAPEC program: CAPEC states them, and no tmodel reviewer has
      accepted them (R-018). Their ids say CAPEC gave them, so they never collide
      with the CWE import's Assertions for the same pair;
    - `parties`: that program, as an organization.

    Categories and views are not objects, as in the CWE import. Links between attack
    patterns, taxonomy mappings (ATT&CK, WASC, OWASP) and every other field stay on
    the entry.
    """
    wanted = set(numbers) if numbers is not None else None
    provenance = (
        f"tmodel CAPEC import: {catalog.name} {catalog.version} ({catalog.date}), "
        f"{catalog.file}, SHA-256 {catalog.sha256}"
    )
    patterns: list[dict[str, Any]] = []
    weaknesses: dict[str, dict[str, Any]] = {}
    assertions: dict[str, dict[str, Any]] = {}
    for entry in catalog.attack_patterns:
        if wanted is not None and entry.number not in wanted:
            continue
        pattern = attack_pattern_id(entry.number)
        patterns.append(
            {
                "id": pattern,
                "name": entry.name,
                "description": entry.description,
                "catalog_ref": entry.id,
            }
        )
        for cwe_id in entry.weaknesses:
            weakness = cwe.weakness_id(cwe.cwe_number(cwe_id))
            weaknesses.setdefault(weakness, {"id": weakness, "catalog_ref": cwe_id})
            assertion = f"assertion:{entry.id.lower()}-related-weakness-{cwe_id.lower()}"
            assertions.setdefault(
                assertion,
                {
                    "id": assertion,
                    "name": f"{cwe_id} is exploited by {entry.id}",
                    "subject": weakness,
                    "predicate": "exploited_by",
                    "object": pattern,
                    "assertion_status": "proposed",
                    "asserted_by": MITRE_PARTY,
                    "generated_by": provenance,
                },
            )
    return {
        "parties": [
            {"id": MITRE_PARTY, "name": "MITRE CAPEC Program", "party_kind": "organization"}
        ],
        "attack_patterns": patterns,
        "weaknesses": sorted(weaknesses.values(), key=cwe._catalog_number),
        "assertions": list(assertions.values()),
    }


# --- reading the file ---------------------------------------------------------------------


def _read(path: Path) -> bytes:
    """The bytes of `path`, read as the CWE reader reads its catalog, with CAPEC's limit."""
    return cwe._read(path, MAX_FILE_BYTES, CapecError)


def _from_bytes(name: str, data: bytes, sha256: str | None) -> CapecCatalog:
    digest = hashlib.sha256(data).hexdigest()
    if sha256 is not None and digest != sha256.strip().lower():
        raise CapecError(
            f"{name}: SHA-256 {digest} is not the {sha256} the library pins; "
            "use the file the library's capec record names, unchanged"
        )
    return _catalog(name, digest, _parse(name, data))


def _parse(name: str, xml: bytes) -> ElementTree.Element:
    if xml.find(b"<Attack_Pattern_Catalog") < 0:
        raise CapecError(f"{name}: not a CAPEC catalog (no Attack_Pattern_Catalog element)")
    # A CAPEC catalog declares no DOCTYPE and no entities, so any declaration, wherever it
    # is in the file, is refused before parsing: no entity is ever expanded.
    if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
        raise CapecError(
            f"{name}: has a DOCTYPE or ENTITY declaration; a CAPEC catalog has none, "
            "so it is not read"
        )
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise CapecError(f"{name}: not well-formed XML ({exc})") from exc
    if root.tag != f"{{{CAPEC_NS}}}Attack_Pattern_Catalog":
        raise CapecError(
            f"{name}: the root is {root.tag}, not a CAPEC Schema 3 Attack_Pattern_Catalog "
            f"(namespace {CAPEC_NS})"
        )
    return root


def _catalog(name: str, digest: str, root: ElementTree.Element) -> CapecCatalog:
    kinds = dict(CONTAINERS)
    entries: dict[str, list[CapecEntry]] = {"Attack_Pattern": [], "Category": [], "View": []}
    references: list[Mapping[str, Any]] = []
    counts: Counter[tuple[str, str]] = Counter()
    unknown: Counter[str] = Counter()
    seen: dict[int, str] = {}
    defined: set[str] = set()
    for container in root:
        container_name = cwe._local(container.tag)
        kind = kinds.get(container_name) if cwe._ns(container.tag) == CAPEC_NS else None
        if kind is None:
            unknown[f"Attack_Pattern_Catalog/{container_name}"] += 1
            continue
        for element in container:
            if cwe._ns(element.tag) != CAPEC_NS or cwe._local(element.tag) != kind:
                unknown[f"{container_name}/{cwe._local(element.tag)}"] += 1
                continue
            fields = cwe._value(element, CAPEC_NS)
            if not isinstance(fields, Mapping):  # an entry with neither attributes nor fields
                fields = MappingProxyType({})
            present = [key for key in fields if not key.startswith("#")]
            counts.update((kind, key) for key in present)
            unknown.update(f"{kind}/{key}" for key in present if key not in ENTRY_FIELDS[kind])
            if kind == "External_Reference":
                reference = str(fields.get("@Reference_ID", ""))
                if reference in defined:  # a citation of it could not say which one it means
                    raise CapecError(f"{name}: external reference {reference} is defined twice")
                defined.add(reference)
                references.append(fields)
                continue
            entry = _entry(name, kind, fields)
            if entry.number in seen:
                first, label = seen[entry.number], f"{name}: CAPEC-{entry.number}"
                raise CapecError(
                    f"{label} is given twice"
                    if first == kind
                    else f"{label} is both {_LABELS[first]} and {_LABELS[kind]}"
                )
            seen[entry.number] = kind
            entries[kind].append(entry)
    return CapecCatalog(
        name=_required_attribute(name, root, "Name"),
        version=_required_attribute(name, root, "Version"),
        date=_required_attribute(name, root, "Date"),
        schema=_schema_version(root),
        file=name,
        sha256=digest,
        attack_patterns=tuple(entries["Attack_Pattern"]),
        categories=tuple(entries["Category"]),
        views=tuple(entries["View"]),
        references=tuple(references),
        field_counts=tuple((kind, key, n) for (kind, key), n in counts.items()),
        unknown=tuple(sorted(unknown.items())),
    )


def _entry(name: str, kind: str, fields: Mapping[str, Any]) -> CapecEntry:
    number = fields.get("@ID")
    if not isinstance(number, str) or not WHOLE_NUMBER.fullmatch(number):
        raise CapecError(f"{name}: {_LABELS[kind]} has no whole-number ID (found {number!r})")
    label = f"CAPEC-{int(number)}"
    text_field = {"Attack_Pattern": "Description", "Category": "Summary", "View": "Objective"}[kind]
    return CapecEntry(
        kind=kind,
        number=int(number),
        name=_attribute(name, label, fields, "@Name"),
        status=_attribute(name, label, fields, "@Status"),
        description=plain_text(cwe._first(fields, text_field)),
        fields=fields,
        abstraction=cwe._optional(fields, "@Abstraction"),
        view_type=cwe._optional(fields, "@Type"),
        likelihood=cwe._text_at(fields, "Likelihood_Of_Attack"),
        severity=cwe._text_at(fields, "Typical_Severity"),
        alternate_terms=tuple(
            plain_text(cwe._first(term, "Term"))
            for term in cwe._items(fields, "Alternate_Terms", "Alternate_Term")
        ),
        related_attack_patterns=tuple(
            (str(p.get("@Nature", "")), f"CAPEC-{int(p['@CAPEC_ID'])}")
            for p in cwe._items(fields, "Related_Attack_Patterns", "Related_Attack_Pattern")
            if WHOLE_NUMBER.fullmatch(str(p.get("@CAPEC_ID", "")))
        ),
        weaknesses=tuple(
            dict.fromkeys(
                f"CWE-{int(w['@CWE_ID'])}"
                for w in cwe._items(fields, "Related_Weaknesses", "Related_Weakness")
                if WHOLE_NUMBER.fullmatch(str(w.get("@CWE_ID", "")))
            )
        ),
        attack_techniques=tuple(
            dict.fromkeys(
                f"T{entry_id}"
                for mapping in cwe._items(fields, "Taxonomy_Mappings", "Taxonomy_Mapping")
                if mapping.get("@Taxonomy_Name") == "ATTACK"
                and ATTACK_ENTRY.fullmatch(entry_id := plain_text(cwe._first(mapping, "Entry_ID")))
            )
        ),
        steps=_count(fields, "Execution_Flow", "Attack_Step"),
        mitigations=_count(fields, "Mitigations", "Mitigation"),
        examples=_count(fields, "Example_Instances", "Example"),
    )


# --- small readers ----------------------------------------------------------------------------


def _cited_id(cited: Mapping[str, Any]) -> str:
    """The reference id a Reference cites, such as REF-1."""
    return str(cited.get("@External_Reference_ID", ""))


def _citation(cited: Mapping[str, Any], reference: Mapping[str, Any] | None) -> dict[str, Any]:
    """One citation for the details view, with the reference it names, if defined."""
    found = reference or {}
    return {
        "id": _cited_id(cited),
        "section": cwe._optional(cited, "@Section"),
        "resolved": reference is not None,
        "title": cwe._text_at(found, "Title"),
        "authors": [plain_text(author) for author in found.get("Author", ())],
        "edition": cwe._text_at(found, "Edition"),
        "publication": cwe._text_at(found, "Publication"),
        "publisher": cwe._text_at(found, "Publisher"),
        "year": cwe._text_at(found, "Publication_Year"),
        "month": cwe._text_at(found, "Publication_Month"),
        "day": cwe._text_at(found, "Publication_Day"),
        "url": cwe._text_at(found, "URL"),
        "url_date": cwe._text_at(found, "URL_Date"),
    }


def _count(fields: Mapping[str, Any], container: str, item: str) -> int:
    """How many `item` values an entry's `container` field holds, text or structured.

    CAPEC writes many items (a Mitigation, an Example, a Prerequisite) as text alone,
    which `cwe._items` leaves out because it returns only structured ones.
    """
    holders = fields.get(container)
    if not isinstance(holders, tuple):
        return 0
    return sum(len(h.get(item, ())) for h in holders if isinstance(h, Mapping))


def _attribute(name: str, label: str, fields: Mapping[str, Any], key: str) -> str:
    value = cwe._optional(fields, key)
    if value is None:
        raise CapecError(f"{name}: {label} has no {key[1:]}")
    return value


def _required_attribute(name: str, root: ElementTree.Element, key: str) -> str:
    value = root.get(key)
    if not value:
        raise CapecError(f"{name}: Attack_Pattern_Catalog has no {key}")
    return value


def _schema_version(root: ElementTree.Element) -> str | None:
    location = root.get(f"{{{cwe.XSI_NS}}}schemaLocation", "").split()
    found = SCHEMA_FILE.search(location[-1]) if location else None
    return found.group(1) if found else None


def _number(capec_id: str | int) -> int | None:
    if isinstance(capec_id, int):
        return capec_id
    text = str(capec_id).strip()
    if text[:6].casefold() == "capec-":
        text = text[6:]
    return int(text) if WHOLE_NUMBER.fullmatch(text) else None
