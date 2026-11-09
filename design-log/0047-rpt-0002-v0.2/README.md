---
schema: "archdoc/v1"
id: DL-0047
title: "RPT-0002 v0.2: Attack Flow, surveys, STRIDE origin, evidence, gap analysis, adversarial review"
type: process
status: draft
version: "0.2.0"
date: "2026-10-22"
updated: "2026-11-09"
record: DL-0047
---

# DL-0047: RPT-0002 v0.2, threat model frameworks

AI-assisted research record for the RPT-0002 v0.2 story in #36, per `CLAUDE.md`.
Student: @paria03. Report:
`research/0002-threat-model-frameworks/report.md`; library records merged in
Threat-Radar/library#30. Every claim an agent returned was re-checked by hand
against its source before it entered a record or the report; the rejections below
are the evidence of that check.

## Phase 1: MITRE Attack Flow as its own framework (2026-10-22)

### Question asked

#36: cover MITRE Attack Flow as its own framework (section, comparison row, library
record).

### What was produced

- Library record `mitre-attack-flow` (spec, summarized), pinned to `docs/language.rst`
  at tag v4.1.0 with a digest; also the digests of `introduction.rst` and the JSON
  schema.
- Report §9.3 (Attack Flow), a comparison-table row, §9.4 (the old §9.3), and
  corrections in §9.2 and §11. Section numbers cited by other documents (§2–§5,
  §9–§11) were kept.

### Method

The assistant read the GitHub release data, the language page, the introduction,
the changelog and the JSON schema at tag v4.1.0. A separate fact-checking agent at
maximum effort, which had not seen the draft's reasoning, then checked the section
and the record against the same sources and the Builder's code.

### What a human accepted

@paria03 asked for the independent re-check and accepted its corrections.

### What was rejected, and why

