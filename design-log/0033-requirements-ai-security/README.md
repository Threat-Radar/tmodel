---
schema: "archdoc/v1"
id: DL-0033
title: "Requirement extraction, AI-security lane: ETSI EN 304 223 and CISA AI-in-OT (#169, deliverable 3)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-03"
updated: "2026-11-03"
record: DL-0033
bears_on: [DEC-001a, R-018]
defers_to: ARCH-0001
---

# DL-0033: Requirement extraction, AI-security lane (#169)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code (claude-opus-5-5) drafted it in @Maimcghee's session, as one agent with no subagents. It produced the two files in `research/0017-requirements-extraction/` named below. Issue: #169, deliverable 3 (parent #168).

## Question asked

#169 asks for one file per record:
- **`etsi-en-304-223`:** "all provisions with a product or technical link". The #159 AI-threat mapping becomes proposed `addresses` Assertions to the NIST AI 100-2 and ATLAS classes, with stub nodes.
- **`cisa-ai-in-ot-principles`:** "principles that name a threat or control; the rest are skipped with a reason".

The student asked the agent to draft both while #197 and #198 are in review.

## Prompt used

The agent followed the prompt in #169 ("Prompt for your coding agent"), with these differences:
- The session was rooted in the `library` checkout, not `tmodel/`. The tmodel worktree `topic/requirements-ai-security` was used for the output, and `CLAUDE.md`, ADR-0012, the schema classes and `mvp-02` were read from `main`.
- The skeleton came from `convert.py` (#197). The agent then wrote the scope, the paraphrases, the kinds and the links, using a build script outside the repository.
- The library files were read at library `main` (`3eacfd0`), where library#32 had merged on 2026-10-25, as #169 asks.

```text
You are extracting requirements for the tmodel threat-modeling knowledge graph.
Read first: tmodel/CLAUDE.md, spec/ADR-0012-requirement-in-core.md, the Requirement / Mitigation /
Assertion / Review classes in spec/schema/tmodel-object-model.linkml.yaml, and the requirements
block in spec/vectors/mvp-02-automotive-ecu.yaml (the worked example). Then follow the output
format in GitHub issue Threat-Radar/tmodel#169 exactly.

For each library record in: etsi-en-304-223, cisa-ai-in-ot-principles
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

| File | In source | Converted | Skipped | Stub nodes | `addresses` | Within-source links |
|---|---|---|---|---|---|---|
| `etsi-en-304-223.yaml` | 73 | 64 | 9 | 42 attack patterns | 108 | 12 |
| `cisa-ai-in-ot-principles.yaml` | 136 | 67 | 69 | 35 attack patterns | 107 | 15 |

Each file's header gives the scope rule and every skip with its reason.
- **Every `text` is the agent's own one-sentence paraphrase** (`text_origin: paraphrase`), although both sources are free, because #169 prefers paraphrases. Designator, locator and normativity are copied from the library record.
- **Every `requirement_kind` is the agent's reading of the provision**, not the converter's default.
- **The `addresses` Assertions are the library's own threat mapping, one per NIST AI 100-2 or ATLAS id.** The mapping is the one library#32 reviewed (its `maps_to`). Confidence is high where the provision names the attack (`kind: stated`), and medium where the mapping is inferred.
- **The within-source links are `refines` or `derived_from` between a sub-provision and its parent**, where the child narrows the parent or depends on its output. Where the child adds a separate concern (ETSI 5.2.1-4.1, 5.2.4-1.2, 5.2.5-4.1 and 5.3.1-2.2), no link is proposed.
- **No Review is written.** The agent writes none (prompt step 4).

## How it was checked

- `linkml-validate` (LinkML 1.12.1, ExampleModelCore), `check-edges.py` and `check.py` (#197) pass on both files.
- **Coverage, checked against the library files:**
  - ETSI: all 35 provisions with a library threat mapping are converted, including the 32 with a NIST AI 100-2 or ATLAS id.
  - CISA: all 34 entries with such an id are converted. The 11 skipped entries with a mapping map only to a framework or to a general or non-adversarial risk.
- **Every stub's ATLAS name** was taken from the ATLAS 2026.09 data the library pins, with the parent technique's name added for sub-techniques. Each stub was compared with 2026.10:
  - four mapped ids are removed: AML.T0024.000, .001 and .002, and AML.T0057;
  - the AML.T0010 family is renamed.
  
  Each affected stub says so (RPT-0009 open question 8).

## Choices the agent made, open to review

- **ETSI scope.** It keeps every provision that constrains the AI system or its lifecycle, and skips only duties that fall on people or management (9). A narrower reading, technical provisions only, would also fit #169's words. It would keep 16 of the 64 and drop the 48 process, documentation and audit provisions.
- **CISA scope.** Besides the 34 mapped entries, 33 are kept because they prescribe a concrete control, such as failsafes, push-based architectures, testing stages or logging. The skip groups are framing, non-normative text, governance and skills, deliberation, pointers, contracts, and accuracy or quality tuning. Borderline calls are R-0022 (sourcing trade-offs, kept because it is mapped) and R-0105 ("use caution", skipped as advisory).
- **CISA normativity overrides.** R-0013 (library: statement) is `informative`. R-0014 ("almost certainly should not", library: prohibition) is `recommended`, not `mandatory`. Each says so in its description.
- **Example items kept.** CISA R-0112 to R-0116 are list items in the predictive-maintenance example. They are kept because each names a control (anomaly detection, monitoring, audit trail, red teaming, egress control), and their names say "(example)".
- **NIST AI 100-2 entries are AttackPattern stubs**, like the ATLAS techniques. NIST's taxonomy ids are attack classes and subclasses rather than techniques, but the schema has no closer class.
- **No `applies_to_family`.** Both sources scope themselves to AI systems in general, and no family value exists for that (DEC-009 is open).

## Human review sample

For each file, 12 proposed links were chosen to cover:
- stated and inferred mappings;
- NIST and ATLAS ids;
- one ATLAS id that 2026.10 removes;
- the within-source links.

The PR listed them, and the agent gave the student each provision's text, the target and the basis. The agent flagged five for a closer look:
- ETSI #3 and CISA #7 point at AML.T0024.000, which ATLAS 2026.10 removes;
- ETSI #9 and CISA #5 link logging to an attack it only detects;
- ETSI #8 is a T0048 match, after RPT-0009 found a spurious one in em-01.

## What a human accepted

- The student asked for both files.
- **Review sample: all 24 links accepted** (12 per file) by @Maimcghee on 2026-11-03, including the five the agent flagged. Each is now `assertion_status: accepted`, with a Review (`review_status: accepted`, reviewer `party:maimcghee`). Each justification gives the basis shown at review.
  - The two AML.T0024.000 links are accepted against ATLAS 2026.09, the version the library pins. A move to 2026.10 would retarget them (RPT-0009 open question 8).
  - The two logging links are accepted with `addresses` read as including detection.
- The other 218 links (ETSI 108 of 120, CISA 110 of 122) stay `proposed`, with no Review.

## What was rejected, and why

- **Corrected by the agent before review: the CISA scope line.** The first draft said every mapped entry was kept "except R-0001". R-0001's mapping has no NIST AI 100-2 or ATLAS id, so it was never an exception, and the line now gives the count instead.
- **Human:** none. No link in the sample was rejected.
