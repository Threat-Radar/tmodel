# #289 — Local human review backend

## Request

Start #289: implement human review and annotation of attack paths, including
corrections, scoped ratings, atomic persistence and consistent risk/view refresh,
while #288 supplies workspace storage and #290 supplies the interface.

## Produced

- Storage-neutral review service using the existing Review, Assertion, Party,
  AttackPath and RiskScore schema, plus the existing #63 calculation.
- Proposed workspace protocol with explicit schema validation, immutable revision
  history and atomic compare-and-save responsibilities for #288.
- Opt-in authenticated local operations; normal startup remains read-only until
  the desktop host supplies a verified session and real workspace adapter.
- Exact route/Assertion binding, correction of one's own review, scoped rating
  updates, structured errors and same-revision report/graph/path/risk results.
- Shared contract, synthetic YAML/JSON examples and automated service/HTTP checks.
- Reused the existing report summary calculation for supplied workspace documents.

This branch includes #269's pending exact-link/risk-scope fixes as a dependency.
No canonical proposal acceptance, schema change or physical storage implementation
was added. The initial implementation left the concrete #288 adapter and native
session integration pending. The follow-up below supplies the contract adapter
and native commands; activation still requires #288. The local identity policy
is proposed for team review, not an accepted ADR.

## Human acceptance and rejection

The user authorized starting #289. No human review of this implementation, API
contract, workspace interface or identity integration has been recorded yet.
The example review verdicts are synthetic test inputs, not human sign-offs.
The user subsequently authorized the initial push and draft PR #291. These
authorizations do not grant permission for later pushes.

## Validation

- Full engine suite: 900 passed, 10 skipped, including 51 new service/HTTP checks.
- Ruff lint and format checks passed; in-process CLI health passed.
- Pinned LinkML validator accepted the initial synthetic model, a saved review
  and rating update, and a revision with cleared feasibility/impact ratings.
- Existing TypeScript report builder consumed the saved-revision report DTO.
- TypeScript/Pages build and generated preview freshness passed without changes
  to published artifacts (10 models, 685 library records).
- Architecture validation, published identity/link guards and whitespace checks
  passed. The pinned library validated with zero errors and 99 existing warnings.

Production save/reopen and packaged-app review testing require #288 and #290
integration. The initial draft PR subsequently passed all 13 hosted checks on e30dc7f.
Those checks do not validate the later local follow-up below.

## PR integration with current main

Opening the draft PR exposed generated-preview conflicts with the branding and
welcome changes merged in #278. Merged current main without changing those
source features, then regenerated the preview using the publishing playbook.
No authored source conflicts required manual resolution. Type checking, all
701 frontend tests, 124 publishing tests, preview freshness, architecture and
published identity/link guards passed. The #289 engine implementation is unchanged.
Whitespace checks against current main passed for authored files; generated
bundled JavaScript retains its upstream template whitespace.


## Earlier finish request: project adapter and native host follow-up

Historical status before #298 merged; the integration below supersedes its pending list.

The user requested finishing #289. Reviewed issue #288 and the published #290
screens in PR #295 (de70e15), including its copy of the workspace contract. The
actual #288 storage implementation is not in any published branch inspected;
#295 describes it as a separate worktree dependency. Its source is required to
finish real persistence integration. The user confirmed that the teammate is
still working on #288; no parallel physical store was created.

Produced locally:

- Merged #269's latest exact damage-scope and human review projection fixes
  (d5647ff); regenerated the browser preview to resolve generated-file conflicts.
- `ProjectReviewWorkspace` delegates to the published `save_version` contract,
  storing optional descriptions and calculated-risk summaries with review changes
  in one operation. The summary retains incomplete counts and unknown categories.
- Imported/read-only models can refresh without an existing reviewer Party.
  Only a verified native principal can create its own person Party on first save,
  in the same candidate as the review/rating updates. Existing agent/organization
  Parties cannot be reclassified; previous documents and provenance are preserved.
- `HostReviewAPI` binds the private native session to the real OS user's
  installation identity and only the host's registered opaque model IDs. It does
  not grant canonical proposal acceptance.
- Native `project_host_session` and `project_host_step` implement #290's command
  names, native path pickers and approved source forms. A fresh HMAC challenge
  verifies the owned engine before revealing its bearer token or selected paths.
  An unrelated/external engine gets no session. Private reviewer identity persists
  across launches; session tokens change per launch. A read-only engine declines
  the session immediately, preserving the existing app startup.
- Bounded draining of modest oversized review requests preserves the structured
  validation error instead of resetting the connection with unread body bytes.
