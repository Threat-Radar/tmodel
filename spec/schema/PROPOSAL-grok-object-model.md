# Grok proposal — LinkML object model (draft 0.1.0)

**This is a Grok proposal. It is not accepted.**

Assigned for Paul (nymble) to pick up. Later a Claude account will own follow-through.

Do not treat `tmodel-object-model.linkml.yaml` or this note as normative until an ADR accepts the object model (`DEC-001`). `spec/schema/` was a README stub on purpose. Landing a draft here does not select an encoding and does not close `DEC-*`.

## What landed

`tmodel-object-model.linkml.yaml` is LinkML draft **0.1.0** (`status: draft`), copied in for adversarial review and as a target shape for library extraction. Federation / import of STIX, OTM, CAPEC, and other external models is a **later mapping** (`DEC-002`, issue #9), not this file.

## Open work (not settled in this proposal)

1. **Adversarial review** against ARCH-0001, ARCH-0001-PROPOSAL v0.2.0, ADR-0003, ADR-0004, design-log, and ADR-0005 / DEC-003. ADR-0005 is **not a file on `main`**. The record is closed PR #70 and `design-log/0011-composite-risk-vector/README.md` (on `main`, DL-0011 says the bot ADR-0005 was dropped and DEC-003 stays open).

   **Known tension — leave it open.** design-log/0011 says Common Criteria feasibility is display-only. The sponsor position associated with DEC-003 / ADR-0005 says CC attack feasibility is a real vector component. The YAML header asserts that DL-0011 is superseded and that DEC-003 / ADR-0005 were accepted on 2026-10-02. That assertion is part of the draft under review. It is not a decision this proposal makes, and it disagrees with DL-0011 and ARCH-0001-PROPOSAL v0.2.0 on `main`.

2. **Agentic extraction.** Upcoming Agent Threat Modeling searches should extract from Library reference records into objects that conform to this schema. Quality bar: good enough to build useful models, not a dump. Iterate on a **subset** first. A second pass only after the first extract is good.

3. **Partitioning (unresolved).** Many threat models versus one large model. Ask for a recommendation after the subset extract. This proposal does not pick one.

4. **Schema status.** Draft 0.1.0. `DEC-001` is not accepted. `spec/schema` was a stub. Federation of STIX/OTM is later mapping (#9), not this file.

5. **For Claude later.** Read this note, `tmodel-object-model.linkml.yaml`, and the pull request that added them. Do not treat them as normative until an ADR.
