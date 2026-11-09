# Risk calculation (#63, ADR-0006)

The engine can calculate the risk vector from existing model records through
`core.risk_assessments`, `GET /risk`, and `tmodel risk`. This is the first slice
of #63 Part 2. It does not change the canonical schema or rate an attack for a
human. The desktop report continues to display authored risk data; it is not
wired to this new endpoint yet.

## Try the calculation

From the repository root, using the existing engine environment:

```sh
PYTHONPATH=engine engine/.venv/bin/python -m engine risk mvp-02-automotive-ecu.yaml \
  --goal threat-instance:remote-diag-injection \
  --matrix annex-h-table-h8 --in-process --json
```

With `tmodel serve` running, replace `--in-process` with `--url
http://127.0.0.1:47811`. The equivalent API request is:

```text
GET /risk?file=mvp-02-automotive-ecu.yaml&goal=threat-instance:remote-diag-injection&matrix=annex-h-table-h8
```

The `file` argument accepts an example filename or a path confined below the
approved model directory, including in the bundled engine. The CLI resolves
paths containing a directory relative to the caller. An outside path, including
a symlink pointing outside the directory, is refused.

Python import note: on some macOS setups, an iCloud-synced Desktop/Documents
folder marks virtual-environment setup files hidden, so an editable install's
`.pth` file is skipped. The command above explicitly supplies the source import
directory. It does not alter the environment or require shell activation.

## What is calculated

Each assessment retains the RiskScore id, threat, damage scenario and recorded
stakeholder. The four categories stay separate: safety, financial, operational
and privacy. The engine binds each computed route to its separately authored
AttackPath and recorded `attack_feasibility`, looks up its category risks, and
folds by the highest feasibility across the threat's routes. For this monotone
matrix that gives the maximum route risk in each category.

The `routes` result includes each computed route's steps, rating, category risks,
and `rating_paths` naming the authored records that supply its rating. `paths`
retains those records' ratings, assertions and reviews; `used_for_ratings` says
whether a record supplied any route's rating. Both JSON and text CLI output
show individual route results alongside the aggregate. Calculation does not accept a proposal, assign
a reviewer, or exclude an unreviewed/rejected path from the fold. The review
records remain available for triage. Every matching review is retained; a
later record does not erase an earlier verdict.

`mitigation_status` is a peer field. Changing it never changes the numeric
risk. The original authored `RiskScore.feasibility` and free-text `risk` remain
under `recorded`; they are not trusted as computed results. No model file is
rewritten. The recorded inputs' human provenance must still be checked by a
reviewer; merely reading an input is not proof that a human rated it.

The current mvp-02 diagnostic example has High feasibility and S/F/O/P impacts
Severe/Major/Severe/Negligible. This profile derives **5/4/5/1**, with mitigation
status still `in_progress`.

## Explicit matrix profile

The caller must select `annex-h-table-h8`; there is no implicit matrix choice.
It implements the informative example recorded in
[RPT-0007 §4.2](../research/0007-iso21434-tara/report.md). It is not a claim that
the standard mandates that matrix. RPT-0007 §4.3 notes four input pairs where
the example formula and matrix disagree; this implementation uses the table
and never substitutes the formula or rounds its fractional results.

Common Criteria and CVSS do not drive this calculation. Feasibility remains a
recorded path-level input; the engine does not aggregate step difficulty or
infer feasibility from graph length.

## Separate ratings for routes with different difficulty

Use one AttackPath record per separately rated route, retaining the shared
steps and global AND/OR structure. Its `steps` must name the complete computed
route, including shared prerequisites. Set its `attack_feasibility` to the
human-supplied rating; no new schema fields are needed. For example, two
illustrative ratings for branches joining at one OR step are represented as:

```yaml
attack_paths:
  - id: attack-path:physical-route
    steps: [attack-step:physical-entry, attack-step:read-data]
    realizes_threat: threat-instance:data-read
    attack_feasibility: low
  - id: attack-path:remote-route
    steps: [attack-step:remote-entry, attack-step:read-data]
    realizes_threat: threat-instance:data-read
    attack_feasibility: high
```

These records assume the model defines both entry steps as preceding the
`read-data` OR step. The Low/High values above demonstrate the format; the
engine never assigns ratings to actual example routes on a human's behalf.
The risk assessment's `attack_paths` list must include both records.

Matching uses the complete step set, not a list index or a heuristic overlap.
Legacy partial-step records remain usable only when they enumerate exactly one
route. An older broad OR record cannot supply or override an alternative's
rating. If two records for the same route disagree, the route reports
`conflicting_route_ratings`; the engine does not choose one by file order.
Identical ratings can be recorded on two different routes, but each route's
result stays visible.

Each output route has a digest id based on its threat, goal step, step ids,
gates and internal ordering edges. It is stable across model-record reordering
and helps clients identify results. It is not a KG object, a rating storage
field, or proof of human approval. Ratings continue to live on AttackPath.

For severe safety impact, a Low route and a High route produce risks **3** and
**5** with this matrix. The scenario reports **5** for safety and keeps both
route results. It performs the same calculation independently for F/O/P.

## Missing data

An omitted impact stays `null`, not negligible. If any path lacks a usable
rating, the aggregate feasibility and derived risk stay `null`; showing only
the rated subset could understate the worst risk. Known category risks can
still appear when other impact categories are missing. Missing damage,
mitigation status, or a mismatch between the assessment's path/damage scope
and its threat is listed under `problems`. Scope mismatches suppress the
aggregate risk rather than silently dropping or mixing paths.

Existing example OR paths that carry only one aggregate rating remain
incomplete until humans author their route-specific records. Enumeration still
uses the whole step graph: a missing record cannot make a possible OR route
disappear. An unrated alternative reports `route_rating_required`, while the
authored path's `problems` retains `alternative_route_ratings_required` for
callers of the first slice. Known route results remain visible, but the overall
feasibility/risk stays null until every computed route has an unambiguous rating.

This implements the requested separate-rating behavior within the existing
schema. It does not mark any DEC accepted or close #63's remaining integration
and human-review work.

The API returns structured partial data with HTTP 200 and `complete: false`.
Here `complete` refers only to calculation inputs, never human approval.
Malformed data or requests return HTTP 400. The CLI emits the same JSON but
exits 1 for incomplete assessments; an assessment with all required inputs
exits 0. Omitting `--goal` includes threats without a RiskScore as incomplete
rows, so absent assessments do not disappear.

## Verification

Tests cover all 16 table cells, worst-path and 1–5 invariants, mitigation
independence, separate OR ratings with a shared join, missing or conflicting
route ratings, record reordering, AND/shared prerequisites, scope mismatches,
missing inputs, mixed SDL/threat models, review preservation and API/CLI parity. The
headlamp regression is a projection of RPT-0007's rating inputs and expected
results: spoofing's High/Medium/Low paths with severe safety yield 5; the two
Low DoS paths with moderate operational impact yield 2. It is not a full
reconstruction of the conflicting step lists in Annex H (RPT-0007 §4.3–4.4).
