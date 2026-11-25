---
id: DL-0053
title: Requirement coverage query and agentic source fragments
status: draft
date: 2026-11-14
updated: 2026-11-22
human_owner: paria03
reviewed: false
---

# Question

For #170 and parent #168, how can the engine report recorded requirement coverage
without counting AI-proposed links, and how can the four owned agentic sources be
prepared for human review under ADR-0012?

# Prompt and constraints

Implement `tmodel coverage FILE --product ID [--json]` and its read-only local API
using ADR-0009 and ADR-0012. Include declared product, instance, component and
family scope; report mitigation-based satisfaction and threats no scoped
requirement addresses. Separate proposals and preserve the human-review boundary.
Validate MVP-02's five scoped Requirements. Reuse existing source extraction
fields rather than extracting NIST again. Convert MAESTRO mitigations, the
GenAI-specific SP 800-218A additions, OWASP v1.1 playbook mitigations and uppercase
MCP MUST/SHOULD clauses into core fragments. Keep every proposed link an
Assertion, with source locators, coverage accounting and no human Reviews. Do not
invent source designators or catalog mappings. Push and open a PR, then check CI.

# Output and decisions

- `engine/engine/coverage.py`, CLI/API adapters, tests and `engine/COVERAGE.md`.
  No architecture, schema, graph/proposal permission or storage changes.
- Four fragments, 244 Requirements and 175 proposed Assertions. Source accounting
  and an undecided human sample accompany them. Every assertion remains proposed;
  no Review, product assessment or family applicability is manufactured.
- New library records are read at merged library snapshot
  `e4068272cec52a92b4414ea2a88a23b7125ce79d`. The original application pin was
  `a28a01375814accc5fe10cb2f5e7083c7d0401a5`. After #200 merged, this branch
  inherited `e406827` and its publication refresh from `main`.
- Preserve the sparse declared scope in MVP-02: the gateway requirement is outside
  scope, matching #170's expected five. Derivation does not grant applicability.
- Require actual human review evidence before an accepted Assertion contributes;
  keep contradictory reviews instead of letting document order select one.
- Interpret source considerations as recommendations to **consider** an option,
  never mandates to adopt it. Six explicitly new NIST tasks are included along
  with 75 R/C additions; informative notes and baseline/overview material are
  accounted for separately.
- MAESTRO has one umbrella layer-control instruction, not seven concrete control
  lists; its seven layer instances are marked `authored`. The source's concrete
  cross-layer, AI-specific and architecture-pattern advice remains paraphrased.
- OWASP's duplicated memory-monitoring bullet is retained under both ordinal
  locators. Parent controls retain relevant nested technical constraints, without
  treating examples as separate obligations. Its adapted fragment carries the
  source's CC-BY-SA-4.0 attribution and license.
- The dated MCP web endpoint is mutable: the capture hash differs from the library
  record's historical HTML hash. Document both; do not claim byte identity or
  silently substitute the living draft. The release-tag MDX was cross-checked but
  is narrower than the dated page/record summary; it is not the extraction input.

# Validation

Run the engine suite, lint/format, CLI/API parity and approved-directory checks;
validate all four fragments with LinkML, check-edges.py and the extraction checker;
run the converter suite and schema regeneration check. Run the repository's app,
Rust, packaging, archdoc, publishing and pinned-library checks before the PR.
Actual results and exact-head CI status are recorded in the PR.

# Main integration (2026-11-20)

After #229 merged, @paria03 requested bringing this PR up to date with `main`,
pushing it and checking fresh CI. This integration uses `main` at `df5fb01`.
The CLI parser conflict is resolved by retaining both the coverage and risk
commands. The new CWE API/CLI and the packaged-engine risk/coverage checks are
also retained. No collector rules, source fragments, proposed links or human
review records change. The PR records validation on the integrated head.

Local integration validation on Python 3.13: 540 engine tests passed, six skipped
(five opt-in packaging checks and one external full-catalog CWE test). All five
packaged-engine checks then passed against the rebuilt sidecar. The four source
fragments passed LinkML, all ten extraction files passed the rule/reference checks,
and nine converter tests passed. Generated schemas and browser preview are current.
Frontend typecheck/build and 373 tests, Rust fmt/clippy and four tests, 14 publishing
tests, archdoc and the identity/link guards passed. The unchanged pinned library
has 550 records, zero errors and 122 existing warnings. The 40 human sample
reviews are still pending.

# Shared review rule (2026-11-21)

The #242 review from @Clovier and @Maimcghee identified differing human-acceptance
rules between TARA and coverage. This local companion fix uses the identical
`engine.review.assertion_review_state` helper introduced by #242. Accepted
Assertions need at least one person Review, with all person Reviews accepting
and giving nonblank text justifications. Contrary human evidence still blocks
acceptance; non-person Reviews neither grant nor veto it. Every source Review
remains intact. The helper retains TARA's normalization of open verdict strings.
Tests check agent verdicts added to a human acceptance and normalized accepted
strings, alongside the existing missing-human, blank-justification and contrary-
human cases. This is a query fix, not a human review or a decision on the pending
version-governance proposals. No source fragment or sample decision changes.

