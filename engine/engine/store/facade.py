"""The store façade: nodes and typed edges with properties, by stable id (#65, ADR-0004).

Callers write and read plain objects (Node, Edge) and never see the store underneath:
the working store is Oxigraph (ADR-0008, `engine.store.oxigraph`), and an adapter for
another engine only has to implement `Adapter`. Files in git stay the source of
truth; the store is a rebuildable copy (ADR-0004 decisions 1 and 3).

Each source loads into its own named graph: the library, one model file, one catalog
release. `Store.load` replaces one graph as a whole, and only when the source's digest
has changed. The store keeps the digest but no load time, so loading the same files
twice gives the same store.

Ids never change on a rebuild. A node's id is the id its file gives it, such as
`library:rfc-8785` or `weakness:cwe-306`. An edge's id is the one its file gives it
(an Assertion id) or, when the file gives none, one derived from its two ends and its
type, so the same fact always gets the same id. The same id may appear in several
graphs, and each graph keeps its own fields for it, so nothing is overwritten.

Every invalid input becomes a StoreError (a ValueError), so callers can report it.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Protocol

# A property value: text, a number, true/false, or a list or mapping of these
# (lists come back as tuples). None at the top level means "no value" and is left out.
Value = Any


class StoreError(ValueError):
    """The input cannot be written as given (empty id, bad value, duplicate id, ...)."""


def _name(value: object, what: str) -> str:
    """An id, type or graph name: any non-empty string."""
    if not isinstance(value, str) or not value:
        raise StoreError(f"{what} must be a non-empty string, not {value!r:.60}")
    return value


def _value(value: object, where: str) -> Value:
    """`value` in the one form the store keeps, so what is read back equals what was written."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StoreError(f"{where}: {value} is not a finite number")
        return value
    if isinstance(value, (list, tuple)):
        return tuple(_value(v, f"{where}[{i}]") for i, v in enumerate(value))
    if isinstance(value, Mapping):
        items = {}
        for key, v in value.items():
            if not isinstance(key, str):
                raise StoreError(f"{where}: mapping keys must be strings, not {key!r:.60}")
            items[key] = _value(v, f"{where}.{key}")
        return MappingProxyType(items)
    raise StoreError(f"{where}: cannot store a {type(value).__name__}")


def _properties(raw: Mapping[str, object], owner: str) -> Mapping[str, Value]:
    if not isinstance(raw, Mapping):
        raise StoreError(f"{owner}: properties must be a mapping")
    props = {}
    for key in sorted(raw, key=lambda k: (not isinstance(k, str), str(k))):
        name = _name(key, f"{owner}: a property name")
        if raw[key] is not None:
            props[name] = _value(raw[key], f"{owner}.{name}")
    return MappingProxyType(props)


def edge_id(source: str, type: str, target: str) -> str:
    """The id of an edge its file gives no id: the same ends and type, the same id."""
    key = json.dumps([source, type, target], ensure_ascii=False)
    return "edge:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class Node:
    """One object: its id, its type, and its fields as properties.

    `graph` is the source the store read it from; leave it unset when writing.
    """

    id: str
    type: str
    properties: Mapping[str, Value] = field(default_factory=dict)
    graph: str | None = None

    def __post_init__(self) -> None:
        _name(self.id, "a node id")
        _name(self.type, f"{self.id}: the node type")
        object.__setattr__(self, "properties", _properties(self.properties, self.id))


@dataclass(frozen=True)
class Edge:
    """A typed edge from `source` to `target` (node ids), with properties.

    `id` is the file's id for the edge when it has one; otherwise it is derived
    (`edge_id`). `graph` is the source the store read it from; leave it unset when
    writing.
    """

    source: str
    type: str
    target: str
    properties: Mapping[str, Value] = field(default_factory=dict)
    id: str = ""
    graph: str | None = None

    def __post_init__(self) -> None:
        _name(self.source, "an edge source")
        _name(self.type, "an edge type")
        _name(self.target, "an edge target")
        if not self.id:
            object.__setattr__(self, "id", edge_id(self.source, self.type, self.target))
        _name(self.id, "an edge id")
        object.__setattr__(self, "properties", _properties(self.properties, self.id))


