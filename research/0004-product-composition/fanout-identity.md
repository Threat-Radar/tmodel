---
schema: "archdoc/v1"
id: RPT-0004-fanout-identity
title: "RPT-0004 Phase 1 fan-out: identifier schemes and build identity"
type: research
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: RPT-0004
---

> Phase 1 fan-out notes, kept as the research agent wrote them; corrections found later are recorded in the design log (DL-0015). Downloaded files were not committed (third-party material); each is identified by URL and SHA-256 so it can be fetched again.

# RPT-0004 fan-out, agent 2: dimensions 6 and 7 (Table 3)

**Scope.** Dimension 7 (identifier schemes: purl, CPE, SWID and CoSWID tag ids, OmniBOR gitoids, SWHIDs, cryptographic hashes, OCI digests) and dimension 6 (build identity and the radar to tmodel input contract). Table 3 is filled in section 3.

**Method.** Everything below was checked on 2026-10-08. Specifications, schemas, source files and API responses were downloaded with `curl` or `gh api` into the agent's scratch folder and read from their own text; JSON was parsed with `jq` and `python3`, PDFs with `pdftotext`. WebSearch worked in this session (6 searches, section 7); it was used only to find documents, and every quote was then confirmed in the fetched file. No WebFetch summaries were used. Where a site blocked `curl` (unece.org, iso.org, wiki.alpinelinux.org), this is said and another primary copy was used or the item is left open.

**Acronyms used throughout.** SBOM: software bill of materials. purl: Package URL. CPE: Common Platform Enumeration. NVD: National Vulnerability Database (NIST). SWID: software identification (tag), ISO/IEC 19770-2. CoSWID: Concise Software Identification tag (RFC 9393). SWHID: SoftWare Hash IDentifier. OCI: Open Container Initiative. OSV: Open Source Vulnerability (format and the OSV.dev database). GHSA: GitHub Security Advisory. GUAC: Graph for Understanding Artifact Composition. DSSE: Dead Simple Signing Envelope. VSA: Verification Summary Attestation (SLSA). SUIT: Software Updates for Internet of Things (IETF). RXSWIN: RX Software Identification Number (UN Regulation No. 156). DIS: draft international standard (ISO stage 40). OmniBOR and SLSA are used as names; neither text we read expands them.

**Two kinds of evidence are kept apart.** "Spec" findings quote what a document says. "Observation" findings report what a tool run, an API or a registry returned on 2026-10-08. The pilot SBOMs are Syft 1.52.0 and Grype 0.119.0 outputs for `alpine:latest`, run on 2026-10-08 by the main session (files in `scratchpad/pilot/`).

**Headline findings.**

