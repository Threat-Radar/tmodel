"""Read MITRE's CWE List into typed entries, keeping every field (#144, #61; PLAN-0002 §5).

Input is the CWE List as MITRE publishes it, `cwec_vX.Y.xml.zip` or the XML inside
it, written to CWE XML Schema 7 (namespace `http://cwe.mitre.org/cwe-7`). Which
release the engine reads is the library's call. Each release is a library record that
pins the file's SHA-256: the first is `cwe` (4.20, Threat-Radar/library#21), and each
newer one is a new record that supersedes the one before. `served_record` finds the
newest, and `load_catalog` refuses any other bytes.

Lossless: every element and attribute of an entry is kept in `CweEntry.fields`, so a
CWE field that has no tmodel slot is carried, not dropped. `CweCatalog.report()`
says, field by field, where each entry field goes in the object model and how many
entries carry it, and `CweCatalog.unknown` lists any entry field this reader does
not know, such as one a newer schema adds. Nothing is dropped silently.

`to_objects()` maps the weaknesses onto the accepted object model (ADR-0010,
ADR-0011): one Weakness per CWE weakness, and a proposed Assertion for each CAPEC
and CVE link CWE gives (DL-0050).

Relationships (#145, DL-0057): each relationship an entry writes, a weakness's
Related_Weakness and a category's or view's Has_Member or Member_Of, is a
`Relationship` tagged with its view (View_ID). `CweCatalog.relationships()` gives them
for any list of views, with the inverses the schema declares (ParentOf, CanFollow,
RequiredBy, MemberOf) derived. They are not objects: the accepted core has no
Weakness-to-Weakness edge, and categories and views are not objects.

Read-only and deterministic, like the library loader: the same bytes give the same
entries in the same order, and nothing is written anywhere.

How an element becomes a value in `fields`:

- an attribute is a key `@Name` holding its text;
- an element holding only text is that text, exactly as written; with attributes,
  a mapping of them plus `#text`;
- an element holding XHTML (CWE's structured text and example code) is a mapping of
  its attributes, if any, plus `#xhtml`: its inner markup without the `xhtml:`
  prefix, trimmed, such as `<p>One.</p><p>Two.</p>`. A plain string is never
  markup, so text such as `x < y` stays text;
- any other element is a mapping: its attributes, then each child's name with the
  list of its values, in the order the names first appear. Where child names
  interleave (a Demonstrative_Example's Body_Text and Example_Code), the children
  are an ordered list of one-key mappings under `#items` instead, so their order
  survives.
"""

from __future__ import annotations

import hashlib
import html
import io
import os
import re
import stat
import sys
import threading
import zipfile
import zlib
from collections import Counter
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
from xml.etree import ElementTree
from xml.sax.saxutils import escape, quoteattr

if TYPE_CHECKING:
    from engine.load.library import Library, LibraryRecord

CWE_NS = "http://cwe.mitre.org/cwe-7"  # CWE XML Schema 7.x; CWE 5.0 (schema 8) is not read
XHTML_NS = "http://www.w3.org/1999/xhtml"
XML_NS = "http://www.w3.org/XML/1998/namespace"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
# Names the CWE catalog file the engine reads (the library record pins its digest).
CATALOG_ENV = "TMODEL_CWE_CATALOG"
# Where a packaged engine finds the release that bin/build-engine bundled (ADR-0014).
BUNDLED_CATALOGS = "catalogs"
# The first library record of the CWE line (4.20). A newer release is a new record that
# supersedes the one before, because library ids are never reused; `served_record`
# follows that chain to the record whose content.url and content.sha256 the engine serves.
LIBRARY_RECORD = "cwe"
# The 4.21 XML is 18.6 MB. A zip whose XML is larger than this is refused.
MAX_XML_BYTES = 256 * 1024 * 1024
# A catalog file, zip or XML, larger than this is refused before any of it is read.
MAX_FILE_BYTES = MAX_XML_BYTES
TERMS_URL = "https://cwe.mitre.org/about/termsofuse.html"
# The licence on that page (last updated 2023-07-20), which a copy of CWE content reproduces.
LICENSE = (
    "CWE™ is free to use by any organization or individual for any research, development, "
    "and/or commercial purposes, per these CWE Terms of Use. Accordingly, The MITRE "
    "Corporation hereby grants you a non-exclusive, royalty-free license to use CWE for "
    "research, development, and commercial purposes. Any copy you make for such purposes is "
    "authorized on the condition that you reproduce MITRE’s copyright designation and this "
    "license in any such copy. CWE is a trademark of The MITRE Corporation. Please contact "
    "cwe@mitre.org if you require further clarification on this issue."
)
DEFINITION_URL = "https://cwe.mitre.org/data/definitions/{number}.html"

