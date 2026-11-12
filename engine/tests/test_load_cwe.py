"""The CWE reader and its objects (#144): every field kept, the extraction's values found.

Runs on `fixtures/cwe/cwec_v4.20-sample.xml`, 13 entries the library copied verbatim
from CWE 4.20, and compares them with what the library's extraction says an importer
must find (`fixtures/cwe/expected.json`, from its examples/expected.yaml). Set
TMODEL_CWE_FULL to MITRE's cwec_v4.20.xml.zip to check the whole release against the
extraction's catalog-stats.yaml as well.
"""

import io
import json
import os
import zipfile
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from xml.etree import ElementTree

import pytest

from engine.load import cwe

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cwe"
SAMPLE = FIXTURES / "cwec_v4.20-sample.xml"
SAMPLE_SHA256 = "e26b565b22747a93e88a999f24d1578299e53d6669011bb9c015e690fef26b43"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
EXPECTED_ENTRIES = [e for fixture in EXPECTED.values() for e in fixture["entries"]]
# Values the extraction derives by reading the text, not fields an importer reads.
DERIVED = {
    "kind",
    "id",
    "cwe_ids_named_in_prose",
    "successor_machine_readable",
    "m2_mapping_decision",
    "modification_dates_ascending",
}
FULL_SHA256 = "3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50"
SAMPLE_NUMBERS = [1093, 1174, 1187, 373, 689, 692, 710, 769, 79]  # in file order


@pytest.fixture(scope="module")
def catalog():
    return cwe.load_catalog(SAMPLE, SAMPLE_SHA256)


# --- reading the sample ----------------------------------------------------------------


def test_sample_loads_with_its_pinned_digest(catalog):
    assert (catalog.name, catalog.version, catalog.date) == ("CWE", "4.20", "2026-04-30")
    assert (catalog.schema, catalog.file, catalog.sha256) == (
        "7.3",
        "cwec_v4.20-sample.xml",
        SAMPLE_SHA256,
    )
    assert [w.number for w in catalog.weaknesses] == SAMPLE_NUMBERS
    assert [c.id for c in catalog.categories] == ["CWE-411", "CWE-811"]
    assert [v.id for v in catalog.views] == ["CWE-709"]
    assert [r["@Reference_ID"] for r in catalog.references] == ["REF-7", "REF-44", "REF-726"]
    assert catalog.unknown == ()


def test_get_takes_any_spelling_of_an_id(catalog):
    assert catalog.get("CWE-79") is catalog.get("cwe-79") is catalog.get("79") is catalog.get(79)
    assert catalog.get("CWE-411").kind == "Category"
    assert catalog.get("CWE-99999") is None and catalog.get("not an id") is None


@pytest.mark.parametrize(
    "expected",
    EXPECTED_ENTRIES,
    ids=[f"{e['kind']}-{e.get('id', e.get('reference_id'))}" for e in EXPECTED_ENTRIES],
)
def test_every_entry_has_the_values_the_extraction_names(catalog, expected):
    if expected["kind"] == "External_Reference":
        fields = next(
            r for r in catalog.references if r["@Reference_ID"] == expected["reference_id"]
        )
    else:
        fields = catalog.get(expected["id"]).fields
    found = _read(expected["kind"], fields)
    for key, value in expected.items():
        if key not in DERIVED:
            assert _like(found[key], value) == value, key


def test_typed_fields_agree_with_the_entry(catalog):
    xss = catalog.get("CWE-79")
    assert (xss.abstraction, xss.structure, xss.status, xss.usage) == (
        "Base",
        "Simple",
        "Stable",
        "Allowed",
    )
    assert xss.description.startswith("The product does not neutralize or incorrectly")
    assert "XSS" in xss.alternate_terms
    assert xss.attack_patterns == tuple(f"CAPEC-{n}" for n in (209, 588, 591, 592, 63, 85))
    assert len(xss.observed_examples) == 20 and xss.mitigations == 12
    first = xss.observed_examples[0]
    assert first.reference.startswith("CVE-") and first.link.startswith("https://")
    assert xss.url == "https://cwe.mitre.org/data/definitions/79.html"
    view = catalog.get("CWE-709")
    assert (view.view_type, view.description) == (
        "Implicit",
        "This view displays Named Chains and their components.",
    )


