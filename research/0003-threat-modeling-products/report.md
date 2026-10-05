---
schema: "archdoc/v1"
id: RPT-0003
title: "Threat Modeling Products — commercial and open source"
short_title: "Threat-modeling products"
description: "Evidence-first comparison of commercial and open-source threat-modeling products, their interaction models, interoperability, workflow integration, and reusable feature requirements."
type: research
category: security
status: draft
version: "0.2.0"
date: "2026-09-26"
updated: "2026-10-04"
authors:
  - role: research
    id: kriishnaa-18
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0003-threat-modeling-products/report.md
library_commit: "pending #P1 ingestion; verified frontier sources are logged in sources.md"
informs: [DEC-001, DEC-002, DEC-003, DEC-005, DEC-006, R-014, R-015, R-018, R-021]
open_decisions: [DEC-001, DEC-002, DEC-003, DEC-005, DEC-006]
issue: 7
---

# Threat Modeling Products — commercial and open source

> **First draft. Evidence, not decisions.** Every `DEC-*` remains open. Product
> claims below mean “documented by the product owner,” not “independently
> verified.” Sources are logged in [`sources.md`](sources.md), queries and
> exclusions in [`searches.md`](searches.md), and comparison axes in
> [`dimensions.md`](dimensions.md).

## Comparison table

Claim notes: “Documented” or “vendor-documented” means the capability is supported by first-party product documentation. “Researcher inference” means the conclusion was drawn from the available evidence rather than explicitly stated by the product. “Unclear” means the reviewed sources did not confirm the capability. None of the products were acceptance-tested.
Maturity reflects the product/project status observed on 2026-09-26 and does not guarantee future maintenance or support.
ThreatTree status was observed on 2026-10-04 and was not acceptance-tested.

| product | pricing / delivery | features | integrations | model portability | UI / interaction model | maturity |
|---|---|---|---|---|---|---|
| IriusRisk | commercial cloud/enterprise product | component/data-flow modeling; security rules generate threats, weaknesses, and suggested countermeasures; templates and AI-assisted starts | Jira, Azure DevOps, ServiceNow, security scanners, Terraform, CloudFormation, draw.io, Visio, Lucidchart, and Microsoft TMT | OTM JSON/YAML import/export; documented API | diagram canvas, questionnaires, and templates | active enterprise product with current documentation, API support, and ongoing product updates |
| Microsoft TMT | free Windows desktop application | Create DFDs; automatically generates STRIDE threats; supports mitigations, threat priority, status, justification, and reusable templates | OneDrive sharing and community templates; CI, issue-tracker, and scanner integrations not clearly documented | local model and template files; HTML report export | drag-and-drop DFD with separate design and analysis views | GA lineage since 2018; reviewed documentation last materially updated in 2022 |
| ThreatModeler Nexus | commercial enterprise product | Automated threat analysis; continuous cloud/IaC assessment; supports frameworks such as STRIDE and VAST | GitHub, Jenkins, Azure DevOps, Jira, ServiceNow, Terraform, CloudFormation, ARM, cloud platforms, and GRC tooling | Imports architecture and IaC formats; API available; cross-tool export is unclear | Builds threat models from diagrams, code/IaC, documents, and cloud architecture | active 2026 product surface |
| SD Elements | commercial SaaS or on-premises platform | Generates threats, weaknesses, countermeasures, developer guidance, and compliance mappings; supports tracking and verification | Jira, GitHub, GitLab, Azure DevOps, and security-testing tools | Supports OTM transfer from Devici; broader threat-model export is unclear | surveys, generated requirements, diagrams, and portfolio dashboards | active 2026 enterprise platform |
| Devici | commercial product | layered architecture modeling; vendor-documented STRIDE, LINDDUN, and MAESTRO proposals; editable threats and mitigations; AI-assisted modeling | GitHub/code scanning, AI clients through MCP, and SD Elements delivery to Jira, GitHub, and Azure DevOps | supports OTM transfer to SD Elements; broader cross-tool export is unclear | Collaborative layered diagram canvas with AI/MCP interaction | active 2026 product integrated into Security Compass |
| Tutamantic | commercial cloud service | Generates threats, mitigations, attack paths, and areas of concern from existing security/architecture designs | CI/CD integration is mentioned, but specific supported tools are not clearly documented | imports draw.io, Visio, Lucidchart, IaC, and infrastructure schemas; neutral export unclear | reuse and enrich existing diagrams or infrastructure schemas | active service site; public technical detail is limited |
| ThreatTree | commercial browser-based product; Free $0, Pro $29/user/month early-adopter pricing, Enterprise quote; dedicated/VPC deployment is an Enterprise option | DFDs with trust boundaries and architecture elements; AND/OR attack trees linked to DFD nodes; framework tagging; likelihood × impact scoring and ranked risk register; mitigations/control mappings; team collaboration and audit logs on paid plans | Enterprise integrations include two-way Jira, ServiceNow, Linear, and Azure DevOps ticketing; Splunk feed; Vanta/Drata sync; Confluence/Notion embeds; OpenAPI, CloudFormation, and Terraform import | JSON export on all plans; STIX 2.1 export on Pro+; PDF exports; Enterprise DFD import from OpenAPI, CloudFormation, and Terraform; cross-tool round trip was not tested | browser DFD editor, attack-tree editor, risk register, and reports | active official product, help, and pricing documentation observed 2026-10-04; no official public source repository was identified; not independently tested |
| OWASP Threat Dragon | Free and open source (Apache-2.0): web, desktop, or self-hosted | DFD modeling; suggested and manually added threats; mitigations; multiple threat categories; PDF reports | GitHub, GitLab, and Bitbucket model storage; no broad CI or issue-tracker layer documented | text-based tool JSON; TMF is tool-specific; TM-BOM is the stated successor direction | DFD canvas, threat forms, and report view | OWASP Production project; v2.6.0 released in 2026; exact reviewed revision logged in `sources.md` |
| OWASP pytm | Free and Open Source (GPL-3.0): Python CLI/library | Python object model; rule-based threat generation; generated DFD and sequence diagrams | Can fit into version-control and CI workflows; no built-in issue-tracker integration is clearly documented | Python model source plus generated diagrams and reports; cross-tool round-trip support is unclear | model-as-code in Python with generated visual/report outputs | established OWASP project; exact reviewed revision logged in `sources.md` |
| Threagile | Free and Open Source (MIT): Go CLI, container, or server | architecture/assets in YAML; standard and custom risk rules; explicit risk tracking; generated diagrams and risk reports | version-control/CI compatibility is a researcher inference from YAML/container operation; tracker integrations not documented | YAML input; JSON, PDF, XLSX, and diagram outputs; REST server; neutral round trip not established | model-as-code with generated diagrams/reports; project states its UI is limited | maintained repository at the exact revision logged in `sources.md` |
| AWS Threat Composer | Free and Open Source (Apache-2.0): web, IDE, or self-hosted | structured threat grammar; architecture/DFD modeling; assumptions, mitigations, reusable packs, and quality insights; AI creates human-refined starter models | VS Code/AWS Toolkit, browser extension, Git hosting, and experimental AI CLI/MCP | versionable `.tc.json`; JSON, Markdown, DOCX, and PDF exports | web/IDE editor with diagrams, structured forms, and insights dashboard | active repository with exact reviewed revision logged in `sources.md` |

