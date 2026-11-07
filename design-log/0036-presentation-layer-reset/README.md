---
schema: "archdoc/v1"
id: DL-0036
title: "Presentation layer reset: readable model views instead of the raw graph"
type: process
status: draft
version: "0.1.0"
date: "2026-11-04"
updated: "2026-11-04"
record: DL-0036
defers_to: ARCH-0001
---

# Presentation layer reset: readable model views instead of the raw graph

**Status: problem statement and proposed direction. Nothing here is accepted.**
No `DEC-*` is decided here. The UI stack stays as ADR-0003 has it (Tauri + TypeScript).

## Request

On 2026-11-04 @nymble opened the app built from `main` (`19442d7`, see DL-0035)
and judged it "problematic … nonsense in the graph … we need a better
presentation layer". Asked: reproduce what the Graph tab shows, list what reads
as nonsense to a non-developer and what a threat-model reader needs, and
propose a direction with acceptance criteria. Related: #202 (MVP review, punch
list items 1 and 4), #204 (Pages browser preview), #182 (TARA render), #58
(object tables).

## How it was reproduced

Fresh clone of `main` at `19442d7`, engine from source (`tmodel serve`), UI in
a browser (`npm run dev`, `http://localhost:1420/`), headless Chrome at
1440×900. Same frontend as the packaged app.

| screenshot | what it shows |
|---|---|
| [`mvp01-default.png`](mvp01-default.png) | Knowledge Graph tab as it opens: always mvp-01, 7-node neighbourhood |
| [`mvp02-default.png`](mvp02-default.png) | `?file=mvp-02-automotive-ecu.yaml`: 4 nodes, a parts list |
| [`mvp02-path-remote-diag.png`](mvp02-path-remote-diag.png) | after choosing "Remote Diag Injection — Reviewed (Accepted)" |

Engine `/graph` returns 42 nodes / 69 edges for mvp-01 and 53 / 76 for mvp-02,
in 17–18 object types and about 30 relationship names.

## Observed problems (what reads as nonsense)

1. **Only one model, and the reader can't change it.** `DEFAULT_MODEL_FILE`
   (`apps/desktop/src/engine-graph-provider.ts:12`) hard-codes mvp-01. There is
   no picker. `?file=` is undocumented and cannot be set in the Tauri window,
   so the automotive model (mvp-02) is unreachable in the app.
2. **It opens on a meaningless fragment.** The start view is the one-hop
   neighbourhood of the first `Component`. mvp-02 opens on 4 nodes (TCU,
   system-on-chip, application core, communications core) joined by
   `composed_of`: a parts list with no threat, damage or risk on screen.
   mvp-01 opens on 7 nodes, including a `Party` ("SaaS operator") and an
   `Assertion` node.
3. **Bookkeeping is drawn as if it were the model.** About 40–45 % of nodes are
   records about the model, not the system: `Assertion`, `Review`, `Party`,
   `LifecyclePhase`, `View` (19 of 42 in mvp-01, 21 of 53 in mvp-02). They
   appear as peers of products and threats, linked by edges named `subject` and
   `object`. Review state belongs on the claim it reviews, as a badge.
4. **Edge labels are schema field names**: `composed_of`, `uses_component`,
   `applies_in_phase`, `realizes_threat`, `steps`, `precedes`, `subject`,
   `object`. They are drawn at about 5 px and unreadable at normal zoom.
5. **The attack-path view doesn't tell the story.** Highlighting the accepted
   remote-diagnostic path shows its three steps and fades everything else
   to grey circles with near-invisible labels. The threat it realises, the damage scenario, the
   affected component, the mitigations and the risk score are not shown.
   Step order is unclear: the model says "reach the modem" and "bypass
   auth" both precede "inject CAN frame" (an AND), so two arrows converge with
   no AND marker. The CLI prints the same path as reach → bypass → inject. The
   view is not fitted to the path; #202 saw it clipped off-canvas.
6. **Developer identifiers everywhere.** The inspector leads with CURIEs
   (`component:tcu-soc`), raw CPE and purl strings
   (`cpe:2.3:h:chipco:soc_t500:-:*:*:*:*:*:*:*`,
   `pkg:oci/…@sha256:…`) and spec-internal notes copied from the vectors
   ("§3 structural node", "§0 authoritative component, not a DFD node").
   Type chips and the legend use class names (`ThreatInstance`, `AttackStep`,
   `AttackPattern`, "Other types").
7. **Names are built from ids, not taken from the model.** The path picker says
   "Remote Diag Injection", a title-cased id slug, where the model's name is
   "Remote unauthenticated diagnostic command injection onto CAN". The status
   line reads "Engine model data path for remote-diag-injection from
   mvp-02-automotive-ecu.yaml · reviewed and accepted · assertion: accepted ·
   review: accepted".
