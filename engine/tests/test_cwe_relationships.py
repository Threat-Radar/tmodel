"""CWE's relationships, each in its view (#145): all kept, any list of views, inverses derived.

Runs on the CWE sample (`fixtures/cwe/`, 12 entries copied verbatim from CWE 4.20). The
relationships it writes are read here a second time with ElementTree alone, with no
engine code, and compared with what the reader keeps. Set TMODEL_CWE_FULL to MITRE's
cwec_v4.20.xml.zip to check the whole release too: 1,602 weakness relationships and
5,024 memberships, the counts on #61.
"""

import io
import os
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import pytest

from engine.load import cwe
from engine.load.cwe import Relationship

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cwe"
SAMPLE = FIXTURES / "cwec_v4.20-sample.xml"
SAMPLE_SHA256 = "e26b565b22747a93e88a999f24d1578299e53d6669011bb9c015e690fef26b43"
FULL_SHA256 = "3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50"
NS = "{http://cwe.mitre.org/cwe-7}"
CONTAINERS = (
    ("Weaknesses", "Related_Weaknesses"),
    ("Categories", "Relationships"),
    ("Views", "Members"),
)
MEMBERSHIP = {"Has_Member": "HasMember", "Member_Of": "MemberOf"}


@pytest.fixture(scope="module")
def catalog():
    return cwe.load_catalog(SAMPLE, SAMPLE_SHA256)


def _written(root):
    """Every relationship in the XML, as the reader should keep it, read with ElementTree alone."""
    found = []
    for container, field in CONTAINERS:
        entries = root.find(NS + container)
        for entry in entries if entries is not None else ():
            for holder in entry.findall(NS + field):
                for child in holder:
                    tag = child.tag.removeprefix(NS)
                    nature = child.get("Nature") if tag == "Related_Weakness" else MEMBERSHIP[tag]
                    chain = child.get("Chain_ID")
                    found.append(
                        (
                            f"CWE-{entry.get('ID')}",
                            nature,
                            f"CWE-{child.get('CWE_ID')}",
                            int(child.get("View_ID")),
                            child.get("Ordinal"),
                            f"CWE-{chain}" if chain else None,
                        )
                    )
    return found


def _tuples(relationships):
    return [(r.source, r.nature, r.target, r.view, r.ordinal, r.chain) for r in relationships]


def _edited(tmp_path, old, new):
    """The sample with one change, read without its digest."""
    text = SAMPLE.read_text(encoding="utf-8")
    assert text.count(old) == 1, old
    changed = tmp_path / "cwe.xml"
    changed.write_text(text.replace(old, new), encoding="utf-8")
    return cwe.load_catalog(changed)


# --- every relationship kept, in its view -------------------------------------------------


def test_every_relationship_the_sample_writes_is_kept_once_in_file_order(catalog):
    written = _written(ElementTree.parse(SAMPLE).getroot())
    assert _tuples(catalog.stated_relationships) == written
    assert len(written) == 20  # 11 between weaknesses, 9 memberships
    assert all(not r.derived for r in catalog.stated_relationships)
    entry = catalog.get("CWE-689")
    assert _tuples(entry.relationships) == [w for w in written if w[0] == "CWE-689"]


def test_an_entry_in_two_views_gets_an_edge_tagged_with_each(catalog):
    xss = catalog.relationships(entry="CWE-79", derived=False)
    parents = [r for r in xss if r.nature == "ChildOf"]
    assert [(r.target, r.view, r.ordinal) for r in parents] == [
        ("CWE-74", 1000, "Primary"),
        ("CWE-74", 1003, "Primary"),
    ]
    assert [r.to_dict()["view"] for r in parents] == ["CWE-1000", "CWE-1003"]
    assert [(r.nature, r.target) for r in xss if r.nature != "ChildOf"] == [
        ("CanPrecede", "CWE-494"),
        ("PeerOf", "CWE-352"),
    ]


def test_a_chain_and_a_membership_keep_what_cwe_writes(catalog):
    chain = catalog.relationships(views=[709], derived=False)
    assert _tuples(chain) == [("CWE-692", "StartsWith", "CWE-184", 709, None, "CWE-692")]
    members = catalog.relationships(entry="CWE-411", derived=False)
    assert {r.nature for r in members} == {"HasMember"} and len(members) == 8
    assert {r.view for r in members} == {699}


