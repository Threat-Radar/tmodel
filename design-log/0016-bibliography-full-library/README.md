---
schema: "archdoc/v1"
id: DL-0016
title: "Bibliography — full-library render and A–Z reference page (#91)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: DL-0016
---

# DL-0016 — bibliography, full library (2026-10-08)

## Question asked

Sponsor: *"let's make a bibliography page and resolve this issue!"* (#91). The
first pass (PR #95) rendered 16 of 129 records. The library is now 414
records at pin `cd28d36`.

## What was produced

- `library` submodule pin moved from `670b6b6` to `cd28d36` (upstream `main`,
  which adds the RPT-0006 knowledge-graph visualization records).
- `render_bibliography.py`:
  - `--sync` appends library records that are missing from the manifest. It
    never edits an existing entry.
  - Index rewritten as an A–Z reference list with counts and jump links.
  - An empty topic is allowed only when the record has no subject tag. It
    renders as "no topic tag yet".
  - YAML subset fix (a flow value on its own line).
  - The remote-asset guard is narrowed to elements that load something.
  - The 40-record cap is removed, along with the duplicated
    `source.record_ids` list.
- `bibliography.yaml` lists all 414 records. `bibliography-review.md` §7–9 and
  `SKILL.md` are updated to match.
- `docs/bibliography/` is regenerated. A second run is byte-identical.
  `check_identities.py` is clean on 421 pages.

## Decisions / rejections (agent-side, pending human review)

- **Rejected: switching the renderer to PyYAML.** It is installed locally, but
  the renderer is stdlib-only on purpose. A one-branch parser fix is smaller,
  and it was checked to give the same result as `yaml.safe_load` on all 414
  records.
- **Rejected: `include: all` in the manifest.** It would hide which records
  were published and with what topic. The issue's shape says the manifest
  lists them. `--sync` keeps the list explicit and reviewable.
- **Rejected: `body` as the citation lead** when a record has no authors or
  publisher. A first render printed "iso." in front of an IANA registry. The
  body is the storage folder, not an author, so the entry now leaves the
  lead out.
- **Rejected: inventing topics for the 10 untagged records**
  (e.g. `iso-iec-15408`, `fips-140-2`). The fix is tagging them in the
  `library` repo.

## Awaiting human review

- The 398 auto-assigned primary topics (default rule in
  `bibliography-review.md` §7). Correct them in `bibliography.yaml`.
  `--sync` will not overwrite the corrections.
- 270 of 414 records have no written summary. That work belongs to #86, not
  this page.
