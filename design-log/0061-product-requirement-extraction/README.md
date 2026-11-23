---
schema: "archdoc/v1"
id: DL-0061
title: "Product-side requirement extraction: ASVS 5, EU CRA Annex I and IEC 62443-4-1 (#171)"
type: process
status: draft
version: "0.8.0"
date: "2026-11-16"
updated: "2026-11-22"
record: DL-0061
bears_on: [DEC-001a, DEC-002, DEC-009, R-018]
defers_to: ARCH-0001
---

# DL-0061: Product-side requirement extraction (#171)

This is the AI-assisted design record for Phase 1 of #171, parent #168. Codex (GPT-5), working as one agent with no subagents, produced and corrected three core-model fragments in `research/0017-requirements-extraction/`. They contain 109 Requirements, 46 Assertions and 27 recorded human Reviews. Twenty-four Assertions are accepted with accepting Reviews; three proposed Assertions have rejecting Reviews; the remaining 19 Assertions have no Review.

Work was performed on branch `issue-171-product-requirements-extraction` in its existing isolated worktree, starting from `origin/main` commit `c467c93ac85274372bd9ac2d6fec0a5e7c935e0f`. The pinned library was read at `a28a01375814accc5fe10cb2f5e7083c7d0401a5`; its gitlink was not changed.

## Question asked

Issue #171 asks this lane to extract product-side requirements from OWASP ASVS 5.0.0, EU CRA Annex I Parts I and II, and the SR, SD, SI, SVV and DM practices of licensed IEC 62443-4-1:2018. Requirements must retain source identity, locator and normativity, use original paraphrases, and initially keep every agent-proposed relationship in an unreviewed Assertion until a human records a decision.

After the initial extraction, an independent audit required correction of relationship semantics, source fidelity, classifications, ASVS authentication coverage, source-reference documentation and the pending human-review packet. The correction pass re-examined all 69 original Assertions, not only the 30-item sample; this was quality control on agent output, not a human Review in the object model.

## Sources and provenance

| Record | State | Record content digest | Additional provenance used |
|---|---|---|---|
| `owasp-asvs-5` | distilled; free | `bcdbec214d70abcfad9284a31d4f9e5134305831d628aad3aa85d7e26626cb35` | ASVS 5.0.0 rows and composed legacy CWE mappings |
| `eu-cra-2024-2847` | distilled; EU law | `e3ecaabddf6e321fa04097d15dfcccc7309d0fe5896240ab7625a27d74ab1b0a` | Annex I atomic provisions in the pinned extraction; digest is the EUR-Lex PDF recorded at `content.sha256` in the pinned library record |
| `iec-62443-4-1-2018` | summarized; licensed | IEC preview `eb2f67981f03f944f8fe0044c6ac176b8f2422cb0473cc08c28d477cb3c52d03` | SDLA-312 v6.3 requirement descriptions, digest `fffdf0bc281370ff68129243fd15006ffa432ae5729fd18a205fa972c07772ab`; the paywalled IEC body was not read |

All files record a 2026-11-16 read date, the library pin and the human owner by GitHub id (`@kriishnaa-18`).

## Source-reference convention

Issue #171 and the RPT-0017 converter prescribe `library:<record>#<designator>`. The ASVS pinned extraction instead uses versioned row ids such as `owasp-asvs-5#v5.0.0-1.3.6`, while carrying `V1.3.6` as the unique human-facing designator. MAP-0001 generally uses the versioned row id.

This fragment retains the issue-prescribed designator alias in `source_ref`. Each alias was reconciled to exactly one pinned source row through that row's `designator`; the canonical versioned-row convention is disclosed in the ASVS file header. `P-10` already matches its canonical row id. No new identifier or schema field was invented. A future architecture decision may standardize aliases versus canonical row ids.

## Extraction decisions and accounting

### OWASP ASVS 5

**461 available, 34 converted, 427 skipped.**

The converted set contains all 13 Level 1 V6 requirements, V6.1.3 and V6.3.4 because they directly govern multiple authentication pathways and carry source-backed inferred CWE-306 mappings, and the original XML/XXE, SSRF/outbound-access and file-handling selection. The skips are 395 non-V6 entries outside the threat/file scope and 32 remaining V6 Level 2/3 entries outside the selected baseline and pathway controls.

Every selected row is paraphrased. Of the original 27 CWE Assertions, seven semantically indirect mappings were removed; two CWE-306 Assertions were added with the new pathway requirements. The final file contains **22 Assertions**: 9 accepted and 13 proposed, including one with a rejecting Review. All retained mappings occur on the pinned source row and remain medium confidence because the source labels them inferred legacy mappings. No CAPEC mapping is proposed.

