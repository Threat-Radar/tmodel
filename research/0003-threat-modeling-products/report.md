---
schema: "archdoc/v1"
id: RPT-0003
title: "Threat Modeling Products — commercial and open source"
short_title: "Threat-modeling products"
description: "Evidence-first comparison of commercial and open-source threat-modeling products, their interaction models, interoperability, workflow integration, and reusable feature requirements."
type: research
category: security
status: draft
version: "0.3.2"
date: "2026-09-26"
updated: "2026-10-12"
authors:
  - role: research
    id: kriishnaa-18
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0003-threat-modeling-products/report.md
library_commit: "pending library ingestion; verified frontier sources are logged in sources.md"
informs: [DEC-001, DEC-002, DEC-003, DEC-006, DEC-009, R-005, R-014, R-015, R-018, R-021, R-030]
open_decisions: [DEC-001, DEC-009]
issue: 7
---

# Threat Modeling Products — commercial and open source

> **Draft research report. Evidence, not decisions.** A product claim below means
> “documented by the product owner” unless it says otherwise; no product was installed
> or acceptance-tested. Sources are in [`sources.md`](sources.md), queries and rejected
> evidence in [`searches.md`](searches.md), and the comparison axes in
> [`dimensions.md`](dimensions.md). This report accepts no `DEC-*`.

## Overview

This report compares eleven threat-modeling products — seven commercial and four open source — and 
evaluates their features, interaction models, integrations, interchange formats, maturity, and 
applicability to tmodel. Version 0.3.2 deepens the original comparison with updated first-party evidence, 
repository and object-model details for open-source tools, a dedicated UI comparison, and a broader 
coverage check for missed products.

Three findings carry most of the weight:

1. **Every product is diagram-, finding- or requirement-centric; none documents the
   threat model as a reviewable graph of ordered attack paths.** ThreatTree's attack trees linked to
   DFDs and STRIDE GPT's generated attack trees come closest. Ordered, reviewable attack
   paths remain the main gap tmodel can fill (R-014/R-015, DEC-001).
2. **Review state is common but thin.** Every product with public technical detail
   records a status, sometimes with a justification, owner or ticket, and a few keep
   audit logs (Tutamantic publishes too little to say). Within the fixed eleven-product
   sample, no reviewed documentation describes a machine proposal and a human verdict kept
   as separate, attributable records, which is what R-018 requires. The coverage check now
   identifies OWASP ThreatAtlas as a follow-up precedent for explicit AI proposals and
   approval, but its persistence semantics were not acceptance-tested.
3. **OTM is the only cross-vendor format with documented producers and consumers in
   this sample** (IriusRisk, Devici → SD Elements, Threat Dragon import). It is still a
   0.2.0 specification from 2023. ThreatTree is the only product here documenting STIX
   2.1 export. Both matter because ADR-0007 commits tmodel to importing OTM and STIX 2.1.

**Decision status.** Since the first draft, DEC-002 (→ ADR-0007), DEC-003 (→ ADR-0006)
and DEC-006 (→ ADR-0003) have been accepted by ADR. This report does not revisit them.
For those decisions it now serves as input to the import mappings, risk display and
console requirements. DEC-001 (object model) and DEC-009 (product mapping and mitigation
lifecycle) remain open.

## 1. Comparison table

How to read the cells: **documented** = stated in first-party material;
**source** = read from the repository at the commit pinned in `sources.md`;
**inference** = the researcher's conclusion; **unverified** = the reviewed sources did
not confirm it. Observations are dated 2026-10-11 unless a cell says otherwise.

