---
schema: "archdoc/v1"
id: RPT-0013
title: "Secure Development Lifecycle & conformance"
short_title: "SDL & conformance"
description: "Landscape of secure-development-lifecycle guidelines (NIST SSDF, Microsoft SDL, OWASP SAMM, BSIMM, SAFECode, ISO/IEC 27034, ISO/SAE 21434 process, IEC 62443-4-1, …), a requirements crosswalk showing how the specs overlap (MAP-0001), and the conformance-validation / document-governance model for tmodel. Evidence, not decisions."
type: research
category: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
authors:
  - role: sponsor
    id: paul-lambert
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0013-sdl-conformance/report.md
defers_to: ARCH-0001
agent_notes: >
  Skeleton. Plan is in dimensions.md (five lanes). Drives the iteration-7 model additions
  (SDL/Gate/Milestone object, Mitigation `kind`, conformance validation, governed document-
  views) and the requirements crosswalk MAP-0001. SDL is post-MVP (ADR-0002 scope guard);
  this is the research that makes it buildable later. Every guideline → a library/ record.
---

# RPT-0013 — Secure Development Lifecycle & conformance

**Evidence, not a decision.** Plan: `dimensions.md`. Feeds iteration-7 of the object model
(#15) and the deferred audit/compliance work (#19). The headline output is **MAP-0001**, a
requirements crosswalk showing how the SDL specs overlap.

## 0. Summary & gap analysis

_pending — the common-requirement set, the biggest overlaps/gaps, and the recommended SDL +
conformance model for tmodel._

## 1. SDL / SSDL guideline landscape (Lane 1)

_pending — NIST SSDF (SP 800-218/218A), Microsoft SDL, OWASP SAMM, BSIMM, SAFECode,
ISO/IEC 27034, ISO/SAE 21434 process, ISO 26262, IEC 62443-4-1, CISA Secure by Design,
SLSA / SP 800-161. Each → a library record._

## 2. Phases, gates, checkpoints, milestones (Lane 2)

_pending — per-framework stage/gate vocabulary; the gate crosswalk onto the canonical
LifecyclePhase axis; program-management attributes (entry/exit criteria, owner, dates, deps)._

## 3. Requirements mapping & overlap → MAP-0001 (Lane 3)

_pending — atomic requirements per spec; the crosswalk (rows = common requirement, columns =
spec, cells = clause/ID); mapping onto our object model._

## 4. Conformance validation & automation (Lane 4)

_pending — how conformance is evidenced/assessed; the automatable "every in-scope threat has an
approved mitigation" check; relation to ISO 21434 work-products and #19._

## 5. Document governance as views over the KG (Lane 5)

_pending — owner / change-tracking / approval / version patterns; the governed document-view
(threat model, SDL plan) as an approvable projection over the KG-as-SoT (ADR-0004, §10, §4)._
