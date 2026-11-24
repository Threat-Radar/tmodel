---
schema: "archdoc/v1"
id: DL-0065
title: "Move the CWE pin to 4.21: a new library record that the engine follows"
type: process
status: draft
version: "0.1.2"
date: "2026-11-22"
updated: "2026-11-23"
record: DL-0065
bears_on: [DEC-008, DEC-002]
defers_to: ARCH-0001
---

# DL-0065: Move the CWE pin to 4.21: a new library record that the engine follows

AI-assisted design record (per `CLAUDE.md`), drafted by Claude Code for @Clovier.

## Question asked

@Clovier asked whether the Weaknesses tab shows the current CWE list. It shows CWE 4.20 (April 2026), the release
the library pins. MITRE published a newer list on 2026-10-28, and #61 (question 3) proposes building on 4.21 now and
adding 5.0 later as a new library record. After seeing what 4.21 changes, @Clovier said: "go ahead with the pin".

## What was found

- **Two releases, one list.** CWE 5.0 (schema 8.0, namespace `http://cwe.mitre.org/cwe-8`) and CWE 4.21 (schema 7.4,
  namespace `http://cwe.mitre.org/cwe-7`) carry the same 984 weaknesses, with identical IDs and names. MITRE's
  "latest" download is 5.0; the importer reads schema 7.x only.
- **Changes from 4.20:** 15 new weaknesses (CWE-1461 to CWE-1476, most about session management and credentials),
  9 new categories and 3 new views; 3 weaknesses deprecated (CWE-377, CWE-391 and CWE-613, now with mapping usage
  `Prohibited`); nothing removed.
- **4.21 does not validate against its own schema 7.4.** xmllint, offline, finds 81 errors, all of them content
  that schema 8.0 adds: new taxonomy names (47), five reference fields (19), custom AI and hardware phases (10), the
  `Overlaps` relationship (3) and one impact value (2). The 4.20 file still validates against 7.3. The library
  record `cwe-4-21` gives the details.
- **The importer reads 4.21 without loss** (984 weaknesses, 431 categories, 62 views), but it reported five
  reference fields as unknown, which the Weaknesses tab shows as a warning: `Alt_URL`, `Alt_URL_Date`, `Media_Type`,
  `Access_Restrictions` and `Rationale`. Schema 8.0 declares all five.
- **A library record never changes release.** The library's `CLAUDE.md`: ids are never reused, and "a new version of
  a spec is a new record linked by `supersedes`". The `cwe` record's FX-1 extraction (its schema, fixtures and counts)
  describes the 4.20 file, so editing that record in place would also make its extraction wrong. ADR-0014 says a
  release changes when someone "updates its pin in the library (URL and SHA-256)", without saying how the library
  holds it.

## What was produced

