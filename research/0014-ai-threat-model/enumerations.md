---
schema: "archdoc/v1"
id: RPT-0014-enumerations
title: "RPT-0014 AI weakness and attack enumerations: survey and crosswalk"
type: research
status: draft
version: "0.2.0"
date: "2026-10-02"
updated: "2026-10-03"
record: RPT-0014
---

# RPT-0014: AI weakness and attack enumerations

Answers "is there a CWE for AI?", surveys every enumeration found, crosswalks them at the concept level, lists what no catalog covers, and proposes candidate local weakness entries for the gaps. Evidence, not decisions: DEC-008 (CWE/NVD integration) stays open. Counts were computed by the enumerations agent from machine-readable files (CWE 4.20 XML, CAPEC 3.9 XML, ATLAS 2026.09 YAML, CoSAI YAML, Arcanum JSON, NVD API) where possible; see the cited S-ids in [sources.md](sources.md).

## 1. The answer: is there a CWE for AI?

**Partly, and it is small.** There is no AI counterpart to CWE with comparable coverage. As of 2026-10-03 the picture is:

1. **CWE itself has an AI slice.** CWE 4.20 (2026-04-30, 969 weaknesses; still current per the CWE REST API on 2026-10-03) added view **CWE-1448** "Weaknesses Related to AI/ML Products" [S-0901]. It groups:
   - category **CWE-1446** "Weaknesses That are Specific to AI/ML Technology", with exactly **four** entries: **CWE-1039** inadequate detection or handling of adversarial input perturbations (2018) [S-0868], **CWE-1426** improper validation of generative AI output (4.15, 2024) [S-0886], **CWE-1427** improper neutralization of input used for LLM prompting, that is prompt injection (4.16, 2024) [S-0887], and **CWE-1434** insecure setting of generative AI/ML inference parameters (4.18, 2025, Draft) [S-0893];
   - category **CWE-1447** "General Software Weaknesses that Appear in Products that Use or Support AI/ML Technology", with 16 members: CWE-22, 77, 78, 79, 94, 95, 116, 250, 434, 502, 862, 918, 1336, plus 1426, 1427 and 1434.
   The view's own maintenance note says "it is still difficult to distinguish common AI/ML related attacks from underlying weaknesses". Status: Incomplete.
