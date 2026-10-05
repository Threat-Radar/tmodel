---
schema: "archdoc/v1"
id: RPT-0014-lanes
title: "RPT-0014 work lanes: extraction and round-2 sweeps across five accounts"
type: research
status: draft
version: "0.2.0"
date: "2026-10-03"
updated: "2026-10-05"
record: RPT-0014
issue: 71
---

# RPT-0014 work lanes

> **2026-10-05: the lanes run WAVE 1 now (#86).** WAVE 1 is a bibliography
> pass: summary, tags, applicability, and reference expansion. It is **not**
> full extraction, and it is not a KG load. The FX-TM / FX-AP extraction below
> is **WAVE 2** (#84). It waits until the five lanes produce similar results
> on the same calibration sources. The lane issues (#78-#82), the owners and
> the review pairs are unchanged.

## WAVE 1: what each lane does

Assignments: [`wave1-assignments.csv`](wave1-assignments.csv). Each row is a
`sources.md` id with its lane and batch. Batches are `calibration` (everyone
does them), `subset-1` (about 20 per student lane, 10 for integration) and
`later` (after the gate). The lane split is a keyword heuristic. If a source
belongs in another lane, say so in your PR rather than skipping it.

The work happens in the **library** repo (`Threat-Radar/library`), opened as
the Claude Code project root so that its skills load: `ingest-reference`,
`summarize`, `distill`.

### Step 1: calibration (everyone, same three sources)

| source | why it is in the calibration set |
|---|---|
| S-0855 NIST AI 100-2 E2025 *Adversarial ML taxonomy* | standard and catalog; public domain |
| S-0166 Greshake et al. *indirect prompt injection* | the seminal attack paper |
| S-0728 BIML *Architectural Risk Analysis of ML Systems* | a published AI threat model |

Each lane does all three **independently** and does not look at the others'
work. Commit them to the tmodel repo, not the library, under
`research/0014-ai-threat-model/calibration/<lane>/<record-id>/`
(`record.yaml` + `summary.md`). The integration lane compares the five
versions: tags, applicability ratings, linked ids and summary claims. It
records the differences in `calibration/COMPARISON.md`, and only the merged
best version becomes the library record. Similar results across the lanes is
the #84 gate; large differences mean the instructions get fixed before anyone
scales up.

### Step 2: subset-1 (your lane's rows)

For each source:

1. **Ingest:** `bin/ingest <type> <source>` (skill `ingest-reference`).
   Check `records/` first, because a few already exist (for example
   `csa-maestro-2025` and `spotlighting-indirect-prompt-injection`). Record
   `content.sha256` and the URL. The PDF stays in your local cache
   (`bin/fetch-pdfs` in tmodel).
2. **Summarize:** use skill `summarize` to write all six sections. Set
   `applicability` (security / cryptography / this_project), `bears_on` (only
   real `DEC-*` or `R-*` ids), `usefulness` (a negative verdict is a valid
   result), `confidence`, and `topic: ai-threat-model-<lane>`.
3. **Tags:** use the controlled tags from `schema/tags.yaml` where they fit,
   plus the AI subject tags in the next section.
4. **RPT-0014 applicability:** add this section to `summary.md`. It is
   many-to-many: one source can apply to many topics.

   ```markdown
   ## RPT-0014 applicability

   | Topic of interest | Rating | Linked ids | Why |
   |---|---|---|---|
   | Published attacks | core / adjacent / none / not assessed | AIT-… | |
   | Existing AI threat models | | TM-… | |
   | Weakness enumerations | | CWE-…, AML.T…, LLM0x:2025 | |
   | Attack → asset mapping | | asset / component ids from report §1 | |
   ```

   A topic you did not assess is `not assessed`, not `none`.
5. **Reference expansion:** list the source's cited references that are in
   scope and **not** in `sources.md`. Add each as a `status: stub` record with
   `relations.cited_by: [<this record>]`. Do not summarize stubs in this pass.

Open **one library PR per lane** for subset-1, with a body that says
`Part of Threat-Radar/tmodel#<your lane issue>`. Run `bin/validate` before you
push. Your review partner checks at least five of your records against the
source.

### Step 3: sweeps (optional this wave)

The `rpt0014-sweep` workflow (below) is the periodic search loop that #86
asks for. Run your lane's sweep only after subset-1 is in review.

### AI subject tags (proposed; promote to `schema/tags.yaml` by PR)

`prompt-injection`, `jailbreak`, `data-poisoning`, `backdoor`,
`model-extraction`, `membership-inference`, `model-inversion`,
`training-data-extraction`, `evasion`, `agent-security`, `mcp`,
`rag-security`, `ai-supply-chain`, `ai-infrastructure`, `side-channel`,
`deepfake`, `ai-enabled-offense`, `ai-threat-model`, `ai-weakness-catalog`,
`ai-incident`, `ai-benchmark`, `ai-governance`

---

# WAVE 2 (paused until the #84 gate): full extraction


The original lane plan from 2026-10-03 follows. The lanes, issues and
review pairs still hold. The extraction runs only in WAVE 2.

The work is split so that five Claude Code accounts share the load. Each
account also has its own WebSearch quota, which ran out in round 1 when one
account did everything. Every lane writes **only its own files**, and the
integration lane assigns ids, so the lane PRs never conflict.

## Setup (once per person)

```sh
git switch main && git pull                      # after PR #76 is merged
bin/wt new rpt0014-<lane>                        # your own worktree and branch
cd ../tmodel-wt/rpt0014-<lane>
bin/fetch-pdfs                                    # rebuild the PDF cache (~660 MB) in ~/tmodel-pdf-cache/ai-threat-model
```

The PDFs never enter the repo. `pdf-manifest.tsv` records each file's URL and
sha256. If you see `CHANGED`, the publisher re-issued the PDF; note it in your
PR description.

## Run (in Claude Code, opened at your worktree root)

Ask Claude to run the named workflows with your lane's arguments, for example:

> Run the `rpt0014-extract` workflow with args
> `{"units": ["TM-014-biml-78", "TM-024-biml-81-llm"], "today": "2026-10-05"}`

> Run the `rpt0014-sweep` workflow with args
> `{"sweeps": ["news-2026"], "today": "2026-10-05"}`

- **Run units one or two at a time.** Each unit runs an extractor and an
  adversarial verifier at max effort, which is several hundred thousand tokens.
  If your plan hits its usage limit, the workflow pauses and resumes. You can
  pass `"effort": "high"` to `rpt0014-extract`; say so in the PR.
- **Outputs:** extraction goes to `extractions/<unit>/` (including the
  verifier's `verify.md`). Sweeps go to `round2/<sweep>.md` plus CSVs and
  `round2/pdf-additions.tsv`.
- **Do not edit** `sources.md`, `incidents.md`, `threat-models.md`,
  `attack-catalog.yaml` or `report.md`. Put corrections in `verify.md` or the
  sweep file. The integration lane (`rpt0014-integrate`) merges them and
  assigns S-, INC-, TM- and AIT- ids.

## PR rules

- One PR per lane (or per batch of units), titled
  `RPT-0014 lane <name>: <units> (#<your lane issue>)`. The body says
  `Closes #<lane issue>` (or `Part of` for a partial batch). Commit with `-s`.
- Add a short `design-log/0011-ai-threat-model-research/lane-<name>.md`: what
  you ran, the token and effort settings, and what **you** rejected or fixed
  by hand, and why. The rejections are the evidence.
- **Human review (R-018).** Your review partner reads at least three entries
  per unit against the source, then signs `reviewed_by` in each unit's
  `summary.md`. An unsigned unit is a hypothesis.

## Lanes

| lane | issue | owner | extraction units (`rpt0014-extract`) | sweep (`rpt0014-sweep`) | reviews |
|---|---|---|---|---|---|
| agentic and MCP | #78 | @paria03 | `TM-058-csa-maestro`, `TM-059-owasp-agentic-threats`, `TM-060-owasp-mas-guide`, `TM-064-agentic-threat-frameworks`, `TM-084-mcp-threat-models`, `S-papers-prompt-injection` | `news-2026` | Mai's units |
| catalogs and schema | #79 | @Maimcghee | `TM-004-nist-ai-100-2-e2025`, `CAT-mitre-atlas-2026-09`, `CAT-owasp-llm-top10-2025`, `TM-041-cosai-risk-map`, `TM-043-dasf-and-safe-ai` | `venues-ml` | Tyler's units |
| supply chain and infrastructure | #80 | @Clovier | `TM-099-rand-model-weights`, `TM-026-aws-threat-composer-genai`, `S-papers-supply-chain-infra`, `S-papers-poisoning-backdoor`, `S-papers-jailbreak-alignment` | `national-intl` | Krishna's units |
| ML risk and assets | #81 | @kriishnaa-18 | `TM-014-biml-78`, `TM-024-biml-81-llm`, `TM-012-microsoft-ai-threat-models`, `TM-005-asset-centric-models`, `S-papers-privacy-extraction` | `arxiv-2025-2026` | Paria's units |
| integration | #82 | @nymble | `S-papers-classical-adversarial` | `venues-security`, `critic-gaps` | all lanes; then runs `rpt0014-integrate` |

Lanes line up with existing work: Paria with #12 (agentic threats); Mai with
schema (#9, #64) and the catalogs that feed #74; Tyler with product
composition and supply chain (#8) and ISO 21434 (#11); Krishna with
threat-modeling products (#7).

## Order

1. PR #76 merges (round 1).
2. The lanes run in parallel and each opens its PR.
3. Review partners sign their units.
4. The integration lane merges the lane PRs, runs `rpt0014-integrate`
   (report v0.3.0, `coverage.md`, `extractions/INDEX.md`), and opens the
   integration PR.
5. #74 (schema) starts from `extractions/*/design-notes.md` and the
   cross-unit vocabulary.
