---
schema: "archdoc/v1"
id: ADR-0002
title: "MVP scope for the early-December demo"
short_title: "MVP scope"
description: "Accepts DEC-005 — the tmodel MVP is a reviewed attack-path graph over multiple products across at least two domains (one deep), demonstrating diverse-domain architecture and generic-model→instance-type mapping. Scoped by the ADR-0001 radar/tmodel split."
type: decision
category: process
status: accepted
version: "1.0.0"
version_policy: "semver; an accepted ADR is 1.0.0 and only changes to record superseding"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: false
reviewed: true
canonical_path: spec/ADR-0002-mvp-scope.md
accepts: DEC-005
defers_to: ARCH-0001
---

# ADR-0002 — MVP scope

**Status: accepted (2026-09-30). Accepts DEC-005.** Option A (reviewed attack-path
graph), **expanded by the sponsor** to span multiple products and domains.

## Context

- **ADR-0001** split the work: **radar** (= `tradar`) does composition & finding;
  **tmodel** is the architectural threat-modeling / knowledge-graph / human-review
  layer that **consumes** radar output. The MVP is **not a scanner**.
- **Demo floor is I3 (Nov 5)**; ~5 weeks, 4 students; achievable beats ambitious.
- Evidence: RPT-0011 (lean RDF; reuse STIX/BRON/CWE/CVE/D3FEND; PROV-O + SHACL),
  the ISO 21434 catalog, FIPS 140 family, RPT-0004 composition.

## Decision

The MVP is **Option A — a reviewed, grounded attack-path graph** — proven **not on
one product but across multiple products in at least two domains**, with **one
modeled deeply** and the other(s) demonstrating breadth:

For each product: ingest **radar output** → build the KG (assets, components,
CVEs → CWE → CAPEC → ATT&CK via the **BRON** backbone) → render an **interactive
threat / attack-path graph** → a human **reviews & annotates** an attack path
(impact S/F/O/P, accept/reject, rationale, **PROV-O** provenance) → a **risk score
that reflects the human input**.

Two sponsor requirements make this more than a single-product slice:

1. **Diverse-domain architecture.** The object model must **generalize across
   domains** (e.g. software / OSS, automotive-embedded, hardware-system), not be
   hardcoded to one. The MVP includes an explicit **architecture note** on domain
   abstraction and demonstrates the model on products from **≥2 domains**.
2. **Generic model → diverse instance types.** Demonstrate mapping the **generic**
   model (threats/weaknesses/attack patterns) onto **specific product instances of
   different types**, where instance identity differs by type:
   - **software** — a build / commit / hash / SBOM,
   - **hardware** — firmware + buses + compute cores (HBOM),
   - **system** — hierarchical composition of the above.
   This engages R-020 and the generic↔instance half of DEC-009 at MVP level.

## Scope

**In:**
- Multiple products across **≥2 domains**; **one deep** (full graph + review + risk),
  the other(s) a breadth demonstration that the model generalizes.
- KG with the CVE→CWE→CAPEC→ATT&CK backbone; interactive attack-path graph.
- Human review/annotation (impact, verdict, rationale, provenance).
- A simple risk score reflecting the review.
- **Domain-abstraction architecture note** + **product-type → instance mapping**
  (software/hardware/system identity).

**Out (post-MVP upside, same graph):**
- Automated product-**family** mitigation divergence; mitigation-lifecycle
  automation (I4); full compliance/audit (ADR-0001 Option B / #19); NSF OKN
  federation (#25 parking lot); multiple scanning dimensions (radar's job).

## Architectural considerations for diverse domains (MVP-level)

- **Domain** and **product type** are first-class: a small **product-type taxonomy**
  (software / hardware / system) with per-type **instance-identity** schema
  (hash/commit/SBOM vs firmware/bus/core vs hierarchy).
- **Generic ↔ instance split:** generic threats/weaknesses/attack patterns live
  once; a per-instance overlay records applicability + review + (later) mitigation
  status. The MVP shows the overlay for instances of ≥2 types.
- **Domain-specific vocabulary binds to the shared backbone:** e.g. automotive via
  the ISO 21434 object model (asset/damage/threat-scenario) mapping onto the same
  CWE/CVE/ATT&CK graph; software via SBOM/components.
- Captured in ARCH-0001 (R-022) and detailed in the modeling-requirements work (#15).

## Acceptance (demo script)

For each product: load (radar) → see threats + a threat chain as a graph →
review/annotate an attack path → risk score updates from the human input → mapped
to the specific product instance (correct type), mitigation state visible. Show it
on the **deep** product fully and on a **second-domain** product to prove
generalization.

## Risk & bound

Multi-product / multi-domain is more than a single-product slice — scope risk.
**Bound it:** go *deep on exactly one* product; the second domain is a
**generalization demonstration** (architecture + a working-but-shallower graph),
with the domain-abstraction documented even where not fully implemented. Demo
floor stays Nov 5; depth is the gate, breadth is the proof-of-generality.

## Consequences

Pulls R-020 and the generic↔instance part of DEC-009 to MVP level; adds R-022
(domain/instance-type generalization) to ARCH-0001. Student reports feed it
(frameworks→model, products/UI→graph, schema→object model + instance types,
composition→radar input). Compliance (B) and federation (D) remain post-MVP.