Local validation on Python 3.13: **549 engine tests passed, six skipped** (the
five opt-in packaging checks and external full-catalog CWE test); a rebuilt
sidecar then passed all **five packaged-engine tests**, including coverage after
relocation. Frontend typecheck/build and 373 tests, Rust fmt/clippy and four
tests, 14 publishing tests, archdoc, current browser preview and the publishing
guards passed. Cross-consumer checks with #242 agreed on 12 evidence scenarios
and both review orders, without changing the input. The helper and its unit
tests are byte-identical on both branches. Fresh CI remains to be checked after
pushing this local commit. The 40 human sample reviews remain pending.

# Source review fixes (2026-11-21)

@Maimcghee found display names cut inside words and invalid URI fragments in
the new source files. @Clovier also identified the outdated library accounting
and the missing actual human sample decisions. This update addresses the
mechanical issues and prepares the evidence for those decisions.

- Merge `main` at `18512e3`, including #200's `e406827` library pin and existing
  publication refresh. All four source records now resolve in the pinned
  submodule. The old `a28a013` lacked two records (MCP and OWASP), not three.
- Give all 244 Requirements whole-word display titles, with an ellipsis for
  abbreviation. Keep hyphenated terms intact. Replace 163 non-native reference
  fragments with the local slug from each existing Requirement ID; leave NIST's
  native designators unchanged. Source heading paths stay in `source_locator`.
  These local slugs are not claimed website anchors or source-issued clauses.
- Add URI-fragment checks and converter percent-encoding so schema validation
  cannot silently allow spaces, angle brackets or malformed percent escapes in
  future references. Regression tests cover both invalid fragments and encoded
  locators while retaining readable locator text and stable object IDs.
- Expand the same 40 sample targets into `agentic-review-packet.md`, with the
  proposed text, target, locator, rationale and blank human decision/reason.
  Flag MAESTRO's partial layer mappings, missing Identity Attack link, and
  explicit-versus-interpreted associations for the human scope check. No
  proposal is deleted to avoid that review. Source-version and access limits
  remain visible; the cached OWASP download attempts are HTML, not evidence
  that the historical PDF digest was checked.

A semantic comparison with the prior files confirms that all 244 full texts,
IDs, source locators, kinds and normativity values, all 175 proposed Assertions
and their targets/confidence, and every Party/Review collection are unchanged.
At the source-formatting step, the packet had the exact original 40 Assertion
IDs, ten per source, with all decisions pending; subsequent human decisions are
recorded below. No human approval or rejection is inferred from these
formatting, validation or documentation fixes.

Local validation: **550 engine tests passed, five opt-in packaging checks
skipped**, with the full pinned 969-weakness CWE release enabled. Rebuilding
the sidecar and running those packaging checks gave **five passes**. All ten
extraction files passed LinkML, reference-integrity and extraction-rule checks;
the converter/checker suite passed **12 tests**, and generated schemas are
current. Frontend typecheck/build and 373 tests, Rust fmt/clippy and four tests,
14 publishing tests, archdoc (28 documents, zero errors), preview freshness,
published links and identity guards passed. The inherited library pin has
685 records, zero errors and 99 existing warnings. Review-packet relative links
and all four library references resolve. Fresh remote CI must be checked after
pushing this local update.

# Human accepted / rejected

**39 accepted; 1 rejected; 0 pending.** @paria03 completed all four source samples on
2026-11-22. M01–M03 were accepted as general layer relationships; M04–M07 as
interpreted links with the stated response, detection and accountability limits;
M08–M10 follow the source's explicit control/threat pairings. Each actual decision
has a person Review with its agreed justification. No acceptance establishes
implementation, effectiveness or exhaustive threat coverage. Across the four
fragments, 39 Assertions are accepted and the other 136 remain proposed. One
of those proposed Assertions has a rejecting human Review (O09).
The N01–N10 acceptances retain the presented model-development scope and
control-specific limits. They accept proposed relationships, not a NIST-approved
crosswalk or evidence of implemented controls. The other two NIST Assertions
remain proposed. The nine OWASP acceptances retain the presented partial,
detection, recovery and investigation limits. O09 is rejected because quotas
limit flooding without establishing message truth or integrity. Its rejecting
Review is preserved, its Assertion stays proposed, and no replacement link is
authored. The ten MCP acceptances retain their source-section scope and the
presented consent, session, authorization and damage-limitation caveats. The
source capture/version limits remain unchanged. All 40 sample decisions are
recorded; unsampled links remain proposed. PR review and CI after publication
remain separate steps; this local completion does not close the issue.