class Adapter(Protocol):
    """What a working-store engine implements to sit behind the façade.

    The façade validates, sets `graph` on what it hands over, and sorts what it
    returns, so an adapter only stores and finds. `None` in a read means "any".
    """

    def digest(self, graph: str) -> str | None: ...

    def graphs(self) -> Iterable[str]: ...

    def replace(
        self, graph: str, digest: str, nodes: Sequence[Node], edges: Sequence[Edge]
    ) -> None: ...

    def drop(self, graph: str) -> None: ...

    def nodes(self, graph: str | None, type: str | None, id: str | None) -> Iterable[Node]: ...

    def edges(
        self, graph: str | None, source: str | None, type: str | None, target: str | None
    ) -> Iterable[Edge]: ...


class Store:
    """The working store, through the façade. Safe to share between threads."""

    def __init__(self, adapter: Adapter | None = None) -> None:
        if adapter is None:
            from .oxigraph import OxigraphAdapter  # the working store (ADR-0008)

            adapter = OxigraphAdapter()
        self._adapter = adapter
        self._lock = threading.RLock()

    @classmethod
    def open(cls, path: str | None = None) -> Store:
        """An Oxigraph store in memory, or kept in the folder `path` between runs."""
        from .oxigraph import OxigraphAdapter

        return cls(OxigraphAdapter(path))

    def load(
        self, graph: str, digest: str, nodes: Iterable[Node], edges: Iterable[Edge] = ()
    ) -> bool:
        """Make `graph` hold exactly these nodes and edges, from a source whose bytes
        have this `digest`. Nothing is written when the graph already holds that
        digest. Returns True when the graph was (re)written."""
        _name(graph, "a graph name")
        _name(digest, f"{graph}: the digest")
        nodes = [self._own(n, Node, graph) for n in nodes]
        edges = [self._own(e, Edge, graph) for e in edges]
        _unique(graph, nodes, edges)
        with self._lock:
            if self._adapter.digest(graph) == digest:
                return False
            self._adapter.replace(graph, digest, nodes, edges)
            return True

    def digest(self, graph: str) -> str | None:
        """The digest of the source `graph` was loaded from, or None if it is not loaded."""
        with self._lock:
            return self._adapter.digest(graph)

    def graphs(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._adapter.graphs()))

    def drop(self, graph: str) -> bool:
        """Remove one source's graph. Returns False if it was not loaded."""
        with self._lock:
            if self._adapter.digest(graph) is None:
                return False
            self._adapter.drop(graph)
            return True

    def node(self, id: str, graph: str) -> Node | None:
        """One source's copy of a node."""
        found = self.nodes(id=id, graph=graph)
        return found[0] if found else None

    def nodes(
        self, *, graph: str | None = None, type: str | None = None, id: str | None = None
    ) -> tuple[Node, ...]:
        """Nodes, sorted by id then graph. With no `graph`, every source's copy is listed."""
        with self._lock:
            found = list(self._adapter.nodes(graph, type, id))
        return tuple(sorted(found, key=lambda n: (n.id, n.graph or "")))

    def edges(
        self,
        *,
        graph: str | None = None,
        source: str | None = None,
        type: str | None = None,
        target: str | None = None,
    ) -> tuple[Edge, ...]:
        """Edges, sorted by source, type, target, id, then graph."""
        with self._lock:
            found = list(self._adapter.edges(graph, source, type, target))
        return tuple(sorted(found, key=lambda e: (e.source, e.type, e.target, e.id, e.graph or "")))

    @staticmethod
    def _own(item: Node | Edge, kind: type, graph: str) -> Any:
        if not isinstance(item, kind):
            raise StoreError(f"{graph}: expected a {kind.__name__}, not {type(item).__name__}")
        if item.graph not in (None, graph):
            raise StoreError(f"{item.id}: belongs to graph {item.graph!r}, not {graph!r}")
        return replace(item, graph=graph)


def _unique(graph: str, nodes: Sequence[Node], edges: Sequence[Edge]) -> None:
    """Within one graph, an id names one node or one edge."""
    seen: set[str] = set()
    for item in (*nodes, *edges):
        if item.id in seen:
            what = "node" if isinstance(item, Node) else "edge"
            raise StoreError(
                f"{graph}: {item.id} is used by more than one node or edge "
                f"(this {what} needs its own id)"
            )
        seen.add(item.id)