## Why this report

Threat Radar needs a threat model that can represent threats, attack paths, system context, risk, and human review. 
Existing threat-modeling products approach these needs in different ways, including diagrams, questionnaires, 
model-as-code, AI-assisted modeling, and workflow integrations.
This report compares these products to identify useful features and interaction patterns that may help inform Threat 
Radar’s requirements. The goal is not to choose a “best” product, but to understand what existing tools offer, how portable 
their models are, and what still needs further testing.

## Applicability to tmodel

This applies the rubric in [`dimensions.md`](dimensions.md). Core means the product provides strong evidence for 
that area; adjacent means the evidence is useful but incomplete; limited means there is little useful evidence; 
and unclear means the reviewed sources do not confirm the capability. These ratings describe how useful each product 
is as research evidence for tmodel, not the overall quality of the product. None of the products were acceptance-tested.

| product | DEC-001 object model | DEC-002 interchange | DEC-003 risk | DEC-006 UI | R-018/R-021 review/lifecycle |
|---|---|---|---|---|---|
| IriusRisk | core | core | core | core | adjacent — generated findings and integrations are documented, but full human-review and lifecycle behavior was not tested |
| Microsoft TMT | core | limited — no standard cross-tool round trip established | adjacent | core | adjacent — status, priority, and justification are documented; lifecycle traceability is limited |
| ThreatModeler Nexus | adjacent — public schema detail is limited | limited — imports/API claims, neutral export unclear | adjacent | core | adjacent — continuous assessment informs lifecycle needs; but human-review behavior is not clearly documented |
| SD Elements | adjacent | adjacent — OTM handoff through Devici; broader cross-tool exchange is unclear | core | adjacent | core — work-item delivery and verification workflows are documented |
| Devici | core | adjacent — OTM handoff documented; broader cross-tool exchange is unclear | adjacent | core | core — editable threats/mitigations and downstream traceability are documented |
| Tutamantic | adjacent | limited | adjacent | adjacent | unclear — public sources do not clearly describe human-review or lifecycle tracking |
| ThreatTree | core — DFD and attack-tree object structures are documented | adjacent — JSON/STIX exports and architecture imports are documented, but round trip was not tested | core — likelihood × impact scoring and a ranked risk register are documented | core — linked DFD, attack-tree, risk-register, and report views are documented | core — collaboration, audit logs, ownership/treatment fields, and ticket-driven mitigation status are documented on paid tiers; not acceptance-tested |
| OWASP Threat Dragon | core | limited — tool-specific JSON; TM-BOM is a direction | adjacent | core | adjacent — manual threat/mitigation editing is documented; lifecycle traceability is limited |
| OWASP pytm | core | limited — executable Python and generated outputs, no neutral round trip | adjacent | limited | limited — no native review/lifecycle model is documented |
| Threagile | core | adjacent — structured YAML/JSON outputs, neutral round trip not established | core | limited | adjacent — explicit risk tracking exists; graphical review/lifecycle support is limited |
| AWS Threat Composer | core | adjacent — versionable tool JSON and report exports | adjacent | core | core — assumptions, mitigations, human refinement, and living-model workflow are documented |

