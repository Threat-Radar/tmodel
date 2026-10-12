---
schema: "archdoc/v1"
id: RPT-0016
title: "Requirements synthesis: testable features and capabilities from the research reports"
short_title: "Requirements synthesis"
description: "A concise, deduped set of testable features, capabilities, and requirements mined from the thirteen research reports (RPT-0001..0015), each tagged MVP / post-MVP / aspiration and mapped to an existing R-/A-/T- or flagged NEW, plus a gap analysis against the ratified docs and the decisions it implicates. Synthesis, not new decisions."
type: research
category: security
status: draft
version: "0.2.0"
date: "2026-10-12"
updated: "2026-10-12"
authors:
    - role: synthesis
      id: nymble
decision_makers:
    - role: sponsor
      id: nymble
reviewers:
    - role: adversarial-critic
      id: claude
needs_review: false
reviewed: true
canonical_path: research/0016-requirements-synthesis/report.md
defers_to: ARCH-0001
---

# RPT-0016 — Requirements synthesis

## Abstract

A six-cluster, multi-agent sweep of the thirteen research reports (RPT-0001…0015;
0008 and 0010 are unused) mined every *testable* feature, capability, and requirement they
imply, deduped across clusters, and mapped each to an existing requirement (`R-` in
ARCH-0001 §4, `A-` in APP-0001, `T-` in BACKLOG-0001) or flagged it **NEW**. This report is
**synthesis, not decision**: it proposes nothing accepted, and routes DEC-gated items to
their decision. It was adversarially reviewed (v0.2.0 folds that review); it is applied to
the docs in a **follow-up PR** (this PR touches no `R-`/`A-`/`T-`).

**Accepted decisions as of 2026-10-12 (the baseline this synthesis reconciles against).**
DEC-005 (ADR-0002 MVP), DEC-006+DEC-010 (ADR-0003/0009 stack), DEC-007 (ADR-0001 radar/tmodel
split), DEC-011 (ADR-0004 storage), DEC-002 (ADR-0007 LinkML IDL + import **OTM/STIX 2.1** only /
export JSON-LD/Turtle/GraphML/CSV), DEC-003 (ADR-0006 composite risk vector), DEC-004 (ADR-0008
Oxigraph), and **DEC-001a (ADR-0010) — the CORE attack-path type system is ACCEPTED** (incl.
AND/OR attack structure, shared-step graph, vuln propagation, the reified `Assertion` spine, and
the human-reviewed-vs-AI-proposed distinction). **Still open:** DEC-001b (governed/program layer +
the §13 integrity gate), DEC-008 (CWE/NVD), DEC-009 (threat→product / lifecycle). Items below are
positioned against this baseline — several "gaps" are a *lag of the ARCH §4 requirement text*
behind an already-accepted ADR, not an open decision.

**Coverage caveat.** RPT-0001 (landscape), RPT-0005 (schema-reps), and RPT-0012
(gui/platform) are still `pending` skeletons; they yielded little beyond their §0/crosswalk.
The substance comes from RPT-0002/0003 (frameworks/products), 0004 (composition),
0006 (visualization), 0007 (ISO 21434 TARA), 0009/0014 (AI threats), 0011/0013/0015
(KG/SDL/schema).

**Classification.** MVP = the Nov-5 attack-path graph (ADR-0002). post-MVP = in scope,
later. aspiration = product-direction / later-scope (per the sponsor, most of 0004's
product-composition depth and most AI vocabulary sit here). Candidate ids are **SR-NN**
(synthesis requirement) — provisional until promoted.

## 1. Consolidated requirements by theme

Columns: **id · statement (testable) · acceptance · class · source · maps_to · target**.

