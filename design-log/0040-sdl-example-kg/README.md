---
schema: "archdoc/v1"
id: DL-0040
title: "SDL example knowledge graph and the tmodel SDL page"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0040
defers_to: ARCH-0001
bears_on: [DEC-001b, DEC-009, R-040, R-041, R-042, R-043, R-044]
---

# SDL example knowledge graph and the "tmodel SDL" page

**Numbering.** DL-0040 is the next free number: 0035, 0036 and 0038 are taken by
open PRs (#207, #211), 0039 is on main. The log already has duplicate numbers
(0012, 0015, 0024 each used twice); this entry does not add one.

**Renamed 2026-11-07.** @nymble accepted ADR-0013 with the RPT-0013-OM names: `WorkProduct`
is now `Evidence` (collection `evidence_items`, ids `evidence:`, `evidence_kind`), and
`RequirementSet` is now `RequirementSource` (collection `requirement_sources`, ids
`requirement-source:`, `source_members`, predicates `*_requirement_source`). RPT-0013-OM has no
practice type, so `SdlPractice` keeps its name. The text below uses the original names.

## Request

@nymble asked on 2026-11-07: do we have a well-formed SDL schema that can publish
SDL tracking and status as HTML or in the Mac app? Build an example SDL knowledge
graph for this project and publish it as "tmodel SDL", a tight, repeatable view of
one selected SDL. The SDL is product-focused and links to the knowledge around it
(library records, research, vulnerabilities). Are the library's and research's best
practices codified in the schema? Is there a process for human review and selection
of SDL delivery items and milestone names, and for selecting the governing
requirements (CRA, ISO/SAE 21434, ...)? Is the process written down for an agent,
or in the app? Should the app have an AI hook to build and edit graphs?

## Survey (repo state at c29a6a4, 2026-11-07)

| Question | Answer | Evidence |
|---|---|---|
| SDL schema that can publish status | **Partial** | `SecurityProgram`, `ProgramNode` (`Gate`, `Milestone`, `Checkpoint`), `GateStatus`, `ThreatModel`, `GovernedView` exist in `spec/schema/tmodel-object-model.linkml.yaml` but are DEC-001b, **not accepted** (ADR-0010/0012 accept only the core and `Requirement`). There is no class for an SDL practice or activity, a work product or evidence item, or a selected requirement set. One worked example (`tv-software-auth-service.yaml`) has no renderer, and the app has no SDL route or view. |
| Product-focused, linked to knowledge | **Partial** | `SecurityProgram.governs` a Product; `Requirement.source_ref` points into library records; `Weakness` / `AttackPattern` / `Vulnerability` carry CWE / CAPEC / CVE. Nothing links a practice to its evidence (repo paths, PRs, workflows). |
| Best practice codified in the schema | **No, docs only** | MAP-0001 (34 practices × 16 frameworks, `spec/MAP-0001.yaml`), RPT-0013 and RPT-0013-OM (46 canonical SDL object types, 60 relationships) are research. Only `Requirement`, `Normativity`, `RequirementKind` and `LifecyclePhaseCode` made it into the schema. The library's `requirements.yaml` files (SSDF, CRA, SLSA, ASVS, SAMM, ...) are referenced by id and never imported (ADR-0012). |
| Human review and selection of delivery items, milestone names | **Partial** | The Assertion + Review spine (ARCH-0001 §4) and `ProgramNode.decided_by` / `SecurityProgram.approved_by` can carry it, but no process doc, UI or check uses them for SDL. The TARA pilot (#178, #180 governance overlay, #185 gate check, DL-0027) is the nearest process; it is I4/I5 and for TARAs, not SDL items. |
| Selecting the governing requirement set | **No** | `Requirement.applies_to` / `applies_to_family` and MAP-0001 say which requirements could apply; nothing records which sets a product selected, rejected or deferred, or why. DEC-009 (generic → product mapping) is open. |
| Agent markdown; app AI hook | **No** | `.claude/skills/` is empty. `docs/publishing/SKILL.md` covers publishing only; `CLAUDE.md` sets the rule that AI output is a proposal until a human accepts it. The app and engine call no model (`apps/desktop/src`, `engine/engine`): there is no AI hook to build or edit graphs. |

## Produced

- `spec/vectors/example-container-sdl.linkml.yaml`: test-harness container = the full
  `ExampleModel` collections + three **proposal** classes kept out of `spec/schema/`
  (as #180 asks for governed-layer changes):
  - `SdlPractice`: `practice_key` (a MAP-0001 row), `at_phase`, `owner`,
    `mitigation_status` (reused enum), `implements` (Requirement), `produces`
    (WorkProduct), `in_program_node`, `external_refs`.
  - `WorkProduct`: `locator` (URL or repo path), `work_product_kind`, `evidence`.
  - `RequirementSet`: `source_ref` (library record), `source_locator`, `set_members`,
    `applies_to_family`.
  No status or selection fields were added. Selection goes through Assertions with
  the predicates `selects_requirement_set`, `considers_requirement_set`,
  `excludes_requirement_set`, `selects_practice` and `proposes_milestone_name`, plus a
  Review. An Assertion with no Review is a proposal.
- `spec/vectors/sdl-01-tmodel-desktop.yaml`: the tmodel desktop app's SDL as EXAMPLE
  DATA. It has 18 practices across six phases, with status from repo evidence
  (release pipeline, SLSA L2, SBOM, pinned actions, branch protection, CI tests, safe
  YAML loading, the missing SECURITY.md and Developer ID). It also has 4 program nodes
  (MVP launch 2026-11-06, I4, a v0.1.0 release gate, I5); 6 candidate requirement sets
  (SSDF and SLSA L2 proposed as selected, CRA and OSPS as candidates, ISO/SAE 21434 and
  IEC 62443-4-1 as not applicable, with rationale); and a 4-threat seed threat model
  with CWE/CAPEC. Every selection is `proposed` and `reviews: []`.
- `docs/publishing/render_sdl.py` + `docs/publishing/sdl.yaml`: renders
  `docs/sdl/index.html` ("tmodel SDL"). The page shows a header with the product and
  its requirement sets, practices by phase (status, owner as a role, evidence links,
  MAP-0001 framework ids for the selected and candidate sets, selection state),
  milestones, the threat model and gaps, plus the MAP-0001 rows the program does not
  cover yet. It is static, with no scripts. The renderer fails on a dangling id, an
  unknown MAP-0001 row or an unknown status, and has a `--check` mode. It is wired
  into `bin/publish-site` and `site.yaml`, and linked from the SDL report.
- `schema.yml` validates `spec/vectors/sdl-*.yaml` against the SDL container.

## Choices and limits

- **Owners render as roles.** No github id is cleared for publication in
  `publishing/identities.yaml`, so the page says "sponsor", "student", "student team".
  The YAML keeps the github ids.
- **Owners are proposals.** Where an issue already assigns the area, the owner is that
  person (@paria03, attack-path review). Elsewhere it is a role. The team picks.
- **Status is AI-drafted from repo evidence** on 2026-11-07 and not reviewed.
- **Not a conformance claim.** The framework ids per practice are MAP-0001's
  crosswalk cells (draft, `needs_review: true`), not an assessment of tmodel.
- **ISO/SAE 21434** appears only as a set id, record link and the scope reasoning;
  no clause text (#154).
- **CRA applicability** (open-source, non-commercial) is left as a human/legal call.
- **Mac app.** `collect()` returns plain data in the shape an engine route would serve
  (`GET /sdl?program=<id>` beside `/graph` and `/library/table`). The desktop app could
  render the same tables. Not built here.

## Recommended next steps (proposals)

1. Schema: fold `SdlPractice` / `WorkProduct` / `RequirementSet` (or RPT-0013-OM's
   Activity / Evidence / RequirementProfile) into the DEC-001b proposal and decide
   DEC-001b. Size M.
2. Process: a one-page SDL selection procedure. A human Review accepts or rejects each
   `selects_*` / `proposes_milestone_name` Assertion, and the page shows the decision.
   Reuse the #180 governance overlay shape. Size S.
3. Agent skill: `.claude/skills/sdl/SKILL.md`. It covers how to propose practices, sets
   and milestones as Assertions, never write Reviews, run the renderer and open a PR.
   Size S.
4. App: engine `GET /sdl` + a read-only SDL table view. The AI hook proposes
   Assertions only and is accepted through the existing review status UI. Size M to L.

## Human review

Pending. Nothing here is accepted; the PR is not to be merged without @nymble.

## Validation

- `linkml-validate -s spec/vectors/example-container-sdl.linkml.yaml -C ExampleModelSdl spec/vectors/sdl-01-tmodel-desktop.yaml`: no issues.
- `python3 docs/publishing/render_sdl.py --check`: fresh.
- `check_identities.py`: clean. `check_links.py`: every relative link resolves.
- `bin/validate-archdoc`: passes.