# --- nothing lost ------------------------------------------------------------------------


def test_every_element_attribute_and_word_is_kept(catalog):
    root = ElementTree.parse(SAMPLE).getroot()
    entries = [e for container in root for e in container]
    kept = [
        *(c.fields for c in (*catalog.weaknesses, *catalog.categories, *catalog.views)),
        *catalog.references,
    ]
    by_key = {_key(f): f for f in kept}
    assert len(by_key) == len(entries)
    for element in entries:
        fields = by_key[(element.get("ID") or element.get("Reference_ID"))]
        assert _tally(fields) == _source_tally(element), element.get("ID")


def test_a_reference_cited_twice_is_kept_twice(catalog):
    cited = catalog.get("CWE-79").fields["References"][0]["Reference"]
    sections = [r.get("@Section", "") for r in cited if r["@External_Reference_ID"] == "REF-44"]
    assert [s.split(":")[0] for s in sections] == ['"Sin 2', '"Sin 3']


def test_interleaved_children_keep_their_order(catalog):
    root = ElementTree.parse(SAMPLE).getroot()
    source = next(w for w in root.iter(f"{{{cwe.CWE_NS}}}Weakness") if w.get("ID") == "79")
    example = next(source.iter(f"{{{cwe.CWE_NS}}}Demonstrative_Example"))
    kept = catalog.get("CWE-79").fields["Demonstrative_Examples"][0]["Demonstrative_Example"][0]
    assert [next(iter(item)) for item in kept["#items"]] == [
        child.tag.rpartition("}")[2] for child in example
    ]


def test_structured_text_keeps_its_markup(catalog):
    extended = catalog.get("CWE-79").fields["Extended_Description"][0]["#xhtml"]
    assert extended.startswith("<p>There are many variants of cross-site scripting")
    assert "xhtml:" not in extended and "xmlns" not in extended


def test_plain_text_is_never_read_as_markup():
    assert cwe.plain_text("if x < y and y > z") == "if x < y and y > z"
    assert cwe.plain_text({"#xhtml": "<p>if x &lt; y</p><p>and y &gt; z</p>"}) == (
        "if x < y and y > z"
    )
    assert cwe.plain_text({"@Date": "2008-04-11", "#text": "  Old  name "}) == "Old name"


def test_an_unknown_field_is_kept_and_reported(tmp_path):
    changed = tmp_path / "cwe.xml"
    text = SAMPLE.read_text(encoding="utf-8")
    changed.write_text(
        text.replace("<Mapping_Notes>", "<Future_Field>soon</Future_Field><Mapping_Notes>", 1),
        encoding="utf-8",
    )
    catalog = cwe.load_catalog(changed)
    assert catalog.unknown == (("Weakness/Future_Field", 1),)
    assert catalog.get("CWE-1093").fields["Future_Field"] == ("soon",)
    row = catalog.report()[-1]
    assert row == {
        "kind": "Weakness",
        "field": "Future_Field",
        "entries": 1,
        "maps_to": None,
        "known": False,
    }


def test_the_report_names_every_entry_field_and_where_it_goes(catalog):
    rows = catalog.report()
    assert len(rows) == sum(len(names) for names in cwe.ENTRY_FIELDS.values())
    by = {(r["kind"], r["field"]): r for r in rows}
    assert by[("Weakness", "Description")] == {
        "kind": "Weakness",
        "field": "Description",
        "entries": 9,
        "maps_to": "Weakness.description",
        "known": True,
    }
    assert by[("Weakness", "Potential_Mitigations")]["maps_to"] is None  # kept on the entry
    assert by[("External_Reference", "Author")]["entries"] == 3


def test_links_name_what_is_not_mapped(catalog):
    links = catalog.links()
    assert links["attack_pattern_links"] == 13
    assert links["observed_examples"] == 28
    assert links["observed_examples_without_cve_id"] == []
    assert links["attack_pattern_links_repeated"] == links["observed_examples_repeated"] == []


