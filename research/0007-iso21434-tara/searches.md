---
schema: "archdoc/v1"
id: RPT-0007-searches
title: "RPT-0007 search log"
type: research
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: RPT-0007
---

# RPT-0007: search log

Every query run, so the survey is reproducible. One row per query.

| date | dimension | query | engine | notable hits → sources.md |
|---|---|---|---|---|
| 2026-10-01 | 1 | `"90.20" "International Standard under systematic review" "60.00" "International Standard under publication" stage codes` | web (via Claude Code) | only iso.org standard pages; iso.org/stage-codes.html refused automated access (HTTP 403), so the stage names in §1.2 still need a manual check |

## Tool runs

| date | command | input | result |
|---|---|---|---|
| 2026-10-01 | `shasum -a 256`; `pdfinfo` | the sponsor's copy of ISO/SAE 21434:2021 (see sources.md) | `73f99007...7cdf4`, the digest in #11 and in `iso-sae-21434-2021`; 87 pages; every page stamped "Downloaded from SAE International by Paul Lambert, Friday, September 25, 2026" |
| 2026-10-01 | `pdftotext` and `pdftotext -layout` | same | plain-text extracts for searching and checking; kept outside the repository, never committed |
| 2026-10-01 | `grep -o -E '\[RQ-[0-9]{2}-[0-9]{2}\]' \| sort -u \| wc -l`, and the same for RC, PM and WP | same | 101 RQ, 13 RC, 4 PM and 42 WP distinct identifiers (§1.3) |
| 2026-10-01 | count, per clause, of identifiers that start a line before Annex A | same | all 118 provisions and 42 work products are defined in Clauses 5 to 15. Clause 5: 17 provisions, 5 work products; 6: 34, 4; 7: 8, 1; 8: 8, 6; 9: 11, 7; 10: 13, 7; 11: 2, 1; 12: 3, 1; 13: 3, 1; 14: 2, 1; 15: 17, 8. Clause 15's provisions run RQ-15-01 to RQ-15-06, PM-15-07, RQ-15-08 to RQ-15-10, RC-15-11 to RC-15-14, RQ-15-15 to RQ-15-17 (§1.3) |
| 2026-10-01 | verb check on each provision's own sentence (text before its first NOTE or EXAMPLE); `resulting from` check on each work product | same | every RQ contains "shall", every RC "should", every PM "may"; all 42 work products name the provisions they result from (§1.3) |
| 2026-10-01 | `grep -i -E '\b(XML\|JSON\|schema\|ReqIF\|SysML\|file format\|data format\|exchange format\|machine-readable)\b'` | same | no matches: the standard defines no data format (§1.1) |
| 2026-10-01 | `grep -i -E 'UNECE\|R ?155\|WP\.? ?29\|type approval\|homologation\|regulation'` | same | no matches: no mention of UN Regulation No. 155 or vehicle type approval (§1.1) |
| 2026-10-01 | Python `csv` lookup by `reference`, and by "ybersecurity" in `title.en` for ISO/TC 22 deliverables | ISO Open Data `iso_deliverables_metadata.csv` (downloaded 2026-09-30) | ISO/SAE 21434:2021: stage 9020, edition 1, published 2021-08-31, 81 pages, no `replacedBy`. ISO 26262-3:2018: 9092, replaced by ISO/DIS 26262-3 (4000). ISO/SAE PAS 8475: 6000. ISO/SAE TR 8477: 6000. ISO/PAS 5112:2022: 9092, replaced by ISO/DTS 5112 (5020). ISO 24089:2023: 6060, plus Amd 1:2024 (§1.2) |
| 2026-10-01 | list of the entries in 3.1; `grep -i -c 'attack step'` | the standard | 3.1 defines 40 terms, and "impact rating" and "risk value" are not among them; "attack step" occurs 0 times (§2.1) |
| 2026-10-01 | search of Clauses 4 to 14 for 15.3 to 15.9, `[WP-15-01]` to `[WP-15-08]` and "TARA", each hit mapped to the provision it belongs to | the standard | TARA is used in 5.4 (RQ-05-02), 6.4 (RQ-06-07, PM-06-08, RQ-06-16, RQ-06-24), 7.4 (RQ-07-04), 8.3, 8.4 (RQ-08-04), 8.5 (RQ-08-05), 8.6 (RQ-08-07, RQ-08-08), 9.4 (RQ-09-03, RQ-09-04, WP-09-02) and 9.5 (§2.10) |
| 2026-10-01 | search of Clauses 10 to 14 for "Clause 15", 15.x, Clause 15 identifiers, "TARA", "risk value", "threat scenario", "attack path", "feasibility" and "damage scenario"; list of `[WP-09-xx]` they cite | the standard | two hits: RQ-11-01 item a (goals against threat scenarios and risk) and RQ-10-13 NOTE 9 (feasibility of access to an attack surface, not a TARA reference). Concept work products cited: Clause 10 WP-09-01, WP-09-06; Clause 11 WP-09-01, WP-09-03, WP-09-04, WP-09-06; Clauses 12 to 14 none (§2.10) |
| 2026-10-01 | search of Annexes G and H for "step", "aggregat", "combin", "maximum", "minimum", "formula" and "risk matrix" | the standard | Annex G mentions distinct steps of an attack only when rating the expertise and equipment factors (G.2.2), and aggregates factor values, not steps (Table G.6); Annex H has a risk matrix (Table H.8) and an example risk formula (Table H.10) (§2.8) |
| 2026-10-01 | `pdftoppm -png` of PDF pages 64, 73 and 74, read as images | the standard | Table E.1 grid, Table G.6 points and Table G.7 bands confirmed; Table G.7 lists two High bands, 0 to 9 and 10 to 13 (§3) |
| 2026-10-01 | WebFetch, then `curl -s -L https://www.first.org/cvss/v3.1/specification-document` and a text search | FIRST CVSS v3.1 specification | 7.1 gives "Exploitability = 8.22 × AttackVector × AttackComplexity × PrivilegesRequired × UserInteraction"; 7.4 weights AV 0.85, 0.62, 0.55, 0.2; AC 0.77, 0.44; PR 0.85, 0.62 (0.68), 0.27 (0.5); UI 0.85, 0.62. Python: lowest E 0.1211, highest 3.887, matching the standard's 0.12 to 3.89 (§3.2) |
| 2026-10-01 | WebFetch, then `curl -s -L https://www.first.org/cvss/v4.0/specification-document` and a text search | FIRST CVSS v4.0 specification | exploitability metrics AV, AC, AT, PR, UI; scoring heading "CVSS v4.0 Scoring using MacroVectors and Interpolation"; no "subscore", "sub-score" or "8.22" anywhere in the page (§3.2) |
| 2026-10-01 | Python: sum of the highest point value of each Table G.6 factor | the standard | 19 + 8 + 11 + 10 + 9 = 57 (§3.2) |
| 2026-10-01 | copy check: every run of 7 words in `report.md` that also occurs in the standard's text | `report.md` vs. the standard | after rewording, only names remain: clause titles, the ISO/TC 22/SC 32 name and the attack potential factor names (§1, §2) |
| 2026-10-01 | `git diff --stat 5b82f83 25a4cf8 -- records/iso/iso-sae-21434-2021/` | `library` repository | empty: the pinned library (`5b82f83`) and library `main` (`25a4cf8`) hold the same 21434 record (§7) |
| 2026-10-01 | word-for-word comparison of each catalog `text` with the extracted standard (whitespace, dashes and quotes normalized; then again ignoring list labels such as "a)") | `distilled/requirements.yaml` vs. the standard | 98 of 118 exact; 113 of 118 when list labels are ignored (§7) |
| 2026-10-01 | list-item check: list labels in each provision's span of the standard (up to the next identifier or heading) vs. the labels in the catalog text; every hit then read by hand | same | 12 entries cut short where a NOTE or EXAMPLE interrupts the list; 4 entries hold annex text instead of the provision (§7) |
