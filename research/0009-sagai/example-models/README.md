---
schema: "archdoc/v1"
id: RPT-0009-example-models
title: "RPT-0009 example models: AI attacks against the proposed schema"
type: research
status: draft
version: "0.1.0"
date: "2026-10-21"
updated: "2026-10-21"
record: RPT-0009
---

# RPT-0009 example models

Published attacks on AI systems, each written as a tmodel model so that the schema's AI-specific gaps show up. This is the loop the sponsor set for the car-attack models (DL-0013, 2026-10-14): model a documented attack, validate it, note what the schema lacks, and repeat. Here it is applied to the AI threats RPT-0009 maps the SAGAI-related requirements onto (DL-0006).

Evidence, not decisions. The models are written against the **proposal** schema in tmodel#130 (DL-0024), which no ADR has accepted. Every Assertion in them is `proposed`, and none has been reviewed by a human.

| Model | Attack | Sources | Checks |
|---|---|---|---|
| [`em-01-echoleak-m365-copilot.yaml`](em-01-echoleak-m365-copilot.yaml) | EchoLeak: one email makes Microsoft 365 Copilot leak the user's data, with no click (CVE-2025-32711) | arXiv:2509.10540 (the researchers' paper); the CVE record; MITRE ATLAS 2026.09 case study AML.CS0059; CWE 4.20 pages for CWE-74 and CWE-1427. Digests are in the file header | `linkml-validate` (LinkML 1.12.1) against #130's proposal container: no issues. DL-0024's `check-refs.py`: 87 objects and 167 references, all resolve; a planted dangling reference fails it |

## What em-01 models

- **The chain Paul asked for, end to end.** Two weaknesses (CWE-74 as the CNA gave it, CWE-1427 as an AI-proposed better fit), the CVE, twelve MITRE ATLAS techniques, one threat, one damage scenario and five mitigations.
- **The attack steps are ATLAS's own.** AML.CS0059's twelve procedure steps (S00 to S11) become attack steps in ATLAS's order, each with its ATLAS tactic. The paper's one-click variant (the user clicks a reference-style link) is a second path, and the two paths meet at an OR gate.
- **The system side uses #130's classes.**
  - 3 assets: the confidential data, Copilot's prompt context and its rendered answer.
  - 4 trust zones: the internet, Microsoft 365, the tenant's data and the client.
  - 8 data flows, from the attacker's email to the proxied image fetch.

## Gaps the model found

Each gap is a candidate for the schema lane (#64) and the AI record shape (#74), not a proposal accepted here.

| # | Gap | What the model does instead | Candidate | Relates to |
|---|---|---|---|---|
| AI-1 | **No link from an attack step to its attack pattern.** ATLAS names a technique for every step of a case study. | 12 Assertions with predicate `uses_technique`, attributed to MITRE ATLAS | `AttackStep.uses_pattern` (range `AttackPattern`) | DL-0024 P4 (step to weakness) |
| AI-2 | **ATLAS case studies are ordered attack paths.** Each step has a `step-id`, a tactic and `leads-to`. RPT-0005 G2 says no released format has an ordered attack path; ATLAS was outside RPT-0005's scope (RPT-0014), and its case studies are an exception. Separately, `kill_chain_phase` is a free string, and ATLAS tactics are not a kill chain. | Steps use `precedes`; each tactic is written into `kill_chain_phase` with its id | Pass the G2 exception to RPT-0005; a tactic slot that names its scheme | RPT-0005 G2, ADR-0007 import list |
| AI-3 | **The context mixes trust levels.** The attack works because the attacker's email and the confidential data sit in one model context. Zones are per component (`in_trust_zone`), so the boundary the attack crosses, inside one component's input, cannot be drawn. And `DataFlow.carries` takes only Assets, so the injected instructions cannot be named on the flow that brings them. | The context is an Asset; the email flow carries nothing, with a note | A content or provenance label (origin, trust level) on what a flow carries, not only on components | The paper's "provenance-based access control"; R-018 |
| AI-4 | **No fit grade on a weakness mapping.** The CNA mapped CWE-74, which CWE 4.20 marks DISCOURAGED for mapping; CWE-1427 is a Base entry, ALLOWED, and fits better. | Two Assertions, one by the CNA and one by the AI drafter, using only `confidence` | A fit grade on the mapping edge, as CWE's own `Mapping_Fit` | RPT-0005 G8, G9 and Table 6 |
| AI-5 | **No carrier for an exploitation signal with a value.** CISA-ADP's SSVC decision (Exploitation none, Automatable yes, Technical Impact total) has nowhere to go: `Assertion.object` must be a Node, and there is no value slot. | Written into the party's description | One Assertion kind for signals: source, signal, value, date | RPT-0005 Table 6 ("statement identity and provenance") |
| AI-6 | **No AI component kinds.** `ComponentKind` has `machine_learning_model` but nothing for a retrieval index, an agent, a guardrail classifier or a tool. ATLAS's own terms include RAG databases (AML.T0085.000) and AI agent tools. | `service` and `machine_learning_model` | Kinds for RAG index, AI agent, guardrail and tool | #74 (AI record shape) |
| AI-7 | **No way to say a defense was bypassed.** The XPIA classifier and link redaction were in place and the attack got past both (steps S00 and S08). A Mitigation has a status but no `bypassed_by`. | Written into the components' descriptions | `Mitigation.bypassed_by` (range `AttackStep`), or an Assertion predicate | SACM's "defeated" claims (RPT-0005 §7) |
| P2 | **No external entities** (reconfirms DL-0024 P2). The attacker's mail sender and server are Components outside the product. | Components with no product | The proposal's ExternalEntity | DL-0024 decision 2 |

What worked without change: ATLAS mitigations fit `Mitigation.catalog_ref` (AML.M0033, AML.M0026); ATLAS techniques fit `AttackPattern.catalog_ref`; CNA and ADP attribution fit `Assertion.asserted_by`; and the one-click and zero-click variants fit an OR gate.

## Next

- A second model from a different attack class, such as poisoning or model theft, so that AI-1 to AI-7 are tested on more than one attack.
- The mapping from the ETSI EN 304 223 and CISA AI-in-OT requirements to these threats (RPT-0009), which will cite the mitigations here.
