---
schema: "archdoc/v1"
id: DL-0011-lane-catalogs-schema
title: "RPT-0014 lane catalogs-schema: WAVE 1 calibration (S-0855, S-0166, S-0728)"
type: process
status: draft
version: "0.2.0"
date: "2026-11-08"
updated: "2026-11-10"
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

- **Tooling:** Claude Code (Opus 5.5) on the lane owner's account, in one interactive session on 2026-11-08 and a second on 2026-11-10 for the review fixes. No `rpt0014-extract` or `rpt0014-sweep` workflow was run (those are WAVE 2), and no subagents.
- **Token and effort settings:** the session's default effort, with no `effort` override, since no workflow was run. Tokens were not metered per unit; the work used part of two interactive sessions.
- **Sources:** fetched from the `pdf-manifest.tsv` URLs, except NIST, which came from the direct `nvlpubs.nist.gov` PDF that the manifest's DOI resolves to. All three SHA-256 digests match the manifest.
- **Reading:** text extracted with `pypdf` 5.4.0, then targeted reading. Each summary's *Limits* section names the sections read. Greshake et al. was read nearly in full; NIST (127 pp.) and BIML (42 pp.) were read in part, hence `confidence: medium`.
- **Ids:** linked ids were taken from `attack-catalog.yaml`, `threat-models.md` and `report.md` §1 (A- and C- ids) on `main` at `59ae9ba`. `DEC-*` and `R-*` ids come from ARCH-0001.
- **Validation:** the three records were copied into a scratch checkout of library `main` (`e5efcb5`), with NIST replacing the existing stub, and `bin/validate` reported 0 errors and no new warnings. After the review fixes, it was re-run on library `main` at `20399c2`: 687 records, 0 errors, and the same 99 warnings as `main` alone. Nothing was committed to the library.

## Facts checked against primary sources

- **S-0166 venue.** `sources.md` gives "ACM AISec 2023 (venue from memory)". Crossref confirms it: *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security*, 2023-11-26, pp. 79–90, DOI 10.1145/3605764.3623985. arXiv lists no DOI or journal reference, and the digest is of arXiv v2 (2023-05-05).
- **S-0728 risk count.** The document itself says 78 risks (PDF pp. 5 and 36), confirming TM-014's "BIML-78". It is version 1.0, dated 1.13.20, and licensed CC BY-SA 3.0.
- **NISTAML ids.** The report defines 25 leaf ids. The taxonomy index (pp. x–xi) lists 23; `.016` and `.017` are defined only in §3.4.1 (p. 51), which a text search of the whole report found. Leaves `.012`, `.013`, `.015`, `.018` and `.023` sit under more than one objective.
- **Tool licences** (GitHub API, 2026-11-08, re-checked 2026-11-10): ART MIT, garak Apache-2.0, greshake/llm-security MIT, PyRIT MIT. PyRIT's original `Azure/PyRIT`, which NIST cites as [364], is archived with a notice that it moved to `microsoft/PyRIT`, which is active. `Azure/counterfit` is archived with no successor, so it is not listed.

## What was rejected or fixed by hand, and why

- **NIST `bears_on`: DEC-001a and DEC-009, not DEC-008.** The library's existing stub (written for RPT-0009, tmodel #189) says DEC-008. DEC-008 is CWE/NVD lookup, and NISTAML ids are neither, so I judged DEC-001a (catalog ids on `AttackPattern`/`Weakness`) and DEC-009 (generic threat → product) the honest fit. The integration lane should decide which version the library keeps.
- **NIST "Published attacks" rated adjacent, not core.** It indexes 449 references but reports no attacks of its own. It is the map, not the evidence.
- **Greshake: no TM id.** Fig. 2 is a threat model of LLM-integrated applications, but `threat-models.md` has no entry for it, so "Existing AI threat models" is rated adjacent with no linked id rather than inventing one.
- **Greshake: AIT-068 (multimodal) is linked but flagged as weak.** The paper has only a limited LLaVA example (§5.3, Fig. 28).
- **BIML type `article`, body `other`.** It is an institute white paper with no DOI, so `paper` would overstate its review status and `academic` its publisher.
- **Tags.** The AI subject tags (`prompt-injection`, `ai-threat-model`, `ai-weakness-catalog` and so on) are LANES.md's *proposed* set, not yet in `schema/tags.yaml`. Role tags are from the controlled set: `normative` for NIST (RPT-0014 maps to its ids), `evidence` for Greshake, `prior-art` for BIML.
- **Reference expansion only partly done.** NIST's 449 references need a scripted title match, so this pass was not attempted. Greshake's taxonomy references are all in `sources.md`. BIML has four in-scope candidates missing (two Barreno papers, Kloft and Laskov 2007, and NISTIR 8269 draft); they are listed in its summary rather than created as stubs, because calibration records live in tmodel, not the library.

