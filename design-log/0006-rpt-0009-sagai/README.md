---
schema: "archdoc/v1"
id: DL-0006
title: "RPT-0009 SAGAI — AI-assisted source gathering and paper summaries"
type: process
status: draft
version: "0.1.0"
date: "2026-10-01"
updated: "2026-10-01"
record: DL-0006
---

# DL-0006 — RPT-0009: SAGAI sources and summaries

AI-assisted research record for #13 (per `CLAUDE.md`). Student: @Maimcghee, working
with Claude Code.

## Question asked

Find the SAGAI sources and their related specifications, set up RPT-0009 in the format of
RPT-0011, and summarize each source in plain English with section-level citations so a
person can check every claim.

## What was produced

- `research/0009-sagai/`: report, dimensions, search log, source log (25 sources).
- Report §2.1–2.7: summaries of the four SAGAI'24 papers, the probable SAGAI'25 output
  (arXiv 2512.01295), its follow-up (arXiv 2605.18991) and a related 2023 workshop report
  (arXiv 2407.12999); §4: summary of the CISA AI-in-OT guidance.
- Draft takeaways for §2 and §4, and the "what tmodel takes" cells in *At a glance*.

## What a human accepted

- §2.1 (Spotlighting): checked against the paper's §5.3 recommendations.
- §2.2 and §4: spot-checked against the image-attack paper's §VI results and CISA §4.1.
- Both takeaways, accepted 2026-10-01.

## What was rejected or corrected — and why

- **"SAGAI = ETSI SAI" was wrong.** The agent first read the target as ETSI's Securing AI
  committee (EN 304 223, the one document the student already had). @nymble's comment on
  #13 (2026-09-25) confirms SAGAI is the IEEE S&P workshop series. ETSI stays in the
  report only as a related source, because CISA's guidance (§3.4) cites it.
- **arXiv 2512.01295 is not confirmed as SAGAI'25's output.** It is written by the
  organizers plus a SAGAI'25 panelist and matches the workshop's stated output, but its
  text never names SAGAI. Labelled "probable" and raised with @nymble.
- **Fraunhofer's "SAGAI" excluded.** It is a different workshop series with the same
  acronym (software architecture and GenAI).
- **Liu et al. (§2.4) marked low relevance.** It covers image classifiers, not GenAI
  systems; kept because it is a SAGAI'24 paper.

## Next steps

Extract §3 (ETSI EN 304 223); ingest the sources as `library/` records; confirm the
SAGAI'25 attribution with @nymble.
