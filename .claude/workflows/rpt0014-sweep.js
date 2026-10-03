export const meta = {
  name: 'rpt0014-sweep',
  description: 'RPT-0014 round 2 (#72): systematic gap sweeps (venues, arXiv, news, national, round-1 critic gaps) into round2/, each adversarially spot-checked',
  whenToUse: 'A student runs their assigned sweep from their lane issue. args: {sweeps: ["news-2026"], pdf: "~/tmodel-pdf-cache/ai-threat-model", today: "YYYY-MM-DD"}',
  phases: [
    { title: 'Sweep', detail: 'one agent per sweep' },
    { title: 'Check', detail: 'adversarial spot-check per sweep' },
  ],
}
const R = 'research/0014-ai-threat-model'
const O = `${R}/round2`
const PDF = (args && args.pdf) || '~/tmodel-pdf-cache/ai-threat-model'
const TODAY = (args && args.today) || 'today'

const SWEEPS = {
  'venues-security': `SYSTEMATIC TOP-VENUE SWEEP, security venues: IEEE S&P, USENIX Security, ACM CCS and NDSS, 2018-2026 (plus AsiaCCS, EuroS&P and ACSAC 2023-2026). List EVERY paper from the DBLP tables of contents, keyword-filter for AI/ML/LLM/agent security, then judge each by title and abstract. Write the FULL candidate list to ${O}/venues-security.csv (venue, year, title, doi, arxiv, in_corpus S-id or blank, relevance 1-3). Write source blocks for every relevance-3 paper not in the corpus, plus relevance-2 papers with more than 50 OpenAlex citations. Report coverage before and after. File: ${O}/venues-security.md`,
  'venues-ml': `SYSTEMATIC TOP-VENUE SWEEP, ML and NLP venues: NeurIPS (including the Datasets and Benchmarks track), ICML, ICLR, ACL, EMNLP, NAACL, SaTML, and security-relevant CVPR, ICCV and ECCV papers, 2018-2026. Use DBLP, the OpenReview API and OpenAlex. Write the full candidate CSV to ${O}/venues-ml.csv (venue, year, title, doi, arxiv, in_corpus, relevance), then source blocks for missing high-relevance and high-citation papers. File: ${O}/venues-ml.md`,
  'arxiv-2025-2026': `ARXIV HARVEST, 2025-01 to ${TODAY}: cs.CR, cs.LG, cs.CL and cs.AI papers on attacks on LLMs, agents, RAG, MCP, multimodal and diffusion models, the model supply chain, AI infrastructure and AI-enabled offense. Rank by OpenAlex or Semantic Scholar citations and by venue acceptance. Write the full candidate list to ${O}/arxiv-harvest.csv, and source blocks for the top missing papers (80-150), especially Jul-Oct 2026. File: ${O}/arxiv-2025-2026.md`,
  'news-2026': `NEWS AND INCIDENTS, 2026-06-01 to ${TODAY}, plus a back-check of 2024-2026 for missed major incidents. Use GDELT DOC 2.0, HN Algolia, NVD (keywords LLM, agent, MCP, Ollama, vLLM, LangChain, Langflow, and similar), CISA KEV, and vendor advisories (MSRC, Google, GitHub, OpenAI, Anthropic, Salesforce). Write incident blocks with primary sources. Also re-fetch, via the Wayback Machine, the primary sources that refused fetch in round 1 (grep report.md and sources.md for "403" or "not read"), and record what they confirm or correct. File: ${O}/news-2026.md`,
  'national-intl': `NON-US AND NON-ENGLISH GUIDANCE AND STANDARDS. Cover: China (TC260 framework 2.0, GB/T AI security standards, CAC rules, major Chinese LLM-security research groups); Japan (AISI, METI, IPA); Korea (KISA); Singapore (CSA, AI Verify, IMDA agentic framework); the EU (ENISA; AI Act Art. 15 harmonised standards, including prEN 18282; CEN-CENELEC JTC 21); Germany (BSI AIC4 and the LLM papers); France (ANSSI); the UK (NCSC, AISI, the Code of Practice, ETSI); Australia (ASD); Canada; India (CERT-In); Israel (INCD). Also ISO/IEC 27090, 27091, 42001, 23894, 5338, PAS 8800 and 12792, and IEEE P3119 and P2986. Record each document's status, its threat content and its threat list where present. File: ${O}/national-intl.md`,
  'critic-gaps': `CLOSE THE ROUND-1 CRITIC GAPS listed in ${O}/round1-critic-gaps.json (58 gaps). For each gap, grep sources.md to see whether it is covered. Write ${O}/critic-gaps-status.csv (gap index, area, status closed, partial or open, S-ids), then find and write the missing sources for every open or partial gap. File: ${O}/critic-gaps.md`,
}
const want = (args && args.sweeps) || []
const bad = want.filter(s => !SWEEPS[s])
if (bad.length || !want.length) throw new Error(`pass args.sweeps from: ${Object.keys(SWEEPS).join(', ')}`)

