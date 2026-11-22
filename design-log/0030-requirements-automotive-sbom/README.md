---
schema: "archdoc/v1"
id: DL-0030
title: "Requirement extraction, automotive and SBOM lane: ISO/SAE 21434, UNECE R155 Annex 5, BSI TR-03183-2 (#172)"
type: process
status: draft
version: "0.3.0"
date: "2026-11-02"
updated: "2026-11-13"
record: DL-0030
bears_on: [DEC-001a, DEC-002, DEC-009]
defers_to: ARCH-0001
---

# DL-0030: Requirement extraction, automotive and SBOM lane (#172)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code drafted it. It produced the three files in `research/0017-requirements-extraction/` and the library summaries of `unece-r155` and `bsi-tr-03183-2`. Issue: #172 (parent #168).

## Question asked

#172 asks for the lane's requirement extraction under ADR-0012:

- **`iso-sae-21434-2021`:** clauses 8, 9, 10 and 15, paraphrase only.
- **`unece-r155`:** Annex 5. Part A threats become stub ThreatInstances, and Part B and C mitigations become Requirements, each restating a stub Mitigation.
- **`bsi-tr-03183-2`:** its SBOM content and format requirements.

Every link is a `proposed` Assertion. The student asked the agent to start #172.

## Prompt used

The agent followed the prompt in #172 ("Prompt for your coding agent"), with these differences:

- The session was rooted in a `library` worktree, not in `tmodel/`. The tmodel worktree `topic/0017-automotive-sbom` and the library worktree `topic/0017-r155-bsi-summaries` were added to it.
- `CLAUDE.md`, ADR-0012, the object-model classes, `mvp-02` and `check-edges.py` were read directly from `main` (8722e4b).

The prompt, as given in the issue:

```text
You are extracting requirements for the tmodel threat-modeling knowledge graph.
Read first: tmodel/CLAUDE.md, spec/ADR-0012-requirement-in-core.md, the Requirement / Mitigation /
Assertion / Review classes in spec/schema/tmodel-object-model.linkml.yaml, and the requirements
block in spec/vectors/mvp-02-automotive-ecu.yaml (the worked example). Then follow the output
format in GitHub issue Threat-Radar/tmodel#172 exactly.

For each library record in: iso-sae-21434-2021, unece-r155, bsi-tr-03183-2
1. Read library/records/<body>/<id>/record.yaml, summary.md and, if present, distilled/requirements.yaml.
   If distilled/requirements.yaml exists, take designator, locator and normativity from it; do not re-extract.
   If it does not exist, read the source at the record's content.url and cite clause/section/table locators.
2. Select the provisions in scope for this lane (see the issue's "Scope"). List the ones you skip, with a reason.
3. For each selected provision, write a Requirement:
   - id requirement:<record-id>-<designator-slug>
   - a ONE-sentence paraphrase in your own words. If the record is a licensed standard (ISO/IEC/SAE),
     never copy its wording, even from requirements.yaml.
   - text_origin, requirement_kind (technical|process|audit|documentation|organizational|other),
     normativity (mandatory|recommended|optional|informative|conditional), source_ref, source_locator
   - applies_to_family only when the source states the product scope.
4. Propose links ONLY as Assertions with assertion_status: proposed and a description giving the basis
   (locator + one-line reason): addresses -> CWE / CAPEC / ATT&CK / the source's own named threats
   (add stub nodes with catalog_ref); stated_as -> when the source lists a mitigation/control that
   the requirement restates; refines / derived_from -> between provisions of the same source.
   Never fill link slots directly. Never write a Review. Never set assertion_status: accepted.
5. Do not invent ids, designators, CWE/CAPEC numbers or clauses. If unsure, leave the link out.
6. Validate each file with linkml-validate (ExampleModelCore) and check-edges.py, and fix it until both pass.
7. Write the per-record coverage line (in source / converted / skipped + reasons) and a
   design-log/NNNN-<slug>/README.md (question, this prompt, output, and a blank "human accepted/rejected" section).
Stop there. A human reviews the proposed links next.
```

