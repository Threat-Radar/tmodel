---
schema: "archdoc/v1"
id: BACKLOG-0001
title: "tmodel backlog"
short_title: "Backlog"
description: "Task backlog. Each task becomes a GitHub issue; this file is the durable index. Increments are in PLAN-0001 §8."
type: backlog
category: process
status: draft
version: "0.2.5"
date: "2026-09-23"
updated: "2026-10-01"
needs_review: true
reviewed: false
canonical_path: project/BACKLOG-0001.md
defers_to: ARCH-0001
agent_notes: >
  Tasks are the execution unit; topics are the assignment unit (PROC-0001).
  Keep the id stable when it becomes an issue — put T-NNN in the issue title.
---

# Backlog

**Convention.** `T-NNN` is stable and survives becoming a GitHub issue — put the
id in the issue title. Status: `todo` · `doing` · `review` · `done` · `parked`.
Size: `S` <½day · `M` ~1day · `L` ~3days. Increments are in `PLAN-0001` §8.

**The demo floor is I3 (Nov 5)** — everything after is upside.

## Progress snapshot — 2026-09-30

- **I0 harness: done.** Repos created, roster added, `CODEOWNERS` set, branch
  protection on, library forked + wired + **synced with upstream m-of-n** (merge
  commit; reconverged). Vault people/project files written.
