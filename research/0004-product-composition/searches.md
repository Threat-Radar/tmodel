---
schema: "archdoc/v1"
id: RPT-0004-searches
title: "RPT-0004 search log"
type: research
status: draft
version: "0.2.0"
date: "2026-09-28"
updated: "2026-10-08"
record: RPT-0004
---

# RPT-0004: search log

Every query run, so the survey is reproducible. One row per query.

| date | dimension | query | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-09-28 | 1 | CycloneDX Authoritative Guide SBOM HBOM guides cyclonedx.org | web (via Claude Code) | OWASP CycloneDX Authoritative Guide to SBOM; cyclonedx.org/guides |
| 2026-09-30 | 1 | iso_deliverables_metadata jsonl download url isopublicstorageprod | web (via Claude Code) | no direct download link for ISO Open Data found; iso.org pages sit behind a bot check |
| 2026-09-30 | 1 | ISO harmonized stage codes 90.60 "close of review" 90.93 confirmed 90.92 revised | web (via Claude Code) | ISO stage-code pages and PDFs (iso.org and ANSI copies refused with HTTP 403); ISO Guide 69 preview copy → sources.md |
| 2026-09-30 | 2 | CISA Hardware Bill of Materials HBOM Framework for Supply Chain Risk Management PDF | web (via Claude Code) | CISA announcement of the HBOM Framework (September 2023) → sources.md |
| 2026-09-30 | 4 | read-only code review of `tradar` by a research subagent (file and line citations), then spot-checked in the main session | Claude Code subagent | findings used in §4 only where re-checked (see Tool runs) |
| 2026-09-30 | 6 | official sources on OCI digests, the SPDX Build profile, CISA SBOM types, SLSA, in-toto and reproducible builds, gathered by a research subagent (its queries were not recorded) | Claude Code subagent | quotes re-checked in the main session → sources.md |
| 2026-09-30 | 5 | official sources on NVD CPE configurations and CWE sources, OSV, purl, Grype and Syft matching, Trivy data sources, gathered by a research subagent (its queries were not recorded) | Claude Code subagent | quotes re-checked live in the main session; the NVD documentation text in NVD's page bundle (see sources.md) |
| 2026-09-30 | 3 | official Dependency-Track and GUAC documentation, gathered by a research subagent (its queries were not recorded) | Claude Code subagent | quotes and issue states re-checked live in the main session → sources.md |
| 2026-09-30 | 2 | CycloneDX HBOM hardware bill of materials capability guide | web (via Claude Code) | the HBOM Framework PDF on cisa.gov; cyclonedx.org → cyclonedx.org/capabilities/hbom/ → sources.md |

## Tool runs

