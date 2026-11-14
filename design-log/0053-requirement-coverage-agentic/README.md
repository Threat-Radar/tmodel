---
id: DL-0053
title: Requirement coverage query and agentic source fragments
status: draft
date: 2026-11-14
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
  `e4068272cec52a92b4414ea2a88a23b7125ce79d`. The existing application pin remains
  `a28a01375814accc5fe10cb2f5e7083c7d0401a5`; publication refresh belongs to #200.
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

# Human accepted / rejected

**Pending. No human acceptance or rejection recorded by this change.**
The owner must review at least ten proposed links per source (40 total), recording
each actual decision and its justification as a Review. The prepared sample is
undecided. The issue remains open until that acceptance criterion is fulfilled.

# Limits

These are source requirements and hypotheses, not validated assessments of a Kia,
a Raspberry Pi or another product. The query uses recorded mitigation status and
does not verify effectiveness. Full library FX-1 extraction and cross-record
mapping are outside this pass; this change does not edit library records, close
source quality gaps, select architecture decisions or certify compliance.
