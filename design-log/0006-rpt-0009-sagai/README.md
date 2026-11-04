---
schema: "archdoc/v1"
id: DL-0006
title: "RPT-0009 SAGAI — AI-assisted source gathering and paper summaries"
type: process
status: draft
version: "0.5.2"
date: "2026-10-01"
updated: "2026-11-04"
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

## References traced and SAGAI'25 confirmed, report 0.3.1 (2026-11-02)

### Question asked

#189's first box, after Part B moved there from #39: every item in RPT-0009 §6, and so every source in `sources.md`, gets a library record (FX-1 or an honest stub) or a written reason it has none, with G12 routed. The student asked the agent to move on to this step. While those PRs waited for review, the student asked what else could be done, and the agent took #189's second box: whether `systems-security-agentic-computing` (arXiv 2512.01295) is a SAGAI'25 output, adding `part_of: sagai-workshop` only if it is.

### What was produced

- **library#40:** ten honest stubs and one not-useful record, each pinned by SHA-256 with a written summary. None is extracted.
  - the two reference schemes: `nist-ai-100-2-e2025` and `mitre-atlas` (2026.09);
  - the ETSI and agency documents: `etsi-ts-104-223`, `etsi-tr-104-128`, `etsi-tr-104-048`, `ncsc-secure-ai-guidelines-2023` and `uk-ai-cyber-security-code-2025`;
  - the papers: `echoleak-zero-click-prompt-injection`, `agent-security-systems-problem` (§2.6) and `securing-future-genai-policy-technology` (§2.7);
  - `fraunhofer-iese-sagai`, `not-useful`.
  - `etsi-en-304-223` now `supersedes: [etsi-ts-104-223]`, as its own comment asked once the TS was held, and the `sagai` topic lists all of these.
- **`sources.md` 0.4.0:** a record id or a written reason in every row; no row says "not yet a record".
- **`report.md` 0.3.1:** the status line, Table 1, §2, §6, G12, open question 6, the `library_commit` note and `issue: 189`.
- **SAGAI'25 confirmed (second box).** arXiv 2512.01295v1 (2025-12-01) opens: "The IEEE Secure Generative AI Agents 2025 workshop (SAGAI; co-located with the IEEE Symposium on Security and Privacy) set out to explore how computer-security research and practice can help inform and advance agentic computing security. This report captures those discussions …". In library#40 the record moves from `see_also` to `part_of: sagai-workshop`, with v1's digest in its header. `agent-security-systems-problem` stays `see_also`. The report's §1, §2.5, Table 1, the §1 takeaway and open question 7 (now answered) follow, as do `sources.md` (0.4.0) and `searches.md` (0.3.0, today's queries logged).

### How it was checked

- The NIST and ATLAS files hash to the digests 0.3.0 already recorded. Every other file was hashed twice (a download, then `bin/ingest --fetch`), and the two agree.
- Metadata was taken from the publishers' own pages or files: NIST's CSRC page (authors, March 2025, DOI); ATLAS's YAML header (2026.09, format 6.0.0) and `LICENSE` at the tag (Apache-2.0); ETSI's `deliver` listings (each document has only V1.1.1); the NCSC and GOV.UK landing pages; arXiv's abstract pages.
- The EN's History table names TS 104 223 V1.1.1 as its first publication (`etsi-en-304-223` `distilled/normative.md`), which supports the `supersedes` link.
- ETSI TS 104 216's `deliver` directory returns 404, so it is unpublished.
- The report was searched for NIST AI 100-1, OWASP, NSA and Barrett. Only Barrett appears, as a lead in §2.7, so "no claim rests on it" holds for each source given no record.
- Library: `bin/validate` reports 0 errors, and 11 more records count as written; `bin/export` and `bin/reindex` show 612 records and 0 dangling. tmodel: `bin/validate-archdoc` passes.
- **SAGAI'25:** the full HTML text of 2512.01295 v1 and v2 and of 2605.18991 v1 and v2 was searched for "SAGAI". Only 2512.01295v1 names it. The 2026-09-28 search read v2, which explains its "none names SAGAI". The v1 author list (Christodorescu, Fernandes, Hooda, Jha, Rehberger, Shams) was read from the HTML. The SAGAI'25 site lists five organizers, four of them authors, and its program has Rehberger giving a talk. The site itself links to no paper, so the evidence is the paper's own sentence.

### Choices the agent made, open to review

