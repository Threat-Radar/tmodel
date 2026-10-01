---
schema: "archdoc/v1"
id: ADR-0001
title: "Split the work: radar (composition/finding) vs tmodel (architectural modeling)"
short_title: "radar / tmodel split"
description: "Accepts DEC-007. The existing tradar becomes the 'radar' composition/finding tool; tmodel is the blue-team architectural threat-modeling layer that consumes radar output."
type: decision
category: architecture
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0001-radar-model-split.md
accepts: DEC-007
defers_to: ARCH-0001
---

# ADR-0001 — radar / tmodel split

**Status: accepted (2026-09-30). Accepts DEC-007.**

## Context

tmodel extends the 2025 *Threat Radar* master's work (`Threat-Radar/tradar` — a
Python CLI for container/dependency composition: Docker extraction, SBOM, CVE
scanning via Grype, AI-assisted triage, reporting). DEC-007 asked whether to
**reuse** tradar's code, **wrap** it, or go **greenfield**.

## Decision

**Split the work into two complementary tools, by role:**

- **radar** (the existing `tradar`) — **composition & finding** (red-team-ish
  discovery): *what is a product made of, and what is known-vulnerable* — package
  extraction, SBOM generation, dependency/CVE scanning, discovery and reporting.
- **tmodel** — **architectural threat modeling** (blue-team): the **knowledge
  graph** and object model, threats, attack steps/paths, **human review &
  annotation**, risk metrics, mitigation lifecycle, and compliance/audit.

**radar feeds tmodel.** tradar's output (components, SBOM, CVEs) is an **input
source** to tmodel's graph. tmodel does **not** re-implement scanning/composition;
it consumes radar's results through a composition→model-input contract.

## Consequences

- tmodel's object model ingests radar/tradar output as `Component`/`Vulnerability`
  nodes; the interface is the composition→model-input mapping surveyed in
  RPT-0004 (#8).
- **DEC-005 (MVP scope) narrows:** tmodel is the modeling / graph / review layer,
  not a scanner. The MVP demonstrates model → review → risk over radar-supplied
  (and/or one other) composition, not a new scanning engine.
- Resolves #18 (application requirements): two repos/tools, one data contract.
- `tradar` continues on its own track; coordination is the data contract, not a
  merge.

## Supersedes / relates

- Accepts ARCH-0001 §8 **DEC-007**.
- Interacts with the open **DEC-005** (MVP scope), now scoped by this split.
