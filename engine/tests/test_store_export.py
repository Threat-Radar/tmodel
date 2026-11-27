"""Store exports (#65, #53): what each format keeps and loses, as round trips (CF-008).

Each export is written from the store, read back, and compared with what the store
holds. The RDF formats are read back into a fresh Oxigraph store and compared through
the façade, so ids, types, properties, graphs and digests are all checked.
"""

from __future__ import annotations

import csv
import io
import json
from xml.etree import ElementTree

import pytest
from test_store import StandIn, small_graph

from engine.store import Edge, Node, Store, StoreError
from engine.store.export import (
    GRAPHML_NS,
    to_csv,
    to_graphml,
    to_jsonld,
    to_trig,
    to_turtle,
)
from engine.store.oxigraph import OxigraphAdapter

G = f"{{{GRAPHML_NS}}}"


def two_sources(store: Store) -> Store:
    """A model and a catalog that share one id (answer 4 on #65), plus odd ids and text."""
    nodes, edges = small_graph()
    nodes.append(Node("a b#c/ü%", "Odd type", {"text": "line\nbreak\r\nend", "n": 0}))
    edges.append(Edge("a b#c/ü%", "rel with space", "product:tcu"))
    store.load("model:tcu", "d1", nodes, edges)
    store.load(
        "catalog:cwe-4.21",
        "c1",
        [Node("weakness:cwe-306", "Weakness", {"name": "CWE's own name", "score": 9})],
        [Edge("weakness:cwe-306", "child_of", "weakness:cwe-284", {"view": "CWE-1000"})],
    )
    return store


@pytest.fixture(params=["oxigraph", "stand-in"])
def store(request):
    return two_sources(Store(OxigraphAdapter() if request.param == "oxigraph" else StandIn()))


def everything(store: Store) -> tuple:
    return (
        store.graphs(),
        tuple(store.digest(g) for g in store.graphs()),
        store.nodes(),
        store.edges(),
    )


# --- the RDF formats --------------------------------------------------------------------------


def test_trig_keeps_everything(store):
    data = to_trig(store)
    assert b"rdf:reifies" in data and b"<<(" in data  # RDF 1.2 reifiers (ADR-0007, ADR-0008)
    back = Store(OxigraphAdapter.from_export(data, "trig"))
    assert everything(back) == everything(store)


def test_jsonld_keeps_everything_with_classic_reification(store):
    data = to_jsonld(store)
    doc = json.loads(data)
    text = json.dumps(doc)
    assert "reifies" not in text and "Statement" in text  # JSON-LD has no triple terms yet
    back = Store(OxigraphAdapter.from_export(data, "jsonld"))
    assert everything(back) == everything(store)


def test_turtle_keeps_one_graph_but_not_its_digest(store):
    data = to_turtle(store, "model:tcu")
    assert b"digest" not in data and b"cwe-4.21" not in data
    back = Store(OxigraphAdapter.from_export(data, "turtle", graph="model:tcu", digest="d1"))
    assert back.nodes() == store.nodes(graph="model:tcu")
    assert back.edges() == store.edges(graph="model:tcu")
    with pytest.raises(StoreError):
        OxigraphAdapter.from_export(data, "turtle")  # Turtle carries no graph or digest


def test_classic_reification_keeps_everything_too(store):
    """rdf12=False writes each edge as an rdf:Statement, for readers that predate RDF 1.2."""
    trig = to_trig(store, rdf12=False)
    assert b"<<(" not in trig and b"rdf:Statement" in trig
    assert everything(Store(OxigraphAdapter.from_export(trig, "trig"))) == everything(store)
    turtle = to_turtle(store, "model:tcu", rdf12=False)
    back = Store(OxigraphAdapter.from_export(turtle, "turtle", graph="model:tcu", digest="d1"))
    assert back.edges() == store.edges(graph="model:tcu")


def test_an_rdf_1_1_reader_reads_the_classic_exports(store):
    """rdflib 7 has no RDF 1.2 yet: it reads JSON-LD and classic TriG, not RDF 1.2 TriG."""
    rdflib = pytest.importorskip("rdflib")  # not an engine dependency, so CI skips this
    for data, fmt in ((to_jsonld(store), "json-ld"), (to_trig(store, rdf12=False), "trig")):
        dataset = rdflib.Dataset()
        dataset.parse(data=data, format=fmt)
        found = dataset.quads((None, rdflib.RDF.type, rdflib.RDF.Statement, None))
        assert len({(s, g) for s, _, _, g in found}) == len(store.edges())


def test_rdf_ids_are_the_store_iris(store):
    data = to_trig(store).decode("utf-8")
    assert "@prefix id: <https://threat-radar.github.io/tmodel/store/id/>" in data
    assert "id:weakness:cwe-306 edge:source_ref id:library:rfc-8785 ." in data
    assert 'graph:catalog:cwe-4.21 tm:digest "c1" .' in data


# --- CSV --------------------------------------------------------------------------------------


def read_csv(nodes: bytes, edges: bytes) -> tuple[tuple[Node, ...], tuple[Edge, ...]]:
    node_rows = list(csv.DictReader(io.StringIO(nodes.decode("utf-8"), newline="")))
    edge_rows = list(csv.DictReader(io.StringIO(edges.decode("utf-8"), newline="")))
    read_nodes = tuple(
        Node(r["id"], r["type"], json.loads(r["properties"]), r["graph"]) for r in node_rows
    )
    read_edges = tuple(
        Edge(r["source"], r["type"], r["target"], json.loads(r["properties"]), r["id"], r["graph"])
        for r in edge_rows
    )
    return read_nodes, read_edges