# --- refusing what is not the pinned catalog ------------------------------------------------


def test_other_bytes_than_the_pinned_ones_are_refused():
    with pytest.raises(cwe.CweError, match=f"SHA-256 {SAMPLE_SHA256} is not the 0+ the library"):
        cwe.load_catalog(SAMPLE, "0" * 64)


def test_the_zip_mitre_publishes_is_read(tmp_path):
    archive = tmp_path / "cwec_v4.20.xml.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(SAMPLE, "cwec_v4.20.xml")
    catalog = cwe.load_catalog(archive)
    assert catalog.file == "cwec_v4.20.xml.zip" and len(catalog.weaknesses) == 9


@pytest.mark.parametrize(
    "members, message",
    [((), "found nothing"), (("a.xml", "b.xml"), "found a.xml, b.xml"), (("a.txt",), "a.txt")],
)
def test_a_zip_must_hold_one_xml_file(tmp_path, members, message):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for name in members:
            z.writestr(name, SAMPLE.read_bytes())
    archive = tmp_path / "bad.zip"
    archive.write_bytes(buffer.getvalue() if members else b"PK\x03\x04 not a zip")
    with pytest.raises(cwe.CweError, match=message if members else "not a readable zip"):
        cwe.load_catalog(archive)


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda t: t.replace("?>", "?><!DOCTYPE x [<!ENTITY a 'b'>]>", 1), "DOCTYPE"),
        (lambda t: t.replace("cwe.mitre.org/cwe-7", "cwe.mitre.org/cwe-8", 1), "Schema 7"),
        (lambda t: "<root/>", "no Weakness_Catalog"),
        (lambda t: t[: len(t) // 2], "not well-formed"),
        (lambda t: t.replace('ID="1187"', 'ID="411"', 1), "both a Weakness and a Category"),
        (lambda t: t.replace('ID="1187" ', "", 1), "no whole-number ID"),
    ],
)
def test_what_is_not_a_cwe_schema_7_catalog_is_refused(tmp_path, change, message):
    bad = tmp_path / "bad.xml"
    bad.write_text(change(SAMPLE.read_text(encoding="utf-8")), encoding="utf-8")
    with pytest.raises(cwe.CweError, match=message):
        cwe.load_catalog(bad)


def test_cached_catalog_reloads_only_when_the_bytes_change(tmp_path):
    copy = tmp_path / "cwe.xml"
    copy.write_bytes(SAMPLE.read_bytes())
    first = cwe.cached_catalog(copy, SAMPLE_SHA256)
    assert cwe.cached_catalog(copy, SAMPLE_SHA256.upper()) is first
    copy.write_bytes(SAMPLE.read_bytes().replace(b"Improper Neutral", b"Improper neutral", 1))
    with pytest.raises(cwe.CweError, match="is not the"):
        cwe.cached_catalog(copy, SAMPLE_SHA256)


def test_configured_catalog_reads_the_variable(monkeypatch):
    monkeypatch.delenv(cwe.CATALOG_ENV, raising=False)
    assert cwe.configured_catalog() is None
    monkeypatch.setenv(cwe.CATALOG_ENV, "  ")
    assert cwe.configured_catalog() is None
    monkeypatch.setenv(cwe.CATALOG_ENV, str(SAMPLE))
    assert cwe.configured_catalog() == SAMPLE


# --- objects in the tmodel object model ------------------------------------------------


def test_one_weakness_object_per_cwe_weakness(catalog):
    objects = cwe.to_objects(catalog)
    assert [w["id"] for w in objects["weaknesses"]] == [f"weakness:cwe-{n}" for n in SAMPLE_NUMBERS]
    xss = next(w for w in objects["weaknesses"] if w["catalog_ref"] == "CWE-79")
    assert xss == {
        "id": "weakness:cwe-79",
        "name": catalog.get("CWE-79").name,
        "description": catalog.get("CWE-79").description,
        "catalog_ref": "CWE-79",
    }


