"""Real HTTP checks: writes are opt-in, authenticated, bounded and revision-scoped."""

import json
import threading
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import UTC

import pytest
from review_support import PRINCIPAL, MemoryWorkspace
from test_review_service import request, review

from engine.api.reviews import MAX_BODY, ReviewAPI
from engine.api.server import make_server
from engine.review_service import ReviewService

TOKEN = "fixture-session-token-" + "x" * 32


@contextmanager
def running(api=None):
    server = make_server("127.0.0.1", 0, review_api=api)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def api_server():
    ws = MemoryWorkspace()
    with running(ReviewAPI(ReviewService(ws), {TOKEN: PRINCIPAL})) as url:
        yield url, ws


def call(url, path, payload=None, headers=None, method="POST", raw=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        **(headers or {}),
    }
    data = raw if raw is not None else json.dumps(payload or {}).encode()
    req = urllib.request.Request(url + path, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read()
        return response.status, dict(response.headers), json.loads(body) if body else None


def test_default_server_remains_read_only():
    with running() as url:
        status, _, body = call(url, "/reviews/changes")
    assert status == 503
    assert body["error"]["code"] == "workspace_failure"


def test_context_combined_save_and_refresh(api_server):
    url, ws = api_server
    status, headers, context = call(
        url, "/reviews/context", request(ws), {"Origin": "tauri://localhost"}
    )
    assert status == 200
    assert headers["Access-Control-Allow-Origin"] == "tauri://localhost"
    assert context["reviewer_id"] == PRINCIPAL.party_id
    status, _, saved = call(
        url,
        "/reviews/changes",
        {
            **request(ws, True),
            "reviews": [review()],
            "feasibility": [{"attack_path_id": "path:a", "rating": "high"}],
        },
    )
    assert status == 200
    assert saved["revision"] == "r2"
    status, _, refreshed = call(url, "/reviews/refresh", request(ws))
    assert status == 200
    assert refreshed == saved


@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": ""},
        {"Authorization": "Bearer attacker-supplied"},
        {"Origin": "https://evil.example"},
        {"Host": "evil.example"},
    ],
)
def test_authentication_host_and_origin_are_enforced(api_server, headers):
    url, ws = api_server
    status, _, body = call(
        url, "/reviews/submit", {**request(ws, True), "reviews": [review()]}, headers
    )
    assert status == 403
    assert body["error"]["code"] == "permission_denied"
    assert ws.current == "r1"


@pytest.mark.parametrize(
    "raw", [b"[]", b'{"model_id":"a","model_id":"b"}', b'{"value":NaN}', b"{", b"\xff"]
)
def test_invalid_or_ambiguous_json_is_rejected(api_server, raw):
    url, ws = api_server
    status, _, body = call(url, "/reviews/changes", raw=raw)
    assert status == 422
    assert body["error"]["code"] == "validation_error"
    assert ws.current == "r1"


@pytest.mark.parametrize(
    "headers,raw",
    [
        ({"Content-Type": "text/plain"}, b"{}"),
        ({}, b" " * (MAX_BODY + 1)),
        ({"Transfer-Encoding": "chunked"}, b"{}"),
    ],
)
def test_invalid_framing_or_large_body_is_rejected(api_server, headers, raw):
    url, ws = api_server
    status, _, body = call(url, "/reviews/changes", raw=raw, headers=headers)
    assert status == 422
    assert body["error"]["code"] == "validation_error"
    assert ws.current == "r1"


def test_structured_revision_conflict_and_save_failure(api_server):
    url, ws = api_server
    stale = {**request(ws, True), "reviews": [review()]}
    assert (
        call(
            url,
            "/reviews/ratings",
            {**request(ws, True), "feasibility": [{"attack_path_id": "path:a", "rating": "high"}]},
        )[0]
        == 200
    )
    status, _, body = call(url, "/reviews/submit", stale)
    assert status == 409
    assert body["error"]["current_revision"] == "r2"
    ws.fail_save = True
    status, _, body = call(url, "/reviews/submit", {**request(ws, True), "reviews": [review()]})
    assert status == 503
    assert body["error"]["code"] == "save_failure"
    assert "private/path" not in json.dumps(body)
    assert ws.current == "r2"


def test_preflight_does_not_require_bearer_but_requires_local_origin(api_server):
    url, _ = api_server
    status, headers, _ = call(
        url,
        "/reviews/changes",
        headers={"Origin": "tauri://localhost", "Authorization": ""},
        method="OPTIONS",
    )
    assert status == 204
    assert headers["Access-Control-Allow-Methods"] == "POST"
    assert "Authorization" in headers["Access-Control-Allow-Headers"]
    assert (
        call(url, "/reviews/changes", headers={"Origin": "https://evil.example"}, method="OPTIONS")[
            0
        ]
        == 403
    )


def test_sessions_are_per_server_not_global():
    ws = MemoryWorkspace()
    with (
        running(ReviewAPI(ReviewService(ws), {TOKEN: PRINCIPAL})) as configured,
        running() as readonly,
    ):
        assert call(configured, "/reviews/context", request(ws))[0] == 200
        assert call(readonly, "/reviews/context", request(ws))[0] == 503


def test_weak_session_credentials_are_rejected():
    with pytest.raises(ValueError, match="credentials"):
        ReviewAPI(ReviewService(MemoryWorkspace()), {"short": PRINCIPAL})


def test_yaml_timestamps_are_json_safe_without_changing_provenance(api_server):
    from datetime import datetime

    url, ws = api_server
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    ws.versions["r1"]["assertions"][0]["asserted_at"] = timestamp
    status, _, context = call(url, "/reviews/context", request(ws))
    assert status == 200
    assert context["assertions"][0]["asserted_at"] == "2026-01-01T00:00:00+00:00"
    assert call(url, "/reviews/submit", {**request(ws, True), "reviews": [review()]})[0] == 200
    assert ws.versions["r2"]["assertions"][0]["asserted_at"] == timestamp
