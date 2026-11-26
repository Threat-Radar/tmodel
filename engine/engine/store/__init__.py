"""The working store behind one façade (#65; ADR-0004, ADR-0008).

    from engine.store import Store, export
    from engine.store.library import load_library

    store = Store()                      # Oxigraph in memory; Store.open(path) keeps it on disk
    load_library(store, library)         # the loaded library, as the graph "library"
    store.edges(source="library:rfc-8785")
    export.to_trig(store)                # also Turtle, JSON-LD, GraphML and CSV

Callers use `Store`, `Node` and `Edge` only; `engine.store.oxigraph` is the one
module that knows the store is RDF.
"""

from .facade import Adapter, Edge, Node, Store, StoreError, edge_id

__all__ = ["Adapter", "Edge", "Node", "Store", "StoreError", "edge_id"]