Final local review validation: all four fragments pass LinkML, reference integrity
(512 objects, 430 references) and extraction rules (244 Requirements). The 40
sample targets each have exactly one matching person Review and agreed rationale;
39 are accepted and O09 is rejected. Source texts, IDs, locators, targets and
confidence are unchanged from the published source-fix head. The review and
coverage suites pass **30 tests**; archdoc passes with zero errors. These checks
do not stand in for CI after pushing the human-review commits.

# Current-main integration (2026-11-22)

@paria03 requested checking #243 and pushing any needed update after #242's
integration. Merge `main` at `8351701`, including the CWE relationship/local
weakness changes, requirements UI and nine-model browser preview. Git merges the
coverage API, CLI and core adapters automatically; no conflicted hunk needs a
manual resolution. This does not pull in the still-open #242 branch.

Preserve the four reviewed source fragments byte for byte, including all 40
human decisions and their limits. Keep the shared review helper identical to
#242. Verify the pre-merge coverage output, validate all extraction files, and
check the requirements UI's coverage parser against actual engine responses.
Local integration validation on Python 3.13:

- **646 engine tests passed, five opt-in packaging checks skipped**, with the
  full pinned CWE release enabled. Rebuilt sidecar: **all five isolated packaging
  tests passed**. Engine lint and formatting passed.
- Frontend typecheck/build and **456 tests passed**; Rust fmt/clippy and
  **four tests passed**. Converter/checker **12 tests** and **23 publishing tests**
  passed (35 tests and 13 subtests in the combined run).
- All **13 extraction files** pass LinkML, extraction rules and reference
  integrity (1,663 objects, 1,518 references). Generated schemas are current.
- The requirements UI parses actual engine responses and uses its engine branch
  without fallback for **ten product cases across nine models**. Its conservative
  graph fallback agrees with those engine answers.
- Coverage JSON remains byte-identical to the pre-merge baseline. All four
  source fragments and their 40 person Reviews remain byte-identical, with 39
  acceptances and O09 rejected. The shared helper matches #242's published head.
- Archdoc has 28 documents and zero errors. Published identity/link checks pass;
  the browser preview is current with nine models and 685 library records.
  The unchanged library has zero errors and 99 existing warnings.

# Review follow-up and merged collector integration (2026-11-23)

@paria03 requested verifying @kriishnaa-18's review and updating this PR after
merging #242. The review targeted `f5528dd`; subsequent source-formatting and
human-review commits already address its three findings:

- All 244 Requirement titles end at word boundaries when shortened. Every
  `source_ref` has a valid fragment; detailed `source_locator` values remain.
- Each of the four sources has ten recorded person Reviews with justifications:
  39 acceptances and the O09 rejection. The rejected Assertion remains proposed.
- The required source records resolve through the unchanged `e406827` library
  pin inherited from #200. No human decision is added or inferred in this update.

Merge `main` at `b14525b`, which now includes #242's collector, the CAPEC loader
and the router example. The CLI, API and core integrations merge automatically;
the shared review helper remains identical to main. All four source fragments,
including the 40 Reviews, are byte-identical to the prior PR head. The TCU
coverage result is still five Requirements: two satisfied and three unsatisfied.
The TARA intermediate retains SHA-256
`4238a573a546db95ea48d4adf584d2746fd40debdfc33dbfe105810f17213712`.

Local verification: 782 engine tests passed, six optional tests skipped; engine
lint and formatting passed. All 13 extraction files pass extraction rules and
reference integrity (1,663 objects, 1,518 references); all four lane fragments
pass LinkML. Converter/checker tests: 12 passed, with 13 subtests. Publishing:
14 tests passed, preview freshness passes for ten models and 685 library records,
and identity/link guards and archdoc pass. Remote CI must be verified on the
final pushed head. The earlier change request remains for its reviewer to
reassess; this update does not dismiss it.

Fresh remote CI and review status must be checked after pushing the integration.
No source decision or product assessment is inferred from this merge.


## Integration with current main (2026-11-25)

Merged main through `6b8b022`, including the requirement catalog, packaged
library, governance validator, publish guard and approved-current TARA check.
The sole conflict was two independent additions at the end of `core.py`:
retain both `requirement_coverage` and `evaluate_tara_gate`. The four source
fragments and all recorded sample decisions remain unchanged from `fed259b`.

Verification: 812 engine tests passed (eight opt-in tests skipped), 470 frontend
tests passed with typechecking, and 121 publishing tests passed with the pinned
LinkML environment. Engine lint/format and preview freshness pass (ten models,
685 library records). Remote CI must pass on the pushed merge commit. The
existing request for reviewer reassessment remains open.

# Limits

These are source requirements and hypotheses, not validated assessments of a Kia,
a Raspberry Pi or another product. The query uses recorded mitigation status and
does not verify effectiveness. Full library FX-1 extraction and cross-record
mapping are outside this pass; this change does not edit library records, close
source quality gaps, select architecture decisions or certify compliance.
