"""The CAPEC reader and its objects (#244): every field kept, the source's values found.

Runs on `fixtures/capec/capec_v3.9-sample.xml`: 13 attack patterns, 3 categories, 3
views and the 15 external references they cite, copied verbatim from MITRE's CAPEC
3.9 and chosen so that every field, attribute value and link kind of the release
appears. The typed values are checked against the XML read independently with
ElementTree. Set TMODEL_CAPEC_FULL to MITRE's capec_v3.9.xml to check the whole
release as well.
"""

import os
import threading
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import pytest

from engine.load import capec, cwe

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "capec"
SAMPLE = FIXTURES / "capec_v3.9-sample.xml"
SAMPLE_SHA256 = "68789138ccecf9e921e079b9ef3283f60d94632f266ae9eae611e8721abb0127"
FULL_SHA256 = "70279a2dff0cb0ad79e546adb07828335a704ad5210e047e09e986172fc9e34d"
NS = f"{{{capec.CAPEC_NS}}}"
SAMPLE_NUMBERS = [115, 192, 23, 273, 478, 497, 5, 602, 63, 66, 7, 701, 88]  # in file order
CWE_SAMPLE = FIXTURES.parent / "cwe" / "cwec_v4.20-sample.xml"


@pytest.fixture(scope="module")
def catalog():
    return capec.load_catalog(SAMPLE, SAMPLE_SHA256)


@pytest.fixture(scope="module")
def source():
    """The sample's attack patterns read straight from the XML, by number."""
    root = ElementTree.parse(SAMPLE).getroot()
    return {int(p.get("ID")): p for p in root.iter(f"{NS}Attack_Pattern")}


# --- reading the sample ----------------------------------------------------------------


def test_sample_loads_with_its_pinned_digest(catalog):
    assert (catalog.name, catalog.version, catalog.date) == ("CAPEC", "3.9", "2023-01-24")
    assert (catalog.schema, catalog.file, catalog.sha256) == (
        "3.5",
        "capec_v3.9-sample.xml",
        SAMPLE_SHA256,
    )
    assert [p.number for p in catalog.attack_patterns] == SAMPLE_NUMBERS
    assert [c.id for c in catalog.categories] == ["CAPEC-210", "CAPEC-371", "CAPEC-684"]
    assert [v.id for v in catalog.views] == ["CAPEC-1000", "CAPEC-483", "CAPEC-703"]
    assert len(catalog.references) == 15 and catalog.references[0]["@Reference_ID"] == "REF-1"
    assert catalog.unknown == ()


def test_get_takes_any_spelling_of_an_id(catalog):
    assert (
        catalog.get("CAPEC-66") is catalog.get("capec-66") is catalog.get(" 66 ") is catalog.get(66)
    )
    assert catalog.get("CAPEC-210").kind == "Category"
    assert catalog.get("CAPEC-99999") is None and catalog.get("not an id") is None


def test_typed_fields_agree_with_the_entry(catalog):
    sql = catalog.get("CAPEC-66")
    assert (sql.name, sql.abstraction, sql.status) == ("SQL Injection", "Standard", "Draft")
    assert (sql.likelihood, sql.severity) == ("High", "High")
    assert sql.description.startswith("This attack exploits target software that constructs SQL")
    assert sql.weaknesses == ("CWE-89", "CWE-1286")
    assert sql.related_attack_patterns == (("ChildOf", "CAPEC-248"),)
    assert (sql.steps, sql.mitigations, sql.examples) == (4, 3, 1)
    assert sql.url == "https://capec.mitre.org/data/definitions/66.html"
    assert catalog.get("CAPEC-478").attack_techniques == ("T1574.011", "T1543.003")
    assert catalog.get("CAPEC-273").alternate_terms == ("HTTP Desync",)
    view = catalog.get("CAPEC-1000")
    assert (view.kind, view.name, view.view_type, view.status) == (
        "View",
        "Mechanisms of Attack",
        "Graph",
        "Stable",
    )
    assert view.description.startswith("This view organizes attack patterns hierarchically")
    assert catalog.get("CAPEC-602").status == "Deprecated"