### EU CRA Annex I

**191 available, 23 converted, 168 skipped.**

All 14 Part I and all 9 Part II entries are converted, including the optional justified-delay provision. Part II(8) now preserves the source's specific no-charge exception for an agreement between a manufacturer and business user concerning a tailor-made product. Part II(3) is a developer process rather than an independent audit.

Two coequal legal duties formerly linked with `derived_from` were removed because timing, overlap or operational dependency does not establish derivation. The generic attack-surface-to-XXE proposal was also removed because no product-specific design evidence shows that the legal requirement counters that path. The final file contains **7 accepted Assertions**, each with an accepting human Review.

### IEC 62443-4-1:2018

**84 available, 52 converted, 32 skipped.**

All normative SR, SD, SI, SVV and DM entries are converted: 15 SR, 7 SD, 5 SI, 13 normative SVV and 12 DM entries. The 31 SM, SUM and SG entries are outside scope; `SVV-5.levels` is a definition rather than a Requirement.

Every `name` and `text` is original project wording. SD-2.2 now describes per-layer secure design and the objective of reducing subsequent-layer exposure without promising absolute protection. DM-4.residual limits reason/risk recording to deferral. Routine development reviews and penetration testing are `process`; only SVV-5 remains `audit` because its source expressly requires tester independence. SD-4.e is a design activity and is `process`.

Suffixes such as `SR-2.review`, `SD-2.2` and `DM-4.residual` are atomic split identifiers defined by the pinned library extraction, not standalone native IEC designators. Their `source_locator` preserves the native clause. The normative IEC body remained unavailable; fidelity was checked against the disclosed SDLA-312 material and IEC preview only.

Twelve unsupported `derived_from` proposals and all three abstract process-to-product-threat `addresses` proposals were removed. Two derivations remained for human review: SD-2 based on the SR-2 threat-model output, and DM-4 based on DM-3 assessment results. Both are now rejected because dependency on an output does not establish Requirement-to-Requirement derivation. Of the fifteen atomic child/detail `refines` Assertions, eight are accepted and seven remain unreviewed. The final file therefore contains **8 accepted and 9 proposed Assertions**, including the two with rejecting Reviews.

## Requirement-kind correction decisions

| Requirement | Final kind | Reason |
|---|---|---|
| CRA Part II(3) | `process` | Regular testing/review is an activity; the source does not require an independent assessor. |
| IEC SR-2.review | `process` | The development team performs the review, so it is not independent. |
| IEC SD-4.e | `process` | The obligation is to apply attack-surface reduction as a design practice, not a standalone product property. |
| IEC SVV-4 | `process` | Penetration testing is required, but independence is not required by this row. |
| IEC DM-6 | `process` | The row requires periodic internal process assessment without an independence condition. |
| IEC DM-6.annual | `process` | This is the frequency refinement of DM-6. |
| IEC SVV-5 | `audit` | Retained as audit because tester independence is explicit. |

## Relationship methodology after correction

- `derived_from` means the subject Requirement was genuinely derived from the target Requirement or from the output its satisfaction necessarily produces. Alignment, review criteria, cross-references, temporal ordering and generic dependency are insufficient.
- `refines` is used only when an atomic child statement narrows, enumerates or adds detail to a broader parent with the same intent.
- `addresses` means the Requirement itself counters the target. A generic development practice is not asserted to address a product-specific threat without product-specific evidence.
- Direct Requirement relationship slots and `Mitigation.stated_as` remain empty.
- Every retained link has confidence and source-grounded `Basis:` text. An Assertion is `accepted` only when a justified human accepting Review records that decision; rejected and unreviewed Assertions remain `proposed`.
- No `maps_to` relation crosses records, and accepting an Assertion does not populate a direct relationship slot.

## Assertion changes made by the correction pass

### Added

| Assertion | Reason |
|---|---|
| `assertion:owasp-asvs-5-v6-1-3--addresses--cwe-306` | Source-backed inferred mapping for documentation of every authentication pathway and consistent control strength. |
| `assertion:owasp-asvs-5-v6-3-4--addresses--cwe-306` | Source-backed inferred mapping for implementation consistency across authentication pathways. |

### Removed from ASVS

