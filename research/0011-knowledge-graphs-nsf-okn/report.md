---
schema: "archdoc/v1"
id: RPT-0011
title: "Knowledge Graphs and NSF OKN"
short_title: "Knowledge graphs & NSF OKN"
description: "Landscape of knowledge-graph practice and the NSF Open Knowledge Network, with applicability + gap analysis for the tmodel threat-modeling knowledge graph. Evidence, not decisions."
type: research
category: knowledge-graph
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
authors:
  - role: sponsor
    id: paul-lambert
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0011-knowledge-graphs-nsf-okn/report.md
library_commit: "see library/ submodule pointer at merge (records under Threat-Radar/library PR #4)"
informs: [DEC-001, DEC-002, DEC-004, DEC-006, R-018]
open_decisions: [DEC-001, DEC-002, DEC-004, DEC-006]
issue: 25
---

# Knowledge Graphs and NSF OKN

> **First draft. Evidence, not decisions.** Every `DEC-*` it informs is open; nothing
> here selects a graph model, encoding, or stack. References are in `library/`
> (Threat-Radar/library PR #4); the full gathered set is in [`sources.md`](sources.md),
> the axes in [`dimensions.md`](dimensions.md), the query log in [`searches.md`](searches.md).

## Why this report

NSF just launched the **NSF Open Knowledge Network** (okn.us) — a national, **federated**
infrastructure of **43 interconnected knowledge graphs** built to give AI a *verifiable,
attributed, governed* knowledge layer (grounding, provenance, auditability). One flagship
cross-graph query maps **cybersecurity exposure across 7,000+ semiconductor products from
247 companies** — supply-chain security *is* an OKN use case. tmodel is itself building a
threat-modeling knowledge graph whose whole point is *AI proposes, humans review, grounded
and auditable*. So OKN is simultaneously a **precedent**, a **standards signal**, and a
possible **federation target**. This report surveys KG practice across four dimensions and
asks, for each source, *what does tmodel take from it?*

## At a glance

| dimension | load-bearing sources | what tmodel takes |
|---|---|---|
| NSF OKN | `nsf-okn-launch`, `frink-fabric`, `securechain-okn`, `sudokn-okn`, `okn-roadmap-2022` | federation pattern (named graphs + one SPARQL endpoint), provenance-by-construction, a supply-chain-security precedent, a possible network to join |
| KG standards | `rdf-1-1-concepts`, `owl-2-primer`, `sparql-1-1`, `shacl`, `prov-o`, `linkml`, `hogan-kg-survey` | an **RDF-world stack**: LinkML → SHACL + OWL/RDF → RML/JSON-LD → PROV-O → SPARQL |
| Cyber KGs | `stix-2-1`, `mitre-attack`, `cwe`, `capec`, `d3fend`, `cve-json-5`, `osv-schema`, `bron`, `guac`, `spdx-3-rdf`, `mulval` | reuse existing vocab/IDs + the **BRON backbone**; D3FEND/SPDX as importable OWL/RDF; GUAC as the supply-chain analog |
| AI grounding | `graphrag-ms`, `unifying-llm-kg`, RoG, ToG | the mechanism for *AI proposes / KG constrains / human corrects* — traceable, auditable |

## 1. NSF OKN — a national, federated, governed KG

OKN grew from the Proto-OKN program (NSF 23-571; $26.7M; 18 teams; partners NIH/NASA/NIJ/NOAA/USGS) into a live federation of 43 graphs. Its architecture is exactly the shape tmodel needs:

- **Fabric / federation** (`frink-fabric`, RENCI): each domain graph is a **named-graph URI** with catalog metadata, all exposed through **one federated SPARQL endpoint**; interoperability comes from **identifier harmonization** and shared graph-construction best practices. Provenance is *operational* (named graphs + stable identifiers) rather than a published policy.
- **Supply-chain security is a use case** (`securechain-okn` — Purdue software supply chain; `sudokn-okn` — ASU manufacturing supply/demand, the best fit for the semiconductor-exposure query). tmodel's composition→weakness→product layer is the same pattern.
- **Grounding AI** (`nsf-okn-launch`, `mcp-okn`): OKN's thesis — "a shared, explicit, interoperable, auditable representation … on which [AI] systems reason and act" — is tmodel's thesis for human-reviewed threat models. `mcp-okn` shows an LLM→governed-KG bridge.

**Takeaway:** OKN validates the whole approach and points to an **RDF/SPARQL/LinkML** stack; federating tmodel's threat graph into OKN (national-security domain) is a live option.

## 2. Knowledge-graph foundations & standards

The `hogan-kg-survey` frames the core fork: **RDF-world** vs **property-graph (LPG)**.
- **RDF world** (`rdf-1-1-concepts`, `owl-2-primer`, `sparql-1-1`): standard semantics, named graphs, `SERVICE` federation. Wins on interoperability, provenance vocabularies, and federation (OKN).
- **LPG world** (openCypher, ISO **GQL** 2024, Neo4j): wins on real-time multi-hop traversal performance and edge-property ergonomics.
- **Validation** (`shacl`): shapes enforce that, e.g., *every risk node carries a provenance link and a review status before acceptance* — a natural **human-review gate**, with violations reported to reviewers.
- **Provenance** (`prov-o`): Entity/Activity/Agent + `wasGeneratedBy`/`wasAttributedTo`/`wasDerivedFrom` — the backbone for tmodel's review/audit (source of each assertion, the analysis activity, the human reviewer as agent). Ties to R-018.
- **Schema authoring** (`linkml`): write the threat/asset/CWE/CVE schema once → generate SHACL + OWL/RDF; it's the language OKN/biomedical teams use, so it also buys federation alignment.

**Takeaway (evidence for DEC-002/DEC-004):** provenance + validation + OKN federation all pull toward the **RDF-world stack**; LPG stays viable only if raw traversal performance dominates and federation is dropped.

## 3. Knowledge graphs for cybersecurity / threat modeling

The field already offers most of tmodel's vocabulary and a working backbone:
- **STIX 2.1** (`stix-2-1`): threat intel *as a graph* — 17 node types (Attack Pattern, Vulnerability, Course of Action, Threat Actor…), typed relationship edges, and **`Opinion`/`Note`** objects that map directly onto tmodel's human-review layer. The strongest candidate interchange schema.
- **MITRE data as graphs**: `mitre-attack`, `cwe`, `capec`, `d3fend`. CWE/CAPEC ship typed relations + XSD; **D3FEND is already an OWL knowledge graph** (defense→offense edges) with a Digital Artifact Ontology that seeds asset modeling.
- **Vulnerabilities**: `cve-json-5` (CVE→CWE, CVSS metrics), `osv-schema` (vuln→exact package/version).
- **BRON** (`bron`): a bidirectional graph already linking **ATT&CK↔CAPEC↔CWE↔CVE↔CPE** — a reusable reference implementation of tmodel's exact backbone.
- **Supply chain**: **GUAC** (`guac`) is the closest working analog (SBOMs + attestations + vulns as a graph; three trees — Evidence/Actor/Software — that map to review-provenance / actors / assets-components); **SPDX 3.0** (`spdx-3-rdf`) is a graph-native SBOM in RDF/OWL/SHACL.
- **Attack paths**: `mulval` (logic/Datalog derivation of reachable paths) — facts=nodes, rules=logic, derivation graph = the reviewable attack-path artifact (ties to our Attack step / Attack path model).

**Takeaway:** don't invent vocabulary — **align to STIX + MITRE + CVE/OSV and reuse the BRON backbone**; import D3FEND/SPDX OWL if RDF; study GUAC for the supply-chain portion.

## 4. Grounding AI with knowledge graphs

- `unifying-llm-kg` (Pan et al.) names three patterns; the **synergized** one — *LLM proposes, KG constrains/verifies* — is essentially tmodel's design.
- **GraphRAG** (`graphrag-ms`) builds a KG then reasons for global, provenance-traceable answers; **RoG** (Reasoning-on-Graphs) and **ToG** (Think-on-Graph) constrain LLM reasoning to real graph paths and are **traceable + expert-correctable** — the concrete mechanism that makes *AI proposes → human reviews* auditable (informs DEC-006).

## 5. Synthesis

The evidence converges on a coherent direction (to be ratified by ADRs, not here):
1. **Lean RDF-world** — because provenance (PROV-O), validation (SHACL), OKN federation, and importable ontologies (D3FEND, SPDX) all live there. Keep LPG as the fallback if traversal performance dominates.
2. **Reuse, don't reinvent** — align the object model to **STIX 2.1 + MITRE (ATT&CK/CWE/CAPEC/D3FEND) + CVE/OSV**, and adopt the **BRON** backbone; author the schema in **LinkML**.
3. **Provenance + review are graph-native** — **PROV-O** for attribution/audit, **SHACL** as the acceptance gate, STIX **Opinion/Note** for reviewer verdicts.
4. **Ground AI with the graph** — RoG/ToG-style constrained, traceable reasoning over the KG; GUAC/GraphRAG as construction precedents.
5. **Consider federating with OKN** — via FRINK (named graph + SPARQL); tmodel's supply-chain threat data is squarely an OKN use case.

## 6. Gap analysis — tmodel vs. KG/OKN state of the art

| capability | OKN / KG state of the art | tmodel status | recommendation → routing |
|---|---|---|---|
| Graph substrate | RDF or LPG, standardized | **undecided** | evidence favors RDF → **DEC-002/DEC-004** |
| Schema authoring | LinkML (OKN-wide) | ad-hoc YAML (spec/schema) | adopt LinkML → **#17** |
| Provenance/attribution | PROV-O, named graphs | in ARCH-0001 §7 as concept, no model | adopt **PROV-O** → **R-018 / #17** |
| Human-review gate | SHACL validation; STIX Opinion/Note | described, not mechanized | **SHACL** acceptance gate → **#17 / #5** |
| Vocabulary | STIX/ATT&CK/CWE/CAPEC/CVE reused | our own draft types | align/import → **#9 / #17** |
| Cross-domain backbone | BRON (ATT&CK↔CAPEC↔CWE↔CVE↔CPE) | not yet built | reuse **BRON** → **#17** |
| Supply-chain graph | GUAC, SPDX-RDF, deps.dev | tradar output only | study **GUAC** → **#8 / #14 (radar/model)** |
| Attack-path derivation | MulVAL, Bayesian attack graphs | Attack step/path in ARCH-0001 §3 | adopt derivation + likelihood → **#17 / metrics #14** |
| AI grounding | GraphRAG, RoG, ToG | "AI proposes, human reviews" stated | RoG/ToG mechanism → **DEC-006 / #10** |
| Federation | OKN FRINK, federated SPARQL | none | evaluate joining OKN → **new decision** |
| Visualization | STIX visualizer, graph UIs | planned (#10) | reuse STIX-viz prior art → **#10** |

## 7. Open questions / next

- **RDF vs LPG** — take DEC-002/DEC-004 with this evidence (lean RDF).
- **Adopt STIX 2.1 as the interchange/graph schema?** (strong candidate) → #9/#17.
- **Federate tmodel into NSF OKN?** national-security + supply-chain fit → propose a decision.
- Promote the remaining `sources.md` references to full library records as the team works them (per #5); line-by-line review of applicability ratings.
