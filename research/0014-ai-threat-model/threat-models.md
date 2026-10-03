---
schema: "archdoc/v1"
id: RPT-0014-threat-models
title: "RPT-0014 catalog of AI threat models and methods"
type: research
status: draft
version: "0.2.0"
date: "2026-10-02"
updated: "2026-10-03"
record: RPT-0014
---

# RPT-0014: catalog of published AI threat models and methodologies

Every published AI threat model and threat-modeling method this run found: academic, vendor, standards-body and government. Each entry is captured for later detailed analysis (#73). Pure enumerations (ATLAS, the OWASP Top 10 lists, CWE, AVID, the MIT AI Risk Repository) are surveyed in [enumerations.md](enumerations.md), not here; an entry appears here when it defines a decomposition, an attacker or asset model, or a method for producing a threat model.

**Fields.** *Decomposition* is how the model cuts up the system (components, layers, lifecycle stages, assets, stakeholders). *Assets* is what it protects. *Threat categories* is its threat vocabulary. *Method* is how a practitioner uses it. *Machine-readability* is whether a structured, importable form exists (confirmed only where an agent fetched it). The fields are condensed by the synthesis agent from the captured source summaries ([sources.md](sources.md)); entries marked `?` were not read beyond a landing page. **Everything here is an AI-written summary and needs checking against the source in #73.**

**Groups.** A: foundational ML and predictive-AI models. B: LLM-application and GenAI models, including vendor and government frameworks. C: agentic, multi-agent and protocol (MCP, A2A) models. D: asset-specific (model weights), frontier-model, sector (automotive, OT) and governance models. E: tools that generate AI-aware threat models; they are comparators for tmodel itself.

## A. Foundational ML / predictive-AI threat models and methods

### TM-001 SoK: Security and Privacy in ML (Papernot et al.)

- **Source:** S-0673: N. Papernot, P. McDaniel, A. Sinha, M. Wellman, "SoK: Security and Privacy in Machine Learning", IEEE EuroS&P 2018. DOI 10.1109/EuroSP.2018.00035. Preprint: "Towards the Science of Security and Privacy in Machine Learning", arXiv:1611.03814 [link](https://arxiv.org/abs/1611.03814) (type survey; confidence high)
- **Decomposition:** ML data pipeline: physical domain -> digital representation -> model -> action; training vs inference stage.
- **Assets:** training data, model, inference inputs and outputs.
- **Threat categories:** Confidentiality, integrity, availability plus privacy; attacks per stage (poisoning, evasion, extraction, inference).
- **Method:** Adversary capability ordered weak to strong per stage (data injection/modification, logic corruption; output-only, oracle, white-box).
- **Machine-readability:** None (paper).
- **Cached PDF:** papernot-2016-towards-science-security-privacy-ml.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-002 Wild Patterns (Biggio & Roli): goal-knowledge-capability attacker model

- **Source:** S-0672: B. Biggio, F. Roli, "Wild patterns: Ten years after the rise of adversarial machine learning", Pattern Recognition 84:317-331, 2018. DOI 10.1016/j.patcog.2018.07.023; arXiv:1712.03141 [link](https://arxiv.org/abs/1712.03141) (type survey; confidence high)
- **Decomposition:** Attacker model triple: goal (violation, specificity), knowledge (perfect, limited, zero), capability (causative vs exploratory, data-manipulation constraints).
- **Assets:** classifier and its training data.
- **Threat categories:** Evasion and poisoning; C/I/A and privacy violations.
- **Method:** Security-evaluation framework and proactive vs reactive arms-race design.
- **Machine-readability:** None.
- **Cached PDF:** biggio-roli-2018-wild-patterns.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-003 On Evaluating Adversarial Robustness (threat-model specification checklist)

- **Source:** S-0058: N. Carlini, A. Athalye, N. Papernot, W. Brendel et al., "On Evaluating Adversarial Robustness", arXiv:1902.06705, 2019. [link](https://arxiv.org/abs/1902.06705) (type paper; confidence high)
- **Decomposition:** Explicit adversary specification: goals, knowledge, capabilities, perturbation set, query budget.
- **Assets:** ML classifier.
- **Threat categories:** Evasion; adaptive attacks.
- **Method:** Checklist for stating and testing robustness claims against adaptive attackers.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-004 NIST AI 100-2 E2025 adversarial ML taxonomy (attacker-model axes)

- **Source:** S-0855: A. Vassilev, A. Oprea, A. Fordyce, H. Anderson, X. Davies, M. Hamin, "Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations", NIST AI 100-2 E2025, March 2025. DOI 10.6028/NIST.AI.100-2e2025 [link](https://doi.org/10.6028/NIST.AI.100-2e2025) (type standard; confidence high)
- **Decomposition:** PredAI vs GenAI; attacker objective (availability, integrity, privacy, misuse); capability (training data, model, test data, label limit, source code, query, resource control); knowledge (white/grey/black box); lifecycle stage.
- **Assets:** data, model, API, RAG store, agent (implicit).
- **Threat categories:** NISTAML.01 availability, .02 integrity, .03 privacy, .04 misuse, .05 supply chain with 25+ leaf ids.
- **Method:** Taxonomy plus mitigations and their known limits per class.
- **Machine-readability:** PDF; stable NISTAML ids but no machine-readable release.
- **Cached PDF:** nist-ai-100-2-e2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-005 Towards More Practical Threat Models in AI Security (Grosse et al., USENIX Sec 2024)

- **Source:** S-0740: K. Grosse, L. Bieringer, T. R. Besold, A. Alahi, "Towards More Practical Threat Models in Artificial Intelligence Security", USENIX Security 2024. arXiv:2311.09994 [link](https://arxiv.org/abs/2311.09994) (type threat-model; confidence high)
- **Decomposition:** Written-down academic threat models for six attacks compared with the access patterns of 271 practitioners.
- **Assets:** deployed models and their data.
- **Threat categories:** Poisoning, backdoors, evasion, model stealing, membership and property inference.
- **Method:** Survey-based calibration of attacker preconditions (access, data fraction, query budget) to deployment reality.
- **Machine-readability:** None.
- **Cached PDF:** grosse-2024-practical-threat-models.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-006 Threat Assessment in ML-based Systems (Tidjon & Khomh)

- **Source:** S-0732: L. N. Tidjon, F. Khomh, "Threat Assessment in Machine Learning based Systems", arXiv:2207.00091, 2022 [link](https://arxiv.org/abs/2207.00091) (type threat-model; confidence high)
- **Decomposition:** 89 real-world attack scenarios (ATLAS, AIID, literature) coded to ATLAS TTPs per ML phase; 854 repositories' vulnerabilities.
- **Assets:** ML phases and models; ML libraries.
- **Threat categories:** ATLAS tactics/techniques; repository CWE classes.
- **Method:** Empirical TTP mining from incidents and CVEs.
- **Machine-readability:** None (paper).
- **Cached PDF:** tidjon-khomh-2022-threat-assessment-ml.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-007 ADMIn: Attacks on Dataset, Model and Input

- **Source:** S-0737: V. Kumar, J. Mayo, K. Bahiss, "ADMIn: Attacks on Dataset, Model and Input. A Threat Model for AI Based Software", arXiv:2401.07960, 2024. [link](https://arxiv.org/abs/2401.07960) (type threat-model; confidence high)
- **Decomposition:** AI software development process model + attack taxonomy by target: Dataset, Model, Input.
- **Assets:** dataset, model, input.
- **Threat categories:** Poisoning; extraction and backdoor; evasion.
- **Method:** Two-part model applied to two real AI systems.
- **Machine-readability:** None.
- **Cached PDF:** kumar-admin-ai-software-tm-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-008 STRIDE-AI (Mauri & Damiani)

- **Source:** S-0731: L. Mauri, E. Damiani, "Modeling Threats to AI-ML Systems Using STRIDE", Sensors 22(17):6662, 2022. DOI 10.3390/s22176662. Extended version of "STRIDE-AI: An Approach to Identifying Vulnerabilities of Machine Learning Assets", IEEE CSR 2021, Rhodes. [link](https://doi.org/10.3390/s22176662) (type threat-model; confidence high)
- **Decomposition:** ML lifecycle reference model; assets in six macro-categories (Data, Models, Actors, Processes, Tools, Artefacts, after ENISA); FMEA failure modes -> violated property -> STRIDE threat.
- **Assets:** requirements, raw data, labelled data, models, actors, processes, tools, artefacts.
- **Threat categories:** STRIDE per ML asset (poisoning, evasion, inversion, theft as examples).
- **Method:** Asset-centred FMEA + STRIDE with ML-specific property definitions (CIA3-R).
- **Machine-readability:** Tables in paper; transcribable to edges.
- **Cached PDF:** mauri-damiani-stride-ai-2022.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-009 Attack Tree Analysis for Adversarial Evasion Attacks

- **Source:** S-0736: Y. Yamaguchi, T. Aoki, "Attack Tree Analysis for Adversarial Evasion Attacks", arXiv:2312.16957, 2023. [link](https://arxiv.org/abs/2312.16957) (type threat-model; confidence high)
- **Decomposition:** Attack trees mixing ML attack nodes and conventional enabling attack nodes.
- **Assets:** ML classifier in a safety system.
- **Threat categories:** Evasion (white/black box) with enabling conventional attacks.
- **Method:** Three steps: literature matrix -> evasion scenarios -> tree; quantitative risk.
- **Machine-readability:** None (node types encodable).
- **Cached PDF:** yamaguchi-attack-tree-evasion-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-010 Threat Modeling for AI: the case for an asset-centric approach (Intel)

- **Source:** S-0762: J. R. Sanchez Vicarte, M. Spoczynski, M. Elsaid, "Threat Modeling for AI: The Case for an Asset-Centric Approach", arXiv:2505.06315, 2025. [link](https://arxiv.org/abs/2505.06315) (type threat-model; confidence high)
- **Decomposition:** Eight fundamental AI asset types (raw data, encoded data/embeddings, labels, metadata, weights, activations, ...) and adversary capabilities over each (influence, contribute, monitor, inspect, deny).
- **Assets:** the eight asset types with cross-model dependencies.
- **Threat categories:** Conventional and AI-specific vulnerabilities composed into capabilities.
- **Method:** Bottom-up: vulnerabilities grant capabilities over assets; an attack is in scope when every step's capability closes.
- **Machine-readability:** None.
- **Cached PDF:** sanchez-vicarte-asset-centric-tm-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-011 ThreatFinderAI: asset-centric threat modeling for AI-based systems

- **Source:** S-0744: J. von der Assen, J. Sharif, C. Feng, C. Killer, G. Bovet, B. Stiller, "Asset-centric Threat Modeling for AI-based Systems", arXiv:2403.06512, 2024. [link](https://arxiv.org/abs/2403.06512) (type threat-model; confidence high)
- **Decomposition:** Asset model of AI system; threat and countermeasure library from ENISA, OWASP AI and ATLAS; residual risk.
- **Assets:** data, model, pipeline assets.
- **Threat categories:** ENISA/OWASP/ATLAS threats.
- **Method:** Tool-guided asset modelling and risk quantification; user study recreating an expert model.
- **Machine-readability:** Tool (format not confirmed).
- **Cached PDF:** asset-centric-tm-ai-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-012 Microsoft: Threat Modeling AI/ML Systems and Dependencies (SDL supplement)

- **Source:** S-0727: A. Marshall, J. Parikh, E. Kiciman, R. Shankar Siva Kumar, "Threat Modeling AI/ML Systems and Dependencies", Microsoft Learn (AETHER Engineering Practices for AI WG), November 2019, page updated 2026-03. [link](https://learn.microsoft.com/en-us/security/engineering/threat-modeling-aiml) (type threat-model; confidence high)
- **Decomposition:** Redrawn trust boundaries: training data stores and providers in scope and assumed compromised; inventory of AI/ML dependencies.
- **Assets:** training data, model API, third-party models, presentation layers.
- **Threat categories:** 11 intentional threats (perturbation, poisoning, inversion, membership inference, stealing, reprogramming, physical, malicious provider, supply chain, backdoor, dependencies).
- **Method:** Security-review questions per consideration; each threat with traditional parallel and SDL severity.
- **Machine-readability:** HTML with regular structure.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-013 Failure Modes in Machine Learning (Kumar et al.)

- **Source:** S-0872: R. Shankar Siva Kumar, D. O'Brien, K. Albert, S. Viljoen, J. Snover, "Failure Modes in Machine Learning Systems", arXiv:1911.11034, 2019; also Microsoft Learn [link](https://learn.microsoft.com/en-us/security/engineering/failure-modes-in-machine-learning) (type catalog; confidence high)
- **Decomposition:** Two axes: intentional vs unintentional failures; each tagged with violated C/I/A.
- **Assets:** ML system.
- **Threat categories:** 11 intentional + 6 unintentional failure modes.
- **Method:** Taxonomy with scenarios; basis of the SDL AI bug bar.
- **Machine-readability:** None (paper/web).
- **Cached PDF:** kumar-failure-modes-ml-2019.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-014 BIML Architectural Risk Analysis of ML Systems (BIML-78)

- **Source:** S-0728: G. McGraw, H. Figueroa, V. Shepardson, R. Bonett, "An Architectural Risk Analysis of Machine Learning Systems: Toward More Secure Machine Learning", Berryville Institute of Machine Learning, v1.0, 2020-01-13. [link](https://berryvilleiml.com/results/ara.pdf) (type threat-model; confidence high)
- **Decomposition:** Generic ML system of nine components: processes (dataset assembly, learning algorithm, evaluation, inference) and things (raw data, datasets, inputs, model, outputs); 3 manipulation + 3 extraction attacks across 3 surfaces.
- **Assets:** the nine components.
- **Threat categories:** 78 risks with ids like [input:1:adversarial examples]; ranked top ten.
- **Method:** Design-level ARA: decompose, enumerate risks per component, rank.
- **Machine-readability:** Parseable ids; no structured export.
- **Cached PDF:** biml-ara-ml-2020.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-015 ENISA AI Threat Landscape (2020)

- **Source:** S-0729: ENISA, "Artificial Intelligence Cybersecurity Challenges: Threat Landscape for Artificial Intelligence", 2020-12-15. [link](https://www.enisa.europa.eu/publications/artificial-intelligence-cybersecurity-challenges) (type threat-model; confidence high)
- **Decomposition:** AI lifecycle reference model; asset inventory (data, models, actors, processes, environment/tools, artefacts); ENISA threat taxonomy (NAA, EIH, PA, UD, FM, OUT, DIS, LEG).
- **Assets:** asset categories across the lifecycle.
- **Threat categories:** 74 AI threats with affected assets and impact on AI properties; threats-to-lifecycle annex.
- **Method:** Asset -> threat -> lifecycle mapping.
- **Machine-readability:** PDF annexes.
- **Cached PDF:** enisa-ai-threat-landscape-2020.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-016 ENISA Securing Machine Learning Algorithms (2021)

- **Source:** S-0781: ENISA, "Securing Machine Learning Algorithms", December 2021. [link](https://www.enisa.europa.eu/publications/securing-machine-learning-algorithms) (type framework; confidence high)
- **Decomposition:** ML algorithm taxonomy -> threats -> vulnerabilities -> controls by lifecycle stage.
- **Assets:** ML algorithms and application components.
- **Threat categories:** Evasion, oracle, poisoning, model/data disclosure, compromise of ML components, failure.
- **Method:** Threat -> vulnerability -> control chain (Annexes B, C).
- **Machine-readability:** PDF annexes.
- **Cached PDF:** enisa-securing-ml-algorithms-2021.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-017 ETSI GR SAI 001 AI Threat Ontology

- **Source:** S-0834: ETSI ISG SAI, "Securing Artificial Intelligence (SAI); AI Threat Ontology", ETSI GR SAI 001 V1.1.1, 2022-01. [link](https://www.etsi.org/deliver/etsi_gr/SAI/001_099/001/01.01.01_60/gr_SAI001v010101p.pdf) (type standard; confidence high)
- **Decomposition:** Ontology: threat agent -> attack instance -> adversarial goal -> attack surface (data acquisition/curation, implementation, deployment, humans) -> trust model; TVRA extension for AI.
- **Assets:** AI system and lifecycle surfaces.
- **Threat categories:** Threat dimensions and attacker objectives.
- **Method:** Ontology + TVRA impact/likelihood.
- **Machine-readability:** Formal expression in report (no released ontology file found).
- **Cached PDF:** etsi-gr-sai-001-ai-threat-ontology.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-018 ETSI GR SAI 004 Problem Statement

- **Source:** S-0832: ETSI ISG SAI, "Securing Artificial Intelligence (SAI); Problem Statement", ETSI GR SAI 004 V1.1.1, 2020-12. [link](https://www.etsi.org/deliver/etsi_gr/SAI/001_099/004/01.01.01_60/gr_SAI004v010101p.pdf) (type standard; confidence high)
- **Decomposition:** C/I/A challenges per ML lifecycle stage; broader bias/ethics/explainability.
- **Assets:** ML lifecycle.
- **Threat categories:** Attack vectors with real-world use cases.
- **Method:** Problem statement (root of SAI series).
- **Machine-readability:** PDF.
- **Cached PDF:** etsi-gr-sai-004-v1-1-1.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-019 NCC Group: Practical Attacks on Machine Learning Systems

- **Source:** S-0972: C. Anley, "Practical Attacks on Machine Learning Systems", NCC Group whitepaper, 2022-07-06. [link](https://research.nccgroup.com/2022/07/06/whitepaper-practical-attacks-on-machine-learning-systems/) (type vendor-research; confidence high)
- **Decomposition:** ML attack surface including conventional components (notebooks, artifact stores, model loaders).
- **Assets:** model artifacts, loaders, notebooks, training data.
- **Threat categories:** Unsafe deserialization, perturbation, MIA, inversion, poisoning, credentials, dependency risks.
- **Method:** Reproductions + taxonomy.
- **Machine-readability:** Whitepaper.
- **Cached PDF:** nccgroup-practical-attacks-ml-2022.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-020 Trail of Bits YOLOv7 threat model and code review

- **Source:** S-0735: A. Crighton, A. Ghosh, H. Khlaaf, J. Miller, K. Willis, M. Domanski, S. Michaels, S. Hussain, W. Woodruff, "YOLOv7 Threat Model and Code Review", Trail of Bits, 2023-10-31. [link](https://github.com/trailofbits/publications/blob/master/reviews/2023-10-yolov7-securityreview.pdf) (type threat-model; confidence high)
- **Decomposition:** Components and trust zones (Internet, data sources, inference client, deployment network, model, inference server, training network/host, storage); actors (end user, dependency upstream, data upstream, network insider, local attacker, malicious contributor).
- **Assets:** training host, dataset, model file, inference server.
- **Threat categories:** Dataset poisoning, malicious config/model files to code execution, deserialization, dependency compromise, DoS.
- **Method:** NIST SP 800-154 / Mozilla RRA style worked model + code review (12 findings).
- **Machine-readability:** PDF tables.
- **Cached PDF:** tob-yolov7-securityreview-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-021 Trail of Bits: Toward Comprehensive Risk Assessments and Assurance of AI-Based Systems

- **Source:** S-0786: H. Khlaaf, "Toward Comprehensive Risk Assessments and Assurance of AI-Based Systems", Trail of Bits whitepaper, 2023-03-07. [link](https://raw.githubusercontent.com/trailofbits/publications/master/papers/trailofbits-20230307-ai-risk-assessments-whitepaper.pdf) (type framework; confidence medium)
- **Decomposition:** System-safety framing: hazards, operational design domain, assurance cases.
- **Assets:** AI-based system.
- **Threat categories:** System hazards, ML failure modes, security risks.
- **Method:** Hazard analysis + assurance argument; threat modeling as part of assurance.
- **Machine-readability:** Whitepaper (no catalog).
- **Cached PDF:** khlaaf-tob-ai-risk-assessments-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-022 NVIDIA AI Red Team assessment framework

- **Source:** S-0784: W. Pearce, J. Lucas, "NVIDIA AI Red Team: An Introduction", NVIDIA Technical Blog, 2023-06-14. [link](https://developer.nvidia.com/blog/nvidia-ai-red-team-an-introduction/) (type framework; confidence high)
- **Decomposition:** Matrix: governance/risk/compliance; ML development lifecycle (8 phases); technical stack x assessment areas (recon, technical vulns, model vulns, harm and abuse).
- **Assets:** ML lifecycle infrastructure and artifacts.
- **Threat categories:** Extraction, evasion, inversion, MIA, poisoning, traditional vulns, harm/abuse.
- **Method:** Assessment scoping matrix; tabletop scenarios.
- **Machine-readability:** Blog (narrative).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-023 "Real Attackers Don't Compute Gradients" (calibration)

- **Source:** S-0685: G. Apruzzese, H. S. Anderson, S. Dambra, D. Freeman et al., ""Real Attackers Don't Compute Gradients": Bridging the Gap Between Adversarial ML Research and Practice", IEEE SaTML 2023. arXiv:2212.14315 [link](https://arxiv.org/abs/2212.14315) (type survey; confidence medium (capped))
- **Decomposition:** Real-world adversary economics vs academic attacker models.
- **Assets:** deployed security ML (phishing, malware, moderation).
- **Threat categories:** Cheap problem-space evasion.
- **Method:** Position + case studies used to calibrate likelihood.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

## B. LLM-application and GenAI threat models

### TM-024 BIML Architectural Risk Analysis of LLMs (81 risks)

- **Source:** S-0739: G. McGraw, H. Figueroa, K. McMahon, R. Bonett, "An Architectural Risk Analysis of Large Language Models: Applied Machine Learning Security", BIML, v1.0, 2024-01-24. [link](https://berryvilleiml.com/results/BIML-LLM24.pdf) (type threat-model; confidence high)
- **Decomposition:** Five user-visible components (raw data, inputs, model, inference algorithm, outputs) + black-box foundation model hiding dataset assembly, datasets, learning, evaluation.
- **Assets:** LLM application components; risks behind the vendor boundary.
- **Threat categories:** 81 risks + 23 black-box risks; LLM top ten (recursive pollution, data debt, improper use, black-box opacity, prompt manipulation, poisoning, ...).
- **Method:** ARA per component; vendor trust boundary means owners accept or transfer many risks.
- **Machine-readability:** Parseable ids.
- **Cached PDF:** biml-ara-llm-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-025 AWS: Threat modeling your generative AI workload (+ re:Invent SEC214)

- **Source:** S-0738: D. Cortegaca, A. Malhotra, K. Abdol-Hamid, AWS Security Blog, 2024-11-18. ; re:Invent 2023 SEC214 deck [link](https://aws.amazon.com/blogs/security/threat-modeling-your-generative-ai-workload-to-evaluate-security-risk/) (type threat-model; confidence high)
- **Decomposition:** Shostack four questions; DFD; explicit assumptions; Threat Composer statement grammar ([source] with [prerequisites] can [action], leading to [impact] on [assets]).
- **Assets:** system prompt, patient/customer DBs, user data, model API.
- **Threat categories:** Prompt injection, data disclosure, extraction/distillation, poisoned adapters, malicious merging, prompt extraction.
- **Method:** Structured threat statements with prerequisites and impacted assets.
- **Machine-readability:** Threat Composer JSON (see S-id of the example workspace).
- **Cached PDF:** aws-reinvent-sec214-genai-tm-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-026 AWS Threat Composer GenAI chatbot example workspace

- **Source:** S-0950: AWS Labs, threat-composer, `packages/threat-composer/src/data/workspaceExamples/GenAIChatbot.tc.json`, commit 3d4ed92f96a2 (2026-09-23). [link](https://github.com/awslabs/threat-composer) (type dataset; confidence high)
- **Decomposition:** applicationInfo, architecture, dataflow, 13 assumptions, 37 threats, 84 mitigations, 95 + 122 links.
- **Assets:** free-text impacted assets that mix business and AI assets, for example "user data", "intellectual property", "business systems and workflows", "impacted individuals and sensitive data", "proprietary information", "the LLM model", "the LLM inference API" and "information in the knowledge base" (counted from the JSON, 2026-10-03); no controlled vocabulary.
- **Threat categories:** 37 structured threats (STRIDE-tagged).
- **Method:** Complete worked model in a published JSON schema.
- **Machine-readability:** Yes: JSON (published schema).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-027 NCC Group: Models-As-Threat-Actors (MATA) and secure AI design principles

- **Source:** S-0742: D. Brauchler, "Analyzing AI Application Threat Models", NCC Group research blog, 2024-02-07. ; D. Brauchler, "Analyzing Secure AI Design Principles", NCC Group research blog (date not shown). [link](https://www.nccgroup.com/us/research-blog/analyzing-ai-application-threat-models/) (type threat-model; confidence high)
- **Decomposition:** Draw the LLM as a potential threat actor; model trust = least-trusted data source it sees; code models vs data models (trustless function paradigm).
- **Assets:** anything an LLM node can call.
- **Threat categories:** Prompt injection, oracle attacks, extraction, water-table poisoning, response poisoning, resource abuse, excessive agency.
- **Method:** Seven design principles (models as threat actors, data-code separation, trust inheritance, least privilege, pass-through authorization, minimal delegation, HITL).
- **Machine-readability:** Blog; directly encodable as a trust-label propagation rule.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-028 Threat modelling LLM-powered applications with STRIDE + DREAD (Tete)

- **Source:** S-0743: S. B. Tete, "Threat Modelling and Risk Analysis for Large Language Model (LLM)-Powered Applications", arXiv:2406.11007, 2024. [link](https://arxiv.org/abs/2406.11007) (type threat-model; confidence medium)
- **Decomposition:** STRIDE identification, DREAD rating, Shostack frame on one app.
- **Assets:** prompt, DB, model.
- **Threat categories:** Poisoning, prompt injection, SQLi via LLM, jailbreak.
- **Method:** Case study.
- **Machine-readability:** None.
- **Cached PDF:** tete-llm-app-threat-modelling-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-029 Operationalizing a Threat Model for Red-Teaming LLMs (Verma et al., TMLR)

- **Source:** S-0745: A. Verma, S. Krishna, S. Gehrmann, M. Seshadri, A. Pradhan, T. Ault et al., "Operationalizing a Threat Model for Red-Teaming Large Language Models (LLMs)", arXiv:2407.14937; TMLR 05/2025. [link](https://arxiv.org/abs/2407.14937) (type threat-model; confidence high)
- **Decomposition:** Entry points across the LLM development and deployment lifecycle.
- **Assets:** training data, fine-tuning, deployment interfaces.
- **Threat categories:** Poisoning, fine-tuning attacks, jailbreaks, prompt injection, extraction, side channels.
- **Method:** Attack families keyed to the stage the attacker must reach; defenses and red-team strategies.
- **Machine-readability:** None (paper).
- **Cached PDF:** verma-red-teaming-threat-model-llm-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-030 LLM Platform Security: systematic evaluation of ChatGPT plugins (Iqbal et al.)

- **Source:** S-0741: U. Iqbal, T. Kohno, F. Roesner, "LLM Platform Security: Applying a Systematic Evaluation Framework to OpenAI's ChatGPT Plugins", arXiv:2309.10254; AAAI/ACM AIES 2024 (shortened). [link](https://arxiv.org/abs/2309.10254) (type threat-model; confidence high)
- **Decomposition:** Stakeholder pairs (platform, user, plugin) iterated to elicit attacks.
- **Assets:** users, platform, plugins.
- **Threat categories:** Plugin->user, plugin->platform, plugin->plugin, user->plugin attacks (credential exfiltration, session hijack, functionality squatting).
- **Method:** Stakeholder-pair elicitation applied to a real ecosystem.
- **Machine-readability:** None.
- **Cached PDF:** iqbal-llm-platform-security-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-031 A New Era in LLM Security (Wu et al.): information-flow constraints

- **Source:** S-0746: F. Wu, N. Zhang, S. Jha, P. McDaniel, C. Xiao, "A New Era in LLM Security: Exploring Security Concerns in Real-World LLM-based Systems", arXiv:2402.18649, 2024 [link](https://arxiv.org/abs/2402.18649) (type threat-model; confidence high)
- **Decomposition:** LLM + objects (frontend, web tools, plugins, sandbox); security = constraints on information flow within and between them.
- **Assets:** chat history, tools, rendering frontend.
- **Threat categories:** Constraint absence/robustness violations; end-to-end chat-history theft.
- **Method:** Multi-layer constraint analysis applied to GPT-4.
- **Machine-readability:** None.
- **Cached PDF:** wu-2024-new-era-llm-security.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-032 Microsoft AI Red Team ontology (Lessons from red teaming 100 GenAI products)

- **Source:** S-0753: B. Bullwinkel, A. Minnich, S. Chawla, G. Lopez, M. Pouliot, W. Maxwell et al., "Lessons From Red Teaming 100 Generative AI Products", arXiv:2501.07238, 2025. [link](https://arxiv.org/abs/2501.07238) (type threat-model; confidence high)
- **Decomposition:** System -> Actor (adversarial or benign) -> TTPs (ATT&CK/ATLAS) -> Weakness -> Impact (security or safety).
- **Assets:** end-to-end GenAI systems.
- **Threat categories:** Prompt injection, jailbreak, XPIA, SSRF, harmful content, privilege escalation.
- **Method:** Ontology + eight lessons from 100 engagements.
- **Machine-readability:** None (maps 1:1 to KG schema).
- **Cached PDF:** bullwinkel-red-teaming-100-genai-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-033 STRIDE-AI for Generative AI (Cyrille & Schwarz; name clash)

- **Source:** S-0771: T. N. R. Cyrille, F. Schwarz, "STRIDE-AI: A Threat Modeling Framework for Generative AI Security Assessment", arXiv:2605.17163, 2026. [link](https://arxiv.org/abs/2605.17163) (type threat-model; confidence medium)
- **Decomposition:** Six-phase assessment lifecycle; STRIDE adaptation; NIST AI RMF x OWASP LLM bridge.
- **Assets:** LLM chatbot.
- **Threat categories:** OWASP LLM Top 10 under STRIDE.
- **Method:** Web tool; one black-box case.
- **Machine-readability:** Tool (format unknown).
- **Cached PDF:** cyrille-stride-ai-genai-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-034 LINDDUN-based privacy threat modeling for GenAI (Liao et al., SOUPS 2026)

- **Source:** S-0773: Q. Liao, J. Bellemans, L. Sion, X. Jiang, D. Usynin, X. Zhou, D. Van Landuyt, L. Desmet, W. Joosen, "A LINDDUN-based Privacy Threat Modeling Framework for GenAI", arXiv:2603.06051, 2026; SOUPS 2026 version "AI've Got a Bad Feeling About This: A Privacy Threat Modeling Framework for GenAI" ( [link](https://www.usenix.org/conference/soups2026/presentation/liao) (type threat-model; confidence high)
- **Decomposition:** LINDDUN DFD-based elicitation extended with GenAI examples (3 of 7 threat types affected; 100 new examples).
- **Assets:** prompts, model, logs, RAG.
- **Threat categories:** Memorisation/regurgitation, inference of personal data, linking, unawareness, non-compliance.
- **Method:** Systematic review + case analysis; validated on an agent system.
- **Machine-readability:** LINDDUN knowledge-base extension (machine-friendly tree/catalog).
- **Cached PDF:** linddun-genai-privacy-tm-2026.pdf, liao-linddun-genai-soups-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-035 PriMod4AI: lifecycle-aware privacy threat modeling with LLMs

- **Source:** S-0777: G. Savaliya, R. Aufschläger, A. Subedi, M. Heigl, M. Schramm, "PriMod4AI: Lifecycle-Aware Privacy Threat Modeling for AI Systems using LLM", arXiv:2602.04927, 2026. [link](https://arxiv.org/abs/2602.04927) (type threat-model; confidence medium)
- **Decomposition:** LINDDUN KB + model-centric privacy attacks KB (MIA, inversion) in a vector DB, retrieved with DFD metadata.
- **Assets:** DFD elements per lifecycle stage.
- **Threat categories:** LINDDUN 7 + model-centric attacks.
- **Method:** RAG over taxonomies prompts an LLM to identify threats.
- **Machine-readability:** Tool/KBs.
- **Cached PDF:** savaliya-primod4ai-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-036 PILLAR: LLM-assisted LINDDUN privacy threat modeling

- **Source:** S-0959: M. Mollaeefar, A. Bissoli, S. Ranise, "PILLAR: an AI-Powered Privacy Threat Modeling Tool", arXiv:2410.08755, 2024. [link](https://arxiv.org/abs/2410.08755) (type tool; confidence high)
- **Decomposition:** LLM-generated DFDs; LINDDUN GO-style multi-agent elicitation; prioritisation.
- **Assets:** system DFD.
- **Threat categories:** LINDDUN categories.
- **Method:** AI applied to threat modeling (not threats to AI).
- **Machine-readability:** Tool.
- **Cached PDF:** mollaeefar-pillar-privacy-tm-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-037 RAG Security and Privacy: formal threat model (Arzanipour et al.)

- **Source:** S-0748: A. Arzanipour, R. Behnia, R. Ebrahimi, K. Dutta, "RAG Security and Privacy: Formalizing the Threat Model and Attack Surface", arXiv:2509.20324, 2025. [link](https://arxiv.org/abs/2509.20324) (type threat-model; confidence high)
- **Decomposition:** Adversary types by access to RAG components (black-box user -> retriever/embedding/generator access); game-based definitions.
- **Assets:** knowledge base, retriever, generator.
- **Threat categories:** Document-level MIA, document reconstruction/leakage, KB poisoning.
- **Method:** Formal games; DP-style bounds.
- **Machine-readability:** None (formal definitions).
- **Cached PDF:** rag-threat-model-formal-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-038 Securing RAG: risk assessment and mitigation framework (Ammann et al.)

- **Source:** S-0797: L. Ammann, S. Ott, C. R. Landolt, M. P. Lehmann, "Securing RAG: A Risk Assessment and Mitigation Framework", arXiv:2505.08728, 2025. [link](https://arxiv.org/abs/2505.08728) (type framework; confidence medium)
- **Decomposition:** RAG pipeline stages: pre-processing, storage, retrieval, LLM integration.
- **Assets:** RAG pipeline.
- **Threat categories:** Per-stage vulnerabilities.
- **Method:** Risk -> mitigation overview merged with guidelines.
- **Machine-readability:** None.
- **Cached PDF:** ammann-securing-rag-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-039 Towards Secure RAG: review of threats, defenses and benchmarks

- **Source:** S-0721: Y. Mu, H. Hu, F. Li, Q. Yuan et al., "Towards Secure Retrieval-Augmented Generation: A Comprehensive Review of Threats, Defenses and Benchmarks", arXiv:2603.21654, 2026. [link](https://arxiv.org/abs/2603.21654) (type survey; confidence medium)
- **Decomposition:** RAG workflow; input-side and output-side defense taxonomy.
- **Assets:** KB, retriever, generator.
- **Threat categories:** Poisoning, MIA, adversarial retrieval.
- **Method:** Survey/index.
- **Machine-readability:** None.
- **Cached PDF:** mu-secure-rag-review-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-040 Google Secure AI Framework (SAIF) risk map

- **Source:** S-0780: Google, "Secure AI Framework (SAIF): Risks" and "Controls".  [link](https://saif.google/secure-ai-framework/risks) (type framework; confidence high)
- **Decomposition:** Component areas (data, infrastructure, model, application) with where each risk is introduced, exposed and mitigated; personas (model creator vs consumer).
- **Assets:** data sources, training, model storage, serving, application, agent.
- **Threat categories:** 15 risks (DP, UTD, MST, EDH, MXF, MDT, DMS, MRE, IIC, PIJ, MEV, SDD, ISD, IMO, RA).
- **Method:** Component map + six control groups + adoption steps.
- **Machine-readability:** Not on saif.google; machine-readable through the CoSAI Risk Map YAML.
- **Cached PDF:** google-saif-approach-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-041 CoSAI Risk Map (secure-ai-tooling)

- **Source:** S-0900: Coalition for Secure AI (OASIS Open Project), "CoSAI Risk Map", repository cosai-oasis/secure-ai-tooling (last commit 2026-10-02). [link](https://github.com/cosai-oasis/secure-ai-tooling) (type catalog; confidence high)
- **Decomposition:** Components (42) x personas (10) -> risks (36) -> controls (37), verified by parsing the YAML at commit 0d8bfc9b5d76 (2026-10-03; the earlier "59 components / 43 controls" count was wrong); fields lifecycleStage, impactType, actorAccess.
- **Assets:** infrastructure, data, model, application, agent, orchestration, tools, identity, MCP transport components.
- **Threat categories:** 15 SAIF risks + 21 additions (side channels, denial of wallet, PEFT injection, tool registry tampering, cache and vector-store poisoning, delegation confused deputy, shadow agents, ...).
- **Method:** Risk/control catalog with version-pinned crosswalks (ADR-027) to ATLAS, OWASP LLM, STRIDE.
- **Machine-readability:** Yes: YAML + JSON Schema, Apache-2.0.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-042 OWASP AI Exchange

- **Source:** S-0826: R. van der Veer et al., "OWASP AI Exchange" (owaspai.org), OWASP Flagship project; PDF export generated 2026-10-01. [link](https://owaspai.org/) (type framework; confidence high)
- **Decomposition:** Threats by attack surface: through use (input), development time, runtime application security; asset periodic table.
- **Assets:** training data, model, augmentation/RAG data, input, output, agent sandbox.
- **Threat categories:** 2.x input threats, 3.x development-time, 4.x runtime (incl. agent escape).
- **Method:** Threat -> control catalog with ISO gap analysis; feeds ISO/IEC 27090 and prEN 18282.
- **Machine-readability:** Web/PDF; section ids and short links (not stable ids). CC0.
- **Cached PDF:** owasp-ai-exchange.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-043 Databricks AI Security Framework (DASF 2.0/3.0)

- **Source:** S-0779: Databricks, "Databricks AI Security Framework (DASF)" v2.0 (12 components, 62 risks, 64 controls) and DASF 3.0 (agentic extension). [link](https://www.databricks.com/resources/whitepaper/databricks-ai-security-framework-dasf) (type framework; confidence medium)
- **Decomposition:** 12 AI system components (raw data -> platform) + component 13 (agent core, MCP server).
- **Assets:** platform components.
- **Threat categories:** 62 risks (2.0) + agentic risks reusing OWASP T-code names.
- **Method:** Component -> risk -> numbered control (DASF 1-69).
- **Machine-readability:** Gated whitepaper; counts from secondary READMEs.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-044 Cisco Integrated AI Security and Safety Framework

- **Source:** S-0801: A. Chang, T. Saade, S. Mendapara, A. Swanda, A. Garg, "Cisco Integrated AI Security and Safety Framework Report", arXiv:2512.12921, 2025. [link](https://arxiv.org/abs/2512.12921) (type framework; confidence high)
- **Decomposition:** Four levels: 19 objectives (OB-001..019), 40 techniques (AITech-x.y), 112 subtechniques, procedures; MCP (14 threat types) and supply-chain taxonomies; 25 harm categories.
- **Assets:** model, agent, MCP, supply chain.
- **Threat categories:** Goal hijacking, data theft, communication compromise, supply chain, privilege escalation, multi-agent PI, MCP threats, harms.
- **Method:** ATT&CK-like hierarchy unifying security and safety.
- **Machine-readability:** No public machine-readable release found (STIX-like claimed).
- **Cached PDF:** cisco-ai-security-framework-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-045 MITRE SAFE-AI

- **Source:** S-0809: J. Kressel, R. Perrella, E. Reed, N. Naik et al. (MITRE), "SAFE-AI: A Framework for Securing AI-Enabled Systems", MITRE Work Product MP250397, April 2025 (Public Release 25-1028). [link](https://atlas.mitre.org/pdf-files/SAFEAI_Full_Report.pdf) (type framework; confidence high)
- **Decomposition:** AI-enabled system = Environment, AI Platform/Tools, AI Models, AI Data; threat x element -> SP 800-53 controls.
- **Assets:** the four elements.
- **Threat categories:** ATLAS techniques per element.
- **Method:** RMF/ATO crosswalk: 100 controls flagged AI-affected; residual risk.
- **Machine-readability:** PDF appendices.
- **Cached PDF:** mitre-safe-ai-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-046 Japan AISI Guide to Red Teaming Methodology on AI Safety

- **Source:** S-0791: Japan AI Safety Institute (J-AISI), "Guide to Red Teaming Methodology on AI Safety" (AIセーフティに関するレッドチーミング手法ガイド), v1.00, 2024-09-25; latest v1.10, 2025-03-31. [link](https://aisi.go.jp/assets/pdf/ai_safety_RT_v1.00_en.pdf) (type framework; confidence high)
- **Decomposition:** LLM system attack catalog (direct/indirect PI, prompt leaking, general AI attacks) + red-team roles and process.
- **Assets:** LLM system.
- **Threat categories:** Prompt injection categories, prompt leaking, poisoning, evasion, extraction.
- **Method:** Red-team methodology.
- **Machine-readability:** PDF.
- **Cached PDF:** japan-aisi-red-teaming-guide-v1-00.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-047 BSI: Evasion Attacks on LLMs, countermeasures in practice

- **Source:** S-0844: BSI (Federal Office for Information Security), "Evasion Attacks on LLMs – Countermeasures in Practice", v1.0, 2025-11-06. [link](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/Evasion_Attacks_on_LLMs-Countermeasures.pdf) (type standard; confidence high)
- **Decomposition:** Attack mechanism, steganography, entry points, attacked component, attacker position; countermeasure codes (SPTE, LPP, CLI, SFF, MFT, guardrails).
- **Assets:** LLM system memory, files, tools.
- **Threat categories:** Direct/indirect PI, jailbreak, memory injection, MCP abuse, code-agent weaponization.
- **Method:** Countermeasure matrix + checklist + case studies.
- **Machine-readability:** PDF with codes.
- **Cached PDF:** bsi-evasion-attacks-llm-countermeasures.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-048 BSI: Generative AI Models, Opportunities and Risks

- **Source:** S-0845: BSI, "Generative AI Models – Opportunities and Risks for Industry and Authorities", v2.0, 2025-01-17 (v1.0 2023-05-15; v1.1 2024-04-04). [link](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/Generative_AI_Models.pdf) (type standard; confidence high)
- **Decomposition:** Risks as proper use, misuse, attacks (poisoning, privacy, evasion) for LLMs and image/video generators.
- **Assets:** GenAI models.
- **Threat categories:** R-/M-style risk and countermeasure ids (69 lines; scheme unverified).
- **Method:** Risk -> countermeasure cross-reference table.
- **Machine-readability:** PDF table.
- **Cached PDF:** bsi-generative-ai-models-opportunities-risks.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-049 ANSSI: Security recommendations for a GenAI system

- **Source:** S-0836: ANSSI, « Recommandations de sécurité pour un système d'IA générative » ("Security Recommendations for a Generative AI System"), 2024-04-29. [link](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative) (type standard; confidence high)
- **Decomposition:** GenAI architecture from training to production; 35 recommendations (R1-R35).
- **Assets:** hosting, GPUs, training data, privileges, gateway.
- **Threat categories:** Supply chain, hosting, privilege, side channel, training-data integrity, automation of critical actions.
- **Method:** Recommendation set (e.g., R16 dedicated GPUs, R17 side channels, R9 no automated critical actions).
- **Machine-readability:** PDF.
- **Cached PDF:** anssi-2024-security-recommendations-genai.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-050 ANSSI-led joint high-level risk analysis on AI

- **Source:** S-0747: ANSSI and co-signing partners, "Building trust in AI through a cyber risk-based approach" (Joint High-Level Risk Analysis on AI), February 2025 (page dated 2025-02-07). [link](https://messervices.cyber.gouv.fr/guides/en-building-trust-ai-through-cyber-risk-based-approach) (type threat-model; confidence high)
- **Decomposition:** Risk scenarios at organization level.
- **Assets:** AI hosting and management infrastructure, interconnected IS, industrial systems.
- **Threat categories:** Infrastructure compromise, supply chain, lateralization via interconnection/IPI, human error, malfunction.
- **Method:** Multinational scenario analysis.
- **Machine-readability:** PDF.
- **Cached PDF:** anssi-2025-building-trust-ai-risk-based.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-051 CSA Singapore Guidelines on Securing AI Systems

- **Source:** S-0837: Cyber Security Agency of Singapore, "Guidelines on Securing AI Systems", 2024-10-15. [link](https://www.csa.gov.sg/resources/publications/guidelines-and-companion-guide-on-securing-ai-systems) (type standard; confidence high)
- **Decomposition:** Five lifecycle stages (plan/design, development, deployment, O&M, end of life).
- **Assets:** AI system.
- **Threat categories:** Classical and AI-specific risks (refers to NIST AI 100-2, ATLAS).
- **Method:** Secure-by-design guidance.
- **Machine-readability:** PDF.
- **Cached PDF:** csa-sg-2024-guidelines-securing-ai.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-052 CSA Singapore Companion Guide on Securing AI Systems

- **Source:** S-0789: Cyber Security Agency of Singapore (with industry and academic contributors), "Companion Guide on Securing AI Systems", 2024-10-15. [link](https://www.csa.gov.sg/resources/publications/guidelines-and-companion-guide-on-securing-ai-systems) (type framework; confidence high)
- **Decomposition:** Treatment controls per lifecycle stage mapped to ATLAS technique ids; two worked examples.
- **Assets:** AI system.
- **Threat categories:** ATLAS techniques (2024 ids, some now deprecated).
- **Method:** Post-risk-assessment control catalog with worked examples.
- **Machine-readability:** PDF tables (control -> ATLAS).
- **Cached PDF:** csa-sg-2024-companion-guide-securing-ai.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-053 NCSC/CISA Guidelines for Secure AI System Development

- **Source:** S-0835: UK NCSC, US CISA and international partners, "Guidelines for secure AI system development", 2023-11-27. [link](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development) (type standard; confidence high)
- **Decomposition:** Four lifecycle stages; secure design requires modelling threats.
- **Assets:** AI system assets (identified and tracked).
- **Threat categories:** Generic AML + conventional threats.
- **Method:** High-level guidance (no catalog).
- **Machine-readability:** PDF.
- **Cached PDF:** ncsc-cisa-secure-ai-guidelines-2023.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-054 ETSI EN 304 223 Baseline Cyber Security Requirements for AI (from UK Code of Practice)

- **Source:** S-0849: ETSI TC SAI, "Securing Artificial Intelligence (SAI); Baseline Cyber Security Requirements for AI Models and Systems", ETSI EN 304 223 V2.1.1 (2025-12); publication announced 2026-01-14. Predecessor TS 104 223 V1.1.1 (2025-04). [link](https://www.etsi.org/deliver/etsi_en/304200_304299/304223/02.01.01_60/en_304223v020101p.pdf) (type standard; confidence high)
- **Decomposition:** 13 principles across 5 lifecycle phases with stakeholder roles; P3 requires threat evaluation.
- **Assets:** AI models and systems.
- **Threat categories:** Referenced via OWASP AI Exchange and ATLAS mitigations.
- **Method:** Requirements (shall/should provisions).
- **Machine-readability:** PDF; provision numbers.
- **Cached PDF:** etsi-en-304223-v2-1-1.pdf, etsi-ts-104223-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-055 NIST AI 600-1 Generative AI Profile

- **Source:** S-0792: NIST, "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile", NIST AI 600-1, 2024-07-26. DOI 10.6028/NIST.AI.600-1 [link](https://doi.org/10.6028/NIST.AI.600-1) (type framework; confidence high)
- **Decomposition:** 12 GAI risks x AI RMF functions with 212 suggested actions.
- **Assets:** organization deploying GAI.
- **Threat categories:** Risk 9 Information Security, 12 Value Chain (attacks); others are harms.
- **Method:** Governance actions (GV/MP/MS/MG ids).
- **Machine-readability:** PDF ids.
- **Cached PDF:** nist-ai-600-1-genai-profile.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-056 Canadian Centre for Cyber Security ITSAP.00.041 Generative AI

- **Source:** S-0846: Canadian Centre for Cyber Security, "Generative artificial intelligence (AI)", ITSAP.00.041, updated December 2025. [link](https://www.cyber.gc.ca/en/guidance/generative-artificial-intelligence-ai-itsap00041) (type standard; confidence high)
- **Decomposition:** Eight organizational GenAI risks.
- **Assets:** corporate data, employees.
- **Threat categories:** Misinformation, phishing, data leakage via queries, malicious/buggy code, poisoned data, bias, IP loss.
- **Method:** Awareness guidance.
- **Machine-readability:** Web page.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-057 PLOT4ai: Library of AI threats (cards)

- **Source:** S-0881: I. Barberá, "PLOT4ai - Practical Library of Threats for AI", 2022; major update 2025. [link](https://plot4.ai/) (type catalog; confidence high)
- **Decomposition:** 138 question cards across 8 categories over the AI lifecycle.
- **Assets:** AI lifecycle assets (implicit).
- **Threat categories:** Data governance, privacy, bias, safety, cybersecurity, ethics, transparency, accountability.
- **Method:** Workshop elicitation (LINDDUN GO-inspired).
- **Machine-readability:** Online tool; GitHub content mentioned, export unconfirmed. CC BY-SA.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-126 AWS Generative AI Security Scoping Matrix (v0.2)

- **Source:** S-1178: AWS, "Securing Generative AI: The Generative AI Security Scoping Matrix" (undated web page). [link](https://aws.amazon.com/ai/generative-ai/security/scoping-matrix/) (type framework; confidence high)
- **Decomposition:** Five scopes by what the organization owns: (1) consumer app, (2) enterprise app with embedded GenAI, (3) applications on pre-trained third-party models via API, (4) fine-tuned models, (5) self-trained models; five disciplines across scopes: governance and compliance, legal and privacy, risk management, controls, resilience.
- **Assets:** implicit per scope (data, models, applications).
- **Threat categories:** none enumerated; it scopes responsibility.
- **Method:** Place each workload in a scope, then apply the disciplines appropriate to that scope.
- **Machine-readability:** None (web page).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73); **priority for #74** as the company-profile axis for ADR-0002 (question 6 in report section 8): the scope fixes which reference components (report section 1) the company owns and therefore which AIT techniques are treated versus accepted or transferred.

### TM-127 NSA AISC et al.: Deploying AI Systems Securely (v0.2)

- **Source:** S-1180: NSA AISC, CISA, FBI, ASD ACSC, CCCS, NCSC-NZ, NCSC-UK, "Deploying AI Systems Securely", 2024-04-15. [link](https://media.defense.gov/2024/Apr/15/2003439257/-1/-1/0/CSI-DEPLOYING-AI-SYSTEMS-SECURELY.PDF) (type framework; confidence medium)
- **Decomposition:** deployment lifecycle of externally developed AI systems (deployment environment, continuous protection, operation and maintenance); exact section structure not read.
- **Assets:** AI systems, their data and services.
- **Threat categories:** not enumerated in what was read.
- **Method:** best-practice checklist for deployers.
- **Machine-readability:** None (PDF).
- **Cached PDF:** — (automated download refused)
- **Capture status:** captured from the CISA landing page only; needs detailed analysis (#73)

## C. Agentic, multi-agent and protocol threat models

### TM-058 CSA MAESTRO

- **Source:** S-0754: K. Huang (CSA), "Agentic AI Threat Modeling Framework: MAESTRO", Cloud Security Alliance blog, 2025-02-06. [link](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) (type threat-model; confidence high)
- **Decomposition:** Seven layers: L1 foundation models, L2 data operations, L3 agent frameworks, L4 deployment and infrastructure, L5 evaluation and observability, L6 security and compliance (vertical), L7 agent ecosystem; plus cross-layer.
- **Assets:** per-layer (implicit).
- **Threat categories:** 6-13 threats per layer; cross-layer supply chain, lateral movement, privilege escalation, data leakage, goal-misalignment cascades.
- **Method:** Six steps: decompose, layer threats, cross-layer threats, risk (L x I), mitigation, monitoring.
- **Machine-readability:** Blog only; no machine-readable form.
- **Cached PDF:** habler-a2a-maestro-2025.pdf, zambare-maestro-network-agent-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-059 OWASP Agentic AI Threats and Mitigations v1.1 (T1-T17)

- **Source:** S-0760: OWASP GenAI Security Project, Agentic Security Initiative, "Agentic AI - Threats and Mitigations", Version 1.1, December 2025 (v1.0 Feb 2025). [link](https://genai.owasp.org/) (type threat-model; confidence high)
- **Decomposition:** Reference agent architecture (memory, planner, tool executor, inter-agent channel, HITL) + decision-tree threat navigator.
- **Assets:** agent components.
- **Threat categories:** T1 memory poisoning ... T15 human manipulation; v1.1 adds T16 protocol abuse, T17 supply chain.
- **Method:** Navigator questions over agent capabilities; mitigation playbooks.
- **Machine-readability:** PDF; stable T-ids.
- **Cached PDF:** owasp-agentic-threats-mitigations-v1-1.pdf, owasp-asi-agentic-threats-mitigations-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-060 OWASP Multi-Agentic System Threat Modelling Guide v1.0

- **Source:** S-0761: OWASP GenAI Security Project, "Agentic AI - Multi-Agentic System Threat Modelling Guide" v1.0, April 2025. [link](https://genai.owasp.org/) (type threat-model; confidence medium)
- **Decomposition:** MAESTRO layers x ASI T-codes + cross-layer row; worked examples (RPA expense agent, ElizaOS, MCP).
- **Assets:** multi-agent components per layer.
- **Threat categories:** T1-T15 per layer.
- **Method:** Worked threat models with mitigations; MAESTRO + ATLAS usage.
- **Machine-readability:** PDF tables.
- **Cached PDF:** owasp-multi-agentic-threat-modeling-guide-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-061 OWASP Securing Agentic Applications Guide 1.0

- **Source:** S-0816: OWASP GenAI Security Project, "Securing Agentic Applications Guide 1.0", 2025-07-27. [link](https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/) (type framework; confidence medium)
- **Decomposition:** Design/deployment guidance complementing ASI T&M (component model not confirmed).
- **Assets:** agent architecture components.
- **Threat categories:** ASI T&M threats.
- **Method:** Guide.
- **Machine-readability:** PDF not fetched.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-062 Extending the OWASP MAS Threat Modeling Guide (Krawiecka & Schroeder de Witt)

- **Source:** S-0758: K. Krawiecka, C. Schroeder de Witt, "Extending the OWASP Multi-Agentic System Threat Modeling Guide: Insights from Multi-Agent Security Research", arXiv:2508.09815, 2025. [link](https://arxiv.org/abs/2508.09815) (type threat-model; confidence high)
- **Decomposition:** Gap analysis of OWASP MAS against multi-agent security research.
- **Assets:** planner/executor graphs, agent networks.
- **Threat categories:** Reasoning collapse, metric overfitting, unsafe delegation escalation, covert coordination, cross-agent hallucination propagation, multi-agent backdoors.
- **Method:** Added threat classes + evaluation strategies.
- **Machine-readability:** None.
- **Cached PDF:** krawiecka-owasp-mas-extension-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-063 Microsoft Taxonomy of Failure Modes in Agentic AI Systems v2.0

- **Source:** S-0902: Microsoft AI Red Team, "Taxonomy of Failure Modes in Agentic AI Systems", v2.0, April 2026 (v1.0 April 2025). (whitepaper) [link](https://www.microsoft.com/en-us/security/blog/) (type catalog; confidence high)
- **Decomposition:** 2x2: novel vs existing x safety vs security; five mitigation families.
- **Assets:** agent system.
- **Threat categories:** Agent compromise/injection/impersonation, flow manipulation, provisioning poisoning, multi-agent jailbreaks, supply chain, goal hijacking, trust escalation, CUA visual attacks, memory poisoning, XPIA.
- **Method:** Checklist elicitation: for each category ask whether and when it can occur.
- **Machine-readability:** PDF only.
- **Cached PDF:** microsoft-agentic-failure-modes-v2-2026.pdf, microsoft-agentic-failure-modes-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-064 ATFAA and SHIELD (Narajala & Narayan)

- **Source:** S-0759: V. S. Narajala, O. Narayan, "Securing Agentic AI: A Comprehensive Threat Model and Mitigation Framework for Generative AI Agents", arXiv:2504.19956, 2025. [link](https://arxiv.org/abs/2504.19956) (type threat-model; confidence high)
- **Decomposition:** Five domains: cognitive architecture, temporal persistence, operational execution, trust boundary, governance circumvention; 9 threats mapped to STRIDE.
- **Assets:** agent reasoning, memory, tools, identity, oversight.
- **Threat categories:** T1 reasoning hijack ... T9 governance evasion.
- **Method:** SHIELD mitigations (segmentation, heuristic monitoring, integrity, escalation control, logging immutability, decentralized oversight).
- **Machine-readability:** None.
- **Cached PDF:** narajala-atfaa-shield-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-065 ASTRIDE: STRIDE + A for agentic AI (platform)

- **Source:** S-0749: E. Bandara, A. Hass, R. Gore, S. Shetty et al., "ASTRIDE: A Security Threat Modeling Platform for Agentic-AI Applications", arXiv:2512.04785, 2025. [link](https://arxiv.org/abs/2512.04785) (type threat-model; confidence medium)
- **Decomposition:** STRIDE plus seventh category A (agent-specific: prompt injection, unsafe tool invocation, reasoning subversion).
- **Assets:** DFD elements extracted from diagrams.
- **Threat categories:** STRIDE+A.
- **Method:** VLM extraction of diagrams, LLM threat generation, agent orchestration.
- **Machine-readability:** Platform (format unclear).
- **Cached PDF:** astride-agentic-tm-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-066 ATAG: AI-agent application threat assessment with attack graphs

- **Source:** S-0750: P. A. Gandhi, A. Shukla, D. Tayouri, B. Ifland et al., "ATAG: AI-Agent Application Threat Assessment with Attack Graphs", arXiv:2506.02859, 2025. [link](https://arxiv.org/abs/2506.02859) (type threat-model; confidence high)
- **Decomposition:** MulVAL facts and interaction rules for agent topologies, LLM vulnerabilities and multi-step scenarios; LLM Vulnerability Database (LVD).
- **Assets:** agents and their privileges.
- **Threat categories:** Prompt injection -> excessive agency -> disclosure chains.
- **Method:** Logic-based attack-graph generation.
- **Machine-readability:** Described, not confirmed: the paper describes Datalog/MulVAL rules and an LLM Vulnerability Database, but no public rules artifact was retrieved (v0.2).
- **Cached PDF:** atag-attack-graphs-agents-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-067 MATRA: modeling the attack surface of agentic AI (OpenClaw case)

- **Source:** S-0774: T. Van hamme, T. Vissers, J. Carnerero-Cano, M. Fritz et al., "MATRA: Modeling the Attack Surface of Agentic AI Systems -- OpenClaw Case Study", arXiv:2605.10763, 2026. [link](https://arxiv.org/abs/2605.10763) (type threat-model; confidence high)
- **Decomposition:** Asset-based impact assessment then attack trees for likelihood within the architecture.
- **Assets:** personal agent assets (files, accounts, network).
- **Threat categories:** Injection-driven tool abuse and exfiltration.
- **Method:** Deployment-specific quantification of sandboxing and least privilege (blast radius).
- **Machine-readability:** None.
- **Cached PDF:** matra-agentic-attack-surface-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-068 Owner-Harm: the agent as a threat to its deployer

- **Source:** S-0775: D. Zhang, Y. Jiang, "Owner-Harm: A Missing Threat Model for AI Agent Safety", arXiv:2604.18658, 2026. [link](https://arxiv.org/abs/2604.18658) (type threat-model; confidence medium)
- **Decomposition:** Eight categories of agent behaviour harming its own deployer.
- **Assets:** deployer credentials, internal data, brand channels.
- **Threat categories:** Credential exfiltration, data leakage, unauthorized posts (mostly injection-mediated).
- **Method:** Benchmark of 300 owner-harm scenarios; gate + post-audit verifier.
- **Machine-readability:** Benchmark.
- **Cached PDF:** zhang-owner-harm-agent-tm-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-069 Agent Security is a Systems Problem (Christodorescu et al.)

- **Source:** S-0769: M. Christodorescu, E. Fernandes, A. Hooda, S. Jha, J. Rehberger, K. Chaudhuri et al., "Agent Security is a Systems Problem", arXiv:2605.18991, 2026. [link](https://arxiv.org/abs/2605.18991) (type threat-model; confidence high)
- **Decomposition:** Generic agent security architecture; model as untrusted component; principles (instruction/data separation, least-privilege sandboxing with verifiable policies, IFC).
- **Assets:** agent runtime and tools.
- **Threat categories:** 11 real attacks mapped to violated principles.
- **Method:** Principle-violation analysis.
- **Machine-readability:** None (rule base).
- **Cached PDF:** christodorescu-agent-security-systems-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-070 The lethal trifecta (Willison)

- **Source:** S-0820: Simon Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication", simonwillison.net, 2025-06-16. [link](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (type framework; confidence high)
- **Decomposition:** Capability composition: private data + untrusted content + external communication.
- **Assets:** any agent.
- **Threat categories:** Injected exfiltration.
- **Method:** Design rule: avoid the combination.
- **Machine-readability:** Rule (three booleans).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-071 Agents Rule of Two (Meta)

- **Source:** S-0808: Meta AI, "Agents Rule of Two: A Practical Approach to AI Agent Security", Meta AI blog, 2025-10-31. [link](https://ai.meta.com/blog/practical-ai-agent-security/) (type framework; confidence high)
- **Decomposition:** At most two of [A] untrusted input, [B] sensitive access, [C] state change or external communication per session.
- **Assets:** agent sessions.
- **Threat categories:** Prompt-injection-driven harmful actions.
- **Method:** Design rule; HITL when all three required.
- **Machine-readability:** Rule (three booleans).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-072 Design patterns for securing LLM agents against prompt injection

- **Source:** S-0799: Luca Beurer-Kellner, Beat Buesser, Ana-Maria Creţu, Edoardo Debenedetti, Daniel Dobos, et al. (14 authors; IBM, Invariant Labs, ETH Zurich, Google, Microsoft and others), "Design Patterns for Securing LLM Agents against Prompt Injections", arXiv 2025. arXiv:2506.08837 [link](https://arxiv.org/abs/2506.08837) (type framework; confidence medium (capped))
- **Decomposition:** Six patterns constraining how untrusted input can influence actions (action-selector, plan-then-execute, map-reduce, dual LLM, code-then-execute, context-minimization).
- **Assets:** agent data-to-action graph.
- **Threat categories:** Prompt injection.
- **Method:** Pattern catalog with utility/security trade-offs.
- **Machine-readability:** None (control nodes).
- **Cached PDF:** design-patterns-prompt-injection-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-073 Google's approach for secure AI agents

- **Source:** S-0806: S. Díaz, C. Kern, K. Olive, "Google's Approach for Secure AI Agents: An Introduction", Google, May 2025. [link](https://research.google/pubs/an-introduction-to-googles-approach-for-secure-ai-agents/) (type framework; confidence high)
- **Decomposition:** Two risks (rogue actions, sensitive data disclosure); three principles (human controllers, limited powers, observable actions).
- **Assets:** agents with tools and user data.
- **Threat categories:** Prompt injection, misalignment.
- **Method:** Hybrid defense in depth: deterministic runtime policy + reasoning-based defenses.
- **Machine-readability:** Paper.
- **Cached PDF:** google-secure-ai-agents-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-074 OpenAI: Practices for governing agentic AI systems

- **Source:** S-0785: Y. Shavit, C. O'Keefe, T. Eloundou, P. McMillan, S. Agarwal, M. Brundage et al. (16 authors), "Practices for Governing Agentic AI Systems", OpenAI white paper, 2023 (December 2023, from recall). [link](https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf) (type framework; confidence high)
- **Decomposition:** Agent lifecycle parties (developer, deployer, user); seven baseline practices.
- **Assets:** agent deployments.
- **Threat categories:** Agent failure and misuse.
- **Method:** Control practices (approval, legibility, monitoring, attributability, interruptibility).
- **Machine-readability:** PDF.
- **Cached PDF:** openai-2023-governing-agentic-ai.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-075 AI Agents Under Threat (Deng et al., ACM CSUR)

- **Source:** S-0701: Zehang Deng, Yongjian Guo, Changzhou Han, Wanlun Ma, Junwu Xiong, Sheng Wen, Yang Xiang, "AI Agents Under Threat: A Survey of Key Security Challenges and Future Pathways", ACM Computing Surveys 57(7), Article 182, July 2025. arXiv:2406.02630 [link](https://arxiv.org/abs/2406.02630) (type survey; confidence high)
- **Decomposition:** Four knowledge gaps: multi-step user inputs, internal execution, operational environments, untrusted external entities.
- **Assets:** agent.
- **Threat categories:** Attacks and defenses per gap.
- **Method:** Survey taxonomy.
- **Machine-readability:** None.
- **Cached PDF:** deng-2025-ai-agents-under-threat-survey.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-076 Cross-dimensional threat taxonomy for agentic AI (Baek et al.)

- **Source:** S-0711: H. Baek, A. Abuadbba, K. Moore, H. Kim, S. Nepal, "Connecting the Dots in Agentic AI Security: A Cross-Dimensional Threat Taxonomy, Evaluation Maturity, and Open Challenges", arXiv:2609.23894, 2026-09-20. [link](https://arxiv.org/abs/2609.23894) (type survey; confidence high)
- **Decomposition:** Threat T = {S surface, B boundary crossed, P property violated, A architecture} over 66 studies.
- **Assets:** agent surfaces.
- **Threat categories:** Prompt/reasoning, memory, tool, human-agent, multi-agent, systemic, long-horizon.
- **Method:** Structured review with evaluation-maturity analysis.
- **Machine-readability:** Tuple schema (directly encodable).
- **Cached PDF:** baek-agentic-cross-dimensional-taxonomy-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-077 SoK: the attack surface of agentic AI (Dehghantanha & Homayoun)

- **Source:** S-0714: Ali Dehghantanha, Sajad Homayoun, "SoK: The Attack Surface of Agentic AI - Tools and Autonomy", arXiv 2026. arXiv:2603.22928 [link](https://arxiv.org/abs/2603.22928) (type survey; confidence high)
- **Decomposition:** Trust boundaries across prompt, RAG, tool and multi-agent layers; attacker models; metrics (Unsafe Action Rate, Privilege Escalation Distance).
- **Assets:** agentic system.
- **Threat categories:** Injection, KB poisoning, tool/plugin exploits, multi-agent emergent threats.
- **Method:** SoK + phased defensive checklist.
- **Machine-readability:** None.
- **Cached PDF:** sok-agentic-attack-surface-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-078 Systematization of computer-use agent vulnerabilities (Microsoft)

- **Source:** S-0703: Daniel Jones, Giorgio Severi, Martin Pouliot, Gary Lopez, Joris de Gruyter, Santiago Zanella-Beguelin, Justin Song, Blake Bullwinkel, Pamela Cortez, Amanda Minnich (Microsoft AI Red Team), "A Systematization of Security Vulnerabilities in Computer Use Agents", arXiv 2025. arXiv:2507.05445 [link](https://arxiv.org/abs/2507.05445) (type survey; confidence high)
- **Decomposition:** Seven CUA risk classes; root causes (no input provenance, weak interface-action binding, weak memory/delegation control).
- **Assets:** CUA on enterprise desktop.
- **Threat categories:** Overlay clickjacking, IPI to RCE, CoT exposure.
- **Method:** Evaluation framework + design principles.
- **Machine-readability:** None.
- **Cached PDF:** jones-cua-vulnerabilities-sok-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-079 Threat model for prompt injection in multi-agent systems (Paul & Nandy)

- **Source:** S-0776: Rudrendu Kumar Paul, Sourav Nandy, "Beyond Single-Model Injection: A Threat Model and Defense Architecture for Prompt Injection in Multi-Agent Systems", ICML 2026 AIWILD Workshop. arXiv:2609.22949 [link](https://arxiv.org/abs/2609.22949) (type threat-model; confidence high)
- **Decomposition:** 14 vectors in 4 categories (direct, tool outputs, inter-agent messages, orchestrator cascade).
- **Assets:** 6-agent system.
- **Threat categories:** Scope violation, privilege escalation, cascade.
- **Method:** Vector x architectural-control matrix with measured reductions.
- **Machine-readability:** None (matrix).
- **Cached PDF:** paul-mas-prompt-injection-tm-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-080 Secure agentic AI with A2A, MAESTRO applied (Habler et al.)

- **Source:** S-0755: I. Habler, K. Huang, V. S. Narajala, P. Kulkarni, "Building A Secure Agentic AI Application Leveraging A2A Protocol", arXiv:2504.16902, 2025. [link](https://arxiv.org/abs/2504.16902) (type threat-model; confidence high)
- **Decomposition:** MAESTRO layers on Google A2A: agent cards, task execution integrity, authentication; A2A + MCP composition.
- **Assets:** agent cards, tasks, credentials.
- **Threat categories:** Card spoofing/tampering, task replay/injection, auth weaknesses, message poisoning.
- **Method:** Protocol threat model + secure-development practices.
- **Machine-readability:** None.
- **Cached PDF:** habler-a2a-maestro-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-081 Threat modeling for agent protocols: MCP, A2A, Agora, ANP

- **Source:** S-0767: Z. Anbiaee, M. Rabbani, M. Mirani, G. Piya, I. Opushnyev, A. Ghorbani, "Security Threat Modeling for Emerging AI-Agent Protocols: A Comparative Analysis of MCP, A2A, Agora, and ANP", arXiv:2602.11327, 2026. [link](https://arxiv.org/abs/2602.11327) (type threat-model; confidence medium)
- **Decomposition:** Protocol architecture, trust assumptions, interaction patterns, lifecycle (creation, operation, update).
- **Assets:** protocol endpoints, registries.
- **Threat categories:** 12 protocol-level risks (transitive dependency evolution, identity, discovery poisoning, message integrity).
- **Method:** Qualitative likelihood x impact comparison.
- **Machine-readability:** None.
- **Cached PDF:** anbiaee-agent-protocols-tm-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-082 MCP landscape, threats and directions (Hou et al.)

- **Source:** S-0757: Xinyi Hou, Yanjie Zhao, Shenao Wang, Haoyu Wang, "Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions", arXiv 2025. arXiv:2503.23278 [link](https://arxiv.org/abs/2503.23278) (type threat-model; confidence medium (capped))
- **Decomposition:** MCP server lifecycle: 4 phases, 16 activities; 4 attacker types.
- **Assets:** MCP servers and hosts.
- **Threat categories:** 16 threat scenarios (name collision, installer spoofing, tool poisoning, sandbox escape, ...).
- **Method:** Lifecycle x attacker matrix with safeguards.
- **Machine-readability:** None.
- **Cached PDF:** hou-mcp-landscape-threats-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-083 MCP threat modeling with STRIDE and DREAD (Huang et al.)

- **Source:** S-0772: Charoes Huang, Xin Huang, Ngoc Phu Tran, Amin Milani Fard, "Model Context Protocol Threat Modeling and Analyzing Vulnerabilities to Prompt Injection with Tool Poisoning", arXiv 2026. arXiv:2603.22489 [link](https://arxiv.org/abs/2603.22489) (type threat-model; confidence high)
- **Decomposition:** Five MCP components: host/client, LLM, MCP server, external data stores, authorization server.
- **Assets:** MCP components.
- **Threat categories:** STRIDE per component; tool poisoning most prevalent.
- **Method:** STRIDE identification + DREAD rating; 7 clients compared.
- **Machine-readability:** None.
- **Cached PDF:** huang-mcp-stride-dread-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-084 MCP-38 threat taxonomy (+ MCPThreatHive)

- **Source:** S-0909: Yi Ting Shen, Kentaroh Toyoda, Alex Leung, "MCP-38: A Comprehensive Threat Taxonomy for Model Context Protocol Systems (v1.0)", arXiv 2026. arXiv:2603.18063 [link](https://arxiv.org/abs/2603.18063) (type catalog; confidence high)
- **Decomposition:** Protocol decomposition -> 38 categories (MCP-01..38) cross-mapped to STRIDE, OWASP LLM 2025 and ASI 2026.
- **Assets:** MCP deployment.
- **Threat categories:** Tool-description poisoning, parasitic tool chaining, dynamic trust violations and 35 more.
- **Method:** Four-phase derivation incl. incident synthesis; MCPThreatHive operationalizes it into a KG with risk scores.
- **Machine-readability:** Category ids; MCPThreatHive open source (claimed).
- **Cached PDF:** mcp-38-threat-taxonomy-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-085 CoSAI MCP Security (WS4)

- **Source:** S-0770: Coalition for Secure AI, Workstream 4 (Secure Design Patterns for Agentic Systems), "Model Context Protocol (MCP) Security", 2026-01-08 (doc version hash 7ec1306f...). Repo: [link](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems) (type threat-model; confidence high)
- **Decomposition:** 12 core categories MCP-T1..T12 (authN/identity, access control, input validation, instruction boundary, data protection, integrity, session/transport, network binding, trust-boundary design, rate limiting, supply chain, logging).
- **Assets:** MCP client, server, transport, registry.
- **Threat categories:** ~40 threats mapped to control families.
- **Method:** Category -> threat -> control table.
- **Machine-readability:** PDF.
- **Cached PDF:** cosai-mcp-security-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-086 Securing MCP: risks, controls, governance (Errico et al.)

- **Source:** S-0804: Herman Errico, Jiquan Ngiam, Shanita Sojan, "Securing the Model Context Protocol (MCP): Risks, Controls, and Governance", arXiv 2025. arXiv:2511.20920 [link](https://arxiv.org/abs/2511.20920) (type framework; confidence high)
- **Decomposition:** Three adversary types: content injectors, supply-chain distributors, over-stepping agents.
- **Assets:** enterprise MCP deployment.
- **Threat categories:** Injection, compromised servers, overreach.
- **Method:** Control catalog mapped to NIST AI RMF / ISO 42001 gaps.
- **Machine-readability:** None.
- **Cached PDF:** errico-securing-mcp-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-087 Enterprise-grade security for MCP (Narajala & Habler)

- **Source:** S-0810: V. S. Narajala, I. Habler, "Enterprise-Grade Security for the Model Context Protocol (MCP): Frameworks and Mitigation Strategies", ICAIC 2026. DOI 10.1109/ICAIC67076.2026.11395723; arXiv:2504.08623 [link](https://arxiv.org/abs/2504.08623) (type framework; confidence medium)
- **Decomposition:** MCP architecture threat model -> enterprise implementation patterns.
- **Assets:** enterprise MCP.
- **Threat categories:** Tool poisoning, server compromise.
- **Method:** Control catalog (vetting, sandboxing, OAuth scopes, monitoring, zero-trust gateways).
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-088 MCP specification: Security Best Practices

- **Source:** S-0829: Model Context Protocol, "Security Best Practices" (specification, draft basic). [link](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices) (type standard; confidence high)
- **Decomposition:** Protocol threat model with explicit preconditions and MUST/SHOULD mitigations.
- **Assets:** MCP client, proxy, authorization server, local servers.
- **Threat categories:** Confused deputy, token passthrough, SSRF via OAuth metadata, session hijack, local server compromise, authorization URL injection.
- **Method:** Normative protocol guidance.
- **Machine-readability:** Web spec.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-089 OWASP MCP Top 10 (beta)

- **Source:** S-0898: OWASP Foundation (project leader V. Verma Sehgal), "OWASP MCP Top 10", 2025, beta release. [link](https://owasp.org/www-project-mcp-top-10/) (type catalog; confidence high)
- **Decomposition:** MCP01..MCP10.
- **Assets:** MCP deployments.
- **Threat categories:** Token exposure, scope creep, tool poisoning, supply chain, command injection, contextual PI, authN/Z, audit, shadow servers, context over-sharing.
- **Method:** Risk list.
- **Machine-readability:** Web.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-090 MAESTRO applied to a network-monitoring agent (Zambare et al.)

- **Source:** S-0766: P. Zambare, V. N. Thanikella, Y. Liu, "Securing Agentic AI: Threat Modeling and Risk Analysis for Network Monitoring Agentic AI System", arXiv:2508.10043, 2025. [link](https://arxiv.org/abs/2508.10043) (type threat-model; confidence high)
- **Decomposition:** MAESTRO seven layers on a LangChain monitoring agent.
- **Assets:** telemetry channel, memory log file.
- **Threat categories:** Traffic-replay DoS, memory poisoning via log tampering.
- **Method:** Empirical case study.
- **Machine-readability:** None.
- **Cached PDF:** zambare-maestro-network-agent-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-091 AgentHeLLM: A2A threats in safety-critical LLM assistants (automotive)

- **Source:** S-0778: L. Stappen, A. E. Turan, J. Hagerer, G. Groh, "Agent2Agent Threats in Safety-Critical LLM Assistants: A Human-Centric Taxonomy", arXiv:2602.05877, 2026. [link](https://arxiv.org/abs/2602.05877) (type threat-model; confidence high)
- **Decomposition:** Separation of assets and attack paths; human-centric asset taxonomy from victim modelling; formal graph model.
- **Assets:** driver and vehicle assets.
- **Threat categories:** NL payload propagation via A2A, driver distraction, unauthorized control.
- **Method:** TARA-like safety-engineering method for LLM agents.
- **Machine-readability:** Formal graph model (no file).
- **Cached PDF:** stappen-agenthellm-a2a-automotive-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-092 Open challenges in multi-agent security

- **Source:** S-0706: C. Schroeder de Witt, K. Krawiecka, I. Krawczuk, B. Hagag, W. L. Anderson, P. Belcak et al., "Open Challenges in Multi-Agent Security: Towards Secure Systems of Interacting AI Agents", arXiv:2505.02077, 2025. [link](https://arxiv.org/abs/2505.02077) (type survey; confidence high)
- **Decomposition:** Agent-agent interaction through free-form protocols.
- **Assets:** agent networks.
- **Threat categories:** Steganographic collusion, swarm attacks, network propagation of jailbreaks/poisoning/privacy breaches.
- **Method:** Research agenda.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-093 Multi-Agent Risks from Advanced AI (Cooperative AI Foundation)

- **Source:** S-0756: L. Hammond et al., "Multi-Agent Risks from Advanced AI", arXiv 2025 (Cooperative AI Foundation technical report). arXiv:2502.14143 [link](https://arxiv.org/abs/2502.14143) (type threat-model; confidence high)
- **Decomposition:** Three failure modes (miscoordination, conflict, collusion) x seven risk factors.
- **Assets:** agent ecosystems.
- **Threat categories:** Systemic multi-agent harms.
- **Method:** Risk taxonomy + mitigations.
- **Machine-readability:** None.
- **Cached PDF:** hammond-2025-multi-agent-risks.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-094 AAGATE: NIST AI RMF-aligned agentic governance platform

- **Source:** S-0795: K. Huang, K. R. Lambros, J. Huang, Y. Mehmood, H. Atta, J. Beck et al., "AAGATE: A NIST AI RMF-Aligned Governance Platform for Agentic AI", arXiv:2510.25863, 2025. [link](https://arxiv.org/abs/2510.25863) (type framework; confidence medium)
- **Decomposition:** MAESTRO for Map, AIVSS+SSVC for Measure, CSA red-teaming guide for Manage.
- **Assets:** agent fleet.
- **Threat categories:** MAESTRO threats.
- **Method:** Operational control plane.
- **Machine-readability:** Platform.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-095 The Promptware Kill Chain (Brodt, Feldman, Schneier, Nassi)

- **Source:** S-0821: Oleg Brodt, Elad Feldman, Bruce Schneier, Ben Nassi, "The Promptware Kill Chain: How Prompt Injections Gradually Evolved Into a Multistep Malware Delivery Mechanism", arXiv 2026. arXiv:2601.09625 [link](https://arxiv.org/abs/2601.09625) (type framework; confidence high)
- **Decomposition:** Seven stages: initial access (PI), privilege escalation (jailbreak), reconnaissance, persistence (memory/retrieval), C2, lateral movement, actions on objective.
- **Assets:** LLM-powered app ecosystems.
- **Threat categories:** Multi-stage promptware campaigns.
- **Method:** Stage analysis of 36 studies/incidents (21 span >= 4 stages).
- **Machine-readability:** None (stage axis).
- **Cached PDF:** promptware-kill-chain-2026.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-096 Authenticated delegation and authorized AI agents (South et al.)

- **Source:** S-0818: T. South, S. Marro, T. Hardjono, R. Mahari, C. D. Whitney et al., "Authenticated Delegation and Authorized AI Agents", arXiv:2501.09674, 2025 [link](https://arxiv.org/abs/2501.09674) (type framework; confidence high)
- **Decomposition:** Delegation from humans to agents via OAuth 2.0 / OIDC extensions with scope and accountability chains.
- **Assets:** user accounts and services accessed by agents.
- **Threat categories:** Delegation abuse, impersonation, over-scoped authority.
- **Method:** Identity/authorization threat model + controls.
- **Machine-readability:** None.
- **Cached PDF:** south-2025-authenticated-delegation.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-097 OpenID Foundation: identity management for agentic AI

- **Source:** S-0819: T. South, S. Nagabhushanaradhya, A. Dissanayaka, S. Cecchetti et al. (21 authors), "Identity Management for Agentic AI: The new frontier of authorization, authentication, and security for an AI agent world", OpenID Foundation white paper, arXiv:2510.25819, 2025-10 [link](https://arxiv.org/abs/2510.25819) (type framework; confidence high)
- **Decomposition:** Agent authentication/authorization landscape and agenda.
- **Assets:** agent-to-service access.
- **Threat categories:** Weak agent identity, shared credentials, MCP auth gaps.
- **Method:** Standards-body white paper.
- **Machine-readability:** PDF.
- **Cached PDF:** south-2025-identity-management-agentic.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-098 CSA Agentic AI Red Teaming Guide

- **Source:** S-0802: Cloud Security Alliance, "Agentic AI Red Teaming Guide", 2025-05-28. [link](https://cloudsecurityalliance.org/artifacts/agentic-ai-red-teaming-guide) (type framework; confidence medium)
- **Decomposition:** Per-category test requirements and steps.
- **Assets:** agent capabilities.
- **Threat categories:** Permission escalation, hallucination, orchestration flaws, memory manipulation, supply chain, others.
- **Method:** Test methodology.
- **Machine-readability:** Login-gated PDF (not read).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

## D. Asset-specific, frontier-model, sector and governance threat models

### TM-099 RAND: Securing AI Model Weights

- **Source:** S-0793: Sella Nevo, Dan Lahav, Ajay Karpur, Yogev Bar-On, Henry Alexander Bradley, Jeff Alstott, "Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models", RAND RR-A2849-1, 2024-05-30. [link](https://www.rand.org/pubs/research_reports/RRA2849-1.html) (type framework; confidence high)
- **Decomposition:** Attacker operational capacity OC1-OC5 x ~38 attack vectors in 9 categories; security levels SL1-SL5 with benchmark controls.
- **Assets:** frontier model weights.
- **Threat categories:** Insider, intrusion, supply chain, physical, side channel, nation-state operations.
- **Method:** Expert-estimated feasibility per vector and OC level; graded controls.
- **Machine-readability:** Report tables (encodable as vector -> feasible-for OC).
- **Cached PDF:** rand-securing-ai-model-weights-2024.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-100 Anthropic Responsible Scaling Policy v2.2 (ASL-3 security standard)

- **Source:** S-0798: Anthropic, "Responsible Scaling Policy", Version 2.2, effective 2025-05-14. [link](https://www.anthropic.com/rsp) (type framework; confidence high)
- **Decomposition:** Attacker groups in scope for weight theft; deployment vs security standards.
- **Assets:** model weights; deployed models.
- **Threat categories:** Weight theft; jailbreak-driven misuse.
- **Method:** Capability-threshold governance.
- **Machine-readability:** Web/PDF.
- **Cached PDF:** anthropic-rsp-v2-2.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-101 Google DeepMind Frontier Safety Framework v3.0

- **Source:** S-0805: Google DeepMind, "Frontier Safety Framework", Version 3.0, 2025-09-22. [link](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/strengthening-our-frontier-safety-framework/frontier-safety-framework_3.pdf) (type framework; confidence high)
- **Decomposition:** Critical Capability Levels -> security levels aligned with RAND; security vs deployment mitigations.
- **Assets:** model weights.
- **Threat categories:** Weight exfiltration; misuse.
- **Method:** Capability governance.
- **Machine-readability:** PDF.
- **Cached PDF:** gdm-frontier-safety-framework-v3.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-102 EU GPAI Code of Practice: Safety and Security chapter

- **Source:** S-0851: European Commission / AI Office, "The General-Purpose AI Code of Practice", published 2025-07-10; Safety and Security chapter PDF [link](https://ec.europa.eu/newsroom/dae/redirection/document/118119) (type standard; confidence high)
- **Decomposition:** Systemic-risk identification with scenarios; Security Goal naming threat actors incl. insiders and (self-)exfiltration; Appendix 4 mitigations; incident reporting timelines.
- **Assets:** GPAI model weights and infrastructure.
- **Threat categories:** Model theft, insider sabotage, self-exfiltration.
- **Method:** Regulatory commitments (Art. 55).
- **Machine-readability:** PDF.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-103 NIST AI 800-1 (2nd draft): managing misuse risk for dual-use foundation models

- **Source:** S-0811: U.S. AI Safety Institute (NIST), "Managing Misuse Risk for Dual-Use Foundation Models", NIST AI 800-1 Second Public Draft, January 2025. [link](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-1.ipd2.pdf) (type framework; confidence high)
- **Decomposition:** Objectives: identify (threat profiles), plan, protect from unauthorized access, measure, mitigate.
- **Assets:** foundation model weights and capabilities.
- **Threat categories:** Misuse enablement, weight theft.
- **Method:** Practice 1.2 threat profiles.
- **Machine-readability:** PDF.
- **Cached PDF:** nist-ai-800-1-ipd2.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-104 Google DeepMind: An approach to technical AGI safety and security

- **Source:** S-0763: R. Shah, A. Irpan, A. M. Turner, A. Wang, A. Conmy et al. (30 authors), "An Approach to Technical AGI Safety and Security", arXiv:2504.01849, 2025 [link](https://arxiv.org/abs/2504.01849) (type threat-model; confidence high)
- **Decomposition:** Four risk areas (misuse, misalignment, mistakes, structural); two lines of defense; model as potential insider.
- **Assets:** AI system with dangerous capabilities.
- **Threat categories:** Misuse, misalignment.
- **Method:** Safety cases + system-level controls.
- **Machine-readability:** Paper.
- **Cached PDF:** shah-2025-gdm-agi-safety-security.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-105 Shanghai AI Lab frontier risk framework in practice (SafeWork-F1)

- **Source:** S-0764: Shanghai AI Lab (X. Chen, Y. Chen, Z. Chen et al., 38 authors), "Frontier AI Risk Management Framework in Practice: A Risk Analysis Technical Report", arXiv:2507.16534, 2025 [link](https://arxiv.org/abs/2507.16534) (type threat-model; confidence high)
- **Decomposition:** E-T-C analysis: deployment Environment, Threat source, enabling Capability; red/yellow lines.
- **Assets:** frontier models.
- **Threat categories:** Cyber offense, bio/chem, persuasion, uncontrolled AI R&D, deception, self-replication, collusion.
- **Method:** Zoned evaluation.
- **Machine-readability:** Report.
- **Cached PDF:** shanghai-ai-lab-2025-frontier-risk-framework.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-106 International AI Safety Report 2026

- **Source:** S-0768: Y. Bengio, S. Clare, C. Prunkl, M. Andriushchenko, B. Bucknall et al. (92 authors), "International AI Safety Report 2026", arXiv:2602.21012, 2026-02 [link](https://arxiv.org/abs/2602.21012) (type threat-model; confidence high)
- **Decomposition:** Malicious use, malfunctions, systemic risks; risk management.
- **Assets:** society and organizations.
- **Threat categories:** AI crime, influence, cyberattacks, bio/chem, reliability, loss of control.
- **Method:** Evidence synthesis.
- **Machine-readability:** PDF (ToC read).
- **Cached PDF:** bengio-2026-international-ai-safety-report.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-107 The Malicious Use of AI (Brundage et al.)

- **Source:** S-0726: M. Brundage, S. Avin, J. Clark, H. Toner, P. Eckersley et al. (26 authors), "The Malicious Use of Artificial Intelligence: Forecasting, Prevention, and Mitigation", arXiv:1802.07228, 2018 [link](https://arxiv.org/abs/1802.07228) (type threat-model; confidence high)
- **Decomposition:** Digital, physical, political security domains; expansion, novelty, changed character of attacks.
- **Assets:** organizations and society.
- **Threat categories:** Automated spear phishing, vulnerability discovery, drones, surveillance, disinformation.
- **Method:** Forecasting + recommendations.
- **Machine-readability:** None.
- **Cached PDF:** brundage-2018-malicious-use-ai.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-108 Generative LMs and automated influence operations (Goldstein et al.)

- **Source:** S-0734: J. A. Goldstein, G. Sastry, M. Musser, R. DiResta, M. Gentzel et al., "Generative Language Models and Automated Influence Operations: Emerging Threats and Potential Mitigations", arXiv:2301.04246, 2023 [link](https://arxiv.org/abs/2301.04246) (type threat-model; confidence high)
- **Decomposition:** Four-stage pipeline: model construction, model access, content dissemination, belief formation.
- **Assets:** public trust, brand.
- **Threat categories:** AI-enabled influence operations.
- **Method:** Mitigation per stage.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-109 The threat of offensive AI to organizations (Mirsky et al.)

- **Source:** S-0689: Y. Mirsky, A. Demontis, J. Kotak, R. Shankar et al., "The Threat of Offensive AI to Organizations", Computers & Security 126, 2023. DOI 10.1016/j.cose.2022.103006; arXiv:2106.15764 [link](https://arxiv.org/abs/2106.15764) (type survey; confidence high)
- **Decomposition:** AI-enabled attacks across the cyber kill chain.
- **Assets:** organizations.
- **Threat categories:** Recon, deepfake social engineering, exploit development, evasion, automation.
- **Method:** Survey + practitioner ranking.
- **Machine-readability:** None.
- **Cached PDF:** mirsky-2023-offensive-ai-organizations.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-110 Framework for evaluating emerging cyberattack capabilities of AI (Google DeepMind)

- **Source:** S-0817: M. Rodriguez et al., "A Framework for Evaluating Emerging Cyberattack Capabilities of AI", arXiv 2025. arXiv:2503.11917 [link](https://arxiv.org/abs/2503.11917) (type framework; confidence medium (capped))
- **Decomposition:** Attack-chain archetypes from 12,000 real AI-involved attacks; phase bottlenecks.
- **Assets:** enterprise.
- **Threat categories:** AI cost reduction per kill-chain phase.
- **Method:** Benchmark of 50 challenges; defender prioritization.
- **Machine-readability:** Paper.
- **Cached PDF:** rodriguez-2025-cyberattack-capability-framework.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-111 ENISA-JRC: AI in autonomous driving

- **Source:** S-0730: ENISA and EC JRC, "Cybersecurity Challenges in the Uptake of Artificial Intelligence in Autonomous Driving", 2021-02-11. [link](https://www.enisa.europa.eu/publications/enisa-jrc-cybersecurity-challenges-in-the-uptake-of-artificial-intelligence-in-autonomous-driving) (type threat-model; confidence medium)
- **Decomposition:** Automotive AI functions and their security.
- **Assets:** vehicle perception stack.
- **Threat categories:** Perception attacks.
- **Method:** Report (PDF not read).
- **Machine-readability:** PDF.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-112 ISO/SAE 21434 TARA + STPA-Sec for AV perception (Ghosh et al.)

- **Source:** S-0733: S. Ghosh, A. Zaboli, J. Hong, J. Kwon, "An Integrated Approach of Threat Analysis for Autonomous Vehicles Perception System", IEEE Access, 2023. DOI 10.1109/ACCESS.2023.3243906 [link](https://doi.org/10.1109/ACCESS.2023.3243906) (type threat-model; confidence medium)
- **Decomposition:** Perception system (sensors, compute, AI) and environment.
- **Assets:** AV perception.
- **Threat categories:** Sensor spoofing/jamming, AI perception manipulation.
- **Method:** TARA vs STPA-Sec comparison + mathematical framework.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-113 AI-enhanced TARA for connected and autonomous vehicles

- **Source:** S-0365: U. Ahmad, M. Han, S. Mahmood, "AI-Enhanced threat analysis and risk assessment for connected and autonomous vehicles", Software Quality Journal, 2025. DOI 10.1007/s11219-025-09723-6 [link](https://doi.org/10.1007/s11219-025-09723-6) (type paper; confidence low)
- **Decomposition:** Metadata only; unclear whether AI components are modelled as targets.
- **Assets:** ?
- **Threat categories:** ?
- **Method:** ?
- **Machine-readability:** ?
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-114 CISA et al.: Principles for the secure integration of AI in OT

- **Source:** S-0848: CISA, ASD's ACSC, NSA AISC, FBI, CCCS, BSI, NCSC-NL, NCSC-NZ, NCSC-UK, "Principles for the Secure Integration of Artificial Intelligence in Operational Technology", joint guidance, 2025-12-03. PDF: [link](https://www.cisa.gov/sites/default/files/2026-01/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508cV2.pdf) (type standard; confidence medium)
- **Decomposition:** Four principles over ML, LLM and agents in OT (see RPT-0009).
- **Assets:** OT process.
- **Threat categories:** Safety/security/reliability risks; prompt injection.
- **Method:** Joint guidance.
- **Machine-readability:** PDF.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-115 TC260 AI Safety Governance Framework 1.0 (and CAC 2.0, 2025)

- **Source:** S-0794: TC260, 《人工智能安全治理框架》1.0版 ("AI Safety Governance Framework v1.0"), 2024-09-09. [link](https://www.cac.gov.cn/2024-09/09/c_1727567886199789.htm) (type framework; confidence high)
- **Decomposition:** Inherent risks (model/algorithm, data, system) vs application risks (cyberspace, real-world, cognitive, ethical).
- **Assets:** AI system.
- **Threat categories:** Two-level risk taxonomy.
- **Method:** Governance measures; 2.0 adds risk grading.
- **Machine-readability:** Web text (2.0 attachment not extracted).
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-116 AI System Threat Vector Taxonomy (Huwyler)

- **Source:** S-0409: H. Huwyler, "Standardized Threat Taxonomy for AI Security, Governance, and Regulatory Compliance", arXiv:2511.21901, 2025. [link](https://arxiv.org/abs/2511.21901) (type paper; confidence medium)
- **Decomposition:** 9 domains, 53 sub-threats mapped to loss categories.
- **Assets:** AI assets.
- **Threat categories:** Misuse, poisoning, privacy, adversarial, bias, unreliable outputs, drift, supply chain, IP.
- **Method:** Quantitative (FAIR-style) risk.
- **Machine-readability:** None.
- **Cached PDF:** huwyler-ai-threat-taxonomy-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-124 OpenAI Preparedness Framework v2 (v0.2)

- **Source:** S-0814: OpenAI, "Preparedness Framework" (updated version, 2025). [link](https://openai.com/index/updating-our-preparedness-framework/) (type framework; confidence low: the page returned 403 to automated fetch in this run and in v0.1)
- **Decomposition:** tracked capability categories with capability thresholds and required safeguards (per the source title; not read).
- **Assets:** frontier model capabilities and weights.
- **Threat categories:** not read.
- **Method:** capability evaluation against thresholds, safeguards reports.
- **Machine-readability:** None.
- **Cached PDF:** —
- **Capture status:** not read (403); needs detailed analysis (#73)

### TM-125 Meta Frontier AI Framework (v0.2)

- **Source:** S-1179: Meta, "Our Approach to Frontier AI", 2025-02-03. [link](https://about.fb.com/news/2025/02/meta-approach-frontier-ai/) (type framework; confidence medium)
- **Decomposition:** outcome-led: catastrophic outcomes in two domains (cybersecurity; chemical and biological), threat scenarios from threat-modelling exercises, risk thresholds by how much a model facilitates a scenario.
- **Assets:** frontier model and its release decision.
- **Threat categories:** cyber and chemical/biological misuse scenarios.
- **Method:** threat modelling with external experts; thresholds gate development and release (actions per threshold not stated in the announcement).
- **Machine-readability:** None.
- **Cached PDF:** — (framework PDF at ai.meta.com returned an error)
- **Capture status:** announcement only; needs detailed analysis (#73)

## E. Tools that generate or support AI-aware threat models (comparators for tmodel)

### TM-117 STRIDE GPT

- **Source:** S-0967: M. Adams, "STRIDE GPT", GitHub mrwadams/stride-gpt, commit a072e8a9f3db (2026-10-02). [link](https://github.com/mrwadams/stride-gpt) (type tool; confidence high)
- **Decomposition:** Application description/diagram/repo -> STRIDE threats, attack trees, DREAD, mitigations, tests.
- **Assets:** from input.
- **Threat categories:** STRIDE + OWASP LLM/ASI pattern detection.
- **Method:** LLM generation.
- **Machine-readability:** Yes: JSON, SARIF, Markdown.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-118 AegisShield

- **Source:** S-0960: M. Grofsky, "AegisShield: Democratizing Cyber Threat Modeling with Generative AI", arXiv:2509.10482, 2025. [link](https://arxiv.org/abs/2509.10482) (type tool; confidence medium)
- **Decomposition:** STRIDE + ATT&CK with NVD and OTX feeds.
- **Assets:** generic systems.
- **Threat categories:** STRIDE/ATT&CK.
- **Method:** LLM generation evaluated against 243 expert threats.
- **Machine-readability:** Tool output.
- **Cached PDF:** grofsky-aegisshield-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-119 ThreMoLIA

- **Source:** S-0765: F. V. Jedrzejewski, D. Fucci, O. Adamov, "ThreMoLIA: Threat Modeling of Large Language Model-Integrated Applications", arXiv:2504.18369, 2025. [link](https://arxiv.org/abs/2504.18369) (type threat-model; confidence medium)
- **Decomposition:** LLM + RAG over prior threat models and architecture repositories.
- **Assets:** LLM-integrated apps.
- **Threat categories:** LIA threats.
- **Method:** Research plan + early evaluation.
- **Machine-readability:** Tool (planned).
- **Cached PDF:** jedrzejewski-thremolia-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-120 LLMs' suitability for STRIDE classification (5G case)

- **Source:** S-0362: A. AbdulGhaffar, A. Matrawy, "LLMs' Suitability for Network Security: A Case Study of STRIDE Threat Modeling", arXiv:2505.04101, 2025. [link](https://arxiv.org/abs/2505.04101) (type paper; confidence high)
- **Decomposition:** Prompting techniques x LLMs for STRIDE labels.
- **Assets:** 5G threats.
- **Threat categories:** STRIDE.
- **Method:** Evaluation of LLM labelling accuracy.
- **Machine-readability:** None.
- **Cached PDF:** abdulghaffar-llm-stride-network-2025.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-121 ATLAS-aligned executable assessment rules (Huang, Halak, Kang)

- **Source:** S-0823: Y. Huang, B. Halak, B. Kang, "A Deterministic and Auditable AI Security Risk Assessment Framework with ATLAS Aligned Executable Rules and Formal Verification", arXiv:2610.01436, 2026-10-01. [link](https://arxiv.org/abs/2610.01436) (type framework; confidence high)
- **Decomposition:** Engineering evidence -> control-id taxonomy (4-level ordinal) -> technique predicates compiled from a pinned ATLAS snapshot.
- **Assets:** system evidence.
- **Threat categories:** ATLAS techniques.
- **Method:** Deterministic decision function with formal verification.
- **Machine-readability:** Described, not confirmed: the paper describes executable rules compiled from a pinned ATLAS snapshot; no rules artifact was fetched (v0.2).
- **Cached PDF:** huang-2026-atlas-aligned-executable-rules.pdf
- **Capture status:** needs detailed analysis (#73)

### TM-122 Continuous threat modeling for AI-driven development (talk)

- **Source:** S-1077: "Detecting Security Posture Drift in AI-Driven Software Development via Continuous Threat Modeling", USENIX Security 2026 (talk; speaker not listed on the page). [link](https://www.usenix.org/conference/usenixsecurity26/presentation/ravindra) (type vendor-research; confidence low)
- **Decomposition:** Threat models derived from code/infra/config with diffs over time.
- **Assets:** codebase and infrastructure.
- **Threat categories:** Posture drift.
- **Method:** Threat-model diffing.
- **Machine-readability:** Talk.
- **Cached PDF:** —
- **Capture status:** needs detailed analysis (#73)

### TM-123 MCPThreatHive

- **Source:** S-0964: Y. T. Shen, K. Toyoda, A. Leung, "MCPThreatHive: Automated Threat Intelligence for Model Context Protocol Ecosystems", arXiv:2604.13849, 2026. [link](https://arxiv.org/abs/2604.13849) (type tool; confidence high)
- **Decomposition:** Multi-source MCP threat intel -> AI extraction -> KG with STRIDE/OWASP/ASI mappings + risk score.
- **Assets:** MCP ecosystem.
- **Threat categories:** MCP-38.
- **Method:** Automated KG pipeline.
- **Machine-readability:** Open source (claimed).
- **Cached PDF:** shen-mcpthreathive-2026.pdf
- **Capture status:** needs detailed analysis (#73)


## Observations for #73 and #74

These are the synthesis agent's reading, offered as hypotheses for the human reviewers.

1. **Five decomposition styles recur.** (a) Lifecycle stage x attacker capability (Papernot, NIST AI 100-2, Verma, NCSC/CISA, ETSI, CSA Singapore). (b) Component or layer (BIML ARA, SAIF/CoSAI, DASF, MAESTRO, Huang's five MCP components, AWS DFD). (c) Asset x capability or property (Mauri & Damiani STRIDE-AI, ENISA 2020, Sanchez Vicarte, ThreatFinderAI, RAND for weights, AgentHeLLM). (d) Capability composition rules for agents (lethal trifecta, Rule of Two, MATA trust inheritance, design patterns). (e) Attack-sequence models (attack trees, ATAG attack graphs, Promptware Kill Chain). A generator needs all five: (b) to place threats on a company's architecture, (c) to say what is damaged, (a) to state preconditions, (d) as cheap mechanical checks, (e) to chain steps into paths.
2. **Only a handful are machine-readable today.** Confirmed (fetched): CoSAI Risk Map (YAML + JSON Schema, Apache-2.0), AWS Threat Composer example (JSON), and ATLAS itself (in enumerations.md); STRIDE GPT emits JSON/SARIF. Described but not confirmed (no public artifact retrieved): ATAG's MulVAL/Datalog rules (TM-066) and the ATLAS-aligned executable rules (TM-121). Everything else is PDF or HTML and needs extraction in #73.
3. **Asset models are the weakest part of the literature.** Most agentic models leave assets implicit per layer. The explicit asset models are predictive-ML era (ENISA 2020, STRIDE-AI, Sanchez Vicarte) or narrow (RAND for weights, AgentHeLLM for vehicle occupants, Owner-Harm for the deployer). Only the AWS Threat Composer GenAI example (TM-026) mixes business and AI assets, as free text without a vocabulary; none covers compute spend or executive likeness, which a company threat model needs (report section 4 proposes a working asset vocabulary). The AWS Generative AI Security Scoping Matrix (TM-126) is the most direct company-profile axis: what the company owns decides which threats it treats.
4. **Attacker models exist but are rarely calibrated.** Grosse et al. show academic threat models are too generous (data fractions, query budgets); Apruzzese et al. show real attackers use cheap problem-space methods; RAND gives the only tiered attacker-capability model (OC1-OC5). tmodel's precondition fields should carry calibrated values, not just "white-box".
5. **Gold sets for evaluating generated threat models.** The Threat Composer GenAI example (37 threats, 84 mitigations), the Trail of Bits YOLOv7 model, the OWASP MAS worked examples (three systems) and the MAESTRO case studies are the best candidates. AegisShield's evaluation method (243 expert threats) is a reusable protocol.
6. **Direct comparators to tmodel.** ThreatFinderAI, ASTRIDE, ThreMoLIA, PriMod4AI, PILLAR, STRIDE GPT, AegisShield and MCPThreatHive all generate or support AI-aware threat models; MCPThreatHive also loads a KG. None records human review of each generated threat as a first-class object, which is ARCH-0001's distinguishing requirement (R-018).
7. **Name collisions need distinct ids.** Two different "STRIDE-AI" methods exist (Mauri & Damiani 2022; Cyrille & Schwarz 2026). Several OWASP agentic documents reuse T-codes with different scopes. Store (publisher, document, version, id).

## Comparison table

Columns: scope; primary decomposition axis; asset model (explicit `yes`, `implicit`, `no`); attacker model; stable threat ids; mitigations linked; machine-readable; validation evidence. `?` = not determined from what was read.

| id | model | source | scope | primary axis | asset model | attacker model | stable threat ids | mitigations linked | machine-readable | validation |
|---|---|---|---|---|---|---|---|---|---|---|
| TM-001 | SoK: Security and Privacy in ML (Papernot et al.) | S-0673 | ML | lifecycle stage x capability | implicit | yes | no | partial | no | literature |
| TM-002 | Wild Patterns (Biggio & Roli): goal-knowledge-capability attacker model | S-0672 | ML | attacker goal x knowledge x capability | no | yes (canonical) | no | partial | no | literature |
| TM-003 | On Evaluating Adversarial Robustness (threat-model specification checklist) | S-0058 | ML | adversary specification | no | yes | no | no | no | community practice |
| TM-004 | NIST AI 100-2 E2025 adversarial ML taxonomy (attacker-model axes) | S-0855 | ML+GenAI | objective x capability x knowledge | implicit | yes | yes | yes | no (ids only) | government consensus |
| TM-005 | Towards More Practical Threat Models in AI Security (Grosse et al., USENIX Sec 2024) | S-0740 | ML | attack x attacker access | no | yes (calibrated) | no | no | no | 271-practitioner survey |
| TM-006 | Threat Assessment in ML-based Systems (Tidjon & Khomh) | S-0732 | ML | ML phase x TTP | no | implicit | ATLAS ids | no | no | 89 scenarios + 854 repos |
| TM-007 | ADMIn: Attacks on Dataset, Model and Input | S-0737 | ML | target asset (D/M/I) | yes (3 types) | partial | no | partial | no | 2 case studies |
| TM-008 | STRIDE-AI (Mauri & Damiani) | S-0731 | ML | asset x property x STRIDE | yes | partial | no | partial | tables only | 1 H2020 use case |
| TM-009 | Attack Tree Analysis for Adversarial Evasion Attacks | S-0736 | ML | attack tree | no | yes | no | no | no | illustrative |
| TM-010 | Threat Modeling for AI: the case for an asset-centric approach (Intel) | S-0762 | ML+GenAI | asset x capability | yes (8 types) | yes (capabilities) | no | no | no | argument |
| TM-011 | ThreatFinderAI: asset-centric threat modeling for AI-based systems | S-0744 | ML+LLM | asset | yes | partial | via libraries | yes | tool | user study |
| TM-012 | Microsoft: Threat Modeling AI/ML Systems and Dependencies (SDL supplement) | S-0727 | ML | threat with traditional parallel | implicit | partial | no | yes | semi | industry practice |
| TM-013 | Failure Modes in Machine Learning (Kumar et al.) | S-0872 | ML | intent x property | no | partial | named modes | no | no | 23 partners' input |
| TM-014 | BIML Architectural Risk Analysis of ML Systems (BIML-78) | S-0728 | ML | component | yes (9) | implicit | yes (component:n:name) | no | parseable | expert analysis |
| TM-015 | ENISA AI Threat Landscape (2020) | S-0729 | ML | asset x lifecycle | yes | no | ENISA codes | no | no | expert |
| TM-016 | ENISA Securing Machine Learning Algorithms (2021) | S-0781 | ML | threat x vulnerability x control | implicit | no | named | yes | no | expert |
| TM-017 | ETSI GR SAI 001 AI Threat Ontology | S-0834 | ML | ontology | implicit | yes | no | no | ontology text | standards body |
| TM-018 | ETSI GR SAI 004 Problem Statement | S-0832 | ML | lifecycle stage | implicit | no | no | no | no | standards body |
| TM-019 | NCC Group: Practical Attacks on Machine Learning Systems | S-0972 | ML | attack surface | implicit | partial | no | partial | no | reproductions |
| TM-020 | Trail of Bits YOLOv7 threat model and code review | S-0735 | ML pipeline | trust zone x actor | yes | yes (6 actors) | finding ids | yes | tables | real code review |
| TM-021 | Trail of Bits: Toward Comprehensive Risk Assessments and Assurance of AI-Based Systems | S-0786 | system | hazard / ODD | implicit | no | no | no | no | position |
| TM-022 | NVIDIA AI Red Team assessment framework | S-0784 | ML | lifecycle x assessment area | implicit | partial | no | no | no | practice |
| TM-023 | "Real Attackers Don't Compute Gradients" (calibration) | S-0685 | ML | attacker economics | no | yes (realistic) | no | no | no | case studies |
| TM-024 | BIML Architectural Risk Analysis of LLMs (81 risks) | S-0739 | LLM | component + vendor boundary | yes | implicit | yes | no | parseable | expert analysis |
| TM-025 | AWS: Threat modeling your generative AI workload (+ re:Invent SEC214) | S-0738 | LLM app | DFD + threat statements | yes | yes (prerequisites) | per-file ids | yes | JSON via Threat Composer | worked example |
| TM-026 | AWS Threat Composer GenAI chatbot example workspace | S-0950 | LLM app | threat statement | yes | yes | yes (file) | yes | yes (JSON) | gold example |
| TM-027 | NCC Group: Models-As-Threat-Actors (MATA) and secure AI design principles | S-0742 | LLM app | trust-label propagation | implicit | yes (model as actor) | no | yes (principles) | rule-encodable | practice |
| TM-028 | Threat modelling LLM-powered applications with STRIDE + DREAD (Tete) | S-0743 | LLM app | STRIDE | implicit | no | no | partial | no | 1 student case |
| TM-029 | Operationalizing a Threat Model for Red-Teaming LLMs (Verma et al., TMLR) | S-0745 | LLM | entry point (stage) | implicit | yes (required access) | no | yes | no | SoK |
| TM-030 | LLM Platform Security: systematic evaluation of ChatGPT plugins (Iqbal et al.) | S-0741 | LLM platform | stakeholder pair | implicit | yes (stakeholders) | no | partial | no | ecosystem measurement |
| TM-031 | A New Era in LLM Security (Wu et al.): information-flow constraints | S-0746 | LLM app | information flow | implicit | yes | no | no | no | GPT-4 analysis |
| TM-032 | Microsoft AI Red Team ontology (Lessons from red teaming 100 GenAI products) | S-0753 | GenAI system | system-actor-TTP-weakness-impact | implicit | yes | via ATLAS | no | schema-like | 100 engagements |
| TM-033 | STRIDE-AI for Generative AI (Cyrille & Schwarz; name clash) | S-0771 | LLM app | STRIDE x OWASP LLM | implicit | partial | OWASP ids | yes | tool | 1 case |
| TM-034 | LINDDUN-based privacy threat modeling for GenAI (Liao et al., SOUPS 2026) | S-0773 | GenAI | DFD x LINDDUN | yes (DFD) | partial | LINDDUN ids | yes | KB | agent validation |
| TM-035 | PriMod4AI: lifecycle-aware privacy threat modeling with LLMs | S-0777 | AI system | DFD x lifecycle | yes | partial | LINDDUN | partial | KB | prototype |
| TM-036 | PILLAR: LLM-assisted LINDDUN privacy threat modeling | S-0959 | generic | DFD x LINDDUN | yes | no | LINDDUN | partial | tool | prototype |
| TM-037 | RAG Security and Privacy: formal threat model (Arzanipour et al.) | S-0748 | RAG | adversary access level | yes | yes (formal) | no | partial | formal | formal |
| TM-038 | Securing RAG: risk assessment and mitigation framework (Ammann et al.) | S-0797 | RAG | pipeline stage | implicit | no | no | yes | no | practitioner |
| TM-039 | Towards Secure RAG: review of threats, defenses and benchmarks | S-0721 | RAG | workflow stage | implicit | partial | no | yes | no | survey |
| TM-040 | Google Secure AI Framework (SAIF) risk map | S-0780 | ML+GenAI+agent | component x persona | yes | implicit | yes (codes) | yes | via CoSAI | vendor |
| TM-041 | CoSAI Risk Map (secure-ai-tooling) | S-0900 | ML+GenAI+agent | component x persona x risk | yes | yes (actorAccess) | yes (camelCase) | yes | yes (YAML) | industry consortium |
| TM-042 | OWASP AI Exchange | S-0826 | ML+GenAI+agent | attack surface | yes | partial | section ids | yes | semi (links) | community |
| TM-043 | Databricks AI Security Framework (DASF 2.0/3.0) | S-0779 | ML+GenAI+agent | component | yes | no | yes | yes | no | vendor |
| TM-044 | Cisco Integrated AI Security and Safety Framework | S-0801 | GenAI+agent | objective -> technique | implicit | implicit | yes | partial | claimed | vendor |
| TM-045 | MITRE SAFE-AI | S-0809 | ML+GenAI | element x ATLAS | yes (4) | via ATLAS | ATLAS ids | yes (800-53) | appendix tables | government |
| TM-046 | Japan AISI Guide to Red Teaming Methodology on AI Safety | S-0791 | LLM | attack type | implicit | no | no | yes | no | government |
| TM-047 | BSI: Evasion Attacks on LLMs, countermeasures in practice | S-0844 | LLM+agent | entry point x countermeasure | implicit | yes (position) | countermeasure codes | yes | codes | government |
| TM-048 | BSI: Generative AI Models, Opportunities and Risks | S-0845 | GenAI | risk class | no | no | partial | yes | table | government |
| TM-049 | ANSSI: Security recommendations for a GenAI system | S-0836 | GenAI | architecture layer | implicit | no | R ids | yes | no | government |
| TM-050 | ANSSI-led joint high-level risk analysis on AI | S-0747 | org + AI system | risk scenario | yes | yes | no | partial | no | multinational |
| TM-051 | CSA Singapore Guidelines on Securing AI Systems | S-0837 | ML+GenAI | lifecycle | implicit | no | no | yes | no | government |
| TM-052 | CSA Singapore Companion Guide on Securing AI Systems | S-0789 | ML+GenAI | lifecycle x ATLAS | implicit | via ATLAS | ATLAS ids | yes | tables | government |
| TM-053 | NCSC/CISA Guidelines for Secure AI System Development | S-0835 | ML+GenAI | lifecycle | implicit | no | no | partial | no | government |
| TM-054 | ETSI EN 304 223 Baseline Cyber Security Requirements for AI (from UK Code of Practice) | S-0849 | ML+GenAI | lifecycle x principle | implicit | no | provision ids | yes | no | EN standard |
| TM-055 | NIST AI 600-1 Generative AI Profile | S-0792 | GenAI | risk category | no | no | action ids | yes | no | government |
| TM-056 | Canadian Centre for Cyber Security ITSAP.00.041 Generative AI | S-0846 | GenAI (org) | risk list | no | no | no | yes | no | government |
| TM-057 | PLOT4ai: Library of AI threats (cards) | S-0881 | trustworthy AI | card question | implicit | no | card ids | partial | partial | practice |
| TM-058 | CSA MAESTRO | S-0754 | agent | layer | implicit | no | layer ids | yes | no | case studies (see Zambare, Habler) |
| TM-059 | OWASP Agentic AI Threats and Mitigations v1.1 (T1-T17) | S-0760 | agent | capability navigator | implicit | partial | yes (T1-T17) | yes | no | community |
| TM-060 | OWASP Multi-Agentic System Threat Modelling Guide v1.0 | S-0761 | multi-agent | layer x T-code | implicit | partial | T-ids | yes | tables | 3 worked examples |
| TM-061 | OWASP Securing Agentic Applications Guide 1.0 | S-0816 | agent | component (unconfirmed) | ? | ? | T-ids | yes | no | community |
| TM-062 | Extending the OWASP MAS Threat Modeling Guide (Krawiecka & Schroeder de Witt) | S-0758 | multi-agent | emergent threat class | no | partial | no | partial | no | literature |
| TM-063 | Microsoft Taxonomy of Failure Modes in Agentic AI Systems v2.0 | S-0902 | agent | novelty x safety/security | no | implicit | named modes | yes | no | 12 months red teaming (claimed) |
| TM-064 | ATFAA and SHIELD (Narajala & Narayan) | S-0759 | agent | domain x STRIDE | implicit | partial | T1-T9 | yes | no | no empirical validation |
| TM-065 | ASTRIDE: STRIDE + A for agentic AI (platform) | S-0749 | agent | DFD x STRIDE+A | yes (DFD) | no | category | no | tool | self-evaluated |
| TM-066 | ATAG: AI-agent application threat assessment with attack graphs | S-0750 | agent | attack graph | yes (topology facts) | yes (initial access) | LVD ids | no | described (Datalog), not retrieved | 2 case studies |
| TM-067 | MATRA: modeling the attack surface of agentic AI (OpenClaw case) | S-0774 | agent (deployment) | asset impact + attack tree | yes | yes | no | yes | no | 1 deployment |
| TM-068 | Owner-Harm: the agent as a threat to its deployer | S-0775 | agent | harm category | yes (owner assets) | yes | no | yes | benchmark | 300 scenarios |
| TM-069 | Agent Security is a Systems Problem (Christodorescu et al.) | S-0769 | agent | principle violation | implicit | yes | no | yes | rule-encodable | 11 incidents |
| TM-070 | The lethal trifecta (Willison) | S-0820 | agent | capability triple | no | yes | no | yes | rule | incident list |
| TM-071 | Agents Rule of Two (Meta) | S-0808 | agent | capability triple | no | yes | no | yes | rule | design guidance |
| TM-072 | Design patterns for securing LLM agents against prompt injection | S-0799 | agent | control pattern | no | yes | pattern names | yes (controls) | no | case studies |
| TM-073 | Google's approach for secure AI agents | S-0806 | agent | risk x principle | implicit | partial | no | yes | no | vendor |
| TM-074 | OpenAI: Practices for governing agentic AI systems | S-0785 | agent | party x practice | no | no | practice ids | yes | no | position |
| TM-075 | AI Agents Under Threat (Deng et al., ACM CSUR) | S-0701 | agent | knowledge gap | no | partial | no | yes | no | survey |
| TM-076 | Cross-dimensional threat taxonomy for agentic AI (Baek et al.) | S-0711 | agent | surface x boundary x property x architecture | yes (surfaces) | implicit | no | no | schema | 66 studies |
| TM-077 | SoK: the attack surface of agentic AI (Dehghantanha & Homayoun) | S-0714 | agent | layer x trust boundary | implicit | yes | no | yes | no | SoK |
| TM-078 | Systematization of computer-use agent vulnerabilities (Microsoft) | S-0703 | CUA | risk class + root cause | implicit | yes | no | yes | no | 3 exploits |
| TM-079 | Threat model for prompt injection in multi-agent systems (Paul & Nandy) | S-0776 | multi-agent | vector category | implicit | yes | vector ids | yes (measured) | no | 6-agent testbed |
| TM-080 | Secure agentic AI with A2A, MAESTRO applied (Habler et al.) | S-0755 | A2A protocol | MAESTRO layer | implicit | partial | no | yes | no | worked protocol |
| TM-081 | Threat modeling for agent protocols: MCP, A2A, Agora, ANP | S-0767 | agent protocols | protocol x lifecycle | implicit | yes (malicious peer/registry) | 12 risk ids | partial | no | comparative |
| TM-082 | MCP landscape, threats and directions (Hou et al.) | S-0757 | MCP | lifecycle phase x attacker type | implicit | yes (4 types) | scenario ids | yes | no | case studies |
| TM-083 | MCP threat modeling with STRIDE and DREAD (Huang et al.) | S-0772 | MCP | component x STRIDE | yes (5) | partial | no | yes | no | 7 clients |
| TM-084 | MCP-38 threat taxonomy (+ MCPThreatHive) | S-0909 | MCP | threat category | implicit | no | yes (MCP-01..38) | partial | ids + tool | incident synthesis |
| TM-085 | CoSAI MCP Security (WS4) | S-0770 | MCP | threat category x control | implicit | no | MCP-T1..T12 | yes | table | consortium |
| TM-086 | Securing MCP: risks, controls, governance (Errico et al.) | S-0804 | MCP | adversary type | implicit | yes (3) | no | yes | no | position |
| TM-087 | Enterprise-grade security for MCP (Narajala & Habler) | S-0810 | MCP | control pattern | implicit | partial | no | yes | no | practitioner |
| TM-088 | MCP specification: Security Best Practices | S-0829 | MCP | attack + preconditions | implicit | yes (preconditions) | no | yes (normative) | no | normative |
| TM-089 | OWASP MCP Top 10 (beta) | S-0898 | MCP | risk | no | no | MCP01..10 | partial | no | community |
| TM-090 | MAESTRO applied to a network-monitoring agent (Zambare et al.) | S-0766 | agent | MAESTRO layer | implicit | yes | no | yes | no | 2 demonstrated threats |
| TM-091 | AgentHeLLM: A2A threats in safety-critical LLM assistants (automotive) | S-0778 | agent (automotive) | asset vs attack path graph | yes (human-centric) | yes | no | partial | formal | in-vehicle case |
| TM-092 | Open challenges in multi-agent security | S-0706 | multi-agent | interaction threat | no | partial | no | no | no | position |
| TM-093 | Multi-Agent Risks from Advanced AI (Cooperative AI Foundation) | S-0756 | multi-agent | failure mode x risk factor | no | incentive-based | no | partial | no | examples |
| TM-094 | AAGATE: NIST AI RMF-aligned agentic governance platform | S-0795 | agent | RMF function | implicit | no | via frameworks | yes | platform | prototype |
| TM-095 | The Promptware Kill Chain (Brodt, Feldman, Schneier, Nassi) | S-0821 | LLM+agent | kill-chain stage | no | yes | stage names | yes (per stage) | no | 36 cases |
| TM-096 | Authenticated delegation and authorized AI agents (South et al.) | S-0818 | agent identity | delegation chain | yes | yes | no | yes | no | proposal |
| TM-097 | OpenID Foundation: identity management for agentic AI | S-0819 | agent identity | access pattern | implicit | partial | no | yes | no | standards body |
| TM-098 | CSA Agentic AI Red Teaming Guide | S-0802 | agent | test category | ? | ? | ? | partial | no | community |
| TM-099 | RAND: Securing AI Model Weights | S-0793 | model weights | attacker tier x vector | yes (weights) | yes (OC1-OC5) | vector list | yes (SL1-SL5) | tables | expert estimation |
| TM-100 | Anthropic Responsible Scaling Policy v2.2 (ASL-3 security standard) | S-0798 | frontier model | attacker group | yes (weights) | yes | no | yes | no | policy |
| TM-101 | Google DeepMind Frontier Safety Framework v3.0 | S-0805 | frontier model | capability level | yes (weights) | via RAND | CCL names | yes | no | policy |
| TM-102 | EU GPAI Code of Practice: Safety and Security chapter | S-0851 | frontier model | commitment | yes | yes | measure ids | yes | no | regulatory |
| TM-103 | NIST AI 800-1 (2nd draft): managing misuse risk for dual-use foundation models | S-0811 | foundation model | objective / practice | yes | yes (threat profiles) | practice ids | yes | no | government draft |
| TM-104 | Google DeepMind: An approach to technical AGI safety and security | S-0763 | frontier model | risk area | implicit | yes | no | yes | no | position |
| TM-105 | Shanghai AI Lab frontier risk framework in practice (SafeWork-F1) | S-0764 | frontier model | environment x threat source x capability | implicit | yes | zone ids | yes | no | model evaluations |
| TM-106 | International AI Safety Report 2026 | S-0768 | general-purpose AI | risk area | no | implicit | no | partial | no | evidence synthesis |
| TM-107 | The Malicious Use of AI (Brundage et al.) | S-0726 | AI-enabled offense | security domain | no | yes | no | partial | no | forecast (now partly realized) |
| TM-108 | Generative LMs and automated influence operations (Goldstein et al.) | S-0734 | AI-enabled offense | pipeline stage | no | yes | no | yes | no | analysis |
| TM-109 | The threat of offensive AI to organizations (Mirsky et al.) | S-0689 | AI-enabled offense | kill-chain phase | no | yes | no | partial | no | survey |
| TM-110 | Framework for evaluating emerging cyberattack capabilities of AI (Google DeepMind) | S-0817 | AI-enabled offense | attack-chain phase | no | yes | no | yes | no | 12,000 instances |
| TM-111 | ENISA-JRC: AI in autonomous driving | S-0730 | automotive | function | implicit | ? | no | yes | no | report |
| TM-112 | ISO/SAE 21434 TARA + STPA-Sec for AV perception (Ghosh et al.) | S-0733 | automotive | TARA asset / control loop | yes | yes | no | partial | no | analysis |
| TM-113 | AI-enhanced TARA for connected and autonomous vehicles | S-0365 | automotive | ? | ? | ? | ? | ? | ? | not read |
| TM-114 | CISA et al.: Principles for the secure integration of AI in OT | S-0848 | OT | principle | implicit | no | no | yes | no | government |
| TM-115 | TC260 AI Safety Governance Framework 1.0 (and CAC 2.0, 2025) | S-0794 | AI (PRC) | inherent vs application | implicit | no | no | yes | no | government |
| TM-116 | AI System Threat Vector Taxonomy (Huwyler) | S-0409 | AI | threat domain x loss | implicit | no | 53 ids | no | no | single author |
| TM-117 | STRIDE GPT | S-0967 | generic + LLM/agent | STRIDE | from input | no | OWASP ids | yes | yes | none published |
| TM-118 | AegisShield | S-0960 | generic | STRIDE x ATT&CK | from input | no | ATT&CK | yes | tool | 243 expert threats |
| TM-119 | ThreMoLIA | S-0765 | LLM app | retrieval of prior models | from repo | no | no | no | tool | early |
| TM-120 | LLMs' suitability for STRIDE classification (5G case) | S-0362 | generic | STRIDE label | no | no | no | no | no | 5 LLMs |
| TM-121 | ATLAS-aligned executable assessment rules (Huang, Halak, Kang) | S-0823 | ML+GenAI | evidence -> control -> technique | implicit | via ATLAS | ATLAS ids (pinned) | yes | described, not retrieved | formally verified |
| TM-122 | Continuous threat modeling for AI-driven development (talk) | S-1077 | generic | diff | from code | no | no | no | ? | talk |
| TM-123 | MCPThreatHive | S-0964 | MCP | KG | implicit | no | MCP-38 | partial | claimed | prototype |

| TM-124 | OpenAI Preparedness Framework v2 | S-0814 | frontier model | capability threshold | yes (weights) | ? | category names | yes | no | not read (403) |
| TM-125 | Meta Frontier AI Framework | S-1179 | frontier model | outcome x threat scenario | implicit | yes | no | yes | no | announcement only |
| TM-126 | AWS Generative AI Security Scoping Matrix | S-1178 | GenAI workload | ownership scope (1-5) x discipline | implicit | no | scope ids | partial | no | vendor guidance |
| TM-127 | NSA AISC et al.: Deploying AI Systems Securely | S-1180 | deployed AI system | deployment lifecycle | implicit | no | no | yes | no | government guidance |

127 entries (TM-124 to TM-127 added in the v0.2 review fold; ids are not in group order).
