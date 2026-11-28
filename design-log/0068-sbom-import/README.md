---
schema: "archdoc/v1"
id: DL-0068
title: "SBOM import: a starter model from Syft's CycloneDX SBOM of a container image and Grype's scan of it (#257)"
type: process
status: draft
version: "0.7.0"
date: "2026-11-25"
updated: "2026-11-27"
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
  [--platform OS/ARCH[/VARIANT]] -o MODEL [--report FILE] [--force]` in `engine/engine/cli.py`. It
  runs in-process only; the API has no route to it.
- `engine/tests/test_import_sbom.py` and the fixture in `engine/tests/fixtures/sbom-import/`.
- This entry.

### The mapping, as built

Each line is one of Table 6's candidate rules or one of #257's acceptance criteria.

- **Product:** one, keyed by the image's versionless purl (R-ID-2), such as
  `pkg:oci/alpine?repository_url=index.docker.io/library/alpine`. A short image name resolves the
  way Docker resolves it (`alpine` is `index.docker.io/library/alpine`). Its id is made from the
  whole repository, registry and path: a readable slug of it and a short hash of the Product's
  key, its purl, the first 16 hex digits (64 bits) of the key's SHA-256
  (`product:index-docker-io-library-alpine-d27fdaebde4326e0`). So the same path in another
  registry gets another id, and so do two repositories whose slugs are one because they differ
  only in punctuation (`ghcr.io/team/alpha-beta/app`, `ghcr.io/team/alpha/beta/app`), in separate
  imports too, but for a 1 in 2^64 chance; and one repository gets one id whatever its tag or
  digest (Review changes, fifth round, items 2 and 7; until then the id was the slug alone, and
  such repositories shared one; the hash had 8 digits until the sixth round). The purl in
  `identifiers` stays the key.
- **ProductInstance:** the scanned build, keyed by the digest Syft records in
  `metadata.component.version` and the build's platform (R-ID-1; decision 2 below), such as
  `linux/arm64/v8`. The digest is in `identifiers` and `version`, beside the versioned purl with the
  `oci` type's `arch` qualifier (`?arch=arm64&repository_url=...`, qualifiers sorted); the platform
  is also in its name and description, and its id is made from the whole digest and the platform
  (`product-instance:sha256-260479a1...-linux-arm64-v8`), a variant's dots written as dashes, as
  the models write a version's (`v8.1` as `v8-1`; no variant may hold a dash, so no two platforms
  share an id). The schema has no platform slot, so none is made up. `build_composed_of` lists
  every Component (ADR-0011 A4). The SBOM never fills the design-level `composed_of` (R-EDGE-2).
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
- **Ids:** each id is a readable slug of what its object is. An id made from a free-form key (the
  Product's purl, a Component's normalized purl, a Party's `organization:NAME`, a package match's
  finding and a CWE link's `cwe:...`) always ends in a dash and the first 16 hex digits (64 bits)
  of the key's SHA-256, so one key gets one id in every import, two keys never share one in an
  import and share one in two only by a 1 in 2^64 chance, and adding or removing other objects
  changes none, twins aside (`component:apk-alpine-zlib-1-3-2-r0-aa0ed361800ecaef` for the aarch64
  zlib). A package match's finding is the CVE it is linked to, the vulnerability id and
  namespace Grype reports, the Component's key, and each match detail's type and matcher, so a
  scan whose scores differ keeps its ids; matches with one finding are twins, told apart by
  their order: by the SBOM entry each is on (`artifact.id`), which a rescan of the same SBOM
  keeps, then by fingerprint. So a rescan keeps twins' ids too, and adding or removing one of
  several twins can renumber only the twins after it. A Vulnerability's and a Weakness's id are their canonical ids' slugs alone
  (`vulnerability:cve-2026-85091`, `weakness:cwe-787`), the ProductInstance's holds the whole digest
  and platform, and Grype's Party is `party:grype`. Should an id be another key's all the same, a
  counter is hashed in with the key until it is free (Review changes, fifth round, items 7, 8 and
  15).
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
2. **The instance key.** R-ID-1 asks for the platform manifest digest, but the CycloneDX file holds
   one digest, `metadata.component.version`, and does not say whether it is a platform manifest's or
   an index's (RPT-0004 Table 6, finding 9), and an index digest is shared by every platform of a
   release. So the key is the digest and the platform: os/architecture, and the variant when one is
   given. An index digest and a platform name exactly one build, and a platform manifest digest and
   its platform still name that one build. The digest is stored as `sha256:<hex>` in `identifiers`.
   The platform comes from `--platform OS/ARCH[/VARIANT]`, or from a scan Grype made of the image
   itself, which records it in `source.target` (`os`, `architecture`, and `architectureVariant`,
   the name Grype gives the variant); Grype leaves those empty when it read the SBOM, as for the
   fixture. Where both give a part, they must agree; a part only one gives is taken from it (Syft
   1.52.0 left the variant out of its own JSON, fanout-identity.md). With neither, the import is
   refused, with a message saying the SBOM does not record which platform its digest names and to
   pass `--platform` (for example `--platform linux/arm64/v8`). The SBOM's own record of its CPU is
   checked against the platform: the image's purl, when it has an `arch`, and each package purl's
   `arch` qualifier, read through a small table of distribution names (`aarch64` is `arm64`,
   `x86_64` is `amd64`, `i686` and `x86` are `386`, `armhf` is `arm`, `ppc64el` is `ppc64le`).
   An image purl naming another architecture, in any case (`arch=MIPS64LE` is `mips64le`), is
   refused, as a scan that contradicts `--platform` is: those are metadata about the build, and
   the platform's os and architecture come from them alone. The packages' qualifiers never refuse
   the import by contradicting the platform (Review changes, fifth round, item 1; the fourth
   round refused an SBOM most of whose packages were another platform's); what they can still
   refuse is a platform they leave unsettled, as the third round's paragraph below says, such as
   two variants pinned when the platform names none, an ambiguity. A package built for the
   platform's architecture or, on a 64-bit platform, for the 32-bit one it also runs (multiarch and
   multilib) is native; one built for any other is foreign, and is kept as a Component like any
   other, with its dependencies and matches, and the report lists it (fourth round, item 1; until
   then it was refused). When more packages are built for one other platform than for it, each
   architecture counting with its own 32-bit sibling, as the platform's does, or none is built for
   the platform's own architecture, the report and a warning say so, with the counts, where the
   platform came from, and the `--platform` to pass if the SBOM is of another build; the command
   prints the warning and exits 0. So does an SBOM with packages of a type only Linux
   distributions use (`apk`, `deb`, `rpm`, `alpm`) under a platform whose os is not linux (fifth
   round, item 11). The advice never names a platform the import would refuse, and following it
   imports without that warning (fifth round, item 6). A name not in the table is listed in the
   report as not checked, and `noarch`, `all` and `any` are skipped. This changes a documented
   choice: the key was the digest alone (Review changes, second round, item 2), and the command
   line: the fixture's import now needs `--platform linux/arm64/v8`. The rest stays. The first
   version reads SBOMs of container images only, and refuses any other SBOM with a message saying
   why: a folder or a file has no digest to key its build by. An image named by a version tag
   gives Syft no digest either (pilot.md: Syft writes the digest only for `latest` or a digest
   reference), and the message says to name the image by digest. A scan must also name this
   SBOM's root `bom-ref` as its image id when Grype read an SBOM (Review changes, item 6).

   Since the third round (Review changes, third round, items 1 and 2), the variant is checked too.
   Some names pin a 32-bit ARM variant, which depends on the distribution, so a second table reads
   them by purl type (and for `deb` by namespace) as the platform an image index lists for that
   build: Alpine's `armhf` is arm/v6 and `armv7` arm/v7, Debian's `armel` arm/v5 and `armhf`
   arm/v7, Ubuntu's `armhf` arm/v7, and RPM's `armv6hl` arm/v6 and `armv7hl` arm/v7. Raspbian
   writes Debian's `armhf` for ARMv6, so another distribution's `armhf` pins no variant, and no
   other name pins one (`aarch64` and `arm64` say nothing of v8.x). The variants that packages
   built for the platform's own architecture pin are counted as the architectures are: a platform
   that names a variant keeps it, those that pin another are kept and reported, and when more of
   them pin one other variant than pin its own, the report and a warning say so (fifth round, item
   1; the fourth round refused that, and until then any other variant was refused). A platform
   that names none takes the one they pin, and the model and the report say so; when they pin two,
   it is refused, with a message asking for the variant. A 32-bit sibling's variant is reported,
   never compared or taken, since the platform's variant is the 64-bit architecture's own. Two
   rules then settle a platform still without one: arm64's variant is v8, the only arm64 variant
   the OCI image index specification lists, so `linux/arm64` and `linux/arm64/v8` are one
   platform, one id and one model; and 32-bit arm, whose v5, v6 and v7 builds one index can list
   side by side, is refused, with a message asking for the variant. Each part of a platform must
   have its form: the os and the architecture letters and digits, a variant letters and digits
   with dots between them (`v8.1`), so `v8-1` is refused and no two platforms give one id. This
   changes two documented choices. The platform was keyed as given, so `linux/arm64` and
   `linux/arm64/v8`, which containerd treats as one platform, gave two ids (name it as the image
   index lists it, this said); they now give one. And a 32-bit arm platform with no variant was
   read; it is now refused unless its packages pin one. The platform is otherwise keyed as given,
   in lower case.
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
  and for `armv7`, which an arm64 image can hold side by side) are two Components. Entries that
  share a purl but give different names, types or versions are refused, every value against every
  other; where they give different descriptions, suppliers or manufacturers, that field is left out
  and listed. (Changed after review, item 1 below: until then, purls that differed only in
  qualifiers were one Component. The first round's example was zlib for `aarch64` and for
  `x86_64`, which one build rarely holds: from the second round's item 2 such an SBOM was
  refused, and since the fourth round's item 1 it is read, the `x86_64` zlib kept as a Component
  built for another platform. Each of the two has its own id, in every import, since the fifth
  round's item 7.)
- **Only the purl rules every type shares are applied.** Which names ignore case differs by type
  and changed between purl-spec versions (DL-0015, Phase 2), so two purls that differ only in such a
  case stay two Components, and a match on one is listed, never joined to the other.
- **An entry with no purl,** such as the operating system, is keyed by its type, name and version.
- **Weaknesses are named by their CWE id.** The import does not read the CWE catalog.
- **A CWE source is a Party named as the scan's database names it,** which for CISA's ADP is its
  organization UUID.
- **Descriptions are put on one line:** line breaks and runs of spaces become one space. The words
  are unchanged. A description with nothing to write (null, empty, or nothing but white space and
  characters that do not print, such as a zero-width space) is left out, and the report counts it
  as blank (Review changes, third round, item 3).
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
  Grype marks invalid, and a database dated after the scan. Since the second round (items 2 and 5):
  no platform, or a `--platform` that is not `OS/ARCH[/VARIANT]` or names its architecture as a
  distribution does (`aarch64`); a `--platform` the scan's platform contradicts; the image's purl
  naming another architecture than the platform's (in any case since the fifth round, item 9); and
  a time that leaves Python's years 1 to 9999 when moved to UTC, which now gets the field's message
  instead of a traceback. Since the third
  round (items 1, 2 and 4): a platform part outside its form (`v8-1`, `arm-64`); two variants of
  its architecture pinned by the packages when the platform names none; and 32-bit arm with no
  variant from the platform or the packages. Nesting deeper than 64 levels now gets the same
  refusal on every Python version. From the second round to the fourth, the packages' own
  architectures refused an import too: any package for an architecture the platform does not run,
  or (since the third round) pinning another variant, and since the fourth round only more such
  packages than the platform's own; and an SBOM none of whose packages is built for the
  platform's own architecture. Since the fifth round (item 1) they give a warning instead.
- **Outputs:** the model and the report are written to temporary files beside their paths and put
  in place only when both are written, so a failed import leaves neither, and puts back any file
  `--force` was replacing. An existing model or report, or a dangling link at its path, is never
  replaced without `--force`, because people edit starter models: without it, each file is put in
  place by a hard link (or, on a volume without them, an exclusive create), which fails if anything
  is there by then, so not even a file that appears while the import runs is written over. An input
  is never written over, whether by its own name, a link to it, a second name for the same file, or
  the same name in another case or Unicode form (names are compared as a Mac's volume compares
  them). Taking back a failed import removes or puts back only a file this import put there, and a
  file `--force` was replacing that cannot be put back is kept under its second name, which the
  command prints. Once both files are in place the import stands: a temporary file or a backup
  that cannot be removed then is named in a warning, and the command exits 0; and a backup copy
  cut short, on a volume without hard links, is removed, or named, before its error comes out
  (Review changes, fifth round, item 3), as is a temporary file whose write fails (item 5). On a
  volume without hard links (FAT, exFAT), each output is created exclusively and recorded by the
  identity it has once written, since such a volume gives an empty file a placeholder inode, so a
  failed import takes back what it created there too (item 4). `--force` gives each file it
  replaces the replaced file's permission bits, so a private model stays private; a new file, and
  one put where a link was, follow the umask (item 10). The model's text is read back before it
  is written and must give the model it was made from. Input text in the model's header and the
  report is escaped, so a line break cannot end a comment. The header names the output only by
  its relative path, or by its name when the path is absolute, so no home folder lands in a
  committed file.
- **Grype's distro is reported, not checked.** The report says whether the distribution Grype
  detected matches the SBOM's operating system, and flags a difference; it is not a refusal,
  because the two tools are not known to spell every distribution's name the same way.

## The fixture

The image RPT-0004's pilot scanned: `alpine:3.24.2` for linux/arm64/v8, platform manifest digest
`sha256:260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d` (the tag's index digest is
`sha256:294b683cb724…`). `alpine:latest`, which the pilot named, has since moved to an image pushed
on 2026-11-08, so the image was fetched by digest on 2026-11-25.

Neither file records that platform: the CycloneDX SBOM has no field for it, and Grype, which read
the SBOM, left `source.target.os` and `architecture` empty. So the fixture is imported with
`--platform linux/arm64/v8`, the platform the index lists for this manifest (or
`--platform linux/arm64`, the same platform since the third round), and its 16 packages'
`arch=aarch64` is read as `arm64`, the platform's architecture (decision 2).

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
  and that the same files give the same bytes. Since the reviews, also the regression tests listed
  under each item of the six rounds below: 319 tests in all (317 after the fifth round, 254 after
  the fourth, 236 after the third, 185 after the second, 135 after the first), counting each
  parametrized case.
- **The fixture's numbers are unchanged by the six rounds:** 17 Components, 24 dependency edges,
  15 Vulnerabilities, 9 Weaknesses, 4 Parties and 45 Assertions (30 package matches, 15 CWE links).
  Every package has its own purl and every match its own (CVE, Component) pair, so keeping the
  qualifiers and one Assertion per match (Review changes, items 1 and 4) change no count. Only two
  ids changed in the first round (item 6): `product:alpine` became
  `product:index-docker-io-library-alpine`, and `product-instance:alpine-260479a1cfaf` became
  `product-instance:sha256-260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d`. The
  second round changes one id again (item 2), because the key now holds the platform: the
  ProductInstance is
  `product-instance:sha256-260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d-linux-arm64-v8`,
  its name ends `for linux/arm64/v8`, and its purl carries `arch=arm64`. No other object of the
  fixture's model changes. The third round changes none: imported with `--platform linux/arm64/v8`,
  the model is e12ab07's byte for byte, and `--platform linux/arm64` now gives the same bytes. One
  line of its report changes (`components[].description`, item 3), and with `linux/arm64` the
  report adds a line saying that it is v8. The fourth round changes nothing of the fixture's: with
  either spelling, the model and the report are f21f4a5's byte for byte, and with
  `--platform linux/amd64` the import is still refused (exit code 2, nothing written), now with the
  counts. The fifth round changes ids only (items 2 and 7): the Product's, every Component's, the
  three CWE sources' Parties' and every Assertion's id now ends in a dash and 8 hex digits, a
  short hash of the object's key (`product:index-docker-io-library-alpine-d27fdaeb`,
  `component:apk-alpine-zlib-1-3-2-r0-aa0ed361`): 66 of the model's 92 ids. The Vulnerabilities',
  the Weaknesses', the ProductInstance's and `party:grype` are unchanged. With either spelling, a
  diff of the two versions' models, each old id mapped to its new one by matching every object on
  what it is, shows no other difference, header included. The report shows no id, and differs
  from 4be86c1's in one line, which says what `matches[].artifact.id` is now read for (item 18).
  With `--platform linux/amd64` the import now writes the model and
  the report and prints the warning (exit code 0, item 1). The sixth round changes the same 66 ids
  again, and nothing else: each now ends in 16 hex digits, its 8 and the next 8 of the same
  SHA-256 (`product:index-docker-io-library-alpine-d27fdaebde4326e0`), and one of them, a CWE
  link whose source is named by a UUID, gives up one character of its readable part to stay within
  80. Imported with `--platform linux/arm64/v8` and with `--platform linux/amd64`, each model is
  775a45c's byte for byte once each old id is mapped to its new one, and each report is 775a45c's
  byte for byte.
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

## Review changes, second round (2026-11-25)

@kriishnaa-18 re-reviewed 9207ad9 and asked for changes again: four blocking findings and one that
is not blocking. As in the first round, each item says what was wrong, what changed (in
`engine/engine/import_sbom.py` unless it says otherwise), and the regression tests in
`engine/tests/test_import_sbom.py`, each of which was run on 9207ad9 first. Those runs used a copy of
the tests whose helper `run` passes no platform, which 9207ad9 has no parameter for; so each
failure below is the finding's, not a missing option. A few tests passed on 9207ad9, and the items
say which and why.

1. **What the import writes over (P1).** `_place` folded case only, so on a Mac a model and a report
   named `café.yaml`, one with é as one character (U+00E9) and one with e and an accent (U+0301),
   were two places to `_check_outputs` and one file to APFS, which compares names that way: the
   report replaced the model without `--force`. And `_publish` checked that nothing was at a path
   and then moved over it with `os.replace`, so a file that appeared between the two, or a name the
   volume folds in some way `_place` does not, was written over. Its undo also removed or replaced
   whatever was at a path by then, and when putting back a file `--force` had replaced failed, it
   deleted the only other copy. Now `_place` compares real paths in Unicode's canonical caseless
   form, `NFD(casefold(NFD(path)))`, everywhere outputs are compared with each other and with the
   inputs. Without `--force`, `_place_new` puts each file in place with `os.link`, which fails if
   anything is at the path, then removes the temporary; on a volume that cannot make hard links
   (any other `OSError`), `_create_new` creates the file exclusively (`O_CREAT | O_EXCL`) and
   writes the text. `FileExistsError` refuses with `SbomImportError` and takes back what this
   import placed. `_take_back` removes or puts back a path only while it still holds the file this
   import put there (the same device and inode), and keeps a file `--force` was replacing that it
   cannot put back, naming it in a note that `engine/engine/cli.py` now prints. With `--force`, the
   files are still moved with `os.replace`, with the same backups. Tests:
   `test_names_a_mac_reads_as_one_are_one_place` (the other Unicode form, and that form in another
   case), `test_an_input_named_in_another_unicode_form_is_never_written_over`,
   `test_a_file_that_appears_after_the_check_is_never_written_over` (a report that appears once the
   model is placed), `test_the_undo_never_removes_a_file_this_import_did_not_place`,
   `test_a_forced_undo_keeps_what_it_cannot_put_back`,
   `test_a_forced_undo_that_cannot_put_a_file_back_keeps_it`,
   `test_a_volume_without_hard_links_is_written_by_exclusive_create`, and
   `test_a_volume_that_reads_two_forms_as_one_name_is_not_written_over`, which runs only where the
   test's own folder reads the two forms as one name (APFS) and is skipped elsewhere (Linux's ext4,
   so CI); it gets past `_check_outputs` and shows the volume itself refusing the report.
   `failing_move` now fails a hard link and an exclusive create too. On 9207ad9: neither pair of
   names was refused (pytest: DID NOT RAISE; on APFS the report replaced the model); the report
   that appeared was written over; the undo put the edited model back over another program's
   file; when putting it back failed, the I/O error replaced the original one and the edited model
   was lost, its backup deleted; and on the real volume the report was not refused either (DID NOT
   RAISE). The input test passed on 9207ad9 on APFS, where `os.path.samefile` already caught it;
   on a volume that tells the two forms apart it was not refused. The hard-link test passed on
   9207ad9, which made no links; it checks the new fallback.
2. **The build is the digest and the platform (P2).** The instance key was the digest alone, and an
   index digest is shared by every platform of a release, so two platform builds with different
   packages got one ProductInstance id: run on 9207ad9, the fixture's SBOM and the same SBOM with
   every `arch=aarch64` made `arch=x86_64` both gave
   `product-instance:sha256-260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d`. Now
   the key is the digest and the platform (decision 2): `parse_platform` reads `--platform`
   (`run(platform=...)`, `engine/engine/cli.py`), `_scan_platform` reads the scan's
   `source.target`, `_build_platform` refuses a disagreement or no platform at all, and
   `_Builder._check_architectures` checks the image's purl and the packages' `arch` qualifiers
   against it, through the table `ARCHITECTURES` and the 32-bit siblings in `ALSO_RUNS`, and lists
   names it does not know. `_Builder._product` makes the id from the digest and the platform and
   adds `arch` to the instance's purl; the model's header, the ProductInstance's name and
   description, and the report say the platform and where it came from, and the report says what
   the packages' architectures were checked against. The variant's field is `architectureVariant`:
   that is the JSON name the Grype 0.119.0 binary gives Syft's image metadata field `Variant`, read
   from the struct tags in the binary itself (the fixture's scan holds neither it nor a `variant`).
   The packages' check allows the 32-bit architecture a 64-bit platform runs, because Debian's
   multiarch and RPM's multilib install such packages beside the native ones (`libc6:i386` on
   amd64); without that, a real image would be refused. This changes a documented choice and the
   command line: the fixture's import now needs `--platform linux/arm64/v8`. Tests:
   `test_one_digest_on_two_platforms_is_two_builds`, `test_without_a_platform_the_import_is_refused`
   (with and without a scan), `test_a_direct_scans_platform_is_the_builds`,
   `test_a_variant_only_one_side_gives_is_no_disagreement`,
   `test_a_platform_the_scan_contradicts_is_refused` (os, architecture, variant),
   `test_a_platform_the_packages_contradict_is_refused` (four cases),
   `test_an_image_purl_for_another_architecture_is_refused`,
   `test_package_architectures_that_are_not_the_platforms_are_reported` (a 32-bit sibling, a name
   the table lacks, `noarch`), `test_the_platform_option_is_checked` (five cases),
   `test_the_platform_option_is_read_in_any_case` and
   `test_the_command_refuses_an_unnamed_platform`; `test_the_product_and_the_scanned_build_have_their_keys`
   and `test_ids_follow_the_identity_keys` are updated for the new id and purl. Two first-round
   tests change their example: `test_entries_whose_purls_differ_in_a_qualifier_are_two_components`
   and `test_a_match_joins_only_the_component_with_its_purl` paired the aarch64 zlib with an x86_64
   one, which no single build holds and which the new check refuses; they now pair it with the
   armv7 build an arm64 image can hold beside it, and still show item 1 of the first round: two
   Components, and a match joined only to its own build (both pass on 9207ad9 too). On 9207ad9,
   with the platform left out of each call, each test failed on what that build lacks: an import
   without a platform was not refused, no contradiction or malformed option was refused (pytest:
   DID NOT RAISE; the command exited 0, not 2), and the instance's id and purl had no platform, a
   direct scan's included.
3. **Every version an entry gives is compared (P2).** `_component` compared each entry sharing a
   purl with the first one only, so when the first gave no version, `1.0` and `2.0` in two later
   entries were never compared, and one Component took `1.0`. Now it collects every name, type and
   version all the entries give, and refuses two different ones, naming the first two entries
   that give them; the Component takes the one value given (it took the first version given before
   too, never the first entry's none). Names and types had no such gap, since every entry has both
   (an entry without a name, or with an unknown type, is refused), but the same loop now covers
   them. Tests: `test_versions_after_an_entry_with_none_must_agree` (none, `1.0` and `2.0`: refused)
   and `test_an_entry_with_no_version_merges_with_one_that_gives_it` (none and `1.0`: one Component,
   version `1.0`). On 9207ad9 the first failed (pytest: DID NOT RAISE); the second passed there, as
   it guards the value the fix must keep.
4. **The report says which values were written (P2).** A description is written only from a record
   whose id is the match's Vulnerability, and only the one `_descriptions` picks for it, but the
   field inventory said `Vulnerability.description` for every `matches[].vulnerability.description`
   and `matches[].relatedVulnerabilities[].description`. So an advisory's description (a GHSA whose
   match is written as its CVE) and a description in other words than the one written were reported
   as written. Now `_Builder._account_for_descriptions` follows every description in the scan,
   repeated matches too, and the inventory line of each description field says how many were
   written and how many were left out, and why, when any was: an advisory's, whose match is written
   as another id (most often a CVE); in other words than the one written for its Vulnerability; or
   with a match left out whole. A new list, "Advisory descriptions left out", names each advisory
   and the id its match is written as, and whether it is that id's alias; the list of
   Vulnerabilities described more than one way now names the namespaces left out too. The other
   field tables, checked for the same fault (a destination some of a field's values never reach):
   `metadata.tools.components[].version` and `metadata.tools[].version` (only Syft's is written),
   `components[].description`, `components[].supplier.name` and `components[].manufacturer.name`
   (left out where entries recorded as one Component disagree), `dependencies[].dependsOn` (an edge
   from the image, to or from an entry that is not a Component, or to itself), a record's `id` (one
   paired with more than one Vulnerability is listed, not written), and `cwes[].cve` and
   `cwes[].cwe` (an entry for an id that is not a Vulnerability, a placeholder, or no CWE). Each now
   says so. Those values were already counted or listed elsewhere in the report; only the inventory
   line claimed more. And a sentence before the inventory says that where a field went is for the
   entries and matches the import keeps: file entries, and the matches listed as left out, are left
   out whole. The fixture's descriptions are all written (NVD's text for each CVE), so its two
   description lines are unchanged; this item changes ten other lines of its report. Tests:
   `test_an_advisorys_description_that_is_not_written_is_listed`,
   `test_a_description_in_other_words_than_the_one_written_is_listed` and
   `test_fields_some_of_whose_values_are_left_out_say_so`. On 9207ad9 the inventory said
   `Vulnerability.description` for both left-out descriptions, and none of the new wording was
   there.
5. **A time outside the range Python holds (not blocking).** `_utc` moved a time with a time zone to
   UTC with `astimezone`, which raises `OverflowError` when the result leaves the years 1 to 9999
   (`0001-01-01T00:00:00+14:00`, `9999-12-31T23:59:59-14:00`), so the command ended in a traceback.
   Now `_utc` returns None for it, and the caller refuses it with the message it gives an unreadable
   time (`metadata.timestamp`, `descriptor.timestamp`, the database's build time): exit code 2, and
   nothing written. `_utc` also writes the time with `isoformat`, which gives the year four digits
   on every platform, where `strftime`'s `%Y` does not on all; the build time and the scan's time
   are compared as text. Tests: three new cases of `test_times_are_read_as_utc`,
   `test_a_time_outside_utcs_range_is_refused_as_an_unreadable_one` (each of the three fields with
   the two times and an unreadable one) and
   `test_the_command_exits_2_on_a_time_outside_utcs_range`. On 9207ad9 the two times raised
   `OverflowError` from `_utc`, out of the command too; the unreadable cases passed there, since
   they are the comparison, and so did the four-digit year on macOS, whose `strftime` pads it.

## Review changes, third round (2026-11-26)

@kriishnaa-18 re-reviewed e12ab07 and asked for changes: two build-identity findings (P2) and one
that is not blocking. @Maimcghee approved e12ab07 with one problem to fix and two notes, which are
follow-ups below. As in the earlier rounds, each item says what was wrong, what changed (in
`engine/engine/import_sbom.py` unless it says otherwise), and the regression tests in
`engine/tests/test_import_sbom.py`, each of which was run on e12ab07 first and failed there, as the
item says.

1. **A variant the packages pin (P2, @kriishnaa-18).** The table of distribution names read an
   `arch` qualifier as an architecture only, so the variant a name pins was dropped: an Alpine SBOM
   whose packages are `arch=armv7` (ARMv7) was imported as `--platform linux/arm/v6`, and with
   `--platform linux/arm` the arm/v6 and arm/v7 builds of one index digest got one id
   (`product-instance:sha256-260479a1...-linux-arm`). Now `ARCH_VARIANTS` gives the 32-bit ARM
   names whose variant a distribution defines, by purl type (and for `deb` by namespace), as the
   platform an image index lists for that build (decision 2); `ARCHITECTURES` is unchanged and pins
   no variant. `_built_for` reads a package through both, and `_Builder._check_variant` and
   `_Builder._settle_platform`, run from `_check_architectures`, apply the rules to the packages
   built for the platform's own architecture: a variant they pin that is not the platform's is
   refused; a platform that names none takes the one they pin, and the model's header, the
   ProductInstance's name and description and the report say so (`from --platform, and its variant
   v7 from the packages' arch=armv7`); packages that pin two variants are refused; arm64 with no
   variant is v8, and the report says how `linux/arm64` was read; and 32-bit arm with no variant
   from the platform or the packages is refused, with a message asking for it. A 32-bit sibling's
   variant (`ALSO_RUNS`) is reported in the packages' line but never compared or taken: the
   platform's variant is the 64-bit architecture's own, and a 64-bit CPU that runs 32-bit code runs
   each of its variants, as Debian's multiarch can install `armel` and `armhf` packages beside
   `arm64` ones. That is the least surprising rule found: comparing a v7 sibling with arm64's v8
   would refuse every arm64 image that holds a 32-bit package, and taking its variant would key an
   arm64 build as v7. A distribution's name in `--platform` is refused with the platforms it means
   (`armhf`: arm/v6 or arm/v7). The instance's purl, key and id are now made once the packages are
   read (`_Builder._instance`, split from `_Builder._product`), since they can settle the platform;
   the purl still names the architecture only, as the `oci` purl type has no qualifier for a
   variant (follow-ups). This changes the two documented choices decision 2 names: arm64 without a
   variant now means v8, and 32-bit arm needs a variant. Tests:
   `test_a_variant_the_packages_contradict_is_refused` (seven cases: the review's Alpine `armv7` as
   arm/v6, Alpine's `armhf` as arm/v7, Debian's and Ubuntu's `armhf` as arm/v6, Debian's `armel` as
   arm/v7, RPM's `armv7hl` as arm/v6 and `armv6hl` as arm/v7),
   `test_a_variant_the_scan_records_is_checked_against_the_packages`,
   `test_a_platform_with_no_variant_takes_the_one_its_packages_pin` (five cases),
   `test_the_arm_v6_and_v7_builds_of_one_index_are_two_builds`,
   `test_packages_that_pin_two_variants_are_refused`,
   `test_32_bit_arm_with_no_variant_anywhere_is_refused` (Raspbian's `armhf`, and no `arch` at
   all), `test_arm64_with_no_variant_is_v8`, `test_a_32_bit_siblings_variant_is_not_the_builds` and
   `test_a_distributions_name_that_pins_a_variant_is_refused_as_a_platform` (two cases). One
   second-round test changes its expected line, since the report now names the variant a name
   pins: `test_package_architectures_that_are_not_the_platforms_are_reported` expects
   `built for arm/v6 (arch=armhf)`, which was `built for arm (arch=armhf)`. A name the tables lack
   is now listed with its purl type (`loongarch64: 1 Component (pkg:apk)`). On e12ab07: every
   contradiction, the two variants and arm with none were accepted (pytest: DID NOT RAISE); the ids
   ended `-linux-arm`, one for v6 and v7; `linux/arm64` gave `-linux-arm64`, so another id and
   another model, with or without a 32-bit sibling; and `armhf` in `--platform` was refused as "a
   distribution's name for arm" with the example `linux/arm`, which names no variant, while
   `armv7hl` was taken as an architecture and refused only because the packages are arm64.
2. **No two platforms give one id (P2, @kriishnaa-18).** `_slug` writes each run of characters
   other than letters and digits as one dash, and a platform part could hold a dot, a dash or an
   underscore, so `linux/arm64/v8.1` and `linux/arm64/v8-1` gave one id for one digest,
   `product-instance:sha256-260479a1...-linux-arm64-v8-1`. Now `parse_platform` and
   `_scan_platform` check each part's form: the os and the architecture are letters and digits
   (`PLATFORM_NAME`), and a variant is letters and digits with dots between them
   (`PLATFORM_VARIANT`), so `v8.1` is read and `v8-1` is refused, with a message naming the form.
   The id keeps its form, and `_id` and `_slug` are unchanged: after its prefix, every id in the
   repository's models is letters, digits and dashes (609 ids in `spec/vectors/`, none with a
   dot), and the models write a version's dots as dashes (`product-instance:papermill-3-1-0`), so a
   variant's dots are dashes too (`v8.1` is `...-linux-arm64-v8-1`). No part can hold a dash now,
   so the id gives back the platform part by part, and no two platforms share one; each part is at
   most 20 characters, so the id is never cut to fit. No other id changes, and neither does the
   fixture's. Tests: `test_a_platform_part_outside_its_form_is_refused` (eight cases),
   `test_a_scans_platform_part_outside_its_form_is_refused`,
   `test_v8_1_and_v8_dash_1_are_never_one_build` and `test_distinct_platforms_never_share_an_id`,
   which imports 86 valid platforms (two operating systems, four architectures, and ten variants,
   dotted ones too, or none) and checks that two ids are the same exactly when the platforms are.
   On e12ab07: `v8-1`, `v8_1` and `lin_ux` were accepted (DID NOT RAISE), and run by hand, the
   review's two platforms gave one id; `v8.`, `.v8` and `v8..1` were refused without the allowed
   form; `arm-64` and `arm64.1` were taken as architectures and refused only because the packages
   are arm64; the scan's `v8-1` was accepted; and the property test failed at `linux/arm64`, whose
   model named no variant.
