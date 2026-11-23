"""Read tmodel's own weakness types, `tr-weak-NNNN`, to serve beside CWE's (#145; PLAN-0002 §5).

A weakness that MITRE's CWE does not have gets an id in tmodel's own namespace,
`tr-weak-NNNN`, with `source: local`. It slots into CWE's type system (the same
status, abstraction and structure values) and relationships (the same natures,
each tagged with a CWE view), so it is a weakness beside CWE's, not a second kind of
thing. This reads such weaknesses from one YAML file, the one `$TMODEL_LOCAL_WEAKNESSES`
names. Where the team keeps that file is not decided yet (DEC-008 holds the local
namespace), so nothing is read when the variable is not set.

The file:

    catalog:
      name: ...                    # what the file is
      version: ...
      maintainer:                  # who its Assertions are attributed to
        id: party:...
        name: ...
    weaknesses:
      - id: tr-weak-0001
        name: ...
        description: ...
        status: Draft              # CWE's values: Stable, Usable, Draft, Incomplete, ...
        abstraction: Base          # optional; CWE's values: Pillar, Class, Base, ...
        structure: Simple          # optional; CWE's values: Simple, Chain, Composite
        alternate_terms: [...]     # optional
        relationships:             # optional; each one like a CWE Related_Weakness
          - nature: ChildOf        # CWE's natures, or MemberOf
            target: CWE-710        # a CWE id, or a tr-weak id in this file
            view: CWE-1000         # the CWE view it belongs to
            ordinal: Primary       # optional
            chain: CWE-692         # optional, a named chain's id
        attack_patterns: [CAPEC-1] # optional
        observed_examples:         # optional
          - reference: ...         # a CVE id becomes a Vulnerability, as in CWE
            description: ...
            link: https://...      # optional
        extensions: {...}          # optional, free-form, kept as written

The file is written by hand, so every key is checked: a key this reader does not
know, a key given twice and a YAML alias are refused rather than read past.
Read-only and deterministic, like the CWE reader.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import threading
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import MappingProxyType
from typing import Any, ClassVar

import yaml

from engine.load import cwe

# Names the YAML file of local weakness types the engine reads.
LOCAL_ENV = "TMODEL_LOCAL_WEAKNESSES"
# What a local weakness says it comes from (PLAN-0002 §5).
SOURCE = "local"
# A file written by hand is far smaller than this; a larger one is refused unread.
MAX_FILE_BYTES = 4 * 1024 * 1024
LOCAL_ID = re.compile(r"tr-weak-([0-9]{4})")
CAPEC_ID = re.compile(r"CAPEC-[0-9]+")
PARTY_ID = re.compile(r"party:[a-z0-9]+(?:-[a-z0-9]+)*")
URL = re.compile(r"https?://\S+")
# CWE XML Schema 7.3's own values (StatusEnumeration, AbstractionEnumeration,
# StructureEnumeration), so a local weakness filters and sorts as a CWE one does.
STATUSES = ("Stable", "Usable", "Draft", "Incomplete", "Obsolete", "Deprecated")
ABSTRACTIONS = ("Pillar", "Class", "Base", "Variant", "Compound")
STRUCTURES = ("Simple", "Chain", "Composite")
# A local weakness writes CWE's natures, or MemberOf. HasMember is a category's or a
# view's, and a local weakness is neither.
NATURES = (*cwe.NATURES, "MemberOf")
# The keys each part of the file may hold, and the ones it must.
TOP_KEYS = ("catalog", "weaknesses")
CATALOG_KEYS = ("name", "version", "maintainer")
MAINTAINER_KEYS = ("id", "name")
WEAKNESS_KEYS = (
    "id",
    "name",
    "description",
    "status",
    "abstraction",
    "structure",
    "alternate_terms",
    "relationships",
    "attack_patterns",
    "observed_examples",
    "extensions",
)
WEAKNESS_REQUIRED = ("id", "name", "description", "status")
RELATIONSHIP_KEYS = ("nature", "target", "view", "ordinal", "chain")
RELATIONSHIP_REQUIRED = ("nature", "target", "view")
EXAMPLE_KEYS = ("reference", "description", "link")
EXAMPLE_REQUIRED = ("reference", "description")


class LocalWeaknessError(ValueError):
    """The file cannot be read: not a regular file, too large, bad YAML or a bad entry."""


@dataclass(frozen=True)
class LocalWeakness:
    """One local weakness type, with the attributes a CWE weakness entry has.

    So the table, the entry answer and the objects serve both alike. A local weakness
    has no Mapping_Notes, likelihood, mitigations or page on cwe.mitre.org, so those
    are empty.
    """

    number: int
    name: str
    status: str
    description: str
    fields: Mapping[str, Any] = field(compare=False, repr=False)  # the entry as written
    abstraction: str | None = None
    structure: str | None = None
    alternate_terms: tuple[str, ...] = ()
    attack_patterns: tuple[str, ...] = ()  # CAPEC ids, in file order, each once
    observed_examples: tuple[cwe.ObservedExample, ...] = ()
    relationships: tuple[cwe.Relationship, ...] = ()  # the ones it writes, in file order

    kind: ClassVar[str] = "Weakness"
    source: ClassVar[str] = SOURCE
    view_type: ClassVar[None] = None
    usage: ClassVar[None] = None
    likelihood: ClassVar[None] = None
    mitigations: ClassVar[int] = 0
    url: ClassVar[None] = None

    @property
    def id(self) -> str:
        return local_id(self.number)

    @property
    def object_id(self) -> str:
        """The tmodel Weakness id, as PLAN-0002 §5 and DL-0026 write it: weakness:tr-weak-NNNN."""
        return f"weakness:{self.id}"

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready, with the keys of `CweEntry.to_dict` in the same order."""
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
class LocalCatalog:
    """One file of local weakness types: what it says it is, and its weaknesses in file order."""

    name: str
    version: str
    maintainer: str  # the Party id its Assertions are attributed to
    maintainer_name: str
    file: str  # the file's name only, so an answer names no local path
    sha256: str
    weaknesses: tuple[LocalWeakness, ...]

    @cached_property
    def _by_number(self) -> Mapping[int, LocalWeakness]:
        return MappingProxyType({w.number: w for w in self.weaknesses})

    def get(self, weakness_id: str) -> LocalWeakness | None:
        """The weakness with this id, such as `tr-weak-0001`, in any case."""
        number = local_number(weakness_id)
        return self._by_number.get(number) if number is not None else None

    @cached_property
    def stated_relationships(self) -> tuple[cwe.Relationship, ...]:
        """Every relationship the file writes, weakness by weakness in file order."""
        return tuple(r for w in self.weaknesses for r in w.relationships)

    @cached_property
    def objects(self) -> Mapping[str, tuple[Mapping[str, Any], ...]]:
        """`to_objects()` for every weakness, built once."""
        built = to_objects(self)
        return MappingProxyType({name: tuple(items) for name, items in built.items()})

    def summary(self) -> dict[str, Any]:
        """Which file an answer's local weaknesses come from. Names no local path."""
        return {
            "name": self.name,
            "version": self.version,
            "file": self.file,
            "sha256": self.sha256,
            "maintainer": self.maintainer,
            "weaknesses": len(self.weaknesses),
        }


