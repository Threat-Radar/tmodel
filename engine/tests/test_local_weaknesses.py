"""Local weakness types, tr-weak-NNNN (#145): read from YAML, served and linked as CWE's are.

The sample (`fixtures/local-weaknesses/tr-weak-sample.yaml`) holds two made-up local
weaknesses that link to entries of the CWE sample (`fixtures/cwe/`), so most tests
read both, through TMODEL_LOCAL_WEAKNESSES and TMODEL_CWE_CATALOG, as the engine does.
"""

import copy
import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest
import yaml

from engine import core
from engine.api.server import make_server
from engine.cli import main
from engine.load import cwe, local_weaknesses
from engine.load.local_weaknesses import LocalWeaknessError

TESTS = Path(__file__).resolve().parent
CWE = TESTS / "fixtures" / "cwe"
LOCAL = TESTS / "fixtures" / "local-weaknesses" / "tr-weak-sample.yaml"
CWE_SAMPLE_IDS = [
    "CWE-79",
    "CWE-373",
    "CWE-689",
    "CWE-692",
    "CWE-710",
    "CWE-769",
    "CWE-1093",
    "CWE-1174",
    "CWE-1187",
]
# The smallest file the reader accepts, which each refusal case below changes once.
MINIMAL = {
    "catalog": {
        "name": "minimal",
        "version": "1",
        "maintainer": {"id": "party:tmodel-test-fixture", "name": "tmodel test fixture"},
    },
    "weaknesses": [
        {"id": "tr-weak-0001", "name": "One", "description": "The first.", "status": "Draft"},
        {"id": "tr-weak-0002", "name": "Two", "description": "The second.", "status": "Draft"},
    ],
}


@pytest.fixture
def local():
    return local_weaknesses.load_local(LOCAL)


@pytest.fixture
def served(monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(CWE / "library"))
    monkeypatch.setenv("TMODEL_CWE_CATALOG", str(CWE / "cwec_v4.20-sample.xml"))
    monkeypatch.setenv("TMODEL_LOCAL_WEAKNESSES", str(LOCAL))


@pytest.fixture
def engine_url(served):
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def api(base, path, query):
    url = f"{base}{path}?" + urllib.parse.urlencode(query)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.status, json.loads(resp.read())


def _written(tmp_path, doc):
    path = tmp_path / "local.yaml"
    text = doc if isinstance(doc, str) else yaml.safe_dump(doc, sort_keys=False)
    path.write_text(text, encoding="utf-8")
    return path


def _relation(r):
    return (r["source"], r["nature"], r["target"], r["view"], r["derived"])


# --- reading the file ---------------------------------------------------------------------


def test_the_sample_loads(local):
    assert local.summary() == {
        "name": "tmodel local weakness sample",
        "version": "0.1",
        "file": "tr-weak-sample.yaml",
        "sha256": local.sha256,
        "maintainer": "party:tmodel-test-fixture",
        "weaknesses": 2,
    }
    one, two = local.weaknesses
    assert (one.id, one.object_id, one.source, one.kind) == (
        "tr-weak-0001",
        "weakness:tr-weak-0001",
        "local",
        "Weakness",
    )
    assert (one.status, one.abstraction, one.structure) == ("Draft", "Class", "Simple")
    assert (two.abstraction, two.structure) == ("Base", None)
    assert one.alternate_terms == ("first sample",) and one.attack_patterns == ("CAPEC-1",)
    assert [(r.nature, r.target, r.view, r.ordinal) for r in one.relationships] == [
        ("ChildOf", "CWE-710", 1000, "Primary"),
        ("CanPrecede", "tr-weak-0002", 1000, None),
    ]
    assert [(r.nature, r.target, r.view) for r in two.relationships] == [
        ("ChildOf", "tr-weak-0001", 1000),
        ("MemberOf", "CWE-411", 699),
    ]
    assert two.observed_examples[0].reference == "CVE-0000-0000"
    assert one.fields["extensions"] == {"note": "an extension is kept as written"}
    assert one.description.startswith("Not a real weakness type. It sits under CWE-710")


