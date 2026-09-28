---
schema: "archdoc/v1"
id: RPT-0003-sources
title: "RPT-0003 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-26"
updated: "2026-09-26"
record: RPT-0003
---

# RPT-0003 — source log

All URLs were resolved on 2026-09-26. **Frontier** means verified and logged
here, but not yet promoted to a complete record in the separate `library`
repository. Issue #7 depends on #P1 for that ingestion; this checkout must not
edit the detached `library/` submodule.

| id | source | kind | status | report use |
|---|---|---|---|---|
| `iriusrisk-create` | [IriusRisk — Creating a threat model](https://www.iriusrisk.com/documentation/creating-a-threat-model) | vendor documentation | frontier | diagram/questionnaire/template/IaC/AI inputs and generated findings |
| `iriusrisk-integrations` | [IriusRisk integrations](https://www.iriusrisk.com/integrations) | vendor documentation | frontier | draw.io/Visio/Lucidchart/TMT, scanners, IaC, API |
| `iriusrisk-otm` | [Open Threat Model specification](https://github.com/iriusrisk/OpenThreatModel) | specification documentation states CC-BY-SA-4.0; `otm_schema.json` separately states Apache-2.0 | frontier | OTM object/interchange model and license distinction |
| `iriusrisk-otm-schema` | [OTM JSON Schema](https://github.com/iriusrisk/OpenThreatModel/blob/main/otm_schema.json) | JSON Schema; embedded comment states Apache-2.0 | frontier | machine-readable OTM fields and schema-specific license |
| `iriusrisk-cli` | [IriusRisk CLI](https://github.com/iriusrisk/iriusrisk-cli) | vendor OSS documentation | frontier | documented OTM import/export and schema validation |
| `ms-tmt-overview` | [Microsoft Threat Modeling Tool overview](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) | product documentation | frontier | STRIDE-per-element and mitigation workflow |
| `ms-tmt-features` | [Microsoft TMT feature overview](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-feature-overview) | product documentation | frontier | design/analysis views, templates, status, reports |
| `threatmodeler-integrations` | [ThreatModeler integrations](https://www.threatmodeler.ai/integrations) | vendor documentation | frontier | IaC, cloud, CI/CD, ticketing, GRC integrations |
| `threatmodeler-mapping` | [ThreatModeler system mapping](https://www.threatmodeler.ai/platform/system-mapping) | vendor documentation | frontier | diagram, code, cloud, document, and IaC ingestion claims |
| `sdelements-datasheet` | [SD Elements threat-modeling datasheet](https://www.securitycompass.com/Datasheets/SD-Elements-Threat-Modeling-Datasheet.pdf) | vendor datasheet | frontier | automated findings, controls, training, verification |
| `sdelements-platform` | [Security Compass platform](https://www.securitycompass.com/platform/) | vendor documentation | frontier | architecture-to-requirements workflow, tracker delivery, traceability claims |
| `devici-product` | [Devici product page](https://www.securitycompass.com/devici/) | vendor documentation | frontier | layered diagrams, AI/MCP, review traceability, OTM handoff |
| `devici-sdelements` | [Devici–SD Elements integration](https://www.securitycompass.com/blog/devici-sd-elements-integration-generally-available/) | vendor release note | frontier | OTM handoff and Jira/GitHub/Azure DevOps delivery |
| `tutamantic-product` | [Tutamantic services](https://www.tutamantic.com/) | vendor documentation | frontier | diagram/IaC ingestion and generated paths/mitigations |
| `threat-dragon` | [OWASP Threat Dragon repository](https://github.com/OWASP/threat-dragon) | OSS repository, Apache-2.0; reviewed `5d6db4f735b0430431a495f4821ccdbe1ec5db8a` | frontier | DFD editor, threats, repository storage, maturity |
| `threat-dragon-release` | [OWASP Threat Dragon releases](https://github.com/OWASP/threat-dragon/releases) | OSS release history | frontier | v2.6.0 activity observation |
| `threat-dragon-guide` | [OWASP Developer Guide — Threat Dragon](https://github.com/OWASP/DevGuide/blob/main/docs/en/04-design/01-threat-modeling/03-threat-dragon.md) | OWASP project documentation | frontier | supported methods, editing flow, desktop/web delivery, PDF reports |
| `threat-dragon-tmf` | [Threat Dragon TMF/TM-BOM note](https://github.com/OWASP/threat-dragon/wiki/Threat-Model-File-%28TMF%29-format) | project documentation | frontier | portability limits and TM-BOM successor |
| `pytm` | [OWASP pytm repository](https://github.com/OWASP/pytm) | OSS repository, GPL-3.0; reviewed `78895796f6c6f6ec3131c28b624c296810fa9797` | frontier | Python object model, generated DFD/sequence/report |
| `threagile` | [Threagile repository](https://github.com/Threagile/threagile) | OSS repository, MIT; reviewed `74e323ed635f026ca85bd61b5082f0da053ba1b2` | frontier | YAML model, rule engine, JSON/PDF/XLSX outputs, REST mode |
| `threat-composer` | [AWS Threat Composer repository](https://github.com/awslabs/threat-composer) | OSS repository, Apache-2.0; reviewed `3d4ed92f96a29605a74795d8df103e068f11ed70` | frontier | structured threats, assumptions, diagrams, AI/CLI/MCP, exports |
| `tm-bom` | [OWASP Threat Model Library / TM-BOM](https://github.com/OWASP/www-project-threat-model-library) | OSS specification/project; reviewed `68640e1447294232f7ab24ceb9527979587f1849` | frontier | emerging neutral JSON interchange |

## Coverage limitations

The OSS revisions above are the upstream `HEAD` values returned by
`git ls-remote` on 2026-09-26. They identify exactly what this pass reviewed;
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