def local_id(number: int) -> str:
    """The id of local weakness `number`: tr-weak-0001."""
    return f"tr-weak-{number:04d}"


def local_number(text: str) -> int | None:
    """The number in a local weakness id (`tr-weak-0001`, in any case), or None."""
    found = LOCAL_ID.fullmatch(text.strip().lower()) if isinstance(text, str) else None
    return int(found.group(1)) if found else None


def configured_file() -> Path | None:
    """The file `$TMODEL_LOCAL_WEAKNESSES` names, or None when it is not set."""
    configured = os.environ.get(LOCAL_ENV, "").strip()
    return Path(os.path.expanduser(configured)) if configured else None


def load_local(path: str | Path) -> LocalCatalog:
    """Read the local weakness types in the YAML file at `path`; LocalWeaknessError if it cannot."""
    path = Path(path)
    data = _read(path)
    return _from_bytes(path.name, data, hashlib.sha256(data).hexdigest())


_cache_lock = threading.Lock()
_cache: dict[str, tuple[str, LocalCatalog]] = {}


def cached_local(path: str | Path) -> LocalCatalog:
    """`load_local(path)`, kept until the file's bytes change."""
    path = Path(path)
    data = _read(path)
    digest = hashlib.sha256(data).hexdigest()
    with _cache_lock:
        cached = _cache.get(str(path))
        if cached is not None and cached[0] == digest:
            return cached[1]
        local = _from_bytes(path.name, data, digest)
        _cache[str(path)] = (digest, local)
        return local