| Assertion | Reason omitted |
|---|---|
| `assertion:owasp-asvs-5-v5-3-1--addresses--cwe-552` | Preventing server-side execution of an upload does not directly counter the broader externally accessible file/directory weakness. |
| `assertion:owasp-asvs-5-v6-1-1--addresses--cwe-307` | Documentation of abuse controls is not itself the implemented countermeasure. |
| `assertion:owasp-asvs-5-v6-2-2--addresses--cwe-620` | Merely enabling password change does not ensure that the change is verified; V6.2.3 carries the direct control. |
| `assertion:owasp-asvs-5-v6-2-5--addresses--cwe-521` | Permitting arbitrary character composition is not independently a password-strength control. |
| `assertion:owasp-asvs-5-v6-2-7--addresses--cwe-521` | Password-manager and paste support is beneficial but only indirectly related to password strength. |
| `assertion:owasp-asvs-5-v6-3-2--addresses--cwe-798` | A default account does not necessarily contain a hard-coded credential. |
| `assertion:owasp-asvs-5-v13-2-4--addresses--cwe-732` | Treating an outbound resource allowlist as permission assignment is too indirect for `addresses`. |

### Removed from CRA

| Assertion | Reason omitted |
|---|---|
| `assertion:cra-partii-2--derived-from--parti-2-c` | Coequal update obligations overlap but the subject is not derived from the target. |
| `assertion:cra-partii-4--derived-from--partii-2` | Availability of an update triggers disclosure timing but does not derive the disclosure Requirement. |
| `assertion:cra-parti-2-j--addresses--xxe-file-read` | Generic attack-surface reduction lacks a product-specific control showing that it counters the XXE path. |

### Removed from IEC

| Assertions | Reason omitted |
|---|---|
| `iec-sr-2-issues--derived-from--dm-3`, `iec-sr-2-issues--derived-from--dm-4` | SR-2 routes issues into those processes; process use is not Requirement derivation. |
| `iec-sr-5--derived-from--sr-2` | Alignment with a threat model is not derivation. |
| `iec-sd-1--derived-from--sr-1`, `iec-sd-1--derived-from--sr-2` | Security context and threat-model artifacts are design inputs, not source Requirements from which SD-1 is derived. |
| `iec-sd-3--derived-from--sr-3`, `iec-sd-3--derived-from--sd-1`, `iec-sd-3--derived-from--sd-4` | These are design-review criteria. |
| `iec-si-1--derived-from--sr-3`, `iec-si-1--derived-from--si-2` | These are implementation-review criteria. |
| `iec-svv-2--derived-from--sr-2` | Tests use threat-model content, but the Requirement is not derived from the SR-2 Requirement itself. |
| `iec-dm-5--derived-from--dm-4` | Reportability is a process input; that dependency does not establish Requirement derivation. |
| `iec-sd-1--addresses--xxe-file-read`, `iec-sd-1--addresses--imds-pivot`, `iec-sd-2--addresses--remote-diag-injection` | Abstract lifecycle practices do not directly counter a particular product threat without implementation/applicability evidence. |

No removed proposal is recorded as a human rejection. These are corrections to agent-generated hypotheses.

## Human-review record and pending checklist

The checklist contains ten ASVS candidates, all seven retained CRA candidates, and ten representative IEC candidates. Advisory recommendations are not Review decisions. The ASVS rows record nine acceptances and one rejection; all seven CRA rows record acceptances; and the IEC rows record eight acceptances and two rejections. The YAML files, rather than this table, are the authoritative Review records.

### OWASP ASVS 5 — 10 of 22 retained Assertions

