---
schema: "archdoc/v1"
id: RPT-0002-searches
title: "RPT-0002 search log"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-30"
record: RPT-0002
---

# RPT-0002 — search log

One row per query or lookup, so coverage is auditable. *Direct* means the
source's own site or PDF was opened by URL (usually found through the SEI
survey's bibliography or a previous hit); *web search* is a general search
engine query; *GitHub* is a repository search or licence check. Before every
ingestion, `library/records/` was searched for an existing record so no source
was ingested twice.

| date | dimension | query / lookup | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-09-28 | all (survey) | SEI library page "Threat Modeling: A Summary of Available Methods" and its PDF | direct (sei.cmu.edu) | `sei-threat-modeling-methods-2018` — backbone survey; its bibliography seeded later lookups |
| 2026-09-28 | STRIDE — tooling | `OWASP/pytm` LICENSE file | GitHub | MIT (+ CAPEC terms); conflicts with RPT-0003's GPL-3.0 |
| 2026-09-29 | attack trees | schneier.com archive page "Attack Trees" (SEI ref [17]) | direct | `schneier-attack-trees-1999` |
| 2026-09-29 | Kill Chain | Lockheed Martin white paper "Intelligence-Driven Computer Network Defense…" | direct (lockheedmartin.com) | `lockheed-kill-chain-2011` |
| 2026-09-29 | ATT&CK | "MITRE ATT&CK: Design and Philosophy" (March 2020 revision) | direct (attack.mitre.org) | `mitre-attack-design-philosophy` |
| 2026-09-29 | ATT&CK — tooling | `mitre-attack/attack-navigator`, `center-for-threat-informed-defense/attack-flow` licences | GitHub | both Apache-2.0 |
| 2026-09-29 | Kill Chain | `Hutchins Cloppert Amin "Intelligence-Driven Computer Network Defense" ICIW 2011 "Leading Issues in Information Warfare"` | web search | venue: *Leading Issues in Information Warfare & Security Research* vol. 1 (2011) |
| 2026-09-29 | attack trees — tooling | `ADTool attack-defense trees tool University of Luxembourg download license` | web search | ADTool page → `tahti/ADTool2` (no licence file, last change 2017) |
| 2026-09-29 | attack trees — tooling | `SeaMonster attack tree misuse case tool SINTEF sourceforge` | web search | SeaMonster (SourceForge; inactive since 2016) |
| 2026-09-29 | attack trees — tooling | `Amenaza SecurITree attack tree software` | web search | SecurITree (commercial) |
| 2026-09-29 | attack trees — tooling | `OWASP Threat Dragon attack tree support` | web search + GitHub | no attack-tree support; feature request issue #607 |
| 2026-09-29 | attack trees — tooling | `IriusRisk attack tree feature threat model` | web search | attack-tree patterns via libraries/templates, no editor |
| 2026-09-29 | PASTA | `"Risk Centric Threat Modeling" UcedaVélez Morana Wiley 2015 ISBN 9780470500965` | web search | book metadata (ISBN, DOI); paywalled → `pasta-risk-centric-threat-modeling` |
| 2026-09-29 | PASTA | OWASP 2012 PASTA slides at the SEI-cited URL | direct | 404 (old owasp.org paths) |
| 2026-09-29 | PASTA | `UcedaVélez "Real World Threat Modeling Using the PASTA Methodology" OWASP AppSec EU 2012 pdf` | web search | wiki.owasp.org copy → `ucedavelez-pasta-owasp-2012` |
| 2026-09-29 | LINDDUN | linddun.org — home, /threat-types/, /methods/ | direct | `linddun-org` (current names; GO/PRO/MAESTRO) |
| 2026-09-29 | LINDDUN | `Deng Wuyts Scandariato Preneel Joosen "A privacy threat analysis framework" Requirements Engineering 2011 doi 10.1007/s00766-010-0115-7` | web search | author manuscript (KU Leuven) → `deng-linddun-2011` |
| 2026-09-29 | LINDDUN — tooling | OWASP Threat Dragon project page — supported methods | direct | lists STRIDE / LINDDUN / CIA / DIE / PLOT4ai |
| 2026-09-29 | OCTAVE | `"Introducing OCTAVE Allegro" CMU/SEI-2007-TR-012 Caralli Stevens Young Wilson pdf` | web search | SEI PDF → `sei-octave-allegro-2007` (timeline contradicts SEI survey) |
| 2026-09-29 | Trike | octotrike.org and the v1 methodology PDF (SEI ref [42]) | direct | HTTP 403 — site refuses automated access |
| 2026-09-29 | Trike | octotrike.org v1 PDF and home page | Internet Archive (Wayback) | archived v1 PDF → `trike-v1-2005` |
| 2026-09-29 | Trike — tooling | `trike threat modeling` | GitHub | `octotrike/trike`, `octotrike/octotrike.github.io`, `Dymaxion00/octotrike` (MIT; dormant) |
| 2026-09-29 | VAST | `VAST threat modeling Agarwal ThreatModeler "Visual, Agile, and Simple Threat" application threat model operational threat model process flow diagram` | web search | vendor page → `threatmodeler-vast`; detailed vendor blog post now 404 |
| 2026-09-29 | other (MAESTRO) | `Cloud Security Alliance MAESTRO agentic AI threat modeling framework Ken Huang 2025 seven layers` | web search | CSA blog → `csa-maestro-2025` |
| 2026-10-22 | Attack Flow | `center-for-threat-informed-defense/attack-flow`: repository metadata and releases (GitHub API) | GitHub | Apache-2.0; tools v4.1.0 and v4.0.0 (2026-10-14), v3.0.0 (2025-07-07) |
| 2026-10-22 | Attack Flow | `docs/language.rst`, `docs/introduction.rst`, `docs/changelog.rst` at tag v4.1.0 | direct (raw.githubusercontent.com) | `mitre-attack-flow` — language spec (digest of `language.rst`); dependency, not order; v4 changes |
| 2026-10-22 | Attack Flow | `stix/attack-flow-schema-2.0.0.json`, `stix/attack-flow-extension-2.0.0.json` at tag v4.1.0 | direct (raw.githubusercontent.com) | object types and properties; `operator` enum `AND`/`OR`; `scope` includes `attack-tree`; extension created 2022-08-02 |
| 2026-10-22 | Attack Flow | language page and `ctid.io/flow` short link | direct | both resolve; the short link opens the Builder (`/attack-flow/ui/`) |
| 2026-10-22 | surveys (peer-reviewed) | research agent: 19 web searches (e.g. `"threat modeling" systematic literature review Computers & Security`, `systematic literature review automated threat modeling tools`, `SoK threat modeling methods`) plus Crossref, OpenAlex and Semantic Scholar lookups | web search + APIs | candidates: Xiong & Lagerström 2019, Tuma et al. 2018, Tatam et al. 2021, Granata & Rak 2024, Huang et al. 2026, Tran et al. 2026; chosen: `tuma-2018-threat-analysis-slr` (open via the thesis reprint), `xiong-2019-threat-modeling-slr` (stub) |
| 2026-10-22 | surveys | Crossref `works/<DOI>` for 10.1016/j.cose.2019.03.010, 10.1016/j.jss.2018.06.073, 10.1016/j.heliyon.2021.e05969, 10.1007/s11219-023-09634-4; Semantic Scholar abstract of Xiong 2019 | API (re-checked by hand) | all four confirmed; Xiong abstract: "most threat modeling work remains to be done manually" |
| 2026-10-22 | surveys | Tuma PhD thesis PDF (University of Gothenburg, 2021), Paper A | direct (research.chalmers.se) | 26 techniques / 38 studies, January 2017 search; the repository stamps each download differently |
| 2026-10-22 | STRIDE — origin | research agent: 17 web searches (e.g. `Kohnfelder Garg "The Threats to Our Products" 1999`, `"Experiences Threat Modeling at Microsoft" Shostack 2008`, `"STRIDE" "adopted by Microsoft in 2002"`) plus Crossref, Library of Congress and Wayback lookups | web search + APIs | `kohnfelder-garg-1999-threats-to-our-products`, `shostack-2008-experiences-threat-modeling-microsoft`, `shostack-threat-modeling-2014` (ISBN 978-1-118-80999-0); "adopted in 2002" found only in SEI 2018 |
| 2026-10-22 | STRIDE — origin | shostack.org copy of the 1999 article; CEUR-WS Vol-413 paper 12; Wiley product page; SEI 2018 PDF text search for "adopted by Microsoft" | direct (re-checked by hand) | digest and byline of the 1999 article confirmed; the 2008 paper names a different 1999 document (Garms, Garg, Howard) |
| 2026-10-22 | comparative evidence | research agent: 24 web searches (e.g. `controlled experiment comparing threat modeling methods STRIDE attack trees empirical evaluation`, `threat modeling practitioners interview study`, `Experimental comparison of attack trees and misuse cases`) plus Crossref, OpenAlex and Semantic Scholar lookups | web search + APIs | Karpati 2014, Opdahl & Sindre 2009, Lallie 2018, Tuma & Scandariato 2018, Mbaka & Tuma 2024, Tuma et al. 2021, Labunets 2013, Stevens 2018, Scandariato 2015, Verreydt 2024 and others |
| 2026-10-22 | comparative evidence | Crossref for 10.1007/s00766-013-0195-2, 10.1142/s0218194023500651, 10.1016/j.infsof.2013.10.004, 10.1109/TIFS.2017.2771238; full texts of Scandariato (Lirias), Verreydt (USENIX), Mbaka & Tuma (arXiv 2208.01524) | API + direct (re-checked by hand) | figures confirmed: 19-24% incorrect / 64-69% overlooked; 13 participants, 7 organizations, no CI/CD integration; 2.5 vs 3.57 threats/hour, 0.40 vs 0.43 precision |

**Coverage notes.**
- Frameworks came from the #6 scope list plus the SEI survey's twelve methods,
  then CSA MAESTRO (found via RPT-0003) for agentic AI.
- Not yet searched: academic evaluations comparing methods beyond SEI (2018);
  original papers for Persona non Grata, hTMM and Quantitative TMM (listed in
  report §10 for later ingestion).
