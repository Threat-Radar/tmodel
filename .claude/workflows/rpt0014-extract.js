export const meta = {
  name: 'rpt0014-extract',
  description: 'RPT-0014 #73: full FX-TM / FX-AP extraction of assigned AI threat-model and attack-paper units, each adversarially verified',
  whenToUse: 'A student runs their assigned extraction units from their #73 lane issue. args: {units: ["TM-014-biml-78", ...], pdf: "~/tmodel-pdf-cache/ai-threat-model", today: "YYYY-MM-DD", effort: "max"}',
  phases: [
    { title: 'Extract', detail: 'one agent per unit, reading the source' },
    { title: 'Verify', detail: 'fresh adversarial verifier per unit' },
  ],
}
// Run from the repo (or worktree) root: agents use repo-relative paths.
const R = 'research/0014-ai-threat-model'
const E = `${R}/extractions`
const PDF = (args && args.pdf) || '~/tmodel-pdf-cache/ai-threat-model'
const TODAY = (args && args.today) || 'today'
const EFFORT = (args && args.effort) || 'max'

const UNITS = {
  'TM-041-cosai-risk-map': ['FX-TM', 'TM-041 CoSAI Risk Map (S-0900) with TM-040 Google SAIF risk map (S-0780). Machine-readable source: clone github.com/cosai-oasis/secure-ai-tooling (record the commit; round 1 used 0d8bfc9b5d76) and convert ALL risks, controls, components and personas losslessly (Apache-2.0, so full text is allowed). Map the SAIF risks to the CoSAI risks.'],
  'TM-026-aws-threat-composer-genai': ['FX-TM', 'TM-026 AWS Threat Composer GenAI chatbot example (S-0950; the GenAIChatbot .tc.json example in github.com/awslabs/threat-composer): every threat statement, mitigation, assumption, DFD element and asset string. Include TM-025 (S-0738) and TM-126 Scoping Matrix (S-1178) as method context. Check the license.'],
  'TM-014-biml-78': ['FX-TM', 'TM-014 BIML Architectural Risk Analysis of ML Systems (S-0728; biml-ara-ml-2020.pdf): all 78 risks with component ids, the 9-component model and the top-10 list.'],
  'TM-024-biml-81-llm': ['FX-TM', 'TM-024 BIML Architectural Risk Analysis of LLMs (S-0739; biml-ara-llm-2024.pdf): all 81 risks, the component model with the vendor black-box boundary, and the top lists.'],
  'TM-058-csa-maestro': ['FX-TM', 'TM-058 CSA MAESTRO (S-0754): the 7 layers, the threats per layer, cross-layer threats and mitigations. Applied cases TM-090 (S-0766) and TM-080 (S-0755) go in examples/.'],
  'TM-059-owasp-agentic-threats': ['FX-TM', 'TM-059 OWASP Agentic AI Threats and Mitigations T1-T17 (S-0760), plus the OWASP Top 10 for Agentic Applications 2026 ASI01-ASI10 (find its S-id; its Appendix A maps ASI to T-codes): every entry, the navigator decision path, the mitigation playbooks and the ASI-to-T mapping. CC BY-SA.'],
  'TM-060-owasp-mas-guide': ['FX-TM', 'TM-060 OWASP Multi-Agentic System Threat Modelling Guide v1.0 (S-0761): the method, every threat, and the 3 worked examples as fixtures.'],
  'CAT-owasp-llm-top10-2025': ['FX-TM', 'OWASP Top 10 for LLM Applications 2025 (find its S-id; S-0883 is v1.1): each LLM01-10:2025 entry with its description, examples, mitigations and attack scenarios (in examples/), plus the v1.1-to-2025 alias table. CC BY-SA.'],
  'TM-004-nist-ai-100-2-e2025': ['FX-TM', 'TM-004 NIST AI 100-2 E2025 (S-0855). Public domain: full text is allowed. Extract the full PredAI and GenAI taxonomy trees: every class and subclass with its NISTAML id, the attacker goals, capabilities and knowledge, the mitigations per class, the limitations and open challenges, and the relevant glossary terms.'],
  'CAT-mitre-atlas-2026-09': ['FX-TM', 'MITRE ATLAS 2026.09 (github.com/mitre-atlas/atlas-data, dist/ATLAS.yaml at the 2026.09 tag; read the changelog): every tactic, technique, sub-technique and mitigation, with maturity and ATT&CK references, plus the 73 case studies as examples/. Crosswalk to AIT ids in both directions. Check the license.'],
  'TM-099-rand-model-weights': ['FX-TM', 'TM-099 RAND Securing AI Model Weights (S-0793): the levels OC1-OC5, every attack vector with its feasibility per OC level, and SL1-SL5 with their benchmarks. All rights reserved: paraphrase.'],
  'TM-012-microsoft-ai-threat-models': ['FX-TM', 'The Microsoft family: TM-012 (S-0727), TM-013 Failure Modes in ML (S-0872), TM-063 Agentic Failure Modes v2.0 (S-0902), and TM-032 the AI Red Team ontology (S-0753). Every failure mode and threat with its classification, the ontology fields, and the case studies.'],
  'TM-064-agentic-threat-frameworks': ['FX-TM', 'TM-064 ATFAA/SHIELD (S-0759); TM-095 Promptware Kill Chain (S-0821; its 36 cases in examples/); TM-069 Agent Security is a Systems Problem (S-0769; its principles and 11 incidents); TM-070/071 lethal trifecta (S-0820) and Rule of Two (S-0808), encoded as machine-checkable rules in examples/rules.yaml.'],
  'TM-084-mcp-threat-models': ['FX-TM', 'MCP threat models: MCP-38 (S-0909), CoSAI MCP Security MCP-T1..T12 (S-0770), the MCP spec Security Best Practices (S-0829), Hou et al. (S-0757) and OWASP MCP Top 10 (S-0898). Build one cross-mapping across all five.'],
  'TM-043-dasf-and-safe-ai': ['FX-TM', 'TM-043 Databricks DASF 2.0/3.0 (S-0779): every risk and control by component. TM-045 MITRE SAFE-AI (S-0809): its 4 elements, the ATLAS mapping and the NIST 800-53 mapping tables.'],
  'TM-005-asset-centric-models': ['FX-TM', 'Asset and attacker models: TM-010 Intel asset-centric (S-0762), TM-008 STRIDE-AI (S-0731), TM-005 Grosse et al. (S-0740), TM-034 LINDDUN GenAI (S-0773), TM-007 ADMIn (S-0737), TM-020 Trail of Bits YOLOv7 (S-0735). Put one consolidated candidate asset vocabulary in design-notes.md.'],
  'S-papers-prompt-injection': ['FX-AP', 'One subdirectory per paper: Greshake et al. indirect PI (S-0166); Liu et al. Formalizing and Benchmarking PI (USENIX Sec 2024); AgentDojo; CaMeL (S-0388); the adaptive-attack papers S-0443 and S-0486; Progent (S-0463).'],
  'S-papers-poisoning-backdoor': ['FX-AP', 'One subdirectory per paper: Carlini web-scale poisoning (S-0231); the 250-documents paper (S-0466); Sleeper Agents; PoisonedRAG; BadNets; AgentPoison.'],
  'S-papers-privacy-extraction': ['FX-AP', 'One subdirectory per paper: Shokri MIA; Carlini Extracting Training Data (2021); Nasr Scalable Extraction (2023); Carlini Stealing Part of a Production LM (2024); Tramer Stealing ML Models (2016); Duan MIAs on LLMs (S-0251).'],
  'S-papers-jailbreak-alignment': ['FX-AP', 'One subdirectory per paper: Zou GCG; PAIR; many-shot jailbreaking; Crescendo; Qi fine-tuning compromises safety; Arditi refusal direction.'],
  'S-papers-supply-chain-infra': ['FX-AP', 'One subdirectory per paper: MalHug (S-0355); stealthy pickle (S-0587); MCP server census (S-0534); agent-skills marketplace study (S-0550); LeftoverLocals (CVE-2023-4969); Weiss et al. token-length side channel.'],
  'S-papers-classical-adversarial': ['FX-AP', 'One subdirectory per paper: Szegedy Intriguing Properties; Goodfellow FGSM; Carlini & Wagner 2017; Madry PGD; Biggio & Roli Wild Patterns; Papernot SoK (S-0673).'],
}

