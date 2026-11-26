---
schema: "archdoc/v1"
id: DL-0068
title: "SBOM import: a starter model from Syft's CycloneDX SBOM of a container image and Grype's scan of it (#257)"
type: process
status: draft
version: "0.2.0"
date: "2026-11-25"
updated: "2026-11-25"
record: DL-0068
bears_on: [DEC-001a, DEC-002, DEC-009, R-018]
defers_to: ARCH-0001
---

# DL-0068: the SBOM import

DL-0063 to DL-0065 are reserved by open pull requests (#260, #261, #262), and DL-0066 and DL-0067
are on `main`, so this entry is DL-0068.

## Question asked

Issue #257: every model is a YAML file written by hand or drafted by AI, so a real product's parts
and known vulnerabilities have to be typed in. Read the two files radar's tools write (ADR-0001,
ARCH-0001 R-002), Syft's CycloneDX SBOM and Grype's scan of it, and write a starter model with the
product, its parts and their known vulnerabilities, using RPT-0004 Table 6
(`research/0004-product-composition/mapping.md`) and its candidate rules. #257 left four questions
open, for #15 and #17: the import route, the instance key, where an SBOM's `dependsOn` goes, and the
match predicate's name and `confidence` scale.

## What was produced

- `engine/engine/import_sbom.py`: the import, and the command `tmodel import-sbom SBOM [--scan SCAN]
  -o MODEL [--report FILE] [--force]` in `engine/engine/cli.py`. It runs in-process only; the API
  has no route to it.
- `engine/tests/test_import_sbom.py` and the fixture in `engine/tests/fixtures/sbom-import/`.
- This entry.

### The mapping, as built

Each line is one of Table 6's candidate rules or one of #257's acceptance criteria.

- **Product:** one, keyed by the image's versionless purl (R-ID-2), such as
  `pkg:oci/alpine?repository_url=index.docker.io/library/alpine`. A short image name resolves the
  way Docker resolves it (`alpine` is `index.docker.io/library/alpine`). Its id is made from the
  whole repository, registry and path (`product:index-docker-io-library-alpine`), so the same path
  in another registry gets another id. The id is a readable slug, so two repository URLs that
  differ only in punctuation (`ghcr.io/org/app`, `ghcr.io/org-app`) would still share one; the
  purl in `identifiers` stays the key.
- **ProductInstance:** the scanned build, keyed by the platform manifest digest Syft records in
  `metadata.component.version` (R-ID-1), with the versioned purl beside it; its id is made from the
  whole digest. `build_composed_of` lists every Component (ADR-0011 A4). The SBOM never fills the
  design-level `composed_of` (R-EDGE-2).
- **Component:** one per SBOM entry other than a file (R-ID-4), keyed by its purl, qualifiers and
  subpath included, normalized by the rules the purl specification gives every type (R-ID-3), with
  `version`, `component_kind` from CycloneDX's `type` (A3), and every purl and CPE the entry
  carries in `identifiers`: the purl as Syft wrote it, its `cpe`, and the `syft:cpe23` candidates.
- **Supplier and manufacturer:** `supplied_by` and `manufactured_by` only from a `supplier` or
  `manufacturer` field. A publisher or package maintainer is not a supplier (Table 6c).
- **Dependencies:** each `dependsOn` as `uses_component`, from the dependent to the dependency
  (R-EDGE-1).
- **Vulnerability:** one per CVE a match names, its own id or one in `relatedVulnerabilities`. A match
  that names no CVE keeps the id Grype reports (GHSA, ALAS, GO and so on), unless the rest of the
  scan pairs its ids with exactly one CVE. Another id goes in `alias_ids` only when the whole scan
  pairs it with exactly one CVE (or, with no CVE, one Vulnerability); an advisory paired with
  several, in one match or across matches, is listed in the import report, not aliased. Ids that
  appear only inside a URL are never read. This is the rule @Clovier chose on 2026-11-24, now in
  #257's acceptance criteria.
- **The package match:** one proposed `propagates_to` Assertion for each match and each
  Vulnerability it names, from the Vulnerability to the Component, joined to the SBOM by purl, not
  by `bom-ref` (R-MATCH-1, R-MATCH-2): the same normalized purl, and the same name and version. A
  match on a part that is not a Component of the SBOM, or whose package the SBOM names differently,
  is left out whole and listed in the report.
