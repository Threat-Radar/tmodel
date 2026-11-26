# Human review packet for #170

Owner: @paria03. **39 accepted; 1 rejected; 0 pending.** This packet expands the exact targets in [the sample](agentic-review-sample.md). Completed cards mirror the actual Reviews recorded in the extraction YAML. Each original rationale retains its pre-review wording; the decision and linked Review give the current human verdict.

For each card, open the source at the stated locator, check that the proposed Requirement is a fair paraphrase (including its strength), then decide whether it addresses the named threat. The mapping rationale is an automated proposal, not a source quotation or a human judgment. Accepting a link does not approve a product, verify a mitigation or certify a standard.

Use the card label when replying, for example `N01: accept — <what you checked and why>` or `N01: reject — <why the link is unsupported>`. Mixed decisions are valid. Leave a card pending if you cannot access or verify its source. Decisions are recorded as model Reviews only after the human owner actually supplies them; the decision fields below mirror those actual Review objects.

[Coverage, source capture differences and licensing](agentic-coverage.md) remain part of the evidence. OWASP material is adapted from the OWASP GenAI Security Project, *Agentic AI — Threats and Mitigations v1.1* (December 2025), under [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/). Its historical PDF digest has not been reverified; the cached download attempts are HTML, so do not treat them as a checked PDF.

## MAESTRO

[Primary source](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) · [Pinned library record](../../library/records/community/csa-maestro-2025/record.yaml) · [Extraction](csa-maestro-2025.yaml)

Scope check: the seven authored layer controls instantiate one general umbrella instruction. Each currently selects one example threat, rather than all threats in its layer. Section 3.2 C links are interpretations; section 4 groups mitigations with named pattern threats. The Multi-Agent pattern also names an Identity Attack with no proposed link here. Check these limits instead of treating every `medium` confidence as equivalent evidence.

### M01 · Layer 1 — Foundation Models — Tailor security controls for the foundation models layer to its…

**Proposed Requirement (recommended; authored):** Tailor security controls for the foundation models layer to its identified threats.

**Proposed target:** Adversarial Examples (`threat-instance:csa-maestro-2025-layer-1-adversarial-examples`).

**Source locator:** §3.2 A, Layer 1: Foundation Models; §3.2 C, Layer-Specific Mitigations

**Source reference:** `library:csa-maestro-2025#layer-1-foundation-models`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 A, Layer 1: Foundation Models; §3.2 C, Layer-Specific Mitigations; layer-specific umbrella advice instantiated for this named threat, not a source-prescribed concrete control.

**Assertion:** `assertion:csa-maestro-2025-layer-1-foundation-models-addresses-csa-maestro-2025-layer-1-adversarial-examples`

**Specific scope question:** Does this general layer-control instruction justify this one named threat link? The proposal is not an exhaustive mapping of the layer. A rejection can record that the specific edge is not supported without rejecting the general control itself.

**Your decision:** accepted

**What you checked and why:** The source identifies adversarial examples in this layer and recommends controls for its listed threats. I accept this as a general relationship.

### M02 · Layer 4 — Deployment and Infrastructure — Tailor security controls for the deployment and infrastructure…

**Proposed Requirement (recommended; authored):** Tailor security controls for the deployment and infrastructure layer to its identified threats.

**Proposed target:** Compromised Container Images (`threat-instance:csa-maestro-2025-layer-4-compromised-container-images`).

**Source locator:** §3.2 A, Layer 4: Deployment and Infrastructure; §3.2 C, Layer-Specific Mitigations

**Source reference:** `library:csa-maestro-2025#layer-4-deployment-and-infrastructure`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 A, Layer 4: Deployment and Infrastructure; §3.2 C, Layer-Specific Mitigations; layer-specific umbrella advice instantiated for this named threat, not a source-prescribed concrete control.

**Assertion:** `assertion:csa-maestro-2025-layer-4-deployment-and-infrastructure-addresses-csa-maestro-2025-layer-4-compromised-container-images`

**Specific scope question:** Does this general layer-control instruction justify this one named threat link? The proposal is not an exhaustive mapping of the layer. A rejection can record that the specific edge is not supported without rejecting the general control itself.

**Your decision:** accepted

**What you checked and why:** Accepted as a general layer-specific relationship: the source lists compromised container images among deployment threats and recommends tailored controls. This is a partial mapping, not evidence that a control is implemented.

### M03 · Layer 6 — Security and Compliance — Tailor security controls for the security and compliance layer…

**Proposed Requirement (recommended; authored):** Tailor security controls for the security and compliance layer to its identified threats.

**Proposed target:** Compromised Security AI Agents (`threat-instance:csa-maestro-2025-layer-6-compromised-security-ai-agents`).

**Source locator:** §3.2 A, Layer 6: Security and Compliance; §3.2 C, Layer-Specific Mitigations

**Source reference:** `library:csa-maestro-2025#layer-6-security-and-compliance`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 A, Layer 6: Security and Compliance; §3.2 C, Layer-Specific Mitigations; layer-specific umbrella advice instantiated for this named threat, not a source-prescribed concrete control.

