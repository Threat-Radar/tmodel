# research/

Versioned research reports. One directory per report: `NNNN-slug/`.

A report is **iterated in place** — its `version` and `updated` move together
(ARCH-0001 §9.5), and its history is the git history of the directory. We do not
spawn `report-v2.md` beside `report-v1.md`.

Each report directory holds:

```
report.md       the report itself (archdoc/v1 front matter, type: research)
dimensions.md   the search axes — what questions each section must answer
searches.md     the search log — queries run, when, by whom
sources.md      the source log — every source found, and its library record id
```

**References live in `library/`, not inline.** A report cites `library@<commit>`
records; the report summarizes and compares, the library holds the bibliographic
truth and the distilled technical detail. A reference that informs no decision is
a reference we did not need.

## Reports

| id | report | status |
|---|---|---|
| `RPT-0001` | [Threat-modeling landscape](0001-threat-modeling-landscape/report.md) | draft (I1) |
| `RPT-0011` | [Knowledge Graphs and NSF OKN](0011-knowledge-graphs-nsf-okn/report.md) | draft (#25) |
