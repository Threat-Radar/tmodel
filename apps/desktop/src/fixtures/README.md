# Fixtures

`library-table.json` is the engine's answer to `GET /library/table`, with no
parameters, over the 12 sample records in `engine/tests/fixtures/library/`. It
lets the library table views (#58) start before they talk to a running engine
(#141).

It is generated, not written by hand. `engine/tests/test_library_table.py` fails
when the engine's answer no longer matches it, so a change to the shape shows up
in CI. Agree a new shape on #58 first, then regenerate it from the engine folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_library_table.py
```

The answer has six parts:

| Key | What it holds |
|---|---|
| `library` | the library's digest, its record count, and the files that failed to load |
| `query` | the filters, search, sort, order, limit and offset the answer used |
| `total`, `count` | matches before paging, and rows in this answer |
| `rows` | one row per record: id, title, short title, type, shelf, status, maturity, date, publisher, topic, tags, url, artifact counts and extraction profile |
| `facets` | whole-library counts for type, status and topic |
| `contextual_facets` | counts constrained by the active search and other filters; each facet excludes its own filter so users can switch selections |

`contextual_facets` is a backward-compatible response addition for #58. The
meaning of `facets` does not change, so existing API clients continue to receive
whole-library counts.

`GET /library?id=<record id>` returns one record in full, for a details view.

The published browser preview does not use this 12-record development fixture.
`docs/publishing/render_app.py` writes the complete public table to
`docs/app/data/library/table.json`; the browser filters, searches, sorts and
builds bounded row-derived document details without publishing local record
paths or the full library records.

## Weakness table (#144)

`weakness-table.json` is the engine's answer to `GET /weaknesses/table`, with no
parameters, over the CWE sample in `engine/tests/fixtures/cwe/`: nine weaknesses
copied verbatim from CWE 4.20. It lets the weakness table view (#234) start before
the CWE import reaches a running engine (DL-0050).

It is generated in the same way as the library fixture, and
`engine/tests/test_weakness_table.py` fails when the engine's answer no longer
matches it. Agree a new shape on #234 first, then regenerate it from the engine
folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_weakness_table.py
```

| Key | What it holds |
|---|---|
| `catalog` | which CWE release: name, version, date, schema version, file name, SHA-256, entry counts, how many entry fields the reader does not know, and MITRE's `notice`, `license` and `terms_url` |
| `query` | the filters (abstraction, structure, status, usage), search, sort, order, limit and offset the answer used |
| `total`, `count` | matches before paging, and rows in this answer |
| `rows` | one row per weakness: CWE id, tmodel object id, name, abstraction, structure, status, mapping usage, likelihood of exploit, description, how many CAPEC links, observed examples and mitigations it has, and its page on cwe.mitre.org |
| `facets` | whole-catalog counts for abstraction, structure, status and usage |
| `contextual_facets` | the same counts under the active search and the other filters, each leaving out its own |

`search` looks in the id, name, description and alternate terms. `sort` takes id
(by number), name, abstraction, structure, status, usage or likelihood; the last five
sort in CWE's own order (Pillar, Class, Base, Variant, Compound; Stable to Deprecated;
Allowed to Prohibited; High to Low), not alphabetically.

`GET /weaknesses?id=CWE-79` returns one entry with every CWE field, for a details
view, plus the tmodel objects the import makes for it. `GET /weaknesses` without
parameters says where each CWE field goes and which links the import could not map.

The desktop app uses this fixture only when opened with
`?weaknessSource=fixture`; its normal source is the local engine and the complete
pinned catalog. The GitHub Pages build uses the same nine-row fixture because a
static page has no local engine or catalog. Fixture selection shows the complete
row summary but deliberately does not fabricate the full `GET /weaknesses?id=…`
payload: the inspector explains that full catalog fields and proposed
relationships require the live engine.

The rows are CWE content. The CWE Terms of Use (https://cwe.mitre.org/about/termsofuse.html)
allow copies on the condition that each one reproduces MITRE's copyright designation
and licence, so every answer carries them in `catalog`, and a view that shows the rows
should show `catalog.notice` and link to `catalog.terms_url`. The licence in full:

> Copyright © 2006-2026, The MITRE Corporation. CWE, CWSS, CWRAF, and the CWE logo are
> trademarks of The MITRE Corporation.
>
> CWE™ is free to use by any organization or individual for any research, development,
> and/or commercial purposes, per these CWE Terms of Use. Accordingly, The MITRE
> Corporation hereby grants you a non-exclusive, royalty-free license to use CWE for
> research, development, and commercial purposes. Any copy you make for such purposes
> is authorized on the condition that you reproduce MITRE’s copyright designation and
> this license in any such copy. CWE is a trademark of The MITRE Corporation. Please
> contact cwe@mitre.org if you require further clarification on this issue.

## Attack-pattern table (#244)

`attack-pattern-table.json` is the engine's answer to `GET /attack-patterns/table`, with no
parameters, over the CAPEC sample in `engine/tests/fixtures/capec/`: 13 attack patterns
copied verbatim from CAPEC 3.9. It lets the attack-pattern table view (#236) start before
the CAPEC import reaches a running engine (DL-0056).

It is generated in the same way as the weakness fixture, and
`engine/tests/test_attack_pattern_table.py` fails when the engine's answer no longer
matches it. Agree a new shape on #236 first, then regenerate it from the engine folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_attack_pattern_table.py
```

| Key | What it holds |
|---|---|
| `catalog` | which CAPEC release: name, version, date, schema version, file name, SHA-256, entry counts, how many entry fields the reader does not know, and MITRE's `notice`, `license` and `terms_url` |
| `query` | the filters (abstraction, status, likelihood, severity), search, sort, order, limit and offset the answer used |
| `total`, `count` | matches before paging, and rows in this answer |
| `rows` | one row per attack pattern: CAPEC id, tmodel object id, name, abstraction, status, likelihood of attack, typical severity, description, the CWE ids it relates to and the ATT&CK techniques it maps to (lists, so a view can link them), how many related attack patterns, attack steps, mitigations and examples it has, and its page on capec.mitre.org |
| `facets` | whole-catalog counts for abstraction, status, likelihood and severity |
| `contextual_facets` | the same counts under the active search and the other filters, each leaving out its own |

`search` looks in the id, name, description, alternate terms, CWE ids and ATT&CK ids.
`sort` takes id (by number), name, abstraction, status, likelihood or severity; the last
four sort in CAPEC's own order (Meta, Standard, Detailed; Stable to Deprecated; High to
Low; Very High to Very Low), not alphabetically.

`GET /attack-patterns?id=CAPEC-66` returns one entry with every CAPEC field, for a details
view, plus `references`, each reference the entry cites resolved to its title, authors,
edition, publication, publisher, date and URL (`resolved` is false for one the release
does not define), and the tmodel objects the import makes for it. `GET /attack-patterns`
without parameters says where each CAPEC field goes, which links the import could not
map, and which citations and attack-pattern links name nothing in the release.

The rows are CAPEC content. The CAPEC Terms of Use (https://capec.mitre.org/about/termsofuse.html)
allow copies provided that each one reproduces MITRE's copyright designation and licence,
so every answer carries them in `catalog`, and a view that shows the rows should show
`catalog.notice` and link to `catalog.terms_url`. The licence in full:

> Copyright © 2007-2023, The MITRE Corporation. CAPEC and the CAPEC logo are trademarks of
> The MITRE Corporation.
>
> The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license to
> use Common Attack Pattern Enumeration and Classification (CAPEC™) for research,
> development, and commercial purposes. Any copy you make for such purposes is authorized
> provided that you reproduce MITRE’s copyright designation and this license in any such
> copy.

## Model report inputs (#208)

`report-input-mvp-01.json`, `report-input-mvp-02.json` and
`report-input-mvp-03.json` are what the Model report view reads for those three
example models: the model's `/models` entry,
its `/graph` answer and one `/attack-paths` answer per threat. The `file` fields
hold the bare file name, never a local path. The report, path-diagram and
static-page tests run on them, so they test real model data rather than a mock.

They are a saved snapshot of the engine's answer, so their values can lag the
model files: editing mvp-01 or mvp-02 does not break any test. What
`engine/tests/test_models_surface.py` does check is their shape: if the engine
renames or drops a field the report reads, it fails and asks for the GUI types
to be updated. Every model's default view (all eight) is checked on the
published pages in `docs/models/` instead (`model-pages.test.ts`). To refresh
the snapshot on purpose, from the engine folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_models_surface.py
```

`sdl-01-view.json` is the engine's answer to `GET /sdl?file=sdl-01-tmodel-desktop.yaml`
(DL-0043). `engine/tests/test_sdl.py` fails when it drifts. After a change to the SDL
model or the view, regenerate it from the engine folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_sdl.py
```

## Review screens (#290)

`human-review-revisions.json` is the #289 review service's own answer, for the shared
example in `engine/examples/human-review/`, to the two requests the review screens need
beside `contract.json`'s: the refresh of r1 (a project version before its first save) and
the context at r2 (after the contract's save, with the reviewer's own review to correct).
`engine/tests/test_review_frontend_fixture.py` makes them with the same model, workspace
double, principal and save request, and fails when they drift. After a contract change
agreed on #289 and #290, regenerate it from the engine folder:

```sh
cd engine && TMODEL_UPDATE_FIXTURES=1 .venv/bin/pytest tests/test_review_frontend_fixture.py
```

`model-workspace-contract.json` is a copy of #288's `engine/examples/model-workspace/contract.json`
(SHA-256 `efd4750f6b61a8c2…`), its examples of every workspace operation and error, made
by #288's own tests. #288 is not merged into this branch yet; once it is, the tests should
read #288's file instead and this copy should go.

`sbom-import-responses.json` holds answers of the engine's `POST /import/sbom` for the
Import New Product screen, in that route's contract shape: a success, a success with a
platform warning, and a refusal. Their model and report texts, counts, warning and refusal
message are the #257 importer's own output for its `alpine-3.24.2` test files, from
`import_sbom.build()` with `--platform linux/arm64/v8`, `linux/amd64`, and no scan or
platform; `counts.assertions` is `match_assertions + cwe_assertions`, as the route adds it,
and `product` and `suggested_name` are the values the route's contract example gives for
this image. The importer is not on this branch, so no test here regenerates them. The model
texts were made again from #268's 55a5f40, whose ids end in 16 hex digits of their keys'
SHA-256 where they had 8; nothing else in them changed.
