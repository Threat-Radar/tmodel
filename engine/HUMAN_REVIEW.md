# Local human review API — #289

This is an implementation contract for C7, using the existing schema and risk
engine. The workspace protocol is **proposed for integration with #288**; it is
not a decision about storage location, version history format, or desktop login.
The frontend integration belongs to #290. Merge #288, then #289, then #290.
This branch also depends on the exact relationship and risk-scope fixes in #269.

## Integration status

The review service and opt-in HTTP operations are implemented and tested with a
storage test double. There is no production workspace adapter in this change.
The normal desktop launch remains read-only. Before enabling the workflow:

1. Implement/adapt `ReviewWorkspace` in #288, including full schema validation,
   atomic compare-and-save, immutable previous revisions and editable-copy checks.
2. Have the trusted desktop host verify the user, bind that identity to an existing
   human Party and grant explicit model access and actions. An arbitrary name or
   Party ID supplied by a webview is not identity verification. This binding and
   secure session delivery need team agreement and launcher integration.
3. Inject `ReviewAPI(ReviewService(workspace), sessions)` into
   `make_server(review_api=...)`. Sessions map host-generated random bearer tokens
   (at least 32 characters, e.g. `secrets.token_urlsafe(32)`) to `ReviewPrincipal`.
   Tokens stay in process memory, must not be logged or put in URLs/YAML, and last
   only for that server session. The host grants `read`, `review`, and/or `rate`
   explicitly; Party classifications do not grant permissions.
4. Connect #290 to the operations below, verify real save/reopen and conflict
   behavior, and rehearse with the packaged desktop app. Do not mark C7 complete
   based on the storage test double.

There is no endpoint to create a privileged session or accept a canonical
proposal. Bundled examples must first be copied using #288's copy operation.

## Operations

All operations use JSON POST requests and `Authorization: Bearer <session>`.
The existing GET API and approved-vector restrictions are unchanged. Requests
with a foreign Host or Origin are rejected, including when a token is supplied.
Tauri production/dev origins support preflight; a local native client can omit
Origin but still needs a token. Requests are bounded to 256 KiB and 100 changes
of each type, with unique JSON keys and no nonfinite numbers.

| Shared name | HTTP route | Revision field | Result |
| --- | --- | --- | --- |
| getReviewContext | `/reviews/context` | `revision` | Targets, provenance, current reviews/history, ratings, actions |
| submitReview | `/reviews/submit` | `expected_revision` | Saved revision and all refreshed views |
| saveRatings | `/reviews/ratings` | `expected_revision` | Saved revision and all refreshed views |
| saveModelChanges | `/reviews/changes` | `expected_revision` | One atomic review/rating save and all refreshed views |
| refreshModel | `/reviews/refresh` | `revision` | All views from that exact saved revision |

Use `saveModelChanges` for a Save button that includes reviews and ratings.
Calling submitReview and saveRatings in succession is not an atomic combined save.
Successful responses always include `model_id` and `revision`.

Context and save requests identify `model_id`, the appropriate revision field,
`matrix`, `threat_id` and `route_id`. The matrix must explicitly be
`annex-h-table-h8` (the existing illustrative table profile). Route IDs come from
#63's calculated risk response; do not construct them from display labels.
`refreshModel` needs only model_id, revision and matrix; it accepts the selection
fields as well. No operation accepts a filename, path, claimed reviewer identity,
role, Assertion status change or arbitrary document patch. Unknown fields fail
validation rather than being silently ignored.

## Save payload

The common selection fields are followed by any of these lists:

```json
{
  "model_id": "local:one",
  "expected_revision": "r1",
  "matrix": "annex-h-table-h8",
  "threat_id": "threat:t",
  "route_id": "route:<id returned by risk calculation>",
  "reviews": [{
    "assertion_id": "assertion:path",
    "verdict": "accepted",
    "rationale": "Explain the human decision here.",
    "annotation": "Optional note."
  }],
  "feasibility": [{"attack_path_id": "path:a", "rating": "high"}],
  "impacts": [{
    "risk_score_id": "risk:r",
    "damage_scenario_id": "damage:d",
    "stakeholder_id": "party:reviewer",
    "values": {"safety": "severe", "privacy": "major"}
  }]
}
```

The full executable fixture and context/save/error mocks are in
[`examples/human-review/contract.json`](examples/human-review/contract.json).
They contain synthetic test judgments, not project sign-offs. No credentials are
included. The initial YAML is in the same directory.

### Exact review targets and permitted corrections

Context resolves a computed route to all unambiguous authored `rating_paths`.
It offers exact Assertions for those paths' `realizes_threat` relationship to the
selected threat, plus Assertions whose subject is that threat. It returns the
whole Assertion so the UI can show subject, predicate and object before a verdict.
The client must select an Assertion ID, never just a displayed route label.

Broad OR paths do not provide a per-alternative rating or review target. Context
reports `route_specific_path_required` when no unambiguous authored path exists;
a model author must supply separate route records before rating an alternative.
This API does not create graph structure to resolve that ambiguity.

