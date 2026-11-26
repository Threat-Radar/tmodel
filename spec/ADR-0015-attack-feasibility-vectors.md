---
schema: "archdoc/v1"
id: ADR-0015
title: "Attack feasibility: computed Annex G vectors with reviewed-state markers (amends ADR-0006)"
short_title: "Feasibility vectors"
description: "Sponsor decision (2026-11-25): path feasibility is computed from an ISO/SAE 21434 Annex G vector (attack potential by default, CVSS exploitability or attack vector by choice per threat scenario), shown with a computed-or-reviewed state, with mandatory-rationale overrides and a not-exploitable extension that gives no risk value. CVSS import accepts only the short CV:3.1 form; a full CVSS:3.1 vector is rejected. Tried first on standalone pages (DL-0069); existing models, schema, engine and app stay unchanged until the later migration is scoped."
type: decision
category: security
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-11-25"
updated: "2026-11-25"
decision_makers:
  - role: sponsor
    id: nymble
reviewers:
  - role: sponsor
    id: nymble
    kind: human
  - role: drafting-agent
    id: grok-bot
    kind: ai_agent
needs_review: false
reviewed: true
canonical_path: spec/ADR-0015-attack-feasibility-vectors.md
amends: ADR-0006
defers_to: ARCH-0001
---

# ADR-0015: Attack feasibility as computed Annex G vectors

**Status: accepted (2026-11-25) on merge.** Decided by @nymble. It amends **ADR-0006**: path
feasibility is computed from an Annex G vector rather than only a human-entered Table 1 label.
Design record: DL-0069. Existing models, schema, engine and app code stay unchanged until the
migration below is scoped.

## Review

| date | who | kind | verdict |
|---|---|---|---|
| 2026-11-25 | drafting agent | ai_agent | drafted as Proposed (DL-0069) |
| 2026-11-25 | @nymble (sponsor) | human | **accepted**. Paraphrase of the decision: accept the ADR; CVSS import accepts only the short `CV:3.1` form, and a full `CVSS:3.1` vector is rejected. |

## Context

ADR-0006 rates path feasibility with a human-entered ISO/SAE 21434 Table 1 label and keeps Common
Criteria numbers display-only. Issue #14 asks for an attack-potential calculator. Annex G of
ISO/SAE 21434 offers three approaches (RC-15-11 to RC-15-14): attack potential (G.2, after
ISO/IEC 18045), CVSS exploitability (G.3) and attack vector (G.4). Each ends on the four Table 1
ratings.

## Decision

1. A path's feasibility is computed from a vector in one of the three Annex G methods, chosen per
   threat scenario by `feasibility_method`; attack potential is the default and methods may mix.
2. The computed rating is the source of truth. Every displayed rating carries a state: computed,
   reviewed as is, changed by human, overridden, review stale, or label only.
3. An override needs level, rationale, author and date, and keeps the computed result at decision
   time. A stale override stays in force, flagged.
4. Extension beyond ISO/SAE 21434: window of opportunity `NEX` (not exploitable), aligned with the
   ISO/IEC 18045 "none" window. It is not summed, has no Table 1 level and gives no risk value; it
   requires a recorded basis and shows the ISO-strict equivalent.
5. The AI hook may propose a vector; only a human accepts, changes, overrides or sets NEX.
6. CVSS import accepts only the short form `CV:3.1/AV:/AC:/PR:/UI:`. A full `CVSS:3.1/...` vector
   and CVSS 4.0 are rejected; the four exploitability metrics are not extracted from a longer string.

## Later change, to be scoped before any model is touched

| Area | Would change |
|---|---|
| Schema | `ThreatInstance.feasibility_method`; per-method vector classes, review, override, NEX basis and append-only history on `AttackPath`. Additive and optional. |
| Models | No automatic conversion. Existing labels stay as "label only" until a person enters a vector. |
| Engine | A feasibility package beside `risk.py`; `risk_routes` reads the effective rating and state; NEX paths are excluded from Table H.8. |
| CLI and API | `tmodel risk` and GET /risk report method, vector, value, computed and effective rating, state and override. |
| App and TARA pages | Compact rows, state markers, exception history and the override dialog, as in the prototype. |

## Consequences

- ADR-0006's "Common Criteria display-only" clause is amended; the composite vector and the
  Table H.8 profile stay.
- Values follow the library record of ISO/SAE 21434 Annex G; the CVSS weights are FIRST CVSS v3.1's.
