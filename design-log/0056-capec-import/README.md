---
schema: "archdoc/v1"
id: DL-0056
title: "CAPEC import: every CAPEC 3.9 entry read whole, mapped onto the core model, and served to the attack-pattern table (#244, #236)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-14"
updated: "2026-11-14"
record: DL-0056
bears_on: [DEC-001a, DEC-008]
defers_to: ARCH-0001
---

# DL-0056: the CAPEC import

AI-assisted design record (per `CLAUDE.md`). Student: @Clovier, the Data lane owner, working with Claude Code.

## Question asked

- **#236** (@kriishnaa-18's attack-pattern table, split from #58) is blocked on data. It asks for an agreed CAPEC source and importer, engine endpoints for table rows and for one entry's details, an agreed response contract with filtering, sorting and paging, and a representative fixture.
- **#244** asks the engine to read the CAPEC release the library pins, keep every field of every entry, and serve it the way the CWE import (#233, DL-0050) serves weaknesses.

## What was produced

| File | Change |
|---|---|
| `engine/engine/load/capec.py` | new: the reader (`load_catalog`, `cached_catalog`), the entries (`CapecEntry`, `CapecCatalog`), the field and link reports, and `to_objects` |
| `engine/engine/load/cwe.py` | the bounded read takes a size limit and an error class, and the element reader takes a namespace, so the CAPEC reader reuses both; CWE's behaviour is unchanged |
| `engine/engine/core.py`, `engine/engine/api/server.py` | `GET /attack-patterns` (what the import found, or one entry in full) and `GET /attack-patterns/table` (rows for the table view). The table's sort is shared with the weakness table |
| `engine/engine/cli.py` | `tmodel attack-patterns`, and `--id` for one entry, which refuses table options as `GET /attack-patterns` does |
| `engine/tests/test_load_capec.py`, `engine/tests/test_attack_pattern_table.py` | 91 tests, and one more that runs only when MITRE's file is at hand |
| `engine/tests/fixtures/capec/` | the sample catalog and a one-record test library |
| `apps/desktop/src/fixtures/attack-pattern-table.json` and its README | the table feed's answer over the sample, for #236 |
| `CONTRIBUTING.md` §10 | how to point the engine at the catalog |

### Where the catalog comes from

The library's `capec` record pins the release: CAPEC 3.9 (2023-01-24), written to CAPEC XML Schema 3.5, as MITRE's `capec_v3.9.xml` with SHA-256 `70279a2dff0cb0ad79e546adb07828335a704ad5210e047e09e986172fc9e34d`. The engine reads that file from the path in `TMODEL_CAPEC_CATALOG`, refuses a file with any other digest, or one that is not a regular file or is larger than 64 MiB, and never downloads it itself: how the app gets catalogs is DEC-008, still open.

The record has had its digest since library commit `4173143`, which is in `e406827`, the pin #200 moves to. tmodel's pin (`a28a013`) predates it, so until the pin moves, `TMODEL_LIBRARY` has to point at a library checkout that has it. Without a pinned digest or a catalog, the API answers 503 with what to set.

### Kept whole

Every element and attribute of an entry is kept in `CapecEntry.fields`, in the form the CWE reader uses (DL-0050): `@Name` for an attribute, text as written, `#xhtml` for structured text, and a mapping of lists, or an ordered `#items` list where child names interleave. The reader reuses the CWE reader's code for this, so the two catalogs have one shape.

The field report (`GET /attack-patterns`) has one row per entry field: the fields of CAPEC XML Schema 3.5, from `ap_schema_v3.5.xsd`, with how many entries carry each one and where it goes. A field the reader does not know is kept and reported with `known: false`. The links report lists each CWE link that could not be mapped, and each one given twice, and counts the links between attack patterns and the taxonomy mappings, which stay on the entries.

### Mapped onto the core model

As far as the accepted model reaches (ADR-0010, ADR-0011):

| CAPEC field | In the object model |
|---|---|
| `@ID` | `AttackPattern.id` `attack-pattern:capec-N`, the id the CWE import and the example models use, and `AttackPattern.catalog_ref` `CAPEC-N` |
| `@Name` | `AttackPattern.name` |
| `Description` | `AttackPattern.description`, as plain text |
| `Related_Weaknesses` | a `Weakness` `weakness:cwe-N` with only `catalog_ref`, and an Assertion: Weakness `exploited_by` AttackPattern, the predicate the CWE import and mvp-02 use |
| every other field | kept on the CAPEC entry, served by `GET /attack-patterns?id=CAPEC-N` |

Every Assertion is `proposed`, `asserted_by` `party:mitre-capec` (an organization), with `generated_by` naming the release, the file and its digest. CAPEC states these links, and no tmodel reviewer has accepted them (R-018), so they stay proposed. An Assertion's id says CAPEC gave it (`assertion:capec-66-related-weakness-cwe-89`), so it never collides with the CWE import's Assertion for the same pair.

### The table feed

`GET /attack-patterns/table` has the shape of `GET /weaknesses/table` and `GET /library/table`: `catalog`, `query`, `total`, `count`, `rows`, `facets` and `contextual_facets`. A row has the CAPEC id, the tmodel object id, the name, abstraction, status, likelihood of attack, typical severity, description, the CWE ids and ATT&CK techniques as lists, counts of related attack patterns, attack steps, mitigations and examples, and the entry's page on capec.mitre.org. The filters are abstraction, status, likelihood and severity, and an enumeration sorts in CAPEC's own order. Search also finds a CWE id or an ATT&CK technique. Every answer that holds CAPEC content carries MITRE's copyright designation and licence, as the CAPEC Terms of Use require of a copy.

## How it was checked

