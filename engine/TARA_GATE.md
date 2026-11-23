# TARA approval and freshness criterion (#185)

This is a **read-only governance pilot**, stacked on #251 and #253. It checks the
recorded exit criterion "a human-approved, current TARA exists". It does not write
a Review, change `Gate.gate_status`, approve a TARA, or prove product conformance.
The governed classes and version-review fields remain DEC-001b proposals.

`engine.core.evaluate_tara_gate(gate, record, current_digest=..., evidence_link=...)`
is the storage-neutral engine operation. Its DTO has `status` (`passed`/`failed`),
the Gate and version IDs, revision, evidence paths, latest person-review IDs,
approved/current digests, a stale flag and reasons. No clock, machine path or run
identifier is added. The result is deterministic and neither input is mutated.

A criterion passes only when:

- `validates_conformance_of` names a ThreatModel in the record, and every
  `gated_by` Requirement has the explicitly requested evidence route to that version;
- both version status fields say approved;
- every declared required role has a current person's approval, including an
  approver role, and `approved_by` includes that current approver's Review;
- no relevant review comment is open;
- `approval_digest` is valid and equals the digest recomputed from today's inputs.

Agent reviews are retained in the input but cannot fill a role. The latest review
is selected by its timestamp as an instant, not by file order. Equal-time contrary
verdicts fail the criterion rather than selecting an arbitrary winner. Earlier
approvals cannot override a later request for changes. Only the named version is
considered; a different version's approval or evidence does not satisfy it.

## Evidence route remains an explicit proposal choice

The sponsor's choice between DL-0027 decision 6 and DL-0054 decision 1 is still
open. There is **no default or automatic fallback**:

| Mode | Route exercised |
|---|---|
| `direct` | Requirement `evidenced_by` → ThreatModel (DL-0027's proposed new edge) |
| `evidence-chain` | Requirement ← `implements` SdlPractice `produces` → Evidence `evidence_of` → ThreatModel (#251's proposal); the Evidence must be a model and name the same revision |

The actual #251 record uses the Evidence route. The direct route has a synthetic
engine test; adding that edge to a validated record still requires a matching
proposal/accepted schema. Supporting both operations does not select either one
or widen the accepted core schema. Proposed Assertions do not become slot links.

## Validated file adapter and local preview

With the pinned LinkML tools installed (`spec/schema/requirements.txt`):

```sh
python docs/publishing/check_tara_gate.py models/tcu/governance.yaml \
  --gate prototype/185-tara-gate/gate.yaml --evidence-link evidence-chain --json
```

The adapter runs #180's schema/reference checks, validates the pilot Gate shape,
and uses **#183's `input_digest.digest`**, not a second digest implementation.
Its inputs must stay inside the repository, including after resolving symlinks.
There is no option to supply an allegedly current digest to the file adapter.

Exit codes: **0** criterion met, **1** unmet, **2** invalid/unavailable input.
The checked-in version 1 is still a draft, with missing human approvals and an
open comment. Its expected result is **unmet (exit 1)**. No real approval is
created to obtain a passing demo; passing fixtures exist only in temporary tests.

For a new local preview, append `--preview /tmp/tara-gate-history.html`. The
preview says "Governance pilot" and "Example data"; it cannot overwrite an
existing file or write into published `docs/`. It does not create `vN/`, update
`latest/` or publish an unapproved draft.

## History renderer integration (#182)

`docs/publishing/check_tara_gate.assess` returns that same engine DTO after file
validation and digest computation. `render_history_status(result)` is an escaped,
side-effect-free HTML section for #182's history page. A renderer can use:

```python
result = assess(record_path, gate_path, evidence_link=selected_route)
history_section = render_history_status(result)
```

The local preview exercises the section now. The actual version/history renderer
is still #182's deliverable; this change does not claim that its public history
page exists. Once that renderer lands, it must include this section and cover its
own templates in #183's digest inputs.

The #183 **publish gate** and this **existence criterion** answer different
questions. An unpublished draft legitimately passes the publish guard because
nothing is being published; it fails this existence criterion. An old approved
version with changed inputs always fails this criterion, even when the publish
guard only reports staleness on an unrelated PR. CODEOWNER/PR approval remains
the publish guard's responsibility; offline metadata is not a PR approval check.