# The containers under Weakness_Catalog, in schema order, with the entry each holds.
CONTAINERS = (
    ("Weaknesses", "Weakness"),
    ("Categories", "Category"),
    ("Views", "View"),
    ("External_References", "External_Reference"),
)
# Each entry's own fields in CWE XML Schema 7.3, attributes first, then child elements
# in schema order (library record `cwe`, distilled/messages.yaml); schema 7.4 declares
# the same ones. A field outside these lists is still kept, and is reported in
# CweCatalog.unknown.
ENTRY_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "Weakness": (
            "@ID",
            "@Name",
            "@Abstraction",
            "@Structure",
            "@Status",
            "@Diagram",
            "Description",
            "Extended_Description",
            "Related_Weaknesses",
            "Weakness_Ordinalities",
            "Applicable_Platforms",
            "Background_Details",
            "Alternate_Terms",
            "Modes_Of_Introduction",
            "Exploitation_Factors",
            "Likelihood_Of_Exploit",
            "Common_Consequences",
            "Detection_Methods",
            "Potential_Mitigations",
            "Demonstrative_Examples",
            "Observed_Examples",
            "Functional_Areas",
            "Affected_Resources",
            "Taxonomy_Mappings",
            "Related_Attack_Patterns",
            "References",
            "Mapping_Notes",
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
            "Mapping_Notes",
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
            "Mapping_Notes",
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
            # Declared by schema 8.0 (CWE 5.0), not 7.x. CWE 4.21 carries them anyway,
            # which is one reason it fails 7.4 validation (library record `cwe-4-21`).
            "Alt_URL",
            "Alt_URL_Date",
            "Media_Type",
            "Access_Restrictions",
            "Rationale",
        ),
    }
)
# Where an entry field goes in the object model (ADR-0010 core, ADR-0011; DL-0050).
# Every other field stays on the entry only, kept whole in CweEntry.fields.
MAPPED: Mapping[tuple[str, str], str] = MappingProxyType(
    {
        ("Weakness", "@ID"): "Weakness.id, Weakness.catalog_ref",
        ("Weakness", "@Name"): "Weakness.name",
        ("Weakness", "Description"): "Weakness.description",
        ("Weakness", "Related_Attack_Patterns"): "Assertion: Weakness exploited_by AttackPattern",
        ("Weakness", "Observed_Examples"): "Assertion: Vulnerability instance_of Weakness",
    }
)
# The organization every imported Assertion is attributed to (design notes, adapt 5).
MITRE_PARTY = "party:mitre-cwe"
# What an entry read from MITRE's file says it comes from; a local weakness says `local`.
SOURCE = "mitre-cwe"
# CWE's relationship natures (RelatedNatureEnumeration, CWE XML Schema 7.3), in schema
# order. 4.20 writes six of them; ParentOf, CanFollow and RequiredBy are declared but
# never written (library record `cwe`, distilled/messages.yaml).
NATURES = (
    "ChildOf",
    "ParentOf",
    "StartsWith",
    "CanFollow",
    "CanPrecede",
    "RequiredBy",
    "Requires",
    "CanAlsoBe",
    "PeerOf",
)
# Membership is a Has_Member or Member_Of element on a category or a view, not a
# Nature. Here it is a nature of its own, spelled as the natures are.
MEMBERSHIP: Mapping[str, str] = MappingProxyType(
    {"Has_Member": "HasMember", "Member_Of": "MemberOf"}
)
# The field each kind of entry writes its relationships in, and the elements in it
# that are relationships.
RELATIONSHIP_FIELDS: Mapping[str, str] = MappingProxyType(
    {"Weakness": "Related_Weaknesses", "Category": "Relationships", "View": "Members"}
)
RELATIONSHIP_ELEMENTS = frozenset({"Related_Weakness", *MEMBERSHIP})
# The inverse pairs the schema declares, derived where CWE writes only one side. The
# other natures have none: CanAlsoBe "is not necessarily reciprocal" (L973), and
# PeerOf and StartsWith name no inverse.
INVERSE: Mapping[str, str] = MappingProxyType(
    {
        "ChildOf": "ParentOf",
        "ParentOf": "ChildOf",
        "CanPrecede": "CanFollow",
        "CanFollow": "CanPrecede",
        "Requires": "RequiredBy",
        "RequiredBy": "Requires",
        "HasMember": "MemberOf",
        "MemberOf": "HasMember",
    }
)
# The natures the schema's text ties Ordinal and Chain_ID to (L540). MITRE's own data
# departs from both, so a departure is reported, never refused (design notes, open
# question 5).
ORDINAL_NATURES = frozenset({"ChildOf"})
CHAIN_NATURES = frozenset({"CanPrecede", "CanFollow"})
CVE_ID = re.compile(r"CVE-[0-9]{4}-[0-9]{4,}")
SCHEMA_FILE = re.compile(r"cwe_schema_v([0-9][0-9.]*)\.xsd$")
WHOLE_NUMBER = re.compile(r"[0-9]+")  # ASCII digits only, so int() always accepts it


class CweError(ValueError):
    """The catalog cannot be read: other bytes than the pinned ones, not a CWE catalog, bad XML."""


@dataclass(frozen=True)
class ObservedExample:
    """One Observed_Example: the vulnerability CWE cites as an instance of the weakness."""

    reference: str  # usually a CVE id
    description: str
    link: str | None = None


