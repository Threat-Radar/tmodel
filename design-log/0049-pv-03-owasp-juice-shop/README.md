---
schema: "archdoc/v1"
id: DL-0049
title: "Proposal vector pv-03: OWASP Juice Shop, a software product to test the app on"
type: process
status: draft
version: "0.1.1"
date: "2026-11-09"
updated: "2026-11-12"
record: DL-0049
bears_on: [DEC-001a]
defers_to: ARCH-0001
---

# DL-0049: Proposal vector pv-03, OWASP Juice Shop

This is an AI-assisted design record (per `CLAUDE.md`). Claude Code drafted it and the model it describes.

## Question asked

The faculty advisor asked the team to test tmodel on real software and hardware products. SOW-0001 §2.2 already makes "load a real product, see threats and paths as a graph, review/annotate a path" the demo acceptance, and ADR-0002 asks for products in at least two domains. @Clovier asked for a software product that costs nothing and has a known answer key, written in the existing model format, so that no new loader code is needed to try it. This is the software half of #230; a router firmware model is the other.

OWASP Juice Shop fits: it is a web shop that OWASP keeps insecure on purpose for training, it is free (MIT), and it ships its own list of hacking challenges and marks the code lines that cause them. Each attack path can be checked against both.

## What was produced

- **`spec/vectors/pv-03-owasp-juice-shop.yaml`**, modeled at Juice Shop v20.4.0 (commit `266448aba68cd8ba5915f526a128da4fa7bc3f9f`): 1 product, 6 components, 6 assets, 2 trust boundaries, 4 data flows, 6 weaknesses, 1 vulnerability, 3 attack patterns, 5 damage scenarios, 5 threats, 13 attack steps, 5 attack paths, 5 mitigations and 20 Assertions. Every attack step has an Assertion whose evidence links the code lines or the challenge it rests on. Every Assertion is `proposed`, and no Review is recorded.
- **Five threats,** each matching a Juice Shop challenge and the code Juice Shop marks for it:

  | Threat | Juice Shop challenge | Code at v20.4.0 | Weakness |
  |---|---|---|---|
  | Log in as the administrator through SQL injection | Login Admin, then Admin Section | `routes/login.ts` line 34; `frontend/src/app/app.routing.ts` line 80 | CWE-89 |
  | Read another customer's basket | View Basket | `routes/basket.ts` lines 18 and 19; `server.ts` lines 388 and 431 (the basket API needs a login) | CWE-639 |
  | Run a script in a shopper's session through the search page | DOM XSS | `frontend/src/app/search-result/search-result.component.ts` line 146 | CWE-79 |
  | Download confidential documents from /ftp | Confidential Document | `server.ts` lines 231 and 294; `routes/fileServer.ts` lines 26 to 29 | CWE-548 |
  | Forge a login token | Forged Signed JWT | `server.ts` lines 301 to 303 (the public key's folder); `lib/insecurity.ts` lines 20 and 52; `package.json` line 123 (jsonwebtoken 0.4.0) | CVE-2015-9235 (CWE-327, CWE-20) |

- **`docs/models/pv-03-owasp-juice-shop.html`** and the models index, regenerated with `render_models.py`.
- **The browser preview's data** (`docs/app/`, DL-0051), regenerated with `render_app.py`, so the preview lists nine models and opens this one at `app/?model=pv-03-owasp-juice-shop`.
- **A row** for it in the landing page's model table and in `spec/vectors/README.md`.
- **The example-data notice for proposal models** (`apps/desktop/src/report-render.ts`) said every proposal model was "drafted by AI from the published write-up of a real automotive attack". That held for pv-01 and pv-02 but not for this one, so the per-model notice now says "drafted by AI from published sources about a real product", and the models index names attack write-ups as one kind of source. The three tests that pinned the old wording follow it, and the pv-01 and pv-02 pages change only in that sentence.

## How it was checked

- `linkml-validate` against the proposed container (`ExampleModelProposed`): no issues.
- `design-log/0024-schema-proposal-g13/check-refs.py` across all nine vectors: every reference resolves (pv-03: 88 objects, 175 references).
- `tmodel models`: nine example models, pv-03 listed as a proposal example with 5 threats, 0 reviewed. The app's model picker reads this list, so pv-03 appears there with no code change.
- `tmodel paths --goal` for each threat: one path each, matching the challenge's steps, 13 steps in all, and all marked not reviewed.
- Engine tests: 331 passed and 5 skipped locally. CI's engine jobs show 329 passed and 7 skipped: they don't check out the library submodule, so the two tests that read it skip. Frontend: `npm run typecheck` clean, `vitest` 375 passed in 30 files, including the published-page tests over all nine model pages.
- `render_models.py --check` (10 pages) and `render_app.py --check` (9 models, 550 library records): up to date. `check_links.py` (436 pages) and `check_identities.py` (487 files): clean.
- In a browser: with `docs/` served at `/tmodel/`, headless Chrome opens `app/?model=pv-03-owasp-juice-shop` on this model's report, with nine models in the picker and "5 threats, 0 with an accepted review, 5 attack paths".
- Facts: the release, commit and challenge list come from GitHub; the code lines, and the Forged Signed JWT hint that calls the public key mandatory (`challenges.yml` line 466), from the pinned commit; CVE-2015-9235, its CWEs and its fixed version (4.2.2) from NVD; the CWE and CAPEC names from MITRE (CWE 5.0, CAPEC 3.9).

## Choices the agent made, open to review

- **A proposal vector, not a core one.** Like pv-01 and pv-02 it is AI-drafted and unreviewed, and it uses Asset, TrustBoundary and DataFlow, so it validates against the proposed container.
- **Admin Section is the last step of the SQL-injection path, not a threat of its own.** The page's guard checks the administrator role (`app.guard.ts`), so reaching it needs the administrator token that Login Admin gives. The last step is an AND gate: the route and the token.
- **No CAPEC for the basket and token threats.** No CAPEC entry was a clear fit, so those links are left out rather than guessed.
- **Mitigations are `accepted_risk`.** Juice Shop leaves them out on purpose. Each names the control that the challenge's mitigation link describes, or is marked as a model suggestion where the challenge gives none.
- **The product id is the GitHub package URL of the release tag.** No Docker image digest is recorded, because no image was pulled.
- **Feasibility and impact are unset.** They are human inputs.
- **Each step's source is an Assertion.** AttackStep has no evidence slot, and an Assertion's predicate is not a closed list. The five steps that exploit a weakness keep `exploits`. The eight others get `targets_element`, the name ThreatInstance's slot already has (ADR-0011), for the component, data flow or asset the step acts on, with the code lines and the challenge as evidence.
- **A component for the /encryptionkeys folder,** beside the one for /ftp, since the token-forging path starts by reading it.
- **One notice for every proposal model, worded more generally,** rather than a notice per model: the renderer chooses the notice by the model's kind, and "published sources about a real product" is true of all three proposal models.

## What a human accepted

- @Clovier, 2026-11-12: make the changes the review of #237 asked for (below).

Nothing in the model is accepted yet. All 20 Assertions are `proposed`, and no Review is recorded.

## What was rejected, and why

- **No human rejections yet.**
- **The agent's own choices:** the other 112 challenges are not modeled; CAPEC ids are not guessed where no entry clearly fits; no Docker image digest is recorded without pulling the image.
- **Dropping the login step from the basket path,** which the review suggested might not be needed: the basket API answers only requests that carry a login token (`server.ts` lines 388 and 431), and View Basket counts only for a logged-in user (`routes/basket.ts` lines 21 to 24). The step stays, and its description now gives the reason.

## Changes after review (2026-11-12)

@kriishnaa-18 reviewed #237 on 2026-11-12 and asked for two changes before approving. Both are made:

- **The forged-token path lacked a step.** Algorithm confusion needs the shop's RSA public key, and Juice Shop's own hint for Forged Signed JWT calls getting it mandatory. The path now starts with `attack-step:get-public-key`: the server lists `/encryptionkeys` and serves its files (`server.ts` lines 301 to 303), and the token checks use the key kept there (`lib/insecurity.ts` lines 20 and 52). The signing step names the trick, an HS256 token signed with the public key, and the last step cites the challenge's check (`routes/verify.ts` lines 90 to 91 and 116 to 133).
- **Seven of the twelve steps had no evidence-bearing Assertion,** which #230 asks of every step. Each of the eight steps without one, the new step included, now has a `targets_element` Assertion whose evidence links the code lines and, where there is one, the challenge.

The engine test counts above now say which run they come from. Validating the proposal vectors in CI, also suggested, is left for its own change: CI's schema job checks the mvp, tv and sdl vectors but no pv ones, and the workflow is under `.github/`, which CODEOWNERS gives to @nymble.

## Next steps

- A person checks the five attack paths against the challenges and the code lines (R-018), and the sponsor decides whether pv-03 joins the examples.
- Generate the product's SBOM with Syft from the Docker image, as input for a future SBOM importer (ADR-0001, RPT-0004 Table 6).
- Add a hardware or firmware product for the second domain, for example a router firmware image with a known exploited CVE.