| date | command | input | result |
|---|---|---|---|
| 2026-09-28 | `syft alpine:latest -o cyclonedx-json` (Syft 1.52.0) | alpine:latest | CycloneDX 1.7; 16 packages, 78 files, 1 OS; no package hashes, no `compositions`, no `vulnerabilities` |
| 2026-09-28 | `trivy sbom alpine.cdx.json` (Trivy 0.74.0) | Syft SBOM above | 0 CVEs; warns "Third-party SBOM may lead to inaccurate vulnerability detection" |
| 2026-09-28 | `grype alpine.cdx.json` (Grype 0.119.0) | Syft SBOM above | 4 matches = 2 distinct CVEs (busybox CVE counted 3x via origin package); 0 fixed |
| 2026-09-28 | `grype alpine.cdx.json -o json`| Syft SBOM above | all 4 matches are `cpe-match` against `nvd:cpe`; `cwes` present: CWE-787 (zlib), CWE-284 (busybox) | 
| 2026-09-28 | `grype alpine.cdx.json -o cyclonedx-json` | Syft SBOM above | same 4 matches; `cwes` field empty |
| 2026-09-30 | `jq '.definitions.component.required' bom-1.7.schema.json` | CycloneDX 1.7 JSON schema (see sources.md) | `["type","name"]`: the only required component fields (§1.1 Naming) |
| 2026-09-30 | `jq '.definitions.componentIdentityEvidence.properties.field.enum' bom-1.7.schema.json` | same | `group`, `name`, `version`, `purl`, `cpe`, `omniborId`, `swhid`, `swid`, `hash`: the spec's identity fields (§1.1 Naming) |
| 2026-09-30 | `jq '[paths \| map(tostring) \| join(".") \| select(test("cwe";"i"))]' bom-1.7.schema.json` | same | every match is under `definitions.cwe` or `vulnerability.cwes`: no other place for a CWE (§1.1 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.dependency.properties.dependsOn.items, .definitions.vulnerability.properties.affects.items.properties.ref.anyOf' bom-1.7.schema.json` | same | `dependsOn` accepts only `refLinkType` (same file); `affects.ref` also accepts `bomLinkElementType` (BOM-Link) (§1.1 Dependencies, Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.vulnerability.properties.analysis \| {required, allOf, if}' bom-1.7.schema.json` | same | all `null`: no rule requires a `justification` for `not_affected` (§1.1 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.scoreMethod.enum' bom-1.7.schema.json` | same | CVSSv2, CVSSv3, CVSSv31, CVSSv4, OWASP, SSVC, other (§1.2 Vulnerabilities) |
| 2026-09-30 | `jq '[paths(type == "string" and test("EPSS\|Known Exploited\|exploit catalog";"i"))]' bom-1.7.schema.json` | same | `[]`: no EPSS or exploit-catalog field (§1.2 Vulnerabilities) |
| 2026-09-30 | `shasum -a 256` | CISA Framing (3rd ed.) PDF, from the record's Source URL | `3a204b5f...cb3397`, same as the `cisa-framing-software-component-transparency` digest; the §2.2.2.5 "discontinued in 2030" sentence is on p. 14 (§1.1 Naming) |
| 2026-09-30 | `grep -o 'Core/RelationshipType/[A-Za-z]*>' spdx-model.ttl \| sort -u \| wc -l` | SPDX 3.0.1 model file (see sources.md) | 59 relationship types (§1.2 Dependencies) |
| 2026-09-30 | `grep -o 'Core/ProfileIdentifierType/[A-Za-z]*>' spdx-model.ttl \| sort -u` | same | 10 profiles: ai, build, core, dataset, expandedLicensing, extension, lite, security, simpleLicensing, software; none for hardware (§1.2 Hardware) |
| 2026-09-30 | `grep -i -c -E 'serialnumber\|macaddress\|manufacturer' spdx-model.ttl` | same | `0`: no serial number, MAC address or manufacturer term (§1.2 Hardware) |
| 2026-09-30 | `grep -o 'Core/HashAlgorithm/[A-Za-z0-9_]*>' spdx-model.ttl \| sort -u \| wc -l` | same | 22 hash algorithm values (§1.2 Naming) |
| 2026-09-30 | `grep -n -i cwe spdx-model.ttl` | same | 4 lines, all about `ExternalRefType/cwe`: CWEs are supported only as an external-reference type, with no dedicated field (§1.2 Vulnerabilities) |
| 2026-09-30 | `jq '.definitions.externalReference.properties.url.anyOf, .definitions.externalReference.properties.type."meta:enum".bom' bom-1.7.schema.json` | CycloneDX 1.7 JSON schema | an external reference's `url` may be an IRI or a BOM-Link, and type `bom` is "Bill of Materials (SBOM, OBOM, HBOM, SaaSBOM, etc)": SBOMs can be linked without a dependency (§1.1 Dependencies) |
| 2026-09-30 | `grep -o 'terms/Extension/[A-Za-z]*' spdx-model.ttl \| sort -u` | SPDX 3.0.1 model file | the Extension profile includes `CdxPropertiesExtension` (name/value pairs "intended to be compatible with" CycloneDX properties, per its spec page) (§1.2 Hardware) |
| 2026-09-30 | `grep -n -i -E 'composition\|aggregate'` on the extracted PDF text | CISA Framing (3rd ed.) PDF | no mapping of completeness to CycloneDX `compositions`/`aggregate`: the completeness tables in §1.1 and §1.2 are our alignment |
| 2026-09-30 | `for w in hardware firmware CPE purl; do grep -c -i "$w" rfc9393.txt; done` | RFC 9393 (rfc-editor.org/rfc/rfc9393.txt) | `0` for each word (§1.3 Naming, Hardware) |
| 2026-09-30 | `grep -c -i -E 'cve\|cwe\|vex\|vulnerab'` on RFC 9393 §2.10 (the full CDDL) | same | `0`: no vulnerability fields in CoSWID's data definition (§1.3 Vulnerabilities) |
| 2026-09-30 | `grep -n -i hardware` on the extracted PDF text | NIST IR 8060 PDF (nvlpubs.nist.gov), sha256 `9aff60d8...a6de8` | 2 lines, both in §5.2.3's definition of executable files (§1.3 Hardware) |
| 2026-09-30 | `curl` of iso.org/standard/65666.html | ISO/IEC 19770-2:2015 page | blocked by a bot check; the standard's current edition status could not be confirmed (§1.3) |
| 2026-09-30 | `grep -c -i` for `exploitable`, `in_triage`, `SPDX` on the extracted text | CISA "Minimum Requirements for VEX" PDF (cisa.gov; direct `curl` got HTTP 403, fetched through Claude Code's web fetch), sha256 `1e73325c...975c8` | `0`, `0`, `0`: CycloneDX appears only as a VEX-capable format; no CycloneDX or SPDX values are mapped. Defines 4 statuses and 5 justifications (§2.7.1) |
| 2026-09-30 | `jq '.definitions.metadata.properties \| keys'` and the same for `license` and `componentEvidence` | CycloneDX 1.7 JSON schema | `authors`, `timestamp`, `lifecycles`, `component`, `supplier`; license `acknowledgement` (declared, concluded) and `licensing`; evidence `licenses`, `copyright`: every CycloneDX 1.6 field in CISA's Table 1 still exists in 1.7 (comparison table) |
| 2026-09-30 | Properties tables of the CreationInfo, Sbom and Package pages | SPDX 3.0.1 spec site | `created`, `createdBy`; `sbomType`; `name`, `packageVersion`, `suppliedBy`, `verifiedUsing`, `copyrightText`, `packageUrl`: every SPDX 3.0 field in CISA's Table 1 still exists in 3.0.1 (comparison table) |
| 2026-09-30 | `sed` of `software-meta-entry` in §2.8, plus `grep -c -i` for `licens`, `copyright`, `timestamp` | RFC 9393 | no license, copyright or creation-time field; `licens` hits are the `licensor` role and license keys, `timestamp` only concerns signatures (comparison table, SWID column) |
| 2026-09-30 | the "corresponds to" / "represents" sentence on each VEX class page | SPDX 3.0.1 spec site | Affected and NotAffected "correspond to", Fixed and UnderInvestigation "represent", the VEX `affected`, `not_affected`, `fixed` and `under_investigation` statuses (comparison table) |
| 2026-09-30 | `python3` parse of each "Equivalent CycloneDX field" and "Equivalent SPDX field" in Appendix C.1 to C.7 | CISA HBOM Framework PDF (fetched through Claude Code's web fetch), sha256 `cba6ce12...025806` | 47 fields; 37 with no CycloneDX equivalent, 36 with no SPDX equivalent (§2) |
| 2026-09-30 | `jq` on `organizationalEntity` and `postalAddress`, plus a search of every schema string for "coordinat", "lead time", "technology node", "country of origin" | CycloneDX 1.7 JSON schema | organizations have an `address` (`country`, `region`, `locality` and more); the four terms: 0 hits (§2) |
| 2026-09-30 | `grep -c -i -E 'terms/Core/(address\|location\|country)' spdx-model.ttl` | SPDX 3.0.1 model file | `0`: no address field (§2) |
| 2026-09-30 | `curl` with a browser user agent | iso.org/open-data.html | blocked by a bot check (§1.3) |
| 2026-09-30 | `python3` `csv` filter for rows whose `reference` contains "19770" | ISO Open Data `iso_deliverables_metadata.csv` (downloaded by Ty), sha256 `4bd58c01...603662` | ISO/IEC 19770-2:2015: edition 2, published 2015-09-30, stage 9060, replaces the 2009 edition, `replacedBy` empty; ISO/IEC 19770-6:2024 *Hardware identification tag*: published 2024-01-26, stage 6060 (§1.3, §2) |
| 2026-09-30 | `python3` `csv` search of `reference` and `title.en` for SPDX, CycloneDX, purl, SWHID, OpenChain and supply-chain terms | ISO Open Data `iso_deliverables_metadata.csv` | ISO/IEC 5962:2021 (SPDX 2.2.1), stage 9092, `replacedBy` ISO/IEC DIS 5962 "SPDX® Specification V3.0" (stage 4060); ISO/IEC CD 27055 "CycloneDX Bill of Materials (BOM) specification" (3099); ISO/IEC CD 27056 "Package-URL (PURL) specification" (3099); ISO/IEC 18670:2025 SWHID V1.2 (6060); also ISO/IEC 27036-3:2023 and 18974:2023 (§1, §7) |
| 2026-09-30 | `grep` for "xx.92", "xx.99" in the text | ISO Guide 69:1999 preview | "xx.92 Decision to redefine project", "xx.99 Decision to register for next applicable phase" (§1) |
| 2026-09-30 | `grep` for "milestone" and "xx.60" in the text | ISO Guide 69:1999 preview (cdn.standards.iteh.ai) | "The stage xx.60 is the end of a main action" (§4.11), and phase 90 is the review stage (§4.16): 90.60 marks the close of a review (§1.3) |
| 2026-09-30 | `syft dir:<tradar> -o cyclonedx-json` and `-o spdx-json` (Syft 1.52.0) | tradar repository at `26d9c76` | CycloneDX 1.7: 76 packages (65 from `uv.lock`, 2 from `docker/requirements-docker.txt`, 9 GitHub Actions), 6 files, 104 dependency edges; every package has a purl and a CPE, none a hash, license or supplier; 920 more candidate CPEs as `syft:cpe23` properties; `metadata.component` is type `file`, named after the local path, no version; no `lifecycles`, no `formulation`. SPDX output is `SPDX-2.3` with 996 `cpe23Type` references (76 + 920) and 104 `DEPENDENCY_OF` (§3, §6) |
| 2026-09-30 | `syft scan --help` | Syft 1.52.0 | output formats: CycloneDX JSON/XML, SPDX 2.3 and 2.2 (JSON, tag-value), Syft JSON and others; no SPDX 3 (§3) |
| 2026-09-30 | `grype sbom:tradar.cdx.json -o json` (Grype 0.119.0, DB schema v6.1.9 built 2026-09-30) | Syft SBOM of tradar | 15 matches, 14 advisories, all `GHSA-` IDs; matchers: `python-matcher` 13, `stock-matcher` 2 (GitHub Actions); all `exact-direct-match`; all 15 carry CWEs; all fixed (§3, §5) |
| 2026-09-30 | `trivy fs --scanners vuln` and `trivy sbom` (Trivy 0.74.0) | tradar directory; Syft SBOM of tradar | `fs`: 12 CVEs, all from `uv.lock`; `sbom`: 13 CVEs; all with `CweIDs`; data source `ghsa`. Grype's CVE aliases cover all of Trivy's; only Grype reports `CVE-2026-47751` (GitHub Action `anthropics/claude-code-action@v1`, in two workflow files, so 15 matches for 14 advisories), and `trivy fs` also misses `CVE-2026-28684` (`python-dotenv@1.0.0` in `docker/requirements-docker.txt`), which `trivy sbom` finds (§3) |
| 2026-09-30 | `grep -rn -i cwe`, key searches for `"dependencies"`, `"compositions"`, `"serialNumber"`, `"hashes"`, `"supplier"`, and `git log --diff-filter=AD -- threat_radar/core/nvd_client.py` | tradar repository | 0 CWE hits; none of the five keys read outside environment config; NVD client added `629d92a` (2025-10-05), deleted `3e26837` (2025-10-09) (§4) |
| 2026-09-30 | `curl` and `grep` of the quoted sentences | SLSA v1.2 Build Provenance, OCI Distribution Spec v1.1.1, in-toto Statement v1 (tag `v1.2.0`), reproducible-builds.org definition, SPDX Build class page | all quotes in §6 found verbatim; `Build` requires only `buildType` (§6) |
| 2026-09-30 | `jq` of `matchDetails` in `alpine.grype.json` | Grype output from 2026-09-28 (Grype 0.119.0, DB built 2026-09-28) | all 4 matches: matcher `apk-matcher`, type `cpe-match`, namespace `nvd:cpe`, empty fix state; busybox, busybox-binsh and ssl_client all searched as `busybox`; CWEs carry source and type `Secondary` (§3, §5) |
| 2026-09-30 | `grype config` | Grype 0.119.0 defaults | `using-cpes: false` for java, dotnet, golang, javascript, python, ruby, rust, hex, dpkg, rpm; `true` for jvm and stock (§5) |
| 2026-09-30 | NVD API `cves/2.0?cveId=` for three CVEs, then `python3` over `weaknesses` and `configurations` | services.nvd.nist.gov | CVE-2022-37434: NVD Primary CWE-787, second source Secondary CWE-120, zlib criterion with `versionEndIncluding` 1.2.12. CVE-2025-60876: Secondary CWE-284 only, 1 configuration. CVE-2026-85091: "Awaiting Analysis", Secondary CWE-787 only, 0 configurations (§5) |
| 2026-09-30 | `curl` of the weakness list, then `python3` search | nvd.nist.gov/public/service/rest/json/nvd/vulns/weakness | definitions of `NVD-CWE-noinfo` and `NVD-CWE-Other` (§5) |
| 2026-09-30 | `curl` of `v3.24/main.json`, then `python3` search of `secfixes` | Alpine secdb | busybox and zlib have entries; neither lists CVE-2025-60876 or CVE-2026-85091 (§5) |
| 2026-09-30 | `curl` and `grep` of the quoted sentences | Grype docs and `apk/matcher.go`, Syft `cpegenerate` README, Trivy docs, OSV schema, purl README, Dependency-Track docs, README and changelog, GUAC README and docs; GitHub API for pull request #1412, issues #1746 and #1850 and latest releases | all quotes in §3 and §5 found verbatim; #1746 open ("on hold"), #1850 open ("long-term"); latest releases Dependency-Track 5.1.1 (2026-09-20), GUAC v1.1.0 (2026-03-13) (§3, §5) |
| 2026-09-30 | `gh api search/code` for "cpe" in `aquasecurity/trivy` `docs/` | Trivy repository | only `docs/guide/coverage/os/rhel.md` (and an image): no Trivy doc describes NVD CPE matching (§5) |
| 2026-09-30 | independent fact-check of §4 to §7 by a Claude Code subagent, then each finding re-verified in the main session (tradar code, Grype `source` block, NVD page bundle `main-QN4PLKKZ.js`) | report.md | 2 errors and 8 overstatements found and fixed (fix-version nodes, purl display, CVSS rule, `manifestDigest`, SPDX `cwe` references, match sources, serial numbers, SPDX Build requirements, library summaries), plus one in §3 (version ranges) |
| 2026-09-30 | independent fact-check of the comparison table, §2 and §3 by a Claude Code subagent, then each finding re-verified in the main session | report.md | 4 errors and 6 overstatements found and fixed (CISA's purl entry, SWID evidence date and license links, relationship counts and CycloneDX `pedigree`, SWID link types and IANA relations, CycloneDX's VEX examples, HBOM field overlaps, tradar SPDX suppliers, Alpine CPE counts, `trivy sbom` versus `trivy fs`); the same points were aligned in 1.1, 1.3 and §7 |
| 2026-09-30 | `jq` of `analysis.state` in each file | CycloneDX bom-examples `VEX/CISA-Use-Cases/Case-1` | `vex-affected.json`: `exploitable`; `vex-fixed.json`: `resolved`; `vex-not_affected.json`: `not_affected`; `vex-under_investigation.json`: `in_triage` (comparison table) |
| 2026-09-30 | `syft dir:<tradar> -o syft-json`, then count `cpes[].source` | tradar repository | 996 CPEs: 10 `nvd-cpe-dictionary`, 986 `syft-generated` (§3) |
| 2026-09-30 | `jq` of `cpe` fields and `syft:cpe23` properties | `alpine.cdx.json` | 16 standard `cpe` values plus 65 properties = 81 candidates (§3) |
| 2026-09-30 | `jq` of `packages[].supplier` | Syft SPDX output of tradar | suppliers for the 9 GitHub Actions: "Organization: GitHub" (6), "Organization: anthropics" (2), "Organization: softprops" (1) (§3) |
| 2026-09-30 | `grep` for "@date", "applicable licenses", `rel="license"`, "Link Relation Types" | NIST IR 8060 text; RFC 9393 | Evidence `@date` (§3.1.3); Link used for "documents containing applicable licenses" with a `rel="license"` example; `rel` may be an IANA "Link Relation Types" name (RFC 9393 §2.7) (comparison table, §1.3) |
| 2026-10-01 | `git show origin/main:spec/ADR-0001-radar-model-split.md` and `origin/main:project/DECISIONS-0001.md` | tmodel `main` | DEC-007 accepted in ADR-0001 (2026-09-30): tradar becomes "radar", tmodel consumes its output, and "the interface is the composition→model-input mapping surveyed in RPT-0004 (#8)"; DEC-001, DEC-002 and DEC-008 still open (front matter, §3, §4, §7) |
| 2026-09-30 | `gh issue view 12` | tmodel issue #12 | "Agentic Threats & Weaknesses"; no mention of bills of materials, so no overlap claimed (§7) |
| 2026-09-30 | `curl` of the page, then word counts | cyclonedx.org/capabilities/vex/ (the CycloneDX page CISA cites) | `under_investigation`, `in_triage`, `not_affected`, `fixed`, `CISA`, `justification`: all `0`: no mapping to CISA's statuses |

## Second pass, Phase 1 (2026-10-08)

Queries from the five fan-out agents (section 7 of each `fanout-*.md`), with the agent's number added. Each agent's notes keep the full detail: what each hit was, its hash and its locator. Agent numbers: 1 formats, baselines and other bill types; 2 identifiers and build identity; 3 the bridge to CVEs and CWEs; 4 hardware and firmware; 5 tools and radar. "2 (re-check)" is the second agent that finished agent 2's notes (fanout-identity.md §9 and §10).

| agent | date | dimension | query | engine | notable hits |
|---|---|---|---|---|---|
| 1 | 2026-10-08 | 1, 8, 9 | which RPT-0004 v0.1.0, RPT-0005, RPT-0014 sections, ARCH-0001 §3, proposal, LinkML draft and library records cover formats and baselines | local repository read | v0.1.0 §1; RPT-0005 `fanout-attack-composition.md` §1.6, §1.7 and `fanout-vuln-data.md` rejected-claims row on "1.7.2"; RPT-0014 S-0705, S-0827, S-0840, S-0847; records `cyclonedx-1-7`, `spdx-3-0-1`, `cisa-2026-sbom-minimum`, `eu-cra-2024-2847`, `fda-premarket-cybersecurity-guidance`, `omb-m-26-05` |
| 1 | 2026-10-08 | 1 | `gh api repos/CycloneDX/specification/{releases,tags,milestones,branches}`; release notes 1.7, 1.7.1, 1.7.2; PR #652, #680; milestone 10 | gh | 1.7.1 2026-06-02, 1.7.2 2026-09-17; 2.0 milestone overdue; no 1.8; "1.6-ECMA" milestone |
| 1 | 2026-10-08 | 1 | CycloneDX schemas at tags 1.6, 1.6.1, 1.6.2, 1.7, 1.7.1, 1.7.2, master; XSD, proto, spdx, jsf, cryptography-defs at 1.7.2; 2.0-dev schema files | curl + jq + python3 | diffs (section 2, Q8); keyword counts |
| 1 | 2026-10-08 | 1 | ECMA-424 2nd edition PDF; Ecma ECMA-424 and TC54 pages; tc54.org; `Ecma-TC54/ECMA-424` repository | curl + gh | conformance clause; "ISO/IEC number DIS 27055"; no third edition |
| 1 | 2026-10-08 | 1 | `gh api repos/spdx/spdx-spec` and `spdx/spdx-3-model` releases, tags, milestones, branches, commits; issues #522, #923, #1046, #1051, #1134, #1158; PRs #1197, #1300; issue comment 3471615629 | gh | 3.1-RC1 only; milestones overdue; pyshacl removed from example checks |
| 1 | 2026-10-08 | 1 | `spdx.org/rdf/3.0.1/` model, context; `spdx.org/schema/3.0.1/` schema; files at tag 3.0.1; tarballs of both repositories at 3.0.1 | curl | served model differs from tagged model |
| 1 | 2026-10-08 | 1 | `spdx/spdx-examples` tree; 8 SPDX 3 examples at commit `08a3552c` | gh + curl | 9 test documents with the spec example |
| 1 | 2026-10-08 | 1 | SPDX diffs annex (site redirect to `spdx/using`); 2.3 relationships chapter at `v2.3`; 2.3 JSON schema | curl + gh | 2.3 to 3.0 changes; `DYNAMIC_LINK` row |
| 1 | 2026-10-08 | 1 | SPDX 3.1-RC1 `serializations.md`, model, context; `spdx.org/rdf/3.1/spdx-context.jsonld` | curl | "strict subset of JSON-LD"; 3.1 namespace |
| 1 | 2026-10-08 | 1 | PyPI JSON for `spdx3-validate` | curl | 0.0.7 (2026-08-10) |
| 1 | 2026-10-08 | 1 | ISO Open Data CSV and JSONL (blob storage URL); `iso.org/stage-codes.html` (403); `committee.iso.org/stage-codes.html` | curl + python3 | DIS 5962 at 40.99; DIS 27055 and 27056 at 40.00 |
| 1 | 2026-10-08 | 1 | ISO Guide 69 harmonized stage codes "40.99" "40.00" DIS registered pdf | WebSearch | iso.org Guide 69 pages (blocked); used `committee.iso.org/stage-codes.html` instead |
| 1 | 2026-10-08 | 1 | cdn.standards.iteh.ai ISO Guide 69 1999 harmonized stage code sample pdf | WebSearch | no preview link found |
| 1 | 2026-10-08 | 1 | `standards.iso.org/iso/19770/-2/` portal, `2015/schema.xsd`, `2015-current/schema.xsd` | curl | free SWID XSD |
| 1 | 2026-10-08 | 1 | RFC 9393 text, JSON metadata, errata page; NIST IR 8060 PDF and CSRC page | curl | no errata; IR 8060 April 2016 |
| 1 | 2026-10-08 | 8 | CISA "2026 Minimum Elements for a Software Bill of Materials" | WebSearch | news items, IC3 PDF link |
| 1 | 2026-10-08 | 8 | CISA 2026 landing page (curl 403; WebFetch summary) and PDF link (403); IC3 copy | curl + WebFetch | publication date confirmed in the PDF |
| 1 | 2026-10-08 | 8 | CISA framing 2024 PDF (403); Internet Archive copy; NTIA 2021 PDF | curl | same hashes as the library records |
| 1 | 2026-10-08 | 8 | BSI TR-03183-2 Software Bill of Materials version 2.1 2.2 2026 pdf | WebSearch | BSI download, mirrors |
| 1 | 2026-10-08 | 8 | BSI TR-03183 English and German landing pages; PDFs v2.0.0, v2.1.0 and the file named v2_2_0 | curl + python3 | 2.1.0 current; mislabelled 1.1 file |
| 1 | 2026-10-08 | 8 | EUR-Lex CRA HTML (`OJ:L_202402847`) | curl + python3 | SBOM passages |
| 1 | 2026-10-08 | 8 | Cyber Resilience Act implementing act Article 13(24) software bill of materials format elements Commission 2026 | WebSearch | no implementing act; a snippet misattributing the SBOM duty to Article 16 (rejected) |
| 1 | 2026-10-08 | 8 | CRA standardisation request M/606 vulnerability handling prEN 40000-1-3 SBOM CEN CENELEC JTC 13 | WebSearch | DIN draft page, ibf article |
| 1 | 2026-10-08 | 8 | "have your say" Cyber Resilience Act implementing regulation "software bill of materials" format draft | WebSearch | nothing relevant |
| 1 | 2026-10-08 | 8 | Commission CRA pages (policy, standardisation, implementation (404)), guidance announcement and C(2026) 5252 PDFs; DIN prEN 40000-1-3 page; STAN4CR pages | curl + python3 | guidance has no SBOM text; prEN 40000-1-3 draft 2026-09 |
| 1 | 2026-10-08 | 8 | FDA "Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions" 2026 guidance SBOM | WebSearch | 2026-02-03 final; blog claims (partly rejected) |
| 1 | 2026-10-08 | 8 | FDA guidance PDF (`/media/119933/download`); OMB M-26-05 PDF; CERT-In v2.0 PDF; IANA hash function text names CSV | curl | hashes match library and RPT-0014 |
| 1 | 2026-10-08 | 8, 9 | G7 "Software Bill of Materials for AI" "Minimum Elements" CISA May 2026 | WebSearch | CISA bulletin, law-firm summaries |
| 1 | 2026-10-08 | 8, 9 | CISA bulletin 416bd74; cisa.gov G7 page via the Internet Archive (403) | curl | G7 guidance exists, not read |
| 1 | 2026-10-08 | 9 | CycloneDX capability pages (sbom, saasbom, cbom, hbom, mlbom, obom, mbom) | curl | page texts |
| 1 | 2026-10-08 | 9 | Linux Foundation AI-BOM landing page and PDF (S-0840) | curl + pdftotext | Table 8 vs model |
| 2 | 2026-10-08 | 6, 7 | read scope and draft model: dimensions.md, report.md 0.1.0, searches.md, sources.md, RPT-0005 fan-out example, ARCH-0001 §3, proposal `0.2.0-proposed.11`, LinkML 0.1.0, OBJECT-MODEL.md, ADR-0001, ADR-0004, RPT-0015 §3 and §4 | local repository read | no identity slots in the draft; "identity-by-hash" and "CPE/purl" only in prose |
| 2 | 2026-10-08 | 6, 7 | library records: `slsa-1-2` (distilled files), `in-toto-attestation-v1`, `in-toto-envelope-v1`, `cyclonedx-1-7`, `spdx-3-0-1`, `iso-24089-2023`, `guac`, `osv-schema`, `secure-systems-lab-dsse`; `find` for purl, CPE, SWID, OmniBOR, SWHID, OCI, R156 records | local library read | no records for purl, CPE, RFC 9393, OmniBOR, SWHID, OCI, Sigstore bundle, R156 |
| 2 | 2026-10-08 | 7 | ECMA-427 Package-URL purl specification edition | WebSearch | ECMA-427 page and 1st edition PDF |
| 2 | 2026-10-08 | 7 | `gh api repos/package-url/purl-spec/releases`, tree at `v1.1.0`, PRs #1011 and #1012, issue #741, search "canonical in:title" | gh | v1.1.0 (2026-10-07) = 2nd edition text; "canonical" removed from Clause 5; #741 open |
| 2 | 2026-10-08 | 7 | `gh api repos/package-url/vers-spec/releases` and tree at `v1.2.1` | gh | vers approved for GA submission Dec 2026; 2 vers types |
| 2 | 2026-10-08 | 7 | ISO Open Data CSV filtered for 27056, 18670, 24089, 19770-2, 19770-6, 27055, 5962, 20153 | curl + python3 | DIS 27056 at 40.00; 18670:2025 published 2025-04-23 |
| 2 | 2026-10-08 | 7 | ISO harmonized stage codes "40.00" "DIS registered" "40.99" | WebSearch | iso.org PDF (403 to curl); certifico.com copy used |
| 2 | 2026-10-08 | 7 | NIST IR 7695, 7696, 7697 PDFs and CSRC status pages | curl + pdftotext | Final, August 2011; no supersession text |
| 2 | 2026-10-08 | 7 | NVD news page; `cve_affected_1.0.json` | curl + python3 | XML dictionary removed 2025-08-20; enrichment prioritized 2026-04-15; CNA `affected` with `packageURL` since 2026-06-17 |
| 2 | 2026-10-08 | 7 | NVD CPE API: zlib 1.3.1; 16 pilot CPEs as vendor:product and as full names (32 queries); CPE Match API for CVE-2022-37434 | curl + jq (NVD API 2.0) | 3 of 16 vendor:product pairs exist; 0 of 16 full names; 29 match strings |
| 2 | 2026-10-08 | 7 | RFC 9393 text; `grep` for purl, cpe, gitoid, swhid, omnibor | curl | 0 hits each; tag-id, hash-entry, §9 collision text |
| 2 | 2026-10-08 | 7 | `gh api repos/omnibor/spec` releases, tags, commits for `spec/SPEC.md`; SPEC.md at main and v0.1; `GITOID_URI.txt`; IANA `prov/gitoid` | gh + curl | v0.2 draft: SHA-256 only, CRLF normalization (2025-07-28) |
| 2 | 2026-10-08 | 7 | swhid.org specification v1.2 clauses 0, 1, 4, 5, 6; `gh api repos/swhid/specification` issues and commits | curl + gh | issues #70 (open), #72; '40000' restored 2026-09-19 |
| 2 | 2026-10-08 | 7 | CycloneDX schema 1.7.2 (`jq` on identity and hash definitions); CycloneDX and SPDX issue search "hash in:title" | curl + jq + gh | issue #96 open since 2021 |
| 2 | 2026-10-08 | 7 | SPDX 3.0.1 model TTL and class pages (Hash, PackageVerificationCode, ContentIdentifier, ExternalIdentifier, Build) | curl + python3 | `Hash` leaves bytes open; PVC discouraged |
| 2 | 2026-10-08 | 6, 7 | OCI image-spec and distribution-spec releases and tags; files at v1.1.1; tree at v1.1.0-rc2 to v1.1.1 for `artifact.md`; PR search "artifact manifest remove" | gh + curl | PR #999 removed the artifact manifest (2023-04-13) |
| 2 | 2026-10-08 | 6 | in-toto attestation releases; spec files at v1.2.0 | gh + curl | v1.2.0 (2026-03-18); SPDX 3 predicate added |
| 2 | 2026-10-08 | 6 | BuildKit latest release and `docs/attestations/*` at v0.34.0 | gh + curl | index-attached storage; OCI-artifact mode adds `subject` |
| 2 | 2026-10-08 | 6 | cosign latest release; `doc/cosign_attest.md`, `specs/*`, `attestation.go`; in-toto-golang v0.11.0 constants; v3.0.x release notes | gh + curl | predicate type mapping; v3 stores OCI 1.1 referring artifacts |
| 2 | 2026-10-08 | 6 | Sigstore protobuf-specs tags; `sigstore_bundle.proto` at v0.5.2 | gh + curl | bundle v0.3; one signature |
| 2 | 2026-10-08 | 6 | `actions/attest-sbom` and `actions/attest` releases and READMEs | gh + curl | digest-bound; GitHub attestations API by default |
| 2 | 2026-10-08 | 6, 7 | Docker Hub registry: tags `latest`, `3.24.2`, `3.24`, `3`; index; arm64 manifest and config; attestation manifest and both blobs; referrers API for manifest and index digests; fallback and cosign tags | curl (registry API v2) | five digests; SPDX 2.3 by Docker Scout; SLSA v0.2; empty referrers |
| 2 | 2026-10-08 | 7 | `jq` over pilot `alpine.cdx.json`, `alpine.syft.json`, `alpine.spdx23.json`, `alpine.grype.json` | jq | identifier counts; image digest levels; `imageID` = `bom-ref` |
| 2 | 2026-10-08 | 7 | `gh api search/code` in anchore/syft for `ManifestDigest` and `TagID`; files at v1.52.0 | gh + curl | decoder maps `bom-ref` to image `ID`; `TagID: distro.ID` |
| 2 | 2026-10-08 | 7 | OSV schema v1.9.1; OSV.dev query API doc; `go/purl` at `16b340c78a51`; 17 queries to `api.osv.dev/v1/query` | curl + gh + jq | apk purls 0 results; Debian purl depends on `distro` spelling |
| 2 | 2026-10-08 | 7 | GitHub REST API OpenAPI description (`/advisories` parameters, `global-advisory` schema); advisory file search `GHSA-cpwx-vrp4-4pq7` | gh + curl + python3 | ecosystem and name only; no purl or CPE |
| 2 | 2026-10-08 | 7 | deps.dev API v3 and v3alpha pages | curl + python3 | hash query (6 ecosystems); purl lookup without qualifiers; OCI chain ids |
| 2 | 2026-10-08 | 7 | GUAC latest release; schema files at v1.1.0 | gh + curl | qualifiers split package nodes; evidence nodes |
| 2 | 2026-10-08 | 7 | Dependency-Track component identity purl cpe swidTagId hashes internal analyzer documentation | WebSearch | docs.dependencytrack.org component-identity page (then fetched) |
| 2 | 2026-10-08 | 7 | `gh api search/code` for omnibor, gitoid, swhid in guacsec/guac, DependencyTrack/dependency-track, DependencyTrack/hyades-apiserver, google/osv.dev, google/deps.dev | gh | 0 hits except DT's vendored CycloneDX proto; google/deps.dev is not the service code |
| 2 | 2026-10-08 | 7 | empirical study SBOM generation tools inconsistent package identifiers purl CPE disagreement paper 2024 2025 | WebSearch | arXiv 2510.05798 (SBOMproof), 2601.05622, 2609.19920, 2606.02442; abstracts fetched, SBOMproof §4 read |
| 2 | 2026-10-08 | 6 | unece.org UN Regulation No. 156 software update management system R156e.pdf RXSWIN | WebSearch | no unece.org PDF in results; EU Publications Office entry |
| 2 | 2026-10-08 | 6 | "UN Regulation No. 156" supplement amendment ECE/TRANS/WP.29 RXSWIN | WebSearch | no supplement found; left open |
| 2 | 2026-10-08 | 6 | unece.org R156 PDF and documents page; op.europa.eu entry; EUR-Lex CELEX 42021X0388; UN ODS symbol ECE/TRANS/WP.29/2020/80 | curl | unece.org 403 (Cloudflare); OJ and UN ODS texts fetched |
| 2 | 2026-10-08 | 6 | datatracker API for draft-ietf-suit-manifest; draft text rev 37 | curl | RFC Editor queue; image digest, size, sequence number |
| 2 | 2026-10-08 | 6 | slsa.dev/spec/ (current version) | curl | "Version 1.2", "Approved" |
| 2 | 2026-10-08 | 6 | tradar `26d9c76`: `core/grype_integration.py`, `cli/cve.py` | gh | `scan_metadata` keeps Grype `source` and `descriptor` |
| 2 | 2026-10-08 | 7 | IANA URI schemes CSV; `prov/pkg`, `prov/gitoid` | curl | pkg, gitoid, swh, swid, swidpath all Provisional |
| 3 | 2026-10-08 | 5 | NVD National Vulnerability Database enrichment change 2026 announcement | WebSearch (standard) | secondary reports of the 2026-04-15 change (Infosecurity Magazine, CSA research note, Black Duck, Strobes); no primary NVD page; used the NVD web bundle instead (1.2) |
| 3 | 2026-10-08 | 5 | NVD "Not Scheduled" enrichment KEV "critical software" site:nist.gov | WebSearch (standard) | secondary only (SecurityWeek, Control Engineering); nothing newer than April 2026 |
| 3 | 2026-10-08 | 5 | NVD news update CPE CNA enrichment "2026" nvd.nist.gov general news | WebSearch (standard) | no NVD change after April 2026 found; CVE Program blog listings |
| 3 | 2026-10-08 | 5 | Impacts of Software Bill of Materials SBOM generation on vulnerability detection O'Donoghue Syft Trivy Grype | WebSearch (standard) | authors' PDF at fdn.montana.edu; INL Pure page → sources |
| 3 | 2026-10-08 | 5 | Dann Plate Hermann Ponta Bodden "Identifying Challenges for OSS Vulnerability Scanners" arXiv | WebSearch (standard) | Paderborn RIS record (DOI, no file) |
| 3 | 2026-10-08 | 5 | "Identifying Challenges for OSS Vulnerability Scanners" pdf Achilles test suite 7,024 Java projects | WebSearch (standard) | author preprint at sse.cs.tu-dortmund.de → sources |
| 3 | 2026-10-08 | 5 | "Software Composition Analysis for Vulnerability Detection: An Empirical Study on Java Projects" arXiv pdf | WebSearch (standard) | FSE 2023 page, OpenAlex record; arXiv 2108.12078 (Imtiaz et al.) → sources; Zhao et al. full text not reachable (section 10) |
| 3 | 2026-10-08 | 5 | empirical study inconsistency affected versions vulnerability databases NVD GitHub Advisory Snyk OSV "affected versions" paper 2024 2025 | WebSearch (standard) | Dong et al. (USENIX), Anwar et al. (arXiv), Nguyen and Massacci (arXiv), safeguard.sh blog (rejected, section 9) |
| 3 | 2026-10-08 | 5 | grype "cpe-match requires verification" exact-direct-match high confidence | WebSearch (standard) | failed: "You've hit your session limit"; continued by fetching known URLs (Anchore sitemap → interpreting-results page) |
| 3 | 2026-10-08 | 5 | `ti:"Software Composition Analysis"`; `abs:"vulnerability scanners" AND abs:container`; `abs:SBOM AND abs:vulnerability AND abs:Grype`; `abs:"affected versions" AND abs:vulnerability AND abs:database`; `abs:CPE AND abs:NVD AND abs:inconsisten`; `abs:Trivy AND abs:Grype` | arXiv API (export.arxiv.org) | 2503.14388 (Churakova et al.), 2108.12078 (Imtiaz et al.), 2604.21278, 2306.05534, 2608.02669 (not read) |
| 3 | 2026-10-08 | 5 | `abs:SBOM AND abs:generators AND abs:vulnerab`; `ti:SBOM AND abs:accuracy`; `abs:"vulnerability databases" AND abs:inconsistenc`; `abs:"vulnerable versions" AND abs:NVD`; `abs:"Common Platform Enumeration"`; `abs:GHSA AND abs:NVD AND abs:Snyk`; `ti:"vulnerability scanners"`; `ti:"Container Security Vulnerability Detection Tools"`; `id_list=1302.4133` | arXiv API | 2409.06390 (Benedetti et al.), 2512.17710 (Rosso et al.), 2101.03844 (Javed and Toor), 1302.4133 (Nguyen and Massacci, abstract only), 2504.06880 and 2601.05622 (agent 1 or 5) |
| 3 | 2026-10-08 | 5 | `query.bibliographic=Impacts of Software Bill of Materials SBOM Generation on Vulnerability Detection`; `works/10.1145/3689944.3696164` | Crossref API | DOI 10.1145/3689944.3696164 (issued date inconsistent, section 9) |
| 3 | 2026-10-08 | 5 | `works/doi:10.1145/3611643.3616299` | OpenAlex API | open-access locations for Zhao et al.; all three refused automated download |
| 3 | 2026-10-08 | 5 | `overrides repo:anchore/grype-db`; `overrides_enabled OR "overrides-enabled" org:anchore`; `"Third-party SBOM may lead to inaccurate" repo:aquasecurity/trivy`; `cwe_ids repo:aquasecurity/trivy-db`; `"Supplier ADP" / SADP repo:CVEProject/cve-website` | GitHub code search (`gh api search/code`) | `.vunnel.yaml`; `pkg/sbom/cyclonedx/unmarshal.go`; test fixtures only; `ADPs.vue`, `SadpTag.vue` |
| 3 | 2026-10-08 | 5 | releases and tags: CVEProject/cve-schema, ossf/osv-schema, anchore/grype, anchore/vunnel, aquasecurity/trivy, DependencyTrack/dependency-track, google/osv-scanner, package-url/vers-spec, CycloneDX/specification, rpm-software-management/rpm, alpinelinux/apk-tools, CVEProject/cvelistV5 | GitHub API | versions pinned in section 1 |
| 4 | 2026-10-08 | 2 | fetch cisa.gov HBOM resource page and PDF (curl, browser user agent) | curl | HTTP 403 (Akamai "Access Denied") |
| 4 | 2026-10-08 | 2 | cisa.gov/resources-tools/resources/hardware-bill-materials-hbom-framework-supply-chain-risk-management | WebFetch (links only) | publication date 2023-09-25; framework PDF, fact sheet (2024-02 folder), webinar |
| 4 | 2026-10-08 | 2 | Wayback CDX for the framework PDF, the fact sheet and the resource page | web.archive.org CDX API | 30+ PDF captures 2023-11-01 to 2026-09-24 with one payload digest; one 403 capture (2026-07-16) |
| 4 | 2026-10-08 | 2 | GitHub API: CycloneDX/specification releases, tags, release notes of 1.7.1 and 1.7.2 | gh api | latest 1.7.2 (2026-09-17); no hardware change |
| 4 | 2026-10-08 | 2 | GitHub API: commits to cdx/device.md; all 131 PRs and the issues mentioning "device" in cyclonedx-property-taxonomy | gh api, gh search issues | device.md last changed 2025-10-28; open issues #43, #67, #104, #185 |
| 4 | 2026-10-08 | 2 | CycloneDX/specification issue #981, PR #982, milestones, PR #652 | gh | hardware support merged into 2.0-dev on 2026-08-20; 2.0 unreleased |
| 4 | 2026-10-08 | 2 | raw.githubusercontent.com CycloneDX schemas at tags 1.5, 1.6, 1.7, 1.7.2 and 2.0-dev modules | curl, jq | 1.5 lacks component manufacturer and address; 1.6 adds both |
| 4 | 2026-10-08 | 2 | GitHub API: spdx/spdx-3-model branches, tree of develop, main and 3.1-rc1, commits to model/Hardware, 3.1-rc1 release notes; spdx/spdx-spec releases | gh api | Hardware and SupplyChain profiles in 3.1-rc1 and develop; latest release 3.0.1 |
| 4 | 2026-10-08 | 2 | spdx.org/rdf/3.0.1/spdx-model.ttl; spdx/spdx-spec chapter headings at tags v2.2, v2.2.2, v2.3 | curl, gh api | model digest unchanged; CISA's SPDX clause numbers match SPDX 2.2 |
| 4 | 2026-10-08 | 2 | GitHub API and PyPI: hughsie/python-uswid | gh api, curl | uswid 0.6.0 (2026-03-16) |
| 4 | 2026-10-08 | 2 | lvfs.readthedocs.io pages; fwupd.org/lvfs/uswid; an LVFS component SWID page | curl | SBOM spec moved to OSFW; claims page; component page 403 |
| 4 | 2026-10-08 | 2 | sbomspec.osfw.foundation; GitHub open-source-firmware/sbom | curl, gh api | Firmware Embedded SBOM Specification 0.10 |
| 4 | 2026-10-08 | 2 | doc.coreboot.org/sbom/sbom.html; coreboot/coreboot Documentation/sbom and src/sbom | curl, gh api | uSWID in CBFS; CONFIG_SBOM default n |
| 4 | 2026-10-08 | 2 | docs.yoctoproject.org/dev-manual/sbom.html; openembedded-core master SPDX classes | curl, gh api | create-spdx inherits create-spdx-3.0; SPDX 3.0.1 |
| 4 | 2026-10-08 | 2 | zephyrproject-rtos/zephyr main and v4.4.2 west spdx sources | gh api, curl | v4.4.2: SPDX 2.2, 2.3; main adds 3.0, 3.1; default 2.3 |
| 4 | 2026-10-08 | 2 | UEFI firmware SBOM uSWID CoSWID Insyde OR AMI OR Phoenix OR "Intel FSP" embedded SBOM | WebSearch | UEFI blog (2023-10-04), UEFI 2024 Plugfest deck, Phoenix press release (not used) |
| 4 | 2026-10-08 | 2 | uefi.org/node/5015 and the 2024 webinar PDF | curl | proposal blog; deck slide 25 |
| 4 | 2026-10-08 | 2 | TCG Platform Certificate Profile specification version 2.0 revision component identifier | WebSearch | v1.1 r19 PDF and resource pages; summary claimed no v2.0 (rejected) |
| 4 | 2026-10-08 | 2 | trustedcomputinggroup.org resource pages (curl, WebFetch) | curl, WebFetch | Cloudflare challenge (403); PDFs under wp-content download directly |
| 4 | 2026-10-08 | 2 | Wayback captures of TCG resource pages (platform certificate, four component class registries, DICE pages) | web.archive.org | latest versions listed in sections 1.13 to 1.15 |
| 4 | 2026-10-08 | 2 | GitHub API: nsacyber/paccor, nsacyber/HIRS | gh api | PACCOR v2.0r16, HIRS v3.2.0 |
| 4 | 2026-10-08 | 2 | www.dmtf.org/dsp/DSP0274; DSP0274_<version>.pdf probes; Wayback captures of the DSP0274 and SPDM pages | curl, web.archive.org | live 403; 1.4.1 latest published |
| 4 | 2026-10-08 | 2 | redfish.dmtf.org/schemas/v1/ index; GitHub DMTF/Redfish-Publications tags and LICENSE | curl, gh api | bundle 2026.2 (2026-09-16), BSD-3-Clause |
| 4 | 2026-10-08 | 2 | datatracker API: draft-ietf-rats-corim, draft-ietf-suit-manifest, draft-ietf-rats-eat and their state codes | curl | CoRIM -11 in WGLC; SUIT -37 in RFC Ed Queue (Blocked); EAT published as RFC 9711 |
| 4 | 2026-10-08 | 2 | ietf.org archive drafts and rfc-editor.org RFC 9711, 9124, 9019, 9393, 9334 | curl | texts parsed |
| 4 | 2026-10-08 | 2 | iso.org/standard/77642.html and OBP preview (curl, WebFetch); Claude in Chrome | curl, WebFetch | 403 (Cloudflare); extension not connected |
| 4 | 2026-10-08 | 2 | Wayback capture of iso.org/standard/77642.html | web.archive.org | status, life-cycle dates |
| 4 | 2026-10-08 | 2 | "19770-6" hardware identification tag HWID elements | WebSearch | national store pages; GSO adoption (not verified) |
| 4 | 2026-10-08 | 2 | standards.iteh.ai ISO/IEC 19770-6:2024 sample | WebSearch | no iTeh sample; BSI Knowledge pages (2024 adoption; 2022 draft titled "Hardware schema") |
| 4 | 2026-10-08 | 2 | BSI Knowledge page and its public preview PDF | curl | 8-page preview with the contents list |
| 4 | 2026-10-08 | 2 | Auto-ISAC SBOM best practice guide vehicle ECU software bill of materials | WebSearch | Auto-ISAC press release and report page |
| 4 | 2026-10-08 | 2 | automotiveisac.com press release, sbom-reports page, report PDF | curl | report v3.0 (2025-01-17) |
| 4 | 2026-10-08 | 2 | UN Regulation No. 155 interpretation document software bill of materials ECU supplier "bill of materials" | WebSearch | vendor blogs only; no UNECE document |
| 4 | 2026-10-08 | 2 | unece.org R155e.pdf, R156e.pdf (2021-03 folder) | curl, web.archive.org | live 403; Wayback captures; 0 SBOM hits |
| 4 | 2026-10-08 | 2 | cert-in.org.in Technical Guidelines PDF v2.0 | curl | digest matches RPT-0014 |
| 4 | 2026-10-08 | 2 | CERT-In "Technical Guidelines" SBOM QBOM CBOM AIBOM HBOM version | WebSearch | v2.0 (2025-07-09) only |
| 4 | 2026-10-08 | 2 | "hardware bill of materials" guidance government agency 2025 OR 2026 HBOM national | WebSearch | ITU-T C-548; IST news (not primary); Federal Register 2025-16147 |
| 4 | 2026-10-08 | 2 | itu.int/md/T25-SG17-C-0548/en; ITU-T SG17 work programme page | curl | C-548 metadata; restricted text |
| 4 | 2026-10-08 | 2 | Institute for Security and Technology hardware bill of materials HBOM initiative Allan Friedman | WebSearch | biographies and podcasts; IST site search and topic feed: no HBOM item |
| 4 | 2026-10-08 | 2 | Korea HBOM guideline hardware bill of materials KISA OR MSIT 2025 | WebSearch | only ITU-T C-548 |
| 4 | 2026-10-08 | 2 | federalregister.gov API document 2025-16147 | curl | CISA 2025 SBOM draft notice; no hardware |
| 4 | 2026-10-08 | 2 | Wayback capture of the CISA 2026 SBOM Minimum Elements PDF | web.archive.org | "hardware" 0 hits, "firmware" 1 |
| 4 | 2026-10-08 | 2 | cyclonedx.org/capabilities/hbom/ | curl | quote re-checked |
| 5 | 2026-10-08 | 3, 4 | what 0.1.0 §3 and §4, RPT-0005 fan-out notes, RPT-0011 and the library records already say about the tools and GUAC | local repository read | report §3, §4; RPT-0011 §3 ("three trees"); records `guac`, `osv-schema`, `openssf-scorecard-checks` |
| 5 | 2026-10-08 | 3 | latest releases of Syft, Grype, Trivy, GUAC, Dependency-Track, Hyades, deps.dev | `gh api …/releases` | Syft v1.54.1, Grype v0.120.1, Trivy v0.75.0, GUAC v1.1.0, DT 5.2.0; Hyades only pre-releases; deps.dev none |
| 5 | 2026-10-08 | 3 | all Syft release notes containing "SPDX 3", "spdx3", "3.0.1" | `gh api --paginate` + `jq` | v1.46.0 "SPDX 3 Support" (#4250, PR #4269) |
| 5 | 2026-10-08 | 3 | Syft issue #4250, PR #4269 and its file list; PR #3462 | `gh api` | SPDX 3 read and write; OS entry in SPDX still open |
| 5 | 2026-10-08 | 3 | Grype 0.120.0 release notes; issue #3746, PR #3747 | `gh api` | dpkg and rpm `using-cpes` were no-ops |
| 5 | 2026-10-08 | 3 | `repo:aquasecurity/trivy "SPDX 3" in:title`; `spdx3`; `"SPDX v3"`; `"spdx 3"`; `SPDX 3.0 support` | GitHub issue search (`gh api search/issues`) | no SPDX 3 issue or PR; only SPDX 2.3 and licence-list items |
| 5 | 2026-10-08 | 3 | `repo:aquasecurity/trivy SPDX 3` | GitHub discussion search (GraphQL) | #8498 "SPDX 3?"; #11140 Syft SPDX false negative; #11139 Syft CycloneDX SrcName |
| 5 | 2026-10-08 | 3 | Trivy SPDX 3.0 support read write SBOM 2026 | WebSearch | trivy.dev SBOM pages; discussion #7174 (CycloneDX 1.6 output, read and not used); no SPDX 3 statement |
| 5 | 2026-10-08 | 3 | GUAC guacsec SPDX 3 support release 2026 | WebSearch | GitHub releases page, third-party blogs (not used); no SPDX 3 release |
| 5 | 2026-10-08 | 3 | Dependency-Track 5.2.0 release SPDX (the tool ran one follow-up query of its own, text not shown) | WebSearch | news and mirror sites; its summary said 5.2.0 does not exist (rejected, section 9) |
| 5 | 2026-10-08 | 3 | Dependency-Track v5 docs sitemap; then 15 concept, reference and upgrade pages | `curl` | file formats, analyzers, data sources, VEX, findings, projects, integrity, v5 changes, breaking changes |
| 5 | 2026-10-08 | 3 | `repo:DependencyTrack/dependency-track "spdxVersion"`; `"SPDX" path:…/resources` | GitHub code search | one test (`BomResourceTest.java`); licence headers |
| 5 | 2026-10-08 | 3 | Dependency-Track 5.2.0 file tree, all paths containing `spdx` | `gh api git/trees/5.2.0?recursive=1` | 20 paths, all licence-expression or licence-list code |
| 5 | 2026-10-08 | 3 | DT issue #1746 with comments; PR #6835 | `gh api` | open, on hold; Snyk checksum matching for Maven |
| 5 | 2026-10-08 | 3 | GUAC schema directory at v1.1.0 and `main`; backends and parser directories; README; `store.go`; `neptune.go`; keyvalue and ent sources; parsers | `gh api contents` + `curl` raw | 28 schema files, identical; 6 backend directories; default `keyvalue` |
| 5 | 2026-10-08 | 3 | GUAC issue #1850 with comments and timeline; tools-golang #237, PR #249, releases | `gh api` | #1850 open, `help wanted` added 2026-10-06; tools-golang SPDX 3 only in v0.6.0-rc4 |
| 5 | 2026-10-08 | 3 | `guacsec/guac-docs` tree; all 46 Markdown pages at `b8022b5` | `gh api` + `curl` | ontology pages; "Actor Tree (Not in v0.1 BETA)"; 0.1.0's quotes found in `graphql.md` and `certifier-osv.md` |
| 5 | 2026-10-08 | 3 | docs.deps.dev index, API index, v3, v3alpha, BigQuery, FAQ; Google APIs Terms page | `curl` | endpoints, data model, terms; no rate limits documented |
| 5 | 2026-10-08 | 3 | `google/deps.dev` repository metadata and `api/` directory | `gh api` | Apache-2.0; `v3`, `v3alpha` |
| 5 | 2026-10-08 | 4 | `gh api repos/Threat-Radar/tradar/commits/main`, branches, repository | `gh api` | `main` = `26d9c76`; `dev` = `9e79f21` |
| 2 (re-check) | 2026-10-08 | 6, 7 | read fanout-identity.md sections 1 to 8, dimensions.md 0.3.0, pilot.md, DL-0015 "Phase 1 fan-out", and section 10 of the four other fan-out files | local repository read | 4 sets of notes for agent 2 |
| 2 (re-check) | 2026-10-08 | 7 | purl-spec releases; tree at `v1.1.0`; Clauses 2, 5, 6; Annex B; `common-qualifiers.md`; `how-to-build.md`; 2nd edition release notes; type schema 1.1; 7 type files; pull request #1012; issue #741 and comments | gh + curl | hashes as agent 2 recorded; 42 types; no `supplier` type; `deb` defines only `arch` |
| 2 (re-check) | 2026-10-08 | 7 | vers-spec releases, tree and Clause 5 at `v1.2.1`; pull request #65 | gh + curl | `npm` and `pypi` only; #65 merged 2026-05-13 |
| 2 (re-check) | 2026-10-08 | 7 | ECMA-427 1st edition PDF; Ecma landing page | curl + pdftotext | same hashes; 0 hits for sort, order, lexicograph |
| 2 (re-check) | 2026-10-08 | 6, 7 | ISO Open Data CSV filtered for 27056, 18670, 19770-2, 19770-6, 24089, 27055, 5962; container listing | curl + python3 | same file (2026-10-07); stages as reported; listing HTTP 404 |
| 2 (re-check) | 2026-10-08 | 7 | NIST IR 7695, 7696, 7697 PDFs | curl + pdftotext | same hashes; quotes verbatim |
| 2 (re-check) | 2026-10-08 | 7 | NVD CPE API: 16 pairs and 16 full names; 3 names without the Alpine suffix; zlib 1.3.1; CPE Match API for CVE-2022-37434 | curl + jq (NVD API 2.0) | 3 of 16 pairs; 0 of 16 names; without suffix only busybox 1.37.0 exists |
| 2 (re-check) | 2026-10-08 | 6, 7 | NVD CVE API with `purl=`, `packageURL=`, `cpeName=`; CVE-2026-85091; news page; `cve_affected_1.0.json`; developer page | curl | purl and packageURL refused (HTTP 404); CNA `affected` with a `pkg:github/…/zlib` purl; developer page is a script shell |
| 2 (re-check) | 2026-10-08 | 6, 7 | RFC 9393, RFC 8122, RFC 5234, RFC 9711 | curl | 0 hits for purl and others in RFC 9393; "ABNF strings are case insensitive" |
| 2 (re-check) | 2026-10-08 | 7 | IANA URI schemes CSV, `prov/pkg`, `prov/gitoid`; Hash Function Textual Names CSV and page | curl | all Provisional; 9 hash names; reference RFC 8122 |
| 2 (re-check) | 2026-10-08 | 7 | OmniBOR spec releases, tags, `SPEC.md` history; `SPEC.md` at `v0.1` and `main`; `GITOID_URI.txt`; pull request #84 | gh + curl | #84 opened 2025-07-28, merged 2025-11-17 |
| 2 (re-check) | 2026-10-08 | 7 | SWHID pull request #72, issues #61 and #70; v1.2 pages (index, Scope, Syntax, Core identifiers, Qualified identifiers) | gh + curl | #72 is a pull request merged 2026-09-19; `'40000'` served |
| 2 (re-check) | 2026-10-08 | 7 | CycloneDX schema 1.7.2 (`jq`); release list; issue #96 and comments | curl + gh + jq | two `omniborId` examples (SHA-1 and SHA-256) |
| 2 (re-check) | 2026-10-08 | 6, 7 | SPDX 3.0.1 model and five class pages; spdx-spec releases | curl + python3 | same hashes; `packageUrl` range `xsd:anyURI` |
| 2 (re-check) | 2026-10-08 | 6, 7 | OCI image-spec and distribution-spec releases and all tags; files at `v1.1.1`; `artifact.md` at four tags; pull request #999 | gh + curl | no newer release; quotes verbatim |
| 2 (re-check) | 2026-10-08 | 6 | in-toto attestation releases; 8 spec files at `v1.2.0` | gh + curl | spdx3.md says "whatever artifacts" |
| 2 (re-check) | 2026-10-08 | 6 | Sigstore protobuf-specs releases and tags; `sigstore_bundle.proto` at `v0.5.2` | gh + curl | 0 releases; tags only |
| 2 (re-check) | 2026-10-08 | 6 | BuildKit releases; three attestation documents at `v0.34.0` | gh + curl | single-platform example stored in an index |
| 2 (re-check) | 2026-10-08 | 6 | cosign releases and `v3.0.0` tag; v3.0.1 notes; `CHANGELOG.md`, docs, specs, `attestation.go`, `go.mod` at `v3.1.3`; in-toto-golang `v0.11.0` constants | gh + curl | no v3.0.0 release; its notes are in the v3.0.1 body |
| 2 (re-check) | 2026-10-08 | 6 | `actions/attest` and `attest-sbom` releases and READMEs | gh + curl | quotes verbatim |
| 2 (re-check) | 2026-10-08 | 6, 7 | Docker Hub registry: 4 tags, index, arm64 manifest, config, attestation manifest, 2 blobs, referrers for 2 digests, 6 fallback and cosign tags | curl (registry API v2) | as agent 2 reported; referrers response hash identical |
| 2 (re-check) | 2026-10-08 | 6, 7 | Syft 1.52.0 runs (`--from registry --platform linux/arm64`): `alpine:latest` twice (CycloneDX, Syft JSON, SPDX 2.3); `alpine:3.24.2`; `alpine@sha256:294b683c…`; `alpine:latest` twice as SPDX 3 | syft (local run) | Syft JSON byte-identical to the pilot's; root `version` is the manifest digest, a tag or the index digest; `tags: []`; `bom-ref` stable; SPDX 3 IRIs change |
| 2 (re-check) | 2026-10-08 | 6, 7 | Syft v1.52.0 source: `image_source.go`, `decoder.go`, CycloneDX and SPDX `to_format_model.go`, cpegenerate README | curl | version logic; zero SHA-1 fallback |
| 2 (re-check) | 2026-10-08 | 7 | OSV.dev API: 17 queries; GHSA-cpwx-vrp4-4pq7; UBUNTU-CVE-2025-60876; an Ubuntu query (UBUNTU-CVE-2024-13176) | curl (api.osv.dev) | results as agent 2 reported; Ubuntu purls served without versions; GHSA copy has a purl |
| 2 (re-check) | 2026-10-08 | 7 | OSV.dev source at `16b340c78a51` (`go/purl`, `query_affected.go`, `docs/api`); osv-schema v1.9.1 `schema.md` and releases | gh + curl | only the Debian parser reads `distro`; `determineversion` takes MD5 file hashes; `Red Hat` ecosystem has a CPE suffix |
| 2 (re-check) | 2026-10-08 | 7 | canonical/ubuntu-security-notices `osv/cve/2025/UBUNTU-CVE-2025-60876.json` | curl | versioned purls in the source file |
| 2 (re-check) | 2026-10-08 | 7 | GitHub REST API description at `7dee0622`; GHSA-cpwx-vrp4-4pq7 file; advisory-database tarball at `0d77cdb5` | gh + curl + python3 | 13 ecosystems; 0 purl or CPE; 0 of 67,514 entries with a purl |
| 2 (re-check) | 2026-10-08 | 7 | deps.dev v3 and v3alpha pages; hash query for the jinja2 3.1.4 wheel (SHA-256 from PyPI's JSON API) | curl | same page hashes; resolves to PYPI jinja2 3.1.4 |
| 2 (re-check) | 2026-10-08 | 7 | GUAC latest release; 8 schema files at `v1.1.0` | gh + curl | same hashes |
| 2 (re-check) | 2026-10-08 | 7 | Dependency-Track component identity page; releases; `pom.xml`, `InternalVulnAnalyzer.java` and OSV `ModelConverter.java` at 5.2.0 | curl + gh | `versatile-core` 0.26.0; vers ranges in the internal analyzer |
| 2 (re-check) | 2026-10-08 | 7 | code search: omnibor, gitoid, swhid in guacsec/guac, google/osv.dev, DependencyTrack/dependency-track, DependencyTrack/hyades-apiserver; versatile in dependency-track | gh search/code | 0 hits except Dependency-Track's vendored CycloneDX proto; rate limit hit once, then retried |
| 2 (re-check) | 2026-10-08 | 7 | SBOMproof (arXiv 2510.05798v1) abstract and PDF; Anwar et al. (arXiv 2006.15074v1) PDF | curl + pdftotext | same hashes; quotes verbatim |
| 2 (re-check) | 2026-10-08 | 6, 7 | CISA 2026 Minimum Elements (IC3 copy); CVE schema releases and `CVE_Record_Format.json` at `v5.2.0` | curl + gh + pdftotext | p. 12 identifier and hash-name sentences; p. 5 G7 mention; `packageURL` is `uriType` |
| 2 (re-check) | 2026-10-08 | 6 | UN R156: UN ODS (ECE/TRANS/WP.29/2020/80); EUR-Lex OJ copy; live unece.org `R156e.pdf`; Wayback capture of 2023-12-16 | curl | quotes verbatim; §7.2.1.2 condition; unece.org HTTP 403; Wayback copy has agent 4's hash |
| 2 (re-check) | 2026-10-08 | 6 | SUIT draft-37 text; datatracker document and its 7 states; RFC Editor queue page | curl | IESG "RFC Ed Queue"; RFC Editor "Blocked"; queue page built by script |
| 2 (re-check) | 2026-10-08 | 6 | tradar `main` and two files at `26d9c76`; LinkML draft, proposal, ARCH-0001, ADR-0001, ADR-0004, RPT-0015 | gh; local read + python3 | unchanged; 62 slots; `grep` also hits line 633; "CPE/purl" in RPT-0015 §3 |
| 2 (re-check) | 2026-10-08 | 6 | reproducible-builds.org definition; slsa.dev/spec; library records (nine) and proposed ids | curl; local library read | same hashes; statuses as reported; no proposed id exists yet |
| 2 (re-check) | 2026-10-08 | 7 | apk-tools GitHub mirror (`doc/apk-v2.5.scd`, `doc/apk-package.5.scd`); Alpine wiki "Apk spec" | gh + curl | installed-database checksum not defined there; wiki behind a bot challenge |
| 2 (re-check) | 2026-10-08 | 6, 7 | WebSearch | none | not used; every check fetched a known URL, API or tool |

### Tool runs, second pass

The pilot's runs ([pilot.md](pilot.md)), one check run in the main session, and the agents' runs. Agent 1's rows start with its test id, which its notes use. Outputs and downloads were not committed.

| agent | date | command | input | result |
|---|---|---|---|---|
| pilot | 2026-10-08 | `syft alpine:latest -o cyclonedx-json=alpine.cdx.json -o syft-json=alpine.syft.json -o spdx-json=alpine.spdx23.json` (Syft 1.52.0) | `alpine:latest`, linux/arm64 (platform manifest `sha256:260479a1…`) | CycloneDX 1.7: 16 `library`, 78 `file`, 1 `operating-system` components; purl and CPE on 16 of 16 packages, no package hash or supplier; 24 dependency edges ([pilot.md](pilot.md) §2) |
| pilot | 2026-10-08 | `grype sbom:alpine.cdx.json -o json` (Grype 0.119.0; database schema v6.1.10, built 2026-10-08T06:33:47Z) | the Syft CycloneDX file above | 30 matches, 15 CVEs: 29 `cpe-match` in `nvd:cpe`, 1 Alpine-feed exact match with a fix; CWEs on all 30, all `Secondary` (pilot.md §3) |
| pilot | 2026-10-08 | `grype sbom:alpine.cdx.json -o cyclonedx-json` | the same file | 30 `vulnerabilities` entries; no `cwes`, no match type or matcher; `affects[].ref` values do not match Syft's `bom-ref` values (pilot.md §3) |
| pilot | 2026-10-08 | registry `GET /v2/library/alpine/manifests/latest` (OCI index media type) | Docker Hub | index `sha256:294b683c…` lists 8 platform manifests (linux/arm64/v8 = `sha256:260479a1…`) and 8 `attestation-manifest` entries (pilot.md §1) |
| main | 2026-10-08 | `syft dir:. -o spdx-json@3.0` (Syft 1.52.0) | a folder holding one `requirements.txt` | SPDX 3.0.1 JSON-LD (`specVersion` 3.0.1, context `spdx-context.jsonld` 3.0.1): Syft 1.52.0 writes SPDX 3, which 0.1.0 §3 denied (DL-0015) |
| 1 | 2026-10-08 | T1: `rdflib.Graph().parse(f, format="json-ld")` | 9 SPDX 3 examples (spec 3.0.1 + 8 from `spdx-examples`) | all loaded (47 to 983 triples); no undefined keys |
| 1 | 2026-10-08 | T2: `pyshacl.validate(g, shacl_graph=model, ont_graph=model)` with the served and the tagged model | same 9 | 7 conform; `software/example7` (5) and `example14` (1) fail `sh:class` on `import`ed IRIs; same result with both models |
| 1 | 2026-10-08 | T3: `spdx3-validate -q --json <file>` | spec example, example7, example14, ai/example01 | all exit 0 |
| 1 | 2026-10-08 | T4: PyLD `to_rdf` with `requests_document_loader` vs rdflib | spec example | 47 triples each; differ only in `xsd:string` typing; default PyLD loader failed ("Could not expand input") |
| 1 | 2026-10-08 | T5: python-jsonschema (`validator_for(schema)`, with and without `FORMAT_CHECKER`) | 9 examples | 0 errors each |
| 1 | 2026-10-08 | T6: 22 mutations M0 to M22 of the spec example through JSON Schema, JSON-LD, pySHACL and spdx3-validate's SHACL step (`scripts/spdx_mutations.py`) | spec example | M1, M2, M3, M7, M8, M8b, M14, M17, M19 fail both layers; M9, M10, M11, M20 fail only the JSON Schema; M15, M16, M22 fail only SHACL (M16 passes spdx3-validate); M4, M5, M6, M12, M13, M18, M21 pass both |
| 1 | 2026-10-08 | T7: Python check of AI and Dataset conformance rules | 9 examples | `ai/example01` declares `ai`; both AIPackages lack `hasConcludedLicense`; its DatasetPackage lacks `releaseTime` |
| 1 | 2026-10-08 | T8: AIPackage and DatasetPackage with only `spdxId`, `name`, `creationInfo` (+ `datasetType`) | spec example + 2 elements | JSON Schema 0 errors; SHACL conforms |
| 1 | 2026-10-08 | T9: VexNotAffected with `relationshipType` `contains` and a Package as `from` | spec example + 1 element | JSON Schema 0 errors; SHACL conforms |
| 1 | 2026-10-08 | T10: `Draft7Validator` with a `referencing` registry (spdx, jsf, cryptography-defs) | `alpine.cdx.json` (pilot) | valid (C0) |
| 1 | 2026-10-08 | T11: 20 mutations C0 to C19 (`scripts/cdx_mutations.py`) | `alpine.cdx.json` | C3b, C5, C6, C15, C17, C18 fail; all others pass |
| 1 | 2026-10-08 | T12: C12 again after `pip install rfc3339-validator` | same | `"yesterday"` now fails with format checking on |
| 1 | 2026-10-08 | T13: `xmllint --noout --schema` and `xmlschema.validate` | 3 SWID tags: no tagCreator; no Entity; tagId "alpine" | all three valid with both validators |
| 1 | 2026-10-08 | T14: `_bcp14` keyword counts (library `bin/_bcp14.py`, imported read-only) | CycloneDX schemas 1.6 to 1.7.2; ECMA-424 text; SPDX TTL comments, model Markdown, spec prose; RFC 9393 | section 2, Q7 |
| 1 | 2026-10-08 | T15: rdflib `to_isomorphic` and shape-by-shape comparison | served vs tagged SPDX 3.0.1 model | not isomorphic; one shape differs (section 1.3) |
| 1 | 2026-10-08 | T16: `jq` counts | `alpine.cdx.json` | section 1.21 |
| 3 | 2026-10-08 | `jq` over `matchDetails`, `cwes`, `fix`, `descriptor` | pilot `alpine.grype.json` (`97e45336…0405`) | 30 matches, 15 CVEs; 29 `cpe-match` details (`nvd:cpe`), 1 exact pair (`alpine:distro:alpine:3.24`); all CWEs `Secondary` (1.11) |
| 3 | 2026-10-08 | `python3` over 402,861 records | cvelistV5 snapshot | section 1.1 counts |
| 3 | 2026-10-08 | `python3` over 8 API pages | NVD API, CVEs published 2026-09 | section 1.2 counts and the CNA versus NVD comparison |
| 3 | 2026-10-08 | `python3` over 382,210 files | GHSA repository tarball | section 1.5 counts |
| 3 | 2026-10-08 | `python3` over 7 zips | osv.dev exports | section 1.4 counts |
| 3 | 2026-10-08 | `python3` over 74,502 entries | Debian tracker JSON | section 1.7 counts |
| 5 | 2026-10-08 | `gh api repos/{anchore/syft, anchore/grype, aquasecurity/trivy, guacsec/guac, DependencyTrack/dependency-track}/releases/latest` | GitHub | Syft v1.54.1 (2026-10-06), Grype v0.120.1 (2026-10-06), Trivy v0.75.0 (2026-10-01), GUAC v1.1.0 (2026-03-13), Dependency-Track 5.2.0 (2026-10-08) |
| 5 | 2026-10-08 | `curl -O` release archives and checksum files; `grep` of each archive line, then `shasum -a 256 -c` | Syft 1.54.1, Grype 0.120.1, Trivy 0.75.0 darwin arm64 | all three `OK` (digests in 1.1 to 1.3) |
| 5 | 2026-10-08 | `grype db update` (0.120.1) | scratch DB cache | DB v6.1.10 built 2026-10-08T06:33:47Z (same as pilot) |
| 5 | 2026-10-08 | `trivy image --download-db-only`, `--download-java-db-only` (0.75.0) | scratch cache | DB v2 updated 2026-10-08T15:33:46Z; Java DB v1 updated 2026-10-08T16:14:37Z |
| 5 | 2026-10-08 | `curl` Maven Central `log4j-core-2.14.1.jar`, `.sha1`, `.md5` (`.sha256`, `.sha512`: 404) | repo1.maven.org | jar SHA-1 `9141212b8507ab50a45525b545b39d224614528b` = `.sha1`; MD5 `948dda787593340a7af1a18e328b7b7f` = `.md5`; SHA-256 `ade7402a70667a727635d5c4c29495f4ff96f061f12539763f6f123973b465b0`; never executed |
| 5 | 2026-10-08 | `syft scan dir:empty -o nonexistent-format` (1.52.0 and 1.54.1) | empty folder | identical format lists; `spdx-json @ 2.2, 2.3, 3.0` |
| 5 | 2026-10-08 | `syft scan dir:empty -o spdx-json@3.0` (1.52.0 and 1.54.1) | empty folder | SPDX 3.0.1 JSON-LD from both versions |
| 5 | 2026-10-08 | `syft scan alpine:latest --platform linux/arm64 -o syft-json -o cyclonedx-json -o spdx-json -o spdx-json@3.0` (1.54.1) | alpine:latest | manifest `sha256:260479a1…3e2d`; facts in section 2 Q1; identical to pilot (1.52.0) on every CycloneDX count |
| 5 | 2026-10-08 | same, second run, `-o spdx-json@3.0 -o cyclonedx-json` | alpine:latest | new `serialNumber` and SPDX namespace UUID; same `bom-ref` and local SPDX id for zlib |
| 5 | 2026-10-08 | `python3 runs/edges.py` on CycloneDX, SPDX 2.3, SPDX 3 | alpine, debian, tradar | 24, 216, 104 dependent→dependency pairs, equal across the three formats |
| 5 | 2026-10-08 | `grype sbom:alpine.cdx.json -o json -o cyclonedx-json -o table` (0.120.1) | Syft alpine CycloneDX | 30 matches, 15 CVEs (section 2); CycloneDX output 0 `cwes` |
| 5 | 2026-10-08 | `grype sbom:alpine.spdx3.json` and `sbom:alpine.spdx23.json` (0.120.1); `grype sbom:alpine.spdx3.json` (0.119.0, scratch DB) | Syft alpine SPDX | 30 matches each |
| 5 | 2026-10-08 | `trivy image --platform linux/arm64 --scanners vuln -f json alpine:latest` (0.75.0) | alpine:latest | 16 packages, 1 CVE (CVE-2026-85091, `alpine`, fixed) |
| 5 | 2026-10-08 | `trivy sbom -f json` on Syft alpine CycloneDX, SPDX 2.3, SPDX 3 (0.75.0) | Syft alpine files | CycloneDX: 1 CVE; SPDX 2.3: `family="none"`, `Unsupported os`, 0 results; SPDX 3: `format="unknown"`, FATAL |
| 5 | 2026-10-08 | `trivy image -f cyclonedx --scanners vuln` and `-f spdx-json` (0.75.0) | alpine:latest | CycloneDX 1.7: 16 libraries + OS, purl 16, CPE 0, hashes 16, supplier 16, 30 edges, 1 vulnerability with `cwes` [787]; SPDX-2.3: 18 packages, 16 checksums, 16 suppliers, 24 `DEPENDS_ON` |
| 5 | 2026-10-08 | `syft scan dir:<tradar> -o syft-json -o cyclonedx-json -o spdx-json -o spdx-json@3.0` (1.54.1) | tradar `26d9c76`, clean | 76 packages, 996 CPEs (10 dictionary), 104 edges; 4 zero-SHA-1 files in SPDX; 0 of 781 `uv.lock` hashes kept |
| 5 | 2026-10-08 | `grype sbom:tradar.cdx.json -o json -o cyclonedx-json`; same on SPDX 2.3 and SPDX 3 (0.120.1) | Syft tradar files | CycloneDX: 17 matches, 16 GHSA; SPDX 2.3 and 3: 15 (GitHub Action matches lost); CycloneDX output 0 `cwes` |
| 5 | 2026-10-08 | `syft convert tradar.spdx3.json -o syft-json` (also from SPDX 2.3 and CycloneDX) | Syft tradar files | from SPDX: 9 `UnknownPackage` + 67 `python`; from CycloneDX: 9 `github-action` + 67 `python` |
| 5 | 2026-10-08 | `trivy fs --scanners vuln -f json <tradar>`; `trivy sbom -f json tradar.cdx.json` (0.75.0) | tradar; Syft tradar CycloneDX | `fs`: 14 CVEs (`uv.lock`); `sbom`: 15; difference python-dotenv 1.0.0 CVE-2026-28684; worktree still clean |
| 5 | 2026-10-08 | `syft scan debian:12-slim --platform linux/arm64 -o …` (1.54.1) | debian:12-slim | manifest `sha256:a1b86db5…be82a`; root version `12-slim`; 88 packages, 261 CPEs, 216 edges |
| 5 | 2026-10-08 | `grype sbom:debian.cdx.json`; also SPDX 2.3 and SPDX 3 (0.120.1) | Syft Debian files | 229 matches, 101 CVEs, all `dpkg-matcher`, 0 `cpe-match`; same from SPDX; CycloneDX output 0 `cwes` |
| 5 | 2026-10-08 | `trivy image … debian:12-slim`; `trivy sbom debian.cdx.json`; `trivy image -f cyclonedx` (0.75.0) | debian:12-slim; Syft Debian CycloneDX | image: 235 findings, 106 ids; `sbom`: 31; `SrcName` ≠ name for 62 of 88 (image) and 0 of 88 (`sbom`) |
| 5 | 2026-10-08 | `python3` purl comparison of Syft and Trivy CycloneDX | alpine, Debian | identical full purls 0/16 and 22/88; identical before `?` 16/16 and 77/88 |
| 5 | 2026-10-08 | `syft scan file:log4j-core-2.14.1.jar -o …` (1.54.1) | log4j jar | 1 package, purl `pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1`, 4 CPE candidates, no CycloneDX package hash, SPDX SHA-1 = Maven Central `.sha1` |
| 5 | 2026-10-08 | `grype sbom:log4j.cdx.json` (also SPDX 2.3 and 3) (0.120.1) | Syft log4j files | 7 GHSA, `java-matcher`, all fixed; same from SPDX |
| 5 | 2026-10-08 | `trivy rootfs`, `trivy fs`, `trivy sbom` (0.75.0) | folder with the jar; Syft log4j CycloneDX | `rootfs` 7 CVEs; `fs` 0; `sbom` 7 |
| 5 | 2026-10-08 | installed `trivy sbom -f json` (0.74.0, scratch DB) | Syft alpine, Debian, tradar CycloneDX | 1, 31, 15: same as 0.75.0 |
| 5 | 2026-10-08 | `python3` `jsonschema` 4.25.0 validation | 4 Syft SPDX 3 files against SPDX 3.0.1 JSON Schema | 0 errors each |
| 5 | 2026-10-08 | `python3` regex test from `originator_supplier.go:203` | maintainer fields of Syft JSON | predicts SPDX supplier presence for 16/16 Alpine and 88/88 Debian packages |
| 5 | 2026-10-08 | `syft cataloger list -o json` (1.54.1) | none | 71 cataloger names; none for hardware or firmware |
| 5 | 2026-10-08 | `grype config` (0.119.0, 0.120.1); `grype --help`; `trivy --help`; `trivy image --help`; `syft scan --help` | none | `using-cpes` defaults; inputs, outputs, VEX flags, severity sources (sections 1.2, 1.3) |
| 5 | 2026-10-08 | `python3 guac/parse_sdl.py` | 28 GUAC schema files, v1.1.0 | 91 types, 23-member `Node` union, 86 `Edge` values, 69 inputs; provenance and time fields per evidence type |
| 5 | 2026-10-08 | `diff -rq schema-v1.1.0 schema-main` | GUAC schema at v1.1.0 and `6ce366c` | identical |
| 5 | 2026-10-08 | `curl` 15 deps.dev API calls (`depsdev/live/urls.txt`) | api.deps.dev | all HTTP 200; results in 1.6 |
| 5 | 2026-10-08 | `gh api repos/Threat-Radar/tradar/commits/main`; `git -C tradar status`, `log` | tradar | `26d9c76…`; clean worktree |
| 5 | 2026-10-08 | `grep` and `python3` keyword searches in tradar (`cwe`, quoted SBOM keys, `manifestDigest`, `EdgeType.*`) | tradar `threat_radar/`, `tests/`, docs | results in 1.7 |
| 2 (re-check) | 2026-10-08 | `syft` 1.52.0, six runs on `alpine` pulled from the registry (fanout-identity.md §9) | `alpine:latest` and other references | Syft JSON byte-identical to the pilot's; root `version` depends on how the image was named |
| main | 2026-10-08 | `syft registry:<ref> -o cyclonedx-json` (Syft 1.52.0), three references | `alpine:latest`; `alpine:3.24.2`; `alpine@sha256:294b683c…` | root `version`: the platform manifest digest; `3.24.2`; the index digest `sha256:294b683c…` |