## Commercial approaches

### IriusRisk — rules platform with a documented open interchange format

IriusRisk is a commercial threat-modeling platform that uses diagrams, questionnaires, templates, architecture/IaC imports,
and AI assistance. Its rules engine can generate threats, weaknesses, and countermeasures based on the system components and 
data flows.

One of its most useful features for tmodel is the Open Threat Model (OTM) format. OTM uses JSON/YAML to represent components, 
data flows, trust zones, threats, mitigations, risk values, and layout information. This makes IriusRisk a useful example when considering how tmodel should store and exchange threat-model data, especially for DEC-002 and DEC-006. However, OTM is still maintained by a vendor and its schema is still in a 0.x version. A round-trip test would be needed before deciding whether it is a good interchange format for tmodel.

Demo / UI reference: IriusRisk product walkthrough video — https://www.youtube.com/watch?v=1JazWthGhr4

### Microsoft Threat Modeling Tool — a legible workshop baseline

Microsoft TMT is a free Windows threat-modeling tool that uses a diagram-first approach. Users create a DFD with processes, 
external entities, data stores, data flows, and trust boundaries. The tool then uses STRIDE-based templates to generate threats.
TMT has separate design and analysis views. In the analysis view, users can review threats and set fields such as status, 
priority, and justification. It can also generate HTML reports.

For tmodel, Microsoft TMT is a useful example of a simple workflow: design the system → generate threats → review and 
mitigate them → create a report. Its main limitations are that it is Windows-only, relies heavily on its own files/templates, 
and does not clearly support an open cross-tool interchange format or a modern CI/API workflow.

UI reference: Threat Modeling Process pictures - https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started 

### ThreatModeler Nexus — broad automation, limited public portability evidence

ThreatModeler Nexus is a commercial threat-modeling platform that can build models from diagrams, code, IaC, and live cloud environments. It also connects with CI/CD tools, issue trackers, cloud platforms, and GRC tools.

A key idea is continuous threat modeling. Instead of treating the threat model as a one-time workshop result, the model can 
be updated as the system or cloud environment changes. This is useful for tmodel’s R-021 lifecycle requirement, although the 
reviewed sources do not clearly show how previous human reviews are preserved when the system changes.

The public documentation also does not clearly describe a standard open export format or detailed object schema. This means ThreatModeler has strong workflow and integration support, but its model portability is less clear.

### SD Elements — threat model as a requirements-production system

SD Elements is a commercial platform that starts from surveys or imported architecture and uses a security knowledge base 
to generate threats, weaknesses, countermeasures, developer guidance, and compliance mappings. It also connects the threat model 
to development workflows by sending security work into issue trackers and using testing 
tools to help verify whether controls have been implemented.

For tmodel, SD Elements is useful because it shows that a mitigation may need more than just a simple mitigated_by relationship. 
It may also need information such as an implementation owner, linked work item, verification evidence, and lifecycle status.
SD Elements also supports an OTM-based handoff from Devici, which provides a useful example to examine for DEC-002 interchange.

### Devici — collaborative canvas and AI proposal surface