@dataclass(frozen=True)
class Relationship:
    """One relationship in one CWE view: as an entry writes it, or a declared inverse.

    `source` is the entry the relationship is written on (for a membership, the
    category or view that has the member) and `target` the entry it names, each an id
    such as `CWE-79` or a local `tr-weak-0001`. `view` is the View_ID, the view the
    relationship belongs to. A `derived` relationship is the inverse the schema
    declares for a written one (INVERSE): source and target swapped, the same view, no
    ordinal and no chain.
    """

    source: str
    nature: str
    target: str
    view: int
    ordinal: str | None = None  # Ordinal, which is only ever Primary
    chain: str | None = None  # Chain_ID, the named chain's id, such as CWE-692
    derived: bool = False

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready, in a fixed key order, with the view as an id."""
        return {
            "source": self.source,
            "nature": self.nature,
            "target": self.target,
            "view": f"CWE-{self.view}",
            "ordinal": self.ordinal,
            "chain": self.chain,
            "derived": self.derived,
        }


@dataclass(frozen=True)
class CweEntry:
    """One Weakness, Category or View. `fields` keeps every field of the entry, read-only."""

    kind: str  # Weakness, Category or View
    number: int
    name: str
    status: str
    description: (
        str  # plain text: a weakness's Description, a category's Summary, a view's Objective
    )
    fields: Mapping[str, Any] = field(compare=False, repr=False)
    abstraction: str | None = None  # weaknesses only
    structure: str | None = None  # weaknesses only
    view_type: str | None = None  # views only
    usage: str | None = (
        None  # Mapping_Notes/Usage: Allowed, Allowed-with-Review, Discouraged or Prohibited
    )
    likelihood: str | None = None  # Likelihood_Of_Exploit
    alternate_terms: tuple[str, ...] = ()
    attack_patterns: tuple[str, ...] = ()  # CAPEC ids such as CAPEC-63, in file order
    observed_examples: tuple[ObservedExample, ...] = ()
    mitigations: int = 0  # Potential_Mitigations entries
    relationships: tuple[Relationship, ...] = ()  # the ones this entry writes, in file order

    @property
    def id(self) -> str:
        return f"CWE-{self.number}"

    @property
    def source(self) -> str:
        return SOURCE

    @property
    def object_id(self) -> str | None:
        """The tmodel Weakness id, for a weakness; categories and views are not objects."""
        return weakness_id(self.number) if self.kind == "Weakness" else None

    @property
    def url(self) -> str:
        return DEFINITION_URL.format(number=self.number)

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready, in a fixed key order, with every field under `fields`."""
        return {
            "id": self.id,
            "kind": self.kind,
            "source": self.source,
            "name": self.name,
            "status": self.status,
            "abstraction": self.abstraction,
            "structure": self.structure,
            "view_type": self.view_type,
            "usage": self.usage,
            "likelihood": self.likelihood,
            "description": self.description,
            "alternate_terms": list(self.alternate_terms),
            "attack_patterns": list(self.attack_patterns),
            "observed_examples": [
                {"reference": e.reference, "description": e.description, "link": e.link}
                for e in self.observed_examples
            ],
            "mitigations": self.mitigations,
            "relationships": [r.to_dict() for r in self.relationships],
            "url": self.url,
            "fields": _thawed(self.fields),
        }


@dataclass(frozen=True)
class CweCatalog:
    """One CWE release: its entries in file order, and what the reader found in them."""

    name: str
    version: str
    date: str
    schema: str | None  # the schema version its xsi:schemaLocation names, such as 7.3
    file: str  # the file's name only, so an answer names no local path
    sha256: str  # of the file as read, the zip when it was a zip
    weaknesses: tuple[CweEntry, ...]
    categories: tuple[CweEntry, ...]
    views: tuple[CweEntry, ...]
    references: tuple[Mapping[str, Any], ...]  # External_Reference fields, in file order
    field_counts: tuple[tuple[str, str, int], ...]  # (kind, field, entries carrying it)
    unknown: tuple[tuple[str, int], ...] = ()  # ("Kind/Field", entries) the reader does not know

    @cached_property
    def _by_number(self) -> Mapping[int, CweEntry]:
        entries = (*self.weaknesses, *self.categories, *self.views)
        return MappingProxyType({e.number: e for e in entries})

    def get(self, cwe_id: str | int) -> CweEntry | None:
        """The entry with this id: `CWE-79`, `cwe-79`, `79` or 79."""
        number = _number(cwe_id)
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

    def links(self) -> dict[str, Any]:
        """What became of CWE's CAPEC and CVE links (DL-0050), naming each one not mapped.

        An observed example becomes an `instance_of` Assertion only when its reference
        is a CVE id; the others stay on their entry and are listed here. A link CWE
        gives twice for one weakness becomes one Assertion, and is listed too.
        """
        capec = [
            (w.id, p.get("@CAPEC_ID", ""))
            for w in self.weaknesses
            for p in _items(w.fields, "Related_Attack_Patterns", "Related_Attack_Pattern")
        ]
        examples = [(w.id, e.reference) for w in self.weaknesses for e in w.observed_examples]
        cve = Counter(pair for pair in examples if CVE_ID.fullmatch(pair[1]))
        return {
            "attack_pattern_links": len(capec),
            "attack_pattern_links_repeated": _repeated(Counter(capec), "capec"),
            "observed_examples": len(examples),
            "observed_examples_without_cve_id": [
                {"weakness": w, "reference": ref} for w, ref in examples if (w, ref) not in cve
            ],
            "observed_examples_repeated": _repeated(cve, "reference"),
        }

    @cached_property
    def objects(self) -> Mapping[str, tuple[Mapping[str, Any], ...]]:
        """`to_objects()` for every weakness, built once."""
        built = to_objects(self)
        return MappingProxyType({name: tuple(items) for name, items in built.items()})

    @cached_property
    def stated_relationships(self) -> tuple[Relationship, ...]:
        """Every relationship the release writes, entry by entry in file order (#145)."""
        entries = (*self.weaknesses, *self.categories, *self.views)
        return tuple(r for e in entries for r in e.relationships)

    @cached_property
    def known_views(self) -> frozenset[int]:
        """The views a query can name: the release's views, and every view a relationship is in."""
        return frozenset(
            {v.number for v in self.views} | {r.view for r in self.stated_relationships}
        )

    def relationships(
        self,
        views: Iterable[int | str] | str | None = None,
        entry: str | int | None = None,
        derived: bool = True,
    ) -> list[Relationship]:
        """The relationships in `views`, any number of them, or in every view when None.

        `views` holds view ids (`CWE-1000`, `1000` or 1000) or is one text of them
        separated by commas; ValueError for one the release does not know. With
        `entry`, only the relationships whose source it is. With `derived`, the
        inverses the schema declares follow the written ones (`with_inverses`).
        """
        source = None if entry is None else f"CWE-{cwe_number(str(entry))}"
        return select(
            self.stated_relationships, view_numbers(views, self.known_views), source, derived
        )

    def relationship_report(self) -> dict[str, Any]:
        """What the release's relationships hold, and where they depart from the schema's text."""
        entries = {e.id for e in (*self.weaknesses, *self.categories, *self.views)}
        return relationship_report(
            self.stated_relationships, entries, {v.number for v in self.views}
        )


