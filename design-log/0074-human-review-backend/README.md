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
was added. The concrete #288 adapter and identity/session launcher integration
remain pending. The contract is proposed for team integration, not an accepted ADR.

## Human acceptance and rejection

The user authorized starting #289. No human review of this implementation, API
contract, workspace interface or identity integration has been recorded yet.
The example review verdicts are synthetic test inputs, not human sign-offs.
No push or PR was authorized for this issue.

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
integration. Hosted CI has not run for this local branch.
