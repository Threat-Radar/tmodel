# Local human review API — #289

This implements C7's review backend using the existing schema and risk engine. Physical storage
belongs to #288 and the interface belongs to #290. Merge #288, then #289, then
#290, with #269's exact relationship and risk-scope fixes available first.

## Integration status

The review service, HTTP operations, project-version adapter and native host
commands are implemented. The adapter follows the #288 contract fixture published
with #295; the actual #288 storage implementation is not in a published branch
at this revision. Adapter tests use storage doubles, not real project files.
**C7 is not complete until real save/reopen and packaged-app integration pass.**

The launcher deliberately preserves read-only startup until #288 supplies its
`serve --projects` implementation. The remaining integration steps are:

1. Wire #288's project instance into `HostReviewAPI`, using the token and reviewer
   identity passed by the native host as `TMODEL_HOST_TOKEN` and
   `TMODEL_REVIEWER_ID`. Supply a trusted `list_models` callback returning #288's
   opened-model registry, in the same shape as `/workspace/models`. That registry
   grants access only to opaque `project:<32 lowercase hex>` and `file:<32 lowercase
   hex>` IDs registered by native picker operations.
2. Inject this API into #288's server handler alongside its workspace routes.
   `make_server(review_api=...)` and `serve(review_api=...)` accept the configured
   API. Keep #288's host-only path routes and token/Origin checks in place. There
   is no endpoint to grant a reviewer identity or sponsor authority.
3. Enable the launcher's `--projects` argument when the storage implementation and
   CLI flag are present. Do not enable an unknown flag on the read-only engine.
4. Verify full ExampleModel schema validation, real YAML save/reopen, stale saves,
   failed saves and immutable history. Exercise #290's actual UI with the packaged
   desktop app before declaring the workflow complete.

### Native session and reviewer identity

`project_host_session` and `project_host_step` implement #290's native command
names. Only the application's own main window can invoke them. Native dialogs
choose file/folder paths; webview requests cannot supply paths or reviewer IDs.
The host sends those path grants directly to #288's host-only routes, with no
Origin header. Cancelling a dialog returns null. Imported YAML is saved only to a
new, user-selected file, preserving existing sources.

The host creates a fresh cryptographically random session token per engine launch
and a persistent random installation identifier in a private `reviewer-id` file
under the app's local-data directory. The reviewer ID combines that installation
identifier with the process's real OS user ID. It identifies the local OS account;
it does not certify a person's legal identity or grant a sponsor role. A trusted
host session grants read/review/rate on opened models only. Missing private
identity storage disables writes while preserving ordinary read-only browsing.

Before disclosing a bearer token or a selected path to the fixed engine port,
Rust obtains a fresh 32-byte challenge's HMAC-SHA256 proof from
`GET /host/health?challenge=<64 lowercase hex>`. The domain is
`tmodel-host-session-v1:` followed by the ASCII challenge. The engine signs with
the session token; Rust verifies the MAC. The proof route rejects every Origin
header, requires no bearer, and returns no token. An unrelated health string or a
replayed proof does not establish the session. An external engine is read-only
from this desktop session. Tokens stay out of URLs, YAML, logs and command-line
arguments; responses use `Cache-Control: no-store`.

A read-only imported model can refresh without an existing reviewer Party. On the
first permitted save, the host's verified local reviewer Party is added atomically
to the editable copy with its review/rating changes. Existing Parties are never
reclassified, original AI provenance remains intact, and canonical proposal
acceptance remains restricted. This is the implemented local identity policy for
team review, not an accepted architecture decision.

## Operations

All operations use JSON POST requests and `Authorization: Bearer <session>`.
The existing GET API and approved-vector restrictions are unchanged. Requests
with a foreign Host or Origin are rejected, including when a token is supplied.
Tauri production/dev origins support preflight; a local native client can omit
Origin but still needs a token. Requests are bounded to 256 KiB and 100 changes
of each type, with unique JSON keys and no nonfinite numbers. A modest oversized
body is drained within the existing timeout before returning a validation error,
so closing unread input does not reset the connection before the UI gets it.

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

Saves may include a nonblank `description` of at most 4096 characters. The project
adapter stores it (or a default description) and a calculated-risk summary in the
same `save_version` operation as the YAML. The summary records the matrix, number
of assessments, incomplete count and highest **known calculated** score per
S/F/O/P category (null when none is known). A known maximum alongside incomplete
assessments must not be presented as a complete overall assessment.

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

`ProjectReviewWorkspace` adapts these operations to #288's published contract:
`read`, `history` and `validate` delegate to its project instance; `commit_version`
calls `save_version(model_id, expected_revision, document, description=..., summary=...)`.
That method must return the new revision string, save metadata atomically with
the document and enforce the guarantees above. Its actual implementation still
needs integration verification; the fixture alone does not prove persistence.

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