- **The CVE-to-CWE link:** one proposed `instance_of` Assertion per (CVE, CWE, source), with
  `asserted_by` the Party that assigned the CWE (R-CWE-1). Placeholders such as `NVD-CWE-Other` are
  left out and counted.
- **Provenance:** every Assertion is `proposed`, with no Review (R-018). `asserted_at` is the scan's
  time in UTC, `generated_by` names Grype's version and its database's schema and build time
  (R-PROV-2), and `evidence` holds the input files' SHA-256 (R-PROV-1): the scan's, and for a
  package match the SBOM's too. `asserted_by` is Grype, a `software_agent` Party, except on a CWE
  link.
- **Nothing else:** no assets, trust boundaries, data flows, threats, attack paths or mitigations
  (Table 6f). `Vulnerability.affects` is not set: deriving a Product's `affects` from package
  matches is RPT-0004's proposal (R-MATCH-1), not a rule yet.

The import report gives each input's name, size and SHA-256, the scan's own account of its image
beside the SBOM's, what was written, what was left out with counts, what the inputs repeat that was
written once, and then every field of both files by its path (`components[].publisher`) with where
it went. A field left out whole is counted with the values it holds. A field the import does not
know, at any depth, is listed as "not read by this import", so a field a newer Syft or Grype adds
cannot disappear unnoticed.

### Provisional answers to #257's four open questions

These are the agent's provisional choices, which @Clovier accepted for this change (below). None of
them decides a `DEC-*`; the sponsor can change any of them.

1. **The import route.** ADR-0007 says interchange additions arrive "as MAP-NNNN + a vector". The
   import writes the vector half, a model file. The field-by-field mapping stays in RPT-0004 Table 6
   and in this entry, and a `MAP-NNNN` for radar's data contract can follow if the sponsor asks
   for one.
2. **The instance key.** R-ID-1, the platform manifest digest, stored as `sha256:<hex>` in
   `identifiers`. So the first version reads SBOMs of container images only, and refuses any other
   SBOM with a message saying why: a folder or a file has no digest to key its build by. An image
   named by a version tag gives Syft no digest either (pilot.md: Syft writes the digest only for
   `latest` or a digest reference), and the message says to name the image by digest. An image
   named by its index digest gets that digest, which every platform of the release shares, and the
   CycloneDX file does not say which kind it is (RPT-0004 Table 6, finding 9); so a scan must also
   name this SBOM's root `bom-ref` as its image id, as Grype does for the SBOM it read (Review
   changes, item 6). Whether two platforms' SBOMs always differ in that `bom-ref` is not checked
   here.
3. **Where `dependsOn` goes.** `uses_component`, option (b) of R-EDGE-3: the edge all seven example
   models with a dependency use (none uses `depends_on`), and the one the schema defines as the edge
   "along which vuln/finding propagation is sound". The engine does not propagate findings itself today; the
   models record propagation by hand as `propagates_to`. The choice keeps imported models meaning
   what the hand-written ones mean.
4. **The match predicate and the confidence scale.** `propagates_to`, which the engine draws like any
   predicate, which the app's model report lists under each vulnerability, and which pv-03 already
   writes for the same kind of link ("CVE-2015-9235 is in the jsonwebtoken 0.4.0 component").
   `confidence` comes from Grype's match type, in R-MATCH-1's order: `high` for an exact direct
   match, `medium` for an exact indirect one, `low` for a CPE match, which Anchore says needs
   verification. The words are the ones the example models already use, because the scale is not
   fixed.

### Other choices the agent made, open to review

- **CWE links are Assertions only.** `Vulnerability.instance_of` is not set as a slot, as 6 of the 7
  models with a CWE link do it (pv-01 also sets the slot), so an unreviewed link never looks
  authored.
- **The scan's time is `asserted_at`,** not the time of the import, so the same two files always give
  the same model. Two runs give the same bytes; a test checks it.
- **Entries with the same normalized purl are one Component,** as when an image holds one package
  twice, and the report lists them. Entries whose purls differ in a qualifier (zlib for `aarch64`
  and for `x86_64`) are two Components. Entries that share a purl but give different names, types
  or versions are refused; where they give different descriptions, suppliers or manufacturers,
  that field is left out and listed. (Changed after review, item 1 below: until then, purls that
  differed only in qualifiers were one Component.)
