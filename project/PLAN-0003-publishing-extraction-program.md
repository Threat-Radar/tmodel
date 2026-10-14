---
schema: "archdoc/v1"
id: PLAN-0003
title: "Program plan — library-driven publishing & extraction (human↔machine review surface → KG + requirements)"
short_title: "Publishing & extraction program"
description: "The program that makes the library drive the design: a top-down HTML review site (tmodel output top → library bibliographic products: landing, A–Z, by-category with expandable rows showing applicability/tags/summary/#requirements/extraction-status, topic pages), and a deepened, type-aware, repeatable extraction pipeline that distils sources into requirements, procedures, agents, code, protocol specs, state machines, formal proofs, human-review logs, and threats/vulnerabilities — mapped to products/companies/projects/procedures as the KG. Plan first; adversarial review of the plan; then phased PRs each adversarially reviewed against these goals."
type: plan
category: process
status: draft
version: "0.1.0"
version_policy: "semver; MINOR = additive; version and updated move together (ARCH-0001 §9.5)"
date: "2026-10-08"
updated: "2026-10-08"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: project/PLAN-0003-publishing-extraction-program.md
defers_to: ARCH-0001
agent_notes: >
  Program plan spanning tmodel (publishing/KG/output) and library (bibliographic products +
  extraction). The library drives the design; HTML is the human↔machine review surface; the
  distilled artifacts become the KG for threat models and the requirements for implementations
  and procedures. This doc is the PLAN; it is reviewed adversarially, then executed as phased
  PRs. It accepts no DEC-*; §5 names the decisions a sponsor/ADR must settle.
---

# PLAN-0003 — library-driven publishing & extraction

## 0. The thesis

**The library drives the design.** A source document is distilled into typed artifacts
(requirements, schemas, state machines, …). Those artifacts become two things:

1. **the KG** that threat models reason over, and
2. **the requirements** that implementations and procedures are built and audited against.

**HTML is the human↔machine review surface** — the way a person inspects what the machine
extracted, and signs off. So the publishing site and the extraction pipeline are one program:
the site exists to review the extraction, and the extraction exists to populate the KG.

## 1. Current state (recon, 2026-10-08)

Three read-only recon passes (library publishing, tmodel publishing, extraction/schema).
**More already exists than the brief assumed — PR #113 and library #14 are merged.**

- **Site is live.** GitHub Pages serves `main:/docs` at `https://threat-radar.github.io/tmodel/`.
  It has a landing page (`docs/index.html`), a bibliography (`docs/bibliography/`:
  `index.html` = A–Z, plus `by-topic`, `by-type`, `by-body`, `crosswalk`), reports
  (`docs/reports/`), and all ~414 per-record pages copied under `docs/library/records/…`.
  Shared nav via `site.yaml` + `site_nav.py`; CI runs `check_identities.py` + `check_links.py`;
  build entrypoint `bin/publish-site`.
- **Import model already chosen.** The **library owns** the data (`record.yaml` + `summary.md`)
  and the **per-record** HTML template (`bin/_record_html.py` → untracked `summary.html`). **tmodel
  owns** the aggregate views, site chrome, landing page, and **hosts** the copied record HTML under
  its Pages. The library has **no Pages of its own**.
- **GitHub fact:** a committed `.html` is shown as source by the repo file viewer; only **Pages**
  renders it. The clickable entry is the Pages URL, reachable from the repo's About/Pages
  environment and (to be added) the README.

### 1a. What already satisfies the brief

- A tmodel top page (`docs/index.html`) served at a single clickable Pages URL. ✓
- Top → bibliography top (`bibliography/index.html`). ✓
- Bibliography landing with an **alphabetic** list (A–Z `index.html`) and **by-category** lists
  (`by-topic`, `by-type`, `by-body`, `crosswalk`). ✓

### 1b. What is missing (the real work)

- **Expandable category rows.** Current category views are flat lists, not compact rows that
  expand to show applicability, tags, a one-line summary, **# of requirements**, and
  **extraction-phase status**. The data for three of those columns does **not exist** as
  machine-readable record fields (see §4).
- **Topic summary pages.** No generator consumes `topics/*.yaml`; topic schema has no
  title/description and many `answer` fields are empty.
- **Ownership of the bibliographic generators.** #113 put the aggregation generators in **tmodel**.
  "The library drives the design / bibliographic products live in the library" argues for the
  generators living in the **library** (see decision D1).
- **The extraction program** (the larger half) — §3.

### 1c. Latent defect introduced by library #14 (fix before any re-pin)

