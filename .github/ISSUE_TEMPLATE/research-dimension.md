---
name: Research dimension
about: One search axis for a research report
title: "RESEARCH — <dimension>"
labels: research
---

**Report:** research/NNNN-<slug>/
**Dimension:** <e.g. methodologies | commercial products | OSS projects | academic papers | schemas & object models | UI comparison | risk metrics>

## Questions to answer

-

## What lands where

- **References** → `library/` records (one record per source; `bears_on` a `DEC-*`/`R-*`)
- **Summary + comparison** → the report's section for this dimension
- **Distilled technical detail** (schemas, field tables → toward code) → the record's `distilled/`

## Done when

- [ ] Sources ingested as library records
- [ ] Section drafted with links to implementations / repos / specs
- [ ] Report `version` + `updated` bumped