- **Only the purl rules every type shares are applied.** Which names ignore case differs by type
  and changed between purl-spec versions (DL-0015, Phase 2), so two purls that differ only in such a
  case stay two Components, and a match on one is listed, never joined to the other.
- **An entry with no purl,** such as the operating system, is keyed by its type, name and version.
- **Weaknesses are named by their CWE id.** The import does not read the CWE catalog.
- **A CWE source is a Party named as the scan's database names it,** which for CISA's ADP is its
  organization UUID.
- **Descriptions are put on one line:** line breaks and runs of spaces become one space. The words
  are unchanged.
- **Refusals, all before anything is written:** CycloneDX other than 1.7, an SBOM not made by Syft
  (the mapping was checked on Syft's output, RPT-0004 pilot.md), a scan that is not Grype's JSON or
  does not record its database's build time, a scan of a different image digest than the SBOM's, a
  repeated `bom-ref`, a component type outside CycloneDX 1.7's, a file over 64 MiB, a file that is
  not a regular file, and text that is not JSON. Since the review (items 1, 6, 7 and 8 below): a
  key repeated in one JSON object; NaN or Infinity, a number too long to read, nesting deeper than
  64 levels, or text that is not valid Unicode; any field the import reads that has the wrong type,
  named by its path; entries that share a purl but not a name, type or version; a scan whose source
  is not an image, names another repository, or was made from another SBOM of the same digest; an
  SBOM whose name and version give two digests; a Grype version that is not a release, a database
  Grype marks invalid, and a database dated after the scan.
- **Outputs:** the model and the report are written to temporary files beside their paths and moved
  into place only when both are written, so a failed import leaves neither, and puts back any file
  `--force` was replacing. An existing model or report, or a dangling link at its path, is never
  replaced without `--force`, because people edit starter models. An input is never written over,
  whether by its own name, a link to it, a second name for the same file, or the same name in
  another case. The model's text is read back before it is written and must give the model it was
  made from. Input text in the model's header and the report is escaped, so a line break cannot end
  a comment. The header names the output only by its relative path, or by its name when the path is
  absolute, so no home folder lands in a committed file.
- **Grype's distro is reported, not checked.** The report says whether the distribution Grype
  detected matches the SBOM's operating system, and flags a difference; it is not a refusal,
  because the two tools are not known to spell every distribution's name the same way.

## The fixture

The image RPT-0004's pilot scanned: `alpine:3.24.2` for linux/arm64/v8, platform manifest digest
`sha256:260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d` (the tag's index digest is
`sha256:294b683cb724…`). `alpine:latest`, which the pilot named, has since moved to an image pushed
on 2026-11-08, so the image was fetched by digest on 2026-11-25.

- **The SBOM** (`alpine-3.24.2.cdx.json`, SHA-256 `7b655bdb7c1a…`) is Syft 1.52.0's CycloneDX 1.7
  output, unchanged: 95 entries (16 library, 1 operating-system, 78 file), as pilot.md records, and
  12 dependency entries with 24 edges, as Table 6 records.
- **The scan** (`alpine-3.24.2.grype.json`, SHA-256 `f01fe22d6a2c…`) is Grype 0.119.0's output with
  the database built 2026-10-08T06:33:47Z: 30 matches for 15 CVEs, 1 from Alpine's own feed and 29
  from NVD's CPE data, exactly the pilot's numbers. Three values were changed before it was
  committed, because they were local paths and one named a home folder:
  `descriptor.configuration.file` is now the file's own name, and
  `descriptor.configuration.db.cache-dir` and `descriptor.db.status.path` start with `~`. The import
  reads none of them, and the rest of the file is Grype's output byte for byte.

The older database was chosen so the tests' numbers can be checked against RPT-0004. The same SBOM
against the database built 2026-11-25T06:22:21Z gives 57 matches for 29 CVEs: 14 CVEs the older
database did not match, and none dropped. The same image gives a different answer on a different
day, which is why every Assertion records the database's build time (R-PROV-2).

## How it was checked

- `engine/tests/test_import_sbom.py`: the pilot's numbers on the fixture; the keys and identifiers;
  provenance on every Assertion; confidence by match type; the vulnerability-id rule case by case
  (an advisory naming one CVE, none, or several; matches sharing a CVE; an id only inside a URL;
  placeholder CWEs; a match on a part the SBOM lacks); suppliers; dependencies that are not between
  Components; entries sharing a key; every refusal, each checked to write nothing; the command line;
  and that the same files give the same bytes. Since the review, also the regression tests listed
  under each item below: 135 tests in all, counting each parametrized case.
- **The fixture's numbers are unchanged by the review:** 17 Components, 24 dependency edges, 15
  Vulnerabilities, 9 Weaknesses, 4 Parties and 45 Assertions (30 package matches, 15 CWE links).
  Every package has its own purl and every match its own (CVE, Component) pair, so keeping the
  qualifiers and one Assertion per match (Review changes, items 1 and 4) change no count. Only two
  ids changed (item 6): `product:alpine` is now `product:index-docker-io-library-alpine`, and
  `product-instance:alpine-260479a1cfaf` is now
  `product-instance:sha256-260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d`.
- The engine lists the imported model and opens it (`core.list_models`, `core.model_graph`): 30
  `propagates_to`, 15 `instance_of`, 24 `uses_component` and 17 `build_composed_of` edges. The
  attack-graph checks pass too; the model has no paths yet.
- `linkml-validate` (LinkML 1.12.1, the version `spec/schema/requirements.txt` pins) accepts the
  imported model as `ExampleModelProposed`, and `design-log/0024-schema-proposal-g13/check-refs.py`
  and `design-log/0021-mvp-core-attack-path-vectors/check-edges.py` resolve its 177 references
  among 92 objects. The test that runs the validator is skipped where LinkML is not installed, as in
  the engine's CI job.
- The import checks its own output before writing it: every id the model references must be an
  object in it. That check caught one bug while this was built: the Parties that assigned CWEs were
  made after the Party list, so the first run refused to write a model with a dangling `asserted_by`.

## Review changes (2026-11-25)

@kriishnaa-18 reviewed c39f2a4 and asked for changes, with eight findings. Each item says what was
wrong, what changed (in `engine/engine/import_sbom.py` unless it says otherwise), and the regression
tests in `engine/tests/test_import_sbom.py`. Every one of those tests was run on the unchanged code
first, and failed there, as each item says.

1. **Component identity and matching.** `_purl_key` dropped every qualifier, so two builds of one
   package (zlib for `aarch64` and for `x86_64`) became one Component, a match on one build joined
   the other, and entries that disagreed on their version were merged without a word. Now
   `_parse_purl` reads a purl by the purl specification's parsing steps and `_Purl.key` writes it
   one way, qualifiers and subpath kept: the type and qualifier keys lowercased, qualifiers sorted,
   empty ones dropped, every part percent-decoded and encoded one way, and `pkg://` read as `pkg:`.
   `_Builder._component` refuses entries that share a purl but give different names, types or
   versions, and an entry whose version differs from its own purl's is listed (an RPM's `epoch`
   qualifier is allowed for). `_Builder._join` joins a match only to the Component with the same
   normalized purl, name and version; any other match is left out and listed, with the SBOM's purls
   for the package when only the qualifiers differ. This changes a documented choice: purls that
   differ only in qualifiers were one Component, and are now two. Tests:
   `test_entries_whose_purls_differ_in_a_qualifier_are_two_components`,
   `test_a_match_joins_only_the_component_with_its_purl`,
   `test_a_match_on_a_build_the_sbom_lacks_is_left_out`, `test_equivalent_spellings_of_a_purl_join`,
   `test_entries_sharing_a_purl_but_not_a_version_are_refused`,
   `test_a_version_that_differs_from_its_purls_is_reported`,
   `test_a_match_whose_package_disagrees_with_the_sbom_is_left_out`, and
   `test_a_components_key_is_its_normalized_purl`, which replaces
   `test_a_components_key_is_its_purl_without_qualifiers`
   (`test_entries_with_the_same_purl_are_one_component` replaces
   `test_entries_with_the_same_key_are_one_component`). On c39f2a4 they failed: 17 Components where
   18 were expected, the `x86_64` match landed on the `aarch64` zlib, the respelled purl joined
   nothing, conflicting versions raised no error, and the report had no line for either
   disagreement.
