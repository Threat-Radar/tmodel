---
schema: "archdoc/v1"
id: DL-0030
title: "Requirement extraction, automotive and SBOM lane: ISO/SAE 21434, UNECE R155 Annex 5, BSI TR-03183-2 (#172)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-02"
updated: "2026-11-02"
record: DL-0030
bears_on: [DEC-001a, DEC-002, DEC-009]
defers_to: ARCH-0001
---

# DL-0030: Requirement extraction, automotive and SBOM lane (#172)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code (claude-opus-5-5) drafted it in @Clovier's session, as one agent with no subagents. It produced the three files in `research/0017-requirements-extraction/` and the library summaries of `unece-r155` and `bsi-tr-03183-2`. Issue: #172 (parent #168).

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
| `iso-sae-21434-2021.yaml` | 49 | 1 party | 40 (`derived_from` and `refines` between provisions) |
| `unece-r155.yaml` | 26 | 23 Mitigation stubs, 70 ThreatInstance stubs, 1 party | 106 (26 `stated_as`, 78 `addresses`, 2 between statements) |
| `bsi-tr-03183-2.yaml` | 52 | 1 Weakness stub (CWE-1395), 1 party | 21 (17 between statements, 4 `addresses`) |

@Clovier has since accepted 10 links per file after checking them against the sources (see "What a human accepted").

**Coverage, per record:**

- **`iso-sae-21434-2021`:** 118 provisions in the record, 49 in scope (clauses 8, 9, 10 and 15). All 49 were converted. 69 were skipped as outside this lane (clauses 5, 6, 7, 11, 12, 13 and 14).
- **`unece-r155`:** in Parts B and C of Annex 5, all 23 numbered mitigations (M1 to M24; M17 is not used) and three more statements inside the M7 and M23 cells were converted. In Part A, all 67 examples of Table A1 became ThreatInstance stubs, plus 30.1 to 30.3, which only Table C3 lists. The regulation's paragraphs 1 to 12 and Annexes 1 to 4 are outside this lane.
- **`bsi-tr-03183-2`:** all 52 normative statements in §3 to §7 were converted. Not converted:
  - §3.1's pointer to section 5, which the §5 requirements cover;
  - the definitions (§3.2.3, §3.2.6 to §3.2.9);
  - the notes, whose lowercase "must" and "recommended" are not BCP 14 keywords (§2);
  - the informative appendix (§8).

**Library side** (the companion library PR): `unece-r155` and `bsi-tr-03183-2` move from `stub` to `summarized`, with the summary's six sections, applicability, implementations and usefulness. Neither is extracted to FX-1.

## How it was checked

- **The two required checks.** `linkml-validate` against `ExampleModelCore` (LinkML 1.12.1) and `check-edges.py` pass on all three files, with exit code 0.
- **The checks catch errors.** Planted errors fail them: a bad `requirement_kind` fails `linkml-validate`, and a dangling assertion object and a `conformance_status` slot each fail `check-edges.py`.
- **Paraphrase check against the source wording:**
  - **ISO/SAE 21434.** The longest run of words any `text` shares with the library's copy of the standard is 5, and those runs are defined terms such as the impact scale. One draft repeated 16 words; it was rewritten before the file was kept.
  - **R155.** No run of 8 or more words.
  - **BSI.** Only section numbers and field-name lists run to 8 or more words.
- **Digests.** The R155 and BSI PDFs fetched on 2026-11-02 match the digests in their records. ISO/SAE 21434 was not re-read: the file rests on the record's `requirements.yaml`.
- **R155 pairings.** These were read from the rendered pages of Tables B1 to B8 and C1 to C3, because the text extraction drops merged cells (one mitigation for several rows). Every threat example has at least one paired mitigation.
- **CWE-1395.** Its name was checked on cwe.mitre.org.

## Choices the agent made, open to review

