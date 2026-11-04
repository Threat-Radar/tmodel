---
schema: "archdoc/v1"
id: MAP-0002
title: "Requirement interchange: how a core Requirement maps to STIX 2.1, OTM, CycloneDX 1.7 and SPDX 3.0.1"
short_title: "Requirement interchange"
description: "For each of four formats, which of ADR-0012's Requirement slots it can carry, how, and what is lost, checked against each format's own specification or schema. STIX 2.1 and OTM have no requirement object. CycloneDX 1.7 has one (definitions.standards[].requirements[]) and attests conformance to it in declarations. SPDX 3.0.1 can name a standard but not a provision. Evidence for #169 and the ADR-0007 import crosswalks, not a decision."
type: mapping
category: security
status: draft
version: "0.1.0"
date: "2026-11-03"
updated: "2026-11-03"
version_policy: "semver; 0.x while draft"
needs_review: true
reviewed: false
canonical_path: spec/MAP-0002-requirement-interchange.md
defers_to: ARCH-0001
---

# MAP-0002: Requirement interchange

**Status: draft 0.1.0, evidence and not a decision.** For each of four formats, this note says how ADR-0012's `Requirement` would map and what would be lost. It answers #169 deliverable 2 (parent #168).

It decides nothing. ADR-0012's scope guard leaves out "an import mapping from the library's requirement format (DEC-002 / #9)". ADR-0007 commits two imports, OTM and STIX 2.1, and says each "gets a `MAP-NNNN` crosswalk + a `spec/vectors/` round-trip". Its four exports are JSON-LD, Turtle, GraphML and CSV, so exporting to any of the formats here would be an addition. ADR-0007 says additions arrive "as MAP-NNNN + a vector, never as silent schema drift". This note is the Requirement slice of those crosswalks. It has no vectors yet.

## Overview

| Format | Requirement object? | Best carrier | What survives | Main losses |
|---|---|---|---|---|
| STIX 2.1 | No: none of its 19 SDOs is one | An Extension Definition (`new-sdo`), §7.3 | Whatever the extension defines. Without one, only a name and prose | Everything, for a consumer that does not know the extension |
| OTM 0.2.0 | No: no requirement or control object | `mitigations[]`, for the mitigation side only | Name, description, flat `attributes` strings | Normativity, kind, source, every requirement edge, review state |
| CycloneDX 1.7 | **Yes:** `definitions.standards[].requirements[]` | That object, with conformance in `declarations` | Text, designator, hierarchy, CRE topics, conformance claims | Kind, normativity and text origin (except as properties), `addresses`, the requirement-to-requirement edges |
| SPDX 3.0.1 | No | `standardName` / `standardCompliance` strings, or an Extension subclass | The name of a standard a product follows | Provisions and every slot, unless a custom extension is defined |

**Read-across.**
- **CycloneDX 1.7 is the only format of the four that carries requirements natively.** It is not in ADR-0007's committed set, so adding it is a sponsor question (Q1).
- **No format carries `addresses`.** None of them links a requirement to the threat, weakness or attack pattern it counters. That is the graph value #168 is after.
- **None carries tmodel's review of an AI-proposed link.** RPT-0005 §6 found the same for conversions between threat-model formats: every conversion drops review state.

## Sources checked

Each claim below was checked against these copies, read 2026-11-03.

| Format | Version and copy read | Digest (sha256) | Library record |
|---|---|---|---|
| STIX 2.1 | OASIS Standard, 10 June 2021, `https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html` | `612b6150…ff6c69` | `stix-2-1` (summarized; same digest) |
| OTM | 0.2.0, `otm_schema.json` at iriusrisk/OpenThreatModel `c88c5a7` | `81e7f5a5…545eef0c` | `open-threat-model` (FX-1; same digest) |
| CycloneDX | 1.7, `schema/bom-1.7.schema.json` at CycloneDX/specification tag `1.7` (commit `4b3f594`, 2025-10-21) | `df472ef4…914221` | `cyclonedx-1-7` (stub; pins the ECMA-424 2nd edition PDF, which this note did not read) |
| SPDX | 3.0.1, `https://spdx.org/rdf/3.0.1/spdx-model.ttl` | `30ebb4af…5c593` | `spdx-3-0-1` (stub; no digest) |

## The slots being mapped

From ADR-0012:
- **Identity and text:** `id`, `name`, `text`, `text_origin`, `requirement_kind` and `normativity`.
- **Source:** `source_ref` (the library record and provision) and `source_locator` (the clause).
- **Requirement-to-requirement edges:** `refines`, `derived_from`, `conflicts_with` and `maps_to`.
- **Edges out:**
  - `addresses` → ThreatInstance | Weakness | AttackPattern;
  - `satisfied_by` → Mitigation;
  - `applies_to` → Product | ProductInstance | Component;
  - `applies_to_family`.
- **On the other side:** `Mitigation.stated_as` → Requirement.
- **Provenance and review:** a proposed link is an Assertion with `confidence`, and a human Review accepts or rejects it.

## Slot by slot

Key: `=` a direct field; `≈` close, with a loss noted; `ext` only through the format's extension mechanism; `—` nothing.

| Slot | STIX 2.1 | OTM 0.2.0 | CycloneDX 1.7 | SPDX 3.0.1 |
|---|---|---|---|---|
| `id` | ext (new SDO `id`) | — | ≈ `bom-ref`, unique only within one BOM | ext |
| `name` | ext; ≈ `course-of-action.name` for the mitigation side | ≈ `mitigations[].name` | = `title` | ext |
| `text` | ext; ≈ `note.content` or CoA `description` (prose only) | ≈ `mitigations[].description` | = `text` | ext |
| `text_origin` | ext | ≈ `attributes` string | ≈ `properties` | ext |
| `requirement_kind` | ext | ≈ `attributes` string | ≈ `properties` | ext |
| `normativity` | ext | ≈ `attributes` string | ≈ `properties` | ext |
| `source_ref` | ≈ `external_references[]` (`source_name`, `external_id`, `url`) | ≈ `attributes` string | ≈ the enclosing `standard` (`name`, `version`, `owner`) plus `externalReferences` | ≈ `externalRef`; ≈ `standardName` (standard only) |
| `source_locator` | ≈ `external_references[].external_id` or `description` | ≈ `attributes` string | ≈ `identifier` (the designator); the clause only as a property | — |
| `refines` | ≈ a Relationship with a user-defined `relationship_type` | — | ≈ `parent` (hierarchy, not refinement) | — |
| `derived_from` | ≈ common `derived-from`, but see its direction below | — | — | — |
| `conflicts_with` | ≈ user-defined `relationship_type` | — | — | — |
| `maps_to` | ≈ user-defined `relationship_type` | — | ≈ `openCre` (a shared topic id, not a pair) | — |
| `addresses` | ≈ user-defined relationship to `attack-pattern` or `vulnerability`; no SDO for a CWE weakness | — (only `threats[].cwes`, on a threat) | — | — |
| `satisfied_by` | ≈ user-defined relationship to a `course-of-action` | ≈ `components[].threats[].mitigations[]` (per component, via a threat) | ≈ `declarations.attestations[].map[]` → `claims[]` → `mitigationStrategies` / `evidence` | — |
| `applies_to` | ≈ user-defined relationship to the import's Product or Component object | — | ≈ `claims[].target`, only inside a claim | ≈ `standardName` on the Artifact (inverted, no provision) |
| `applies_to_family` | ext | — | ≈ `properties` | — |
| `Mitigation.stated_as` | ≈ `course-of-action` for the mitigation, plus a user-defined relationship | ≈ `mitigations[]`, with the requirement in `attributes` | — | — |
| Assertion `confidence` | = `confidence` (0–100; Appendix A maps Low/Med/High to 15/50/85) | — | ≈ `attestations[].map[].confidence.score` (0–1), but for conformance, not for a link | — |
| Review | ≈ `opinion` (five-point scale, `explanation`, `authors`) | — | ≈ `assessors[]` and `evidence[].reviewer`, for conformance | ≈ `Annotation` with `annotationType: review` |

## STIX 2.1

**No requirement object.** None of STIX 2.1's 19 SDOs (§4.1 to §4.19) is a requirement or control. #169 named three options. Checked against the text:

- **A custom object is the deprecated route.** §11 says the Extension mechanisms of §7.3 "replace the customization mechanisms defined in this section", and that those mechanisms "should not be used to implement any new extensions". §11.2 adds: "Custom objects SHOULD be defined using the STIX Extension mechanism for new SDO". So the current form of this option is an **Extension Definition** with `extension_types: ["new-sdo"]`. Its required properties include `name`, `schema` ("the normative definition of the extension") and `version`. It could carry every Requirement slot. The cost is §7.3: "A consumer that receives STIX content containing a STIX extension that it does not understand MAY refuse to process the content or MAY ignore that extension."
- **A `note` is prose attached to objects.** It has `content` (required), `abstract`, `authors` and `object_refs` (required), and §4.13 says it conveys "informative text to provide further context". A Requirement written as a Note keeps its text but loses every typed slot: normativity, kind, source and edges. It also reads as commentary on other objects, not as an obligation.
- **`course-of-action` fits the mitigation side only.** §4.3 defines it as "an action taken either to prevent an attack or to respond to an attack that is in progress". It notes that CoA "is a stub" with only `name`, `description` and a reserved `action`. It can stand for the generic Mitigation that a Requirement is `stated_as`. Its `mitigates` relationship (to attack-pattern, indicator, malware, tool and vulnerability) is the nearest thing to `addresses`, but it is the mitigation's edge, not the requirement's.

**Edges.** §5.1: `relationship_type` "SHOULD be an exact value listed in the relationships for the source and target SDO, but MAY be any string", using a–z, 0–9 and hyphen. So `refines`, `conflicts-with`, `maps-to`, `addresses` and `satisfied-by` can be user-defined names, which a consumer will not understand without the extension's documentation. STIX's common `derived-from` (§3.7) exists, but the specification defines it as: "The information in the target object is based on information from the source object". Read literally, that is the reverse of tmodel's `A derived_from B`. An exporter must pick a direction and document it, or use its own name.

**Provenance and review.** The common `confidence` (§3.2) is an integer from 0 to 100, and Appendix A maps a None/Low/Med/High scale to 0/15/50/85. That fits tmodel's `high | medium | low`. An `opinion` (§4.15) is "an assessment of the correctness of the information in a STIX Object produced by a different entity", on a five-point scale from strongly-disagree to strongly-agree. It is the nearest thing to a Review. It can judge a Relationship object, but it has no accepted or rejected state, so a reviewed link and a disputed one look alike.

**Import.** STIX 2.1 defines no requirement object, so an import has none to read. `course-of-action` imports as Mitigation, under ADR-0007's STIX crosswalk.

**What is lost.**
- Without an extension, everything except a name and prose.
- With one, nothing in the file, but for any consumer that does not know it, everything.
- In both cases, the Assertion and Review split collapses into objects and opinions.

## OTM 0.2.0

**No requirement or control object.** The schema's top level is `otmVersion`, `project`, `representations`, `assets`, `trustZones`, `components`, `dataflows`, `threats` and `mitigations`. Neither "requirement" nor "control" occurs anywhere in `otm_schema.json`.

**The mitigation side.**
- `mitigations[]` requires `id`, `name` and `riskReduction` (a number), and allows `description` and `attributes`.
- A generic Mitigation that a Requirement is `stated_as` can be exported this way, with the requirement's fields flattened into `attributes`. That field is a free-form `Map [string, string]`, per the library record's extraction (`open-threat-model`, `distilled/normative.md`).
- **`riskReduction` is required, and tmodel has no value for it.** An exporter must not invent one, so it either leaves such mitigations out or needs a rule the sponsor agrees to (Q3).

**Per-component state.** `components[].threats[]` holds threat instances (`threat`, `state`), each with `mitigations[]` (`mitigation`, `state`). That is the nearest thing to `satisfied_by` for one product: a mitigation is recorded as in place against a threat on a component. It runs through the threat, not the requirement.

**Weaknesses** appear only as `threats[].cwes`, so a requirement's `addresses` can be expressed only by attaching the requirement to a threat that lists the CWE.

**Import.** OTM 0.2.0 has no requirement object, so an import has none to read. `mitigations[]` imports as Mitigation, under ADR-0007's OTM crosswalk.

**What is lost.**
- Normativity, kind, text origin, source and locator, except as untyped strings.
- Every requirement-to-requirement edge, and `addresses`.
- All review state: OTM has none (RPT-0005 §6).

## CycloneDX 1.7

**A requirement object exists.**
- `definitions.standards[]` is described as "regulations, industry or organizational-specific standards, maturity models, best practices, or any other requirements which can be evaluated against or attested to". Each standard has `name`, `version`, `description`, `owner`, `requirements[]`, `levels[]` and `externalReferences`.
- Each requirement has:
  - `bom-ref`;
  - `identifier`: "This should match what is in the standard and should not be the requirements bom-ref";
  - `title` and `text`;
  - `descriptions[]` ("supplemental text … not directly part of the requirement");
  - `openCre[]` (Common Requirement Enumeration ids);
  - `parent` ("The `bom-ref` to a parent requirement");
  - `properties` and `externalReferences`.

**Mapping.**
- `text`, `title` and `identifier` map directly. For a licensed standard, the exported `text` is tmodel's paraphrase. CycloneDX has no field to say so, so `text_origin` needs a property.
- The enclosing `standard` stands for the library record (`source_ref`), and `identifier` for the designator.
- `requirement_kind`, `normativity`, `text_origin`, `applies_to_family` and the clause locator have no field. They go into `properties`, whose names the schema says "are encouraged to be registered" in the CycloneDX property taxonomy, so tmodel would need its own namespace.
- `levels[]` (identifier, title, description and the `requirements` in each level) has no tmodel equivalent, so it is lost on import.

**Edges.**
- **`parent`** gives a hierarchy. That is close to, but not the same as, `refines`: a child clause is not always a refinement.
- **`openCre`** gives a shared topic id. Two requirements with the same CRE overlap, which approximates `maps_to` through a hub, but without the pair and without any mapping provenance.
- **Nothing else:** there is no `derived_from`, no `conflicts_with`, and no link from a requirement to a vulnerability, a CWE or a threat (`addresses`).

**Conformance.** `declarations` holds:
- `assessors[]` (`thirdParty`, `organization`);
- `attestations[]`, each with an `assessor` and a `map[]` of `requirement` → `claims[]` and `counterClaims[]`, with `conformance` (`score` from 0 to 1, `rationale`, `mitigationStrategies`) and `confidence` (`score`, `rationale`);
- `claims[]` (`target`, `predicate`, `mitigationStrategies`, `reasoning`, `evidence`, `counterEvidence`);
- `evidence[]` (with `author` and `reviewer`);
- `targets` and `affirmation`.

A claim whose evidence is a mitigation approximates `satisfied_by` for the claim's `target`. But the attestation's conformance score is the R-042 verdict, which ADR-0012 keeps out of the core as `Requirement.conformance_status` (DEC-001b). **Importing or exporting conformance is therefore a DEC-001b question, not a core mapping.**

**Provenance.** CycloneDX 1.7's `citations[]` attribute named BOM fields (by JSON Pointer or path expression) to an `attributedTo` party or a `process`, with a `timestamp` and a `note`. That could carry "proposed by an agent" provenance for an exported field. It has no review verdict.

**Import.** A "standards" BOM imports directly as Requirements, with `parent` as a candidate `refines`, but only as a `proposed` Assertion (ADR-0012's review rule). `openCre` becomes a candidate `maps_to` to other requirements with the same CRE id, also proposed.

**What is lost.**
- On export: `addresses`, `derived_from`, `conflicts_with`, the pairwise `maps_to`, and the Assertion and Review split. The typed kind, normativity and text origin survive only as properties.
- On import: `levels`, and the attestations, until DEC-001b is decided.

## SPDX 3.0.1

**No requirement class.** The nearest terms in the model:
- `Artifact.standardName` (Core): "The name of a relevant standard that may apply to an artifact." A string naming a standard, not a provision.
- `AIPackage.standardCompliance` (AI profile): "Captures a standard that is being complied with." Also a string, and only on an AI package.
- `externalRef` types `secureSoftwareAttestation`, `certificationReport`, `riskAssessment` and `securityThreatModel`, which point at documents.
- `Annotation` (Core): "An assertion made in relation to one or more elements". Its `annotationType` includes `review` ("Used when someone reviews the Element"), and it has a `statement`.
- The Extension profile: `Element.extension` holds an `Extension`, an abstract class ("Instantiate a subclass instead"). A tmodel subclass could carry the Requirement slots, but no other tool would understand it.
- The software purposes `requirement` ("The Element provides a requirement needed as input for another Element") and `evidence` ("The Element is the evidence that a specification or requirement has been fulfilled") label files and packages, not statements.

**A trap: `hasRequirement`.** The Core relationship type `hasRequirement` reads: "The `from` Element has a requirement on each `to` Element, during a LifecycleScopeType period." It sits beside `hasProvidedDependency` and describes what one element needs from another. It is not a normative requirement, and Requirement edges must not be mapped to it.

**Edges.** `RelationshipType` is a closed list of 59 values (`sh:in` in the model). There is no refines, derived-from, conflicts-with, maps-to or addresses. `other` exists but "is directionless", so it would lose the direction of every edge.

**Import.** An SPDX document can say which standard a product names or claims (`standardName`, `standardCompliance`) and point at an attestation. That could become a candidate `applies_to` from that standard's Requirements to the Product, at the level of the whole standard and as a proposed Assertion. No provision-level requirement imports.

**What is lost.** Nearly everything, unless tmodel defines its own Extension subclass.

## Recommendations for review

These are candidates for the sponsor, not decisions.

1. **Do not export Requirements to OTM or SPDX.** Neither can hold one without flattening it into strings or a private extension. Name the standard in SPDX (`standardName`) and stop there.
2. **For STIX, export Requirements only through a published Extension Definition, if at all.** Map the mitigation side to `course-of-action`. Do not use a `note` or a deprecated custom object.
3. **Treat CycloneDX 1.7 as the candidate requirement interchange.** It carries text, designator, hierarchy and CRE topics natively. Adding it to ADR-0007 is the sponsor's call (Q1). Its conformance side waits on DEC-001b.
4. **Whatever the format, an imported link arrives as a `proposed` Assertion.** That covers `parent`, `openCre` and `standardName`, which become candidate `refines`, `maps_to` and `applies_to`. This follows ADR-0012's review rule.
5. **Before any of this ships,** add a `spec/vectors/` round-trip per format, as ADR-0007 requires.

## Questions for the sponsor

1. Should CycloneDX 1.7 (`definitions.standards`) join ADR-0007's interchange list as the requirement format, through a MAP and a vector?
2. Does exporting Requirements to STIX matter? If it does, should tmodel publish an Extension Definition for it?
3. OTM requires `riskReduction` on every mitigation. Should a generic mitigation's export leave it out, or is there an agreed value? (Inventing one is not an option.)
4. Should CycloneDX conformance attestations be read at all before DEC-001b decides `conformance_status`?

## Method and limits

- Each claim was checked against the copy in "Sources checked": the STIX HTML text, the OTM and CycloneDX JSON schemas, and the SPDX RDF model. The quotes are verbatim from those copies.
- **Not read:** the ECMA-424 edition of CycloneDX 1.7, because its host was not reachable from the drafting session. The SPDX 3.0.1 HTML specification was not read either; the RDF model is generated from the same source.
- **Formats not covered:** OSCAL, ReqIF, SysML v2 and SACM carry requirements natively (RPT-0005 §7, G10). Their mappings onto Requirement are ADR-0012 follow-up work, not part of #169.
- This note was drafted by an AI agent (Claude Code, claude-opus-5-5) in @Maimcghee's session and has not been reviewed by a human. Its design record is DL-0032.