@pytest.mark.parametrize("number", SAMPLE_NUMBERS)
def test_every_attack_pattern_has_the_values_its_xml_holds(catalog, source, number):
    entry, xml = catalog.get(number), source[number]
    assert (entry.name, entry.abstraction, entry.status) == (
        xml.get("Name"),
        xml.get("Abstraction"),
        xml.get("Status"),
    )
    assert entry.likelihood == _text(xml.find(f"{NS}Likelihood_Of_Attack"))
    assert entry.severity == _text(xml.find(f"{NS}Typical_Severity"))
    assert entry.description == " ".join("".join(xml.find(f"{NS}Description").itertext()).split())
    assert list(entry.weaknesses) == list(
        dict.fromkeys(f"CWE-{w.get('CWE_ID')}" for w in xml.iter(f"{NS}Related_Weakness"))
    )
    assert entry.related_attack_patterns == tuple(
        (r.get("Nature"), f"CAPEC-{r.get('CAPEC_ID')}")
        for r in xml.iter(f"{NS}Related_Attack_Pattern")
    )
    assert list(entry.attack_techniques) == list(
        dict.fromkeys(
            f"T{t.findtext(f'{NS}Entry_ID').strip()}"
            for t in xml.iter(f"{NS}Taxonomy_Mapping")
            if t.get("Taxonomy_Name") == "ATTACK"
        )
    )
    counts = (entry.steps, entry.mitigations, entry.examples)
    assert counts == tuple(
        len(xml.findall(f"{NS}{container}/{NS}{item}"))
        for container, item in (
            ("Execution_Flow", "Attack_Step"),
            ("Mitigations", "Mitigation"),
            ("Example_Instances", "Example"),
        )
    )


def test_items_written_as_text_alone_are_counted(catalog):
    # CAPEC writes mitigations, examples and prerequisites as text, which a reader
    # that counts only structured items would miss.
    mitigations = catalog.get("CAPEC-66").fields["Mitigations"][0]["Mitigation"]
    assert [type(m) for m in mitigations] == [str, str, str]
    assert catalog.get("CAPEC-66").mitigations == 3


# --- nothing lost ------------------------------------------------------------------------


def test_every_element_attribute_and_word_is_kept(catalog):
    root = ElementTree.parse(SAMPLE).getroot()
    entries = [e for container in root for e in container]
    kept = [
        *(e.fields for e in (*catalog.attack_patterns, *catalog.categories, *catalog.views)),
        *catalog.references,
    ]
    by_key = {(f.get("@ID") or f.get("@Reference_ID")): f for f in kept}
    assert len(by_key) == len(entries) == 34
    for element in entries:
        fields = by_key[element.get("ID") or element.get("Reference_ID")]
        assert _tally(fields) == _source_tally(element), element.get("ID")


def test_structured_text_keeps_its_markup(catalog):
    extended = catalog.get("CAPEC-66").fields["Extended_Description"][0]["#xhtml"]
    assert extended.startswith("<p>When specially crafted user-controlled input")
    assert "xhtml:" not in extended and "xmlns" not in extended


def test_an_unknown_field_is_kept_and_reported(tmp_path):
    changed = tmp_path / "capec.xml"
    text = SAMPLE.read_text(encoding="utf-8")
    changed.write_text(
        text.replace("<Content_History>", "<Future_Field>soon</Future_Field><Content_History>", 1),
        encoding="utf-8",
    )
    catalog = capec.load_catalog(changed)
    assert catalog.unknown == (("Attack_Pattern/Future_Field", 1),)
    assert catalog.get("CAPEC-115").fields["Future_Field"] == ("soon",)
    assert catalog.report()[-1] == {
        "kind": "Attack_Pattern",
        "field": "Future_Field",
        "entries": 1,
        "maps_to": None,
        "known": False,
    }