- **I1 research: underway.** First drafts merged for **RPT-0003** (products, #7),
  **RPT-0004** (composition, #8), **RPT-0011** (Knowledge Graphs & NSF OKN, #25).
  Library seeded: ISO/SAE 21434 (+ requirement catalog), FIPS 140-3 family
  (SP 800-140x), and ~28 NSF-OKN / KG-standard / cyber-KG reference records.
- **Open standard (blocks "done" on spec records): FX-1 full extraction** — spec
  records must be fully extracted (requirements, schemas, formats, vectors), not
  summarized. Most current reference records are first-pass summaries and do not
  yet meet the bar. See T-029.
- **Not yet started:** the Week-0 gate decisions (DEC-005 scope, DEC-007 tradar),
  the design/synthesis increment (I2), and everything from I3 on.

---

## I0 — Harness · Sep 23–29 · done

| id | task | own | sz | status |
|---|---|---|---|---|
| T-001 | Create GitHub repo `Threat-Radar/tmodel` (public) | PL | S | done |
| T-002 | Fork `m-of-n/library`; wire as submodule (absolute URL) | PL | S | done |
| T-003 | Add 4 students + Prof. Haskell as repo admins | PL | S | done |
| T-004 | Confirm roster; student handles in `CODEOWNERS`; vault people files | PL | S | done |
| T-005 | Port/author role skills into `tmodel/.claude/skills/` | all | M | todo |
| T-006 | Publishing site (mkdocs or equivalent) | all | M | parked |
| T-007 | Branch protection on `main` (PR-only, 1 review) | PL | S | done |
| T-008 | **Week-0 gate:** R-set + DEC-005 (ADR-0002) + DEC-007 (ADR-0001) ratified | all | L | **done** |

## I1 — Research · Sep 30–Oct 13 · underway

Research reports are now per-topic GitHub issues (#6–#13, #25); RPT-0001 remains
the umbrella landscape scaffold. Each report: sources → `library/` records
(FX-1, T-029), a comparison table + sections, then human review.

| id | task | issue / owner | sz | status |
|---|---|---|---|---|
| T-021 | RPT-0003 — Threat Modeling Products (commercial + OSS, UI comparison) | #7 · kriishnaa-18 | L | **review** (first draft merged) |
| T-022 | RPT-0004 — Product Composition (SBOM / HBOM) | #8 · Clovier | L | **review** (first draft merged) |
| T-023 | RPT-0011 — Knowledge Graphs & NSF OKN (+ gap analysis) | #25 · nymble | L | **review** (first draft merged) |
| T-024 | RPT — Threat Model Frameworks | #6 · paria03 | L | todo |
| T-025 | RPT — Schema Representations of Cybersecurity Information | #9 · Maimcghee | L | todo |
| T-026 | RPT — Knowledge Graph Visualization & Review Console | #10 · kriishnaa-18 | M | todo |
| T-027 | Extraction: ISO/SAE 21434 & TARA requirements + object model | #11 · Clovier | L | **doing** (record + 118-req catalog in; verify vs FX-1) |
| T-030 | RPT — Agentic Threats & Weaknesses | #12 · paria03 | L | todo |
| T-031 | Extraction: SAGAI (Secure AI) & related specifications | #13 · Maimcghee | M | todo |
| T-032 | RPT-0001 umbrella landscape — reconcile with the per-topic reports | — | M | todo |
| T-028 | Define target use cases; draft DEC-005 options with evidence | all | M | **doing** |

## I1b — Extraction standard (cross-cutting, high priority)

| id | task | own | sz | status |
|---|---|---|---|---|
| T-029 | **FX-1 full extraction** of applicable spec records (not summaries): requirements, schemas, message/object formats, state machines, examples-as-fixtures, decision mapping. Multi-agent extract → adversarial verify → cross-check, **each pass at max effort**. First targets: the ~28 KG/OKN reference records (currently `summarized` → stub or FX-1), ISO 21434, FIPS 140 family. Follow `library/docs/extraction.md` + `extract` skill; `bin/extract-scaffold`. | nymble + all | L | **todo** |

## I2 — Model · Oct 14–27

| id | task | issue | sz | status |
|---|---|---|---|---|
| T-040 | ARCH-0001 → v0.2: core object model (input to DEC-001) | #15 | L | **doing** (PROPOSAL proposed.5: iter-4 + sponsor display/redundancy round, §10) |
| T-041 | `spec/schema/` first draft (LinkML?) importing one existing format; a round-trip vector | #16/#17 | L | todo |
| T-042 | CWE/NVD integration design (DEC-008) | #17 | M | todo |
| T-043 | Risk-metric survey → DEC-003 direction (CVSS / ISO 21434 / CC feasibility) | #14 | M | todo |
| T-044 | RDF-vs-LPG + PROV-O/SHACL/STIX decision, from RPT-0011 gap analysis | #17 | M | todo |
| T-045 | Application requirements (APP-0001): product shape, GUI/platform/perf/CLI, radar vs tmodel split | #18 | M | **doing** (APP-0001 draft in; hardens after RPT-0012) |
| T-046 | RPT-0012 — GUI, platform & implementation stack | #10 | L | **review** (direction decided → Path A; residual = A-044 viz comparison) |
| T-047 | DEC-006 + DEC-010 — stack & language | #18 | M | **done** (ADR-0003, Path A) |

## I3 — MVP core (demo floor Nov 5) · Oct 28–Nov 5

| id | task | issue | sz | status |
|---|---|---|---|---|
| T-060 | Interactive graphical threat model + threat-chain view (DEC-006) | #10 | L | todo |
| T-061 | Human review/annotation model wired: impact, accept/reject, rationale (R-018…R-021) | #15/#17 | L | todo |
| T-062 | End-to-end on one worked example (input → graph → review → risk) | — | L | todo |

## I4 — Risk & mitigation · Nov 6–19

| id | task | issue | sz | status |
|---|---|---|---|---|
| T-080 | Risk metrics computed per product/environment (DEC-003) | #14 | L | todo |
| T-081 | Mitigation mappings; generic→product & product-family mapping (R-020) | #19 | L | todo |
| T-082 | Mitigation tracking over the design lifecycle (R-021) | #19 | M | todo |
| T-083 | NVD lookup automation (DEC-008) | #17 | M | todo |
| T-084 | Automated compliance validation — requirement/work-product/audit model | #19 | M | todo |

## I5 — Integrate & demo · Nov 20–Dec 5

| id | task | own | sz | status |
|---|---|---|---|---|
| T-100 | Vectors green; docs; published site | all | M | todo |
| T-101 | Demo script + dry run | all | M | todo |

## I-App — Path A application (ADR-0003) · parallel track

The desktop app, built as progressive vertical slices (ADR-0003). Cadence per slice:
**design → documents → code → build → test → validate → GUI integrate → review → plan
next.** Progressive UI: **tables → KG browse → threat chains → WebGL.** Local-only; no
remote servers. Tracking epic: the GitHub "Path A" issue. Slices 0–3 are the spine; Slice
4 is the ADR-0002 interactive attack-path graph.

| id | task | issue | sz | status |
|---|---|---|---|---|
| T-200 | **Slice 0 — scaffolding**: Tauri+TS shell, Python engine package, local API `health`, CLI stub, CI build/test (no cloud) | Path A epic | M | todo |
| T-201 | **Slice 1 — tabular filter UI**: tables of filter info, sample → live; `tmodel filters list` | Path A epic | M | todo |
| T-202 | **Slice 2 — KG browse/query**: browse/query through the store façade; CLI parity. **Logical edges pinned (ADR-0004); DEC-004 = substrate only** | Path A epic | L | todo |
| T-203 | **Slice 3 — threat chains/paths**: compute + display chains (tabular + linked); CLI path cmd | Path A epic | L | todo |
| T-204 | **Slice 4 — WebGL graph viz**: interactive graph; pick viz lib under A-044; chain highlight | Path A epic | L | todo |
| T-205 | **Slice 5 — polish, packaging, agent CLI recipes**: Mac build/signing, loopback hardening | Path A epic | M | todo |
| T-206 | App toolchain in CONTRIBUTING (current Node, Python ver, Tauri deps; harness node-v8 ≠ product) | Path A epic | S | todo |
| T-207 | **Edge Rich KG — loader**: rebuild working store from git SoT (YAML/JSON + link records) | #51 | M | todo |
| T-208 | **Edge Rich KG — edge façade**: typed edges w/ properties; LPG + RDF-star/reified adapters, no ID churn | #52 | L | todo |
| T-209 | **Edge Rich KG — export generators**: Turtle / JSON-LD / GraphML / CSV (non-canonical) | #53 | M | todo |
| T-210 | **Edge Rich KG — docs sync**: ADR-0003 + Slice 2 cite ADR-0004; DEC-004 scoped to substrate | #54 | S | todo |
| T-211 | **CI/CD**: lint + test + build (TS + Python), PR-gated, no cloud (PLAN-0002 Track A) | #47 | M | todo |
| T-212 | **Packaging + signing + download**: `tauri build` → signed `.dmg` → GitHub Releases (PLAN-0002 Track A) | #47 | M | todo |
| T-213 | **CWE lossless import**: merge 3 CWE views (699/1000/1194) losslessly into `Weakness`; allow non-MITRE `tr-weak-*`; reconciliation test (PLAN-0002 §5) | #47 | L | todo |
| T-214 | **Library ↔ weakness-type link**: typed edge `record characterised_by Weakness` (PLAN-0002 B4) | #47 | S | todo |

## Parking lot

- ISO/SAE 21434 full risk analysis (high value, optional; may exceed one semester).
- Export to a common threat-model format (R-006).
- Rule-based scanning engine, if not chosen at DEC-005.
- **Federate tmodel into NSF OKN** (FRINK) — new decision surfaced by RPT-0011.
- **Curated upstream PR to m-of-n/library** (schema/process + shared refs) — deferred.
- Align SBOM/supply-chain record ids with m-of-n (both orgs now model these).
