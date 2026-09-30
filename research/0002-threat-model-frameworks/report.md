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
| PASTA | business risk: threats to an application ranked by business impact, across seven stages | a process; uses DFDs, attack trees, use/abuse cases, CWE/CVSS inside stages | strong — stage 6 builds attack trees and links attacks to vulnerabilities and exploits | low — a heavy, multi-role process; individual stages use automatable inputs (threat intel, scanners, CWE) | no open-source tool found; supported by some commercial platforms (see RPT-0003) | mature (2012; book 2015); moderate adoption, mainly in risk-focused organisations | `ucedavelez-pasta-owasp-2012`, `pasta-risk-centric-threat-modeling`, `sei-threat-modeling-methods-2018` |
| Attack trees | an attacker goal decomposed into alternative (OR) and required (AND) sub-goals | tree diagram with AND/OR nodes; one tree per goal | strong — leaves are concrete steps; an attack is a set of leaves that satisfies the root. Basic trees do not order steps (sequential-AND extensions do) | medium — scoring and cheapest-path analysis are computable once values are assigned; building a realistic tree is expert work | SecurITree (commercial); ADTool, SeaMonster (academic, unmaintained); mostly general diagram tools (see §4) | mature concept (Schneier, 1999); tooling maturity mixed | `sei-threat-modeling-methods-2018`; `schneier-attack-trees-1999` |
| LINDDUN | privacy threats: seven categories mapped onto data-flow-diagram elements | DFD + threat-to-element mapping table + privacy threat trees; GO variant uses cards | moderate — privacy threat trees detail how a threat is realised; no ordered steps | medium — the element mapping is a rule a tool can apply (as for STRIDE); judging privacy impact is human | OWASP Threat Dragon (LINDDUN threats); LINDDUN GO cards | mature (KU Leuven, 2011; actively maintained, renamed categories) | `deng-linddun-2011`, `linddun-org`, `sei-threat-modeling-methods-2018` |
| OCTAVE | organisational risk to critical (information) assets, not a system design | process with worksheets and questionnaires; threat trees classify threat sources | weak — threat trees list actor, means and outcome, not multi-step attacks | low — workshop or worksheet driven; Allegro can be done by one person | worksheets in the SEI reports; no open-source tool found | mature (SEI/CERT: 1999; OCTAVE-S 2005; Allegro 2007) | `sei-octave-allegro-2007`, `sei-threat-modeling-methods-2018` |
| Trike | who may do what to which asset (actor–asset–action matrix); threats are violations of that | matrix + DFDs; attack trees joined into an attack graph | strong — attack trees per threat, merged into one attack graph that can share nodes | high (by design) — threats generated deterministically from the matrix; judging attacks and risk is human | Trike tools (MIT, dormant since 2019) | niche; v1 (2005) documented, v2 never documented; dormant | `trike-v1-2005`, `sei-threat-modeling-methods-2018` |
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

**What it is.** The *Process for Attack Simulation and Threat Analysis*: a
**risk-centric** threat-modeling method created by Tony UcedaVélez (SEI dates it
to 2012), described in full in UcedaVélez & Morana's book (Wiley, 2015). Where
STRIDE asks *what can go wrong*, PASTA asks *which threats matter most to the
business* and works backwards from business objectives to countermeasures. Its
author's argument: pen tests, vulnerability scans and static analysis each give a
partial view; a unifying method should connect them to business impact.

**The seven stages.**

| # | stage | main activities |
|---|---|---|
| 1 | Define objectives | business objectives, security and compliance requirements, business impact analysis |
| 2 | Define technical scope | boundaries of the technical environment; infrastructure, application and software dependencies |
| 3 | Application decomposition | use cases, entry points, actors, assets, trust boundaries, data-flow diagrams |
| 4 | Threat analysis | threat intelligence, security logs and incident data → likely threats |
| 5 | Vulnerability and weakness analysis | existing vulnerability reports; mapping to MITRE CWE/CVE; CVSS/CWSS scoring |
| 6 | Attack modeling | attack surface; **attack trees**; use and abuse cases; attack → vulnerability → exploit mapping |
| 7 | Risk and impact analysis | business impact, residual risk, countermeasures and mitigation strategy |

**Notation.** Not a notation of its own — a process that *uses* other notations
inside its stages: data-flow diagrams (stage 3), attack trees and use/abuse-case
diagrams (stage 6), CWE/CVE enumerations and CVSS scores (stage 5).