Devici is a commercial threat-modeling platform that uses layered architecture diagrams and supports methods such as STRIDE, 
LINDDUN, and MAESTRO. It also supports AI-assisted modeling through MCP and can create models from code or other artifacts.
An important idea for tmodel is that the AI-generated content stays inside the same editable threat model that humans review. 
Threats and mitigations can still be changed instead of being produced only as a separate text report.
Devici can also transfer threat-model information to SD Elements using OTM. This is useful for DEC-002 interchange, although 
it is still unclear whether every review and provenance field is preserved during the transfer.

### Tutamantic — diagram reuse with thin public evidence

Tutamantic is a commercial threat-modeling service that can use existing diagrams and IaC instead of requiring users to redraw 
the system from scratch. It can enrich those designs with security information and generate threats, mitigations, attack paths, 
and areas of concern.

For tmodel, this is useful because it shows how existing architecture files, such as Visio or draw.io diagrams, could be reused
as inputs to a threat model. However, Tutamantic has limited public technical documentation. The reviewed sources do not clearly explain its object schema, API, review-state model, or export format, so it provides less evidence for tmodel’s design decisions 
than some of the other products.

### ThreatTree — linked DFD, attack-tree, and risk-register workflow

ThreatTree is a commercial browser-based threat-modeling product with Free, Pro, and Enterprise plans. Its official documentation describes a forest that contains Data Flow Diagrams and Attack Trees. DFDs represent processes, data stores, trust boundaries, external entities, and data flows. Attack Trees use AND/OR logic to decompose a goal into atomic attack steps and can link back to the DFD node they target. ThreatTree supports framework tags, likelihood × impact scoring, mitigations and treatment information, standards-based control mappings, and a ranked risk register.

The documented interface includes DFD and Attack Tree editors, a risk-register view, and PDF reports. JSON export is available on all plans, while Pro and Enterprise add STIX 2.1 export. Enterprise documentation describes DFD imports from OpenAPI, CloudFormation, and Terraform, plus integrations with ticketing, SIEM, GRC, and documentation systems. In particular, its ticketing documentation says closing or reopening a linked ticket changes the risk's mitigation state in ThreatTree.

For tmodel, ThreatTree provides directly relevant evidence for linking architecture elements to ordered or branching attack steps, for risk prioritization, and for tracking mitigation through external work items. Its collaboration, audit, and ticket-sync features also provide evidence for R-018/R-021 review and lifecycle requirements. These are first-party documented capabilities only: the product was not acceptance-tested, cross-tool round trips were not verified, and no official public source repository was identified during this pass.

## Open-source approaches

### OWASP Threat Dragon — accessible diagram-first collaboration

OWASP Threat Dragon is a free, open-source threat-modeling tool available for web and desktop use. It uses DFDs and lets users 
add or review threats, mitigations, and different threat categories. It also supports repository-backed storage and PDF reports.

For tmodel, Threat Dragon is useful as an example of an approachable visual threat-modeling interface. Its model data is stored 
in JSON, but that does not automatically make it portable to other tools. The project notes incompatibility with formats used by 
pytm, Threagile, and OTM, while TM-BOM is being explored as a future direction.

### OWASP pytm — threat model as executable Python

OWASP pytm is a free, open-source Python-based threat-modeling tool. Users define system elements and data flows as Python 
objects, and the tool can generate DFDs, sequence diagrams, applicable threats, and reports. Because the threat model is written 
as code, it can fit naturally with source-control and CI workflows, although this is an inference from its code-based design 
rather than a clearly documented built-in integration.

For tmodel, pytm is useful as an example of model-as-code and rule-based threat generation. Its main limitation is that it does 
not provide the graphical human-review experience needed for actions such as accepting, rejecting, or re-scoring threats under requirements like R-018.

### Threagile — a well-documented model-as-code pipeline precedent

Threagile is a free, open-source threat-modeling tool that represents system architecture in YAML. It supports built-in and 
custom risk rules, tracks risks, and can generate outputs such as JSON, PDF, XLSX, and diagrams. It can run through a CLI, 
container, or REST server, which makes it suitable for automated and CI-based workflows. However, its graphical UI is still limited.

For tmodel, Threagile is a useful example of model-as-code and repeatable automated analysis. At the same time, tmodel should 
avoid relying only on YAML because human reviewers also need an easier graphical way to inspect and review threats.

### AWS Threat Composer — structured authoring plus cautious AI assistance

AWS Threat Composer is a free, open-source threat-modeling tool that supports architecture/DFD diagrams, structured threat descriptions, assumptions, mitigations, reusable packs, and quality insights. Its models can be stored in versionable .tc.json 
files and exported into several report formats. It also supports VS Code, Git-based workflows, and experimental AI tools through 
CLI/MCP.