const want = (args && args.units) || []
const bad = want.filter(u => !UNITS[u])
if (bad.length) throw new Error(`unknown units: ${bad.join(', ')}. Known: ${Object.keys(UNITS).join(', ')}`)
if (!want.length) throw new Error('pass args.units (see your lane issue)')

const COMMON = `You are performing a FULL EXTRACTION for RPT-0014 (Threat-Radar/tmodel #73). Work from the repository root. Read ${E}/README.md first; it defines the profiles FX-TM and FX-AP, the file set, the completeness header, the quoting and licensing rules (the repo is PUBLIC) and the passes. Follow it exactly. A summary is NOT an extraction: capture EVERY entry the source enumerates.
Inputs: ${R}/sources.md (S-ids and citations), ${R}/pdf-manifest.tsv (cached PDF file, sha256, S-id, URL), ${R}/threat-models.md, ${R}/attack-catalog.yaml (AIT ids), ${R}/enumerations.md. The PDF cache is ${PDF}/; if a file is missing, run bin/fetch-pdfs or fetch it yourself into ${PDF}/. NEVER put a PDF or other third-party binary inside the repo. Clone third-party repos only to a temp dir outside the repo.
YAML must parse (python3 -c "import yaml; yaml.safe_load(open(F))"). Every entry carries a locator. Today is ${TODAY}.`

phase('Extract')
const results = await pipeline(want,
  u => agent(`${COMMON}\n\nPROFILE: ${UNITS[u][0]}. UNIT DIRECTORY: ${E}/${u}/ (for multi-source units, one subdirectory per source inside it).\nUNIT: ${UNITS[u][1]}\nRETURN a short report: the files written, source vs extracted counts, anything unreadable, and anything N/A with the reason.`,
    { label: `extract:${u}`, phase: 'Extract', effort: EFFORT }),
  (ex, u) => agent(`${COMMON}\n\nYou are the ADVERSARIAL VERIFIER (pass 2) for ${E}/${u}/ (unit: ${UNITS[u][1]}). You did not extract it; assume it is wrong and incomplete. From the SOURCE: (1) recount the source's entries and add every dropped or merged one; (2) check at least 25 locators and every verbatim quote, and enforce the licensing rule; (3) check the numbers in FX-AP attacks.yaml against the cited tables; (4) spot-check 15 crosswalk mappings against ATLAS 2026.09, OWASP:2025 and CWE 4.20; (5) confirm the required files exist or are N/A with a reason, and that the YAML parses. Fix defects in place. Write ${E}/${u}/verify.md: the defects found, the fixes, the residual issues, and proposed corrections to sources.md, threat-models.md and attack-catalog.yaml, including missing AIT techniques. Do NOT edit those three files. The extractor reported: ${String(ex).slice(0, 3000)}\nRETURN: defect counts by kind, final counts, residual issues.`,
    { label: `verify:${u}`, phase: 'Verify', effort: EFFORT }).then(v => ({ unit: u, verify: v })))
return results.filter(Boolean)
