"""The CWE import's reconciliation (#146): the file read twice, and every loss named.

Runs on the CWE sample (`fixtures/cwe/`, 12 entries and 3 references copied verbatim
from CWE 4.20), which the import keeps whole, and on imports that are made to lose one
thing, which the report must name. Set TMODEL_CWE_FULL to MITRE's cwec_v4.20.xml.zip to
check the whole release, and that the committed report is the one the release gives.
"""

import dataclasses
import json
import os
from pathlib import Path
from types import MappingProxyType

import pytest

from engine.load import cwe, cwe_reconcile
from engine.load.cwe_reconcile import main, reconcile, to_markdown

TESTS = Path(__file__).resolve().parent
SAMPLE = TESTS / "fixtures" / "cwe" / "cwec_v4.20-sample.xml"
SAMPLE_SHA256 = "e26b565b22747a93e88a999f24d1578299e53d6669011bb9c015e690fef26b43"
FULL_SHA256 = "3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50"
REPORT_420 = TESTS.parents[1] / "design-log" / "0058-cwe-reconciliation" / "report-cwe-4.20.md"


@pytest.fixture(scope="module")
def report():
    return reconcile(SAMPLE, SAMPLE_SHA256)


def _losing(monkeypatch, change):
    """Make the import lose something: `change` takes the catalog and returns the one served."""
    load = cwe.load_catalog

    def changed(path, sha256=None):
        return change(load(path, sha256))

    monkeypatch.setattr(cwe, "load_catalog", changed)


def _without(catalog, entry_id):
    """The catalog with one weakness gone."""
    kept = tuple(w for w in catalog.weaknesses if w.id != entry_id)
    return dataclasses.replace(catalog, weaknesses=kept)


def _with_fields(catalog, entry_id, change):
    """The catalog with one weakness's kept fields changed."""
    weaknesses = tuple(
        dataclasses.replace(w, fields=MappingProxyType(change(dict(w.fields))))
        if w.id == entry_id
        else w
        for w in catalog.weaknesses
    )
    return dataclasses.replace(catalog, weaknesses=weaknesses)


def _edited(tmp_path, old, new, first=False):
    """The sample with `old` changed to `new`: its one occurrence, or with `first` the first."""
    text = SAMPLE.read_text(encoding="utf-8")
    assert first or text.count(old) == 1, old
    changed = tmp_path / "cwe.xml"
    changed.write_text(text.replace(old, new, 1), encoding="utf-8")
    return changed


# --- the sample is kept whole ----------------------------------------------------------------


def test_the_sample_is_lossless(report):
    assert report["lossless"] is True
    assert report["catalog"]["sha256"] == SAMPLE_SHA256
    entries = report["entries"]
    assert entries["by_kind_in_file"] == entries["by_kind_imported"]
    assert entries["by_kind_in_file"] == {"Weakness": 9, "Category": 2, "View": 1}
    assert entries["missing"] == entries["extra"] == entries["kind_changed"] == []
    assert (report["references"]["in_file"], report["references"]["imported"]) == (3, 3)
    assert report["references"]["repeated_differently"] == []
    rel = report["relationships"]
    assert (rel["in_file"], rel["imported"], rel["distinct_in_file"]) == (20, 20, 20)
    assert rel["missing"] == rel["extra"] == rel["repeated_differently"] == []
    assert report["fields"]["checked"] == 15 and report["fields"]["not_kept"] == []
    assert report["fields"]["unknown"] == []
    links = report["links"]
    assert all(link["in_file"] == link["imported"] for link in links.values())
    assert links["observed_examples"]["in_file"] > 0 < links["attack_pattern_links"]["in_file"]


def test_the_three_views_plan_0002_names_are_reported_on_their_own(report):
    # #146's criterion is the union of the entries across CWE-1000, CWE-699 and CWE-1194;
    # the report gives it apart from the coverage across every view (#249, second review).
    named = report["views"]["named"]
    assert named == {
        "views": ["CWE-1000", "CWE-699", "CWE-1194"],
        "entries_reached": 7,
        "imported": 7,
        "missing": [],
    }
    text = to_markdown(report)
    assert (
        "across the three views it names, CWE-1000, CWE-699, and CWE-1194: their relationships "
        "reach 7 entries, and the import has all of them. Across all the views, 8 entries are "
        "reached"
    ) in " ".join(text.split())


