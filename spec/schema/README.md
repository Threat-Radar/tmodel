# spec/schema/

Our **threat-model object model** — the encoding-neutral schema for the logical
types this system reasons about: assets, components, trust boundaries, threats,
attack paths / threat chains, weaknesses (CWE), vulnerabilities (CVE/NVD),
mitigations, risk scores, and the **human review / annotation** state attached to
each.

Two hard requirements shape it, both open as `DEC-*` until settled:

1. **Import (and possibly export) existing formats.** We do not invent in a
   vacuum. The model must ingest the schemas and object models the field already
   uses (surveyed in `research/0001-threat-modeling-landscape`), and re-express
   them. Candidate imports are recorded as `library/` records, not vendored here.
2. **Traceable human review.** An AI-proposed threat or attack path is a
   hypothesis. The schema must carry who reviewed it, what impact a human
   assigned, whether a threat is mitigated for a given product, and how that
   holds over the product's design lifecycle — so a generic threat mapped onto a
   specific product (or product family) keeps its provenance and its review.

*Status 2026-10-18: ADR-0007 made LinkML the schema language (DEC-002), and ADR-0010
accepted the core type system in `tmodel-object-model.linkml.yaml` (DEC-001a); the
governed layer in the same file is still a proposal (DEC-001b). The paragraph below
predates both.*

This directory is empty of a chosen schema on purpose: selecting an encoding now
would decide `DEC-*` by accident. Draft schemas go in as proposals against
ARCH-0001.

A Grok draft (not accepted) is in [`PROPOSAL-grok-object-model.md`](PROPOSAL-grok-object-model.md) with [`tmodel-object-model.linkml.yaml`](tmodel-object-model.linkml.yaml). It does not choose the schema.

## Generated files

`generated/` holds the files ADR-0007 says are generated from the LinkML, never written by hand (#64):

| file | generator | use |
|---|---|---|
| `generated/tmodel-object-model.schema.json` | `gen-json-schema` | validating instance data as JSON |
| `generated/tmodel-object-model.shacl.ttl` | `gen-shacl` | validating instance data as RDF (the Oxigraph store, ADR-0008) |
| `generated/tmodel_object_model.py` | `gen-pydantic` | Python types for the engine and its loaders |

Regenerate after any change to `tmodel-object-model.linkml.yaml`, and commit the result:

```sh
python -m pip install -r spec/schema/requirements.txt   # pinned tools
bin/gen-schema                                          # rewrite generated/
bin/gen-schema --check                                  # what CI runs
```

The `schema` CI job (`.github/workflows/schema.yml`) fails a pull request when `generated/` is out of date, when a vector in `spec/vectors/` does not validate, or when an id-reference in an MVP core vector does not resolve.