| Assertion | Source → predicate → target | Exact locator | Evidence | Limitation | Advisory recommendation | Human decision | Human justification |
|---|---|---|---|---|---|---|---|
| `assertion:owasp-asvs-5-v1-3-6--addresses--cwe-918` | `requirement:owasp-asvs-5-v1-3-6` → `addresses` → `weakness:cwe-918` | V1.3 Sanitization, row 1.3.6 (PDF p.27) | Source row explicitly counters SSRF with request-target constraints and maps to CWE-918. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Restricting outbound request destinations directly mitigates SSRF; the mechanism supports the inferred legacy mapping. |
| `assertion:owasp-asvs-5-v1-5-1--addresses--cwe-611` | `requirement:owasp-asvs-5-v1-5-1` → `addresses` → `weakness:cwe-611` | V1.5 Safe Deserialization, row 1.5.1 (PDF p.28) | Disabling external-entity resolution directly counters XXE. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Disabling unsafe XML external-entity processing directly mitigates the same underlying XXE mechanism. |
| `assertion:owasp-asvs-5-v1-5-3--addresses--cwe-436` | `requirement:owasp-asvs-5-v1-5-3` → `addresses` → `weakness:cwe-436` | V1.5 Safe Deserialization, row 1.5.3 (PDF p.29) | Consistent parser interpretation directly addresses the row's mapped interpretation conflict. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Consistent parser interpretation addresses the relevant subset of CWE-436 without claiming complete coverage. |
| `assertion:owasp-asvs-5-v5-2-2--addresses--cwe-434` | `requirement:owasp-asvs-5-v5-2-2` → `addresses` → `weakness:cwe-434` | V5.2 File Upload and Content, row 5.2.2 (PDF p.43) | Extension and content validation counters unsafe file-type upload. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Extension and content validation partially mitigates acceptance of dangerous or disguised file types. |
| `assertion:owasp-asvs-5-v5-2-5--addresses--cwe-61` | `requirement:owasp-asvs-5-v5-2-5` → `addresses` → `weakness:cwe-61` | V5.2 File Upload and Content, row 5.2.5 (PDF p.43) | Rejecting or constraining archive symlinks counters unsafe link following. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT — WITH QUALIFICATIONS | The control partially mitigates unsafe symbolic-link following in applicable UNIX-like environments; it does not imply complete weakness elimination or universal platform applicability. |
| `assertion:owasp-asvs-5-v5-3-2--addresses--cwe-73` | `requirement:owasp-asvs-5-v5-3-2` → `addresses` → `weakness:cwe-73` | V5.3 File Storage, row 5.3.2 (PDF p.44) | Trusted path construction counters external control of file paths. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Trusted construction and strict validation partially mitigate attacker control over file paths; inferred mapping provenance acknowledged. |
| `assertion:owasp-asvs-5-v6-1-3--addresses--cwe-306` | `requirement:owasp-asvs-5-v6-1-3` → `addresses` → `weakness:cwe-306` | V6.1 Authentication Documentation, row 6.1.3 (PDF p.46) | The row requires every authentication pathway and its controls to be documented and carries CWE-306. | Documentation governs but does not implement authentication; mapping is inferred legacy. | NEEDS FURTHER EVIDENCE | REJECT | Documentation does not independently enforce authentication; the relationship is too indirect without more evidence, while V6.3.4 is implementation-focused. |
| `assertion:owasp-asvs-5-v6-3-4--addresses--cwe-306` | `requirement:owasp-asvs-5-v6-3-4` → `addresses` → `weakness:cwe-306` | V6.3 General Authentication Security, row 6.3.4 (PDF p.48) | The row requires no undocumented authentication path and consistent enforcement across paths. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Consistent enforcement across all pathways partially mitigates missing authentication, including overlooked or alternative paths. |
| `assertion:owasp-asvs-5-v6-3-1--addresses--cwe-307` | `requirement:owasp-asvs-5-v6-3-1` → `addresses` → `weakness:cwe-307` | V6.3 General Authentication Security, row 6.3.1 (PDF p.47) | Implemented credential-stuffing and brute-force controls directly limit authentication abuse. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Implemented credential-stuffing and brute-force defenses mitigate excessive attempts without implying complete prevention. |
| `assertion:owasp-asvs-5-v13-2-5--addresses--cwe-918` | `requirement:owasp-asvs-5-v13-2-5` → `addresses` → `weakness:cwe-918` | V13.2 Backend Communication Configuration, row 13.2.5 (PDF p.80) | Server request-target allowlisting directly constrains SSRF. | Composed legacy mapping, labelled inferred. | ACCEPT | ACCEPT | Destination allowlisting mitigates SSRF while other mechanisms may require additional safeguards; inferred mapping provenance acknowledged. |

### EU CRA — all 7 retained Assertions

