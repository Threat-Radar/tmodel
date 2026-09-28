---
schema: "archdoc/v1"
id: RPT-0011-sources
title: "RPT-0011 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
record: RPT-0011
---

# RPT-0011 — source log

Sources gathered for this report. **Held** = a `library/` record exists
(Threat-Radar/library PR #4). **Frontier** = verified and logged here, to be
promoted to a record as the team works it (per #5). A source is not "in the report"
until it is at least logged here.

## Held (library records)

| record id | source |
|---|---|
| `nsf-23-571` | NSF 23-571 Proto-OKN solicitation |
| `nsf-okn-launch` | NSF OKN launch (okn.us) |
| `okn-roadmap-2022` | OKN Roadmap (NSF/OSTP 2022) |
| `frink-fabric` | FRINK — OKN fabric/federation (RENCI) |
| `securechain-okn` | SecureChain — software supply-chain KG (Purdue) |
| `sudokn-okn` | SUDOKN — manufacturing supply/demand KG (ASU) |
| `mcp-okn` | MCP access to OKN graphs |
| `rdf-1-1-concepts` | RDF 1.1 Concepts (W3C) |
| `owl-2-primer` | OWL 2 Primer (W3C) |
| `sparql-1-1` | SPARQL 1.1 (W3C) |
| `shacl` | SHACL (W3C) |
| `prov-o` | PROV-O (W3C) |
| `linkml` | LinkML |
| `hogan-kg-survey` | Knowledge Graphs survey (Hogan et al., 2021) |
| `stix-2-1` | STIX 2.1 (OASIS) |
| `mitre-attack` | MITRE ATT&CK |
| `cwe` | MITRE CWE |
| `capec` | MITRE CAPEC |
| `d3fend` | MITRE D3FEND (OWL KG) |
| `cve-json-5` | CVE JSON Record Format v5 |
| `osv-schema` | OSV Schema (OpenSSF) |
| `bron` | BRON — ATT&CK↔CAPEC↔CWE↔CVE↔CPE |
| `guac` | GUAC — supply-chain graph (OpenSSF) |
| `spdx-3-rdf` | SPDX 3.0 RDF model |
| `mulval` | MulVAL attack-path analyzer |
| `graphrag-ms` | GraphRAG (Microsoft) |
| `unifying-llm-kg` | Unifying LLMs and KGs: a roadmap |
| `first-cvss` | CVSS (FIRST) — already held (from ISO 21434) |

## Frontier (verified, not yet recorded)

- **NSF OKN:** okn.us registry (registry.okn.us / frink.renci.org/okn), NSF Convergence Accelerator Track A (KnowWhereGraph, Biomedical OKN, SCALES), the remaining Proto-OKN Theme-1 teams (SPOKE, SAWGraph, WEN-OKN, DREAM-KG, IJP, RURAL-KG, …).
- **Standards:** TAXII 2.1, R2RML/RML, JSON-LD 1.1, ISO/IEC 39075 GQL, Wikidata, schema.org, KG-refinement (Paulheim 2017; CleanGraph 2024).
- **Cyber KGs:** CVSS v4.0 spec, NVD API 2.0, CycloneDX, deps.dev, SLSA, CISA SBOM, cti-python-stix2 / stix-visualization, Attack Flow (CTID), cybersecurity-KG surveys (Sikos 2023; Zhao 2024), CWE↔CVE↔CPE inference (Shi 2023), CAPG (Poisson 2023).
- **Attack graphs:** Sheyner 2002, Ammann 2002 (monotonicity), Swiler 1998, Bayesian attack graphs (Poolsappasit 2012), MulVAL-extensions survey (2022), graph-models survey (Wachter 2023).
- **AI grounding:** RAG (Lewis 2020), Reasoning-on-Graphs (RoG), Think-on-Graph (ToG), CTI-GraphRAG preprints (2026).

**Rule:** a frontier source informing a `DEC-*`/`R-*` should be promoted to a record before it is cited normatively. Flags (unverified attributions, paywalled DOIs, 2026 preprints) are in `searches.md`.
