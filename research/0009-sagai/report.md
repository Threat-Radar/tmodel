---
schema: "archdoc/v1"
id: RPT-0009
title: "SAGAI and related AI-security specifications"
short_title: "SAGAI & AI-security specs"
description: "Which AI attacks the leading AI-security requirements defend against (ETSI EN 304 223, CISA AI-in-OT), what the SAGAI research adds, and what tmodel must represent to model such attacks; mapped to NIST AI 100-2 E2025 classes and MITRE ATLAS, and tested on one real attack (EchoLeak). Evidence, not decisions."
type: research
category: security
status: draft
version: "0.3.0"
date: "2026-09-28"
updated: "2026-10-22"
authors:
  - role: student
    id: Maimcghee
  - role: research
    id: ai-assisted
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0009-sagai/report.md
library_commit: "pending (library#32, unmerged: etsi-en-304-223 and cisa-ai-in-ot-principles FX-1 with threat mappings)"
informs: [DEC-001a, DEC-001b, DEC-008, R-018]
open_decisions: [DEC-001b, DEC-008]
issue: 39
---

# RPT-0009: SAGAI and related AI-security specifications

**Status: draft 0.3.0.** Done: the SAGAI papers (§2); full extractions of ETSI EN 304 223 and of CISA's AI-in-OT principles, with every entry mapped to AI attack classes (library#32); and one worked example, EchoLeak (§5). Not yet done: a human technical review, the adversarial review and the clarity pass. Related guidance (§6) is listed, not extracted. This report accepts nothing; each recommendation routes to an open `DEC-*`, an accepted ADR's follow-up work, or an issue.

**Abstract.** Which AI attacks do the leading AI-security requirements defend against, and what must tmodel represent to model those attacks? This report maps the 73 entries of ETSI EN 304 223 and the 136 of CISA's *Principles for the Secure Integration of AI in OT* onto NIST AI 100-2 E2025's attack classes and MITRE ATLAS techniques. It reads the SAGAI workshop papers for the threats and defenses research has established, and tests both on one documented attack, EchoLeak (CVE-2025-32711). The requirements cover poisoning, privacy, supply chain and conventional cyber security, but they reach prompt injection only by inference: each document names it once. Neither mentions retrieval, output rendering or exfiltration, which is the path EchoLeak took. The SAGAI papers propose the defenses the standards lack. To model attacks like EchoLeak, tmodel's schema needs seven additions (G1 to G7).

## Why this report

#39 part B (which replaces #13) asks for clear, concise requirements from **SAGAI** and its related specifications, in a form that feeds testing, requirements validation and the schema. @nymble confirmed the target on #13 (2026-09-25): SAGAI is the **IEEE S&P workshop series on securing generative AI**, with two seed sources, the SAGAI call for papers and CISA's *Principles for the Secure Integration of AI in Operational Technology*.