def test_get_takes_an_id_in_any_case(local):
    assert local.get("tr-weak-0001") is local.get("TR-WEAK-0001") is local.weaknesses[0]
    assert local.get("tr-weak-0099") is None and local.get("CWE-79") is None


def test_a_local_weakness_answers_with_the_keys_a_cwe_entry_has(local):
    catalog = cwe.load_catalog(CWE / "cwec_v4.20-sample.xml")
    entry = local.weaknesses[0].to_dict()
    assert list(entry) == list(catalog.get("CWE-79").to_dict())
    assert (entry["source"], entry["url"], entry["usage"], entry["mitigations"]) == (
        "local",
        None,
        None,
        0,
    )
    assert entry["fields"]["relationships"][0] == {
        "nature": "ChildOf",
        "target": "CWE-710",
        "view": "CWE-1000",
        "ordinal": "Primary",
    }


def test_objects_are_made_as_cwe_ones_are(local):
    objects = local_weaknesses.to_objects(local)
    party = {"id": "party:tmodel-test-fixture", "name": "tmodel test fixture"}
    assert objects["parties"] == [{**party, "party_kind": "organization"}]
    assert objects["weaknesses"][0] == {
        "id": "weakness:tr-weak-0001",
        "name": "Sample local weakness one",
        "description": local.weaknesses[0].description,
        "catalog_ref": "tr-weak-0001",
    }
    assert [p["id"] for p in objects["attack_patterns"]] == ["attack-pattern:capec-1"]
    assert [v["id"] for v in objects["vulnerabilities"]] == ["vulnerability:cve-0000-0000"]
    exploited, instance = objects["assertions"]
    assert (exploited["subject"], exploited["predicate"], exploited["object"]) == (
        "weakness:tr-weak-0001",
        "exploited_by",
        "attack-pattern:capec-1",
    )
    assert (instance["subject"], instance["predicate"], instance["object"]) == (
        "vulnerability:cve-0000-0000",
        "instance_of",
        "weakness:tr-weak-0002",
    )
    assert instance["evidence"] == ["https://example.org/not-a-real-advisory"]
    for assertion in objects["assertions"]:
        assert assertion["assertion_status"] == "proposed"  # nobody reviewed them (R-018)
        assert assertion["asserted_by"] == "party:tmodel-test-fixture"
        assert local.sha256 in assertion["generated_by"]
    assert local_weaknesses.to_objects(local, [2])["weaknesses"][0]["id"] == "weakness:tr-weak-0002"
    assert dict(local.objects) == {k: tuple(v) for k, v in objects.items()}


def test_cached_local_reloads_only_when_the_bytes_change(tmp_path):
    path = _written(tmp_path, MINIMAL)
    first = local_weaknesses.cached_local(path)
    assert local_weaknesses.cached_local(path) is first
    changed = copy.deepcopy(MINIMAL)
    changed["weaknesses"][0]["name"] = "One, renamed"
    _written(tmp_path, changed)
    again = local_weaknesses.cached_local(path)
    assert again is not first and again.weaknesses[0].name == "One, renamed"


def test_configured_file_reads_the_variable(monkeypatch):
    monkeypatch.delenv("TMODEL_LOCAL_WEAKNESSES", raising=False)
    assert local_weaknesses.configured_file() is None
    monkeypatch.setenv("TMODEL_LOCAL_WEAKNESSES", "  ")
    assert local_weaknesses.configured_file() is None
    monkeypatch.setenv("TMODEL_LOCAL_WEAKNESSES", "~/tr-weak.yaml")
    assert local_weaknesses.configured_file() == Path.home() / "tr-weak.yaml"


# --- what the reader refuses ---------------------------------------------------------------