| product | pricing / delivery | features | integrations | model portability | UI / interaction model | maturity |
|---|---|---|---|---|---|---|
| IriusRisk | Community edition free (3 active threat models, one user, SaaS); Enterprise by quote, SaaS or on-premise | component/data-flow modeling on a draw.io-based canvas; questionnaires and templates; a rules engine generates threats, weaknesses and countermeasures; AI-assisted starts | page lists Jenkins, GitHub Actions, ServiceNow, Azure DevOps (CI/CD); Jira, Rally; OWASP ZAP; Cucumber, JBehave/JUnit; Terraform, CloudFormation; draw.io, Visio, Lucidchart, Microsoft TMT; OpenAPI. No SBOM/CVE scanner is named | OTM JSON/YAML import (author of OTM); Community exports the diagram as XML; Enterprise exports the full threat model in “multiple file formats” (formats not listed) | diagram canvas + questionnaires + templates | active commercial product; monthly updates claimed on the plans page |
| Microsoft TMT | free Windows desktop app (Windows 10+, .NET 4.7.1) | DFDs with STRIDE-per-element threat generation from templates; status, priority and justification per threat; custom templates | none documented beyond file sharing; no CI, tracker or scanner integration found | `.tm7` model and `.tb7` template files; HTML report; no neutral export | drag-and-drop DFD with separate design and analysis views | GA since 2018; latest release 7.3.51110.1 on 2025-11-10 (file-location safeguard, bug and accessibility fixes) |
| ThreatModeler | commercial; no public price list; AWS Marketplace listing (v7.4) uses usage-based pricing and deploys by CloudFormation template | System Mapping, Graph and Reporting agents operate on a Secure Design Graph populated from diagrams, code, IaC, documents and live cloud; continuous assessment; STRIDE/VAST support | Terraform, CloudFormation, ARM; GitHub Actions, Azure DevOps, Jenkins, Jira & Bitbucket, ServiceNow; AWS, GCP, Azure; ArmorCode, ServiceNow GRC. No SBOM/CVE scanner named | imports architecture and IaC; API exists per vendor; **no export format documented** in sources reviewed | diagram-based models plus a connected graph; vendor says decisions are recorded and traceable | active 2026 product surface; Marketplace v7.4 |
| SD Elements | commercial; SaaS or on-site deployment (OSD); no public price | survey- or architecture-driven requirement generation from a knowledge base; threats, weaknesses, countermeasures; verification and compliance mapping | **trackers:** Jira, GitHub, GitLab, Azure DevOps/TFS, Micro Focus ALM, ServiceNow ITSM, Rally, Digital.ai Agility; **verification:** HCL AppScan family, Checkmarx, Coverity, Fortify, Klocwork, ThreadFix, Veracode, WhiteHat, Nessus, Prisma Cloud, Black Duck, Snyk, GitLab Ultimate, SonarQube, OWASP Dependency-Check and **Dependency-Track (SBOM)** | imports OTM 0.2.0 from Devici; broader export unverified | surveys, generated requirement lists, task status, dashboards; Devici tab renders an imported diagram | active enterprise platform (docs “master” and release 5.x lines) |
| Devici | commercial; free canvas tier (“no trial clock, no credit card”); paid plan with unlimited users and models; Code Genius on Enterprise | layered diagram canvas; Codex library maps attributes → threats → mitigations (STRIDE, LINDDUN, MAESTRO, OT/IoT, “9+” frameworks); AI drafts from text or a GitHub repo | Jira and Azure DevOps with status sync back; GitHub Action re-runs Code Genius on PRs; hosted MCP endpoint (Cursor, Claude, VS Code Copilot); SD Elements hand-off to Jira/GitHub/ADO | **imports OTM, draw.io, TM7**; exports OTM 0.2.0 (canvas or REST) with elements, flows, threats, mitigations, boundaries and layout | collaborative real-time canvas; Code Genius drafts strategic, tactical and operational layers | active; part of Security Compass |
| Tutamantic | commercial cloud service plus training and consulting; prices “inquire now” (email) | reuses existing diagrams; user adds security metadata; generates threats, mitigations, “threat paths” and areas of concern | “CI/CD automation chain” and “Agile integration” mentioned; **no tool is named** | input: draw.io, Terraform, Visio, Lucidchart, “infrastructure schemas”; **export, API: unverified** | reuse of an existing diagram, enriched with metadata | site footer © 2024; latest blog post 2023-11-04; public technical documentation not found |
| ThreatTree | browser SaaS; Free $0; Pro $29/user/month; Enterprise quote with dedicated/VPC option | forests of DFDs and AND/OR attack trees linked to DFDs; STRIDE, LINDDUN, OWASP Top 10, CAPEC, MITRE ATT&CK tags; likelihood × impact (1–5 each) risk register; treatment Mitigate/Avoid/Transfer/Accept | Enterprise: Jira, ServiceNow, Linear, Azure DevOps (ticket close → risk Mitigated); Splunk HEC; Vanta, Drata; Confluence/Notion embeds; Pro+: Slack/Teams alerts. **Pricing page also lists Sentinel and OneTrust; Help Center says neither is supported** | JSON on all plans; STIX 2.1 on Pro+; PDF; Enterprise import from OpenAPI 3/Swagger 2, CloudFormation/SAM, Terraform (always creates a new DFD) | DFD editor, attack-tree editor, risk register, reports | active; pages modified 2026-10-11; no public changelog or source repository found |
| OWASP Threat Dragon | free, Apache-2.0; web app, self-hosted, or desktop (Windows, macOS, Linux) | DFD modeling; threats per element with a methodology type (`modelType`), status, severity and score; PDF reports | model storage in GitHub, GitHub Enterprise, GitLab, Bitbucket; no CI or tracker integration documented | native JSON (v2 schema); **imports OTM and TM-BOM** (source); TM-BOM import hardened in v2.6.2 | DFD canvas + per-element threat forms + report | OWASP Production project; v2.6.2 (2026-05-10); see §2 |
| OWASP pytm | free, **MIT**; Python library/CLI | model-as-code; rule-based threat findings; DFD and sequence diagrams; templated reports; recent `Agent` and `LLM` element types | none built in; fits CI as a script (inference) | Python source; native JSON output and loading; generated diagrams and reports; no foreign-tool format documented | text/IDE; generated visuals | v1.4.0 (2026-07-06); see §2 |
| Threagile | free, MIT; Go CLI, Docker image, REST server | YAML architecture model; built-in and custom (YAML-script) risk rules; explicit risk tracking | none built in; CI via container (inference) | YAML input; JSON, PDF, XLSX, diagram outputs; no import from other tools | YAML in an IDE; generated diagrams; README: UI “far from being ready” | last release v0.9.1 (2024-07-30), commits until 2026-04-08; see §2 |
| AWS Threat Composer | free, Apache-2.0; web app (browser storage), VS Code (AWS Toolkit), browser extension | structured threat-statement grammar; assumptions, mitigations and their links; architecture and dataflow sections; reference packs; insights dashboard; AI CLI and MCP server that draft starter models (Amazon Bedrock, inference costs apply) | `.tc.json` viewing on GitHub, GitLab, Bitbucket, CodeCatalyst via browser extension; MCP clients | `.tc.json` (schema v1); exports JSON, Markdown, DOCX, PDF | form-driven editor + insights dashboard; IDE editing | v1.0.85 (2026-08-24); see §2 |

### Required-field completeness ledger

The matrix above is optimized for reading. This ledger makes every subfield frozen in
`dimensions.md` explicit. A semicolon-separated integration cell is ordered **CI;
tracker; SBOM/CVE/scanner; IaC; API**. **ND** means not documented in the reviewed
sources; **unverified** means a broad claim exists but the needed detail was not
established. No round trip was acceptance-tested.

