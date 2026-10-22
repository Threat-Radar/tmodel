---
schema: "archdoc/v1"
id: RPT-0002-sources
title: "RPT-0002 source log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
record: RPT-0002
---

# RPT-0002 — source log

A source is not "in the report" until it is a `library/` record.

| source | type | framework | library record id | bears_on |
|---|---|---|---|---|
| Threat Modeling: A Summary of Available Methods (Shevchenko et al., SEI, 2018) | paper | all (survey of 12) | `sei-threat-modeling-methods-2018` | DEC-001, DEC-005 |
| Attack Trees (Schneier, Dr. Dobb's Journal, 1999) | article | attack trees | `schneier-attack-trees-1999` | DEC-001, DEC-005 |
| Intelligence-Driven Computer Network Defense … Intrusion Kill Chains (Hutchins, Cloppert & Amin, Lockheed Martin, 2011) | paper | Cyber Kill Chain | `lockheed-kill-chain-2011` | DEC-001, DEC-005 |
| MITRE ATT&CK: Design and Philosophy (Strom et al., MITRE, 2018/2020) | paper | MITRE ATT&CK | `mitre-attack-design-philosophy` | DEC-001, DEC-005 |
| MITRE ATT&CK knowledge base + STIX data | dataset | MITRE ATT&CK | `mitre-attack` (existing, from #25) | DEC-001 |
| MulVAL (attack graphs) | paper | attack trees → attack graphs | `mulval` (existing, from #25) | — |
| Agentic AI Threat Modeling Framework: MAESTRO (Huang, Cloud Security Alliance, 2025) | web | MAESTRO (§10) | `csa-maestro-2025` | DEC-001, DEC-005 |
| FIRST CVSS | spec | CVSS (§10) | `first-cvss` (existing) | DEC-003 |
| ISO/SAE 21434:2021 | spec | TARA (§10) | `iso-sae-21434-2021` (existing, #11) | DEC-003, DEC-005 |
| VAST — ThreatModeler product page (vendor) | web | VAST | `threatmodeler-vast` | DEC-005, DEC-006 |
| Trike v.1 Methodology Document [Draft] (Saitta, Larcom & Eddington, 2005) — Internet Archive copy | paper | Trike | `trike-v1-2005` | DEC-001, DEC-003, DEC-005 |
| Introducing OCTAVE Allegro (Caralli, Stevens, Young & Wilson, SEI CMU/SEI-2007-TR-012) | paper | OCTAVE | `sei-octave-allegro-2007` | DEC-001, DEC-003, DEC-005 |
| A privacy threat analysis framework (Deng, Wuyts, Scandariato, Preneel & Joosen, Requirements Engineering, 2011) | paper | LINDDUN | `deng-linddun-2011` | DEC-001, DEC-005 |
| LINDDUN official site (KU Leuven DistriNet) | web | LINDDUN | `linddun-org` | DEC-001, DEC-005 |
| Real World Threat Modeling Using the PASTA Methodology (UcedaVélez, OWASP AppSec EU 2012) | slides | PASTA | `ucedavelez-pasta-owasp-2012` | DEC-001, DEC-003, DEC-005 |
| Risk Centric Threat Modeling (UcedaVélez & Morana, Wiley 2015) — not read, paywalled | book | PASTA | `pasta-risk-centric-threat-modeling` (existing stub, completed) | DEC-001, DEC-003, DEC-005 |
| Attack Flow — Language, STIX 2.1 extension 2.0.0 (MITRE Center for Threat-Informed Defense; docs at release v4.1.0, 2026) | spec | MITRE Attack Flow | `mitre-attack-flow` | DEC-001, DEC-005 |
| Threat analysis of software systems: A systematic literature review (Tuma, Calikli & Scandariato, Journal of Systems and Software 144, 2018) — read via the first author's 2021 thesis | paper | all (survey of 26) | `tuma-2018-threat-analysis-slr` | DEC-001 |
| Threat modeling – A systematic literature review (Xiong & Lagerström, Computers & Security 84, 2019) — paywalled, abstract only | paper | all (survey) | `xiong-2019-threat-modeling-slr` (stub) | DEC-001 |
| The threats to our products (Kohnfelder & Garg, Microsoft, 1999; published by Microsoft 2009) | article | STRIDE | `kohnfelder-garg-1999-threats-to-our-products` | DEC-001 |
| Experiences Threat Modeling at Microsoft (Shostack, MODSEC08, CEUR-WS Vol-413, 2008) | paper | STRIDE | `shostack-2008-experiences-threat-modeling-microsoft` | DEC-001 |
| Threat Modeling: Designing for Security (Shostack, Wiley 2014) — paid book, not read | book | STRIDE | `shostack-threat-modeling-2014` (stub) | DEC-001 |
| A descriptive study of Microsoft's threat modeling technique (Scandariato, Wuyts & Joosen, Requirements Engineering 20, 2015) | paper | STRIDE (evaluation) | `scandariato-2015-stride-descriptive-study` | DEC-001 |
| Threat modeling state of practice in Dutch organizations (Verreydt, Yskout, Sion & Joosen, SOUPS 2024) | paper | practice | `verreydt-2024-threat-modeling-practice` | DEC-001 |
| On the Measures of Success in Replication of Controlled Experiments with STRIDE (Mbaka & Tuma, IJSEKE 34, 2024) — read via the arXiv preprint | paper | STRIDE (evaluation) | `mbaka-tuma-2024-stride-replication` | DEC-001 |
| Comparing attack trees and misuse cases in an industrial setting (Karpati, Redda, Opdahl & Sindre, IST 56, 2014) — paywalled, abstract only | paper | attack trees (evaluation) | `karpati-2014-attack-trees-misuse-cases` (stub) | DEC-001 |
| An Empirical Evaluation of the Effectiveness of Attack Graphs and Fault Trees in Cyber-Attack Perception (Lallie, Debattista & Bal, IEEE TIFS 13, 2018) — paywalled, abstract only | paper | attack graphs (evaluation) | `lallie-2018-attack-graphs-fault-trees` (stub) | DEC-001 |
