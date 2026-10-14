---
schema: "archdoc/v1"
id: RPT-0004-fanout-hardware
title: "RPT-0004 Phase 1 fan-out: hardware and firmware bills"
type: research
status: draft
version: "0.1.0"
date: "2026-10-08"
updated: "2026-10-08"
record: RPT-0004
---

> Phase 1 fan-out notes, kept as the research agent wrote them; corrections found later are recorded in the design log (DL-0015). Downloaded files were not committed (third-party material); each is identified by URL and SHA-256 so it can be fetched again.

# RPT-0004 fan-out, agent 4: dimension 2 (hardware and firmware)

Scope: dimension 2 of `dimensions.md` (v0.2.0), questions 1 to 9, and Table 4. Everything below was checked on 2026-10-08. Files were fetched with curl (or through the GitHub API with `gh`) and parsed with jq, python3, grep and `pdftotext` 26.x; they were kept in the session scratchpad and are not committed. Where a publisher's site refused automated requests (cisa.gov returned "Access Denied" from Akamai; trustedcomputinggroup.org, dmtf.org, iso.org and unece.org returned Cloudflare challenges), the same file was taken from the Internet Archive's Wayback Machine with the `id_` modifier, which returns the original bytes; the capture time is given in each record. WebSearch worked for the whole session (11 queries, section 7). The Claude in Chrome extension was not connected, so the ISO Online Browsing Platform preview could not be loaded (section 1.23).

Conventions. "Our reading" marks an interpretation; everything else is quoted or counted from the source. Quotes are kept short (most under 15 words), because several sources (TCG, DMTF, ISO, Auto-ISAC) restrict copying; field names, enum values and table labels are given as facts. Fidelity marks are those of `dimensions.md` (`=`, `≈`, `⊂`, `⊃`, `ext`, `txt`, `none`). In Table 4 a mark compares the source's element with the row's hardware fact, because the draft model has no hardware attributes yet. Base: the v0.1.0 report, §2. RPT-0005 covers the security parts of CycloneDX 1.7 and SPDX 3.0.1; this file cites it and does not repeat it.

## 1. Per-source records

### 1.1 CISA, A Hardware Bill of Materials (HBOM) Framework for Supply Chain Risk Management (2023)

| field | value |
|---|---|
| Citation and URL | Cybersecurity and Infrastructure Security Agency (CISA), ICT Supply Chain Risk Management Task Force, HBOM Working Group, *A Hardware Bill of Materials (HBOM) Framework for Supply Chain Risk Management*. <https://www.cisa.gov/sites/default/files/2023-09/A%20Hardware%20Bill%20of%20Materials%20Framework%20for%20Supply%20Chain%20Risk%20Management%20%28508%29.pdf>; resource page <https://www.cisa.gov/resources-tools/resources/hardware-bill-materials-hbom-framework-supply-chain-risk-management> |
| Version and date | No version number in the document; the taxonomy's own version field must be "1.0" (C.1.1). Publication date on the resource page: September 25, 2023. PDF metadata: created 2023-09-07, modified 2023-09-14; 33 pages. |
| Steward | CISA National Risk Management Center, through the ICT SCRM Task Force (public-private, co-chaired by CISA and the IT and Communications sector councils, §1). |
| What it is | A voluntary field taxonomy for HBOMs (47 fields in seven categories, Appendix C), use-case categories (Appendix A), and a parent-child nesting layout "suggested for spreadsheet HBOMs" (Appendix B.1.1). No file format. |
| Licence | No licence or copyright statement in the PDF (grep for "copyright", "public domain", "TLP": 0 hits). Not checked further. |
| Library record | none (`cisa-hbom-framework-2023` proposed, section 6). Cited by the existing record `omb-m-26-05` (its `cites`, p. 2 bullet 3). |
| How checked | cisa.gov returned HTTP 403 to curl. The resource page was read with WebFetch (links only). The PDF was taken from the Wayback capture of 2026-08-22 (`20260822203154id_`): SHA-256 `cba6ce12fc98be11b831f08b3cf3bb12b3a59f86397e3a27a410fdd515025806`, identical to the digest in the v0.1.0 `searches.md`. Its SHA-1 (base32 `GRTZA3QEXSAAJDEZH7ESP6UX7VSALA5U`) equals the payload digest of every Wayback capture of that URL from 2023-11-01 to 2026-08-23, plus a revisit record of 2026-09-24. Appendix C parsed with a python3 script over the `pdftotext -layout` output (one record per "FIELD NAME" heading, reading "Field type", "Equivalent CycloneDX field" and "Equivalent SPDX field"). Fact sheet (2 pages, dated September 2023): Wayback capture 2025-02-22, SHA-256 `68d8204695db51f0b18516c48b5733132a34db267b9b5ec6b2a9561f8482c801`. |

Findings:

- **The v0.1.0 counts hold.** The parse finds 47 fields under headings C.1 to C.7, with 7, 2, 5, 15, 8, 2 and 8 fields per category. 37 fields give "None" (36) or "None, do not map" (1, `HBOM_STD_VERSION`) as their CycloneDX equivalent; 36 give "None" (35) or "None, do not map" (1) as their SPDX equivalent. The 10 fields with a CycloneDX equivalent are `HBOM_MODIFY_DATE`, `HBOM_AUTHOR`, `FGA_NUM`, `FGA_VERSION`, `FGA_HASH`, `FGA_MAIN_MANUFACTURER`, `COMP_MANUFACTURER`, `COMP_MANUFACTURER_PN`, `COMP_HASH`, `COMP_VERSION`; `COMP_SUPPLIER_PN` has an SPDX mapping only ("(2.5) SPDX Document Namespace (3.2) SPDXID:", C.5.2).
- **The SPDX mappings use SPDX 2.2 clause numbers.** For example "(3.1) PackageName:" (C.1.6) and "(2.9) Created:" (C.1.3). These numbers match the SPDX 2.2 chapter headings ("3.1 Package Name", "2.9 Created", spdx/spdx-spec tag `v2.2`); tags `v2.2.2` and `v2.3` number the same fields 7.1 and 6.9. The framework names no CycloneDX or SPDX version (grep of the text).
- **The CycloneDX mappings predate CycloneDX 1.6.** Manufacturers map to "Supplier publisher" (C.3.2, C.3.5). CycloneDX 1.5 (released 2023-06-26, current when the framework appeared) has no `component.manufacturer` and no organization `address`; 1.6 (2024-04-09) adds both (schema check, section 7). So part of the "no equivalent" count is CycloneDX's 2023 state, not its current one (section 3.3).
- **Two mapping slips (our reading).** `HBOM_CREATION_DATE` maps to "None" (C.1.2) while `HBOM_MODIFY_DATE` maps to "metadata/timestamp" (C.1.3), although CycloneDX defines `metadata.timestamp` as "when the BOM was created". `COMP_SUPPLIER` maps to "None" (C.3.4) although CycloneDX has had `components[].supplier` since before 1.5.
- **Category boundaries disagree inside the document.** Table 3 lists "Assembly & Test Supplier" as an Entity Name example, but C.4.1 puts `ASSY_AND_TEST_SUPPLIER` under Entity Location; C.5.1 puts a location code (`ASSY_AND_TEST_LOC_CODE`) under Component Part Information. Our reading of the C.8 quick-reference layout is that each heading from C.3 on sits one field early. The count of 47 is not affected.
- **The taxonomy has no serial number.** "serial" occurs 0 times in the text. `FGA_NUM` is a "Unique Number issued by manufacturer to identify the product" (C.1.6), mapped by CISA to `name`: a product number, not a unit number. An HBOM made this way describes a product or part type, not one physical unit.
- **Firmware has no field.** §1.3 says the framework covers "the provider of the firmware" but "stops short of proposing a framework for examining the provenance"; no field names a firmware or its provider. Firmware enters only as one of "Hardware, and/or Software, and/or Firmware version number" in `FGA_VERSION` and `COMP_VERSION` (C.2.2, C.6.2). There is no digest field: `FGA_HASH` and `COMP_HASH` are "An intrinsic identifier", with a UUID as the example (C.3.1, C.5.8).
- **Parts are typed only loosely.** `COMP_TYPE` is "hardware", "software" or "service", and "another string may be used" (C.5.5); `COMP_PART_TYPE` is a string ("* might enum this") holding a "Component category (e.g., semiconductor, antenna, etc.)" (C.5.6). Buses and compute cores have no field.
- **Hierarchy is by separate documents.** "a separate HBOM is required for the assembly", joined "via the part-level information" (B.1.1, Table 5 shows four HBOMs for one finished good).
- **Supply-chain origin is the richest area.** 15 Entity Location fields give place names, WGS84 or decimal-degree coordinates, and ISO 3166 country and subdivision codes for the OEM headquarters, the main and alternate manufacturing sites, the component manufacturer and the semiconductor assembly-and-test site (C.4). For semiconductors it asks for the supplier and the fab "as separate data points" (B.1.3).
- **Internal inconsistency.** `HBOM_STD_VERSION`: "Must be "1.0,"" but the example is "0.9" (C.1.1).
- **Appendix D names entity and part resolution as unsolved** ("multiple identifiers can be used for the same part"), and notes that "not all fields have a direct 1:1 mapping" to CycloneDX and SPDX.
- **Not updated since 2023.** Evidence: the unchanged PDF digest on the Wayback Machine from 2023-11-01 to 2026-08-23 (above); the live resource page (WebFetch, 2026-10-08) still links only this PDF, the fact sheet (dated "September 2023" on its page 1) and a webinar; CISA's *2026 Minimum Elements for a Software Bill of Materials* (publication July 29, 2026; Wayback capture 2026-10-04, SHA-256 `b42046c466ea3afcd2110b9b20607896d7172d6aaf66051459a769d0aa7456fc`) mentions "firmware" once, as a kind of SBOM component, and "hardware" 0 times. OMB M-26-05 (2026-01-23) still cites the September 2023 framework (library record `omb-m-26-05`).

### 1.2 CycloneDX 1.7.2: hardware support, and the `cdx:device` property taxonomy

| field | value |
|---|---|
| Citation and URL | OWASP CycloneDX / Ecma TC54, CycloneDX 1.7 (ECMA-424 2nd edition). JSON Schema at tag `1.7.2`: <https://raw.githubusercontent.com/CycloneDX/specification/1.7.2/schema/bom-1.7.schema.json>. Property taxonomy: <https://github.com/CycloneDX/cyclonedx-property-taxonomy/blob/main/cdx/device.md>. Capability page: <https://cyclonedx.org/capabilities/hbom/> |
| Version and date | Latest release 1.7.2 (2026-09-17); earlier 1.7.1 (2026-06-02) and 1.7 (2025-10-21) (GitHub releases list, checked 2026-10-08). Taxonomy at commit `836dc95e89` (2026-09-30); `cdx/device.md` last changed 2025-10-28. |
| Steward | OWASP CycloneDX with Ecma TC54 (RPT-0005). Taxonomy: CycloneDX Core Working Group. |
| What it is | The released CycloneDX schema. Hardware is a component `type` (`device`) with a nesting rule; hardware details live in registered property names outside the schema. |
| Licence | Schema Apache-2.0 (repository); taxonomy Apache-2.0 (GitHub API `license.spdx_id`). |
| Library record | `cyclonedx-1-7` (queued; owner `Ndewedo-Newbury`). Taxonomy: none (`cyclonedx-property-taxonomy` proposed). |
| How checked | Schemas at tags `1.7` (SHA-256 `df472ef4aaf593904c479293723a1a5c191d6672715c93b3c0b5c318f3914221`) and `1.7.2` (SHA-256 `73308edec3ab2d38bfffd993e96a042b594314143b6971a6e9ed98bbb6bd76ce`, same as RPT-0005) diffed with `jq -S`. Release notes of 1.7.1 and 1.7.2 read through the GitHub API. `device.md` at `836dc95e89`: SHA-256 `88b4df646e16c52f65e78691814b4355077ebcb0cc06449a25fa59344d8a0a23`. All 131 pull requests of the taxonomy repository listed and searched for "device", "hardware", "hbom", "firmware", "chip", "board"; issues searched for "device". Capability page HTML SHA-256 `bca41ee8d8742369b986d0b0334296fe193034095815bb1ddf53320ccb680468`. Schemas at tags `1.5` (SHA-256 `067f7824b08653839ea050ae9e09ca48375eadc2652b0e2a299476e7db90335b`) and `1.6` (SHA-256 `3e92dddbc30cf7f6a02b80f0942b1a4cfd4fb1c26f1dfc4310afa9d613cafb93`) checked for `manufacturer` and `address`. |

Findings:

- **No hardware change since the v0.1.0 report.** The 1.7 to 1.7.2 JSON diff is 24 lines, all editorial (typo fixes and one sentence added to the `ratings` description). The 1.7.1 notes list XML and Protobuf alignment for model cards; the 1.7.2 notes list an XML node for cryptographic protocol relations. `cdx/device.md` was last changed on 2025-10-28 ("docs: cdx rules and processes"); no device pull request exists after #6 (2022). Open issue #67 (2023-07-12) asks for `cdx:device:countryOfOrigin`; a maintainer comment of 2026-08-24 points to CycloneDX 2.0 instead (section 1.3).
- **The device rule.** `definitions.component.properties.type["meta:enum"].device`: "A hardware device such as a processor or chip-set", which "SHOULD include a component for the physical hardware itself and another component of type 'firmware' or 'operating-system'". `firmware` is "A special type of software that provides low-level control over a device's hardware". The component type enum has 13 values.
- **Nesting.** `components` description: "This is not a dependency tree" and "similar to system → subsystem → parts assembly in physical supply chains". `compositions[].assemblies`: "References do not cascade to child parts."
- **The only hardware vocabulary is the taxonomy.** `cdx:device` has 9 base names (`quantity`, `function`, `location`, `deviceType`, `serialNumber`, `sku`, `lotNumber`, `prodTimestamp`, `macAddress`), 2 `bom` names (`ebom`, `mbom`), 4 certification name patterns and 8 GS1 names. `properties` is for "data not officially supported in the standard"; "Formal registration is optional".
- **Location is partial.** `manufacturer` and `supplier` are `organizationalEntity` objects with an `address` (`postalAddress`: `country`, `region`, `locality`, `postalCode`, `postOfficeBoxNumber`, `streetAddress`); `country` is "The country name or the two-letter ISO 3166-1 country code". A search of all schema strings for "coordinat", "latitude", "longitude", "lead time", "technology node" and "country of origin" finds none.
- **No device serial number in the schema.** The two `serialNumber` paths are the BOM document's serial number and `cryptoProperties.certificateProperties.serialNumber` (a certificate's).
- **The capability page** says the format covers "processors, embedded systems, IoT devices, and industrial control systems" (cyclonedx.org/capabilities/hbom/).

### 1.3 CycloneDX 2.0 (in development): first-class hardware support

| field | value |
|---|---|
| Citation and URL | CycloneDX specification, branch `2.0-dev`, commit `f6dcf4d33fecff511c21c4616a5a66d2b8134687` (2026-10-07). Feature issue <https://github.com/CycloneDX/specification/issues/981>; pull request <https://github.com/CycloneDX/specification/pull/982>; modules under `schema/2.0/modules/`. |
| Version and date | Unreleased. Pull request #982 "Added first-class hardware support" was merged into `2.0-dev` on 2026-08-20. The 2.0 milestone was due 2026-08-31 and is still open (90 open, 86 closed issues); draft pull request #652 "[WIP] CycloneDX v2.0 Specification" (2.0-dev → master) is open. Latest release is still 1.7.2. |
| Steward | CycloneDX Hardware Feature Working Group; issue #981 carries the labels "RFC vote accepted", "tc54 reviewed" and "tc54 accepted". |
| What it is | The 2.0 module set adds a physical module (classification, board location, package style, quantity, lead time, material form), certifications, party-attributed identifiers (including serial numbers), geographic origins, and physical inspection techniques for identity evidence. |
| Licence | Apache-2.0 (repository). |
| Library record | none; a `cyclonedx-2-0` record would be created at release. |
| How checked | Issue and pull request read with `gh`. Module schemas downloaded at the pinned commit and parsed with python3 and jq. SHA-256: physical `223edb72dc293a5c2ee19efe964b270a18fe3d650b9c5b02d1438fdd40aa20d2`; component `6d89303041db208fb550cf727cdba11654f7097e80687712a966fd51ce9e0975`; common `1fd1bb3cb6c7d96e3544796a37284d8f7495c7b6c9f1090813ada8e057d51920`; party `49b7143f05c5bf845f492212537edd625e57aa7adc981de57376e5bafd74a944`; evidence `3cb147baabf303fbb0ba37bace588d4ab47932def57fe54eeb4e11f4e8ff4751`; certification `286153731140dc0de636f5ec72490b621d04cbd1f61639cda919f34d5bdd3b16`; metadata `da9f6af18147198b7572511ecbc71171fa0af03234a071984c9875fbc488a553`; bundled `72ffe3c450e23ae3e8ce263fdb4f40510bee8f9868c4cca8ce9be3796a1b3280`. |

Findings:

- **Why it was added.** Issue #981: today hardware detail goes into properties, which "are not machine comparable across producers and carry no validation"; the working group "analyzed the CISA Hardware Bill of Materials Framework".
- **Physical attributes, schema-enforced.** `component` gains `classification` (`category`, `subcategory`, `codes[]` of `{standard, value}`), `boardLocation` (`designators` such as "U5, R12, C3", `layer`, `subsystem`), `deviceType` (package style: `smd`, `pth`, `bga`, `qfn` and 10 more), `quantity`, `leadTime` (`value`, `unit` in days, weeks or months, `range`) and `materialForm`. An `allOf` rule allows `boardLocation` and `deviceType` "only when `type` is `device`". The type enum gains `material` and `service` (15 values).
- **Identity is a set of attributed claims.** `identifiers[]` groups "identity claims by the party asserting them" and "carry positive claims of identity"; schemes include `mpn`, `part-number`, `model-number`, `sku`, `serial-number` ("Unique identifier for an individual instance of a product."), `asset-tag`, `udi-di`, `udi-pi`, `fcc-id`, `imei`, `mac-address`, GS1 keys, `purl`, `cpe`, `swid`, `swhid`, `omniborid` and `tei` (25 predefined, plus custom).
- **Origins with stage and share.** `origins[]` records where a component comes from "as a distribution across one or more countries or subdivisions", per `stage` (`designed`, `mined`, `smelted`, `manufactured`, `assembled`, `tested` and 13 more) and `basis`, each region with an ISO 3166 `isoCode`, a `percentage` and an optional `performedBy` party.
- **Parties replace the single manufacturer.** `parties` carry roles (68 predefined, including `manufacturer`, `supplier`, `assembler`, `distributor`, `owner`) with a `role.order` "(for example, primary supplier with order 1 and alternate supplier with order 2)". Organizations have `identifiers` (LEI, DUNS, CAGE named in the description), `formerNames`, `aliases` and `addresses` with `isoCode` and `coordinates` (latitude, longitude, datum).
- **Identity evidence for physical parts.** The evidence module adds `visual-inspection`, `x-ray-inspection`, `electrical-testing`, `material-analysis` and `decapsulation` as analysis techniques ("for example exposing a semiconductor die").
- **Still absent (search of the bundled schema):** an interconnect or bus relation, processor cores, and a lot or date-code field (a lot appears only in descriptions, for example of `quantity`). The `device` description and its firmware rule are unchanged from 1.7.