| Assertion | Source → predicate → target | Exact locator | Evidence | Limitation | Advisory recommendation | Human decision | Human justification |
|---|---|---|---|---|---|---|---|
| `assertion:cra-partii-7--refines--parti-2-c` | Part II(7) → `refines` → Part I(2)(c) | Annex I, Part II, point (7) | Adds secure distribution detail to the broader update capability. | Agent-inferred same-source refinement. | ACCEPT | ACCEPT | Secure distribution gives more specific support to the shared update objective without changing either provision's independent obligations or applicability. |
| `assertion:cra-partii-8--refines--parti-2-c` | Part II(8) → `refines` → Part I(2)(c) | Annex I, Part II, point (8) | Adds timing, charge-exception and advisory detail to update delivery. | Agent-inferred same-source refinement. | ACCEPT | ACCEPT | Prompt distribution, user guidance, and the qualified free-update duty refine the shared objective without implying identical legal scope or override. |
| `assertion:cra-partii-4-delay--refines--partii-4` | Part II(4)-delay → `refines` → Part II(4) | Annex I, Part II, point (4), after semicolon | The source states this conditional exception inside the same disclosure provision. | Atomic split introduced by the pinned extraction. | ACCEPT | ACCEPT | The source expressly qualifies the same disclosure duty; `refines` approximates the narrower exception while preserving its conditions and the underlying duty. |
| `assertion:cra-partii-6--refines--partii-5` | Part II(6) → `refines` → Part II(5) | Annex I, Part II, point (6) | Reporting contact and information sharing add detail to coordinated disclosure. | Agent-inferred same-source refinement. | ACCEPT | ACCEPT — WITH QUALIFICATIONS | Reporting channels operationalize coordinated disclosure, supported by Annex II point (2) and Recital 76; the edge does not claim legal subordination, complete containment, or loss of either independent duty. |
| `assertion:cra-parti-2-d--addresses--cwe-306` | Part I(2)(d) → `addresses` → `weakness:cwe-306` | Annex I, Part I, point (2)(d) | Authentication and comparable access controls counter missing authentication. | CWE target comes from illustrative mvp-02, not the regulation. | ACCEPT | ACCEPT | Authentication and access controls directly counter missing authentication; this is an analytical CWE mapping, not a mapping stated by EU law or a compliance conclusion. |
| `assertion:cra-parti-2-d--addresses--remote-diag-injection` | Part I(2)(d) → `addresses` → `threat-instance:remote-diag-injection` | Annex I, Part I, point (2)(d) | Unauthorized-access controls counter the vector's unauthenticated command path. | Product threat comes from illustrative mvp-02. | ACCEPT | ACCEPT | Unauthorized-access protection addresses the unauthenticated diagnostic-command path; this is a product-specific analytical mapping, not a claim that the CRA identifies the threat. |
| `assertion:cra-parti-2-f--addresses--remote-diag-injection` | Part I(2)(f) → `addresses` → `threat-instance:remote-diag-injection` | Annex I, Part I, point (2)(f) | Command-integrity protection counters unauthorized command injection. | Product threat comes from illustrative mvp-02. | ACCEPT | ACCEPT | Protection against unauthorized manipulation of commands addresses the injection mechanism; this is an analytical mapping to the illustrative threat, not an explicit CRA relationship. |

### IEC 62443-4-1 — 10 of 17 retained Assertions

All IEC rows below inherit the limitation that clause identities come from the IEC preview and wording was assessed through SDLA-312 rather than the paywalled normative body.

| Assertion | Source → predicate → target | Exact locator | Evidence | Limitation | Advisory recommendation | Human decision | Human justification |
|---|---|---|---|---|---|---|---|
| `assertion:iec-sd-2--derived-from--sr-2` | SD-2 → `derived_from` → SR-2 | IEC 62443-4-1:2018 §7.3.1; SDLA-312 p.12 | Layered defense is expressly based on the threat-model output. | Secondary wording; target is the Requirement that produces the artifact. | ACCEPT | REJECT | Dependence on SR-2's threat-model output does not establish that the SD-2 Requirement is derived from the SR-2 Requirement. |
| `assertion:iec-dm-4--derived-from--dm-3` | DM-4 → `derived_from` → DM-3 | §10.5.1; SDLA-312 p.20 | Disposition and reportability are expressly based on DM-3 assessment results. | Secondary wording. | ACCEPT | REJECT | Operational dependence on assessment results produced under DM-3 does not establish Requirement-to-Requirement derivation. |
| `assertion:iec-sd-2-2--refines--sd-2` | SD-2.2 → `refines` → SD-2 | §7.3.1; SDLA-312 p.12 | Atomic child adds responsibility assignment and per-layer secure design. | SD-2.2 is a library split id, not a native designator. | ACCEPT | ACCEPT | Adds responsibility assignment within the broader layered-defense process. |
| `assertion:iec-sd-4-e--refines--sd-4` | SD-4.e → `refines` → SD-4 | §7.5.1; SDLA-312 p.13 | Attack-surface reduction is one enumerated SD-4 design practice. | SD-4.e is a library split id. | ACCEPT | ACCEPT | Attack-surface reduction is a specific secure-design practice under SD-4. |
| `assertion:iec-si-1-sca-tool--refines--si-1` | SI-1.sca-tool → `refines` → SI-1 | §8.3.1; SDLA-312 p.14 | Adds the available-tool condition to static analysis. | Library split id; secondary wording. | ACCEPT | ACCEPT | Specifies tool-based static analysis within the broader SI-1 implementation-review process. |
| `assertion:iec-svv-1-types--refines--svv-1` | SVV-1.types → `refines` → SVV-1 | §9.2.1; SDLA-312 p.16 | Enumerates the test categories used to satisfy SVV-1. | Library split id; secondary wording. | ACCEPT | ACCEPT | Specifies categories of security verification testing. |
| `assertion:iec-svv-2-activities--refines--svv-2` | SVV-2.activities → `refines` → SVV-2 | §9.3.1; SDLA-312 p.16 | Adds confirmation and attempted defeat of each mitigation. | Library split id; secondary wording. | ACCEPT | ACCEPT | Details testing activities that verify mitigation effectiveness. |
| `assertion:iec-svv-3-known--refines--svv-3` | SVV-3.known → `refines` → SVV-3 | §9.4.1; SDLA-312 p.17 | Specifies the information source used for known-vulnerability testing. | Library split id; secondary wording. | ACCEPT | ACCEPT | Specifies the use of established vulnerability-information sources. |
| `assertion:iec-svv-3-d--refines--svv-3` | SVV-3.d → `refines` → SVV-3 | §9.4.1; SDLA-312 p.17 | Makes executable software-composition analysis part of SVV-3. | Library split id; secondary wording. | ACCEPT | ACCEPT | Specifies executable software-composition analysis as part of vulnerability testing. |
| `assertion:iec-dm-6-annual--refines--dm-6` | DM-6.annual → `refines` → DM-6 | §10.7.1; SDLA-312 p.21 | Adds the annual minimum frequency to the periodic DM-6 review. | Library split id; secondary wording. | ACCEPT | ACCEPT | Adds a minimum annual review frequency to the broader periodic process-review requirement. |

