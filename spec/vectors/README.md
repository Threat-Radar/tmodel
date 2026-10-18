# spec/vectors/

Published example threat models and test vectors — the interop and regression
contract. A vector is a concrete, worked threat model (or a fragment of one)
expressed in our schema: an asset with a trust boundary, a threat, an attack
path/chain, a mapped CWE/CVE, a mitigation, and its review state.

Vectors are how we prove:

- an imported external format round-trips into our model,
- a risk metric computes the same score everywhere,
- a threat chain renders the same graph everywhere,
- a UI or exporter reads the model without a private side agreement.

## These are EXAMPLES, not accepted truth

The object model (`../schema/tmodel-object-model.linkml.yaml`) is a **DRAFT
proposal — DEC-001 is OPEN**; nothing here ratifies it. These vectors exist to
**dogfood** that draft: to prove honest, worked examples validate against it, and
to surface what the model still cannot express. They are not normative, not a
sign-off on any product, and carry **no project person's real name** — people
appear as github ids / roles only (CLAUDE.md). AI-proposed content is marked
`proposed` on its Assertion and is never presented as reviewed.

## CORE §8 MVP vectors — DEC-001a evidence (`mvp-NN-*.yaml`)

These are the acceptance evidence for **DEC-001a**, the **CORE** object model: a
reviewed attack-path knowledge graph with **NO governance layer** (no ThreatModel /
SecurityProgram / Gate / Milestone / Checkpoint / Requirement / GovernedView) and
**no Environment/Deployment** (`ARCH-0001-PROPOSAL` §8: "no Environment parameter —
post-MVP, H3"). They realise the §8 "MVP vectors 1–6 + 18" set — the critic's
"attack-path KG, no Environment, no governance". The filename number `NN` is the §8
vector the file primarily realises.

| File | §8 vector | Domain | Realises |
|---|---|---|---|
| `mvp-01-software-doc-service.yaml` | **1** | software (ADR-0002 *deep*) | container-image software model: Components w/ CPE/purl `identifiers`, CVE→CWE→CAPEC with propagation as a reviewed Assertion, two ordered AttackPaths (**AND** + **OR** gate), composite-vector RiskScore, graph `View`, human-reviewed vs AI-proposed |
| `mvp-02-automotive-ecu.yaml` | **2** | automotive / embedded (ADR-0002 *breadth*) | ISO 21434 TARA asset/damage/threat-scenario binding onto the core classes + same CWE/CVE backbone; firmware/HBOM instance identity; remote+pivot AND/OR paths; composite RiskScore; AI-proposed path **human-rejected** |
| `mvp-03-hierarchical-system.yaml` | **3** | system (ADR-0002 *system* type) | 3-level `composed_of` subsystem tree; two subsystem threats **roll up** to one system-level DamageScenario + a worst-path system RiskScore; AND/OR paths; cross-subsystem AI-proposed pivot |
| `mvp-18-shared-vuln-vex-override.yaml` | **18** | hardware + software | one finding propagates **core → chip → server** in product A; a **second product is VEX `not_affected`**; propagation and the per-product override both via the Assertion+Review spine (also the §8 vector-4 flavour — divergent per-product disposition, no ProductFamily class) |

**Cross-cutting §8 vectors.** Vector **5** (multi-step AND/OR attack path with ordering)
and vector **6** (AI-proposed threat, human-reviewed-or-rejected, with provenance)
are exercised **inside every** `mvp-NN` file, not as standalone fragments. Vector
**4** (product-family divergent mitigations) has **no core home** — `ProductFamily`
and `MitigationInstance` are not core classes — so it is shown in its expressible
form (per-product divergence via VEX + per-instance `mitigation_status`) in
`mvp-18`, and recorded as a limit in the design log. Vectors 7–17 are post-MVP.

Each `mvp-NN` vector validates against the **CORE** container
(`example-container-core.linkml.yaml`, class `ExampleModelCore`), whose tree root
exposes collections for the DEC-001a core classes **only** — no governed-layer and
no Environment/Deployment collections — so "no governance, no Environment" is
enforced structurally, not by convention.

## Governance-heavy worked examples (`tv-*.yaml`)

These exercise the **full** model including the DEC-001b governed layer; they
validate against the full `ExampleModel` container.

| File | Domain | Exercises |
|---|---|---|
| `tv-software-auth-service.yaml` | software (ADR-0002 *deep* product) | components w/ CPE/purl, CVE→CWE propagation (reviewed Assertion), two AttackPaths with AND + OR gates, Mitigations w/ status, composite-vector RiskScore (ADR-0006), Party roles, human-reviewed vs AI-proposed, a governed **ThreatModel** snapshot (supersedes chain), and an **SDL SecurityProgram** (Gate/Milestone, a `Requirement` with an opaque `source_ref`, a Gate that `validates_conformance_of` the ThreatModel) |
| `tv-hardware-brake-ecu.yaml` | hardware/firmware (ADR-0002 *breadth* product) | firmware-image hash + compute cores as structural/instance identity, a physical/glitch AttackPath, LifecyclePhase + Environment/Deployment, Mitigations w/ status, composite-vector RiskScore, human-reviewed vs AI-proposed, a governed ThreatModel snapshot |

## Proposal vectors (`pv-NN-*.yaml`, DL-0024)

Example models built to shape the classes DL-0024 proposes (Asset, TrustBoundary,
DataFlow; RPT-0005 G13), as the sponsor directed on 2026-10-14: published automotive
attacks, modeled from their primary write-ups. They validate against
`example-container-proposed.linkml.yaml` (class `ExampleModelProposed`), the core
container plus collections for the proposed classes. **AI-drafted and unreviewed:**
every Assertion is `proposed`, no Review is recorded, and feasibility and impact are
left for a human.

| File | Attack | Source | Exercises |
|---|---|---|---|
| `pv-01-can-injection-theft.yaml` | keyless car theft by CAN injection (Toyota RAV4, CVE-2023-29389) | Canis Automotive Labs write-up, 2023-04-03; CVE record | Asset, nested TrustBoundary zones, DataFlows on two CAN buses, `instance_of` with a CVE whose CWE came from CISA-ADP (Assertion with `asserted_by`) |
| `pv-02-dealer-portal-owner-data.yaml` | theft of owners' personal data and silent takeover through a dealer portal (Kia, 2024) | Curry et al. write-up, 2024 | Assets with confidentiality, a dealer-only zone, DataFlows that carry personal data, a Weakness without a CVE (an `exploits` Assertion by a `software_agent` Party) |

```sh
for v in pv-01-can-injection-theft pv-02-dealer-portal-owner-data; do
  linkml-validate -s spec/vectors/example-container-proposed.linkml.yaml \
    -C ExampleModelProposed spec/vectors/$v.yaml
done
python3 design-log/0024-schema-proposal-g13/check-refs.py \
  spec/vectors/mvp-*.yaml spec/vectors/tv-*.yaml spec/vectors/pv-*.yaml
```

## Validating a vector

`linkml` is installed. Each vector is one tree-rooted file validated against the
`ExampleModel` container (`example-container.linkml.yaml`), which imports the real
object model and adds **only** a flat per-type collection class so a whole worked
example validates in one invocation. The container is a **test harness**; it is
not part of the domain model and is not rendered into `OBJECT-MODEL.md`.

```sh
# CORE §8 MVP vectors (DEC-001a) — CORE container, no governed collections:
for v in mvp-01-software-doc-service mvp-02-automotive-ecu \
         mvp-03-hierarchical-system mvp-18-shared-vuln-vex-override; do
  linkml-validate -s spec/vectors/example-container-core.linkml.yaml \
    -C ExampleModelCore spec/vectors/$v.yaml
done

# Governance-heavy worked examples — full container:
linkml-validate -s spec/vectors/example-container.linkml.yaml \
  -C ExampleModel spec/vectors/tv-software-auth-service.yaml
linkml-validate -s spec/vectors/example-container.linkml.yaml \
  -C ExampleModel spec/vectors/tv-hardware-brake-ecu.yaml
```

All report `No issues found` (0 failures). Note: `linkml-validate` checks
structure, types, enums, and cardinality; it does **not** enforce referential
integrity between the id-reference edges (`inlined: false`). Resolving every
cross-reference to a real object in the same file is a convention here, checked
for the `mvp-NN` vectors by a standalone resolver (see
`design-log/0021-mvp-core-attack-path-vectors/`): 268 id-references across the four
files, all resolving.

## Findings (what dogfooding revealed)

See `design-log/0019-object-model-example-vectors/` for the full list. The one
change the examples **forced** into the draft schema: an opaque, multivalued
`identifiers` slot on `Product` / `ProductInstance` / `Component`, so a software
build/commit/SBOM/purl/CPE and a hardware firmware-image digest (ADR-0002 per-type
instance identity) have a home — previously only catalog classes carried a
`catalog_ref`, and `catalog_ref` names a *generic* catalog entry, not the concrete
artifact. Remaining gaps are recorded as findings, not fixed (DEC-001 stays open).
