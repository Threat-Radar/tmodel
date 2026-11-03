---
schema: "archdoc/v1"
id: DL-0026
title: "PLAN-0004 AI threat program: parallel planning, adversarial critique and fold (#71)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-26"
updated: "2026-10-26"
record: DL-0026
bears_on: [DEC-001, DEC-003, DEC-008, DEC-009]
defers_to: ARCH-0001
---

# DL-0026: PLAN-0004, the AI threat program

AI-assisted design record (per `CLAUDE.md`). Sponsor: @nymble, working with Claude Code.

## Question asked

The sponsor asked for a plan to take RPT-0014 round 1 (1,181 sources, 146 hypothesis techniques,
179 incidents, 127 threat models) to professional-grade AI threat research. The plan had to deliver:

- a catalog of the breadth, scope and categories of attacks on and with AI;
- a collection of target and product types in the KG that is suitable for modelling;
- a multi-part, hierarchical report on AI threats today, organised by phase of risk (supply chain,
  data, development, deployment, operation, …), where individual reports roll up into final reports
  and form the basis for threat models;
- a TARA HTML threat model that is reproducible for several domains, as an artifact of this SDL and
  of other SDL processes;
- a bibliography connected to weaknesses and threats, in which every reference has a summary and
  categorisations or references to artifacts;
- a hunt for the latest attacks (X included);
- adversarial review of completeness, with ingestion and wider searches rerun until the research
  passes on clarity and coverage.

The sponsor also asked whether an AI threat model can be built now, how the work should be
distributed among the sponsor, four students and agents running on several Claude accounts, and
what issue structure should follow.

## Method

1. **Three parallel planning threads, all read-only** over tmodel `main` @ 449f515, library `main`
   @ 6d9a51f, and the open issues and PRs:
   - A: status, stalls and decisions;
   - B: ingestion, sources, the DX-AI/1 distillation profile, coverage model and prioritisation;
   - C: KG representation, domain profiles, TARA pipeline and report architecture.

   Each wrote a scratch memo. The memos are not committed. The plan inlines every rule that a DoD
   depends on, so the memos serve as provenance only.
