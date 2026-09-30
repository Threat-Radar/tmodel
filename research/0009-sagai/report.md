---
schema: "archdoc/v1"
id: RPT-0009
title: "SAGAI and related AI-security specifications"
short_title: "SAGAI & AI-security specs"
description: "Requirements and recommendations for securing GenAI systems, from the SAGAI workshop series and the AI-security guidance it connects to (CISA AI-in-OT, ETSI SAI), with applicability + gap analysis for tmodel. Evidence, not decisions."
type: research
category: security
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-30"
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
| SAGAI workshop series | SAGAI'24 papers (4); SAGAI'25 research-challenges output (unconfirmed); SAGAI'26 | _pending_ |
| ETSI SAI requirements | ETSI EN 304 223 V2.1.1; TS 104 216 (conformance); TR 104 128 (guide) | _pending_ |
| CISA AI in OT | CISA et al., *Principles for the Secure Integration of AI in OT* | _pending_ |
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

**Takeaway:** _pending — to be written once the other SAGAI papers are read._

## 3. Requirements: ETSI EN 304 223

13 principles across five lifecycle phases (secure design, development, deployment,
maintenance, end of life); 72 provisions, each naming the stakeholder responsible
(Developer, System Operator, Data Custodian, End-user). Input to DEC-001 and DEC-004.

**Takeaway:** _pending._

## 4. Recommendations: CISA AI in OT

Joint guidance from 9 agencies (Dec 2025): 4 principles in 12 subsections, written as
recommendations ("should", "may") rather than requirements. Input to DEC-004.

**Takeaway:** _pending._

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
- Ingest the seed sources and the ETSI documents as `library/` records (#5 pipeline), then distil EN 304 223 first.
