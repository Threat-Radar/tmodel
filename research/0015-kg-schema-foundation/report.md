---
schema: "archdoc/v1"
id: RPT-0015
title: "Knowledge-graph schema foundation — Stage 1 (SOTA, schema language, extraction/vector method)"
short_title: "KG schema foundation (Stage 1)"
description: "Stage 1 of #104: ingest KG state-of-the-art (incl. Google's actual current KG surface), determine the schema-definition language (LinkML + validation layers), and set the per-object schema standard + extraction/vector methodology. Evidence + a decision-direction for Stage 2; accepts no DEC."
type: research
category: knowledge-graph
status: draft
version: "0.1.0"
date: "2026-10-05"
updated: "2026-10-05"
authors:
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: sponsor
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0015-kg-schema-foundation/report.md
defers_to: ARCH-0001
agent_notes: >
  Stage 1 of the 3-stage KG-schema foundation (#104), from three verified-source research
  lanes. Sets the Stage-2 authoring standard (LinkML + the per-object checklist + the gap
  list) and the Stage-3 vector methodology. Proposes a direction for DEC-002 (schema-IDL
  half); accepts nothing (ADR-only). Unverified items are flagged, not pretended.
---

# RPT-0015 — KG schema foundation, Stage 1

**The premise (sponsor):** a list of ~23 classes with mostly `range: string` slots
(`spec/schema/tmodel-object-model.linkml.yaml`) is an **object inventory, not a schema**.
Stage 1 ingests the state of the art, fixes the **schema-definition language**, and defines
**what a proper per-object schema must contain** — the standard Stage 2 authors to. Evidence,
not a decision.

## 0. Summary

- **Schema language → LinkML** (authoring IDL), with **JSON Schema + SHACL** generated for
  validation (+ **hand-written SHACL-SPARQL** for the one constraint codegen can't emit — the
  Assertion acceptance gate), and **RDF-star** + a **custom LinkML→LPG adapter** as the
  substrate lowerings DEC-004 leaves open. LinkML's only real gap is LPG (no native generator)
  — already ADR-0004's edge-façade work (#52).
- **KG approach holds, with improvements:** git files stay canonical and the working store is a
  **rebuildable cache** (reinforced by the Kuzu collapse, below); **schema-guided extraction**
  (constrain the LLM with the LinkML schema) + **grounding** + **quote-grounding** + a
  **validation gate**; a **vector index beside** the graph; expose read-only via a **small local
  MCP**. No substrate change forced; a mild industry tilt to LPG/GQL argues for keeping DEC-004 open.
- **The current draft schema has structural defects** (§4) that Stage 2 must fix — including a
  **feasibility contradiction** (Common-Criteria text vs ISO-21434 enum — the dropped ADR-0005
  ghost), **no `Requirement` class**, `risk` as a free string, an **Assertion with no provenance
  slots**, and pervasive missing patterns/cardinality/enums/rules.

## 1. KG state of the art — deltas since RPT-0011, and improvements

- **"Google next-gen KG" is not a real thing to chase.** No verified 2025–26 "Google KG v2".
  Google's actual current surface: **Data Commons exposed to agents over MCP** (Sept 2025;
  hosted Feb 2026), **Spanner Graph** (ISO GQL + vector/ScaNN for GraphRAG, *cloud-only*), and
  Gemini graph extensions. **Borrow the pattern** (governed KG → agents via a small **local**
  MCP), not the product; do not adopt Spanner (cloud breaks local-first/private-data).
- **Embedded-graph risk (new).** Kuzu (the "DuckDB for graphs") was acqui-hired by Apple and
  **archived** (Oct 2025); successors are immature. → **Never let the embedded store hold
  canonical data; make the load deterministic; the store is a rebuildable cache** (reinforces
  ADR-0004). Candidates to *evaluate later, not commit*: DuckDB + DuckPGQ, or oxigraph (RDF).
- **Schema-guided extraction is the trend** (ontology/schema-constrained LLM extraction, e.g.
  OMD-GraphRAG) — reinforces using the LinkML schema as the **extraction target**.
- **Hybrid vector+graph retrieval** is now the default production RAG pattern (vector for entry,
  typed-edge traversal after) — add a vector index **beside** the graph, regenerated from git.
- **Graph standards maturing:** **RDF 1.2 Concepts at W3C Candidate Recommendation (2026-04)**;
  **SHACL 1.2/SHACL-star still First Public Working Draft (pre-stable)**; **ISO GQL (39075:2024)**
  defines property-graph "graph types" (the target if DEC-004 picks LPG). SQL/PGQ is query-only.

## 2. Schema-definition language — LinkML (proposes DEC-002's IDL half)

