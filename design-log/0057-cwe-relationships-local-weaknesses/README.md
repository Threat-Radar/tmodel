---
schema: "archdoc/v1"
id: DL-0057
title: "CWE relationships kept in each view, and local tr-weak weaknesses served beside CWE's (#145, #61)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-15"
updated: "2026-11-15"
record: DL-0057
bears_on: [DEC-001a, DEC-008]
defers_to: ARCH-0001
---

# DL-0057: CWE relationships per view, and local weaknesses

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, the Data lane owner, working with Claude Code.

## Question asked

- **#145** (part of #61; PLAN-0002 §5) asks for three things: keep CWE's relationships (ChildOf, MemberOf, PeerOf, CanPrecede and the rest) each tagged with its view; take a list of views rather than exactly three; and load the project's own weakness types, with `tr-weak-*` ids and `source: local`, beside CWE's. Its test plan: an entry that sits in two views gets an edge tagged with each; the importer runs with one, three and four views; a sample `tr-weak-*` weakness loads and links like a CWE entry.
- DL-0050, the CWE import, left relationships and membership to this issue (its choice 4).

## What was produced

| File | Change |
|---|---|
| `engine/engine/load/cwe.py` | `Relationship`; each entry's relationships read as it loads (`CweEntry.relationships`); `CweCatalog.relationships()` for any list of views, one entry, with or without inverses; `relationship_report()`; the shared `with_inverses`, `view_numbers` and `select`; `objects_for`, which `to_objects` now calls; each entry gives its `source` and `object_id` |
| `engine/engine/load/local_weaknesses.py` | new: the reader of local weakness types (`load_local`, `cached_local`), `LocalWeakness`, `LocalCatalog` and `to_objects` |
| `engine/engine/core.py`, `engine/engine/api/server.py` | `GET /weaknesses/relationships`; `GET /weaknesses?id=` takes a `tr-weak` id and adds `local` and `derived_relationships`; `GET /weaknesses/table` lists the local weaknesses after CWE's |
| `engine/engine/cli.py` | `tmodel weaknesses --relationships`, with `--id`, `--view` and `--stated-only`, and `--id tr-weak-0001` |
| `engine/tests/test_cwe_relationships.py`, `engine/tests/test_local_weaknesses.py` | 88 tests, one of which runs only when MITRE's file is at hand |
| `engine/tests/fixtures/local-weaknesses/tr-weak-sample.yaml` | two made-up local weaknesses that link to entries of the CWE sample |
| `CONTRIBUTING.md` §10 | the relationships command and `TMODEL_LOCAL_WEAKNESSES` |

### Relationships, each in its view

Each relationship an entry writes becomes one `Relationship`: its source, nature, target, view (`View_ID`), `Ordinal` and `Chain_ID`. A weakness's `Related_Weakness` keeps its `Nature`. A category's or view's `Has_Member` and `Member_Of` become the natures `HasMember` and `MemberOf`, so one list holds both kinds. Nothing is merged across views: CWE-79 is a child of CWE-74 in view 1000 and again in view 1003, and both relationships are kept.

`relationships()` takes any number of views, written `CWE-1000`, `1000` or as one text `CWE-1000,699`, or none for every view. A view must be a view of the release or one some relationship is in; any other is refused, so a typo cannot return an empty list. PLAN-0002 §5 named three views. Following the answer proposed on #61 (question 1), the whole catalog is read once and a query picks the views, so 699, 1000 and 1194 are three of the 41 views that 4.20's relationships use.

The schema declares inverse pairs (RelatedNatureEnumeration, L973): ChildOf and ParentOf, CanPrecede and CanFollow, Requires and RequiredBy, and, for membership, `Has_Member` and `Member_Of`. CWE 4.20 writes only one side of each. The other side is derived and marked `derived`, with no ordinal or chain, so an entry's relationships include the inverses of those that name it: CWE-74 shows ParentOf CWE-79 in both views. CanAlsoBe "is not necessarily reciprocal" (L973), and PeerOf and StartsWith name no inverse, so none is derived for them.

`relationship_report()` counts the relationships by nature and by view, and the inverses derived. It lists, each in full, a nature the schema does not declare, a target that is not an entry read, an `Ordinal` or a `Chain_ID` on another nature than the schema's text names (L540), and an entry with two Primary relationships of one nature in one view (the extraction's design notes, open questions 2 and 5). It counts by view the relationships in a view that is not a view read. None of these is refused, because MITRE's own catalog has some of them.

Relationships are not objects. The accepted core has no Weakness-to-Weakness edge (DL-0013), and the extraction's design notes give ChildOf/ParentOf and CanPrecede/CanFollow the verdict "not in the accepted core (DEC-001a, ADR-0010); needs a follow-up ADR". Categories and views are not objects either (DL-0050). So the engine serves relationships beside the objects, and `to_objects` makes the same objects it made before.

### Local weaknesses

The project's own weakness types are read from one YAML file, the one `TMODEL_LOCAL_WEAKNESSES` names. The file names itself and its maintainer, then lists weaknesses. A weakness has an id `tr-weak-NNNN`, a name, a description and a status, and optionally an abstraction, a structure, alternate terms, relationships, CAPEC links, observed examples and free-form extensions (PLAN-0002 §5). Status, abstraction and structure take CWE's own values, and relationships take CWE's natures (or MemberOf), each with a CWE view. The docstring of `local_weaknesses.py` gives the format in full. The reader is strict, since the file is written by hand: an unknown key, a key given twice and a YAML alias are refused, as are a relationship that names a `tr-weak` id the file does not have and one that names its own entry.

A local weakness is served as a CWE weakness is:

