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

The answer has five parts:

| Key | What it holds |
|---|---|
| `library` | the library's digest, its record count, and the files that failed to load |
| `query` | the filters, search, sort, order, limit and offset the answer used |
| `total`, `count` | matches before paging, and rows in this answer |
| `rows` | one row per record: id, title, short title, type, shelf, status, maturity, date, publisher, topic, tags, url, artifact counts and extraction profile |
| `facets` | how many records have each type, status and topic, for filter menus |

`GET /library?id=<record id>` returns one record in full, for a details view.
