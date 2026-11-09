---
schema: "archdoc/v1"
id: DL-0037
title: "TARA draft v0 for mvp-02: the #184 fixes and a clause 15 page (#202 item 3)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-04"
updated: "2026-11-04"
record: DL-0037
bears_on: [DEC-001a, DEC-003]
defers_to: ARCH-0001
---

# DL-0037: TARA draft v0 for mvp-02 (#202 item 3)

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code (claude-opus-5-5) drafted it in
@Clovier's session, as one agent with no subagents. It produced the mvp-02 changes, the core
container's `assets` collection, the wider reference check and the TARA page builder. @Clovier made
the two rating calls recorded below. **Proposal only.** No `DEC-*` is accepted here, and the page is
not the governed TARA of DL-0027.

## Question asked

The sponsor's MVP review (#202, item 3) asks to publish mvp-02 as a TARA-shaped page: fix the top
#184 gaps (assets, S/F/O/P impact ratings, a treatment decision per risk) and render the model in
clause 15 order as a "TARA draft v0 (example data)" page, paraphrase only. The data fixes follow
@Clovier's gap table on #184 (2026-10-31): V1 to V4, A1, and R1 and R2 for the page. ISO/SAE 21434
is paraphrased from RPT-0007 and cited by clause, provision and table ids only (#154).

## What was produced

| File | Change |
|---|---|
| `spec/vectors/mvp-02-automotive-ecu.yaml` | V1 to V4 and A1 (below); 17 values lose a spaced dash |
| `spec/vectors/example-container-core.linkml.yaml` | an `assets` collection (A1); Asset is core since ADR-0011 |
| `design-log/0021-mvp-core-attack-path-vectors/check-edges.py` | the 13 reference slots ADR-0011 added, so the new edges are checked |
| `docs/publishing/render_tara.py`, `docs/publishing/tara.yaml` | new: the page builder and its manifest |
| `docs/reports/tara-mvp-02.html` | generated: the page |
| `docs/publishing/render_report.py`, `reports.yaml`, `docs/reports/index.html` | the reports index lists pages other renderers write (`listed:`) |
| `docs/publishing/site.yaml`, `SKILL.md`, `bin/publish-site` | the page's place in the site map, the playbook and the build |

### The data, by #184 fix

- **V1 (15.3, 15.5).** The damage scenario names the vehicle function (braking) and the road users
  harmed (the occupants and the people around the vehicle). `party:fleet-operator` is now described
  as the owner the score is reported for (`for_stakeholder`), with the ratings for the road users.
- **V2 (15.5).** The RiskScore gives a reason per impact category, against the Annex F examples as
  RPT-0007 §3.1 paraphrases them; safety severe is ISO 26262-3 class S3 (RQ-15-06). Writing the
  reasons showed two ratings that did not fit those examples (see "What a human accepted").
- **V3 (15.7, 15.8).** The remote path is rated High by the attack-vector approach (RC-15-14, G.4):
  it starts over the cellular network, a network vector, which Table G.9 rates High. The risk values
  are read from the High column of Annex H's example matrix (Table H.8), and the RiskScore names it.
- **V4 (15.9).** The RiskScore records the decision, reduce (RQ-15-17), and a new authored requirement,
  `requirement:gateway-filter-safety-can`, is `satisfied_by` the gateway mitigation. It is a
  requirement on the TCU's operational environment (the vehicle's domain gateway), derived from
  RQ-09-09.
- **A1 (15.3, 15.4).** Two Assets: the safety CAN commands (integrity, authenticity) and the remote
  diagnostic service (authorization), each `processed_by` a component. The damage scenario has
  `damages_asset` and `compromised_property`; the human-elicited threat has `targets_element`.
