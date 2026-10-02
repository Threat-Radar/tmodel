---
schema: "archdoc/v1"
id: PLAN-0002
title: "Application build plan — walking skeleton → library tables → knowledge graph"
short_title: "App build plan"
description: "The concrete build plan for the tmodel desktop app (Path A, ADR-0003). Pipeline-first: a rapid dummy 'walking skeleton' gets build/CI/CD/packaging/download green before any feature; then two parallel tracks — A (build/tooling/CI/CD/distribution) and B (data → library table views → knowledge graph), including the lossless CWE import. The edge-rich storage layer (ADR-0004) is a separable concern."
type: plan
category: application
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
needs_review: true
reviewed: false
canonical_path: project/PLAN-0002-app-build.md
defers_to: ARCH-0001
agent_notes: >
  The HOW-to-build companion to ADR-0003 (Path A stack) and ADR-0002 (MVP scope). Pipeline
  first: Phase 0 ships a signed, downloadable dummy app so CI/CD/packaging is proven before
  features. Then Track A (build/tooling/CI/CD/distribution) and Track B (data → tables → KG)
  run in parallel. The edge-rich storage/adapters (ADR-0004 / Edge Rich KG #50) are kept
  SEPARABLE — tables and the KG work against the engine façade, not a chosen substrate.
  "No slice started yet" — this is the plan, not the build.
---

# PLAN-0002 — Application build plan

**What this is.** The concrete, ordered steps to build the tmodel desktop application. It is
the HOW-to-build companion to **ADR-0003** (Path A stack: local-only macOS Tauri/TS + Python
KG engine + CLI), scoped by **ADR-0002** (MVP) and using **APP-0001** as the requirements.
It refines the slice sketch in ADR-0003 into a buildable sequence.

**Two principles.**
1. **Pipeline before features** — a rapid *walking-skeleton "dummy app"* makes build, CI/CD,
   packaging, signing, and download work end-to-end *before* a single feature. You never
   debug the toolchain and a feature at the same time.
2. **The edge-rich storage layer is separable** (ADR-0004 / Edge Rich KG #50). Tables and the
   KG view talk to the engine **façade**; whether the working store is LPG or RDF (DEC-004) and
   how edges are reified is behind that façade and does **not** gate the build or the UI.

```
Phase 0  Walking skeleton (dummy app) — pipeline green, downloadable
   │
   ├── Track A  Build / tooling / CI-CD / distribution         (separable from edges)
   │
   └── Track B  Data → library table views → knowledge graph   (uses engine façade)
                 └── CWE lossless import feeds the Weakness objects
   Edge layer (ADR-0004, #50) plugs in under the façade — parallel, not blocking
```

## 1. Repo layout (monorepo)

```
tmodel/                      (this repo)
  apps/desktop/              Tauri (Rust shell) + TypeScript frontend
  engine/                    Python KG engine package (pyproject.toml)
    engine/api/              local API (loopback HTTP/WS or IPC)
    engine/cli.py            CLI entrypoint (same engine)
    engine/store/            store façade + adapters (edge layer — ADR-0004)
    engine/load/             library loader + importers (CWE, …)
  .github/workflows/         CI (build + test, TS + Python; no cloud)
  CONTRIBUTING.md            app toolchain (current Node, Python ver, Tauri deps)
```
Spec/plan/research stay where they are. App code is new (`apps/`, `engine/`). The harness
`node` v8 constraint is **harness-only** — the app repo uses current Node (ADR-0003).

## 2. Phase 0 — Walking skeleton (the "dummy app"): get the build going

Goal: a **signed, downloadable macOS app that launches and says "connected to local engine"**
— with CI building and testing it — *before any feature*. Exit criteria below are the gate to
start Tracks A/B.

Ordered steps:
1. **Toolchain + CONTRIBUTING** — pin Node (current LTS), Python (3.11+), Rust/Tauri deps;
   document `npm install` / `pip install -e engine[dev]` / `npm run tauri dev` (T-206).
2. **Dummy Python engine** — `engine` package with a `health`/`version` endpoint over the
   local API (loopback); nothing domain-specific yet.
3. **Dummy CLI** — `tmodel health` / `tmodel version` calling the *same* engine (proves A-030
   boundary + A-060 CLI parity from day one).
4. **Dummy Tauri+TS window** — one window that calls `health` and shows "connected to local
   engine · vX".
5. **CI** (`.github/workflows/ci.yml`) — lint + unit test + build for **both** TS and Python,
   on PRs; **no cloud services** required (A-043). Keep `bin/validate-archdoc` for docs.
6. **Packaging** — `tauri build` → `.app`/`.dmg` on macOS; wire **signing/notarization**
   (needs the Apple Developer cert — see §6 open items; stub until then).
7. **Distribution/download** — publish the artifact to **GitHub Releases**; a teammate can
   download the dummy app and run it (A-046).

**Exit (Phase 0 done):** fresh-clone instructions work on a Mac; the signed app downloads,
launches, and shows engine health; CLI health hits the same engine; CI is green with no cloud.
(This is BACKLOG **T-200**, expanded — it is the whole pipeline, not just a code skeleton.)

## 3. Track A — Build / tooling / CI-CD / distribution (separable from edges)

Hardens Phase 0 into a real pipeline; independent of any feature or the edge layer.
- **Dependency & reproducibility** — lockfiles (TS + Python), pinned Tauri, deterministic build.
- **Versioning & release automation** — one version across app/engine/CLI; tagged GitHub
  Releases produce signed `.dmg` artifacts (T-212).
- **CI/CD matrix** — lint, type-check, unit + API-contract tests, build, package; PR-gated;
  **no cloud** (T-211).
- **Signing / notarization** — Apple Developer ID; notarize on release (gated on the cert).
- **Update channel** — how a user gets a new build (manual download for MVP; auto-update later).

## 4. Track B — Data → library table views → knowledge graph

Drives the first *useful* UI from real content. Each step works through the engine façade, so
the edge layer (ADR-0004) can land underneath without changing the UI.

- **B1 — Library load.** The engine reads **library records** (read-only) into the working
  store and exposes them as typed objects (weaknesses, vulnerabilities, attack patterns,
  standards, components, …). Loader lives in `engine/load/` (T-207). *Library content changes
  happen in the `library` repo, not this checkout (PROC-0001).*
- **B2 — Table views (the first screen).** Per-object-type **sortable / filterable / searchable
  tables** of the library objects — start with sample fixtures, flip to live (T-201). This is
  the "tables of the objects in the library" Paul asked for, and the fastest path to something
  real on screen.
- **B3 — Knowledge-graph view.** A graph over the same objects and their links (B4, CWE, BRON),
  starting as node/detail lists, then the interactive projection (T-202 → T-204). One
  projection for the MVP (ADR-0002); best-in-class viz is post-MVP (APP-0001 A-042).
- **B4 — Library ↔ weakness-type linking.** A library record (a component, a finding, a spec
  clause) can **link to a weakness type** (e.g. a CWE) via an explicit, edge-rich link (ADR-0004).
  Modeled as a typed edge `record —characterised_by→ Weakness`, stable IDs across encodings
  (T-214).

## 5. CWE lossless import — the Weakness data spine

Weaknesses/vulnerabilities are **populated for CWE losslessly**, merging the **three CWE
views** and **allowing weakness types not in MITRE** in our schema. (T-213.)

**Source — the "three tables" (confirm, §6):** the three primary CWE organizational views —
**CWE-1000 Research Concepts**, **CWE-699 Software Development**, **CWE-1194 Hardware Design**.
Each view organizes the *same* underlying CWE entries under *different* category hierarchies,
so merging all three gives full coverage and every parent/child relationship. The importer is
written to take **N views**, not exactly three, so adding CWE-1400 or a future view is trivial.

**Lossless rule.** Import each CWE entry **once** (keyed by CWE-ID) but **preserve every field
and every relationship from every view** — nothing is collapsed or dropped:
- **Entry fields:** name, abstraction (Pillar/Class/Base/Variant), structure, status,
  description, extended description, modes of introduction, common consequences, detection
  methods, potential mitigations, demonstrative/observed examples (incl. CVE refs), related
  attack patterns (CAPEC), and taxonomy mappings.
- **Relationships** (ChildOf / MemberOf / PeerOf / CanPrecede …) are kept **tagged by view**,
  because a CWE's parent differs between 699, 1000, and 1194. A single merged hierarchy would
  be *lossy*; we keep per-view edges.
- The **library record** for CWE keeps the full source (digest + extracted text) per the FX-1
  extraction standard — the import derives our objects *from* that record, it does not replace it.

**Our schema — `Weakness`** (engine object; substrate-neutral per ADR-0004):
```
Weakness {
  id            # "cwe-79"  | local "tr-weak-0001"
  source        # mitre-cwe | local
  name, abstraction, status
  descriptions  # short + extended
  consequences[], mitigations[], detection_methods[]
  relationships[] { type, target_weakness_id, view_id }   # per-view, lossless
  mappings[]    { scheme: capec|attack|taxonomy, ref }
  extensions    # free-form for local, non-MITRE weakness types
}
```
- **New weaknesses not in MITRE** use the `tr-weak-*` ID namespace and `source: local`, slot
  into the same type system and relationships, and are first-class alongside CWEs. (Home for
  radar findings, domain-specific or AI-proposed weakness types — the latter still subject to
  the "AI proposes → human reviews" rule.)
- **Vulnerabilities (CVE)** link to `Weakness` via the BRON backbone (`vulnerability —instance_of→
  weakness`), already modeled in ARCH-0001.

**Lossless validation (the acceptance test).** A reconciliation report proves nothing was lost:
imported entry count == union of entries across the three views; imported relationship count ==
the distinct `(entry, type, target, view)` tuples in the sources; a field-level diff flags any
unmapped CWE field. The import fails CI if the report shows loss.

## 6. The edge layer — separable (ADR-0004 / Edge Rich KG #50)

Everything above works against the engine **store façade**. The edge-rich model (typed edges
with properties; stable IDs across LPG / RDF-star / reified encodings; file canonical SoT;
local embedded working store; derived export) is **ADR-0004**, built as its own sub-tasks
(#51 loader, #52 edge façade, #53 export, #54 docs). It can land before, during, or after the
table/KG UI — the UI depends on the façade, not the substrate. **DEC-004** (RDF vs LPG) stays
open underneath.

## 7. Sequencing & backlog map

| phase / step | backlog |
|---|---|
| Phase 0 walking skeleton | T-200 (+ T-206 toolchain) |
| Track A CI/CD | T-211 |
| Track A packaging/signing/download | T-212 |
| B1 library load | T-207 (loader) |
| B2 table views | T-201 |
| B3 KG view | T-202 → T-204 |
| B4 library ↔ weakness link | T-214 |
| CWE lossless import | T-213 |
| edge layer (façade/export) | T-208 / T-209 (#52/#53) |

**Order:** Phase 0 first (gate). Then Track A hardening ∥ Track B (B1 → B2 → CWE import →
B4 → B3). Edge layer in parallel under the façade.

## 8. Open items (confirm before building)

- **"Three tables" = CWE views 699 / 1000 / 1194?** Confirm, or name the three sources. (The
  importer is N-view-general either way.)
- **Apple Developer cert / signing timeline** — gates notarized downloads (Phase 0 step 7);
  unsigned local builds work meanwhile.
- **Where the CWE importer lives** — `engine/load/` in this repo vs an ingestion step in the
  `library` repo. Proposed: the library holds the **records** (lossless source); the engine
  holds the **importer→objects**. Confirm the split.
- **Monorepo vs split** — `apps/` + `engine/` in this repo is assumed; split only if it earns it.
