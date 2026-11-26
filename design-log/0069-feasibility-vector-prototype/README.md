---
schema: "archdoc/v1"
id: DL-0069
title: "Attack feasibility vectors: standalone prototype of the three Annex G methods (#14)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-25"
updated: "2026-11-25"
record: DL-0069
human_owner: nymble
bears_on: [DEC-003, ADR-0006, ADR-0015]
defers_to: ARCH-0001
---

# DL-0069: Attack feasibility vectors, standalone prototype (#14)

DL-0064, DL-0065 and DL-0068 are reserved by open PRs #261, #262 and #268, so this entry uses
DL-0069. ADR-0014 is reserved by #261, so the proposed ADR is ADR-0015.

## Question asked

The sponsor (@nymble) asked for a multipart, colour-coded attack-feasibility vector that follows
ISO/SAE 21434 exactly (#14, Common Criteria attack-potential calculator), then for a design, and then,
once the design was approved, to try it on its own pages first so layout and behaviour can be checked
before any existing threat model, schema, engine or app code changes.

## What was produced

- `docs/feasibility/index.html`, `ui.js`, `feasibility.js`: a static page (no build step) with
  vector parsing and validation for three methods, the computation, compact and mini rows, an
  expanded view with a method switcher and level pickers, rating-state markers, and per-item
  exception markers with a hover or pinned history popover.
- `docs/feasibility/examples.js`: ten invented example threat scenarios, labelled example data.
- `docs/feasibility/test-feasibility.js`: 16 checks, run with `node docs/feasibility/test-feasibility.js`.
  Not wired into CI.
- `spec/ADR-0015-attack-feasibility-vectors.md`: status proposed. It records the decisions below and
  what would change later; it changes nothing now.

Nothing else in the repository changes: no model file, schema, engine, app or existing page, and no
nav link.

## Notation

One grammar for all three methods; codes name levels, numbers live in one table.

| Method (Annex G) | Vector | Rating |
|---|---|---|
| Attack potential (G.2, Tables G.1 to G.7) | `AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE` | sum of Table G.6 points, Table G.7 bands |
| CVSS exploitability (G.3, Table G.8) | `CV:3.1/AV:A/AC:L/PR:N/UI:R` | E = 8.22 × AV × AC × PR × UI, Table G.8 bands |
| Attack vector (G.4, Table G.9) | `AX:2021/AV:N` | read from Table G.9 |

Total, E and rating are computed and never part of the string. CVSS 4.0 vectors are rejected.

## Accepted by the sponsor (2026-11-25)

1. The computed rating is the source of truth, and every displayed rating says whether it is
   computed or human-reviewed. States: computed, reviewed as is, changed by human, overridden,
   review stale, label only. Shape and text carry the state, never colour.
2. An override needs a level, rationale, author and date; the computed result at decision time is
   kept. A stale override stays in force and is flagged.
3. Elapsed time uses the five ISO/SAE 21434 levels, not the ten of ISO/IEC 18045.
4. Window of opportunity gains a not-exploitable level, `WO:NEX`, as a tmodel extension beyond
   ISO/SAE 21434, marked † wherever it shows. It lines up with the "none" window in ISO/IEC 18045
   (CEM:2022 Table B.2, note b) and suits physical-security cases. A NEX path is not summed, has
   no Table 1 level and gives no risk value (it does not feed Table H.8); the report still shows the
   ISO-strict equivalent (window difficult, 10 points) and the recorded basis.
5. All three Annex G methods are supported, selectable per threat scenario; attack potential is the
   default, and one model may mix methods. Every row carries a method tag and starts on the default;
   a human then approves it as it stands or changes it, and the marker shows which.
6. The Okabe-Ito factor palette is approved. CVSS and attack-vector chips stay neutral slate. A
   single vector item can carry an exception marker (outline pattern plus corner glyph: changed by a
   reviewer, disputed, commented) with its history on hover or click.

## Rejected, and why

- **Common Criteria as display only (ADR-0006, DEC-003).** Replaced by computed ratings, through
  ADR-0015 once accepted. Display-only numbers would leave the rating unexplained.
- **Mapping NEX to Very low.** A Very low rating still scores risk 2 for a severe impact under the
  Table H.8 example; the sponsor chose no risk value instead.
- **Automatic conversion of existing human labels.** One label matches many vectors, so inventing
  factors would fabricate evidence. Existing labels stay as "label only".

## Verification of the values

The licensed PDF was not on the box or on the reachable Mac (searched the box filesystem, the Mac
home directory and project clones, and the sponsor's mail for an attachment). The record says the
purchased copy is kept in a library clone's gitignored `.cache`; no such clone was reachable today.
The values were checked instead against the library's record of the standard, which was itself
verified against that copy:

- `records/iso/iso-sae-21434-2021/distilled/examples/annex-g-feasibility.yaml` (Tables G.1 to G.9,
  bands, CVSS ranges): every level name and point value of the five factors, the Table G.7 bands,
  the Table G.8 bands and ranges, and the Table G.9 mapping match `feasibility.js` exactly (scripted
  comparison).
- `records/iso/iso-sae-21434-2021/distilled/examples/expected.yaml`: the Table G.7 boundary cases,
  the two Table H.7 paths (sums 20 and 24, both Low, an independent check on the G.6 points as the
  standard prints them) and nine CVSS cases are reproduced by `test-feasibility.js`. That file also
  fixes the two CVSS conventions used here: scope-unchanged weights and E rounded half up to two
  decimals.
- `records/iso/iso-sae-21434-2021/distilled/normative.md` §5.7 (the markdown summary of Annex G)
  and `record.yaml` locators agree with the clause and table numbers used.
- `records/iso/iso-sae-21434-2021/distilled/verification.md`: the record's pass 2 compared the annex
  values with the purchased PDF (SHA-256 `73f99007…cdf4`), reading Tables G.6 and G.7 from page
  images. Its `reviewed_by` is still empty, so a human check against the PDF remains open.
- Public cross-checks: ISO/IEC 18045 (CEM:2022 Release 1, B.6, Tables B.2 and B.3; same digest as
  library record `iso-iec-18045`) for the attack-potential points and bands; FIRST CVSS v3.1
  specification, Table 16, for the CVSS weights.

No mismatch was found. The prototype carries level names and numbers only, no text of the standard.

## Open

- A human check of the Annex G values against the PDF, when the machine holding it is online.
- Scoping the later change to existing threat models (ADR-0015 lists what would change); nothing is
  converted automatically.
