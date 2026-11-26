---
schema: "archdoc/v1"
id: DL-0059
title: "TARA publish gate and input digest: the check step of the governed TARA pilot (#183)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-20"
updated: "2026-11-20"
record: DL-0059
bears_on: [DEC-001, R-018, R-043]
defers_to: ARCH-0001
---

# DL-0059: TARA publish gate and input digest

AI-assisted design record (per `CLAUDE.md`). Student: @Maimcghee, the Schema / Storage lane owner, working with Claude Code (Opus 5.5) in one interactive session, no subagents. No `DEC-*` is accepted here. The gate enforces DL-0027's proposed defaults as written, so it changes if the sponsor changes them.

## Question asked

**#183** (DL-0027 pilot, Sprint 6, after #180):
- a script that computes the input digest, the git tree hash of the inputs (DL-0027 decision 4);
- a check that fails when a required review is missing, when only an AI review approves, when a comment is open, or when the YAML approval and the PR approval disagree;
- the check runs on PRs that touch `docs/models/` or `models/`;
- a test for each failure case and a passing one, and one that edits an input and gets a new digest;
- the workflow change goes to @nymble for review (CODEOWNERS `/.github/`).

## What was produced

| File | What it is |
|---|---|
| `docs/publishing/input_digest.py` | The digest of each governed version, `git-tree:<sha1>`, and `--list` to show what it covers |
| `docs/publishing/check_publish.py` | The publish gate, for each version a record publishes |
| `docs/publishing/test_input_digest.py` | 17 tests, including that the digest is the tree `git write-tree` makes from the same files |
| `docs/publishing/test_check_publish.py` | 28 tests: the passing case, each failure, and the PR and CODEOWNERS rules |
| `.github/workflows/tara.yml` | The CI job: `check_governance.py`, the tests, then the gate with the PR's reviews |
| `docs/publishing/SKILL.md`, `check_governance.py`, `models/tcu/governance.yaml` | Two rows for the new scripts; comments that pointed to #183 now point to them |

## The digest (DL-0027 decision 4)

A version's digest is the git tree hash of three things:
- **the vector** the record `governs`, as committed;
- **the version's own entry** in the record, without the fields that change when it is approved (`approved_by`, `approval_status`, `approval_digest`, `governance_status`, `updated`), as canonical JSON;
- **the TARA template**: `render_tara.py` and `tara.yaml` today.

The tree is built as git builds one, so `git write-tree` over the same files gives the same id. A test holds that, with names chosen so that git's sort order for directories matters.

## The gate

A version is **published** when the record approves it (`governance_status: approved`) or it has pages under `docs/models/<item>/tara/v<N>/`. Drafts with no pages are not published, so the gate passes them and `check_governance.py` still checks their record. For a published version, the gate fails when:

| #183 asks | The gate fails when |
|---|---|
| a required review is missing | a role in `required_review_roles` has no person's review of the version, or that role's latest review is not `approved` |
| only an AI review approves | an AI agent's review approves and no person's does (DL-0027 rule 1) |
| a comment is open | a comment on the version, or on a review of it, is `open` (rule 3) |
| the YAML and the PR disagree | the version has pages the record does not approve; or the record approves it and no code owner of the record approves the PR at its head commit; or a reviewer's standing verdict on the PR is "changes requested" (decision 1) |
| (rule 4) | `approval_digest` is missing, or is not the digest of today's inputs |

The PR and digest rows apply to what the PR publishes: a version the PR newly approves, compared with the record on the base branch, or one whose pages the PR changes. A version approved in an earlier PR whose inputs have since changed is reported **stale**, for the page's stale banner (rule 4), and does not fail.

**PR verdicts** follow GitHub's own counting. A comment doesn't replace an approval, and a dismissal does. An approval counts only on the head commit. Bots and the PR's author are left out. **Code owners** come from `.github/CODEOWNERS`, where the last matching line wins.

## The CI job

`tara.yml` runs on every pull request, and again when a review is submitted or dismissed, since the gate reads the PR's approvals. Its first step lists the PR's files and stops unless one is a governed TARA or one of its inputs. That list is `models/`, `docs/models/`, mvp-02, the governance container, the three checks and their tests, the TARA template, CODEOWNERS and the workflow itself.

The job has read-only permissions, and its actions are pinned to the same SHAs as `ci.yml`. Event values reach the shell only through `env`.

## Decisions made while drafting, and why

1. **The version's own entry, not the whole record minus its reviews.** DL-0027 says "the overlay minus its review block". The other versions, the comment log and the evidence chain are about approving, not about what the version shows. If they were in the digest, writing a version 2, or resolving a comment after approval, would mark version 1 stale.
2. **The template is today's renderer and page text.** `render_tara.py` and `tara.yaml` make the clause 15 page (DL-0037). The `vN/` template is #182's, and `TEMPLATE` changes when it lands. #181's collector (`engine/engine/tara.py`, PR #242) joins it once the page is built from it.
3. **Only what is published is gated.** If drafts were gated too, every edit to a draft record would fail CI, since a draft is by definition not yet approved.
4. **A role needs an approval, not just a review.** "A required review is missing" is read as: each required role's latest review by a person approves the version. A role whose latest review requests changes blocks too.
5. **The PR side is checked through CODEOWNERS, not through the record's roles.** The record's reviewers are roles (`party:tara-approver`), and `Party` has no slot for a GitHub account, so the gate can't tell which PR approver holds which role. Instead it asks for a code owner's approval of the record (decision 1), and DL-0027 decision 2's `/docs/models/` rule would make that the sponsor. **For @nymble:** keep this, or add an account slot to Party in DEC-001b so the two sides can be matched by name.
6. **An earlier version going stale is a note, not a failure.** Rule 4 asks for a banner, not a block, and a block would stop unrelated changes to mvp-02.
7. **No `paths:` filter.** A `pull_request_review` event can't take one, and the gate has to run again when an approval arrives. The first step does the filtering instead.
8. **Run locally, the PR side is skipped, and the report says so.** In CI the job always passes the PR's reviews.

## What a human accepted

Nothing yet. @Maimcghee reviews the PR. @nymble reviews the workflow (CODEOWNERS `/.github/`) and decision 5.

## Rejected, and why

- **DL-0027's alternative, a content hash over the collected intermediate.** It needs #181's collector to be merged and its output stable. The tree hash needs neither and can be checked with git.
- **Hashing `governance.yaml` as committed.** Writing the approval into the record would change the digest it records.
- **Gating on `pull_request` with `paths:` only.** A later approval wouldn't re-run the check, so a PR would keep a stale result.

## Left out (other issues)

- The stale banner on the page, and the publish step that writes `vN/`, `latest/` and history: #182.
- The `/docs/models/` CODEOWNERS rule naming the approver (DL-0027 decision 2), and making `TARA publish gate` a required check: both @nymble's.
- The I5 Gate check that evaluates "an approved TARA exists" (#185).

## How it was checked

- `test_input_digest.py` and `test_check_publish.py`: 45 passed. The whole `docs/publishing/` suite passes with LinkML installed, as the CI job runs it.
- The digest of the TCU's version 1 equals `git write-tree` over the same files.
- `check_publish.py --base origin/main` on today's repo: ok, version 1 is a draft and not published.
- `check_governance.py`: the record still passes. `ruff check` and `ruff format --check` with the engine's settings are clean.
- `bin/validate-archdoc`, `check_identities.py`, `check_links.py`: clean.
