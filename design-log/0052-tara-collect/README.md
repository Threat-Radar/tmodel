---
schema: "archdoc/v1"
id: DL-0052
title: "TARA collect phase: deterministic engine intermediate for mvp-02"
type: process
status: draft
version: "0.1.2"
date: "2026-11-14"
updated: "2026-11-21"
record: DL-0052
issue: "Threat-Radar/tmodel#181"
defers_to: ARCH-0001
---

# DL-0052 — TARA collection

## Question

@paria03 requested #181: an engine command that writes one repeatable TARA
intermediate with assets, damage scenarios, threats, attack paths, risk,
mitigations and derived requirements. Each source item must retain its KG id
and review evidence. This implements the collect phase of DL-0027, not its
governance proposals or #182's HTML publishing work.

## Implementation

The branch originally started at PR #229's `a1e97c3` because collection needs
the #63 risk calculator. #229 merged on 2026-11-20 as `df5fb01`; this branch
now incorporates that `main`. No sponsor decision or human review is inferred
from the calculator implementation. The library
gitlink stays at `a28a013`; no library record or example vector changes.

The storage-neutral `engine.tara.collect_document` reads a mapping, validates
it through the existing graph projection, preserves records and calls the
existing risk calculator. `core.collect_tara`, `GET /tara` and `tmodel tara`
share that operation. The API uses the existing approved-directory boundary
and never writes an output file. The CLI optionally writes an atomic JSON
artifact. `engine/TARA.md` documents the DTO, consumer order, errors and review
semantics so the renderer owner can use it without this chat.

Source records, Assertions and all Reviews stay separate from calculated
risk. The export covers the whole model and explicitly labels bundled vectors
as example data. Source IDs remain intact; computed route IDs remain derived
identifiers with references to authored paths and steps. No rating, Review or
approval is created. Requirements retain their source clauses and text origin;
`stated_as` and `satisfied_by` links preserve slot versus Assertion origin.

The current HTML stop-gap collector filters out unreviewed threats, formats
names without ids and uses a last-review lookup. Moving that representation
into the engine would not meet #181. Instead this implementation reuses the
model loader, projection/validation and risk computation, while giving #182 an
evidence-preserving collection. The existing HTML page is unchanged.

## Rejected or deferred

| option | outcome | reason |
|---|---|---|
| Copy the current HTML collector's reviewed-only filter | rejected | The intermediate must retain proposed and rejected material, visibly labeled, rather than hide the evidence. |
| Treat the last Review in the file as authoritative | rejected | Reordering must not erase an earlier contrary judgment; every review is retained. |
| Call an accepted Assertion with no recorded person review human-reviewed | rejected | Export must not manufacture human acceptance from a status string alone. |
| Infer object or TARA approval from a reviewed relationship | rejected | Core Review targets Assertion; summaries explicitly name that scope. |
| Copy AI-proposed requirement links into slot values | rejected | ADR-0012 keeps proposals as Assertions until a human accepts them. |
| Infer missing ratings or parse authored risk prose as the derived result | rejected | The #63 calculator supplies explicit matrix values and honest incomplete rows. |
| Select one product from a multi-product file by heuristic | deferred | #181's pilot is the one-product mvp-02 model; the export states whole-model scope. |
| Accept governance classes, choose the approval digest, or publish HTML | deferred | These belong to #180/#183/#182 and their accepted decisions, not collection. |
| Add a clock, run id or absolute model path | rejected | They would make identical input vary by run or machine. |

## Validation and review

The test plan exercises mvp-02 twice through separate CLI processes with
different hash seeds and compares output bytes. Tests also cover API/CLI
parity, full source identities, rejected/proposed content, review-order
independence, person versus software-agent reviewers, requirement traces,
invalid inputs, non-destructive output errors and confinement. An opt-in
packaging check collects the model through a relocated bundled engine.

Original implementation validation (2026-11-14):

- Full engine and publishing suites: **481 passed, 5 skipped**. The five opt-in
  packaging checks were then run against the rebuilt standalone engine and
  **all five passed**, including `/tara` after relocation.
- Frontend: **373 tests passed**, typecheck and production build passed.
- Rust formatting, clippy and **four tests passed**.
- Archdoc: **28 documents, 0 errors**; publishing identity/link checks pass and
  the generated browser preview remains byte-for-byte current. No public page
  or frontend source changes are needed.