- Until the schema has fields for them (#184 F1, F3, F5), the reasons, the feasibility method and
  the decision are labelled paragraphs in the RiskScore's description: "Impact (15.5)", "Feasibility
  (15.7)", "Risk values (15.8)", "Treatment decision (15.9)". The builder reads them by those labels.

### The page

`docs/publishing/render_tara.py` reads each entry of `tara.yaml` and writes one static page.

- **Through the engine.** The model is loaded with `engine/engine/load/vector.py`, and review state
  comes from `engine/engine/graph.py`: a threat counts as reviewed only when every attack path for it
  has an accepted Assertion. So the page and the app agree on what is reviewed. The site's own reader,
  `library/bin/_record_yaml.py`, differs from PyYAML on all eight vectors (it reads list items such as
  `- attack-step:x` as mappings), so the builder needs PyYAML and `bin/publish-site` runs it with
  `engine/.venv/bin/python` when that exists.
- **Collect, then render**, as DL-0027 plans the pilot (#181, #182): `collect()` returns the TARA as
  plain data, section by section; `render()` only formats it.
- **No judgement of its own.** Every rating, risk value and decision is read from the model. The
  build fails where a reason names a different level from the rating beside it. Nothing is computed
  from Table H.8, which would pick a risk metric (DEC-003 is open).
- **Sections in clause order:** item and scope (9.3), assets and damage scenarios (15.3), threat
  scenarios (15.4), impact (15.5), attack paths with the CVE to CWE to CAPEC chain (15.6),
  feasibility (15.7), risk values (15.8), treatment (15.9), and the requirements the TARA produced,
  found by following `addresses` and `satisfied_by` from the threat and its mitigations (R2). Then:
  what was left out, the review record, and the gaps from `tara.yaml`.
- **R1.** The AI-proposed threat and its rejected path are kept out of sections 1 to 9 and shown,
  labelled, under "Left out", with the reviewer's reason.
- **Labels and identities.** An example-data banner opens the page (DL-0027). Person parties render
  as "a human reviewer (example role)", never by handle.
- **Where.** `docs/reports/tara-mvp-02.html`, listed on the reports index. Not under `docs/models/`:
  DL-0027 keeps `docs/models/tcu/tara/` for approved versions, and #202 item 1 is building
  `docs/models/`.

## How it was checked

- `linkml-validate` (core container): mvp-01, mvp-02, mvp-03 and mvp-18, no issues.
- `check-edges.py`: the four mvp vectors (199 objects, 306 references) and the requirement extraction
  files resolve; mvp-02 has 56 objects and 89 references. With a broken `damages_asset` it reports
  the unresolved reference. pv-01 and pv-02, which CI does not run, also resolve with the wider list.
- A parse-level diff of mvp-02 against `main`: the changes listed above, plus 17 values whose only
  change is a spaced em dash becoming a colon. The first attempt left a colon and space inside
  unquoted values, which is not valid YAML; the validators caught it, and those values are now quoted.
- Engine tests: 239 passed, 5 skipped (the packaging tests, which need a built app).
- `render_tara.py --check` matches the committed page; `check_links.py` (424 pages) and
  `check_identities.py` pass.
- The builder, on changed copies of the model in memory: a reason that disagrees with its rating
  stops the build; a missing decision shows as "no decision recorded"; accepting the AI path's
  Assertion moves its threat into the TARA; with today's data the AI threat appears only under "Left
  out". The page has no script.
- Not checked: the page in a browser (the browser extension was not connected).
- `bin/publish-site` stops at `render_bibliography.py` on `main` today: `bibliography.yaml` gives
  fips-204 the topic `post-quantum-migration`, its library record `nist-cryptography`. This change
  does not touch either.

## Choices the agent made, open to review

1. **Braking** as the vehicle function: the standard's own example (RPT-0007 §2.4, §2.6) and what
   the path's "safety actuator" step implies.
2. The two Assets and their properties follow A1's examples.
3. `targets_element` only on the human-elicited threat. The AI-proposed threat is left exactly as it
   was proposed, so the record of what the AI produced stays clean.
4. The gateway requirement has no `applies_to`: its range is Product, ProductInstance or Component,
   and the gateway is not modelled. Its description says where it applies.
5. The core container gains `assets` only, not `trust_boundaries` or `data_flows`, which no core
   vector uses yet.
6. `check-edges.py` gets all 13 ADR-0011 reference slots, not only the three mvp-02 uses.
7. `render_report.py` changes only to list `listed:` pages on the index; `render_tara.py` refuses to
   build a page that is not listed there under the same title.

## What a human accepted

- @Clovier, 2026-11-04, in the session: V3, **High by attack vector**, which #184 offered against
  keeping medium with attack-potential inputs.
- @Clovier, 2026-11-04: **the impact ratings follow the Annex F examples** (RPT-0007 §3.1).
  Operational goes from major to severe, since braking is a core vehicle function behaving
  unexpectedly; privacy goes from moderate to negligible, since this damage scenario exposes no
  personal information. With High feasibility, Table H.8 gives safety 5, financial 4, operational 5
  and privacy 1.

The reasons text, the assets, the gateway requirement and the page are the agent's draft until a
human reviews them on the PR.

## What was rejected, and why

- **Keeping operational major and privacy moderate** and writing reasons to fit: rejected by
  @Clovier. The reasons could not match the examples they cite.
- **Medium feasibility with attack-potential inputs** (V3's other option): not chosen by @Clovier;
  #184 notes High changes fewer lines.
- **The site's stdlib YAML reader** for the builder: it misreads the vectors (above).
- **Computing risk values in the builder** from Table H.8: that would select a risk metric while
  DEC-003 is open, and copy the standard's table into code.
- **Projecting Assets in the engine's `/graph`**: an engine change outside this item. The engine's
  collection map does not include `assets` yet, so the app's Graph tab does not show them.
- **A gateway Component** added to mvp-02 just to give the requirement an `applies_to`.
- **Writing the page under `docs/models/`** (above).

## Follow-ups

- The engine projects Assets (and trust boundaries and data flows) in `/graph`.
- CI runs `render_tara.py --check`. The CI jobs do not check out the `library` submodule, which the
  site nav needs.
- The schema follow-ups F1 to F6 (#184), which the page lists as gaps.
- Item 1's models index and item 2's landing page link to this page.
- The fips-204 topic mismatch that stops `bin/publish-site`.

## Gate

`bin/validate-archdoc` clean. LinkML validation, `check-edges.py`, the engine tests, `render_tara.py
--check`, `check_links.py` and `check_identities.py` pass.
