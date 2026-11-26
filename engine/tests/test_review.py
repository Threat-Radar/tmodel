"""Evidence rules shared by derived model consumers, without approving objects."""

import pytest

from engine.review import assertion_review_state


@pytest.mark.parametrize(
    ("verdict", "expected"),
    [("rejected", "rejected"), (" Changes-Requested ", "changes_requested"), (None, "unreviewed")],
)
def test_incomplete_contrary_human_evidence_cannot_be_hidden_by_valid_acceptance(verdict, expected):
    assertion = {"id": "assertion:a", "assertion_status": " Accepted "}
    reviews = [
        {
            "id": "review:yes",
            "reviews": "assertion:a",
            "reviewer": "party:human",
            "review_status": " ACCEPTED ",
            "justification": "Checked source and scope.",
        },
        {
            "id": "review:contrary",
            "reviews": "assertion:a",
            "reviewer": "party:human",
            "review_status": verdict,
        },
    ]
    parties = {"party:human": {"party_kind": "person"}}
    forward = assertion_review_state(assertion, reviews, parties)
    assert forward == assertion_review_state(assertion, reversed(reviews), parties)
    assert forward["status"] == expected
    assert not forward["reviewed"]
    assert forward["assertion_status"] == " Accepted "
    assert forward["review_ids"] == ["review:contrary", "review:yes"]


def test_another_assertions_review_cannot_approve_this_assertion():
    state = assertion_review_state(
        {"id": "assertion:a", "assertion_status": "accepted"},
        [
            {
                "id": "review:other",
                "reviews": "assertion:b",
                "reviewer": "party:human",
                "review_status": "accepted",
                "justification": "Checked a different claim.",
            }
        ],
        {"party:human": {"party_kind": "person"}},
    )
    assert state["status"] == "unreviewed"
    assert not state["reviewed"]
    assert state["review_ids"] == []
