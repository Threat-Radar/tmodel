---
schema: "archdoc/v1"
id: DL-0068
title: "SBOM import: a starter model from Syft's CycloneDX SBOM of a container image and Grype's scan of it (#257)"
type: process
status: draft
version: "0.1.0"
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
  way Docker resolves it (`alpine` is `index.docker.io/library/alpine`).
- **ProductInstance:** the scanned build, keyed by the platform manifest digest Syft records in
  `metadata.component.version` (R-ID-1), with the versioned purl beside it. `build_composed_of`
  lists every Component (ADR-0011 A4). The SBOM never fills the design-level `composed_of`
  (R-EDGE-2).
- **Component:** one per SBOM entry other than a file (R-ID-4), keyed by its purl without qualifiers
  or subpath (R-ID-3), with `version`, `component_kind` from CycloneDX's `type` (A3), and every purl
  and CPE the entry carries in `identifiers`: the purl as Syft wrote it, its `cpe`, and the
  `syft:cpe23` candidates.
- **Supplier and manufacturer:** `supplied_by` and `manufactured_by` only from a `supplier` or
  `manufacturer` field. A publisher or package maintainer is not a supplier (Table 6c).
- **Dependencies:** each `dependsOn` as `uses_component`, from the dependent to the dependency
  (R-EDGE-1).
- **Vulnerability:** one per CVE a match names, its own id or one in `relatedVulnerabilities`. A match
  that names no CVE keeps the id Grype reports (GHSA, ALAS, GO and so on), unless another match in
  the scan pairs that id with exactly one CVE. A match's other id goes in `alias_ids` only when it
  names exactly one CVE; an advisory that names several is listed in the import report, not aliased.
  Ids that appear only inside a URL are never read. This is the rule @Clovier chose on 2026-11-24,
  now in #257's acceptance criteria.
- **The package match:** a proposed `propagates_to` Assertion from the Vulnerability to each
  Component a match puts it in, joined to the SBOM by purl, not by `bom-ref` (R-MATCH-1, R-MATCH-2).
  A match on a part that is not a Component of the SBOM is left out whole and listed in the report.
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

The import report gives each input's name, size and SHA-256, what was written, what was left out
with counts, and then every field at every level of both files with where it went. A field the
import does not know is listed as "not read by this import", so a field a newer Syft or Grype adds
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
   `latest` or a digest reference), and the message says to name the image by digest.
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
- **Entries with the same key are one Component.** Two SBOM entries whose purls differ only in
  qualifiers are one Component holding both purls, and the report lists them.
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
  not a regular file, and text that is not JSON.
- **Outputs:** the model is written to a temporary file and moved into place. An existing model or
  report is never replaced without `--force`, because people edit starter models, and an input is
  never written over. The model's header names the output only by its relative path, or by its name
  when the path is absolute, so no home folder lands in a committed file.

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
  and that the same files give the same bytes.
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

## What a human accepted

- @Clovier, 2026-11-25, after asking for each term to be explained: build #257 now, with the four
  provisional answers above ("yes i'm okay as they are, build 257"); for the match link, "pick the
  one the engine can draw"; use the alpine image RPT-0004's pilot scanned for the test files; and
  download a fresh Grype database.

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

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass.
