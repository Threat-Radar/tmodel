---
schema: "archdoc/v1"
id: BACKLOG-0001
title: "tmodel backlog"
short_title: "Backlog"
description: "Task backlog. Each task becomes a GitHub issue; this file is the durable index. Increments are in PLAN-0001 §8."
type: backlog
category: process
status: draft
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
needs_review: true
reviewed: false
canonical_path: project/BACKLOG-0001.md
defers_to: ARCH-0001
agent_notes: >
  Tasks are the execution unit; topics are the assignment unit (PROC-0001).
  Keep the id stable when it becomes an issue — put T-NNN in the issue title.
---

# Backlog

**Convention.** `T-NNN` is stable and survives becoming a GitHub issue — put the
id in the issue title. Status: `todo` · `doing` · `review` · `done` · `parked`.
Size: `S` <½day · `M` ~1day · `L` ~3days. Increments are in `PLAN-0001` §8.

**The demo floor is I3 (Nov 10)** — everything after is upside.

---

## I0 — Harness · Sep 23–29

| id | task | own | sz | status |
|---|---|---|---|---|
| T-001 | Create GitHub repo `Threat-Radar/tmodel` (public) | PL | S | todo |
| T-002 | Fork `m-of-n/library` → `Threat-Radar/library`; wire as `tmodel` submodule (absolute URL) | PL | S | todo |
| T-003 | Add 4 students + Prof. Haskell as admins (a `Threat-Radar/tmodel` team with `admin` on the repo) | PL | S | todo |
| T-004 | Confirm roster; add student handles to `CODEOWNERS`; vault people files | PL | S | todo |
| T-005 | Port/author role skills into `tmodel/.claude/skills/` (research, propose-arch) | all | M | todo |
| T-006 | Publishing site (mkdocs or equivalent) — defer decision; stub for now | all | M | parked |
| T-007 | Branch protection on `main` (PR-only, 1 review) | PL | S | todo |
| T-008 | **Week-0 gate:** ratify R-set, DEC-005 (MVP scope), DEC-007 (tradar relationship) | all | L | todo |

## I1 — Research · Sep 30–Oct 13

| id | task | own | sz | status |
|---|---|---|---|---|
| T-020 | RPT-0001: methodologies (STRIDE, PASTA, attack trees, LINDDUN, OCTAVE, …) | — | L | todo |
| T-021 | RPT-0001: commercial products + competitive **UI comparison** | — | L | todo |
| T-022 | RPT-0001: open-source projects (with repo links, licenses, activity) | — | L | todo |
| T-023 | RPT-0001: academic papers | — | M | todo |
| T-024 | RPT-0001: **schema definitions & object models** for threat modeling | — | L | todo |
| T-025 | RPT-0001: risk-metric standards (CVSS, ISO/SAE 21434, Common Criteria) | — | M | todo |
| T-026 | RPT-0001: MITRE CWE + NVD as integration targets | — | M | todo |
| T-027 | Every source → a `library/` record; distill technical specs toward schema | all | L | todo |
| T-028 | Define target use cases; draft DEC-005 options with evidence | all | M | todo |

## I2 — Model · Oct 14–27

| id | task | own | sz | status |
|---|---|---|---|---|
| T-040 | ARCH-0001 → v0.2: object model (input to DEC-001) | — | L | todo |
| T-041 | `spec/schema/` first draft importing one existing format; a round-trip vector | — | L | todo |
| T-042 | CWE/NVD integration design (DEC-008) | — | M | todo |
| T-043 | Risk-metric survey → DEC-003 direction | — | M | todo |

## I3 — MVP core (demo floor) · Oct 28–Nov 10

| id | task | own | sz | status |
|---|---|---|---|---|
| T-060 | Interactive graphical threat model + threat-chain view (DEC-006) | — | L | todo |
| T-061 | Human review/annotation model wired: impact, accept/reject, rationale (R-018…R-021) | — | L | todo |
| T-062 | End-to-end on one worked example (input → graph → review → risk) | — | L | todo |

## I4 — Risk & mitigation · Nov 11–24

| id | task | own | sz | status |
|---|---|---|---|---|
| T-080 | Risk metrics computed per product/environment (DEC-003) | — | L | todo |
| T-081 | Mitigation mappings; generic→product & product-family mapping (R-020) | — | L | todo |
| T-082 | Mitigation tracking over the design lifecycle (R-021) | — | M | todo |
| T-083 | NVD lookup automation (DEC-008) | — | M | todo |

## I5 — Integrate & demo · Nov 25–Dec 5

| id | task | own | sz | status |
|---|---|---|---|---|
| T-100 | Vectors green; docs; published site | — | M | todo |
| T-101 | Demo script + dry run | all | M | todo |

## Parking lot

- ISO/SAE 21434 full risk analysis (high value, optional; may exceed one semester).
- Export to a common threat-model format (R-006).
- Rule-based scanning engine, if not chosen at DEC-005.
