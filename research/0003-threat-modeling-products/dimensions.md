---
schema: "archdoc/v1"
id: RPT-0003-dimensions
title: "RPT-0003 dimensions — threat-modeling products"
type: research
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
record: RPT-0003
---

# RPT-0003 — search dimensions

The comparison is organized around the work a product enables, not its marketing
category. Each product is assessed on the same axes.

## 1. Product and operating model

- commercial, free, or open source; disclosed price or sales-led quote
- hosted, self-hosted, desktop, IDE, or command-line deployment
- evidence of maintenance: release or repository activity, with an observation date
- intended operator: security specialist, architect, or developer

## 2. Model and analysis

- primary input: diagram, questionnaire, code, IaC, or model-as-code
- object model: system elements, data flows, boundaries, threats, mitigations,
  assumptions, and review state
- analysis method: STRIDE/rules, curated knowledge base, custom rules, or AI
- risk prioritization and evidence/provenance exposed to reviewers

## 3. Human interaction

- diagram, form/list, text/IDE, graph, matrix, dashboard, and report views
- collaborative authoring, review, status, rationale, and audit history
- AI proposal boundaries: whether machine output remains editable/reviewable

## 4. Interchange and workflow

- documented import/export format and round-trip potential
- version-control compatibility
- CI/CD, issue tracker, source repository, security scanner, SBOM/CVE, and API
  integration

## 5. Applicability to tmodel

Rate each product **core**, **adjacent**, **limited** or **unclear** for:

- logical object-model evidence (DEC-001)
- interchange evidence (DEC-002)
- risk and prioritization evidence (DEC-003)
- product/UI requirements (DEC-006)
- human review and lifecycle traceability (R-018/R-021)

Claims are marked **documented** when supported by first-party material. This
report does not equate a vendor claim with an independently tested capability.
