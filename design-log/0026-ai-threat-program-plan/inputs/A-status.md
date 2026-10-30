# Thread A: status and plans review for the AI threat program (RPT-0014 and successors)

**Date:** 2026-10-26 · **Scope:** Threat-Radar/tmodel `main` @ `449f515`, open PRs, open issues; Threat-Radar/library `main` @ `6d9a51f` (fresh clone; the tmodel submodule is pinned at `b3786cd`) · **Mode:** read-only. Nothing was edited, commented on or created in either repo.

---

## 1. Summary

- **RPT-0014 round 1 is a large corpus nobody has reviewed.** `research/0014-ai-threat-model/` holds 1,181 sources, 179 incidents, 127 threat models (TM-), 146 techniques (AIT-) and report v0.2.0. Every AIT entry has `review_status: hypothesis` (146 of 146), and 112 sources are "medium (capped)" because they contain details recalled from memory. Of the 1,181 sources, about **10 exist as library records on library `main`** (for example csa-maestro-2025, spotlighting, sp-800-218a, etsi-en-304-223, cisa-ai-in-ot, lf-2024-spdx3-aibom, nocera-2025-aibom-mlr, stride-gpt, aws-threat-composer). NIST AI 100-2 E2025, ATLAS, the OWASP LLM Top 10 and CoSAI are **not** library records yet.
- **Of the five lanes, only one produced anything.** agentic-mcp (#78, paria03) delivered the calibration (PR #117, merged 10-12) and 19 subset-1 records (library#22). library#22 has been open since 10-14; two students reviewed it, it is mergeable, and it waits on a sponsor merge. The other four lanes (#79–#82) did no calibration, so `calibration/COMPARISON.md` does not exist and the #84 "five lanes agree" gate cannot be reached. `extractions/` holds only its README and `round2/` holds only the critic-gaps JSON. WAVE 2 (FX-TM/FX-AP) has not started.
- **Some AI-threat work moved outside RPT-0014:**
  - PR #159 (RPT-0009 0.3.0, Maimcghee, **APPROVED, not merged**) has the first AI threat model in schema form. `em-01-echoleak-m365-copilot.yaml` contains 12 ATLAS steps, 3 assets, 4 trust zones, 8 data flows and 5 mitigations, and it lists schema gaps AI-1…AI-7.
  - #170 (paria03) asks for requirement extraction from MAESTRO, SP 800-218A, OWASP agentic and MCP best practices, with proposed `addresses` links to agentic threats.
- **The machinery to publish an AI threat model mostly exists:**
  - Accepted core schema (ADR-0010) and validation harness (`spec/vectors`, `check-edges.py`, `bin/gen-schema`)
  - Engine attack-path enumeration (#132 merged), engine graph API and Cytoscape view (PR #162 open)
  - Static report and bibliography publishing with an identity guard (`docs/publishing/`)
  - The #168 recipe for "AI-proposed Assertion, then human Review"
- **What is missing:**
  - Asset, TrustBoundary and DataFlow, which sit in PR #130 / ADR-0011 (unmerged)
  - AI component kinds and the step→pattern link (AI-1, AI-6)
  - Feasibility and impact values, which ADR-0006 requires a human to set
  - Structured mitigations (catalog mitigations are free-text strings)
  - Engine risk (Part 2 of #63)
  - Any human-reviewed AI content
- **Answer to "can we build an AI threat model right now?": yes, as a reviewed demonstrator; no, as a validated professional product.** One LLM-agent / RAG / MCP product model, generated reproducibly from `attack-catalog.yaml` plus §1 of the report and hand-checked on a sample, can be produced in about 5–8 working days of agent time plus 1–2 days of human review. It depends on merging #130 (or validating against its proposal container) and on keeping every AI-derived edge `proposed` until reviewed.

---

## 2. Timeline and capacity

**Calendar (SOW-0001 §3, PLAN-0001 §8, BACKLOG-0001).** Today is 10-26, inside I3 (Oct 23–Nov 5).

| Milestone | Date | Content |
|---|---|---|
| M3 demo floor | **Nov 5** (10 days) | library in the engine, table views, interactive attack-path graph with review end to end on one worked example |
| M4 | Nov 19 | ADR-0006 risk computed; ≥2 domains |
| M5 | **Dec 5** | `.dmg`, docs, demo |

- The issues use one-week sprints. Sprint 1 is Oct 16–22, so S3 is Oct 30–Nov 5, S4 Nov 6–12, S6 Nov 20–26 (Thanksgiving week) and S7 Nov 27–Dec 3. About 5.5 weeks of semester remain.
- **SOW §2 C10** keeps "AI threat model research" as a capability (#71, lanes #78–#82), but no milestone in M1–M5 names an AI deliverable. The sponsor's new program is unscheduled scope on top of the MVP.
- PLAN-0001 and BACKLOG-0001 are stale. BACKLOG was last updated 10-15, still lists T-030/T-031 as todo, and has no AI rows after I1.

**Student load, read from open issues and PRs:**

| Handle | Build / MVP commitments | Research / library in flight | RPT-0014 status |
|---|---|---|---|
| paria03 | #63 Part 2 risk (I3), #124/PR #155 packaging, #170 coverage query + agentic requirement sources | library#30 (RPT-0002) | #78: calibration done (#117); subset-1 is library#22 (reviewed, unmerged); no WAVE 2 |
| kriishnaa-18 | #58 tables, #59 / PR #162 graph (6.5k LOC, open), #171 | — | #81: nothing; its dates (10-12…10-22) have passed |
| Clovier | #60 / #138–#142 loader, #61 / #143–#146 CWE import, #152–#154, PR #130 schema proposal, PR #161 | library#24, #28, #29, #31, #33 | #80: #134 calibration (S1, missed); #135 is S4 and #136 is S6, so RPT-0014 subset-1 is scheduled into M4/M5 weeks |
| Maimcghee | #64/#65, #169 converter + CI | PR #158, PR #159 (AI threats, approved), library#21, #157 | #79: nothing; redirected to RPT-0009 part B (AI) on 10-21 |
| nymble (sponsor) | ADRs, merges, #82 integration lane | library#34–#36, PR #167, PR #174 | #82: no COMPARISON.md, no integration run |

**Capacity verdict.**
- Every student is fully booked on M3/M4 build work and on the new #168 requirement pass, filed today.
- RPT-0014 WAVE 1 for the other three lanes (60 records plus calibration) does not fit before M4 unless something is dropped.
- The sponsor is the merge bottleneck:
  - tmodel: #130, #159, #162 and #167 wait on review or merge.
  - library: #22 and #21 wait on review or merge.
  - Claude cannot merge.
- A large AI program this semester must therefore be **agent-executed, with the sponsor as reviewer**, and students as reviewers of small samples, not as producers.

---

## 3. Decided and open decisions relevant to AI threat work

**Decided (usable now):**
- **ADR-0010 / DEC-001a, core types.** Product, ProductInstance, Component, Party, Weakness, Vulnerability, AttackPattern, ThreatInstance, AttackStep (AND/OR, `precedes`, `kill_chain_phase`), AttackPath (`attack_feasibility`), DamageScenario, Mitigation (`catalog_ref`, `mitigates`, `mitigation_status`), RiskScore/ImpactVector, Review/Assertion, `identifiers`.
  - The accepted core has **no Asset, TrustBoundary or DataFlow class and no `component_kind`**. The only mentions of "asset" in `spec/schema/tmodel-object-model.linkml.yaml` are comments.
- **ADR-0006 / DEC-003.** Risk is a composite vector:
  - feasibility on the ISO/SAE 21434 Table-1 four-level scale, **human-rated at MVP**;
  - impact as S/F/O/P, human-supplied;
  - mitigation status as a peer, never lowering risk;
  - risk = M(Impact, Feasibility), folded worst-path;
  - Common Criteria is display-only.
  - RPT-0007 §3.2 gives the three Annex G methods. The **attack-vector method (G.4)** suits concept-phase models and maps cleanly from the catalog's `attacker_access` field.
- **ADR-0007 / DEC-002.** LinkML is the IDL. Import is OTM and STIX 2.1 only; export is JSON-LD, Turtle, GraphML and CSV. ATLAS and CoSAI import is an **extension that needs a further interchange ADR** (RPT-0016 §3, SR-I7).
- **ADR-0004.** Files are the source of truth, with typed link records; a library record can bear on many model elements, as #84 asks.
- **ADR-0008.** Oxigraph is the working store.
- **ADR-0003/0009.** Tauri + TypeScript UI, with a Python engine.
- **ADR-0002.** The MVP is a reviewed attack-path graph over at least two domains, one modeled in depth. AI is **not** one of the MVP domains; the domains are software, automotive and hardware.
- **PLAN-0003 sponsor rulings.**
  - D1: the bibliography generators belong in the library (A3 not done).
  - D1a: there is one tmodel Pages site.
  - D3: requirements are written in LinkML.
  - A2: topic pages must include "AI-threats" as a grouping (not built).

**Pending, accepted on merge:**
- **PR #130 → ADR-0011** (front matter `status: accepted`; decision_maker Clovier, "delegated_by: nymble"; `reviewed: false`). It adds:
  - Asset, TrustBoundary (zone plus `in_trust_zone`) and DataFlow;
  - `component_kind`, `DamageScenario.damages_asset` and `ThreatInstance.targets_element`;
  - Assertion provenance (`asserted_by`, `generated_by`, `evidence`).
  - **It is a prerequisite for any AI model with trust boundaries.**
  - The sponsor still has to rule on three open choices: DataFlow joined to Components (OTM style) or a DFD layer; naming; and whether the pv-01/pv-02 vectors get reviewed. Having a student-authored ADR self-mark itself accepted is a governance smell worth one line in the merge decision.
- **PR #167 → ADR-0012.** Requirement joins the core, with `addresses` (ThreatInstance / Weakness / AttackPattern), `satisfied_by` Mitigation, `Mitigation.stated_as` and `applies_to_family`. This gives an AI model "control requirement" nodes. Whichever of #130 and #167 merges second must regenerate the generated schema files.

**Open:**
- **DEC-001b.** The governed layer: ThreatModel, SecurityProgram, Gate. A "TARA as an SDL artifact" with approval and digest needs the C1/C2 fixes from DL-0020, so a governed, signed threat-model artifact is **not** expressible in the accepted schema yet. An HTML snapshot plus a git tag is the workaround.
- **DEC-008.** CWE/NVD, plus local `LW-*` weaknesses, non-CVE vulnerability ids and version-pinned catalog references (SR-I1/I2).
- **DEC-009.** Generic threat → product/family mapping. This *is* the "reusable TARA across domains" question.
- **#84.** Partition (many models or one large one), flat or hierarchical storage, and the five-lane gate.
- **RPT-0014 §8 questions 1–7** have had no sponsor answers. They cover AI-enabled offense as capability or technique, non-adversarial failures, prompt-injection granularity, importing CoSAI/ATLAS, the `LW-*` namespace, the first AI deep-domain profile, and the scope of provider-side and consumer-harm threats. They block a consistent catalog.

**Not decided anywhere but needed:**
- AI component kinds (AI-6, SR-I6)
- `AttackStep.uses_pattern` (AI-1)
- Content trust labels on flows (AI-3, SR-I4)
- `Mitigation.bypassed_by` and `evaluated_against_adaptive` (AI-7, SR-I8)
- Mapping fit grade (AI-4)
- Signal values such as SSVC and EPSS (AI-5)
- `maturity` as a feasibility input (SR-I10, a DEC-003 residue)

---

## 4. Issue and PR map

**Merge candidates. These are sponsor actions; Claude cannot merge.**

| Item | Why it matters for the AI program |
|---|---|
| PR #159 (approved) | The first AI model plus gaps AI-1…AI-7; the AI-security requirement-to-threat mapping |
| library#22 (reviewed twice, mergeable) | 19 agentic/MCP records; unblocks #170 (two of its sources live there) |
| PR #130 (ADR-0011) | Asset, TrustBoundary and DataFlow, needed before any AI TARA vector |
| PR #167 (ADR-0012) | Requirement/mitigation layer, needed for control requirements in AI models |
| PR #162 (graph API + view) | Renders any vector under `spec/vectors/`; the demo surface |
| library#21, #25, #32 (already merged) | CWE FX-1 (#21) is needed for CWE-1426/1427/1039 nodes |

**Keep, and re-scope:**

| Issue | Recommended re-scope |
|---|---|
| #71 | Remains the AI parent. Rewrite the definition of done for the new program (catalog, product-type KG, hierarchical report, TARA vector, bibliography). Answer report §8 Q1–Q7. |
| #73 | Re-scope to agent-run FX-TM extraction of about 10 machine-readable catalogs first (CoSAI YAML, ATLAS 2026.09, OWASP LLM/ASI, NIST AI 100-2, Threat Composer GenAI JSON, MAESTRO), not 127 models. |
| #74 | **Unblocked**: DEC-001a is accepted and #130/#167 are pending. Make it the home for AI-1…AI-7 and SR-I1–I10 as one ADR-0011 amendment proposal. |
| #75 | Keep. It depends on #74 and on the loader (#60/#139–#142). |
| #84 | Replace the "five lanes agree" gate, which is unreachable, with an agent-vs-agent plus human-sample gate. The agentic-mcp calibration is the human baseline. |
| #86 | Keep as the bibliography parent. Add per-reference summary, categories and artifact links as the definition of done. Absorbs the program's "hierarchical bibliography" request. |
| #87 | Keep (publication umbrella); add the AI report and TARA HTML outputs. |
| #104 | Stage 1 is done (RPT-0015) and Stage 2 is partly done (ADR-0010/0011/0012). Close it, or narrow it to the Stage 3 per-object extraction vectors, including AI ones. |
| #63 | Part 2 (risk) is on the critical path for any risk-bearing TARA. Its open questions block it: one rating per OR alternative; file policy for `/attack-paths`. |
| #168, #170 | #170 already owns agentic requirement extraction; reuse it as the AI controls layer. |

**Supersede or close candidates. Close with a note pointing at the new program issues.**

- **#78–#82 WAVE 2 unit lists.** The WAVE 2 extraction units and sweeps listed in each lane body are obsolete given the current load. Supersede them with program issues. Close #78 when library#22 merges (its WAVE 1 is done). Close #79/#81/#82 as superseded, or shrink each to "review 5 agent-produced records". #80's children #134–#137 are scheduled in S4/S6 against M4/M5; drop or convert them to review-only tasks.
- **#72, #12, #13** are already closed; nothing to do.
- **#20** (research epic, stale since 10-01) and **#15/#17** (design issues superseded by ADR-0010/0011/0012). Close, or link to the ADRs.
- **#19.** Fold into #168 / DEC-001b.
- **#14.** Superseded by ADR-0006; the residue is in library#35.
- **#50–#54 (Edge Rich KG).** Stale since 10-01–10-02; ADR-0004/0008 are done. #51 duplicates #60/#142, and #52/#53 overlap #65. Close as superseded by the lane issues.
- **#5.** The ingestion pipeline is largely delivered (library#14–#19); close or narrow it.
- **Privacy fixes (not closures):**
  - Titles of **#36, #38, #39** contain project people's real first names, and #39 also a surname. The body of **#84** has first names.
  - **`research/0014-ai-threat-model/LANES.md` on `main` lines 170–178** still uses students' first names in the review column and the "Lanes line up…" paragraph. This contradicts PR #112 ("Remove all project-person names").
  - Commit author names on `main` also show first names. Git metadata is outside the published pages, but worth noting.

---

## 5. RPT-0014 state, and why it stalled

**On `main`:**
- `report.md` v0.2.0, AI-generated and AI-reviewed (46 findings folded); `reviewed: false`; `library_commit: "records not yet ingested"`.
- `attack-catalog.yaml`: 146 entries. Fields are id, class, `class_group` X01–X16, `lifecycle_stage`, `intent`, attacker access and knowledge, `asset_classes` A01–A18, `reference_components` C01–C21, preconditions, impacts, `example_incidents`, `mitigations` (free-text strings), `catalog_ids` (ATLAS 2026.09, OWASP LLM:2025 and ASI:2026, CWE 4.20, NISTAML), sources, `maturity` and `maturity_basis`, and `review_status: hypothesis`.
- Maturity counts: 38 in the wild (31 exploited plus 7 occurred), 42 production-demonstrated, 62 research only, 4 theoretical.
- `incidents.md` (179), `threat-models.md` (127 TM entries) and `enumerations.md` (crosswalk, 16 candidate `LW-*` weaknesses).
- `wave1-assignments.csv`: 90 subset-1 rows plus 5 calibration rows; **1,088 rows are "later"** and have no owner or schedule.
- `calibration/agentic-mcp/` holds 3 records (NIST AI 100-2, Greshake, BIML ARA), with good-quality applicability tables that link AIT and C ids.
- `extractions/README.md` defines the FX-TM and FX-AP profiles; there are no units.
- `round2/round1-critic-gaps.json`: the critic's verdict is that the survey is "not complete … must not be treated as a PhD-level bibliography" until a top-venue sweep and a non-US sweep are done.
- `.claude/workflows/rpt0014-{extract,sweep,integrate}.js` exist and have never been run by the lanes.

**Why it stalled, from the evidence:**
1. **Bad timing.** The WAVE 1 kickoff (10-07) landed on I2 build lanes (Oct 9–22). Students put graded build and report work first: #132, #129/#130, #126, #122/#123, #110/#127. Between 10-07 and 10-26, 15 tmodel PRs came from students and exactly one (#117) was RPT-0014.
2. **The gate design could not complete.** The five-lane calibration agreement (#84) needed all four students to calibrate; one did. The integration lane (#82, sponsor) never wrote COMPARISON.md, so nothing advanced to subset scale.
3. **Merge latency.** The only subset output (library#22) has sat for 12 days after two student reviews. Lanes that see no merge see no reason to continue.
4. **Gated on schema.** WAVE 2 waited on #74 / DEC-001. DEC-001a was accepted 10-12, but #74 was never restarted, and ADR-0011 and ADR-0012 are still open PRs.
5. **Friction:**
   - work must be opened from the library project root;
   - each lane needs its own Claude account and WebSearch quota;
   - a 660 MB PDF cache must be rebuilt;
   - the scale is a mismatch: 1,181 sources against 90 assigned.
6. **The sponsor redirected the AI work.** On 10-21 Maimcghee's AI effort went to RPT-0009 part B, which produced the only AI schema model. On 10-26 the students got a new requirement-extraction pass (#168–#172).

**What the library holds for AI on `main` (566 records):**
- Roughly 20–25 records are substantively AI-security. Examples: etsi-en-304-223 (FX-1), cisa-ai-in-ot-principles (FX-1), sp-800-218a (distilled), csa-maestro-2025 (thin), spotlighting, spml-image-prompt-injection, systems-security-agentic-computing, sagai-workshop, llm-programmatic-dual-use, nocera-2025-aibom-mlr, lf-2024-spdx3-aibom, g7-sbom-for-ai-2026, stride-gpt, aws-threat-composer, aws-security-agent-threat-modeling, draft-asor-wimse-agent-delegation-chain, eu-ai-act-art-50.
- There is **no AI topic** in `topics/`; only `sagai.yaml` (8 records) is close.
- Matching the RPT-0014 source URLs, arXiv ids and DOIs against library records gave 19 raw hits, about 10 of them true identity matches. library#22 would add 19 more, including owasp-agentic-threats-mitigations-v1-1, owasp-mcp-top10-2025, mcp-spec-security-best-practices and AgentDojo.

---

## 6. Reusable machinery

| Need | Exists | Gap |
|---|---|---|
| Schema and validation | `spec/schema/tmodel-object-model.linkml.yaml` (core accepted), `bin/gen-schema --check` (JSON Schema/SHACL/Python), schema CI job (PR #129), `spec/vectors/example-container-core.linkml.yaml`, `design-log/0021-…/check-edges.py`, plus `check-refs.py` in #130 | Asset/TB/DataFlow (#130), Requirement (#167), the AI slots AI-1…AI-7 |
| Worked models | mvp-01/02/03/18 (core), tv-* (governed), pv-01/02 (#130), em-01 EchoLeak (#159) | No AI model under `spec/vectors/`; em-01 lives under `research/0009-sagai/example-models/` |
| Engine | `engine/engine/paths.py` (AND/OR enumeration, review-state carry-through), API `/attack-paths`, CLI `tmodel paths`; `/graph` in #162 | Risk vector (#63 Part 2); coverage query (#170); a lethal-trifecta / Rule-of-Two check (SR-I5); `/graph` reads only `spec/vectors/` |
| GUI | Cytoscape view with path highlighting and review status (PR #162) | Not merged; bundling of vectors in the `.dmg` (#63 comment) |
| Report publishing | `docs/publishing/render_report.py` (archdoc md → static HTML; `reports.yaml` manifest; version = REVISION), SDL report already published; `check_identities.py` + `publishing/identities.yaml` (GitHub ids only, local real-name override); `check_links.py`; `bin/publish-site`; `site.yaml`/`site_nav.py` | Mermaid is not rendered (no JS allowed, and the no-Node rule) → pre-render SVG with `dot` (graphviz is installed, as the SDL object-model SVG shows); no TARA template; no multi-part report support |
| Bibliography publishing | `render_bibliography.py` (A–Z, by-topic/type/body, crosswalk; 415 manifest entries), per-record HTML from library `bin/render-html` | No AI topic grouping (PLAN-0003 A2), no expandable rows (A1), no requirements/extraction-status columns (B1), generators not yet moved into the library (A3) |
| Extraction | library skills `ingest-reference`, `summarize`, `distill`; FX-1; `library_requirements` LinkML v3 (library#16); RPT-0014 workflows `rpt0014-extract/sweep/integrate.js`; the #170 prompt template (proposed Assertions plus a human review sample) | Workflows never run; the FX-TM/FX-AP profiles are untested |
| Catalog data | `attack-catalog.yaml` (146), C01–C21, TB1–TB14, A01–A18, X01–X16, incidents with ATLAS case-study ids (69), the CoSAI Risk Map commit pinned at 0d8bfc9b5d76, ATLAS 2026.09 YAML with digest (in em-01) | No ATLAS/CoSAI importer (needs an interchange ADR); mitigations unstructured |

---

## 7. Can we build an AI threat model right now?

**Short answer.** Yes for a reproducible, honestly labeled demonstrator of one AI product type, in days. No for a professional-grade, reviewed, cross-domain TARA this month.

**What the data supports:**
- **Decomposition.** C01–C21 and TB1–TB14 (report §1) are a usable reference architecture; each AIT carries `reference_components`. For an "LLM agent with RAG and MCP tools" product, the relevant components are C05–C11, C13, C17, C18 and C19, and the relevant boundaries are TB2, TB5, TB6, TB7, TB8, TB9, TB10, TB13 and TB14.
- **Threats.** Selecting the AIT entries whose `reference_components` overlap the product gives about 60–80 candidates. Filtering to maturity W/P gives about 25. Strongest are AIT-064/065/066/083/084/091/092/093/096/097/099/100/101/102/111/113/114 and AIT-134/139/140.
- **Attack paths.** These can be grounded in public step sequences: ATLAS case studies (em-01 already encodes AML.CS0059), plus incidents INC-123 (malicious MCP server) and the INC-112/154 coding-agent RCE classes.
- **Assets.** A01–A18 give a working asset taxonomy (report §4), with counts per asset.
- **Catalog ids** are version-pinned, which satisfies SR-I1 in spirit.

**What is missing:**
1. **Schema.** Asset, TrustBoundary and DataFlow exist only in #130. The accepted core cannot draw the context-window boundary (AI-3) or type an agent or RAG component (AI-6). Workaround: validate against #130's `example-container-proposed.linkml.yaml`, as em-01 does, and record the gaps.
2. **Feasibility (ADR-0006).** It must be human-rated. The catalog offers `attacker_access` and `maturity`. An agent may *propose* a G.4 attack-vector rating per path as an Assertion; a human sets `attack_feasibility`. Impact S/F/O/P is human. Without those two, RiskScore is empty, and #63 Part 2 is not built anyway.
3. **Mitigations.** These are free-text strings such as "AML.M0030 restrict tool invocation…". They need splitting into Mitigation nodes (`catalog_ref` AML.M*, CoSAI control ids, system controls such as CaMeL, Progent and egress allowlists) linked by proposed `mitigates` Assertions. #170's OWASP-agentic and MCP requirements can supply Requirement plus `stated_as`.
4. **Weaknesses.** CWE-1427, 1426, 1039 and 1434 are fine. Most AI classes have no CWE; `LW-*` candidates (enumerations.md §5) need a DEC-008 call, or have to be marked local and candidate.
5. **Review.** All 146 AIT entries are hypotheses. No human has signed one entry, mapping or maturity rating. RPT-0014 calibration is the only human-checked AI material: 3 records plus 19 in library#22.
6. **Governed artifact.** A "TARA as an SDL artifact" (ThreatModel with approval and digest) is DEC-001b, so it is not available. Ship an HTML snapshot with REVISION, the git commit and the `library@commit` pin instead.

**A concrete minimal path, about 2 weeks elapsed, mostly agent work:**

| Day | Step | Output | Reviewer |
|---|---|---|---|
| 0 | Sponsor merges #159, library#22 and #130 (or rules to validate against the proposal container); answers RPT-0014 §8 Q6 (first AI profile = "enterprise LLM agent: copilot + RAG + MCP tools + coding agent", or the AWS Scoping Matrix scope) and Q3 (granularity of prompt injection) | decisions in an issue comment or ADR | sponsor |
| 1–2 | **Generator** `research/0014-ai-threat-model/gen/` (Python, stdlib + PyYAML, deterministic). Input: a product profile (component list → C-ids, trust zones → TB-ids, held assets → A-ids). It selects AIT by component overlap and maturity, emits ThreatInstance / AttackPattern (ATLAS `catalog_ref`) / Weakness / Mitigation stubs, and makes **every** threat→component, threat→asset, mitigation and mapping edge a `proposed` Assertion with a basis (AIT id + S-/INC- ids). This is the reproducibility and cross-domain piece (C9/DEC-009 demonstrator). | `ai-01-llm-agent.yaml` | — |
| 3–4 | **Hand-author 3–4 grounded attack paths** on top: EchoLeak (reuse em-01's 12 steps), MCP tool poisoning or rug-pull to credential theft (AIT-096/097/100; INC-123), coding-agent injection to RCE in CI (AIT-092/110; INC-112/141), and memory poisoning (AIT-102). Add proposed G.4 feasibility. Add a lethal-trifecta finding (SR-I5) as a small engine query. Validate with `linkml-validate`, `check-edges.py`/`check-refs.py` and engine `paths`. | vector + engine output | — |
| 5 | **Adversarial review agent**, fresh context: recount, check each AIT→ATLAS/OWASP/CWE id against the pinned catalogs, check each incident claim against its source, and hunt for omitted AIT entries that apply. | `verify.md`, reject log | — |
| 6–7 | **Human review sample** (sponsor plus 1–2 students, about 1 hour each): Reviews on 20–30 Assertions (each path, top threats, 10 mappings); human feasibility and S/F/O/P on the 4 paths | Review records | humans |
| 8–10 | **TARA HTML**: a `render_tara.py` template beside `render_report.py`, built from the vector. Sections: item definition, assets, damage scenarios, threat scenarios, attack paths (SVG via `dot`), feasibility, risk matrix, treatment, open hypotheses table. Every unreviewed element is visibly badged "AI-proposed". Run `check_identities.py`/`check_links.py`; publish under `docs/reports/`. | published TARA | sponsor |

- **Where it lives.** Under `research/0014-ai-threat-model/models/` while #130 is unmerged. Move it to `spec/vectors/ai-01-*.yaml` once ADR-0011 merges, so #162's `/graph` can show it.
- **What it proves.** The pipeline from catalog to product model to reviewed paths to TARA works for AI.
- **What it does not prove.** Catalog completeness, or correct ratings beyond the reviewed sample.

---

## 8. Risks

1. **R-018: unreviewed AI-generated data presented as analysis.**
   - 146 of 146 AIT entries are hypotheses. 112 sources carry details recalled from memory, and one critic pass called the survey not complete.
   - Maturity is "mechanically derived" from incident kinds that are themselves judgements.
   - A professional-looking TARA built on this invites rubber-stamping, which is PLAN-0001 §10 "AI summaries unread".
   - Mitigation: proposed-by-default Assertions; visible badges; a published "hypotheses remaining" count; human samples with explicit coverage percentages.
2. **Citation and fabrication risk at scale.** A 1,000+ reference bibliography with an agent-written summary for every entry multiplies the round-1 error classes: a wrong arXiv id, wrong CVEs, 39 deprecated ATLAS ids, ATLAS renumbering (2026.07), and OWASP id drift (9 of 10 ids changed). Every id needs (framework, version, id), and spot-checks need a defined sampling rate.
3. **Schema churn.**
   - #130 and #167 both amend DEC-001a and regenerate the same files.
   - An AI model built now will need re-shaping when AI-1…AI-7 land.
   - DEC-001b blocks a governed TARA.
   - Sequence the merges: #130, then #167, then the AI vector.
4. **Scope versus semester.**
   - The demo floor is in 10 days, and AI is not an MVP domain under ADR-0002.
   - The program competes with M3/M4 for sponsor review time, which is the real bottleneck.
   - Using AI as the "≥2 domains" breadth example would turn the threat into a contribution, but needs a sponsor ruling.
5. **Student capacity and learning goal.** If agents produce everything, the "learning is an explicit outcome" goal (PLAN-0001 §1) suffers. If students produce it, the MVP slips. A compromise: students own *review samples* and one short report section each.
6. **Privacy.** First names appear in LANES.md on `main`, in the titles of #36/#38/#39 and in the body of #84. The publishing guard checks only `docs/**/*.html`. Any new report rendered from LANES-like text would leak names.
7. **Licensing.** Most vendor, RAND and journal sources are all-rights-reserved. FX-AP quotes must stay to a sentence or two with locators, and ISO/IEC/SAE text must be paraphrased (ADR-0012). The repo is public.
8. **Tool and quota limits.**
   - Round 1 exhausted the 200-call WebSearch budget early on day one. The arXiv, Crossref, Semantic Scholar and NVD APIs were the fallback, which skews discovery toward arXiv.
   - ACM DL and IEEE Xplore were unreachable.
   - The per-account quota strategy failed because the accounts were not used.
9. **Prompt injection against the extraction tooling (SR-I9).** The corpus is literally prompt-injection research and incident write-ups. Extraction agents read attacker-authored content, so the AI pipeline must never write accepted state, and the identity and link guards must run in CI.
10. **Merge authority.** Claude cannot merge, and PR-only `main` applies to both repos. Every phase ends in the sponsor's queue.

---

## 9. Recommendations for the program plan

1. **Re-baseline before expanding.**
   - Merge the ready items: #159, library#22, then #130 and #167 in that order, then #162.
   - Close or supersede the stale issues listed in §4.
   - Fix the name leaks in LANES.md and in the titles and bodies of #36/#38/#39/#84.
   - Answer RPT-0014 §8 Q1–Q7 in one sponsor comment on #71.
2. **Retire the five-lane production model.** The program should be **agent-produced and human-sampled**:
   - one Claude-run lane per deliverable;
   - students as named reviewers of fixed samples (for example 5 records or 10 Assertions each per week);
   - replace #84's agreement gate with an "agent A vs agent B vs the agentic-mcp human baseline" agreement metric on the 3 calibration sources (PLAN-0003 R-B4).
3. **Deliver a vertical slice first** (§7): an AI-01 LLM-agent TARA vector plus generator plus HTML. It shows all six sponsor asks in miniature, and it exposes schema gaps early. Fold AI-1…AI-7 and SR-I1–I10 into a single **#74 proposal** (an ADR-0010 amendment, like ADR-0011).
4. **Then scale breadth in layers, each with its own definition of done and review gate:**
   - (a) **Attack catalog v0.3.** Normalize mitigations into nodes; add ATLAS-only techniques left unmapped (enumerations §6); run the critic-gap sweeps (top venues, non-US) with API-first search to save WebSearch.
   - (b) **Product/target-type KG.** Use `Product.classifications` / `applies_to_family` (ADR-0012) for families such as copilot, RAG app, coding agent, MCP server, model hub consumer, MLOps platform, edge/embodied and AI-in-OT (CISA), each mapped to C-ids. This is the DEC-009 demonstrator, and needs an ADR before it is treated as decided.
   - (c) **Hierarchical report.** Split RPT-0014 into parts (architecture; per-class §3.1–3.15; incidents; enumerations; threat-model comparison), published via `reports.yaml` with SVG diagrams.
   - (d) **Hierarchical bibliography.** Add an `ai-threats` grouping topic in the library (PLAN-0003 A2) with subtopics per X-class group. Every RPT-0014 source becomes at least an honest stub library record with summary, tags and applicability; expandable rows follow (A1a). Prioritize tier 1 and W/P-cited sources (about 459 sources are cited by no technique; deprioritize those).
   - (e) **Adversarial completeness loop.** Each round is a fresh critic, a gap fill and a fold, with design-log reject logs. Stop on a coverage metric, for example "no ATLAS technique and no OWASP LLM/ASI 2025/26 id without an AIT; top-5-venue 2025–26 sessions swept", not on round count.
5. **Keep it outside the MVP critical path.** Schedule the vertical slice for S4–S5 (Nov 6–19), after the demo floor. Present AI-01 at M5 as the breadth domain only if the sponsor rules it counts. Everything else (catalog v0.3, the bibliography at full scale, multi-part report polish) is post-semester or optional, and should be written up as its own PLAN/BACKLOG (PLAN-0003 already says research tracks graduate to their own documents).
6. **Mandatory rules for every AI artifact:**
   - provenance on each Assertion (agent, model, date, basis);
   - `proposed` until a named Review exists;
   - a published reviewed-vs-proposed ratio;
   - (framework, version, id) on every catalog reference;
   - paraphrase-only for licensed text;
   - GitHub handles only;
   - `check_identities` and `check_links` in CI.
