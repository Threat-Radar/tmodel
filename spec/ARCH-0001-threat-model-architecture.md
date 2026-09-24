---
schema: "archdoc/v1"
id: ARCH-0001
title: "Threat-model architecture — object model, risk, and human-reviewed attack paths"
short_title: "Threat-model architecture"
description: "The source of truth for tmodel: the logical object model, requirements, interchange, risk metrics, and the human review/annotation model. Nothing is accepted; every DEC-* is open."
type: architecture
category: security
status: draft
version: "0.1.1"
version_policy: "semver; PATCH = editorial; MINOR = additive; MAJOR = breaking. version and updated move together (§9.5)."
date: "2026-09-23"
updated: "2026-09-24"
authors:
  - role: sponsor
    id: paul-lambert
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: spec/ARCH-0001-threat-model-architecture.md
constraints:
  no_invented_decisions: true
  human_review_is_first_class: true
agent_notes: >
  This is the architecture, not the plan. Scheduling lives in PLAN-0001.
  Every architectural question routes to an open DEC-* in §8. Do not mark any
  DEC accepted from any file other than an ADR-NNNN (§9).
---

# ARCH-0001 — Threat-model architecture

**Status: draft (v0.1.0). Nothing here is accepted. Every `DEC-*` in §8 is open.**

This is a **skeleton set for week 1**. Requirements and final goals are ratified
in the Week-0 gate (PLAN-0001). It records the shape of the problem and the
decisions that must be made, so that research (RPT-0001) has targets and code
does not decide anything by accident.

## 1. Purpose and scope

tmodel is a threat-modeling system whose model is a **knowledge graph**, whose
attack paths are **reviewable and annotatable by humans**, and whose risk
metrics say *how bad* a threat is in a **specific product's** environment.

It extends the 2025 *Threat Radar* work, which analyses threats from **container
and dependency composition** (`Threat-Radar/tradar`). That is one dimension of
input. tmodel generalises: the container view is a source of components and
weaknesses, not the whole model.

**In scope:** the object model; import (and possibly export) of existing
threat-model formats; risk metrics; the human-review/annotation model; a
graphical, interactive representation of threats and threat chains; mapping a
generic threat onto a specific product and product family; tracking whether a
threat stays mitigated across a product's design lifecycle.

**Explicitly deferred to a `DEC-*`, not decided here:** encoding, graph
substrate, UI stack, risk-metric scheme, and how much of `tradar` is reused.

## 2. What this proves — and what it does not

An AI-generated threat model is a **set of hypotheses**. It is useful only if a
human can review, correct, and own it.

- The system **surfaces** candidate threats, weaknesses and attack paths.
- A **human** determines real impact in their environment, accepts or rejects a
  path, and records why (§7).
- Traceability from a machine-proposed element to its human review is a
  **hard requirement** (R-018…R-021), not a feature.

Threat modeling has historically been manual — architects and domain experts
drawing attack paths by hand. tmodel's contribution is to make that faster and
current, **without removing the human from the loop**.

## 3. The object model (logical types)

Encoding-neutral. Names are working labels; DEC-001 ratifies the model.

| Type | What it is |
|---|---|
| **Asset** | Something worth protecting; the thing damage happens to |
| **Component** | A part of the system (service, container, dependency, source module) |
| **TrustBoundary** | Where control or assumptions change |
| **Weakness** | A class of flaw — maps to **MITRE CWE** |
| **Vulnerability** | A concrete instance — maps to **CVE / NVD** |
| **Threat** | An adverse action against an asset via a component/boundary |
| **AttackStep** | One atomic action an attacker takes — a single move in a path |
| **AttackPath / ThreatChain** | An ordered set of attack steps leading to damage; rendered as a graph |
| **Mitigation** | A control that reduces a threat, mapped to the threat(s) it addresses |
| **RiskScore** | *How bad* — per §6, per product/environment |
| **Review** | Human judgement attached to any element: impact, accept/reject, rationale, reviewer, date (§7) |
| **Product / ProductFamily** | The concrete thing a generic threat is mapped onto; family members may differ in which attack paths are mitigated |

Relations are **typed edges** (`exploits`, `mitigated_by`, `part_of`, `step_of`,
`instance_of`, `reviewed_by`, `applies_to_product`, `supersedes`) — the same
discipline the `library/` knowledge graph uses. Typed edges make the model
queryable ("every unmitigated attack path bearing on asset X in product Y").

## 4. Requirements (draft)

`R-NNN`. All **draft** until the Week-0 gate. Each names a capability, not a design.

