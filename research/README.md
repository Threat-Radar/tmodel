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
| `RPT-0002` | [Threat model frameworks](0002-threat-model-frameworks/report.md) | draft (#6) |
| `RPT-0003` | [Threat-modeling products](0003-threat-modeling-products/report.md) | draft (#7) |
| `RPT-0004` | [Product composition](0004-product-composition/report.md) | draft (I1) |
| `RPT-0007` | [ISO/SAE 21434 and TARA](0007-iso21434-tara/report.md) | draft (#11) |
| `RPT-0005` | [Schema representations](0005-schema-representations/report.md) | scaffold (plan in dimensions.md; #39) |
| `RPT-0009` | [SAGAI & AI-security specs](0009-sagai/report.md) | draft (#13) |
| `RPT-0011` | [Knowledge Graphs and NSF OKN](0011-knowledge-graphs-nsf-okn/report.md) | draft (#25) |
| `RPT-0012` | [GUI, platform & implementation stack](0012-gui-platform-stack/report.md) | scaffold (plan in dimensions.md) |
| `RPT-0013` | [Secure Development Lifecycle & conformance](0013-sdl-conformance/report.md) | scaffold (plan in dimensions.md) |
| `RPT-0014` | [AI threat model: attacks, threat models, enumerations](0014-ai-threat-model/report.md) | in progress (#71) |
