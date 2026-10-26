---
schema: "archdoc/v1"
id: PLAN-0004
title: "Program plan — AI threat research, knowledge graph, hierarchical report and reproducible TARA (RPT-0014 round 2 and successors)"
short_title: "AI threat program"
description: "The program that turns RPT-0014 round 1 (1,181 sources, 146 hypothesis techniques, 179 incidents, 127 threat models) into AI threat research with a defined release bar: a distilled bibliography linked to weaknesses, techniques and incidents with measured coverage; a target-type working vocabulary feeding a knowledge-layer ADR; a hierarchical multi-part report organised by risk phase and target type; a reproducible multi-domain TARA HTML artifact for the SDL; and latest-attacks and adversarial-completeness loops that terminate. Agents produce and cross-check; humans review a budgeted, prioritised sample and a gold set; the sponsor gates within a stated weekly budget. Accepts no DEC-*; section 7 names the decisions an ADR or a sponsor ruling must settle."
type: plan
category: research
status: draft
version: "0.2.0"
version_policy: "semver; MINOR = additive; version and updated move together (ARCH-0001 §9.5)"
date: "2026-10-26"
updated: "2026-10-26"
issue: 71
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: project/PLAN-0004-ai-threat-program.md
defers_to: ARCH-0001
informs: [DEC-001a, DEC-001b, DEC-003, DEC-002, DEC-008, DEC-009]
open_decisions: [DEC-001b, DEC-008, DEC-009]
related: [PLAN-0002, PLAN-0003, SOW-0001, RPT-0014, RPT-0016, MAP-0001]
agent_notes: >
  AI-drafted from three read-only planning memos (status; ingestion and sources; representation)
  over tmodel main @ 449f515 and library main @ 6d9a51f; v0.2.0 folds a fresh adversarial
  critique (41 findings; see "Review log" and DL-0026). This is the research track PLAN-0003 §1d
  said would graduate into its own PLAN; it consumes PLAN-0003 items rather than restating them.
  Every schema element is a proposal routed to an ADR (Appendix E is input to an ADR draft, not a
  decision); every AI output is a hypothesis until a human Review exists (R-018). Every rule a
  DoD depends on is stated in this file; the memos are provenance only. People appear by GitHub
  handle or role only. Design-log entry: DL-0026 (verified free on main and on open PRs #130,
  #167; ships in the same PR as this plan).
---

# PLAN-0004 — AI threat program

> **Plan, not decision.** Nothing here accepts a `DEC-*`; an ADR does that (ARCH-0001 §9).
> Every AI-produced record, mapping, rating, summary and model element named in this plan is a
> **hypothesis until a human Review exists** (R-018). Agent cross-checks raise confidence; they
> never make anything "reviewed".

## 0. Decision brief (one page)

**Asks → deliverables.** Catalog the breadth, scope and categories of attacks on and with AI (D1);
a target/product-type collection in the KG suitable for modelling (D2); a multi-part hierarchical
report "AI threats today" by risk phase that is the basis for threat models (D3); a bibliography
where every reference has a summary, categorisation and artifact links, connected to weaknesses
and threats (D4); a reproducible multi-domain TARA HTML artifact for this and other SDL processes
(D5); a weekly latest-attacks loop incl. X (D6); adversarial completeness rounds that repeat until
coverage and clarity pass (D7); a gap dashboard feeding new mini-reports (D8).

**What is realistic this semester (5.5 weeks, M3/M4/M5 first).**

- **Yes:** a *draft* edition (banner on every page) with measured coverage; an AI-01
  LLM-agent/RAG/MCP demonstrator TARA, reproducible from a lock, with human feasibility and
  S/F/O/P on 3–4 paths and 10 human-reviewed Assertions; a 30-reference human gold set that
  measures how wrong the agent pipeline is, field by field.
- **No:** a reviewed or "professional-grade" edition (§2.1 defines that bar; earliest Phase 3,
  post-semester), human review of most records, multi-domain reviewed TARAs.

**Operating model.** Agents produce **and cross-check each other** (independent prompts and
contexts; a second model family where Q-17 allows). Humans spend a **fixed, measured budget**:
students ≈ 20 review units/week in total (1 unit ≈ 15 min ≈ one record), the sponsor ≤ 5 h/week
(4 h in M3 week). That budget goes to a gold set (the correctness anchor) and to the few claims
that change what the site displays as fact. Everything else stays hypothesis-badged, and each
edition publishes held / agent-cross-checked / human-reviewed counts and the gold-set error
estimate instead of promising coverage nobody can give (§3.2–§3.4).

**Decisions the sponsor is asked for** (full table §7; recommendations in bold):

| When | Q | Recommendation |
|---|---|---|
| S3 | Q-18 sponsor budget + delegations | **4 h in S3, 5 h/week S4–S7; delegate library record merges (M-b) and issue edits to the agent** |
| S3 | Q-01 merge authority | **One weekly merge window now; M-b for `records/**` from S4** |
| S3 | Q-03 AI as an M4 breadth domain | **No for M4; decide M5 at the Phase 1 gate (S5)** |
| S4 | Q-02 student role | **Budgeted reviewers + one short report section each; SOW-0001 amendment with faculty sign-off** |
| S4 | ADR-0011 (PR #130) | **Ratify or reverse the four delegated decisions; record `reviewed: true`** |
| S4 | Q-04, Q-11, Q-13, Q-14 | **Q1–Q7 as direction only; taxonomies as working vocabulary; DX-AI/1 as optional `threats` keys; #84 gate → §3.4** |
| S5 | Q-08 X account, Q-17 cross-model verifier | **$25/month cap after terms check; second model family if available** |
| S7 | Q-16 post-semester human capacity | **Sponsor states who reviews in Phase 3; plan restates targets from it** |

**Week-1 actions (S2 tail + S3, Oct 27 – Nov 5; zero student hours).**

| # | Action | Owner | Hours |
|---|---|---|---|
| 1 | Merge PR #159 (approved) and library#22 | @nymble | 0.25 |
| 2 | Review + merge the privacy PR (LANES.md 170–179); retitle #36–#39; edit #84 body | agent drafts; @nymble applies | 0.5 |
| 3 | One comment on #71: Q-18, Q-01, Q-03 | @nymble | 0.75 |
| 4 | Read this brief; approve or amend direction | @nymble | 1.0 |
| 5 | 20-reference throughput pilot on A1 (tokens, wall time, defects/reference) | integration agent | agent |
| 6 | `source-ids.yaml`, `ident`, `prefill`, `next`, day-1 harvesters; golden-example drafts; library DX-AI/1 schema PR draft; report split (R0); §10 issue-edit drafts | integration agent | agent |

---

## 1. Status baseline (2026-10-26)

Today is inside I3 (Oct 23–Nov 5). Sprints are one week: S2 Oct 23–29, S3 Oct 30–Nov 5,
S4 Nov 6–12, S5 Nov 13–19, S6 Nov 20–26 (Thanksgiving), S7 Nov 27–Dec 3. M3 demo floor
**Nov 5**, M4 **Nov 19** (ADR-0006 risk; ≥2 domains), M5 **Dec 5** (`.dmg`, docs, demo).

### 1.1 Done

| Asset | State |
|---|---|
| RPT-0014 v0.2.0 | AI-generated, AI-reviewed (46 findings folded); `reviewed: false`; records not yet ingested |
| Corpus | 1,181 sources (812 tier-1, 369 tier-2; 675 papers; 2016–2022 only 196; 285 with a cached PDF); 179 incidents (69 with ATLAS case-study ids); 127 published threat models; 16 candidate `LW-*` weaknesses |
| `attack-catalog.yaml` | 146 AIT, all `hypothesis`; maturity 38 in-the-wild, 42 production-demonstrated, 62 research, 4 theoretical; ids pinned to ATLAS 2026.09, OWASP LLM:2025/ASI:2026, CWE 4.20, NISTAML; 769 AIT→S-id pairs, 459 sources cited by no AIT |
| agentic-mcp lane records | #78, @paria03: 3 `library-record/v1` records (applicability, tags, usefulness, six-section summary), agent-drafted and student-reviewed; PR #117 merged 10-12. No TT, evidence level or catalog ids, so **not** a baseline for DX-AI/1 fields |
| Subset-1 | library#22 (@paria03): 19 agentic/MCP records, open since 10-14; a comment review by @Clovier (10-21) and comments by @kriishnaa-18 (10-23, 10-24); no formal approval; mergeable |
| First AI schema model | PR #159 (RPT-0009 0.3.0, @Maimcghee, **approved, unmerged**): `em-01` EchoLeak; schema gaps AI-1…AI-7 |
| Machinery | Accepted core (ADR-0010), `bin/gen-schema --check`, schema CI (#129); engine path enumeration (#132); `render_report.py`, `render_bibliography.py`, `check_identities.py`, `check_links.py`, `bin/publish-site`; three `rpt0014-*` workflows; the #168 "AI-proposed Assertion → human Review" recipe |

### 1.2 Stalled, and why

- **Four of five lanes produced nothing** (#79–#82): no `calibration/COMPARISON.md`, so the #84
  "five lanes agree" gate cannot be reached; WAVE 2 not started; the 1,088 "later" rows in
  `wave1-assignments.csv` have a lane but no schedule.
- **Library uptake ≈ 0.** About 10 of 1,181 sources are records on library `main`; no
  AI-threats topic exists (`topics/sagai.yaml`, Secure AI, does). NIST AI 100-2 E2025, ATLAS,
  OWASP LLM Top 10 and CoSAI are not records yet.
- **Root causes:** WAVE-1 kickoff (10-07) collided with graded I2 build lanes; a convoy gate
  needing all five lanes; merge latency (library#22 open 12 days); schema gating (#74 not
  restarted after DEC-001a; ADR-0011/0012 still open PRs); friction (two repo roots, per-lane
  quota, a 660 MB PDF cache, hardest-first calibration); redirection (AI work moved to RPT-0009
  part B on 10-21; requirement extraction #168–#172 filed 10-26).

### 1.3 Capacity (measured, not hoped)

| Handle | MVP commitments | AI work state |
|---|---|---|
| @paria03 | #63 Part 2 risk (M4 critical path), #124 / PR #155, #170 | #78 done; library#22 unmerged |
| @kriishnaa-18 | #58, #59 / PR #162 (graph view, M3), #171 | #81: nothing |
| @Clovier | #60 / #138–#142, #61 / #143–#146, #152–#154, PR #130, PR #161, #172 | #80: #134 missed |
| @Maimcghee | #64/#65, #169, PR #158, PR #159, library#21 | #79: nothing; redirected to RPT-0009 part B |
| @nymble (sponsor) | ADRs, merges, M3–M5 integration, #82 | #82: no integration run |

Observed student review throughput on program work is **≈ 20 records/week across all four**
(≈ 5 each, PR comment reviews). That number, not a target, sizes §3.

**Program merge queue:** PR #159, library#22, PR #130, PR #167. Adjacent but not program-blocking:
PR #162 (student M3 build PR) and library#21 (CWE/OTM extractions, relevant to W3's CWE import).

### 1.4 Hygiene items found during the baseline

- **Privacy.** `research/0014-ai-threat-model/LANES.md` on `main`, lines 170–179, carries project
  people's first names (contradicts PR #112). Titles of #36–#39 (#37 is closed) and the body of
  #84 also carry names. Commit-author metadata on `main` carries real names; history is not
  rewritten, and no renderer may read it. `check_identities.py` scans only `docs/**/*.html`.
- **PR #130 / ADR-0011.** The sponsor delegated four decisions to @Clovier on 2026-10-22; they were
  made as recommended (DL-0024 on the PR branch): (1) A1–A7 and B1–B5 accepted in one ADR amending
  ADR-0010; (2) DataFlow joins Components directly, no DFD layer; (3) the five names kept;
  (4) pv-01/pv-02 left unreviewed pending student review. ADR-0011 reads `status: accepted`,
  `reviewed: false`; the PR has only COMMENTED reviews. Nothing is open; what remains is the
  sponsor's ratification (or reversal) and `reviewed: true`.
- **Numbering.** Design-log numbers are already duplicated on `main` (0006, 0011, 0012, 0015);
  0024 is used on `main` and by PR #130; 0025 by PR #167. This plan's entry is DL-0026, shipped in
  the same PR.
- **Stale plans.** PLAN-0001 and BACKLOG-0001 (last updated 10-15) have no AI rows after I1.

---

## 2. Goals and deliverables

| D | Deliverable | Form | Done when (at grade v1.0, §2.1) |
|---|---|---|---|
| **D1** | AI attack catalog v0.3+ — AIT, X01–X16 → 36 classes, incidents, weaknesses, mitigation nodes, pinned crosswalk | one file per entry + link records; derived `attack-catalog.yaml` | Every AIT meets the evidence minima (§4.1.1); every AIT has ≥1 weakness link or a dated "no weakness layer" note; 0 unpinned/deprecated ids; maturity-driving claims human-verified |
| **D2** | Target-type knowledge — TT working vocabulary, reference architectures, domain profiles | `research/0014-*/schemes/` now; schema range only via ADR (Q-05b) | Each TT has ≥10 held sources and a resolvable reference architecture; first 2 profiles reviewed by ≥2 approvers |
| **D3** | Hierarchical report "AI threats today" — L0 → L1 parts → L2 mini-reports → L3 pages | `reports/ai-threats/prose/**` → `docs/ai-threats/**` | §4.4 tree at the grade's scope; every L2 passes `check_prose_ids.py`; numbers from data |
| **D4** | Hierarchical AI bibliography (part of D3) | library records + DX-AI/1 profiles → `docs/ai-threats/bibliography/**` | 100% of **held** references complete (summary + ≥1 category + ≥1 link to an AIT, weakness or incident); held / shown / complete published |
| **D5** | Reproducible multi-domain TARA HTML (SDL artifact) | `docs/tara/<profile>/<run_id>/` + `tara-lock.yaml` + exports | Same lock + pinned toolchain → identical digests in CI; ≥2 domain profiles; one profile also rendered through a second method adapter (§W6) |
| **D6** | Latest-attacks loop incl. X/Bluesky/Mastodon/HN | `tools/rpt0014/harvest-*`, `leads/log.csv` | Weekly run; E3+ items stubbed ≤7 days; X spend ≤ cap |
| **D7** | Adversarial completeness loop | critic rounds, independent holdout, reject logs | Gating axes pass twice, or the timebox closes with gaps published (§W7) |
| **D8** | Coverage and evidence dashboard | `coverage/*.csv` → `coverage.html` | Weekly; every gap row has a mini-report ticket, a dated negative search or an accepted-gap record |

### 2.1 Release bar: edition grades

| Grade | Definition | Earliest |
|---|---|---|
| **draft** | Banner on every page; held / agent-cross-checked / human-reviewed counts and gold-set error estimate shown | S5–S7 (in-semester ceiling) |
| **reviewed-core** | Every L0 and L1 statement, and every claim that makes an AIT display as in-the-wild or production-demonstrated (E4/E5 support), human-verified; gold-set gates (§3.4) pass on all gated fields; D4 completeness 100% of held; one W7 coverage pass | Phase 3 |
| **v1.0 ("professional-grade")** | reviewed-core + a read of L0, Part V (risk phases) and Part VI (target types) by a reviewer outside the project (faculty advisor or an industry reviewer, named by role) + W7 closed (§W7) + ≥2 domain TARAs reproducible in CI + the second-method render | end of Phase 3 at the earliest |

Every edition states its grade on every page. D1–D5 "done" means v1.0; nothing in-semester claims
more than draft.

---

## 3. Operating model

### 3.1 Roles and budgets

| Role | Who | Does | Budget |
|---|---|---|---|
| **Gatekeeper** | @nymble | Rulings, ADR acceptance, one weekly merge window, gold adjudication, human ratings on AI-01 | **4 h in S3, 5 h/week S4–S7 (3 h in S6)** — Q-18 |
| **Integration lane (agent)** | sponsor account A1 | Harvest, identity, triage, L0, V1–V3 checks, coverage, generators, TARA runs, report builds, PR and issue drafts | agent time (bounded by the S3 pilot) |
| **Budgeted reviewers** | @paria03, @kriishnaa-18, @Clovier, @Maimcghee | Gold-set labels, AI-01 Assertions, maturity-claim checks (`kg/reviews/*.yaml`) | 0 in S3; ≈1.25 h (5 units) each in S4, S5, S7; S6 optional |
| **Critic (agent)** | any account other than the producer's | Completeness and clarity rounds | 40 searches per round |
| **External reader** | faculty advisor or industry reviewer (role only) | v1.0 read (§2.1); learning-outcome check (Q-02) | post-semester |

Students do not run distillation batches in-semester; all agent production runs on A1 (a student
may volunteer account quota, never time). Workflows: `rpt0014-extract`, `-sweep`, `-integrate`
(exist); `rpt0014-distill` (extractor + V1 verifier), `rpt0014-critic`, `rpt0014-minireport`
(new). Deterministic tools are Python stdlib under `tools/rpt0014/`, never Node. Headless
(`claude -p`) output carries `review.extracted_by.model` and never counts as reviewed.

### 3.2 Review budget: supply against demand (in-semester)

1 unit ≈ 15 minutes of focused human review ≈ one record, or one Assertion, or one reference
labelled blind on the six gated fields.

| Supply | S3 | S4 | S5 (M4) | S6 | S7 | Total |
|---|---|---|---|---|---|---|
| Students (4) | 0 | 20 | 20 | 0 | 20 | **60** |
| Sponsor (review share of budget) | 0 | 4 | 8 | 4 | 8 | **24** |

| Demand that is funded | Units | Who | When |
|---|---|---|---|
| Golden examples (3) sign-off before any use | 4 | sponsor | S4 |
| Gold set: 30 references labelled blind on the gated fields | 30 | students | S4 (20), S5 (10) |
| Gold overlap: 10 references labelled by a second student (human–human ceiling) | 10 | students | S7 |
| Gold adjudication (human vs pipeline, human vs human) | 6 | sponsor | S6–S7 |
| AI-01: 10 Assertions (each path, top threats, mappings) | 10 | students | S5 |
| AI-01: feasibility and S/F/O/P on 3–4 paths (ADR-0006) | 4 | sponsor | S5 |
| New-AIT proposals, `first_of_kind`, `bears_on` | 4 | sponsor | S5 |
| Maturity-driving claims (E4/E5 support of an in-the-wild AIT) | 16 | students 10, sponsor 6 | S7 |
| **Total** | **84** | | |

**Not funded in-semester (stays hypothesis-badged, carried to Phase 3 under Q-16):** review of
other E3+ items; any percentage sample of TT/AIT/catalog ids beyond the gold set; human review of
every extractor/verifier disagreement (agents adjudicate, §3.3; unresolved items display as
`disputed`); 22 of 38 in-the-wild claims and all 42 production-demonstrated claims; any L2 banner
lift; profile approvals. If supply falls short, the cut order is: maturity claims → gold overlap
→ AI-01 Assertions (to 6); the gold set is cut last.

### 3.3 Verification layers (agents carry the volume; humans anchor correctness)

| Layer | What | Coverage | Status it confers |
|---|---|---|---|
| **V0 mechanical** | Metadata from APIs (never an LLM); catalog-pin rule; locator rule; number rule where cached text exists (else marked `unverifiable`, confidence ≤ medium); quote checker incl. imported catalog text; licence; link liveness | 100% | — |
| **V1 independent re-extraction** | Fresh context, an independently written prompt built from field definitions only; re-extracts **blind**, then a script diffs field by field | 100% of L0 | `ai-proposed`, V1 agreement recorded |
| **V2 cross-model** | Re-extraction by a second model family (Q-17), or at least a different model tier plus a third prompt | 10% random sample + every V1 disagreement on a gated field | `ai-cross-checked` (a display state; still a hypothesis) |
| **V3 adversarial claim check** | A critic agent re-reads the source for each claim that would raise displayed maturity (E3+), resolves CVE/KEV/INC ids, and hunts contradicting evidence | 100% of maturity-driving claims | flags; never accepts |
| **V4 human** | Gold set (correctness anchor) and the funded items in §3.2 | budgeted | `reviewed-*` |

**Correlated error (R15).** V1–V3 on one model family measure consistency, not correctness. Hence:
the gold set is the only correctness estimate, and it is published; V2 uses a second family where
allowed; agent-agent agreement is reported but never gates anything. Sources whose publisher is the
vendor of the affected product or of the model running the pipeline (RPT-0014 §8 item 4) are
tagged `evidence.self_reported: true` and do not raise maturity unless independently corroborated.

**Published honesty line (every edition, every TARA):** held · L0 distilled · V2 cross-checked ·
human-reviewed · disputed, with the gold-set per-field agreement and 95% CI as the error estimate
for unreviewed fields.

### 3.4 Agreement design (replaces the #84 five-lane gate)

- **Gated fields** (the DX-AI/1 fields that drive display): `targets[]` (TT), `attack.ait`,
  `attack.x_class`, `lifecycle` (risk phase), `evidence.level`, catalog ids (ATLAS, OWASP).
- **Golden examples** (3 worked references with "why each field is what it is") define the fields
  and tune prompts. The sponsor signs them off before they are used (S4).
- **Gold set G:** 30 references drawn by script with a fixed seed from the held corpus, stratified
  by source type (paper, CVE/advisory, vendor research, catalog entry, incident report, blog) and
  X-group; never the golden examples. Students label blind to agent output; 10 are labelled twice
  (human–human ceiling). The sponsor adjudicates disagreements. G is scored, never tuned against;
  after one prompt change it may be re-scored once, and a second tuning round needs a fresh
  15-reference extension.
- **Statistics.** Per field: percent agreement (single-valued) or Jaccard (sets) with 95% CI (Wilson
  / bootstrap). Cohen's κ only for `evidence.level`, only with n ≥ 30 and no category above 80%
  prevalence; otherwise a confusion matrix.
- **Comparisons:** human–human (ceiling, n = 10); pipeline (extractor + V1) vs adjudicated G;
  V2 pipeline vs G; agent vs agent on the 10% V2 sample (consistency only).
- **Gate per field:** lower CI bound of pipeline-vs-G ≥ 0.6 **and** point estimate within 0.10 of
  the human–human ceiling. A failing field displays as `unverified field` and gets its definition or
  prompt fixed, not more people. First result: end of S7.
- **agentic-mcp records:** re-run the DX-AI/1 pipeline on their 3 sources (S-0855, S-0166, S-0728)
  in the S3 pilot as a **smoke test** only; it gates nothing.
- **Reviewer calibration** falls out of G (each student's labels vs adjudicated G); no sponsor
  double-check of "first 5 reviews".

### 3.5 Retire the five-lane production model

- #78–#82 remain only as lane labels; their WAVE-2 lists and sweeps are dropped (§10.2).
- Unit = one reference, claimed by `tools/rpt0014/next`. No convoy; a PR with 3 done and 2
  `blocked: <reason>` is a success.
- Students never set `bears_on` or `novelty.first_of_kind`.

### 3.6 Merges: batched and countable (Q-01)

| Option | What | Against |
|---|---|---|
| **M-a** Weekly merge window | Sponsor merges once a week (Friday) from a `merge-ready` label; ≤1 h | Single-threaded |
| **M-b** Delegated library record merges | In Threat-Radar/library, a PR touching only `records/**` with green `bin/validate` + `check-ai-profile` and one approval from the named review partner may be merged by that partner | Branch-protection change |
| **M-c** Generated-path auto-merge | Green CI on PRs touching only `coverage/*.csv`, `leads/log.csv`, rebuilt `docs/ai-threats/**` | Path-filter CI job; never `kg/reviews/`, profiles, `spec/**` |

**Recommendation:** M-a now; M-b ruled in S3 and live in S4; M-c when the coverage job exists.
`spec/**`, ADRs, schemes, profiles and `kg/reviews/` stay sponsor-merged. Claude never merges.
Library stubs are generated deterministically (no LLM) in ≤3 bulk PRs; distilled profiles go in
batches of 25. **Expected volume:** tmodel 2–3 program PRs/week (sponsor window); library 1–3
PRs/week (M-b). Library is a fork of m-of-n/library; program records stay in the fork, and
upstreaming is curated and out of scope.

---

## 4. Workstreams

Every workstream: provenance on outputs (agent, model, date, basis, prompt digest); AI output is
`ai-proposed`; catalog references are (framework, release, id); licensed text paraphrased; GitHub
handles only; identity and link guards in CI; a `design-log/` entry with rejects per PR.

### W0 — Re-baseline and governance

| | |
|---|---|
| **Outputs** | S3: #159 and library#22 merged; privacy PR; #36–#39 retitled; #84 body cleaned; Q-18/Q-01/Q-03 comment on #71. S4: ADR-0011 ratified or reversed with `reviewed: true`, #130 merged, #167 rebased and merged; RPT-0014 §8 Q1–Q7 direction comment (Q-04); issue edits per §10; this plan merged with DL-0026; BACKLOG-0001 AI rows |
| **Method** | Agent drafts every PR, comment and issue edit; sponsor applies (or delegates issue edits, Q-18). #130 then #167, one schema regeneration each |
| **DoD** | Program queue empty; RPT-0014 §8 Q1–Q7 answered as direction or deferred; `check_identities.py` (with the `identities.local.yaml` matcher) extended to renderer inputs (`research/**/*.md`, `reports/**`, generated YAML) and clean on LANES.md, issue titles #36–#39 and #84's body; epic exists |
| **Owner** | @nymble; integration agent |

### W1 — Ingestion and sources (incl. latest-attacks loop)

| | |
|---|---|
| **Purpose** | Turn round 1 into a corpus with **measured** recall, kept current weekly |
| **Outputs** | `tools/rpt0014/{harvest-*,ident,triage,prefill,next,check-ai-profile,coverage,review-queue,x-budget}` (stdlib, `--since`, `--dry-run`); `leads/log.csv` (ids/URLs only); `leads/raw/` (private, not committed); `feeds.yaml`; `social/accounts.yaml` (organisations only in the repo; individuals' handles in a private local list); `coverage/*.csv`; deterministic library stubs for every in-scope item |
| **Method** | discover → identity/dedupe → triage (cheap model, pinned prompt) → ingest record (`bin/ingest` + `prefill`; **no LLM for metadata**) → summarise → distill (W2) → V0–V3 → human (budgeted) → integrate. Identity keys in order: DOI, arXiv id (version-less), OpenReview id, CVE, GHSA, OSV, ATLAS CS, AIID number, post id, OpenAlex/S2 ids; fuzzy title+year+first author only without a strong key. One INC per real-world event |
| **DoD** | Day-1 harvesters (arXiv, cvelist/NVD, KEV, RSS, Bluesky, HN) weekly with cost logging; coverage CSVs regenerate; licence register (§4.1.3) complete for every imported catalog and API |
| **Depends on** | library#22; API keys (OpenAlex, S2, NVD); Q-08 |

#### 4.1.1 Coverage model (gating vs reported)

| Axis | Frame | Target | Gates? |
|---|---|---|---|
| Venue-year recall | Full TOCs (DBLP XML dump; OpenAlex; Crossref; OpenReview v2; ACL Anthology bulk) + in-scope classifier | Top-4 security 2016–26 ≥95% | **gate** |
| | | SaTML 2023–26 ≥95% (≈8% today); second-tier security ≥80%; ML/NLP/CV ≥90% of high-impact `in` items | reported |
| Seed-set recall | NIST AI 100-2 E2025 refs; 73 ATLAS case studies; OWASP LLM/ASI/MCP refs; CoSAI/MAESTRO/SAIF/DASF; 10–12 SoKs fixed at kickoff | NIST ≥95%; ATLAS CS 100% linked | **gate** |
| | | OWASP ≥95%; industry ≥90%; SoKs ≥90% | reported |
| Snowball closure | Backward (cited by ≥3 held), forward (deep tier), Chapman capture–recapture per X-class | held/N̂ ≥0.90 (N̂ a lower bound); branch stops at <3% new | reported |
| Evidence minima | per X-class / per AIT | X-class: ≥1 SoK, ≥1 item ≤6 months, ≥10 primary sources, explicit ITW line. AIT: ≥2 independent primary sources, ≥1 top-venue or vendor/CVE, seminal paper named, pinned mappings, ≥1 weakness link or dated note | **gate** for non-hypothesis display |
| Target-type | TT vocabulary (App. B) | ≥10 held sources per TT; every incident/CVE mapped to ≥1 TT | reported |
| Incident/vuln recall | ATLAS CS; AIID snapshot; OECD AIM sample; AVID; NVD/cvelist vs AI-product strings; KEV; GHSA | KEV AI entries 100%; AVID/NVD/GHSA 100% triaged | **gate** |
| | | AIID ≥85%; OECD ≥70% | reported |
| Freshness | `discovered_at` vs `published_at` | median ≤7 days to stub for E3+, ≤14 for papers | reported |
| Non-English | GDELT, OECD AIM, national CERTs | ≥1 national guidance record per G20 jurisdiction that published one; non-English share of new incidents (≈0% today) | reported |

Any cell closes by meeting target, by a dated negative search, or by a sponsor-signed accepted-gap
record. **Corpus size:** the round-1 memo's 2,800–3,500 is an unsupported placeholder; Phase 2's
venue TOC sweep counts in-scope items per venue-year and replaces it.

#### 4.1.2 Social-signal pipeline

- **X (pay-per-use API; pricing checked 2026-10-26):** $0.005 per post read; narrow recent-search
  shards (curated authors ∧ attack keywords ∧ `has:links -is:retweet`) twice daily ≈ $5–12/month;
  **hard cap $25/month** via `x-budget` and console limits; one sponsor-owned key, never committed.
  Before purchase, Q-08 confirms in X's developer terms that post text may be passed to a
  third-party LLM for triage (and, if the xAI search option is considered, its terms). **The repo
  stores post IDs and URLs only.** No scraping, scraper services or mirrors.
- **Bluesky** (free; `api.bsky.app` searchPosts, lists, Jetstream; 3,000 req/5 min), **Mastodon**
  (infosec.exchange token; mastodon.social public tags), **HN** (Algolia), **GitHub** (repo search,
  awesome-list diffs, GHSA). Reddit deferred; LinkedIn/Discord/Telegram manual only.
- **Corroboration:** a lead becomes a source only when a primary artifact (paper, CVE/GHSA/advisory,
  write-up, code, talk) is fetched and recorded. A write-up by the same poster is not independent
  corroboration. Social-only items: type `web`, `evidence: social-only`, capped at E0–E2, excluded
  from maturity and from E3+ queues; archive the outbound link if any, else record the post ID only;
  re-check in 30 days.
- **Platform metrics (monthly):** leads, % corroborated, % first (≥3 days ahead), cost per new
  source; drop a platform at <5% corroboration or no "first" in 8 weeks.

#### 4.1.3 Licence register (catalogs and APIs)

Each catalog lock and API entry records `licence`, `redistribution` (full | ids+names+paraphrase |
ids only) and `attribution`. Permissively licensed catalogs may republish entry text with
attribution (the register must confirm, e.g., ATLAS data's licence and NOTICE; OWASP GenAI's
share-alike terms; CWE terms of use; AIID data licence). Catalogs without an open licence (e.g. CSA
MAESTRO and CSA guides) store ids, names and paraphrases only. API terms bind derived data (e.g.
Semantic Scholar TLDRs are not republished). The quote checker covers imported catalog
descriptions. Unconfirmed entries default to ids+names+paraphrase.

### W2 — Distillation (DX-AI/1) and tiering

| | |
|---|---|
| **Purpose** | Every reference says *what is attacked, how, at what phase, with what evidence, linked to which catalog ids, weaknesses and artifacts* |
| **Outputs** | `records/<body>/<id>/distilled/ai-profile.yaml` (library side) + `verify.md`; golden examples; gold set G; one small library schema PR (Q-13; field list App. A) |
| **Method** | Extractor + V1 at the effort the S3 pilot shows is sufficient (start medium for L0); deep tier at max, one unit at a time. Script rules: locator (every `stated` value has a locator, else `inferred`); number (headline number grep-matches cached text; no cache → `unverifiable`, confidence ≤ medium); catalog-pin (un-suffixed OWASP ids and ids absent from the pinned release rejected); quote (>50 verbatim words from a non-permissive source flagged) |
| **Tiers** | **L0** agent-only, confidence ≤ medium, ordered by tier score (App. A.3), volume bounded by the pilot; **L1** = human-reviewed (in-semester: G + funded maturity claims, ≈45); **deep** FX-AP/FX-TM, ≈10–15 in-semester, agent-run, sponsor-sampled |
| **Taxonomies** | TT (App. B) and risk phases (App. C) are a **working vocabulary**, versioned in `research/0014-ai-threat-model/schemes/` with a remap script; frozen as research labels at end of S4 (Q-11). They become a schema range only through the Q-05b ADR |
| **DoD** | `check-ai-profile` passes on every profile; §3.4 gates reported; HYPOTHESIS badge wherever `reviewed_by` is empty |
| **Throughput** | Restated from the S3 pilot (tokens, wall time and defects per reference; per-account weekly capacity from the usage meter). The draft's 60–120k tokens/reference and "5–8 agent-days" for AI-01 are estimates to be replaced |

### W3 — Threat-knowledge layer (proposal to ARCH-0001, not a design here)

| | |
|---|---|
| **Purpose** | Make catalog, targets, incidents, references and links queryable and reviewable without copying generic knowledge into product models |
| **Outputs** | `spec/ARCH-0001-PROPOSAL-threat-knowledge.md` (a diff against ARCH-0001) + proposal LinkML module + vectors `ai-01` (one AIT end-to-end), `ai-02` (Rule-of-Two fixture), `ai-03` (catalog drift alias); then the knowledge-layer ADR (next free number) under a new DEC id; `source-ids.yaml` (S-id → library id, needed now). Migration (`bin/kg-migrate-rpt0014`) and catalog importers only after the ADR accepts |
| **Summary of the proposal** | Two layers joined by typed, reviewable bridge edges (the DEC-009 seam); reuse core types (AIT as `AttackPattern`, weaknesses as `Weakness`, controls as `Mitigation` `stated_as` a family `Requirement`); bibliography links as evidence Assertions; maturity derived from incidents, never authored; catalog references version-pinned. The sketch is in Appendix E, **input to the ADR draft, not a decision** |
| **DoD** | Proposal module validates; vectors pass `linkml-validate`, `check-refs.py`, `check-edges.py`; the R-018 gate is enforced by the integrity checker |
| **Depends on** | #130 and #167 merged; #74 restarted as home for AI-1…AI-7 + SR-I1…I10; loader #139–#142; Q-05, Q-06, Q-07, Q-10 |

### W4 — Reports (mini-reports → parts → final reports)

| | |
|---|---|
| **Outputs** | `reports/ai-threats/prose/<scope>/<id>.md` (ids in brackets; numbers as placeholders); `docs/ai-threats/**`; `render_report.py` extensions (include/placeholder expansion, anchors + TOC, breadcrumbs, inline SVG, id-link rewriting); `check_prose_ids.py` |
| **Method** | Each L2 page = prose fragment + generated sections (techniques, assets, incidents, mitigations, crosswalk, references by role, backlinks) + evidence-state box. Diagrams pre-rendered to inline SVG with Graphviz (no browser scripts, no Node). **Synthesis step:** L1 part syntheses and L0 findings are agent drafts built from the L2 evidence boxes, then a sponsor read, recorded in the design log; includes alone do not count as roll-up. **Gap loop:** every failing coverage row or critic must-have cluster becomes an L2 ticket, a negative search or an accepted gap |
| **Editions** | One edition per term plus a monthly "what changed" delta page; every page shows grade, as-of date, KB commit, library pin and catalog releases. Page budget: in-semester draft ≤ 30 pages (L0, 13 L1 introductions, 10 risk-phase L2s, 4–6 gap L2s); later editions per Q-16 |
| **DoD (per edition)** | All L1 parts present at the edition's scope; each L2 passes `check_prose_ids.py` and `check_links.py`; banner and evidence-state box on every page with ai-proposed content; sponsor reads L0 (draft) or L0 + L1 introductions (reviewed-core and above) |
| **Depends on** | R0 split needs nothing; generated sections need W3 or a YAML fallback; PLAN-0003 A1a |

#### 4.4.1 Proposed report tree

```
L0  AI Threats Today — overview (1 page): findings · risk-by-phase heat table ·
    top in-the-wild techniques per target type · what changed since last edition
L1  Part I    Landscape, scope and method (scope per Q-04; method; evidence levels; coverage statement)
    Part II   Reference architecture, assets and harms (C01–C21, TB1–TB14, A01–A18; dangerous
              compositions; harm and impact categories)
    Part III  Actors and capabilities (attacker positions, knowledge, RAND-style capability tiers)
    Part IV   Attack taxonomy and catalog (one L2 per class group X01–X16)
    Part V    Risk phases: design · supply chain · data · development (incl. evaluation and
              red-teaming) · deployment · inference · agentic operation · platform ·
              human and organisation · retirement
    Part VI   Target-type profiles (by family, App. B)
    Part VII  Incidents and patterns (P1–P8)
    Part VIII Defenses and controls; regulatory and standards crosswalk (EU AI Act, NIST AI RMF,
              ISO/IEC 42001 and 27090; licensed previews only)
    Part IX   Catalogs and enumerations (crosswalk, drift, weaknesses, CWE 5.0 watch)
    Part X    Threat-model methods (127 published models)
    Part XI   Domain TARAs (links to docs/tara/…)
    Part XII  Bibliography (§W5)
    Part XIII Gaps and open questions
L2  per class group/class · per phase (10) · per target type · per pattern · per control family · gaps
L3  AIT · INC · TM · weakness · catalog entry · Reference (→ library record page)
```

**In-semester L2 set:** the 10 Part V phase pages and 4–6 gap pages from: coding/CI-agent
compromise; MCP servers and skills as supply chain; model-file deserialisation and hub hijack;
RAG and memory poisoning; AI infrastructure exploitation (KEV-listed MLflow, Ray, n8n, Langflow);
denial of wallet and LLMjacking. **Final reports:** the full edition; a practitioner edition (L0 +
Parts II, V, VI, VIII); per-domain annexes bound to each TARA run — one KG, one bibliography.

### W5 — Bibliography (hierarchical, distilled, linked)

| | |
|---|---|
| **Outputs** | Library topic `ai-threats` with subtopics per X-class group (PLAN-0003 A2); `docs/ai-threats/bibliography/**` from an `ai-bibliography.yaml` manifest on the library's generators (A3); an "AI threat context" block per record page; `check_kg_coverage.py` |
| **Views** | Seven `<details>` hierarchies (no JS), membership derived from evidence links: (1) attack class → AIT → references by role; (2) **weakness (CWE, `tr-weak`/`LW`) → AIT → references**; (3) target-type family → type; (4) risk phase; (5) source type; (6) year; (7) catalog |
| **Entry row** | Citation · one-line summary (interim summaries badged `AI-written, unreviewed`) · category chips · artifact links · status · review state · confidence |
| **Completeness (CI)** | Denominator = **held** corpus (round 1 + round 2). A reference is complete with a summary, ≥1 category and ≥1 link to an AIT, weakness or incident. The coverage page publishes held / shown / complete, sources cited by no AIT, AIT without references, AIT without a weakness link. Warnings for draft editions; **the build fails** for any edition graded reviewed-core or above if a held reference is incomplete |
| **Depends on** | W1, W2, W3; PLAN-0003 A1a, A2, A3, B1 |

### W6 — TARA generator and domain profiles (SDL artifact)

| | |
|---|---|
| **Outputs** | Phase 1: `research/0014-ai-threat-model/gen/` (deterministic: profile → C/TB/A → AIT by component overlap and maturity → stubs, every edge a `proposed` Assertion), `models/ai-01-llm-agent.yaml`, `docs/publishing/render_tara.py`. Later: profiles with review overlays; the `tara` pipeline; `docs/tara/<profile>/<run_id>/` |
| **Pipeline** | S0 resolve + lock (`tara-lock.yaml`: profile, KB commit, catalog releases + hashes, library commit, overlay, **toolchain pinned by version and hash** — Python, Graphviz, LinkML) → S1 instantiate → S2 assets/damage (21434 cl. 15.3) → S3 threat scenarios (method adapter) → S4 impact → S5 paths (engine) → S6 feasibility → S7 risk (#63 Part 2) → S8 treatment → S9 validate (incl. R-018 gate) → S10 emit (HTML, CSV/JSON-LD/GraphML, `provenance.json`, `SHA256SUMS`) → S11 semantic diff |
| **Reproducibility** | No model call inside the pipeline; canonical serialisation; no wall-clock or paths; `tara --check <lock>` in CI rebuilds in the pinned environment and compares digests. A tools-only change that alters digests fails CI until `tara --rebaseline` records the new digests with a design-log entry |
| **Priors ≠ ratings** | Profile priors are `ai-proposed`, shown in a "suggested" column; ratings come only from the human overlay (ADR-0006); maturity shown beside feasibility, never folded in (Q-10) |
| **Multi-SDL test** | Phase 3 deliverable: one profile rendered through a second S3 adapter (STRIDE-on-DFD or MAESTRO layers) with the same output contract; CI checks both runs validate against the same schema and share S0–S2/S4–S11 output structure |
| **Domains** | `dp:enterprise-llm-agent` (Phase 1/3); `dp:automotive-perception` (Phase 3); then `dp:coding-assistant`, `dp:biometric-kyc`, `dp:ml-platform` |
| **SDL hookup** | MAP-0001 row 3 (TARA work products + `provenance.json`), row 2 (family Requirements in `treatment.html`), row 7 (supply-chain threats by ownership scope), row 15 (once DEC-001b accepts, a Gate validates `approval_digest = graph_sha256`) |
| **Depends on** | #130 (or its proposal container); #63 Part 2 for S7; Q-03, Q-06, Q-09 |

### W7 — Review loops (completeness, clarity)

| | |
|---|---|
| **Coverage round** | A fresh critic on a non-producer account, without our coverage CSVs, 40 searches + paper-API scripts; grades must-have (top venue, ≥50 citations, catalog/seed-cited, ITW incident, KEV/flagship CVE) vs nice-to-have; reports yield per search |
| **Independent holdout** | 60 items drawn at Phase 3 kickoff from frames the harvesters do **not** use: practitioner talks (Black Hat, DEF CON AI Village, USENIX Enigma), vendor and research blogs outside `feeds.yaml`, expert-nominated lists, social leads; stratified by X-class and TT; sponsor picks the frames, a script samples with a fixed seed and emits only hashes, held outside the repo until round end. Frames are added to the harvesters after reveal |
| **Clarity round** | A fresh reader-critic per L1 part: claims cite ids; numbers are placeholders; every L2 states scope, evidence state and "none found" lines; readable by a practitioner |
| **Pass** | Coverage: all **gating** axes (§4.1.1) met; critic ≤5 must-haves per 1,000 held at a 40-search budget; holdout ≥54/60 with all must-haves. Clarity: no blocking defect on any L1 part |
| **Stop** | Two consecutive passes end broad discovery. **Timebox:** at the end of Phase 3 (2027-02-28) broad discovery stops regardless; open cells are published as known gaps in the coverage statement. The weekly loop and quarterly critics continue |
| **On fail** | Each must-have becomes a query, venue or channel added to the harvesters |
| **Cadence** | Round 1 (critic only, no holdout) in S7; then every 2 weeks in Phase 3; quarterly after |

---

## 5. Phases and calendar

| Phase | Window | Content | Exit gate |
|---|---|---|---|
| **0 Re-baseline** | Oct 27 – Nov 5 (S3); sponsor ≤4 h + agent; zero student hours | Week-1 actions (§0); harvesters, `ident`, `prefill`, `next`, `check-ai-profile`; pilot; golden-example drafts; library schema PR draft; working-vocabulary drafts; R0 report split | #159 and library#22 merged; privacy fix merged; Q-18, Q-01, Q-03 ruled; pilot reported; harvesters log runs |
| **1 Vertical slice (AI-01)** | Nov 6 – 19 (S4–S5); parallel to M4, off the M3 path | ADR-0011 ratification and #130/#167; generator + AI-01 vector; 3–4 grounded paths (EchoLeak from em-01, MCP tool poisoning, coding-agent CI RCE, memory poisoning); Rule-of-Two query (SR-I5); V3 check; `render_tara.py`; gold set labelling | AI-01 validates; paths enumerate; 10 Assertions human-reviewed; feasibility and S/F/O/P human-set; TARA HTML published as draft; lock rebuild identical; Q-03 ruled for M5 |
| **2 Breadth** | Nov 20 – Dec 3 (S6–S7), continuing | Catalog v0.3 drafts; deterministic stubs for all RPT-0014 sources; L0 by tier score; ≈10–15 deep units; top-4 + SaTML TOC sweep; seed recall; critic round 1; first `coverage.html`; draft edition; gold-set result; Q-05/06/07 proposal drafts | Every RPT-0014 source ≥ stub with summary + tags; coverage CSVs weekly; critic round 1 logged; gold-set agreement published; any shortfall against §3.2 or W2 throughput goes to the sponsor for a ruling (not self-restated) |
| **3 Consolidation** | Dec 2026 – Feb 2027 | ADRs; migration and importers; holdout; snowball; ML/NLP sweeps; non-English pass; critic rounds; full tree; two profiles reviewed; `tara` S0–S11; second-method render; external read | reviewed-core edition; W7 closed by pass or timebox; ≥2 domain TARAs reproducible in CI |
| **4 Steady state** | from ≈ Mar 2027 | Weekly latest-attacks loop; daily KEV/cvelist alerts; monthly catalog re-pin with remap; quarterly critic; TARA re-runs with `diff.html` | Freshness held; each edition carries its grade and coverage statement |

**Milestone guard.** Nothing is on the M3 path. In M4 week (S5) students give only their 5 review
units (≈1.25 h); no student runs agent batches in-semester. M5 uses AI-01 only if Q-03 says so.
**Fallback when sponsor time runs short:** slip critic round 1 and gap mini-reports first, then
maturity-claim checks, then AI-01 publication; never slip the privacy fix or merges that unblock
graded student work.

---

## 6. Task distribution — next three sprints

| Sprint | @nymble (budget) + A1 agent | Each student |
|---|---|---|
| **S3** Oct 30–Nov 5 (M3) | **4 h:** week-1 actions 1–4 (§0). **Agent:** pilot, tooling, golden drafts, library schema PR draft, vocabulary drafts, R0 split, §10 issue drafts, #130/#167 rebase notes | **None** (M3) |
| **S4** Nov 6–12 | **5 h:** ratify/reverse ADR-0011, merge #130 then #167 (1.5); Q-02, Q-04, Q-11, Q-13, Q-14 (1); golden sign-off (1); merge window (0.5); keys (0.25); issue edits or delegation (0.5). **Agent:** AI-01 generator + vector + paths; G drawn by script; L0 batch 1; M-b protection change drafted | **5 units:** label 5 gold references blind (@paria03, @kriishnaa-18, @Clovier, @Maimcghee) |
| **S5** Nov 13–19 (M4) | **5 h:** AI-01 feasibility + S/F/O/P (1); new-AIT/`first_of_kind` rulings (1); Phase 1 gate + Q-03 for M5 (0.5); Q-08, Q-17 (0.5); merge window (0.5); slack (1.5). **Agent:** V3, `render_tara.py`, TARA HTML, `tara --check`; stubs bulk PR 1; L0 batch 2 | **5 units:** 2–3 more gold labels + 2–3 AI-01 Assertions (agentic paths: @paria03; supply chain + CWE nodes: @Clovier; catalog mappings: @Maimcghee; top threats: @kriishnaa-18) |

S6 (Thanksgiving): sponsor 3 h (adjudication, merge window, proposal read); students optional. S7:
students 5 units (gold overlap + maturity claims); sponsor 5 h (adjudication, maturity claims,
critic round 1 read, L0 read for the draft edition, Q-16). If a student's MVP issue slips, their row drops to zero that sprint
without penalty and the cut order in §3.2 applies.

---

## 7. Decisions required (open; this plan accepts none)

| Q | Question | Recommendation | Vehicle | When |
|---|---|---|---|---|
| **Q-01** | Merge authority | M-a weekly window now; M-b for library `records/**` from S4; M-c later; spec, ADRs, schemes, profiles, reviews stay sponsor-merged | Ruling; library branch protection; PROC-0001 amendment | S3 |
| **Q-02** | Student role | Budgeted reviewers (§3.2) + one short report section each as the learning outcome | SOW-0001 §4 amendment with faculty sign-off | S4 |
| **Q-03** | AI as MVP breadth domain | No for M4; decide M5 at the Phase 1 gate; if yes, ADR-0002 amendment | Ruling / ADR | S3, S5 |
| **Q-04** | RPT-0014 §8 Q1–Q7 | Q1 techniques + an `uplifts` edge to ATT&CK; Q2 non-adversarial failures as AttackPatterns with `intent ≠ adversarial`; Q3 one Weakness (CWE-1427) + channel AITs; Q4 version-pinned catalog layers (Q-06); Q5 one local namespace (Q-07); Q6 `dp:enterprise-llm-agent` first; Q7 A17/A18 in scope via customer-chatbot and biometric-KYC | Comment on #71 labelled **"direction only; DEC-008 and schema changes are accepted only by ADR"** | S4 |
| **Q-05** | Threat-knowledge layer | ARCH-0001 PROPOSAL diff → ADR under a new DEC id (DEC-012 is free); module-vs-one-file rule (ADR-0010) ruled explicitly | PROPOSAL → ADR | Phase 2–3 |
| **Q-05b** | AI-1…AI-7 + SR-I1…I10 | One ADR-0010 amendment proposal in #74 after #130 and #167; whether `component_kind`'s range is a concept scheme is decided there | #74 → ADR | Phase 3 |
| **Q-06** | ADR-0007 catalog-layer import | Amend ADR-0007: pinned read-only catalog layers, each with a MAP and round-trip vector; licence register per layer (§4.1.3) | ADR | Phase 3 |
| **Q-07** | DEC-008: catalogs and weakness ids | Cached pinned mirror. Weakness ids keep PLAN-0002's convention (`cwe-79`, `tr-weak-NNNN`); the release pin lives on the catalog reference (`cwe@4.20:CWE-1427` as a `CatalogEntry` key with an alias to `cwe-1427`); `LW-*` become permanent aliases of `tr-weak-*` | ADR | Phase 3 |
| **Q-08** | X account | Sponsor-owned pay-per-use, $25/month cap, after the terms check (§4.1.2) | Ruling (billing) | S5 |
| **Q-09** | DEC-009 generic → product | Interim: Assertions + `Product.classifications` string; no new class before DEC-009 | ADR | Phase 3 |
| **Q-09b** | DEC-001b governed TARA | C1 widen `Review.reviews` to Node; C2 `approval_digest := graph_sha256`; until then HTML snapshot + tag + lock | ADR | Phase 3 |
| **Q-10** | ADR-0006 follow-up | Priors only as `ai-proposed`, display-only; maturity beside feasibility; resolve SR-R4 before #63 Part 2 is used in a TARA | ADR | Phase 3 |
| **Q-11** | Taxonomies | Merged TT vocabulary (App. B) and 10-phase scheme (App. C) as **working vocabulary, not schema**, frozen as research labels at end of S4 | Ruling | S4 |
| **Q-12** | Canonical knowledge location | `kg/` (location only) | Ruling | Phase 3 |
| **Q-13** | Library schema for DX-AI/1 | Optional keys on `threats` + an `ai_profile` header | Library PR | S4 |
| **Q-14** | #84 gate | §3.4 agreement design; #84 keeps partition/storage questions | Sponsor edit of #84 | S4 |
| **Q-15** | Deep-tier scope | ≈10–15 this term, rest next term, stated up front | Ruling | S4 |
| **Q-16** | Post-semester human capacity | Sponsor states who reviews in Phase 3 and how much; the plan restates reviewed-core and v1.0 dates from it | Ruling | S7 |
| **Q-17** | Cross-model verifier (V2) | A second model family if one is available with acceptable terms and cost (data stays within licence terms); else a different Claude tier + independent prompt, reported as consistency only | Ruling | S5 |
| **Q-18** | Sponsor budget and delegations | 4 h S3, 5 h/week S4–S7, 3 h S6; delegate library record merges (M-b) and the §10 issue edits (agent applies an approved list) | Ruling | S3 |

---

## 8. Metrics and gates

| Area | Metric | Target | Where |
|---|---|---|---|
| Coverage | Gating axes (§4.1.1) | met, or closed by negative search / accepted gap; timebox end of Phase 3 | `coverage/*.csv` |
| Completeness | Critic must-haves per 1,000 held (40-search budget); yield per search | ≤5; reported | W7 log |
| Completeness | Independent holdout recall | ≥54/60; all must-haves | W7 log |
| Evidence | AIT meeting minima incl. weakness link | 100% of AIT displayed as non-hypothesis | `technique-evidence.csv` |
| Bibliography | Complete / held | 100% for reviewed-core; reported for draft | `check_kg_coverage.py` |
| Review | Held · L0 · V2-checked · human-reviewed · disputed | published per edition and per TARA; no promised ratio | evidence-state boxes |
| Review | Funded human units delivered (§3.2) | reported weekly with the cut applied | `review-queue` |
| Accuracy | Gold-set per-field agreement (pipeline vs adjudicated G; human–human) | lower 95% bound ≥0.6 and within 0.10 of human–human | §3.4 report |
| Integrity | Unpinned or deprecated catalog ids; `accepted` without Review; AI-authored Review | 0 | checkers |
| Integrity | Verbatim >50 words from non-permissive source (incl. catalog text) | 0 | quote checker |
| Privacy | Identity-guard hits in published pages and renderer inputs | 0 | `check_identities.py` |
| Reproducibility | Same lock + pinned toolchain → same digests | identical; rebaseline only with a DL entry | CI |
| Freshness | Median days to stub (E3+ / papers) | ≤7 / ≤14 | `freshness.csv` |
| Flow | Program PR merge latency | ≤ one merge window (≤7 days) | PR timestamps |
| Cost | X spend; WebSearch | ≤$25/month; ≤120/week/account + 40 per critic round | logs |

---

## 9. Risks and mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | Unreviewed AI output presented as analysis (R-018) | Proposed-by-default; derived badges; banner; edition grades; published honesty line |
| R2 | Citation/fabrication at scale (round 1: wrong ids, 39 deprecated ATLAS ids, OWASP drift) | Metadata from APIs; pinned-catalog validator; number rule (unverifiable without cache); V1–V3 |
| R3 | Schema churn — #130, #167 and the knowledge-layer ADR all amend DEC-001a | Sequence #130 → #167 → proposal; Phase 1 validates against proposal containers |
| R4 | Sponsor time is the single point of failure | Stated weekly budget (Q-18); delegations; batched merges; fallback order (§5) |
| R5 | Learning outcome if agents produce everything | Gold labelling teaches the schema; one report section each; SOW amendment (Q-02) |
| R6 | Quota/tokens | S3 pilot; tier-score order; L0 at the lowest effort the pilot supports; one deep unit at a time |
| R7 | Prompt injection against extraction tooling (SR-I9) | Pipeline never writes accepted state; agents never write `kg/reviews/`; V1 on fresh context; no social text in repo |
| R8 | Licensing of vendor/journal/standards text | Paraphrase; ≤2 sentences verbatim with locator; ISO/IEC via licensed previews; no third-party PDFs committed |
| R9 | Privacy | W0 fixes; guard extended to renderer inputs; renderers never read owner fields, reviewer handles, design-log or commit authorship; individuals' social handles kept private |
| R10 | Platform terms/cost (X, Reddit, AIID, DBLP) | Official APIs with caps; IDs-only storage; terms checks (Q-08); snapshots and dumps |
| R11 | Taxonomy churn mid-round | Working vocabulary frozen as research labels at end of S4; remap scripts |
| R12 | Discovery bias | Separate channels; N̂ as lower bound; blind critic; holdout from non-harvested frames |
| R13 | M-b misused | `records/**` only, green validators, named partner, weekly sponsor audit |
| R14 | Determinism drift | Toolchain pinned in the lock and CI; explicit rebaseline |
| R15 | **Correlated model error and self-assessment** — every agent stage shares a model family; the corpus includes the model vendor's own threat reports | Gold set as the correctness anchor; V2 cross-model where allowed (Q-17); agent-agent agreement never gates; `self_reported` evidence excluded from maturity unless corroborated |
| R16 | **Catalog and API licences** — imported entries republished as HTML | Licence register (§4.1.3); ids+names+paraphrase by default; quote checker on catalog text |
| R17 | **Stop criteria never met** | Gating vs reported axes; accepted-gap records; Phase 3 timebox |

---

## 10. Proposed issue structure (to be created on approval)

### 10.1 Epic and sub-issues

**Epic: #71 re-scoped** — "AI threat program (PLAN-0004)"; DoD = D1–D8 at the grades in §2.1.

| # | Title | Depends on |
|---|---|---|
| E1 | W0: re-baseline — merges, ADR-0011 ratification, Q1–Q7 direction, privacy, issue cleanup | — |
| E2 | W1a: ingestion tooling + day-1 harvesters + S3 pilot | E1 (library#22) |
| E3 | W1b: coverage model (gating vs reported) + licence register | E2 |
| E4 | W1c: latest-attacks loop incl. social signal | E2, Q-08 |
| E5 | W2a: DX-AI/1 — library schema PR, golden examples, `rpt0014-distill` (extractor + V1) | E2, Q-13 |
| E6 | W2b: gold set and agreement design; V2/V3 (replaces #84 gate) | E5, Q-17 |
| E7 | W2c: L0 / deep batches by tier score | E5, E6 |
| E8 | W3a: ARCH-0001 PROPOSAL diff, proposal module, vectors ai-01..03 | #130, #167; #74 |
| E9 | W3b: migration + catalog importers | E8 accepted; Q-06, Q-07, Q-12 |
| E10 | W6a: AI-01 vertical slice | E1; #130; #63 Part 2 for risk |
| E11 | W6b: `tara` pipeline, lock, `--check`, `--rebaseline`, diff, second-method adapter | E10, E9 |
| E12 | W6c: domain profiles | E11, Q-09 |
| E13 | W4a: report split (R0) + renderer extensions + `check_prose_ids.py` | E1 |
| E14 | W4b: L2 mini-reports (phase pages + gap queue) | E13, E3 |
| E15 | W4c: editions, synthesis step, delta pages | E14, E12 |
| E16 | W5: hierarchical bibliography (7 views) + `check_kg_coverage.py` | E5, E8 |
| E17 | W7: critic rounds, independent holdout, reject logs | E3, E13 |

### 10.2 Existing issues

| Issue | Action | Note |
|---|---|---|
| #71 | Keep → epic | Rewrite DoD; RPT-0014 §8 Q1–Q7 direction |
| #73 | Re-scope | Agent-run FX-TM of ≈10 machine-readable catalogs first |
| #74 | Re-scope | Home for AI-1…AI-7 + SR-I1…I10 (Q-05b); parent of E8 |
| #75 | Keep | KG load; parent of E9 |
| #78 | Close when library#22 merges | Lane label kept |
| #79, #81, #82 | Supersede | Point to E5–E7 / E17 |
| #80, #134–#137 | Convert | #134 drop; #135/#136 close; #137 → gold-set labelling |
| #84 | Re-scope | §3.4 replaces the five-lane gate; keep partition/storage; remove names |
| #86 | Keep | Bibliography parent; DoD per §W5; parent of E16 |
| #87 | Keep | Publication umbrella; add AI report and TARA outputs |
| #104 | Close or narrow | To per-object extraction vectors incl. AI |
| #63 | Keep (critical path) | Part 2 risk unblocks TARA S7 |
| #168, #170 | Keep | #170 = AI controls layer, reused for `stated_as` in profiles |
| #20, #14 | Close | Superseded (ADRs; ADR-0006, residue in library#35) |
| #15, #17 | Close or link | Superseded by ADR-0010/0011/0012 |
| #19 | Fold | Into #168 / DEC-001b |
| #50–#54 | Close as superseded | ADR-0004/0008; #51 dup of #60/#142; #52/#53 overlap #65 |
| #5 | Close or narrow | Largely delivered (library#14–#19) |
| #36, #37, #38, #39 | Retitle | Remove personal names (#37 is closed; retitle anyway) |

---

## Appendix A — DX-AI/1 distillation profile (input to the library schema PR, Q-13; moves there when it opens)

### A.1 Fields

| Field | Content | Filled by | Mechanical check | Human |
|---|---|---|---|---|
| bibliographic, identifiers, sha256, licence | from APIs | APIs, not the LLM | validator; DOI/arXiv resolve | — |
| `contribution_kind` | attack · defense · measurement · benchmark · survey/SoK · threat-model · catalog · incident-report · advisory · tool · position | agent | enum | — |
| `targets[]` ★ | TT code + `product_examples` + locator + `stated`/`inferred` | agent, V1, V2 | enum; locator when `stated` | gold set |
| `modality`, `deployment` | text…sensor; provider-hosted…n/a | agent | enum | — |
| `lifecycle` ★ | primary `ai-risk-phase` + optional secondary phases | agent, V1 | enum | gold set |
| `attack.ait`, `attack.x_class` ★ | existing ids or `proposed: "<name>"` | agent, V1, V2 | id exists | gold set; sponsor for `proposed` |
| `attack.atlas/owasp/nist_ai_100_2/cwe/other` ★ | versioned ids (OWASP year-suffixed) | agent, V1 | id in pinned release | gold set |
| `attacker.*` | position, knowledge, capabilities, cost | agent | enum | deep sample |
| `preconditions`, `impact.*` | list; CIA+; A-ids; one number + locator | agent | number rule | deep sample |
| `evidence.level` ★ | E0 theoretical · E1 simulation · E2 offline real model · E3 production demo/disclosed · E4 CVE/advisory · E5 exploited ITW | agent, V1, V3 | E4 needs a CVE; E5 needs INC or KEV | gold set; funded maturity claims |
| `evidence.self_reported` | publisher is the affected vendor or the pipeline's model vendor | agent | publisher match | — |
| `evidence.against/incidents/cves/reproducibility` | named systems; INC; CVEs; code-released…none | agent | ids resolve | — |
| `mitigations.evaluated/proposed` | name, result, locator | agent | — | — |
| `artifacts.*` | URL, licence, `checked` date | agent + GitHub/Zenodo/HF search | liveness; licence | — |
| `novelty.*`, `bears_on` | first_of_kind, builds_on; DEC/R ids | suggest only / never | ids exist | sponsor only |
| `confidence` | low/medium/high | agent proposes | ≤ medium if `inferred` without locator, abstract-only, or number unverifiable | human final |
| `review.*` | extracted_by, verified_by (V1/V2 with model), reviewed_by | auto | — | empty `reviewed_by` = hypothesis |

★ = gated field (§3.4).

### A.2 Deep-tier score

```
score = 3·seminal + 2·catalog_cited + 2·evidence(E5=2, E4=1.5, E3=1) + 1.5·sole_source
      + 1·log10(1 + citations/age_years) + 1·top_venue + 1·artifact + 1·recency(≤6 mo ∧ E3+)
      − 2·superseded − 1·self_reported_only
```

Long-run quotas (post-semester): seminal paper per AIT; FX-TM for the top 40 threat models and
catalogs; ≈20 SoKs; ≈30 E4/E5 write-ups; floors ≥5 deep per X-class and ≥3 per TT with E3+
evidence.

---

## Appendix B — Target-type working vocabulary (TT v1; research labels, not schema — Q-11)

A target is the **product type attacked**, distinct from asset class (A-ids) and component (C-ids).
**Id policy:** `TT01…TT27` are the only target-type ids; family names are `broader` labels used as
Part VI headings; `dp:*` ids name domain profiles only, each a composition of TTs plus ownership
scope and assets. Memo C's `tt:*` ids are not used.

| Family | TT | Target type | C-map |
|---|---|---|---|
| Model producers and ML platforms | TT01 | Hosted foundation model / model API | C13, C05 |
| | TT02 | Open-weight model checkpoint | C04, C05 |
| | TT03 | Fine-tuned / adapted model | C03, C04 |
| | TT13 | Model, dataset or prompt hub / registry | C04 |
| | TT14 | ML/LLM frameworks, libraries, serialisation formats | C04, C14 |
| | TT15 | Training-data pipeline | C01, C02, C03 |
| | TT16 | Federated / collaborative / split learning | C03, C05 |
| | TT17 | Inference serving, MLOps/LLMOps, AI gateway | C05, C15, C18, C19 |
| | TT18 | Accelerator / GPU / memory / TEE hardware | C15 |
| AI-enabled applications | TT06 | LLM chat app / copilot / assistant | C07 |
| | TT07 | RAG / enterprise search / knowledge assistant | C06 |
| | TT08 | Tool-using autonomous agent and agent memory | C08, C10, C11 |
| | TT09 | Coding assistant / coding or CI agent | C08, C14 |
| | TT10 | Computer-use / browser agent | C20 |
| | TT11 | Multi-agent system / agent-to-agent protocol | C08 |
| | TT12 | MCP server, tool, plugin, skill, marketplace | C09 |
| | TT24 | Recommender, ranking, search, LLM-as-judge | C05, C07 |
| Predictive and perception ML | TT04 | Predictive ML model | C05 |
| | TT05 | Security ML and guardrails | C05, C18 |
| | TT21 | Biometric and identity verification | C16, C05 |
| Edge and embodied AI | TT19 | Edge, embedded, on-device AI | C16 |
| | TT20 | Autonomous vehicle, drone, robot perception and control | C16 |
| | TT22 | Speech / voice assistant interfaces | C16, C07 |
| Generative media and provenance | TT23 | Vision, multimodal, generative media models | C05 |
| | TT25 | Content provenance, watermark, deepfake detection | C05 |
| The organisation as target | TT26 | People and organisations targeted by AI-enabled offense | C12 |
| | TT27 | Conventional IT attacked with AI uplift | C17 |

**Profiles (`dp:*`, compositions):** `enterprise-copilot-rag` (TT06+TT07; internal users,
enterprise documents, A-ids for corporate data), `customer-chatbot` (TT06+TT07; external
anonymous users, customer PII and transactions, A17/A18; consumer-app ownership scope),
`enterprise-llm-agent` (+TT08, TT12), `coding-assistant` (TT09+TT12+TT14),
`browser-computer-use-agent` (TT10), `multi-agent-system` (TT11), `ai-security-tooling`
(TT05+TT24), `foundation-model-developer` (TT01/TT02+TT15), `ml-platform` (TT17+TT13),
`inference-provider` (TT01+TT17), `automotive-perception` (TT20), `biometric-kyc` (TT21),
`on-device-model` (TT19), `voice-assistant` (TT22), `media-generation-service` (TT23+TT25),
`enterprise-workforce` (TT26+TT27). Each carries a reference architecture, typical assets, an
ownership scope and its ADR-0002 instance type.

---

## Appendix C — AI risk-phase working vocabulary (`ai-risk-phase`; not schema)

Every item has one **primary** phase (where the attacker acts) and optional secondary phases.

| Phase | Catalog `lifecycle_stage` folded in | `LifecyclePhaseCode` | Part V page |
|---|---|---|---|
| `aip:design` | — (architecture choices: excessive agency, lethal trifecta) | concept, architecture | V.1 |
| `aip:supply-chain` | supply-chain; parts of model-artifact | design, implementation, production, distribution | V.2 |
| `aip:data` | data | design, implementation, operation (RAG refresh) | V.3 |
| `aip:development` | training; model-artifact; evaluation and red-teaming | implementation, verification_validation | V.4 |
| `aip:deployment` | deployment | production, distribution, deployment | V.5 |
| `aip:operation-inference` | inference | operation, maintenance | V.6 |
| `aip:operation-agentic` | agent-runtime | operation | V.7 |
| `aip:platform` | infrastructure | operation, maintenance | V.8 |
| `aip:human-org` | human | operation | V.9 |
| `aip:retirement` | change and retirement | end_of_support, decommission | V.10 |

AIT-137 (catalog stage model-artifact) and AIT-142 (deployment) keep their catalog stage as
primary phase and `aip:retirement` as secondary. Continuous red-teaming in operation is secondary
to `aip:operation-*`. The accepted `LifecyclePhase` is not overloaded; profile instantiation
resolves one to the other.

---

## Appendix D — Source inventory (probed 2026-10-26; licence column feeds §4.1.3)

| Class | Source | Access | Cost / limit | Redistribution (to confirm) |
|---|---|---|---|---|
| Papers | arXiv | API, OAI-PMH, RSS | ≤1 req/3 s | metadata; paper text per its licence |
| | OpenAlex | `api.openalex.org` (key) | free key per account | CC0 metadata |
| | Semantic Scholar | graph API (key) | 1 rps | ids only; no TLDR republication |
| | Crossref | `api.crossref.org` | free | metadata |
| | DBLP | XML dump (search API behind Anubis) | free | metadata |
| | OpenReview v2; ACL Anthology bulk | API; bulk | free | metadata |
| | USENIX / NDSS | program pages | open access | links |
| | Google Scholar | — | no automation | — |
| Catalogs | MITRE ATLAS v2026.09 | GitHub releases | free | confirm licence + NOTICE |
| | OWASP GenAI (LLM 2025, ASI 2026, MCP) | site, GitHub | free | confirm share-alike terms |
| | CWE/CAPEC 4.20 | downloads | free | terms-of-use attribution |
| | NIST, ETSI/UK, CoSAI, SAIF, DASF | publications, GitHub | free | per document |
| | CSA MAESTRO and guides | site | free to read | ids + names + paraphrase |
| | ISO/IEC | licensed previews only | — | paraphrase |
| Vulns | NVD CVE 2.0; CVE List V5; GHSA; OSV; CISA KEV (2026.10.23, 1,756 entries); vendor RSS | APIs, feeds | free (NVD key 50 req/30 s) | ids + facts |
| Incidents | AIID (weekly snapshots; GraphQL origin-restricted); OECD AIM (manual); AVID, AIAAIC; GDELT | snapshots, UI, GitHub | free | confirm AIID data licence |
| Social | X (pay-per-use, cap $25/month); Bluesky; Mastodon; HN; GitHub | APIs | see §4.1.2 | post IDs/URLs only |
| Search | WebSearch | Claude tool | ≤120/week/account + 40 per critic round | — |

**Quotes:** public domain / CC0 / CC BY(-SA) / Apache / MIT → quotes with attribution and the
licence's obligations; arXiv default licence, all-rights-reserved PDFs, journals, news → paraphrase,
≤2 sentences verbatim with locator; social posts → no text.

---

## Appendix E — Knowledge-layer sketch (**input to the ADR draft, not a decision**)

This sketch exists so the PROPOSAL diff (W3) does not start from nothing. It is superseded by that
diff the day it opens; nothing here binds the schema.

- **Candidate classes:** `Concept` (one SKOS-shaped class for every vocabulary), `TargetType`
  (is_a Concept), `Catalog` / `CatalogRelease` / `CatalogEntry`, `Incident`,
  `PublishedThreatModel`, `Reference` (generated by the library loader), `DomainProfile`; slot
  additions to AttackPattern / Weakness / Mitigation via a `ThreatKnowledgeEntry` mixin.
- **Candidate bridge edges:** `instance_of`, `uses_technique`, `exploits_weakness`, `stated_as`,
  `applies_to_family`; catalog mappings with SKOS `mapping_kind`.
- **Candidate evidence qualifiers:** an `Assertion(predicate: evidenced_by)` with `evidence_role`
  ∈ {supports, describes, demonstrates, observes, mitigates, contradicts, catalogs, measures},
  `locator`, `quote_sha256`, provenance; the 769 AIT→S-id pairs would migrate as
  `describes`/`proposed`.
- **Candidate derived state:** maturity from `observed_in` incident kinds (checker fails on drift);
  `epistemic_status` ∈ {imported-authoritative, ai-proposed, ai-cross-checked, human-authored,
  reviewed-accepted, reviewed-rejected, disputed, superseded, derived}.
- **Candidate catalog reference form:** `<framework>@<release>:<local_id>` on catalog references
  only (Q-07 keeps Weakness ids per PLAN-0002).
- **Candidate layout (Q-12):** `kg/schemes/`, `kg/catalogs/<framework>/<release>/{lock,entries}.yaml`,
  `kg/knowledge/ai/**`, `kg/links/**`, `kg/reviews/` (humans only), `kg/profiles/<domain>/`;
  `research/0014-ai-threat-model/` frozen as the v0.2.0 snapshot after migration; PDF cache
  outside every repo.

---

## Review log

**Round 1 — adversarial critique (2026-10-26).** A fresh critic with no part in drafting reviewed
v0.1.0 against tmodel `main` @ 449f515, library `main` @ 6d9a51f, open PRs and issues, and the
three memos: **41 findings (3 critical, 18 major, 20 minor)**; 27 of 32 checked claims held.
Folded into v0.2.0: **34 applied, 7 applied in part, 0 rejected.** The three critical findings
(review supply, missing calibration baseline, unbudgeted sponsor time) are resolved by §3.1–§3.4
and Q-18: a measured review budget with a cut order, agent cross-checks (V1–V3) carrying volume, a
30-reference gold set as the correctness anchor, and a stated sponsor budget with delegations.
Partial applications, each with its reason in DL-0026: L0 volume is not capped at human sampling
capacity (the gold set estimates error at any volume; capping would only hide references); the gold
set is student-labelled and sponsor-adjudicated, not sponsor-authored (sponsor budget); the
knowledge-layer sketch stays as a labelled appendix instead of a premature PROPOSAL file; v1.0 accepts
a timebox-closed W7 (otherwise the stop rule could again never terminate); corpus-size arithmetic
waits for the Phase 2 TOC sweep; evaluation and red-teaming sit inside existing phases rather than a
new one; the appendices are cut and relabelled but not moved out. Per-finding dispositions: DL-0026.
