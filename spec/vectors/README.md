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

## Current vectors

| File | Domain | Exercises |
|---|---|---|
| `tv-software-auth-service.yaml` | software (ADR-0002 *deep* product) | components w/ CPE/purl, CVE→CWE propagation (reviewed Assertion), two AttackPaths with AND + OR gates, Mitigations w/ status, composite-vector RiskScore (ADR-0006), Party roles, human-reviewed vs AI-proposed, a governed **ThreatModel** snapshot (supersedes chain), and an **SDL SecurityProgram** (Gate/Milestone, a `Requirement` with an opaque `source_ref`, a Gate that `validates_conformance_of` the ThreatModel) |
| `tv-hardware-brake-ecu.yaml` | hardware/firmware (ADR-0002 *breadth* product) | firmware-image hash + compute cores as structural/instance identity, a physical/glitch AttackPath, LifecyclePhase + Environment/Deployment, Mitigations w/ status, composite-vector RiskScore, human-reviewed vs AI-proposed, a governed ThreatModel snapshot |

## Validating a vector

`linkml` is installed. Each vector is one tree-rooted file validated against the
`ExampleModel` container (`example-container.linkml.yaml`), which imports the real
object model and adds **only** a flat per-type collection class so a whole worked
example validates in one invocation. The container is a **test harness**; it is
not part of the domain model and is not rendered into `OBJECT-MODEL.md`.

```sh
linkml-validate -s spec/vectors/example-container.linkml.yaml \
  -C ExampleModel spec/vectors/tv-software-auth-service.yaml
linkml-validate -s spec/vectors/example-container.linkml.yaml \
  -C ExampleModel spec/vectors/tv-hardware-brake-ecu.yaml
```

Both currently report `No issues found` (0 failures). Note: `linkml-validate`
checks structure, types, enums, and cardinality; it does **not** enforce
referential integrity between the id-reference edges (`inlined: false`). Resolving
every cross-reference to a real object in the same file is a convention here.

## Findings (what dogfooding revealed)

See `design-log/0019-object-model-example-vectors/` for the full list. The one
change the examples **forced** into the draft schema: an opaque, multivalued
`identifiers` slot on `Product` / `ProductInstance` / `Component`, so a software
build/commit/SBOM/purl/CPE and a hardware firmware-image digest (ADR-0002 per-type
instance identity) have a home — previously only catalog classes carried a
`catalog_ref`, and `catalog_ref` names a *generic* catalog entry, not the concrete
artifact. Remaining gaps are recorded as findings, not fixed (DEC-001 stays open).
