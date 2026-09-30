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
| Cyber Kill Chain | an intrusion as seven ordered phases, each a point where defenders can act | linear phase list + courses-of-action matrix | ordered but coarse — phases, not concrete actions; one broken phase stops the attack | manual analysis; phases used as labels in threat-intelligence tooling | no dedicated tooling; used alongside ATT&CK | mature (Lockheed Martin, 2011); very widely known | `lockheed-kill-chain-2011` |
| MITRE ATT&CK | observed adversary behaviour: tactics (why), techniques and sub-techniques (how), procedures, groups, software, mitigations | matrix (tactics × techniques); STIX 2.1 JSON data | concrete steps, but **unordered** — tactics are tags; sequences need Attack Flow | high — machine-readable catalog; mapping a system's threats to techniques still needs people | ATT&CK Navigator, Attack Flow (Apache-2.0); used by many security products | mature (MITRE, 2013–); de-facto industry vocabulary | `mitre-attack`, `mitre-attack-design-philosophy` |
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

## 9. Cyber Kill Chain and MITRE ATT&CK

Unlike STRIDE and attack trees, which are used to analyse a system being
*designed*, these two describe how *real attackers behave*. Both came from
defenders studying real intrusions.

### 9.1 Cyber Kill Chain

**What it is.** A model of an intrusion as seven ordered phases, introduced by
Lockheed Martin (Hutchins, Cloppert & Amin, 2011). The paper's argument is that
conventional defence looks only at vulnerabilities and fails against
persistent, well-resourced adversaries (APTs); defenders should study the
adversary instead.

| # | phase | what the attacker does |
|---|---|---|
| 1 | Reconnaissance | researches and selects the target (e.g. harvests email addresses) |
| 2 | Weaponization | couples an exploit with a backdoor into a deliverable payload |
| 3 | Delivery | transmits it (email attachment, website, USB) |
| 4 | Exploitation | the exploit runs on the victim's system |
| 5 | Installation | installs a backdoor to keep access |
| 6 | Command and Control | the compromised host contacts the attacker |
| 7 | Actions on Objectives | the real goal: steal, destroy, or move further |

**What it models and notation.** The phases of an intrusion, plus a
**courses-of-action matrix**: for each phase, what defenders can do — detect,
deny, disrupt, degrade, deceive, destroy (from US DoD information-operations
doctrine). Indicators seen across intrusions are linked into **campaigns**,
creating an intelligence feedback loop.

**Attack paths / steps.** **Ordered, but coarse.** The adversary must succeed at
every phase, so *one mitigation anywhere breaks the chain*. This is the only
framework so far whose steps have a built-in order — the property ARCH-0001 §3
asks of an `AttackPath`. But a phase is a stage, not a concrete action, and real
intrusions loop back (e.g. reconnaissance again after gaining access).

**Manual vs automatable.** Mostly manual analysis of intrusions; the phases are
widely used as labels in threat-intelligence tools.

**Maturity and adoption.** Mature and very widely known; a standard vocabulary
in security operations and threat intelligence.

**Strengths.** Simple; shows defenders they can stop an attack at any phase, not
only at exploitation; ties detection to a defensive action per phase.

**Limits.** Built for malware-delivered network intrusions by external
attackers — fits insiders, cloud-account abuse, or attacks with no malware
poorly; linear and coarse; a model for analysing intrusions, not a method for
finding threats in a design.

### 9.2 MITRE ATT&CK

**What it is.** A knowledge base of real adversary behaviour, maintained by
MITRE since 2013 and built from observed incidents. Its design rationale is
*MITRE ATT&CK: Design and Philosophy* (Strom et al., 2018, revised 2020).

**What it models.**
- **Tactics** — the adversary's *why*: a tactical objective, e.g. Initial
  Access, Execution, Persistence, Privilege Escalation, Exfiltration.
- **Techniques** and **sub-techniques** — the *how*, e.g. Phishing (T1566) →
  Spearphishing Attachment (T1566.001).
- **Procedures** — how a specific group actually carried out a technique.
- Linked **groups**, **software**, and **mitigations**; three domains:
  Enterprise, Mobile, ICS.

**Notation.** A matrix: tactics as columns, techniques in the cells. Also
published as machine-readable STIX 2.1 JSON (`mitre-attack`), which makes it a
ready graph source (RPT-0011).

**How it relates to STRIDE and the Kill Chain.** The source itself answers this
(Design and Philosophy §4.1.3): high-level models such as the Kill Chain and
STRIDE explain adversary goals but not individual actions or how one action
relates to another; exploit and malware databases are too specific. ATT&CK is
the **mid-level** model between them.

**Attack paths / steps.** **Concrete, but unordered.** Techniques are good
candidates for tmodel's `AttackStep`, but tactics are *tags*, not stages — one
technique can serve several tactics, and ATT&CK does not record the order in
which techniques are used. Sequences need something extra: MITRE's
**Attack Flow** format (Center for Threat-Informed Defense) exists precisely to
describe ordered sequences of ATT&CK techniques, or the Kill Chain's phases can
supply a coarse order.

**Manual vs automatable.** High for the catalog — it is structured data with
stable IDs. Mapping *your* system's threats to techniques still needs people.

**Tooling.**

| tool | what it does | license |
|---|---|---|
| [ATT&CK Navigator](https://github.com/mitre-attack/attack-navigator) | web tool for annotating and colouring the matrix (e.g. coverage, threat profiles) | Apache-2.0 |
| [Attack Flow](https://github.com/center-for-threat-informed-defense/attack-flow) | format and tools for ordered sequences of techniques | Apache-2.0 |
| ATT&CK STIX data | the whole knowledge base as JSON | see `mitre-attack` |

**Maturity and adoption.** Mature and the de-facto industry vocabulary for
adversary behaviour; stated uses are adversary emulation, red teaming,
behavioural-analytics development, defensive gap assessment, SOC maturity
assessment, and threat-intelligence enrichment.

**Strengths.** Evidence-based (observed, not hypothesised); stable IDs; very
detailed; linked to mitigations; machine-readable; shared vocabulary across
tools and teams.

**Limits.** Not a threat-modeling method by itself — no process for analysing a
system under design; covers only behaviour someone has already seen and
reported; no ordering of steps; strongest for enterprise IT; changes with each
release.

### 9.3 Implications for tmodel

Together they cover the two halves of an attack path that neither has alone:
the Kill Chain gives **order** (coarse), ATT&CK gives **concrete steps**
(unordered), and Attack Flow shows one existing way to combine them. This is
input to #15 and DEC-001; **no decision is taken here.**

**Sources.** `lockheed-kill-chain-2011`; `mitre-attack-design-philosophy`;
`mitre-attack`.

## 10. Others found in the search

_Pending._ (e.g. hTMM, Quantitative TM, persona non grata, CVSS-based — only if
sources justify them.) ISO/SAE 21434 TARA is covered by #11; one-line pointer here.

## 11. Implications for tmodel

_Pending._ How the frameworks represent attack steps and paths, and what that
implies for ARCH-0001 §3 (`AttackStep`, `AttackPath`) — framed as inputs to
#15 and DEC-001. **No decision is taken here.**
