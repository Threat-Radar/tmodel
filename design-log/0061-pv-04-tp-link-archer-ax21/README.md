---
schema: "archdoc/v1"
id: DL-0061
title: "Proposal vector pv-04: TP-Link Archer AX21, a home router to test the app on"
type: process
status: draft
version: "0.1.0"
date: "2026-11-22"
updated: "2026-11-22"
record: DL-0061
bears_on: [DEC-001a]
defers_to: ARCH-0001
---

# DL-0061: Proposal vector pv-04, TP-Link Archer AX21

AI-assisted design record (per `CLAUDE.md`), drafted by Claude Code for @Clovier. **Proposal only.** Nothing in the
model is accepted: every Assertion is `proposed`, and no Review is recorded.

## Question asked

#230 asks to test the app on real products: OWASP Juice Shop for software (pv-03, DL-0049), then a router firmware for
hardware, drafted the same way, with every attack step citing its source (a code line, a challenge, an advisory or a
CVE record). The sponsor asked for threat models in two domains. @Clovier asked for the router model "in a safe
capacity".

## What was produced

| File | What it is |
|---|---|
| `spec/vectors/pv-04-tp-link-archer-ax21.yaml` | The model, 35 objects: the product, three components, three assets, two trust boundaries, one data flow, CWE-77, CVE-2023-1389, CAPEC-248, one damage scenario, one threat, a three-step attack path, four mitigations, seven Assertions and two lifecycle phases |
| `spec/vectors/README.md` | A row for pv-04 and its line in the validation loop |
| `docs/index.html` | A row in the landing page's model table |
| `docs/models/`, `docs/app/` | Regenerated with `render_models.py` and `render_app.py` |

The one threat: someone with a device on the home network runs commands as root on the router without logging in
(CVE-2023-1389). The path: reach the web management interface from a device on the home network; exploit the
unauthenticated command injection; the router runs the commands as root.

## The two scope calls

1. **The pin: hardware version 3 (US), firmware 1.1.3 Build 20221125** (published 2022-12-02), the last numbered V3
   release before the fix, 1.1.4 Build 20230219 (published 2023-03-17). NVD's affected range ("before 1.1.4 Build
   20230219") is written in V3's numbering.
2. **Only the home-network flaw, CVE-2023-1389.** It is the one CISA lists as exploited (added 2023-05-01), and NVD
   rates it adjacent-network (CVSS 3.1 8.8, `AV:A`). The internet-side race, CVE-2023-27359 (ZDI-23-452), is left out:
   it is not in CISA's catalog, NVD lists a single affected build (1.1.1 Build 20220603), and the first hardware model
   stays small.

## Advisory level, on purpose

The model says what the flaw lets an attacker do, cites the public records, and stops there.

- **No request, address, parameter, payload or step-by-step procedure.** The injection step names the CVE and points to
  the advisories.
- **The path ends where the router runs the attacker's commands as root.** What botnets then do with a router (ZDI's
  blog of 2023-04-24 reports them using this flaw) is part of the damage scenario, not attack steps.
- **The evidence is public records:** NVD, the CVE record, CISA's catalog, ZDI-23-451, ZDI's blog, TP-Link's statement
  and V3 firmware page, and MITRE's CWE and CAPEC pages. Proof-of-concept pages are not cited.

## How it was checked

- `linkml-validate` (LinkML 1.12.1, the pinned version) against `ExampleModelProposed`: no issues for pv-01 to pv-04.
- `check-refs.py` (DL-0024): pv-04 has 35 objects and 64 references; across all ten models, 493 objects and 858
  references, all resolving.
- The engine lists ten models with no problems, and `tmodel paths` gives one path for the one threat.
- `render_models.py --check` (11 pages) and `render_app.py --check` (10 models, 685 library records) are up to date. The
  14 publishing tests pass, `check_links.py` resolves 708 pages, `check_identities.py` finds 763 files clean, and
  `bin/validate-archdoc` reports 0 errors. `vitest` passes 377 tests, `npm run typecheck` and `npm run build` are clean,
  and the engine's tests give 612 passed and 7 skipped.
- The facts come from the research notes of 2026-11-13 (sources read that day) and the saved NVD and CISA records,
  re-read on 2026-11-22: CVSS 3.1 8.8 `AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` from NVD and from the CNA, CWE-77, and the
  CISA entry added 2023-05-01 with "Apply updates per vendor instructions." CWE 4.20 links CWE-77 to CAPEC-248, and
  CAPEC 3.9 links CAPEC-248 back to CWE-77.

## Choices the agent made, open to review

- **CWE-77, not CWE-78.** NVD and CISA name CWE-77, a Class. CWE-78 (OS Command Injection, a Base) fits a command run
  by a shell more exactly, but no source names it, so it is left for a reviewer.
- **No CWE-306.** "No login is needed" fits Missing Authentication for Critical Function, but no source names it.
- **CAPEC-248 (Command Injection), not CAPEC-88.** CAPEC-248 is the pattern CWE-77 links to; CAPEC-88 links CWE-78.
- **One damage scenario.** A threat realizes one damage scenario, so taking over the router, losing the household's
  connection and being used against others are one scenario over three assets.
- **A device on the home network is a component,** so the data flow has a source. It stands for any phone, laptop or
  smart-home device on the LAN or Wi-Fi.
- **The vendor fix is a `complete` mitigation in implementation.** Updating the router and keeping it updated are
  `planned` mitigations in operation, because the pinned firmware does not have the fix. Keeping untrusted devices off
  the home network is a model suggestion, not the vendor's, and says so.
- **Feasibility and impact are unset.** They are human inputs.

## What a human accepted

- @Clovier, 2026-11-16: the pin (1.1.3 Build 20221125) and the home-network path only.
- @Clovier, 2026-11-22: build the model "in a safe capacity", which this record reads as advisory level.

Nothing in the model is accepted yet. All seven Assertions are `proposed`, and no Review is recorded.

## What was rejected, and why

- **Path B, the internet side (CVE-2023-27359):** left out, as above.
- **Exploit detail:** the request, its address and parameters, and how botnets run on a router are left out on purpose.
- **The first attempt (2026-11-16):** it followed the research notes' step list, including the botnet's own steps and
  the request format. It was stopped before anything was written, and the router model was parked. This version keeps
  to advisory level instead.

## Findings from the sources

1. **NVD's affected range misses hardware V2.** NVD's firmware range is in V3's numbering. V2 numbers its firmware
   2.1.x, and TP-Link's statement lists fixes for V1.2, V2 and V3, so a scanner matching NVD's range alone would miss
   vulnerable V2 routers.
2. **The CVE record's fixed version has a typo:** "1.14 Build 20230219" for 1.1.4.
3. **V3 has two firmware lines,** numbered (1.1.x) and date-named. The model pins the numbered line.

## Next steps

- A person checks the path, the affected versions and the fix against NVD's record and CISA's catalog entry, and
  records the result (#230's last box).
- The sponsor decides whether pv-04 joins the examples.