def notice(catalog: CweCatalog) -> str:
    """MITRE's copyright designation for a release, which every copy of CWE content carries.

    The CWE Terms of Use (TERMS_URL) let anyone copy CWE on the condition that the
    copy reproduces this designation and LICENSE.
    """
    return (
        f"Copyright © 2006-{catalog.date[:4]}, The MITRE Corporation. CWE, CWSS, CWRAF, "
        "and the CWE logo are trademarks of The MITRE Corporation."
    )


def cwe_number(cwe_id: str) -> int:
    """The number in a CWE id written `CWE-79`, `cwe-79` or `79`; ValueError for anything else."""
    number = _number(cwe_id)
    if number is None:
        raise ValueError(f"a CWE id looks like CWE-79, not {cwe_id!r}")
    return number


def load_catalog(path: str | Path, sha256: str | None = None) -> CweCatalog:
    """Read the catalog at `path`, a CWE zip as MITRE publishes it or the XML inside one.

    With `sha256`, the file must have exactly that digest, or CweError says which it
    has instead. Raises CweError for a file that is not a CWE Schema 7 catalog, and,
    before reading it, for one that is not a regular file or is larger than
    MAX_FILE_BYTES.
    """
    path = Path(path)
    return _from_bytes(path.name, _read(path), sha256)


def configured_catalog(url: str | None = None) -> Path | None:
    """The CWE release to read: `$TMODEL_CWE_CATALOG` if set, else a packaged engine's copy.

    The engine never fetches a catalog itself (ADR-0014). `bin/build-engine` downloads
    the release the library pins at `url`, checks its SHA-256 and bundles it below
    `_MEIPASS` as `catalogs/<bundled_name(url)>`, and a packaged engine reads that copy.
    In a source checkout there is none until the variable names a file.
    """
    configured = os.environ.get(CATALOG_ENV, "").strip()
    if configured:
        return Path(os.path.expanduser(configured))
    if url and getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / BUNDLED_CATALOGS / bundled_name(url)
        return bundled if bundled.is_file() else None
    return None


def bundled_name(url: str) -> str:
    """The file name a bundled copy of the release at `url` has: the URL's last segment."""
    return PurePosixPath(urlparse(url).path).name


def served_record(library: Library) -> LibraryRecord | None:
    """The library record of the CWE release the engine serves: the newest one.

    The line starts at LIBRARY_RECORD (`cwe`, 4.20). A newer release is a new record that
    supersedes the one before, so this follows `supersedes` forward until no record
    supersedes the current one: `cwe-4-21` once the library has it. None when the
    library has no `cwe` record. A line that forks or loops is a library mistake, so
    it raises rather than pick a record.
    """
    record = library.get(LIBRARY_RECORD)
    seen: set[str] = set()
    while record is not None:
        seen.add(record.id)
        newer = sorted(r.id for r in library if record.id in r.related("supersedes"))
        if not newer:
            return record
        if len(newer) > 1:
            raise CweError(
                f"the library's CWE line forks: {', '.join(newer)} each supersede {record.id}"
            )
        if newer[0] in seen:
            raise CweError(f"the library's CWE line loops back to {newer[0]}")
        record = library.get(newer[0])
    return None


_cache_lock = threading.Lock()
_cache: dict[str, tuple[str, CweCatalog]] = {}


