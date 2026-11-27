# Third-party frontend dependencies

## Cytoscape.js

- Package: `cytoscape`
- Installed version: 3.34.0
- Project: https://js.cytoscape.org/
- License: MIT

Cytoscape.js provides the interactive knowledge-graph rendering used by Issue
#59. The MIT license permits commercial use, modification, distribution, and
private use, satisfying APP-0001 A-044.

Copyright (c) 2016-2026, The Cytoscape Consortium.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Tauri includes this notice in the distributed application. On macOS it is at
`tmodel.app/Contents/Resources/THIRD_PARTY_NOTICES.md`.

# Third-party data

## CWE (MITRE)

- Release: CWE 4.20 (`cwec_v4.20.xml.zip`), the release the library pins (ADR-0014)
- Project: https://cwe.mitre.org/
- Terms of use: https://cwe.mitre.org/about/termsofuse.html

The app's engine carries this release so the Weaknesses tab works without a download.
MITRE's terms allow copies that reproduce its copyright designation and license:

Copyright © 2006–2026, The MITRE Corporation.

CWE™ is free to use by any organization or individual for any research, development, and/or commercial purposes, per these CWE Terms of Use. Accordingly, The MITRE Corporation hereby grants you a non-exclusive, royalty-free license to use CWE for research, development, and commercial purposes. Any copy you make for such purposes is authorized on the condition that you reproduce MITRE’s copyright designation and this license in any such copy. CWE is a trademark of The MITRE Corporation. Please contact cwe@mitre.org if you require further clarification on this issue.

## Inter and Unbounded

Inter Variable is distributed as the upstream WOFF2 from
[Inter v4.1](https://github.com/rsms/inter/tree/v4.1). Unbounded Bold is the
weight-700 instance of
[Unbounded from Google Fonts](https://github.com/google/fonts/tree/5026800714d07231937d92eb4cceabf06e05d74e/ofl/unbounded),
instantiated with FontTools and encoded as WOFF2. Both fonts render from
bundled files in the desktop app and browser preview.

Both are licensed under the SIL Open Font License 1.1. Their original
copyright and license notices ship with the web assets as
`fonts/Inter-OFL.txt` and `fonts/Unbounded-OFL.txt`.
