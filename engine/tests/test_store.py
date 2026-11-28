"""The store façade (#65): nodes and typed edges with properties, stable ids, rebuilds.

Every façade test runs twice: against Oxigraph (ADR-0008) and against a stand-in
adapter that keeps plain dicts, so callers cannot depend on store details.
"""

from __future__ import annotations

import gc
from dataclasses import replace

import pytest

from engine.store import Edge, Node, Store, StoreError, edge_id
from engine.store.oxigraph import OxigraphAdapter


class StandIn:
    """The smallest adapter: one dict per graph, no RDF anywhere."""

    def __init__(self) -> None:
        self._graphs: dict[str, tuple[str, list[Node], list[Edge]]] = {}

    def digest(self, graph):
        return self._graphs[graph][0] if graph in self._graphs else None

    def graphs(self):
        return list(self._graphs)

    def replace(self, graph, digest, nodes, edges):
        self._graphs[graph] = (digest, list(nodes), list(edges))

    def drop(self, graph):
        self._graphs.pop(graph, None)

    def nodes(self, graph, type, id):
        for name, (_, nodes, _) in self._graphs.items():
            for n in nodes:
                if graph in (None, name) and type in (None, n.type) and id in (None, n.id):
                    yield n

    def edges(self, graph, source, type, target):
        for name, (_, _, edges) in self._graphs.items():
            for e in edges:
                if (
                    graph in (None, name)
                    and source in (None, e.source)
                    and type in (None, e.type)
                    and target in (None, e.target)
                ):
                    yield e


@pytest.fixture(params=["oxigraph", "stand-in"])
def new_store(request):
    """A function making a new, empty store of one kind."""
    if request.param == "oxigraph":
        return lambda: Store(OxigraphAdapter())
    return lambda: Store(StandIn())


def small_graph() -> tuple[list[Node], list[Edge]]:
    nodes = [
        Node("product:tcu", "Product", {"name": "Telematics unit", "version": 3}),
        Node(
            "weakness:cwe-306",
            "Weakness",
            {
                "name": "Missing Authentication for Critical Function",
                "score": 7.5,
                "abstract": False,
                "aliases": ["CWE-306", "missing auth"],
                "content": {
                    "url": "https://cwe.mitre.org/data/definitions/306.html",
                    "pages": None,
                },
                "note": None,  # None is no value, so it is left out
            },
        ),
        Node("library:rfc-8785", "LibraryRecord", {"title": "JCS", "id": "rfc-8785"}),
    ]
    edges = [
        Edge("product:tcu", "has_weakness", "weakness:cwe-306", {"locator": "§4.2", "rank": 1}),
        Edge("weakness:cwe-306", "source_ref", "library:rfc-8785"),
        # The same ends and type twice: the file gives each its own (Assertion) id.
        Edge("product:tcu", "cites", "library:rfc-8785", {"locator": "§3"}, id="assertion:a1"),
        Edge("product:tcu", "cites", "library:rfc-8785", {"locator": "§5"}, id="assertion:a2"),
    ]
    return nodes, edges


def snapshot(store: Store) -> tuple:
    return store.graphs(), store.nodes(), store.edges()


def test_write_and_read_nodes_and_edges(new_store):
    store = new_store()
    nodes, edges = small_graph()
    assert store.load("model:tcu", "d1", nodes, edges) is True
    assert store.graphs() == ("model:tcu",)
    assert store.digest("model:tcu") == "d1"

    weakness = store.node("weakness:cwe-306", "model:tcu")
    assert weakness == replace(nodes[1], graph="model:tcu")
    assert weakness.properties["aliases"] == ("CWE-306", "missing auth")
    assert weakness.properties["content"] == {
        "url": "https://cwe.mitre.org/data/definitions/306.html",
        "pages": None,
    }
    assert weakness.properties["score"] == 7.5 and weakness.properties["abstract"] is False
    assert "note" not in weakness.properties
    assert store.node("product:tcu", "model:tcu").properties["version"] == 3

    assert [n.id for n in store.nodes()] == ["library:rfc-8785", "product:tcu", "weakness:cwe-306"]
    assert [n.id for n in store.nodes(type="Weakness")] == ["weakness:cwe-306"]
    assert store.edges() == tuple(
        sorted(
            (replace(e, graph="model:tcu") for e in edges),
            key=lambda e: (e.source, e.type, e.target, e.id),
        )
    )
    has = store.edges(source="product:tcu", type="has_weakness")
    assert len(has) == 1 and has[0].properties == {"locator": "§4.2", "rank": 1}
    assert has[0].id == edge_id("product:tcu", "has_weakness", "weakness:cwe-306")
    cites = store.edges(type="cites", target="library:rfc-8785")
    assert [(e.id, e.properties["locator"]) for e in cites] == [
        ("assertion:a1", "§3"),
        ("assertion:a2", "§5"),
    ]
    assert store.edges(source="library:rfc-8785") == ()


