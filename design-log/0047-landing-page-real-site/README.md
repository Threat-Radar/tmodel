---
schema: "archdoc/v1"
id: DL-0047
title: "Landing page: replace the download mock with the real site"
type: process
status: draft
version: "0.1.0"
date: "2026-11-09"
updated: "2026-11-09"
record: DL-0047
defers_to: ARCH-0001
---

# Landing page: replace the download mock with the real site

## Request

#202 item 2 (@Maimcghee): replace the GitHub Pages distribution mock on
`docs/index.html` with a landing page that shows what tmodel produces and how
to get a real build. Screenshots come from DL-0038 (#211). The page must stay
static HTML and CSS with no scripts.

## Produced (#212)

- Replaced the fake macOS / Linux / Windows download buttons, the
  "Version 0.0.0-mock" stamp, and the SKILL.md / manifest links with a real
  site: app screenshots (model report, attack path, explore graph), cards for
  example models, the mvp-02 TARA draft, research reports, the bibliography,
  the tmodel SDL page, and the YAML under `spec/vectors`.
- Listed all eight example models, grouped the same way the app's model picker
  groups them, each linking to its static `docs/models/` page from #211.
- "Get tmodel" points at the unsigned rolling
  `latest-main` macOS `.dmg` (`tmodel_macos_aarch64.dmg` from #213) and at the
  README quickstart for building from source. Mock install steps are gone.
- Kept the newer main additions that landed while the PR was open: the SDL
  page link (#217), the model pages (#211), and the fixed-name `.dmg` download
  (#213).

## Merge note (this entry)

`topic/202-landing-page` was rebased onto current `main` by merge (no force-push)
after #211, #207, #224 and #226 landed. The only conflict was the top nav in
`docs/index.html`: main still had the mock "Download" / "Install" links; the
branch kept the real-site nav (Example models, Reports, Bibliography, Get
tmodel, About). `docs/models/` from #211 clears the `check_links` failures that
blocked archdoc on earlier heads of this PR.

## Choices and limits

Documentation and static Pages assets only. No engine, app, schema, or release
workflow changes in this PR. The `.dmg` remains an unsigned development build;
the release page stays linked for checksum and attestation.
