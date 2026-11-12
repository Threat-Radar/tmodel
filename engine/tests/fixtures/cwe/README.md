# CWE fixtures

The CWE import tests (#144) read these files, so they run in CI without MITRE's 2 MB
catalog or the library submodule.

| File | What it is |
|---|---|
| `cwec_v4.20-sample.xml` | One CWE catalog holding the 13 entries the library copied verbatim from CWE 4.20 for importer tests: 9 weaknesses (CWE-79, 373, 689, 692, 710, 769, 1093, 1174, 1187), 2 categories (CWE-411, 811), 1 view (CWE-709) and 3 external references (REF-7, REF-44, REF-726) |
| `expected.json` | What the library's extraction says an importer must find in those entries, copied from its `examples/expected.yaml` |
| `library/` | A one-record test library whose `cwe` record pins the sample's SHA-256 |
| `.gitattributes` | Keeps the sample's bytes as they are: git converts no line ends (the references section ends its lines in CRLF, as MITRE's file does) |

## Where the sample comes from

The entries are byte for byte those of the library record `cwe`
(Threat-Radar/library, `records/other/cwe/distilled/examples/`), which cut them from
MITRE's `cwec_v4.20.xml` (SHA-256 `1f5a78bd62e00f86436b4fe32d5034a57e8f0da88e4063b2072b664ae510912e`,
from `cwec_v4.20.xml.zip`, SHA-256 `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`).
The sample is built the way the library builds its fixtures: the 4.20 file's first bytes
up to and including the `Weakness_Catalog` start tag, then each container with its
entries, then the end tag. Each entry's bytes were checked against the SHA-256 that
`expected.yaml` gives for it, and the sample validates against `cwe_schema_v7.3.xsd`
(SHA-256 `690dedee…e45f98`) with `xmllint --nonet`.

- `cwec_v4.20-sample.xml`: 139,913 bytes, SHA-256 `e26b565b22747a93e88a999f24d1578299e53d6669011bb9c015e690fef26b43`

## Terms of use

The sample and `expected.json` hold CWE content. MITRE's copyright designation and
licence, which the CWE Terms of Use (https://cwe.mitre.org/about/termsofuse.html)
require in any copy:

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
