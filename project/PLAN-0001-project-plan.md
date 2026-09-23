---
schema: "archdoc/v1"
id: PLAN-0001
title: "Project plan — semester execution, repo, library, research, and team"
short_title: "Project plan"
description: "Execution plan for the CS 490 Fall 2026 senior project. Subordinate to ARCH-0001 for all architecture. Schedules the work to an early-December MVP demo."
type: plan
category: process
status: draft
version: "0.1.1"
version_policy: "semver; MINOR = additive; version and updated move together (§9.5)"
date: "2026-09-23"
updated: "2026-09-23"
authors:
  - role: sponsor
    id: paul-lambert
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: project/PLAN-0001-project-plan.md
companion:
  - spec/ARCH-0001-threat-model-architecture.md
defers_to: ARCH-0001
constraints:
  architecture_source_of_truth: ARCH-0001
  no_invented_decisions: true
agent_notes: >
  This plans execution only. It does not decide architecture. Every
  architectural question routes to an open DEC-* in ARCH-0001 §8. Do not mark a
  DEC accepted from this file.
---

# Project plan — CS 490 Fall 2026

**Sponsor / SR:** Paul Lambert (Threat-Radar) · **Students:** four, repo `admin` (roster: BACKLOG T-004) · **Faculty:** Prof. Paul Haskell
**Plan date:** 2026-09-23 · **Demo:** early December 2026 (CS 490 demo day; exact date TBD) · **Weeks remaining:** ~10
**Architecture source of truth:** `ARCH-0001` v0.1.0 (every `DEC-*` open)

---

## 1. What this plan adds to ARCH-0001

ARCH-0001 defines the object model, requirements, interchange, risk framing, the
human-review model, and the open decisions — deliberately **not scheduled**. This
plan supplies what ARCH-0001 leaves out: the schedule against ~10 weeks and four
students, the repository and publication structure, the shared library, the
research reports, the application, the demo, and how the team works.

**Goal (sponsor).** Best-in-class threat modeling: a GUI with interactive,
graphical threat and threat-chain models; human review, annotation, and impact
judgement as first-class; risk metrics that say *how bad* a threat is; mappings
from generic threats to specific products and product families (which may differ
per attack-path mitigation) suitable for corporate use; and expansion of the
`library/` knowledge graph as a deliverable in its own right. The first work is
**deep research** to define requirements and remaining implementation goals.

## 2. Week-0 gate — this week

**Requirements and final goals are finalized in week 1.** Until the gate:

- ARCH-0001 §4 requirements are **draft**; ARCH-0001 §8 `DEC-*` are **open**.
- The gate meeting ratifies: the R-set, the MVP scope (DEC-005), and the
  relationship to `tradar` (DEC-007) — the two decisions that shape everything
  downstream.
- Bootstrap completes: repos created, roster added as admins, library forked and
  wired as a submodule (see §4–§5 and the harness increment I0).

## 3. Team and how we work

Four students are repo `admin` and review each other; the sponsor owns the
normative surface (`spec/**` via `CODEOWNERS`); faculty advises. Coordination,
lanes, and "which repo do I open" are in `PROC-0001`. Scrum cadence: a weekly
30-minute Zoom (decision + unblock + increment demo), a draft PR per increment
opened on day one, issues before code. The repo is the record.

## 4. Repositories and publication

| repo | org | purpose |
|---|---|---|
| **`tmodel`** | Threat-Radar | this repo — architecture, plan, research, spec, prototype |
| **`library`** | Threat-Radar | knowledge-graph library; a **fork** of `m-of-n/library`, submodule of `tmodel` |
| `tradar` | Threat-Radar | the 2025 container/dependency CVE+SBOM CLI; input source (DEC-007) |

**Public by design.** Goals, plans, research reports, references, and
bibliographies are written in **concise, public-facing forms** in the public
repo. Anything sensitive stays out (there is none expected for a class project).

## 5. The library — reuse and expand

We **fork** `m-of-n/library` into `Threat-Radar/library` so the team writes in
its own org, expands it freely, keeps lineage to m-of-n, and can upstream
selected records by PR. It is vendored into `tmodel` as a submodule pinned to a
commit, so every report's bibliography is reproducible as `library@<commit>`.
**Expanding the library is a first-class deliverable** (R-030): every research
source becomes a record; technical specs are distilled toward schema and code.