- **Library (Threat-Radar/library#52):** record `cwe-4-21` (`records/other/cwe-4-21/`), with `supersedes: [cwe]`, pinning
  `cwec_v4.21.xml.zip` (SHA-256 `5225e2b4…7e718862`), at the summary bar. Its `summary.md` lists the changes from
  4.20 and the 81 departures from schema 7.4. The `schema-representations` topic lists it beside `cwe`.
- **Engine:**
  - `cwe.served_record(library)` follows `supersedes` forward from `cwe` to the newest release, and refuses a line
    that forks or loops. `core._served_catalog` and `bin/build-engine` use it, so the engine serves 4.21 and the
    app bundles it. The build log names the record, and the smoke test prints the release version.
  - `ENTRY_FIELDS` knows the five reference fields, with a comment that only schema 8.0 declares them.
- **Tests** (`engine/tests/test_load_cwe.py`): the line (one record, two newer releases, a fork, no `cwe`); the five
  fields known, and any other new field still reported; and a tripwire: the pinned library must serve `cwe-4-21`
  with its URL and digest.
- **Docs:** CONTRIBUTING (the record and the `curl` lines, and without the old note to point `TMODEL_LIBRARY` at
  another checkout: the pinned library has had the CWE record since library#21), and the app's third-party notice
  (CWE 4.21).
- **The submodule** moves to the library commit that adds `cwe-4-21`. That also brings library#50
  (`iso-sae-21434-2021` FX-1, #154), merged there since the last pin.

## Review changes (2026-11-23)

@kriishnaa-18 found that the tripwire never ran in CI: `test_the_pinned_library_serves_cwe_4_21` skips without the library submodule, and CI's engine jobs do not check it out. The desktop job does, and it runs `engine/tests/test_packaging.py` against the built app, but that test only checked that the bundled catalog was not empty.

The packaging tests now check the release the built app ships:

- `test_relocated_engine_reads_bundled_cwe_release_without_checkout`: the bundled catalog is exactly CWE 4.21, `cwec_v4.21.xml.zip`, SHA-256 `5225e2b4…7e718862`.
- `test_relocated_engine_serves_bundled_library_without_checkout`: the bundled library's `cwe-4-21` record pins that file, supersedes `cwe`, and is superseded by nothing, so it is the record the engine serves.

Checked locally with an engine built from this branch by `bin/build-engine` (686 library records, CWE 4.21 with 984 entries): all 7 packaging tests pass. Against the earlier CWE 4.20 test build, both changed tests fail, as they should for any other release.

@paria03 then found that the site's bibliography still described the old pin: `docs/publishing/bibliography.yaml` listed 685 records without `cwe-4-21`, and no record page had been copied for it. `render_bibliography.py --sync` added `cwe-4-21` (type `dataset`, topic `schema-representations`, from its record). The manifest's topic for `iso-sae-21434-2021` moves from `threat-modeling` to `sdl`, because library#50 gave that record `topic: sdl` and the manifest must follow a record's own topic (`docs/publishing/SKILL.md`). Rebuilding the site with `bin/publish-site`'s steps changed only the bibliography pages (now 686 sources) and two record pages: the new `cwe-4-21` page and library#50's `iso-sae-21434-2021` page. A second run changes nothing, and the identity and link checks pass. library#52 itself merged on 2026-11-23 as a merge commit, so the pinned commit is in library main's history.

## Choices

- **A new record, not an edit,** per the library's rule. `cwe` stays the 4.20 record, with its extraction.
- **The engine follows the line instead of naming a record.** A constant such as `LIBRARY_RECORD = "cwe-4-21"`
  would make every test library rename its record, and ADR-0014 puts the pin in the library. The tripwire keeps the
  choice visible in tmodel: a library bump that brings a newer CWE record fails the tests until the same pull
  request updates them.
- **4.21, not 5.0:** the same list, in the schema the importer reads, as #61 proposes. 5.0 needs a schema 8.0
  reader first.
- **Teach the five fields** instead of showing a warning about a release chosen on purpose. A field outside the
  list is still reported.

## What a human accepted

@Clovier asked for the move ("go ahead with the pin"). The choices above are Claude Code's and are not reviewed
yet; the pull requests are where they get accepted or rejected.

## Options not taken, and why

- **Edit `cwe` in place:** breaks the library's id rule and leaves the 4.20 extraction describing the wrong file.
- **Keep 4.20 under `cwe/versions/`:** the library folds old versions of drafts that way, but `cwe/distilled/` would
  then describe a file the record no longer pins.
- **Name the record in the engine:** see Choices.
- **Move to 5.0:** needs a schema 8.0 reader (Categories become Groupings, a new namespace, new fields).
- **Stay on 4.20:** the app would ship a list MITRE has replaced, without the 15 new weaknesses and with 3 retired
  ones looking current.

## Next steps

1. Merge Threat-Radar/library#52, then point this branch's submodule at the merged commit if the merge changes it.
2. This branch builds on #260: merge #261 (ADR-0014), then #260, then this.
3. #249's CI check pins MITRE's 4.20 file and its report. It keeps checking 4.20, which the library still holds as
   `cwe`, until it moves to 4.21.
4. CWE 5.0 later, as a new library record, once the importer reads schema 8.0 (#61).
5. The `owasp-asvs-5` record links 8 requirements to CWE-613 as inferred legacy mappings. They now point at a
   retired entry; remapping them is that record's call.