| proposed | by | outcome | why |
|---|---|---|---|
| "an arrow is a dependency, not a time order" | assistant (first draft) | rejected | the sentence before the quoted line says "the second action cannot be executed until the first action completes successfully", so a dependency implies a partial order |
| "only Attack Flow combines all three" properties, with none of the methods having them | assistant (first draft, §11 item 2) | rejected | corrected once the dependency reading was fixed; later qualified again (Phase 5) |
| ATLAS, D3FEND and Fight Fraud "added in v4.0" | assistant | rejected | the v3.1.0 release notes (2026-04-21) add them |
| schema link `…/attack-flow/stix/attack-flow-schema-2.0.0.json` | assistant | rejected | returns HTTP 404 (so does the schema's own `$id`); replaced by the file at the tag |
| seven `scope` values cited to `language.rst` | assistant | rejected | `language.rst` at v4.1.0 lists five; the other two were added to the schema in place |
| "the 2.0.0 schema" as fixed | assistant | rejected | it was widened in place (`attack-tree` 2024, `emulation-plan` 2025) without a version change |

## Phase 2: peer-reviewed surveys and STRIDE's origin (2026-10-22)

### Question asked

#36: add at least one peer-reviewed survey beyond SEI 2018, and resolve the STRIDE
source `shostack-threat-modeling-2014`, which had no record.

### What was produced

Records `tuma-2018-threat-analysis-slr` (summarized, read in the first author's
thesis reprint), `xiong-2019-threat-modeling-slr` (stub), `kohnfelder-garg-1999-threats-to-our-products`,
`shostack-2008-experiences-threat-modeling-microsoft` (both summarized) and
`shostack-threat-modeling-2014` (stub, with ISBN); the report's surveys paragraph
and STRIDE history.

### Method

Two research agents ran in parallel at maximum effort, one per question, with
instructions to verify every DOI through Crossref and give only URLs they opened.
The assistant then re-checked every DOI, digest, quotation and number used.

### Choices the agent made, open to review

- Tuma et al. (2018) is read in its thesis reprint; page numbers are the thesis's.
- The thesis repository stamps every download differently (same size, a different
  digest each time), so the recorded digest identifies only the copy read.

### What a human accepted

@paria03 chose Tuma et al. (2018) as the main survey and Xiong & Lagerström (2019)
as a stub.

### What was rejected, and why

| proposed | by | outcome | why |
|---|---|---|---|
| Xiong & Lagerström (2019) as the main survey | survey agent (its first rank) | declined | only its abstract could be read (paywalled); Tuma et al. was read in full |
| Tatam et al. 2021, Granata & Rak 2024, Huang et al. 2026, Tran et al. 2026, and others | survey agent | not added in v0.2 | narrower scope (APT, tools, cyber-physical) or not a survey of methods |
| thesis "Chalmers, 2020" | survey agent | corrected | the title page says University of Gothenburg, 2021 |
| "STRIDE … adopted by Microsoft in 2002" as fact | report v0.1 (from SEI) | rejected as fact | the only source is SEI 2018; no primary source supports it. Attributed to SEI |

## Phase 3: comparative evidence (2026-10-22)

### Question asked

Find peer-reviewed studies that compare or test threat-modeling methods, as evidence
for the gap analysis.

### What was produced

Records `scandariato-2015-stride-descriptive-study`, `verreydt-2024-threat-modeling-practice`,
`mbaka-tuma-2024-stride-replication` (summarized) and
`karpati-2014-attack-trees-misuse-cases`, `lallie-2018-attack-graphs-fault-trees`
(stubs).

### What a human accepted

@paria03 accepted adding the three open, fully read studies as records and the two
paywalled ones as stubs.

### What was rejected, and why

| proposed | by | outcome | why |
|---|---|---|---|
| quotation "not different enough to make a practical impact" (Mbaka & Tuma) | comparison agent | not used | it is from the journal abstract; the text read is the arXiv preprint, which does not contain it |
| Verreydt et al. as "7 large organizations" | comparison agent | narrowed | the title and text say large Dutch organizations |
| findings from Karpati et al. 2014 | comparison agent (from search snippets) | not used | no abstract or full text could be read |

## Phase 4: gap analysis (2026-10-22)

### Question asked

#36: a gap-analysis table: what the field has, what tmodel lacks, a
recommendation, and where it is decided, taking no decision.

### What was produced

§11 item 7, measured against the accepted core (ADR-0010, `main` at `e1ae8c3`).

### What was rejected, and why

| proposed | by | outcome | why |
|---|---|---|---|
| G2 citing #130's gap P4 as an AttackStep-to-AttackPattern link | assistant | corrected | P4 is an AttackStep-to-Weakness slot |

## Phase 5: adversarial review (2026-10-22)

### Question asked

#36: an adversarial review pass by a fresh agent (coverage, citations), with
findings fixed and rejections recorded.

### Method

A fresh agent at maximum effort, which had not written the report, read the
report, its logs, the 27 cited records, the ADRs, the schema, the decision register
and the sibling reports, and re-opened primary sources. It returned 42 findings
and judged that six groups blocked calling the report reviewed. The assistant
re-checked the findings it applied against the sources.

### What a human accepted

@paria03 accepted fixing the six blocking groups and the smaller errors now, and
leaving the larger new analysis for the next iteration.

### Applied

- **Decision status:** the decisions the report informs are accepted (DEC-001a,
  DEC-002, DEC-003, DEC-005); the report takes no decision and amends no ADR.
- **Citations:** §11 cites its evidence by record id; Lallie et al.'s finding is
  reported from its abstract; the Xiong and Lallie stubs have abstract-only
  summaries.
- **§11:** the gap table reframed as options with routes (G1–G6), with G1 and G5
  completed (the OTM import, DL-0013, the `dfd` projection; ADR-0006's
  business-impact rule); the two evidence rows moved out with their caveats
  (students, a catalog baseline, review burden); the closing paragraph corrected.
- **STRIDE:** the Kohnfelder/Garg versus Garms/Garg/Howard conflict disclosed;
  SEI's 2002 date handled consistently, with *Writing Secure Code* (2001, 2002, as
  listed by Shostack 2008); Scandariato's primary figures.
- **Coverage and reconciliation:** the ISO/SAE 21434 TARA row filled from
  RPT-0007; CAPEC, OTM and CycloneDX TM-BOM cross-referenced; the "only …" claims
  qualified; RPT-0005's G2 reconciled; RPT-0003 and RPT-0014 cross-referenced;
  language-model generation named as a second route.
- **Attack Flow:** the Builder's v4 confidence scale stated exactly, and the
  generation guide's "validate … by updating the Confidence property" confirmed;
  "partial order" limited to acyclic flows.
- **Smaller:** DREAD's scale (0/5/9/10 for Discoverability), CVSS versions, VAST's
  automation claim, Trike's "only", SAND marked unsourced, AI assistance disclosed in
  the front matter.

### What was rejected or not applied, and why

| finding | outcome | why |
|---|---|---|
| the Builder's v3 confidence scale (Speculative 0, Very Doubtful 10) | not applied | could not be verified: the v3 file was not found at tag v3.2.0. Only the v4 scale, which was verified, is stated |
| MAESTRO "extends … STRIDE, PASTA and LINDDUN" | rejected | the record says "extends rather than replaces frameworks like STRIDE"; only STRIDE is named |
| OCTAVE FORTE falsifies §6's "three variants" | not applied | the method could not be verified in Crossref, OpenAlex or the guessed SEI URL; left for the next iteration |
| attack-tree antecedents (threat trees; Salter et al. 1998) | partly applied | "introduced by" became "popularised by"; the antecedents are not cited without a record |
| hTMM's formal source (CMU/SEI-2018-TN-002) | not applied | not verified |
| merge the library records and pin the submodule before calling the report reviewed | deferred to the PR step | it is the order of the PRs: the library PR merges first, then the tmodel PR bumps the pin |
| version 0.2.0 and `updated` | deferred | done once at the end of v0.2 |

