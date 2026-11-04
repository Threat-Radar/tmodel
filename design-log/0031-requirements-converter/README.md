---
schema: "archdoc/v1"
id: DL-0031
title: "Requirement extraction: folder, converter and CI check (#169, deliverable 1)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-03"
updated: "2026-11-03"
record: DL-0031
bears_on: [DEC-001a, DEC-002]
defers_to: ARCH-0001
---

# DL-0031: Requirement extraction folder, converter and CI check (#169)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code (claude-opus-5-5) drafted it in @Maimcghee's session, as one agent with no subagents. Issue: #169, deliverable 1 (parent #168).

## Question asked

#169 asks for this first, because the other lanes use it:
- a folder README that describes the file format;
- a converter from a library `distilled/requirements.yaml` (`library-requirements/v2`) to a skeleton tmodel file. It copies `id`, `source_ref`, `source_locator` and `normativity`, defaults `requirement_kind` from `nature` and `actor` and marks it for review, and leaves `text` empty for a licensed record;
- a CI step that validates every file in the folder against `ExampleModelCore` and with `check-edges.py`;
- one sample conversion, of a licensed source with empty `text`.

The student asked the agent to start #169's next big task after the morning's quick wins. Deliverables 2 (the import/export mapping note) and 3 (the ETSI EN 304 223 and CISA AI-in-OT files) are later PRs.

## What was produced

All of it is in `research/0017-requirements-extraction/` (RPT-0017), apart from the workflow change:

- **`README.md`:** the file format, the rules, a lane's workflow, the converter's field-by-field mapping, the three checks and the limits.
- **`convert.py`:** stdlib and PyYAML only. It reads `record.yaml` and `distilled/requirements.yaml` and writes Requirements, the owner as a Party, and empty `assertions` and `reviews`. It never proposes a link. Options:
  - `--only` keeps designator prefixes, and `--skip-file` drops provisions with a reason;
  - `--normativity` maps an extra library value;
  - `--empty-text` leaves `text` empty for a free source;
  - `--force` overwrites an existing file.
  
  The header records the digest, the library commit, the read date and the coverage, with every skip and its reason. The converter re-parses its own output before writing it.
- **`check.py`:** checks the rules that the two existing checks cannot:
  - required fields, and ids and `source_ref` that name the file's record;
  - no `verbatim` for a licensed record, and no filled link slot;
  - only the allowed predicates, with `refines`, `derived_from` and `conflicts_with` inside the file;
  - a `Basis:` in every description;
  - `accepted` only with a person's accepting Review, and a justification on every Review.
- **`test_convert.py`:** 9 tests. Two fixture records, one free and one licensed, cover every mapping, both skip reasons, the options, the id-collision stop and the converter's output passing `check.py`. Each `check.py` rule is mutation-tested: a file that breaks it must fail.
- **`iso-iec-30111-2019.yaml`:** the sample. It is unedited converter output from library `3eacfd0`: 32 of 32 provisions, all with empty `text`. ISO/IEC 30111 is in #168's "not in this pass" list ("convert mechanically with the converter"), so the sample does not take a lane's record.
- **`.github/workflows/schema.yml`:** the folder joins the path filters. Three steps run `linkml-validate`, `check-edges.py` and `check.py` on every file in the folder, and then the tests. `.github/` routes to @nymble for review.

## How it was checked

- **The checks, run locally with the pinned LinkML 1.12.1:** `linkml-validate` (ExampleModelCore), `check-edges.py` and `check.py` pass on the sample. They also pass on the three files in #196, so this CI does not fail that PR when both merge. All 9 tests pass. The MVP vectors still resolve.
- **Trial conversions of the records the lanes need**, all valid against ExampleModelCore:
  - `etsi-en-304-223`: 73 of 73 provisions;
  - `cisa-ai-in-ot-principles`: 120 of 136. The 16 skipped have library normativity principle (5), consideration (6), statement (3) or scope (2), so the lane maps or skips them by hand;
  - `iso-sae-21434-2021`: 118 of 118.
- **Against a lane's own work.** #196 (@Clovier) converted 49 ISO/SAE 21434 provisions by hand. For all 49, the converter gives the same `id`, `source_ref`, `source_locator`, `normativity` and `text_origin`. `requirement_kind` matched for 10 at first, and for 45 after the change rejected below.
- **ETSI EN 304 223's organizational entries.** The actor rule gives 6 `organizational` provisions (5.1.1-1, 5.1.1-1.1, 5.1.1-2, 5.1.1-2.1, 5.1.1-2.2 and 5.1.2-5.1), the same 6 that RPT-0009 §3 counts as obliging the organization.

## Choices the agent made, open to review

- **The licence test is a heuristic.** A record counts as licensed if it is under the library's `records/iso/`, or if its publisher names ISO, IEC or SAE. `check.py` uses the file name, an id starting `iso-` or `iec-`. Neither the library schema nor #154 has a licence field yet.
- **A free source keeps the library's verbatim text, marked for paraphrase.** The issue prefers paraphrase but allows verbatim for free sources. Copying the text with `text_origin: verbatim` is true to where it came from, and `--empty-text` gives the other choice.
- **Library normativity values outside the issue's three are skipped, with the reason.** The converter also maps prohibition to mandatory and informative to informative. principle, consideration, statement, scope and the other family values need a human choice, given with `--normativity`.
- **The library's `condition` does not become `conditional`.** It is marked for review, because the library records conditions inconsistently (`docs/requirements-schema.md`: 984 of 6,274 rows).
- **A process provision is `organizational` when every actor is the organization or its management.** Other actors keep the default from `nature`.
- **A licensed record gets the designator as its name.** The library's short titles can copy the standard's words.
- **Review marks are YAML comments (`# REVIEW:`).** The schema has no review flag on a Requirement. `check.py` counts the marks but does not fail on them.
- **`check.py` is stricter than ADR-0012.** ADR-0012 lets a reviewed link become a slot value. Here every link stays an Assertion, as #169 asks: "Never fill addresses / satisfied_by / stated_as / … directly".
- **The converter reads the raw v2 file, not the library's v3 loader.** This keeps tmodel to ADR-0012's reference-only rule, at the cost of handling raw-file quirks itself, such as a scalar `actor`.
- **The folder README takes the id RPT-0017**, after the folder number. The research index (`research/README.md`) has no row for RPT-0016 or RPT-0017 yet.

## What a human accepted

- The student asked for #169 to start with deliverable 1. Nothing in this PR has been reviewed yet.

## What was rejected, and why

- **Rejected by the agent: deliverable-producing → documentation.** The first version defaulted the library's `deliverable-producing` to `documentation`. Compared with #196, that disagreed with the lane for 39 of 49 provisions. The library's schema groups the two values ("deliverable / deliverable-producing (yields a work product)"), but a deliverable-producing provision still obliges someone to do something. RQ-08-01, for example, is to select the sources of cybersecurity information. tmodel's `process` is "an activity the developer or operator must perform", and its `documentation` is "a work product or record that must exist". So the default is now `process`, and `documentation` is kept for `deliverable`. That leaves 4 disagreements, all judgement calls on single provisions (RQ-08-06, RQ-09-06, RC-10-06, RQ-10-13). #196's kinds were chosen by its agent; @Clovier's Reviews there cover links, not kinds. So the comparison is a second opinion, not a reviewed answer.
- **Fixed after a test failed: the designator check in `source_locator`.** The first version tested "is the designator in the locator" as a substring, so designator `1` counted as present in `§1`. It now has to be a whole word.