- **Normativity:**
  - ISO's `requirement`, `recommendation` and `permission` become mandatory, recommended and optional, copied rather than re-read. "If X, then shall" provisions stay mandatory, with the condition in the text.
  - R155's numbered mitigations are all `conditional`. §7.3.4 requires every Part B or C mitigation relevant to an identified risk, or another appropriate one.
  - The unnumbered data-correlation line in the M7 cell is `optional`, because the annex says the attacks "could be mitigated" that way.
  - BSI's capitalized MUST, SHOULD and MAY become mandatory, recommended and optional. "MUST ... if it exists" becomes conditional.
- **Families:**
  - Two values are new: `family:unece-r155-vehicle` (the regulation's own scope, §1.1 and §1.2) for Part B mitigations, and `family:vehicle-backend` (Annex 5 paragraph 1) for Part C.
  - M3 gets only the back-end family, although Table B2 also lists it, because its text is about back-end systems. M19 gets none, because it binds organizations, not a product.
  - ISO and BSI get no family. The ISO provisions are process obligations, and the library record does not state the standard's scope. BSI covers the SBOM of any software product.
- **`derived_from` or `refines`:**
  - A provision that applies another provision's method or output is `derived_from` it. This covers explicit cross-references and "in accordance with 15.x", which points at that subclause's provision.
  - A provision that adds detail to the same obligation `refines` it.
  - Explicit bracketed references are `high` confidence. Clause-number references and "the X" back-references are `medium`. Links that rest only on Annex H fragments are `low`.
- **Unnumbered statements in R155 cells.** The extra lines in the M7 and M23 cells became their own Requirements: `m7-data-correlation`, `m23-testing` and `m23-system-design`. Their locators name the table rows. Their `source_ref` keeps the cell's M number, and no designator was invented.
- **BSI `source_ref`.** It points at the section number, such as `#5.2.2`. The guideline has no provision ids, and a slug could be mistaken for one.
- **CWE-1395 links.** These are the agent's inference; the guideline names no CWE. Two are `medium`, because §1 and Table 5 tie SBOM data to vulnerability lookup. Two are `low`.

## Problems found in the sources

- **The library's ISO/SAE 21434 `requirements.yaml` has broken text for 7 of the 49 provisions in scope:**
  - RQ-09-01, RQ-10-01, RQ-10-04 and RQ-15-17 are cut off partway through their lists.
  - RQ-09-03 and RQ-09-04 hold Annex H examples and the bibliography.
  - RQ-10-08 holds Annex E table text.

  Each affected Requirement says so in its `description`, and paraphrases only what the rest of the record supports. A human with the standard should check them, and the library record needs a fix from the purchased PDF.
- **UNECE R155 Annex 5** (original version):
  - Table C3 cites threats 30.1 to 30.3, which Table A1 does not list.
  - Table A1 has no threat 14 and no example 22.1.
  - M17 is unused.
- **BSI TR-03183-2's** source-code hash field has no defined method yet (§5.2.5).

## What a human accepted

- **The sample.** On 2026-11-02 @Clovier checked 30 proposed links against their source passages, 10 per file, and accepted all 30.
- **How it is recorded.** Each accepted link has a Review in its file, and its Assertion is now `accepted`. No accepted link was written into a slot; the accepted Assertion carries the decision.
- **What the sample covers.** It mixes confidence levels. It includes the ISO link that rests on the record's Annex H text (RQ-09-03 `derived_from` RQ-15-15), and all four BSI links to CWE-1395, which are the agent's inference.
- **Still unreviewed.** The other 137 links (30 ISO, 96 R155, 11 BSI) stay `proposed`, with no Review.

## What was rejected, and why

- **No human rejections.** None of the 30 sampled links was rejected.
- **The agent's own corrections** (not human rejections). Before the files were kept, the agent rewrote drafts that repeated source wording:
  - one ISO paraphrase that repeated 16 words of the standard, and six that repeated 6 to 9;
  - two R155 texts and five BSI texts that repeated 8 to 11 words of those free sources.