### Deferred to the next iteration

These are new analysis rather than corrections: a crosswalk from each framework's
concepts to the accepted classes; a pinned definition of "attack path"; gate
semantics (top-down tree AND/OR versus tmodel's join); a CAPEC section and
sequential-AND trees and logical attack graphs as prior art; gap rows for
step-level mitigation, attacker capability and catalog versioning; a domain-fit
axis; sources for the adoption claims; a coverage table against SEI's 12 and Tuma's
26 techniques; EMB3D and a "not covered, and where" list; a Tooling paragraph in
§9.1.

## Phase 6: clarity pass (2026-10-22)

### Question asked

#36: a separate clarity pass — an overview, a conclusion, defined acronyms, a lead-in
for every table — so the report reads top to bottom without other context.

### Method

A fresh editing agent at maximum effort edited a copy of the report, with rules
not to change any fact, number, quotation, record id, identifier, URL, section
number or the front matter, and not to add or remove findings. A script then
compared the protected items (numbers, quotations, backticked ids, identifiers,
URLs, headings) in the original and the edit: none was removed; the additions are
in the new sections. The assistant read the new Overview, abbreviations section,
Conclusion and the restructured §2 against §11 and §2 before applying the edit.

### What was produced

An Overview; an "Abbreviations and identifiers" section before §1; a Conclusion
after §11; lead-ins for all tables; acronyms defined at first use; tightened prose;
§2's history in its own paragraph; "Sources." lines added to §9.1 and §9.2. Section
numbers and §11 items 1–7 (G1–G6) are unchanged.

### What was rejected, and why

| proposed | by | outcome | why |
|---|---|---|---|
| tmodel described as "the project's threat-modeling knowledge graph" | editing agent | corrected | tmodel is a threat-modeling tool built on a knowledge graph |
| British spelling, chosen by the editing agent as the report's majority form | editing agent | changed | @paria03 chose American spelling throughout, matching "modeling" in the project's name; quotations, titles, record ids and links were left as written |

## PR preparation (2026-11-03)

@paria03 requested the remaining #36 preparation and a report PR. Library #30
has merged. The report's `library_commit` and the submodule pin now both name
`f1443afa4519d1f5df1f6f809be973756176e796`, the merge containing its references.
This advances the existing pin; no library records are authored in this change.
The identical untracked search-log copy was archived outside the repository.
The research index identifies the report as draft 0.2.0, and this log initially used
DL-0033 to avoid colliding with the existing Requirement design log DL-0025.
That number was later taken on main; the 2026-11-09 correction renames this
log DL-0047 after checking main and open PR file lists.

The substantive corrections and the clarity pass are recorded above. The larger
analysis listed under "Deferred to the next iteration" remains deferred. Human
review of the completed report, including a cold read of its overview and
conclusion, remains pending. This preparation does not mark the report reviewed.

Validation before opening the PR:

- All 27 source-table record IDs resolve in the pinned library.
- Library validation: 601 records, 23 topics, 0 errors and 112 warnings. The
  warnings are reported by the already merged library snapshot; no library
  record changes are included in the tmodel PR.
- Engine library-loader regression tests: 36 passed, including the full pinned
  library.
- Archdoc: 25 documents, 0 errors. Publishing identity and relative-link checks
  pass for all 423 published pages; `git diff --check` passes.

## Review corrections (2026-11-09)

### Question asked

Finish the remaining #36 work after the #63 route-rating implementation.
Address PR #200's review findings without accepting a new architecture decision.

### Changes prepared

- Correct both Verreydt passages against the original SOUPS paper, §3.3 / RQ3.1,
  p. 477. The downloaded PDF's SHA-256 matches the existing library record.
  Reassessment practices vary; no interviewed organization used CI/CD to trigger
  reassessment. The earlier claim that none ever reassess is withdrawn.
- Name Attack Flow as an exception to the traditional methods' lack of defined
  interchange formats in both §11 and the conclusion. Point G6 to MAP-0002's
  STIX extension-consumer boundary; general STIX import is not Attack Flow import.
- Keep Karpati as a metadata-only stub with no empirical findings used. Neither
  abstract nor full text was read; the source log's abstract-only label was
  unsupported and is corrected. Identify Shostack's existing stub consistently.
- Correct the search log's dependency/order wording and its stale claim that
  comparative evidence had not yet been searched.
- Identify the October 22 architecture/search baseline prominently. Note the
  later accepted ADR-0011/0012/0013 additions and the G4 implementation under
  review in #229; do not present historical G1/G5 as current missing classes.
- Rename this log to DL-0047. Main already uses DL-0033 and DL-0034; main and
  open PR file lists were checked before choosing the next free number.
- Complete the `mitre-attack-flow` extraction in the independent library
  worktree, using the repository's FX-1 skill. Separate artifact extractors
  read the primary sources; source contradictions are retained instead of
  repaired in extracted fixtures. Independent verification and cross-check
  must pass before the record declares those passes complete.

### Rejections

| proposed or earlier claim | result | reason |
|---|---|---|
| None of the seven organizations reassess after changes | rejected | The study reports varying reassessment practices and specifically no CI/CD-triggered reassessment. |
| No surveyed method defines a file format | rejected | Attack Flow defines a published STIX-based format. |
| Calling Karpati a controlled comparison | rejected | The retained metadata does not establish its study design; the report now says comparison. |
| Karpati abstract-only label | rejected | The recorded evidence establishes metadata, not a read abstract. |
| Reuse DL-0034 as suggested at the time of review | rejected | It has since been merged for the release pipeline; DL-0047 is free at preparation time. |
| Treat published schema validation as complete language conformance | rejected | The source has prose/schema differences, custom-type fallback, and whole-flow rules outside per-object validation. |
| Automatically mark extraction or the report human-reviewed | rejected | Automated checking is not the per-artifact human sign-off required by FX-1. |

### Human review

No new human acceptance is claimed by this correction. The report stays draft
and the extraction's `reviewed_by` values remain empty. Reviewer sign-off and
merges remain separate steps.


### Fresh automated report passes

A fresh adversarial reviewer independently enumerated the requested framework
groups and SEI's twelve methods, resolved all 27 source-log record IDs, checked
the Verreydt and Attack Flow digests and source claims, and verified the later
accepted ADRs and MAP-0002 boundary. It found no material blocker. Its minor
finding — the unsupported word "controlled" for the metadata-only Karpati
comparison — was applied and recorded in the rejection table above.

A separate fresh clarity reviewer read the overview, conclusion and full paper
without the chat. It found no material clarity blocker. Applied its bounded
polish: reinforce local baseline wording; expand SDL and CI/CD at first use;
clarify the unread PASTA book's existing metadata-stub label. A lead-in was
added to the revision table. No finding, decision, quotation, source identifier
or numeric result changed in this editing pass.

### Extraction cross-check corrections

The independent artifact cross-check caught two prose errors in the message
inventory. The dictionary datatype note had copied a binary/hex suffix rule
from the separate generic-property schema; the actual dictionary schema has
no such rule. That sentence was removed only from the dictionary note. The
bundle note now names the five Attack Flow SDO types as the individual objects
validated by the root schema, avoiding any suggestion that it validates the
extension-definition or creator identity grammar. No published schema,
fixture bytes or extracted normative requirement changed.


### Final dependency and validation

The full extraction is committed in the independent library branch
`topic/36-attack-flow-extraction` at
`a04e8899138a49c2dec7aaf4b8c3356c4c430d27`, based on library main `20399c2`.
The report's `library_commit` and the submodule pin both name that exact commit.
This also includes the already merged library-main updates since the old report
pin; they are not new records authored for this correction. The library PR must
be published and merged, and the final report pin checked against that merge,
before PR #200 is merged. No remote publication or merge is implied by this
local preparation.

Independent extraction verification and cross-check completed at maximum
effort with no unresolved material finding. All 22 source modals occur exactly
once in the 109 entries; ten language tables, 14 schemas/36 references and all
ten source fixtures were checked. Five JSON examples validate; the two custom
examples reproduce their upstream errors. Human artifact signatures stay empty.
One authored README hard-break was replaced with a blank line for whitespace
validation after the automated passes; no source fixture, schema, requirement
or semantic statement changed.

Final local checks:

- Library: 685 records, 24 topics, 41 fully extracted, 0 errors; 99 existing
  warnings remain, with none attributable to this extraction.
- Requirements schema: all 53 sets validate; artifact checker: 180 YAML files,
  0 parse/structural errors, 38 existing warnings, none on this extraction.
- YAML reader: 15/15 regression cases; export and reindex: all 685 bibliography
  entries, 0 dangling relations. FX-1 changed-record gate passes.
- Report: all 27 source-log IDs resolve at the exact new pin; archdoc: 28
  documents, 0 errors; publishing identity/link checks: all 425 pages clean.
- Engine library-loader/table/surface regression tests: 122 passed against the
  new pin. Staged whitespace checks pass in both repositories.

Publication still follows @paria03's approval rule. The report remains draft
0.2.1 and `reviewed: false`; teammate review and per-artifact human sign-off are
not replaced by these automated passes.
