"""The weakness feeds (#144, #58): GET /weaknesses/table, GET /weaknesses, and the GUI's fixture.

The engine reads the CWE sample (`fixtures/cwe/`, 9 weaknesses copied verbatim from
CWE 4.20) through TMODEL_CWE_CATALOG, with the digest a one-record test library pins
(TMODEL_LIBRARY). `apps/desktop/src/fixtures/weakness-table.json` must equal the
engine's answer; TMODEL_UPDATE_FIXTURES=1 rewrites it after a shape change agreed on
#58.
"""

import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from engine import core
from engine.api.server import make_server
from engine.cli import main

TESTS = Path(__file__).resolve().parent
CWE = TESTS / "fixtures" / "cwe"
SAMPLE = CWE / "cwec_v4.20-sample.xml"
GUI_FIXTURE = TESTS.parents[1] / "apps" / "desktop" / "src" / "fixtures" / "weakness-table.json"
ROW_KEYS = [
    "id",
    "weakness",
    "name",
    "abstraction",
    "structure",
    "status",
    "usage",
    "likelihood",
    "description",
    "attack_patterns",
    "observed_examples",
    "mitigations",
    "url",
]
BY_NUMBER = [
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


@pytest.fixture(autouse=True)
def cwe_sample(monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(CWE / "library"))
    monkeypatch.setenv("TMODEL_CWE_CATALOG", str(SAMPLE))


@pytest.fixture
def engine_url():
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


def ids(payload):
    return [row["id"] for row in payload["rows"]]


# --- the GUI's sample fixture ---------------------------------------------------------------


def test_gui_fixture_is_the_engines_answer():
    payload = core.weakness_table()
    if os.environ.get("TMODEL_UPDATE_FIXTURES") == "1":
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        GUI_FIXTURE.write_text(text, encoding="utf-8")
    assert json.loads(GUI_FIXTURE.read_text(encoding="utf-8")) == payload, (
        "the weakness feed changed: agree the new shape on #58, then regenerate the fixture "
        "with TMODEL_UPDATE_FIXTURES=1 pytest tests/test_weakness_table.py"
    )


def test_row_shape():
    payload = core.weakness_table()
    assert list(payload) == [
        "catalog",
        "query",
        "total",
        "count",
        "rows",
        "facets",
        "contextual_facets",
    ]
    catalog = payload["catalog"]
    assert (catalog["name"], catalog["version"], catalog["schema"]) == ("CWE", "4.20", "7.3")
    assert (catalog["weaknesses"], catalog["unknown_fields"]) == (9, 0)
    assert catalog["file"] == "cwec_v4.20-sample.xml"  # a name, never a local path
    assert catalog["notice"].startswith("Copyright © 2006-2026, The MITRE Corporation.")
    assert catalog["license"].startswith("CWE™ is free to use by any organization")
    assert catalog["terms_url"] == "https://cwe.mitre.org/about/termsofuse.html"
    for row in payload["rows"]:
        assert list(row) == ROW_KEYS
    xss = next(row for row in payload["rows"] if row["id"] == "CWE-79")
    assert xss["weakness"] == "weakness:cwe-79"
    assert (xss["abstraction"], xss["structure"], xss["status"], xss["usage"]) == (
        "Base",
        "Simple",
        "Stable",
        "Allowed",
    )
    assert (xss["attack_patterns"], xss["observed_examples"], xss["mitigations"]) == (6, 20, 12)
    assert xss["url"] == "https://cwe.mitre.org/data/definitions/79.html"


# --- parameters -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query, expected",
    [
        ({}, BY_NUMBER),
        ({"order": "desc"}, BY_NUMBER[::-1]),
        ({"status": "Deprecated"}, ["CWE-373", "CWE-769", "CWE-1187"]),
        ({"usage": "Allowed"}, ["CWE-79", "CWE-689", "CWE-1174"]),
        ({"abstraction": "Compound"}, ["CWE-689", "CWE-692"]),
        ({"structure": "Chain"}, ["CWE-692"]),
        ({"abstraction": "Base", "status": "Stable"}, ["CWE-79"]),
        ({"search": "XSS"}, ["CWE-79", "CWE-692"]),  # 79's alternate term, 692's description
        ({"search": "cwe-1093"}, ["CWE-1093"]),
        ({"search": "nothing like this"}, []),
        (
            {"sort": "abstraction"},
            [
                "CWE-710",
                "CWE-1093",
                "CWE-79",
                "CWE-373",
                "CWE-769",
                "CWE-1187",
                "CWE-1174",
                "CWE-689",
                "CWE-692",
            ],
        ),
        (
            {"sort": "status", "order": "desc"},
            [
                "CWE-373",
                "CWE-769",
                "CWE-1187",
                "CWE-710",
                "CWE-1093",
                "CWE-689",
                "CWE-692",
                "CWE-1174",
                "CWE-79",
            ],
        ),
        ({"limit": "2", "offset": "1"}, ["CWE-373", "CWE-689"]),
    ],
)
def test_table_queries(query, expected):
    assert ids(core.weakness_table(query)) == expected


