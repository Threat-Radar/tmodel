# Security policy

tmodel is a student senior project (USF CS 490, Fall 2026) sponsored by @nymble.
We take reports seriously and respond on a best-effort basis.

## Reporting a vulnerability

Please report privately through GitHub's **private vulnerability reporting**:
open the repository's **Security** tab and choose **Report a vulnerability**
([direct link](https://github.com/Threat-Radar/tmodel/security/advisories/new)).

Do not open a public issue, pull request or discussion for a suspected
vulnerability. Include what you found, how to reproduce it, the affected
version or commit, and the impact you expect.

We aim to acknowledge a report within 7 days. There is no bug bounty.

## Scope

- The Python engine (`engine/`), including the local API it serves on
  `127.0.0.1:47811`.
- The desktop app (`apps/desktop/`, Tauri + TypeScript) and its bundled engine
  sidecar.
- Release artifacts on GitHub Releases (`.dmg`, SBOM, attestations) and the
  workflows that build them (`.github/workflows/`).
- The published site at <https://threat-radar.github.io/tmodel/>.

Out of scope: example threat-model data in `spec/vectors/` (it is example data,
not a security claim), and third-party dependencies, which should be reported
upstream. We still welcome a heads-up if one affects tmodel.

## Supported versions

| Version | Supported |
|---|---|
| `latest-main` rolling prerelease | yes |
| Latest tagged release (`v0.1.x`) | yes |
| Anything older | no |

## Verifying a download

Every release `.dmg` carries SLSA Build L2 provenance (DL-0034). Verify a
download before opening it:

```sh
gh attestation verify tmodel.dmg -R Threat-Radar/tmodel
shasum -a 256 -c tmodel.dmg.sha256
```

Builds are ad-hoc signed (no Apple Developer ID yet), so macOS asks you to
confirm the first launch.