## GUI implementation

The second #171 delivery adds a dedicated Requirements view without changing any extraction object or human Review. It was implemented after rebasing the extraction commit onto `856886fa2adb86ecc8a9573e46c710d8d29642ec`, with the repository library gitlink still at `e4068272cec52a92b4414ea2a88a23b7125ce79d`.

### Requirements table and inspector

The frontend reads the existing storage-neutral `/graph` response and derives a Requirement catalog for the selected example model. The table exposes stable id and name, kind, normativity, source reference and locator, applicable product, and recorded satisfaction. Search includes ids, names, statements and source fields; kind and product filters, deterministic column sorting, page sizes and next/previous controls operate client-side over that model graph.

Applicability is shown only from an authored relationship, a justified human-accepted Assertion, or a recorded `applies_to_family` match against the Product classification. Satisfaction is shown only from established `satisfied_by` links and the target Mitigation's recorded status. A proposed scope or satisfaction Assertion is visible in the inspector but does not affect the table result. Requirements with no applicable Product or no satisfying Mitigation say “Not recorded” rather than receiving an inferred value.

The accessible row inspector preserves the full statement, description, text origin, source identity and locator, scope, Product matches, Mitigation evidence, directed relationships, Assertion ids/status/confidence/evidence, and available Review ids/status/justification. Loading, empty, error and retry states use the established Library-view patterns; the navigation remains keyboard-operable and URL-hash-addressable.

### Knowledge-graph projection

The engine projection now treats all ADR-0012 Requirement references as edges: `addresses`, `stated_as`, `satisfied_by`, `refines`, `derived_from`, `conflicts_with`, `maps_to`, and `applies_to`. This removes those reference slots from node properties while retaining their schema direction. Every graph edge has an explicit `authored` provenance flag and an ordered `assertions` collection. Each collection entry preserves that Assertion's own status, confidence, description, evidence and Reviews, so coalescing equal subject/predicate/object triples cannot overwrite one Assertion with another or present an aggregate verdict as every Assertion's verdict. Legacy summary properties remain only for conservative graph styling; a multi-Assertion edge deliberately has no singular assertion or Review status.

Authored provenance and Assertion provenance are independent. A directly authored triple remains established if a proposed or rejected Assertion names the same triple. An Assertion-only triple becomes established only when its own Assertion is accepted and every recorded human Review accepts it with a nonblank justification. The frontend fallback and Requirement catalog use these rules independently per Assertion; hypothetical results are calculated from the authored-plus-validly-accepted baseline.

Requirement nodes have a distinct cyan node color and a legend entry. Existing relationship review-state rendering remains authoritative: structural and accepted links are solid, while proposed, changes-requested, rejected and unknown links use their distinct dashed styles. The graph and Requirements inspector display the status and provenance but never mutate an Assertion or populate a direct slot.

### Coverage contract and interim fallback