| layer | choice | role |
|---|---|---|
| **Authoring IDL (SoT)** | **LinkML** (`spec/schema/`) | the one schema source; §13 + ADR-0004 already assume it |
| Validation (files) | **JSON Schema** (`gen-json-schema`) | validate file-SoT YAML/JSON in CI |
| Validation (RDF) | **SHACL** (`gen-shacl`) + **hand-written SHACL-SPARQL** | structural shapes + the §4 acceptance gate codegen can't emit |
| RDF lowering | **RDF 1.2 / RDF-star + SHACL-star** | edge-reification lowering of `Assertion` |
| LPG lowering | **custom LinkML→GQL/openCypher adapter** | LinkML's gap; = ADR-0004 edge façade (#52) |

**Why LinkML:** it natively expresses everything a real schema needs — `range` (scalar/class/
enum), `required`, `multivalued` + explicit `minimum_cardinality`/`maximum_cardinality`,
`permissible_values`, `pattern`/`structured_pattern`, `ifabsent` (defaults), value bounds,
`unique_keys`, `is_a`/`mixins`, and class-level `rules` for cross-field invariants. **The draft
uses almost none of these — the language is not the limitation, the draft is.** It generates the
validation/code targets (JSON-Schema, SHACL, OWL, Pydantic for the Path-A Python engine) and
`linkml-validate` checks instances. **Honest limits (into the ADR):** no native LPG generator
(custom adapter needed); `gen-shacl` is structural only (gate is hand-written); import from
CWE/CAPEC/STIX/OTM is bootstrap+curation, not round-trip (stays the DEC-002/#9 mapping layer);
choosing LinkML decides **only** DEC-002's schema-language half, not DEC-004 (substrate).

Rejected as the *primary* IDL (with their real roles): **SHACL** (validation layer, not an
authoring IDL), **OWL** (open-world inference, wrong for required-field checks; keep as a generated
mapping/alignment target), **JSON Schema** (generated file validator; no identity/graph model),
**ISO GQL/SQL-PGQ** (describes a running LPG store, not files/RDF; the LPG-adapter target),
**RDF-star** (a data model, the RDF lowering), **schema.org** (too soft — reject).

## 3. What "a proper schema" must specify — the Stage-2 standard

**Per class:** stable-id slot + **id scheme/`pattern`**; `is_a`/`mixins` + `class_uri`/`mappings`
to the external vocab it realizes (PROV-O/STIX/CWE/CAPEC); description + ARCH §-anchor + the
DEC/requirement it traces to + worked `examples`; `unique_keys` beyond id; **class-level rules**
(cross-field invariants); node-vs-reified-edge declaration + which relational roles are **edges**;
MVP/post-MVP + normative/draft marker.

**Per slot:** name + § anchor; **range/type** (scalar incl. `uri`/`curie`, class, or enum);
**required**; **multivalued + explicit cardinality**; **closed enum** where the vocab is
controlled (state open/closed); **pattern/format** for id strings (`CVE-\d{4}-\d+`, `CWE-\d+`,
`CAPEC-\d+`, CPE/purl, IRI); **default** (`ifabsent`); inlined-vs-referenced for object-valued
slots; **value constraints**; **edge metadata** (inverse/cardinality/predicate IRI, whether it
reifies to `Assertion` when reviewed); **epistemic stance** (human-input / AI-proposed / derived;
can it carry Assertion+Review?); **external mapping** (`slot_uri`); **scale/units** for ordinals
(feasibility, confidence, severity); definition provenance.

## 4. Gap list — Stage-2 work on the current draft

**Four structural problems to settle first:**
1. **No `Requirement` class** — yet it's a core object (ISO 21434 FX-1 already supplies its fields;
   MAP-0001 needs it). Add a thin `Requirement` class.
2. **Feasibility contradiction** — `AttackPath`/`RiskScore` descriptions say Common Criteria
   (dropped **ADR-0005** ghost) while `feasibility`/`FeasibilityLevel` say ISO 21434 Table-1.
   **Resolve to ISO 21434 Table-1** (method); CC is display-only (per the merged proposal §3).
3. **`risk` is a free string** (M(I,F) unfixed) → RiskScore vectors are "structure-only" until
   DEC-003 fixes the aggregation.
4. **Assertion acceptance gate not expressible in LinkML** → a hand-written SHACL-SPARQL or Python
   checker, separate from the schema.

**Systemic (nearly every class):** no `pattern`s; no cardinality beyond required/multivalued; no
`ifabsent` defaults; **free-string slots that must be enums** (`review_status`, `priority`,
`confidence`, `assertion_status`, `source_method`, `violates_property`, `classifications`, the
three `Environment` facets); no class-level `rules` (the Assertion gate, `valid_to>=valid_from`,
derived-`risk`); no `unique_keys`; declared `stix:`/`prov:` prefixes **unused** (no mappings); no
edge/inverse/reification metadata.

