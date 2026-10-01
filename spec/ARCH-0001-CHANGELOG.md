---
schema: "archdoc/v1"
id: ARCH-0001-CHANGELOG
title: "ARCH-0001 changelog"
description: "Every change to ARCH-0001, newest first. §9.5 requires an entry per version bump."
type: process
category: security
status: active
version: "0.1.6"
version_policy: "tracks ARCH-0001; one entry per version bump"
date: "2026-09-23"
updated: "2026-10-01"
needs_review: false
reviewed: true
canonical_path: spec/ARCH-0001-CHANGELOG.md
defers_to: ARCH-0001
---

# ARCH-0001 changelog

Newest first. Every ARCH-0001 version bump appends a line here (§9.5).

## 0.1.6 — 2026-10-01

**DEC-011 accepted** via ADR-0004 (storage & edges): file canonical SoT (YAML/JSON/LinkML +
link records), edge-rich typed-edge logical invariant (stable IDs across LPG / RDF-star /
reified encodings), local embedded rebuildable working store, derived (non-canonical) export.
**Narrows DEC-004** to the working-store engine pick (still open). Tracking: Edge Rich KG (#50).

## 0.1.5 — 2026-10-01

**DEC-006 and DEC-010 accepted** via ADR-0003 (**Path A**): a local-only, macOS-first
desktop app — Tauri (Rust) shell + TypeScript/WebGL frontend over a Python KG engine,
shared CLI, local IPC. Viz library (A-044) and KG substrate (DEC-004) stay open behind
adapters. Opens the I-App slice increment.

## 0.1.4 — 2026-10-01

Register (§8) adds **DEC-010** (implementation stack & language, driven by RPT-0012).
Notes that application (product) requirements now live in `spec/APP-0001`, distinct from
the object-model requirements (§4). No model change — the display/redundancy additions
(R-033/034/035) are in `ARCH-0001-PROPOSAL-v0.2.0` and fold into §3/§4 at DEC-001 acceptance.

## 0.1.3 — 2026-09-30

DEC-005 **accepted** via ADR-0002 (MVP = reviewed attack-path graph over multiple products in ≥2 domains, one deep). Adds R-022 (domain/instance-type generalization).

## 0.1.2 — 2026-09-30

DEC-007 **accepted** via ADR-0001: split into **radar** (tradar — composition/finding) and **tmodel** (architectural modeling); radar feeds tmodel. Scopes DEC-005.

## 0.1.1 — 2026-09-24

Add `AttackStep` as a first-class node (§3): one atomic action an attacker takes.
An `AttackPath` / `ThreatChain` is now defined as an ordered set of attack steps,
joined by a `step_of` typed edge. Aligns the model with the README entity list (#2).

## 0.1.0 — 2026-09-23

Genesis skeleton. Object model (§3), draft requirements (§4), interchange (§5),
risk framing (§6), the human-review/annotation model (§7), and open decisions
DEC-001…DEC-009 (§8). Nothing accepted; requirements ratified in the Week-0 gate.
