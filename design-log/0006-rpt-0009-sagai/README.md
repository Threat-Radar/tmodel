---
schema: "archdoc/v1"
id: DL-0006
title: "RPT-0009 SAGAI — AI-assisted source gathering and paper summaries"
type: process
status: draft
version: "0.2.0"
date: "2026-10-01"
updated: "2026-10-21"
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

## Sponsor direction and the first AI example model (2026-10-21)

### Question asked

After a meeting with the sponsor on 2026-10-21, the student relayed the direction: focus #39 on threats, vulnerabilities and weaknesses, specifically AI ones; build example models that shape the schema (#64), as for the car attacks (DL-0013); and integrate part B (this report) into that work instead of pausing it. The student chose these three readings from a list of options, which records them as relayed, not as the sponsor's words. The student asked for the first AI attack example model.

### What was produced

- **`research/0009-sagai/example-models/em-01-echoleak-m365-copilot.yaml`**, a model of EchoLeak (CVE-2025-32711), written against the proposal schema in tmodel#130.
  - The chain runs from CWE-74 and an AI-proposed CWE-1427, through the CVE and twelve MITRE ATLAS techniques, to one threat, one damage scenario and five mitigations.
  - The attack steps follow ATLAS case study AML.CS0059 (S00 to S11), and a second path covers the paper's one-click variant.
- **`research/0009-sagai/example-models/README.md`**: what the model shows, and seven AI-specific gaps (AI-1 to AI-7) plus DL-0024's P2, each routed to #64 or #74.
- **`report.md` 0.2.1**: the author id is now the GitHub id. It had been a personal-name slug, against the no-real-names rule (DL-0013 noted this on 2026-10-16).

### How it was checked

- **Primary sources, fetched 2026-10-21, with digests in the model's header:**
  - the researchers' paper (arXiv:2509.10540v1, CC BY 4.0), whose sections "Overview and Timeline", "Threat Model" and "Vulnerability Analysis" support every component and step;
  - the CVE record (CNA Microsoft: CWE-74, CVSS 3.1 9.3; CISA-ADP SSVC: Exploitation none);
  - ATLAS 2026.09, pinned at tag v2026.09: the case study's steps, techniques and tactics, and which ATLAS mitigations cover them;
  - CWE 4.20: CWE-74 is a Class with usage DISCOURAGED, and CWE-1427 a Base with usage ALLOWED.
- **Validation:** `linkml-validate` (LinkML 1.12.1) against #130's proposal container found no issues. DL-0024's `check-refs.py` found 87 objects and 167 references, all resolving, and a planted dangling reference failed it.

### Choices the agent made, open to review

- **ATLAS's steps, not the paper's four.** ATLAS's twelve steps include preparation (crafting, staging) and give a technique and a tactic per step. The paper's Steps 1 to 4 are folded into S00, S08, S09 and S10.
- **`AML.T0051.002` (Triggered), not `.001` (Indirect).** ATLAS classifies EchoLeak's injection as triggered, because it runs when the user later invokes Copilot. The model follows ATLAS.
- **Mitigations other than Microsoft's fix are suggestions** (`mitigation_status: planned`). They are taken from the paper's "Defensive Solutions", and two are linked to ATLAS mitigations (AML.M0033, AML.M0026).

### What a human accepted

- The student asked for this work. The student's review is for clarity. The model is AI-drafted and unreviewed; a technical review is pending.

### What was rejected, and why

- **"Chat logs, OneDrive files, SharePoint content, Teams messages"** as the exposed data. A search-engine summary of secondary articles gave this list, not the paper. The model uses the paper's "emails and files" and ATLAS's "emails, files, or project details".
- **`https://atlas.mitre.org/studies/AML.CS0059` as evidence.** It returns HTTP 404 to a direct request. The model cites the pinned ATLAS data file instead.
- **RPT-0005 G2 as an absolute.** G2 says no released format has an ordered attack path, but ATLAS case studies order their steps (`leads-to`). ATLAS was outside RPT-0005's scope, so this is passed to RPT-0005 as an exception (gap AI-2) rather than counted as an error there.