- in `GET /weaknesses/table`, after CWE's in id order, with its `tr-weak` id and no usage, likelihood, mitigations or url;
- in `GET /weaknesses?id=tr-weak-0001`, in full, with `source: local`;
- as objects made the way CWE's are: a Weakness `weakness:tr-weak-NNNN` with `catalog_ref` `tr-weak-NNNN` (the id form of PLAN-0002 §5, PLAN-0004 Q-07 and DL-0026), and proposed Assertions for its CAPEC and CVE links, attributed to the file's maintainer;
- in the relationships, beside CWE's, with the same inverses. A local weakness that is a child of CWE-710 makes CWE-710 show ParentOf it.

## How it was checked

- **The sample.** Its 20 relationships (11 between weaknesses and 9 memberships) were read a second time from the XML with ElementTree alone, with no engine code, and equal what the reader keeps, in file order. CWE-79 has ChildOf CWE-74 tagged with view 1000 and with view 1003. One, three and four views (1000; 1000, 1003, 709; and those with 699) give 17, 20 and 36 relationships, each set exactly the relationships of those views. The 18 derived inverses are exactly the declared inverses of the written ones.
- **The whole 4.20 release**, MITRE's zip, whose digest matches the record. Its relationships, read a second time from the XML, equal the reader's: 6,626 in all, of which 1,602 are between weaknesses (ChildOf 1,318, CanPrecede 143, PeerOf 98, CanAlsoBe 27, Requires 13, StartsWith 3), 4,260 are memberships of categories and 764 of views. These are the counts on #61. 6,498 inverses are derived. Every target is an entry of the release and every view is one of its views. 27 Primary ordinals sit on PeerOf or CanPrecede and 3 chain ids on StartsWith, the design notes' figures, and no entry has two Primaries of one nature in one view. The objects are those DL-0050 counts (969 weaknesses, 450 attack patterns, 2,154 vulnerabilities and 4,329 assertions), and the release still parses in about 0.65 s.
- **CWE 4.21** (2026-10-28, schema 7.4). The library does not pin it, so it was read without a digest. Its 6,785 relationships include 3 with the nature `Overlaps`, which schema 7.3 does not declare. They are kept with no inverse and listed in the report.
- **Local weaknesses.** The sample loads, and its weaknesses come out in the table, by id, as objects and in the relationships, as above. 26 kinds of bad entry are refused, each with where it is, and so are a YAML alias, a key given twice, text that is not UTF-8, a file over the size limit, a directory, a missing file and a FIFO.
- **The engine.** 507 passed and 5 skipped on Python 3.11, 3.12 and 3.13, with MITRE's file at hand. `ruff check` and `ruff format --check` are clean. The GUI's fixture for the weakness table is unchanged.

## Choices the agent made, open to review

1. **Relationships are not objects,** for the reasons above. If an ADR adds a specialization or ordering edge, each `Relationship` maps onto it.
2. **Membership is a nature,** `HasMember` and `MemberOf`, spelled as the natures are, although CWE writes it as elements.
3. **Inverses only where the schema declares a pair.**
4. **An entry's relationships are those whose source it is,** the written ones and the inverses. A PeerOf, CanAlsoBe or StartsWith that names an entry is found from the entry that writes it.
5. **A view nobody knows is refused,** not answered with an empty list.
6. **Departures from L540 are reported, not refused,** as the design notes say.
7. **One YAML file, named by `TMODEL_LOCAL_WEAKNESSES`, and no real one shipped.** No local weakness type is agreed yet, and DEC-008 holds the local namespace, including whether RPT-0014's `LW-*` candidates become `tr-weak` entries.
8. **CWE's own status, abstraction and structure values,** so a local weakness filters and sorts as a CWE one does. DL-0026 proposed `status: candidate`, which is not one of CWE's values.
9. **A local relationship names a CWE view.** The design notes' adapt 4, a fit-graded mapping to the nearest CWE entry (Exact, CWE More Abstract and the rest), is another way to link a local weakness, and is not added here.
10. **A strict reader,** as above.
11. **The table's row keeps its shape,** which is agreed on #234: a local row is told apart by its id, and a `source` column is #234's to add.
12. **Local Assertions are attributed to the file's maintainer** and stay proposed (R-018).
13. **`GET /weaknesses` keeps its shape.** The relationship report is in `GET /weaknesses/relationships`, beside the relationships.

## What a human accepted

- @Clovier, 2026-11-15: start #145, as local work, nothing committed until reviewed.

The code, the format and the choices above are the agent's draft until a human reviews them on the pull request.

## What was rejected, and why

- **Assertions with predicates named after CWE's natures.** The core has no such edge, and adding one is an architecture decision (DL-0013, the design notes).
- **Reading only three views.** That drops the 223 relationships in other views and the 64 deprecated entries (#61, question 1).
- **One hierarchy merged across views.** PLAN-0002 §5 calls it lossy.
- **Deriving PeerOf and CanAlsoBe as symmetric.** The schema declares no inverse for PeerOf, and says CanAlsoBe is not necessarily reciprocal.
- **Refusing an Ordinal or a Chain_ID on another nature.** That would refuse MITRE's own catalog.
- **A `source` column in the table now.** The row's shape is agreed on #234.

## Follow-ups

- #146: the reconciliation report and its CI check can count relationships from `stated_relationships` and `relationship_report()`.
- An ADR for a Weakness-to-Weakness edge, if the graph is to hold relationships as objects.
- Where the team's local file lives, and what becomes of RPT-0014's `LW-*` candidates (DEC-008).
- #234: whether the weakness table shows a source column and the relationships.
- Once the CAPEC import (#244) merges, the attack patterns that local weaknesses link to can be named the way CWE's are.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
