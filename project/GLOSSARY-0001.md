---
schema: "archdoc/v1"
id: GLOSSARY-0001
title: "Glossary — threat-modeling terms as this project uses them"
short_title: "Glossary"
description: "Controlled definitions for terms that mean more than one thing across sources. The object-model terms defer to ARCH-0001 §3."
type: process
category: process
status: draft
version: "0.1.0"
date: "2026-09-23"
updated: "2026-09-23"
needs_review: true
reviewed: false
canonical_path: project/GLOSSARY-0001.md
defers_to: ARCH-0001
---

# Glossary

Terms as **this project** uses them. The object-model types are normative in
ARCH-0001 §3; this restates them plainly and adds the surrounding vocabulary.

- **Threat** — an adverse action against an asset. Not the same as a vulnerability.
- **Weakness** — a *class* of flaw (maps to **MITRE CWE**). A `Vulnerability` is a concrete instance (maps to **CVE / NVD**).
- **Attack path / threat chain** — an ordered set of threats leading to damage; rendered as a graph.
- **Mitigation** — a control reducing a threat, mapped to the threat(s) it addresses; its state is per product and versioned.
- **Risk** — *how bad* a threat is, **in an environment**. Not intrinsic. See ARCH-0001 §6.
- **Review** — human judgement attached to any element: impact, verdict, rationale, reviewer, date. An AI-proposed element is a hypothesis until reviewed.
- **Product / product family** — the concrete thing a generic threat is mapped onto. Family members may differ in which attack paths are mitigated.
- **Composition analysis** — deriving components (and their weaknesses) from what a system is built of: containers/dependencies (as in `tradar`) or source code.
- **SCA** — software composition analysis.
- **CWE** — MITRE Common Weakness Enumeration.
- **NVD / CVE** — NIST National Vulnerability Database / Common Vulnerabilities and Exposures.
- **CVSS** — Common Vulnerability Scoring System.
- **ISO/SAE 21434** — automotive cybersecurity engineering standard; carries a risk-analysis method (optional, high value).
- **Common Criteria** — ISO/IEC 15408; source of an attack-feasibility metric.
- **OKF** — Open Knowledge Format: YAML front matter over Markdown, human- and agent-readable; the `library/` records and these docs follow it.
- **archdoc/v1** — the front-matter contract for `spec/` and `project/` docs, enforced by `bin/validate-archdoc`.
