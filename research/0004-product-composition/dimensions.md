---
schema: "archdoc/v1"
id: RPT-0004-dimensions
title: "RPT-0004 dimensions: the search axes"
type: research
status: draft
version: "0.2.0"
date: "2026-09-28"
updated: "2026-10-08"
record: RPT-0004
---

# RPT-0004: search dimensions

This file is Phase 0 of the deep-research playbook in issue #38 (part A, Product Composition). Version 0.1.0 scoped the first draft of the report, which was merged in PR #35 (issue #8 is closed). Version 0.2.0 scopes the second pass: it fixes the questions each section must answer and the exact columns of every table, so "complete" means the same thing to the author, the reviewer agents and the human reviewers. Each dimension is one section of `report.md`.

The report is evidence for DEC-001 (object model), DEC-002 (encoding, and which formats tmodel imports) and DEC-008 (CWE/NVD integration), with smaller inputs to DEC-004 (graph substrate, through the SPDX 3 RDF model and GUAC's graph) and DEC-009 (mapping a generic threat onto a product instance; R-022). It also supplies the input contract that ADR-0001 points to: "the interface is the composition→model-input mapping surveyed in RPT-0004 (#8)". It feeds #15 (core objects) and #17 (schema). It accepts nothing.

## What this pass adds

Version 0.1.0 answered six dimensions from the formats' own texts and from tool runs on two inputs. #38 asks for a complete survey and for full extraction (FX-1) of the sources. This pass adds:

- the sources #38 names that 0.1.0 did not cover: deps.dev, GUAC's graph model, and the SPDX 3 RDF model;
- three new dimensions: identifier schemes (7), minimum elements and policy baselines (8), and other bill types (9);
- the deliverable #38 asks for: a composition → model-input mapping for #15 and #17 (dimension 10, Table 6);
- five-axis applicability ratings for every source (Table 7) and an explicit gap analysis (Table 8);
- a library record for every cited source, either FX-1 complete or an honest stub (Table 9);
- an adversarial review by a fresh agent (Phase 4) and a separate clarity pass (Phase 6).

Sections 1 to 6 keep their 0.1.0 numbers, because RPT-0005 cites them (§1.1, §1.2, §3, §5, §6). New sections come after them, and the old synthesis (§7) moves to §11.

## What complete means: the tables

Every table below must be filled before the report leaves draft. In a cell, `none` means the source has no such thing, and `?` means it has not been found yet; a `?` blocks done. Wide tables may be split or turned on their side in the report; the columns below are what must be filled.

Tables 4 and 6 use RPT-0005's fidelity marks, so the two reports can be read together:

| mark | meaning |
|---|---|
| `=` | same concept, no loss on import |
| `≈` | close; import loses something (say what in a note) |
| `⊂` / `⊃` | the source's element is narrower / broader than ours |
| `ext` | absent, but the source's extension mechanism could carry it |
| `txt` | present only as prose, not machine-readable |
| `none` | absent and not extensible (RPT-0005 writes this mark as a dash) |

### Table 1. Formats at a glance (report front)

Columns: CycloneDX 1.7, SPDX 3.0.1, SWID (ISO/IEC 19770-2) with CoSWID (RFC 9393), and any format Phase 1 adds. 0.1.0's "five questions at a glance" table becomes a subset of these rows.

| row | what goes in it |
|---|---|
| Version pinned | version, patch level and date; any newer release or draft seen |
| Steward and standard status | who maintains it; its Ecma, ISO or IETF status, with the ISO stage code |
| Encodings | serializations and schema language (JSON Schema, XSD, OWL with SHACL, CDDL) |
| Element identity | how an element is named, and whether that name is global or local to one document |
| Component identifiers | which of purl, CPE, SWID, OmniBOR, SWHID and hashes it can carry, and where |
| Required to name a component | the minimum fields |
| Hardware and firmware | what it can say (detail in Table 4) |
| Relationships | the kinds of relationship, and whether they can cross documents |
| Completeness | how a document says a list is complete, and how "none" differs from "unknown" |
| Vulnerability link | where a vulnerability or a CWE attaches (detail in RPT-0005, dimension 7) |
| Build record | a record of how the product was built (SPDX `Build`, CycloneDX `formulation`), or `none` |
| Extension mechanism | how a producer adds fields |
| Licence | of the specification and of its schema files |
| Library record | id and status (`stub` or FX-1) |

### Table 2. Minimum-element crosswalk (report front; detail in §8)

One row per element of the pinned baseline. If CISA's 2026 Minimum Elements is final, its elements are the rows; if not, CISA's 2024 framing (third edition) stays the baseline, as in 0.1.0.

| column | what goes in it |
|---|---|
| Element | as named in the baseline |
| Required by | which baselines require it, and at which level: NTIA 2021, CISA 2024 framing, CISA 2026, and any other baseline §8 adds |
| CycloneDX 1.7 | field path |
| SPDX 3.0.1 | class and property |
| SWID / CoSWID | element |
| Filled in practice | whether Syft's output filled it in our tool runs |
| Notes | "our reading" flags, where a cell is our closest match and not an official mapping |

### Table 3. Identifier schemes (§7)

| column | what goes in it |
|---|---|
| Scheme | name and the specification version pinned (for example purl, ECMA-427 first edition) |
| Names what | a package version, a product, a file, exact bytes, a directory, a commit, a tag |
| Assigned or computed | assigned names can be wrong or guessed; computed ones come from the bytes |
| Minted by | who can create one (anyone, an ecosystem, a dictionary such as NVD's CPE dictionary) |
| Canonical form | whether normalization rules exist, so that two producers write the same string |
| Version-specific | whether one identifier pins one version |
| Carried in | the CycloneDX field, the SPDX property, the SWID element |
| Keyed on by | the databases and tools that match on it (NVD, OSV, GHSA, deps.dev, GUAC, Dependency-Track) |
| Known failure modes | guessing, collisions, ambiguity, drift |
| Standard status | Ecma, ISO, IETF or NIST status |
| Library record | id and status |

### Table 4. Hardware and firmware coverage (§2)

Rows are the hardware facts that R-022 and #8 name, plus those the CISA HBOM framework adds: device or part identity; manufacturer and part number; firmware bound to its device; firmware version and digest; bus or interconnect; compute core or processor; board and assembly hierarchy; serial number (one physical unit); supply-chain origin (country, site); lot or date code; measured identity (what a device reports about itself, for example in an attestation).

Columns: CISA HBOM framework, CycloneDX 1.7, SPDX 3.0.1, ISO/IEC 19770-6 (only if a copy can be read), and each source Phase 1 confirms. Candidates: TCG platform certificates, DMTF Redfish and SPDM, IETF CoRIM and SUIT, and CoSWID or uSWID tags embedded in firmware. Cells use the fidelity marks and name the field or element.

### Table 5. Tools (§3)

Rows: Syft, Grype, Trivy, Dependency-Track, GUAC, deps.dev, and any tool the coverage review adds.

| column | what goes in it |
|---|---|
| Tool | name, version pinned, date |
| Role | generates an SBOM, matches vulnerabilities, aggregates many documents, or answers queries |
| Reads | input formats and versions (SPDX 3? CycloneDX 1.7?) |
| Writes | output formats and versions |
| Identifiers | which it emits or keys on |
| Vulnerability data | its sources (NVD, GHSA, OSV, distribution feeds) |
| CWE | whether it carries CWEs, and from where |
| VEX | which VEX encodings it reads or writes |
| Hardware and firmware | any support |
| Graph model | its node and edge types, if it keeps a graph |
| Evidence | run by us (input and date) or documentation (URL and date) |
| Licence | |

### Table 6. Composition → model-input mapping (§10, the deliverable for #15 and #17)

One row per model input. Rows come from ARCH-0001 §3, the source of truth, and, marked as draft, from the types and slots that the ARCH-0001 proposal (`0.2.0-proposed.11`) and the LinkML draft (`spec/schema/tmodel-object-model.linkml.yaml`, 0.1.0) add, because #15 and #17 iterate those. Starting rows: Product, ProductInstance, Component, `composed_of`, `depends_on`, `uses_component`, Party with `supplied_by` and `manufactured_by`, Vulnerability with `affects`, Weakness, Assertion (for a vulnerability match and for a VEX override), and Review. Composition facts with no target yet get rows too, marked as gaps: completeness claims, a component's set of identifiers, the build record, hardware attributes. If #15 or #17 change the draft, the table is re-pointed, as RPT-0007 §5 was.

| column | what goes in it |
|---|---|
| Model input | the type, slot or edge, and the draft version it comes from |
| CycloneDX 1.7 | source path |
| SPDX 3.0.1 | source class and property |
| radar today | what Syft's and Grype's outputs give, and what tradar keeps (§4) |
| Fidelity | mark |
| Rule | how the value would be derived: which identifier keys a Component across scans, how two SBOMs of one build merge, which way an edge runs. Each rule is a candidate, not a decision |
| Lost | what the import drops |
| Routes to | the `DEC-*` or issue that decides it |

RPT-0005's concept crosswalk (its Table 2) rates what each format can express for each concept. This table is the input contract instead, so it adds the radar column, the derivation rules, and the identity and merge rules. Where RPT-0005 has a cell for SPDX or CycloneDX, this table cites it rather than redoing it.

### Table 7. Applicability ratings (sources.md; summarized in §11)

Every kept source is rated 0 to 3 on the five axes #38 sets. The rubric is RPT-0005's (its Table 5), copied here so that ratings can be compared across reports:

| axis | 3 means |
|---|---|
| Object model | its entities map onto ARCH-0001 §3 types with `=` or `≈` and little loss |
| Provenance/attribution | every statement carries who made it and when, natively |
| Human review/audit | it can record a human accept/reject decision and rationale |
| Federation | ids are globally unique and stable, and records can be exchanged and merged across organizations |
| AI-grounding | an agent can cite an entry by a stable id and retrieve its normative text |

0 = absent, 1 = mentioned or weak, 2 = partial (needs extension), 3 = strong. Every rating cites the field or section that justifies it. Ratings are within the source's own scope: a scanner is not marked down on Object model for lacking threat types.

### Table 8. Gap analysis (§11)

| column | what goes in it |
|---|---|
| Gap | what the field has that tmodel lacks, or what tmodel needs that no source has |
| Evidence | the section and the source |
| Recommendation | the smallest change that would close it, as evidence only |
| Routes to | the `DEC-*` or issue that decides it |

### Table 9. Library records (sources.md)

| column | what goes in it |
|---|---|
| Source | as in sources.md |
| Record id | the existing id, or the id `bin/ingest` assigns |
| Type | `spec`, `rfc`, `repo`, and so on |
| Status before → after | for example `queued` → FX-1 |
| FX-1 artifacts | present, or not applicable with the reason (`library/docs/extraction.md`) |
| Notes | owner, upstream copy, duplicates |

**Which status each record gets.** #38 says a spec record left at `summarized` is rejected: it is either an honest stub or FX-1 complete. So a spec whose fields the report relies on is extracted to FX-1 (candidates: `cyclonedx-1-7`, `spdx-3-0-1`, purl, CoSWID, CPE naming, `osv-schema`); a spec cited only for its status or for one definition stays a stub, with the reason written down; and sources that are not specifications (tools, guides, data) reach the summary bar. Phase 2 confirms the list with the student before extracting, because each FX-1 extraction is a multi-agent job (the CycloneDX 1.7 PDF alone is 566 pages).

## Dimensions

### 1. SBOM formats (CycloneDX, SPDX, SWID)

CycloneDX 1.7, SPDX 3.0.1, and SWID with CoSWID. 0.1.0's five questions stay:

1. How is a component named? (`purl`, `cpe`, `hashes`, `swid`)
2. Can it describe hardware or firmware?
3. How does it say "A depends on B"?
4. How does it say "this list is complete"?
5. How does it attach vulnerabilities (CVE, CWE)?

New in this pass:

6. **The SPDX 3 RDF model.** SPDX 3.0.1 is defined as an RDF/OWL model with SHACL shapes and is serialized as JSON-LD. Can a document be loaded into an RDF store as it is? What do the SHACL shapes check, and what does the JSON Schema check? Which rules in the text does neither check? (Bears on DEC-004 and on ADR-0004's RDF adapter.)
7. **Validation in every format.** Which rules are machine-checked (schema, shapes) and which exist only as text? 0.1.0 found one case in SPDX (a "MUST" the model does not enforce); this question asks for all of them.
8. **What changed, and what comes next.** What changed between CycloneDX 1.6 and 1.7 (and in the 1.7.1 and 1.7.2 patches RPT-0005 found), and between SPDX 2.3 and 3.0.1, that affects an importer? What is the status of SPDX 3.1 and of the next CycloneDX version?

Boundary: how vulnerabilities, VEX statements, scores and the AI and Dataset profiles attach is RPT-0005 (dimension 7); this section cites it.

### 2. HBOM and firmware

0.1.0's four questions stay:

1. What does an HBOM record that an SBOM cannot? (reference: CISA HBOM Framework, 2023)
2. Which formats can carry it (CycloneDX, SPDX, SWID), and how much of the framework maps onto them?
3. How is firmware tied to its device?
4. Can it name the parts issue #8 lists (buses, compute cores, firmware components)?

New in this pass:

5. **Firmware bills in practice.** How do firmware producers publish composition today (candidates: CoSWID or uSWID tags embedded in firmware images, and firmware-update services that ask for them)? Which formats and fields do they use?
6. **Device identity and attestation.** Do device-identity and attestation standards record what a device contains, so that they could act as a measured hardware or firmware bill? Candidates: TCG platform certificates and DICE, DMTF SPDM and Redfish, IETF RATS (CoRIM, EAT) and IETF SUIT manifests.
7. **ISO/IEC 19770-6 (hardware identification tags).** If a copy can be read, which fields it defines. If not, what public sources say, marked as such.
8. **Hierarchical systems.** How does a system of systems (a vehicle and its control units, a server and its boards) state its composition, and how are its software versions identified? For vehicles the candidates are the software identification number of UN Regulation No. 156 and ISO 24089, cross-linked with RPT-0007. (R-022 names hierarchical systems.)
9. **Guidance beyond CISA.** Which other public HBOM guidance exists (for example CERT-In's technical guidelines, already in RPT-0014's source list as S-0847), and does any of it define a format?

### 3. Tools (Syft, Grype, Trivy, Dependency-Track, GUAC, deps.dev)

0.1.0's questions stay: what each tool produces or consumes, which fields it fills, and whether tools agree on the same input. New in this pass:

1. **Re-runs.** Run Syft, Grype and Trivy at their current versions on the two 0.1.0 inputs and on one more input that exercises other matchers (a Debian-based image or a Java project, as 0.1.0's limits suggest).
2. **deps.dev.** What does it hold (packages, versions, resolved dependency graphs, advisories, licences, OpenSSF Scorecard results, provenance), through which interfaces (API, dataset), and keyed on what (purl, version, hash)? Can it answer "which package version has this hash"?
3. **GUAC's graph model.** Which node and edge types does its ontology define, how does it merge documents about the same package or artifact, and how does it record where a fact came from? It is the closest existing composition knowledge graph to tmodel's (DEC-001, DEC-004, #25).
4. **SPDX 3 support.** Which tools read or write SPDX 3 today? (0.1.0: not Syft, Dependency-Track or GUAC.)
5. **Dependency-Track 5.** What changed in version 5 that affects composition data (its data model, its API)?

### 4. How radar (tradar) uses these today

Which formats and fields tradar reads, and what it keeps or drops on the way to its graph. tradar's `main` has not changed since `26d9c76` (checked on GitHub, 2026-10-08), so 0.1.0's findings stand. This pass re-checks them and adds to them only if the code changes.

### 5. The bridge: components to CVEs and CWEs

0.1.0's question stays: how a component is matched to CVEs (CPE versus purl, NVD versus distribution advisories) and to CWEs, where each CWE assignment comes from, and what happens to NVD's placeholder values. New in this pass:

1. **How each vulnerability source names affected software** (CVE Record Format 5.x `affected`, NVD CPE match criteria, OSV `affected` with purl and ranges, GHSA, distribution feeds), and which identifier each one needs from an SBOM. Record structure in depth is RPT-0005 (dimension 1); this section asks only what a match needs.
2. **Match provenance.** What does each scanner record about how it made a match (method, data source, confidence), and could that become an Assertion with a confidence (ARCH-0001 proposal §4, §5)?
3. **Version ranges.** How are affected versions written (CPE `versionEnd*`, OSV ranges, `vers` in CycloneDX), and where does version comparison differ by ecosystem?
4. **Disagreement.** Is there published evidence on how often CPE matching and ecosystem matching disagree? (0.1.0 showed one case, on Alpine.)

Boundary: VEX encodings in depth are RPT-0005's (dimension 3). 0.1.0's VEX status table stays in this report, because RPT-0005 cites it.

### 6. Build identity and the radar → tmodel input contract

0.1.0's question stays: how composition pins one specific product version (commit, hash, image digest, SBOM serial number). New in this pass:

1. **Which identity anchors which model type.** In the current draft, what pins a Product, a ProductInstance (the proposal's "identity-by-hash" instance, §3b) and a Component? When is a rescan the same ProductInstance, and when is it a new one?
2. **Attestations as carriers.** How do in-toto statements, SLSA provenance (library record `slsa-1-2`, already FX-1), Sigstore bundles and OCI referrers attach an SBOM or a provenance record to an artifact digest?
3. **The contract.** What would radar have to emit for tmodel to fill Table 6: which fields, in which format, with which identity guarantees? Evidence only: ADR-0001 owns the contract, and the proposal puts build provenance after the MVP (§7).
4. **Other domains.** How a firmware image and a vehicle's software set are identified (with dimension 2, question 8).

### 7. Identifier schemes (new)

purl (ECMA-427), CPE 2.3 (NIST IR 7695 for naming, NIST IR 7696 for matching), SWID tag ids and CoSWID, OmniBOR (gitoid), SWHID (ISO/IEC 18670), cryptographic hashes, and OCI digests.

1. What does each name, and is it assigned or computed from the bytes?
2. Who can mint one, and is there a canonical form?
3. Which databases and tools key on it?
4. How does each fail in practice (guessed CPEs, purl type and namespace ambiguity, a hash of which bytes)?
5. Which could serve as a stable key for a Component in a knowledge graph shared across organizations, and what must be stored next to it (issuing authority, algorithm, version)?

### 8. Minimum elements and policy baselines (new)

NTIA 2021 (`ntia-sbom-minimum-elements`), CISA's 2024 framing (`cisa-framing-software-component-transparency`), CISA's 2026 Minimum Elements (stub `cisa-2026-sbom-minimum`), and other documents that require SBOM content. Candidates: Germany's BSI TR-03183-2, the EU Cyber Resilience Act, FDA premarket guidance for medical devices, and OMB M-26-05 (record `omb-m-26-05`, which lists CISA's 2025 draft and the HBOM framework as references).

1. What does each require, and at which level (minimum, recommended, aspirational)?
2. What changed from NTIA 2021 to CISA 2026?
3. Does each format carry each element (Table 2)?
4. Which baselines require a hash, a supplier, a dependency depth or a completeness statement, and do our tools' outputs meet them?

### 9. Other bill types (new, short)

CycloneDX's other bill types (services and SaaSBOM, CBOM for cryptographic assets, ML-BOM for models and data, OBOM, MBOM) and SPDX 3's other profiles (AI, Dataset, Build, Lite), from the composition side only.

1. Which kinds of component does each add (services, models, datasets, cryptographic assets)?
2. Does tmodel's Component cover them, or would they need types of their own? ARCH-0001 §3 defines a Component as "A part of the system (service, container, dependency, source module)", and the proposal adds chips and cores (§0).

Boundary: their security fields are RPT-0005 (dimension 7), and AI threats are RPT-0014 (#71; lane #80). The AI-BOM sources already in RPT-0014's source list (S-0705, S-0827, S-0840, S-0847) are reused, not searched again.

### 10. Composition → model-input mapping (new; the deliverable)

Assembled in the main session from sections 1 to 9, as Table 6.

1. For each model input, which composition field fills it, in each format and in radar's output?
2. Which identifier keys a Component, and how are two SBOMs of the same build merged?
3. Which composition facts have no home in the model (completeness, identifier sets, build records, hardware attributes)?
4. What does the import lose, and what would the model have to add to keep it?

### 11. Synthesis and gap analysis

The evidence by decision (DEC-001, DEC-002, DEC-004, DEC-008, DEC-009), then Table 8 (gaps routed to `DEC-*` and issues) and a summary of the Table 7 ratings. Replaces 0.1.0's §7.

### 12. Method, adversarial review and limits (Phase 4)

A fresh agent that did not write the draft checks:

1. **Coverage.** Against an independent list, did we miss a format, tool or standard that matters? Candidates to test against: OpenVEX and CSAF (in RPT-0005), cdxgen, OSV-Scanner, Microsoft's sbom-tool, protobom and bomctl, OSS Review Toolkit, ScanCode, Tern, the Yocto and Zephyr SBOM outputs, SBOMs attached to OCI images, Sigstore, BSI TR-03183-2, the EU Cyber Resilience Act, ISO/IEC 27036-3 and ISO/IEC 18974 (OpenChain).
2. **Citations.** Is every claim traceable to a verified source?
3. **Extraction.** For each FX-1 record: count the source's normative keywords first, then check that the extraction has the same count.
4. **Mapping.** Spot-check Table 6 cells against the format texts and the draft schema.

Findings go back through dimensions 1 to 10. Rejected findings and the reasons go in the design log (DL-0015).

## Per-source record

What each Phase 1 agent returns for every source: the citation and a verified URL (fetched, not remembered); the version and date pinned; the steward; what it is, in two or three lines; the dimension questions it answers, each with a quote and a locator; the table cells it fills; the five-axis ratings with their justification; its applicability to the tmodel knowledge graph (which model types and edges); its library record id and proposed status (FX-1, summary or stub); how each fact was checked (artifact parsed, page fetched, tool run); and every claim it rejected, with the reason.

## Phase 1 plan

1. **Pilot first, in the main session.** Fill Table 6 for one real composition (Syft's CycloneDX output and Grype's JSON for `alpine:latest`, re-run with the tool versions recorded) and Table 3's rows for purl and CPE. This tests Table 6's rows and columns before the fan-out, and it gives #15 and #17 a first mapping early in I2 (PLAN-0001: October 9 to 22, when ARCH-0001 moves to v0.2 and a first schema draft imports an existing format). If the columns do not work, this file is revised first.
2. **Fan-out: five agents in parallel, at maximum effort.**
   - agent 1: dimensions 1, 8 and 9 (formats, baselines, other bill types; Tables 1 and 2)
   - agent 2: dimensions 6 and 7 (build identity and identifier schemes; Table 3)
   - agent 3: dimension 5 (the bridge)
   - agent 4: dimension 2 (hardware and firmware; Table 4)
   - agent 5: dimensions 3 and 4 (tools and radar, with the re-runs; Table 5)
3. Dimensions 10 and 11 are assembled in the main session from the agents' results.

The playbook allows three to five agents; five keeps each agent to one to three closely related dimensions. Merging agents 2 and 3, and agents 1 and 4, would make three if cost matters more than depth.

Rules for every agent: fetch every URL and read it from its own text, not from a fetch tool's summary; parse schemas and model files rather than describing them from memory; quote with a locator; pin versions and dates; log every query for `searches.md`; never commit a third-party file (record its URL and SHA-256 instead). If WebSearch runs out, as it did for RPT-0005's agents, say so in `searches.md` and fall back to fetching known URLs. Each agent's notes are kept in this folder as `fanout-<topic>.md`, as RPT-0005 does, and later corrections are recorded in the design log.

## Phases 2 to 6

| phase | what | output |
|---|---|---|
| 2. Library records | `bin/ingest` the new records; FX-1 extraction (extract, then adversarial verify, then cross-check, every pass at maximum effort) for the specs Table 9 marks FX-1 | a `Threat-Radar/library` pull request on its own branch, `Part of Threat-Radar/tmodel#38` |
| 3. Distill and rate | a summary per source, and the Table 7 ratings | `summary.md` per record; Table 7 in sources.md |
| 4. Adversarial review | a fresh agent (dimension 12); every gap goes back through phases 1 to 3 until it finds nothing material | a findings list; rejections in the design log |
| 5. Report | `report.md` 0.2.0: comparison tables first, sections 1 to 10, synthesis and gap analysis (§11), method and limits (§12); citations by library record id | `report.md` |
| 6. Clarity pass | a separate editing pass: an overview and a conclusion, acronyms defined, a lead-in for every table, a diagram where it earns its place (candidate: the radar → tmodel data flow), consistent citations. Readers: Prof. Haskell and the sponsor | `report.md` |

## Definition of done (from #38)

- [ ] Library records FX-1 complete, or honest stubs with the reason (Table 9)
- [ ] Report: comparison tables, sections, synthesis and gap analysis
- [ ] Composition → model-input mapping for #15 and #17 (Table 6)
- [ ] Adversarial review passed
- [ ] Clarity pass done
- [ ] Human review sign-off
- [ ] `version` and `updated` moved together on every edit (ARCH-0001 §9.5)

## Related reports (cite, do not redo)

| report | overlaps on | rule here |
|---|---|---|
| RPT-0005 schema representations (#39) | VEX encodings; CVE, NVD, CWE and OSV records; the security parts of SPDX 3 and CycloneDX 1.7; the concept crosswalk; the rubric | cited; this report keeps naming, dependencies, completeness, hardware, build identity, tools and the input contract |
| RPT-0011 knowledge graphs and NSF OKN (#25) | GUAC, SPDX 3 as RDF, the graph substrate | cited; the substrate stays with DEC-004 |
| RPT-0013 SDL and conformance (#67) | SLSA, in-toto, OMB M-26-05 | records reused (`slsa-1-2` is already FX-1) |
| RPT-0014 AI threat model (#71) | AI-BOMs | its AI-BOM sources reused; AI threats stay there |
| RPT-0015 KG schema foundation (#104) | schema language, identifier patterns | Table 6 targets the draft schema it feeds |
| RPT-0007 ISO/SAE 21434 (#11) | vehicles, ISO 24089 | cross-linked from dimensions 2 and 6 |
| RPT-0003 threat-modeling products (#7) | products' SBOM and CVE features | reused, not searched again |

## Open questions for the sponsor

1. **Which FX-1 rule applies?** The fork's `docs/extraction.md` says that touching a spec record triggers FX-1. Upstream changed this in m-of-n/library PR #42 (merged 2026-10-05): only the intent to extract triggers it, and a pull request that only summarizes is allowed. #38 says a spec record left `summarized` is rejected. Should the fork take the upstream change, and does #38's rule still hold for this topic?
2. **Upstream owner.** `cyclonedx-1-7` and `spdx-3-0-1` have an upstream owner (`owner: Ndewedo-Newbury`, the `sbom` lane), and both were still `queued` upstream on 2026-10-08. Should we extract them in the fork and offer the work upstream, or coordinate first?
3. **Duplicate records.** `ntia-2021-sbom-minimum` (stub) and `ntia-sbom-minimum-elements` (summarized) describe the same NTIA report; `iso-iec-5962` (stub) and `iso-iec-5962-2021` (queued) both describe ISO/IEC 5962:2021. Ids are never reused, so how should a duplicate be retired?
4. **Paywalled standards.** Can the project get ISO/IEC 19770-2:2015 (SWID) and ISO/IEC 19770-6:2024 (hardware identification tags), as it did ISO/SAE 21434? If not, both stay stubs, and the report keeps relying on NIST IR 8060, RFC 9393 and ISO's catalog data.
