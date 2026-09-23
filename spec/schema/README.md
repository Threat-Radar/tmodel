# spec/schema/

Our **threat-model object model** — the encoding-neutral schema for the logical
types this system reasons about: assets, components, trust boundaries, threats,
attack paths / threat chains, weaknesses (CWE), vulnerabilities (CVE/NVD),
mitigations, risk scores, and the **human review / annotation** state attached to
each.

Two hard requirements shape it, both open as `DEC-*` until settled:

1. **Import (and possibly export) existing formats.** We do not invent in a
   vacuum. The model must ingest the schemas and object models the field already
   uses (surveyed in `research/0001-threat-modeling-landscape`), and re-express
   them. Candidate imports are recorded as `library/` records, not vendored here.
2. **Traceable human review.** An AI-proposed threat or attack path is a
   hypothesis. The schema must carry who reviewed it, what impact a human
   assigned, whether a threat is mitigated for a given product, and how that
   holds over the product's design lifecycle — so a generic threat mapped onto a
   specific product (or product family) keeps its provenance and its review.

This directory is empty of a chosen schema on purpose: selecting an encoding now
would decide `DEC-*` by accident. Draft schemas go in as proposals against
ARCH-0001.
