"""Read-only approved/current-TARA criterion for the DL-0027 governance pilot.

Gate, governed-version reviews and both evidence routes remain DEC-001b proposals.
The caller must name the evidence route being exercised; no route is selected here.
This result neither decides a Gate nor verifies a product's conformance or safety.
"""

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from engine.graph import GraphError

EVIDENCE_LINKS = ("direct", "evidence-chain")
ROLES = {"owner", "assessor", "approver"}
DIGEST = re.compile(r"git-tree:[0-9a-f]{40}\Z")


def _index(doc: Mapping[str, Any], collection: str) -> dict[str, Mapping[str, Any]]:
    rows = doc.get(collection) or []
    if not isinstance(rows, list):
        raise GraphError(f"{collection}: expected a list")
    result = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("id"), str) or not row["id"]:
            raise GraphError(f"{collection}: each item needs an id")
        if row["id"] in result:
            raise GraphError(f"{row['id']}: duplicate id")
        result[row["id"]] = row
    return result


def _refs(row: Mapping[str, Any], slot: str) -> list[str]:
    value = row.get(slot, [])
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        raise GraphError(f"{row.get('id', '?')}: {slot} needs ids")
    return value


def _time(review: Mapping[str, Any]) -> datetime:
    value = review.get("reviewed_at")
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise GraphError(f"{review['id']}: reviewed_at needs a timestamp") from exc
    if parsed.tzinfo is None:
        raise GraphError(f"{review['id']}: reviewed_at needs a timezone")
    return parsed


def evaluate(
    gate: Mapping[str, Any],
    doc: Mapping[str, Any],
    *,
    current_digest: str,
    evidence_link: str,
) -> dict[str, Any]:
    """Evaluate the TARA approval/freshness criterion over validated proposal mappings.

    `current_digest` is recomputed by the file adapter using #183's input_digest;
    it is not taken from the version's approval_digest. Inputs are never changed.
    A history renderer can display this DTO without recomputing approval policy.
    """
    if evidence_link not in EVIDENCE_LINKS:
        raise GraphError("choose an explicit evidence_link: direct or evidence-chain")
    if not isinstance(current_digest, str) or not DIGEST.fullmatch(current_digest):
        raise GraphError("current_digest must be a recomputed git-tree digest")
    if not isinstance(gate.get("id"), str) or not gate["id"]:
        raise GraphError("gate needs an id")
    models = _index(doc, "threat_models")
    target = gate.get("validates_conformance_of")
    if not isinstance(target, str) or target not in models:
        raise GraphError("validates_conformance_of must name a ThreatModel in the record")
    version = models[target]
    if not str(version.get("revision", "")).isdigit():
        raise GraphError("ThreatModel revision must be a whole number")
    criteria = sorted(set(_refs(gate, "gated_by")))
    if not criteria:
        raise GraphError("gate needs a gated_by Requirement")
    requirements = _index(doc, "requirements")
    parties = _index(doc, "parties")
    reviews = _index(doc, "reviews")
    comments = _index(doc, "review_comments")
    practices = _index(doc, "sdl_practices")
    evidence = _index(doc, "evidence_items")
    seen = {gate["id"]}
    for collection in (models, requirements, parties, reviews, comments, practices, evidence):
        if seen & collection.keys():
            raise GraphError("ids must be unique across the gate and governance record")
        seen.update(collection)
    reasons = []
    paths = []
    for rid in criteria:
        if rid not in requirements:
            raise GraphError(f"{rid}: no such gated_by Requirement")
        found = []
        if evidence_link == "direct":
            if target in _refs(requirements[rid], "evidenced_by"):
                found.append([rid, target])
        else:
            for pid, practice in sorted(practices.items()):
                if rid not in _refs(practice, "implements"):
                    continue
                for eid in sorted(set(_refs(practice, "produces"))):
                    if eid not in evidence:
                        raise GraphError(f"{pid}: produces unknown Evidence {eid}")
                    item = evidence[eid]
                    if (
                        item.get("evidence_kind") == "model"
                        and item.get("evidence_of") == target
                        and str(item.get("about_version")) == str(version.get("revision"))
                    ):
                        found.append([rid, pid, eid, target])
        if not found:
            reasons.append(f"{rid}: no {evidence_link} evidence path to this version")
        paths.extend(found)

    mine = [r for r in reviews.values() if r.get("reviews") == target]
    people = [r for r in mine if parties.get(r.get("reviewer"), {}).get("party_kind") == "person"]
    roles = _refs(version, "required_review_roles")
    if not roles or not set(roles) <= ROLES or "approver" not in roles:
        reasons.append("version must require human roles including an approver")
    latest_ids: dict[str, list[str]] = {}
    for role in sorted(set(roles)):
        matching = [r for r in people if r.get("reviewer_role") == role]
        if not matching:
            reasons.append(f"no {role} approval by a person")
            continue
        newest = max(_time(r) for r in matching)
        latest = [r for r in matching if _time(r) == newest]
        latest_ids[role] = sorted(r["id"] for r in latest)
        # Equal-time contrary verdicts cannot be resolved by list order.
        if any(r.get("review_outcome") != "approved" for r in latest):
            reasons.append(f"latest {role} review is not unanimously approved")
    approvals = _refs(version, "approved_by")
    if not approvals or not set(approvals) & set(latest_ids.get("approver", [])):
        reasons.append("approved_by must include the current human approver's review")
    for rid in sorted(set(approvals)):
        if not any(r["id"] == rid and r.get("review_outcome") == "approved" for r in people):
            reasons.append(f"{rid}: approved_by is not a person's approval of this version")
    if (
        version.get("governance_status") != "approved"
        or version.get("approval_status") != "approved"
    ):
        reasons.append("version is not recorded as approved in both status fields")
    on_version = {target} | {r["id"] for r in mine}
    for cid, comment in sorted(comments.items()):
        if comment.get("comment_status") not in {"open", "resolved", "rejected"}:
            raise GraphError(f"{cid}: invalid comment_status")
        if comment.get("comment_on") in on_version and comment.get("comment_status") == "open":
            reasons.append(f"{cid}: review comment is open")
    pinned = version.get("approval_digest")
    digest_valid = isinstance(pinned, str) and bool(DIGEST.fullmatch(pinned))
    stale = digest_valid and pinned != current_digest
    if not digest_valid:
        reasons.append("version has no valid approval digest")
    elif stale:
        reasons.append("inputs changed after approval")
    return {
        "gate": gate["id"],
        "threat_model": target,
        "revision": str(version.get("revision", "")),
        "status": "failed" if reasons else "passed",
        "stale": stale,
        "approval_digest": pinned,
        "current_digest": current_digest,
        "evidence_link": evidence_link,
        "evidence_paths": sorted(paths),
        "latest_person_reviews": latest_ids,
        "reasons": reasons,
        "scope": "pilot-recorded-tara-exit-criterion",
        "interpretation": (
            "Pilot proposal: checks recorded TARA approval, evidence linkage and input freshness. "
            "Does not approve a Gate, verify adequacy, or decide product conformance."
        ),
    }