const COMMON = `You are a GAP-SWEEP agent, round 2 of RPT-0014 (Threat-Radar/tmodel #71/#72). Work from the repository root. The round-1 corpus is ${R}/sources.md (S-0001..S-1181), incidents.md, threat-models.md, attack-catalog.yaml and report.md (see its Method / Limits).
Search: use WebSearch and WebFetch (load them with ToolSearch "select:WebSearch,WebFetch"). If WebSearch is refused for quota, stop retrying it and use the APIs: DBLP (https://dblp.org/search/publ/api?q=...&format=json&h=1000, plus venue TOC pages), OpenAlex (https://api.openalex.org/works?search=...), Semantic Scholar, the arXiv API, Crossref, NVD, CISA KEV, GitHub, GDELT DOC 2.0 (https://api.gdeltproject.org/api/v2/doc/doc?query=...&mode=artlist&format=json), HN Algolia, and the Wayback Machine. Sleep 1-3 s between calls and back off on 429.
DEDUPE against sources.md (arXiv id, DOI, title fragment) before adding. Never invent a citation: every entry is confirmed by a fetched record, with its URL. Recalled details cap confidence at medium. Vendor claims are recorded as claims.
Do NOT assign S-, INC-, TM- or AIT- ids and do NOT edit the round-1 files; the integration lane (nymble) assigns ids and merges. Important new PDFs go ONLY to ${PDF}/: record the file name, sha256 and URL in ${O}/pdf-additions.tsv (append, tab-separated: file, sha256, url). Never put a PDF in the repo.
Block format: "### <kebab-id> - <short title>" with these bullets: citation, type, confirmed_via, pdf, attack_classes, summary (3-6 technical sentences: attack, attacker access and knowledge, target asset or component, impact, defenses, key numbers), threat_model_mapping (asset -> threat -> precondition -> impact), catalog_ids (ATLAS 2026.09, OWASP LLM:2025 or ASI:2026, CWE 4.20, NIST AI 100-2 E2025), confidence; incidents add date, kind (ITW, ITW-Q, DV, LEG) and primary_source. End with "## Search log" (a table) and "## Still open". Today is ${TODAY}.`

phase('Sweep')
const res = await pipeline(want,
  s => agent(`${COMMON}\n\n${SWEEPS[s]}\nRETURN: the count of new items, the coverage statistics, and what is still open.`, { label: `sweep:${s}`, phase: 'Sweep', effort: 'high' }),
  (r, s) => agent(`${COMMON}\n\nYou are an ADVERSARIAL CHECKER for the ${s} sweep output in ${O}/ (task: ${SWEEPS[s]}). Assume it is wrong and incomplete. (1) Fetch the URLs of 25 random new entries and check the title, authors, year, venue and claims; fix or delete bad ones. (2) Check that no entry duplicates sources.md. (3) Measure the filter's recall by hand on one sample (one venue-year table of contents, one news week, or one country) and add what the filter missed. (4) Put the findings in a "## Check" section at the end of the file. RETURN: the defects found and fixed, and the residual issues. Sweep agent's report: ${String(r).slice(0, 2500)}`, { label: `check:${s}`, phase: 'Check', effort: 'max' }).then(c => ({ sweep: s, report: String(r).slice(0, 1500), check: c })))
return res.filter(Boolean)
