# Library test fixtures

Byte-for-byte copies of 13 `record.yaml` files from Threat-Radar/library at
commit `a28a013`, the commit this repo pins as the `library` submodule: 12
records, plus one superseded version kept inside its record. They let
`tests/test_load_library.py` run the library loader (#139) on real records in
CI, which checks out this repo without its submodules.

They are test data, not library content. Never edit them to fix a record: fix
the record in the `library` repo. When the pin moves, these copies may fall
behind; that is fine, because they test parsing, not current content.

| Record | Shelf | Why it is here |
|---|---|---|
| `rfc-8785` | ietf | rfc, distilled with a full extraction (7 artifacts, none reviewed yet) |
| `rfc-8152` | ietf | rfc with a `part_of` relation |
| `rfc-9393` | ietf | stub with one-line implementation entries |
| `draft-mih-scitt-agent-action-capsule` | ietf | draft with a superseded version under `versions/-02/` |
| `benedetti-2024-sbom-python` | academic | paper stub with page count, media type and extra keys (`venue`, `license`) |
| `sbomproof-2025` | academic | paper whose arXiv id is unquoted, so it must stay text |
| `sudokn-okn` | academic | web page with applicability and a usefulness verdict |
| `gram` | community | repo with a pinned `commit` and blank `date` and `sha256` |
| `cwe` | other | dataset (the CWE catalog record that #61 builds on) |
| `ecma-424` | other | duplicate pointer (`duplicate_of`) |
| `eo-14306` | regulator | spec with citations, both record ids and the document's own labels |
| `threattree-help` | vendor | web page with a named commercial implementation |

No summaries are copied, so every fixture record has `summary` set to `None`.
The test of the whole pinned library covers summaries.
