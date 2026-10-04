---
schema: "archdoc/v1"
id: RPT-0014-extractions
title: "RPT-0014 extractions: full extraction of AI threat models and key attack papers"
type: research
status: draft
version: "0.1.0"
date: "2026-10-03"
updated: "2026-10-03"
record: RPT-0014
issue: 73
---

# RPT-0014 extractions (#73)

These are full extractions of the published AI threat models and key attack
papers cataloged in [`../threat-models.md`](../threat-models.md) and
[`../sources.md`](../sources.md). They adapt the library's full-extraction
standard (FX-1) to two new source kinds. A summary is not an extraction. The
target is everything a threat-model generator would otherwise have to re-read
the source to find, in a form a program can consume.

These directories are staging. #75 moves them into `library/` records. The
record shape is decided in #74 (DEC-001 and DEC-002 are open), so the YAML
keys here are working data, not a schema.

## Profile FX-TM: threat models, frameworks and catalogs

One directory, `TM-NNN-slug/`, per threat model.

| file | content | N/A allowed? |
|---|---|---|
| `summary.md` | what it is, scope, version and date, license, how it was read (PDF sha256, repo commit, page) | no |
| `decomposition.yaml` | components, data flows, trust boundaries, layers, each with its source name and locator | with reason |
| `assets.yaml` | every asset the model names, with locator; `explicit` or `implicit` | with reason |
| `actors.yaml` | attacker and persona model: goals, knowledge, access, capabilities | with reason |
| `threats.yaml` | **every** threat, risk or failure-mode entry: source id, name, description, locator, components, assets, actor, preconditions, impacts, lifecycle stage, linked controls, external ids | no |
| `controls.yaml` | **every** control or mitigation, with locator and the threat ids it addresses | with reason |
| `method.md` | how threats are elicited and rated: process steps and any scoring scheme | no |
| `examples/` | worked examples and case studies from the source, as fixture files | with reason |
| `crosswalk.yaml` | each threat mapped to `AIT-` ids ([`../attack-catalog.yaml`](../attack-catalog.yaml)), ATLAS 2026.09, OWASP LLM:2025 / ASI:2026, CWE 4.20 and NIST AI 100-2 E2025 ids, each with a confidence | no |
| `design-notes.md` | how the source bears on ARCH-0001 and DEC-001/002/003/009: what tmodel adopts, adapts or rejects; open questions | no |

`threats.yaml` and `controls.yaml` start with a completeness header:

```yaml
source_count: 78          # entries the source itself enumerates (counted, not estimated)
extracted_count: 78
reconciliation: ""        # REQUIRED when the two differ: say exactly why
license: "CC BY-SA 4.0"   # governs quoting (below)
```

## Profile FX-AP: attack papers

One directory, `S-NNNN-slug/`, per paper.

| file | content |
|---|---|
| `summary.md` | the contribution, plus a correction note if the `sources.md` summary was wrong |
| `attacks.yaml` | each attack or variant: algorithm steps; threat model (access, knowledge, capability) with locator; target asset and component; preconditions; success metric with the reported numbers and their table or figure locators; models and datasets; defenses evaluated and their results; limitations the authors state; code and data artifacts |
| `quotes.md` | verbatim definitions and threat-model statements, with locators |
| `crosswalk.yaml` | as in FX-TM |
| `design-notes.md` | what the generator must encode: preconditions, asset nodes, capability edges, evidence |

## Quoting and licensing

The repo is **public**. Quote in full only from public-domain sources (US
Government works such as NIST) or permissively licensed ones (Apache-2.0,
CC BY, CC BY-SA, MIT), with attribution. For all-rights-reserved sources (most
vendor PDFs, RAND, journal papers), paraphrase each entry and quote at most a
sentence or two, always with its locator. Never commit the source document
itself.

## Passes (each at maximum effort)

1. **Extract**: one agent per unit, reading the **source** (cached PDF, repo
   file, or page), never the summary.
2. **Verify**: a fresh adversarial agent that did not extract. It recounts the
   source entries, checks every locator and quote, and hunts for dropped
   entries and wrong mappings. It fixes the defects and records them in
   `verify.md` in the unit directory.
3. **Human review**: a person signs off on each unit. Until then every entry
   is a hypothesis (R-018).
