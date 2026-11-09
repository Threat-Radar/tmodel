---
schema: "archdoc/v1"
id: DL-0011-lane-catalogs-schema
title: "RPT-0014 lane catalogs-schema: WAVE 1 calibration (S-0855, S-0166, S-0728)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-08"
updated: "2026-11-08"
record: DL-0011
issue: 79
---

# DL-0011 lane note: catalogs-schema, WAVE 1 calibration

Lane owner: @Maimcghee. Review partner (R-018, LANES.md lane table): @paria03.

## Question asked

LANES.md Step 1: every lane writes its own `record.yaml` and `summary.md` for the same three calibration sources, without looking at the other lanes' versions. The integration lane (#82) then compares tags, applicability ratings, linked ids and summary claims across the lanes before WAVE 2 (#84) scales up.

## What was produced

Under `research/0014-ai-threat-model/calibration/catalogs-schema/`:

| Record | Source | Status | Confidence |
|---|---|---|---|
| `nist-ai-100-2-e2025/` | S-0855, NIST AI 100-2 E2025 | summarized | medium (read in part) |
| `greshake-2023-indirect-prompt-injection/` | S-0166, Greshake et al., AISec '23 | summarized | high |
| `biml-ara-ml-2020/` | S-0728, BIML ARA of ML systems v1.0 | summarized | medium (read in part) |

Each `summary.md` has the six `summarize` sections, the RPT-0014 applicability table, a reference-expansion note, and `reviewed_by: ""` in its front matter for the review partner to sign.

## How it was run

- **Tooling:** Claude Code (Opus 5.5) on the lane owner's account, 2026-11-08, in one interactive session. No `rpt0014-extract` or `rpt0014-sweep` workflow (those are WAVE 2) and no subagents.
- **Sources:** fetched from the `pdf-manifest.tsv` URLs, except NIST, which came from the direct `nvlpubs.nist.gov` PDF that the manifest's DOI resolves to. All three SHA-256 digests match the manifest.
- **Reading:** text extracted with `pypdf` 5.4.0, then targeted reading. Each summary's *Limits* section names the sections read. Greshake et al. was read nearly in full; NIST (127 pp.) and BIML (42 pp.) were read in part, hence `confidence: medium`.
- **Ids:** linked ids were taken from `attack-catalog.yaml`, `threat-models.md` and `report.md` §1 (A- and C- ids) on `main` at `59ae9ba`. `DEC-*` and `R-*` ids come from ARCH-0001.
- **Validation:** the three records were copied into a scratch checkout of library `main` (`e5efcb5`), with NIST replacing the existing stub, and `bin/validate` reported 0 errors and no new warnings. Nothing was committed to the library.

## Facts checked against primary sources

- **S-0166 venue.** `sources.md` gives "ACM AISec 2023 (venue from memory)". Crossref confirms it: *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security*, 2023-11-26, pp. 79–90, DOI 10.1145/3605764.3623985. arXiv lists no DOI or journal reference, and the digest is of arXiv v2 (2023-05-05).
- **S-0728 risk count.** The document itself says 78 risks (PDF pp. 5 and 36), confirming TM-014's "BIML-78". It is version 1.0, dated 1.13.20, and licensed CC BY-SA 3.0.
- **NISTAML ids.** The full list was read from the report's taxonomy index (pp. x–xi). Leaves `.012`, `.013`, `.015`, `.018` and `.023` sit under more than one objective.
- **Tool licences** (GitHub API, 2026-11-08): ART MIT, garak Apache-2.0, greshake/llm-security MIT. `Azure/counterfit` and `Azure/PyRIT` are archived, so they are not listed.

## What was rejected or fixed by hand, and why

- **NIST `bears_on`: DEC-001a and DEC-009, not DEC-008.** The library's existing stub (written for RPT-0009, tmodel #189) says DEC-008. DEC-008 is CWE/NVD lookup, and NISTAML ids are neither, so I judged DEC-001a (catalog ids on `AttackPattern`/`Weakness`) and DEC-009 (generic threat → product) the honest fit. The integration lane should decide which version the library keeps.
- **NIST "Published attacks" rated adjacent, not core.** It indexes 449 references but reports no attacks of its own. It is the map, not the evidence.
- **Greshake: no TM id.** Fig. 2 is a threat model of LLM-integrated applications, but `threat-models.md` has no entry for it, so "Existing AI threat models" is rated adjacent with no linked id rather than inventing one.
- **Greshake: AIT-068 (multimodal) is linked but flagged as weak.** The paper has only a limited LLaVA example (§5.3, Fig. 28).
- **BIML type `article`, body `other`.** It is an institute white paper with no DOI, so `paper` would overstate its review status and `academic` its publisher.
- **Tags.** The AI subject tags (`prompt-injection`, `ai-threat-model`, `ai-weakness-catalog` and so on) are LANES.md's *proposed* set, not yet in `schema/tags.yaml`. Role tags are from the controlled set: `normative` for NIST (RPT-0014 maps to its ids), `evidence` for Greshake, `prior-art` for BIML.
- **Reference expansion only partly done.** NIST's 449 references need a scripted title match, so this pass was not attempted. Greshake's taxonomy references are all in `sources.md`. BIML has four in-scope candidates missing (two Barreno papers, Kloft and Laskov 2007, and NISTIR 8269 draft); they are listed in its summary rather than created as stubs, because calibration records live in tmodel, not the library.

## Calibration points for the integration lane (#82)

1. **AIT entries missing S-0166.** Greshake et al. demonstrate a self-spreading email worm (§4.2.3), persistence through a memory tool (§4.2.4) and availability attacks (§4.2.6). Yet AIT-108, AIT-102 and AIT-112 do not list S-0166 in `sources`; only AIT-064 does. It is the earliest demonstration for all three.
2. **The NISTAML hierarchy is a DAG, not a tree.** A catalog schema that derives the objective from an id's prefix (`NISTAML.015` → `.01` availability) will mis-file `.012`, `.013`, `.015`, `.018` and `.023`. Store the violated objective as its own field. This is a point for #74's record shape.
3. **BIML ids mix attacks and design flaws.** Overfitting, reproducibility and encoding integrity are weaknesses with no attacker. A schema that only has `AttackPattern` cannot hold them; one with `Weakness` can.
4. **The NIST library record exists, with a different `bears_on` and topic** (`sagai`). Whichever version wins, the record should carry both RPT-0009 and RPT-0014 use.

## Human review

Not yet reviewed. @paria03 (review partner per LANES.md) reads at least three entries per record against the source, then signs `reviewed_by` in each `summary.md`. Until then each record is a hypothesis (R-018).
