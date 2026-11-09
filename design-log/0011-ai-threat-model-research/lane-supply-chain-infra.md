---
schema: "archdoc/v1"
id: DL-0011-lane-supply-chain-infra
title: "RPT-0014 lane supply-chain-infra: WAVE 1 calibration (S-0855, S-0166, S-0728)"
type: process
status: draft
version: "0.1.0"
date: "2026-10-29"
updated: "2026-10-29"
record: DL-0011
issue: 134
---

# DL-0011 lane note: supply-chain-infra, WAVE 1 calibration

AI-assisted record for #134 (part of #80), as `CLAUDE.md` and the PR rules in
`research/0014-ai-threat-model/LANES.md` require.

## Question asked

Run LANES.md Step 1 for this lane: write the three shared calibration sources as
`record.yaml` and `summary.md` under
`research/0014-ai-threat-model/calibration/supply-chain-infra/<record-id>/`, without
looking at the other lanes' versions.

## What was produced

| Record | Source | Type, shelf | RPT-0014 ratings (attacks, threat models, enumerations, asset mapping) |
|---|---|---|---|
| `greshake-2023-indirect-prompt-injection` | S-0166 | paper, academic | core, adjacent, adjacent, core |
| `biml-ara-ml-2020` | S-0728 | paper, academic | adjacent, core, adjacent, core |
| `nist-ai-100-2-e2025` | S-0855 | spec, nist | adjacent, core, core, adjacent |

All three are `status: summarized`, `confidence: medium`, `owner: Clovier`,
`topic: ai-threat-model-supply-chain-infra` and `bears_on: DEC-001a`.

## How it was run

- **Agent and settings.** Claude Code in @Clovier's session, Opus model, max effort. One
  agent, no subagents and no workflow. Token use was not metered for this task; the same
  session did other work.
- **Sources.** Each PDF was read in full as text extracted with `pdftotext`. The PDFs came
  from the local cache (`bin/fetch-pdfs`), and their sha256 digests matched
  `pdf-manifest.tsv` on 2026-10-29. No PDF is committed.
- **Tools.** The skeletons came from the library's `bin/ingest`, run in a scratch copy of
  Threat-Radar/library at 6d9a51f, not in a library checkout. They were then filled by
  hand following the `summarize` skill and LANES.md Step 2 items 2 to 4.
- **Checks.** With the three records added to that scratch copy, the library's
  `bin/validate` reported 0 errors and no new warnings (568 records). The engine's library
  loader from PR #186 read the same copy with no problems.
- **Independence.** `calibration/agentic-mcp/` and `COMPARISON.md` were not opened. Ids
  were looked up only in the shared RPT-0014 files: `sources.md`, `threat-models.md`,
  `attack-catalog.yaml`, `enumerations.md`, `incidents.md` and `report.md`.

## Facts checked against primary sources

- **Greshake venue.** `sources.md` marks the ACM AISec 2023 venue "from memory". Crossref
  confirms it: AISec '23, pp. 79-90, DOI 10.1145/3605764.3623985, with the same author
  order as arXiv. arXiv v1 (2023-02-23) had a different title, "More than you've asked
  for"; the digest is v2.
- **Who cites Greshake.** CWE-1427 lists it as REF-1452 (CWE 5.0 page, 2026-10-28). NIST AI
  100-2e2025 cites it as reference [146] for six NISTAML ids in §3.4.
- **NIST edition.** The cached PDF's modification date, 2025-04-01, matches the corrected
  upload that CSRC records. NIST's errata, last updated 2025-06-03, corrects the GenAI
  availability entries in the id index on page x.
- **NIST references.** By DOI, [267] resolves to "Sponge Examples" and [410] to the paper
  of [408]. Checked with the arXiv API.
- **NIST lineage.** CSRC shows NISTIR 8269 (2019 draft), which BIML compares itself with,
  obsoleted on 2023-03-08 by the AI 100-2 E2023 draft.
- **BIML numbering.** A script checked every label in the text against the definitions: 79
  risks under 78 numbers, and four cross-references with the wrong number.
- **Names and repositories.** OWASP ML Top 10 entry names come from its GitHub repository.
  github.com/greshake/lm-safety redirects to greshake/llm-security (MIT). PyRIT moved
  from Azure/PyRIT, now archived, to microsoft/PyRIT.

## What was rejected or fixed by hand, and why

1. **Round-1 notes corrected or not repeated.**
   - `sources.md` gives NIST one list of seven attacker capabilities. The report has six
     for PredAI and four for GenAI; resource control is GenAI-only. The split matters for
     the AttackStep precondition proposal.
   - `sources.md` says BIML's ids "can be parsed with little effort". The pattern parses,
     but the numbers are not unique keys (see the BIML record's Limits).
   - `sources.md` says the 2025 edition "adds" GenAI sections. This was not repeated,
     because the 2023 edition was not compared.
2. **AIT links rejected.**
   - Greshake, AIT-092 (coding-agent prompt injection to code execution): the Copilot
     attack only steers completions and runs nothing.
   - Greshake, AIT-112 in favour of AIT-111: the catalog puts NISTAML.017, which NIST
     attributes to this paper, on AIT-111.
   - Greshake, AIT-068 (multimodal): §5.3 reports only limited success with LLaVA.
     AIT-071, AIT-073 and AIT-126 were also left out, because the paper does not
     demonstrate them as the catalog defines them.
   - BIML, AIT-005 (sensor injection): a one-phrase mention.
   - NIST: the 98 catalog entries that carry a NISTAML id were not listed. Only the
     attacks its supply-chain sections describe are linked, and the record says so.
3. **DEC-001a, not DEC-001.** ARCH-0001 §8 now lists DEC-001a and DEC-001b. Existing AI
   records in the library still say DEC-001.
4. **Schema over adapter.** The paper adapter writes `media_type` and `pages` at the top
   level. Schema v5 puts them under `content`, and existing records follow the schema, so
   these records do too.
5. **No `cites`.** Step 1 does not ask for it, and a partial list would look complete.
   `relations.cited_by` records two checked facts instead: NIST's reference [146] and the
   spotlighting record's `cites`.
6. **No `maturity`.** None of the three has a checked standing that fits the enum, so it
   stays unset, as the `summarize` skill says.

## Calibration points for the integration lane (#82)

- **`bears_on`:** DEC-001 or DEC-001a. The instructions could name the current id.
- **"Published attacks" for non-attack sources:** a taxonomy (NIST) and a risk analysis
  (BIML) were rated adjacent here, with links only to attacks the text names.
- **Linked ids for NIST:** a full list is 98 entries. This lane linked a supply-chain
  subset; the instructions could say which subset each lane should use.
- **Cryptography axis:** NIST rated adjacent, for the hash verification and attestation it
  recommends; BIML rated none, for passing mentions.
- **Greshake's exfiltration demos:** split here between AIT-066 (the user clicks a link)
  and AIT-091 (the agent sends mail with the user's authority).
- **Adapter versus schema** for `media_type` and `pages`, and whether calibration records
  should fill `cites`.
- **Side finding for report.md §6.** CWE 5.0 was published on 2026-10-28, and category
  CWE-1446 still has the same four members (1039, 1426, 1427, 1434). The report says the
  CWE AI Working Group targets CWE 5.0 for October 2026 "with more entries"; that sentence
  needs updating in the next integration pass. Lanes do not edit report.md.

## Human review

Pending. Under R-018 every rating, mapping and linked id in these records is a hypothesis
until @Clovier reads them and the review partner, @Maimcghee, checks them against the
sources. Record here what each accepts or rejects, and why.
