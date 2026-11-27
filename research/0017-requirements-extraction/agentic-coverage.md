# Agentic requirement extraction accounting (#170)

Read 2026-11-14. All four fragments originated as **AI-proposed extractions**. All four samples now have 40 recorded human decisions: 39 acceptances and one rejection (O09); no sample decisions remain pending. No product applicability or mitigation completion is inferred from that acceptance. Source locator paths are not invented standard clause numbers.

| Record | Source units | Converted Requirements | Skipped | Extracted Assertions |
|---|---:|---:|---|---:|
| `csa-maestro-2025` | 18 | 24 | 0 mitigation blocks; one layer umbrella becomes seven authored instances | 24 |
| `sp-800-218a` | 168 | 81 | 87 entries (listed below) | 12 |
| `owasp-agentic-threats-mitigations-v1-1` | 105 | 105 | 0 top-level bullets; one repeated source bullet retained | 105 |
| `mcp-spec-security-best-practices` | 34 | 34 | 0 uppercase MUST/SHOULD clauses | 34 |

## Provenance and scope

The source records and existing NIST extraction were read at merged library commit `e4068272cec52a92b4414ea2a88a23b7125ce79d`. After #200 merged, this branch inherited that same application pin and the refreshed public library from `main`; all four `library:<id>` references now resolve in the pinned submodule. The prior pin `a28a013` lacked **two** of these records (MCP and OWASP), not three. This change authors no library record and does not republish the library separately.

Display names now use whole-word short titles with an ellipsis when abbreviated. NIST's native designators remain unchanged in `source_ref`. MAESTRO, OWASP and MCP have no native requirement designators for these provisions, so their URI fragments now use each existing Requirement ID's local slug. The source heading/clause paths remain unchanged in `source_locator`; the slugs are not source-issued clause numbers or website anchors. Requirement IDs, full paraphrases, normativity and proposed link IDs are unchanged.

