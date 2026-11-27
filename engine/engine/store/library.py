"""The loaded library as nodes and edges in the working store (#65, for #142).

The answers agreed on #65 for the library loader:

1. **Node ids.** Each record is a node `library:<record-id>`, the form a Requirement's
   `source_ref` already uses. A `source_ref` with a fragment points at the record's
   node; the fragment is a locator for the edge, not a node (`split_source_ref`).
2. **Edges.** Every relation kind, and `cites` where it names a record, is one edge
   per fact, written forward whichever record states it: `superseded_by`, `updated_by`
   and `cited_by` are read from the other end as `supersedes`, `updates` and `cites`.
   `see_also` and `contradicts` have no direction (the library's `docs/references.md`
   calls them symmetric), so each pair is one edge, from the lower record id to the
   higher. So a link recorded on one side only gives the same graph as one recorded on
   both. `stated_by` lists the records that state it. Citations with no record id stay on
   the record's node as data. A relation to a record the library does not hold makes
   no edge and no empty node; `LibraryLoad.missing` lists it.
3. **Rebuild.** The library is one graph, `library`, loaded whole and replaced only
   when `Library.digest` changes.

The loader (`engine.load.library`) keeps no store code: it hands the loaded library to
`load_library` in one call (#142).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..load.library import Library, LibraryRecord
from .facade import Edge, Node, Store

GRAPH = "library"
NODE_TYPE = "LibraryRecord"
PREFIX = "library:"
# An inverse relation kind, and the forward kind it is read as from the other end.
FORWARD = {"superseded_by": "supersedes", "updated_by": "updates", "cited_by": "cites"}
# Relation kinds with no direction: one edge per pair, from the lower id to the higher.
SYMMETRIC = frozenset({"see_also", "contradicts"})


def node_id(record_id: str) -> str:
    return PREFIX + record_id


def split_source_ref(ref: str) -> tuple[str, str | None]:
    """A `source_ref` as the node it points at and its locator, if it has one.

    `library:iso-sae-21434-2021#RQ-09-09` gives (`library:iso-sae-21434-2021`, `RQ-09-09`).
    """
    node, mark, locator = ref.partition("#")
    return node, (locator if mark and locator else None)


@dataclass(frozen=True)
class LibraryGraph:
    """The library as the store holds it, before it is written."""

    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    missing: tuple[str, ...]  # "record: kind -> target" for targets the library lacks


@dataclass(frozen=True)
class LibraryLoad:
    graph: str
    digest: str
    rebuilt: bool  # False when the store already held this digest
    nodes: int
    edges: int
    missing: tuple[str, ...]


def library_graph(library: Library) -> LibraryGraph:
    held = {r.id for r in library}
    stated: dict[tuple[str, str, str], list[str]] = {}
    missing: list[str] = []
    for record in library:
        for kind, target in _links(record):
            if target not in held:
                missing.append(f"{record.id}: {kind} -> {target}")
                continue
            if kind in FORWARD:
                fact = (target, FORWARD[kind], record.id)
            elif kind in SYMMETRIC:
                low, high = sorted((record.id, target))
                fact = (low, kind, high)
            else:
                fact = (record.id, kind, target)
            sayers = stated.setdefault(fact, [])
            if record.id not in sayers:
                sayers.append(record.id)
    edges = tuple(
        Edge(node_id(source), kind, node_id(target), {"stated_by": sorted(sayers)})
        for (source, kind, target), sayers in stated.items()
    )
    return LibraryGraph(nodes=tuple(_node(r) for r in library), edges=edges, missing=tuple(missing))


def load_library(store: Store, library: Library) -> LibraryLoad:
    """Write the library into `store` as the graph `library`, unless it is already there."""
    graph = library_graph(library)
    rebuilt = store.load(GRAPH, library.digest, graph.nodes, graph.edges)
    return LibraryLoad(
        graph=GRAPH,
        digest=library.digest,
        rebuilt=rebuilt,
        nodes=len(graph.nodes),
        edges=len(graph.edges),
        missing=graph.missing,
    )


def _links(record: LibraryRecord) -> list[tuple[str, str]]:
    links = [(kind, target) for kind, targets in record.relations for target in targets]
    links += [("cites", c.record) for c in record.cites if c.record]
    return links


def _node(record: LibraryRecord) -> Node:
    """The record's fields, as the loader gives them, less the links that are edges."""
    fields = record.to_dict()
    del fields["relations"]
    fields["cites"] = [
        {k: v for k, v in c.items() if k != "record"} for c in fields["cites"] if not c["record"]
    ]
    return Node(node_id(record.id), NODE_TYPE, fields)