def test_the_views_reach_some_entries_and_the_import_keeps_the_rest(report):
    views = report["views"]
    assert views["entries_reached"] == 8
    assert [(x["id"], x["status"], x["view_type"]) for x in views["entries_without_view"]] == [
        ("CWE-373", "Deprecated", None),
        ("CWE-709", "Incomplete", "Implicit"),
        ("CWE-769", "Deprecated", None),
        ("CWE-1187", "Deprecated", None),
    ]


def test_relationships_are_compared_by_nature_and_by_view(report):
    by_nature = report["relationships"]["by_nature"]
    assert list(by_nature) == [
        "ChildOf",
        "StartsWith",
        "CanPrecede",
        "Requires",
        "PeerOf",
        "HasMember",
    ]
    assert by_nature["HasMember"] == {"in_file": 9, "imported": 9}
    by_view = report["relationships"]["by_view"]
    assert list(by_view)[:2] == ["CWE-1000", "CWE-699"]  # PLAN-0002 §5's views first
    assert by_view["CWE-1003"] == {"in_file": 1, "imported": 1}


def test_every_field_has_a_row_saying_where_it_goes(report):
    rows = report["fields"]["rows"]
    assert len(rows) == sum(len(names) for names in cwe.ENTRY_FIELDS.values())
    description = next(r for r in rows if (r["kind"], r["field"]) == ("Weakness", "Description"))
    assert description == {
        "kind": "Weakness",
        "field": "Description",
        "in_file": 9,
        "imported": 9,
        "maps_to": "Weakness.description",
        "known": True,
    }


# --- a loss is named, and the check fails -------------------------------------------------------


def test_dropping_one_relationship_shows_the_loss_and_fails(monkeypatch, capsys):
    # #146's test plan: drop one relationship from a test import
    read = cwe._relationships

    def one_fewer(name, label, kind, fields):
        found = read(name, label, kind, fields)
        return found[1:] if label == "CWE-79" else found

    monkeypatch.setattr(cwe, "_relationships", one_fewer)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    rel = lossy["relationships"]
    assert rel["missing"] == [
        {
            "source": "CWE-79",
            "nature": "ChildOf",
            "target": "CWE-74",
            "view": "CWE-1000",
            "ordinal": "Primary",
            "chain": None,
        }
    ]
    assert (rel["in_file"], rel["imported"]) == (20, 19)
    assert rel["by_view"]["CWE-1000"] == {"in_file": 9, "imported": 8}
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256]) == 1
    out, err = capsys.readouterr()
    assert "**Lossless: no.**" in out
    assert "Missing: CWE-79 ChildOf CWE-74 in CWE-1000 (ordinal Primary)." in out
    assert "the import lost something from the file" in err


def test_a_dropped_entry_is_named_once(monkeypatch):
    _losing(monkeypatch, lambda catalog: _without(catalog, "CWE-692"))
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    assert lossy["entries"]["missing"] == ["CWE-692"]
    assert lossy["entries"]["by_kind_imported"]["Weakness"] == 8
    assert lossy["fields"]["not_kept"] == []  # the entry is missing, which says it all
    assert {t["source"] for t in lossy["relationships"]["missing"]} == {"CWE-692"}


def test_a_field_not_kept_is_named_with_both_tallies(monkeypatch):
    def drop_notes(fields):
        fields.pop("Notes")
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", drop_notes))
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    [loss] = lossy["fields"]["not_kept"]
    assert (loss["entry"], loss["field"]) == ("CWE-79", "Notes")
    assert loss["in_file"]["values"] == 1 and loss["kept"] == {"values": 0, "tally": [0, 0, 0]}
    assert loss["differs"] == ["values", "elements", "names", "attributes", "words"]
    notes = next(
        r for r in lossy["fields"]["rows"] if (r["kind"], r["field"]) == ("Weakness", "Notes")
    )
    assert notes["in_file"] == notes["imported"] + 1