## What was produced

| File | Requirements | Other nodes | Links (all proposed by the agent) |
|---|---|---|---|
| `iso-sae-21434-2021.yaml` | 49 | 1 party | 43 (`derived_from` and `refines` between provisions) |
| `unece-r155.yaml` | 26 | 23 Mitigation stubs, 70 ThreatInstance stubs, 1 party | 106 (26 `stated_as`, 78 `addresses`, 2 between statements) |
| `bsi-tr-03183-2.yaml` | 59 | 1 Weakness stub (CWE-1395), 1 party | 26 (22 between statements, 4 `addresses`) |

These are the counts after the review on tmodel#196, with the ISO row updated for tmodel#154, when the seven provisions left out on review came back (see "The seven brought back"). @Clovier accepted 10 links per file after checking them against the sources; 4 of the ISO ones went with the seven provisions left out on review, and @Clovier accepted 4 more in their place (see "What a human accepted").

**Coverage, per record:**

- **`iso-sae-21434-2021`:** 118 provisions in the record, 49 in scope (clauses 8, 9, 10 and 15). All 49 are converted: 42 after the review on tmodel#196, and the seven whose library text was broken came back for tmodel#154 (see "Problems found in the sources" and "The seven brought back"). 69 were skipped as outside this lane (clauses 5, 6, 7, 11, 12, 13 and 14).
- **`unece-r155`:** in Parts B and C of Annex 5, all 23 numbered mitigations (M1 to M24; M17 is not used) and three more statements inside the M7 and M23 cells were converted. In Part A, all 67 examples of Table A1 became ThreatInstance stubs, plus 30.1 to 30.3, which only Table C3 lists. The regulation's paragraphs 1 to 12 and Annexes 1 to 4 are outside this lane.
- **`bsi-tr-03183-2`:** 59 Requirements. All 52 capitalized normative statements in §3 to §7 were converted. After review, so were the six notes that state a duty, a recommendation or a permission (§3.2.8, two in §5.1, §5.2.1, two in §5.2.2), and the §3.2.5 sentence, with no keyword, that the referenced BOM's information prevails. Not converted:
  - §3.1's pointer to section 5, which the §5 requirements cover;
  - the definitions (§3.2.3, §3.2.6 to §3.2.9), apart from the §3.2.8 note;
  - the five notes that only explain (§3.1, §3.2.5, the format notes under Tables 2 and 3, and §5.2.5);
  - the appendix (§8), which the guideline calls "additional, explanatory information".

**Library side** (the companion library PR): `unece-r155` and `bsi-tr-03183-2` move from `stub` to `summarized`, with the summary's six sections, applicability, implementations and usefulness. Neither is extracted to FX-1.

## How it was checked

