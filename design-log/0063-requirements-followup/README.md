---
schema: "archdoc/v1"
id: DL-0063
title: "Requirements follow-up: extracted catalog, relationship evidence audit, and satisfaction language"
type: process
status: draft
version: "0.1.0"
date: "2026-11-22"
updated: "2026-11-22"
record: DL-0063
bears_on: [DEC-001a, DEC-002, DEC-009, R-018]
defers_to: ARCH-0001
---

# DL-0063: Requirements follow-up (#258)

This design record addresses the three nonblocking observations in @Clovier's approving review of
PR #258. DL-0061 remains the historical record of the extraction. DL-0062 was already reserved by
the reviewer's separate work, so this follow-up uses DL-0063.

## Question asked

How can the app make the 109 extracted Requirements discoverable without treating them as part of a
selected product model, determine whether the extraction has defensible Requirement-to-Mitigation
links, and make the table and coverage summary describe missing satisfaction evidence consistently?

The constraints are ADR-0003's desktop/engine boundary, ADR-0004's file-canonical source of truth,
ADR-0007's generated interchange discipline, ADR-0012's Requirement and Assertion review rules,
and the repository's public-identity policy.

## Review observations

The approving review identified three follow-ups:

1. The 109 extracted Requirements existed only in the research fragments; the app showed only
   Requirements in the selected model.
2. The extraction established no `Requirement.satisfied_by` or `Mitigation.stated_as` links.
3. A missing satisfying mitigation appeared as “Not recorded” in the table but contributed to the
   coverage API's `unsatisfied` bucket.

These observations do not invalidate PR #258. They identify a discoverability gap, a relationship
evidence question, and a presentation-language inconsistency.

## Decision 1: keep two explicit browsing contexts

The Requirements screen has two sources:

- **Model requirements** are objects in the selected model graph. Product filtering and recorded
  coverage continue to operate only here.
- **Extracted standards catalog** is reference material built from the three Issue #171 fragments.
  It is not merged into a model, does not inherit a selected product, and has no coverage summary.

The catalog mode says that entries are not assigned to the selected model. Its table uses “Catalog
only” instead of a satisfaction state, and its inspector says that visibility establishes neither
applicability nor satisfaction. Search covers id, name, statement, source reference, source name and
locator. Source, kind and normativity filters, sorting, paging, source attribution and the existing
relationship/Review inspector remain available.

This separation preserves the accepted meaning of a model graph. A standard's existence is not
evidence that its provisions apply to a product or that the product complies with them.

## Data and publishing path

`docs/publishing/render_requirements_catalog.py` reads these authoritative files:

| Source | File | Requirements |
|---|---|---:|
| OWASP ASVS | `owasp-asvs-5.yaml` | 34 |
| EU Cyber Resilience Act | `eu-cra-2024-2847.yaml` | 23 |
| IEC 62443-4-1:2018 | `iec-62443-4-1-2018.yaml` | 52 |
| **Total** | | **109** |

The generator runs the extraction rules from `check.py`, loads YAML through the engine's safe vector
loader, and projects it through the storage-neutral graph adapter already used by `/graph`. It rejects
wrong per-source counts, duplicate Requirement ids, broken references and stale output. The committed
artifact is `apps/desktop/public/data/requirements/catalog.json`; Vite copies that same artifact into
desktop and Pages builds. `render_app.py --check` verifies freshness before comparing `docs/app/`.

The generated graph preserves Requirement text, identifiers, source references, locators, Assertion
evidence, Review verdicts and Review justifications. Project-person identities are not approved for
GitHub Pages, so the public projection replaces human ids/names by the role “Human reviewer” while
retaining the fact of human review and its reason. The catalog and browser-preview renderers use the
same public-data guard for Unix, macOS and Windows user paths and supported credential patterns. The
authoritative YAML remains unchanged.

The catalog contains 46 unique Assertions: 24 accepted, three with rejecting Reviews, and 19 proposed
without a Review. The inspector labels these states as accepted, rejected, or proposed/unreviewed;
none is silently promoted.

## Decision 2: no new mitigation relationship

### Inventory

- All three extraction fragments contain **zero Mitigation objects**.
- They contain **zero** direct or Assertion-backed `satisfied_by` and `stated_as` relationships.
- Their retained Assertions concern `addresses`, `refines`, and `derived_from` only.
- `sdl-01-tmodel-desktop.yaml` has two model-local CRA Requirements with the same source references
  as catalog entries for Annex I Part II(1) and Part II(5). They map to SSDF Requirements. The model
  records `mitigation:slsa-provenance` as satisfying SSDF PS.3.2, but it does not record that mitigation
  as satisfying either CRA Requirement. A `maps_to` edge does not transfer satisfaction.
- Other example-model mitigations are product-specific and carry no source-backed mapping to an ASVS,
  CRA, or IEC catalog Requirement.

### Result

No defensible `satisfied_by` or `stated_as` proposal can be added from the current evidence. Creating
one would require at least:

1. a reviewed mapping or canonical-identity decision between a catalog entry and a model-local
   Requirement;
2. explicit product applicability and scope;
3. evidence that a concrete Mitigation implements the obligation, including limitations; and
4. a proposed Assertion followed by an independent human Review before any direct slot is populated.

The catalog therefore makes the absence explicit and leaves all source fragments unchanged. A later
mapping issue can do this product-by-product. It must not infer compliance from a shared standard
reference, textual similarity, or a transitive `maps_to` path.

## Decision 3: preserve the API, clarify the presentation

The PR #243 coverage contract has three statuses: `satisfied`, `in_progress`, and `unsatisfied`.
Both the live implementation on its feature branch and PR #258's frontend fallback put a Requirement
with no satisfying mitigation into `unsatisfied`. Changing that response now would break compatibility.

The UI instead presents the distinction carried by each row's mitigation list:

| Recorded evidence | User-facing text | API value |
|---|---|---|
| A complete satisfying Mitigation | Satisfied | `satisfied` |
| An in-progress satisfying Mitigation | In progress | `in_progress` |
| No satisfying Mitigation | No recorded satisfaction evidence | `unsatisfied` in coverage; `not_recorded` in the table model |
| A satisfying Mitigation exists but is neither complete nor in progress | Not satisfied (recorded mitigation is not complete) | `unsatisfied` |

The coverage count is labeled “No recorded / not satisfied” because the current API intentionally
aggregates the last two cases. The detail rows explain which case applies. Neither phrase claims a
regulatory noncompliance finding.

## Validation and limits

Focused tests cover source counts, unique ids, locators, freshness, privacy, absence of unsupported
mitigation links, relationship decision states, source/kind/normativity filters, search, paging,
source-mode switching (including zero-result contextual facets and cached catalog/model changes),
catalog-only language, all four satisfaction presentations, exact YAML-to-artifact provenance,
coverage language, shared public-data rejection, and static fetching. The normal frontend, engine,
extraction, publishing and repository checks remain the release gate.

Outstanding limitations:

- The catalog is a read-only reference view. It does not author applicability or mapping Assertions.
- The coverage API retains its three-value contract and therefore aggregates the two negative-evidence
  cases in its counts.
- A future relationship-mapping issue needs product evidence and human review; this follow-up does not
  supply either.
