---
schema: "archdoc/v1"
id: DL-0032
title: "Requirement interchange mapping note, MAP-0002 (#169, deliverable 2)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-03"
updated: "2026-11-03"
record: DL-0032
bears_on: [DEC-001a, DEC-001b, DEC-002]
defers_to: ARCH-0001
---

# DL-0032: Requirement interchange mapping note (#169)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code (claude-opus-5-5) drafted it in @Maimcghee's session, as one agent with no subagents. It produced `spec/MAP-0002-requirement-interchange.md`. Issue: #169, deliverable 2 (parent #168).

## Question asked

#169 asks: "For each format, say how Requirement maps", for STIX 2.1, OTM, CycloneDX 1.7 and SPDX 3.0.1, with "what is lost" for each and "claims checked against the spec text". For CycloneDX it adds: "check whether `definitions.standards` and declarations/attestations carry requirements. Verify this against the spec; do not assume." The note is "a doc, not code", either a `spec/MAP-…` proposal or a section in an RPT-0005 follow-up. The student asked the agent to write it while #197 is in review.

## What was produced

- **`spec/MAP-0002-requirement-interchange.md`** (draft 0.1.0), with:
  - an overview table and a slot-by-slot table covering the 16 Requirement slots (ADR-0012's 14, plus `id` and `name`), plus `Mitigation.stated_as`, Assertion `confidence` and Review;
  - a section per format, each with an import line and a "what is lost" line;
  - five recommendations and four questions for the sponsor.

## How it was checked

Every claim was checked against a copy of the format's own specification or schema, read on 2026-11-03. Each copy's digest is in the note.

| Format | Copy | Checked |
|---|---|---|
| STIX 2.1 | The OASIS HTML. Its sha256 matches the library's `stix-2-1` record | The 19 SDO sections; §4.3 CoA, §4.13 Note and §4.15 Opinion properties; §5.1 `relationship_type`; §3.2 `confidence` and Appendix A's scale; §3.7 `derived-from`; §7.3 Extension Definition; §11's deprecation of custom objects |
| OTM 0.2.0 | `otm_schema.json` from the library's FX-1 record (same digest) | Top-level properties; `mitigations[]`, `threats[]`, `components[].threats[]` and their required fields; no "requirement" or "control" anywhere |
| CycloneDX 1.7 | `bom-1.7.schema.json` at tag `1.7` (commit `4b3f594`) | `definitions.standards[]`, its `requirements[]` and `levels[]`; `declarations` (assessors, attestations, claims, evidence, targets, affirmation); `citations`; `property` |
| SPDX 3.0.1 | `spdx-model.ttl` from spdx.org | `standardName` (on Artifact), `standardCompliance` (on AIPackage), `hasRequirement`, the relationship-type list (59 values, closed), `Annotation`, `Extension`, the software purposes `requirement` and `evidence`, and the security `ExternalRefType` values |

Every quotation in the note was copied from these files, not from memory.

## Choices the agent made, open to review

- **Placed in `spec/` as MAP-0002, status draft.** ADR-0007 says each import format "gets a `MAP-NNNN` crosswalk" and that additions arrive "as MAP-NNNN + a vector". MAP-0001 is the precedent for a draft mapping in `spec/`. An RPT-0005 section was the other option, but RPT-0005 0.5.0 has just been through its adversarial review. `spec/**` routes to @nymble.
- **One note across four formats, for one class.** ADR-0007's crosswalks are per format. This note covers only Requirement in each, so each format's own MAP can absorb its column later.
- **#169's "custom object" option is restated as an Extension Definition.** STIX 2.1 §11 deprecates custom objects in favour of §7.3.
- **The STIX `derived-from` direction is flagged, not resolved.** The specification's definition reads as the reverse of tmodel's `derived_from`. The note quotes it and leaves the choice to an exporter, rather than guessing what was intended.
- **CycloneDX conformance is routed to DEC-001b.** An attestation's conformance score is the R-042 verdict that ADR-0012 keeps out of the core.
- **The recommendations go no further than the evidence.** CycloneDX as the candidate format, no export to OTM or SPDX, and STIX only through an extension. Each is put as a sponsor question.

## What a human accepted

- The student asked for this note. Nothing in it has been reviewed yet.

## What was rejected, and why

- **Not used: the ECMA-424 edition of CycloneDX 1.7.** The library's `cyclonedx-1-7` record pins the ECMA-424 2nd edition PDF, but its host did not resolve from the drafting session. The agent did not try to work around the block. The CycloneDX JSON schema at the `1.7` tag was used instead, since the structural claims rest on it.
- **Dropped: a claim about what STIX bundles "in common use" carry.** It was not checked, so the note says only that STIX 2.1 defines no requirement object.
- **Narrowed: the RPT-0005 citation.** The first draft cited RPT-0005 §6 as saying every conversion drops review state. §6 says it about conversions between threat-model formats, so the note now says so.
