---
schema: "archdoc/v1"
id: RPT-0004
title: "Product composition: SBOM and HBOM formats, tools, and the bridge to the threat model"
short_title: "Product composition"
description: "Survey of software and hardware bills of materials: formats, standards, tools, and how composition data becomes threat-model input. No design decisions are made, it only contains the evidence."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
authors:
    - role: student
      id: ty-van-heerden
decision_makers:
    - role: sponsor
      id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0004-product-composition/report.md
library_commit: "see library/ submodule pointer at time of merge"
informs: [DEC-001, DEC-002, DEC-007, DEC-008]
open_decisions: [DEC-001, DEC-002, DEC-007, DEC-008]
---

# Product composition

> **This report does not select a design.** It is evidence for the open decisions listed above.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md). 
Axes: [`dimensions.md`](dimensions.md).

## Comparison table

_In progress. Starting point: CISA Framing (3rd ed.) Table 1, updated to CycloneDX 1.7, plus SWID._

## 1. SBOM formats (CycloneDX, SPDX, SWID)

Input to DEC-002.

## 2. HBOM (hardware and firmware)

Input to DEC-001.

## 3. Tools (Syft, Grype, Trivy, Dependency-Track)

Input to DEC-002 and DEC-007.

## 4. How tradar uses these today

Input to DEC-007.

## 5. The bridge: components to CVEs and CWEs

Input to DEC-001 and DEC-008.

## 6. Build identity: how composition pins a product version

Input to DEC-001.

## 7. Synthesis: implications for tmodel