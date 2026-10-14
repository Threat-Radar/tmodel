---
schema: "archdoc/v1"
id: RPT-0003-dimensions
title: "RPT-0003 dimensions — threat-modeling products"
type: research
status: draft
version: "0.2.1"
date: "2026-09-26"
updated: "2026-10-12"
record: RPT-0003
---

# RPT-0003 — search dimensions

The comparison is organized around the work a product enables, not its marketing
category. Each product is assessed on the same axes. This file fixes what
"complete" means for issue #37 (deepening #7): every product in the required set
appears in every comparison table with every required field, or the cell says
**unverified** with the reason.

## 0. Required product set and fields (issue #37)

**Commercial:** IriusRisk, Microsoft Threat Modeling Tool, ThreatModeler,
SD Elements, Devici, Tutamantic, ThreatTree (sponsor request on #37).
**Open source:** OWASP Threat Dragon, OWASP pytm, Threagile, AWS Threat Composer.

| field | applies to | what the cell must hold |
|---|---|---|
| features | all | inputs, analysis method, risk scoring, AI assistance |
| integrations | all | CI/CD, issue trackers, SBOM/CVE/scanner, IaC, API — named, not "various" |
| model portability | all | documented import and export formats; round trip tested or not |
| UI / interaction model | all | diagram, form/questionnaire, graph, matrix, dashboard, text/IDE |
| pricing | all | public price with observation date, "quote only", or free/OSS |
| maturity | all | latest release or documentation date observed, and company/project status |
| repo URL, licence, activity, object model | open source | URL; SPDX licence from the repository; latest release and last push with dates; first-class objects read from the schema or source at a pinned commit |

Products found by the independent coverage enumeration (§6) are added to the
required comparison only when they are active, materially distinct **and selected
for the issue's fixed product scope**. Other active candidates are listed with a
reasoned follow-up or exclusion verdict rather than silently expanding the matrix.

## 1. Product and operating model

- commercial, free, or open source; disclosed price or sales-led quote
- hosted, self-hosted, desktop, IDE, or command-line deployment
- evidence of maintenance: release or repository activity, with an observation date
- intended operator: security specialist, architect, or developer

## 2. Model and analysis

- primary input: diagram, questionnaire, code, IaC, or model-as-code
- object model: system elements, data flows, boundaries, threats, mitigations,
  assumptions, attack paths/trees, and review state
- analysis method: STRIDE/rules, curated knowledge base, custom rules, or AI
- risk prioritization and evidence/provenance exposed to reviewers

## 3. Human interaction (UI comparison)

- diagram, form/list, text/IDE, graph, matrix, dashboard, and report views
- which view is primary, and whether the views edit one shared model
- collaborative authoring, review, status, rationale, and audit history
- AI proposal boundaries: whether machine output remains editable/reviewable

## 4. Interchange and workflow

- documented import/export format and round-trip potential (OTM and STIX 2.1 are
  the committed import formats under ADR-0007, so support for them is called out)
- version-control compatibility
- CI/CD, issue tracker, source repository, security scanner, SBOM/CVE, and API
  integration

## 5. Applicability to tmodel

Rate each product **core**, **adjacent**, **limited** or **unclear** as evidence for:

- logical object model (DEC-001, open)
- interchange (DEC-002, accepted → ADR-0007; evidence now informs the OTM/STIX
  import mappings rather than the format choice)
- risk and prioritization (DEC-003, accepted → ADR-0006)
- product/UI requirements (DEC-006, accepted → ADR-0003; APP-0001)
- human review and lifecycle traceability (R-018/R-021, DEC-009 open)

Issue #37's Phase-3 source-applicability axes are also recorded explicitly:
object model, provenance/attribution, human-review/audit, federation, and
AI-grounding. `report.md` keeps these separate from the product-design rubric so
that interchange support is not mistaken for federation evidence.

Claims are marked **documented** when supported by first-party material. This
report does not equate a vendor claim with an independently tested capability.

## 6. Completeness checks (Phase 4 focus)

The adversarial reviewer attacks two things specifically, as #37 requires:

- **missed products** — compared against an enumeration built independently of
  this report (community tool lists, OWASP material, AI-native entrants);
- **unverified claims** — every price, licence, version, date, and integration
  name must trace to a fetched first-party source in `sources.md`, or be marked
  unverified.