def test_an_attribute_kept_with_another_value_is_named(monkeypatch):
    def rename(fields):
        fields["@Name"] = "Something else"
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", rename))
    [loss] = reconcile(SAMPLE, SAMPLE_SHA256)["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["kept"]) == ("CWE-79", "@Name", "Something else")
    assert loss["in_file"].startswith("Improper Neutralization of Input")


def test_a_word_lost_inside_a_field_is_named(monkeypatch):
    def shorter(fields):
        fields["Description"] = ("The product does not neutralize input.",)
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", shorter))
    [loss] = reconcile(SAMPLE, SAMPLE_SHA256)["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["differs"]) == ("CWE-79", "Description", ["words"])
    assert loss["in_file"]["tally"][2] > loss["kept"]["tally"][2]  # fewer words kept


def test_a_word_changed_for_another_is_named(monkeypatch):
    # the same number of words is not enough: the words themselves must be kept
    def one_word_changed(fields):
        words = fields["Description"][0].split()
        fields["Description"] = (" ".join(["output", *words[1:]]),)
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", one_word_changed))
    [loss] = reconcile(SAMPLE, SAMPLE_SHA256)["fields"]["not_kept"]
    assert (loss["field"], loss["differs"]) == ("Description", ["words"])
    assert loss["in_file"]["tally"] == loss["kept"]["tally"]  # equal counts, other words


def test_an_attribute_inside_a_field_kept_with_another_value_is_named(monkeypatch):
    def other_view(fields):
        held = cwe._thawed(fields["Related_Weaknesses"])
        held[0]["Related_Weakness"][0]["@View_ID"] = "1001"
        fields["Related_Weaknesses"] = held
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", other_view))
    [loss] = reconcile(SAMPLE, SAMPLE_SHA256)["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["differs"]) == (
        "CWE-79",
        "Related_Weaknesses",
        ["attributes"],
    )


# --- what is kept is not a loss -------------------------------------------------------------


def test_an_unknown_field_is_flagged_and_still_lossless(tmp_path):
    future = "<Future_Field>soon</Future_Field><Mapping_Notes>"
    changed = _edited(tmp_path, "<Mapping_Notes>", future, first=True)
    flagged = reconcile(changed)
    assert flagged["lossless"] is True
    assert flagged["fields"]["unknown"] == [
        {
            "kind": "Weakness",
            "field": "Future_Field",
            "in_file": 1,
            "imported": 1,
            "maps_to": None,
            "known": False,
        }
    ]
    assert "Fields the reader does not know: Weakness/Future_Field." in to_markdown(flagged)


def test_a_relationship_written_twice_is_counted_twice(tmp_path):
    line = '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>'
    twice = reconcile(_edited(tmp_path, line, line + line))
    rel = twice["relationships"]
    assert twice["lossless"] is True
    assert (rel["in_file"], rel["imported"], rel["distinct_in_file"]) == (21, 21, 20)


# --- losses that leave every total equal (#249 review) ------------------------------------------


def test_one_relationship_losing_a_copy_as_another_gains_one_is_a_loss(monkeypatch, tmp_path):
    # The file writes PeerOf CWE-352 twice; the import keeps it once, and keeps CWE-79's
    # first relationship twice. The totals, the tuples and every view still agree.
    line = '<Related_Weakness Nature="PeerOf" CWE_ID="352" View_ID="1000"/>'
    twice = _edited(tmp_path, line, line + line)
    read = cwe._relationships

    def offsetting(name, label, kind, fields):
        found = read(name, label, kind, fields)
        if label != "CWE-79":
            return found
        peer = [r for r in found if (r.nature, r.target) == ("PeerOf", "CWE-352")]
        rest = [r for r in found if (r.nature, r.target) != ("PeerOf", "CWE-352")]
        return (*rest, rest[0], *peer[1:])

    monkeypatch.setattr(cwe, "_relationships", offsetting)
    lossy = reconcile(twice)
    rel = lossy["relationships"]
    assert (rel["in_file"], rel["imported"], rel["missing"], rel["extra"]) == (21, 21, [], [])
    assert rel["repeated_differently"] == [
        {"source": "CWE-79", "nature": "ChildOf", "target": "CWE-74", "view": "CWE-1000"}
        | {"ordinal": "Primary", "chain": None, "in_file": 1, "imported": 2},
        {"source": "CWE-79", "nature": "PeerOf", "target": "CWE-352", "view": "CWE-1000"}
        | {"ordinal": None, "chain": None, "in_file": 2, "imported": 1},
    ]
    assert lossy["lossless"] is False
    assert (
        "Given a different number of times: CWE-79 ChildOf CWE-74 in CWE-1000 (ordinal Primary)"
        in to_markdown(lossy)
    )


def test_two_entries_that_trade_kinds_are_a_loss(monkeypatch):
    # A weakness read as a category and a category read as a weakness leave the counts
    # by kind equal. Neither carries CAPEC links or observed examples, so nothing else moves.
    def traded(catalog):
        weakness = next(w for w in catalog.weaknesses if w.id == "CWE-373")
        category = next(c for c in catalog.categories if c.id == "CWE-411")
        return dataclasses.replace(
            catalog,
            weaknesses=(
                *(w for w in catalog.weaknesses if w is not weakness),
                dataclasses.replace(category, kind="Weakness"),
            ),
            categories=(
                *(c for c in catalog.categories if c is not category),
                dataclasses.replace(weakness, kind="Category"),
            ),
        )

    _losing(monkeypatch, traded)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    entries = lossy["entries"]
    assert entries["by_kind_in_file"] == entries["by_kind_imported"]
    assert (entries["missing"], entries["extra"]) == ([], [])
    assert entries["kind_changed"] == ["CWE-373", "CWE-411"]
    assert all(link["in_file"] == link["imported"] for link in lossy["links"].values())
    assert lossy["lossless"] is False
    assert "Read as another kind: CWE-373, CWE-411." in to_markdown(lossy)


def test_a_reference_kept_fewer_times_than_the_file_defines_it_is_a_loss(monkeypatch, tmp_path):
    # The file defines REF-7 twice; the import keeps one. The ids are the same set.
    text = SAMPLE.read_text(encoding="utf-8")
    start = text.rindex("\n", 0, text.index('<External_Reference Reference_ID="REF-7"')) + 1
    end = text.index("</External_Reference>", start) + len("</External_Reference>\n")
    doubled = tmp_path / "cwe.xml"
    doubled.write_text(text[:end] + text[start:end] + text[end:], encoding="utf-8")

    def once_each(catalog):
        kept = {}
        for reference in catalog.references:
            kept.setdefault(reference["@Reference_ID"], reference)
        return dataclasses.replace(catalog, references=tuple(kept.values()))

    _losing(monkeypatch, once_each)
    lossy = reconcile(doubled)
    references = lossy["references"]
    assert (references["in_file"], references["imported"]) == (4, 3)
    assert (references["missing"], references["extra"]) == ([], [])
    assert references["repeated_differently"] == ["REF-7"]
    assert lossy["lossless"] is False
    assert "Given a different number of times: REF-7." in to_markdown(lossy)


def test_an_element_kept_under_another_name_is_a_loss(monkeypatch):
    # CWE-79's Modes_Of_Introduction/Introduction/Phase read as Wrong_Phase: the same place,
    # attributes and text, so only the element's name tells them apart (@paria03, #249).
    def wrong_phase(fields):
        (modes,) = fields["Modes_Of_Introduction"]
        (introduction,) = modes["Introduction"]
        wrong = {("Wrong_Phase" if k == "Phase" else k): v for k, v in introduction.items()}
        introductions = (MappingProxyType(wrong),)
        fields["Modes_Of_Introduction"] = (MappingProxyType({"Introduction": introductions}),)
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", wrong_phase))
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    (loss,) = lossy["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["differs"]) == (
        "CWE-79",
        "Modes_Of_Introduction",
        ["names"],
    )
    assert loss["in_file"] == loss["kept"]  # same counts: only the name moved
    assert loss["first_name_difference"] == {
        "in_file": "Modes_Of_Introduction/Introduction/Phase",
        "kept": "Modes_Of_Introduction/Introduction/Wrong_Phase",
    }
    assert lossy["lossless"] is False
    assert "Fields not kept: CWE-79 Modes_Of_Introduction." in to_markdown(lossy)


# --- losses no tally or total shows (#249, second review) ---------------------------------------


def test_text_moved_into_the_next_element_is_a_loss(monkeypatch):
    # CWE-79's Phase text moved into the Note beside it: the same elements, names,
    # attributes and words, in the same order, but another element holds them
    # (@kriishnaa-18, #249).
    def moved(fields):
        (modes,) = fields["Modes_Of_Introduction"]
        (introduction,) = modes["Introduction"]
        (phase,), (note,) = introduction["Phase"], introduction["Note"]
        changed = MappingProxyType({**introduction, "Phase": ("",), "Note": (f"{phase} {note}",)})
        fields["Modes_Of_Introduction"] = (MappingProxyType({"Introduction": (changed,)}),)
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", moved))
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    (loss,) = lossy["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["differs"]) == (
        "CWE-79",
        "Modes_Of_Introduction",
        ["placement"],
    )
    assert loss["in_file"] == loss["kept"]  # every tally agrees
    phase = "Modes_Of_Introduction/Introduction/Phase"
    assert loss["first_difference"] == {
        "in_file": {"path": phase, "attributes": {}, "text": ["Implementation"]},
        "kept": {"path": phase, "attributes": {}, "text": [""]},
    }


def test_an_attribute_lost_inside_structured_text_is_a_loss(monkeypatch, tmp_path):
    # An XHTML image whose src the import drops. The words and the field's own attributes
    # are unchanged, so only the image's attributes show it (@kriishnaa-18, #249: CWE-1189).
    image = '<xhtml:img src="images/variants.png" alt="Variants"/>'
    old = "<xhtml:p>There are many variants"
    edited = _edited(tmp_path, old, old.replace("<xhtml:p>", f"<xhtml:p>{image}"))
    assert reconcile(edited)["lossless"] is True  # the import keeps the image, src and all

    def without_src(fields):
        (description,) = fields["Extended_Description"]
        markup = description["#xhtml"].replace(' src="images/variants.png"', "", 1)
        fields["Extended_Description"] = (MappingProxyType({**description, "#xhtml": markup}),)
        return fields

    _losing(monkeypatch, lambda catalog: _with_fields(catalog, "CWE-79", without_src))
    lossy = reconcile(edited)
    assert lossy["lossless"] is False
    (loss,) = lossy["fields"]["not_kept"]
    assert (loss["entry"], loss["field"], loss["differs"]) == (
        "CWE-79",
        "Extended_Description",
        ["attributes"],
    )
    first = loss["first_difference"]
    assert first["in_file"]["path"] == first["kept"]["path"] == "Extended_Description/p/img"
    assert first["in_file"]["attributes"] == {"alt": "Variants", "src": "images/variants.png"}
    assert first["kept"]["attributes"] == {"alt": "Variants"}


def test_a_relationship_kept_without_its_ordinal_or_chain_is_a_loss(monkeypatch):
    # The fields keep Ordinal and Chain_ID, but the relationships the app reads lose them,
    # and the (entry, nature, target, view) tuples alone still agree (@kriishnaa-18, #249).
    read = cwe._relationships
    stripped = {"CWE-79": ("ChildOf", "CWE-74", 1000), "CWE-692": ("StartsWith", "CWE-184", 709)}

    def without(name, label, kind, fields):
        return tuple(
            dataclasses.replace(r, ordinal=None, chain=None)
            if (r.nature, r.target, r.view) == stripped.get(label)
            else r
            for r in read(name, label, kind, fields)
        )

    monkeypatch.setattr(cwe, "_relationships", without)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    rel = lossy["relationships"]
    assert (rel["in_file"], rel["imported"]) == (20, 20)
    chain = {"source": "CWE-692", "nature": "StartsWith", "target": "CWE-184", "view": "CWE-709"}
    ordinal = {"source": "CWE-79", "nature": "ChildOf", "target": "CWE-74", "view": "CWE-1000"}
    assert rel["missing"] == [
        chain | {"ordinal": None, "chain": "CWE-692"},
        ordinal | {"ordinal": "Primary", "chain": None},
    ]
    assert rel["extra"] == [
        chain | {"ordinal": None, "chain": None},
        ordinal | {"ordinal": None, "chain": None},
    ]
    assert "CWE-79 ChildOf CWE-74 in CWE-1000 (ordinal Primary)" in to_markdown(lossy)


def test_an_observed_example_kept_with_another_reference_and_link_is_a_loss(monkeypatch):
    # The example's fields are kept, but the observed example the app reads names another
    # CVE and another URL, and every count agrees (@kriishnaa-18, #249).
    def other(catalog):
        def changed(weakness):
            first, *rest = weakness.observed_examples
            first = dataclasses.replace(
                first, reference="CVE-2024-0001", link="https://example.org/"
            )
            return dataclasses.replace(weakness, observed_examples=(first, *rest))

        weaknesses = tuple(changed(w) if w.id == "CWE-79" else w for w in catalog.weaknesses)
        return dataclasses.replace(catalog, weaknesses=weaknesses)

    _losing(monkeypatch, other)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    examples = lossy["links"]["observed_examples"]
    assert examples["in_file"] == examples["imported"]
    (differ,) = examples["values_differ"]
    assert (differ["entry"], differ["number"]) == ("CWE-79", 1)
    cve = "CVE-2024-49038"
    assert differ["in_file"]["reference"] == cve
    assert differ["in_file"]["link"] == f"https://www.cve.org/CVERecord?id={cve}"
    assert (differ["imported"]["reference"], differ["imported"]["link"]) == (
        "CVE-2024-0001",
        "https://example.org/",
    )
    assert "Observed examples kept with other values: CWE-79 example 1." in to_markdown(lossy)


def test_a_capec_link_kept_with_another_target_is_a_loss(monkeypatch):
    # CWE-689's first CAPEC link read as another attack pattern: the fields and the
    # count of links agree (@kriishnaa-18, #249).
    def other(catalog):
        weaknesses = tuple(
            dataclasses.replace(w, attack_patterns=("CAPEC-1", *w.attack_patterns[1:]))
            if w.id == "CWE-689"
            else w
            for w in catalog.weaknesses
        )
        return dataclasses.replace(catalog, weaknesses=weaknesses)

    _losing(monkeypatch, other)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    capec = lossy["links"]["attack_pattern_links"]
    assert capec["in_file"] == capec["imported"]
    assert capec["values_differ"] == [
        {
            "entry": "CWE-689",
            "in_file": ["CAPEC-26", "CAPEC-27"],
            "imported": ["CAPEC-1", "CAPEC-27"],
        }
    ]
    assert "CAPEC links kept with other values: CWE-689." in to_markdown(lossy)


def test_an_entry_imported_twice_is_a_loss(monkeypatch):
    # CWE-769 is deprecated: it writes no relationship and has no link, so a second copy
    # moves no other count, and entries keyed by id fold the copies into one (#249).
    def twice(catalog):
        copy = next(w for w in catalog.weaknesses if w.id == "CWE-769")
        return dataclasses.replace(catalog, weaknesses=(*catalog.weaknesses, copy))

    _losing(monkeypatch, twice)
    lossy = reconcile(SAMPLE, SAMPLE_SHA256)
    assert lossy["lossless"] is False
    entries = lossy["entries"]
    assert entries["by_kind_imported"]["Weakness"] == entries["by_kind_in_file"]["Weakness"] + 1
    assert (entries["missing"], entries["extra"]) == ([], [])
    assert entries["repeated_differently"] == ["CWE-769"]
    assert "Given a different number of times: CWE-769." in to_markdown(lossy)


def test_a_reference_copy_kept_with_the_other_copys_content_is_a_loss(monkeypatch, tmp_path):
    # The file defines REF-7 twice, the first copy with another title. The import keeps
    # the second copy twice. The ids and the counts agree, and a comparison keyed by id
    # sees only the last copy on each side (@kriishnaa-18, #249).
    text = SAMPLE.read_text(encoding="utf-8")
    start = text.rindex("\n", 0, text.index('<External_Reference Reference_ID="REF-7"')) + 1
    end = text.index("</External_Reference>", start) + len("</External_Reference>\n")
    title = "<Title>Writing Secure Code</Title>"
    first = text[start:end].replace(title, "<Title>Writing Secure Code, a draft</Title>")
    assert first != text[start:end]
    doubled = tmp_path / "cwe.xml"
    doubled.write_text(text[:start] + first + text[start:], encoding="utf-8")

    def second_twice(catalog):
        references = list(catalog.references)
        a, b = (i for i, r in enumerate(references) if r["@Reference_ID"] == "REF-7")
        references[a] = references[b]
        return dataclasses.replace(catalog, references=tuple(references))

    _losing(monkeypatch, second_twice)
    lossy = reconcile(doubled)
    assert lossy["lossless"] is False
    references = lossy["references"]
    assert (references["in_file"], references["imported"]) == (4, 4)
    assert references["repeated_differently"] == []
    (loss,) = lossy["fields"]["not_kept"]
    assert (loss["entry"], loss["copy"], loss["field"], loss["differs"]) == (
        "REF-7",
        1,
        "Title",
        ["words"],
    )
    assert "Fields not kept: REF-7 (copy 1) Title." in to_markdown(lossy)


# --- the report, the command and the committed copy -----------------------------------------


def test_the_same_file_always_gives_the_same_report(report):
    assert to_markdown(reconcile(SAMPLE, SAMPLE_SHA256)) == to_markdown(report)
    text = to_markdown(report)
    assert text.startswith("# CWE import reconciliation: CWE 4.20\n")
    assert "**Lossless: yes.**" in text and text.endswith("\n")
    assert "\u2014" not in text  # the project writes no em dashes


def test_the_report_does_not_depend_on_the_files_name(tmp_path, report):
    # CI saves MITRE's download under its own name; the committed report must still match
    renamed = tmp_path / "downloaded.xml"
    renamed.write_bytes(SAMPLE.read_bytes())
    again = reconcile(renamed, SAMPLE_SHA256)
    assert again["catalog"]["file"] == "downloaded.xml"  # the JSON still says which file
    assert to_markdown(again) == to_markdown(report)
    assert "downloaded.xml" not in to_markdown(again)


def test_write_then_check_passes_and_a_stale_report_fails(tmp_path, capsys):
    saved = tmp_path / "report.md"
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256, "--write", str(saved)]) == 0
    assert saved.read_text(encoding="utf-8") == to_markdown(reconcile(SAMPLE, SAMPLE_SHA256))
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256, "--check", str(saved)]) == 0
    saved.write_text("an older report\n", encoding="utf-8")
    capsys.readouterr()
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256, "--check", str(saved)]) == 1
    assert f"regenerate it with --write {saved}" in capsys.readouterr().err
    assert main([str(SAMPLE), "--check", str(tmp_path / "missing.md")]) == 2


