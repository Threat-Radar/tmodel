# CAPEC fixtures

The CAPEC import tests (#244) read these files, so they run in CI without MITRE's 3.8 MB
catalog or the library submodule.

| File | What it is |
|---|---|
| `capec_v3.9-sample.xml` | One CAPEC catalog cut from MITRE's CAPEC 3.9: 13 attack patterns (CAPEC-5, 7, 23, 63, 66, 88, 115, 192, 273, 478, 497, 602, 701), 3 categories (CAPEC-210, 371, 684), 3 views (CAPEC-483, 703, 1000), the 15 external references they cite, and REF-9, which none of them cites but which carries `Edition`, the one reference field the 15 lack. Together they hold every entry field, every abstraction and status value, every kind of link between attack patterns and every taxonomy the release uses |
| `library/` | A one-record test library whose `capec` record pins the sample's SHA-256 |
| `.gitattributes` | Keeps the sample's bytes as they are: git converts no line ends and adds no final newline (MITRE's file has none) |

## Where the sample comes from

MITRE's `capec_v3.9.xml` (2023-01-24, schema 3.5), the file the library record `capec`
pins: https://capec.mitre.org/data/xml/capec_v3.9.xml, 3,849,998 bytes, SHA-256
`70279a2dff0cb0ad79e546adb07828335a704ad5210e047e09e986172fc9e34d`. The sample is that
file's bytes up to and including the `Attack_Pattern_Catalog` start tag, then each
container's start line, the chosen entries' lines in file order, and the container's end
line, then the end tag. Every entry is byte for byte as MITRE wrote it. The sample, like
the whole file, validates against `ap_schema_v3.5.xsd` (SHA-256 `7b6a8e95…6a80a0`) with
`xmllint --nonet`, with the W3C XHTML schemas matched by digest.

- `capec_v3.9-sample.xml`: 126,027 bytes, SHA-256 `0faa35f49021c2bc652725a53ad371d047675d4e40370dace32f558f15c18b7e`

## Terms of use

The sample holds CAPEC content. MITRE's copyright designation and licence, which the
CAPEC Terms of Use (https://capec.mitre.org/about/termsofuse.html) require in any copy:

> Copyright © 2007-2023, The MITRE Corporation. CAPEC and the CAPEC logo are trademarks of
> The MITRE Corporation.
>
> The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license to
> use Common Attack Pattern Enumeration and Classification (CAPEC™) for research,
> development, and commercial purposes. Any copy you make for such purposes is authorized
> provided that you reproduce MITRE’s copyright designation and this license in any such
> copy.