- **Stubs, not reasons, for the ten.** A stub costs a digest and a short summary and lets a cited id resolve. Reasons were kept for sources no claim rests on (NIST AI 100-1, OWASP, NSA, Barrett), for a committee (TC SAI), for an unpublished draft (TS 104 216) and for #8's SBOM documents.
- **`cited_by` left empty.** `docs/references.md` reserves it for our own documents, although about 20 library records list library ids there.
- **Summaries say only what was checked.** Content comes from RPT-0009's existing readings (§2.6, §2.7, §5) or the publishers' pages. TR 104 048's summary says its content was not read.
- **The record keeps pinning v2.** v2 is the text §2.5 summarizes. v1, the workshop report as first issued, gets its digest in the record's header rather than a record of its own.
- **Answered without asking the sponsor.** 0.3.0 planned to ask @nymble. The paper's own sentence settles it, so question 7 is marked answered rather than removed.

### What a human accepted

- The student asked for this step. Nothing here is technically reviewed yet; library#40 and this PR need a reviewer.

### What was rejected, and why

- **"Neither has a library record"** (§6) and **"have no record of their own"** (§6). Both are stubs now.
- **"§2.6 and §2.7 have none"** (Table 1, §2). Both have stubs.
- **"probable SAGAI'25 output"** and **"the paper itself does not name the workshop"** (§2.5), and "unconfirmed" (`sources.md`). Its v1 names the workshop and calls itself its report.
- **"a SAGAI'25 panelist"** (§2.5). The program has Rehberger giving a talk in the session on attacks on agentic systems.
- **"SAGAI'25 position papers (2)"** (Table 1, §1 takeaway). One is the workshop's report; the other, 2605.18991, does not name the workshop.

## Adversarial review and fixes, report 0.4.0 (2026-11-02)

### Question asked

#189's third box: an adversarial review by a fresh agent (Phase 4 of #39's playbook), with the findings fixed and the rejections recorded here. The student started the review while #195 and library#40 waited for reviewers. When it reported, the student asked how to go faster. Neither PR had a review or a comment yet, so the student chose to put the fixes on the open PRs rather than in follow-ups, so that reviewers read the corrected version once. The clarity pass (#189's fourth box) went into the same change.

### What was produced

- **The review.** A general-purpose agent at maximum effort, read-only on both repositories, reviewed tmodel `84da598` and library `5a8171a`. It wrote down its own list of the sources it expected before reading the report's source list. It took about 55 minutes and about 490k tokens, and found 28 problems: 12 material and 16 minor.
- **`report.md` 0.4.0:**
  - the status line and the abstract;
  - Tables 1 to 3, with Table 3 now saying for each row whether its provisions were found by id or by reading;
  - §3 and §4, and §5 with a new item 4 on human oversight;
  - §6, §7 with a new conclusion, the gap table G1 to G12, and open questions 3, 4 and 8;
  - §10, and a new acronyms table.
- **`sources.md` 0.5.0** and **`searches.md` 0.4.0:** the sources the review found, and the searches it ran.
- **`example-models/README.md` 0.1.2:** the real-name fix, the case study relabelled as secondary, and #130's design log cited by path.
- **library#40:** five new stubs (`etsi-ts-104-050`, `aim-labs-echoleak-disclosure` and three SAGAI'26 papers), plus fixes to the existing stubs.

The table maps each first-round finding to what was done.

