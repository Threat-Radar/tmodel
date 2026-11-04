---
schema: "archdoc/v1"
id: RPT-0017
title: "Requirement extraction: library provisions as core Requirements (ADR-0012)"
short_title: "Requirement extraction"
type: research
status: draft
version: "0.1.0"
date: "2026-11-03"
updated: "2026-11-03"
bears_on: [DEC-001a, DEC-002, DEC-009]
defers_to: ARCH-0001
---

# RPT-0017: Requirement extraction

This folder turns the library's provision extractions into tmodel `Requirement`s, the core class ADR-0012 added. It holds one YAML file per library record, named `<record-id>.yaml`. Each file is a core model fragment: Requirements, the stub nodes their proposed links point at, the proposed links as Assertions, and the human Reviews of them. The work is split into lanes (#168): #169, #170, #171 and #172.

This is evidence, not a decision. ADR-0012 accepts the Requirement class. It does not accept an import mapping from the library's requirement format (DEC-002 / #9), so `convert.py` is research tooling that makes a starting skeleton, not an importer.

## What is here

| File | What it is |
|---|---|
| `README.md` | This page: the file format, the workflow and the checks |
| `convert.py` | Makes a skeleton file from a library record's `distilled/requirements.yaml` |
| `check.py` | Checks the rules below that `linkml-validate` and `check-edges.py` cannot |
| `test_convert.py` | Tests for both scripts |
| `iso-iec-30111-2019.yaml` | A sample: `convert.py`'s output for a licensed standard, unedited, so every `text` is empty |
| `<record-id>.yaml` | One file per record, added by each lane's PR |

## The file format

The format is the one in #169 and the other lane issues. A file starts with a comment header and then lists its collections:

```yaml
# <record-id>: requirement extraction, AI-proposed, UNREVIEWED unless a Review below says otherwise.
# Source: library:<record-id> (digest <sha256 from the library record>), read <date>.
# Agent: <tool + model>. Human owner: @<github-id>.
# Coverage: <n> in the source, <m> converted, <k> skipped, with the reason for each skip.
requirements:
  - id: requirement:<record-id>-<designator-slug>   # stable; never renumber
    name: "<designator> — <short title>"
    text: >-
      <one-sentence paraphrase; for a licensed standard, never the standard's words>
    text_origin: paraphrase        # paraphrase | verbatim (only if the licence allows) | authored
    requirement_kind: technical    # technical | process | audit | documentation | organizational | other
    normativity: mandatory         # mandatory | recommended | optional | informative | conditional
    source_ref: "library:<record-id>#<designator>"
    source_locator: "<designator> (§x.y)"
    applies_to_family: ["family:<family>"]   # only if the source states the scope
weaknesses: []        # stub nodes, only for targets a proposed link points at
attack_patterns: []
threat_instances: []
mitigations: []       # stated_as stays empty
parties:              # the human reviewer, by GitHub id
  - { id: "party:<github-id>", name: "@<github-id>", party_kind: person }
assertions:           # every link the agent proposes
  - id: assertion:<requirement-slug>--addresses--cwe-306
    subject: requirement:<record-id>-<designator-slug>
    predicate: addresses
    object: weakness:cwe-306
    confidence: medium
    assertion_status: proposed
    description: "Proposed by <agent>, <date>. Basis: <locator>; <one-line reason>."
reviews:              # one per link a human checked
  - { id: "review:<assertion-slug>", reviews: "assertion:<...>", reviewer: "party:<github-id>",
      review_status: accepted, justification: "<what was checked>" }
```

### Rules

