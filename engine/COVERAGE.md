# Recorded requirement coverage (#170)

```sh
tmodel coverage mvp-02-automotive-ecu.yaml --product product:telematics-control-unit --json --in-process
# With the local engine running, omit --in-process; --url selects its loopback URL.
# GET /coverage?file=mvp-02-automotive-ecu.yaml&product=product:telematics-control-unit
```

CLI, API and `core.requirement_coverage` return the same read-only JSON. Plain CLI
output summarizes requirement status and counts; JSON includes individual threat
ids and proposed links. Missing/blank/unknown parameters, unknown Product ids,
invalid reference types and paths outside the approved example directory fail.
Absolute paths and symlinks must resolve inside the source or bundled example
directory, as for `/graph`. Errors are HTTP 400 / CLI exit 1; missing CLI options
are usage errors (exit 2). Gaps are valid results (exit 0). This does not add an
upload endpoint or write to a model.

`engine.coverage.collect(document, product_id)` takes a storage-neutral mapping;
it does not need attack steps, a library checkout or a database. The file adapter
uses the existing full-document YAML loader rather than modifying attack-path
loading or the graph/proposal permission allowlist.

## Rules

1. Start with the selected Product and ProductInstances whose `of_product` points
   to it. Follow Product/Component `composed_of`, Component `uses_component` and
   ProductInstance `build_composed_of`, stopping safely at cycles. Dependencies
   do not imply component membership. Family classification is exact and case
   sensitive; there is no family inheritance or fuzzy matching.
2. Include Requirements with `applies_to` any scoped object or with an
   `applies_to_family` string matching that Product's `classifications`. Generic
   `derived_from`, `refines`, `stated_as`, `maps_to` and `addresses` do not confer
   product scope or transmit satisfaction.
3. `satisfied_by` any complete Mitigation means `satisfied`; otherwise any
   `in_progress` Mitigation means `in_progress`; otherwise `unsatisfied`.
   Missing, planned or unknown mitigation statuses cannot discharge a requirement.
   This is the existential rule requested in #170, not a judgment that all
   controls or a full standard have been implemented. Results expose mitigation
   ids and their recorded statuses so reviewers can inspect the basis.
4. `unaddressed_threats` contains every ThreatInstance in the supplied model
   without a direct `addresses` edge from an in-scope Requirement. Weakness and
   AttackPattern links do not imply a ThreatInstance link. The result includes
   unreviewed/rejected hypotheses and threats from any other product in the same
   file: it is a model-level gap list against the selected product's requirements,
   not an inferred inventory of verified threats to that product.
5. Authored slot values form the baseline. Assertions for the seven typed link
   predicates listed in `coverage.LINKS` contribute only when their status is
   `accepted`, at least one recorded person Review targets that Assertion, and
   every person Review accepts it with a nonblank text justification. Missing or
   contrary human evidence excludes the Assertion. Non-person reviews neither
   grant nor veto human acceptance; they remain recorded evidence. This uses
   `engine.review.assertion_review_state`, the same helper as the TARA collector
   in #242. A human review must accompany AI acceptance under ADR-0012;
   an accepted flag alone is
   insufficient. Reviews are not last-wins. Slots already authored in the model
   remain baseline; this query does not revoke them or reconcile disputed models.
6. Proposed Assertions never contribute to baseline counts. `proposed_assertions`
   lists those whose acceptance would change the answer, either alone (`effect:
   individual`) or together with other proposed scope/coverage links (`effect:
   with_other_proposals`). Each includes `if_accepted`, its individual hypothetical
   answer, and all targeting `review_ids`. `if_all_proposed_accepted` is the joint
   hypothetical, explicitly separate from baseline. These simulations are not
   acceptances; even a rejected proposal remains hypothetical evidence. Other
   ineffective or unrelated proposals are omitted. `excluded_assertions` names
   relevant non-proposed Assertions that lack the required human acceptance.

Rows and ids are sorted, and querying does not mutate the input. The output
contains no computed timestamp or local file path. `file` is the input basename.
Unknown optional model collections are not projected by this core adapter;
accepted Requirement relations are checked separately without widening the
existing AI proposal allowlist. This is recorded coverage, **not verified
compliance**, proof of mitigation effectiveness or automated human review.

## Worked result

MVP-02 has five scoped Requirements: three unsatisfied and two satisfied by
`mitigation:authenticate-diag-service`. Its gateway-filter requirement has no
`applies_to` or matching family and is therefore out of scope; its environment is
not a TCU component. The infotainment-pivot hypothesis remains an unaddressed
ThreatInstance. `assertion:ai-req-addresses-pivot` appears separately; accepting it
hypothetically removes that gap without changing the actual result.

The four #170 research fragments are unreviewed source material. They deliberately
contain neither Product assessments nor inferred family classifications. A human
must scope applicable provisions and decide proposed links before they can be used
as accepted product evidence. See the extraction accounting and review sample in
`research/0017-requirements-extraction/agentic-coverage.md`.
