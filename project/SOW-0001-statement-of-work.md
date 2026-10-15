---
schema: "archdoc/v1"
id: SOW-0001
title: "Statement of Work — tmodel (CS 490, Fall 2026)"
short_title: "Statement of Work"
description: "Course statement of work: project, capabilities C1–C10, technical approach, testing, milestones, and lane responsibilities. Supersedes the Google Doc draft; defers to the ADRs and PLAN-0001."
type: plan
category: process
status: draft
version: "0.1.0"
version_policy: "semver; MINOR = additive; version and updated move together (ARCH-0001 §9.5)"
date: "2026-10-15"
updated: "2026-10-15"
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: project/SOW-0001-statement-of-work.md
defers_to: PLAN-0001
---

# Statement of Work — tmodel

> **This file supersedes the Google Doc draft** ("Statement of Work — tmodel",
> doc `10X-ydkvu9QVkhTOrjt9AKrhJW7ekI0UJ013Idtiwj7Y`). Edit here, by PR. Per PR #112,
> people are referred to by GitHub handle only (no real names) (see `identities.yaml`).

**Course:** CS 490 Senior Team Project, Fall 2026 · **Team:** @paria03 · @kriishnaa-18 · @Clovier · @Maimcghee ·
**Sponsor:** @nymble (Threat-Radar) · **Faculty advisor:** @paul-haskell ·
**Repository:** https://github.com/Threat-Radar/tmodel (shared reference library https://github.com/Threat-Radar/library)

## 1. What project are we working on?

**tmodel** is a threat-modeling tool for security engineers. Threat modeling — working out how a
product could be attacked, how badly, and what would stop it — is still done largely by hand.
tmodel makes it faster and keeps it current **without removing the human from the loop**:

- The product's parts, weaknesses (MITRE CWE), vulnerabilities (CVE/NVD), attack patterns (CAPEC,
  ATT&CK), threats, attack steps and mitigations are stored as one connected **knowledge graph**.
- The tool can **propose** threats and attack paths, but every proposal is a hypothesis until a
  **human reviews it** — sets the impact, accepts or rejects it, and records why.
- **Risk** is shown as an ISO/SAE 21434 **composite vector** (feasibility, impact, mitigation
  status, derived risk) for a specific product in its environment — not a single opaque score (ADR-0006).
- Generic threats are **mapped onto specific products** of different kinds (software, hardware, systems).

tmodel extends last year's Threat Radar (tradar) scanner: **radar finds** what a product is made
of and what is known-vulnerable; **tmodel models** threats, attack paths, risk and review on top (ADR-0001).

## 2. Capabilities

The **MVP** (ADR-0002) is **a reviewed, grounded attack-path graph** over products from **at least
two domains**, one modeled in depth.

| # | Capability | What it does |
|---|---|---|
| C1 | **Reference library** | Curated, citable library of standards and research (CWE, CVE, ATT&CK, ISO/SAE 21434, NIST, methods, AI-security), each with summary and relevance. *(Record count: unverified — see Threat-Radar/library.)* |
| C2 | **Object model and schema** | LinkML definition of asset, component, weakness, vulnerability, threat, attack step/path, mitigation, review, product and their links. Core accepted (DEC-001a → ADR-0010); governed layer open (DEC-001b). |
| C3 | **Knowledge-graph engine** | Local engine loading library and product data into the working store (Oxigraph, ADR-0008) with a CLI for scripts and AI agents. |
| C4 | **Data import** | radar output, SBOMs, catalogs such as CWE (live vs cached mirror: DEC-008, open); import OTM and STIX 2.1 (ADR-0007). |
| C5 | **Attack paths** | Attack steps with AND/OR logic and explicit order; the engine finds paths reaching an asset. |
| C6 | **Risk metric** | Per **ADR-0006**: a **composite vector shown with its inputs, never collapsed to one number** — attack feasibility by the ISO/SAE 21434 Table-1 method (human-rated at MVP); impact as the 21434 S/F/O/P vector; mitigation status as a peer; derived risk = 21434 risk matrix M(Impact, Feasibility), per threat scenario and impact category; folded across attack paths **worst-path**. Common Criteria values are **display-only**. |
| C7 | **Human review and annotation** | Reviewer sets impact, accepts/rejects, records rationale; every machine-proposed element keeps provenance (ADR-0010 Review/Assertion). |
| C8 | **Desktop application** | Table views and an interactive graph view for exploring/highlighting attack paths. |
| C9 | **Generic → product mapping** | One generic model applied to product instances (software/SBOM, hardware/firmware, systems). Mapping scheme: DEC-009 (open). |
| C10 | **AI threat model research** | Catalog of attacks on AI systems (prompt injection, agent/MCP, poisoning, model theft) — #71, lanes #78–#82. |