**Assertion:** `assertion:csa-maestro-2025-layer-6-security-and-compliance-addresses-csa-maestro-2025-layer-6-compromised-security-ai-agents`

**Specific scope question:** Does this general layer-control instruction justify this one named threat link? The proposal is not an exhaustive mapping of the layer. A rejection can record that the specific edge is not supported without rejecting the general control itself.

**Your decision:** accepted

**What you checked and why:** Accepted as a general layer-specific relationship: the source identifies compromised security AI agents in the security and compliance layer and recommends tailored controls. This is a partial mapping, not evidence that a control is implemented.

### M04 · Secure Inter-Layer Communication — Protect communication between architecture layers with secure…

**Proposed Requirement (recommended; paraphrase):** Protect communication between architecture layers with secure protocols.

**Proposed target:** Lateral Movement (`threat-instance:csa-maestro-2025-lateral-movement`).

**Source locator:** §3.2 C, Mitigation Strategies > Secure Inter-Layer Communication

**Source reference:** `library:csa-maestro-2025#secure-inter-layer-communication`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 C, Mitigation Strategies > Secure Inter-Layer Communication; proposed relationship to the named threat at §3.2 B. Cross-Layer Threats, not an explicit source crosswalk.

**Assertion:** `assertion:csa-maestro-2025-secure-inter-layer-communication-addresses-csa-maestro-2025-lateral-movement`

**Your decision:** accepted

**What you checked and why:** Accepted as an inferred relationship: protected inter-layer communication is relevant to lateral movement. This does not establish that communication protection alone stops such movement.

### M05 · Incident Response Plan — Prepare a response plan for incidents affecting multiple…

**Proposed Requirement (recommended; paraphrase):** Prepare a response plan for incidents affecting multiple architecture layers.

**Proposed target:** Goal Misalignment Cascades (`threat-instance:csa-maestro-2025-goal-misalignment-cascades`).

**Source locator:** §3.2 C, Mitigation Strategies > Incident Response Plan

**Source reference:** `library:csa-maestro-2025#incident-response-plan`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 C, Mitigation Strategies > Incident Response Plan; proposed relationship to the named threat at §3.2 B. Cross-Layer Threats, not an explicit source crosswalk.

**Assertion:** `assertion:csa-maestro-2025-incident-response-plan-addresses-csa-maestro-2025-goal-misalignment-cascades`

**Your decision:** accepted

**What you checked and why:** Accepted as an inferred response relationship: a cross-layer incident plan is relevant to cascading goal changes. This supports incident response, not a finding that the cascade is prevented.

### M06 · Explainable AI (XAI) — Make agent decisions sufficiently transparent to support…

**Proposed Requirement (recommended; paraphrase):** Make agent decisions sufficiently transparent to support auditing.

**Proposed target:** Repudiation (`threat-instance:csa-maestro-2025-repudiation`).

**Source locator:** §3.2 C, Mitigation Strategies > Explainable AI (XAI)

**Source reference:** `library:csa-maestro-2025#explainable-ai-xai`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 C, Mitigation Strategies > Explainable AI (XAI); proposed relationship to the named threat at §3.2 A. Layer 7, not an explicit source crosswalk.

**Assertion:** `assertion:csa-maestro-2025-explainable-ai-xai-addresses-csa-maestro-2025-repudiation`

**Your decision:** accepted

**What you checked and why:** Accepted as an inferred accountability relationship: transparent decisions support auditing when agents deny their actions. Explainability alone does not provide a complete audit trail.

### M07 · Safety Monitoring — Observe agent behavior during execution to detect unsafe…

**Proposed Requirement (recommended; paraphrase):** Observe agent behavior during execution to detect unsafe actions.

**Proposed target:** Agent Tool Misuse (`threat-instance:csa-maestro-2025-agent-tool-misuse`).

**Source locator:** §3.2 C, Mitigation Strategies > Safety Monitoring

**Source reference:** `library:csa-maestro-2025#safety-monitoring`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §3.2 C, Mitigation Strategies > Safety Monitoring; proposed relationship to the named threat at §3.2 A. Layer 7, not an explicit source crosswalk.

**Assertion:** `assertion:csa-maestro-2025-safety-monitoring-addresses-csa-maestro-2025-agent-tool-misuse`

**Your decision:** accepted

**What you checked and why:** Accepted as an inferred detection relationship: runtime monitoring can help identify unsafe tool use. This is not a prevention or effectiveness finding.

### M08 · Unconstrained Conversational Autonomy — Validate conversational input and apply safety filters tailored…

**Proposed Requirement (recommended; paraphrase):** Validate conversational input and apply safety filters tailored to the interaction.

**Proposed target:** Prompt Injection/Jailbreaking (`threat-instance:csa-maestro-2025-unconstrained-conversational-autonomy-prompt-injection-jailbreaking`).

**Source locator:** §4, Unconstrained Conversational Autonomy > Mitigations

