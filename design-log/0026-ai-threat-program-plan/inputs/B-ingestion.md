# B. Ingestion and sources strategy for RPT-0014 round 2

Thread B of the RPT-0014 round-2 plan (issue #71). Written 2026-10-26. Read-only
survey of `tmodel@449f515` and `library@6d9a51f`. External facts were probed live
today; the probe results are in §2.9.

## 0. Where we are (baseline the plan has to move)

| Item | State 2026-10-26 |
|---|---|
| `sources.md` | 1,181 sources: 812 tier-1 and 369 tier-2. 675 papers, 121 vendor research, 55 surveys, 54 threat models, 51 frameworks, 48 catalogs, 46 advisories, 42 datasets, 38 standards, 33 news, 17 tools. By year: 2026 276, 2025 331, 2024 241, 2023 108, and **2016-2022 only 196** (the classic canon is thin). Confidence: 736 high, 422 medium, 23 low. 705 unique arXiv ids, about 300 DOIs. |
| Gaps | `round1-critic-gaps.json` lists 58 named gaps and 16 suspect entries. The biggest ones: USENIX Sec 2026 (about 70 AI papers on the program, 2 held), SaTML (4 of the top 50 held), CCS 2025 and S&P 2026, pre-2023 canon, non-US national guidance, and news after 2026-08. |
| Library | 566 records, of which roughly 15 are AI-relevant. **0 RPT-0014 WAVE-1 records merged.** |
| Lanes | 1 of 5 lanes finished calibration (agentic-mcp, commit `c6cd1e0`, 3 records). The supply-chain lane was re-cut into issues #134-#136 on 2026-10-21. The other lanes have no output after about 3 weeks. |
| Social | X, Bluesky, Mastodon, HN and Reddit were **never searched** in round 1: `searches.md` has no hits for them. |

The plan below treats round 1 as a **seed corpus**, not as ground truth. Its
recall is measured against external frames (§1), not against itself.

---

## 1. Coverage model: what "good coverage" means and how to measure it

Coverage is measured on **six independent axes**. Each axis has a
script-generated CSV under `research/0014-ai-threat-model/coverage/`. These are
generated files that are never hand-edited, the same rule as `index/`. Each axis
has a numeric target. Round 2 **passes** when every axis meets its target in two
consecutive weekly runs **and** a blind adversarial critic (§1.7) finds fewer
than the stated threshold of new must-haves.

### 1.1 Venue-year recall (academic breadth)

**Frame.** Take the full table of contents (TOC) for each venue-year. Run a
two-stage in-scope classifier over every title and abstract:

1. A keyword prefilter: a recall-oriented regex for adversarial, poison,
   backdoor, jailbreak, prompt injection, membership, extraction, watermark,
   LLM, agent, model, federated, deepfake and similar terms.
2. An LLM triage with label `in|adjacent|out` and a one-line reason.

A human spot-checks 5% of each label, plus every `adjacent`. The **denominator**
is `in`. The **numerator** is items held as at least a `stub` library record.

| Venue set | Years | Target recall of `in` | Why |
|---|---|---|---|
| IEEE S&P, USENIX Security, ACM CCS, NDSS | 2016-2026 | **≥ 95%** (≥ 98% for 2024-2026) | Top-4 security venues; the sponsor's "professional grade" bar |
| IEEE SaTML | 2023-2026 | **≥ 95%** | Dedicated venue; currently about 8% recall |
| ACM AISec, DLSP/SPW, EuroS&P, AsiaCCS, ACSAC, RAID, ESORICS | 2019-2026 | ≥ 80% | Second tier, heavy on attack papers |
| NeurIPS, ICML, ICLR (main), plus the NeurIPS D&B track | 2018-2026 | ≥ 90% of `in` papers with ≥ 50 citations, or orals and spotlights; ≥ 60% of all `in` | Volume is too high for a full sweep, so stratify by impact |
| ACL, EMNLP, NAACL, plus Findings | 2020-2026 | Same rule as NeurIPS etc. | Jailbreak and prompt-injection lineage |
| CVPR, ICCV, ECCV | 2017-2026 | ≥ 90% of `in` with ≥ 100 citations | Physical and patch attacks, AV and biometrics |
| arXiv cs.CR ∪ cs.LG ∪ cs.CL ∪ cs.AI ∪ cs.CV ∪ cs.MA ∪ cs.SE ∪ cs.RO ∪ eess.AS (keyword-filtered) | rolling 2025-09 → now | 100% of items triaged; held = `in` with any of: ≥ 10 citations, a top-venue acceptance, a code release with ≥ 50 stars, or a catalog citation | Cannot hold everything (about 50 prompt-injection papers a month) |

**Output.** `coverage/venue-year.csv` with columns `venue, year, toc_n, in_n, held_n, recall, missing_ids`.

**Getting the TOCs.** On 2026-10-26 the DBLP search API (`https://dblp.org/search/publ/api`) returns an **Anubis bot challenge (HTTP 202)** to scripted clients from every mirror (dblp.org, dblp.uni-trier.de, dblp.dagstuhl.de). Options in order:

1. The monthly DBLP XML dump, `https://dblp.org/xml/dblp.xml.gz` (1.1 GB, HTTP 200), parsed locally by `crossref`/`booktitle` key (`conf/uss/uss2025`, `conf/sp/...`, `conf/ccs/...`, `conf/ndss/...`). Releases are at `https://dblp.org/xml/release/`.
2. OpenAlex `works?filter=primary_location.source.id:S…,publication_year:2025` (§2.1).
3. Crossref `https://api.crossref.org/works?filter=container-title:…,from-pub-date:…` for the ACM and IEEE proceedings that round 1 could not reach.
4. Venue program pages: USENIX technical-sessions (open access), NDSS paper pages, OpenReview v2 for ICLR, NeurIPS, ICML and SaTML (`https://api2.openreview.net/notes?invitation=…` works unauthenticated today), and the ACL Anthology bulk BibTeX with abstracts (`https://aclanthology.org/anthology+abstracts.bib.gz`).

### 1.2 Seed-set recall (canonical bibliographies)

**Frame.** Use the reference lists of canonical works. For each one, extract
every reference, classify it in or out of scope, and compute held/in.

| Seed | Target |
|---|---|
| NIST AI 100-2 E2025 reference list (public domain; parse from the cached PDF) | **≥ 95%** of in-scope references held |
| MITRE ATLAS v2026.09: every case study (73) and every technique `references:` URL (`ATLAS.yaml` in `mitre-atlas/atlas-data`) | **100%** of case studies linked to an INC or S-id; ≥ 95% of technique references |
| OWASP LLM Top 10:2025, Agentic Top 10:2026 (ASI), MCP Top 10, AI Testing Guide: reference sections | ≥ 95% |
| CoSAI Risk Map (YAML), CSA MAESTRO, Google SAIF, Databricks DASF 2.0 references | ≥ 90% |
| SoKs and surveys: Yao et al. 2312.02003; Das et al. LLM S&P survey; Cinà et al. *Wild Patterns Reloaded* (poisoning); Grosse et al. *Practical threat models* (USENIX'24); Liu et al. prompt-injection benchmark/SoK; the agent-security SoKs of 2025-2026; the LLM supply-chain agenda (2404.12736); an MCP security survey; a membership-inference SoK; a watermark-removal SoK. Use a list of 10-12, fixed at round-2 kickoff. | ≥ 90% of in-scope references held |
| International AI Safety Report 2025/2026 (cyber chapter refs) | ≥ 80% |

**Output.** `coverage/seed-recall.csv` with columns `seed_id, ref_n, in_scope_n, held_n, recall, missing`.

**Method.** Get the reference lists from OpenAlex `referenced_works` or the
Semantic Scholar `/paper/{id}/references` endpoint where available, and from
GROBID or `pdftotext` plus an LLM parser over the cached PDF otherwise. Every
missing in-scope reference becomes a `stub` record with
`relations.cited_by: [<seed>]`.

### 1.3 Citation-chasing closure (snowball convergence)

- **Backward.** Every in-scope reference cited by **≥ 3 held records** must be held.
- **Forward.** For every deep-tier record (§5), every in-scope citing paper with ≥ 20 citations, or from a top-4 or SaTML venue, must be held.
- **Convergence.** Each snowball round reports `new_in_scope / triaged`. Stop chasing a branch when one round adds **< 3%** new in-scope items, or zero items with ≥ 20 citations.
- **Capture-recapture estimate.** Two discovery channels run independently. For example, A = venue/TOC sweeps and B = citation snowball plus OpenAlex concept search. Then N̂ = (n_A · n_B) / m_AB (Lincoln-Petersen, or the Chapman variant N̂ = (n_A+1)(n_B+1)/(m+1) − 1), estimated **per attack class**. Target: held/N̂ **≥ 0.90** for every X-class. Bias caveat: the channels are not independent (both favour highly cited work), so read N̂ as a lower bound and report it beside the critic result in §1.7.

**Output.** `coverage/closure.csv` with columns `class, n_A, n_B, overlap, N_hat, held, est_recall, last_round_yield`.

### 1.4 Minimum evidence per attack class and per technique

| Unit | Minimum to pass |
|---|---|
| Each X-class (X01-X16) | ≥ 1 SoK or survey **and** ≥ 1 item ≤ 6 months old **and** ≥ 10 primary sources **and** an explicit "in-the-wild evidence: yes (INC/CVE ids) / none found (date, search)" line |
| Each AIT technique (146 today, plus new ones) | ≥ 2 independent primary sources (different author groups); ≥ 1 top-venue paper **or** a primary vendor/CVE disclosure; the seminal (first) paper identified; maturity backed by evidence-level fields (§3); every catalog mapping version-pinned |
| New technique proposals | Enter `attack-catalog.yaml` only when ≥ 2 primary sources show it and an integration-lane reviewer accepts it |

**Output.** `coverage/class-evidence.csv` and `coverage/technique-evidence.csv`.
Each row is `pass` or `fail(reason)`.

### 1.5 Coverage per target type

Use the target taxonomy in §3.2 (TT01-TT27). Each target type needs:

- ≥ 10 held sources;
- ≥ 3 sources at evidence level ≥ E3 where any exist;
- every incident or CVE in the log mapped to ≥ 1 TT;
- an explicit "none found" row with a dated query where nothing exists.

The matrix of TT × X-class × max evidence level is the asset-attack matrix's
twin for *product types*. An empty cell requires a logged negative search.

**Output.** `coverage/target-matrix.csv`.

### 1.6 Incident and vulnerability recall

| Frame | Target |
|---|---|
| ATLAS case studies (v2026.09: 73) | 100% linked |
| AI Incident Database: incidents classified security, adversarial, misuse or privacy (filter the weekly snapshot by the CSET/GMF taxonomy fields and keywords) | ≥ 85% linked or explicitly out of scope |
| OECD AIM: incidents tagged *security / robustness / privacy* | ≥ 70% of a stratified random sample of 100 linked or explicitly out of scope (no bulk API; see §2.4) |
| AVID reports | 100% triaged (the repo has been stale since 2026-03) |
| NVD/CVE: CVEs against the AI-stack product list (about 120 CPE/vendor/product strings, maintained in `coverage/ai-products.csv`) **plus** keyword hits ("prompt injection", "LLM", "model", "agent", "MCP", "pickle", "safetensors", …) | 100% triaged; every CVSS ≥ 7, KEV-listed or vendor-flagship CVE gets an INC/advisory entry |
| CISA KEV: AI-stack entries | **100%**. On catalog 2026.10.23 these were already MLflow, Ray, n8n and 6 Langflow CVEs. |
| GHSA reviewed advisories for AI packages (langchain*, llama-index, transformers, vllm, ollama, gradio, comfyui, mlflow, ray, open-webui, litellm, MCP SDKs, …) | 100% triaged |

**Output.** `coverage/incident-recall.csv`.

### 1.7 Adversarial completeness review (the actual pass/fail gate)

Each review round, a **fresh critic** works on a *different* account, with no
access to our coverage CSVs. It gets a fixed budget of about 40 searches, the
paper-API scripts, and one instruction: find in-scope items that are missing.
Each item it finds is graded **must-have** (top venue, ≥ 50 citations, catalog-
or seed-cited, an ITW incident, or a KEV/flagship CVE) or **nice-to-have**.

- **Planted holdout.** At kickoff the integration lane privately draws **60 items** stratified across the venue TOCs, ATLAS and AIID. The draw is a hash list, kept out of the repo until the end of the round. The lanes' measured recall on this holdout is the unbiased recall estimate. Target: **≥ 54/60 (90%)**, and **60/60 for the must-have subset**.
- **Pass.** The critic finds **≤ 5 must-haves** (normalized per 1,000 held) **and** holdout recall is ≥ 90%. **Two consecutive passes** end broad discovery. After that only the weekly latest-attacks loop (§4.3) continues.
- **Fail.** Every must-have the critic found becomes a *query*, a venue or a channel added to the harvesters. The harvesters must find it automatically next time. This fixes the method, not just the item.

### 1.8 Freshness (the "latest attacks" axis)

- **Detection latency:** median days from primary publication (arXiv v1, advisory date, blog post) to `stub`.
  - Target ≤ 7 days for E3+ items (production-demonstrated, CVE, ITW).
  - Target ≤ 14 days for papers.
- **Lag to light profile:** ≤ 21 days for E3+.

**Output.** `coverage/freshness.csv`, computed from `discovered_at` against `published_at` in the lead log.

### 1.9 Expected corpus size

| Component | Estimate |
|---|---|
| Round-1 corpus | 1,181 |
| Critic gap items | +400 to +600 |
| Venue sweeps | +600 to +1,000, mostly 2016-2022 and SaTML/USENIX'26 |
| Seed and snowball | +300 to +500 |
| Incidents, CVEs and advisories | +300 |
| **Expected total** | **about 2,800-3,500 references** |

Hence the tiering in §5: not every reference gets human-reviewed distillation.

---

## 2. Source inventory

### 2.1 Academic metadata and discovery APIs (all scriptable; verified 2026-10-26 unless marked)

| Source | Endpoint | Access and limits | Use |
|---|---|---|---|
| arXiv API | `https://export.arxiv.org/api/query?search_query=…&sortBy=submittedDate` | Free; ≤ 1 request per 3 s. A test returned 1,088 hits for `all:"prompt injection"`. | Daily delta by category and keyword. Use OAI-PMH (`https://oaipmh.arxiv.org/oai`) for bulk, and RSS `https://rss.arxiv.org/rss/cs.CR` for the daily listing. |
| OpenAlex | `https://api.openalex.org/works?search=…` | **Changed: an API key is now expected.** Without a key, a shared $0.10/day budget per IP; a **free key gets $1/day** (`https://openalex.org/settings/api`), and search costs about $0.001 per call (from today's response `meta`). | TOCs by `source.id`, `referenced_works`, `cited_by`, concepts and topics, OA locations and licenses. **One key per account** (5 keys = $5/day ≈ 5,000 calls/day). |
| Semantic Scholar Graph | `https://api.semanticscholar.org/graph/v1/…` | Unauthenticated calls return 429 (shared pool, observed today). Free key at `https://www.semanticscholar.org/product/api#api-key-form` (1 rps). | Citation counts, references, citations, `influentialCitationCount`, TLDRs, bulk search sorted by citations |
| Crossref | `https://api.crossref.org/works` (add `mailto=` for the polite pool) | Free | ACM and IEEE proceedings TOCs (CCS 10.1145, S&P 10.1109), DOI resolution, license field |
| DBLP | XML dump `https://dblp.org/xml/dblp.xml.gz` | **The search API is behind an Anubis bot challenge (HTTP 202) today.** Use the dump. | Venue-year TOCs (§1.1) |
| OpenReview v2 | `https://api2.openreview.net/notes/search?term=…`, `notes?invitation=ICLR.cc/2026/Conference/-/Submission` | Unauthenticated reads work (verified) | ICLR, NeurIPS, ICML, SaTML, TMLR; rejected papers too, flagged |
| ACL Anthology | `https://aclanthology.org/anthology+abstracts.bib.gz` | Free bulk | ACL, EMNLP, NAACL, Findings |
| USENIX / NDSS | `https://www.usenix.org/conference/usenixsecurity26/technical-sessions`; `https://www.ndss-symposium.org/ndss-program/…` | Open access HTML and PDF | Program sweeps; USENIX'26 is the largest single gap |
| Papers with Code successor / GitHub | `gh api search/repositories?q=…` | Use the authenticated `gh` CLI | Artifact links (code, datasets, PoCs) |
| Google Scholar | — | **No API; scraping violates its terms.** Do not automate it. Manual lookups only. | — |

### 2.2 Catalogs and standards (pin a version; re-harvest on release)

| Catalog | Where | Watch |
|---|---|---|
| MITRE ATLAS | `https://github.com/mitre-atlas/atlas-data/releases`: v2026.09 (2026-09-15), v2026.08, v2026.07 | GitHub releases feed. Diff techniques, case studies and deprecations each month; ids drift (report finding 9). |
| OWASP GenAI Security Project | `genai.owasp.org`; LLM Top 10:2025, Agentic Top 10:2026 (ASI01-10), MCP Top 10, Agentic Threats & Mitigations, AI Testing Guide, AIVSS; GitHub `OWASP/www-project-top-10-for-large-language-model-applications` (last commit 2026-08-05) | Repo commits and the release blog |
| CWE / CAPEC | `https://cwe.mitre.org/data/downloads.html`; the AI WG; view 1448 | CWE 5.0 (targeted for Oct 2026 per round 1). Check monthly. |
| NIST | AI 100-2 E2025, AI 600-1, SP 800-218A, AI RMF, the AI-security control overlays (COSAIS / SP 800-53 overlays), CAISI evaluations | `csrc.nist.gov` publications RSS |
| ETSI / UK | ETSI TC SAI (TS/EN 104 223, the baseline AI cyber requirements derived from the UK AI Cyber Security Code of Practice) | Publications search |
| ISO/IEC | 27090 (AI security), 42001, 23894, 5338 | iTeh licensed previews only (memory rule: no licence-walled downloads without asking) |
| Industry | CoSAI (Risk Map YAML, `github.com/cosai-oasis`), CSA (MAESTRO, AICM), Google SAIF, Databricks DASF, IBM AI Atlas Nexus, MIT AI Risk Repository | Commits and releases |
| National | UK NCSC/DSIT; CISA/NSA/FBI joint guidance (*Deploying AI Systems Securely*, *AI Data Security*); ANSSI; BSI; ENISA; Singapore CSA; Japan AISI; China TC260; Korea KISA; India CERT-In; Australia ASD; Canada CCCS | The non-US gap. Check quarterly. Use landing pages plus the English PDFs; translate the summaries. |

### 2.3 Vulnerability feeds

| Feed | Endpoint | Note |
|---|---|---|
| NVD CVE API 2.0 | `https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=…&pubStartDate=…` (a free key raises limits to 50 requests per 30 s) | `keywordSearch=prompt injection` returned **211** CVEs today. Round 1 counted 194 CVEs with both words on 2026-10-03 (136 with the exact phrase), so about +17 in 3 weeks: this needs a weekly loop. |
| CVE List V5 | `https://github.com/CVEProject/cvelistV5` (delta commits every 7 minutes) | Faster than NVD enrichment. Covers huntr (Protect AI is a CNA), GitHub and vendor CNAs. |
| GHSA | `gh api /advisories?ecosystem=pip&affects=<pkg>&per_page=100` | Note: the `keyword` parameter was **ignored** in today's probe (it returned unrelated advisories). Query by `affects` over the package list. |
| OSV | `https://api.osv.dev/v1/querybatch` | One call per batch over the AI package list (`langchain` alone has 45 vulns) |
| CISA KEV | `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | Catalog 2026.10.23 (1,756 entries). Filter by the AI product list. |
| huntr | `https://huntr.com` (`/bounties` returned 404 today; the site layout changed) | Rely on its CVEs through cvelistV5. Read its blog manually. |
| ZDI | `https://www.zerodayinitiative.com/rss/published/` | Pwn2Own AI category advisories |
| Vendor advisories | MSRC Security Update Guide API (`https://api.msrc.microsoft.com/cvrf/v3.0/`), Google/Android bulletins, GitLab, JetBrains, Anthropic/OpenAI/GitHub security pages, Cursor/Windsurf changelogs | Coding-agent CVEs (report finding 5) |

### 2.4 Incident databases

| Source | Access | Note |
|---|---|---|
| AI Incident Database (AIID) | GraphQL `https://incidentdatabase.ai/api/graphql` now returns **403 "API access is restricted to authorized domains"**. Weekly **snapshots** are public: `https://incidentdatabase.ai/research/snapshots/`, latest `backup-20261026101519.tar.bz2` | Weekly snapshot diff. Filter by taxonomy (CSET, GMF) and keywords. Ask the AIID for API access if needed. |
| OECD AI Incidents Monitor | `https://oecd.ai/en/incidents` (302 to the app; no documented bulk API) | Manual stratified sampling and the UI's export where available. Multilingual news, so it partly fixes the non-English gap. |
| AVID | `https://github.com/avidml/avid-db` (last commit 2026-03-26) | One-time triage |
| ATLAS case studies | `ATLAS.yaml` | 100% linked |
| AIAAIC Repository | `https://www.aiaaic.org/aiaaic-repository` (published as a Google Sheet) | Monthly CSV export |
| MITRE AI Incident Sharing; vendor threat-intel reports (Anthropic, OpenAI, Google GTIG, Microsoft MSTIC) | Pages and PDFs | AI-enabled offense (X14). These are quarterly report series. |
| GDELT DOC 2.0 | `https://api.gdeltproject.org/api/v2/doc/doc?query=…&mode=artlist&format=json&timespan=7d` | **Limit 1 request per 5 s** (we hit a 429 today). The `sourcelang:` filter gives multilingual news leads. Leads only. |

### 2.5 Vendor research blogs and newsletters (harvested as RSS/Atom; leads plus primary sources)

**Primary research blogs** (often the primary disclosure):

Embrace The Red (Rehberger), Simon Willison (`simonwillison.net/atom/everything/`), PromptArmor, Invariant Labs/Snyk, Trail of Bits, NCC Group, HiddenLayer, Protect AI/huntr, JFrog, Wiz Research, Legit, Aim Labs/Cato, Zenity Labs, Noma, Pillar, Lakera, Koi Security, Socket, ReversingLabs, Unit 42, Check Point Research, Kaspersky Securelist, Microsoft AI Red Team and MSRC blog, Google Project Zero, Google GTIG and Big Sleep, Anthropic (threat intelligence reports, red-team posts), OpenAI (threat reports), Cisco AI Defense, Tenable, Orca, Sysdig, Aqua, GitGuardian, Truffle Security, Brave security blog (AI browser bugs), LayerX, SPLX, Straiker, Mindgard.

**Aggregators and newsletters** (leads only):

tl;dr sec, the AI security newsletters and digests (e.g. "Prompt Injection weekly"-style curations), Risky Business News, SANS NewsBites, The Register / BleepingComputer / SecurityWeek / Dark Reading AI tags, Import AI, Last Week in AI.

**Conference talks** (leads, plus primary sources for talk-only disclosures):

Black Hat (USA/EU/Asia) briefings pages, DEF CON (AI Village, media.defcon.org), CCC (`media.ccc.de` API), USENIX YouTube, CAMLIS, SaTML, OWASP Global AppSec, BSides. Vendor talks often disclose before the paper does.

The harvester takes a curated `feeds.yaml` (about 80 feeds) of `{url, kind: primary|aggregator, owner_lane}`. Adding a feed is a one-line PR.

### 2.6 Social signal: realistic options in late 2026

**X/Twitter.** This is where much of the AI-security "first post" happens (PoCs, jailbreak threads, disclosures).

- **Official API, pay-per-use.** This is now the default for new developers. Verified on `https://docs.x.com/x-api/getting-started/pricing` on 2026-10-26:
  - post read **$0.005 per post returned**; user read $0.010;
  - recent counts $0.005 per request; full-archive counts $0.010;
  - cap of **3M post reads per billing cycle**;
  - posts dedup-billed within 24 h UTC (a soft guarantee);
  - $20 starter credit.
  - Legacy Basic ($200/month) and Pro ($5,000/month) are reportedly only for existing subscribers, and Enterprise is about $42k/month (third-party guides, not verified on X's site).
- **Cost model.** Do not stream a list timeline: 150 researchers × about 5 posts/day ≈ 22k reads/month ≈ $110. Instead, run **narrow recent-search queries** combining the curated author list with link and keyword filters, e.g. `(from:a OR from:b …) (jailbreak OR "prompt injection" OR CVE OR exploit OR poisoning OR backdoor OR MCP OR agent) has:links -is:retweet`. Run them in 5-6 query shards (query length limits) twice daily. That is ≈ 30-80 posts/day ≈ **$5-12/month**. Set a hard cap of **$25/month**, enforced by the harvester's spend counter plus X console limits. One account, owned by the sponsor (billing), shared as a GitHub Actions secret or a local secret. It is never committed.
- **Terms that bind us:**
  1. **No scraping.** X's ToS bars crawling or scraping without prior written consent, with **liquidated damages of $15,000 per 1,000,000 posts** accessed in a 24 h period (in force since 2024-11-15; Knight Institute and ConductAtlas reported text, not fetched from X, whose ToS page returned 402).
  2. The developer agreement (June 2025) **bars using X API content to train or fine-tune foundation or frontier models**. Our use (lead triage and summarization) is not training, but no X content may go into any fine-tuning set. Write this into `PROVENANCE`.
  3. X's developer policy limits redistribution to **post IDs**, so the public repo stores **post IDs and URLs only, never post text or media**. Paraphrase in our own words, and only after corroboration.
- **Not acceptable:**
  - headless-browser or logged-in-session scraping;
  - third-party "X scraper" services (Apify actors and the like) or Nitter-style mirrors;
  - sharing one API key across people or tools against the developer terms;
  - bulk archiving of post text into the repo.
- **Acceptable without the API:** humans reading X on their own accounts and pasting a URL into the lead form (`leads/inbox.csv` or a GitHub issue form). A bookmark export of the person's own bookmarks counts as owned reads. Possible add-on: xAI's API offers an X-search tool (licensed access, billed per source). Evaluate it only if the $25/month raw-API pipeline under-delivers, and check its current price and terms first.

**Bluesky.** Open and free. This is the best social ROI today; many ML and security researchers moved there.

- `https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=…&sort=latest` works **unauthenticated** (HTTP 200 today).
- `https://public.api.bsky.app/…/searchPosts` returned **403** today. Use `api.bsky.app` or authenticate with an app password (`com.atproto.server.createSession`).
- Researcher lists and starter packs: `app.bsky.graph.getList`, `getStarterPack`.
- Firehose filtered by DID: Jetstream `wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post&wantedDids=…`.
- Terms: public data; respect rate limits (3,000 requests per 5 min per IP on the AppView).

**Mastodon.**

- `infosec.exchange` (the infosec hub) returns **422 "requires an authenticated user"** on tag timelines, and search returns empty unauthenticated. Create a research account on that instance and use a read-only app token (`read:statuses`).
- `mastodon.social` tag timelines are public (`/api/v1/timelines/tag/promptinjection`, HTTP 200).
- Harvest hashtags (#promptinjection, #llmsecurity, #aisecurity, #jailbreak, #mcp) plus the home timeline of a research account that follows the curated list.
- Respect per-instance rate limits (300 requests per 5 min) and the instance rules.

**Hacker News.** Algolia API: `https://hn.algolia.com/api/v1/search_by_date?query=…&tags=story` (free; verified; returned 2026-10-24..26 prompt-injection and MCP items). Good for vendor write-ups and PoC repos.

**Reddit.** Unauthenticated JSON returns **403** today. API access needs a registered OAuth app under Reddit's developer terms (pre-approval for new apps). Low priority: r/netsec, r/LocalLLaMA and r/MachineLearning add little beyond HN and Bluesky. Apply only if the critic finds Reddit-first disclosures.

**GitHub as a social signal.**

- `gh api search/repositories?q=jailbreak+OR+prompt-injection+created:>…&sort=stars`;
- trending PoC repos;
- security advisories (§2.3);
- awesome lists (e.g. awesome-llm-security, awesome-MCP-security) as seed lists. Diff them weekly.

**LinkedIn, Discord, Telegram.** Do not automate; terms forbid scraping. Use manual lead entry only.

**Curated researcher lists** (`social/accounts.yaml`; public handles of researchers and orgs only; reviewed quarterly):

- about 150 entries;
- per-platform handles;
- `why` (e.g. "frequent first disclosure of coding-agent bugs");
- `last_signal_date`; drop after 6 months without a hit.

Seed the list from authors of E3+ sources in the corpus and from vendor research team accounts. It contains public professional handles only, not people from the project (publishing-privacy rule).

**Compliant social-signal pipeline (leads → corroboration → corpus):**

```
harvest_{x,bsky,masto,hn,gh}  →  leads/raw/YYYY-MM-DD.jsonl   (private cache, NOT committed: post text lives here only)
   fields: platform, post_id, url, author_handle, created_at, text_hash, outbound_urls[], matched_query
→ extract outbound URLs, canonicalize (§4.2); drop posts with no outbound link unless author ∈ trusted list
→ resolve against corpus identity index (DOI / arXiv / CVE / GHSA / canonical URL): KNOWN → append to lead log as corroboration signal only
→ NEW → triage (LLM, cheap): in-scope? kind? (paper|advisory|PoC|incident|opinion) → score
→ corroboration gate: a lead becomes a source ONLY when a PRIMARY artifact is fetched and recorded:
     paper/preprint, CVE/GHSA/vendor advisory, vendor or researcher write-up with technical detail, code repo, talk recording/slides.
   If the post itself is the only disclosure: record as type `web`, confidence low, `evidence: social-only`,
   archive via Wayback "Save Page Now" for the outbound link (not X itself), and re-check in 30 days.
→ committed artifact: leads/log.csv  (lead_id, platform, post_id, url, discovered_at, resolved_to (record id|none), status)
   — IDs and URLs only, no post text.
```

**Signal metrics (monthly):** leads per platform, % corroborated, % that were *first* (discovered ≥ 3 days before any other channel), cost per corroborated new source. If a platform has a < 5% corroboration rate or contributes no "first" item in 8 weeks, drop it.

### 2.7 WebSearch

WebSearch is reserved for what no API covers: non-English national guidance, news after 2026-08, vendor pages, and critic rounds. With 5 accounts at about 200 calls per session, the budget is **≤ 120 calls/week per account**, logged in `searches.md` (query, account, hits, kept). Everything in §2.1-2.6 runs through free APIs with scripts and does not use the WebSearch quota.

### 2.8 Non-English coverage

- GDELT with `sourcelang:chinese|japanese|korean|french|german|russian` plus AI-security keywords;
- the OECD AIM multilingual feed;
- CNKI and J-STAGE titles through OpenAlex (OpenAlex has non-English metadata);
- national CERT feeds: CNVD/CNNVD AI entries where public, JPCERT, KrCERT, CERT-FR, BSI.

**Targets.**

- ≥ 1 national guidance record per G20 jurisdiction that has published one.
- A non-English incident share ≥ 10% of newly logged incidents, against about 0% today.

### 2.9 Probe log (2026-10-26)

| Probe | Result |
|---|---|
| `api.bsky.app` searchPosts | 200 (unauthenticated) |
| `public.api.bsky.app` searchPosts | 403 |
| infosec.exchange tag timeline | 422 (requires auth) |
| mastodon.social tag timeline | 200 |
| HN Algolia | 200 |
| Reddit JSON | 403 |
| OpenAlex | 200, with a notice that a key is now expected |
| DBLP API | 202 Anubis challenge on all three mirrors |
| DBLP XML dump | 200 (1.11 GB) |
| Semantic Scholar | 429 without a key |
| arXiv API | 200 |
| OpenReview v2 | 200 |
| NVD | 200 ("prompt injection": 211 CVEs) |
| OSV | 200 |
| CISA KEV | 200 (catalog 2026.10.23) |
| ATLAS releases | v2026.09 |
| AIID GraphQL | 403 (origin-restricted); weekly snapshots 200 |
| GDELT | 429 (1 request per 5 s) |
| huntr `/bounties` | 404 |
| X pricing docs | fetched |
| X ToS | 402 to the fetcher |

---

## 3. Distillation profile for every reference: **DX-AI/1** ("light")

DX-AI/1 sits **between** the library `summary.md` (six sections) and FX-AP/FX-TM.

- **Target size:** a 1-2 page `distilled/ai-profile.yaml`, plus the RPT-0014 applicability table already defined in LANES.md.
- **Library fit:** it uses the existing `threats` artifact family (`schema/artifact.schema.yaml`, `library-threats/v1`: `threats[]` with actor, capability, attack_vector, affected_asset, external_id, locator, kind) **plus** an `ai_profile` header block. That block needs one small library schema PR: a forward-looking family `ai-attack-profile`, or optional keys on `threats`. This keeps the library free of any tmodel KG dependency, as `consumed_by` in that schema requires.
- **Record fields:** `distillation.artifacts[]` gets `kind: threats`, `path: distilled/ai-profile.yaml`, `coverage`, `reviewed_by`.

### 3.1 Fields

```yaml
schema: "library-ai-profile/v1"        # proposed
record: greshake-2023-indirect-prompt-injection
profile: DX-AI/1
contribution_kind: attack            # attack | defense | measurement | benchmark | survey/SoK | threat-model | catalog | incident-report | advisory | tool | position
targets:                             # §3.2 taxonomy; 1..n; each with locator + kind
  - {tt: TT06, product_examples: ["Bing Chat (GPT-4)"], locator: "§4.1", kind: stated}
  - {tt: TT09, product_examples: ["GitHub Copilot-style code completion"], locator: "§4.3", kind: stated}
  - {tt: TT07, kind: inferred}
modality: [text, code]               # text|code|image|audio|video|tabular|graph|rl|multimodal|sensor
deployment: [provider-hosted]        # provider-hosted | self-hosted | on-device | federated | n/a
lifecycle: [operation]               # supply-chain | data | development-training | deployment | operation | decommission
attack:
  ait: [AIT-0xx]                     # existing ids; or `proposed: "<name>"` for integration lane
  x_class: [X08, X11]
  atlas: {version: "v2026.09", ids: [AML.T0051.001]}
  owasp: [LLM01:2025, ASI01:2026]   # always year-suffixed
  nist_ai_100_2: {version: E2025, ids: [NISTAML.015]}
  cwe: {version: "4.20", ids: [CWE-1427]}
  other: []                          # MCP Top10, CoSAI risk ids, CAPEC, ATT&CK (AI-enabled offense), LW-*
attacker:
  position: content-plant            # none-external | api-user | content-plant (indirect) | supply-chain-contributor | co-tenant | insider-developer | operator/provider | physical-proximity | network-adjacent
  knowledge: black-box               # white-box | grey-box | black-box | n/a
  capabilities: ["publish web content the app retrieves"]
  cost: {queries: null, compute: null, money_usd: null, note: ""}
preconditions: ["app retrieves untrusted content into context", "tool or render channel available"]
impact:
  cia: [confidentiality, integrity]  # + availability | safety | financial | privacy | reputational | autonomy-loss
  assets: [A07, A09, A03]            # report §2 asset classes
  headline_result: "…"               # one number with table/figure locator
evidence:
  level: E3                          # E0 theoretical | E1 simulation/toy | E2 real model offline/open-weight | E3 production system demo / disclosed to vendor | E4 CVE/advisory issued | E5 exploited in the wild (INC/KEV)
  against: ["Bing Chat 2023-02"]     # named systems
  incidents: [INC-…]                 # links into incidents.md
  cves: []
  reproducibility: code-released     # code-released | partial | described-only | none
mitigations:
  evaluated: [{name: "…", result: "bypassed|reduced to x%|held", locator: ""}]
  proposed: ["…"]
artifacts:                           # every link checked for liveness by script
  code: [{url: "https://github.com/…", license: "MIT", stars: 0, checked: "2026-10-27"}]
  datasets: []
  pocs: []
  models: []
  advisories: []
  talks: []
novelty: {first_of_kind: true, builds_on: [record-ids], superseded_by: []}
confidence: medium
review:
  extracted_by: {lane: agentic-mcp, account: A3, model: "…", effort: high, date: "2026-10-27"}
  verified_by: {pass: ai-verify, date: "…", defects: 2}
  reviewed_by: ""                    # human; empty = hypothesis (R-018)
```

### 3.2 Target / product-type taxonomy (TT; maps to reference components C01-C21)

| TT | Target type | C-map | Examples |
|---|---|---|---|
| TT01 | Hosted foundation model / model API (closed weights) | C13, C05 | GPT, Claude, Gemini APIs |
| TT02 | Open-weight model checkpoint | C04, C05 | Llama, Qwen, Mistral weights |
| TT03 | Fine-tuned or adapted model (LoRA/PEFT, merges, distillations) | C03, C04 | adapters on hubs |
| TT04 | Predictive ML model (tabular, credit, fraud, forecasting) | C05 | scoring models |
| TT05 | Security ML and guardrails (malware/spam/IDS classifiers, guard models, moderation, AI detectors) | C05, C18 | Llama Guard, PDF malware classifiers |
| TT06 | LLM chat app / copilot / assistant | C07 | ChatGPT, M365 Copilot, Slack AI |
| TT07 | RAG / enterprise search / knowledge assistant | C06 | vector DB + LLM |
| TT08 | Tool-using autonomous agent (general) and agent memory | C08, C10, C11 | assistants with email or calendar |
| TT09 | Coding assistant / coding agent / CI-integrated agent | C08, C14 | Copilot, Cursor, Claude Code, Gemini CLI, GitHub agentic workflows |
| TT10 | Computer-use / browser agent, AI browser or extension | C20 | Comet, Atlas, Operator |
| TT11 | Multi-agent system / agent-to-agent protocol | C08 | A2A, CrewAI |
| TT12 | MCP server, tool, plugin, agent skill, marketplace | C09 | MCP registries, GPT Store, skills |
| TT13 | Model, dataset or prompt hub and registry | C04 | Hugging Face, Ollama registry |
| TT14 | ML/LLM frameworks, libraries and serialization formats | C04, C14 | PyTorch, pickle, Keras, transformers, LangChain |
| TT15 | Training data pipeline (collection, labeling, preference/RLHF, web-scale corpora) | C01, C02, C03 | LAION, Common Crawl |
| TT16 | Federated, collaborative and split learning / inference | C03, C05 | FL, split inference |
| TT17 | Inference serving and MLOps/LLMOps platform, AI gateway | C05, C15, C18, C19 | vLLM, Ollama, Ray, MLflow, Langflow, LiteLLM |
| TT18 | Accelerator / GPU / memory / TEE hardware | C15 | GPU Rowhammer, side channels |
| TT19 | Edge, embedded and on-device AI | C16 | phones, NPUs, IoT |
| TT20 | Autonomous vehicle, drone and robot perception and control (embodied AI) | C16 | LiDAR spoofing, BadRobot |
| TT21 | Biometric and identity verification (face, voice, liveness, KYC) | C16, C05 | face recognition, voice auth |
| TT22 | Speech / voice assistant interfaces | C16, C07 | DolphinAttack |
| TT23 | Vision, multimodal and generative image/video/audio models (VLM, T2I) | C05 | diffusion, VLM jailbreaks |
| TT24 | Recommender, ranking, search, LLM-as-judge and evaluator | C05, C07 | JudgeDeceiver, SEO for LLM search |
| TT25 | Content provenance, watermark and deepfake detection | C05 | C2PA, SynthID-style marks |
| TT26 | People and organizations as targets of AI-enabled offense (phishing, deepfake fraud, influence, hiring) | C12 | Arup, fake IT workers |
| TT27 | Conventional IT and software attacked with AI uplift (exploitation, malware, recon) | C17 | AI-orchestrated intrusion |

**Rule.** A target is the *product type that is attacked*, not the asset class
(A-ids) and not the component (C-ids). All three are recorded. TT gives the
sponsor's "impacted product types" view. TT26 and TT27 keep AI-enabled offense
in scope without pretending it targets an AI system.

### 3.3 Who fills which field

| Field | AI-extract | Mechanical check | Human review |
|---|---|---|---|
| Bibliographic, identifiers, sha256, license | ✓ (from APIs, not the LLM) | Validator; DOI/arXiv resolve | — |
| contribution_kind, modality, deployment, lifecycle | ✓ | Enum | Sample 10% |
| targets (TT) + product_examples | ✓ draft | Enum; a locator is present when `stated` | **Required** for deep tier; sample 15% light; 100% when the two AI passes disagree |
| AIT / x_class | ✓ draft | Id exists in `attack-catalog.yaml` | **Required** when `proposed` or new; sample 15% otherwise |
| ATLAS / OWASP / NIST / CWE ids | ✓ draft | Id exists in the **pinned** version file (ATLAS.yaml v2026.09, CWE 4.20 XML, OWASP id+year list, NISTAML list); deprecated ids rejected | Sample 15%; edge cases flagged by `kind: inferred` |
| attacker position/knowledge, preconditions | ✓ | Enum | Sample 15%; required deep |
| impact, headline_result | ✓ with locator | The number appears in the cached text (grep check) | Required deep |
| **evidence.level** | ✓ draft | E4 requires a CVE id that resolves in NVD/cvelist; E5 requires an INC or KEV id | **Required for E3+** (it drives maturity) |
| mitigations | ✓ | — | Sample |
| artifacts (code, data, PoC) | ✓ + GitHub/Zenodo/HF search | URL liveness, license via `gh api repos/…/license`, stars | — |
| novelty.first_of_kind | Suggest | — | **Human or integration lane only** |
| confidence | AI proposes | Capped at medium if any field is `inferred` without a locator, or if read from the abstract only | Human final |
| bears_on (DEC/R ids) | **Not for students or AI**: integration lane | Ids exist in ARCH-0001 | Integration lane |

### 3.4 Quality controls for DX-AI/1 (cheap, script-enforced)

1. **Two-pass disagreement.**
   - Every light profile is produced by an extractor pass and a separate verifier pass (fresh context, effort high, reads the source text).
   - The verifier outputs only a field-level diff.
   - Disagreement on `targets`, `ait`, `evidence.level` or `atlas` triggers human review.
   - 5% of items are double-extracted on **different accounts**. Report field agreement: exact match on enums, Jaccard on sets. Target Jaccard ≥ 0.7 for TT and AIT, and κ ≥ 0.7 for evidence level. Below that, the definitions get fixed, not the people.
2. **Locator rule.** Every `stated` value has a locator (section, page, table or figure). Anything without one is `inferred`.
3. **Number rule.** Every number in `headline_result` must grep-match the cached text (pdftotext).
4. **Catalog pin rule.** The validator rejects un-suffixed OWASP ids and ATLAS ids absent from the pinned release.

---

## 4. Ingestion pipeline and loop

### 4.1 Stages

| # | Stage | Tool (to build; stdlib Python 3, no Node) | Output | Done when |
|---|---|---|---|---|
| 1 | **Discover** | `harvest-arxiv`, `harvest-openalex`, `harvest-dblp-dump`, `harvest-crossref`, `harvest-openreview`, `harvest-acl`, `harvest-s2-refs`, `harvest-nvd`, `harvest-cvelist`, `harvest-ghsa`, `harvest-osv`, `harvest-kev`, `harvest-atlas`, `harvest-aiid-snapshot`, `harvest-rss` (feeds.yaml), `harvest-bsky`, `harvest-masto`, `harvest-hn`, `harvest-x` (budget-capped), `harvest-gdelt`, `harvest-gh-repos` | `leads/raw/*.jsonl` (private cache) | Each run writes `{source, query, n, cost}` to `leads/runs.csv` |
| 2 | **Identity and dedupe** | `ident` (§4.2) | `leads/candidates.csv` with `match: new\|known:<record-id>\|fuzzy:<id>?` | Fuzzy matches resolved by a human in a batch view |
| 3 | **Triage** | `triage` (LLM, cheap model or low effort; prompt pinned in repo) | `in\|adjacent\|out`, kind, X-class guess, TT guess, priority score (§5) | 5% human spot check; out-of-scope items logged with a reason (`usefulness: not-useful` keeps them from returning) |
| 4 | **Ingest record** | `bin/ingest` (library) + `prefill` (fills authors, date, ids, venue, license, OA PDF URL from Crossref/OpenAlex/arXiv: **no LLM for metadata**) + `fetch-pdf` (cache + sha256) | `records/<body>/<id>/record.yaml`, `status: stub\|fetched` | `bin/validate` passes |
| 5 | **Summarize** | Library skill `summarize` | `summary.md`, `status: summarized` | Six sections + RPT-0014 applicability table |
| 6 | **Distill** | New skill `distill-ai` (DX-AI/1); deep tier → existing `rpt0014-extract` (FX-AP/FX-TM) | `distilled/ai-profile.yaml` | Schema-valid; locator, number and pin checks pass |
| 7 | **Adversarial verify** | `verify-ai` (fresh context, different account where possible) | `distilled/verify.md` with field diffs and defects | All disagreements resolved or flagged |
| 8 | **Human sample review** | `review-queue` (prints the next N items to review with source links) | `reviewed_by` signed | Sampling quotas (§3.3) met per week |
| 9 | **Integrate** | `rpt0014-integrate` (integration lane) + `coverage` | New S-/INC-/AIT- ids, catalog updates, `coverage/*.csv`, report delta | Weekly |

### 4.2 Dedupe and identity keys (in priority order)

- **Work vs version.** The library holds one record per document *line* (schema `versions/`). arXiv v1→v3 and a later venue version are the **same** record. Venue DOI and arXiv id are both kept in `identifiers`.
- **Strong keys, in order:**
  1. DOI, lowercased, with the `https://doi.org/` prefix stripped.
  2. arXiv id without version (`2302.12173`), also derived from `arxiv.org/{abs,pdf,html}/…vN` URLs.
  3. OpenReview forum id.
  4. CVE id.
  5. GHSA id.
  6. OSV id.
  7. ATLAS `AML.CSxxxx`.
  8. AIID incident number.
  9. Post id (`x:<id>`, `bsky:<at-uri>`, `hn:<id>`).
  10. OpenAlex W-id and S2 paperId (as cross-walk keys).
- **URL canonicalization:**
  - force https; lowercase the host; drop `www.`;
  - strip `utm_*`, `ref`, `fbclid`, `gclid` and fragments;
  - drop a trailing `/` and `index.html`;
  - resolve shorteners (`t.co`, `bit.ly`, `lnkd.in`) with a HEAD follow;
  - map `medium.com/@x/slug-<hash>` to the hash;
  - map `usenix.org/conference/<conf>/presentation/<slug>` to `(conf, slug)`;
  - map `github.com/o/r/(tree|blob)/…` to `o/r` plus path;
  - map `x.com` and `twitter.com` to `x:<id>`.
- **Fuzzy key:** `norm_title`, the first 12 tokens after lowercasing and stripping punctuation and stopwords, plus `year ±1` plus the first author surname. Candidates go to a human only when the title similarity is ≥ 0.9 and no strong key matches.
- **Content hash:** sha256 of the retrieved bytes, stored as `content.sha256`. It is evidence, **not identity**. arXiv revisions and publisher re-issues change it, and `bin/fetch-pdfs` already reports `CHANGED`.
- **Incident identity:** one INC per real-world event. CVEs, AIID ids, ATLAS case studies and news articles attach to it as aliases.

### 4.3 Cadence

| Loop | Cadence | Content |
|---|---|---|
| **Latest-attacks loop** | **Weekly** (Monday harvest, Friday integrate) | arXiv delta, cvelist/NVD/GHSA/OSV/KEV delta, RSS, Bluesky/Mastodon/HN/X, AIID snapshot diff, GitHub repo search. Target: about 30-80 new in-scope leads a week; every E3+ item gets a light profile within 14 days. |
| Daily (optional, automated) | Daily | KEV and cvelist AI-product filter. **Alert** (GitHub issue) on any KEV-listed AI product: those are ITW evidence. |
| Catalog watch | Monthly | ATLAS release diff, OWASP repo diff, CWE release, NIST/CSRC, CoSAI commits. Re-pin, then remap the affected ids by script. |
| Breadth sweep | Once in round 2, then annually | Venue-year TOCs (§1.1), seed sets (§1.2), snowball (§1.3) |
| Critic round | Every 2 weeks until two passes, then quarterly | §1.7 |
| National guidance | Quarterly | §2.2 national row |

### 4.4 PDF and licensing policy

**PDFs.**

- PDFs are cached **outside every repo**: `~/tmodel-pdf-cache/ai-threat-model/<record-id>.pdf`, with a `.txt` extracted alongside.
- `pdf-manifest.tsv`, or the library record's `content`, holds the URL, sha256, retrieval date and license.
- The cache is per person, rebuilt with `bin/fetch-pdfs`. Optionally, one shared copy goes on the NAS, under the workspace archive rules: it is an archive, so a `library/` record and an explicit yes come first.
- Only open-access URLs: arXiv, OA publisher copies, USENIX/NDSS open proceedings, government PDFs, and OA locations from OpenAlex/Unpaywall. **No** Sci-Hub or shadow libraries. **No** licence-walled standards (iTeh previews only for ISO/IEC). **No** paywalled IEEE/ACM full text unless it is fetched through an account licence a student personally holds; those copies are cached locally only and **never** quoted beyond fair-use snippets.

**Quotes in the public repo.** Record `license` per record from the arXiv license field, the Crossref `license`, OpenAlex `best_oa_location.license`, or the repo LICENSE.

| License | Rule |
|---|---|
| Public domain (US Government), CC0, CC BY, CC BY-SA, Apache-2.0, MIT | Full quotes allowed, with attribution |
| **arXiv default "non-exclusive license to distribute"** (most arXiv papers), all-rights-reserved vendor PDFs, journals, news | Paraphrase; ≤ 2 sentences verbatim per entry with a locator, as already in `extractions/README.md` |
| Social posts | **No text.** IDs and URLs only (X policy), and our own paraphrase only after corroboration |

The quote checker in `verify-ai` flags any verbatim run of more than 50 words from a non-permissive source.

### 4.5 Budget and quota across the 5 accounts

| Resource | Allocation |
|---|---|
| WebSearch | ≤ 120 calls/week per account; critic rounds get a separate 40 per round; log every call |
| OpenAlex | 1 free key per account ($1/day each). Harvesters spread by lane, so the shared IP budget is never used. |
| Semantic Scholar | 1 key for the integration lane (1 rps) |
| NVD | 1 key (integration lane) |
| X API | 1 sponsor-owned account, hard cap $25/month |
| Bluesky / Mastodon | 1 research account each (integration lane); app password / read token as local secrets |
| LLM effort | Triage: low effort or a small model, batch. Light profile: extractor + verifier at **high**, not max (≈ 60-120k tokens per reference in total). Deep FX-AP/FX-TM: max, ≈ 300-600k per unit (LANES.md), **one unit at a time**. |

**Weekly per-account envelope** (to be calibrated in week 1 from the actual usage meters):

- about 25-40 light profiles per student account;
- about 2-3 deep units per account;
- the integration account mostly runs scripts, triage and verification.

Batch automation (`claude -p` headless) is allowed for triage and L0
(below). Its output is labelled `review.extracted_by.model` and never counts
as reviewed.

### 4.6 Tooling to build (week 1-2)

Proposed location: `tools/rpt0014/` in tmodel. Language: Python 3 stdlib plus `requests`/`pyyaml` if already used. **No Node** (workspace rule). Each tool is ≤ 200 lines, has `--since` and `--dry-run`, and writes JSONL/CSV.

1. `harvest-*`, as in §4.1. Day-1 priorities: arxiv, openalex, cvelist/nvd, kev, rss, bsky, hn.
2. `ident`: the canonicalizer and identity index (`index/identity.csv`, regenerated from library records + `sources.md` + `incidents.md`).
3. `triage`: the LLM triage runner with a pinned prompt; output to the candidates CSV.
4. `prefill`: metadata to a record scaffold, wrapping `bin/ingest`, so students never type metadata.
5. `next`: claims the next unit from `queue.csv` (lane, priority), creates the branch, fetches the PDF, prefills, prints the checklist. **This is the "ready-made script" that unblocks students** (§6).
6. `check-ai-profile`: schema, enums, catalog-pin, locator, number-grep and link-liveness checks.
7. `coverage`: regenerates `coverage/*.csv` and a one-page `coverage.md` with pass/fail per axis.
8. `review-queue`: the stratified sampler for human review.
9. `x-budget`: the spend counter, which refuses to run once the monthly cap is reached.

---

## 5. Prioritization: which references get deep distillation

**Three tiers:**

| Tier | Count | What it gets | Who |
|---|---|---|---|
| **L0 auto** | all (about 3,000) | record + summary + DX-AI/1 from the AI extract+verify passes, `reviewed_by` empty, confidence capped at medium | Headless batches, integration lane |
| **L1 light-reviewed** | about 600-900 | L0 + human review of `targets`, `ait`, `evidence.level`, catalog ids | Students, about 25/week each |
| **D deep** | **about 200-250** (hard cap 300) | FX-AP (attack papers) or FX-TM (threat models, catalogs), 3 passes + human sign-off | Students, about 2/week each; integration verifies |

**Deep-tier score** (computed by `coverage`; ties broken by the integration lane):

```
score = 3·seminal(first paper for an AIT technique or X-class)
      + 2·catalog_cited (cited by NIST AI 100-2, ATLAS technique/case study, OWASP, CoSAI) 
      + 2·evidence (E5=2, E4=1.5, E3=1)
      + 1.5·sole_source (only source for a TT×X cell or an AIT technique)
      + 1·log10(1 + citations/age_years)          # S2/OpenAlex, normalized per year
      + 1·top_venue (S&P, USENIX, CCS, NDSS, SaTML, NeurIPS, ICML, ICLR, ACL)
      + 1·artifact (code or PoC released)
      + 1·recency (≤ 6 months and E3+)
      − 2·superseded (a later paper/version of the same line is in D)
```

**Quotas** (so the top-N is not all prompt-injection papers):

| Quota | Count |
|---|---|
| Seminal paper for each AIT technique (de-duplicated) | ≈ 110 |
| FX-TM for the top 40 threat models and catalogs (ATLAS, OWASP ×4, NIST AI 100-2, CoSAI, MAESTRO, SAIF, DASF, BIML ×2, MS AI threat models, AWS Threat Composer GenAI, national guidance ×10, …) | 40 |
| SoKs and surveys (one or two per X-class) | ≈ 20 |
| Incident and vulnerability write-ups with E4/E5 evidence, at least 1 per TT where one exists | ≈ 30 |
| Recent (≤ 6 months) high-impact attacks, refreshed each month | ≈ 20 |
| **Floors** | ≥ 5 deep items per X-class; ≥ 3 per TT with any E3+ evidence |

The current `extractions/` unit list in LANES.md (about 25 units) is the first
slice of this set, unchanged.

---

## 6. Work split, throughput, and a gate that gets people moving

### 6.1 Why round-1 lanes stalled (evidence: 1 of 5 calibrations done in about 3 weeks; #134-#136 re-cut on 10-21)

1. **The first task was the hardest.** Calibration began with NIST AI 100-2, a long taxonomy document, before anyone had done an easy paper.
2. **There was a convoy gate.** WAVE 2 waited for all five lanes to converge, so any one slow lane blocked everyone, and there was no individual signal of "you're done".
3. **The setup tax was heavy.** Students needed two repos, worktrees, a 660 MB PDF cache, library skills that load only from the library root, and tmodel workflows from the tmodel root.
4. **Done criteria were ambiguous and needed expert judgement.** `bears_on` needed DEC/R ids from ARCH-0001. Applicability ratings and reference expansion were open-ended.
5. **Instructions churned.** WAVE 1 vs WAVE 2 changed mid-stream (10-03 → 10-05), the issue text carried competing instructions, and there was no single worked example to copy until `c6cd1e0`.
6. **The units were too big for the token budget.** Max-effort extraction ran "several hundred thousand tokens" per unit, so students' plans hit limits mid-unit.
7. **The review dependency was unclear.** Each student's work needed a partner's review before it counted.

### 6.2 Fixes

- **Unit = one reference.** Each one comes from `tools/rpt0014/next`, which does setup, prefill and PDF fetch in one command and prints a 6-item checklist. No worktree is needed for library work: one branch per batch of 5.
- **Golden examples first.** The integration lane publishes **3 fully worked references** before students start: one paper (Greshake), one CVE/vendor write-up, one catalog entry. Each has `record.yaml`, `summary.md` and `ai-profile.yaml`, plus a "why each field is what it is" commentary. The agentic-mcp calibration records are the starting point.
- **Calibration is rolling and per person, not a five-way convoy.**
  - Each student's **first 5 references** are double-coded by the integration lane (AI + human).
  - **Individual gate:** field agreement ≥ 0.7 on TT, AIT and evidence. Passing it gives "cleared for L1 at 10% sampling".
  - Failing it gives feedback within 48 h and 5 more references.
  - Nobody waits for anyone else.
- **Done criteria are machine-checked:**
  - `bin/validate` passes;
  - `check-ai-profile` passes;
  - every `stated` field has a locator;
  - `reviewed_by` is set on the 5 partner-sampled items;
  - the PR is titled with the issue number.
  - **Students never set `bears_on`.** The integration lane does.
- **Batches of 5 per PR** within a 1-week timebox. A PR with 3 done and 2 marked `blocked: <reason>` is a success.
- **Throughput dashboard:** `coverage.md` shows per-lane counts by status, so progress is visible each week.
- **Deep units are separate.** They are optional for a student until cleared for L1, and run at most one at a time.
- **Office hour:** 30 minutes twice a week, with the integration lane pairing live on the first reference.

### 6.3 Lanes (keep the owners and issues #78-#82; add a target-type axis)

| Lane | X-classes | TT focus | Social/news channel it owns | Weekly target (after week 2) |
|---|---|---|---|---|
| agentic-mcp (#78) | X08, X10, X11, X12 | TT06-TT12, TT10 | Bluesky + HN | 25 L1 + 2 D |
| catalogs-schema (#79) | catalog crosswalk; X15 | all (catalog pins) | Catalog watch, OWASP/ATLAS diff | 15 L1 + 2 D (FX-TM) + catalog pin upkeep |
| supply-chain-infra (#80) | X03, X06, X07, X13 | TT13, TT14, TT17, TT18 | cvelist/GHSA/OSV/KEV + vendor RSS | 25 L1 + 2 D |
| ml-risk-assets (#81) | X01, X02, X04, X05, X09, X16 | TT01-TT05, TT15, TT16, TT19-TT25 | arXiv delta + Mastodon | 25 L1 + 2 D |
| integration (#82) | X14, cross-cutting | TT26, TT27 | X API, GDELT, AIID snapshot, critic rounds | Runs L0 batches (200-300/week), triage, sampling review, ids, coverage, report delta |

**Realistic team throughput** at about 8-10 student hours/week each:

- about **90 L1 per week**;
- about **8 deep units per week**;
- about **250 L0 per week** automated.

### 6.4 Seven-week schedule (2026-10-27 → 2026-12-12)

| Week | Goal |
|---|---|
| W1 (10-27) | Integration lane builds `next`, `prefill`, `ident`, `check-ai-profile` and harvesters for arxiv, cvelist, KEV, RSS, Bluesky and HN; lands the DX-AI/1 schema PR in the library and the 3 golden examples; gets OpenAlex, S2 and NVD keys; sets up the X account with a cap. Students set up and do their first 2 references. |
| W2 | Students finish their 5 calibration references (individual gate). L0 batch over the round-1 corpus begins. DBLP-dump TOC sweep for the top-4 venues and SaTML. |
| W3-W4 | L1 at full rate; the first 20 deep units; seed-set recall (NIST, ATLAS, OWASP); critic round 1; first `coverage.md`. |
| W5-W6 | Snowball closure; ML/NLP venue sweeps; non-English pass; critic round 2; weekly latest-attacks loop steady. |
| W7 | Critic round 3 / holdout reveal; report v0.3.0 with the coverage section; decide whether round 2 passes. |

**Expected state at W7:**

- L0 for about 2,500-3,000 references;
- L1 for about 450-550;
- deep for about 50-60.

The deep target of 200-250 carries into next term at about 8/week. Say this to
the sponsor up front rather than promising all deep work this term.

### 6.5 Risks

| Risk | Mitigation |
|---|---|
| L0 output mistaken for reviewed work | The validator renders a "HYPOTHESIS" badge when `reviewed_by` is empty; R-018 |
| X costs creep | `x-budget` hard stop; review monthly |
| DBLP challenge also blocks the dump | Fall back to OpenAlex/Crossref TOCs |
| Taxonomy churn (TT, AIT) mid-round | Freeze TT v1 at the end of W1; changes only through a PR with remap scripts |
| Public-repo licensing | Quote checker plus the license field are mandatory before merge |
| Student names in published pages | The identity guard already in tmodel (publishing-privacy rule) |
