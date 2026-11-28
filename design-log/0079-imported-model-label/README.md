---
schema: "archdoc/v1"
id: DL-0079
title: "Imported models: their own kind and label, by the im- prefix (#281)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0079
human_owner: Clovier
bears_on: [R-018]
defers_to: ARCH-0001
---

# DL-0079: the imported-model label

## Question asked

#281, from DL-0068's follow-ups: the app labels every `pv-` model "Proposal example (AI-drafted,
unreviewed)", but a model `tmodel import-sbom` writes (#257) is made by a tool from an SBOM and a
scan, not drafted by AI. How should the app tell an imported model apart, in the model list and
in the report's banner?

## What was produced

- **The kind:** `engine/engine/core.py` picks a model's kind from its file name (`MODEL_KINDS`).
  A file named `im-NN-*.yaml` is now the kind `imported`, labelled "Imported starter model (from
  an SBOM, unreviewed)", and the list shows it after the proposals.
- **The report banner:** `apps/desktop/src/report-render.ts` gives an imported model its own
  notice: it was imported by `tmodel import-sbom` from a container image's SBOM and its
  vulnerability scan, every link in it is proposed until a person reviews it, and it is a
  starter model, not a security assessment. The sentence about recorded reviews still comes from
  the model's Reviews, never from its kind.
- **The list's banner:** the Pages index of models (`apps/desktop/src/model-pages.ts`) says that
  some of its models were imported only when it lists one (`modelListNotice`); with none, as
  today, its text is unchanged word for word.
- **Opening and reviewing them:** `engine/engine/propose.py` adds `im-` to the model prefixes
  the engine's proposal functions accept (`MODEL_PREFIXES`). Without it the list showed an
  imported model, but the Graph tab's saved views (`GET /proposals`), `tmodel propose` and
  `tmodel accept` refused it as "not a model file", and the proposals list left it out.
- **The model picker:** `apps/desktop/src/model-catalog.ts` shows "Unreviewed" for an imported
  model with no accepted review, as it does for a proposal.
- **Three tests that walk spec/vectors:** `test_paths_vectors.py` and `test_graph.py` require
  every model they check to hold attack paths, so they leave `im-` files out, as they leave out
  SDL models (and the paths test `pv-` files): an imported model holds none until someone adds
  them. The order check in `test_models_surface.py` names every kind, so it now names
  `imported`. Without these, the first committed `im-` file would fail all three.
- **The schema check:** `.github/workflows/schema.yml` validates any `im-*.yaml` against the
  proposed container, as #292 does for `pv-*`, and passes when there are none.
- **The docs:** `spec/vectors/README.md` has a section for imported starter models, and the
  `kg-propose` skill names them as a target.
- Tests: `test_an_imported_model_has_its_own_kind_after_the_proposals` and
  `test_an_imported_model_is_proposed_to_and_accepted_like_the_others` (engine); in
  `report-render.test.ts`, "tells an imported starter model apart from a proposal drafted by AI"
  and "names imported models in the list's banner only when the list holds one"; and the
  picker's "Unreviewed" check in `model-catalog.test.ts`.

## Choices open to review

- **A file-name prefix, not a field in the model.** Every kind is already chosen by prefix, and a
  marker inside the model would need a schema addition the sponsor reviews. The prefix is short,
  like `mvp-`, `tv-`, `pv-` and `sdl-`.
- **Rejected:** `sbom-` (longer, though plainer), and keeping `pv-` with a marker in the file
  (the schema change above).
- **An imported model is a proposal target.** A person reviews its links as for a `pv-` model:
  an agent or a person proposes, and the sponsor decides with `tmodel accept`. A model the app
  opens but nobody can propose to would leave the importer's proposed links no way to be
  reviewed. Every collection the importer writes is already one a proposal may change, so the
  drift guard in `test_propose_v2.py` holds for it.
- **Not in this change:** the importer's `-o` help still suggests a `pv-` name on #268's branch;
  #287's route change on that branch makes it suggest `im-01-NAME.yaml`.

## How it was checked

- The engine suite, `ruff check` and `ruff format --check`.
- The app's typecheck, tests and build; the browser preview regenerated and
  `render_app.py --check` passes; the publishing tests, `check_links.py` and
  `check_identities.py`.
- A real imported model (#268's alpine fixture, made by `tmodel import-sbom` and saved as
  `im-01-alpine.yaml`), through every engine route the app calls for a model, on a local
  server. Before the prefix change, `GET /proposals` refused it as "not a model file" and the
  proposals list left it out. After it, `/models` labels it, `/graph` (92 nodes),
  `/attack-paths` (no threats) and `/proposals` all answer, and the list includes it.
- A copy of this branch with that model committed, as the first imported model will be. The
  new schema step validates it, `check-refs.py` resolves all 177 of its references, and the
  publishing checks pass with it published. The engine suite passes once the order check names
  the imported kind (this change; it failed before). Of the app tests, only the popover check
  in `canvas-layout.test.ts` failed, in one run of four; it fails at times on `main` too.
- `bin/validate-archdoc` and `git diff --check`.

## What a human accepted

- @Clovier, 2026-11-27: chose the `im-` prefix ("im- prefix (Recommended)", over `sbom-` and over
  a marker in the file) and asked for the label to be built; the wording and code are Claude
  Code's draft until the pull request review accepts them.