**Out of scope for the MVP:** full compliance auditing, cloud hosting or multi-user servers, and new
vulnerability scanning (radar's job). **Mitigation tracking across product families** is not
decided here — its scope follows **DEC-009** (open; PLAN-0001 I4 lists it as post-floor work).

### 2.1 Technical approach

- **Architecture** (ADR-0003, ADR-0009): local, offline macOS desktop app; Tauri (Rust shell) + TypeScript UI;
  Python engine (modeling, import, API, CLI) with the embedded Rust store Oxigraph (RDF/SPARQL, ADR-0008).
- **Data** (ADR-0004, ADR-0007): LinkML schema; import OTM, STIX 2.1; export JSON-LD, Turtle, GraphML, CSV.
  Git files are the source of truth; the store is rebuilt from them.
- **Development:** issues as stories, two-week increments, reviewed PRs, decisions as ADRs
  (`spec/ADR-*`), AI-assisted research and drafting with human review of every result.
- **Deployment:** macOS `.dmg` on GitHub Releases (PLAN-0002 §2 steps 6–7, T-212, #124).
  **Caveat:** signed and notarized downloads are gated on an Apple Developer ID certificate; until
  then releases may be unsigned and build-from-source remains the supported path.

### 2.2 Testing

- Unit tests (pytest engine, vitest UI) in CI on every PR with lint and macOS build (PR #98).
  *(Test counts not stated here; see CI.)*
- Regression vectors with known answers (`spec/vectors/`, e.g. mvp-01/02/03/18).
- Property checks on risk: overall risk is never lower than any single path (worst-path);
  mitigation status never silently lowers risk.
- LinkML validation of model data; validation of library records on change.
- Human review of every AI-proposed threat or research result; second-student cross-check.
- Demo acceptance: load a real product, see threats and paths as a graph, review/annotate a path,
  see the risk vector reflect the review.

## 3. Milestones

Per PLAN-0001 §10–11 (week 1 = Sep 21–27). Nov 5 is the **demo floor**; later milestones are upside.

| # | Milestone | Done when | Date |
|---|---|---|---|
| M1 | **Research** | Core reports drafted by Oct 8 (enough for DEC-005/DEC-003); report work runs **through Oct 13**, overlapping M2 (BACKLOG-0001) | Oct 8 / Oct 13 |
| M2 | **Model and app foundation** | **Already accepted:** DEC-001a (ADR-0010), DEC-002 (ADR-0007), DEC-003 (ADR-0006), DEC-004 (ADR-0008), DEC-010 (ADR-0003 + ADR-0009); walking skeleton with CI merged (PR #98). **Open:** DEC-001b (governed layer), DEC-008 (CWE/NVD), DEC-009 (threat→product / mitigation lifecycle) | Oct 22 |
| M3 | **MVP core — demo floor** | Library in engine; table views; interactive attack-path graph with review/annotation end to end on one worked example | Nov 5 |
| M4 | **Risk and multi-domain** | ADR-0006 risk vector computed; generic threats mapped onto ≥2 domains | Nov 19 |
| M5 | **Integrate and demo** | `.dmg` on GitHub Releases (signing caveat above); docs; vectors green; MVP demo | Dec 5 (early Dec) |

## 4. Responsibilities (by GitHub handle, lane and issue)

| Handle | Lane | Build issues | Research issues |
|---|---|---|---|
| @paria03 | Engine | Walking skeleton (PR #98, merged), attack paths + risk #63, packaging #124 | Methods & agentic threats #36; AI lane agentic-mcp #78 |
| @kriishnaa-18 | GUI | Table views #58, graph view #59 | Products & graph viz #37; AI lane ml-risk-assets #81 |
| @Clovier | Data | Library loader #60, CWE import #61 | Composition/SBOM & ISO 21434 #38; AI lane supply-chain-infra #80 |
| @Maimcghee | Schema & Storage | LinkML schema #64, store façade/export #65 | Formats & AI-security specs #39; AI lane catalogs-schema #79 |
| @nymble (sponsor) | Architecture | Decisions/ADRs (DECISIONS-0001), review, integration; epic #47 | AI lane integration #82 (owner TBD) |
| @paul-haskell (faculty advisor) | — | Course oversight and grading | — |
