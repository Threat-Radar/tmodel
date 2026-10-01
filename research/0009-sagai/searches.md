---
schema: "archdoc/v1"
id: RPT-0009-searches
title: "RPT-0009 search log"
type: research
status: draft
version: "0.2.0"
date: "2026-09-28"
updated: "2026-10-01"
record: RPT-0009
---

# RPT-0009: search log

Every query run, so the survey is reproducible. One row per query.

| date | dimension | query | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-09-28 | 1 | seed: SAGAI CFP (WikiCFP event 177703) | direct fetch | SAGAI 2024 = *Security Architectures for GenAI Systems*, IEEE S&P workshop, May 23 2024; site sites.google.com/view/sagai2024 |
| 2026-09-28 | 1 | `SAGAI workshop "Security Architectures for GenAI Systems" accepted papers IEEE S&P workshops` | web (via Claude Code) | SAGAI'25 site; Fraunhofer "SAGAI" (different series); arXiv 2407.12999 |
| 2026-09-28 | 2 | SAGAI'24 program page | direct fetch | 4 accepted papers; keynotes by Wallace (OpenAI) and Cattell (nbhd.ai) |
| 2026-09-28 | 1, 2 | SAGAI'25 home, program and workshop-format pages | direct fetch | *Secure Generative AI Agents Workshop*, May 15 2025; talks and panels only, no papers; stated output is a joint research-challenges document |
| 2026-09-28 | 2 | `"SAGAI" 2024 IEEE Security and Privacy Workshops SPW Xplore "Spotlighting" OR "User-Provided Specifications" proceedings` | web (via Claude Code) | IEEE SPW 2024 proceedings on IEEE Xplore |
| 2026-09-28 | 2 | `SAGAI'25 workshop research challenges document agentic security Christodorescu Fernandes Jha Mitchell Shams arXiv` | web (via Claude Code) | arXiv 2512.01295; arXiv 2605.18991 |
| 2026-09-28 | 2 | full text of arXiv 2512.01295, 2605.18991, 2407.12999 searched for "SAGAI" | direct fetch (arXiv HTML) | none names SAGAI; 2407.12999 summarizes a separate Oct 2023 workshop by the same organizers |
| 2026-09-28 | 1 | IEEE S&P 2026 workshops page | direct fetch | SAGAI'26 = *Secure Agents for Generative Artificial Intelligence*, May 21 2026; site content not retrievable |
| 2026-09-28 | 1 | Fraunhofer IESE SAGAI page | direct fetch | different series (*Software Architecture and Generative AI*, at ICSA); out of scope |
| 2026-09-28 | 4 | seed: CISA landing page for *Principles for the Secure Integration of AI in OT* | direct fetch | published Dec 3 2025 by 9 agencies; PDF link |
| 2026-09-28 | 4, 5 | CISA PDF, Resources and References sections | read | cites ETSI TC SAI, NCSC/CISA secure AI development guidelines, UK AI Code of Practice, NIST AI RMF, MITRE ATLAS, NSA joint guidance, SBOM documents |
| 2026-09-29 | 2 | arXiv API title search for each SAGAI'24 paper | arXiv API | 3 of 4 found: 2403.14720, 2302.05733, 2212.03334 |
| 2026-09-29 | 2 | `"Defending Language Models Against Image-Based Prompt Attacks via User-Provided Specifications" Sharma Gupta Grossman` | web (via Claude Code) | author PDF (homes.cs.washington.edu/~reshabh/SAGAI.pdf); IEEE Xplore 10579532 |
| 2026-09-29 | 1 | SAGAI'26 program page (sites.google.com/view/sagai-2026/program) | direct fetch | 404, no program published there |

## Tool runs

| date | command | input | result |
|---|---|---|---|
| 2026-09-28 | `pypdf` text extraction + normative-verb count | ETSI EN 304 223 V2.1.1 (16 pages) | 72 provisions; clause 5 (the provisions): 59 shall, 28 should |
| 2026-09-28 | `shasum -a 256` | local ETSI PDF vs download from etsi.org | identical: `1ef542acf1fac7f108aa0b3c8548d91d82395fe026f0036bffe7f1f32456d21a` |
| 2026-09-28 | `pypdf` text extraction + normative-verb count | CISA AI-in-OT PDF, version 508cV2 (25 pages) | 4 principles, 12 subsections; whole document: 40 should, 37 may, 5 must |
| 2026-09-28 | `shasum -a 256` | CISA PDF | `1fde3cbaadf9f75411158a144595631f8dd4029e52b11545c49811d29f531560` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Hines et al., Spotlighting, arXiv 2403.14720v1 (8 pages) | read in full for §2.1; sha256 `8c57c6da480eb46c0deaec1f34dfd98fc75810bd352d4391c6f423430774877d` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Sharma et al., Image-Based Prompt Attacks, author PDF (20 pages) | read for §2.2; sha256 `e315bf3a3488339f9e93c6150e90685387330e26c794be8e4832ec4972a4a1f8` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Kang et al., Programmatic Behavior of LLMs, arXiv 2302.05733v1 (14 pages) | read for §2.3; sha256 `3340777038e9909067f6deed3e1b7a57cd6bb98ff3c9e25148c9512bec601adf` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Liu et al., Pre-trained Encoders, arXiv 2212.03334v1 (33 pages; body and conclusion) | read for §2.4; sha256 `4ca85a38891f99bcc5fe2e86201f7817adeca10cd3b247c5b5fdfe1a4015ec86` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Christodorescu et al., Systems Security Foundations, arXiv 2512.01295v2 (27 pages) | read for §2.5; sha256 `a6afdd4020ac8007ea062fe5c7e6aab1e5200d969a416999282c7a6a63d9d4df` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Christodorescu et al., Agent Security is a Systems Problem, arXiv 2605.18991v2 (18 pages) | read for §2.6; sha256 `eb02d189389663de9e0b4a315ca9f33b07fa1b2e32b23972ea245273134bbadf` |
| 2026-09-30 | `pypdf` text extraction; `shasum -a 256` | Christodorescu et al., Securing the Future of GenAI, arXiv 2407.12999v1 (25 pages; intro, §6–8) | read for §2.7; sha256 `1a6596654e07c708bb09d8b374a1415489fdae72d6e26e689b80a3b3c41020e1` |
| 2026-09-30 | `pypdf` text extraction | CISA AI-in-OT PDF, principles 1–4 | read in full for §4 |
