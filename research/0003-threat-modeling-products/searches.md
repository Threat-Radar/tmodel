---
schema: "archdoc/v1"
id: RPT-0003-searches
title: "RPT-0003 search log"
type: research
status: draft
version: "0.3.2"
date: "2026-09-26"
updated: "2026-10-12"
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

## Issue #37 deepening pass (2026-10-11)

The pass re-checked each required product against first-party documentation,
repository metadata, release history, licence files and source/schema files at the
pinned commits in `sources.md`.

| lane | queries / fetches (verbatim where a search engine was used) | result |
|---|---|---|
| ThreatModeler integrations | fetched `threatmodeler.ai/integrations`; search “ThreatModeler API export threat model OTM JSON documentation”; search “ThreatModeler pricing plans 2026”; fetched the AWS Marketplace listing | integrations now named one by one; no official export format found (a community forum post on exports was moved and returned 404, so it is not used); pricing is usage/quote based; analyst and reseller pages rejected for pricing |
| SD Elements | search “site:docs.sdelements.com integrations issue tracker Jira GitLab Azure DevOps verification tool”; fetched the issue-tracker and verification-tool “Supported tools” pages and the FAQ | 8 issue trackers and ~20 verification tools named in first-party docs, including OWASP Dependency-Track (SBOM); OSD and SaaS deployment |
| Devici | reviewed the Devici product page and SD Elements “Exporting an OTM from Devici” documentation | free tier, OTM/draw.io/TM7 import, Jira/Azure DevOps with status sync, accept/mitigate/accepted-risk with audit trail, OTM 0.2.0 export contents |
| IriusRisk | fetched `iriusrisk.com/integrations`; `iriusrisk.com/pricing` returned 404; search “IriusRisk Community Edition free plan 2026”; fetched `iriusrisk.com/plans` | Community edition (free, 3 threat models, SaaS) and Enterprise (quote, SaaS or on-premise); integrations page names OWASP ZAP as its only security tool |
| Microsoft TMT | fetched the release-notes index and the 7.3.51110.1 notes | latest GA 7.3.51110.1 (2025-11-10) — the draft's “last materially updated in 2022” was wrong |
| Tutamantic | fetched `tutamantic.com` and hashed it | no new technical documentation: no prices, API, export format, or named integrations; footer © 2024 |
| ThreatTree | fetched and hashed the homepage, Help Center and pricing page (all `Last-Modified` 2026-10-11) | prices unchanged but “early adopter” wording gone; pricing page and Help Center disagree on Sentinel and OneTrust |
| OSS repositories | GitHub API: repo metadata, `/releases/latest`, commits since 2025-10-11, `LICENSE` history; raw schema/source files at pinned commits | licence, activity and object model for all four tools; **pytm licence corrected to MIT**; Threat Dragon OTM and TM-BOM import code found |
| Coverage enumeration | fetched the OWASP Threat Modeling Cheat Sheet (names methods, no tools); fetched `hysnsec/awesome-threat-modelling`; search “AI threat modeling tool 2026 platform automated design review (Seezo OR "Prime Security" OR "ThreatCanvas" OR "Aribot")”; search “"Threats Manager Studio" threat modeling tool”; search “aws.amazon.com "AWS Security Agent" threat modeling preview what's new 2026”; GitHub API for CAIRIS, STRIDE GPT, Gram, Threatspec, MAL toolbox, OWASP threat-model-cookbook; fetched Gram and STRIDE GPT READMEs and the AWS What's New page | candidates and verdicts are in the report's coverage section |

### Rejected or downgraded in this pass

- Gartner, Capterra, G2, Techjockey and CB Insights pages: rejected for pricing and
  capability claims (secondary, undated, or behind login).
- ThreatModeler AWS Marketplace per-dimension hourly figures: not used. The listing
  shows the same figure across hundreds of dimensions, which does not read as a list
  price for the product.
- ThreatModeler community-forum export answer: the URL now redirects and then returns
  404, so it could not be read.
- Threats Manager Studio: only a conference speaker bio and a book chapter turned up,
  both secondary, so the product could not be verified.
- Seezo, Prime Security, ThreatCanvas, Aribot, Apiiro: search results were press or
  secondary coverage. Seezo and Prime Security homepages resolved but were not read for
  capabilities; the ThreatCanvas product URL tried returned 404. Listed as unverified
  leads only.
- Threatspec (no push since 2020-12-30) and OWASP threat-model-cookbook (archived):
  excluded as inactive.

## Issue #37 Phase-1 parallel research (2026-10-12)

Three independent lanes searched the frozen dimensions in parallel and compared their
findings with the existing report. Capability claims used first-party sources; community
lists were used only to discover coverage candidates.

| lane | dimensions and searches | outcome |
|---|---|---|
| commercial product and analysis | §1–§2; IriusRisk plans/create/integrations, Microsoft TMT overview/features/releases, ThreatModeler platform/System Mapping/Secure Design Graph/integrations/VAST, SD Elements product and integration documentation, Devici product documentation, Tutamantic, ThreatTree Help/Pricing | corrected previously thin ThreatModeler AI/graph/audit evidence and added Devici's documented status/version history; no material gap for the other five commercial products |
| open-source model and analysis | §1–§2; repository, release, licence, README and pinned source/schema checks for Threat Dragon, pytm, Threagile and Threat Composer | added pytm native JSON loading/round-trip evidence and `SetOfProcesses`; no material gap for the other three OSS products |
| interaction, interchange and completeness | §3–§6; UI/review/audit, OTM/STIX/TM-BOM, workflow integrations, and an independent active-product enumeration | corrected ThreatTree DFD-link and STIX-mapping wording; added OWASP ThreatAtlas as a materially distinct follow-up candidate; no other material gap in the fixed product set |

The new evidence came from the ThreatModeler platform and graph pages, Devici product
documentation, pytm README and v1.4.0 release, ThreatTree Help Center, and the OWASP
ThreatAtlas project page and changelog. Exact URLs and uses are recorded in `sources.md`.

## Independent review passes (2026-10-12)

Separate checks then reviewed source integrity, adversarial completeness, and report
clarity without expanding the fixed comparison scope:

| pass | independent scope | material findings and disposition |
|---|---|---|
| evidence integrity | trace load-bearing claims to `sources.md`; hunt contradictions and overreach | corrected Devici ticket-close wording, qualified lifecycle claims, narrowed Dependency-Track to its documented integration, fixed revision-date language, and added the missing OWASP Cheat Sheet source row |
| adversarial completeness | attack required-product coverage, frozen matrix fields, missed products, Phase-3 axes and deliverables | confirmed the eleven required products and deliverables; added the required-field ledger and five Phase-3 axes; reconciled the fixed-scope rule; the Phase-1 re-check then added ThreatAtlas to the follow-up enumeration |
| clarity and completeness | check section order, lead-ins, terminology, negative-claim qualification and source consistency | retained the comparison-first structure and narrowed claims where documentation establishes only vendor-reported or untested behavior |

The report remains comparison-first, followed by per-product sections, synthesis,
gap analysis and review gates; no broad rewrite was needed.
