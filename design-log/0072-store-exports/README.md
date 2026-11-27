---
schema: archdoc/v1
id: DL-0072
title: Exports of the working store - Turtle, TriG, JSON-LD, GraphML and CSV
type: process
status: draft
version: "0.1.1"
date: "2026-11-26"
updated: "2026-11-26"
human_owner: Maimcghee
defers_to: ARCH-0001
---

# Question and scope

#65 left the exports to a second story: Turtle, JSON-LD, GraphML and CSV, written from the working store (#53, BACKLOG T-209). ADR-0004 decision 4 and ADR-0007 fix them as derived, never canonical. ADR-0007 also asks for the DEC-002 round trip (CF-008): test what each format keeps and what it loses. Every object and edge keeps one stable id in every encoding (ADR-0004). This builds on the store façade (DL-0071, #273) and is stacked on it. (This entry was opened as DL-0071, and the façade's as DL-0070. Both moved up one on 2026-11-26, because #272 took DL-0070 on main first.)

# What was built

- **`engine/store/export.py`:** `to_turtle`, `to_trig`, `to_jsonld`, `to_graphml` and `to_csv`. Each reads the store only through the façade, and each refuses a graph that isn't loaded.
  - The default is every graph, sorted by name. The same store always gives the same bytes.
  - A stand-in adapter gives byte-identical files, which shows that no export reads the store directly.
- **RDF formats, in `engine/store/oxigraph.py`:** the store's own IRIs, written with short prefixes (`id:`, `edge:`, `prop:`, `type:`, `graph:`). An id is the IRI's last part, decoded.
  - **TriG:** every graph, and the digests. Each edge is an RDF 1.2 reifier, the standard form of the RDF-star that ADR-0007 and ADR-0008 name.
  - **Turtle:** one graph. Turtle has no named graphs, so the digest is left out.
  - **JSON-LD:** every graph and the digests, written expanded. JSON-LD can't hold a triple term yet (Oxigraph: "JSON-LD does not support RDF 1.2 yet"). So each edge is a classic `rdf:Statement`, with the same IRI and properties: the reified form ADR-0004 allows.
  - **`rdf12=False`:** writes Turtle and TriG the same classic way, for readers that predate RDF 1.2.
  - **`OxigraphAdapter.from_export`:** reads any of these back, so the round trips can be tested.
- **CSV:** two files, `nodes.csv` (graph, id, type, properties) and `edges.csv` (graph, id, source, type, target, properties). There is one row per graph's copy, with the properties as one JSON object, so nothing is lost.
- **GraphML, for viewers:**
  - **Ids:** one node per id and one edge per edge id. When several of the chosen graphs hold an id, the first in `graphs` order gives its type and fields, and `tmodel:graphs` lists every graph that holds it.
  - **Bare nodes:** an edge to a node no chosen graph holds gets a bare node.
  - **Types:** a property gets a GraphML type only when all its values share it. Otherwise it is a string, with non-text values as JSON.
  - **Refusals:** a character XML can't hold (NUL, say) is refused, and the error names the formats that keep it. A carriage return is escaped, so it survives.

# What each format keeps (CF-008)

| Format | Graphs | Digests | Ids, types, properties | Read back by |
|---|---|---|---|---|
| TriG | all | yes | all | `from_export`, identical through the façade; rdflib 7.6 with `rdf12=False` |
| Turtle | one | no | all, for that graph | `from_export`, given the graph and digest |
| JSON-LD | all | yes | all | `from_export`, identical; rdflib 7.6 |
| CSV | all, a column | no | all | the test's reader, identical |
| GraphML | merged by id | no | the first graph's copy; others named in `tmodel:graphs` | ElementTree in the tests; networkx 3.4.2 |

# Rejected or deferred

| Option | Outcome and reason |
|---|---|
| Map store IRIs to the schema's `tmodel:` namespace | Deferred. Library records, relation kinds and the store's own types aren't schema terms, and the schema declares no IRI form for ids. The store IRIs are stable, and an export carries them with prefixes. DL-0071 had left this to the exports. |
| RDF 1.2 reifiers in JSON-LD | Not possible yet: neither JSON-LD 1.1 nor Oxigraph can write a triple term. |
| Turtle for several graphs | Turtle has no named graphs. TriG is Turtle with graphs. |
| CSV with one column per property | Rejected: an empty cell can't tell an absent property from an empty one, and numbers lose their type. One JSON column keeps both. |
| GraphML with one node per (graph, id) | Rejected: the same object would get two ids, and edges between graphs would not meet. |
| Replace characters XML can't hold | Rejected: that changes data silently. The error names the formats that keep them. |
| A `tmodel export` command | Deferred: nothing loads the store from the CLI yet. #142 wires the library into it. |

# Validation

Local, on Python 3.14 with `pyoxigraph` 0.5.13:

- **25 new tests**, the export tests each run against Oxigraph and the stand-in adapter:
  - TriG, JSON-LD and classic TriG read back identical through the façade, and Turtle reads back one graph;
  - CSV reads back identical;
  - GraphML: one node per id, the graph order picks whose fields are written, typed keys, line breaks and odd ids kept, and a NUL refused;
  - the same bytes twice, the same bytes through the stand-in, and unknown or repeated graphs refused;
  - with rdflib installed, it reads the JSON-LD and the classic TriG and finds every edge.
- **Engine suite:** 846 passed, 12 skipped (823 before). The 2 new skips are the rdflib test, since rdflib isn't an engine dependency. With rdflib 7.6.0 installed, all 25 export tests pass. Ruff lint and format pass.
- **The whole pinned library** (`e406827`, 685 records, 907 edges, after #273's one edge per `see_also` pair). Each export takes about 0.1 s:
  - TriG 1.51 MB, Turtle 1.49 MB, JSON-LD 3.46 MB, GraphML 1.59 MB, and CSV 1.12 MB plus 0.14 MB;
  - TriG and JSON-LD read back identical;
  - rdflib 7.6.0 reads the JSON-LD and the classic TriG (21,305 quads each), but not the RDF 1.2 TriG;
  - networkx 3.4.2 reads the GraphML: 685 nodes, 907 edges. Each `see_also` pair is one edge, so no pair shows twice (@Clovier's review).

# Human accepted / rejected

@Maimcghee asked for this as #65's second story. No human has reviewed this code yet.
