---
schema: "archdoc/v1"
id: RPT-0009-example-models
title: "RPT-0009 example models: AI attacks against the proposed schema"
type: research
status: draft
version: "0.2.0"
date: "2026-10-21"
updated: "2026-11-09"
record: RPT-0009
---

# RPT-0009 example models

Published attacks on AI systems, each written as a tmodel model so that the schema's AI-specific gaps show up. This is the loop the sponsor set for the car-attack models (DL-0013, 2026-10-14): model a documented attack, validate it, note what the schema lacks, and repeat. Here it is applied to the AI threats RPT-0009 maps the SAGAI-related requirements onto (DL-0006).

Evidence, not decisions. em-01 was written against the **proposal** schema in tmodel#130; its Asset, TrustBoundary and DataFlow classes are now on `main` (ADR-0011), and all three models validate against `main`'s `spec/vectors/example-container-proposed.linkml.yaml`. Every Assertion in them is `proposed`, and none has been reviewed by a human.

| Model | Attack | Sources | Checks (2026-11-09, on `main`) |
|---|---|---|---|
| [`em-01-echoleak-m365-copilot.yaml`](em-01-echoleak-m365-copilot.yaml) | EchoLeak: one email makes Microsoft 365 Copilot leak the user's data, with no click (CVE-2025-32711) | arXiv:2509.10540 (a third-party case study of public material; the finders' disclosure is Aim Labs', `aim-labs-echoleak-disclosure`); the CVE record; MITRE ATLAS 2026.09 case study AML.CS0059; CWE 4.20 pages for CWE-74 and CWE-1427. Digests are in the file header | `linkml-validate` (LinkML 1.12.1): no issues. `design-log/0024-schema-proposal-g13/check-refs.py`: 87 objects and 167 references, all resolve |
| [`em-02-copilot-agent-self-approval.yaml`](em-02-copilot-agent-self-approval.yaml) | Instructions in a project file make GitHub Copilot agent mode in VS Code turn on its own auto-approve setting, then run commands on the developer's machine (CVE-2025-53773) | Embrace The Red write-up, 2025-08-12; the CVE record; CWE pages for CWE-77, CWE-15 and CWE-1427; ATLAS 2026.09 for ids only (no case study exists). Digests are in the file header | `linkml-validate`: no issues. `check-refs.py`: 83 objects and 166 references, all resolve |
| [`em-03-forcedleak-agentforce.yaml`](em-03-forcedleak-agentforce.yaml) | ForcedLeak: a public Web-to-Lead form submission makes Salesforce Agentforce send CRM data out through an expired, still allow-listed domain (no CVE) | Noma Labs write-up, 2025-09-25; CWE pages for CWE-1427 and CWE-942; ATLAS 2026.09 for ids only (no case study exists). Salesforce's help article renders only with JavaScript and was not read. Digests are in the file header | `linkml-validate`: no issues. `check-refs.py`: 71 objects and 130 references, all resolve |

## What em-01 models

- **The chain the sponsor (@nymble) asked for, end to end.** Two weaknesses (CWE-74 as the CNA gave it, CWE-1427 as an AI-proposed better fit), the CVE, twelve MITRE ATLAS techniques, one threat, one damage scenario and five mitigations.
- **The attack steps are ATLAS's own.** AML.CS0059's twelve procedure steps (S00 to S11) become attack steps in ATLAS's order, each with its ATLAS tactic. The paper's one-click variant (the user clicks a reference-style link) is a second path, and the two paths meet at an OR gate.
- **The system side uses #130's classes.**
  - 3 assets: the confidential data, Copilot's prompt context and its rendered answer.
  - 4 trust zones: the internet, Microsoft 365, the tenant's data and the client.
  - 8 data flows, from the attacker's email to the proxied image fetch.

## What em-02 and em-03 add

Both are prompt injection again, as the attack class, but each tests a different part of the model than em-01.

- **em-02 runs code instead of leaking data.** The agent rewrites its own workspace settings so that it stops asking before tool calls ("YOLO mode"), then runs commands.
  - Two threats, two damage scenarios and three paths. The visible and invisible-instruction variants meet at an OR gate. The self-spreading path, which the write-up describes but does not demonstrate, branches after the command runs.
  - Two products: VS Code with Copilot, which the write-up attacks, and Visual Studio 2022 17.14, the only product the CVE record lists (gap AI-9).
  - The CNA's CWE-77, plus two AI-proposed weaknesses: CWE-1427 as the root cause, and CWE-15 for the settings change.
