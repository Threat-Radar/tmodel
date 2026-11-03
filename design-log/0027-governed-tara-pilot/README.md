---
schema: "archdoc/v1"
id: DL-0027
title: "Governed TARA pilot: a versioned, reviewed HTML TARA for the TCU model (mvp-02)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-27"
updated: "2026-10-27"
record: DL-0027
bears_on: [DEC-001, R-041, R-042, R-043, R-044]
defers_to: ARCH-0001
---

# DL-0027: governed TARA pilot (TCU / mvp-02)

AI-assisted design record (per `CLAUDE.md`). Sponsor: @nymble, working with Grok Bot.
**Proposal only.** No `DEC-*` is accepted here; DEC-001b stays open. The schema changes below are
proposals for a DEC-001b ADR, not edits. This is I4 work and is **not** on the Nov 5 demo path.

## Question asked

The sponsor asked for a governance pilot: one TARA, for one model, that is **governed, versioned
and reviewed end to end**, published as HTML at fixed URLs, with a design note recording the
choices. The model is the Telematics Control Unit in
[`spec/vectors/mvp-02-automotive-ecu.yaml`](../../spec/vectors/mvp-02-automotive-ecu.yaml).

## Problem: what exists today

1. **No end-to-end governed publish/approve flow.** Nothing takes a threat model from draft to
   reviewed to approved to published, and nothing records who approved which version.
2. **Governance objects exist only in the schema.** `ThreatModel`, `SecurityProgram`, `Gate`,
   `Milestone`, `Checkpoint` and `GovernedView` (DL-0018) carry `owner`, `revision`, `approved_by`,
   `approval_digest`, `governance_status` and `supersedes`, but no code reads or enforces them.
   The only instance is the hand-written `threat-model:brake-ecu-v1` in
   `tv-hardware-brake-ecu.yaml`, whose digest is a placeholder. mvp-02 is core-only and has no
   governance layer at all.
3. **No KG → HTML TARA renderer.** `render_report.py` renders archdoc Markdown; nothing renders
   TARA content (assets, damage scenarios, threats, attack paths, risk, treatments) from the KG.
4. **The report renderer overwrites a single file.** `docs/reports/<slug>.html` carries a
   revision number but each build replaces the page; earlier approved versions are not kept at a
   stable URL.
5. **CODEOWNERS routes `docs/` to the students.** The catch-all `*` rule means a published TARA
   would be approved by the four student reviewers only. No sponsor or assessor role is required.
6. **`Review` only targets an `Assertion`.** `Review.reviews` ranges over Assertion, so a review of
   a *document version* (a ThreatModel revision or a GovernedView snapshot) cannot be recorded in
   the model. `Review` also cannot say whether the reviewer was a human or an AI agent.

## The pilot

- **Scope.** The TCU TARA over mvp-02 (product `product:telematics-control-unit`).
- **Governance overlay** at `models/tcu/governance.yaml`. It sits beside, not inside, the core
  vector, so mvp-02 stays core-only (its header says so) and DEC-001a acceptance evidence is not
  disturbed.
- **Published layout** (fixed URLs, immutable once written):
  - `docs/models/tcu/tara/vN/index.html`: one directory per approved version; never rewritten.
  - `docs/models/tcu/tara/latest/index.html`: a copy of the newest approved version.
  - `docs/models/tcu/tara/history.html`: every version, with date, digest, approvers and the
    `supersedes` chain.
- **Page sections** follow the TARA work products of ISO/SAE 21434 clause 15 (paraphrased, cited by
  clause; the standard is not quoted): the item and its scope (from the item definition, 9.3),
  assets and damage scenarios (15.3), threat scenarios (15.4), impact rating (15.5), attack paths
  (15.6), attack feasibility (15.7), risk values (15.8) and risk treatment decisions (15.9). The page **ends with
  the requirements the TARA produced**, reached through `Mitigation.stated_as → Requirement`
  (ADR-0012, PR #167). Gaps between mvp-02 and these work products are a child issue.
- **Built with the #93 multiphase publish skill**, as its first real use: **collect** (engine
  assembles the TARA intermediate from the KG) → **render** (type-specific HTML template) →
  **check** (governance CI) → **publish** (write `vN/`, refresh `latest/` and history).
- **Example data label.** mvp-02 is example/test data. Any TARA built from example data carries a
  clear, unmissable "example data, not an assessment of a real product" label on every page.
- **Identities on the page.** The reviewer table renders reviewer github ids. Under the privacy
  rule (`docs/publishing/SKILL.md`, `check_identities.py`) each id shown must be on the
  `approved:` list in `publishing/identities.yaml` with sponsor sign-off, or rendered as a role
  only. The pilot uses roles plus approved ids.

## The governed record

