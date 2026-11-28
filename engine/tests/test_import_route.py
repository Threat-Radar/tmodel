"""The Import New Product route (#287): `POST /import/sbom` on a real local server."""

from __future__ import annotations

import base64
import hashlib
import json
import socket
import struct
import tempfile
import threading
import time
import tracemalloc
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml

from engine import import_sbom
from engine.api import import_route, server
from engine.api.server import EngineHandler, make_server

FIXTURES = Path(__file__).parent / "fixtures" / "sbom-import"
SBOM = FIXTURES / "alpine-3.24.2.cdx.json"
SCAN = FIXTURES / "alpine-3.24.2.grype.json"
ORIGIN = "tauri://localhost"
TINY = {"sbom": {"name": "a.json", "base64": "e30="}}  # `{}`, refused by the importer


def serve(import_enabled: bool):
    httpd = make_server("127.0.0.1", 0, import_enabled=import_enabled)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


@pytest.fixture
def enabled():
    httpd, base = serve(True)
    yield base
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def disabled():
    httpd, base = serve(False)
    yield base
    httpd.shutdown()
    httpd.server_close()


def post(base, payload, *, path=import_route.PATH, headers=None, raw=None):
    body = raw if raw is not None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, dict(response.headers), json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), json.loads(exc.read())


def encoded(path: Path, name: str | None = None) -> dict[str, str]:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"name": path.name if name is None else name, "base64": data}


def upload(platform="linux/arm64/v8", scan=True):
    return {
        "sbom": encoded(SBOM),
        "scan": encoded(SCAN) if scan else None,
        "platform": platform,
    }


def error(body):
    return body["error"]["code"], body["error"]["message"]


def test_the_route_is_off_unless_the_host_enables_it(disabled):
    status, _, body = post(disabled, upload())
    assert status == 503 and error(body)[0] == "not_enabled"


def test_an_import_answers_with_what_the_command_line_writes(enabled):
    status, headers, body = post(enabled, upload(), headers={"Origin": ORIGIN})
    assert status == 200
    expected = import_sbom.build(
        SBOM, scan=SCAN, platform="linux/arm64/v8", output_name="original.yaml"
    )
    assert body["model_text"] == expected.model_text  # byte for byte, header included
    assert body["report_text"] == expected.report_text
    assert body["warnings"] == []
    assert body["counts"] == expected.counts
    assert body["counts"]["components"] == 17 and body["counts"]["vulnerabilities"] == 15
    assert body["platform"] == "linux/arm64/v8"
    assert body["product"] == "index.docker.io/library/alpine"
    assert body["suggested_name"] == "alpine"
    assert headers["Access-Control-Allow-Origin"] == ORIGIN
    assert "original.yaml" in body["model_text"]  # the project's file, in the header
    yaml.safe_load(body["model_text"])  # the model reads back


def test_the_model_records_the_files_own_digests(enabled):
    status, _, body = post(enabled, upload())
    assert status == 200
    for path in (SBOM, SCAN):
        assert hashlib.sha256(path.read_bytes()).hexdigest() in body["model_text"]


def test_a_warning_comes_back_with_the_model(enabled):
    status, _, body = post(enabled, upload(platform="linux/amd64"))
    assert status == 200
    (warning,) = body["warnings"]
    assert "built for arm64" in warning and "--platform linux/arm64/v8" in warning


def test_a_refused_import_names_the_reason(enabled):
    status, _, body = post(enabled, upload(platform="linux/arm64/v8-1"))
    assert status == 422 and error(body)[0] == "import_refused"
    assert "v8-1" in error(body)[1]


@pytest.mark.parametrize("platform", [None, ""])
def test_without_a_platform_the_import_asks_for_one(enabled, platform):
    status, _, body = post(enabled, upload(platform=platform))
    assert status == 422 and error(body)[0] == "import_refused"
    assert "--platform" in error(body)[1]


def test_an_sbom_alone_imports_without_vulnerabilities(enabled):
    status, _, body = post(enabled, upload(scan=False))
    assert status == 200
    assert body["counts"]["components"] == 17 and body["counts"]["vulnerabilities"] == 0


