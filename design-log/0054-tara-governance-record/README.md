---
schema: "archdoc/v1"
id: DL-0054
title: "Governed TARA record for the TCU, and the DEC-001b schema proposal it needs (#180, #64)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-13"
updated: "2026-11-13"
record: DL-0054
bears_on: [DEC-001, R-018, R-043]
defers_to: ARCH-0001
---

# DL-0054: governed TARA record and its schema proposal

AI-assisted design record (per `CLAUDE.md`). Student: @Maimcghee, the Schema / Storage lane owner, working with Claude Code (Opus 5.5) in one interactive session, no subagents. **Proposal only.** No `DEC-*` is accepted here; DEC-001b stays open, and nothing in `spec/schema/` changes.

## Question asked

- **#180** (DL-0027 pilot, Sprint 5): create `models/tcu/governance.yaml` for mvp-02 with version 1 as a draft, a schema for it, and a validator that passes on the file and fails on a missing field or a bad enum value. Record one AI review and one human review as examples. GitHub ids or roles only.
- **#64** (Sprint 5, pairs with #180): write DL-0027's four schema changes as a tested proposal. A Review can target a ThreatModel or GovernedView version; a reviewer actor kind (`human` or `ai_agent`, with model and run id), lined up with the `software_agent` party kind and the Assertion provenance from #130; a `ReviewComment`; an evidence link from Requirement to ThreatModel. No edit to the accepted core, no ADR. The example governed record from #180 must validate against it.

## What was produced