**Source reference:** `library:csa-maestro-2025#unconstrained-conversational-autonomy`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §4, Unconstrained Conversational Autonomy > Mitigations; the pattern explicitly pairs this mitigation with the named threat.

**Assertion:** `assertion:csa-maestro-2025-unconstrained-conversational-autonomy-addresses-csa-maestro-2025-unconstrained-conversational-autonomy-prompt-injection-jailbreaking`

**Your decision:** accepted

**What you checked and why:** Accepted because the source explicitly pairs input validation and conversation-specific safety filters with prompt injection and jailbreaking in the Unconstrained Conversational Autonomy pattern.

### M09 · Hierarchical Agent Pattern — Protect agent communication, constrain access and routinely…

**Proposed Requirement (recommended; paraphrase):** Protect agent communication, constrain access and routinely monitor hierarchical agents.

**Proposed target:** Compromise of a Higher-Level Agent to Control Subordinates (`threat-instance:csa-maestro-2025-hierarchical-agent-pattern-compromise-of-a-higher-level-agent-to-control-subordinates`).

**Source locator:** §4, Hierarchical Agent Pattern > Mitigations

**Source reference:** `library:csa-maestro-2025#hierarchical-agent-pattern`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §4, Hierarchical Agent Pattern > Mitigations; the pattern explicitly pairs this mitigation with the named threat.

**Assertion:** `assertion:csa-maestro-2025-hierarchical-agent-pattern-addresses-csa-maestro-2025-hierarchical-agent-pattern-compromise-of-a-higher-level-agent-to-control-subordinates`

**Your decision:** accepted

**What you checked and why:** Accepted because the source explicitly pairs secure agent communication, access controls and monitoring with takeover of a higher-level agent in the Hierarchical Agent pattern.

### M10 · Self-Learning and Adaptive Agents — Clean and validate data used to train adaptive agents.

**Proposed Requirement (recommended; paraphrase):** Clean and validate data used to train adaptive agents.

**Proposed target:** Data Poisoning through Backdoor Trigger Injection (`threat-instance:csa-maestro-2025-self-learning-and-adaptive-agents-data-poisoning-through-backdoor-trigger-injection`).

**Source locator:** §4, Self-Learning and Adaptive Agents > Mitigations

**Source reference:** `library:csa-maestro-2025#self-learning-and-adaptive-agents`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: §4, Self-Learning and Adaptive Agents > Mitigations; the pattern explicitly pairs this mitigation with the named threat.

**Assertion:** `assertion:csa-maestro-2025-self-learning-and-adaptive-agents-addresses-csa-maestro-2025-self-learning-and-adaptive-agents-data-poisoning-through-backdoor-trigger-injection`

**Your decision:** accepted

**What you checked and why:** Accepted because the source explicitly pairs training-data sanitization and validation with poisoning through a hidden backdoor trigger in the Self-Learning and Adaptive Agents pattern.

## NIST SP 800-218A

