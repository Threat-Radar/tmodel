---
schema: "archdoc/v1"
id: ADR-0002
title: "MVP scope for the early-December demo"
short_title: "MVP scope"
description: "PROPOSED decision for DEC-005 — what the tmodel MVP demonstrates, scoped by the ADR-0001 radar/tmodel split. Options + recommendation; accept at the Week-0 gate."
type: decision
category: process
status: proposed
version: "0.1.0"
version_policy: "semver; accept by flipping status to accepted and bumping to 1.0.0"
date: "2026-09-30"
updated: "2026-09-30"
decision_makers:
  - role: sponsor
    id: paul-lambert
reviewers: []
needs_review: true
reviewed: false
canonical_path: spec/ADR-0002-mvp-scope.md
proposes: DEC-005
defers_to: ARCH-0001
---

# ADR-0002 — MVP scope (PROPOSED)

**Status: proposed. This drafts DEC-005 for ratification at the Week-0 gate — it
does not accept it.** To accept: pick an option, flip `status: accepted`, bump to
1.0.0, add a changelog line, and update ARCH-0001 §8 DEC-005.

## Context

- **ADR-0001** split the work: **radar** (= `tradar`) does composition & finding;
  **tmodel** is the architectural threat-modeling / knowledge-graph / human-review
  layer that **consumes** radar output. So the MVP is **not a scanner** — it is the
  modeling, review, risk, and graph layer.
- **Demo floor is I3 (Nov 5)**; ~5 weeks, 4 students. Review criteria reward a
  **modest, achievable** end-to-end slice over a wildly ambitious one.
- Evidence in hand: RPT-0011 (lean RDF stack; reuse STIX/BRON/CWE/CVE/D3FEND;
  PROV-O + SHACL for provenance/review), the ISO 21434 requirement catalog, the
  FIPS 140 family, and the composition work (RPT-0004).
- Still open and **not required to finalize** for this choice: DEC-001 (object
  model), DEC-002/004 (graph substrate), DEC-006 (UI), DEC-003 (risk metric) —
  the MVP proceeds on provisional, RPT-0011-aligned choices.

## Decision to make (DEC-005)

*What single vertical slice does the early-December MVP demonstrate?*

## Options

### Option A — Reviewed attack-path graph over one real product  *(recommended)*
Ingest **radar output for one real product** (e.g. a container image) → build the
KG (assets, components, CVEs → CWE → CAPEC → ATT&CK via the **BRON** backbone) →
render an **interactive threat / attack-path graph** → a human **reviews &
annotates** an attack path (impact S/F/O/P, accept/reject, rationale, **PROV-O**
provenance) → a **risk score that reflects the human input**.
- **Proves the differentiating thesis end-to-end**: AI proposes, human reviews,
  grounded + auditable. Hits the PLAN §9 demo definition directly.
- Reuses what's already in the library; consumes radar per ADR-0001.
- In: object model + graph + human review + a simple risk score. Out (→ upside):
  product families, mitigation-lifecycle automation, compliance, multi-dimension.
- **Lowest-risk path to a compelling Nov-5 demo.**

### Option B — Compliance / audit-first (ISO 21434 or FIPS 140 driven)
MVP = the **requirement → work-product → evidence** audit model: load a product,
map applicable requirements (ISO 21434 TARA or FIPS 140), check coverage, emit an
**audit/gap report** with human review.
- Leverages the already-extracted ISO 21434 + FIPS 140 records; strong corporate
  angle. But less visual "threat graph," narrower wow-factor, and depends on #19.
- Good as **I4 upside built on Option A's graph**, not as the MVP floor.

### Option C — Breadth demo (several dimensions, shallow)
Touch SCA + rule-based + CWE/NVD + risk + graph shallowly.
- **Not recommended:** thin everywhere, nothing end-to-end; violates the demo-floor
  discipline and the "achievable beats ambitious" criterion.

### Option D — KG + NSF OKN federation / cross-graph query
Build toward OKN federation; demo a cross-graph query (à la the semiconductor
supply-chain example).
- **Not recommended for the MVP:** federation is a parking-lot item; too much risk
  for 5 weeks. Keep as a post-demo direction.

## Recommendation

**Option A.** It proves the thesis end-to-end, is demoable by Nov 5, reuses the
existing library backbone, and leaves B (compliance/audit), mitigation lifecycle,
and product-family mapping as **I4 upside on the same graph**. B's audit model and
D's federation become the "what's next" story at the demo, not the MVP.

## If Option A is accepted — MVP definition

- **In:** one real product via radar; KG with the CVE→CWE→CAPEC→ATT&CK backbone;
  interactive attack-path graph; human review/annotation (impact, verdict,
  rationale, provenance); one risk score reflecting the review.
- **Out (upside):** product families, automated mitigation lifecycle, compliance
  audit, multiple expansion dimensions, OKN federation.
- **Acceptance (demo script):** load product → see threats + a threat chain as a
  graph → review/annotate an attack path → risk score updates from the human input
  → mapped to the product, mitigation state visible. (= PLAN §9.)
- **Depends on:** DEC-001/002/004/006 provisional choices (lean RDF; reuse
  STIX/BRON vocab; a graph UI from #10); DEC-003 — use a **simple risk metric**
  (CVSS environmental + human impact) for the MVP, deferring ISO 21434 / Common
  Criteria feasibility to I4.

## Consequences

Narrows I1–I3 effort to the Option-A slice; the student research reports feed it
(frameworks → model, products/UI → graph UI, schema → object model, composition →
radar input). B/D move to the post-MVP backlog.
