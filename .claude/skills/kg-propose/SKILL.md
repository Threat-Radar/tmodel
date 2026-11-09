---
name: kg-propose
description: Propose additions, edits or removals to a tmodel knowledge graph, an attack-path threat model (spec/vectors/mvp-*, tv-*, pv-*), an SDL model (sdl-*) or the saved KG views the Graph tab loads, as proposals only, with `tmodel propose`. For Claude Code, Grok Bot or any agent. An agent proposes; only the sponsor accepts, with `tmodel accept` in a pull request.
---

# KG propose: patch → proposal → sponsor decides in a PR

Design: `design-log/0046-ai-hook-v2-kg-threat-model-views/README.md` (v1 patches) and
DL-0044 (v0). Rules: `CLAUDE.md`, and `project/PROC-0002-sdl-review-and-selection.md` for SDL.
For SDL content (practices, evidence, requirement sources), also read `.claude/skills/sdl/SKILL.md`.

## Never

- Edit a model file (`spec/vectors/*.yaml`) yourself for a content change. Write a patch.
- Write a `Review`, set `assertion_status`, `review_status`, `approved_by` or `decided_by`,
  or run `tmodel accept`. That is the sponsor's command (@nymble only).
- Present a proposed object, edge or view as reviewed.
- Put a real name anywhere, or quote a licensed standard (paraphrase plus clause id).
- Merge, or commit on `main`.

## Steps

1. **Branch.** `git switch -c kg/<slug>` (or `bin/wt new kg/<slug>`).
2. **Look.** `tmodel proposals` lists the models with pending counts.
   `tmodel proposals mvp-01-software-doc-service.yaml` shows the pending proposals and saved
   views. `tmodel paths FILE` shows the attack paths. Add `--in-process` when no engine is running.
3. **Write a patch** (YAML). Examples: `engine/tests/fixtures/threat-patch-example.yaml` and
   `engine/tests/fixtures/sdl-patch-example.yaml`.
   ```yaml
   schema: tmodel.patch/v1
   target: mvp-01-software-doc-service.yaml   # a file in spec/vectors
   proposed_by: party:drafting-agent          # declare it under add.parties if it is new
   generated_by: "claude-code <version>, <run or session id>"
   rationale: One or two sentences: why.
   add:      {mitigations: [...], attack_steps: [...], views: [...]}
   edit:     [{collection: components, id: component:x, set: {description: ...}, unset: [...]}]
   remove:   [{collection: mitigations, id: mitigation:y}]
   assertions:                                # claims and relationships worth a review
     - {id: assertion:z, predicate: mitigates, subject: mitigation:new, object: threat-instance:t}
   ```
   - **Saved KG views** are `views` objects with `projection: graph` and a `focus_query`. The
     query is `START_ID -> step -> ...`, where a step is a collection (the nearest objects of
     that kind) or a relationship such as `composed_of*` (`*` repeats it). Text after `;` is
     a note.
   - An id never changes; to rename an id, remove the object and add a new one. Reviews cannot
     be added, edited or removed.
4. **Check, then write.** `tmodel propose patch.yaml --dry-run`, then `tmodel propose patch.yaml`.
   A refusal lists every problem and writes nothing. Common causes are an existing id, a dangling
   reference, a pending change to the same object, a decision key, or a view query that
   selects nothing. The proposal goes to
   `spec/vectors/proposals/<model>.proposals.yaml`; the model file is not touched.
5. **PR.** Commit the proposals file and open a PR with `gh pr create`. In the body, give the
   rationale, list each change, and ask the sponsor (@nymble) to decide. End the body with your
   attribution line. The desktop app shows the proposal under Graph › Pending proposals (or in
   the SDL tab), and a proposed view appears in Graph › Saved view as "Proposed: … (not reviewed)".

## The sponsor's step (not the agent's)

In the PR branch, the sponsor runs:

```sh
tmodel accept <proposal-id> --model <file> --reviewer party:nymble \
  --justification "why" [--verdict rejected|changes_requested] [--declare-sponsor nymble]
```

`accepted` applies the proposal to the model file. Only the touched blocks are rewritten and
comments are kept. Each Assertion is marked accepted and gets a Review by the sponsor.
`rejected` and `changes_requested` leave the model alone. Either way, the decision goes to
`spec/vectors/proposals/<model>.decided.yaml`. `tmodel accept` refuses to run on `main` and is
never an API route. After it runs, run the schema checks (`linkml-validate`, see
`.github/workflows/schema.yml`) and push to the PR.
