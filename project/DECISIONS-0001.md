---
schema: "archdoc/v1"
id: DECISIONS-0001
title: "Open decision register — everything waiting on a human"
short_title: "Decisions"
description: "The DEC-* register: status, what blocks on each, and the evidence that will settle it. Mirrors ARCH-0001 §8. An ADR accepts a decision; this file only tracks it."
type: process
category: process
status: active
version: "0.1.5"
date: "2026-09-23"
updated: "2026-10-01"
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
| **DEC-005** | MVP scope — what the early-Dec demo demonstrates | **accepted → ADR-0002** | everything downstream | ADR-0002 (Option A, multi-product/≥2-domain) |
| **DEC-006** | UI stack and interaction model for the graphical threat model | **accepted → ADR-0003** | I3 | ADR-0003 (Path A); RPT-0012, APP-0001 |
| **DEC-007** | Relationship to `tradar`: reuse / wrap / greenfield | **accepted → ADR-0001** | I2, I3 | ADR-0001 (radar/tmodel split) |
| **DEC-008** | CWE/NVD integration: live vs cached mirror; automation | open | I2, I4, R-010 | RPT-0001 §CWE/NVD |
| **DEC-009** | Generic-threat → product / product-family mapping; mitigation lifecycle | open | I4, R-020, R-021 | RPT-0001, ARCH-0001 §7 |
| **DEC-010** | Implementation stack & language for the application (GUI + backend + CLI) | open | I3 build, DEC-006 | RPT-0012; requirements APP-0001 |

## Priority

**Both Week-0-gate decisions are accepted:** DEC-007 (ADR-0001, radar/tmodel split) and DEC-005 (ADR-0002, MVP scope). They set MVP scope and how much of
tradar we reuse — everything else sizes off them. The rest are informed by
RPT-0001 and taken across I2–I4 as the evidence lands.

**Stack decided (2026-10-01):** DEC-006 and DEC-010 accepted → ADR-0003 (Path A). The
substrate (DEC-004) and the commercial-viz filter (A-044) are deliberately kept open
behind adapters so slice work can start without pre-empting them.