- **R-001** Represent the §3 types and typed relations as a queryable graph.
- **R-002** Ingest components and weaknesses from container/dependency analysis (reuse tradar output; DEC-007).
- **R-003** Ingest source-code composition (candidate expansion; DEC-005).
- **R-004** Support rule-based scanning that emits Weaknesses/Threats (candidate; DEC-005).
- **R-005** Import at least one existing threat-model format; round-trip proven by a vector.
- **R-006** Optionally export to a common format.
- **R-010** Map Weakness→CWE and Vulnerability→CVE, with automated NVD lookup (DEC-008).
- **R-011** Compute a risk metric ("how bad") per threat, per product/environment (DEC-003).
- **R-012** Support ISO/SAE 21434 risk analysis as an option (high value; DEC-003).
- **R-013** Support a Common Criteria attack-feasibility metric (DEC-003).
- **R-014** Render threats and threat chains as an interactive graph (DEC-006).
- **R-015** Let a user edit/author attack paths in the graphical view.
- **R-018** Attach a human Review to any element; nothing machine-proposed is "final" without it.
- **R-019** A human sets the real impact of a damage type in their environment.
- **R-020** Map a generic threat onto a specific product and a product family.
- **R-021** Track whether a threat is mitigated across a product's design lifecycle; family members may differ per attack path.
- **R-030** Expand the `library/` knowledge graph as a first-class deliverable.

## 5. Interchange

The field already has formats and object models (surveyed in RPT-0001). tmodel
**imports** them rather than inventing in a vacuum, and **may export** a common
form. Imported formats are recorded as `library/` records; the mapping to our
model is a `MAP-NNNN` document; round-trips are proven by `spec/vectors/`.

## 6. Risk — "how bad is a threat"

A threat's badness is **not** intrinsic; it depends on the asset and the
environment. The metric scheme is open (DEC-003) and must at least accommodate:
CVSS (base/temporal/environmental), a per-environment impact set by a human
(R-019), and — as options — ISO/SAE 21434 and a Common Criteria feasibility
score. RPT-0001 surveys these before DEC-003 is taken.

## 7. Human review, annotation, and traceability

The knowledge graph is **annotated to show review**. A `Review` node carries the
reviewer, date, verdict (accept/reject/needs-work), the impact the human
assigned, and a rationale, and it is a typed edge to the element it reviews. This
answers the sponsor's questions directly:

- *How do we annotate a knowledge graph to show human review?* → `Review` nodes and `reviewed_by` edges (R-018).
- *How do we map a generic threat to a specific product?* → `applies_to_product` edges to `Product`/`ProductFamily` (R-020).
- *How do we track a threat's mitigation over the design lifecycle?* → `Mitigation` state is per product and versioned; a query returns the mitigation status at any point in the lifecycle (R-021).

## 8. Open decisions

All open. An `ADR-NNNN` accepts one; nothing else does (§9).

| id | question |
|---|---|
| **DEC-001** | The core object model — the first-class types and typed relations (§3). |
| **DEC-002** | Encoding / serialization, and which existing formats we import (and export). |
| **DEC-003** | Risk-metric scheme: CVSS, custom, ISO/SAE 21434, Common Criteria feasibility — or a composite. |
| **DEC-004** | Knowledge-graph substrate and the annotation/review model (§7). |
| **DEC-005** | MVP scope: which expansion dimension(s) beyond container SCA the demo implements. |
| **DEC-006** | UI stack and interaction model for the graphical, interactive threat model. |
| **DEC-007** | Relationship to `tradar`: reuse its code, wrap it, or greenfield. |
| **DEC-008** | CWE/NVD integration: live lookup vs cached mirror; how automation runs. |
| **DEC-009** | Generic-threat → product / product-family mapping and mitigation-lifecycle tracking model. |

The register with status and evidence links is `project/DECISIONS-0001.md`.

## 9. Governance

**9.1 Source of truth.** This document is authoritative for the architecture.
Every other document defers to it.

**9.4 No parallel architecture documents.** Do not write a rival essay. Propose a
diff against this file as `spec/ARCH-0001-*-PROPOSAL-*.md`.

**9.5 `version` and `updated` move together.** Any change bumps both, and appends
a line to `ARCH-0001-CHANGELOG.md`. CI (`bin/validate-archdoc`) enforces it.

**Acceptance.** A `DEC-*` is accepted only by an `ADR-NNNN` file, with a changelog
line and a status update here pointing at the ADR. Not in a PR body, a commit
message, a Zoom note, or a comment.
