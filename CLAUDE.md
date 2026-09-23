# tmodel

Best-in-class threat modeling. Read this before touching anything.

## The one rule

`spec/ARCH-0001-threat-model-architecture.md` is the **source of truth** for the
object model and architecture. Everything else defers to it. Read it before
proposing anything.

**Every `DEC-*` is open.** No object model, schema encoding, risk-metric scheme,
or UI stack has been selected. Do not write code or documents that assume one.

## Never

- **Never mark a `DEC-*` accepted** anywhere except an `ADR-NNNN` file, with a
  changelog line and a status update in ARCH-0001. Not in a PR description, not
  in a commit message, not in a comment.
- **Never write a parallel architecture document.** Propose a diff against
  ARCH-0001 (`spec/ARCH-0001-*-PROPOSAL-*.md`), not a rival essay.
- **Never bump `version` without `updated`.** ARCH-0001 §9.5; CI enforces it.
- **Never commit a third-party PDF, spreadsheet, ebook, or vendor report.**
  Record the digest and locator in `library/`; see `library/CLAUDE.md`.
- **Never present an AI-generated threat or attack path as reviewed.** It is a
  hypothesis until a human accepts it, with the acceptance recorded (ARCH-0001
  on annotation and traceability). Impact judgement is a human input.
- **Never work inside `library/`** from this checkout — it is a submodule on a
  detached HEAD, so commits there belong to no branch and are trivially lost.
  Open the `library` repo directly (PROC-0001 §1).

## Layout

| | |
|---|---|
| `spec/` | ARCH, ADR, MAP, `schema/`, `vectors/` — normative, authored |
| `project/` | PLAN, BACKLOG, PROC, DECISIONS, GLOSSARY — execution, authored |
| `research/` | versioned reports; references go to `library/`, not inline |
| `prototype/` | throwaway spikes; never ships |
| `design-log/` | AI-assisted design record — see below |
| `library/` | submodule; has its own `CLAUDE.md` |

## The design log is not optional

This project claims **AI-assisted development** as part of its method. That is
only credible if it is instrumented. Any agent producing specification text,
schema, mappings, or vectors writes a `design-log/NNNN-slug/` entry: the question
asked, what was produced, and what a human accepted or **rejected and why**. The
rejections are the evidence.

## Before any PR

```sh
bin/validate-archdoc                 # front matter, version/updated coupling
```

Once the library submodule is wired (after the Threat-Radar/library fork exists):

```sh
git submodule status                 # pin is intentional, not accidental
(cd library && bin/validate)         # library records well-formed
```

Branch, worktree and review rules: `CONTRIBUTING.md`. Agents get their own
worktree — `bin/wt new <branch>` — so edits cannot collide. If you are about to
edit on `main`, stop and make a worktree.

## Skills — open the repo you are working in

Claude Code loads skills from the **project root only**, never through a
submodule and never from a parent. A session rooted at a parent workspace (e.g.
`~/cb`) gets **none** of this project's skills and nothing warns you.

| Working on | Open as project |
|---|---|
| architecture, plan, spec, backlog, research | **`tmodel/`** |
| library records, ingestion, summaries | **`library/`** |

Role skills for `tmodel/` are ported/authored in increment I0 (BACKLOG T-005);
until then `.claude/skills/` is intentionally near-empty. See PROC-0001 §1.

## Working agreement — every task

1. **End with clear next steps** — what happens next, who does it, what it unblocks.
2. **Open the PR in the browser when ready** (`gh pr view <n> --web`); don't
   describe a diff in chat and wait to be asked.
3. **The argument lives in the document, not the PR body.** If a reviewer would
   have to read the chat to follow the reasoning, the document is incomplete.
4. **Write the `design-log/` entry in the same change**, not afterwards.
5. **Use a worktree — always.** Multiple sessions run here at once.
