---
schema: "archdoc/v1"
id: DL-0035
title: "Release history 2026-11-04 and repair runbook (rc.1, rc.2, latest-main)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-04"
updated: "2026-11-04"
record: DL-0035
defers_to: ARCH-0001
---

# Release history 2026-11-04 and repair runbook

A record of every build and release change made on Wed 2026-11-04, the state it
left behind, and the exact commands to undo or repair each one. Written so a
coding agent or student who was not there can orient, verify and fix. MVP
launch: Fri 2026-11-06. Sponsor: @nymble.

Times are Pacific (PST, UTC-8). GitHub stores UTC, so add 8 h to compare with
`gh` output. Every fact below was checked with `gh` or `git` when this was
written. Re-check before acting: tags and releases can move.

## 1. How to orient (read first)

| file | what it is |
|---|---|
| `.github/workflows/release.yml` | builds the `.dmg` on `macos-latest`, attests provenance, publishes drafts (version tags) and the rolling `latest-main` prerelease (push to `main`) |
| `.github/workflows/app.yml` | app CI; on PRs uploads an ad-hoc-signed debug `.app` artifact (7 days) |
| `bin/build-engine` | PyInstaller sidecar `apps/desktop/src-tauri/binaries/tmodel-engine-<triple>`; bundles `spec/vectors/` |
| `bin/build-dmg-local` | review-only local `.dmg` build on a Mac (added with this entry) |
| `apps/desktop/src-tauri/tauri.conf.json` | app `version` (tags must match), ad-hoc `signingIdentity: "-"`, bundled resources |
| `apps/desktop/src/engine-graph-provider.ts` | Graph tab data; `DEFAULT_MODEL_FILE` (line 12) hard-codes mvp-01 |
| `CONTRIBUTING.md` §10 | toolchain, "Releases and supply chain", download-and-verify |
| `design-log/0034-slsa-release-pipeline/` | DL-0034: why the pipeline looks the way it does |
| `design-log/0036-presentation-layer-reset/` | DL-0036: the presentation-layer problem found the same evening |

Rules that apply to any fix:

- Refer to people by **GitHub handle only** (`@nymble`, `@paria03`), never a real
  name, in files, commits, PR bodies and issue text (`CLAUDE.md`).
- Licensed standards (ISO/SAE 21434 and similar) are **paraphrased only**, with
  clause ids; never verbatim text.
- **Never merge without the sponsor's OK.** Open a PR and stop. Do not push to
  `main`. Steps marked **DESTRUCTIVE** below need explicit approval from
  @nymble before you run them.
- PR and issue bodies drafted by an agent end with the sponsor's attribution
  line. Copy it from the last line of #206's body; it is kept out of committed
  files.
- `git commit -s` (DCO). Run `bin/validate-archdoc`,
  `docs/publishing/check_identities.py` and `docs/publishing/check_links.py`
  before you push.

## 2. Timeline