8. **Nothing says what the reader is looking at.** No model title, scope,
   example-data banner or summary ("2 threats, 1 accepted, 1 rejected AI
   hypothesis"). The legend shows six edge-review styles before the reader has
   seen a threat.

## What a threat-model reader needs (and can't see today)

In the order a TARA reads (ISO/SAE 21434 clause 15, paraphrased): what the item
is, what is worth protecting, what could go wrong, how, how likely, how bad, and
what we do about it, each with its review state.

| need | form |
|---|---|
| Which model: title, domain, product, scope, example-data banner | header + model picker |
| Assets / components and the security property at stake | table |
| Damage scenarios with impact (S/F/O/P where present) | table |
| Threats: name, violated property, source (human / AI-proposed), **review status** | table, status as a badge |
| Attack paths: ordered steps with AND/OR, feasibility, **review status**, who reviewed and why | numbered text per path, plus a focused graph |
| Weakness chain: CVE → CWE → CAPEC behind a threat | inline links in the threat row |
| Mitigations: what, against which threat, status | table |
| Risk: per threat/path, feasibility × impact, treatment | table |
| Requirements that apply (paraphrase + clause id) | table |
| What is still a hypothesis (AI-proposed, not accepted) | filter + banner |

## Proposed direction

1. **Model picker.** An engine route lists the available models (title, domain,
   file). The app opens on a model chooser or the last model used, never a
   hard-coded file. `?file=` stays as a developer switch and is documented.
2. **A "Model report" view, TARA-ordered, as the default tab for a model.**
   Header (title, scope, banner, counts by review status), then tables:
   assets/components, damage scenarios, threats, attack paths with review
   status, mitigations, risk, requirements. Human labels only; ids live in a
   collapsible "details" row. Bookkeeping (Assertion, Review, Party,
   LifecyclePhase, View) becomes badges, reviewer handles and footnotes, never
   nodes.
3. **Graph only as a focused attack-path view.** Opened from a threat or path
   row: the steps in order (left to right, AND/OR shown), the threat and damage
   at the end, the affected component and the mitigations at their steps. Human
   labels, readable edge words ("leads to", "mitigated by"), fitted to view. The
   whole-model graph moves behind an "explore" toggle for developers.
4. **One renderer, two outputs.** The same view code renders inside the app and
   to static HTML for Pages (#204, #202 item 1, a descoped #182). One code path,
   so the site and the app cannot disagree. The tables follow the object tables
   of #58.

## Acceptance criteria (MVP, Fri 2026-11-06)

- [ ] In the packaged app a reader can choose mvp-01, mvp-02 and at least one
      more example model without URL parameters.
- [ ] Opening a model shows its title, an example-data banner and counts of
      threats by review status, before any graph.
- [ ] The report view has tables for assets/components, damage scenarios,
      threats, attack paths, mitigations and risk, in that order, with human
      labels. No CURIE, CPE, purl or schema field name in the default view.
- [ ] Each threat and attack path shows its review status (accepted, rejected,
      changes requested, AI-proposed/not reviewed) and the reviewer handle.
- [ ] The rejected AI hypothesis in mvp-02 (infotainment pivot) is visibly
      marked as rejected in both the table and the path view.
- [ ] The attack-path view shows the ordered steps with AND/OR, the threat,
      the damage and the mitigations, fitted to the window at 1280×800, with
      every visible node labelled.
- [ ] Assertion, Review, Party, LifecyclePhase and View objects are not drawn as
      graph nodes in the default views.
- [ ] The same renderer produces a static HTML page per example model for Pages
      (#204), linked from the landing page, passing `check_links.py` and
      `check_identities.py`.
- [ ] Before-and-after screenshots for mvp-01 and mvp-02 attached to the PR.

## Open questions

1. Report first or graph first when a model opens? Proposed: report first.
2. Keep the whole-model "explore" graph in the MVP at all, or hide it until I4?
3. Where does the report shape live: an engine route that returns
   TARA-ordered JSON (#181, descoped) or frontend code over `/graph`? The
   engine route keeps the Pages renderer and the app on one source.
4. mvp-02 has one damage scenario, one risk score and no Asset objects (#184).
   Fill the vector before Friday, or render the gaps as explicit "not assessed" rows?
5. `/graph` accepts a bare file name but `/attack-paths` wants an absolute
   path (it answers "give an absolute path"). Unify before adding a picker?
6. Labels for path steps and edges: human text in the vectors, or
   a fixed vocabulary map in the UI ("precedes" → "then")?

## Human review

Pending (@nymble; GUI lane @kriishnaa-18).
