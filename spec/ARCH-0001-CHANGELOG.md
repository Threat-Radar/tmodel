---
schema: "archdoc/v1"
id: ARCH-0001-CHANGELOG
title: "ARCH-0001 changelog"
description: "Every change to ARCH-0001, newest first. §9.5 requires an entry per version bump."
type: process
category: security
status: active
version: "0.1.1"
version_policy: "tracks ARCH-0001; one entry per version bump"
date: "2026-09-23"
updated: "2026-09-24"
needs_review: false
reviewed: true
canonical_path: spec/ARCH-0001-CHANGELOG.md
defers_to: ARCH-0001
---

# ARCH-0001 changelog

Newest first. Every ARCH-0001 version bump appends a line here (§9.5).

## 0.1.1 — 2026-09-24

Add `AttackStep` as a first-class node (§3): one atomic action an attacker takes.
An `AttackPath` / `ThreatChain` is now defined as an ordered set of attack steps,
joined by a `step_of` typed edge. Aligns the model with the README entity list (#2).

## 0.1.0 — 2026-09-23

Genesis skeleton. Object model (§3), draft requirements (§4), interchange (§5),
risk framing (§6), the human-review/annotation model (§7), and open decisions
DEC-001…DEC-009 (§8). Nothing accepted; requirements ratified in the Week-0 gate.
