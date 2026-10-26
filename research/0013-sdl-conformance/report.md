---
schema: "archdoc/v1"
id: RPT-0013
title: "Secure Development Lifecycle & conformance"
short_title: "SDL & conformance"
description: "Landscape of secure-development-lifecycle guidelines (NIST SSDF, Microsoft SDL, OWASP SAMM, BSIMM, SAFECode, ISO/IEC 27034, ISO/SAE 21434 process, IEC 62443-4-1, …), a requirements crosswalk showing how the specs overlap (MAP-0001), and the conformance-validation / document-governance model for tmodel. Evidence, not decisions."
type: research
category: process
status: draft
version: "0.4.0"
date: "2026-10-01"
updated: "2026-10-22"
authors:
  - role: sponsor
    id: nymble
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: nymble
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0013-sdl-conformance/report.md
defers_to: ARCH-0001
agent_notes: >
  v0.4.0 (2026-10-22) replaces the 2026-10-01 first-draft body, whose claims the ingestion and
  crosswalk disproved (no records yet; release gate unique to SSDF; 19x7 crosswalk). Body now states
  the verified findings and points at the evidence: library topic sdl (44 records), MAP-0001 v0.2.0,
  RPT-0013-OM, and the public report sdl-report.md (RPT-0013-PUB, published as docs/reports/sdl.html).
  Evidence, not decisions: the SDL/governed layer is DEC-001b, held open by ADR-0010.
---
# RPT-0013 — Secure Development Lifecycle & conformance

**Evidence, not a decision.** This is the internal research record for issue #67. The public,
reader-facing report built from it is **[`sdl-report.md`](sdl-report.md)** (RPT-0013-PUB),
published as `docs/reports/sdl.html`. The SDL / governed layer it informs is **DEC-001b, held
open by ADR-0010**; ARCH-0001 proposal §3c carries the current model text.

| Artifact | What it is |
|---|---|
| `library/` topic `sdl` | 44 records; 29 with full FX-1 extraction plus an independent verify and cross-check pass; every record has an object-model pass. Source log: [`sources.md`](sources.md) |
| [`spec/MAP-0001`](../../spec/MAP-0001-sdl-requirements-crosswalk.md) v0.2.0 (+ `MAP-0001.yaml`) | 34 requirements × 16 frameworks, from source-published mappings; judgement cells marked; contradictions listed |
| [`sdl-object-model.md`](sdl-object-model.md) (RPT-0013-OM v0.2.0) | 46 canonical SDL objects and 60 relationships from 1,510 source objects; evidence for R-040…R-044 |
| [`sdl-report.md`](sdl-report.md) (RPT-0013-PUB v1.0.0) | Public report: specifications compared, lifecycle, catalog, implementation, maturity, object model, bibliography |

All extraction, synthesis and reports passed an adversarial review; human review (FX-1 pass 4,
`reviewed_by`) is still outstanding everywhere.

## 0. Summary

- **Four kinds of document, read as layers.** Outcome frameworks say what to achieve (NIST SSDF,
  CISA Secure by Design, ETSI TS 104 219); process standards say how to organise it (Microsoft SDL,
  SAFECode, IEC 62443-4-1, IEC 81001-5-1, ISO/IEC 27034, BSI TR-03185); maturity models say how well
  (OWASP SAMM 2.2, BSIMM16); verification and supply-chain standards say what the product must
  satisfy (OWASP ASVS 5, SLSA 1.2, OSPS Baseline). Law now sits on top (EU CRA).
- **The most widely shared requirements** (MAP-0001, published mappings / any match, of 16):
  third-party component risk 13/15, security testing 12/15, threat modeling 11/15, secure design
  principles 11/14, vulnerability remediation and monitoring 11/14 each. **No requirement appears in
  all 16.** Threat modeling is one of the most widely shared practices, not the single universal one.
- **Real divergences:** build provenance (published mappings in only 3 frameworks), notification of
  actively exploited vulnerabilities (1, the CRA), cryptographic standards and AI-specific practice.
  For ISO/SAE 21434 and the FDA guidance no publisher maps at all; those columns are our judgement.
- **Release gates are common, in three styles** — not unique to SSDF PO.4 as the first draft said:
  SDL 5.2's Final Security Review, IEC 62443-4-1 SM-11/SM-12, BSIMM SM1.4/SM1.7/SM2.6 (descriptive),
  BSI TR-03185, ENISA's 125 gate criteria, and the CRA as a legal precondition. The current Microsoft
  SDL publishes no gate, and the SSDF says its table order implies no sequence.
- **Policy status (verified 2026-10-02/03):** OMB M-26-05 (2026-01-23) rescinded M-22-18 and M-23-16,
  so SSDF attestation is optional for US agencies; SSDF 1.2 (SP 800-218r1) is still an initial public
  draft (2025-12-17). CRA Art. 14 reporting applies from 2026-09-11, the rest from 2027-12-11; no
  harmonised standard is cited in the OJ yet.

## 1. Guideline landscape

