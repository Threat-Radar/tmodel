"""Engine operations, independent of transport.

The local API and the CLI both call these functions, so the GUI and the CLI
always run the same engine code (APP-0001 A-030 boundary, A-060 CLI parity).
"""

from __future__ import annotations

import platform
import sys
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

from engine import __version__, tara_gate
from engine import propose as proposals
from engine import sdl as sdl_view
from engine import tara as tara_view
from engine.graph import AttackGraph, GraphError
from engine.load import capec, cwe, local_weaknesses
from engine.load.library import (
    Library,
    LibraryError,
    LibraryRecord,
    cached_library,
    configured_root,
)
from engine.load.vector import MODEL_SUFFIXES, load_vector, load_vector_document
from engine.model_graph import project_model_graph
from engine.paths import enumerate_paths
from engine.risk import assess_document

ENGINE_NAME = "tmodel-engine"
# PyInstaller unpacks the one-file sidecar and its data below _MEIPASS. In a
# source checkout, the examples live at the repository root instead. Neither
# location depends on the app's working directory or a developer's checkout.
APPROVED_VECTOR_DIRECTORY = (
    (Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2])
    / "spec"
    / "vectors"
)
# The MAP-0001 crosswalk the SDL view reads (bundled beside spec/vectors by bin/build-engine).
CROSSWALK_FILE = APPROVED_VECTOR_DIRECTORY.parent / "MAP-0001.yaml"
SDL_PREFIX = "sdl-"  # SDL models are spec/vectors/sdl-*.yaml (DL-0040)
SDL_OPTIONS = ("file", "program")
LIBRARY_FILTERS = ("id", "type", "topic", "status")
# The library table view (#141, #58): what it can sort by, and what it counts for filter menus.
TABLE_OPTIONS = ("search", "sort", "order", "limit", "offset")
TABLE_SORTS = ("id", "title", "type", "shelf", "status", "maturity", "date", "publisher", "topic")
TABLE_FACETS = ("type", "status", "topic")
# The weakness table view (#144, #234): exact filters, sorts and facet counts over CWE weaknesses.
WEAKNESS_FILTERS = ("abstraction", "structure", "status", "usage")
WEAKNESS_SORTS = ("id", "name", "abstraction", "structure", "status", "usage", "likelihood")
WEAKNESS_FACETS = WEAKNESS_FILTERS
# CWE's own order for its enumerations, which a sort follows; other values come after, by name.
WEAKNESS_ORDER = {
    "abstraction": ("Pillar", "Class", "Base", "Variant", "Compound"),
    "structure": ("Simple", "Chain", "Composite"),
    "status": ("Stable", "Usable", "Draft", "Incomplete", "Obsolete", "Deprecated"),
    "usage": ("Allowed", "Allowed-with-Review", "Discouraged", "Prohibited"),
    "likelihood": ("High", "Medium", "Low", "Unknown"),
}
# The weakness relationships (#145): any list of views, one entry, inverses or not, paged.
RELATIONSHIP_OPTIONS = ("view", "id", "derived", "limit", "offset")
# A weakness the table and the answers serve: CWE's, or a local one (#145).
_Weakness = cwe.CweEntry | local_weaknesses.LocalWeakness
# The attack-pattern table view (#244, #236): exact filters, sorts and facet counts over
# CAPEC attack patterns, with CAPEC's own order for its enumerations (ap_schema_v3.5.xsd).
ATTACK_PATTERN_FILTERS = ("abstraction", "status", "likelihood", "severity")
ATTACK_PATTERN_SORTS = ("id", "name", "abstraction", "status", "likelihood", "severity")
ATTACK_PATTERN_FACETS = ATTACK_PATTERN_FILTERS
ATTACK_PATTERN_ORDER = {
    "abstraction": ("Meta", "Standard", "Detailed"),
    "status": ("Stable", "Usable", "Draft", "Incomplete", "Obsolete", "Deprecated"),
    "likelihood": ("High", "Medium", "Low", "Unknown"),
    "severity": ("Very High", "High", "Medium", "Low", "Very Low"),
}
# The example-model families, told apart by file-name prefix (spec/vectors/README.md).
# The order is the order the model list uses.
MODEL_KINDS = (
    ("mvp-", "core", "Core example"),
    ("tv-", "worked", "Worked example with governance"),
    ("pv-", "proposal", "Proposal example (AI-drafted, unreviewed)"),
)
# Schema test harnesses live beside the models but are not models.
HARNESS_SUFFIX = ".linkml.yaml"
# What a model summary counts: summary name -> model collection.
MODEL_COUNTS = (
    ("assets", "assets"),
    ("components", "components"),
    ("damage_scenarios", "damage_scenarios"),
    ("threats", "threat_instances"),
    ("attack_paths", "attack_paths"),
    ("mitigations", "mitigations"),
    ("risk_scores", "risk_scores"),
    ("requirements", "requirements"),
)


class Unavailable(RuntimeError):
    """Something the engine needs is missing, such as the library (the API answers 503)."""


def version() -> dict[str, Any]:
    """Engine and runtime version."""
    return {
        "engine": ENGINE_NAME,
        "version": __version__,
        "python": platform.python_version(),
    }


def health() -> dict[str, Any]:
    """Liveness check. Grows real checks (store reachable, library loaded) later."""
    return {"status": "ok", **version()}