def cached_catalog(path: str | Path, sha256: str) -> CweCatalog:
    """`load_catalog(path, sha256)`, kept until the file's bytes change.

    Parsing the whole 4.20 catalog takes a few seconds; hashing the 2 MB zip takes a
    few milliseconds, so each call hashes the file and parses only when it changed.
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


# --- relationships (#145) ---------------------------------------------------------------


def with_inverses(stated: Iterable[Relationship]) -> tuple[Relationship, ...]:
    """The written relationships, then the inverse the schema declares for each (INVERSE).

    An inverse is `derived`: source and target swapped, the same view, no ordinal and
    no chain. An inverse that is also written, or that two relationships give, appears
    once.
    """
    stated = tuple(stated)
    seen = {(r.source, r.nature, r.target, r.view) for r in stated}
    derived: list[Relationship] = []
    for r in stated:
        nature = INVERSE.get(r.nature)
        key = (r.target, nature, r.source, r.view)
        if nature is None or key in seen:
            continue
        seen.add(key)
        derived.append(Relationship(r.target, nature, r.source, r.view, derived=True))
    return stated + tuple(derived)


def view_numbers(
    views: Iterable[int | str] | str | None, known: Collection[int]
) -> frozenset[int] | None:
    """The views asked for, as numbers, or None (every view) when `views` is None.

    `views` holds view ids (`CWE-1000`, `1000` or 1000) or is one text of them
    separated by commas. ValueError for a malformed id, for an empty list, and for a
    view not in `known`.
    """
    if views is None:
        return None
    named = [v.strip() for v in views.split(",")] if isinstance(views, str) else list(views)
    numbers = []
    for view in named:
        number = _number(view)
        if number is None:
            raise ValueError(f"a view id looks like CWE-1000, not {view!r}")
        numbers.append(number)
    if not numbers:
        raise ValueError("name at least one view, such as CWE-1000")
    unknown = sorted(set(numbers) - set(known))
    if unknown:
        listed = ", ".join(f"CWE-{n}" for n in unknown)
        raise ValueError(f"not a view this catalog knows: {listed}")
    return frozenset(numbers)


def select(
    stated: Iterable[Relationship],
    views: Collection[int] | None = None,
    source: str | None = None,
    derived: bool = True,
) -> list[Relationship]:
    """The relationships in `views` (every view when None) whose source is `source` (any).

    With `derived`, the declared inverses come after the written ones, so an entry's
    relationships include the inverses of those that name it. A PeerOf, CanAlsoBe or
    StartsWith has no declared inverse, so it is found only from the entry that
    writes it.
    """
    pool = with_inverses(stated) if derived else tuple(stated)
    return [
        r
        for r in pool
        if (views is None or r.view in views) and (source is None or r.source == source)
    ]


def relationship_report(
    stated: Iterable[Relationship], entries: Collection[str], views: Collection[int]
) -> dict[str, Any]:
    """The relationships counted, and each one that departs from the schema or the entries read.

    `entries` holds the ids of the entries read and `views` the numbers of the views
    read. Counted: the relationships written, by nature and by view, and the inverses
    derived. Listed in full: one with a nature the schema does not declare (kept, with
    no inverse), one whose target is not an entry read, an Ordinal or a Chain_ID on
    another nature than the schema's text names (L540), and an entry with two Primary
    relationships of one nature in one view (design notes, open question 2). Counted
    by view: relationships in a view that is not a view read. None is refused.
    """
    stated = tuple(stated)
    derived = with_inverses(stated)[len(stated) :]
    declared = {*NATURES, *MEMBERSHIP.values()}
    primaries = Counter((r.source, r.nature, r.view) for r in stated if r.ordinal == "Primary")
    elsewhere = Counter(r.view for r in stated if r.view not in views)
    return {
        "stated": len(stated),
        "derived": len(derived),
        "natures": _by_nature(r.nature for r in stated),
        "derived_natures": _by_nature(r.nature for r in derived),
        "views": {f"CWE-{n}": c for n, c in sorted(Counter(r.view for r in stated).items())},
        "undeclared_natures": [r.to_dict() for r in stated if r.nature not in declared],
        "targets_not_read": [r.to_dict() for r in stated if r.target not in entries],
        "views_not_read": {f"CWE-{n}": c for n, c in sorted(elsewhere.items())},
        "ordinal_departures": [
            r.to_dict() for r in stated if r.ordinal and r.nature not in ORDINAL_NATURES
        ],
        "chain_departures": [
            r.to_dict() for r in stated if r.chain and r.nature not in CHAIN_NATURES
        ],
        "primary_repeated": [
            {"source": source, "nature": nature, "view": f"CWE-{view}", "times": n}
            for (source, nature, view), n in primaries.items()
            if n > 1
        ],
    }


# --- objects in the tmodel object model -------------------------------------------------


def weakness_id(number: int) -> str:
    """The tmodel object id of CWE weakness `number`, as the example models write it."""
    return f"weakness:cwe-{number}"


def to_objects(
    catalog: CweCatalog, numbers: Iterable[int] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """The tmodel objects for the catalog's weaknesses (all, or those numbered), as a container.

    The collections are those of the example models (`ExampleModelCore`):

    - `weaknesses`: one Weakness per CWE weakness, with `id` weakness:cwe-N, `name`,
      `description` (its Description) and `catalog_ref` CWE-N;
    - `attack_patterns`: one AttackPattern per CAPEC id those weaknesses cite, with
      only `catalog_ref`, until a CAPEC import gives them names;
    - `vulnerabilities`: one Vulnerability per CVE id in their observed examples, with
      only `catalog_ref`;
    - `assertions`: Weakness `exploited_by` AttackPattern for each CAPEC link, and
      Vulnerability `instance_of` Weakness for each observed example, with the
      example's text and link. All are `proposed` and attributed to MITRE's CWE
      program: CWE states them, and no tmodel reviewer has accepted them (R-018);
    - `parties`: that program, as an organization.

    Categories and views are not objects: a category is not a mapping target. Nor are
    relationships (#145): the accepted core has no Weakness-to-Weakness edge, so they
    are served by `CweCatalog.relationships()`. An observed example without a CVE id
    stays on its entry.
    """
    wanted = set(numbers) if numbers is not None else None
    provenance = (
        f"tmodel CWE import: {catalog.name} {catalog.version} ({catalog.date}), "
        f"{catalog.file}, SHA-256 {catalog.sha256}"
    )
    return objects_for(
        [e for e in catalog.weaknesses if wanted is None or e.number in wanted],
        {"id": MITRE_PARTY, "name": "MITRE CWE Program", "party_kind": "organization"},
        provenance,
    )


def objects_for(
    entries: Iterable[Any], party: Mapping[str, Any], provenance: str
) -> dict[str, list[dict[str, Any]]]:
    """The objects for weakness entries, CWE's or local ones (#145), as `to_objects` says.

    An entry gives its `object_id`, `id`, `name`, `description`, `attack_patterns`
    and `observed_examples`. Every Assertion is `proposed`, asserted by `party`, with
    `provenance` as its `generated_by`.
    """
    weaknesses: list[dict[str, Any]] = []
    patterns: dict[str, dict[str, Any]] = {}
    vulnerabilities: dict[str, dict[str, Any]] = {}
    assertions: dict[str, dict[str, Any]] = {}
    for entry in entries:
        weakness = entry.object_id
        weaknesses.append(
            {
                "id": weakness,
                "name": entry.name,
                "description": entry.description,
                "catalog_ref": entry.id,
            }
        )
        for capec in entry.attack_patterns:
            pattern = f"attack-pattern:{capec.lower()}"
            patterns.setdefault(pattern, {"id": pattern, "catalog_ref": capec})
            assertion = f"assertion:{entry.id.lower()}-exploited-by-{capec.lower()}"
            assertions.setdefault(
                assertion,
                {
                    "id": assertion,
                    "name": f"{entry.id} is exploited by {capec}",
                    "subject": weakness,
                    "predicate": "exploited_by",
                    "object": pattern,
                    "assertion_status": "proposed",
                    "asserted_by": party["id"],
                    "generated_by": provenance,
                },
            )
        for example in entry.observed_examples:
            if not CVE_ID.fullmatch(example.reference):
                continue
            vulnerability = f"vulnerability:{example.reference.lower()}"
            vulnerabilities.setdefault(
                vulnerability, {"id": vulnerability, "catalog_ref": example.reference}
            )
            assertion = f"assertion:{example.reference.lower()}-instance-of-{entry.id.lower()}"
            statement = {
                "id": assertion,
                "name": f"{example.reference} is an observed example of {entry.id}",
                "description": example.description,
                "subject": vulnerability,
                "predicate": "instance_of",
                "object": weakness,
                "assertion_status": "proposed",
                "asserted_by": party["id"],
                "generated_by": provenance,
            }
            if example.link:
                statement["evidence"] = [example.link]
            assertions.setdefault(assertion, statement)
    return {
        "parties": [dict(party)],
        "weaknesses": weaknesses,
        "attack_patterns": sorted(patterns.values(), key=lambda p: _catalog_number(p)),
        "vulnerabilities": sorted(vulnerabilities.values(), key=lambda v: v["catalog_ref"]),
        "assertions": list(assertions.values()),
    }


# --- reading the file ---------------------------------------------------------------------


def _read(path: Path, limit: int | None = None, error: type[ValueError] = CweError) -> bytes:
    """The bytes of `path`, a regular file of at most `limit` bytes; `error` otherwise.

    `limit` defaults to MAX_FILE_BYTES; the CAPEC reader passes its own limit and
    error class. The open file's type and size are checked before anything is read,
    so a FIFO or a device is refused rather than waited on or read without end. The
    read stops one byte past the limit, so a file that grows after the check is
    refused too, and the digest is never taken over more than the limit.
    """
    limit = MAX_FILE_BYTES if limit is None else limit
    too_large = f"{path.name}: larger than {limit} bytes, so it is not read"
    try:
        with open(path, "rb", opener=_open_without_waiting) as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise error(f"{path.name}: not a regular file, so it is not read")
            if info.st_size > limit:
                raise error(too_large)
            data = handle.read(limit + 1)
    except OSError as exc:
        raise error(f"{path.name}: cannot read ({exc.strerror or exc})") from exc
    if len(data) > limit:  # it grew after the check
        raise error(too_large)
    return data


def _open_without_waiting(path: str | Path, flags: int) -> int:
    # Opening a FIFO that has no writer waits for one; O_NONBLOCK returns at once, so
    # _read can refuse it. A regular file reads the same either way.
    return os.open(path, flags | getattr(os, "O_NONBLOCK", 0))


def _from_bytes(name: str, data: bytes, sha256: str | None) -> CweCatalog:
    digest = hashlib.sha256(data).hexdigest()
    if sha256 is not None and digest != sha256.strip().lower():
        raise CweError(
            f"{name}: SHA-256 {digest} is not the {sha256} the library pins; "
            "use the file the library's cwe record names, unchanged (the zip, if it names a zip)"
        )
    xml = _unzipped(name, data) if data[:4] == b"PK\x03\x04" else data
    return _catalog(name, digest, _parse(name, xml))


def _unzipped(name: str, data: bytes) -> bytes:
    """The one XML file inside a CWE zip; CweError for any other zip."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = [i for i in archive.infolist() if not i.is_dir()]
            if len(members) != 1 or not members[0].filename.endswith(".xml"):
                listed = ", ".join(i.filename for i in members) or "nothing"
                raise CweError(f"{name}: expected one .xml file in the zip, found {listed}")
            with archive.open(members[0]) as member:  # the header's size can lie; count instead
                xml = member.read(MAX_XML_BYTES + 1)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, EOFError, zlib.error) as exc:
        raise CweError(f"{name}: not a readable zip ({exc})") from exc
    if len(xml) > MAX_XML_BYTES:
        raise CweError(f"{name}: {members[0].filename} is larger than {MAX_XML_BYTES} bytes")
    return xml


