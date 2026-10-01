---
schema: "archdoc/v1"
id: DL-0003
title: "Sponsor review → iteration 3 (physical/environment, networks, data-flow, provenance)"
type: process
status: draft
version: "0.1.0"
date: "2026-09-30"
updated: "2026-09-30"
record: DL-0003
---

# DL-0003 — Sponsor review of the object model → iteration 3

AI-assisted design record for #15, per `CLAUDE.md`. Two rounds of sponsor comments
on ARCH-0001-PROPOSAL-v0.2.0 (iteration 2); all folded into iteration 3.

## Round 1 — physical context, codebase issues, propagation, hardware depth
Comments & how addressed:
- **Physical/environmental (server in secure facility vs phone; inside vs outside the car).**
  → `Deployment`→`Environment` (physical_security / connectivity / operational_context),
  per-instance; `AttackSurface.exposure` (internal/external/remote); feasibility & risk
  made **deployment-relative**. (R-023)
- **Codebase issues mapped to ≥1 product, later Jira-backed.** → `Finding` on a shared
  `Component` propagates to all products via `uses_component`; `external_refs` (Jira) on
  Finding/MitigationInstance/Review. (R-028)
- **Can vulnerabilities carry; other objects needed?** → propagation of applicability
  along `uses_component`/`composed_of`; **VEX** per-instance override; surfaced the new
  objects (Deployment/Environment, AttackSurface, Interconnect/Bus, Network, external_refs).
  (R-027)
- **Component depth: chips in a server, cores in a chip on a bus.** → recursive
  `composed_of`; **Interconnect/Bus** as a non-containment `connected_via` that threats
  traverse.

## Round 2 — networks, data flow, process provenance
- **Ethernet, multiple servers, server-to-server long distance, DNS.** → Interconnect
  generalized to `Network`/`NetworkLink` (bus→Ethernet→WAN); network **services as
  Components** (DNS/gateway/LB/CA) with `depends_on`. (R-026)
- **Complex workflows; AI workflows through servers over networks; AI in phone vs secure
  server communicating.** → behavioral **DFD layer**: `Process`/`DataFlow`/`DataStore`/
  `ExternalEntity`/`Workflow` over the structure, crossing trust boundaries. (R-024)
- **Processing in a data flow — compiling, AI generation by a prompt.** → `Process` =
  PROV `Activity`; compile = SLSA/in-toto build provenance; AI-gen = prompt→output
  provenance. (R-025)
- **Capture & show the provenance of a flow.** → PROV-O subgraph (`used`/`wasGeneratedBy`/
  `wasDerivedFrom`/`wasAssociatedWith`); a provenance view in the console (#10); reuses
  SLSA/in-toto + the GUAC library record. (R-025)

## Accepted / adapted
- All comments accepted and folded in (R-023…R-028; vectors 14–18).
- **Scoping note:** the model now expresses far more than the ADR-0002 MVP needs; §9 of
  the proposal marks what the MVP demonstrates (one flow, one provenance chain, one
  second-domain product) vs. the full target. Audit objects stay deferred (#19).
- Rejected: nothing — these are additive and align the model with DFD-based frameworks
  (#6) and the schema crosswalk (#9).

## Next
Iteration 4: fold research #6/#7/#9; decide the edge-reification mechanism
(DEC-002/DEC-004) that gates process/edge provenance; build the vectors; then fold into
ARCH-0001 §3/§4 and accept DEC-001 via an ADR.
