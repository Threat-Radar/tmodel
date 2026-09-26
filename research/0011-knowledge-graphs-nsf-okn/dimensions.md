---
schema: "archdoc/v1"
id: RPT-0011-dimensions
title: "RPT-0011 dimensions — the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
record: RPT-0011
---

# RPT-0011 — search dimensions

Four lanes (one multi-agent research pass each). Every source → a `library/`
record; the report summarizes, compares, and rates applicability to the tmodel
threat-modeling KG on: **object model · provenance/attribution · human-review/audit ·
federation · AI grounding.**

## 1. NSF OKN
okn.us / launch; NSF 23-571 solicitation; OKN Roadmap (2022); the 18 Proto-OKN
teams; the **FRINK fabric** / federation; governance & provenance; the
semiconductor supply-chain cross-graph example (SecureChain, SUDOKN); LLM↔OKN
bridges (mcp-okn).

## 2. KG foundations & standards
RDF/RDFS/OWL; SPARQL; **SHACL**; RML/R2RML; JSON-LD; property graphs
(LPG/openCypher/**GQL**); **PROV-O**; **LinkML**; Wikidata; schema.org; KG
refinement / human-in-the-loop.

## 3. KG for cybersecurity / threat modeling
STIX/TAXII; MITRE ATT&CK/CWE/CAPEC/**D3FEND** as graph/linked data; vulnerability
KGs (CVE/NVD/OSV/CVSS); **BRON**; supply-chain KGs (**GUAC**, SBOM/CycloneDX/SPDX-RDF,
deps.dev, SLSA); attack-graph research (MulVAL, Bayesian attack graphs, surveys).

## 4. Grounding AI with KGs
RAG → **GraphRAG**; LLM+KG roadmap (synergized pattern); **RoG** / **ToG**
(constrained, traceable, human-correctable reasoning); CTI-specific GraphRAG.

---
**Applicability rubric (per source):** rate core / adjacent / none on each of the
five axes above; a source that informs none is recorded with a reason, not dropped.
