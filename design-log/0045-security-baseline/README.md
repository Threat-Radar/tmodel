---
schema: "archdoc/v1"
id: DL-0045
title: "Repository security baseline: reporting, scanning, required checks"
type: process
status: draft
version: "0.1.0"
date: "2026-11-07"
updated: "2026-11-07"
record: DL-0045
defers_to: ARCH-0001
---

# Repository security baseline: reporting, scanning, required checks

## Request

@nymble asked on 2026-11-07 to fix the repository security gaps that the SDL
example graph (#217, DL-0040) recorded: no SECURITY.md, private vulnerability
reporting off, no required status checks on `main`, Dependabot security updates
off, secret scanning off, and no CodeQL.

## Produced

Repository settings, changed by an AI agent as @nymble on 2026-11-07 (before
and after values kept with the change record):

| setting | before | after |
|---|---|---|
| private vulnerability reporting | off | on |
| secret scanning | off | on |
| secret scanning push protection | off | on |
| Dependabot security updates | off | on |
| required status checks on `main` | none | `archdoc` (strict off) |
| required approving reviews | 1, stale dismissed | unchanged |
| admins bypass protection (`enforce_admins`) | allowed | unchanged |

In this change:

- `SECURITY.md`: private reporting route, scope, supported versions, how to
  verify a download (`gh attestation verify`).
- `.github/workflows/codeql.yml`: CodeQL for Python, JavaScript/TypeScript and
  GitHub Actions, on pull requests, `main` and weekly. Actions pinned to commit
  SHAs, read-only checkout token, `security-events: write` on the job only
  (DL-0034 practice).
- `.github/dependabot.yml`: grouped weekly updates for actions, `engine/` (pip)
  and `apps/desktop/` (npm).
- CONTRIBUTING §10: a short paragraph pointing to the above.

## Choices

- **Only `archdoc` is required.** It is the one check that runs on every pull
  request. The engine, frontend, schema and desktop workflows have path filters,
  so requiring them would block pull requests that never trigger them. Making
  them required needs either removing the filters or adding an always-running
  summary job; left as a follow-up.
- **CodeQL is not required yet.** Add it after a few clean runs, so the first
  findings can be triaged without blocking work.
- **`enforce_admins` stays off.** The sponsor uses admin merge (#174, #206).
  Turning it on is the sponsor's decision.

## Undo

Each setting can be switched back in Settings, Code security, or with the same
`gh api` endpoints. Delete `codeql.yml` and `dependabot.yml` to stop scanning
and update PRs.

## Review

| reviewer | kind | verdict | date |
|---|---|---|---|
| @nymble | human (sponsor) | pending | |

(Drafted by Grok Bot for Paul)