def _change(path, value):
    """MINIMAL with the value at `path` (keys and list indexes) set, or removed when None."""
    doc = copy.deepcopy(MINIMAL)
    *parents, last = path
    holder = doc
    for key in parents:
        holder = holder[key]
    if value is None:
        del holder[last]
    else:
        holder[last] = value
    return doc


REL = {"nature": "ChildOf", "target": "CWE-710", "view": "CWE-1000"}


@pytest.mark.parametrize(
    "path, value, message",
    [
        (["extra"], "x", "the file: unknown key 'extra'; the keys are catalog, weaknesses"),
        (["catalog", "version"], None, "catalog: 'version' is missing"),
        (["catalog", "maintainer", "id"], "Team", "a party id looks like party:tmodel-team"),
        (["weaknesses"], "none", "weaknesses: expected a list"),
        (["weaknesses", 0, "Status"], "Draft", "tr-weak-0001: unknown key 'Status'"),
        (["weaknesses", 0, "name"], None, "tr-weak-0001: 'name' is missing"),
        (["weaknesses", 0, "name"], " ", "tr-weak-0001.name: expected a text"),
        (["weaknesses", 0, "id"], "TR-0001", "an id looks like tr-weak-0001, not 'TR-0001'"),
        (["weaknesses", 0, "id"], "TR-WEAK-0001", "an id looks like tr-weak-0001"),
        (["weaknesses", 1, "id"], "tr-weak-0001", "tr-weak-0001 given more than once"),
        (["weaknesses", 0, "status"], "Candidate", "'Candidate' is not one of Stable, Usable"),
        (["weaknesses", 0, "abstraction"], "Large", "'Large' is not one of Pillar, Class"),
        (["weaknesses", 0, "structure"], "Tree", "'Tree' is not one of Simple, Chain"),
        (["weaknesses", 0, "attack_patterns"], ["63"], "a CAPEC id looks like CAPEC-63"),
        (["weaknesses", 0, "extensions"], ["x"], "tr-weak-0001.extensions: expected a mapping"),
        (["weaknesses", 0, "relationships"], "ChildOf", ".relationships: expected a list"),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "nature": "HasMember"}],
            "'HasMember' is not one of ChildOf",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "target": "79"}],
            "expected a CWE-79 or tr-weak-0001 id, not '79'",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "target": "tr-weak-0009"}],
            "names the target tr-weak-0009, which is not a weakness in this file",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "target": "tr-weak-0001"}],
            "tr-weak-0001 cannot name itself",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "view": "Research Concepts"}],
            "a view id looks like CWE-1000, not 'Research Concepts'",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "ordinal": "Secondary"}],
            "'Secondary' is not one of Primary",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{**REL, "chain": "tr-weak-0007"}],
            "names the chain tr-weak-0007",
        ),
        (
            ["weaknesses", 0, "relationships"],
            [{"nature": "ChildOf", "target": "CWE-710"}],
            "'view' is missing",
        ),
        (
            ["weaknesses", 0, "observed_examples"],
            [{"reference": "CVE-0000-0000", "description": "d", "link": "ftp://x"}],
            "expected an http or https URL",
        ),
        (
            ["weaknesses", 0, "observed_examples"],
            [{"reference": "CVE-0000-0000"}],
            "'description' is missing",
        ),
    ],
)
def test_a_bad_entry_is_refused_with_where_it_is(tmp_path, path, value, message):
    with pytest.raises(LocalWeaknessError, match=message.replace("(", r"\(")) as err:
        local_weaknesses.load_local(_written(tmp_path, _change(path, value)))
    assert str(err.value).startswith("local.yaml: ")


