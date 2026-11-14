---
schema: "archdoc/v1"
id: DL-0052
title: "TARA collect phase: deterministic engine intermediate for mvp-02"
type: process
status: draft
version: "0.1.0"
date: "2026-11-14"
updated: "2026-11-14"
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

The branch starts at PR #229's `a1e97c3` because collection needs the #63 risk
calculator. #229 remains a dependency until accepted and merged; no sponsor
decision or human review is inferred from that implementation. The library
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

Local validation completed:

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

No human acceptance is claimed by this log. The implementation is prepared
locally; publication requires @paria03's saved push approval and fresh CI on
the published head. PR #229 and this work require human review. Main and open
PR file lists were checked before choosing DL-0052.