def test_capec_and_cve_links_become_proposed_assertions(catalog):
    objects = cwe.to_objects(catalog, [79])
    statements = objects["assertions"]
    exploited = [a for a in statements if a["predicate"] == "exploited_by"]
    assert [a["object"] for a in exploited] == [
        f"attack-pattern:capec-{n}" for n in (209, 588, 591, 592, 63, 85)
    ]
    assert [p["catalog_ref"] for p in objects["attack_patterns"]] == [
        f"CAPEC-{n}" for n in (63, 85, 209, 588, 591, 592)
    ]
    instances = [a for a in statements if a["predicate"] == "instance_of"]
    assert len(instances) == len(objects["vulnerabilities"]) == 20
    for statement in statements:
        assert statement["assertion_status"] == "proposed"
        assert statement["asserted_by"] == cwe.MITRE_PARTY
        assert "SHA-256 " + SAMPLE_SHA256 in statement["generated_by"]
    example = catalog.get("CWE-79").observed_examples[0]
    first = instances[0]
    assert first["subject"] == f"vulnerability:{example.reference.lower()}"
    assert first["object"] == "weakness:cwe-79"
    assert (first["description"], first["evidence"]) == (example.description, [example.link])


def test_every_reference_resolves_inside_the_objects(catalog):
    objects = cwe.to_objects(catalog)
    ids = {o["id"] for items in objects.values() for o in items}
    assert len(ids) == sum(len(items) for items in objects.values())  # ids are unique
    for statement in objects["assertions"]:
        assert {statement["subject"], statement["object"], statement["asserted_by"]} <= ids
    assert objects["parties"] == [
        {"id": "party:mitre-cwe", "name": "MITRE CWE Program", "party_kind": "organization"}
    ]


# --- the whole release, when MITRE's file is at hand --------------------------------------------


@pytest.mark.skipif(not os.environ.get("TMODEL_CWE_FULL"), reason="TMODEL_CWE_FULL not set")
def test_the_whole_420_release_matches_the_extraction():
    full = cwe.load_catalog(os.environ["TMODEL_CWE_FULL"], FULL_SHA256)
    assert (full.version, full.schema, full.unknown) == ("4.20", "7.3", ())
    counts = (len(full.weaknesses), len(full.categories), len(full.views), len(full.references))
    assert counts == (969, 422, 59, 1026)  # catalog-stats.yaml: counts
    assert Counter(w.status for w in full.weaknesses) == {
        "Incomplete": 486,
        "Draft": 432,
        "Stable": 26,
        "Deprecated": 25,
    }
    assert Counter(w.usage for w in full.weaknesses) == {
        "Allowed": 749,
        "Allowed-with-Review": 93,
        "Prohibited": 83,
        "Discouraged": 44,
    }
    history = {"Weakness": full.weaknesses, "Category": full.categories, "View": full.views}
    for kind, (modifications, submissions, names) in {
        "Weakness": (14707, 969, 774),
        "Category": (1677, 422, 134),
        "View": (191, 59, 17),
    }.items():
        found = Counter()
        for entry in history[kind]:
            for name, values in entry.fields["Content_History"][0].items():
                found[name] += len(values)
        assert (found["Modification"], found["Submission"], found["Previous_Entry_Name"]) == (
            modifications,
            submissions,
            names,
        )
    links = full.links()
    assert (links["attack_pattern_links"], links["observed_examples"]) == (1212, 3134)


# --- helpers -----------------------------------------------------------------------------------


def _one(fields, name):
    values = fields.get(name, ()) if isinstance(fields, Mapping) else ()
    return values[0] if values else None


def _all(fields, *path):
    found = [fields]
    for name in path:
        found = [
            value
            for holder in found
            if isinstance(holder, Mapping)
            for value in (_children(holder, name))
        ]
    return found


def _children(holder, name):
    if "#items" in holder:
        return [item[name] for item in holder["#items"] if name in item]
    return holder.get(name, ())


