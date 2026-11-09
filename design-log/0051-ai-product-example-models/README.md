---
schema: "archdoc/v1"
id: DL-0051
title: "Two more AI product example models (Copilot agent mode, Agentforce) and an app test"
type: research
status: draft
version: "0.1.0"
date: "2026-11-09"
updated: "2026-11-11"
record: DL-0051
defers_to: ARCH-0001
---

# Two more AI product example models, and an app test

## Request

The sponsor (@nymble) asked the team to test the app with real products; #230 tracks the request. @Maimcghee read this as the loop set on 2026-10-14 (DL-0013): take a published attack on a real product, model it from its primary write-up, and see what the schema and the app cannot show. em-01 (EchoLeak, RPT-0009) already did this once.

Four candidates were offered, each with a primary source in RPT-0014's `sources.md`: GitHub Copilot agent mode (CVE-2025-53773, S-1112), Cursor MCPoison (CVE-2025-54136, S-1097), Slack AI (S-0993) and Salesforce Agentforce ForcedLeak (S-1019). **@Maimcghee chose Copilot and Agentforce.** Together they cover what em-01 does not: code execution instead of a data leak, and an attack with no CVE.

## What was produced

In `research/0009-sagai/example-models/`, beside em-01:

| File | Objects | References | Threats | Paths |
|---|---|---|---|---|
| `em-02-copilot-agent-self-approval.yaml` | 83 | 166 | 2 | 3 (OR gate) |
| `em-03-forcedleak-agentforce.yaml` | 71 | 130 | 1 | 1 (AND gate) |

The example-models README (0.2.0) records the two models, gaps AI-8 to AI-12, and findings A-1 to A-4 from opening all three models in the desktop app.

## How it was run

- **Tooling:** Claude Code (Opus 5.5) on @Maimcghee's account, 2026-11-09, one interactive session, no subagents.
- **Sources:** fetched with `curl`, with each SHA-256 recorded in the file headers. The write-ups were read in full. Salesforce's help article 005135034 renders only with JavaScript, so it was not read; the Agentforce fix is described as Noma reports it.
- **Checks:**
  - `linkml-validate` (LinkML 1.12.1, `spec/schema/requirements.txt`) against `spec/vectors/example-container-proposed.linkml.yaml`: no issues.
  - `design-log/0024-schema-proposal-g13/check-refs.py`: every reference resolves.
  - em-01 was re-run on `main` too, with the same result.
  - `bin/validate-archdoc`: 0 errors.
- **Number:** drafted as DL-0048 and renumbered on 2026-11-11 before the PR opened. #231 uses DL-0048, @Clovier claimed DL-0049 for the Juice Shop model (#200 review), and #233 uses DL-0050.
- **App test:** the engine (`tmodel serve`) and `npm run dev` were run from a local checkout of the #211 code, which differs from `main` only in a packaging requirement. The three files were copied into `spec/vectors/` for the test and not committed (finding A-1). Screenshots of the model report and attack-path views were checked by eye.

## What was decided while drafting, and why

- **Steps from the write-ups, not from ATLAS.** ATLAS 2026.09 has 73 case studies and none for either attack. Every step-to-technique link is therefore an Assertion by the AI drafter, with a confidence per link. These were not made to look like ATLAS's own mappings (gap AI-8).
- **Copilot: two products.** The CVE record lists only Visual Studio 2022 17.14, while the write-up attacks VS Code. `affects` follows the CVE record, and VS Code with Copilot is linked by an AI-proposed Assertion. Naming VS Code in `affects` directly would have put words in the CNA's mouth (gap AI-9). The cost is a 143-character model title in the app (finding A-4).
- **Copilot: no `reported_by`.** The write-up says MSRC was already tracking the issue and that Persistent Security reported it too, so no single reporter is recorded.
- **Copilot: the self-spreading path is modeled, with low confidence.** The write-up describes it ("Building an AI Virus") but does not demonstrate it. It is kept because it is a second threat that shares steps with the first.
- **Copilot: CWE-77 kept as the CNA gave it.** CWE-1427, as the root cause, and CWE-15, for the settings change, were added as AI-proposed. CWE-77 is ALLOWED-WITH-REVIEW, not DISCOURAGED like em-01's CWE-74, so it was not called a misfit.
- **Agentforce: no Vulnerability object.** Without a CVE, inventing a catalog id was rejected. The weaknesses enter through `exploits` Assertions, as in pv-02, and Noma's "CVSS 9.4", which has no vector, is quoted in the researcher party's description only (gap AI-10).
- **Agentforce: CWE-942 for the expired domain.** CWE-942's own description names a CSP that includes untrusted domains. The domain became untrusted by expiring, which CWE-942 does not distinguish, so the mapping is `medium` confidence.
- **The off-topic probe is linked to AML.T0069 at `low` confidence.** Leaving it unlinked was the alternative. A low-confidence link the reviewer can reject was preferred to silence.
- **Descriptions reworded for the app.** The app hides any sentence with code marks, file names or ids as a "modelling note". Five descriptions opened with such a sentence and showed nothing to a reader, so each now opens with plain text.

## Human review

Not yet reviewed:

- @Maimcghee checks the sources against each file, as was done for pv-01 and pv-02.
- The attack paths wait for a reviewer, as pv-01 and pv-02 do.
- Until both are done, every Assertion stays `proposed` (R-018).

## Open

1. **Where the models live.** They stay under RPT-0009 for now. Moving them into `spec/vectors/` would list them in the app and on the site. That needs the sponsor's call, which DL-0038 item 7 also left open for pv-01 and pv-02.
2. **App findings A-2 to A-4.** These are for the renderer's owner (@kriishnaa-18):
   - A-2: the real-product banner wording;
   - A-3: Assertion-held links are invisible;
   - A-4: the title is built from every product.
3. **Routing gaps AI-8 to AI-12.** RPT-0009 §8 routes AI-1 to AI-7 as G1 to G7. Routing AI-8 to AI-12 waits for the report's next version.
