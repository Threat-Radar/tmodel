---
schema: "archdoc/v1"
id: RPT-0013
title: "Secure Development Lifecycle & conformance"
short_title: "SDL & conformance"
description: "Landscape of secure-development-lifecycle guidelines (NIST SSDF, Microsoft SDL, OWASP SAMM, BSIMM, SAFECode, ISO/IEC 27034, ISO/SAE 21434 process, IEC 62443-4-1, …), a requirements crosswalk showing how the specs overlap (MAP-0001), and the conformance-validation / document-governance model for tmodel. Evidence, not decisions."
type: research
category: process
status: draft
version: "0.3.0"
date: "2026-10-01"
updated: "2026-10-03"
authors:
  - role: sponsor
    id: paul-lambert
  - role: research
    id: multi-agent
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: research/0013-sdl-conformance/report.md
defers_to: ARCH-0001
agent_notes: >
  Skeleton. Plan is in dimensions.md (five lanes). Drives the iteration-7 model additions
  (SDL/Gate/Milestone object, Mitigation `kind`, conformance validation, governed document-
  views) and the requirements crosswalk MAP-0001. SDL is post-MVP (ADR-0002 scope guard);
  this is the research that makes it buildable later. Every guideline → a library/ record.
---

# RPT-0013 — Secure Development Lifecycle & conformance

