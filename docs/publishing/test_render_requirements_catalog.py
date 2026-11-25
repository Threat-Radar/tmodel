import json
import re
from pathlib import Path

import render_requirements_catalog as catalog
import yaml

EXPECTED_COUNTS = {
    "owasp-asvs-5": 34,
    "eu-cra-2024-2847": 23,
    "iec-62443-4-1-2018": 52,
}
REQUIREMENT_PROPERTIES = (
    "text",
    "description",
    "text_origin",
    "requirement_kind",
    "normativity",
    "source_ref",
    "source_locator",
    "applies_to_family",
)


def _assertions(payload: dict) -> list[dict]:
    return [
        assertion
        for source in payload["sources"]
        for edge in source["graph"]["edges"]
        for assertion in edge["assertions"]
    ]


def test_catalog_has_every_unique_requirement_and_source_count() -> None:
    payload = catalog.build_catalog()
    assert payload["schema_version"] == 1
    assert payload["count"] == 109
    assert {
        source["id"]: source["count"] for source in payload["sources"]
    } == EXPECTED_COUNTS

    requirements = [
        node
        for source in payload["sources"]
        for node in source["graph"]["nodes"]
        if node["domain_type"] == "Requirement"
    ]
    assert len(requirements) == len({row["id"] for row in requirements}) == 109
    assert all(row["properties"]["source_locator"] for row in requirements)


def test_relationship_decisions_do_not_invent_mitigations() -> None:
    payload = catalog.build_catalog()
    assertions = _assertions(payload)
    assert len(assertions) == 46
    assert sum(item["assertion_status"] == "accepted" for item in assertions) == 24
    assert (
        sum(
            any(review["review_status"] == "rejected" for review in item["reviews"])
            for item in assertions
        )
        == 3
    )
    assert (
        sum(
            item["assertion_status"] == "proposed" and not item["reviews"]
            for item in assertions
        )
        == 19
    )

    predicates = {
        edge["relationship_type"]
        for source in payload["sources"]
        for edge in source["graph"]["edges"]
    }
    assert "satisfied_by" not in predicates
    assert "stated_as" not in predicates


def test_catalog_preserves_authoritative_requirements_assertions_and_reviews() -> None:
    payload = catalog.build_catalog()
    all_requirement_ids: list[str] = []

    for source in payload["sources"]:
        authoritative = yaml.safe_load(
            (catalog.RESEARCH / source["graph"]["file"]).read_text()
        )
        graph = source["graph"]
        requirements = {
            node["id"]: node
            for node in graph["nodes"]
            if node["domain_type"] == "Requirement"
        }
        expected_requirements = {
            requirement["id"]: requirement
            for requirement in authoritative["requirements"]
        }
        assert requirements.keys() == expected_requirements.keys()
        all_requirement_ids.extend(requirements)

        for requirement_id, expected in expected_requirements.items():
            actual = requirements[requirement_id]
            assert actual["label"] == expected["name"]
            for field in REQUIREMENT_PROPERTIES:
                assert actual["properties"].get(field) == expected.get(field)

        assertions = {
            assertion["id"]: assertion
            for edge in graph["edges"]
            for assertion in edge["assertions"]
        }
        expected_assertions = {
            assertion["id"]: assertion
            for assertion in authoritative.get("assertions", [])
        }
        assert assertions.keys() == expected_assertions.keys()
        for assertion_id, expected in expected_assertions.items():
            actual = assertions[assertion_id]
            assert actual["assertion_status"] == expected["assertion_status"]
            assert actual["confidence"] == expected.get("confidence")
            assert actual["description"] == expected.get("description")
            assert actual["evidence"] == expected.get("evidence", [])
            edges = [
                edge
                for edge in graph["edges"]
                if any(item["id"] == assertion_id for item in edge["assertions"])
            ]
            assert len(edges) == 1
            assert (
                edges[0]["source"],
                edges[0]["relationship_type"],
                edges[0]["target"],
            ) == (expected["subject"], expected["predicate"], expected["object"])

        reviews = {
            review["id"]: review
            for assertion in assertions.values()
            for review in assertion["reviews"]
        }
        expected_reviews = {
            review["id"]: review for review in authoritative.get("reviews", [])
        }
        assert reviews.keys() == expected_reviews.keys()
        identities = {
            identity
            for party in authoritative.get("parties", [])
            if party.get("party_kind") == "person"
            for identity in (
                party["id"],
                party["id"].removeprefix("party:"),
                party.get("name", ""),
            )
            if identity
        }
        for review_id, expected in expected_reviews.items():
            actual = reviews[review_id]
            justification = expected["justification"]
            for identity in sorted(identities, key=len, reverse=True):
                justification = re.sub(
                    re.escape(identity),
                    "the human reviewer",
                    justification,
                    flags=re.IGNORECASE,
                )
            assert actual["review_status"] == expected["review_status"]
            assert actual["justification"] == justification
            assert actual["reviewer"].startswith(catalog.PUBLIC_REVIEWER_PREFIX)
            assert actual["reviewer"] != expected["reviewer"]

    assert len(all_requirement_ids) == len(set(all_requirement_ids)) == 109


def test_catalog_is_deterministic_current_and_public_safe(tmp_path: Path) -> None:
    first = catalog.render()
    second = catalog.render()
    assert first == second
    assert catalog.check() == 0
    assert json.loads(first)["count"] == 109
    assert "kriishnaa-18" not in first.casefold()
    assert str(catalog.ROOT) not in first

    copy = tmp_path / "catalog.json"
    copy.write_text(first)
    assert copy.read_bytes() == catalog.OUT.read_bytes()