**Direction since then (2026-10-21, relayed by the student after a meeting with the sponsor; DL-0006):** focus on threats, vulnerabilities and weaknesses, specifically AI ones; build example models of published attacks that shape the schema (#64), as for the car attacks (RPT-0005 G13); and integrate this part into that work instead of pausing it. That is why the report is organized around one question: which attack does each requirement defend against?

tmodel both **uses AI** (machine-proposed threats are hypotheses until a human reviews them, ARCH-0001 §2) and **models threats**. AI-security requirements therefore bear on it twice: as attacks the object model must express (§5, §8), and as requirements on tmodel's own AI features (§7).

## Comparison

### Table 1. The documents compared

| Document | Steward | Kind | Entries extracted | Normative strength | Library record |
|---|---|---|---|---|---|
| ETSI EN 304 223 V2.1.1 (2025-12), *Baseline Cyber Security Requirements for AI Models and Systems* | ETSI TC SAI | European Standard | 73: 72 provisions plus one clause 4 statement | 49 *shall*, 24 *should* | `etsi-en-304-223`, FX-1 (library#32) |
| *Principles for the Secure Integration of Artificial Intelligence in Operational Technology* (2025-12-03; PDF 508cV2, revised 2026-01) | CISA with partner agencies | joint guidance | 136 | 104 recommendations, 10 permissions, 6 considerations, 5 principles, 3 requirements (*must*), 1 prohibition, 7 other | `cisa-ai-in-ot-principles`, FX-1 (library#32) |
| SAGAI'24 papers (4), SAGAI'25 position papers (2), one related workshop report | IEEE S&P workshops; authors | research papers | threats and defenses (§2) | none | 5 records `summarized` (library#7); §2.6 and §2.7 have none |

### Table 2. Which attack classes the requirements defend against

The number of entries mapped to each NIST AI 100-2 E2025 class (one entry can map to several). "Stated" means the document itself names the attack; otherwise the mapping is our reading (`inferred`), with its reason recorded in the library record. The last column shows where the class appears in the EchoLeak model (§5).

| Attack class | ETSI entries (stated) | CISA entries (stated) | SAGAI papers | EchoLeak steps |
|---|---|---|---|---|
| Evasion | 1 (1) | 4 (1) | §2.4 | — |
| Poisoning | 10 (5) | 7 (2) | §2.4 | S05 (RAG poisoning) |
| Privacy | 5 (2) | 7 (2) | §2.4 | S07, S10 (data leakage) |
| Direct prompt injection | 5 (0) | 4 (0) | §2.2, §2.3 | — |
| Indirect prompt injection | 2 (0) | 4 (0) | §2.1, §2.5, §2.6 | S03 to S06 |
| Supply chain | 8 (0) | 6 (0) | — | — |
| Availability | 1 (0) | 0 | — | — |
| Misuse | 0 | 0 | §2.3 | — |
| Conventional cyber security (outside NIST's taxonomy) | 7 (1) | 16 (4) | — | S02, S10 |
| Not an attack (drift, explainability, skills) | 5 (3) | 18 (8) | — | — |
| An attack, but no single class | 1 (1) | 5 (4) | — | — |
| No attack mapped (governance and process) | 38 | 79 | — | — |

Read across the rows:
- **Prompt injection is reached only by inference.** ETSI names "indirect prompt injection" once, in its Introduction's list of AI-specific risks (p. 5), and CISA names "prompt injection" once, in Table 2. None of the 10 entries mapped to a prompt-injection class (5 in each document) names the attack itself.
- **Supply chain is covered, but never by name as an attack.** ETSI's Principle 7 (secure the supply chain) and CISA §2.3 (vendor transparency, including an SBOM that covers AI) are mapped to supply-chain attacks by us, not by the documents.
- **Most of CISA is about AI's operational risks, not attacks.** 18 entries concern drift, explainability, operator load or skills, and 16 concern conventional cyber security around the AI.
- **About half of each document maps to no attack**: governance, documentation and process duties.

## 1. Target and family map

- **SAGAI'24**, *Security Architectures for GenAI Systems*, May 23 2024: peer-reviewed
  papers, published in the IEEE SPW 2024 proceedings.
- **SAGAI'25**, *Secure Generative AI Agents Workshop*, May 15 2025: invited talks and
  panels, no papers; its stated output is a joint research-challenges document.
- **SAGAI'26**, *Secure Agents for Generative Artificial Intelligence*, May 21 2026:
  program not yet retrieved.
- Not in scope: Fraunhofer IESE's "SAGAI" (*Software Architecture and Generative AI*),
  a different series with the same acronym.

**Takeaway:** SAGAI is a research venue, not a standard: it supplies threats and system-level defenses (§2), while the requirements a product can be held to come from ETSI and CISA (§3, §4). The SAGAI'24 papers and the SAGAI'25 position papers are the research input; ETSI EN 304 223 and CISA's AI-in-OT principles are the requirements this report maps.


## 2. SAGAI papers and outputs

Threats and defenses established by the workshop papers, each placed in NIST AI 100-2 E2025's classes. The papers have library records (`summarized`, library#7) except §2.6 and §2.7.

| Paper | Attack class it addresses (NIST AI 100-2 E2025) | Defense level |
|---|---|---|
| §2.1 Spotlighting | indirect prompt injection | system (input transformation) |
| §2.2 Image-based prompt attacks | prompt injection through images (multimodal) | system (specification checks) |
| §2.3 Programmatic behavior of LLMs | direct prompt injection used for misuse (jailbreaks) | argues for system level (sandboxing, isolation) |
| §2.4 Pre-trained encoders | poisoning (including backdoors), evasion, privacy | model (certified training) |
| §2.5, §2.6 Agentic systems security | indirect prompt injection leading to exfiltration or command execution | system (least privilege, information-flow control, separation) |
| §2.7 Policy and technology | not one attack class: regulation against capability | policy |

### 2.1 Spotlighting (Hines et al., SAGAI'24, arXiv 2403.14720)

- **Threat — indirect prompt injection (XPIA).** An LLM receives instructions and
  untrusted data as one undifferentiated stream of text, so it cannot tell "code" from
  "data". An attacker plants instructions in content the LLM will later process (a web
  page, an email, a document); the user is the victim, and the attacker's instructions
  run in the user's session (§1, §2.2).
- **Defense — spotlighting.** Transform the untrusted input so its origin stays visible
  to the model, and tell the model in the system prompt never to follow instructions
  inside it (§3). Three variants: *delimiting* (markers around the input), *datamarking*
  (a special token interleaved throughout the input), *encoding* (e.g. base64).
- **Where it sits.** System level, around a black-box model: no retraining, only an
  input transformation plus system-prompt instructions (§1, §3.1).
- **Results.** Attack success fell from over 50% to under 2% with little effect on task
  performance (abstract). Delimiting roughly halved attacks; datamarking cut them to
  about 3% or less; encoding reached about 0%, but only high-capacity models (GPT-4)
  kept task performance with encoded input (§5.1–5.2).
- **Recommendations (§5.3–5.4, §8.2):**
  - Do not rely on delimiting alone; an attacker who learns the delimiters can forge them.
  - Use at least datamarking; with high-capacity models, use encoding, and validate task
    performance per use case.
  - Assume the system prompt has leaked; randomize the marking token per request.
  - Use a one-way encoding the attacker cannot exploit (base64, not ROT13).
  - Few-shot "don't fall for this" examples help but should not be relied on; they only
    cover known attacks.
- **Limits stated by the authors.** Why spotlighting works is not understood; it is not
  perfectly secure — a real fix would carry instructions and data in separate channels,
  which current LLM architectures do not support (§6). Evaluated on 2023 GPT models with
  a simple keyword-payload attack (§4).

### 2.2 Image-based prompt attacks (Sharma, Gupta, Grossman, SAGAI'24)

- **Threat.** Prompt injection carried in an *image* sent to a multimodal chatbot (text
  written on, hidden in, or blended into the picture); text-only defenses do not see it
  (§I-A, §II).
- **Defense — two stages driven by developer-written specifications** in SPML, a small
  language for chatbot definitions (§I-B, Fig. 1):
  1. *Input validation* (§III): the developer states what images the chatbot expects
     (e.g. "a clear parking sign"); a model describes the incoming image in the same
     terms, and any conflict with the specification rejects the image.
  2. *Prompt-injection detection* (§IV): a model reads the image as if it were an
     instruction to the chatbot; if the chatbot specification it implies differs from the
     real one (e.g. a new name), the interaction is dropped.
- **Where it sits.** System level: checks run before and around the chatbot's model, no
  retraining (§I-B).
- **Results** (small case study: 7 attack images, 3 models; §VI): detection of malicious
  images was 100% with GPT-4-Vision, 42.8% with LLaVA-13B, 0% with MiniGPT-4; every image
  that actually succeeded against a model was detected. The checker model should be as
  capable as the chatbot's own model (§VI).
- **Limits stated by the authors.** The checker is itself a multimodal model and can be
  manipulated by the same input (§VII).

### 2.3 Exploiting programmatic behavior of LLMs (Kang et al., SAGAI'24)

- **Threat — misuse (dual use).** The attacker is the user, trying to get a hosted LLM to
  write scams, phishing or hate speech past the provider's filters (§3.1).
- **Key idea.** Instruction-following LLMs behave like programs (string concatenation,
  variable assignment, sequential steps, branching), so classic program attacks carry
  over: obfuscation (typos, synonyms), code injection / payload splitting, and
  virtualization (a fictional scenario built over several prompts) (§2, §3.3–3.4).
- **Results.** Obfuscation and virtualization bypassed OpenAI's input filter, output filter
  and refusal behavior in 100% of the tested scenarios (Table 1, §4); generated scams were
  rated highly convincing and cost about $0.0064–$0.016 each, below human cost (§5–6).
- **Implication stated by the authors.** Input filtering is fundamentally limited — what a
  complex prompt does can only be known by running it — so defenses should draw on
  traditional security such as sandboxing and isolation (§3.5, §8).
- **Limits.** Tested on early-2023 OpenAI models; OpenAI has since patched the specific
  prompts, though modified versions still worked (§1, Responsible Disclosure).

### 2.4 Pre-trained encoders improve secure and private learning (Liu et al., SAGAI'24)

- **Topic.** Model-level, not system-level: image *classifiers*, not GenAI applications.
- **Threats covered.** Training-time and model attacks: data poisoning, backdoors,
  adversarial examples, and privacy attacks (membership inference, model inversion), plus
  the right to be forgotten (§1, §3).
- **Finding.** Building on a clean encoder pre-trained on public data (OpenAI's CLIP)
  makes provable ("certified") defenses both more accurate and stronger. Example (STL10):
  bagging accuracy 0.352 → 0.979 and certified poisoning size 1.3 → 68.8; differentially
  private accuracy 0.237 → 0.956 (§1).
- **Limits.** Assumes the encoder itself is clean; attacks on the encoder are out of
  scope (§3, §9).

### 2.5 Systems security foundations for agentic computing (Christodorescu et al.; probable SAGAI'25 output)

Written by the SAGAI'25 organizers and a SAGAI'25 panelist; the paper itself does not name
the workshop (see §8). Read version: arXiv 2512.01295v2, Feb 2026.

- **Position.** Agent security needs the systems-security view of the whole system, not
  only a more robust model (§1).
- **Four challenges** when classic security principles meet agents (§2): the trusted
  computing base (TCB) includes a *probabilistic* model; security policy is *dynamic and
  task-specific*; the security boundary is *fuzzy* (no layers between a prompt and a tool
  call); and following new instructions is sometimes a feature, not an attack.
- **Eleven real attacks** (Copilot, Devin, ChatGPT memory, Claude Code, Cursor, …) mapped to
  five violated principles: least privilege, TCB tamper resistance, complete mediation,
  secure information flow, human weak link (§3, Table 1). Nearly all are indirect prompt
  injection leading to data exfiltration or command execution.
- **Current defenses** surveyed in Table 2 (§4), e.g. a tool-call policy language (Progent)
  cut attack success from 41.2% to 2.2%.
- **Open problems** (§5): separating instructions from data; least-privilege access
  control; information-flow control; and, long-term, guarantees from probabilistic
  components. Separation alone "is unlikely to fully solve the prompt injection problem"
  (§5.1).

### 2.6 Agent security is a systems problem (Christodorescu et al., 2026)

Same authors; a shorter position paper building on §2.5.

- **Position.** Treat the model powering an agent as an **untrusted component** and enforce
  security invariants at the system level (abstract, §1).
- **Three mechanisms** (§1, §3): provable separation of instructions and data;
  least-privilege sandboxing with *verifiable* policy generation (natural-language intent
  translated into formal, checkable policy); information-flow control.
- **Against stacking guard models.** Several ML filters are not real defense in depth,
  because they share failure modes; an input that fools the agent likely fools its ML
  monitor too (§4).

### 2.7 Securing the future of GenAI: policy and technology (Christodorescu et al., 2024)

Related, not a SAGAI paper: summarizes an Oct 2023 workshop by the same organizers
(Google, UW-Madison, Stanford).

- **Content.** Compares GenAI regulation (EU AI Act, US Executive Order, China) with what
  technology can deliver; alignment, model inspection and watermarking all have
  limitations (§2–5, §8). Gaps: alignment, liability, watermarking (§6).
- **Link to SAGAI.** Its recommendation to research *out-of-model* guardrails lists the
  same topics as the SAGAI'24 call for papers ("secure sequential and parallel composition
  of GenAI-based systems, layered security for multi-agent systems, security uses of
  watermarked GenAI outputs, and model explainability for security and privacy") (§7).
- **Snowball lead.** Cites the output of an earlier July 2023 workshop: Barrett et al.,
  *Identifying and Mitigating the Security Risks of Generative AI* (ref. [12]).

**Takeaway** _(AI-assisted draft; accepted by @Maimcghee, 2026-10-01)_: across the SAGAI papers the consistent
message is that **model-level robustness is not enough**. The threat that recurs is
injection through content the system processes (text, images, tool output), and the
defenses that hold up are system-level: mark or separate untrusted input (§2.1), validate
input against an explicit specification (§2.2), least privilege and information-flow
control around the model (§2.5–2.6). For tmodel this suggests (a) the object model needs
AI-specific threat types — indirect prompt injection, filter bypass / misuse, data
poisoning — and (b) tmodel's own AI features should treat the model as untrusted.

## 3. Requirements: ETSI EN 304 223

ETSI EN 304 223 V2.1.1 (record `etsi-en-304-223`, FX-1 in library#32) is a European Standard: 13 principles across five lifecycle phases, 72 provisions, each naming the stakeholder responsible. Input to DEC-001b and R-018.

- **Phases.** Secure design 26 entries, development 31, deployment 5, maintenance 8, end of life 2, and one clause 4 statement that spans them.
- **Stakeholders.** Developer 54 (3 of them implied), System Operator 45 (1 implied), Data Custodian 6, End-user 2, Affected entity 1. The accepted schema has no edges for these roles (G8).
- **Testable.** 29 entries are testable as written, 42 partly, 2 not.
- **Markers.** Reconciled over the whole document, with every exclusion listed (shall 61 → 59, should 32 → 29); all are lowercase, so the BCP 14 count is 0.
- **Threats it names.** 14 entries, 13 of them in its own words: data poisoning, poisoned publicly sourced data, model obfuscation, indirect prompt injection, adversarial attacks, model inversion, membership inference, reverse engineering of the model or its data, API abuse, unintended influence through outputs, data drift, unexpected inputs and failure, issues carried between AI instantiations, and unauthorized access to training or test data.
- **Provisions closest to prompt injection** (all mappings ours):
  - 5.1.2-2: "withstand adversarial AI attacks, unexpected inputs and AI system failure";
  - 5.1.2-6: permissions on other systems and data sources "only provided as required for functionality and … risk assessed";
  - 5.2.1-4.1: "checks and sanitisation to data and inputs";
  - 5.2.5-4.1: evaluate model outputs so they "do not provide System Operators or End-users with unintended influence over the system".
- **Human oversight** is its own principle (5.1.4-1 to 5.1.4-3), close to ARCH-0001 §7's Review.
- **One gap in the source:** it names "model obfuscation" as a risk but never defines it (open question 1).

**Takeaway:** ETSI is the stronger requirements document: 49 *shall*s, a stakeholder for each, and 29 testable as written. Its threat coverage is strongest for poisoning and the model's data, and generic for prompt injection: 5.1.2-2 asks for robustness without saying against what.

## 4. Recommendations: CISA AI in OT

CISA's joint guidance (record `cisa-ai-in-ot-principles`, FX-1 in library#32) has 4 principles in 13 numbered subsections. It is written as recommendations: 104 of its 136 entries, against 3 requirements (*must*). Nearly every entry is addressed to the critical-infrastructure owner or operator (111 entries, 4 implied). 57 entries are testable as written, 49 partly, 30 not. It names 32 threats, mostly operational: drift, explainability, cognitive load, dependency, skills, interoperability, latency. Input to R-018 and DEC-001b.

- **Principle 1 — Understand AI.** Table 2 lists AI risks in OT: cybersecurity (including
  prompt injection), data quality, model drift, lack of explainability, operator cognitive
  load, compliance (audit trails), over-dependence, interoperability, complexity,
  reliability; LLMs "almost certainly should not be used to make safety decisions for OT
  environments" (§1.1). Follow the secure AI lifecycle of the NCSC/CISA guidelines (§1.2);
  train staff to validate AI output and keep manual skills (§1.3).
- **Principle 2 — Consider AI use in the OT domain.** First assess whether AI is the right
  tool at all (§2.1); protect and control OT data, and do not share sensitive data with
  externally hosted models (§2.2); require vendor transparency, including an SBOM that
  covers AI, notice if the AI can give improper advice, and the ability to disable AI
  features (§2.3); prefer push-based architectures, keep a failsafe fallback to manual
  operation, and limit AI control without a human in the loop (§2.4).
- **Principle 3 — Governance and assurance.** Clear roles and regular audits (§3.1);
  integrate AI into existing security frameworks, log AI endpoints, inspect prompts and
  outputs, and add **MITRE ATLAS** techniques alongside ATT&CK when modeling threats (§3.2);
  test on non-production infrastructure first (§3.3); names ETSI TR 104 128, TS 104 223 and
  TR 104 048 as the top AI technical standards (§3.4).
- **Principle 4 — Oversight and failsafes.** Inventory AI components; log inputs and
  outputs with an audit trail where the AI's identity is distinct from users and machines;
  human-in-the-loop decision-making; anomaly detection; AI red teaming; and "regularly
  update threat models with AI-specific attack vectors (such as adversarial inputs or data
  poisoning)" (§4.1). Add AI failure states to safety and incident-response plans (§4.2).

- **What it adds for attacks** (all mappings ours):
  - R-0101 and R-0114: log and monitor AI inputs and outputs, with an audit trail.
  - R-0109: log AI decisions so the AI's identity is distinct from users' and machines'.
  - R-0084: flow and access logs for AI endpoints; "track data egress by asset and identity".
  - R-0085: "data loss prevention for prompts and output inspection".
  - R-0120: "regularly update threat models with AI-specific attack vectors".

**Takeaway** (unchanged in substance from 0.2.0, accepted by @Maimcghee on 2026-10-01): the recommendations most relevant to tmodel are the threat-modeling ones, ATLAS alongside ATT&CK (§3.2) and AI-specific attack vectors in threat models (R-0120), and the oversight ones: human in the loop, and an audit trail of AI inputs and outputs (§4.1). Both match ARCH-0001 §7 and R-018. New in 0.3.0: CISA is also the only one of the two documents that names the output side, through egress tracking and output inspection.

## 5. Worked example: EchoLeak against the requirements

EchoLeak (CVE-2025-32711) is a zero-click prompt injection in Microsoft 365 Copilot. One email carried hidden instructions; when the user later asked Copilot an ordinary question, retrieval pulled the email into the model's context. Copilot then put the user's data into a reference-style image link, which the client fetched through an allow-listed Teams service to the attacker's server. The example model is [`example-models/em-01-echoleak-m365-copilot.yaml`](example-models/em-01-echoleak-m365-copilot.yaml). It follows MITRE ATLAS case study AML.CS0059 step by step and is checked against the researchers' paper (arXiv:2509.10540) and the CVE record.

**Table 3** places each stage of the attack against the nearest provisions, and says how far they reach. Its links were made by matching ids at ATLAS's parent-technique level, then reading the provision. Like the rest of the model, it is AI-drafted and unreviewed.

| EchoLeak stage (ATLAS steps) | Nearest provisions | How far they reach |
|---|---|---|
| Injection through a retrieved email (S03 to S06: AML.T0093, T0070, T0051.002) | ETSI 5.1.2-2 (withstand adversarial attacks and unexpected inputs), 5.2.1-4.1 (checks and sanitisation of inputs); CISA R-0011 (consider Table 2's risks), R-0120 (update threat models) | **General.** Robustness and input checks, with nothing on content that arrives through retrieval |
| Collecting data from the user's scope (S07: AML.T0085.000) | ETSI 5.1.2-6 (permissions only as required), 5.2.1-4 (protect sensitive data) | **Partial.** Least privilege applies, but Copilot acted with the user's own, delegated access |
| Hiding the data in the answer (S08, S09: AML.T0067, T0077) | ETSI 5.2.5-4.1 (evaluate outputs for unintended influence); CISA R-0085 (output inspection, data loss prevention) | **Partial.** Inspection of what the output says, not of how the client renders it |
| Sending it out through an allow-listed service (S10: AML.T0025) | CISA R-0084 (track data egress), R-0116 (egress controls) | **Detection.** Egress is tracked, but the request went to an allowed domain |
| After the fact | ETSI 5.4.2-1 and 5.4.2-2 (log and analyse); CISA R-0101, R-0109, R-0114 (log inputs and outputs, distinct AI identity) | **Forensics.** These would show what happened, not stop it |
| Human oversight | ETSI 5.1.4-1 to 5.1.4-3; CISA R-0068, R-0104 | **Not triggered.** A zero-click attack has no human step |

What the example shows:

1. **The requirements stop short of the output channel.** Neither document mentions retrieval (RAG), output rendering, links or images, content security policies, or exfiltration. Three of the four bypasses EchoLeak chained are on that channel: link redaction, image auto-fetch and the content-security-policy allowlist. The fourth, the injection classifier, falls only under ETSI 5.1.2-2's general robustness duty. The paper's mitigations (filtering every link and image, strict content security policies) have no counterpart in either standard.
2. **The SAGAI research covers that gap.** Spotlighting (§2.1) is one form of the "prompt partitioning" the EchoLeak paper recommends. The agentic-systems papers (§2.5, §2.6) argue for exactly the least-privilege and information-flow controls that would have contained S07 to S10.
3. **Id matching needs the parent technique.** The library records map prompt-injection provisions to ATLAS AML.T0051.000 (direct) and .001 (indirect), while ATLAS classifies EchoLeak as .002 (triggered). A match at the sub-technique level finds nothing; at AML.T0051 it finds the provisions above. Mappings in tmodel therefore need a fit grade and a level (G4).

## 6. Related guidance

The documents the seeds cite are listed in [sources.md](sources.md). Two are used here as reference schemes without being extracted:
- **NIST AI 100-2 E2025** (*Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*) supplies the attack classes and the `NISTAML.*` ids.
- **MITRE ATLAS 2026.09** supplies the technique ids and the EchoLeak case study.

Neither has a library record, so their ids resolve only to a citation (open question 6). The NCSC/CISA secure-AI guidelines, the UK AI Code of Practice, ETSI TR 104 128, TS 104 216 and TR 104 048 are cited inside the two extracted records, but have no record of their own. Overlaps: ATLAS with RPT-0014 (#71), agent threats with RPT-0008 (#12), and the AI bill of materials with RPT-0004 (#38).

## 7. Synthesis

- **The standards and the research meet at different layers.** ETSI and CISA set duties: robustness, least privilege, logging, human oversight, supplier transparency. The SAGAI papers explain why model-level robustness fails against prompt injection, and propose system-level defenses: separating instructions from data, least privilege, information-flow control. A threat model needs both, the duty as a requirement and the defense as a mitigation.
- **Prompt injection is the weakest link between the two.** It is the attack the SAGAI papers and nearly every agent incident in §2.5 are about, yet both standards name it once and no provision addresses it in words. EchoLeak's path, through retrieval and through the output channel, is outside both documents.
- **Zero-click attacks defeat the human-oversight provisions by design.** Those provisions match ARCH-0001 §7 and R-018 for decisions a human makes. They do not engage when no human step exists, so tmodel should model when a review can happen, not only whether one is required.
- **For tmodel's own AI features**, the provisions that apply most directly are human oversight (ETSI 5.1.4), logging of AI inputs, outputs and identity (ETSI 5.4.2-1; CISA R-0101, R-0109, R-0114), and treating the model as untrusted (§2.6). These already align with R-018; the gap is in implementation, not in the requirements (#17, #19).

## 8. Gap analysis: what tmodel needs to model AI attacks

Each row is evidence for the decision or issue it routes to; none is a decision. G1 to G7 come from the EchoLeak model ([example-models/README.md](example-models/README.md), AI-1 to AI-7), and G8 to G12 from the two extractions.

| # | Finding | Evidence | Routes to |
|---|---|---|---|
| G1 | No link from an attack step to its attack pattern. ATLAS gives a technique for every step, and em-01 carries its twelve as Assertions. | em-01; AI-1 | #64 (ADR-0010 amendment), DL-0024 P4 |
| G2 | ATLAS case studies are ordered attack paths (`step-id`, tactic, `leads-to`), an exception to RPT-0005 G2. The free-string `kill_chain_phase` cannot say which scheme a tactic belongs to. | ATLAS 2026.09 data; AI-2 | RPT-0005 G2 (exception), #74 |
| G3 | An LLM's context mixes trusted and untrusted content. Per-component trust zones cannot draw the boundary the attack crosses, and a data flow can carry only Assets. | §5; AI-3 | #64, #74, R-018 |
| G4 | A weakness or technique mapping has no fit grade or level. The CNA mapped CWE-74, which CWE 4.20 marks DISCOURAGED, while CWE-1427 fits better; and id joins need the parent ATLAS technique. | §5 item 3; AI-4 | DEC-008, #64 (RPT-0005 G8, G9) |
| G5 | An exploitation signal with a value (CISA-ADP's SSVC decision) has no carrier. | em-01; AI-5 | #64 (RPT-0005 Table 6) |
| G6 | No component kinds for AI parts: retrieval index, agent, guardrail classifier, tool. | em-01; AI-6 | #74, #130 |
| G7 | A defense that was in place but bypassed cannot be recorded. | em-01 (the XPIA classifier, link redaction); AI-7 | #64 |
| G8 | ETSI's stakeholder roles (Developer, System Operator, Data Custodian, End-user) have no edges in the accepted core. | §3; library#32 question 3 | DEC-001a amendment (#64) |
| G9 | `catalog_ref` is single-valued, so one attack cannot carry a NIST class and several ATLAS ids. | library#32 question 3 | #64 |
| G10 | Training data and model weights could be an Asset, a Component, or both. | library#32 question 2; em-01 | #130 decision 2 |
| G11 | Neither standard covers the output channel (rendering, links, content security policies). The defenses come from research (§2) and the EchoLeak paper. | §5 item 1 | #74 (record shape for mitigations from research) |
| G12 | NIST AI 100-2 E2025 and ATLAS have no library records, so their ids resolve to no record. | §6 | library issue (open question 6) |

## 9. Open questions for the sponsor

1. ETSI names "model obfuscation" as a risk but never defines it. How should it be read?
2. Are training data and model weights an Asset, a Component, or both (G10, #130)?
3. Should the core gain stakeholder roles (G8) and multi-valued catalog references (G9)?
4. Do safety and reliability risks (drift, hallucination) count as threats in tmodel? Should attacks that use AI as a tool be modeled?
5. Should the candidate CWE ids for AI weaknesses be adopted, and mappings derived from ATLAS's mitigation links?
6. Should NIST AI 100-2 E2025 and ATLAS get library records (G12)?
7. Is arXiv 2512.01295 the SAGAI'25 research-challenges document (§2.5)?

Questions 1 to 6 are also in library#32.

## 10. Method and limits

**Method.**
- **Library records.** ETSI EN 304 223 and CISA's AI-in-OT principles were extracted to FX-1 in the library (library#32) in three passes: extract, then verify by independent agents against the source PDFs, then a threat-mapping review. About 4 hours of work and 1.9M tokens.
- **Mapping.** Every entry was mapped to NIST AI 100-2 E2025 classes and MITRE ATLAS 2026.09 techniques, each mapping marked `stated` or `inferred`.
- **Independent check.** A separate session re-checked the final records:
  - every ATLAS id exists in ATLAS 2026.09, and all 38 id-and-name pairs match;
  - every NIST id and name appears in NIST AI 100-2 E2025's index;
  - all 44 threats marked `stated` quote their source verbatim;
  - the PDFs' digests match the records.
- **Worked example.** em-01 was built from the EchoLeak paper, the CVE record and ATLAS case study AML.CS0059, and validated against the #130 proposal schema (LinkML 1.12.1; 167 references resolve).
- **SAGAI papers.** §2 is unchanged from 0.2.0, apart from the class table.

**Limits.**
- The mappings are AI-produced, and most are `inferred`: 56 of ETSI's 81 and 81 of CISA's 122.
- Table 3's reach judgments are AI-drafted and unreviewed.
- The student's review is for clarity, not technical correctness (DL-0006).
- em-01 depends on the unaccepted #130 proposal.
- One example cannot show how often the gaps matter; a second model, of a different attack class, is the next step.

**References** are in [sources.md](sources.md), and the library records named above. The library commit is pinned when library#32 merges.
