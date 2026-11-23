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
        {"source": "CWE-79", "nature": "ChildOf", "target": "CWE-74", "view": "CWE-1000"}
    ]
    assert (rel["in_file"], rel["imported"]) == (20, 19)
    assert rel["by_view"]["CWE-1000"] == {"in_file": 9, "imported": 8}
    assert main([str(SAMPLE), "--sha256", SAMPLE_SHA256]) == 1
    out, err = capsys.readouterr()
    assert "**Lossless: no.**" in out
    assert "Missing: CWE-79 ChildOf CWE-74 in CWE-1000." in out
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
    assert loss["differs"] == ["values", "elements", "attributes", "words"]
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
        | {"in_file": 1, "imported": 2},
        {"source": "CWE-79", "nature": "PeerOf", "target": "CWE-352", "view": "CWE-1000"}
        | {"in_file": 2, "imported": 1},
    ]
    assert lossy["lossless"] is False
    assert "Given a different number of times: CWE-79 ChildOf CWE-74 in CWE-1000" in to_markdown(
        lossy
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
    assert to_markdown(full) == REPORT_420.read_text(encoding="utf-8")