@pytest.mark.parametrize(
    "views, expected",
    [
        ([1000], 17),
        ([1000, 1003, 709], 20),
        ([1000, 1003, 709, 699], 36),
    ],
    ids=["one view", "three views", "four views"],
)
def test_the_importer_takes_one_three_or_four_views(catalog, views, expected):
    found = catalog.relationships(views)
    assert len(found) == expected
    assert {r.view for r in found} == set(views)
    assert found == [r for r in catalog.relationships() if r.view in views]


def test_a_view_is_named_by_id_by_number_or_in_a_list(catalog):
    one = catalog.relationships([1000])
    assert catalog.relationships("CWE-1000") == catalog.relationships(["1000"]) == one
    assert catalog.relationships("cwe-1000, 1003") == catalog.relationships([1000, 1003])


@pytest.mark.parametrize(
    "views, message",
    [
        ("CWE-4242", "not a view this catalog knows: CWE-4242"),
        ([1000, 4242, 4243], "not a view this catalog knows: CWE-4242, CWE-4243"),
        ("Research Concepts", "a view id looks like CWE-1000, not 'Research Concepts'"),
        ("1000,", "a view id looks like CWE-1000, not ''"),
        ([], "name at least one view"),
    ],
)
def test_an_unknown_or_malformed_view_is_refused(catalog, views, message):
    with pytest.raises(ValueError, match=message):
        catalog.relationships(views)


# --- the inverses the schema declares --------------------------------------------------


def test_the_inverses_the_schema_declares_are_derived(catalog):
    stated = catalog.stated_relationships
    derived = [r for r in catalog.relationships() if r.derived]
    expected = [
        (r.target, cwe.INVERSE[r.nature], r.source, r.view)
        for r in stated
        if r.nature in cwe.INVERSE
    ]
    assert [(r.source, r.nature, r.target, r.view) for r in derived] == expected
    assert len(derived) == 18
    assert all(r.ordinal is None and r.chain is None for r in derived)
    assert {r.nature for r in derived} == {"ParentOf", "CanFollow", "RequiredBy", "MemberOf"}
    for inverse in [
        ("CWE-74", "ParentOf", "CWE-79", 1000),
        ("CWE-74", "ParentOf", "CWE-79", 1003),
        ("CWE-494", "CanFollow", "CWE-79", 1000),
        ("CWE-362", "RequiredBy", "CWE-689", 1000),
        ("CWE-412", "MemberOf", "CWE-411", 699),
        ("CWE-79", "MemberOf", "CWE-811", 809),
    ]:
        assert inverse in expected


def test_peerof_canalsobe_and_startswith_have_no_inverse():
    # CanAlsoBe "is not necessarily reciprocal" (L973); PeerOf and StartsWith name none.
    stated = [
        Relationship("CWE-1", nature, "CWE-2", 1000) for nature in ("PeerOf", "CanAlsoBe")
    ] + [Relationship("CWE-3", "StartsWith", "CWE-4", 709, chain="CWE-3")]
    assert cwe.with_inverses(stated) == tuple(stated)


def test_an_inverse_cwe_writes_itself_is_not_derived_again():
    child = Relationship("CWE-1", "ChildOf", "CWE-2", 1000, ordinal="Primary")
    parent = Relationship("CWE-2", "ParentOf", "CWE-1", 1000)
    assert cwe.with_inverses([child, parent]) == (child, parent)
    twice = cwe.with_inverses([child, child])
    assert twice[2:] == (Relationship("CWE-2", "ParentOf", "CWE-1", 1000, derived=True),)


def test_an_entrys_relationships_include_the_inverses_of_those_that_name_it(catalog):
    xss = catalog.relationships(entry="CWE-79")
    assert [(r.nature, r.target, r.view) for r in xss if r.derived] == [
        ("MemberOf", "CWE-811", 809)
    ]
    # CWE-74 is not in the sample, but the relationships that name it still give its side
    assert [(r.nature, r.target, r.view) for r in catalog.relationships(entry="CWE-74")] == [
        ("ParentOf", "CWE-79", 1000),
        ("ParentOf", "CWE-79", 1003),
    ]
    assert catalog.relationships(entry=79) == catalog.relationships(entry="cwe-79") == xss


