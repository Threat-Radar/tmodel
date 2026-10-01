---
schema: "archdoc/v1"
id: RPT-0009
title: "SAGAI and related AI-security specifications"
short_title: "SAGAI & AI-security specs"
description: "Requirements and recommendations for securing GenAI systems, from the SAGAI workshop series and the AI-security guidance it connects to (CISA AI-in-OT, ETSI SAI), with applicability + gap analysis for tmodel. Evidence, not decisions."
type: research
category: security
status: draft
version: "0.2.0"
date: "2026-09-28"
updated: "2026-10-01"
authors:
  - role: student
    id: mai-li-mcghee
  - role: research
    id: ai-assisted
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0009-sagai/report.md
library_commit: "see library/ submodule pointer at merge (records not yet ingested)"
informs: [DEC-001, DEC-004, R-018]
open_decisions: [DEC-001, DEC-004]
issue: 13
---

# SAGAI and related AI-security specifications

> **Skeleton. Evidence, not decisions.** Every `DEC-*` it informs is open; nothing
> here selects a design. References are not yet in `library/`; the gathered set is in
> [`sources.md`](sources.md), the axes in [`dimensions.md`](dimensions.md), the query
> log in [`searches.md`](searches.md).

## Why this report

Issue #13 asks for clear, concise requirements from **SAGAI** and its related
specifications, in a form that later feeds testing, requirements validation and the
schema (#15, #17). @nymble confirmed the target on #13 (2026-09-25): SAGAI is the
**IEEE S&P workshop series on securing generative AI**, with two seed sources, the
SAGAI call for papers and CISA's *Principles for the Secure Integration of AI in
Operational Technology*. tmodel both **uses AI** (machine-proposed threats and attack
paths are hypotheses until a human reviews them, ARCH-0001 §2) and **models threats**,
so AI-security requirements bear on it twice: as threats the object model must be
able to express, and as requirements on tmodel's own AI features.

## At a glance

| dimension | load-bearing sources | what tmodel takes |
|---|---|---|
| SAGAI workshop series | SAGAI'24 papers (4); SAGAI'25 research-challenges output (unconfirmed); SAGAI'26 | AI-specific threat types for the object model; treat the model as untrusted in tmodel's own AI features |
| ETSI SAI requirements | ETSI EN 304 223 V2.1.1; TS 104 216 (conformance); TR 104 128 (guide) | _pending_ |
| CISA AI in OT | CISA et al., *Principles for the Secure Integration of AI in OT* | MITRE ATLAS alongside ATT&CK; AI attack vectors in threat models; human-in-the-loop and audit trail |
| Related guidance | NCSC/CISA secure AI development guidelines; UK AI Code of Practice; NIST AI RMF, AI 100-2; MITRE ATLAS; OWASP | _pending_ |

## 1. Target and family map

- **SAGAI'24**, *Security Architectures for GenAI Systems*, May 23 2024: peer-reviewed
  papers, published in the IEEE SPW 2024 proceedings.
- **SAGAI'25**, *Secure Generative AI Agents Workshop*, May 15 2025: invited talks and
  panels, no papers; its stated output is a joint research-challenges document.
- **SAGAI'26**, *Secure Agents for Generative Artificial Intelligence*, May 21 2026:
  program not yet retrieved.
- Not in scope: Fraunhofer IESE's "SAGAI" (*Software Architecture and Generative AI*),
  a different series with the same acronym.

**Takeaway:** _pending._

## 2. SAGAI papers and outputs

Threats and defenses established by the workshop papers. Input to DEC-001.

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

**Takeaway** _(AI-assisted draft; accepted by Mai Li McGhee, 2026-10-01)_: across the SAGAI papers the consistent
message is that **model-level robustness is not enough**. The threat that recurs is
injection through content the system processes (text, images, tool output), and the
defenses that hold up are system-level: mark or separate untrusted input (§2.1), validate
input against an explicit specification (§2.2), least privilege and information-flow
control around the model (§2.5–2.6). For tmodel this suggests (a) the object model needs
AI-specific threat types — indirect prompt injection, filter bypass / misuse, data
poisoning — and (b) tmodel's own AI features should treat the model as untrusted.

## 3. Requirements: ETSI EN 304 223

13 principles across five lifecycle phases (secure design, development, deployment,
maintenance, end of life); 72 provisions, each naming the stakeholder responsible
(Developer, System Operator, Data Custodian, End-user). Input to DEC-001 and DEC-004.

**Takeaway:** _pending._

## 4. Recommendations: CISA AI in OT

Joint guidance from 9 agencies (Dec 2025): 4 principles in 12 subsections, written as
recommendations ("should", "may") rather than requirements. Input to DEC-004.

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

**Takeaway** _(AI-assisted draft; accepted by Mai Li McGhee, 2026-10-01)_: the recommendations most relevant to
tmodel are the threat-modeling ones — ATLAS alongside ATT&CK (§3.2) and AI-specific attack
vectors in threat models (§4.1) — and the oversight ones (human in the loop, audit trail of
AI inputs and outputs, §4.1), which match ARCH-0001 §7 and R-018.

## 5. Related guidance

_Pending._ Documents cited by the seeds; which carry requirements worth distilling and
which are stubs. Overlaps: MITRE ATLAS with #9, agent threats with #12, SBOM guidance
with #8.

**Takeaway:** _pending._

## 6. Synthesis

_Pending._ What the evidence implies, to be ratified by ADRs, not here.

## 7. Gap analysis — tmodel vs. AI-security requirements

| capability | requirement / state of the art | tmodel status | recommendation → routing |
|---|---|---|---|
| Human oversight of AI output | _to assess_ | _to assess_ | _to assess_ |
| Audit trail of models and prompts | _to assess_ | _to assess_ | _to assess_ |
| AI threat types in the object model | _to assess_ | _to assess_ | _to assess_ |
| Handling adversarial and untrusted input | _to assess_ | _to assess_ | _to assess_ |
| AI supply chain (models, providers) | _to assess_ | _to assess_ | _to assess_ |

## 8. Open questions / next

- Is arXiv 2512.01295 the SAGAI'25 research-challenges document? Ask @nymble.
- Retrieve the SAGAI'26 program.
- Snowball: Barrett et al., *Identifying and Mitigating the Security Risks of Generative
  AI* (July 2023 workshop, cited by §2.7); ETSI TR 104 048 *Data Supply Chain Security*
  (cited by CISA §3.4).
- Ingest the seed sources and the ETSI documents as `library/` records (#5 pipeline), then distil EN 304 223 first.
