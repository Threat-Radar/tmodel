---
schema: "archdoc/v1"
id: DL-0011
title: "RPT-0014 AI threat model: multi-agent search, coverage critique, report review"
type: process
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-03"
record: DL-0011
---

# DL-0011: RPT-0014 AI threat-model research

AI-assisted research record for #71 / #72 (per `CLAUDE.md`).

## Question asked

Deep, PhD-level research on threats and attacks against AI systems, with full
bibliographic references. It covers publications, journals, and news; logs the
major AI security issues in the news; and captures and summarizes papers. The
goal is to extract specific attacks that map to a threat model (company,
assets). It also captures every existing AI threat model for later analysis and
answers whether a CWE-like AI weakness enumeration exists.

## Method

A single workflow (run `wf_aeac1556-700`):

1. **Search**: six parallel dimension agents (ML-model attacks; LLM, RAG, and
   agent attacks; enumerations; published threat models; news incidents; supply
   chain, infrastructure, and AI-enabled offense).
2. **Coverage critique**: a fresh adversarial agent at max effort checks
   technical-paper coverage against top-venue programs and Semantic Scholar
   citation ranks, and spot-checks citations for fabrication.
3. **Gap fill**: two agents close the named gaps and correct or reject suspect
   entries.
4. **Synthesize**: dedupes sources and writes the report plus derived artifacts.
5. **Report review**: two adversarial lenses at max effort, one for threat
   completeness and mapping, one for evidence and citation rigor.
6. **Fold**: applies or rejects each finding.

PDFs go to a local cache outside every repo
(`~/cb/projects/tmodel2026/pdf-cache/ai-threat-model/`); only filenames and
sha256 digests are recorded.

## Results, accepted, rejected

**Run.** The run took 13 agents and about 6.8M subagent tokens. It finished on
2026-10-03, after two pauses when the account hit its usage limit.

**What it produced** (`research/0014-ai-threat-model/`, report v0.2.0):

| file | content |
|---|---|
| `sources.md` | 1,181 deduplicated sources with an annotated technical summary for each; 285 have a cached PDF, with its sha256 |
| `incidents.md` | 179 incidents (all 73 ATLAS case studies included), patterns P1-P11 |
| `threat-models.md` | 127 published AI threat models, methods and frameworks, all marked for detailed analysis (#73) |
| `enumerations.md` | answers whether there is a CWE for AI (CWE 4.20 view 1448 has 4 entries); catalog survey and crosswalk; 16 candidate local weaknesses |
| `attack-catalog.yaml` | 146 attack techniques (AIT-001..146): asset, component, precondition, impact, mitigation, catalog ids, and maturity derived from incidents. Working data, not a schema (#74) |
| `report.md` | the preliminary threat report, including a reference architecture and the asset x attack matrix |

The PDF cache (`~/cb/projects/tmodel2026/pdf-cache/ai-threat-model/`, 283
files, 659 MB) is outside every repo.

**Adversarial rounds:**

1. *Coverage critique* found **58 gaps** and **16 suspect entries**. Its
   verdict: "accurate where it cites, but far from complete", with no
   systematic top-venue sweep and too little non-US work. It checked 484 arXiv
   id/title pairs (483 matched) and 34 CVEs (32 matched; CamoLeak and
   GrafanaGhost were mis-paired). The gap-fill agents swept USENIX Security
   2026, IEEE S&P 2026, SaTML 2026 and CCS 2025 (via Crossref), the ATLAS
   legacy case studies and national guidance. They corrected one arXiv id, two
   CVEs and 39 deprecated ATLAS ids, merged 40 duplicate works, and capped
   confidence on entries that contain details recalled from memory.
2. *Report review* used two lenses at max effort and found **48 findings**
   (2 critical). The critical ones: maturity was inflated (61 of 133
   techniques rated "in the wild", now 38 of 146 on an incident-derived
   scale), and OWASP LLM ids were reused across the 2023 and 2025 editions
   with different meanings.
3. *Fold* applied 41 findings in full and 5 in part, and rejected none
   outright. The partial cases and their reasons are in `report.md` § Review
   log.

**Human spot check (main session, not a subagent).** Six arXiv citations
sampled from `sources.md` were checked against arXiv abstract pages, and all
six matched.

**Rejected / not done, and why.**

- *Zero outright rejections in the fold* is a weak signal, not a strength. An
  AI fold agrees with an AI critic too easily. The human review that ARCH-0001
  R-018 requires has not happened. No AIT entry, mapping or maturity rating is
  accepted.
- *Search coverage is limited.* The session's 200-call WebSearch budget ran out
  early on day one. Later discovery used arXiv, Crossref, Semantic Scholar,
  NVD, CWE and GitHub APIs and known URLs, which biases the corpus toward
  arXiv and toward work the agents already knew. ACM DL and IEEE Xplore full
  text were not reached. News after 2026-08 and non-English sources are
  under-sampled. **Next round:** re-run the paper and news sweeps with a fresh
  search budget, split by venue and year.
- *Primary sources refused automated fetch:* OpenAI, Guardian, BBC, Reuters,
  the Meta framework PDF and the NSA PDF. These need a human fetch.
- *`sources.md` is 2.2 MB*, too large for GitHub's web renderer. Split it when
  the records move into `library/` (#75).