| File | What it is |
|---|---|
| `spec/vectors/example-container-governance.linkml.yaml` | The proposal (#64) and the record's schema (#180): enums, `Proposed<Class>` subclasses carrying each change, `ReviewComment`, and the container class `ExampleModelGovernance` |
| `models/tcu/governance.yaml` | The governed record for the TCU TARA: version 1 (draft), four role parties, two reviews, a comment log of two, and the evidence chain to an "approved TARA" requirement |
| `docs/publishing/check_governance.py` | The validator: LinkML against the container, then the rules the schema cannot state |
| `docs/publishing/test_check_governance.py` | 16 tests: the record passes, a missing field and a bad enum value fail, and one test per rule |
| `docs/publishing/SKILL.md` | One row for the new check |

## The proposal (#64)

A container cannot change an imported class, so, as DL-0040 kept its SDL classes out of `spec/schema/`, each changed class appears as a `Proposed<Class>` subclass carrying the change. A DEC-001b ADR that accepts it folds each subclass into its parent and drops it.

| # | DL-0027 asks for | Proposed as | Why this shape |
|---|---|---|---|
| 1 | Review of a governed **version**, not only an Assertion | `ProposedReview.reviews` widened to Assertion, ThreatModel or GovernedView; `review_outcome` (approved / changes_requested / comment); `reviewed_at` | Widening is additive: every existing Review still validates. The brake-ECU example shows the need: `tv-hardware-brake-ecu.yaml` approves its ThreatModel through a stand-in Assertion (`assertion:tm-hw-scope`) because a Review could not point at the version |
| 2 | Reviewer actor kind, with model and run id for an agent | The **reviewer Party's `party_kind`** (`person` or `software_agent`, ADR-0011 A5), plus `agent_model` and `agent_run_id` on the review | Lines up with #130 as #64 asks: the kind lives on the identity, exactly as for an Assertion's `asserted_by`, so no second enum says the same thing. The model and run vary per review, so they sit on the review |
| 3 | Comment log | `ReviewComment`: `comment_on` (a Review or a version), `comment_locator`, `comment_status` (open / resolved / rejected), `resolved_by`; the text in `description` | DL-0027's fields, with the PR or issue URL as locator so the record works offline and links back |
| 4 | "An approved TARA exists" as evidence for a Requirement | `ProposedEvidence.evidence_of` (ThreatModel or GovernedView), on ADR-0013's `Evidence` | See the first decision below |
| 5 | (not in DL-0027's list) required reviewers by role | `ReviewRole` (owner / assessor / approver), `ProposedThreatModel.required_review_roles`, `ProposedReview.reviewer_role` | DL-0027's record holds "required reviewers by role" per version, and the publish gate (#183) needs it, but its list of schema changes leaves it out |

## The governed record (#180)

`models/tcu/governance.yaml` governs `spec/vectors/mvp-02-automotive-ecu.yaml`, named in its `governs` field.

- **Version 1** (`threat-model:tcu-tara-v1`) lists as `members` the 13 mvp-02 objects behind the clause 15 work products the TARA page shows: the product, both assets, the damage scenario, both threat scenarios, both attack paths, the risk score, two mitigations and two technical requirements. Draft, approval pending, needing owner, assessor and approver.
- **Parties are roles** (`party:tara-owner`, `party:tara-assessor`, `party:tara-approver`) plus `party:claude-code` as a `software_agent`. No person is named.
- **The AI review is real.** Claude Code reviewed version 1 against mvp-02 and the TARA page's gap list in this session (`agent_run_id` is the session id) and asks for one change. The TARA page's clause 15.8 gap says the risk metric is still open (DEC-003), but ADR-0006 accepted it on 2026-10-08, and mvp-02's risk score cites ADR-0006 and reads its values from Table H.8. #232 fixed the same claim in DL-0037 but not on the page. That is the open comment.
- **The human review is an example, and says so.** #180 asks for one, and a record that claims a person reviewed something they did not would defeat its purpose. So the owner-role review's text says "EXAMPLE ENTRY ... not a real review", to be replaced by the owner's own before version 1 leaves draft.
- **The resolved comment is real history.** @Clovier's clause 15 gap table on #184 found that mvp-02 had no assets; #209 added them. It shows the trail DL-0027 asks for: comment, then change, then version.
- **The evidence chain** exercises change 4: `requirement:tcu-approved-tara` (authored, process) ← implements, `sdl-practice:tcu-threat-modeling` produces → `evidence:tcu-tara-v1`, evidence_of → version 1. The requirement is met only once version 1 is approved.

## The check

`check_governance.py` runs LinkML first (missing required fields, values outside an enum), then rules:

- ids are unique, and every reference resolves to an object of the right kind, in the record or in the governed model (members, requirement links);
- a review of a version has an outcome;
- an AI agent's review names its model and run and fills no role; a person's review of a version fills a role and names no model; an organization cannot review;
- a resolved comment names its fix, and only a resolved one does;
- a version has a whole-number revision and required roles, supersedes an earlier revision, and once approved has a digest and is approved only by people's `approved` reviews of it.

The publish gate (a role unfilled, an open comment, YAML and PR approvals disagreeing) and the input digest are #183's.

## Decisions made while drafting, and why

1. **Change 4 uses ADR-0013's `Evidence`, not a new Requirement edge.** DL-0027 (2026-10-27) proposed an evidence link from Requirement to ThreatModel because `satisfied_by` takes only a Mitigation. ADR-0013 (2026-11-07) then accepted `Evidence`, with `evidence_kind: model`, `digest`, `about_version` and `fresh_until`, reached from a Requirement through `SdlPractice.implements` and `produces`; sdl-01 already records a threat model that way (`evidence:sdl-01-threat-model`). One typed `evidence_of` link from that Evidence to the version gives DL-0027 decision 6 its path and reuses the digest and freshness fields the stale-banner rule needs. **For @nymble to choose:** this, or DL-0027's direct `Requirement.evidenced_by` → ThreatModel, which is one hop instead of three but duplicates what ADR-0013 accepted.
2. **No `actor_kind` enum.** PartyKind already has `person` and `software_agent`. A second enum on Review could disagree with the reviewer's own kind.
3. **`review_outcome` beside `review_status`, not instead of it.** Reviews of Assertions use `review_status` with accepted / changes_requested / rejected (32 uses across the vectors). A version review's outcomes differ (approved / comment). One slot for both is possible in the ADR; here they stay apart so no existing vector changes.
4. **An AI review fills no role, structurally.** DL-0027 rule 1 says an AI approval never satisfies a required reviewer. The check makes that impossible to write: a `software_agent` review with a `reviewer_role` fails.
5. **Version scope by `members`, checked against the governed model.** `scope_query` has no evaluator yet, so explicit members are the only scope the check can verify.
6. **The check lives in `docs/publishing/`,** beside `check_links.py` and `check_identities.py`, because it is the "check" step of DL-0027's collect, render, check, publish flow, and #183 extends it into the gate.
7. **Not in CI yet.** Wiring it in needs a `.github/` change, which is @nymble's (CODEOWNERS), and #183 adds the CI job that runs on `models/` changes. Locally it runs with LinkML from `spec/schema/requirements.txt`.

## What a human accepted

Nothing yet. @Maimcghee reviews the PR. @nymble decides the proposal (all five changes, and decision 1's choice) in a DEC-001b ADR, since `spec/` changes need the sponsor's review (CODEOWNERS).

## Rejected, and why

- **Editing `spec/schema/` directly**, as DL-0024 did before ADR-0011: #64 and #180 both say not to.
- **A copy of the core schema with the changes applied:** it would drift from the core, and a reviewer could not see what changed.
- **A fabricated human review in a named person's name:** a governed record exists to say truthfully who approved what.
- **Keying the record by file path instead of ids:** ids are stable across moves (ADR-0004), paths are not.

## Left out (other issues)

- Input digest and the publish gate: #183. `approval_digest` stays empty while version 1 is a draft.
- Published `vN/`, `latest/` and history pages: #181, #182.
- A `/docs/models/` CODEOWNERS rule for the approver (DL-0027 decision 2): @nymble's `.github/` change.
- The I5 Gate check that evaluates "an approved TARA exists".
- Fixing the TARA page's DEC-003 line (the open comment): a small separate change to `docs/publishing/tara.yaml`.

## How it was checked

- `linkml-validate` (LinkML 1.12.1, pinned): the record validates against `ExampleModelGovernance`. A copy with `review_outcome: lgtm` and one without `comment_status` both fail.
- `check_governance.py`: the record passes both passes.
- `test_check_governance.py`: 16 passed with LinkML; without it the 5 schema tests skip and the 11 rule tests pass. `ruff check` and `ruff format --check` with the engine's settings are clean.
- The four mvp vectors still validate against the core container, unchanged.
- `linkml-lint` on the container: only "recommended description" warnings on the collection slots, as on the other containers.
- `bin/validate-archdoc`, `check_identities.py`, `check_links.py`: clean.