@pytest.mark.parametrize(
    "text, message",
    [
        ("- a\n- b\n", "the file: expected a mapping"),
        ("catalog: [unclosed\n", "not valid YAML at line"),
        (
            "catalog: &c {name: n, version: '1', maintainer: {id: party:x, name: x}}\n"
            "weaknesses: [{id: tr-weak-0001, name: *c, description: d, status: Draft}]\n",
            "uses the alias \\*c; write the value out",
        ),
        (
            "catalog: {name: n, version: '1', maintainer: {id: party:x, name: x}}\n"
            "weaknesses:\n- id: tr-weak-0001\n  name: a\n  name: b\n  description: d\n"
            "  status: Draft\n",
            "the key 'name' is given twice",
        ),
    ],
    ids=["not a mapping", "bad YAML", "an alias", "a key twice"],
)
def test_what_a_hand_written_file_should_not_hold_is_refused(tmp_path, text, message):
    with pytest.raises(LocalWeaknessError, match=message):
        local_weaknesses.load_local(_written(tmp_path, text))


def test_a_file_that_is_not_utf8_is_refused(tmp_path):
    path = tmp_path / "local.yaml"
    path.write_bytes("catalog: café\n".encode("latin-1"))
    with pytest.raises(LocalWeaknessError, match="not UTF-8 text"):
        local_weaknesses.load_local(path)


def test_a_file_over_the_size_limit_is_refused_before_it_is_read(tmp_path, monkeypatch):
    monkeypatch.setattr(local_weaknesses, "MAX_FILE_BYTES", 16)
    with pytest.raises(LocalWeaknessError, match="larger than 16 bytes"):
        local_weaknesses.load_local(_written(tmp_path, MINIMAL))


def test_only_a_readable_regular_file_is_read(tmp_path):
    with pytest.raises(LocalWeaknessError, match="cannot read|not a regular file"):
        local_weaknesses.load_local(tmp_path)  # Python refuses a directory itself on some systems
    with pytest.raises(LocalWeaknessError, match="cannot read"):
        local_weaknesses.load_local(tmp_path / "missing.yaml")


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="no FIFOs on this platform")
def test_a_fifo_is_refused_without_waiting_for_a_writer(tmp_path):
    fifo = tmp_path / "fifo.yaml"
    os.mkfifo(fifo)
    with pytest.raises(LocalWeaknessError, match="not a regular file"):
        local_weaknesses.load_local(fifo)


# --- served beside CWE's -------------------------------------------------------------------


def test_the_table_lists_local_weaknesses_after_cwe_ones(served):
    payload = core.weakness_table()
    assert [r["id"] for r in payload["rows"]] == [*CWE_SAMPLE_IDS, "tr-weak-0001", "tr-weak-0002"]
    row = payload["rows"][-2]
    assert row["weakness"] == "weakness:tr-weak-0001" and row["url"] is None
    assert (row["usage"], row["likelihood"], row["mitigations"]) == (None, None, 0)
    assert list(row) == list(payload["rows"][0])  # the row's shape is #234's
    assert payload["total"] == 11 and payload["catalog"]["weaknesses"] == 9
    newest = core.weakness_table({"order": "desc", "limit": "2"})
    assert [r["id"] for r in newest["rows"]] == ["tr-weak-0002", "tr-weak-0001"]


def test_filters_search_and_facets_take_local_weaknesses_in(served, monkeypatch):
    found = core.weakness_table({"search": "sample local weakness"})
    assert [r["id"] for r in found["rows"]] == ["tr-weak-0001", "tr-weak-0002"]
    classes = core.weakness_table({"abstraction": "Class"})
    assert "tr-weak-0001" in [r["id"] for r in classes["rows"]]
    with_local = core.weakness_table()["facets"]
    monkeypatch.delenv("TMODEL_LOCAL_WEAKNESSES")
    cwe_only = core.weakness_table()["facets"]
    assert with_local["status"]["Draft"] == cwe_only["status"].get("Draft", 0) + 2
    assert with_local["abstraction"]["Class"] == cwe_only["abstraction"].get("Class", 0) + 1


def test_without_the_variable_nothing_local_is_served(served, monkeypatch):
    monkeypatch.delenv("TMODEL_LOCAL_WEAKNESSES")
    assert [r["id"] for r in core.weakness_table()["rows"]] == CWE_SAMPLE_IDS
    missing = core.weaknesses({"id": "tr-weak-0001"})
    assert (missing["local"], missing["entry"], missing["objects"]) == (None, None, None)