def test_rebuild_keeps_every_id(new_store):
    """No id churn: rebuilding from the same files gives the same ids and edges."""
    first, second = new_store(), new_store()
    for store in (first, second):
        nodes, edges = small_graph()
        store.load("model:tcu", "d1", nodes, edges)
    assert snapshot(first) == snapshot(second)
    assert [e.id for e in first.edges()] == [e.id for e in second.edges()]

    # A new digest rebuilds the graph, and unchanged facts keep their ids.
    nodes, edges = small_graph()
    first.load("model:tcu", "d2", nodes, edges)
    assert first.digest("model:tcu") == "d2"
    assert snapshot(first)[1:] == snapshot(second)[1:]


def test_same_digest_writes_nothing(new_store):
    store = new_store()
    nodes, edges = small_graph()
    assert store.load("model:tcu", "d1", nodes, edges) is True
    before = snapshot(store)
    assert store.load("model:tcu", "d1", nodes[:1], []) is False
    assert snapshot(store) == before


def test_changed_digest_replaces_only_that_graph(new_store):
    store = new_store()
    nodes, edges = small_graph()
    store.load("model:tcu", "d1", nodes, edges)
    store.load("catalog:cwe-4.21", "c1", [Node("weakness:cwe-306", "Weakness", {"name": "CWE"})])
    store.load("model:tcu", "d2", nodes[:1], [])
    assert [n.id for n in store.nodes(graph="model:tcu")] == ["product:tcu"]
    assert store.edges(graph="model:tcu") == ()
    assert store.node("weakness:cwe-306", "catalog:cwe-4.21").properties == {"name": "CWE"}


def test_same_id_in_two_graphs_keeps_both(new_store):
    """The catalog's CWE-306 and a model's own CWE-306 share one id, not one set of fields."""
    store = new_store()
    store.load(
        "catalog:cwe-4.21", "c1", [Node("weakness:cwe-306", "Weakness", {"text": "catalog"})]
    )
    store.load("model:mvp-02", "m1", [Node("weakness:cwe-306", "Weakness", {"text": "model"})])
    copies = store.nodes(id="weakness:cwe-306")
    assert [(n.graph, n.properties["text"]) for n in copies] == [
        ("catalog:cwe-4.21", "catalog"),
        ("model:mvp-02", "model"),
    ]
    assert store.drop("model:mvp-02") is True
    assert store.drop("model:mvp-02") is False
    assert store.graphs() == ("catalog:cwe-4.21",)
    assert [n.graph for n in store.nodes(id="weakness:cwe-306")] == ["catalog:cwe-4.21"]


def test_unusual_ids_and_text_round_trip(new_store):
    store = new_store()
    odd = ["a b", "x#frag", "100%", "ü:ñ/é", '<>"{}|\\^`', "?q=1&r"]
    nodes = [Node(i, "Odd type/ü", {"text": "line\nbreak \u0000 ünï"}) for i in odd]
    edges = [Edge(odd[0], "rel with space", odd[1], {"k ey": "v"})]
    store.load("graph with space/#", "d", nodes, edges)
    assert [n.id for n in store.nodes()] == sorted(odd)
    assert store.node("ü:ñ/é", "graph with space/#").properties == {
        "text": "line\nbreak \u0000 ünï"
    }
    assert store.edges()[0].properties == {"k ey": "v"}
    assert store.graphs() == ("graph with space/#",)


