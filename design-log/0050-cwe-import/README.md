---
schema: "archdoc/v1"
id: DL-0050
title: "CWE import: every CWE 4.20 entry read whole, mapped onto the core model, and served to the table views (#144, #61, #58)"
type: process
status: draft
version: "0.1.1"
date: "2026-11-11"
updated: "2026-11-12"
record: DL-0050
bears_on: [DEC-001a, DEC-008]
defers_to: ARCH-0001
---

# DL-0050: the CWE import

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, the Data lane owner, working with Claude Code.

## Question asked

- **#144** (part of #61; PLAN-0002 §5) asks the engine to import each CWE entry once, keyed by CWE-ID, keeping every field. Its definition of done: a `Weakness` for every CWE entry in the extraction, tests on sample entries, and no field dropped silently, so any field the import cannot map is reported.
- **#58** (2026-11-11): should the weakness table wait for #144, and when will its engine feed and response contract exist? The sponsor answered on #58 the same day that the CWE mapping to the knowledge graph comes first.
- **#61**, open since 2026-10-31: two questions shape #144, namely which CWE line to build on and where CWE's other fields go. They have no answer yet. This entry builds on the answers proposed there, the 4.x line and option (c), and says below where it departs from them.

## What was produced

| File | Change |
|---|---|
| `engine/engine/load/cwe.py` | new: the reader (`load_catalog`, `cached_catalog`), the entries (`CweEntry`, `CweCatalog`), the field and link reports, and `to_objects` |
| `engine/engine/core.py`, `engine/engine/api/server.py` | `GET /weaknesses` (what the import found, or one entry in full) and `GET /weaknesses/table` (rows for the table view) |
| `engine/engine/cli.py` | `tmodel weaknesses`, and `--id` for one entry, which refuses table options as `GET /weaknesses` does, so the CLI matches the API (APP-0001 A-060) |
| `engine/tests/test_load_cwe.py`, `engine/tests/test_weakness_table.py` | 88 tests, and one more that runs only when MITRE's file is at hand |
| `engine/tests/fixtures/cwe/` | the sample catalog, the extraction's expected values for it, and a one-record test library |
| `apps/desktop/src/fixtures/weakness-table.json` and its README | the table feed's answer over the sample, for #58 (now #234) |
| `CONTRIBUTING.md` §10 | how to point the engine at the catalog |

### Where the catalog comes from

The library's `cwe` record (Threat-Radar/library#21) pins the release: CWE 4.20 (2026-04-30), written to CWE XML Schema 7.3, as MITRE's `cwec_v4.20.xml.zip` with SHA-256 `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`. The engine reads that file from the path in `TMODEL_CWE_CATALOG`, refuses a file with any other digest, or one that is not a regular file or is larger than 256 MiB, and never downloads it itself: whether the app bundles, caches or fetches the catalog is DEC-008, still open.

tmodel's library pin (`a28a013`) predates the extraction, and its `cwe` record has no digest. Until the pin moves, `TMODEL_LIBRARY` has to point at a library checkout that has it (library `main` at `20399c2` does). Without a pinned digest or a catalog, the API answers 503 with what to set.

### Kept whole

Every element and attribute of an entry is kept in `CweEntry.fields`, in one JSON-ready form: an attribute is `@Name`; a text-only element is its text as written; structured text and example code are `#xhtml`, the inner markup without the `xhtml:` prefix; every other element is a mapping of its attributes and children, with each child name holding a list. Where child names interleave, as a Demonstrative_Example's Body_Text and Example_Code do, the children are an ordered `#items` list instead, so their order survives. The module docstring gives the rules in full.

The field report (`GET /weaknesses`) has one row per entry field: the fields of CWE XML Schema 7.3, from the extraction's `messages.yaml`, with how many entries carry each one and where it goes. A field the reader does not know is kept and reported with `known: false`. The links report lists each CAPEC or CVE link that could not be mapped, and each one given twice.

### Mapped onto the core model

This is option (c) from #61, as far as the accepted model reaches (ADR-0010, ADR-0011):

| CWE field | In the object model |
|---|---|
| `@ID` | `Weakness.id` `weakness:cwe-N`, as the example models write it, and `Weakness.catalog_ref` `CWE-N`, as the extraction's design notes and the models do |
| `@Name` | `Weakness.name` |
| `Description` | `Weakness.description`, as plain text |
| `Related_Attack_Patterns` | an `AttackPattern` `attack-pattern:capec-N` with only `catalog_ref`, and an Assertion: Weakness `exploited_by` AttackPattern, the predicate mvp-02 uses for the CWE to CAPEC mapping |
| `Observed_Examples` with a CVE id | a `Vulnerability` `vulnerability:cve-…` with only `catalog_ref`, and an Assertion: Vulnerability `instance_of` Weakness, with the example's text as its description and its link as its evidence |
| every other field | kept on the CWE entry, served by `GET /weaknesses?id=CWE-N` |

