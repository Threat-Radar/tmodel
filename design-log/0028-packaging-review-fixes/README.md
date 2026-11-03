---
schema: "archdoc/v1"
id: DL-0028
title: "Packaging review fixes for PR #155"
type: process
status: draft
version: "0.1.0"
date: "2026-10-29"
updated: "2026-10-29"
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
