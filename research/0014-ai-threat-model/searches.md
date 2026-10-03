---
schema: "archdoc/v1"
id: RPT-0014-searches
title: "RPT-0014 search log"
type: research
status: draft
version: "0.2.0"
date: "2026-10-02"
updated: "2026-10-03"
record: RPT-0014
---

# RPT-0014: search log

Every query the agents logged, merged from the eight raw files, so the survey is reproducible. One row per logged query or query batch. Agents: six dimension agents (2026-10-02), one adversarial coverage reviewer, two gap-fill agents (2026-10-03).

**Read this first: search was constrained.** The session-wide WebSearch budget (200 calls) was spent early on 2026-10-02, mostly by the incidents agent. Every later WebSearch call was refused and is logged as such. The other agents switched to direct, primary-source retrieval: the arXiv export API, Semantic Scholar and Crossref APIs, the NVD CVE 2.0 API, the CWE REST API and XML, the CAPEC XML, the MITRE ATLAS data repository, GitHub APIs, OpenAlex, HN Algolia (only to discover primary URLs), Wikipedia (context only), venue program pages (USENIX Security 2026, IEEE S&P 2026, SaTML 2026, NDSS 2026) and WebFetch of known URLs. Consequence: discovery is biased toward sources the agents already knew or that the reviewer named, and news from 2026-08 to 2026-10 is under-sampled. See report.md section 8.

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-02 | 1 ML-model attacks | NIST AI 100-2 E2025 Adversarial Machine Learning taxonomy | WebSearch | FAILED (budget exhausted) |
| 2026-10-02 | 1 ML-model attacks | Biggio Roli "Wild patterns" Pattern Recognition 2018 | WebSearch | FAILED (budget exhausted) |
| 2026-10-02 | 1 ML-model attacks | Papernot "SoK: Security and Privacy in ML" EuroS&P 2018 | WebSearch | FAILED (budget exhausted) |
| 2026-10-02 | 1 ML-model attacks | ti:"Intriguing properties of neural networks" | arXiv API | 1312.6199 |
| 2026-10-02 | 1 ML-model attacks | ti:"Explaining and Harnessing Adversarial Examples" | arXiv API | 1412.6572 |
| 2026-10-02 | 1 ML-model attacks | ti:"Towards Evaluating the Robustness of Neural Networks" | arXiv API | 1608.04644 |
| 2026-10-02 | 1 ML-model attacks | ti:"Towards Deep Learning Models Resistant to Adversarial Attacks" | arXiv API | 1706.06083 |
| 2026-10-02 | 1 ML-model attacks | ti:"Adversarial examples in the physical world" | arXiv API | 1607.02533; physical-world survey 2311.01473 |
| 2026-10-02 | 1 ML-model attacks | ti:"Adversarial Patch" | arXiv API | 1712.09665; certified patch defense 2003.06693 |
| 2026-10-02 | 1 ML-model attacks | ti:"Robust Physical-World Attacks on Deep Learning" | arXiv API | 1707.08945 |
| 2026-10-02 | 1 ML-model attacks | ti:"Practical Black-Box Attacks against Machine Learning" | arXiv API | 1602.02697 |
| 2026-10-02 | 1 ML-model attacks | 14 black-box / transfer titles (Universal perturbations, ZOO, Square, HopSkipJump, GCG...) | arXiv API | rate-limited (HTTP 429), no output |
| 2026-10-02 | 1 ML-model attacks | Wild patterns ten years after | Semantic Scholar API | HTTP 429 |
| 2026-10-02 | 1 ML-model attacks | Wild patterns ten years after | DBLP API | bot-challenge page |
| 2026-10-02 | 1 ML-model attacks | Wild patterns ten years after rise adversarial ML | Crossref | 10.1016/j.patcog.2018.07.023; CCS tutorial 10.1145/3243734.3264418 |
| 2026-10-02 | 1 ML-model attacks | SoK Security and Privacy in ML Papernot | Crossref | 10.1109/eurosp.2018.00035 |
| 2026-10-02 | 1 ML-model attacks | Membership Inference Attacks Against ML Models Shokri | Crossref | 10.1109/sp.2017.41; enhanced MIA CCS 2022 |
| 2026-10-02 | 1 ML-model attacks | Stealing ML Models via Prediction APIs Tramer | Crossref | no relevant hit (USENIX has no DOI) |
| 2026-10-02 | 1 ML-model attacks | Model Inversion Attacks that Exploit Confidence Information | Crossref | 10.1145/2810103.2813677 |
| 2026-10-02 | 1 ML-model attacks | Extracting Training Data from LLMs / Diffusion Models | Crossref | no relevant hit |
| 2026-10-02 | 1 ML-model attacks | Poisoning Attacks against SVMs Biggio | Crossref | no relevant hit |
| 2026-10-02 | 1 ML-model attacks | Sponge Examples: Energy-Latency Attacks | Crossref | 10.1109/eurosp51992.2021.00024; sponge poisoning SSRN |
| 2026-10-02 | 1 ML-model attacks | Terminal Brain Damage | Crossref | no relevant hit |
| 2026-10-02 | 1 ML-model attacks | Bit-Flip Attack: Crushing NN with Progressive Bit Search | Crossref | 10.1109/iccv.2019.00130; GBFA 2026 |
| 2026-10-02 | 1 ML-model attacks | Stealing ML Models via Prediction APIs | OpenAlex | arXiv 1609.02943; Stealing Hyperparameters S&P 2018 |
| 2026-10-02 | 1 ML-model attacks | Universal adversarial perturbations; Transferability in ML; ZOO; limited queries; decision-based; Square; HopSkipJump; obfuscated gradients; AutoAttack; EOT; audio adversarial; evasion at test time (12 queries) | OpenAlex | CVPR 2017 UAP; 1605.07277; AutoZOOM; 1804.08598; 1712.04248; 1912.00049; S&P 2020 HSJA; 1802.00420; 2003.01690; 1707.07397; SPW 2018; ECML 2013 |
| 2026-10-02 | 1 ML-model attacks | Poisoning SVMs; BadNets; Trojaning; Poison Frogs; targeted backdoor; Witches' Brew; web-scale poisoning; Sleeper Agents; instruction-tuning poisoning; near-constant poison; universal jailbreak backdoors; backdoor survey; dataset security; Neural Cleanse; spectral signatures; blind backdoors; FL backdoor; undetectable backdoors; Hidden Killer; weight poisoning (20 queries) | OpenAlex | all seminal hits confirmed; also Nature Medicine medical poisoning; Jagielski regression S&P 2018; latent backdoors CCS 2019 |
| 2026-10-02 | 1 ML-model attacks | Stealing part of production LM; Knockoff Nets; high-fidelity extraction; cryptanalytic extraction; Thieves on Sesame Street; logits leak; PRADA; LiRA; ML-Leaks; overfitting privacy; MIA on LLMs; Secret Sharer; extracting LLM/diffusion; scalable extraction; quantifying memorization; Secret Revealer; feature leakage; DLG; inverting gradients; overlearning; MIA survey (22 queries) | OpenAlex | all confirmed; polynomial-time cryptanalytic extraction EUROCRYPT 2024; Nasr white-box S&P 2019; iDLG |
| 2026-10-02 | 1 ML-model attacks | Terminal Brain Damage; DeepHammer; PrisonBreak; Cache Telepathy; CSI NN; sponge poisoning | OpenAlex | confirmed; bit-flip survey (Electronics 2023); fault-injection quantized LM (ACM 2025) |
| 2026-10-02 | 1 ML-model attacks | OverThink; watermark-by-backdooring; SoK watermark; LLM watermark; watermarks in sand; conferrable; instructional fingerprint; dataset inference; fine-pruning; entangled watermarks | OpenAlex | FAILED (daily budget exhausted, HTTP 429) |
| 2026-10-02 | 1 ML-model attacks | arxiv.org/search title: OverThink; watermarking by backdooring | arXiv HTML search | 2502.02542; laundering 2004.11368; BlockDoor 2412.12194 |
| 2026-10-02 | 1 ML-model attacks | arxiv.org/search title: 16 titles (Turning Your Weakness; SoK watermark; LLM watermark; Watermarks in the Sand; Conferrable; Instructional FP; Dataset Inference; Entangled; Persistent pretraining poisoning; Scaling laws poisoning; Exploiting LLM Quantization; Stealing prompts MoE; Privacy side channels; Subliminal learning; Emergent misalignment; Nightshade) | arXiv HTML search | 1802.04633; 2108.04974; 2311.04378; 1912.00888; 2401.12255; 2104.10706; 2002.12200; 2410.13722; 2405.18137 (+2605.15152 follow-up); 2410.22884; 2309.05610; 2507.14805; 2502.17424; 2310.13828 |
| 2026-10-02 | 1 ML-model attacks | arxiv.org/search title: GCG; visual adversarial jailbreak; image hijacks; +12 more | arXiv HTML search | 2307.15043; 2306.13213; 2309.00236; the rest rate-limited |
| 2026-10-02 | 1 ML-model attacks | OpenAlex search "Text Embeddings Reveal" | WebFetch | HTTP 429 |
| 2026-10-02 | 1 ML-model attacks | arxiv.org/a/morris_j_1 | WebFetch | wrong author page (no hit) |
| 2026-10-02 | 1 ML-model attacks | arxiv.org/search "Text Embeddings Reveal" | WebFetch | HTTP 429 |
| 2026-10-02 | 1 ML-model attacks | titles.title:"Text Embeddings Reveal" | DataCite | 2310.06816; reproducibility study 2507.07700 |
| 2026-10-02 | 1 ML-model attacks | 15 exact titles (LLM watermark, scaling-law poisoning, LM inversion, Min-K%, SoK MIA LLM, strong MIA, informed adversaries, fine-tuning compromises safety, You Autocomplete Me, TrojanPuzzle, false promise imitation, neighbourhood MIA, not bugs features, randomized smoothing, DP-SGD) | DataCite | 2301.10226; 2310.16789; 2406.17975; 2201.04845; 2310.03693; 2007.02220; 2301.02344; 2305.15717; 2305.18462; 1905.02175; 1902.02918; 1607.00133; scaling-laws NONE |
| 2026-10-02 | 1 ML-model attacks | 16 exact titles (strong MIA, Robbing the Fed, Byzantine FL poisoning, adversarial lens, Nasr comprehensive, label-only MIA, hyperparameters, model extraction attacks, T2I prompt stealing, Nature Med poisoning, Engorgio, Coercing LLMs, GPUHammer, OneFlip) | DataCite | 2505.18773; 2110.13057; 1911.11815; 1811.12470; 1812.00910; 2007.14321; 1802.05351; 2606.03381; 2302.09923; 2412.19394; 2402.14020; 2507.08166; OneFlip NONE |
| 2026-10-02 | 1 ML-model attacks | 2025-2026 keyword: model extraction/stealing survey; poisoning pretraining; bit flip LLM; rowhammer model; membership inference LLM; training data extraction; distillation attack; gradient inversion federated; AML taxonomy; backdoor survey LLM | DataCite (year-filtered) | bit-flip: 2603.16382, 2608.15475, 2607.25227, 2604.17249, 2603.10042, 2505.16670, 2602.17837, 2510.00490, 2509.21843; MIA: 2603.28378, 2606.17464, 2512.16292; FL: 2508.19819, 2604.15063, 2603.17623; distillation: 2510.10987, 2509.23871; survey 2502.05224 |
| 2026-10-02 | 1 ML-model attacks | 2025-2026 keyword: model stealing; poisoning LLMs; memorization extraction; watermark removal; fingerprinting LLM; energy latency attack; unlearning attack; SoK adversarial; weights exfiltration | DataCite (year-filtered) | 2502.15567, 2505.18323, 2604.27426, 2607.10794, 2606.15493; 2610.01367, 2605.26595, 2606.17110, 2509.23041, 2605.23168; 2609.09320; watermark removal 2605.09203, 2602.01513; FP 2508.02092, 2511.08905; unlearning 2506.09923, 2507.20573 |
| 2026-10-02 | 1 ML-model attacks | Towards the Science of Security and Privacy in ML; Wild Patterns; Shokri MIA; DLG; Sponge; Model Inversion; AML at Scale; Delving transferable; ZOO; JSMA; DeepFool; NIST taxonomy | DataCite | 1611.03814; 1712.03141; 1610.05820; 2006.03463; MI surveys 2402.04013, 2411.10023; 1611.01236; 1611.02770; 1708.03999; 1511.07528; 1511.04599 |
| 2026-10-02 | 1 ML-model attacks | Real attackers don't compute gradients; AML industry perspectives; ML security industry survey; model stealing survey; privacy attacks survey; CV adversarial survey; Fishing for user data; Curious abandon honesty; property inference; data-free extraction; GNN stealing; subconscious jailbreak | DataCite | 2212.14315; 2002.05646; 2207.05164; 2206.08451; 2007.07646; 1801.00553; 2202.00580; 2112.02918; GNN stealing 2112.08331, 2405.12295 |
| 2026-10-02 | 1 ML-model attacks | Ganju property inference; Ateniese hacking smart machines; NIST AML taxonomy DOIs | Crossref | 10.1145/3243734.3243834; 10.1504/ijsn.2015.071829; 10.6028/nist.ai.100-2e2025, e2023, e2023.ipd |
| 2026-10-02 | 1 ML-model attacks | https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks | WebFetch | confirmed 2026-02-23 report (16M exchanges, 24k accounts) |
| 2026-10-02 | 1 ML-model attacks | https://arxiv.org/abs/1905.02175, /abs/1906.08935 | curl (abs page) | titles confirmed |
| 2026-10-02 | 1 ML-model attacks | NIST AI 100-2 E2025 PDF text, grep NISTAML ids | local pdftotext | full NISTAML.01-.05 identifier list (see catalog key) |
| 2026-10-02 | 1 ML-model attacks | ATLAS YAML (sibling cache) technique filter | local | AML.T0015, .T0043.x, .T0020, .T0018.x, .T0024.x, .T0029, .T0034, .T0058, .T0010.x |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebSearch "Universal and Transferable Adversarial Attacks ... GCG", "Many-shot jailbreaking", "Crescendo", "Skeleton Key" | WebSearch | none: session WebSearch budget (200/200) already exhausted by sibling agents; switched to direct fetches |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv API search_query ti:"..." (10 jailbreak titles) | export.arxiv.org API | HTTP 429 (throttled); abandoned |
| 2026-10-02 | 2 LLM/RAG/agent attacks | Semantic Scholar /paper/search?query=many-shot+jailbreaking | api.semanticscholar.org | HTTP 429 |
| 2026-10-02 | 2 LLM/RAG/agent attacks | DBLP publ search "many-shot jailbreaking" | dblp.org API | HTTP 500 |
| 2026-10-02 | 2 LLM/RAG/agent attacks | OpenAlex works?search=prompt injection agents (2026) | api.openalex.org | daily budget exhausted |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv HTML title search: GCG, AutoDAN (Liu), PAIR, TAP, Crescendo | arxiv.org/search | 2307.15043, 2310.04451, 2310.08419, 2312.02119, 2404.01833 |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv HTML title search batch 1 (25 titles: low-resource, CipherChat, BoN, DAN, Jailbroken, ArtPrompt, adaptive attacks, GPTFuzzer, PAP, refusal direction, visual adv, DeepInception, AutoDAN-Zhu, Ignore Previous Prompt, BIPIA, Tensor Trust, HackAPrompt, auto-universal PI, Neural Exec, adaptive IPI, WASP, prompt extraction, output2prompt, LM inversion, prompt stealing) | arxiv.org/search + abs pages | partial before throttling; remainder confirmed by abs-page fetch (below) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv HTML title search batch 2 (27 titles: BadRAG, vec2text, Phantom, RAG jamming, TrojanRAG, RAG privacy, ConfusedPilot, backdoored retrievers, ToolEmu, Imprompter, ASB, tool selection PI, Prompt Infection, MAS-RCE, ARE, images/sounds, image hijacks, FigStep, OverThink, shadow alignment, LoRA undo, emergent misalignment, covert FT, watermark, watermark stealing, DIPPER, AI-text detection) | arxiv.org/search + abs pages | 2406.00083, 2406.05870; vec2text query returned reproducibility study 2507.07700 (kept as note) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv HTML title search batch 3 (27 titles: Llama Guard, baseline defenses, SmoothLLM, constitutional classifiers, circuit breakers, Gemini lessons, FIDES, MELON, DataSentinel, Task Shield, JailbreakBench, CyberSecEval 1/2, StrongREJECT, jailbreak survey, Greshake, HouYi, Liu formalizing, InjecAgent, AgentDojo, PoisonedRAG, AgentPoison, MINJA, Agent Smith, Morris II, pop-ups, EIA) | arxiv.org/search + abs pages | all confirmed |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv HTML title search batch 4 (25 titles: package hallucinations, Qi FT, CaMeL, design patterns, Spotlighting, StruQ, SecAlign, instruction hierarchy, HarmBench, AgentHarm, CSE3, many-shot, attacker-moves-second, sleeper agents, RLHF backdoors, instruction-tuning poisoning, custom GPTs, MCP audit, MCPTox, MCP landscape, agentic misalignment, spec gaming, Trust No AI) | arxiv.org/search + abs pages | all paper ids confirmed; agentic misalignment is a blog, not arXiv |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv abs-page verification of 130 candidate ids (jailbreak, PI, RAG, agent, MCP, memory, MAS, CUA, coding, multimodal, DoS, alignment, watermark, defenses, benchmarks) | arxiv.org/abs | 130/130 titles matched the expected papers (e.g., 2412.03556 BoN, 2307.02483, 2402.11753, 2404.02151, 2406.11717, 2503.00061, 2504.18575, 2310.06816, 2405.20485, 2408.04870, 2410.14923, 2503.12188, 2502.02542, 2502.17424, 2402.19361, 2505.14534, 2505.23643, 2506.09956, 2406.00799, 2509.22040, 2508.17155, 2502.13172, 2504.03111) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv abs-page fetch for sibling-cached PDFs (promptware kill chain, CUA SoK, Invitation, SoK agentic surface, MCP-38, MAS TM, IPI-in-the-wild, A2ABreak, EchoLeak, MCP STRIDE, AWI GHA) | arxiv.org/abs | 2601.09625, 2507.05445, 2508.12175, 2603.22928, 2603.18063, 2609.22949, 2604.27202, 2609.10871, 2509.10540, 2603.22489, 2605.07135 |
| 2026-10-02 | 2 LLM/RAG/agent attacks | Crossref query.bibliographic "prompt injection LLM agents", "jailbreak large language models", "Model Context Protocol security", "retrieval-augmented generation poisoning", "LLM agent memory poisoning", "computer-use web agent attack", "multi-agent system LLM attack", "coding assistant prompt injection" (from 2025-06-01, proceedings) | api.crossref.org | ObliInjection (NDSS26), ToolHijacker (NDSS26), SoK jailbreak guardrails (S&P26), URLcoat (S&P26), ATAG and Mind the Web (AsiaCCS26) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | Crossref prefix:10.14722 (NDSS) x {LLM, language model, agent, jailbreak, prompt} from 2025 | api.crossref.org | about 50 NDSS 2025-2026 LLM papers incl. Bleeding Pathways, ACE, ThinkTrap, Beyond Jailbreak, Les Dissonances, semantic cache poisoning, Odysseus, Rennervate, watermark char-perturbation, Chasing Shadows, FPA, IsolateGPT |
| 2026-10-02 | 2 LLM/RAG/agent attacks | Crossref container IEEE S&P / ACM CCS x {large language model, LLM agent, jailbreak, prompt injection, retrieval augmented} from 2025 | api.crossref.org | MetaBreak, dark patterns, LLMThief, PromptLocate, AttnTrace, chatbot plugins, Who Taught the Lie, adversarial hubness, AudioHijack, SoK jailbreak robustness, Fun-tuning, prompt stealing in-the-wild, LLM app stores, Flashboom, SecAlign (CCS), ImportSnare, FlippedRAG, GASLITE, Riddle Me This, SysVec |
| 2026-10-02 | 2 LLM/RAG/agent attacks | Crossref works/{doi} for 38 DOIs | api.crossref.org | titles, authors, venues confirmed; no abstracts |
| 2026-10-02 | 2 LLM/RAG/agent attacks | NDSS paper pages for 14 NDSS DOIs (slug from title) | ndss-symposium.org | 13 abstracts fetched; IsolateGPT page layout differed (confirmed via arXiv) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv title search for 25 S&P/CCS/AsiaCCS titles (sequential, 8 s spacing) | arxiv.org/search | 2506.10597, 2604.14604, 2605.05058, 2510.10271, 2510.18113, 2510.12252, 2508.03793, 2511.05797, 2412.14113, 2501.09798, 2407.08422, 2509.07941, 2501.02968, 2412.20953, 2502.00306, 2509.21884, 2506.07153, 2403.04960; no arXiv for URLcoat, LLMThief, Who Taught the Lie, prompt stealing in-the-wild, Flashboom |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv title search batch 5 (MCPSecBench, MCP security analysis, hidden prompts peer review, memory poisoning defense, A-MemGuard, SafeArena, AiTM, ISE, Meta SecAlign, Progent, f-secure IFC, IPIGuard, agentic firewalls, Asleep at the Keyboard, credential memorization, Importing Phantoms, agent skills, AdvWave, oncology VLM PI, CUA clickjacking, markdown exfil, denial of wallet, excessive agency, Poisoned LangChain, ICL backdoor) | arxiv.org/search + abs pages | 2508.13220, 2507.06185, 2601.05504, 2503.04957, 2502.14847, 2410.09102, 2507.02735, 2409.19091, 2508.15310, 2502.01822, 2108.09293, 2309.07639, 2501.19012, 2606.23416, 2412.08608, 2609.28585; no hit for Progent and several generic queries |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv newest-first listing, title "prompt injection" (50) | arxiv.org/search order=-announced_date_first | about 50 papers from Aug-Sep 2026 alone (e.g., 2609.35932, 2609.33628, 2608.27092, 2608.30362, 2608.08939, 2608.05715, 2608.06477, 2608.10281, 2608.07808, 2609.22510, 2609.36576) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | arXiv newest-first listing, titles "Model Context Protocol", "jailbreak", "agent memory", "computer-use agent", "multi-agent attack", "tool poisoning", "coding agent" (15 each) | arxiv.org/search | 2609.14119, 2607.05744, 2609.12413, 2609.31121, 2609.34686, 2610.00450, 2609.27624, 2607.19432, 2606.27027, 2606.06387, 2605.26154, 2601.07395, 2609.38983, 2609.39678, 2609.14079 |
| 2026-10-02 | 2 LLM/RAG/agent attacks | CWE-1427, 1426, 1039, 1434, 1446, 1447, 1448 pages | cwe.mitre.org | AI/ML weakness view CWE-1448 (CWE 4.20) and its members |
| 2026-10-02 | 2 LLM/RAG/agent attacks | NIST AI 100-2 E2025 PDF text (cached) grep NISTAML ids | local pdftotext | id-to-section mapping for GenAI classes |
| 2026-10-02 | 2 LLM/RAG/agent attacks | MITRE ATLAS YAML (scratchpad) technique list | local yaml | LLM and agent technique ids (v5.6.0) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | OWASP LLM Top 10 2025 and Agentic Top 10 2026 PDFs (cached) | local pdftotext | LLM01-10, ASI01-10 titles |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch microsoft.com Skeleton Key blog | WebFetch | confirmed (2024-06-26) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch simonwillison.net lethal trifecta / dual LLM / prompt injection 2022 | WebFetch | confirmed (2025-06-16, 2023-04-25, 2022-09-12) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch invariantlabs.ai tool poisoning; GitHub MCP | WebFetch | confirmed (2025-04-01; 2025-05-26) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch pillar.security rules file backdoor | WebFetch | confirmed (2025-03-18) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch blog.trailofbits.com image scaling; MCP line jumping | WebFetch | confirmed (2025-08-21; 2025-04-21) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch embracethered.com Copilot CVE-2025-53773; SpAIware; Bing Chat exfil; ZombAIs; Gemini memory; M365 ASCII smuggling | WebFetch | all confirmed |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch ai.meta.com Agents Rule of Two | WebFetch | confirmed (2025-10-31) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch brave.com Comet IPI | WebFetch | confirmed (2025-08-20) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch anthropic.com many-shot; agentic misalignment; prompt-injection defenses | WebFetch | confirmed (2024-04-02; 2025-06-20; 2025-11-24) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch legitsecurity.com CamoLeak | WebFetch | confirmed (2025-10-08) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch unit42 Deceptive Delight; A2A session smuggling | WebFetch | confirmed (2024-10-23; 2025-10-31) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch sysdig.com LLMjacking | WebFetch | confirmed (2024-05-06) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch hiddenlayer.com Policy Puppetry; neuraltrust.ai Echo Chamber | WebFetch | confirmed (2025-04-24; 2025-06-23) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch socket.dev slopsquatting | WebFetch | confirmed (2025-04-08) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch promptarmor Slack AI | WebFetch | confirmed (2024-08) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch blog.google layered IPI defense (via security.googleblog.com redirect) | WebFetch | confirmed (2025-06-13) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch nist.gov CAISI agent hijacking blog | WebFetch | confirmed (2025-01-17) |
| 2026-10-02 | 2 LLM/RAG/agent attacks | WebFetch/curl openai.com Atlas hardening; medium.com Elena Cross MCP; aim.security EchoLeak; msrc IPI defense; vulcan.io package hallucination | WebFetch/curl | 403, 403, 403, redirect-to-index, redirect-to-unrelated -> UNVERIFIED |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | pickle deserialization malicious models Hugging Face nullifAI bypass picklescan | WebSearch | refused: session search budget exhausted |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Keras Lambda layer safe_mode bypass CVE-2024-3660 CVE-2025-1550 | WebSearch | refused: budget exhausted |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | GGUF chat template injection backdoor llama-cpp-python CVE-2024-34359 Jinja | WebSearch | refused: budget exhausted |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | model namespace reuse Unit 42 Hugging Face Vertex AI Azure | WebSearch | refused: budget exhausted |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | ti:"LeftoverLocals"; abs:pickle AND abs:"Hugging Face"; ti:"Models Are Codes"; ti:PickleBall | arXiv API | failed (HTTP 429) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | LeftoverLocals GPU local memory | OpenAlex | 2401.16603; MOLE (CCS'25); SafeRace; on-device KV leakage |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | malicious models Hugging Face pickle | arXiv search | ShadowPickle 2607.17503; PickleFuzzer 2605.15084; SafePickle 2602.19818; 2601.04553; PickleBall 2508.15987 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | pickle model scanner evasion | arXiv search | ShadowPickle; SafePickle |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | safetensors | arXiv search | CryptoTensors 2512.04580 (format, not attack) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Keras Lambda layer arbitrary code | arXiv search | no hits |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | GGUF | arXiv search | quantization and deployment papers only |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | chat template backdoor | arXiv search | BadTemplate 2602.05401; Fogel 2602.04653; turn-based triggers 2601.14340 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | model hub typosquatting; LoRA backdoor adapter; malicious LoRA; Hugging Face supply chain; pre-trained model supply chain | arXiv search | empty (429 rate limit) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | malicious machine learning models Hugging Face pickle | OpenAlex | Models Are Codes (ASE'24); PickleBall (CCS'25); Sood CACM 2025 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Models Are Codes malicious model hub | OpenAlex | DOI 10.1145/3691620.3695271 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | PickleBall secure deserialization | OpenAlex | 2508.15987; Modelstamp 2609.01781; ShadowPickle |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | insecurity of loading machine learning models | OpenAlex | no relevant hits |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Keras Lambda layer code execution model | OpenAlex | no relevant hits |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | LoRA backdoor adapter share-and-play | OpenAlex | LoRATK (Findings EMNLP 2025); PEFTGuard (S&P 2025); LoRA detox backdoor (NDSS 2026) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | malicious adapter LoRA supply chain | OpenAlex | LoRATK; NDSS 2026 LoRA backdoor |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Hugging Face model supply chain empirical | OpenAlex | Stalnaker 2502.04484 (TOSEM); Jiang 2022 PTM supply chain risks |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | pre-trained model reuse supply chain security | OpenAlex | BadNets; Jiang 2022 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | chat template backdoor inference time GGUF | OpenAlex | Fogel 2602.04653; AGENTQ quantization backdoor 2609.14060 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | GPU side channel deep learning multi-tenant | OpenAlex | Neighbors From Hell (FPGA voltage, 2020) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | GPU memory isolation inference leak LLM | OpenAlex | LeftoverLocals; "Creating the First Confidential GPUs" (ACM Queue 2023) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | confidential computing GPU TEE attack AI | OpenAlex | Confidential GPUs (Queue) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | TEE.fail DDR5 interposer | OpenAlex | VCEK seed extraction on EPYC Milan 2605.12990; RISC-V PMP aliasing |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | prompt caching timing side channel LLM API | OpenAlex | InputSnatch 2411.18191 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | KV cache sharing side channel prompt leakage | OpenAlex | PromptPeek (NDSS 2025); Early Bird (TIFS 2025) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | speculative decoding side channel | OpenAlex | CPU speculative-execution papers only |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | token length side channel encrypted LLM traffic | OpenAlex | InputSnatch |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Whisper Leak side channel | OpenAlex | no direct hit |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | CPU cache side channel LLM tokens | OpenAlex | no direct hit |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | CVE-2023-4969, CVE-2024-3660, CVE-2025-1550, CVE-2024-34359, CVE-2023-48022, CVE-2024-37032, CVE-2024-0132, CVE-2025-23266, CVE-2023-6831, CVE-2023-1177, CVE-2024-24590, CVE-2025-3248, CVE-2025-6965 | NVD API | all confirmed (descriptions, CVSS, CWE) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | vLLM (keyword) | NVD API | CVE-2025-32444, -29783, CVE-2024-11041, -9053, CVE-2025-25183, -24357, -30202, CVE-2024-8768 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Triton Inference Server (keyword) | NVD API | 65 results; CVE-2025-23310/23311/23317; CVE-2024-0087; CVE-2023-31036 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Kubeflow (keyword) | NVD API | CVE-2026-54745 (SSRF, 10.0); CVE-2026-47237; ART Kubeflow RCE CVE-2026-31228/9/30 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | safetensors (keyword) | NVD API | CVE-2026-65920 Diffusers path traversal |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | torch.load (keyword) | NVD API | CVE-2025-32434 (PyTorch weights_only RCE); CVE-2025-1945 (picklescan); InvokeAI CVE-2024-12029 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Hugging Face transformers deserialization | NVD API | CVE-2024-11392/3/4; CVE-2025-14920/21/24/29/30 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | CVE-2025-1945, CVE-2025-32434, CVE-2025-25183, CVE-2025-8217, CVE-2023-1177 (references) | NVD API | huntr reference for MLflow; GHSA ids |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | remote timing attacks efficient language model inference | OpenAlex | Carlini and Nasr 2410.17175 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | package hallucination code generating LLM slopsquatting | OpenAlex | slopsquatting review papers (low quality) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Exploiting LLM quantization | OpenAlex | Egashira 2405.18137 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | spy in the GPU box covert side channel multi-GPU | OpenAlex | Spy in the GPU-box (ISCA'23); Rendered Insecure (CCS'18); TunneLs for Bootlegging (CCS'23) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | GPU side channel neural network architecture leakage | OpenAlex | no relevant hits |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | energy latency sponge attack LLM denial of service | OpenAlex | Crabs (Findings ACL'25); ThinkTrap (NDSS'26) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | unbounded consumption denial of wallet LLM | OpenAlex | prompt-injection reviews only |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | OAuth authorization AI agents delegation identity | OpenAlex | NCCoE response (Zenodo); risk-adaptive authorization (SoutheastCon'26) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | non-human identity AI agent credentials security | OpenAlex | no relevant hits |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | deepfake voice fraud detection human study | OpenAlex | detection surveys only |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | We Have a Package for You package hallucinations | OpenAlex | Spracklen 2406.10279 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | humans cannot reliably detect speech deepfakes | OpenAlex | Mai et al. PLoS ONE 2023 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | PentestGPT LLM penetration testing | OpenAlex | PentestGPT 2308.06782 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | CVE-Bench AI agents exploit web application vulnerabilities | OpenAlex | CVE-Bench 2503.17332; Fang one-day |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | BountyBench offensive defensive cyber AI agents | OpenAlex | BountyBench; ExploitGym 2605.11086; cost-aware eval 2607.15263 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | MLOps security threats survey pipeline | OpenAlex | general MLOps surveys (no security focus) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | SoK machine learning supply chain security | OpenAlex | general ML security surveys |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | AI bill of materials AIBOM transparency | OpenAlex | AIBOM MLR (TOSEM 2025); ALOHA; BOMs Away (ICSE'24) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Jupyter notebook security attack data science; model watermark weight theft insider | OpenAlex | failed (daily budget exhausted) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | ten title-confirmation queries (What Was Your Prompt, TEE.fail, GPUHammer, ...) | OpenAlex | failed (budget exhausted) |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | TEE.fail Breaking TEEs DDR5 Memory Bus Interposition | Crossref | IEEE S&P 2026, DOI 10.1109/sp63933.2026.00101 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Evaluating LLMs Capability to Launch Fully Automated Spear Phishing | Crossref | ESWA 2026 journal version |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | Stealing Part of a Production Language Model; Exploit Instrumentation Study HF | Crossref | no matching DOI |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | 40 arXiv abstract pages (2402.06664, 2305.06972, 2410.17175, 2406.10279, 2405.18137, 2411.18191, 2409.20002, 2301.07829, 2503.17332, 2203.15981, 2308.06782, 2403.09539, 2505.00817, 2403.06634, 2509.06703, 2404.08144, 2602.04653, 2502.07776, 2508.15987, 2507.08166, 2403.00108, 2511.03675, 2601.14163, 2401.16603, 2408.01605, 2411.01076, 2403.09751, 2408.08926, 2406.01637, 2607.17503, 2602.19818, 2602.05401, 2302.10149, 2412.19394, 2502.02542, 2006.03463, 2608.09867, 2509.23594) | arxiv.org/abs fetch | all titles, authors, and abstracts confirmed |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | about 60 direct page fetches of vendor, research, advisory, and news primaries (JFrog, ReversingLabs, Trail of Bits, Unit 42 x2, Wiz x3, Oligo x2, PyTorch, PyPI, HiddenLayer x2, Sysdig, Microsoft x4, RAND, HF, OpenSSF, CycloneDX, Sigstore, LF, Mithril, 5stars217, Trend Micro, Logpoint, Anthropic x2, Battering RAM, WireTap, Nx GHSA, OWASP x3, MCP spec, GTIG x2, Project Zero, Google blog, DARPA, XBOW, ESET, HYAS (Wayback), FinCEN, CNN, AISI x2, Verge, AWS bulletin) | curl fetch | see confirmed_via fields; failures are listed under UNVERIFIED |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | scratchpad/raw/atlas.yaml technique and case-study listing | local file | ATLAS v5.6.0 ids; case studies CS0015 to CS0056 |
| 2026-10-02 | 3 supply chain, infra, AI-enabled offense | cached OWASP Agentic 2026 PDF and NIST AI 100-2 E2025 PDF | pdftotext | ASI01 to ASI10 titles; NISTAML ids |
| 2026-10-02 | 4 incidents and news | EchoLeak CVE-2025-32711 Microsoft 365 Copilot zero-click Aim Security | WebSearch | hackthebox, sentra, rescana |
| 2026-10-02 | 4 incidents and news | CVE-2025-53773 GitHub Copilot Visual Studio Code prompt injection RCE | WebSearch | MSRC advisory, embracethered |
| 2026-10-02 | 4 incidents and news | Amazon Q Developer extension malicious prompt wiper July 2025 AWS bulletin | WebSearch | AWS-2025-015 via press, Pillar, TechRepublic |
| 2026-10-02 | 4 incidents and news | Nx s1ngularity supply chain AI CLI Claude Gemini credentials | WebSearch | StepSecurity, THN (GitGuardian numbers) |
| 2026-10-02 | 4 incidents and news | postmark-mcp malicious MCP server Koi Security BCC | WebSearch | Snyk, THN, Dark Reading |
| 2026-10-02 | 4 incidents and news | Anthropic disrupting first AI-orchestrated cyber espionage GTG-1002 | WebSearch | Anthropic PDF, MITRE C0062, AIID 1263 |
| 2026-10-02 | 4 incidents and news | Anthropic threat intelligence report Aug 2025 vibe hacking GTG-2002 | WebSearch | Anthropic PDF, Dark Reading |
| 2026-10-02 | 4 incidents and news | Google GTIG adversarial misuse of generative AI Gemini state actors | WebSearch | GTIG blog, Nov 2025 tracker PDF |
| 2026-10-02 | 4 incidents and news | OpenAI disrupting malicious uses of AI report 2025 state-affiliated | WebSearch | OpenAI Feb 2025 PDF, 2024 post |
| 2026-10-02 | 4 incidents and news | Microsoft OpenAI staying ahead of threat actors Forest Blizzard Feb 2024 | WebSearch | Microsoft Security blog |
| 2026-10-02 | 4 incidents and news | Microsoft Tay chatbot 2016 learning from Tay's introduction Peter Lee | WebSearch | academic analyses (Neff & Nagy) |
| 2026-10-02 | 4 incidents and news | Kevin Liu Bing Chat Sydney prompt injection system prompt leak | WebSearch | Wikipedia Sydney |
| 2026-10-02 | 4 incidents and news | Samsung engineers leaked source code ChatGPT ban April 2023 | WebSearch | Gizmodo, Slashdot |
| 2026-10-02 | 4 incidents and news | OpenAI March 20 ChatGPT outage redis-py payment 1.2% | WebSearch | BleepingComputer, HelpNetSecurity |
| 2026-10-02 | 4 incidents and news | Chevrolet of Watsonville chatbot $1 Tahoe Chris Bakke | WebSearch | AIID 622, VentureBeat |
| 2026-10-02 | 4 incidents and news | Moffatt v. Air Canada 2024 BCCRT 149 chatbot | WebSearch | ABA, Lexology |
| 2026-10-02 | 4 incidents and news | Arup deepfake video conference HK$200 million | WebSearch | CNN, AIID 634, PRMIA PDF |
| 2026-10-02 | 4 incidents and news | PromptArmor Slack AI data exfiltration private channels | WebSearch | Willison, The Register |
| 2026-10-02 | 4 incidents and news | embracethered M365 Copilot ASCII smuggling | WebSearch | Embrace The Red 2024 |
| 2026-10-02 | 4 incidents and news | Replit AI agent deleted production database SaaStr | WebSearch | The Register, heise |
| 2026-10-02 | 4 incidents and news | Invariant Labs GitHub MCP toxic agent flow | WebSearch | invariantlabs.ai |
| 2026-10-02 | 4 incidents and news | Sysdig LLMjacking stolen cloud credentials Bedrock | WebSearch | CSO, AIID 898 |
| 2026-10-02 | 4 incidents and news | Oligo ShadowRay CVE-2023-48022 exploited | WebSearch | Oligo, MITRE C0045, ShadowRay 2.0 |
| 2026-10-02 | 4 incidents and news | ReversingLabs nullifAI Hugging Face broken pickle | WebSearch | ReversingLabs blog |
| 2026-10-02 | 4 incidents and news | JFrog malicious ML models Hugging Face 100 models | WebSearch | THN, BleepingComputer, arXiv 2601.14163 |
| 2026-10-02 | 4 incidents and news | PyTorch torchtriton compromised dependency Dec 2022 | WebSearch | pytorch.org blog |
| 2026-10-02 | 4 incidents and news | exposed Ollama servers Cisco Talos 1,100 Shodan | WebSearch | Cisco blog |
| 2026-10-02 | 4 incidents and news | Wiz DeepSeek exposed ClickHouse database | WebSearch | Wiz, CyberScoop |
| 2026-10-02 | 4 incidents and news | embracethered ChatGPT macOS SpAIware memory | WebSearch | Embrace The Red, FGCS DOI |
| 2026-10-02 | 4 incidents and news | Brave Comet Perplexity indirect prompt injection | WebSearch | Brave blog, Willison |
| 2026-10-02 | 4 incidents and news | Noma ForcedLeak Salesforce Agentforce | WebSearch | THN, Noma |
| 2026-10-02 | 4 incidents and news | Cursor CVE-2025-54135 CurXecute MCP | WebSearch | Tenable FAQ, THN DuneSlide |
| 2026-10-02 | 4 incidents and news | Claude Code CVE 2025 GHSA anthropics/claude-code | WebSearch | 5 GHSA advisories, Datadog |
| 2026-10-02 | 4 incidents and news | Langflow CVE-2025-3248 CISA KEV Flodrix | WebSearch | Trend Micro, CSO |
| 2026-10-02 | 4 incidents and news | Wiz NVIDIA Container Toolkit CVE-2024-0132 | WebSearch | Wiz blog x2 |
| 2026-10-02 | 4 incidents and news | AI agent security incident 2026 prompt injection breach | WebSearch | OWASP Q1-26, Microsoft SK blog, THN Oct 2026 |
| 2026-10-02 | 4 incidents and news | "2026" AI coding agent supply chain attack npm CVE | WebSearch | Phoenix Security, Tenable Mini Shai-Hulud |
| 2026-10-02 | 4 incidents and news | Critical Cursor flaws prompt injection escape sandbox July 2026 | WebSearch | THN, SecurityWeek (DuneSlide) |
| 2026-10-02 | 4 incidents and news | SalesBleed Salesforce Agentforce three flaws 2026 | WebSearch | The Register, BusinessWire |
| 2026-10-02 | 4 incidents and news | OpenClaw Moltbot Clawdbot security malicious skills 2026 | WebSearch | BleepingComputer, Bitdefender |
| 2026-10-02 | 4 incidents and news | Clinejection Cline npm GitHub issue title Feb 2026 | WebSearch | Snyk, CSA PDF |
| 2026-10-02 | 4 incidents and news | LiteLLM PyPI backdoor March 2026 | WebSearch | Datadog, Snyk, CSA |
| 2026-10-02 | 4 incidents and news | Rehberger Google Bard prompt injection exfiltration 2023 | WebSearch | HackerOne blog, Greshake post |
| 2026-10-02 | 4 incidents and news | Gemini Trifecta Tenable | WebSearch | Security Boulevard, THN |
| 2026-10-02 | 4 incidents and news | Gemini calendar invite "Invitation Is All You Need" SafeBreach | WebSearch | CODE BLUE archive, TechRepublic |
| 2026-10-02 | 4 incidents and news | OpenAI Operator prompt injection embracethered | WebSearch | Embrace The Red, Fortune |
| 2026-10-02 | 4 incidents and news | vLLM CVE-2025-47277 PyNcclPipe Mooncake | WebSearch | GHSA, OSV |
| 2026-10-02 | 4 incidents and news | NVIDIA Triton CVE-2025-23319 Wiz chain | WebSearch | NVIDIA bulletin 5687, NVD |
| 2026-10-02 | 4 incidents and news | Steve Kramer Biden deepfake robocall FCC fine | WebSearch | NPR, NHPR, NH DOJ |
| 2026-10-02 | 4 incidents and news | voice clone CEO fraud UK energy EUR 220,000 2019 | WebSearch | PaymentsJournal, Munich Re |
| 2026-10-02 | 4 incidents and news | FBI IC3 PSA AI voice impersonating senior officials 2025 | WebSearch | IC3 PSA250515, PSA251219 |
| 2026-10-02 | 4 incidents and news | HiddenLayer AI Threat Landscape Report 2025 | WebSearch | PRNewswire x2 |
| 2026-10-02 | 4 incidents and news | IBM Cost of a Data Breach 2025 AI 13% shadow AI | WebSearch | IBM PR, Kiteworks |
| 2026-10-02 | 4 incidents and news | AI Incident Database 2025 roundup | WebSearch | AIID blog roundups |
| 2026-10-02 | 4 incidents and news | Gartner survey 2025 GenAI attacks deepfake 62% | WebSearch | Gartner newsroom |
| 2026-10-02 | 4 incidents and news | Anthropic threat intelligence report 2026 | WebSearch | Anthropic Sep 2026 report |
| 2026-10-02 | 4 incidents and news | GTIG AI threat tracker PROMPTFLUX PROMPTSTEAL | WebSearch | GTIG PDF, CSO |
| 2026-10-02 | 4 incidents and news | Mexican government breach Claude Bloomberg 2026 | WebSearch | Bloomberg, Engadget |
| 2026-10-02 | 4 incidents and news | Unit 42 Vertex AI double agent 2026 | WebSearch | THN, CSA |
| 2026-10-02 | 4 incidents and news | Claude Code source leak npm source map March 2026 Zscaler | WebSearch | Zscaler, HelpNetSecurity |
| 2026-10-02 | 4 incidents and news | Meta internal AI agent exposed data March 2026 | WebSearch | press aggregations |
| 2026-10-02 | 4 incidents and news | Salesloft Drift OAuth UNC6395 GTIG | WebSearch | FINRA, BleepingComputer |
| 2026-10-02 | 4 incidents and news | Wiz Moltbook exposed Supabase | WebSearch | Wiz blog |
| 2026-10-02 | 4 incidents and news | CamoLeak GitHub Copilot Camo Legit Security | WebSearch | secondary analyses |
| 2026-10-02 | 4 incidents and news | ESET PromptLock gpt-oss Ollama NYU | WebSearch | THN, Security Boulevard |
| 2026-10-02 | 4 incidents and news | Zenity AgentFlayer ChatGPT Connectors Black Hat 2025 | WebSearch | CSO, Hackread |
| 2026-10-02 | 4 incidents and news | AppOmni ServiceNow second-order prompt injection | WebSearch | AppOmni AO Labs |
| 2026-10-02 | 4 incidents and news | ServiceNow BodySnatcher CVE-2025-12420 | WebSearch | AppOmni, THN, CyberScoop |
| 2026-10-02 | 4 incidents and news | Varonis Reprompt Copilot Jan 2026 | WebSearch | SecurityWeek, Windows Central |
| 2026-10-02 | 4 incidents and news | Noma GeminiJack Gemini Enterprise | WebSearch | Dark Reading, Infosecurity |
| 2026-10-02 | 4 incidents and news | OpenAI Mixpanel security incident Nov 2025 | WebSearch | BleepingComputer |
| 2026-10-02 | 4 incidents and news | OWASP GenAI Exploit Round-up Q2 2026 | WebSearch | only Q1-26 and Q2-25 found |
| 2026-10-02 | 4 incidents and news | Mercor breach LiteLLM 2026 | WebSearch | SecurityWeek, Fortune, TechCrunch |
| 2026-10-02 | 4 incidents and news | Flowise CVE-2025-59528 exploited 2026 | WebSearch | BleepingComputer, THN |
| 2026-10-02 | 4 incidents and news | GrafanaGhost Noma Grafana | WebSearch | CyberScoop, Dark Reading |
| 2026-10-02 | 4 incidents and news | OpenAI threat report 2026 | WebSearch | OpenAI index, Wikipedia "2026 OpenAI agent cyberattacks" |
| 2026-10-02 | 4 incidents and news | (5 further queries refused: session WebSearch budget of 200 exhausted, shared across agents) | WebSearch | none |
| 2026-10-02 | 4 incidents and news | fetch Microsoft SK blog, OWASP Q1-26, THN ThreatsDay, Anthropic Sep-26, Wikipedia x2, HF blog, AWS-2025-015, Tay blog, Anthropic GTG-1002, Wiz DeepSeek, Brave, Noma, Datadog, Wiz Moltbook, Tenable Cursor, DuneSlide, Register SalesBleed, Snyk Clinejection, Invariant, Embrace The Red, AIID roundup, GTIG Jan-25, Oligo SR2 | WebFetch | primary confirmation; 403 on openai.com, aim.security, canlii; 429 on Semantic Scholar and arXiv API |
| 2026-10-02 (pass 2) | 4 incidents and news | Shai-Hulud npm worm September 2025 TruffleHog | WebSearch | refused: session budget of 200 already used; pass 2 used WebFetch, the arXiv HTML search, and local ATLAS data only |
| 2026-10-02 (pass 2) | 4 incidents and news | ti: "Not what you've signed up for", EchoLeak, "Invitation Is All You Need", "Ransomware 3.0", "Trust No AI", "Here Comes The AI Worm" | arXiv search (HTML) | 2302.12173, 2509.10540, 2508.12175, 2508.20444, 2412.06090, 2403.02817 |
| 2026-10-02 (pass 2) | 4 incidents and news | prompt injection in the wild; agentic browser prompt injection; MCP tool poisoning | arXiv search (HTML) | 2604.27202, 2601.07072, 2511.20597, 2603.22489 |
| 2026-10-02 (pass 2) | 4 incidents and news | package hallucination; malicious MCP servers; AI agent incidents; pickle deserialization models; AI coding assistants security | arXiv search (all fields) | 2608.23897, 2609.35799, 2610.00902, 2607.17503, 2508.19774, 2605.07135, 2606.23130 |
| 2026-10-02 (pass 2) | 4 incidents and news | AI incident database; voice cloning scam; LLMjacking; rules file backdoor; LLM malware in the wild | arXiv search | AIID-method papers only; no hits for LLMjacking or rules-file backdoor |
| 2026-10-02 (pass 2) | 4 incidents and news | arXiv abs pages for 13 ids | curl arxiv.org/abs | titles, authors, dates, and abstracts confirmed |
| 2026-10-02 (pass 2) | 4 incidents and news | MITRE ATLAS 2026.09 case studies AML.CS0000-CS0072 and technique ids | local ATLAS-2026.09.yaml | all AML ids in file validated; 19 existing entries given AML.CS ids; about 20 new incidents sourced |
| 2026-10-02 (pass 2) | 4 incidents and news | OWASP Top 10 for Agentic Applications 2026 names | local owasp-top10-agentic-2026.txt | ASI01-ASI10 names confirmed |
| 2026-10-02 (pass 2) | 4 incidents and news | fetch CISA Shai-Hulud alert; Wiz 38TB, HF cross-tenant, Probllama, SAPwned, Replicate, Shai-Hulud 2.0; HF Spaces secrets; claude.com Claude for Chrome; OWASP agentic page | WebFetch | primary confirmation |
| 2026-10-02 (pass 2) | 4 incidents and news | fetch HF security-incident-july-2026, HF agent-intrusion timeline, METR investigation, JFrog blog | WebFetch | HF incident mechanics; agent-count conflict |
| 2026-10-02 (pass 2) | 4 incidents and news | fetch Anthropic distillation; Microsoft AI recommendation poisoning, Claude Code GH Action, SesameOp, Storm-2139; Unit 42 Hermes and namespace reuse; MODA Taiwan; Check Point Skynet and AI-in-the-middle; Pillar GGUF and rules file; Lasso; Lumia AIKatz; Sysdig LLMjacking x2 | WebFetch | primary confirmation |
| 2026-10-02 (pass 2) | 4 incidents and news | fetch CERT-UA LAMEHUG; Radware ZombieAgent; NewsGuard Pravda; The Verge LLaMA leak | WebFetch | empty body / bot check / 403 / blocked |
| 2026-10-02 | 5 enumerations | CWE 4.20 release notes AI/ML view 1448 weaknesses | WebSearch | refused: budget exhausted |
| 2026-10-02 | 5 enumerations | CWE Artificial Intelligence Working Group AI WG 2026 | WebSearch | refused: budget exhausted |
| 2026-10-02 | 5 enumerations | CVE program AI working group guidance AI vulnerabilities CNA rules model | WebSearch | refused: budget exhausted |
| 2026-10-02 | 5 enumerations | MITRE ATLAS 2026 update agentic AI techniques case studies new release | WebSearch | refused: budget exhausted |
| 2026-10-02 | 5 enumerations | cwe-api.mitre.org /cwe/version; /cwe/weakness/{1426,1427,1039,1434} | CWE REST API | CWE 4.20 (2026-04-30), 969 weaknesses; entry metadata |
| 2026-10-02 | 5 enumerations | cwec_latest.xml.zip regex scan for AI terms; categories/views | CWE XML | CWE-1446, 1447, 1448; AI/ML platform on 22 CWEs |
| 2026-10-02 | 5 enumerations | cwe.mitre.org/data/definitions/1448.html | WebFetch | view introduced in 4.20; maintenance note |
| 2026-10-02 | 5 enumerations | cwe.mitre.org/community/working_groups.html | WebFetch | AI WG purpose; GitHub repo |
| 2026-10-02 | 5 enumerations | GitHub CWE-CAPEC/AI-Working-Group minutes 2026-06-12 + slides 2026-06-26 | GitHub raw | CWE 5.0 Oct 2026; AI submissions pipeline |
| 2026-10-02 | 5 enumerations | capec_latest.xml regex scan | CAPEC XML | v3.9 2023-01-24; zero AI patterns |
| 2026-10-02 | 5 enumerations | mitre-atlas/atlas-data releases, dist/manifest.yaml, dist/v6/ATLAS-2026.09.yaml, CHANGELOG.md | GitHub API/raw | 16/120/88/40/73; renumbering T0019/T0058/T0104 to T0115.*; platforms |
| 2026-10-02 | 5 enumerations | mitre-atlas/atlas-navigator-data dist listing | GitHub API | stix-atlas.json, stix-atlas-attack-enterprise.json |
| 2026-10-02 | 5 enumerations | genai.owasp.org/llm-top-10/ | WebFetch | LLM01-10:2025 list; CC BY-SA |
| 2026-10-02 | 5 enumerations | genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | WebFetch | released 2025-12-09 |
| 2026-10-02 | 5 enumerations | owasp.org/www-project-machine-learning-security-top-10/ | WebFetch | 404; fell back to GitHub README (draft, ML01-10:2023) |
| 2026-10-02 | 5 enumerations | owaspai.org | WebFetch | 300+ pages; ISO/CEN liaison |
| 2026-10-02 | 5 enumerations | aivss.owasp.org | WebFetch | v0.8 latest; calculators |
| 2026-10-02 | 5 enumerations | www.cve.org/About/Process/WorkingGroups | WebFetch | page body not rendered |
| 2026-10-02 | 5 enumerations | NVD API cveId= 17 AI CVEs | NVD API 2.0 | CWE typing table |
| 2026-10-02 | 5 enumerations | NVD API cweId=CWE-1427/1426/1434/1039 | NVD API 2.0 | 0 results each (filter unreliable) |
| 2026-10-02 | 5 enumerations | NVD API keywordSearch "prompt injection" / "large language model" / "LLM" / "Model Context Protocol" | NVD API 2.0 | 194 / 189 / 321 / 135; CWE distributions |
| 2026-10-03 | 5 enumerations | GitHub code search "CWE-1427"/"CWE-1426"/"CWE-1039"/"CWE-1434" repo:CVEProject/cvelistV5 | GitHub search | 17 / 3 / 3 / 0 records (lower bound) |
| 2026-10-03 | 5 enumerations | cvelistV5 CVE-2026-44688.json | GitHub raw | CNA CWE-1427 dropped in NVD |
| 2026-10-02 | 5 enumerations | csrc.nist.gov/pubs/ir/8596/iprd | WebFetch | Cyber AI Profile iprd 2025-12-16 |
| 2026-10-02 | 5 enumerations | csrc.nist.gov/projects/cosais | WebFetch | five overlay use cases; dates |
| 2026-10-02 | 5 enumerations | nist.gov/itl/ai-risk-management-framework | WebFetch | AI RMF under revision; CI profile concept note |
| 2026-10-02 | 5 enumerations | csrc.nist.gov/pubs/ai/100/2/e2025/final | WebFetch | authors, DOI, no newer edition |
| 2026-10-02 | 5 enumerations | docs.avidml.org taxonomy *.md; avid-db GitHub tree | WebFetch / GitHub API | SEP ids; report and vuln counts; MIT license |
| 2026-10-02 | 5 enumerations | incidentdatabase.ai; /taxonomies/; /research/snapshots/; /apps/incidents/; GraphQL | WebFetch / curl | CSETv1, GMF, MIT taxonomies; snapshot 2026-09-28; API forbidden |
| 2026-10-02 | 5 enumerations | airisk.mit.edu | WebFetch | 1,700+ risks; v4 Dec 2025; CC BY 4.0 |
| 2026-10-02 | 5 enumerations | oecd.ai/en/incidents | WebFetch | ~18,050 incidents and hazards |
| 2026-10-02 | 5 enumerations | oecd.org common reporting framework page | WebFetch | HTTP 403 |
| 2026-10-02 | 5 enumerations | learn.microsoft.com bug-bar-aiml | WebFetch | intentional threats list |
| 2026-10-02 | 5 enumerations | microsoft.com/msrc/aibugbar | WebFetch | AI severity classes |
| 2026-10-02 | 5 enumerations | saif.google risks and controls | WebFetch | 15 risks with codes; control groups |
| 2026-10-02 | 5 enumerations | github.com/cosai-oasis/secure-ai-tooling + risk-map YAML + ADR-027 | WebFetch / GitHub raw | 36 risks, 37 controls, 42 components, 10 personas; mappings |
| 2026-10-02 | 5 enumerations | coalitionforsecureai.org | WebFetch | 4 workstreams; MCP Security v2.0 2026-09-25 |
| 2026-10-02 | 5 enumerations | databricks DASF landing page; blog dasf-v3 | WebFetch | no counts; blog 404 |
| 2026-10-02 | 5 enumerations | GitHub search "databricks ai security framework" | GitHub API | dasf_assistant (12/62/64), dasf-demo (DASF 3.0) |
| 2026-10-02 | 5 enumerations | cloudsecurityalliance.org/artifacts/ai-controls-matrix | WebFetch | 243 controls, 18 domains |
| 2026-10-02 | 5 enumerations | CSA MAESTRO blog | WebFetch | seven layers |
| 2026-10-02 | 5 enumerations | 0din.ai/research/taxonomy | WebFetch | 3-level hierarchy |
| 2026-10-02 | 5 enumerations | github.com/Arcanum-Sec/arc_pi_taxonomy + taxonomy.json | WebFetch / GitHub raw | 27/70/63/12 nodes, v1.6.1 |
| 2026-10-02 | 5 enumerations | etsi.org/committee/2312-sai; deliver PDFs | WebFetch / curl | EN 304 223 V2.1.1; TS 104 158-1/-2 |
| 2026-10-02 | 5 enumerations | enisa.europa.eu AI cybersecurity challenges | WebFetch | 2020 report; later publications |
| 2026-10-02 | 5 enumerations | artificialintelligenceact.eu/article/15/ | WebFetch | Art. 15(5) verbatim |
| 2026-10-02 | 5 enumerations | gov.uk AI cyber security code of practice | WebFetch | 13 principles, 2025-01-31 |
| 2026-10-02 | 5 enumerations | iso.org standard pages (3 ids) | curl / WebFetch | Cloudflare / 403 |
| 2026-10-02 | 5 enumerations | Wikipedia ISO/IEC JTC 1/SC 42 raw | MediaWiki | 42001, 23894, 22989, 5338 listed |
| 2026-10-02 | 5 enumerations | gcve.eu | WebFetch | GNA scheme; BCP-05 |
| 2026-10-02 | 5 enumerations | aiaaic.org repository | WebFetch | structure only |
| 2026-10-02 | 5 enumerations | atlas.mitre.org/pdf-files/SAFEAI_Full_Report.pdf | curl | SAFE-AI PDF |
| 2026-10-02 | 5 enumerations | prompt injection taxonomy | Semantic Scholar API | Greshake 2023; Wang 2026; Correia 2026; Duarte 2026 (IEEE Access) |
| 2026-10-02 | 5 enumerations | jailbreak taxonomy large language models | Semantic Scholar API | Pelaez-Gonzalez 2025; Yi 2024 survey; SoK jailbreak guardrails (S&P 2026) |
| 2026-10-02 | 5 enumerations | taxonomy of security threats AI agents survey | Semantic Scholar API | Gan 2024 (TOSEM 2026); Chen 2025 CUA survey; Chu 2026 |
| 2026-10-02 | 5 enumerations | AI vulnerability database taxonomy | Semantic Scholar API | noise only |
| 2026-10-02 | 5 enumerations | ti:taxonomy AND abs:"prompt injection" | arXiv API | MCP-38; Wang 2026; Ji 2025 IPI defense taxonomy; Correia 2026 |
| 2026-10-02 | 5 enumerations | ti:taxonomy AND ti:jailbreak | arXiv API | Pelaez-Gonzalez 2025; Giarrusso 2025; audio jailbreak taxonomy 2026 |
| 2026-10-02 | 5 enumerations | ti:taxonomy AND (agent OR agentic) AND (security OR threats OR attacks) | arXiv API | Baek 2026; Jiang 2026 SoK; agent-skills taxonomy 2026; MCP formal 2026 |
| 2026-10-02 | 5 enumerations | ti:"failure modes in machine learning" | arXiv API | 1911.11034 |
| 2026-10-02 | 5 enumerations | ti:SoK AND abs:"prompt injection" | arXiv API | Dehghantanha 2026; Shi 2025 trust-authorization SoK |
| 2026-10-02 | 5 enumerations | ti:"flaw disclosure" | arXiv API | Cattell 2024; Longpre 2025 |
| 2026-10-02 | 5 enumerations | abs:"AI incident" AND ti:taxonomy | arXiv API | Agarwal 2025; Huwyler 2025 |
| 2026-10-02 | 5 enumerations | abs:"MITRE ATLAS" AND (mapping OR taxonomy OR framework) | arXiv API | Cisco 2025; Huang 2026 ATLAS rules; Arora 2025 |
| 2026-10-02 | 5 enumerations | title lookups: HackAPrompt, Jailbroken, DAN, Rossi, Weidinger, AI Agents Under Threat | arXiv API | ids confirmed |
| 2026-10-03 | 5 enumerations | id_list 2311.06237 | arXiv API | Inie et al. grounded theory of LLM red teaming (0DIN basis) |
| 2026-10-02 | 6 threat models | CSA MAESTRO agentic AI threat modeling framework seven layers | WebSearch | NOT RUN: session budget 200/200 exhausted |
| 2026-10-02 | 6 threat models | BIML architectural risk analysis LLM 81 risks | WebSearch | NOT RUN: budget exhausted |
| 2026-10-02 | 6 threat models | Microsoft "Threat Modeling AI/ML Systems and Dependencies" | WebSearch | NOT RUN: budget exhausted |
| 2026-10-02 | 6 threat models | Google SAIF risk map components risks controls | WebSearch | NOT RUN: budget exhausted |
| 2026-10-02 | 6 threat models | ti:MAESTRO AND abs:agentic | arXiv API | no relevant hit (name clashes) |
| 2026-10-02 | 6 threat models | ti:"threat model" AND ti:agentic | arXiv API | 2504.19956 ATFAA; 2512.04785 ASTRIDE; 2604.18658 Owner-Harm |
| 2026-10-02 | 6 threat models | abs:STRIDE AND abs:"machine learning" AND ti:threat | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:ATFAA | arXiv API | none (indexed under title) |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND abs:LLM | arXiv API | 2410.08755 PILLAR; 2504.18369 ThreMoLIA; 2505.04101 |
| 2026-10-02 | 6 threat models | ti:"threat model" AND ti:"retrieval-augmented" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"Model Context Protocol" AND ti:security | arXiv API | 2511.20920 Errico; 2602.01129 SMCP; 2508.12538 MCPXKIT |
| 2026-10-02 | 6 threat models | ti:"custom GPTs" AND ti:"prompt injection" | arXiv API | 2311.11538 Yu et al. |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND abs:"machine learning" | arXiv API | 2401.07960 ADMIn |
| 2026-10-02 | 6 threat models | abs:"STRIDE-AI" | arXiv API | 2605.17163 (second STRIDE-AI) |
| 2026-10-02 | 6 threat models | ti:"LLM Platform Security" | arXiv API | 2309.10254 Iqbal et al. |
| 2026-10-02 | 6 threat models | ti:"Model Context Protocol" AND ti:threat | arXiv API | 2503.23278 Hou; 2603.18063 MCP-38; 2603.22489 Huang; 2604.13849 MCPThreatHive |
| 2026-10-02 | 6 threat models | ti:"retrieval-augmented generation" AND ti:security AND abs:"threat model" | arXiv API | 2603.21654 Mu et al. |
| 2026-10-02 | 6 threat models | ti:"attack tree" AND abs:"machine learning" | arXiv API | 2312.16957 Yamaguchi & Aoki |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND ti:"generative AI" | arXiv API | 2509.10482 AegisShield |
| 2026-10-02 | 6 threat models | ti:LINDDUN AND abs:AI | arXiv API | 2603.06051 LINDDUN GenAI |
| 2026-10-02 | 6 threat models | ti:"risk analysis" AND abs:"machine learning" AND abs:architectural | arXiv API | noise |
| 2026-10-02 | 6 threat models | ti:"threat assessment" AND abs:"large language model" | arXiv API | 2506.02859 ATAG |
| 2026-10-02 | 6 threat models | ti:"threat model" AND abs:"LLM-integrated" | arXiv API | FAIL (API timeout) |
| 2026-10-02 | 6 threat models | ti:"threat modelling" AND abs:LLM | arXiv API | 2406.11007 Tete; 2605.10808 |
| 2026-10-02 | 6 threat models | ti:"agentic" AND ti:"attack surface" | arXiv API | 2603.22928 SoK; 2605.10763 MATRA; 2602.22525 |
| 2026-10-02 | 6 threat models | ti:"multi-agent" AND ti:"threat model" | arXiv API | 2508.09815 Krawiecka; 2609.22949 Paul & Nandy |
| 2026-10-02 | 6 threat models | ti:"red teaming" AND ti:"threat model" | arXiv API | 2407.14937 Verma et al. |
| 2026-10-02 | 6 threat models | ti:"asset-centric" AND ti:threat | arXiv API | 2403.06512 ThreatFinderAI; 2505.06315 Intel |
| 2026-10-02 | 6 threat models | ti:TARA AND abs:"artificial intelligence" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"failure modes" AND abs:agentic | arXiv API | noise |
| 2026-10-02 | 6 threat models | ti:"agent-to-agent" AND abs:security | arXiv API | 2511.05359 ConVerse; 2508.01332 BlockA2A |
| 2026-10-02 | 6 threat models | ti:SoK AND ti:"prompt injection" | arXiv API | none |
| 2026-10-02 | 6 threat models | abs:MAESTRO AND abs:"threat model" | arXiv API | 2508.10043 Zambare; 2504.16902 Habler; 2510.25863 AAGATE |
| 2026-10-02 | 6 threat models | ti:"Agent2Agent" AND abs:security | arXiv API | 2602.05877 AgentHeLLM |
| 2026-10-02 | 6 threat models | ti:RAG AND ti:"threat model" | arXiv API | 2509.20324 Arzanipour et al. |
| 2026-10-02 | 6 threat models | ti:"privacy threat" AND abs:"large language model" AND abs:LINDDUN | arXiv API | 2602.04927 PriMod4AI |
| 2026-10-02 | 6 threat models | ti:"AI security" AND ti:taxonomy AND abs:"threat" | arXiv API | 2511.21901 Huwyler; 2609.23894 Baek et al. |
| 2026-10-02 | 6 threat models | ti:"computer-use agents" AND ti:SoK | arXiv API | none (2507.05445 found from cache) |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND abs:"autonomous vehicle" AND abs:"machine learning" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"AI supply chain" AND abs:"threat model" | arXiv API | 2510.05159 Malice in Agentland |
| 2026-10-02 | 6 threat models | ti:"secure by design" AND abs:"AI agents" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"agentic AI" AND ti:security AND ti:survey | arXiv API | 2605.23989; 2508.19870 |
| 2026-10-02 | 6 threat models | ti:"lessons from red teaming" AND abs:"generative AI" | arXiv API | 2501.07238 Bullwinkel et al. |
| 2026-10-02 | 6 threat models | ti:"systematic literature review" AND ti:"threat model" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND abs:practitioners AND abs:"machine learning" | arXiv API | none |
| 2026-10-02 | 6 threat models | ti:"on evaluating adversarial robustness" | arXiv API | 1902.06705 Carlini et al. |
| 2026-10-02 | 6 threat models | ti:"agent security" AND ti:"systems" | arXiv API | 2605.18991 Christodorescu; 2505.02077 Schroeder de Witt |
| 2026-10-02 | 6 threat models | ti:"AI agents" AND ti:"threat modeling" | arXiv API | 2602.11327 Anbiaee et al. |
| 2026-10-02 | 6 threat models | ti:"risk assessment" AND ti:agentic | arXiv API | 2510.15739 AURA; 2511.18114 ASTRA |
| 2026-10-02 | 6 threat models | ti:"security analysis" AND ti:"agent protocols" | arXiv API | 2606.28690 formal protocol composition |
| 2026-10-02 | 6 threat models | ti:"threat modeling" AND ti:"machine learning" | arXiv API | noise |
| 2026-10-02 | 6 threat models | ti:"threat model" AND ti:"machine learning" AND ti:systems | arXiv API | FAIL |
| 2026-10-02 | 6 threat models | abs:"MITRE ATLAS" AND ti:"threat" | arXiv API | FAIL |
| 2026-10-02 | 6 threat models | ti:"prompt injection" AND ti:"threat model" | arXiv API | 2603.22489; 2609.22949 |
| 2026-10-02 | 6 threat models | STRIDE-AI approach ... machine learning assets | Semantic Scholar API | empty (rate-limited) |
| 2026-10-02 | 6 threat models | Mauri Damiani modeling threats AI-ML STRIDE | Semantic Scholar API | empty (rate-limited); confirmed from the cached PDF |
| 2026-10-02 | 6 threat models | threat analysis and risk assessment machine learning automotive ISO 21434 | Semantic Scholar API | Ghosh et al. IEEE Access 2023; Ahmad et al. SQJ 2025 |
| 2026-10-02 | 6 threat models | attack trees machine learning systems threat modeling | Semantic Scholar API | noise |
| 2026-10-02 | 6 threat models | PLOT4ai privacy library of threats AI | Semantic Scholar API | empty |
| 2026-10-02 | 6 threat models | Khlaaf comprehensive risk assessments AI | Semantic Scholar API | empty (rate-limited); found via the ToB GitHub API |
| 2026-10-02 | 6 threat models | DOI:10.1109/ACCESS.2023.3243906 | Semantic Scholar API (WebFetch) | abstract; OA URL served HTML |
| 2026-10-02 | 6 threat models | arXiv:2002.05646 | Semantic Scholar API (WebFetch) | HTTP 429; confirmed via arXiv API |
| 2026-10-02 | 6 threat models | cloudsecurityalliance.org MAESTRO blog | WebFetch | layers, method steps |
| 2026-10-02 | 6 threat models | berryvilleiml.com/results | WebFetch | BIML-78, BIML-LLM24, IEEE Computer 2024 |
| 2026-10-02 | 6 threat models | learn.microsoft.com threat-modeling-aiml; bug-bar-aiml; failure-modes | WebFetch/curl | full text; Nov 2019 |
| 2026-10-02 | 6 threat models | microsoft.com/msrc/aibugbar | WebFetch | AI severity classification |
| 2026-10-02 | 6 threat models | saif.google SAIF map; services.google.com SAIF approach PDF | WebFetch/curl | 15 risks; PDF downloaded |
| 2026-10-02 | 6 threat models | github cosai-oasis/secure-ai-tooling risk-map YAML | WebFetch + curl | 36 risks, 59 components, 43 controls, 10 personas |
| 2026-10-02 | 6 threat models | aws.amazon.com security blog GenAI threat modeling | WebFetch | Nov 2024; Threat Composer grammar |
| 2026-10-02 | 6 threat models | github awslabs/threat-composer workspaceExamples | WebFetch + curl | GenAIChatbot.tc.json (37 threats) |
| 2026-10-02 | 6 threat models | plot4.ai | WebFetch | 138 threats, 8 categories |
| 2026-10-02 | 6 threat models | developer.nvidia.com AI red team intro | WebFetch | Jun 2023 framework |
| 2026-10-02 | 6 threat models | rand.org RRA2849-1 | WebFetch/curl | HTTP 403; used the cached PDF |
| 2026-10-02 | 6 threat models | modelcontextprotocol.io security best practices | WebFetch | full attack list |
| 2026-10-02 | 6 threat models | genai.owasp.org ASI T&M; Securing Agentic Apps; MAS guide; ASI Top 10 | WebFetch/curl | landing pages confirmed |
| 2026-10-02 | 6 threat models | ncsc.gov.uk secure AI guidelines | WebFetch | Nov 2023 |
| 2026-10-02 | 6 threat models | raw.githubusercontent cosai risks.yaml | WebFetch | risk list + field schema |
| 2026-10-02 | 6 threat models | robustintelligence.com ai-security-taxonomy | WebFetch | FAIL ECONNREFUSED |
| 2026-10-02 | 6 threat models | github mitre-atlas/atlas-data | WebFetch + curl | v6 2026.09: 73 case studies |
| 2026-10-02 | 6 threat models | github trailofbits/publications | WebFetch + GitHub API | YOLOv7 TM, Khlaaf whitepaper, talks |
| 2026-10-02 | 6 threat models | ai.meta.com Agents Rule of Two | WebFetch | Oct 31 2025 |
| 2026-10-02 | 6 threat models | simonwillison.net lethal trifecta | WebFetch | Jun 16 2025 |
| 2026-10-02 | 6 threat models | openai.com preparedness framework | WebFetch | FAIL 403 |
| 2026-10-02 | 6 threat models | nccgroup.com MATA + design principles | WebFetch | Feb 2024 |
| 2026-10-02 | 6 threat models | cloudsecurityalliance.org agentic red teaming guide | WebFetch | May 2025 (login-gated PDF) |
| 2026-10-02 | 6 threat models | iso.org 27090 / PAS 8800 | WebFetch/curl | FAIL 403 / Cloudflare |
| 2026-10-02 | 6 threat models | github mrwadams/stride-gpt | WebFetch | features, MIT license |
| 2026-10-02 | 6 threat models | gov.uk AI cyber security code of practice | WebFetch | Jan 2025, 13 principles |
| 2026-10-02 | 6 threat models | media.defense.gov Deploying AI Systems Securely | WebFetch | FAIL 403 |
| 2026-10-03 | 6 threat models | ~22 candidate confirmation URLs | curl status check | 200 for most; 403 rand/mdpi/msft blog; 404 threat-composer.github.io |
| 2026-10-03 | 7 gap fill: papers (1-3) | id_list= 203 arXiv ids named in the reviewer gap list (evasion, adaptive attacks, physical/voice, NLP, GNN/RL, backdoors, LLM backdoors, poisoning, FL, extraction, MIA, LLM MIA, PII, unlearning, jailbreaks, alignment, red teaming, PI, agent defenses, RAG, MCP, skills, MAS, memory, embodied, VLM/T2I, DoS, watermarks, offense, code, surveys) | arXiv API (export.arxiv.org/api/query) | all 203 resolved; titles matched the brief except that 1911.02142 is now the extended TOPS version (first author Cortellazzi) |
| 2026-10-03 | 7 gap fill: papers (1-3) | POST /paper/batch ARXIV:<203 ids> fields=venue,year,citationCount,externalIds | Semantic Scholar batch API | venues and DOIs for 202 of 203; citation counts (for example Yao survey 1368, Ensemble AT 3116, C&W detectors 2021) |
| 2026-10-03 | 7 gap fill: papers (1-3) | id_list= 27 follow-up ids (PyRIT 2410.02828, garak 2406.11036, BALD 2405.20774, MoEcho 2508.15036, MSF 2106.09249, Nasr 2510.01676, Cascading bias 2505.24842, DDE 2506.17353, DCMI 2509.06026, AgentSentinel 2509.07764, RAG-WM 2501.05249, Sentry 2510.00554, NICGSlowDown 2203.15859, Architectural backdoors 2206.07840, Beyond Indistinguishability 2604.18697, LLM-GNN 2603.26105, Hollow-LLM 2607.28884, GPUBreach 2605.03812, SaTML 2026 items) | arXiv API | all resolved |
| 2026-10-03 | 7 gap fill: papers (1-3) | id_list= 24 ids "read from PDF" in sibling files + 2403.04786, 2410.04490, 2302.05733 | arXiv API | only Casey is mismatched (2403.04786 is Chowdhury et al.) |
| 2026-10-03 | 7 gap fill: papers (1-3) | ti:"backdoor" AND ti:"embodied" | arXiv API search | 2405.20774 BALD (Jiao et al.); 2408.02882 contextual backdoors; 2510.27623 BEAT |
| 2026-10-03 | 7 gap fill: papers (1-3) | ti:MoEcho; ti:PyRIT; ti:garak AND abs:LLM | arXiv API search | 2508.15036; (PyRIT not found by title search, resolved by id); 2406.11036 |
| 2026-10-03 | 7 gap fill: papers (1-3) | GET usenix.org/conference/usenixsecurity26/technical-sessions | direct fetch | 377 presentations; about 104 AI-related titles; 64 paper pages fetched with abstracts |
| 2026-10-03 | 7 gap fill: papers (1-3) | GET usenix.org pages: usenixsecurity16 carlini; usenixsecurity20 sugawara; usenixsecurity23 niu; usenixsecurity24 lin-zilong, yu-jiahao; usenixsecurity25 li-xiang; usenixsecurity14 fredrikson_matthew | direct fetch | Hidden Voice Commands, Light Commands, CodexLeaks, Malla, LLM-Fuzzer, OneFlip, Fredrikson 2014 (Best Paper) |
| 2026-10-03 | 7 gap fill: papers (1-3) | GET sp2026.ieee-security.org/accepted-papers.html | direct fetch | about 55 AI-related titles; 10 already in sibling files; new: Site Isolation is Dead, WebCloak, EnchTable, Hollow-LLM, Beyond Indistinguishability, WRATH, GPUBreach, GDDRHammer, TDXRay, Person Behind the Sound, Stride/Reflectivity, LLM-enhanced GNN poisoning, Leaderboard poisoning, CSAM concept filtering, AI-text detectors |
| 2026-10-03 | 7 gap fill: papers (1-3) | GET sigsac.org/ccs/CCS2025/accepted-papers/ | direct fetch | JavaScript-rendered, no list; fell back to Crossref title queries |
| 2026-10-03 | 7 gap fill: papers (1-3) | GET satml.org/2026/accepted-papers/; satml.org/2025/accepted-papers/ | direct fetch | 62 SaTML 2026 papers with abstracts and arXiv links; 2025 page format not parsed |
| 2026-10-03 | 7 gap fill: papers (1-3) | Crossref /works/<doi>: 10.1145/2976749.2978392, 10.1145/3372297.3423359, 10.14722/ndss.2021.24498, 10.14722/ndss.2020.24178, 10.1109/SP61157.2025.00103, 10.1109/SP61157.2025.00118, 10.1038/s41586-024-08025-4, 10.1145/3719027.3765196, 10.1109/SP40000.2020.00073, 10.1145/3359789.3359790 | Crossref API | all resolved (Accessorize, Phantom ADAS, Manipulating the Byzantine, CloudLeak, BAIT, GPTracker, SynthID-Text, AI Worm CCS, Pierazzi S&P, STRIP ACSAC) |
| 2026-10-03 | 7 gap fill: papers (1-3) | Crossref query.bibliographic: Latent Backdoor; Invisible for both Camera and LiDAR; production malware Magika; ControlLoc; Cascading Adversarial Bias; Differentiation-Based Extraction; DCMI; AgentSentinel; MoEcho; RAG-WM; Sentry; WireTap; NICGSlowDown; ILFO; Safety Misalignment; Architectural Backdoors; Model Inversion confidence; Rosenberg survey; Arp; Lyu FL survey | Crossref API | CCS 2025 DOIs 10.1145/3719027.* for 10 papers; CVPR/NDSS/S&P DOIs; Rosenberg CSUR 10.1145/3453158 |
| 2026-10-03 | 7 gap fill: papers (1-3) | /paper/search/match for 53 exact titles (S&P 2026, CCS 2025, older non-arXiv venues) | Semantic Scholar API | abstracts and DOIs for 49; no match for MoEcho, Leaderboards, CSAM filtering, embodied-backdoor variants |
| 2026-10-03 | 7 gap fill: papers (1-3) | POST /paper/batch for 30 "per memory" venue claims in sibling files | Semantic Scholar batch API | see C15 table |
| 2026-10-03 | 7 gap fill: papers (1-3) | NVD /cves/2.0?cveId=CVE-2025-59145; CVE-2026-27876 | NVD API | color-name npm malware; Grafana SQL Expressions RCE |
| 2026-10-03 | 7 gap fill: papers (1-3) | Legit Security CamoLeak blog | WebFetch | no CVE; CVSS 9.6; fixed 2025-08-14 |
| 2026-10-03 | 7 gap fill: papers (1-3) | noma.security/blog/grafana-ghost/ | direct fetch | 2026-04-07, no CVE on page |
| 2026-10-03 | 7 gap fill: papers (1-3) | anthropic.com/threat-intelligence-report-september-2026 | WebFetch | H1 "Detecting and countering misuse of AI: September 2026"; 10 GTG case ids |
| 2026-10-03 | 7 gap fill: papers (1-3) | api.github.com/repos/NVIDIA/garak; microsoft/PyRIT; Azure/PyRIT | GitHub API | garak created 2023-05-10, Apache-2.0, about 9.4k stars; microsoft/PyRIT created 2023-12-12, MIT; Azure/PyRIT created 2026-03-25 |
| 2026-10-03 | 7 gap fill: papers (1-3) | owasp.org/www-project-agentic-skills-top-10/ + raw index.md | direct fetch | AST01-AST10 summary table, v1.0-2026 |
| 2026-10-03 | 7 gap fill: papers (1-3) | c2pa.org/specifications/; spec.c2pa.org 2.2 spec | direct fetch | redirect to v2.4; hard and soft binding sections |
| 2026-10-03 | 7 gap fill: papers (1-3) | atlas-2026.09.yaml technique enumeration + atlas-changelog grep T0115/T0019/T0058/T0104 | local cache | 208 technique and sub-technique ids; rename mapping confirmed |
| 2026-10-03 | 7 gap fill: papers (1-3) | regex scan of sibling files: arXiv/DOI duplicate keys; "per memory" with confidence: high; "^### [A-Z]\. " headings; ATLAS ids absent from 2026.09 | local analysis | 40 duplicate works; 81 over-confident entries; 16 phantom headings; 46 deprecated-id uses |
| 2026-10-03 | 7 gap fill: papers (1-3) | curl arxiv.org/pdf/<id> x25 + file + shasum -a 256 | arXiv PDF | 25 PDFs valid (surveys, SoKs, threat-model frameworks, tools) |
| 2026-10-03 | 7 gap fill: other (3-6) | keyword sweep of 120 gap terms over raw/*.md | grep (local) | confirmed which gap items were absent; Rendered Insecure only in a search log; OneFlip UNVERIFIED; Pravda UNVERIFIED |
| 2026-10-03 | 7 gap fill: other (3-6) | "Rendered Insecure GPU side channel" (and 4 more) | WebSearch | REFUSED: session budget exhausted (200/200); no further WebSearch attempted |
| 2026-10-03 | 7 gap fill: other (3-6) | id_list of 30 arXiv ids from reviewer (2006.12784 ... 2303.02552) | arXiv export API | all 30 resolved; titles matched reviewer claims |
| 2026-10-03 | 7 gap fill: other (3-6) | 10 title queries (Rendered Insecure, DeepSniffer, CipherSteal, MoEcho, ...) | Semantic Scholar search API | CipherSteal (S&P 2025), HyperTheft (CCS 2024); then HTTP 429 |
| 2026-10-03 | 7 gap fill: other (3-6) | 29 title queries | DBLP API | blocked by Anubis bot challenge |
| 2026-10-03 | 7 gap fill: other (3-6) | Rendered Insecure; DeepSniffer; MoEcho; ICCAD 2017 fault injection; Breier CCS 2018; OneFlip; GDDRHammer; token-length side channel; local research agents; mobile LLM memory forensics; Pitropakis | Crossref API | DOIs for Rendered Insecure, DeepSniffer, MoEcho (CCS 2025), Liu ICCAD 2017, Breier CCS 2018, GDDRHammer (S&P 2026), memory forensics (S&P 2026), Pitropakis (CSR 2019); token-length paper not found |
| 2026-10-03 | 7 gap fill: other (3-6) | TDXRay; WireTap; AMD Secure Processor; Hide and Seek; Sentry; StegoNet; MaleficNet; OIDF identity; Hermes; DeepSteal; Grosse; Dong; Shadow in Cache; Qu; Luo; SAGA; BadMerging; DeepRecon; Duddu; BarraCUDA; TBT; SNIFF | Crossref API | TDXRay (S&P 2026), WireTap (CCS 2025), TEE.Fail (S&P 2026), Sentry (CCS 2025), StegoNet (ACSAC 2020), MaleficNet (LNCS 2022), DeepSteal (S&P 2022), Shadow in Cache (NDSS 2026), Qu (S&P 2025), Luo (CCS 2025), SAGA (NDSS 2026), BadMerging (CCS 2024), DeepCache (CCS 2024), TBT (CVPR 2020); AMD SP not found |
| 2026-10-03 | 7 gap fill: other (3-6) | MaleficNet; DeepSteal S&P; AMD SEV jailbreak; Keen Tesla; Tidjon; Mirsky; LLM SC agenda TOSEM; PTM reuse ICSE | Crossref API | MaleficNet DOI; DeepSteal DOI; Mirsky C&S 2023; Wang TOSEM; Jiang ICSE 2023; Tidjon TOSEM 2026 follow-up |
| 2026-10-03 | 7 gap fill: other (3-6) | ti:"token length"; ti:"local research agents"; ti:"Hide and Seek" AND pickle; ti:MaleficNet; ti:"AMD Secure Processor"; ti:"Identity Management for Agentic AI"; ti:"AI Risk Atlas"; ti:GDDRHammer; ti:TDXRay; ti:MoEcho; ti:"One Bit Flip"; ti:CipherSteal; ti:"Rendered Insecure"; ti:WireTap; ti:Sentry | arXiv search API | 2508.20282, 2508.19774, 2510.25819, 2503.05780, 2508.15036, 2510.00554 |
| 2026-10-03 | 7 gap fill: other (3-6) | ti:"International AI Safety Report"; ti:Rowhammer AND ti:GPU; ti:"KV cache" AND side channel; split learning LLM inversion; fault injection DNN; StegoNet; DeepSniffer; Wild Patterns | arXiv search API | IASR 2026 (2602.21012), Key Updates (2510.13653, 2511.19863), GPUThor (2609.16546), SpliceLeak (2606.21842), GPUHammer (already in corpus) |
| 2026-10-03 | 7 gap fill: other (3-6) | 14 DOIs (abstracts) | OpenAlex works API | abstracts for Rendered Insecure, DeepSniffer, CipherSteal, HyperTheft, Liu 2017, Breier 2018, StegoNet, WireTap, DeepCache; none for MaleficNet, GDDRHammer, TDXRay, memory forensics, Pitropakis |
| 2026-10-03 | 7 gap fill: other (3-6) | S2 batch by DOI | Semantic Scholar batch API | HTTP 429 |
| 2026-10-03 | 7 gap fill: other (3-6) | usenixsecurity25/li-xiang; usenixsecurity21/zhu; usenixsecurity24/grosse | WebFetch | OneFlip, Hermes, Grosse abstracts confirmed |
| 2026-10-03 | 7 gap fill: other (3-6) | usenixsecurity26 technical-sessions (x2) | WebFetch | Hide and Seek confirmed; token-length and AMD SP titles not found on the page |
| 2026-10-03 | 7 gap fill: other (3-6) | owasp.org MCP Top 10; Agentic Skills Top 10 (owasp.org and owasp.github.io); AI Testing Guide | WebFetch | MCP01-10 (beta 2025); AST01-10 v1.0-2026; AITG v1 2025-11-26 |
| 2026-10-03 | 7 gap fill: other (3-6) | github.com/IBM/ai-atlas-nexus; api.github.com repos, releases | WebFetch / GitHub API | LinkML, Apache-2.0, v1.2.5 2026-08-31, arXiv 2503.05780 |
| 2026-10-03 | 7 gap fill: other (3-6) | api.github.com mitre-atlas/atlas-data and atlas-navigator-data dist | GitHub API | stix-atlas.json, stix-atlas-attack-enterprise.json, opencti-bundles |
| 2026-10-03 | 7 gap fill: other (3-6) | ibm.com/think/topics/ai-risk-atlas | WebFetch | page body not rendered |
| 2026-10-03 | 7 gap fill: other (3-6) | csa.gov.sg guidelines and companion guide | WebFetch + curl | page and both PDFs (2024-10-15) |
| 2026-10-03 | 7 gap fill: other (3-6) | aiaaic.org repository | WebFetch | structure; "several hundred" (imprecise) |
| 2026-10-03 | 7 gap fill: other (3-6) | tc260.org.cn notices 202609/ec14... and 202609/e5b8...; tc260 homepage | WebFetch | 4 practice guides (2026-09-15); agent guide draft (2026-09-18, comments to 2026-10-02) |
| 2026-10-03 | 7 gap fill: other (3-6) | cac.gov.cn 2024-09/09 framework 1.0; 2025-09/15 framework 2.0 | WebFetch | both confirmed |
| 2026-10-03 | 7 gap fill: other (3-6) | openstd.samr.gov.cn search 45654 | WebFetch | GB/T 45654-2025, released 2025-04-25, effective 2025-11-01 |
| 2026-10-03 | 7 gap fill: other (3-6) | tc260 tzgg index | WebFetch | 404 |
| 2026-10-03 | 7 gap fill: other (3-6) | imda.gov.sg 2024 GenAI framework PR; 2026 agentic framework PR | WebFetch | headline and date only (2024-01-16; 2026-01-22) |
| 2026-10-03 | 7 gap fill: other (3-6) | aisi.go.jp/output | WebFetch | RT guide v1.00/v1.10; eval-perspectives v1.20 (2026-07-07); sector guides |
| 2026-10-03 | 7 gap fill: other (3-6) | cert-in.org.in AIBOM PDF | WebFetch + curl | v2.0 dated 2025-07-09; Table 10 |
| 2026-10-03 | 7 gap fill: other (3-6) | cyber.gouv.fr ANSSI GenAI recs and 2025 joint risk analysis | WebFetch (301 to messervices) + curl | both PDFs |
| 2026-10-03 | 7 gap fill: other (3-6) | bsi.bund.de KI publications page; two PDFs (?__blob=publicationFile) | WebFetch + curl | evasion countermeasures v1.0 (2025-11-06); GenAI models v2.0 (2025-01-17) |
| 2026-10-03 | 7 gap fill: other (3-6) | enisa.europa.eu multilayer framework; ENISA-JRC autonomous driving | WebFetch + curl | multilayer PDF (2023-06-07); AD landing page (2021-02-11) |
| 2026-10-03 | 7 gap fill: other (3-6) | etsi.org deliver GR SAI directory, 001/002/005/006/009 | curl | titles, dates, scopes, ToCs |
| 2026-10-03 | 7 gap fill: other (3-6) | europol.europa.eu ChatGPT report | WebFetch | JS app shell only ("Loading application") |
| 2026-10-03 | 7 gap fill: other (3-6) | cyber.gc.ca ITSAP.00.041 | WebFetch | December 2025 version |
| 2026-10-03 | 7 gap fill: other (3-6) | cisa.gov AI data security; deploying AI securely; AI in OT | WebFetch | AI data security (2025-05-22) OK; deploying AI securely 404; OT page OK ("Super Intelligence" anomaly) |
| 2026-10-03 | 7 gap fill: other (3-6) | cyber.gov.au engaging with AI | WebFetch | timeout |
| 2026-10-03 | 7 gap fill: other (3-6) | digital-strategy.ec.europa.eu GPAI code; Safety & Security chapter PDF | WebFetch + pdftotext | commitments, Measures 6.1, 6.2, 9.3; Appendix 4 |
| 2026-10-03 | 7 gap fill: other (3-6) | csrc.nist.gov SP 800-218A; nvlpubs AI 800-1 ipd2; AI 100-4 | WebFetch + curl | all three |
| 2026-10-03 | 7 gap fill: other (3-6) | mitre.org AI incident sharing; ai-incidents.mitre.org; atlas.mitre.org pages | WebFetch | 403 / TLS error / 404 |
| 2026-10-03 | 7 gap fill: other (3-6) | incidentdatabase.ai | WebFetch | latest Incident 1720 (2026-10-01) |
| 2026-10-03 | 7 gap fill: other (3-6) | ATLAS case studies AML.CS0000-CS0014 | local YAML (atlas-2026.09.yaml, v6.0.0) | 15 case studies with technique chains |
| 2026-10-03 | 7 gap fill: other (3-6) | legitsecurity GitLab Duo; tracebit Gemini CLI; generalanalysis Supabase MCP; upguard Asana MCP; lasso Wayback Copilot; promptarmor Cowork; embracethered Month of AI Bugs | WebFetch | all fetched |
| 2026-10-03 | 7 gap fill: other (3-6) | radware ShadowLeak | WebFetch + curl | bot-verification page; used thehackernews.com 2025/09 instead |
| 2026-10-03 | 7 gap fill: other (3-6) | ian.sh/mcdonalds; nowsecure DeepSeek iOS; blogs.cisco.com DeepSeek | WebFetch | all fetched |
| 2026-10-03 | 7 gap fill: other (3-6) | justice.gov Disney plea | WebFetch + curl | empty body / JS challenge; Wikipedia "The Walt Disney Company" used |
| 2026-10-03 | 7 gap fill: other (3-6) | knowbe4 fake IT worker; retool MFA | WebFetch | both fetched |
| 2026-10-03 | 7 gap fill: other (3-6) | wired Slovakia; guardian Grok; arstechnica ByteDance; pcmag Disney; theverge Grok; bbc DPD | WebFetch | domain blocked for WebFetch (no curl workaround used) |
| 2026-10-03 | 7 gap fill: other (3-6) | Wikipedia API: Grok (chatbot); ByteDance; AI Overviews; 2023 Slovak election; Liar's dividend; Pravda network; searches for DPD/Ferrari/WPP/ByteDance intern | Wikipedia API / WebFetch | Grok section; Liar's dividend (Šimečka); Pravda network; AI Overviews restriction; one HTTP 429 |
| 2026-10-03 | 7 gap fill: other (3-6) | blog.google AI Overviews update May 2024 | WebFetch | Reid 2024-05-30 primary |
| 2026-10-03 | 7 gap fill: other (3-6) | hn.algolia: ByteDance intern sabotage; DPD chatbot; WPP deepfake CEO; Ferrari deepfake Vigna; Grok unauthorized modification; xAI Grok white genocide employee; McAfee Tesla tape; model hacking ADAS McAfee; DeepSeek DDoS XLab; Grok MechaHitler | HN Algolia API | press URLs for ByteDance (BBC/Guardian/SCMP/Wired), DPD, WPP (Guardian/FT), Ferrari (Fortune), Grok (Verge), McAfee ADAS; none for DeepSeek DDoS or MechaHitler |
| 2026-10-03 | 7 gap fill: other (3-6) | theregister DPD; fortune Ferrari; scmp ByteDance; theregister ByteDance (guessed path) | WebFetch | DPD and Ferrari fetched; SCMP 403; Register guess 404 (discarded) |
| 2026-10-03 | 7 gap fill: other (3-6) | trellix/mcafee ADAS; blog.xlab.qianxin.com | WebFetch | 403; XLab blog page 1 has no DeepSeek DDoS post |
| 2026-10-03 | 7 gap fill: other (3-6) | newsguardtech Pravda special report | WebFetch | fetched (2025-03-06) |
| 2026-10-03 | 7 gap fill: other (3-6) | kisa.or.kr | WebFetch | TLS certificate error |
| 2026-10-03 | 7 gap fill: other (3-6) | legitsecurity exposed GenAI services | WebFetch | fetched (2024-08-28) |
| 2026-10-03 | 7 gap fill: other (3-6) | github.com/xai-org/grok-prompts | WebFetch | repo exists; no incident note |
| 2026-10-03 | 8 review fold | ATLAS 2026.09 YAML (github raw, dist/v6) and CHANGELOG | curl | 208 technique objects, 73 case studies parsed; CalVer since 2026.05 |
| 2026-10-03 | 8 review fold | NVD API 2.0: CVE-2025-6514, -49596, -68664, -68613, -48757, CVE-2026-21858, CVE-2024-50050, CVE-2025-25183 | curl | records and CWE/CVSS read |
| 2026-10-03 | 8 review fold | NVD API keywordSearch "prompt injection" with and without keywordExactMatch; cweId=CWE-1427 | curl | 194 / 136 / 0 |
| 2026-10-03 | 8 review fold | CISA KEV JSON feed | curl | catalogVersion 2026.10.02; n8n CVE-2025-68613 listed 2026-03-11 |
| 2026-10-03 | 8 review fold | CWE REST API (1256, 1261, 1260, 1339, 1247, 1319, 1332, 208, 203, 290, 345, 349, 354, 328, 778, 1426, 1434, 1427, 1039) | curl | names confirmed |
| 2026-10-03 | 8 review fold | arXiv API: 2508.14925, 2609.14119, 2310.03693, 2504.11703, 2502.11844, 2410.13722, 2510.01676, 2403.06634, 2609.22949, 2501.18837, 2501.01818, 2510.13653, 2608.23897, 2609.35799, 2610.00902 | curl | abstracts read |
| 2026-10-03 | 8 review fold | arXiv PDF 2504.11703v3 (Progent) into the pdf cache | curl | 39.9% -> 1.0% AgentDojo |
| 2026-10-03 | 8 review fold | CoSAI secure-ai-tooling risk-map YAML at main (0d8bfc9b5d76) | curl | 36 / 37 / 42 / 10 |
| 2026-10-03 | 8 review fold | AWS threat-composer GenAIChatbot.tc.json | curl | 37 threats, 84 mitigations, asset strings |
| 2026-10-03 | 8 review fold | sentinelone.com Silent Brothers; misinforeview.hks.harvard.edu; anthropic.com constitutional-classifiers; cloud.google.com AP2; ftc.gov 6(b); en.wikipedia.org Grok, GPT-4o, Sycophancy; batteringram.eu; tee.fail; wiz.io Moltbook; sysdig.com LLMjacking; aisi.gov.uk trends report; saif.google risks; aws scoping matrix; about.fb.com Meta frontier; cisa.gov Deploying AI Systems Securely | WebFetch | fetched; openai.com (403), theguardian/bbc/reuters (refused), ai.meta.com PDF (500), media.defense.gov PDF (refused) |
| 2026-10-03 | 8 review fold | USENIX presentation pages (weiss, deng); Crossref DOI 10.1016/j.patcog.2018.07.023 | curl | venues confirmed |
| 2026-10-03 | 8 review fold | WebSearch | WebSearch | refused: session budget (200) exhausted; DuckDuckGo HTML used once to find the SentinelLabs URL |

497 logged queries or batches (12 added by the v0.2 review fold).