tmodel pins the library submodule at `06640cc` (pre-banner), so `check_links.py` **passes today**
(the critic re-ran it: 422 pages, all links resolve). The defect is **latent, not live**: library
`main` (`0f80486`, my #14) added a top `<header>` with `href="../../../README.md"`, and the tmodel
copy step (`render_bibliography.py` `publish_record_pages`) replaces **only** the `<!-- site-nav -->`
comment, leaving the library header intact. So the next submodule re-pin forward would give every
copied page (a) a dead `README.md` link → `check_links.py` / CI fails, **and** (b) double chrome
(tmodel nav + leftover library header). This is **A0** — mine to fix, and it gates every re-pin.

### 1d. Program boundary (scope)

This document covers a **Dec-MVP publishing program** and a separately-scoped **extraction research
track**. They are not one sprint. The MVP program is **A0 → B0(minimal) → B1 → A1/A2**: the review
surface and the record data it needs. The research track (**B2–B5**) — new artifact types,
type-aware profiles, the convergence loop, and the KG bridge — is a multi-semester agenda and will
graduate into its own `PLAN`/`BACKLOG` once the MVP surface lands; it must **not** hold the MVP
hostage to formal-proof tooling or convergence metrics.

## 2. Track A — publishing (the review surface)

Phased; each phase a PR with a design-log entry and an adversarial review.

- **A0 — fix the re-pin defect (gates every re-pin).** The library header (the whole chrome, not
  just the bare `<!-- site-nav -->` comment) must become the *replaceable region*: wrap it as
  `<!-- site-nav -->…<!-- /site-nav -->` so the library's **own standalone pages keep the "README ↑"
  banner** (the library is forkable/standalone) while a publisher replaces the **entire region** with
  its own nav — removing both the dead `README.md` link and the double chrome. This touches the
  library template **and** the tmodel copy step (region-replace, not comment-replace). **Ordering
  gate:** no submodule re-pin may land before the library fix is merged; the re-pin must advance the
  pin to a commit that already contains the fix, in the same change. *Library PR → then tmodel
  re-pin PR; confirm `check_links.py` green.*
- **A1 — expandable category rows (MVP: STUB only, sponsor).** Land the row mechanics as a stub now;
  defer the data-backed columns until B1. Split so the mechanics can precede the data:
  - **A1a — row mechanics (the stub).** Redesign the by-category/by-topic views so each entry is a compact row
    that expands (native `<details>/<summary>` — **no JavaScript**, honouring the SKILL no-script
    rule; `refuse_active()` enforces it; 414 records is trivial for static `<details>`). Columns that
    exist today (applicability, tags, and `short_title` as the interim one-line summary). *Can precede B1.*
  - **A1b — data-backed columns.** Add the three columns that need new data — one-line summary,
    **# requirements**, **extraction-phase status** — once **B1** supplies them. *Depends on B1 → B0.*
- **A2 — topic summary pages.** A generator over `topics/*.yaml` (question, answer, status, owned
  records, `bears_on`). **Topics must include threat-modeling, AI-threats, and the other major
  groupings** (sponsor), not only the current fine-grained topics — i.e. a grouping layer above
  individual topics. Requires a topic-schema title/description + grouping field (B0). Library-owned
  product.
- **A3 — bibliographic generators in the library (D1 RESOLVED).** The **basic bibliography
  generators live in the library** (it is a fork; it owns its bibliographic products) and are shared
  as **basic skills** across forks; **other forks may define other biblio types** on top. Relocate
  the basic aggregation logic from `tmodel/docs/publishing/render_bibliography.py` into a shared
  **library** module the tmodel publisher imports (as it already imports `_record_html.py`); tmodel
  keeps only tmodel-specific output + site chrome + hosting.
- **A4 — real entry + hub.** Add a prominent Pages-URL link to the tmodel README (so it is clickable
  from the repo). Decide whether `docs/index.html` stays a distribution mock or becomes a real
  project hub that routes top → bibliography (A–Z + by-category) → record → (review).

## 3. Track B — extraction (what the review surface reviews)

The library distils sources into artifacts that become the KG and the requirements.

### 3a. MVP subset (part of the Dec-MVP program)

- **B0 — formalize the schemas (TOP priority; its OWN PR, ASAP; multi-agent create → iterate).**
  Sponsor directive (2026-10-08): the schema is a **primary deliverable**, expedited and iterated to
  perfection, because it is what improves all *later* extraction. Nine+ artifact schemas are in use
  but undocumented (`library-requirements/v2` — used by 41 records — `object-model/v1`×42,
  `state-machine/v1`×25, `protocol/v1`×16, `messages/v1`×12, `crosswalk/v1`×6, `fields/v1`,
  `claim-trees/v1`). Pin and document each as a **versioned** schema `bin/validate` enforces, and
  **reconcile the `distillation.artifacts.kind` enum** with reality (add `object-model`, `crosswalk`,
  `verification`).
  - **Requirements schema = LinkML** (sponsor directive, overriding the critic's library-local
    recommendation). LinkML is an **open IDL**, not a tmodel coupling: the requirements LinkML schema
    **lives in the library** (the library owns its extraction products — D1) and is shared as a basic
    skill across forks; tmodel **aligns/imports** it, so the dependency still points **tmodel→library**
    (the critic's real concern — avoiding library→tmodel/ADR-0007 coupling — is met by *location +
    direction*, not by refusing LinkML). The schema must capture semantic context and support mapping
    to products/companies/projects/procedures and **external import** (OSCAL/ReqIF/SACM, OTM/STIX per
    the #39 crosswalk).
  - **Method:** a deep read of the plans, reports (RPT-0005 schema representations, the #39 crosswalk),
    and external import requirements → **multi-agent creation** (one schema family per agent, the
    requirements LinkML as keystone) → **adversarial iterate** → a dedicated library PR. Not blocked on
    the rest of this program.
- **B1 — record-level rollup for publishing (couples to A1b).** Generate machine-readable
  record-level data the publisher reads — a **one-line summary** (`short_title` as interim fallback),
  a **requirements count**, and an **extraction-phase status / progress**. Source of truth stays in
  `distilled/requirements.yaml` and `distillation.passes`/`artifacts[]`; B1 **emits a rollup** — not a
  publish-time reopen of every file, not drift-prone hand fields (decision D2). **Define what
  "# requirements" counts** (e.g. normative requirement entries, excluding group/practice roll-ups):
  `counts.entries` conflates groups + practices + statements while `native_counts` isolates active
  tasks — pick and document one.
### 3b. Research track (post-MVP — to be spun out into its own PLAN/BACKLOG)

**Not sprint phases of the MVP.** A multi-semester agenda; it graduates to its own doc once the MVP
surface lands, and must not block A0/A1.

- **R-B2 — missing artifact types.** Kinds + schemas + FX-1 treatment for **procedures**, **agents**,
  **formal proofs**, **threats/vulnerabilities**, and promote **human-review logs** to first-class
  (today only implicit `reviewed_by` + an undeclared `verification.md`).
- **R-B3 — type-aware extraction profiles.** FX-1 is type-*gated* (4 record types) but one-size in
  its artifact set; define per-type **profiles** (protocol / regulation / process-standard / paper /
  dataset) of required-vs-N/A artifacts.
- **R-B4 — requirement-correctness convergence loop.** Beyond today's single verify pass: an
  **N-independent-extraction + reconcile** loop with an agreement metric, recorded in
  `distillation.passes`.
- **R-B5 — the KG bridge (requirements ↔ products/companies/projects/procedures).** Two parts, two
  gates: **(i)** the requirement↔product/party/mitigation *edges* are **already decided** — ADR-0004
  (accepted) carries them as typed **link records** (file SoT), so this is modelling work, not a new
  decision; **(ii)** a first-class **`Requirement` type** does **not** exist in the canonical LinkML
  and is **DEC-001-gated** — author it as a `spec/ARCH-0001-*-PROPOSAL-*.md` **diff**, never committed
  into `spec/schema/tmodel-object-model.linkml.yaml` (CLAUDE.md: no parallel architecture doc; no DEC
  accepted outside an ADR). Connects to DEC-009 and the existing MAP-0001 requirement↔requirement crosswalk.

## 4. Schema workstream (answers "do we need to update/document schemas?" — **yes**)

Cross-cutting, feeds both tracks:

1. **Pin + document** every in-use artifact schema (B0); stop shipping implicit shapes.
2. **Requirements schema in LinkML** (sponsor directive) — an **open IDL owned by the library**, with
   generated JSON-Schema the library's `bin/validate` enforces, so the representation is stable and
   round-trippable. tmodel *aligns* a KG view to it (tmodel→library); this is **not** governed by
   ADR-0007 (which is tmodel-scoped).
3. **New record fields** for the review surface (B1): a one-line summary (`short_title` fallback),
   a requirements count, extraction-phase status — surfaced via a generated rollup.
4. **New classes** in the tmodel KG: `Requirement` + the requirement↔product/company/project/
   procedure mapping (R-B5) — authored as an **ARCH-0001 PROPOSAL diff**, proposal-level until DEC-001
   accepts; the edges themselves are already ADR-0004 link records.
5. **Enum reconciliation**: `distillation.artifacts.kind` gains `object-model`, `crosswalk`,
   `verification`, plus B2's new kinds.

## 5. Decisions (sponsor rulings 2026-10-08; this plan accepts no DEC-*)

- **D1 — ownership of the bibliographic generators. RESOLVED → LIBRARY.** The basic bibliography
  generators live in the **library** (it is a fork; it owns its bibliographic products) and are shared
  as **basic skills** across forks; other forks may add their own biblio types. tmodel imports the
  basic generators and hosts under tmodel Pages. (A3.)
  - **D1a — hosting. RESOLVED → single tmodel Pages (import/host).** No separate library Pages site.
- **D2 — expando-row data source.** *Recommend (not yet ruled):* a **generated per-record rollup**
  from `requirements.yaml` + `distillation`, read by the publisher — not a publish-time reopen, not
  drift-prone hand fields. (B1.)
- **D3 — requirements IDL. RESOLVED → LinkML** (sponsor: "LinkML for requirements … schema is a
  primary delivery"). Owned by the library as an open IDL; generated JSON-Schema for `bin/validate`.
  (B0.)
- **D4 — `docs/index.html`.** *Recommend (not yet ruled):* make it a real project hub rather than
  today's distribution mock, so "review from the top" is a genuine landing. (A4.)

## 6. Gaps (explicit)

Schema: no documented `requirements/v2`; 9+ implicit schemas; `artifacts.kind` enum out of sync; no
`summary`/`requirements_count`/phase-rollup fields; topic schema has no title/description; tmodel KG
has no `Requirement` class and no requirement↔product/company/project mapping. Extraction: five of
the requested artifact types missing (procedures, agents, formal proofs, threats/vulns, first-class
review-log); extraction is type-gated not type-profiled; no N-run convergence loop. Publishing: no
expando rows, no topic pages; the re-pin bug (A0); README has no Pages-entry link.

## 7. Risks

- **A0 is latent** (not live): the pin is pre-banner so CI passes today; the dead link + double
  chrome trigger on the **next re-pin** — so A0 must land before any re-pin.
- **#113 refactor (A3)** — moving the basic generators into the library must keep the site up; keep
  the import boundary so tmodel Pages never goes dark.
- **DEC-001 still open** — the `Requirement` type is a PROPOSAL diff, never a commit to the canonical
  LinkML; do not let R-B5 silently "decide" the object model.
- **No-JavaScript constraint** — expando rows use `<details>/<summary>`, not script (SKILL rule;
  `refuse_active()` enforces).
- **Scope** — the research track (R-B2…R-B5) is multi-semester and must not block A0/B0/B1/A1.

## 8. Execution & meta-process (the sequence you asked for)

1. **This plan → a fresh adversarial-critic pass** (done; findings folded — DL-0017).
2. **Sponsor rulings folded** (§5: D1→library, D3→LinkML, A1→stub, A2→groupings, B0→own PR ASAP).
3. **Corrected order** (critic C1 — build data before the rows that show it):
   **A0 (gates re-pin) → B0 (schemas, TOP priority, own PR, multi-agent) → B1 (rollup) →
   A1a stub / A2 → A1b / A3 / A4.** The research track (R-B2…R-B5) follows in its own PLAN/BACKLOG.
4. **Each PR**: a design-log entry, deterministic/re-runnable generators, and an **adversarial review
   against this plan's goals** before merge — the extract→verify→cross-check discipline.
5. **Multi-agent execution** where parallelizable — B0 (one schema family per agent, requirements
   LinkML as keystone) → adversarial iterate; later R-B2/R-B3 likewise.

## 9. Sequencing summary

```
A0 (fix banner region; gates every re-pin)           ← urgent, mine
B0 schemas (OWN PR, ASAP, multi-agent; LinkML reqs)  ← TOP priority
   └─ B1 rollup (summary · #reqs · phase status)
         └─ A1a stub rows (now) → A1b data columns (after B1)
A2 topic pages incl. threat-modeling / AI-threats / major groupings
A3 move basic biblio generators into library (D1) ; A4 README Pages-entry link
── research track (own doc) ──
R-B2 artifact types · R-B3 type profiles · R-B4 convergence loop
R-B5 KG bridge: ADR-0004 link records (decided) + Requirement PROPOSAL diff (DEC-001-gated)
```