def test_paging_reports_the_total_and_the_query():
    payload = core.weakness_table({"limit": "4", "offset": "8", "sort": "name"})
    assert (payload["total"], payload["count"]) == (9, 1)
    assert payload["query"] == {
        "filters": {},
        "search": None,
        "sort": "name",
        "order": "asc",
        "limit": 4,
        "offset": 8,
    }


def test_a_weakness_without_the_sort_field_comes_last_both_ways():
    asc = ids(core.weakness_table({"sort": "likelihood"}))
    desc = ids(core.weakness_table({"sort": "likelihood", "order": "desc"}))
    rated = [r["id"] for r in core.weakness_table()["rows"] if r["likelihood"]]
    assert set(asc[: len(rated)]) == set(desc[: len(rated)]) == set(rated)
    assert asc[len(rated) :] == desc[len(rated) :]  # unrated ones keep id order


def test_facets_count_the_whole_catalog_and_contextual_ones_follow_the_query():
    payload = core.weakness_table({"status": "Deprecated", "search": "e"})
    assert payload["facets"]["status"] == {
        "Deprecated": 3,
        "Draft": 3,
        "Incomplete": 2,
        "Stable": 1,
    }
    assert payload["facets"]["usage"] == {
        "Allowed": 3,
        "Allowed-with-Review": 1,
        "Discouraged": 2,
        "Prohibited": 3,
    }
    contextual = payload["contextual_facets"]
    assert contextual["status"] == payload["facets"]["status"]  # its own filter is left out
    assert contextual["usage"] == {"Prohibited": 3}


@pytest.mark.parametrize(
    "query, message",
    [
        ({"colour": "red"}, "unknown parameter 'colour'"),
        ({"status": ""}, "parameter 'status' needs a value"),
        ({"sort": "weight"}, "cannot sort by 'weight'"),
        ({"order": "up"}, "order must be asc or desc"),
        ({"limit": "0"}, "limit must be a whole number of at least 1"),
        ({"offset": "-1"}, "offset must be a whole number of at least 0"),
    ],
)
def test_core_rejects_bad_parameters(query, message):
    with pytest.raises(ValueError, match=message):
        core.weakness_table(query)


@pytest.mark.parametrize("query", [{}, {"search": "neutral", "sort": "name", "limit": "3"}])
def test_api_matches_core(engine_url, query):
    status, payload = api(engine_url, "/weaknesses/table", query)
    assert status == 200 and payload == core.weakness_table(query)


def test_api_bad_parameters_are_400_with_a_message(engine_url):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses/table", {"sort": "weight"})
    assert err.value.code == 400
    assert "cannot sort by" in json.loads(err.value.read())["error"]


# --- no catalog to serve: 503, with what to do -----------------------------------------------


def test_no_catalog_configured_is_503_naming_the_file_to_get(engine_url, monkeypatch):
    monkeypatch.delenv("TMODEL_CWE_CATALOG")
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses/table", {})
    assert err.value.code == 503
    message = json.loads(err.value.read())["error"]
    assert "set TMODEL_CWE_CATALOG" in message and "e26b565b" in message


def test_a_library_that_pins_no_release_is_503(engine_url, monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(TESTS / "fixtures" / "library"))  # cwe sha256 ""
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses", {})
    assert err.value.code == 503
    assert "pins no CWE release" in json.loads(err.value.read())["error"]


