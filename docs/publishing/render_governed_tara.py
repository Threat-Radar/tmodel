#!/usr/bin/env python3
"""Render and publish a governed TARA from the #181 intermediate (#182).

This renderer is deliberately separate from ``render_tara.py``.  That script owns
the useful draft report built directly from an example vector; this one consumes
``tmodel.tara-collection/v1`` and the governance record proposed by #180.

Only versions accepted by #180's validator and #183's complete publication gate
are published; ``governance_status`` alone is never sufficient. A first publication
also needs #183's input digest implementation and a matching recorded
``approval_digest``. Existing ``vN/`` directories are immutable. ``latest/`` and
``history.html`` are refreshable views, so they can warn when an already-published
version later becomes stale without rewriting its historical page.

Typical use, after collecting the intermediate, is::

    PYTHONPATH=engine engine/.venv/bin/python -m engine tara \
      mvp-02-automotive-ecu.yaml --matrix annex-h-table-h8 --in-process \
      --output /tmp/tcu-tara.json
    engine/.venv/bin/python docs/publishing/render_governed_tara.py \
      /tmp/tcu-tara.json --base origin/main --pr-reviews /tmp/reviews.json \
      --head "$HEAD_SHA" --author "$PR_AUTHOR" --changed /tmp/changed.txt

Use ``--check`` to compare the refreshable pages and require each approved version
directory without writing anything.  No clock, random value, or local path enters
the output.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:
    raise SystemExit(
        "render_governed_tara: PyYAML is missing; run with engine/.venv/bin/python "
        "(CONTRIBUTING §10)"
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOVERNANCE = ROOT / "models" / "tcu" / "governance.yaml"
DEFAULT_OUTPUT = ROOT / "docs" / "models" / "tcu" / "tara"
IDENTITIES = ROOT / "publishing" / "identities.yaml"
FORMAT = "tmodel.tara-collection/v1"
EXAMPLE_NOTICE = "Example data — not an assessment of a real product."
CATEGORIES = ("safety", "financial", "operational", "privacy")
FRESHNESS_START = "<!-- freshness:start -->"
FRESHNESS_END = "<!-- freshness:end -->"
FRESHNESS_DETAILS_START = "<!-- freshness-details:start -->"
FRESHNESS_DETAILS_END = "<!-- freshness-details:end -->"
# #183 owns the algorithm.  These are the page-shaping inputs its TEMPLATE
# contract must cover before this renderer treats its result as authoritative.
DIGEST_TEMPLATE_FILES = frozenset(
    {
        "docs/publishing/render_governed_tara.py",
        "docs/publishing/render_tara.py",
        "docs/publishing/site.yaml",
        "docs/publishing/site_nav.py",
        "publishing/identities.yaml",
    }
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_nav
from render_tara import paragraphs as labeled_paragraphs

REPORT_CSS = """body{max-width:52rem;margin:0 auto 2rem;padding:0 1rem;font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a}
h1,h2,h3,h4{line-height:1.25} h1{border-bottom:2px solid #eee;padding-bottom:.3rem}
code{background:#f4f4f4;padding:.1em .3em;border-radius:3px;font-size:.9em}
pre{background:#f4f4f4;padding:1rem;overflow:auto;border-radius:6px}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95em} th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}
th{background:#fafafa} footer{margin-top:3rem;border-top:1px solid #eee;padding-top:1rem;font-size:.85em;color:#777}"""

CSS = (
    REPORT_CSS
    + """
body{max-width:76rem}.notice{border:2px solid #6b4e00;background:#fff4d6;border-radius:6px;padding:.8rem 1rem;margin:1rem 0}
.stale{border-color:#991b1b;background:#fef2f2;color:#7f1d1d}.approved{border-color:#166534;background:#ecfdf3;color:#14532d}
.meta{color:#555;font-size:.92em}.pill{display:inline-block;border:1px solid #aaa;border-radius:999px;padding:.08rem .55rem;font-size:.82em;white-space:nowrap}
.accepted{color:#14532d;background:#ecfdf3;border-color:#9fd3b2}.proposed,.unreviewed,.mixed{color:#6b4e00;background:#fefbe8;border-color:#e3cf7d}
.rejected,.incomplete{color:#7f1d1d;background:#fef2f2;border-color:#efb1b1}.authored{color:#374151;background:#f3f4f6;border-color:#c7cbd1}
.id{font-size:.82em;color:#555}.missing{font-weight:650;color:#7f1d1d}.toc{columns:2 18rem}.toc li{margin:.18rem 0}
caption{text-align:left;font-weight:650;margin:.8rem 0 .3rem}td ul{margin:.1rem 0;padding-left:1.2rem}section{scroll-margin-top:1rem}
@media print{.site-nav{display:none}}
"""
)

SECTIONS = (
    ("item", "Item definition and scope", "9.3"),
    ("assets", "Assets and damage scenarios", "15.3"),
    ("threats", "Threat scenarios", "15.4"),
    ("impact", "Impact ratings", "15.5"),
    ("paths", "Attack paths", "15.6"),
    ("feasibility", "Attack feasibility", "15.7"),
    ("risk", "Risk values and assessments", "15.8"),
    ("treatment", "Risk treatment decisions and mitigations", "15.9"),
    ("requirements", "Derived security requirements and relationships", "9.5"),
    ("governance", "Governance and review history", ""),
)


class RenderError(ValueError):
    """The intermediate or governance record cannot be rendered safely."""


@dataclass(frozen=True)
class Freshness:
    recorded: str | None
    current: str | None

    @property
    def state(self) -> str:
        if not self.recorded or not self.current:
            return "unknown"
        return "current" if self.recorded == self.current else "stale"


@dataclass
class PublishResult:
    created: list[Path] = field(default_factory=list)
    preserved: list[Path] = field(default_factory=list)
    refreshed: list[Path] = field(default_factory=list)
    out_of_date: list[Path] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GateDecision:
    """Result supplied by the authoritative #180/#183 checks."""

    errors: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class GateContext:
    """PR evidence required by #183 for a newly published or changed version."""

    pr_reviews: Path | None = None
    head: str | None = None
    author: str | None = None
    base: str | None = None
    changed: tuple[str, ...] = ()


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load_yaml(path: Path) -> Mapping[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise RenderError(f"{path}: expected a mapping")
    return value


def load_intermediate(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise RenderError(f"{path}: expected a JSON object")
    return value


def validate(intermediate: Mapping[str, Any], governance: Mapping[str, Any]) -> None:
    if intermediate.get("format") != FORMAT:
        raise RenderError(f"expected {FORMAT}, got {intermediate.get('format')!r}")
    source = intermediate.get("source")
    if not isinstance(source, Mapping) or source.get("example_data") is not True:
        raise RenderError(
            "the TCU pilot must be collected with source.example_data: true"
        )
    governs = governance.get("governs")
    if not isinstance(governs, str) or Path(governs).name != source.get("file"):
        raise RenderError(
            "governance.governs does not identify the intermediate's source file"
        )
    records = intermediate.get("records")
    if not isinstance(records, Mapping):
        raise RenderError("the intermediate has no records mapping")
    risk = intermediate.get("calculated_risk")
    if not isinstance(risk, Mapping) or not isinstance(risk.get("assessments"), list):
        raise RenderError("the intermediate has no calculated_risk.assessments list")


class Records:
    """Lookup that never discards the source envelope or its review state."""

    def __init__(self, intermediate: Mapping[str, Any]) -> None:
        raw = intermediate["records"]
        self.collections: Mapping[str, Any] = raw
        self.by_id: dict[str, Mapping[str, Any]] = {}
        for values in raw.values():
            for envelope in values if isinstance(values, list) else []:
                if isinstance(envelope, Mapping) and isinstance(
                    envelope.get("id"), str
                ):
                    self.by_id[envelope["id"]] = envelope

    def all(self, name: str) -> list[Mapping[str, Any]]:
        values = self.collections.get(name) or []
        return [v for v in values if isinstance(v, Mapping)]

    def envelope(self, oid: object) -> Mapping[str, Any]:
        return self.by_id.get(oid, {}) if isinstance(oid, str) else {}

    def data(self, oid: object) -> Mapping[str, Any]:
        value = self.envelope(oid).get("data")
        return value if isinstance(value, Mapping) else {}

    def name(self, oid: object) -> str:
        data = self.data(oid)
        return str(data.get("name") or oid or "")


def refs(data: Mapping[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    return [item for item in values if isinstance(item, str)]


def version_records(governance: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        version
        for kind in ("threat_models", "governed_views")
        for version in governance.get(kind) or []
        if isinstance(version, Mapping) and isinstance(version.get("id"), str)
    ]


def revision(version: Mapping[str, Any]) -> int:
    try:
        number = int(str(version.get("revision", "")))
    except ValueError as exc:
        raise RenderError(f"{version.get('id')}: revision must be an integer") from exc
    if number < 1:
        raise RenderError(f"{version.get('id')}: revision must be positive")
    return number


def approved_versions(governance: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    approved = [
        v
        for v in version_records(governance)
        if v.get("governance_status") == "approved"
    ]
    numbers = [revision(v) for v in approved]
    if len(numbers) != len(set(numbers)):
        raise RenderError("approved versions must have unique revisions")
    return sorted(approved, key=revision)


def version_members(version: Mapping[str, Any], records: Records) -> frozenset[str]:
    """Return the exact #180 governed scope, rejecting ambiguous membership."""
    raw = version.get("members")
    if not isinstance(raw, list) or not raw:
        raise RenderError(f"{version.get('id')}: members must be a non-empty list")
    if not all(isinstance(member, str) for member in raw):
        raise RenderError(f"{version.get('id')}: every member must be an id")
    members = frozenset(raw)
    missing_ids = sorted(members - records.by_id.keys())
    if missing_ids:
        raise RenderError(
            f"{version.get('id')}: members missing from the TARA intermediate: "
            + ", ".join(missing_ids)
        )
    return members


def _member_envelopes(
    records: Records, collection: str, members: frozenset[str]
) -> list[Mapping[str, Any]]:
    return [row for row in records.all(collection) if row.get("id") in members]


def _member_assessments(
    intermediate: Mapping[str, Any], members: frozenset[str]
) -> list[Mapping[str, Any]]:
    return [
        assessment
        for assessment in intermediate["calculated_risk"]["assessments"]
        if isinstance(assessment, Mapping)
        and (
            assessment.get("source_id") in members
            or assessment.get("threat") in members
        )
    ]


def approved_identities(path: Path = IDENTITIES) -> frozenset[str]:
    if not path.is_file():
        return frozenset()
    doc = load_yaml(path)
    values = doc.get("approved") or []
    return frozenset(str(value).lstrip("@").lower() for value in values)


def party_label(
    party_id: object,
    parties: Mapping[str, Mapping[str, Any]],
    approved: frozenset[str],
    role: object = None,
) -> str:
    party = parties.get(str(party_id), {})
    kind = party.get("party_kind")
    name = str(party.get("name") or "")
    if kind == "software_agent":
        return name or "AI agent"
    if kind == "person":
        if role:
            return f"{str(role).replace('_', ' ')} role"
        handle = (
            name.lstrip("@") if name.startswith("@") else str(party_id).split(":")[-1]
        )
        if handle.lower() in approved:
            return f"@{handle}"
        if "role" in name.lower() and "@" not in name:
            return name
        return "human reviewer (identity withheld)"
    return name or str(party_id or "not recorded")


def pill(text: str, css: str) -> str:
    return f'<span class="pill {css}">{esc(text)}</span>'


def missing(label: str = "Not recorded") -> str:
    return f'<span class="missing">{esc(label)}</span>'


def state_badge(envelope: Mapping[str, Any]) -> str:
    state = envelope.get("review_state")
    state = state if isinstance(state, Mapping) else {}
    data = envelope.get("data")
    data = data if isinstance(data, Mapping) else {}
    status = str(state.get("status") or "unreviewed")
    scope = state.get("scope")
    proposed = data.get("assertion_status") == "proposed"
    if proposed and status == "rejected":
        return pill("Proposed assertion — rejected", "rejected")
    if proposed:
        return pill("Proposed assertion — not accepted", "proposed")
    if status == "rejected":
        label = (
            "Rejected assertion"
            if scope == "assertion"
            else "Related assertion rejected"
        )
        return pill(label, "rejected")
    if status == "accepted" and state.get("reviewed") is True:
        label = (
            "Accepted assertion — human reviewed"
            if scope == "assertion"
            else "Related assertion accepted; record not approved"
        )
        return pill(label, "accepted")
    if status == "accepted":
        return pill("Accepted in source — human review incomplete", "incomplete")
    if status == "mixed":
        return pill("Mixed related assertion states", "mixed")
    return pill("Unreviewed", "unreviewed")


def relationship_badge(link: Mapping[str, Any]) -> str:
    if link.get("origin") == "slot":
        return pill("Authored source relationship", "authored")
    envelope = {
        "data": {
            "assertion_status": (link.get("review_state") or {}).get("status")
            if isinstance(link.get("review_state"), Mapping)
            else None
        },
        "review_state": link.get("review_state"),
    }
    return state_badge(envelope)


def id_label(oid: object) -> str:
    return f'<br><code class="id">{esc(oid)}</code>' if oid else ""


def list_names(ids: Iterable[str], records: Records) -> str:
    values = [
        f'{esc(records.name(oid))} <code class="id">{esc(oid)}</code>' for oid in ids
    ]
    return "<br>".join(values) if values else missing()


def table(caption: str, headings: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    rows = list(rows)
    if not rows:
        return f"<h3>{esc(caption)}</h3><p>{missing('No information recorded.')}</p>"
    head = "".join(f'<th scope="col">{esc(value)}</th>' for value in headings)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (
        f"<table><caption>{esc(caption)}</caption><thead><tr>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def site_header(depth: int) -> str:
    """Render the one canonical shared navigation implementation."""
    return site_nav.header(depth, "")


def _safe_party_name(oid: object, records: Records) -> str:
    envelope = records.envelope(oid)
    data = envelope.get("data") if isinstance(envelope.get("data"), Mapping) else {}
    if data.get("party_kind") == "person":
        return "human role (identity withheld)"
    return records.name(oid)


def _item_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    product_ids = intermediate.get("scope", {}).get("product_ids") or []
    product_ids = [oid for oid in product_ids if oid in members]
    product_ids.extend(
        str(row.get("id")) for row in _member_envelopes(records, "products", members)
    )
    products = [records.envelope(oid) for oid in dict.fromkeys(product_ids)]
    product_rows = []
    component_ids: list[str] = []
    for envelope in products:
        data = envelope.get("data") or {}
        component_ids.extend(refs(data, "composed_of"))
        product_rows.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                esc(data.get("description")) or missing(),
                esc(_safe_party_name(data.get("owned_by"), records))
                if data.get("owned_by")
                else missing(),
                state_badge(envelope),
            ]
        )
    component_ids.extend(
        str(row.get("id")) for row in _member_envelopes(records, "components", members)
    )
    components = [records.envelope(oid) for oid in dict.fromkeys(component_ids)]
    component_rows = [
        [
            f"<strong>{esc((row.get('data') or {}).get('name') or row.get('id'))}</strong>"
            + id_label(row.get("id")),
            esc((row.get("data") or {}).get("description")) or missing(),
            list_names(refs(row.get("data") or {}, "composed_of"), records),
            "Governed version member"
            if row.get("id") in members
            else "Referenced context; not a governed member",
            state_badge(row),
        ]
        for row in components
    ]
    return table(
        "Items in scope",
        ("Item", "Definition", "Owner", "Source review state"),
        product_rows,
    ) + table(
        "Item components and referenced context",
        ("Component", "Description", "Parts", "Scope", "Source review state"),
        component_rows,
    )


def _assets_section(records: Records, members: frozenset[str]) -> str:
    assets = []
    for envelope in _member_envelopes(records, "assets", members):
        data = envelope.get("data") or {}
        assets.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                esc(data.get("description")) or missing(),
                esc(", ".join(refs(data, "security_properties"))) or missing(),
                list_names(
                    refs(data, "processed_by") + refs(data, "stored_in"), records
                ),
                state_badge(envelope),
            ]
        )
    damage = []
    for envelope in _member_envelopes(records, "damage_scenarios", members):
        data = envelope.get("data") or {}
        damage.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                esc(data.get("description")) or missing(),
                list_names(refs(data, "damages_asset"), records),
                esc(", ".join(refs(data, "compromised_property"))) or missing(),
                state_badge(envelope),
            ]
        )
    return table(
        "Assets",
        ("Asset", "Description", "Properties", "Location", "Source review state"),
        assets,
    ) + table(
        "Damage scenarios",
        (
            "Scenario",
            "Description",
            "Affected assets",
            "Properties lost",
            "Source review state",
        ),
        damage,
    )


def _threats_section(records: Records, members: frozenset[str]) -> str:
    rows = []
    for envelope in _member_envelopes(records, "threat_instances", members):
        data = envelope.get("data") or {}
        rows.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                esc(data.get("description")) or missing(),
                list_names(refs(data, "targets_element"), records),
                esc(data.get("violates_property")) or missing(),
                list_names(refs(data, "realizes_damage"), records),
                state_badge(envelope),
            ]
        )
    return table(
        "Threat scenarios",
        (
            "Scenario",
            "Description",
            "Targets",
            "Property",
            "Damage",
            "Source review state",
        ),
        rows,
    )


def _impact_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    rows = []
    for assessment in _member_assessments(intermediate, members):
        source = records.envelope(assessment.get("source_id"))
        impact = assessment.get("impact") or {}
        stakeholder = assessment.get("for_stakeholder")
        for category in CATEGORIES:
            value = impact.get(category)
            rows.append(
                [
                    f"{esc(records.name(assessment.get('damage_scenario')))}"
                    + id_label(assessment.get("damage_scenario")),
                    esc(category.capitalize()),
                    f"<strong>{esc(value)}</strong>"
                    if value
                    else missing("Incomplete"),
                    esc(_safe_party_name(stakeholder, records))
                    if stakeholder
                    else missing(),
                    f"<code>{esc(assessment.get('source_id'))}</code>",
                    state_badge(source),
                ]
            )
    return table(
        "Impact ratings retained from the engine assessment",
        (
            "Damage scenario",
            "Category",
            "Rating",
            "Stakeholder",
            "Source",
            "Source review state",
        ),
        rows,
    )


def _paths_section(records: Records, members: frozenset[str]) -> str:
    rows = []
    for envelope in _member_envelopes(records, "attack_paths", members):
        data = envelope.get("data") or {}
        step_ids = refs(data, "steps")
        steps = (
            "<ol>"
            + "".join(
                f'<li>{esc(records.name(step))} <code class="id">{esc(step)}</code></li>'
                for step in step_ids
            )
            + "</ol>"
            if step_ids
            else missing()
        )
        rows.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                list_names(refs(data, "realizes_threat"), records),
                steps,
                state_badge(envelope),
            ]
        )
    return table(
        "Authored attack paths",
        ("Path", "Threat scenario", "Ordered steps", "Related assertion state"),
        rows,
    )


def _feasibility_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    rows = []
    for assessment in _member_assessments(intermediate, members):
        for path in assessment.get("paths") or []:
            if not isinstance(path, Mapping) or path.get("id") not in members:
                continue
            envelope = records.envelope(path.get("id"))
            data = envelope.get("data") or {}
            problems = path.get("problems") or []
            rows.append(
                [
                    f"{esc(records.name(path.get('id')))}" + id_label(path.get("id")),
                    f"<strong>{esc(path.get('feasibility'))}</strong>"
                    if path.get("feasibility")
                    else missing("Incomplete"),
                    esc(path.get("rating_source")) or missing(),
                    esc(data.get("description")) or missing(),
                    esc(", ".join(problems)) if problems else "None recorded",
                    state_badge(envelope),
                ]
            )
    return table(
        "Attack feasibility",
        (
            "Path",
            "Rating",
            "Rating source",
            "Authored rationale",
            "Problems",
            "Review state",
        ),
        rows,
    )


def _risk_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    rows = []
    matrix = intermediate["calculated_risk"].get("matrix")
    for assessment in _member_assessments(intermediate, members):
        source = records.envelope(assessment.get("source_id"))
        values = assessment.get("derived_risk") or {}
        for category in CATEGORIES:
            value = values.get(category)
            rows.append(
                [
                    f"{esc(records.name(assessment.get('threat')))}"
                    + id_label(assessment.get("threat")),
                    esc(category.capitalize()),
                    f"<strong>{esc(value)}</strong>"
                    if value is not None
                    else missing("Incomplete"),
                    esc(assessment.get("feasibility")) or missing("Incomplete"),
                    esc(matrix) or missing(),
                    f"<code>{esc(assessment.get('source_id'))}</code>",
                    state_badge(source),
                ]
            )
    return table(
        "Engine-calculated risk values",
        (
            "Threat",
            "Category",
            "Risk",
            "Feasibility",
            "Matrix",
            "Source",
            "Source review state",
        ),
        rows,
    )


def _treatment_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    risk_rows = []
    for assessment in _member_assessments(intermediate, members):
        envelope = records.envelope(assessment.get("source_id"))
        data = envelope.get("data") or {}
        authored = labeled_paragraphs(str(data.get("description") or ""))
        decision = authored.get("15.9")
        risk_rows.append(
            [
                f"{esc(records.name(assessment.get('threat')))}"
                + id_label(assessment.get("threat")),
                esc(
                    assessment.get("mitigation_status") or data.get("mitigation_status")
                )
                or missing("Incomplete"),
                (
                    esc(decision)
                    + '<br><span class="meta">Authored narrative; no structured schema field.</span>'
                    if decision
                    else missing("No authored treatment decision recorded")
                ),
                esc(authored.get("")) or missing("No other authored treatment context"),
                state_badge(envelope),
            ]
        )
    mitigation_rows = []
    for envelope in _member_envelopes(records, "mitigations", members):
        data = envelope.get("data") or {}
        mitigation_rows.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                list_names(refs(data, "mitigates"), records),
                esc(data.get("mitigation_status")) or missing(),
                list_names(refs(data, "stated_as"), records),
                state_badge(envelope),
            ]
        )
    return table(
        "Recorded treatment information",
        (
            "Threat",
            "Mitigation status",
            "Decision",
            "Authored context",
            "Source review state",
        ),
        risk_rows,
    ) + table(
        "Mitigations",
        (
            "Mitigation",
            "Threats mitigated",
            "Status",
            "Stated as",
            "Source review state",
        ),
        mitigation_rows,
    )


