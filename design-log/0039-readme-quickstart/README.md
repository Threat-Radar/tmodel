---
schema: "archdoc/v1"
id: DL-0039
title: "README status and tested app quickstart"
type: process
status: draft
version: "0.1.0"
date: "2026-11-06"
updated: "2026-11-06"
record: DL-0039
defers_to: ARCH-0001
---

# README status and tested app quickstart

## Request

@paria03 requested the README work in #202 item 6 after testing the app.
No additional review of #211 was requested.

## Produced

- Replaced the obsolete bootstrap status with the prototype's current behavior
  and limits. Linked the rolling macOS release and the pending report-first UI
  in #211; documented the Library/Knowledge Graph interface present on main.
- Added a browser quickstart, exact software and automotive model URLs, and
  engine CLI examples. The `#graph` fragment is required to open the graph tab;
  the `file` parameter alone only chooses the model.
- Explained that model files are bundled but Library documents require a
  separate checkout. Kept native build and provenance instructions in
  CONTRIBUTING §10 rather than duplicating them.
- Updated CONTRIBUTING §7–8 for the existing pinned submodule and linked the
  quickstart. Corrected README descriptions of accepted architecture decisions.

## Choices and limits

This is documentation only: no engine, frontend, release workflow, dependency,
or library-pin changes. The base is main at c91d78c, with library pinned to
a28a01375814accc5fe10cb2f5e7083c7d0401a5. Report-first views remain described
as pending review rather than available on main.

An initial test with Python 3.14.3 exposed a local environment problem: macOS
marked the editable-install `.pth` file hidden and Python skipped it, so later
CLI invocations could not import the engine. The completed quickstart test used
a fresh Python 3.13.1 environment. The README now names the 3.11–3.13 CI matrix
and uses `python3.13` explicitly. No Python 3.14 support claim is made here.

## Validation

- Fresh worktree and initialized pinned library; fresh Python 3.13.1 virtual
  environment, editable engine installation, and `npm ci` with Node 22.23.0.
- Started the documented engine and Vite commands. Browser check: connected
  engine, Library search `21434` (two records), both exact model URLs, and
  automotive accepted diagnostic and rejected infotainment path selection.
- All three README CLI commands passed; infotainment JSON returned two
  alternatives with `review_status: rejected` and `reviewed: false`.
- Archdoc, publishing identity/link checks, README/CONTRIBUTING local file
  links, and whitespace validation passed.
- Pinned library validation: 550 records, 21 topics, 0 errors, 122 existing
  warnings (including unfinished summaries and possible duplicate records).

## Human review

Documentation review pending. The user's successful app test is separate from
review of this documentation change and from any model's recorded review state.