2. **What the import writes over.** `_check_outputs` compared paths as strings, so `model.yaml` and
   `MODEL.yaml`, or an input under another case or a second name (a hard link), counted as different
   files; it used `exists()`, which is false for a dangling link, so a link at the output was
   replaced without `--force`; and `run` wrote the model before the report, so a report that could
   not be written left a model behind. Now `_same_place` compares by `os.path.samefile` when both
   paths exist and by case-folded real path otherwise; `_check_outputs` uses `os.path.lexists` and
   refuses a folder; and `_publish` writes both files to temporary files beside their paths and
   moves them into place only when both are written. A file `--force` replaces keeps a second name
   (`_keep`) until both moves are done, so a failed move puts it back. Tests:
   `test_a_report_named_like_the_model_in_another_case_is_refused`,
   `test_an_input_named_in_another_case_is_never_written_over`,
   `test_a_second_name_for_an_input_is_never_written_over`,
   `test_a_dangling_link_is_an_existing_output` (at the model and at the report),
   `test_a_report_that_cannot_be_written_leaves_no_model`, `test_a_failed_move_leaves_neither_file`
   and `test_a_failed_forced_import_keeps_what_it_would_replace`. On c39f2a4 they failed: none of
   the five paths was refused, the model was left beside an unwritable report folder, and a failed
   report move left the new model where the edited one had been.
