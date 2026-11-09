---
schema: "archdoc/v1"
id: DL-0034
title: "SLSA build provenance and rolling latest-main build"
type: process
status: draft
version: "0.1.0"
date: "2026-11-04"
updated: "2026-11-04"
record: DL-0034
defers_to: ARCH-0001
---

# SLSA build provenance and rolling latest-main build

## Request

@nymble asked on 2026-11-04 for the app's build and release pipeline to follow
SLSA best practice, minimalist first: a working, verifiable delivery path before
the MVP launch (Fri 2026-11-06), then low-risk hardening. Input: `release.yml`
as merged in #201, the first tagged run (`v0.1.0-rc.1`, run 41947795292,
succeeded and created a draft prerelease), and issues #203 and #205.

## Produced

- `release.yml` split into `build` (macOS; `contents: read`, `id-token: write`,
  `attestations: write`) and `publish` (Ubuntu; `contents: write`, no checkout,
  no build tools). `build` attests SLSA provenance for the `.dmg`, the bundled
  engine and an SPDX SBOM with `actions/attest-build-provenance`.
- Pushes to `main` that touch the app publish the rolling prerelease
  `latest-main` (tag moved, assets replaced, build `<version>-main.<sha7>`, #203).
  Version tags still produce drafts; assets are now named after the build label.
- `app.yml` uploads the PR's debug `.app` as a 7-day artifact (part of #205).
- All workflows: third-party actions pinned to commit SHAs, `permissions:` set,
  checkouts without persisted credentials; `cargo fetch --locked` in releases.
- CONTRIBUTING §10 documents the pipeline, the SLSA level and verification.

## Choices and limits

- Claimed SLSA Build L2, not L3: provenance is generated inside the build job
  rather than by an isolated reusable workflow (for example the SLSA GitHub
  generator), and the build is not hermetic (caches, floating stable Rust,
  unhashed pip installs). L3 via a reusable workflow is a follow-up.
- Kept the npm and Rust caches: release time matters for #203's 20-minute goal,
  and only default-branch runs can write caches that tag builds read.
- Kept action major versions as they were (pinned to the latest release of each
  major) to avoid behaviour changes days before launch; Node 20 deprecation
  warnings remain until a deliberate major bump.
- #205's sticky PR comment is not done: it needs `pull-requests: write`, which is
  unavailable to fork PRs; the artifact is on the run page.
- No Developer ID signing: the Apple secrets are not set.

## Human review

Pending.

## Validation

See the pull request: actionlint 1.7.12 with ShellCheck 0.11.0 passes all
workflows; archdoc and publishing checks pass; the branch's `release.yml` was run
by `workflow_dispatch` to exercise build and attestation.
