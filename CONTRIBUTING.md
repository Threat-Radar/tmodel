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

The engine serves the library's records from the pinned `library/` submodule, so
check it out first (`git submodule update --init library`), or set
`TMODEL_LIBRARY` to another library checkout. `tmodel library` lists the records,
and `--type`, `--topic` and `--status` filter them (#140).

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
copy to pick the change up. The sidecar includes the example models from
`spec/vectors/`. In the installed app, `/graph` resolves model filenames inside
the sidecar's unpacked resources, independent of the working directory. In a
source checkout it continues to read `spec/vectors/`. The examples are read-only
inputs; they are separate from the reference library and a user's working store.

**Run it:**

```sh
(cd apps/desktop && npm run tauri dev)
```

The app starts its bundled engine and stops it gracefully when you quit; the window says
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
runtime. The app also carries the Cytoscape MIT notice at
`tmodel.app/Contents/Resources/THIRD_PARTY_NOTICES.md`.

**Fast local review build.** `bin/build-dmg-local` runs the two steps above from
the current checkout after checking the prerequisites (macOS, Xcode command-line
tools, Python 3.11+, Node 22+, Rust), then prints `BUILD_SECONDS=` and the `.dmg`
path. About 3 minutes cold and 75 s warm on an Apple Silicon Mac, against about
9 minutes in CI. The result is ad-hoc signed, not notarized and has no
provenance: use it to look at a change, never to distribute. Releases come only
from `release.yml` (below). The history of the first release candidates and a
repair runbook are in `design-log/0035-release-history-2026-11-04/`.

**Releases and supply chain.** `.github/workflows/release.yml` builds the
`.dmg` on a GitHub-hosted macOS runner, checks the bundle, and publishes it with
a `.sha256` file and an SPDX SBOM (`.spdx.json`, taken from the lockfiles):

| trigger | result |
|---|---|
| tag `vX.Y.Z` (matching `version` in `tauri.conf.json`) | **draft** release that a maintainer reviews and publishes |
| tag `vX.Y.Z-rc.N` | draft **prerelease** |
| merge to `main` touching `apps/`, `engine/`, `spec/vectors/` or the build | rolling prerelease [`latest-main`](https://github.com/Threat-Radar/tmodel/releases/tag/latest-main): its tag moves to the new commit and its assets are replaced; the build is named `<version>-main.<sha7>` (#203) |
| manual run (`workflow_dispatch`) | workflow artifact only |
| pull request touching the app | `app.yml` uploads an ad-hoc-signed debug `.app` (zip) as a workflow artifact, kept 7 days (#205) |

The `build` job can only read the repository and mint an OIDC token; it signs a
[SLSA build provenance](https://slsa.dev/spec/v1.0/provenance) attestation for
the `.dmg`, the bundled engine (`tmodel.app/Contents/MacOS/tmodel-engine`) and
the SBOM with `actions/attest-build-provenance` (Sigstore, stored on this repo).
A separate `publish` job, which never runs build tools, holds the token that
writes releases. All third-party actions are pinned to commit SHAs; checkouts
do not keep their token; `npm ci` and `cargo fetch --locked` hold the build to
the lockfiles. With the `APPLE_*` secrets listed in the workflow the app is also
signed with a Developer ID and notarized; without them it stays ad-hoc signed.
Dependency installation runs before signing credentials are exposed; credentials
are scoped to the app build step.

*SLSA level: Build L2* (hosted build platform, signed provenance that anyone can
verify), with most of L3's isolation from GitHub-hosted runners and the split
jobs. It is not L3: the provenance comes from a step inside the build job, not
an isolated reusable workflow, and the build is neither hermetic nor
reproducible (rust, npm and pip caches; a floating `stable` Rust toolchain;
engine dependencies installed without hashes). Not signed with a Developer ID
yet, so Gatekeeper cannot vouch for it; the provenance is the integrity check.

*Download and verify* (needs the GitHub CLI, `gh`):

```sh
gh release download latest-main -R Threat-Radar/tmodel -p '*.dmg' -p '*.sha256'   # or a version tag
shasum -a 256 -c tmodel_*_aarch64.dmg.sha256
gh attestation verify tmodel_*_aarch64.dmg -R Threat-Radar/tmodel
# after installing, the engine inside the app verifies too:
gh attestation verify /Applications/tmodel.app/Contents/MacOS/tmodel-engine -R Threat-Radar/tmodel
```

`gh attestation verify` checks that the file was built by a workflow in this
repository and prints the workflow, commit and trigger. Then open the `.dmg`,
drag tmodel to Applications and, on first launch, use **Open Anyway** (below).

**Packaging acceptance (#124).** Keep the issue open after the implementation
merges until a test version tag has produced the draft release and a downloaded
installer has been checked on a clean Mac or fresh user account. On normal quit,
stdin closes so the engine and its PyInstaller launcher can exit and remove the
unpacked runtime. The app waits up to ten seconds for termination. Check three
launch/quit cycles for new `_MEI*` leftovers, confirm the engine port is released,
and check startup with the port already occupied. `bin/build-engine` also reads
an example model with the bundled engine in an empty environment, exercising
PyYAML and attack-path computation without a system Python. Both app CI and the
release workflow verify the bundled notice and test the installed sidecar. The
tests copy only the executable to a temporary directory, clear its environment,
load the bundled MVP-01 and MVP-02 graphs through the local API, and pass the
returned model path to attack-path enumeration. They check review metadata,
directory confinement, and runtime cleanup after exit. Run them locally with:

```sh
TMODEL_PACKAGED_ENGINE="$PWD/apps/desktop/src-tauri/target/release/bundle/macos/tmodel.app/Contents/MacOS/tmodel-engine" \
  engine/.venv/bin/python -m pytest -q engine/tests/test_packaging.py
```

This automated isolation check complements the downloaded-installer check on a
clean Mac; it does not verify Gatekeeper or replace that manual acceptance step.

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
