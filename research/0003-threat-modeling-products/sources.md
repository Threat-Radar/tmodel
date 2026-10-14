---
schema: "archdoc/v1"
id: RPT-0003-sources
title: "RPT-0003 source log"
type: research
status: draft
version: "0.3.2"
date: "2026-09-26"
updated: "2026-10-12"
record: RPT-0003
---

# RPT-0003 — source log

All URLs were resolved on 2026-09-26. **Frontier** means verified and logged
here, but not yet promoted to a complete record in the separate `library`
repository. Issue #7 depends on #P1 for that ingestion; this checkout must not
edit the detached `library/` submodule.

ThreatTree sources were resolved on 2026-10-04 and remain frontier sources pending #P1 ingestion.

The #37 deepening pass re-resolved sources and added new ones on 2026-10-11. Rows marked
**(re-checked 2026-10-11)** were re-fetched in that pass; rows without the mark carry
2026-09-26/2026-10-04 evidence only. Vendor pages drift, so the SHA-256 of the fetched
bytes is recorded for the pages that carry load-bearing pricing or integration claims.

| id | source | kind | status | report use |
|---|---|---|---|---|
| `iriusrisk-create` | [IriusRisk — Creating a threat model](https://www.iriusrisk.com/documentation/creating-a-threat-model) | vendor documentation | frontier | diagram/questionnaire/template/IaC/AI inputs and generated findings |
| `iriusrisk-integrations` | [IriusRisk integrations](https://www.iriusrisk.com/integrations) | vendor documentation | frontier | draw.io/Visio/Lucidchart/TMT, scanners, IaC, API |
| `iriusrisk-otm` | [Open Threat Model specification](https://github.com/iriusrisk/OpenThreatModel) | specification documentation states CC-BY-SA-4.0; `otm_schema.json` separately states Apache-2.0 | frontier | OTM object/interchange model and license distinction |
| `iriusrisk-otm-schema` | [OTM JSON Schema](https://github.com/iriusrisk/OpenThreatModel/blob/main/otm_schema.json) | JSON Schema; embedded comment states Apache-2.0 | frontier | machine-readable OTM fields and schema-specific license |
| `iriusrisk-cli` | [IriusRisk CLI](https://github.com/iriusrisk/iriusrisk-cli) | vendor OSS documentation | frontier | documented OTM import/export and schema validation |
| `ms-tmt-overview` | [Microsoft Threat Modeling Tool overview](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) | product documentation | frontier | STRIDE-per-element and mitigation workflow |
| `ms-tmt-features` | [Microsoft TMT feature overview](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-feature-overview) | product documentation | frontier | design/analysis views, templates, status, reports |
| `threatmodeler-integrations` | [ThreatModeler integrations](https://www.threatmodeler.ai/integrations) | vendor documentation (re-checked 2026-10-11; SHA-256 `f67490e5db1a712d…38a203`) | frontier | named integrations: Terraform, CloudFormation, ARM; GitHub Actions, Azure DevOps, Jenkins, Jira & Bitbucket, ServiceNow; AWS, GCP, Azure; ArmorCode, ServiceNow GRC; no export format named |
| `threatmodeler-mapping` | [ThreatModeler system mapping](https://www.threatmodeler.ai/platform/system-mapping) | vendor documentation (re-checked 2026-10-12) | frontier | System Mapping Agent ingests diagram, code, cloud, document and IaC sources into the Secure Design Graph |
| `threatmodeler-platform` | [ThreatModeler Nexus platform](https://www.threatmodeler.ai/platform) | vendor documentation (2026-10-12) | frontier | System Mapping, Graph and Reporting agents; MCP/CI workflow; vendor claims deterministic governance and traceability |
| `threatmodeler-graph` | [ThreatModeler Secure Design Graph](https://www.threatmodeler.ai/platform/secure-design-graph) | vendor documentation (2026-10-12) | frontier | connected architecture/threat/control graph; recorded and traceable security decisions |
| `sdelements-datasheet` | [SD Elements threat-modeling datasheet](https://www.securitycompass.com/Datasheets/SD-Elements-Threat-Modeling-Datasheet.pdf) | vendor datasheet | frontier | automated findings, controls, training, verification |
| `sdelements-platform` | [Security Compass platform](https://www.securitycompass.com/platform/) | vendor documentation | frontier | architecture-to-requirements workflow, tracker delivery, traceability claims |
| `devici-product` | [Devici product page](https://www.securitycompass.com/devici/) | vendor documentation (re-checked 2026-10-12) | frontier | free canvas tier; OTM/draw.io/TM7 import; Jira/Azure DevOps status sync; audit trail; threat/workflow status and version history; hosted MCP; Code Genius GitHub Action |
| `devici-sdelements` | [Devici–SD Elements integration](https://www.securitycompass.com/blog/devici-sd-elements-integration-generally-available/) | vendor release note | frontier | OTM handoff and Jira/GitHub/Azure DevOps delivery |
| `tutamantic-product` | [Tutamantic services](https://www.tutamantic.com/) | vendor documentation (re-checked 2026-10-11; SHA-256 `960f5c3f6609ad49…7d552d`; footer © 2024) | frontier | drawio/Terraform/Visio/Lucidchart reuse; generated threats, mitigations, threat paths; no named integrations, prices, API or export format |
| `threattree-product` | [ThreatTree product site](https://threattree.com/) | vendor product documentation | frontier | DFDs, linked AND/OR attack trees, framework tags, risk scoring/register, controls, collaboration, JSON/STIX/PDF exports |
| `threattree-help` | [ThreatTree Help Center](https://threattree.com/app/help) | vendor technical documentation (re-checked 2026-10-12; earlier digest `77a46232a51ab2af…ce97a6`) | frontier | object/interaction model; attack-tree-to-DFD links; review/treatment; STIX 2.1 high-level mapping; audit and integration details |
| `threattree-pricing` | [ThreatTree Plans & Pricing](https://threattree.com/app/membership) | vendor pricing documentation (re-checked 2026-10-11; page `Last-Modified` 2026-10-11; SHA-256 `9ce58422c511f8fa…26cb8e`) | frontier | Free $0, Pro $29/user/mo, Enterprise quote; no “early adopter” wording on 2026-10-11; lists Sentinel and OneTrust, which the Help Center contradicts |
| `threat-dragon` | [OWASP Threat Dragon repository](https://github.com/OWASP/threat-dragon) | OSS repository, Apache-2.0; re-reviewed `1753ad0fae42d65c56e754fa8faf8fb57179f9f5` (re-checked 2026-10-11; earlier pass `5d6db4f735b0430431a495f4821ccdbe1ec5db8a`) | frontier | DFD editor, threats, repository storage, maturity |
| `threat-dragon-release` | [OWASP Threat Dragon releases](https://github.com/OWASP/threat-dragon/releases) | OSS release history (re-checked 2026-10-11) | frontier | latest release v2.6.2 (2026-05-10); v2.6.2 notes harden TM-BOM import/merge |
| `threat-dragon-guide` | [OWASP Developer Guide — Threat Dragon](https://github.com/OWASP/DevGuide/blob/main/docs/en/04-design/01-threat-modeling/03-threat-dragon.md) | OWASP project documentation | frontier | supported methods, editing flow, desktop/web delivery, PDF reports |
| `threat-dragon-tmf` | [Threat Dragon TMF/TM-BOM note](https://github.com/OWASP/threat-dragon/wiki/Threat-Model-File-%28TMF%29-format) | project documentation | frontier | portability limits and TM-BOM successor |
| `pytm` | [OWASP pytm repository](https://github.com/OWASP/pytm) | OSS repository, **MIT** (corrected 2026-10-11: `LICENSE` and `pyproject.toml` state MIT, and `LICENSE` was already MIT at the previously reviewed `78895796f6c6f6ec3131c28b624c296810fa9797`); re-reviewed `381dea05c58055ba218e632510dd3a327d2bf215` (re-checked 2026-10-12) | frontier | Python object model, generated DFD/sequence/report, native JSON output/load |
| `pytm-v1-4-0` | [pytm v1.4.0 release](https://github.com/OWASP/pytm/releases/tag/v1.4.0) | OSS release notes (2026-07-06) | frontier | `Data` decoding enables round-trip serialization; native pytm JSON only |
| `threagile` | [Threagile repository](https://github.com/Threagile/threagile) | OSS repository, MIT; reviewed `74e323ed635f026ca85bd61b5082f0da053ba1b2` (still `HEAD` on 2026-10-11) | frontier | YAML model, rule engine, JSON/PDF/XLSX outputs, REST mode |
| `threat-composer` | [AWS Threat Composer repository](https://github.com/awslabs/threat-composer) | OSS repository, Apache-2.0; re-reviewed `4ae9bda22d75165c461c3c396c204603db2a092e` (re-checked 2026-10-11; earlier pass `3d4ed92f96a29605a74795d8df103e068f11ed70`) | frontier | structured threats, assumptions, diagrams, AI/CLI/MCP, exports |
| `tm-bom` | [OWASP Threat Model Library / TM-BOM](https://github.com/OWASP/www-project-threat-model-library) | OSS specification/project; reviewed `68640e1447294232f7ab24ceb9527979587f1849` | frontier | emerging neutral JSON interchange |
| `iriusrisk-plans` | [IriusRisk plans](https://www.iriusrisk.com/plans) | vendor pricing documentation (2026-10-11) | frontier | Community edition free, 3 active threat models, one user, SaaS, XML diagram export; Enterprise price on request, SaaS or on-premise, issue trackers, OpenAPI |
| `ms-tmt-releases` | [Microsoft TMT release notes](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-releases) | product release notes (page updated 2025-12-10) | frontier | latest GA 7.3.51110.1 (2025-11-10); Windows 10+, .NET 4.7.1; free ClickOnce download |
| `ms-tmt-7-3-51110` | [Microsoft TMT 7.3.51110.1 release](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-releases-73511101) | product release notes | frontier | file-location safeguard for `.tm7`/`.tb7`, bug and accessibility fixes |
| `threatmodeler-aws-marketplace` | [ThreatModeler on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-vdjencmrr5vak) | marketplace listing (2026-10-11) | frontier | listing version 7.4; delivered as a CloudFormation template; usage-based pricing (per-dimension figures not used) |
| `sde-issue-trackers` | [SD Elements issue-tracker supported tools](https://docs.sdelements.com/master/guide/docs/integrations/issue_tracker_integration/supported_tools/) | vendor documentation (2026-10-11) | frontier | Jira, GitHub, GitLab, Azure DevOps/TFS, Micro Focus ALM, ServiceNow ITSM, Rally, Digital.ai Agility; Remote Integration Agent for on-site deployments |
| `sde-security-tools` | [SD Elements verification-tool supported tools](https://docs.sdelements.com/master/guide/docs/integrations/security_tools/supported_tools/) | vendor documentation (2026-10-11) | frontier | HCL AppScan family, Checkmarx, Coverity, Fortify, Klocwork, ThreadFix, Veracode, WhiteHat, OWASP Dependency-Check/-Track, SonarQube, Nessus, Prisma Cloud, Black Duck, Snyk, GitLab Ultimate |
| `sde-faq-deployment` | [SD Elements FAQ — on-site deployment vs SaaS](https://docs.sdelements.com/release/5.14/guide/docs/faq) | vendor documentation | frontier | both on-site deployment (OSD) and SaaS are documented |
| `sde-devici-otm` | [SD Elements — Exporting an OTM from Devici](https://docs.sdelements.com/master/guide/docs/import_from_devici/exporting_otm_from_devici.html) | vendor documentation (2026-10-11) | frontier | OTM 0.2.0 from canvas Export or REST `format=otm`; carries elements, dataflows, attributes, threats, mitigations, trust boundaries, layout, methodology metadata |
| `threat-dragon-otm-code` | [Threat Dragon OTM migration code](https://github.com/OWASP/threat-dragon/tree/1753ad0fae42d65c56e754fa8faf8fb57179f9f5/td.vue/src/service/migration/otm) | source inspection | frontier | OTM import path (`migration/otm`) and TM-BOM path (`migration/tmBom`) present at the reviewed revision |
| `threat-dragon-v2-schema` | [Threat Dragon v2 JSON Schema](https://github.com/OWASP/threat-dragon/blob/1753ad0fae42d65c56e754fa8faf8fb57179f9f5/td.vue/src/assets/schema/threat-dragon-v2.schema.json) | source inspection | frontier | object model: summary, diagrams, cells (shape, data, source/target), per-cell threats with status/severity/score/mitigation |
| `pytm-source` | [pytm package source](https://github.com/OWASP/pytm/tree/381dea05c58055ba218e632510dd3a327d2bf215/pytm) | source inspection | frontier | classes TM, Element, Actor, Asset, Process, SetOfProcesses, Datastore, Lambda, Server, ExternalEntity, Agent, LLM, Boundary, Dataflow, Data, Threat, Finding, Assumption, Controls; v1.4.0 (2026-07-06) |
| `threagile-model-source` | [Threagile input model](https://github.com/Threagile/threagile/blob/74e323ed635f026ca85bd61b5082f0da053ba1b2/pkg/input/model.go) | source inspection | frontier | data assets, technical assets, trust boundaries, shared runtimes, communication links, custom risk categories, risk tracking (status, justification, ticket, date, checked_by) |
| `threat-composer-types` | [Threat Composer data-exchange types](https://github.com/awslabs/threat-composer/blob/4ae9bda22d75165c461c3c396c204603db2a092e/packages/threat-composer/src/customTypes/dataExchange.ts) | source inspection | frontier | `.tc.json` schema: applicationInfo, architecture, dataflow, assumptions, mitigations, threats, assumption/mitigation links, brainstorm; threat and mitigation status fields |
| `otm-repo-2026` | [OpenThreatModel repository](https://github.com/iriusrisk/OpenThreatModel) | specification repository (re-checked 2026-10-11) | frontier | latest release 0.2.0 (2023-08-30); `HEAD` `c88c5a7b4115f0f025e28d5682a2b0d790b389e4` (2025-12-11) |
| `stride-gpt` | [STRIDE GPT repository](https://github.com/mrwadams/stride-gpt) | OSS repository, MIT (2026-10-11) | frontier | coverage check: LLM-generated STRIDE threat models, attack trees, DREAD, Gherkin tests; v0.20.0 (2026-09-26) |
| `gram` | [Gram repository](https://github.com/klarna-incubator/gram) | OSS repository, Apache-2.0 (2026-10-11) | frontier | coverage check: collaborative DFD threat modeling with a review system, Jira and SSO integrations |
| `cairis` | [CAIRIS repository](https://github.com/cairis-platform/cairis) | OSS repository, Apache-2.0 (2026-10-11) | frontier | coverage check: security requirements and design platform; last release 2.3.9 (2023-02-01), pushed 2026-05-09 |
| `aws-security-agent-tm` | [AWS Security Agent threat modeling (What's New)](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-security-agent-threat-modeling/) | vendor announcement (2026-06-17) | frontier | coverage check: agentic STRIDE threat models from design documents or source; public preview; no export format named |
| `awesome-threat-modelling` | [awesome-threat-modelling list](https://github.com/hysnsec/awesome-threat-modelling) | community list (secondary) | frontier | independent tool enumeration for the coverage check only; no capability claims taken from it |
| `owasp-threat-modeling-cheat-sheet` | [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) | OWASP first-party guidance | frontier | independent coverage enumeration and method context only; it names methods, not products |
| `owasp-threatatlas` | [OWASP ThreatAtlas](https://owasp.org/projects/threatatlas) | OWASP project page; Apache-2.0 (2026-10-12) | frontier | coverage check: self-hosted team DFD application with approvals, history, API/Jira/CI gate and optional AI |
| `owasp-threatatlas-changelog` | [ThreatAtlas changelog](https://github.com/OWASP/www-project-threatatlas/blob/main/CHANGELOG.md) | first-party release history (2026-10-12) | frontier | v0.9.0 (2026-09-24); AI proposals, formal risk acceptance, audit log, threat/mitigation version diffs and residual-risk history |

## Coverage limitations

The OSS revisions above are pinned upstream commits captured on the review or
re-check date stated in each row. They identify exactly what that pass reviewed;
they do not replace validated `library/` records.

- Commercial entries rely primarily on first-party documentation and were not
  independently exercised; undocumented limits may exist.
- Product editions and integrations change. The observation date is part of the
  evidence, and later report revisions must re-check them.
- Complete bibliographic records remain outstanding in `Threat-Radar/library`
  under the #P1 workflow. Exact upstream revisions were captured here, but they
  are not durable library pins until #P1 creates and validates the records.
- The OpenThreatModel repository itself was reviewed at
  `c88c5a7b4115f0f025e28d5682a2b0d790b389e4`; its documentation license and
  schema-file license are intentionally recorded separately above.
