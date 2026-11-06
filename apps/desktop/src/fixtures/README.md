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

## Model report inputs (#208)

`report-input-mvp-01.json` and `report-input-mvp-02.json` are what the Model
report view reads for those two example models: the model's `/models` entry,
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
