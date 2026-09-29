---
schema: "archdoc/v1"
id: RPT-0002
title: "Threat model frameworks — methodologies compared"
short_title: "Threat model frameworks"
description: "Survey of threat-modeling frameworks/methodologies (STRIDE, PASTA, attack trees, LINDDUN, OCTAVE, Trike, VAST, kill chain / ATT&CK, …): what each models, how it represents attack paths, and how automatable it is. Evidence for #15 (modeling requirements). It does not select a design."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
authors:
  - role: student
    id: paria03
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0002-threat-model-frameworks/report.md
library_commit: "see library/ submodule pointer at time of merge"
issue: "Threat-Radar/tmodel#6"
informs: [DEC-001, DEC-005]
open_decisions: [DEC-001, DEC-005]
---

# Threat model frameworks

> **This report does not select a design.** It is evidence for the modeling
> requirements (#15). Every `DEC-*` it informs stays open.

Search log: [`searches.md`](searches.md). Source log: [`sources.md`](sources.md).
Axes: [`dimensions.md`](dimensions.md). References live in `library/`.

## 1. Comparison

| framework | what it models | notation | attack path / steps | manual vs automatable | tooling | maturity / adoption | library record |
|---|---|---|---|---|---|---|---|
| STRIDE | six threat categories, each the violation of one security property, applied to system elements | data-flow diagram (DFD) + threat table | weak — finds individual threats per element; chains must be built by hand (or with attack trees) | medium — per-element rules generate candidate threats; realism, impact, mitigation and priority are human | MS Threat Modeling Tool, OWASP Threat Dragon, pytm, IriusRisk, ThreatModeler (see RPT-0003) | most mature method (1999; Microsoft 2002); high adoption in software security | `sei-threat-modeling-methods-2018`, `shostack-threat-modeling-2014` (to ingest) |
| PASTA | | | | | | | `pasta-risk-centric-threat-modeling` |
| Attack trees | an attacker goal decomposed into alternative (OR) and required (AND) sub-goals | tree diagram with AND/OR nodes; one tree per goal | strong — leaves are concrete steps; an attack is a set of leaves that satisfies the root. Basic trees do not order steps (sequential-AND extensions do) | medium — scoring and cheapest-path analysis are computable once values are assigned; building a realistic tree is expert work | ADTool, SecurITree; general diagram tools (see §4) | mature concept (Schneier, 1999); tooling maturity mixed | `sei-threat-modeling-methods-2018`; `schneier-attack-trees-1999` |
| LINDDUN | | | | | | | |
| OCTAVE | | | | | | | |
| Trike | | | | | | | |
| VAST | | | | | | | |
| Kill chain / MITRE ATT&CK | | | | | | | |
| ISO/SAE 21434 TARA | see #11 | | | | | | `iso-sae-21434-2021` |

## 2. STRIDE

**What it is.** A threat-discovery framework: a mnemonic for six categories of
threat, each the violation of one security property. It helps find possible
threats against components, data flows, users, services, and trust boundaries.
Invented in 1999 by Loren Kohnfelder and Praerit Garg (*The Threats to Our
Products*), adopted by Microsoft in 2002, and popularised by Shostack's *Threat
Modeling: Designing for Security* (2014). SEI calls it the most mature
threat-modeling method.

| threat | violates |
|---|---|
| **S**poofing | authentication |
| **T**ampering | integrity |
| **R**epudiation | non-repudiation |
| **I**nformation disclosure | confidentiality |
| **D**enial of service | availability |
| **E**levation of privilege | authorization |

**Notation.** Not a strict graph language — diagrams plus tables. The system is
drawn as a data-flow diagram (external entities, processes, data stores, data
flows, trust boundaries); threats are recorded in a threat table per element.

**How it is applied.** *STRIDE-per-element* checks only the categories that
apply to each element type (e.g. a data store: tampering, information
disclosure, denial of service); *STRIDE-per-interaction* checks each data flow
between elements. The per-element mapping is a rule, which is what lets tools
generate candidate threats from a diagram.

**Attack paths / steps.** Weak to moderate. STRIDE identifies individual threat
types at components and data flows; it has no notion of an ordered sequence of
attacker steps. Chains are added manually, or by pairing STRIDE with attack
trees (§4) — as the hybrid Quantitative Threat Modeling Method does (§10).

**Manual vs automatable.** Medium.
- *Automatable:* parsing architecture diagrams; identifying components and data
  flows; applying STRIDE per element; generating candidate threats from
  templates/rules or AI.
- *Manual:* deciding whether a threat is realistic; business impact; choosing
  mitigations; verifying trust boundaries; priority and risk.

**Tooling.** Tools compared in detail in RPT-0003 (#7); here only their STRIDE role.

| tool | STRIDE role | license | model format |
|---|---|---|---|
| [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) | generates STRIDE threats from a DFD | free, proprietary | own template/model files |
| [OWASP Threat Dragon](https://github.com/OWASP/threat-dragon) | STRIDE (also LINDDUN, CIA) threats on diagrams | Apache-2.0 | JSON |
| [OWASP pytm](https://github.com/OWASP/pytm) | threats generated from a system described in Python code | MIT (its threat catalog reuses CAPEC material under MITRE's terms) | Python code |
| IriusRisk, ThreatModeler | commercial; STRIDE among supported methods | commercial | see RPT-0003 |

**Maturity and adoption.** Mature and widely taught, documented and tool-supported.
Microsoft no longer maintains STRIDE itself, but it is still used in the
Microsoft Security Development Lifecycle through the Threat Modeling Tool.
High adoption in software security: web and cloud application design,
enterprise architecture reviews, secure-SDLC programs, developer training.

**Strengths.** Simple, easy-to-teach acronym; a good checklist for beginners;
works well with DFDs; finds common software threats; supported by many tools;
useful early in design; maps directly onto basic security properties.

**Limits.** The number of threats grows quickly as the system gets more
complex, which makes it time-consuming. An empirical study of Microsoft's
technique (Scandariato et al., cited by SEI) found a moderately low
false-positive rate but a moderately high false-negative rate — it misses real
threats more often than it invents fake ones. Does not model attack chains; no built-in risk scoring, likelihood,
or business impact; can produce many generic threats; depends heavily on diagram
quality; can miss domain-specific threats; not suited on its own to privacy
(→ LINDDUN, §5), safety, hardware, automotive (→ TARA, #11), or agentic AI
(→ MAESTRO, #12).

**Sources.** `sei-threat-modeling-methods-2018`; `shostack-threat-modeling-2014`
(to ingest).

## 3. PASTA

_Pending._

## 4. Attack trees

**What it is.** A method that represents an attacker's **goal** as a tree of the
possible ways to achieve it. If STRIDE is a checklist of what can go wrong,
an attack tree is a map of attacker strategy. Introduced by Bruce Schneier in
1999 (*Dr. Dobb's Journal*); SEI calls it one of the oldest and most widely
applied techniques, used on cyber-only, cyber-physical and physical systems.
Originally a method on its own, it is now often combined with STRIDE, CVSS and
PASTA.

**What it models.** Attacker objectives and the alternative ways to reach them:
attack steps, required sub-steps, dependencies between steps, and — when values
are attached to nodes — cost, difficulty, probability or skill. It asks: *what
does the attacker want, how could they get it, what steps are required, and
where can we block them?*

**Notation.** A tree. The root is the attacker's goal (a bad outcome); child
nodes are ways to achieve their parent; leaves are concrete attack steps. Each
goal gets its own tree, so a system analysis produces a *set* of trees; for
complex systems, trees can be built per component. Two node types:

- **OR** — the attacker needs *any one* child;
- **AND** — the attacker needs *all* children.

```
Goal: steal user data                     (OR)
├── Compromise database                   (AND)
│   ├── Gain internal network access
│   ├── Obtain DB credentials
│   └── Query sensitive table
├── Compromise admin account              (OR)
│   ├── Phish admin
│   └── Steal session cookie
└── Access backups                        (AND)
    ├── Find backup location
    └── Obtain cloud key
```

**Attack paths / steps.** Strong — much stronger than STRIDE for attack-chain
thinking, because it shows how steps relate. Two precise points matter for
tmodel:

- **An attack is a set of leaves, not always a single root-to-leaf path.** Under
  an OR node one leaf can suffice (*phish admin*); under an AND node every child
  is needed, so "compromise the database" is the three leaves together.
- **Basic AND nodes are unordered.** A classic attack tree says *which* steps are
  needed, not *in what order*. Ordered steps need an extension such as
  sequential-AND (SAND) attack trees. ARCH-0001 §3 defines an `AttackPath` as an
  *ordered* set of `AttackStep`s, so this difference has to be handled.

**Manual vs automatable.** Medium; building is manual, analysis is automatable.
- *Manual:* choosing the goal; decomposing it into realistic sub-goals; choosing
  AND/OR; estimating cost, probability, skill, time and impact; choosing
  mitigations; reviewing whether the tree makes sense. SEI notes the method
  assumes high expertise and gives no guidance for assessing sub-goals or risk.
- *Automatable:* candidate trees from known attack catalogs (e.g. MITRE ATT&CK,
  CAPEC); leaves from vulnerability scan results; path cost or risk once values
  are assigned; the cheapest/easiest path; which mitigations block the most paths.

**Tooling.**

| tool | kind | notes |
|---|---|---|
| ADTool | open-source, academic | attack–defence trees (adds countermeasure nodes); _verify license and maintenance_ |
| SecurITree (Amenaza) | commercial | dedicated attack-tree modeling and analysis; _verify_ |
| SeaMonster | open-source, academic | attack trees and misuse cases; _verify whether still maintained_ |
| IriusRisk, ThreatModeler, OWASP Threat Dragon | threat-modeling tools | _verify whether they support attack trees at all_ (see RPT-0003) |
| draw.io, Mermaid, Graphviz, Visio, Miro | general diagramming | common in practice; no AND/OR semantics or scoring |

Questions per tool: AND/OR nodes? node scoring? easiest-path calculation?
export to JSON/XML/YAML? open source? maintained?

**Maturity and adoption.** The concept is mature (over 25 years); tooling
maturity is mixed. Adopted where teams need rigorous reasoning about attacker
behaviour — security architecture, high-assurance, embedded, automotive and
hardware security, risk analysis, and academic research. Less used than STRIDE
by everyday web teams, because trees take more effort.

**Strengths.** Excellent for multi-step attacks; shows alternative paths
clearly; AND/OR captures dependencies; supports quantitative scoring; shows
where a mitigation is most useful — e.g. if three paths all need *obtain admin
credentials*, MFA blocks all three; can reveal the easiest attack; fits
graph-based visualisation; easy for humans to follow.

**Limits.** Trees grow quickly for complex systems; quality depends on expert
knowledge, and paths are missed without domain expertise (SEI: useful only when
the system and its security concerns are well understood); hard to keep current
as the system changes; can over-focus on known goals; scoring is subjective;
needs other models for assets, trust boundaries, vulnerabilities and
mitigations. The **tree shape itself is a limit**: real systems are graph-like,
where one step enables many later ones, so a tree duplicates shared nodes or
hides shared dependencies. *Attack graphs* (e.g. MulVAL, library record
`mulval`) generalise the idea to graphs — relevant because tmodel is a
knowledge graph that could hold attack trees and richer relationships.

**STRIDE vs attack trees.** STRIDE lists *categories of what can go wrong* and is
better for systematic coverage; attack trees show *how an attacker reaches a bad
goal* and are better for attack paths. They are complementary — the
Quantitative Threat Modeling Method builds attack trees for STRIDE categories
and scores them with CVSS (§10).

**Sources.** `sei-threat-modeling-methods-2018`; `schneier-attack-trees-1999`;
`mulval`.

## 5. LINDDUN

_Pending._

## 6. OCTAVE

_Pending._

## 7. Trike

_Pending._

## 8. VAST

_Pending._

## 9. Kill chain and MITRE ATT&CK

_Pending._

## 10. Others found in the search

_Pending._ (e.g. hTMM, Quantitative TM, persona non grata, CVSS-based — only if
sources justify them.) ISO/SAE 21434 TARA is covered by #11; one-line pointer here.

## 11. Implications for tmodel

_Pending._ How the frameworks represent attack steps and paths, and what that
implies for ARCH-0001 §3 (`AttackStep`, `AttackPath`) — framed as inputs to
#15 and DEC-001. **No decision is taken here.**