For tmodel, one of the most useful ideas is that AI-generated threat models are treated as a starting point that still requires 
human review and refinement. This closely matches tmodel’s R-018 requirement that machine-generated content should not be 
considered final until a human reviews it.

## Competitive feature list for #D1 / #D4

The authoritative reusable artifact is
[`competitive-features.md`](competitive-features.md). The table below summarizes the main 
capabilities identified across the reviewed products. These are research findings, 
not accepted tmodel requirements.

| capability | reviewed-sample evidence | tmodel relevance |
|---|---|---|
| Multiple starts | blank canvas, questionnaire, template, existing diagram, IaC, code, or AI draft | reduce blank-page cost without privileging one input source |
| Dual authoring | diagram/form for workshops plus text/API for automation | R-014/R-015 and developer workflow must operate on one model |
| Explicit review state | priority, status, justification, decision, assignee, linked work-item history | evaluate a minimum UI for R-018; retain proposal and verdict separately |
| Deterministic rules beside AI | STRIDE/knowledge-base/custom rules remain inspectable | evaluate reproducible grounds and provenance for AI suggestions |
| Model diff and lifecycle | version control, drift refresh, incremental releases | R-021 requires temporal status, not an overwritten snapshot |
| Work-item closure | Jira/GitHub/ADO/ServiceNow assignment and bidirectional status | mitigation needs ownership, implementation, and verification evidence |
| Portfolio and focused views | dashboard/report plus per-element findings | support executives, security reviewers, and developers without duplicating facts |
| Open interchange | OTM, TM-BOM, tool JSON/YAML, APIs | DEC-002 must test semantic round trip, including review/provenance and layout |
| Reusable knowledge | templates, threat/control packs, custom rules | separate reusable patterns from product-instance facts |
| Evidence-bearing reports | diagrams, rationale, unresolved findings, control status | export is a review artifact, not a substitute for the canonical graph |

## Synthesis and gap analysis

The reviewed products show two general patterns. Commercial tools focus more on collaboration, 
integrations, ticketing, dashboards, and workflow automation. Open-source tools focus more on 
inspectable models, versionable files, deterministic rules, and local execution.

Across the reviewed products, there is still limited evidence of a single graph-based model that 
also preserves AI proposals, human review decisions, lifecycle state, and portable threat-model data. 
The table below summarizes these gaps and connects them to existing tmodel decisions and requirements.

| need | reviewed precedent | unresolved gap → routing |
|---|---|---|
| approachable modeling | TMT / Threat Dragon / Devici canvas | graph/path editing across multiple views → **DEC-006, #10** |
| automation-ready source | Threagile YAML / pytm Python / APIs | one encoding that also serves non-developer reviewers → **DEC-002** |
| portable model | OTM and emerging TM-BOM | test round-trip loss for review, provenance, ordered paths, and layout → **DEC-002** |
| AI-assisted start | IriusRisk / Devici / Threat Composer | record prompt/source/derivation and keep proposal distinct from acceptance → **R-018, DEC-004** |
| lifecycle traceability | ThreatModeler drift / SD Elements work items | per-product, per-version mitigation evidence → **R-021, DEC-009** |
| risk prioritization | product rules and configurable scores | environment-specific impact with explainable calculation → **DEC-003** |
| reusable content | product libraries and packs | open, attributable threat/control library → **R-030** |
| graph-native attack paths | Tutamantic claims path generation; most tools remain DFD/finding-centric | path derivation, ordering, branching, and human correction remain a tmodel differentiator → **DEC-001, #10** |

## Candidate development paths

1. **Diagram-first shell over a canonical graph.** Use a familiar visual interface like
 Microsoft TMT or Threat Dragon, while keeping the underlying threat-model data in one
  structured graph. It is still an open question whether diagram layout information should
   be stored as part of the main model.
2. **Model-as-code core plus review console.** Takes deterministic CI and diffs
   from Threagile/pytm, while adding the visual review surface they lack.
3. **Interchange-led prototype.** Import OTM and TM-BOM into the logical graph,
   then measure loss on export before selecting DEC-002.

One hypothesis for later design review is to combine paths 2 and 3 behind a
diagram/review shell. This report does not select that path.

## Next review gates

- Human review of matrix fairness and whether the feature list matches #D1/#D4.
- Complete #P1 library ingestion. Exact reviewed revisions are logged in
  `sources.md`, but the durable library records and pins remain outstanding.
- Run the same small model through Threat Dragon, Threagile, and Threat Composer;
  attempt OTM/TM-BOM conversion and log every lost field.
- Revisit commercial entries with demonstrations or trial evidence before using
  undocumented behavior in an ADR.