@pytest.mark.parametrize(("scan", "total"), [(True, 45), (False, 0)])
def test_the_counts_give_every_assertion_and_both_kinds(enabled, scan, total):
    # The Import New Product screen shows counts.assertions (#296); kriishnaa-18's review.
    status, _, body = post(enabled, upload(scan=scan))
    assert status == 200
    counts = body["counts"]
    assert counts["assertions"] == total
    assert counts["assertions"] == counts["match_assertions"] + counts["cwe_assertions"]
    assert len(yaml.safe_load(body["model_text"]).get("assertions", [])) == total


@pytest.mark.parametrize(
    ("payload", "message", "field"),
    [
        ([], "must be a JSON object", None),
        ({}, "Provide the SBOM file", "sbom"),
        ({"sbom": "text"}, "its name and its bytes in base64", "sbom"),
        ({"sbom": {"name": "a.json", "text": "{}"}}, "its name and its bytes in base64", "sbom"),
        ({"sbom": {"name": 5, "base64": "e30="}}, "its name and its bytes in base64", "sbom"),
        ({"sbom": {"name": "a.json", "base64": ""}}, "is empty", "sbom"),
        ({"sbom": {"name": "a.json", "base64": "@@@@"}}, "base64 is not valid", "sbom"),
        ({"sbom": {"name": "a.json", "base64": "ZT\u00e9="}}, "base64 is not valid", "sbom"),
        ({**TINY, "scan": {"base64": "e30"}}, "base64 is not valid", "scan"),
        ({**TINY, "platform": 5}, "platform must be text", "platform"),
        ({**TINY, "project": "x"}, "Unknown field 'project'", None),
    ],
)
def test_a_malformed_request_is_refused(enabled, payload, message, field):
    status, _, body = post(enabled, payload)
    assert status == 422 and error(body)[0] == "validation_error"
    assert message in error(body)[1]
    assert body["error"].get("fields", [{}])[0].get("field") == field


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (b"not json", "is not JSON"),
        (b'{"sbom": {"base64": "e30="}, "platform": NaN}', "is not JSON"),
        (b'{"sbom": {"base64": "e30="}, "sbom": {"base64": "e30="}}', "'sbom' appears twice"),
        (b"[" * 100_000 + b"]" * 100_000, "Send only the SBOM"),
        (b'{"sbom": {"base64": "e30="}, "platform": [' + b"0.0," * 1000 + b"0.0]}", "Send only"),
        (
            b'{"sbom": {"base64": "e30="}, "x": ' + b"[[]," * 50 + b"[]" + b"]" * 50 + b"}",
            "Send only",
        ),
    ],
)
def test_a_body_that_is_not_the_envelope_is_refused(enabled, raw, message):
    status, _, body = post(enabled, None, raw=raw)
    assert status == 422 and error(body)[0] == "validation_error"
    assert message in error(body)[1]


def test_only_json_is_accepted(enabled):
    status, _, body = post(enabled, TINY, headers={"Content-Type": "text/plain"})
    assert status == 422 and error(body)[0] == "validation_error"


def test_files_over_the_limit_are_refused(enabled, monkeypatch):
    monkeypatch.setattr(import_route, "_MAX_ENCODED", 1024)
    status, _, body = post(enabled, upload())
    assert status == 422 and "larger than" in error(body)[1]
    assert body["error"]["fields"][0]["field"] == "sbom"
    monkeypatch.setattr(import_route, "MAX_BODY_BYTES", 10)  # refused before it is read
    status, _, body = post(enabled, TINY)
    assert status == 422 and "too large" in error(body)[1]


@pytest.mark.parametrize("extra", [1, 2, 3])
def test_a_file_just_over_the_limit_is_refused_alike(enabled, monkeypatch, extra):
    # base64 rounds up to four characters, so the bytes are checked as well as the text.
    monkeypatch.setattr(import_route, "MAX_FILE_BYTES", 31)
    monkeypatch.setattr(import_route, "_MAX_ENCODED", 44)
    data = base64.b64encode(b" " * (31 + extra)).decode("ascii")
    status, _, body = post(enabled, {"sbom": {"name": "a.json", "base64": data}})
    assert status == 422 and error(body)[0] == "validation_error"
    assert body["error"]["fields"][0]["field"] == "sbom"