3. **The model's YAML.** The header wrote input text (the SBOM's serial, Syft's version, file names)
   into `#` comments as it came, so a line break ended a comment and the rest became model data,
   and a control character made the file unreadable, while the import exited 0. A name holding NEL
   (U+0085) was written single-quoted and read back as a different name. Now `_header` and the
   report escape every character that does not print (`_one_line`); `_represent_text` writes such
   text double-quoted, where YAML escapes it; and `_read_back` loads the finished text with
   `yaml.safe_load` and writes nothing unless it gives the model it was made from. Tests:
   `test_input_text_cannot_escape_the_models_header` (a newline, a carriage return, NEL, U+2028,
   ESC and NUL), `test_a_name_with_a_next_line_character_reads_back_exactly` and
   `test_a_model_that_does_not_read_back_is_not_written`. On c39f2a4 they failed: the header held
   an uncommented `injected: true` line, or PyYAML refused the file over the ESC or NUL; the name
   read back changed; and a model that was not YAML was written without an error.
4. **Advisories and one Assertion per match.** An advisory paired with one CVE in one match and
   another CVE in another became an alias of both, and matches were merged by (Vulnerability,
   Component), so an exact match from Alpine's feed and a GHSA's CPE match on the same zlib became
   one Assertion with mixed details and the higher confidence. Now `_Builder._matches` pairs every
   other id with the CVEs it appears beside across the whole scan; `_Builder._aliases` writes an
   alias only for an id the whole scan pairs with exactly one Vulnerability, and lists the rest; and
   `_refs` gives a match naming no CVE the one CVE its ids are paired with, or else its own id.
   `_Builder._match_assertions` writes one `propagates_to` Assertion for each match and each
   Vulnerability it names (R-MATCH-1), with its own confidence and description, and a match that
   repeats another exactly is written once and counted. This changes a documented behavior: two
   matches sharing a CVE and a Component were one Assertion, and are now two. Tests:
   `test_an_advisory_paired_with_several_cves_anywhere_is_no_alias` (three cases),
   `test_distinct_matches_on_one_component_are_distinct_assertions`, which replaces
   `test_matches_sharing_a_cve_are_one_vulnerability_and_one_link`, and
   `test_a_match_repeated_exactly_is_one_assertion_and_counted`. On c39f2a4 they failed: the GHSA
   or ALAS id was an alias of each CVE, one Assertion stood for both matches, and the repeat was not
   counted.
