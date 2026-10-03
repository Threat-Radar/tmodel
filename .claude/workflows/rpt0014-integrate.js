export const meta = {
  name: 'rpt0014-integrate',
  description: 'RPT-0014 integration lane: merge round2/ sweeps and extraction verify proposals into the corpus with stable ids, then an adversarial completeness critic and fold',
  whenToUse: 'The integration lane (nymble) runs this after lane PRs merge. args: {today: "YYYY-MM-DD", version: "0.3.0"}',
  phases: [{ title: 'Merge' }, { title: 'Critique' }, { title: 'Fold' }],
}
const R = 'research/0014-ai-threat-model'
const TODAY = (args && args.today) || 'today'
const VER = (args && args.version) || '0.3.0'
phase('Merge')
const merge = await agent(`Work from the repo root. You are the INTEGRATION agent for RPT-0014. Merge ${R}/round2/*.md, *.csv and pdf-additions.tsv, plus every proposal in ${R}/extractions/*/verify.md, into ${R}/. Ids are stable forever: append only.
1. sources.md: dedupe, then append S-NNNN after the current maximum id (rows plus annotated entries); apply verified corrections to existing entries and note them.
2. incidents.md: append INC ids and update the patterns.
3. threat-models.md: append TM ids, add comparison rows, and set "capture status" to "extracted (extractions/<unit>)" for the extracted TMs.
4. attack-catalog.yaml: add AIT ids for classes the evidence shows are missing; attach the new S and INC ids; re-derive maturity by the header rule; it must parse.
5. pdf-manifest.tsv: append the pdf-additions rows with their S-ids.
6. coverage.md (archdoc front matter, id RPT-0014-coverage, record RPT-0014, date and updated ${TODAY}): measured coverage per venue-year from the CSVs, the arXiv harvest statistics, the critic-gap closure table, and what remains open.
7. searches.md: append the round-2 query logs.
8. report.md: update the counts, any claims the new evidence changes, a "Round 2" Method subsection, and a link to extractions/INDEX.md; version ${VER}, updated ${TODAY}.
9. extractions/INDEX.md: a table of every unit: source ids, profile, source vs extracted counts, verify defects, residual issues, and "awaiting human review (R-018)" until a reviewer signs.
Check that every cited id resolves. RETURN: the counts added and the files changed.`, { label: 'merge', phase: 'Merge', effort: 'high' })
phase('Critique')
const crit = await agent(`Work from the repo root. You are an ADVERSARIAL COMPLETENESS CRITIC for RPT-0014 v${VER}: ${R}/report.md, sources.md, coverage.md, incidents.md, threat-models.md, attack-catalog.yaml and extractions/INDEX.md. Assume it is incomplete and wrong. Check: (1) whether the coverage measurement is honest (hand-check the filter recall on 2 venue-years); (2) whether the 30 most-cited AI-security papers (OpenAlex, sorted by citations) are all present; (3) 25 new entries against their URLs; (4) incident kinds and any missing 2026 events; (5) report claims that the new evidence contradicts. RETURN a numbered list of findings, each with its severity, file and fix.`, { label: 'critic', phase: 'Critique', effort: 'max' })
phase('Fold')
const fold = await agent(`Work from the repo root. Apply or reject (with a reason) each finding to ${R}/ (not extractions/ unit content), verifying each fact first. Findings:\n${crit}\nAfterwards: attack-catalog.yaml parses, every id resolves, the front matter is intact, and a review-log row is added to report.md. RETURN the applied and rejected findings with reasons (they go into the design log).`, { label: 'fold', phase: 'Fold', effort: 'high' })
return { merge, critic: crit, fold }