[Primary source](https://doi.org/10.6028/NIST.SP.800-218A) · [Pinned library record](../../library/records/nist/sp-800-218a/record.yaml) · [Extraction](sp-800-218a.yaml)

Strength check: an R recommendation remains recommended; a C consideration asks you to evaluate an option. The requirement does not mandate adopting that option.

### N01 · PO.5.1.R1 — Measure and constrain user resource consumption and request…

**Proposed Requirement (recommended; paraphrase):** Measure and constrain user resource consumption and request rates during model development.

**Proposed target:** Denial-of-service conditions arising from adversarial prompts (`threat-instance:sp-800-218a-resource-exhaustion`).

**Source locator:** Table 1 (§3), PO.5.1 Recommendations/Considerations/Notes, R1, p. 10

**Source reference:** `library:sp-800-218a#PO.5.1.R1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PO.5.1 Recommendations/Considerations/Notes, R1, p. 10; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-po-5-1-r1-addresses-sp-800-218a-resource-exhaustion`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: resource and request limits address service exhaustion by limiting excessive consumption during model development.

### N02 · PO.5.1.R6 — Continuously check development environments for exposed…

**Proposed Requirement (recommended; paraphrase):** Continuously check development environments for exposed plaintext credentials or other secrets.

**Proposed target:** Unauthorized information disclosure (`threat-instance:sp-800-218a-disclosure`).

**Source locator:** Table 1 (§3), PO.5.1 Recommendations/Considerations/Notes, R6, p. 11

**Source reference:** `library:sp-800-218a#PO.5.1.R6`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PO.5.1 Recommendations/Considerations/Notes, R6, p. 11; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-po-5-1-r6-addresses-sp-800-218a-disclosure`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: monitoring for exposed secrets addresses information disclosure from leaked secrets specifically, not every form of disclosure.

### N03 · PS.1.1.R2 — Minimize direct model and model-component access regardless of…

**Proposed Requirement (recommended; paraphrase):** Minimize direct model and model-component access regardless of execution or storage location.

**Proposed target:** Theft of AI model weights (`threat-instance:sp-800-218a-weight-theft`).

**Source locator:** Table 1 (§3), PS.1.1 Recommendations/Considerations/Notes, R2, p. 11

**Source reference:** `library:sp-800-218a#PS.1.1.R2`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PS.1.1 Recommendations/Considerations/Notes, R2, p. 11; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-ps-1-1-r2-addresses-sp-800-218a-weight-theft`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: restricting direct model access reduces opportunities for unauthorized access and model-weight theft.

### N04 · PS.1.3.R4 — Apply protections proportionate to weight-related risk, such as…

**Proposed Requirement (recommended; paraphrase):** Apply protections proportionate to weight-related risk, such as encryption, integrity checks, signatures, multiparty approval or isolation.

**Proposed target:** Theft of AI model weights (`threat-instance:sp-800-218a-weight-theft`).

**Source locator:** Table 1 (§3), PS.1.3 Recommendations/Considerations/Notes, R4, p. 12

**Source reference:** `library:sp-800-218a#PS.1.3.R4`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PS.1.3 Recommendations/Considerations/Notes, R4, p. 12; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-ps-1-3-r4-addresses-sp-800-218a-weight-theft`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: encryption and access controls can protect model weights from theft. Hashes alone do not prevent theft.

### N05 · PW.3.1 — Check development data for poisoning, bias, excessive…

**Proposed Requirement (recommended; paraphrase):** Check development data for poisoning, bias, excessive uniformity and tampering before use and mitigate identified risks.

**Proposed target:** Poisoning of training data (`threat-instance:sp-800-218a-poisoning`).

**Source locator:** Table 1 (§3), PW.3.1, p. 14

**Source reference:** `library:sp-800-218a#PW.3.1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.3.1, p. 14; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-3-1-addresses-sp-800-218a-poisoning`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: checking development data for poisoning and tampering directly addresses poisoned training data.

### N06 · PW.3.1.R1 — Check dataset integrity and any known provenance before using…

**Proposed Requirement (recommended; paraphrase):** Check dataset integrity and any known provenance before using it for model development.

**Proposed target:** Poisoning of training data (`threat-instance:sp-800-218a-poisoning`).

**Source locator:** Table 1 (§3), PW.3.1 Recommendations/Considerations/Notes, R1, p. 14

**Source reference:** `library:sp-800-218a#PW.3.1.R1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.3.1 Recommendations/Considerations/Notes, R1, p. 14; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-3-1-r1-addresses-sp-800-218a-poisoning`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: data provenance and integrity checks help detect changes associated with poisoned data. A known origin does not guarantee safe content.

### N07 · PW.3.1.R2 — Choose suitable dataset-analysis and modification techniques…

**Proposed Requirement (recommended; paraphrase):** Choose suitable dataset-analysis and modification techniques such as anomaly detection, bias analysis, filtering, cleaning or fact checking.

**Proposed target:** Poisoning of training data (`threat-instance:sp-800-218a-poisoning`).

**Source locator:** Table 1 (§3), PW.3.1 Recommendations/Considerations/Notes, R2, p. 15

**Source reference:** `library:sp-800-218a#PW.3.1.R2`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.3.1 Recommendations/Considerations/Notes, R2, p. 15; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-3-1-r2-addresses-sp-800-218a-poisoning`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: data analysis, filtering and cleaning can identify or remove harmful data relevant to poisoning.

### N08 · PW.4.4.R2 — Inspect and extensively test acquired models and components for…

**Proposed Requirement (recommended; paraphrase):** Inspect and extensively test acquired models and components for malicious content and vulnerabilities before use.

**Proposed target:** Supply chain attacks (`threat-instance:sp-800-218a-supply-chain`).

**Source locator:** Table 1 (§3), PW.4.4 Recommendations/Considerations/Notes, R2, p. 16

**Source reference:** `library:sp-800-218a#PW.4.4.R2`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.4.4 Recommendations/Considerations/Notes, R2, p. 16; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-4-4-r2-addresses-sp-800-218a-supply-chain`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: testing acquired models and components for malicious content addresses supply-chain attacks.

### N09 · PW.5.1.R2 — Log, analyze and contextually validate model inputs and…

**Proposed Requirement (recommended; paraphrase):** Log, analyze and contextually validate model inputs and outputs, sanitizing or discarding problematic content.

**Proposed target:** Malicious code or other unwanted content in inputs and outputs (`threat-instance:sp-800-218a-injected-content`).

**Source locator:** Table 1 (§3), PW.5.1 Recommendations/Considerations/Notes, R2, p. 16

**Source reference:** `library:sp-800-218a#PW.5.1.R2`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.5.1 Recommendations/Considerations/Notes, R2, p. 16; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-5-1-r2-addresses-sp-800-218a-injected-content`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: contextual input and output validation and sanitization address malicious content. Logging alone does not remove content.

### N10 · PW.5.1.R3 — Encode model inputs and outputs so they cannot trigger…

**Proposed Requirement (recommended; paraphrase):** Encode model inputs and outputs so they cannot trigger unauthorized code execution.

**Proposed target:** Malicious code or other unwanted content in inputs and outputs (`threat-instance:sp-800-218a-injected-content`).

**Source locator:** Table 1 (§3), PW.5.1 Recommendations/Considerations/Notes, R3, p. 16

**Source reference:** `library:sp-800-218a#PW.5.1.R3`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Table 1 (§3), PW.5.1 Recommendations/Considerations/Notes, R3, p. 16; safeguard targets the named risk enumerated at Table 1, PW.1.1.R1.

**Assertion:** `assertion:sp-800-218a-pw-5-1-r3-addresses-sp-800-218a-injected-content`

**Your decision:** accepted

**What you checked and why:** Accepted as a proposed relationship: input and output encoding addresses unauthorized code execution from executable content, not every harmful output.

## OWASP Agentic AI Threats and Mitigations v1.1

[Primary source](https://genai.owasp.org/download/45674/?tmstv=1739819891) · [Pinned library record](../../library/records/community/owasp-agentic-threats-mitigations-v1-1/record.yaml) · [Extraction](owasp-agentic-threats-mitigations-v1-1.yaml)

Access/version check: locate the December 2025 v1.1 playbook and printed page, not an unrelated later edition. The download can return a sign-up page; leave a decision pending if you cannot verify the source text. The source repeats one bullet, and the extraction intentionally retains both occurrences.

### O01 · Playbook 1 / Step 1 / bullet 1 — Constrain available tools to reduce opportunities to manipulate…

**Proposed Requirement (recommended; paraphrase):** Constrain available tools to reduce opportunities to manipulate agent interactions.

**Proposed target:** T6 — Intent Breaking & Goal Manipulation (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t6`).

**Source locator:** Mitigation Strategies > Playbook 1 > Step 1 > top-level bullet 1 (printed p. 35; PDF page 36)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-1-step-1-bullet-1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 1 > Step 1 > top-level bullet 1 (printed p. 35; PDF page 36); Playbook 1 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-1-step-1-bullet-1-addresses-owasp-agentic-threats-mitigations-v1-1-t6`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted relationship: restricting available tools reduces opportunities for goal manipulation. This is partial protection, not proof that manipulation is prevented.

### O02 · Playbook 2 / Step 1 / bullet 2 — Record access to agent memory.

**Proposed Requirement (recommended; paraphrase):** Record access to agent memory.

**Proposed target:** T1 — Memory Poisoning (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t1`).

**Source locator:** Mitigation Strategies > Playbook 2 > Step 1 > top-level bullet 2 (printed p. 36; PDF page 37)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-2-step-1-bullet-2`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 2 > Step 1 > top-level bullet 2 (printed p. 36; PDF page 37); Playbook 2 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-2-step-1-bullet-2-addresses-owasp-agentic-threats-mitigations-v1-1-t1`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted investigation relationship: memory access logs support investigation of memory poisoning. Logging does not prevent poisoning.

### O03 · Playbook 2 / Step 2 / bullet 5 — Capture agent-memory snapshots that support forensic…

**Proposed Requirement (recommended; paraphrase):** Capture agent-memory snapshots that support forensic restoration.

**Proposed target:** T1 — Memory Poisoning (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t1`).

**Source locator:** Mitigation Strategies > Playbook 2 > Step 2 > top-level bullet 5 (printed p. 36; PDF page 37)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-2-step-2-bullet-5`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 2 > Step 2 > top-level bullet 5 (printed p. 36; PDF page 37); Playbook 2 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-2-step-2-bullet-5-addresses-owasp-agentic-threats-mitigations-v1-1-t1`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted recovery relationship: memory snapshots support recovery from memory poisoning if a trustworthy snapshot exists.

### O04 · Playbook 3 / Step 1 / bullet 5 — Limit request rates for APIs and expensive computations.

**Proposed Requirement (recommended; paraphrase):** Limit request rates for APIs and expensive computations.

**Proposed target:** T4 — Resource Overload (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t4`).

**Source locator:** Mitigation Strategies > Playbook 3 > Step 1 > top-level bullet 5 (printed p. 38; PDF page 39)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-3-step-1-bullet-5`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 3 > Step 1 > top-level bullet 5 (printed p. 38; PDF page 39); Playbook 3 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-3-step-1-bullet-5-addresses-owasp-agentic-threats-mitigations-v1-1-t4`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted relationship: limiting expensive requests directly limits excessive consumption associated with resource overload.

### O05 · Playbook 3 / Step 3 / bullet 1 — Detect excessive agent workloads as requests arrive.

**Proposed Requirement (recommended; paraphrase):** Detect excessive agent workloads as requests arrive.

**Proposed target:** T4 — Resource Overload (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t4`).

**Source locator:** Mitigation Strategies > Playbook 3 > Step 3 > top-level bullet 1 (printed p. 38; PDF page 39)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-3-step-3-bullet-1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 3 > Step 3 > top-level bullet 1 (printed p. 38; PDF page 39); Playbook 3 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-3-step-3-bullet-1-addresses-owasp-agentic-threats-mitigations-v1-1-t4`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted detection relationship: detecting excessive workloads helps identify resource overload. A response is required to stop the overload.

### O06 · Playbook 4 / Step 1 / bullet 6 — Authenticate both participants before allowing agent-to-agent…

**Proposed Requirement (recommended; paraphrase):** Authenticate both participants before allowing agent-to-agent exchanges.

**Proposed target:** T3 — Privilege Compromise (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t3`).

**Source locator:** Mitigation Strategies > Playbook 4 > Step 1 > top-level bullet 6 (printed p. 39; PDF page 40)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-4-step-1-bullet-6`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 4 > Step 1 > top-level bullet 6 (printed p. 39; PDF page 40); Playbook 4 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-4-step-1-bullet-6-addresses-owasp-agentic-threats-mitigations-v1-1-t3`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted relationship: authenticating communicating agents helps block unauthorized participants relevant to privilege compromise. Authentication alone does not enforce permissions.

### O07 · Playbook 4 / Step 3 / bullet 5 — Flag identity-related behavior inconsistent with the agent's…

**Proposed Requirement (recommended; paraphrase):** Flag identity-related behavior inconsistent with the agent's history.

**Proposed target:** T9 — Identity Spoofing & Impersonation (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t9`).

**Source locator:** Mitigation Strategies > Playbook 4 > Step 3 > top-level bullet 5 (printed p. 39; PDF page 40)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-4-step-3-bullet-5`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 4 > Step 3 > top-level bullet 5 (printed p. 39; PDF page 40); Playbook 4 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-4-step-3-bullet-5-addresses-owasp-agentic-threats-mitigations-v1-1-t9`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted detection relationship: unusual identity behavior can help detect impersonation. Anomalies are not proof of impersonation.

### O08 · Playbook 5 / Step 3 / bullet 1 — Make decision audit records cryptographically protected and…

**Proposed Requirement (recommended; paraphrase):** Make decision audit records cryptographically protected and resistant to alteration.

**Proposed target:** T15 — Human Manipulation (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t15`).

**Source locator:** Mitigation Strategies > Playbook 5 > Step 3 > top-level bullet 1 (printed p. 40; PDF page 41)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-5-step-3-bullet-1`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 5 > Step 3 > top-level bullet 1 (printed p. 40; PDF page 41); Playbook 5 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-5-step-3-bullet-1-addresses-owasp-agentic-threats-mitigations-v1-1-t15`

**Your decision:** accepted

**What you checked and why:** Accepted as an indirect investigation relationship: protected decision audit logs support investigation of human manipulation. They do not prevent deceptive persuasion.

### O09 · Playbook 6 / Step 1 / bullet 8 — Apply per-agent quotas and rate limits to prevent request…

**Proposed Requirement (recommended; paraphrase):** Apply per-agent quotas and rate limits to prevent request flooding.

**Proposed target:** T12 — Agent Communication Poisoning (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t12`).

**Source locator:** Mitigation Strategies > Playbook 6 > Step 1 > top-level bullet 8 (printed p. 41; PDF page 42)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-6-step-1-bullet-8`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 6 > Step 1 > top-level bullet 8 (printed p. 41; PDF page 42); Playbook 6 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-6-step-1-bullet-8-addresses-owasp-agentic-threats-mitigations-v1-1-t12`

**Your decision:** rejected

**What you checked and why:** Rejected the current control-to-threat connection: quotas limit flooding but do not establish message truth or integrity. Without an additional rationale, this control fits resource overload more directly than communication poisoning.

### O10 · Playbook 6 / Step 3 / bullet 6 — Compare decisions in similar situations and flag unexplained…

**Proposed Requirement (recommended; paraphrase):** Compare decisions in similar situations and flag unexplained contradictions.

**Proposed target:** T12 — Agent Communication Poisoning (`threat-instance:owasp-agentic-threats-mitigations-v1-1-t12`).

**Source locator:** Mitigation Strategies > Playbook 6 > Step 3 > top-level bullet 6 (printed p. 42; PDF page 43)

**Source reference:** `library:owasp-agentic-threats-mitigations-v1-1#playbook-6-step-3-bullet-6`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Mitigation Strategies > Playbook 6 > Step 3 > top-level bullet 6 (printed p. 42; PDF page 43); Playbook 6 names this threat in its threat mapping (pp. 34–35); this individual control-to-threat selection is an unreviewed interpretation.

**Assertion:** `assertion:owasp-agentic-threats-mitigations-v1-1-playbook-6-step-3-bullet-6-addresses-owasp-agentic-threats-mitigations-v1-1-t12`

**Your decision:** accepted

**What you checked and why:** Accepted as an interpreted detection relationship: contradictory agent decisions may reveal manipulation associated with communication poisoning. Contradictions alone are not proof.

## MCP Security Best Practices

[Primary source](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · [Pinned library record](../../library/records/community/mcp-spec-security-best-practices/record.yaml) · [Extraction](mcp-spec-security-best-practices.yaml)

Version check: these provisions refer to the recorded dated-page capture. Its digest differs from the library record, and the release-tag MDX has fewer sections. Check the capture/version described in the accounting notes; do not silently substitute the living page.

### C01 · Confused Deputy Problem > Mitigation / per-client-consent — Require each client to obtain user consent at the proxy before…

**Proposed Requirement (mandatory; paraphrase):** Require each client to obtain user consent at the proxy before third-party authorization begins.

**Proposed target:** Confused Deputy Problem (`threat-instance:mcp-spec-security-best-practices-confused-deputy-problem`).

**Source locator:** Confused Deputy Problem > Mitigation

**Source reference:** `library:mcp-spec-security-best-practices#confused-deputy-problem-mitigation-per-client-consent`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Confused Deputy Problem > Mitigation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-confused-deputy-problem-mitigation-per-client-consent-addresses-mcp-spec-security-best-practices-confused-deputy-problem`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: per-client consent addresses confused-deputy attacks by preventing reuse of another client's consent.

### C02 · Confused Deputy Problem > Required Protections > Redirect URI Validation / redirect-match — Match requested redirect URIs exactly to registered values and…

**Proposed Requirement (mandatory; paraphrase):** Match requested redirect URIs exactly to registered values and reject changed destinations until re-registration.

**Proposed target:** Confused Deputy Problem (`threat-instance:mcp-spec-security-best-practices-confused-deputy-problem`).

**Source locator:** Confused Deputy Problem > Required Protections > Redirect URI Validation

**Source reference:** `library:mcp-spec-security-best-practices#confused-deputy-problem-required-protections-redirect-uri-validation-redirect-match`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Confused Deputy Problem > Required Protections > Redirect URI Validation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-confused-deputy-problem-required-protections-redirect-uri-validation-redirect-match-addresses-mcp-spec-security-best-practices-confused-deputy-problem`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: exact redirect matching blocks redirect substitution relevant to confused-deputy attacks. Other authorization checks remain necessary.

### C03 · Token Passthrough > Mitigation / token-audience — Reject tokens unless they were issued specifically for this MCP…

**Proposed Requirement (mandatory; paraphrase):** Reject tokens unless they were issued specifically for this MCP server.

**Proposed target:** Token Passthrough (`threat-instance:mcp-spec-security-best-practices-token-passthrough`).

**Source locator:** Token Passthrough > Mitigation

**Source reference:** `library:mcp-spec-security-best-practices#token-passthrough-mitigation-token-audience`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Token Passthrough > Mitigation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-token-passthrough-mitigation-token-audience-addresses-mcp-spec-security-best-practices-token-passthrough`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: accepting only tokens explicitly issued for the MCP server enforces the intended token audience and addresses token passthrough.

### C04 · Server-Side Request Forgery (SSRF) > Mitigation > Validate Redirect Targets / redirect-targets — Reapply URL scheme and address restrictions at each redirect…

**Proposed Requirement (recommended; paraphrase):** Reapply URL scheme and address restrictions at each redirect destination instead of following redirects unchecked.

**Proposed target:** Server-Side Request Forgery (SSRF) (`threat-instance:mcp-spec-security-best-practices-server-side-request-forgery-ssrf`).

**Source locator:** Server-Side Request Forgery (SSRF) > Mitigation > Validate Redirect Targets

**Source reference:** `library:mcp-spec-security-best-practices#server-side-request-forgery-ssrf-mitigation-validate-redirect-targets-redirect-targets`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Server-Side Request Forgery (SSRF) > Mitigation > Validate Redirect Targets; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-server-side-request-forgery-ssrf-mitigation-validate-redirect-targets-redirect-targets-addresses-mcp-spec-security-best-practices-server-side-request-forgery-ssrf`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: validating every redirect destination addresses SSRF by preventing redirects from bypassing destination restrictions.

### C05 · Session Hijacking > Mitigation / unpredictable-session-id — Assign secure session identifiers that cannot be predicted…

**Proposed Requirement (mandatory; paraphrase):** Assign secure session identifiers that cannot be predicted deterministically.

**Proposed target:** Session Hijacking (`threat-instance:mcp-spec-security-best-practices-session-hijacking`).

**Source locator:** Session Hijacking > Mitigation

**Source reference:** `library:mcp-spec-security-best-practices#session-hijacking-mitigation-unpredictable-session-id`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Session Hijacking > Mitigation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-session-hijacking-mitigation-unpredictable-session-id-addresses-mcp-spec-security-best-practices-session-hijacking`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: unpredictable session identifiers reduce guessing relevant to session hijacking. They do not protect an already stolen identifier.

### C06 · Local MCP Server Compromise > Mitigation / one-click-consent — Obtain informed consent before running commands supplied…

**Proposed Requirement (mandatory; paraphrase):** Obtain informed consent before running commands supplied through one-click local-server configuration.

**Proposed target:** Local MCP Server Compromise (`threat-instance:mcp-spec-security-best-practices-local-mcp-server-compromise`).

**Source locator:** Local MCP Server Compromise > Mitigation

**Source reference:** `library:mcp-spec-security-best-practices#local-mcp-server-compromise-mitigation-one-click-consent`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: Local MCP Server Compromise > Mitigation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-local-mcp-server-compromise-mitigation-one-click-consent-addresses-mcp-spec-security-best-practices-local-mcp-server-compromise`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: informed consent before local commands adds human scrutiny relevant to local-server compromise. Consent does not prove a command safe.

### C07 · OAuth Authorization URL Validation > Mitigation > URL Scheme Validation / validate-schemes — Check authorization URL schemes and reject dangerous ones.

**Proposed Requirement (mandatory; paraphrase):** Check authorization URL schemes and reject dangerous ones.

**Proposed target:** OAuth Authorization URL Validation — Arbitrary Code Execution (`threat-instance:mcp-spec-security-best-practices-oauth-authorization-url-validation`).

**Source locator:** OAuth Authorization URL Validation > Mitigation > URL Scheme Validation

**Source reference:** `library:mcp-spec-security-best-practices#oauth-authorization-url-validation-mitigation-url-scheme-validation-validate-schemes`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: OAuth Authorization URL Validation > Mitigation > URL Scheme Validation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-oauth-authorization-url-validation-mitigation-url-scheme-validation-validate-schemes-addresses-mcp-spec-security-best-practices-oauth-authorization-url-validation`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: rejecting dangerous authorization URL schemes blocks code execution through dangerous URL handlers.

### C08 · OAuth Authorization URL Validation > Mitigation > URL Scheme Validation / prefer-allowlist — Validate authorization URLs against permitted schemes rather…

**Proposed Requirement (recommended; paraphrase):** Validate authorization URLs against permitted schemes rather than relying on a forbidden-scheme list.

**Proposed target:** OAuth Authorization URL Validation — Arbitrary Code Execution (`threat-instance:mcp-spec-security-best-practices-oauth-authorization-url-validation`).

**Source locator:** OAuth Authorization URL Validation > Mitigation > URL Scheme Validation

**Source reference:** `library:mcp-spec-security-best-practices#oauth-authorization-url-validation-mitigation-url-scheme-validation-prefer-allowlist`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: OAuth Authorization URL Validation > Mitigation > URL Scheme Validation; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-oauth-authorization-url-validation-mitigation-url-scheme-validation-prefer-allowlist-addresses-mcp-spec-security-best-practices-oauth-authorization-url-validation`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: allowlisting authorization URL schemes reduces gaps from incomplete blocklists relevant to code execution.

### C09 · OAuth Authorization URL Validation > Mitigation > Secure URL Opening / native-url-opener — Use the platform URL-opening facility that does not execute a…

**Proposed Requirement (recommended; paraphrase):** Use the platform URL-opening facility that does not execute a shell.

**Proposed target:** OAuth Authorization URL Validation — Arbitrary Code Execution (`threat-instance:mcp-spec-security-best-practices-oauth-authorization-url-validation`).

**Source locator:** OAuth Authorization URL Validation > Mitigation > Secure URL Opening

**Source reference:** `library:mcp-spec-security-best-practices#oauth-authorization-url-validation-mitigation-secure-url-opening-native-url-opener`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: OAuth Authorization URL Validation > Mitigation > Secure URL Opening; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-oauth-authorization-url-validation-mitigation-secure-url-opening-native-url-opener-addresses-mcp-spec-security-best-practices-oauth-authorization-url-validation`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: opening URLs without a shell avoids shell-command injection through URLs.

### C10 · stdio Transport Security in Proxy Scenarios > Mitigation > Client-Side Protections / proxy-isolation — Isolate proxy communication and constrain proxy privileges with…

**Proposed Requirement (recommended; paraphrase):** Isolate proxy communication and constrain proxy privileges with process sandboxing or a restricted execution environment.

**Proposed target:** stdio Transport Security in Proxy Scenarios — full system compromise (`threat-instance:mcp-spec-security-best-practices-stdio-transport-security-in-proxy-scenarios`).

**Source locator:** stdio Transport Security in Proxy Scenarios > Mitigation > Client-Side Protections

**Source reference:** `library:mcp-spec-security-best-practices#stdio-transport-security-in-proxy-scenarios-mitigation-client-side-protections-proxy-isolation`

**Original AI mapping rationale (before the recorded review):** AI-proposed, 2026-11-14; unreviewed. Basis: stdio Transport Security in Proxy Scenarios > Mitigation > Client-Side Protections; control appears in the named attack section, so the link is proposed at that section scope.

**Assertion:** `assertion:mcp-spec-security-best-practices-stdio-transport-security-in-proxy-scenarios-mitigation-client-side-protections-proxy-isolation-addresses-mcp-spec-security-best-practices-stdio-transport-security-in-proxy-scenarios`

**Your decision:** accepted

**What you checked and why:** Accepted as a source-section relationship: isolating and restricting proxy processes limits damage from system compromise. It does not eliminate the underlying vulnerability.
