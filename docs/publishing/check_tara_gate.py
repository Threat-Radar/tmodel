#!/usr/bin/env python3
"""Evaluate the #185 TARA criterion and prepare an optional local history preview.

Uses #180's proposal validator and #183's real input digest. The evidence route is
explicit because DL-0027's direct edge and DL-0054's Evidence route remain open.
Exit 0: criterion met; 1: criterion unmet; 2: invalid input or unavailable inputs.
This is not the #183 publish gate, does not query PR approval, and publishes nothing.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from check_governance import SCHEMA, check_file
from input_digest import ROOT, TEMPLATE, digest

sys.path.insert(0, str(ROOT / "engine"))
from engine.core import evaluate_tara_gate  # noqa: E402
from engine.graph import GraphError  # noqa: E402
from engine.tara_gate import EVIDENCE_LINKS  # noqa: E402


def _inside(path: Path, root: Path) -> Path:
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise GraphError("input file is outside the repository")
    return resolved


def assess(
    record: Path,
    gate_file: Path,
    *,
    evidence_link: str,
    root: Path = ROOT,
    schema: Path = SCHEMA,
) -> dict[str, Any]:
    """Validated file adapter for #182's history renderer; never writes the record."""
    record, gate_file = _inside(record, root), _inside(gate_file, root)
    try:
        from linkml.validator import validate
    except ImportError as exc:
        raise GraphError("governance validation needs spec/schema/requirements.txt") from exc
    errors = check_file(record, root, schema)
    if errors:
        raise GraphError("invalid governance record: " + "; ".join(errors))
    doc = yaml.safe_load(record.read_text(encoding="utf-8"))
    gate = yaml.safe_load(gate_file.read_text(encoding="utf-8"))
    if not isinstance(gate, Mapping):
        raise GraphError("gate file must contain one Gate mapping")
    report = validate(dict(gate), str(schema), "Gate")
    errors = [r.message for r in report.results if r.severity.name == "ERROR"]
    if errors:
        raise GraphError("invalid pilot Gate: " + "; ".join(errors))
    target = gate.get("validates_conformance_of")
    if not isinstance(target, str):
        raise GraphError("gate needs validates_conformance_of")
    for path in (doc["governs"], *TEMPLATE):
        _inside(Path(path), root)
    current = digest(record, doc, target, root)
    return evaluate_tara_gate(gate, doc, current_digest=current, evidence_link=evidence_link)


def render_history_status(result: Mapping[str, Any]) -> str:
    """Escaped HTML section #182 can embed in history; no file or policy side effects."""

    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    label = "Met" if result["status"] == "passed" else "Not met"
    reasons = "".join(f"<li>{esc(reason)}</li>" for reason in result["reasons"])
    if not reasons:
        reasons = "<li>Recorded human approvals and evidence are current.</li>"
    return (
        '<section aria-label="TARA approval and freshness check">'
        "<h2>TARA approval and freshness check</h2>"
        f"<p><strong>{label}</strong> · version {esc(result['revision'])}</p>"
        "<p>Governance pilot · Example data, not an assessment of a real product.</p>"
        f"<p>{esc(result['interpretation'])}</p>"
        f"<ul>{reasons}</ul>"
        "<details><summary>Recorded evidence</summary><dl>"
        f"<dt>Evidence route exercised</dt><dd>{esc(result['evidence_link'])}</dd>"
        f"<dt>Approved input digest</dt><dd>{esc(result['approval_digest'] or 'Not recorded')}</dd>"
        f"<dt>Current input digest</dt><dd>{esc(result['current_digest'])}</dd>"
        "</dl></details></section>"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("record", type=Path)
    parser.add_argument("--gate", required=True, type=Path, help="explicit pilot Gate file")
    parser.add_argument("--evidence-link", required=True, choices=EVIDENCE_LINKS)
    parser.add_argument("--json", action="store_true", help="print the history DTO")
    parser.add_argument("--preview", type=Path, help="new local HTML preview outside docs/")
    args = parser.parse_args(argv)
    try:
        result = assess(args.record, args.gate, evidence_link=args.evidence_link, root=ROOT)
        if args.preview:
            output = args.preview.resolve()
            if output.is_relative_to((ROOT / "docs").resolve()) or output.suffix != ".html":
                raise GraphError("preview must be an .html file outside published docs/")
            page = (
                '<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width">'
                "<title>TARA gate pilot — local history preview</title>"
                "<style>body{font:17px system-ui;max-width:900px;margin:40px auto;"
                "padding:0 24px;line-height:1.5}dd{overflow-wrap:anywhere}</style>"
                "<main>" + render_history_status(result) + "</main></html>"
            )
            # Drafts stay previews; do not replace an existing file or publish vN/latest.
            with output.open("x", encoding="utf-8") as stream:
                stream.write(page)
        if args.json:
            print(json.dumps(result, sort_keys=True, indent=2))
        else:
            print(f"{result['gate']}: {result['status']} (pilot criterion only)")
            for reason in result["reasons"]:
                print(f"  {reason}")
        return 0 if result["status"] == "passed" else 1
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        print(f"check_tara_gate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
