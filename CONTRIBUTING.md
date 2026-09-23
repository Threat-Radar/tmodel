# Contributing to tmodel

Four students, a sponsor, and a faculty advisor, mostly async. The repo is the
record: **if it is not in the repo, it did not happen.** Zoom and chat decide;
the repo remembers.

---

## 1. The ladder

Escalate only when the rung below has failed.

| Channel | For | Expectation |
|---|---|---|
| **Issues** | All work. One per task, labelled, on a milestone | Every task is an issue before it is code |
| **Pull requests** | All changes. No direct pushes to `main` | Review within 24h on weekdays |
| **Discussions** | Open design questions, `DEC-*` debates | Resolved into an ADR, then closed |
| **Weekly Zoom** | Decisions, unblocking, increment demo | 30 min; notes committed the same day |
| **Chat/SMS** | Blocked >24h, or a schedule change | Escalation only — **never content** |

---

## 2. Branches

```
main                     protected. no direct pushes, ever
topic/<topic-id>         research and library work
feat/<short-name>        implementation
doc/<doc-id>             architecture and planning documents
fix/<short-name>         corrections
```

Branch names carry the topic or document id so a reviewer knows the blast radius
before opening the diff. One topic per branch.

---

## 3. Worktrees — parallel work without collisions

A worktree is a second checkout of the same repo on a different branch, in a
different directory. One clone, one object store, as many working copies as you
have parallel threads. No stashing, no mid-task branch switching.

```sh
bin/wt new topic/landscape-methodologies   # create + prints the path
bin/wt list                                # what is checked out where
bin/wt rm  topic/landscape-methodologies   # remove when merged
```

Under the hood: `git worktree add ../tmodel-wt/<branch> -b <branch>`.

Rules:
- **Never work inside `library/`.** It is a submodule checkout on a **detached
  HEAD**; commits there belong to no branch and are trivially lost. Open the
  `library` repo directly (PROC-0001 §1).
- Worktrees live in `../tmodel-wt/` — outside the repo, so they are never committed.
- One branch per worktree; git enforces this.
- `bin/wt rm` when the branch merges. Stale worktrees hold locks.

---

## 4. Pull requests

Open a **draft PR on day one of an increment.** A draft PR is the progress
signal; a status message is not.

Every PR states: **what changed / why / how tested / which deliverable.** The
template asks for exactly that.

**Review:**
- One approving review to merge. The four students are Owners and review each other.
- `CODEOWNERS` routes `spec/**` to the sponsor — the normative surface.
- Comment on the line, not in chat. A line comment survives; a text does not.
- **Suggested changes** for anything under ~5 lines.
- Resolve a thread only when the change is pushed.
- Small and reviewable beats big and correct. One PR per deliverable slice.

**Merging:** squash merge, linear history. Delete the branch. `bin/wt rm <branch>`.

---

## 5. Architecture changes serialize

`spec/ARCH-0001-*.md` is the source of truth. Per its §9:

- Edit **in place** for additive clarification; bump `version` and `updated`
  **together**, and append to the changelog. CI enforces this.
- An accepted decision becomes `ADR-NNNN-*.md`, a changelog line, and a status
  update in ARCH-0001 pointing at the ADR.
- **Never mark a `DEC-*` accepted** in a PR description, a Zoom note, or a commit
  message. Only an ADR accepts a decision.
- Never open two PRs that both change the model. Serialize.

---

## 6. Document conventions

Every document under `spec/` and `project/` carries `archdoc/v1` front matter
(OKF-aligned: YAML front matter over Markdown, human- and agent-readable) and is
validated by `bin/validate-archdoc` in CI.

```
ARCH-NNNN   architecture / object model    ADR-NNNN   accepted decisions
MAP-NNNN    interchange mappings           PLAN-NNNN  execution
PROC-NNNN   process                        BACKLOG    tasks
DECISIONS   open-decision register         GLOSSARY   terms
```

`bin/new-doc <kind> <slug> "<title>"` scaffolds correct front matter.

---

## 7. Before you open a PR

```sh
bin/validate-archdoc          # front matter, version/updated coupling
git submodule status          # library pin intentional (once wired)
cd library && bin/validate    # library records (once wired)
```

CI runs the archdoc check. Running it locally means you find out in 3 seconds.

---

## 8. First-time setup

```sh
git clone --recurse-submodules https://github.com/Threat-Radar/tmodel
cd tmodel
```

**Wiring the library submodule** (done once, by a maintainer, after the
`Threat-Radar/library` fork exists):

```sh
git submodule add https://github.com/Threat-Radar/library.git library
git commit -m "Add library submodule (fork of m-of-n/library)"
```

**Set your git identity to an address GitHub will accept.** If *Block command
line pushes that expose my email* is on (it is on by default), a push is rejected
with `email privacy restrictions`. Use your GitHub noreply address:

```sh
git config user.email "<id>+<login>@users.noreply.github.com"
git config user.name  "Your Name"
```

Use a repo-local setting (no `--global`).

## 9. Licensing and sign-off

Contributions are under the **DCO**; `git commit -s` adds the `Signed-off-by`
line. **Code is Apache-2.0; specifications and documents are CC-BY-4.0.** A
`LICENSE` file is added when the sponsor confirms the public-license choice (an
`agent_ask_first` item — see the vault `projects/tmodel.md`).