- **em-03 has no CVE.**
  - Its weaknesses, CWE-1427 and CWE-942 (a CSP that includes untrusted domains), enter through `exploits` Assertions, as in pv-02.
  - Its one path has an AND gate: the form is submitted only once the payload is written *and* the expired domain is bought.
  - Its mitigations split between Salesforce (the domain taken back, Trusted URLs Enforcement on 2025-09-08) and the customer (enforcing Trusted URLs in the org, screening fields, auditing leads).
- **Neither attack has an ATLAS case study.** em-01's steps and technique links are ATLAS's own. In em-02 and em-03, the steps come from the write-ups, and each step-to-technique link is attributed to the AI drafter (gap AI-8).

## Gaps the models found

Each gap is a candidate for the schema lane (#64) and the AI record shape (#74), not a proposal accepted here. em-02 and em-03 hit AI-1, AI-3 and AI-6 again, em-02 hits AI-5 and AI-7 again, and both add AI-8 to AI-12.

| # | Gap | What the model does instead | Candidate | Relates to |
|---|---|---|---|---|
| AI-1 | **No link from an attack step to its attack pattern.** ATLAS names a technique for every step of a case study. | 12 Assertions with predicate `uses_technique`, attributed to MITRE ATLAS | `AttackStep.uses_pattern` (range `AttackPattern`) | #130 P4 (step to weakness) |
| AI-2 | **ATLAS case studies are ordered attack paths.** Each step has a `step-id`, a tactic and `leads-to`. RPT-0005 G2 says no released format has an ordered attack path; ATLAS was outside RPT-0005's scope (RPT-0014), and its case studies are an exception. Separately, `kill_chain_phase` is a free string, and ATLAS tactics are not a kill chain. | Steps use `precedes`; each tactic is written into `kill_chain_phase` with its id | Pass the G2 exception to RPT-0005; a tactic slot that names its scheme | RPT-0005 G2, ADR-0007 import list |
| AI-3 | **The context mixes trust levels.** The attack works because the attacker's email and the confidential data sit in one model context. Zones are per component (`in_trust_zone`), so the boundary the attack crosses, inside one component's input, cannot be drawn. And `DataFlow.carries` takes only Assets, so the injected instructions cannot be named on the flow that brings them. | The context is an Asset; the email flow carries nothing, with a note | A content or provenance label (origin, trust level) on what a flow carries, not only on components | The paper's "provenance-based access control"; R-018 |
| AI-4 | **No fit grade on a weakness mapping.** The CNA mapped CWE-74, which CWE 4.20 marks DISCOURAGED for mapping; CWE-1427 is a Base entry, ALLOWED, and fits better. | Two Assertions, one by the CNA and one by the AI drafter, using only `confidence` | A fit grade on the mapping edge, as CWE's own `Mapping_Fit` | RPT-0005 G8, G9 and Table 6 |
| AI-5 | **No carrier for an exploitation signal with a value.** CISA-ADP's SSVC decision (Exploitation none, Automatable yes, Technical Impact total) has nowhere to go: `Assertion.object` must be a Node, and there is no value slot. | Written into the party's description | One Assertion kind for signals: source, signal, value, date | RPT-0005 Table 6 ("statement identity and provenance") |
| AI-6 | **No AI component kinds.** `ComponentKind` has `machine_learning_model` but nothing for a retrieval index, an agent, a guardrail classifier or a tool. ATLAS's own terms include RAG databases (AML.T0085.000) and AI agent tools. | `service` and `machine_learning_model` | Kinds for RAG index, AI agent, guardrail and tool | #74 (AI record shape) |
| AI-7 | **No way to say a defense was bypassed.** The XPIA classifier and link redaction were in place and the attack got past both (steps S00 and S08). A Mitigation has a status but no `bypassed_by`. In em-02 the defense, Copilot's confirmation prompt, is not bypassed but **switched off by the attack itself**. | Written into the components' and the step's descriptions | `Mitigation.bypassed_by` (range `AttackStep`), or an Assertion predicate; em-02 also wants a "disabled by" form | SACM's "defeated" claims (RPT-0005 §7) |
| AI-8 | **Most published AI attacks have no catalog case study.** ATLAS 2026.09 has 73 case studies and none for CVE-2025-53773 or ForcedLeak, so em-02's and em-03's step-to-technique links are the drafter's hypotheses. `asserted_by` tells them apart from em-01's ATLAS-attributed links, but with AI-1 unresolved they are 9 Assertions per model, and the app does not show them (app finding A-3) | `uses_technique` Assertions by the AI drafter, confidence per link | AI-1's `AttackStep.uses_pattern`, keeping who made each link | AI-1; RPT-0014 calibration |
| AI-9 | **The CVE's affected product is not the product attacked.** CVE-2025-53773's title names "GitHub Copilot and Visual Studio" and its CVE Program container cites the write-up, which attacks VS Code. Yet its affected list names only Visual Studio 2022 17.14.0 to before 17.14.12. Separately, `Vulnerability.affects` points at a Product, with no version range. | Two Products: `affects` names the CVE's product, and an AI-proposed `affects` Assertion names VS Code with Copilot. The version range is in the product's name | A version range on the `affects` edge, as CVE `versions` and the CSAF product tree have | RPT-0005 Table 6 (product identity) |
| AI-10 | **No home for a vulnerability without a CVE.** ForcedLeak has a name, a disclosure timeline and a researcher-claimed "CVSS 9.4" with no vector, but no catalog id. | No Vulnerability; the weaknesses enter through `exploits` Assertions (as in pv-02); the score is in the researcher party's description | A Vulnerability whose `catalog_ref` is optional, named by `alias_ids` (e.g. "ForcedLeak"), with severity claims as AI-5's signal Assertions | AI-5; pv-02 |
| AI-11 | **Trust that lapses.** The browser trusted `*.my-salesforce-cms.com` by name, and the domain expired and was bought for $5. A trust zone has no basis ("trusted because Salesforce owns it") and no validity, so the attacker's server sits inside a trusted zone with nothing to flag it. | A `csp-allowlisted-domains` zone inside the internet, with the expiry in its description | A basis and a validity period on zone membership (`in_trust_zone`), or on TrustBoundary | CWE-942 |
| AI-12 | **A vendor fix that the customer must also turn on.** Salesforce shipped Trusted URLs Enforcement; Noma tells customers to apply Salesforce's recommended actions. One `mitigation_status` cannot say "available from the vendor, adoption unknown", and MitigationStatus has no `unknown`. | Two Mitigations, Salesforce's `complete` and the customer's `planned` | An `unknown` status, or vendor availability kept apart from per-deployment status | `MitigationInstance` (not core; spec/vectors README) |
| P2 | **No external entities** (reconfirms #130's P2). The attacker's mail sender and server are Components outside the product. | Components with no product | The proposal's ExternalEntity | #130 decision 2 |

What worked without change: ATLAS mitigations fit `Mitigation.catalog_ref` (AML.M0033, AML.M0026; ATLAS 2026.10 renames M0026, RPT-0009 §6); ATLAS techniques fit `AttackPattern.catalog_ref`; CNA and ADP attribution fit `Assertion.asserted_by`; and the one-click and zero-click variants fit an OR gate.

## Tested in the desktop app (2026-11-09)

At the sponsor's request, all three models were opened in the desktop app. The app ran from a local checkout of `main`'s #211 code, with `tmodel serve` and `npm run dev`. The engine lists them, `/graph` builds them (87, 83 and 71 nodes), and `/attack-paths` finds every threat. The model report, attack-path and graph views all render, including em-02's OR gate and em-03's AND gate. What the test found:

| # | Finding | Where |
|---|---|---|
| A-1 | **The app opens only models in `spec/vectors/`.** These files live here, so they were copied there locally for the test and not committed. | engine `list_models`; `/graph` resolves names in that folder |
| A-2 | **The example banner says "It is not a security assessment of a real product"** under titles like "Microsoft 365 Copilot". DL-0038 fixed the wording for `pv-*` models only. These files get the default kind, `other`, so they get the default wording. Even the `pv-*` wording says "a real automotive attack", so it would not fit these models either. | `report-render.ts`, `EXAMPLE_KIND_NOTICES` |
| A-3 | **Links held in Assertions do not show.** In the report, the Weaknesses table says "None recorded" for attack patterns, and the attack-path boxes show each step's tactic but not its technique. So the `uses_technique` and `exploits` links (AI-1, AI-8) are invisible to a reader. | report Weaknesses and Attack patterns tables; attack-path step boxes |
| A-4 | **A model with two products gets both names as its title.** em-02's title joins VS Code with Copilot and Visual Studio 2022 17.14 with "and", so it is 143 characters long. | engine `_model_summary` (title from all products) |

The app's "modelling note" rule hides any description sentence that holds code marks, file names or ids. Sentences in em-02 and em-03 were reordered so that each description opens with plain text, and the notes stay under Details.

## Next

- A model from a different attack class, such as poisoning or model theft, so that AI-1 to AI-12 are tested on more than prompt injection.
- Route AI-8 to AI-12 in RPT-0009 §8, as G13 onward, in the report's next version. How they were found is in DL-0051.
- Findings A-2 to A-4 go to the renderer's owner. Whether these models move into `spec/vectors/`, so that the app and the site list them, is the sponsor's call (DL-0038 item 7 left the same question open for pv-01 and pv-02).
- RPT-0009 §5 now places each stage of em-01 against the ETSI EN 304 223 and CISA AI-in-OT provisions, and §8 routes these gaps as G1 to G7.