def _values(query: Mapping[str, str], allowed: tuple[str, ...], noun: str) -> dict[str, str]:
    """The query's values, each checked to be one of `allowed` and to be non-empty."""
    values: dict[str, str] = {}
    for name, value in query.items():
        if name not in allowed:
            known = (
                allowed[0] if len(allowed) == 1 else ", ".join(allowed[:-1]) + " or " + allowed[-1]
            )
            raise ValueError(f"unknown {noun} {name!r}: use {known}")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{noun} {name!r} needs a value")
        values[name] = value.strip()
    return values


def _served_library() -> Library:
    root = configured_root()
    try:
        return cached_library(root)
    except LibraryError as exc:
        raise Unavailable(
            f"no library at {root}: check out the submodule "
            "(git submodule update --init library) or set TMODEL_LIBRARY to a library checkout"
        ) from exc


def _matching(records: Iterable[LibraryRecord], filters: Mapping[str, str]) -> list[LibraryRecord]:
    return [r for r in records if all(getattr(r, k) == v for k, v in filters.items())]


def library_records(filters: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The library's records, optionally filtered by id, type, topic and status (#140).

    A filter keeps the records whose field equals its value; several filters must
    all match, so `id` alone returns one record. The library is the one
    `configured_root()` names. Records that fail to load are left out and listed
    under `library.problems`, so a screen can still open. Raises ValueError for an
    unknown or empty filter, and Unavailable when there is no library to read.
    """
    wanted = _values(filters or {}, LIBRARY_FILTERS, "filter")
    library = _served_library()
    records = _matching(library, wanted)
    return {
        "library": {
            "root": library.root,
            "digest": library.digest,
            "count": len(library),
            "problems": list(library.problems),
        },
        "filters": wanted,
        "count": len(records),
        "records": [r.to_dict() for r in records],
    }


def library_table(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Rows for the library table views (#141, #58): filtered, searched, sorted, paged.

    Parameters, all optional: the `library_records` filters; `search`, a text that
    must appear (ignoring case) in a record's id, title, short title, publisher,
    topic or tags; `sort`, one of TABLE_SORTS (default `id`); `order`, `asc` or
    `desc`; and `limit` and `offset` for paging. Records without a value for the
    sort field come last in both orders, and ties keep id order. `total` counts
    the matches before paging. `facets` contains whole-library counts for type,
    status, and topic. `contextual_facets` applies the current search and the
    other exact filters, excluding each facet's own filter so a user can switch
    its selection. The payload names no local path, so a saved copy is the same
    on every machine.
    """
    values = _values(query or {}, LIBRARY_FILTERS + TABLE_OPTIONS, "parameter")
    sort = values.get("sort", "id")
    if sort not in TABLE_SORTS:
        raise ValueError(f"cannot sort by {sort!r}: use one of {', '.join(TABLE_SORTS)}")
    order = values.get("order", "asc")
    if order not in ("asc", "desc"):
        raise ValueError(f"order must be asc or desc, not {order!r}")
    limit = _whole_number(values, "limit", minimum=1)
    offset = _whole_number(values, "offset", minimum=0) or 0
    search = values.get("search")

    library = _served_library()
    filters = {k: v for k, v in values.items() if k in LIBRARY_FILTERS}
    searched = _searched(library, search)
    matched = _matching(searched, filters)
    matched = _sorted(matched, sort, descending=order == "desc")
    page = matched[offset : offset + limit if limit is not None else None]
    return {
        "library": {
            "digest": library.digest,
            "count": len(library),
            "problems": list(library.problems),
        },
        "query": {
            "filters": filters,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
        "total": len(matched),
        "count": len(page),
        "rows": [_row(r) for r in page],
        "facets": {name: _counts(library, name) for name in TABLE_FACETS},
        "contextual_facets": {
            name: _counts(
                _matching(searched, {key: value for key, value in filters.items() if key != name}),
                name,
            )
            for name in TABLE_FACETS
        },
    }


def _counts(records: Iterable[LibraryRecord], field: str) -> dict[str, int]:
    """How many records have each value of `field`, in value order; blanks are not counted."""
    return dict(sorted(Counter(getattr(r, field) for r in records if getattr(r, field)).items()))


def _whole_number(values: Mapping[str, str], name: str, minimum: int) -> int | None:
    if name not in values:
        return None
    text = values[name]
    if not (text.isascii() and text.isdigit()) or int(text) < minimum:
        raise ValueError(f"{name} must be a whole number of at least {minimum}, not {text!r}")
    return int(text)


def _searchable(r: LibraryRecord) -> str:
    fields = [r.id, r.title, r.short_title, r.publisher, r.topic, *r.tags]
    return " ".join(f for f in fields if f).casefold()


def _searched(records: Iterable[LibraryRecord], search: str | None) -> list[LibraryRecord]:
    """Records matching the table's text search, or every record when search is absent."""
    if search is None:
        return list(records)
    needle = search.casefold()
    return [record for record in records if needle in _searchable(record)]


def _sort_value(r: LibraryRecord, field: str) -> str | None:
    value = r.body if field == "shelf" else getattr(r, field)
    return value.casefold() if value else None


def _sorted(records: list[LibraryRecord], field: str, descending: bool) -> list[LibraryRecord]:
    by_id = sorted(records, key=lambda r: r.id)
    present = [r for r in by_id if _sort_value(r, field) is not None]
    missing = [r for r in by_id if _sort_value(r, field) is None]
    present.sort(key=lambda r: _sort_value(r, field), reverse=descending)  # stable: ties by id
    return present + missing


def _row(r: LibraryRecord) -> dict[str, Any]:
    """One table row: what a list of documents shows, plus the key to fetch the rest."""
    return {
        "id": r.id,
        "title": r.title,
        "short_title": r.short_title,
        "type": r.type,
        "shelf": r.body,
        "status": r.status,
        "maturity": r.maturity,
        "date": r.date,
        "publisher": r.publisher,
        "topic": r.topic,
        "tags": list(r.tags),
        "url": r.content.url,
        "artifacts": len(r.artifacts),
        "reviewed_artifacts": sum(1 for a in r.artifacts if a.reviewed),
        "profile": r.profile,
    }


def _served_catalog() -> cwe.CweCatalog:
    """The CWE release the library pins, read from the file `$TMODEL_CWE_CATALOG` names."""
    record = _served_library().get(cwe.LIBRARY_RECORD)
    pinned = record.content.sha256 if record is not None else None
    if record is None or not pinned:
        raise Unavailable(
            "the library pins no CWE release: its cwe record has no content.sha256 "
            "(the CWE extraction is Threat-Radar/library#21); set TMODEL_LIBRARY to a "
            "library checkout that has it"
        )
    path = cwe.configured_catalog()
    if path is None:
        raise Unavailable(
            f"no CWE catalog: download {record.content.url} (SHA-256 {pinned}) "
            f"and set {cwe.CATALOG_ENV} to that file"
        )
    try:
        return cwe.cached_catalog(path, pinned)
    except cwe.CweError as exc:
        raise Unavailable(str(exc)) from exc


def _served_local() -> local_weaknesses.LocalCatalog | None:
    """The local weakness types `$TMODEL_LOCAL_WEAKNESSES` names, or None when it names none."""
    path = local_weaknesses.configured_file()
    if path is None:
        return None
    try:
        return local_weaknesses.cached_local(path)
    except local_weaknesses.LocalWeaknessError as exc:
        raise Unavailable(f"{exc} (the file {local_weaknesses.LOCAL_ENV} names)") from exc


def _weakness_entry_id(text: str) -> str:
    """A weakness id as the answers write it: CWE-79, or a local tr-weak-0001."""
    number = local_weaknesses.local_number(text)
    if number is not None:
        return local_weaknesses.local_id(number)
    try:
        return f"CWE-{cwe.cwe_number(text)}"
    except ValueError as exc:
        raise ValueError(f"{exc} (a local weakness id looks like tr-weak-0001)") from exc


def _stated(
    catalog: cwe.CweCatalog, local: local_weaknesses.LocalCatalog | None
) -> tuple[cwe.Relationship, ...]:
    """The relationships the CWE release and the local weaknesses write, CWE's first."""
    return catalog.stated_relationships + (local.stated_relationships if local is not None else ())


def _catalog_summary(catalog: cwe.CweCatalog) -> dict[str, Any]:
    """Which CWE release an answer comes from, with MITRE's notice and licence.

    Every answer that holds CWE content carries them, as the CWE Terms of Use require
    of a copy. Names no local path.
    """
    return {
        "name": catalog.name,
        "version": catalog.version,
        "date": catalog.date,
        "schema": catalog.schema,
        "file": catalog.file,
        "sha256": catalog.sha256,
        "weaknesses": len(catalog.weaknesses),
        "categories": len(catalog.categories),
        "views": len(catalog.views),
        "references": len(catalog.references),
        "unknown_fields": len(catalog.unknown),
        "notice": cwe.notice(catalog),
        "license": cwe.LICENSE,
        "terms_url": cwe.TERMS_URL,
    }


def weaknesses(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The CWE release the engine serves (#144): what the import found, or one entry in full.

    Without parameters: the catalog; `fields`, one row per entry field with how many
    entries carry it and where it goes in the object model (an unknown field has
    `known` false); `links`, what became of CWE's CAPEC and CVE links, naming each
    one not mapped; and how many objects of each kind the import makes. With `id`
    (`CWE-79` or `79`, or a local `tr-weak-0001`, #145): that weakness, category or
    view with every field and the relationships it writes, the objects the import makes
    for a weakness, `local` (the file of local weaknesses, when one is named), and
    `derived_relationships`, the inverses the schema declares for relationships that
    name it, from CWE's entries and the local ones. An id neither has gives
    `entry: null`. Raises ValueError for another parameter or a malformed id, and
    Unavailable when there is no pinned catalog to read or the local file cannot be read.
    """
    values = _values(query or {}, ("id",), "parameter")
    catalog = _served_catalog()
    summary = {"catalog": _catalog_summary(catalog)}
    if "id" not in values:
        return {
            **summary,
            "fields": catalog.report(),
            "links": catalog.links(),
            "objects": {name: len(items) for name, items in catalog.objects.items()},
        }
    wanted = _weakness_entry_id(values["id"])
    local = _served_local()
    entry: cwe.CweEntry | local_weaknesses.LocalWeakness | None
    if local_weaknesses.local_number(wanted) is not None:
        entry = local.get(wanted) if local is not None else None
        objects = (
            local_weaknesses.to_objects(local, [entry.number])
            if local is not None and entry is not None
            else None
        )
    else:
        entry = catalog.get(wanted)
        weakness = entry is not None and entry.kind == "Weakness"
        objects = cwe.to_objects(catalog, [entry.number]) if weakness else None
    derived = [r for r in cwe.select(_stated(catalog, local), source=wanted) if r.derived]
    return {
        **summary,
        "local": local.summary() if local is not None else None,
        "id": wanted,
        "entry": entry.to_dict() if entry is not None else None,
        "objects": objects,
        "derived_relationships": [r.to_dict() for r in derived],
    }


def weakness_relationships(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The weakness relationships (#145): in any list of CWE views, of one entry, paged.

    Every relationship the CWE release writes, a weakness's Related_Weakness and a
    category's or view's Has_Member or Member_Of, each tagged with its view; then
    those the local weaknesses write (`$TMODEL_LOCAL_WEAKNESSES`), and the inverses
    the schema declares for all of them, marked `derived`. Parameters, all optional:
    `view`, one view id or several separated by commas (`CWE-1000,699`), the views
    whose relationships to give; `id`, an entry (`CWE-79` or `tr-weak-0001`) whose
    relationships to give, the ones whose source it is; `derived`, `true` (the
    default) or `false` for only the written ones; and `limit` and `offset` for
    paging. `report` counts them all, whatever the query, and lists each one that
    departs from the schema or names an entry or view not read. Raises ValueError
    for a bad parameter or a view neither catalog knows, and Unavailable as
    `weaknesses` does. The payload names no local path.
    """
    values = _values(query or {}, RELATIONSHIP_OPTIONS, "parameter")
    derived = values.get("derived", "true")
    if derived not in ("true", "false"):
        raise ValueError(f"derived must be true or false, not {derived!r}")
    limit = _whole_number(values, "limit", minimum=1)
    offset = _whole_number(values, "offset", minimum=0) or 0
    source = _weakness_entry_id(values["id"]) if "id" in values else None

    catalog = _served_catalog()
    local = _served_local()
    stated = _stated(catalog, local)
    known = set(catalog.known_views)
    entries = {e.id for e in (*catalog.weaknesses, *catalog.categories, *catalog.views)}
    if local is not None:
        known |= {r.view for r in local.stated_relationships}
        entries |= {w.id for w in local.weaknesses}
    views = cwe.view_numbers(values.get("view"), known)
    found = cwe.select(stated, views, source, derived == "true")
    page = found[offset : offset + limit if limit is not None else None]
    return {
        "catalog": _catalog_summary(catalog),
        "local": local.summary() if local is not None else None,
        "query": {
            "views": [f"CWE-{n}" for n in sorted(views)] if views is not None else None,
            "id": source,
            "derived": derived == "true",
            "limit": limit,
            "offset": offset,
        },
        "report": cwe.relationship_report(stated, entries, {v.number for v in catalog.views}),
        "total": len(found),
        "count": len(page),
        "relationships": [r.to_dict() for r in page],
    }


def weakness_table(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Rows for the weakness table view (#144, #234): filtered, searched, sorted, paged.

    Parameters, all optional, as in `library_table`: the WEAKNESS_FILTERS, each an
    exact match; `search`, a text that must appear (ignoring case) in a weakness's
    id, name, description or alternate terms; `sort`, one of WEAKNESS_SORTS (default
    `id`, by number), where an enumeration sorts in CWE's own order; `order`, `asc`
    or `desc`; and `limit` and `offset` for paging. Weaknesses without a value for
    the sort field come last in both orders, and ties keep id order. `facets` counts
    the whole catalog; `contextual_facets` apply the search and the other filters,
    each leaving out its own. The payload names no local path.

    When `$TMODEL_LOCAL_WEAKNESSES` names a file, its weaknesses are rows too (#145),
    after CWE's in id order: a local row has its `tr-weak-` id, and no usage,
    likelihood, mitigations or url. The row's shape is #234's, so it is unchanged.
    """
    values = _values(query or {}, WEAKNESS_FILTERS + TABLE_OPTIONS, "parameter")
    sort = values.get("sort", "id")
    if sort not in WEAKNESS_SORTS:
        raise ValueError(f"cannot sort by {sort!r}: use one of {', '.join(WEAKNESS_SORTS)}")
    order = values.get("order", "asc")
    if order not in ("asc", "desc"):
        raise ValueError(f"order must be asc or desc, not {order!r}")
    limit = _whole_number(values, "limit", minimum=1)
    offset = _whole_number(values, "offset", minimum=0) or 0
    search = values.get("search")

    catalog = _served_catalog()
    local = _served_local()
    rows: tuple[_Weakness, ...] = (
        *catalog.weaknesses,
        *(local.weaknesses if local is not None else ()),
    )
    filters = {k: v for k, v in values.items() if k in WEAKNESS_FILTERS}
    searched = _weakness_searched(rows, search)
    matched = _weakness_sorted(_matching(searched, filters), sort, descending=order == "desc")
    page = matched[offset : offset + limit if limit is not None else None]
    return {
        "catalog": _catalog_summary(catalog),
        "query": {
            "filters": filters,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
        "total": len(matched),
        "count": len(page),
        "rows": [_weakness_row(w) for w in page],
        "facets": {name: _counts(rows, name) for name in WEAKNESS_FACETS},
        "contextual_facets": {
            name: _counts(
                _matching(searched, {key: value for key, value in filters.items() if key != name}),
                name,
            )
            for name in WEAKNESS_FACETS
        },
    }


def _weakness_searched(weaknesses: Iterable[_Weakness], search: str | None) -> list[_Weakness]:
    if search is None:
        return list(weaknesses)
    needle = search.casefold()
    return [
        w
        for w in weaknesses
        if needle in " ".join((w.id, w.name, w.description, *w.alternate_terms)).casefold()
    ]


def _weakness_sorted(weaknesses: list[_Weakness], field: str, descending: bool) -> list[_Weakness]:
    # id order: CWE's weaknesses by number, then the local ones by number (#145)
    return _entries_sorted(
        weaknesses,
        field,
        descending,
        WEAKNESS_ORDER,
        id_key=lambda w: (w.source != cwe.SOURCE, w.number),
    )


def _entries_sorted(
    entries: list[Any],
    field: str,
    descending: bool,
    orders: Mapping[str, tuple[str, ...]],
    id_key: Callable[[Any], Any] = lambda e: e.number,
) -> list[Any]:
    """Catalog entries by `field`: `id` in `id_key` order; an enumeration in the catalog's order.

    By default `id` order is by number. Entries without a value come last in both orders,
    and ties keep id order. Used by the CWE and CAPEC tables, whose entries both have
    `number` and the sort fields; the weakness table passes an `id_key` that puts CWE's
    weaknesses before the local ones (#145).
    """
    by_number = sorted(entries, key=id_key)
    if field == "id":
        return by_number[::-1] if descending else by_number
    order = {value: rank for rank, value in enumerate(orders.get(field, ()))}

    def key(e: Any) -> tuple[int, str]:
        value = getattr(e, field)
        return (order.get(value, len(order)), value.casefold())

    present = [e for e in by_number if getattr(e, field)]
    missing = [e for e in by_number if not getattr(e, field)]
    present.sort(key=key, reverse=descending)  # stable: ties keep id order
    return present + missing


def _weakness_row(w: _Weakness) -> dict[str, Any]:
    """One table row: what a list of weaknesses shows, plus the keys to fetch the rest."""
    return {
        "id": w.id,
        "weakness": w.object_id,
        "name": w.name,
        "abstraction": w.abstraction,
        "structure": w.structure,
        "status": w.status,
        "usage": w.usage,
        "likelihood": w.likelihood,
        "description": w.description,
        "attack_patterns": len(w.attack_patterns),
        "observed_examples": len(w.observed_examples),
        "mitigations": w.mitigations,
        "url": w.url,
    }


def _served_capec_catalog() -> capec.CapecCatalog:
    """The CAPEC release the library pins, read from the file `$TMODEL_CAPEC_CATALOG` names."""
    record = _served_library().get(capec.LIBRARY_RECORD)
    pinned = record.content.sha256 if record is not None else None
    if record is None or not pinned:
        raise Unavailable(
            "the library pins no CAPEC release: its capec record has no content.sha256 "
            "(it has one from library commit 4173143 on); set TMODEL_LIBRARY to a "
            "library checkout that has it"
        )
    path = capec.configured_catalog()
    if path is None:
        raise Unavailable(
            f"no CAPEC catalog: download {record.content.url} (SHA-256 {pinned}) "
            f"and set {capec.CATALOG_ENV} to that file"
        )
    try:
        return capec.cached_catalog(path, pinned)
    except capec.CapecError as exc:
        raise Unavailable(str(exc)) from exc


def _capec_summary(catalog: capec.CapecCatalog) -> dict[str, Any]:
    """Which CAPEC release an answer comes from, with MITRE's notice and licence.

    Every answer that holds CAPEC content carries them, as the CAPEC Terms of Use
    require of a copy. Names no local path.
    """
    return {
        "name": catalog.name,
        "version": catalog.version,
        "date": catalog.date,
        "schema": catalog.schema,
        "file": catalog.file,
        "sha256": catalog.sha256,
        "attack_patterns": len(catalog.attack_patterns),
        "categories": len(catalog.categories),
        "views": len(catalog.views),
        "references": len(catalog.references),
        "unknown_fields": len(catalog.unknown),
        "notice": capec.notice(catalog),
        "license": capec.LICENSE,
        "terms_url": capec.TERMS_URL,
    }


def attack_patterns(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The CAPEC release the engine serves (#244): what the import found, or one entry in full.

    Without parameters: the catalog; `fields`, one row per entry field with how many
    entries carry it and where it goes in the object model (an unknown field has
    `known` false); `links`, what became of CAPEC's links to CWE weaknesses, naming
    each one not mapped, with counts of the links kept on the entries; and how many
    objects of each kind the import makes. With `id` (`CAPEC-66` or `66`): that attack
    pattern, category or view with every field, `references`, each reference it cites
    resolved to its title, authors, publication and URL (`CapecCatalog.citations`), and
    the objects the import makes for an attack pattern. An id the catalog does not have
    gives `entry: null` and `references: null`. Raises
    ValueError for another parameter or a malformed id, and Unavailable when there is
    no pinned catalog to read.
    """
    values = _values(query or {}, ("id",), "parameter")
    catalog = _served_capec_catalog()
    summary = {"catalog": _capec_summary(catalog)}
    if "id" not in values:
        return {
            **summary,
            "fields": catalog.report(),
            "links": catalog.links(),
            "objects": {name: len(items) for name, items in catalog.objects.items()},
        }
    number = capec.capec_number(values["id"])
    entry = catalog.get(number)
    pattern = entry is not None and entry.kind == "Attack_Pattern"
    return {
        **summary,
        "id": f"CAPEC-{number}",
        "entry": entry.to_dict() if entry is not None else None,
        "references": catalog.citations(entry) if entry is not None else None,
        "objects": capec.to_objects(catalog, [number]) if pattern else None,
    }


def attack_pattern_table(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Rows for the attack-pattern table view (#244, #236): filtered, searched, sorted, paged.

    Parameters, all optional, as in `weakness_table`: the ATTACK_PATTERN_FILTERS, each
    an exact match; `search`, a text that must appear (ignoring case) in an attack
    pattern's id, name, description, alternate terms, CWE ids or ATT&CK ids; `sort`,
    one of ATTACK_PATTERN_SORTS (default `id`, by number), where an enumeration sorts
    in CAPEC's own order; `order`, `asc` or `desc`; and `limit` and `offset` for
    paging. Attack patterns without a value for the sort field come last in both
    orders, and ties keep id order. `facets` counts the whole catalog;
    `contextual_facets` apply the search and the other filters, each leaving out its
    own. The payload names no local path.
    """
    values = _values(query or {}, ATTACK_PATTERN_FILTERS + TABLE_OPTIONS, "parameter")
    sort = values.get("sort", "id")
    if sort not in ATTACK_PATTERN_SORTS:
        raise ValueError(f"cannot sort by {sort!r}: use one of {', '.join(ATTACK_PATTERN_SORTS)}")
    order = values.get("order", "asc")
    if order not in ("asc", "desc"):
        raise ValueError(f"order must be asc or desc, not {order!r}")
    limit = _whole_number(values, "limit", minimum=1)
    offset = _whole_number(values, "offset", minimum=0) or 0
    search = values.get("search")

    catalog = _served_capec_catalog()
    filters = {k: v for k, v in values.items() if k in ATTACK_PATTERN_FILTERS}
    searched = _attack_pattern_searched(catalog.attack_patterns, search)
    matched = _entries_sorted(
        _matching(searched, filters), sort, order == "desc", ATTACK_PATTERN_ORDER
    )
    page = matched[offset : offset + limit if limit is not None else None]
    return {
        "catalog": _capec_summary(catalog),
        "query": {
            "filters": filters,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
        "total": len(matched),
        "count": len(page),
        "rows": [_attack_pattern_row(p) for p in page],
        "facets": {name: _counts(catalog.attack_patterns, name) for name in ATTACK_PATTERN_FACETS},
        "contextual_facets": {
            name: _counts(
                _matching(searched, {key: value for key, value in filters.items() if key != name}),
                name,
            )
            for name in ATTACK_PATTERN_FACETS
        },
    }


def _attack_pattern_searched(
    patterns: Iterable[capec.CapecEntry], search: str | None
) -> list[capec.CapecEntry]:
    if search is None:
        return list(patterns)
    needle = search.casefold()
    return [
        p
        for p in patterns
        if needle
        in " ".join(
            (p.id, p.name, p.description, *p.alternate_terms, *p.weaknesses, *p.attack_techniques)
        ).casefold()
    ]


def _attack_pattern_row(p: capec.CapecEntry) -> dict[str, Any]:
    """One table row: what a list of attack patterns shows, plus the keys to fetch the rest."""
    return {
        "id": p.id,
        "attack_pattern": capec.attack_pattern_id(p.number),
        "name": p.name,
        "abstraction": p.abstraction,
        "status": p.status,
        "likelihood": p.likelihood,
        "severity": p.severity,
        "description": p.description,
        "weaknesses": list(p.weaknesses),
        "attack_techniques": list(p.attack_techniques),
        "related_attack_patterns": len(p.related_attack_patterns),
        "steps": p.steps,
        "mitigations": p.mitigations,
        "examples": p.examples,
        "url": p.url,
    }


def attack_paths(file: str, goal: str | None = None) -> dict[str, Any]:
    """Attack paths to `goal` (a step or threat id) in a model file (#63).

    Without a goal, lists the file's threats, each with whether it is reviewed,
    so a caller can pick one. Raises GraphError (a ValueError) for a bad file or
    goal. `file` must be absolute: the API serves callers in any directory.
    """
    path = Path(file)
    if not path.is_absolute():
        raise GraphError(f"{file}: give an absolute path")
    graph = load_vector(path)
    if goal is None:
        return {
            "file": str(path),
            "threats": graph.threats(),
            "reviewed_threats": [t for t in graph.threats() if graph.threat_reviewed(t)],
            "steps": len(graph.steps),
        }
    return {
        "file": str(path),
        "goal": goal,
        "paths": [p.to_dict() for p in enumerate_paths(graph, goal)],
    }


def risk_assessments(file: str, matrix: str, goal: str | None = None) -> dict[str, Any]:
    """Derived risk for approved example-model files; ratings remain authored inputs."""
    path = _approved_vector_path(file)
    try:
        result = assess_document(load_vector_document(path), matrix=matrix, goal=goal)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    return {"file": path.name, **result}


def collect_tara(file: str, matrix: str) -> dict[str, Any]:
    """Read-only, whole-model TARA intermediate from an approved example (#181)."""
    path = _approved_vector_path(file)
    try:
        result = tara_view.collect_document(load_vector_document(path), matrix=matrix)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    return {"source": {"file": path.name, "example_data": True}, **result}


def model_graph(file: str) -> dict[str, Any]:
    """Return a read-only graph projection of an approved example model.

    Relative paths are resolved below the bundled examples (or ``spec/vectors``
    in a source checkout). Absolute paths must resolve inside that directory.
    """
    path = _approved_vector_path(file)
    try:
        doc = load_vector_document(path)
        # Retain the graph integrity checks already used by PR #132.
        AttackGraph.from_dict(doc)
        graph = project_model_graph(doc)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    if not graph.nodes:
        raise GraphError(f"{path.name}: expected at least one model object")
    return {"file": str(path), **graph.to_dict()}


def list_models() -> dict[str, Any]:
    """The example models a reader can open (#208), one summary each.

    Lists the approved model directory: the bundled examples, or ``spec/vectors``
    in a source checkout. Schema test harnesses (``*.linkml.yaml``) are not models,
    and SDL program models (``sdl-*.yaml``) have their own ``/sdl`` selector, so
    both are left out. A file that fails to load is listed under ``problems`` so
    the rest can still be opened. Each summary's ``file`` is what ``/graph`` accepts.
    The title and description come from the model itself (its products), else the
    file name; nothing is made up. The payload names no local path.
    """
    root = APPROVED_VECTOR_DIRECTORY.resolve()
    models: list[dict[str, Any]] = []
    problems: list[dict[str, str]] = []
    candidates = sorted(root.iterdir()) if root.is_dir() else []
    for path in candidates:
        if (
            path.suffix not in MODEL_SUFFIXES
            or path.name.endswith(HARNESS_SUFFIX)
            or path.name.startswith(SDL_PREFIX)
            or not path.is_file()
        ):
            continue
        try:
            summary = _model_summary(path)
        except GraphError as exc:
            problems.append({"file": path.name, "error": _sanitized_model_error(path, exc)})
            continue
        if summary is not None:
            models.append(summary)
    rank = {kind: index for index, (_prefix, kind, _label) in enumerate(MODEL_KINDS)}
    models.sort(key=lambda model: (rank.get(model["kind"], len(rank)), model["file"]))
    return {"count": len(models), "models": models, "problems": problems}


def _model_summary(path: Path) -> dict[str, Any] | None:
    """One model's list entry, or None for a file with no model objects."""
    doc = load_vector_document(path)
    attack_graph = AttackGraph.from_dict(doc)  # the same integrity checks as /graph
    if not project_model_graph(doc).nodes:
        return None
    products = [p for p in doc.get("products") or [] if isinstance(p, Mapping)]
    names = [p["name"].strip() for p in products if _has_text(p.get("name"))]
    kind, kind_label = next(
        ((kind, label) for prefix, kind, label in MODEL_KINDS if path.name.startswith(prefix)),
        ("other", "Example model"),
    )
    threats = attack_graph.threats()
    return {
        "id": path.stem,
        "file": path.name,
        "title": " and ".join(names) if names else path.stem,
        "description": _products_description(products),
        "kind": kind,
        "kind_label": kind_label,
        "counts": {
            name: len(entries) if isinstance(entries := doc.get(collection), list) else 0
            for name, collection in MODEL_COUNTS
        },
        "reviewed_threats": sum(1 for t in threats if attack_graph.threat_reviewed(t)),
    }


def _products_description(products: list[Mapping[str, Any]]) -> str | None:
    """The products' own descriptions, in model order, nothing added.

    One product: its description. Several (mvp-18 has two): one line per product
    that has a description, "Name: description", so the scope covers every
    product the title names. Whitespace inside a description is collapsed, so a
    newline only ever separates two products; the app reads each line apart.
    """
    described = [
        (p.get("name"), " ".join(p["description"].split()))
        for p in products
        if _has_text(p.get("description"))
    ]
    if not described:
        return None
    if len(products) == 1:
        return described[0][1]
    return "\n".join(
        f"{name.strip()}: {text}" if _has_text(name) else text for name, text in described
    )


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _approved_vector_path(file: str) -> Path:
    if not file or not file.strip():
        raise GraphError("file: expected a model filename")
    root = APPROVED_VECTOR_DIRECTORY.resolve()
    supplied = Path(file)
    candidate = supplied if supplied.is_absolute() else root / supplied
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise GraphError("file: outside approved model directory")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise GraphError(f"{supplied.name or 'file'}: cannot read") from exc
    if not resolved.is_relative_to(root):
        raise GraphError("file: outside approved model directory")
    if not resolved.is_file():
        raise GraphError(f"{resolved.name}: expected a model file")
    return resolved


def _sanitized_model_error(path: Path, error: GraphError) -> str:
    """Keep model errors useful without returning the engine's local filesystem path."""
    message = str(error).replace(str(path), path.name)
    return message if message.startswith(f"{path.name}:") else f"{path.name}: {message}"


def sdl_models() -> dict[str, Any]:
    """The SDL models the app can open (spec/vectors/sdl-*.yaml), with their programs."""
    root = APPROVED_VECTOR_DIRECTORY
    models = []
    for path in sorted(root.glob(f"{SDL_PREFIX}*.yaml")):
        try:
            doc = load_vector_document(path)
        except GraphError as exc:
            models.append({"file": path.name, "error": _sanitized_model_error(path, exc)})
            continue
        models.append({"file": path.name, "programs": sdl_view.programs(dict(doc))})
    return {"models": models}


def sdl(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The SDL program view of one SDL model (DL-0043): what the "tmodel SDL" page shows.

    Without `file`, lists the SDL models (`sdl_models`). `file` is a name in the
    approved model directory and must be an `sdl-*.yaml` model; `program` picks a
    SecurityProgram when the file has more than one. Raises ValueError (400) for a bad
    file, an unknown program, a dangling reference or a broken PROC-0002 review rule.
    The payload is read-only and names no local path.
    """
    values = _values(query or {}, SDL_OPTIONS, "parameter")
    if "file" not in values:
        return sdl_models()
    path = _approved_vector_path(values["file"])
    if not path.name.startswith(SDL_PREFIX):
        raise GraphError(f"{path.name}: not an SDL model (expected {SDL_PREFIX}*.yaml)")
    try:
        doc = dict(load_vector_document(path))
        xwalk = load_vector_document(CROSSWALK_FILE)
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    try:
        pending = proposals.load_proposals(path)
        view = sdl_view.collect(doc, dict(xwalk), program=values.get("program"))
        view["proposals"] = proposals.summary(pending, doc)
    except (KeyError, TypeError) as exc:
        raise GraphError(f"{path.name}: malformed SDL model ({type(exc).__name__}: {exc})") from exc
    except sdl_view.SdlError as exc:
        raise GraphError(f"{path.name}: {exc}") from exc
    return {"file": path.name, **view}


def _model_path(file: str) -> Path:
    """An example model in the approved directory: mvp-*, tv-*, pv-* or sdl-*.yaml."""
    path = _approved_vector_path(file)
    if not path.name.startswith(proposals.MODEL_PREFIXES) or path.suffix != ".yaml":
        raise GraphError(
            f"{path.name}: not a model file (expected "
            f"{', '.join(p + '*.yaml' for p in proposals.MODEL_PREFIXES)})"
        )
    return path


def _relative(path: Path) -> str:
    return str(path.relative_to(APPROVED_VECTOR_DIRECTORY.parent.parent))


def propose(patch: Mapping[str, Any], write: bool = True) -> dict[str, Any]:
    """Check an agent's patch and append it to the target's proposals file (DL-0044, DL-0046).

    Never edits the model, writes a Review or accepts anything. Raises ValueError
    (ProposalError) with every problem when the patch is refused; nothing is written.
    """
    target = patch.get("target") if isinstance(patch, Mapping) else None
    if not isinstance(target, str):
        raise proposals.ProposalError("target is required")
    try:
        path = _model_path(target)
    except GraphError as exc:
        raise proposals.ProposalError(str(exc)) from exc
    xwalk = load_vector_document(CROSSWALK_FILE)
    record = proposals.propose(patch, path, xwalk, write=write)
    return {
        "written": write,
        "file": _relative(proposals.proposals_path(path)) if write else None,
        "proposal": record,
    }


def pending_proposals(query: Mapping[str, str] | None = None) -> dict[str, Any]:
    """GET /proposals (DL-0046): pending proposals and saved KG views. Read-only.

    Without `file`, lists every example model with its number of pending proposals.
    With `file`, returns that model's pending proposals (as GET /sdl shows them) and
    its saved KG views, the model's own first, then the proposed ones, each with the
    object ids it selects. Nothing here accepts anything; there is no write route.
    """
    values = _values(query or {}, ("file",), "parameter")
    root = APPROVED_VECTOR_DIRECTORY
    if "file" not in values:
        models = []
        for path in sorted(root.glob("*.yaml")):
            if not path.name.startswith(proposals.MODEL_PREFIXES):
                continue
            try:
                count = len(proposals.load_proposals(path))
            except proposals.ProposalError as exc:
                models.append({"file": path.name, "error": str(exc)})
                continue
            models.append({"file": path.name, "kind": proposals.model_kind(path), "pending": count})
        return {"models": models}
    path = _model_path(values["file"])
    try:
        doc = dict(load_vector_document(path))
        pending = proposals.load_proposals(path)
        return {
            "file": path.name,
            "kind": proposals.model_kind(path),
            "proposals": proposals.summary(pending, doc),
            "views": proposals.views(doc, pending),
        }
    except GraphError as exc:
        raise GraphError(_sanitized_model_error(path, exc)) from exc
    except (KeyError, TypeError) as exc:
        raise GraphError(f"{path.name}: malformed proposals ({type(exc).__name__}: {exc})") from exc


def evaluate_tara_gate(
    gate: Mapping[str, Any],
    record: Mapping[str, Any],
    *,
    current_digest: str,
    evidence_link: str,
) -> dict[str, Any]:
    """Read-only DL-0027 pilot criterion; no Gate decision or conformance verdict."""
    return tara_gate.evaluate(
        gate, record, current_digest=current_digest, evidence_link=evidence_link
    )