Structures, verified against the library records: **SSDF 1.1** (4 groups, 19 practices, 42 tasks;
1.2 IPD adds PO.6 and PS.4); **SP 800-218A** (generative-AI profile); **Microsoft SDL** (current web
set: 10 practices, 48 sub-practices; Process Guidance 5.2 of 2012 with phases and the FSR);
**SAFECode** 3rd ed. (2018); **OWASP SAMM 2.2.0** (5 functions, 15 practices, 30 streams, 90
activities, levels 1–3; scores summed across levels); **BSIMM16** (4 domains, 12 practices, 128
activities, 111 firms; descriptive); **IEC 62443-4-1:2018** (8 practices, 47 requirements, ML 1–4;
SR-2 = threat model); **ISO/SAE 21434** (Cl. 15 TARA); **ASVS 5.0.0** (345 requirements, L1–L3);
**SLSA 1.2** (Build L0–L3, Source L1–L4); **OSPS Baseline** v2026.08.28 (41 controls, levels 1–3);
**EU CRA** (Annex I Parts I–II, Art. 13–14); **UK Software Security Code of Practice** (14 principles);
**ETSI TS 104 219** (6 essentials, 42 tasks, 183 actions, Annex B.2 crosswalk to 29 frameworks);
**BSI TR-03185** v1.1.1 and **TR-03183-1** v1.0.0; **ENISA SbD playbook** v1.0; **FDA** premarket
cybersecurity guidance (Feb 2026, QMSR). Paywalled standards (IEC 62443-4-1, IEC 81001-5-1, ISO/IEC
27034-1, 29147, 30111) are summarized from free preview material only. Full list and versions:
[`sources.md`](sources.md).

## 2. Phases, gates, checkpoints, milestones

The consolidated object model separates three things the sources conflate: a **Gate** (when a
decision is made, with typed exit criteria and an accountable approver), a **Milestone** (a dated,
owned deliverable) and a **Level** (how strongly something holds — `AssuranceLevel` for products,
`MaturityLevel` for organisations; BSIMM levels are observation bands and never gate criteria). Only
a few sources order their phases (Microsoft SDL 5.2 numbers them); the SSDF and BSI TR-03185 say
their order is not a required sequence. **Any canonical phase order is therefore our choice.** A
`Gate` needs entry/exit criteria, owner, approval, planned vs actual dates and dependencies.
Detail: RPT-0013-OM §4(b).

## 3. Requirements mapping & overlap → MAP-0001

[`spec/MAP-0001`](../../spec/MAP-0001-sdl-requirements-crosswalk.md) v0.2.0 replaces the first
draft's 19 × 7 table: 34 requirements × 16 frameworks, about 1,030 clause references, each with
provenance (anchor / direct / chained / bridge / ours) and target edition. Hub = SSDF 1.1 tasks,
with other anchors where the SSDF is silent. Fifteen contradictions between published mappings are
documented (for example SSDF vs SAMM on 10 IEC and 40 BSIMM ids; SAMM's two SSDF mappings disagree
on 15 tasks; ETSI B.2 prints ten SBOM rows under PW.1.1). 123 judgement-only cells need expert review.

## 4. Conformance validation & automation

Conformance spans self-attestation (CISA form, now optional; SLSA; CISA pledge), maturity scoring
(SAMM, BSIMM), internal gates (SDL 5.2 FSR), third-party certification (IEC 62443-4-1 via ISASecure
SDLA; PCI Secure SLC assessors) and law (CRA conformity assessment). **No source mandates a
machine-checkable format.** Automatable today: signed attestations (in-toto + SLSA provenance/VSA,
policy engines), SBOM/VEX schema checks, OSCAL control mapping. Not automatable: maturity scores,
independence and adequacy judgements.

**The automatable "threats-mitigated" check (R-042).** Over a machine-readable threat model, fail
the gate unless every in-scope threat has a disposition (mitigate / accept / transfer / avoid /
share); every "mitigate" threat links at least one mitigation with an approving Review; each such
mitigation's requirement has fresh, digest-matching evidence bound to the release; accept and
transfer carry an authorised, time-bound approval; out-of-scope threats carry a rationale.
**The result needs more than pass/fail:** not-applicable with a reason, inconclusive, partial,
covered-by-POA&M, waived, not-assessed — store the source's native value (RPT-0013-OM §4(c); the
SLSA VSA is the closest ready shape). ADR-0010 names the missing Mitigation→Review edge (C1) as a
precondition. **Limit:** this proves linkage and approval, not adequacy.

## 5. Document governance as views over the KG

Governed-view metadata confirmed across the sources: an owner distinct from the approver, approvers
with quorum and independence, version and snapshot, audience or disclosure tier, retention, and
refresh triggers (`ChangeEvent`; ESF: every functional change, major release and at least yearly).
The CISA attestation form supplies a governance pattern: a signatory with authority, a scope, a
kind (new / revised / after waiver), forward binding until revoked, and third-party assessment in
lieu of signature. Approval attaches to a specific snapshot so "approved" is reproducible. Prior art
for document-as-view: SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word. Detail: RPT-0013-OM §4(d).

## 6. Open questions

- Human review (FX-1 pass 4) of the library records, MAP-0001 and RPT-0013-OM.
- Licensing of verbatim extracts in the public library (SAFECode all rights reserved; SDL 5.2
  CC BY-NC-SA).
- CRA harmonised standards (EN 40000-1-2, -1-3) and PCI Secure SLC 2.0 text: ingest when available.
- DEC-001b: the critique items C1/M1/M4/M5 in ADR-0010.
