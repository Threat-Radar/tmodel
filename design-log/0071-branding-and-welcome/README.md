---
schema: "archdoc/v1"
id: DL-0071
title: "tmodel branding, design system, and welcome screen"
type: process
status: draft
version: "0.1.0"
date: "2026-11-26"
updated: "2026-11-26"
record: DL-0071
defers_to: ARCH-0001
bears_on: [APP-0001, DL-0038, DL-0051, DL-0070]
---

# tmodel branding, design system, and welcome screen

## Request

Establish the visual identity and the desktop welcome. The approved
logo screenshot supplied the radar geometry and wordmark. The HTML reference
supplied the composition, contour lines, connected nodes, concentric rings, and
sweep. The written brief specified the final copy, the compact Get started
button, both appearances, and the existing workspace as the destination.
The follow-up requested the welcome at every fresh native launch.

## Produced

- The reusable radar SVG preserves the three rings, diagonal, sweep, and detection
  points. Both lockups render the SVG in the document so its strokes and fills use
  the active WebView appearance. The favicon uses the same geometry. The Tauri icon
  tool generated the native resources from a light rendering with a rounded ice
  white tile and soft border. The translucent sweep keeps the two interior
  rings visible underneath it.
- The lowercase wordmark uses the actual 700 face of Unbounded. Inter Medium
  sits centered underneath it with tracked uppercase lettering. The compact
  workspace lockup uses the same lettering and radar. On the welcome screen,
  the wordmark is slightly larger, the Inter Medium 500 tagline is smaller,
  and the full lockup sits slightly left of the page midpoint to balance its
  visual weight.
  Inter Variable is used in
  the interface and canvas labels. Both WOFF2 files and the original SIL OFL 1.1
  notices are bundled. Upstream revisions and packaging details are recorded in
  `apps/desktop/THIRD_PARTY_NOTICES.md`.
- The welcome centers the complete lockup, tagline, supporting sentence, and
  44-pixel action within the webview. The artwork grows with the window and fades
  behind the text. The decorative sweep makes a continuous 54-second rotation.
  The two existing contours on the left change shape together over a seamless
  28-second loop, and two nodes pulse once on arrival. Reduced-motion mode
  leaves the contours at rest and suppresses the sweep, pulse, and workspace
  transition.
- A fresh native launch presents a focused main landmark and one native button.
  Enter from the landmark advances. Enter and Space also work on the focused
  button. Get started removes the welcome from the current window, reveals the
  workspace, and transfers focus. Navigation, history, and model changes within
  the loaded workspace keep welcome dismissed. Completion is never saved, so
  the next fresh launch shows welcome without a preference reset. Engine startup
  can proceed before the user enters the workspace. An explicit model or view
  link opens the workspace directly. The Pages preview opens directly to the
  read-only examples.
- Semantic tokens define surfaces, borders, typography, spacing, focus, action
  states, status colors, and canvas colors. Existing OS appearance behavior drives
  both palettes. Both Cytoscape views read the same tokens as the DOM and update
  their styles when appearance changes. Review labels, edge patterns, and
  provenance remain visible alongside their colors.

## Appearance and accessibility

| Role | Light | Dark |
| --- | --- | --- |
| Application background | `#F4F7FA` | `#111D2B` |
| Surface | `#FFFFFF` | `#1C2D40` |
| Brand and heading text | `#20354B` | `#E8F0F7` |
| Icon accent | `#587C9D` | `#A3C4DE` |
| Selection | `#DCE8F2` | `#304A62` |
| Surface border | `#CEDCE8` | `#3A5269` |
| Primary action | `#20354B` / `#FFFFFF` | `#B5D0E7` / `#142638` |

The foreground tokens target 4.5:1 for text. Control boundaries and focus
indicators have dedicated tokens checked at 3:1 against their adjacent surfaces.
Status chips and banners carry explicit labels. The welcome artwork is hidden
from the accessibility tree and has no pointer targets.

## Native screenshots

Captured from Tauri windows using the local Python sidecar. The before screenshot
uses `origin/main` at `fbae65a`. Light and dark review builds used temporary
bundle identifiers and per-window appearance overrides. macOS System Settings
were left alone.

| View | Light | Dark |
| --- | --- | --- |
| Workspace before | [Model Report](screenshots/workspace-before.jpg) | |
| Welcome | [Light](screenshots/welcome-light.jpg) | [Dark](screenshots/welcome-dark.jpg) |
| Workspace after | [Model Report](screenshots/workspace-light.jpg) | [Model Report](screenshots/workspace-dark.jpg) |

## Implementation and verification

The redesign preserves the existing Model Report, Attack Paths, Explore Graph,
and Library navigation from PR #272. Library data, review and risk calculations,
the Python engine, and the API retain their existing behavior. Standalone
published model reports retain their site styles. The dedicated Projects page
and separately scoped importer, local-project, review, and risk work remain
follow-up phases.

In the original branding verification, both native appearances were visually
checked at 1280 × 800 and about 926 × 589. The native WebKit inspector reported both bundled font faces loaded
and Unbounded at weight 700. Manual checks exercised welcome, Tab and Enter,
the pointer action, focus transfer, model selection, Library navigation, search and filter reset, sorting and
pagination, the Details inspector, path fitting, graph highlighting and zoom,
and report disclosures. Review builds connected to the real packaged sidecar.
The native inspector confirmed the sweep moved and ran once for 4.6 seconds.
Automated WKWebView layout checks covered short and narrow workspaces, graphs,
pagination, and popovers.