3. **A blank description (not blocking, @kriishnaa-18).** A description that was empty or only
   white space was not written, but the report did not count it: a description field's inventory
   line said `Vulnerability.description` unless some description was left out for a listed reason,
   so a whitespace-only advisory description was reported as written. One of characters that do not
   print, such as a zero-width space (U+200B), was written. Now `_description_at` reads every
   description, and one that is null, empty, or nothing but white space and characters that do not
   print (`_blank`) is not written and is counted as blank: under "Left out, with counts" ("SBOM
   component descriptions that are blank", "scan descriptions that are blank"), on a scan field's
   line (`left out: 1 blank (counted above)`), and in the rule for `components[].description`.
   Tests: `test_a_blank_advisory_description_is_counted_as_left_out`,
   `test_a_blank_vulnerability_description_is_not_written` and
   `test_a_blank_component_description_is_counted_as_left_out`, six cases each (empty, spaces, a
   line break and a tab, an ideographic space, a zero-width space, and null). On e12ab07 the line
   said `Vulnerability.description`, or the report had no count; the zero-width space was written as
   the description, and in the advisory's case listed as an advisory's description.
4. **The depth check on Python 3.14 (@Maimcghee).** `_read_json` checked that the top level is an
   object before it checked the depth. Python 3.11 to 3.13 raise RecursionError on a 100,000-deep
   array, which the import refuses as "nests too deeply to read"; Python 3.14's json reads it (on
   3.14.2, a standard-library script got the array back 100,000 levels deep, where 3.13.9 raised
   RecursionError), so the import refused it as "expected a JSON object at the top level", and
   `test_json_that_python_reads_but_is_not_sound_is_refused[text2-nests too deeply]` failed there.
   Now `_check_sound`, which walks the file without recursion, runs before the top-level check, so
   a file that nests too deeply is refused as one on every version, and every refusal stays. The
   engine's tests cannot run on 3.14 here (it has no PyYAML, and nothing was installed), but the
   reader itself, run on 3.14.2 with PyYAML stubbed, refused the array as "nests too deeply (more
   than 64 levels)", where e12ab07's said "expected a JSON object at the top level". Test:
   `test_the_depth_is_checked_before_the_top_level`, which reads the file as 3.14 does, with
   `json.loads` returning the deep array without raising, on every version. On e12ab07 it failed as
   on 3.14: "deep.json: expected a JSON object at the top level".