def test_one_local_entry_by_id(engine_url):
    one = core.weaknesses({"id": "tr-weak-0001"})
    assert (one["id"], one["entry"]["id"], one["entry"]["source"]) == (
        "tr-weak-0001",
        "tr-weak-0001",
        "local",
    )
    assert one["local"]["file"] == "tr-weak-sample.yaml"
    assert [w["id"] for w in one["objects"]["weaknesses"]] == ["weakness:tr-weak-0001"]
    assert [_relation(r) for r in one["entry"]["relationships"]] == [
        ("tr-weak-0001", "ChildOf", "CWE-710", "CWE-1000", False),
        ("tr-weak-0001", "CanPrecede", "tr-weak-0002", "CWE-1000", False),
    ]
    assert [_relation(r) for r in one["derived_relationships"]] == [
        ("tr-weak-0001", "ParentOf", "tr-weak-0002", "CWE-1000", True)
    ]
    assert core.weaknesses({"id": "TR-WEAK-0001"}) == one
    status, payload = api(engine_url, "/weaknesses", {"id": "tr-weak-0001"})
    assert status == 200 and payload == one
    missing = core.weaknesses({"id": "tr-weak-0099"})
    assert (missing["id"], missing["entry"], missing["objects"]) == ("tr-weak-0099", None, None)


def test_a_cwe_entry_shows_the_local_weaknesses_that_name_it(served):
    pillar = core.weaknesses({"id": "CWE-710"})
    assert ("CWE-710", "ParentOf", "tr-weak-0001", "CWE-1000", True) in [
        _relation(r) for r in pillar["derived_relationships"]
    ]
    category = core.weaknesses({"id": "CWE-411"})
    assert [_relation(r) for r in category["derived_relationships"]] == [
        ("CWE-411", "HasMember", "tr-weak-0002", "CWE-699", True)
    ]
    assert category["entry"]["source"] == "mitre-cwe"


def test_the_relationships_of_both_catalogs(engine_url):
    everything = core.weakness_relationships()
    assert (everything["total"], everything["count"]) == (46, 46)  # 24 written, 22 derived
    report = everything["report"]
    assert (report["stated"], report["derived"]) == (24, 22)
    targets = {r["target"] for r in report["targets_not_read"]}
    assert "CWE-74" in targets and not any(t.startswith("tr-weak-") for t in targets)
    assert everything["local"]["name"] == "tmodel local weakness sample"
    assert everything["query"] == {
        "views": None,
        "id": None,
        "derived": True,
        "limit": None,
        "offset": 0,
    }
    in_699 = core.weakness_relationships({"view": "CWE-699"})
    assert ("tr-weak-0002", "MemberOf", "CWE-411", "CWE-699", False) in [
        _relation(r) for r in in_699["relationships"]
    ]
    assert in_699["query"]["views"] == ["CWE-699"]
    two = core.weakness_relationships({"id": "tr-weak-0002"})
    assert [_relation(r) for r in two["relationships"]] == [
        ("tr-weak-0002", "ChildOf", "tr-weak-0001", "CWE-1000", False),
        ("tr-weak-0002", "MemberOf", "CWE-411", "CWE-699", False),
        ("tr-weak-0002", "CanFollow", "tr-weak-0001", "CWE-1000", True),
    ]
    stated = core.weakness_relationships({"derived": "false"})
    assert stated["total"] == 24 and not any(r["derived"] for r in stated["relationships"])
    page = core.weakness_relationships({"limit": "5", "offset": "44"})
    assert (page["total"], page["count"]) == (46, 2)
    assert page["relationships"] == everything["relationships"][44:]
    query = {"view": "CWE-1000,CWE-699", "id": "CWE-710"}
    status, payload = api(engine_url, "/weaknesses/relationships", query)
    assert status == 200 and payload == core.weakness_relationships(query)