1. **Five SHA-256 values identify "the same image".** For the pilot image on Docker Hub, `alpine:latest` resolves to an image index (`sha256:294b683c…`); Syft recorded the linux/arm64/v8 manifest (`sha256:260479a1…`, one of eight platform manifests); the image config, which the OCI specification calls the ImageID, is `sha256:33bee74c…`; the one layer is `sha256:a9986cd6…` compressed and `sha256:1b349a33…` uncompressed. The CycloneDX output keeps only the manifest digest, in `metadata.component.version` (1.20, 1.21).
2. **Two SBOMs of the same bytes name the same packages differently.** Docker's own SBOM attestation for that arm64 manifest (Docker Scout 1.18.1, 2026-09-17) writes `pkg:apk/alpine/zlib@1.3.2-r0?os_name=alpine&os_version=3.24`; Syft writes `pkg:apk/alpine/zlib@1.3.2-r0?arch=aarch64&distro=alpine-3.24.2`. The apk purl type defines only the `arch` qualifier. GUAC's schema treats purls with different qualifiers as different packages, and OSV.dev returned no advisories for any apk purl form we tried while the same package queried by OSV ecosystem name returned five (1.20, 1.22, 1.25).
3. **CPEs in the pilot are all guesses.** All 81 candidate CPEs are `syft-generated`; for the 16 standard `cpe` values, 13 vendor:product pairs are not in NVD's CPE dictionary and none of the 16 full names is (NVD CPE API, 2026-10-08). NVD also changed how it maintains CPE data: the legacy XML dictionary was removed on 2025-08-20, and since 2026-04-15 NVD enriches (adds product lists to) only prioritized CVEs (1.7).
4. **purl is in flux.** ECMA-427 1st edition (December 2025) is the published standard; purl-spec v1.1.0 (released 2026-10-07) is the 2nd edition text that Ecma TC54 approved for the December 2026 General Assembly. It removes the word "canonical" from Clause 5. ISO lists ISO/IEC DIS 27056 at stage 40.00 (DIS registered), no longer CD 30.99 as RPT-0004 0.1.0 reported. `vers` is a separate draft Ecma standard (1.1 to 1.3).
5. **The draft model has no identity slots.** In the LinkML draft 0.1.0, Product, ProductInstance and Component are identified only by the opaque `Node.id`; none of the 62 slots holds a purl, CPE, digest, hash, version or commit, although the proposal's prose says "identity-by-hash `ProductInstance`" and "Component (CPE/purl, shared)" (section 2, dimension 6 Q1).
6. **Attestations bind by digest, but storage differs.** in-toto matches subjects "purely by digest"; BuildKit stores SBOM and SLSA attestations as manifests inside the image index (Docker's alpine uses the legacy form, with no `subject`), so Docker Hub's OCI referrers API returns an empty list for the pilot manifest; cosign v3 stores Sigstore bundles as OCI 1.1 referrers; GitHub's `actions/attest` stores them in GitHub's attestations API unless `push-to-registry` is set (1.14 to 1.20).

## 1. Per-source records

### 1.1 purl: ECMA-427 1st edition (December 2025)

| field | value |
|---|---|
| Citation and URL | Ecma International, *ECMA-427: Package-URL (PURL) specification*, 1st edition, December 2025. PDF <https://ecma-international.org/wp-content/uploads/ECMA-427_1st_edition_december_2025.pdf>; landing page <https://www.ecma-international.org/publications-and-standards/standards/ecma-427/> |
| Version pinned and date | 1st edition, adopted by the Ecma General Assembly of December 2025 (PDF p. iii). Newer text: purl-spec v1.1.0, the 2nd edition approved by TC54 for the December 2026 General Assembly (1.2). Landing page lists "ISO/IEC number DIS 27056" (fetched 2026-10-08). |
| Steward | Ecma Technical Committee 54 (TC54); editors listed on p. iv. Community repository github.com/package-url/purl-spec. |
| What it is | The syntax of a purl (`scheme:type/namespace/name@version?qualifiers#subpath`) and a JSON Schema for defining purl types. It defines no individual types. |
| Licence | Ecma copyright notice permitting copying and limited derivative works (p. v); the embedded schema is under a BSD licence ("Software License", p. 31). |
| Library record | none; proposed `ecma-427` (section 6). |
| How checked | PDF downloaded (40 pages), SHA-256 `037180df99e7d7c26d910dc3adb3fa07c4fb787cc4bd29e43634de3802313825`; text extracted with `pdftotext`; `grep` for canonical, order, sort, VERS. Landing page SHA-256 `962938a8230e86f6d874b264e6fe3cb5a965af80ebaefd3c13dbf6ea057fea65`. |

Findings:

- **No type definitions in the standard.** "This Standard specifies the syntax for PURLs and the schema for defining PURL types, but it does not include any specific PURL type definitions, such as maven, pypi or npm." (§1 Scope). Our reading: the rules that make two purls of one package equal live outside the standard, in the type definitions (1.2).
- **Canonical form is required but only partly defined.** "Implementations shall ensure that equivalent PURLs are consistently resolved to the same canonical representation. This includes strict adherence to normalisation and equivalence rules." (§2 Conformance). The core rules: "The type is case insensitive. The canonical form is lowercase." (§5.6.2); leading and trailing slashes "should be stripped in the canonical form" (§5.6.3, §5.6.4, §5.6.7); qualifier keys "shall be composed only of lowercase ASCII letters and numbers, period '.', dash '-' and underscore '_'" and "Each key shall be unique" (§5.6.6). A `grep` of the full text for "sort", "order" and "lexicograph" finds no rule for the order of qualifiers in the canonical form; ordering appears only in non-normative documents (1.2).
- **Per-type normalization is prose.** For each component a type may give `normalization_rules`: "These are plain text, unstructured rules as some require programming and cannot be enforced only with a schema. Tools are expected to apply these rules programmatically." (§6.5.7 and repeated in §6.6.5, §6.7.5, §6.9.5).
- **A version is opaque.** "A version is a plain and opaque string." (§5.6.5). Version comparison is out of scope; ranges are a separate specification: the standard "does not cover ecosystem-specific types or extensions such as PURL Version Ranges (VERS)" (§4).
- **Colon encoding.** "The following characters shall not be percent-encoded: ... the colon ':', whether used as a Separator Character or otherwise" (§5.4). Observation: Syft's SPDX output and the `oci` and `docker` type examples write `sha256%3A…` (1.2, 1.21).
- **The text points elsewhere for the current version.** "The document at https://tc54.org/purl/ is the most accurate and up-to-date Package-URL specification." (About this specification, p. iv).

### 1.2 purl: purl-spec repository v1.1.0 (ECMA-427 2nd edition text) and the type registry

| field | value |
|---|---|
| Citation and URL | package-url/purl-spec, release v1.1.0, <https://github.com/package-url/purl-spec/releases/tag/v1.1.0>; files read at tag `v1.1.0`: `docs/specification/ECMA-427-2nd_Edition-Release_notes.md`, `docs/specification/standard/Clause-2-Conformance.md`, `Clause-5-Package-URL-Specification.md`, `Annex-B-Recommended-Qualifiers.md`, `docs/specification/how-to-build.md`, `types/*-definition.json`; issue #741 |
| Version pinned and date | v1.1.0 published 2026-10-07T23:43:42Z; earlier v1.0.1 (2026-08-03) and v1.0.0 (2025-12-19, the 1st edition baseline). Checked with `gh api repos/package-url/purl-spec/releases` on 2026-10-08. |
| Steward | Package-URL community with Ecma TC54. |
| What it is | The working text of ECMA-427 and the registry of purl types: 42 `types/*-definition.json` files at v1.1.0. |
| Licence | MIT (repository `LICENSE`, "SPDX-License-Identifier: MIT"). |
| Library record | none; fold into `ecma-427` as the 2nd edition note, or a later record linked by `supersedes` (section 6). |
| How checked | Release list JSON SHA-256 `ddd25691a06ea725a0d0e75811f188f1b797b48cebf565ff608268c05fb35c8a`; tree listing at the tag; files: release notes `c9fed55e51a5d536384470d7dce14f480e995b3ce6de6257c56b0fe09e023b2e`, Clause 2 `3c1ca08aa4c646add6d1ef377d6e511660bd928c11306e8ddb15eaf44524397c`, Clause 5 `f7dc36d3e1841adc857527e44aff379ee96040ff23098d82bab060e05fe3c704`, Annex B `d763e9ec357202a38d5251fae4383b3b55820ec10554ee592f482a0539bfedfc`, how-to-build `bafb64309b6507a605e1e69482fb21cb83e938fbe368c1a15258ac867e44b3c9`; type files `apk` `5c583fe68d74ddd3cfd16107f09f4ec9aae98c06c037be82df53d05e1f3c9bc6`, `oci` `0359742850665c2f5bc87d55d678940ce8b5090ca182a9ec53f346dcf6d5a431`, `docker` `9b6af47e1d6f3e1b07ef9f465b4ce5ec01dbc37a968c36b4118ed40edcd5436e`, `golang` `abaf3cf7195329103f6bb2a4e55690cbc31ad3caeca45a242bc1a742075389c2`, `nuget` `685230de2383a39f7629f5716d0a80ae16e22f07270181769ea87184e66b5496`, `pypi` `82b7eb6bef86f4b58fe0c35ba62a1281b249d5e8fa5b149ab1a4c5cff930c534`; issue #741 JSON `8ac51b742cd5692d0cfdb11da117decc49ab35bb0424c947ca77bb1e6f47adba`. |

Findings:

- **The 2nd edition is approved by the committee, not yet adopted.** Release v1.1.0: "This release marks the approval of PURL ECMA-427 2nd Edition by TC54 for submission to the Ecma General Assembly for approval in December 2026." The release notes call it "a minor update" affecting Clauses 3, 5 and 6, Annex A, new Annex B (Recommended Qualifiers) and Annex C (ABNF grammar), and the Bibliography.
- **The type registry is outside the standard.** New Clause 5.7 (release notes): "This Standard includes the Package-URL Type Definition Schema but it does not include the set of current "registered" PURL `type` (JSON format) definition files because there are ongoing additions and changes to these files." Two rules: a purl of a registered type "is invalid if it does not conform to all of the rules from the corresponding PURL `type` definition"; an unregistered type is valid if it meets the core rules, with a warning. The 2nd edition schema (1.1) adds `registered_values` for namespaces and a `recommended` requirement for qualifier keys, both producing warnings, not errors.
- **"Canonical" was removed from Clause 5.** Pull request #1012 (merged 2026-09-17): "Replaced "The canonical form is lowercase." with "The form is lowercase."" and "Replaced "should be stripped in the canonical form." with "should be stripped."". Clause 2 at v1.1.0 still says equivalent purls must resolve "to the same canonical representation" (lines 20 to 21). Our reading: the 2nd edition keeps the conformance duty but no longer calls the stripped and lowercased form "canonical" in Clause 5.
- **Qualifier order is informative only.** Annex B.1 (informative): "Tools that build PURLs should sort multiple **qualifiers** lexicographically by **key**, but this is not expected behaviour for a tool to parse or validate a PURL." The non-normative `how-to-build.md` says "Sort this list of qualifier strings lexicographically".
- **Recommended qualifiers.** Annex B.3 lists `checksum`, `download_url`, `file_name`, `repository_url`, `vcs_url` and `vers`. `distro`, `upstream`, `os_name` and `os_version` (the qualifiers our two Alpine SBOMs use, 1.20) are not in it, and the `apk` type defines only `arch` ("The arch is the qualifiers key for a package architecture."). A `checksum` value takes the form "'lowercase_algorithm:hex_encoded_lowercase_value'" (B.3.1), so a purl can carry a content hash.
- **Container types disagree on which digest.** `docker`: "The version should be the image id sha256 or a tag. Since tags can be moved, a sha256 image id is preferred." `oci`: "The version is the sha256:hex_encoded_lowercase_digest of the artifact and is required to uniquely identify the artifact.", yet its `version_definition.requirement` is `optional`. Our reading: the OCI specification's "ImageID" is the config digest (1.12), so `docker` points at a different digest from the manifest digest that Syft and the attestations use. Both types' examples percent-encode the colon (`sha256%3A244fd47e07d10`), and one `oci` example does not (`sha256:244fd47e07d10`), against ECMA-427 §5.4.
- **Type definitions contain errors that implementations copy.** `golang` at v1.1.0 has `name_definition.case_sensitive: true` and the note "The name shall be lowercased."; its type note says the definition "predates Go modules and has several practical problems". `nuget` has `case_sensitive: true` and the note "Technically the name is case-preserving, but case-insensitive". In issue #741 (open since 2025-11-06) a participant writes that "there are currently multiple errors in the PURL spec package types where what the spec tells you to do is wrong" and "multiple errors in implementations where the outputted PURL is unintentionally not canonical (eg `pkg:pypi` name normalization)" (comment of 2026-07-30), and a CSAF participant reports "a drift in behavior. Some inputs that are accepted by PURL tooling and then normalized are rejected by CSAF because CSAF expects canonical form at validation time" (2026-07-30). These are statements in an issue, not maintainer decisions.
- **Build and parse rules are not in the standard.** A maintainer in #741 (2026-07-29): "How to build, parse or validate documents are part of the PURL and VERS specifications but are not included in either standard because they still need a lot of work."

### 1.3 vers: vers-spec v1.2.1 (draft Ecma standard)

| field | value |
|---|---|
| Citation and URL | package-url/vers-spec, release v1.2.1, <https://github.com/package-url/vers-spec/releases/tag/v1.2.1>; `docs/specification/standard/Clause-5-VERS-Specification.md`, `About.md` |
| Version pinned and date | v1.2.1, 2026-10-07T23:05:13Z; earlier v1.2.0 (2026-09-09), first release v1.0.0 (2026-08-04). |
| Steward | Package-URL community with Ecma TC54 (repository `Ecma-TC54/ECMA-xxx-VERS`). |
| What it is | A URI syntax for version ranges, `vers:<type>/<constraints>`, with per-type comparison rules. |
| Licence | MIT (repository `LICENSE`). |
| Library record | none; proposed `vers-spec` stub (section 6). |
| How checked | Release notes via `gh api`; Clause 5 SHA-256 `e70398a23564721dab92b0d0a76f4f18f0ddd67f9a03de5ed2301cdb32c675ba`, About `81c61bbe224d83af16d6f32e058bae3a4345f514941a01d3e7822c164e8ed50e`; tree at tag `v1.2.1` lists `types/npm-definition.json` and `types/pypi-definition.json` only. |

Findings:

- **Status.** v1.2.1 release notes: "The normative content was approved for submission to the Ecma General Assembly at its December meeting." It is not yet an Ecma standard; the About page still links to placeholder `ECMA-4XX` pages.
- **Scope.** "This edition of the VERS specification only applies to linear versioning use cases; it does not cover tree-based versioning use cases." (Clause 5). Two vers types are registered in the repository at v1.2.1 (npm, pypi); "By convention a **type** should be the same as the PURL **type**" (§5.3.2).
- **How it meets purl.** purl Annex B.3.6 (2nd edition, informative): the `vers` qualifier "is mutually exclusive with use of the **version** component". CycloneDX 1.7 uses vers in `component.versionRange` (external components only) and `vulnerabilities[].affects[].versions[].range` (schema 1.7.2, `definitions.versionRange`: "A version range specified in Package URL Version Range syntax (vers)"). SPDX 3.0.1 has no vers field (`grep` of the model file for "vers:" and "version range": 0 hits).

### 1.4 CPE 2.3 Naming: NIST IR 7695

| field | value |
|---|---|
| Citation and URL | Cheikes, Waltermire, Scarfone, *Common Platform Enumeration: Naming Specification Version 2.3*, NIST Interagency Report 7695, August 2011. <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf>; status page <https://csrc.nist.gov/pubs/ir/7695/final> |
| Version pinned and date | CPE 2.3, August 2011; the CSRC page shows "Final" and "Date Published: August 2011", and no "superseded" or "withdrawn" text (checked 2026-10-08). |
| Steward | NIST (Computer Security Division). |
| What it is | The well-formed CPE name (WFN) data model and its two bindings (URI and formatted string `cpe:2.3:…`). |
| Licence | No licence or copyright statement found in the PDF text (`grep -i copyright`: 0 hits); a US federal publication. |
| Library record | none; proposed `nistir-7695` (FX-1 candidate, section 6). |
| How checked | PDF SHA-256 `01553a4638b21eda10018690b71162e91605d78eb15850f881bd0b2b691ac3f6`; `pdftotext`; CSRC page SHA-256 `f0b4b707bd73b4dfcb3f6cbab4be15b9e22f2e30d3e72f027c8ffa4b6e0f4db6`. |

Findings:

- **A CPE names a class, never an instance.** "WFNs are used solely for product classes. They cannot identify product instances, which are unique, physically discernible entities in the world" (§5).
- **Values are not governed by the naming spec.** Out of scope: "Defining procedures and guidelines for assigning "correct" or "valid" values to attributes of product descriptions or identifiers" (§5). For vendor and product: "Values for this attribute SHOULD be selected from an attribute-specific valid-values list ... Any character string meeting the requirements for WFNs (cf. 5.3.2) MAY be specified as the value of the attribute." (§5.3.3.2, §5.3.3.3). Our reading: anyone can mint a syntactically valid CPE; only the dictionary (1.6) makes one official.
- **Canonical form.** The WFN is described as "an abstract canonical form" (§5.1), and binding is defined "To deterministically transform a logical construct into a machine-readable representation" (§2.1, definition of "Bind"). Unused attributes default to ANY (§5.2); `part` is "a", "o" or "h" (§5.3.3.1).
- **Version text is copied as found.** "Version information SHOULD be copied directly ... from discoverable data and SHOULD NOT be truncated or otherwise modified." (§5.3.3.4). Observation: Syft puts the Alpine release suffix into the CPE version (`1.37.0-r31`, 1.21).

### 1.5 CPE 2.3 Name Matching: NIST IR 7696

| field | value |
|---|---|
| Citation and URL | Parmelee, Booth, Waltermire, Scarfone, *Common Platform Enumeration: Name Matching Specification Version 2.3*, NIST IR 7696, August 2011. <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7696.pdf>; <https://csrc.nist.gov/pubs/ir/7696/final> |
| Version pinned and date | 2.3, August 2011; "Final" on CSRC (2026-10-08). |
| Steward | NIST. |
| What it is | Set-theoretic comparison of a source WFN with a target WFN. |
| Licence | as 1.4. |
| Library record | none; proposed `nistir-7696` stub. |
| How checked | PDF SHA-256 `966eecc18a0d94c1e1c035994a633c4adee790c83d122bad2a79ac7ce4981a45`; CSRC page `2cf06c9c5cd004012ea8b3a8e4af920c0b218da8c6c399299e2fa248daf4a526`. |

Findings:

- **One name against one name.** The specification "provides a method for conducting a one-to-one comparison of a source CPE name to a target CPE name" (Abstract) and can "determine if the source and target names are equal, if one of the names is a subset of the other, or if the names are disjoint" (§1 Introduction).
- **No version ranges.** A `grep` for "range", "versionStart" and "versionEnd" finds only the phrase "a broad range of use cases". Our reading: NVD's `versionStartIncluding` and `versionEndIncluding` match criteria (1.7) are an NVD convention layered on top of CPE 2.3, not part of IR 7696.

### 1.6 CPE 2.3 Dictionary: NIST IR 7697

| field | value |
|---|---|
| Citation and URL | Cichonski, Waltermire, Scarfone, *Common Platform Enumeration: Dictionary Specification Version 2.3*, NIST IR 7697, August 2011. <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7697.pdf>; <https://csrc.nist.gov/pubs/ir/7697/final> |
| Version pinned and date | 2.3, August 2011; "Final" on CSRC (2026-10-08). |
| Steward | NIST; the Official CPE Dictionary is hosted by NVD. |
| What it is | Rules for CPE dictionaries: the Official CPE Dictionary, extended dictionaries, lookups and deprecation. |
| Licence | as 1.4. |
| Library record | none; proposed `nistir-7697` stub. |
| How checked | PDF SHA-256 `3e5b36aa66219f853634613a85674e17ba61edb2053495bfea6d4b1befaaa592`; CSRC page `e9fdf6608d510661daa2c8fccf42130386dbb14a5726e6096befd97392353034`. |

Findings:

- **One authoritative minting point.** "NIST hosts the Official CPE Dictionary, which is the authoritative repository of identifier names." (§1 Introduction). Products "SHOULD only use official identifier names, which are located in the Official CPE Dictionary. If an official identifier name is not available, the product MUST use an identifier name contained within an extended CPE dictionary to which it has access." (§4.1).
- **Names drift by design, through deprecation.** "All identifier names stored within a dictionary MUST be immutable ... Any updates to the product data captured in the identifier name MUST occur through deprecation." (§6.2). "Deprecated Identifier Name: An identifier name that is no longer valid because it has either been replaced by a new identifier name or set of identifier names or was created erroneously." (§2.1). Three deprecation types: "Identifier Name Correction", "Identifier Name Removal" and "Additional Information Discovery", the last one "may be one-to-many" (§6.2). A consumer "MUST first determine if the identifier name is deprecated" before using it (§4.1, item 3).

### 1.7 NVD CPE dictionary, CPE APIs and the 2025 to 2026 NVD changes

| field | value |
|---|---|
| Citation and URL | NVD Products API `https://services.nvd.nist.gov/rest/json/cpes/2.0` and CPE Match API `https://services.nvd.nist.gov/rest/json/cpematch/2.0`; NVD news page <https://nvd.nist.gov/general/news>; NVD "CVE Affected v1.0" schema <https://csrc.nist.gov/schema/nvd/api/2.0/cve_affected_1.0.json> |
| Version pinned and date | API format `NVD_CPE` and `NVD_CPEMatchString` version 2.0; responses timestamped 2026-10-08T17:46 to 18:06 (NVD time). News page as of 2026-10-08 (latest item 2026-08-26). |
| Steward | NIST NVD program. |
| What it is | The Official CPE Dictionary and CVE match criteria, served by API and JSON feeds. |
| Licence | not checked (US government data). |
| Library record | none; proposed `nvd-cpe-apis` (summary bar, data source). |
| How checked | API responses saved and parsed: `cpes/2.0?cpeMatchString=cpe:2.3:a:zlib:zlib:1.3.1` SHA-256 `5ae444dde015a98935afabb5f6314a5193a95a0fcc3c746d3bb2df03bd41ab9f`; `cpematch/2.0?cveId=CVE-2022-37434` `5935cfbbfc58394a99644f58da5be4e8e9e94af232a51dae5d87204e47063937`; 32 dictionary queries for the pilot CPEs (section 7); news page `217828475f30168f73122b897f73358be3013350cd4d5c678b2393c21102cc22`; affected schema `6ad105e90486f4b82a949aef1af369b1ef1ce6720918d31cc158e11a26ff68ff`. |

Findings (spec and announcements):

- **Legacy dictionary files are gone.** "As of August 20th, 2025, the following legacy Data Feed files have been removed ... 1.0 CPE Match Feed ... XML CPE Dictionary Files to include the Official CPE 2.2 and 2.3 Dictionary .zip and .gz" (news, 2025-08-20). The replacement is the 2.0 API and 2.0 JSON feeds, where "the CPE Match 2.0 and CPE Dictionary 2.0 are provided as tar.gz" chunks (news, 2025-05-19).
- **Fewer CVEs get NVD product lists.** "Going forward, NIST will add details, or "enrich," those CVEs that meet certain criteria": KEV CVEs, "CVEs for software used within the federal government" and "CVEs for critical software as defined by Executive Order 14028"; others are "Lowest Priority - not scheduled for immediate enrichment", and backlogged CVEs "with an NVD publish date earlier than March 1, 2026" move to "Not Scheduled" (news, 2026-04-15). In the same item, enrichment is described as adding "severity scores and product lists". Earlier, CVEs published before 2018-01-01 awaiting enrichment were marked "Deferred" (news, 2025-04-02).
- **NVD now also carries CNA "affected" data, including a versionless purl.** From 2026-06-17 the NVD "will also include any provided "affected" information as represented in the CVE Record Format" (news, 2026-05-28 and 2026-06-17). The schema `cve_affected_1.0.json` has `packageURL`: "A Package URL ... The Package URL MUST NOT include a version.", alongside `vendor`, `product`, `packageName`, `collectionURL`, `cpes`, `versions` and others. Our reading: this is data supplied by the CNA and passed through, not NVD's own CPE analysis.

Observations (API, 2026-10-08):

- **Dictionary entries have NVD-minted UUIDs and dates.** The zlib 1.3.1 entry: `cpeName` `cpe:2.3:a:zlib:zlib:1.3.1:*:*:*:*:*:*:*`, `cpeNameId` `FB1C373B-6814-4D38-B660-3F24BFA348B7`, `deprecated: false`, `created` and `lastModified` 2026-09-07T00:39:55.363.
- **Match criteria resolve to dictionary names.** CVE-2022-37434 has 29 match strings; the zlib one is `cpe:2.3:a:zlib:zlib:*:*:*:*:*:*:*:*` with `versionEndIncluding` `1.2.12`, `status` `Active`, and 80 `matches` (dictionary names with `cpeNameId`).
- **The pilot's CPEs are not in the dictionary.** For each of Syft's 16 standard `cpe` values (1.21) we queried the vendor:product pair and the full name: `busybox:busybox` (165 entries), `musl-libc:musl` (93) and `zlib:zlib` (84) exist; the other 13 vendor:product pairs (for example `alpine-keys:alpine-keys`, `libcrypto3:libcrypto3`, `ssl-client:ssl-client`) have 0 entries; 0 of the 16 full names exist, because each version carries the Alpine release suffix (for example `1.3.2-r0`).

### 1.8 SWID and CoSWID tag ids: RFC 9393 (with ISO/IEC 19770-2:2015 metadata)

| field | value |
|---|---|
| Citation and URL | Birkholz, Fitzgerald-McKay, Schmidt, Waltermire, *Concise Software Identification Tags*, RFC 9393, June 2023. <https://www.rfc-editor.org/rfc/rfc9393.txt> |
| Version pinned and date | RFC 9393, Standards Track, June 2023. ISO/IEC 19770-2:2015 (edition 2, published 2015-09-30, stage 90.60 "Close of review") per ISO Open Data (1.31); paywalled, not read. |
| Steward | IETF (Standards Track RFC); ISO/IEC JTC 1/SC 7 for SWID (ISO Open Data). |
| What it is | The CBOR form of SWID tags: one tag per software component release, with a globally unique `tag-id`, entities, links and file payloads. |
| Licence | "Copyright (c) 2023 IETF Trust and the persons identified as the document authors" (BCP 78 boilerplate). |
| Library record | none; proposed `rfc-9393` (FX-1 candidate; dimensions.md already names CoSWID). |
| How checked | Text SHA-256 `6708be37258615edb39de76e32b11439967885d6792f4e2f0ee02de1a0864ebc`; `grep -c -i` for purl, "package url", cpe, gitoid, swhid, omnibor: 0 each. |

Findings:

- **The tag-id is meant to be the global key, without a registry.** "The tag identifier MUST be globally unique. Failure to ensure global uniqueness can create ambiguity in tag use, since the tag-id serves as the global key for matching and lookups." A binary tag-id "MUST be a valid Universally Unique Identifier (UUID)"; a textual one may be "a DNS domain name followed by a "/" and a text string" (§2.3, `tag-id`). "CoSWID is designed to not require a registry of identifiers. As a result, CoSWID requires the tag creator to employ a method of generating a unique tag identifier." and "A collision in tag-ids may result in false positives/negatives in software integrity checks or misidentification of installed software" (§9).
- **A derived identifier names the creator too.** For SWIMA, "TAG_CREATOR_REGID "_" "_" UNIQUE_ID", where TAG_CREATOR_REGID is the `reg-id` of the tag-creator entity (§6.7).
- **Tag version is not product version.** `tag-version` "allows a CoSWID tag producer to correct an incorrect tag previously released without indicating a change to the underlying software component the tag represents" (§2.3). `software-version` with a `version-scheme` (multipartnumeric, alphanumeric, decimal, semver and others) carries the release (§2.3, §4.1).
- **A product line has its own id.** `persistent-id`: "A globally unique identifier used to identify a set of software components that are related. Software components sharing the same persistent-id can be different versions." (§2.8, `software-meta-entry`). Our reading: this is the closest SWID concept to tmodel's Product, as opposed to a ProductInstance.
- **File hashes, sometimes without an algorithm.** The `hash-entry` uses IANA "Named Information Hash Algorithm Registry" ids: "other hash algorithms MUST NOT be used. If the hash-alg-id is not known, then the integer value "0" MUST be used. This allows for conversion from ISO SWID tags [SWID], which do not allow an algorithm to be identified for this field." (§2.9.1). §9 warns: "The CoSWID format allows the use of hash values without an accompanying hash algorithm identifier. This exposes the tags to some risk of cross-algorithm attacks."
- **No purl, CPE, gitoid or SWHID field** (counts above). IANA lists the `swid` and `swidpath` URI schemes, defined in RFC 9393 §5, as "Provisional" (1.31).

### 1.9 OmniBOR specification (v0.1 tag and v0.2 draft) and the gitoid URI scheme

| field | value |
|---|---|
| Citation and URL | OmniBOR Working Group, *OmniBOR Specification*, <https://github.com/omnibor/spec> (`spec/SPEC.md`, `spec/GITOID_URI.txt`); IANA provisional registration <https://www.iana.org/assignments/uri-schemes/prov/gitoid> |
| Version pinned and date | Two texts: tag `v0.1` (released 2024-10-13), header "Version 0.1, Status Draft"; and `main` at commit `daf090f6` (2025-11-17), header "Version 0.2, Status Draft". |
| Steward | OmniBOR Working Group (community). IANA registrant listed as Ed Warnicke; IANA's page names "Scheme Creator: GitBOM", the repository copy names "Scheme Creator: OmniBOR". |
| What it is | Artifact identifiers computed as git blob object ids, and Input Manifests listing the artifact ids of every build input, forming an artifact dependency graph. |
| Licence | Community Specification License 1.0 (`LICENSE.md`). |
| Library record | none; proposed `omnibor-spec` stub (draft; see section 6). |
| How checked | `SPEC.md` at main SHA-256 `beb2dd6f45c1de7582a41e7e8f176b284ee6bc1739e9e6334fb863db4e08fc47`, at v0.1 `d81992650a9feed63a128e5e2c066df86d91e3d97e4e75991e0fe6323567d698`; `GITOID_URI.txt` `db896f786d86820c32290b92ed5c7ed4ded8b477eae39f13135cd6fbbc14f637`; IANA page `21c079d43e118650e89255e52374399991b2d7db69f0ebeda367d3acb97b0a9a`; commit history of `spec/SPEC.md` via `gh api`. |

Findings:

- **Which bytes.** The gitoid of a byte array is the hash of a git object: "A git object is formed by prepending an object header to the object's contents. A git object header consists of: <git object type>" "<size of contents as decimal string>"\0"" (gitoid registration, "Scheme semantics"). Syntax: `gitoid:<git object type>:<hash algorithm>:<hash value>`, with types blob, tree, commit, tag and algorithms sha1 and sha256.
- **The OmniBOR id changed between versions.** v0.1 allowed two identifier types, `gitoid:blob:sha1` and `gitoid:blob:sha256`. The v0.2 draft: "We have decided to only permit the use of SHA-256 as a hash algorithm for Artifact Identifiers for OmniBOR." (§6.1.1). It also adds newline normalization (commit `aa932090`, "feat: Add newline normalization to spec.", 2025-07-28): "Artifact Identifier construction _must_ normalize all Windows-style newlines to Unix-style" "before being hashed", "regardless of any information about the artifact being identified" (§6.1.2). Our reading: for a file with CRLF line endings, the v0.2 id is not the git blob id of the file's bytes, and two files that differ only in line endings get the same id, although §5.2 says "Two artifacts are equivalent if and only if their binary representations are equal".
- **SHA-1 is ambiguous.** "`gitoid:blob:sha1` may describe either SHA-1 or SHA-1CD depending on the version of Git being used" (§6.1.1).
- **Formats lag the spec.** CycloneDX 1.7.2's `omniborId` example is `gitoid:blob:sha1:a94a8fe5…` (1.11), which v0.2 no longer permits; SPDX 3.0.1's `gitoid` type links to OmniBOR commit `eb1ee5c` (1.11).
- **IANA status.** `gitoid` is "Provisional"; the registration's interoperability considerations read "Unknown, use with care." (1.31).

### 1.10 SWHID specification v1.2 and ISO/IEC 18670:2025

| field | value |
|---|---|
| Citation and URL | SWHID Contributors, *The SWHID Specification Version 1.2*, <https://www.swhid.org/specification/v1.2/> (clauses 0, 1, 4, 5, 6); repository <https://github.com/swhid/specification>. ISO/IEC 18670:2025, *SoftWare Hash IDentifier (SWHID) Specification V1.2* (title in ISO Open Data, after the "Information technology" prefix). |
| Version pinned and date | v1.2 (repository tag `v1.2`); ISO/IEC 18670:2025 published 2025-04-23, edition 1, 14 pages, stage 60.60 (ISO Open Data, 1.31). |
| Steward | SWHID contributors (Software Heritage community); ISO/IEC JTC 1. |
| What it is | Intrinsic identifiers for content, directories, revisions, releases and snapshots, computed as SHA-1 over git-style serializations, plus qualifiers that give context. |
| Licence | Community Specification License 1.0 (page footer and `LICENSE.md`). ISO text: paywalled, not read. |
| Library record | none; proposed `swhid-spec-1-2` (FX-1 candidate if Table 3 keeps it; short text) and `iso-iec-18670-2025` stub. |
| How checked | Pages fetched and text extracted: index `9712ab74cec367a130a293526c488c508977f95be487f04484ecddd77e660ded`, Scope `64f4183290529055c8108ecdb4294861c5f1a6c9c9a45bcea72ab9a8ebec000a`, Syntax `27221f48cc9ff99338887e6e4a0f3e28be661934c7e25d67dc3706063d1feca6`, Core identifiers `8a6a0153dbbf47f063470b20f06ebccbae07330123f3518833c61b5288479b12`, Qualified identifiers `457a09f64a7d975d2c099a3443de77beb6bb39a74a6b58fcffe0e1b498ce6b7d`; issues listed with `gh api`. |

Findings:

- **Computed, no registry.** SWHIDs "can be computed using cryptographically strong functions directly from the digital objects they refer to, by anyone that has access to a copy of those objects. This enables decentralised and independent verification of integrity, without relying on a registry or a central authority." (§1). The same sentence is in ISO's public scope text for ISO/IEC 18670:2025 (ISO Open Data `scope.en`).
- **Object types.** Core identifier `swh:1:<object_type>:<object_id>` with `snp`, `rel`, `rev`, `dir`, `cnt`; `<object_id>` is 40 hex digits (§4). For a content, "the SHA1 of the byte sequence obtained by concatenating: the ASCII string "blob" (4 bytes), an ASCII space, the length of the content as ASCII-encoded decimal digits, a NULL byte, and the actual content of the file. No metadata is used" (§5.2). Our reading: a `cnt` id equals the git SHA-1 blob id and the `gitoid:blob:sha1` value of the same raw bytes, and differs from an OmniBOR v0.2 id.
- **Revisions include metadata.** A `rev` id hashes author, committer, timestamps, parents and message as well as the tree (§5.4), so one source tree has many revision ids.
- **Git compatibility is not promised.** "Git compatibility is practical, but incidental and is not guaranteed to be maintained in future versions of this specification, nor across different versions of Git." (§5.8).
- **Qualified identifiers.** Fragment qualifiers `lines` and `bytes` (contents only) and context qualifiers `origin`, `visit`, `anchor`, `path` (§6). "A conformant implementation shall not generate invalid qualifiers or qualifier combinations, and shall ignore them if present" (§6.1).
- **Documented defects.** Issue #72 (closed 2026-09-19) restored the directory mode `'40000'` because the six-byte form `'040000'` in §5.3 "does not match any directory identifier in the archive" and the published site "still serves the six-byte form" at that time; our fetch on 2026-10-08 shows `'40000'`. Issue #70 (open, 2026-09-19): "A directory containing a submodule therefore has no serialisation under 5.3, and consequently no computable SWHID." Whether ISO/IEC 18670:2025 carries the same text was not checked (paywalled).

### 1.11 Hashes in CycloneDX 1.7 and SPDX 3.0.1 ("a hash of which bytes")

| field | value |
|---|---|
| Citation and URL | CycloneDX JSON schema at tag `1.7.2`, <https://raw.githubusercontent.com/CycloneDX/specification/1.7.2/schema/bom-1.7.schema.json>; SPDX 3.0.1 model <https://spdx.org/rdf/3.0.1/spdx-model.ttl> and class pages (Hash, PackageVerificationCode, ContentIdentifier, ExternalIdentifier, Build); CycloneDX issue #96 <https://github.com/CycloneDX/specification/issues/96> |
| Version pinned and date | CycloneDX 1.7.2 (release 2026-09-17); SPDX 3.0.1 (2024-12-17). Same files and hashes as RPT-0005's pin. |
| Steward | OWASP CycloneDX with Ecma TC54; SPDX project (Linux Foundation). Formats in depth are agent 1's; this record covers only identifier and hash fields. |
| What it is | Where each format carries identifiers and hashes, and what it says about them. |
| Licence | CycloneDX specification repository Apache-2.0; SPDX per library record `spdx-3-0-1`. |
| Library record | `cyclonedx-1-7` (queued), `spdx-3-0-1` (queued); agent 1 owns their Table 9 rows. |
| How checked | CycloneDX schema SHA-256 `73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce` (parsed with `jq`); SPDX model `30ebb4af2d70a9809044ef46f44cc3dc5125226d70f818a50ed2e1d5f404c593` (parsed with `python3`); class pages: Hash `896f159e1797f984f7ca0e4f6e172364af0c51474706294fbef81ed984a5124d`, PackageVerificationCode `aa723bbf6559eb52d43d9e998e2561a51dccad7210ec5f2e72ae29b8917a7c1f`, ContentIdentifier `774cde8deff89e534035c844e89bb82c180e410d56c2027e0bc2aa64e235c46a`, ExternalIdentifier `b46364d1d10bb35b3ecd201f395586b03d4962ab39d58015ff41d5cb325ff87a`, Build `6c762d6d80e4d493886532c3ed95bb3145ad0394f8ae38a14e65957a2f53d35c`. |

Findings:

- **CycloneDX does not say which bytes.** `components[].hashes`: "The hashes of the component."; `hash.alg`: "The algorithm that generated the hash value." (14 values from MD5 to Streebog-512); `hash.content` must match a hex pattern of 32, 40, 64, 96 or 128 characters. Issue #96, open since 2021-10-28: "What I am missing is for **what** the hash has been calculated, i.e. for which file." A maintainer replied: "We follow whatever the convention is for the particular ecosystem ... But that should be more clear. For NuGet it's the hash of the nupkg file itself. Note, this differs to the hash in a package lock file".
- **CycloneDX identity fields are claims pointing at outside specs.** `purl` "must be valid and conform to the specification defined at: https://github.com/package-url/purl-spec"; `cpe` "must conform to the CPE 2.2 or 2.3 specification"; `omniborId` must conform to the IANA gitoid registration; `swhid` points to `docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html`, not to swhid.org or ISO/IEC 18670; `swid` requires `tagId` and `name`. Each begins "Asserts the identity of the component". None has a JSON Schema `pattern`. `evidence.identity` lists `field` values `group`, `name`, `version`, `purl`, `cpe`, `omniborId`, `swhid`, `swid`, `hash`, with `confidence` and `methods[].technique` (for example `hash-comparison`, `manifest-analysis`, `attestation`).
- **SPDX `Hash` does not say which bytes either.** Class Hash: "A mathematically calculated representation of a grouping of data."; `hashValue`: "The result of applying a hash algorithm to an Element." Our reading: an Element is a logical object, so the bytes hashed are left to the producer.
- **SPDX defines the bytes in one place, and discourages it.** `PackageVerificationCode` gives an algorithm over sorted per-file hashes, excluding listed files, and says: "Use of this verification code method is discouraged except for scenarios where the contentIdentifier property on Artifact can not be used." `ContentIdentifier`: "a canonical, unique, immutable identifier of the content of a software artifact" with types `gitoid` and `swhid` only.
- **SPDX external identifiers.** `ExternalIdentifierType` includes `cpe22`, `cpe23` (linked to NIST IR 7695), `packageUrl`, `swid` ("Concise Software Identification (CoSWID) tag, as defined in RFC 9393 Section 2.3"), `gitoid` and `swhid`. The `gitoid` text says gitoids of artifacts "should be recorded in the SPDX 3.0 SoftwareArtifact's contentIdentifier property" and gitoids of Input Manifests in `externalIdentifier`. The `swhid` text still says "(ISO/IEC DIS 18670)", which ISO published on 2025-04-23. `ExternalIdentifier` carries an optional `issuingAuthority` ("An entity that is authorized to issue identification credentials.").
- **SPDX Build.** "Class that describes a build instance of software/artifacts"; of its own properties only `buildType` is required (1..1); "buildStartTime and buildEndTime are optional, and may be omitted to simplify creating reproducible builds." (re-check of RPT-0004 0.1.0 §6).

### 1.12 OCI Image Format Specification v1.1.1

| field | value |
|---|---|
| Citation and URL | Open Container Initiative, *OCI Image Format Specification*, v1.1.1, <https://github.com/opencontainers/image-spec/tree/v1.1.1>: `descriptor.md`, `image-index.md`, `manifest.md`, `config.md`, `annotations.md`, `artifacts-guidance.md` |
| Version pinned and date | v1.1.1, released 2025-03-03 (latest release and tag on 2026-10-08). |
| Steward | Open Container Initiative (Linux Foundation project). |
| What it is | Content-addressed image formats: descriptors with digests, image indexes (multi-platform), image manifests, configs and layers. |
| Licence | Apache-2.0. |
| Library record | none; proposed `oci-image-spec-1-1-1` (FX-1 candidate if the contract relies on its digest rules). |
| How checked | Files at tag: descriptor `89399b5ffabfeb9688b66de9afcf08b60691710d94d0f5b061cb30e6fbc75428`, image-index `abbd4ecefe1d85588ae98393600a20b618cc190d630bb534d596c9a642584bf9`, manifest `fc35d252c5cc192ce972bbd52b560184ba427a8a374107fc5cdd7442034cd867`, config `0504e056297a41dd14cf2ec276d53fab4321d2b08a3e7fd98b2f87792f3f0a57`, annotations `e080458d943cb404387adbb1a0d5b95362340203ee98ab50525f07aef7cb02ad`, artifacts-guidance `2c716295bf463cdde920511a0e8fd1498091ade4d782ae6c48ad04a202795803`; release history via `gh api`. |

Findings:

- **A digest is a hash of exact bytes.** "The _digest_ property of a Descriptor acts as a content identifier, enabling content addressability." Grammar `digest ::= algorithm ":" encoded`; pseudo-code `let D = '<alg>:' + Encode(H(C))` over "Content `C` is a string of bytes." (descriptor.md, Digests). "compliant implementations SHOULD use SHA-256" and "Implementations MUST implement SHA-256 digest verification for use in descriptors." It also allows "canonicalization of the underlying content to ensure stable content identifiers" (MAY).
- **Index versus manifest versus config.** "The image index is a higher-level manifest which points to specific image manifests, ideal for one or more platforms." (image-index.md). "Each image's ID is given by the SHA256 hash of its configuration JSON." (config.md, ImageID). Our reading: an image has at least three digests at different levels, and the pilot image shows five (1.20).
- **Artifacts and `subject`.** `artifactType` "contains the type of an artifact when the manifest is used for an artifact"; `subject` "specifies a descriptor of another manifest. This value defines a weak association to a separate Merkle Directed Acyclic Graph (DAG) structure, and is used by the `referrers` API" (manifest.md, also on image-index.md).
- **The separate "artifact manifest" was dropped before 1.1.0.** `artifact.md` exists at tag `v1.1.0-rc2` and not at `v1.1.0-rc3` or later; pull request #999 ("Remove artifact manifest", merged 2023-04-13): "The artifact manifest does not confer any additional benefits beyond the existing image manifest. Drop it for the sake of backward compatibility." Artifacts now use the image manifest (`artifacts-guidance.md`).
- **Build identity can travel as annotations.** `org.opencontainers.image.revision` "Source control revision identifier for the packaged software", `org.opencontainers.image.source`, `org.opencontainers.image.version`, `org.opencontainers.image.created`, `org.opencontainers.image.base.digest` (annotations.md). The pilot image's index carries `version`, `revision` and `source` on each platform descriptor (1.20).

### 1.13 OCI Distribution Specification v1.1.1 (tags and the referrers API)

| field | value |
|---|---|
| Citation and URL | Open Container Initiative, *OCI Distribution Specification*, v1.1.1, <https://github.com/opencontainers/distribution-spec/blob/v1.1.1/spec.md> |
| Version pinned and date | v1.1.1, released 2025-01-29 (latest release and tag on 2026-10-08). |
| Steward | Open Container Initiative. |
| What it is | The registry HTTP API: pull and push by tag or digest, tag listing, and the referrers API. |
| Licence | Apache-2.0. |
| Library record | none; proposed `oci-distribution-spec-1-1-1` (FX-1 candidate together with 1.12). |
| How checked | `spec.md` SHA-256 `360b29820869bfaac5f73ebfa30669c9172c069ef619f8c6689acc3bcef6f719`; live calls against Docker Hub (1.20). |

Findings (re-check of RPT-0004 0.1.0 §6 quotes, all found verbatim):

- **Definitions.** "**Digest**: a unique identifier created from a cryptographic hash of a Blob's content." "**Tag**: a custom, human-readable pointer to a manifest. A manifest digest may have zero, one, or many tags referencing it." (Definitions). "If the `<reference>` part of a manifest request is a digest, clients SHOULD verify the returned manifest matches this digest." (Pulling manifests).
- **A registry may answer with a different digest.** "The `Docker-Content-Digest` header, if present on the response, returns the canonical digest of the uploaded blob which MAY differ from the provided digest." (Pushing blobs).
- **Referrers API.** `GET /v2/<name>/referrers/<digest>`, optionally `?artifactType=`; "If the registry supports the referrers API, the registry MUST NOT return a `404 Not Found` to a referrers API requests." and "If a query results in no matching referrers, an empty manifest list MUST be returned." (Listing Referrers). Without it, clients fall back to a tag `<alg>-<ref>` ("Referrers Tag Schema"), and "Protection against race conditions is the responsibility of clients and end users".

### 1.14 in-toto Attestation Framework v1.2.0

| field | value |
|---|---|
| Citation and URL | in-toto, *in-toto Attestation Framework*, release v1.2.0, <https://github.com/in-toto/attestation/tree/v1.2.0/spec>: `v1/statement.md`, `v1/resource_descriptor.md`, `v1/digest_set.md`, `v1/envelope.md`, `v1/bundle.md`, `predicates/spdx2.md`, `predicates/spdx3.md`, `predicates/cyclonedx.md` |
| Version pinned and date | Release v1.2.0, 2026-03-18 (Statement type `https://in-toto.io/Statement/v1`). Previous v1.1.2 (2025-06-14). |
| Steward | in-toto project (CNCF). |
| What it is | Layers for signed software attestations: Envelope (DSSE recommended), Statement (subject digests plus predicate type), Predicate, Bundle. |
| Licence | Apache-2.0 (`LICENSE`). |
| Library record | `in-toto-attestation-v1` (queued; summary empty; `url` points to in-toto.io and `version` is empty) and `in-toto-envelope-v1` (stub; its `topic` is `post-quantum-migration`, which looks misfiled). Proposed: FX-1 for `in-toto-attestation-v1`, pinned to v1.2.0. |
| How checked | Files at tag: statement `cbe684a18b812b8b613d9202eb43b2ea24477f91a2ad6ca5be935185a455ebea`, resource_descriptor `bee71bedd6a957771233cbbe6494144157b865992e53cc91d607a8e02a34c58a`, digest_set `0b1889fdea7f6d623b41555632aedf04ee4398cf02a32002060608c75ebb038e`, envelope `c02c65880ccc117bbdecc6c916d5108541c1a864de67f8f9082efbaf15265d11`, bundle `e90a4419c8913f91ad8ec34ce810404130400faf8f22866607c5083bcacee690`, spdx2 `4aa2f2005dc51d29b9146efb3baeb6d00c2408d662bf9b50a0dd18ac8206ca60`, spdx3 `4297dc7a4991252439510b707e86c4264f4e035644fc8ad3942de72eb233bf59`, cyclonedx `62859de726161fe8ee96da4b4bed8918c364abfaab9ce58830472495b24612f5`. |

Findings:

- **Subjects are matched by digest only.** `subject`: "Each element MUST have `digest` set." "Subjects are assumed to be _immutable_". "IMPORTANT: Subject artifacts are matched purely by digest, regardless of content type." (statement.md). The `name` "may be used as an identifier to distinguish this artifact from others within the `subject`"; its semantics "are up to the producer and consumer".
- **Matching rule for digest sets.** "Two DigestSets SHOULD be considered matching if ANY acceptable field matches." "Consumers MUST only accept algorithms that they consider secure and MUST ignore unrecognized or unaccepted algorithms." (digest_set.md, Guidelines). Standard algorithms (`sha256`, `sha512`, `sha1`, `md5`, and others) are hex "for cases when the method of serialization is obvious or well known"; `gitCommit`, `gitTree`, `gitBlob`, `gitTag` are computed "over `<type> SP <size> NUL <content>`"; `dirHash` is the Go module directory hash. Non-cryptographic ids (for example an AWS image ARN) are allowed "so long as the risk of the object being mutated is acceptable for the application".
- **Which field a digest matches is left to the predicate.** "The field that consumers are expected to match the `digest` against is ultimately determined by the predicate type, and SHOULD be documented by the predicate specification." (resource_descriptor.md, Semantics). The SBOM predicates do not document it: "The `subject` contains whatever software artifacts are to be associated with this SPDX document." (spdx2.md; same sentence in spdx3.md and, for "this CycloneDX BOM document", cyclonedx.md).
- **SBOM predicate types.** SPDX 2: "Type URI: https://spdx.dev/Document" and "https://spdx.dev/Document/v2.3"; SPDX 3 (new in v1.2.0): "https://spdx.dev/Document/v3"; CycloneDX: "Type URI: https://cyclonedx.org/bom", "Version: 1.4", while its example uses `https://cyclonedx.org/bom/v1.4`. Our reading: the CycloneDX predicate page is internally inconsistent about whether the version is in the URI.
- **Envelope rules.** DSSE is recommended; the envelope "MUST support the inclusion of multiple signatures in a single envelope", so "The Sigstore Bundle, while supporting DSSE, is not currently ITE-5 compliant because it requires a _single signature_ in the envelope." `payloadType` "MUST be set to `application/vnd.in-toto.<predicate>+json` or to `application/vnd.in-toto+json`" (envelope.md). Bundles are JSON Lines, "SHOULD use the suffix `.intoto.jsonl`", and "The Bundle is not authenticated as a whole" (bundle.md).

### 1.15 SLSA v1.2 build provenance (library record `slsa-1-2`, FX-1)

| field | value |
|---|---|
| Citation and URL | SLSA Specification v1.2, <https://slsa.dev/spec/v1.2/>; read from the library record's distilled files: `library/records/openssf/slsa-1-2/distilled/normative.md`, `messages.yaml`, `design-notes.md` |
| Version pinned and date | v1.2, released 2025-11-24 (record). Still current on 2026-10-08: slsa.dev/spec/ reads "Status: Approved" and "This is Version 1.2 of the SLSA specification" (page SHA-256 `46edf628a901c268261cf8b72a1b478926ae9b2db050fa21194c914e7417e3ae`). |
| Steward | OpenSSF SLSA project. |
| What it is | Supply-chain integrity levels, with build provenance (`https://slsa.dev/provenance/v1`) and VSAs carried in in-toto Statements. |
| Licence | per record (not re-checked). |
| Library record | `slsa-1-2`, `status: distilled`, FX-1 passes extract, verify and cross-check (2026-10-02); `reviewed_by` empty. No action proposed. |
| How checked | Distilled files read locally (not re-extracted, as instructed); one live check of the version page. |

Findings:

- **Artifacts include images and firmware.** Terminology: "Artifact | An immutable blob of data ... | A file, a git commit, a directory of files (serialized in some way), a container image, a firmware image." (normative.md, Build: Terminology).
- **Verification is a digest match.** "Verify that statement's `subject` matches the digest of the artifact in question." (normative.md, Verifying artifacts, step 2).
- **The source revision is a dependency.** "a build that takes a git repository URI as a parameter might record the specific git commit that the URI resolved to as a dependency." `resolvedDependencies`: "Unordered collection of artifacts needed at build time. Completeness is best effort, at least through SLSA Build L3." (normative.md, Build: Provenance). Re-check of RPT-0004 0.1.0 §6: the quote is verbatim.
- **Fields useful as identity.** `Builder.id` ("URI indicating the transitive closure of the trusted build platform"), `BuildMetadata.invocationId`, `startedOn`, `finishedOn`; `ResourceDescriptor` with `digest` as "map (algorithm→hex string), e.g. sha256, sha512, gitCommit" (messages.yaml).
- **Attach to artifacts, publish somewhere, lookup undefined.** "Attestations SHOULD be bound to artifacts, not releases." "Producers MUST publish attestations in at least one place, and SHOULD publish attestations in more than one place" (normative.md, Distributing provenance). In the attestation model's recommended suite, "Storage/Lookup | **TBD**" (normative.md, Software attestations).
- **Existing design note.** The record's `design-notes.md` (not human-reviewed) proposes: "When radar hands evidence over (ADR-0001), we keep the attestation as an external `Entity` with a digest and a `verified_by` edge to the conformance result. We do not re-model DSSE inside tmodel."

### 1.16 Sigstore bundle v0.3 (protobuf-specs v0.5.2)

| field | value |
|---|---|
| Citation and URL | Sigstore, `protos/sigstore_bundle.proto`, <https://github.com/sigstore/protobuf-specs/blob/v0.5.2/protos/sigstore_bundle.proto> |
| Version pinned and date | Repository tag `v0.5.2` (commit dated 2026-08-21; the repository publishes tags, not GitHub releases). Bundle media type version 0.3. |
| Steward | Sigstore (OpenSSF). |
| What it is | One file with a signature or a DSSE envelope plus everything needed to verify it (certificate or key hint, transparency log entries, timestamps). |
| Licence | Apache-2.0. |
| Library record | none (related: `sigstore-2022` stub, `sigstore-threat-model` stub). Proposed `sigstore-bundle-v0-3` stub. |
| How checked | File SHA-256 `bf8d01cc4a52f8485f5eb795f499396f2e05cc4e0e45d131375b4c780b190792`. |

Findings:

- **Current version.** "The current version as specified by this file is: application/vnd.dev.sigstore.bundle.v0.3+json"; clients must also accept `application/vnd.dev.sigstore.bundle+json;version=0.1`, `0.2` and `0.3`.
- **One signature per envelope.** "DSSE envelopes in a bundle MUST have exactly one signature." and "a client MUST reject an envelope if the number of signatures is not equal to one." This is the limitation in-toto's envelope spec notes (1.14).

### 1.17 BuildKit attestation storage and SBOM attestations (v0.34.0)

| field | value |
|---|---|
| Citation and URL | moby/buildkit, `docs/attestations/attestation-storage.md`, `sbom.md`, `slsa-provenance.md` at tag `v0.34.0`, <https://github.com/moby/buildkit/tree/v0.34.0/docs/attestations> |
| Version pinned and date | BuildKit v0.34.0, released 2026-10-07T23:37:31Z (latest release on 2026-10-08). |
| Steward | Moby project (Docker). |
| What it is | How BuildKit generates SBOM and SLSA provenance attestations and stores them next to an image. |
| Licence | Apache-2.0. |
| Library record | none; proposed `buildkit-attestations` (tool documentation, summary bar). |
| How checked | storage `9103a45463fbfdacfc34ccf365f8036179b628ccd4762ffc8cdd1125cdbeee9d`, sbom `36723f5595edd4c225c9c55e6c8b3f992a0361da0db8ee0e34e45ae4dadb018f`, slsa-provenance `318033c93bd0af5e567d1b046966a8f9f700bac94ff379968ebc83020c418cea`. |

Findings:

- **Stored inside the image index.** "Attestations are stored as manifest objects in the image index." "BuildKit stores attestations as OCI artifacts when OCI media types are enabled. Set the image exporter option `oci-artifact=false` to use the legacy attestation image manifest format." With OCI artifacts, "the manifest `artifactType` is set to `application/vnd.docker.attestation.manifest.v1+json`, the `subject` descriptor points to the target image manifest". The index descriptor gets `platform` `unknown/unknown` and annotations `vnd.docker.reference.type: attestation-manifest` and `vnd.docker.reference.digest`.
- **Subject binding.** "The subject of the attestation should be set to be the same digest as the target manifest described in the Attestation Manifest Descriptor, or some object within."
- **SBOM format and default scanner.** "All SBOMs generated by BuildKit are wrapped inside in-toto attestations in the SPDX JSON format", by default using `docker/buildkit-syft-scanner`; "By default, only the final build result is scanned". Example subject name: `pkg:docker/<registry>/<image>@<tag/digest>?platform=<platform>`.
- **Provenance versions.** BuildKit supports SLSA provenance v0.2 and v1, and the `version` option defaults to `v1` (slsa-provenance.md, options table). Observation: the official alpine image still carries v0.2 (1.20).

### 1.18 cosign v3.1.3 (`cosign attest`)

| field | value |
|---|---|
| Citation and URL | sigstore/cosign v3.1.3: `doc/cosign_attest.md`, `specs/ATTESTATION_SPEC.md`, `specs/SBOM_SPEC.md`, `pkg/cosign/attestation/attestation.go`; v3.0.0 and v3.0.1 release notes; in-toto-golang v0.11.0 `in_toto/attestations.go` and SLSA provenance constants |
| Version pinned and date | cosign v3.1.3, released 2026-08-06 (latest on 2026-10-08); depends on `github.com/in-toto/attestation v1.2.0` and `github.com/in-toto/in-toto-golang v0.11.0` (`go.mod`). |
| Steward | Sigstore (OpenSSF). |
| What it is | CLI that signs and attaches attestations to container images in OCI registries. |
| Licence | Apache-2.0. |
| Library record | none; proposed `cosign` (tool, summary bar). |
| How checked | cosign_attest `b4ab5579334a70399ee24a863964a75c11305d5a48a50b5a77c445c52a238fde`, ATTESTATION_SPEC `45f45cf39fda629a136bd82adb71052e4353efc6156bb2cb8e66139fb7ae5fbc`, SBOM_SPEC `5b62d34d52f553d3d040e0434f394ac3acaa46fc60d584f7541c8f514ef3426a`, attestation.go `59c5f7dfb69b75a52f8df6b69467783387bd12758422dc204f5011664eeec53e`, in-toto-golang attestations.go `dbb1b66dade23c7438b57ad9dbad0d034744313c56e53559d19dfc445cc300b3`, SLSA v0.2 constants `d8956c1ecfe5709c80d4b5fa49b06f6437ca11017205b380580c47b3145bb348`, SLSA v1 constants `af5a35623172a636564c48da28efc1926c96c3480136e92a4af6d14c828e04df`. |

Findings:

- **Predicate types.** `--type` "specify a predicate type (slsaprovenance\|slsaprovenance02\|slsaprovenance1\|link\|spdx\|spdxjson\|cyclonedx\|vuln\|openvex\|custom) or an URI (default "custom")" (cosign_attest.md). In the code, `slsaprovenance` and `slsaprovenance02` both produce SLSA v0.2 (`https://slsa.dev/provenance/v0.2`), `slsaprovenance1` produces `https://slsa.dev/provenance/v1`, `spdx` and `spdxjson` produce `https://spdx.dev/Document`, `cyclonedx` produces `https://cyclonedx.org/bom`, `vuln` produces `https://cosign.sigstore.dev/attestation/vuln/v1`, `openvex` produces `https://openvex.dev/ns`, and the default custom type is `https://cosign.sigstore.dev/attestation/v1` (attestation.go, `switch opts.Type` at lines 172 to 195; constants in in-toto-golang v0.11.0).
- **Storage changed in v3.** v3.0.0 notes: new capabilities are "on by default", including "the standardized bundle format (`--new-bundle-fomat`)" [sic] and "container signatures stored as an OCI Image 1.1 referring artifact". The v3.0.1 note: "the `--bundle` flag ... has moved from optional to required in v3."
- **Subject check.** "When verifying an attestation for a container image, implementations MUST verify the relationship between the `subject` field and the container image." (ATTESTATION_SPEC.md).
- **SBOM attachments are deprecated.** "**WARNING**: SBOM attachments are deprecated and support will be removed in a Cosign release soon" ... "Instead, please use SBOM attestations." (SBOM_SPEC.md).

### 1.19 GitHub `actions/attest` v4.2.2 (and `actions/attest-sbom` v4.1.0)

| field | value |
|---|---|
| Citation and URL | <https://github.com/actions/attest/blob/v4.2.2/README.md>; <https://github.com/actions/attest-sbom/blob/v4.1.0/README.md> |
| Version pinned and date | attest v4.2.2 (2026-08-04); attest-sbom v4.1.0 (2026-03-18). |
| Steward | GitHub. |
| What it is | GitHub Actions that create Sigstore-signed in-toto attestations (provenance, SBOM, custom). |
| Licence | MIT (actions/attest). |
| Library record | none; proposed `github-actions-attest` (vendor documentation, summary bar). |
| How checked | attest README `c513a2a22ce3fa07b67216d36db2c1552be51f7391fe81266f6f1a4cee8da5d6`; attest-sbom README `ffaf8c252bee439e56532aca6c8f2a7815fdeac873462eb8ab2f2194c5efebe5`. |

Findings:

- **Digest, not tag.** "Do NOT include a tag as part of the image name -- the specific image being attested is identified by the supplied digest."
- **Where it is stored.** "Attestations are saved in the JSON-serialized Sigstore bundle format." `push-to-registry` "Defaults to false" and "Requires that the resolved subject is a single fully-qualified OCI image reference with a SHA-256 digest". attest-sbom: the attestation "will be uploaded to the GH attestations API"; SBOMs "must be in either the SPDX or CycloneDX JSON-serialized format"; the action "is being deprecated in favor of `actions/attest`".

### 1.20 Live registry check: `library/alpine` on Docker Hub (the pilot image)

| field | value |
|---|---|
| Citation and URL | Docker Hub registry API, `https://registry-1.docker.io/v2/library/alpine/…` (anonymous pull token) |
| Version pinned and date | Queried 2026-10-08 between 17:47 and 18:13 UTC. |
| Steward | Docker (Docker Official Images). |
| What it is | The image the pilot scanned, its index, manifests, config, attestation manifests and attestation blobs. |
| Licence | not applicable (observation). |
| Library record | not a record (tool observation; recorded here and in searches.md). |
| How checked | Each response saved and hashed; every manifest's SHA-256 equals its digest. Index `294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6`; arm64 manifest `260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d`; config `33bee74c45f307e3268adc2010c0f55c48e7a6041e12cd12432bb1a46e498e43`; attestation manifest `ecc9a3031ac9bafed188097b6e65f328f5bf95f032d5e30030532cb259c6e006`; SBOM attestation blob `36c38f094eae6b8c898327c8ba99b22c1c113e91d0921c75ed91f9822b64aaff`; provenance blob `ec67817084c65cc94e49ae8782110dab2ea31ac3d2b7a0ac008fa4862049acbc`; referrers response `3d60eec733f106e03a571223c6adb85a3dabd53590ae0d8339e8ea2de2d32c56`. |

Observations:

- **Tags.** `latest`, `3.24.2`, `3.24` and `3` all returned `docker-content-digest: sha256:294b683c…` (an `application/vnd.oci.image.index.v1+json`), the value Syft lists in `repoDigests` (1.21).
- **The index.** 16 entries: 8 platform manifests (linux/amd64, arm/v6, arm/v7, arm64/v8, 386, ppc64le, riscv64, s390x) and 8 attestation manifests (`platform` unknown/unknown, `vnd.docker.reference.type: attestation-manifest`, `vnd.docker.reference.digest` pointing at a platform manifest). Each platform descriptor carries `org.opencontainers.image.version: 3.24.2`, `org.opencontainers.image.revision: 1c744e2d49059e51b063a11a6e3e18c9ccf04ab8` and `org.opencontainers.image.source: https://github.com/alpinelinux/docker-alpine.git#1c744e2d…:<arch>`.
- **Five digests for one image.** Index `294b683c…`; linux/arm64/v8 manifest `260479a1…` (what Syft recorded); config `33bee74c…` (Syft's `imageID`, the OCI ImageID); layer blob `a9986cd6…` (`application/vnd.oci.image.layer.v1.tar+gzip`, 4,187,659 bytes); layer diff_id `1b349a33…` (from the config's `rootfs.diff_ids`; Syft's `layerID` in package locations).
- **Attestation manifest (legacy format).** For arm64 (`ecc9a303…`): `config.mediaType` `application/vnd.oci.image.config.v1+json`, no `subject`, no `artifactType`; two layers of media type `application/vnd.in-toto+json` annotated `in-toto.io/predicate-type: https://spdx.dev/Document` and `https://slsa.dev/provenance/v0.2`. The blobs are plain in-toto Statements, not DSSE envelopes.
- **The SBOM attestation.** `_type: https://in-toto.io/Statement/v0.1`; 9 subjects, all with `sha256: 260479a1…` and different names: `pkg:docker/alpine@3.24.2?platform=linux%2Farm64%2Fv8`, the same for `@3.24`, `@3`, `@latest`, four `pkg:docker/arm64v8/alpine@…` names and one `pkg:docker/oisupport/staging-arm64v8@f99379c9…`. The predicate is SPDX 2.3, created 2026-09-17T20:37:06Z by "Tool: docker-scout-1.18.1", "Tool: buildkit-0.16.0-tianon" and "Organization: Docker, Inc". It lists 20 apk packages plus a document root: the 16 Syft also found, and 4 origin packages (`alpine-base`, `ca-certificates`, `openssl`, `pax-utils`) linked by 10 `GENERATED_FROM` relationships. Purls look like `pkg:apk/alpine/zlib@1.3.2-r0?os_name=alpine&os_version=3.24`; there are no CPEs; each package names a supplier (a person); 78 files carry SHA-1 and SHA-256.
- **The provenance attestation.** SLSA v0.2: `builder.id` `https://github.com/docker-library`; `buildType` `https://mobyproject.org/buildkit@v1`; `invocation.configSource.uri` the git repository at `1c744e2d…:aarch64`, entry point `Dockerfile`; `metadata.buildStartedOn` 2026-09-17T20:36:54Z, `buildFinishedOn` 20:37:07Z, `completeness` all true, `reproducible: false`; `materials` include the git commit as `{"sha1": "1c744e2d…"}` (not `gitCommit`) and the BuildKit and Scout indexer images by digest. The embedded Dockerfile is `FROM scratch`, `ADD alpine-minirootfs-3.24.2-aarch64.tar.gz /`, `CMD ["/bin/sh"]`: the provenance covers assembling the image from a tarball, not building the apk packages.
- **Not discoverable as referrers.** `GET /v2/library/alpine/referrers/sha256:260479a1…` returned 200 with an empty image index; the same for the index digest. The fallback tag `sha256-260479a1…` and the cosign-style tags `sha256-<digest>.sig` and `sha256-<digest>.att` (for both the index and the arm64 manifest digest) returned 404. Our reading: a consumer that looks only at the referrers API finds no SBOM for this image, although one is attached to its index.

### 1.21 Pilot outputs and Syft v1.52.0 source (what a real SBOM carries)

| field | value |
|---|---|
| Citation and URL | Pilot files (main session, 2026-10-08): `alpine.cdx.json` (CycloneDX 1.7), `alpine.syft.json` (Syft JSON schema 16.1.10), `alpine.spdx23.json` (SPDX 2.3), `alpine.grype.json`. Syft v1.52.0 source: `syft/format/internal/cyclonedxutil/helpers/decoder.go`, `syft/format/common/cyclonedxhelpers/to_format_model.go`, `syft/pkg/cataloger/internal/cpegenerate/README.md` |
| Version pinned and date | Syft 1.52.0, Grype 0.119.0 (database schema v6.1.10 built 2026-10-08T06:33:47Z), run 2026-10-08. |
| Steward | Anchore (tools). |
| What it is | Observation of the identifiers a real scan emits, and the code that maps them. |
| Licence | Syft and Grype Apache-2.0. |
| Library record | not records (tool outputs); Syft and Grype records are agent 5's. |
| How checked | `jq` over the four files: `alpine.cdx.json` `057c616b81fe01be2f658eb9493c056616933b6dff9d9d98c772c9011b8fe289`, `alpine.syft.json` `1a8fd622fb31f11be7eea1e38cc46427c5ac13dd5fae5c0b13bb3675588227fd`, `alpine.spdx23.json` `236c3f6e90e2dbfdc31f38a8660b1f5a4831b97943e5b5d125656369f9f535d3`, `alpine.grype.json` `97e45336b412caad27f03045a6d5f2a3f7c0b67e0ccfdc1b814774fdc6f40405`; source files: decoder.go `684b212581247d1459dc264998defa52d6a485dede02f8cca1925031d6b5717b`, to_format_model.go `b546f85e79faf5cf47b13ad940a9d0c52c47a27777b9628656b9ccc53a67ee54`, cpegenerate README `17fd2fe5f905fdc4e6eac944a3ca39f421c1170931dcef0a9e83ddbdbf5d8f60`. |

Observations:

- **Package identifiers (CycloneDX).** 16 `library` components, 78 `file` components, 1 `operating-system`. Of the 16 packages: 16 have `purl`, 16 have `cpe`, 0 have `hashes`, 0 `supplier`, 0 `swid`, 0 `omniborId`, 0 `swhid`, 0 `evidence`. All 78 files have SHA-1 and SHA-256. Example: `"purl": "pkg:apk/alpine/zlib@1.3.2-r0?arch=aarch64&distro=alpine-3.24.2"`, `"cpe": "cpe:2.3:a:zlib:zlib:1.3.2-r0:*:*:*:*:*:*:*"`; 10 of the 16 purls also carry `upstream=` (for example `upstream=openssl` on `libcrypto3`).
- **CPE provenance.** Syft JSON: 81 CPEs in all (16 in the standard field plus 65 `syft:cpe23` properties in CycloneDX), every one with `"source": "syft-generated"`. Syft's README: "CPE generation in Syft uses a **two-tier approach**": dictionary lookups for listed ecosystems and "Heuristic Generation (Fallback)" for "Java, .NET/NuGet, Alpine APK, Debian/RPM, and any other package type Syft discovers". None of the four candidates for `libcrypto3` names `openssl` (`libcrypto3:libcrypto3`, `libcrypto3:libcrypto`, `libcrypto:libcrypto3`, `libcrypto:libcrypto`).
- **Package digests exist only as vendor properties.** Syft JSON keeps apk metadata `pullChecksum` (`Q1qeG8MrsxW/2sYiT5J4Xk2aM0vyk=` for zlib) and `gitCommitOfApkPort` (`f248b33b…`); CycloneDX carries them only as `syft:metadata:pullChecksum` and `syft:metadata:gitCommitOfApkPort` properties; the SPDX 2.3 output does not carry them (0 matches). What bytes `pullChecksum` covers was not verified (the Alpine wiki returned 403).
- **The image, three ways.** Syft JSON `source.metadata` has `userInput` `alpine:latest`, `imageID` `sha256:33bee74c…`, `manifestDigest` `sha256:260479a1…`, `mediaType` `application/vnd.oci.image.manifest.v1+json`, `repoDigests` `index.docker.io/library/alpine@sha256:294b683c…`, `architecture` `arm64`, `os` `linux`. CycloneDX keeps only `metadata.component` `{"bom-ref": "caf3142caa4aa41f", "type": "container", "name": "alpine", "version": "sha256:260479a1…"}`, with no `purl` or `hashes`. SPDX 2.3 has a root package with `versionInfo` `sha256:260479a1…`, `checksums` `[{"algorithm": "SHA256", "checksumValue": "260479a1…"}]` and purl `pkg:oci/alpine@sha256%3A260479a1…?arch=arm64&tag=latest`. The index digest and the config digest appear only in Syft JSON (`grep` counts: 1 in syft.json, 0 in the other three files).
- **Grype's view of a CycloneDX input mislabels identity.** `alpine.grype.json` `source.target`: `"userInput": "alpine"`, `"imageID": "caf3142caa4aa41f"`, `"manifestDigest": "sha256:260479a1…"`, `"repoDigests": []`, `"architecture": ""`. Syft's decoder (v1.52.0, lines 237 to 240) maps a CycloneDX container component as `UserInput: c.Name`, `ID: c.BOMRef`, `ManifestDigest: c.Version`. Our reading: Grype was given the CycloneDX file, so the document-local `bom-ref` became `imageID`.
- **The OS component's SWID tag id is not unique.** CycloneDX OS component `"swid": {"tagId": "alpine", "name": "alpine", "version": "3.24.2"}`. Syft source: `TagID: distro.ID`, under the code comment "is it idiomatic to be using SWID here for specific name and version information?" (to_format_model.go, lines 173 to 175). Every Alpine release therefore gets tag id `alpine`, against RFC 9393's "MUST be globally unique" (1.8).
- **Document identity.** `serialNumber` `urn:uuid:dd9def15-aedf-4e87-9d42-335572c393cc`, `metadata.timestamp` `2026-10-08T10:31:04-07:00`, `metadata.tools` syft 1.52.0; `metadata.lifecycles` absent. CycloneDX: "Every BOM generated SHOULD have a unique serial number, even if the contents of the BOM have not changed over time" (schema 1.7.2, `serialNumber`).

### 1.22 OSV: schema v1.9.1, the OSV.dev query API, its purl mapping code, and live queries

| field | value |
|---|---|
| Citation and URL | OpenSSF, *OSV Schema* v1.9.1, <https://github.com/ossf/osv-schema/blob/v1.9.1/docs/schema.md>; OSV.dev API doc `docs/api/post-v1-query.md` and Go package `go/purl/` at google/osv.dev commit `16b340c78a51` (2026-10-08T04:14:27Z); API endpoint `https://api.osv.dev/v1/query` |
| Version pinned and date | Schema v1.9.1 (release 2026-09-24); OSV.dev `master` at `16b340c78a51`; queries run 2026-10-08 about 17:55 UTC. |
| Steward | OpenSSF (schema); Google (OSV.dev). |
| What it is | The OSV record format (`affected[].package`, ranges) and the OSV.dev database API. Records in depth are agent 3's; this record covers only what OSV keys on. |
| Licence | Apache-2.0 (both repositories). |
| Library record | `osv-schema` (summarized; agent 3 owns it). |
| How checked | schema.md SHA-256 `e5b87d6258f133f2fb146661b4d7ee7d6c1ffb15f7b752d49b1b790ea683307e`; post-v1-query.md `27d5f844015702dcfb5c7b846dbdb153f16721833d8b87b4686f9a7f60ea5802`; `ecosystem_debian.go` `209ff3edf35f2ad1621deaccfb2e56c8a2adedaa5b2aef68889d6a5e80d95e66`; `ecosystems_simple.go` `3acb149c258c3c6b34c257c19bb2a49a4510ec378929f0c602a3a296fab52f9f`; 17 query responses saved (section 7). |

Findings (spec and code):

- **Keyed on ecosystem and name; purl optional and versionless.** "The object itself has two required fields, `ecosystem` and `name`, and an optional `purl` field." The `purl` "identifies the package, without the `@version` component. This field is optional but recommended." (schema.md, `affected[].package`).
- **Commit hashes are first-class versions.** For `GIT` ranges "The versions `introduced` and `fixed` are full-length Git commit hashes." (schema.md, `affected[].ranges[].type`). The API: "Lists vulnerabilities for given package and version. May also be queried by commit hash." Package objects "can be described by package name AND ecosystem OR by the package URL" (post-v1-query.md).
- **purl to ecosystem mapping is per type.** For Debian, the parser reads the `distro` qualifier: "Lenient mapping: check if it's a codename", otherwise "Or if it's already a version number (e.g., distro=11)" and builds `"Debian:" + distroVal` (`ecosystem_debian.go`). Alpine is registered with `registerSimple(osvconstants.EcosystemAlpine, "apk", "alpine", sourceArchQualifiers)`, and the simple parser returns the bare ecosystem without a release (`ecosystems_simple.go`, lines 45 to 52 and 102). Our reading: `distro=debian-12` becomes the ecosystem `Debian:debian-12`, and any `pkg:apk/alpine/...` purl maps to `Alpine` with no release.

Observations (API, 2026-10-08):

| query | result |
|---|---|
| `{"package": {"name": "busybox", "ecosystem": "Alpine:v3.18"}, "version": "1.36.1-r0"}` | 5 advisories (for example `ALPINE-CVE-2022-48174`, `ALPINE-CVE-2023-42363`) |
| the same package as `pkg:apk/alpine/busybox@1.36.1-r0` with `?arch=x86_64&distro=alpine-3.18.0`, `?arch=x86_64&distro=3.18.0`, `?os_name=alpine&os_version=3.18`, `?distro=v3.18`, or no qualifiers | 0 for each |
| `{"package": {"name": "openssl", "ecosystem": "Debian:12"}, "version": "3.0.11-1~deb12u2"}` | 52 |
| `pkg:deb/debian/openssl@3.0.11-1~deb12u2?distro=bookworm` | 52 (byte-identical response) |
| `pkg:deb/debian/openssl@3.0.11-1~deb12u2?arch=amd64&distro=debian-12` | 0 |
| `pkg:deb/debian/openssl@3.0.11-1~deb12u2` (no qualifiers), or versionless purl plus `"version"` | 82 |
| `pkg:pypi/jinja2@3.1.4` and `{"name": "jinja2", "ecosystem": "PyPI"}` with `3.1.4` | 6 each, same ids |
| the pilot's packages (busybox `1.37.0-r31`), four spellings incl. `Alpine:v3.24` | 0 each (no known advisories for that version) |

Our reading: for language ecosystems the purl is a working key; for distribution packages the same package version gives 0, 52 or 82 results depending on how, or whether, the release is spelled in the purl.

### 1.23 GitHub Advisory Database (GHSA)

| field | value |
|---|---|
| Citation and URL | GitHub REST API OpenAPI description, `descriptions/api.github.com/api.github.com.json` at github/rest-api-description commit `7dee0622`; advisory `GHSA-cpwx-vrp4-4pq7` in github/advisory-database (`advisories/github-reviewed/2025/03/…`) |
| Version pinned and date | OpenAPI description at `7dee0622` (main, fetched 2026-10-08); advisory file at `main` on 2026-10-08. |
| Steward | GitHub. |
| What it is | The global security advisories API and the OSV-format advisory repository. |
| Licence | not checked here (agent 3). |
| Library record | none; agent 3 (bridge) owns the GHSA record proposal. |
| How checked | OpenAPI JSON SHA-256 `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194` (parsed with `python3`); advisory `dd20a2e4e7fbc8812f5b4216fdc9f9d192003e5ef0ee9148f9a5d525084b6438`. |

Findings:

- **Keyed on ecosystem and package name.** `vulnerabilities[].package` has `ecosystem` and `name` ("The unique package name within its ecosystem."); the `affects` filter takes "`package` or `package@version`". The `global-advisory` schema has no purl or CPE property (case-insensitive search of the schema text: 0 hits for "purl" and "cpe"). Ecosystems: `rubygems`, `npm`, `pip`, `maven`, `nuget`, `composer`, `go`, `rust`, `erlang`, `actions`, `pub`, `other`, `swift`.
- **Example.** `GHSA-cpwx-vrp4-4pq7` has `"package": {"ecosystem": "PyPI", "name": "Jinja2"}` and no purl. Our reading: a consumer keyed on `pkg:pypi/jinja2` must normalize the case first (the `pypi` purl type is case-insensitive, 1.2).

### 1.24 deps.dev API (v3 and v3alpha)

| field | value |
|---|---|
| Citation and URL | <https://docs.deps.dev/api/v3/> and <https://docs.deps.dev/api/v3alpha/> |
| Version pinned and date | Pages fetched 2026-10-08 (no version stamp on the pages). |
| Steward | Google (Open Source Insights). |
| What it is | Package, version, dependency, advisory and project data, queryable by name, version, hash and purl. Agent 5 covers deps.dev in depth. |
| Licence | not checked (agent 5). |
| Library record | none; agent 5. |
| How checked | v3 page SHA-256 `010ef93f40c66f0be9c6976d7b27d7fde11034ceaea6c1f5918af2e196642079`; v3alpha `e4b5e4330f72b0eba9557476cb2a90ee17e8f42fc5bcc2ac272ebb80b294fd07`; text extracted, `grep` for swhid, gitoid, omnibor, cpe, swid: 0 hits in both. |

Findings:

- **Hash lookup, with a warning.** "Query returns information about multiple package versions, which can be specified by name, content hash, or both." "Querying by content hash is currently supported for npm, Cargo, Maven, NuGet, PyPI and RubyGems. It is typical for hash queries to return many results; hashes are matched against multiple release artifacts (such as JAR files) that comprise package versions, and any given artifact may appear in several package versions." `hash.type` is one of MD5, SHA1, SHA256, SHA512 (v3, Query).
- **purl lookup without qualifiers.** "Extra fields in the purl must be empty, otherwise the request will fail. In particular, there must be no subpath or qualifiers." Supported types: cargo, gem, golang, maven, npm, nuget, pypi (v3alpha, PurlLookup). Returned purls "may differ from the names in the request, due to canonicalization".
- **Container images by layer chain.** `QueryContainerImages` takes an "OCI Chain ID", "a hashed encoding of an ordered sequence of OCI layers"; "If an image contains empty layers, it is available from this endpoint under two different chain IDs" (v3alpha). Our reading: this is a sixth image digest, different from the five in 1.20.

### 1.25 GUAC v1.1.0 GraphQL schema

| field | value |
|---|---|
| Citation and URL | guacsec/guac v1.1.0, `pkg/assembler/graphql/schema/{package,artifact,source,pkgEqual,hashEqual,isOccurrence,hasSBOM,hasSLSA}.graphql`, <https://github.com/guacsec/guac/tree/v1.1.0/pkg/assembler/graphql/schema> |
| Version pinned and date | v1.1.0, released 2026-03-13 (latest release on 2026-10-08). |
| Steward | OpenSSF (GUAC). |
| What it is | The node and evidence types of GUAC's composition graph. Agent 5 covers GUAC as a tool. |
| Licence | Apache-2.0 (file headers). |
| Library record | `guac` (summarized). |
| How checked | package `0c57daa9c179c9652c5ec6646465bcb990f619ff8d4efdedebc55e3da36acf15`, artifact `8ee0612a04764616a4fc8c1b38d46920f6bf20d63833922b8066d2113c4ded75`, source `4d87bf0f3263e61238c977e3c7d7e9311c07fd6ee5501888c5f5a10b90620d91`, pkgEqual `c8d205dd08179f7df3248e3f3bb3f1e73ca0d65d2e0c08d9ddc2a5ad7057c29c`, hashEqual `358d1cdc00c59bca1eaf953ce0729b7c166c3d4b34fea97b85f9287b15952183`, isOccurrence `5d59899b93d26eed9714fdbfa979fd53a2d2a3da12db9630c506e09b10382659`, hasSBOM `4538202adb1cb0e684a1284c2e25f2a5496948036230497da780a84a91a2b39c`, hasSLSA `d78092dacda2da322e0303f8e3c9fd4cbaa2e5dd860a621971983bd7a568e1be`; `gh api search/code` in guacsec/guac for "omnibor", "gitoid", "swhid": 0 hits each (default branch, 2026-10-08). |

Findings:

- **Packages are a purl trie, and qualifiers split nodes.** "We map package information to a trie, closely matching the pURL specification ... but deviating from it where GUAC heuristics allow for better representation". "Two nodes that have different qualifiers and/or subpath but the same version mean two different packages in the trie (they are different). Two nodes that have same version but qualifiers of one are a subset of the qualifier of the other also mean two different packages in the trie." (`PackageVersion` description).
- **Artifacts are digests.** "Artifact represents an artifact identified by a checksum hash. The checksum is split into the digest value and the algorithm used to generate it. Both fields are mandatory and canonicalized to be lowercase."
- **Sources are VCS paths with a tag or commit.** Source is a trie "as a derivative of the pURL specification: each path in the trie represents a type, namespace, name and an optional qualifier that stands for tag/commit information".
- **Equivalence and occurrence are evidence nodes.** `PkgEqual` ("Two packages that are similar") and `HashEqual` ("Two artifacts that are similar") each carry `justification`, `origin`, `collector` and `documentRef`; `IsOccurrence` is "an attestation to link an artifact to a package or source". `HasSBOM` keeps the SBOM's `uri`, `algorithm`, `digest`, `downloadLocation`, `knownSince` and its subject (package or artifact). `HasSLSA` links an `Artifact` subject to a SLSA record.

### 1.26 Dependency-Track component identity

| field | value |
|---|---|
| Citation and URL | <https://docs.dependencytrack.org/analysis-types/component-identity/> |
| Version pinned and date | v4 documentation site, fetched 2026-10-08. Latest release on GitHub: 5.2.0 (2026-10-08T09:09:37Z). |
| Steward | OWASP Dependency-Track. |
| What it is | Which identifiers the policy engine matches. Agent 5 covers Dependency-Track as a tool. |
| Licence | not checked here (agent 5). |
| Library record | none; agent 5. |
| How checked | page SHA-256 `52a2607281bb673bcfb3d11da0977bb089d5680a0ebfe2f63c2658250ae61769`; `gh api search/code` in DependencyTrack/dependency-track for "omnibor" and "swhid": 1 hit each, both in the vendored CycloneDX 1.7 protobuf file. |

Findings:

- **Identity kinds.** "Components can be evaluated based on their identity as part of the Dependency-Track policy engine." Identity may be "Coordinates" (group, name, version), "Package URL", "CPE", "SWID TagID" or "Hash"; "Hash identity automatically checks all supported hash algorithms" (12 listed, MD5 to BLAKE3).

### 1.27 SBOMproof (arXiv 2510.05798)

| field | value |
|---|---|
| Citation and URL | *SBOMproof: Beyond Alleged SBOM Compliance for Supply Chain Security of Container Images*, arXiv:2510.05798, submitted 2025-10-07, 4 authors. <https://arxiv.org/abs/2510.05798> |
| Version pinned and date | arXiv v1 PDF as served on 2026-10-08. |
| Steward | academic authors (not checked further). |
| What it is | An empirical comparison of SBOM generators and scanners on container images, focused on Debian and Alpine packages. |
| Licence | arXiv (not checked). |
| Library record | none; proposed `sbomproof-2025` (paper, summary bar). |
| How checked | abstract page SHA-256 `5dad99df9ddc376b75e657bff923add412771e0e7b6fa07003a58653f2ba3b85`; PDF `df6ea23bf601372f61c785889e0208a002f2d5f46c33a5460766e9873ade4a4f`; §4.1 and §4.2 read in the extracted text. Tool versions used in the study were not recorded in these notes. |

Findings (the paper's results, as stated by its authors):

- "the pURLs generated by the considered tools are substantially different from each other, with only a minor overlap occurring between Anchore and Google. We found similar results in the Alpine datasets" (§4.1).
- Table 4 lists purl qualifiers by tool: Trivy "arch, distro, epoch", Anchore "arch, distro, upstream", Docker "os_distro, os_version, os_name". This matches our observation in 1.20 and 1.21.
- "Observation 1: Tools do not employ the same pURLs and none of them respects the standard. Some tools generate incomplete or incorrect pURLs." and "Observation 2: Some tools do not use pURLs to uniquely identify packages and rely on other SPDX parameters or optional fields." (§4.1, §4.2). They also report that Trivy ignored purl qualifiers and that "Grype employs version information from the SBOM package instead of that inside the pURL to index CVEs" (§4.2.1).

### 1.28 UN Regulation No. 156 (software update and RXSWIN)

| field | value |
|---|---|
| Citation and URL | UNECE WP.29, *Proposal for a new UN Regulation on uniform provisions concerning the approval of vehicles with regards to software update and software updates management system*, ECE/TRANS/WP.29/2020/80, 31 March 2020, from the UN Official Document System: <https://documents.un.org/api/symbol/access?s=ECE/TRANS/WP.29/2020/80&l=en&t=pdf>. EU copy: *UN Regulation No 156*, OJ L 82, 9.3.2021, p. 60 (CELEX 42021X0388), <https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:42021X0388> |
| Version pinned and date | Original version; "Date of entry into force: 22 January 2021" (OJ copy). Later supplements were not checked. |
| Steward | UNECE World Forum for Harmonization of Vehicle Regulations (WP.29). |
| What it is | Type-approval requirements for vehicle software updates, including the software update management system (SUMS) and the RXSWIN. |
| Licence | UN document; EU OJ copy. Not checked further. |
| Library record | none; proposed `unece-r156` (shelf `regulator`); stub now, FX-1 candidate under RPT-0007 (#11). |
| How checked | unece.org returned HTTP 403 with a Cloudflare challenge for `R156e.pdf` and the documents page (2026-10-08), so the regulation text was taken from the UN Official Document System (UN text SHA-256 `eed671947171c0f9455f7c994b16c1db2701874d2b0c7d047885ef8f8564b2a9`) and checked against the EU OJ copy (`1ee81699cf0af825e0551269dc73b08f79655c0058495807301d3c0ee9f69e68`); the OJ copy states "The authentic and legally binding text is: ECE/TRANS/WP.29/2020/80." |

Findings:

- **Definition.** ""RX Software Identification Number (RXSWIN)" means a dedicated identifier, defined by the vehicle manufacturer, representing information about the type approval relevant software of the Electronic Control System contributing to the Regulation N° X type approval relevant characteristics of the vehicle." (§2.2).
- **When it changes.** "Each RXSWIN shall be uniquely identifiable. When type approval relevant software is modified by the vehicle manufacturer, the RXSWIN shall be updated if it leads to a type approval extension or to a new type approval." (§7.2.1.2.1). Our reading: an RXSWIN changes only with type-approval-relevant changes, not with every software change.
- **What stands behind it.** "For every RXSWIN, there shall be an auditable register describing all the software relevant to the RXSWIN of the vehicle type before and after an update. This shall include information of the software versions and their integrity validation data for all relevant software for each RXSWIN." (§7.1.2.3). "Integrity validation data" means "a representation of digital data, against which comparisons can be made to detect errors or changes in the data. This may include checksums and hash values." (§2.11). The SUMS must uniquely identify "all initial and updated software versions, including integrity validation data, and relevant hardware components of a type approved system" (§7.1.1.2).
- **Read from the vehicle, or declared.** "Each RXSWIN shall be easily readable in a standardized way via the use of an electronic communication interface, at least by the standard interface (OBD port). If RXSWINs are not held on the vehicle, the manufacturer shall declare the software version(s) of the vehicle or single ECUs with the connection to the relevant type approvals to the Approval Authority." (§7.2.1.2.2). RXSWINs and software versions must be protected "against unauthorised modification" (§7.2.1.2.3).

### 1.29 ISO 24089:2023 (public metadata only)

| field | value |
|---|---|
| Citation and URL | ISO 24089:2023, *Road vehicles: Software update engineering*; ISO 24089:2023/Amd 1:2024 |
| Version pinned and date | Published 2023-02-08 (edition 1, 24 pages, stage 60.60); Amd 1 published 2024-07-25 (ISO Open Data, file of 2026-10-07). |
| Steward | ISO/TC 22/SC 32. |
| What it is | Requirements and recommendations for vehicle software update engineering. |
| Licence | paywalled; not read. |
| Library record | `iso-24089-2023` (stub). Keep as stub. |
| How checked | ISO Open Data CSV (1.31), rows id 77796 and 87522, including the public `scope.en` text. |

Findings (public metadata only):

- Scope (ISO's own abstract): "This document specifies requirements and recommendations for software update engineering for road vehicles on both the organizational and the project level." and "this document does not prescribe specific technologies or solutions for software update engineering." The public text does not mention identification, so this report cannot say what ISO 24089 requires for software identifiers.

### 1.30 IETF SUIT manifest (draft-ietf-suit-manifest-37)

| field | value |
|---|---|
| Citation and URL | *A Concise Binary Object Representation (CBOR)-based Serialization Format for the Software Updates for Internet of Things (SUIT) Manifest*, draft-ietf-suit-manifest-37, <https://www.ietf.org/archive/id/draft-ietf-suit-manifest-37.txt> |
| Version pinned and date | Revision 37; datatracker states "RFC Ed Queue" and "Submitted to IESG for Publication", not yet an RFC (datatracker API, 2026-10-08; document time 2026-09-30). |
| Steward | IETF SUIT working group. |
| What it is | A signed manifest that tells a device how to fetch, check and install firmware or software images. Firmware composition is agent 4's; this record covers identity only. |
| Licence | IETF Trust (not re-checked). |
| Library record | none; proposed `draft-ietf-suit-manifest` stub (coordinate with agent 4). |
| How checked | Text SHA-256 `6f20207134bdb011a601b661f9373ff085dde8f6ff9e3aacb070acd156f6c7c3`; datatracker JSON for state ids. |

Findings:

- **Firmware is identified by digest and size.** `suit-parameter-image-digest`: "A fingerprint computed over the component itself" (§8.4.8.6); `suit-parameter-image-size`: "The size of the firmware image in bytes." (§8.4.8.7).
- **Vendor and class ids are not identity.** "Identifiers are used for compatibility checks. They MUST NOT be used as assertions of identity." (§8.4.8.2).
- **Ordering is a counter, not a version.** "The suit-manifest-sequence-number is a monotonically increasing anti-rollback counter. Each Recipient MUST reject any manifest that has a sequence number lower than its current sequence number." (§8.4.2). Image version checks are deferred to the separate update-management draft (requirement `REQ.USE.IMG.VERSIONS` mapped to `[I-D.ietf-suit-update-management]`).

### 1.31 Status sources: ISO Open Data, ISO stage codes, IANA URI schemes

| field | value |
|---|---|
| Citation and URL | ISO Open Data `iso_deliverables_metadata.csv`, <https://isopublicstorageprod.blob.core.windows.net/opendata/_latest/iso_deliverables_metadata/csv/iso_deliverables_metadata.csv>; ISO stage-code table reproduced at certifico.com (<https://certifico.com/normazione/208-documenti-riservati-normazione/organismi-normazione/documenti-iso/7880-international-harmonized-stage-codes-iso>); IANA Uniform Resource Identifier (URI) Schemes registry CSV <https://www.iana.org/assignments/uri-schemes/uri-schemes-1.csv> and the `pkg` and `gitoid` registration pages |
| Version pinned and date | ISO CSV `Last-Modified: Wed, 07 Oct 2026 00:41:52 GMT` (81,585 rows); IANA fetched 2026-10-08. |
| Steward | ISO; IANA. |
| What it is | Status data only. |
| Licence | ISO Open Data: ODC-By (as recorded in RPT-0004 0.1.0 sources.md). IANA: public registry. |
| Library record | none (RPT-0004 0.1.0 also had none). |
| How checked | ISO CSV SHA-256 `cf68a7ee4eaedc8a2a35a137a22b2f19360b8cd228935f7774e6003df8bb0b91`, filtered with `python3`; iso.org's stage-code page returned 403 (bot check), so the certifico copy (`57cab6cb5481611362fd93fc258eabdca59a6389329832bffd5f574cbc75ed02`) was used for code meanings; IANA CSV `1e7c3a601a7f1116dc8f86125dbe5a4c3010b0ca7885631a167bfe89df8cdb6a`, `pkg` page `d5c9b6a1a65b338f5af3a3127223871d4af02fdd13f014e3e6560f4a9f0bfaf6`. |

Findings:

- **ISO rows (current stage).** ISO/IEC DIS 27056 "Package-URL (PURL) specification", stage 4000; ISO/IEC 18670:2025 SWHID V1.2, 6060, published 2025-04-23; ISO/IEC 19770-2:2015, 9060; ISO/IEC 19770-6:2024, 6060; ISO 24089:2023, 6060; ISO/IEC DIS 27055 (CycloneDX), 4000; ISO/IEC DIS 5962 (SPDX 3.0), 4099. Code meanings (certifico copy): "30.99 CD approved for registration as DIS", "40.00 DIS registered", "40.99 Full report circulated: DIS approved for registration as FDIS", "60.60 International Standard published", "90.60 Close of review".
- **Change since RPT-0004 0.1.0.** 0.1.0 (ISO data of 2026-09-30) had purl as "ISO/IEC CD 27056, also at stage 30.99"; the file of 2026-10-07 lists ISO/IEC DIS 27056 at 40.00, and Ecma's page lists "DIS 27056".
- **IANA URI schemes.** `pkg` "Provisional" (registered 2026-07-27; the page says "It is standardized as ECMA-427"), `gitoid` "Provisional", `swh` "Provisional", `swid` and `swidpath` "Provisional" (referencing RFC 9393 §5.1 and §5.2).

### 1.32 tradar at `26d9c76` (re-check of RPT-0004 0.1.0 §4 claims used here)

| field | value |
|---|---|
| Citation and URL | Threat-Radar/tradar at commit `26d9c76`: `threat_radar/core/grype_integration.py`, `threat_radar/cli/cve.py` |
| Version pinned and date | `main` is still `26d9c76` (merge commit dated 2026-09-11T00:52:41Z) on 2026-10-08. |
| Steward | Threat-Radar (project). |
| What it is | radar's current code. |
| Licence | not re-checked. |
| Library record | none (0.1.0: "not yet a record"). |
| How checked | `gh api …/contents?ref=26d9c76`; grype_integration.py SHA-256 `c6efec650902f9950e34f2dce11312fababd59038a01b1f9c212962481bbeab4`, cve.py `6199662dcec9c0e8c443ca8af485e6f81b6285b4a33ec3a85d1455b3d94b1757`. |

Findings:

- **Grype's identity block is kept but unread.** `grype_integration.py` lines 411 to 418 build `scan_metadata = {"source": source, "descriptor": descriptor, "grype_version": ..., "grype_db": ...}`; `cli/cve.py` saves `"scan_metadata": result.scan_metadata` (lines 151, 337, 480). This confirms 0.1.0 §4. Combined with 1.21: on the SBOM path (`grype sbom:<file>`), that block holds the manifest digest and the CycloneDX `bom-ref` as `imageID`, with no index digest, platform or config digest.

## 2. Dimension questions answered

### Dimension 6: build identity and the radar to tmodel input contract

**Base question (from 0.1.0): how does composition pin one specific product version?** The 0.1.0 quotes were re-checked and stand: OCI's definitions of digest and tag and the client duty to verify a digest (1.13); SLSA's git commit as a resolved dependency (1.15); in-toto's "MUST have `digest` set" and "matched purely by digest" (1.14); CycloneDX's per-document serial number (1.21); SPDX `Build` requiring only `buildType` (1.11); and the reproducible-builds definition, "A build is reproducible if given the same source code, build environment and build instructions, any party can recreate bit-by-bit identical copies of all specified artifacts." (<https://reproducible-builds.org/docs/definition/>, SHA-256 `535b0c2bf32d3b552751762ad6f08c51b27b0b35fbc1a085b6c253026f513164`, fetched 2026-10-08). New in this pass: "a digest" is not enough, because an image has at least five (1.20), and the SBOM path keeps only one of them, unlabelled (1.21, 1.32).

**Q1. Which identity anchors which model type, and when is a rescan the same ProductInstance?**

*What the draft says today.* All quotes are from `spec/schema/tmodel-object-model.linkml.yaml` (draft 0.1.0, last changed in `bd6625c`, 2026-10-05) and `spec/ARCH-0001-PROPOSAL-v0.2.0.md` (`0.2.0-proposed.11`); nothing in them is accepted.

- Every object has one key, `Node.id`: `identifier: true`, `range: uriorcurie`, `required: true`, "Stable object id (ADR-0004). Adapters must not renumber it." (LinkML lines 315 to 319). ADR-0004: "The canonical file ID is authoritative; adapters MUST map to it" (line 70).
- **Product**: "A product design (structural layer, §1)." Slots `composed_of`, `manufactured_by`, `supplied_by`, `owned_by` (lines 51 to 60).
- **ProductInstance**: "A versioned, identity-bearing instance of a Product (§1, §3b)." and "A refurbished unit can share a firmware hash and still carry a new phase, Deployment, and owner." Slots `of_product` (required), `current_phase`, `valid_from`, `valid_to`, `owned_by` (lines 62 to 74, 361 to 364).
- **Component**: "Authoritative deployed artifact (service, container, dependency, chip, core)" (line 79). Slots `composed_of`, `depends_on`, `uses_component`, `owned_by`.
- **No identity slot exists.** Checked exhaustively: the schema defines 62 slots (listed with `python3`); a case-insensitive `grep` for purl, cpe, digest, hash, sbom, commit and version matches only the schema's own `version: 0.1.0` and the two description lines quoted above; `identifier: true` occurs once (on `id`) and there is no `unique_keys`. RPT-0015 §4 already lists "no `unique_keys`" as a systemic gap and asks for id-string patterns that include "CPE/purl".
- **The proposal's prose goes further than the schema.** §1: "Product/ProductInstance(versioned), Component (CPE/purl, shared)" (line 109). §3b: "the same identity-by-hash `ProductInstance`", and "state is carried by a (ProductInstance, time) pair, not by the hash alone" (lines 280 to 282). §7 marks "Product/ProductInstance, Component(CPE/purl)+composition" as MVP build (line 420). ARCH-0001 R-022 names "software (build/commit/hash/SBOM)" instance types (line 121).

Our reading: today a ProductInstance or Component is whatever `id` a loader mints; the draft states the intent (identity by hash for instances, CPE and purl for components) but has no slot, rule or pattern that connects an `id` to composition evidence.

*Evidence that could pin each type.*

| model type | candidate keys (evidence) | assigned or computed |
|---|---|---|
| Product (a design or product line) | versionless purl, as OSV (1.22) and NVD's new "affected" data (1.7) use it; Official CPE vendor:product (a class, 1.4, 1.6); CoSWID `persistent-id` (1.8); OCI repository name (1.13); vehicle type (R156 §2.1) | assigned |
| ProductInstance (one concrete build) | OCI index or platform-manifest digest (1.12, 1.20); attestation subject digest (1.14, 1.15); source commit plus build provenance (1.15, 1.20); firmware image digest and size (1.30); RXSWIN plus its register of software versions and integrity data (1.28) | computed, except RXSWIN |
| Component | versioned purl (1.1, 1.2); package or file hashes (1.11, 1.21); gitoid or SWHID for files and source trees (1.9, 1.10); CPE as a matching attribute (1.4 to 1.7); SWID tag-id where an authoritative tag exists (1.8) | mixed |

*When is a rescan the same ProductInstance? Options and trade-offs (evidence, not a decision):*

| option | for | against |
|---|---|---|
| A. Same platform-manifest digest | Computed and verifiable (OCI digest rule, 1.12); it is what in-toto and SLSA verification match (1.14, 1.15), what BuildKit uses as subject (1.20), what Syft records (1.21), and what the proposal calls identity-by-hash | One release becomes one instance per platform (8 for alpine 3.24.2, 1.20); which platform a scan sees depends on the machine (our reading; Syft's selection logic not checked); the same bytes can be in different lifecycle states, so state needs a (ProductInstance, time) pair, as §3b says |
| B. Same index digest | It is what the tags resolve to (1.20); one instance per multi-platform release | Syft's CycloneDX and SPDX outputs do not carry it and Grype loses it (1.21); with BuildKit's index-attached storage the index also lists attestation manifests, so (our reading) re-attesting changes the index digest without changing any image; single-platform images have no index |
| C. Same name and tag (or version string) | Human-meaningful; what users type | Tags are pointers: "A manifest digest may have zero, one, or many tags referencing it" (1.13); the `docker` purl type says "tags can be moved" (1.2); four tags named one digest on 2026-10-08 (1.20) |
| D. Same source commit and build definition | Stable across rebuilds; links to source review | Needs provenance, which the proposal puts after the MVP (§7); builds are often not reproducible (the alpine provenance says `"reproducible": false`, 1.20), so one commit can yield several digests; for alpine the commit identifies a Dockerfile and a tarball, not the package builds |
| E. Same SBOM | none found | A serial number identifies a document, not a build (1.21); two tools describe the same bytes differently (16 versus 20 package entries, different purls, 1.20) |
| F. Domain-specific | Vehicles: RXSWIN is the regulator's unit (1.28); firmware: SUIT image digest and component id (1.30) | An RXSWIN changes only with type-approval-relevant changes (1.28), so it is coarser than a digest; SUIT's sequence number orders updates but is not identity (1.30) |

The options combine: for example, A as the key with B, C and D stored as attributes or links. A rescan of the same key by another tool is then a new composition claim about the same instance, not a new instance (section 5, rule R-MERGE-1).

**Q2. Attestations as carriers: how do SBOMs and provenance attach to an artifact digest?**

| carrier (version) | binds by | SBOM and provenance predicate types | where it lives | source |
|---|---|---|---|---|
| in-toto Statement v1 (framework v1.2.0, 2026-03-18) | `subject[].digest`, "matched purely by digest"; any acceptable algorithm matches | `https://spdx.dev/Document` (and `/v2.3`), `https://spdx.dev/Document/v3`, `https://cyclonedx.org/bom` (example uses `/v1.4`); SLSA `https://slsa.dev/provenance/v1` | not specified; JSON Lines bundles `.intoto.jsonl`; SLSA's suite says "Storage/Lookup: TBD" | 1.14, 1.15 |
| SLSA build provenance v1 (SLSA 1.2) | subject digests of outputs; verifier checks "subject matches the digest" | `https://slsa.dev/provenance/v1` | "MUST publish attestations in at least one place"; release, registry sidecar, or transparency log | 1.15 |
| Sigstore bundle v0.3 | wraps one DSSE envelope with exactly one signature | any in-toto predicate | file or registry | 1.16 |
| OCI image manifest with `subject` (image-spec v1.1.1) and referrers API (distribution-spec v1.1.1) | `subject` descriptor digest | given by `artifactType` and the payload | registry, listed by `GET /v2/<name>/referrers/<digest>` | 1.12, 1.13 |
| BuildKit attestations (v0.34.0) | attestation manifest in the index, `vnd.docker.reference.digest`; in OCI-artifact mode also `subject` | SBOM `https://spdx.dev/Document` (SPDX JSON); provenance v1 by default, v0.2 supported | inside the image index | 1.17 |
| Docker Official Image `alpine` (observed) | index descriptor annotations; Statement `subject` = platform manifest digest under 9 names | `https://spdx.dev/Document` (SPDX 2.3 by Docker Scout 1.18.1); `https://slsa.dev/provenance/v0.2` | legacy attestation manifest in the index, unsigned in-toto Statement v0.1; empty referrers list | 1.20 |
| cosign v3.1.3 `cosign attest` | image digest; "MUST verify the relationship between the `subject` field and the container image" | `spdx`/`spdxjson` to `https://spdx.dev/Document`; `cyclonedx` to `https://cyclonedx.org/bom`; `slsaprovenance` and `slsaprovenance02` to v0.2; `slsaprovenance1` to v1 | v3 default: OCI 1.1 referring artifact with a Sigstore bundle | 1.18 |
| GitHub `actions/attest` v4.2.2 | "identified by the supplied digest" | SPDX or CycloneDX JSON SBOM; SLSA provenance | GitHub attestations API; registry only with `push-to-registry` | 1.19 |

Our reading: every carrier binds by digest, but three things vary: which digest (manifest, index, or "some object within", 1.17), where the attestation is stored (index, referrers, a separate API), and how the SBOM predicate type is spelled (with or without a version). A consumer that queries only one storage route misses the others (1.20).

**Q3. The contract: what would radar have to emit for tmodel to fill Table 6?** Evidence only; ADR-0001 owns the contract ("tmodel does **not** re-implement scanning/composition; it consumes radar's results through a composition→model-input contract", lines 48 to 49), and the proposal puts "compile/SLSA build provenance" after the MVP (§7, line 431).

1. **Subject identity, every level, labelled.** The user's reference (`userInput`), each digest with its algorithm and media type (index, platform manifest, config), the platform (os, architecture, variant), the repository, and the tags seen at scan time with the time. Syft JSON already has all of these (1.21); CycloneDX and SPDX outputs keep only the manifest digest, and Grype's CycloneDX path relabels the `bom-ref` as `imageID` (1.21); tradar keeps Grype's block but reads none of it (1.32).
2. **Who made the composition claim, and when.** SBOM format and version, serial number or document namespace, generator name and version, timestamp, and the SBOM file's own digest (GUAC's `HasSBOM` keeps `uri`, `algorithm`, `digest`, `knownSince`, 1.25); for findings, the scanner's database build time and provider capture times (Grype `descriptor.db`, pilot).
3. **The Component identity set, raw and parsed.** The purl string exactly as emitted plus its parsed parts and qualifiers; each CPE with its `source` (dictionary or generated, 1.21) and, if looked up, NVD's `cpeNameId` and `deprecated` flag (1.7); each hash with its algorithm and what was hashed (file, package archive, layer); locations (layer diff_id, path); origin or upstream package; the distribution release, which OSV needs as an ecosystem key (1.22).
4. **Relationships** (depends-on, contains, file ownership), as 0.1.0 §4 already lists.
5. **Build record (post-MVP).** Any attestation found for the subject digest: its predicate type, where it was found (index, referrers, GitHub API), whether it was signed and verified, and from provenance the builder id, build type, source URI and commit, timestamps and the `reproducible` flag (1.15, 1.20).
6. **A binding envelope.** All surveyed carriers put an SBOM inside an in-toto Statement whose `subject` is the artifact digest (1.14 to 1.19). If radar emitted its output the same way, tmodel could match it by digest exactly as verifiers do (our reading).

**Q4. Other domains: firmware images and vehicle software sets.**

- **Firmware image.** SUIT identifies an image by "A fingerprint computed over the component itself" and its size, plus component identifiers; vendor and class UUIDs "MUST NOT be used as assertions of identity"; the manifest sequence number is an anti-rollback counter (1.30). CoSWID offers `software-version` with a `version-scheme` and per-file hashes, where the algorithm may be unknown (`hash-alg-id` 0) when converted from ISO SWID (1.8). SLSA counts "a firmware image" as an artifact, so provenance can name it by digest (1.15). Firmware bills and device binding are agent 4's.
- **Vehicle software set.** UN R156's RXSWIN is "a dedicated identifier, defined by the vehicle manufacturer" for "type approval relevant software"; each must be "uniquely identifiable", is updated only when a change "leads to a type approval extension or to a new type approval", must be readable via the standard interface or replaced by declared software versions per ECU, and is backed by "an auditable register" of software versions and "integrity validation data" (checksums and hash values) (1.28). Our reading: an RXSWIN is an assigned, regulator-facing name for a set, and the register behind it is the computed part. ISO 24089:2023 was not read (paywalled); its public scope does not mention identification (1.29). Cross-link: RPT-0007 (#11).

### Dimension 7: identifier schemes

**Q1. What does each name, and is it assigned or computed from the bytes?**

- **purl**: a package in an ecosystem, optionally one version and one file inside it (subpath); assigned by the ecosystem's naming, though a version can be a digest (`oci`) and a `checksum` qualifier can carry a hash (1.1, 1.2).
- **CPE 2.3**: a product class, never an instance (IR 7695 §5); assigned (1.4).
- **SWID or CoSWID tag-id**: one tag for one software component release; assigned by the tag creator (1.8).
- **OmniBOR artifact id**: the exact bytes of one artifact, after CRLF normalization in the v0.2 draft; computed; an Input Manifest id names the set of build inputs (1.9).
- **SWHID**: a content, directory, revision (with author and commit metadata), release or snapshot; computed (1.10).
- **Cryptographic hash**: whatever bytes the producer hashed; computed; CycloneDX and SPDX `Hash` do not say which bytes (1.11).
- **OCI digest**: the exact bytes of a blob, manifest, index or config; computed; the ImageID is the config digest; tags are assigned pointers (1.12, 1.13).

**Q2. Who can mint one, and is there a canonical form?**

- **purl**: anyone. A canonical form is required (§2) but only partly defined: lowercase type, slash stripping, per-type case flags and prose normalization rules; qualifier order is informative only; the 2nd edition removes "canonical" from Clause 5; whether non-canonical input is valid is an open issue (#741) (1.1, 1.2).
- **CPE**: anyone can write a WFN-conformant name, but official names are minted only by NVD's dictionary; the WFN is an "abstract canonical form" with deterministic bindings, while value choice is out of scope (1.4, 1.6).
- **SWID tag-id**: the tag creator; uniqueness by UUID or DNS prefix, with no registry (1.8).
- **OmniBOR, SWHID, hashes, OCI digests**: anyone with the bytes; canonical syntax exists (gitoid URI; `swh:1:` grammar; `algorithm:encoded`), lowercase hex. A registry may return a "canonical digest" that "MAY differ from the provided digest" (1.13).

**Q3. Which databases and tools key on each?** (Table 3, "Keyed on by"; checked in each one's own documentation, code or API on 2026-10-08.)

- **NVD**: CPE match criteria resolved against the Official CPE Dictionary (1.7). Since 2026-06-17 it also passes through CNA "affected" data, which may contain a versionless `packageURL` (1.7).
- **OSV**: ecosystem plus name (required); versionless purl (optional in records; accepted by the API); git commit hashes in `GIT` ranges and the API's `commit` query (1.22).
- **GHSA**: ecosystem plus name only; no purl or CPE field (1.23).
- **deps.dev**: system, name and version; content hashes for six ecosystems; purls without qualifiers for seven types; OCI layer chain ids (1.24). No CPE, SWID, gitoid or SWHID in its API docs.
- **GUAC**: purl components (qualifiers split nodes), artifact `algorithm` plus `digest`, VCS source plus tag or commit (1.25). No OmniBOR, gitoid or SWHID (code search).
- **Dependency-Track**: coordinates, purl, CPE, SWID tag id and hashes in the policy engine (1.26); its NVD analysis needs a CPE (0.1.0 §3).
- **Attestation verifiers** (cosign, SLSA verifier, GitHub): artifact digests (1.14 to 1.19).

**Q4. How does each fail in practice?** Documented cases only:

- **purl**: two tools gave the same bytes different purls (Syft `distro=alpine-3.24.2` and `upstream=`, Docker Scout `os_name` and `os_version`; 1.20, 1.21), as SBOMproof found across tools (1.27); OSV.dev resolves `distro` only as a Debian codename or number and ignores the release for apk, so purl queries returned 0 where ecosystem queries returned 5 or 52 (1.22); GUAC treats differing qualifiers as different packages (1.25); type definitions contradict themselves (`golang`, `nuget`) and implementations emit non-canonical purls (#741, 1.2); the colon is percent-encoded in `oci` and `docker` examples and in Syft's output against ECMA-427 §5.4 (1.1, 1.2, 1.21); case differs between GHSA (`Jinja2`) and purl (1.23); deps.dev rejects qualifiers (1.24).
- **CPE**: generated, not looked up: all 81 pilot CPEs are `syft-generated`, 13 of 16 vendor:product pairs are not in the dictionary, none of the 16 full names is, and none of `libcrypto3`'s four candidates names openssl (1.7, 1.21); names are deprecated and replaced by design (1.6); NVD stopped publishing the XML dictionary (2025-08-20) and from 2026-04-15 adds product lists only to prioritized CVEs (1.7).
- **SWID tag-id**: uniqueness rests on the creator, with no registry, and collisions cause misidentification (RFC 9393 §9); Syft sets `tagId` to the distribution id `alpine` for every Alpine release (1.21); hashes converted from ISO SWID may have no algorithm (1.8).
- **OmniBOR**: the id of one file changed between v0.1 (SHA-1 or SHA-256, raw bytes) and the v0.2 draft (SHA-256 only, CRLF normalized); "sha1" may mean SHA-1 or SHA-1CD; CycloneDX 1.7's example still uses `gitoid:blob:sha1` (1.9).
- **SWHID**: the published directory serialization was wrong until 2026-09-19 (`'040000'` versus `'40000'`, issue #72); directories containing git submodules have no computable SWHID (issue #70, open); git compatibility is "incidental" (1.10).
- **Hashes**: "for which file" is undefined in CycloneDX (issue #96, open since 2021); SPDX `Hash` also leaves the bytes open; the pilot image has five SHA-256 values at different levels, Syft's SPDX output records the manifest digest as the image package's checksum, and no package has a hash (1.11, 1.20, 1.21).
- **OCI digests**: index versus platform manifest versus config (`docker` purl type prefers the "image id", i.e. the config digest, while `oci` and the attestations use the manifest digest); tags move; attestations attached to the index are invisible to the referrers API (1.2, 1.12, 1.13, 1.20).

**Q5. Which could be a stable Component key in a graph shared across organizations, and what must be stored with it?** Evidence and options only:

- **Computed ids (hash, OCI digest, gitoid, SWHID) are stable and checkable by anyone** (OCI digest rule 1.12; SWHID "without relying on a registry" 1.10), but they name bytes, not a component: one package version has different bytes as an archive, as installed files, and inside an image layer (1.21); OmniBOR and SWHID differ for the same file (1.9, 1.10). Stored with each: the scheme and its version (`swh:1`, OmniBOR spec version), the algorithm, and what was hashed (file content, archive, manifest, config, layer, diff_id).
- **A normalized purl is the closest shared name for a package version**: anyone can mint it, and OSV, deps.dev, GUAC, Dependency-Track and NVD's new "affected" data use it (Q3). Stored with it: the raw string as emitted, the producer (tool and version), the purl edition and type-definition version used to normalize it, and qualifiers kept separately, because tools disagree on them (1.20, 1.27) and GUAC would otherwise split nodes (1.25). Distribution packages need the release stated in a form each database understands (1.22).
- **CPE is a matching attribute, not a key**: it names classes (1.4), is often guessed (1.21), and is renamed by deprecation (1.6). Stored with it: `source` (dictionary or generated), NVD `cpeNameId`, `deprecated`, and the lookup date.
- **SWID tag-id works only for authoritative tags**: store the tag creator's `reg-id` and `tag-version` (1.8).
- **Precedent**: GUAC keeps packages (purl trie), artifacts (algorithm and digest) and sources (commit) as separate nodes, and links them by evidence nodes with a justification and origin (`IsOccurrence`, `PkgEqual`, `HashEqual`, 1.25). Section 5 turns this into candidate rules.

## 3. Table cells: Table 3 (identifier schemes)

`none` = absent; `?` = not found. "Keyed on by" covers NVD, OSV, GHSA, deps.dev, GUAC and Dependency-Track (DT), plus attestation verifiers where relevant; each entry was checked in that system's own docs, code or API on 2026-10-08 (section 2, dimension 7 Q3). vers is added as a companion row because the purl question asks for it; it is a version-range specifier, not an identifier.

| Scheme | Names what | Assigned or computed | Minted by | Canonical form | Version-specific | Carried in | Keyed on by | Known failure modes | Standard status | Library record |
|---|---|---|---|---|---|---|---|---|---|---|
| purl, ECMA-427 1st edition (Dec 2025); 2nd edition text = purl-spec v1.1.0 (2026-10-07) | a package in an ecosystem; optionally one version (`@version`) and a file inside it (`#subpath`) | assigned (ecosystem names); a version may be a digest (`oci`), and a `checksum` qualifier can carry hashes | anyone; types registered by the Package-URL community (42 at v1.1.0) | partly: lowercase type, slash stripping, per-type case flags and prose normalization rules; qualifier order only informative; 2nd edition drops "canonical" from Clause 5; non-canonical input still debated (#741) | only when `@version` is set; OSV and NVD "affected" use versionless purls for a package | CycloneDX `components[].purl`; SPDX 3.0.1 `packageUrl` (Package) or `externalIdentifier` type `packageUrl`; SWID none | OSV (optional `purl`; API accepts it), deps.dev (no qualifiers, 7 types), GUAC (purl trie), DT (identity and analysis), NVD (CNA `packageURL` without version, since 2026-06-17); GHSA none | tool-specific qualifiers for the same bytes (Syft `distro`/`upstream` vs Docker Scout `os_name`/`os_version`; SBOMproof Table 4); OSV.dev drops the apk release and reads `distro` only as a Debian codename or number (0 vs 52 results); GUAC splits nodes by qualifier; contradictory type definitions (`golang`, `nuget`); `%3A` in `oci`/`docker` examples and Syft output vs §5.4; GHSA case `Jinja2` | Ecma standard ECMA-427 (1st ed.); 2nd ed. TC54-approved for GA Dec 2026; ISO/IEC DIS 27056, stage 40.00 (file of 2026-10-07); IANA `pkg` provisional (2026-07-27) | none; proposed `ecma-427` (FX-1 candidate) |
| vers, vers-spec v1.2.1 (2026-10-07) | a set of versions of one package (version range) | assigned | anyone; vers types registered by the community (npm, pypi at v1.2.1) | yes: `vers:<type>/<constraints>`; canonical-only inputs adopted for the planned standard (#741 comment) | no (a range) | CycloneDX `component.versionRange`, `vulnerabilities[].affects[].versions[].range`; SPDX none; SWID none | none of the six found keying on it (OSV and NVD use their own range structures) | only linear versioning ("does not cover tree-based versioning"); not part of ECMA-427 | draft Ecma standard, approved for GA submission Dec 2026 | none; proposed `vers-spec` stub |
| CPE 2.3 (NIST IR 7695, 7696, 7697, Aug 2011) | a product class (application, OS or hardware), never an instance | assigned | anyone can form a WFN; official names minted by NVD's Official CPE Dictionary | yes: WFN is an "abstract canonical form" with deterministic bindings; values are not governed | only when `version` is set; `*`/ANY names all versions | CycloneDX `components[].cpe`; SPDX 3.0.1 `externalIdentifier` type `cpe22` or `cpe23`; SWID none | NVD (match criteria to dictionary `cpeNameId`), DT (identity; NVD analysis needs a CPE); OSV none; GHSA none; deps.dev none; GUAC none found | heuristic guesses (pilot: 81/81 `syft-generated`; 13/16 vendor:product absent from the dictionary; 0/16 full names present; no openssl candidate for `libcrypto3`); deprecation renames names; XML dictionary removed 2025-08-20; NVD product lists only for prioritized CVEs since 2026-04-15 | NIST IR, Final (Aug 2011); NVD-operated dictionary and API 2.0 | none; proposed `nistir-7695` (FX-1 candidate), `nistir-7696` and `nistir-7697` stubs, `nvd-cpe-apis` summary |
| SWID tag id (ISO/IEC 19770-2:2015) and CoSWID `tag-id` (RFC 9393) | one software component release as described by one tag; `persistent-id` names a related set | assigned | the tag creator (software provider = authoritative; others non-authoritative) | partial: binary form must be a UUID; text free-form (UUID or DNS prefix recommended); no `__` | yes (one tag per release; `tag-version` revises the tag, not the software) | CycloneDX `components[].swid.tagId`; SPDX 3.0.1 `externalIdentifier` type `swid` (CoSWID, RFC 9393 §2.3); CoSWID `tag-id` (index 0) | DT (SWID TagID identity); NVD, OSV, GHSA, deps.dev, GUAC none found | no registry, so collisions possible (RFC 9393 §9); Syft sets `tagId` to `alpine` for every Alpine release; ISO SWID hashes lack an algorithm id (`hash-alg-id` 0) | ISO/IEC 19770-2:2015 (90.60); RFC 9393 Standards Track (June 2023); IANA `swid`, `swidpath` provisional | none; proposed `rfc-9393` (FX-1 candidate); ISO/IEC 19770-2 stub (paywalled) |
| OmniBOR artifact id (gitoid), spec v0.1 (tag 2024-10-13) and v0.2 draft (main, 2025-11-17) | exact bytes of one artifact (git blob object); Input Manifest id names a build's inputs | computed | anyone with the bytes | yes: `gitoid:blob:<alg>:<lowercase hex>`; v0.2 normalizes CRLF to LF before hashing | yes | CycloneDX `components[].omniborId[]`; SPDX 3.0.1 `contentIdentifier` type `gitoid` (artifact) or `externalIdentifier` type `gitoid` (input manifest); SWID none | none of the six (GUAC, OSV.dev code search: 0 hits; DT only in vendored CycloneDX proto; not in deps.dev API docs) | ids change across spec versions (SHA-1 allowed in v0.1, SHA-256 only in v0.2; CRLF normalization added 2025-07-28); "sha1" may mean SHA-1 or SHA-1CD; CycloneDX 1.7 example still SHA-1 | community draft (Community Specification License 1.0); IANA `gitoid` provisional, "Unknown, use with care" | none; proposed `omnibor-spec` stub |
| SWHID v1.2 (swhid.org) = ISO/IEC 18670:2025 | content, directory, revision, release or snapshot (git-like objects) | computed (SHA-1 Merkle DAG) | anyone with the objects; no registry | yes: `swh:1:<type>:<40 hex>` grammar; qualifiers `origin`, `visit`, `anchor`, `path`, `lines`, `bytes` | yes (exact object) | CycloneDX `components[].swhid[]`; SPDX 3.0.1 `contentIdentifier` or `externalIdentifier` type `swhid`; SWID none | none of the six (code search and docs); OSV keys on git commit hashes, which a `rev` SWHID wraps for git repositories (our reading) | published directory mode text wrong until 2026-09-19 (#72); submodule directories uncomputable (#70, open); git compatibility "incidental"; SPDX 3.0.1 still cites "ISO/IEC DIS 18670" | ISO/IEC 18670:2025 published 2025-04-23 (60.60); IANA `swh` provisional | none; proposed `swhid-spec-1-2` (FX-1 candidate) and `iso-iec-18670-2025` stub |
| Cryptographic hashes (CycloneDX 1.7 `hashes`, SPDX 3.0.1 `Hash`, CoSWID `hash-entry`) | exact bytes of whatever the producer hashed | computed | anyone | value encodings defined (CycloneDX hex pattern; CoSWID raw bytes with IANA algorithm id; in-toto lowercase hex); which bytes is not defined, except SPDX `PackageVerificationCode` | yes | CycloneDX `hashes[]` (`alg`, `content`) on components and external references; SPDX 3.0.1 `verifiedUsing` (`Hash`), `PackageVerificationCode`; CoSWID `hash` on file resources | deps.dev (MD5/SHA1/SHA256/SHA512 for 6 ecosystems), GUAC (`Artifact` algorithm + digest), DT (hash identity, 12 algorithms); NVD, OSV, GHSA none | "for which file" undefined (CycloneDX #96, open since 2021); pilot packages have no hash (0/16); Syft's SPDX output gives the image package the manifest digest as its checksum; apk `pullChecksum` only as a Syft property; MD5/SHA-1 still allowed | format fields in ECMA-424 2nd ed. (CycloneDX 1.7) and SPDX 3.0.1; RFC 9393 | `cyclonedx-1-7`, `spdx-3-0-1` (queued; agent 1); `rfc-9393` proposed |
| OCI digest, image-spec v1.1.1 and distribution-spec v1.1.1 | exact bytes of a blob, image manifest, image index or config (ImageID = config digest); a tag is a mutable name pointing at a manifest | computed (digest); assigned (tag) | anyone (digest); repository owner (tag) | yes: `algorithm ":" encoded`, SHA-256 required; registry may return a different "canonical digest" | yes (digest); no (tag) | CycloneDX: no dedicated field (Syft puts the manifest digest in `metadata.component.version`; `hashes` or a `pkg:oci` purl could hold it); SPDX 3.0.1: no dedicated field (Syft SPDX 2.3: `versionInfo`, a SHA256 checksum and `pkg:oci` purl); SWID none | GUAC (`Artifact`), attestation verifiers (cosign, SLSA verifier, GitHub), registries (referrers API); deps.dev uses OCI layer chain ids instead; NVD, OSV, GHSA, DT none found | five SHA-256 values for one image (index, manifest, config, layer, diff_id); `docker` purl prefers the config "image id", `oci` and attestations the manifest digest; tags move; attestations in the index are invisible to the referrers API; SBOM outputs keep one unlabelled digest | OCI (Linux Foundation) specifications, not de jure; latest releases 2025-03-03 and 2025-01-29 | none; proposed `oci-image-spec-1-1-1` and `oci-distribution-spec-1-1-1` (FX-1 candidates) |

## 4. Table 7 ratings

0 = absent, 1 = mentioned or weak, 2 = partial, 3 = strong; within each source's own scope (rubric in dimensions.md, copied from RPT-0005). OSV, GHSA, deps.dev and Dependency-Track are rated by agents 3 and 5; the pilot outputs and the Docker Hub check are observations, not rated.

| Source | Object model | Provenance/attribution | Human review/audit | Federation | AI-grounding |
|---|---|---|---|---|---|
| ECMA-427 1st ed. and purl-spec v1.1.0 | 2: a purl ≈ Component as a package version (§1); no Product or instance types | 0: a purl carries no author or time | 0: none | 2: globally meaningful syntax that anyone mints (§5), but normalization is per type and partly prose (§6.5.7), and tools diverge (1.27) | 2: numbered clauses and versioned type files; 2nd edition pending |
| vers-spec v1.2.1 | 1: a range ≈ the version scope of an `affects` edge | 0 | 0 | 2: shared syntax, two registered types | 1: draft standard text |
| NIST IR 7695 (CPE naming) | 1: classes only, "They cannot identify product instances" (§5) | 0 | 0 | 2: WFN canonical form and bindings (§5.1, §6), values ungoverned (§5) | 3: final NIST text with clause numbers |
| NIST IR 7696 (CPE matching) | 1: set relations between names | 0 | 0 | 2: deterministic comparison (§4 conformance) | 3 |
| NIST IR 7697 (CPE dictionary) | 1: identifier names and deprecation links | 2: dictionaries "MUST capture the identifier name provenance data" (§4.2, item 5) | 1: deprecation records corrections (§6.2), no reviewer verdict | 2: one official dictionary plus extended ones (§4.2.1, §4.2.2) | 3 |
| NVD CPE APIs and 2025 to 2026 changes | 1: product names and match criteria ≈ applicability of a Vulnerability | 2: `created`, `lastModified`, `deprecated` per entry; no author field seen | 1: deprecation links | 2: NVD-minted `cpeNameId` and `matchCriteriaId` UUIDs, single authority | 2: stable ids retrievable by API; enrichment coverage reduced since 2026-04-15 |
| RFC 9393 (CoSWID) | 2: tag ≈ Component release with files, links and entity roles | 2: tag-creator entity and `generator`; `tag-version`; no timestamp field (0.1.0 §1.3) | 1: signatures only (§7) | 2: tag-id globally unique by rule, no registry (§9) | 3: Standards Track RFC, numbered sections |
| OmniBOR spec (v0.1, v0.2 draft) | 2: artifact ids and input manifests ≈ build-input graph for Components | 0: none in the ids | 0 | 2: computed by anyone, but the id changed between versions (§6.1.1, §6.1.2) | 1: draft text on `main` that changed in 2025 |
| SWHID v1.2 / ISO/IEC 18670:2025 | 1: source objects (content to snapshot), not Components | 1: `origin` and `visit` qualifiers give context (§6.3) | 0 | 3: computed, "without relying on a registry or a central authority" (§1) | 2: public v1.2 text; ISO text paywalled; recent defects (#70, #72) |
| OCI image-spec v1.1.1 | 2: index, manifest, config and layers ≈ ProductInstance and its parts | 1: optional annotations (`created`, `revision`, `source`) | 0 | 3: content addressing across any registry (descriptor.md, Digests) | 2: versioned spec in git |
| OCI distribution-spec v1.1.1 | 1: tags, referrers | 1: referrers associate attestations with a digest | 0 | 3: standard registry API and referrers | 2 |
| in-toto Attestation Framework v1.2.0 | 2: Statement ≈ an Assertion about a subject; ResourceDescriptor ≈ artifact identity | 2: attester through the envelope signature; no time field in the Statement | 1: verification predicates exist (VSA, SVR); no human verdict | 3: digest matching across organizations ("ANY acceptable field matches") | 2: versioned spec and predicate type URIs |
| SLSA 1.2 (record `slsa-1-2`) | 2: provenance ≈ a build Activity; builder ≈ Party | 3: `builder.id`, `invocationId`, `startedOn`, `finishedOn`, signed envelope | 2: VSA verification result (`verificationResult`, policy, inputs) | 3: digest-bound, any party verifies | 3: FX-1 record with requirement ids |
| Sigstore bundle v0.3 | 0: a packaging format | 3: certificate identity, transparency log entries, timestamps | 0 | 3: verifiable anywhere | 2: versioned media type |
| BuildKit attestations (v0.34.0 docs) | 1: attestation manifests tied to platform manifests | 2: SBOM generator and provenance included; legacy form unsigned (observed) | 0 | 2: index-attached legacy form not visible to referrers (1.20) | 2 |
| cosign v3.1.3 | 0 | 3: signed attestations with transparency log | 0 | 3: OCI 1.1 referrers by default in v3 | 2 |
| GitHub `actions/attest` v4.2.2 | 0 | 3: Sigstore-signed, workflow identity | 0 | 2: GitHub API by default; registry optional | 2 |
| GUAC v1.1.0 schema | 2: Package, Artifact, Source ≈ Component identities; `IsOccurrence`, `HasSBOM` ≈ composition assertions | 3: every evidence node has `origin`, `collector`, `documentRef`, `justification` | 0: no human verdict field | 2: purl and digest keys; node ids local to one GUAC instance | 1: ids are backend-local |
| UN Regulation No. 156 | 1: RXSWIN ≈ a ProductInstance software-set id for a vehicle type | 2: "auditable register" and SUMS documentation (§7.1.2.3) | 2: approval authority assesses the SUMS and type approval | 1: manufacturer-defined ids, no exchange format | 2: paragraph numbers; authentic text public via UN ODS |
| ISO 24089:2023 | not rated: not read (paywalled) | not rated | not rated | not rated | not rated |
| SUIT manifest draft-37 | 1: image digest, size and component ids ≈ firmware Component identity | 2: signed manifest, sequence number | 0 | 2: digests are global; vendor and class ids are compatibility checks only | 2: draft in the RFC Editor queue |
| SBOMproof (arXiv 2510.05798) | 0: evidence source, not a model | 0 | 0 | 0 | 2: stable arXiv id |

## 5. Applicability to the tmodel model (candidate Table 6 rows and rules)

Targets are ARCH-0001 §3 and, marked as draft, the proposal `0.2.0-proposed.11` and the LinkML draft 0.1.0. Format cells for SPDX and CycloneDX that RPT-0005 Table 2 already rates are cited, not redone. Every rule is a candidate for #15 and #17, not a decision.

| Model input | CycloneDX 1.7 | SPDX 3.0.1 | radar today | Fidelity | Rule (candidate) | Lost | Routes to |
|---|---|---|---|---|---|---|---|
| ProductInstance (draft 0.1.0; proposal §3b "identity-by-hash") | `metadata.component` (type `container`): `version`, `hashes`, `purl` | `Sbom.rootElement` Package: `packageVersion`, `verifiedUsing`, `packageUrl` | Syft JSON `source.metadata` has index, manifest and config digests, platform, tags; Syft CycloneDX keeps only the manifest digest in `version`; Grype-from-CycloneDX puts `bom-ref` in `imageID`; tradar stores Grype's block, unread (1.21, 1.32) | `≈` (one digest, level unlabelled) | R-ID-1: key on (algorithm, digest, media type) of the scanned platform manifest; keep index digest, config digest, platform, repository, tags (with time) and OCI annotations as attributes; same key on rescan = same instance | index and config digests, platform, tags, OCI `version`/`revision`/`source` annotations | DEC-001, DEC-009, ADR-0001 contract (#38, #15, #17) |
| Product (draft 0.1.0) | `metadata.component.name`, `group`, `supplier`, `manufacturer` | root Package `name`, `suppliedBy` | `alpine` (CycloneDX `name`, Grype `userInput`); no registry or repository | `≈` | R-ID-2: key on the versionless repository purl (for example `pkg:oci/alpine?repository_url=index.docker.io/library/alpine`); CoSWID `persistent-id` and Official CPE vendor:product as aliases; never derive a Product from a tag | registry, repository path, supplier | DEC-001, DEC-009 |
| Component identifier set (gap: no slot in 0.1.0) | `purl`, `cpe`, `swid`, `omniborId[]`, `swhid[]`, `hashes[]`, `evidence.identity` (RPT-0005 Table 2) | `packageUrl`; `externalIdentifier[]` (`cpe22`, `cpe23`, `packageUrl`, `swid`, `gitoid`, `swhid`, `issuingAuthority`); `contentIdentifier[]`; `verifiedUsing[]` | Syft: purl 16/16, CPE 16/16 plus 65 alternates, all generated, no package hashes (1.21); tradar graph keeps name, version, ecosystem only (0.1.0 §4) | `none` (no target) | R-ID-3: key a Component on its purl normalized by the type definition (type, namespace, name, version, type-required qualifiers only); keep the raw string, producer, purl edition and type-definition version; store other identifiers as (scheme, value, scheme version, source or issuing authority, producer) | every identifier except name and version | DEC-001, DEC-002, #17 (`unique_keys`, id patterns; RPT-0015 §4) |
| Artifact or content identity (gap: no type in 0.1.0) | `hashes[]` on file components; `omniborId`, `swhid` | `verifiedUsing`, `contentIdentifier` | 78 file components with SHA-1 and SHA-256; layer diff_id and apk `pullChecksum` only as Syft properties (1.21) | `none` | R-ID-4: a content node keyed on (algorithm, digest, what was hashed), linked to a Component by an occurrence Assertion (GUAC `IsOccurrence`); digest sets match if any accepted algorithm matches (in-toto) | all file and layer digests | DEC-001, DEC-004 |
| `composed_of` from SBOM inclusion | `components[]`, nested `components` (RPT-0005 Table 2) | `Sbom.element`, `contains` relationships | Syft lists 16 packages and Docker Scout 20 entries for the same digest (1.20); tradar keeps only vulnerable packages | `≈` (the draft puts `composed_of` on Product and Component, not ProductInstance) | R-MERGE-1: each SBOM's inclusion list for a subject digest is an Assertion with provenance (tool, version, time, SBOM digest); rescans and other tools add Assertions to the same instance; disagreements (origin packages, qualifiers) go to Review | which tool claimed which inclusion | DEC-001, DEC-009 |
| Identity equivalence (draft `Assertion`) | `evidence.identity` (`concludedValue`, `confidence`, `methods`) | none dedicated | none | `ext` | R-MERGE-2: merge two Components or Artifacts only through an equivalence Assertion with a justification (for example "same type-normalized purl", "same SHA-256"); heuristic mappings (qualifier spellings, CPE to purl) need a Review (GUAC `PkgEqual`, `HashEqual`) | today nothing is merged; duplicates appear (1.20) | DEC-001, DEC-004 |
| SBOM document (no target; PROV Entity in proposal §4) | `serialNumber`, `version`, `metadata.timestamp`, `metadata.tools` | document `spdxId`, `CreationInfo` (`created`, `createdBy`, `createdUsing`) | present in Syft output; ignored by tradar | `none` | R-PROV-1: an SBOM is evidence for composition Assertions, never a ProductInstance key (CycloneDX: a new serial number per generation) | all document metadata | DEC-001 (§4), ADR-0001 |
| Build record (gap; post-MVP per proposal §7) | `formulation` | `Build` (`buildType`, `buildId`, `configSourceDigest`, times) with `hasInput`, `hasOutput` | none: Syft and Grype do not fetch attestations; the registry holds SLSA v0.2 and SPDX attestations for the pilot image (1.20) | `none` | R-BUILD-1: attach provenance to a ProductInstance only by subject digest match; keep the attestation as an external Entity with its digest, predicate type and where it was found (SLSA record design note); the source commit becomes a source-revision node (GUAC `Source`) | everything | ADR-0001, DEC-001, DEC-009 |
| Vulnerability `affects` keys (agent 3 owns matching) | `vulnerabilities[].affects[].ref`, `versions[].range` (vers) | `hasAssociatedVulnerability`, `VulnAssessmentRelationship` (RPT-0005) | Grype matches; tradar keeps name, version, ecosystem | `⊂` (draft `affects` targets Product, LinkML lines 396 to 399, not Component) | R-ID-3 must keep CPE, purl and ecosystem-plus-name forms, with the distribution release explicit, because NVD, OSV and GHSA each key on a different one (section 2, dimension 7 Q3) | CPEs, purls, release | DEC-008, DEC-009 |
| Party via `supplied_by`, `manufactured_by` | `supplier`, `manufacturer`, `authors` | `suppliedBy`, `originatedBy` | Syft CycloneDX: no supplier (0/16); Docker's SBOM names a person per package (1.20); SLSA `builder.id` | `≈` | issuing-authority ids (CoSWID `reg-id`, purl namespace) as Party aliases; CPE vendor strings are names, not Party ids | suppliers | DEC-001 (R-036, post-MVP) |
| Firmware and vehicle instances (R-022) | `firmware` component with `hashes` | Package `primaryPurpose` `firmware`, `verifiedUsing` | none | `ext` | R-ID-5: firmware instance key = image digest plus component id (SUIT); vehicle software-set key = (manufacturer, vehicle type, RXSWIN), with the register's software versions and integrity data as linked Components | everything | DEC-001, DEC-009, RPT-0007 (#11), agent 4 |

**Trade-offs of the candidate rules.**

- R-ID-1 (instance = platform manifest digest) matches every verifier and the proposal's "identity-by-hash", but multiplies instances per platform and needs index digests kept for release-level questions (section 2, dimension 6 Q1, options A and B).
- R-ID-3 (Component = type-normalized purl) gives one shared key, but depends on type definitions that still contain errors (1.2) and on a release field that tools spell differently (1.20, 1.22); keeping the raw string lets a later fix re-normalize without data loss, which is the concern raised in purl-spec #741.
- R-MERGE-1 and R-MERGE-2 avoid silent merges, which matter because two correct tools disagree on the same bytes (1.20, 1.27), at the cost of more Assertions and Reviews; this fits the proposal's reified Assertion (§4) and ADR-0004's typed edges.

## 6. Library records (Table 9 rows)

Proposals follow #38's rule as dimensions.md states it (a spec record is FX-1 complete or an honest stub); Phase 2 confirms the list with the student, and the open question on which FX-1 trigger applies (dimensions.md, sponsor question 1) still stands. Proposed ids follow existing conventions (`rfc-NNNN`, `nistir-NNNN`, `ecma-424` on the `other` shelf).

| Source | Record id | Type | Status before → after | FX-1 artifacts | Notes |
|---|---|---|---|---|---|
| ECMA-427 1st edition (purl) | `ecma-427` (new, shelf `other`) | spec | none → FX-1 | all applicable: normative clauses, requirements, Annex A JSON Schema verbatim, examples, design notes | Table 3 and rule R-ID-3 rely on its clauses. Its keywords are lowercase "shall"/"should" (Ecma style), so the BCP 14 keyword count needs a stated method. The 2nd edition (GA Dec 2026) would be a new record linked by `supersedes`. |
| purl-spec v1.1.0 and type definitions | fold into `ecma-427` notes (or new `purl-spec-types`, dataset) | dataset | none → summary | not applicable: a changing registry of 42 JSON files, cited by tag | Pin the tag; type definitions change between releases. |
| vers-spec v1.2.1 | `vers-spec` (new) | spec (maturity draft) | none → stub | not applicable: cited for status and scope only | Revisit after the December 2026 GA. |
| NIST IR 7695 (CPE naming) | `nistir-7695` (new) | spec | none → FX-1 | all applicable (uppercase BCP 14 keywords present; ABNF in §5 and §6) | dimensions.md lists "CPE naming" as an FX-1 candidate; Table 3 relies on §5. |
| NIST IR 7696 (CPE matching) | `nistir-7696` (new) | spec | none → stub | not applicable: cited for one definition (one-to-one comparison) and the absence of ranges | |
| NIST IR 7697 (CPE dictionary) | `nistir-7697` (new) | spec | none → stub | not applicable: cited for dictionary authority and deprecation types | Upgrade to FX-1 if Table 6 adopts CPE deprecation handling. |
| NVD CPE and CPE Match APIs, NVD news 2025 to 2026, `cve_affected_1.0.json` | `nvd-cpe-apis` (new) | dataset | none → summary | not applicable: data source | Records the 2025-08-20 feed removal and the 2026-04-15 enrichment policy. |
| RFC 9393 (CoSWID) | `rfc-9393` (new) | rfc | none → FX-1 | all applicable, including the CDDL verbatim | dimensions.md names CoSWID as a candidate; Table 3 relies on §2.3, §2.9.1, §6.7, §9. |
| ISO/IEC 19770-2:2015 (SWID) | `iso-iec-19770-2-2015` (new) | spec | none → stub | not applicable: paywalled | dimensions.md sponsor question 4. |
| OmniBOR specification | `omnibor-spec` (new; pin commit `daf090f6` and tag `v0.1`) | spec (maturity draft) | none → stub | not applicable: a draft whose id rules changed in 2025; cited for algorithm and normalization rules | Fold the IANA `gitoid` registration in as an identifier. |
| SWHID specification v1.2 | `swhid-spec-1-2` (new) | spec | none → FX-1 | all applicable; short text | Table 3 relies on §4 to §6. |
| ISO/IEC 18670:2025 | `iso-iec-18670-2025` (new) | spec | none → stub | not applicable: paywalled | `see_also: swhid-spec-1-2`. |
| OCI image-spec v1.1.1 | `oci-image-spec-1-1-1` (new, shelf `community`) | spec | none → FX-1 | all applicable | Rules R-ID-1 and R-BUILD-1 rely on its digest, index and `subject` rules. |
| OCI distribution-spec v1.1.1 | `oci-distribution-spec-1-1-1` (new) | spec | none → FX-1 | all applicable, including protocol (referrers and fallback) | 0.1.0 sources.md already cites v1.1.1. |
| in-toto Attestation Framework v1 | `in-toto-attestation-v1` (existing) | spec | queued → FX-1 | all applicable; pin v1.2.0; set `version` and a spec `url` | Relied on for Statement, ResourceDescriptor, DigestSet and SBOM predicates; also cited by the proposal §4 and RPT-0013. |
| in-toto Envelope | `in-toto-envelope-v1` (existing) | spec | stub → stub (or fold into the FX-1 above) | not applicable | Its `topic: post-quantum-migration` looks misfiled. |
| SLSA v1.2 | `slsa-1-2` (existing) | spec | distilled → no change | present (FX-1 passes 1 to 3) | Verified current on 2026-10-08; human review (`reviewed_by`) still empty. |
| Sigstore bundle v0.3 | `sigstore-bundle-v0-3` (new) | spec | none → stub | not applicable: cited for the media type and the one-signature rule | Related stubs `sigstore-2022`, `sigstore-threat-model`. |
| BuildKit attestation docs v0.34.0 | `buildkit-attestations` (new) | repo | none → summary | not applicable: tool documentation | |
| cosign v3.1.3 | `cosign` (new) | repo | none → summary | not applicable: tool | Coordinate with agent 5. |
| GitHub `actions/attest` v4.2.2 | `github-actions-attest` (new) | repo | none → summary | not applicable: vendor tool | |
| UN Regulation No. 156 | `unece-r156` (new, shelf `regulator`) | spec | none → stub | not applicable now | Cited for §2.2, §2.11, §7.1.1.2, §7.1.2.3, §7.2.1.2; FX-1 candidate under RPT-0007 (#11); supplements not checked. |
| ISO 24089:2023 | `iso-24089-2023` (existing) | spec | stub → stub | not applicable: paywalled | Public scope only. |
| SUIT manifest draft-37 | `draft-ietf-suit-manifest` (new) | draft | none → stub | not applicable: cited for three identity fields | Agent 4 may extend; new record when the RFC is published. |
| SBOMproof (arXiv 2510.05798) | `sbomproof-2025` (new, shelf `academic`) | paper | none → summary | not applicable | |
| GUAC v1.1.0 | `guac` (existing) | repo | summarized → no change here | not applicable | Agent 5 owns it. |
| ISO Open Data deliverables metadata | none (as in 0.1.0) | dataset | none → summary or none | not applicable | Status lookups; ODC-By attribution. |
| Reproducible Builds definition | none (as in 0.1.0) | web | none → stub | not applicable | Re-checked 2026-10-08. |

## 7. searches.md rows

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-08 | 6, 7 | read scope and draft model: dimensions.md, report.md 0.1.0, searches.md, sources.md, RPT-0005 fan-out example, ARCH-0001 §3, proposal `0.2.0-proposed.11`, LinkML 0.1.0, OBJECT-MODEL.md, ADR-0001, ADR-0004, RPT-0015 §3 and §4 | local repository read | no identity slots in the draft; "identity-by-hash" and "CPE/purl" only in prose |
| 2026-10-08 | 6, 7 | library records: `slsa-1-2` (distilled files), `in-toto-attestation-v1`, `in-toto-envelope-v1`, `cyclonedx-1-7`, `spdx-3-0-1`, `iso-24089-2023`, `guac`, `osv-schema`, `secure-systems-lab-dsse`; `find` for purl, CPE, SWID, OmniBOR, SWHID, OCI, R156 records | local library read | no records for purl, CPE, RFC 9393, OmniBOR, SWHID, OCI, Sigstore bundle, R156 |
| 2026-10-08 | 7 | ECMA-427 Package-URL purl specification edition | WebSearch | ECMA-427 page and 1st edition PDF |
| 2026-10-08 | 7 | `gh api repos/package-url/purl-spec/releases`, tree at `v1.1.0`, PRs #1011 and #1012, issue #741, search "canonical in:title" | gh | v1.1.0 (2026-10-07) = 2nd edition text; "canonical" removed from Clause 5; #741 open |
| 2026-10-08 | 7 | `gh api repos/package-url/vers-spec/releases` and tree at `v1.2.1` | gh | vers approved for GA submission Dec 2026; 2 vers types |
| 2026-10-08 | 7 | ISO Open Data CSV filtered for 27056, 18670, 24089, 19770-2, 19770-6, 27055, 5962, 20153 | curl + python3 | DIS 27056 at 40.00; 18670:2025 published 2025-04-23 |
| 2026-10-08 | 7 | ISO harmonized stage codes "40.00" "DIS registered" "40.99" | WebSearch | iso.org PDF (403 to curl); certifico.com copy used |
| 2026-10-08 | 7 | NIST IR 7695, 7696, 7697 PDFs and CSRC status pages | curl + pdftotext | Final, August 2011; no supersession text |
| 2026-10-08 | 7 | NVD news page; `cve_affected_1.0.json` | curl + python3 | XML dictionary removed 2025-08-20; enrichment prioritized 2026-04-15; CNA `affected` with `packageURL` since 2026-06-17 |
| 2026-10-08 | 7 | NVD CPE API: zlib 1.3.1; 16 pilot CPEs as vendor:product and as full names (32 queries); CPE Match API for CVE-2022-37434 | curl + jq (NVD API 2.0) | 3 of 16 vendor:product pairs exist; 0 of 16 full names; 29 match strings |
| 2026-10-08 | 7 | RFC 9393 text; `grep` for purl, cpe, gitoid, swhid, omnibor | curl | 0 hits each; tag-id, hash-entry, §9 collision text |
| 2026-10-08 | 7 | `gh api repos/omnibor/spec` releases, tags, commits for `spec/SPEC.md`; SPEC.md at main and v0.1; `GITOID_URI.txt`; IANA `prov/gitoid` | gh + curl | v0.2 draft: SHA-256 only, CRLF normalization (2025-07-28) |
| 2026-10-08 | 7 | swhid.org specification v1.2 clauses 0, 1, 4, 5, 6; `gh api repos/swhid/specification` issues and commits | curl + gh | issues #70 (open), #72; '40000' restored 2026-09-19 |
| 2026-10-08 | 7 | CycloneDX schema 1.7.2 (`jq` on identity and hash definitions); CycloneDX and SPDX issue search "hash in:title" | curl + jq + gh | issue #96 open since 2021 |
| 2026-10-08 | 7 | SPDX 3.0.1 model TTL and class pages (Hash, PackageVerificationCode, ContentIdentifier, ExternalIdentifier, Build) | curl + python3 | `Hash` leaves bytes open; PVC discouraged |
| 2026-10-08 | 6, 7 | OCI image-spec and distribution-spec releases and tags; files at v1.1.1; tree at v1.1.0-rc2 to v1.1.1 for `artifact.md`; PR search "artifact manifest remove" | gh + curl | PR #999 removed the artifact manifest (2023-04-13) |
| 2026-10-08 | 6 | in-toto attestation releases; spec files at v1.2.0 | gh + curl | v1.2.0 (2026-03-18); SPDX 3 predicate added |
| 2026-10-08 | 6 | BuildKit latest release and `docs/attestations/*` at v0.34.0 | gh + curl | index-attached storage; OCI-artifact mode adds `subject` |
| 2026-10-08 | 6 | cosign latest release; `doc/cosign_attest.md`, `specs/*`, `attestation.go`; in-toto-golang v0.11.0 constants; v3.0.x release notes | gh + curl | predicate type mapping; v3 stores OCI 1.1 referring artifacts |
| 2026-10-08 | 6 | Sigstore protobuf-specs tags; `sigstore_bundle.proto` at v0.5.2 | gh + curl | bundle v0.3; one signature |
| 2026-10-08 | 6 | `actions/attest-sbom` and `actions/attest` releases and READMEs | gh + curl | digest-bound; GitHub attestations API by default |
| 2026-10-08 | 6, 7 | Docker Hub registry: tags `latest`, `3.24.2`, `3.24`, `3`; index; arm64 manifest and config; attestation manifest and both blobs; referrers API for manifest and index digests; fallback and cosign tags | curl (registry API v2) | five digests; SPDX 2.3 by Docker Scout; SLSA v0.2; empty referrers |
| 2026-10-08 | 7 | `jq` over pilot `alpine.cdx.json`, `alpine.syft.json`, `alpine.spdx23.json`, `alpine.grype.json` | jq | identifier counts; image digest levels; `imageID` = `bom-ref` |
| 2026-10-08 | 7 | `gh api search/code` in anchore/syft for `ManifestDigest` and `TagID`; files at v1.52.0 | gh + curl | decoder maps `bom-ref` to image `ID`; `TagID: distro.ID` |
| 2026-10-08 | 7 | OSV schema v1.9.1; OSV.dev query API doc; `go/purl` at `16b340c78a51`; 17 queries to `api.osv.dev/v1/query` | curl + gh + jq | apk purls 0 results; Debian purl depends on `distro` spelling |
| 2026-10-08 | 7 | GitHub REST API OpenAPI description (`/advisories` parameters, `global-advisory` schema); advisory file search `GHSA-cpwx-vrp4-4pq7` | gh + curl + python3 | ecosystem and name only; no purl or CPE |
| 2026-10-08 | 7 | deps.dev API v3 and v3alpha pages | curl + python3 | hash query (6 ecosystems); purl lookup without qualifiers; OCI chain ids |
| 2026-10-08 | 7 | GUAC latest release; schema files at v1.1.0 | gh + curl | qualifiers split package nodes; evidence nodes |
| 2026-10-08 | 7 | Dependency-Track component identity purl cpe swidTagId hashes internal analyzer documentation | WebSearch | docs.dependencytrack.org component-identity page (then fetched) |
| 2026-10-08 | 7 | `gh api search/code` for omnibor, gitoid, swhid in guacsec/guac, DependencyTrack/dependency-track, DependencyTrack/hyades-apiserver, google/osv.dev, google/deps.dev | gh | 0 hits except DT's vendored CycloneDX proto; google/deps.dev is not the service code |
| 2026-10-08 | 7 | empirical study SBOM generation tools inconsistent package identifiers purl CPE disagreement paper 2024 2025 | WebSearch | arXiv 2510.05798 (SBOMproof), 2601.05622, 2609.19920, 2606.02442; abstracts fetched, SBOMproof §4 read |
| 2026-10-08 | 6 | unece.org UN Regulation No. 156 software update management system R156e.pdf RXSWIN | WebSearch | no unece.org PDF in results; EU Publications Office entry |
| 2026-10-08 | 6 | "UN Regulation No. 156" supplement amendment ECE/TRANS/WP.29 RXSWIN | WebSearch | no supplement found; left open |
| 2026-10-08 | 6 | unece.org R156 PDF and documents page; op.europa.eu entry; EUR-Lex CELEX 42021X0388; UN ODS symbol ECE/TRANS/WP.29/2020/80 | curl | unece.org 403 (Cloudflare); OJ and UN ODS texts fetched |
| 2026-10-08 | 6 | datatracker API for draft-ietf-suit-manifest; draft text rev 37 | curl | RFC Editor queue; image digest, size, sequence number |
| 2026-10-08 | 6 | slsa.dev/spec/ (current version) | curl | "Version 1.2", "Approved" |
| 2026-10-08 | 6 | tradar `26d9c76`: `core/grype_integration.py`, `cli/cve.py` | gh | `scan_metadata` keeps Grype `source` and `descriptor` |
| 2026-10-08 | 7 | IANA URI schemes CSV; `prov/pkg`, `prov/gitoid` | curl | pkg, gitoid, swh, swid, swidpath all Provisional |

## 8. sources.md rows

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| ECMA-427, *Package-URL (PURL) specification*, 1st edition (Dec 2025), <https://ecma-international.org/wp-content/uploads/ECMA-427_1st_edition_december_2025.pdf> (SHA-256 `037180df…3825`) | spec | 7 | `ecma-427` (new, Phase 2) | DEC-001, DEC-002 |
| purl-spec v1.1.0 (ECMA-427 2nd edition text, type definitions, Annex B, issue #741), <https://github.com/package-url/purl-spec/tree/v1.1.0> | spec (draft edition) + dataset | 7 | fold into `ecma-427` | DEC-001, DEC-002 |
| vers-spec v1.2.1, <https://github.com/package-url/vers-spec/tree/v1.2.1> | spec (draft) | 7 | `vers-spec` (new, stub) | DEC-008 |
| NIST IR 7695, CPE Naming 2.3 (Aug 2011), <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7695.pdf> (`01553a46…c6f3`) | spec | 7 | `nistir-7695` (new) | DEC-002, DEC-008 |
| NIST IR 7696, CPE Name Matching 2.3 (Aug 2011), <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7696.pdf> (`966eecc1…1e45`) | spec | 7 | `nistir-7696` (new, stub) | DEC-008 |
| NIST IR 7697, CPE Dictionary 2.3 (Aug 2011), <https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7697.pdf> (`3e5b36aa…a6a5`) | spec | 7 | `nistir-7697` (new, stub) | DEC-008 |
| NVD Products and CPE Match APIs 2.0, NVD news page, `cve_affected_1.0.json` (fetched 2026-10-08) | data | 7 | `nvd-cpe-apis` (new) | DEC-008 |
| RFC 9393, *Concise Software Identification Tags* (June 2023), <https://www.rfc-editor.org/rfc/rfc9393.txt> (`6708be37…6ebc`) | rfc | 6, 7 | `rfc-9393` (new) | DEC-001, DEC-002 |
| OmniBOR specification v0.1 (tag) and v0.2 draft (main `daf090f6`), <https://github.com/omnibor/spec>; IANA `prov/gitoid` | spec (draft) | 7 | `omnibor-spec` (new, stub) | DEC-001, DEC-002 |
| SWHID specification v1.2, <https://www.swhid.org/specification/v1.2/>; issues #61, #70, #72 | spec | 7 | `swhid-spec-1-2` (new) | DEC-001, DEC-002 |
| ISO/IEC 18670:2025 (SWHID V1.2), metadata only | spec | 7 | `iso-iec-18670-2025` (new, stub) | DEC-002 |
| CycloneDX 1.7 JSON schema at `1.7.2` (identity and hash fields) and issue #96 | spec | 7 | `cyclonedx-1-7` (existing, queued) | DEC-002 |
| SPDX 3.0.1 model and class pages (Hash, PackageVerificationCode, ContentIdentifier, ExternalIdentifier, Build) | spec | 6, 7 | `spdx-3-0-1` (existing, queued) | DEC-002, DEC-004 |
| OCI Image Format Specification v1.1.1, <https://github.com/opencontainers/image-spec/tree/v1.1.1>; PR #999 | spec | 6, 7 | `oci-image-spec-1-1-1` (new) | DEC-001, DEC-009 |
| OCI Distribution Specification v1.1.1, <https://github.com/opencontainers/distribution-spec/blob/v1.1.1/spec.md> | spec | 6, 7 | `oci-distribution-spec-1-1-1` (new) | DEC-001 |
| in-toto Attestation Framework v1.2.0, <https://github.com/in-toto/attestation/tree/v1.2.0/spec> | spec | 6 | `in-toto-attestation-v1` (existing, queued) | DEC-001, DEC-004 |
| SLSA v1.2 (distilled record files) | spec | 6 | `slsa-1-2` (existing, distilled) | DEC-001, DEC-009 |
| Sigstore `sigstore_bundle.proto` at protobuf-specs v0.5.2 | spec | 6 | `sigstore-bundle-v0-3` (new, stub) | DEC-001 |
| BuildKit `docs/attestations` at v0.34.0 | tool docs | 6 | `buildkit-attestations` (new) | DEC-001 |
| cosign v3.1.3 docs, specs and `attestation.go`; in-toto-golang v0.11.0 constants | tool | 6 | `cosign` (new) | DEC-001 |
| GitHub `actions/attest` v4.2.2 and `actions/attest-sbom` v4.1.0 READMEs | tool docs | 6 | `github-actions-attest` (new) | DEC-001 |
| Docker Hub `library/alpine` index, manifests, config, attestations and referrers responses (2026-10-08) | data (observation) | 6, 7 | none (observation) | DEC-001, DEC-009 |
| Pilot outputs (Syft 1.52.0, Grype 0.119.0, 2026-10-08) and Syft v1.52.0 source files | tool output, code | 6, 7 | none (agent 5 owns tool records) | DEC-001, DEC-002 |
| OSV schema v1.9.1, OSV.dev API doc and `go/purl` at `16b340c78a51`, live queries | spec, code, data | 7 | `osv-schema` (existing, summarized) | DEC-008 |
| GitHub REST API OpenAPI description at `7dee0622`; GHSA-cpwx-vrp4-4pq7 | spec (API), data | 7 | none (agent 3) | DEC-008 |
| deps.dev API v3 and v3alpha docs | tool docs | 7 | none (agent 5) | DEC-002 |
| GUAC v1.1.0 GraphQL schema files | code | 6, 7 | `guac` (existing, summarized) | DEC-001, DEC-004 |
| Dependency-Track component identity docs | tool docs | 7 | none (agent 5) | DEC-002 |
| SBOMproof, arXiv:2510.05798 (2025-10-07) | paper | 7 | `sbomproof-2025` (new) | DEC-002 |
| UN Regulation No. 156, ECE/TRANS/WP.29/2020/80 (UN ODS) and OJ L 82 (2021-03-09) copy | spec (regulation) | 6 | `unece-r156` (new, stub) | DEC-001, DEC-009 |
| ISO 24089:2023, metadata only | spec | 6 | `iso-24089-2023` (existing, stub) | DEC-009 |
| draft-ietf-suit-manifest-37 | draft | 6 | `draft-ietf-suit-manifest` (new, stub) | DEC-001 |
| ISO Open Data `iso_deliverables_metadata.csv` (file of 2026-10-07) and ISO stage-code table (certifico.com copy) | dataset, guide | 7 | none | DEC-002 |
| IANA URI Schemes registry (2026-10-08) | registry | 7 | none | DEC-002 |
| Reproducible Builds definition, <https://reproducible-builds.org/docs/definition/> | guide | 6 | none | DEC-001 |
| tradar at `26d9c76` (`grype_integration.py`, `cli/cve.py`) | code | 6 | none | DEC-001 |

## 9. Rejected claims

Agent 2's own list of rejected claims was lost when it stopped at the usage limit; this section comes from an adversarial re-check of sections 1 to 8 by a second agent on 2026-10-08.

**How the re-check was done.** Each source was fetched again with `curl` or `gh api` and read from its own text. More than 100 of agent 2's recorded file hashes were compared with fresh downloads; all matched except the NVD news page, whose HTML changes between loads (its quotes were already confirmed by the main session, DL-0015). API responses carry timestamps, so they were compared by content. Syft 1.52.0 was run six times on `alpine` (linux/arm64, pulled straight from the registry with `--from registry`); Grype and Trivy were not run. NVD (National Vulnerability Database) and OSV.dev were queried live. WebSearch was not used. Sections 1 to 8 are unchanged; the main session decides what to correct. Below, CNA means a CVE Numbering Authority, the organization that publishes a CVE (Common Vulnerabilities and Exposures) record.

| what | where it came from | why rejected |
|---|---|---|
| "The CycloneDX output keeps only the manifest digest, in `metadata.component.version`"; also "on the SBOM path ... that block holds the manifest digest"; "CycloneDX and SPDX outputs keep only the manifest digest"; "Syft puts the manifest digest in `metadata.component.version`" | Headline 1; 1.21 ("The image, three ways"); 1.32; section 2, dimension 6 base question and Q3 item 1; Table 3, OCI digest row; section 5, ProductInstance row | Qualified: true only for the pilot's input, `alpine:latest`. Syft sets the root `version` from how the image was named: a tag other than `latest` is kept, a digest reference is kept, and only an empty or `latest` tag is replaced by the manifest digest (`syft/source/stereoscopesource/image_source.go` at v1.52.0, lines 61 to 67 and 86 to 87, SHA-256 `6cc1b59c…9e13779`; `to_format_model.go` lines 319 to 338). Runs on 2026-10-08 of the same bytes: `alpine:latest` gave `sha256:260479a1…`; `alpine:3.24.2` gave `"version": "3.24.2"` and 0 occurrences of the manifest digest in the file (`debb8cbd…5834`); `alpine@sha256:294b683c…` gave the index digest (`4ff6ad1b…4ca9`). Syft's decoder copies that value into `ManifestDigest` (`decoder.go` lines 237 to 240), so Grype's `manifestDigest` can hold a tag or an index digest (agent 5 observed `"12-slim"`). The container `bom-ref` is `artifact.IDByHash(metadata.ID)` (line 330), a hash of the image ID; it was `caf3142caa4aa41f` in all three runs. |
| "Syft JSON already has all of these" (the user's reference, each digest with its media type, os, architecture and variant, the repository, and "the tags seen at scan time with the time"); "Syft JSON `source.metadata` has index, manifest and config digests, platform, tags" | Section 2, dimension 6 Q3, item 1; section 5, ProductInstance row | Qualified. A re-run produced a Syft JSON file byte-identical to the pilot's (SHA-256 `1a8fd622…27fd`). In it `source.metadata.tags` is `[]`; there is no timestamp field (two runs gave identical bytes); `variant` (`v8`) appears only inside the base64 `config` blob; the index digest appears only inside a `repoDigests` string, with no media type; the config media type appears only inside the base64 `manifest`. Syft JSON carries the most identity data of the three outputs, but not the tags, a time, or a labelled variant. |
| "single-platform images have no index" | Section 2, dimension 6 Q1, option B ("against") | Rejected as stated. A single-platform image can be a bare manifest, but one with BuildKit attestations is stored in an index: "Attestations are stored as manifest objects in the image index", and BuildKit's own "Example showing an SBOM attestation attached to a `linux/amd64` image" is an index that "defines two descriptors: an AMD64 image `sha256:23678f31..` and an attestation manifest `sha256:02cb9aa7..` for that image" (`docs/attestations/attestation-storage.md` at v0.34.0, SHA-256 `9103a454…ee9d`). Correct: "single-platform images may have no index". |
| "0 of the 16 full names exist, because each version carries the Alpine release suffix" | 1.7, Observations, third bullet | Rejected as stated (the cause); the count held. All 32 queries were re-run (NVD CPE API, 2026-10-08, 19:46 to 19:50 UTC): `busybox:busybox` 165, `musl-libc:musl` 93, `zlib:zlib` 84, the other 13 pairs 0, all 16 full names 0. The suffix explains 1 name: for 13 names the vendor:product pair is absent, and without the suffix only `cpe:2.3:a:busybox:busybox:1.37.0` exists, while `zlib:zlib:1.3.2` and `musl-libc:musl:1.2.6` return 0 entries. |
| NVD listed under "Keyed on by" for purl: "NVD (CNA `packageURL` without version, since 2026-06-17)" | Table 3, purl row | Rejected as stated: NVD carries the CNA's purl but does not key on it. `GET /rest/json/cves/2.0?purl=…` and `?packageURL=…` both return HTTP 404 with "Invalid parameter: purl." and "Invalid parameter: packageURL." (2026-10-08), while `cpeName=` works. The carried value can name a source repository rather than a package: for CVE-2026-85091 (zlib) the response has `affected[].affectedData[].packageURL` `pkg:github/<owner>/zlib` (the zlib source repository; the owner, a person's account name, is omitted here), supplied by the CNA VulnCheck, with `vulnStatus` "Awaiting Analysis" (response SHA-256 `94fc5ce1…83a2`). Correct cell: "NVD: carried as CNA data, not a query key". |
| "OSV none" in "Keyed on by" | Table 3, CPE row | Qualified. OSV schema v1.9.1 defines the `Red Hat` ecosystem this way: "The ecosystem string has a `:<CPE>` suffix to scope the RPM to a specific Red Hat product stream. `<CPE>` is a translation of a Red Hat ... (CPE)" (`docs/schema.md`, "Defined ecosystems", SHA-256 `e5b87d62…307e`). Red Hat records are therefore keyed on a product-stream CPE (2.2 style) inside the ecosystem name; no other ecosystem in that table uses CPE. |
| "NVD, OSV, GHSA none" in "Keyed on by" | Table 3, cryptographic hashes row; section 2, dimension 7 Q3 (no hash key listed for OSV) | Qualified for OSV. OSV.dev documents an experimental `POST /v1experimental/determineversion`: "Given the source code hashes of C/C++ libraries, this endpoint attempts to find the closest upstream library and version"; `file_hashes` is "An array of MD5 hashes of each relevant file in the library to identify" (`docs/api/post-v1-determineversion.md` at `16b340c78a51`, SHA-256 `c9968b0d…02d6bc`; only C/C++ projects integrated into OSS-Fuzz). It identifies a version, which is then queried by name and version. NVD and GHSA: no content-hash field found (GHSA schemas: 0 hits for "hash" and "sha256"; NVD's `cve_affected_1.0.json`: one hit, the `repo` description "to resolve git hash version ranges", which concerns commit-hash version ranges, not content hashes). |
| "none of the six found keying on it (OSV and NVD use their own range structures)" | Table 3, vers row | Qualified. Dependency-Track 5.2.0 (released 2026-10-08) depends on `io.github.nscuro:versatile-core` 0.26.0 (`pom.xml`, SHA-256 `3be9885f…188b`). Its internal analyzer builds a `Vers` from the match criteria and tests `buildVers(criteria, versioningScheme).contains(targetVersion)` (`InternalVulnAnalyzer.java` lines 457 to 490, `a084bfbc…36d1`); its OSV importer converts OSV ranges with `versFromOsvRange` and stores `.setRange(vers.toString())` (OSV `ModelConverter.java` lines 75 and 578, `905f5a5b…cd96`). Our reading: vers is Dependency-Track's internal range form for matching, not a key read from SBOMs. |
| "canonical-only inputs adopted for the planned standard (#741 comment)" | Table 3, vers row, "Canonical form" | Qualified wording. The maintainer's comment of 2026-07-29 says: "We have not changed the VERS specification overall to only allow canonical inputs. What we have done is draw a clear boundary between requiring canonical inputs for conformance with the planned ECMA-VERS standard vs other specification use cases where an implementation/tool may choose to normalize inputs". The change is vers-spec pull request #65, "Require Normalized Vers" (merged 2026-05-13). Correct cell: "canonical input required for conformance with the planned standard; tools may still normalize". |
| "no package has a hash"; "pilot packages have no hash (0/16)" | Section 2, dimension 7 Q4 (hashes); Table 3, cryptographic hashes row | Qualified. True of CycloneDX `hashes` (0 of 16) and SPDX 2.3 `checksums` (0 of 16). But Syft's SPDX 2.3 output gives all 16 apk packages `filesAnalyzed: true` and a `packageVerificationCode` (zlib: `949e9364df447b0e30fad69d0104d85f0f26e51d`; re-run file `638dce95…bf2`), which is SPDX's own defined hash over a package's files (1.11). |
| "CycloneDX 1.7.2's `omniborId` example is `gitoid:blob:sha1:a94a8fe5…`"; "CycloneDX 1.7's example still uses `gitoid:blob:sha1`"; "CycloneDX 1.7 example still SHA-1" | 1.9 ("Formats lag the spec"); section 2, dimension 7 Q4; Table 3, OmniBOR row | Qualified. The schema gives two examples, `gitoid:blob:sha1:a94a8fe5ccb19ba61c4c0873d391e987982fbbd3` and `gitoid:blob:sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08` (`definitions.component.properties.omniborId.examples`, schema at tag 1.7.2, `73308ede…76ce`). Correct: "one of its two examples uses SHA-1, which the v0.2 draft no longer permits". |
| "CRLF normalization added 2025-07-28" | Table 3, OmniBOR row (1.9 gives the same date for commit `aa932090`) | Qualified date. The commit is dated 2025-07-28, but it reached `main` through pull request #84, opened 2025-07-28 and merged 2025-11-17 (merge commit `daf090f6`; GitHub API, 2026-10-08). Correct: "proposed 2025-07-28, merged into the draft 2025-11-17". |
| "Issue #72 (closed 2026-09-19) restored the directory mode `'40000'`"; "the published directory serialization was wrong until 2026-09-19" | 1.10 ("Documented defects"); section 2, dimension 7 Q4; Table 3, SWHID row | Qualified. #72 is a pull request, merged into `main` on 2026-09-19; it closed issue #61 ("Clarify directory permission format: 040000 vs 40000", opened 2025-11-09). Its text says the site "still serves the six-byte form under both `dev` and `v1.2`". The site served `'40000'` on 2026-10-08 (Core identifiers page, same SHA-256 as agent 2's, `8a6a0153…9b12`). So the repository text was fixed on 2026-09-19 and the published page between 2026-09-19 and 2026-10-08. |
| The RXSWIN rules quoted as unconditional ("Each RXSWIN shall be uniquely identifiable ...", readable through the OBD port, protected against modification), and the candidate key "(manufacturer, vehicle type, RXSWIN)" | 1.28; section 2, dimension 6 Q4; section 5, firmware and vehicle row (R-ID-5) | Qualified. Paragraph 7.2.1.2 sets a condition before 7.2.1.2.1 to 7.2.1.2.3: "7.2.1.2. Where a vehicle type uses RXSWIN:" (ECE/TRANS/WP.29/2020/80, SHA-256 `eed67194…b2a9`; same text in the published E/ECE/TRANS/505/Rev.3/Add.155, Wayback capture of 2023-12-16, `9a7b4192…cb5a8`). Our reading: R156 does not require every vehicle type to use an RXSWIN, so R-ID-5 needs another key when there is none, such as the software versions and "integrity validation data" that the software update management system must identify (§7.1.1.2). |
| "datatracker states 'RFC Ed Queue' and 'Submitted to IESG for Publication'"; "draft in the RFC Editor queue" | 1.30; section 4, SUIT row | Qualified (incomplete). The datatracker also gives the RFC Editor state "Blocked" (state type `draft-rfceditor`), next to the IESG (Internet Engineering Steering Group) state "RFC Ed Queue" (datatracker API, 2026-10-08, SHA-256 `ee0731e9…df2a`). The reason was not found: the RFC Editor's queue page is built by script. When it becomes an RFC is therefore uncertain. |
| "v3.0.0 notes: new capabilities are 'on by default' ..." | 1.18 ("Storage changed in v3") | Qualified locator; the quotes are verbatim. GitHub has no release v3.0.0, only a tag. The quoted "# v3.0.0" text is inside the v3.0.1 release body, which begins "v3.0.1 is an equivalent release to v3.0.0, which was never published due to a failure in our CI workflows." (SHA-256 `9bf404bb…fb96`), and in `CHANGELOG.md` at v3.1.3 (`0f526b6d…9cb4`). The first published v3 release is v3.0.1 (2025-10-08). |
| "same sentence in spdx3.md" | 1.14 ("Which field a digest matches is left to the predicate") | Qualified wording. spdx3.md reads "The `subject` contains whatever artifacts are to be associated with this SPDX document." (no "software"; `predicates/spdx3.md` at v1.2.0, `4297dc7a…bf59`). The point stands. |
| "a case-insensitive `grep` for purl, cpe, digest, hash, sbom, commit and version matches only the schema's own `version: 0.1.0` and the two description lines quoted above" | Section 2, dimension 6 Q1 ("No identity slot exists") | Qualified. The same `grep` also matches line 633 ("schema (not a committed query language ..."), because "committed" contains "commit". That line is not a slot, so the conclusion stands: 62 slots, one `identifier: true`, no `unique_keys` (schema SHA-256 `90ed014c…af77`, last changed in `bd6625c`). |
| "RPT-0015 §4 ... asks for id-string patterns that include 'CPE/purl'" | Section 2, dimension 6 Q1 | Locator. "no `unique_keys`" is in §4 (report.md line 156); the pattern list with "CPE/purl" is in §3, on what a proper schema must specify (line 126). |
| "OmniBOR, SWHID, hashes, OCI digests: ... canonical syntax exists ..., lowercase hex" | Section 2, dimension 7 Q2 | Qualified. Lowercase is required or recommended for OCI digests (`/[a-f0-9]{64}/` for `sha256`, `descriptor.md`), SWHIDs (grammar `<hex_digit>` is 0 to 9 and a to f) and gitoids ("should be expressed as a hexadecimal string in lower case", `GITOID_URI.txt` line 23), but not for hashes in general: CycloneDX `hash-content` accepts `[a-fA-F0-9]`, and SPDX 3.0.1 `hashValue` has no pattern. |
| Note: CISA 2026 asks "for hashes named by IANA textual names, which none of the formats uses" | Agent 1's note to agent 2 (fanout-formats-baselines.md, section 10) | Qualified. The CISA sentence is verbatim: "The SBOM author should identify the algorithm using Internet Assigned Numbers Authority (IANA) Hash Function Textual Names." (IC3 copy, SHA-256 `1faeda1e…3873`, p. 12). But IANA's registry (CSV `f80a6ba1…a5d`) cites RFC 8122, whose names are defined in ABNF (Augmented Backus-Naur Form), and "ABNF strings are case insensitive" (RFC 5234 §2.3). Our reading: CycloneDX's `MD5`, `SHA-1`, `SHA-256`, `SHA-384` and `SHA-512` are IANA textual names apart from letter case; SPDX 3.0.1 (`sha256`) and CoSWID (integer ids) do not use them; CycloneDX's SHA-3, BLAKE and Streebog values have no IANA textual name. |
| Note: "Ubuntu's OSV purls carry versions" | Agent 3's note to agent 2 (fanout-bridge.md, section 10; its 1.8) | Qualified by copy. True of Canonical's files: UBUNTU-CVE-2025-60876 has `pkg:deb/ubuntu/busybox@1:1.21.0-1ubuntu1.4+esm1?arch=source&distro=esm-infra-legacy/trusty` (canonical/ubuntu-security-notices, SHA-256 `4a6a1dad…9e0d`, the same file agent 3 read). OSV.dev serves the same record with `pkg:deb/ubuntu/busybox?arch=source&distro=esm-infra-legacy%2Ftrusty`: version removed, slash percent-encoded (api.osv.dev, 2026-10-08, `d42ffb53…cf47`). Which copy a tool reads changes the purl. |

**Claims that held: 75 of the 95 re-checked.** The other 20 are the first 20 rows above (3 rejected as stated, 17 qualified); the two rows marked "Note" come from other agents' notes and are not counted. What was checked and held:

- **purl.** ECMA-427 1st edition (edition, adoption by the December 2025 General Assembly, 40 pages, every quoted clause, the licence texts, and 0 hits each for "sort", "order" and "lexicograph"); Ecma's "ISO/IEC number DIS 27056"; purl-spec release dates and the v1.1.0 release text; the 42 type files; pull request #1012 and Clause 2 lines 20 to 21; Annex B (and `distro`, `upstream`, `os_name`, `os_version` absent from it and from `common-qualifiers.md`); the `apk`, `docker`, `oci`, `golang` and `nuget` type texts; issue #741 (open since 2025-11-06) and all four quotes; the 2nd edition's "a warning, not an error" rule.
- **vers.** Release dates and notes, the two registered types, Clause 5 quotes; CycloneDX `versionRange` (external components only); SPDX 3.0.1 without vers.
- **CPE.** IR 7695, 7696 and 7697 quotes (including the Table 7 locator, §4.2 item 5); the zlib 1.3.1 dictionary entry; CVE-2022-37434 (29 match strings, zlib `versionEndIncluding` 1.2.12, 80 matches); 3 of 16 pairs and 0 of 16 full names; the NVD news page's latest item (2026-08-26); `cve_affected_1.0.json` (same hash).
- **SWID and CoSWID.** RFC 9393 quotes, section numbers and the zero-hit `grep`; IANA statuses (`pkg` registered 2026-07-27, "It is standardized as ECMA-427"); Syft's `tagId` `alpine` (lines 173 to 175).
- **OmniBOR and SWHID.** Both OmniBOR texts (SHA-256 only, newline normalization, SHA-1CD); IANA and repository "Scheme Creator"; SWHID v1.2 pages (same hashes) and quotes; issue #70; ISO/IEC 18670:2025 metadata; "none of the six" for both (also 0 hits in GHSA's schemas and NVD's affected schema).
- **Formats.** CycloneDX 1.7.2 identity and hash definitions (14 algorithms, hex pattern, no `pattern` on identity fields, `evidence.identity`, `serialNumber`) and issue #96; SPDX 3.0.1 model and the five class pages (same hashes), `Build` cardinalities, identifier types, "(ISO/IEC DIS 18670)", OmniBOR commit `eb1ee5c`, release date 2024-12-17.
- **OCI.** v1.1.1 of both specifications is still the latest release and tag; every quote; `artifact.md` and pull request #999.
- **Attestations.** in-toto v1.2.0 (dates, eight file hashes, quotes, the CycloneDX predicate's URI inconsistency); Sigstore bundle v0.3 (no GitHub releases, tag commit 2026-08-21, one-signature rule); BuildKit v0.34.0 quotes and the `v1` default; cosign v3.1.3 (`--type` text, `switch` at lines 172 to 195, predicate constants, spec quotes, `go.mod`); GitHub `actions/attest` and `attest-sbom`.
- **Registry.** Four tags to one index; 16 index entries (8 plus 8) and their annotations; the five digests (layer 4,187,659 bytes); the legacy attestation manifest; the SBOM attestation (9 subjects, SPDX 2.3 by Docker Scout 1.18.1, 20 packages, 4 origin packages, 10 `GENERATED_FROM`, 78 files with SHA-1 and SHA-256, no CPE); the provenance details; empty referrers responses (same hash) and six 404 tags.
- **Pilot and Syft.** Every count in 1.21 (16, 78, 1; 16 of 16 purls and CPEs; 81 `syft-generated` CPEs; 65 `syft:cpe23` properties; 10 `upstream=`; `libcrypto3`'s four candidates; `pullChecksum` and `gitCommitOfApkPort` only as properties; the SPDX 2.3 root package; the `grep` counts); the cited source lines.
- **Databases and tools.** OSV schema v1.9.1 quotes; OSV.dev `go/purl` lines (only the Debian parser reads `distro`; the Go API imports this package, `query_affected.go` line 21); all 17 OSV query results (5, five 0s, 52, 52 byte-identical, 0, 82, 82, 6 and 6 with the same ids, four 0s); GHSA's 13 ecosystems, `affects` text and 0 purl or CPE properties (including referenced schemas); GHSA-cpwx-vrp4-4pq7; deps.dev quotes (6 hash ecosystems, 7 purl types, 0 hits for swhid, gitoid, omnibor, cpe, swid); GUAC v1.1.0 schema quotes; Dependency-Track identity page (12 algorithms); SBOMproof's quotes and Table 4.
- **Regulation, drafts, status.** R156 quotes and paragraph numbers in both copies, entry into force and "authentic and legally binding text"; ISO 24089 metadata and scope; SUIT draft-37 quotes and section numbers; the ISO Open Data rows (file of 2026-10-07, 81,585 rows).
- **Repository and library.** tradar `26d9c76` lines; LinkML counts and line numbers; the proposal, ARCH-0001, ADR-0001 and ADR-0004 lines; RPT-0015 §4 "no `unique_keys`"; the Reproducible Builds definition and slsa.dev's "Version 1.2" (same hashes); the SLSA record's distilled quotes; the statuses of the eight library records and the absence of every proposed id.

## 10. Open items, and notes for other agents

Written by the second agent on 2026-10-08 from its re-check; agent 2's own open items were lost.

### Open items (dimensions 6 and 7, Table 3)

1. **Which bytes the apk `pullChecksum` covers** (1.21; Table 3, hashes row). The Alpine wiki now answers with a bot challenge (HTTP 307 to a "goaway" page), and the apk-tools documents `apk-v2(5)` and `apk-package(5)` (GitHub mirror, `master` at `44dcdfc2`) do not define the installed-database checksum. Close: read apk-tools 3.0.8 source (`src/package.c`, `src/database.c`) or the wiki in a browser.
2. **What Grype does with a tag or an index digest in the CycloneDX root `version`** (section 9, first row). Only Syft's decoder was read; Grype was not run. Close: Grype runs on Syft CycloneDX files made from `alpine:latest`, `alpine:3.24.2` and `alpine@sha256:294b683c…` (agent 5's lane; this re-check's files were not kept, only their SHA-256 values in section 9). It decides whether Grype's `manifestDigest` can be trusted for rule R-ID-1.
3. **How Syft chooses a platform without `--platform`** (option A says it "depends on the machine", our reading). Close: read stereoscope's platform selection, or scan without `--platform` on an amd64 host.
4. **Whether re-attesting changes an index digest** (option B, our reading). Not tested. Close: a BuildKit push of the same image with and without new attestations to a test registry.
5. **ISO/IEC 18670:2025 against SWHID v1.2**: whether the ISO text has `'40000'` or `'040000'`, and whether it covers submodules (#70). Close: the paywalled ISO text.
6. **ISO/IEC 19770-2:2015** is still unread (dimensions.md, sponsor question 4); Table 3's SWID row rests on RFC 9393.
7. **Why the SUIT draft is "Blocked"** at the RFC Editor (section 9). Close: the RFC Editor queue in a browser.
8. **ISO stage-code meanings** (1.31) come from a secondary copy (certifico.com) because iso.org blocks scripted fetches, and ISO Open Data's container cannot be listed (HTTP 404). Close: iso.org's stage-code page in a browser.
9. **Dependency-Track identity kinds** come from the v4 documentation site, while the latest release is 5.2.0. Close: the v5 documentation or its policy code (for "SWID TagID" and hash identity).
10. **Code-search "0 hits"** (OmniBOR, gitoid, SWHID in GUAC, OSV.dev and Dependency-Track) cover only files GitHub has indexed on default branches. Close: clone at the pinned tags and `grep`, which would make those Table 3 cells exhaustive.
11. **How often NVD's carried purls can match an SBOM.** The one sample (CVE-2026-85091) names the zlib GitHub repository (`pkg:github/<owner>/zlib`), not distribution packages. Close: a sample of 2026 CVE responses, counting purl types.
12. **R156 after 2021**: supplements and amendments were not checked, so it is not known whether §7.2.1.2 changed. Close: the WP.29 document list for R156.
13. **CycloneDX 2.0-dev `identifiers[]`** (agent 1's note) was not re-checked. Close: read the 2.0-dev component schema at a pinned commit before Table 3 cites it.

### Notes received from other agents

**From agent 1** (fanout-formats-baselines.md, section 10):

- *Syft's `"swid": {"tagId": "alpine"}` cannot meet RFC 9393's "MUST be globally unique".* Checked: holds (re-run CycloneDX output; `to_format_model.go` lines 173 to 175). Already in 1.21 and Table 3; no change.
- *CERT-In's `pkg:supplier/OrganizationName/ComponentName@Version?qualifiers&subpath` uses a `supplier` purl type.* Checked against the type registry only (the CERT-In text was not re-read): `supplier` is not one of the 42 types at purl-spec v1.1.0. The 2nd edition's new Clause 5.7 says: "If the PURL **type** is not registered, then the **type** component is valid if it conforms to the rules stated in the _Type_ component rules in this Clause of the Standard. In this case an implementation should report a warning that the PURL **type** is not registered." Change: add to Table 3's purl failure modes "unregistered types prescribed by policy guidance (CERT-In), valid with a warning under the 2nd edition". Report: §7 Q4 and §8.
- *CycloneDX 2.0-dev replaces `purl`, `cpe` and the rest with `identifiers[]` naming the asserting party, with 25 schemes.* Not checked (open item 13). If confirmed: Table 3's "Carried in" needs a note that 2.0-dev drops the 1.x fields, and Q5 gains a format that already stores "identity claim plus asserting party", as R-ID-3 proposes. Report: §7 Q5 and §1 ("what comes next").
- *CISA 2026 asks for all identifiers and for hashes named by IANA textual names, which none of the formats uses.* Checked: both CISA sentences are verbatim (p. 12). CISA 2026 also names the schemes: the field "should use common software identifiers, such as Common Platform Enumeration (CPE) and Package-URL (PURL)" and "may also include universally unique identifiers (UUID), organization-specific identifiers, commit hashes, and intrinsic identifiers such as OmniBOR and Software Hash Identifier (SWHID)", and "If there are multiple software identifiers, the SBOM author should include all of them." The "none of the formats" part is qualified (section 9, first "Note" row). Change: Q5's advice to store every identifier matches CISA; Table 3 could mark purl and CPE as "named by CISA 2026" and OmniBOR and SWHID as "allowed by CISA 2026". Report: §7 Q5 and Table 2.
- *ISO/IEC DIS 27056 is at 40.00.* Checked: holds (ISO Open Data, file of 2026-10-07). Already in 1.31.

**From agent 3** (fanout-bridge.md, section 10):

- *CVE 5.2.0 `packageURL` is checked only as a URI.* Checked: `definitions.product.properties.packageURL` is `$ref: #/definitions/uriType` (a string with `"format": "uri"`, 1 to 2048 characters), and "The Package URL MUST NOT include a version." is prose only (CVEProject/cve-schema v5.2.0, released 2025-10-29, `CVE_Record_Format.json` SHA-256 `33f75174…de67`). SPDX 3.0.1's `packageUrl` likewise has range `xsd:anyURI`, and CycloneDX's `purl` has no pattern (1.11). Change: Table 3's purl "Canonical form" can add "no carrying format or record schema checks purl syntax beyond URI form". Report: §7 Q2.
- *Ubuntu's OSV purls carry versions.* Checked: true of Canonical's files, not of OSV.dev's copy (section 9, second "Note" row). Change: Table 3 purl failure mode "the same record has different purls in its source file and in OSV.dev". Report: §5 and §7 Q4.
- *osv.dev adds purls that GitHub's files lack.* Checked: OSV.dev's copy of GHSA-cpwx-vrp4-4pq7 has `{"name": "jinja2", "ecosystem": "PyPI", "purl": "pkg:pypi/jinja2"}` (`343a0678…6349`), while GitHub's file has `"Jinja2"` and no purl (1.23); OSV.dev also lowercases the name. Change: 1.23's "a consumer keyed on `pkg:pypi/jinja2` must normalize the case first" applies to GitHub's own data, not to OSV.dev's copy. Table 3's "GHSA none" stays for GitHub's data; agent 3's count supports it and was reproduced here from the same tarball (SHA-256 `0c227c74…4a24`): 382,210 files, 0 of 67,514 `affected` entries with a purl (36,616 reviewed advisories hold 67,511 of them). Report: §5 and §7 Q3.
- *Syft's apk purls carry `distro=` and `upstream=`, which Grype uses.* First half checked (16 of 16 carry `distro=alpine-3.24.2`, 10 of 16 carry `upstream=`); Grype's use was not checked (Grype not run). No change.
- *vers v1.2.1 registers only `npm` and `pypi`.* Checked: holds (tree at tag `v1.2.1`). Already in 1.3.
- *CPE vendor naming inconsistency in NVD (Anwar et al., about 10% of vendors in 2018).* Checked: "The NVD includes ≈19K distinct vendors, and about 10% of them were impacted by vendor naming inconsistencies." (arXiv:2006.15074v1, SHA-256 `19c91664…afa`; "a snapshot of NVD captured on May 21, 2018"). Change: Table 3's CPE failure modes can add "inconsistent vendor names inside NVD itself (about 10% of ≈19K vendors in a 2018 snapshot)". Report: §7 Q4 (CPE), with the date.

**From agent 4** (fanout-hardware.md, section 10):

- *Unit identity candidates: "TCG Platform Serial Number, SPDM hardware identity keys, DICE and EAT UEIDs, Redfish `SerialNumber` and `UUID`"* (TCG: Trusted Computing Group; SPDM: Security Protocol and Data Model; EAT: Entity Attestation Token, whose `ueid` is the "Universal Entity ID", RFC 9711 §4.2.1). Not checked (agent 4's sources). Change: dimension 6 Q1's evidence table has no row for one physical unit; these would fill a "ProductInstance (one physical unit)" row, next to RXSWIN and SUIT. Report: §6 Q1 and Q4, with Table 4.
- *Firmware SBOMs use the UEFI ESRT GUID as the CoSWID `tag-id`.* Not checked (agent 4 quotes the uswid README: "for UEFI firmware this is typically the ESRT GUID value"). It fits RFC 9393, where a binary tag-id "MUST be a valid Universally Unique Identifier (UUID)" (§2.3). Change: Table 3's SWID row, "Minted by", can note that firmware vendors reuse the GUID that already names the updatable firmware. Report: §2 and §7.
- *The Firmware Embedded SBOM Spec's VEX product id `pkg:<GUID>` (§6.1.1) appears to lack the purl type and name structure.* Checked against ECMA-427 only (the firmware specification was not read here): "All required components of a PURL, such as the scheme, type, and name, shall be present" (§2), Table 1 marks `name` "Required", and "The type shall start with an ASCII letter" (§5.6.2). Our reading: `pkg:` followed directly by a GUID has no name, so it is not a conforming purl. Change: Table 3 purl failure mode "purl-shaped strings that are not purls". Report: §2 (firmware VEX) and §7 Q4.
- *R156 §2.2 and §7.1.2.3 are in `R156e.pdf` (SHA-256 `9a7b4192…cb5a8`).* Checked: the Wayback capture of 2023-12-16 has that SHA-256; it is E/ECE/TRANS/505/Rev.3/Add.155 of 2021-03-04 and has the same paragraphs, including the §7.2.1.2 condition (section 9). The live unece.org URL still returned HTTP 403 on 2026-10-08. Change: 1.28 can cite the published Add.155 text as well as ECE/TRANS/WP.29/2020/80. Report: §6 Q4.

**From agent 5** (fanout-tools.md, section 10):

- *Syft and Trivy purls for the same package differ.* Not checked (Trivy was not run). It agrees with SBOMproof's Table 4 (1.27). Change: Table 3's purl failure modes can cite agent 5's run as a second observed pair. Report: §3 and §7 Q4.
- *Syft's `package-id` in `bom-ref` is stable across runs.* Checked: two runs (2026-10-08, 19:44 UTC) differ only in `serialNumber` and `metadata.timestamp` (CycloneDX) and in `created` and `documentNamespace` (SPDX 2.3); every `bom-ref` is identical. The container `bom-ref` also stayed `caf3142caa4aa41f` across `alpine:latest`, `alpine:3.24.2` and the digest reference. Change: none to Table 3; Table 6's "key a Component by its purl (not by `bom-ref`)" still holds, because the value is Syft's own hash. Report: §10.
- *The SPDX 3 `spdxId` IRI is not stable.* Checked: 382 of 383 `spdxId` strings are the same in two runs, but they are prefixed names (for example `SPDXRef:Package-apk-busybox-6cb7d4b8a66ff2bf`) whose prefix the document's `namespaceMap` maps to `https://anchore.com/syft/image/alpine-<random UUID>#`, so every expanded IRI differs between runs (files `eff7fb3e…95d4` and `99378915…6a8f`). Holds. Change: Table 1 "Element identity" and rule R-PROV-1: Syft's SPDX 3 element IRIs are per document. Report: §1 and §10.
- *The CycloneDX root `version` is the tag for tagged images, and Grype copies it into `manifestDigest`.* Checked: the first half by runs, the second half by Syft's decoder (section 9, first row); Grype not run.
- *Syft writes a zero SHA-1 for undigested files in SPDX.* Checked in source: "for now we include a 0 sha1 digest as requested by the spdx spec", used when a location has no digest and "the file is most likely a symlink or non-regular file" (`syft/format/common/spdxhelpers/to_format_model.go` at v1.52.0, lines 699 to 706, SHA-256 `d14f72af…6e0d`). Not seen on the pilot image (78 of 78 files have digests). Change: Table 3's hashes failure modes can add "placeholder values (an all-zero SHA-1)". Report: §7 Q4.
- *`uv.lock` hashes are not carried.* Not checked.
- *Trivy's apk SHA-1 equals the apk `pullChecksum` (which bytes?).* Not checked (Trivy); which bytes is open item 1.
- *deps.dev resolves a wheel hash from `uv.lock` and a jar SHA-256 to a package version.* Checked for a wheel: `GET /v3/query?hash.type=SHA256&hash.value=…` with the SHA-256 of `jinja2-3.1.4-py3-none-any.whl` (from PyPI's JSON API) returned `{"system": "PYPI", "name": "jinja2", "version": "3.1.4"}` (`60cc4d99…2fa2`); the jar case was not checked. Change: supports Table 3's hashes row (deps.dev); Q5 can say that a release-artifact hash resolves to a package version where the ecosystem publishes artifact hashes, which the pilot's apk packages do not. Report: §3 and §7 Q5.

### Notes for the main session and later phases

- **Phase 2 (library records).** `ecma-427`: pin both texts (the 1st edition PDF, and purl-spec v1.1.0 for the 2nd edition, including the new Clause 5.7); count normative keywords as Ecma verbal forms (lowercase "shall"). `unece-r156`: use the published Add.155 (Wayback capture, `9a7b4192…cb5a8`) as the artifact, name ECE/TRANS/WP.29/2020/80 as the authentic text (OJ copy), and record the §7.2.1.2 condition. `osv-schema` (agent 3): add the `Red Hat` ecosystem's CPE suffix, OSV.dev's experimental `determineversion` endpoint, and OSV.dev's re-serialized purls. `cve-json-5` (existing, `summarized`): CVE 5.2.0's `packageURL` is a `uriType`. Dependency-Track (agent 5): `versatile` (vers) is its internal range engine in 5.2.0.
- **Phase 5 (report).** §6 Q1, Q3 and Table 6: use section 9's first two rows. The CycloneDX root `version` cannot carry identity, and no current output carries a labelled digest set together with tags and a capture time, so the contract has to ask for them explicitly. Table 3: apply the corrections in section 9 and add the failure modes listed above (unregistered or malformed purls, copies of one record that disagree, placeholder hashes, inconsistent NVD vendor names). §6 Q4 and R-ID-5: the RXSWIN condition. §12 (limits): code-search coverage, and the pages that block scripts (NVD developer pages, the RFC Editor queue, the Alpine wiki, unece.org, iso.org).
- **dimensions.md (suggestions).** Table 3 could gain a column "Named by policy" (CISA 2026 names CPE and purl and allows OmniBOR, SWHID, UUIDs and commit hashes; BSI per agent 1), or fold it into "Standard status". Dimension 6 Q1 could add "how the image was named" (tag, `latest`, digest) as a test variable, since it changes what the SBOM records.
- **RPT-0005.** NVD's CVE API now returns CNA `affected` data (CVE-2026-85091) and refuses `purl` as a query parameter; OSV.dev serves Ubuntu purls without versions and adds purls to its GHSA copies.
- **RPT-0007 (#11).** R156 §7.2.1.2 makes the RXSWIN duties conditional; the published Add.155 text is reachable through the Wayback capture; supplements after 2021 are unchecked; ISO 24089 is still unread.
- **RPT-0014.** purl-spec v1.1.0 registers `huggingface` and `mlflow` types (model identity). CISA 2026 (p. 5) says CISA and its G7 partners released joint guidance, the "Software Bill of Materials for AI" minimum elements, in May 2026: the document agent 1 could not fetch.

### searches.md rows (re-check)

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-08 | 6, 7 | read fanout-identity.md sections 1 to 8, dimensions.md 0.3.0, pilot.md, DL-0015 "Phase 1 fan-out", and section 10 of the four other fan-out files | local repository read | 4 sets of notes for agent 2 |
| 2026-10-08 | 7 | purl-spec releases; tree at `v1.1.0`; Clauses 2, 5, 6; Annex B; `common-qualifiers.md`; `how-to-build.md`; 2nd edition release notes; type schema 1.1; 7 type files; pull request #1012; issue #741 and comments | gh + curl | hashes as agent 2 recorded; 42 types; no `supplier` type; `deb` defines only `arch` |
| 2026-10-08 | 7 | vers-spec releases, tree and Clause 5 at `v1.2.1`; pull request #65 | gh + curl | `npm` and `pypi` only; #65 merged 2026-05-13 |
| 2026-10-08 | 7 | ECMA-427 1st edition PDF; Ecma landing page | curl + pdftotext | same hashes; 0 hits for sort, order, lexicograph |
| 2026-10-08 | 6, 7 | ISO Open Data CSV filtered for 27056, 18670, 19770-2, 19770-6, 24089, 27055, 5962; container listing | curl + python3 | same file (2026-10-07); stages as reported; listing HTTP 404 |
| 2026-10-08 | 7 | NIST IR 7695, 7696, 7697 PDFs | curl + pdftotext | same hashes; quotes verbatim |
| 2026-10-08 | 7 | NVD CPE API: 16 pairs and 16 full names; 3 names without the Alpine suffix; zlib 1.3.1; CPE Match API for CVE-2022-37434 | curl + jq (NVD API 2.0) | 3 of 16 pairs; 0 of 16 names; without suffix only busybox 1.37.0 exists |
| 2026-10-08 | 6, 7 | NVD CVE API with `purl=`, `packageURL=`, `cpeName=`; CVE-2026-85091; news page; `cve_affected_1.0.json`; developer page | curl | purl and packageURL refused (HTTP 404); CNA `affected` with a `pkg:github/…/zlib` purl; developer page is a script shell |
| 2026-10-08 | 6, 7 | RFC 9393, RFC 8122, RFC 5234, RFC 9711 | curl | 0 hits for purl and others in RFC 9393; "ABNF strings are case insensitive" |
| 2026-10-08 | 7 | IANA URI schemes CSV, `prov/pkg`, `prov/gitoid`; Hash Function Textual Names CSV and page | curl | all Provisional; 9 hash names; reference RFC 8122 |
| 2026-10-08 | 7 | OmniBOR spec releases, tags, `SPEC.md` history; `SPEC.md` at `v0.1` and `main`; `GITOID_URI.txt`; pull request #84 | gh + curl | #84 opened 2025-07-28, merged 2025-11-17 |
| 2026-10-08 | 7 | SWHID pull request #72, issues #61 and #70; v1.2 pages (index, Scope, Syntax, Core identifiers, Qualified identifiers) | gh + curl | #72 is a pull request merged 2026-09-19; `'40000'` served |
| 2026-10-08 | 7 | CycloneDX schema 1.7.2 (`jq`); release list; issue #96 and comments | curl + gh + jq | two `omniborId` examples (SHA-1 and SHA-256) |
| 2026-10-08 | 6, 7 | SPDX 3.0.1 model and five class pages; spdx-spec releases | curl + python3 | same hashes; `packageUrl` range `xsd:anyURI` |
| 2026-10-08 | 6, 7 | OCI image-spec and distribution-spec releases and all tags; files at `v1.1.1`; `artifact.md` at four tags; pull request #999 | gh + curl | no newer release; quotes verbatim |
| 2026-10-08 | 6 | in-toto attestation releases; 8 spec files at `v1.2.0` | gh + curl | spdx3.md says "whatever artifacts" |
| 2026-10-08 | 6 | Sigstore protobuf-specs releases and tags; `sigstore_bundle.proto` at `v0.5.2` | gh + curl | 0 releases; tags only |
| 2026-10-08 | 6 | BuildKit releases; three attestation documents at `v0.34.0` | gh + curl | single-platform example stored in an index |
| 2026-10-08 | 6 | cosign releases and `v3.0.0` tag; v3.0.1 notes; `CHANGELOG.md`, docs, specs, `attestation.go`, `go.mod` at `v3.1.3`; in-toto-golang `v0.11.0` constants | gh + curl | no v3.0.0 release; its notes are in the v3.0.1 body |
| 2026-10-08 | 6 | `actions/attest` and `attest-sbom` releases and READMEs | gh + curl | quotes verbatim |
| 2026-10-08 | 6, 7 | Docker Hub registry: 4 tags, index, arm64 manifest, config, attestation manifest, 2 blobs, referrers for 2 digests, 6 fallback and cosign tags | curl (registry API v2) | as agent 2 reported; referrers response hash identical |
| 2026-10-08 | 6, 7 | Syft 1.52.0 runs (`--from registry --platform linux/arm64`): `alpine:latest` twice (CycloneDX, Syft JSON, SPDX 2.3); `alpine:3.24.2`; `alpine@sha256:294b683c…`; `alpine:latest` twice as SPDX 3 | syft (local run) | Syft JSON byte-identical to the pilot's; root `version` is the manifest digest, a tag or the index digest; `tags: []`; `bom-ref` stable; SPDX 3 IRIs change |
| 2026-10-08 | 6, 7 | Syft v1.52.0 source: `image_source.go`, `decoder.go`, CycloneDX and SPDX `to_format_model.go`, cpegenerate README | curl | version logic; zero SHA-1 fallback |
| 2026-10-08 | 7 | OSV.dev API: 17 queries; GHSA-cpwx-vrp4-4pq7; UBUNTU-CVE-2025-60876; an Ubuntu query (UBUNTU-CVE-2024-13176) | curl (api.osv.dev) | results as agent 2 reported; Ubuntu purls served without versions; GHSA copy has a purl |
| 2026-10-08 | 7 | OSV.dev source at `16b340c78a51` (`go/purl`, `query_affected.go`, `docs/api`); osv-schema v1.9.1 `schema.md` and releases | gh + curl | only the Debian parser reads `distro`; `determineversion` takes MD5 file hashes; `Red Hat` ecosystem has a CPE suffix |
| 2026-10-08 | 7 | canonical/ubuntu-security-notices `osv/cve/2025/UBUNTU-CVE-2025-60876.json` | curl | versioned purls in the source file |
| 2026-10-08 | 7 | GitHub REST API description at `7dee0622`; GHSA-cpwx-vrp4-4pq7 file; advisory-database tarball at `0d77cdb5` | gh + curl + python3 | 13 ecosystems; 0 purl or CPE; 0 of 67,514 entries with a purl |
| 2026-10-08 | 7 | deps.dev v3 and v3alpha pages; hash query for the jinja2 3.1.4 wheel (SHA-256 from PyPI's JSON API) | curl | same page hashes; resolves to PYPI jinja2 3.1.4 |
| 2026-10-08 | 7 | GUAC latest release; 8 schema files at `v1.1.0` | gh + curl | same hashes |
| 2026-10-08 | 7 | Dependency-Track component identity page; releases; `pom.xml`, `InternalVulnAnalyzer.java` and OSV `ModelConverter.java` at 5.2.0 | curl + gh | `versatile-core` 0.26.0; vers ranges in the internal analyzer |
| 2026-10-08 | 7 | code search: omnibor, gitoid, swhid in guacsec/guac, google/osv.dev, DependencyTrack/dependency-track, DependencyTrack/hyades-apiserver; versatile in dependency-track | gh search/code | 0 hits except Dependency-Track's vendored CycloneDX proto; rate limit hit once, then retried |
| 2026-10-08 | 7 | SBOMproof (arXiv 2510.05798v1) abstract and PDF; Anwar et al. (arXiv 2006.15074v1) PDF | curl + pdftotext | same hashes; quotes verbatim |
| 2026-10-08 | 6, 7 | CISA 2026 Minimum Elements (IC3 copy); CVE schema releases and `CVE_Record_Format.json` at `v5.2.0` | curl + gh + pdftotext | p. 12 identifier and hash-name sentences; p. 5 G7 mention; `packageURL` is `uriType` |
| 2026-10-08 | 6 | UN R156: UN ODS (ECE/TRANS/WP.29/2020/80); EUR-Lex OJ copy; live unece.org `R156e.pdf`; Wayback capture of 2023-12-16 | curl | quotes verbatim; §7.2.1.2 condition; unece.org HTTP 403; Wayback copy has agent 4's hash |
| 2026-10-08 | 6 | SUIT draft-37 text; datatracker document and its 7 states; RFC Editor queue page | curl | IESG "RFC Ed Queue"; RFC Editor "Blocked"; queue page built by script |
| 2026-10-08 | 6 | tradar `main` and two files at `26d9c76`; LinkML draft, proposal, ARCH-0001, ADR-0001, ADR-0004, RPT-0015 | gh; local read + python3 | unchanged; 62 slots; `grep` also hits line 633; "CPE/purl" in RPT-0015 §3 |
| 2026-10-08 | 6 | reproducible-builds.org definition; slsa.dev/spec; library records (nine) and proposed ids | curl; local library read | same hashes; statuses as reported; no proposed id exists yet |
| 2026-10-08 | 7 | apk-tools GitHub mirror (`doc/apk-v2.5.scd`, `doc/apk-package.5.scd`); Alpine wiki "Apk spec" | gh + curl | installed-database checksum not defined there; wiki behind a bot challenge |
| 2026-10-08 | 6, 7 | WebSearch | none | not used; every check fetched a known URL, API or tool |
