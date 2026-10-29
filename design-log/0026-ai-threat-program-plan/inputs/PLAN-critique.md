# PLAN-0004 draft: adversarial review

Reviewed: `PLAN-draft.md` (849 lines). Checked against tmodel `origin/main` @ 449f515, Threat-Radar/library `main` @ 6d9a51f, the open PRs and issues on GitHub (read-only), and the three input memos. Date: 2026-10-26.

## Verdict

The facts are mostly right: 27 of 32 checked claims hold, and none look invented. The plan covers every sponsor ask at least nominally, and it handles governance carefully: no DEC is accepted, R-018 badging runs throughout, there are no third-party PDFs, and the plan itself contains GitHub handles only (no personal names). **It is not yet decision-ready, and the in-semester part is not feasible as written.** Its whole operating model ("agents produce, humans sample, sponsor gates") rests on three things that the plan's own numbers, or the repo, contradict:

1. Human review capacity is about 20 records a week. The sampling rules in §3.4 need several times that.
2. The "human calibration baseline" behind the agreement metric is missing. The agentic-mcp records hold none of the fields being measured, and n=3 cannot support κ.
3. The sponsor's S3 load (during M3 week) and S4+ load go well beyond the 4–6 h/week the plan budgets.

It also misreports PR #130, which has delegated decisions already made rather than "three open choices." It embeds a de facto architecture spec in a PLAN, which goes against the "no parallel architecture doc" rule. It decides a taxonomy freeze that becomes schema without an ADR. It leaves three sponsor asks diluted:

- the link to weaknesses
- "professional-grade," with no release bar
- "other SDL processes," with no test

At 86 KB it is too long to rule on. It needs a one-page decision brief, and the appendices should move into the artifacts they specify.

**Counts:** critical 3 · major 18 · minor 20.

---

## Findings

### Critical

1. **Critical. §3.4 (lines 245–259), §W2 realism note (369–374), §6 (532–540). Review demand far exceeds review supply.**
   - **Supply:** 4 student reviewers × 5 records a week (line 257) ≈ 20 records a week. With Thanksgiving, S5–S7 gives about 50–60 records in total.
   - **Demand:**
     - L1 target of 120–200 human-checked records (line 372)
     - 100% human review of every `evidence.level` ≥ E3 (line 251), with L0 at 1,000–1,500 items. The corpus already holds 179 incidents, 46 advisories and 121 vendor-research items, so E3+ items alone likely run to hundreds.
     - a 15% sample of TT/AIT/catalog ids (about 150–225 items)
     - 100% review on every extractor/verifier disagreement
     - 20–30 AI-01 Assertions
     - 100% human read of every L2 page before its banner lifts
   - **Internal contradiction:** "L0 = `reviewed_by` empty" (line 363) is incompatible with "100% review of E3+" unless every E3+ item is promoted to L1. That promotion alone breaks the L1 estimate.
   - **Fix:**
     - Add a review-budget table: hours supplied per role per sprint against items demanded per rule.
     - Size L0 production to what can be sampled.
     - Restrict the 100% E3+ rule to items that drive displayed maturity or non-hypothesis status. Leave the rest hypothesis-badged.
     - State what is dropped when supply falls short.

