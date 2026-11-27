---
schema: "archdoc/v1"
id: DL-0011-review-catalogs-schema-285
title: "Catalogs-schema review-partner source checks (#285)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-26"
updated: "2026-11-26"
record: RPT-0014
issue: 285
defers_to: ARCH-0001
---

# Catalogs-schema source checks

Task: [#285](https://github.com/Threat-Radar/tmodel/issues/285). This records
source verification of the three calibration summaries on #228 at `0bb869b`
and the five-record sample from library#51 at `8fc3878`. It does not change
applicability judgments or grant human sign-off. Every sampled summary's
`reviewed_by` remains blank pending confirmation from @paria03.

## Calibration sample

Each PDF was downloaded from its recorded URL on 2026-11-26. All three hashes
match the records and manifest. Locators below refer to the pinned editions;
printed page numbers are distinguished from PDF page numbers.

| Record | Source checks | Result and limit |
|---|---|---|
| NIST AI 100-2 E2025 | Executive Summary: five classification axes. Body: 25 leaf ids; `.016` and `.017` occur in section 3.4.1, printed p. 51 / PDF p. 64. Sections 2.1.2, 3.2.3 and 4.2.1 name cryptographic mitigations; section 3.6 names Garak and PyRIT. | Supported. Rejoin line-broken `NIS` / `TAML` before counting. This is a taxonomy, not a product assessment. |
| Greshake et al., arXiv v2 | Section 4.2.3 and Fig. 6: a synthetic email application propagates an injected message. Section 4.2.4 and Fig. 8: stored memory reinfects a later session. Section 4.2.6: availability disruption, including a time-consuming task; section 5.2 limits the experimental claims. | Supported. Synthetic demonstrations and browser experiments do not establish the prevalence or success rate of deployed attacks. |
| BIML ARA v1.0 | Fig. 1 and the component sections: nine-component generic ML system. PDF p. 20: two distinct `inference:3` risks. PDF pp. 15, 18, 19 and 21: the four mislabeled references resolve by component and descriptor; the p. 15 and p. 21 instances are controls labels, not additional risk definitions. | Supported. Preserve the original ids and the source's stated 78 count alongside the 79-entry caveat. The sample does not turn this partial-read calibration into full extraction. |

Primary sources:

- [NIST AI 100-2 E2025](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf), SHA-256 `4811fb6ad73f9c9121843ab77e029b5adc6f2c86d33c2fc5b2099ef133847646`.
- [Greshake et al.](https://arxiv.org/pdf/2302.12173), SHA-256 `428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81`.
- [BIML ARA](https://berryvilleiml.com/results/ara.pdf), SHA-256 `247d7f06d8c768cc734dc84ab7004c6e4d645e91911af61002fd1743807ef312`.

The calibration catalog recount is 98 of 146 entries carrying a NISTAML id,
60 through AIT-075. Correct the stale lane-note bullet from four missing BIML
references to twelve. No calibration record, applicability rating or signature
is changed by that correction.

## Five-record library sample

The companion evidence is in library#51 at
`docs/catalogs-schema-review-285.md`. The sample comprises OCCULT, NCC's MATA
threat-model article, NCC's design-principles article, Cyber Centre
ITSAP.00.041, and OWASP NHI Top 10 2025. All five recorded capture hashes
match; the two NCC archives are hashed as their original compressed bytes.
Each record has at least three source checks with explicit locators.

This is five records, including two different publications behind S-0742.
It is not a source review of the other lane records or of all reference stubs.

## Corrections and validation

- Library#51's 256 new reference stubs have 261 reverse library `cited_by`
  links. Each already has the corresponding forward `cites` entry. Remove
  only those inverse links, following library `docs/references.md`; preserve
  all forward citations, record ids, hashes, owners and review states.
- Update the two affected source summaries' descriptions of that field.
- Correct the NCC design-principles summary's stale redirect claim: on
  2026-11-26 its recorded live article URL serves the article again. Retain
  the archived content URL and digest as the source pin.
- Run the library's CI steps locally while hosted Actions are paused. Keep
  local results separate from hosted CI, and verify tmodel's new-head CI.

## Human review boundary

The remaining #285 acceptance step is confirmation of these eight sampled
summaries by the designated review partner. Only then should the three
calibration and five library `reviewed_by` fields be populated. The issue
must remain open while those signatures are pending; neither a successful
automated check nor a PR approval substitutes for that human record.

Local checks: archdoc validates 28 documents with zero errors, and diff checks
pass. Companion library checks validate 967 records with zero errors and the
same 99 warnings; all YAML, requirement, artifact, bibliography and extraction
checks pass. Hosted checks are reported separately after pushing.
