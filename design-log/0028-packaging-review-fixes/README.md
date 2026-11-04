---
schema: "archdoc/v1"
id: DL-0028
title: "Packaging review fixes for PR #155"
type: process
status: draft
version: "0.2.2"
date: "2026-10-29"
updated: "2026-11-03"
record: DL-0028
defers_to: ARCH-0001
---

# Packaging review fixes

## Request and evidence

@paria03 asked to start the packaging review fixes. Input: @Clovier's review on
PR #155, plus its existing implementation and the current main branch. Work
stays on `feat/124-packaging`; no architectural decision changes.

## Changes and reasoning

- Merged main so the sidecar includes the merged attack-path engine and PyYAML.
- Normal quit closes the sidecar's stdin instead of sending SIGKILL to its
  process group. The engine's existing `--exit-with-parent` watcher shuts down
  the server, allowing the PyInstaller launcher to remove its unpacked runtime.
  A condition variable waits for the termination event, bounded at ten seconds,
  to avoid immediately reopening against the old engine. The external-engine
  case remains unowned and is not stopped.
- `bin/build-engine` now loads an example YAML and computes its two IMDS paths
  in an empty environment, in addition to checking the executable's version.
- Opt-in packaged-executable tests check model loading and runtime cleanup over
  three normal restarts and three closes before server readiness. The macOS CI
  job runs them against the executable it just built.
- Release dependency installation happens before signing credentials become
  available. Apple credentials are scoped to the build step, and absent values
  are unset to preserve ad-hoc signing. Checkout no longer persists its write
  token. Draft release candidates are marked prerelease at creation.
- Engine CI includes Python 3.13, the version shipped in the app, and reruns on
  vector changes. CONTRIBUTING records the remaining release acceptance checks.

## Choices and limits

- Rejected force-killing the launcher on every normal quit: it prevents cleanup.
  Crash/force-quit cleanup continues to rely on stdin closure.
- No full tagged release, clean-machine download, or Developer ID notarization
  is claimed by these code changes. #124 stays open for that acceptance work.
- No changes to model storage, graph rendering, or architecture decisions.

## Human review

Pending. These are AI-assisted fixes responding to an existing human review;
this log does not claim a human has accepted the revised implementation.

## Validation

- Python 3.13 engine suite: 101 passed, 3 opt-in packaging checks skipped.
- Those three checks run separately against the rebuilt executable: 3 passed.
  They include six stdin-close cycles and verify no `_MEI*` runtime remains.
- Frontend: 11 tests passed, TypeScript typecheck and production build passed.
- Rust: 4 tests passed, rustfmt and clippy with warnings denied passed.
- The release `.app` and `.dmg` build passed; deep strict codesign verification passed.
- Three actual `.app` launches followed by normal quit each stopped the engine
  and left no unpacked runtime in an isolated temporary directory.
- Actionlint 1.7.12 passed for app.yml and release.yml (ShellCheck unavailable).
  The downloaded actionlint archive was verified against its release checksum.
- Tagged release, clean-machine download, and Developer ID signing remain untested.

## Installed graph resources follow-up (2026-10-30)

### Request and problem

@paria03 asked to continue #124 after reviewing #162. PR #162 is now merged:
its graph endpoint resolves models under the source checkout's `spec/vectors/`,
but that directory was absent from the one-file engine. The Cytoscape notice
also existed only in the source tree. The question was how an installed app
can load its example graph and carry the dependency notice without a checkout.

### Produced and choices

- Include `spec/vectors/` as PyInstaller data. The engine resolves the examples
  below PyInstaller's unpacked runtime in a frozen build and below the repository
  root in source runs. Filename confinement and symlink checks still apply.
- Map the existing Cytoscape notice into Tauri resources. On macOS the notice is
  readable at `Contents/Resources/THIRD_PARTY_NOTICES.md`.
- Test the actual standalone executable after copying only that executable to a
  temporary directory with an empty environment. Request MVP-01 and MVP-02 via
  `/graph`, use the returned filename with `/attack-paths`, preserve negative
  human review states, reject graph access outside the example directory, and
  verify runtime cleanup. App CI and the release workflow run these checks
  against the sidecar from the app bundle and compare the notice byte for byte.
- Rejected a dependency on the launch directory or a developer's absolute source
  path: neither exists reliably in a downloaded installation. Putting the
  examples in the engine also lets the standalone executable serve the same graph.
- Reference-library installation is a separate integration question on #60/#188;
  bundling examples does not select its policy. No schema, vector contents, or
  architecture decisions change.

Implementation references: [PyInstaller runtime data](https://www.pyinstaller.org/en/stable/runtime-information.html)
and [Tauri resource mappings](https://v2.tauri.app/develop/resources/).

### Human review and acceptance

On 2026-10-30, @paria03 reported successful manual testing of the local packaged
build. Individual checklist results were not itemized. Code review remains
pending; a tagged draft release and a downloaded-installer test on a clean
account remain necessary to close #124. Notarization remains untested.

### Follow-up validation

- Engine: 149 passed; 6 skipped without a packaged executable or initialized
  library submodule. Ruff lint and formatting pass.
- Packaged executable: all 5 checks pass, including both relocated graph tests
  and six stdin-close cleanup cycles. All 5 also pass against the release app's
  signed sidecar.
- Frontend: 137 tests pass, TypeScript checking and production build pass.
- Rust: 4 tests pass; formatting and clippy with warnings denied pass.
- Release `.app` and `.dmg`, plus the debug app bundle used in app CI, build.
  Both app bundles pass deep strict codesign verification and contain the exact
  Cytoscape notice. The read-only mounted `.dmg` also passes these checks.
- An app copied from the `.dmg` to a path outside the checkout starts its sidecar
  and serves the default 42-node, 69-edge graph from its unpacked examples. An
  interrupt stops the sidecar, releases the port, and removes the unpacked runtime.
- Actionlint passes both changed workflows (ShellCheck unavailable), and archdoc,
  publishing identity/link checks, shell syntax and `git diff --check` pass.
- Automated window observation was unavailable because computer-control
  permission was not granted. @paria03 subsequently reported that the local
  manual test passed. A tagged draft release, download on a clean account, and
  Developer ID notarization remain untested.

## Retest after pulling main (2026-11-03)

@paria03 requested a fresh installer before publication. The code at `a469b35`
includes the pulled library API/table work and preserves the packaged example
lookup. The engine was rebuilt with Python 3.13.1, followed by the release app
and `.dmg`. No implementation changes were needed for this retest.

The installer was mounted read-only. Its app passed deep strict codesign
verification, its notice matched the source file, and a copy was placed outside
the checkout for manual testing. The engine suite used the signed sidecar from
that installer copy: 237 tests passed, including all five packaging checks;
two full-library checks skipped because the submodule is not initialized in
this worktree. Both bundled example graphs and stdin-close cleanup passed.

Frontend: 137 tests, TypeScript checking and production build passed. Rust:
four tests, formatting and clippy with warnings denied passed. Engine lint and
formatting, archdoc, workflow linting (without ShellCheck), publishing identity
and relative-link checks, and `git diff --check` passed.

The successful manual test recorded above applies to the October 30 build.
Manual testing of this rebuilt installer is pending. The tagged-release and
clean-account acceptance checks remain outstanding; #124 stays open.
