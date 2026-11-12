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

## Weakness table (#144)

`weakness-table.json` is the engine's answer to `GET /weaknesses/table`, with no
parameters, over the CWE sample in `engine/tests/fixtures/cwe/`: nine weaknesses
copied verbatim from CWE 4.20. It lets a weakness table view (#58) start before the
CWE import reaches a running engine (DL-0050).

It is generated in the same way as the library fixture, and
`engine/tests/test_weakness_table.py` fails when the engine's answer no longer
matches it. Agree a new shape on #58 first, then regenerate it from the engine
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