- [MAESTRO, Cloud Security Alliance](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro): HTML capture SHA-256 `10cb6b7964fb514b19c429b1461724741de31dde683c2da9e85c3cb642a233e4`; library record has no digest. Count ten §3.2 C mitigation blocks (one layer umbrella, four cross-layer, five AI-specific) and eight §4 architecture-pattern mitigation blocks. Represent all 18 as 24 Requirements by expanding only the umbrella into seven **authored** layer instances; these contain no invented concrete security techniques. Source principles, threat descriptions, procedural modeling steps and examples are contextual material outside that denominator.
- [NIST SP 800-218A](https://doi.org/10.6028/NIST.SP.800-218A): reuse the existing `distilled/requirements.yaml`, source PDF digest `e088c8bc75716824dae7c36a987f408364638561d381ed001b5c12254a7b10d8`; no fresh PDF extraction or binary digest check. Include 59 native R recommendations, 16 C considerations, and six explicitly new tasks. Preserve native designators and locator strings. Map recommendations to `recommended`; map considerations to recommendations to **evaluate**, keeping their weaker meaning in the text. Skip 11 informative notes, 14 governing prose entries and 62 baseline/overview practice or task entries. Source entries are not all tasks: its 168 entries include practices, tasks, additions and prose.
- [OWASP GenAI Security Project, Agentic AI - Threats and Mitigations v1.1](https://genai.owasp.org/download/45674/?tmstv=1739819891): December 2025, 53-page PDF, read official extracted PDF text. The library records binary digest `65e3bd59f99c411b055c6caf2bac96ab361dff8c010e4bef532a593ce10345ff`; it was **not reverified** because a direct download returned an HTML consent page. Coverage is all 105 top-level bullets in six playbooks, printed pp. 35–42 (PDF pages 36–43), representing 104 distinct texts; Playbook 2 / Step 3 repeats its last bullet. Nested examples/constraints are incorporated in parent paraphrases, not counted independently. The fragment is an adaptation under [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/); retain its attribution and license when redistributing.
- [MCP Security Best Practices, dated endpoint](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices): HTML capture SHA-256 `0d944ee66f3519ce2e9513d226e8849e5e0f2acd135f06f70b31cdfb014ead23`, distinct from record digest `95beaace4d676d89e92d94751bab1ad4c9870e1458bc5f6f7eae8dd8bbc75bec`. The endpoint is dated but mutable; these are different byte captures, not proof that the historical text is identical. Extract 21 uppercase MUST/MUST NOT and 13 SHOULD occurrences as 34 clauses (including list-introducing clauses and normative children). The scope-minimization section contains lowercase advice and MAY, outside this issue’s MUST/SHOULD scope; attack-flow examples, DNS prose and resources are also outside the clause denominator. The [official release-tag source](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/2025-11-25/docs/specification/2025-11-25/basic/security_best_practices.mdx) was cross-checked, but has fewer sections than this dated endpoint; do not substitute it or the living draft for this capture.

No normalized `applies_to_family` value is inferred from an article’s audience. Links use only source-named threat stubs: no CWE, CAPEC or cross-record mappings are guessed. Most links are proposed interpretations, even where a source groups controls and threats by playbook; the source does not assert a per-control product-specific edge.

## NIST skipped entries

| Native designator | Reason |
|---|---|
| `R-0001` | governing prose outside the GenAI additions lane |
| `R-0002` | governing prose outside the GenAI additions lane |
| `R-0003` | governing prose outside the GenAI additions lane |
| `R-0004` | governing prose outside the GenAI additions lane |
| `R-0005` | governing prose outside the GenAI additions lane |
| `R-0006` | governing prose outside the GenAI additions lane |
| `R-0007` | governing prose outside the GenAI additions lane |
| `R-0008` | governing prose outside the GenAI additions lane |
| `R-0009` | governing prose outside the GenAI additions lane |
| `R-0010` | governing prose outside the GenAI additions lane |
| `R-0011` | governing prose outside the GenAI additions lane |
| `R-0012` | governing prose outside the GenAI additions lane |
| `R-0013` | governing prose outside the GenAI additions lane |
| `R-0014` | governing prose outside the GenAI additions lane |
| `PO.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.1.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.1.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.1.2.N1` | informative note, not an obligation |
| `PO.1.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.2.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.2.1.N1` | informative note, not an obligation |
| `PO.2.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.2.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.3.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.3.1.N1` | informative note, not an obligation |
| `PO.3.1.N2` | informative note, not an obligation |
| `PO.3.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.3.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.3.3.N1` | informative note, not an obligation |
| `PO.4` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.4.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.4.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.5` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.5.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PO.5.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.1.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.2.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.3.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PS.3.1.N1` | informative note, not an obligation |
| `PS.3.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.1.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.1.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.1.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.2.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.3.2.N1` | informative note, not an obligation |
| `PW.4` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.4.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.4.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.4.4` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.5` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.5.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.6` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.6.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.6.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.7` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.7.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.7.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.8` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.8.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.8.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.9` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.9.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.9.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `PW.9.2.N1` | informative note, not an obligation |
| `RV.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.1.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.1.1.N1` | informative note, not an obligation |
| `RV.1.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.1.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.2.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.2.1.N1` | informative note, not an obligation |
| `RV.2.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.3.1` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.3.1.N1` | informative note, not an obligation |
| `RV.3.2` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.3.3` | SSDF practice/task baseline or overview; AI additions are converted separately |
| `RV.3.4` | SSDF practice/task baseline or overview; AI additions are converted separately |

## OWASP bullet reconciliation

| Playbook | Step 1 | Step 2 | Step 3 | Total |
|---|---:|---:|---:|---:|
| 1 | 3 | 3 | 5 | 11 |
| 2 | 8 | 6 | 6 | 20 |
| 3 | 8 | 7 | 7 | 22 |
| 4 | 7 | 5 | 7 | 19 |
| 5 | 7 | 2 | 4 | 13 |
| 6 | 9 | 5 | 6 | 20 |

## Human sample review completed

[The prepared sample](agentic-review-sample.md) contains ten proposed links per source, spread across its sections. The [review packet](agentic-review-packet.md) expands those same 40 targets into the proposed Requirement text, threat target, source locator and mapping rationale, with decision fields. M01–M10, N01–N10, O01–O10 and C01–C10 have 40 recorded Reviews and justifications: 39 accepted and O09 rejected. No sample decisions remain pending. The human owner checks the source, paraphrase and link rationale, then records the actual decision in a `reviews` entry with reviewer, status and justification. Accepting a link also requires changing its Assertion status to `accepted`; a rejected link stays `proposed` with its rejecting Review. Re-run all three extraction checks afterward. Completing this sample does not approve or merge the PR, close the issue, or review the remaining proposed links.

MAESTRO's mappings need particular scope review: each authored layer-control Requirement currently proposes one example threat from that layer, while the source umbrella addresses the layer's identified threats collectively. These links are not an exhaustive mapping. The source also names an Identity Attack under the Multi-Agent pattern that has no proposed link here. Section 4's explicit associations and section 3.2 C's interpreted associations must be distinguished when reviewing the rationale; a shared `medium` confidence is not evidence that their source support is equivalent. The packet flags these questions without deleting proposals. The ten recorded MAESTRO acceptances retain the presented limits: M01–M03 are general layer relationships, M04–M07 are interpreted response/detection/accountability relationships, and M08–M10 follow explicit source pairings. These acceptances do not make the mapping exhaustive or establish implementation or effectiveness.

The ten NIST acceptances concern model-development controls and inferred control-to-threat relationships, not a NIST-approved crosswalk. Their justifications preserve the secret-specific scope, provenance limits, confidentiality versus integrity distinction, and input/output execution limits presented to the human owner. No acceptance establishes implementation or mitigation effectiveness. The other two NIST Assertions remain proposed.

The OWASP sample has nine acceptances with the presented partial-protection, detection, investigation and recovery limits. O09 is rejected: quotas limit flooding but do not establish message truth or integrity, so the proposed communication-poisoning link lacks sufficient support. Its rejecting Review is preserved and the Assertion remains proposed; the requirement and source text are unchanged. No replacement resource-overload link is inferred from that rejection.

The ten MCP sample acceptances retain the presented source-section scope and limits: consent adds scrutiny rather than proving safety; session randomness does not protect stolen identifiers; redirect checks do not replace authorization; proxy isolation limits damage rather than eliminating vulnerabilities. The dated capture and historical-record digest mismatch remains documented above. Across the four fragments, 39 Assertions are accepted; 136 remain proposed, including O09 with its rejecting Review.

This sample is a review aid, not evidence of accuracy or a statistical validation of a product assessment.
