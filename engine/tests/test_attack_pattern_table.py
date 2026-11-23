"""The attack-pattern feeds (#244, #236): GET /attack-patterns/table, GET /attack-patterns, and
the GUI's fixture.

The engine reads the CAPEC sample (`fixtures/capec/`, 13 attack patterns copied verbatim
from CAPEC 3.9) through TMODEL_CAPEC_CATALOG, with the digest a one-record test library
pins (TMODEL_LIBRARY). `apps/desktop/src/fixtures/attack-pattern-table.json` must equal
the engine's answer; TMODEL_UPDATE_FIXTURES=1 rewrites it after a shape change agreed
on #236.
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
CAPEC = TESTS / "fixtures" / "capec"
SAMPLE = CAPEC / "capec_v3.9-sample.xml"
GUI_FIXTURE = (
    TESTS.parents[1] / "apps" / "desktop" / "src" / "fixtures" / "attack-pattern-table.json"
)
ROW_KEYS = [
    "id",
    "attack_pattern",
    "name",
    "abstraction",
    "status",
    "likelihood",
    "severity",
    "description",
    "weaknesses",
    "attack_techniques",
    "related_attack_patterns",
    "steps",
    "mitigations",
    "examples",
    "url",
]
BY_NUMBER = [
    "CAPEC-5",
    "CAPEC-7",
    "CAPEC-23",
    "CAPEC-63",
    "CAPEC-66",
    "CAPEC-88",
    "CAPEC-115",
    "CAPEC-192",
    "CAPEC-273",
    "CAPEC-478",
    "CAPEC-497",
    "CAPEC-602",
    "CAPEC-701",
]


@pytest.fixture(autouse=True)
def capec_sample(monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(CAPEC / "library"))
    monkeypatch.setenv("TMODEL_CAPEC_CATALOG", str(SAMPLE))


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
    payload = core.attack_pattern_table()
    if os.environ.get("TMODEL_UPDATE_FIXTURES") == "1":
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        GUI_FIXTURE.write_text(text, encoding="utf-8")
    assert json.loads(GUI_FIXTURE.read_text(encoding="utf-8")) == payload, (
        "the attack-pattern feed changed: agree the new shape on #236, then regenerate the "
        "fixture with TMODEL_UPDATE_FIXTURES=1 pytest tests/test_attack_pattern_table.py"
    )


def test_row_shape():
    payload = core.attack_pattern_table()
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
    assert (catalog["name"], catalog["version"], catalog["schema"]) == ("CAPEC", "3.9", "3.5")
    assert (catalog["attack_patterns"], catalog["unknown_fields"]) == (13, 0)
    assert catalog["file"] == "capec_v3.9-sample.xml"  # a name, never a local path
    assert catalog["notice"].startswith("Copyright © 2007-2023, The MITRE Corporation.")
    assert catalog["license"].startswith("The MITRE Corporation (MITRE) hereby grants you")
    assert catalog["terms_url"] == "https://capec.mitre.org/about/termsofuse.html"
    for row in payload["rows"]:
        assert list(row) == ROW_KEYS
    sql = next(row for row in payload["rows"] if row["id"] == "CAPEC-66")
    assert sql["attack_pattern"] == "attack-pattern:capec-66"
    assert (sql["abstraction"], sql["status"], sql["likelihood"], sql["severity"]) == (
        "Standard",
        "Draft",
        "High",
        "High",
    )
    assert (sql["weaknesses"], sql["attack_techniques"]) == (["CWE-89", "CWE-1286"], [])
    assert (sql["related_attack_patterns"], sql["steps"], sql["mitigations"], sql["examples"]) == (
        1,
        4,
        3,
        1,
    )
    assert sql["url"] == "https://capec.mitre.org/data/definitions/66.html"


# --- parameters -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query, expected",
    [
        ({}, BY_NUMBER),
        ({"order": "desc"}, BY_NUMBER[::-1]),
        ({"status": "Deprecated"}, ["CAPEC-602"]),
        ({"abstraction": "Meta"}, ["CAPEC-115", "CAPEC-192", "CAPEC-602"]),
        ({"severity": "Very High"}, ["CAPEC-5", "CAPEC-23", "CAPEC-63"]),
        (
            {"abstraction": "Standard", "likelihood": "High"},
            ["CAPEC-23", "CAPEC-63", "CAPEC-66", "CAPEC-88", "CAPEC-497"],
        ),
        ({"search": "sql"}, ["CAPEC-7", "CAPEC-66"]),
        ({"search": "CWE-89"}, ["CAPEC-7", "CAPEC-66"]),  # a related weakness's id
        ({"search": "t1574"}, ["CAPEC-478"]),  # an ATT&CK technique's id
        ({"search": "HTTP Desync"}, ["CAPEC-273"]),  # an alternate term
        ({"search": "capec-115"}, ["CAPEC-115"]),
        ({"search": "nothing like this"}, []),
        (
            {"sort": "abstraction"},
            [
                "CAPEC-115",
                "CAPEC-192",
                "CAPEC-602",
                "CAPEC-23",
                "CAPEC-63",
                "CAPEC-66",
                "CAPEC-88",
                "CAPEC-497",
                "CAPEC-701",
                "CAPEC-5",
                "CAPEC-7",
                "CAPEC-273",
                "CAPEC-478",
            ],
        ),
        (
            {"sort": "severity"},
            [
                "CAPEC-5",
                "CAPEC-23",
                "CAPEC-63",
                "CAPEC-7",
                "CAPEC-66",
                "CAPEC-88",
                "CAPEC-273",
                "CAPEC-478",
                "CAPEC-701",
                "CAPEC-115",
                "CAPEC-192",
                "CAPEC-497",
                "CAPEC-602",
            ],
        ),
        ({"limit": "2", "offset": "1"}, ["CAPEC-7", "CAPEC-23"]),
    ],
)
def test_table_queries(query, expected):
    assert ids(core.attack_pattern_table(query)) == expected


def test_paging_reports_the_total_and_the_query():
    payload = core.attack_pattern_table({"limit": "4", "offset": "12", "sort": "name"})
    assert (payload["total"], payload["count"]) == (13, 1)
    assert payload["query"] == {
        "filters": {},
        "search": None,
        "sort": "name",
        "order": "asc",
        "limit": 4,
        "offset": 12,
    }


def test_an_attack_pattern_without_the_sort_field_comes_last_both_ways():
    asc = ids(core.attack_pattern_table({"sort": "likelihood"}))
    desc = ids(core.attack_pattern_table({"sort": "likelihood", "order": "desc"}))
    rated = [r["id"] for r in core.attack_pattern_table()["rows"] if r["likelihood"]]
    assert len(rated) == 11
    assert set(asc[: len(rated)]) == set(desc[: len(rated)]) == set(rated)
    assert asc[len(rated) :] == desc[len(rated) :] == ["CAPEC-115", "CAPEC-602"]


def test_facets_count_the_whole_catalog_and_contextual_ones_follow_the_query():
    payload = core.attack_pattern_table({"status": "Draft", "search": "e"})
    assert payload["facets"]["status"] == {
        "Deprecated": 1,
        "Draft": 8,
        "Obsolete": 1,
        "Stable": 2,
        "Usable": 1,
    }
    assert payload["facets"]["severity"] == {
        "High": 6,
        "Low": 1,
        "Medium": 1,
        "Very High": 3,
        "Very Low": 1,
    }
    contextual = payload["contextual_facets"]
    assert contextual["status"] == payload["facets"]["status"]  # its own filter is left out
    assert contextual["severity"] == {"High": 4, "Medium": 1, "Very High": 2, "Very Low": 1}


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
        core.attack_pattern_table(query)


@pytest.mark.parametrize("query", [{}, {"search": "injection", "sort": "severity", "limit": "3"}])
def test_api_matches_core(engine_url, query):
    status, payload = api(engine_url, "/attack-patterns/table", query)
    assert status == 200 and payload == core.attack_pattern_table(query)


def test_api_bad_parameters_are_400_with_a_message(engine_url):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/attack-patterns/table", {"sort": "weight"})
    assert err.value.code == 400
    assert "cannot sort by" in json.loads(err.value.read())["error"]


# --- no catalog to serve: 503, with what to do -----------------------------------------------


def test_no_catalog_configured_is_503_naming_the_file_to_get(engine_url, monkeypatch):
    monkeypatch.delenv("TMODEL_CAPEC_CATALOG")
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/attack-patterns/table", {})
    assert err.value.code == 503
    message = json.loads(err.value.read())["error"]
    assert "set TMODEL_CAPEC_CATALOG" in message and "0faa35f4" in message


def test_a_library_that_pins_no_release_is_503(engine_url, monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(TESTS / "fixtures" / "library"))  # no capec record
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/attack-patterns", {})
    assert err.value.code == 503
    assert "pins no CAPEC release" in json.loads(err.value.read())["error"]


def test_a_catalog_with_other_bytes_is_503(engine_url, monkeypatch, tmp_path):
    other = tmp_path / "capec.xml"
    other.write_bytes(SAMPLE.read_bytes().replace(b"SQL Injection", b"SQL injection", 1))
    monkeypatch.setenv("TMODEL_CAPEC_CATALOG", str(other))
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/attack-patterns/table", {})
    assert err.value.code == 503
    assert "is not the 0faa35f4" in json.loads(err.value.read())["error"]


# --- GET /attack-patterns: the import report, or one entry in full ------------------------------


def test_the_report_says_where_every_field_goes():
    payload = core.attack_patterns()
    assert list(payload) == ["catalog", "fields", "links", "objects"]
    assert all(row["known"] for row in payload["fields"])
    mapped = {
        r["field"]: r["maps_to"]
        for r in payload["fields"]
        if r["kind"] == "Attack_Pattern" and r["maps_to"]
    }
    assert mapped == {
        "@ID": "AttackPattern.id, AttackPattern.catalog_ref",
        "@Name": "AttackPattern.name",
        "Description": "AttackPattern.description",
        "Related_Weaknesses": "Assertion: Weakness exploited_by AttackPattern",
    }
    assert payload["objects"] == {
        "parties": 1,
        "attack_patterns": 13,
        "weaknesses": 19,
        "assertions": 25,
    }


def test_one_entry_by_id(engine_url):
    one = core.attack_patterns({"id": "CAPEC-66"})
    assert (one["id"], one["entry"]["id"], one["entry"]["kind"]) == (
        "CAPEC-66",
        "CAPEC-66",
        "Attack_Pattern",
    )
    assert one["entry"]["fields"]["@Name"] == one["entry"]["name"] == "SQL Injection"
    # Each cited reference resolved, for the details view (#236), not just its id.
    assert [(r["id"], r["resolved"], r["title"], r["section"]) for r in one["references"]] == [
        ("REF-607", True, "OWASP Web Security Testing Guide", "Testing for SQL Injection")
    ]
    assert list(one["references"][0]) == [
        "id",
        "section",
        "resolved",
        "title",
        "authors",
        "edition",
        "publication",
        "publisher",
        "year",
        "month",
        "day",
        "url",
        "url_date",
    ]
    assert [p["id"] for p in one["objects"]["attack_patterns"]] == ["attack-pattern:capec-66"]
    assert core.attack_patterns({"id": "66"}) == one
    status, payload = api(engine_url, "/attack-patterns", {"id": "capec-66"})
    assert status == 200 and payload == one


def test_a_category_has_no_objects_and_an_unknown_id_no_entry():
    category = core.attack_patterns({"id": "CAPEC-210"})
    assert (category["entry"]["kind"], category["objects"]) == ("Category", None)
    assert [r["id"] for r in core.attack_patterns({"id": "CAPEC-684"})["references"]] == ["REF-718"]
    missing = core.attack_patterns({"id": "CAPEC-99999"})
    assert (missing["id"], missing["entry"], missing["references"], missing["objects"]) == (
        "CAPEC-99999",
        None,
        None,
        None,
    )


@pytest.mark.parametrize(
    "query, message",
    [
        ({"id": "SQLi"}, "a CAPEC id looks like CAPEC-66"),
        ({"name": "x"}, "unknown parameter 'name'"),
    ],
)
def test_bad_attack_pattern_queries_are_400(engine_url, query, message):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, "/attack-patterns", query)
    assert err.value.code == 400 and message in json.loads(err.value.read())["error"]


# --- the CLI: same engine code ---------------------------------------------------------------


def test_cli_lists_the_table(capsys):
    assert main(["attack-patterns", "--in-process", "--abstraction", "Meta"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "3 of 3 matching attack patterns (CAPEC 3.9, 2023-01-24: 13 attack patterns)"
    assert [line.split()[0] for line in out[1:]] == ["CAPEC-115", "CAPEC-192", "CAPEC-602"]


def test_cli_shows_one_entry(capsys):
    assert main(["attack-patterns", "--in-process", "--id", "CAPEC-66"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "CAPEC-66  SQL Injection",
        "  Attack Pattern (Standard); status Draft; likelihood High; severity High",
        "  2 CWE links, 0 ATT&CK techniques, 4 attack steps, 3 mitigations",
        "  https://capec.mitre.org/data/definitions/66.html",
    ]


def test_cli_says_one_without_a_plural(capsys):
    assert main(["attack-patterns", "--in-process", "--id", "CAPEC-115"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[2] == "  1 CWE link, 1 ATT&CK technique, 0 attack steps, 0 mitigations"


def test_cli_refuses_table_options_with_id(capsys):
    assert main(["attack-patterns", "--in-process", "--id", "CAPEC-66", "--status", "Draft"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--id shows one entry and takes no table options (--status)" in captured.err


def test_cli_json_is_the_engines_answer(capsys):
    assert main(["attack-patterns", "--in-process", "--json", "--limit", "2"]) == 0
    assert json.loads(capsys.readouterr().out) == core.attack_pattern_table({"limit": "2"})


def test_cli_without_a_catalog_fails_with_a_message(capsys, monkeypatch):
    monkeypatch.delenv("TMODEL_CAPEC_CATALOG")
    assert main(["attack-patterns", "--in-process"]) == 1
    assert "set TMODEL_CAPEC_CATALOG" in capsys.readouterr().err