The Pages build was regenerated with the pinned library. An automated WKWebView
smoke test exercised both palettes, local font and favicon loading, the
read-only controls, the ten-model catalog, a model and CWE deep link, graph
rendering, model switching, and Back and Forward. Production Tauri packaging
created an ad hoc signed macOS bundle and local disk image.

Verification passed for 580 frontend tests, 122 publishing tests, four Rust
tests, and 784 engine tests with ten skips. TypeScript, Cargo formatting and
Clippy, generated asset freshness, public links and identity guards, and
architecture documentation checks passed.

The launch-behavior follow-up adds regression checks for opening welcome again
on a fresh launch, dismissing it for the loaded workspace, and preserving direct
links and preview entry. TypeScript and all 581 frontend tests passed on the
follow-up. The regenerated Pages preview passed deep-link and history checks in
both appearances. The regular native bundle continues to inherit system
appearance.

The welcome refinements retain the same composition and artwork. Regression
checks cover the looping radar, drift of the existing contours, and reduced
motion. The native WebViews reported a running sweep and contour drift in both
appearances. The welcome screenshots show the refined composition. Get started
opened the connected workspace, and the regular bundle was relaunched on
welcome using macOS appearance. All 582 frontend tests and preview freshness
checks passed.

## Final background refinement

The previous contour animation translated both lines by a few pixels together
over 24 seconds. The strokes stayed parallel and retained their shape, so the
motion read as an almost imperceptible drift. The final version keeps the curve
endpoints in place and interpolates their Bézier control points and intermediate
joins. Both curves return to the same resting pose every 28 seconds. WebKit
runs the SVG timing directly, while the 54-second CSS radar rotation runs on
its own timeline.

The left and right node groups, radar rings, rotating sweep, contour strokes,
and dotted texture each have theme-specific opacity. The right node group
receives the larger reduction. The tagline is about 10 percent smaller and
retains Inter Medium 500 and its line spacing. The wordmark, logo, subtitle
alignment, supporting copy, button, and layout spacing retain their approved
settings.

All 583 frontend tests passed. Offscreen WKWebView renders covered light and
dark appearances at 1280 × 800 and 926 × 589. Geometry checks measured the
contours in the viewport across successive cycles and checked continuity at
both animation boundaries. A simulated reduced-motion preference left the
contours at rest, and the reduced-motion stylesheet rule disabled the radar
rotation in that test. The regular native bundle was rebuilt and its signature
verified at the worktree release path. The production app was left unopened
for manual review. The native screenshots above predate this final adjustment.

## Graph color refinement

Explore Graph assigns a dedicated color to each category. Product is blue,
Component teal, Vulnerability coral, Weakness amber, Attack Pattern purple,
Threat Instance rose, Attack Path orange, Attack Step sky blue, Requirement
green, and other types slate. Light and dark use the same associations. The
canvas and the circular legend read the same tokens. The original circular
nodes, dimensions, borders, selection styles, path highlighting, and layout
remain in place.

Attack Paths keeps its original rounded boxes and AND/OR gates. Its tinted
surfaces and connector accents follow the roles of steps, threats, damage,
mitigations, and targets. Review colors retain their meanings and the
existing line patterns and labels.

The contrast suite checks graph text at 4.5:1 and graphical elements at 3:1
against their relevant backgrounds. Simulations for protanopia, deuteranopia,
and tritanopia found pairs that look similar, including coral and green under
deuteranopia. Category text in the node list and selected-object inspector,
and the existing review labels and line patterns, convey those distinctions.
[WCAG use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) ·
[Machado et al.](https://pubmed.ncbi.nlm.nih.gov/19834201/)

Both native appearances verified the complete TCU view with all ten legend
groups, match between node and legend colors, original circle dimensions
and borders, and path highlighting. The Papermill model verified Attack Paths
fills, labels, gates, connector patterns, and the dashed review outline.
All 645 frontend tests passed and the regenerated browser preview passed
freshness, link, and identity checks. The regular worktree bundle was signed
and left unopened.

## Code review follow-up

- The light scrollbar thumb uses `#6A8299`. Its contrast is 3.99:1 against
  the white table, 3.81:1 against inset panels and striped rows, and 3.71:1
  against the application background. The tests also cover raised surfaces,
  subtle surfaces, and the graph canvas in both appearances. The native
  Library table reported the new thumb over its transparent track while
  scrolling.
- A selected node inside a highlighted path has a solid circular ring, with
  a canvas-colored gap around the node's categorical fill. The ring follows
  the theme's text color and leaves the node's dimensions and layout intact.
  The isolated native review app with the bundled engine drew the ring at
  0.30× in both appearances in the full 35-node TCU model. The images below
  show the same selection in the WebKit browser preview at that zoom,
  centered on the highlighted path.
- Welcome and the workspace now consult the same view router. A recognized
  view or nonempty `model` or `file` reference opens directly. Unknown
  fragments and empty or whitespace-only references keep welcome visible.
  Browser preview continues to open directly and preserve history.

| Explore Graph selection | Light | Dark |
| --- | --- | --- |
| TCU, highlighted path at 0.30× | [Light](screenshots/graph-selection-light.jpg) | [Dark](screenshots/graph-selection-dark.jpg) |

All 679 frontend tests and 122 publishing tests passed. The production desktop
build and regenerated preview passed TypeScript, preview freshness, link, and
identity checks. The regular macOS bundle was rebuilt, passed strict signature
verification, and stayed unopened. Native verification used a separate Tauri
build with a per-window appearance switch. The deferred radar motion refinement
remains outside this review follow-up.