The coverage client implements the exact response shape documented and tested by open PR #243: product scope, Requirement rows and counts, Mitigation evidence, unaddressed threats, excluded Assertions, separate proposals, and individual and joint `if_accepted` hypotheticals. A valid `/coverage` response is parsed before display. Any malformed response or non-404 engine failure stays visible.

Because #243 is not merged, only HTTP 404 activates the temporary read-only frontend fallback. The fallback applies #243's conservative rules to the same graph: scope closure from Product composition, family applicability, complete/in-progress Mitigation status, and accepted Assertion use only when a human Party has an accepting Review with a nonblank justification. Proposed links are held apart and evaluated as counterfactual additions, never established coverage. Both the panel and response interpretation state that this is recorded evidence, not verified regulatory compliance.

The Pages build uses `StaticPreviewApi`; `/coverage` intentionally returns 404 there and the fallback reads the already-published model graph, so it makes no localhost request. The desktop uses the live endpoint as soon as #243 lands without a frontend branch change. Removing the fallback can be considered after the published preview gains a generated coverage snapshot.

### Integration and tradeoffs

- The three signed-off #171 commits were rebased onto `c29f9e99f83cb0c2542ef8128e08fe085a8b1c70`, which contains merged PR #250. Conflicts in `index.html`, `app-navigation.ts`, `app-navigation.test.ts`, `main.ts` and `styles.css` were resolved by retaining both independently initialized table views, both URL-hash routes and engine-state paths, and both responsive/dark-mode style sets. The combined `AppView` union and navigation tests include both `requirements` and `weaknesses`.
- PR #250 and #171 had each supplied one side of an alternative HTML panel block. Retaining both alternatives initially left their shared closing tags ambiguous; the integration correction closes the Weaknesses inspector/workspace/panel before opening the Requirements panel. A focused application-shell regression checks both reciprocal tab/panel ARIA mappings, their sibling boundary, and uniqueness of every HTML id.
- Generated Pages HTML, JavaScript and CSS conflicts were used only as temporary rebase placeholders. `docs/publishing/render_app.py` then removed obsolete assets and generated one bundle from the integrated source with all nine current example models and both table views.
- PR #243 will add the real backend route and may conflict only if its response contract changes. The provider deliberately does not copy that backend implementation; it can be switched from fallback to the endpoint by merging #243 unchanged under the inspected contract.
- The published graph JSON for every example changes because direct Requirement references and richer Assertion/Review provenance are now projected consistently. These are generated artifacts owned by `docs/publishing/render_app.py`, not hand edits.
- Coverage is model-local. The three research extraction fragments remain standalone evidence and are not silently assigned to a Product or inserted into an example model.

### Final independent-review corrections

The final independent review found three presentation-layer defects; no extraction object, Assertion decision, Review, or library pin changed while correcting them:

- A direct authored graph relationship now keeps its neutral solid primary line even when proposed, rejected, disputed, or mixed-state Assertions name the same triple. The inspector continues to display every Assertion and Review independently. Assertion-only edges retain their accepted, proposed, rejected, changes-requested and unknown styling. Multiple Assertions with the same state receive a count label without borrowing one Assertion's raw status fields; differing states are explicitly labelled mixed.
- Successful `/coverage` responses are rejected when their totals contradict `count`, their status counts contradict the Requirement rows, Requirement or proposal ids repeat, any individual or joint hypothetical is inconsistent, or the returned Product/model filename does not match the request. Such failures remain visible and never trigger the 404-only fallback. The valid response produced by PR #243 remains accepted without adding mandatory fields.
- The Requirements inspector now prefers structured per-Assertion provenance and uses legacy summary fields only when structured provenance is absent. Descriptions, evidence and Reviews therefore appear once, while reviewer ids and justifications remain visible and multiple Assertions stay separate.

Fourteen regression cases cover the three corrections, including actual Cytoscape edge data and style precedence, authored-plus-proposed/rejected triples, Assertion-only states, mixed and matching multi-Assertion edges, contradictory baseline and hypothetical coverage answers, duplicate ids, response identity, and single/multiple inspector provenance.

### GUI verification

- Frontend after PR #250 integration: TypeScript typecheck passed; 456 tests passed across 40 files; the production Vite 8.3.8 build passed. The combined suite includes the Requirements behavior below, PR #250's Weaknesses contract/view/indentation/accessibility regressions, navigation between both routes, and the two application-shell coexistence checks.
- Engine: Ruff check and format check passed; 614 tests passed and 7 packaging-dependent tests skipped. Projection tests cover every ADR-0012 direct relationship, authored provenance, independent evidence for multiple Assertions sharing an edge, and both accepted and proposed Assertion-backed relationships with source/Review metadata.
- Publishing: the 14 app publishing/link/identity tests passed; `render_app.py --check` passed for 9 models and 685 library records; 707-page relative-link validation passed; the identity guard checked 758 files with 6 protected identities enforced; architecture-document validation found 28 documents and 0 errors.
- Both desktop and Pages builds emit the existing non-failing warning that the main JavaScript chunk exceeds Vite's 500 kB recommendation. No new dependency or remote asset was introduced.