def _parse(name: str, xml: bytes) -> ElementTree.Element:
    if xml.find(b"<Weakness_Catalog") < 0:
        raise CweError(f"{name}: not a CWE catalog (no Weakness_Catalog element)")
    # A CWE catalog declares no DOCTYPE and no entities, so any declaration, wherever it
    # is in the file, is refused before parsing: no entity is ever expanded. Looking only
    # before the first `<Weakness_Catalog` let a comment holding those bytes hide one.
    if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
        raise CweError(
            f"{name}: has a DOCTYPE or ENTITY declaration; a CWE catalog has none, "
            "so it is not read"
        )
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise CweError(f"{name}: not well-formed XML ({exc})") from exc
    if root.tag != f"{{{CWE_NS}}}Weakness_Catalog":
        raise CweError(
            f"{name}: the root is {root.tag}, not a CWE Schema 7 Weakness_Catalog "
            f"(namespace {CWE_NS})"
        )
    return root


def _catalog(name: str, digest: str, root: ElementTree.Element) -> CweCatalog:
    kinds = dict(CONTAINERS)
    entries: dict[str, list[CweEntry]] = {"Weakness": [], "Category": [], "View": []}
    references: list[Mapping[str, Any]] = []
    counts: Counter[tuple[str, str]] = Counter()
    unknown: Counter[str] = Counter()
    seen: dict[int, str] = {}
    for container in root:
        container_name = _local(container.tag)
        kind = kinds.get(container_name) if _ns(container.tag) == CWE_NS else None
        if kind is None:
            unknown[f"Weakness_Catalog/{container_name}"] += 1
            continue
        for element in container:
            if _ns(element.tag) != CWE_NS or _local(element.tag) != kind:
                unknown[f"{container_name}/{_local(element.tag)}"] += 1
                continue
            fields = _value(element)
            if not isinstance(fields, Mapping):  # an entry with neither attributes nor fields
                fields = MappingProxyType({})
            present = [key for key in fields if not key.startswith("#")]
            counts.update((kind, key) for key in present)
            unknown.update(f"{kind}/{key}" for key in present if key not in ENTRY_FIELDS[kind])
            if kind == "External_Reference":
                references.append(fields)
                continue
            entry = _entry(name, kind, fields)
            container = RELATIONSHIP_FIELDS[kind]
            unknown.update(  # kept in `fields`, but not a relationship this reader knows
                {
                    f"{kind}/{container}/{element}"
                    for element, _ in _relationship_elements(kind, fields)
                    if element not in RELATIONSHIP_ELEMENTS
                }
            )
            if entry.number in seen:
                raise CweError(
                    f"{name}: CWE-{entry.number} is both a {seen[entry.number]} and a {kind}"
                )
            seen[entry.number] = kind
            entries[kind].append(entry)
    return CweCatalog(
        name=_required_attribute(name, root, "Name"),
        version=_required_attribute(name, root, "Version"),
        date=_required_attribute(name, root, "Date"),
        schema=_schema_version(root),
        file=name,
        sha256=digest,
        weaknesses=tuple(entries["Weakness"]),
        categories=tuple(entries["Category"]),
        views=tuple(entries["View"]),
        references=tuple(references),
        field_counts=tuple((kind, key, n) for (kind, key), n in counts.items()),
        unknown=tuple(sorted(unknown.items())),
    )