def test_the_report_names_every_entry_field_and_where_it_goes(catalog):
    rows = catalog.report()
    assert len(rows) == sum(len(names) for names in capec.ENTRY_FIELDS.values()) == 54
    by = {(r["kind"], r["field"]): r for r in rows}
    assert by[("Attack_Pattern", "Description")] == {
        "kind": "Attack_Pattern",
        "field": "Description",
        "entries": 13,
        "maps_to": "AttackPattern.description",
        "known": True,
    }
    assert by[("Attack_Pattern", "Related_Weaknesses")]["maps_to"] == (
        "Assertion: Weakness exploited_by AttackPattern"
    )
    assert by[("Attack_Pattern", "Mitigations")]["maps_to"] is None  # kept on the entry
    assert by[("View", "Audience")]["entries"] == 0  # in the schema, in no 3.9 view
    assert by[("External_Reference", "Title")]["entries"] == 15


def test_links_name_what_is_not_mapped(catalog):
    assert catalog.links() == {
        "weakness_links": 25,
        "weakness_links_without_cwe_id": [],
        "weakness_links_repeated": [],
        "attack_pattern_links": {
            "CanAlsoBe": 1,
            "CanFollow": 1,
            "CanPrecede": 9,
            "ChildOf": 10,
            "PeerOf": 1,
        },
        "taxonomy_mappings": {"ATTACK": 4, "OWASP Attacks": 3, "WASC": 4},
    }


def test_a_weakness_given_twice_makes_one_link_and_is_listed(tmp_path):
    changed = tmp_path / "capec.xml"
    text = SAMPLE.read_text(encoding="utf-8")
    one = '<Related_Weakness CWE_ID="89"/>'
    assert text.count(one) == 2  # CAPEC-66 and CAPEC-7 both cite CWE-89
    changed.write_text(text.replace(one, one + one, 1), encoding="utf-8")
    catalog = capec.load_catalog(changed)
    first = next(p for p in catalog.attack_patterns if "CWE-89" in p.weaknesses)
    assert catalog.links()["weakness_links_repeated"] == [
        {"attack_pattern": first.id, "weakness": "CWE-89", "times": 2}
    ]
    assert first.weaknesses.count("CWE-89") == 1


# --- refusing what is not the pinned catalog ------------------------------------------------


def test_other_bytes_than_the_pinned_ones_are_refused():
    with pytest.raises(
        capec.CapecError, match=f"SHA-256 {SAMPLE_SHA256} is not the 0+ the library pins"
    ):
        capec.load_catalog(SAMPLE, "0" * 64)


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda t: t.replace("?>", "?><!DOCTYPE x [<!ENTITY a 'b'>]>", 1), "DOCTYPE or ENTITY"),
        # a declaration after the root's start tag is refused too, wherever it is
        (lambda t: t.replace("<Views>", "<Views><!ENTITY a 'b'>", 1), "DOCTYPE or ENTITY"),
        (lambda t: t.replace("capec.mitre.org/capec-3", "capec.mitre.org/capec-4", 1), "Schema 3"),
        (lambda t: "<root/>", "no Attack_Pattern_Catalog"),
        (lambda t: t[: len(t) // 2], "not well-formed"),
        (lambda t: t.replace('ID="66"', 'ID="210"', 1), "both an attack pattern and a category"),
        (lambda t: t.replace('ID="66"', 'ID="7"', 1), "CAPEC-7 is given twice"),
        (lambda t: t.replace('ID="66" ', "", 1), "has no whole-number ID"),
        (lambda t: t.replace(' Status="Deprecated"', "", 1), "CAPEC-602 has no Status"),
        (lambda t: t.replace(' Version="3.9"', "", 1), "Attack_Pattern_Catalog has no Version"),
    ],
)
def test_what_is_not_a_capec_schema_3_catalog_is_refused(tmp_path, change, message):
    bad = tmp_path / "bad.xml"
    bad.write_text(change(SAMPLE.read_text(encoding="utf-8")), encoding="utf-8")
    with pytest.raises(capec.CapecError, match=message):
        capec.load_catalog(bad)


def test_a_zip_is_not_read(tmp_path):
    # The library pins MITRE's XML itself, so a zip of it is another file.
    archive = tmp_path / "capec_v3.9.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(SAMPLE, "capec_v3.9.xml")
    with pytest.raises(capec.CapecError, match="not a CAPEC catalog"):
        capec.load_catalog(archive)