## Calibration points for the integration lane (#82)

1. **AIT entries missing S-0166.** Greshake et al. demonstrate a self-spreading email worm (§4.2.3), persistence through a memory tool (§4.2.4) and availability attacks (§4.2.6). Yet AIT-108, AIT-102 and AIT-111 do not list S-0166 in `sources`; only AIT-064 does. It is the earliest demonstration for all three. AIT-111 is the sharper case: it carries `NISTAML.017`, for which NIST's only source is S-0166. The same holds for AIT-088, which carries `.016`. (The first version named AIT-112 here, but §4.2.6's time-consuming tasks are `.017`, which the catalog files under AIT-111.)
2. **The NISTAML hierarchy is a DAG, not a tree, and the index is not the id list.** A catalog schema that derives the objective from an id's prefix (`NISTAML.015` → `.01` availability) will mis-file `.012`, `.013`, `.015`, `.018` and `.023`, so store the violated objective as its own field. An importer that reads ids from the index will miss `.016` and `.017`. Both are points for #74's record shape.
3. **BIML ids mix attacks and design flaws, and are unique only as full strings.** Overfitting, reproducibility and encoding integrity are weaknesses with no attacker. A schema that only has `AttackPattern` cannot hold them; one with `Weakness` can. Two numbers each name two risks (`data:4`, `inference:3`), and three cross-references use the wrong number, so a BIML id has to be stored and matched as the full `component:n:descriptor` string.
4. **The NIST library record exists, with a different `bears_on` and topic** (`sagai`). Whichever version wins, the record should carry both RPT-0009 and RPT-0014 use.

## Corrected after review (2026-11-10)

@Clovier's review on #228 found five errors and made two optional points. Each was re-checked against the PDF, `attack-catalog.yaml`, `sources.md` or the GitHub API before it was fixed, and all of them held.

| # | Error | Root cause | Fix |
|---|---|---|---|
| 1 | Two NISTAML ids missing (`.016`, `.017`) | The id list was taken from the index, and the text extraction split one id across a line break (`NIS` / `TAML.016`) | 25 leaves. Both ids are added to NIST and to Greshake, which NIST cites for both. Greshake's availability link moves from AIT-112 to AIT-111 |
| 2 | "Every catalog entry carries a NISTAML id" | Assumed, not counted | 98 of 146 (60 up to AIT-075, 38 after), with the scope notes of the other 48, in the NIST summary and `record.yaml` |
| 3 | NIST cryptography rated `none`, "only as a contrast" | §§2.1.2, 3.2.3 and 4.2.1 were not read | Rated `adjacent`, naming the three cryptographic mitigations |
| 4 | PyRIT called archived, and §3.6 said to list no tools | The redirect notice was missed; §3.6 was misread | PyRIT listed at `microsoft/PyRIT`; §3.6 names Garak and PyRIT |
| 5 | BIML's "already present" list wrong for three entries, and only 4 of 12 missing references found | BIML's reference list was not compared with `sources.md` title by title | All 35 references checked by title and author: 12 present, 12 missing and in scope |
| opt. | BIML ids not unique | The id format was assumed sound | Recorded in BIML's Limits and calibration point 3. Two more cases than the review named were found (`data:4`; `[inference:3:hosting]`) |
| opt. | Token and effort settings missing | Omitted | Added under "How it was run" |

Errors 1 and 5 share a cause: a list built from a partial read was presented as complete. The NIST summary now says which sections were read, and the BIML expansion now covers every reference.

## Human review

@Clovier checked the three records against the sources on 2026-11-09 (#228). Not yet signed. @paria03 (review partner per LANES.md) reads at least three entries per record against the source, then signs `reviewed_by` in each `summary.md`. Until then each record is a hypothesis (R-018).