### 1.1 Attack structure & path analysis (the MVP spine)

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-A1 | Model attacks as AND/OR decomposition with explicit step ordering | A fixture tree enumerates minimal attack sets; an ordering cycle is rejected; same steps in different order are distinct | MVP | 0002 | **DEC-001a accepted (ADR-0010)**; §4 text lags (R-031 in proposal) | ARCH §4 **reconcile text** |
| SR-A2 | Attack structure is a graph: one AttackStep is shared across paths/threats, not duplicated | Two paths sharing a step reference one node with two incoming edges | MVP | 0002/0003 | **DEC-001a accepted**; R-001/R-031 text | ARCH §4 reconcile |
| SR-A3 | An AttackStep carries a technique id (ATT&CK/CAPEC) separate from an ordered kill-chain phase | `technique=T1566.001, phase=Delivery`; lookup by technique resolves; phase is order, tactic is a tag | MVP | 0002 | NEW (slot on the DEC-001a AttackStep) | ARCH §4 |
| SR-A4 | Path analysis: return the easiest/cheapest path and the mitigation that blocks the most paths | On a fixture, the ranked-mitigation query returns the shared-step cut first; easiest path matches a hand computation | MVP | 0002 | NEW (query capability; *not* R-021, which is mitigation-lifecycle) | ARCH §4 / APP |
| SR-A5 | A `realizes` edge links each AttackPath to the threat scenario(s) it realizes (many-to-many) | Path→threat edge exists; a threat aggregates feasibility (worst path) over its paths; a path with 0 threats is flagged | MVP | 0007 | NEW edge — **HOLD: fold via the DEC-001 schema vehicle** (ADR-0010 closed the core type system), not a bare §4 R- | ARCH §3 schema (proposal diff) |

