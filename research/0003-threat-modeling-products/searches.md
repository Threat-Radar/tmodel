---
schema: "archdoc/v1"
id: RPT-0003-searches
title: "RPT-0003 search log"
type: research
status: draft
version: "0.2.0"
date: "2026-09-26"
updated: "2026-10-04"
record: RPT-0003
---

# RPT-0003 — search log

Search pass run 2026-09-26. Searches preferred product documentation,
specifications, repositories, release pages, and license files. Vendor pages are
used only for vendor capability claims. No product was installed or acceptance
tested in this pass.

| lane | representative queries | result |
|---|---|---|
| Commercial platforms | IriusRisk docs OTM API import export; Microsoft TMT features templates; ThreatModeler integrations IaC; SD Elements threat modeling integrations; Devici OTM; Tutamantic | six commercial products; public pricing was generally absent, so the matrix says “quote/demo” rather than guessing |
| Open-source applications | OWASP Threat Dragon README releases model JSON; AWS Threat Composer README schema AI; OWASP Threat Model Library TM-BOM | browser/desktop and web/IDE tools, current formats, releases, and licenses |
| Model-as-code | OWASP pytm README license; Threagile README YAML risk rules REST outputs | two developer-centered approaches with inspectable models and automation surfaces |
| Interchange | Open Threat Model specification; Threat Dragon TMF/TM-BOM; product import/export docs | portability is fragmented; OTM and TM-BOM are two documented convergence attempts in the reviewed sample |
| Workflow evidence | Jira GitHub Azure DevOps integrations; CI/CD APIs; repository storage; reports and review status | enterprise products emphasize workflow orchestration; OSS emphasizes inspectable, versionable artifacts |
| ThreatTree extension (2026-10-04) | ThreatTree official product, help center, pricing, DFD attack tree risk register, JSON STIX export, integrations, GitHub repository | first-party product/help/pricing evidence verified; no official public source repository identified; no installation or acceptance test performed |

## Rejected or downgraded evidence

- Search-result snippets, comparison blogs, and reseller pages were not used for
  load-bearing capability claims when first-party evidence was available.
- Marketing performance percentages and “industry-leading” claims were excluded;
  no reproducible study was supplied in the reviewed material.
- Repository stars are omitted as a maturity measure. A release or recent commit
  is more useful, but activity remains a point-in-time observation.
- Pricing is recorded only when publicly disclosed. “Commercial” does not imply a
  price tier.

## Follow-up searches

- Pin repository commits and create complete `library/` records through the #P1
  ingestion workflow.
- Acceptance-test OTM and TM-BOM round trips with representative models.
- Prototype one diagram-first and one model-as-code tool on the same threat graph;
  measure information loss, reviewer effort, and diff quality.