def _entry(name: str, kind: str, fields: Mapping[str, Any]) -> CweEntry:
    number = fields.get("@ID")
    if not isinstance(number, str) or not WHOLE_NUMBER.fullmatch(number):
        raise CweError(f"{name}: a {kind} has no whole-number ID (found {number!r})")
    label = f"CWE-{int(number)}"
    text_field = {"Weakness": "Description", "Category": "Summary", "View": "Objective"}[kind]
    return CweEntry(
        kind=kind,
        number=int(number),
        name=_attribute(name, label, fields, "@Name"),
        status=_attribute(name, label, fields, "@Status"),
        description=plain_text(_first(fields, text_field)),
        fields=fields,
        abstraction=_optional(fields, "@Abstraction"),
        structure=_optional(fields, "@Structure"),
        view_type=_optional(fields, "@Type"),
        usage=_text_at(fields, "Mapping_Notes", "Usage"),
        likelihood=_text_at(fields, "Likelihood_Of_Exploit"),
        alternate_terms=tuple(
            plain_text(_first(term, "Term"))
            for term in _items(fields, "Alternate_Terms", "Alternate_Term")
        ),
        attack_patterns=tuple(
            dict.fromkeys(
                f"CAPEC-{int(p['@CAPEC_ID'])}"
                for p in _items(fields, "Related_Attack_Patterns", "Related_Attack_Pattern")
                if WHOLE_NUMBER.fullmatch(str(p.get("@CAPEC_ID", "")))
            )
        ),
        observed_examples=tuple(
            ObservedExample(
                reference=plain_text(_first(example, "Reference")),
                description=plain_text(_first(example, "Description")),
                link=plain_text(_first(example, "Link")) or None,
            )
            for example in _items(fields, "Observed_Examples", "Observed_Example")
        ),
        mitigations=len(_items(fields, "Potential_Mitigations", "Mitigation")),
        relationships=_relationships(name, label, kind, fields),
    )


def _relationships(
    name: str, label: str, kind: str, fields: Mapping[str, Any]
) -> tuple[Relationship, ...]:
    """The relationships an entry writes, in file order (#145).

    A weakness's Related_Weakness keeps its Nature; a category's or view's Has_Member
    and Member_Of become HasMember and MemberOf. Ordinal and Chain_ID are kept on any
    nature, since MITRE's data puts them where the schema's text does not (L540).
    """
    found = []
    for element, item in _relationship_elements(kind, fields):
        if element not in RELATIONSHIP_ELEMENTS:
            continue  # kept in `fields`; _catalog reports it
        if not isinstance(item, Mapping):
            raise CweError(f"{name}: {label} has a {element} with no attributes")
        nature = item.get("@Nature") if element == "Related_Weakness" else MEMBERSHIP[element]
        if not isinstance(nature, str) or not nature:
            raise CweError(f"{name}: {label} has a {element} with no Nature")
        target, view, chain = item.get("@CWE_ID"), item.get("@View_ID"), item.get("@Chain_ID")
        if not _whole(target) or not _whole(view):
            raise CweError(
                f"{name}: a {nature} of {label} needs a whole-number CWE_ID and View_ID "
                f"(found {target!r} and {view!r})"
            )
        found.append(
            Relationship(
                source=label,
                nature=nature,
                target=f"CWE-{int(target)}",
                view=int(view),
                ordinal=_optional(item, "@Ordinal"),
                chain=f"CWE-{int(chain)}" if _whole(chain) else _optional(item, "@Chain_ID"),
            )
        )
    return tuple(found)


