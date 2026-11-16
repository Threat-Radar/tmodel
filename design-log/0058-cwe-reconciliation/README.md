---
schema: "archdoc/v1"
id: DL-0058
title: "CWE import reconciliation: the file read twice, every loss named, and a CI check on MITRE's release (#146, #61)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-15"
updated: "2026-11-15"
record: DL-0058
bears_on: [DEC-008]
defers_to: ARCH-0001
---

# DL-0058: the CWE import's reconciliation

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, the Data lane owner, working with Claude Code.

## Question asked

- **#146** (part of #61) is PLAN-0002 §5's acceptance test for the CWE import. A reconciliation report must show that the imported entries equal the union of the entries across the views, that the imported relationships equal the distinct (entry, type, target, view) tuples, and, with a field-level diff, any CWE field left unmapped. A CI job must fail on any loss. The test plan: drop one relationship from a test import, and the report shows the loss and the check fails; in CI, the job passes on the real import. The last box links the report on #61.
- It builds on #145 (DL-0057), which keeps every relationship with its view.

## What was produced

| File | Change |
|---|---|
| `engine/engine/load/cwe_reconcile.py` | new: `reconcile()`, `to_markdown()`, and the command `python -m engine.load.cwe_reconcile` |
| `engine/tests/test_cwe_reconcile.py` | 20 tests, one of which runs only when MITRE's file is at hand |
| `design-log/0058-cwe-reconciliation/report-cwe-4.20.md` | the report for MITRE's CWE 4.20, the release the library pins |
| `.github/workflows/cwe.yml` | new: the CI job |
| `CONTRIBUTING.md` §10 | how to run it, and how to refresh the report |

### One file, read twice

The importer reads the file into entries (DL-0050, DL-0057). The reconciliation reads the same bytes a second time with ElementTree alone, with none of the importer's code, and compares the two readings:

- **Entries.** The kind and id of every Weakness, Category and View, and the id of every External_Reference.
- **Relationships.** The (entry, nature, target, view) tuples, counted as often as they are written, all together, by nature and by view.
- **Fields.** For every entry and reference, field by field: an attribute by its exact value, and any other field by its elements, the names and values of the attributes inside it, and its words, in order. A field the reader does not know is kept (DL-0050), so it is flagged but not counted as lost.
- **Links.** The CAPEC links and the observed examples.

`lossless` is true only when all four agree. The second read must give the bytes the importer read (the same SHA-256), so a file that changes between the two reads is refused.

### "The union of entries across the views"

PLAN-0002 §5 wrote the entry check as "imported entry count == union of entries across the three views". The import reads the whole catalog instead (#61, question 1), so the report says how the two differ. In 4.20, 1,371 of the 1,450 entries are reached by some view's relationships. The other 79 are the 64 deprecated entries and the 15 implicit views, which pick their members with a filter instead of listing them. An import that took its entries from the views' relationships would drop all 79.

### The report

The report is Markdown, and the same file always gives the same text: it names no time, no path and no file name, only the file's SHA-256. The committed `report-cwe-4.20.md` is the report for MITRE's 4.20 zip. `--write` refreshes it, and `--check` fails when it is not the report the file gives, so it cannot go stale without CI saying so.

### The CI job

`.github/workflows/cwe.yml` runs when the importer, the reconciliation, the engine's dependencies, this folder or the workflow itself change. It installs the engine and downloads MITRE's zip from the URL the library's `cwe` record names. It refuses any other bytes, checking them with `sha256sum` against the record's digest. Then it runs the reconciliation with `--check`. It fails on any loss and on a stale report, and it adds the report to the run's summary page.

## How it was checked

- **The sample** (12 entries and 3 references) is lossless: 20 relationships, and 15 entries and references compared field by field.
- **Losses made on purpose, each named.** One relationship dropped, as #146's test plan asks: the report shows CWE-79 ChildOf CWE-74 in CWE-1000 missing, and the command exits 1. Also named: a weakness dropped (once, as an entry), a field dropped, an attribute kept with another value, an attribute inside a field changed, words lost from a field, and a word swapped for another, which leaves the counts equal.
- **Kept, not lost.** An unknown field is flagged and the import stays lossless. A relationship written twice is counted twice in both readings.
- **The command.** `--write` then `--check` passes. A stale report fails, with how to regenerate it. A missing report is a read error. Other bytes than the pinned ones are refused, and so is a file that changes between the reads. The report does not depend on the file's name.
- **MITRE's whole 4.20 zip** is lossless: 969 weaknesses, 422 categories, 59 views and 1,026 references; 6,626 relationships, all distinct; 2,476 entries and references compared field by field, none lost and none unknown; 1,212 CAPEC links and 3,134 observed examples. It takes about 1.7 s.
- **CWE 4.21**, read without a digest, is lossless too. Its five new External_Reference fields are flagged as unknown, as DL-0050 found.
- **The CI job's steps, run locally.** MITRE's zip, downloaded fresh, matches the digest, and the reconciliation passes with `--check`. A first run found that the report named the file, so a download saved under another name could never match. The report now leaves the name out, and a test holds that.
- **The engine.** 527 passed and 5 skipped on Python 3.11, 3.12 and 3.13, with MITRE's file at hand. `ruff check` and `ruff format --check` are clean.

## Choices the agent made, open to review

1. **A second, independent reading,** rather than counting what the importer read: a count of the importer's own output cannot show what it missed.
2. **Fields compared by their content in order,** not by rebuilding the XML and comparing bytes. The import's field form (DL-0050) is not XML. Whitespace and the order of attributes are not kept, by design, so the attributes inside a field are compared by name and value.
3. **Membership of implicit views is not evaluated.** Their filters are expressions, not lists, so the report says which entries no relationship reaches instead of working out every view's members.
4. **Relationships compared as counts per tuple,** so a relationship written twice must be kept twice.
5. **A committed report checked by CI,** rather than a CI artifact. An artifact expires, so a link on #61 would break, while the committed report can be read in review and linked, and `--check` keeps it true.
6. **CI downloads MITRE's file.** It is never committed (`CLAUDE.md`), and CI has no other copy. The URL and digest are the library record's, written into the workflow because tmodel's library pin (`a28a013`) predates the record's digest. How the app gets the catalog stays DEC-008's question.
7. **A workflow of its own,** `cwe.yml`, rather than a job in `app.yml`: it needs the network, and it runs only when the import changes. `.github/` is @nymble's in `CODEOWNERS`.
8. **`python -m engine.load.cwe_reconcile`, not a `tmodel` command.** It is a check that reads a local file, not an answer of the engine's API (APP-0001 A-060).

## What a human accepted

- @Clovier, 2026-11-15: take #146 once #145 was up for review (#248), as local work, nothing committed until reviewed.

The code, the report and the choices above are the agent's draft until a human reviews them on the pull request.

## What was rejected, and why

- **Counting only what the importer read.** It cannot show what the importer missed.
- **Comparing word counts only.** A word swapped for another would pass, so the words themselves are compared.
- **A reconciliation over three views.** It would call 79 entries the import keeps "extra", and it would miss what PLAN-0002 §5 wants, which is that nothing is dropped.
- **Committing MITRE's catalog for CI.** `CLAUDE.md` forbids committing third-party files; the library holds the locator and the digest.
- **A CI artifact as the report.** It expires, and the link on #61 with it.

## Follow-ups

- Link the report on #61 (#146's last box) once this merges.
- When tmodel's library pin moves past library#21, have the workflow read the URL and the digest from the submodule's `cwe` record.
- When the library pins another CWE release, regenerate the report for it.
- The same check for the CAPEC import (#244), once it merges.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