| time (PT) | action | actor | reference |
|---|---|---|---|
| 09:12 | MVP readiness review posted: external-view punch list | @nymble | [#202](https://github.com/Threat-Radar/tmodel/issues/202) |
| 17:19 | Packaging fix approved and squash-merged: bundle graph models in the sidecar, license notice | @paria03 (author), @nymble (approve, merge) | [#201](https://github.com/Threat-Radar/tmodel/pull/201) → `a29aa06` |
| 17:20 | Tag `v0.1.0-rc.1` created on `a29aa06` (lightweight, via the refs API) | @nymble | run [41947795292](https://github.com/Threat-Radar/tmodel/actions/runs/41947795292) success 17:20–17:30 → **draft** prerelease, `.dmg` + `.sha256`, **no attestation** (the workflow had no attest step yet) |
| 17:20 | Issues opened: rolling latest-main `.dmg`; Pages browser preview; macOS build per PR | @nymble | [#203](https://github.com/Threat-Radar/tmodel/issues/203) (@paria03), [#204](https://github.com/Threat-Radar/tmodel/issues/204) (@kriishnaa-18), [#205](https://github.com/Threat-Radar/tmodel/issues/205) (unassigned) |
| 17:36 | Branch `feat/slsa-release` (`fdc939a`) exercised by `workflow_dispatch`; PR checks green | @nymble | run [41949643556](https://github.com/Threat-Radar/tmodel/actions/runs/41949643556) |
| 17:55 | SLSA release pipeline merged **with no approving review** (admin bypass; branch protection requires 1 approval, `enforce_admins` off). Sponsor's decision | @nymble | [#206](https://github.com/Threat-Radar/tmodel/pull/206) → `19442d7` |
| 17:56 | Tag `v0.1.0-rc.2` created on `19442d7` | @nymble | run [41951818365](https://github.com/Threat-Radar/tmodel/actions/runs/41951818365) success 17:56–18:05 → **draft** prerelease, `.dmg` + `.sha256` + `.spdx.json`, **attested** |
| 17:56 | Push to `main` triggered the rolling build | workflow | run [41951810115](https://github.com/Threat-Radar/tmodel/actions/runs/41951810115) success 17:56–18:08 → tag `latest-main` + **public** prerelease `tmodel latest-main (0.1.0-main.19442d7)`, `.dmg` + `.sha256` + `.spdx.json`, **attested** |
| evening | Local fast build on the sponsor's Mac mini (Homebrew `node@22`; scratch script, clone under `~/scratch/tm-build`): cold 190 s, warm ~75 s, vs ~9 min on `macos-latest`. Ad-hoc signed, not notarized | @nymble | not on GitHub; repo version is `bin/build-dmg-local` |
| evening | Sponsor opened the locally built app: "problematic … nonsense in the graph … we need a better presentation layer" | @nymble | DL-0036, new presentation-layer issue |

`ci`, `app` and `schema` on `main` were green for both `a29aa06` and `19442d7`.

## 3. State at the end of the day

| tag | points at | release | assets | attested |
|---|---|---|---|---|
| `v0.1.0-rc.1` | `a29aa06` | draft prerelease (not public) | `tmodel_0.1.0_aarch64.dmg`, `.sha256` | **no** (`sha256:c53856d8…cdd860` has no attestation) |
| `v0.1.0-rc.2` | `19442d7` | draft prerelease (not public) | `tmodel_0.1.0-rc.2_aarch64.dmg`, `.sha256`, `.spdx.json` | yes (`sha256:032d0e9f…66d5e2`) |
| `latest-main` | `19442d7` | **published** prerelease, not marked latest | `tmodel_0.1.0-main.19442d7_aarch64.dmg`, `.sha256`, `.spdx.json` | yes (`sha256:43e3e0d9…b7d9bc`) |

No release is published as a full release. `latest-main` is the only build any
visitor can download, and it moves with every merge to `main` that touches
`apps/`, `engine/`, `spec/vectors/`, `bin/build-engine` or `release.yml`.
All builds are ad-hoc signed (no Apple secrets), so macOS needs **Open Anyway**.
Merging this entry does not trigger the rolling build: it touches none of those paths.

Check the live state:

```sh
R=Threat-Radar/tmodel
gh release list -R $R
git ls-remote --tags https://github.com/$R
gh run list -R $R -w release --limit 10
```

## 4. Repair runbook

Pick the smallest step that fixes the problem. Every change to `main` goes
through a PR that @nymble approves. Steps that delete or move something
public are marked **DESTRUCTIVE: needs @nymble approval**.

### 4.1 Verify an artifact (read-only, always safe)

```sh
R=Threat-Radar/tmodel
gh release download v0.1.0-rc.2 -R $R -p '*.dmg' -p '*.sha256'      # or latest-main
shasum -a 256 -c tmodel_*_aarch64.dmg.sha256
gh attestation verify tmodel_0.1.0-rc.2_aarch64.dmg -R $R
# after installing, the engine inside the app:
gh attestation verify /Applications/tmodel.app/Contents/MacOS/tmodel-engine -R $R
```

Expected: rc.2 and latest-main verify and name `release.yml`, the commit and the
trigger. rc.1 **fails** to verify: it predates #206. Do not publish rc.1.

### 4.2 Stop the rolling `latest-main` build (PR)

Edit `.github/workflows/release.yml` so `push` fires on tags only. Remove
`branches: [main]` and the `paths:` list under it (path filters apply to branch
pushes only):

```yaml
on:
  push:
    tags: ["v*"]
  workflow_dispatch:
```

Open a PR; the `publish` step for `refs/heads/main` then never runs. Emergency stop,
which also stops tag builds: `gh workflow disable release.yml -R Threat-Radar/tmodel`
(**needs @nymble approval**; undo with `gh workflow enable`).

### 4.3 Delete or reset `latest-main` (DESTRUCTIVE: needs @nymble approval)

```sh
gh release delete latest-main -R Threat-Radar/tmodel --cleanup-tag --yes   # release and tag
```

The next qualifying push to `main` recreates both unless 4.2 landed first.
To rebuild it from the current `main` instead, re-run the newest `release` run on
`main`: `gh run rerun <run-id> -R Threat-Radar/tmodel`. It moves the tag to that
run's commit and replaces the assets.

### 4.4 Delete or recreate the rc tags and drafts (DESTRUCTIVE: needs @nymble approval)

```sh
gh release delete v0.1.0-rc.1 -R Threat-Radar/tmodel --cleanup-tag --yes
gh release delete v0.1.0-rc.2 -R Threat-Radar/tmodel --cleanup-tag --yes
```

Prefer a **new** number (`v0.1.0-rc.3`) over reusing a deleted one, so
attestations and downloads never refer to two different builds by one name.
Cut it on a reviewed `main` commit; the tag must match `version` in
`tauri.conf.json` (`0.1.0`, plus an `-rc.N` suffix):

```sh
gh api repos/Threat-Radar/tmodel/git/refs -f ref=refs/tags/v0.1.0-rc.3 -f sha=<full-sha>
gh run watch -R Threat-Radar/tmodel "$(gh run list -R Threat-Radar/tmodel -w release --limit 1 --json databaseId -q '.[0].databaseId')"
```

The result is a draft prerelease. Publishing it is a separate maintainer decision.

### 4.5 Revert #206: SLSA pipeline, rolling build, pinned actions (PR)

```sh
git fetch origin && git switch -c revert/206-slsa-release origin/main
git revert -s --no-edit 19442d7
bin/validate-archdoc
git push -u origin revert/206-slsa-release
gh pr create -R Threat-Radar/tmodel --title "Revert #206 (SLSA release pipeline)" --body-file revert-206.md   # what/why/how tested; ends with the attribution line
```

This removes provenance attestation, the SBOM, the rolling build, SHA pinning,
least-privilege `permissions:`, the PR debug `.app` artifact, CONTRIBUTING §10
"Releases and supply chain" and DL-0034. `release.yml` goes back to tag-only
triggers, so merging the revert does not run a rolling build. It does **not**
delete the releases or tags already made: do 4.3 and 4.4 as well if needed.
If this entry has merged, the revert conflicts in CONTRIBUTING §10 next to
"Fast local review build". Keep that paragraph and drop the sentence that
points to `release.yml` provenance.

### 4.6 Revert #201: packaging fix (PR; not recommended)

Revert #206 first (newest first), then:

```sh
git revert -s --no-edit a29aa06
```

Without #201 the packaged app cannot find the example models and the Graph tab
is empty (DL-0028). Only do this if #201 itself is shown to be wrong.

### 4.7 Rebuild locally for review

On a Mac with the prerequisites in CONTRIBUTING §10:

```sh
git switch --detach origin/main && git submodule update --init library   # or any ref
bin/build-dmg-local
# prints BUILD_SECONDS=… and DMG=…/apps/desktop/src-tauri/target/release/bundle/dmg/tmodel_0.1.0_aarch64.dmg
```

Review builds are ad-hoc signed and carry no provenance. Never upload one to a release.

## 5. Open items

- #124 stays open until a downloaded release `.dmg` passes the clean-Mac check.
- #206 had no second reviewer. A post-merge review by a student (`.github/` and
  CONTRIBUTING §10) is still useful.
- Do not link the landing page to a download until the presentation layer
  (DL-0036) is fit to show.
- Design-log numbers: `0006`, `0011`, `0012`, `0015` and `0024` are duplicated on `main`.
  Open PRs #195, #196 and #200 use `0006`, `0030` and `0033`. This entry
  and DL-0036 took the next free numbers.

## Human review

Pending (@nymble).
