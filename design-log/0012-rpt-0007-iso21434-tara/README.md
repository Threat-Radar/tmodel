---
schema: "archdoc/v1"
id: DL-0012
title: "RPT-0007 ISO/SAE 21434 and TARA: AI-assisted extraction, object mapping and catalog check"
type: process
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-03"
record: DL-0012
---

# DL-0012: RPT-0007, ISO/SAE 21434 and TARA

AI-assisted research record for #11 (per `CLAUDE.md`). Student: @Clovier, working with Claude Code. First written as DL-0011; renumbered 0012 on 2026-10-03 because `main` now has DL-0011 (the composite risk vector entry, #77), and 0008 to 0010 were already taken. Open pull request #76 also uses 0011.

## Question asked

Issue #11: extract ISO/SAE 21434:2021 and its threat analysis and risk assessment (TARA) method, recommend a candidate object model for the schema work (#17), and relate 21434 risk to the metrics work (#14), building on the sponsor's library catalog. The student asked for every claim to be checked against its source, for nothing to be copied from the paid standard, and, from section 6 on, for independent subagents to fact-check every section.

## What was produced

- `research/0007-iso21434-tara/`: the report (eight sections), dimensions, search log and source log.
- Report §5: a mapping of 23 ISO/SAE 21434 objects onto ARCH-0001 v0.1.6 and ARCH-0001-PROPOSAL, first at `0.2.0-proposed.7` and, after the sponsor's review, at `0.2.0-proposed.10`, with gaps both ways and the cardinalities the standard states. This mapping is why the entry is required.
- Report §6: a check of the proposal's risk-metric claims (DEC-003) against the standard, extended to the composite risk vector of `proposed.10` (items 12 to 16).
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

## Sponsor review round (2026-10-03)

**Question asked.** The sponsor's note on PR #69 (2026-10-02) held the merge on five points: the copyright posture (paraphrase plus locators and digests, not verbatim ISO text), a human DEC-003 sign-off (the extraction is evidence and does not accept the risk metric), who fixes the catalog under FX-1, whether Annex H becomes a fixture given the Table H.5 and H.6 mismatch, and a remap of §5 and §6 once #66 landed (titled `proposed.8`; it merged at `proposed.9`). It added that the open questions in the PR body stand. The student asked the agent to double-check the note, make the fixes and finish the pull request.

**What was produced.**
- §5 and §6 remapped onto `proposed.10` (#66 and #77 merged after the note). No fit changed. New in the table: the asset's owner, ThreatActor as a facet of a Party, impact on the threat's risk record, the mitigation status, and the risk rule that presumes a path-to-threat-scenario link no model names. §5.3 checks the lifecycle enum (a counterpart for each 21434 stage) and the owner and business-impact axis (beyond 21434's road-user viewpoint). §6.2 gains items 12 to 16.
- §7 records the sponsor's posture, library PR #9, and a conflict the posture creates: FX-1 requires verbatim normative and requirement text with no exception, so a paid standard cannot meet it as written.
- §4.4 suggests a resolution for the fixture (follow Table H.5 and Figure H.3) and shows it changes no expected result.
- §8 lists the five holds with what the note says and what is still open, including whether the merge and the DEC-003 ADR wait on each other.
- Three older sentences reworded because the copy check found them too close to the standard: §3.2 (scaling, G.1), §3.3 (who sets a CAL) and §4.2 (a Table H.3 row).
- This entry renumbered from 0011 to 0012.

**Double-checks.** The Table H.5 and H.6 mismatch was confirmed again on page images (PDF pages 80 and 81): Table H.5 says OFF and gives the OBD path four steps; Figure H.3, which draws only the cellular path, also says off; Table H.6 says ON and gives the OBD path three steps. The new claims about the standard were read again in the local copy, among them 15.1, 15.4 NOTE 3, RQ-15-04 with its notes, RQ-15-05, RQ-15-09, RQ-15-15 to RQ-15-17, RQ-09-05, RQ-09-06, Table 1, RC-15-11 to RC-15-14, 3.1.26, 3.1.31, 12.1, 14.1, the titles of Clauses 9 to 14, and Annexes E, F and G. The claims about the proposal were checked against `proposed.10` on `main` (`05aca39`).

**What a human accepted.** The student asked for the round on 2026-10-03; review of the changes is pending.

**Rejected or corrected.** Two independent fact-check subagents checked this round (32 findings, none rejected; searches.md, Tool runs). The ones that changed a claim:
- **Figure H.3 has no OBD path.** It draws only the cellular path, so the fixture suggestion now takes Table H.5 as the reference, with Figure H.3 agreeing.
- **"End-user" is in the standard once** (RQ-13-01, NOTE 5), so the report no longer calls it the proposal's word only.
- **The note's holds are not all answers.** The note also says the open questions in the PR body stand, so §8 now reports what the note says instead of calling it answers.
- **A vehicle owner is a road user** (3.1.31), so only the loss of an owner who is not a road user lies outside 21434's ratings.
- **The proposal's per-owner risk values** were said to be kept apart from S, F, O and P; the proposal does not say which impact they use.
- Smaller fixes: an exact quote ("annexes `not-reviewed`"), "by our reading" added where a mapping is ours, the per-owner rule's unnamed path-to-asset link, and the dates and versions of #66 and #77.

## Next steps

- Human review and sign-off of RPT-0007, by the student and then the sponsor.
- Sponsor decisions still open from RPT-0007 §8: the exceptions the text posture needs in the library's draft policy and in FX-1, who rewrites the catalog's provision texts, whether the reviewed sections meet the DEC-003 blocker and whether the catalog must be fixed first, the order of this merge and the DEC-003 ADR, and whether Annex H becomes a fixture.
- Library PR #9 (metadata fixes) to review and merge; then bump tmodel's library pin and update RPT-0007's sources.md record ids.
- Revisit §5 and §6 when the proposal moves past `proposed.10`.
