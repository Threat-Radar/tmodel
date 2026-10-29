---
schema: "archdoc/v1"
id: DL-0023
title: "Generated JSON Schema, SHACL and Python types, and a CI check for the schema and vectors (#64)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-18"
updated: "2026-10-18"
record: DL-0023
bears_on: [DEC-001, DEC-002, DEC-004]
defers_to: ARCH-0001
---

# DL-0023: generated schema files and a schema CI job

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, working with Claude Code, taking this piece of #64 off @Maimcghee's plate (announced on #64).

## Question asked

#64 asks to "generate JSON Schema + SHACL + Python types; iterate via PRs; vectors validate against it". ADR-0007 says JSON Schema and SHACL "are generated from the LinkML (`gen-json-schema`, `gen-shacl`), never hand-authored". None of the three existed, and no CI job validated the vectors; DL-0021 ran the validators by hand.

## What was produced

- `bin/gen-schema`: runs the three generators on `spec/schema/tmodel-object-model.linkml.yaml` and writes `spec/schema/generated/`; `--check` exits 1 if a committed file is out of date.
- `spec/schema/generated/`: `tmodel-object-model.schema.json` (44 definitions), `tmodel-object-model.shacl.ttl` (2,268 triples), `tmodel_object_model.py` (pydantic models), generated from the file as it is on `main`.
- `spec/schema/requirements.txt`: the pinned tools (LinkML 1.12.1 and the libraries whose versions shape the output).
- `.github/workflows/schema.yml`: on changes to the schema, vectors or the script, checks that `generated/` is current, validates the four MVP core vectors against the core container and the two governance vectors against the full container, and runs DL-0021's reference resolver on the MVP vectors.
- `spec/schema/README.md`: a dated status line (the core is accepted; the paragraph below it predates that) and a "Generated files" section.

## Method and checks

- Each generator was run twice and from two working directories. JSON Schema and SHACL were byte-identical every time. The Python file records the source path it was given (`source_file`), so `bin/gen-schema` always runs from the repo root with a relative path.
- The generated files load: the pydantic module builds a `Component` with `identifiers`, `rdflib` parses the SHACL, and the JSON Schema parses.
- The CI steps fail when they should: `linkml-validate` exits 1 on a vector with a renamed `id` and a non-string `assertion_status`; the resolver exits 1 on a dangling reference; `--check` exits 1 when a generated file is edited.
- All six vectors validate on `main` (LinkML 1.12.1). `bin/validate-archdoc`: 0 errors.

## Choices made, open to review

- **The Python types stay in `spec/schema/generated/`,** not inside `engine/`. The engine is standard-library only on purpose (`engine/pyproject.toml`, easy to bundle, #124), and pydantic would be its first dependency. That choice belongs to the engine lane.
- **pydantic, not `gen-python` dataclasses.** The engine already speaks JSON over its local API, and pydantic validates on construction. `gen-python` would be the alternative if the engine lane prefers `linkml-runtime`.
- **The resolver is called from its design-log folder** (`design-log/0021-.../check-edges.py`), where DL-0021 committed it. Moving it to `bin/` would be tidier; it was left in place so DL-0021's record stays true.
- **Python 3.13 in CI,** the version the files were generated with; the job pins every tool that shapes the output.

## What was rejected, and why

Nothing yet; this waits on review by @Maimcghee (the lane owner) and @nymble (`spec/` and `.github/` under CODEOWNERS).

## What a human accepted

- The student chose to take this piece of #64 and asked for it to be done as a pull request.
- Pending: review.