Verdicts are `accepted` or `rejected`; rationale is required and nonblank. Rationale
and annotations are limited to 4096 characters each. The server creates the Review
ID and binds `reviewer` to the verified principal. An annotation uses the existing
`Review.description`; rationale uses `Review.justification`.

To correct a review, send its `review_id` together with the exact Assertion ID.
Only the authenticated person's matching review can be corrected. Other reviews
remain unchanged. An existing own review cannot be silently replaced by omitting
its ID. Omitting annotation preserves an existing note; an empty string clears it.
Duplicate updates to the same target in one request fail validation.

A correction changes that Review in the new document revision. The previous
revision retains its original content. Context history shows each distinct review
version and the revision where it first appears, through the requested revision.
No new schema fields, timestamps, supersedes links or deletion operations are
invented. Assertion status, evidence, asserted_by/at and generated_by are preserved.
A local accepted verdict never calls `tmodel accept` or promotes a proposed
Assertion to canonical accepted status. Existing review-state rules still apply.

### Rating scope

Feasibility is stored on the selected route's authored AttackPath:
`high`, `medium`, `low`, `very_low`, or null to clear. A broad OR rating cannot be
assigned to one alternative. If multiple authored records own the same route,
conflicting or missing ratings stay unresolved until the author explicitly fixes
them; saving one value does not overwrite the other records.

Impact is a partial S/F/O/P update to one existing RiskScore. The score must belong
to the selected threat, and its damage scenario and stakeholder must match the
request exactly (including null if originally absent). Values are `negligible`,
`moderate`, `major`, `severe`, or null to clear. Omitted categories keep their
existing values; an absent category is never invented. Do not merge stakeholder
scopes. Changing a stakeholder, damage link or graph structure is outside C7.

## Workspace and consistency contract

`engine/review_workspace.py` defines `ModelRevision`, `ReviewWorkspace`,
`ReviewPrincipal` and structured `ReviewError`. The required adapter operations:

| Operation | Guarantee |
| --- | --- |
| read(model_id, revision) | Isolated document for exactly that revision, with editable flag |
| history(model_id, revision) | Ordered snapshots through that revision, no later/foreign content |
| validate(document) | Full selected ExampleModel container/schema validation |
| commit(model_id, expected_revision, document) | Revalidate and compare current revision atomically; retain old revisions; return new revision |

IDs and revisions are opaque strings, at most 256 characters. Physical paths are
never frontend identifiers. The adapter must not alter the candidate on commit.
If a model disappears or a revision is unavailable, raise `not_found`. On a stale
save, raise `revision_conflict` with `current_revision`; no write may occur. On
schema failure raise `validation_error` with the affected field. On I/O failure
raise `save_failure`. Error messages must not expose paths or credentials.

The service detaches a candidate, checks permissions and exact targets, validates
all changes and derives all views **before** the atomic commit. Thus an analysis
failure cannot save a partly applied update. A successful response uses those
same candidate views tagged with the newly saved revision, never a later reread.
Refresh reads an explicit revision, not the latest model behind the client's back.

A success response includes:

- `graph`: existing graph projection plus model_id/revision and an opaque file label.
- `attack_paths`: model_id/revision and per-threat `responses`.
- `risk`: existing calculated-risk response plus model_id/revision.
- `report_data`: a complete existing frontend `ModelReportInput`, with model_id and
  revision added. Its model summary/counts, graph and attackPaths all derive from
  the candidate. The frontend can call its existing report builder on this object.

The `file` values in these DTOs are opaque local model labels for compatibility
with the report types. Do not send them to the legacy approved-vector GET routes.
Use the supplied data or refreshModel. After a successful save, replace all view
caches together. On a conflict or failure, retain unsaved user edits.

The risk service reuses #63's per-route ratings and worst-risk-per-category
calculation. Rejecting a route does not remove it from the risk calculation.
Unreviewed/rejected evidence and missing/conflicting ratings remain visible.
Neither mitigation status nor recorded historical aggregate risk substitutes for
the existing calculation.

## Errors

```json
{"error":{"code":"revision_conflict","message":"Reload before retrying.","current_revision":"r2"}}
```

| Code | HTTP status | Frontend behavior |
| --- | --- | --- |
| validation_error | 422 | Show optional fields[].field/message; preserve edits |
| permission_denied | 403 | Disable restricted action; do not retry as another claimed reviewer |
| not_found | 404 | Model/revision unavailable; preserve edits |
| revision_conflict | 409 | Offer reload/reconciliation; never silently discard edits |
| save_failure | 503 | Preserve edits and allow retry |
| workspace_failure | 503 | Workspace/session adapter unavailable; do not enable saves |
| internal_error | 500 | Preserve edits and report an unexpected failure |

The default engine returns workspace_failure for these operations until the host
explicitly configures them. This does not imply the ordinary read-only app failed.