@pytest.mark.parametrize(
    "query, message",
    [
        ({"view": "CWE-4242"}, "not a view this catalog knows: CWE-4242"),
        ({"view": "Research"}, "a view id looks like CWE-1000"),
        ({"derived": "maybe"}, "derived must be true or false, not 'maybe'"),
        ({"id": "XSS"}, "a CWE id looks like CWE-79"),
        ({"id": "XSS"}, "a local weakness id looks like tr-weak-0001"),
        ({"limit": "0"}, "limit"),
        ({"name": "x"}, "unknown parameter 'name'"),
    ],
)
def test_bad_relationship_queries_are_400(engine_url, query, message):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses/relationships", query)
    assert err.value.code == 400 and message in json.loads(err.value.read())["error"]


def test_an_unreadable_local_file_is_503_naming_the_variable(engine_url, monkeypatch, tmp_path):
    monkeypatch.setenv("TMODEL_LOCAL_WEAKNESSES", str(_written(tmp_path, "- not a catalog\n")))
    for path in ("/weaknesses/table", "/weaknesses/relationships"):
        with pytest.raises(urllib.error.HTTPError) as err:
            api(engine_url, path, {})
        body = json.loads(err.value.read())["error"]
        assert err.value.code == 503 and "TMODEL_LOCAL_WEAKNESSES" in body, path


# --- the CLI: same engine code ---------------------------------------------------------------


def test_cli_lists_relationships(served, capsys):
    argv = ["weaknesses", "--in-process", "--relationships", "--view", "CWE-699", "--stated-only"]
    assert main(argv) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == (
        "9 of 9 relationships in CWE-699 (CWE 4.20 and tmodel local weakness sample 0.1)"
    )
    assert out[1] == "  CWE-411 HasMember CWE-412 (CWE-699)"
    assert out[-1] == "  tr-weak-0002 MemberOf CWE-411 (CWE-699)"


def test_cli_shows_a_local_entry_with_its_relationships(served, capsys):
    assert main(["weaknesses", "--in-process", "--id", "tr-weak-0002"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "tr-weak-0002  Sample local weakness two",
        "  Weakness (Base); status Draft; usage none",
        "  0 CAPEC links, 1 observed examples, 0 mitigations",
        "  tr-weak-0002 ChildOf tr-weak-0001 (CWE-1000, Primary)",
        "  tr-weak-0002 MemberOf CWE-411 (CWE-699)",
        "  tr-weak-0002 CanFollow tr-weak-0001 (CWE-1000, derived)",
    ]
    assert main(["weaknesses", "--in-process", "--id", "tr-weak-0099"]) == 0
    assert capsys.readouterr().out == "tr-weak-0099: not in tmodel local weakness sample 0.1\n"


def test_cli_without_a_local_file_says_so(served, monkeypatch, capsys):
    monkeypatch.delenv("TMODEL_LOCAL_WEAKNESSES")
    assert main(["weaknesses", "--in-process", "--id", "tr-weak-0001"]) == 0
    assert capsys.readouterr().out == (
        "tr-weak-0001: not in any local file (TMODEL_LOCAL_WEAKNESSES is not set)\n"
    )


def test_cli_refuses_options_that_would_be_ignored(served, capsys):
    assert main(["weaknesses", "--in-process", "--relationships", "--status", "Draft"]) == 2
    assert "not the table's options (--status)" in capsys.readouterr().err
    assert main(["weaknesses", "--in-process", "--view", "CWE-1000"]) == 2
    assert "--view and --stated-only go with --relationships" in capsys.readouterr().err
    assert main(["weaknesses", "--in-process", "--stated-only"]) == 2
    capsys.readouterr()


def test_cli_json_is_the_engines_answer(served, capsys):
    argv = ["weaknesses", "--in-process", "--json", "--relationships", "--id", "CWE-79"]
    assert main(argv) == 0
    assert json.loads(capsys.readouterr().out) == core.weakness_relationships({"id": "CWE-79"})