2. **More is coming, but deliberately coarse.** The CWE AI Working Group targets **CWE 5.0 for October 2026** with "support for AI-specific lifecycles" [S-0888]. Its pipeline (minutes 2026-06-12, slides 2026-06-26) holds new-entry proposals for improper isolation of task-relevant context, executable logic in AI/ML workflow definitions, reserved special tokens in AI instruction streams, learned-representation stability, and bypass of human authorization controls; likely modifications for cross-model scripting (into CWE-79), MCP client configuration, and retrieved content in prompt construction. The WG has said "CWE doesn't make separate entries for where the bad input came from", so prompt injection will not be split by channel (RAG vs email vs file name). CWE 5.0 had not shipped when this report was written; recheck before #74 closes.
3. **There is no AI attack-pattern layer in CAPEC.** CAPEC 3.9 (2023-01-24, still latest) contains no AI pattern [S-0882]. **MITRE ATLAS** fills the attack role: release 2026.09 has 16 tactics, 120 techniques and 88 sub-techniques (208 technique objects), 40 mitigations and 73 case studies [S-0903]. But ATLAS is not linked to CWE, and none of the four AI CWEs lists a related attack pattern, so the classic weakness -> attack pattern -> technique chain is broken for AI.
4. **In practice, AI root causes vanish from CVE records.** Of the 136 NVD CVEs whose description contains the phrase "prompt injection" (194 match both words anywhere; some of those are not about LLMs, for example CVE-2018-5314 and the KaiOS HTML-injection CVEs), none carries CWE-1427 in NVD, and NVD's `cweId=CWE-1427` query returns 0 records (in-house queries re-run 2026-10-03; S-0948 is this report's own measurement, not a publication); they are typed CWE-94, 77, 78, 22, 79, 74, 89, 918 [S-0948]. When a CNA does assign CWE-1427 (for example Eclipse's CVE-2026-44688), NVD can drop it. GitHub code search finds at least 17 CVE.org records citing CWE-1427, 3 citing CWE-1426 and 3 citing CWE-1039 (a lower bound). The CVE AI Working Group charter [S-0838] states that "not all AI issues are appropriate for a CVE assignment": jailbreaks, model-behaviour flaws and flaws in versionless hosted models generally get no CVE. Many production flaws in this report's incident log were fixed server-side with no CVE at all.
5. **Everything else is a risk list, a taxonomy or a scoring overlay**, not a weakness enumeration: OWASP Top 10 lists, the OWASP agentic threat catalog, NIST AI 100-2, SAIF/CoSAI, DASF, Cisco's framework, the MIT AI Risk Repository, AVID and others (section 2).

**Implication for tmodel (a proposal for DEC-008, not a decision).** A Weakness node mapped only to CWE (ARCH-0001 section 3) would leave most AI attack classes without a weakness at all: poisoning, backdoors, extraction, membership inference, RAG and memory poisoning, jailbreak root causes, agent authority and delegation flaws, approval binding and denial of wallet have no CWE. The evidence supports (a) mapping to CWE where an entry exists, including the general CWE-1447 members that dominate real AI CVEs; (b) holding candidate local weakness entries for the rest (section 5), each tracking the CWE AI WG pipeline; and (c) linking weaknesses to ATLAS techniques through tmodel's own reviewed edges, since no catalog provides them.

## 2. Survey of enumerations

Scope: what the catalog enumerates. Unit: what one id denotes. Count, version and format as fetched. Licence where stated.

### 2.1 Weakness and vulnerability identifiers

| enumeration | S-id | scope / unit | id scheme | count | version (date) | format | licence |
|---|---|---|---|---|---|---|---|
| CWE AI/ML view and categories | [S-0901] | weaknesses (developer mistakes) | CWE-n; view 1448, categories 1446/1447 | 4 AI-specific + 13 general in 1447 (16 members incl. the 3 GenAI entries); AI/ML platform tag on 22 CWEs | 4.20 (2026-04-30) | XML, REST API, HTML | CWE terms of use (free) |
| CWE-1427, 1426, 1434, 1039 | [S-0887], [S-0886], [S-0893], [S-0868] | individual AI weaknesses | CWE-n | 4 | 4.15-4.18 additions | as above | as above |
| CWE AI Working Group pipeline | [S-0888] | proposed entries for CWE 5.0 | CDR #n | 9 AI submissions, 7 proposing new entries | target 2026-10 | GitHub minutes and slides | public |
| CVE AI Working Group (CVEAI) | [S-0838] | what is CVE-able in AI | n/a | n/a | charter v1.1 (2024-09-16) | PDF charter; TLP:AMBER work | n/a |
| NVD / CVE.org typing of AI CVEs (measured) | [S-0948], [S-1084] | CVEs | CVE-yyyy-n | 136 "prompt injection" as a phrase (194 matching both words), 321 "LLM", 135 "Model Context Protocol" (NVD keyword; in-house measurement) | 2026-10-03 | NVD API 2.0 JSON | public |
| GCVE (decentralized CVE-compatible numbering) | [S-0894] | vulnerability ids from independent numbering authorities | GCVE-GNA-yyyy-n | 40+ GNAs | 2025-2026 | JSON | open |
| AVID | [S-0899] | AI flaws incl. non-CVE ones; reports | AVID-yyyy-Vnnn / -Rnnnn; taxonomy S0100-S0601, E, P, L01-L06 | 40 vulnerabilities (2022-23); 1,000+ reports in 2026 | repo pushed 2026-03-26 | JSON | MIT |

### 2.2 Attack (adversary-behaviour) enumerations

| enumeration | S-id | scope / unit | id scheme | count | version | format | licence |
|---|---|---|---|---|---|---|---|
| MITRE ATLAS | [S-0903] | adversary tactics and techniques against and with AI; mitigations; case studies | AML.TA00xx, AML.T0xxx[.00x], AML.M00xx, AML.CS00xx | 16 tactics, 120 techniques + 88 sub-techniques, 40 mitigations, 73 case studies; 139 technique objects tagged Agentic AI; maturity Realized 101 / Demonstrated 83 / Feasible 24 | 2026.09 (format 6.0.0, 2026-09-15); monthly CalVer content releases since 2026.05 (2026-05-27); earlier releases SemVer v5.x (v5.4.0 2026-02-05, v5.5.0 2026-03-30, v5.6.0 2026-04-30); the 2024.x-2025.x files under dist/v6 are retro-labelled | YAML, STIX 2.1, Navigator layers | Apache-2.0 |
| ATLAS <-> ATT&CK linkage | [S-0904] | technique/tactic equivalence | attack-reference fields | 44 techniques, 14 tactics, 4 mitigations | 2026.09 | YAML, STIX bundle | Apache-2.0 |
| ATLAS id drift (evidence) | [S-0905] | renumbering log | n/a | 2026.07 (2026-07-31): T0019 -> T0115.000, T0058 -> T0115.001, T0104 -> T0115.002; 2026.08 (2026-08-31): TA0001 renamed from "AI Attack Staging" to "AI Attack Adaptation" | 2026.07, 2026.08 | CHANGELOG | Apache-2.0 |
| CAPEC | [S-0882] | attack patterns | CAPEC-n | 0 AI patterns | 3.9 (2023-01-24) | XML | free |
| Cisco Integrated AI Security and Safety Framework | [S-0801] | objectives -> techniques -> subtechniques -> procedures; MCP and supply-chain taxonomies; harms | OB-001..019, AITech-x.y, AISubtech | 19 / 40 / 112; MCP 14 types; 25 harm categories | 2025 (arXiv 2512.12921) | PDF (machine-readable form claimed, not found) | ? |
| MITRE SAFE-AI | [S-0809] | ATLAS threats x system element -> SP 800-53 controls | ATLAS ids, 800-53 ids | 100 controls flagged AI-affected | April 2025 | PDF | public release |

### 2.3 Risk lists and threat taxonomies

| enumeration | S-id | scope / unit | id scheme | count | version | format | licence |
|---|---|---|---|---|---|---|---|
| OWASP Top 10 for LLM Applications 2025 | [S-0897] | LLM application risks | LLM01-LLM10:2025 | 10 | 2025 | PDF, web | CC BY-SA 4.0 |
| OWASP Top 10 for LLM v1.1 (archived) | [S-0883] | as above | LLM01-LLM10 (2023) | 10 (9 of 10 ids changed meaning in 2025; only LLM01 kept; alias table in section 2.6) | 2023 | repo | CC BY-SA |
| OWASP Top 10 for Agentic Applications | [S-0908] | agentic application risks | ASI01-ASI10 | 10 | 2026 (released 2025-12-09) | PDF with Appendix A crosswalk | CC BY-SA 4.0 |
| OWASP Agentic AI Threats and Mitigations | [S-0760] | agentic threats | T1-T17 | 17 | v1.1 (2025-12) | PDF | CC BY-SA |
| OWASP Machine Learning Security Top 10 | [S-0884] | ML model risks | ML01-ML10 | 10 | 2023 draft | GitHub markdown | CC BY-SA |
| OWASP MCP Top 10 | [S-0898] | MCP risks | MCP01-MCP10 | 10 | 2025 beta | web | CC BY-SA |
| OWASP Agentic Skills Top 10 | [S-0906] | agent skill risks | AST01-AST10 | 10 | v1.0-2026 | web | CC BY-SA |
| OWASP Non-Human Identities Top 10 | [S-0896] | machine/agent identity risks | NHI1-NHI10 | 10 | 2025 | web | CC BY-SA |
| OWASP AI Exchange | [S-0826] | threats and controls by attack surface | section numbers + owaspai.org/go/ short links | 300+ pages | living (PDF 2026-10-01) | web, PDF | CC0 1.0 |
| NIST AI 100-2 E2025 | [S-0855] | adversarial ML attacks (PredAI, GenAI) and mitigations | NISTAML.0x (5 classes) and NISTAML.0xx (25 leaves) | 30 ids | E2025 (2025-03) | PDF | US Government work |
| NIST AI 100-2 E2023 | [S-0841] | as above, no ids | none | n/a | 2024-01 | PDF | US Government work |
| NIST AI 600-1 GenAI Profile | [S-0792] | GAI risks and actions | risks 1-12; actions GV/MP/MS/MG-x.x-nnn | 12 risks, 212 actions | 2024-07-26 | PDF | US Government work |
| Google SAIF risk map | [S-0780] | AI risks on a component map | 2-3 letter codes (DP .. RA) | 15 enumerated on the risks page (re-fetched 2026-10-03; an earlier "17" was not reproduced) | living | web | ? |
| CoSAI Risk Map | [S-0900] | risks, controls, components, personas, crosswalks | camelCase (riskPromptInjection) | 36 risks, 37 controls, 42 components, 10 personas (verified by parsing the YAML at commit 0d8bfc9b5d76, 2026-10-03; the "43 risks / 59 components" alternative was wrong) | commit 2026-10-02 | YAML + JSON Schema | Apache-2.0 |
| CoSAI MCP Security | [S-0770] | MCP threat categories | MCP-T1..T12 | 12 categories, ~40 threats | 2026-01-08 (v2.0 2026-09-25) | PDF | OASIS |
| MCP-38 | [S-0909] | MCP threat categories | MCP-01..MCP-38 | 38 | v1.0 (2026) | PDF table | arXiv |
| Databricks DASF | [S-0779] | component risks and controls | component.n; DASF 1-69 | 12-13 components, 62 risks, 64+ controls | 2.0 / 3.0 | gated PDF | ? |
| CSA AI Controls Matrix | [S-0803] | controls with threat-category tags | CCM-style domain-nn | 243 controls, 18 domains | v1.0 (2025-07-09), v1.1 | spreadsheet | ? |
| Microsoft Failure Modes in ML | [S-0872] | intentional and unintentional ML failures | named modes | 11 + 6 | 2019 | web, arXiv | ? |
| Microsoft agentic failure modes | [S-0902] | agentic failure modes (novel/existing x safety/security) | named modes | v2.0 adds 4 security modes | v2.0 (2026-04) | PDF | ? |
| Arcanum Prompt Injection Taxonomy | [S-0865] | prompt-injection intents, techniques, evasions, inputs | PIT-I/T/E/N-nn | 27 + 70 + 63 + 12 = 172 nodes | v1.6.1 | JSON | CC BY 4.0 |
| 0DIN jailbreak taxonomy | [S-0863] | jailbreak categories, strategies, techniques | names | 3 levels (counts not shown) | living | web | ? |
| Rossi et al. PI categorization | [S-0308] | prompt-injection classes | names | 10 direct/indirect classes | 2024 | paper | arXiv |
| MIT AI Risk Repository | [S-0889] | risks extracted from frameworks | domain 1.1-7.x; causal taxonomy | 1,725 risks from 74 frameworks; 7 domains, 24 subdomains | v4 (2025-12) | database, sheet | CC BY 4.0 |
| IBM AI Risk Atlas / Atlas Nexus | [S-0892], [S-0957] | AI risk taxonomy and crosswalk KG | URIs | ? | Nexus v1.2.5 (2026-08-31) | LinkML YAML | Apache-2.0 |
| AIR 2024 risk categorization | [S-0224] | AI risk categories from policies | 4-level | 314 leaf categories (per source) | 2024 | paper | arXiv |
| Huwyler threat vector taxonomy | [S-0409] | threats mapped to loss categories | 9 domains | 53 sub-threats | 2025 | paper | arXiv |
| EU AI Act Art. 15(5) | [S-0839] | legally named AI attack classes | article text | 5 classes | Regulation 2024/1689 | law | public |
| ENISA AI Threat Landscape | [S-0729] | AI threats on assets | ENISA taxonomy codes | 74 threats | 2020 | PDF | ENISA |

### 2.4 Scoring and severity schemes

| scheme | S-id | what it scores | form | status |
|---|---|---|---|---|
| OWASP AIVSS | [S-0860] | agentic vulnerabilities: CVSS v4.0 base + agentic amplification (10 factors, 0/0.5/1) x threat multiplier x mitigation factor | formula, calculators | v0.8, pre-1.0, ordinal |
| MSRC AI severity classification | [S-0830] | inference manipulation and inferential disclosure classes | severity table | vendor, undated |
| Microsoft AI/ML SDL bug bar | [S-0831] | intentional ML failure modes -> SDL severity | table | 2019, superseded by MSRC |
| CVSS | — | no AI metrics; CWE AI WG minutes report CVSS discussions declined to score "output manipulation alone" | — | — |

### 2.5 Incident catalogs and exchange formats

| catalog | S-id | unit | ids | size (as fetched) | technique field? | format | licence |
|---|---|---|---|---|---|---|---|
| AI Incident Database | [S-0912] | incident with reports | integer | latest Incident 1720 (2026-10-01) | no (CSETv1, GMF, MIT harm taxonomies) | weekly JSON/CSV snapshots | not stated |
| CSET AI harm taxonomy | [S-0885] | harm coding of AIID incidents | field values | n/a | no | docs | ? |
| OECD AI Incidents and Hazards Monitor | [S-0911] | auto-extracted news incidents and hazards | AIM ids | about 18,050 | no | web | OECD |
| AIAAIC Repository | [S-0910] | incidents and controversies | ids | not confirmed | no | sheet | ? |
| MITRE ATLAS case studies | [S-0903] | incident or exercise coded to techniques | AML.CS00xx | 73 | **yes** (technique chain) | YAML | Apache-2.0 |
| ETSI TS 104 158 (AICIE) | [S-0859] | incident exchange record and container | GCVE-style record ids | n/a | no attack vocabulary | JSON (normative annex) | ETSI |
| OECD common reporting framework | [S-0856] | incident report structure | n/a | n/a | no | paper | OECD |
| Agarwal et al. incident schema | [S-0364] | proposed incident fields | n/a | n/a | partial | paper | arXiv |
| MITRE AI Incident Sharing | [S-0890] | member incident sharing | ? | ? | ? | ? | unverified |

### 2.6 OWASP LLM Top 10: v1.1 (2023) to 2025 alias table

Nine of the ten ids changed meaning between v1.1 (2023, S-0883) and the 2025 edition (S-0897); only LLM01 kept its meaning, and LLM09 was renamed and re-scoped. A reference written as a bare `LLM03` or `LLM10` is therefore ambiguous; every stored OWASP id must carry its edition (`LLM03:2023`, `LLM03:2025`). attack-catalog.yaml and sources.md now do (v0.2 fold).

| v1.1 (2023) id | v1.1 (2023) risk | 2025 successor | 2025 meaning of the same id |
|---|---|---|---|
| LLM01:2023 | Prompt Injection | LLM01:2025 | Prompt Injection (unchanged) |
| LLM02:2023 | Insecure Output Handling | LLM05:2025 Improper Output Handling | Sensitive Information Disclosure |
| LLM03:2023 | Training Data Poisoning | LLM04:2025 Data and Model Poisoning | Supply Chain |
| LLM04:2023 | Model Denial of Service | LLM10:2025 Unbounded Consumption | Data and Model Poisoning |
| LLM05:2023 | Supply Chain Vulnerabilities | LLM03:2025 Supply Chain | Improper Output Handling |
| LLM06:2023 | Sensitive Information Disclosure | LLM02:2025 Sensitive Information Disclosure | Excessive Agency |
| LLM07:2023 | Insecure Plugin Design | no direct successor (closest: LLM06:2025 Excessive Agency; ASI02:2026 Tool Misuse) | System Prompt Leakage |
| LLM08:2023 | Excessive Agency | LLM06:2025 Excessive Agency | Vector and Embedding Weaknesses |
| LLM09:2023 | Overreliance | LLM09:2025 Misinformation (renamed and re-scoped) | Misinformation |
| LLM10:2023 | Model Theft | LLM10:2025 (model extraction under Unbounded Consumption) and LLM02:2025 | Unbounded Consumption |

## 3. Crosswalk

### 3.1 Who officially maps what

| from | to | maintained by | form | notes |
|---|---|---|---|---|
| ATLAS techniques, tactics, mitigations | ATT&CK Enterprise | MITRE | `attack-reference` in ATLAS YAML; STIX `stix-atlas-attack-enterprise.json` | 44 techniques, 14 tactics, 4 mitigations; AI Model Access and AI Attack Adaptation have no ATT&CK counterpart |
| OWASP ASI01-ASI10 | OWASP LLM 2025; Agentic T1-T17; AIVSS core risks | OWASP | PDF Appendix A | many-to-many; no ATLAS or CWE mapping |
| OWASP NHI1-NHI10 | ASI; T-codes; AIVSS | OWASP | PDF Appendix C | entry level |
| OWASP LLM01-10:2025 | ATLAS (partial: 01, 02, 03, 04, 07, 09, 10); CWE-400 (LLM10 only) | OWASP | PDF prose | LLM05, 06, 08 unmapped; pre-rename ATLAS names |
| AIVSS core risks | ASI01-ASI10 | OWASP AIVSS | PDF Appendix B | 10 to 10 |
| CoSAI risks | ATLAS (version-pinned @5.0.1), OWASP LLM 2025, STRIDE; registry also nist-ai-rmf, iso-22989, eu-ai-act | CoSAI | YAML + JSON Schema | 19/36 to ATLAS, 19/36 to OWASP, 26/36 to STRIDE; one dangling id (riskDataPoisoning -> AML.T0019, now T0115.000) |
| ATLAS techniques | NIST SP 800-53 Rev 5 | MITRE SAFE-AI | PDF appendices | per threat x system element |
| CSF 2.0 subcategories (Cyber AI Profile) | ATLAS mitigations, DASF controls, OWASP AI Exchange, SP 800-53 | NIST IR 8596 (draft) | informative references | first NIST document citing ATLAS at subcategory level |
| CSA Singapore treatment controls | ATLAS technique ids, OWASP LLM | CSA Singapore | PDF tables | cites now-deprecated ATLAS ids |
| CSA AICM controls | ISO/IEC 42001, NIST AI RMF / 600-1, BSI AIC4, EU AI Act | CSA | spreadsheet | control level |
| OWASP AI Exchange | ISO/IEC 27090, prEN 18282, ISO 42001/23894/5338/27002, OpenCRE | OWASP | web | section level |
| MCP-38 | STRIDE, OWASP LLM 2025, ASI 2026 | academic | PDF table | no ATLAS |
| Arcanum PIT nodes | OWASP, ATLAS, NIST | Arcanum | JSON aliases | node level |
| AVID security categories | ATLAS (category level, "map directly to") | AVID | docs | not id level |
| **CWE AI entries** | **ATLAS, OWASP, NIST** | **none** | n/a | **No official mapping.** No Taxonomy_Mapping or Related_Attack_Pattern for 1039/1426/1427/1434 |
| **NIST AI 100-2 NISTAML ids** | **ATLAS, OWASP, CWE** | **none** | n/a | **No official id-level mapping** |

### 3.2 Concept-level crosswalk

Rows are attack or weakness concepts. Plain entries are stated by the catalog owner or an official crosswalk; `(i)` is inferred by the agents from definitions; `-` means no corresponding entry. v0.2: cells were reconciled with attack-catalog.yaml after the review fold (rows marked v0.2 are new); OWASP LLM ids in this table are the 2025 edition. The last column links to this report's [attack-catalog.yaml](attack-catalog.yaml). Versions: CWE 4.20; ATLAS 2026.09; OWASP LLM 2025; ASI 2026; OWASP Agentic T&M v1.1; OWASP ML 2023; NIST AI 100-2 E2025; SAIF/CoSAI as of 2026-10-02.

| concept | CWE | ATLAS | OWASP LLM | ASI | T-code | ML | NIST AI 100-2 | SAIF / CoSAI | AVID | EU AI Act 15(5) | other (MCP Top 10, AST10, Cisco, MCP-38) | AIT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Direct prompt injection | CWE-1427 | AML.T0051.000 | LLM01 | ASI01 | T6 | - | NISTAML.018 | PIJ / riskPromptInjection | - | - | Cisco AITech-1.1 | AIT-063 |
| Indirect prompt injection | CWE-1427 | AML.T0051.001, T0093, T0066 (i) | LLM01 | ASI01, ASI06 | T6, T1 | - | NISTAML.015 (.016, .017) | PIJ / riskPromptInjection | - | - | MCP06; MCP-38 (i) | AIT-064, AIT-065 |
| Hidden-character smuggling | CWE-1427, CWE-116 (i) | AML.T0068 | LLM01 | ASI01 | T6 (i) | - | NISTAML.015 | riskPromptInjection (i) | - | - | - | AIT-067 |
| Special-token / chat-template role forgery | - (WG submission) | AML.T0051.000 (i) | LLM01 | ASI01 (i) | - | - | NISTAML.018 (i) | - | - | - | - | AIT-069 |
| Jailbreak / guardrail bypass | - (gap) | AML.T0054, T0068 | LLM01 | - | T7 (i) | - | NISTAML.018 under .04 | riskPromptInjection (i) | - | - | Cisco harms | AIT-073, AIT-074 |
| Harmful fine-tuning / white-box safety removal | - | AML.T0018.000, T0054 (i) | LLM04 | - | - | ML10 (i) | NISTAML.037, .04 | MST (i) | S0201 (i) | model poisoning (i) | - | AIT-081, AIT-082 |
| System-prompt extraction | CWE-200 (i) | AML.T0056, T0069.002 | LLM07 | - | - | - | NISTAML.035 | SDD / riskSensitiveDataDisclosure | S0301 (i) | confidentiality attacks | - | AIT-083 |
| Improper output handling (XSS/SQLi/RCE via output) | CWE-1426 (+79, 94, 77) | AML.T0077, T0050 (i) | LLM05 | ASI05 | T11 | ML09 (i) | NISTAML.039 | IMO / riskInsecureModelOutput | S0100 | - | MCP05 | AIT-072, AIT-066 |
| Excessive agency / tool misuse | CWE-250, 862 (i) | AML.T0053, T0086, T0101 | LLM06 | ASI02 | T2, T4, T16 | - | NISTAML.015, .039 for injection-driven misuse (AIT-091); - for non-adversarial excessive agency (AIT-114, out of NIST scope) | RA / riskRogueActions | - | - | MCP02 | AIT-091, AIT-114 |
| Human-approval bypass | - (WG submission CDR #174) | AML.T0053 (i) | LLM06 | ASI09 | T10 | - | - | - | - | - | AST (i) | AIT-093 |
| Identity and privilege abuse, credential harvesting | CWE-862, 522 (i) | AML.T0012, T0055, T0083, T0098, T0113, T0091.001, T0082 | LLM06, LLM02 | ASI03 | T3 (ASI Appendix A); T9 (i) | - | - (gap: section 3.5 has no id) | riskCrossTenantCredentialPropagation, riskStaleAgentIdentityBinding | - | - | MCP01, MCP07; NHI | AIT-100, AIT-101, AIT-099 |
| Training-data poisoning | - | AML.T0020, T0115.000, T0059 | LLM04 | ASI06 (i) | T1 (i) | ML02 | NISTAML.013, .012, .024 | DP / riskDataPoisoning | S0600, S0601 | data poisoning | - | AIT-011 .. AIT-027 |
| Backdoor / model poisoning (LoRA, PEFT, template, quantization) | - | AML.T0018, T0018.003, T0115.001 | LLM04 | ASI04 | T17 | ML10, ML07 | NISTAML.023, .021, .011, .026, .051 | MST / riskModelSourceTampering, riskAdapterPEFTInjection | S0201 | model poisoning | - | AIT-015, AIT-033, AIT-031, AIT-032 |
| Unsafe model deserialization / loader RCE | CWE-502, 94 | AML.T0011.000, T0010.003, T0076 | LLM03 | ASI04 (ASI05 only when an agent loads or runs it) | T17, T11 | ML06 | - (out of scope: platform attack, NIST section 1; NISTAML.05 covers only ML-specific supply-chain poisoning) | riskMaliciousLoaderDeserialization (unmapped) | S0201 | - | - | AIT-028, AIT-029 |
| Dependency / tool / MCP supply chain, rug pull | CWE-829 | AML.T0010, T0109, T0110, T0110.001, T0111, T0115.002 | LLM03 | ASI04 | T17, T16 | ML06 | - (out of scope, as above) | riskToolSourceProvenance, riskToolRegistryTampering, riskZombieShadowMCPServers | S0202 | - | MCP03, MCP04, MCP09; AST; MCP-38 | AIT-096, AIT-097, AIT-095, AIT-037 |
| Evasion / adversarial examples | CWE-1039 | AML.T0015, T0043 | (CoSAI maps MEV to LLM01) | - | - | ML01 | NISTAML.022, .025 | MEV / riskModelEvasion | S0403 | adversarial examples | - | AIT-001 .. AIT-010 |
| Model extraction / theft | - | AML.T0024.002, T0048.004, T0005 | LLM10 (refs T0024), LLM02 (i) | - | - | ML05 | NISTAML.031 | MXF, MRE | S0502 | confidentiality attacks | - | AIT-052, AIT-054, AIT-055 |
| Membership inference / inversion | - | AML.T0024.000, .001 | LLM02 | - | - | ML03, ML04 | NISTAML.033, .032, .034 | SDD, ISD | S0501 | confidentiality attacks | - | AIT-046, AIT-047 |
| Training-data extraction / user-data leakage | CWE-200 (i) | AML.T0057, T0024 | LLM02 | ASI03 (i) | - | - | NISTAML.038, .037, .036 | SDD, EDH | S0301 | confidentiality attacks | MCP10 | AIT-048, AIT-084 |
| RAG / vector-store poisoning; embedding inversion | - (WG submission pending) | AML.T0070, T0071, T0066 | LLM08 | ASI06 | T1 | - | NISTAML.015, .013 | riskRetrievalVectorStorePoisoning (unmapped) | - | - | - | AIT-086, AIT-050 |
| Agent memory / context poisoning | - | AML.T0080 (.000, .001) | LLM04, LLM08 (via ASI06) | ASI06 | T1, T4 | - | - | - | - | - | - | AIT-102 |
| Insecure inter-agent communication | - | - (gap: no ATLAS technique for injection into a victim's inter-agent channel; AML.T0118 is rogue agents' own communication); AIT-106 uses T0051.001 + T0110.002 | LLM02, LLM06 (via ASI07) | ASI07 | T12, T16 | - | - | riskMCPTransportHijacking, riskAgentDelegationChainOpacity, riskAgenticDelegationConfusedDeputy | - | - | - | AIT-106 |
| Cascading failures / hallucination propagation | CWE-1426, CWE-1434 (i) | AML.T0062 (i) | LLM09 (via ASI08) | ASI08 | T5, T8 | - | - (out of scope: non-adversarial) | riskRunawayAgentToolLoops | P-domain (i) | model flaws | - | AIT-116, AIT-107 |
| Rogue / misaligned agent | - | AML.T0117, T0118.000, T0121, T0105 (as coded in AML.CS0068) | LLM02, LLM09 (via ASI10) | ASI10 | T13, T14, T15 (ASI Appendix A) | - | - (out of scope: non-adversarial) | - (riskShadowAndUnknownAgents concerns unmanaged agents; moved to the shadow-agent row) | - | - | MCP09 (i) | AIT-115 |
| Unbounded consumption / denial of wallet / sponge | CWE-400 | AML.T0029, T0034, T0034.002, T0008.005 (LLMjacking resale) | LLM10 | ASI02, ASI08 (i) | T4 | - | NISTAML.014, .017, .01 | DMS / riskDenialOfMLService, riskEconomicDenialOfWallet | S0302 | - | - | AIT-112, AIT-111, AIT-113 |
| Agent code execution / sandbox escape | CWE-94, 78, 77, 1336 | AML.T0050, T0105, T0053 | LLM05, LLM06 | ASI05 | T11 | - | NISTAML.015 when injection-driven (integrity); .039 only for the data-leak step | IIC / riskInsecureIntegratedComponent | S0100 | - | MCP05 | AIT-092, AIT-110 |
| Unsafe inference parameters / hallucinated packages | CWE-1434 | AML.T0060, T0062 | LLM09 | - | T5 | - | - (out of scope: non-adversarial model flaw) | - | - | model flaws | - | AIT-038 |
| Serving and accelerator side channels (KV cache, token length, GPU memory) | CWE-208, CWE-203, CWE-226 (general) | - (gap; AIT-058/059 use generic AML.T0024, T0025, T0057) | LLM02 (i) | - | - | - | - (no dedicated id; NISTAML.031 section 2.4.4 names cache, EM and Rowhammer side channels only for model extraction) | riskAcceleratorAndSystemSideChannels, riskPromptResponseCachePoisoning (unmapped) | - | - | - | AIT-058, AIT-059, AIT-089 |
| Hardware faults / bit flips on weights | CWE-1256, CWE-1261 (bit flips); CWE-1247, CWE-1319, CWE-1332 (physical fault injection) | - (gap; AIT-061 uses AML.T0018/T0031 as nearest) | - | - | - | - | - (no dedicated id; NISTAML.026 direct model modification by extension) | - | - | - | - | AIT-061, AIT-062 |
| Exposed AI infrastructure and stores | CWE-306, 284, 732 (general) | AML.T0132, T0049, T0010.004 | - (no OWASP LLM entry for non-agentic AI-infrastructure RCE; recorded as a gap) | - (ASI05 only when an agent executes code) | - | - | - (out of scope: platform attack) | IIC (i) | S0100 | - | MCP09 | AIT-039, AIT-042 |
| Offensive use: AI-orchestrated intrusion | - | AML.T0116, T0117, T0124, T0118.001, T0017.001 | - | - | - | - | NISTAML.04 only where a jailbreak is used (AIT-121, per AML.CS0069) | - | - | - | - | AIT-121, AIT-122 |
| Deepfake-enabled social engineering | CWE-290 for biometric spoofing (AIT-010) | AML.T0088, T0052.001 | - | - (ASI09 concerns agents exploiting human trust; no agent involved) | T15 (i) | - | - (out of scope: misuse without circumvention) | - | - | - | - | AIT-127 |
| Agent payment and transaction manipulation (v0.2) | CWE-863 | AML.T0051.001, T0070, T0053, T0048.000 (per AML.CS0026) | LLM01, LLM06 | ASI01, ASI02, ASI09 | - | - | NISTAML.015 | - | - | - | LW-005 (candidate) | AIT-134 |
| LLM-enabled attribute inference / deanonymization (v0.2) | CWE-359 | AML.T0087, T0116 | LLM02 | - | - | - | - (misuse outside NIST scope) | ISD / riskInferredSensitiveData | - | - | - | AIT-135 |
| Shadow, orphaned and stale agents and NHIs (v0.2) | - | AML.T0055, T0012 | LLM06 | ASI03 | - | - | - (gap) | riskShadowAndUnknownAgents, riskZombieShadowMCPServers, riskStaleAgentIdentityBinding | - | - | MCP09; NHI1 | AIT-138 |
| Repudiation of agent actions (v0.2) | CWE-778 | - (gap) | - | - (T8 maps to ASI08/ASI09) | T8 | - | - (gap) | - | - | - | MCP08 | AIT-139 |
| Human-review flooding / approval fatigue (v0.2) | - | AML.T0046 | - | ASI09 | T10 | - | - | - | - | - | - | AIT-140 |
| Provider data handling and upstream model change (v0.2) | CWE-359, 200 | - (gap) | LLM02, LLM03 | - | - | - | - (out of scope) | - | - | - | - | AIT-141, AIT-142 |
| LLM router manipulation (v0.2) | - | - (gap) | - | - | - | - | - | riskOrchestratorRouteHijacking | - | - | - | AIT-146 |

## 4. Gaps: what no catalog covers well

1. **No weakness-level entry for most AI attack classes.** CWE has 4 AI-specific weaknesses. Poisoning, backdoors, extraction, membership inference, RAG and memory poisoning, jailbreak root causes (competing objectives, mismatched generalization [S-0207]), agent authority and delegation, context isolation, approval binding and denial of wallet have no CWE. CWE 5.0 may add several; it will not add per-channel variants.
2. **AI root causes are lost from vulnerability records** (section 1, item 4). Vulnerability-driven threat modeling cannot discover AI weaknesses from NVD.
3. **The weakness -> attack-pattern -> technique chain is broken.** CAPEC has no AI patterns; ATLAS is not linked to CWE.
4. **Model-behaviour flaws have no identifiers.** Jailbreaks, guardrail bypasses and flaws in versionless hosted models fall outside CVE; AVID, GCVE numbering authorities and flaw-disclosure proposals ([S-0434], [S-0235]) are the alternatives, none widely used.
5. **Catalogs drift.** OWASP changed the meaning of 9 of its 10 LLM ids between v1.1 (2023) and 2025 (section 2.6). ATLAS renumbered three techniques in 2026.07 (T0019/T0058/T0104 -> T0115.*), renamed a tactic in 2026.08, and has released content monthly since 2026.05. Only CoSAI (ADR-027) and [S-0823] pin versions. A KG must store (framework, version, id) triples and keep an alias table for deprecated ids. This report pins every id it uses (attack-catalog.yaml header).
6. **Agentic coverage is broad but unaligned.** ASI (10), T-codes (17), ATLAS (139 agentic technique objects), Microsoft agentic failure modes, Cisco OB/AITech, MCP-38, CoSAI MCP-T, OWASP MCP Top 10, AST10, DASF component 13 and 21 CoSAI additions overlap; no official crosswalk joins ATLAS with the OWASP agentic lists.
7. **Some classes appear in almost no catalog.** Serving side channels (KV cache, prompt cache, token length, MoE routing, speculative decoding), GPU memory leakage and bit-flip attacks on weights appear only as an unmapped CoSAI risk or not at all; ATLAS and NIST have no dedicated hardware-fault id (NIST mentions Rowhammer and EM side channels only as model-extraction methods under NISTAML.031, and NISTAML.026 covers fault-induced weight changes only by extension), while CWE does have hardware entries that fit (CWE-1256, 1261, 1247, 1319, 1332). Chat-template, quantization and adapter backdoors collapse into generic "model poisoning". Multimodal triggers only gained AML.T0129 in 2026.09; computer-use visual attacks appear only in Microsoft v2.
8. **No catalog maps AI threats to business assets.** Only ENISA 2020, SAFE-AI and CoSAI carry asset or actor fields; none models business assets such as customer PII in a RAG store or cloud spend. [S-0409] is the only link to quantitative loss.
9. **Scoring is immature.** AIVSS is pre-1.0, agentic-only and ordinal on top of CVSS v4.0; CVSS has no AI metrics.
10. **Incident catalogs do not link to techniques**, except ATLAS case studies (73). AIID, OECD AIM and AIAAIC classify harms, not techniques or weaknesses. ETSI AICIE standardizes exchange without an attack vocabulary. 110 of the 179 incidents in this report's log have no ATLAS case study (v0.2), although every one of ATLAS's 73 case studies now appears in the log.
11. **Regulation enumerates five classes.** EU AI Act Art. 15(5) names data poisoning, model poisoning, adversarial examples, confidentiality attacks and model flaws; it omits prompt injection, agents and supply-chain code execution. prEN 18282 and ISO/IEC 27090 were not confirmed published.
12. **Prompt injection is enumerated at incompatible granularities**: one entry (CWE-1427, LLM01), two NIST ids (.015/.018), Rossi's classes, the seven-component model of [S-0825], and Arcanum's 172 nodes. There is no agreed intermediate level for threat-model generation; the AIT catalog uses ten prompt-injection techniques as a working middle level.

## 5. Candidate local weakness entries (candidate, not accepted)

Where no CWE fits, tmodel will need weakness nodes of its own or will have to leave AI attacks without a weakness. The entries below are **candidates proposed by the synthesis agent, not accepted, not CWE entries, and not a decision on DEC-001 or DEC-008**. Each names the closest existing CWE (a candidate parent), the CWE AI WG submission it may be superseded by, the attack techniques it enables, and the evidence. Ids use a local `LW-` prefix so they cannot be mistaken for CWE ids. If CWE 5.0 (October 2026) adds a matching entry, the candidate should be retired in favour of it.

| id | candidate weakness | description | closest CWE (candidate parent) | WG pipeline overlap | enables (AIT) | evidence |
|---|---|---|---|---|---|---|
| LW-001 | Training or retrieval data accepted without integrity or provenance binding | Data used to train, fine-tune or ground a model is fetched or ingested without content hashes, signed provenance or source trust, so a third party can change it between curation and use. | CWE-345, CWE-494 | none | AIT-013, AIT-014, AIT-086, AIT-090 | [S-0231], [S-0466], [S-0493], [S-1040] |
| LW-002 | AI artifact referenced by a mutable or reusable identifier | Models, adapters, datasets or MCP servers are fetched by a name (hub path, package name) that another party can later register or change, without a pinned digest. | CWE-829, CWE-494 | "MCP client configuration" (partial) | AIT-036, AIT-097, AIT-038 | [S-1061], [S-0534], [S-0468] |
| LW-003 | Behaviour not re-validated after a model transformation | A model is evaluated before, but deployed after, quantization, merging, adapter composition or chat-template substitution, so behaviour that appears only after the transformation is never tested. | CWE-1068 (i), CWE-693 | none | AIT-032, AIT-033, AIT-031 | [S-0252], [S-0348], [S-0517] |
| LW-004 | Co-location of untrusted input, sensitive access and external effect in one model context | One agent session can read untrusted content, access private data or systems, and change state or communicate externally, with no deterministic policy between them (lethal trifecta, Rule of Two). | CWE-653 (insufficient compartmentalization), CWE-441 | "Improper isolation of task-relevant context" (partial) | AIT-091, AIT-065, AIT-104 | [S-0820], [S-0808], [S-0388], [S-0769] |
| LW-005 | Human approval not bound to the executed action | The action a human approves (as displayed) differs from, or can be changed before, what executes; allow-lists check only a prefix or a name. | CWE-863, CWE-367 | "Bypass of human authorization controls" (CDR #174) | AIT-093, AIT-092 | [S-0638], [S-0427], [S-1056] |
| LW-006 | Agent can modify its own security-relevant configuration | Files or settings that govern the agent's permissions, tool set or approvals (auto-approve flags, MCP config, rules files) are inside the agent's write scope. | CWE-15, CWE-732 | "MCP client configuration" (partial) | AIT-094, AIT-092 | [S-1112], [S-1097] |
| LW-007 | Model-visible metadata from third-party tools, skills or rules not neutralized | Tool descriptions, skill files and rules files enter the model context as trusted instructions, unseen or unrendered for the human. | CWE-1427 (variant), CWE-116 | "Retrieved content in prompt construction" | AIT-096, AIT-095, AIT-098 | [S-1031], [S-1046], [S-0515] |
| LW-008 | Persistent agent memory written without provenance or consent | The agent writes long-term memory from content it processed or from any user, without recording origin, confirming with the owner, or isolating per user. | CWE-345, CWE-668 | none | AIT-102, AIT-071 | [S-0392], [S-0995], [S-1066] |
| LW-009 | Unbounded per-session consumption in agent loops | No bound on context growth, recursion, tool re-billing or cumulative spend across turns, so untrusted data or tools convert into recurring cost. | CWE-400, CWE-770 | none | AIT-111, AIT-112 | [S-0662], [S-0418], [S-0576] |
| LW-010 | Cross-tenant shared inference state | KV, prefix, semantic or prompt caches, MoE routing or GPU memory are shared across tenants without isolation or constant-time behaviour, leaking or corrupting other users' prompts and outputs. | CWE-203, CWE-226, CWE-668 | none | AIT-058, AIT-089, AIT-059 | [S-0480], [S-0465], [S-0318], [S-1109] |
| LW-011 | Unpadded token streaming | Responses are streamed one token per network record, so ciphertext lengths and timing reveal token lengths and topics. | CWE-203 | none | AIT-058 | [S-0325], [S-0440] |
| LW-012 | Inference API exposes model internals beyond the use case | Logprobs, logit bias, full-vocabulary scores, reusable encrypted reasoning or embeddings are returned when the product does not need them, enabling extraction, inversion or distillation. | CWE-200, CWE-497 | none | AIT-053, AIT-052, AIT-050, AIT-054 | [S-0232], [S-0255], [S-0581], [S-0188] |
| LW-013 | Sensitive data memorized by a deployed model | Training or fine-tuning data containing PII, secrets or confidential text is learned in recoverable form (duplicated, overfit, no DP), and the model is exposed to parties not entitled to that data. | CWE-359, CWE-312 (i) | none | AIT-048, AIT-046 | [S-0113], [S-0189], [S-0269] |
| LW-014 | Model-internal safety relied on as an access-control boundary | Safety training or refusal behaviour is the only control against misuse by parties who can fine-tune, hold the weights, or query without limit. | CWE-602 (client-side enforcement, by analogy), CWE-693 | "Learned representation stability" (partial) | AIT-081, AIT-082, AIT-077 | [S-0303], [S-0227], [S-0271] |
| LW-015 | Model judgement used as the sole security decision | An LLM classifier, judge or guard model decides authorization, moderation, triage or malware verdicts with no deterministic backstop, so input that fools the task model can fool the guard. | CWE-807 (i), CWE-693 | none | AIT-130, AIT-007 | [S-0316], [S-1054], [S-0443] |
| LW-016 | Weights resident in fault-susceptible shared memory without integrity checking | Model weights or KV blocks sit in DRAM/GDDR shared with untrusted tenants, without ECC or runtime integrity checks, so bit flips change behaviour. | CWE-1256 (cites Rowhammer bit flips), CWE-1261 (single-event upsets); v0.1 named CWE-1260 and CWE-1339, which are unrelated (overlapping protected memory ranges; real-number precision) | none | AIT-061 | [S-0428], [S-0424], [S-0241] |

**How to use these in #74.** If DEC-001 keeps a Weakness type mapped to CWE, these candidates need a status (`candidate`), a pointer to the CWE AI WG submission they track, and a `superseded_by` edge for when CWE 5.0 or later adds an entry. Whether tmodel keeps local weaknesses at all is part of DEC-001 and DEC-008 and is not decided here.

## 6. ATLAS 2026.09 coverage check (v0.2)

The catalog maps 133 of the 208 technique objects in ATLAS 2026.09. The other 75 are listed here as intentionally unmapped, so that an import can tell a deliberate omission from a missed one. Re-run against each pinned release.

| unmapped technique | reason |
|---|---|
| AML.T0000 Search Open Technical Databases (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0000.000 Journals and Conference Proceedings (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0000.001 Pre-Print Repositories (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0000.002 Technical Blogs (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0000.003 Scan Databases (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0001 Search Open AI Vulnerability Analysis (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0002 Acquire Public AI Artifacts (Realized) | resource development or staging; attacker-side preparation |
| AML.T0002.000 Datasets (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0002.001 Models (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0002.002 AI Agent Configuration (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0003 Search Victim-Owned Websites (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0004 Search Application Repositories (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0005.000 Train Proxy via Gathered AI Artifacts (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0005.002 Use Pre-Trained Model (Feasible) | resource development or staging; attacker-side preparation |
| AML.T0006 Active Scanning (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0006.000 Enumerate Hosted AI Resources (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0006.001 Query Platform Metadata APIs (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0006.002 Scan for Exposed AI Infrastructure (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0006.003 Probe AI Agent Trigger Channels (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0007 Discover AI Artifacts (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0008 Acquire Infrastructure (Realized) | resource development or staging; attacker-side preparation |
| AML.T0008.000 AI Development Workspaces (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0008.001 Consumer Hardware (Realized) | resource development or staging; attacker-side preparation |
| AML.T0008.002 Domains (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0008.003 Physical Countermeasures (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0008.004 Serverless (Feasible) | resource development or staging; attacker-side preparation |
| AML.T0010 AI Supply Chain Compromise (Realized) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0011.003 Malicious Link (Demonstrated) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0013 Discover AI Model Ontology (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0016 Obtain Capabilities (Realized) | resource development or staging; attacker-side preparation |
| AML.T0016.000 Adversarial AI Attack Implementations (Realized) | resource development or staging; attacker-side preparation |
| AML.T0016.001 Software Tools (Realized) | resource development or staging; attacker-side preparation |
| AML.T0016.003 Exploits (Realized) | resource development or staging; attacker-side preparation |
| AML.T0016.004 AI Agent Tools (Realized) | resource development or staging; attacker-side preparation |
| AML.T0017 Develop Capabilities (Realized) | resource development or staging; attacker-side preparation |
| AML.T0017.000 Adversarial AI Attacks (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0017.002 AI Agent Tools (Realized) | resource development or staging; attacker-side preparation |
| AML.T0034.000 Excessive Queries (Feasible) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0037 Data from Local System (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0042 Verify Attack (Demonstrated) | resource development or staging; attacker-side preparation |
| AML.T0052 Phishing (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0063 Discover AI Model Outputs (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0067 LLM Trusted Output Components Manipulation (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0069 Discover LLM System Information (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0069.000 Special Character Sets (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0069.001 System Instruction Keywords (Demonstrated) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0074 Masquerading (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0075 Enterprise Resource Discovery (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0078 Drive-by Compromise (Demonstrated) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0079 Stage Capabilities (Realized) | resource development or staging; attacker-side preparation |
| AML.T0080 AI Agent Context Poisoning (Realized) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0084.000 Embedded Knowledge (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0084.001 Tool Definitions (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0084.002 Activation Triggers (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0084.003 Call Chains (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0089 Enterprise Environment Discovery (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0091 Use Alternate Authentication Material (Realized) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0092 Manipulate User LLM Chat History (Demonstrated) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0095 Search Open Websites/Domains (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0095.000 Code Repositories (Realized) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
| AML.T0097 Virtualization/Sandbox Evasion (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0103 Deploy AI Agent (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0106 Exploitation for Credential Access (Demonstrated) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0107 Exploitation for Defense Evasion (Demonstrated) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0110 AI Agent Tool Poisoning (Realized) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0112 Machine Compromise (Demonstrated) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0112.001 AI Artifacts (Feasible) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0115 Publish Poisoned AI Artifacts (Realized) | parent or sibling of a mapped (sub-)technique; the more specific id is used |
| AML.T0120 AI Artifact Repository (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0122 Exploitation of Remote Services (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0123 Obfuscated Files or Information (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0125 Create Account (Realized) | resource development or staging; attacker-side preparation |
| AML.T0127 Data Staged (Realized) | generic enterprise or post-exploitation step (collection, evasion, credential access, lateral movement); recorded on attack paths, not per technique |
| AML.T0128 Compromise Infrastructure (Realized) | resource development or staging; attacker-side preparation |
| AML.T0133 Discover AI Agent Runtime Capabilities (Feasible) | reconnaissance or discovery step; attaches to attack paths, not to a technique entry |
