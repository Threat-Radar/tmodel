---
schema: "archdoc/v1"
id: DL-0011
title: "RPT-0007 ISO/SAE 21434 and TARA: AI-assisted extraction, object mapping and catalog check"
type: process
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-02"
record: DL-0011
---

# DL-0011: RPT-0007, ISO/SAE 21434 and TARA

AI-assisted research record for #11 (per `CLAUDE.md`). Student: Tyler Van Heerden, working with Claude Code. Numbered 0011 because open pull requests #66 and #68 already use 0008 to 0010.

## Question asked

Issue #11: extract ISO/SAE 21434:2021 and its threat analysis and risk assessment (TARA) method, recommend a candidate object model for the schema work (#17), and relate 21434 risk to the metrics work (#14), building on the sponsor's library catalog. The student asked for every claim to be checked against its source, for nothing to be copied from the paid standard, and, from section 6 on, for independent subagents to fact-check every section.

## What was produced

- `research/0007-iso21434-tara/`: the report (eight sections), dimensions, search log and source log.
- Report §5: a mapping of 23 ISO/SAE 21434 objects onto ARCH-0001 v0.1.6 and ARCH-0001-PROPOSAL `0.2.0-proposed.7`, with gaps both ways and the cardinalities the standard states. This mapping is why the entry is required.
- Report §6: a check of the proposal's risk-metric claims (DEC-003) against the standard.
- Report §7: a mechanical check of the library catalog `iso-sae-21434-2021`. 16 of 118 provision texts are wrong or cut short, 16 of the 32 work products tied to named provisions have missing links, and 19 locators, 3 titles and 3 Figure 3 edges are off.
- Method: the sponsor's purchased copy of the standard, used only on the student's machine (its digest is in sources.md); the report paraphrases and cites clause numbers; a script flags any run of 7 words the report shares with the standard; tables and figures whose layout breaks in text extraction were checked as page images.

## What a human accepted

- The student had each section committed and pushed one at a time (`8d8794c` to `09788b6`), after a summary and a list of PDF pages to spot-check.
- The student chose to publish the example numbers of Tables E.1, G.6 to G.9 and H.8 (numbers and level names, no prose) without asking the sponsor first.
- The student asked for the fact-check subagents and for their findings to be applied.
- Still to come: a line-by-line review by the student and the sponsor, and a manual check of the ISO stage names on iso.org (§1.2). No human has rejected anything yet.

## What was rejected or corrected, and why

Eight fact-check subagent runs, one per section, raised 107 findings (two earlier runs stopped when the student's computer slept and produced none). Each was re-checked against the source before it was fixed. The ones that changed a claim:

- **"STRIDE is outside 21434's scope" was wrong.** The standard names STRIDE among the frameworks for threat scenario identification (15.4, NOTE 2).
- **"An item is scoped by one function" was wrong.** Figure 3 and RQ-09-01 allow several functions.
- **Figure H.2 was misread.** The other ECUs lie outside the operational environment, not inside it.
- **RQ-07-04 was misclassified** as a cut-short list. Its catalog text is Annex C's template, so 5 entries hold annex text and 11 are cut short.
- **"Fixing the catalog puts more of the standard online" was backwards.** The fixes would shrink the catalog's copy by nearly a third, if it stays verbatim.
- **The library's Figure 3 notes** were first summarized as three reversed edges. Three differ in meaning, and two more are only written the other way round.
- **Section 8 overstated what the report settles.** It said sections 2 to 4 and 7 cover the DEC-003 blocker pending sign-off; whether they clear it is the sponsor's call (§6.2).

Corrections the agent made to its own method before or between the subagent runs:

- A first parser missed identifiers split across lines ("[RQ-" then "15-06]"), which hid the WP-15-04 range defect. It was fixed and rerun.
- Wording suggested by the checkers sometimes echoed the standard; the 7-word copy check caught it, and those sentences were reworded.
- No checker suggestion was rejected outright. One was handled differently from its suggestion: instead of weakening the claim that every Annex H table was checked as a page image, the two pages not yet checked were rendered and checked.

## Next steps

- Human review and sign-off of RPT-0007, by the student and then the sponsor.
- Sponsor decisions on the three open questions in RPT-0007 §8: verbatim text in the public library, whether the report clears the DEC-003 blocker, and who fixes the catalog under FX-1.
- A library pull request to fix the catalog (RPT-0007 §7.2), once the sponsor decides.
- Revisit §5 and §6 if the proposal moves on: open pull request #66 (`proposed.8`) adds stakeholder-relative impact and a TARA owner.
