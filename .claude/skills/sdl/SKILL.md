---
name: sdl
description: Propose changes to a product's SDL knowledge graph (spec/vectors/sdl-*.yaml), such as practices, status, evidence, requirement sets and milestone names, then validate, re-render the "tmodel SDL" page and open a PR. Use it for any SDL tracking or status update. An agent proposes; it never reviews or accepts.
---

# SDL: propose, validate, render, PR

Rules: `CLAUDE.md` and `project/PROC-0002-sdl-review-and-selection.md`. Schema:
`SdlPractice`, `Evidence` and `RequirementSource` in `spec/schema/tmodel-object-model.linkml.yaml`
(ADR-0013). Example:
`spec/vectors/sdl-01-tmodel-desktop.yaml`.

## Never

- Write a `Review` of a selection, or set any `assertion_status` to `accepted` or `rejected`.
  Only a person does that (PROC-0002). `render_sdl.py` fails if you try.
- Mark a `DEC-*` accepted, or present AI-drafted status as reviewed.
- Put a real name anywhere. Use github ids or roles. Pages show roles only.
- Quote a licensed standard (ISO, IEC, SAE). Use a paraphrase plus the clause id.
- Merge, or edit on `main`.

## Steps

1. **Worktree.** `bin/wt new sdl/<slug>` (or `git switch -c sdl/<slug>` in your own checkout).
2. **Edit the YAML.** One object per list entry, ids `kind:slug`, and edges as id references:
   - Practice: `sdl_practices` entry with `practice_key` (a row key in `spec/MAP-0001.yaml`),
     `at_phase`, `owner`, `mitigation_status` (complete, in_progress, planned, accepted_risk,
     not_applicable), `produces` → work products, `in_program_node` → milestones.
   - Evidence: `evidence_items` entry with `locator` (repo path or URL) and `evidence_kind`.
     Status must match the evidence. Cite the file, PR or workflow.
   - **Any selection is a new Assertion**, with `subject` set to the program,
     `assertion_status: proposed`, `asserted_by: party:drafting-agent` (or your Party), an
     `asserted_at` timestamp and the reasoning in `description`. Predicates:
     `selects_requirement_source`, `considers_requirement_source`, `excludes_requirement_source`,
     `selects_practice`, `proposes_milestone_name`.
   - To change a decided selection, add a new proposed Assertion and leave the old one as it is.
   - With the engine available, `tmodel propose` writes proposals for you and refuses anything
     else (DL-0044). A `tmodel.patch/v1` patch can also edit or remove SDL objects, and can
     propose saved KG views; see `.claude/skills/kg-propose/SKILL.md` (DL-0046). The sponsor
     decides with `tmodel accept`; an agent never runs it.
3. **Validate.** Use the pinned tools (`pip install -r spec/schema/requirements.txt`):
   ```sh
   linkml-validate -s spec/vectors/example-container-sdl.linkml.yaml -C ExampleModelSdl spec/vectors/sdl-01-tmodel-desktop.yaml
   python3 docs/publishing/render_sdl.py          # re-render docs/sdl/; fails on dangling ids and review-rule breaks
   python3 docs/publishing/render_sdl.py --check
   python3 -B docs/publishing/test_render_sdl.py
   python3 docs/publishing/check_links.py && python3 docs/publishing/check_identities.py
   bin/validate-archdoc
   ```
   Fix the model, never the generated HTML.
4. **Design log.** Add a short `design-log/NNNN-slug/README.md` for anything beyond a status
   tweak: what was asked, what you proposed, and what is left for a human. Take the next free
   number, and check open PRs first (`gh pr list`).
5. **PR.** `gh pr create`. In the body, list each proposed Assertion and ask the decider (the sponsor,
   `@nymble`, only; faculty and students are not deciders) to accept or
   reject it per PROC-0002. Then `gh pr view --web`.
