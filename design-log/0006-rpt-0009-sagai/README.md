---
schema: "archdoc/v1"
id: DL-0006
title: "RPT-0009 SAGAI — AI-assisted source gathering and paper summaries"
type: process
status: draft
version: "0.3.0"
date: "2026-10-01"
updated: "2026-10-22"
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

## Report 0.3.0: requirements mapped to AI threats (2026-10-22)

### Question asked

With library#32 holding the FX-1 extractions of ETSI EN 304 223 and CISA AI-in-OT, the student asked for the RPT-0009 rewrite: build the report around which AI attack each requirement defends against (the sponsor's direction, previous entry), and test it on the EchoLeak model.

### What was produced

`report.md` 0.3.0, with `dimensions.md` 0.2.0 (new dimensions 7 and 8), `sources.md` 0.3.0 and `example-models/README.md` 0.1.1.
- **The front:** an abstract, Table 1 (the documents compared) and Table 2 (entries per NIST AI 100-2 E2025 class, with how many each document states itself).
- **§1 and §2:** a takeaway for §1, and a class-per-paper table for §2. §2's paper summaries are unchanged.
- **§3 (ETSI) and §4 (CISA) rewritten from the library records:**
  - phases, stakeholders, testability and the threats each names;
  - the provisions closest to prompt injection;
  - the output-side controls CISA adds.
  - §4's principle summaries and its 0.2.0 takeaway are kept, with a line on what is new.
- **§5, a worked example.** Table 3 places each EchoLeak stage against the nearest provisions and says how far each reaches.
- **§6 to §10:** related guidance, a synthesis, a gap analysis (G1 to G12, routed), the open questions for the sponsor, and method and limits.
- **`sources.md`:** record ids for the five SAGAI papers, the workshop, ETSI and CISA, which had all said "not yet a record". NIST AI 100-2 E2025 and ATLAS 2026.09 are now pinned with digests, and the EchoLeak sources are added.

### How it was checked

- Every count in Tables 1 and 2 and in §3 and §4 was computed from the library#32 records. Table 2's entry counts match the extraction session's own table.
- The claim that neither document mentions retrieval, rendering, links or images, content security policies or exfiltration was checked by searching both source PDFs. Each names prompt injection exactly once: ETSI in its Introduction (p. 5), CISA in Table 2.
- Every provision quoted in §3 to §5 was read in `requirements.yaml`.
- `bin/validate-archdoc`: this change's files pass. The one error is `main`'s `project/SOW-0001`.

### Choices the agent made, open to review

- **Table 3's "how far it reaches" column** is the agent's reading, made by matching ids at ATLAS's parent-technique level and then reading the provision text.
- **§2's paper summaries are kept as accepted on 2026-10-01**, with only a class table added.
- **§4's takeaway is kept and marked as accepted in 0.2.0**, with one new sentence.

### What a human accepted

- The student asked for the rewrite. The student's review is for clarity; a technical review is pending (@Clovier, the AI-lane review partner, is requested).

### What was rejected, and why

- **"4 principles in 12 subsections"** (0.2.0, §4). The record shows 13 numbered subsections, 1.1 to 4.2.
- **"None of the 15 entries mapped to either prompt-injection class"** (draft). It counted entries mapped to both classes twice; there are 10 distinct entries.
- **"ETSI names indirect prompt injection … (§1)"** (draft). The record locates it in the Introduction, p. 5.
- **"Those are the four bypasses EchoLeak chained"** (draft). Only three of the four are on the output channel; the fourth, the injection classifier, is input-side.
