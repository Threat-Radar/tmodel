"""Recorded human evidence for an Assertion, independent of storage or export.

This summarizes existing reviews; it never authenticates a reviewer, changes
an Assertion or approves an endpoint object or document version.
"""

import re
from collections.abc import Iterable, Mapping
from typing import Any

from engine.graph import GraphError


def _status(value: Any) -> str:
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
    verdicts = {_status(review.get("review_status")) for review in human}
    justified = all(
        isinstance(review.get("justification"), str) and bool(review["justification"].strip())
        for review in human
    )
    recorded = _status(assertion.get("assertion_status"))
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