- **Ingesting is not reviewing.** Every link an agent proposes is an Assertion with `assertion_status: proposed`. It becomes `accepted` only when a human Review accepts it. A rejected link stays `proposed`, with its rejecting Review. Nothing is written into a link slot (`addresses`, `satisfied_by`, `refines`, `derived_from`, `conflicts_with`, `maps_to`, `Mitigation.stated_as`).
- **Allowed predicates:** `addresses`, `stated_as`, `satisfied_by`, and, between provisions of the same source, `refines`, `derived_from` and `conflicts_with`. Links between two sources (`maps_to`) belong to MAP-0001 (#67), not here.
- **Licensed text is paraphrase only.** ISO, IEC, SAE and other paid standards get our own one-sentence paraphrase, with the clause in `source_locator`. Their wording is never copied, not even from a library `requirements.yaml` that holds it. Free sources (EU law, UNECE, NIST, CISA, OWASP, ETSI) may be `verbatim`, but a one-line paraphrase is preferred.
- **Never invent.** Every Requirement points at a real designator or locator in the source. Do not make up ids, clauses, or CWE or CAPEC numbers. If unsure, leave the link out.
- **GitHub ids only**, never real names.

## Workflow for a lane

1. **Convert.** Run `convert.py` on the library record. It copies what the library already extracted, so nothing is re-extracted.
2. **Choose the scope.** Drop the provisions outside your lane with `--only` or `--skip-file`, giving a reason for each. The reasons go into the header's coverage line, and the PR body repeats it.
3. **Fill in the skeleton.** Write each `text`, confirm or change every value marked `# REVIEW:`, and then remove the mark. Add `applies_to_family` only where the source states the scope.
4. **Propose links.** Add Assertions, each with a stub node and a description that gives its basis.
5. **Check.** Run the three checks below until all pass.
6. **Review.** A human checks at least 10 proposed links per record (or all of them, if fewer) and records each as a Review.
7. **Record.** Add a `design-log/NNNN-<slug>/` entry in the same PR, as `CLAUDE.md` requires.

## `convert.py`

```sh
python3 research/0017-requirements-extraction/convert.py \
    ../library/records/other/etsi-en-304-223 --owner <github-id> \
    -o research/0017-requirements-extraction/etsi-en-304-223.yaml
```

It needs Python 3 and PyYAML, and reads `record.yaml` and `distilled/requirements.yaml` (`library-requirements/v2`). It writes Requirements, the owner as a Party, and empty `assertions` and `reviews`. It never proposes a link.

| Field | Where it comes from |
|---|---|
| `id` | `requirement:<record-id>-<slug>`, where the slug is the designator in lower case with every other character run turned into `-` (`RQ-09-09` → `rq-09-09`, `5.1.2-3` → `5-1-2-3`). Two designators that give the same id stop the run. |
| `name` | `<designator> — <short_title>` from the library. A licensed source gets the designator only, because a short title can copy the standard's words. |
| `text`, `text_origin` | Licensed source: empty, with `paraphrase`. Free source: the library's verbatim text, whitespace normalized, with `verbatim`; `--empty-text` leaves it empty instead. |
| `normativity` | See the first table below. |
| `requirement_kind` | A default, marked `# REVIEW:`; see the second table below. |
| `source_ref` | `library:<record-id>#<designator>` |
| `source_locator` | The library's `locator`. When the designator is not already a word in it, it becomes `<designator> (<locator>)`. |
| Header | The digest from `record.yaml` (`content.sha256`), the library commit, the read date, and the coverage, with every skip and its reason. |

| Library `normativity` | tmodel `normativity` |
|---|---|
| requirement, prohibition | mandatory |
| recommendation | recommended |
| permission | optional |
| informative | informative |
| any other value (principle, consideration, statement, scope, …) | skipped with the reason, unless `--normativity VALUE=TMODEL` maps it |

The library's `condition` is not mapped to `conditional`. Where a condition is stated, the converter marks `normativity` for review instead.

| Library `nature` | Default `requirement_kind` |
|---|---|
| process, deliverable-producing | process (an activity, even one that yields a work product) |
| deliverable | documentation |
| product, property | technical |
| missing | other |
| process, where every actor is the organization or its management | organizational |

**What counts as licensed.** A record is treated as licensed if it lives under the library's `records/iso/`, or if its publisher names ISO, IEC or SAE. Today that covers the ISO, ISO/IEC, ISO/SAE and IEC records. `check.py` applies the same test to the file name, as a record id starting `iso-` or `iec-`. A licensed record anywhere else must be handled by hand: use `--empty-text`, and keep `text_origin: paraphrase`.

Other behaviour:
- Entries whose library `status` is withdrawn, retired or rescinded are skipped.
- An existing output file is not overwritten without `--force`, because it may hold reviewed work.
- Before writing, the converter parses its own output and checks it against the input.

## Checks

```sh
linkml-validate -s spec/vectors/example-container-core.linkml.yaml -C ExampleModelCore research/0017-requirements-extraction/<record-id>.yaml
python3 design-log/0021-mvp-core-attack-path-vectors/check-edges.py research/0017-requirements-extraction/<record-id>.yaml
python3 research/0017-requirements-extraction/check.py research/0017-requirements-extraction/<record-id>.yaml
```

`linkml-validate` checks the shape against the core container, and `check-edges.py` checks that every reference resolves. `check.py` checks the rules above:
- the five required fields, an id and `source_ref` that name the file's record, and no `verbatim` for a licensed record;
- no filled link slot, and only the allowed predicates, with `refines`, `derived_from` and `conflicts_with` staying in the file;
- a `Basis:` in every Assertion's description;
- `accepted` only with an accepting Review by a person, and `proposed` with none;
- a justification on every Review.

It reports empty `text` and `# REVIEW:` marks as notes, so a skeleton passes.

The `schema` workflow (`.github/workflows/schema.yml`) runs all three on every `research/0017-requirements-extraction/*.yaml`, plus `test_convert.py`, whenever a PR touches this folder.

## Limits

- `requirement_kind` is a default from two library fields, not a reading of the provision. On the 49 ISO/SAE 21434 provisions in #196, it matched the lane's own choice for 45. The other 4 are judgement calls, which is why every kind is marked for review.
- The converter reads the raw library v2 file. It does not use the library's v3 normalization loader (`bin/_requirements.py`), so that tmodel keeps to ADR-0012's reference-only rule. A record whose fields differ from the ones above needs a hand check.
- The licence test is a heuristic. #154 owns the library-side decision on licensed text.
