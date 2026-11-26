---
schema: archdoc/v1
id: DL-0066
title: Approved and current TARA criterion for the governance pilot
type: process
status: draft
version: "0.1.0"
date: "2026-11-22"
updated: "2026-11-22"
human_owner: paria03
defers_to: ARCH-0001
---

# Question and scope

@paria03 requested #185: evaluate whether a human-approved, current TCU TARA
exists, using the governance overlay (#180), input digest (#183) and evidence
link from DL-0027 decision 6, with a result for the history page (#182).

The dependency PRs #251 (`0a6c67e`) and #253 (`52af474`) are approved but open.
This local branch is stacked on #253 and integrates main at `8351701` in
`94f8c5c`. It does not merge or edit either remote branch. The governance record
stays a draft; its example review and unresolved comment are not manufactured
approvals or automatically resolved by this task.

# Architecture and unresolved choice

ARCH-0001 retains Gate, governed-version approval and the rest of DEC-001b as
proposals. DL-0027 decision 6 proposes a direct Requirement → ThreatModel edge;
DL-0054 decision 1 instead proposes ADR-0013's Evidence chain with a new
`evidence_of` binding. #251 explicitly asks the sponsor to choose; neither its
student approval nor this implementation is a DEC/ADR acceptance.

The checker therefore requires the caller to specify `direct` or
`evidence-chain`, with no default or fallback. It can exercise either operation
without claiming a policy selection. The actual #251 record exercises the
Evidence chain. The direct edge is tested only in a synthetic engine fixture;
it still needs the matching schema decision before use in a validated record.
No accepted schema or architecture document is changed.

# Implementation

- `engine.tara_gate.evaluate` and `core.evaluate_tara_gate` compute a deterministic,
  read-only exit-criterion result. A Gate targets one ThreatModel; every gated
  Requirement needs a typed evidence path to that version. Model evidence also
  binds its revision. Assertions are not silently written into link slots.
- Required roles need their latest person's approval, including an approver;
  `approved_by` must include that current approver. Both approval status fields
  must agree, all relevant comments must be closed, and the approved/current
  digests must match. AI reviews cannot fill a human role. Timestamps are compared
  as instants; equal-time contrary verdicts fail without using file order.
- `check_tara_gate.py` validates the record with #180's existing schema/rule
  checker and validates the pilot Gate shape. It recomputes the digest through
  #183's existing `input_digest.digest`; it accepts no caller-supplied current
  digest at the file boundary. Input paths remain confined to the source root.
- The DTO and escaped `render_history_status` section are #182's consumer hook.
  A new local HTML preview can demonstrate the result outside published `docs/`.
  This does not create a substitute versioned renderer or publish an unapproved
  draft. The prototype Gate retains its stored `gate_status: planned`.
- Extend #183's workflow scope and tests to exercise this pilot and its adapter
  with the pinned LinkML environment. Workflow review remains subject to
  CODEOWNERS; no branch-protection or publication setting changes.

The query's `passed` result means only the recorded TARA exit criterion is met.
It does not decide Gate passage, authenticate an identity, validate mitigation
adequacy or certify product conformance. The #183 publish guard separately checks
the PR side: a draft may be safe not to publish while failing this criterion;
an approved but stale version fails this criterion even on an unrelated PR.

# Rejected or deferred

| Option | Outcome and reason |
|---|---|
| Treat an approved code review as the sponsor's evidence-link/DEC choice | Rejected: the choice is explicitly open in #251. |
| Guess the evidence route from whichever links happen to exist | Rejected: it hides the unresolved policy choice. |
| Copy #183's digest algorithm | Rejected: reuse its function and test actual input changes. |
| Use the publish guard's successful draft result as proof that a TARA exists | Rejected: an unpublished draft is not an approved, current TARA. |
| Mark the real example approved so the demonstration passes | Rejected: all passing approvals are synthetic, isolated test data. |
| Resolve a tied review by list order | Rejected: conflicting equal-time human evidence fails. |
| Write a formal Gate decision, change core schema, or publish `vN/latest` | Deferred to the accepted governance decision, actual human reviews and #182. |

# Validation

The regression plan includes pass, draft/no-human approval, stale vector and
template inputs, AI-only reviews, missing roles, contrary/tied human reviews,
wrong version/evidence binding, status disagreement, invalid input and path
confinement, no mutation, deterministic output, CLI exit codes and safe history
HTML. Validate the stacked governance/digest/publish checks and the normal
engine/app/publishing suites before proposing the change.

Local validation on Python 3.13:

- **639 engine tests passed, five opt-in packaging checks skipped**; the full
  pinned CWE release was enabled. A rebuilt sidecar then passed all **five
  packaging checks**. Engine lint and formatting passed.
- **98 publishing tests passed** with the pinned LinkML environment. There are
  **37 new focused cases** across the engine criterion and file/history adapter.
  The inherited governance, digest and publish-guard tests remain passing.
- Frontend typecheck/build and **456 tests passed**. Rust fmt/clippy and **four
  tests passed**. Archdoc has 28 documents and zero errors; publishing identities,
  links and preview freshness pass (nine models, 685 library records). The
  unchanged pinned library has zero errors and 99 existing warnings.
- Generated schemas are current. All workflow shell blocks parse, and ten
  positive/negative path-filter cases agree. No actual schema, vector, governed
  record, version page or browser-preview asset changed in this feature.
- The real draft produces an unmet criterion and a local history preview. The
  browser view shows its missing roles, example owner review, open comment and
  missing approval digest; the evidence details show the recomputed digest and
  “Not recorded” for approval. The real record is byte-identical to #253's source.
- Temporary browser/server resources were closed after verification. Remote CI
  has not run for this local-only feature; it must be checked after an authorized
  push/PR.

# Human accepted / rejected

@paria03 requested implementation. No human has approved this code, selected the
evidence-link policy, accepted a governance schema, or approved the TARA version
through this task. #185 remains open until those dependencies and the real
history-page integration are satisfied.
