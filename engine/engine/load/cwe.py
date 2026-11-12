"""Read MITRE's CWE List into typed entries, keeping every field (#144, #61; PLAN-0002 §5).

Input is the CWE List as MITRE publishes it, `cwec_vX.Y.xml.zip` or the XML inside
it, written to CWE XML Schema 7 (namespace `http://cwe.mitre.org/cwe-7`). Which
release the engine reads is the library's call: its `cwe` record pins the file's
SHA-256 (Threat-Radar/library#21), and `load_catalog` refuses any other bytes.

Lossless: every element and attribute of an entry is kept in `CweEntry.fields`, so a
CWE field that has no tmodel slot is carried, not dropped. `CweCatalog.report()`
says, field by field, where each entry field goes in the object model and how many
entries carry it, and `CweCatalog.unknown` lists any entry field this reader does
not know, such as one a newer schema adds. Nothing is dropped silently.

`to_objects()` maps the weaknesses onto the accepted object model (ADR-0010,
ADR-0011): one Weakness per CWE weakness, and a proposed Assertion for each CAPEC
and CVE link CWE gives (DL-0050).

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
import threading
import zipfile
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import MappingProxyType
from typing import Any
from xml.etree import ElementTree
from xml.sax.saxutils import escape, quoteattr

CWE_NS = "http://cwe.mitre.org/cwe-7"  # CWE XML Schema 7.x; CWE 5.0 (schema 8) is not read
XHTML_NS = "http://www.w3.org/1999/xhtml"
XML_NS = "http://www.w3.org/XML/1998/namespace"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
# Names the CWE catalog file the engine reads (the library record pins its digest).
CATALOG_ENV = "TMODEL_CWE_CATALOG"
# The library record that pins the release: content.url and content.sha256.
LIBRARY_RECORD = "cwe"
# The 4.21 XML is 18.6 MB. A zip whose XML claims more than this is refused.
MAX_XML_BYTES = 256 * 1024 * 1024
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
# in schema order (library record `cwe`, distilled/messages.yaml). A field outside these
# lists is still kept, and is reported in CweCatalog.unknown.
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

    @property
    def id(self) -> str:
        return f"CWE-{self.number}"

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
    has instead. Raises CweError for a file that is not a CWE Schema 7 catalog.
    """
    path = Path(path)
    return _from_bytes(path.name, _read(path), sha256)


def configured_catalog() -> Path | None:
    """The catalog file `$TMODEL_CWE_CATALOG` names, or None when it is not set.

    The engine never fetches the catalog itself: whether it is bundled, cached or
    fetched at install is DEC-008, still open.
    """
    configured = os.environ.get(CATALOG_ENV, "").strip()
    return Path(os.path.expanduser(configured)) if configured else None


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

    Categories and views are not objects: a category is not a mapping target, and
    the hierarchy is #145. An observed example without a CVE id stays on its entry.
    """
    wanted = set(numbers) if numbers is not None else None
    provenance = (
        f"tmodel CWE import: {catalog.name} {catalog.version} ({catalog.date}), "
        f"{catalog.file}, SHA-256 {catalog.sha256}"
    )
    weaknesses: list[dict[str, Any]] = []
    patterns: dict[str, dict[str, Any]] = {}
    vulnerabilities: dict[str, dict[str, Any]] = {}
    assertions: dict[str, dict[str, Any]] = {}
    for entry in catalog.weaknesses:
        if wanted is not None and entry.number not in wanted:
            continue
        weakness = weakness_id(entry.number)
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
                    "asserted_by": MITRE_PARTY,
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
                "asserted_by": MITRE_PARTY,
                "generated_by": provenance,
            }
            if example.link:
                statement["evidence"] = [example.link]
            assertions.setdefault(assertion, statement)
    return {
        "parties": [{"id": MITRE_PARTY, "name": "MITRE CWE Program", "party_kind": "organization"}],
        "weaknesses": weaknesses,
        "attack_patterns": sorted(patterns.values(), key=lambda p: _catalog_number(p)),
        "vulnerabilities": sorted(vulnerabilities.values(), key=lambda v: v["catalog_ref"]),
        "assertions": list(assertions.values()),
    }


# --- reading the file ---------------------------------------------------------------------


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise CweError(f"{path.name}: cannot read ({exc.strerror or exc})") from exc


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
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, EOFError) as exc:
        raise CweError(f"{name}: not a readable zip ({exc})") from exc
    if len(xml) > MAX_XML_BYTES:
        raise CweError(f"{name}: {members[0].filename} is larger than {MAX_XML_BYTES} bytes")
    return xml


def _parse(name: str, xml: bytes) -> ElementTree.Element:
    start = xml.find(b"<Weakness_Catalog")
    if start < 0:
        raise CweError(f"{name}: not a CWE catalog (no Weakness_Catalog element)")
    if b"<!DOCTYPE" in xml[:start] or b"<!ENTITY" in xml[:start]:
        raise CweError(f"{name}: has a DOCTYPE; a CWE catalog has none, so it is not read")
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
    )


# --- elements to values ---------------------------------------------------------------------


def _value(element: ElementTree.Element) -> Any:
    """One element as a JSON-ready value, by the rules in the module docstring."""
    attributes = {f"@{_attribute_name(k)}": v for k, v in element.attrib.items()}
    children = list(element)
    text = element.text or ""
    mixed = any(_ns(c.tag) != CWE_NS for c in children) or (
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
        items = tuple(MappingProxyType({_local(c.tag): _value(c)}) for c in children)
        return MappingProxyType({**attributes, "#items": items})
    grouped: dict[str, list[Any]] = {}
    for child in children:
        grouped.setdefault(_local(child.tag), []).append(_value(child))
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
