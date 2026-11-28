"""Read-only ADR-0012 requirement coverage over a storage-neutral model document."""

from collections.abc import Mapping
from typing import Any

from engine.graph import GraphError
from engine.model_graph import COLLECTION_DOMAIN_TYPES, project_model_graph
from engine.review import assertion_review_state, normalize_status

# Typed traversal only: dependencies and generic requirement derivation do not confer scope.
LINKS = {
    "composed_of": ({"Product", "Component"}, {"Component"}),
    "uses_component": ({"Component"}, {"Component"}),
    "build_composed_of": ({"ProductInstance"}, {"Component"}),
    "of_product": ({"ProductInstance"}, {"Product"}),
    "applies_to": ({"Requirement"}, {"Product", "ProductInstance", "Component"}),
    "satisfied_by": ({"Requirement"}, {"Mitigation"}),
    "addresses": ({"Requirement"}, {"ThreatInstance", "Weakness", "AttackPattern"}),
}


def _refs(record: Mapping[str, Any], slot: str) -> list[str]:
    value = record.get(slot, [])
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise GraphError(f"{record['id']}: {slot} must be a string or list of strings")
    return value


def collect(doc: Mapping[str, Any], product: str) -> dict[str, Any]:
    """Slot values plus unanimously human-accepted Assertions; proposals stay hypothetical.

    This reports recorded mitigation status, not verified compliance or threat validity.
    All ThreatInstances in the supplied model are checked, including hypotheses.
    """
    project_model_graph(doc)  # validate collections, identity and existing reference slots
    records = {
        raw["id"]: (kind, raw)
        for collection, kind in COLLECTION_DOMAIN_TYPES.items()
        for raw in (doc.get(collection) or [])
    }
    if product not in records or records[product][0] != "Product":
        raise GraphError(f"unknown product: {product}")
    edges: set[tuple[str, str, str]] = set()

    def edge(subject: str, predicate: str, target: str) -> tuple[str, str, str]:
        sources, targets = LINKS[predicate]
        if (
            subject not in records
            or target not in records
            or records[subject][0] not in sources
            or records[target][0] not in targets
        ):
            raise GraphError(f"invalid {predicate} relationship: {subject} -> {target}")
        return subject, predicate, target

    for rid, (kind, raw) in records.items():
        for predicate, (sources, _targets) in LINKS.items():
            if kind in sources:
                edges.update(edge(rid, predicate, target) for target in _refs(raw, predicate))
        if kind == "Mitigation" and raw.get("mitigation_status") is not None:
            if not isinstance(raw["mitigation_status"], str):
                raise GraphError(f"{rid}: mitigation_status must be a string")
        if kind in {"Product", "Requirement"}:
            _refs(raw, "classifications" if kind == "Product" else "applies_to_family")

    assertions = doc.get("assertions") or []
    reviews = doc.get("reviews") or []
    parties = {party["id"]: party for party in doc.get("parties") or []}

    def verdicts(assertion: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        return [r for r in reviews if r.get("reviews") == assertion["id"]]

    def accepted(assertion: Mapping[str, Any]) -> bool:
        return assertion_review_state(assertion, reviews, parties)["reviewed"]

    pending = []
    excluded = []
    for assertion in sorted(assertions, key=lambda a: a["id"]):
        predicate = assertion["predicate"]
        if predicate not in LINKS:
            continue
        triple = edge(assertion["subject"], predicate, assertion["object"])
        if accepted(assertion):
            edges.add(triple)
        elif normalize_status(assertion.get("assertion_status")) == "proposed":
            pending.append((assertion, triple))
        else:
            excluded.append(assertion["id"])

    def answer(relations: set[tuple[str, str, str]]) -> dict[str, Any]:
        def targets(subject: str, predicate: str) -> set[str]:
            return {t for s, p, t in relations if s == subject and p == predicate}

        scope = {product} | {s for s, p, t in relations if p == "of_product" and t == product}
        todo = list(scope)
        while todo:
            current = todo.pop()
            children = set().union(
                *(
                    targets(current, p)
                    for p in ("composed_of", "uses_component", "build_composed_of")
                )
            )
            for child in children - scope:
                scope.add(child)
                todo.append(child)
        families = set(_refs(records[product][1], "classifications"))
        rows = []
        addressed = set()
        for rid, (kind, raw) in sorted(records.items()):
            if kind != "Requirement":
                continue
            concrete = targets(rid, "applies_to") & scope
            family = set(_refs(raw, "applies_to_family")) & families
            if not concrete and not family:
                continue
            mitigations = [
                {"id": mid, "status": records[mid][1].get("mitigation_status")}
                for mid in sorted(targets(rid, "satisfied_by"))
            ]
            statuses = {m["status"] for m in mitigations}
            status = (
                "satisfied"
                if "complete" in statuses
                else "in_progress"
                if "in_progress" in statuses
                else "unsatisfied"
            )
            threats = targets(rid, "addresses") & {
                t for t, (k, _) in records.items() if k == "ThreatInstance"
            }
            addressed.update(threats)
            rows.append(
                {
                    "id": rid,
                    "name": raw.get("name", rid),
                    "status": status,
                    "scope": {"applies_to": sorted(concrete), "families": sorted(family)},
                    "mitigations": mitigations,
                    "addressed_threats": sorted(threats),
                }
            )
        threats = {rid for rid, (kind, _) in records.items() if kind == "ThreatInstance"}
        return {
            "requirements": rows,
            "count": len(rows),
            "counts": {
                s: sum(r["status"] == s for r in rows)
                for s in ("satisfied", "in_progress", "unsatisfied")
            },
            "scope": sorted(scope),
            "unaddressed_threats": sorted(threats - addressed),
        }

    baseline = answer(edges)
    hypothetical = edges | {triple for _, triple in pending}
    joint = answer(hypothetical)
    proposals = []
    for assertion, triple in pending:
        individual = answer(edges | {triple})
        # Also surface links whose effect depends on another proposed scope/link.
        others = edges | {t for _a, t in pending if t != triple}
        if individual == baseline and answer(others) == joint:
            continue
        proposals.append(
            {
                "id": assertion["id"],
                "subject": triple[0],
                "predicate": triple[1],
                "object": triple[2],
                "assertion_status": "proposed",
                "review_ids": sorted(r["id"] for r in verdicts(assertion)),
                "effect": "individual" if individual != baseline else "with_other_proposals",
                "if_accepted": individual,
            }
        )
    return {
        "product": product,
        **baseline,
        "proposed_assertions": proposals,
        "if_all_proposed_accepted": joint,
        "excluded_assertions": excluded,
        "interpretation": "Recorded requirement coverage; not verified compliance. "
        "Threat gaps include every ThreatInstance in this model, including hypotheses.",
    }