2. **Synthesis.** The memos were merged into PLAN-0004 v0.1.0 (849 lines).
3. **Fresh adversarial critic.** A new agent with no part in drafting checked v0.1.0 against the
   repo, GitHub and the memos.
   - It found **41 findings: 3 critical, 18 major, 20 minor.**
   - It verified 32 claims: 27 held, 2 were wrong (PR #130 "three open choices"; library#22 "waited
     12 days after two reviews") and 3 were partly wrong.
4. **Fold.** A separate pass applied the findings, giving v0.2.0.
   - Each fact that changed was re-checked with `gh` and `git show origin/…`.
   - PR #130 is open with only COMMENTED reviews. Its DL-0024 records that the sponsor delegated
     four decisions to @Clovier on 2026-10-22, and that they were made as recommended.
   - library#22 is open since 10-14. It has a comment review by @Clovier (10-21) and comments by
     @kriishnaa-18 (10-23, 10-24), but no approval.
   - #37 is closed and its title carries a name.
   - DL-0026 is free on `main` and on every open PR. #130 uses 0024 and #167 uses 0025. 0006, 0011,
     0012 and 0015 are already duplicated on `main`.

## What was produced

- `project/PLAN-0004-ai-threat-program.md` v0.2.0. It is a draft and accepts no `DEC-*`. It
  contains:
  - a one-page decision brief: asks → deliverables, the decisions with recommendations, and
    week-1 actions with owners and hours;
  - a review budget sized to measured capacity: about 20 student units/week and a stated sponsor
    budget of 4 h in S3 and 5 h/week in S4–S7;
  - verification layers V0–V3, in which agents cross-check each other on independent prompts and
    contexts, using a second model family where Q-17 allows;
  - a 30-reference human gold set that serves as the correctness anchor, with field-level
    agreement and confidence intervals;
  - edition grades (draft / reviewed-core / v1.0);
  - a licence register for catalogs and APIs;
  - an independent holdout;
  - stop criteria with a timebox at the end of Phase 3;
  - Q-01…Q-18.
- This entry.

## Choices made, open to review

- **Humans anchor correctness; they do not cover volume.** In-semester human review totals about
  84 units. Everything else stays hypothesis-badged, and each edition publishes the held,
  cross-checked and reviewed counts plus the gold-set error estimate.
- **No student runs agent batches in-semester.** All production runs on the sponsor's account, so
  in-semester volume is bounded by one account's quota. The S3 pilot measures that quota.
- **The taxonomies are working vocabulary, not schema.** They become a schema range only through
  the Q-05b ADR.
- **The knowledge-layer sketch stays in Appendix E**, labelled "input to the ADR draft, not a
  decision". It is not moved into a PROPOSAL file.

## Findings and dispositions

Totals: **34 applied, 7 applied in part, 0 rejected.** No finding was rejected outright. Where the
fold departs from the critic's proposed fix, the reason is stated in the table. These departures
are the evidence of what was not accepted.

| # | Sev. | Finding (short) | Disposition | How / reason |
|---|---|---|---|---|
| 1 | C | Review demand far exceeds supply (~20/week) | Applied in part | §3.2 sets supply against demand and adds a cut order. The 100% E3+ rule now covers only claims that drive maturity. Departure: L0 production is not capped at sampling capacity. A fixed random gold set estimates field error at any volume, and capping production would only hide references |
| 2 | C | Calibration baseline does not exist; κ on n=3 is meaningless | Applied in part | §3.4: gold set of 30, stratified; field-level agreement with 95% CIs; κ only at n≥30; the agentic-mcp re-run is a smoke test; the "human baseline" was renamed. Departure: the gold set is labelled blind by students and adjudicated by the sponsor, not sponsor-authored. Sponsor-authored would take ~15 h against a 5 h/week budget |
| 3 | C | Sponsor capacity unbudgeted | Applied | Per-sprint hour budget (§3.1, §6, Q-18). S3 is limited to #159, library#22, privacy, Q-01/Q-03/Q-18. #130/#167, Q-04 and issue edits move to S4. Merges and issue edits are delegated. Fallback order in §5. The "first-5 double-check" is removed, not delegated, because the gold set calibrates reviewers |
| 4 | M | PR #130 misdescribed | Applied | §1.4 and Q table: "ratify or reverse the four delegated decisions; record `reviewed: true`", with the four decisions listed |
| 5 | M | Plan embeds a parallel architecture spec | Applied in part | W3 is cut to purpose, outputs, a summary and dependencies, and points to the ARCH-0001 PROPOSAL diff and ADR. Departure: the sketch stays in Appendix E, labelled "input to ADR draft, not a decision", instead of moving to a PROPOSAL file now. Writing that file before the plan is ruled on would front-run the ADR process |
| 6 | M | Taxonomy freeze is a schema decision without an ADR | Applied | Working vocabulary in `research/0014-*/schemes/` with a remap script. Use as a schema range only via the Q-05b ADR (Q-11, App. B/C) |
| 7 | M | Milestone guard contradicts S5 batches; Phase 0 exit contradicts S4 | Applied | No student agent batches in-semester. The Phase 0 exit uses the pilot, not the agreement run |
| 8 | M | Completeness loophole ("shown") | Applied | Denominator = held corpus. Held/shown/complete are published. Build fails for reviewed-core+ editions |
| 9 | M | Weaknesses under-served | Applied | Weakness view (W5 view 2); every AIT needs a weakness link or a dated note; every reference needs a link to an AIT, weakness or incident |
| 10 | M | Holdout not independent | Applied | Drawn from non-harvested frames, stratified by X-class and TT, hashes only. Critic yield per search is reported |
| 11 | M | Correlated error / model self-assessment missing | Applied | R15; §3.3 V2 cross-model (Q-17); gold set as the anchor; `evidence.self_reported` excluded from maturity |
| 12 | M | Catalog/API licensing missing | Applied | §4.1.3 licence register; ids+names+paraphrase by default; quote checker covers catalog text; R16. The critic's licence facts are marked "to confirm" because they were not verified |
| 13 | M | Merge volume outgrows capacity | Applied | Deterministic bulk stubs (≤3 PRs), batches of 25, M-b ruled S3 and live S4, expected PRs/week stated (§3.6) |
| 14 | M | "Professional-grade" has no release bar | Applied in part | §2.1 edition grades; D1–D5 tied to v1.0; external reader by role. Departure: v1.0 requires W7 to be closed by two passes **or** the timebox, not two passes alone. Otherwise finding 18's non-termination returns |
| 15 | M | Throughput and cost numbers asserted | Applied in part | 20-reference S3 pilot; per-account capacity from the meter; targets restated from it; L0 effort no longer "high". Departure: venue-size arithmetic is not shown. The data does not exist yet, and the Phase 2 TOC sweep replaces the placeholder |
| 16 | M | Uncommitted memos cited as normative | Applied | Every rule a DoD uses is inlined. Memo section citations are removed, and the memos are provenance only (critic's first option) |
| 17 | M | Privacy DoD unmeetable; scope incomplete | Applied | DoD scoped to the leak sites with the `identities.local.yaml` matcher; `check_identities.py` extended to renderer inputs; #37 added; commit-author metadata noted |
| 18 | M | Stop criteria may never terminate | Applied | Axes marked gating vs reported; accepted-gap records; timebox 2027-02-28 (R17) |
| 19 | M | Roll-up structural only; L2 scope unprioritised | Applied | In-semester L2 set (10 phase pages + 4–6 gap pages); explicit synthesis step; page budget per edition |
| 20 | M | Report and phase model gaps | Applied in part | Added: Part III Actors and capabilities, harm categories (Part II), regulatory crosswalk (Part VIII), `aip:design` mapped to concept/architecture. Departure: evaluation and red-teaming are placed inside `aip:development` (pre-release) and as secondary to operation, not given a phase of their own. They are activities that run across phases, not where an attacker acts |
| 21 | M | Multi-SDL and reproducibility untestable | Applied | Second S3 adapter as a Phase 3 deliverable with a CI check; toolchain pinned with hashes; `tara --rebaseline` with a DL entry |
| 22 | m | library#22 wording | Applied | "Open 12 days; comment review and comments; no formal approval" |
| 23 | m | "later" rows have a lane, not "no owner" | Applied | Reworded |
| 24 | m | `topics/sagai.yaml` exists | Applied | "No AI-threats topic" |
| 25 | m | #37 missing from retitle list | Applied | §10.2 lists #36–#39 |
| 26 | m | "§8 Q1–Q7" ambiguous | Applied | "RPT-0014 §8 Q1–Q7" throughout |
| 27 | m | library#21 / #162 misaligned | Applied | Program queue = #159, library#22, #130, #167; #162 and library#21 listed as adjacent; #162 dropped from the W0 DoD |
| 28 | m | AIT-137/142 double-classified | Applied | Primary/secondary phase rule (App. C) |
| 29 | m | customer-chatbot = enterprise-copilot-rag | Applied | Distinguished by users, assets (A17/A18) and ownership scope |
| 30 | m | Four target-type id systems | Applied | Id policy in App. B: TT codes only; families as labels; `dp:*` for profiles; memo C's `tt:*` dropped |
| 31 | m | Canonical CWE form conflicts with PLAN-0002 | Applied | Q-07: Weakness ids keep `cwe-79`/`tr-weak-NNNN`; the release pin lives on the catalog reference, with an alias |
| 32 | m | Design-log collisions wider than 0024 | Applied | §1.4 lists 0006/0011/0012/0015; DL-0026 ships in the same PR |
| 33 | m | Social-only corroboration rules | Applied | E0–E2 cap, excluded from maturity and E3+ queues; no-link case; same-poster write-ups not independent |
| 34 | m | X/xAI terms; handle list privacy | Applied | Terms check in Q-08 and §4.1.2; repo list limited to organisations, individuals kept private |
| 35 | m | Q-04 comment touches DEC-008 | Applied | Comment labelled "direction only; accepted only by ADR" |
| 36 | m | Golden examples circular | Applied | Sponsor sign-off before any use; the gold set is never tuned against |
| 37 | m | Reviewers vs producers; SOW vehicle | Applied | Students do not produce in-semester; Q-02 vehicle is a SOW-0001 amendment with faculty sign-off |
| 38 | m | "Met or restated" always passes | Applied | A shortfall goes to the sponsor for a ruling |
| 39 | m | No edition cadence / as-of | Applied | One edition per term plus a monthly delta page; grade and as-of on every page |
| 40 | m | Number rule needs cached text (285 of 1,181) | Applied | `unverifiable` without a cache; confidence ≤ medium |
| 41 | m | Too long; appendices duplicate targets | Applied in part | One-page decision brief added; W3 and the appendices cut (86 KB → 70 KB). Departure: Appendices A–E stay, each labelled with the artifact it feeds and "moves there when it opens". The target artifacts do not exist yet, and the plan must be reviewable on its own |

## Rejected

- **A sponsor-authored gold set** (finding 2's fix as written). It does not fit the stated sponsor
  budget. Students label and the sponsor adjudicates.
- **Capping L0 at what humans can sample** (finding 1). The gold-set estimate plus badging is
  honest at any volume.
- **Two W7 passes as a hard v1.0 condition** (finding 14). It conflicts with a terminating stop
  rule.
- **A separate evaluation/red-teaming phase** (finding 20). These are activities, not attacker
  positions.
- **Moving the appendices out now** (findings 5, 41). Their target artifacts do not exist yet.

## Inputs (raw agent memos, kept as evidence)

`inputs/A-status.md`, `inputs/B-ingestion.md`, `inputs/C-representation.md`
(the three read-only planning threads) and `inputs/PLAN-critique.md` (the
adversarial critique of v0.1.0). They are unreviewed agent output. Where a
memo quoted project people's first names, those lines have been redacted.