| product | input | analysis | risk scoring | AI | integrations: CI; tracker; scanner; IaC; API | import | export | round trip | dated maturity observation |
|---|---|---|---|---|---|---|---|---|---|
| IriusRisk | canvas, questionnaire, template | rules/knowledge base | unverified | assisted start | Jenkins/GitHub Actions/Azure DevOps; Jira/Rally/ServiceNow; ZAP; Terraform/CloudFormation; OpenAPI | OTM, diagrams/TMT | XML diagram; enterprise formats unnamed | not tested | plans observed 2026-10-11; active, monthly updates claimed |
| Microsoft TMT | DFD canvas/template | STRIDE per element | priority, no numeric method documented | ND | ND; ND; ND; ND; ND | `.tm7`/`.tb7` | `.tm7`, HTML report | not tested | v7.3.51110.1, 2025-11-10; GA |
| ThreatModeler | diagram, code, IaC, document, cloud | STRIDE/VAST agents over Secure Design Graph | method unverified | System Mapping/Graph/Reporting agents; vendor claims graph-grounded traceability | GitHub Actions/Azure DevOps/Jenkins; Jira/Bitbucket/ServiceNow; ArmorCode/ServiceNow GRC, no SBOM/CVE tool named; Terraform/CloudFormation/ARM; API exists | architecture/IaC | ND | not tested | Marketplace v7.4 observed 2026-10-11; active |
| SD Elements | survey/architecture | knowledge-base requirements | prioritization method unverified | ND | ND; eight named trackers; about twenty verification tools including Dependency-Track; ND; ND | Devici OTM 0.2.0 | broader export unverified | not tested | master + 5.x docs observed 2026-10-11; active |
| Devici | canvas, text, GitHub repository | Codex mappings | scoring method unverified | Code Genius drafting | GitHub Action; Jira/Azure DevOps; ND; ND; hosted MCP + OTM REST export | OTM/draw.io/TM7 | OTM 0.2.0 | not tested | product/docs observed 2026-10-11; active Security Compass product |
| Tutamantic | draw.io/Terraform/Visio/Lucidchart | generated threats/mitigations/paths; method unverified | unverified | unverified | unnamed automation; unnamed Agile integration; ND; Terraform input; API ND | named diagram/IaC inputs | ND | not tested | site observed 2026-10-11; newest public blog found 2023-11-04 |
| ThreatTree | DFD/OpenAPI/IaC | STRIDE/LINDDUN/framework tags + attack trees | likelihood × impact, 1–5 | ND | ND; Jira/ServiceNow/Linear/Azure DevOps; Splunk/Vanta/Drata but no SBOM/CVE tool named; CloudFormation/SAM/Terraform; API ND | OpenAPI/Swagger/CloudFormation/SAM/Terraform | JSON/STIX 2.1/PDF | not tested | pages modified 2026-10-11; active |
| OWASP Threat Dragon | DFD canvas | methodology-tagged per-element threats | severity + score; method unverified | ND | repository storage only; ND; ND; ND; ND | OTM/TM-BOM/native JSON | native JSON/PDF | not tested | v2.6.2, 2026-05-10; OWASP Production |
| OWASP pytm | Python source | rule-based findings | CVSS + likelihood fields | ND | scriptable in CI (inference); ND; ND; code is model, no IaC ingest; ND | Python source/native JSON | JSON/diagrams/reports | native JSON load documented; not acceptance-tested | v1.4.0, 2026-07-06; active repository |
| Threagile | YAML | built-in/custom risk rules | rule-derived risks | ND | container usable in CI (inference); ND; ND; YAML architecture, no IaC ingest documented; REST server | YAML | JSON/PDF/XLSX/diagrams | not tested | v0.9.1, 2024-07-30; last push 2026-04-08 |
| AWS Threat Composer | structured forms/`.tc.json` | threat grammar/reference packs | status fields; scoring method unverified | Bedrock CLI/MCP starter drafts | ND; ND; ND; ND; MCP | `.tc.json` | JSON/Markdown/DOCX/PDF | not tested | v1.0.85, 2026-08-24; active repository |

## 2. Open-source repository facts

Issue #37 requires repository URL, licence, activity and object model for each
open-source tool. Licence is the SPDX value from the GitHub API checked against the
`LICENSE` file. Activity was observed 2026-10-11. The object model was read from schema
or source files at the pinned commit.

