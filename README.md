# tmodel

A local threat-modeling prototype. Explore example products and components,
inspect their threats and mitigations, and follow attack paths with recorded
human-review status. The desktop app and command line use the same Python engine.

A one-semester senior team project, with an early working demo and continued
development toward the December MVP.

Extends the 2025 *Threat Radar* master's work (container / dependency composition
analysis — [`Threat-Radar/tradar`](https://github.com/Threat-Radar/tradar)) and
reuses the [`library`](https://github.com/Threat-Radar/library) knowledge graph.

**Download:** [latest macOS test build](https://github.com/Threat-Radar/tmodel/releases/tag/latest-main) · **Project site:** [threat-radar.github.io/tmodel](https://threat-radar.github.io/tmodel/) · [bibliography](https://threat-radar.github.io/tmodel/bibliography/)

> **A threat model proves nothing on its own.** An AI-generated attack path is a
> hypothesis until a human with domain knowledge accepts it. Human review,
> annotation, and impact judgement are first-class here, not an afterthought.
> See [`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md).

## Status

**Working prototype.** The current main branch provides a library document table,
an interactive Knowledge Graph, and attack-path enumeration through the app,
local API, and CLI. Example models include software services and automotive
systems. The graph displays recorded accepted, rejected, and proposed states.

The views are read-only. Report-first presentation and model selection are in
review in [PR #211](https://github.com/Threat-Radar/tmodel/pull/211). Automatic
risk calculation, requirement coverage, and review/authoring workflows remain
under development. Ratings already present in example files are authored data.

## Try it in five minutes

### Download the desktop app (macOS, Apple Silicon)

1. Open the [latest-main release](https://github.com/Threat-Radar/tmodel/releases/tag/latest-main)
   and download its `.dmg`. The build name includes the source commit.
2. Open the installer and copy `tmodel.app` to Applications. No Python, Node.js,
   or Rust installation is needed to run it.
3. Open the app, wait for **connected to local engine**, and open the
   **Knowledge Graph** tab to explore the example and highlight an attack path.

These are development prereleases for Apple Silicon Macs; Windows and Linux
installers are not provided. Developer ID signing and notarization are pending.
See [CONTRIBUTING §10](CONTRIBUTING.md) for macOS's first-launch procedure and
checksum/build-provenance verification.

The engine includes the example model files. Reference-library documents require
a separate library checkout; the packaged Library tab can report that no library
is configured. The source quickstart below supplies the pinned library.

### Run from source in a browser (macOS or Linux)

Prerequisites: Git, Python **3.11–3.13** (the CI-tested versions), and Node.js
**22 LTS** with npm. The commands below use Python 3.13; substitute `python3.11`
or `python3.12` if that is your installed version. This browser preview does not
require Rust or a native app build.

In the first terminal:

```sh
git clone --recurse-submodules https://github.com/Threat-Radar/tmodel
cd tmodel
python3.13 -m venv engine/.venv
engine/.venv/bin/python -m pip install -e ./engine
(cd apps/desktop && npm ci)
engine/.venv/bin/tmodel serve
```

Leave the engine running. From the same repository root in a second terminal:

```sh
(cd apps/desktop && npm run dev)
```

Open one of these URLs:

| View | URL |
|---|---|
| Library document search | <http://localhost:1420/> |
| Software example (mvp-01) | <http://localhost:1420/?file=mvp-01-software-doc-service.yaml#graph> |
| Automotive example (mvp-02) | <http://localhost:1420/?file=mvp-02-automotive-ecu.yaml#graph> |

The `file` parameter selects the example; `#graph` opens the graph tab. Wait for
the engine connection, select a node for its details, and use **Highlight attack
path**. The mvp-02 infotainment pivot is marked **Rejected**; the diagnostic path
is recorded as accepted. In Library, search for `21434` to find reference records.

For an existing clone, run `git submodule update --init library` and reinstall
the engine and frontend dependencies after pulling updates. Stop each server
with **Ctrl+C** in its terminal. The engine listens only on `127.0.0.1:47811`;
the development frontend uses port `1420`.

### Check the engine from the command line

With the engine running, use another terminal at the repository root:

```sh
engine/.venv/bin/tmodel health
engine/.venv/bin/tmodel paths spec/vectors/mvp-02-automotive-ecu.yaml
engine/.venv/bin/tmodel paths spec/vectors/mvp-02-automotive-ecu.yaml --goal threat-instance:infotainment-pivot --json
```

For native development and building a `.dmg`, follow
[CONTRIBUTING §10](CONTRIBUTING.md), including its Rust and Xcode prerequisites.

## What the model tracks

The logical model covers these concepts. The accepted core type system is
recorded in ADR-0010, amended by ADR-0011 and ADR-0012; the decision table in
[`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md) identifies the
accepted and remaining open decisions.

| node | what it is | maps to |
|---|---|---|
| **Asset** | what damage happens to | — |
| **Component** | a part of the system (container, dependency, source module) | SBOM / composition |
| **Weakness** | a *class* of flaw | **MITRE CWE** |
| **Vulnerability** | a concrete instance of a weakness | **CVE / NVD** |
| **Threat** | an adverse action against an asset | — |
| **Attack step** | one atomic action an attacker takes | — |
| **Attack path / chain** | an ordered set of attack steps leading to damage | rendered as a graph |
| **Mitigation** | a control that reduces a threat | tracked per product |
| **Risk score** | feasibility, impact, mitigation status, and derived risk | ISO/SAE 21434 composite vector; Common Criteria display-only (ADR-0006) |
| **Review** | a human's verdict + assigned impact on any node | — |
| **Product / family** | what a generic threat is mapped onto | — |

Edges are **typed** (`exploits`, `mitigated_by`, `instance_of`, `step_of`,
`reviewed_by`, `applies_to_product`, …) — that is what makes the graph queryable,
e.g. *"every unmitigated attack path bearing on asset X in product Y."*

### Why track weaknesses and vulnerabilities, not just threats

A threat is a judgement; a weakness (CWE) and a vulnerability (CVE) are catalogued
facts. Keeping them as distinct, linked nodes supports the planned capabilities:

- **integrate MITRE CWE and automate NVD/CVE lookups**, instead of hand-listing risks;
- carry a **per-product mitigation status** — the same weakness can be mitigated in
  one product and open in another member of the same family;
- answer the lifecycle question **"is this weakness still mitigated in product X?"**
  as the design evolves, rather than rebuilding the model each release.

This dimension grows the graph fastest, and it carries a design implication: the
schema ([`spec/schema/`](spec/schema/)) and the `library` (which ingests
CWE / CAPEC / NVD as reference data) must treat weaknesses and vulnerabilities as
**durable, versioned, cross-linked** records — not transient scan output. Tracked
in ARCH-0001 as R-010 (CWE/CVE mapping + NVD automation) and R-021 (mitigation
lifecycle). The embedded-store direction is accepted in ADR-0008; automated
CWE/NVD integration remains tracked under DEC-008.

## Where to start

| document | what it is |
|---|---|
| [`spec/ARCH-0001`](spec/ARCH-0001-threat-model-architecture.md) | **Architecture — the source of truth.** Read first; its decision table links accepted ADRs. |
| [`project/PLAN-0001`](project/PLAN-0001-project-plan.md) | Semester execution plan, increments, demo |
| [`project/BACKLOG-0001`](project/BACKLOG-0001.md) | Tasks (`T-NNN`) |
| [`project/DECISIONS-0001`](project/DECISIONS-0001.md) | Decision register; consult ARCH and the ADRs for accepted decisions |
| [`project/PROC-0001`](project/PROC-0001-team-coordination.md) | Team lanes, who opens which repo |
| [`research/0001-threat-modeling-landscape`](research/0001-threat-modeling-landscape/report.md) | First research report — the competitive landscape |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branches, worktrees, PRs, review |
| [`CLAUDE.md`](CLAUDE.md) | Constraints for agents and humans |

## Layout

```
spec/          ARCH, ADR, MAP — the object model and architecture      (archdoc/v1)
spec/schema/   our threat-model schema; imports (and may export) existing formats
spec/vectors/  example threat models — the interop / regression contract
project/       PLAN, BACKLOG, PROC, DECISIONS, GLOSSARY — how we run it (archdoc/v1)
research/      versioned research reports; references land in library/
library/       submodule -> Threat-Radar/library (the knowledge graph)
engine/        Python engine, local API, CLI, and tests
apps/desktop/  TypeScript frontend and Rust/Tauri desktop shell
prototype/     throwaway spikes; never ships
design-log/    AI-assisted design record — what was produced, accepted, rejected
```

## The library is a submodule

`library/` is a fork of [`m-of-n/library`](https://github.com/m-of-n/library) in
the Threat-Radar org, vendored here as a submodule pinned to a commit so a report's
bibliography — and its CWE/CAPEC/NVD reference records — is reproducible as
`library@<commit>`. Expanding it is a named deliverable. **Never work inside
`library/`** from this checkout (detached HEAD); open the `library` repo directly.
See CONTRIBUTING §3.

The source quickstart initializes this pinned checkout. Library contributions
belong in the independent library repository and its own feature branch.