def test_json_is_the_report(capsys):
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256, "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == reconcile(SAMPLE, SAMPLE_SHA256)


def test_other_bytes_than_the_pinned_ones_are_refused(capsys):
    assert main([str(SAMPLE), "--sha256", "0" * 64]) == 2
    assert "is not the" in capsys.readouterr().err


def test_a_file_that_changes_between_the_two_reads_is_refused(monkeypatch):
    real, reads = cwe._read, []

    def changing(path):  # the importer's read sees the file; the second read, other bytes
        reads.append(path)
        return real(path) if len(reads) == 1 else real(path) + b"\n<!-- changed -->"

    monkeypatch.setattr(cwe, "_read", changing)
    with pytest.raises(cwe.CweError, match="changed while it was being read"):
        cwe_reconcile.reconcile(SAMPLE)
    assert len(reads) == 2


@pytest.mark.skipif(not os.environ.get("TMODEL_CWE_FULL"), reason="TMODEL_CWE_FULL not set")
def test_the_whole_420_release_is_lossless_and_the_committed_report_is_its_report():
    full = reconcile(os.environ["TMODEL_CWE_FULL"], FULL_SHA256)
    assert full["lossless"] is True
    assert full["entries"]["by_kind_in_file"] == {"Weakness": 969, "Category": 422, "View": 59}
    assert full["references"]["in_file"] == 1026
    rel = full["relationships"]
    assert (rel["in_file"], rel["imported"], rel["distinct_in_file"]) == (6626, 6626, 6626)
    assert full["fields"]["checked"] == 2476 and full["fields"]["unknown"] == []
    without = full["views"]["entries_without_view"]
    assert full["views"]["entries_reached"] == 1371 and len(without) == 79
    assert sum(1 for x in without if x["status"] == "Deprecated") == 64
    assert all(x["view_type"] == "Implicit" for x in without if x["status"] != "Deprecated")
    assert full["views"]["named"]["entries_reached"] == full["views"]["named"]["imported"] == 1000
    for link in full["links"].values():
        assert link["values_differ"] == []
    assert (
        full["links"]["attack_pattern_links"]["in_file"],
        full["links"]["observed_examples"]["in_file"],
    ) == (1212, 3134)
    # two of the 17 implicit views are deprecated, so the rest are the 15 "other" ones
    assert (
        "the 64 deprecated entries (2 of them implicit views) and the 15 other implicit views"
        in (to_markdown(full))
    )
    assert to_markdown(full) == REPORT_420.read_text(encoding="utf-8")
