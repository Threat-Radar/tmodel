"""The library table feed (#141, #58): its shape, its parameters, and the GUI's fixture.

The engine reads the fixture library (`fixtures/library/`, 12 real records) through
TMODEL_LIBRARY. `apps/desktop/src/fixtures/library-table.json` must equal the
engine's answer; TMODEL_UPDATE_FIXTURES=1 rewrites it after a shape change agreed
on #58.
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

TESTS = Path(__file__).resolve().parent
FIXTURES = TESTS / "fixtures" / "library"
GUI_FIXTURE = TESTS.parents[1] / "apps" / "desktop" / "src" / "fixtures" / "library-table.json"
ROW_KEYS = [
    "id",
    "title",
    "short_title",
    "type",
    "shelf",
    "status",
    "maturity",
    "date",
    "publisher",
    "topic",
    "tags",
    "url",
    "artifacts",
    "reviewed_artifacts",
    "profile",
]
ALL_IDS = [
    "benedetti-2024-sbom-python",
    "cwe",
    "draft-mih-scitt-agent-action-capsule",
    "ecma-424",
    "eo-14306",
    "gram",
    "rfc-8152",
    "rfc-8785",
    "rfc-9393",
    "sbomproof-2025",
    "sudokn-okn",
    "threattree-help",
]


@pytest.fixture(autouse=True)
def fixture_library(monkeypatch):
    monkeypatch.setenv("TMODEL_LIBRARY", str(FIXTURES))


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def api(base, query):
    url = f"{base}/library/table?" + urllib.parse.urlencode(query)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.status, json.loads(resp.read())


def ids(payload):
    return [row["id"] for row in payload["rows"]]


# --- the GUI's sample fixture ----------------------------------------------------


def test_gui_fixture_is_the_engines_answer():
    payload = core.library_table()
    if os.environ.get("TMODEL_UPDATE_FIXTURES") == "1":
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        GUI_FIXTURE.write_text(text, encoding="utf-8")
    assert json.loads(GUI_FIXTURE.read_text(encoding="utf-8")) == payload, (
        "the table feed changed: agree the new shape on #58, then regenerate the fixture "
        "with TMODEL_UPDATE_FIXTURES=1 pytest tests/test_library_table.py"
    )


def test_row_shape():
    payload = core.library_table()
    assert list(payload) == ["library", "query", "total", "count", "rows", "facets"]
    assert "root" not in payload["library"]  # no local path: the fixture is machine-independent
    for row in payload["rows"]:
        assert list(row) == ROW_KEYS
    rfc = next(row for row in payload["rows"] if row["id"] == "rfc-8785")
    assert (rfc["shelf"], rfc["artifacts"], rfc["reviewed_artifacts"]) == ("ietf", 7, 0)
    assert rfc["profile"] == "full"
    assert rfc["url"] == "https://www.rfc-editor.org/rfc/rfc8785.txt"


# --- parameters --------------------------------------------------------------------


@pytest.mark.parametrize(
    "query, expected",
    [
        ({}, ALL_IDS),
        ({"type": "rfc"}, ["rfc-8152", "rfc-8785", "rfc-9393"]),
        ({"search": "SBOM"}, ["benedetti-2024-sbom-python", "rfc-9393", "sbomproof-2025"]),
        ({"search": "sbom", "type": "paper"}, ["benedetti-2024-sbom-python", "sbomproof-2025"]),
        ({"search": "no such text"}, []),
        (
            {"sort": "date", "order": "desc"},
            [
                "draft-mih-scitt-agent-action-capsule",
                "sbomproof-2025",
                "eo-14306",
                "benedetti-2024-sbom-python",
                "rfc-9393",
                "rfc-8785",
                "rfc-8152",
                # no date: last, in id order
                "cwe",
                "ecma-424",
                "gram",
                "sudokn-okn",
                "threattree-help",
            ],
        ),
        (
            {"status": "stub", "sort": "date"},
            ["rfc-9393", "benedetti-2024-sbom-python", "sbomproof-2025", "ecma-424"],
        ),
        (
            {"sort": "topic", "order": "desc"},
            [
                "ecma-424",  # ties keep id order, even descending
                "eo-14306",
                "gram",
                "threattree-help",
                "benedetti-2024-sbom-python",
                "rfc-9393",
                "sbomproof-2025",
                "draft-mih-scitt-agent-action-capsule",
                "rfc-8152",
                "rfc-8785",
                "cwe",  # no topic: last in both orders
                "sudokn-okn",
            ],
        ),
        ({"sort": "shelf", "type": "rfc"}, ["rfc-8152", "rfc-8785", "rfc-9393"]),
        ({"limit": "5"}, ALL_IDS[:5]),
        ({"limit": "5", "offset": "10"}, ALL_IDS[10:]),
        ({"offset": "11"}, ALL_IDS[11:]),
    ],
)
def test_table_queries(query, expected):
    payload = core.library_table(query)
    assert ids(payload) == expected
    assert payload["count"] == len(expected)


def test_paging_reports_the_total_and_the_query():
    payload = core.library_table({"limit": "5", "offset": "10", "search": "e"})
    assert payload["total"] > payload["count"] == len(payload["rows"])
    assert payload["query"] == {
        "filters": {},
        "search": "e",
        "sort": "id",
        "order": "asc",
        "limit": 5,
        "offset": 10,
    }


def test_title_sort_ignores_case():
    titles = [row["title"].casefold() for row in core.library_table({"sort": "title"})["rows"]]
    assert titles == sorted(titles)


def test_facets_count_the_whole_library():
    expected = {
        "type": {
            "dataset": 1,
            "draft": 1,
            "paper": 2,
            "repo": 1,
            "rfc": 3,
            "spec": 2,
            "web": 2,
        },
        "status": {"distilled": 1, "fetched": 2, "stub": 4, "summarized": 5},
        "topic": {
            "canonical-encoding": 1,
            "cbor-implementation": 1,
            "predicate-rendering": 1,
            "product-composition": 3,
            "rpt-0003-threat-modeling-products": 2,
            "supply-chain-attestation": 2,
        },
    }
    assert core.library_table()["facets"] == expected
    assert core.library_table({"type": "rfc", "search": "x"})["facets"] == expected


BAD = [
    ({"kind": "rfc"}, "unknown parameter 'kind': use id, type, topic, status, search, sort"),
    ({"sort": "pages"}, "cannot sort by 'pages': use one of id, title, type, shelf"),
    ({"order": "up"}, "order must be asc or desc, not 'up'"),
    ({"limit": "0"}, "limit must be a whole number of at least 1, not '0'"),
    ({"limit": "ten"}, "limit must be a whole number of at least 1, not 'ten'"),
    ({"limit": "²"}, "limit must be a whole number of at least 1"),
    ({"offset": "-1"}, "offset must be a whole number of at least 0, not '-1'"),
    ({"search": " "}, "parameter 'search' needs a value"),
]


@pytest.mark.parametrize("query, message", BAD)
def test_core_rejects_bad_parameters(query, message):
    with pytest.raises(ValueError) as caught:
        core.library_table(query)
    assert message in str(caught.value)


# --- local API -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [{}, {"type": "rfc"}, {"search": "sbom", "sort": "date", "order": "desc"}, {"limit": "3"}],
)
def test_api_matches_core(engine_url, query):
    status, body = api(engine_url, query)
    assert status == 200
    assert body == core.library_table(query)


@pytest.mark.parametrize("query, message", BAD)
def test_api_bad_parameters_are_400_with_a_message(engine_url, query, message):
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, query)
    assert err.value.code == 400
    assert message in json.loads(err.value.read())["error"]


def test_api_without_a_library_is_503(engine_url, monkeypatch, tmp_path):
    monkeypatch.setenv("TMODEL_LIBRARY", str(tmp_path))
    with pytest.raises(urllib.error.HTTPError) as err:
        api(engine_url, {})
    assert err.value.code == 503


# --- one record by id, for a details view ---------------------------------------------


def test_one_record_by_id(engine_url):
    one = core.library_records({"id": "rfc-8785"})
    assert one["count"] == 1 and one["records"][0]["id"] == "rfc-8785"
    assert core.library_records({"id": "no-such-record"})["count"] == 0
    url = f"{engine_url}/library?id=rfc-8785"
    with urllib.request.urlopen(url, timeout=30) as resp:
        assert json.loads(resp.read()) == one