### 1.2 Composition & identity

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-C1 | Ingest a component with several typed identifiers at once (purl, CPE, hashes, SWID) | Each identifier is queryable by kind; A-001 names only CPE/purl today | MVP | 0004 | A-001 (extend) | APP |
| SR-C2 | Grade identity: computed-from-bytes (hash/SWHID) vs assigned (purl/CPE); flag heuristic CPEs low-confidence | A hash-bearing component shows "verifiable"; a Syft-generated CPE carries a low-confidence flag | post-MVP | 0004 | NEW | ARCH §4 |
| SR-C3 | Accept CycloneDX composition arriving via the **radar→tmodel contract** (SBOM ingestion lives in radar per ADR-0001; tmodel consumes radar output — see SR-C7), not a direct SBOM importer in tmodel | A radar-delivered CycloneDX-derived composition loads; dependency edges become typed edges | MVP (via radar) | 0004 | R-002 (radar output); direct-SBOM import would be a **DEC-002 extension beyond ADR-0007's OTM/STIX set** | ARCH §4 |
| SR-C4 | Keep relationship kinds distinct: depends-on, contains/assembly, provides, lifecycle scope | A contains edge and a depends-on edge between the same pair are separate, filterable | MVP | 0004 | R-001 (edge vocab) | ARCH §4 |
| SR-C5 | Distinguish none / unknown / unspecified for dependencies; carry a completeness level | Empty `dependsOn` = "known none"; absent = "unknown"; path analysis through an incomplete node marks results "possibly incomplete" | post-MVP (high correctness) | 0004 | NEW | ARCH §4 |
| SR-C6 | Separate SBOM-document id, product identity, and build record; pin product version to a content digest | Two SBOMs of one build map to one Product version; an unpinned product triggers a warning | MVP | 0004 | R-022 | ARCH §4 |
| SR-C7 | The radar→tmodel contract carries purl/CPE/deps/CWE/hashes/supplier **and includes non-vulnerable components** (the "non-vulnerable" clause is this report's synthesis inference; the 16-vs-4 counts are RPT-0004 facts) | A radar output ingests with all fields on nodes; all 16 Alpine packages become Components, not just the 4 with matches | MVP | 0004 | R-002/A-001/ADR-0001 | APP / ARCH |
| SR-C8 | Record match provenance & confidence (matcher, namespace, fix-state, CVE aliases) | A Grype CPE match stores "cpe-match, needs verification"; a GHSA match "high confidence"; fix state queryable | MVP | 0004 | A-002 | APP |
| SR-C9 | Model hardware/firmware as first-class instances; (aspiration) HBOM supply-chain attributes + queries | A device+firmware stores two linked components; a firmware vuln traces to the device; (asp.) a single-source/flagged-country query returns parts | MVP (hw one-deep) / aspiration (supply-chain) | 0004 | R-022 | ARCH §4 |
| SR-C10 | Import VEX; map CycloneDX/SPDX states to one status set; a VEX justification is a reviewable proposal, not final | A `not_affected` flips a finding with provenance and stays a proposal until a Review | post-MVP | 0004 | NEW · **DEC-002** | ARCH §4 |

### 1.3 Risk & TARA

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-R1 | Record DamageScenario + assets with cybersecurity properties (C/I/A); a ThreatScenario names asset + property + cause | An asset with no property fails validation; a threat missing asset/property/cause is flagged | MVP | 0007 | R-001 (extend) + NEW (cause) | ARCH §3/§4 |
| SR-R2 | Human sets impact per damage-scenario, per S/F/O/P category, 4 levels, with a skip rationale | One rating per category; safety flagged ISO 26262-sourced; a skipped category requires a rationale | MVP | 0007 | R-019 · DEC-003 | ARCH §6 |
| SR-R3 | Human rates path feasibility (4 levels) and records the rating **method** + inputs | Rating stored with a `method` field; (post-MVP) a calculator reproduces Annex-H bands | MVP (field) / post-MVP (calc) | 0007 | A-005/R-012/R-013 | ARCH §6 |
| SR-R4 | Document and test the risk **combiner** (DEC-003 residue) | A unit test pins the rule; ISO 21434's own Annex-H example *matrix* vs example *formula* disagree on 4 of 16 cells, and integer-vs-fraction/rounding is unstated — resolve and document (ADR-0006 pins only range 1–5 + worst-path fold) | documentation/test item (I4, Nov 6–19); prerequisite to *showing* a derived Risk number | 0007 | DEC-003 accepted; ADR-0006 follow-up | ARCH §6 |
| SR-R5 | Record a treatment decision {avoid, reduce, share, retain}; share/retain need a rationale (claim) | Decision accepts all four; share/retain without rationale fails; reduce links ≥1 mitigation | post-MVP | 0007 | R-021 · DEC-009 | ARCH §6 |
| SR-R6 | Re-assessment triggers: a new finding / changed asset / reuse change flags linked threats "needs-reassessment" | Importing a finding marks linked threats stale | post-MVP | 0007 | R-021 · DEC-009 | ARCH §7 |
| SR-R7 | ISO 21434 Annex-H headlamp example as a regression fixture (own words, licensed-text posture) | Load the fixture; computed feasibility/risk/decisions match the published outputs | MVP | 0007 | R-005 / vector | spec/vectors |
| SR-R8 | Decide weakness-vs-vulnerability: a weakness is a vulnerability only if an attack path can exploit it | A weakness with no path requires a rationale to stay "not a vulnerability" | post-MVP | 0007 | R-010 | ARCH §4 |

### 1.4 SDL, conformance, governed layer — **DEC-001b** (held) / post-MVP, **except SR-S1** (`Mitigation.kind`, MVP-adjacent, R-040/T-220 — not part of the governed layer)

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-S1 | `Mitigation.kind ∈ {technical, documentation, process}` | Field validates; query by kind | MVP-adjacent | 0013 | R-040 / T-220 | ARCH §4 |
| SR-S2 | SecurityProgram with ordered, named, dated Gates/Checkpoints/Milestones + entry/exit criteria + owner | A gate isn't "passed" until criteria met; planned-vs-actual dates queryable | post-MVP | 0013 | R-041 · DEC-001b | ARCH §3c |
| SR-S3 | Requirement object with cross-spec `maps_to` (MAP-0001: 34 req × 16 frameworks) | "Which frameworks require threat modeling?" returns per-framework edges; `spec/MAP-0001.yaml` validates | post-MVP | 0013 | R-044 · DEC-001b | ARCH §3c |
| SR-S4 | Automated, CI-runnable "threats-mitigated" conformance check (linkage + approval, **not adequacy**) | Each failing condition (undisposed threat, mitigation below approved, missing/stale/mismatched evidence, dangling id) emits a distinct error | post-MVP | 0013 | R-042 / A-061 | ARCH §3c |
| SR-S5 | Evidence/WorkProduct records with freshness + digest matching, attached to mitigations | A mismatched-digest or stale evidence record fails SR-S4 | post-MVP | 0013 | NEW · T-084 | ARCH §3c |
| SR-S6 | Governed document-views: owner(role)/version/status/change-history/approval bound to a KG snapshot digest | Governance metadata is stamped from the snapshot; a hand-edit to a rendered view is flagged | aspiration | 0013 | R-043 | ARCH §3c |

### 1.5 Schema quality, provenance, grounding & extraction

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-Q1 | CI validates every instance against the JSON-Schema generated from LinkML | A negative-vector set is rejected; a clean set passes | MVP | 0015 | NEW (A-061 partial) | ARCH §4 |
| SR-Q2 | A substrate-neutral integrity checker (separate from `linkml-validate`) catches cross-instance violations | accepted-without-review / dangling-ref / `valid_to<valid_from` / edge-vs-Assertion divergence each fail the checker but pass linkml-validate alone | post-MVP (**DEC-001b-held** — this *is* ADR-0010's §13 integrity gate, M1) | 0015/0011 | DEC-001b §13 gate | BACKLOG task |
| SR-Q3 | Mechanized review gate: no machine-proposed element reaches `accepted` without a Review; violation names the node | Create an AI Assertion with no Review → gate returns a violation; add a Review → passes | principle=MVP (ratified R-018); mechanization=post-MVP | 0015/0011 | R-018 (principle, ratified) + DEC-001b (gate, with SR-Q2) | ARCH §4 (principle) / BACKLOG (gate) |
| SR-Q4 | Each class has valid/invalid/boundary conformance vectors + a serialize→load round-trip; coverage is reported | A coverage report lists classes with <3 vectors; CI fails below threshold; canonical YAML round-trips byte-stable | MVP | 0015 | R-005 + NEW (T-100) | BACKLOG |
| SR-Q5 | Provenance model: an Assertion carries a PROV activity (model id, prompt hash, source digest, locator, quote, agent, timestamp) | "Who/what generated this, from which source, when" returns all fields; a fact missing them fails | MVP (core) / post-MVP (full) | 0015/0011 | R-018/A-045 | ARCH §4 |
| SR-Q6 | Retrieve an element's derivation chain back to a library record | The provenance view lists upstream sources/agents; `wasDerivedFrom` ends at a library record | MVP (inspect) | 0011 | A-022 | APP |
| SR-Q7 | Grounding: reject invented catalog ids; quote-grounding checks the span appears verbatim in source | "CWE-99999999" is rejected and creates no node; an altered quote is rejected | MVP | 0015 | R-010 (extend) / T-029 | ARCH §4 |
| SR-Q8 | Schema-constrained extraction: LLM output that fails schema validation never enters the graph | Extraction on a fixture either validates or is rejected with an error | MVP | 0015 | NEW | ARCH §4 |
| SR-Q9 | Governance lint: a committed file never cites a non-accepted ADR as accepted | A header citing "ADR-NNNN accepted" for a non-accepted ADR fails the lint | MVP | 0015 | NEW | BACKLOG |
| SR-Q10 | Read-only local MCP/CLI query over the governed graph; every returned fact carries its review status | An MCP call returns a node with `review_status`; a write is rejected; no network call | post-MVP | 0015/0011 | A-030/A-062 (not T-205, which is Slice-5 packaging) | APP |
| SR-Q11 | A `MAP-NNNN` crosswalk per imported format; each class maps to an external `class_uri` or is flagged "local extension" | A class with neither fails a crosswalk test | MVP (OTM/STIX) / post-MVP (rest) | 0005/0015 | R-005 · **DEC-002** | ARCH §5 |
| SR-Q12 | Export Reviews as STIX Opinion/Note (and import them back) | Exported bundle validates STIX 2.1 and round-trips the reviewer reference | post-MVP | 0011 | R-006 · **DEC-002** | ARCH §4 |
| SR-Q13 | Define what "round-trip" means **per format** (R-005 "round-trip proven" vs imports-not-round-trip) | Each import/export vector reports exactly which fields are lossy | **decision** | 0015 | R-005 · **DEC-002** | ARCH §5 |

### 1.6 UI / display / platform

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-U1 | Presentation actions (filter/hide/focus/pan/zoom/drag/layout) never mutate the domain; a verdict is only an explicit action | After a filter/hide/layout/drag sequence, the SoT git diff is empty; no verdict is logged | MVP | 0006 | ARCH §10 (never-written-back); not A-045 | APP |
| SR-U2 | Show review state with a redundant non-colour cue (label/badge/glyph) | Under grayscale/colour-blind simulation all 5 states are distinguishable | MVP | 0006 | A-007/A-021 (extend) | APP |
| SR-U3 | **Define numeric interaction budgets** (RPT-0006 requires measurable targets and gives none; A-042 is only "no jank") | Budgets exist and are tested. *Specific numbers are TBD, set by the SR-U4 benchmark* — illustrative only: fps during pan/zoom/drag, expand/filter latency, time-to-first-render. The at-A-041-scale "best-in-class" bar is A-042 (post-MVP). | MVP (define budgets) / post-MVP (A-041-scale targets) | 0006 | A-027/A-041/A-042 (make measurable; numbers TBD) | APP |
| SR-U4 | A benchmark harness that gates the A-044 viz-library pick | CI/script reports fps/memory/layout-time across a scale sweep up to A-041 (RPT-0006 ran only 300 nodes; it sets no target) | MVP | 0006 | A-044/T-204 | BACKLOG |
| SR-U5 | **Accessibility**: non-colour cues for review state (MVP); keyboard review loop, visible focus, reduced-motion, screen-reader alt (post-MVP) | MVP: review state readable in grayscale. post-MVP: core review loop completable by keyboard; reduced-motion disables physics | MVP (non-colour cue only) / post-MVP (rest) | 0006 | NEW (RPT-0006: a11y untested, a "candidate need") | APP |
| SR-U6 | Proposal-vs-accepted diff before a verdict + an audit entry (actor/time/base-rev/rationale/before-after) | A verdict can't be recorded until the diff renders; the verdict appears in the audit log with all fields | MVP | 0006 | A-004 (extend) | APP |
| SR-U7 | Attack-path view: primary highlighted; alternates + mitigation-interrupt points subdued-not-deleted; steps inspectable; paths carry an origin label (computed/curated/AI) | A 7-edge primary + 2-edge alternate render with the primary emphasised, alternate dimmed; prominence never styles a node "accepted" | MVP | 0006 | A-005 (extend) | APP |
| SR-U8 | Focus-view honesty: a "showing N of M" indicator, dim-not-delete, search by name/id, reset/fit/back | A focused view shows the subset indicator and a hidden-neighbour count; search focuses/loads an unloaded node | MVP | 0006 | A-023 (extend) + NEW (search) | APP |
| SR-U9 | Stable/incremental layout with pinning and a **measurable** stability criterion | After expand, pinned nodes move 0 px; unpinned existing nodes move ≤ X px (threshold TBD) | MVP (pin + stable-on-expand) | 0006 | A-020 (make measurable) | APP |
| SR-U10 | A viz adapter: the domain `type` field must not collide with renderer-reserved attrs; renderer swappable behind the adapter + licence filter | A fixture with a semantic `type` renders through the adapter unchanged; switching renderers changes no domain/view-spec | MVP (design) | 0006/0012 | A-044/T-204 | ARCH §10 / BACKLOG |
| SR-U11 | Packaging & platform: signed/notarised `.dmg`, startup budget; stated min macOS + arch; WebGL verified in WKWebView at scale | A clean mac installs the `.dmg`, Gatekeeper accepts; the WebGL canvas renders in WKWebView at A-041 | post-MVP (Slice-5: T-205/T-212; A-046 MVP is only "installs/runs") | 0012 | A-040/A-046/T-212 (extend) | APP |
| SR-U12 | Table view (MVP) + coordinated multi-view sync across table↔graph↔detail by stable id (post-MVP) | MVP: a table view (T-201) lists items; selecting a row selects the graph node. post-MVP: full cross-view sync | table=MVP / multi-view=post-MVP | 0006 | table↔A-003/T-201 (MVP); multi-view↔A-009 (post-MVP) | APP |

### 1.7 AI threats (mostly post-MVP / **DEC-001b / DEC-008**)

| id | statement | acceptance | class | src | maps_to | target |
|---|---|---|---|---|---|---|
| SR-I1 | Store every external catalog ref as (framework, version, id) + a deprecated-id alias table | ATLAS 2026.09 / OWASP-LLM 2025 store the version; an unversioned id is flagged ambiguous; a deprecated id resolves to current | post-MVP | 0014 | R-010 (extend) · **DEC-008** | ARCH §4 |
| SR-I2 | A local `LW-*` weakness namespace (status candidate) with `superseded_by` to a later CWE; non-CVE vuln ids | An LW-004 validates without a CWE; a CWE 5.0 entry links via `superseded_by`; a vuln with only an advisory URL validates | post-MVP | 0014 | R-010 · **DEC-008** | ARCH §4 |
| SR-I3 | AI method facets (ATLAS, MAESTRO, SAGAI) + an `intent` facet (adversarial/accidental/insider/provider/autonomous) distinct from method | Facet by `maestro` returns its threats; filter `intent=accidental` excludes adversarial | post-MVP | 0014 | MethodFacet (extend) · DEC-001b | ARCH §4 |
| SR-I4 | Agent capability edges (`ingests_untrusted`/`can_access`/`can_act_on`/`holds_credential`/`renders_to`) + trust-label propagation | Marking a RAG source untrusted taints its downstream agent; a query lists reachable-from-untrusted components | post-MVP | 0014 | NEW | ARCH §4 |
| SR-I5 | A mechanical Rule-of-Two / lethal-trifecta check (untrusted input + sensitive access + external effect, no deterministic policy) | A fixture agent with all three + no policy emits one finding; removing a capability or adding a policy clears it | post-MVP (**best first AI vector**) | 0014 | NEW | ARCH §4 |
| SR-I6 | AI vocabularies: component-kind, asset-class, trust-boundary type | A Component can be typed `agent-runtime`; an Asset classed `weights` with human-set impact; a boundary typed `agent→egress` | post-MVP | 0014 | R-001/R-019 (extend) · DEC-001b | ARCH §4 |
| SR-I7 | Import MITRE ATLAS (STIX) and the CoSAI Risk Map as version-pinned catalog layers | An ATLAS technique is queryable as an AttackPattern with tactic + AML.M mitigations | post-MVP | 0014/0009 | R-005 · **DEC-002** | ARCH §4 |
| SR-I8 | Mitigation assurance: `evaluated_against_adaptive` + guarantee scope; a model-internal control is not an access boundary | A prompt-level defense with `evaluated_against_adaptive=false` is flagged lower-assurance; a threat mitigated only by a model-level control shows "partial" | post-MVP | 0014 | NEW (beyond T-220 kind) | ARCH §4 |
| SR-I9 | tmodel's own AI-safety: model is an untrusted component (no direct SoT write, output can't change review state); log AI provenance (model/prompt/version); input-separation on ingest | Injected instructions in an imported doc cannot auto-accept or write outside the proposal path; a proposed Assertion lists the producing model+version | post-MVP | 0009 | NEW (A-045 adjacent) | APP |
| SR-I10 | A `maturity` attribute (in-the-wild / production / research / theoretical) derived from linked incidents, as a likelihood input | Linking an ITW incident sets maturity `W`; changing links recomputes it | post-MVP | 0014 | R-011 · DEC-003 | ARCH §4 |

## 2. Gap analysis — top capabilities absent from the ratified docs today

1. **AND/OR + ordering + shared-step graph semantics** (SR-A1/A2) are **accepted** as DEC-001a (ADR-0010) but the ARCH §4 *requirement text* still lags (only R-031 in the proposal mentions them). The gap is a doc-text reconciliation, not an open decision; they are the MVP's core differentiator.
2. **The path→threat `realizes` edge** (SR-A5) that the accepted risk rule presumes is absent from the canonical edge list.
3. **Radar→tmodel field contract + non-vulnerable components** (SR-C7): ADR-0001 points at RPT-0004 but no `R-`/`A-` enumerates the fields.
4. **Product / document / build identity + digest pinning** (SR-C6): prerequisite for R-021's per-product versioned mitigation state.
5. **Numeric interaction budgets + a benchmark harness** (SR-U3/U4): A-041/A-042 give scale and "no jank" but no number, and nothing gates A-044.
6. **Accessibility** (SR-U5): A-040…A-046 are silent; a WebGL canvas is especially exposed.
7. **Schema-quality CI + integrity checker + mechanized review gate** (SR-Q1/Q2/Q3): R-018 states the principle; enforcement has no requirement/task.
8. **A provenance model** (SR-Q5): ARCH §7 has the concept only.
9. **Completeness / unknown-vs-none semantics** (SR-C5): the main correctness risk for SBOM-derived attack-path claims.
10. **Version-pinned catalog references** (SR-I1): `catalog_ref` is unversioned while ATLAS/OWASP ids demonstrably drift.

## 3. Decisions implicated

- **DEC-002 (interchange) — ACCEPTED (ADR-0007: import OTM + STIX 2.1 only; export JSON-LD/Turtle/GraphML/CSV).** The following are **extensions beyond the accepted import set and need a follow-up interchange decision (a DEC-002 amendment / new ADR), not "DEC-002 open":** SBOM/HBOM import (SR-C3/C9), VEX (SR-C10), ATLAS/CoSAI/D3FEND/SPDX/OSV (SR-I7), STIX review export (SR-Q12), per-format crosswalk (SR-Q11), and **what "round-trip" means per format** (SR-Q13).
- **DEC-003 (risk).** The **combiner residue** (SR-R4): matrix and formula disagree on 4/16 cells, integer-vs-fraction unstated — a documentation-and-test blocker on an accepted metric. Also whether `maturity` (SR-I10) is a feasibility input.
- **DEC-008 (CWE/NVD).** Multi-source weaknesses, placeholders, local `LW-*`/non-CVE ids (SR-I2), catalog versioning (SR-I1).
- **DEC-009 (threat→product / lifecycle).** Treatment decisions (SR-R5), re-assessment (SR-R6). **Note:** RPT-0004 supplies almost no *product-family* evidence — family modelling stays a DEC-009 open with thin support.
- **DEC-001b (governed layer).** All of §1.4 and most AI vocabulary (SR-I3/I4/I6).

## 4. Recommendations

(Corrected after the adversarial review — the originally-drafted set over-promoted DEC-001b-held items and invented UI numbers.)

**Into ratified ARCH §4 (new `R-`), SAFE** — MVP, decision-free against the §1 baseline: SR-A1, SR-A2 (as a **reconciliation of §4 text with the accepted ADR-0010 / DEC-001a**, not promotion of an unaccepted proposal), SR-A3, SR-C4, SR-C6, SR-R1, SR-Q5(core). SR-Q3: promote only the **R-018 principle** (already ratified). **Not promoted:** SR-Q2 → it is ADR-0010's held §13 integrity gate (DEC-001b) → a BACKLOG task; SR-A5 (`realizes` edge) → **HOLD**, fold via the DEC-001 schema vehicle (ADR-0010 closed the core type system), not a bare §4 `R-`.

**Into APP-0001 (new `A-`), SAFE** — MVP product/UI: SR-C1, SR-C7 (as inference), SR-C8, SR-U1, SR-U2, SR-U6, SR-U7, SR-U8, SR-U9 (threshold TBD); and fix A-006 to read as the accepted composite vector (it still says "simple"). **Trim/defer:** SR-U3 → "define budgets" only, the numbers TBD (the A-041-scale bar is A-042, post-MVP); SR-U5 → non-colour review-state cue is MVP, the rest (keyboard loop, reduced-motion, screen-reader) post-MVP; SR-U11 → post-MVP (Slice-5); SR-U12 → table is MVP, coordinated multi-view is post-MVP (A-009).

**New BACKLOG tasks (MVP tooling/vectors)**: SR-A4, SR-Q1, SR-Q4, SR-Q9, SR-U4, SR-U10, SR-R7, SR-I5 (the best first AI vector) — **plus** the DEC-001b **§13 integrity checker (ex-SR-Q2)** and the **review-gate mechanization (SR-Q3 gate)**.

**Record as aspirations / later-scope (BACKLOG)**: most of §1.2 depth (SR-C2, SR-C5 full model, SR-C9 supply-chain, SR-C10), §1.4 governed layer (SR-S2…S6; SR-S1 `Mitigation.kind` is MVP-adjacent, not here), §1.7 AI (SR-I1…I10). 0004's product-composition direction lands here per the sponsor. *(Candidate to pull forward: the `unknown`-vs-`none` dependency **flag** from SR-C5 — §2 item 9 calls it the main SBOM-correctness risk and the MVP is the attack-path graph.)*

**Route to a decision (don't encode yet)**: SR-R4 → DEC-003/ADR-0006 follow-up (I4 doc/test); SR-Q13 + the SBOM/VEX/ATLAS import extensions → a **DEC-002 amendment / new interchange ADR** (DEC-002 itself is accepted); SR-I1/I2 → DEC-008; SR-R5/R6 → DEC-009.

## 5. Traceability

| report | status | feeds |
|---|---|---|
| RPT-0001 landscape | skeleton | — (blocked on T-024/T-032) |
| RPT-0002 frameworks | substantive | SR-A1…A4, risk facets |
| RPT-0003 products | substantive | SR-A2/A4, SR-U12, review/diff/report |
| RPT-0004 composition | substantive | SR-C1…C10 (mostly aspiration) |
| RPT-0005 schema-reps | skeleton | SR-Q11 only |
| RPT-0006 kg-visualization | substantive | SR-U1…U12 |
| RPT-0007 iso21434-tara | substantive | SR-R1…R8 |
| RPT-0009 sagai | substantive | SR-I9, SR-I8 |
| RPT-0011 kg-nsf-okn | substantive | SR-Q5/Q6/Q10/Q12, SR-I4 |
| RPT-0012 gui/platform | skeleton | SR-U10/U11 (via §0) |
| RPT-0013 sdl-conformance | substantive | SR-S1…S6 |
| RPT-0014 ai-threat-model | substantive | SR-I1…I10 |
| RPT-0015 kg-schema-foundation | substantive | SR-Q1…Q9 |

**Next:** adversarial review of this set, then a follow-up PR applying §4's promotions to ARCH-0001 §4, APP-0001, and BACKLOG-0001 (each new `R-`/`A-`/`T-` citing its `SR-` + source report), and opening the DEC-002/003/008/009 follow-ups named in §3.