5. **CWE links and the order of the matches.** Each match's CWE entries were read as soon as the
   match was, so an entry naming a CVE that a later match made a Vulnerability was dropped: which
   CWE links were written depended on the order of the rows, and so did which description was kept.
   Now `_Builder._matches` makes every Vulnerability first and reads the CWE entries after
   (`_Builder._cwe`), and makes Parties, Vulnerabilities and Weaknesses in sorted order;
   `_Builder._descriptions` picks a description by namespace, not by order, and lists a
   Vulnerability the scan describes in more than one way. Test:
   `test_the_order_of_the_matches_changes_nothing`, the same three matches in two orders, which
   must give the same model, evidence digests aside. On c39f2a4 the two models differed: the first
   order lacked the CVE-2026-0001 to CWE-79 link, and the descriptions differed.
6. **The product and the scanned build.** A scan was matched to its SBOM by the digest alone,
   though the digest Syft records is the one the image was named by, and an index digest is shared
   by every platform of a release (R-ID-1's cost); the scan's other source fields were never
   compared; and the Product id was made from the repository path without its registry, so
   `ghcr.io/org/app` and `index.docker.io/org/app` were both `product:org-app`. Now `_check_scan`
   also requires `source.type` to be `image`, `source.target.userInput` to name the same repository
   (a file or a folder Grype read is not compared), and, when Grype read an SBOM, the image id to be
   this SBOM's root `bom-ref`, which is where Grype records it (RPT-0004 Table 6a;
   `fanout-identity.md`: Syft's decoder maps the root as `ID: c.BOMRef`); a scan Grype made from the
   image itself records a configuration digest there and is still read. `_check_sbom`
   refuses a name that carries another digest than the version, and checks the image's own purl
   when there is one. The report gives the scan's image, image id, tags, repository digests and
   platform, and whether Grype's distro matches the SBOM's operating system. `_Builder._product`
   makes the Product id from the whole repository URL (R-ID-2) and the ProductInstance id from the
   whole digest (R-ID-1). This changes the fixture's two ids (above), and nothing else in its
   model. Tests: `test_ids_follow_the_identity_keys`, `test_a_scan_of_another_image_is_refused`
   (three cases), `test_an_sbom_naming_two_digests_is_refused` and
   `test_the_scans_identity_is_reported`; `test_a_scan_grype_made_from_the_image_itself_is_read`
   checks that a direct scan is still read. On c39f2a4 they failed: the Product id was
   `product:alpine`, three repositories shared one id, every mismatched scan or SBOM was accepted,
   and the report had no identity lines.
7. **The report accounts for every field and repeat.** Python's json keeps the last value of a
   repeated key, so a file with `"specVersion":"1.6","specVersion":"1.7"` was read as 1.7 without a
   word. The field inventory listed fixed levels only, so the fields inside `metadata.tools`, a
   supplier, `source.target`, `descriptor.db` or a CWE entry were never named, and values the
   import writes once (a CPE an entry repeats, a repeated dependency edge, a CWE entry that several
   matches carry) were not counted. Now `_read_json` builds objects with `_object`, which refuses a
   repeated key, and `_inventory` walks every field by its path: each field inside a part the
   import reads is listed, a part left out whole is counted with the values it holds, and a field
   with no rule, at any depth, is "not read by this import". `_Builder.repeats` counts what the
   inputs repeat, under "Repeated in the inputs, written once", and the report counts the Syft
   properties it leaves out. This changes the report's format: one list of paths, such as
   `components[].publisher`, replaces the lists by level. Tests:
   `test_a_key_repeated_in_one_object_is_refused` (in the SBOM and in the scan),
   `test_the_report_lists_nested_fields_by_path`,
   `test_a_nested_field_the_import_does_not_know_is_reported`,
   `test_repeated_values_are_counted_in_the_report`, `test_the_fixtures_repeated_values_are_counted`
   and the updated `test_the_report_accounts_for_every_field`. On c39f2a4 they failed: a repeated
   key raised no error, and none of the paths or repeat counts was in the report.
8. **Malformed input and provenance.** The fields the import reads were not type-checked: a number
   where a list belongs raised Python's own TypeError (in `properties` or `cwes`), a version, purl,
   description or supplier of the wrong type was dropped without a word, and JSON that Python reads
   but the JSON standard does not allow (NaN, a 5000-digit number, deep nesting, half of a
   surrogate pair) raised ValueError or RecursionError, or was read. A scan with no Grype version, a
   development build's `[not provided]`, a database Grype marks invalid, a schema version that is
   not text, or a database dated after the scan still gave Assertions their provenance. Now every
   field read goes through `_text_at`, `_list_at` or `_object_at`, which refuse the wrong type with
   the field's path (`components[0].properties is not a list`); `_read_json` and `_check_sound`
   refuse NaN and Infinity, a number too long to read, nesting deeper than 64 levels and text that
   is not valid Unicode; and `_check_scan` and `_scan_database` require a Grype release version, a
   database not marked invalid, a schema version that is text or a whole number, and a build time
   no later than the scan. Each refusal is an `SbomImportError`: exit code 2 from the command, and
   nothing written. Tests: `test_a_malformed_field_is_refused_with_its_path` (18 cases),
   `test_json_that_python_reads_but_is_not_sound_is_refused` (5 cases) and
   `test_the_command_exits_2_on_a_malformed_field`. On c39f2a4 they failed: a TypeError, ValueError
   or RecursionError escaped, or nothing was raised at all.

The review's two other observations are follow-ups, below. `engine/engine/cli.py` and the app are
not changed.

## What a human accepted

- @Clovier, 2026-11-25, after asking for each term to be explained: build #257 now, with the four
  provisional answers above ("yes i'm okay as they are, build 257"); for the match link, "pick the
  one the engine can draw"; use the alpine image RPT-0004's pilot scanned for the test files; and
  download a fresh Grype database.
- @Clovier, 2026-11-25: asked for these fixes ("do all those", after @kriishnaa-18's review of
  c39f2a4); the wording and code are Claude Code's draft until the pull request review accepts them.

The code, the mapping and the choices above are the agent's draft until a human reviews them on the
pull request.

## What was rejected, and why

- **The agent's first reason for `uses_component`.** It said the engine follows `uses_component` and
  `composed_of` when it spreads a CVE. The engine has no such code; the schema only defines the edge
  as the one along which spreading is sound. The agent corrected the reason before @Clovier chose,
  and the choice rests on consistency with the existing models and the schema's meaning.
- **`affects` for the package match.** `affects` stays Product-only (DL-0024).
- **Reading tradar's saved scan file.** It keeps only the packages with a match and drops the
  dependencies, the CWEs and the match details (#257).
- **Committing the scan file exactly as Grype wrote it.** It recorded three local paths, one with a
  home folder in it.
- **A scan with today's database as the fixture.** Its numbers cannot be checked against the pilot.

## Follow-ups

- **Juice Shop** (pv-03, #230): import its Docker image, then carry pv-03's threats and attack paths
  over, or the imported parts into pv-03. The import writes a fresh model and does not merge into
  an edited one; that stays open (#257's re-import question).
- **An upload screen in the app,** which #257 leaves as a follow-up: the engine opens models only from
  its approved directory, which the packaged app bundles, so users need a folder they can write to
  outside the app and an engine call that writes. Saving a review in the app (the MVP's step 4)
  needs the same.
- **More inputs:** SPDX 3.0.1 and other CycloneDX versions; SBOMs of folders and files, which need a
  key for their build; HBOMs stay out of scope (#257).
- **R-ID-1's other identifiers:** the index digest, configuration digest, platform and tags are not
  in Syft's CycloneDX output; Syft's own JSON has them.
- **Weakness names** from the pinned CWE catalog, instead of the id alone.
- **The model list's label:** `pv-` files show as "Proposal example (AI-drafted, unreviewed)"
  (`MODEL_KINDS` in `engine/engine/core.py`); an imported one is tool-made, not AI-drafted.
- **For the sponsor:** a `MAP-NNNN` for radar's data contract (DEC-002, ADR-0007), the instance key
  (R-ID-1), and the match predicate's name and confidence scale (R-MATCH-1) are provisional here.
- **The app's model report** (@kriishnaa-18's review, not blocking): it could set proposed
  vulnerability links apart from reviewed ones, and show a build's composition
  (`build_composed_of`). This change does not touch the app.
- **#243 also changes `engine/engine/cli.py`** (@kriishnaa-18's review, not blocking): check the
  `import-sbom` command when the two come together. This change does not touch `cli.py`.
- **purl type rules:** apply each type's own rules (which names ignore case) once a purl-spec
  version is pinned (DL-0015), so purls that differ only in such a case join.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