def _relationship_rows(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> list[list[str]]:
    rows: list[list[str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    def endpoint(oid: str) -> str:
        label = f"{esc(records.name(oid))}" + id_label(oid)
        if oid not in members:
            label += '<br><span class="meta">Referenced context; not a governed member.</span>'
        return label

    def add(subject: str, predicate: str, target: str, origin: str, badge: str) -> None:
        key = (subject, predicate, target, origin)
        if key in seen:
            return
        seen.add(key)
        rows.append(
            [
                endpoint(subject),
                esc(predicate.replace("_", " ")),
                endpoint(target),
                esc(origin),
                badge,
            ]
        )

    for envelope in _member_envelopes(records, "requirements", members):
        data = envelope.get("data") or {}
        subject = str(envelope.get("id"))
        for predicate in ("addresses", "refines", "derived_from"):
            for target in refs(data, predicate):
                add(
                    subject,
                    predicate,
                    target,
                    "source slot",
                    pill("Authored source relationship", "authored"),
                )
    for link in intermediate.get("requirement_links") or []:
        if not isinstance(link, Mapping):
            continue
        predicate = str(link.get("predicate"))
        subject = str(link.get("subject"))
        target = str(link.get("object"))
        requirement_id = target if predicate == "stated_as" else subject
        if requirement_id not in members:
            continue
        origin = str(link.get("origin"))
        assertion_id = link.get("assertion_id")
        provenance = (
            f"assertion {assertion_id}"
            if origin == "assertion" and assertion_id
            else "source slot"
            if origin == "slot"
            else origin
        )
        add(subject, predicate, target, provenance, relationship_badge(link))
    for envelope in records.all("assertions"):
        data = envelope.get("data") or {}
        if (
            data.get("predicate") == "addresses"
            and str(data.get("subject", "")) in members
        ):
            add(
                str(data.get("subject")),
                "addresses",
                str(data.get("object")),
                f"assertion {envelope.get('id')}",
                state_badge(envelope),
            )
    return rows


def _requirements_section(
    records: Records,
    intermediate: Mapping[str, Any],
    members: frozenset[str],
) -> str:
    requirements = []
    for envelope in _member_envelopes(records, "requirements", members):
        data = envelope.get("data") or {}
        requirements.append(
            [
                f"<strong>{esc(data.get('name') or envelope.get('id'))}</strong>"
                + id_label(envelope.get("id")),
                esc(data.get("text")) or missing(),
                esc(data.get("requirement_kind")) or missing(),
                esc(data.get("normativity")) or missing(),
                esc(data.get("text_origin")) or missing(),
                state_badge(envelope),
            ]
        )
    return table(
        "Security requirements",
        (
            "Requirement",
            "Text",
            "Kind",
            "Normativity",
            "Text origin",
            "Source review state",
        ),
        requirements,
    ) + table(
        "Requirement relationships",
        ("Subject", "Relationship", "Object", "Provenance", "Information state"),
        _relationship_rows(records, intermediate, members),
    )


def _assertion_touches_members(
    envelope: Mapping[str, Any], members: frozenset[str]
) -> bool:
    if envelope.get("id") in members:
        return True
    data = envelope.get("data")
    if not isinstance(data, Mapping):
        return False
    return bool(members.intersection(refs(data, "subject") + refs(data, "object")))


def _governance_section(
    governance: Mapping[str, Any],
    version: Mapping[str, Any],
    records: Records,
    approved: frozenset[str],
    freshness: Freshness,
    members: frozenset[str],
    *,
    historical: bool,
) -> str:
    parties = {
        str(p.get("id")): p
        for p in governance.get("parties") or []
        if isinstance(p, Mapping) and p.get("id")
    }
    reviews = [
        review
        for review in governance.get("reviews") or []
        if isinstance(review, Mapping) and review.get("reviews") == version.get("id")
    ]
    review_ids = {r.get("id") for r in reviews}
    reviewer_rows = []
    for review in reviews:
        party = parties.get(str(review.get("reviewer")), {})
        kind = party.get("party_kind")
        actor = (
            "AI agent"
            if kind == "software_agent"
            else "Human"
            if kind == "person"
            else str(kind or "unknown")
        )
        note = (
            "Does not count as human approval."
            if kind == "software_agent"
            else "Human review record."
        )
        if review.get("agent_model"):
            note += f" Model: {review.get('agent_model')}; run: {review.get('agent_run_id') or 'not recorded'}."
        reviewer_rows.append(
            [
                esc(
                    party_label(
                        review.get("reviewer"),
                        parties,
                        approved,
                        review.get("reviewer_role"),
                    )
                ),
                esc(review.get("reviewer_role")) or missing("No required role"),
                esc(actor),
                esc(review.get("review_outcome")) or missing(),
                esc(review.get("reviewed_at")) or missing(),
                esc(note),
            ]
        )
    comments = []
    for comment in governance.get("review_comments") or []:
        if not isinstance(comment, Mapping):
            continue
        if comment.get("comment_on") not in ({version.get("id")} | review_ids):
            continue
        comments.append(
            [
                f"{esc(comment.get('name') or comment.get('id'))}"
                + id_label(comment.get("id")),
                esc(comment.get("comment_status")) or missing(),
                esc(comment.get("description")) or missing(),
                esc(comment.get("resolved_by")) or missing("Unresolved"),
            ]
        )
    changes = []
    for item in sorted(version_records(governance), key=revision):
        changes.append(
            [
                f"v{revision(item)}" + id_label(item.get("id")),
                esc(item.get("governance_status")) or missing(),
                esc(item.get("created")) or missing(),
                esc(item.get("updated")) or missing(),
                esc(item.get("supersedes")) or "None",
                esc(item.get("description")) or missing(),
            ]
        )
    assertions = []
    for envelope in records.all("assertions"):
        if not _assertion_touches_members(envelope, members):
            continue
        data = envelope.get("data") or {}
        assertions.append(
            [
                f"{esc(data.get('name') or envelope.get('id'))}"
                + id_label(envelope.get("id")),
                esc(data.get("assertion_status")) or missing(),
                state_badge(envelope),
                list_names(refs(data, "subject"), records),
                esc(data.get("predicate")) or missing(),
                list_names(refs(data, "object"), records),
            ]
        )
    digest = (
        FRESHNESS_DETAILS_START
        + _freshness_details(freshness, historical=historical)
        + FRESHNESS_DETAILS_END
    )
    return (
        "<p><strong>An accepted review of one Assertion does not approve its endpoint record or this "
        "TARA.</strong> TARA approval is shown only from the governed version record and its required "
        "human reviews. AI reviews remain visible but never count as human approval.</p>"
        + digest
        + table(
            "Version reviewers",
            ("Reviewer", "Role", "Actor kind", "Outcome", "Date", "Approval meaning"),
            reviewer_rows,
        )
        + table(
            "Review comments", ("Comment", "Status", "Detail", "Resolution"), comments
        )
        + table(
            "Change history",
            (
                "Version",
                "Governance status",
                "Created",
                "Updated",
                "Supersedes",
                "Change",
            ),
            changes,
        )
        + table(
            "Assertion review evidence (supporting context; does not expand governed scope)",
            (
                "Assertion",
                "Source status",
                "Human review result",
                "Subject",
                "Predicate",
                "Object",
            ),
            assertions,
        )
    )


def _freshness_banner(freshness: Freshness) -> str:
    if freshness.state == "stale":
        return (
            '<div class="notice stale" role="alert"><strong>STALE TARA:</strong> the current input '
            "digest no longer matches the digest approved for this version. The approval remains an "
            "immutable historical record; use this report only with that warning.</div>"
        )
    if freshness.state == "unknown":
        return (
            '<div class="notice stale" role="alert"><strong>Freshness not verified:</strong> a recorded '
            "or current input digest is unavailable. This is not treated as a successful match.</div>"
        )
    return (
        '<div class="notice approved" role="status"><strong>Input digest matches the approved '
        "version.</strong> Governance approval applies to this recorded example version only.</div>"
    )


def _historical_freshness_banner(freshness: Freshness) -> str:
    if freshness.state == "current":
        message = "Input digest matched at publication."
        css = "approved"
    else:
        message = "Input digest match was not verified at publication."
        css = "stale"
    return (
        f'<div class="notice {css}" role="status"><strong>{message}</strong> '
        "This immutable page records publication-time status; see "
        '<a href="../latest/">latest</a> or <a href="../history.html">history</a> for '
        "current freshness.</div>"
    )


def _freshness_details(freshness: Freshness, *, historical: bool) -> str:
    if historical:
        status = (
            "matched at publication"
            if freshness.state == "current"
            else "not verified at publication"
        )
        return (
            f'<p class="meta">Approval digest: <code>{esc(freshness.recorded)}</code>; '
            f"publication input digest: <code>{esc(freshness.current)}</code>; publication status: "
            f"<strong>{esc(status)}</strong>. Current freshness is reported only by the "
            "refreshable latest and history pages.</p>"
        )
    return (
        f'<p class="meta">Approval digest: <code>{esc(freshness.recorded)}</code>; '
        f"current input digest: <code>{esc(freshness.current)}</code>; freshness: "
        f"<strong>{esc(freshness.state)}</strong>.</p>"
    )


def _replace_marked(page: str, start: str, end: str, content: str) -> str:
    before, marker, rest = page.partition(start)
    _current, end_marker, after = rest.partition(end)
    if not marker or not end_marker:
        raise RenderError(f"immutable version page has no {start} markers")
    return before + start + content + end + after


def replace_freshness(page: str, freshness: Freshness) -> str:
    """Refresh every freshness claim in a copy of an immutable version page."""
    page = _replace_marked(
        page, FRESHNESS_START, FRESHNESS_END, _freshness_banner(freshness)
    )
    return _replace_marked(
        page,
        FRESHNESS_DETAILS_START,
        FRESHNESS_DETAILS_END,
        _freshness_details(freshness, historical=False),
    )


def render_version(
    intermediate: Mapping[str, Any],
    governance: Mapping[str, Any],
    version: Mapping[str, Any],
    freshness: Freshness,
    *,
    approved: frozenset[str] = frozenset(),
) -> str:
    validate(intermediate, governance)
    records = Records(intermediate)
    members = version_members(version, records)
    number = revision(version)
    title = str(version.get("name") or f"TARA version {number}")
    sections = {
        "item": _item_section(records, intermediate, members),
        "assets": _assets_section(records, members),
        "threats": _threats_section(records, members),
        "impact": _impact_section(records, intermediate, members),
        "paths": _paths_section(records, members),
        "feasibility": _feasibility_section(records, intermediate, members),
        "risk": _risk_section(records, intermediate, members),
        "treatment": _treatment_section(records, intermediate, members),
        "requirements": _requirements_section(records, intermediate, members),
        "governance": _governance_section(
            governance,
            version,
            records,
            approved,
            freshness,
            members,
            historical=True,
        ),
    }
    toc = "".join(
        f'<li><a href="#{sid}">{esc(name)}</a></li>' for sid, name, _ in SECTIONS
    )
    body = "".join(
        f'<section id="{sid}" data-section="{index}"><h2>{index}. {esc(name)}'
        + (f' <span class="id">ISO/SAE 21434 {esc(clause)}</span>' if clause else "")
        + f"</h2>{sections[sid]}</section>"
        for index, (sid, name, clause) in enumerate(SECTIONS, 1)
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head><body>
{site_header(4)}
<div class="notice" role="note"><strong>{EXAMPLE_NOTICE}</strong> The model, reviews, ratings and governance
records shown here are examples. This page makes no compliance or real-product assessment claim.</div>
{FRESHNESS_START}{_historical_freshness_banner(freshness)}{FRESHNESS_END}
<h1>{esc(title)}</h1>
<p class="meta"><strong>TARA version v{number}</strong> · governance status:
<strong>{esc(version.get("governance_status"))}</strong> · approval status:
<strong>{esc(version.get("approval_status") or "not recorded")}</strong> · source
<code>{esc(intermediate["source"]["file"])}</code></p>
<p><a href="../history.html">Version history</a> · <a href="../latest/">Newest approved version</a></p>
<p>This static report follows the expected TARA work-product order. It paraphrases the licensed standard and
retains source identifiers, provenance, gaps, proposals and rejections from the collector.</p>
<ol class="toc">{toc}</ol>
{body}
<footer>Generated from the deterministic <code>{FORMAT}</code> intermediate and the governed record. Do not
hand-edit. Historical <code>vN/</code> pages are immutable; <code>latest/</code> and
<code>history.html</code> carry current freshness information.</footer>
</body></html>
"""


def render_history(
    governance: Mapping[str, Any],
    output_root: Path,
    freshness: Mapping[str, Freshness],
    latest: Mapping[str, Any],
) -> str:
    rows = []
    reviews = [r for r in governance.get("reviews") or [] if isinstance(r, Mapping)]
    comments = [
        c for c in governance.get("review_comments") or [] if isinstance(c, Mapping)
    ]
    for version in sorted(version_records(governance), key=revision, reverse=True):
        number = revision(version)
        approved_version = version.get("governance_status") == "approved"
        published = (
            approved_version and (output_root / f"v{number}" / "index.html").is_file()
        )
        state = freshness.get(str(version.get("id")), Freshness(None, None)).state
        version_reviews = [r for r in reviews if r.get("reviews") == version.get("id")]
        review_ids = {r.get("id") for r in version_reviews}
        open_comments = [
            str(comment.get("id"))
            for comment in comments
            if comment.get("comment_on") in ({version.get("id")} | review_ids)
            and comment.get("comment_status") == "open"
        ]
        name = (
            f'<a href="v{number}/">v{number}</a>'
            if published
            else f"v{number} (not published)"
        )
        rows.append(
            [
                name + id_label(version.get("id")),
                esc(version.get("governance_status")) or missing(),
                esc(version.get("approval_status")) or missing(),
                esc(state) if approved_version else "Not applicable",
                esc(version.get("created")) or missing(),
                esc(version.get("updated")) or missing(),
                esc(version.get("supersedes")) or "None",
                esc(", ".join(open_comments)) if open_comments else "None recorded",
                esc(version.get("description")) or missing(),
            ]
        )
    latest_number = revision(latest)
    latest_freshness = freshness[str(latest.get("id"))]
    history = table(
        "Documented versions",
        (
            "Version",
            "Governance",
            "Approval",
            "Freshness",
            "Created",
            "Updated",
            "Supersedes",
            "Open review information",
            "Change",
        ),
        rows,
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TCU TARA version history</title><style>{CSS}</style></head><body>
{site_header(3)}
<div class="notice" role="note"><strong>{EXAMPLE_NOTICE}</strong> Every version and review listed here is
example data.</div>
{_freshness_banner(latest_freshness)}
<h1>TCU TARA version history</h1>
<p>The newest approved version is <a href="latest/">v{latest_number}</a>. Draft and unapproved versions are
listed for traceability but are not linked or presented as approved publications.</p>
{history}
<footer>Generated from the governance record. Published <code>vN/</code> directories are immutable.</footer>
</body></html>
"""


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


DigestResolver = Callable[[Path, Mapping[str, Any], str], str | None]
GateResolver = Callable[
    [Path, Mapping[str, Any], Path, GateContext | None], GateDecision
]


def current_digest(
    record: Path, governance: Mapping[str, Any], version_id: str
) -> str | None:
    """Delegate to #183.  Absence is unknown, never a successful comparison."""
    try:
        from input_digest import TEMPLATE, digest
    except (ImportError, ModuleNotFoundError):
        return None
    try:
        template = frozenset(TEMPLATE)
    except TypeError:
        return None
    if not DIGEST_TEMPLATE_FILES.issubset(template):
        return None
    try:
        value = digest(record, governance, version_id)
    except (KeyError, OSError, TypeError, ValueError):
        return None
    return (
        value
        if isinstance(value, str) and re.fullmatch(r"git-tree:[0-9a-f]{40}", value)
        else None
    )


def current_gate(
    record: Path,
    governance: Mapping[str, Any],
    output_root: Path,
    context: GateContext | None,
) -> GateDecision:
    """Delegate approval exclusively to #180/#183, failing closed on absence."""
    try:
        on_disk = load_yaml(record)
    except (OSError, yaml.YAMLError, RenderError) as exc:
        return GateDecision(errors=(f"cannot validate governance record: {exc}",))
    if on_disk != governance:
        return GateDecision(
            errors=(
                (
                    "the governance document being published differs from the record "
                    "validated on disk"
                ),
            )
        )

    try:
        import check_governance
        import check_publish
    except (ImportError, ModuleNotFoundError) as exc:
        return GateDecision(
            errors=(
                (
                    "authoritative #180/#183 governance gate unavailable "
                    f"({exc.name or type(exc).__name__}); publication remains blocked"
                ),
            )
        )

    try:
        validation_errors = tuple(check_governance.check_file(record))
    except (
        AttributeError,
        OSError,
        TypeError,
        ValueError,
        yaml.YAMLError,
        SystemExit,
    ) as exc:
        detail = str(exc) or type(exc).__name__
        return GateDecision(
            errors=(f"#180 governance validation could not run: {detail}",)
        )
    if validation_errors:
        return GateDecision(
            errors=tuple(
                f"#180 governance validation: {line}" for line in validation_errors
            )
        )

    context = context or GateContext()
    if context.pr_reviews is not None and not context.head:
        return GateDecision(errors=("#183 PR reviews require the PR head commit",))
    try:
        verdicts = (
            check_publish.pr_verdicts(
                check_publish.read_reviews(context.pr_reviews),
                context.head,
                context.author,
            )
            if context.pr_reviews is not None
            else None
        )
        changed = list(context.changed)
        for version in approved_versions(governance):
            number = revision(version)
            target = output_root / f"v{number}" / "index.html"
            page = check_publish.pages_dir(record, str(number)) + "index.html"
            base_page = (
                subprocess.run(
                    ["git", "-C", str(ROOT), "show", f"{context.base}:{page}"],
                    capture_output=True,
                    check=False,
                )
                if context.base
                else None
            )
            matches_base = (
                target.is_file()
                and base_page is not None
                and base_page.returncode == 0
                and target.read_bytes() == base_page.stdout
            )
            if not matches_base and page not in changed:
                changed.append(page)
        gate = check_publish.check_record(
            record,
            governance,
            base_doc=check_publish._base_doc(record, context.base),
            verdicts=verdicts,
            changed=changed,
        )
    except (
        AttributeError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        return GateDecision(errors=(f"#183 publishing gate could not run: {exc}",))

    errors = list(gate.errors)
    notes = list(gate.notes)
    unchecked = [note for note in notes if "PR approvals not checked" in note]
    errors.extend(
        f"#183 publishing gate lacks required PR/CODEOWNER evidence: {note}"
        for note in unchecked
    )
    return GateDecision(errors=tuple(errors), notes=tuple(notes))


def publish(
    intermediate: Mapping[str, Any],
    governance: Mapping[str, Any],
    *,
    record: Path,
    output_root: Path,
    digest_resolver: DigestResolver = current_digest,
    gate_resolver: GateResolver = current_gate,
    gate_context: GateContext | None = None,
    approved: frozenset[str] = frozenset(),
    check: bool = False,
) -> PublishResult:
    validate(intermediate, governance)
    result = PublishResult()
    for version in version_records(governance):
        target = output_root / f"v{revision(version)}"
        if version.get("governance_status") != "approved" and target.exists():
            raise RenderError(
                f"unapproved version {version.get('id')} has a publication path: {target}"
            )
    versions = approved_versions(governance)
    if not versions:
        result.notes.append(
            "no approved governance version; no governed TARA was published"
        )
        return result

    decision = gate_resolver(record, governance, output_root, gate_context)
    result.notes.extend(decision.notes)
    if decision.errors:
        raise RenderError(
            "governed TARA publication blocked:\n  " + "\n  ".join(decision.errors)
        )

    freshness = {
        str(version["id"]): Freshness(
            str(version.get("approval_digest"))
            if version.get("approval_digest")
            else None,
            digest_resolver(record, governance, str(version["id"])),
        )
        for version in versions
    }
    version_pages: dict[str, str] = {}

    for version in versions:
        number = revision(version)
        target = output_root / f"v{number}" / "index.html"
        fresh = freshness[str(version["id"])]
        if target.parent.exists():
            if not target.is_file():
                raise RenderError(
                    f"immutable version directory exists without {target.name}: {target}"
                )
            version_pages[str(version["id"])] = target.read_text(encoding="utf-8")
            result.preserved.append(target)
            continue
        if fresh.state != "current":
            raise RenderError(
                f"refusing first publication of v{number}: input digest is {fresh.state}; "
                "#183 must supply a matching current digest"
            )
        content = render_version(
            intermediate, governance, version, fresh, approved=approved
        )
        if check:
            version_pages[str(version["id"])] = content
            result.out_of_date.append(target)
        else:
            target.parent.mkdir(parents=True, exist_ok=False)
            _write_atomic(target, content)
            version_pages[str(version["id"])] = content
            result.created.append(target)

    latest = versions[-1]
    latest_content = replace_freshness(
        version_pages[str(latest["id"])], freshness[str(latest["id"])]
    )
    latest_path = output_root / "latest" / "index.html"
    history_path = output_root / "history.html"

    def refresh(path: Path, content: str) -> None:
        old = path.read_text(encoding="utf-8") if path.is_file() else None
        if old == content:
            return
        if check:
            result.out_of_date.append(path)
        else:
            _write_atomic(path, content)
            result.refreshed.append(path)

    refresh(latest_path, latest_content)
    history_content = render_history(governance, output_root, freshness, latest)
    refresh(history_path, history_content)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("intermediate", type=Path, help=f"a {FORMAT} JSON file")
    parser.add_argument("--governance", type=Path, default=DEFAULT_GOVERNANCE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--pr-reviews", type=Path, help="GitHub PR reviews consumed by #183"
    )
    parser.add_argument("--head", help="PR head commit approved by reviewers")
    parser.add_argument("--author", help="PR author, whose own review cannot count")
    parser.add_argument(
        "--base", help="base ref used by #183 to identify new approvals"
    )
    parser.add_argument(
        "--changed", type=Path, help="file containing paths changed by the PR"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.pr_reviews and not args.head:
        parser.error("--pr-reviews needs --head")
    if not args.governance.is_file():
        print(
            f"render_governed_tara: governance record unavailable ({args.governance}); "
            "#180 has not merged, nothing published"
        )
        return 0
    try:
        governance = load_yaml(args.governance)
        intermediate = load_intermediate(args.intermediate)
        changed = (
            tuple(args.changed.read_text(encoding="utf-8").split())
            if args.changed
            else ()
        )
        result = publish(
            intermediate,
            governance,
            record=args.governance,
            output_root=args.output_root,
            gate_context=GateContext(
                pr_reviews=args.pr_reviews,
                head=args.head,
                author=args.author,
                base=args.base,
                changed=changed,
            ),
            approved=approved_identities(),
            check=args.check,
        )
    except (OSError, json.JSONDecodeError, RenderError, yaml.YAMLError) as exc:
        print(f"render_governed_tara: {exc}", file=sys.stderr)
        return 1
    action = "checked" if args.check else "rendered"
    print(f"render_governed_tara: {action} {args.output_root}")
    for path in result.created:
        print(f"  created immutable {path}")
    for path in result.preserved:
        print(f"  preserved immutable {path}")
    for path in result.refreshed:
        print(f"  refreshed {path}")
    for path in result.out_of_date:
        print(f"  out of date: {path}")
    for note in result.notes:
        print(f"  note: {note}")
    return 1 if result.out_of_date else 0


if __name__ == "__main__":
    raise SystemExit(main())