2. **Critical. §3.5 items 1–2 (lines 263–271), §0 (line 75), Phase 0 exit (line 514). The calibration baseline the metric is anchored on does not exist.**
   - The agentic-mcp calibration (`research/0014-ai-threat-model/calibration/agentic-mcp/*`, PR #117) consists of `library-record/v1` records: applicability, tags, usefulness and a six-section summary. They hold no TT, no `evidence.level`, no versioned catalog ids and no DX-AI/1 fields. Jaccard on TT and κ on evidence level therefore cannot be computed against them.
   - They were produced by a student lane running the agent workflow. Calling them a "human calibration" overstates them.
   - κ on 3 sources is statistically meaningless (and undefined when one category dominates). "First 5 reviews, agreement ≥ 0.7 clears them" (line 272) is equally underpowered.
   - **Fix:**
     - In S3–S4, build a sponsor-authored DX-AI/1 gold set of at least 25–30 references, stratified by source type and X-class.
     - Report percent agreement with confidence intervals. Use κ only at n ≥ 30.
     - Treat the 3-source run as a smoke test, not a gate.
     - Rename the "agentic-mcp human baseline."

3. **Critical. §0 "First three moves" (78–87), §3.1 (line 200), §6 S3/S4 rows (534–535), §W7 (498), §3.4. Sponsor capacity is the single point of failure and it is not budgeted.**
   - **In S3 (M3 demo week)** the sponsor is asked to:
     - merge #159, library#22, #130, #167 and #162. #130 and #167 both rewrite `spec/schema/generated/*`, ARCH-0001, the CHANGELOG and OBJECT-MODEL.md, so expect rebase conflicts.
     - answer RPT-0014 §8 Q1–Q7
     - rule on Q-01–Q-04
     - file the epic plus 17 sub-issues and edit about 25 existing issues
     - land the privacy PR
     - review the agent tooling
     - and still own M3 integration
   - **From S4** the sponsor also has to:
     - double-check every student's first 5 reviews
     - decide every `first_of_kind` and `bears_on`
     - approve every proposed AIT
     - approve the profiles
     - draw the 60-item holdout
     - rate the AI-01 feasibility and S/F/O/P
     - read all L2 prose
   - None of this fits in 4–6 h/week.
   - **Fix:**
     - Add an hours-per-sprint budget for the sponsor.
     - In S3, keep only what unblocks: merge #159 and library#22, rule Q-01 and Q-03, and the privacy PR.
     - Move Q-04, the issue restructuring and the #130/#167 merges to S4.
     - Name a delegate for Assertion and sample double-checks.
     - State the fallback: which deliverable slips first.

### Major

4. **Major. §0 move 1 (line 80), §1.4 (170–172), §W0 Method. PR #130 is misdescribed.**
   - The plan says "rule on PR #130's three open choices." DL-0024 in the PR branch records that the sponsor *delegated four decisions* to @Clovier on 2026-10-22. They were made: A1–A7 and B1–B5 accepted, DataFlow joined to Components, names kept, pv-01/pv-02 left for review. ADR-0011 says `status: accepted`, `reviewed: false`. Nothing is left open; what remains is ratification.
   - The "governance smell" framing is also off. The delegation *was* the sponsor's act. The real gap is `reviewed: false` and no sponsor review on the PR.
   - **Fix:** Reword to "ratify or reverse the delegated ADR-0011 decisions (list the four) and record the sponsor review (`reviewed: true`)."

5. **Major. §W3 Method / Catalog pinning / Namespace (381–388), Appendix C, Appendix E, Q-05 (552). The plan embeds a parallel architecture spec.**
   - The PLAN contains:
     - a class list (Concept, TargetType, CatalogRelease/Entry, Incident, PublishedThreatModel, Reference, DomainProfile)
     - the bridge-edge set
     - the `evidence_role` and `epistemic_status` enums
     - the canonical id grammar
     - the "maturity derived, checker fails" rule
     - the phase→LifecyclePhaseCode mapping
     - the `kg/` layout
   - It labels all of this "proposal," but once committed under `project/` it becomes a rival design text. CLAUDE.md requires a diff against ARCH-0001 instead.
   - **Fix:** Move that content into a `spec/ARCH-0001-PROPOSAL-threat-knowledge-*.md` draft (or keep it in the memo) and cut W3 to its purpose, the deliverables, the dependencies, and a pointer to the proposal id.

6. **Major. §W2 Taxonomies (364), Q-11 (560), Q-05b (553). A schema decision is taken outside an ADR.**
   - Q-05b makes `component_kind`'s range "the `component-kind` concept scheme." Q-11 then freezes the target-type and phase schemes by "sponsor ruling; scheme file PR" at the end of S4.
   - Once a scheme is a slot range, freezing it is an object-model decision under DEC-001a or DEC-009. It needs an ADR.
   - **Fix:** Freeze only a research label set in `research/0014-*/schemes/` (versioned, with a remap script). State that adopting it as a schema range happens only through the Q-05/Q-05b ADR.

7. **Major. §5 Milestone guard (520–522) contradicts §6 S5 (536), and Phase 0 exit (514) contradicts §6 S4 (535).**
   - The guard says that in M4 week students give "only review samples (≈2 h)," yet §6 S5 also has each student launching and pushing a distill-batch PR.
   - The Phase 0 exit requires the "agreement run on 3 calibration sources reported," but §6 schedules that run in S4.
   - **Fix:** Either move the student distill batches to S7 or run them on A1. Move the agreement run out of the Phase 0 gate.

8. **Major. D4 (186), §W5 CI checks / DoD (469–470), §8 (577). The bibliography completeness metric has a loophole.**
   - "100% … for every entry **shown**" lets incomplete entries be hidden to pass.
   - The W5 DoD covers only the 1,181 RPT-0014 sources, not the ≈1,600–2,300 round-2 additions.
   - The sponsor asked that *every* reference has a summary and categorisation or artifact references.
   - **Fix:** Use the full held corpus as the denominator. Publish held vs shown vs complete. Fail the edition build if a held reference lacks a summary and at least one category or artifact link.

9. **Major. §W5 Views (467), D1, §8. Weaknesses are under-served relative to the ask ("bibliography coverage connected to weaknesses and threats").**
   - The six views are attack class, target type, phase, source type, year and catalog. None is a weakness view.
   - The completeness check never requires a weakness or threat link.
   - There are only 16 `LW-*` weaknesses, and RPT-0014 itself names "missing weakness layer" as its most consequential gap.
   - **Fix:**
     - Add a seventh view: weakness (CWE + `tr-weak`/`LW`) → AIT → references.
     - Add a metric: every AIT has at least one weakness link, or a dated "no weakness layer" note.
     - Require each reference to have at least one link to an AIT, weakness or incident.

10. **Major. §W7 Coverage round (498), §8 (574). The holdout is not independent.**
    - The 60 holdout items are drawn "over venue TOCs, ATLAS and AIID." Those are exactly the frames W1 harvests to 95–100% recall, so holdout recall mostly re-measures the harvesters.
    - The critic's "≤5 must-haves per 1,000" is not normalised to its 40-search budget.
    - **Fix:**
      - Draw the holdout from frames the harvesters do not use: practitioner talks (Black Hat, DEF CON AI Village, USENIX Enigma), vendor and research blogs, expert-nominated lists, and social leads.
      - Stratify it by X-class and TT.
      - Report the critic's yield per search and per budget.

11. **Major. §3.5, §A.2, §9 (no row). A correlated-error and model-bias risk is missing.**
    - The extractor, verifier, critic, minireport writer and "agent-vs-agent on two accounts" all run the same model family, so agreement measures consistency, not correctness.
    - The corpus also includes threat reports from the model's own vendor (RPT-0014 §8 item 4), which is a self-assessment risk.
    - **Fix:**
      - Add risk R15.
      - Make the human gold set (finding 2) the correctness anchor.
      - Run a cross-model or human verifier on a fixed sample.
      - Tag vendor-self-reported evidence and exclude it from maturity unless it is independently corroborated.

12. **Major. §9 R8 (606), Appendix D. Licensing of catalogs and API data is missing.**
    - R8 covers vendor and journal text only. W3 imports catalog *entries* into `kg/catalogs/*/entries.yaml` and republishes them as HTML:
      - OWASP GenAI material is CC BY-SA (share-alike obligations)
      - CSA MAESTRO and the CSA guides are not openly licensed
      - CWE has terms-of-use attribution
      - ATLAS is Apache-2.0 (NOTICE)
      - the AIID data licence needs checking
      - the Semantic Scholar API licence restricts redistribution (TLDRs)
    - **Fix:**
      - Keep a licence register per catalog and per API in the lock file.
      - Store ids, names and paraphrases only for non-permissive catalogs.
      - Extend the quote checker to imported catalog descriptions.
      - Add a risk row.

13. **Major. §3.2 (227), §W5 DoD (470), §5 Phase 2 (516), §3.3. Merge volume grows faster than merge capacity.**
    - "One branch per batch of 5," with stubs for all 1,181 sources plus round-2 items, comes to roughly 240+ library PRs this term.
    - Meanwhile M-a means twice-weekly sponsor merges, and M-b (delegated merges) only starts in Phase 2 after a branch-protection change. Library is also a fork synced with upstream.
    - **Fix:**
      - Generate stubs deterministically (no LLM) as a few bulk PRs.
      - Use batches of 25 for distilled profiles.
      - Decide M-b in S3, not Phase 2.
      - Count the expected PRs per week in §3.3.

14. **Major. §2 D1/D3, §8 Review row (578), §W4 DoD. "Professional-grade" has no release criterion.**
    - The reviewed/proposed ratio has "no target." No edition is ever defined as non-draft, and no reviewer from outside the project appears.
    - **Fix:**
      - Define edition grades, for example:
        - **draft:** banner on
        - **reviewed-core:** 100% of L0/L1 claims and all ITW/E4–E5 statements human-verified
        - **v1.0:** reviewed-core plus an external read of L0 and Parts IV/V by the faculty advisor or an industry reviewer, and two W7 passes
      - Tie D1–D4 "done" to those grades.

15. **Major. §0 (57–58), §W2 Method (362) and realism (369–374), §9 R6, §4.1.1 (323). Throughput and cost numbers are asserted, not derived.**
    - "5–8 agent-days," "60–120k tokens/reference at high effort for L0," "L0 1,000–1,500" and "2,800–3,500 references" have no stated basis.
    - L0 at high effort contradicts R6's "triage at low effort."
    - Venue-recall targets of ≥90–95% over ML/NLP venues for 2016–26 make 3,000 look low.
    - **Fix:**
      - Run a 20-reference pilot on A1 in S3 and record tokens, wall time and defects per reference.
      - Derive per-account weekly capacity from the usage meter.
      - Restate all tier targets from that pilot.
      - Show the venue-size arithmetic behind the corpus estimate.

16. **Major. D1 DoD (183), §4.1.1 (310), §W1 Inputs, §0 move 3, §5 Phase 0 (514). The plan treats uncommitted scratch memos as normative.**
    - The plan cites "B §1.4 evidence minima," "memo B §1," "B §4.5/§4.6/§6.2," "C R0" and so on. The memos stay uncommitted (line 103), so committed DoDs would point at nothing.
    - **Fix:** Inline every rule a DoD depends on, or commit the memos under `design-log/0026-*/` and cite them by path.

17. **Major. §W0 DoD (294), §1.4 (166–169), §10.2 (666). The privacy DoD cannot be met, and the scope is incomplete.**
    - "`grep` for project first names in `research/**` returns 0" will always fail: cited external authors in `research/0014-ai-threat-model/sources.md` (for example S-0091, S-0176, S-0318, S-0415, S-0745) share first names with project people.
    - Closed issue #37 also carries a personal name in its title and is missing from the retitle list.
    - Commit-author metadata on `main` carries real names. History cannot be fixed, but the plan should note it.
    - **Fix:** Scope the DoD to the actual leak sites: LANES.md lines 170–179, the titles of #36–#39 and the body of #84. Use the `identities.local.yaml` matcher, and extend `check_identities.py` (it currently scans only `docs/**/*.html`) to renderer inputs.

18. **Major. §8 Coverage row (572), §W7 Pass/stop (500), §4.1.1. The stop criteria may never terminate.**
    - "Round 2 passes when *every* axis meets target in two consecutive weekly runs **and** W7 passes." Axes such as non-English ≥10% (≈0% today), OECD ≥70%, ML-venue recall and SaTML ≥95% (≈8% today) may never all pass.
    - **Fix:**
      - Mark which axes gate and which are reported only.
      - Let a dated negative search or an accepted-gap record close a cell.
      - Add a timebox (for example, end of Phase 3), after which remaining gaps are published as gaps.

19. **Major. §W4 / §4.4.1 (403–458). The roll-up is structural, not synthetic, and the in-semester report scope is not prioritised.**
    - The tree implies about 100 L2 pages (52 class, 9 phase, 22–27 TT, P1–P8, control families, gaps), each needing a 100% human read.
    - No author or process is named for L1 part syntheses and the L0 findings ("what the L2s add up to"). "Individual reports roll up into final reports" is satisfied only by includes.
    - **Fix:**
      - Name the in-semester L2 set: the 9 Part IV phase pages plus 4–6 gap pages.
      - Define the L1/L0 synthesis step: an agent draft from the L2 evidence boxes, then a sponsor read, recorded in the design log.
      - Set a page budget per edition.

20. **Major. §4.4.1 Parts I–XII, Appendix C. The report and phase model have content gaps.**
    - There is no part on threat actors and attacker capability tiers (RPT-0014 already uses RAND tiers), no harm/impact taxonomy, and no regulatory and standards landscape (EU AI Act, NIST AI RMF, ISO/IEC 42001/27090; RPT-0014 §8 item 7).
    - The phase scheme has no design or architecture phase: `concept` and `architecture` in `LifecyclePhaseCode` are unmapped, although architecture-level threats such as excessive agency and the lethal trifecta are design decisions.
    - There is no evaluation or red-teaming phase.
    - **Fix:** Add Part "Actors and capabilities," add a regulatory crosswalk to Part VII/VIII, and add `aip:design` (mapped to concept and architecture) or explain its absence.

21. **Major. §W6 SDL hookup (486), Reproducibility (483), §8 (585–586). The multi-SDL and reproducibility claims cannot be tested as written.**
    - The ask is "reproducible … as an artifact of this and *other* SDL processes." The only evidence offered is that other methods "swap only the S3 adapter," with no deliverable and no test.
    - Byte-identical HTML through Graphviz depends on the exact Graphviz and Python builds, and the lock lists "tool versions" but no pinned environment.
    - "Tools-only change → CI failure by design" has no rebaseline path.
    - **Fix:**
      - Add a Phase 3 deliverable: one profile rendered through a second method adapter (STRIDE-on-DFD or MAESTRO) with the same output contract.
      - Pin the toolchain (versions plus hashes) in `tara-lock.yaml` and in CI.
      - Add a `tara --rebaseline` with a design-log entry.

### Minor

22. **Minor. §1.3 (line 141).** "library#22 has waited 12 days after two reviews." It has been open 12 days (since 10-14). The two reviews are comments dated 10-21 to 10-24, and `reviewDecision` is empty (no formal approval). **Fix:** say "open 12 days; reviewed by two students via comments, last 10-24; no formal approval."
23. **Minor. §1.2 (line 135).** "1,088 of the assignment rows are 'later' with no owner." The `wave1-assignments.csv` rows all have a `lane`. They lack a schedule, not an owner. **Fix:** reword.
24. **Minor. §1.2 (line 137).** "No AI topic exists in `topics/`." Library `topics/sagai.yaml` (Secure AI) exists. **Fix:** "no AI-threats topic."
25. **Minor. §1.4, §10.2 (666).** Issue #37 is missing from the retitle list (see finding 17).
26. **Minor. §W0 Outputs/DoD (292, 294), §10.2 (647).** "§8 Q1–Q7" is ambiguous, because this plan's own §8 is Metrics. **Fix:** write "RPT-0014 §8 Q1–Q7" everywhere.
27. **Minor. §1.3 (160) vs §W0 Method (293).** library#21 is in the merge queue but not in the merge sequence. #162 is a student M3 build PR (graph view), not a program PR, so it should not sit in the program's DoD. **Fix:** align the two lists and drop #162 from the W0 DoD.
28. **Minor. Appendix C (780).** AIT-137 (catalog `lifecycle_stage: model-artifact`) and AIT-142 (`deployment`) are also listed under `aip:retirement`, so they are double-classified. **Fix:** state a primary-phase rule and allow secondary phases explicitly.
29. **Minor. Appendix B (754–756).** `customer-chatbot` and `enterprise-copilot-rag` have the same composition (TT06+TT07). **Fix:** distinguish them by ownership scope or assets (A17/A18) or merge them.
30. **Minor. Appendix B, §W6 domains, Q-11.** Target types use four id systems: TT codes, memo C's `tt:*`, `dp:*` profiles and the Part V families. **Fix:** one mapping table and one prefix policy.
31. **Minor. §W3 Catalog pinning (384), Q-07.** The canonical form `cwe@4.20:CWE-1427` conflicts with PLAN-0002's existing Weakness id convention (`cwe-79`, `tr-weak-0001`). **Fix:** Q-07 must state the migration or the alias.
32. **Minor. Front matter `agent_notes` (32–33), §1.4 (173–174).** Design-log number collisions are wider than 0024: 0006, 0011, 0012 and 0015 are already duplicated on `main`. **Fix:** note it, and ship DL-0026 in the same PR as the plan (CLAUDE.md working agreement).
33. **Minor. §4.1.2 corroboration (346–350).**
    - Social-only items should be capped at E0–E2 and excluded from maturity derivation and E3+ review queues.
    - "Archive the outbound link" has no case for a post with no link.
    - A write-up by the same poster is not independent corroboration.
    - **Fix:** add these three rules.
34. **Minor. §4.1.2, Q-08.**
    - Confirm in X's developer terms that post text may be passed to a third-party LLM for triage.
    - The xAI search option is itself an LLM over X content, so it needs a terms check.
    - `social/accounts.yaml` (~150 individuals' handles) in a world-viewable repo is a light privacy and optics issue.
    - **Fix:** keep the curated list private or limit it to organisations, and add the terms check to Q-08.
35. **Minor. Q-04 (551).** Answering RPT-0014 Q5 (namespace) in an issue comment touches DEC-008. **Fix:** label the comment "direction only; DEC-008 is accepted only by ADR" (the CLAUDE.md "never in a comment" rule).
36. **Minor. §3.5 item 1 (263–266), §6 S4.** The integration agent writes the golden examples, and students are gated against them in the same sprint the sponsor reviews them. That is circular. **Fix:** sponsor sign-off on the golden examples before they are used as a gate.
37. **Minor. §0 (72–73) vs §9 R5 (603).** "Students are reviewers, not producers" conflicts with "students run their own distill batches." Q-02 also changes graded responsibilities in SOW-0001 §4, which needs an SOW amendment, not a "note" (line 549). **Fix:** reconcile, and make the vehicle an SOW amendment with faculty sign-off.
38. **Minor. §5 Phase 2 exit (516).** "In-semester estimate met **or restated**" always passes. **Fix:** make the restatement go back to the sponsor for a ruling.
39. **Minor. §W4, §8.** Staleness: there is no edition cadence or as-of policy for the report, even though catalogs re-pin monthly. **Fix:** set an edition cadence (for example, one per term plus a monthly "what changed" delta page) and show the as-of date on every page.
40. **Minor. §A.2, R2.** The number rule needs cached text, but only 285 of the 1,181 sources have a cached PDF. **Fix:** mark the rule "unverifiable" when no cache exists and cap confidence at medium.
41. **Minor. Whole document (849 lines, 86 KB).** It is too long to be decision-ready. Appendices A (DX-AI/1 → library schema PR), B (TT → scheme file), D (sources → `tools/rpt0014/README`) and E (layout → PROPOSAL) duplicate their target artifacts. **Fix:** add a one-page decision brief (asks → deliverables → Q-01…Q-15 with recommended answers → week-1 actions with owner and hours) and move the appendices out.

---

## Claims verified (32 checked)

| # | Claim (plan line) | Result |
|---|---|---|
| 1 | M3 Nov 5 / M4 Nov 19 / M5 Dec 5 (114) | ✓ SOW-0001 §3 lines 105–107 |
| 2 | I3 = Oct 23–Nov 5 (112) | ✓ PLAN-0001 line 148 |
| 3 | S4 = Nov 6–12, S6 = Nov 20–26 (112) | ✓ issues #135, #136 (S1 = Oct 16–22 per #134) |
| 4 | PR #159 approved, unmerged; @Maimcghee (126) | ✓ APPROVED by @paria03 10-23; OPEN |
| 5 | em-01: 3 assets, 4 trust zones, 8 flows, 5 mitigations, 12 ATLAS steps (126) | ✓ (12 attack_patterns; 13 attack_steps) |
| 6 | PR #117 merged 10-12, @paria03, 3 records (124) | ✓ |
| 7 | library#22 19 records, open since 10-14 (125) | ✓ |
| 8 | library#22 "reviewed by two students, mergeable" (125) | ✓ (comment reviews by @Clovier and @kriishnaa-18; MERGEABLE/CLEAN) |
| 9 | "waited 12 days after two reviews" (141) | ✗ open 12 days; reviews 10-21…10-24 (finding 22) |
| 10 | #130/#167 carry ADR-0011/0012, open (143) | ✓ |
| 11 | PR #130 "three open choices" (80) | ✗ four delegated decisions already made (finding 4) |
| 12 | ADR-0011 `status: accepted`, student decision-maker, `delegated_by: nymble`, `reviewed: false` (170–171) | ✓ |
| 13 | DL 0024 on main and in #130; 0025 in #167 (173) | ✓ (also older duplicates, finding 32) |
| 14 | #132 merged; #129 schema CI; #162 open (127) | ✓ |
| 15 | 146 AIT, all `hypothesis` (123) | ✓ |
| 16 | Maturity 38 ITW / 42 / 62 / 4 (123) | ✓ (31 exploited + 7 occurred = 38) |
| 17 | 1,181 sources, 812 tier-1 / 369 tier-2, 675 papers (122) | ✓ sources.md and wave1-assignments.csv |
| 18 | 179 incidents, 127 TMs (122) | ✓ |
| 19 | 112 sources capped at medium (64) | ✓ report §8 item 3 |
| 20 | 769 AIT→S-id pairs; 459 sources cited by no AIT (383, 469) | ✓ (722 distinct cited) |
| 21 | X01–X16 → 36 fine classes (183) | ✓ |
| 22 | round1-critic-gaps: 58 gaps, 16 suspect (303) | ✓ |
| 23 | 1,088 "later" rows "with no owner" (135) | ◐ count ✓, "no owner" ✗ (finding 23) |
| 24 | "No AI topic in topics/" (137) | ◐ `sagai.yaml` exists (finding 24) |
| 25 | LANES.md lines 170–178 carry names (166) | ✓ (170–179) |
| 26 | #36/#38/#39 titles carry names (167) | ✓ but #37 omitted |
| 27 | check_identities scans only `docs/**/*.html` (168) | ✓ |
| 28 | Three rpt0014-* workflows exist in `.claude/workflows/` (212–214) | ✓ (`.js` files) |
| 29 | DEC-001b/008/009 open (95) | ✓ ARCH-0001 lines 38–39 |
| 30 | ADR-0002 domains software/automotive/hardware, ≥2 domains (96) | ✓ |
| 31 | ADR-0006 human-rated feasibility, S/F/O/P (97) | ✓ |
| 32 | MAP-0001 rows 2/3/7/15 (99, 486) | ✓ requirements / TARA / third-party / release gate |

Also confirmed:

- KEV catalog 2026.10.23 with 1,756 entries
- 73 ATLAS case studies (enumerations.md)
- 11 source types
- SR-I5/I7/I9/I10 and SR-R4 in RPT-0016
- PLAN-0003 §1d, A1a/A2/A3/B1 and R-B2/B4/B5
- the `tr-weak-*` namespace in PLAN-0002
- DEC-011 is the highest DEC (so DEC-012 is free)
- the `LifecyclePhaseCode` values used in Appendix C exist
- `Review.reviews` range is Assertion (Q-09b's widening is real)
- no personal names in the draft itself

Not verified (outside the repo): the X pricing and ToS figures, Bluesky and NVD rate limits, and the "211 prompt-injection CVEs."