def test_a_file_over_the_size_limit_is_refused_before_it_is_read(monkeypatch):
    monkeypatch.setattr(capec, "MAX_FILE_BYTES", SAMPLE.stat().st_size - 1)
    with pytest.raises(capec.CapecError, match="larger than .* bytes, so it is not read"):
        capec.load_catalog(SAMPLE, SAMPLE_SHA256)
    monkeypatch.setattr(capec, "MAX_FILE_BYTES", SAMPLE.stat().st_size)
    assert len(capec.load_catalog(SAMPLE, SAMPLE_SHA256).attack_patterns) == 13


def test_the_limit_is_capecs_own(monkeypatch):
    monkeypatch.setattr(cwe, "MAX_FILE_BYTES", 1)  # the CWE reader's limit does not apply
    assert len(capec.load_catalog(SAMPLE, SAMPLE_SHA256).attack_patterns) == 13


def test_a_missing_file_cannot_be_read(tmp_path):
    with pytest.raises(capec.CapecError, match="missing.xml: cannot read"):
        capec.load_catalog(tmp_path / "missing.xml")


@pytest.mark.parametrize("kind", ["directory", "device"])
def test_only_a_regular_file_is_read(tmp_path, kind):
    target = tmp_path if kind == "directory" else Path(os.devnull)
    if not target.exists():
        pytest.skip(f"no {os.devnull} here")
    with pytest.raises(capec.CapecError, match="cannot read|not a regular file"):
        capec.load_catalog(target)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="no FIFOs on this platform")
