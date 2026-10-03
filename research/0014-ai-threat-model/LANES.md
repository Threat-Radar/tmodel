---
schema: "archdoc/v1"
id: RPT-0014-lanes
title: "RPT-0014 work lanes: extraction and round-2 sweeps across five accounts"
type: research
status: draft
version: "0.1.0"
date: "2026-10-03"
updated: "2026-10-03"
record: RPT-0014
issue: 71
---

# RPT-0014 work lanes

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

| lane | owner | extraction units (`rpt0014-extract`) | sweep (`rpt0014-sweep`) | reviews |
|---|---|---|---|---|
| agentic and MCP | @paria03 | `TM-058-csa-maestro`, `TM-059-owasp-agentic-threats`, `TM-060-owasp-mas-guide`, `TM-064-agentic-threat-frameworks`, `TM-084-mcp-threat-models`, `S-papers-prompt-injection` | `news-2026` | Mai's units |
| catalogs and schema | @Maimcghee | `TM-004-nist-ai-100-2-e2025`, `CAT-mitre-atlas-2026-09`, `CAT-owasp-llm-top10-2025`, `TM-041-cosai-risk-map`, `TM-043-dasf-and-safe-ai` | `venues-ml` | Tyler's units |
| supply chain and infrastructure | @Clovier | `TM-099-rand-model-weights`, `TM-026-aws-threat-composer-genai`, `S-papers-supply-chain-infra`, `S-papers-poisoning-backdoor`, `S-papers-jailbreak-alignment` | `national-intl` | Krishna's units |
| ML risk and assets | @kriishnaa-18 | `TM-014-biml-78`, `TM-024-biml-81-llm`, `TM-012-microsoft-ai-threat-models`, `TM-005-asset-centric-models`, `S-papers-privacy-extraction` | `arxiv-2025-2026` | Paria's units |
| integration | @nymble | `S-papers-classical-adversarial` | `venues-security`, `critic-gaps` | all lanes; then runs `rpt0014-integrate` |

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