def _pairs(holder):
    """(name, value) for each child of a mapping, in file order."""
    if "#items" in holder:
        return [next(iter(item.items())) for item in holder["#items"]]
    return [(k, v) for k, values in holder.items() if not k.startswith(("@", "#")) for v in values]


def _text(value):
    return cwe.plain_text(value) if value is not None else None


def _optional(**values):
    return {k: v for k, v in values.items() if v is not None}


def _read(kind, f):
    """What an importer reads from an entry's fields, named as expected.yaml names it."""
    if kind == "External_Reference":
        return {
            "reference_id": f["@Reference_ID"],
            "authors": [_text(a) for a in f.get("Author", ())],
            **{
                key: _text(_one(f, name))
                for key, name in (
                    ("title", "Title"),
                    ("edition", "Edition"),
                    ("publication", "Publication"),
                    ("publication_year", "Publication_Year"),
                    ("publication_month", "Publication_Month"),
                    ("publication_day", "Publication_Day"),
                    ("publisher", "Publisher"),
                    ("url", "URL"),
                    ("url_date", "URL_Date"),
                )
            },
            "child_elements": [name for name, _ in _pairs(f)],
        }
    notes = _one(f, "Mapping_Notes")
    found = {
        "name": f["@Name"],
        "status": f["@Status"],
        "abstraction": f.get("@Abstraction"),
        "structure": f.get("@Structure"),
        "type": f.get("@Type"),
        "diagram": f.get("@Diagram"),
        "child_elements": [name for name, _ in _pairs(f)],
        "description": _text(_one(f, "Description")),
        "summary": _text(_one(f, "Summary")),
        "objective": _text(_one(f, "Objective")),
        "filter": _one(f, "Filter"),
        "related_weaknesses": [
            _optional(
                nature=r["@Nature"],
                cwe_id=int(r["@CWE_ID"]),
                view_id=int(r["@View_ID"]),
                ordinal=r.get("@Ordinal"),
                chain_id=int(r["@Chain_ID"]) if "@Chain_ID" in r else None,
            )
            for r in _all(f, "Related_Weaknesses", "Related_Weakness")
        ],
        "primary_parents": {
            r["@View_ID"]: int(r["@CWE_ID"])
            for r in _all(f, "Related_Weaknesses", "Related_Weakness")
            if r["@Nature"] == "ChildOf" and r.get("@Ordinal") == "Primary"
        },
        "weakness_ordinalities": [
            _text(_one(o, "Ordinality"))
            for o in _all(f, "Weakness_Ordinalities", "Weakness_Ordinality")
        ],
        "taxonomy_mappings": [
            _optional(
                taxonomy_name=t["@Taxonomy_Name"],
                entry_id=_one(t, "Entry_ID"),
                entry_name=_one(t, "Entry_Name"),
                mapping_fit=_one(t, "Mapping_Fit"),
            )
            for t in _all(f, "Taxonomy_Mappings", "Taxonomy_Mapping")
        ],
        "related_attack_patterns": [
            int(p["@CAPEC_ID"])
            for p in _all(f, "Related_Attack_Patterns", "Related_Attack_Pattern")
        ],
        "references_cited": list(  # distinct ids; a reference cited twice is kept twice
            dict.fromkeys(r["@External_Reference_ID"] for r in _all(f, "References", "Reference"))
        ),
        "counts": {
            name: n
            for name, n in {
                item: len(_all(f, container, item))
                for container, item in (
                    ("Common_Consequences", "Consequence"),
                    ("Detection_Methods", "Detection_Method"),
                    ("Potential_Mitigations", "Mitigation"),
                    ("Demonstrative_Examples", "Demonstrative_Example"),
                    ("Observed_Examples", "Observed_Example"),
                    ("Modes_Of_Introduction", "Introduction"),
                    ("Alternate_Terms", "Alternate_Term"),
                    ("Notes", "Note"),
                )
            }.items()
            if n
        },
        "note_types": [n["@Type"] for n in _all(f, "Notes", "Note")],
        "members": [
            {"relation": name, "cwe_id": int(m["@CWE_ID"]), "view_id": int(m["@View_ID"])}
            for holder in (*f.get("Relationships", ()), *f.get("Members", ()))
            for name, m in _pairs(holder)
        ],
        "audience": [
            _optional(type=_text(_one(s, "Type")), description=_text(_one(s, "Description")))
            for s in _all(f, "Audience", "Stakeholder")
        ],
        "mapping_notes": {
            "usage": _one(notes, "Usage"),
            "reasons": [r["@Type"] for r in _all(notes, "Reasons", "Reason")],
            "rationale": _text(_one(notes, "Rationale")),
            "comments": _text(_one(notes, "Comments")),
            "suggestions": [
                {"cwe_id": int(s["@CWE_ID"]), "comment": s["@Comment"]}
                for s in _all(notes, "Suggestions", "Suggestion")
            ],
        },
        "content_history": _history(_one(f, "Content_History")),
    }
    return found