Every Assertion is `proposed`, `asserted_by` `party:mitre-cwe` (an organization), with `generated_by` naming the release, the file and its digest. CWE states these links, and no tmodel reviewer has accepted them (R-018), so they stay proposed. That follows the design notes (adapt 5): the provenance of an imported edge is MITRE CWE at one catalog version, never a person.

### The table feed

`GET /weaknesses/table` has the shape `GET /library/table` has (#141, agreed on #58): `catalog`, `query`, `total`, `count`, `rows`, `facets` and `contextual_facets`. So the library table's paging, facets and search can be reused. A row has the CWE id, the tmodel object id, the name, abstraction, structure, status, mapping usage, likelihood of exploit, description, counts of CAPEC links, observed examples and mitigations, and the entry's page on cwe.mitre.org. The filters are abstraction, structure, status and usage, and an enumeration sorts in CWE's own order. Every answer that holds CWE content carries MITRE's copyright designation and licence, as the CWE Terms of Use require of a copy.

## How it was checked

- **The sample.** The library's 13 example files, copied verbatim from CWE 4.20 for importer tests: 12 entries (9 weaknesses, 2 categories and 1 view) and a file of 3 external references, so the reader finds 15 items. Each file was checked byte for byte against its digest in the library's `expected.yaml` and against MITRE's 4.20 file. The assembled sample validates against `cwe_schema_v7.3.xsd` with `xmllint --nonet`, with the W3C XHTML schemas matched by digest.
- **The extraction's values.** For every sample entry, the values the extraction says an importer must find are found: names, abstraction, structure, status, related weaknesses with view, ordinal and chain, taxonomy mappings, CAPEC ids, cited references, counts, note types, mapping notes and content history.
- **Nothing lost.** Per entry, the elements, attributes and words kept equal those in the XML.
- **The whole 4.20 release**, MITRE's zip, whose digest matches the record. It has 969 weaknesses, 422 categories, 59 views and 1,026 references, with 0 unknown fields, and parses in about 0.6 s. The status and usage counts, the content-history counts per kind, the 1,212 CAPEC links and the 3,134 observed examples all equal the extraction's `catalog-stats.yaml`.
- **The objects.** For the whole release, the import makes 969 weaknesses, 450 attack patterns, 2,154 vulnerabilities, 4,329 assertions and 1 party. Those objects and the sample's both validate against `ExampleModelCore` with `linkml-validate` (LinkML 1.12.1), with no issues. Every reference resolves inside them.
- **CWE 4.21** (2026-10-28, schema 7.4). The library does not pin it, so it was read without a digest. It reads with no code change: 984 weaknesses, 431 categories, 62 views and 1,081 references. The report flags five External_Reference fields that schema 7.4 adds (`Access_Restrictions`, `Alt_URL`, `Alt_URL_Date`, `Media_Type`, `Rationale`), which are kept, not dropped.
- **A bounded read.** A FIFO with no writer, `/dev/zero` and a directory are refused at once. Before the change, the FIFO made the read wait for a writer, and the device would have been read without end. A file over the size limit is refused before it is read, and MITRE's 4.20 zip still reads whole in about 0.6 s.
- **The engine.** After merging main (`b0604a4`): 418 passed and 6 skipped on Python 3.11, 3.12 and 3.13. CI's engine jobs skip two more, the tests that read the library submodule, which those jobs do not check out. `ruff check` and `ruff format --check` are clean, and `tmodel health --in-process` answers ok.

## Found in MITRE's 4.20 data

- 8 observed examples cite a reference instead of a CVE: `[REF-1100]` (CWE-1260), `[REF-1095]` (CWE-1277), `[REF-1374]` (CWE-332, 392, 703, 755 and 1391) and `[REF-1468]` (CWE-1429). They are kept on the entry, with no Vulnerability.
- CWE-837 cites `CVE-2002-216`, which has three digits after the year and so is not a valid CVE id. It is kept, not mapped, and listed by `GET /weaknesses`.
- 8 pairs of a weakness and a CVE are listed twice, for example CVE-2012-0911 under both CWE-502 and CWE-915. Each pair makes one Assertion, and both texts are kept on the entry.
- CWE-79 cites REF-44 twice, for two sections, and both are kept.

## Choices the agent made, open to review

1. **CWE 4.20, not 4.21.** The library pins 4.20 by digest, and the engine reads only what the library pins. The proposal on #61 was the 4.x line (schema 7) rather than 5.0. Moving to 4.21 takes only a new library record.
2. **Option (c) from #61**, as far as the core model goes. A Weakness gets its id, name, description and catalog_ref, and the CAPEC and CVE links become proposed Assertions.
3. **Mitigations stay on the entry.** `Mitigation.mitigates` takes a ThreatInstance, and no slot or agreed predicate links a Mitigation to a Weakness. Mapping CWE's mitigations needs that decision first (#61 question 4).
4. **Categories and views are not objects.** The design notes reject categories as mapping targets, and relationships and membership are #145.
5. **AttackPattern and Vulnerability objects carry only `catalog_ref`.** CWE gives no CAPEC names, and an observed example describes the CVE in the weakness's terms, so its text goes on the Assertion.
6. **The predicates are `exploited_by` and `instance_of`,** the names mvp-02 and ADR-0011 already use.
7. **One field form,** with lists everywhere, `#xhtml` for markup and `#items` for interleaved children, so the GUI and #146's reconciliation meet one shape.
8. **An enumeration sorts in CWE's own order,** not alphabetically.
9. **A copy of the sample in tmodel.** The engine CI does not check out the library, so the tests need their own copy. It is the library's verbatim set, with MITRE's notice and licence beside it.
10. **No route that exports every object.** `to_objects` is there for the store (#65) and the graph. The API serves the report, one entry with its objects, and the table.
11. **One size limit for the file and its XML,** 256 MiB. A zip is far smaller than the XML inside it, so the file's limit refuses nothing the XML's limit would accept.

## What a human accepted

- @Clovier, 2026-11-11: after the sponsor's #58 comment, build #144 on the answers proposed on #61 (the 4.x line, option (c)) without waiting for a reply there, and give #58 the table feed's shape and a fixture first.

- @Clovier, 2026-11-12: make the changes the review of #233 asked for (below).

The code, the mapping and the choices above are the agent's draft until a human reviews them on the pull request.

## What was rejected, and why

- **Building on CWE 4.21**, which the first draft of the #58 reply named. The library pins 4.20, and a release the library does not pin has no digest to check.
- **A Weakness for each category and view.** CWE says a category "should not be mapped to by external sources" (the design notes, reject 3).
- **Mapping mitigations through a new predicate.** That would invent model semantics nobody agreed. Mitigation nodes with no link to their weakness would be orphans in the graph.
- **Fetching the catalog from MITRE inside the engine.** DEC-008 is open, and the engine stays local (ADR-0003).
- **Plain strings for structured text.** A text such as `x < y` would be misread as markup. Writing the tests found this, and structured text became `#xhtml`.
- **Unwrapping one-value fields** (`Description: "…"` instead of a list). That needs each field's cardinality, and lists everywhere keep one shape.
- **Moving the library pin in this change.** It also moves the site's record pages, so it is a change of its own.

## Changes after review (2026-11-12)

@kriishnaa-18 reviewed #233 on 2026-11-12 and asked for two changes before approving. Both are made:

- **Merge main.** #231 added a paragraph about the browser preview where this change adds the weakness table's section to `apps/desktop/src/fixtures/README.md`. Both are kept, the preview's paragraph first, since it is about the library fixture above it.
- **A bounded read.** `load_catalog` read the whole file into memory before checking its digest, and only the XML inside a zip had a size limit. Now the file is opened without waiting, and anything that is not a regular file is refused, as is a file larger than `MAX_FILE_BYTES` (256 MiB, the XML's limit), before any of it is read. The read stops one byte past the limit, so a file that grows after the check is refused too.

The review's two suggestions are taken as well, open to review like the rest: `tmodel weaknesses --id` refuses table options instead of ignoring them, as `GET /weaknesses` already did with a 400; and the sample's description now tells the library's 13 example files apart from the 15 items read from them (12 entries and 3 references).

#58 was closed the same day and split into one issue per table. The weakness table view is #234, so the fixture README, the test that checks the fixture and the code comments now point there.

## Follow-ups

- The sponsor answers #61 questions 3 and 4, or confirms (c) as built. Mitigations wait on question 4.
- Move tmodel's library pin past library#21, so `TMODEL_LIBRARY` is not needed.
- #145: per-view relationships and memberships. #146: the reconciliation report and its CI check, which start from this entry's field and link reports.
- A CAPEC import names the AttackPatterns, and the CVE records' own CWE mappings give the other direction.
- The engine's `/graph` links a model's `weakness:cwe-N` nodes to their catalog entries.
- DEC-008: how the app gets the catalog.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