def test_a_name_full_of_brackets_and_commas_still_imports(enabled):
    payload = upload()
    payload["sbom"]["name"] = "sbom" + "[" * 20 + ", final, v2.json"
    status, _, body = post(enabled, payload)
    assert status == 200 and body["counts"]["components"] == 17


def test_names_with_more_commas_than_the_limit_still_import(enabled):
    # kriishnaa-18's review: a name with 62 commas was refused, as the count took in
    # strings. Only brackets and commas outside strings count now.
    payload = upload()
    payload["sbom"]["name"] = "sbom" + "," * 62 + ".json"
    payload["scan"]["name"] = "scan" + '{[,\\"' * 40 + ".json"
    assert import_route.structure(json.dumps(payload)) <= import_route.MAX_STRUCTURE
    status, _, body = post(enabled, payload)
    assert status == 200 and body["counts"]["components"] == 17


@pytest.mark.parametrize(
    ("text", "count"),
    [
        ('{"a": "x,y[", "b": [1, 2]}', 4),
        (r'{"a": "q\"[,", "b": {}}', 3),  # an escaped quote does not end the string
        (r'{"a": "\\", "b": [1, 2]}', 4),  # an escaped backslash does not escape the quote
        (r'{"a": "\u0022,[", "b": 1}', 2),
        ('{"a": "no end, [[[', 1),  # parsing stops at a string with no end
    ],
)
def test_the_structure_count_reads_strings_as_parsing_does(text, count):
    assert import_route.structure(text) == count


def test_structure_after_a_string_with_escaped_quotes_still_counts(enabled):
    raw = b'{"sbom": {"name": "a\\",", "base64": "e30="}, "x": [' + b"0," * 100 + b"0]}"
    status, _, body = post(enabled, None, raw=raw)
    assert status == 422 and "Send only" in error(body)[1]


@pytest.mark.parametrize(
    "raw", [b'"' + b'\\"' * 2_000_000, b'"' * 4_000_000], ids=["escaped", "bare"]
)
def test_a_body_of_quotes_is_refused_before_strings_are_looked_for(enabled, raw):
    status, _, body = post(enabled, None, raw=raw)
    assert status == 422 and "Send only" in error(body)[1]


@pytest.mark.parametrize(
    "text",
    ['"' + '\\"' * 500_000, '"' + "\\\\" * 500_000, '{"a": "' + "\\n" * 500_000 + '"}'],
    ids=["escaped quotes", "escaped backslashes", "other escapes"],
)
def test_the_structure_count_keeps_its_memory_flat(text):
    # The second Claude Code review: a pattern that could backtrack kept about 90 bytes
    # for each byte of escapes (97 MB on this 1 MB), which at 179 MB would freeze a Mac.
    tracemalloc.start()
    try:
        import_route.structure(text)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert peak < len(text)


@pytest.mark.parametrize("encoding", ["utf-16", "utf-32"])
def test_only_utf_8_is_read(enabled, encoding):
    # json reads UTF-16 and UTF-32 as well, but the structure count reads UTF-8 only.
    status, _, body = post(enabled, None, raw=json.dumps(TINY).encode(encoding))
    assert status == 422 and error(body)[0] == "validation_error"
    assert "must be JSON in UTF-8" in error(body)[1]


def test_a_byte_order_mark_is_read_past(enabled):
    status, _, body = post(enabled, None, raw=b"\xef\xbb\xbf" + json.dumps(upload()).encode())
    assert status == 200 and body["counts"]["components"] == 17


def test_a_foreign_host_or_origin_is_refused(enabled):
    status, _, body = post(enabled, TINY, headers={"Host": "attacker.example"})
    assert status == 403 and error(body)[0] == "permission_denied"
    status, headers, body = post(enabled, TINY, headers={"Origin": "https://attacker.example"})
    assert status == 403 and error(body)[0] == "permission_denied"
    assert "Access-Control-Allow-Origin" not in headers


