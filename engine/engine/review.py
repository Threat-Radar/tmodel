"""Recorded human evidence for an Assertion, independent of storage or export.

This summarizes existing reviews; it never authenticates a reviewer, changes
an Assertion or approves an endpoint object or document version.
"""

import re
from collections.abc import Iterable, Mapping
from typing import Any

from engine.graph import GraphError


def normalize_status(value: Any) -> str:
    """Normalize recorded status spelling without changing the authored value."""
    return re.sub(r"[\s-]+", "_", value.strip().lower()) if isinstance(value, str) else ""


def assertion_review_state(
    assertion: Mapping[str, Any],
    reviews: Iterable[Mapping[str, Any]],
    parties: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Require an accepted Assertion and unanimous, justified person acceptance.

    All reviews remain visible. Non-person reviews neither grant nor veto human
    acceptance. Contrary person verdicts take precedence even without a rationale;
    missing or blank justifications cannot establish acceptance.
    """
    if assertion.get("assertion_status") is not None and not isinstance(
        assertion["assertion_status"], str
    ):
        raise GraphError(f"{assertion['id']}: assertion_status must be a string")
    matching = sorted(
        (review for review in reviews if review.get("reviews") == assertion["id"]),
        key=lambda review: review["id"],
    )
    human = [
        review
        for review in matching
        if isinstance(review.get("reviewer"), str)
        and parties.get(review["reviewer"], {}).get("party_kind") == "person"
    ]
    verdicts = {normalize_status(review.get("review_status")) for review in human}
    justified = all(
        isinstance(review.get("justification"), str) and bool(review["justification"].strip())
        for review in human
    )
    recorded = normalize_status(assertion.get("assertion_status"))
    if "rejected" in verdicts:
        state = "rejected"
    elif "changes_requested" in verdicts:
        state = "changes_requested"
    elif recorded == "accepted" and verdicts == {"accepted"} and justified:
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
        "review_ids": [review["id"] for review in matching],
        "human_review_ids": [review["id"] for review in human],
    }


def relationship_review_states(
    doc: Mapping[str, Any],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Summarize exact statements, keeping all matching human verdicts significant.

    Callers validate the model collections first. One accepted duplicate Assertion
    cannot conceal a contrary human verdict on the same subject/predicate/object.
    An unrelated statement or an agent's verdict cannot lend human acceptance.
    """
    reviews = doc.get("reviews") or []
    parties = {party["id"]: party for party in doc.get("parties") or []}
    groups: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for assertion in doc.get("assertions") or []:
        key = tuple(assertion.get(name) for name in ("subject", "predicate", "object"))
        if all(isinstance(value, str) for value in key):
            groups.setdefault(key, []).append(assertion)
    result = {}
    for key, assertions in groups.items():
        ids = {assertion["id"] for assertion in assertions}
        matching = [
            review
            for review in reviews
            if isinstance(review.get("reviews"), str)
            and review.get("reviews") in ids
            and isinstance(review.get("reviewer"), str)
            and parties.get(review.get("reviewer"), {}).get("party_kind") == "person"
        ]
        verdicts = {normalize_status(review.get("review_status")) for review in matching}
        if "rejected" in verdicts:
            verdict = "rejected"
        elif "changes_requested" in verdicts:
            verdict = "changes_requested"
        else:
            verdict = next(iter(verdicts)) if len(verdicts) == 1 else "mixed" if verdicts else None
        recorded = {normalize_status(assertion.get("assertion_status")) for assertion in assertions}
        status = (
            "accepted"
            if "accepted" in recorded
            else next(iter(recorded))
            if len(recorded) == 1
            else "mixed"
        )
        accepted = any(assertion_review_state(a, reviews, parties)["reviewed"] for a in assertions)
        justified = all(
            isinstance(review.get("justification"), str) and bool(review["justification"].strip())
            for review in matching
        )
        result[key] = {
            "assertion_status": status or None,
            "review_status": verdict or None,
            "reviewed": accepted and verdicts == {"accepted"} and justified,
        }
    return result
