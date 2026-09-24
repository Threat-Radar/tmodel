---
schema: "archdoc/v1"
id: DECISIONS-0001
title: "Open decision register — everything waiting on a human"
short_title: "Decisions"
description: "The DEC-* register: status, what blocks on each, and the evidence that will settle it. Mirrors ARCH-0001 §8. An ADR accepts a decision; this file only tracks it."
type: process
category: process
status: active
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
needs_review: false
reviewed: true
canonical_path: project/DECISIONS-0001.md
defers_to: ARCH-0001
---

# Open decision register

Mirrors `ARCH-0001` §8. **A `DEC-*` is accepted only by an `ADR-NNNN` file** — not
here, not in a PR body, not in a Zoom note. This tracks status and evidence.

Status: `open` · `researching` · `proposed` (an ADR is drafted) · `accepted`.

| id | question | status | blocks | evidence |
|---|---|---|---|---|
| **DEC-001** | The core object model — first-class types and typed relations | open | I2, the schema, the UI | RPT-0001 §schemas/object-models |
| **DEC-002** | Encoding/serialization; which existing formats we import (and export) | open | schema, vectors, MAP-* | RPT-0001 §schemas |
| **DEC-003** | Risk-metric scheme: CVSS / custom / ISO 21434 / Common Criteria / composite | open | I4 risk, R-011…R-013 | RPT-0001 §risk metrics |
| **DEC-004** | Knowledge-graph substrate and the annotation/review model | open | I3, R-018…R-021 | RPT-0001 §schemas, library design |
| **DEC-005** | MVP scope — which expansion dimension(s) beyond container SCA | **open — Week-0 gate** | everything downstream | RPT-0001, T-028 |
| **DEC-006** | UI stack and interaction model for the graphical threat model | open | I3 | RPT-0001 §UI comparison |
| **DEC-007** | Relationship to `tradar`: reuse / wrap / greenfield | **open — Week-0 gate** | I2, I3 | tradar review |
| **DEC-008** | CWE/NVD integration: live vs cached mirror; automation | open | I2, I4, R-010 | RPT-0001 §CWE/NVD |
| **DEC-009** | Generic-threat → product / product-family mapping; mitigation lifecycle | open | I4, R-020, R-021 | RPT-0001, ARCH-0001 §7 |

## Priority

**DEC-005 and DEC-007 are the Week-0 gate.** They set MVP scope and how much of
tradar we reuse — everything else sizes off them. The rest are informed by
RPT-0001 and taken across I2–I4 as the evidence lands.
