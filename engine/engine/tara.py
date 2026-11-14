"""Read-only TARA intermediate for the render phase (#181, DL-0027).

This is a derived export, not a canonical model or a governed approval record.
Keep source records and every review; compute risk with the existing calculator.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from engine.graph import GraphError
from engine.model_graph import COLLECTION_DOMAIN_TYPES, project_model_graph
from engine.risk import assess_document

FORMAT = "tmodel.tara-collection/v1"


def collect_document(doc: Mapping[str, Any], *, matrix: str) -> dict[str, Any]:
    """Collect the entire model without promoting, hiding or rewriting proposals.

    Record review summaries refer to related Assertions, not approval of the
    endpoint object or the TARA. Only recorded person reviews can count toward
    an accepted assertion; contrary human reviews are never lost by list order.
    """
    project_model_graph(doc)
    records = {
        name: sorted(doc.get(name) or [], key=lambda record: record["id"])
        for name in COLLECTION_DOMAIN_TYPES
    }
    if not records["products"]:
        raise GraphError("tara: expected a threat model with at least one Product")
    evidence = _Evidence(records)
    risk = assess_document(doc, matrix=matrix)
    scores = {r["id"]: r for r in records["risk_scores"]}
    threats = {r["id"]: r for r in records["threat_instances"]}
    for assessment in risk["assessments"]:
        source = scores.get(assessment["id"])
        collection = "risk_scores" if source is not None else "threat_instances"
        source = source if source is not None else threats[assessment["threat"]]
        assessment["source_id"] = source["id"]
        assessment["review_state"] = evidence.for_record(source, collection)
    return {
        "format": FORMAT,
        "notice": "Draft collection, not an approved TARA. Collection does not accept proposals.",
        "scope": {"kind": "whole_model", "product_ids": [r["id"] for r in records["products"]]},
        "records": {
            name: [
                {
                    "id": record["id"],
                    "type": domain_type,
                    "data": _json_value(record),
                    "review_state": evidence.for_record(record, name),
                }
                for record in records[name]
            ]
            for name, domain_type in COLLECTION_DOMAIN_TYPES.items()
        },
        "requirement_links": _requirement_links(records, evidence),
        "calculated_risk": risk,
    }


def serialize(payload: Mapping[str, Any]) -> str:
    """One portable UTF-8 JSON document, with no clock or machine-local metadata."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n"


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return {key: _json_value(item) for key, item in value.items()}
    raise GraphError("tara: model records must contain JSON-compatible values")


def _status(value: Any) -> str:
    return re.sub(r"[\s-]+", "_", value.strip().lower()) if isinstance(value, str) else ""


class _Evidence:
    def __init__(self, records: Mapping[str, list[Mapping[str, Any]]]) -> None:
        self.assertions = records["assertions"]
        self.reviews = records["reviews"]
        self.parties = {party["id"]: party for party in records["parties"]}

    def assertion(self, assertion: Mapping[str, Any]) -> dict[str, Any]:
        if assertion.get("assertion_status") is not None and not isinstance(
            assertion["assertion_status"], str
        ):
            raise GraphError(f"{assertion['id']}: assertion_status must be a string")
        reviews = [r for r in self.reviews if r.get("reviews") == assertion["id"]]
        human = [
            r
            for r in reviews
            if isinstance(r.get("reviewer"), str)
            and self.parties.get(r["reviewer"], {}).get("party_kind") == "person"
        ]
        verdicts = {_status(r.get("review_status")) for r in human}
        recorded = _status(assertion.get("assertion_status"))
        if "rejected" in verdicts:
            state = "rejected"
        elif "changes_requested" in verdicts:
            state = "changes_requested"
        elif recorded == "accepted" and verdicts == {"accepted"}:
            state = "accepted"
        elif recorded in {"proposed", "rejected", "changes_requested"}:
            state = recorded
        else:
            state = "unreviewed"
        return {
            "id": assertion["id"],
            "assertion_status": assertion.get("assertion_status"),
            "status": state,
            "reviewed": state == "accepted",
            "review_ids": [r["id"] for r in reviews],
            "human_review_ids": [r["id"] for r in human],
        }

    def summarize(self, assertions: list[Mapping[str, Any]], *, scope: str) -> dict[str, Any]:
        states = [self.assertion(a) for a in assertions]
        statuses = {s["status"] for s in states}
        status = (
            next(iter(statuses)) if len(statuses) == 1 else "mixed" if statuses else "unreviewed"
        )
        return {
            "scope": scope,
            "status": status,
            "reviewed": bool(states) and all(s["reviewed"] for s in states),
            "assertion_ids": [s["id"] for s in states],
            "review_ids": sorted({rid for s in states for rid in s["review_ids"]}),
            "assertions": states,
        }

    def for_record(self, record: Mapping[str, Any], collection: str) -> dict[str, Any]:
        if collection == "assertions":
            return self.summarize([record], scope="assertion")
        if collection == "reviews":
            assertions = [a for a in self.assertions if a["id"] == record.get("reviews")]
            return self.summarize(assertions, scope="target_assertion")
        assertions = [
            a for a in self.assertions if record["id"] in (a.get("subject"), a.get("object"))
        ]
        return self.summarize(assertions, scope="related_assertions")


def _references(record: Mapping[str, Any], slot: str) -> list[str]:
    value = record.get(slot, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise GraphError(f"{record['id']}: {slot} must be a list of ids")
    return sorted(set(value))


def _requirement_links(
    records: Mapping[str, list[Mapping[str, Any]]], evidence: _Evidence
) -> list[dict[str, Any]]:
    """Keep slot and assertion links distinct, including unaccepted proposals."""
    requirements = {r["id"] for r in records["requirements"]}
    mitigations = {r["id"] for r in records["mitigations"]}
    links = []

    def append(subject: str, predicate: str, target: str, assertion: Mapping | None = None) -> None:
        if predicate == "stated_as":
            valid = subject in mitigations and target in requirements
        else:
            valid = subject in requirements and target in mitigations
        if not valid:
            raise GraphError(f"{subject}: {predicate} must link a Mitigation and a Requirement")
        links.append(
            {
                "subject": subject,
                "predicate": predicate,
                "object": target,
                "origin": "assertion" if assertion else "slot",
                "assertion_id": assertion["id"] if assertion else None,
                "review_state": evidence.summarize(
                    [assertion] if assertion else [],
                    scope="assertion" if assertion else "authored_slot",
                ),
            }
        )

    for mitigation in records["mitigations"]:
        for target in _references(mitigation, "stated_as"):
            append(mitigation["id"], "stated_as", target)
    for requirement in records["requirements"]:
        for target in _references(requirement, "satisfied_by"):
            append(requirement["id"], "satisfied_by", target)
    for assertion in records["assertions"]:
        if assertion.get("predicate") in {"stated_as", "satisfied_by"}:
            append(assertion["subject"], assertion["predicate"], assertion["object"], assertion)
    return sorted(
        links,
        key=lambda link: (
            link["subject"],
            link["predicate"],
            link["object"],
            link["assertion_id"] or "",
        ),
    )
