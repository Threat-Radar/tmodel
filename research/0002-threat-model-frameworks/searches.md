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

**Coverage notes.**
- Frameworks came from the #6 scope list plus the SEI survey's twelve methods,
  then CSA MAESTRO (found via RPT-0003) for agentic AI.
- Not yet searched: academic evaluations comparing methods beyond SEI (2018);
  original papers for Persona non Grata, hTMM and Quantitative TMM (listed in
  report §10 for later ingestion).