def test_a_fifo_is_refused_without_waiting_for_a_writer(tmp_path):
    fifo = tmp_path / "capec_v3.9.xml"
    os.mkfifo(fifo)
    errors = []

    def load():
        try:
            capec.load_catalog(fifo)
        except capec.CapecError as exc:
            errors.append(str(exc))

    worker = threading.Thread(target=load, daemon=True)
    worker.start()
    worker.join(timeout=10)
    waited = worker.is_alive()
    if waited:  # open the FIFO's other end, so the thread can finish
        os.close(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
        worker.join(timeout=10)
    assert not waited, "load_catalog waited for a writer instead of refusing the FIFO"
    assert errors == ["capec_v3.9.xml: not a regular file, so it is not read"]


def test_cached_catalog_reloads_only_when_the_bytes_change(tmp_path):
    copy = tmp_path / "capec.xml"
    copy.write_bytes(SAMPLE.read_bytes())
    first = capec.cached_catalog(copy, SAMPLE_SHA256)
    assert capec.cached_catalog(copy, SAMPLE_SHA256.upper()) is first
    copy.write_bytes(SAMPLE.read_bytes().replace(b"SQL Injection", b"SQL injection", 1))
    with pytest.raises(capec.CapecError, match="is not the"):
        capec.cached_catalog(copy, SAMPLE_SHA256)


def test_configured_catalog_reads_the_variable(monkeypatch):
    monkeypatch.delenv(capec.CATALOG_ENV, raising=False)
    assert capec.configured_catalog() is None
    monkeypatch.setenv(capec.CATALOG_ENV, "  ")
    assert capec.configured_catalog() is None
    monkeypatch.setenv(capec.CATALOG_ENV, str(SAMPLE))
    assert capec.configured_catalog() == SAMPLE


def test_capec_number_takes_an_id_and_refuses_anything_else():
    assert capec.capec_number("CAPEC-66") == capec.capec_number("capec-66") == 66
    with pytest.raises(ValueError, match="a CAPEC id looks like CAPEC-66, not 'CWE-89'"):
        capec.capec_number("CWE-89")


# --- objects in the tmodel object model ------------------------------------------------


def test_one_attack_pattern_object_per_capec_attack_pattern(catalog):
    objects = capec.to_objects(catalog)
    assert [p["id"] for p in objects["attack_patterns"]] == [
        f"attack-pattern:capec-{n}" for n in SAMPLE_NUMBERS
    ]
    sql = next(p for p in objects["attack_patterns"] if p["catalog_ref"] == "CAPEC-66")
    assert sql == {
        "id": "attack-pattern:capec-66",
        "name": "SQL Injection",
        "description": catalog.get("CAPEC-66").description,
        "catalog_ref": "CAPEC-66",
    }


def test_cwe_links_become_proposed_assertions(catalog):
    objects = capec.to_objects(catalog, [66])
    assert [w["id"] for w in objects["weaknesses"]] == ["weakness:cwe-89", "weakness:cwe-1286"]
    assert all(set(w) == {"id", "catalog_ref"} for w in objects["weaknesses"])
    assert [a["id"] for a in objects["assertions"]] == [
        "assertion:capec-66-related-weakness-cwe-89",
        "assertion:capec-66-related-weakness-cwe-1286",
    ]
    for statement in objects["assertions"]:
        assert (statement["predicate"], statement["object"]) == (
            "exploited_by",
            "attack-pattern:capec-66",
        )
        assert statement["assertion_status"] == "proposed"
        assert statement["asserted_by"] == capec.MITRE_PARTY
        assert "SHA-256 " + SAMPLE_SHA256 in statement["generated_by"]
    assert objects["assertions"][0]["name"] == "CWE-89 is exploited by CAPEC-66"


def test_every_reference_resolves_inside_the_objects(catalog):
    objects = capec.to_objects(catalog)
    ids = {o["id"] for items in objects.values() for o in items}
    assert len(ids) == sum(len(items) for items in objects.values())  # ids are unique
    for statement in objects["assertions"]:
        assert {statement["subject"], statement["object"], statement["asserted_by"]} <= ids
    assert objects["parties"] == [
        {"id": "party:mitre-capec", "name": "MITRE CAPEC Program", "party_kind": "organization"}
    ]


def test_ids_meet_the_cwe_imports_and_assertions_never_collide(catalog):
    cwe_objects = cwe.to_objects(cwe.load_catalog(CWE_SAMPLE))
    capec_objects = capec.to_objects(catalog)
    # CWE-79 cites CAPEC-63 in both samples: the same AttackPattern id, which the CWE
    # import makes with only catalog_ref and this import names.
    shared = {p["id"] for p in cwe_objects["attack_patterns"]} & {
        p["id"] for p in capec_objects["attack_patterns"]
    }
    assert "attack-pattern:capec-63" in shared
    assert "weakness:cwe-79" in {w["id"] for w in capec_objects["weaknesses"]}
    assert not {a["id"] for a in cwe_objects["assertions"]} & {
        a["id"] for a in capec_objects["assertions"]
    }


# --- the whole release, when MITRE's file is at hand --------------------------------------------


@pytest.mark.skipif(not os.environ.get("TMODEL_CAPEC_FULL"), reason="TMODEL_CAPEC_FULL not set")
def test_the_whole_39_release():
    full = capec.load_catalog(os.environ["TMODEL_CAPEC_FULL"], FULL_SHA256)
    assert (full.version, full.schema, full.unknown) == ("3.9", "3.5", ())
    counts = (
        len(full.attack_patterns),
        len(full.categories),
        len(full.views),
        len(full.references),
    )
    assert counts == (615, 78, 13, 440)
    assert Counter(p.abstraction for p in full.attack_patterns) == {
        "Detailed": 341,
        "Standard": 197,
        "Meta": 77,
    }
    assert Counter(p.status for p in full.attack_patterns) == {
        "Draft": 402,
        "Stable": 154,
        "Deprecated": 56,
        "Usable": 2,
        "Obsolete": 1,
    }
    links = full.links()
    assert (links["weakness_links"], len(links["weakness_links_repeated"])) == (1214, 2)
    assert links["taxonomy_mappings"] == {"ATTACK": 272, "OWASP Attacks": 39, "WASC": 37}
    objects = {name: len(items) for name, items in full.objects.items()}
    assert objects == {"parties": 1, "attack_patterns": 615, "weaknesses": 336, "assertions": 1212}


# --- helpers -----------------------------------------------------------------------------------


def _text(element):
    return " ".join(element.text.split()) if element is not None and element.text else None


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
    holds_markup = any(not c.tag.startswith(NS) for c in element)
    text = " ".join(element.itertext()) if holds_markup or not len(element) else ""
    elements, attributes, words = 1, len(element.attrib), len(text.split())
    if not holds_markup:
        for child in element:
            e, a, w = _source_tally(child)
            elements, attributes, words = elements + e, attributes + a, words + w
    return elements, attributes, words
