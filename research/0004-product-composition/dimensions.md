---
schema: "archdoc/v1"
id: RPT-0004-dimensions
title: "RPT-0004 dimensions: the search axes"
type: research
status: draft
version: "0.1.0"
date: "2026-09-28"
updated: "2026-09-28"
record: RPT-0004
---

# RPT-0004: search dimensions

Each dimension is one section of `report.md`.

## 1. SBOM formats
CycloneDX 1.7, SPDX 3.0.1, SWID. For each format:
1. How is a component named? (`purl`, `cpe`, `hashes`, `swid`)
2. Can it describe hardware or firmware?
3. How does it say "A depends on B"?
4. How does it say "this list is complete"?
5. How does it attach vulnerabilities (CVE, CWE)?

## 2. HBOM
Hardware and firmware bills of materials. What can a hardware BOM describe that an SBOM cannot, and which formats and guidance exist?

## 3. Tools
Syft, Grype, Trivy, Dependency-Track. What each produces or consumes, which fields it fills, and whether tools agree on the same input.

## 4. tradar today
Which formats and fields tradar reads, and what it keeps or drops on the way to its graph.

## 5. Components to vulnerabilities and weaknesses
How a component is matched to CVEs (CPE vs PURL, NVD vs distro advisories) and to CWEs.

## 6. Build identity
How composition pins one specific product version (commit, hash, image digest, SBOM serial number). 