def test_stated_only_leaves_the_inverses_out(catalog):
    assert catalog.relationships(derived=False) == list(catalog.stated_relationships)


# --- what the report counts and lists --------------------------------------------------


def test_the_report_counts_and_lists_each_departure(catalog):
    report = catalog.relationship_report()
    assert (report["stated"], report["derived"]) == (20, 18)
    assert report["natures"] == {
        "ChildOf": 6,
        "StartsWith": 1,
        "CanPrecede": 1,
        "Requires": 2,
        "PeerOf": 1,
        "HasMember": 9,
    }
    assert report["derived_natures"] == {
        "ParentOf": 6,
        "CanFollow": 1,
        "RequiredBy": 2,
        "MemberOf": 9,
    }
    assert report["views"] == {
        "CWE-699": 8,
        "CWE-709": 1,
        "CWE-809": 1,
        "CWE-1000": 9,
        "CWE-1003": 1,
    }
    # the sample holds only view CWE-709, and few of the entries its relationships name
    assert report["views_not_read"] == {"CWE-699": 8, "CWE-809": 1, "CWE-1000": 9, "CWE-1003": 1}
    assert len(report["targets_not_read"]) == 18
    assert all(catalog.get(r["target"]) is None for r in report["targets_not_read"])
    # 4.20 gives the named chains' StartsWith a Chain_ID, which L540 ties to CanPrecede
    assert report["chain_departures"] == [
        {
            "source": "CWE-692",
            "nature": "StartsWith",
            "target": "CWE-184",
            "view": "CWE-709",
            "ordinal": None,
            "chain": "CWE-692",
            "derived": False,
        }
    ]
    assert report["ordinal_departures"] == report["primary_repeated"] == []
    assert report["undeclared_natures"] == []


def test_an_ordinal_on_another_nature_is_reported_not_refused(tmp_path):
    catalog = _edited(
        tmp_path,
        '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>',
        '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000" Ordinal="Primary"/>',
    )
    departures = catalog.relationship_report()["ordinal_departures"]
    assert [(d["source"], d["nature"], d["target"]) for d in departures] == [
        ("CWE-79", "PeerOf", "CWE-352")
    ]


def test_two_primaries_of_one_nature_in_one_view_are_reported(tmp_path):
    catalog = _edited(
        tmp_path,
        '<Related_Weakness Nature="CanPrecede" CWE_ID="494" View_ID="1000"/>',
        '<Related_Weakness Nature="ChildOf" CWE_ID="494" View_ID="1000" Ordinal="Primary"/>',
    )
    assert catalog.relationship_report()["primary_repeated"] == [
        {"source": "CWE-79", "nature": "ChildOf", "view": "CWE-1000", "times": 2}
    ]


def test_a_nature_the_schema_does_not_declare_is_kept_without_an_inverse(tmp_path):
    # CWE 4.21 (schema 7.4) writes Overlaps, which schema 7.3 does not declare
    catalog = _edited(
        tmp_path,
        '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>',
        '<Related_Weakness Nature="Overlaps" CWE_ID="352" View_ID="1000"/>',
    )
    overlaps = [r for r in catalog.relationships() if r.nature == "Overlaps"]
    assert _tuples(overlaps) == [("CWE-79", "Overlaps", "CWE-352", 1000, None, None)]
    report = catalog.relationship_report()
    assert [r["nature"] for r in report["undeclared_natures"]] == ["Overlaps"]
    assert report["natures"]["Overlaps"] == 1 and "Overlaps" not in report["derived_natures"]


def test_membership_whose_element_names_interleave_is_read_in_order(tmp_path):
    catalog = _edited(
        tmp_path,
        '<Has_Member CWE_ID="413" View_ID="699"/>',
        '<Member_Of CWE_ID="1400" View_ID="1400"/><Has_Member CWE_ID="413" View_ID="699"/>',
    )
    written = catalog.relationships(entry="CWE-411", derived=False)
    assert [(r.nature, r.target) for r in written[:3]] == [
        ("HasMember", "CWE-412"),
        ("MemberOf", "CWE-1400"),
        ("HasMember", "CWE-413"),
    ]
    assert len(written) == 9
    inverse = catalog.relationships(views=[1400], entry="CWE-1400")
    assert [(r.nature, r.target, r.derived) for r in inverse] == [("HasMember", "CWE-411", True)]