def test_a_header_carries_the_engines_own_origin_string():
    # CodeQL's response splitting check: an allowed origin is answered with the module's
    # own string, an equal one, so no text from the request reaches a header.
    for origin in server.ALLOWED_ORIGINS:
        sent = origin.encode().decode()
        assert sent == origin and sent is not origin
        assert server.allowed_origin(sent) is origin
    for other in (None, "", "https://attacker.example", "tauri://localhost\r\nX-Injected: 1"):
        assert server.allowed_origin(other) is None


def test_an_unknown_operation_is_not_found(enabled):
    status, _, body = post(enabled, TINY, path="/import/other")
    assert status == 404 and error(body)[0] == "not_found"


def preflight(base, origin, path=import_route.PATH):
    request = urllib.request.Request(
        base + path,
        method="OPTIONS",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers)


def test_the_preflight_lets_the_app_read_why_importing_is_off(enabled, disabled):
    for base in (enabled, disabled):
        status, headers = preflight(base, ORIGIN)
        assert status == 204
        assert headers["Access-Control-Allow-Origin"] == ORIGIN
        assert headers["Access-Control-Allow-Methods"] == "POST"
        assert headers["Access-Control-Allow-Headers"] == "Content-Type"
    assert preflight(enabled, "https://attacker.example")[0] == 403
    assert preflight(enabled, ORIGIN, path="/import/other")[0] == 403
    # After the preflight, the app can read the refusal, so it can say why.
    status, headers, body = post(disabled, TINY, headers={"Origin": ORIGIN})
    assert status == 503 and error(body)[0] == "not_enabled"
    assert headers["Access-Control-Allow-Origin"] == ORIGIN


def test_file_names_lose_their_folders_and_no_path_comes_back(enabled):
    payload = upload()
    payload["sbom"]["name"] = "../../Users/someone/secret folder/my sbom.cdx.json"
    payload["scan"]["name"] = "C:\\Users\\someone\\scan.json"
    status, _, body = post(enabled, payload)
    assert status == 200
    text = json.dumps(body)
    assert "Users" not in text and "someone" not in text and ".." not in body["model_text"]
    assert "my-sbom.cdx.json" in body["model_text"]  # the base name, made safe


@pytest.mark.parametrize(("sbom", "scan"), [("Alpine.json", "alpine.json"), ("a.json", "a.json")])
def test_two_files_are_read_whatever_their_names(enabled, sbom, scan):
    # Names that differ only in case, or not at all, are one file on a Mac's disk; the route
    # never writes them to disk, so each is read as sent.
    payload = {**upload(), "sbom": encoded(SBOM, sbom), "scan": encoded(SCAN, scan)}
    status, _, body = post(enabled, payload)
    assert status == 200 and body["counts"]["vulnerabilities"] == 15


def test_nothing_is_read_from_or_written_to_disk(enabled, monkeypatch):
    def refuse(*_args, **_kwargs):
        raise AssertionError("the route touched the disk")

    monkeypatch.setattr(import_sbom, "_read", refuse)  # how the importer reads a path
    for name in ("mkdtemp", "mkstemp", "NamedTemporaryFile", "TemporaryDirectory"):
        monkeypatch.setattr(tempfile, name, refuse)
    status, _, body = post(enabled, upload())
    assert status == 200 and body["counts"]["vulnerabilities"] == 15


