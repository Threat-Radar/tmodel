---
schema: "archdoc/v1"
id: RPT-0004-pilot
title: "RPT-0004 Phase 1 pilot: one real composition through the mapping table"
type: research
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: RPT-0004
---

# RPT-0004 Phase 1 pilot: one real composition through the mapping table

Step 1 of the Phase 1 plan in [dimensions.md](dimensions.md): push one real composition through Table 6 (the composition → model-input mapping) to test its rows and columns, and fill Table 3's rows for purl and CPE. It ran in the main session, without sub-agents, at the same time as the five fan-out agents (they do not fill Table 6; DL-0015 records why the order changed). Every fact below was checked against the tool outputs, the CycloneDX 1.7.2 JSON Schema, the SPDX 3.0.1 model file and the LinkML draft. The outputs and downloads stay outside the repository; their SHA-256 values are in §1.

The model inputs come from the LinkML draft (`spec/schema/tmodel-object-model.linkml.yaml`, 0.1.0) and the ARCH-0001 proposal (`0.2.0-proposed.11`). Nothing in them is accepted. Every "rule" below is a candidate, not a decision.

## 1. The run

| | |
|---|---|
| Date | 2026-10-08, 17:30 UTC |
| Input | `alpine:latest`, resolved by Syft for linux/arm64 |
| Commands | `syft alpine:latest -o cyclonedx-json=alpine.cdx.json -o syft-json=alpine.syft.json -o spdx-json=alpine.spdx23.json`; `grype sbom:alpine.cdx.json -o json`; `grype sbom:alpine.cdx.json -o cyclonedx-json` |
| Tool versions | Syft 1.52.0 and Grype 0.119.0 (both built 2026-09-17), the same versions as the 0.1.0 runs. Grype database schema v6.1.10, built 2026-10-08T06:33:47Z (Alpine data captured 00:34:20Z, NVD data 00:35:27Z). |
| Image digests | Syft JSON `source.metadata`: `manifestDigest` `sha256:260479a1cfaf…` (the linux/arm64 image manifest), `imageID` `sha256:33bee74c45f3…` (the image configuration), `repoDigests` `index.docker.io/library/alpine@sha256:294b683cb724…` (the multi-platform index). Checked against the registry: `alpine:latest` is an OCI image index (`application/vnd.oci.image.index.v1+json`, digest `sha256:294b683c…`) listing eight platform manifests, one of them linux/arm64/v8 `sha256:260479a1…`, and eight entries marked `attestation-manifest`. |
| Outputs (not committed) | `alpine.cdx.json` `057c616b81fe…`, `alpine.syft.json` `1a8fd622fb31…`, `alpine.spdx23.json` `236c3f6e90e2…`, `alpine.grype.json` `97e45336b412…`, `alpine.grype.cdx.json` `3f907409cd13…` |
| Reference files | CycloneDX `bom-1.7.schema.json` at tag `1.7.2` (`73308edec3ab…`, same as RPT-0005's); SPDX `spdx-model.ttl` 3.0.1 (`30ebb4af2d70…`) and `spdx-context.jsonld` 3.0.1 (`c72b0928f094…`) |

0.1.0 recorded the image as `sha256:260479a1...` on 2026-09-28; its first eight hex characters, the only part 0.1.0 kept, match today's platform manifest digest.

## 2. What the SBOM holds

From Syft's CycloneDX output (`specVersion` 1.7):

- **Document.** `serialNumber` `urn:uuid:dd9def15-…`, `version` 1, `metadata.timestamp`, and `metadata.tools` naming Syft 1.52.0. No `metadata.lifecycles`, `supplier`, `manufacturer` or `authors`. No `compositions`, `vulnerabilities`, `formulation` or `annotations`.
- **The product.** `metadata.component` is `{type: container, name: alpine}`, and its `version` holds the platform manifest digest, not a release number. That depends on how the image was named: Syft writes the digest only for `latest`. Named `alpine:3.24.2`, the version is `3.24.2`; named by the index digest, it is that digest (main session, Syft 1.52.0, 2026-10-08, after the re-check of agent 2's notes in fanout-identity.md §9).
- **Components.** 95: 16 `library` (the apk packages), 78 `file`, 1 `operating-system` (Alpine 3.24.2, with a `swid` block whose `tagId` is `alpine`).
- **Package identifiers.** All 16 packages have a `purl` and a `cpe`; none has `hashes` or a `supplier`. All 16 have a `publisher`: the apk maintainer (a person's name and email address). Every CPE is a guess: Syft's JSON marks all 81 candidate CPEs `syft-generated`, the CycloneDX output keeps one per package in `cpe` and moves the other 65 into `syft:cpe23` properties, and in 15 of the 16 `cpe` values the vendor and the product are the same word.
- **Upstream (source) packages.** 10 of the 16 purls carry an `upstream=` qualifier, for example `libcrypto3` and `libssl3` (`upstream=openssl`) and `busybox-binsh` and `ssl_client` (`upstream=busybox`).
- **Files.** All 78 file components carry SHA-1 and SHA-256 hashes.
- **Relationships.** `dependencies` has 12 entries with 24 `dependsOn` edges. Syft's own JSON has the same 24 edges as `dependency-of`, written with the dependency as the parent (`musl` → `libssl3` means `libssl3` depends on `musl`), plus 94 `contains` edges (image to package, package to file) and 16 `evident-by` edges. None of the `contains` or `evident-by` edges appears in the CycloneDX output: its component list is flat.

## 3. What Grype matched

From Grype's JSON output:

- **30 matches, 15 CVEs, 6 packages** (`busybox`, `busybox-binsh`, `ssl_client`, `libcrypto3`, `libssl3`, `zlib`).
- **One match came from Alpine's own feed.** CVE-2026-85091 on `zlib`: namespace `alpine:distro:alpine:3.24`, match details `exact-direct-match` and `exact-indirect-match` from the `apk-matcher`, version constraint `< 1.3.2-r1 (apk)`, and a fix (`1.3.2-r1`, state `fixed`, first observed 2026-10-07).
- **29 matches came from NVD CPE data.** All `cpe-match` against namespace `nvd:cpe`: 13 OpenSSL CVEs on both `libcrypto3` and `libssl3` (Grype searched `cpe:2.3:a:openssl:openssl:3.5.8:*:*:*:*:*:*:*`, the upstream's CPE), and CVE-2025-60876 on `busybox`, `busybox-binsh` and `ssl_client` (constraint `<= 1.37.0`). None of the 29 names a fix version: the fix state is `unknown` for 26 and empty for 3.
- **CWEs.** Every match carries `vulnerability.cwes[]` as `{cve, cwe, source, type}`. All 30 are `Secondary`, from three sources: `openssl-security@openssl.org`, `disclosure@vulncheck.com`, and a source that Grype names only by the UUID `134c704f-9b21-4f2e-91b3-4a467353bcc0`. That UUID is CISA's Authorized Data Publisher (ADP) container, `CISA-ADP` ("CISA ADP Vulnrichment"), in the CVE record of CVE-2025-60876 (cveawg.mitre.org API, checked 2026-10-08; found by agent 3, fanout-bridge.md).
- **Scores.** Each vulnerability also carries `cvss[]` (with its source and type), `epss[]` (with a date) and a `risk` number.
- **Grype's CycloneDX output keeps less.** It has 30 `vulnerabilities` entries (one per match), each with one `affects` entry. Only the zlib entry adds a `vers` range (`vers:apk/>=1.3.2-r1`, marked `unaffected`); the other 29 list only the affected version. It has no `cwes`, no `analysis`, no properties, and nothing about the match type or matcher. Its 30 `affects[].ref` values point at Grype's own re-emitted components, not at Syft's SBOM: none of the 30 equals a `bom-ref` in Syft's file, because Grype wraps the original `bom-ref` inside a new `package-id` qualifier (URL-encoded). Decoding that qualifier gives back the original `bom-ref` for all 30 (our check). Its one CVSS 4.0 vector is written with `method: other`, although the 1.7 schema's `scoreMethod` list includes `CVSSv4`.

**The same image gave a different answer ten days apart.** On 2026-09-28, 0.1.0's run (same tool versions, same digest prefix) found 4 matches for 2 CVEs, all from NVD CPE data (0.1.0 §3 and §5). Today it found 30 matches for 15 CVEs, and the zlib match now comes from Alpine's feed with a fix. The bytes did not change; the vulnerability database did. A match is therefore a claim about one SBOM, one database snapshot and one matcher, not about the component alone.

## 4. Table 6, filled for this composition

Columns as revised by this pilot (§5): the fidelity mark sits in each source cell. "tradar keeps" is what reaches tradar's graph or saved files, from the 0.1.0 report §4 (tradar's `main` is unchanged since `26d9c76`). The SPDX 3.0.1 column comes from the model file only, because the pilot did not ask Syft for SPDX 3 output. (0.1.0 §3 says Syft cannot write SPDX 3. That is wrong: Syft has written SPDX 3.0.1 with `-o spdx-json@3.0` since version 1.46.0, found by agent 5 in fanout-tools.md and confirmed in the main session with Syft 1.52.0 on 2026-10-08.) A cell marked `?` waits for the fan-out.

| Model input (draft 0.1.0) | CycloneDX 1.7 | SPDX 3.0.1 (model file) | Syft and Grype output (this run) | tradar keeps | Rule (candidate) | Lost | Routes to |
|---|---|---|---|---|---|---|---|
| **Product** | `metadata.component` (`type: container`, `name`) ≈ | `Software/Sbom` `rootElement` ≈ | `source.name` (`alpine`), `source.metadata.userInput` (`alpine:latest`) ≈ | none: no container node is built | one Product per image repository; the tag is not part of it, because a tag moves | the registry host, unless kept | #15, DEC-001 |
| **ProductInstance** ("versioned, identity-bearing"; identity-by-hash, proposal §3b) | a digest in `metadata.component.version` ≈ (only for `latest`; a tag gives the tag, a digest reference gives that digest) | the root element's `verifiedUsing` (`Hash`) or `contentIdentifier` ≈ | `manifestDigest`, `imageID`, `repoDigests` = | none: Grype's `source` block (with `manifestDigest`) is saved but never read | `id` from the platform manifest digest; the index and configuration digests as aliases. One index then maps to one ProductInstance per platform (eight here) | which digest was used, unless recorded | #15, #17, DEC-001 (dimension 6) |
| **Component** | `components[]` of `type` `library` or `operating-system` = | `Software/Package` = | `artifacts[]` (16 apk packages) = | ⊂: name, version and ecosystem, only for the 6 vulnerable packages | one Component per package, not per file; files stay as evidence (their hashes) | everything except name and version (see the next rows) | #15, #17 |
| Component identifiers (target: none; only `Node.id`, although proposal §1 says "Component (CPE/purl, shared)") | `purl` (16/16), `cpe` (16/16), `swid` (OS only), `hashes` (0 of 16 packages), `bom-ref` (local) | `packageUrl`; `externalIdentifier` (`cpe23`, `packageUrl`, `swid`, `gitoid`, `swhid`); `verifiedUsing` | `purl`; `cpes[]` (81, all `syft-generated`); Syft's package `id` | none: purl only for display and a CSV export | key a Component by its purl (not by `bom-ref`, which adds Syft's `package-id`); keep each other identifier with its source (`syft-generated` versus a dictionary) | all identifiers | #17, DEC-002 (Table 3) |
| Version (target: none on Component, Product or ProductInstance) | `components[].version` | `packageVersion` | `artifacts[].version` | kept | needs a slot, or must be encoded in `id` or `name` | the version scheme (apk `-r` revisions) | #17 |
| Component kind (target: none) | `components[].type` (`library`, `file`, `operating-system`, `container`) | `primaryPurpose` (`library`, `operatingSystem`, `container`, `firmware`, `device`, …) | `artifacts[].type` (`apk`, an ecosystem, not a kind) | the ecosystem | needs a slot; R-022 needs software and hardware kinds | the kind | #17, R-022 |
| **`composed_of`** (on Product and Component only) | flat `components[]`; nesting through `components[].components` exists but is not used here | `contains` relationship | `contains` (94: image to package, package to file) | none | the packages listed in this SBOM; package-to-file containment kept as evidence only | Syft's 94 `contains` edges never reach the CycloneDX file | #15 |
| **`depends_on`** | `dependencies[].dependsOn` (24 edges) = | `dependsOn`, and the finer `hasStaticLink`, `hasDynamicLink`, `hasOptionalDependency`, `hasProvidedDependency`, `hasPrerequisite` ≈ | `dependency-of` (24, direction reversed) = | none | one edge per `dependsOn`; reverse Syft's `dependency-of`; keep SPDX's finer type as a qualifier | edge types and completeness | #15, DEC-001 |
| **`uses_component`** ("use edge along which vuln/finding propagation is sound") | ? | ? | ? | none | not fillable: the draft does not say how it differs from `depends_on` | | #15 |
| **Party**, through `supplied_by` and `manufactured_by` (on Product only) | `metadata.supplier`, `metadata.manufacturer` (both absent here) =; `components[].supplier` (0/16); `publisher` (16/16) ≈ | `suppliedBy`, `originatedBy` (to an `Agent`) = | apk `maintainer` ≈ | none | Product.supplied_by from `metadata.supplier`. A component-level supplier needs a slot: the draft's Component has only `owned_by`. A publisher is not a supplier (our reading) | component suppliers | #15 (§2b), Table 2 |
| **Vulnerability** (`catalog_ref`) | `vulnerabilities[].id` (in Grype's CycloneDX output) = | `Security/Vulnerability` with an `externalIdentifier` of type `cve` = | `vulnerability.id` (15 distinct) = | kept: id, severity, first fix version, description, URLs, data source, namespace, one CVSS score | one Vulnerability per CVE id; other ids (GHSA, distribution advisories) as aliases | | DEC-008 |
| **`affects`** (range: Product only) | `vulnerabilities[].affects[].ref` (component level) ≈ | `hasAssociatedVulnerability` (from an Artifact) ≈ | one match per CVE and package (30) ≈ | ≈: an edge from the vulnerability node to a package node | an Assertion (subject: Vulnerability, predicate: `affects`, object: Component), rolled up to the product by propagation (proposal §5), because `affects` cannot point at a Component. Join Grype's report to the SBOM by purl: its `affects[].ref` values do not match Syft's `bom-ref` values (§3) | which package, if `affects` is used as defined | #15, #17, DEC-001 |
| **Assertion** for a match (`confidence`, `assertion_status`; no provenance slot) | none in Grype's CycloneDX output (no match type or matcher) | the relationship's `creationInfo` (`createdBy`, `createdUsing`, `created`) ≈ | `matchDetails[]`: `type`, `matcher`, `searchedBy`, `found.versionConstraint`; `descriptor.db.status.built` = | none | `confidence` from the match type (Anchore: exact matches are high confidence, `cpe-match` "requires verification"; 0.1.0 §5), plus fields the draft lacks: matcher, data-source namespace, version constraint, database build time, tool version | the method and the database date, which together decided this result (§3) | #15 (§4), #17, DEC-008 |
| **Weakness** (`catalog_ref`; no edge from Vulnerability in the draft; ARCH-0001 §3 lists `instance_of`) | `vulnerabilities[].cwes[]` (integers; empty in Grype's output) ≈ | `externalRef` of type `cwe` ≈ | `vulnerability.cwes[]` with `source` and `type` (30/30, all `Secondary`) = | none: no CWE handling | a Weakness per CWE id; the CVE-to-CWE link as an Assertion that keeps `source` and `type`, because sources can disagree (0.1.0 §5) | who assigned the CWE | #15, #17, #61, DEC-008 |
| Fix information (target: none; `Mitigation.mitigates` ranges over ThreatInstance) | `affects[].versions[]` with `status` ≈; `recommendation` txt | `VexFixedVulnAssessmentRelationship` ≈ | `vulnerability.fix` (`versions`, `state`, `available[]` with dates) = | ⊂: the first fix version, as an `is_fix` node | an attribute of the match Assertion (a remediation option), not a Mitigation | fix state and date | #15, DEC-009 |
| Scores (target: none by design; RiskScore is "Not a single CVSS score") | `vulnerabilities[].ratings[]` | CVSS and EPSS assessment relationships (RPT-0005) | `cvss[]`, `epss[]`, `risk` | one CVSS base score | keep as display attributes of the Vulnerability; the risk scheme is DEC-003's question | | DEC-003 |
| Operating system | a `components[]` entry of `type: operating-system` = | `primaryPurpose: operatingSystem` ≈ | Syft and Grype `distro` = | none | a Component that the packages run on; it also selects the distribution feed a scanner uses | | #15 |
| Upstream (source) package (target: none) | `pedigree.ancestors` (not used by Syft); Syft uses the purl's `upstream=` and a `syft:metadata:originPackage` property | `generates` relationship (our reading) | `metadata.originPackage`; Grype `artifact.upstreams[]` | none | a "built from" edge to a source Component, because one upstream CVE lands on several binary packages (13 OpenSSL CVEs on 2 packages; 1 busybox CVE on 3) | why several packages share one CVE | #15 |
| Completeness (target: none) | `compositions[].aggregate` (absent here) | `completeness` on a relationship | none | none | needs a home: the composition claim of one ProductInstance | whether a missing dependency entry means "none" or "unknown" | #15, DEC-001 |
| The SBOM document and its creation (target: none; proposal §4 names PROV-O, the draft has no provenance class) | `serialNumber`, `version`, `metadata.timestamp`, `metadata.tools` | `SpdxDocument` (its IRI is `spdxId` in JSON-LD), `CreationInfo` (`created`, `createdBy`, `createdUsing`) | Syft and Grype `descriptor` blocks | Grype's `source` and `descriptor` blocks, in saved files only | provenance on every imported node and edge: which document, which tool, when | | #15 (§4), #17 |
| SBOM capture stage (do not map to LifecyclePhase) | `metadata.lifecycles[].phase` (absent here): "the stage(s) in which data in the BOM was captured" | `Sbom.sbomType` | none | none | not a LifecyclePhase: it says when the SBOM data was captured, not where the product is in its life (our reading). Two names overlap (`design`, `decommission`) | | #15 (§3b) |
| Build record (target: none; post-MVP, proposal §7) | `formulation` (absent) | `Build/Build` | none: Syft records the image, not its build | none | the radar contract (ADR-0001), after the MVP | | ADR-0001, dimension 6 |
| VEX override (Assertion and Review; post-MVP, proposal §7) | `vulnerabilities[].analysis` (absent) | `Vex*VulnAssessmentRelationship` | none (Grype can read VEX documents with `--vex`; not used here) | none | an `assertion_status` and a Review on the match Assertion (RPT-0005, dimension 3) | | #15, DEC-001 |
| Review | `annotations[]` (absent) | `Annotation` with `annotationType: review` | none | none | everything imported starts unreviewed (R-018) | | R-018 |
| Licences | `components[].licenses` (16/16) | `hasDeclaredLicense`, `hasConcludedLicense` | `licenses` | display and statistics only | out of scope for the threat model (our reading) | | none |

Hardware rows are not exercised by a container image; they come from agent 4 (Table 4).

## 5. What the pilot changes in dimensions.md (0.3.0)

1. **Table 6 columns.** The single "Fidelity" column is gone: each source cell carries its own mark, because the sources fit differently (for example, `affects` is ≈ in all three sources for one reason, while Component identifiers fit nowhere). The "radar today" column is split in two: "Syft and Grype output" (what radar could pass on now) and "tradar keeps" (what its pipeline passes on today).
2. **Table 6 rows.** Added the rows this pilot needed: version, component kind, upstream (source) package, match provenance, fix information, scores, operating system, the SBOM document and its creation, the SBOM capture stage, licences, and Review.
3. **Table 3.** The columns worked for purl and CPE; no change.
4. **Dimension 5, question 2.** Match provenance must include the database snapshot (its build time), because the same SBOM gave 4 matches on 2026-09-28 and 30 on 2026-10-08.
5. **Dimension 6, question 1.** Name the three image digests (platform manifest, image configuration, multi-platform index) explicitly.

## 6. Findings for #15 and #17 (evidence only)

The pilot met six places where the draft cannot hold what a real SBOM and scan say. Each is a candidate for Table 8, not a proposal.

1. **Composition sits on the wrong type for builds.** `composed_of` is a slot of Product ("a product design") and Component, not of ProductInstance. An SBOM lists what is in one build (one digest), and builds of the same product differ, so the SBOM's component list has no per-build home.
2. **`affects` can point only at a Product.** Matches are per package; the per-package link has to become an Assertion (§4), as the proposal already plans for propagation and VEX (§5).
3. **No version, identifier or kind slot.** Component, Product and ProductInstance have only `id`, `name` and `description`, although the proposal's §1 says "Component (CPE/purl, shared)".
4. **No edge from Vulnerability to Weakness** in the draft, so the CWEs in every match have nowhere to go. ARCH-0001 §3 lists an `instance_of` edge.
5. **No provenance on Assertion.** `confidence` and `assertion_status` exist; the data source, matcher, tool version and database date do not, and §3 shows they decide the result.
6. **`depends_on` versus `uses_component`.** The draft defines both, and the pilot could not tell which an SBOM's `dependsOn` should fill.

## 7. Table 3, pilot rows

The two rows the pilot can fill from its own data. Cells marked "fan-out" are agent 2's (fanout-identity.md).

| column | purl | CPE 2.3 |
|---|---|---|
| Scheme | purl, ECMA-427 (version: fan-out) | CPE 2.3, NIST IR 7695 |
| Names what | a package version in an ecosystem; here also the architecture and the distribution release (`pkg:apk/alpine/zlib@1.3.2-r0?arch=aarch64&distro=alpine-3.24.2`) | a product: vendor, product, version (`cpe:2.3:a:openssl:openssl:3.5.8:*:*:*:*:*:*:*`) |
| Assigned or computed | assigned, from the package manager's own name | assigned |
| Minted by | anyone, following the type's rules; here Syft, from the apk database | NVD's CPE dictionary, or guessed by a tool: all 81 here are `syft-generated` |
| Canonical form | fan-out | fan-out |
| Version-specific | yes (`@version`) | yes when the version part is set; NVD match criteria use `*` with version ranges |
| Carried in | CycloneDX `purl`; SPDX `packageUrl` or `externalIdentifier` of type `packageUrl`; SWID: none | CycloneDX `cpe` (one; Syft puts the rest in `syft:cpe23` properties); SPDX `externalIdentifier` of type `cpe22` or `cpe23` |
| Keyed on by | in this run, Grype's Alpine-feed match searched by distribution and package name, not by purl (`searchedBy`, our reading); other tools: fan-out | NVD configurations; Grype's `nvd:cpe` namespace (29 of 30 matches here) |
| Known failure modes | qualifiers change the string for the same package (`arch`, `distro`, `upstream`); Syft's `bom-ref` adds a `package-id`, and Grype re-wraps it (§3) | guessed vendor and product (15 of 16 with vendor = product); binary packages matched through their upstream (`libssl3` to `openssl`) |
| Standard status | ECMA-427; ISO/IEC CD 27056 (0.1.0 §1) | NIST IR 7695 (naming) to 7698 |
| Library record | none yet | none yet |
