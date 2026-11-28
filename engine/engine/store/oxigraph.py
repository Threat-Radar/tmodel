"""The Oxigraph adapter: the working store ADR-0008 chose, behind the façade (#65).

Only this module knows the store is RDF. Ids become IRIs under one base that is
private to the store, so changing the base never changes an id; exports (#53) choose
their own vocabulary.

- A node is a subject in its source's named graph, with `rdf:type` and one literal
  per property.
- An edge is the triple `source type target`, asserted so SPARQL path queries see it,
  plus a reifier named by the edge's id (RDF 1.2 `rdf:reifies`, the successor of
  RDF-star). The reifier carries the edge's properties, so two edges with the same
  ends and type can still have their own ids and properties.
- Each graph's digest is kept in the default graph, which holds nothing else.

A graph is replaced in two steps: its digest and contents are removed, then the new
contents and digest are added in one transaction. A run that stops in between leaves
a graph with no digest, which `load` rebuilds and which is cleared when the store
is next opened.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from urllib.parse import quote, unquote

from pyoxigraph import DefaultGraph, Literal, NamedNode, Quad, Store, Triple

from .facade import Edge, Node, StoreError, Value

BASE = "https://threat-radar.github.io/tmodel/store/"
_ID, _TYPE, _PROP, _EDGE, _GRAPH = (
    BASE + part for part in ("id/", "type/", "prop/", "edge/", "graph/")
)
_DIGEST = NamedNode(BASE + "digest")

_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_XSD = "http://www.w3.org/2001/XMLSchema#"
_RDF_TYPE = NamedNode(_RDF + "type")
_REIFIES = NamedNode(_RDF + "reifies")
_JSON = NamedNode(_RDF + "JSON")
_STRING, _BOOLEAN, _INTEGER, _DOUBLE = (
    NamedNode(_XSD + t) for t in ("string", "boolean", "integer", "double")
)
_SAFE = ":@!$&'()*+,;=/"  # kept as written; everything else is percent-encoded


def _iri(namespace: str, name: str) -> NamedNode:
    return NamedNode(namespace + quote(name, safe=_SAFE))


def _decode(namespace: str, node: object) -> str | None:
    """The name inside an IRI from `namespace`, or None for any other term."""
    if isinstance(node, NamedNode) and node.value.startswith(namespace):
        return unquote(node.value[len(namespace) :])
    return None


def _literal(value: Value) -> Literal:
    if isinstance(value, str):
        return Literal(value)
    if isinstance(value, bool):
        return Literal("true" if value else "false", datatype=_BOOLEAN)
    if isinstance(value, int):
        return Literal(str(value), datatype=_INTEGER)
    if isinstance(value, float):
        return Literal(repr(value), datatype=_DOUBLE)
    # Lists and mappings keep their order as one JSON value.
    text = json.dumps(_plain(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return Literal(text, datatype=_JSON)


def _plain(value: Value) -> object:
    if isinstance(value, tuple):
        return [_plain(v) for v in value]
    if isinstance(value, MappingProxyType):
        return {k: _plain(v) for k, v in value.items()}
    return value


def _python(literal: object) -> Value:
    if not isinstance(literal, Literal):
        raise StoreError(f"not a property value: {literal}")
    datatype = literal.datatype
    if datatype == _STRING:
        return literal.value
    if datatype == _BOOLEAN:
        return literal.value in ("true", "1")
    if datatype == _INTEGER:
        return int(literal.value)
    if datatype == _DOUBLE:
        return float(literal.value)
    if datatype == _JSON:
        return json.loads(literal.value)  # the façade turns lists into tuples
    raise StoreError(f"not a property value: {literal}")


class OxigraphAdapter:
    """An Oxigraph store in memory, or on disk in the folder `path`."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._store = Store(str(path)) if path is not None else Store()
        loaded = {g.value for g, _ in self._digests()}
        for graph in list(self._store.named_graphs()):
            if graph.value not in loaded:  # a replace that stopped half way
                self._store.remove_graph(graph)

    def _digests(self) -> Iterator[tuple[NamedNode, str]]:
        for quad in self._store.quads_for_pattern(None, _DIGEST, None, DefaultGraph()):
            yield quad.subject, quad.object.value

    def digest(self, graph: str) -> str | None:
        quads = self._store.quads_for_pattern(_iri(_GRAPH, graph), _DIGEST, None, DefaultGraph())
        return next((q.object.value for q in quads), None)

    def graphs(self) -> list[str]:
        return [name for g, _ in self._digests() if (name := _decode(_GRAPH, g)) is not None]

    def replace(
        self, graph: str, digest: str, nodes: Sequence[Node], edges: Sequence[Edge]
    ) -> None:
        g = _iri(_GRAPH, graph)
        self.drop(graph)
        quads = [Quad(g, _DIGEST, Literal(digest), DefaultGraph())]
        for node in nodes:
            subject = _iri(_ID, node.id)
            quads.append(Quad(subject, _RDF_TYPE, _iri(_TYPE, node.type), g))
            quads.extend(_props(subject, node.properties, g))
        for edge in edges:
            fact = Triple(_iri(_ID, edge.source), _iri(_EDGE, edge.type), _iri(_ID, edge.target))
            reifier = _iri(_ID, edge.id)
            quads.append(Quad(fact.subject, fact.predicate, fact.object, g))
            quads.append(Quad(reifier, _REIFIES, fact, g))
            quads.extend(_props(reifier, edge.properties, g))
        self._store.extend(quads)  # one transaction: all of it, digest included, or none

    def drop(self, graph: str) -> None:
        g = _iri(_GRAPH, graph)
        for quad in list(self._store.quads_for_pattern(g, _DIGEST, None, DefaultGraph())):
            self._store.remove(quad)  # first, so a stop part way leaves no digest
        self._store.remove_graph(g)

    def nodes(self, graph: str | None, type: str | None, id: str | None) -> Iterator[Node]:
        g = _iri(_GRAPH, graph) if graph is not None else None
        subject = _iri(_ID, id) if id is not None else None
        kind = _iri(_TYPE, type) if type is not None else None
        for quad in self._store.quads_for_pattern(subject, _RDF_TYPE, kind, g):
            name = _decode(_GRAPH, quad.graph_name)
            node_id, node_type = _decode(_ID, quad.subject), _decode(_TYPE, quad.object)
            if name is None or node_id is None or node_type is None:
                continue
            yield Node(node_id, node_type, self._read_props(quad.subject, quad.graph_name), name)

    def edges(
        self, graph: str | None, source: str | None, type: str | None, target: str | None
    ) -> Iterator[Edge]:
        g = _iri(_GRAPH, graph) if graph is not None else None
        subject = _iri(_ID, source) if source is not None else None
        predicate = _iri(_EDGE, type) if type is not None else None
        obj = _iri(_ID, target) if target is not None else None
        for quad in self._store.quads_for_pattern(subject, predicate, obj, g):
            name = _decode(_GRAPH, quad.graph_name)
            ends = (
                _decode(_ID, quad.subject),
                _decode(_EDGE, quad.predicate),
                _decode(_ID, quad.object),
            )
            if name is None or None in ends:
                continue
            fact = Triple(quad.subject, quad.predicate, quad.object)
            for reified in self._store.quads_for_pattern(None, _REIFIES, fact, quad.graph_name):
                edge_id = _decode(_ID, reified.subject)
                if edge_id is not None:
                    props = self._read_props(reified.subject, quad.graph_name)
                    yield Edge(*ends, props, edge_id, name)

    def _read_props(self, subject: NamedNode, graph: NamedNode) -> dict[str, Value]:
        props = {}
        for quad in self._store.quads_for_pattern(subject, None, None, graph):
            key = _decode(_PROP, quad.predicate)
            if key is not None:
                props[key] = _python(quad.object)
        return props


def _props(subject: NamedNode, properties: Mapping[str, Value], graph: NamedNode) -> Iterator[Quad]:
    for key, value in properties.items():
        yield Quad(subject, _iri(_PROP, key), _literal(value), graph)