`models/tcu/governance.yaml` is the **source of truth for approval and process flow**. PR
discussion stays on GitHub, but the YAML record is authoritative, and the published page renders
its reviewer table and change history from it.

Per document version:

| Field | Meaning |
|---|---|
| `version` | Integer N; matches `vN/` and `ThreatModel.revision` |
| `owner` | Party role responsible for the TARA (a github id or role) |
| `input_digest` | Digest of the inputs the version was built from (see decision 4) |
| `supersedes` | The previous version, or none |
| `required_reviewers` | By role: `owner`, `assessor`, `approver` |
| `reviews` | One entry per review (below) |
| `comments` | The comment log (below) |

Each **review** records: reviewer identity (github id), `actor_kind` (`human` or `ai_agent`; for an
AI agent also `model` and `run_id`), the date, and the `outcome` (`approved`,
`changes_requested`, `comment`).

Each **comment** has an `id`, the text or a link to the PR comment, a `status` (`open`,
`resolved`, `rejected`) and, when resolved, a link to the resolving commit or PR. That gives an
auditable trail: comment → change → next version.

Rules:

1. **AI reviews are recorded but never count as approval.** An `ai_agent` review with outcome
   `approved` does not satisfy a required reviewer.
2. **Final sign-off is a named human** in the `approver` role.
3. **CI blocks publish** if a required review is missing, if any comment is `open`, or if the YAML
   record and the PR approvals disagree (decision 1).
4. **Stale banner.** If the inputs change after approval, the recomputed digest no longer matches
   `input_digest`; the published page shows a stale banner until a new version is approved.

### Schema changes needed (proposals for DEC-001b, not done)

- `Review.reviews` widened to also target a `ThreatModel` or `GovernedView` **version**, not only
  an Assertion.
- A reviewer actor kind on `Review` (`human` / `ai_agent`, with model and run id for an agent).
  PR #130 proposes `PartyKind: software_agent` and Assertion provenance; the two should align.
- Comment-log objects: a `ReviewComment` (id, body or locator, status, resolved_by link) attached
  to a Review or to a governed version.
- An evidence link from `Requirement` to `ThreatModel` (decision 6).

## Decisions: proposed defaults for @nymble to confirm on the PR

Each is a **proposed default**. The pilot proceeds on these unless the sponsor changes them.

1. **Authoritative approval** = the YAML `Review` entries plus `ThreatModel.governance_status`.
   The PR's CODEOWNER approval is **also** required. CI checks that the two agree.
2. **TARA approver** = @nymble or a holder of the assessor role. `CODEOWNERS` gains a
   `/docs/models/` rule that includes @nymble (a `.github/` change, so it is the sponsor's PR).
3. **Publish approved versions only.** Drafts are PR previews (build artifacts), never written
   under `docs/models/`.
4. **Digest** = the git tree hash of the inputs (the vector, the overlay minus its review block,
   the template). Alternative: a content hash over the collected intermediate, which is stable
   across file moves but needs a canonical serialization.
5. **DEC-001b scope.** Accept `ThreatModel`, `GovernedView` and the digest rule first; leave
   `SecurityProgram`, `Checkpoint` and `RedundancyGroup` open (DL-0020 M4: exercise or drop).
6. **"An approved TARA exists"** (a process Requirement) is met through an **evidence link from
   Requirement to ThreatModel**. `satisfied_by` targets only Mitigation today, so a new edge is
   needed; the I5 Gate check evaluates it.
7. **The governed record** is as described above: versioning, owner, reviewers (human or AI, with
   actor kind), and the comment log.

## Work breakdown

Tracked as a parent issue with seven child issues (overlay and schema, collect, render, CI and
digest, 21434 content gaps, Gate check, and this note). Increments: I4 for the pilot, I5 for the
Gate check.

## Accepted (and why)

- **Overlay file, not edits to mvp-02.** Keeps the core vector core-only.
- **Immutable `vN/` plus a `latest/` copy.** Stable citations for an approved version, and a
  stable link to the current one. Copy rather than redirect, because GitHub Pages has no redirects.
- **YAML as authority, GitHub as conversation.** The record survives a move off GitHub and can be
  rendered and checked offline.

## Rejected / deferred (and why)

- **PR approval alone as the record.** Not reproducible offline, cannot carry actor kind, and is not
  in the KG.
- **Counting AI reviews toward approval.** Contradicts `CLAUDE.md` (AI output is a hypothesis
  until a human accepts it).
- **Rewriting `render_report.py` in place.** The TARA is a new type with its own template (#93);
  the Markdown report path stays as is.
- **Schema edits in this PR.** They belong in a DEC-001b ADR.

## Gate

`bin/validate-archdoc` clean. No generated files, schema or vectors change in this PR.
