---
schema: "archdoc/v1"
id: RPT-0014-dimensions
title: "RPT-0014 dimensions: the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-03"
record: RPT-0014
---

# RPT-0014: search dimensions

The search axes for #72, one section per dimension, with the questions each must answer. Dimensions 1 to 6 were run as parallel agents on 2026-10-02. Dimension 7 is the adversarial coverage review and the two gap-fill passes on 2026-10-03. Dimension 8 is the synthesis that produced the derived artifacts. Each maps to sections of [report.md](report.md).

Every dimension records, per source: citation, type (paper, survey, threat-model, framework, standard, catalog, dataset, tool, vendor-research, advisory, news), how it was confirmed, cached PDF (filename and sha256, cache outside every repo), attack classes, a technical summary, a threat-model mapping (*asset or component -> threat -> precondition -> impact*), catalog ids (ATLAS, OWASP LLM, OWASP Agentic, OWASP ML, NIST AI 100-2, CWE) and confidence.

## 1. Attacks on the ML model itself (predictive and foundation models)

Scope: evasion and adversarial examples (digital, physical, audio, text, graph, RL), poisoning and backdoors (availability, targeted, clean-label, trojan, web-scale, pretraining, instruction tuning, RLHF, federated), model extraction and stealing, membership, attribute and property inference, model inversion, training-data extraction, gradient inversion, watermark and fingerprint removal, energy-latency attacks, hardware fault and bit-flip attacks on weights.

1. Which attack classes exist, and what is the seminal and the current state-of-the-art paper for each?
2. What attacker access (none, query, data contribution, training control, white-box, physical) and knowledge does each assume, and is that realistic for deployed systems?
3. Which asset does each damage, and through which property (C, I, A, privacy, safety)?
4. Is the attack demonstrated against a production system or only in the lab?
5. Which defenses exist, and were they evaluated against adaptive attackers?
6. Which ATLAS, OWASP ML, NIST AI 100-2 and CWE ids apply, and where does no id apply?

Report: sections 2 and 3 (evasion, poisoning, privacy, model theft, hardware).

## 2. Attacks on LLM applications, RAG and agents

Scope: direct and indirect prompt injection, jailbreaks (manual, optimization-based, multi-turn, many-shot, multimodal), system-prompt and data leakage, improper output handling, RAG and vector-store poisoning and extraction, embedding inversion, agent hijacking and tool misuse, MCP and tool poisoning, memory poisoning, multi-agent propagation, computer-use and browser agents, denial of service and denial of wallet, harmful fine-tuning, watermark attacks; defenses as context.

1. What is the mechanism and the root cause (for example, no channel separation between instructions and data)?
2. Which channel carries the attacker's content (user turn, web page, email, document, tool output, memory, peer agent, image, audio)?
3. Which agent capability turns injection into damage (tool, credential, egress, state change)?
4. Which defenses hold up under adaptive evaluation, and which are system-level rather than model-level?
5. Which benchmarks measure each class (AgentDojo, InjecAgent, HarmBench, WASP and others)?
6. Which ids apply in ATLAS 2026.09, OWASP LLM 2025, OWASP Agentic 2026, NIST AI 100-2 and CWE-1426/1427?

Report: sections 2, 3 (prompt injection, jailbreak, leakage, RAG, agents, multi-agent), 4.

## 3. AI supply chain, infrastructure, and AI as an attacker tool

Scope: malicious model files and loaders, model-hub abuse (namespace reuse, typosquatting, org confusion), poisoned adapters and templates, ML dependency compromise, package hallucination, MLOps and inference-server vulnerabilities, tenant isolation on AI platforms, exposed AI data stores, GPU and serving side channels, TEEs, model-weight theft, LLMjacking; AI-enabled offense (autonomous intrusion, exploit development, AI-querying malware, phishing, deepfakes, influence operations).

1. Which artifacts in the AI supply chain execute code or carry behaviour, and which controls (formats, scanners, signing, AI BOM) fail?
2. Which AI infrastructure components are exposed or vulnerable, with CVEs and in-the-wild exploitation?
3. What is the evidence for AI uplift to attackers: lab benchmarks, government evaluations, vendor threat intelligence, and incidents?
4. Which provider-level controls (security levels for weights, abuse detection) exist?

Report: sections 2, 3 (supply chain, infrastructure, AI-enabled offense), 4.

## 4. AI security incidents in the news (2016 to 2026)

1. What happened, when, to which product or organization, through which attack class, with what impact?
2. What is the primary source (vendor advisory, researcher disclosure, court record, government statement), and what is press only?
3. Was it exploited in the wild, a disclosed vulnerability, a red-team demonstration, a non-adversarial failure, or a threat-intelligence report?
4. Does ATLAS publish a case study for it?
5. What patterns repeat across incidents?

Output: [incidents.md](incidents.md). Report: section 3 (in-the-wild evidence per class) and section 8.

## 5. Weakness and attack enumerations: is there a CWE for AI?

1. Which CWE entries are AI-specific, in which release, and what is in the CWE AI Working Group pipeline?
2. How are AI vulnerabilities typed in CVE and NVD in practice?
3. Which attack enumerations (ATLAS, CAPEC) and risk lists (OWASP LLM, Agentic, ML, MCP, Skills; NIST AI 100-2; SAIF and CoSAI; DASF; Cisco; MIT AI Risk Repository; AVID; incident databases) exist, with scope, id scheme, count, version, format and licence?
4. Who officially maps what to what, and where are the crosswalks missing or broken (id drift)?
5. What is not enumerated anywhere?

Output: [enumerations.md](enumerations.md). Report: section 6.

## 6. Published AI threat models and methodologies

1. Which published threat models and methods target ML, LLM applications, RAG, agents, MCP and AI supply chains, from academia, vendors, standards bodies and governments?
2. For each: the decomposition (components, layers, lifecycle stages, assets), the asset model, the threat categories, the attacker model, the method (STRIDE variant, ARA, attack trees, attack graphs, capability composition, checklist), machine-readability and validation.
3. Which are worked examples that can serve as gold sets for evaluating generated threat models?
4. Which tools already generate AI-aware threat models (comparators for tmodel)?

Output: [threat-models.md](threat-models.md); each entry is captured for detailed analysis in #73. Report: section 5.

## 7. Adversarial coverage review and gap fill

1. Is coverage of technical papers complete against the top-venue programs (IEEE S&P, USENIX Security, CCS, NDSS, SaTML, NeurIPS/ICML/ICLR, ACL/EMNLP) and against highly cited work?
2. Are any citations fabricated, mis-attributed, or carrying a wrong id, CVE or venue?
3. Are confidence ratings calibrated to what was actually verified?
4. Are duplicate works recorded under several ids?
5. Are catalog ids current for the pinned catalog versions?

Output: the gaps-papers and gaps-other raw files (Corrections sections applied in [sources.md](sources.md)). Report: method section.

## 8. Synthesis: derived artifacts for threat-model generation

1. What reference architecture of an AI-enabled enterprise system lets generic attacks map onto company components and trust boundaries?
2. Which attack classes threaten which enterprise assets (asset x attack matrix)?
3. What record does each attack technique need (access, knowledge, assets, components, preconditions, impacts, incidents, mitigations, catalog ids, sources, maturity)?
4. What node and edge types does the evidence require in the tmodel object model (ARCH-0001 section 3)? Proposals only; DEC-001, DEC-008 and DEC-009 stay open.

Output: [attack-catalog.yaml](attack-catalog.yaml); report sections 1, 2, 4, 7 and 9.