def test_an_unknown_element_among_relationships_is_kept_and_reported(tmp_path):
    catalog = _edited(
        tmp_path,
        '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>',
        '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>'
        '<Related_Future CWE_ID="1" View_ID="1000"/>',
    )
    assert catalog.unknown == (("Weakness/Related_Weaknesses/Related_Future", 1),)
    held = catalog.get("CWE-79").fields["Related_Weaknesses"][0]["Related_Future"]
    assert held == ({"@CWE_ID": "1", "@View_ID": "1000"},)
    assert len(catalog.stated_relationships) == 20  # not read as a relationship
    assert catalog.report()[-1]["field"] == "Related_Weaknesses/Related_Future"


@pytest.mark.parametrize(
    "attributes, message",
    [
        ('Nature="PeerOf" CWE_ID="x" View_ID="1000"', "needs a whole-number CWE_ID and View_ID"),
        ('Nature="PeerOf" CWE_ID="352"', "needs a whole-number CWE_ID and View_ID"),
        ('CWE_ID="352" View_ID="1000"', "has a Related_Weakness with no Nature"),
    ],
)
def test_a_relationship_cwe_could_not_have_written_is_refused(tmp_path, attributes, message):
    with pytest.raises(cwe.CweError, match=message):
        _edited(
            tmp_path,
            '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>',
            f"<Related_Weakness {attributes}/>",
        )


# --- entries --------------------------------------------------------------------------------


def test_entries_say_where_they_come_from_and_what_they_write(catalog):
    xss = catalog.get("CWE-79")
    assert (xss.source, xss.object_id) == ("mitre-cwe", "weakness:cwe-79")
    assert catalog.get("CWE-411").object_id is None  # categories are not objects
    as_dict = xss.to_dict()
    assert as_dict["source"] == "mitre-cwe"
    assert as_dict["relationships"] == [r.to_dict() for r in xss.relationships]
    assert as_dict["relationships"][0] == {
        "source": "CWE-79",
        "nature": "ChildOf",
        "target": "CWE-74",
        "view": "CWE-1000",
        "ordinal": "Primary",
        "chain": None,
        "derived": False,
    }


def test_the_objects_still_hold_no_relationship(catalog):
    # the accepted core has no Weakness-to-Weakness edge, so none becomes an Assertion
    predicates = Counter(a["predicate"] for a in catalog.objects["assertions"])
    assert set(predicates) == {"exploited_by", "instance_of"}


# --- the whole 4.20 release -------------------------------------------------------------


@pytest.mark.skipif(not os.environ.get("TMODEL_CWE_FULL"), reason="TMODEL_CWE_FULL not set")
def test_the_whole_420_release_keeps_every_relationship():
    path = Path(os.environ["TMODEL_CWE_FULL"])
    catalog = cwe.load_catalog(path, FULL_SHA256)
    with zipfile.ZipFile(io.BytesIO(path.read_bytes())) as archive:
        root = ElementTree.fromstring(archive.read(archive.namelist()[0]))
    assert _tuples(catalog.stated_relationships) == _written(root)
    report = catalog.relationship_report()
    assert (report["stated"], report["derived"]) == (6626, 6498)
    assert report["natures"] == {
        "ChildOf": 1318,
        "StartsWith": 3,
        "CanPrecede": 143,
        "Requires": 13,
        "CanAlsoBe": 27,
        "PeerOf": 98,
        "HasMember": 5024,
    }
    assert report["derived_natures"] == {
        "ParentOf": 1318,
        "CanFollow": 143,
        "RequiredBy": 13,
        "MemberOf": 5024,
    }
    assert len(report["views"]) == 41
    # the design notes' figures: 27 Primary ordinals off ChildOf, 3 Chain_IDs on StartsWith
    assert (len(report["ordinal_departures"]), len(report["chain_departures"])) == (27, 3)
    assert report["primary_repeated"] == report["targets_not_read"] == []
    assert report["views_not_read"] == {} and report["undeclared_natures"] == []
    members = Counter(catalog.get(r.source).kind for r in catalog.stated_relationships)
    assert members == {"Weakness": 1602, "Category": 4260, "View": 764}