def test_numbers_round_trip_exactly(new_store):
    store = new_store()
    values = {"big": 2**70, "neg": -3, "tiny": 1e-300, "huge": 1e300, "third": 1 / 3, "t": True}
    store.load("g", "d", [Node("n", "T", values)])
    read = store.node("n", "g").properties
    assert read == values
    assert type(read["big"]) is int and type(read["t"]) is bool and type(read["huge"]) is float


@pytest.mark.parametrize(
    "make",
    [
        lambda: Node("", "T"),
        lambda: Node("n", ""),
        lambda: Node("n", "T", {"x": float("nan")}),
        lambda: Node("n", "T", {"x": {1, 2}}),
        lambda: Node("n", "T", {"x": {1: "a"}}),
        lambda: Node("n", "T", {"": "a"}),
        lambda: Node("n", "T", ["not", "a", "mapping"]),
        lambda: Edge("a", "", "b"),
        lambda: Edge("a", "t", "b", {"x": object()}),
    ],
)
def test_bad_objects_are_refused(make):
    with pytest.raises(StoreError):
        make()


def test_bad_loads_are_refused_and_change_nothing(new_store):
    store = new_store()
    nodes, edges = small_graph()
    store.load("model:tcu", "d1", nodes, edges)
    before = snapshot(store)
    bad = [
        ("model:tcu", "d2", [nodes[0], nodes[0]], []),  # one id, two nodes
        ("model:tcu", "d2", nodes, [edges[2], edges[2]]),  # one id, two edges
        ("model:tcu", "d2", nodes, [Edge("a", "t", "b", id="product:tcu")]),  # edge id = node id
        ("model:tcu", "d2", [replace(nodes[0], graph="other")], []),  # from another graph
        ("model:tcu", "", nodes, []),
        ("", "d2", nodes, []),
        ("model:tcu", "d2", ["product:tcu"], []),
    ]
    for graph, digest, n, e in bad:
        with pytest.raises(StoreError):
            store.load(graph, digest, n, e)
    assert snapshot(store) == before


def test_on_disk_store_keeps_ids_and_digests_between_runs(tmp_path):
    nodes, edges = small_graph()
    store = Store.open(str(tmp_path / "store"))
    store.load("model:tcu", "d1", nodes, edges)
    before = snapshot(store)
    del store
    gc.collect()  # releases the folder's lock

    reopened = Store.open(str(tmp_path / "store"))
    assert snapshot(reopened) == before
    assert reopened.load("model:tcu", "d1", nodes, edges) is False


def test_a_replace_that_stopped_half_way_is_cleared_on_open(tmp_path):
    """Contents with no digest are a replace that did not finish: never read as loaded."""
    from pyoxigraph import Literal, NamedNode, Quad
    from pyoxigraph import Store as Oxigraph

    from engine.store import oxigraph

    path = str(tmp_path / "store")
    store = Store.open(path)
    store.load("model:tcu", "d1", *small_graph())
    del store
    gc.collect()
    raw = Oxigraph(path)  # a half-finished write: contents in a graph with no digest
    half = NamedNode(oxigraph.BASE + "graph/half")
    raw.add(
        Quad(
            NamedNode(oxigraph.BASE + "id/x"),
            NamedNode(oxigraph.BASE + "prop/p"),
            Literal("v"),
            half,
        )
    )
    del raw
    gc.collect()

    reopened = Store.open(path)
    assert reopened.graphs() == ("model:tcu",)
    assert reopened.digest("half") is None
    assert all(n.graph == "model:tcu" for n in reopened.nodes())
    assert reopened.load("half", "h1", [Node("x", "T")]) is True


def test_only_the_oxigraph_module_imports_pyoxigraph():
    """The façade and the library mapping stay store-neutral (ADR-0004, ADR-0008)."""
    from pathlib import Path

    import engine.store

    folder = Path(engine.store.__file__).parent
    users = sorted(p.name for p in folder.glob("*.py") if "pyoxigraph" in p.read_text("utf-8"))
    assert users == ["oxigraph.py"]