- **The sample.** 13 attack patterns, 3 categories, 3 views and the 15 references they cite, cut byte for byte from MITRE's 3.9 file and chosen so that every entry field, abstraction and status value, link kind and taxonomy of the release appears. It validates against `ap_schema_v3.5.xsd` with `xmllint --nonet`, with the W3C XHTML schemas matched by digest, as the whole file does.
- **The values.** For every sample attack pattern, the name, abstraction, status, likelihood, severity, description, CWE ids, related attack patterns, ATT&CK techniques and the counts equal what ElementTree reads from the XML directly.
- **Nothing lost.** Per entry, the elements, attributes and words kept equal those in the XML.
- **The whole 3.9 release**, MITRE's file, whose digest matches the record. It has 615 attack patterns (77 Meta, 197 Standard, 341 Detailed), 78 categories, 13 views and 440 references, with 0 unknown fields, and parses in about 0.1 s.
- **The objects.** For the whole release, the import makes 615 attack patterns, 336 weaknesses, 1,212 assertions and 1 party. Those objects and the sample's both validate against `ExampleModelCore` with `linkml-validate` (LinkML 1.12.1), with no issues, and `check-edges.py` finds every reference resolved.
- **Against CWE 4.20**, the release the CWE import reads. Every one of the 450 CAPEC ids that CWE cites is in CAPEC 3.9, so every AttackPattern the CWE import makes gets a name. Every one of the 336 CWE ids that CAPEC cites is a CWE 4.20 weakness, none deprecated. The two catalogs state exactly the same 1,212 weakness and attack pattern pairs.
- **The engine.** 509 passed and 7 skipped on Python 3.11, 3.12 and 3.13, with the CWE import's 88 tests unchanged. `ruff check` and `ruff format --check` are clean. The frontend's typecheck and 373 tests pass, and `render_app.py --check` shows the published app unchanged.

## Found in MITRE's 3.9 data

- CAPEC-545 cites CWE-1258 twice, and CAPEC-644 cites CWE-308 twice. Each pair makes one Assertion, and both are listed by `GET /attack-patterns`.
- The 39 OWASP Attacks taxonomy mappings have a name but no `Entry_ID`. They are kept on the entry.
- CAPEC writes an ATT&CK technique as `1574.010`, without the `T`. The rows give it as `T1574.010`, ATT&CK's own form, and the entry keeps CAPEC's text.
- The schema allows a `ParentOf` link and a view `Audience`, but no 3.9 entry uses either.
- CWE 4.20 cites CAPEC-5, which CAPEC 3.9 marks Obsolete.

## Choices the agent made, open to review

1. **CAPEC 3.9, as the library pins it.** The engine reads only what the library pins by digest.
2. **One AttackPattern per attack pattern, including the 56 deprecated ones and the obsolete one.** The CWE import keeps its deprecated weaknesses too, and the status is on the entry.
3. **An Assertion per source.** CAPEC and CWE state the same 1,212 pairs. Each import makes its own proposed Assertion, attributed to its own program, so the provenance of each edge stays one catalog at one version (DL-0050, adapt 5). A reviewer who accepts one can see the other.
4. **Mitigations, execution flows, prerequisites and the rest stay on the entry.** No slot links a Mitigation to an AttackPattern, as with CWE (#61 question 4).
5. **Categories, views and the links between attack patterns are not objects**, as in the CWE import; the hierarchy is #145's kind of work.
6. **CWE ids and ATT&CK techniques are lists in a row**, not counts as in the weakness table, so the view can link a row to the weakness table and to ATT&CK.
7. **An enumeration sorts in CAPEC's own order**, not alphabetically, as the weakness table does.
8. **Reuse the CWE reader's code** for the bounded read and the element rules, rather than a copy, so a fix there (such as the promised follow-up to #233) reaches both.
9. **Refuse a DOCTYPE or ENTITY declaration anywhere in the file**, not just before the root. MITRE's 3.9 file has none. This is the rule the follow-up to #233 brings to the CWE reader.
10. **No zip.** The library pins MITRE's XML itself, so a zip of it is another file, and the reader says it is not a CAPEC catalog.
11. **A 64 MiB limit.** The 3.9 file is 3.8 MB.
12. **A copy of the sample in tmodel**, with MITRE's notice and licence beside it, because the engine CI does not check out the library.

## What a human accepted

- @Clovier, 2026-11-14: open #244 for the CAPEC import that #236 waits on, and build the importer that night, on top of #233.

The code, the mapping and the choices above are the agent's draft until a human reviews them on the pull request.

## What was rejected, and why

- **Copying the CWE reader's helpers into the CAPEC reader.** Two copies of the bounded read would drift; the CWE reader now takes the limit, the error class and the namespace instead.
- **Reusing the CWE reader's item list to count mitigations and examples.** It returns only structured items, and CAPEC writes most of them as text alone, so CAPEC-66 showed 0 mitigations instead of 3. The reader counts every item.
- **Only one Assertion for a pair both catalogs state.** That would drop one catalog's provenance, or make an import's output depend on the other's.
- **Moving the library pin in this change.** It also moves the site's record pages, so it is a change of its own (#200 makes it).

## Follow-ups

- #236: the attack-pattern table view, from `attack-pattern-table.json` now and the live feed once this merges.
- Move tmodel's library pin past `4173143` (#200 does), so `TMODEL_LIBRARY` is not needed.
- The follow-up to #233 (refuse a DOCTYPE anywhere, `zlib.error` as `CweError`, `_values`' one-name message) now covers the shared read.
- A CVE import for #235, and the store (#65) merging the CWE and CAPEC objects, which share their ids on purpose.
- DEC-008: how the app gets the catalogs.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