- **The two required checks.** `linkml-validate` against `ExampleModelCore` (LinkML 1.12.1) and `check-edges.py` pass on all three files, with exit code 0. Rerun on 2026-11-03 on the final files, after the Reviews and the review fixes: `linkml-validate` reports no issues, and `check-edges.py` resolves every reference (ISO 79 objects and 72 references, R155 236 and 232, BSI 97 and 72). `check.py` (#197) passes all three.
- **The checks catch errors.** Planted errors fail them: a bad `requirement_kind` fails `linkml-validate`, and a dangling assertion object and a `conformance_status` slot each fail `check-edges.py`.
- **Paraphrase check against the source wording:**
  - **ISO/SAE 21434.** The longest run of words any `text` shares with the library's copy of the standard is 5, and those runs are defined terms such as the impact scale. One draft repeated 16 words; it was rewritten before the file was kept.
  - **R155.** No run of 8 or more words.
  - **BSI.** Only section numbers and field-name lists run to 8 or more words.
- **Digests.** The R155 and BSI PDFs fetched on 2026-11-02 match the digests in their records. ISO/SAE 21434 was not re-read for the first 42 provisions: they rest on the record's `requirements.yaml`. The seven brought back for tmodel#154 were read from the licensed copy (see "The seven brought back").
- **R155 pairings.** These were read from the rendered pages of Tables B1 to B8 and C1 to C3, because the text extraction drops merged cells (one mitigation for several rows). Every threat example has at least one paired mitigation.
- **CWE-1395.** Its name was checked on cwe.mitre.org.

## Choices the agent made, open to review

- **Normativity:**
  - ISO's `requirement`, `recommendation` and `permission` become mandatory, recommended and optional, copied rather than re-read. "If X, then shall" provisions stay mandatory, with the condition in the text.
  - R155's numbered mitigations are all `conditional`. §7.3.4 requires every Part B or C mitigation relevant to an identified risk, or another appropriate one.
  - The unnumbered data-correlation line in the M7 cell is `optional`, because the annex says the attacks "could be mitigated" that way.
  - BSI's capitalized MUST, SHOULD and MAY become mandatory, recommended and optional. "MUST ... if it exists" becomes conditional.
  - A BSI note converted after review takes its normativity from its plain wording (must or has to, recommended, may), because §2 gives BCP 14 force only to capitalized keywords. Each such Requirement's `description` says it comes from a note.
- **Scope of BSI Table 3.** Each Table 3 Requirement states which components it covers. Creator, name and version apply to every kind; dependencies and distribution licences also to logical components; filename, hash and the three file properties only to fully described components that are not logical (§3.2.1, §3.2.2, §3.2.4, §3.2.5, §5.1).
- **Families:**
  - Two values are new: `family:unece-r155-vehicle` (the regulation's own scope, §1.1 and §1.2) for Part B mitigations, and `family:vehicle-backend` (Annex 5 paragraph 1) for Part C.
  - M3 gets only the back-end family, although Table B2 also lists it, because its text is about back-end systems. M19 gets none, because it binds organizations, not a product.
  - ISO and BSI get no family. The ISO provisions are process obligations, and the library record does not state the standard's scope. BSI covers the SBOM of any software product.
- **`derived_from` or `refines`:**
  - A provision that applies another provision's method or output is `derived_from` it. This covers explicit cross-references and "in accordance with 15.x", which points at that subclause's provision.
  - A provision that adds detail to the same obligation `refines` it.
  - Explicit bracketed references are `high` confidence. Clause-number references and "the X" back-references are `medium`. Links that rest only on Annex H fragments are `low` (none remain since tmodel#154).
- **Unnumbered statements in R155 cells.** The extra lines in the M7 and M23 cells became their own Requirements: `m7-data-correlation`, `m23-testing` and `m23-system-design`. Their locators name the table rows. Their `source_ref` keeps the cell's M number, and no designator was invented.
- **BSI `source_ref`.** It points at the section number, such as `#5.2.2`. The guideline has no provision ids, and a slug could be mistaken for one.
- **CWE-1395 links.** These are the agent's inference; the guideline names no CWE. Two are `medium`, because §1 and Table 5 tie SBOM data to vulnerability lookup. Two are `low`.

## Problems found in the sources

- **The library's ISO/SAE 21434 `requirements.yaml` had broken text for 7 of the 49 provisions in scope:**
  - RQ-09-01, RQ-10-01, RQ-10-04 and RQ-15-17 are cut off partway through their lists.
  - RQ-09-03 and RQ-09-04 hold Annex H examples and the bibliography.
  - RQ-10-08 holds Annex E table text.

  These seven were first kept, each with a `description` saying the text was broken. After review they were left out, with their 14 links, because a paraphrase of broken text is not source-supported. They could come back once someone checked them against a licensed copy and the library record was fixed from the purchased PDF. Both have happened: Threat-Radar/library#47 completed the seven from the licensed copy, and they are back in `iso-sae-21434-2021.yaml` (see "The seven brought back").
- **UNECE R155 Annex 5** (original version):
  - Table C3 cites threats 30.1 to 30.3, which Table A1 does not list.
  - Table A1 has no threat 14 and no example 22.1.
  - M17 is unused.
- **BSI TR-03183-2's** source-code hash field has no defined method yet (§5.2.5).

## What a human accepted

- **The sample.** On 2026-11-02 @Clovier checked 30 proposed links against their source passages, 10 per file, and accepted all 30.
- **How it is recorded.** Each accepted link has a Review in its file, and its Assertion is now `accepted`. No accepted link was written into a slot; the accepted Assertion carries the decision.
- **What the sample covers.** It mixes confidence levels. It included the ISO link that then rested on the record's Annex H text (RQ-09-03 `derived_from` RQ-15-15), which left the sample with the seven on tmodel#196 and is back as `proposed`, now resting on the provision itself. It includes all four BSI links to CWE-1395, which are the agent's inference.
- **After the review on tmodel#196.** Four of the ten accepted ISO links touched the seven provisions left out, so they were removed with them: RQ-09-06 `derived_from` RQ-09-03, RQ-10-05 `derived_from` RQ-10-04, RQ-08-07 `derived_from` RQ-15-17 and RQ-09-03 `derived_from` RQ-15-15. To get back to #172's 10, @Clovier checked 4 more ISO links against the source on 2026-11-03 and accepted all 4: RC-15-13 `refines` RC-15-11, RC-15-14 `refines` RC-15-11, RQ-10-10 `derived_from` RQ-10-05 and RC-15-11 `refines` RQ-15-10. Each has a Review in the file.
- **Still unreviewed.** The other 145 links (33 ISO, 96 R155, 16 BSI) stay `proposed`, with no Review. 17 of the ISO ones arrived with the seven provisions for tmodel#154: 14 came back and 3 are new. The five new BSI links are `refines` from the note Requirements to the statements they narrow.

## What was rejected, and why

- **No human rejections.** None of the 30 sampled links was rejected.
- **The agent's own corrections** (not human rejections). Before the files were kept, the agent rewrote drafts that repeated source wording:
  - one ISO paraphrase that repeated 16 words of the standard, and six that repeated 6 to 9;
  - two R155 texts and five BSI texts that repeated 8 to 11 words of those free sources.

## Review on tmodel#196 and library#42 (@kriishnaa-18, 2026-11-03)

@kriishnaa-18 reviewed both PRs and asked for four changes on tmodel#196 and two on library#42 before merging. @Clovier asked the agent to apply them, and chose how to handle the first.

1. **ISO/SAE 21434 source accuracy.** Seven Requirements rested on broken library text. Checking them against a licensed copy was not possible, so @Clovier chose to leave them out until it is (see "Problems found in the sources"), and then reviewed 4 more links so the file keeps 10 Reviews.
2. **BSI component fields.** The Table 3 Requirements read as if every component needed every field. Each now states its scope, following §3.2.1, §3.2.2, §3.2.4, §3.2.5 and §5.1 (see "Choices the agent made, open to review").
3. **BSI notes.** §2 does not make notes informative, so each of the 11 notes in §3 to §7 was read on its own. Six state a duty, a recommendation or a permission and are now Requirements; five only explain. A §3.2.5 sentence with no keyword, found during the same check, was converted too. The BSI file goes from 52 to 59 Requirements, with five new proposed `refines` links.
4. **Validation evidence.** The checks were rerun on the final files (see "How it was checked").

On library#42, the BSI summary now gives the reduced field sets for logical, identified and referenced components; says that §2 does not make notes informative, and lists the notes that state duties; and says the guideline is separate from the CRA and does not claim that following it establishes conformity.

## The seven brought back (tmodel#154)

Threat-Radar/library#47 completed the 16 flagged entries of the library record from the licensed copy, and Threat-Radar/library#48 reworded the paraphrases that stayed close to the standard. With the source text complete, the seven provisions left out on review are back: RQ-09-01, RQ-09-03, RQ-09-04, RQ-10-01, RQ-10-04, RQ-10-08 and RQ-15-17. Claude Code drafted the changes.

- **Text.** Each `text` was written for this file from the licensed copy, the PDF whose sha256 is the record's digest, and six were reworded on 2026-11-13 (see below). None is copied from the standard or from the library's paraphrase. Some of the other 42 texts share longer runs with the library's current paraphrases (up to 11 words in a row, RQ-09-11); those paraphrases came later, from Threat-Radar/library#44 (merged 2026-11-07) and #48, while this file's texts date from 2026-11-02. On 2026-11-08 the longest run any of them shared with the standard was 5 words, and those runs were step names, list names and clause numbers. Designator, locator and normativity come from the record, as for the other 42.
- **The 14 links that left with them are back,** all `proposed`. Each basis was rechecked against the licensed copy. Three had rested on the broken record text: RQ-09-04 `derived_from` RQ-15-17 and RQ-09-03 `derived_from` RQ-15-15 cited the record's Annex H text, and RQ-08-07 `derived_from` RQ-15-17 cited the cut-off record. They now cite the provisions themselves. RQ-09-04 `derived_from` RQ-09-03 now rests on RQ-09-04's own reference to RQ-09-03 instead of on RQ-09-07 b). Three confidences rose to match the real text: RQ-09-04 `derived_from` RQ-15-17 from low to medium, RQ-09-03 `derived_from` RQ-15-15 from low to medium, and RQ-09-04 `derived_from` RQ-09-03 from medium to high.
- **Three new links,** all `proposed`. RQ-09-03 `derived_from` RQ-09-01 and RQ-09-03 `derived_from` RQ-09-02: RQ-09-03 starts from the item definition, which §9.3.2 produces through those two provisions (WP-09-01). RQ-10-08 `derived_from` RQ-10-01: RQ-10-08 verifies the specifications that RQ-10-01 defines.
- **A choice open to review.** RQ-09-03 runs the steps of 15.3 to 15.8. Only the 15.8 link (to RQ-15-15, which works out the risk value) is kept, because it was one of the 14. Links from RQ-09-03 to the 15.3 to 15.7 provisions are left for a reviewer to add. 15.4 holds a single provision, RQ-15-03, so RQ-09-03 `derived_from` RQ-15-03 is the clearest candidate.
- **Reviews.** None of the 17 has a Review yet. Of the four links @Clovier accepted on 2026-11-02 that left with the seven, one (RQ-09-03 `derived_from` RQ-15-15) was accepted on the Annex H text. Their Reviews were not restored, since a Review records a check of the text as it then stood; they can be checked again against the new text. The file keeps its 10 Reviews.
- **Reworded on 2026-11-13.** A check against the library record's paraphrases (which Threat-Radar/library#47 and #48 checked against the licensed copy), an independent agent's check and the licensed copy itself changed six texts, three bases and two confidences:
  - RQ-09-01 now says to identify the item information, not to record it.
  - RQ-10-01 now says to define the specifications; the earlier wording only said to base them on their inputs.
  - RQ-09-03 says "these clause 15 steps", so it cannot be read as all of clause 15, and no longer opens with the same five words as the library's paraphrase.
  - RQ-10-04 keeps its six criteria in wording further from the standard's list and from the library's.
  - RQ-10-08 says verify instead of check.
  - RQ-15-17 no longer opens with the standard's own first four words.
  - The basis of RQ-09-06 `derived_from` RQ-09-04 says that retaining the risk counts only when it rests on assumptions in the RQ-09-03 analysis; the basis of RQ-08-07 `derived_from` RQ-15-17 says that only one of RQ-08-07's two routes uses 15.9; and the basis of RQ-09-04 `derived_from` RQ-09-03 says RQ-09-04 cites RQ-09-03 by number.
  - RQ-10-08 `derived_from` RQ-10-01 and RQ-09-04 `derived_from` RQ-15-17 are `medium`, by the rule above: the first rests on a back-reference and the second on a clause number, like their sibling links.

  The same day, the texts and bases were checked against the licensed copy again. The longest run any of them shares with the standard is 5 words, and word-sequence closeness is below 0.70 for all but RQ-09-03, whose shared words are its six step names and their clause numbers.
- **Checks.** On the final files, `linkml-validate` (core container), `check-edges.py` and `check.py` pass for all six extraction files, and the converter's tests pass. `check-edges.py` now counts 103 objects and 106 references in the ISO file.