def test_a_catalog_with_other_bytes_is_503(engine_url, monkeypatch, tmp_path):
    other = tmp_path / "cwe.xml"
    other.write_bytes(SAMPLE.read_bytes().replace(b"Improper Neutral", b"Improper neutral", 1))
    monkeypatch.setenv("TMODEL_CWE_CATALOG", str(other))
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses/table", {})
    assert err.value.code == 503
    assert "is not the e26b565b" in json.loads(err.value.read())["error"]


# --- GET /weaknesses: the import report, or one entry in full ---------------------------------


def test_the_report_says_where_every_field_goes():
    payload = core.weaknesses()
    assert list(payload) == ["catalog", "fields", "links", "objects"]
    assert all(row["known"] for row in payload["fields"])
    mapped = {
        r["field"]: r["maps_to"]
        for r in payload["fields"]
        if r["kind"] == "Weakness" and r["maps_to"]
    }
    assert mapped == {
        "@ID": "Weakness.id, Weakness.catalog_ref",
        "@Name": "Weakness.name",
        "Description": "Weakness.description",
        "Observed_Examples": "Assertion: Vulnerability instance_of Weakness",
        "Related_Attack_Patterns": "Assertion: Weakness exploited_by AttackPattern",
    }
    assert payload["objects"] == {
        "parties": 1,
        "weaknesses": 9,
        "attack_patterns": 12,
        "vulnerabilities": 26,
        "assertions": 41,
    }


def test_one_entry_by_id(engine_url):
    one = core.weaknesses({"id": "CWE-79"})
    assert (one["id"], one["entry"]["id"], one["entry"]["kind"]) == ("CWE-79", "CWE-79", "Weakness")
    assert one["entry"]["fields"]["@Name"] == one["entry"]["name"]
    assert [w["id"] for w in one["objects"]["weaknesses"]] == ["weakness:cwe-79"]
    assert core.weaknesses({"id": "79"}) == one
    status, payload = api(engine_url, "/weaknesses", {"id": "cwe-79"})
    assert status == 200 and payload == one


def test_a_category_has_no_objects_and_an_unknown_id_no_entry():
    category = core.weaknesses({"id": "CWE-411"})
    assert (category["entry"]["kind"], category["objects"]) == ("Category", None)
    missing = core.weaknesses({"id": "CWE-99999"})
    assert (missing["id"], missing["entry"], missing["objects"]) == ("CWE-99999", None, None)


@pytest.mark.parametrize(
    "query, message",
    [({"id": "XSS"}, "a CWE id looks like CWE-79"), ({"name": "x"}, "unknown parameter 'name'")],
)
def test_bad_weakness_queries_are_400(engine_url, query, message):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/weaknesses", query)
    assert err.value.code == 400 and message in json.loads(err.value.read())["error"]


# --- the CLI: same engine code ---------------------------------------------------------------


def test_cli_lists_the_table(capsys):
    assert main(["weaknesses", "--in-process", "--status", "Deprecated"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "3 of 3 matching weaknesses (CWE 4.20, 2026-04-30: 9 weaknesses)"
    assert [line.split()[0] for line in out[1:]] == ["CWE-373", "CWE-769", "CWE-1187"]


def test_cli_shows_one_entry(capsys):
    assert main(["weaknesses", "--in-process", "--id", "CWE-79"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("CWE-79  Improper Neutralization of Input")
    assert out[1] == "  Weakness (Base/Simple); status Stable; usage Allowed"
    assert out[2] == "  6 CAPEC links, 20 observed examples, 12 mitigations"


def test_cli_json_is_the_engines_answer(capsys):
    assert main(["weaknesses", "--in-process", "--json", "--limit", "2"]) == 0
    assert json.loads(capsys.readouterr().out) == core.weakness_table({"limit": "2"})


def test_cli_without_a_catalog_fails_with_a_message(capsys, monkeypatch):
    monkeypatch.delenv("TMODEL_CWE_CATALOG")
    assert main(["weaknesses", "--in-process"]) == 1
    assert "set TMODEL_CWE_CATALOG" in capsys.readouterr().err