def _history(h):
    submission = _one(h, "Submission")
    modifications = _all(h, "Modification")
    last = modifications[-1] if modifications else None
    return {
        "submission": _optional(
            name=_one(submission, "Submission_Name"),
            organization=_one(submission, "Submission_Organization"),
            date=_one(submission, "Submission_Date"),
            version=_one(submission, "Submission_Version"),
            release_date=_one(submission, "Submission_ReleaseDate"),
        ),
        "modifications": len(modifications),
        "modification_dates_ascending": [_one(m, "Modification_Date") for m in modifications]
        == sorted(_one(m, "Modification_Date") for m in modifications),
        "modifications_critical": [
            _optional(
                date=_one(m, "Modification_Date"),
                version=_one(m, "Modification_Version"),
                comment=_text(_one(m, "Modification_Comment")),
            )
            for m in modifications
            if _one(m, "Modification_Importance") == "Critical"
        ],
        "last_modification": _optional(
            date=_one(last, "Modification_Date"),
            version=_one(last, "Modification_Version"),
            release_date=_one(last, "Modification_ReleaseDate"),
        ),
        "contributions": [
            _optional(
                type=c["@Type"],
                date=_one(c, "Contribution_Date"),
                version=_one(c, "Contribution_Version"),
            )
            for c in _all(h, "Contribution")
        ],
        "previous_entry_names": [
            {"name": p["#text"], "date": p["@Date"]} for p in _all(h, "Previous_Entry_Name")
        ],
    }


def _like(found, expected):
    """`found` cut down to the keys `expected` has, so optional keys compare cleanly."""
    if isinstance(expected, dict) and isinstance(found, dict):
        return {key: _like(found.get(key), value) for key, value in expected.items()}
    if isinstance(expected, list) and isinstance(found, list) and len(found) == len(expected):
        return [_like(f, e) for f, e in zip(found, expected, strict=True)]
    return found


def _key(fields):
    return fields.get("@ID") or fields.get("@Reference_ID")


def _tally(value):
    """(elements, attributes, words) in a kept value, counting the entry itself."""
    elements, attributes, words = 1, 0, 0
    if isinstance(value, str):
        return 1, 0, len(cwe.plain_text(value).split())
    for key, item in value.items():
        if key.startswith("@"):
            attributes += 1
        elif key in ("#text", "#xhtml"):
            words += len(cwe.plain_text({key: item}).split())
        elif key == "#items":
            for one in item:
                e, a, w = _tally(next(iter(one.values())))
                elements, attributes, words = elements + e, attributes + a, words + w
        else:
            for one in item:
                e, a, w = _tally(one)
                elements, attributes, words = elements + e, attributes + a, words + w
    return elements, attributes, words


def _source_tally(element):
    """The same count read straight from the XML: XHTML inside an element counts as its words."""
    holds_markup = any(not c.tag.startswith(f"{{{cwe.CWE_NS}}}") for c in element)
    text = " ".join(element.itertext()) if holds_markup or not len(element) else ""
    elements, attributes, words = 1, len(element.attrib), len(text.split())
    if not holds_markup:
        for child in element:
            e, a, w = _source_tally(child)
            elements, attributes, words = elements + e, attributes + a, words + w
    return elements, attributes, words