def test_csv_keeps_every_node_and_edge_of_every_graph(store):
    nodes, edges = to_csv(store)
    assert nodes.splitlines()[0] == b"graph,id,type,properties"
    assert edges.splitlines()[0] == b"graph,id,source,type,target,properties"
    read_nodes, read_edges = read_csv(nodes, edges)
    key = lambda n: (n.graph, n.id)  # noqa: E731
    assert sorted(read_nodes, key=key) == sorted(store.nodes(), key=key)
    assert sorted(read_edges, key=lambda e: (e.graph, e.id)) == sorted(
        store.edges(), key=lambda e: (e.graph, e.id)
    )


# --- GraphML ----------------------------------------------------------------------------------


def read_graphml(data: bytes) -> tuple[dict, dict, dict]:
    root = ElementTree.fromstring(data)
    keys = {k.get("id"): (k.get("attr.name"), k.get("attr.type")) for k in root.iter(G + "key")}

    def fields(element):
        return {keys[d.get("key")][0]: d.text or "" for d in element.iter(G + "data")}

    nodes = {n.get("id"): fields(n) for n in root.iter(G + "node")}
    edges = {
        e.get("id"): {"source": e.get("source"), "target": e.get("target"), **fields(e)}
        for e in root.iter(G + "edge")
    }
    return nodes, edges, {name: kind for name, kind in keys.values()}


def test_graphml_has_one_node_per_id_and_says_which_graphs_hold_it(store):
    nodes, edges, kinds = read_graphml(to_graphml(store))
    ids = {n.id for n in store.nodes()} | {"weakness:cwe-284"}  # the bare end of an edge
    assert set(nodes) == ids
    shared = nodes["weakness:cwe-306"]
    # The first graph in `graphs` order (default: sorted) gives the fields.
    assert json.loads(shared["tmodel:graphs"]) == ["catalog:cwe-4.21", "model:tcu"]
    assert shared["name"] == "CWE's own name" and "aliases" not in shared
    assert nodes["weakness:cwe-284"] == {"tmodel:graphs": "[]"}
    assert {e["tmodel:type"] for e in edges.values()} >= {"cites", "child_of", "has_weakness"}
    assert edges["assertion:a1"]["locator"] == "§3"
    # Types come from the values written: the catalog's score (9) wins here, so it is long.
    assert kinds["score"] == "long" and kinds["n"] == "long"
    assert "abstract" not in kinds  # only the model's copy has it, and the catalog's won


def test_graphml_graph_order_picks_whose_fields_win(store):
    nodes, _, kinds = read_graphml(to_graphml(store, ["model:tcu", "catalog:cwe-4.21"]))
    shared = nodes["weakness:cwe-306"]
    assert json.loads(shared["tmodel:graphs"]) == ["model:tcu", "catalog:cwe-4.21"]
    assert shared["name"] == "Missing Authentication for Critical Function"
    assert json.loads(shared["aliases"]) == ["CWE-306", "missing auth"]
    # Now the model's score (7.5) is written, so the key is a double.
    assert kinds["score"] == "double" and kinds["abstract"] == "boolean"
    assert kinds["aliases"] == "string"


def test_graphml_keeps_line_breaks_and_odd_ids(store):
    nodes, edges, _ = read_graphml(to_graphml(store, ["model:tcu"]))
    assert nodes["a b#c/ü%"]["text"] == "line\nbreak\r\nend"
    assert any(e["source"] == "a b#c/ü%" for e in edges.values())


def test_graphml_refuses_a_character_xml_cannot_hold():
    store = Store()
    store.load("g", "d", [Node("n", "T", {"text": "a\u0000b"})])
    with pytest.raises(StoreError, match="U\\+0000"):
        to_graphml(store)
    back = Store(OxigraphAdapter.from_export(to_trig(store), "trig"))
    assert back.node("n", "g").properties == {"text": "a\u0000b"}  # TriG keeps it


# --- every format ------------------------------------------------------------------------------


def all_exports(store: Store) -> dict[str, bytes]:
    nodes, edges = to_csv(store)
    return {
        "turtle": to_turtle(store, "model:tcu"),
        "trig": to_trig(store),
        "jsonld": to_jsonld(store),
        "graphml": to_graphml(store),
        "csv-nodes": nodes,
        "csv-edges": edges,
    }


def test_the_same_store_gives_the_same_bytes():
    first = all_exports(two_sources(Store()))
    again = all_exports(two_sources(Store()))
    assert first == again


def test_exports_read_only_the_facade():
    """A stand-in adapter gives byte-identical exports, so no export reads the store directly."""
    assert all_exports(two_sources(Store(StandIn()))) == all_exports(two_sources(Store()))


def test_only_loaded_graphs_can_be_exported(store):
    with pytest.raises(StoreError, match="not loaded: model:none"):
        to_trig(store, ["model:none"])
    with pytest.raises(StoreError, match="listed twice"):
        to_csv(store, ["model:tcu", "model:tcu"])
    with pytest.raises(StoreError, match="not loaded"):
        to_turtle(store, "catalog:none")
