---
schema: "archdoc/v1"
id: DL-0011
title: "RPT-0014 AI threat model: multi-agent search, coverage critique, report review"
type: process
status: draft
version: "0.1.0"
date: "2026-10-02"
updated: "2026-10-02"
record: DL-0011
---

# DL-0011: RPT-0014 AI threat-model research

AI-assisted research record for #71 / #72 (per `CLAUDE.md`).

## Question asked

Deep, PhD-level research on threats and attacks against AI systems, with full
bibliographic references. It covers publications, journals, and news; logs the
major AI security issues in the news; and captures and summarizes papers. The
goal is to extract specific attacks that map to a threat model (company,
assets). It also captures every existing AI threat model for later analysis and
answers whether a CWE-like AI weakness enumeration exists.

## Method

A single workflow (run `wf_aeac1556-700`):

1. **Search**: six parallel dimension agents (ML-model attacks; LLM, RAG, and
   agent attacks; enumerations; published threat models; news incidents; supply
   chain, infrastructure, and AI-enabled offense).
2. **Coverage critique**: a fresh adversarial agent at max effort checks
   technical-paper coverage against top-venue programs and Semantic Scholar
   citation ranks, and spot-checks citations for fabrication.
3. **Gap fill**: two agents close the named gaps and correct or reject suspect
   entries.
4. **Synthesize**: dedupes sources and writes the report plus derived artifacts.
5. **Report review**: two adversarial lenses at max effort, one for threat
   completeness and mapping, one for evidence and citation rigor.
6. **Fold**: applies or rejects each finding.

PDFs go to a local cache outside every repo
(`~/cb/projects/tmodel2026/pdf-cache/ai-threat-model/`); only filenames and
sha256 digests are recorded.

## Results, accepted, rejected

_Filled in when the run completes._