### 1.4 SPDX 3.0.1: hardware

| field | value |
|---|---|
| Citation and URL | The Linux Foundation, *System Package Data Exchange (SPDX) Specification* 3.0.1. Model: <https://spdx.org/rdf/3.0.1/spdx-model.ttl> |
| Version and date | 3.0.1 (2024-12-17), still the latest release (spdx/spdx-spec releases, checked 2026-10-08). |
| Steward | SPDX project of the Linux Foundation; SPDX 3.0 is ISO/IEC DIS 5962 (v0.1.0 report). |
| What it is | Covered in the v0.1.0 report §1.2; this record re-checks the hardware points only. |
| Licence | CC-BY-3.0 and Community Specification License 1.0 (library record `spdx-3-0-1`). |
| Library record | `spdx-3-0-1` (queued). |
| How checked | `spdx-model.ttl` (served with `Last-Modified: Thu, 08 Oct 2026 17:21:54 GMT`): SHA-256 `30ebb4af2d70a9809044ef46f44cc3dc5125226d70f818a50ed2e1d5f404c593`, the same digest RPT-0005 recorded, so the content is unchanged. Purpose and relationship comments read with grep. |

Findings:

- **The v0.1.0 points hold.** Ten profile identifiers, none for hardware. `software_primaryPurpose` `device`: "The Element refers to a chipset, processor, or electronic board."; `firmware`: "The Element provides low level control over a device's hardware."; `deviceDriver`: "The Element represents software that controls hardware devices." "serialNumber", "partNumber" and "manufacturer" occur 0 times.
- **Agents and times are generic.** `originatedBy`: "Identifies from where or whom the Element originally came."; `suppliedBy` names who "supplied the artifact"; `builtTime`: "Specifies the time an artifact was built." The relationship types `runsOn` and `locatedAt` do not exist in 3.0.1; `contains` is "The `from` Element contains each `to` Element."

### 1.5 SPDX 3.1 (pre-release): Hardware and SupplyChain profiles