The fork also **decouples us from upstream schema churn.** m-of-n/library's
`record.schema.yaml` is at v5 and still moving; tmodel is now a *second*
consumer (threat modeling, and possibly SBOM), so a pinned fork lets us adopt
schema changes deliberately — and propose our own — instead of tracking a moving
target. Changes both consumers need are coordinated with the m-of-n project
before either side depends on them.

## 6. Research — the first work

RPT-0001 (`research/0001-threat-modeling-landscape/`) is a **deep survey** of the
competitive and standards environment. It is iterated in place (versioned). Its
`dimensions.md` lists the search axes; references land in `library/`; the report
summarizes and compares. It produces two decisions' worth of evidence: MVP scope
(DEC-005) and the risk-metric scheme (DEC-003), plus the object-model and UI
inputs (DEC-001, DEC-006).

## 7. Candidate expansion dimensions

Beyond tradar's container/dependency composition. RPT-0001 + the gate pick which
land in the MVP (DEC-005); the rest are backlog:

source-code composition analysis · rule-based scanning · graphical interactive
threat models · MITRE CWE integration · NVD lookup automation · risk metrics
("how bad") · Common Criteria attack-feasibility metric · ISO/SAE 21434 risk
analysis (optional, high value) · threat-chain analysis with graphic
representation · knowledge-graph annotation for human review · generic-threat →
specific-product / product-family mapping · mitigation tracking over the design
lifecycle · library expansion.

## 8. Increments (scrum, ~2-week sprints)

**The demo floor is I3 (Nov 10).** Everything after is upside. Each increment
opens a draft PR on day one and ends with a demo at the weekly Zoom.

| inc | window | outcome |
|---|---|---|
| **I0 Harness** | Sep 23–29 | Repos, roster as admins, library fork + submodule, CI, backlog, Week-0 gate. **This PR + hand-off.** |
| **I1 Research** | Sep 30–Oct 13 | RPT-0001 v0.x across all dimensions; references in `library/`; target use cases; DEC-005/DEC-003 evidence. |
| **I2 Model** | Oct 14–Oct 27 | ARCH-0001 → v0.2 with a chosen object model (DEC-001) and a first `spec/schema/` draft importing an existing format; CWE/NVD design (DEC-008); risk-metric survey → DEC-003 direction. |
| **I3 MVP core** *(demo floor)* | Oct 28–Nov 10 | Interactive graphical threat model + threat-chain view over the chosen dimension (DEC-005/DEC-006), with the human review/annotation model wired (R-018…R-021). End-to-end on one worked example. |
| **I4 Risk & mitigation** | Nov 11–Nov 24 | Risk metrics computed (DEC-003), mitigation mappings, generic→product & product-family mapping, mitigation-lifecycle tracking, NVD automation. |
| **I5 Integrate & demo** | Nov 25–Dec 5 | Polish, docs, published site, vectors green, MVP demo. |

## 9. Definition of MVP (the demo)

A user loads a real system (via tradar output and/or one chosen expansion
dimension), sees threats and a threat chain rendered as an interactive graph,
**reviews and annotates** an attack path (sets impact, accepts/rejects with a
rationale), sees a risk score that reflects that human input, and maps the threat
onto a specific product — with the mitigation state visible. Backed by the
`library` knowledge graph and an object model that imported at least one existing
format (round-trip proven by a vector).

## 10. Risks

- **Scope.** The dimension list is large; DEC-005 must pick ruthlessly at the gate. Demo floor is I3.
- **Cross-org library.** The submodule is cross-org (Threat-Radar ← forked from m-of-n). Absolute URL, not relative; `git submodule status` in every pre-PR check.
- **Detached-HEAD data loss** in `library/`. Never work inside the submodule checkout; open the `library` repo (PROC-0001 §1).
- **AI without traceability.** An AI threat model is worthless if it cannot be reviewed. R-018…R-021 are not deferrable past I3.
- **Team ramp.** Four students, new stack. I0/I1 front-load setup and reading.

## 11. Milestones

- **Week 1** — requirements + final goals finalized (Week-0 gate).
- **Oct 13** — research landscape complete enough to take DEC-005/DEC-003.
- **Nov 10** — MVP core demoable (floor).
- **early Dec** — MVP demo.