## Validation

The corrected files were checked with the repository commands and the pinned LinkML 1.12.1 tools:

```sh
linkml-validate -s spec/vectors/example-container-core.linkml.yaml -C ExampleModelCore \
  research/0017-requirements-extraction/<record-id>.yaml
python3 design-log/0021-mvp-core-attack-path-vectors/check-edges.py \
  research/0017-requirements-extraction/<record-id>.yaml
python3 research/0017-requirements-extraction/check.py \
  research/0017-requirements-extraction/<record-id>.yaml
python3 -B research/0017-requirements-extraction/test_convert.py
bin/gen-schema --check
bin/validate-archdoc
(cd library && bin/validate)
```

Results after correction:

- LinkML: the three #171 files pass with no issues.
- Edge integrity: the three corrected files contain 206 objects and 146 id references; all resolve (ASVS 86/64, CRA 40/28, IEC 80/54).
- Extraction rules: all three files pass; they contain 34, 23 and 52 Requirements.
- Source reconciliation: every selected designator resolves to exactly one pinned row, every locator matches, mapped normativity agrees, and counts reconcile.
- Assertion governance: 24 of the 46 retained Assertions are `accepted`, each with an accepting human Review; 22 remain `proposed`. Three proposed Assertions have rejecting Reviews and 19 Assertions are unreviewed. No direct relationship slot is populated.
- IEC copy check: the longest contiguous shared run remains five words, consisting of generic or enumerated technical phrases.
- Converter tests: 9 passed.
- Architecture-document validation after the DL-0061 rename: 28 documents, 0 errors.
- The earlier correction pass additionally reported the generated schema current, the pinned library at 550 records with 0 errors and 122 pre-existing warnings, and clean whitespace/final-newline checks; those broader checks were not needed to recompute the three-file figures above.

Passing automated checks establishes structural consistency only; it does not accept any source-derived relationship.

## Open questions and limitations

1. ASVS designator aliases follow Issue #171 and the converter, while canonical pinned row ids are versioned. Both are traceable, but the repository does not yet have one enforced convention.
2. ASVS CWE mappings are inherited legacy mappings and retain that provenance despite being present in the library record. Nine are accepted by recorded human Reviews, one is rejected and remains proposed, and twelve remain proposed without a Review.
3. CWE stub names remain identifiers except where a readable title already exists in the repository. No unverified canonical titles were invented.
4. CRA Part I point (2) applicability is conditional on the manufacturer's risk assessment, while the pinned library classifies the provisions as requirements; the extraction preserves source normativity and states the condition in the text.
5. The IEC normative body was unavailable. Clause locations come from the IEC preview and requirement descriptions from SDLA-312.
6. The fragments are standalone research evidence. They are not assigned to a Product and are not automatically part of an approved `spec/vectors` model.

## What a human accepted

- The implementation plan and Phase 1 correction scope were approved before work began.
- Nine ASVS `addresses` Assertions, all seven CRA Assertions and eight IEC `refines` Assertions are accepted by recorded Reviews from `@kriishnaa-18`, each with a justification. The exact decisions and qualifications appear in the review tables above and in the YAML `reviews` collections.
- No extracted Requirement text, requirement classification, unreviewed relationship or Assertion confidence is thereby accepted; the Reviews decide only the Assertions they name.

## What a human rejected, and why

- `assertion:owasp-asvs-5-v6-1-3--addresses--cwe-306` is rejected by a recorded Review because documenting authentication pathways does not itself enforce authentication, making the relationship too indirect without further evidence. The Assertion remains `proposed`, as required for a rejected proposal.
- `assertion:iec-sd-2--derived-from--sr-2` is rejected because dependence on threat-model output does not establish derivation from the SR-2 Requirement.
- `assertion:iec-dm-4--derived-from--dm-3` is rejected because using DM-3 assessment results is an operational dependency, not Requirement-to-Requirement derivation.
- Twelve ASVS Assertions and seven IEC Assertions remain without a formal Review. CRA has no unreviewed Assertion, and the IEC ten-link human-review sample required by #171 is complete.
