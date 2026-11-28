---
schema: "archdoc/v1"
id: DL-0082
title: "AI-proposed attack paths: a local LLM drafts attack paths for an imported model, as proposals (#302)"
type: process
status: draft
version: "0.1.0"
date: "2026-11-27"
updated: "2026-11-27"
record: DL-0082
human_owner: Clovier
bears_on: [DEC-001a]
defers_to: ARCH-0001
---

# DL-0082: AI-proposed attack paths (#302)

DL-0081 is taken by open pull requests (#291 and #301 both use it), so this entry is
DL-0082.

## Question asked

#302: let a local LLM draft attack paths for an imported model, end to end, from the
model's components, CVEs and CWEs and the library's CAPEC records, as proposals a person
reviews in Review & Edit and then rates for risk; nothing leaves the user's Mac. After
kriishnaa-18's feedback on the issue, this sprint's scope is the attack path generation
end to end, with setup instructions in place of an in-app download, and questions and
answers only if time allows. The frontend is kriishnaa-18's, from a contract posted on
#302.

## What was produced

- `engine/engine/llm.py`: the Ollama client. Loopback URLs only; `status()` (running,
  model installed, its digest) and `chat_json(prompt, schema)` (one turn, the answer held
  to a JSON Schema by Ollama's `format`, temperature 0, seed 7, an 8,192-token context,
  and `keep_alive: 0` so the model leaves memory once it answers).
- `engine/engine/ai_paths.py`: the harness. `draft(model_text)` returns the model with the
  proposals added.
- `engine/engine/api/ai_routes.py`: `GET /ai/status` and `POST /ai/attack-paths`, mixed
  in ahead of the engine's handler like #288's workspace routes; `serve()` installs them,
  and `tmodel serve --enable-ai` turns drafting on.
- `engine/engine/cli.py`: `tmodel ai-status`, `tmodel ai-paths MODEL -o OUT`, and
  `tmodel serve --enable-ai`.
- `engine/AI_PROPOSALS.md`: the interface for the app; `engine/examples/ai-proposals/`:
  a synthetic imported model and `contract.json`, every answer of the routes.
- `engine/tests/test_ai_paths.py`: 43 tests against a stand-in Ollama (a local HTTP
  server answering as Ollama 0.33 does) and stand-in catalogs, so CI needs no model.

## Choices the agent made, open to review

1. **Local only, through Ollama.** SOW-0001 §2.1 and ADR-0003 make the app local and
   offline, and an SBOM with its CVEs maps what is vulnerable in a product. The client
   refuses any URL but a loopback one. A hosted API (OpenRouter and the like) is rejected
   below.
2. **The facts come from code, not from the LLM.** The model's `propagates_to` and
   `instance_of` Assertions (not rejected ones) give each component's vulnerabilities and
   their weaknesses; the pinned CWE release gives each weakness's related CAPEC patterns,
   and the pinned CAPEC release their names, likelihood, severity and description.
3. **A weakness with no pattern borrows its parent's.** In the alpine fixture 5 of the 9
   weaknesses relate to no pattern in CWE 4.20 (CWE-787, CWE-1284, CWE-407, CWE-440,
   CWE-476). Each borrows the patterns of its primary `ChildOf` parent in CWE-1000, at
   most two levels up (CWE-787 gets CWE-119's), and the prompt says so.
4. **At most 8 patterns per weakness,** the likeliest and most severe first, then
   Standard before Detailed before Meta. CWE-20 alone relates to dozens; without the cut
   the alpine prompt held 95 patterns and about 30,400 characters, with it 38 patterns and
   about 11,800 (about 2,900 tokens).
5. **The model picks only real choices.** A step `exploits` one `C<n> W<n> CAPEC-<n>`
   choice: a component, a weakness it has, and a pattern of that weakness. The choices
   are an `enum` in the answer's JSON Schema, so Ollama never lets the model write
   anything else, and the engine writes every id. In the trials below, free ids failed 18
   ways in one answer; separate component, weakness and pattern enums still paired
   patterns with the wrong weakness; the combined choice fixed both.
6. **Catalog and scanner text is data.** CVE and pattern descriptions are cut to one
   printable line (160 and 100 characters), and the prompt says the descriptions are
   data, not instructions. Whatever the model writes, it can only pick choices, and the
   result is only a proposal.
7. **The checks `tmodel propose` runs.** The answer becomes a `tmodel.patch/v1` patch, and
   `propose.propose(patch, …, write=False)` checks it on a temporary copy of the model
   (ids, the proposing Party, every Assertion `proposed`, the merged attack graph and
   graph projection). Then `accept.apply_text` adds the objects to the model's own text,
   so its comments and order stay. A refused answer goes back to the model with its
   problems, at most twice more; the third refusal is `generation_failed`.
8. **mvp-01's shape for an AI-proposed path.** Each path has an authored
   `realizes_threat` and a `proposed` `realizes_threat` Assertion by the model's
   `software_agent` Party. #291's review service selects a threat that has an authored
   path and offers that Assertion (and the threat's own Assertions) for a verdict, and
   #269 counts it reviewed only after a justified person's acceptance. The threat's
   `exploits_weakness`, each step's `exploits`, `targets_element` and `instance_of`, and
   a weakness's `exploited_by` follow the predicates the example models already use.
   No feasibility, impact, rating or review is written (ARCH-0001: impact judgement is a
   human input; CLAUDE.md: never present an AI-generated path as reviewed).
9. **A weak path is kept with a warning, not refused.** A path whose steps all use one
   pattern (the 9B model's habit in the trials) is kept, and the answer says so: a person
   reviews every path anyway, and refusing would often end in `generation_failed`.
10. **The routes write nothing.** `POST /ai/attack-paths` takes the model's text and
    answers with the new text; the app saves it as the project's next version (#288) and
    opens Review & Edit. One draft runs at a time (`busy` otherwise).
11. **Helpers named for the routes.** Every helper of `AiRoutes` starts with `_ai_`, and a
    test checks that it shares only `do_GET`, `do_POST` and `do_OPTIONS` with the handlers
    behind it, after #297 found a `_read_body` of the workspace routes replacing the import
    route's.

## How it was checked

- **Tests:** `tests/test_ai_paths.py`, 43 passed. The engine suite with Python 3.13 and no
  pyoxigraph: 1321 passed, 15 skipped, with `tests/test_store.py` and
  `tests/test_store_library.py` left out, as both need pyoxigraph (CI installs it). `ruff format --check` and `ruff check` pass on every file this
  change touches; the 7 `ruff check` findings left are main's (`model_graph.py`,
  `store/facade.py`, `tara.py`).
- **The pipeline with a stand-in model** on the alpine fixture, the real CWE 4.20 and
  CAPEC 3.9 releases (both checked against the library's pinned SHA-256): 2 paths, 4
  steps, 3 patterns and 20 Assertions added, all `proposed` by `party:ai-qwen3-5-9b`; the
  threats appear in `AttackGraph.threats()`; the model's header comment stays.
- **Trials with `qwen3.5:9b`** (Ollama 0.33.2, Q4_K_M, Apple M3 Pro, 18 GB), on the alpine
  import, with a scratch script that built the same kind of prompt before this code
  existed:
  - free ids and `precedes` written by the model: 66 s, 18 problems (ids without their
    prefix, `precedes` naming paths);
  - component, weakness and pattern as separate enums, steps ordered per path: 56 s, no
    id problems, but step names that did not fit their patterns, since the prompt had only
    CAPEC ids;
  - with CAPEC names and descriptions: names that fit, but patterns paired with the wrong
    weakness; the first try was cut off at Ollama's default context;
  - the combined choice: 76 s, no problems, every pairing real; the model reused one
    pattern for every step of a path.
- **The first run of this code with the real model** (`tmodel ai-paths` on the alpine
  import, the same Mac, about 68% of its memory free beforehand): 43 s, on the first
  attempt, 3 paths, and the model unloaded afterwards. The paths follow the scan's own CVEs
  (BusyBox wget's request smuggling, CVE-2025-60876; zlib's heap overflow in
  `gz_vacate()`; OpenSSL's memory growth from many CRL distribution points), and the saved
  model passes the attack graph and graph projection checks with 3 AI threats, every
  Assertion `proposed`. What a reviewer would catch: names numbered "Path 1: ..." (now
  dropped by the engine, with a test); CAPEC-19 (Embedding Scripts within Scripts), the
  top pattern of CWE-284, used where it does not fit, such as the last step of the denial
  of service path; one path reusing a pattern throughout (the warning); and a path that
  chains zlib, then BusyBox, then a rootkit.
- **A trial that went wrong:** `gpt-oss` (13.8 GB) with a 16,384-token context, for a
  comparison, froze the Mac and it restarted. Rejected below.

## What a human accepted

- Clovier, 2026-11-27: posted #302 and asked for the work to start ("post the llm issue
  and start working on it"), with kriishnaa-18's priorities: the generation end to end
  first, setup instructions for now, questions and answers later, and a contract for the
  frontend; the contract was posted on #302 without a mention ("no need to tag her").
- Clovier, 2026-11-27: allowed the CAPEC 3.9 download ("yes to the capec download") and the
  `qwen3.5:9b` download, and had `gpt-oss` removed after the freeze ("yes remove gpt-oss").

The code and the wording are Claude Code's draft until the pull request review accepts
them.

## What was rejected, and why

- **A hosted LLM (OpenRouter and the like).** Data would leave the Mac, against the SOW's
  local, offline app; every user would need a key the desktop app cannot keep; and a free
  model can be busy or gone during a demo. The client speaks only to a loopback URL.
- **An in-app download with a progress bar, for now** (kriishnaa-18): setup instructions
  cost far less this sprint; Ollama's `POST /api/pull` can serve it later.
- **Bundling a model in the app:** it would add gigabytes to every download.
- **`gpt-oss` on this Mac:** 13.8 GB on an 18 GB machine froze it.
- **Letting the model write ids or `precedes`:** the first trial shows why.
- **Only an Assertion-based path-to-threat link:** #291's review service lists only a
  threat with an authored path, so the authored `realizes_threat` stays, as in mvp-01.
- **Refusing a path that reuses one pattern:** it would often end the draft with
  `generation_failed`; the warning leaves it to the reviewer.

## Follow-ups

- **The desktop launcher** must start the engine with `--enable-ai` (with `--enable-import`
  and `--projects`, DL-0078's one switch).
- **The packaged app bundles no CAPEC release** (only the CWE one, ADR-0014), so a draft
  there answers `ai_unavailable` until it does.
- **Better paths:** a worked example from mvp-01 in the prompt, and a check that each step
  enables the next.
- **A score for comparing models and prompts:** the alpine import and two or three
  example models with human-reviewed paths, measured on the checks passed, real ids, and
  closeness to the human paths.
- **Questions and answers** from the same model, only from records the engine looks up.
- **A smaller model** for 8 GB Macs.

## Gate

`bin/validate-archdoc` clean. The engine tests, `ruff check` and `ruff format --check` pass
on the files this change touches.