def to_objects(
    local: LocalCatalog, numbers: Iterable[int] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """The tmodel objects for the file's weaknesses (all, or those numbered), as CWE's are made.

    One Weakness per local weakness, with `id` weakness:tr-weak-NNNN and `catalog_ref`
    tr-weak-NNNN, and the same AttackPatterns, Vulnerabilities and proposed
    Assertions `cwe.to_objects` makes, attributed to the file's maintainer. Nobody has
    reviewed them, so they stay proposed (R-018).
    """
    wanted = set(numbers) if numbers is not None else None
    party = {"id": local.maintainer, "name": local.maintainer_name, "party_kind": "organization"}
    provenance = (
        f"tmodel local weaknesses: {local.name} {local.version}, {local.file}, "
        f"SHA-256 {local.sha256}"
    )
    return cwe.objects_for(
        [w for w in local.weaknesses if wanted is None or w.number in wanted], party, provenance
    )


# --- reading the file ---------------------------------------------------------------------


def _read(path: Path) -> bytes:
    """The bytes of `path`, a regular file of at most MAX_FILE_BYTES, as the CWE reader reads.

    The open file's type and size are checked before anything is read, so a FIFO or a
    device is refused rather than waited on or read without end.
    """
    too_large = f"{path.name}: larger than {MAX_FILE_BYTES} bytes, so it is not read"
    try:
        # O_NONBLOCK: opening a FIFO with no writer returns at once, so it can be refused
        no_wait = getattr(os, "O_NONBLOCK", 0)
        with open(path, "rb", opener=lambda p, flags: os.open(p, flags | no_wait)) as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise LocalWeaknessError(f"{path.name}: not a regular file, so it is not read")
            if info.st_size > MAX_FILE_BYTES:
                raise LocalWeaknessError(too_large)
            data = handle.read(MAX_FILE_BYTES + 1)
    except OSError as exc:
        raise LocalWeaknessError(f"{path.name}: cannot read ({exc.strerror or exc})") from exc
    if len(data) > MAX_FILE_BYTES:  # it grew after the check
        raise LocalWeaknessError(too_large)
    return data


class _Loader(yaml.BaseLoader):
    """Strings, lists and mappings only, as the library loader reads YAML.

    Also refuses a YAML alias, which a hand-written file has no need of and which can
    make a small file expand without end, and a key given twice, which YAML would
    otherwise drop silently.
    """

    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()
            raise yaml.composer.ComposerError(
                None, None, f"uses the alias *{event.anchor}; write the value out", event.start_mark
            )
        return super().compose_node(parent, index)

    def construct_mapping(self, node: Any, deep: bool = False) -> Any:
        seen: set[str] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if isinstance(key, str) and key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"the key {key!r} is given twice", key_node.start_mark
                )
            if isinstance(key, str):
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


