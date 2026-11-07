#!/usr/bin/env python3
"""Tests for the PROC-0002 review rules in render_sdl.governance() (DL-0042).

    python3 -B docs/publishing/test_render_sdl.py      (CI: schema.yml)
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_sdl as r  # noqa: E402

DOC = r.load(r.ROOT / "spec" / "vectors" / "sdl-01-tmodel-desktop.yaml")
ENTRY = next(e for e in r.load(r.MANIFEST)["pages"] if e["src"].endswith("sdl-01-tmodel-desktop.yaml"))
XWALK = r.load(r.MAP_0001)
TARGET = "assertion:select-ssdf"


def with_review(reviewer="party:nymble", status="accepted", assertion_status="accepted", **extra):
    doc = copy.deepcopy(DOC)
    for a in doc["assertions"]:
        if a["id"] == TARGET:
            a["assertion_status"] = assertion_status
    doc["reviews"] = [dict(id="review:t", name="t", reviews=TARGET, reviewer=reviewer,
                           review_status=status, **extra)]
    return doc


def fails(doc, needle):
    try:
        r.collect(doc, ENTRY, XWALK)
    except r.SdlError as exc:
        assert needle in str(exc), f"expected {needle!r} in {exc}"
        return
    raise AssertionError(f"expected a review-rule failure mentioning {needle!r}")


def test_example_is_all_proposals():
    data = r.collect(DOC, ENTRY, XWALK)
    assert data["awaiting_review"], "the example has no Reviews, so every selection waits"
    assert all(a["predicate"] in r.SELECTION_PREDICATES for a in data["awaiting_review"])


def test_human_accept_is_shown():
    data = r.collect(with_review(justification="SSDF is the hub."), ENTRY, XWALK)
    ssdf = next(s for s in data["sets"] if s["id"] == "requirement-set:ssdf-1-1")
    assert ssdf["decision"]["state"] == "accepted"
    assert TARGET not in {a["id"] for a in data["awaiting_review"]}


def test_ai_agent_cannot_decide():
    fails(with_review(reviewer="party:drafting-agent"), "not a person")


def test_decided_without_review():
    doc = copy.deepcopy(DOC)
    next(a for a in doc["assertions"] if a["id"] == TARGET)["assertion_status"] = "accepted"
    fails(doc, "with no Review")


def test_rejection_needs_justification():
    fails(with_review(status="rejected", assertion_status="rejected"), "needs a justification")


def test_status_must_match_review():
    fails(with_review(assertion_status="proposed"), "set both")


def test_unknown_verdict():
    fails(with_review(status="approved"), "is not one of")


def test_reviewer_role_required():
    fails(with_review(reviewer="party:phaskell"), "has none of the roles")


def test_changes_requested_still_waits():
    data = r.collect(with_review(status="changes_requested", assertion_status="proposed",
                                 justification="Name the profile."), ENTRY, XWALK)
    assert TARGET in {a["id"] for a in data["awaiting_review"]}


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"test_render_sdl: {len(tests)} passed")