| field | value |
|---|---|
| Citation and URL | spdx/spdx-3-model, branch `develop`, commit `4eaf6a4bb081b4f7270ef174fee20fa4acb94daa` (2026-10-06), `model/Hardware/` and `model/SupplyChain/`; pre-release tag `3.1-rc1` (2026-01-24) |
| Version and date | Not released. spdx/spdx-spec has the pre-release `v3.1-RC1` (2026-01-24) and no 3.1 final. The `main` branch of the model (3.0.1) has no Hardware directory; tag `3.1-rc1` and `develop` do. The latest commit touching `model/Hardware` is of 2026-09-02. |
| Steward | SPDX project; the 3.1-rc1 release notes list the pull requests "Profile hardware - Draft Hardware Profile Submission" (#947), "add HBOM supply chain" (#977) and "Add taxonomy type for hardware" (#1027). |
| What it is | A Hardware profile (abstract `Hardware` under `/Core/Artifact`, with `PhysicalHardware`, `BulkHardware` and `VirtualHardware`), a SupplyChain profile of processes and actions (manufacture, assembly, test, transport, storage, responsibility change and more), and Core additions (`Location`, `PhysicalLocation`, new relationship and identifier types). |
| Licence | Community-Spec-1.0 (file headers). |
| Library record | none (a record at the 3.1 release). |
| How checked | Every file under `model/Hardware` and the SupplyChain, Location, Organization and vocabulary files fetched at the pinned commit; vocabularies diffed against tag `3.0.1`. SHA-256: `Classes/Hardware.md` `424992a5b6b1f08d5f501b0e4c2e261a9db2dde9dfe27a169ef61de32fed5d1b`; `Properties/serialNumber.md` `2c072ef3dceddb8bb506f4c6eb98110ba63eab207f99b6e1e8891c9c214bc048`; `Properties/partNumber.md` `e8f912efdeac54c13534ae9c85eea730e9a2f713d2a7fc994a98d7acab9c7dbd`; `Properties/productAgent.md` `b0e8d0d603443c476e644b29f267ceb578ee63203b5c63f4181d63d33df0e51d`; `Core/Classes/PhysicalLocation.md` `b8688875cc035d5929ea534f587a039c947780b3e8e440b49c74af0b2907515e`; `Core/Vocabularies/RelationshipType.md` `29f545173da54fbf1814754ebe40d79278a827757410086bbd0fee6f434bcf96`; `Core/Vocabularies/ExternalIdentifierType.md` `bdd79b2144ff4b0ec05245bdf32f9a7b5f25820cfbf42c45df0d0a5630ddc9fa`. |

Findings:

- **Hardware as its own class.** `Hardware.md`: "Hardware is any product, real or virtual." `Hardware` has a required `partNumber` ("Product Part Number as defined by OEM."), a required `productAgent` ("such as an original equipment manufacturer (OEM)"), and optional `serialNumber` ("a specific identifier assigned to a specific product"), `batchNumber`, `releaseDate`, `hazard`, `category` (a `DefinedType`: a type name plus its defining specification) and `additionalInformation`. It forbids the Artifact properties `originatedBy`, `suppliedBy`, `builtTime`, `releaseTime`, `standardName` and `supportLevel` (`maxCount: 0`). `PhysicalHardware` adds mass, dimensions and centre of mass; `BulkHardware` a `bulkQuantity` and no serial number.
- **Firmware gets a typed link to hardware.** New relationship `runsOn`: "The `from` Element (the instructions) runs on each `to` /Hardware/Hardware (processing element)". Also new: `hasInstall`, `locatedAt` ("`from` Element located at a specific `to` Location"), `hasInstance`, `performedBy` and 19 others (31 added since 3.0.1).
- **Locations and supply-chain identifiers.** `PhysicalLocation` has `country` (ISO 3166-1 alpha-3), `provinceStateCode`, `city`, `streetAddress` and `geographicPointLocation` (ISO 6709); `Organization` has `headquartersLocation`; SupplyChain actions have `actionLocation`. New external identifier types include `duns`, `gln`, `gtin`, `hsCodes` and `lei` (35 added since 3.0.1).
- **Still absent:** any bus or interconnect relation, and processor or core classes (only the open `category`).

### 1.6 Firmware Embedded SBOM Specification 0.10 (Open-Source Firmware Foundation)

| field | value |
|---|---|
| Citation and URL | R. Hughes (Red Hat), M. Fernandez (Eclypsium), A. Williamson (Red Hat), *Firmware Embedded SBOM Specification*, revision 0.10. <https://sbomspec.osfw.foundation/>; source <https://github.com/open-source-firmware/sbom> at commit `abab4b8960787b06d47ae5a748a4bfd1fa94d32d` (2025-06-28) |
| Version and date | 0.10, "2024-FEB-21", "Initial prerelease version. Imported text from LVFS." (revision history). The text moved from fwupd.org to this repository on 2025-06-26; the LVFS page now says "This specification has moved to the Open-Source Firmware Foundation". |
| Steward | Open-Source Firmware Foundation repository; the acknowledgements thank the "UEFI SBOM Sub Team". |
| What it is | Requirements for embedding CoSWID SBOM metadata in firmware images and their components, and for building firmware and platform SBOMs from them. |
| Licence | CC-BY-4.0 (`SPDX-License-Identifier` in every source file). |
| Library record | none (`osfw-firmware-embedded-sbom-0-10` proposed). |
| How checked | Rendered page (SHA-256 `52dcd10bcec2ac09cd44a3ae8982f415e0abc2507f8b0d2804f4a5dd59305e9e`) and the `.rst` sources at the pinned commit (`embedding.rst` `a5d03eb025c4e32f34ccb62950985705614b4e3459b816ceef645965ed1125a0`, `metadata.rst` `8f6b0c855902e90a68e4b01acb049a5a2b33562311fd55ca3a48e2ba38672ec0`, `information.rst` `c5a8c5112dde261ab615aeb7bf912a2c6e507968afaef10afc8daf966c7bb130`, `appendix.rst` `306c5b71c851067f377672c26b90dcf27fc589e0e182f14127a39951d7999bc2`, `revhistory.rst` `e3ce11e198e005a3f7181a98b70b52450aeff2dc47c7235c4edfb318c463a6bc`). `bin/bcp14-count` on the text: 109 uppercase keywords. |

Findings:

- **CoSWID is the embedded format.** §4.3: vendors "MUST use the DTMF coSWID binary format with CBOR encoding". The link goes to RFC 9393, an IETF document; "DTMF" is an error in the source (our reading).
- **Where the SBOM sits.** In a PE binary's `.sbom` COFF section (§4.4, §4.5), which "is verified by the existing Authenticode digital signature"; in any other binary behind "the discoverable uSWID header" (§4.6); and optionally as a "defragmented" firmware SBOM that "MUST contain all component SBOMs present in the image" (§4.7). Detached metadata is allowed only for space-constrained blobs such as microcode, and "MUST always contain the SHA256 hash value of the binary" (§7.1).
- **Required tag content (§5.2):** a GUID identifier; a name; at least one entity, one with the tag-creator role and one with the software-creator role; a version; and, for binaries built from source, "a file hash that is generated from all the source files" (SHA-1 or SHA-256), "what uSWID calls a "colloquial version."". A source-tree hash is "what uSWID calls an "edition."". Links: `license` (MUST, SPDX licence URL for open source), `see-also` for compiler and linker, `requires` for linked libraries, `installationmedia` for the source URL (§5.5).
- **These two fields change meaning (our reading).** RFC 9393 defines `colloquial-version` as an informal version ("a year value, a major version number") and `edition` as a functional variant ("enterprise, standard, or professional"), §2.8. A generic CoSWID consumer would read the hashes as version strings.
- **Device binding is by construction.** The SBOM travels inside the image, and an end user can dump the flash to get the "current" firmware SBOM (§6.1). A "Platform SBOM" covers "all the components in use on a real-world device" and can be "a superset that includes metadata for multiple firmware" (§3.2). Signing is optional: the SBOM "MAY be signed" (§7.5). A runtime ACPI SBOM table "may be used in the future" (§7.3).
- **No hardware facts.** Components are firmware parts ("PE files, PEIMs, CPU microcodes, CMSE/PSP, FSP/AGESA, EC and OptionROMs", §3.2); nothing describes the device.
- **VEX by GUID.** "VEX product IDs are specified using PURL, and the GUID MUST be used as the component name", with the example `pkg:dca533ab-2c1f-4327-9b2b-09ac19533404` (§6.1.1).

### 1.7 python-uswid 0.6.0 and the uSWID header

| field | value |
|---|---|
| Citation and URL | R. Hughes, *python-uswid*, <https://github.com/hughsie/python-uswid>, commit `d19305337feff3b43594ce78d9b99dd6b1480f81` (2026-09-04); PyPI package `uswid` |
| Version and date | 0.6.0, uploaded to PyPI 2026-03-16 (PyPI JSON API); latest git tag `0.6.0`. |
| Steward | Maintainer Richard Hughes. |
| What it is | A tool and library to create, merge and convert firmware SBOMs (CoSWID, SWID, CycloneDX, SPDX, INI, pkg-config, PE sections, FIT images) and to embed them behind a 16-byte magic header. |
| Licence | PyPI metadata: BSD-2-Clause-Patent; the GitHub API reports NOASSERTION. |
| Library record | none (`hughsie-python-uswid` proposed). |
| How checked | Files at the pinned commit: `README.md` `f8f883ea01d1cf603d6b095b35539923c3b1af2c275d2fc9bf56dffa746b8433`, `uswid/format_uswid.py` `a903928019695fb849487c2f5abf2dc71b50c643c889b867d11e4572590612ad`, `uswid/format_cyclonedx.py` `f95c59400674740414ff5f1a4910a08429c91e88dc86ff4670e1a13c0d9f0f24`, `uswid/format_spdx.py` `ac6d5e0536795b32f2740438403561a6743caf8897a06a45c7507776a3ad1f6c`, `uswid/component.py` `a5e017de54106e3e74115d2015af3a9d8b999aa212f6579e59ebb4034b70d5af`. Not run. |

Findings:

- **The header has three sizes.** `format_uswid.py` writes version 2 (24 bytes) for uncompressed or zlib CoSWID, version 3 (25 bytes) for LZMA, and version 4 (26 bytes) only when the payload is CycloneDX or SPDX. The README calls it a "24 byte header" in one place and "The 25 byte uSWID header in full" in another, then lists the version 4 layout (header length "typically 0x1A", that is 26). Spec 0.10 §4.6 still describes version 3 ("25-byte", "typically 0x03").
- **Hardware is lost on import.** The uSWID component types are only `firmware`, `application` and `library`; the CycloneDX importer maps `device`, `device-driver` and `platform` to `firmware` (`format_cyclonedx.py`, `_convert_str_to_component_type`).
- **Export versions.** CycloneDX output declares `specVersion` "1.6"; SPDX output declares "SPDX-2.3" (`format_cyclonedx.py`, `save`; `format_spdx.py`, line 240). The SPDX reader also accepts SPDX 3.0 JSON-LD.
- **The tag-id convention.** README: "for UEFI firmware this is typically the ESRT GUID value", which is the identifier of the updatable firmware resource (our reading: the only device-side key in this ecosystem).

### 1.8 LVFS (Linux Vendor Firmware Service) SBOM handling

| field | value |
|---|---|
| Citation and URL | LVFS documentation, "Claims" page <https://lvfs.readthedocs.io/en/latest/claims.html>; SBOM Generation Helper <https://fwupd.org/lvfs/uswid>; SBOM page <https://lvfs.readthedocs.io/en/latest/sbom.html> |
| Version and date | Documentation fetched 2026-10-08 (footer "©2016-2020"; no page date). |
| Steward | Linux Vendor Firmware Service Project, a Series of LF Projects, LLC (page footer). |
| What it is | The firmware update service used by fwupd. It scans uploaded firmware for embedded SBOMs and offers a web form that generates CoSWID, uSWID, SWID XML or INI files. |
| Licence | Not stated on the pages read. |
| Library record | none (`lvfs` proposed). |
| How checked | curl. `claims.html` SHA-256 `0dbd0b83d3a9eeaf4daaacc505f3cbec0447a39c339614a8acf9abb45263becc`; helper page `439559da838c4230161d9500835602475a7abfd041d29fc2770b5bb5ec2a125a`; `sbom.html` `e17b8e7cbc167fc05dcdc3546460d397411ca5887d1de14f494d887516f4a3d3`. A component SBOM page (`/lvfs/devices/component/64327/swid`) returned a Cloudflare challenge (HTTP 403), so no per-firmware export was inspected. |

Findings:

- **Every upload is scanned.** All uploaded firmware "gets scanned for both CoSWID data embedded in the SBOM section" of COFF binaries and for uSWID metadata; sections are appended when several are found (claims page, "Software Bill of Materials"). For blobs such as AMD microcode or Intel FSP, external metadata "is expected" from the vendor or integrator. The pages read state no rule that an upload without an SBOM is refused.
- **The helper form's fields** are CoSWID fields: tag ID ("usually a GUID"), software name and version, product, summary, colloquial version ("usually a git tree hash"), revision, edition ("usually a combined file git hash"), entity name and registration ID with roles (software creator, aggregator, distributor, licensor, maintainer), and a licence link. Output: "uSWID Header + CoSWID (recommended)", CoSWID, SWID XML or INI. No hardware field.

### 1.9 coreboot SBOM

| field | value |
|---|---|
| Citation and URL | coreboot, `Documentation/sbom/sbom.md` and `src/sbom/`, GitHub mirror commit `1fd5d0f3185fe5e8c6662ea281ccb427e96554af` (2026-10-08); rendered <https://doc.coreboot.org/sbom/sbom.html> |
| Version and date | Documentation last changed 2024-01-26; `src/sbom` last changed 2026-08-14 ("sbom: Disable VCS stamping for goswid"). |
| Steward | coreboot project. |
| What it is | An optional build step that writes a uSWID file (CoSWID tags for coreboot, payloads, microcode, Intel ME, FSP, EC, ACMs, compiler) into the CBFS of the firmware image. |
| Licence | GPL-2.0-only (headers of the templates). |
| Library record | none (`coreboot-sbom` proposed). |
| How checked | `sbom.md` SHA-256 `6b858b15f4632c4596da9dfa3b6695210bb635346c3748267089f08829e1b452`; `src/sbom/Kconfig` `8ac395589f1bfefbf073ff27e4c1b85269c54c2c08eacb64a50d97d0101cd87c`; templates `coreboot.json`, `intel-microcode.json`, `intel-me.json` read. |

Findings:

- **Format and placement.** "In coreboot it’s saved as “uSWID” file", built by the `goswid` tool and placed in CBFS. The Kconfig option `SBOM` has `default n`, so the SBOM is opt-in; there are 19 `SBOM*` options.
- **Templates carry little.** Each template has `tag-id`, `software-name`, `software-version`, `version-scheme`, `software-meta` (`persistent-id`, `summary`, sometimes `colloquial-version`) and one entity, coreboot itself, with role `tagCreator`, also for third-party blobs such as Intel ME. The documentation warns that defaults hold "very little information or even worse wrong information".
- **No hardware facts** in templates or options; the board appears only as the build target.

### 1.10 UEFI Forum SBOM sub-team material

| field | value |
|---|---|
| Citation and URL | R. Hughes and M. Fernandez, "Firmware SBOM Proposal", UEFI Forum blog, October 04, 2023, <https://uefi.org/node/5015>; T. Lewis (Insyde Software), "UEFI Unveiled: Ensuring Transparency in Your Firmware", UEFI 2024 Virtual Plugfest, <https://uefi.org/sites/default/files/resources/UEFI_Unveiled_Ensuring_Transparency_in_Your_Firmware_Final_Edit.pdf> |
| Version and date | Blog 2023-10-04; deck PDF created 2024-10-24 (PDF metadata). |
| Steward | UEFI Forum (blog and webinar series). |
| What it is | The proposal that became the Firmware Embedded SBOM Specification (1.6), and an industry deck on firmware SBOMs. |
| Licence | Not stated. |
| Library record | none (stub proposed). |
| How checked | curl. Blog HTML SHA-256 `28eb3a53718572caa078c4c6543a75aa13b6013e258f8d950fc17cc9c2ca18c8`; deck `c6f638c39223997bd6902a54c90e8f430ee9c3796ddc89eeff5aebd1f35c5c8b` (29 pages). |

Findings:

- The blog says the "UEFI SBoM Sub Team has been working on recommendations" and presents the CoSWID-plus-uSWID approach as a proposal for feedback.
- The deck shows a coSWID SBOM inside firmware file-system (FFS) entries per component, and its call to action asks vendors to produce a complete firmware SBOM "in SWID, SPDX or CycloneDX format" (slide 25). It cites the specification at its old LVFS address. No UEFI specification text for SBOMs was found.

### 1.11 Yocto Project / OpenEmbedded-Core SBOM output

| field | value |
|---|---|
| Citation and URL | Yocto Project documentation, "Creating a Software Bill of Materials", <https://docs.yoctoproject.org/dev-manual/sbom.html> ("The Yocto Project ® 6.0-tip documentation"); openembedded-core `master` at commit `aba08734931428eb3c853bb497d8e21127ad746e` (2026-10-08) |
| Version and date | Development documentation (6.0-tip) and master as of 2026-10-08. |
| Steward | Yocto Project / OpenEmbedded. |
| What it is | The build system's SPDX generator for images, SDKs and recipes. |
| Licence | Not checked. |
| Library record | none (tool; agent 5 owns tools). |
| How checked | Page SHA-256 `ea9926d993846c82ec502d285ac66975f808dcb9338aadfe029316f0c2fddab0`; `meta/classes/create-spdx.bbclass` `d1161705256481d125c416899527ce16ba4ab1d87f0a275c5c1b40c904645797`; `meta/lib/oe/spdx30_tasks.py` `f6a2707f1fa863573060aeea7e8d3c018da6440fa0d15324a431cc2007a652e1`; `meta/lib/oe/spdx30/model.py` `f69494d3b87a2f9a83852b2560cfe74a5e6f267852241f83e9f568349c9fc8d7`. |

Findings:

- **On by default, SPDX 3.0.1.** The build system generates the SBOM "by default", through `create-spdx` in `INHERIT_DISTRO`; on master `create-spdx.bbclass` is one line, `inherit create-spdx-3.0`, and the model module uses the `https://spdx.org/rdf/3.0.1/` namespace.
- **The target machine is only a name.** The image document is named `IMAGE-MACHINE.spdx.json`, and `spdx30_tasks.py` uses `MACHINE` only in object-set names (for example `"%s-%s-image" % (image_basename, machine)`); "device" occurs 0 times in that file. No hardware element is emitted.

### 1.12 Zephyr `west spdx`

| field | value |
|---|---|
| Citation and URL | zephyrproject-rtos/zephyr, `scripts/west_commands/spdx.py` and `scripts/pylib/zspdx/`, main at commit `bbc6385f0a2c6476b5f191b3101d902303a34f50` (2026-10-08); release tag `v4.4.2` (2026-08-07) |
| Version and date | As above. |
| Steward | Zephyr Project. |
| What it is | The RTOS build system's SPDX generator. |
| Licence | Apache-2.0 (repository). |
| Library record | none (tool). |
| How checked | Files at both refs. SHA-256 (main): `spdx.py` `aa9399b3f0a93dc35173035c6309aca12724bcf87486b07e30ea2066a5484b44`, `zspdx/version.py` `0475980c26baa218fc165e36ccf3eadb489a7fb5cf3fcc8136ba375eae921583`, SPDX 3 serializer `1c48e6bc655193672bebf9c42a5c199041de4a067850c1ec56dd8254bd0ebc59`, `walker.py` `9b95da525a4e1cd978db77be5efb1d1beedca56fff91cfa1bcdc0be634265d15`; v4.4.2 `spdx.py` `0f78b65151a2326b0517c557ed24537e841f9d454cd42cb0e16d0d66ba3a690a`. |

Findings:

- **Versions.** Release v4.4.2 supports SPDX 2.2 and 2.3 (`version.py`). Main adds 3.0 and 3.1 choices; the default stays 2.3 ("SPDX specification version to use (default: 2.3)").
- **The board is a build input.** On main, `BOARD`, `ARCH` and the toolchain go into `build_environment`, and the CMake system processor into a `build_parameter` named `target:processor`, of an SPDX 3 `build_Build` (serializer, `_add_build_environment`, `_add_build_parameters`). No hardware element.

### 1.13 TCG Platform Certificate Profile 2.1

| field | value |
|---|---|
| Citation and URL | Trusted Computing Group, *TCG Platform Certificate Profile*, Version 2.1. <https://trustedcomputinggroup.org/wp-content/uploads/TCG_Platform_Certificate_Profile_2.1_Pub_v2.pdf>; resource page <https://trustedcomputinggroup.org/resource/tcg-platform-certificate-profile/> |
| Version and date | 2.1, "January 27, 2026" on the cover and the resource page; the page footer reads "Version 2.1", "1/12/2026", "PUBLISHED". Previous: 2.0 Revision 39 (2024-07-29, with an errata of the same date), 1.1 Revision 19 (2020-04-10, three errata). |
| Steward | TCG Infrastructure Work Group, Platform Certificate Interoperability subgroup (acknowledgements; editor from Hewlett Packard Enterprise). |
| What it is | An X.509 attribute or public-key certificate, signed by the platform manufacturer or a later supply-chain party, asserting a platform's roots of trust, identity and component list. |
| Licence | TCG copyright; copying allowed only for "examining or implementing TCG specifications" or "developing, testing, or promoting" standards, with the notice (disclaimer page). |
| Library record | none (`tcg-platform-certificate-profile-2-1` proposed). Related stubs in topic `device-attestation`: `tcg-tpm2-keys-device-identity`, `tcg-dice-*`. |
| How checked | The resource page returned a Cloudflare challenge; the Wayback capture of 2026-09-02 (decompressed SHA-256 `3e86f35c6728484acc83a731e3c02f4aeef19cb3cd5f9f7724e28b2e7c6a30a6`) lists the versions. The PDF downloaded directly: SHA-256 `077676d51348c973bf94ac0c8842c975be36f096b4b4854e8cf3efa4b81adaa7` (67 pages). Also downloaded v1.1 r19: `6725293f3a13caa152b8b1f21014344b3002f2546df3df60142a1e4e83216e64`. `bin/bcp14-count`: 301 keywords. A WebSearch summary that said no version 2.0 was public was rejected (section 9). |

Findings:

- **TCG presents it as an HBOM carrier.** Resource page: "The component list attribute supports recent calls for a Hardware Bill of Material (HBOM) artifact".
- **Component identity (§3.3.19).** `PlatformConfiguration-v3` holds `platformComponents`, a flat SEQUENCE OF `ComponentIdentifier-v2`, each a SEQUENCE OF `Trait` (`traitId`, `traitCategory`, `traitRegistry`, `description`, `descriptionURI`, `traitValue`). Each component SHALL have a class, manufacturer and model trait, SHOULD have a serial and field-replaceable trait, and MAY have a revision trait; in a Delta certificate a status trait (added, modified, removed) is required. The 1.1-compatible `ComponentIdentifierV11` keeps `componentClass`, `componentManufacturer`, `componentModel`, `componentSerial`, `componentRevision`, `componentManufacturerId` (PEN), `fieldReplaceable`, `componentAddresses` (Ethernet, WLAN, Bluetooth MAC), `componentPlatformCert`, `componentPlatformCertUri` and `status`.
- **An inconsistency.** §4.2.5 says a V11 trait "SHALL populate the componentClass, componentManufacturer and componentSerial fields", but its ASN.1 marks `componentSerial` OPTIONAL, while §3.3.19 makes the serial trait only SHOULD.
- **New in 2.1: origin and part numbers.** `countryOfOriginTrait` (`OriginComposition`: `location` and `hasComponents`) and `entityGeoLocationTrait` ("the geographic location of a supply chain entity": ISO 3166 country code, subdivision, locality, street, Open Location Code coordinates, postal code), §4.2.22 and §4.2.23; a `componentPartNumber` trait category, because components "may be associated with multiple part numbers" (§4.1.2); and a `manufacturingAssertions` attribute "about the manufacturing and supply chain properties of the platform" (§2.1.4.18, §3.3.22).
- **The 2.1 ASN.1 has editorial defects.** `EntityGeoLocation` has no closing brace and skips tag [4]; `countryOfOriginTrait` uses `WITH SYNTAX` and `OriginComposition SEQUENCE ::= Sequence {` with a trailing comma; the §4.2.22 heading reads "End of informative commententityGeoLocationTrait"; §4.1.2 says a trait that "contains a component location SHALL have tcg-tr-cat-componentPartNumber" (our reading: a copy slip for "part number"). A parser cannot take this module as written.
- **Signed, not measured.** A Platform Certificate is "a signed statement" (§2); certificates "are Endorsements that a Verifier uses when evaluating the Evidence provided by an Attester" (§2.1.1). The certificate binds to the platform's roots of trust through Cryptographic Anchors (EK, IDevID or DICE certificates, §2.1.4.9).
- **Lifecycle and custody.** Base, Delta and Rebase certificates; integrators and VARs link theirs to the previous one, "thus creating a chain of custody in the supply chain" (§2.1.3). A Delta certificate SHALL keep the platform manufacturer, model and serial number of the base (§2.2.3).
- **Unit identity.** Platform Serial Number, when present, "SHALL contain a customer-visible serial number" (§2.1.4.14).
- **Practice.** NSA's open-source PACCOR (`nsacyber/paccor`, release `v2.0r16`, 2026-10-04, Apache-2.0) "creates, signs, inspects, and validates TCG Platform Certificates"; its README (SHA-256 `f851c53111aaba7cc258ea7fe186dc49569cf815dba22f8e71848287d567a93b`) says it supports v2.1, v1.1 and v1.0, with v1.1 the default output. NSA's HIRS (`v3.2.0`, 2026-06-17) validates them. Neither was run.

### 1.14 TCG Component Class Registry 1.0 r14, and the PCIe, SMBIOS and Storage registries

| field | value |
|---|---|
| Citation and URL | TCG, *TCG Component Class Registry*, Version 1.0 Revision 14, <https://trustedcomputinggroup.org/wp-content/uploads/TCG_Component_Class_Registry_v1.0_rev14_pub.pdf>; *PCIe-based Component Class Registry* Version 1 Revision 18, <https://trustedcomputinggroup.org/wp-content/uploads/TCG_PCIe_Component_Class_Registry_v1_r18_pub10272021.pdf>; *SMBIOS-based Component Class Registry* Version 1 Revision 01, <https://trustedcomputinggroup.org/wp-content/uploads/SMBIOS-Component-Class-Registry_v1.01_finalpublication.pdf> |
| Version and date | Component Class Registry 1.0 r14, 2023-05-31; PCIe r18, 2021-10-27; SMBIOS r01, 2021-02-18; Storage 1.0 r22, 2024-01-26 (latest versions on the archived resource pages of 2026-09-02). |
| Steward | TCG. |
| What it is | Registries of 4-byte `componentClassValue` codes used in Platform Certificates, and rules for filling component fields from device data. |
| Licence | TCG copyright (as 1.13). |
| Library record | none (`tcg-component-class-registry-1-0-r14` proposed; PCIe registry `tcg-pcie-component-class-registry-1-r18`). |
| How checked | Resource pages via Wayback (2026-09-02). PDFs downloaded directly: TCG registry SHA-256 `3b5496bb99b6740a9f53a233349b89c5dc0aa6e6d74b60387577c3e121bc40a3` (16 pages); PCIe `453bad2ac9729058c3403592952d1c2a0a8aec6702fc8a5aed351e26c80eea10`; SMBIOS `15c55ff595f737670adb1b7d7ddfc8cd6e31dcaac22f70c6bb3dd10a6c1d863d`. Table 1 of the TCG registry parsed with a regular expression over the layout text (names that wrap onto two lines are truncated in the parse). The Storage registry PDF was not downloaded. |

Findings:

- **Classes found (Table 1, our parse): 87 values in 13 categories**: general (1), microprocessor (8: General Processor, CPU, DSP Processor, Video Processor, GPU, DPU, Embedded processor, SoC), container (16, including Main Server Chassis, Sub Chassis, Blade, IoT), IC board (4, including Daughter board, Riser Card), module (2, including TPM), controller (14, including Ethernet, SATA, SAS, USB controllers, BMC, DMA controller), memory (9), storage (6), media drive (4), network adapter (10, including Wi-Fi, Bluetooth, 5G, Network Switch, Network Router), energy object (3), cooling (3), input (1), firmware (6: General Firmware, System firmware, Drive firmware, Bootloader, SMM, NIC firmware).
- **No class for a bus or for a core.** "bus" occurs once, in "A Universal Serial Bus port controller". Processors are typed (CPU, GPU, SoC), cores are not.
- **Sources of the codes.** Some values copy SMBIOS (DMTF DSP0134), RFC 6933 and RFC 8348 codes; the rest are "TCG Defined".
- **The PCIe registry measures identity from the device.** `componentClassValue` is the PCIe Class Code Register; `componentManufacturer` is Vendor ID, Subsystem Vendor ID and the VPD manufacturer string; `componentModel` is Device ID, Subsystem ID and the VPD part number; `componentSerial` is the EUI-64 Serial Number capability and the VPD serial; `componentRevision` is the Revision ID (Table 1 of that registry). So a verifier can read the same values from configuration space and compare.

### 1.15 TCG DICE Attestation Architecture 1.2

| field | value |
|---|---|
| Citation and URL | TCG, *DICE Attestation Architecture*, Version 1.2, <https://trustedcomputinggroup.org/wp-content/uploads/DICE-Attestation-Architecture-v1.2_pub.pdf>; *Errata v1.0 r1 for DICE Attestation Architecture Version 1.2*, <https://trustedcomputinggroup.org/wp-content/uploads/Errata-v1.0-r1-for-DICE-Attestation-Architecture-Version-1.2_pub.pdf> |
| Version and date | 1.2, 2025-04-24 (cover; footer "Revision 3"); errata 2026-01-29. Earlier on the resource page: 1.1 Revision 18 and 1.0 Revision 0.23. |
| Steward | TCG DICE Work Group. |
| What it is | X.509 certificate extensions that carry measurements of each DICE layer (DiceTcbInfo and others), signed by the previous layer. |
| Licence | TCG copyright. |
| Library record | none for this document (`tcg-dice-attestation-architecture-1-2` proposed). Existing stubs: `tcg-dice-layering`, `tcg-dice-cert-profiles` (pinned to r01; the resource page lists v1.1 of 2025-04-24 as latest), `tcg-dice-hw-requirements`, `tcg-dice-implicit-identity`, `tcg-dice-symmetric`, `google-open-dice`. |
| How checked | Resource page via Wayback (2026-09-30). PDFs: SHA-256 `a930c341a65493e87d42207ac485da0b97fe0eb2c0ce0c7642316e7825759f2d` (44 pages) and errata `86c706b8942658f59b31dc0346da8478b1bb37dc4968a44a5f00d391d02b96da`. `bin/bcp14-count`: 81. |

Findings:

- **Measured evidence in the certificate.** §6.1.1: the extension carries "attestation Evidence about a Target Environment that is measured by an Attesting Environment". `DiceTcbInfo` fields: `vendor`, `model`, `version`, `svn`, `layer`, `index`, `fwids` (`hashAlg`, `digest`), `flags`, `vendorInfo`, `type`, and (corrected by the errata) `flagsMask` [10] and `integrityRegisters` [11]; the published 1.2 text wrongly replaced `flagsMask` with `integrityRegisters`.
- **The measurement is bound into the key.** Any field "that contributes to the CDI that generates the subject key" must be in the extension (§6.1.1), so a firmware change changes the device's attestation key.
- **Device identity.** A UEID extension "identifies the device containing the private key" (§6.1.4).
- **CoSWID as evidence.** §6.1.6: "A SWID or CoSWID manifest may be used to contain Evidence", unsigned inside the signed certificate.
- **Layers are boot stages,** not physical parts (our reading); there is nothing about boards, buses or origin.

### 1.16 DMTF SPDM (DSP0274) 1.4.1

| field | value |
|---|---|
| Citation and URL | DMTF, *Security Protocol and Data Model (SPDM) Specification*, DSP0274 version 1.4.1, <https://www.dmtf.org/sites/default/files/standards/documents/DSP0274_1.4.1.pdf> |
| Version and date | 1.4.1, dated 2026-06-26, "Supersedes: 1.4.0", "Document Status: Published". The DMTF SPDM page (Wayback capture 2026-09-30) lists DSP0274 1.4.1 as published; URL probes for 1.4.2 and 1.5.0 returned 404. |
| Steward | DMTF Security Protocols and Data Models Working Group. |
| What it is | A request-response protocol for device authentication and measurement (MCTP, PCIe DOE and other transports are bindings). |
| Licence | DMTF copyright; "Members and non-members may reproduce DMTF specifications" for consistent uses "provided that correct attribution is given". |
| Library record | none (`dmtf-dsp0274-1-4-1` proposed). |
| How checked | dmtf.org pages returned Cloudflare challenges; the PDF downloaded directly. SHA-256 `a5259037e0853913efc0efd07358669a4bcfc630d3a61eb1cf09e3758db057b6` (313 pages). The DSP0274 page capture of 2026-08-24 lists versions 1.0.0 to 1.4.1. |

Findings:

- **Measurement kinds (Table 61).** `DMTFSpecMeasurementValueType` 0x0 "Immutable ROM.", 0x1 "Mutable firmware.", 0x2 hardware configuration, 0x3 firmware configuration, 0x4 freeform manifest, 0x5 debug and device mode, 0x6 firmware version number, 0x7 firmware security version number, 0x8 hash-extend measurement, 0x9 informational, 0xA structured manifest. Each block holds a digest or a raw bit stream (Table 60).
- **Signed by the device.** MEASUREMENTS responses are signed over a transcript of the exchanged messages (§10.12.3).
- **Hardware identity.** A certificate chain "should contain at least one certificate that includes hardware identity information"; that key pair "is constant on the instance of the device, regardless of the version of firmware" (§7.2.1.1). A `DMTFOtherName` (OID 1.3.6.1.4.1.412.274.1) carries "manufacturer:product:serialNumber" (§10.9.2).
- **Manifests can carry other formats.** A structured manifest starts with a standards-body header; registry ID 0xA, "IANA CBOR", identifies the content by CBOR tag (Table 67), which could carry a CoRIM or CoSWID (our reading; the manifest format is "outside the scope of this specification").
- **FX-1 caveat.** DMTF writes requirements in lowercase ("shall" 1,367 times, "should" 141); `bin/bcp14-count` counts uppercase keywords only and returns 1.

### 1.17 DMTF Redfish schema bundle DSP8010 2026.2

| field | value |
|---|---|
| Citation and URL | DMTF, Redfish schemas (DSP8010), release 2026.2; read-only copy <https://github.com/DMTF/Redfish-Publications>, tag `2026.2` (commit `4f81814e399213c9055863ddaff42791c6b3706a`); published schemas <https://redfish.dmtf.org/schemas/v1/> |
| Version and date | 2026.2, tagged 2026-09-16; each schema file carries `"release": "2026.2"` (for example `Processor.v1_24_0.json`). |
| Steward | DMTF Redfish Forum. |
| What it is | The JSON Schemas of the Redfish management API: the model a management controller uses to report a server's or device's hardware, firmware and integrity. |
| Licence | BSD-3-Clause (`LICENSE.md` of the publications repository). |
| Library record | none (`dmtf-redfish-schema-2026-2` proposed). |
| How checked | Latest versions read from the schema index and pinned to the tag. SHA-256: `Processor.v1_24_0.json` `2a361cc2eb8de3e0d01584d50170a0712cbe3c58332629f48f4f1356b4c46179`; `Memory.v1_24_0.json` `d5605e51993f1bfa829d0dc3b3dc7d62949075706ebd661c35715affa39b43be`; `PCIeDevice.v1_23_0.json` `7ba6efd837063a18e4950949b9b618a241d69f9864c646de29f29f805b617f18`; `PCIeFunction.v1_7_0.json` `ac3e8c5d1797ada4c873350c08475806bb01ee75e61d7022c906da06da940708`; `Assembly.v1_6_1.json` `a7a6c46e3970943e46625a8374bdee2e23b51c52677351bc293bf0e192e936b2`; `Chassis.v1_29_0.json` `bdd9ef9925d743a47882461bb948fff9f942d22572e7d01594908119b2eaeda2`; `SoftwareInventory.v1_15_0.json` `0c06060359fc2e2552b4248a8f04c468043d6699c2dd566b7725bfc6a3dcb61e`; `ComponentIntegrity.v1_5_0.json` `d44725c9019e6496183758652ad124e197408269b1e37b361b8b7b8a36363ef9`; `Resource.v1_25_0.json` `5f14c13aeecea3e3222cbc6903bd97f5ea5101af32f8138f70ff379f67c8519b`. Parsed with python3. |

Findings:

- **Processor and cores.** `ProcessorType`: `CPU`, `GPU`, `FPGA`, `DSP`, `Accelerator`, `Core` ("A core in a processor."), `Thread`, `Partition`, `OEM`. `SubProcessors` links "cores or threads, that are part of a processor"; also `TotalCores`, `ProcessorArchitecture` (x86, IA-64, ARM, MIPS, Power, RISC-V, OEM), `ProcessorId` (vendor ID, identification registers, microcode), `Manufacturer`, `Model`, `PartNumber`, `SerialNumber`, `UUID`, `FirmwareVersion`, `Socket`, `Location`. 67 properties.
- **Buses.** `PCIeDevice` has `PCIeInterface` (`PCIeType`, `LanesInUse`, `MaxLanes`), `DeviceType` (`SingleFunction`, `MultiFunction`, `Simulated`, `Retimer`), `Slot`, `Manufacturer`, `PartNumber`, `SerialNumber`, `FirmwareVersion`; `PCIeFunction` has `BusNumber`, `DeviceNumber`, `FunctionNumber`, `VendorId`, `DeviceId`, `ClassCode`, `SubsystemId`, `SubsystemVendorId`, `RevisionId` and a `DeviceClass` enum (23 values). Processors link to their PCIe device and functions.
- **Assemblies and containment.** `Chassis.Links.Contains` is "An array of links to any other chassis that this chassis has in it", with `ContainedBy`; `ChassisType` has 24 values (Rack, Blade, Card, Module, Component and others). `AssemblyData` has `Model`, `PartNumber`, `SparePartNumber`, `SKU`, `SerialNumber`, `Vendor`, `Producer`, `ProductionDate`, `EngineeringChangeLevel`, `Version`, `PhysicalContext`, `Location`, `Replaceable`, `BinaryDataURI` and `ISOCountryCodeOfOrigin` ("the manufacturing country of origin", alpha-2 or alpha-3). `PartLocation.LocationType`: Slot, Bay, Connector, Socket, Backplane, Embedded.
- **Firmware bound to devices.** `SoftwareInventory.RelatedItem` lists "devices to which this software inventory applies"; also `Version`, `VersionScheme` (SemVer, DotIntegerNotation, OEM), `SoftwareId`, `Manufacturer`, `ReleaseDate`, `UefiDevicePaths`, `AdditionalVersions` (bootloader, kernel, microcode and others).
- **Measurements moved to ComponentIntegrity.** `Processor.Measurements`, `Memory.Measurements` and `SoftwareInventory.Measurement` are "deprecated in favor of the `ComponentIntegrity` resource". `ComponentIntegrity` reports SPDM or TPM measurement sets for a `TargetComponentURI`, using the DMTF measurement types of 1.16, and has an `SPDMGetSignedMeasurements` action that returns signed measurements with the certificate.
- **Location is where the equipment is, not where it was made.** `Location` (`PostalAddress` with 33 properties, `Latitude`, `Longitude`, `Placement`, `PartLocation`) describes the installed position; only `ISOCountryCodeOfOrigin` is about origin.

### 1.18 IETF CoRIM (draft-ietf-rats-corim-11)

| field | value |
|---|---|
| Citation and URL | H. Birkholz, T. Fossati, Y. Deshpande, N. Smith, W. Pan, *Concise Reference Integrity Manifest*, draft-ietf-rats-corim-11, <https://www.ietf.org/archive/id/draft-ietf-rats-corim-11.txt> |
| Version and date | Revision 11, 6 July 2026, expires 7 January 2027. Datatracker (API, 2026-10-08): state Active, IESG "I-D Exists", stream state "In WG Last Call", intended status Proposed Standard. |
| Steward | IETF RATS working group. |
| What it is | A CBOR format for reference values and endorsements (CoMID, CoSWID and CoTL tags) that a verifier compares with evidence. |
| Licence | IETF Trust Legal Provisions (BCP 78). |
| Library record | `draft-ietf-rats-corim` (stub; its `identifiers.draft` is empty and its URL is `https://datatracker.ietf.org/doc//`). |
| How checked | Text SHA-256 `cdbfa267337e35c6e03170b2c40ac36c95895561aef82418470a76c239b65053`; CDDL read with sed. `bin/bcp14-count`: 135. |

Findings:

- **Environments name what is measured.** `environment-map`: `class` (`class-id` as OID, UUID or bytes; `vendor`; `model`; `layer`; `index`), `instance`, `group`. "An environment MUST be globally unique."
- **Measured values.** `measurement-values-map`: `version`, `svn`, `digests`, `flags`, `raw-value`, `mac-addr`, `ip-addr`, `serial-number`, `ueid`, `uuid`, `name`, `cryptokeys`, `integrity-registers`, `int-range` (§5.1.4.5.2).
- **Composition as a graph.** Domain membership triples link a domain to its member environments; members can be domains, enabling "the recursive construction of an entity's topology", and "The domain topology MUST be acyclic." Trust dependency triples say which components a component "depends on" (§5.1.11). This is a typed containment and dependency graph for composite devices.
- **Firmware bills linked to targets.** A CoSWID triple "relates reference measurements contained in one or more CoSWIDs to a Target Environment" (§5.1.12).
- **Signed.** "A CoRIM tag MUST be wrapped in a COSE_Sign1 structure." (§4.2); the CDDL also defines an unsigned tagged map (tag 501) as an entry point (§4.1).

### 1.19 IETF EAT (RFC 9711)

| field | value |
|---|---|
| Citation and URL | L. Lundblade, G. Mandyam, J. O'Donoghue, C. Wallace, *The Entity Attestation Token (EAT)*, RFC 9711, <https://www.rfc-editor.org/rfc/rfc9711.txt> |
| Version and date | RFC 9711, Standards Track, April 2025 (from draft-ietf-rats-eat-31; datatracker state "RFC Published"). |
| Steward | IETF RATS working group. |
| What it is | Claims for attestation evidence and results, in a CBOR Web Token (CWT) or JSON Web Token (JWT). |
| Licence | IETF Trust Legal Provisions. |
| Library record | `rfc-9711` (stub). |
| How checked | Text SHA-256 `20d43b5a03151e5023533e069835e5581ebcaf5a70779a216d3d0ca06f2fd2c7`. `bin/bcp14-count`: 115. |

Findings:

- **Entity identity.** `ueid` identifies "an individual manufactured entity"; "It is akin to a serial number, though it does not have to be sequential." (§4.2.1). `oemid` (random, IEEE or PEN based), `hwmodel` (opaque, at most 32 bytes, unique within an OEM ID), `hwversion` (§4.2.3 to 4.2.5).
- **Manifests versus measurements.** `manifests`: "The defining characteristic of a manifest is that it is created by the software manufacturer." (§4.2.15). `measurements`: "its contents are created by processes on the entity"; a CoSWID here "MUST be an evidence CoSWID" (§4.2.16). The token keeps the manufacturer's claim and the device's own measurement apart.
- **Nesting.** `submods`: "A submodule may include a submodule, allowing for arbitrary levels of nesting." (§4.2.18).
- **Location is current position,** "the geographic position of the entity from which the attestation originates" (§4.2.10), not manufacturing origin.

### 1.20 IETF SUIT manifest (draft-ietf-suit-manifest-37), with RFC 9019 and RFC 9124

| field | value |
|---|---|
| Citation and URL | B. Moran, H. Tschofenig, H. Birkholz, K. Zandberg, Ø. Rønningstad, *A Concise Binary Object Representation (CBOR)-based Serialization Format for the Software Updates for Internet of Things (SUIT) Manifest*, draft-ietf-suit-manifest-37, <https://www.ietf.org/archive/id/draft-ietf-suit-manifest-37.txt>; RFC 9019 (architecture) and RFC 9124 (information model) |
| Version and date | Revision 37, 18 June 2026. Datatracker: IESG state "RFC Ed Queue", RFC Editor state "Blocked", IANA "RFC-Ed-Ack"; not yet an RFC. RFC 9019: Informational, April 2021. RFC 9124: Informational, January 2022. |
| Steward | IETF SUIT working group. |
| What it is | A signed manifest that tells an IoT device which firmware images to fetch, check and install. |
| Licence | IETF Trust Legal Provisions. |
| Library record | none (`draft-ietf-suit-manifest`, `rfc-9019`, `rfc-9124` proposed as stubs). |
| How checked | SHA-256: draft `6f20207134bdb011a601b661f9373ff085dde8f6ff9e3aacb070acd156f6c7c3`, RFC 9019 `b29e6c39ff2db10cb4c138c0c45bd47a478386a6b053b02129b3704efa1008e6`, RFC 9124 `0a1647c36503262689791fe2853dd6a450314ea8b8a7f9add65c806a6319d354`. `bin/bcp14-count` on the draft: 165. |

Findings:

- **Identifiers are compatibility checks.** Vendor, class and device identifiers are UUIDs (vendor ID from the vendor's domain name, class ID from vendor ID plus model number, hardware revision or bootloader version); "They MUST NOT be used as assertions of identity." (§8.4.8.2). `suit-parameter-device-identifier` is a UUID for "the specific device or component" (§8.4.8.5).
- **Firmware binding.** Components are `SUIT_Component_Identifier` arrays of byte strings; images are checked by `suit-parameter-image-digest` and `-image-size`. The text map adds `suit-text-vendor-name`, `-model-name`, `-vendor-domain`, `-model-info`, `-component-description`, `-component-version`.
- **A hardware example.** A device with "A host Microcontroller" and "A Wi-Fi module" reports class IDs for the hardware model, the OS, the Wi-Fi module and the application, so that each can be updated separately (§8.4.8.2).

### 1.21 RFC 9334, RATS architecture

| field | value |
|---|---|
| Citation and URL | RFC 9334, *Remote ATtestation procedureS (RATS) Architecture*, <https://www.rfc-editor.org/rfc/rfc9334.txt> |
| Version and date | Informational, January 2023. |
| Steward | IETF RATS working group. |
| What it is | The roles (Attester, Verifier, Relying Party, Endorser) and conceptual messages (Evidence, Endorsements, Reference Values) that CoRIM, EAT, SPDM-based and TCG designs use. |
| Licence | IETF Trust Legal Provisions. |
| Library record | `rfc-9334` (stub). |
| How checked | SHA-256 `b80d035fb64a00a637d4888d2855772412246230913231301727ef78d4b00540`. |

Findings:

- A composite device is "an entity composed of multiple sub-entities" whose trustworthiness depends on all of them; the example is a router chassis with slots, where a main slot collects the others' evidence (§3.3). This is the attestation view of a hierarchical system.

### 1.22 RFC 9393, CoSWID: re-check for hardware

| field | value |
|---|---|
| Citation and URL | RFC 9393, *Concise Software Identification Tags*, <https://www.rfc-editor.org/rfc/rfc9393.txt> |
| Version and date | Standards Track, June 2023. |
| Library record | none in the library (agent 1 owns CoSWID). |
| How checked | SHA-256 `6708be37258615edb39de76e32b11439967885d6792f4e2f0ee02de1a0864ebc`; grep. |

Findings:

- The v0.1.0 statement holds: "hardware" and "firmware" occur 0 times. "device" occurs 15 times; the one device field is the evidence entry's `device-id`, "The endpoint's string identifier from which the evidence was collected" (§2.9.4). CoSWID's CDDL has extension sockets (`$$...-extension`, §2.2).

### 1.23 ISO/IEC 19770-6:2024, Hardware identification tag: public information only

| field | value |
|---|---|
| Citation and URL | ISO/IEC 19770-6:2024, *Information technology, IT asset management, Part 6: Hardware identification tag* (title punctuation changed here). Catalog page <https://www.iso.org/standard/77642.html>; BSI page of the identical British adoption <https://knowledge.bsigroup.com/products/information-technology-it-asset-management-hardware-identification-tag> |
| Version and date | Edition 1, published 2024-01-26, 41 pages, stage 60.60, ISO/IEC JTC 1/SC 7 (ISO Open Data, record id 77642). BS ISO/IEC 19770-6:2024 published by BSI on 30 June 2024. |
| Steward | ISO/IEC JTC 1/SC 7. |
| What it is | A tag format for hardware identification data, the hardware counterpart of SWID tags. |
| Licence | Paywalled; © ISO/IEC. |
| Library record | none (`iso-iec-19770-6-2024` proposed as a stub). |
| What was read | (1) ISO Open Data `iso_deliverables_metadata.csv` (the file downloaded by Ty on 2026-09-30, SHA-256 `4bd58c011cbce818a5881874b111c04d52cf86b8d9740c8dd8149d012c603662`): reference, dates, pages, scope text. (2) The ISO catalog page as captured by the Wayback Machine on 2026-03-12 (decompressed SHA-256 `c16cdf057e42c1d96b2d824f78c046ebb8051b860cb97fba65b55c7fe7042ba6`): status and life-cycle dates; the live page and the OBP preview returned Cloudflare challenges, and the browser extension was not connected. (3) BSI's public preview of BS ISO/IEC 19770-6:2024 (8 pages: cover, national foreword, contents list, foreword, part of the introduction), <https://middleware.accord.bsigroup.com/pdf-preview?path=Preview%2F000000000030404170.pdf>, SHA-256 `1cd47fbed274b43f154ea00437da2e05637601ef3ba48905a1ee2850945aedfd`. |
| What was not read | Clauses 1 to 7 and Annexes A to C: the definition of each element and attribute, cardinalities, conformance rules, the XSD, and the sample tags. Nothing here says which fields are required or whether any tool produces HWID tags. No public material by its editors was found (two searches). |

Findings (from the public material only):

- **Scope (ISO metadata).** It "provides specifications for a transport format" and "deals only with hardware device or component identification"; it applies to tag producers (device or component providers, tag tool providers) and tag consumers (device consumers, IT discovery tools).
- **Life cycle (ISO page).** New project approved 2019-09-25; CD consultation 2021-12-09; DIS ballot 2022-11-16 to 2023-02-09; FDIS ballot closed 2023-12-19; published 2024-01-26. A BSI draft for comment of 22 November 2022 (22/30404169 DC) carried the title "Part 6. Hardware schema" (BSI page).
- **Contents list (BSI preview).** Conformance for HWID tags, applications and platforms (4.1 to 4.3); hardware identifiers `<hwidID>` (5.2); HWID types: primary HWID and system HWID, each with issuance, adding information and archiving, and "Systems of systems" (5.4.2 to 5.4.8); supplemental HWID types (5.5); uniqueness of `regid` and `hwidId` (5.7); trustworthiness and authenticity of HWIDs, with XML and JSON digital signatures (6.4, 6.5); minimum and recommended tag data (7.2, 7.3); XML and JSON naming conventions (7.4); data definitions `HWID`, `HWIDMeta`, `Entity`, `Link`, `LinkContent`, `Meta`, `OrderInfo`, `Location` (7.7); attribute value sets `ChannelType`, `HWIDType`, `hwType`, `purchaseCondition`, `LocationType`, `Role`, `SupplementalHWIDType`, `TrustLevel`, `Rel` (7.8); informative XSD (Annex A), UML (Annex B) and sample HWIDs (Annex C).
- **Introduction (BSI preview).** The tag holds identification data about a hardware product "and/or the system configuration of multiple hardware products", "often provided in an XML data file" (0.2).
- **Our reading of the contents list only:** the element names suggest it covers identity, entities, links between tags, ordering information, locations, system-level tags and signatures, structured like SWID; whether `Location` means manufacturing origin or installed location, and what `OrderInfo` holds, cannot be told without the text.

### 1.24 CERT-In, Technical Guidelines on SBOM, QBOM and CBOM, AIBOM and HBOM, Version 2.0

| field | value |
|---|---|
| Citation and URL | Indian Computer Emergency Response Team (CERT-In), MeitY, *Technical Guidelines on SBOM, QBOM & CBOM, AIBOM, HBOM*, Version 2.0, dated 09.07.2025, <https://www.cert-in.org.in/PDF/TechnicalGuidelines-on-SBOM,QBOM&CBOM,AIBOM_and_HBOM_ver2.0.pdf> (RPT-0014 source S-0847) |
| Version and date | 2.0, 2025-07-09 (page footers "Version 2.0 Dated 09.07.2025"); 66 pages. No newer version found (one search). |
| Steward | CERT-In, Ministry of Electronics and Information Technology, India. |
| What it is | National guidance covering SBOM, quantum and cryptographic BOMs, AI BOMs and, in section 10, HBOMs. |
| Licence | No statement found in the text. |
| Library record | none; RPT-0014 named it `cert-in-2025-aibom-guidelines` ("not yet a record"); reuse that id. |
| How checked | curl; SHA-256 `28aa48f329114d665f8e4f8c4d2f33baf4981e29168a318e6e719c11a5ff5151`, identical to RPT-0014's. Section 10 read in full. `bin/bcp14-count`: 0 (lowercase "must" and "should"). |

Findings:

- **A minimum element list, no format.** Table 11 ("Minimum Elements of HBOM", §10.3) has 20 rows and 18 distinct names: Product Name, Product Version, Product Details, Warranty/AMC, Manufacturer Name, Manufacturer Location, Manufacturing Date, Supplier Information, Supplier Location, Model Number, Serial Number, Technical Specification, a second Supplier Information and Supplier Location (for the component's supplier), Technology Node, Compliance, Power supply, License Information, Test Result, Sub-component. On formats it says only "preferably using extended SBOM formats like CycloneDX or custom XML/JSON schemas" (§10.4.1.6).
- **Unit-level and recursive.** Serial Number is "A unique identifier assigned to each individual unit"; Sub-component "refers to the recursive nature of an HBOM". Yet §10.4.1.9 says "A separate HBOM must be maintained for each hardware version or model". Our reading: per-model documents with a per-unit field leave open where unit serials go.
- **Requirements for government supply.** Hardware supplied to government and public-sector bodies "must be accompanied by a complete and accurate HBOM" (§10.4.1.2), with "manufacturer name, model number, component version, firmware version, origin, criticality rating, and associated vulnerabilities" (§10.4.1.4); firmware version, criticality rating and vulnerabilities are not Table 11 elements. Vendors "must provide" a VEX or equivalent hardware vulnerability statement with the four CISA statuses, then a CSAF advisory (§10.4.1.5).

### 1.25 Auto-ISAC, Software Bill of Materials (SBOM) Informational Report, v3.0

| field | value |
|---|---|
| Citation and URL | Automotive Information Sharing and Analysis Center (Auto-ISAC), *Auto-ISAC Software Bill of Materials (SBOM) Informational Report*, TLP:CLEAR, V 3.0, January 17, 2025. <https://automotiveisac.com/s/2025_01_17_SBOM-IR_v30_TLP_CLEAR-1.pdf> (linked from <https://automotiveisac.com/sbom-reports>; public release announced 2025-02-11) |
| Version and date | 3.0, 2025-01-17; 101 pages. |
| Steward | Auto-ISAC SBOM Working Group. |
| What it is | Industry practice guidance on SBOM creation and exchange between vehicle OEMs and tier suppliers. |
| Licence | "© 2025 Auto-ISAC. All rights reserved."; marked TLP:CLEAR. |
| Library record | none (`auto-isac-sbom-ir-v3` proposed). |
| How checked | curl (redirects to a Squarespace static URL); SHA-256 `5a3c0587db01494fdbe8740924f9a2d086981f2c573d36c58ee8e537db688740`; grep for hardware, HBOM, ECU, firmware, formats, R155, R156. |

Findings:

- **Software only.** The working group's "scope of study is limited to vulnerability management and cybersecurity" (§1.5); "HBOM" occurs once, in a tool list (Appendix B). Hardware appears in passing: a supplier can share "SBOM parts that are known to be stable such as hardware component SBOMs" (§6.8.3).
- **Formats.** It recommends "either SPDX or CycloneDX SBOM formats in JSON" (§4.13) and CSAF with the VEX profile for vulnerability information (§4.14). Its examples are SPDX 2.3 and CycloneDX JSON for an OEM software release built from supplier modules (Appendix A).
- **Tiers.** OEMs are responsible "for the entire vehicle including all parts sourced from suppliers", Tier-1s to OEMs, Tier-2s to Tier-1s (§1.4).
- **Regulation.** On UN R155: "the rule does not explicitly refer to SBOMs" (§2.6.3).

### 1.26 UN Regulations No. 155 and No. 156 (2021 texts)

| field | value |
|---|---|
| Citation and URL | UNECE, E/ECE/TRANS/505/Rev.3/Add.154 (UN Regulation No. 155) and Add.155 (UN Regulation No. 156), 4 March 2021, <https://unece.org/sites/default/files/2021-03/R155e.pdf> and <https://unece.org/sites/default/files/2021-03/R156e.pdf> |
| Version and date | Original texts, in force as annexes to the 1958 Agreement from 22 January 2021. Later supplements and the WP.29 interpretation documents were not checked. |
| Steward | UNECE WP.29. |
| What it is | Type-approval regulations for the cybersecurity management system (R155) and the software update management system (R156). |
| Licence | Not stated in the extract read. |
| Library record | none (`unece-r155`, `unece-r156` proposed as stubs). RPT-0007 covers ISO/SAE 21434 and ISO 24089. |
| How checked | unece.org returned Cloudflare challenges; Wayback captures of 2023-05-30 (R155, SHA-256 `81695076742173c80f72f54414ae3ed6c310f49a277738815f8e2d2ccb379187`, 30 pages) and 2023-12-16 (R156, SHA-256 `9a7b419295a56b718404131d9dde1f464cbde834d157c61a8f4f969816dcb5a8`, 16 pages). grep. |

Findings:

- "bill of material" and "SBOM" occur 0 times in either text.
- R156 asks for a process whereby software versions "and relevant hardware components of a type approved system can be uniquely identified" (§7.1.1.2), for documentation with "unique identification for the type approved system’s hardware and software" (§7.1.2.2), and for an auditable register for each RXSWIN (§7.1.2.3; RXSWIN is defined in §2.2). It names no format. Agent 2 covers RXSWIN.

### 1.27 ITU-T SG17 Contribution 548: proposed work item X.hbomsec

| field | value |
|---|---|
| Citation and URL | ITU-T SG17 (study period 2025), Contribution 548, *Proposal for a new work item on X.hbomsec: Guidelines for Minimum Hardware Bill of Materials Requirements to Enhance Hardware Supply Chain Security in ICT Products*, source Korea (Rep. of), <https://www.itu.int/md/T25-SG17-C-0548/en> |
| Version and date | Dated 2026-05-19, for the meeting of 2026-06-01, Question 4/17; posted 2026-05-21. |
| What was read | The document's metadata page only (SHA-256 `de8b8a6c78fd081fa431521d87ddda149cb718e731af35f650e18f09984e814e`); the contribution is "Restricted to TIES users". Whether SG17 accepted the work item was not found (the work programme page fetched lists 20 items and is partial). |
| Library record | none (a stub at most). |

### 1.28 Sources only noted

- **CISA 2026 Minimum Elements for an SBOM** (stub record `cisa-2026-sbom-minimum`, agent 1's): used here only for "hardware" 0 hits and one "firmware" mention (1.1).
- **Institute for Security and Technology HBOM effort:** a news snippet only; no primary source found (section 9).

## 2. Dimension questions answered

**Q1. What does an HBOM record that an SBOM cannot?** In the CISA framework, mostly supply-chain facts: entity names, the locations of the OEM headquarters, the main and alternate manufacturing sites, the component fab and the semiconductor assembly-and-test site (15 fields with place names, coordinates and ISO 3166 codes), sourcing share, lead times, quantities, technology node, part codes and sizes, and date codes (1.1). It records product and part types, not units: it has no serial number. It has no firmware field beyond a version string that mixes hardware, software and firmware versions, and no digest. CERT-In adds unit serial numbers, manufacturing date, test results, compliance marks, power data and licence information (1.24). Attestation sources add what a bill cannot: what the device itself reports, signed (1.15, 1.16, 1.19).

**Q2. Which formats can carry it, and how much of the framework maps onto them?** The v0.1.0 counts are confirmed: of 47 fields, 37 list no CycloneDX equivalent and 36 no SPDX equivalent (1.1). That count is CISA's own 2023 mapping, made against CycloneDX 1.5-era fields and SPDX 2.2 clause numbers. Our per-field reading against current schemas (section 3.3): CycloneDX 1.7.2 has a native field for 24 fields (9 `=`, 15 `≈`) and needs properties for 23; SPDX 3.0.1 has 19 (7 `=`, 12 `≈`) and needs extensions for 28. What comes next changes this: CycloneDX 2.0 (unreleased; hardware support merged into the 2.0-dev branch on 2026-08-20, labelled "tc54 accepted") covers 40 (29 `=`, 11 `≈`), and SPDX 3.1 (pre-release RC1 of 2026-01-24, with Hardware and SupplyChain profiles) 38 (20 `=`, 18 `≈`) (1.3, 1.5). No hardware field was added to CycloneDX 1.7.1, 1.7.2 or the `cdx:device` taxonomy after the v0.1.0 report (1.2). SWID and CoSWID carry no hardware (1.22), and uSWID turns a CycloneDX `device` into `firmware` on import (1.7).

**Q3. How is firmware tied to its device?** Seven different ways, from weakest to strongest (our ordering):
- by prose only: the CISA framework (1.1);
- by containment with a SHOULD: CycloneDX's `device` description, nested `firmware` component (1.2); SPDX 3.0.1 only by a generic `contains` (1.4);
- by a typed relation: SPDX 3.1's `runsOn` (1.5), Redfish's `SoftwareInventory.RelatedItem` (1.17), CoRIM's reference and CoSWID triples (1.18), SUIT's vendor, class and device ID conditions, which are compatibility checks, not identity (1.20);
- by construction: an SBOM embedded in the firmware image (`.sbom` section, uSWID header, coreboot CBFS), with the UEFI ESRT GUID as tag id by convention (1.6, 1.7, 1.9);
- by a signed report from the device: SPDM measurements signed with the device's hardware identity key (1.16), EAT `measurements` and `submods` in a signed token (1.19);
- by key derivation: DICE, where the firmware measurement feeds the key that signs the next certificate (1.15).

**Q4. Can it name the parts issue #8 lists?** *Buses:* only Redfish has first-class interconnect resources (`PCIeDevice`, `PCIeFunction` with bus, device and function numbers, `Port`, `PCIeSlots`, cables) (1.17); TCG has controller classes and derives component IDs from PCIe configuration space, but records no topology (1.14); CycloneDX (1.7 and 2.0-dev), SPDX (3.0.1 and 3.1-dev), the CISA framework and CERT-In have no bus or interconnect relation. *Compute cores:* Redfish `ProcessorType` `Core` and `Thread`, with `SubProcessors` (1.17); TCG and CycloneDX 2.0 classify processors (CPU, GPU, SoC; classification codes) but not cores (1.14, 1.3); CycloneDX `device` and SPDX `device` cover "processor" only as a broader type (1.2, 1.4). *Firmware components:* every format can name them (CycloneDX `firmware`, SPDX `firmware` purpose, TCG Firmware classes, Redfish `SoftwareInventory`, CoSWID tags inside firmware).

**Q5. Firmware bills in practice.** The open firmware ecosystem uses CoSWID in CBOR, embedded in the image: in the PE `.sbom` COFF section, behind the uSWID magic header, or as a uSWID file in coreboot's CBFS (1.6, 1.7, 1.9). The Firmware Embedded SBOM Specification 0.10 (prerelease, 2024) requires a GUID tag id, name, version, tag-creator and software-creator entities, and for built binaries a source-file hash and a source-tree hash, which it stores in CoSWID's `colloquial-version` and `edition`, fields RFC 9393 defines differently (1.6). LVFS scans every upload for these and exports SPDX, SWID and CycloneDX (1.8; 1.6 §7.6); uswid exports CycloneDX 1.6 and SPDX 2.3 (1.7). coreboot's SBOM is opt-in, and its templates name coreboot as tag creator even for Intel blobs (1.9). The UEFI Forum's sub-team proposed this approach in 2023 and a 2024 Plugfest deck asks vendors for firmware SBOMs in SWID, SPDX or CycloneDX (1.10). Embedded Linux and RTOS builds emit SPDX: OpenEmbedded-Core by default, SPDX 3.0.1 on master (1.11); Zephyr SPDX 2.3 by default, with 3.0 and 3.1 options on main only (1.12). In all of these the hardware appears at most as a build input (`MACHINE`, `BOARD`, target processor), never as a hardware element.

**Q6. Device identity and attestation as measured bills.**

| Source (version, status) | Component facts recorded | Signed or measured |
|---|---|---|
| TCG Platform Certificate Profile 2.1 (published 2026-01-27) (1.13) | platform manufacturer, model, version, serial; per component class (registry code), manufacturer, model, serial, revision, part numbers, MAC addresses, field-replaceability, country of origin, entity locations; Delta status | signed by the issuer (manufacturer or later supply-chain party); an Endorsement, not a measurement |
| TCG Component Class Registry 1.0 r14 (2023-05-31), PCIe r18 (1.14) | 87 class codes in 13 categories; PCIe rules fill IDs from configuration-space registers | codes are static; PCIe values can be read from the device to compare |
| TCG DICE Attestation Architecture 1.2 (2025-04-24; errata 2026-01-29) (1.15) | vendor, model, version, SVN, layer, index, firmware digests, operational flags, UEID; optional CoSWID evidence | measured by the previous layer and signed in an X.509 certificate whose key derives from the measurement |
| DMTF SPDM 1.4.1 (published 2026-06-26) (1.16) | measurements of immutable ROM, mutable firmware, hardware and firmware configuration, firmware version and SVN, device mode, manifests; manufacturer, product and serial in the certificate | measured by the device and signed with its hardware-identity key |
| DMTF Redfish 2026.2 (2026-09-16) (1.17) | full hardware inventory (processors and cores, memory, PCIe devices and functions, chassis, assemblies with part, serial, production date and country of origin), firmware inventory bound to devices, integrity measurements | reported by the management service; signed SPDM measurements only through the `SPDMGetSignedMeasurements` action |
| IETF CoRIM draft-11 (in WG Last Call, 2026-07-06) (1.18) | reference values per environment (class, instance, group): version, SVN, digests, serial number, UEID, MAC and IP addresses; domain membership and trust dependency graphs; links to CoSWID tags | signed by the CoRIM creator (COSE_Sign1); reference values, not evidence |
| IETF EAT, RFC 9711 (April 2025) (1.19) | UEID, OEM ID, hardware model and version, software name and version, manufacturer manifests, on-device measurements, nested submodules | signed token (CWT or JWT) from the attester; measurements are made on the entity |
| IETF SUIT manifest draft-37 (RFC Editor queue) (1.20) | firmware component IDs, image digests and sizes, vendor, class and device UUIDs, human-readable vendor and model text | signed by the author; identifiers are compatibility checks, not identity |

So the attestation standards do record what a device contains, but each records a different slice: TCG and Redfish list hardware parts; DICE, SPDM and EAT measure firmware and report it signed; CoRIM and the platform certificate hold the supplier's signed expectations. None of them records supply-chain origin except TCG 2.1 (country of origin, entity locations) and Redfish (country of origin of an assembly).

**Q7. ISO/IEC 19770-6:2024.** Read: ISO metadata (scope, 41 pages, stage 60.60, life-cycle dates) and BSI's 8-page public preview (contents list, foreword, part of the introduction). Not read: every clause that defines fields. From the contents list: primary and system HWID types, a clause on systems of systems, signatures in XML and JSON, and the data definitions `HWID`, `HWIDMeta`, `Entity`, `Link`, `LinkContent`, `Meta`, `OrderInfo` and `Location` (1.23). Which fields these contain, which are required, and whether any tool emits HWID tags is unknown.

**Q8. Hierarchical systems.** Mechanisms found: CycloneDX nested `components` and `compositions[].assemblies` (1.2), CycloneDX 2.0 `boardLocation` (1.3); SPDX `contains` and SPDX 3.1's assembly processes (1.4, 1.5); the CISA framework's one-HBOM-per-assembly nesting (1.1); CERT-In's recursive sub-component element (1.24); Redfish `Chassis.Links.Contains` and `ContainedBy`, `Assembly`, `SubProcessors`, `PartLocation` (1.17); TCG's flat component list, with a component's own platform certificate referenced through `componentPlatformCert` and Delta certificates for later changes (1.13); CoRIM's acyclic domain membership and trust dependency graphs (1.18); EAT `submods` (1.19); RFC 9334's composite device (1.21); ISO 19770-6's system HWIDs and "Systems of systems" (contents list only, 1.23). Vehicles: no public vehicle or ECU HBOM guidance was found. Auto-ISAC's report is about software SBOMs across supplier tiers and recommends SPDX or CycloneDX JSON (1.25); UN R155 does not mention SBOMs, and R156 requires unique identification of the hardware and software of type-approved systems and an RXSWIN register, without a format (1.26). Vehicle software identification (RXSWIN, ISO 24089) is agent 2's.

**Q9. Guidance beyond CISA.** CERT-In v2.0 (2025-07-09) is the only national guidance found with an HBOM element list (Table 11); it defines no format and points to "extended SBOM formats like CycloneDX or custom XML/JSON schemas" (1.24). Korea proposed an ITU-T work item, X.hbomsec, on minimum HBOM requirements (SG17 C-548, 2026-05-19; text restricted) (1.27). ISO/IEC 19770-6 is the international tag standard (1.23). CISA has not updated its framework since September 2023 (1.1).

## 3. Table 4: hardware and firmware coverage

Rows and the first columns are those of `dimensions.md`. The ISO/IEC 19770-6 column is omitted, because no copy could be read (1.23). Columns added for sources verified in section 1; the two pre-release columns are marked as such. The table is split in two for width: 4a for bills and guidance, 4b for identity and attestation standards. Cells name the field; "(ext)" cells name the extension mechanism.

### 3.1 Table 4a: bills and guidance

| Hardware fact | CISA HBOM framework (2023) | CycloneDX 1.7.2 | SPDX 3.0.1 | CycloneDX 2.0-dev (unreleased) | SPDX 3.1-dev (pre-release) | CoSWID / uSWID firmware SBOM (spec 0.10, uswid 0.6.0) | CERT-In v2.0, Table 11 |
|---|---|---|---|---|---|---|---|
| Device or part identity | `≈` `COMP_MANUFACTURER_PN`, `COMP_SUPPLIER_PN`, `COMP_HASH` (an "intrinsic identifier", UUID example), `FGA_NUM`; free strings, no scheme | `≈` component `type: device`, `name`, `version`; GS1 keys only as `cdx:device:gs1:*` properties | `≈` Package with `software_primaryPurpose: device`; `externalIdentifier` has no hardware type | `=` `identifiers[]`, party-attributed (`mpn`, `part-number`, `model-number`, `sku`, GS1, `udi-di`, `fcc-id`) | `=` `Hardware` subclasses with required `partNumber`, `category` | `ext` CDDL extension sockets only; tags identify software (`tag-id` GUID) | `≈` Product Name, Model Number, Product Version |
| Manufacturer and part number | `=` `COMP_MANUFACTURER`, `COMP_MANUFACTURER_PN`, `FGA_MAIN_MANUFACTURER` | `≈` `manufacturer` (organization); part number only in `name`, as CISA maps it | `≈` `originatedBy` or `suppliedBy`; part number only in `name` or `externalIdentifier` (type `other`) | `=` `parties` (role `manufacturer`, `role.order`) and scheme `mpn` | `=` `productAgent` (OEM) and `partNumber` | `ext`; entities name firmware creators and distributors (`regid`) | `≈` Manufacturer Name, Model Number |
| Firmware bound to its device | `txt` §1.3 ("the provider of the firmware"); no field | `≈` `device` description: separate `firmware` component, SHOULD; linked only by nesting | `≈` generic `contains`; no rule | `≈` same `device` rule (unchanged) | `=` `runsOn` (instructions to `Hardware`), `hasInstall` | `≈` SBOM embedded in the image (`.sbom` section, uSWID header, CBFS); `tag-id` usually the ESRT GUID | `txt` §10.4.1.4 lists "firmware version"; no element |
| Firmware version and digest | `≈` `COMP_VERSION`, `FGA_VERSION` (hardware, software or firmware version in one string); no digest | `=` firmware component `version`, `hashes` | `=` firmware Package `packageVersion`, `verifiedUsing` | `=` same as 1.7 | `=` same as 3.0.1 | `=` `software-version`; payload `hash`; `colloquial-version` and `edition` reused as source-file and source-tree hashes | `txt` §10.4.1.4 "firmware version"; no digest |
| Bus or interconnect | `none` (free-text `COMP_PART_TYPE` only) | `ext` `cdx:device:function` ("network, storage, microprocessor, connector"); no relation | `ext` Extension | `ext`; `classification` can label a bus part; no relation | `ext`; `category` only; no relation | `ext` | `none` |
| Compute core or processor | `none` (free-text `COMP_PART_TYPE`; `TECHNOLOGY_NODE`) | `⊃` `device` ("a processor or chip-set"); no core | `⊃` purpose `device` ("chipset, processor, or electronic board") | `≈` `device` with `classification` (for example `microcontroller`) and taxonomy `codes` | `≈` `Hardware` with `category`; `runsOn` calls the target a "processing element" | `ext` (microcode is a software tag) | `none` (Technology Node, Technical Specification) |
| Board and assembly hierarchy | `≈` B.1.1 nesting: one HBOM per assembly, joined by part-level information | `=` nested `components`, `compositions[].assemblies`; board position `cdx:device:location` (ext) | `≈` `contains`, `hasOptionalComponent`, `completeness` | `=` nested `components`, `boardLocation` (designators, layer, subsystem), `quantity` | `≈` `contains`; SupplyChain `AssemblyProcess` and `AssemblyAction` | `ext` for hardware; a "platform SBOM" combines the firmware SBOMs of one device | `≈` Sub-component ("recursive nature of an HBOM") |
| Serial number (one unit) | `none` (no serial field) | `ext` `cdx:device:serialNumber` | `ext` Extension | `=` scheme `serial-number` | `=` `serialNumber` | `≈` evidence `device-id` (endpoint of collected evidence, RFC 9393) | `=` Serial Number ("each individual unit") |
| Supply-chain origin (country, site) | `=` 15 Entity Location fields (place, coordinates, ISO 3166 codes for OEM, main and alternate sites, fab, assembly and test), `SUPPLIER_SOURCED_PCTG` | `≈` `manufacturer.address`, `supplier.address` (`country`, `region`, `locality`); no coordinates, no stage | `ext` Extension (no address field) | `=` `origins[]` (stage, basis, ISO 3166 distribution, `performedBy`); party `addresses` with `isoCode`, `coordinates` | `≈` `PhysicalLocation` (alpha-3 country, ISO 6709 point), `locatedAt`, `headquartersLocation`, `actionLocation` | `ext` | `≈` Manufacturer Location, Supplier Location; "origin" in §10.4.1.4 |
| Lot or date code | `=` `COMP_DATECODE` ("timestamp/lot date code/lot number") | `ext` `cdx:device:lotNumber`, `cdx:device:prodTimestamp` | `ext` Extension | `ext` (no field; `udi-pi` scheme for medical devices) | `≈` `batchNumber` (lot only) | `ext` | `≈` Manufacturing Date (no lot) |
| Measured identity | `none` | `ext` only a link: `externalReferences` type `attestation` | `ext` Extension | `ext`; adds inspection evidence (`x-ray-inspection`, `decapsulation`), not device-reported | `ext` | `ext`; a runtime ACPI SBOM table is future work (§7.3) | `none` (audits in prose, §10.4.2.4) |

### 3.2 Table 4b: identity and attestation standards

| Hardware fact | TCG Platform Certificate Profile 2.1 (with Component Class Registry r14, PCIe r18) | TCG DICE Attestation Architecture 1.2 | DMTF SPDM 1.4.1 | DMTF Redfish 2026.2 | IETF CoRIM draft-11 | IETF EAT (RFC 9711) | IETF SUIT manifest draft-37 |
|---|---|---|---|---|---|---|---|
| Device or part identity | `=` `ComponentIdentifier-v2` traits: class (registry and 4-byte value), manufacturer, model (all SHALL); platform manufacturer, model, version | `≈` `DiceTcbInfo` `vendor`, `model`, `type`, `layer`, `index` describe the measured environment | `≈` hardware-identity certificate; `DMTFOtherName` "manufacturer:product:serialNumber" | `=` `Manufacturer`, `Model`, `PartNumber`, `SKU`, `SerialNumber`, `UUID` on hardware resources and `AssemblyData` | `=` `environment-map` (`class-id`, `vendor`, `model`; `instance`; `group`) | `=` `ueid`, `oemid`, `hwmodel`, `hwversion` | `≈` vendor and class identifiers (UUIDs); "MUST NOT be used as assertions of identity" |
| Manufacturer and part number | `=` manufacturer trait (PEN in the V11 form) and `componentPartNumber` trait category (new in 2.1) | `≈` `vendor`, `model` | `≈` manufacturer and product strings in `otherName`; no part number | `=` `Manufacturer`, `PartNumber`, `SparePartNumber`; `AssemblyData.Producer`, `Vendor` | `≈` `vendor`, `model` | `≈` `oemid` and opaque `hwmodel` | `txt` `suit-text-vendor-name`, `suit-text-model-name` |
| Firmware bound to its device | `≈` Firmware class components (System firmware, Bootloader, NIC firmware) listed beside hardware; no firmware-to-device relation | `=` TCB info in the certificate whose key derives from the measured firmware | `=` measurements reported and signed by the device's own responder (0x0, 0x1) | `=` `SoftwareInventory.RelatedItem`; `FirmwareVersion` on hardware resources | `=` reference triples (environment to measurements); CoSWID triples | `=` `swname`, `swversion`, `manifests`, `measurements` in the entity's token or a submodule | `=` images bound to devices through vendor, class and device ID conditions |
| Firmware version and digest | `≈` `componentRevision` (string); digests only via `platformConfigUri` | `=` `version`, `svn`, `fwids` (`hashAlg`, `digest`) | `=` types 0x6 (version), 0x7 (SVN), 0x1 (digest) | `=` `SoftwareInventory.Version`, `SoftwareId`, `ReleaseDate`; digests in `ComponentIntegrity` | `=` `version`, `svn`, `digests` | `=` `swversion`; evidence CoSWID in `measurements` | `=` `suit-parameter-image-digest`, `-image-size`; `suit-text-component-version` |
| Bus or interconnect | `≈` controller classes (USB, SATA, SAS, Ethernet); PCIe registry IDs; MAC addresses; no topology | `ext` | `ext` (runs over MCTP and other transports; does not describe them) | `=` `PCIeDevice` (`PCIeInterface`), `PCIeFunction` (bus, device, function numbers), `Port`, `PCIeSlots`, chassis cables | `ext` (`mac-addr`, `ip-addr` are values) | `ext` | `ext` |
| Compute core or processor | `≈` Microprocessor classes (CPU, GPU, DSP, DPU, SoC and others); no core class | `ext` | `ext` | `=` `Processor` with `ProcessorType` (`Core`, `Thread` included), `SubProcessors`, `TotalCores` | `ext` | `ext` | `ext` |
| Board and assembly hierarchy | `≈` flat component list; container and board classes; `componentPlatformCert` points to a component's own certificate; location trait category | `ext` (layers are boot stages) | `ext` (manifests index one device's measurements) | `=` `Chassis.Links.Contains`, `ContainedBy`; `Assembly`; `PartLocation` | `≈` domain membership triples (acyclic), trust dependency triples | `≈` nested `submods` | `ext` |
| Serial number (one unit) | `=` serial trait (SHOULD; SHALL in the V11 trait); Platform Serial Number | `≈` UEID extension (`TcgUeid`) | `≈` serial number in `otherName` | `=` `SerialNumber` | `=` `serial-number`, `ueid`, `uuid` | `≈` `ueid` ("akin to a serial number") | `≈` `suit-parameter-device-identifier` (UUID) |
| Supply-chain origin (country, site) | `=` `countryOfOriginTrait`, `entityGeoLocationTrait`, `manufacturingAssertions` (new in 2.1) | `ext` | `ext` | `≈` `AssemblyData.ISOCountryCodeOfOrigin` (country only); `Location` is the installed position | `ext` | `ext` (`location` is the current position) | `ext` |
| Lot or date code | `ext` (no trait; issuers may add traits) | `ext` | `ext` | `≈` `AssemblyData.ProductionDate`, `EngineeringChangeLevel`; no lot | `ext` | `ext` | `ext` |
| Measured identity | `≈` a signed manufacturer Endorsement bound to the roots of trust; registries say how a verifier reads the same values; not device-reported | `=` `DiceTcbInfo`: evidence measured by the attesting layer, in a signed certificate | `=` signed `MEASUREMENTS` (0x2 hardware configuration, 0x5 device mode) | `≈` `ComponentIntegrity` measurements relayed by the service; signed only via `SPDMGetSignedMeasurements` | `≈` signed reference values and endorsements for appraising evidence; not the device's report | `=` the signed token; `measurements` made on the entity | `ext` (authored manifest) |

### 3.3 Supporting crosswalk: the 47 CISA fields against current formats (our reading)

CISA's columns are copied from Appendix C. The four right-hand columns are our reading of the pinned schemas (sections 1.2 to 1.5): `=` a field of the same meaning, `≈` a field that loses something, `ext` only through properties or extensions. Counts: CycloneDX 1.7.2 9 `=`, 15 `≈`, 23 `ext`; CycloneDX 2.0-dev 29 `=`, 11 `≈`, 7 `ext`; SPDX 3.0.1 7 `=`, 12 `≈`, 28 `ext`; SPDX 3.1-dev 20 `=`, 18 `≈`, 9 `ext`. The pre-release columns may change before release.

| § | Field | CISA: CycloneDX | CISA: SPDX | CycloneDX 1.7.2 | CycloneDX 2.0-dev | SPDX 3.0.1 | SPDX 3.1-dev |
|---|---|---|---|---|---|---|---|
| C.1.1 | `HBOM_STD_VERSION` | None, do not map | None, do not map | ext metadata.properties | ext metadata.properties | ext Extension | ext Extension |
| C.1.2 | `HBOM_CREATION_DATE` | None | None | = metadata.timestamp | = metadata.timestamp | = CreationInfo.created | = CreationInfo.created |
| C.1.3 | `HBOM_MODIFY_DATE` | metadata/timestamp | (2.9) Created: | ≈ metadata.timestamp of a new BOM version | ≈ same | ≈ created of a new version | ≈ same |
| C.1.4 | `HBOM_AUTHOR` | metadata/authors/author | (2.8) Creator: | = metadata.authors | = metadata.authors | = CreationInfo.createdBy | = CreationInfo.createdBy |
| C.1.5 | `FGA_SUPPLIER` | None | None | ≈ metadata.supplier | ≈ parties (role supplier or manufacturer) | ≈ suppliedBy | = productAgent |
| C.1.6 | `FGA_NUM` | name | (3.1) PackageName: | ≈ name | = identifiers (scheme model-number or mpn) | ≈ name or externalIdentifier (other) | = partNumber |
| C.1.7 | `FGA_DESCRIPTION` | None | None | = description | = description | = description | = description |
| C.2.1 | `FGA_TYPE` | None | None | ≈ type (device) and services[] | = type (device, material, service, software types) | ≈ software_primaryPurpose (device) | = element class (Hardware, software Package, Service) |
| C.2.2 | `FGA_VERSION` | version | (3.3) PackageVersion: | = version | = version | = packageVersion | = version |
| C.3.1 | `FGA_HASH` | Hash “alg” | (3.10) PackageChecksum: (3.9) PackageVerificationCode: | ≈ hashes (content digest) | ≈ identifiers (custom scheme) or hashes | ≈ verifiedUsing | ≈ verifiedUsing |
| C.3.2 | `FGA_MAIN_MANUFACTURER` | Supplier publisher | (3.5) PackageSupplier: | = manufacturer | = parties (role manufacturer) | ≈ originatedBy | ≈ ManufactureAction with performedBy |
| C.3.3 | `FGA_ALT_MANUFACTURER` | None | None | ext properties | = parties (role manufacturer, role.order 2) | ext Extension | ext Extension |
| C.3.4 | `COMP_SUPPLIER` | None | None | = components[].supplier | = parties (role supplier) | = suppliedBy | ≈ supply-chain actions (Hardware forbids suppliedBy) |
| C.3.5 | `COMP_MANUFACTURER` | Supplier publisher | (3.5) PackageSupplier: | = components[].manufacturer | = parties (role manufacturer) | ≈ originatedBy | ≈ productAgent or ManufactureAction |
| C.4.1 | `ASSY_AND_TEST_SUPPLIER` | None | None | ext properties | = origins (stage assembled or tested, performedBy) | ext Extension | ≈ AssemblyAction or TestAction with performedBy |
| C.4.2 | `FGA_SUPPLIER_LOC` | None | None | ≈ supplier.address | = organization.addresses | ext Extension | = Organization.headquartersLocation |
| C.4.3 | `FGA_LOC_COORDS` | None | None | ext properties | = postalAddress.coordinates | ext Extension | = PhysicalLocation.geographicPointLocation |
| C.4.4 | `FGA_LOC_CODE` | None | None | ≈ address.country (region is free text) | = postalAddress.isoCode | ext Extension | ≈ country (alpha-3) and provinceStateCode |
| C.4.5 | `FGA_MAIN_LOCATION` | None | None | ≈ manufacturer.address | = origins (stage manufactured or assembled) | ext Extension | = ManufactureAction actionLocation |
| C.4.6 | `FGA_MAIN_LOC_COORDS` | None | None | ext properties | ≈ performing party address coordinates | ext Extension | = actionLocation geographicPointLocation |
| C.4.7 | `FGA_MAIN_LOC_CODE` | None | None | ≈ manufacturer.address.country | = origins distribution isoCode | ext Extension | ≈ country and provinceStateCode |
| C.4.8 | `FGA_ALT_LOCATION` | None | None | ext properties | ≈ second manufacturer party address | ext Extension | ext Extension |
| C.4.9 | `FGA_ALT_LOC_COORDS` | None | None | ext properties | ≈ second manufacturer party address coordinates | ext Extension | ext Extension |
| C.4.10 | `FGA_ALT_LOC_CODE` | None | None | ext properties | ≈ second manufacturer party address isoCode | ext Extension | ext Extension |
| C.4.11 | `COMP_MFG_LOCATION` | None | None | ≈ components[].manufacturer.address | = origins (stage manufactured) | ext Extension | = ManufactureAction actionLocation |
| C.4.12 | `COMP_MFG_LOC_COORDS` | None | None | ext properties | ≈ performing party address coordinates | ext Extension | = actionLocation geographicPointLocation |
| C.4.13 | `COMP_MFG_LOC_CODE` | None | None | ≈ manufacturer.address.country | = origins distribution isoCode | ext Extension | ≈ country and provinceStateCode |
| C.4.14 | `ASSY_AND_TEST_LOCATION` | None | None | ext properties | = origins (stage assembled or tested) | ext Extension | = AssemblyAction or TestAction actionLocation |
| C.4.15 | `ASSY_AND_TEST_LOC_COORDS` | None | None | ext properties | ≈ performing party address coordinates | ext Extension | = actionLocation geographicPointLocation |
| C.5.1 | `ASSY_AND_TEST_LOC_CODE` | None | None | ext properties | = origins distribution isoCode | ext Extension | ≈ country and provinceStateCode |
| C.5.2 | `COMP_SUPPLIER_PN` | None | (2.5) SPDX Document Namespace (3.2) SPDXID: | ext cdx:device:sku | = identifiers (scheme part-number or sku) | ≈ externalIdentifier (other) | ≈ partNumber is the OEM number |
| C.5.3 | `COMP_MANUFACTURER_PN` | name | (3.1) PackageName: | ≈ name | = identifiers (scheme mpn) | ≈ name or externalIdentifier (other) | = partNumber |
| C.5.4 | `COMP_DESCRIPTION` | None | None | = description | = description | = description | = description |
| C.5.5 | `COMP_TYPE` | None | None | ≈ type | = type | ≈ software_primaryPurpose | = element class |
| C.5.6 | `COMP_PART_TYPE` | None | None | ext cdx:device:function | = classification.category | ext Extension | = category (DefinedType) |
| C.5.7 | `COMP_PART_CODE` | None | None | ext properties | = classification.codes[] (standard, value) | ext Extension | ≈ category (DefinedType) or externalIdentifier hsCodes |
| C.5.8 | `COMP_HASH` | Hash “alg” | (3.10) PackageChecksum: (3.9) PackageVerificationCode: | ≈ hashes (content digest) | ≈ identifiers (custom scheme) or hashes | ≈ verifiedUsing | ≈ verifiedUsing |
| C.6.1 | `COMP_OPT_NAME` | None | None | ext properties | ext properties | ext Extension | ext additionalInformation |
| C.6.2 | `COMP_VERSION` | version | (3.3) PackageVersion: | = version | = version | = packageVersion | = version |
| C.7.1 | `COMP_DATASHEET` | None | None | ≈ externalReferences (type documentation) | ≈ externalReferences (type documentation) | ≈ externalRef (type documentation) | ≈ additionalInformationSpecification |
| C.7.2 | `SUPPLIER_SOURCED_PCTG` | None | None | ext properties | ext properties | ext Extension | ext Extension |
| C.7.3 | `LEADTIMES` | None | None | ext properties | = leadTime | ext Extension | ext Extension |
| C.7.4 | `QUANTITY` | None | None | ext cdx:device:quantity | = quantity | ext Extension | ≈ bulkQuantity (BulkHardware only) |
| C.7.5 | `TECHNOLOGY_NODE` | None | None | ext properties | ext properties | ext Extension | ext additionalInformation |
| C.7.6 | `COMP_PART_SIZE_VAL` | None | None | ext properties | ext properties | ext Extension | ≈ dimensions, massOfHardware |
| C.7.7 | `COMP_PART_SIZE_UNIT` | None | None | ext properties | ext properties | ext Extension | ≈ UnitOfMeasure |
| C.7.8 | `COMP_DATECODE` | None | None | ext cdx:device:lotNumber, cdx:device:prodTimestamp | ext properties; identifiers scheme udi-pi (medical devices) | ext Extension | ≈ batchNumber (lot only) |

## 4. Table 7 ratings

0 = absent, 1 = mentioned or weak, 2 = partial, 3 = strong; within each source's own scope. Where RPT-0005 rated the same format, its rating is reused unless the hardware part differs.

| Source | Object model | Provenance/attribution | Human review/audit | Federation | AI-grounding |
|---|---|---|---|---|---|
| CISA HBOM framework (1.1) | 2: parts map to Component, makers and suppliers to Party, nesting to `composed_of` (B.1.1); locations, sourcing and lead times have no ARCH-0001 home | 1: author and dates for the whole HBOM only (C.1.2 to C.1.4) | 0: no review field | 1: no identifier scheme; Appendix D names part and entity resolution as unsolved | 2: stable field names and C.x.y numbers with descriptions; PDF only, no schema |
| CycloneDX 1.7.2, hardware (1.2) | 2: `device` = Component (chip), nesting = `composed_of`, `manufacturer`/`supplier` = Party edges; hardware details only as properties | 2: BOM authors and timestamp; `citations[]` (RPT-0005) | 2: annotations, declarations (RPT-0005) | 2: `bom-ref` local; serial number and BOM-Link (RPT-0005) | 1: property names are stable strings but unvalidated |
| CycloneDX 2.0-dev, hardware (1.3) | 2: device, material, parties with roles, origins, identifiers; no interconnect or core | 2: identifiers and origins attributed to a party (`party`, `performedBy`) | 2: physical inspection evidence; certifications linked to attestation claims; no verdict | 2: party LEI/DUNS/CAGE, GS1 keys; `bom-ref` still local | 1: unreleased, moving branch |
| CycloneDX `cdx:device` taxonomy (1.2) | 1: flat property names | 0: none | 0: none | 2: registered namespace names | 2: one-line definitions at stable names |
| SPDX 3.0.1, hardware (1.4) | 1: `device` is a purpose label; no hardware fields | 3: `creationInfo` on every element (RPT-0005) | 2: `Annotation` of type review (RPT-0005) | 3: `spdxId` IRIs (RPT-0005) | 2: (RPT-0005) |
| SPDX 3.1-dev Hardware and SupplyChain (1.5) | 2: `Hardware` classes, `runsOn`, locations, supply-chain actions; no interconnect | 3: inherits `creationInfo`; actions with `performedBy` | 2: as 3.0.1, plus `InspectionAction` | 3: `spdxId`; `duns`, `gln`, `gtin`, `lei` identifiers | 1: pre-release text on a moving branch |
| Firmware Embedded SBOM Spec 0.10 (1.6) | 1: firmware components and vendors only | 2: tag-creator and software-creator entities per tag | 0: validation by tool only | 2: GUID tag ids, DNS `regid`, LVFS as neutral store | 1: prerelease 0.10 with section numbers; a known error ("DTMF") |
| python-uswid 0.6.0 (1.7) | 1: three software types; `device` becomes `firmware` | 2: entities with roles, evidence date | 0 | 2: converts CoSWID, CycloneDX 1.6, SPDX 2.3 | 1: tool documentation |
| LVFS (1.8) | 1: scans and exports firmware SBOMs | 1: vendor accounts (not inspected) | 1: test waivers recorded (release notes), not for SBOM data | 2: one public service across vendors | 1: undated pages |
| coreboot SBOM (1.9) | 1: CoSWID templates per firmware part | 1: tag creator is coreboot even for third-party blobs | 0 | 2: UUID `tag-id`, `persistent-id` | 1: documentation only |
| UEFI Forum material (1.10) | 1: proposal and slides | 1: named authors | 0 | 1 | 1: blog and deck |
| OpenEmbedded-Core SPDX output (1.11) | 1: software packages and builds; machine only as a name | 3: SPDX `creationInfo` | 1: none specific | 3: `spdxId` | 1: tool output |
| Zephyr `west spdx` (1.12) | 1: software; board as a build parameter | 2: SPDX creation info | 0 | 2: SPDX ids | 1: tool output |
| TCG Platform Certificate Profile 2.1 (1.13) | 2: components ≈ Component, platform ≈ ProductInstance (serial), manufacturer = Party, Delta = lifecycle change; flat list | 3: every certificate signed by a named issuer with a validity period; chain of custody (§2.1.3) | 1: verifier policy decides trust; no human record | 3: X.509, OIDs, registries, PEN | 2: public and versioned; ASN.1 defects; restrictive licence |
| TCG Component Class Registry r14, PCIe r18 (1.14) | 2: a class vocabulary for Component kinds; no bus or core class | 1: registry versions only | 0 | 3: registered 4-byte codes per registry OID; PCIe values read from devices | 3: stable codes with one-line definitions |
| TCG DICE Attestation Architecture 1.2 (1.15) | 1: measured layers ≈ firmware Components | 3: each measurement signed by the previous layer | 0 | 2: X.509, OIDs, UEID | 2: public; needs the errata for the ASN.1 |
| DMTF SPDM 1.4.1 (1.16) | 1: per-device measurements and identity, not composition | 3: signed measurement transcripts, certificate chains | 0 | 2: X.509 chains, DMTF OIDs, vendor registries | 2: public, versioned, numbered paragraphs |
| DMTF Redfish 2026.2 (1.17) | 3: Chassis, Assembly, Processor (cores), Memory, PCIe, Port, SoftwareInventory map onto Component, `composed_of`, interconnect and firmware | 1: values reported by a service; `LastUpdated` on ComponentIntegrity | 0 | 2: `@odata.id` is local to a service; UUIDs and serials global | 3: versioned JSON Schemas with a normative `longDescription` per property at stable URLs |
| IETF CoRIM draft-11 (1.18) | 2: environments ≈ Component and ProductInstance; domain membership = `composed_of`; trust dependency ≈ `depends_on` | 3: COSE_Sign1 by the creator; `authorized-by` per measurement | 1: appraisal by verifier, no human record | 3: OIDs, UUIDs, UEIDs, CoSWID tag ids, IANA registries | 2: Internet-Draft in WG Last Call |
| IETF EAT, RFC 9711 (1.19) | 2: entity identity, submodules ≈ `composed_of`, manifests and measurements | 3: signed token, `iat`, nonce | 0 | 3: UEID global, IANA claim registry | 3: RFC with CDDL |
| IETF SUIT manifest draft-37 (1.20) | 1: firmware components and device classes | 3: signed manifest | 0 | 2: UUID5-derived vendor and class IDs | 2: in the RFC Editor queue |
| RFC 9334 (1.21) | 1: roles and the composite device | 1 | 0 | 1 | 3: RFC |
| ISO/IEC 19770-6:2024 (1.23) | not rated: text not read | not rated | not rated | not rated | 1: stable reference, paywalled text |
| CERT-In v2.0, HBOM part (1.24) | 2: elements map to Component (with sub-components) and Party; no format | 0: no author or time element for an HBOM | 1: audits and validation in prose (§10.4.1.12, §10.4.2.4) | 1: no identifier scheme | 2: numbered clauses in a dated public PDF |
| Auto-ISAC SBOM IR v3.0 (1.25) | 1: software SBOM practice; hardware in passing | 1 | 1: supplier and customer agreement steps (§6.8) | 1 | 2: numbered sections, TLP:CLEAR |
| UN R155 and R156, 2021 (1.26) | 1: R156 requires unique identification of hardware and software, no model | 1: documentation and registers | 2: type approval is an audit by an approval authority | 1 | 3: stable UN document numbers and paragraphs |
| ITU-T SG17 C-548 (1.27) | not rated: text restricted | not rated | not rated | not rated | 1: metadata page only |

## 5. Applicability to the tmodel model

The draft model today (ARCH-0001 §3; proposal `0.2.0-proposed.11` §0, §1, §2b, §3b; LinkML 0.1.0): `Component` is "service, container, dependency, chip, core" (proposal §0) with slots `composed_of`, `depends_on`, `uses_component`, `owned_by`; `manufactured_by` and `supplied_by` exist on `Product` only; `ProductInstance` has `of_product`, `current_phase`, `valid_from`, `valid_to`, `owned_by`; the proposal names Interconnect, Network and NetworkLink and a `connected_via` path (§1), which the LinkML draft does not define; R-022 names "hardware (firmware/buses/compute cores), and hierarchical systems". tradar has no hardware handling (v0.1.0 §4).

### 5.1 Candidate Table 6 rows (hardware), in Table 6's columns

| Model input | CycloneDX 1.7 | SPDX 3.0.1 | radar today | Fidelity | Rule (candidate) | Lost | Routes to |
|---|---|---|---|---|---|---|---|
| `Component` kind for hardware (proposal §0 "chip, core"; LinkML 0.1.0 `Component`, no kind slot) | `type: device`, `firmware` | `software_primaryPurpose: device`, `firmware` | none | `≈` (CycloneDX), `⊃` (SPDX) | keep the source type as a Component kind, and keep firmware as its own Component; take a class code when a registry gives one (TCG class, Redfish `ProcessorType`, CycloneDX 2.0 `classification`) | class detail; no slot for it | DEC-001, #17 |
| `composed_of` for boards and assemblies (proposal §3; LinkML 0.1.0 slot) | nested `components[]`; `compositions[].assemblies` | `contains` | none | `=` / `≈` | edge runs from the assembly to the part; reject cycles (CoRIM requires an acyclic domain graph, 1.18); Redfish `Contains` and EAT `submods` import the same way | board position, quantity (properties) | DEC-001, #17 |
| Firmware-to-device binding (gap: no draft edge; proposal `runs_on` is a DFD projection edge) | `device` with nested `firmware` | `contains` | none | `≈` | either reuse `composed_of` (device to firmware) or add a Component-to-Component `runs_on` as in SPDX 3.1; keep how the binding is known (declared, embedded, measured) as provenance | the binding's strength | DEC-001 |
| Component version and digest (gap: no LinkML slots) | `version`, `hashes` | `packageVersion`, `verifiedUsing` | Syft gives name and version; no hash (v0.1.0 §3) | `none` in the model | add version and digest attributes; a firmware digest pins a firmware build, not a unit | all of it today | DEC-001, DEC-002 |
| `manufactured_by`, `supplied_by` on Component (gap: only on Product in LinkML 0.1.0) | `manufacturer`, `supplier` | `originatedBy`, `suppliedBy` | none | `none` for Component | allow both edges on Component, ordered (CycloneDX 2.0 `role.order` keeps primary and alternate makers) | alternate makers, A&T supplier, fab | DEC-001 (R-036) |
| Component identifier set (gap row of `dimensions.md`) | `name`, `cpe`, `purl`; `cdx:device:*` properties | `externalIdentifier` | purl and CPE dropped by tradar (v0.1.0 §4) | `none` in the model | store (scheme, value, asserting party) triples as CycloneDX 2.0 `identifiers` do; hardware schemes: MPN, part number, serial, GTIN, PCIe IDs, UEID | scheme and asserter | DEC-001, DEC-002 |
| Physical unit identity (LinkML `ProductInstance`; proposal §3b "identity-by-hash") | `cdx:device:serialNumber` (ext) | none | none | `none` | separate build identity (firmware hash) from unit identity (serial number, UEID, device key): the proposal's example of a refurbished unit with "the same identity-by-hash `ProductInstance`" makes every unit running that build one instance (our reading) | unit identity | DEC-001, DEC-009 |
| Interconnect or bus (proposal §1 Interconnect, NetworkLink, `connected_via`; absent from LinkML 0.1.0) | none (ext `cdx:device:function`) | none | none | `none` | only Redfish gives first-class links (PCIe device and function, ports, slots, cables); TCG gives PCIe class codes without topology; import them as `connected_via` edges | everything in CycloneDX and SPDX | DEC-001, #17 |
| Processor and core (proposal §0) | `device` | `device` purpose | none | `⊃` | processor `composed_of` cores, as Redfish `SubProcessors` (`Core`, `Thread`) | cores | DEC-001 |
| Supply-chain origin (gap) | `manufacturer.address.country` | none | none | `none` in the model | an origin attribute on Component, or on the `manufactured_by` edge, with stage and basis (CycloneDX 2.0 `origins`; TCG 2.1 `countryOfOriginTrait`; Redfish `ISOCountryCodeOfOrigin`) | coordinates, stages, shares | DEC-001 (R-036; R-037 production phase) |
| Lot or date code (gap) | `cdx:device:lotNumber` (ext) | none | none | `none` | a production batch between Product and ProductInstance, or an attribute | lot | DEC-001 |
| Measured identity as `Assertion` (proposal §4; LinkML 0.1.0 `Assertion`) | none | none | none | `none` | import each signed measurement (SPDM, DICE, EAT) as an Assertion whose provenance is the signing key and time; import platform certificates and CoRIM as Assertions by the manufacturer Party (Endorsements); an appraisal is an automated Assertion until a human Review accepts it | signatures, unless kept | DEC-001, DEC-004 |
| Platform changes after manufacture (proposal §3b lifecycle and custody provenance, post-MVP) | none | none | none | `none` | a TCG Delta certificate (added, modified, removed, by integrator, VAR or owner) is custody evidence for a (ProductInstance, time) pair | none if kept | DEC-009, DEC-001 |
| Completeness of hardware composition (gap row) | `compositions[].aggregate` for `assemblies` | `completeness` on `contains` | none | `none` in the model | carry the claim on the `composed_of` set; TCG Delta status and Base/Rebase completeness are the attestation analogue | completeness | DEC-001 |

### 5.2 Which source can fill which model element

| Model element | Sources that can fill it |
|---|---|
| Component (hardware part) | CycloneDX `device`; SPDX 3.1 `Hardware`; TCG `ComponentIdentifier-v2`; Redfish `Processor`, `Memory`, `PCIeDevice`, `Chassis`, `AssemblyData`; CoRIM `environment-map`; EAT entity and `submods`; CISA and CERT-In fields (no format) |
| Component (firmware) | CycloneDX `firmware`; SPDX `firmware` purpose; CoSWID tags embedded in firmware; Redfish `SoftwareInventory`; TCG Firmware classes; SUIT components |
| `composed_of` | CycloneDX nesting; SPDX `contains`; Redfish `Contains`, `SubProcessors`; CoRIM domain membership; EAT `submods`; CISA B.1.1 nesting; CERT-In Sub-component |
| `depends_on` | CoRIM trust dependency triples (trust, not build); CoSWID `requires` links (library linking, 1.6) |
| Party with `manufactured_by`, `supplied_by` | CycloneDX `manufacturer`, `supplier` (2.0: `parties` with roles); SPDX `originatedBy`, `suppliedBy` (3.1: `productAgent`); TCG manufacturer and PEN; Redfish `Manufacturer`, `Producer`, `Vendor`; CISA entity fields |
| ProductInstance (unit) | TCG Platform Serial Number; Redfish `SerialNumber`, `UUID`; EAT `ueid`; DICE UEID; SPDM hardware identity |
| `owned_by` | TCG `platformOwnership`; CycloneDX 2.0 party role `owner` |
| Assertion with provenance | SPDM signed measurements; DICE TCB info; EAT; CoRIM (signed reference values); TCG platform certificates (signed endorsements); CycloneDX 2.0 attributed identifiers |
| LifecyclePhase (production, distribution) | SPDX 3.1 SupplyChain actions; CycloneDX 2.0 origin stages; TCG Delta and Rebase certificates |

## 6. Library records (Table 9 rows)

FX-1 here means the full extraction of `library/docs/extraction.md`. The rule in `dimensions.md`: a spec whose fields the report relies on is FX-1, a spec cited only for status or one definition stays a stub with the reason written down, and non-specifications reach the summary bar. Phase 2 confirms the list with the student.

| Source | Record id (existing or proposed) | Type | Status now | Proposed action | Reason |
|---|---|---|---|---|---|
| CISA HBOM framework (2023) | `cisa-hbom-framework-2023` (proposed; body `regulator`) | spec | none | FX-1 (small) | Table 4 and section 3.3 rely on all 47 fields; a machine-checkable rendering of Appendix C would serve as the schema artifact; `bcp14-count` gives 0, so requirements need the lowercase "must" in C.1.1 recorded as a reconciliation |
| CycloneDX 1.7 | `cyclonedx-1-7` | spec | queued (owner `Ndewedo-Newbury`) | FX-1 (with agent 1) | hardware fields used: component `type`, `components`, `manufacturer`, `supplier`, `organizationalEntity.address`, `compositions`, `properties` |
| CycloneDX property taxonomy (`cdx:device`) | `cyclonedx-property-taxonomy` (proposed) | repo | none | summary | registry of names used in `ext` cells |
| CycloneDX 2.0-dev | none | spec | none | none until release; then a new `cyclonedx-2-0` record | unreleased; cited by commit |
| CycloneDX HBOM capability page | `cyclonedx-hbom-capability` (proposed) | web | none | stub | one quote |
| SPDX 3.0.1 | `spdx-3-0-1` | spec | queued | FX-1 (with agent 1) | device and firmware purposes, `contains`, agents |
| SPDX 3.1 (RC1, develop) | none | spec | none | stub at release | pre-release; Hardware profile cited by commit |
| Firmware Embedded SBOM Specification 0.10 | `osfw-firmware-embedded-sbom-0-10` (proposed) | spec | none | FX-1 candidate (109 keywords, short) or stub | Q5 relies on its required fields; it is the only written firmware SBOM profile found |
| python-uswid | `hughsie-python-uswid` (proposed) | repo | none | summary | tool behaviour (header versions, type mapping) |
| LVFS documentation | `lvfs` (proposed) | web | none | summary | service practice |
| coreboot SBOM | `coreboot-sbom` (proposed) | web | none | summary | practice |
| UEFI Forum blog and 2024 deck | `uefi-firmware-sbom-proposal-2023` (proposed) | article | none | stub | context only |
| OpenEmbedded-Core and Zephyr SBOM generators | agent 5's tool records | repo | none | agent 5 | tools |
| TCG Platform Certificate Profile 2.1 | `tcg-platform-certificate-profile-2-1` (proposed) | spec | none | FX-1 candidate (301 keywords, ASN.1) or stub | Table 4b relies on its traits; the ASN.1 defects (1.13) belong in its design notes |
| TCG Component Class Registry 1.0 r14 | `tcg-component-class-registry-1-0-r14` (proposed) | spec | none | FX-1 candidate (15 keywords; the class table is the messages artifact) | class vocabulary for Component kinds |
| TCG PCIe-based Component Class Registry r18 | `tcg-pcie-component-class-registry-1-r18` (proposed) | spec | none | stub | cited for one mapping rule |
| TCG DICE Attestation Architecture 1.2 and errata | `tcg-dice-attestation-architecture-1-2` (proposed) | spec | none | FX-1 candidate (81 keywords) or stub | `DiceTcbInfo` fields in Table 4b; existing `tcg-dice-cert-profiles` is pinned to r01 while v1.1 (2025-04-24) is current, so a new record is needed by the library's versioning rule |
| DMTF SPDM DSP0274 1.4.1 | `dmtf-dsp0274-1-4-1` (proposed) | spec | none | stub | cited for measurement types and identity OIDs; FX-1 would need a lowercase "shall" count (1,367), since `bcp14-count` finds 1 |
| DMTF Redfish DSP8010 2026.2 | `dmtf-redfish-schema-2026-2` (proposed) | spec | none | FX-1 candidate limited to the eight schemas used (the JSON Schemas are the schema artifact) or summary | Table 4b and section 5 rely on its properties |
| IETF CoRIM | `draft-ietf-rats-corim` | draft | stub; `identifiers.draft` empty, URL `https://datatracker.ietf.org/doc//` | stub, metadata fixed and pinned to -11 | draft still changing (WG Last Call) |
| IETF EAT | `rfc-9711` | rfc | stub | FX-1 candidate if Table 6 adopts its claims; otherwise stub | several claims cited in Table 4b |
| IETF SUIT manifest | `draft-ietf-suit-manifest` (proposed) | draft | none | stub | in the RFC Editor queue |
| RFC 9019, RFC 9124 | `rfc-9019`, `rfc-9124` (proposed) | rfc | none | stub | status only |
| RFC 9334 | `rfc-9334` | rfc | stub | stub | one definition (composite device) |
| RFC 9393 (CoSWID) | none | rfc | none | agent 1 (FX-1 candidate in `dimensions.md`) | firmware SBOM fields reuse its CDDL |
| ISO/IEC 19770-6:2024 | `iso-iec-19770-6-2024` (proposed) | spec | none | stub | paywalled; metadata and contents list only |
| CERT-In Technical Guidelines v2.0 | `cert-in-2025-aibom-guidelines` (id named in RPT-0014; reuse) | spec (body `regulator`) | none | summary | guidance; one record for both reports |
| Auto-ISAC SBOM IR v3.0 | `auto-isac-sbom-ir-v3` (proposed) | spec (body `other`) | none | summary | industry guidance |
| UN R155, UN R156 | `unece-r155`, `unece-r156` (proposed) | spec (body `regulator`) | none | stub | two clauses cited; agent 2 and RPT-0007 may need more |
| ITU-T SG17 C-548 | `itu-t-sg17-c548-2026` (proposed) | note | none | stub | metadata only; text restricted |
| NSA PACCOR | `nsacyber-paccor` (proposed) | repo | none | stub (agent 5) | practice evidence only |
| OMB M-26-05 | `omb-m-26-05` | spec | summarized | add a `cites` link to `cisa-hbom-framework-2023` once it exists | it already cites the framework by title |

Library observation: the topic file `topics/device-attestation.yaml` has `records: []`, although 26 records set `topic: device-attestation` (grep of `record.yaml` files). A reindex in the library repository would list them.

## 7. searches.md rows

| date | dimension | query | engine | notable hits |
|---|---|---|---|---|
| 2026-10-08 | 2 | fetch cisa.gov HBOM resource page and PDF (curl, browser user agent) | curl | HTTP 403 (Akamai "Access Denied") |
| 2026-10-08 | 2 | cisa.gov/resources-tools/resources/hardware-bill-materials-hbom-framework-supply-chain-risk-management | WebFetch (links only) | publication date 2023-09-25; framework PDF, fact sheet (2024-02 folder), webinar |
| 2026-10-08 | 2 | Wayback CDX for the framework PDF, the fact sheet and the resource page | web.archive.org CDX API | 30+ PDF captures 2023-11-01 to 2026-09-24 with one payload digest; one 403 capture (2026-07-16) |
| 2026-10-08 | 2 | GitHub API: CycloneDX/specification releases, tags, release notes of 1.7.1 and 1.7.2 | gh api | latest 1.7.2 (2026-09-17); no hardware change |
| 2026-10-08 | 2 | GitHub API: commits to cdx/device.md; all 131 PRs and the issues mentioning "device" in cyclonedx-property-taxonomy | gh api, gh search issues | device.md last changed 2025-10-28; open issues #43, #67, #104, #185 |
| 2026-10-08 | 2 | CycloneDX/specification issue #981, PR #982, milestones, PR #652 | gh | hardware support merged into 2.0-dev on 2026-08-20; 2.0 unreleased |
| 2026-10-08 | 2 | raw.githubusercontent.com CycloneDX schemas at tags 1.5, 1.6, 1.7, 1.7.2 and 2.0-dev modules | curl, jq | 1.5 lacks component manufacturer and address; 1.6 adds both |
| 2026-10-08 | 2 | GitHub API: spdx/spdx-3-model branches, tree of develop, main and 3.1-rc1, commits to model/Hardware, 3.1-rc1 release notes; spdx/spdx-spec releases | gh api | Hardware and SupplyChain profiles in 3.1-rc1 and develop; latest release 3.0.1 |
| 2026-10-08 | 2 | spdx.org/rdf/3.0.1/spdx-model.ttl; spdx/spdx-spec chapter headings at tags v2.2, v2.2.2, v2.3 | curl, gh api | model digest unchanged; CISA's SPDX clause numbers match SPDX 2.2 |
| 2026-10-08 | 2 | GitHub API and PyPI: hughsie/python-uswid | gh api, curl | uswid 0.6.0 (2026-03-16) |
| 2026-10-08 | 2 | lvfs.readthedocs.io pages; fwupd.org/lvfs/uswid; an LVFS component SWID page | curl | SBOM spec moved to OSFW; claims page; component page 403 |
| 2026-10-08 | 2 | sbomspec.osfw.foundation; GitHub open-source-firmware/sbom | curl, gh api | Firmware Embedded SBOM Specification 0.10 |
| 2026-10-08 | 2 | doc.coreboot.org/sbom/sbom.html; coreboot/coreboot Documentation/sbom and src/sbom | curl, gh api | uSWID in CBFS; CONFIG_SBOM default n |
| 2026-10-08 | 2 | docs.yoctoproject.org/dev-manual/sbom.html; openembedded-core master SPDX classes | curl, gh api | create-spdx inherits create-spdx-3.0; SPDX 3.0.1 |
| 2026-10-08 | 2 | zephyrproject-rtos/zephyr main and v4.4.2 west spdx sources | gh api, curl | v4.4.2: SPDX 2.2, 2.3; main adds 3.0, 3.1; default 2.3 |
| 2026-10-08 | 2 | UEFI firmware SBOM uSWID CoSWID Insyde OR AMI OR Phoenix OR "Intel FSP" embedded SBOM | WebSearch | UEFI blog (2023-10-04), UEFI 2024 Plugfest deck, Phoenix press release (not used) |
| 2026-10-08 | 2 | uefi.org/node/5015 and the 2024 webinar PDF | curl | proposal blog; deck slide 25 |
| 2026-10-08 | 2 | TCG Platform Certificate Profile specification version 2.0 revision component identifier | WebSearch | v1.1 r19 PDF and resource pages; summary claimed no v2.0 (rejected) |
| 2026-10-08 | 2 | trustedcomputinggroup.org resource pages (curl, WebFetch) | curl, WebFetch | Cloudflare challenge (403); PDFs under wp-content download directly |
| 2026-10-08 | 2 | Wayback captures of TCG resource pages (platform certificate, four component class registries, DICE pages) | web.archive.org | latest versions listed in sections 1.13 to 1.15 |
| 2026-10-08 | 2 | GitHub API: nsacyber/paccor, nsacyber/HIRS | gh api | PACCOR v2.0r16, HIRS v3.2.0 |
| 2026-10-08 | 2 | www.dmtf.org/dsp/DSP0274; DSP0274_<version>.pdf probes; Wayback captures of the DSP0274 and SPDM pages | curl, web.archive.org | live 403; 1.4.1 latest published |
| 2026-10-08 | 2 | redfish.dmtf.org/schemas/v1/ index; GitHub DMTF/Redfish-Publications tags and LICENSE | curl, gh api | bundle 2026.2 (2026-09-16), BSD-3-Clause |
| 2026-10-08 | 2 | datatracker API: draft-ietf-rats-corim, draft-ietf-suit-manifest, draft-ietf-rats-eat and their state codes | curl | CoRIM -11 in WGLC; SUIT -37 in RFC Ed Queue (Blocked); EAT published as RFC 9711 |
| 2026-10-08 | 2 | ietf.org archive drafts and rfc-editor.org RFC 9711, 9124, 9019, 9393, 9334 | curl | texts parsed |
| 2026-10-08 | 2 | iso.org/standard/77642.html and OBP preview (curl, WebFetch); Claude in Chrome | curl, WebFetch | 403 (Cloudflare); extension not connected |
| 2026-10-08 | 2 | Wayback capture of iso.org/standard/77642.html | web.archive.org | status, life-cycle dates |
| 2026-10-08 | 2 | "19770-6" hardware identification tag HWID elements | WebSearch | national store pages; GSO adoption (not verified) |
| 2026-10-08 | 2 | standards.iteh.ai ISO/IEC 19770-6:2024 sample | WebSearch | no iTeh sample; BSI Knowledge pages (2024 adoption; 2022 draft titled "Hardware schema") |
| 2026-10-08 | 2 | BSI Knowledge page and its public preview PDF | curl | 8-page preview with the contents list |
| 2026-10-08 | 2 | Auto-ISAC SBOM best practice guide vehicle ECU software bill of materials | WebSearch | Auto-ISAC press release and report page |
| 2026-10-08 | 2 | automotiveisac.com press release, sbom-reports page, report PDF | curl | report v3.0 (2025-01-17) |
| 2026-10-08 | 2 | UN Regulation No. 155 interpretation document software bill of materials ECU supplier "bill of materials" | WebSearch | vendor blogs only; no UNECE document |
| 2026-10-08 | 2 | unece.org R155e.pdf, R156e.pdf (2021-03 folder) | curl, web.archive.org | live 403; Wayback captures; 0 SBOM hits |
| 2026-10-08 | 2 | cert-in.org.in Technical Guidelines PDF v2.0 | curl | digest matches RPT-0014 |
| 2026-10-08 | 2 | CERT-In "Technical Guidelines" SBOM QBOM CBOM AIBOM HBOM version | WebSearch | v2.0 (2025-07-09) only |
| 2026-10-08 | 2 | "hardware bill of materials" guidance government agency 2025 OR 2026 HBOM national | WebSearch | ITU-T C-548; IST news (not primary); Federal Register 2025-16147 |
| 2026-10-08 | 2 | itu.int/md/T25-SG17-C-0548/en; ITU-T SG17 work programme page | curl | C-548 metadata; restricted text |
| 2026-10-08 | 2 | Institute for Security and Technology hardware bill of materials HBOM initiative Allan Friedman | WebSearch | biographies and podcasts; IST site search and topic feed: no HBOM item |
| 2026-10-08 | 2 | Korea HBOM guideline hardware bill of materials KISA OR MSIT 2025 | WebSearch | only ITU-T C-548 |
| 2026-10-08 | 2 | federalregister.gov API document 2025-16147 | curl | CISA 2025 SBOM draft notice; no hardware |
| 2026-10-08 | 2 | Wayback capture of the CISA 2026 SBOM Minimum Elements PDF | web.archive.org | "hardware" 0 hits, "firmware" 1 |
| 2026-10-08 | 2 | cyclonedx.org/capabilities/hbom/ | curl | quote re-checked |

## 8. sources.md rows

| source | type | dimension | library record id | bears_on |
|---|---|---|---|---|
| CISA, A Hardware Bill of Materials (HBOM) Framework for Supply Chain Risk Management (September 2023), PDF SHA-256 `cba6ce12…025806` | guide | 2 | `cisa-hbom-framework-2023` (proposed) | DEC-001, DEC-002 |
| CISA HBOM framework fact sheet (September 2023) | guide | 2 | none (folded into the framework record) | DEC-001 |
| CycloneDX 1.7.2 JSON schema (tag `1.7.2`) and 1.5, 1.6, 1.7 schemas for history | spec | 1, 2 | `cyclonedx-1-7` (queued) | DEC-001, DEC-002 |
| CycloneDX property taxonomy, `cdx/device.md` at `836dc95e89` | spec (side list) | 2 | `cyclonedx-property-taxonomy` (proposed) | DEC-001, DEC-002 |
| CycloneDX 2.0-dev modules at `f6dcf4d`; issue #981, PR #982 | spec (unreleased) | 2 | none until release | DEC-001, DEC-002 |
| CycloneDX HBOM capability page | web page | 2 | `cyclonedx-hbom-capability` (proposed) | DEC-001 |
| SPDX 3.0.1 model file (`spdx-model.ttl`) | spec | 1, 2 | `spdx-3-0-1` (queued) | DEC-001, DEC-002, DEC-004 |
| SPDX 3.1-rc1 and develop (`4eaf6a4`): Hardware, SupplyChain, Core locations | spec (pre-release) | 2 | none until release | DEC-001, DEC-002 |
| Firmware Embedded SBOM Specification 0.10 (OSFW, commit `abab4b8960`) | spec | 2 | `osfw-firmware-embedded-sbom-0-10` (proposed) | DEC-001, DEC-002 |
| python-uswid 0.6.0 (commit `d1930533`) | tool | 2 | `hughsie-python-uswid` (proposed) | DEC-002 |
| LVFS documentation (claims page, SBOM helper) | tool docs | 2 | `lvfs` (proposed) | DEC-002 |
| coreboot SBOM documentation and `src/sbom` (commit `1fd5d0f3`) | tool docs | 2 | `coreboot-sbom` (proposed) | DEC-002 |
| UEFI Forum, "Firmware SBOM Proposal" (2023-10-04) and 2024 Plugfest deck | article | 2 | `uefi-firmware-sbom-proposal-2023` (proposed) | DEC-002 |
| Yocto Project SBOM documentation (6.0-tip) and openembedded-core master SPDX classes | tool docs | 2, 3 | agent 5 | DEC-002 |
| Zephyr `west spdx` sources (main `bbc6385f`, v4.4.2) | tool docs | 2, 3 | agent 5 | DEC-002 |
| TCG Platform Certificate Profile 2.1 (2026-01-27) | spec | 2 | `tcg-platform-certificate-profile-2-1` (proposed) | DEC-001, DEC-009 |
| TCG Component Class Registry 1.0 r14; PCIe-based r18; SMBIOS-based r01 | spec | 2 | `tcg-component-class-registry-1-0-r14`, `tcg-pcie-component-class-registry-1-r18` (proposed) | DEC-001 |
| NSA PACCOR (v2.0r16) and HIRS (v3.2.0) | tool | 2 | `nsacyber-paccor` (proposed) | DEC-002 |
| TCG DICE Attestation Architecture 1.2 and errata (2026-01-29) | spec | 2 | `tcg-dice-attestation-architecture-1-2` (proposed) | DEC-001 |
| DMTF SPDM DSP0274 1.4.1 | spec | 2 | `dmtf-dsp0274-1-4-1` (proposed) | DEC-001 |
| DMTF Redfish schemas DSP8010 2026.2 (Redfish-Publications tag `2026.2`) | spec (machine-readable) | 2 | `dmtf-redfish-schema-2026-2` (proposed) | DEC-001, DEC-004 |
| IETF draft-ietf-rats-corim-11 | draft | 2 | `draft-ietf-rats-corim` (stub) | DEC-001, DEC-004 |
| RFC 9711, EAT | rfc | 2 | `rfc-9711` (stub) | DEC-001 |
| IETF draft-ietf-suit-manifest-37; RFC 9019; RFC 9124 | draft, rfc | 2 | `draft-ietf-suit-manifest`, `rfc-9019`, `rfc-9124` (proposed) | DEC-001 |
| RFC 9334, RATS architecture | rfc | 2 | `rfc-9334` (stub) | DEC-001 |
| RFC 9393, CoSWID (re-check) | rfc | 1, 2 | none (agent 1) | DEC-002 |
| ISO/IEC 19770-6:2024: ISO Open Data row, ISO catalog page (Wayback 2026-03-12), BSI preview of BS ISO/IEC 19770-6:2024 | spec (not read) | 2 | `iso-iec-19770-6-2024` (proposed) | DEC-001, DEC-002 |
| CERT-In, Technical Guidelines on SBOM, QBOM & CBOM, AIBOM, HBOM, v2.0 (2025-07-09) | guide | 2, 8 | `cert-in-2025-aibom-guidelines` (RPT-0014 id) | DEC-001, DEC-002 |
| Auto-ISAC SBOM Informational Report v3.0 (2025-01-17) | guide | 2 | `auto-isac-sbom-ir-v3` (proposed) | DEC-002, DEC-009 |
| UN Regulation No. 155 and No. 156 (2021 texts) | regulation | 2, 6 | `unece-r155`, `unece-r156` (proposed) | DEC-009 |
| ITU-T SG17 Contribution 548 (X.hbomsec proposal), metadata only | note | 2 | `itu-t-sg17-c548-2026` (proposed) | DEC-002 |
| CISA 2026 Minimum Elements for an SBOM (2026-07-29), checked for hardware only | spec | 2, 8 | `cisa-2026-sbom-minimum` (stub; agent 1) | DEC-002 |
| ISO Open Data `iso_deliverables_metadata` (downloaded 2026-09-30) | dataset | 1, 2 | not yet a record (v0.1.0) | DEC-002 |

## 9. Rejected claims

| Claim met | Where | Why rejected |
|---|---|---|
| The TCG Platform Certificate Profile's current version is 1.1 r19 and no version 2.0 is public | WebSearch summary (TCG query) | The archived resource page (2026-09-02) lists 2.1 (2026-01-27) and 2.0 r39 (2024-07-29); both PDFs are public (2.1 downloaded, 1.13) |
| BS ISO/IEC 19770-6:2024 "was published on June 6, 2024, and contains 52 pages" | WebSearch summary (iTeh query) | ISO: published 2024-01-26, 41 pages; BSI's page: BS adoption published 30 June 2024; no fetched page gives 52 pages |
| "The uSWID format is a 24 byte header" | WebSearch snippet (UEFI query) | True only for header version 2; versions 3 and 4 are 25 and 26 bytes (`format_uswid.py`, 1.7) |
| "The 25 byte uSWID header in full" followed by the version 4 layout | uswid README | Inconsistent: the version 4 header is 26 bytes (`hdrsz` 26; length "typically 0x1A") |
| CoSWID is a DMTF ("DTMF") format | Firmware Embedded SBOM Spec 0.10, §4.3 | The linked document is RFC 9393, an IETF standard; treated as an error in the source |
| UN R155 makes the SBOM "the regulation's most operationally difficult clause" | WebSearch summary of a vendor blog (safeguard.sh) | R155 (2021 text) contains no "bill of material" or "SBOM"; Auto-ISAC says the rule "does not explicitly refer to SBOMs"; the blog is not primary |
| A former CISA SBOM official leads a new HBOM multistakeholder process at the Institute for Security and Technology (November 2025) | WebSearch snippet (Inside Cybersecurity, paywalled) | No primary source found on the IST site (search and bill-of-materials topic feed); not used |
| "The SBOM Guidelines have not been made mandatory" (CERT-In) | WebSearch summary | Not checked against an official statement; the HBOM section itself says "must" for hardware supplied to government bodies (§10.4.1.2); not used |
| A Gulf adoption "GSO ISO/IEC 19770-6:2025" exists | WebSearch result title | Not fetched; not used |
| SPDX and CycloneDX are "US NIST endorsed formats" | Auto-ISAC report §4.13 | Not verified against NIST; reported only as Auto-ISAC's wording |
| The framework's "47 fields" or category totals change when the C.8 quick reference is used | own check | Rejected: C.8 lists the same 47 names; only category boundaries differ (1.1) |

## 10. Open items, and notes for other agents

Open items:

1. **ISO/IEC 19770-6:2024** text not read (paywalled). The OBP preview did not load (Cloudflare; Claude in Chrome not connected). Only the contents list is known. Sponsor question 4 in `dimensions.md` stands.
2. **Not read, possibly relevant:** the TCG Reference Integrity Manifest specifications and *TCG Platform Requirements for Certificates and RIMs* (linked from the Platform Certificate page); DICE Certificate Profiles v1.1; the Storage Component Class Registry r22 PDF; DMTF DSP0266 and DSP0268 (Redfish protocol and data model texts); the TCG DICE endorsement architecture (a CoRIM profile).
3. **Release dates unknown:** CycloneDX 2.0 (milestone due 2026-08-31, still open) and SPDX 3.1 (RC1 of 2026-01-24 only). Columns and counts for both are from moving branches.
4. **UN R155 and R156:** only the 2021 base texts; later supplements and the WP.29 interpretation documents not checked. ISO 24089 not read (library stub `iso-24089-2023`; RPT-0007).
5. **Practice not inspected:** no LVFS per-firmware SBOM export (Cloudflare); no tool was run (uswid, goswid, PACCOR, HIRS); agent 5 owns tool runs.
6. **The C.8 category reading** of the HBOM framework is from the page layout, not the PDF structure tree.
7. **ITU-T X.hbomsec:** whether the work item was approved at the June 2026 meeting was not found.
8. **Decisions for the main session:** Table 4's last row mixes device-reported evidence and signed supplier references; splitting it into "measured (evidence)" and "endorsed reference" would remove the `≈` cells in 4b. Row "bus or interconnect" mixes a bus part and a connection.

Notes for other agents:

- **Agent 1 (formats, baselines, other bills):** CycloneDX 1.7.2 (2026-09-17) is the latest release; CycloneDX 2.0-dev also adds threat, risk, weakness, requirement, control and blueprint modules (`schema/2.0/modules/` at `f6dcf4d`), relevant to RPT-0005 and to "what comes next". SPDX 3.1-RC1 (2026-01-24) adds Hardware, SupplyChain, Service, Operations and FunctionalSafety profiles. CISA's *2026 Minimum Elements* (publication 2026-07-29) is public (Wayback capture 2026-10-04, SHA-256 `b42046c4…a7456fc`). Taxonomy issue #185 proposes `cdx:cisa` and `cdx:fda` namespaces mapping the 2026 elements.
- **Agent 2 (identifiers, build identity):** unit identity candidates are TCG Platform Serial Number, SPDM hardware identity keys, DICE and EAT UEIDs, Redfish `SerialNumber` and `UUID`. The firmware SBOM convention uses the UEFI ESRT GUID as CoSWID `tag-id`. The Firmware Embedded SBOM Spec's VEX product id `pkg:<GUID>` (§6.1.1) appears to lack the purl type and name structure (not checked against ECMA-427). R156 §2.2 (RXSWIN definition) and §7.1.2.3 (register) are in `R156e.pdf` (SHA-256 `9a7b4192…cb5a8`).
- **Agent 3 (bridge to CVEs and CWEs):** CERT-In §10.4.1.5 asks hardware vendors for VEX (four CISA statuses) then CSAF; the firmware SBOM spec names LVFS as a possible VEX "trusted neutral entity" and matches VEX by GUID. Hardware identity in CPE is outside this file.
- **Agent 5 (tools and radar):** firmware SBOM tools to list: uswid 0.6.0 (exports CycloneDX 1.6 and SPDX 2.3), goswid (coreboot), PACCOR v2.0r16 and HIRS v3.2.0 (platform certificates), OpenEmbedded-Core `create-spdx-3.0`, Zephyr `west spdx`. None was run here.