def _from_bytes(name: str, data: bytes, digest: str) -> LocalCatalog:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LocalWeaknessError(f"{name}: not UTF-8 text") from exc
    try:
        doc = yaml.load(text, Loader=_Loader)  # strings, lists and mappings; builds no objects
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark else ""
        reason = " ".join(str(getattr(exc, "problem", None) or exc).split())
        raise LocalWeaknessError(f"{name}: not valid YAML{where} ({reason})") from exc
    top = _mapping(name, "the file", doc, TOP_KEYS, TOP_KEYS)
    catalog = _mapping(name, "catalog", top["catalog"], CATALOG_KEYS, CATALOG_KEYS)
    maintainer = _mapping(
        name, "catalog.maintainer", catalog["maintainer"], MAINTAINER_KEYS, MAINTAINER_KEYS
    )
    party = _text(name, "catalog.maintainer.id", maintainer["id"])
    if not PARTY_ID.fullmatch(party):
        raise LocalWeaknessError(
            f"{name}: catalog.maintainer.id: a party id looks like party:tmodel-team, not {party!r}"
        )
    items = top["weaknesses"]
    if not isinstance(items, list):
        raise LocalWeaknessError(f"{name}: weaknesses: expected a list")
    weaknesses = [_weakness(name, i, item) for i, item in enumerate(items)]
    twice = [local_id(n) for n, times in Counter(w.number for w in weaknesses).items() if times > 1]
    if twice:
        raise LocalWeaknessError(f"{name}: {', '.join(twice)} given more than once")
    ids = {w.id for w in weaknesses}
    for w in weaknesses:
        for r in w.relationships:
            for kind, value in (("target", r.target), ("chain", r.chain)):
                if value is not None and value.startswith("tr-weak-") and value not in ids:
                    raise LocalWeaknessError(
                        f"{name}: {w.id}: a {r.nature} names the {kind} {value}, "
                        "which is not a weakness in this file"
                    )
    return LocalCatalog(
        name=_text(name, "catalog.name", catalog["name"]),
        version=_text(name, "catalog.version", catalog["version"]),
        maintainer=party,
        maintainer_name=_text(name, "catalog.maintainer.name", maintainer["name"]),
        file=name,
        sha256=digest,
        weaknesses=tuple(weaknesses),
    )


def _weakness(name: str, index: int, item: Any) -> LocalWeakness:
    where = f"weaknesses[{index}]"  # until its id is known, so later errors can name it
    if not isinstance(item, dict):
        raise LocalWeaknessError(f"{name}: {where}: expected a mapping")
    if "id" not in item:
        raise LocalWeaknessError(f"{name}: {where}: 'id' is missing")
    number = local_number(item["id"]) if isinstance(item["id"], str) else None
    if number is None or item["id"] != local_id(number):
        raise LocalWeaknessError(
            f"{name}: {where}: an id looks like tr-weak-0001, not {item['id']!r}"
        )
    label = local_id(number)
    entry = _mapping(name, label, item, WEAKNESS_KEYS, WEAKNESS_REQUIRED)
    relationships = _list(name, f"{label}.relationships", entry.get("relationships"))
    examples = _list(name, f"{label}.observed_examples", entry.get("observed_examples"))
    extensions = entry.get("extensions")
    if extensions is not None and not isinstance(extensions, dict):
        raise LocalWeaknessError(f"{name}: {label}.extensions: expected a mapping")
    return LocalWeakness(
        number=number,
        name=_text(name, f"{label}.name", entry["name"]),
        status=_one_of(name, f"{label}.status", entry["status"], STATUSES),
        description=_text(name, f"{label}.description", entry["description"]),
        fields=_frozen(entry),
        abstraction=_optional_one_of(name, label, entry, "abstraction", ABSTRACTIONS),
        structure=_optional_one_of(name, label, entry, "structure", STRUCTURES),
        alternate_terms=tuple(
            _text(name, f"{label}.alternate_terms", t)
            for t in _list(name, f"{label}.alternate_terms", entry.get("alternate_terms"))
        ),
        attack_patterns=tuple(
            dict.fromkeys(
                _capec(name, f"{label}.attack_patterns", p)
                for p in _list(name, f"{label}.attack_patterns", entry.get("attack_patterns"))
            )
        ),
        observed_examples=tuple(
            _example(name, f"{label}.observed_examples[{i}]", e) for i, e in enumerate(examples)
        ),
        relationships=tuple(
            _relationship(name, f"{label}.relationships[{i}]", label, r)
            for i, r in enumerate(relationships)
        ),
    )


