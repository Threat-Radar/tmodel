# Collecting a TARA intermediate (#181)

The engine collects one model into a JSON file for the TARA render phase
(#182). It retains the source records, their KG identifiers and review evidence,
plus the #63 risk calculations. It does not approve a TARA, change a model,
accept proposals, or publish an HTML page. Governance, version history and the
approval digest remain the separate DL-0027 tasks.

## Run it

From the repository root:

```sh
PYTHONPATH=engine engine/.venv/bin/python -m engine tara mvp-02-automotive-ecu.yaml \
  --matrix annex-h-table-h8 --in-process --output /tmp/tcu-tara.json
```

Omit `--output` to print the same JSON to stdout. `--json` is accepted for
consistency with the other CLI operations; this command always emits JSON.
With `tmodel serve` running, replace `--in-process` with
`--url http://127.0.0.1:47811`. Both transports use the same engine facade:

```text
GET /tara?file=mvp-02-automotive-ecu.yaml&matrix=annex-h-table-h8
```

The API only reads models under the approved example directory, including the
bundled examples in an installed app. Absolute paths and symlinks must resolve
inside that directory. CLI basenames refer to those examples; paths with a
directory are relative to the caller. An `output` API parameter is refused:
only the CLI writes files on the caller's machine. Output filenames must end in
`.json`; a temporary file in the destination directory is replaced atomically
only after successful collection and serialization. A bad input leaves a
previous export untouched. The destination directory must already exist.

Exit 0 means the collection succeeded, including when some assessment inputs
are missing. Those incomplete rows and hypotheses are part of the requested
draft, not export errors. Exit 1 means an input, service or output error; exit 2
means a CLI usage error. The explicit matrix choice has the same informative
example status as [RISK.md](RISK.md); no feasibility or impact is invented.

## Format for the renderer

`tmodel.tara-collection/v1` identifies a derived engine DTO, not a new canonical
object-model schema. Its fields are:

| field | content |
|---|---|
| `source` | example filename and `example_data: true`; no machine-local path |
| `notice` | explicit draft/non-approval label |
| `scope` | `whole_model` and all source Product IDs |
| `records` | every collection recognized by the graph adapter, with an array per collection, including empty arrays |
| `requirement_links` | `Mitigation.stated_as` and `Requirement.satisfied_by` links, with source/target IDs, origin and review evidence |
| `calculated_risk` | the existing calculator's matrix, assessment rows and computed routes, with source IDs and review summaries |

The export covers the entire input model. It does not infer which subset of a
multi-product file is a separate product assessment. The pilot's mvp-02 file
contains one Product, the TCU.

Each entry in `records` has this envelope:

```json
{
  "id": "asset:diagnostic-service",
  "type": "Asset",
  "data": {"id": "asset:diagnostic-service", "name": "Remote diagnostic service"},
  "review_state": {
    "scope": "related_assertions",
    "status": "unreviewed",
    "reviewed": false,
    "assertion_ids": [],
    "review_ids": [],
    "assertions": []
  }
}
```

`data` retains the source fields, including nested impact vectors, descriptions,
requirements, clause locators and provenance. YAML dates become ISO strings;
unsupported non-JSON values are refused. References stay IDs so a renderer can
resolve names without losing traceability. Every Assertion and Review is also
exported as a record. No authored value or review is rewritten.

The expected renderer order is: item/products/components; assets and damage
scenarios; threats; impact; attack paths and feasibility; calculated risk;
mitigations/treatment descriptions; requirements and their links. The source
RiskScore descriptions remain available for authored treatment reasoning. The
collector does not parse prose into a new treatment-decision schema or turn
requirement links into a conformance verdict (#170).

## Reading review state correctly

The core's Review targets an Assertion, not an arbitrary object. Therefore
`scope: related_assertions` summarizes claims touching a record; it is **not**
approval of the endpoint object or the whole TARA. `scope: assertion` is the
Assertion's own evidence, and `scope: target_assertion` on a Review describes
its target. With no evidence, the state is `unreviewed`, not accepted.

The collector keeps every review and does not choose the last one in file
order. Only a Review whose reviewer is recorded as a `Party` of kind `person`
can contribute to human acceptance. The Assertion must also be recorded as
`accepted`, at least one such review must say `accepted`, and all recorded
person reviews must agree. Rejection and changes requested take precedence;
unknown/missing verdicts cannot establish acceptance. A proposed Assertion
stays proposed even if a review says accepted. Non-person reviews remain in
the export and cannot supply human approval. This reads recorded provenance;
it does not authenticate a person's identity or implement the approval gate.

A record touching claims in different states is `mixed`. The individual claim
states and review IDs remain visible. Slot links have `origin: slot`; they are
recorded source relationships, not newly reviewed Assertions. Assertion links
have `origin: assertion` and retain their own proposed/rejected/accepted state;
they are never copied into a requirement or mitigation's slot.

Calculated risk is kept separate from authored `risk_scores`. A row's
`source_id` references its RiskScore, or its ThreatInstance when no score is
recorded; its review summary describes that source. Route digests are derived
result identifiers, not invented KG objects or proof of review. Route
`rating_paths`, authored path IDs and step IDs link back to the source records.
Missing ratings remain null and mitigation status never lowers numeric risk.

## Repeatability and the TCU example

Serialization sorts object keys and source record IDs, uses UTF-8, two-space
indentation and one final newline. It adds no current time, run ID or local
filesystem path. Authored sequence-valued fields are preserved. The same input
and matrix produce the same bytes, also across processes with different Python
hash seeds. This byte stability is not an approval digest rule for #183.

For mvp-02, the file includes both assets, both threats, both authored paths,
six requirements and the original assertion/review records. The diagnostic
scenario calculates S/F/O/P **5/4/5/1**. The AI-proposed infotainment path remains
visible with its recorded rejection; its OR routes remain unrated and its risk
incomplete. A consumer must not label that hypothesis accepted merely because
collection or calculation succeeded.

Tests cover repeatable CLI output, API/CLI parity, complete source identities,
rejected/proposed content, contrary reviews in either order, non-person
reviews, missing reviews, requirement links, invalid references, output errors
and file confinement. The opt-in bundled-engine check exercises `/tara` after
relocating only the executable, without a Python installation or checkout.
