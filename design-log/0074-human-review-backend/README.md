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


## Finish request: project adapter and native host follow-up

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