**Evidence, not a decision.** Plan: `dimensions.md`. Feeds iteration-7 of the object model
(#15) and the deferred audit/compliance work (#19). The headline output is **MAP-0001**, a
requirements crosswalk showing how the SDL specs overlap.

## 0. Summary & gap analysis

> **Update 2026-10-03 (v0.3.0).** The guidelines are now library records (topic `sdl`, 44 records,
> 29 with full FX-1 extraction + independent verify/cross-check; see `sources.md`). MAP-0001 is rebuilt
> as **v0.2.0** from source-published mappings (34 requirements × 16 frameworks, companion
> `spec/MAP-0001.yaml`), and the per-reference object-model passes are consolidated in
> **`sdl-object-model.md`** (RPT-0013-OM: 46 canonical objects, 60 relationships, answers to the
> R-040…R-044 design questions). Corrections to this draft found on the way: the release gate is
> **not** unique to SSDF PO.4 (SDL 5.2 FSR, BSIMM SM1.4/SM1.7/SM2.6, IEC 62443-4-1 SM-12,
> BSI TR-03185 and ENISA all define one); crypto is first-class in more frameworks (ASVS, FDA, ENISA);
> SSDF 1.2 (800-218r1) is still an initial public draft; OMB M-26-05 (2026-01-23) rescinded M-22-18
> and M-23-16, so SSDF attestation is now optional for US agencies. The sections below are the
> 2026-10-01 first draft, kept for the record.


**First draft from a 3-lane multi-agent pass** (landscape, crosswalk, conformance/governance).
Framework structures verified against primary sources; many atomic cells are `approx` pending the
purchased standards, and **no guideline is a library record yet** (ingestion = T-033/T-029).

- **Two kinds of guideline + maturity models.** Lifecycle/process standards (MS SDL, IEC 62443-4-1,
  ISO/SAE 21434, ISO 26262, ISO 27034) have phases + work products; outcome catalogues (NIST SSDF,
  SAFECode, CISA Secure by Design, SLSA, SP 800-161) have no phases; SAMM/BSIMM measure maturity.
- **The near-universal requirements** (MAP-0001): **threat modeling/TARA** (all 7 — the anchor for
  tmodel), security requirements, security testing before release, vulnerability management +
  disclosure, third-party/SBOM, secure design + coding.
- **Real divergences:** crypto standards (first-class only in MS SDL + SAFECode), secure-build/
  provenance (strong in SSDF/MS, thin elsewhere), hardening (IEC SG most prescriptive), operational
  IR (IEC 4-1 defers it), and the **release gate** (only SSDF PO.4 names it as a discrete auditable
  practice — our SDL `Gate` exit-criteria hook).
- **Recommendation shape:** model each common requirement as a `Requirement` with cross-spec
  `maps_to` edges (MAP-0001); SDL `Gate`s carry phase-due requirements as exit criteria; conformance
  is the automatable "every in-scope threat has an approved, evidenced mitigation" check (§4).
  Crosswalk: **MAP-0001**.

## 1. SDL / SSDL guideline landscape (Lane 1)

Verified structures (sources in `sources.md`): **NIST SSDF 800-218** (PO/PS/PW/RV, 19 practices/42
tasks; SDLC-agnostic; PW.1.1 = threat modeling) + **800-218A** (generative-AI profile); **Microsoft
SDL** (now 10 named practices, no IDs; rooted in Training→Req→Design→Impl→Verif→Release→Response);
**OWASP SAMM v2** (5 functions × 3 practices × 2 streams, maturity 0–3); **BSIMM** (4 domains / 12
practices; descriptive, observation-based); **ISO/SAE 21434** (Cl.5–15; Cl.9 concept, **Cl.15 TARA**,
Cl.11 validation, Cl.13 ops/IR, Cl.8 continual); **IEC 62443-4-1** (8 practices SM/SR/SD/SI/SVV/DM/
SUM/SG, ML1–ML4; **SR-2 = threat model**); **SAFECode 2018** (ASC Definition → Design → Secure Coding
→ Testing → Manage Findings → Vuln Response). Context-setters: **CISA Secure by Design** (principles,
pledge), **SLSA** (build track L0–L3, provenance), **SP 800-161** (C-SCRM). *SSDF 1.2 (800-218r1)
was in public draft Dec 2025; final status unconfirmed as of today.*

## 2. Phases, gates, checkpoints, milestones (Lane 2)

Each framework's native phase/gate vocabulary and the **canonical phase-line crosswalk** are in
**MAP-0001**. Key points: lifecycle standards (MS SDL, IEC 4-1, ISO 21434) order explicit phases with
**gates** (MS "mandatory checks and approvals"; ISO 21434 "release for post-development"; IEC ML-scored
practices); catalogues (SSDF, SAFECode) and maturity models (SAMM, BSIMM) are **not** phase-ordered —
their placement onto the canonical line is best-fit. Program-management attributes a `Gate` needs:
entry/exit criteria, owner, approval, planned vs actual dates, dependencies.

## 3. Requirements mapping & overlap → MAP-0001 (Lane 3)

**Delivered as a first-draft crosswalk: [`spec/MAP-0001`](../../spec/MAP-0001-sdl-requirements-crosswalk.md)**
— 19 atomic requirements × 7 frameworks, with the big overlaps, the divergences, and the phase line.
A "cell" means different things per column (hard requirement vs maturity activity vs named practice);
`approx` cells + IEC/ISO IDs need verification against the purchased standards before acceptance.

## 4. Conformance validation & automation (Lane 4)

Conformance spans self-attestation (SSDF via the CISA form; SLSA; CISA pledge), maturity scoring
(SAMM self-assessment, BSIMM paid benchmark), internal gate enforcement (MS SDL), and third-party
certification/audit (IEC 62443-4-1 via ISASecure SDLA; ISO 21434/26262). **Nobody mandates a
machine-checkable format.** Automatable today: signed **attestations** (in-toto + SLSA predicate +
Sigstore/cosign; policy engines like Kyverno), **SBOM/VEX** schema checks, and **OSCAL** control
mapping (catalog/profile/SSP/assessment-results/POA&M; compliance-trestle, C2P). **Not** automatable:
maturity scores, independence/adequacy judgements, and whether a mitigation is *actually* adequate.

**The automatable "threats-mitigated" check (design for R-042):** over a machine-readable threat
model, fail the gate unless — every in-scope threat has a `disposition` (mitigate/accept/transfer/
avoid, mirroring ISO 21434 risk treatment); every "mitigate" threat links ≥1 mitigation with status
≥ approved; each such mitigation has ≥1 resolvable, fresh, digest-matching **evidence** record;
accept/transfer carry an authorised approval; out-of-scope threats carry a rationale; no dangling IDs.
Validate schema (JSON Schema) + semantics (OPA/Rego or CEL) as a required CI check; approvals as
signed records; optionally emit OSCAL assessment-results. **Limit:** this proves linkage + approval,
not adequacy — the human cybersecurity-assessment role (ISO 21434) remains.

## 5. Document governance as views over the KG (Lane 5)

Governance attributes seen in practice (synthesised; not one standard): **document owner (role),
version, change history (author/reviewer/approver, dated), status** (draft/in-review/approved/
superseded), review cadence, a link to the **baseline** (release/commit) it describes. Prior art for
**document-as-view-over-a-SoT**: MBSE / **SysML v2 View & Viewpoint** (documents generated from the
model); **OMG SACM** assurance cases (structured argument is the SoT, the rendered case is a view);
**OSCAL → Word** (the machine-readable file is authoritative, the Word doc is generated); GRC
platforms. Consequence for our **governed document-view**: approval attaches to a **specific snapshot**
(commit/digest) so "approved" is reproducible; the view carries the governance metadata but **stamps it
from the KG snapshot**, not free-text; hand-edits to a rendered view are rejected/flagged; signed
attestations (in-toto / signed git tags) are the natural sign-off. Folds into §10 + §4 at iteration 8.