def test_imports_run_one_at_a_time(enabled, monkeypatch):
    # A second import waits for the first; one that waits too long is told to try again.
    results = []

    def one():
        status, _, body = post(enabled, upload())
        results.append((status, body.get("model_text")))

    threads = [threading.Thread(target=one) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(120)
    assert [status for status, _ in results] == [200, 200, 200]
    assert len({text for _, text in results}) == 1
    monkeypatch.setattr(import_route, "WAIT_SECONDS", 0.2)
    with import_route._SLOT:
        status, _, body = post(enabled, TINY)
    assert status == 503 and error(body)[0] == "busy"


BIG = {"sbom": {"name": "big.json", "base64": base64.b64encode(b" " * 2_000_000).decode("ascii")}}


def test_a_refusal_reaches_a_client_still_sending_a_large_body(enabled, disabled, monkeypatch):
    # The body is read and discarded first, so the client sees the refusal, not a reset.
    status, _, body = post(disabled, BIG, headers={"Origin": ORIGIN})
    assert status == 503 and error(body)[0] == "not_enabled"
    status, _, body = post(enabled, BIG, headers={"Content-Type": "text/plain"})
    assert status == 422 and error(body)[0] == "validation_error"
    monkeypatch.setattr(import_route, "WAIT_SECONDS", 0.2)
    with import_route._SLOT:
        status, _, body = post(enabled, BIG)
    assert status == 503 and error(body)[0] == "busy"
    assert post(enabled, TINY)[0] == 422  # the slot is free again


class _Connection:
    def __init__(self):
        self.timeouts = []

    def settimeout(self, value):
        self.timeouts.append(value)


class _Trickle:
    """A body arriving one byte per read, each read taking `step` seconds of a fake clock."""

    def __init__(self, clock, step, stall=False):
        self.clock, self.step, self.stall = clock, step, stall

    def read1(self, _n):
        if self.stall:
            raise TimeoutError
        self.clock[0] += self.step
        return b" "


def handler(rfile):
    h = EngineHandler.__new__(EngineHandler)
    h.connection, h.rfile = _Connection(), rfile
    return h


def test_the_whole_body_must_arrive_by_the_deadline(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(server.time, "monotonic", lambda: clock[0])
    h = handler(_Trickle(clock, step=0.4))  # every read is quick; the whole body is not
    with pytest.raises(import_route.ImportRouteError) as refused:
        h._read_body(100, 1)
    assert refused.value.status == 408 and refused.value.code == "request_timeout"
    assert clock[0] < 1.5  # cut off at the deadline, not a timeout after each read
    assert h.connection.timeouts[-1] == 1  # restored for sending the answer
    stalled = handler(_Trickle(clock, step=0, stall=True))
    with pytest.raises(import_route.ImportRouteError) as refused:
        stalled._read_body(100, 1)
    assert refused.value.status == 408
    assert handler(_Trickle(clock, step=0.1))._read_body(3, 1) == b"   "


def test_a_stalled_client_is_answered(enabled, monkeypatch):
    monkeypatch.setattr(import_route, "READ_SECONDS", 1)
    url = urlsplit(enabled)
    with socket.create_connection((url.hostname, url.port), timeout=10) as sock:
        sock.sendall(
            b"POST /import/sbom HTTP/1.1\r\nHost: 127.0.0.1\r\n"
            b"Content-Type: application/json\r\nContent-Length: 100\r\n\r\n{"
        )
        started = time.monotonic()
        answer = b""
        while chunk := sock.recv(65536):
            answer += chunk
    assert answer.split(b"\r\n", 1)[0].endswith(b"408 Request Timeout")
    assert b'"request_timeout"' in answer
    assert time.monotonic() - started < 5


def test_an_unexpected_failure_names_no_path(enabled, monkeypatch):
    def broken(*_args, **_kwargs):
        raise OSError("/private/tmp/somewhere: disk full")

    monkeypatch.setattr(import_route.import_sbom, "build", broken)
    status, _, body = post(enabled, upload())
    assert status == 500 and error(body)[0] == "internal_error"
    assert "/private" not in json.dumps(body)


# Beside #288's project routes (#298), now on main -----------------------------------------


def test_the_import_route_answers_beside_the_project_routes(monkeypatch, tmp_path):
    # serve() puts #288's workspace routes in front of this handler, and they pass every
    # other path on, so the import, its preflight and the project routes all answer.
    from workspace_support import EXAMPLE, TOKEN, Clock, Tokens, projects, use_examples

    from engine.api.workspace import install_workspace_routes
    from engine.model_workspace import ProjectWorkspace

    use_examples(monkeypatch, tmp_path)
    workspace = ProjectWorkspace(schema_check=False, clock=Clock(), token=Tokens())
    workspace.create_project(projects(tmp_path) / "Project", source_file=EXAMPLE)
    httpd = make_server("127.0.0.1", 0, import_enabled=True)
    install_workspace_routes(httpd, workspace, TOKEN)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        status, headers, body = post(base, upload(), headers={"Origin": ORIGIN})
        assert status == 200 and body["counts"]["components"] == 17
        assert headers["Access-Control-Allow-Origin"] == ORIGIN
        status, headers = preflight(base, ORIGIN)
        assert status == 204 and headers["Access-Control-Allow-Headers"] == "Content-Type"
        listed = urllib.request.Request(
            base + "/workspace/models", headers={"Authorization": f"Bearer {TOKEN}"}
        )
        with urllib.request.urlopen(listed, timeout=10) as response:
            assert response.status == 200 and json.loads(response.read())["count"] == 1
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        ([], {"import_enabled": False, "host_token": None}),
        (["--enable-import"], {"import_enabled": True, "host_token": None}),
        (["--enable-import", "--projects"], {"import_enabled": True, "host_token": "secret"}),
    ],
)
def test_the_serve_command_passes_both_switches(monkeypatch, argv, expected):
    from engine import cli

    token = "test-host-token-" + "x" * 32  # a test secret, not a credential
    seen = {}
    monkeypatch.setattr(server, "serve", lambda **kwargs: seen.update(kwargs))
    monkeypatch.setenv("TMODEL_HOST_TOKEN", token)
    assert cli.main(["serve", *argv]) == 0
    if expected["host_token"] == "secret":
        expected = {**expected, "host_token": token}
    assert {key: seen[key] for key in expected} == expected