- Regenerated the shared synthetic response after #269's graph changes; its test
  now compares the entire deterministic save response, including all refreshed views.

Validation of the local follow-up:

- Full engine suite: 919 passed, 10 skipped; 59 targeted service/HTTP checks.
- Frontend type check and all 709 tests passed.
- All 124 publishing tests passed; preview freshness, architecture validation,
  published identity/link checks and authored whitespace checks passed.
- Pinned LinkML validation accepted a saved model containing the native host's
  reviewer Party and Review. This validates the candidate schema, not disk storage.
- Nine native unit tests pass. Native formatting and Clippy with warnings denied
  are checked separately. Native checks use a Tauri configuration override with
  no external binary; they do not claim a packaged C7 end-to-end test.

Still required before #289/C7 can be marked complete:

1. Obtain #288's actual implementation, verify the adapter against it, and wire
   `HostReviewAPI` into its server and trusted opened-model registry.
2. Enable `serve --projects` in the native launcher when #288 supplies that flag.
   Passing it before the dependency exists would break ordinary app startup, so
   this follow-up deliberately leaves the launcher in read-only mode.
3. Test real YAML save/reopen, immutable history, stale/concurrent saves and failed
   writes through the production workspace, with full schema validation.
4. Integrate #295, regenerate its additional revision fixture, and ensure version
   history reads the saved assessment/incomplete counts (its current metadata
   parser only reads derived_risk). Exercise actual native pickers and the complete
   review/rating/save/recalculation flow in the packaged app.

This follow-up remains local pending authorization to push. The existing PR stays
in draft; neither storage-double tests nor earlier hosted CI establish completion.


## Runtime integration after #298

The user requested continuing #289 after #288's implementation became available.
Merged current main (including #298) and the exact #301 schema-validation follow-up
(8cb60a4) as a dependency. #301 must merge before this PR: activating project writes
in a standalone engine without its schema check would not meet #288's acceptance
criteria. No change was made to the separate storage implementation.

Produced:

- `make_desktop_server` configures one real `ProjectWorkspace`, its workspace
  routes, and the native `HostReviewAPI` over the same registry. `serve` uses the
  factory. The CLI reads the host identity only with `--projects`; a token alone
  retains workspace operations without granting review permissions.
- The native launcher now enables `--projects` when it has private credentials.
  Missing private identity storage preserves read-only browsing. Existing external
  engines receive no native write grant.
- Aligned optional version descriptions with #288's 500-character limit. Longer
  or blank descriptions fail before writes; rationale/annotation limits stay 4096.
- Eight production-workspace integration cases cover a combined review/rating
  save, all four views at one revision, a review correction, persistent history,
  exact reopening after a server restart, immutable original/earlier versions,
  stale/concurrent saves, failed disk writes, permissions and host CLI identity.
- Added a packaged-engine regression: copy only the executable to a temporary
  directory, with no system Python on PATH or LinkML, verify the native-session
  proof, create a project from a YAML source, save review/rating changes, reject a
  stale save, restart and reopen the exact same saved response.
- Updated HUMAN_REVIEW.md to describe the active runtime rather than manual future
  wiring. Compared #295's published r1 refresh/r2 context fixture with the backend;
  it still matches, as does the complete shared save response.

Validation:

- Full Python 3.13 engine suite: **1457 passed, 14 skipped** without LinkML, after
  installing current main's newly required pyoxigraph dependency. The first run
  stopped at collection because the older validation environment lacked it; this
  was an environment dependency, not a test assertion failure.
- Targeted workspace/review checks: **47 passed**. The eight new real-workspace
  cases also passed with pinned LinkML validation enabled.
- Standalone engine build and all its smoke checks passed; **8 packaged tests
  passed**, including the new authenticated review/restart/reopen case.
- **9 Rust tests**, Rust formatting and Clippy with warnings denied passed using
  the actual built sidecar; the debug macOS app bundle built successfully.
- Type checking and **709 frontend tests** passed; **124 publishing tests**,
  preview freshness, architecture and published identity/link checks passed.

The backend can now be reviewed against real storage. The PR still depends on
#269 and #301; do not merge it ahead of those dependencies. C7's frontend/native
picker rehearsal belongs to the combined #290/#295 integration and is not claimed
by the backend/package tests. In particular, #295's persisted-summary parser
should retain assessment/incomplete counts, not just category values.

No new human verdict or implementation approval is recorded. These updates remain
local until the user authorizes pushing them to the existing draft PR #291.