- Unchanged pinned library: **550 records, 0 errors, 122 existing warnings**.
- Engine lint/format and whitespace checks pass.
- The sample TCU export has one Product, two Assets, one DamageScenario, two
  ThreatInstances, seven AttackSteps, two AttackPaths, one authored RiskScore,
  three Mitigations, six Requirements, six Assertions and five Reviews.
  Its four requirement traces retain their source identities. The diagnostic
  scenario derives S/F/O/P 5/4/5/1; the rejected hypothesis remains incomplete.

## Main integration (2026-11-20)

After #229 merged, @paria03 requested updating #242 with `main`, retargeting
it to `main`, pushing the update and checking fresh CI. The integration keeps
both the TARA adapters and the new CWE API/CLI functionality. Four files had
conflicts because the squashed risk branch did not include the TARA additions;
those additions and the existing packaged-TARA regression are preserved.
The collector's behavior and output contract are unchanged.

Integration validation on Python 3.13: **546 engine tests passed, 6 skipped**
(five opt-in packaging tests and one full-catalog CWE test). Rebuilding the
sidecar and running the isolated packaged-engine tests gave **five passes**.
The frontend's 373 tests, typecheck and production build, four Rust tests plus
fmt/clippy, 14 publishing tests, archdoc, browser-preview freshness and identity/
link guards passed. The pinned library remains at 550 records, zero errors and
122 existing warnings. The TCU JSON is byte-identical to the original sample
(SHA-256 `4238a573a546db95ea48d4adf584d2746fd40debdfc33dbfe105810f17213712`).

The local Python 3.14 installation could not load its XML parser and its fresh
venv setup failed; these checks were rerun on a working Python 3.13 rather than
changing the application or the system installation to mask that environment
problem.

#242 had an approving review on `037b56e` before this integration. The current
head's validation and review status are recorded on the PR; the earlier counts
above describe the original implementation. No object, link or whole-TARA human
acceptance is inferred from a code review. Main and open PR file lists were
checked before choosing DL-0052.

## Review fixes (2026-11-21)

@Clovier identified that blank justifications could count as human acceptance
here, while #243 required justification but allowed a non-person Review to veto
human acceptance. @Maimcghee recommended retaining person-only verdicts and
sharing that rule. `engine.review.assertion_review_state` now implements the
storage-neutral rule: an accepted Assertion needs at least one person Review;
all person Reviews must accept it with nonblank text justifications. Contrary
person verdicts take precedence, including when their justification is missing.
Every Review remains visible; non-person Reviews neither grant nor veto human
acceptance. The helper retains the existing case/whitespace/hyphen normalization
for verdict strings, which the core schema keeps open. A matching local update
to #243 consumes the identical helper, avoiding two implementations. That
companion update is separate from #243's outstanding source-review work.

The CLI now stages a normally created file inside a private temporary directory,
then atomically replaces the destination. This respects the caller's umask
instead of unconditionally leaving mode 0600, as @Maimcghee observed, without
changing the process umask. Failed replacement retains the previous export and
removes staging files. TARA.md also identifies where a renderer finds `addresses`
slots and Assertions, separately from the requirement/mitigation trace list.

Regression tests cover missing/blank/non-text human justifications, human plus
agent reviews (including contrary agent verdicts), review targeting/order,
contrary human evidence, umasks 022/077 and failed atomic replacement. These
changes do not record human acceptance, widen Review targets or implement
the pending TARA-version governance proposals.

Local validation: **562 engine tests passed, six skipped** (five opt-in packaged
checks and the external full-catalog CWE test); all **five packaged checks passed**
against a rebuilt Python 3.13 sidecar. Frontend typecheck/build and 373 tests,
Rust fmt/clippy and four tests, 14 publishing tests, archdoc and publishing
guards passed. The browser preview is current; the unchanged pinned library
still has 550 records, zero errors and 122 existing warnings. Cross-consumer
checks cover 12 review scenarios and both review orders, with identical answers
and no input mutation. The mvp-02 JSON remains byte-identical to the prior export
with SHA-256 `4238a573a546db95ea48d4adf584d2746fd40debdfc33dbfe105810f17213712`.
Remote CI must be checked after pushing these review fixes.
