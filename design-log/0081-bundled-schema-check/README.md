---
schema: "archdoc/v1"
id: DL-0081
title: "The schema check on every project save, without LinkML (#288)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0081
human_owner: Maimcghee
bears_on: [ADR-0004, R-018]
defers_to: ARCH-0001
---

# Question and scope

#288 asks the workspace to "validate the resulting model against the existing schema
before committing". DL-0075 (#298) runs that check with LinkML, which the packaged app
does not have. There, a save gets the engine's own checks only. This change makes the
schema check run in the packaged app too, and changes nothing else in DL-0075's design.

No `DEC-*` is decided here.

# What a save let through without LinkML

The 51 broken models below went through `save_version` on #298 (`9feec0a`) with
`schema_check=False`, as the packaged app runs it, and through `linkml-validate` 1.12.1
(`spec/schema/requirements.txt`).

- They are copies of `pv-01`, `mvp-02` and `tv-software-auth-service`, each unchanged and
  with up to 16 kinds of breakage.
- The breakages include unknown collections and fields, bad enums, missing or null ids,
  lists and scalars swapped, objects for references, nested `ImpactVector` errors, and
  Reviews added.
- **8 were saved as `v002` although `linkml-validate` rejects them:**
  - an unknown field in a record (`attack_paths[0].colour`), in all three models;
  - a number for an enum (`parties[0].party_kind: 3`), in all three;
  - a Review with no `reviews` or `reviewer` and the status `maybe`, in `pv-01` and `mvp-02`.
- The engine's own checks caught the rest. Three Reviews that LinkML accepts were refused
  because their reviewer does not exist; LinkML does not check that references resolve.

# What was built

- **`engine/schema_check.py`** checks a document against a container's LinkML YAML with
  no LinkML. It reads the same container files and the object model they import, and
  applies the part of LinkML those files use:
  - classes with `is_a`, `slots`, `attributes` and `slot_usage`;
  - slots with `range`, `any_of`, `multivalued`, `inlined`, `required` and `identifier`;
  - enums, and the `string`, `integer`, `boolean`, `date`, `datetime` and `uriorcurie`
    types.
- Like `linkml-validate`, every class is closed and a reference is only checked to be
  text. A schema that uses any other LinkML feature raises `SchemaError` when it loads,
  so a schema change cannot quietly weaken the check.
- **`ProjectWorkspace`** loads the four containers when it starts. Where it does not use
  LinkML (`schema_check=False`, or None without LinkML), it runs this check at DL-0075's
  step 3. If the schema cannot be loaded, the engine does not start with project
  folders on. `schema_validation` in `GET /workspace/models` is now always true.
- **`bin/build-engine`** bundles `spec/schema/tmodel-object-model.linkml.yaml` beside
  the containers, which import it from `../schema/`. Its new smoke step starts the built
  engine with `--projects` and fails the build if project folders do not start.
- With LinkML, nothing changes: LinkML runs, as in DL-0075.

# Rejected

- **Bundling LinkML, or `jsonschema` with the generated JSON Schema.** Both add large
  runtime dependencies to an app that bundles only `pyyaml` (`engine/pyproject.toml`).
  The generated JSON Schema also covers the object model, not the example containers.
- **Running both checks when LinkML is present.** They agree, so the second adds time and
  a second set of messages for no gain.
- **Leaving the gap as a known limit.** The packaged app is where people edit models, so
  that is where #288's check has to hold.

# Validation

- **The same 51 cases on this change:** 0 are saved while `linkml-validate` rejects them,
  and every one `linkml-validate` accepts is saved, except the three Reviews with a
  missing reviewer (above). Compared on its own, `engine/schema_check.py` gives
  `linkml-validate`'s verdict on all 51.
- **Every bundled example** fits its container: 4 core, 4 proposal, 2 worked and 1 SDL.
- **The packaged engine**, built with `bin/build-engine` on macOS arm64:
  - the build and its smoke steps pass;
  - `POST /workspace/host/open-file` on the built binary opens `pv-01`;
  - it refuses `pv-01` with `colour` on an attack path, or with `party_kind: 3`, with 422
    and `Schema check (ExampleModelProposed): ...`.
- **Tests:**
  - `test_schema_check.py` (24) covers the checker itself;
  - `test_model_workspace.py` adds the three kinds of breakage above, a bundle without
    the object model failing at start, and `bin/build-engine` bundling it;
  - two of DL-0075's invalid-document cases (a bad gate and a bad feasibility) are now
    caught by the schema check, so their `field` names the field, not `model`;
  - `contract.json` changes only in `schema_validation`.
- **Results:**
  - the whole engine suite on Python 3.13 without LinkML: 989 passed, 14 skipped;
  - the workspace and schema tests with LinkML 1.12.1: 175 passed;
  - the same tests on Python 3.11: 173 passed, 2 skipped;
  - `ruff check` and `ruff format --check` are clean.

# Human accepted / rejected

- @Maimcghee had this built for #288 while @Clovier's #298 was not yet pushed, then moved
  it onto #298 as a follow-up. @Clovier's DL-0075 design is unchanged.
- No human has reviewed this code yet.
