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
and privacy. The engine reads each relevant AttackPath's recorded
`attack_feasibility`, looks up its category risks, and folds by the highest
feasibility across the threat's paths. For this monotone matrix that gives the
maximum path risk in each category.

The result includes each path's steps/alternatives, recorded rating, category
risks, assertions and reviews. Calculation does not accept a proposal, assign
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

## Missing data and the open OR-route decision

An omitted impact stays `null`, not negligible. If any path lacks a usable
rating, the aggregate feasibility and derived risk stay `null`; showing only
the rated subset could understate the worst risk. Known category risks can
still appear when other impact categories are missing. Missing damage,
mitigation status, or a mismatch between the assessment's path/damage scope
and its threat is listed under `problems`. Scope mismatches suppress the
aggregate risk rather than silently dropping or mixing paths.

An authored path can enumerate several OR routes, including prerequisites
shared with other paths. Today its one `attack_feasibility` does not identify
which route it rates. Issue #63 explicitly leaves this policy for the sponsor.
These cases therefore report `alternative_route_ratings_required`; the one
authored rating is shown but is not copied to every route. Splitting authored
path records alone may not disambiguate a shared OR join, since enumeration
follows the whole step graph. A route-to-rating binding must be settled before
the remaining OR cases can be calculated.

The recommended next policy is separate human ratings for routes with different
prerequisites/difficulty, individual results plus the maximum risk, and shared
ratings only when their applicability to every alternative is explicit. This
recommendation does not accept a schema or architecture change. #63 remains
open pending that decision and its implementation.

The API returns structured partial data with HTTP 200 and `complete: false`.
Here `complete` refers only to calculation inputs, never human approval.
Malformed data or requests return HTTP 400. The CLI emits the same JSON but
exits 1 for incomplete assessments; an assessment with all required inputs
exits 0. Omitting `--goal` includes threats without a RiskScore as incomplete
rows, so absent assessments do not disappear.

## Verification

Tests cover all 16 table cells, worst-path and 1–5 invariants, mitigation
independence, AND/shared prerequisites, unresolved OR alternatives, scope
mismatches, missing inputs, review preservation and API/CLI parity. The
headlamp regression is a projection of RPT-0007's rating inputs and expected
results: spoofing's High/Medium/Low paths with severe safety yield 5; the two
Low DoS paths with moderate operational impact yield 2. It is not a full
reconstruction of the conflicting step lists in Annex H (RPT-0007 §4.3–4.4).
