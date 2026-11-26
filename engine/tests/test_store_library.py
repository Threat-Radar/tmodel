"""The library in the working store (#65): node ids, which links become edges, rebuilds.

These pin the three answers agreed on #65 for the library loader (#142).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.load.library import Citation, Library, LibraryRecord, load_library
from engine.store import Node, Store
from engine.store import library as store_library
from engine.store.library import GRAPH, split_source_ref

FIXTURES = Path(__file__).parent / "fixtures" / "library"


def record(id: str, **fields) -> LibraryRecord:
    return LibraryRecord(
        id=id,
        body="other",
        type="spec",
        title=id,
        status="stub",
        path=f"records/other/{id}/record.yaml",
        **fields,
    )


def library(*records: LibraryRecord, digest: str = "d1") -> Library:
    return Library(root="/lib", records=tuple(sorted(records, key=lambda r: r.id)), digest=digest)


def edges(store: Store) -> list[tuple[str, str, str, tuple[str, ...]]]:
    return [(e.source, e.type, e.target, e.properties["stated_by"]) for e in store.edges()]


def test_records_become_library_nodes():
    store = Store()
    loaded = load_library(FIXTURES)
    result = store_library.load_library(store, loaded)
    assert result.graph == GRAPH and result.rebuilt is True and result.digest == loaded.digest
    assert result.nodes == len(loaded) == 12
    assert store.graphs() == (GRAPH,)
    assert [n.id for n in store.nodes()] == [f"library:{r.id}" for r in loaded]

    node = store.node("library:rfc-8785", GRAPH)
    assert node.type == "LibraryRecord"
    fields = loaded.get("rfc-8785").to_dict()
    del fields["relations"], fields["cites"]
    expected = Node("x", "T", fields).properties  # lists come back as tuples, None left out
    assert {k: v for k, v in node.properties.items() if k != "cites"} == expected


def test_inverse_links_are_one_forward_edge():
    """4 of 12 `supersedes` links on main are recorded on one side only; the graph can't tell."""
    one_side = library(
        record("v2", relations=(("supersedes", ("v1",)),)),
        record("v1"),
        record("u2"),
        record("u1", relations=(("updated_by", ("u2",)),)),
    )
    both_sides = library(
        record("v2", relations=(("supersedes", ("v1",)),)),
        record("v1", relations=(("superseded_by", ("v2",)),)),
        record("u2", relations=(("updates", ("u1",)),)),
        record("u1", relations=(("updated_by", ("u2",)),)),
    )
    a, b = Store(), Store()
    store_library.load_library(a, one_side)
    store_library.load_library(b, both_sides)
    facts = lambda s: [(e.id, e.source, e.type, e.target) for e in s.edges()]  # noqa: E731
    assert (
        facts(a)
        == facts(b)
        == [
            (a.edges()[0].id, "library:u2", "updates", "library:u1"),
            (a.edges()[1].id, "library:v2", "supersedes", "library:v1"),
        ]
    )
    assert edges(b) == [
        ("library:u2", "updates", "library:u1", ("u1", "u2")),
        ("library:v2", "supersedes", "library:v1", ("v1", "v2")),
    ]


def test_cites_naming_a_record_are_edges_and_the_rest_stay_data():
    lib = library(
        record(
            "a",
            cites=(
                Citation(record="b"),
                Citation(record="b"),  # said twice, one fact
                Citation(ref="[3]", title="Not held", url="https://example.org/x", locator="p. 4"),
            ),
        ),
        record("b", relations=(("cited_by", ("a",)), ("see_also", ("a",)), ("part_of", ("c",)))),
        record("c", relations=(("implements_concept", ("a",)), ("contradicts", ("b",)))),
    )
    store = Store()
    store_library.load_library(store, lib)
    assert edges(store) == [
        ("library:a", "cites", "library:b", ("a", "b")),
        ("library:b", "part_of", "library:c", ("b",)),
        ("library:b", "see_also", "library:a", ("b",)),
        ("library:c", "contradicts", "library:b", ("c",)),
        ("library:c", "implements_concept", "library:a", ("c",)),
    ]
    assert store.node("library:a", GRAPH).properties["cites"] == (
        {"ref": "[3]", "title": "Not held", "url": "https://example.org/x", "locator": "p. 4"},
    )


def test_links_to_records_not_held_are_listed_not_invented():
    lib = library(
        record("a", relations=(("see_also", ("gone",)), ("superseded_by", ("later",)))),
        record("b", cites=(Citation(record="nowhere"),)),
    )
    store = Store()
    result = store_library.load_library(store, lib)
    assert result.missing == (
        "a: see_also -> gone",
        "a: superseded_by -> later",
        "b: cites -> nowhere",
    )
    assert store.edges() == ()
    assert [n.id for n in store.nodes()] == ["library:a", "library:b"]


def test_fixture_links_point_outside_the_fixture():
    """The fixture is 12 records cut from a whole library, so its links are all reported."""
    result = store_library.load_library(Store(), load_library(FIXTURES))
    assert result.edges == 0
    assert "ecma-424: see_also -> cyclonedx-1-7" in result.missing
    assert "eo-14306: updates -> eo-14144" in result.missing


def test_loading_the_library_twice_gives_the_same_store():
    """#142's test: load the fixture library twice and get the same store."""
    once, twice = Store(), Store()
    store_library.load_library(once, load_library(FIXTURES))
    store_library.load_library(twice, load_library(FIXTURES))
    again = store_library.load_library(twice, load_library(FIXTURES))
    assert again.rebuilt is False
    assert (once.graphs(), once.nodes(), once.edges()) == (
        twice.graphs(),
        twice.nodes(),
        twice.edges(),
    )
    assert once.digest(GRAPH) == load_library(FIXTURES).digest


def test_a_changed_library_is_reloaded_whole():
    store = Store()
    store_library.load_library(store, library(record("a"), record("b"), digest="d1"))
    result = store_library.load_library(store, library(record("a"), digest="d2"))
    assert result.rebuilt is True
    assert [n.id for n in store.nodes()] == ["library:a"]


@pytest.mark.parametrize(
    ("ref", "expected"),
    [
        ("library:iso-sae-21434-2021#RQ-09-09", ("library:iso-sae-21434-2021", "RQ-09-09")),
        ("library:rfc-8785", ("library:rfc-8785", None)),
        ("library:rfc-8785#", ("library:rfc-8785", None)),
    ],
)
def test_a_source_ref_fragment_is_a_locator_not_a_node(ref, expected):
    assert split_source_ref(ref) == expected