def _relationship(name: str, where: str, label: str, item: Any) -> cwe.Relationship:
    r = _mapping(name, where, item, RELATIONSHIP_KEYS, RELATIONSHIP_REQUIRED)
    nature = _one_of(name, f"{where}.nature", r["nature"], NATURES)
    target = _weakness_ref(name, f"{where}.target", r["target"])
    if target == label:
        raise LocalWeaknessError(f"{name}: {where}: {label} cannot name itself")
    view = _view(name, f"{where}.view", r["view"])
    ordinal = None
    if "ordinal" in r:
        ordinal = _one_of(name, f"{where}.ordinal", r["ordinal"], ("Primary",))
    chain = _weakness_ref(name, f"{where}.chain", r["chain"]) if "chain" in r else None
    return cwe.Relationship(
        source=label, nature=nature, target=target, view=view, ordinal=ordinal, chain=chain
    )


def _example(name: str, where: str, item: Any) -> cwe.ObservedExample:
    e = _mapping(name, where, item, EXAMPLE_KEYS, EXAMPLE_REQUIRED)
    link = None
    if "link" in e:
        link = _text(name, f"{where}.link", e["link"])
        if not URL.fullmatch(link):
            raise LocalWeaknessError(f"{name}: {where}.link: expected an http or https URL")
    return cwe.ObservedExample(
        reference=_text(name, f"{where}.reference", e["reference"]),
        description=_text(name, f"{where}.description", e["description"]),
        link=link,
    )


# --- small readers ----------------------------------------------------------------------------


def _mapping(
    name: str, where: str, value: Any, keys: tuple[str, ...], required: tuple[str, ...]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LocalWeaknessError(f"{name}: {where}: expected a mapping")
    for key in value:
        if key not in keys:
            raise LocalWeaknessError(
                f"{name}: {where}: unknown key {key!r}; the keys are {', '.join(keys)}"
            )
    for key in required:
        if key not in value:
            raise LocalWeaknessError(f"{name}: {where}: {key!r} is missing")
    return value


def _list(name: str, where: str, value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise LocalWeaknessError(f"{name}: {where}: expected a list")
    return value


def _text(name: str, where: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LocalWeaknessError(f"{name}: {where}: expected a text")
    return " ".join(value.split())


def _one_of(name: str, where: str, value: Any, allowed: tuple[str, ...]) -> str:
    text = _text(name, where, value)
    if text not in allowed:
        raise LocalWeaknessError(f"{name}: {where}: {text!r} is not one of {', '.join(allowed)}")
    return text


def _optional_one_of(
    name: str, label: str, entry: Mapping[str, Any], key: str, allowed: tuple[str, ...]
) -> str | None:
    return _one_of(name, f"{label}.{key}", entry[key], allowed) if key in entry else None


def _weakness_ref(name: str, where: str, value: Any) -> str:
    """A CWE id as CWE-79, or a local id as tr-weak-0001."""
    text = _text(name, where, value)
    number = local_number(text)
    if number is not None:
        return local_id(number)
    if text.upper().startswith("CWE-") and cwe.WHOLE_NUMBER.fullmatch(text[4:]):
        return f"CWE-{int(text[4:])}"
    raise LocalWeaknessError(f"{name}: {where}: expected a CWE-79 or tr-weak-0001 id, not {text!r}")


def _view(name: str, where: str, value: Any) -> int:
    text = _text(name, where, value)
    digits = text[4:] if text.upper().startswith("CWE-") else text
    if not cwe.WHOLE_NUMBER.fullmatch(digits):
        raise LocalWeaknessError(f"{name}: {where}: a view id looks like CWE-1000, not {text!r}")
    return int(digits)


def _capec(name: str, where: str, value: Any) -> str:
    text = _text(name, where, value)
    if not CAPEC_ID.fullmatch(text):
        raise LocalWeaknessError(f"{name}: {where}: a CAPEC id looks like CAPEC-63, not {text!r}")
    return f"CAPEC-{int(text[6:])}"


def _frozen(value: Any) -> Any:
    """A read-only copy: mappings become read-only, lists tuples."""
    if isinstance(value, dict):
        return MappingProxyType({key: _frozen(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_frozen(item) for item in value)
    return value


def _thawed(value: Any) -> Any:
    """A JSON-ready copy of a read-only value: mappings become dicts, tuples lists."""
    if isinstance(value, Mapping):
        return {key: _thawed(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thawed(item) for item in value]
    return value
