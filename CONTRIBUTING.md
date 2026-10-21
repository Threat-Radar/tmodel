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

---

## 10. The desktop app and engine — toolchain

The application (ADR-0003, ADR-0009; PLAN-0002) lives in two folders:

```
engine/          Python engine package `tmodel-engine` (local API + `tmodel` CLI)
apps/desktop/    Tauri desktop app: Rust shell (src-tauri/) + TypeScript frontend (src/)
```

The window and the CLI both talk to the engine through its **local API** on
`127.0.0.1:47811` (override with `TMODEL_ENGINE_PORT`). It never listens on a
network address. The harness's Node v8 pin does **not** apply here; the app uses
current Node.

**Prerequisites (macOS)**

| tool | version | install |
|---|---|---|
| Xcode command-line tools | current | `xcode-select --install` |
| Python | 3.11 or newer | python.org or Homebrew |
| Node.js | 22 LTS | nodejs.org or Homebrew |
| Rust | stable | `brew install rustup && rustup default stable`, then add `$(brew --prefix rustup)/bin` to `PATH` (or use rustup.rs) |

**First-time setup** (from the repo root):

```sh
python3 -m venv engine/.venv
engine/.venv/bin/pip install -e "engine[dev]"     # installs the `tmodel` command
bin/build-engine                                  # the engine as one executable (the app bundles it)
(cd apps/desktop && npm ci)
```

`bin/build-engine` (PyInstaller, pinned in `engine/packaging/requirements.txt`)
writes `apps/desktop/src-tauri/binaries/tmodel-engine-<target>`, which the Tauri
build requires. Re-run it after changing the engine if you want the app's own
copy to pick the change up.

**Run it:**

```sh
(cd apps/desktop && npm run tauri dev)
```

The app starts its bundled engine and stops it when you quit; the window says
**"starting local engine…"** for a few seconds, then **"connected to local engine ·
v0.1.0"**. If a tmodel engine is already answering on the port, the app uses it
instead, so while you work on the engine, run it from source in a second terminal
first: `engine/.venv/bin/tmodel serve`. If another program holds the port, the
window says so. `tmodel health` and `tmodel version` query the same engine from
the terminal (`--json` for scripts, `--in-process` without a server).

**Build the installer** (`.app` and `.dmg`, Apple Silicon):

```sh
bin/build-engine
(cd apps/desktop && CI=true npx tauri build)
# -> apps/desktop/src-tauri/target/release/bundle/dmg/tmodel_<version>_aarch64.dmg
```

`CI=true` skips the step that asks Finder to lay out the `.dmg` window, which fails
when the terminal may not control Finder. Without an Apple certificate the app is
ad-hoc signed (`signingIdentity: "-"` in `tauri.conf.json`); `Entitlements.plist`
lets the one-file engine load the Python it unpacks at launch under the hardened
runtime.

**Releases.** Pushing a tag `vX.Y.Z` (matching `version` in `tauri.conf.json`;
`vX.Y.Z-rc.N` for a test) runs `.github/workflows/release.yml`: it builds the
`.dmg` on a macOS runner, checks it, and attaches it with a SHA-256 file to a
**draft** GitHub Release that a maintainer publishes. With the `APPLE_*` secrets
listed in that workflow it also signs with a Developer ID and notarizes; without
them the app stays ad-hoc signed.

**Opening a build that is not signed with a Developer ID.** macOS refuses to open
it on first launch and says it cannot verify the app. Close that dialog, then open **System
Settings → Privacy & Security**, scroll to **Security**, click **Open Anyway** next
to tmodel and confirm. The button appears only for a while after the blocked
attempt. On macOS 14 and earlier, Control-click the app and choose **Open**
instead; macOS 15 removed that shortcut. This is needed once per download.

**Before you open a PR that touches `engine/` or `apps/`** — the same checks CI
runs in `.github/workflows/app.yml`:

```sh
(cd engine && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q)
(cd apps/desktop && npm run typecheck && npm test && npm run build)
(cd apps/desktop/src-tauri && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test)
```

Changes under `.github/` are routed to the sponsor for review (`CODEOWNERS`).