**Worst-specified classes:** **DamageScenario** (`slots: []`, empty but referenced);
**Assertion** (the provenance spine has **no provenance slots** — no generating Activity/agent/
timestamp; `confidence` unscaled); **Review** (`review_status` free, undermines the gate);
**ThreatInstance** (no `targets`/`on_element` edge despite STRIDE-on-DFD-target); **Mitigation**
(missing `kind ∈ {technical,documentation,process}` R-040; no effectiveness/evidence);
**RiskScore** (doesn't model the per-(scenario,category,stakeholder) multiplicity); **Party**
(the "one identity, many facets" claim unschematized; no canonical-org-id for dedup).

**Absent classes (stub or explicitly scope out):** the DFD behavioral layer (Process/DataStore/
DataFlow/ExternalEntity + `realized_by` — where STRIDE attaches), TrustBoundary/AttackSurface/
Network, **Asset** (the real `owned_by` target), ProductFamily, PROV Activity/Agent, and the
iteration-8 SDL objects (SDL/Gate/Requirement/WorkProduct/GovernedView — post-MVP).

**Keep as the quality bar:** `LifecyclePhase*`, `ImpactVector` (S/F/O/P each an `ImpactSeverity`
enum), and the `PartyKind`/`MethodFacet`/`AttackGate`/`FeasibilityLevel`/`MitigationStatus`/
`RedundancyRelation`/`ViewProjection` enums — these show the target quality the rest must meet.

## 5. Extraction + vector methodology (Stage-3 input)

- **Schema-constrained extraction** (SPIRES/OntoGPT pattern, LinkML as the target) + **grounding**
  — resolve `catalog_ref` (CWE-79, CAPEC-63, CVE-…, D3FEND) against the **library record**; never
  accept an LLM-minted catalog id. **Quote-grounding:** the extractor returns the exact source span,
  checked verbatim against the source (fits FX-1). Every extracted fact → an `Assertion` with a PROV
  Activity (model id, prompt hash, source digest, locator, quote) + a separate `Review`; accept only
  after the gate.
- **Validation:** `linkml-validate --target-class X` pass/fail is the per-vector check; wire into CI.
- **Vectors = conformance triples per class:** ≥1 valid, ≥1 invalid (missing-required / bad-enum /
  bad-id-pattern / dangling-ref / rule-violation e.g. accepted-without-review), ≥1 boundary; plus
  **round-trip** (serialize→load→revalidate) and an optional **Layer-B** extraction regression
  (source-span → expected instance, field-level scored, non-gating). Track **per-class coverage**.
- **Prerequisite:** CWE/CAPEC/D3FEND/ATT&CK are only `summarized` — **FX-1-distill them first** so
  vectors can cite `record#locator` (as ISO 21434 already does). Build **one connected scenario**
  (a CWE → its CAPEC → a mitigating D3FEND → a CVE instance → one AttackPath+RiskScore) to cover
  §8 vectors 1–6.
- **Per-object reference** (extract each from): Weakness←CWE, Vulnerability←CVE(JSON-5),
  AttackPattern←CAPEC/ATT&CK, AttackStep←ATT&CK chain/attack-tree (AND+OR), AttackPath←ATT&CK
  tactic chain, ThreatInstance←a worked STRIDE-on-DFD example, DamageScenario←ISO 21434 TARA,
  Mitigation←D3FEND, RiskScore←ISO 21434 TARA worked example (structure-only), Requirement←ISO
  21434 clause (already distilled; SSDF once ingested), Review/Assertion←a CWE↔CAPEC mapping.

## 6. Sources & unverified flags

Verified this session (search/fetch): LinkML generator catalog (no LPG target) + framework papers
(GigaScience 2025; arXiv 2511.16935); RDF 1.2 at W3C CR 2026-04; SHACL 1.2 FPWD 2025; ISO GQL
39075:2024 graph types; Google Data Commons MCP (2025–26), Spanner Graph; GraphRAG surveys (ACM
10.1145/3777378; arXiv 2501.13958, 2507.03226); ontology-guided extraction (arXiv 2603.25152,
2511.05991); SPIRES/OntoGPT (arXiv 2304.02711); OntoLogX (arXiv 2510.01409); `linkml-validate` docs.
**Unverified (flagged, verify before the DEC-002/004 ADR):** most claims are from search snippets
not full-text; `schema-automator` import behavior; LinkML advanced-constraint syntax at the pinned
version; CWE/CAPEC/ATT&CK/D3FEND current version numbers; that the library holds a worked ISO 21434
TARA example. **Gather an RDF-star library record** (RDF 1.2 is now real/CR) before the ADR.

## 7. Next (Stage 2 / Stage 3)

**Stage 2:** adopt LinkML (propose via the DEC-002 ADR when ready), then author **proper per-object
schemas** to the §3 standard, fixing the §4 gaps (MVP-core classes first), and **review each against
its requirements**. **Stage 3:** build the per-object extraction vectors (§5), distilling CWE/CAPEC/
D3FEND/ATT&CK first. Both run multi-agent with an adversarial review at the gate.
