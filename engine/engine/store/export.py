"""Exports of the working store: Turtle, TriG, JSON-LD, GraphML and CSV (#65, #53).

Derived, never canonical (ADR-0004 decision 4, ADR-0007): files in git stay the source
of truth, and an export is written from what the store holds, read through the façade.
Every node and edge keeps its id in every format (ADR-0004), and the same store always
gives the same bytes.

What each format keeps (the CF-008 round trip, tested in tests/test_store_export.py):

- **TriG** (Turtle with named graphs) and **JSON-LD**: everything. Each source stays
  its own graph, and the digests come too.
  - TriG writes each edge as an RDF 1.2 reifier, which is RDF-star's successor
    (ADR-0007, ADR-0008). Readers that predate RDF 1.2 (rdflib 7, for one) cannot
    read that, so `rdf12=False` writes the same edge as a classic `rdf:Statement`,
    as JSON-LD does.
  - JSON-LD cannot hold a triple term yet, so it writes the same edge as a classic
    `rdf:Statement` with the same IRI. It is written expanded, with full IRIs.
- **Turtle**: one graph, everything but its digest. Turtle has no named graphs.
- **CSV**: everything. One row per (graph, node) and per (graph, edge), with the
  properties as one JSON object, so no type or order is lost.
- **GraphML**, for graph viewers: one node per id and one edge per edge id.
  - When several of the chosen graphs hold the same id, the first in `graphs` order
    gives its type and fields, and `tmodel:graphs` lists every graph that holds it.
    So list the graph whose text should win first, and use another format to keep
    every copy.
  - An edge to a node no chosen graph holds gets a bare node, so the file stays
    valid.
  - A property is typed (boolean, long, double) only when all its values share that
    type. Otherwise it is a string, with lists, mappings and other non-text values
    written as JSON.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Sequence
from xml.sax.saxutils import escape, quoteattr

from .facade import Edge, Node, Store, StoreError, Value
from .oxigraph import dump

GRAPHML_NS = "http://graphml.graphdrawing.org/xmlns"
NODE_COLUMNS = ("graph", "id", "type", "properties")
EDGE_COLUMNS = ("graph", "id", "source", "type", "target", "properties")
# Characters XML 1.0 cannot hold at all, not even as a character reference.
_NOT_XML = re.compile("[^\t\n\r\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")


def to_turtle(store: Store, graph: str, *, rdf12: bool = True) -> bytes:
    """One graph as Turtle. Its digest is left out: Turtle has no place for it."""
    return dump(_sources(store, [graph]), "turtle", rdf12=rdf12)


def to_trig(store: Store, graphs: Sequence[str] | None = None, *, rdf12: bool = True) -> bytes:
    """The chosen graphs (default: all) as TriG, with their digests."""
    return dump(_sources(store, graphs), "trig", rdf12=rdf12)


def to_jsonld(store: Store, graphs: Sequence[str] | None = None) -> bytes:
    """The chosen graphs (default: all) as JSON-LD, with their digests."""
    return dump(_sources(store, graphs), "jsonld")


def to_csv(store: Store, graphs: Sequence[str] | None = None) -> tuple[bytes, bytes]:
    """The chosen graphs (default: all) as two CSV files: nodes, then edges."""
    sources = _sources(store, graphs)
    nodes, edges = io.StringIO(), io.StringIO()
    node_rows, edge_rows = csv.writer(nodes), csv.writer(edges)
    node_rows.writerow(NODE_COLUMNS)
    edge_rows.writerow(EDGE_COLUMNS)
    for graph, _, graph_nodes, graph_edges in sources:
        for n in graph_nodes:
            node_rows.writerow((graph, n.id, n.type, _json(n.properties)))
        for e in graph_edges:
            edge_rows.writerow((graph, e.id, e.source, e.type, e.target, _json(e.properties)))
    return nodes.getvalue().encode("utf-8"), edges.getvalue().encode("utf-8")


def to_graphml(store: Store, graphs: Sequence[str] | None = None) -> bytes:
    """The chosen graphs (default: all) as one GraphML graph, for viewers."""
    sources = _sources(store, graphs)
    nodes: dict[str, Node | None] = {}  # None: a bare node at the end of an edge
    edges: dict[str, Edge] = {}
    held: dict[str, list[str]] = {}  # id -> the graphs that hold it, in `graphs` order
    for graph, _, graph_nodes, graph_edges in sources:
        for item in (*graph_nodes, *graph_edges):
            held.setdefault(item.id, []).append(graph)
            target = nodes if isinstance(item, Node) else edges
            target.setdefault(item.id, item)
    for e in edges.values():  # an edge's ends must be nodes in the file
        for end in (e.source, e.target):
            if end not in nodes:
                nodes[end] = None
                held.setdefault(end, [])
    node_keys = _keys([n.properties for n in nodes.values() if n is not None], "n")
    edge_keys = _keys([e.properties for e in edges.values()], "e")

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<graphml xmlns="{GRAPHML_NS}">',
        '  <key id="nt" for="node" attr.name="tmodel:type" attr.type="string"/>',
        '  <key id="ng" for="node" attr.name="tmodel:graphs" attr.type="string"/>',
        '  <key id="et" for="edge" attr.name="tmodel:type" attr.type="string"/>',
        '  <key id="eg" for="edge" attr.name="tmodel:graphs" attr.type="string"/>',
    ]
    for kind, keys in (("node", node_keys), ("edge", edge_keys)):
        for name, (key_id, key_type) in keys.items():
            out.append(
                f'  <key id="{key_id}" for="{kind}" attr.name={_attr(name)} '
                f'attr.type="{key_type}"/>'
            )
    out.append('  <graph id="tmodel" edgedefault="directed">')
    for node_id in sorted(nodes):
        node = nodes[node_id]
        out.append(f"    <node id={_attr(node_id)}>")
        if node is not None:
            out.append(_data("nt", node.type))
        out.append(_data("ng", _json(held[node_id])))
        if node is not None:
            out += [_data(*_cell(node_keys[k], v)) for k, v in sorted(node.properties.items())]
        out.append("    </node>")
    for e in sorted(edges.values(), key=lambda e: (e.source, e.type, e.target, e.id)):
        out.append(f"    <edge id={_attr(e.id)} source={_attr(e.source)} target={_attr(e.target)}>")
        out.append(_data("et", e.type))
        out.append(_data("eg", _json(held[e.id])))
        out += [_data(*_cell(edge_keys[k], v)) for k, v in sorted(e.properties.items())]
        out.append("    </edge>")
    out += ["  </graph>", "</graphml>", ""]
    return "\n".join(out).encode("utf-8")


def _sources(
    store: Store, graphs: Sequence[str] | None
) -> list[tuple[str, str, tuple[Node, ...], tuple[Edge, ...]]]:
    """(graph, digest, nodes, edges) for each chosen graph, in the order given."""
    loaded = store.graphs()
    chosen = list(loaded if graphs is None else graphs)
    unknown = [g for g in chosen if g not in loaded]
    if unknown:
        raise StoreError(f"not loaded: {', '.join(unknown)} (loaded: {', '.join(loaded)})")
    if len(set(chosen)) != len(chosen):
        raise StoreError("a graph is listed twice")
    return [(g, store.digest(g) or "", store.nodes(graph=g), store.edges(graph=g)) for g in chosen]


def _plain(value: Value) -> object:
    if isinstance(value, tuple):
        return [_plain(v) for v in value]
    if hasattr(value, "items") and not isinstance(value, str):
        return {k: _plain(v) for k, v in value.items()}
    return value


def _json(value: object) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _keys(all_props: list, prefix: str) -> dict[str, tuple[str, str]]:
    """Each property name -> (GraphML key id, attr.type), in name order."""
    values: dict[str, list[Value]] = {}
    for props in all_props:
        for name, value in props.items():
            values.setdefault(name, []).append(value)
    keys = {}
    for i, name in enumerate(sorted(values)):
        seen = values[name]
        if all(isinstance(v, bool) for v in seen):
            kind = "boolean"
        elif all(isinstance(v, int) and not isinstance(v, bool) for v in seen):
            kind = "long"
        elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in seen):
            kind = "double"
        else:
            kind = "string"
        keys[name] = (f"{prefix}{i}", kind)
    return keys


def _cell(key: tuple[str, str], value: Value) -> tuple[str, str]:
    key_id, kind = key
    if kind == "boolean":
        return key_id, "true" if value else "false"
    if kind in ("long", "double"):
        return key_id, repr(float(value)) if kind == "double" else str(value)
    return key_id, value if isinstance(value, str) else _json(value)


def _xml(text: str) -> str:
    """`text`, refused if XML cannot hold it (a NUL, say), so nothing is changed silently."""
    bad = _NOT_XML.search(text)
    if bad:
        raise StoreError(
            f"GraphML cannot hold the character U+{ord(bad.group()):04X} in {text[:60]!r}; "
            "export this graph as TriG, JSON-LD or CSV instead"
        )
    return text


def _attr(text: str) -> str:
    return quoteattr(_xml(text))


def _data(key_id: str, text: str) -> str:
    # A carriage return is escaped too, or XML readers turn "\r\n" into "\n".
    return f'      <data key="{key_id}">{escape(_xml(text), {chr(13): "&#13;"})}</data>'