**Attack paths / steps.** Strong, through stage 6: attack trees show how attacks
are built, and each attack is linked to the vulnerabilities and exploits it uses.
The author's slides even define an attack tree as the *relationship among
asset, actor, use case, abuse case, vulnerability, exploit and countermeasure* —
close to a graph of tmodel's own object types (ARCH-0001 §3).

**Manual vs automatable.** Low overall. The method is a workshop-heavy process
needing business, architecture, operations and security people (SEI: laborious,
though richly documented). Several *inputs* are automatable — threat-intelligence
feeds, vulnerability scanners, CWE/CVE lookups, CVSS scoring — but tying them to
business impact is human work.

**Risk.** PASTA's distinguishing feature. It ends in business impact and
residual risk, and the author argues risk should include a **probability** term
informed by attack simulation, not only threat × vulnerability × impact — though
the slides do not define how to compute it. Relevant to DEC-003 and #14.

**Tooling.** No open-source PASTA tool found (searched 2026-09-29). Consulting and
tooling are offered by VerSprite (the author's firm), and some commercial
threat-modeling platforms list PASTA among supported methods — see RPT-0003.

**Maturity and adoption.** Mature and well documented (a 2015 book); used mainly
by organisations that want threat modeling tied to risk management. SEI notes it
encourages collaboration across stakeholders and has built-in prioritisation.

**Strengths.** Ties threats to business impact; covers the whole path from
objectives to countermeasures; built-in prioritisation; combines attack trees,
CWE and CVSS rather than replacing them; attacker-centric analysis with
asset-centric output.

**Limits.** Heavy and time-consuming — hard for small teams or fast iterations;
depends on good threat intelligence and on business input; the risk calculation
is not precisely specified in the free sources; examples are web applications;
the primary sources are written by the method's creator, whose firm sells
PASTA services. **The book itself was not read for this report** (paywalled) —
this section rests on the author's 2012 slides and the SEI survey.

**Sources.** `ucedavelez-pasta-owasp-2012`; `pasta-risk-centric-threat-modeling`;
`sei-threat-modeling-methods-2018`.

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

| tool | kind | notes (checked 2026-09-29) |
|---|---|---|
| [ADTool](https://satoss.uni.lu/members/piotr/adtool/) | academic, free (University of Luxembourg, SnT) | attack–defence trees: adds countermeasure nodes, bottom-up evaluation of values. Described by its authors as free and open source, but the [source repo](https://github.com/tahti/ADTool2) has no license file and was last updated in 2017 — effectively unmaintained |
| [SecurITree](https://www.amenaza.com/securitree-main.php) (Amenaza) | commercial | dedicated attack-tree modeling; generates attack scenarios; ships a library of pre-built trees; also fault-tree analysis |
| [SeaMonster](https://sourceforge.net/projects/seamonster/) | open source, academic (SINTEF) | attack trees and misuse cases; project activity ended in 2016 — unmaintained |
| IriusRisk | commercial threat-modeling tool | no attack-tree editor; its documentation describes reproducing repeatable attack-tree patterns as threat libraries and templates |
| OWASP Threat Dragon | open-source threat-modeling tool | no attack-tree support: data-flow diagrams only; threat trees are an open feature request ([issue #607](https://github.com/OWASP/threat-dragon/issues/607)) |
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

**What it is.** A **privacy** threat-modeling framework — the privacy
counterpart to STRIDE. Introduced by Deng, Wuyts, Scandariato, Preneel and
Joosen at KU Leuven (*Requirements Engineering*, 2011) and maintained at
linddun.org by the DistriNet research unit. Like STRIDE, the name is a mnemonic
for its threat categories, and it works over a data-flow diagram.

**The seven threat types** (current names from linddun.org; the 2011 paper and
SEI use older names such as *Linkability*, *Identifiability*, *Detectability*):

| threat | meaning (linddun.org) |
|---|---|
| **L**inking | associating data items or user actions to learn more about someone |
| **I**dentifying | learning someone's identity through leaks, deduction or inference |
| **N**on-repudiation | being able to attribute a claim to an individual |
| **D**etecting | deducing someone's involvement through observation |
| **D**ata disclosure | excessively collecting, storing, processing or sharing personal data |
| **U**nawareness & unintervenability | not informing, involving or empowering people about their data |
| **N**on-compliance | deviating from best practice, standards or legislation |

Note **non-repudiation** is a *threat* here but a security *property* in STRIDE
(where *repudiation* is the threat): for privacy, being unable to deny an action
can itself harm the user.

**What it models.** Privacy threats to personal data in a system. The 2011 paper
separates **hard privacy** (data minimisation — share as little as possible)
from **soft privacy** (the user must trust the organisation holding the data).

**Notation and process.** A data-flow diagram of the system; a **mapping table**
of which threat types apply to which DFD element types; a catalogue of **privacy
threat tree patterns** that detail how each threat can be realised; threats
documented as misuse cases; finally mapped to **privacy-enhancing technologies**
(PETs) as countermeasures.

**Three flavours today** (linddun.org):
- **LINDDUN GO** — a card deck for a lean team brainstorm from informal sketches;
- **LINDDUN PRO** — systematic analysis of interactions between DFD elements
  with threat trees and mapping tables; described as STRIDE-compatible;
- **LINDDUN MAESTRO** — model-driven, using enriched system descriptions; still
  "more info coming soon". *Not* the Cloud Security Alliance's MAESTRO framework
  for agentic AI, which shares the name.

**Attack paths / steps.** Moderate. Threat trees break a privacy threat into the
conditions that realise it (similar to attack trees), but there are no ordered
steps.

**Manual vs automatable.** Medium, like STRIDE: the threat-to-element mapping is
a rule a tool can apply; judging privacy impact and choosing PETs is human.

**Tooling.** [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
lists LINDDUN among its threat categories (Apache-2.0); the LINDDUN GO card deck
is available from linddun.org (no license stated). See RPT-0003 for commercial
tools.

**Maturity and adoption.** Mature (2011) and actively maintained, with an
extensive privacy knowledge base (SEI); the standard reference for privacy
threat modeling.

**Strengths.** Brings privacy into the same DFD workflow as STRIDE; reusable
threat-tree knowledge; direct link from threats to privacy-enhancing
technologies; lighter (GO) and heavier (PRO) options.

**Limits.** Same scaling problem as STRIDE — threats multiply with system size;
labour-intensive, and generic threats reduce efficiency (SEI); privacy only, so
used alongside a security method; category names changed since 2011, so sources
disagree on terms; no license stated for its materials.

**Sources.** `deng-linddun-2011`; `linddun-org`; `sei-threat-modeling-methods-2018`.

## 6. OCTAVE

**What it is.** *Operationally Critical Threat, Asset, and Vulnerability
Evaluation* — a family of **organisational risk assessments** from the CERT
Division of SEI/CMU. It asks: *which information assets matter most to this
organisation, what threatens them, and what would it cost us?* It is a
risk-assessment method more than a design-time threat-modeling method.

**History** (from OCTAVE Allegro's own timeline): OCTAVE Framework 1.0 in
**September 1999**, developed with the US DoD for HIPAA compliance; framework 2.0
in 2001; **OCTAVE-S** for small organisations (v0.9 2003, v1.0 2005);
**OCTAVE Allegro** in 2007. *The SEI survey says OCTAVE was created in 2003 and
refined in 2005 — that appears to confuse it with OCTAVE-S (recorded as a
`contradicts` relation in the library).*

**Three variants.**

| variant | for | approach |
|---|---|---|
| OCTAVE method | large organisations | workshops; three phases: asset-based threat profiles → infrastructure vulnerabilities → security strategy and plans |
| OCTAVE-S | small organisations (20–80 people, per SEI) | a small team with good knowledge of the organisation; fewer workshops |
| OCTAVE Allegro | information assets | eight streamlined steps; can be done by a small team or one person |

**OCTAVE Allegro's eight steps.** (1) establish risk measurement criteria;
(2) profile the information asset; (3) identify its **containers** — where it
lives: technical (servers, laptops), physical (paper, rooms), people;
(4) identify areas of concern; (5) identify threat scenarios using **threat
trees**; (6) identify risks; (7) analyse risks with a **relative risk score**;
(8) select a mitigation approach.

**Notation.** Worksheets and questionnaires, plus four standard **threat
trees** that classify *where a threat comes from*: human actors using technical
means; human actors using physical access; technical problems (defects,
malware); other problems (natural disasters, power or supplier failure).

**Attack paths / steps.** Weak. OCTAVE's threat trees are a classification of
threat *sources* (actor, access, motive, outcome), not multi-step attack paths —
despite the similar name to attack trees.

**Manual vs automatable.** Low: judgement-heavy workshops or worksheets; the
impact criteria are defined by the organisation itself.

**Risk.** Its strength. Impact criteria are set per organisation (reputation,
financial, productivity, safety, legal…), producing a **relative risk score**;
probability is optional because it is hard to quantify. Relevant to DEC-003 and
#14.

**Tooling.** Worksheets, questionnaires and guidance in the SEI reports; no
open-source tool found (searched 2026-09-29).

**Maturity and adoption.** Mature and well known in organisational risk
management and compliance; SEI notes it is designed to be scalable.

**Strengths.** Ties security to business impact and the organisation's own
risk tolerance; covers people and physical threats as well as technical ones;
the "container" idea captures everywhere an asset lives; Allegro makes it
lighter.

**Limits.** Organisational, not system-design — it does not analyse a
software architecture or data flows; no attack paths; qualitative scoring;
time-consuming and, per SEI, large and vague documentation; dated (Allegro is
from 2007).

**Sources.** `sei-octave-allegro-2007`; `sei-threat-modeling-methods-2018`.

## 7. Trike

**What it is.** A formal, automation-oriented threat-modeling method for
security **auditing** from a risk and **defender's** perspective, by Paul
Saitta, Brenda Larcom and Michael Eddington (Trike v1 methodology, 2005, MIT
license). Where STRIDE starts from threat *types*, Trike starts from the
system's **requirements** — what each actor is *supposed* to be able to do — and
treats every deviation from that as a threat.

**How it works (v1).**
1. **Requirements model.** List the actors, the assets, and the intended actions
   on each asset (create, read, update, delete), plus any rules. Summarise them in
   an **actor–asset–action matrix**: rows are actors, columns are assets, and each
   cell says, for each CRUD action, allowed, disallowed, or allowed with rules.
2. **Implementation model.** Data-flow diagrams and "use flows" showing how the
   intended actions are carried out.
3. **Threat generation — automatic.** Threats follow deterministically from the
   matrix and come in only **two kinds**:
   - **denial of service** — an actor is prevented from an intended action;
   - **elevation of privilege** — an actor does something disallowed, breaks an
     action's rules, or uses the system against another system.

   Trike argues that spoofing, tampering and information disclosure are really
   *attacks* or kinds of elevation of privilege — a direct critique of STRIDE.
4. **Attacks.** Each threat is the root of an **attack tree**; the trees are
   joined into one **attack graph**. Weaknesses, vulnerabilities and mitigations
   are then identified, and reusable **attack libraries** kept.
5. **Risk model.** Asset values, actor risk ratings and action probabilities on
   five-point scales.

**Notation.** The actor–asset–action matrix, data-flow diagrams, and attack
trees/graph.

**Attack paths / steps.** Strong. Trike is the only framework in this report
whose v1 explicitly merges attack trees into an **attack graph**, where one attack
step can serve several threats — the limitation of plain trees noted in §4. Its
separation of **threat** (a business-rule event, never technology-specific) from
**attack** (a technology-specific step) is also a precise distinction.

**Manual vs automatable.** High by design: once the matrix exists, threat
generation is mechanical. Building the matrix, finding attacks and judging risk
remain human work.

**Tooling.** The Trike tool (v2, Smalltalk, [GitHub](https://github.com/octotrike/trike))
and an older Python port ([GitHub](https://github.com/Dymaxion00/octotrike)), both
MIT-licensed and unchanged since 2019 and 2015. The project site
(octotrike.org) refuses automated access; the v1 document was read from the
Internet Archive.

**Maturity and adoption.** Niche and dormant. Versions 1.5 (which drops threat
trees) and 2 (with "attack chaining") exist, but v2 was never documented; the
site still says it is under active development, yet its repository last changed
in 2019. SEI calls its documentation vague and insufficient.

**Strengths.** Formal and repeatable; threats come from the system's own access
rules, so coverage is systematic; automatic threat generation; attack graph
rather than isolated trees; clear threat/attack/weakness/vulnerability/mitigation
vocabulary; defender's perspective.

**Limits.** Draft-quality, partly experimental documentation with no worked
example; v2 undocumented and the project dormant; only two threat categories
may feel coarse in practice; SEI finds its five-point risk scales too vague for a
formal method; the actor–asset–action matrix grows quickly for large systems.

**Relevance to tmodel.** Trike v1's model — actor, asset, action, rule, threat,
attack, attack tree/graph, weakness, vulnerability, mitigation, attack library —
is very close to ARCH-0001 §3's object types, and it shows threats generated *by
rule* from a model. Worth reading in full for #15. **No decision is taken here.**

**Sources.** `trike-v1-2005`; `sei-threat-modeling-methods-2018`.

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