| tool | repository @ commit | licence | activity | object model (first-class objects) |
|---|---|---|---|---|
| OWASP Threat Dragon | [OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) @ `1753ad0f` | Apache-2.0 | latest release v2.6.2 (2026-05-10); last push 2026-10-07; 1,077 commits in the past 12 months | v2 JSON schema: model `summary` (title, owner, description) and `detail` (contributors, reviewer, diagrams); each diagram holds `cells` (components, data flows and boundaries, typed by free-string `shape` and `type`) with `data` flags (e.g. `isEncrypted`, `isPublicNetwork`, `outOfScope`) and a `threats` array (title, type, `modelType`, status — NA, Open, Mitigated, Accepted, Transferred, Avoided, Eliminated — severity, score, mitigation) |
| OWASP pytm | [OWASP/pytm](https://github.com/OWASP/pytm) @ `381dea05` | **MIT** | v1.4.0 (2026-07-06); last push 2026-10-05; 49 commits in the past 12 months | Python classes: `TM`, `Element`, `Actor`, `Asset` (`Process`, `SetOfProcesses`, `Datastore`, `Lambda`, `Server`, `ExternalEntity`, `Agent`, `LLM`), `Boundary`, `Dataflow`, `Data`, `Threat`, `Finding` (severity, CVSS, likelihood, mitigations, response), `Assumption`, `Controls` |
| Threagile | [Threagile/threagile](https://github.com/Threagile/threagile) @ `74e323ed` | MIT | last release v0.9.1 (2024-07-30); last push 2026-04-08; 73 commits in the past 12 months, none since April | YAML model: `data_assets`, `technical_assets`, `trust_boundaries`, `shared_runtimes`, communication links on assets, `custom_risk_categories`, `risk_tracking` (status `unchecked`/`in-discussion`/`accepted`/`in-progress`/`mitigated`/`false-positive`, justification, ticket, date, `checked_by`) |
| AWS Threat Composer | [awslabs/threat-composer](https://github.com/awslabs/threat-composer) @ `4ae9bda2` | Apache-2.0 | v1.0.85 (2026-08-24); last push 2026-10-08; 79 commits in the past 12 months | `.tc.json` (schema 1): `applicationInfo`, `architecture`, `dataflow`, `assumptions`, `mitigations` (with status), `threats` (threat source, prerequisites, action, impact, impacted goals and assets, status), `assumptionLinks`, `mitigationLinks`, `brainstorm` |

**Correction from v0.2.0:** pytm was listed as GPL-3.0. Its `LICENSE` file has been MIT
since 2018 and was MIT at the commit the first draft reviewed. That error would have
wrongly excluded pytm under APP-0001 A-044 (no copyleft).

The interchange formats beside these tools: **OTM** ([iriusrisk/OpenThreatModel](https://github.com/iriusrisk/OpenThreatModel))
— latest release 0.2.0 (2023-08-30), last commit 2025-12-11; the specification is
CC-BY-SA-4.0 and the schema file states Apache-2.0. **TM-BOM**
([OWASP/www-project-threat-model-library](https://github.com/OWASP/www-project-threat-model-library))
— MIT, release v1.0.2 (2025-10-20); Threat Dragon ships TM-BOM examples as CycloneDX
(`.cdx.json`) files.

## 3. UI comparison

The issue asks for the UI/interaction model of each product. The table records each
product's **primary** surface and whether other views edit the same model.

| product | primary surface | other views | one shared model? | where review happens | attack paths shown as |
|---|---|---|---|---|---|
| IriusRisk | diagram canvas (draw.io-based) | questionnaires, templates, threat/countermeasure lists, reports | likely (inference) | threat and countermeasure lists | not documented |
| Microsoft TMT | DFD canvas (design view) | analysis view: threat list + property pane; HTML report | yes (one `.tm7`) | analysis view: status, priority, justification | not supported |
| ThreatModeler | diagram canvas | cloud/IaC-generated models and Secure Design Graph | vendor documents one connected graph | recorded/traceable decisions and reports claimed; behavior not tested | not documented |
| SD Elements | survey / requirement list | dashboards; imported Devici diagram tab | requirement list is the model | task status, verification results | not supported |
| Devici | collaborative canvas (layered) | threat/mitigation panel; MCP in IDE | yes | on the canvas: accept, mitigate, accepted-risk, with audit trail | not documented |
| Tutamantic | the user's existing diagram | unverified | unverified | unverified | “threat paths” claimed; presentation unverified |
| ThreatTree | DFD editor + attack-tree editor | risk register, reports | yes (forest) | register: owner, collaborator, treatment; status set by ticket sync | **AND/OR attack trees linked to a DFD** |
| OWASP Threat Dragon | DFD canvas | per-element threat form; report | yes | threat status on each element | not supported |
| OWASP pytm | Python source (text/IDE) | generated DFD, sequence diagram, report | yes; visuals are generated, read-only | none built in | not supported |
| Threagile | YAML (text/IDE) | generated diagrams, PDF/XLSX reports | yes; visuals generated | `risk_tracking` entries in YAML | not supported |
| AWS Threat Composer | structured forms (threat grammar) | insights dashboard, architecture and dataflow sections, IDE editor | yes (`.tc.json`) | threat and mitigation status fields | not supported |

Three interaction patterns recur: **canvas-first** (TMT, Threat Dragon, IriusRisk,
Devici, ThreatTree), **list/questionnaire-first** (SD Elements, Threat Composer), and
**text-first with generated views** (pytm, Threagile). No product lets a reviewer step
through an ordered attack path as a first-class object. ThreatTree's AND/OR trees
express alternatives and conjunctions, not an ordered chain.

## 4. Applicability to tmodel

This applies the rubric in [`dimensions.md`](dimensions.md) §5. **Core** means strong
evidence for that area, **adjacent** useful but incomplete, **limited** little useful
evidence, **unclear** not confirmed by the reviewed sources. The ratings describe each
product's value as evidence, not product quality.

| product | DEC-001 object model | interchange (ADR-0007 import mapping) | risk (ADR-0006 display) | UI (ADR-0003 / APP-0001) | R-018/R-021 review & lifecycle |
|---|---|---|---|---|---|
| IriusRisk | core | core — OTM author | core | core | adjacent — generated findings and tracker integration documented; review behavior not tested |
| Microsoft TMT | core | limited — `.tm7` only; IriusRisk and Devici import it | adjacent | core | adjacent — status, priority, justification |
| ThreatModeler | adjacent — schema not public | limited — import only | adjacent | adjacent | adjacent — continuous assessment and traceable decisions documented; prior-review preservation not tested |
| SD Elements | adjacent | adjacent — OTM consumer | core | adjacent | core — tracker delivery and verification-tool results per requirement |
| Devici | core | core — OTM import and export with documented contents | adjacent | core | core — accept/mitigate/accepted-risk with audit trail; tracker status sync |
| Tutamantic | limited | unclear | unclear | limited | unclear |
| ThreatTree | core — DFD + linked attack trees | adjacent — **STIX 2.1 export**; JSON; round trip untested | core — L×I register | core | core — audit log, owner, treatment, ticket-driven mitigation state (paid tiers) |
| OWASP Threat Dragon | core | adjacent — imports OTM and TM-BOM | limited | core | adjacent — per-threat status |
| OWASP pytm | core | limited — native JSON load/output only | adjacent — CVSS, likelihood fields | limited | limited |
| Threagile | core | limited — YAML/JSON out only | core — rule-derived risks | limited | core — `risk_tracking` with status, justification, ticket, `checked_by` |
| AWS Threat Composer | core | adjacent — open `.tc.json` schema | limited | core | adjacent — status fields; AI output explicitly a starting point for human refinement |

### Phase-3 applicability axes

Issue #37 also requires applicability on five evidence axes. These ratings describe
the public evidence reviewed, not product quality. **None** means the reviewed
sources provide no evidence; it does not prove the product lacks the capability.

| product | object model | provenance / attribution | human review / audit | federation | AI-grounding |
|---|---|---|---|---|---|
| IriusRisk | core — OTM + rules objects | adjacent — generated findings have rule/KB grounds | adjacent — workflow documented, audit behavior not tested | none — OTM portability is not federated operation | adjacent — AI-assisted starts; grounding detail unverified |
| Microsoft TMT | core — DFD/template/threat objects | limited — template-derived STRIDE only | adjacent — status, priority, justification | none | none |
| ThreatModeler | adjacent — public schema absent | core — vendor says decisions trace through the Secure Design Graph | adjacent — decisions/reports are claimed traceable; behavior not tested | none | adjacent — agents operate on the graph; deterministic/grounded behavior not tested |
| SD Elements | adjacent — requirements-centric | core — knowledge-base and verification-tool traceability | core — tracker and verification status | none | none |
| Devici | core — layered canvas + OTM | core — Codex mapping and per-call MCP audit claims | core — decisions, audit trail and tracker sync | none | adjacent — source inputs named; grounding detail unverified |
| Tutamantic | limited | unclear | unclear | none | unclear |
| ThreatTree | core — DFD/tree/risk objects | adjacent — framework tags and linked objects | core — audit, ownership, treatment | none | none |
| OWASP Threat Dragon | core — published JSON schema | adjacent — methodology and per-threat fields | adjacent — reviewer/status fields, no audit history | none | none |
| OWASP pytm | core — Python classes | core — inspectable rules and source | limited — no native review workflow | none | none |
| Threagile | core — published YAML model | core — rule/risk-tracking fields | core — status, justification, ticket, `checked_by` | none | none |
| AWS Threat Composer | core — published `.tc.json` types | adjacent — reference packs and linked objects | adjacent — status fields, no audit history | none | adjacent — Bedrock drafting is a starter; grounding detail unverified |

## 5. Commercial products

### IriusRisk — rules platform and the author of OTM

IriusRisk models components and data flows on a draw.io-based canvas, supplemented by
questionnaires and templates. Its rules engine generates threats, weaknesses and
countermeasures. The free **Community** edition is limited to three active threat
models, one user and SaaS, and exports only the diagram (XML). **Enterprise** is priced
on request, runs as SaaS or on-premise, and adds issue-tracker integration, the OpenAPI,
and full threat-model export.

Its main value to tmodel is OTM, which IriusRisk created. OTM represents components,
data flows, trust zones, threats, mitigations, risk and layout in JSON or YAML. Because
ADR-0007 commits tmodel to OTM import, IriusRisk is the reference producer to test
against. The specification's latest release is still 0.2.0 (2023-08-30). Its official
integrations page names OWASP ZAP as its only security-testing tool; no SBOM or CVE
scanner is listed.

### Microsoft Threat Modeling Tool — the workshop baseline

TMT is a free Windows application for drawing a DFD (processes, external entities, data
stores, flows, trust boundaries). It generates STRIDE-per-element threats from a
template, and the analysis view records status, priority and justification per threat.
It remains maintained: release 7.3.51110.1 (2025-11-10) added a safeguard against
saving models in the install directory and shipped accessibility fixes. The first draft
said its documentation was last materially updated in 2022; that was wrong.

For tmodel it is the reference for the simplest end-to-end workflow: draw → generate →
triage → report. Its limits are Windows-only delivery, no documented integrations, and
a proprietary `.tm7` format. IriusRisk lists Microsoft TMT among its diagram-tool
integrations and Devici documents TM7 import; these are the only routes found from TMT
models to another tool.

UI reference: [Getting started with the Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started).

### ThreatModeler — broad integrations, no documented export

ThreatModeler builds models from diagrams, code, IaC, documents and live cloud accounts,
and positions this as continuous threat modeling. Its System Mapping, Graph and Reporting
agents operate on a connected Secure Design Graph; the vendor says generated components,
threats, mitigations and decisions remain recorded and traceable. This documents an AI and
audit model, but it was not independently tested and no public graph schema was found.
Its integrations page, re-checked for
#37, names **Terraform, CloudFormation and ARM** (IaC); **GitHub Actions, Azure DevOps,
Jenkins, Jira & Bitbucket and ServiceNow** (DevOps/CI-CD); **AWS, Google Cloud and
Azure** (cloud environments); and **ArmorCode and ServiceNow GRC** (risk and
compliance). No SBOM, CVE or scanner integration and no export format is named. An AWS
Marketplace listing (version 7.4) shows a self-hosted option deployed by CloudFormation
template with usage-based pricing; no public list price was found.

For R-021, continuous re-assessment is the relevant idea. The vendor claims traceable
decisions, but the reviewed sources do not specify how an earlier human verdict is bound
to a regenerated finding when infrastructure changes. That is the question tmodel must
answer itself.

### SD Elements — threat model as requirements production

SD Elements starts from a survey or imported architecture and draws on a knowledge base
to produce threats, weaknesses, countermeasures, developer guidance and compliance
mappings. It runs as SaaS or on-site deployment. Its documentation lists the widest
integration set in the sample: eight issue trackers (Jira, GitHub, GitLab, Azure
DevOps/TFS, Micro Focus ALM, ServiceNow ITSM, Rally, Digital.ai Agility) and around
twenty verification tools, including **OWASP Dependency-Track**, the only SBOM-based
integration found in the commercial sample. A Remote Integration Agent covers on-site
deployments that cannot reach the tracker directly.

For tmodel, SD Elements shows that a mitigation needs more than a `mitigated_by` edge.
It also needs an owner, a linked work item, verification evidence from a tool, and a
status over time (R-021, DEC-009). It consumes OTM 0.2.0 from Devici.

### Devici — collaborative canvas with OTM in and out

Devici (Security Compass) is a diagram-first tool with a free canvas tier and a paid
plan with unlimited users and models. Components get attributes. The maintained
**Codex** maps those attributes to threats and default mitigations across STRIDE,
LINDDUN, MAESTRO, OT/IoT and other frameworks. Drafts can start from a text
description, an imported diagram (**OTM, draw.io, TM7**), or a GitHub repository scanned
by Code Genius, which a GitHub Action re-runs on pull requests.

Two aspects bear directly on R-018. First, threats are reviewed on the canvas
(“reviews, accepts, mitigates, or marks accepted-risk”) with an audit trail of who
decided. Second, the hosted MCP endpoint lets an AI client build and update models, with
every action started by a human prompt and logged per call. Its **OTM export** is the
best-documented one in the sample: elements, dataflows, attributes, threats tagged by
methodology, mitigations, trust boundaries and canvas layout. That makes it a useful
test case for which review fields OTM does *not* carry. Jira and Azure DevOps status
syncs back to the model.
The vendor also documents threat status, workflow states and version history showing how
architecture and risk changed over time. The granularity, exportability and behavior of
that history were not independently tested.

### Tutamantic — diagram reuse with thin public evidence

Tutamantic reuses existing diagrams (draw.io, Visio, Lucidchart, Terraform), asks the
user to add security metadata, and generates threats, mitigations, “threat paths” and
areas of concern. It is sold with training (its “Rapid Threat Model Prototyping”
course) and consulting. The re-check for #37 found no public documentation, prices
(“Inquire Now”), API, export format or named integrations. The site footer reads © 2024
and its latest blog post is dated 2023-11-04. The vendor's performance percentages are
excluded as unsupported marketing.

It remains in the comparison because #37 names it. Its evidence is the weakest in the
sample, and every cell beyond input formats and generated outputs is unverified.

### ThreatTree — linked DFDs, attack trees and a risk register

ThreatTree is a browser product organized as *forests* of DFDs and AND/OR attack trees.
DFD elements are Process, External Entity, Data Store and Trust Boundary, plus 13
infrastructure types. Attack-tree nodes are Goal, OR gate, AND gate and Leaf, and a tree
links to at most one DFD. Threats carry framework tags (STRIDE, LINDDUN, OWASP Top 10,
CAPEC, MITRE ATT&CK). Risk is likelihood × impact on 1–5 scales (1–25, banded
Low/Medium/High/Critical). The register records owner, collaborator, treatment
(Mitigate/Avoid/Transfer/Accept) and mitigation status.

Prices on 2026-10-11: **Free $0** (3 forests, 3 DFDs per forest, 5 trees per DFD),
**Pro $29 per user per month** (compliance mapping, collaboration, audit logs, STIX 2.1
export), **Enterprise by quote** (SSO, custom roles, dedicated/VPC deployment,
integrations). The first draft's “early-adopter” label no longer appears on the page.
JSON export is on every plan and STIX 2.1 on Pro and above.

**Conflicting first-party evidence.** The pricing page lists Microsoft Sentinel and
OneTrust among Enterprise integrations. The Help Center says SIEM is “Splunk only —
Microsoft Sentinel isn't yet supported” and that OneTrust is not supported. This report
follows the Help Center, which is the more specific document, and flags both claims as
contested. Mitigation status is set only by ticket sync: closing a linked Jira,
ServiceNow, Linear or Azure DevOps ticket marks the risk Mitigated, and reopening it
reverts the status.

For tmodel, ThreatTree is the closest precedent for linking architecture to attack
structure (DEC-001) and the only product here that exports STIX 2.1, one of the
ADR-0007 import formats. No account was created to test its export, and a complete
field mapping was not inspected. The Help Center does document the high-level mapping:
STIX `attack-pattern` and `relationship` objects, MITRE ATT&CK `external_references`, and
risk scores in custom `x_threattree_*` properties; a complete field mapping remains untested.

## 6. Open-source products

### OWASP Threat Dragon — approachable DFD tool that now imports OTM and TM-BOM

Threat Dragon is a DFD editor delivered as a web app or as Windows, macOS and Linux
desktop builds. It stores models as JSON (v2 schema) in GitHub, GitHub Enterprise,
GitLab or Bitbucket. Threats attach to diagram cells with type, status, severity, score
and mitigation, and reports render to PDF. The first draft treated TM-BOM only as a
future direction. At the reviewed commit the source contains import paths for both
**OTM** and **TM-BOM**, and the v2.6.2 release notes harden TM-BOM import and merge.
This is source-level evidence; a round trip was not run.

For tmodel it is the approachable-canvas reference under a licence compatible with
A-044. It is also an independent OTM consumer, which makes it a second test target
beside IriusRisk.

### OWASP pytm — threat model as executable Python

pytm models a system as Python objects and generates findings, DFDs, sequence diagrams
and templated reports; `--json` emits the model and the README documents loading its
native JSON. The v1.4.0 notes specifically add `Data` decoding for round-trip
serialization, but no acceptance test was run and this is not a foreign-tool format.
Recent element types `Agent` and `LLM`
extend it to AI systems. Findings carry severity, CVSS, likelihood, mitigations and a
response, but there is no reviewer, verdict or audit history. Licence: **MIT** (see the
correction in §2).

It is the cleanest model-as-code reference, and its findings are deterministic and
diffable. It offers nothing for a graphical review console (R-014/R-015, R-018).

### Threagile — model-as-code with explicit risk tracking

Threagile reads a YAML architecture model (data assets, technical assets, trust
boundaries, shared runtimes, communication links), applies built-in and YAML-scripted
custom risk rules, and writes JSON, PDF, XLSX and diagrams from a CLI, Docker image or
REST server. Its `risk_tracking` block is the most explicit review record among the
open-source tools: status (`unchecked`, `in-discussion`, `accepted`, `in-progress`,
`mitigated`, `false-positive`), justification, ticket, date and `checked_by`.

Activity has slowed. The last release is v0.9.1 (2024-07-30), the last commit was
2026-04-08, and the README says UI efforts are “far from being ready”. Its review-status
vocabulary is directly reusable evidence for R-018. Its maintenance trajectory should be
re-checked before tmodel depends on it.

### AWS Threat Composer — structured authoring with AI as a starting point

Threat Composer structures threats as a grammar (threat source, prerequisites, action,
impact, impacted goals and assets) and links them to assumptions and mitigations, all
stored in a versionable `.tc.json` file whose schema is defined in the source as Zod types. It runs as a
web app with browser storage, in VS Code via the AWS Toolkit, and as a browser extension that renders
`.tc.json` on GitHub, GitLab, Bitbucket and CodeCatalyst. It exports JSON, Markdown,
DOCX and PDF. An AI CLI and an MCP server, both using Amazon Bedrock, generate starter
models from source code. The README says human expertise remains “essential to refine,
validate, and evolve” them.

That framing — AI output as a draft that people must refine — is the closest
open-source match to R-018. Its threat statements do not encode order between threats,
so they do not express attack paths.

## 7. Coverage check — products outside the required set

Phase 4 asked whether the eleven required products miss anything material. An
enumeration was built independently of this report from a community tool list
(`awesome-threat-modelling`), the OWASP Threat Modeling Cheat Sheet (which names methods,
not tools), GitHub, and searches for AI-native entrants. Products are *mentioned*, not
added to the required comparison: #37 fixes the product scope, while this pass records
active, materially distinct candidates and a reasoned follow-up verdict instead of
silently expanding the matrix. STRIDE GPT sharpens the attack-tree finding, Gram the
review-workflow finding, and ThreatAtlas the versioned-review and AI-proposal findings;
none requires expanding the fixed comparison matrix.

| product | kind | verified facts (2026-10-11) | why it matters | verdict |
|---|---|---|---|---|
| STRIDE GPT | OSS, MIT | v0.20.0 (2026-09-26); LLM-generated STRIDE threat models, **attack trees**, DREAD scoring, Gherkin test cases, GitHub repository analysis, Mermaid DFDs | an active open-source AI threat-modeling tool that generates attack trees | mention; candidate for a follow-up spike on AI-proposed attack paths |
| Gram (Klarna) | OSS, Apache-2.0 | collaborative DFD tool; “Review system for use by your Security Champions”; Jira and Okta SSO; tech-stack-based threat/control suggestions | an open-source product with an explicit review workflow | mention |
| OWASP ThreatAtlas | OSS, Apache-2.0, self-hosted | v0.9.0 (2026-09-24); DFDs, formal risk-acceptance approval/rejection with justification, audit log, version comparison including threat/mitigation changes, API/Jira/CI gate, optional AI proposals | active evidence for versioned review and explicit proposal/approval workflows outside the fixed sample | follow-up candidate; persistence semantics and behavior not acceptance-tested |
| CAIRIS | OSS, Apache-2.0 | last release 2.3.9 (2023-02-01); last push 2026-05-09 | security requirements and design platform; long research lineage | mention as low-activity |
| AWS Security Agent threat modeling | commercial, public preview (2026-06-17) | agentic STRIDE threat models from design documents or source; usable from IDEs such as Kiro and Claude Code; no export format named | a hyperscaler AI entrant | mention; re-check at GA |
| Seezo, Prime Security, ThreatCanvas, Aribot, Apiiro | commercial, AI-native | only press or secondary coverage was read | AI design-review wave | **unverified leads**; not described further |
| Threatspec; OWASP threat-model-cookbook | OSS | no push since 2020-12-30; archived | — | excluded (inactive) |

## 8. Competitive feature list (for #15/#18)

The reusable artifact is [`competitive-features.md`](competitive-features.md) (CF-001 to
CF-013). Issue #37 asks for it as a reusable artifact for #15 and #18; earlier drafts
routed the same list to #D1 and #D4, and both routings are kept. These are research
findings, not accepted requirements. The table summarizes them.

| capability | evidence in the sample | tmodel relevance |
|---|---|---|
| Multiple starting points | blank canvas, questionnaire, template, existing diagram, IaC, code, AI draft | reduce blank-page cost without privileging one input |
| Dual authoring | canvas/forms plus text/API/MCP over one model | R-014/R-015 and automation on one model |
| Explicit review state | status vocabularies (Threagile, Threat Dragon, Devici, TMT); owner/treatment (ThreatTree); `checked_by` (Threagile) | minimum review record for R-018; keep proposal and verdict separate |
| Deterministic rules beside AI | Codex/rules/templates next to AI drafts | provenance and reproducibility for machine proposals |
| Model diff and lifecycle | version-controlled files; continuous re-assessment; PR-triggered refresh | R-021: temporal status, not an overwritten snapshot |
| Work-item closure | ticket close → mitigated (ThreatTree); tracker status sync (Devici); verification-tool results (SD Elements) | mitigation needs owner, link, verification evidence |
| Portfolio and focused views | dashboards and registers beside per-element findings | different roles without duplicating facts |
| Open interchange | OTM (IriusRisk, Devici, SD Elements, Threat Dragon), STIX 2.1 export (ThreatTree), TM-BOM (Threat Dragon), `.tc.json` | ADR-0007 import mappings must state what each format loses |
| Reusable knowledge | Codex, templates, packs, custom rules | separate reusable patterns from instance facts (R-030) |
| Evidence-bearing reports | PDF/DOCX/HTML with rationale and status | export is a review artifact, not the canonical graph |
| Attack trees linked to architecture | ThreatTree; STRIDE GPT (generated) | closest precedent for AttackPath; tmodel needs ordering as well as AND/OR |
| AI via MCP with human-initiated actions | Devici MCP; Threat Composer MCP | an agent surface must leave every change attributable and reviewable |
| SBOM/scanner verification integration | SD Elements supports OWASP Dependency-Track; exact CVE-to-mitigation mapping is unverified | test how scanner/SBOM findings supply verification evidence (R-010, R-021) |

## 9. Synthesis and gap analysis

**What the field does well.** Commercial products concentrate on workflow: tracker
delivery, status sync, verification-tool feedback, dashboards and, increasingly, AI
drafting through MCP. Open-source tools concentrate on inspectable artifacts:
versionable JSON/YAML/Python models with published schemas. Both camps document some
review state.

**What the field lacks that tmodel needs.** The gaps below are routed to the decision or
requirement that owns them. Rows routed to accepted decisions are inputs to
implementation, not reasons to reopen them.

| need | best precedent in the sample | gap | routing |
|---|---|---|---|
| ordered, reviewable attack paths | ThreatTree AND/OR trees linked to a DFD; STRIDE GPT generated trees | no product makes an ordered path a first-class, editable, reviewable object | DEC-001 (AttackPath/AttackStep); R-014/R-015 |
| proposal vs verdict | Devici audit trail; Threat Composer “starting point” framing; Threagile `checked_by`; ThreatAtlas explicit AI proposals/approval outside the fixed sample | no fixed-sample product documents the machine proposal and human verdict as separate attributable records; ThreatAtlas may supply a precedent but was not tested | R-018; ARCH-0001 §7 `Review` |
| lifecycle mitigation status | ThreatTree ticket closure; Devici status sync and version history; SD Elements verification results; ThreatAtlas version/risk history outside the fixed sample | vendors document history, but per-version identity, query semantics and export fidelity remain untested | R-021; DEC-009 |
| OTM import fidelity | IriusRisk (author), Devici export contents, Threat Dragon import | no product documents what OTM drops, especially review and provenance fields | ADR-0007 import mapping; R-005 round-trip vector |
| STIX 2.1 import | ThreatTree export | only one producer found; the Help Center gives a high-level mapping, but complete field coverage and round-trip loss were not inspected | ADR-0007 import mapping |
| SBOM/scanner verification | SD Elements + Dependency-Track | exact CVE-to-mitigation mapping is unverified and no comparable integration was documented for the other products | R-010; DEC-008 |
| licence-safe building blocks | Threat Dragon, Threat Composer (Apache-2.0); pytm, Threagile (MIT) | all four required OSS tools are permissive; none supplies a review console | APP-0001 A-044 |
| AI proposals at scale | Devici MCP; Threat Composer and STRIDE GPT generators; AWS Security Agent (preview); ThreatAtlas proposals outside the fixed sample | fixed-sample tools do not document a persistent proposed state; ThreatAtlas documents proposals and approval, but its storage semantics were not inspected | R-018; APP-0001 A-045 |

## 10. Candidate development paths

These are options for later design work, not a selection.

1. **Diagram-first shell over a canonical graph.** Borrow the canvas conventions of TMT,
   Threat Dragon and Devici, but keep facts in the canonical graph (ADR-0004), with layout
   as presentation state.
2. **Model-as-code core plus review console.** Keep deterministic, diffable model files
   in the spirit of Threagile and pytm (consistent with ADR-0004's file source of
   truth) and add the review surface they lack.
3. **Interchange-led prototype.** Import the same small model from IriusRisk/Devici OTM,
   Threat Dragon and ThreatTree STIX 2.1 into the logical graph. Log every field lost or
   invented, and turn the result into the R-005 round-trip vector.

The evidence favors testing path 3 first, because ADR-0007 already commits to the
formats and the loss is unmeasured. This is a recommendation for the next research
step, not a design decision.

## 11. Limits of this evidence

- No product was installed or acceptance-tested; no account was created. Commercial
  entries rest on first-party documentation that may omit limits.
- Pricing and integrations drift. The dates and digests in `sources.md` are part of the
  evidence.
- Tutamantic has the thinnest public technical documentation. ThreatTree's own pages
  contradict each other on two integrations.
- OSS object models were read from source and schema files at the pinned commits, not
  from running the tools.
- The coverage check is one independent enumeration, not an exhaustive market survey.
- Library records for the sources added in this pass were deliberately not created in
  this change (see the next gates).

## 12. Outstanding items

1. **OTM/STIX interoperability testing** remains unverified because no round-trip acceptance 
test was run.
2. **ThreatTree integration conflict** remains flagged because its pricing page and Help Center 
disagree on Sentinel and OneTrust support.
3. **Volatile evidence** such as Threagile maintenance and AWS Security Agent status should be 
re-checked before being used in later design or ADR work.