def test_the_workspace_routes_share_no_helper_with_this_handler():
    # The workspace routes sit in front of this handler in one class, so a private helper
    # of theirs with the same name would replace this one: on b38074f both had a
    # `_read_body`, with different arguments, and every import failed with 500 once
    # project folders were on. Only the request methods they pass on may be shared.
    from engine.api.workspace import WorkspaceRoutes

    def names(cls):
        return {name for name in vars(cls) if not name.startswith("__")}

    ours = set().union(
        *(names(cls) for cls in EngineHandler.__mro__ if cls.__module__.startswith("engine."))
    )
    assert names(WorkspaceRoutes) & ours == {"do_GET", "do_POST", "do_OPTIONS"}


def reset_server(route: str):
    """A server for the reset test, and the request head and the part of a body to send."""
    if route == "import":
        httpd = make_server("127.0.0.1", 0, import_enabled=True)
        head = f"POST {import_route.PATH} HTTP/1.1\r\nContent-Length: 1000000\r\n"
        return httpd, head, b"{" * 1000
    from workspace_support import TOKEN, Clock, Tokens

    from engine.api.workspace import install_workspace_routes
    from engine.model_workspace import ProjectWorkspace

    httpd = make_server("127.0.0.1", 0)
    workspace = ProjectWorkspace(schema_check=False, clock=Clock(), token=Tokens())
    install_workspace_routes(httpd, workspace, TOKEN)
    head = (
        "POST /workspace/host/open-file HTTP/1.1\r\n"
        f"Authorization: Bearer {TOKEN}\r\nContent-Length: 5000\r\n"
    )
    return httpd, head, b"{" * 100


@pytest.mark.parametrize("route", ["import", "workspace"])
def test_a_client_that_resets_part_way_through_its_body_is_let_go_quietly(route):
    # On d4fb812 the engine answered into the closed connection, which raised again and
    # printed a traceback: the import route with a 500, the workspace routes with a 400.
    # Now the connection ends quietly, and the one-import slot is free.
    httpd, head, part = reset_server(route)
    errors, closed = [], threading.Event()
    httpd.handle_error = lambda request, address: errors.append(address)
    shutdown_request = httpd.shutdown_request

    def closing(request):
        shutdown_request(request)
        closed.set()

    httpd.shutdown_request = closing
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    request = head + "Host: 127.0.0.1\r\nContent-Type: application/json\r\n\r\n"
    try:
        with socket.create_connection(httpd.server_address[:2]) as client:
            client.sendall(request.encode("ascii") + part)
            time.sleep(0.5)  # the engine is reading the body
            client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        assert closed.wait(10)  # closed with a reset, not a FIN
        assert errors == []
        assert import_route.acquire_slot()
        import_route.release_slot()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_serve_takes_its_switches_by_name_only():
    # serve(host, port, exit_with_parent, ...) then the switches: by position, a token in
    # the fourth place would have turned importing on and left project folders off.
    with pytest.raises(TypeError):
        server.serve("127.0.0.1", 0, False, "test-host-token-" + "x" * 32)