def _relationship_elements(kind: str, fields: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """The children of an entry's relationship field, as (name, value) pairs in file order."""
    holders = fields.get(RELATIONSHIP_FIELDS[kind])
    found: list[tuple[str, Any]] = []
    for holder in holders if isinstance(holders, tuple) else ():
        if not isinstance(holder, Mapping):
            continue
        if "#items" in holder:  # the names interleave: one-key mappings, in order
            found += [pair for item in holder["#items"] for pair in item.items()]
        else:
            found += [
                (key, value)
                for key, values in holder.items()
                if not key.startswith(("@", "#"))
                for value in values
            ]
    return found


# --- elements to values ---------------------------------------------------------------------


def _value(element: ElementTree.Element, ns: str = CWE_NS) -> Any:
    """One element as a JSON-ready value, by the rules in the module docstring.

    `ns` is the catalog's own namespace: a child in any other namespace (XHTML) makes
    the element structured text. The CAPEC reader passes its namespace.
    """
    attributes = {f"@{_attribute_name(k)}": v for k, v in element.attrib.items()}
    children = list(element)
    text = element.text or ""
    mixed = any(_ns(c.tag) != ns for c in children) or (
        children and (text.strip() or any((c.tail or "").strip() for c in children))
    )
    if mixed:
        return MappingProxyType({**attributes, "#xhtml": _inner_markup(element).strip()})
    if not children:
        if not attributes:
            return text
        return MappingProxyType({**attributes, "#text": text} if text else attributes)
    names = [_local(c.tag) for c in children]
    runs = [n for i, n in enumerate(names) if i == 0 or names[i - 1] != n]
    if len(runs) != len(set(runs)):  # a name comes back after another: keep the order
        items = tuple(MappingProxyType({_local(c.tag): _value(c, ns)}) for c in children)
        return MappingProxyType({**attributes, "#items": items})
    grouped: dict[str, list[Any]] = {}
    for child in children:
        grouped.setdefault(_local(child.tag), []).append(_value(child, ns))
    return MappingProxyType({**attributes, **{k: tuple(v) for k, v in grouped.items()}})


def _inner_markup(element: ElementTree.Element) -> str:
    return escape(element.text or "") + "".join(
        _outer_markup(child) + escape(child.tail or "") for child in element
    )


def _outer_markup(element: ElementTree.Element) -> str:
    name = _local(element.tag)
    attributes = "".join(f" {_attribute_name(k)}={quoteattr(v)}" for k, v in element.attrib.items())
    inner = _inner_markup(element)
    return f"<{name}{attributes}>{inner}</{name}>" if inner else f"<{name}{attributes}/>"


def plain_text(value: Any) -> str:
    """The text of a field value, markup removed, each run of whitespace one space.

    Only an `#xhtml` value is markup; a string or `#text` is text as written.
    """
    if isinstance(value, Mapping):
        if "#xhtml" in value:
            value = html.unescape(re.sub(r"<[^>]*>", " ", value["#xhtml"]))
        else:
            value = value.get("#text", "")
    return " ".join(value.split()) if isinstance(value, str) else ""


# --- small readers ----------------------------------------------------------------------------


def _ns(tag: str) -> str:
    return tag[1:].partition("}")[0] if tag.startswith("{") else ""


def _local(tag: str) -> str:
    return tag.rpartition("}")[2]


def _attribute_name(key: str) -> str:
    if key.startswith(f"{{{XML_NS}}}"):
        return f"xml:{_local(key)}"
    if key.startswith(f"{{{XSI_NS}}}"):
        return f"xsi:{_local(key)}"
    return _local(key)


def _first(fields: Any, name: str) -> Any:
    values = fields.get(name) if isinstance(fields, Mapping) else None
    return values[0] if isinstance(values, tuple) and values else None


def _items(fields: Mapping[str, Any], container: str, item: str) -> list[Mapping[str, Any]]:
    """The `item` mappings inside an entry's `container` field, in file order."""
    found = []
    for holder in fields.get(container, ()) if isinstance(fields.get(container), tuple) else ():
        if isinstance(holder, Mapping):
            found += [v for v in holder.get(item, ()) if isinstance(v, Mapping)]
    return found


def _text_at(fields: Mapping[str, Any], *path: str) -> str | None:
    value: Any = fields
    for name in path:
        value = _first(value, name)
    text = plain_text(value)
    return text or None


def _optional(fields: Mapping[str, Any], key: str) -> str | None:
    value = fields.get(key)
    return value if isinstance(value, str) and value else None


def _attribute(name: str, label: str, fields: Mapping[str, Any], key: str) -> str:
    value = _optional(fields, key)
    if value is None:
        raise CweError(f"{name}: {label} has no {key[1:]}")
    return value


def _required_attribute(name: str, root: ElementTree.Element, key: str) -> str:
    value = root.get(key)
    if not value:
        raise CweError(f"{name}: Weakness_Catalog has no {key}")
    return value


def _schema_version(root: ElementTree.Element) -> str | None:
    location = root.get(f"{{{XSI_NS}}}schemaLocation", "").split()
    found = SCHEMA_FILE.search(location[-1]) if location else None
    return found.group(1) if found else None


def _number(cwe_id: str | int) -> int | None:
    if isinstance(cwe_id, int):
        return cwe_id
    text = str(cwe_id).strip()
    if text[:4].casefold() == "cwe-":
        text = text[4:]
    return int(text) if WHOLE_NUMBER.fullmatch(text) else None


def _whole(value: Any) -> bool:
    return isinstance(value, str) and WHOLE_NUMBER.fullmatch(value) is not None


def _by_nature(natures: Iterable[str]) -> dict[str, int]:
    """Counts per nature, in schema order, then membership, then any other by name."""
    counts = Counter(natures)
    rank = {n: i for i, n in enumerate((*NATURES, *MEMBERSHIP.values()))}
    return {n: counts[n] for n in sorted(counts, key=lambda n: (rank.get(n, len(rank)), n))}


def _catalog_number(item: Mapping[str, Any]) -> int:
    return int(item["catalog_ref"].rpartition("-")[2])


def _repeated(counts: Counter[tuple[str, str]], key: str) -> list[dict[str, Any]]:
    return [{"weakness": w, key: ref, "times": n} for (w, ref), n in counts.items() if n > 1]


def _thawed(value: Any) -> Any:
    """A JSON-ready copy of a read-only value: mappings become dicts, tuples lists."""
    if isinstance(value, Mapping):
        return {key: _thawed(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thawed(item) for item in value]
    return value
