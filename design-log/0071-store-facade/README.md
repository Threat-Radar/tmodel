---
schema: archdoc/v1
id: DL-0071
title: Store façade with an Oxigraph adapter, and the library as nodes and edges
type: process
status: draft
version: "0.1.1"
date: "2026-11-25"
updated: "2026-11-26"
human_owner: Maimcghee
defers_to: ARCH-0001
---

# Question and scope

#65 (Sprint 6) asks for the store façade ADR-0004 and ADR-0008 describe: write and
read calls for nodes and typed edges with properties, ids that never change on a
rebuild, one adapter for Oxigraph, and the answers to the library loader's three
questions. The exports (Turtle, JSON-LD, GraphML, CSV) are a second story (#53).

The three answers were posted on #65 on 2026-11-16, with a fourth from the CWE
import (#233), and @Clovier accepted them for #142 the same day. This entry records
them as built.

This entry was opened as DL-0070. It became DL-0071 on 2026-11-26, because #272 took
DL-0070 on main first.

# What was built

- **`engine/store/facade.py`.** `Node` (id, type, properties), `Edge` (source,
  type, target, properties, id) and `Store`. The write call is `Store.load(graph,
  digest, nodes, edges)`: it replaces one source's named graph as a whole, and
  writes nothing when the graph already holds that digest. The reads are `node`,
  `nodes` and `edges`, filtered by graph, type, id or ends and returned sorted.
  Property values are text, numbers, true/false, and lists or mappings of these.
  None means no value. Invalid input raises `StoreError` before anything is written.
- **Stable ids.** A node keeps its file's id. An edge keeps its file's id when it
  has one (an Assertion id). Otherwise its id is derived from its two ends and its
  type (`edge_id`), so the same fact gets the same id on every rebuild. Within one
  graph an id names one node or one edge. Across graphs the same id may appear
  again, each graph keeping its own fields (answer 4).
- **`engine/store/oxigraph.py`, the one adapter.** It is the only module that
  imports `pyoxigraph` (a test checks this). Ids become IRIs under a base private
  to the store (`https://threat-radar.github.io/tmodel/store/`), so changing the
  base never changes an id.
  - An edge is the asserted triple (for SPARQL path queries), plus a reifier named
    by the edge id that carries its properties (RDF 1.2 `rdf:reifies`).
  - Digests live in the default graph, which holds nothing else.
  - A replace removes the old digest first, then writes the contents and the new
    digest in one transaction. A run that stops in between leaves no digest, so the
    half-written graph is rebuilt, and is cleared when the store is next opened.
- **`engine/store/library.py`, the answers for the library.**
  1. Each record is a node `library:<record-id>`. `split_source_ref` turns
     `library:<id>#<fragment>` into the node and a locator for the edge.
  2. All relation kinds, plus `cites` naming a record, become one forward edge per
     fact: `superseded_by`, `updated_by` and `cited_by` are read from the other end.
     `stated_by` keeps which records state each one. Citations with no record id
     stay on the node. A link to a record not held is listed in `missing`, with no
     edge and no empty node.
  3. The library is one graph, `library`, replaced only when `Library.digest`
     changes. #142 calls `load_library(store, library)` and needs no store code.
- **`pyoxigraph>=0.5.13,<0.6`** in `engine/pyproject.toml` (MIT or Apache-2.0;
  0.5.13 was released 2026-10-22). Nothing the CLI or server runs imports the store
  yet, so the packaged engine (#124) is unchanged until #142 uses it.

# Rejected or deferred

| Option | Outcome and reason |
|---|---|
| Add and remove single nodes or edges | Deferred: the agreed rebuild is a whole source at a time (answer 3), and a per-record update would need its own id and digest rules. |
| Derive edge ids from the properties too | Rejected: changing a property would change the id. Two edges with the same ends and type give their own ids instead. |
| Keep the inverse links as written | Rejected: 4 of the 12 `supersedes` and 3 of the 6 `updates` links on the pinned library are recorded on one side only, so two records would disagree in the graph. |
| Create empty nodes for missing link targets | Rejected (answer 2): the pinned library has none, and an empty node would look like a record. |
| RDF-star quoted triples as subjects | Not available: pyoxigraph 0.5 implements RDF 1.2, which replaces them with reifiers. ADR-0008 says "RDF-star"; the reifier is its standard form, so no ADR change is proposed. |
| Use the schema's `tmodel:` namespace for store IRIs | Deferred to the exports (#53): store IRIs are internal, and an export chooses its published vocabulary. |
| A stand-in adapter in the engine package | Rejected: #65 asks for one adapter. The stand-in lives in the tests. |

# Validation

Local, on Python 3.14 with `pyoxigraph` 0.5.13:

- **38 new tests**, the façade tests each run against Oxigraph and the stand-in adapter:
  - a small graph written, read back and rebuilt in a fresh store, with the same ids and edges;
  - an unchanged digest writes nothing, and a changed one replaces only that graph;
  - the same id kept separately in two graphs;
  - unusual ids and text, and exact numbers;
  - bad objects and loads refused with nothing changed;
  - an on-disk store reopened with its digests, and a half-finished replace cleared.
- The library tests use the fixture library and small built libraries:
  - node ids;
  - one-sided and two-sided inverse links giving the same edges;
  - record cites as edges, with external cites kept on the node;
  - missing targets listed;
  - loading twice giving the same store (#142's test).
- **822 engine tests pass, 10 skipped** (784 before). Ruff lint and format pass.
- The whole pinned library (`e406827`, 685 records) loads in 0.09 s:
  - 1,080 edges (757 `see_also`, 240 `cites`, 60 `part_of`, 12 `supersedes`, 6 `updates`, 4 `implements_concept`, 1 `contradicts`);
  - 860 external cites on nodes, and nothing missing;
  - a rebuild gives the same store.

# Human accepted / rejected

@Clovier accepted the three answers on #65 (2026-11-16). No human has reviewed this
code yet.