| Finding | What was done |
|---|---|
| F-01 TR 104 128 names prompt injection, RAG and exfiltration against EN provisions | Fixed: §3 quotes the guide's clause 6 by clause; the abstract, Table 2, §5 and §7 scope "only by inference" to the EN's own text |
| F-02 the prompt-injection list disagreed with the record | Fixed: the report now follows the record (5.1.2-2, 5.1.2-6, 5.1.3-1.2, 5.2.5-4.1, 5.4.2-1); 5.2.1-4.1 is discussed as the guide's reading, not ours |
| F-03 Table 3's stated method did not reproduce it | Fixed: a "Linked by" column; ETSI 5.2.1-4 and CISA R-0039 added at S10, the id matches the table had left out |
| F-04 CISA "no attack mapped" 79 should be 86 | Fixed, with the 7 framework-only entries named and the shares given (52%, 63%) |
| F-05 S05 under Poisoning | Fixed: removed; a note gives NIST's placement (NISTAML.015, §3.4.2) and NISTAML.036 and .039 for S07 to S10 |
| F-06 routing stale against ADR-0012 | Fixed: §3 and §4 route provisions to ADR-0012's Requirement; G8 and G9 restated against it; §7 names the accepted pair |
| F-07 SAGAI'26 papers on arXiv | Fixed: three stubs; §1, Table 1, Table 2 and §2.8 |
| F-08 ETSI TS 104 050 missing | Fixed as a stub and named in §6 and open question 4; its comparison with G1 to G10 is deferred |
| F-09 arXiv 2509.10540 is secondary | Fixed in §5, `sources.md` and the README; the Aim Labs disclosure is a stub |
| F-10 the catalogues name the output channel | Fixed in §5 item 1 and G11, which now routes catalogue mitigations to #74; the OWASP row in `sources.md` is revised |
| F-11 ATLAS 2026.10 | The drift is stated in §6 and G12; G2 now also routes to ADR-0007. Re-pinning is deferred (open question 8) |
| F-12 "defeat the human-oversight provisions by design" overstates | Fixed: Table 3 says "not engaged"; §5 item 4 and §7 give the case study's human-in-the-loop evidence |
| F-13 a real first name in the README | Fixed: "the sponsor (@nymble)" |
| F-14 duplicate DL ids | #130's DL-0024 is cited by path. The duplicate DL-0006 is not renumbered (below) |
| F-15 "RPT-0008 (#12)" does not exist | Fixed: §6 points to RPT-0014 (#71) |
| F-16 Organization omitted; G8 omits Affected entity | Fixed |
| F-17 "14 entries" were threats | Fixed |
| F-18 "neither mentions exfiltration" against CISA's egress entries | Fixed: scoped to the words, with CISA's egress and output-inspection entries named |
| F-19 R-0087 paraphrase widened | Fixed: "when mapping threat-actor behavior" |
| F-20 "all 38 id-and-name pairs" | Fixed: the claim no longer rests on a count; the review's count of 37 is given |
| F-21 to F-25 stub wording (ATLAS relationships, NIST erratum, EchoLeak venue, unpinned GOV.UK quotes, TR 104 048 poisoning) | Fixed in library#40 |
| F-26 G4's routing | Fixed: the CWE fit grade goes to DEC-008, the ATLAS join to #64 and #74 |
| F-27 CWE 5.0 | Noted in G4 and `sources.md`; the pins stay at 4.20 |
| F-28 `cwe-1426-genai-output-validation` unused | Deferred (below) |

### How it was checked

- **Every finding acted on was re-checked against its source first**, by the agent making the fixes, not by the reviewer. The checks used the bytes the reviewer downloaded, whose digests match the records, and the library records.
- **The counts were recomputed from the library records:**
  - CISA has 136 entries, 50 of them with an attack class, so 86 have none; 79 have no mapping at all.
  - The record's prompt-injection entries are exactly the five §3 lists.
  - Of ATLAS ids, only T0051 and T0025 occur in the records among Table 3's steps. S11's T0048 also matches at the parent level, spuriously; the second review found this.
  - ETSI has 6 Organization entries, 2 of them implied.
- **The quotes were found verbatim:** TR 104 128's clause 6 (clause headings name the EN provisions), NIST §3.4.2 and §3.4.3, the case study's Limitations and its Tables 2 and 3, and TS 104 050's scope notes.
- **ADR-0012** is on `main` (70b15ac), and its status is accepted.

### Second review of the fixes

A second fresh agent reviewed only the fixes (tmodel `84da598..1f15fa3`, library `5a8171a..f527c1e`), checking each first-round finding and spot-checking the new claims against the sources. It found 11 problems, 1 of them material. Of the 28 first-round findings, 24 were resolved, 3 were partly resolved and 1 (F-28) was legitimately deferred. All 11 were then fixed, after re-checking each one against its source:
- **R-01 (material): TR 104 128 was undercounted.** The report said the guide names prompt injection against five EN provisions. A search of all of clause 6 finds it in the examples for 15, RAG for 11 and exfiltration for 2 (5.1.2-6 and 5.2.1-4). The "five" came from the seven subclauses read in full, and the `searches.md` row recorded that partial result as a search of clause 6. Fixed in §3, Table 2's read-across, Table 3 (S07, S10), §7, `searches.md` and the library stub (`c3d6e3b`).
- **R-02 to R-11 (minor):**
  - the DEC-001b routing is scoped to `conformance_status`;
  - the §10 method line names §2.8;
  - "13 of them as attacks" is now "13 in its own words";
  - Table 3's id-match sentence covers S11's spurious T0048 match and adds T0068;
  - ATLAS 2026.10's M0020 → T0077 link is added;
  - the T0010 renames are added to §6 and open question 8;
  - the OWASP id now gives both editions (LLM02 in 2023, LLM05 in 2025);
  - "links or images" is now "in model output";
  - Table 2's SAGAI column gets the pentest paper's conventional and supply-chain objectives;
  - the GWU case study is named so that it is not confused with ATLAS's, and the acronyms and table introductions are completed.

### Choices the agent made, open to review

- **Fixing on the open PRs, not in follow-ups**, because neither had been reviewed yet.
- **The report follows the library record on 5.2.1-4.1.** The library review read its normative text as training-data hygiene. ETSI's guide reads it as covering prompts too, and the report gives both readings rather than changing an FX-1 mapping on guidance alone.
- **New sources are stubs, not readings.** TS 104 050 and the SAGAI'26 papers are summarized from their own front matter and abstracts only.

### What a human accepted

- The student approved the approach: fixes on the open PRs, stubs for new sources, deferring the ATLAS re-pin, and a narrower second review of the fixes. Nothing here is technically reviewed.

### What was rejected or deferred, and why

- **Corrected, by the agent itself: its own correction of AML.M0026's name.** The agent fixing the findings told the library helper that the review had M0026's 2026.10 name wrong. Its search had caught the next block's name instead, AML.M0027 ("Manage User-Delegated AI Agent Access"). The helper re-read the YAML. The review was right: M0026 is "Privileged AI Agent Permissions Configuration" in 2026.09 and "Manage AI Agent Service Access" in 2026.10.
- **Rejected: the review's quote from TS 104 050**, "defines what an AI threat is …". It is not in the text. The stub and §6 quote its scope notes instead.
- **Corrected: the review's "four" attack steps covered by the case study's human-in-the-loop check.** Its Table 3 marks five of six: the review missed the LLM scope violation column.
- **Confirmed after a first doubt: CS0059's new attribution.** ATLAS 2026.10 replaces 2026.09's `actor: Aim Labs` with an `attributed-to` link to AML.E0016, Cato Networks, which acquired Aim Security in 2025. The `mitre-atlas` stub records it.
- **Open, for the technical review: em-01's AML.M0026 link.** em-01 links its least-privilege suggestion to M0026 (privileged agent permissions). Copilot acted with the user's delegated access, so M0027 (single-user agent permissions) may fit better. em-01 is unchanged, because its mitigations are AI-drafted suggestions awaiting review.
- **Not pinned: the Aim Labs disclosure.** Its page returned HTTP 403 to `bin/ingest --fetch`. The stub has a URL but no digest, and no claim rests on its content.
- **Deferred: re-pinning ATLAS to 2026.10.** Four ids the records use are gone, so re-pinning means re-mapping both FX-1 records and em-01. The question goes to the sponsor (open question 8).
- **Deferred: re-pinning CWE to 5.0.** The em-01 claims hold in 5.0, per the review; the parent did not re-check this.
- **Deferred: TR 104 222 and a comparison of TS 104 050 with G1 to G10.** Neither changes a table now.
- **Deferred: extracting TR 104 128.** It would turn several `inferred` mappings into ETSI-guidance links, but it is a separate FX-1 job.
- **Deferred: F-28.** The parent did not confirm the review's reading of CWE-1426's guidance about prompt injection.
- **Not renumbered: the duplicate DL-0006.** `design-log/0006-iteration5-research-fold` and this entry share the id. Renumbering either would retarget existing citations, so the report cites this one by path. The repo owners can decide which keeps the number.
- **Passed on:** for RPT-0014 (#71), TS 104 050 updates and extends its GR SAI 001 entry, and ATLAS 2026.10 changes ids it may use.

## Human technical review, report 0.4.1 (2026-11-03)

@Clovier reviewed tmodel#195 at `2a45c45` (report 0.4.0, with the second review's fixes) and re-checked its claims against the sources:
- NIST AI 100-2 E2025 §3.4.2 and §3.4.3 (knowledge base poisoning, NISTAML.036, NISTAML.039);
- ATLAS 2026.09 against 2026.10: the removed ids, the T0010 and M0026 renames, M0020's new links, and CS0059's steps and attribution;
- TR 104 128 clause 6: prompt injection for the same 15 provisions, RAG for 11, exfiltration for 2, and nothing on rendering or markdown. This confirms R-01's count independently;
- the TS 104 050, GWU case study, SAGAI'25 and SAGAI'26 quotes, CVE-2025-32711's references and CWE, the two library#32 records' `maps_to`, and ADR-0012's status;
- no teammate's real name in the five files.

### What a human accepted

The review found no errors. Its two optional wording fixes were both accepted:
- **Table 2's read-across:** "Of the 50 CISA entries with an attack class" contradicted the "Not an attack" row those 18 belong to. The review suggested "with any mapping"; the report says "outside the 'No attack mapped' row" instead, because 7 more entries link only to a framework (the next bullet), so "any mapping" would count 57.
- **§9:** "Questions 1 to 6 are also in library#32" now says 3 and 6 are restated here.

The reviewer will approve after library#40 merges and the `library_commit` pin is updated, so that the approval is not dismissed by that push. em-01's M0026 question (above) was not taken up and stays open.

**Second comment (2026-11-04).** @Clovier confirmed both fixes, and noted that three commits on the branch (`1f15fa3`, `2a45c45`, `e4b0bd0`) had no `Signed-off-by` line, as CONTRIBUTING.md §9's DCO requires. Both are fixed in report 0.4.2:
- `library_commit` is pinned to `1fca00a`, library#40's merge on library `main`;
- the branch was rebased with `--signoff`, which adds the line without changing any file. The tree hash before and after the rebase is the same. The three commits are now `b6a0272`, `f71377b` and `c900957`. The older ids cited above (`1f15fa3`, `2a45c45`) are the first two of them before the rebase.