@Maimcghee's two notes, Parties named by raw identifiers and the `cli.py` conflict with #243, are
follow-ups below. `engine/engine/cli.py` and the app are not changed.

## Review changes, fourth round (2026-11-26)

@kriishnaa-18 re-reviewed f21f4a5 and asked for changes: one blocking finding (P2) and one that is
not blocking (P3). Item 3 is a defect found while checking those fixes. As in the earlier rounds, each item says what was wrong, what changed (in
`engine/engine/import_sbom.py` unless it says otherwise), and the regression tests in
`engine/tests/test_import_sbom.py`, each of which was run on f21f4a5 first and failed there, as the
item says. Every test of the earlier rounds passes unchanged.

1. **Packages built for another platform are kept (P2).** `_check_architectures` refused an SBOM if
   any package was built for an architecture the platform does not run, other than the 32-bit
   sibling a 64-bit platform also runs. A real image can hold such packages: Debian's multiarch
   installs them, after `dpkg --add-architecture`, for cross-compiling, and an emulator or a
   toolchain can bring some. So a valid SBOM was refused even when its native packages and the
   platform (from `--platform` or a scan of the image) agree. This item reverses the second round's
   refusal of foreign-architecture packages (second round, item 2; the follow-ups listed it as
   open). Now a package is native, built for the platform's architecture or for the 32-bit sibling
   it also runs (`ALSO_RUNS`), or foreign, built for any other architecture the tables know, and a
   foreign one is a Component like any other, with its dependency edges and its vulnerability
   matches. What replaces the refusal is a majority rule, `_Builder._check_majority`: the platform
   is refused only when more packages are built for one other platform than for it, each other
   architecture counting with its own 32-bit sibling (`SIBLING_OF`), as the platform's does, and the
   message gives the counts. So the fixture under `--platform linux/amd64` (16 for arm64, none for
   amd64) and 1 amd64 package beside 15 arm64 ones are still refused. A 32-bit platform does not run
   64-bit code, so arm64 packages are foreign to arm/v7, counted apart from arm's own. The tie rule
   is the agent's choice, open to review: a tie goes to the platform, which the packages then do not
   contradict (as when no package names a CPU), and the report says so. Refusing a tie would leave
   an evenly split SBOM no way in, since no option overrides the check, and a build's own packages
   are nearly always most of it. An SBOM none of whose packages is built for the platform's own
   architecture is still refused (all 386 is the 386 build, though amd64 runs it), and so is an
   image purl naming another architecture. The variants follow the same rule, in
   `_Builder._check_variant`: a platform that names a variant is refused when more of its
   architecture's packages pin one other variant than pin its own, as the third round's Alpine
   `armv7` packages under `--platform linux/arm/v6` still are, now with the counts; a tie goes to
   the platform; and packages that pin another variant beside those are kept and reported. A
   platform that names no variant still takes the one its packages pin, and when they pin two it is
   still refused, now with a message asking for the variant (`--platform linux/arm/VARIANT`). The
   third round's tables and rules (`ARCH_VARIANTS`, `_built_for`, `_settle_platform`, and a 32-bit
   sibling's variant reported, never compared or taken) are unchanged. The report lists the kept
   packages by architecture ("2 Components built for amd64 (arch=x86_64), not the platform's arm64:
   kept"), and the model's header says it in one line (`_Builder.foreign`). This changes two
   documented choices, in decision 2: packages built for another architecture were refused, and so
   were packages that pin a second variant under a platform that names one. The plan for this round
   refused a variant only when none of the variant-pinning packages gives the platform's; the agent
   applied the architectures' majority rule instead, since otherwise one Alpine `armhf` package
   beside 15 `armv7` ones would let the third round's contradiction through under
   `--platform linux/arm/v6`. Tests: `test_packages_built_for_another_platform_are_kept` (the
   platform from `--platform` and from a scan of the image: two x86_64 packages, one depending on
   the other, a native package depending on one, and a match on one; every Component, edge and
   Assertion of the fixture's model is kept, and so are the foreign ones),
   `test_arm64_packages_are_foreign_to_a_32_bit_arm_platform`,
   `test_most_packages_built_for_another_platform_is_a_contradiction` (four cases: the fixture; 1
   for amd64 beside 15 for arm64; 6 for amd64 against 5 for arm64 and 5 for arm; and all for 386),
   `test_a_tie_goes_to_the_platform` (two ties of architectures and two of variants),
   `test_packages_pinning_another_variant_beside_the_platforms_are_kept`,
   `test_most_packages_pinning_another_variant_is_a_contradiction` (none and 1 of 16 for the
   platform's variant) and `test_two_variants_and_a_platform_that_names_none_asks_for_it`. On
   f21f4a5: the mixed SBOMs, the ties and the kept variant were refused ("the SBOM's packages are
   built for amd64 (arch=x86_64), but the platform is linux/arm64/v8 (from --platform)", the same
   from the scan, and "more than one variant of arm" for the variants); and the contradictions were
   refused without their counts, and the two variants without asking for one (pytest: Regex pattern
   did not match).
2. **Every backup is tracked (P3).** With `--force`, `_publish` made the second names that keep the
   files it replaces (`_keep`) in one list comprehension, so when the second one failed, the list
   was never assigned, and the first, `.import-sbom-....old`, was left beside the outputs without a
   word. Now each is recorded as soon as `_keep` makes it, so a failure while making a later one
   removes the earlier ones; and `_remove` removes what a failed import made, names in a note on the
   original error any file it could not remove, as the second round's take-back notes do, and lets
   that error come out (the command prints the notes). Tests:
   `test_a_failed_second_backup_leaves_no_first_one` (no `.import-sbom-*.old` file beside the
   outputs, the outputs unchanged, and the original error) and
   `test_a_backup_that_cannot_be_removed_is_named`. On f21f4a5 the first left a
   `.import-sbom-....old` file beside the outputs, and the second's error had no note. A forced
   import that succeeds removes its second names as before (follow-ups).
3. **The outputs get the usual file permissions (found while checking this round).** Since the
   second round, `_place_new` links the temporary file into place, and `_temporary` made it with
   `tempfile.NamedTemporaryFile`, which creates a file only its owner can read (mode 0600). So the
   model and the report were 0600, where a file the user saves follows their umask (0644 under
   the usual 022). `_temporary` now creates the file as `_create_new` does, with mode 0o666 less
   the umask, under a random `.import-sbom-<hex>.tmp` name it creates exclusively. Test:
   `test_the_outputs_get_the_usual_file_permissions` (an unforced import, then a forced one, under
   umask 022). On f21f4a5 both files were 0600.

`engine/engine/cli.py` and the app are not changed.

## Review changes, fifth round (2026-11-27)

@kriishnaa-18 re-reviewed 4be86c1 and asked for changes: three findings, all P2 (items 1 to 3).
Items 4 to 18 are defects an independent review of those fixes found while they were checked,
one P2 and fourteen P3 (items 14 to 17 on its second pass, and item 18 on its third), each
reproduced before it was fixed. As in the earlier rounds, each item
says what was wrong, what changed (in `engine/engine/import_sbom.py` unless it says otherwise),
and the regression tests in `engine/tests/test_import_sbom.py`, each of which was run on 4be86c1
first and failed there, as the item says, unless it says the test guards a fix: a copy of the
final test file, run in a worktree of 4be86c1, failed 80 of its 88 new or changed cases, and
the other 8 are the guards items 4 and 15 name. Every other test (228, and the schema check,
which is skipped where LinkML is not installed) passes unchanged, there and here.

1. **The packages' architectures warn, where they refused (P2).** The fourth round's majority rule
   (`_Builder._check_majority`, and `_Builder._check_variant` for variants) still refused a valid
   SBOM when its packages built for another platform outnumbered the platform's own, even when
   `--platform` and the scan's `source.target` agreed: 16 arm64 packages beside 2 amd64 ones were
   refused under `linux/amd64`, and so was an SBOM none of whose packages is built for the
   platform's own architecture. This item replaces the fourth round's majority refusal (fourth
   round, item 1), and its tie rule with it. The platform's os and architecture come only from
   metadata, which must agree: `--platform` and the scan's `source.target` give them
   (`_build_platform`), and the image's own purl, when it names an architecture, must name the
   platform's (`_Builder._check_architectures`); a disagreement among them is refused as before.
   A variant the metadata leaves out still comes from the packages, as since the third round.
   The packages' `arch` qualifiers never refuse an import by contradicting the platform:
   `_check_majority` no longer raises, for
   more packages built for another platform or for none built for the platform's architecture,
   and `_check_variant` no longer raises when the platform names a variant and more packages pin
   another. Every package stays a Component, with its dependency edges and its matches, and is
   reported as before (`_Builder.foreign`, the report's architecture lines and the model header's
   one line). In place of the refusal, `_Builder._warn` adds a note to the report when the
   packages built for one other platform outnumber the platform's own, when none is built for its
   architecture, or when more pin one other variant than the platform's. The note gives the counts
   and where the platform came from, says that every package is kept, and names the `--platform`
   to pass if the SBOM is of another build: the platform's os with the architecture and variant
   most of those packages are built for (`_likeliest`, which item 14 replaces), and a scan Grype
   made of the SBOM when the scan records a platform that one would contradict (items 6, 11 and
   14 refine which platform it names). `ImportResult.warnings` carries the same
   text after the SBOM's name, and `engine/engine/cli.py` prints each warning as `warning: ...` on
   stderr and exits 0. That warning is the safety net the refusal was. These stay refusals: a scan
   that contradicts `--platform`, an image purl for another architecture, 32-bit arm with no
   variant anywhere, and packages that pin two variants when the platform names none, which is an
   ambiguity, not a contradiction, and asks for `--platform OS/ARCH/VARIANT`. A platform that
   names no variant still takes the one its packages pin. A tie with another platform gives no
   warning of its own, and the tie rule's note goes; one where none is built for the platform's
   own architecture still warns, for that (8 packages for 386 and 8 for arm64 under
   `linux/amd64`, item 13). When no package fits the platform, the report's line says "No package
   fits the platform." instead of listing nothing. Which `--platform` the advice names, and when
   it adds the scan, are the agent's choices, open to review. Tests:
   `test_an_sbom_mostly_for_another_platform_imports_with_a_warning` (the review's case: 16
   packages for arm64 and 2 for amd64, a dependency between the two and one from an arm64 package,
   and a match on one, under `linux/amd64` from `--platform` and a scan of the image, and from
   `--platform` alone: every Component, edge and Assertion of the fixture's model is kept with the
   new ones, and the report and the warning give the counts),
   `test_an_sbom_with_no_package_for_the_platforms_architecture_imports_with_a_warning` (every
   package for 386 under `linux/amd64`, with all 24 edges and 30 matches),
   `test_metadata_that_contradicts_the_platform_is_still_refused` (the review's SBOM imports under
   `--platform linux/amd64`, and is refused with a scan of the image pulled for `linux/arm64/v8`,
   and with an image purl for arm64) and `test_the_command_prints_the_platform_warning_and_exits_0`
   (the fixture under `linux/amd64`). The tests that expected the old refusals now check the
   warning, renamed to say so: `test_a_platform_the_packages_contradict_is_refused` is
   `test_packages_that_contradict_the_platform_are_kept_with_a_warning` (four cases),
   `test_most_packages_built_for_another_platform_is_a_contradiction` is
   `test_most_packages_built_for_another_platform_give_a_warning` (four cases),
   `test_a_variant_the_packages_contradict_is_refused` is
   `test_a_variant_the_packages_contradict_is_kept_with_a_warning` (seven cases),
   `test_a_variant_the_scan_records_is_checked_against_the_packages` is
   `test_a_variant_the_scan_records_is_kept_with_a_warning`, and
   `test_most_packages_pinning_another_variant_is_a_contradiction` is
   `test_most_packages_pinning_another_variant_give_a_warning` (two cases); and
   `test_a_tie_goes_to_the_platform` is `test_a_tie_with_another_platform_gives_no_warning` (four
   cases). `test_packages_that_pin_two_variants_are_refused`,
   `test_two_variants_and_a_platform_that_names_none_asks_for_it` and
   `test_32_bit_arm_with_no_variant_anywhere_is_refused` pass unchanged. On 4be86c1 every one of
   those imports was refused with the fourth round's message ("16 of the SBOM's packages are built
   for arm64 (arch=aarch64), but the platform is linux/amd64 (from --platform and the scan
   (source.target)), and 2 for amd64 or the 386 it also runs: more are built for another platform
   than for this one, so the SBOM is not of that build", "none of the SBOM's packages is built for
   amd64", "more pin another variant than the platform's"), and the command exited 2; the ties
   failed on `ImportResult.warnings`, which 4be86c1 does not have; and the metadata test failed at
   its first import, while its two refusals are 4be86c1's, unchanged.
2. **One repository, one Product id, in every import (P2).** `_Builder._id` makes an id a readable
   slug, which writes each run of characters other than letters and digits as one dash, and adds a
   short hash of the key only when another key already has that slug in the same model. A model
   has one Product, so the hash never came: `ghcr.io/team/alpha-beta/app` and
   `ghcr.io/team/alpha/beta/app` got one id, `product:ghcr-io-team-alpha-beta-app`, in their
   separate imports, as did `team/alpha.beta/app` and `team/alpha_beta/app`. Now the Product id is
   always the readable slug, as before, and a short hash of the repository URL, registry and path
   as `_image_repository` normalizes it: `_id` and `_slug` take `hashed`, which always ends the
   slug in the first 8 hex digits of the text's SHA-256, cutting the slug to make room, so the
   part after `product:` stays within the 80 characters `_id` allows; the `_id` registry records
   the id under the Product's purl, as before. Every distinct repository gets its own id, and one
   repository the same id in every import, whatever its tag or digest. This changes a documented
   choice: the mapping said two repositories that differ only in punctuation would share an id.
   With these fixes the fixture's Product id was `product:index-docker-io-library-alpine-1b919904`,
   in its own `id` and the ProductInstance's `of_product`, and no other id changed: the
   ProductInstance's was already made from the whole digest and the platform. Item 7 then makes
   every id made from a free-form key end in a hash of its key, the Product's included, so the
   hash is now its purl's, and the id `product:index-docker-io-library-alpine-d27fdaeb`. Tests:
   `test_repositories_whose_slugs_are_one_get_distinct_product_ids` (the review's two
   repositories and two more, on one registry, in separate imports: four ids),
   `test_one_repository_has_one_product_id_in_every_import` (two tags and a digest of one
   repository: one id), and `test_ids_follow_the_identity_keys`, updated for the fixture's new id
   (the three hold item 7's ids now).
   On 4be86c1 the four ids were one, `product:ghcr-io-team-alpha-beta-app`, and the other two
   tests found ids without the hash (`product:ghcr-io-team-app`,
   `product:index-docker-io-library-alpine`).
3. **What is left once the outputs are written (P2).** Once both outputs were in place, `_publish`
   removed its temporary files and the backups `--force` makes with an `unlink` that nothing
   caught, so a backup that could not be removed failed the import after both outputs had been
   replaced: `run` raised, and the command printed `error: cannot write (Permission denied)` and
   exited 1. And on a volume without hard links, `_keep` makes each backup with `shutil.copy2`,
   which can fail part way, on a full disk, after it has made the file; the caller records only a
   backup `_keep` returns, so a partial `.import-sbom-....old` was left beside the outputs without
   a word. Now, once every output is in place, `_publish` removes each leftover with `_remove`,
   which catches `OSError` file by file and goes on, and returns one warning for each file kept.
   The warning names the output, the file and what it is, and says the outputs were written:
   `model.yaml: the outputs were written, but .import-sbom-<hex>.old, a backup of the file --force
   replaced, could not be removed (Permission denied) and is left beside it; it can be deleted`.
   `run` puts them on `ImportResult.warnings` (a new field, empty by default), and
   `engine/engine/cli.py` prints each as `warning: ...` and exits 0. `_place_new` no longer
   removes its temporary file as soon as it has linked it into place: `_publish` removes it with
   the rest, so failing to remove a temporary file never takes back an import that is done either.
   `_keep` removes a partial copy before the error comes out, and when it cannot, adds a note to
   the error naming it, which `_print_notes` prints; the caller still removes or names every backup
   made before it, each recorded as it is made (fourth round, item 2). Tests:
   `test_a_backup_left_after_a_forced_import_is_a_warning` (both outputs replaced and their two
   backups not removable: `run` returns, both files hold the new text, and the two warnings name
   the two backups, which hold the old texts),
   `test_the_command_prints_a_kept_backup_as_a_warning_and_exits_0`,
   `test_a_temporary_file_left_after_an_import_is_a_warning` (unforced, the two temporary files
   not removable: both outputs are written, and the two warnings name the two temporary files),
   `test_a_backup_copy_that_fails_part_way_leaves_nothing` (with `os.link` failing, the model's
   backup copy cut short, and the report's after the model's was made: no `.import-sbom-*.old`
   file is left, the old outputs are unchanged, and the original error comes out) and
   `test_a_partial_backup_that_cannot_be_removed_is_named`. On 4be86c1 `run` raised the
   PermissionError, and the command exited 1; failing to remove the model's temporary file took
   the model back, and the import raised the PermissionError too; the partial copy was left beside
   the outputs, in both cases; and the error had no note.
4. **A failed import on a FAT or exFAT volume (found while checking this round, P2).** On a volume
   without hard links, `_place_new` creates each output exclusively (`_create_new`), which
   recorded the file's device and inode from `fstat` right after the create, before the text was
   written. macOS's msdos and exfat drivers give an empty file a placeholder inode (a number near
   2^64, one per file), which changes once data is written, so when the second output failed,
   `_take_back` found another inode at the model's path, left the model, and said another program
   had replaced it, which was false. With this round's first three items, on a 20 MB FAT and a
   20 MB exFAT disk image (made with `hdiutil`), filled so the report's placement ran out of
   space, the command exited 1 with that note twice and left `model.yaml` and an empty
   `report.md` (4be86c1 removed the model's temporary file before placing the report, which
   freed the room, but it left the model in the same way when the report's placement failed
   otherwise, as the two existing tests below show). Now `_create_new` writes, flushes
   and syncs the text first and records the stamp from `fstat` after that: a probe on both volumes
   showed that stamp equals `lstat` once the file is closed, and that an empty file's placeholder
   holds still and is that file's own. `placed` does not hold the file while it is written, so a
   write that fails is taken back in `_create_new` itself: the file is removed while the path
   still names the open file (`_names`, which reads `fstat` and `lstat` at once), and named in a
   note when it cannot be removed or another file is there by then (`_remove`, whose note now says
   "left there" when the file is the output itself). On the same two volumes, short of space in
   the same place, the command now exits 1 with `error: cannot write (No space left on device)`
   alone and leaves nothing; a traced run showed the model created and written, the report's
   create failing, and the model taken back with no note. The review's probe of a failed move on
   each volume, and the two existing tests that failed with their temporary folders on such a
   volume, `test_a_failed_move_leaves_neither_file` and
   `test_a_volume_that_reads_two_forms_as_one_name_is_not_written_over`, pass on both; with
   4be86c1's code they left `model.yaml` and `café.yaml` behind. At every free-space level on
   both volumes, fresh and forced, the import now either writes both files and leaves nothing
   else, or fails for lack of space and leaves nothing, or the old files put back. Six tests
   cannot hold on such a volume, before these fixes or after, for what it lacks (item 17):
   `test_a_fifo_is_refused_without_waiting` (no FIFOs),
   `test_a_second_name_for_an_input_is_never_written_over` (no hard links),
   `test_a_report_that_cannot_be_written_leaves_no_model` (a 0500 folder stays writable),
   `test_a_file_that_appears_after_the_check_is_never_written_over` (its harness hooks `os.link`,
   which such a volume never reaches), and `test_the_outputs_get_the_usual_file_permissions` and
   item 10's test (every file there is 0700). Tests, which run anywhere, CI included, with
   `fstat` and `lstat` patched so that an
   empty file reports one fixed placeholder inode, and hard links failing:
   `test_a_failed_import_on_a_volume_with_placeholder_inodes_leaves_nothing` (the report cannot be
   created: nothing is left, and no note),
   `test_an_import_on_a_volume_with_placeholder_inodes_is_written`, and
   `test_a_write_that_fails_on_a_volume_with_placeholder_inodes_is_taken_back` (the model's own
   write fails: its file is removed; or named, when it cannot be removed; or, when another
   program's file is at the name by then, left with a note). On 4be86c1 the failed import and the
   failed write left the model, with the false note; the file that could not be removed got the
   false note in place of its own; and the successful import failed only on
   `ImportResult.warnings`, which 4be86c1 does not have, as its files were written there too. The
   case of another program's file passes on 4be86c1 too: it guards that the new removal never
   takes another program's file.
5. **A temporary file that cannot be written or removed (found while checking this round, P3).**
   When writing a temporary file failed, `_temporary` removed it with an `unlink` that nothing
   caught, so when that failed too, its error replaced the original and the file was never named:
   with the report's temporary file failing its `fsync` on a full disk, and neither temporary file
   removable, the command said `error: cannot write (Permission denied)` and named only the
   model's. Now `_temporary` removes the file through `_remove`, as `_keep` removes a partial
   backup, adds its notes to the original error and raises that. Test:
   `test_a_temporary_file_that_cannot_be_written_or_removed_is_named` (the command prints `No
   space left on device` and names both temporary files). On 4be86c1 it printed `Permission
   denied`.
6. **The advice never names a platform the import refuses (found while checking this round,
   P3).** Two cases. When the SBOM's image purl names an architecture, the import gets that far
   only if it is the platform's, so a `--platform` for another architecture is refused: the
   fixture with `arch=amd64` in its image purl, under `linux/amd64`, was told to pass
   `--platform linux/arm64`, which the purl then refused. Now `_Builder._warn` names no other
   architecture when the image purl names one, and says instead that the SBOM's own image purl
   also names the platform's architecture; advice for another variant of that architecture stays,
   as an `oci` purl names no variant, unless another architecture outnumbers the platform's too:
   then, as the next sentences say, the variants give no warning, and only the report lists the
   packages that pin another variant (item 16). And when another architecture outnumbered the
   platform's,
   `_check_variant` could warn too: with 6 Alpine `armv7` packages and 10 `aarch64` ones under
   `linux/arm/v6`, one warning named `linux/arm64` and another `linux/arm/v7`, under which the
   first came back. Now `_check_majority` says whether it warned so, and `_check_variant` then
   gives no warning of its own. The scan's wording is unchanged. Tests:
   `test_an_image_purl_for_the_platform_is_named_in_place_of_another_architecture`,
   `test_an_image_purl_leaves_the_advice_for_another_variant` and
   `test_another_architecture_outnumbering_the_platforms_gives_one_warning` (under `linux/arm/v6`
   and `linux/arm/v7`: one warning, naming `linux/arm64`, which item 14 writes `linux/arm64/v8`);
   and every test of a warning that names a platform to pass now imports the SBOM again under it,
   and finds no warning there (`followed`, or the test's own import; item 17 adds the last two).
   On 4be86c1 each of these imports was refused by the fourth round's majority rule.
7. **Ids that changed or collided between imports (found while checking this round, P3, as item
   2).** `_id` added a hash only when another key had the slug in the same model, so a
   Component's, a Party's and an Assertion's id depended on what else the import held: the armv7
   zlib was `component:apk-alpine-zlib-1-3-2-r0` alone and `...-r0-a7ac6a88` beside the aarch64
   one; the aarch64 and the x86_64 zlib had one id in their separate imports; `Alpine Linux` and
   `alpine.linux` were `party:alpine-linux` and `party:alpine-linux-33d91671` in one import, and
   `alpine.linux` was `party:alpine-linux` in another; and adding a package could change the ids
   of another package's Assertions. Now every id made from a free-form key always ends in a short
   hash of that key, not of its readable text: the Product's (its purl), each Component's (its
   normalized purl), each Party's (`organization:NAME`) and both kinds of Assertion's
   (`match:...` and `cwe:...`; item 15 makes a package match's key its finding alone); a package
   match's readable part names the Component's purl, not
   its id, which ends in a hash of its own. The Vulnerabilities' and Weaknesses' ids (their
   canonical ids), the ProductInstance's (the whole digest and platform) and `party:grype` are as
   they were. The Product's hash changes from the repository URL's to its purl's, so the fixture's
   Product is `...-d27fdaeb`, where item 2 made it `...-1b919904`. In the fixture's model, 66 of the
   92 ids change: the Product, the 17 Components, the 3 CWE sources' Parties and the 45 Assertions,
   each the old id with a dash and 8 hex digits after it. A diff of the two versions' models, each
   old id mapped to its new one by matching every object on what it is, shows nothing else
   changed, header included; and the report is 4be86c1's byte for byte, as it shows no id. Tests:
   `test_a_components_id_is_the_same_beside_another_build_of_it`,
   `test_two_builds_of_one_package_never_share_an_id`,
   `test_parties_whose_names_slug_alike_keep_their_own_ids` and
   `test_assertion_ids_hold_when_another_package_is_added` (a zlib whose purl has no qualifiers,
   and no match of its own); the tests that show ids hold the new ones
   (`test_ids_follow_the_identity_keys`, `test_packages_built_for_another_platform_are_kept` and
   item 2's), and
   `test_an_sbom_with_no_package_for_the_platforms_architecture_imports_with_a_warning` compares
   its two builds by name, as their ids now differ. On 4be86c1 each failed as this item's
   first sentences say.
8. **An id another key has taken is never given twice (found while checking this round, P3).**
   `_id`'s fallback, the slug and a hash of the key, was given out unchecked, so a crafted entry
   could hold it first: `pkg:apk/alpine/zlib@1.3.2-r0-a7ac6a88`, beside the two zlibs, took
   `component:apk-alpine-zlib-1-3-2-r0-a7ac6a88`, the armv7 zlib's fallback, and the import ended
   in `internal error: the model does not hold together (duplicate model object id ...)`. Now
   `_id` keeps deriving a new suffix, a hash of the key with a counter after it, until the id is
   free, so the same inputs always give the same ids. Under item 7 that entry no longer
   collides, as each Component's id ends in its own key's hash; the same collision is still
   possible among ids that are slugs alone, such as `GHSA-AAAA-BBBB-CCCC`, `ghsa-aaaa-bbbb-cccc`
   and a third id that spells the second's fallback. Tests:
   `test_a_purl_that_spells_another_components_id_gives_a_model` (the review's entry) and
   `test_vulnerability_ids_that_spell_one_another_give_a_model` (the same collision under the new
   rule). On 4be86c1 both ended in the internal error, for `...-r0-a7ac6a88` and for
   `vulnerability:ghsa-aaaa-bbbb-cccc-8b8e9abd`.
9. **An image purl's architecture in any case (found while checking this round, P3).**
   `_check_architectures` compared an image purl's arch that the table does not know as it was
   written, so `arch=MIPS64LE` was refused under `--platform linux/mips64le`, which is read in
   lower case. Now it is compared in lower case too. Test:
   `test_an_image_purl_names_its_architecture_in_any_case`. On 4be86c1:
   `metadata.component.purl says arch=MIPS64LE, but the platform is linux/mips64le`.
10. **`--force` keeps the mode of the file it replaces (found while checking this round, P3).** A
    forced import moved its temporary file, made by the umask (0644 under 022), over the model, so
    a private 0600 model became readable by others. Now `_publish` gives the temporary file the
    permission bits of the regular file it replaces, before the move (`_take_mode`); a link at the
    path is replaced, not followed, so the new file there follows the umask, as a new file does.
    Test: `test_a_forced_import_keeps_the_mode_of_the_file_it_replaces` (a 0600 model stays 0600,
    a link at the report's name becomes a 0644 file, and the file the link named keeps its mode
    and text); `test_the_outputs_get_the_usual_file_permissions` passes unchanged. On 4be86c1 the
    model became 0644.
11. **Linux packages under another os (found while checking this round, P3).** Nothing compared
    the platform's os with the packages: `--platform windows/arm64/v8` imported the fixture's 16
    `apk` packages without a word. Now `_Builder._check_os` warns, through `_warn` (the report's
    note and `ImportResult.warnings`, never a refusal), when packages of a purl type only Linux
    distributions use (`apk`, `deb`, `rpm`, `alpm`) meet a platform whose os is not linux. The
    warning names the os and the types, and the `linux/ARCH[/VARIANT]` platform to pass. Every
    warning's advice then names linux when the packages are a Linux distribution's, and the OS
    warning names the architecture another warning names, so two warnings never send the user two
    ways (`advice_os`, `pointed`; the agent's choice, open to review). Tests:
    `test_linux_packages_under_another_os_give_a_warning` (the command exits 0 with the warning,
    and under the platform it names there is none) and `test_two_warnings_name_one_platform_to_pass`
    (`windows/amd64`: both warnings name `linux/arm64`, under which there is none). On 4be86c1 the
    first printed nothing, and the second was refused by the majority rule.
12. **Two parts no test checked (found while checking this round, P3).** Mutating the report's "No
    package fits the platform." line, or the `/VARIANT` placeholder in the advice, failed no test.
    Tests: `test_the_report_says_when_no_package_fits_the_platform` (the fixture under
    `linux/amd64`) and `test_the_advice_asks_for_the_variant_32_bit_arm_needs` (Raspbian's `armhf`
    packages, which pin no variant, under `linux/amd64`: the advice names `linux/arm/VARIANT`, and
    `linux/arm/v6` then imports with no warning). On 4be86c1 both imports were refused. The
    review's four mutations, and one for each other change of items 4 to 11, each fail at least
    one test now; taking the stamp before the write again, as 4be86c1 did, fails
    `test_a_failed_import_on_a_volume_with_placeholder_inodes_leaves_nothing`.
13. **Sentences that were no longer true (found while checking this round, P3).** Corrected: the
    note in "Other choices" that an SBOM with zlib for `aarch64` and for `x86_64` is refused (it
    is read since the fourth round); "the packages never refuse" (decision 2, item 1 of this round
    and a test's header), since packages that pin two variants under a platform that names none
    are still refused, as an ambiguity; that the platform comes only from metadata (the module's
    docstring, `_check_majority`'s and item 1), since a variant the metadata leaves out comes from
    the packages; the tie (item 1, `_check_majority`'s docstring), since a tie where none is built
    for the platform's own architecture still warns, for that; and the exit codes in
    `engine/engine/cli.py`'s docstring, which now give `import-sbom`'s 1 for a file it could not
    write and say that it exits 0 with its warnings. Also corrected: the module docstring's account
    of the ids and a comment on the report's line for foreign packages. Test:
    `test_a_tie_where_none_is_built_for_the_platforms_architecture_still_warns` (8 packages for 386
    and 8 for arm64 under `linux/amd64`: one warning, naming `linux/386`, under which there is
    none). On 4be86c1 the import was refused.
14. **Advice that sent the user back and forth (found while checking this round, P3).**
    `_likeliest` advised the single build most of the outnumbering packages were built for, but a
    group of builds holds together only under its 64-bit architecture: with 7 packages for
    x86_64, 5 for Alpine's `armhf` (arm/v6) and 4 left for aarch64, `linux/amd64` advised
    `linux/arm/v6`, `linux/arm/v6` advised `linux/amd64`, and only `linux/arm64` gave no warning.
    Now one rule, `_build_to_pass`, names the platform for both warnings, more packages for
    another platform and none for the platform's own architecture. Of the architectures the
    packages are built for, it takes the one under which the most of them are native, built for
    it or for the 32-bit sibling it also runs; on a tie, the one the most are built for
    themselves (8 for ppc64le beat 6 for arm64 and 2 for the arm it runs), then the first by
    name. 386 packages alone advise `linux/386`, as no package is built for the amd64 that runs
    them. Its variant is the one most of its own packages pin, the first in sorted order
    on a tie; arm64's default, v8, when they pin none; and the `/VARIANT` placeholder for 32-bit
    arm. Under the platform it names, no other platform can outnumber the platform's own and some
    package is built for it, so the advice leads to a model with no such warning, from any
    platform. The os's and the image purl's rules (items 6 and 11) are unchanged. As arm64's
    default is v8, the advice now writes arm64 as `linux/arm64/v8`, the platform the import reads
    `linux/arm64` as, and ten test cases that expected `linux/arm64` there expect that. `followed`'s
    docstring now says only what it does. Tests:
    `test_the_advice_names_the_platform_most_packages_are_native_to` (the review's case under
    `linux/amd64`, `linux/arm/v6` and `linux/386`: each advises `linux/arm64/v8`, under which, as
    under `linux/arm64`, there is no warning),
    `test_packages_for_386_alone_advise_386_not_the_amd64_that_runs_them` (under `linux/amd64`
    and `linux/arm64`), `test_a_tie_goes_to_the_architecture_more_packages_are_built_for` and
    `test_the_advice_leads_to_no_warning_from_any_platform` (six mixes of
    builds, each imported under six platforms, every warning's advice followed to a model with no
    warning). On 4be86c1 each import was refused by the majority rule.
15. **A rescan gave a match a new id (found while checking this round, P3).** Item 7 hashed a
    package match's key, its CVE, its Component's key and its fingerprint, the SHA-256 of the
    whole match, so a scan with a newer database, whose EPSS, risk or CVSS for the same finding
    differ, gave its Assertion a new id: changing only `matches[0].vulnerability.epss` moved the
    zlib match's. 4be86c1, whose ids were slugs alone, kept it. Now the key is the finding alone
    (`_finding`): the CVE it is linked to, the vulnerability id and namespace Grype reports, the
    Component's key, and each match detail's type and matcher; never a score, an EPSS, a risk, a
    description, a URL, a fix state or a time. Matches that share a finding are twins, and keep
    one Assertion each: `_id` takes a `twin` count and gives each later twin the next free id its
    counter gives, so twins are told apart by their order, which follows their fingerprints, so
    the scan's own order still changes nothing; a twin's id can change when its scores do, and no
    other match's can. The fixture has no twins. In its model the 30 package matches' ids change
    once more, each keeping its readable part; the 15 CWE links' and every other id stay item
    7's, and the report is the same. Tests:
    `test_a_rescan_that_changes_only_scores_or_words_keeps_every_assertion_id` (EPSS, risk, CVSS,
    description, fix state and URLs, each changed on every match),
    `test_matches_that_differ_in_type_or_matcher_keep_ids_of_their_own` (each match's id is the
    same with the other or without it),
    `test_matches_that_say_one_finding_get_two_ids_in_a_fixed_order` and
    `test_cwe_link_ids_are_the_round_s_own`. The six rescan cases pass on 4be86c1, whose
    Assertion ids held no hash, so they guard this fix: run on a copy of the review's snapshot
    of this round's code before item 14, all six failed. On 4be86c1 the type and matcher cases
    failed, as one of the two matches took a fallback id that changed with the other's presence,
    and the CWE link's id had no hash; the twins case passes there, as a guard of one Assertion
    per match.
16. **What the variants say when the image purl has spoken (found while checking this round,
    P3).** `_check_variant`'s docstring said that when another architecture outnumbers the
    platform's, the warning for that names the architecture, and item 6 said that advice for
    another variant of the image purl's architecture stays. With an image purl, that warning
    names no other architecture (item 6), and the variants then give no warning either: with 6
    `armv7` packages and 10 `aarch64` ones under `linux/arm/v6`, and an image purl for arm, the
    one warning names no platform, and only the report lists the 6 packages for arm/v7, as kept.
    Both texts now say exactly that; the code is unchanged. Test:
    `test_an_image_purl_and_another_architecture_leave_the_variants_to_the_report`. On 4be86c1
    the import was refused.
17. **What this entry said of the tests (found while checking this round, P3).** Item 4 said that
    two tests cannot hold on a FAT or exFAT volume; with their temporary folders on one
    (`--basetemp`), six fail, as item 4 now says, each for what such a volume lacks. On 600 MB
    FAT and exFAT images, the whole test file failed those six and no other, with this round's
    code before item 14 and with its final code. And item 6 said that every test of a warning
    imports the SBOM again under the platform its advice names, which
    `test_the_command_prints_the_platform_warning_and_exits_0` and
    `test_metadata_that_contradicts_the_platform_is_still_refused` did not; both now do, and item
    6 says it of every test of a warning that names a platform to pass. On 4be86c1 both tests
    failed before their new lines: the command exited 2, and the first import was refused.
18. **Twins kept their ids only by chance in a rescan (found in the final check of this round,
    P3).** Item 15 told twins apart by their fingerprints, which hold every score, so a rescan that
    changed only their scores could swap the two ids: in the review's probe of 7 real twin pairs,
    20 rescans each, about half the pairs swapped on each rescan, though only the ids moved, as
    real twins' Assertions are the same apart from their ids. Real twins come from a package the
    SBOM records twice, under two bom-refs (as Syft does for a package it finds in two places):
    Grype's two matches share everything but `artifact.id` and the locations. And with twins whose
    words differ, which the probe made up, adding a match could move which description an existing
    id carried, so the Ids bullet's "adding or removing other objects changes none" was not true of
    twins. Now `_row` reads `artifact.id`, the SBOM entry a match is on (its bom-ref, when Grype
    read the SBOM), and `_Builder._match_assertions` orders twins by it, then by fingerprint, the
    order under which the same probe found no rescan to swap any pair, of all 140. The report's
    line for `matches[].artifact.id` says what it is read for, the one line of the fixture's report
    that changes; the join is still by purl (R-MATCH-2). The Ids bullet now says that adding or
    removing one of several twins can renumber the twins after it. The fixture has no twins, so its
    model is unchanged. Test: `test_twins_keep_their_ids_when_their_scores_change` (two twins on
    two entries, with other affected versions so each Assertion's description names its match,
    imported and then rescanned with new scores and in the other order: each keeps its id). On this
    round's code before this item, two of its four cases failed, the two ids swapped. On 4be86c1
    all four failed: one twin took the bare slug and the other a fallback id hashed from a key that
    held its fingerprint, which the rescan's new scores changed.

`engine/engine/cli.py` now prints the warnings and gives `import-sbom`'s exit codes; the app is not
changed.

## Review changes, sixth round (2026-11-27)

@kriishnaa-18 re-reviewed 775a45c: the fifth round's fixes hold, and one minor correctness issue
remains (item 1). As in the earlier rounds, the item says what was wrong, what changed (in
`engine/engine/import_sbom.py`), and its regression tests in `engine/tests/test_import_sbom.py`,
each run on 775a45c first, where it failed. Every other test passes, six of them (eight cases)
once the ids they name carry 16 digits.

1. **A hashed id ended in 32 bits of its key's hash (P3).** An id made from a free-form key ended
   in the first 8 hex digits of the key's SHA-256 (fifth round, items 2 and 7). In one import a
   counter tells apart two keys whose ids would be one, but in separate imports the hash is all
   that tells apart two repositories whose slugs are one, and 32 bits left each such pair a 1 in
   2^32 chance of one Product id. A search over the separators between the same ten letters found
   a pair in under 78,000 tries: `ghcr.io/team/a-b-c-d-e/f.g/h-i.j` and
   `ghcr.io/team/a.b-c/d-e-f.g.h/i_j`, which on 775a45c both gave
   `product:ghcr-io-team-a-b-c-d-e-f-g-h-i-j-c9e24419`. Now `HASH_DIGITS` is 16, so every hashed
   id (the Product's, every Component's, every Party's but `party:grype`, and every Assertion's)
   ends in 64 bits of its key's SHA-256: the 8 digits it had and the next 8. One key still gives
   one id in every import, and two free-form keys share one in separate imports only by a 1 in
   2^64 chance. The rule is one for every hashed id, as the Ids bullet has said since the fifth
   round, and the same reasoning reaches the Components', Parties' and Assertions' ids, so they
   lengthen with the Product's.

   The 80-character limit stays, by choice: no id grows past the length it could reach before,
   and a hashed id's readable part gives up what passes 63 characters, where it gave up what
   passed 71 (`_slug`). One of the fixture's ids does, by one character: a CWE link whose source
   is named by a UUID. A limit of 88 would keep every readable part whole, at the cost of longer
   ids. An id made from a canonical key is unchanged unless it holds a hash: one whose slug is
   longer than 80 characters is cut and ends in a hash of it, and one whose id another object has
   takes a fallback hash, and both hashes now have 16 digits. Two canonical keys whose slugs are
   one, such as `GHSA-AAAA-BBBB-CCCC` and `ghsa-aaaa-bbbb-cccc` (one advisory), still give one id
   in separate imports, as before, since the slug alone is the id.

   Tests: `test_repositories_whose_first_8_hash_digits_are_one_get_distinct_product_ids` (the two
   repositories above, imported separately: on 775a45c both got the one id) and
   `test_every_hashed_id_ends_in_16_hex_digits` (all 66 of the fixture's hashed ids, with the
   Product's, the 16 Components' that have a purl and the 3 Parties' checked against their keys:
   on 775a45c none had 16 digits). The two tests that craft a version and an advisory id spelling
   another object's id now spell its 16-digit id. The advisory test still meets the collision it
   was written for; the version test, a guard since the fifth round, meets none, since a
   Component's id ends in its own key's hash.

## What a human accepted

- @Clovier, 2026-11-25, after asking for each term to be explained: build #257 now, with the four
  provisional answers above ("yes i'm okay as they are, build 257"); for the match link, "pick the
  one the engine can draw"; use the alpine image RPT-0004's pilot scanned for the test files; and
  download a fresh Grype database.
- @Clovier, 2026-11-25: asked for these fixes ("do all those", after @kriishnaa-18's review of
  c39f2a4); the wording and code are Claude Code's draft until the pull request review accepts them.
- @Clovier, 2026-11-25: asked for these fixes ("fix 268", after @kriishnaa-18's re-review of
  9207ad9); the wording and code are Claude Code's draft until the pull request review accepts them.
- @Clovier, 2026-11-26: asked for these fixes ("review/fix what's outstanding", after
  @kriishnaa-18's and @Maimcghee's reviews of e12ab07); the wording and code are Claude Code's
  draft until the pull request review accepts them.
- @Clovier, 2026-11-26: asked for these fixes ("fix 268", after @kriishnaa-18's review of
  f21f4a5); the wording and code are Claude Code's draft until the pull request review accepts
  them.
- @Clovier, 2026-11-27: asked for these fixes ("fix 268", after @kriishnaa-18's re-review of
  4be86c1), and asked that everything be covered, so an independent review of the fixes, whose
  findings are items 4 to 18, was run before anything was pushed; the wording and code are
  Claude Code's draft until the pull request review accepts them.
- @Clovier, 2026-11-27: asked for review fixes to go in overnight ("continue working and fixing
  reviews until i wake up"), which covers the sixth round, after @kriishnaa-18's review of
  775a45c; the wording and code are Claude Code's draft until the pull request review accepts
  them.

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
- **R-ID-1's other identifiers:** the index digest, configuration digest and tags are not in Syft's
  CycloneDX output. Syft's own JSON has the configuration digest, and the index digest when the
  image is named by tag or by that digest; its tags were empty in every run (RPT-0004 Table 6a).
  The platform is not in the CycloneDX output either, which is why the key now takes it from
  `--platform` or from a scan of the image itself (decision 2); Syft's JSON records the os and
  architecture (not the variant), so reading it could make the option unneeded.
- **Platform spellings:** settled for arm64 in the third round (item 1): arm64 with no variant is
  v8, so `linux/arm64` and `linux/arm64/v8` give one id, the fixture's, which stays
  `...-linux-arm64-v8`. That is the one rule of the kind this import applies, so other spellings
  that might name one platform still give their own ids, and 32-bit arm with no variant is refused
  rather than given one. Writing every platform as containerd normalizes it is for #15 and #17,
  with the instance key.
- **A variant in the instance's purl:** the `oci` purl type has an `arch` qualifier and none for a
  variant, so the arm/v6 and arm/v7 builds of one index digest share the versioned purl in their
  ProductInstance's `identifiers`; the key, the id, the name and the description tell them apart
  (third round, item 1). A qualifier for it would be the purl specification's to add.
- **Other distributions' ARM names:** the variant table covers Alpine's, Debian's, Ubuntu's and
  RPM's 32-bit ARM names. Another distribution's name, such as Arch Linux ARM's `armv7h`, is listed
  as not checked, and Raspbian's `armhf` pins no variant; a row can be added for each, with its
  source.
- **`os.version`:** an image index can list two builds of one os and architecture that differ in
  `os.version`, as Windows images do; the key holds the os, the architecture and the variant only.
  The import has been checked on a Linux image only.
- **Packages for a foreign CPU:** kept since the fourth round (item 1), which settles this
  follow-up, and since the fifth (item 1) never refused: a warning says when more are built for
  one other platform than for the build's, or none for its architecture. The rule was checked on
  SBOMs made from the fixture; no real multiarch or emulator image has been imported here.
- **A second name left after a forced import that succeeds:** settled in the fifth round (item
  3). One that cannot be removed once both outputs are in place is named in a warning, and the
  command exits 0, where it used to end with an error (exit code 1) that did not name it.
- **Weakness names** from the pinned CWE catalog, instead of the id alone.
- **The model list's label:** `pv-` files show as "Proposal example (AI-drafted, unreviewed)"
  (`MODEL_KINDS` in `engine/engine/core.py`); an imported one is tool-made, not AI-drafted.
- **For the sponsor:** a `MAP-NNNN` for radar's data contract (DEC-002, ADR-0007), the instance key
  (R-ID-1), and the match predicate's name and confidence scale (R-MATCH-1) are provisional here.
- **The app's model report** (@kriishnaa-18's review, not blocking): it could set proposed
  vulnerability links apart from reviewed ones, and show a build's composition
  (`build_composed_of`). This change does not touch the app.
- **#243 also changes `engine/engine/cli.py`** (@kriishnaa-18's review, not blocking): check the
  `import-sbom` command when the two come together. The first round did not touch `cli.py`; the
  second adds `--platform` to `import-sbom` and prints a failed import's notes; the third and the
  fourth do not change it; the fifth prints an import's warnings and gives its exit codes.
  @Maimcghee's review of e12ab07 (a note, not blocking) adds that #243 adds its command in the
  same place, so whichever of the two merges second has a simple conflict to resolve by keeping
  both commands.
- **Party names for CWE sources** (@Maimcghee's review of e12ab07, a note, not blocking): the
  three CWE sources among the fixture's four Parties are named as the scan's database names them,
  and two of those names are raw identifiers: `134c704f-9b21-4f2e-91b3-4a467353bcc0`, an NVD
  source UUID (CISA's ADP, as above), and `disclosure@vulncheck.com`, an e-mail address (as is the
  third, `openssl-security@openssl.org`). Mapping NVD's source identifiers to organization names
  could follow. This change does not touch the app.
- **purl type rules:** apply each type's own rules (which names ignore case) once a purl-spec
  version is pinned (DL-0015), so purls that differ only in such a case join.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
